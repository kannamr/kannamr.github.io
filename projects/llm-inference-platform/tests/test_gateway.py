# SPDX-FileCopyrightText: 2026 Kumar Raja Annamreddi
# SPDX-License-Identifier: Apache-2.0
import asyncio
import json
import logging
from contextlib import asynccontextmanager

import httpx
import pytest

from inference.admission import Admission
from inference.app import create_app
from inference.backend import BackendError, OllamaBackend
from inference.config import Settings

KEY = 'test-only-token-not-for-deployment'
HEADERS = {'Authorization': 'Bearer ' + KEY}
PAYLOAD = {'model': 'synthetic-v1', 'messages': [{'role': 'user', 'content': 'test prompt'}]}


@asynccontextmanager
async def client_for(backend=None, **options):
    app = create_app(Settings(api_key=KEY, **options), backend=backend)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://test') as client:
            yield app, client


@pytest.mark.asyncio
async def test_authentication_and_metrics_access():
    async with client_for() as (_, client):
        assert (await client.get('/healthz')).status_code == 200
        assert (await client.get('/metrics')).status_code == 401
        assert (await client.post('/v1/chat/completions', json=PAYLOAD)).status_code == 401
        assert (await client.post('/v1/chat/completions', json=PAYLOAD,
                                 headers={'Authorization': 'Bearer incorrect'})).status_code == 401
        assert (await client.get('/metrics', headers=HEADERS)).status_code == 200


@pytest.mark.asyncio
async def test_completion_metrics_and_payload_free_logs(caplog):
    caplog.set_level(logging.INFO, logger='inference')
    async with client_for() as (_, client):
        response = await client.post('/v1/chat/completions', json=PAYLOAD, headers=HEADERS)
        assert response.status_code == 200
        assert response.json()['model'] == 'synthetic-v1'
        assert response.headers['x-inference-backend'] == 'synthetic'
        trace_id = response.headers['x-trace-id']
        assert len(trace_id) == 32
        metrics = (await client.get('/metrics', headers=HEADERS)).text
        assert 'inference_active_requests 0.0' in metrics
        assert 'inference_requests_total{route="/v1/chat/completions",status="200"} 1.0' in metrics
    records = [json.loads(r.message) for r in caplog.records if r.name == 'inference']
    spans = [r for r in records if r.get('event') == 'span' and r['trace_id'] == trace_id]
    assert {s['name'] for s in spans} == {'gateway.request', 'backend.complete'}
    parent = next(s for s in spans if s['name'] == 'gateway.request')
    child = next(s for s in spans if s['name'] == 'backend.complete')
    assert child['parent_span_id'] == parent['span_id']
    assert KEY not in caplog.text
    assert 'test prompt' not in caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize('update', [{'stream': True}, {'model': 'other'}, {'max_tokens': 257},
                                    {'max_tokens': '5'}, {'unknown': 1}, {'messages': []}])
async def test_invalid_requests(update):
    async with client_for() as (_, client):
        response = await client.post('/v1/chat/completions', json={**PAYLOAD, **update}, headers=HEADERS)
        assert response.status_code == 422
        assert 'test prompt' not in response.text


@pytest.mark.asyncio
async def test_body_limits_and_media_type():
    async with client_for() as (_, client):
        assert (await client.post('/v1/chat/completions', content='bad', headers=HEADERS)).status_code == 415
        headers = {**HEADERS, 'Content-Type': 'application/json'}
        assert (await client.post('/v1/chat/completions', content='bad', headers=headers)).status_code == 422
        async def chunks():
            yield b'x' * 10000
            yield b'x' * 10000
        assert (await client.post('/v1/chat/completions', content=chunks(), headers=headers)).status_code == 413


def test_rate_bucket_refills_and_capacity_does_not_consume_token():
    now = [0.0]
    admission = Admission(1, 60, 1, clock=lambda: now[0])
    assert admission.acquire() is None
    now[0] = 1
    assert admission.acquire() == 'capacity'
    admission.release()
    assert admission.acquire() is None
    admission.release()
    assert admission.acquire() == 'rate'
    now[0] = 2
    assert admission.acquire() is None


@pytest.mark.asyncio
async def test_rate_limit_http():
    async with client_for(burst=1, requests_per_minute=1) as (_, client):
        assert (await client.post('/v1/chat/completions', json=PAYLOAD, headers=HEADERS)).status_code == 200
        response = await client.post('/v1/chat/completions', json=PAYLOAD, headers=HEADERS)
        assert response.status_code == 429
        assert 'retry-after' in response.headers


class BlockingBackend:
    def __init__(self):
        self.started = asyncio.Event()
        self.release = asyncio.Event()
        self.cancelled = False

    async def complete(self, request):
        self.started.set()
        try:
            await self.release.wait()
        except asyncio.CancelledError:
            self.cancelled = True
            raise
        return {'model': 'synthetic-v1', 'choices': []}


