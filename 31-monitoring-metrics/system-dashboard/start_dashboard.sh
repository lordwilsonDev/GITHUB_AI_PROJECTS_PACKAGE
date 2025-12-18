#!/bin/bash
# Start System Monitoring Dashboard

set -e

DASHBOARD_DIR="$HOME/system-dashboard"
LOG_DIR="$DASHBOARD_DIR/logs"
PID_DIR="$DASHBOARD_DIR/pids"

echo "🚀 Starting System Monitoring Dashboard..."

# Create necessary directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Change to dashboard directory
cd "$DASHBOARD_DIR"

# Check if database exists
if [ ! -f "$DASHBOARD_DIR/database/monitoring.db" ]; then
    echo "❌ Database not found. Please run ./init_database.sh first"
    exit 1
fi

# Function to check if process is running
is_running() {
    [ -f "$1" ] && kill -0 $(cat "$1") 2>/dev/null
}

# Start Health Monitor
if is_running "$PID_DIR/health_monitor.pid"; then
    echo "⚠️  Health Monitor already running"
else
    echo "🏥 Starting Health Monitor..."
    nohup python3 backend/health_monitor.py > "$LOG_DIR/health_monitor.log" 2>&1 &
    echo $! > "$PID_DIR/health_monitor.pid"
    echo "   PID: $(cat $PID_DIR/health_monitor.pid)"
fi

# Start Metrics Collector
if is_running "$PID_DIR/metrics_collector.pid"; then
    echo "⚠️  Metrics Collector already running"
else
    echo "📊 Starting Metrics Collector..."
    nohup python3 backend/metrics_collector.py > "$LOG_DIR/metrics_collector.log" 2>&1 &
    echo $! > "$PID_DIR/metrics_collector.pid"
    echo "   PID: $(cat $PID_DIR/metrics_collector.pid)"
fi

# Start Alert Manager
if is_running "$PID_DIR/alert_manager.pid"; then
    echo "⚠️  Alert Manager already running"
else
    echo "🚨 Starting Alert Manager..."
    nohup python3 backend/alert_manager.py > "$LOG_DIR/alert_manager.log" 2>&1 &
    echo $! > "$PID_DIR/alert_manager.pid"
    echo "   PID: $(cat $PID_DIR/alert_manager.pid)"
fi

# Start Web Dashboard (FastAPI)
if is_running "$PID_DIR/dashboard.pid"; then
    echo "⚠️  Web Dashboard already running"
else
    echo "🌐 Starting Web Dashboard on port 9000..."
    nohup uvicorn main:app --host 0.0.0.0 --port 9000 > "$LOG_DIR/dashboard.log" 2>&1 &
    echo $! > "$PID_DIR/dashboard.pid"
    echo "   PID: $(cat $PID_DIR/dashboard.pid)"
fi

sleep 2

echo ""
echo "✅ System Monitoring Dashboard Started!"
echo ""
echo "📊 Dashboard URL: http://localhost:9000"
echo "📁 Logs directory: $LOG_DIR"
echo ""
echo "To stop the dashboard, run: ./stop_dashboard.sh"
echo "To view logs, run: tail -f $LOG_DIR/*.log"
