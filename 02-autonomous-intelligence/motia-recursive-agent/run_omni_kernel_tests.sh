#!/bin/bash

echo "Running Omni-Kernel Tests..."
echo "=============================="

# Navigate to project directory
cd /Users/lordwilson/motia-recursive-agent

# Check if test file exists
if [ ! -f "tests/omni-kernel.step.test.ts" ]; then
    echo "❌ Test file not found: tests/omni-kernel.step.test.ts"
    exit 1
fi

# Check if implementation file exists
if [ ! -f "steps/omni-kernel.step.ts" ]; then
    echo "❌ Implementation file not found: steps/omni-kernel.step.ts"
    exit 1
fi

echo "✅ Files found - running tests..."

# Run the specific test
npm test -- omni-kernel.step.test.ts

echo ""
echo "Test execution completed."