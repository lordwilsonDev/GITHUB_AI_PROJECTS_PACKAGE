#!/bin/bash
# Check System Monitoring Dashboard Status

DASHBOARD_DIR="$HOME/system-dashboard"
PID_DIR="$DASHBOARD_DIR/pids"
LOG_DIR="$DASHBOARD_DIR/logs"

echo "📊 System Monitoring Dashboard Status"
echo "═══════════════════════════════════════"
echo ""

# Function to check process status
check_status() {
    local name=$1
    local pid_file=$2
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            echo "✅ $name: RUNNING (PID: $pid)"
            return 0
        else
            echo "❌ $name: STOPPED (stale PID file)"
            return 1
        fi
    else
        echo "❌ $name: STOPPED"
        return 1
    fi
}

# Check all components
check_status "Health Monitor" "$PID_DIR/health_monitor.pid"
check_status "Metrics Collector" "$PID_DIR/metrics_collector.pid"
check_status "Alert Manager" "$PID_DIR/alert_manager.pid"
check_status "Web Dashboard" "$PID_DIR/dashboard.pid"

echo ""
echo "📁 Recent Log Activity:"
echo "───────────────────────"
if [ -d "$LOG_DIR" ]; then
    for log in "$LOG_DIR"/*.log; do
        if [ -f "$log" ]; then
            echo "$(basename $log): $(wc -l < $log) lines"
        fi
    done
else
    echo "No logs directory found"
fi

echo ""
echo "🌐 Dashboard URL: http://localhost:9000"
