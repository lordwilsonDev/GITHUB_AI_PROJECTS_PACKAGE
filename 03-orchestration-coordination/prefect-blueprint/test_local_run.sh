#!/bin/bash
# Test script - Runs data_pipeline.py locally without deployment
# This validates the code works before setting up infrastructure

set -e

PROJECT_DIR="$HOME/prefect-blueprint"
cd "$PROJECT_DIR"

echo "================================================================="
echo "Testing data_pipeline.py - Local Execution"
echo "================================================================="
echo ""

echo "[1/3] Activating virtual environment..."
source .venv/bin/activate
echo "✓ Virtual environment activated"

echo ""
echo "[2/3] Checking Prefect server connection..."
if curl -s http://127.0.0.1:4200/api/health > /dev/null 2>&1; then
    echo "✓ Prefect server is running"
else
    echo "✗ Prefect server is NOT running!"
    echo ""
    echo "Please start the server in a new terminal:"
    echo "  cd ~/prefect-blueprint"
    echo "  source .venv/bin/activate"
    echo "  prefect server start"
    echo ""
    exit 1
fi

echo ""
echo "[3/3] Running data_pipeline.py..."
echo "----------------------------------------------------------------"
python data_pipeline.py
echo "----------------------------------------------------------------"

echo ""
echo "================================================================="
echo "Test Complete!"
echo "================================================================="
echo ""
echo "Next steps:"
echo "1. Check the UI at http://127.0.0.1:4200/runs"
echo "2. You should see a flow run that just completed"
echo "3. Click on it to view logs and task details"
echo ""
echo "If successful, proceed with deployment:"
echo "  ./phase2_execute.sh"
echo ""
