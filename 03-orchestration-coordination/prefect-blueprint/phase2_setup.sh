#!/bin/bash
# Phase 2: Orchestration and Deployment

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd ~/prefect-blueprint
source .venv/bin/activate

echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}  PHASE 2: ORCHESTRATION AND DEPLOYMENT${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo ""

echo "[1/5] Creating Process Work Pool..."
prefect work-pool create "local-process-pool" --type process 2>/dev/null || echo "Work pool already exists"
echo -e "${GREEN}✓ Work pool ready${NC}"

echo ""
echo "[2/5] Verifying work pool..."
echo -e "${BLUE}----------------------------------------${NC}"
prefect work-pool ls
echo -e "${BLUE}----------------------------------------${NC}"

echo ""
echo "[3/5] Initializing Prefect project..."
if [ ! -f "prefect.yaml" ]; then
    prefect init --recipe local
    echo -e "${GREEN}✓ Project initialized${NC}"
else
    echo -e "${GREEN}✓ prefect.yaml already exists${NC}"
fi

echo ""
echo "[4/5] Checking prefect.yaml configuration..."
if grep -q "local-process-pool" prefect.yaml; then
    echo -e "${GREEN}✓ prefect.yaml configured correctly${NC}"
else
    echo -e "${YELLOW}! prefect.yaml may need manual configuration${NC}"
    echo "  Ensure it contains:"
    echo "    - entrypoint: data_pipeline.py:data_pipeline"
    echo "    - work_pool name: local-process-pool"
fi

echo ""
echo "[5/5] Deploying the flow..."
prefect deploy --name production-etl --no-prompt
echo -e "${GREEN}✓ Deployment created${NC}"

echo ""
echo -e "${GREEN}=====================================================================${NC}"
echo -e "${GREEN}  PHASE 2 COMPLETE! ✓${NC}"
echo -e "${GREEN}=====================================================================${NC}"
echo ""

echo -e "${YELLOW}NEXT STEPS:${NC}"
echo ""
echo -e "${BLUE}Step 1: Start Worker (Terminal C)${NC}"
echo "  Open a NEW terminal and run:"
echo -e "  ${GREEN}cd ~/prefect-blueprint && source .venv/bin/activate && prefect worker start --pool \"local-process-pool\"${NC}"
echo ""
echo -e "${BLUE}Step 2: Verify Deployment${NC}"
echo "  Check UI at: http://127.0.0.1:4200/deployments"
echo ""
echo -e "${YELLOW}After Phase 2 verification, proceed to Phase 3:${NC}"
echo "  Run: ./phase3_trigger.sh"
echo ""
