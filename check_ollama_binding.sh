#!/bin/bash
# Minimal Ollama Binding Check for CachyOS
# Run this first to check Ollama status

echo "🔍 Checking Ollama on CachyOS..."
echo ""

# Check if Ollama is running
if pgrep -x "ollama" > /dev/null; then
    echo "✅ Ollama is running"
else
    echo "❌ Ollama is not running"
    echo "Start it with: export OLLAMA_HOST=0.0.0.0:11434 && ollama serve"
    exit 1
fi

# Check binding
echo "🔍 Checking binding..."
BINDING=$(ss -tulpn 2>/dev/null | grep 11434 | grep -o "0.0.0.0\|127.0.0.1\|:::" | head -1)

case $BINDING in
    "0.0.0.0"|":::")
        echo "✅ Ollama bound to all interfaces ($BINDING)"
        ;;
    "127.0.0.1")
        echo "⚠️  Ollama bound to localhost only - needs fixing"
        echo "Run: pkill ollama && export OLLAMA_HOST=0.0.0.0:11434 && ollama serve"
        ;;
    *)
        echo "❓ Could not determine binding (output: $BINDING)"
        echo "Check with: ss -tulpn | grep 11434"
        ;;
esac

# Check firewall (Arch/CachyOS typically no firewall by default)
echo ""
echo "🔍 Checking firewall..."
if command -v ufw &> /dev/null && ufw status | grep -q "active"; then
    echo "UFW active - check if port 11434 allowed"
elif command -v firewall-cmd &> /dev/null && firewall-cmd --state | grep -q "running"; then
    echo "firewalld active - check if port 11434 allowed"
else
    echo "ℹ️  No active firewall detected (common on Arch/CachyOS)"
fi

echo ""
echo "📋 If binding is the issue, fix with:"
echo "   pkill ollama"
echo "   export OLLAMA_HOST=0.0.0.0:11434"
echo "   ollama serve"