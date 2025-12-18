#!/bin/bash
# VY-NEXUS Controller - Complete Deployment Script
# One command to rule them all

set -e

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🚀 VY-NEXUS CONTROLLER - COMPLETE DEPLOYMENT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd "$(dirname "$0")"

# Make all scripts executable
echo "Step 1: Making scripts executable..."
chmod +x *.sh
echo "  ✅ Done"
echo ""

# Check backend status
echo "Step 2: Checking backend services..."
if ./CHECK_BACKEND.sh 2>/dev/null; then
  echo "  ✅ Backend is running"
else
  echo "  ⚠️  Backend is not running"
  echo ""
  read -p "Start backend services now? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./START_BACKEND.sh
    echo "Waiting 10 seconds for services to start..."
    sleep 10
  else
    echo "⚠️  Skipping backend startup. App may not work without it."
  fi
fi
echo ""

# Build the app
echo "Step 3: Building VY-NEXUS Controller..."
./BUILD.sh
echo ""

# Install to Applications
echo "Step 4: Installing to /Applications..."
read -p "Install to /Applications? (requires sudo) (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  ./INSTALL.sh
else
  echo "  ⚠️  Skipping installation. You can run from build directory."
fi
echo ""

# Final status
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🎉 DEPLOYMENT COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To launch VY-NEXUS Controller:"
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo "  open /Applications/VyNexusController.app"
else
  echo "  open build/Build/Products/Release/VyNexusController.app"
fi
echo ""
echo "Or open in Xcode:"
echo "  ./RUN.sh"
echo ""
echo "🚀 THE COCKPIT IS READY. TIME TO FLY. 🚀"
echo ""
