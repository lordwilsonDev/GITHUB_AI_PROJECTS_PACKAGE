#!/bin/bash
cd "$(dirname "$0")"
echo "🚀 Starting Consciousness Loop..."
./consciousness_daemon.sh start &
sleep 2
./consciousness_daemon.sh status

