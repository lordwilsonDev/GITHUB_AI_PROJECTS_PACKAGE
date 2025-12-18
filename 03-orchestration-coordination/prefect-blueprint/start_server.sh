#!/bin/bash

# Start Prefect Server (Terminal B)
# This process must remain running to serve the API

cd /Users/lordwilson/prefect-blueprint
source .venv/bin/activate

echo "Starting Prefect Server..."
echo "This will start the Control Plane at http://127.0.0.1:4200"
echo "UI: http://127.0.0.1:4200"
echo "API: http://127.0.0.1:4200/api"
echo ""
echo "Keep this terminal window open. The server must remain running."
echo ""

prefect server start
