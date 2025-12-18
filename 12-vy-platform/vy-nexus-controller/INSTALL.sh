#!/bin/bash
# VY-NEXUS Controller - Installation Script
# Builds and installs the app to /Applications

set -e

cd "$(dirname "$0")"

echo "📦 Installing VY-NEXUS Controller..."
echo ""

# Build first
echo "Step 1: Building app..."
./BUILD.sh

echo ""
echo "Step 2: Installing to /Applications..."

# Copy to Applications
APP_PATH="build/Build/Products/Release/VyNexusController.app"
if [ -d "$APP_PATH" ]; then
  sudo cp -R "$APP_PATH" /Applications/
  echo "✅ Installed to /Applications/VyNexusController.app"
else
  echo "❌ Build failed - app not found at $APP_PATH"
  exit 1
fi

echo ""
echo "🎉 Installation complete!"
echo ""
echo "To launch:"
echo "  open /Applications/VyNexusController.app"
echo ""
echo "Or find 'VY-NEXUS' in your Applications folder"
echo ""
