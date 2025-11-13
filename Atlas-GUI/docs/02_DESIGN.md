# 2. DESIGN: UI Structure & Features

This document outlines the proposed design for the Atlas-GUI Streamlit application. The design prioritizes clarity, operator control, and safety.

## UI Tabs

The application will be organized into the following tabs:

*   **`Dashboard` (Home):** A central overview page.
    *   **Agent Status:** A clear indicator showing if Atlas is `Idle`, `Monitoring`, `Generating Patch`, or `Awaiting Confirmation`.
    *   **Active Project:** Displays the target repository currently being worked on.
    *   **Active LLM:** Shows the model currently selected for patch generation.
    *   **Last Action Summary:** A log of the most recent significant event (e.g., "Patch `abc1234` applied successfully").
    *   **Safety Status:** Prominently display the status of critical safety flags like `enable_master_push`.

*   **`Workflow` (Propose → Verify → Apply):** An interactive tab to guide the operator through the core patch lifecycle.
    *   **Input:** A text area to paste a link to a failed GitHub Actions run or paste raw error logs.
    *   **Propose:** A button to trigger the `generate_patch` process. The proposed patch, explanation, and confidence score will be displayed here.
    *   **Verify:** A section to run the patch in an isolated worktree. It will stream the build and test output directly to the UI.
    *   **Apply:** If verification passes, this section will show the final `git` commands and require a manual, explicit confirmation button click to merge the patch.

*   **`Performance & Logs`:** A hub for analysis.
    *   **LLM Iteration Viewer:** A structured view of the agent's "thinking" process. For each attempt (propose, refine), it will show the prompt, the generated patch, and the test results.
    *   **Performance Metrics:** A table or chart displaying:
        *   `Model Name`
        *   `Response Time` (in seconds)
        *   `Input Tokens`
        *   `Output Tokens`
    *   **Log Viewer:** An easy way to view the raw CI/CD error logs that triggered the agent.

*   **`Configuration`:** A settings page for managing the agent.
    *   **Model Selection:** A dropdown menu to select the active LLM from the ones defined in `llm_config.yaml`.
    *   **Endpoint Management:** A view to see the configured LLM endpoints and a "Test Connection" button for each to ensure they are reachable.

*   **`History & Rollback`:** A critical safety and audit feature.
    *   **Recent Patches:** A list of recent commits made by Atlas, showing the commit hash, message, and verification status.
    *   **Rollback:** A button next to each commit to initiate a `git revert`. This will also require explicit, final confirmation.
