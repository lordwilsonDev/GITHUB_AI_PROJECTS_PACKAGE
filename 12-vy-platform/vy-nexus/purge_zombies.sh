#!/bin/bash
echo "🔴 INITIATING SYSTEM PURGE..."

# 1. Kill the Headless Browsers (The Memory Hogs)
echo "   - Terminating Chrome Helpers..."
pkill -f "Google Chrome Helper"
pkill -f "VyChrome"

# 2. Kill the Old Pulse/Scheduler
echo "   - Terminating Old Python Schedulers..."
pkill -f "autonomous_scheduler.py"
pkill -f "vy_daemon.py"

# 3. Kill any lingering Ray processes
echo "   - Terminating Ray..."
pkill -f "ray"

# 4. Clear System Cache/Swap pressure (Requires Sudo, skips if no password provided)
echo "   - Attempting to sync filesystem..."
sync

echo "✅ PURGE COMPLETE. RAM should be recovering."
