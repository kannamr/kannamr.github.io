# SPDX-FileCopyrightText: 2026 Kumar Raja Annamreddi
# SPDX-License-Identifier: Apache-2.0
"""Explicit, fail-closed configuration for local development."""
import math
import os
from dataclasses import dataclass
from urllib.parse import urlsplit


@dataclass(frozen=True)
class Settings:
    api_key: str
    backend: str = 'synthetic'
    model: str = 'synthetic-v1'
    backend_url: str = 'http://127.0.0.1:11434'
    max_concurrent: int = 2
    requests_per_minute: int = 60
    burst: int = 5
    timeout_seconds: float = 10.0
    synthetic_delay: float = 0.025
    max_body_bytes: int = 16384
    max_output_tokens: int = 256

    def __post_init__(self):
        if len(self.api_key) < 24 or not self.api_key.isascii():
            raise ValueError('Set INFERENCE_API_KEY to an ASCII token of at least 24 characters.')
        if self.backend not in {'synthetic', 'ollama'}:
            raise ValueError('Only synthetic and local Ollama backends are enabled.')
        url = urlsplit(self.backend_url)
        if (url.scheme != 'http' or url.hostname not in {'127.0.0.1', '::1'}
                or url.username or url.password or url.query or url.fragment
                or url.path not in {'', '/'}):
            raise ValueError('Backend URL must be a literal loopback HTTP address with no credentials or path.')
        if not self.model or 'cloud' in self.model.lower():
            raise ValueError('Cloud model names are disabled.')
        if self.backend == 'synthetic' and self.model != 'synthetic-v1':
            raise ValueError('The synthetic backend must be labeled synthetic-v1.')
        for value in [self.max_concurrent, self.requests_per_minute, self.burst,
                      self.max_body_bytes, self.max_output_tokens]:
            if value < 1:
                raise ValueError('Limits must be positive.')
        if not math.isfinite(self.timeout_seconds) or self.timeout_seconds <= 0:
            raise ValueError('Timeout must be finite and positive.')
        if not math.isfinite(self.synthetic_delay) or self.synthetic_delay < 0:
            raise ValueError('Synthetic delay must be finite and nonnegative.')

    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.environ.get('INFERENCE_API_KEY', ''),
            backend=os.environ.get('INFERENCE_BACKEND', 'synthetic'),
            model=os.environ.get('INFERENCE_MODEL', 'synthetic-v1'),
            backend_url=os.environ.get('INFERENCE_BACKEND_URL', 'http://127.0.0.1:11434'),
            max_concurrent=int(os.environ.get('INFERENCE_MAX_CONCURRENT', '2')),
            requests_per_minute=int(os.environ.get('INFERENCE_REQUESTS_PER_MINUTE', '60')),
            burst=int(os.environ.get('INFERENCE_BURST', '5')),
            timeout_seconds=float(os.environ.get('INFERENCE_TIMEOUT_SECONDS', '10')),
        )
