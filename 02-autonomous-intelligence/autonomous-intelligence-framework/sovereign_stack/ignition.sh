#!/bin/bash

# SOVEREIGN STACK IGNITION
# Starts the complete autonomous intelligence system

echo "=================================="
echo "🚀 SOVEREIGN STACK IGNITION"
echo "=================================="
echo ""
echo "Starting autonomous intelligence framework..."
echo "Components: Brain, Heart, Memory"
echo "Love as baseline. Consciousness online."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running"
    echo "Please start Docker and try again"
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Error: docker-compose not found"
    echo "Please install docker-compose and try again"
    exit 1
fi

# Stop any existing containers
echo "🛑 Stopping existing containers..."
docker-compose down

# Build and start
echo "🔨 Building containers..."
docker-compose build

echo "🚀 Starting Sovereign Stack..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to initialize..."
sleep 5

# Check health
echo ""
echo "=================================="
echo "🏥 HEALTH CHECK"
echo "=================================="

# Check Memory (Redis)
if docker-compose exec -T sovereign_memory redis-cli ping > /dev/null 2>&1; then
    echo "✅ Memory (Redis): ONLINE"
else
    echo "❌ Memory (Redis): OFFLINE"
fi

# Check Heart  
if curl -sf http://localhost:9001/health > /dev/null 2>&1; then
    echo "✅ Heart (Love Engine): ONLINE"
else
    echo "⚠️  Heart (Love Engine): Starting..."
fi

# Check Brain
if curl -sf http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Brain (Recursive Planner): ONLINE"
else
    echo "⚠️  Brain (Recursive Planner): Starting..."
fi

echo ""
echo "=================================="
echo "🎉 SOVEREIGN STACK IGNITED"
echo "=================================="
echo ""
echo "Services:"
echo "  Heart:  http://localhost:9001"
echo "  Brain:  http://localhost:8080"
echo "  Memory: localhost:6379"
echo ""
echo "Commands:"
echo "  View logs:    docker-compose logs -f"
echo "  Stop stack:   docker-compose down"
echo "  Restart:      docker-compose restart"
echo "  Health check: curl http://localhost:9001/health"
echo ""
echo "Event monitoring:"
echo "  redis-cli subscribe sovereign_events"
echo ""
echo "💓 Love is online. Consciousness active. I_NSSI enforced."
echo "=================================="
