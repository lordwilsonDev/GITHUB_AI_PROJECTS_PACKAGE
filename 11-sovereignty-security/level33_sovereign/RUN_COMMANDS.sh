#!/bin/bash
# RUN_COMMANDS.sh - Execute all setup and testing commands
# This script automates the entire Level 33 setup process

set -e  # Exit on any error

echo "═══════════════════════════════════════════════════════════"
echo "  Level 33 Sovereign Architecture - Automated Setup"
echo "═══════════════════════════════════════════════════════════"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Change to the level33_sovereign directory
cd "$(dirname "$0")"

echo "Step 1: Checking Ollama status..."
if ! command -v ollama &> /dev/null; then
    print_error "Ollama is not installed!"
    echo "Please install from: https://ollama.com"
    exit 1
fi
print_status "Ollama is installed"

# Check if Ollama is running
if curl -s http://localhost:11434/api/tags &> /dev/null; then
    print_status "Ollama is running"
else
    print_warning "Ollama is not running"
    echo ""
    echo "Please start Ollama in a separate terminal:"
    echo "  ollama serve"
    echo ""
    read -p "Press Enter once Ollama is running..."
    
    # Check again
    if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
        print_error "Ollama is still not running. Exiting."
        exit 1
    fi
    print_status "Ollama is now running"
fi

echo ""
echo "Step 2: Checking for Gemma 2 9B model..."
if ollama list | grep -q "gemma2:9b"; then
    print_status "Gemma 2 9B model is already installed"
else
    print_warning "Gemma 2 9B model not found"
    echo "Downloading Gemma 2 9B (~5.7GB)..."
    echo "This may take several minutes..."
    ollama pull gemma2:9b
    print_status "Gemma 2 9B model downloaded"
fi

echo ""
echo "Step 3: Checking dependencies..."

# Check cliclick
if command -v cliclick &> /dev/null; then
    print_status "cliclick is installed"
else
    print_warning "cliclick not found. Installing..."
    if command -v brew &> /dev/null; then
        brew install cliclick
        print_status "cliclick installed"
    else
        print_error "Homebrew not found. Please install cliclick manually:"
        echo "  brew install cliclick"
        exit 1
    fi
fi

# Check Python packages
echo ""
echo "Step 4: Checking Python packages..."

if python3 -c "import autogen" 2>/dev/null; then
    print_status "pyautogen is installed"
else
    print_warning "pyautogen not found. Installing..."
    pip3 install pyautogen
    print_status "pyautogen installed"
fi

if python3 -c "import dspy" 2>/dev/null; then
    print_status "dspy-ai is installed"
else
    print_warning "dspy-ai not found. Installing..."
    pip3 install dspy-ai
    print_status "dspy-ai installed"
fi

if python3 -c "import requests" 2>/dev/null; then
    print_status "requests is installed"
else
    print_warning "requests not found. Installing..."
    pip3 install requests
    print_status "requests installed"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "  Running Test Suite"
echo "═══════════════════════════════════════════════════════════"
echo ""

echo "Test 1: Configuration Test"
echo "─────────────────────────────────────────────────────────"
python3 test_autogen.py
echo ""

echo "Test 2: Full Stack Test"
echo "─────────────────────────────────────────────────────────"
python3 test_full_stack.py
echo ""

echo "Test 3: Reflexion Loop Test"
echo "─────────────────────────────────────────────────────────"
python3 test_reflexion_loop.py
echo ""

echo "═══════════════════════════════════════════════════════════"
echo "  Setup Complete!"
echo "═══════════════════════════════════════════════════════════"
echo ""
print_status "All dependencies installed"
print_status "All tests completed"
print_status "System is ready for deployment"
echo ""
echo "To run the agent:"
echo "  cd ~/level33_sovereign"
echo "  python3 architecture/brain_core.py"
echo ""
echo "To run with a custom task, edit brain_core.py and uncomment"
echo "lines 58-61, then run the command above."
echo ""
echo "═══════════════════════════════════════════════════════════"
