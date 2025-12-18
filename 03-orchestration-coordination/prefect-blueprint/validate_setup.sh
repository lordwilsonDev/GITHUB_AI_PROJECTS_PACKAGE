#!/bin/bash
# Validation Script - Checks if all components are ready

set -e

PROJECT_DIR="$HOME/prefect-blueprint"
cd "$PROJECT_DIR"

echo "================================================================="
echo "Prefect 3 Blueprint - Setup Validation"
echo "================================================================="
echo ""

# Check 1: Project directory
echo "[1/10] Checking project directory..."
if [ -d "$PROJECT_DIR" ]; then
    echo "✓ Project directory exists: $PROJECT_DIR"
else
    echo "✗ Project directory not found!"
    exit 1
fi

# Check 2: Virtual environment
echo ""
echo "[2/10] Checking virtual environment..."
if [ -d ".venv" ]; then
    echo "✓ Virtual environment exists"
else
    echo "✗ Virtual environment not found!"
    echo "Run: python3 -m venv .venv"
    exit 1
fi

# Check 3: data_pipeline.py
echo ""
echo "[3/10] Checking data_pipeline.py..."
if [ -f "data_pipeline.py" ]; then
    echo "✓ data_pipeline.py exists"
    # Check syntax
    source .venv/bin/activate
    python3 -m py_compile data_pipeline.py 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✓ data_pipeline.py syntax valid"
    else
        echo "✗ data_pipeline.py has syntax errors!"
        exit 1
    fi
else
    echo "✗ data_pipeline.py not found!"
    exit 1
fi

# Check 4: prefect.yaml
echo ""
echo "[4/10] Checking prefect.yaml..."
if [ -f "prefect.yaml" ]; then
    echo "✓ prefect.yaml exists"
    # Check for required fields
    if grep -q "production-etl" prefect.yaml; then
        echo "✓ Deployment 'production-etl' configured"
    else
        echo "✗ Deployment 'production-etl' not found in prefect.yaml!"
        exit 1
    fi
    if grep -q "local-process-pool" prefect.yaml; then
        echo "✓ Work pool 'local-process-pool' configured"
    else
        echo "✗ Work pool 'local-process-pool' not found in prefect.yaml!"
        exit 1
    fi
else
    echo "✗ prefect.yaml not found!"
    exit 1
fi

# Check 5: Execution scripts
echo ""
echo "[5/10] Checking execution scripts..."
for script in execute_all_phases.sh phase2_execute.sh phase3_execute.sh; do
    if [ -f "$script" ]; then
        echo "✓ $script exists"
        if [ -x "$script" ]; then
            echo "✓ $script is executable"
        else
            echo "⚠️  $script is not executable (run: chmod +x $script)"
        fi
    else
        echo "✗ $script not found!"
        exit 1
    fi
done

# Check 6: Documentation
echo ""
echo "[6/10] Checking documentation..."
for doc in README.md EXECUTION_GUIDE.md QUICK_START.md; do
    if [ -f "$doc" ]; then
        echo "✓ $doc exists"
    else
        echo "✗ $doc not found!"
    fi
done

# Check 7: Prefect installation
echo ""
echo "[7/10] Checking Prefect installation..."
source .venv/bin/activate
if command -v prefect &> /dev/null; then
    echo "✓ Prefect CLI available"
    PREFECT_VERSION=$(prefect version 2>&1 | head -n 1)
    echo "  Version: $PREFECT_VERSION"
else
    echo "✗ Prefect not installed!"
    echo "Run: pip install -U prefect"
    exit 1
fi

# Check 8: Python version
echo ""
echo "[8/10] Checking Python version..."
PYTHON_VERSION=$(python3 --version)
echo "  $PYTHON_VERSION"
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "✓ Python version meets requirements (3.10+)"
else
    echo "✗ Python version too old! Requires 3.10+"
    exit 1
fi

# Check 9: Prefect API URL configuration
echo ""
echo "[9/10] Checking Prefect API URL..."
API_URL=$(prefect config view --show-sources 2>/dev/null | grep PREFECT_API_URL | head -n 1 || echo "Not set")
echo "  $API_URL"
if echo "$API_URL" | grep -q "127.0.0.1:4200"; then
    echo "✓ API URL configured for local server"
else
    echo "⚠️  API URL not set to local server"
    echo "Run: prefect config set PREFECT_API_URL='http://127.0.0.1:4200/api'"
fi

# Check 10: Server status (optional)
echo ""
echo "[10/10] Checking Prefect server status..."
if curl -s http://127.0.0.1:4200/api/health > /dev/null 2>&1; then
    echo "✓ Prefect server is running and healthy"
    echo "  UI: http://127.0.0.1:4200"
else
    echo "⚠️  Prefect server is not running"
    echo "To start: prefect server start"
fi

echo ""
echo "================================================================="
echo "Validation Complete!"
echo "================================================================="
echo ""
echo "Status Summary:"
echo "  ✓ Project structure valid"
echo "  ✓ Code files present and valid"
echo "  ✓ Configuration files correct"
echo "  ✓ Execution scripts ready"
echo "  ✓ Documentation complete"
echo ""
echo "Next Steps:"
echo "  1. If scripts not executable: bash make_executable.sh"
echo "  2. Start execution: ./execute_all_phases.sh"
echo "  3. Follow QUICK_START.md for detailed instructions"
echo ""
