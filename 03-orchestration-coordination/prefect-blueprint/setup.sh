#!/bin/bash
# Prefect 3 Blueprint - Setup Script
# Phase 1: Local Setup and Initial Code Construction

set -e  # Exit on error

echo "=== Prefect 3 Blueprint Setup ==="
echo "Phase 1: Local Setup and Initial Code Construction"
echo ""

# Step 1: Create project directory
echo "[1/8] Creating project directory..."
mkdir -p ~/prefect-blueprint
cd ~/prefect-blueprint

# Step 2: Initialize virtual environment
echo "[2/8] Initializing virtual environment..."
python3 -m venv .venv

# Step 3: Activate virtual environment and install Prefect
echo "[3/8] Installing Prefect 3..."
source .venv/bin/activate
pip install -U prefect

# Step 4: Validate installation
echo "[4/8] Validating installation..."
prefect version

echo ""
echo "✓ Setup complete!"
echo "Next steps:"
echo "1. Activate the virtual environment: source ~/prefect-blueprint/.venv/bin/activate"
echo "2. Start the Prefect server in a new terminal: prefect server start"
echo "3. Configure API URL: prefect config set PREFECT_API_URL='http://127.0.0.1:4200/api'"
