#!/bin/bash
# Check status of all AI Agent Orchestration Stack services

echo "====================================="
echo "  Stack Status"
echo "====================================="
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

check_service() {
    SERVICE=$1
    PATTERN=$2
    PORT=$3
    
    if pgrep -f "$PATTERN" > /dev/null; then
        PID=$(pgrep -f "$PATTERN")
        echo -e "${GREEN}✓${NC} $SERVICE (PID: $PID)"
        if [ ! -z "$PORT" ]; then
            if nc -z localhost $PORT 2>/dev/null; then
                echo "  Port $PORT: OPEN"
            else
                echo "  Port $PORT: CLOSED"
            fi
        fi
    else
        echo -e "${RED}✗${NC} $SERVICE (not running)"
    fi
}

check_service "Nomad" "nomad agent" "4646"
check_service "NATS" "nats-server" "4222"
check_service "Consul" "consul agent" "8500"
check_service "Temporal" "temporal server" "8233"

echo ""
echo "Service UIs:"
echo "  • Nomad:    http://localhost:4646"
echo "  • Consul:   http://localhost:8500"
echo "  • Temporal: http://localhost:8233"
echo ""
echo "Resource Usage:"
ps aux | grep -E 'nomad|nats-server|consul|temporal' | grep -v grep | awk '{printf "  %-15s %5s%% CPU  %5s%% MEM\n", $11, $3, $4}'
echo ""
