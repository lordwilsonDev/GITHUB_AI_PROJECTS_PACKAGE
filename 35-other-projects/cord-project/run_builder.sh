#!/bin/bash

# CORD Autonomous Builder Runner
# This script runs the autonomous builder to build CORD using Aider

echo "========================================"
echo "🚀 CORD AUTONOMOUS BUILDER"
echo "========================================"
echo ""
echo "This will use Aider + Claude 3.5 Sonnet to:"
echo "  1. Build Viral Probability Engine"
echo "  2. Build AI Persona Mode"
echo "  3. Build Smart Reply Bot"
echo ""
echo "Watch as CORD builds itself! 🔥"
echo ""
echo "Press Ctrl+C to stop at any time"
echo "========================================"
echo ""

# Set up environment
export OPENROUTER_API_KEY="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"

# Run the builder
python3 autonomous_builder.py

echo ""
echo "========================================"
echo "🎉 Build complete!"
echo "========================================"
