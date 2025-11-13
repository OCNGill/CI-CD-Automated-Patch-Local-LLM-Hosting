import streamlit as st
import yaml
from pathlib import Path
import subprocess
import tempfile
import json
import requests
from urllib.parse import urlparse, urlunparse

# --- Configuration Loading ---
def load_config():
    """Loads the YAML configuration file with robust path resolution."""
    # Get repo root by going up from Atlas-GUI/ to repo root
    repo_root = Path(__file__).parent.parent.resolve()
    config_path = repo_root / "atlas_core" / "config" / "llm_config.yaml"
    
    try:
        if not config_path.exists():
            st.error(f"Config file not found at: {config_path}")
            st.info(f"Repo root resolved to: {repo_root}")
            st.info(f"Current __file__: {Path(__file__).resolve()}")
            return None
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
            if config_data is None:
                st.warning("Config file is empty or invalid YAML")
                return None
            return config_data
    except FileNotFoundError:
        st.error(f"Config file not found: {config_path}")
        return None
    except yaml.YAMLError as e:
        st.error(f"YAML parsing error: {e}")
        return None
    except Exception as e:
        st.error(f"Unexpected error loading config: {e}")
        return None

config = load_config()

# --- UI Rendering ---
st.set_page_config(
    page_title="Atlas Self-Healing Agent",
    page_icon="🤖",
    layout="wide",
)

st.title("🤖 Atlas Self-Healing Agent")

# --- Main App ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Dashboard", "Workflow", "Performance & Logs", "Configuration", "History & Rollback", "Get More Models"
])

