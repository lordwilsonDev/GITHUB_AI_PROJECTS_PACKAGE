#!/bin/bash
# VY SOVEREIGNTY COMMAND CENTER - Startup Script

echo "🔮 Starting VY Sovereignty Command Center..."

# Check if requirements are installed
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing requirements..."
    pip3 install -r requirements.txt --break-system-packages
fi

# Start the backend server
echo "🚀 Starting backend on http://localhost:8888..."
python3 backend.py &
BACKEND_PID=$!

# Wait for server to start
sleep 3

# Open in browser
echo "🌐 Opening Command Center in browser..."
open http://localhost:8888/index.html || xdg-open http://localhost:8888/index.html

echo ""
echo "✅ VY Sovereignty Command Center is LIVE!"
echo ""
echo "   🔗 URL: http://localhost:8888"
echo "   📊 Dashboard: Real-time monitoring"
echo "   🎮 Controls: Start/Stop/Restart systems"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Wait for Ctrl+C
trap "kill $BACKEND_PID; echo ''; echo '🛑 Command Center stopped.'; exit 0" INT
wait $BACKEND_PID
