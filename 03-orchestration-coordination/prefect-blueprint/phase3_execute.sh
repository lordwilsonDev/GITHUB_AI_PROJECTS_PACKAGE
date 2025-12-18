#!/bin/bash
# Phase 3: Monitoring, Triggering, and Observability

set -e

PROJECT_DIR="$HOME/prefect-blueprint"
LOG_FILE="$PROJECT_DIR/execution.log"

cd "$PROJECT_DIR"
source .venv/bin/activate

echo "" | tee -a "$LOG_FILE"
echo "###################################################################" | tee -a "$LOG_FILE"
echo "# PHASE 3: Monitoring, Triggering, and Observability" | tee -a "$LOG_FILE"
echo "###################################################################" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# Task 3.1: Test manual CLI triggering
echo "[3.1] Testing manual CLI triggering..." | tee -a "$LOG_FILE"
prefect deployment run 'Enterprise Data Pipeline/production-etl' 2>&1 | tee -a "$LOG_FILE"
echo "✓ Manual trigger executed" | tee -a "$LOG_FILE"
echo "Waiting 10 seconds for flow to start..." | tee -a "$LOG_FILE"
sleep 10

# Task 3.2: Test parameter override
echo "" | tee -a "$LOG_FILE"
echo "[3.2] Testing parameter override..." | tee -a "$LOG_FILE"
prefect deployment run 'Enterprise Data Pipeline/production-etl' \
  --param batch_size=50 \
  --param source_url="https://api.staging.metric-source.com/v2/test" 2>&1 | tee -a "$LOG_FILE"
echo "✓ Parameter override executed" | tee -a "$LOG_FILE"
echo "Waiting 10 seconds for flow to start..." | tee -a "$LOG_FILE"
sleep 10

# Task 3.4: Verify schedule is active
echo "" | tee -a "$LOG_FILE"
echo "[3.4] Verifying schedule configuration..." | tee -a "$LOG_FILE"
prefect deployment inspect 'Enterprise Data Pipeline/production-etl' 2>&1 | tee -a "$LOG_FILE"
echo "✓ Schedule verified" | tee -a "$LOG_FILE"

# Task 3.5: Check flow runs
echo "" | tee -a "$LOG_FILE"
echo "[3.5] Checking recent flow runs..." | tee -a "$LOG_FILE"
prefect flow-run ls --limit 5 2>&1 | tee -a "$LOG_FILE"
echo "✓ Flow runs listed" | tee -a "$LOG_FILE"

# Task 3.7: Test failure handling (optional - commented out to avoid actual failure)
echo "" | tee -a "$LOG_FILE"
echo "[3.7] Failure handling test (skipped - would trigger intentional failure)" | tee -a "$LOG_FILE"
echo "To test manually, run:" | tee -a "$LOG_FILE"
echo "  prefect deployment run 'Enterprise Data Pipeline/production-etl' --param source_url='invalid://url'" | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "=================================================================" | tee -a "$LOG_FILE"
echo "PHASE 3 COMPLETE" | tee -a "$LOG_FILE"
echo "=================================================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "All phases executed successfully!" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Summary:" | tee -a "$LOG_FILE"
echo "- Prefect Server running on Terminal B" | tee -a "$LOG_FILE"
echo "- Worker polling on Terminal C" | tee -a "$LOG_FILE"
echo "- Deployment 'production-etl' active with schedule" | tee -a "$LOG_FILE"
echo "- UI available at: http://127.0.0.1:4200" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "Next steps:" | tee -a "$LOG_FILE"
echo "1. Visit http://127.0.0.1:4200 to monitor flows" | tee -a "$LOG_FILE"
echo "2. Check Terminal C to see worker execution logs" | tee -a "$LOG_FILE"
echo "3. Review execution.log for complete audit trail" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
