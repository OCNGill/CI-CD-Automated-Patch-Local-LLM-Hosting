"""
Atlas Patch Generation Tool
Propose → Verify → Refine → Apply lifecycle
"""

import argparse
import json
import requests
import yaml
from pathlib import Path
from datetime import datetime

def load_llm_config():
    """Load LLM configuration from yaml"""
    config_path = Path(__file__).parent.parent / 'config' / 'llm_config.yaml'
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def call_llm(prompt: str, config: dict) -> dict:
    """
    Call Ollama LLM endpoint with structured JSON response requirement
    
    Returns:
        dict with keys: confidence_score, patch_diff, explanation, affected_files, test_commands
    """
    endpoint = config['llm_endpoints']['local']
    
    if not endpoint['enabled']:
        raise RuntimeError("Local LLM endpoint not enabled in config")
    
    system_prompt = """You are Atlas, a CI/CD error diagnosis and patch generation expert.
You MUST respond with valid JSON ONLY, no markdown formatting, no explanations outside the JSON.

Required JSON schema:
{
  "confidence_score": 0.0-1.0,
  "patch_diff": "unified diff format",
  "explanation": "human-readable rationale",
  "affected_files": ["list", "of", "files"],
  "test_commands": ["command1", "command2"]
}"""
    
    payload = {
        "model": endpoint['model'],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "stream": False  # Disable streaming for JSON response
    }
    
    try:
        response = requests.post(
            endpoint['url'],
            json=payload,
            timeout=endpoint.get('timeout_seconds', 300)
        )
        response.raise_for_status()
        
        result = response.json()
        
        # Ollama returns the response in result['message']['content']
        if 'message' in result and 'content' in result['message']:
            content = result['message']['content']
        else:
            raise ValueError(f"Unexpected Ollama response format: {result}")
        
        # Parse JSON response
        try:
            patch_data = json.loads(content)
            
            # Validate schema
            required_keys = ['confidence_score', 'patch_diff', 'explanation', 'affected_files', 'test_commands']
            if not all(key in patch_data for key in required_keys):
                raise ValueError(f"Missing required keys. Expected: {required_keys}")
            
            return patch_data
        
        except json.JSONDecodeError as e:
            print(f"❌ LLM returned invalid JSON: {e}")
            print(f"Response: {content}")
            raise
    
    except requests.exceptions.RequestException as e:
        print(f"❌ LLM endpoint unreachable: {e}")
        raise

def log_performance_and_iteration(prompt, patch_data, raw_response, config):
    """Logs performance metrics and the iteration details to persistent files."""
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(exist_ok=True)
    
    # --- Log Performance ---
    perf_log_path = log_dir / 'performance.jsonl'
    
    # Extract performance data from Ollama's response
    duration_ns = raw_response.get('total_duration', 0)
    prompt_tokens = raw_response.get('prompt_eval_count', 0)
    response_tokens = raw_response.get('eval_count', 0)
    
    perf_entry = {
        "timestamp": datetime.now().isoformat(),
        "model": config['llm_endpoints']['local']['model'],
        "response_time_ms": duration_ns / 1_000_000,
        "prompt_tokens": prompt_tokens,
        "response_tokens": response_tokens,
        "tokens_per_second": response_tokens / (duration_ns / 1_000_000_000) if duration_ns > 0 else 0,
        "confidence_score": patch_data.get('confidence_score')
    }
    
    with open(perf_log_path, 'a') as f:
        f.write(json.dumps(perf_entry) + '\n')

    # --- Log Iteration ---
    iteration_log_path = log_dir / 'iterations.jsonl'
    iteration_entry = {
        "timestamp": datetime.now().isoformat(),
        "model": config['llm_endpoints']['local']['model'],
        "prompt": prompt,
        "response": patch_data
    }
    with open(iteration_log_path, 'a') as f:
        f.write(json.dumps(iteration_entry) + '\n')


