"""
Atlas Pre-Demo Validation Script
Run this before class to ensure everything is working
"""

import sys
from pathlib import Path

def check_dependencies():
    """Verify all required packages are installed"""
    print("🔍 Checking dependencies...")
    
    required = ['yaml', 'requests']
    missing = []
    
    for package in required:
        try:
            __import__(package if package != 'yaml' else 'yaml')
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING!")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Install missing packages: pip install {' '.join(missing)}")
        return False
    
    print("✅ All dependencies installed\n")
    return True

def check_config():
    """Verify LLM configuration"""
    print("🔍 Checking LLM configuration...")
    
    import yaml
    
    config_path = Path(__file__).parent / 'atlas_core' / 'config' / 'llm_config.yaml'
    
    if not config_path.exists():
        print("❌ Config file not found!")
        return False
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    local_endpoint = config.get('llm_endpoints', {}).get('local', {})
    url = local_endpoint.get('url', '')
    
    if '<HTPC_IP_ADDRESS>' in url:
        print(f"  ⚠️  HTPC IP not configured!")
        print(f"     Update: {config_path}")
        print(f"     Replace: <HTPC_IP_ADDRESS> with actual IP")
        return False
    
    print(f"  ✅ URL: {url}")
    print(f"  ✅ Model: {local_endpoint.get('model')}")
    print(f"  ✅ Enabled: {local_endpoint.get('enabled')}")
    
    print("✅ Configuration valid\n")
    return True

def test_llm_connection():
    """Test connection to LLM endpoint"""
    print("🔍 Testing LLM connection...")
    
    import yaml
    import requests
    
    config_path = Path(__file__).parent / 'atlas_core' / 'config' / 'llm_config.yaml'
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    endpoint = config['llm_endpoints']['local']
    
    if not endpoint['enabled']:
        print("  ⚠️  Local endpoint disabled in config")
        return False
    
    try:
        # Try to reach /api/tags endpoint (Ollama's models list)
        if '/api/chat' in endpoint['url']:
            # Ollama API
            base_url = endpoint['url'].replace('/api/chat', '')
            models_url = f"{base_url}/api/tags"
        else:
            # Fallback to OpenAI-style
            base_url = endpoint['url'].replace('/v1/chat/completions', '')
            models_url = f"{base_url}/v1/models"
        
        print(f"  Testing: {models_url}")
        
        response = requests.get(models_url, timeout=5)
        response.raise_for_status()
        
        print(f"  ✅ Connection successful!")
        print(f"  ✅ Response time: {response.elapsed.total_seconds():.2f}s")
        
        print("✅ LLM endpoint reachable\n")
        return True
    
    except requests.exceptions.ConnectionError:
        print(f"  ❌ Connection refused - Is Ollama running?")
        print(f"     On HTPC: ollama serve")
        return False
    
    except requests.exceptions.Timeout:
        print(f"  ❌ Connection timeout - Check HTPC IP and firewall")
        return False
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def create_test_error():
    """Create sample error log for testing"""
    print("🔍 Creating test error log...")
    
    test_error = """ERROR: tests/test_authentication.py::test_user_login FAILED
AssertionError: Expected status code 200, got 500

Traceback (most recent call last):
  File "tests/test_authentication.py", line 45, in test_user_login
    response = client.post('/api/login', json={'username': 'test', 'password': 'test123'})
  File "src/auth_service.py", line 28, in login_handler
    hashed = hash_password(password)
NameError: name 'hash_password' is not defined

The function 'hash_password' is used but never imported.
File: src/auth_service.py, Line 28

Exit code: 1
"""
    
    with open('test_error_demo.txt', 'w') as f:
        f.write(test_error)
    
    print("  ✅ Created: test_error_demo.txt")
    print("✅ Test error log ready\n")
    return True

def test_patch_generation():
    """Test patch generation"""
    print("🔍 Testing patch generation...")
    
    try:
        from atlas_core.tools.generate_patch import propose_patch
        
        print("  Running: propose_patch('test_error_demo.txt', 'demo_patch.diff', dry_run=True)")
        
        result = propose_patch('test_error_demo.txt', 'demo_patch.diff', dry_run=True)
        
        print(f"\n  ✅ Patch generated successfully!")
        print(f"  ✅ Confidence: {result['confidence_score']:.2f}")
        print(f"  ✅ Affected Files: {', '.join(result['affected_files'])}")
        
        print("\n✅ Patch generation working!\n")
        return True
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        print("\n❌ Patch generation failed\n")
        return False

def main():
    """Run all validation checks"""
    print("=" * 60)
    print("Atlas Pre-Demo Validation")
    print("=" * 60)
    print()
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Configuration", check_config),
        ("LLM Connection", test_llm_connection),
        ("Test Error Log", create_test_error),
        ("Patch Generation", test_patch_generation),
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} check crashed: {e}\n")
            results.append((name, False))
    
    # Summary
    print("=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    all_passed = all(result for _, result in results)
    
    print()
    if all_passed:
        print("🎉 ALL CHECKS PASSED! YOU'RE READY FOR DEMO!")
        print()
        print("Next steps:")
        print("  1. Review: DEMO_QUICK_REFERENCE.md")
        print("  2. Practice your 5-minute demo script")
        print("  3. Get a good night's sleep!")
        return 0
    else:
        print("⚠️  SOME CHECKS FAILED - Fix issues before demo")
        print()
        print("Common fixes:")
        print("  - Dependencies: pip install pyyaml requests")
        print("  - Config: Update HTPC IP in llm_config.yaml")
        print("  - LLM: Start Ollama server on HTPC")
        return 1

if __name__ == '__main__':
    sys.exit(main())
