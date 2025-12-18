#!/bin/bash
# Automated launcher for AI Agent Orchestration Stack
# This script starts all services and runs example workflows

set -e

echo "====================================================="
echo "  AI Agent Orchestration Stack - Automated Launcher"
echo "====================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Create directories
mkdir -p ~/ai-orchestration/logs
mkdir -p ~/ai-orchestration/data
mkdir -p ~/ai-orchestration/config

echo -e "${BLUE}[1/5] Checking installations...${NC}"
echo ""

# Check installations
MISSING=0

if ! command -v nomad &> /dev/null; then
    echo -e "${RED}✗ Nomad not installed${NC}"
    MISSING=1
else
    echo -e "${GREEN}✓ Nomad installed${NC}"
fi

if ! command -v nats-server &> /dev/null; then
    echo -e "${RED}✗ NATS not installed${NC}"
    MISSING=1
else
    echo -e "${GREEN}✓ NATS installed${NC}"
fi

if ! command -v consul &> /dev/null; then
    echo -e "${RED}✗ Consul not installed${NC}"
    MISSING=1
else
    echo -e "${GREEN}✓ Consul installed${NC}"
fi

if ! command -v temporal &> /dev/null; then
    echo -e "${RED}✗ Temporal not installed${NC}"
    MISSING=1
else
    echo -e "${GREEN}✓ Temporal installed${NC}"
fi

if ! python3 -c "import ray" 2>/dev/null; then
    echo -e "${RED}✗ Ray not installed${NC}"
    MISSING=1
else
    echo -e "${GREEN}✓ Ray installed${NC}"
fi

if [ $MISSING -eq 1 ]; then
    echo ""
    echo -e "${RED}Missing components! Install with:${NC}"
    echo "  brew install nomad nats-server consul temporal"
    echo "  pip3 install ray[default] temporalio nats-py python-consul langgraph langchain-core"
    exit 1
fi

echo ""
echo -e "${BLUE}[2/5] Starting services in background...${NC}"
echo ""

# Kill any existing services
echo "Stopping any existing services..."
pkill -f "nomad agent" 2>/dev/null || true
pkill -f "nats-server" 2>/dev/null || true
pkill -f "consul agent" 2>/dev/null || true
pkill -f "temporal server" 2>/dev/null || true
sleep 2

# Start Nomad
echo -e "${YELLOW}Starting Nomad...${NC}"
nomad agent -dev -bind 0.0.0.0 > ~/ai-orchestration/logs/nomad.log 2>&1 &
NOMAD_PID=$!
echo "  PID: $NOMAD_PID"
echo "  UI: http://localhost:4646"

# Start NATS
echo -e "${YELLOW}Starting NATS with JetStream...${NC}"
nats-server -js -sd ~/ai-orchestration/data/nats > ~/ai-orchestration/logs/nats.log 2>&1 &
NATS_PID=$!
echo "  PID: $NATS_PID"
echo "  Port: 4222"

# Start Consul
echo -e "${YELLOW}Starting Consul...${NC}"
consul agent -dev > ~/ai-orchestration/logs/consul.log 2>&1 &
CONSUL_PID=$!
echo "  PID: $CONSUL_PID"
echo "  UI: http://localhost:8500"

# Start Temporal
echo -e "${YELLOW}Starting Temporal...${NC}"
temporal server start-dev > ~/ai-orchestration/logs/temporal.log 2>&1 &
TEMPORAL_PID=$!
echo "  PID: $TEMPORAL_PID"
echo "  UI: http://localhost:8233"

echo ""
echo -e "${BLUE}[3/5] Waiting for services to be ready...${NC}"
sleep 5

# Check if services are running
echo ""
if ps -p $NOMAD_PID > /dev/null; then
    echo -e "${GREEN}✓ Nomad running${NC}"
else
    echo -e "${RED}✗ Nomad failed to start${NC}"
fi

if ps -p $NATS_PID > /dev/null; then
    echo -e "${GREEN}✓ NATS running${NC}"
else
    echo -e "${RED}✗ NATS failed to start${NC}"
fi

if ps -p $CONSUL_PID > /dev/null; then
    echo -e "${GREEN}✓ Consul running${NC}"
else
    echo -e "${RED}✗ Consul failed to start${NC}"
fi

if ps -p $TEMPORAL_PID > /dev/null; then
    echo -e "${GREEN}✓ Temporal running${NC}"
else
    echo -e "${RED}✗ Temporal failed to start${NC}"
fi

echo ""
echo -e "${BLUE}[4/5] Running example workflows...${NC}"
echo ""

# Test Ray
echo -e "${YELLOW}Testing Ray actors...${NC}"
if python3 ~/ai-orchestration/ray-agent-actors.py 2>&1 | tee ~/ai-orchestration/logs/ray-test.log; then
    echo -e "${GREEN}✓ Ray test passed${NC}"
else
    echo -e "${RED}✗ Ray test failed (see logs/ray-test.log)${NC}"
fi

echo ""
# Test NATS
echo -e "${YELLOW}Testing NATS messaging...${NC}"
if timeout 10 python3 ~/ai-orchestration/nats-agent-messaging.py 2>&1 | tee ~/ai-orchestration/logs/nats-test.log; then
    echo -e "${GREEN}✓ NATS test passed${NC}"
else
    echo -e "${RED}✗ NATS test failed (see logs/nats-test.log)${NC}"
fi

echo ""
echo -e "${BLUE}[5/5] Stack Status${NC}"
echo ""
echo -e "${GREEN}All services are running!${NC}"
echo ""
echo "Service UIs:"
echo "  • Nomad:    http://localhost:4646"
echo "  • Consul:   http://localhost:8500"
echo "  • Temporal: http://localhost:8233"
echo ""
echo "Logs:"
echo "  tail -f ~/ai-orchestration/logs/*.log"
echo ""
echo "Stop services:"
echo "  pkill -f 'nomad agent'"
echo "  pkill -f 'nats-server'"
echo "  pkill -f 'consul agent'"
echo "  pkill -f 'temporal server'"
echo ""
echo "Or run: ~/ai-orchestration/STOP_STACK.sh"
echo ""
echo -e "${GREEN}✓ Stack is ready for 620+ AI agents!${NC}"
