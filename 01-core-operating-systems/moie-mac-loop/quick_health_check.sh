#!/bin/bash
# quick_health_check.sh - Fast status check for Ouroboros node

echo "=== Quick Ouroboros Health Check ==="

# Check daemon
DAEMON_COUNT=$(ps aux | grep vy_grounding_daemon | grep -v grep | wc -l)
echo "Daemons running: $DAEMON_COUNT"

# Check grounding files
if [ -f ~/.truth_anchor.json ] && [ -f ~/.current_mode.json ]; then
    echo "✅ Grounding layer: OK"
else
    echo "❌ Grounding layer: Missing files"
fi

# Check constitutional layer
if [ -f moie_history.jsonl ]; then
    INVERSIONS=$(wc -l < moie_history.jsonl)
    echo "✅ Constitutional layer: $INVERSIONS inversions"
else
    echo "❌ Constitutional layer: Missing history"
fi

# Quick status
node node_status.cjs 2>/dev/null || echo "❌ Node status script failed"

echo ""
echo "💡 Run './setup_ouroboros.sh' for full setup"
echo "💡 Run './motia.sh \"mode test\"' to test governor"