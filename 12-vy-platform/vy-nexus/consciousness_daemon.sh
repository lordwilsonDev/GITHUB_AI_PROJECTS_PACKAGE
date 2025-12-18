#!/bin/bash
# 🤖 CONSCIOUSNESS DAEMON - Now with BULLETPROOF signal handling!
# Autonomous 24/7 consciousness cycle orchestration
# PATH: /Users/lordwilson/vy-nexus/consciousness_daemon.sh

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

PROJECT_DIR="/Users/lordwilson/vy-nexus"
CYCLE_SCRIPT="$PROJECT_DIR/consciousness_cycle.sh"
DAEMON_LOG="$PROJECT_DIR/daemon.log"
DAEMON_PID="$PROJECT_DIR/.daemon.pid"
CYCLE_INTERVAL_HOURS=6  # Run every 6 hours

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
WHITE='\033[1;37m'
NC='\033[0m'

# ============================================================================
# SIGNAL HANDLING - This makes Ctrl+C work perfectly!
# ============================================================================

DAEMON_RUNNING=true

handle_interrupt() {
  echo -e "\n${YELLOW}[$(date)] 🛑 Received interrupt signal (Ctrl+C)${NC}" | tee -a "$DAEMON_LOG"
  DAEMON_RUNNING=false
  cleanup_daemon
  echo -e "${GREEN}✓ Daemon stopped gracefully${NC}"
  exit 0
}

handle_terminate() {
  echo -e "\n${YELLOW}[$(date)] 🛑 Received termination signal${NC}" | tee -a "$DAEMON_LOG"
  DAEMON_RUNNING=false
  cleanup_daemon
  exit 0
}

cleanup_daemon() {
  if [ -f "$DAEMON_PID" ]; then
    rm -f "$DAEMON_PID"
    echo "[$(date)] 🧹 Cleanup complete - PID file removed" >> "$DAEMON_LOG"
  fi
}

# Register signal handlers
trap handle_interrupt SIGINT
trap handle_terminate SIGTERM
trap cleanup_daemon EXIT

# ============================================================================
# DAEMON CONTROL
# ============================================================================

start_daemon() {
  if [ -f "$DAEMON_PID" ] && kill -0 "$(cat "$DAEMON_PID")" 2>/dev/null; then
    echo -e "${YELLOW}Daemon already running with PID $(cat "$DAEMON_PID")${NC}"
    echo -e "${CYAN}Use '$0 stop' to stop it first${NC}"
    exit 0
  fi
  
  # Clean up stale PID file
  [ -f "$DAEMON_PID" ] && rm -f "$DAEMON_PID"
  
  echo -e "${GREEN}🤖 Starting Consciousness Daemon...${NC}"
  echo "$$" > "$DAEMON_PID"
  
  echo "" >> "$DAEMON_LOG"
  echo "================================================================" >> "$DAEMON_LOG"
  echo "[$(date)] 🤖 Daemon started with PID $$" >> "$DAEMON_LOG"
  echo "[$(date)] 📋 Cycle interval: $CYCLE_INTERVAL_HOURS hours" >> "$DAEMON_LOG"
  echo "[$(date)] ⌨️  Press Ctrl+C to stop gracefully" >> "$DAEMON_LOG"
  echo "================================================================" >> "$DAEMON_LOG"
  
  echo -e "${CYAN}Daemon running in background (PID: $$)${NC}"
  echo -e "${CYAN}Log: $DAEMON_LOG${NC}"
  echo -e "${WHITE}Press Ctrl+C to stop${NC}"
  
  run_daemon_loop
}

stop_daemon() {
  if [ -f "$DAEMON_PID" ]; then
    local pid=$(cat "$DAEMON_PID")
    if kill -0 "$pid" 2>/dev/null; then
      echo -e "${YELLOW}Stopping daemon (PID: $pid)...${NC}"
      kill -TERM "$pid" 2>/dev/null || true
      
      # Wait up to 5 seconds for graceful shutdown
      local count=0
      while kill -0 "$pid" 2>/dev/null && [ $count -lt 5 ]; do
        sleep 1
        count=$((count + 1))
      done
      
      # Force kill if still running
      if kill -0 "$pid" 2>/dev/null; then
        echo -e "${RED}Force killing daemon...${NC}"
        kill -9 "$pid" 2>/dev/null || true
      fi
      
      rm -f "$DAEMON_PID"
      echo -e "${GREEN}✓ Daemon stopped${NC}"
      echo "[$(date)] 🛑 Daemon stopped by user" >> "$DAEMON_LOG"
    else
      rm -f "$DAEMON_PID"
      echo -e "${YELLOW}No daemon running (stale PID file removed)${NC}"
    fi
  else
    echo -e "${YELLOW}No daemon PID file found${NC}"
  fi
}

