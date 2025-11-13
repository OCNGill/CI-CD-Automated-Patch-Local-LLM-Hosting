"""
Atlas Patch Verification Tool
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path
import yaml
import tempfile
import shutil

def load_config():
    """Loads the YAML configuration file."""
    config_path = Path(__file__).parent.parent / "config" / "llm_config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def run_command(command, cwd):
    """Runs a command and captures its output, streaming it live."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True,
        cwd=cwd
    )
    output = []
    for line in iter(process.stdout.readline, ''):
        print(line, end='') # Print to parent process stdout for live streaming
        sys.stdout.flush()
        output.append(line)
    
    process.wait()
    return process.returncode, "".join(output)

def verify_patch(patch_file_path: str):
    """
    Verifies a patch in an isolated git worktree.
    Follows the logic from docs/patch_lifecycle.md.
    """
    config = load_config()
    repo_root = Path(__file__).parent.parent.parent
    worktree_name = f"atlas-verify-{Path(patch_file_path).stem}"
    worktree_path = repo_root / worktree_name
    results = {
        "verification_status": "fail",
        "steps": []
    }

    try:
        # 1. Create isolated worktree
        print(f"--- Creating temporary worktree: {worktree_name} ---")
        if worktree_path.exists():
            shutil.rmtree(worktree_path)
        
        code, out = run_command(f"git worktree add {worktree_name}", repo_root)
        results["steps"].append({"name": "Create Worktree", "code": code, "log": out})
        if code != 0:
            raise RuntimeError("Failed to create git worktree.")

        # 2. Apply patch
        print(f"--- Applying patch: {patch_file_path} ---")
        # We need to copy the patch file into the worktree to apply it
        shutil.copy(patch_file_path, worktree_path)
        patch_filename_in_worktree = Path(patch_file_path).name
        
        code, out = run_command(f"git apply {patch_filename_in_worktree}", worktree_path)
        results["steps"].append({"name": "Apply Patch", "code": code, "log": out})
        if code != 0:
            raise RuntimeError("Failed to apply patch.")

        # 3. Run build and test commands
        target_repo_key = list(config.get("target_repos", {}).keys())[0]
        target_repo_config = config["target_repos"][target_repo_key]
        
        build_command = target_repo_config.get("build_command")
        test_commands = target_repo_config.get("test_commands", [])

        if build_command:
            print(f"--- Running Build Command: {build_command} ---")
            code, out = run_command(build_command, worktree_path)
            results["steps"].append({"name": f"Build: {build_command}", "code": code, "log": out})
            if code != 0:
                raise RuntimeError("Build command failed.")

        for cmd in test_commands:
            print(f"--- Running Test Command: {cmd} ---")
            code, out = run_command(cmd, worktree_path)
            results["steps"].append({"name": f"Test: {cmd}", "code": code, "log": out})
            if code != 0:
                raise RuntimeError(f"Test command failed: {cmd}")

        results["verification_status"] = "pass"
        print("--- ✅ Verification successful! ---")

    except Exception as e:
        print(f"--- ❌ Verification failed: {e} ---", file=sys.stderr)
        # The error is already part of the results steps

    finally:
        # 4. Clean up worktree
        print(f"--- Cleaning up worktree: {worktree_name} ---")
        if worktree_path.exists():
            shutil.rmtree(worktree_path)
        
        # This command is needed to finalize the removal
        run_command(f"git worktree prune", repo_root)
        
        # Final JSON output for the UI
        print(f"ATLAS_JSON_RESULT:{json.dumps(results)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Atlas Patch Verification Tool")
    parser.add_argument("--patch-file", required=True, help="Path to the patch diff file to verify.")
    args = parser.parse_args()

    try:
        verify_patch(args.patch_file)
    except Exception as e:
        print(f"An unhandled error occurred: {e}", file=sys.stderr)
        sys.exit(1)
