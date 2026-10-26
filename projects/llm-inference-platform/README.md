# LLM Inference Platform

An original, local-first engineering project by [Kumar Raja Annamreddi](https://github.com/kannamr), focused on admission control, observable request handling, and repeatable inference experiments.

**Status: milestone 1 — local gateway verified with a synthetic backend.** No model-serving or GPU performance claim is made. This is independent portfolio work, not an employer system or professional production deployment.

## License and attribution

Licensed under the [Apache License 2.0](LICENSE). You may use, modify, and
redistribute the project, including commercially, subject to the license terms.
When redistributing, include the license, preserve applicable notices, and
identify modified files as required by the license.

Copyright (c) 2026 Kumar Raja Annamreddi, for original material to the extent
copyright is held. Licensing grants permissions without transferring ownership.
Third-party components retain their own licenses; see [NOTICE](NOTICE) and
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

See the [licensing guide](docs/licensing.md) for scope and attribution details.
Feedback is welcome; [CONTRIBUTING.md](CONTRIBUTING.md) describes the current
feedback-only contribution policy. Forking and modifying the project under
Apache 2.0 do not require permission to contribute to this repository.

## What works today

- Bearer-token authentication, including protected metrics.
- A constrained, non-streaming `/v1/chat/completions` API.
- Token-bucket rate limiting, immediate overload rejection, and backend deadlines.
- Bounded request bodies and output-token requests; one configured model.
- Prometheus metrics, payload-free JSON logs, and OpenTelemetry gateway/backend spans.
- A deterministic synthetic backend and a contract-tested local Ollama adapter.
- Automated tests and a repeatable HTTP benchmark over loopback.

Streaming, real local model validation, Kubernetes deployment, distributed admission control, and vLLM GPU validation are later milestones. The Dockerfile and manual CI workflow are supplied but have not been run in their target environments.

## Run locally

Requires Python 3.12. Work from this directory:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
export INFERENCE_API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
python -m inference.app
```

The server binds to `127.0.0.1:8000`. Keep the generated token in your shell; do not put it in Git or a screenshot. `.env.example` documents settings but is not loaded automatically. In a second terminal, set `INFERENCE_API_KEY` to the same token, then:

```bash
curl http://127.0.0.1:8000/v1/chat/completions \
  -H "Authorization: Bearer $INFERENCE_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"synthetic-v1","messages":[{"role":"user","content":"Hello"}],"max_tokens":32}'

curl http://127.0.0.1:8000/metrics \
  -H "Authorization: Bearer $INFERENCE_API_KEY"
```

The response explicitly says that no model inference occurred. `X-Inference-Backend` identifies the backend; `X-Trace-Id` correlates request logs and spans.

## Verify

```bash
python -m pytest -q
python tools/benchmark.py
```

The benchmark creates a temporary loopback server, runs a warm-up plus baseline, overload, and recovery scenarios, and shuts it down. It generates an ephemeral token and uses no model or external endpoint. Local results go to ignored `results/local-synthetic.json`. The reviewed milestone result is in [results/milestone-1-synthetic.json](results/milestone-1-synthetic.json).

## Architecture and engineering notes

- [Architecture, technology choices, and tradeoffs](docs/architecture.md)
- [Milestones and acceptance criteria](docs/milestones.md)
- [Security boundaries and operational limits](docs/security.md)
- [Cost and hardware constraints](docs/costs.md)
- [Milestone 1 case study](docs/case-study.md)
- [Five-minute demo](docs/demo.md)

```text
inference/          Gateway, admission control, backend adapters, telemetry
tests/             Authentication, overload, timeout, privacy, adapter tests
tools/             Reproducible synthetic HTTP benchmark
docs/              Design, milestones, security, costs, case study, demo
results/           Reviewed benchmark evidence; local runs ignored
Dockerfile         Non-root gateway image definition; not yet built
LICENSE / NOTICE   Usage terms and original-project attribution
third_party/       Unmodified packaged dependency notices
.github/workflows/ Manual test workflow for a future standalone repository
```

## Local model path

The Ollama adapter accepts only literal loopback URLs, rejects cloud model names, checks that the model is locally installed with positive size and no remote metadata, and disables redirects and proxy environment settings. It never downloads models. Only synthetic operation has been verified on the development machine.

Before real inference, follow milestone 2: select a small model with suitable licensing, verify its local provenance, disable Ollama cloud features, and measure memory use. Do not use the already installed cloud-model alias. Local HTTP alone is insufficient proof that a model runs locally: Ollama can route cloud models through its local server.

## Repository and publication

This project uses a standalone repository layout. The manual workflow in
`.github/workflows/ci.yml` runs tests only when explicitly started. Local tests
remain the default; verify no-cost eligibility before using hosted CI. There is
no deployment job, model auto-download, or paid-service integration.

The portfolio and resume should continue to mark the project as planned/in progress until the relevant implementation milestones pass. No employer code, internal architecture, credentials, or resource identifiers belong here.
