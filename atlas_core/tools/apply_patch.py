"""
Atlas Patch Application Tool
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path
import tempfile

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

def apply_patch(patch_content: str, commit_message: str, push: bool):
    """
    Applies, commits, and optionally pushes a patch.
    """
    repo_root = Path(__file__).parent.parent.parent
    results = {
        "status": "fail",
        "steps": []
    }

    try:
        # Use a temporary file for the patch content
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".diff", prefix="apply-") as temp_patch_file:
            temp_patch_file.write(patch_content)
            patch_file_path = temp_patch_file.name

        # 1. Apply patch
        print("--- Applying patch ---")
        code, out = run_command(f"git apply {patch_file_path}", repo_root)
        results["steps"].append({"name": "Apply Patch", "code": code, "log": out})
        if code != 0:
            raise RuntimeError("Failed to apply patch.")

        # 2. Add changes
        print("--- Staging changes ---")
        code, out = run_command("git add .", repo_root)
        results["steps"].append({"name": "Stage Changes (git add)", "code": code, "log": out})
        if code != 0:
            raise RuntimeError("Failed to stage changes.")

        # 3. Commit changes
        print(f"--- Committing with message: '{commit_message}' ---")
        # Use a temporary file for the commit message to handle quotes and special characters
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt", prefix="commit-msg-") as temp_msg_file:
            temp_msg_file.write(commit_message)
            commit_msg_path = temp_msg_file.name

        code, out = run_command(f"git commit -F {commit_msg_path}", repo_root)
        results["steps"].append({"name": "Commit", "code": code, "log": out})
        if code != 0:
            raise RuntimeError("Failed to commit changes.")

        # 4. Push changes (if enabled)
        if push:
            print("--- Pushing to origin ---")
            # Assuming the current branch is the one to push to
            code, out = run_command("git push", repo_root)
            results["steps"].append({"name": "Push to Origin", "code": code, "log": out})
            if code != 0:
                raise RuntimeError("Failed to push changes.")
        else:
            print("--- Skipping push (dry run) ---")
            results["steps"].append({"name": "Push to Origin", "code": 0, "log": "Push skipped by user."})


        results["status"] = "pass"
        print("--- ✅ Patch applied successfully! ---")

    except Exception as e:
        print(f"--- ❌ Patch application failed: {e} ---", file=sys.stderr)
    
    finally:
        # Clean up temp files
        if 'patch_file_path' in locals() and Path(patch_file_path).exists():
            Path(patch_file_path).unlink()
        if 'commit_msg_path' in locals() and Path(commit_msg_path).exists():
            Path(commit_msg_path).unlink()
            
        # Final JSON output for the UI
        print(f"ATLAS_JSON_RESULT:{json.dumps(results)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Atlas Patch Application Tool")
    parser.add_argument("--patch-content", required=True, help="The raw diff content of the patch.")
    parser.add_argument("--commit-message", required=True, help="The commit message.")
    parser.add_argument("--push", action="store_true", help="Push the commit to the remote repository.")
    args = parser.parse_args()

    try:
        apply_patch(args.patch_content, args.commit_message, args.push)
    except Exception as e:
        print(f"An unhandled error occurred: {e}", file=sys.stderr)
        sys.exit(1)