with tab1:
    st.header("Dashboard")
    if not config:
        st.error("Failed to load `llm_config.yaml`. Please ensure the file exists and is correctly formatted.")
    else:
        # --- Agent Status & Active Project ---
        col1, col2, col3 = st.columns(3)
        with col1:
            # Placeholder for dynamic status
            st.metric(label="Agent Status", value="Idle", delta="Monitoring", delta_color="off")
        
        with col2:
            # Assuming the first repo is the active one for now
            active_repo = list(config.get("target_repos", {}).keys())[0] if config.get("target_repos") else "N/A"
            st.metric(label="Active Project", value=active_repo)

        with col3:
            active_model = config.get("llm_endpoints", {}).get("local", {}).get("model", "N/A")
            st.metric(label="Active LLM", value=active_model)

        st.divider()

        # --- Safety Status ---
        st.subheader("Safety & Operational Status")
        safety_config = config.get("safety", {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            auto_apply = safety_config.get('enable_auto_apply', False)
            st.metric("Auto Apply Patch", "ENABLED" if auto_apply else "DISABLED", delta_color="inverse")
        
        with col2:
            master_push = safety_config.get('enable_master_push', False)
            st.metric("Auto Push to Master", "ENABLED" if master_push else "DISABLED", delta_color="inverse")

        with col3:
            manual_confirm = safety_config.get('require_manual_confirmation', True)
            st.metric("Require Manual Confirmation", "YES" if manual_confirm else "NO")

        # --- Hardware Info ---
        with st.expander("View Hardware Configuration"):
            hardware_config = config.get("hardware", {})
            if hardware_config:
                primary_gpu = hardware_config.get("primary_gpu", {})
                llm_server = hardware_config.get("llm_server", {})

                st.write(f"**Primary GPU:** {primary_gpu.get('model', 'N/A')} ({primary_gpu.get('vram_gb', 'N/A')} GB VRAM)")
                st.write(f"**LLM Server:** `{llm_server.get('host', 'N/A')}:{llm_server.get('port', 'N/A')}`")
            else:
                st.info("No hardware configuration found in `llm_config.yaml`.")


with tab2:
    st.header("Workflow (Propose → Verify → Apply)")

    # --- 1. Propose ---
    st.subheader("1. Propose Patch")
    with st.container(border=True):
        input_mode = st.radio(
            "Select Input Mode", 
            ("Manual Log Input", "GitHub Actions URL (Not Implemented)"),
            horizontal=True,
            label_visibility="collapsed"
        )

        if input_mode == "Manual Log Input":
            error_log = st.text_area("Paste the full error log here to begin:", height=250, key="error_log")
            
            if st.button("Generate Patch", type="primary"):
                if error_log:
                    # This path assumes the script is run from the Atlas-GUI directory
                    log_file_path = Path("temp_error.log")
                    with open(log_file_path, "w") as f:
                        f.write(error_log)

                    # Path to the core agent script
                    script_path = Path(__file__).parent.parent / "atlas_core" / "tools" / "generate_patch.py"
                    
                    with st.spinner("Atlas is thinking... This may take a moment."):
                        try:
                            # We assume generate_patch.py can take a log file and outputs structured JSON
                            # We also assume it's being run from the root of the project
                            process = subprocess.run(
                                ["python", str(script_path), "--log-file", str(log_file_path)],
                                capture_output=True,
                                text=True,
                                check=True,
                                cwd=Path(__file__).parent.parent # Run from the root directory
                            )
                            
                            # Assuming the script prints a JSON object to stdout
                            patch_data = json.loads(process.stdout)
                            st.session_state['patch_data'] = patch_data
                            st.success("Patch generated successfully!")

                        except subprocess.CalledProcessError as e:
                            st.error(f"Failed to generate patch. The agent returned an error:")
                            st.code(e.stderr, language="bash")
                        except json.JSONDecodeError:
                            st.error("The agent script did not return valid JSON. Cannot display patch.")
                        except Exception as e:
                            st.error(f"An unexpected error occurred: {e}")
                else:
                    st.warning("Please paste an error log before generating a patch.")

    # --- 2. Verify ---
    st.subheader("2. Verify Patch")
    with st.container(border=True):
        verify_disabled = 'patch_data' not in st.session_state
        
        if st.button("Verify Patch", disabled=verify_disabled, type="primary"):
            patch_data = st.session_state.get('patch_data')
            if patch_data:
                # Create a temporary file for the patch diff
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".diff", prefix="atlas-patch-") as temp_patch_file:
                    temp_patch_file.write(patch_data['patch_diff'])
                    patch_file_path = temp_patch_file.name

                # Path to the verification script
                script_path = Path(__file__).parent.parent / "atlas_core" / "tools" / "verify_patch.py"
                
                st.write("--- Verification Log ---")
                log_placeholder = st.empty()
                full_log = ""
                
                try:
                    # Use Popen to stream output in real-time
                    process = subprocess.Popen(
                        ["python", "-u", str(script_path), "--patch-file", patch_file_path],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        cwd=Path(__file__).parent.parent, # Run from the root directory
                        bufsize=1,
                        universal_newlines=True
                    )

                    final_json_result = None
                    for line in iter(process.stdout.readline, ''):
                        if line.startswith("ATLAS_JSON_RESULT:"):
                            final_json_result = json.loads(line.replace("ATLAS_JSON_RESULT:", "").strip())
                            break # Stop reading log here
                        full_log += line
                        log_placeholder.code(full_log, language="bash")
                    
                    process.wait()

                    if final_json_result:
                        st.session_state['verification_result'] = final_json_result
                        if final_json_result.get("verification_status") == "pass":
                            st.success("✅ Verification Passed!")
                        else:
                            st.error("❌ Verification Failed. See logs for details.")
                    else:
                        st.error("Verification script did not return a final result.")

                except Exception as e:
                    st.error(f"An unexpected error occurred during verification: {e}")
                    st.code(full_log, language="bash") # Show what we got
            else:
                st.warning("No patch data found to verify.")

        if 'verification_result' in st.session_state:
            result = st.session_state['verification_result']
            if result.get("verification_status") == "pass":
                st.success("✅ Verification Passed")
            else:
                st.error("❌ Verification Failed")
            
            with st.expander("Show Full Verification Log"):
                for step in result.get("steps", []):
                    st.write(f"**Step:** {step['name']} (Exit Code: {step['code']})")
                    st.code(step['log'], language="bash")


    # --- 3. Apply Patch
    st.subheader("3. Apply Patch")
    with st.container(border=True):
        apply_disabled = st.session_state.get('verification_result', {}).get('verification_status') != 'pass'
        
        if not apply_disabled:
            st.info("Verification passed. The patch is ready to be applied.")
            
            # Check the safety setting for pushing to master
            master_push_enabled = config.get("safety", {}).get("enable_master_push", False)
            
            commit_message = f"atlas: {st.session_state['patch_data'].get('explanation', 'Applied patch')}"

            if master_push_enabled:
                st.warning("⚠️ **Master Push Enabled:** This action will commit and push directly to the main branch.")
                confirmation_text = "I authorize push to master"
                user_confirmation = st.text_input(f"Type the following to confirm: `{confirmation_text}`")
                
                apply_button_disabled = user_confirmation != confirmation_text
                if st.button("Execute and Push", disabled=apply_button_disabled, type="primary"):
                    run_apply_script(push=True)
            else:
                st.info("Master push is disabled. The patch will be committed locally but not pushed.")
                if st.button("Commit Locally", type="primary"):
                    run_apply_script(push=False)
        else:
            st.info("Application step will appear here after a patch is successfully verified.")


with tab3:
    st.header("Performance & Logs")

    log_dir = Path(__file__).parent.parent / 'atlas_core' / 'logs'
    perf_log_path = log_dir / 'performance.jsonl'
    iter_log_path = log_dir / 'iterations.jsonl'

    # --- Performance Metrics ---
    st.subheader("LLM Performance Metrics")
    if not perf_log_path.exists():
        st.info("No performance data recorded yet. Generate a patch to see metrics here.")
    else:
        perf_data = []
        with open(perf_log_path, 'r') as f:
            for line in f:
                perf_data.append(json.loads(line))
        
        if not perf_data:
            st.info("No performance data recorded yet.")
        else:
            # Use a dataframe for better display and sorting
            import pandas as pd
            df = pd.DataFrame(perf_data)
            
            # Formatting for better readability
            df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            df['response_time_s'] = df['response_time_ms'] / 1000
            df['tokens_per_second'] = df['tokens_per_second'].round(2)
            
            st.dataframe(df[{
                'timestamp', 'model', 'response_time_s', 
                'prompt_tokens', 'response_tokens', 'tokens_per_second', 'confidence_score'
            }], use_container_width=True)

    st.divider()

    # --- Iteration Viewer ---
    st.subheader("Agent Iteration Viewer")
    if not iter_log_path.exists():
        st.info("No iteration data recorded yet. Generate a patch to see the agent's thinking process.")
    else:
        iter_data = []
        with open(iter_log_path, 'r') as f:
            for line in f:
                iter_data.append(json.loads(line))
        
        if not iter_data:
            st.info("No iteration data recorded yet.")
        else:
            # Display the most recent iteration first
            for i, entry in enumerate(reversed(iter_data)):
                with st.expander(f"{entry['timestamp']} - Model: {entry['model']}"):
                    st.write("##### Prompt Sent to LLM:")
                    st.text(entry['prompt'])
                    st.write("---")
                    st.write("##### Raw JSON Response from LLM:")
                    st.json(entry['response'])

    st.divider()

    # --- Placeholder for Advanced Hardware Metrics ---
    st.subheader("Advanced Hardware Monitoring (Future)")
    st.info(
        """
        This section will display real-time hardware metrics (GPU, VRAM, CPU usage) 
        from the machine running the LLM.
        
        **Implementation Plan:**
        1. Create a lightweight metrics agent/script to run on the LLM server (e.g., the HTPC).
        2. This agent will use libraries like `psutil` (for CPU/RAM) and `rocm_smi` (for AMD GPUs) 
           or `nvitop` (for NVIDIA GPUs) to collect system stats.
        3. The agent will expose these stats on a simple HTTP endpoint.
        4. This UI will then poll that endpoint to display live hardware data.
        """
    )


with tab4:
    st.header("Configuration")
    if not config:
        st.error("Failed to load `llm_config.yaml`.")
    else:
        st.subheader("Model Selection")

        hardware_config = config.get("hardware", {})
        recommended_models = hardware_config.get("primary_gpu", {}).get("recommended_models", [])
        
        current_model = config.get("llm_endpoints", {}).get("local", {}).get("model")
        
        # Get index of current model in recommended_models, default to 0 if not found
        try:
            current_model_index = recommended_models.index(current_model)
        except (ValueError, TypeError):
            current_model_index = 0

        new_model = st.selectbox(
            "Select a model for the local endpoint:",
            options=recommended_models,
            index=current_model_index,
            help="These models are recommended in your config. The agent will use the selected model for patch generation."
        )

        if st.button("Save Model Selection"):
            config["llm_endpoints"]["local"]["model"] = new_model
            config_path = Path(__file__).parent.parent / "atlas_core" / "config" / "llm_config.yaml"
            try:
                with open(config_path, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False, sort_keys=False)
                st.success(f"Configuration updated! Local model set to `{new_model}`.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to write to config file: {e}")

        st.divider()

        st.subheader("LLM Endpoints")
        endpoints = config.get("llm_endpoints", {})
        
        # Display Local Endpoint
        local_endpoint = endpoints.get("local", {})
        if local_endpoint:
            with st.container(border=True):
                st.write("##### Local Endpoint")
                st.text(f"URL: {local_endpoint.get('url', 'Not set')}")
                st.text(f"Model: {local_endpoint.get('model', 'Not set')}")
                st.text(f"Status: {'Enabled' if local_endpoint.get('enabled') else 'Disabled'}")
                if st.button("Test Connection (Local)"):
                    st.info("Connection test logic not yet implemented.")

        # Display Cloud Endpoint
        cloud_endpoint = endpoints.get("cloud", {})
        if cloud_endpoint:
            with st.container(border=True):
                st.write("##### Cloud Endpoint")
                st.text(f"URL: {cloud_endpoint.get('url', 'Not set')}")
                st.text(f"Model: {cloud_endpoint.get('model', 'Not set')}")
                st.text(f"Status: {'Enabled' if cloud_endpoint.get('enabled') else 'Disabled'}")
                if st.button("Test Connection (Cloud)", disabled=True):
                    # Placeholder for connection test logic
                    pass

with tab5:
    st.header("History & Rollback")
    st.info("This section shows recent commits made by Atlas and allows you to revert them.")

    # --- Git History ---
    history_script_path = Path(__file__).parent.parent / "atlas_core" / "tools" / "git_history.py"
    try:
        process = subprocess.run(
            ["python", str(history_script_path)],
            capture_output=True,
            text=True,
            check=True,
            cwd=Path(__file__).parent.parent
        )
        commit_history = json.loads(process.stdout)
        st.session_state['commit_history'] = commit_history
    except (subprocess.CalledProcessError, json.JSONDecodeError) as e:
        st.error(f"Failed to fetch commit history: {e}")
        st.code(process.stderr if 'process' in locals() else "", language="bash")
        commit_history = []

    # --- Display History and Rollback UI ---
    if not commit_history:
        st.write("No Atlas commits found in the recent history.")
    else:
        for commit in commit_history:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Commit:** `{commit['hash']}`")
                    st.write(f"**Subject:** {commit['subject']}")
                    st.caption(f"Authored by {commit['author']} {commit['date']}")
                
                with col2:
                    if st.button("Rollback", key=f"rollback_{commit['hash']}", type="secondary"):
                        st.session_state['commit_to_rollback'] = commit
                
                # --- Rollback Confirmation Modal ---
                if st.session_state.get('commit_to_rollback', {}).get('hash') == commit['hash']:
                    st.warning(f"You are about to revert the commit: **{commit['subject']}**")
                    
                    master_push_enabled = config.get("safety", {}).get("enable_master_push", False)
                    
                    if master_push_enabled:
                        confirmation_text = "I authorize rollback and push"
                        user_confirmation = st.text_input(f"Type `{confirmation_text}` to confirm:", key=f"confirm_{commit['hash']}")
                        
                        if st.button("Execute Rollback and Push", key=f"exec_{commit['hash']}", type="primary", disabled=(user_confirmation != confirmation_text)):
                            run_rollback_script(commit['hash'], push=True)
                    else:
                        if st.button("Execute Local Rollback", key=f"exec_local_{commit['hash']}", type="primary"):
                            run_rollback_script(commit['hash'], push=False)
                    
                    if st.button("Cancel", key=f"cancel_{commit['hash']}"):
                        del st.session_state['commit_to_rollback']
                        st.rerun()

def run_apply_script(push: bool):
    """Helper function to call the apply_patch.py script."""
    patch_content = st.session_state['patch_data']['patch_diff']
    commit_message = st.session_state['commit_message']
    
    script_path = Path(__file__).parent.parent / "atlas_core" / "tools" / "apply_patch.py"
    
    command = [
        "python", "-u", str(script_path),
        "--patch-content", patch_content,
        "--commit-message", commit_message
    ]
    if push:
        command.append("--push")

    st.write("--- Application Log ---")
    log_placeholder = st.empty()
    full_log = ""
    
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=Path(__file__).parent.parent,
            bufsize=1,
            universal_newlines=True
        )

        final_json_result = None
        for line in iter(process.stdout.readline, ''):
            if line.startswith("ATLAS_JSON_RESULT:"):
                final_json_result = json.loads(line.replace("ATLAS_JSON_RESULT:", "").strip())
                break
            full_log += line
            log_placeholder.code(full_log, language="bash")
        
        process.wait()

        if final_json_result:
            if final_json_result.get("status") == "pass":
                st.success("✅ Patch applied successfully!")
                # Clear session state to reset the workflow
                for key in ['patch_data', 'verification_result']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
            else:
                st.error("❌ Patch application failed. See logs for details.")
        else:
            st.error("Application script did not return a final result.")

    except Exception as e:
        st.error(f"An unexpected error occurred during application: {e}")
        st.code(full_log, language="bash")


