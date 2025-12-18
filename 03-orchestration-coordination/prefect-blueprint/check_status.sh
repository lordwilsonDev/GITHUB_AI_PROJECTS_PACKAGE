#!/bin/bash
# Status checker - Shows current state of all components

PROJECT_DIR="$HOME/prefect-blueprint"
cd "$PROJECT_DIR"

echo "================================================================="
echo "Prefect 3 Blueprint - System Status"
echo "================================================================="
echo ""

# Check virtual environment
echo "[Virtual Environment]"
if [ -d ".venv" ]; then
    echo "✓ Virtual environment exists"
    if [ -n "$VIRTUAL_ENV" ]; then
        echo "✓ Virtual environment is activated"
    else
        echo "⚠️  Virtual environment NOT activated"
        echo "  Run: source .venv/bin/activate"
    fi
else
    echo "✗ Virtual environment not found"
fi

echo ""
echo "[Prefect Server]"
if curl -s http://127.0.0.1:4200/api/health > /dev/null 2>&1; then
    echo "✓ Server is RUNNING"
    echo "  UI: http://127.0.0.1:4200"
    echo "  API: http://127.0.0.1:4200/api"
else
    echo "✗ Server is NOT running"
    echo "  Start with: prefect server start"
fi

echo ""
echo "[Work Pools]"
if [ -n "$VIRTUAL_ENV" ] || source .venv/bin/activate 2>/dev/null; then
    if prefect work-pool ls 2>/dev/null | grep -q "local-process-pool"; then
        echo "✓ Work pool 'local-process-pool' exists"
    else
        echo "✗ Work pool 'local-process-pool' not found"
        echo "  Create with: prefect work-pool create local-process-pool --type process"
    fi
fi

echo ""
echo "[Deployments]"
if [ -n "$VIRTUAL_ENV" ] || source .venv/bin/activate 2>/dev/null; then
    if prefect deployment ls 2>/dev/null | grep -q "production-etl"; then
        echo "✓ Deployment 'production-etl' exists"
        echo ""
        echo "Deployment Details:"
        prefect deployment inspect 'Enterprise Data Pipeline/production-etl' 2>/dev/null | head -n 20
    else
        echo "✗ Deployment 'production-etl' not found"
        echo "  Deploy with: prefect deploy --all"
    fi
fi

echo ""
echo "[Recent Flow Runs]"
if [ -n "$VIRTUAL_ENV" ] || source .venv/bin/activate 2>/dev/null; then
    prefect flow-run ls --limit 5 2>/dev/null || echo "No flow runs found"
fi

echo ""
echo "[Worker Status]"
echo "⚠️  Cannot automatically detect worker status"
echo "Check Terminal C for worker polling messages"
echo "Worker should show: 'Worker pool local-process-pool polling...'"

echo ""
echo "================================================================="
echo "Status Check Complete"
echo "================================================================="
echo ""
