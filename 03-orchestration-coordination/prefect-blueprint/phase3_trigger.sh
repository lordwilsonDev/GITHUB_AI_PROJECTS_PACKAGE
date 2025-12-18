#!/bin/bash
# Phase 3: Monitoring, Triggering, and Observability

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd ~/prefect-blueprint
source .venv/bin/activate

echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}  PHASE 3: MONITORING, TRIGGERING, AND OBSERVABILITY${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo ""

echo -e "${YELLOW}Test 1: Basic Manual Trigger${NC}"
echo "Triggering deployment with default parameters..."
prefect deployment run 'Enterprise Data Pipeline/production-etl'
echo -e "${GREEN}✓ Flow run created${NC}"
echo "Check Terminal C (Worker) for execution logs"
echo ""

read -p "Press Enter to continue to Test 2..."

echo ""
echo -e "${YELLOW}Test 2: Parameter Override${NC}"
echo "Triggering with custom batch_size and source_url..."
prefect deployment run 'Enterprise Data Pipeline/production-etl' \
  --param batch_size=50 \
  --param source_url="https://api.staging.metric-source.com/v2/test"
echo -e "${GREEN}✓ Flow run created with custom parameters${NC}"
echo ""

read -p "Press Enter to continue to Test 3..."

echo ""
echo -e "${YELLOW}Test 3: JSON Parameter Syntax${NC}"
echo "Triggering with JSON parameters..."
prefect deployment run 'Enterprise Data Pipeline/production-etl' \
  --params '{"batch_size": 200}'
echo -e "${GREEN}✓ Flow run created with JSON parameters${NC}"
echo ""

read -p "Press Enter to continue to Test 4 (Failure Test)..."

echo ""
echo -e "${YELLOW}Test 4: Failure Handling and Retry Mechanism${NC}"
echo "Triggering with invalid URL to test retry logic..."
prefect deployment run 'Enterprise Data Pipeline/production-etl' \
  --param source_url="invalid://url"
echo -e "${GREEN}✓ Flow run created (will fail and retry)${NC}"
echo "Watch Terminal C to see:"
echo "  1. Initial failure"
echo "  2. 2-second wait"
echo "  3. Retry attempts (up to 3)"
echo "  4. Final failure state"
echo ""

echo -e "${GREEN}=====================================================================${NC}"
echo -e "${GREEN}  PHASE 3 COMPLETE! ✓${NC}"
echo -e "${GREEN}=====================================================================${NC}"
echo ""

echo -e "${YELLOW}MONITORING CHECKLIST:${NC}"
echo "  ✓ Terminal A (Client): Shows run creation confirmations"
echo "  ✓ Terminal B (Server): Shows API requests"
echo "  ✓ Terminal C (Worker): Shows execution logs"
echo "  ✓ Browser UI: http://127.0.0.1:4200/runs"
echo ""

echo -e "${BLUE}OPTIONAL: Add Scheduling${NC}"
echo "To add a daily 9 AM schedule:"
echo "1. Edit prefect.yaml"
echo "2. Add under deployment:"
echo "     schedules:"
echo "       - cron: \"0 9 * * *\""
echo "         timezone: \"America/Chicago\""
echo "         active: true"
echo "3. Redeploy: prefect deploy --name production-etl --no-prompt"
echo ""

echo -e "${GREEN}ALL PHASES COMPLETE! Blueprint implementation successful! ✓${NC}"
echo ""
