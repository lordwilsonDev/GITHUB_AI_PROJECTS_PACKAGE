#!/bin/bash

echo "====================================="
echo "Verifying Patch Application"
echo "====================================="
echo ""

cd /Users/lordwilson/vy-nexus

echo "1. Checking Level10 files moved..."
if [ -d "modules/level10" ] && [ -f "modules/level10/agent_core.py" ]; then
    echo "   ✅ Level10 directory exists with files"
    ls -1 modules/level10/
else
    echo "   ❌ Level10 directory or files missing"
    exit 1
fi

echo ""
echo "2. Checking for output fixture..."
if grep -q "def output():" tests/test_micro_automation.py; then
    echo "   ✅ Output fixture found"
else
    echo "   ❌ Output fixture missing"
    exit 1
fi

echo ""
echo "3. Checking helper functions renamed..."
if grep -q "def success_func(" tests/test_micro_automation.py && \
   grep -q "def failure_func(" tests/test_micro_automation.py && \
   grep -q "def retry_func(" tests/test_micro_automation.py; then
    echo "   ✅ Helper functions renamed correctly"
else
    echo "   ❌ Helper functions not renamed"
    exit 1
fi

echo ""
echo "4. Checking for old function names (should not exist)..."
if grep -q "execute_func=test_success_func" tests/test_micro_automation.py || \
   grep -q "execute_func=test_failure_func" tests/test_micro_automation.py || \
   grep -q "execute_func=test_retry_func" tests/test_micro_automation.py; then
    echo "   ❌ Old function references still exist"
    exit 1
else
    echo "   ✅ All references updated"
fi

echo ""
echo "====================================="
echo "Patch Verification: SUCCESS"
echo "====================================="
echo ""
echo "Ready to run tests with:"
echo "  python3 -m pytest tests/test_micro_automation.py -v"
echo ""
