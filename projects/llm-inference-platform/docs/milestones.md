# Milestones and acceptance criteria

Work proceeds one milestone at a time. A later milestone is not complete because a design or configuration file exists.

## 1. Local gateway foundation

Deliverables: authenticated non-streaming API, bounded admission, synthetic backend, metrics and trace context, tests, a repeatable benchmark, architecture, and initial case study.

Acceptance:

- Missing/invalid tokens are rejected; metrics require authentication.
- Invalid and oversized requests are rejected without echoing prompts.
- Concurrency exhaustion returns 503; rate exhaustion returns 429.
- Backend timeout/error/cancellation releases admitted capacity.
- Logs exclude prompt text and credentials; gateway/backend spans correlate.
- Loopback benchmark completes baseline, rejects overload, and recovers.
- Cloud endpoint/model configuration is rejected; no cloud resources are created.

Status: verified locally. Docker and hosted CI execution are explicitly excluded from this milestone's verification claim.

## 2. Real local inference and streaming

Use a free, small, locally downloaded model only after checking licensing, disk use, RAM, and Ollama cloud-disable controls. Record model name, digest, quantization, context length, runtime version, and hardware.

Acceptance: actual responses via the gateway; streamed completion framing; time to first token; inter-token latency; bounded slow-client buffering; disconnect cancellation through a real socket; memory measurements; sustained and burst tests; cold/warm measurements; tokenizer-aware input budget where supported. No cloud fallback. Preserve synthetic tests for failure injection.

## 3. Containers and local Kubernetes

Validate the supplied Dockerfile with a free local container runtime before adding cluster manifests. Measure memory overhead on the 8 GiB machine; skip the cluster if it cannot coexist safely with inference. Model serving may remain on the host for initial gateway deployment tests.

Acceptance: non-root/read-only execution, dropped capabilities, resource limits, least-privilege service account, generated local secrets, readiness/liveness behavior, internal service routing, graceful shutdown, supported network policy, image scanning, and reproducible teardown. Test manifests on an actual local cluster. Do not use EKS or paid cloud services.

## 4. Observability and reliability

Add a local Prometheus/Grafana setup and OpenTelemetry Collector/trace store only within measured memory limits. Write a small SLO proposal after collecting baseline data.

Acceptance: correlated traces across components, actionable dashboards, backend restart and timeout experiments, rate-limit recovery, log redaction tests, open-loop arrival-rate benchmarking, and reproducible experiment reports. Do not infer GPU throughput from synthetic results.

## 5. vLLM and scaling experiments — hardware gated

Use only already available, suitable hardware at no additional cost. No GPU rental or paid API. If no suitable hardware is available, record this milestone as unverified and leave it incomplete.

Acceptance: backend contract tests against vLLM, model/version/hardware recorded, concurrency sweep, TTFT and inter-token metrics, OOM boundaries, actual resource measurements. Multi-replica tests require adequate hardware and shared admission semantics. No theoretical scale-out claim presented as a measurement.

## 6. Release and portfolio integration

Complete the README, architecture, case study, benchmark evidence, and demo plan with links to reproducible results. Review dependencies, licensing, credentials, and scope claims. Refresh the third-party notices and keep LICENSE and NOTICE with distributed code. Create a standalone repository only when requested.

Acceptance: a clean setup reproduces all claimed functionality; CI runs if a verified no-cost allowance is available; every unverified capability is labeled; portfolio/resume describe independent work accurately. A local-inference release can have a narrower verified scope while GPU and scaling experiments remain explicitly pending. Never label the entire project production-ready based on milestone 1.
