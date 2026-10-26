# Security and operational limits

This is a local development service. Do not expose it directly to the internet or submit private data to it.

## Implemented controls

- Loopback binding for the normal Python launch command.
- Required high-entropy bearer token; constant-time comparison; metrics protected.
- Request size/schema/output-token limits and a single allowlisted model.
- Process-local concurrency and rate controls; backend deadline and bounded response reads.
- Loopback-only backend URL, no redirects, no environment proxy use, no model auto-download.
- Cloud-model names and remote metadata rejected by the Ollama adapter.
- No prompt, response content, token, or upstream error detail in request logs or spans.
- Fixed route labels to avoid unbounded metric cardinality.

The admission gate bounds backend work, not every TCP connection or unauthenticated request. Slow/large clients are partly constrained by the body size/deadline; a production edge would need connection-level limits and TLS. The local configuration is not a multi-tenant security boundary.

## Known boundaries

Static tokens do not provide per-user permissions. Limits are process-local. Backend request cancellation is tested in-process; client disconnect behavior over a real TCP connection and actual model cancellation are pending. A local daemon may continue computation after an HTTP timeout; that must be measured in milestone 2.

The Dockerfile runs as a non-root user but has not been built locally. It listens on all interfaces inside the container. When testing it later, publish only to loopback and add runtime limits:

```bash
# Milestone 3: requires a working, free container runtime; not yet verified.
docker build -t llm-gateway:local .
docker run --rm --read-only --tmpfs /tmp --cap-drop=ALL \
  --security-opt=no-new-privileges --memory=256m --cpus=1 \
  -p 127.0.0.1:8000:8000 -e INFERENCE_API_KEY \
  llm-gateway:local
```

Use the synthetic backend for this first container test. Container loopback does not reach the host Ollama service; that network configuration will be designed and tested separately.

No employer code, internal schemas, account IDs, cost codes, credentials, or proprietary architecture are used. The public project is about inference request handling, not a reproduction of the enterprise developer platform.
