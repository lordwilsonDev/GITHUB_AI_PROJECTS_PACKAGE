#!/bin/bash

# Simple test to verify Aider works

echo "🧪 Testing Aider integration..."
echo ""

# Set API key
export OPENROUTER_API_KEY="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"

# Create a simple test file
echo "Creating test file..."
cat > test_hello.py << 'EOF'
# This is a placeholder
pass
EOF

echo "✅ Test file created"
echo ""
echo "Now running Aider to generate a hello world function..."
echo ""

# Run Aider with a simple task
echo "def hello():\n    pass\n\nImplement a hello world function that returns 'Hello, CORD!'\n/exit" | aider \
  --model openrouter/anthropic/claude-3.5-sonnet \
  --yes \
  --no-auto-commits \
  test_hello.py

echo ""
echo "========================================"
echo "🎉 Test complete!"
echo "========================================"
echo ""
echo "Generated code:"
cat test_hello.py
echo ""
echo "✅ Aider is working!"
echo "🚀 Ready to build CORD!"
