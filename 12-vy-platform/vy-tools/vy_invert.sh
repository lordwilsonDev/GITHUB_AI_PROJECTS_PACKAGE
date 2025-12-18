#!/usr/bin/env bash

# VY Inversion Bridge Script
# This script provides a stable interface to the MoIE Mac Loop
# Usage: vy_invert.sh [--domain=DOMAIN] [--axiom=AXIOM] [--mode=MODE]

# Set the path to the moie-mac-loop directory
MOIE_DIR="$HOME/moie-mac-loop"

# Check if the MoIE directory exists
if [ ! -d "$MOIE_DIR" ]; then
    echo "Error: MoIE Mac Loop directory not found at $MOIE_DIR"
    echo "Please ensure the moie-mac-loop directory exists in your home folder."
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed or not in PATH"
    echo "Please install Node.js to use the MoIE Mac Loop."
    exit 1
fi

# Change to the MoIE directory and run the inversion
cd "$MOIE_DIR" || {
    echo "Error: Could not change to MoIE directory"
    exit 1
}

# Pass all arguments to the Node.js script
echo "🔮 VY Bridge: Invoking MoIE Mac Loop..."
node index.js "$@"

# Check if the command was successful
if [ $? -eq 0 ]; then
    echo "✅ VY Bridge: Inversion completed successfully"
else
    echo "❌ VY Bridge: Inversion failed"
    exit 1
fi
