#!/bin/bash
# VY-NEXUS Controller - Build Script
# Builds the macOS app from command line

set -e

echo "🏗️  Building VY-NEXUS Controller..."
echo ""

cd "$(dirname "$0")"

# Build the app
xcodebuild -project VyNexusController.xcodeproj \
  -scheme VyNexusController \
  -configuration Release \
  -derivedDataPath ./build \
  clean build

echo ""
echo "✅ Build complete!"
echo "📦 App location: build/Build/Products/Release/VyNexusController.app"
echo ""
echo "To run:"
echo "  open build/Build/Products/Release/VyNexusController.app"
echo ""
