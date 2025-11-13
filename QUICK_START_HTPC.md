# 🚀 QUICK START - Atlas on HTPC

**Everything is pushed to GitHub!**  
**Repository:** `https://github.com/OCNGill/atlas-ci-cd-auto-fixer`

---

## On HTPC (CachyOS) - Do This Now:

### Step 1: Pull the Repository
```bash
cd ~/projects  # or wherever you keep code
git clone https://github.com/OCNGill/atlas-ci-cd-auto-fixer.git
cd atlas-ci-cd-auto-fixer
```

### Step 2: Run Automated Setup
```bash
chmod +x setup_htpc.sh
./setup_htpc.sh
```

**This script will:**
- ✅ Install Ollama (if not installed)
- ✅ Download CodeLlama 7B model
- ✅ Detect your HTPC IP address
- ✅ Create conda environment
- ✅ Install Python dependencies
- ✅ Start Ollama server

### Step 3: Update Configuration
```bash
# The script will tell you your IP address
# Edit the config file:
nano atlas_core/config/llm_config.yaml

# Replace BOTH instances of <HTPC_IP_ADDRESS> with your actual IP
# The script output will show you exactly what IP to use
```

---

## On Windows Laptop - After HTPC Setup:

### Test Connection
```powershell
# Replace <HTPC_IP> with the IP from setup script
Invoke-RestMethod -Uri "http://<HTPC_IP>:11434/v1/models"
```

### Run Validation
```powershell
cd "c:\Users\Gillsystems Laptop\source\repos\OCNGill\atlas-ci-cd-auto-fixer"
python validate_demo_readiness.py
```

**Expected output:**
```
🎉 ALL CHECKS PASSED! YOU'RE READY FOR DEMO!
```

---

## 📋 Files to Read

**On HTPC or Windows:**
1. **`CONVERSATION_SUMMARY.md`** - Complete conversation recap
2. **`CLASS_DEMO_ACTION_PLAN.md`** - Detailed setup and demo guide
3. **`DEMO_QUICK_REFERENCE.md`** - Quick reference during demo
4. **`EXECUTIVE_SUMMARY.md`** - Full analysis and roadmap

---

## ⏱️ Time Estimate

- HTPC setup: **30-45 minutes** (mostly downloading CodeLlama model)
- Config update: **5 minutes**
- Testing: **15 minutes**
- Demo practice: **30 minutes**

**Total: ~2 hours** (can be done tonight!)

---

## 🎯 Success Criteria for Tonight

- [ ] Ollama running on HTPC
- [ ] CodeLlama 7B model downloaded
- [ ] HTPC IP address noted and configured
- [ ] Validation script passes all checks
- [ ] One successful patch generation test

---

## 🆘 Quick Troubleshooting

**Setup script fails?**
```bash
# Check logs
tail /tmp/ollama.log

# Manual Ollama start
ollama serve
```

**Can't reach HTPC from Windows?**
```bash
# On HTPC, check firewall
sudo ufw status
sudo ufw allow 11434/tcp

# Verify Ollama is listening on all interfaces
ss -tulpn | grep 11434
```

**Model download slow?**
- CodeLlama 7B is ~4GB
- On slow connection, may take 30+ minutes
- Can continue other setup while downloading

---

## 🎓 Ready for Demo

Once validation passes, you're ready to demonstrate:
1. Error log analysis
2. AI-powered patch generation
3. Confidence scoring
4. 7D Agile Stage 4 integration

**You've got this! 🚀**

---

**Questions? Everything is documented in the files listed above!**
