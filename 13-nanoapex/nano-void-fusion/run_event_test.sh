#!/bin/bash

echo "🧪 Running Event System Integration Test"
echo "======================================"

# Change to nano-void-fusion directory
cd /Users/lordwilson/nano-void-fusion

# Check if Node.js is available
if command -v node &> /dev/null; then
    echo "✅ Node.js found"
    node test_event_system.js
else
    echo "❌ Node.js not found, running Python test instead"
    python3 direct_test.py
fi

echo "
📊 Final nano_memory status:"
ls -la ~/nano_memory/*.nano
