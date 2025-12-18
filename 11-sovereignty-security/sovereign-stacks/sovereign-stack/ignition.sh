#!/bin/bash

echo "🔥 IGNITION SEQUENCE INITIATED"
echo "================================"

# Define the payload with BOTH goal and description
PAYLOAD='{
  "goal": "Build a Python web scraper that extracts article titles from Hacker News",
  "description": "System initialization test via ignition script",
  "priority": "high"
}'

echo ""
echo "📡 Sending goal to Brain..."
echo "Payload: $PAYLOAD"

# Send the request
RESPONSE=$(curl -s -X POST http://localhost:8000/api/plan \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

echo ""
echo "🧠 Brain Response:"
echo "$RESPONSE" | python3 -m json.tool

echo ""
echo "================================"
echo "✨ First spark fired!"
echo ""
echo "Monitor the system:"
echo "  - Brain logs: docker logs -f sovereign_brain"
echo "  - Heart logs: docker logs -f sovereign_heart"
