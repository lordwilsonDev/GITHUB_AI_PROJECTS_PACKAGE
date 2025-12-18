#!/bin/bash
# Phase 1 Execution Script

set -e

echo "=== Phase 1: Local Setup and Initial Code Construction ==="
echo ""

cd ~/prefect-blueprint

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "[1/6] Creating virtual environment..."
    python3 -m venv .venv
else
    echo "[1/6] Virtual environment already exists"
fi

# Activate and install
echo "[2/6] Activating virtual environment and installing Prefect..."
source .venv/bin/activate
pip install -q -U prefect

# Validate installation
echo "[3/6] Validating Prefect installation..."
prefect version

echo ""
echo "[4/6] Configuring Prefect API URL..."
prefect config set PREFECT_API_URL="http://127.0.0.1:4200/api"

echo ""
echo "[5/6] Phase 1 setup complete!"
echo ""
echo "Next manual steps:"
echo "1. Open a new terminal and run: cd ~/prefect-blueprint && source .venv/bin/activate && prefect server start"
echo "2. After server starts, run: python data_pipeline.py"
echo "3. Visit http://127.0.0.1:4200 to view the UI"
