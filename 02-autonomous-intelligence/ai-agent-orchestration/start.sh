#!/bin/bash

# AI Orchestration System - Startup Script
# This script starts the 620-agent orchestration system

set -e

echo "========================================"
echo "AI Orchestration System - Startup"
echo "========================================"
echo ""

# Check if Docker is running
echo "[1/5] Checking Docker status..."
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running!"
    echo "Please start Docker Desktop and try again."
    echo ""
    echo "To start Docker Desktop:"
    echo "  open -a Docker"
    exit 1
fi
echo "✓ Docker is running"
echo ""

# Navigate to project directory
echo "[2/5] Navigating to project directory..."
cd "$(dirname "$0")"
echo "✓ In directory: $(pwd)"
echo ""

# Pull latest images (optional, can be slow)
echo "[3/5] Checking Docker images..."
echo "(This may take a few minutes on first run)"
echo ""

# Start services
echo "[4/5] Starting all services..."
echo "This will start:"
echo "  - Consul (Service Discovery)"
echo "  - NATS (Messaging)"
echo "  - PostgreSQL (Database)"
echo "  - Temporal (Workflow Orchestration)"
echo "  - Ray (Distributed Computing)"
echo "  - Nomad (Agent Management)"
echo "  - Prometheus (Metrics)"
echo "  - Grafana (Monitoring)"
echo ""

docker-compose up -d

echo ""
echo "[5/5] Waiting for services to initialize..."
sleep 10

# Check status
echo ""
echo "========================================"
echo "Service Status:"
echo "========================================"
docker-compose ps

echo ""
echo "========================================"
echo "System Ready!"
echo "========================================"
echo ""
echo "Access your dashboards:"
echo ""
echo "  Temporal UI:      http://localhost:8080"
echo "  Ray Dashboard:    http://localhost:8265"
echo "  Consul UI:        http://localhost:8500"
echo "  Nomad UI:         http://localhost:4646"
echo "  NATS Monitoring:  http://localhost:8222"
echo "  Prometheus:       http://localhost:9090"
echo "  Grafana:          http://localhost:3000 (admin/admin)"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop the system:"
echo "  docker-compose down"
echo ""
echo "========================================"
