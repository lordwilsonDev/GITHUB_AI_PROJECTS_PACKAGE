#!/bin/bash
# Stop all AI Agent Orchestration Stack services

echo "Stopping AI Agent Orchestration Stack..."
echo ""

pkill -f "nomad agent" && echo "✓ Stopped Nomad" || echo "✗ Nomad not running"
pkill -f "nats-server" && echo "✓ Stopped NATS" || echo "✗ NATS not running"
pkill -f "consul agent" && echo "✓ Stopped Consul" || echo "✗ Consul not running"
pkill -f "temporal server" && echo "✓ Stopped Temporal" || echo "✗ Temporal not running"

echo ""
echo "All services stopped."
