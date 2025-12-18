#!/bin/bash
# VY-NEXUS Orchestration Script
# Full cycle: Mine → Synthesize → Propose → Validate

set -e

echo "🌌 VY-NEXUS: Cross-Domain Breakthrough Synthesis"
echo "=================================================="

# Navigate to project
cd ~/vy-nexus

echo ""
echo "Step 1: Running pattern mining & synthesis..."
python3 nexus_core.py

echo ""
echo "Step 2: Bridging to VY Pulse system..."
python3 nexus_pulse_bridge.py

echo ""
echo "✨ VY-NEXUS cycle complete!"
echo ""
echo "📊 Check outputs:"
echo "   - ~/vy-nexus/synthesis/           (breakthrough reports)"
echo "   - ~/nano_memory/pulse/            (constitutional proposals)"
echo ""
echo "🔄 Next: VY Pulse will validate proposals on next cycle"
