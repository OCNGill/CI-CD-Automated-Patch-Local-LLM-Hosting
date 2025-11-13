# Atlas CI/CD Auto-fixer Agent

## Overview
**Atlas is an autonomous, safety-first GitHub Actions workflow error detection and self-healing agent. It monitors CI/CD pipeline failures, diagnoses root causes, and proposes or applies fixes using LLM-powered patch generation. Atlas is designed for dual-repo integration, robust audit trails, and human-in-the-loop safety controls.**

---

## Core Philosophy: Local-First and Secure

A fundamental design principle of Atlas is that **your code and your compute stay on your machine.**

- **No Cloud Dependency:** Unlike cloud-based AI assistants, Atlas is built to run entirely within your own environment. It uses your local hardware (e.g., a GPU running an Ollama server) to perform all analysis and code generation.
- **Your Data Stays Private:** Your source code, error logs, and other proprietary data are never sent to a third-party service. All operations happen within the security of your local network.
- **You Control the Model:** You have complete control over which Large Language Model is used, allowing you to choose models that are optimized for code, run efficiently on your hardware, and meet your security requirements.

Atlas is not a cloud service; it is a **self-hosted, private, and specialized AI agent** that you control.

For deployment and security best-practices see `SECURITY.md` (local-first defaults, GitHub token guidance, and network exposure recommendations).

Per-user setup: When other users download Atlas they should configure their own `atlas_core/config/llm_config.yaml` and use a per-user copy of `Atlas-GUI/launch.bat` or `Atlas-GUI/README_ATLAS_GUI.md` as a template. Do not commit machine-specific secrets into the repo.

---

## Key Features
- **OpenAI-compatible LLM integration** (local or cloud)
- **Propose → Verify → Refine → Apply** patch lifecycle
- **Temporary git worktree verification** (no main branch pollution)
- **Manual confirmation and rollback controls**
- **Append-only JSONL provenance logging**
- **Streamlit UI** for operator review, patch approval, and rollback
- **Windows-first workflows** (PowerShell, conda, ROCm installer integration)
- **Tested on Radeon 7900 XTX/7600 hardware**

---

## Documentation
- **Quick Start & AI Agent Guide:** `.github/copilot-instructions.md`
- **LLM API & Iteration:** [`docs/llm_integration.md`](docs/llm_integration.md)
- **Patch Lifecycle & Rollback:** [`docs/patch_lifecycle.md`](docs/patch_lifecycle.md)
- **Hardware Setup (ROCm, GPUs):** [`docs/hardware_setup.md`](docs/hardware_setup.md)
- **Streamlit UI Workflows:** [`docs/ui_workflows.md`](docs/ui_workflows.md)

---

## Getting Started
1. **Clone this repo**
2. **Set up your LLM server** (see `docs/hardware_setup.md`)
3. **Configure Atlas** (`atlas_core/config/llm_config.yaml`)
4. **Integrate with your target repo** (see `.github/copilot-instructions.md`)
5. **Start the Streamlit UI** for manual review (see `docs/ui_workflows.md`)

---

## Release Notes
### v0.1.69 (Initial Release)
- Full dual-repo architecture (agent + target integration)
- Canonical propose → verify → refine → apply patch loop
- OpenAI-compatible LLM API (local/cloud)
- Streamlit UI for patch review, manual override, and rollback
- Append-only JSONL provenance and multi-layer audit trail
- Windows-first, ROCm installer integration, tested on Radeon 7900 XTX/7600
- Modular documentation in `docs/`

---

## Contributing
- See `.github/copilot-instructions.md` for AI agent and developer onboarding
- All patches and rollbacks require manual confirmation by default
- Please open issues or PRs for feature requests and bug reports

---

## License
[MIT License](LICENSE)

---

## Maintainer
- [OCNGill](https://github.com/OCNGill)

---

## 💖 Support / Donate

If you find this project helpful, you can support ongoing work — thank you!

<p align="center">
	<img src="images/qr-paypal.png" alt="PayPal QR code" width="180" style="margin:8px;">
	<img src="images/qr-venmo.png" alt="Venmo QR code" width="180" style="margin:8px;">
</p>


**Donate:**

- [![PayPal](https://img.shields.io/badge/PayPal-Donate-009cde?logo=paypal&logoColor=white)](https://paypal.me/gillsystems) https://paypal.me/gillsystems
- [![Venmo](https://img.shields.io/badge/Venmo-Donate-3d95ce?logo=venmo&logoColor=white)](https://venmo.com/Stephen-Gill-007) https://venmo.com/Stephen-Gill-007

---


<p align="center">
	<img src="images/Gillsystems_logo_with_donation_qrcodes.png" alt="Gillsystems logo with QR codes and icons" width="800">
</p>

<p align="center">
	<a href="https://paypal.me/gillsystems"><img src="images/paypal_icon.png" alt="PayPal" width="32" style="vertical-align:middle;"></a>
	<a href="https://venmo.com/Stephen-Gill-007"><img src="images/venmo_icon.png" alt="Venmo" width="32" style="vertical-align:middle;"></a>
</p>