@pytest.mark.asyncio
async def test_concurrent_overload_and_recovery():
    backend = BlockingBackend()
    async with client_for(backend, max_concurrent=1) as (app, client):
        first = asyncio.create_task(client.post('/v1/chat/completions', json=PAYLOAD, headers=HEADERS))
        await asyncio.wait_for(backend.started.wait(), 1)
        response = await client.post('/v1/chat/completions', json=PAYLOAD, headers=HEADERS)
        assert response.status_code == 503
        assert app.state.admission.active == 1
        backend.release.set()
        assert (await first).status_code == 200
        assert app.state.admission.active == 0
        assert (await client.post('/v1/chat/completions', json=PAYLOAD, headers=HEADERS)).status_code == 200


@pytest.mark.asyncio
async def test_timeout_cancels_backend_and_releases_slot():
    backend = BlockingBackend()
    async with client_for(backend, timeout_seconds=.02) as (app, client):
        response = await client.post('/v1/chat/completions', json=PAYLOAD, headers=HEADERS)
        assert response.status_code == 504
        assert backend.cancelled
        assert app.state.admission.active == 0


@pytest.mark.asyncio
async def test_cancelled_request_releases_slot():
    backend = BlockingBackend()
    async with client_for(backend) as (app, client):
        task = asyncio.create_task(client.post('/v1/chat/completions', json=PAYLOAD, headers=HEADERS))
        await asyncio.wait_for(backend.started.wait(), 1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert app.state.admission.active == 0
        assert backend.cancelled


@pytest.mark.asyncio
async def test_backend_error_is_sanitized():
    class Failing:
        async def complete(self, request):
            raise BackendError('private upstream diagnostic')
    async with client_for(Failing()) as (app, client):
        response = await client.post('/v1/chat/completions', json=PAYLOAD, headers=HEADERS)
        assert response.status_code == 502
        assert 'private' not in response.text
        assert app.state.admission.active == 0


@pytest.mark.parametrize('options', [dict(api_key='short'), dict(backend='cloud'),
    dict(backend_url='https://api.example.com'), dict(backend_url='http://localhost:11434'),
    dict(backend_url='http://127.0.0.1:11434/path'), dict(model='minimax:cloud'),
    dict(timeout_seconds=float('nan')), dict(max_concurrent=0)])
def test_configuration_fails_closed(options):
    with pytest.raises(ValueError):
        Settings(**{'api_key': KEY, **options})


@pytest.mark.asyncio
@pytest.mark.parametrize('tag', [None, {'name': 'tiny', 'size': 1, 'remote_host': 'https://remote'},
                                {'name': 'tiny', 'size': 0}])
async def test_ollama_rejects_missing_or_remote_models(tag):
    paths = []
    def handler(request):
        paths.append(request.url.path)
        return httpx.Response(200, json={'models': [] if tag is None else [tag]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        backend = OllamaBackend(client, 'http://127.0.0.1:11434', 'tiny')
        with pytest.raises(BackendError):
            await backend.complete(PAYLOAD)
    assert paths == ['/api/tags']


@pytest.mark.asyncio
async def test_ollama_contract_uses_local_model_and_forwards_trace():
    seen = []
    def handler(request):
        seen.append(request)
        if request.url.path == '/api/tags':
            return httpx.Response(200, json={'models': [{'name': 'tiny', 'size': 100}]})
        return httpx.Response(200, json={'model': 'tiny', 'choices': [{'message': {'content': 'hello'}}]})
    from inference.telemetry import Telemetry
    telemetry = Telemetry()
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        backend = OllamaBackend(client, 'http://127.0.0.1:11434', 'tiny')
        with telemetry.tracer.start_as_current_span('test'):
            result = await backend.complete({**PAYLOAD, 'model': 'tiny'})
        assert result['choices'][0]['message']['content'] == 'hello'
        assert seen[-1].url.path == '/v1/chat/completions'
        assert 'traceparent' in seen[-1].headers
    telemetry.provider.shutdown()


@pytest.mark.asyncio
@pytest.mark.parametrize('response', [httpx.Response(302, headers={'Location': 'https://remote'}),
    httpx.Response(200, content=b'x' * 262145), httpx.Response(200, content=b'invalid')])
async def test_backend_redirects_and_invalid_responses_rejected(response):
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda _: response)) as client:
        with pytest.raises(BackendError):
            await OllamaBackend(client, 'http://127.0.0.1:11434', 'tiny').complete(PAYLOAD)


@pytest.mark.asyncio
async def test_malformed_model_inventory_is_a_backend_error():
    async with httpx.AsyncClient(transport=httpx.MockTransport(
            lambda _: httpx.Response(200, json={'models': None}))) as client:
        with pytest.raises(BackendError):
            await OllamaBackend(client, 'http://127.0.0.1:11434', 'tiny').complete(PAYLOAD)
