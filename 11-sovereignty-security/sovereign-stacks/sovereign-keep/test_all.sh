#!/bin/bash
#
# Comprehensive Test Suite for Sovereign Keep Protocol
# Runs all tests: unit, property-based, fuzz, golden, accuracy, and benchmarks
#

set -e  # Exit on first error

COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_BLUE='\033[0;34m'
COLOR_RESET='\033[0m'

echo -e "${COLOR_BLUE}========================================${COLOR_RESET}"
echo -e "${COLOR_BLUE}Sovereign Keep Protocol - Test Suite${COLOR_RESET}"
echo -e "${COLOR_BLUE}========================================${COLOR_RESET}\n"

# Change to project directory
cd "$(dirname "$0")"

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo -e "${COLOR_RED}Error: Virtual environment not found${COLOR_RESET}"
    echo "Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate

# Install test dependencies if needed
echo -e "${COLOR_YELLOW}[1/9] Checking test dependencies...${COLOR_RESET}"
pip install -q pytest hypothesis pytest-cov 2>/dev/null || true
echo -e "${COLOR_GREEN}✓ Dependencies ready${COLOR_RESET}\n"

# 1. Lint/Static Checks (optional, skip if not installed)
echo -e "${COLOR_YELLOW}[2/9] Running static analysis...${COLOR_RESET}"
if command -v flake8 &> /dev/null; then
    flake8 src/ --max-line-length=120 --ignore=E501,W503 || echo "  (warnings only)"
    echo -e "${COLOR_GREEN}✓ Static analysis complete${COLOR_RESET}\n"
else
    echo -e "  Skipping (flake8 not installed)\n"
fi

# 2. Unit Tests
echo -e "${COLOR_YELLOW}[3/9] Running unit tests...${COLOR_RESET}"
pytest tests/test_semantic_analysis.py -v --tb=short
echo -e "${COLOR_GREEN}✓ Unit tests passed${COLOR_RESET}\n"

# 3. Property-Based Tests
echo -e "${COLOR_YELLOW}[4/9] Running property-based tests (Hypothesis)...${COLOR_RESET}"
pytest tests/test_property_based.py -v --tb=short -x
echo -e "${COLOR_GREEN}✓ Property tests passed${COLOR_RESET}\n"

# 4. Fuzz Tests
echo -e "${COLOR_YELLOW}[5/9] Running fuzz tests...${COLOR_RESET}"
pytest tests/test_fuzz.py -v --tb=short
echo -e "${COLOR_GREEN}✓ Fuzz tests passed${COLOR_RESET}\n"

# 5. Golden Tests
echo -e "${COLOR_YELLOW}[6/9] Running golden/regression tests...${COLOR_RESET}"
pytest tests/test_golden.py -v --tb=short
echo -e "${COLOR_GREEN}✓ Golden tests passed${COLOR_RESET}\n"

# 6. Accuracy Tests
echo -e "${COLOR_YELLOW}[7/9] Running accuracy tests (precision/recall)...${COLOR_RESET}"
pytest tests/test_accuracy.py -v --tb=short -s
echo -e "${COLOR_GREEN}✓ Accuracy tests passed${COLOR_RESET}\n"

# 7. Coverage Report
echo -e "${COLOR_YELLOW}[8/9] Generating coverage report...${COLOR_RESET}"
pytest tests/ --cov=src --cov-report=term-missing --cov-report=html -q
echo -e "${COLOR_GREEN}✓ Coverage report generated (see htmlcov/index.html)${COLOR_RESET}\n"

# 8. Benchmark (smoke test)
echo -e "${COLOR_YELLOW}[9/9] Running performance benchmark...${COLOR_RESET}"
if [ -f "tests/test_benchmark.py" ]; then
    pytest tests/test_benchmark.py -v --tb=short
    echo -e "${COLOR_GREEN}✓ Benchmark complete${COLOR_RESET}\n"
else
    echo -e "  Skipping (benchmark not implemented yet)\n"
fi

# Summary
echo -e "${COLOR_BLUE}========================================${COLOR_RESET}"
echo -e "${COLOR_GREEN}✓ ALL TESTS PASSED${COLOR_RESET}"
echo -e "${COLOR_BLUE}========================================${COLOR_RESET}\n"

echo "Test Results:"
echo "  • Unit tests: ✓"
echo "  • Property-based tests: ✓"
echo "  • Fuzz tests: ✓"
echo "  • Golden tests: ✓"
echo "  • Accuracy tests: ✓"
echo "  • Coverage report: htmlcov/index.html"
echo ""
echo "Next steps:"
echo "  1. Review coverage report: open htmlcov/index.html"
echo "  2. Check accuracy metrics in test output above"
echo "  3. Run on real data: ./analyze.sh ~/Downloads/Takeout/Keep"
echo ""
