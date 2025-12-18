#!/bin/bash
# Quick analysis script for Sovereign Keep Protocol
# Usage: ./analyze.sh <path-to-takeout-keep-folder>

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Sovereign Keep Protocol - Quick Analyzer ===${NC}\n"

# Check if path provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No Takeout path provided${NC}"
    echo ""
    echo "Usage: ./analyze.sh <path-to-takeout-keep-folder>"
    echo "Example: ./analyze.sh ~/Downloads/Takeout/Keep"
    echo ""
    echo "Don't have a Takeout export yet?"
    echo "1. Go to https://takeout.google.com"
    echo "2. Select only 'Keep'"
    echo "3. Download and extract the archive"
    echo "4. Run this script with the path to the 'Keep' folder"
    exit 1
fi

TAKEOUT_PATH="$1"

# Check if path exists
if [ ! -d "$TAKEOUT_PATH" ]; then
    echo -e "${RED}Error: Directory not found: $TAKEOUT_PATH${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}\n"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Check if dependencies installed
if ! python -c "import sentence_transformers" 2>/dev/null; then
    echo -e "${YELLOW}Dependencies not installed. Installing (this will take 10-15 minutes)...${NC}"
    pip install -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}\n"
fi

# Run analysis
echo -e "${GREEN}Running semantic analysis...${NC}\n"
cd src
python standalone_analyzer.py "$TAKEOUT_PATH"

# Check if report was generated
if [ -f "../data/analysis_report.txt" ]; then
    echo -e "\n${GREEN}=== Analysis Complete! ===${NC}\n"
    echo "Reports generated:"
    echo "  📄 Text report: data/analysis_report.txt"
    echo "  📊 JSON data: data/analysis_results.json"
    echo ""
    echo "Opening report..."
    
    # Open report based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open ../data/analysis_report.txt
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open ../data/analysis_report.txt 2>/dev/null || cat ../data/analysis_report.txt
    else
        cat ../data/analysis_report.txt
    fi
else
    echo -e "${RED}Error: Report not generated${NC}"
    exit 1
fi
