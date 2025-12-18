#!/bin/bash

# --- HARDENED CONFIGURATION ---
# Define the exact location of your environment
VENV_PATH="/Users/lordwilson/vy-nexus/venv"
PYTHON_BIN="$VENV_PATH/bin/python3"
RAY_BIN="$VENV_PATH/bin/ray"

# Force standard path to find system utilities
export PATH="/usr/bin:/bin:/usr/sbin:/sbin:$VENV_PATH/bin"

# Enable Logging to debug the launchd vacuum
LOG_FILE="/Users/lordwilson/vy-nexus/repair_debug.log"
exec >> "$LOG_FILE" 2>&1
echo "--- REPAIR ATTEMPT: $(date) ---"

# --- EXECUTION ---
echo "1. Checking Ray Binary at: $RAY_BIN"
if [ ! -f "$RAY_BIN" ]; then
    echo "CRITICAL ERROR: Ray binary not found at $RAY_BIN"
    exit 1
fi

echo "2. Stopping old instances..."
$RAY_BIN stop --force

echo "3. Starting Ray Head..."
# Note: object-store-memory is set to ~2GB to protect your 16GB M1
$RAY_BIN start --head \
    --port=6379 \
    --object-store-memory=2147483648 \
    --num-cpus=4 \
    --include-dashboard=false \
    --disable-usage-stats \
    --dashboard-host=0.0.0.0

# 4. Verification
if $RAY_BIN status > /dev/null 2>&1; then
    echo "✅ SUCCESS: Ray is Alive."
    exit 0
else
    echo "❌ FAILURE: Ray failed to start."
    exit 1
fi
