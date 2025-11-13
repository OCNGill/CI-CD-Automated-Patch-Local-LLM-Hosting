#!/bin/bash
# Conservative Ollama Network Fix for CachyOS
# Only fixes binding and firewall if clearly needed

echo "🔧 Atlas Ollama Network Fix (Conservative)"
echo "==========================================="
echo ""

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "❌ Ollama is not running!"
    echo "Starting Ollama..."
    export OLLAMA_HOST=0.0.0.0:11434
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
fi

# Check binding FIRST
echo "🔍 Checking Ollama binding..."
BINDING=$(ss -tulpn 2>/dev/null | grep 11434 | grep -o "0.0.0.0\|127.0.0.1\|:::" | head -1)

if [ "$BINDING" = "127.0.0.1" ] || [ "$BINDING" = "" ]; then
    echo "⚠️  Ollama bound to localhost only - fixing..."
    export OLLAMA_HOST=0.0.0.0:11434
    pkill ollama
    sleep 2
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
    echo "✅ Ollama restarted with 0.0.0.0 binding"
elif [ "$BINDING" = "0.0.0.0" ] || [ "$BINDING" = ":::" ]; then
    echo "✅ Ollama already bound to all interfaces"
else
    echo "❌ Could not determine Ollama binding (got: '$BINDING')"
    echo "Manual check: ss -tulpn | grep 11434"
fi

# FIREWALL: Only touch if we detect an active firewall
echo ""
echo "🔍 Checking firewall (CachyOS/Arch style)..."

FIREWALL_ACTIVE=false

# Check UFW (if installed)
if command -v ufw &> /dev/null; then
    if sudo ufw status 2>/dev/null | grep -q "Status: active"; then
        FIREWALL_ACTIVE=true
        echo "UFW firewall is active"
        if sudo ufw status 2>/dev/null | grep -q "11434"; then
            echo "✅ Port 11434 already allowed in UFW"
        else
            echo "⚠️  Adding port 11434 to UFW..."
            sudo ufw allow 11434/tcp
            echo "✅ Port 11434 allowed in UFW"
        fi
    fi
fi

# Check firewalld (if installed)
if command -v firewall-cmd &> /dev/null; then
    if sudo firewall-cmd --state 2>/dev/null | grep -q "running"; then
        FIREWALL_ACTIVE=true
        echo "firewalld is active"
        if sudo firewall-cmd --list-ports 2>/dev/null | grep -q "11434"; then
            echo "✅ Port 11434 already allowed in firewalld"
        else
            echo "⚠️  Adding port 11434 to firewalld..."
            sudo firewall-cmd --permanent --add-port=11434/tcp
            sudo firewall-cmd --reload
            echo "✅ Port 11434 allowed in firewalld"
        fi
    fi
fi

if [ "$FIREWALL_ACTIVE" = false ]; then
    echo "ℹ️  No active firewall detected (expected on CachyOS/Arch)"
fi

# Test local connection
echo ""
echo "🧪 Testing local connection..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama responding locally"
else
    echo "❌ Ollama not responding locally"
    echo "Check logs: tail /tmp/ollama.log"
    exit 1
fi

# Get IP address
IP_ADDR=$(ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | head -n 1)

echo ""
echo "================================"
echo "✅ Network Fix Complete!"
echo "================================"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. From Windows laptop, test connection:"
echo "   Test-NetConnection -ComputerName $IP_ADDR -Port 11434"
echo ""
echo "2. Or test with Invoke-RestMethod:"
echo "   Invoke-RestMethod -Uri \"http://$IP_ADDR:11434/api/tags\""
echo ""
echo "3. If still not working, check:"
echo "   - Router firewall settings"
echo "   - Windows firewall settings"
echo "   - Network connectivity between machines"
echo ""
echo "🎉 Ollama should now be accessible from Windows!"
