#!/bin/bash

echo "🚀 Running Nano-Void Fusion Engine Test"
echo "=========================================="

# Change to the nano-void-fusion directory
cd /Users/lordwilson/nano-void-fusion

# Check Python and dependencies
echo "📋 Checking Python environment..."
python3 -c "import numpy; print('NumPy version:', numpy.__version__)"

# Show existing nano files
echo "
📁 Current nano files in ~/nano_memory:"
ls -la ~/nano_memory/*.nano

# Run the fusion engine
echo "
🌌 Running Nano-Void Fusion Engine..."
python3 src/nano_void.py

# Show results
echo "
📊 Nano files after fusion:"
ls -la ~/nano_memory/*.nano

echo "
✅ Test complete!"