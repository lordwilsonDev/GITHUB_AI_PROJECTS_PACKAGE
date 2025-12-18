#!/bin/bash

# AI Orchestration System - Shutdown Script

set -e

echo "========================================"
echo "AI Orchestration System - Shutdown"
echo "========================================"
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

echo "Stopping all services..."
echo ""

docker-compose down

echo ""
echo "========================================"
echo "System Stopped"
echo "========================================"
echo ""
echo "To start again:"
echo "  ./start.sh"
echo ""
echo "To remove all data (clean slate):"
echo "  docker-compose down -v"
echo ""
