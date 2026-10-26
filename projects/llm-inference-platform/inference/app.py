# SPDX-FileCopyrightText: 2026 Kumar Raja Annamreddi
# SPDX-License-Identifier: Apache-2.0
"""Authenticated, bounded local API for non-streaming chat completion requests."""
import asyncio
import hmac
import json
import logging
import time
from contextlib import asynccontextmanager
from typing import List, Literal

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from opentelemetry.trace import Status, StatusCode
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .admission import Admission
from .backend import BackendError, OllamaBackend, SyntheticBackend
from .config import Settings
from .telemetry import LOG, Telemetry


class Message(BaseModel):
    model_config = ConfigDict(extra='forbid')
    role: Literal['system', 'user', 'assistant']
    content: str = Field(min_length=1, max_length=8192)


class Completion(BaseModel):
    model_config = ConfigDict(extra='forbid')
    model: str
    messages: List[Message] = Field(min_length=1, max_length=32)
    max_tokens: int = Field(default=128, ge=1, le=256, strict=True)
    stream: Literal[False] = False


async def request_body(request, limit):
    data = bytearray()
    async for chunk in request.stream():
        data.extend(chunk)
        if len(data) > limit:
            raise HTTPException(413, 'Request body too large')
    return data


def create_app(settings=None, backend=None):
    settings = settings or Settings.from_env()
    telemetry = Telemetry()
    admission = Admission(settings.max_concurrent, settings.requests_per_minute, settings.burst)

    @asynccontextmanager
    async def lifespan(app):
        async with httpx.AsyncClient(timeout=settings.timeout_seconds, follow_redirects=False,
                                     trust_env=False, limits=httpx.Limits(
                                         max_connections=settings.max_concurrent,
                                         max_keepalive_connections=settings.max_concurrent)) as client:
            app.state.backend = backend or (SyntheticBackend(settings.synthetic_delay)
                if settings.backend == 'synthetic' else OllamaBackend(client, settings.backend_url, settings.model))
            yield
        telemetry.provider.shutdown()

    app = FastAPI(title='Local Inference Gateway', lifespan=lifespan,
                  docs_url=None, redoc_url=None, openapi_url=None)
    app.state.telemetry = telemetry
    app.state.admission = admission

    async def authenticate(request: Request):
        token = request.headers.get('authorization', '')
        if not hmac.compare_digest(token.encode(), ('Bearer ' + settings.api_key).encode()):
            raise HTTPException(401, 'Valid bearer token required', headers={'WWW-Authenticate': 'Bearer'})

    @app.middleware('http')
    async def observe(request, call_next):
        route = request.url.path if request.url.path in {'/healthz', '/metrics', '/v1/chat/completions'} else 'other'
        started = time.perf_counter()
        status = 500
        with telemetry.tracer.start_as_current_span('gateway.request', record_exception=False,
                                                    set_status_on_exception=False) as span:
            trace_id = format(span.get_span_context().trace_id, '032x')
            try:
                response = await call_next(request)
                status = response.status_code
                response.headers['X-Trace-Id'] = trace_id
                response.headers['Cache-Control'] = 'no-store'
                return response
            finally:
                duration = time.perf_counter() - started
                span.set_attribute('http.route', route)
                span.set_attribute('http.response.status_code', status)
                telemetry.requests.labels(route, str(status)).inc()
                telemetry.duration.labels(route).observe(duration)
                LOG.info(json.dumps({'event': 'request', 'trace_id': trace_id,
                                     'route': route, 'status': status,
                                     'duration_ms': round(duration * 1000, 3),
                                     'backend': settings.backend}))

    @app.get('/healthz')
    async def health():
        return {'status': 'alive', 'backend': settings.backend, 'inference_verified': False}

    @app.get('/metrics', dependencies=[Depends(authenticate)])
    async def metrics():
        return Response(generate_latest(telemetry.registry), headers={'Content-Type': CONTENT_TYPE_LATEST})

    @app.post('/v1/chat/completions', dependencies=[Depends(authenticate)])
    async def complete(request: Request):
        if request.headers.get('content-type', '').split(';')[0] != 'application/json':
            raise HTTPException(415, 'Content-Type must be application/json')
        try:
            body = await asyncio.wait_for(request_body(request, settings.max_body_bytes), timeout=5)
            payload = Completion.model_validate_json(body)
        except asyncio.TimeoutError:
            raise HTTPException(408, 'Request body timeout')
        except (ValidationError, ValueError):
            # Validation errors can contain the user's prompt. Return only a generic error.
            raise HTTPException(422, 'Invalid request; use non-streaming text messages and max_tokens 1-256')
        if payload.model != settings.model or payload.max_tokens > settings.max_output_tokens:
            raise HTTPException(422, 'Model or output limit is not allowed')
        rejection = admission.acquire()
        if rejection:
            telemetry.rejections.labels(rejection).inc()
            raise HTTPException(429 if rejection == 'rate' else 503,
                                'Rate limit reached' if rejection == 'rate' else 'Inference capacity reached',
                                headers={'Retry-After': '1'})
        telemetry.active.inc()
        try:
            with telemetry.tracer.start_as_current_span('backend.complete', record_exception=False,
                                                        set_status_on_exception=False) as span:
                span.set_attribute('backend.type', settings.backend)
                try:
                    result = await asyncio.wait_for(app.state.backend.complete(payload.model_dump()),
                                                    timeout=settings.timeout_seconds)
                except (asyncio.TimeoutError, httpx.TimeoutException):
                    span.set_status(Status(StatusCode.ERROR))
                    raise HTTPException(504, 'Inference deadline exceeded')
                except (BackendError, httpx.HTTPError):
                    span.set_status(Status(StatusCode.ERROR))
                    raise HTTPException(502, 'Inference backend unavailable')
            return JSONResponse(result, headers={'X-Inference-Backend': settings.backend})
        finally:
            admission.release()
            telemetry.active.dec()

    return app


def main():
    import uvicorn
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    uvicorn.run(create_app(), host='127.0.0.1', port=8000, workers=1, access_log=False)


if __name__ == '__main__':
    main()
