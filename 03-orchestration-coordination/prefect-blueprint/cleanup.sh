#!/bin/bash
# Cleanup script - Removes deployments and work pools (keeps code)

PROJECT_DIR="$HOME/prefect-blueprint"
cd "$PROJECT_DIR"

echo "================================================================="
echo "Prefect 3 Blueprint - Cleanup"
echo "================================================================="
echo ""

echo "This will remove:"
echo "  - Deployments"
echo "  - Work pools"
echo "  - Flow run history"
echo ""
echo "This will NOT remove:"
echo "  - Code files (data_pipeline.py, prefect.yaml)"
echo "  - Virtual environment"
echo "  - Documentation"
echo ""

read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

source .venv/bin/activate

echo ""
echo "[1/3] Removing deployment..."
if prefect deployment ls 2>/dev/null | grep -q "production-etl"; then
    prefect deployment delete 'Enterprise Data Pipeline/production-etl' --yes 2>/dev/null || true
    echo "✓ Deployment removed"
else
    echo "  No deployment to remove"
fi

echo ""
echo "[2/3] Removing work pool..."
if prefect work-pool ls 2>/dev/null | grep -q "local-process-pool"; then
    prefect work-pool delete 'local-process-pool' --yes 2>/dev/null || true
    echo "✓ Work pool removed"
else
    echo "  No work pool to remove"
fi

echo ""
echo "[3/3] Cleanup complete!"
echo ""
echo "To redeploy:"
echo "  ./phase2_execute.sh"
echo ""