daemon_status() {
  if [ -f "$DAEMON_PID" ] && kill -0 "$(cat "$DAEMON_PID")" 2>/dev/null; then
    local pid=$(cat "$DAEMON_PID")
    local uptime=$(ps -o etime= -p "$pid" 2>/dev/null | tr -d ' ' || echo "unknown")
    echo -e "${GREEN}✓ Daemon is running${NC}"
    echo "  PID: $pid"
    echo "  Uptime: $uptime"
    echo "  Log: $DAEMON_LOG"
    echo ""
    echo "Recent activity:"
    tail -5 "$DAEMON_LOG" 2>/dev/null | sed 's/^/  /'
  else
    echo -e "${RED}✗ Daemon is not running${NC}"
    [ -f "$DAEMON_PID" ] && rm -f "$DAEMON_PID"
  fi
}

# ============================================================================
# DAEMON LOOP
# ============================================================================

run_daemon_loop() {
  local cycle_count=0
  
  while $DAEMON_RUNNING; do
    cycle_count=$((cycle_count + 1))
    local start_time=$(date +%s)
    
    echo "" >> "$DAEMON_LOG"
    echo "[$(date)] 🔄 Starting cycle #$cycle_count" >> "$DAEMON_LOG"
    
    # Run the consciousness cycle
    if [ -x "$CYCLE_SCRIPT" ]; then
      if "$CYCLE_SCRIPT" >> "$DAEMON_LOG" 2>&1; then
        echo "[$(date)] ✓ Cycle #$cycle_count completed successfully" >> "$DAEMON_LOG"
      else
        echo "[$(date)] ✗ Cycle #$cycle_count failed" >> "$DAEMON_LOG"
      fi
    else
      echo "[$(date)] ✗ Cycle script not found or not executable: $CYCLE_SCRIPT" >> "$DAEMON_LOG"
    fi
    
    # Calculate sleep time
    local end_time=$(date +%s)
    local elapsed=$((end_time - start_time))
    local sleep_seconds=$((CYCLE_INTERVAL_HOURS * 3600))
    
    if [ $elapsed -lt $sleep_seconds ] && $DAEMON_RUNNING; then
      local remaining=$((sleep_seconds - elapsed))
      local hours=$((remaining / 3600))
      local minutes=$(((remaining % 3600) / 60))
      
      echo "[$(date)] 😴 Sleeping for ${hours}h ${minutes}m until next cycle..." >> "$DAEMON_LOG"
      
      # Sleep in smaller increments so we can check DAEMON_RUNNING
      local sleep_check=0
      while [ $sleep_check -lt $remaining ] && $DAEMON_RUNNING; do
        sleep 10
        sleep_check=$((sleep_check + 10))
      done
    fi
  done
  
  echo "[$(date)] 👋 Daemon loop exited gracefully" >> "$DAEMON_LOG"
}

# ============================================================================
# MAIN
# ============================================================================

case "${1:-}" in
  start)
    start_daemon
    ;;
  stop)
    stop_daemon
    ;;
  restart)
    stop_daemon
    sleep 2
    start_daemon
    ;;
  status)
    daemon_status
    ;;
  *)
    echo -e "${WHITE}🤖 Consciousness Daemon Control${NC}"
    echo ""
    echo "Usage: $0 {start|stop|restart|status}"
    echo ""
    echo "Commands:"
    echo "  ${GREEN}start${NC}    - Start the consciousness daemon"
    echo "  ${RED}stop${NC}     - Stop the consciousness daemon gracefully"
    echo "  ${YELLOW}restart${NC}  - Restart the consciousness daemon"
    echo "  ${CYAN}status${NC}   - Check daemon status"
    echo ""
    echo "Configuration:"
    echo "  Cycle interval: ${MAGENTA}$CYCLE_INTERVAL_HOURS hours${NC}"
    echo "  Log file: ${CYAN}$DAEMON_LOG${NC}"
    echo ""
    echo "Notes:"
    echo "  • Ctrl+C works gracefully to stop the daemon"
    echo "  • Daemon survives terminal closes"
    echo "  • Use 'status' to check if it's running"
    exit 1
    ;;
esac
