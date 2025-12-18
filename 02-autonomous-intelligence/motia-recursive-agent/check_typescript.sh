#!/bin/bash

echo "Checking TypeScript compilation for Omni-Kernel..."
echo "================================================"

# Navigate to project directory
cd /Users/lordwilson/motia-recursive-agent

# Check if TypeScript is available
if ! command -v npx &> /dev/null; then
    echo "❌ npx not found"
    exit 1
fi

# Try to compile the omni-kernel step file
echo "Compiling omni-kernel.step.ts..."
npx tsc --noEmit steps/omni-kernel.step.ts

if [ $? -eq 0 ]; then
    echo "✅ TypeScript compilation successful for omni-kernel.step.ts"
else
    echo "❌ TypeScript compilation failed for omni-kernel.step.ts"
fi

# Try to compile the test file
echo ""
echo "Compiling omni-kernel.step.test.ts..."
npx tsc --noEmit tests/omni-kernel.step.test.ts

if [ $? -eq 0 ]; then
    echo "✅ TypeScript compilation successful for omni-kernel.step.test.ts"
else
    echo "❌ TypeScript compilation failed for omni-kernel.step.test.ts"
fi

echo ""
echo "TypeScript check completed."