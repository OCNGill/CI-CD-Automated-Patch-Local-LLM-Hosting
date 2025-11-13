"""
Atlas Git History Tool
"""
import subprocess
import json
import sys

def get_atlas_history(limit=20):
    """
    Retrieves the git log for commits made by Atlas.
    """
    try:
        # Using a custom format to easily parse the output
        # %H: commit hash, %an: author name, %ar: author date, relative, %s: subject
        # Using a unique separator to handle multi-line subjects
        log_format = '{"hash": "%H", "author": "%an", "date": "%ar", "subject": "%s"},'
        
        # The command filters for commits where the subject starts with "atlas:"
        command = f'git log --grep="^atlas:" --pretty=format:{log_format} -n {limit}'
        
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            shell=True,
            check=True,
            cwd=Path(__file__).parent.parent.parent # Run from repo root
        )
        
        # Wrap the output in a list to form a valid JSON array
        json_output = f"[{process.stdout.strip().rstrip(',')}]"
        
        commits = json.loads(json_output)
        return commits

    except (subprocess.CalledProcessError, json.JSONDecodeError):
        # If git log fails or returns no commits, return an empty list
        return []
    except Exception as e:
        print(f"An error occurred while fetching git history: {e}", file=sys.stderr)
        return []

if __name__ == "__main__":
    from pathlib import Path
    history = get_atlas_history()
    # Print the final JSON list to stdout
    print(json.dumps(history))
