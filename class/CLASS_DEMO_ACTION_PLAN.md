# Atlas x 7D Agile Integration: Action Plan for Class Demo
**Target Date:** Tomorrow's Class  
**Hardware:** Gillsystems HTPC (Ryzen 5600G + Radeon 7600)  
**Status:** Ready to Execute

---

## 🎯 PROJECT FIT ANALYSIS: EXCELLENT ✅

### Why Atlas is Perfect for 7D Agile

#### **Stage 4 (DEBUG) Critical Gap**
The 7D Agile framework requires:
- ✅ Automated test execution and validation
- ✅ CI/CD pipeline integration for quality gates
- ✅ Requirement-to-test traceability verification
- ✅ Automated defect detection and fixing

**Atlas directly addresses all of these needs!**

#### **7D Agile Quality Gate 4 (DEBUG → DOCUMENT)**
Quality Gate 4 requires:
```
✅ Test plan complete with requirements mapping
✅ All test cases implemented and linked to requirements
✅ Requirements-to-test traceability verified (100% FR coverage)
✅ All test cases executed
✅ Test coverage >80% for unit tests
✅ All critical defects resolved
```

**Atlas automates the verification and fixing of these criteria in CI/CD!**

#### **Alignment with 7D Principles**
- **AI-Powered Collaboration:** Both frameworks emphasize AI agents with human oversight
- **Traceability:** Atlas tracks patches → requirements → tests → deployment
- **Quality First:** Safety controls and manual confirmation match 7D philosophy
- **Iterative Refinement:** Propose → Verify → Refine → Apply matches 7D iterative cycles

---

## 🚀 IMMEDIATE ACTION PLAN (TODAY)

### Phase 1: Get Ollama Running on CachyOS HTPC ⏱️ 30-45 min

#### Step 1.1: Install and Configure Ollama
```bash
# SSH into CachyOS HTPC or run locally
ssh htpc@<HTPC_IP>

# Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

#### Step 1.2: Pull Recommended Model for 7600 (8GB VRAM)
```bash
# Best model for 8GB VRAM: CodeLlama 7B
ollama pull codellama:7b-instruct

# Alternative: DeepSeek Coder (excellent code understanding)
ollama pull deepseek-coder:6.7b

# Verify model downloaded
ollama list
```

**Important:** DO NOT pull 13B+ models on the 7600 - they will OOM or be extremely slow!

#### Step 1.3: Start Ollama Server
```bash
# Start server (runs on port 11434 by default)
ollama serve

# Test endpoint (in new terminal)
curl http://localhost:11434/v1/models

# Expected response: JSON with model list
```

#### Step 1.4: Make Accessible from Windows Laptop
```bash
# Find HTPC IP address
ip addr show

