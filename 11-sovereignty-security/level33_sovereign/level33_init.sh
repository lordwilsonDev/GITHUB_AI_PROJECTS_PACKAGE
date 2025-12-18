#!/bin/bash
# level33_init.sh

echo "🦁 INITIALIZING LEVEL 33 SOVEREIGN STACK..."

# 1. Hardware Check
ARCH=$(uname -m)
if [ "$ARCH" != "arm64" ]; then
    echo "⚠️  WARNING: Not running on Apple Silicon. Performance will degrade."
fi

# 2. Dependency Check
if ! command -v cliclick &> /dev/null; then
    echo "Installing Physical Agency (cliclick)..."
    brew install cliclick
fi

if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not found. Install from ollama.com"
    exit 1
fi

# 3. Model Hydration
echo "🧠 Loading Neural Core (Gemma 2 9B)..."
ollama pull gemma2:9b

# 4. Python Environment
echo "🐍 Hydrating Python Environment..."
pip3 install pyautogen dspy-ai

echo "✅ SYSTEM READY."
echo "   Run 'python3 architecture/brain_core.py' to activate the agent."
