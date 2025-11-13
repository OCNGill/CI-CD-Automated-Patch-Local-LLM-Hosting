# CI/CD Automated Patch Generation v1.1
## Local LLM-Powered Self-Healing Agent

> **Note**: My robot is still learning. 🤖

**Atlas v1.1** is a local-first CI/CD error detection and self-healing agent with complete Streamlit GUI. Use your own Ollama server to diagnose and fix pipeline failures—no cloud required, complete privacy.

---

## ✨ What's New in v1.1

- 🎨 **Complete Streamlit Web UI** with 6 functional tabs
- 🔐 **Localhost-only defaults** for maximum security
- 🎯 **Multi-project support** with dropdown selector
- 📊 **Live Ollama integration** for model management
- 🚀 **Production-ready** with safety controls and audit trails

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running
- Git for version control

### Installation

```powershell
# Clone the repository
git clone https://github.com/OCNGill/CI-CD-Automated-Patch-Local-LLM-Hosting.git
cd CI-CD-Automated-Patch-Local-LLM-Hosting

# Install dependencies
pip install -r requirements.txt

# Pull a code model
ollama pull codellama:7b-instruct

# Launch the GUI
cd Atlas-GUI
.\launch.bat
```

Open your browser to: **http://localhost:8501**

---

## 📚 Key Features

### 🎨 Streamlit Web Interface
- **Dashboard**: Agent status, project selector, active model
- **Workflow**: Full Propose → Verify → Apply pipeline
- **Performance**: Track iterations, confidence scores, patch history
- **Configuration**: Select and manage LLM models
- **History & Rollback**: Git viewer with one-click rollback
- **Get More Models**: Download models from Ollama library

### 🔐 Security & Privacy
- ✅ **100% Local** - No cloud dependencies
- ✅ **Privacy-First** - Your code never leaves your machine
- ✅ **Manual Controls** - All patches require confirmation
- ✅ **Complete Audit Trail** - JSONL logs + git commits

### 🎯 Technical Highlights
- OpenAI-compatible API (works with Ollama, LM Studio, vLLM)
- Git worktree verification (no main branch pollution)
- Multi-repository support
- Windows-first design with ROCm GPU support

---

## 🛠️ Configuration

Edit **tlas_core/config/llm_config.yaml**:

```yaml
llm_endpoints:
  local:
    url: \"http://127.0.0.1:11434/v1/chat/completions\"
    model: \"codellama:7b-instruct\"
    enabled: true

target_repos:
  MyProject:
    build_command: \"pytest tests/ -v\"
    test_commands:
      - \"pytest tests/\"
```

---

## 📖 Documentation

- **Full Docs**: See [docs/](docs/) folder
- **Security Guide**: [SECURITY.md](SECURITY.md)
- **Public Setup**: [PUBLIC_SETUP.md](PUBLIC_SETUP.md)
- **LLM Integration**: [docs/llm_integration.md](docs/llm_integration.md)
- **Hardware Setup**: [docs/hardware_setup.md](docs/hardware_setup.md)

---

## 🆘 Troubleshooting

**GUI won't start?**
- Ensure port 8501 is available
- Run: `pip install -r Atlas-GUI/requirements.txt`

**Models not loading?**
- Verify Ollama is running: `ollama list`
- Check endpoint: `curl http://127.0.0.1:11434/api/tags`

**YAML config errors?**
- Ensure you're running from repo root
- Check file exists: `atlas_core/config/llm_config.yaml`

---

## 🤝 Contributing

This is a community project! Issues and PRs welcome.

**To report issues**:
1. Check existing issues first
2. Provide error logs and steps to reproduce
3. Tag with appropriate labels

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file

---

## 💖 Support the Project

If you find this helpful, consider supporting ongoing development!

- **PayPal**: https://paypal.me/gillsystems
- **Venmo**: https://venmo.com/Stephen-Gill-007

---

## 🎓 Learn More

- 🔗 [Ollama Model Library](https://ollama.com/library)
- 🔗 [Streamlit Documentation](https://docs.streamlit.io/)
- 🔗 [Project Repository](https://github.com/OCNGill/CI-CD-Automated-Patch-Local-LLM-Hosting)

---

**Remember**: This is a local-first tool. Your code, your compute, your control. 🚀

> *My robot is still learning, but it's getting smarter every day!* 🤖
