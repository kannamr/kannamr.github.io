# SPDX-FileCopyrightText: 2026 Kumar Raja Annamreddi
# SPDX-License-Identifier: Apache-2.0
"""Run a bounded synthetic benchmark against a temporary loopback gateway."""
import argparse
import asyncio
from collections import Counter
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import platform
import secrets
import socket
import subprocess
import sys
import tempfile
import time

import httpx

ROOT = Path(__file__).resolve().parents[1]


def percentile(values, fraction):
    if not values:
        return None
    return round(sorted(values)[max(0, math.ceil(len(values) * fraction) - 1)], 3)


async def scenario(client, url, token, requests, concurrency):
    statuses = Counter()
    success_ms = []
    all_ms = []
    work = asyncio.Queue()
    for i in range(requests):
        work.put_nowait(i)

    async def worker():
        while not work.empty():
            work.get_nowait()
            start = time.perf_counter()
            try:
                response = await client.post(url + '/v1/chat/completions',
                    headers={'Authorization': 'Bearer ' + token},
                    json={'model': 'synthetic-v1', 'messages': [{'role': 'user', 'content': 'benchmark'}],
                          'max_tokens': 16})
                status = str(response.status_code)
            except httpx.HTTPError:
                status = 'transport_error'
            elapsed = (time.perf_counter() - start) * 1000
            all_ms.append(elapsed)
            statuses[status] += 1
            if status == '200':
                success_ms.append(elapsed)

    start = time.perf_counter()
    await asyncio.gather(*(worker() for _ in range(concurrency)))
    duration = time.perf_counter() - start
    return {'requests': requests, 'client_concurrency': concurrency,
            'wall_seconds': round(duration, 4), 'statuses': dict(statuses),
            'successful_requests_per_second': round(len(success_ms) / duration, 3),
            'successful_latency_ms': {'p50': percentile(success_ms, .5),
                                      'p95': percentile(success_ms, .95),
                                      'p99': percentile(success_ms, .99)},
            'all_request_latency_ms': {'p50': percentile(all_ms, .5), 'p95': percentile(all_ms, .95)}}


async def run():
    token = secrets.token_urlsafe(32)
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        port = listener.getsockname()[1]
    url = f'http://127.0.0.1:{port}'
    env = {**os.environ, 'INFERENCE_API_KEY': token, 'INFERENCE_BACKEND': 'synthetic',
           'INFERENCE_MODEL': 'synthetic-v1', 'INFERENCE_MAX_CONCURRENT': '2',
           'INFERENCE_REQUESTS_PER_MINUTE': '60000', 'INFERENCE_BURST': '1000',
           'INFERENCE_TIMEOUT_SECONDS': '10', 'INFERENCE_BACKEND_URL': 'http://127.0.0.1:11434'}
    with tempfile.TemporaryFile() as server_log:
        proc = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'inference.app:create_app',
                                 '--factory', '--host', '127.0.0.1', '--port', str(port),
                                 '--no-access-log', '--log-level', 'warning'],
                                 cwd=ROOT, env=env, stdout=server_log, stderr=server_log)
        try:
            async with httpx.AsyncClient(timeout=15, trust_env=False) as client:
                for _ in range(100):
                    if proc.poll() is not None:
                        raise RuntimeError('Benchmark server exited during startup')
                    try:
                        if (await client.get(url + '/healthz')).status_code == 200:
                            break
                    except httpx.HTTPError:
                        pass
                    await asyncio.sleep(.05)
                else:
                    raise RuntimeError('Benchmark server did not become ready')
                await scenario(client, url, token, 5, 1)
                baseline = await scenario(client, url, token, 100, 2)
                overload = await scenario(client, url, token, 100, 12)
                recovery = await scenario(client, url, token, 10, 1)
                assert baseline['statuses'] == {'200': 100}, baseline
                assert overload['statuses'].get('503', 0) > 0, overload
                assert not (set(overload['statuses']) - {'200', '503'}), overload
                assert recovery['statuses'] == {'200': 10}, recovery
                return {'recorded_at_utc': datetime.now(timezone.utc).isoformat(),
                        'backend': 'synthetic', 'model_inference': False,
                        'hardware': {'architecture': platform.machine(), 'os': platform.system(),
                                     'python': platform.python_version()},
                        'gateway_concurrency': 2, 'synthetic_delay_ms': 25,
                        'rate_limit_per_minute': 60000, 'burst': 1000, 'warmup_requests': 5,
                        'method': 'closed-loop HTTP over loopback; nearest-rank percentiles; one run',
                        'scenarios': {'baseline': baseline, 'overload': overload, 'recovery': recovery},
                        'limitations': ['No model or GPU measured', 'Not a capacity forecast',
                                        'Closed-loop load can understate latency during stalls',
                                        'Successful latency excludes rejected requests']}
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'results/local-synthetic.json')
    args = parser.parse_args()
    result = asyncio.run(run())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))
