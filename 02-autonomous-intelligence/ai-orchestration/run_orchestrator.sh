#!/bin/bash
# Run the AI Agent Orchestration System

set -e

echo "====================================="
echo "AI Agent Orchestration System"
echo "====================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

cd ~/ai-orchestration

echo -e "${BLUE}[1/3] Checking Python dependencies...${NC}"
python3 -c "import asyncio" 2>/dev/null && echo -e "${GREEN}✓${NC} asyncio" || echo -e "${RED}✗${NC} asyncio"
python3 -c "import logging" 2>/dev/null && echo -e "${GREEN}✓${NC} logging" || echo -e "${RED}✗${NC} logging"
python3 -c "import json" 2>/dev/null && echo -e "${GREEN}✓${NC} json" || echo -e "${RED}✗${NC} json"

echo ""
echo -e "${BLUE}[2/3] Optional dependencies (system will work without these):${NC}"
python3 -c "import ray" 2>/dev/null && echo -e "${GREEN}✓${NC} Ray (distributed execution)" || echo -e "${YELLOW}⚠${NC} Ray not installed (will use local mode)"
python3 -c "import nats" 2>/dev/null && echo -e "${GREEN}✓${NC} NATS (messaging)" || echo -e "${YELLOW}⚠${NC} NATS not installed (will use fallback)"
python3 -c "import consul" 2>/dev/null && echo -e "${GREEN}✓${NC} Consul (service discovery)" || echo -e "${YELLOW}⚠${NC} Consul not installed (optional)"
python3 -c "import temporalio" 2>/dev/null && echo -e "${GREEN}✓${NC} Temporal (workflows)" || echo -e "${YELLOW}⚠${NC} Temporal not installed (optional)"

echo ""
echo -e "${BLUE}[3/3] Starting Enhanced Master Orchestrator...${NC}"
echo ""
echo -e "${YELLOW}This will start:${NC}"
echo "  - Task Queue System (priority-based scheduling)"
echo "  - Message Bus (inter-agent communication)"
echo "  - Worker Agent Pool (10 workers)"
echo "  - Coordinator Agents (2 coordinators)"
echo "  - Specialized Agents (JARVIS, Level33, NanoApex, MoIE)"
echo "  - Task Scheduler (automatic task distribution)"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop${NC}"
echo ""

# Run the orchestrator
python3 master_orchestrator.py
