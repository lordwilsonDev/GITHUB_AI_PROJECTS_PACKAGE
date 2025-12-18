#!/bin/bash

# Level 33 Dashboard Launcher

echo "🚀 Starting Level 33 Dashboard..."
echo ""

# Check if uvicorn is installed
if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "📦 Installing required packages..."
    pip install fastapi uvicorn websockets psutil
    echo ""
fi

# Navigate to project directory
cd "$(dirname "$0")"

# Start the server
echo "🌐 Dashboard will be available at:"
echo "   http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 api/server.py
