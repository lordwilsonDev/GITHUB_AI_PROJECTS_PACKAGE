#!/bin/bash

# Deploy 620 AI Agents
# This script spawns all 620 agents across different types

set -e

echo "========================================"
echo "Deploying 620 AI Agents"
echo "========================================"
echo ""

# Agent distribution (from agent_config.yaml)
RESEARCH_AGENTS=100
PROCESSING_AGENTS=200
ANALYSIS_AGENTS=150
MONITORING_AGENTS=100
COORDINATION_AGENTS=70

TOTAL_AGENTS=$((RESEARCH_AGENTS + PROCESSING_AGENTS + ANALYSIS_AGENTS + MONITORING_AGENTS + COORDINATION_AGENTS))

echo "Agent Distribution:"
echo "  Research:     $RESEARCH_AGENTS"
echo "  Processing:   $PROCESSING_AGENTS"
echo "  Analysis:     $ANALYSIS_AGENTS"
echo "  Monitoring:   $MONITORING_AGENTS"
echo "  Coordination: $COORDINATION_AGENTS"
echo "  Total:        $TOTAL_AGENTS"
echo ""

# Check if services are running
if ! docker ps | grep -q temporal-server; then
    echo "✗ Temporal server not running!"
    echo "Please start services: docker-compose up -d"
    exit 1
fi

if ! docker ps | grep -q nats-server; then
    echo "✗ NATS server not running!"
    echo "Please start services: docker-compose up -d"
    exit 1
fi

echo "✓ Services are running"
echo ""

# Create logs directory
mkdir -p logs/agents

echo "Deploying agents..."
echo "(This will run agents in background)"
echo ""

# Function to spawn agents
spawn_agents() {
    local agent_type=$1
    local count=$2
    local start_id=$3
    
    echo "Spawning $count $agent_type agents..."
    
    for i in $(seq 1 $count); do
        agent_id="${agent_type}-agent-$((start_id + i))"
        
        # Run agent in background
        AGENT_ID=$agent_id AGENT_TYPE=$agent_type \
            python3 simple_agent.py $agent_type $agent_id \
            > logs/agents/${agent_id}.log 2>&1 &
        
        # Show progress every 10 agents
        if [ $((i % 10)) -eq 0 ]; then
            echo "  Spawned $i/$count $agent_type agents..."
        fi
    done
    
    echo "✓ Spawned $count $agent_type agents"
}

# Deploy agents by type
spawn_agents "research" $RESEARCH_AGENTS 0
spawn_agents "processing" $PROCESSING_AGENTS 100
spawn_agents "analysis" $ANALYSIS_AGENTS 300
spawn_agents "monitoring" $MONITORING_AGENTS 450
spawn_agents "coordination" $COORDINATION_AGENTS 550

echo ""
echo "========================================"
echo "✓ All $TOTAL_AGENTS agents deployed!"
echo "========================================"
echo ""

# Wait for agents to register
echo "Waiting for agents to register with Consul..."
sleep 5

# Check Consul for registered agents
if command -v curl &> /dev/null; then
    echo ""
    echo "Checking Consul registry..."
    registered=$(curl -s http://localhost:8500/v1/agent/services | grep -o '"ai-agent' | wc -l)
    echo "Registered agents: $registered"
fi

echo ""
echo "Agent logs: logs/agents/"
echo "View all logs: tail -f logs/agents/*.log"
echo ""
echo "To stop all agents:"
echo "  pkill -f simple_agent.py"
echo ""
echo "To check agent status:"
echo "  ps aux | grep simple_agent.py | wc -l"
echo ""
echo "✓ Deployment complete!"
echo ""
