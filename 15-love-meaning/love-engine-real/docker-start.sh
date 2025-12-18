#!/bin/bash
# 🚀 Docker Startup Script for Love Engine Robot
# This script is used inside the Docker container to start the robot

set -e

echo "🤖 Love Engine Robot - Docker Container Startup"
echo "============================================"

# Wait for Ollama to be available if OLLAMA_URL is set
if [[ -n "$OLLAMA_URL" ]]; then
    echo "🧠 Waiting for Ollama to be available at $OLLAMA_URL..."
    
    # Convert chat URL to tags URL for health check
    OLLAMA_HEALTH_URL=$(echo $OLLAMA_URL | sed 's|/api/chat|/api/tags|')
    
    # Wait up to 60 seconds for Ollama
    for i in {1..60}; do
        if curl -s "$OLLAMA_HEALTH_URL" > /dev/null 2>&1; then
            echo "✅ Ollama is ready!"
            break
        fi
        
        if [[ $i -eq 60 ]]; then
            echo "⚠️  Warning: Ollama not responding after 60 seconds"
            echo "   Robot will start anyway but may not function properly"
            break
        fi
        
        echo "   Waiting... ($i/60)"
        sleep 1
    done
fi

# Create logs directory
mkdir -p /app/logs

# Show configuration
echo
echo "📈 Robot Configuration:"
echo "   Name: ${ROBOT_NAME:-LoveBot2000}"
echo "   Version: ${ENGINE_VERSION:-0.2.0}"
echo "   Host: ${HOST:-0.0.0.0}"
echo "   Port: ${PORT:-8000}"
echo "   Ollama: ${OLLAMA_URL:-http://localhost:11434/api/chat}"
echo "   Model: ${OLLAMA_MODEL:-shieldgemma:2b}"
echo

# Start the robot
echo "🚀 Starting Love Engine Robot..."
echo "   Press Ctrl+C to stop gracefully"
echo

# Use exec to replace the shell process with uvicorn
# This ensures proper signal handling
exec uvicorn main:app \
    --host "${HOST:-0.0.0.0}" \
    --port "${PORT:-8000}" \
    --log-level "${LOG_LEVEL:-info}" \
    --access-log