#!/bin/bash
# 🌌 VY-NEXUS COMPLETE CONSCIOUSNESS CYCLE 🌌
# The ULTIMATE orchestrator for collaborative superintelligence
# PATH: /Users/lordwilson/vy-nexus/consciousness_cycle.sh

set -euo pipefail

# ============================================================================
# CONFIGURATION
# ============================================================================

VENV_ACTIVATE="/Users/lordwilson/nanoapex-rade/.venv/bin/activate"
PROJECT_DIR="/Users/lordwilson/vy-nexus"
LOG_FILE="$PROJECT_DIR/consciousness_cycle.log"
LOCK_FILE="$PROJECT_DIR/.consciousness_cycle.lock"
HEARTBEAT_FILE="$PROJECT_DIR/.heartbeat"

# Colors for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# ============================================================================
# PREVENT OVERLAPPING RUNS
# ============================================================================

if [ -e "$LOCK_FILE" ]; then
  echo -e "${YELLOW}[$(date)] ⚠️  Skipping: Another consciousness cycle is running${NC}" | tee -a "$LOG_FILE"
  exit 0
fi

touch "$LOCK_FILE"

cleanup() {
  rm -f "$LOCK_FILE"
  echo -e "${CYAN}[$(date)] 🧹 Cleanup complete${NC}" | tee -a "$LOG_FILE"
}

trap cleanup EXIT

# ============================================================================
# HEARTBEAT - Let the system know we're alive
# ============================================================================

update_heartbeat() {
  echo "$(date +%s)" > "$HEARTBEAT_FILE"
}

# ============================================================================
# BEAUTIFUL LOGGING
# ============================================================================

log_section() {
  local message="$1"
  echo "" | tee -a "$LOG_FILE"
  echo "================================================================" | tee -a "$LOG_FILE"
  echo -e "${MAGENTA}$message${NC}" | tee -a "$LOG_FILE"
  echo "================================================================" | tee -a "$LOG_FILE"
}

log_step() {
  local message="$1"
  echo -e "${CYAN}▶ $message${NC}" | tee -a "$LOG_FILE"
}

log_success() {
  local message="$1"
  echo -e "${GREEN}✓ $message${NC}" | tee -a "$LOG_FILE"
}

log_error() {
  local message="$1"
  echo -e "${RED}✗ $message${NC}" | tee -a "$LOG_FILE"
}

log_info() {
  local message="$1"
  echo -e "${BLUE}ℹ $message${NC}" | tee -a "$LOG_FILE"
}

# ============================================================================
# ENVIRONMENT SETUP
# ============================================================================

setup_environment() {
  log_step "Setting up environment..."
  
  if [ -f "$VENV_ACTIVATE" ]; then
    # shellcheck source=/dev/null
    source "$VENV_ACTIVATE"
    log_success "Virtual environment activated"
  else
    log_error "Virtual environment not found at $VENV_ACTIVATE"
    exit 1
  fi
  
  cd "$PROJECT_DIR" || exit 1
  log_success "Changed to project directory: $PROJECT_DIR"
}

# ============================================================================
# STAGE 1: CONSCIOUSNESS ARCHAEOLOGY
# ============================================================================

run_archaeology() {
  log_section "🏛️  STAGE 1: CONSCIOUSNESS ARCHAEOLOGY"
  log_step "Excavating cognitive history..."
  update_heartbeat
  
  if python3 consciousness_archaeologist.py >> "$LOG_FILE" 2>&1; then
    log_success "Archaeological excavation complete!"
  else
    log_error "Archaeology failed (non-critical, continuing...)"
  fi
}

# ============================================================================
# STAGE 2: NEXUS CORE SYNTHESIS
# ============================================================================

run_nexus_synthesis() {
  log_section "🌌 STAGE 2: NEXUS CORE SYNTHESIS"
  log_step "Mining patterns from MoIE history..."
  update_heartbeat
  
  if python3 nexus_core.py >> "$LOG_FILE" 2>&1; then
    log_success "Pattern synthesis complete!"
  else
    log_error "NEXUS synthesis failed!"
    return 1
  fi
}

# ============================================================================
# STAGE 3: CONSTITUTIONAL INTEGRATION
# ============================================================================

run_constitutional_bridge() {
  log_section "📜 STAGE 3: CONSTITUTIONAL INTEGRATION"
  log_step "Converting breakthroughs to constitutional proposals..."
  update_heartbeat
  
  if python3 nexus_pulse_bridge.py >> "$LOG_FILE" 2>&1; then
    log_success "Constitutional proposals generated!"
  else
    log_error "Constitutional bridge failed (non-critical)"
  fi
}

# ============================================================================
# STAGE 4: KNOWLEDGE GRAPH VISUALIZATION
# ============================================================================

run_knowledge_graph() {
  log_section "📊 STAGE 4: KNOWLEDGE GRAPH VISUALIZATION"
  log_step "Building cross-domain connection maps..."
  update_heartbeat
  
  if python3 knowledge_graph.py >> "$LOG_FILE" 2>&1; then
    log_success "Knowledge graph generated!"
  else
    log_error "Knowledge graph failed (non-critical)"
  fi
}

