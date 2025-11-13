#!/bin/bash
# Atlas HTPC Setup Script
# Run this on CachyOS HTPC after pulling the repo

set -e  # Exit on error

echo "=================================================="
echo "Atlas CI/CD Auto-Fixer - HTPC Setup"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check if Ollama is installed
echo "🔍 Checking for Ollama..."
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✅ Ollama is already installed${NC}"
    ollama --version
else
    echo -e "${YELLOW}⚠️  Ollama not found. Installing...${NC}"
    curl -fsSL https://ollama.com/install.sh | sh
    echo -e "${GREEN}✅ Ollama installed${NC}"
fi

echo ""

# Step 2: Import models from LM Studio to Ollama
echo "📦 Importing models from LM Studio to Ollama..."
LMSTUDIO_MODELS="/home/gillsystemshtpc/.lmstudio/models"

if [ -d "$LMSTUDIO_MODELS" ]; then
    echo -e "${GREEN}✅ Found LM Studio models directory${NC}"
    
    # Find all GGUF models
    GGUF_FILES=$(find "$LMSTUDIO_MODELS" -name "*.gguf" -type f)
    
    if [ -n "$GGUF_FILES" ]; then
        echo "Found the following models:"
        echo "$GGUF_FILES"
        echo ""
        
        # Import each model to Ollama
        while IFS= read -r model_file; do
            model_name=$(basename "$model_file" .gguf)
            echo -e "${YELLOW}📥 Importing $model_name to Ollama...${NC}"
            
            # Create a Modelfile for Ollama
            cat > /tmp/Modelfile.tmp << EOF
FROM "$model_file"
PARAMETER temperature 0.7
PARAMETER top_p 0.9
EOF
            
            # Import to Ollama
            if ollama create "$model_name" -f /tmp/Modelfile.tmp 2>/dev/null; then
                echo -e "${GREEN}✅ Successfully imported $model_name${NC}"
            else
                echo -e "${YELLOW}⚠️  Skipping $model_name (may already exist or format incompatible)${NC}"
            fi
        done <<< "$GGUF_FILES"
        
        rm -f /tmp/Modelfile.tmp
        echo ""
        echo "📋 Available models in Ollama:"
        ollama list
    else
        echo -e "${YELLOW}⚠️  No GGUF models found in LM Studio directory${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  LM Studio models directory not found at $LMSTUDIO_MODELS${NC}"
fi

echo ""

# Step 3: Configure LLM endpoint with current IP
echo "⚙️  Configuring LLM endpoint..."
IP_ADDR=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -n 1)
echo -e "${GREEN}✅ IP Address: $IP_ADDR${NC}"

# Update llm_config.yaml with the current IP
CONFIG_FILE="atlas_core/config/llm_config.yaml"
if [ -f "$CONFIG_FILE" ]; then
    echo "Updating $CONFIG_FILE with IP: $IP_ADDR"
    sed -i "s/<HTPC_IP_ADDRESS>/$IP_ADDR/g" "$CONFIG_FILE"
    echo -e "${GREEN}✅ Configuration updated${NC}"
else
    echo -e "${RED}❌ Config file not found: $CONFIG_FILE${NC}"
fi

echo ""

# Step 4: Configure Ollama for network access
echo "🌐 Configuring Ollama for network access..."

# Create systemd service for network-accessible Ollama
OLLAMA_BIN=$(which ollama)
cat > /tmp/ollama-network.service << EOF
[Unit]
Description=Ollama LLM Server (Network Accessible)
After=network-online.target

[Service]
Type=simple
User=$USER
Environment="OLLAMA_HOST=0.0.0.0:11434"
Environment="PATH=/usr/local/bin:/usr/bin:/bin"
ExecStart=$OLLAMA_BIN serve
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo cp /tmp/ollama-network.service /etc/systemd/system/ollama.service
sudo systemctl daemon-reload
sudo systemctl enable ollama > /dev/null 2>&1

# Kill any existing ollama processes
sudo pkill -9 ollama 2>/dev/null || true
sleep 2

# Start the service
sudo systemctl start ollama
sleep 3

