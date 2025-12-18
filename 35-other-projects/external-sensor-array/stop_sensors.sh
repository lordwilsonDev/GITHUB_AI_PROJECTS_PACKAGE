#!/bin/bash
# Stop all External Sensor Array services

echo "🛑 Stopping External Sensor Array..."

if [ -f ".pids/epistemic.pid" ]; then
    kill $(cat .pids/epistemic.pid) 2>/dev/null
    echo "Stopped Epistemic Filter"
fi

if [ -f ".pids/breakthrough.pid" ]; then
    kill $(cat .pids/breakthrough.pid) 2>/dev/null
    echo "Stopped Breakthrough Scanner"
fi

if [ -f ".pids/panopticon.pid" ]; then
    kill $(cat .pids/panopticon.pid) 2>/dev/null
    echo "Stopped Panopticon Logger"
fi

# Clean up PID files
rm -rf .pids/*.pid

echo "✅ All services stopped"
