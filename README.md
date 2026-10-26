
# Kumar Raja Annamreddi
### Cloud Engineering · Platform Engineering · AI Infrastructure

Cloud and platform engineer with 10+ years of experience building and operating cloud infrastructure, Kubernetes platforms, infrastructure automation, and CI/CD systems in enterprise environments.

I focus on platform reliability, developer enablement, cloud governance, automation, and cost visibility. At Charter Communications, I am developing an enterprise multi-application GitOps platform on AWS EKS Auto Mode supporting an internal portal for AI-assisted applications built by engineers across the organization.

**Portfolio:** [kannamr.github.io](https://kannamr.github.io)  
**LinkedIn:** [linkedin.com/in/kumarannamreddi](https://www.linkedin.com/in/kumarannamreddi)  
**GitHub:** [github.com/kannamr](https://github.com/kannamr)  
**Contact:** [kr.annamreddi@gmail.com](mailto:kr.annamreddi@gmail.com)

---

## Technical Expertise

| Area | Technologies |
|---|---|
| Cloud Platforms | AWS, Azure, GCP |
| Containers & Orchestration | Kubernetes, Amazon EKS, Docker, Helm |
| Infrastructure as Code | Terraform, Terragrunt, CloudFormation, Ansible |
| CI/CD & GitOps | GitHub Actions, GitLab CI, Jenkins, Harness, Flux, Argo CD |
| Observability | Prometheus, Grafana, Loki, Datadog |
| Data & Workflow Platforms | Amazon MWAA, Airflow, Kafka, Flink, Redis, PostgreSQL |
| Cloud Security | IAM, Service Control Policies, GuardDuty, access governance |
| Automation & Scripting | Python, Bash, YAML, HCL |

## Enterprise Engineering Case Studies

### Enterprise Internal Developer Platform

At Charter Communications, I designed and developed a multi-application GitOps platform on **AWS EKS Auto Mode** supporting an internal portal for AI-assisted applications created and deployed by engineers across the organization. Development is ongoing.

- Declarative application onboarding and Helm-based reusable application infrastructure.
- Flux-based GitOps automation and CI/CD workflows.
- Blue-green deployments and release safeguards.
- Workload identity, secrets management, and support for different application dependencies.

### Kubernetes FinOps and Cost Attribution

Within the platform, I implemented team-level application identification using team names and organizational cost codes. This associates application infrastructure with the teams responsible for consuming those resources and supports ownership and cloud cost attribution. This capability is part of the internal developer platform.

### IAM Key Rotation Tool

At Charter Communications, I built a UI tool that helps IAM access-key owners rotate their keys as part of a scheduled quarterly process. I integrated the workflow with Datadog to update dashboards with relevant rotation data and enable users to configure alerts through communication channels.

The internal developer platform, its FinOps capability, and the IAM key-rotation tool are all professional work at Charter Communications.

**Source code for these Charter projects is proprietary and unavailable publicly.** These summaries describe my contributions without sharing confidential architecture, internal identifiers, or implementation details.

## Independent AI Infrastructure Projects

The [LLM Inference Platform](https://github.com/kannamr/llm-inference-platform) is **in progress**. Milestone 1 includes an authenticated Python gateway, rate limiting, concurrency controls, observability, and 31 passing tests. Current benchmarks use a synthetic backend; real-model inference and GPU performance remain unverified.

**LLM project repository:** [github.com/kannamr/llm-inference-platform](https://github.com/kannamr/llm-inference-platform)

| Project | Status |
|---|---|
| [Production-Grade LLM Inference Platform](https://github.com/kannamr/llm-inference-platform) | In progress — Milestone 1 verified with a synthetic backend |
| Secure AI Agent Runtime Platform | Planned |
| AI Reliability & Evaluation Platform | Planned |
| Kubernetes GPU Workload Scheduling Lab | Planned |

These are independent personal projects, separate from my professional enterprise work. Implementations live in their own repositories. Completed projects will be added to my resume after the claimed functionality has been tested and verified.

## Selected Engineering Impact

- **Enterprise cloud automation:** Developed Python automation for IAM access-key rotation across 200+ AWS accounts.
- **Cloud governance:** Supported IAM governance and least-privilege controls across 50+ AWS accounts.
- **Build optimization:** Reduced CI build duration from 90 minutes to 20 minutes.
- **Developer enablement:** Built Kubernetes tooling and deployment frameworks supporting 30+ engineering teams.
- **Cloud cost optimization:** Contributed to initiatives associated with $500K in annual cloud-spend reduction.
- **AWS modernization:** Helped reduce infrastructure costs by 25% while maintaining availability.

## Professional Experience

- **Charter Communications** — DevOps Engineer
- **LogRhythm Inc.** — Cloud Engineer
- **Nutrien Ag Solutions** — Cloud Engineer
- **Empower Retirement** — DevOps Engineer
- **Academy Sports** — DevOps Engineer
- **Wolters Kluwer** — Cloud Engineer
- **Optum** — DevOps Engineer
- **Servizon** — DevOps / Build and Release Engineer

## Current Technical Direction

I am building on my cloud and platform engineering background with a focus on:

- AI workload infrastructure and model-serving platforms
- Kubernetes-based deployment and scaling
- Infrastructure automation and reproducible environments
- Observability, reliability, and operational readiness
- Secure, cost-efficient cloud architecture

Portfolio projects will be linked here as their implementations and documentation become publicly available.

## Education

**Master of Science — Cyber Systems and Information Security**  
Auburn University at Montgomery

---

*Target roles: Senior/Staff Platform Engineer, AI Infrastructure Engineer, and ML Platform Engineer.*

## Resume files

- [Download resume](assets/resume.pdf)
- [Editable resume source](assets/resume.md)
- Regenerate the PDF with `python3 scripts/build_resume.py` (requires ReportLab).

## Maintaining the portfolio

Edit `index.html` for page content and `styles.css` for presentation. The site uses plain HTML, CSS, and JavaScript; no build step is needed.

Edit `assets/resume.md`, install ReportLab in your Python environment, and run `python3 scripts/build_resume.py` to update the downloadable resume. Review the PDF before committing it. Keep the source, build script, and PDF together in the repository so future updates are reproducible.

Local settings, credentials, Python caches, and temporary review files are excluded by `.gitignore`. Keep screenshots and other review output in `tmp/` or `output/`; files in `assets/` are intended for publication.

## Personal project licensing

The [LLM Inference Platform](https://github.com/kannamr/llm-inference-platform) is an
independent project licensed under [Apache License 2.0](https://github.com/kannamr/llm-inference-platform/blob/main/LICENSE).
It permits commercial use, modification, and redistribution subject to its terms.
Read the [licensing guide](https://github.com/kannamr/llm-inference-platform/blob/main/docs/licensing.md) for
scope, attribution, and third-party notices.

The implementation lives in its own repository, separate from this portfolio.
Keep project source code in a sibling checkout, not inside this website repository.

That license covers the standalone project only. It does not license employer
systems, the portfolio's resume or photograph, or future projects automatically.
The project's implementation status remains separate from its licensing status.
