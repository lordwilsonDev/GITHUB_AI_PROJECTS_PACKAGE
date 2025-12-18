#!/bin/bash
# Prefect 3 Blueprint - Complete Execution Script
# This script guides you through all 3 phases

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================================================${NC}"
echo -e "${BLUE}  PREFECT 3 ORCHESTRATION BLUEPRINT - COMPLETE EXECUTION${NC}"
echo -e "${BLUE}=====================================================================${NC}"
echo ""

cd ~/prefect-blueprint

echo -e "${YELLOW}PHASE 1: LOCAL SETUP AND INITIAL CODE CONSTRUCTION${NC}"
echo ""

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "[1/6] Creating virtual environment..."
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

echo ""
echo "[2/6] Activating virtual environment..."
source .venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

echo ""
echo "[3/6] Installing/Updating Prefect 3..."
pip install -q -U prefect
echo -e "${GREEN}✓ Prefect 3 installed${NC}"

echo ""
echo "[4/6] Validating installation..."
echo -e "${BLUE}----------------------------------------${NC}"
prefect version
echo -e "${BLUE}----------------------------------------${NC}"

echo ""
echo "[5/6] Configuring API URL..."
prefect config set PREFECT_API_URL="http://127.0.0.1:4200/api"
echo -e "${GREEN}✓ API URL configured${NC}"

echo ""
echo "[6/6] Verifying data_pipeline.py exists..."
if [ -f "data_pipeline.py" ]; then
    echo -e "${GREEN}✓ data_pipeline.py found${NC}"
    echo "  - Contains Pydantic V2 validation"
    echo "  - 3 tasks with retry logic"
    echo "  - Comprehensive logging"
else
    echo -e "${RED}✗ data_pipeline.py not found!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}=====================================================================${NC}"
echo -e "${GREEN}  PHASE 1 COMPLETE! ✓${NC}"
echo -e "${GREEN}=====================================================================${NC}"
echo ""

echo -e "${YELLOW}NEXT STEPS:${NC}"
echo ""
echo -e "${BLUE}Step 1: Start Prefect Server (Terminal B)${NC}"
echo "  Open a NEW terminal and run:"
echo -e "  ${GREEN}cd ~/prefect-blueprint && source .venv/bin/activate && prefect server start${NC}"
echo ""
echo -e "${BLUE}Step 2: Test Local Execution (This Terminal)${NC}"
echo "  After server is running, execute:"
echo -e "  ${GREEN}python data_pipeline.py${NC}"
echo ""
echo -e "${BLUE}Step 3: Verify in UI${NC}"
echo "  Open browser to: http://127.0.0.1:4200/runs"
echo ""
echo -e "${YELLOW}After Phase 1 verification, proceed to Phase 2:${NC}"
echo "  Run: ./phase2_setup.sh"
echo ""
echo -e "${BLUE}=====================================================================${NC}"
