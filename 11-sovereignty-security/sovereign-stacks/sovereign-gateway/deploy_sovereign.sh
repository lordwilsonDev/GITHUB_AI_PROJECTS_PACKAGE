#!/bin/bash
#
# SCRIPT: deploy_sovereign.sh
# PURPOSE: Executes the complete, self-healing, robust deployment for the sovereign-gateway.
#
set -e # Exit immediately if a command exits with a non-zero status.

# --- Configuration Variables ---
GATEWAY_NAME="sovereign-gateway"
GATEWAY_BIN="./target/release/${GATEWAY_NAME}"
GATEWAY_PORT="8080"
GATEWAY_HOST="127.0.0.1" # Health check target
LOG_FILE="./deploy_log_$(date +%Y%m%d_%H%M%S).txt"

# Redirect all output to a log file and standard output
exec > >(tee -a "$LOG_FILE") 2>&1

echo "=========================================================="
echo "🚀 START: SOVEREIGN DEPLOYMENT (Self-Healing & Robust)"
echo "Timestamp: $(date)"
echo "=========================================================="

## LAYER 1: GENESIS BUILD - ENVIRONMENT AUDIT & HEALING

echo "### [L1: Genesis Build] 1. Environment Auditing & Healing (Fixing AddrInUse)..."

# 1.1. Check for Port Conflicts (Predictive Failure Analytics)
echo "1.1. Checking for lingering process on port ${GATEWAY_PORT}..."
CONFLICT_PID=$(sudo lsof -t -i :${GATEWAY_PORT} 2>/dev/null | head -1)

if [ -n "$CONFLICT_PID" ]; then
    echo "⚠️ WARNING: Port ${GATEWAY_PORT} is held by PID ${CONFLICT_PID}. Executing KILL -9."
    sudo kill -9 "$CONFLICT_PID"
    sleep 1
    if sudo lsof -t -i :${GATEWAY_PORT} &>/dev/null; then
        echo "✅ Port ${GATEWAY_PORT} successfully freed."
    else
        echo "❌ CRITICAL FAILURE: Failed to free port ${GATEWAY_PORT}. Exiting."
        exit 1
    fi
else
    echo "✅ Port ${GATEWAY_PORT} is free."
fi

# 1.2. Build the Rust Gateway (Fixing: hyphen vs. underscore bug)
echo "1.2. Compiling Rust Gateway (Target: ${GATEWAY_BIN})..."
# RUST_BACKTRACE=1 added for better error logging
RUST_BACKTRACE=1 cargo build --release --bin "$GATEWAY_NAME"

if [ ! -f "$GATEWAY_BIN" ]; then
    echo "❌ BUILD FAILURE: Expected binary not found at ${GATEWAY_BIN}."
    exit 1
fi
echo "✅ Rust Build Success. Binary path verified."

## PHASE 3: AUTONOMOUS DEPLOYMENT & HEALTH CHECK

echo "### [L3: Autonomous Deployment] 2. Executing Deployment and Health Check..."

# 2.1. Start Docker services (for browser/git containers)
echo "2.1. Bringing up Docker-Compose services..."
docker-compose up -d

# 2.2. Start the Gateway in the background
echo "2.2. Starting ${GATEWAY_NAME} in the background..."
nohup "$GATEWAY_BIN" > gateway_running.log 2>&1 &

GATEWAY_PID=$!
echo "Gateway started with PID: ${GATEWAY_PID}"

# 2.3. Wait and Health Check (Fixing: Network namespace issue by binding to 0.0.0.0 in code)
echo "2.3. Waiting for ${GATEWAY_NAME} to become healthy on ${GATEWAY_HOST}:${GATEWAY_PORT}..."
MAX_ATTEMPTS=15
HEALTH_SUCCESS=0

for i in $(seq 1 $MAX_ATTEMPTS); do
    sleep 2
    # The health check is now robust because the server binds to 0.0.0.0
    # We use a combined check: status code 200-299 (-f), silent (-s), and output status (-w)
    HEALTH_STATUS=$(curl -fsS -o /dev/null -w "%{http_code}" http://${GATEWAY_HOST}:${GATEWAY_PORT}/health 2>/dev/null)

    if [[ "$HEALTH_STATUS" -ge 200 && "$HEALTH_STATUS" -lt 300 ]]; then
        echo "✅ HEALTH CHECK SUCCESS (HTTP ${HEALTH_STATUS}) on attempt $i."
        HEALTH_SUCCESS=1
        break
    fi
done

# Final check block
if [ "$HEALTH_SUCCESS" -eq 0 ]; then
    echo "❌ FAILED: Health check failed after $MAX_ATTEMPTS attempts."
    echo "Attempting graceful shutdown and logging final state..."
    kill "$GATEWAY_PID" || true
    echo "--- LAST 20 LINES OF GATEWAY RUNNING LOG (PID ${GATEWAY_PID}) ---"
    tail -n 20 gateway_running.log
    echo "------------------------------------------------------------------"
    exit 1
fi

echo "=========================================================="
echo "✨ DEPLOYMENT COMPLETE & VERIFIED."
echo "Access Gateway Health: http://${GATEWAY_HOST}:${GATEWAY_PORT}/health"
echo "Metrics Endpoint: http://${GATEWAY_HOST}:${GATEWAY_PORT}/metrics"
echo "Full Deployment Log saved to: ${LOG_FILE}"
echo "=========================================================="
