# Atlas Security & Local-First Policy

This repository is designed to be run locally and to keep your code and compute on the machine where Atlas is installed.

Key points and operator responsibilities

- Local-first defaults
  - All LLM endpoints and the Streamlit UI are configured to bind to localhost/127.0.0.1 by default.
  - Do not change hosts/ports to public-facing addresses unless you understand the security implications and follow the guidance below.

- Per-machine configuration
  - Each user who downloads Atlas should configure their own `atlas_core/config/llm_config.yaml` and `Atlas-GUI/launch.bat` if needed.
  - The shipped `launch.bat` includes a hostname check; replace the sample hostname with your own machine name to prevent accidental use on other machines.

- GitHub integration and tokens
  - If you enable GitHub push automation (e.g., `enable_master_push: true`), you MUST use a least-privilege token scoped to the required repo operations and store it in secrets (e.g., `ATLAS_PUSH_TOKEN`).
  - Require typed confirmations for any automated push or destructive operation. Atlas enforces `require_manual_confirmation: true` by default.

- Network exposure
  - If you deliberately expose the LLM server or UI to other hosts, run them behind a firewall or reverse proxy and require authentication.
  - Use TLS (HTTPS) and authenticated proxies for any remote exposure; do not bind to 0.0.0.0 on untrusted networks.

- Access control for multi-user machines
  - If others need to run Atlas on the same host, create separate user accounts, separate working directories, and separate config files.
  - Avoid sharing a single host account or a single LLM endpoint among multiple untrusted users.

- Audit and provenance
  - Atlas maintains append-only JSONL provenance logs. Do not edit those logs manually.

Reporting security issues

Please open an issue and tag it `security` if you discover a vulnerability or an accidental exposure. Include repro steps and a suggested patch if possible.
