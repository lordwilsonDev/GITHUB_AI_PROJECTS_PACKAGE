#!/bin/bash
# setup_ouroboros.sh - Clean setup for Ouroboros governor loop system

echo "=== Setting up Ouroboros Node ==="

# Kill any existing daemons
echo "Cleaning up existing daemons..."
pkill -f vy_grounding_daemon.sh 2>/dev/null || true
sleep 2

# Start the grounding daemon from home directory
echo "Starting Vy grounding daemon..."
/Users/lordwilson/vy_grounding_daemon.sh &
sleep 5

# Verify daemon is running
DAEMON_COUNT=$(ps aux | grep vy_grounding_daemon | grep -v grep | wc -l)
if [ $DAEMON_COUNT -eq 1 ]; then
    echo "✅ Daemon started successfully"
else
    echo "❌ Daemon failed to start or multiple instances running"
fi

# Check grounding layer
echo "
Checking grounding layer..."
if [ -f ~/.truth_anchor.json ] && [ -f ~/.current_mode.json ]; then
    echo "✅ Grounding files created"
    cat ~/.current_mode.json
else
    echo "❌ Grounding files missing"
fi

# Test the governor
echo "
Testing governor integration..."
./motia.sh "mode test"

echo "
=== Ouroboros Node Ready ==="
echo "Run './quick_health_check.sh' for status checks"
echo "Run 'node node_status.cjs' for detailed status"
# setup_ouroboros.sh - Clean setup and health check for Ouroboros node

echo "=== Ouroboros Node Setup ==="

# 1. Clean up any existing daemons
echo "🧹 Cleaning up existing daemons..."
pkill -f vy_grounding_daemon.sh 2>/dev/null || true
sleep 2

# 2. Start fresh daemon from absolute path
echo "🚀 Starting Vy grounding daemon..."
/Users/lordwilson/vy_grounding_daemon.sh &
sleep 5

# 3. Verify single daemon running
echo "🔍 Checking daemon status..."
DAEMON_COUNT=$(ps aux | grep vy_grounding_daemon | grep -v grep | wc -l)
if [ "$DAEMON_COUNT" -eq 1 ]; then
    echo "✅ Single daemon running correctly"
    ps aux | grep vy_grounding_daemon | grep -v grep
else
    echo "❌ Expected 1 daemon, found $DAEMON_COUNT"
    ps aux | grep vy_grounding_daemon | grep -v grep
fi

# 4. Health check - grounding layer
echo ""
echo "🏥 Health Check - Grounding Layer:"
if [ -f ~/.truth_anchor.json ]; then
    echo "✅ Truth anchor exists"
    echo "📊 System metrics:"
    cat ~/.truth_anchor.json | grep -E '"load_1m"|"ram_ratio"' | head -2
else
    echo "❌ Missing ~/.truth_anchor.json"
fi

if [ -f ~/.current_mode.json ]; then
    echo "✅ Current mode exists"
    echo "🎛️  Mode status:"
    cat ~/.current_mode.json | grep -E '"mode"|"system_policy"|"resonance_mode"'
else
    echo "❌ Missing ~/.current_mode.json"
fi

# 5. Health check - constitutional layer
echo ""
echo "🧬 Health Check - Constitutional Layer:"
if [ -f moie_history.jsonl ]; then
    INVERSION_COUNT=$(wc -l < moie_history.jsonl)
    echo "✅ Constitutional history exists with $INVERSION_COUNT inversions"
    echo "🔬 Latest inversion:"
    tail -n 1 moie_history.jsonl | head -c 200
    echo "..."
else
    echo "❌ Missing moie_history.jsonl"
fi

# 6. Quick execution test
echo ""
echo "🧪 Testing execution layer..."
node test_nano.js

echo ""
echo "📋 Final status:"
node node_status.cjs

echo ""
echo "🎉 Ouroboros node setup complete!"
echo "💡 Next: Run './motia.sh \"mode test\"' to test governor integration"