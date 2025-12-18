#!/bin/bash
# Setup script for AI Agent Orchestration Stack
# Checks installations and starts services in dev mode

set -e

echo "====================================="
echo "AI Agent Orchestration Stack Setup"
echo "====================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "[1/6] Checking installations..."
echo ""

# Check Nomad
if command_exists nomad; then
    VERSION=$(nomad version | head -n1)
    echo -e "${GREEN}✓${NC} Nomad: $VERSION"
else
    echo -e "${RED}✗${NC} Nomad not found. Install: brew install nomad"
    MISSING=1
fi

# Check NATS
if command_exists nats-server; then
    VERSION=$(nats-server --version 2>&1 | head -n1)
    echo -e "${GREEN}✓${NC} NATS: $VERSION"
else
    echo -e "${RED}✗${NC} NATS not found. Install: brew install nats-server"
    MISSING=1
fi

# Check Consul
if command_exists consul; then
    VERSION=$(consul version | head -n1)
    echo -e "${GREEN}✓${NC} Consul: $VERSION"
else
    echo -e "${RED}✗${NC} Consul not found. Install: brew install consul"
    MISSING=1
fi

# Check Temporal
if command_exists temporal; then
    VERSION=$(temporal --version 2>&1 | head -n1)
    echo -e "${GREEN}✓${NC} Temporal CLI: $VERSION"
else
    echo -e "${RED}✗${NC} Temporal not found. Install: brew install temporal"
    MISSING=1
fi

# Check Ray
if python3 -c "import ray" 2>/dev/null; then
    VERSION=$(python3 -c "import ray; print(f'v{ray.__version__}')")
    echo -e "${GREEN}✓${NC} Ray: $VERSION"
else
    echo -e "${RED}✗${NC} Ray not found. Install: pip3 install ray[default]"
    MISSING=1
fi

# Check Python packages
echo ""
echo "[2/6] Checking Python packages..."
echo ""

PYTHON_PACKAGES=("temporalio" "nats" "consul" "langgraph" "langchain_core")
for package in "${PYTHON_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $package"
    else
        echo -e "${YELLOW}!${NC} $package not found (optional)"
    fi
done

if [ -n "$MISSING" ]; then
    echo ""
    echo -e "${RED}Missing required components. Please install them first.${NC}"
    echo ""
    echo "Quick install:"
    echo "  brew install nomad nats-server consul temporal"
    echo "  pip3 install ray[default] temporalio nats-py python-consul langgraph langchain-core"
    exit 1
fi

echo ""
echo -e "${GREEN}All components installed!${NC}"
echo ""

# Create directories
echo "[3/6] Creating directories..."
mkdir -p ~/ai-orchestration/logs
mkdir -p ~/ai-orchestration/data
mkdir -p ~/ai-orchestration/config
echo -e "${GREEN}✓${NC} Directories created"

echo ""
echo "[4/6] Service startup options:"
echo ""
echo "Start services individually:"
echo ""
echo "  Nomad (dev mode):"
echo "    nomad agent -dev -bind 0.0.0.0 > ~/ai-orchestration/logs/nomad.log 2>&1 &"
echo "    UI: http://localhost:4646"
echo ""
echo "  NATS with JetStream:"
echo "    nats-server -js -sd ~/ai-orchestration/data/nats > ~/ai-orchestration/logs/nats.log 2>&1 &"
echo "    Port: 4222"
echo ""
echo "  Consul (dev mode):"
echo "    consul agent -dev > ~/ai-orchestration/logs/consul.log 2>&1 &"
echo "    UI: http://localhost:8500"
echo ""
echo "  Temporal (dev mode):"
echo "    temporal server start-dev > ~/ai-orchestration/logs/temporal.log 2>&1 &"
echo "    UI: http://localhost:8233"
echo ""

echo "[5/6] Resource monitoring:"
echo ""
echo "  Check running services:"
echo "    ps aux | grep -E 'nomad|nats|consul|temporal'"
echo ""
echo "  Monitor resource usage:"
echo "    top -pid \$(pgrep -d, 'nomad|nats|consul|temporal')"
echo ""

echo "[6/6] Next steps:"
echo ""
echo "  1. Start services (see commands above)"
echo "  2. Run example workflows:"
echo "     python3 ~/ai-orchestration/temporal-workflow-example.py"
echo "     python3 ~/ai-orchestration/ray-agent-actors.py"
echo "     python3 ~/ai-orchestration/nats-agent-messaging.py"
echo "     python3 ~/ai-orchestration/langgraph-safety-gates.py"
echo ""
echo "  3. Deploy Nomad job:"
echo "     nomad job run ~/ai-orchestration/nomad-agent-job.hcl"
echo ""
echo "  4. Configure Datadog monitoring (if installed)"
echo ""
echo -e "${GREEN}Setup complete!${NC}"
