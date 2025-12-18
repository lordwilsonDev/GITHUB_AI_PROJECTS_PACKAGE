#!/bin/bash

# M1 Optimization Agent - Dependency Installation Script
# Installs all required dependencies for the agent

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}=== M1 Optimization Agent - Dependency Installation ===${NC}"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Install Python 3 from https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python version: $PYTHON_VERSION"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}uv package manager not found. Installing...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Add uv to PATH for current session
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if command -v uv &> /dev/null; then
        echo -e "${GREEN}✓${NC} uv installed successfully"
    else
        echo -e "${YELLOW}⚠${NC} uv installation may require shell restart"
        echo "Run: source ~/.bashrc (or ~/.zshrc)"
    fi
else
    echo -e "${GREEN}✓${NC} uv is already installed"
fi

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Create virtual environment
if [ -d "venv" ] || [ -d ".venv" ]; then
    echo -e "${YELLOW}⚠${NC} Virtual environment already exists"
    read -p "Remove and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv .venv
        echo -e "${GREEN}✓${NC} Removed existing virtual environment"
    else
        echo "Keeping existing environment"
    fi
fi

if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    
    if command -v uv &> /dev/null; then
        uv venv
        echo -e "${GREEN}✓${NC} Virtual environment created with uv"
    else
        python3 -m venv venv
        echo -e "${GREEN}✓${NC} Virtual environment created with venv"
    fi
fi

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

echo -e "${GREEN}✓${NC} Virtual environment activated"

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"

if command -v uv &> /dev/null; then
    uv pip install -r requirements.txt
    echo -e "${GREEN}✓${NC} Dependencies installed with uv"
else
    pip install -r requirements.txt
    echo -e "${GREEN}✓${NC} Dependencies installed with pip"
fi

# Check if Ollama is installed
echo ""
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓${NC} Ollama is installed"
    OLLAMA_VERSION=$(ollama --version 2>&1 | head -n 1)
    echo "  Version: $OLLAMA_VERSION"
else
    echo -e "${YELLOW}⚠${NC} Ollama is not installed"
    echo "  Install from: https://ollama.ai"
    echo "  Or run: curl https://ollama.ai/install.sh | sh"
fi

# Check for optional tools
echo ""
echo -e "${YELLOW}Checking optional tools...${NC}"

if [ -d "/Applications/Macs Fan Control.app" ]; then
    echo -e "${GREEN}✓${NC} Macs Fan Control is installed"
else
    echo -e "${YELLOW}⚠${NC} Macs Fan Control not found (optional for thermal management)"
    echo "  Install from: https://crystalidea.com/macs-fan-control"
fi

# Create necessary directories
echo ""
echo -e "${YELLOW}Setting up directories...${NC}"
mkdir -p logs
mkdir -p config
mkdir -p examples
echo -e "${GREEN}✓${NC} Directories created"

# Make scripts executable
echo -e "${YELLOW}Making scripts executable...${NC}"
chmod +x scripts/*.sh
chmod +x scripts/*.py
chmod +x main_agent.py
echo -e "${GREEN}✓${NC} Scripts are now executable"

# Check for API key
echo ""
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠${NC} OPENAI_API_KEY not set"
    echo "  For AutoGen functionality, set your API key:"
    echo "  export OPENAI_API_KEY='your-key-here'"
    echo "  Or add it to config/agent_config.json"
else
    echo -e "${GREEN}✓${NC} OPENAI_API_KEY is set"
fi

echo ""
echo -e "${GREEN}=== Installation Complete ===${NC}"
echo ""
echo "Next steps:"
echo "  1. Configure your preferences in config/user_preferences.json"
echo "  2. Set your OpenAI API key (if using AutoGen)"
echo "  3. Run: ./scripts/startup.sh --apply-optimizations"
echo "  4. Or try: python3 scripts/quick_optimize.py --status"
echo ""
echo "For more information, see README.md"
