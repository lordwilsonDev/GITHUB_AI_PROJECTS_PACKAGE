#!/bin/bash
# Phase 1: Local Setup Script

cd ~/prefect-blueprint

# Initialize virtual environment
echo "Creating virtual environment..."
python3 -m venv .venv

# Activate and install Prefect
echo "Installing Prefect 3..."
source .venv/bin/activate
pip install -U prefect

# Validate installation
echo "\nValidating installation:"
prefect version

echo "\n=== Phase 1 Setup Complete ==="
echo "Next steps:"
echo "1. Start Prefect server: prefect server start"
echo "2. Configure API URL: prefect config set PREFECT_API_URL='http://127.0.0.1:4200/api'"
