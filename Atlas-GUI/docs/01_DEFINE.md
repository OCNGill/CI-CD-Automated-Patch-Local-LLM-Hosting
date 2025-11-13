# 1. DEFINE: Project Goals & User Needs

The primary goal is to create an intuitive, local, and secure web UI for operators to monitor, manage, and interact with the Atlas agent. The UI must empower users while upholding the project's "safety-first" philosophy.

## Core Philosophy: Local-First and Secure

A fundamental design principle of Atlas is that **your code and your compute stay on your machine.**

- **No Cloud Dependency:** Atlas is built to run entirely within your own environment. It uses your local hardware to perform all analysis and code generation.
- **Your Data Stays Private:** Your source code, error logs, and other proprietary data are never sent to a third-party service.
- **You Control the Model:** You have complete control over which Large Language Model is used.

The Atlas-GUI is the control panel for this self-hosted, private agent.

## Core User Stories:

*   **As an Operator, I want to...**
    *   ...see the current status of the Atlas agent at a glance.
    *   ...know which repository Atlas is currently working on.
    *   ...choose which LLM to use for patch generation so I can balance speed and quality.
    *   ...view CI/CD error logs and the agent's iterative attempts to fix them.
    *   ...compare the performance (token usage, response time) of different models.
    *   ...have a simple way to launch the application.
    *   ...feel confident and in control, with clear warnings for high-risk actions.
