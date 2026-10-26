# SPDX-FileCopyrightText: 2026 Kumar Raja Annamreddi
# SPDX-License-Identifier: Apache-2.0
"""Synthetic test responses and a loopback-only Ollama adapter."""
import asyncio
import json
import uuid

import httpx
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


class BackendError(Exception):
    pass


async def read_json(client, method, url, **kwargs):
    async with client.stream(method, url, **kwargs) as response:
        if response.status_code != 200:
            raise BackendError('Backend request failed')
        body = bytearray()
        async for chunk in response.aiter_bytes():
            body.extend(chunk)
            if len(body) > 262144:
                raise BackendError('Backend response exceeds limit')
        try:
            return json.loads(body)
        except (ValueError, UnicodeDecodeError) as exc:
            raise BackendError('Backend response is not JSON') from exc


class SyntheticBackend:
    """Exercises gateway behavior; never performs model inference."""
    def __init__(self, delay):
        self.delay = delay

    async def complete(self, request):
        await asyncio.sleep(self.delay)
        return {
            'id': 'synthetic-' + uuid.uuid4().hex,
            'object': 'chat.completion',
            'model': 'synthetic-v1',
            'choices': [{'index': 0, 'message': {'role': 'assistant',
                         'content': 'Synthetic test response; no model inference was performed.'},
                         'finish_reason': 'stop'}],
        }


class OllamaBackend:
    def __init__(self, client, base_url, model):
        self.client = client
        self.base_url = base_url.rstrip('/')
        self.model = model

    async def complete(self, request):
        headers = {}
        TraceContextTextMapPropagator().inject(headers)
        # Verify local provenance before sending any prompt. Never pull a model.
        tags = await read_json(self.client, 'GET', self.base_url + '/api/tags', headers=headers)
        candidates = tags.get('models', []) if isinstance(tags, dict) else []
        if not isinstance(candidates, list):
            raise BackendError('Invalid model inventory')
        local = [item for item in candidates if isinstance(item, dict)
                 and self.model in {item.get('name'), item.get('model')}]
        if not local or any(item.get('remote_host') or item.get('remote_model')
                            or not isinstance(item.get('size'), int) or item['size'] <= 0
                            for item in local):
            raise BackendError('A locally installed model is required')
        result = await read_json(self.client, 'POST', self.base_url + '/v1/chat/completions',
                                 headers=headers, json=request)
        try:
            text = result['choices'][0]['message']['content']
            if not isinstance(text, str) or not isinstance(result.get('model'), str):
                raise ValueError('Invalid completion')
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise BackendError('Invalid backend completion') from exc
        return result