def propose_patch(error_log_path: str, output_path: str = 'suggested_patch.diff', dry_run: bool = False, quiet: bool = False):
    """
    Generate patch proposal from error logs
    
    Phase 1: Propose
    """
    if not quiet:
        print("🔄 Atlas: Analyzing error logs...")
    
    # Load error context
    with open(error_log_path, 'r') as f:
        error_logs = f.read()
    
    # Load configuration
    config = load_llm_config()
    
    # Construct diagnostic prompt
    prompt = f"""Analyze this CI/CD failure and propose a patch to fix it.

Error Logs:
{error_logs}

Provide a structured JSON response with:
1. confidence_score: Your confidence this patch will work (0.0-1.0)
2. patch_diff: Unified diff format patch
3. explanation: Clear explanation of the fix
4. affected_files: List of files modified
5. test_commands: Commands to validate the fix
"""
    
    # Call LLM
    try:
        # We need the raw response for metrics, so we'll adjust the call_llm logic slightly
        endpoint = config['llm_endpoints']['local']
        system_prompt = """You are Atlas, a CI/CD error diagnosis and patch generation expert.
You MUST respond with valid JSON ONLY, no markdown formatting, no explanations outside the JSON.

Required JSON schema:
{
  "confidence_score": 0.0-1.0,
  "patch_diff": "unified diff format",
  "explanation": "human-readable rationale",
  "affected_files": ["list", "of", "files"],
  "test_commands": ["command1", "command2"]
}"""
        payload = {
            "model": endpoint['model'],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        response = requests.post(
            endpoint['url'],
            json=payload,
            timeout=endpoint.get('timeout_seconds', 300)
        )
        response.raise_for_status()
        raw_llm_response = response.json()
        
        content = raw_llm_response.get('message', {}).get('content', '')
        if not content:
            raise ValueError(f"Unexpected Ollama response format: {raw_llm_response}")
            
        patch_data = json.loads(content)
        
        # Log performance and iteration details
        log_performance_and_iteration(prompt, patch_data, raw_llm_response, config)

        if not quiet:
            print(f"\n✅ Patch Generated")
            print(f"   Confidence: {patch_data['confidence_score']:.2f}")
            print(f"   Affected Files: {', '.join(patch_data['affected_files'])}")
            print(f"\n📝 Explanation:\n{patch_data['explanation']}")
            
            if patch_data['confidence_score'] < 0.6:
                print(f"\n⚠️  Low confidence warning: {patch_data['confidence_score']:.2f}")
        
        # Save patch and metadata
        if not dry_run:
            # Save diff
            with open(output_path, 'w') as f:
                f.write(patch_data['patch_diff'])
            
            if not quiet:
                print(f"\n💾 Patch saved to: {output_path}")
            
            # Save metadata for provenance
            metadata_path = output_path.replace('.diff', '_metadata.json')
            metadata = {
                'timestamp': datetime.now().isoformat(),
                'patch_id': f"atlas-patch-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                'confidence_score': patch_data['confidence_score'],
                'explanation': patch_data['explanation'],
                'affected_files': patch_data['affected_files'],
                'test_commands': patch_data['test_commands'],
                'error_log_source': error_log_path
            }
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            if not quiet:
                print(f"💾 Metadata saved to: {metadata_path}")
                print(f"\n📋 Next Steps:")
                print(f"   1. Review patch: cat {output_path}")
                print(f"   2. Verify patch: atlas verify --patch {output_path}")
        
        return patch_data
    
    except Exception as e:
        if not quiet:
            print(f"\n❌ Patch generation failed: {e}")
        raise

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Atlas Patch Generation Tool")
    parser.add_argument("--log-file", required=True, help="Path to the error log file.")
    parser.add_argument("--output-path", default="suggested_patch.diff", help="Path to save the generated patch file.")
    parser.add_argument("--json-output", action="store_true", help="Output the patch data as a single JSON string to stdout.")
    
    args = parser.parse_args()

    try:
        # When json_output is true, we run in 'quiet' mode to suppress human-readable prints
        patch_result = propose_patch(args.log_file, args.output_path, quiet=args.json_output)
        
        if args.json_output:
            # Print the final JSON object to stdout for the Streamlit app to capture
            print(json.dumps(patch_result))
            
    except Exception as e:
        # If something fails, print the error to stderr and exit
        # This is important so the Streamlit app can capture it
        import sys
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)
