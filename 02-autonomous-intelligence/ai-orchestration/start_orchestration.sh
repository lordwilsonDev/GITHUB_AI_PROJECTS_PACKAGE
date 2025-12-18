#!/bin/bash

# AI Agent Orchestration System - Startup Script
# This script starts all Docker containers for the 620-agent orchestration system

set -e

echo "========================================"
echo "AI Agent Orchestration System"
echo "Starting Docker Containers..."
echo "========================================"
echo ""

# Change to script directory
cd "$(dirname "$0")"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "✗ Docker is not running!"
    echo ""
    echo "Please start Docker Desktop:"
    echo "  1. Open Docker Desktop application"
    echo "  2. Wait for Docker to start (whale icon in menu bar)"
    echo "  3. Run this script again"
    echo ""
    exit 1
fi

echo "✓ Docker is running"
echo ""

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "✗ docker-compose.yml not found!"
    echo "Please ensure you're in the ai-orchestration directory"
    exit 1
fi

echo "✓ docker-compose.yml found"
echo ""

# Stop any existing containers
echo "Stopping any existing containers..."
docker-compose down 2>/dev/null || true
echo ""

# Start containers
echo "Starting containers..."
echo "This may take 1-2 minutes for first-time setup..."
echo ""

docker-compose up -d

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✓ All containers started successfully!"
    echo "========================================"
    echo ""
    echo "Waiting for services to initialize (30 seconds)..."
    
    # Progress bar
    for i in {1..30}; do
        echo -n "."
        sleep 1
    done
    echo ""
    echo ""
    
    echo "Container Status:"
    docker-compose ps
    echo ""
    
    echo "========================================"
    echo "Service URLs:"
    echo "========================================"
    echo "Temporal Web UI:    http://localhost:8080"
    echo "Ray Dashboard:      http://localhost:8265"
    echo "Consul UI:          http://localhost:8500"
    echo "NATS Monitoring:    http://localhost:8222"
    echo ""
    
    echo "========================================"
    echo "Quick Commands:"
    echo "========================================"
    echo "View logs:          docker-compose logs -f"
    echo "Stop services:      docker-compose down"
    echo "Restart services:   docker-compose restart"
    echo "Check status:       docker-compose ps"
    echo ""
    
    echo "========================================"
    echo "Next Steps:"
    echo "========================================"
    echo "1. Open Temporal UI: http://localhost:8080"
    echo "2. Open Ray Dashboard: http://localhost:8265"
    echo "3. Deploy agent framework (see README.md)"
    echo "4. Run test workflow"
    echo ""
    
    echo "✓ System ready for agent deployment!"
    echo ""
else
    echo ""
    echo "✗ Failed to start containers"
    echo "Check logs with: docker-compose logs"
    exit 1
fi
