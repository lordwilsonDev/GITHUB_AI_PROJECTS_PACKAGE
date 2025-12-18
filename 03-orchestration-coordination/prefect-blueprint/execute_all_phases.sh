#!/bin/bash
# Comprehensive Prefect 3 Blueprint Execution Script
# Executes all three phases systematically

set -e  # Exit on error

PROJECT_DIR="$HOME/prefect-blueprint"
LOG_FILE="$PROJECT_DIR/execution.log"

cd "$PROJECT_DIR"

echo "=================================================================" | tee -a "$LOG_FILE"
echo "Prefect 3 Blueprint - Comprehensive Execution" | tee -a "$LOG_FILE"
echo "Started: $(date)" | tee -a "$LOG_FILE"
echo "=================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# ============================================================================
# PHASE 1: Local Setup and Initial Code Construction
# ============================================================================
echo "" | tee -a "$LOG_FILE"
echo "###################################################################" | tee -a "$LOG_FILE"
echo "# PHASE 1: Local Setup and Initial Code Construction" | tee -a "$LOG_FILE"
echo "###################################################################" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Task 1.1-1.2: Virtual Environment
if [ ! -d ".venv" ]; then
    echo "[1.1-1.2] Creating virtual environment..." | tee -a "$LOG_FILE"
    python3 -m venv .venv
    echo "✓ Virtual environment created" | tee -a "$LOG_FILE"
else
    echo "[1.1-1.2] ✓ Virtual environment already exists" | tee -a "$LOG_FILE"
fi

# Activate virtual environment
source .venv/bin/activate

# Task 1.3: Install Prefect
echo "" | tee -a "$LOG_FILE"
echo "[1.3] Installing Prefect 3..." | tee -a "$LOG_FILE"
pip install -q -U prefect 2>&1 | tee -a "$LOG_FILE"
echo "✓ Prefect installed" | tee -a "$LOG_FILE"

# Task 1.4: Validate Installation
echo "" | tee -a "$LOG_FILE"
echo "[1.4] Validating Prefect installation..." | tee -a "$LOG_FILE"
prefect version | tee -a "$LOG_FILE"
echo "✓ Installation validated" | tee -a "$LOG_FILE"

# Task 1.6: Configure API URL
echo "" | tee -a "$LOG_FILE"
echo "[1.6] Configuring Prefect API URL..." | tee -a "$LOG_FILE"
prefect config set PREFECT_API_URL="http://127.0.0.1:4200/api" | tee -a "$LOG_FILE"
echo "✓ API URL configured" | tee -a "$LOG_FILE"

# Task 1.7: Verify data_pipeline.py exists
echo "" | tee -a "$LOG_FILE"
echo "[1.7] Verifying data_pipeline.py..." | tee -a "$LOG_FILE"
if [ -f "data_pipeline.py" ]; then
    echo "✓ data_pipeline.py exists" | tee -a "$LOG_FILE"
    # Validate Python syntax
    python3 -m py_compile data_pipeline.py
    echo "✓ data_pipeline.py syntax valid" | tee -a "$LOG_FILE"
else
    echo "✗ data_pipeline.py not found!" | tee -a "$LOG_FILE"
    exit 1
fi

echo "" | tee -a "$LOG_FILE"
echo "=================================================================" | tee -a "$LOG_FILE"
echo "PHASE 1 SETUP COMPLETE" | tee -a "$LOG_FILE"
echo "=================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "IMPORTANT: Manual steps required before continuing:" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "1. Open a NEW terminal window (Terminal B)" | tee -a "$LOG_FILE"
echo "   Run: cd ~/prefect-blueprint && source .venv/bin/activate && prefect server start" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "2. Wait for server to start (you'll see 'Uvicorn running on...')" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "3. Open browser to http://127.0.0.1:4200 to verify UI" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "4. Then run: ./phase2_execute.sh" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