def run_rollback_script(commit_hash: str, push: bool):
    """Helper function to call the rollback_commit.py script."""
    script_path = Path(__file__).parent.parent / "atlas_core" / "tools" / "rollback_commit.py"
    
    command = [
        "python", "-u", str(script_path),
        "--hash", commit_hash
    ]
    if push:
        command.append("--push")

    st.write("--- Rollback Log ---")
    log_placeholder = st.empty()
    full_log = ""
    
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=Path(__file__).parent.parent,
            bufsize=1,
            universal_newlines=True
        )

        final_json_result = None
        for line in iter(process.stdout.readline, ''):
            if line.startswith("ATLAS_JSON_RESULT:"):
                final_json_result = json.loads(line.replace("ATLAS_JSON_RESULT:", "").strip())
                break
            full_log += line
            log_placeholder.code(full_log, language="bash")
        
        process.wait()

        if final_json_result:
            if final_json_result.get("status") == "pass":
                st.success("✅ Rollback successful!")
                # Clear state and rerun to refresh history
                if 'commit_to_rollback' in st.session_state:
                    del st.session_state['commit_to_rollback']
                st.rerun()
            else:
                st.error("❌ Rollback failed. See logs for details.")
        else:
            st.error("Rollback script did not return a final result.")

    except Exception as e:
        st.error(f"An unexpected error occurred during rollback: {e}")
        st.code(full_log, language="bash")

