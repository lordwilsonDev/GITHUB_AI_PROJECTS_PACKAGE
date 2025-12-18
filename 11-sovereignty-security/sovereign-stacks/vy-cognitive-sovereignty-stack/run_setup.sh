#!/bin/bash

# Run the setup script and log output
cd /Users/lordwilson/vy-cognitive-sovereignty-stack

echo "Starting setup script execution..."
echo "Time: $(date)"
echo "---"

python3 setup_repository.py 2>&1 | tee setup_execution.log

echo "---"
echo "Setup script completed at: $(date)"
echo "Exit code: $?"
