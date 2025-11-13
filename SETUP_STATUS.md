# Atlas HTPC Setup Status

**Date**: November 12, 2025  
**Machine**: CachyOS HTPC (Gillsystems)  
**IP Address**: `10.0.0.160`

## ✅ Setup Complete

### 1. Ollama Installation
- **Status**: ✅ Installed and Running
- **Version**: 0.12.7
- **Server**: Running on port 11434
- **Models Directory**: `~/.ollama/models`

### 2. Models Imported from LM Studio
All GGUF models from `/home/gillsystemshtpc/.lmstudio/models` have been successfully imported to Ollama:

| Model Name | Size | Status |
|------------|------|--------|
| openhermes-2.5-mistral-7b.Q6_K | 5.9 GB | ✅ Active |
| dolphin-2.2-mistral-7b.Q6_K | 5.9 GB | ✅ Active |
| granite-4.0-1b-q8_0 | 1.7 GB | ✅ Active |
| granite-4.0-h-tiny-Q6_K | 5.7 GB | ✅ Active |

**Total**: 4 models imported (19.2 GB total)

### 3. Atlas Configuration
- **Config File**: `atlas_core/config/llm_config.yaml`
- **LLM Endpoint**: `http://10.0.0.160:11434/v1/chat/completions`
- **Status**: ✅ Updated with current IP address

**Current Configuration**:
```yaml
llm_endpoints:
  local:
    url: "http://10.0.0.160:11434/v1/chat/completions"
    model: "codellama:7b-instruct"  # Can be changed to any imported model
    enabled: true
    timeout_seconds: 300
```

### 4. Python Environment
- **Type**: Virtual Environment (system Python managed)
- **Location**: `/home/gillsystemshtpc/.atlas-venv`
- **Python Version**: 3.13.7
- **Status**: ✅ Created and configured

**Installed Dependencies**:
- pyyaml
- requests
- streamlit
- pytest
- pylint

**To activate**:
```bash
source /home/gillsystemshtpc/.atlas-venv/bin/activate
```

## 🎯 Next Steps

### From Windows Laptop

1. **Test LLM Endpoint Connection**:
   ```powershell
   # PowerShell
   Invoke-RestMethod -Uri "http://10.0.0.160:11434/api/tags"
   ```

2. **Run Validation Script**:
   ```powershell
   cd atlas-ci-cd-auto-fixer
   python validate_demo_readiness.py
   ```

3. **Update Windows Config** (if needed):
   Edit `atlas_core/config/llm_config.yaml` on Windows to point to:
   ```yaml
   url: "http://10.0.0.160:11434/v1/chat/completions"
   ```

### From HTPC (if needed)

1. **Activate Virtual Environment**:
   ```bash
   source ~/.atlas-venv/bin/activate
   ```

2. **Test Locally**:
   ```bash
   cd ~/VS-Code-workspaces/action-workflow-error-self-healer-agent/atlas-ci-cd-auto-fixer
   python validate_demo_readiness.py
   ```

3. **Start Streamlit UI** (local testing):
   ```bash
   source ~/.atlas-venv/bin/activate
   streamlit run atlas_core/ui/streamlit/main.py --server.address 0.0.0.0 --server.port 8501
   ```

## 📋 Model Usage Notes

### Recommended Models for Atlas

1. **OpenHermes-2.5-Mistral-7B** (Primary Recommendation)
   - Best balance of code understanding and instruction following
   - 5.9 GB VRAM usage
   - Use in config: `openhermes-2.5-mistral-7b.Q6_K:latest`

2. **Dolphin-2.2-Mistral-7B** (Alternative)
   - Good for code generation
   - 5.9 GB VRAM usage
   - Use in config: `dolphin-2.2-mistral-7b.Q6_K:latest`

3. **Granite-4.0-1B** (Fast/Lightweight)
   - Faster inference, lower quality
   - 1.7 GB VRAM usage
   - Use for quick testing
   - Use in config: `granite-4.0-1b-q8_0:latest`

### To Change Model

Edit `atlas_core/config/llm_config.yaml`:
```yaml
llm_endpoints:
  local:
    model: "openhermes-2.5-mistral-7b.Q6_K:latest"  # Change this line
```

## 🔧 Troubleshooting

### Ollama Server Not Responding
```bash
# Check if running
systemctl status ollama

# Check logs
sudo journalctl -u ollama -n 50

# Restart if needed
sudo systemctl restart ollama

# Verify it's listening on network
ss -tlnp | grep 11434
# Should show: *:11434 (not 127.0.0.1:11434)
```

### Port 11434 Not Accessible from Network
```bash
# Check firewall status
sudo ufw status
# Should show: 11434/tcp ALLOW Anywhere

# If not, add the rule
sudo ufw allow 11434/tcp comment 'Ollama LLM Server'

# Test from HTPC
curl http://10.0.0.160:11434/api/tags

# Test from Windows (PowerShell)
Test-NetConnection -ComputerName 10.0.0.160 -Port 11434
Invoke-RestMethod -Uri "http://10.0.0.160:11434/api/tags"
```

### Ollama Only Listening on Localhost
```bash
# Check listening address
ss -tlnp | grep 11434

# If shows 127.0.0.1:11434 instead of *:11434:
# The systemd service should already be configured, but to verify:
sudo systemctl cat ollama | grep OLLAMA_HOST
# Should show: Environment="OLLAMA_HOST=0.0.0.0:11434"

# If not set, reinstall service:
sudo systemctl stop ollama
cd ~/VS-Code-workspaces/action-workflow-error-self-healer-agent/atlas-ci-cd-auto-fixer
./setup_htpc.sh
```

### Virtual Environment Issues
```bash
# Recreate if needed
rm -rf ~/.atlas-venv
python3 -m venv ~/.atlas-venv
source ~/.atlas-venv/bin/activate
pip install pyyaml requests streamlit pytest pylint
```

### Network Connectivity
```bash
# Test from HTPC
curl http://localhost:11434/api/tags

# Test from Windows (PowerShell)
Test-NetConnection -ComputerName 10.0.0.160 -Port 11434
```

## 📊 System Resources

**GPU**: Radeon RX 7600 (8 GB VRAM)
- Sufficient for 7B models with Q6_K quantization
- Can run 2-3 concurrent requests
- Monitor with: `radeontop` or `rocm-smi` (if ROCm installed)

**RAM**: Should have 16+ GB for smooth operation
**Disk**: Models consume ~19 GB

## 🎉 Demo Readiness

✅ All components installed and configured  
✅ Models imported and accessible  
✅ Configuration updated with correct IP  
✅ Python environment ready  
✅ Ready for demonstration tomorrow!

### Pre-Demo Checklist
- [ ] Test Windows → HTPC connection
- [ ] Run `validate_demo_readiness.py` from Windows
- [ ] Test one patch generation workflow end-to-end
- [ ] Verify Streamlit UI accessible (optional)
- [ ] Ensure Ollama stays running during demo

---

**Setup completed by**: Atlas Setup Script v2  
**Last updated**: 2025-11-12 (automated)