with tab6:
    st.header("Get More Models")
    st.write("Manage the LLMs available on your Ollama server.")

    with st.expander("🛠️ Tips for Fast, Local-First Setup"):
        st.markdown(
            """
            - **Use SSD storage** to speed up model loading and swapping.
            - **Pre-fetch models** during off-peak hours if your ISP throttles.
            - **Check model sizes** before pulling—some exceed 100GB.
            - Use `ollama list` on the server to verify local availability and avoid redundant downloads.
            """
        )

    if not config:
        st.error("Failed to load `llm_config.yaml`. Cannot connect to Ollama server.")
    else:
        try:
            # Construct base URL for Ollama API
            local_endpoint_url = config.get("llm_endpoints", {}).get("local", {}).get("url", "")
            if not local_endpoint_url:
                raise ValueError("Local LLM endpoint URL not configured.")
            
            parsed_url = urlparse(local_endpoint_url)
            base_ollama_url = urlunparse((parsed_url.scheme, parsed_url.netloc, '', '', '', ''))

            # --- List Local Models ---
            st.subheader("Available Local Models")
            with st.spinner("Fetching models from Ollama server..."):
                tags_url = f"{base_ollama_url}/api/tags"
                response = requests.get(tags_url, timeout=10)
                response.raise_for_status()
                models_data = response.json().get("models", [])
                
                if models_data:
                    import pandas as pd
                    df = pd.DataFrame(models_data)
                    df['size_gb'] = (df['size'] / 1e9).round(2)
                    df['modified_at'] = pd.to_datetime(df['modified_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
                    st.dataframe(df[['name', 'size_gb', 'modified_at']], use_container_width=True)
                else:
                    st.info("No models found on the Ollama server.")

            st.divider()

            # --- Pull New Model ---
            st.subheader("Pull a New Model")
            model_to_pull = st.text_input("Enter model name to pull (e.g., `codellama:13b`):", key="model_to_pull")
            
            if st.button("Pull Model", type="primary"):
                if model_to_pull:
                    pull_url = f"{base_ollama_url}/api/pull"
                    payload = {"name": model_to_pull, "stream": True}
                    
                    st.write(f"--- Pulling `{model_to_pull}` ---")
                    log_placeholder = st.empty()
                    full_log = ""
                    
                    try:
                        with requests.post(pull_url, json=payload, stream=True, timeout=30) as r:
                            r.raise_for_status()
                            for chunk in r.iter_lines():
                                if chunk:
                                    line_data = json.loads(chunk.decode('utf-8'))
                                    status = line_data.get("status", "")
                                    
                                    # For progress bars
                                    total = line_data.get("total", 0)
                                    completed = line_data.get("completed", 0)
                                    
                                    if "error" in line_data:
                                        st.error(f"Error pulling model: {line_data['error']}")
                                        break
                                    
                                    if total > 0:
                                        progress = completed / total
                                        full_log += f"{status} - {progress:.1%}\n"
                                    else:
                                        full_log += f"{status}\n"
                                    
                                    log_placeholder.code(full_log, language="bash")
                        
                        st.success(f"Successfully pulled `{model_to_pull}`. Refreshing model list...")
                        st.rerun()

                    except requests.exceptions.RequestException as e:
                        st.error(f"Failed to connect to Ollama server: {e}")
                else:
                    st.warning("Please enter a model name to pull.")

        except Exception as e:
            st.error(f"An error occurred while managing models: {e}")
