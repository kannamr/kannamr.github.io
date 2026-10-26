# Case study: bounded admission for a local inference gateway

## Context

This independent project explores the request-handling layer around model serving. The development machine has 8 GiB of unified memory, and the budget excludes additional service or hardware spending. No local inference model was available at the start. The existing cloud-model alias was not used.

The first question was whether the gateway could admit a bounded amount of work, fail predictably, preserve capacity after errors, and produce useful telemetry. A synthetic backend made those behaviors reproducible before introducing model-loading and hardware constraints.

## Implementation

A Python/FastAPI gateway validates a narrow chat-completion request format. Authentication precedes body parsing. A token bucket controls admitted request rate, while an independent concurrency gate caps active backend work. There is no application queue. The gateway returns 429 for exhausted rate capacity and 503 for concurrent overload, rather than letting requests accumulate indefinitely.

Every admitted request has a deadline and releases capacity in a `finally` block. Prometheus metrics distinguish HTTP outcomes, active requests, admission rejection reasons, and latency. OpenTelemetry produces correlated gateway/backend spans; JSON request logs exclude prompts, credentials, and response content.

A separate local Ollama adapter is tested with simulated HTTP responses. It checks local model metadata before sending a prompt and rejects cloud configuration. That contract test does not establish compatibility with a live model or validate real backend cancellation.

## Verification and observed results

Thirty-one automated tests passed on Python 3.12.14. Coverage includes authentication, body limits, invalid inputs, token refill, concurrent overload, timeout cancellation, in-process cancellation, sanitized upstream errors, telemetry privacy, trace correlation, and rejection of remote/missing models and redirected upstream responses.

The [recorded HTTP benchmark](../results/milestone-1-synthetic.json) ran over loopback on Apple Silicon. It used a 25 ms synthetic delay, two gateway concurrency slots, a high rate limit to isolate concurrency, five warm-up requests, and closed-loop client workers. Application INFO logging was disabled by the benchmark launch; logging overhead is not represented in these results.

| Scenario | Requests / client concurrency | Outcomes | Successful-request p95 |
|---|---|---|---:|
| Baseline | 100 / 2 | 100 HTTP 200 | 35.070 ms |
| Overload | 100 / 12 | 9 HTTP 200; 91 HTTP 503 | 82.836 ms |
| Recovery | 10 / 1 | 10 HTTP 200 | 29.300 ms |

These are one-run observations, not a throughput guarantee. The overload run deliberately rejects work; its overall response latency is not a substitute for successful inference latency. Successful-request percentiles exclude rejected requests. With only nine accepted overload requests, the high percentile is effectively the slowest observation. Closed-loop load can understate latency during stalls. A larger, open-loop experiment belongs in a later milestone.

## Tradeoffs and remaining work

Fail-fast admission makes overload visible but sacrifices burst absorption. A single token is adequate for this local experiment, not multi-user authorization. Process-local counters are simple and testable, but cannot enforce a cluster-wide budget. JSON span export makes correlation inspectable without deploying a telemetry stack; it does not demonstrate remote trace collection.

Next, a small free local model will be selected and verified against the same API. Streaming introduces additional questions: time to first token, slow-client buffering, disconnect handling, and whether cancellation actually stops backend computation. Those require real socket and runtime tests.

The supplied Dockerfile and manual CI workflow remain unexecuted. Kubernetes, vLLM, GPU throughput, and horizontal scaling remain pending. No cloud infrastructure was provisioned, no paid API was called, and no employer implementation was used.
