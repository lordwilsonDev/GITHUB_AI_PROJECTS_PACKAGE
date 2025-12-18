#!/bin/bash

# AI Orchestration System - Status Check

set -e

echo "========================================"
echo "AI Orchestration System - Status"
echo "========================================"
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

# Check Docker
echo "[Docker Status]"
if docker info > /dev/null 2>&1; then
    echo "✓ Docker is running"
else
    echo "✗ Docker is NOT running"
    exit 1
fi
echo ""

# Check services
echo "[Service Status]"
docker-compose ps
echo ""

# Check resource usage
echo "[Resource Usage]"
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
echo ""

echo "========================================"
echo "Dashboard URLs:"
echo "========================================"
echo "  Temporal UI:      http://localhost:8080"
echo "  Ray Dashboard:    http://localhost:8265"
echo "  Consul UI:        http://localhost:8500"
echo "  Nomad UI:         http://localhost:4646"
echo "  NATS Monitoring:  http://localhost:8222"
echo "  Prometheus:       http://localhost:9090"
echo "  Grafana:          http://localhost:3000"
echo ""
