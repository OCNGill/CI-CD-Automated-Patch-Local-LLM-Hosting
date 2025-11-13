"""
Atlas Rollback Tool
"""
import argparse
import subprocess
import sys
from pathlib import Path

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

def rollback_commit(commit_hash: str, push: bool):
    """
    Reverts a specific commit and optionally pushes the revert.
    """
    repo_root = Path(__file__).parent.parent.parent
    results = {
        "status": "fail",
        "steps": []
    }

    try:
        # 1. Revert commit
        print(f"--- Reverting commit: {commit_hash} ---")
        # --no-edit prevents the editor from opening for a commit message
        code, out = run_command(f"git revert {commit_hash} --no-edit", repo_root)
        results["steps"].append({"name": f"Revert {commit_hash}", "code": code, "log": out})
        if code != 0:
            raise RuntimeError("Failed to revert commit.")

        # 2. Push changes (if enabled)
        if push:
            print("--- Pushing revert to origin ---")
            code, out = run_command("git push", repo_root)
            results["steps"].append({"name": "Push Revert", "code": code, "log": out})
            if code != 0:
                raise RuntimeError("Failed to push revert commit.")
        else:
            print("--- Skipping push (dry run) ---")
            results["steps"].append({"name": "Push Revert", "code": 0, "log": "Push skipped by user."})

        results["status"] = "pass"
        print("--- ✅ Rollback successful! ---")

    except Exception as e:
        print(f"--- ❌ Rollback failed: {e} ---", file=sys.stderr)
    
    finally:
        # Final JSON output for the UI
        import json
        print(f"ATLAS_JSON_RESULT:{json.dumps(results)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Atlas Rollback Tool")
    parser.add_argument("--hash", required=True, help="The commit hash to revert.")
    parser.add_argument("--push", action="store_true", help="Push the revert commit to the remote repository.")
    args = parser.parse_args()

    try:
        rollback_commit(args.hash, args.push)
    except Exception as e:
        print(f"An unhandled error occurred: {e}", file=sys.stderr)
        sys.exit(1)