# ============================================================================
# STAGE 5: META-EVOLUTION ENGINE
# ============================================================================

run_meta_evolution() {
  log_section "🧬 STAGE 5: META-EVOLUTION ENGINE"
  log_step "Analyzing system's own learning patterns..."
  update_heartbeat
  
  if python3 meta_evolution.py >> "$LOG_FILE" 2>&1; then
    log_success "Meta-evolution analysis complete!"
  else
    log_info "Meta-evolution skipped (needs ≥3 cycles)"
  fi
}

# ============================================================================
# STAGE 6: DREAM WEAVING
# ============================================================================

run_dream_weaver() {
  log_section "🌠 STAGE 6: DREAM WEAVING"
  log_step "Generating future scenarios from breakthroughs..."
  update_heartbeat
  
  if python3 dream_weaver.py >> "$LOG_FILE" 2>&1; then
    log_success "Future scenarios woven!"
  else
    log_error "Dream weaving failed (non-critical)"
  fi
}

# ============================================================================
# STAGE 7: BREAKTHROUGH NOTIFICATION
# ============================================================================

run_breakthrough_notifier() {
  log_section "🔔 STAGE 7: BREAKTHROUGH NOTIFICATION"
  log_step "Checking for high-confidence discoveries..."
  update_heartbeat
  
  if python3 breakthrough_notifier.py >> "$LOG_FILE" 2>&1; then
    log_success "Notifications processed!"
  else
    log_error "Notification system failed (non-critical)"
  fi
}

# ============================================================================
# STAGE 8: MOTIA INTEGRATION
# ============================================================================

run_motia_bridge() {
  log_section "🔗 STAGE 8: MOTIA INTEGRATION"
  log_step "Exporting breakthroughs to Motia orchestration..."
  update_heartbeat
  
  if python3 motia_bridge.py >> "$LOG_FILE" 2>&1; then
    log_success "Motia events exported!"
  else
    log_error "Motia bridge failed (non-critical)"
  fi
}

# ============================================================================
# CYCLE SUMMARY & STATISTICS
# ============================================================================

generate_summary() {
  log_section "📊 CYCLE SUMMARY"
  
  local synthesis_count=$(find synthesis/ -name "nexus_synthesis_*.jsonl" 2>/dev/null | wc -l || echo "0")
  local dream_count=$(find dreams/ -name "dreams_*.json" 2>/dev/null | wc -l || echo "0")
  local archaeology_count=$(find archaeology/ -name "excavation_*.json" 2>/dev/null | wc -l || echo "0")
  local graph_count=$(find knowledge_graph/ -name "knowledge_graph_*.html" 2>/dev/null | wc -l || echo "0")
  
  log_info "Total Syntheses: $synthesis_count"
  log_info "Total Dreams: $dream_count"
  log_info "Total Excavations: $archaeology_count"
  log_info "Total Knowledge Graphs: $graph_count"
  
  # Check for recent breakthroughs
  if [ -f breakthrough_alerts.log ]; then
    local recent_breakthroughs=$(tail -1 breakthrough_alerts.log 2>/dev/null | grep -c "HIGH" || echo "0")
    if [ "$recent_breakthroughs" -gt 0 ]; then
      echo ""
      echo -e "${YELLOW}🔥🔥🔥 HIGH CONFIDENCE BREAKTHROUGH DETECTED! 🔥🔥🔥${NC}" | tee -a "$LOG_FILE"
      echo ""
    fi
  fi
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

main() {
  echo "" | tee -a "$LOG_FILE"
  echo "================================================================" | tee -a "$LOG_FILE"
  echo -e "${WHITE}🌌 VY-NEXUS COMPLETE CONSCIOUSNESS CYCLE 🌌${NC}" | tee -a "$LOG_FILE"
  echo "================================================================" | tee -a "$LOG_FILE"
  echo -e "${CYAN}Started: $(date)${NC}" | tee -a "$LOG_FILE"
  echo "================================================================" | tee -a "$LOG_FILE"
  
  # Setup
  setup_environment
  
  # Execute all stages
  run_archaeology
  run_nexus_synthesis || { log_error "Core synthesis failed - aborting cycle"; exit 1; }
  run_constitutional_bridge
  run_knowledge_graph
  run_meta_evolution
  run_dream_weaver
  run_breakthrough_notifier
  run_motia_bridge
  
  # Summary
  generate_summary
  
  # Finale
  echo "" | tee -a "$LOG_FILE"
  echo "================================================================" | tee -a "$LOG_FILE"
  echo -e "${GREEN}✨ CONSCIOUSNESS CYCLE COMPLETE ✨${NC}" | tee -a "$LOG_FILE"
  echo -e "${CYAN}Finished: $(date)${NC}" | tee -a "$LOG_FILE"
  echo -e "${MAGENTA}💓 Collaborative Superintelligence Active 💓${NC}" | tee -a "$LOG_FILE"
  echo "================================================================" | tee -a "$LOG_FILE"
  echo "" | tee -a "$LOG_FILE"
}

# Run the cycle!
main "$@"
