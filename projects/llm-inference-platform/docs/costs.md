# Cost and hardware constraints

The spending limit is **$0 in additional service, software, or hardware purchases**. Existing computer electricity and internet usage are not measured by this project and cannot be claimed to cost nothing.

Observed development environment: Apple Silicon (`arm64`), 8 GiB unified memory, Python 3.12.14. Ollama is installed, but no local inference model was available during milestone 1. The installed cloud-model alias was not used. Docker and kubectl were not available on PATH.

| Work | Additional service spending | Limit |
|---|---:|---|
| Synthetic gateway, tests, loopback benchmark | $0 | Runs on the existing Mac |
| Small local model | $0 for services | Requires free model licensing and available disk/RAM; not downloaded yet |
| Local container/Kubernetes experiments | $0 for services | Choose a free runtime and measure memory overhead first |
| Hosted CI | Not enabled | Use local tests; verify no-cost eligibility before any manual hosted run |
| vLLM GPU experiments | Not authorized to spend | Only suitable hardware already available at no charge |
| Cloud deployment | Disabled | Documentation only; no provisioning or billing-enabled trial |

No paid API credentials, GPU rentals, subscriptions, cloud fallback, model auto-pulls, or infrastructure provisioning are implemented. Package installation downloads free open-source dependencies. Benchmarking uses only loopback traffic and a deterministic backend.

The gateway's loopback checks do not sandbox the Ollama daemon itself. Real local-model validation must also disable cloud features and verify local model provenance. A compromised local daemon is outside this milestone's threat boundary.
