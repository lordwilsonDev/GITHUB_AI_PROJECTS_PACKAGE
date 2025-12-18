#!/bin/bash
# Startup script for External Sensor Array
# Run all three services in background

echo "🚀 Starting External Sensor Array..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start Epistemic Filter (Port 9002)
echo "Starting Epistemic Filter on port 9002..."
python3 epistemic_filter.py > logs/epistemic_filter.log 2>&1 &
EPISTEMIC_PID=$!
echo "Epistemic Filter PID: $EPISTEMIC_PID"

# Start Breakthrough Scanner (Port 9003)
echo "Starting Breakthrough Scanner on port 9003..."
python3 breakthrough_scanner.py > logs/breakthrough_scanner.log 2>&1 &
BREAKTHROUGH_PID=$!
echo "Breakthrough Scanner PID: $BREAKTHROUGH_PID"

# Start Panopticon Logger (Port 9004)
echo "Starting Panopticon Logger on port 9004..."
python3 panopticon_logger.py > logs/panopticon_logger.log 2>&1 &
PANOPTICON_PID=$!
echo "Panopticon Logger PID: $PANOPTICON_PID"

# Save PIDs for easy shutdown
echo "$EPISTEMIC_PID" > .pids/epistemic.pid
echo "$BREAKTHROUGH_PID" > .pids/breakthrough.pid
echo "$PANOPTICON_PID" > .pids/panopticon.pid

echo ""
echo "✅ All services started!"
echo "Epistemic Filter: http://localhost:9002"
echo "Breakthrough Scanner: http://localhost:9003"
echo "Panopticon Logger: http://localhost:9004"
echo ""
echo "To stop services: ./stop_sensors.sh"
