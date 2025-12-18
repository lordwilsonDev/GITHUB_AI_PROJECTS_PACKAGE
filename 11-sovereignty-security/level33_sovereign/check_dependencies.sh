#!/bin/bash
# Dependency Check Script for Level 33 Sovereign Architecture

echo "=== Level 33 Dependency Check ==="
echo ""

# Check Ollama
echo "1. Checking Ollama..."
if command -v ollama &> /dev/null; then
    echo "   ✓ Ollama is installed"
    echo "   Version: $(ollama --version)"
    
    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo "   ✓ Ollama is running"
        
        # Check for Gemma 2 9B model
        if ollama list | grep -q "gemma2:9b"; then
            echo "   ✓ Gemma 2 9B model is installed"
        else
            echo "   ✗ Gemma 2 9B model NOT found"
            echo "   Run: ollama pull gemma2:9b"
        fi
    else
        echo "   ✗ Ollama is NOT running"
        echo "   Start it with: ollama serve"
    fi
else
    echo "   ✗ Ollama is NOT installed"
    echo "   Install from: https://ollama.com"
fi

echo ""

# Check cliclick
echo "2. Checking cliclick..."
if command -v cliclick &> /dev/null; then
    echo "   ✓ cliclick is installed"
    echo "   Version: $(cliclick -V)"
else
    echo "   ✗ cliclick is NOT installed"
    echo "   Install with: brew install cliclick"
fi

echo ""

# Check Python packages
echo "3. Checking Python packages..."

if python3 -c "import autogen" 2>/dev/null; then
    echo "   ✓ pyautogen is installed"
else
    echo "   ✗ pyautogen is NOT installed"
    echo "   Install with: pip install pyautogen"
fi

if python3 -c "import dspy" 2>/dev/null; then
    echo "   ✓ dspy-ai is installed"
else
    echo "   ✗ dspy-ai is NOT installed"
    echo "   Install with: pip install dspy-ai"
fi

echo ""
echo "=== Dependency Check Complete ==="