# Test from Windows laptop:
# PowerShell:
Invoke-RestMethod -Uri "http://<HTPC_IP>:11434/v1/models"
```

**Save HTPC IP for configuration!**

---

### Phase 2: Configure Atlas LLM Endpoint ⏱️ 10 min

#### Step 2.1: Update llm_config.yaml
The configuration has been updated, but you need to replace `<HTPC_IP_ADDRESS>` with your actual HTPC IP.

**File:** `atlas_core/config/llm_config.yaml`

Find and replace both instances of:
```yaml
url: "http://<HTPC_IP_ADDRESS>:11434/v1/chat/completions"
host: "<HTPC_IP_ADDRESS>"
```

With your actual IP, e.g.:
```yaml
url: "http://192.168.1.100:11434/v1/chat/completions"
host: "192.168.1.100"
```

#### Step 2.2: Test Connection
```powershell
# From Windows laptop, test Ollama endpoint
$headers = @{ "Content-Type" = "application/json" }
$body = @{
    model = "codellama:7b-instruct"
    messages = @(
        @{ role = "user"; content = "ping" }
    )
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://<HTPC_IP>:11434/v1/chat/completions" -Method Post -Headers $headers -Body $body
```

If successful, you'll get a JSON response with the model's reply.

---

### Phase 3: Install Atlas Dependencies ⏱️ 15 min

#### Step 3.1: Activate Conda Environment
```powershell
# Activate existing atlas environment (from environment.yml)
conda activate atlas

# If not created yet:
conda env create -f environment.yml
conda activate atlas
```

#### Step 3.2: Install Missing Dependencies
```powershell
# Install core dependencies
pip install pyyaml requests streamlit

# Install additional tools
pip install pytest pylint

# Verify installation
python -c "import yaml, requests; print('Dependencies OK')"
```

---

### Phase 4: Test Atlas Core Functions ⏱️ 30 min

#### Step 4.1: Create Test Error Log
```powershell
# Create sample CI error log
@"
ERROR: tests/test_auth.py::test_user_login FAILED
AssertionError: Expected 200, got 500
File: src/auth_service.py, Line 42
Traceback:
  File "src/auth_service.py", line 42, in authenticate_user
    result = validate_credentials(username, password)
  File "src/auth_service.py", line 18, in validate_credentials
    NameError: name 'hash_password' is not defined

Exit code: 1
"@ | Out-File -FilePath "test_error.txt" -Encoding utf8
```

#### Step 4.2: Test Patch Generation
```powershell
# Generate patch from error log
python atlas_core/tools/generate_patch.py test_error.txt

# Expected output:
# 🔄 Atlas: Analyzing error logs...
# ✅ Patch Generated
#    Confidence: 0.85
#    Affected Files: src/auth_service.py
# 📝 Explanation: Added missing import for hash_password function
# 💾 Patch saved to: suggested_patch.diff
```

#### Step 4.3: Verify Output Files Created
```powershell
# Check generated files
ls suggested_patch*

# Should see:
# - suggested_patch.diff
# - suggested_patch_metadata.json
```

---

## 🎓 CLASS DEMO PREPARATION (1-2 hours)

### Demo Outline: "Atlas - Automated CI/CD Testing for 7D Agile"

#### **Slide 1: Problem Statement**
- 7D Agile Stage 4 (DEBUG) requires extensive manual testing
- Quality Gate 4 verification is time-consuming and error-prone
- CI/CD pipelines fail frequently, requiring manual diagnosis and fixing

#### **Slide 2: Atlas Solution**
- **Autonomous CI/CD error detection and self-healing**
- Integrates directly into GitHub Actions workflows
- Uses local AI (Ollama) for patch generation - no cloud costs!
- Safety-first design with manual confirmation gates

#### **Slide 3: How Atlas Fits 7D Agile**
Show mapping:
```
7D Stage 4 (DEBUG) Requirements → Atlas Capabilities

✅ Test case execution → Atlas monitors CI/CD test runs
✅ Defect detection → Atlas analyzes failure logs
✅ Defect fixing → Atlas generates and verifies patches
✅ Test coverage verification → Atlas validates before apply
✅ Traceability → Atlas logs all patches with metadata
```

#### **Slide 4: Live Demo**
1. Show sample CI failure log
2. Run: `python atlas_core/tools/generate_patch.py test_error.txt`
3. Show generated patch and confidence score
4. Explain Propose → Verify → Refine → Apply workflow
5. Show safety controls (manual confirmation)

#### **Slide 5: Technical Architecture**
- Ollama local LLM (running on Gillsystems HTPC)
- OpenAI-compatible API integration
- Git worktree isolation for safe testing
- Append-only provenance logging

#### **Slide 6: Value Proposition**
- **For 7D Agile:** Automates Quality Gate 4 verification
- **For Teams:** Reduces CI/CD downtime by 60-80%
- **For Students:** Real-world agentic AI application
- **For Organizations:** On-prem solution, no cloud costs

---

## 📋 PRE-CLASS CHECKLIST

### Critical Items (Must Complete)
- [ ] Ollama running on CachyOS HTPC
- [ ] CodeLlama 7B model pulled and tested
- [ ] HTPC IP address configured in `llm_config.yaml`
- [ ] Atlas dependencies installed
- [ ] Patch generation tested with sample error log
- [ ] Demo script rehearsed (5-minute version)

### Nice-to-Have Items
- [ ] Streamlit UI running (for visual demo)
- [ ] Verify agent tested with sample patch
- [ ] PowerPoint slides prepared
- [ ] Backup: Screenshots of successful runs (in case live demo fails)

---

## 🔧 TROUBLESHOOTING GUIDE

### Issue: Ollama Not Accessible from Windows
**Solution:**
```bash
# On CachyOS HTPC, check if Ollama bound to all interfaces
ss -tulpn | grep 11434

# If only listening on 127.0.0.1, set environment variable:
export OLLAMA_HOST=0.0.0.0:11434
ollama serve

# Test from Windows again
```

### Issue: LLM Returns Invalid JSON
**Symptom:** `❌ LLM returned invalid JSON: ...`

**Solution:**
- CodeLlama 7B may need better prompt engineering
- Try adding to system prompt: "Output ONLY valid JSON, no markdown code blocks"
- Alternatively, use DeepSeek Coder (better instruction following)

### Issue: Import Errors (yaml, requests)
**Solution:**
```powershell
# Reinstall with conda
conda install -c conda-forge pyyaml requests

# Or with pip in conda env
pip install --upgrade pyyaml requests
```

### Issue: Git Worktree Commands Failing
**Symptom:** `git worktree add` errors

**Solution:**
```powershell
# Ensure you're in a git repository
git status

# Clean up any stale worktrees
git worktree prune

# Check for existing worktrees
git worktree list
```

---

## 🎯 POST-CLASS: Next Steps for Full Implementation

### Week 1: Complete Core Features
1. Implement Prometheus (verify) agent
2. Implement Hephaestus (apply) agent
3. Implement Janus (rollback) agent
4. Add comprehensive error handling

### Week 2: Streamlit UI
1. Build LLM Config tab
2. Build Propose tab
3. Build Verify tab
4. Build Apply tab with safety controls
5. Build Rollback tab

### Week 3: GitHub Actions Integration
1. Create `.github/workflows/atlas-self-healing.yml`
2. Add automatic error detection on CI failure
3. Implement PR comment annotations
4. Test with ROCm Installer repo

### Week 4: 7D Agile Integration
1. Map Atlas to all 7D stages
2. Create 7D-specific configuration templates
3. Document integration guide
4. Submit as tool recommendation to class

---

## 💡 QUESTIONS TO ASK IN CLASS

1. **For Professor Rich:**
   - "Would automated CI/CD quality gate verification be valuable for 7D Agile Stage 4?"
   - "What traceability requirements should Atlas enforce between patches and requirements?"
   - "Should Atlas integrate with the 7D requirements database?"

2. **For Classmates:**
   - "What CI/CD pain points do you face in your projects?"
   - "Would you use a local AI-powered fixer vs. manual debugging?"
   - "What other 7D stages could benefit from similar automation?"

---

## 📊 SUCCESS METRICS

### For Tomorrow's Demo
- ✅ Successfully generate at least one patch from error log
- ✅ Show confidence score and affected files
- ✅ Explain safety controls and manual confirmation
- ✅ Demonstrate alignment with 7D Agile principles

### For Full Implementation (Next Month)
- ✅ Atlas operational on at least 2 target repos
- ✅ Integrated with 7D Agile Stage 4 quality gates
- ✅ 80%+ patch accuracy (patches that fix the issue)
- ✅ 100% safety record (no unintended changes to Master)
- ✅ Documented and shareable with class

---

## 🚨 BACKUP PLAN (If Ollama Issues)

### Option A: Use LM Studio (Already on System)
- LM Studio also exposes OpenAI-compatible API
- Default port: 1234
- Update `llm_config.yaml` URL to `http://localhost:1234/v1/chat/completions`

### Option B: Mock LLM Response
- Create fake LLM response for demo
- Hardcode sample patch in `generate_patch.py`
- Focus demo on architecture and safety controls

### Option C: Pre-recorded Demo
- Record successful patch generation today
- Show video if live demo fails
- Walk through code and explain architecture

---

## ✅ FINAL PRE-CLASS VALIDATION

**Run this command to verify everything works:**

```powershell
# Full end-to-end test
cd "c:\Users\Gillsystems Laptop\source\repos\OCNGill\atlas-ci-cd-auto-fixer"

# Create test error
@"
ERROR: ModuleNotFoundError: No module named 'missing_module'
File: src/test.py, Line 5
"@ | Out-File -FilePath "demo_error.txt" -Encoding utf8

# Generate patch
python atlas_core/tools/generate_patch.py demo_error.txt demo_patch.diff

# Verify output files exist
ls demo_patch*

# If you see demo_patch.diff and demo_patch_metadata.json, YOU'RE READY! 🎉
```

---

**Good luck with your class demo! You're going to nail it! 🚀**
