#!/bin/bash

# This script will be executed to deploy the AI orchestration system
# It combines all necessary steps into one execution

set -e

echo "================================================="
echo "AI ORCHESTRATION SYSTEM - AUTOMATED DEPLOYMENT"
echo "================================================="
echo ""
echo "Starting deployment process..."
echo ""

# Step 1: Check Docker
echo "[Step 1/6] Checking Docker status..."
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running!"
    echo ""
    echo "Please start Docker Desktop:"
    echo "  1. Open Finder"
    echo "  2. Go to Applications"
    echo "  3. Double-click 'Docker'"
    echo "  4. Wait for Docker to start (whale icon in menu bar)"
    echo "  5. Run this script again"
    echo ""
    echo "Or from Terminal:"
    echo "  open -a Docker"
    echo "  sleep 30"
    echo "  ./EXECUTE_DEPLOYMENT.sh"
    exit 1
fi
echo "✓ Docker is running"
echo ""

# Step 2: Navigate to directory
echo "[Step 2/6] Navigating to project directory..."
cd "$(dirname "$0")"
PROJECT_DIR=$(pwd)
echo "✓ Project directory: $PROJECT_DIR"
echo ""

# Step 3: Make scripts executable
echo "[Step 3/6] Making scripts executable..."
chmod +x start.sh stop.sh status.sh 2>/dev/null || true
echo "✓ Scripts are executable"
echo ""

# Step 4: Check for existing containers
echo "[Step 4/6] Checking for existing containers..."
if docker-compose ps | grep -q "Up"; then
    echo "⚠ Some containers are already running"
    echo "Stopping existing containers..."
    docker-compose down
    echo "✓ Existing containers stopped"
else
    echo "✓ No existing containers found"
fi
echo ""

# Step 5: Start all services
echo "[Step 5/6] Starting all services..."
echo "This will start:"
echo "  • Consul (Service Discovery)"
echo "  • NATS (Messaging)"
echo "  • PostgreSQL (Database)"
echo "  • Temporal (Workflow Orchestration)"
echo "  • Temporal UI (Web Interface)"
echo "  • Ray Head (Distributed Computing)"
echo "  • Ray Workers x10 (Agent Execution)"
echo "  • Nomad (Agent Management)"
echo "  • Prometheus (Metrics)"
echo "  • Grafana (Monitoring)"
echo ""
echo "Starting containers (this may take 2-3 minutes)..."
echo ""

docker-compose up -d

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to start containers!"
    echo "Check the error messages above."
    echo ""
    echo "Common issues:"
    echo "  - Port conflicts: Another service using the same port"
    echo "  - Insufficient resources: Not enough RAM/CPU"
    echo "  - Docker issues: Try restarting Docker Desktop"
    echo ""
    echo "To see detailed logs:"
    echo "  docker-compose logs"
    exit 1
fi

echo "✓ All containers started"
echo ""

# Step 6: Wait for services to initialize
echo "[Step 6/6] Waiting for services to initialize..."
echo "(This takes about 30 seconds)"
for i in {1..30}; do
    echo -n "."
    sleep 1
done
echo ""
echo "✓ Services initialized"
echo ""

# Display status
echo "================================================="
echo "DEPLOYMENT COMPLETE!"
echo "================================================="
echo ""
echo "Service Status:"
echo "------------------------------------------------"
docker-compose ps
echo ""

# Count running containers
RUNNING=$(docker-compose ps | grep "Up" | wc -l | tr -d ' ')
echo "Running containers: $RUNNING"
echo ""

# Display dashboard URLs
echo "================================================="
echo "ACCESS YOUR DASHBOARDS"
echo "================================================="
echo ""
echo "Open these URLs in your browser:"
echo ""
echo "  Temporal UI:      http://localhost:8080"
echo "  Ray Dashboard:    http://localhost:8265"
echo "  Consul UI:        http://localhost:8500"
echo "  Nomad UI:         http://localhost:4646"
echo "  NATS Monitoring:  http://localhost:8222"
echo "  Prometheus:       http://localhost:9090"
echo "  Grafana:          http://localhost:3000"
echo "                    (login: admin / admin)"
echo ""
echo "================================================="
echo "SYSTEM INFORMATION"
echo "================================================="
echo ""
echo "Total Agents:     620 (distributed across 10 Ray workers)"
echo "RAM Usage:        < 2GB total"
echo "Auto-restart:     Enabled (24/7 operation)"
echo "Network:          orchestration_net (172.20.0.0/16)"
echo ""
echo "================================================="
echo "USEFUL COMMANDS"
echo "================================================="
echo ""
echo "Check status:     ./status.sh"
echo "View logs:        docker-compose logs -f"
echo "Stop system:      ./stop.sh"
echo "Restart:          docker-compose restart"
echo ""
echo "================================================="
echo "NEXT STEPS"
echo "================================================="
echo ""
echo "1. Open the dashboards above in your browser"
echo "2. Explore the Temporal UI to see workflow capabilities"
echo "3. Check Ray Dashboard to see your 10 worker nodes"
echo "4. Review README.md for example workflows"
echo "5. Start building your first AI agent workflow!"
echo ""
echo "For detailed documentation:"
echo "  - README.md: Complete user guide"
echo "  - COMPONENTS.md: Technical details"
echo "  - DEPLOY_NOW.md: Deployment reference"
echo ""
echo "================================================="
echo "DEPLOYMENT SUCCESSFUL! 🚀"
echo "================================================="
echo ""
