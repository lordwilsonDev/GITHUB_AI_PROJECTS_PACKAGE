#!/bin/bash
# Install Prefect 3 and configure the environment

set -e

echo "=== Installing Prefect 3 ==="
cd ~/prefect-blueprint
source .venv/bin/activate

echo "Installing Prefect..."
pip install -U prefect

echo ""
echo "=== Validating Installation ==="
prefect version

echo ""
echo "=== Configuring API URL ==="
prefect config set PREFECT_API_URL='http://127.0.0.1:4200/api'

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Open a new terminal and run: cd ~/prefect-blueprint && source .venv/bin/activate && prefect server start"
echo "2. Wait for server to start, then continue with Phase 2"
