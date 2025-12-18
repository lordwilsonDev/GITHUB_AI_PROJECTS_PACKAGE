#!/bin/bash
# Phase 2: Orchestration and Deployment with Hybrid Model

set -e

PROJECT_DIR="$HOME/prefect-blueprint"
LOG_FILE="$PROJECT_DIR/execution.log"

cd "$PROJECT_DIR"
source .venv/bin/activate

echo "" | tee -a "$LOG_FILE"
echo "###################################################################" | tee -a "$LOG_FILE"
echo "# PHASE 2: Orchestration and Deployment with Hybrid Model" | tee -a "$LOG_FILE"
echo "###################################################################" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Task 2.1: Create Process Work Pool
echo "[2.1] Creating Process Work Pool..." | tee -a "$LOG_FILE"

# Check if work pool already exists
if prefect work-pool ls | grep -q "local-process-pool"; then
    echo "✓ Work pool 'local-process-pool' already exists" | tee -a "$LOG_FILE"
else
    prefect work-pool create "local-process-pool" --type process | tee -a "$LOG_FILE"
    echo "✓ Work pool created" | tee -a "$LOG_FILE"
fi

# Task 2.2: Verify work pool creation
echo "" | tee -a "$LOG_FILE"
echo "[2.2] Verifying work pool..." | tee -a "$LOG_FILE"
prefect work-pool ls | tee -a "$LOG_FILE"
echo "✓ Work pool verified" | tee -a "$LOG_FILE"

# Task 2.4: Verify prefect.yaml exists
echo "" | tee -a "$LOG_FILE"
echo "[2.4] Verifying prefect.yaml configuration..." | tee -a "$LOG_FILE"
if [ -f "prefect.yaml" ]; then
    echo "✓ prefect.yaml exists" | tee -a "$LOG_FILE"
    cat prefect.yaml | tee -a "$LOG_FILE"
else
    echo "✗ prefect.yaml not found!" | tee -a "$LOG_FILE"
    exit 1
fi

# Task 2.6: Deploy flow (non-interactive)
echo "" | tee -a "$LOG_FILE"
echo "[2.6] Deploying flow..." | tee -a "$LOG_FILE"
prefect deploy --all 2>&1 | tee -a "$LOG_FILE"
echo "✓ Flow deployed" | tee -a "$LOG_FILE"

# Task 2.7: Verify deployment
echo "" | tee -a "$LOG_FILE"
echo "[2.7] Verifying deployment..." | tee -a "$LOG_FILE"
prefect deployment ls | tee -a "$LOG_FILE"
echo "✓ Deployment verified" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "=================================================================" | tee -a "$LOG_FILE"
echo "PHASE 2 COMPLETE" | tee -a "$LOG_FILE"
echo "=================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "IMPORTANT: Next manual steps:" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "1. Open a NEW terminal window (Terminal C)" | tee -a "$LOG_FILE"
echo "   Run: cd ~/prefect-blueprint && source .venv/bin/activate && prefect worker start --pool local-process-pool" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "2. Wait for worker to start polling" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "3. Then run: ./phase3_execute.sh" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
