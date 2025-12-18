#!/bin/bash
# Quick verification script
echo "Checking Prefect 3 Blueprint status..."
echo ""
echo "1. Checking if server is running..."
if pgrep -f "prefect server start" > /dev/null; then
    echo "   ✓ Server is running"
else
    echo "   ✗ Server is NOT running"
fi

echo "2. Checking if worker is running..."
if pgrep -f "prefect worker start" > /dev/null; then
    echo "   ✓ Worker is running"
else
    echo "   ✗ Worker is NOT running"
fi

echo "3. Checking UI accessibility..."
if curl -s http://127.0.0.1:4200/api/health > /dev/null 2>&1; then
    echo "   ✓ UI is accessible at http://127.0.0.1:4200"
else
    echo "   ✗ UI is NOT accessible"
fi

echo ""
echo "Quick commands:"
echo "  - View runs: prefect flow-run ls"
echo "  - View deployments: prefect deployment ls"
echo "  - Trigger run: prefect deployment run 'Enterprise Data Pipeline/production-etl'"
