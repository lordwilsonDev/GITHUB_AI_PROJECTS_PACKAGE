#!/bin/bash

echo "Stopping existing Motia processes..."
# Kill any existing Motia processes
pkill -f "motia" 2>/dev/null
pkill -f "npx motia" 2>/dev/null

# Kill anything on port 3000
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "Waiting for processes to stop..."
sleep 2

echo "Starting Motia dev server..."
cd /Users/lordwilson/moie-mac-loop
npx motia dev
