#!/bin/bash
# VY-NEXUS Controller - Backend Startup Script
# Starts both Motia and Love Engine in separate terminals

set -e

echo "🚀 Starting VY-NEXUS Backend Services..."
echo ""

# Check if Motia directory exists
if [ ! -d "$HOME/motia-recursive-agent" ]; then
  echo "❌ Motia directory not found at ~/motia-recursive-agent"
  echo "   Please update the path in this script."
  exit 1
fi

# Check if Love Engine directory exists
if [ ! -d "$HOME/love-engine-zfc" ]; then
  echo "❌ Love Engine directory not found at ~/love-engine-zfc"
  echo "   Please update the path in this script."
  exit 1
fi

echo "Starting Motia Recursive Agent (port 3000)..."
osascript -e 'tell application "Terminal" to do script "cd ~/motia-recursive-agent && npm start"'

echo "Starting Love Engine (port 9001)..."
osascript -e 'tell application "Terminal" to do script "cd ~/love-engine-zfc && python3 server.py"'

echo ""
echo "✅ Backend services starting in new Terminal windows!"
echo ""
echo "Wait 5-10 seconds for services to initialize, then run:"
echo "  ./CHECK_BACKEND.sh"
echo ""
