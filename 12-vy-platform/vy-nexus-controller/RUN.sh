#!/bin/bash
# VY-NEXUS Controller - Quick Run Script
# Opens the app in Xcode and runs it

set -e

cd "$(dirname "$0")"

echo "🚀 Launching VY-NEXUS Controller in Xcode..."
echo ""

# Open in Xcode
open VyNexusController.xcodeproj

echo "✅ Xcode opened!"
echo ""
echo "Next steps:"
echo "  1. Press Cmd+R to build and run"
echo "  2. Or click the Play button in Xcode"
echo ""
echo "Make sure your backend is running:"
echo "  - Motia on port 3000"
echo "  - Love Engine on port 9001"
echo ""
