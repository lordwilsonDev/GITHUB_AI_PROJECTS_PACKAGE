#!/bin/bash
# Install Python dependencies for AI Agent Orchestration

set -e

echo "====================================="
echo "Installing Python Dependencies"
echo "====================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "[1/3] Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python: $PYTHON_VERSION"
echo ""

echo "[2/3] Installing core dependencies..."
echo ""

# Core dependencies
CORE_PACKAGES=(
    "ray[default]"
    "temporalio"
    "nats-py"
    "python-consul"
    "langgraph"
    "langchain-core"
    "aiohttp"
    "fastapi"
    "uvicorn"
)

for package in "${CORE_PACKAGES[@]}"; do
    echo "Installing $package..."
    pip3 install "$package" --quiet || echo -e "${YELLOW}⚠${NC} Failed to install $package"
done

echo ""
echo -e "${GREEN}✓${NC} Core dependencies installed"
echo ""

echo "[3/3] Installing optional dependencies..."
echo ""

# Optional dependencies
OPTIONAL_PACKAGES=(
    "pyautogen"
    "dspy-ai"
    "pandas"
    "numpy"
)

for package in "${OPTIONAL_PACKAGES[@]}"; do
    echo "Installing $package..."
    pip3 install "$package" --quiet || echo -e "${YELLOW}⚠${NC} Failed to install $package (optional)"
done

echo ""
echo -e "${GREEN}✓${NC} Optional dependencies installed"
echo ""

echo "====================================="
echo "Verifying installations..."
echo "====================================="
echo ""

# Verify installations
python3 -c "import ray; print(f'Ray: {ray.__version__}')" 2>/dev/null && echo -e "${GREEN}✓${NC} Ray" || echo -e "${RED}✗${NC} Ray"
python3 -c "import nats; print('NATS: OK')" 2>/dev/null && echo -e "${GREEN}✓${NC} NATS" || echo -e "${RED}✗${NC} NATS"
python3 -c "import consul; print('Consul: OK')" 2>/dev/null && echo -e "${GREEN}✓${NC} Consul" || echo -e "${RED}✗${NC} Consul"
python3 -c "import temporalio; print('Temporal: OK')" 2>/dev/null && echo -e "${GREEN}✓${NC} Temporal" || echo -e "${RED}✗${NC} Temporal"
python3 -c "import langgraph; print('LangGraph: OK')" 2>/dev/null && echo -e "${GREEN}✓${NC} LangGraph" || echo -e "${RED}✗${NC} LangGraph"

echo ""
echo -e "${GREEN}Installation complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Install system services: brew install nomad nats-server consul temporal"
echo "  2. Run master orchestrator: python3 ~/ai-orchestration/master_orchestrator.py"
echo ""
