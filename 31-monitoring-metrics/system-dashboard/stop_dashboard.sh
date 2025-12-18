#!/bin/bash
# Stop System Monitoring Dashboard

set -e

DASHBOARD_DIR="$HOME/system-dashboard"
PID_DIR="$DASHBOARD_DIR/pids"

echo "🛑 Stopping System Monitoring Dashboard..."

# Function to stop process
stop_process() {
    local name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            echo "   Stopping $name (PID: $pid)..."
            kill $pid
            sleep 1
            # Force kill if still running
            if kill -0 $pid 2>/dev/null; then
                echo "   Force stopping $name..."
                kill -9 $pid
            fi
            rm "$pid_file"
            echo "   ✅ $name stopped"
        else
            echo "   ⚠️  $name not running (stale PID file)"
            rm "$pid_file"
        fi
    else
        echo "   ℹ️  $name not running"
    fi
}

# Stop all components
stop_process "Web Dashboard" "$PID_DIR/dashboard.pid"
stop_process "Alert Manager" "$PID_DIR/alert_manager.pid"
stop_process "Metrics Collector" "$PID_DIR/metrics_collector.pid"
stop_process "Health Monitor" "$PID_DIR/health_monitor.pid"

echo ""
echo "✅ System Monitoring Dashboard Stopped!"
