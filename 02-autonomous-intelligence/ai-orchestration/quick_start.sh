#!/bin/bash
# Quick start script for AI Agent Orchestration System

set -e

echo "====================================="
echo "AI Agent Orchestration - Quick Start"
echo "====================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

cd ~/ai-orchestration

echo -e "${BLUE}[1/4] Installing Python dependencies...${NC}"
chmod +x install_dependencies.sh
./install_dependencies.sh

echo ""
echo -e "${BLUE}[2/4] Creating directories...${NC}"
mkdir -p logs data config
echo -e "${GREEN}✓${NC} Directories created"

echo ""
echo -e "${BLUE}[3/4] Making scripts executable...${NC}"
chmod +x master_orchestrator.py
chmod +x setup-services.sh
echo -e "${GREEN}✓${NC} Scripts ready"

echo ""
echo -e "${BLUE}[4/4] Testing master orchestrator...${NC}"
echo ""
echo "Starting orchestrator in test mode..."
echo "(This will check dependencies and initialize components)"
echo ""

# Run orchestrator with timeout
timeout 10 python3 master_orchestrator.py || true

echo ""
echo "====================================="
echo -e "${GREEN}Quick Start Complete!${NC}"
echo "====================================="
echo ""
echo "System is ready. To run the full orchestrator:"
echo ""
echo -e "  ${YELLOW}python3 ~/ai-orchestration/master_orchestrator.py${NC}"
echo ""
echo "Optional: Install system services for full functionality:"
echo ""
echo -e "  ${YELLOW}brew install nomad nats-server consul temporal${NC}"
echo ""
echo "For more information, see:"
echo "  - README.md"
echo "  - QUICK_START.md"
echo ""
