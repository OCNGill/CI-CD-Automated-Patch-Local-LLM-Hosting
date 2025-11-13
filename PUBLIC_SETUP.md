# CI/CD Automated Patch Generation with Local LLM Hosting

## Public Template - Quick Start Guide

This is the **public template** version of Atlas, a CI/CD error detection and self-healing agent that uses **local LLM hosting** for privacy and control.

### Key Differences from Private Setups

- **Local-only defaults**: All endpoints bind to `127.0.0.1` by default
- **No remote access configured**: You run everything on your own machine
- **Customizable**: Edit `atlas_core/config/llm_config.yaml` to match your setup

### What You Need

1. **Python 3.10+** (tested on 3.10 and 3.13)
2. **Ollama or compatible LLM server** running locally
3. **Git** for version control and patch operations
4. **A GitHub repository** to monitor (optional for getting started)

### Installation Steps

#### 1. Clone This Repository

```powershell
git clone https://github.com/YOUR_USERNAME/CI-CD-Automated-Patch-Local-LLM-Hosting.git
cd CI-CD-Automated-Patch-Local-LLM-Hosting
```

#### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

#### 3. Set Up Your Local LLM Server

**Option A: Ollama (Recommended)**
```powershell
# Install Ollama from https://ollama.ai
# Pull a code model
ollama pull codellama:7b-instruct

# Start Ollama (usually auto-starts on install)
```

**Option B: LM Studio, vLLM, or other OpenAI-compatible server**
- Configure your server to listen on `http://127.0.0.1:11434`
- Or update `atlas_core/config/llm_config.yaml` with your server's address

#### 4. Customize Your Configuration

Edit `atlas_core/config/llm_config.yaml`:

```yaml
llm_endpoints:
  local:
    url: "http://127.0.0.1:11434/v1/chat/completions"  # Your LLM server
    model: "codellama:7b-instruct"  # Your preferred model
    enabled: true

hardware:
  primary_gpu:
    model: "YOUR_GPU_MODEL_HERE"  # e.g., "RTX 4090", "Radeon RX 7900 XTX"
    vram_gb: 24  # Your GPU's VRAM
```

#### 5. Launch the GUI

```powershell
cd Atlas-GUI
.\launch.bat
```

Or run directly:
```powershell
streamlit run Atlas-GUI\app.py --server.address 127.0.0.1 --server.port 8501
```

Open your browser to: `http://127.0.0.1:8501`

### Using Atlas

1. **Dashboard Tab**: View agent status, active project, and safety settings
2. **Workflow Tab**: Propose → Verify → Apply patches
3. **Performance & Logs Tab**: Monitor patch generation performance
4. **Configuration Tab**: Edit settings in the GUI
5. **History & Rollback Tab**: View and revert past patches
6. **Get More Models Tab**: Manage LLM models via Ollama

### Security & Privacy

- **Everything runs locally by default** - your code never leaves your machine
- **No cloud dependencies** - Atlas works offline
- **You control the model** - choose models that fit your hardware and needs
- **Safety-first design** - manual confirmation required for all patches

See `SECURITY.md` for detailed security guidance.

### Remote Access (Advanced)

If you want to access Atlas from multiple machines (e.g., laptop accessing HTPC's LLM):

1. Update `llm_config.yaml` with your LLM server's network IP (e.g., `10.0.0.160`)
2. **Secure your setup**: Follow `SECURITY.md` for firewall, VPN, and authentication guidance
3. **Never expose to public internet without proper security**

### Customizing for Your Projects

Edit `atlas_core/config/llm_config.yaml` under `target_repos`:

```yaml
target_repos:
  MyProject:
    build_command: "npm run build"  # or "pytest", "cargo build", etc.
    test_commands:
      - "npm test"
      - "npm run lint"
```

### Troubleshooting

**YAMLs not loading?**
- Ensure you're running from the repo root or using `launch.bat`
- Check that `atlas_core/config/llm_config.yaml` exists

**LLM endpoint unreachable?**
- Verify Ollama or your LLM server is running: `curl http://127.0.0.1:11434/v1/models`
- Check firewall settings if using remote LLM server

**GUI not starting?**
- Install requirements: `pip install -r Atlas-GUI/requirements.txt`
- Ensure port 8501 is available

### Documentation

- **Full Documentation**: See `docs/` folder
- **LLM Integration**: `docs/llm_integration.md`
- **Patch Lifecycle**: `docs/patch_lifecycle.md`
- **Hardware Setup**: `docs/hardware_setup.md`
- **UI Workflows**: `docs/ui_workflows.md`

### Contributing

Issues and pull requests welcome! This is a community project focused on making AI-powered CI/CD accessible to everyone.

### License

MIT License - see `LICENSE` file

### Support

If you find this project helpful, consider supporting ongoing development!

- **PayPal**: https://paypal.me/gillsystems
- **Venmo**: https://venmo.com/Stephen-Gill-007

---

**Remember**: This is a local-first tool. Your code, your compute, your control. 🚀