if systemctl is-active --quiet ollama; then
    echo -e "${GREEN}✅ Ollama service started (network accessible)${NC}"
else
    echo -e "${RED}❌ Failed to start Ollama service${NC}"
    echo "   Check logs: sudo journalctl -u ollama -n 20"
    exit 1
fi

# Configure firewall
echo "🔥 Configuring firewall..."
if command -v ufw &> /dev/null && sudo ufw status | grep -q "Status: active"; then
    sudo ufw allow 11434/tcp comment 'Ollama LLM Server' > /dev/null 2>&1
    echo -e "${GREEN}✅ Firewall rule added (UFW)${NC}"
elif command -v firewall-cmd &> /dev/null && sudo firewall-cmd --state 2>/dev/null | grep -q "running"; then
    sudo firewall-cmd --permanent --add-port=11434/tcp > /dev/null 2>&1
    sudo firewall-cmd --reload > /dev/null 2>&1
    echo -e "${GREEN}✅ Firewall rule added (firewalld)${NC}"
else
    echo -e "${YELLOW}⚠️  No active firewall detected, skipping${NC}"
fi

echo ""

echo ""

# Step 5: Check Python environment
echo "🔍 Checking Python environment..."
if command -v conda &> /dev/null; then
    echo -e "${GREEN}✅ Conda is installed${NC}"
    
    # Check if atlas environment exists
    if conda env list | grep -q "atlas"; then
        echo -e "${GREEN}✅ 'atlas' conda environment exists${NC}"
    else
        echo -e "${YELLOW}⚠️  Creating 'atlas' conda environment...${NC}"
        conda create -n atlas python=3.10 -y
        echo -e "${GREEN}✅ 'atlas' environment created${NC}"
    fi
    
    # Step 6: Install Python dependencies
    echo ""
    echo "📦 Installing Python dependencies..."
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate atlas
    pip install pyyaml requests streamlit pytest pylint
    echo -e "${GREEN}✅ Dependencies installed (conda environment)${NC}"
else
    echo -e "${YELLOW}⚠️  Conda not found, using Python virtual environment${NC}"
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | grep -oP '\d+\.\d+')
        echo -e "${GREEN}✅ Python $PYTHON_VERSION is available${NC}"
        
        # Create virtual environment if it doesn't exist
        VENV_DIR="$HOME/.atlas-venv"
        if [ ! -d "$VENV_DIR" ]; then
            echo -e "${YELLOW}⚠️  Creating virtual environment at $VENV_DIR...${NC}"
            python3 -m venv "$VENV_DIR"
            echo -e "${GREEN}✅ Virtual environment created${NC}"
        else
            echo -e "${GREEN}✅ Virtual environment exists at $VENV_DIR${NC}"
        fi
        
        # Step 6: Install Python dependencies
        echo ""
        echo "📦 Installing Python dependencies..."
        source "$VENV_DIR/bin/activate"
        pip install pyyaml requests streamlit pytest pylint
        echo -e "${GREEN}✅ Dependencies installed (virtual environment)${NC}"
        echo -e "${YELLOW}ℹ️  To use Atlas, activate the environment first:${NC}"
        echo "   source $VENV_DIR/bin/activate"
    else
        echo -e "${RED}❌ Python 3 not found. Please install Python 3.10+${NC}"
        exit 1
    fi
fi

echo ""

echo ""
echo "=================================================="
echo -e "${GREEN}✅ HTPC Setup Complete!${NC}"
echo "=================================================="
echo ""
echo "📋 Configuration Summary:"
echo "   • LLM Endpoint: http://$IP_ADDR:11434/v1/chat/completions"
echo "   • Config file updated: atlas_core/config/llm_config.yaml"
echo "   • Models imported from LM Studio to Ollama"
echo ""
echo "📋 Next Steps:"
echo "   1. Test connection from Windows laptop:"
echo "      Invoke-RestMethod -Uri \"http://$IP_ADDR:11434/v1/models\""
echo ""
echo "   2. Run validation script (from Windows):"
echo "      python validate_demo_readiness.py"
echo ""
echo "   3. Start demo testing!"
echo ""
echo "🎉 Ready for demo tomorrow!"
