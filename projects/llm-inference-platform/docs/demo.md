# Five-minute milestone 1 demo

1. Explain the scope: an independent local inference gateway; the demo backend performs no model inference.
2. Show the architecture and why overload is rejected rather than queued indefinitely.
3. Generate a token and start the gateway using the README. Keep the token off screen.
4. Send a request without authentication and show HTTP 401. Send an authenticated request and show the synthetic response and trace ID.
5. Read authenticated metrics and correlate the gateway/backend spans in the terminal. Explain why prompts and tokens are excluded.
6. Run `python -m pytest -q` and describe timeout, overload, privacy, and cloud-rejection tests.
7. Run `python tools/benchmark.py`. Compare successful latency with rejected-request counts; show recovery after overload.
8. Close with the next experiment: a small local model and streamed-response measurements. State that Docker, Kubernetes, real inference, and GPU throughput remain unverified.

Do not call the synthetic request rate tokens per second. Do not present this milestone as production experience. Stop the foreground gateway with Ctrl-C; the benchmark stops its own temporary server automatically.
