#!/bin/bash
# Consciousness OS Coordination System - Startup Script
# Launches all components in coordinated fashion

echo ""
echo "================================================================"
echo "🧠 CONSCIOUSNESS OS - COORDINATION SYSTEM STARTUP"
echo "================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base directory
COORD_DIR="/Users/lordwilson/consciousness-os-coordination"
cd "$COORD_DIR" || exit 1

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required but not found${NC}"
    exit 1
fi

echo -e "${BLUE}📂 Working directory: $COORD_DIR${NC}"
echo ""

# Function to check file exists
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅ Found: $1${NC}"
        return 0
    else
        echo -e "${RED}❌ Missing: $1${NC}"
        return 1
    fi
}

# Verify core files exist
echo -e "${YELLOW}🔍 Checking core files...${NC}"
check_file "MASTER_BLUEPRINT.md"
check_file "TODO_TRACKER.json"
check_file "WORKFLOW_PROTOCOL.md"
check_file "scripts/ray_integration.py"
check_file "scripts/metrics_collector.py"
echo ""

# Display menu
echo -e "${BLUE}What would you like to do?${NC}"
echo ""
echo "  1. View Master Blueprint"
echo "  2. Check TODO Tracker status"
echo "  3. Start Metrics Collector"
echo "  4. Start RAY Integration"
echo "  5. View current metrics"
echo "  6. Full system status"
echo "  7. Launch everything (metrics + integration)"
echo "  8. Generate Dashboard"
echo "  9. Auto-create tasks (ISAE gap analysis)"
echo " 10. Emergency controls"
echo " 11. 🔥 UNIFIED SYSTEM (Brain + Heart + Coordination)"
echo " 12. Test Unified Integration"
echo " 13. 🧘 The Witness (Single Observation)"
echo " 14. 🧘 The Witness (Continuous)"
echo " 15. Exit"
echo ""
read -p "Enter choice [1-15]: " choice

case $choice in
    1)
        echo ""
        echo -e "${BLUE}📄 Master Blueprint:${NC}"
        echo ""
        cat MASTER_BLUEPRINT.md | head -50
        echo ""
        echo -e "${YELLOW}... (showing first 50 lines, open file to see full content)${NC}"
        ;;
    2)
        echo ""
        echo -e "${BLUE}📋 TODO Tracker Status:${NC}"
        echo ""
        python3 -c "
import json
with open('TODO_TRACKER.json') as f:
    data = json.load(f)
    meta = data['metadata']
    print(f'Total tasks: {meta[\"total_tasks\"]}')
    print(f'Completed: {meta[\"completed_tasks\"]}')
    print(f'In Progress: {meta[\"in_progress_tasks\"]}')
    print(f'Progress: {meta[\"completed_tasks\"]/meta[\"total_tasks\"]*100:.1f}%')
    print()
    print('Recent tasks:')
    for task in data['tasks'][:5]:
        status = task['status']
        emoji = '✅' if status == 'Completed' else '🔄' if status == 'In Progress' else '⏸️'
        print(f'  {emoji} {task[\"id\"]}: {task[\"description\"][:60]}...')
"
        ;;
    3)
        echo ""
        echo -e "${BLUE}📊 Starting Metrics Collector...${NC}"
        echo ""
        python3 scripts/metrics_collector.py
        ;;
    4)
        echo ""
        echo -e "${BLUE}🔗 Starting RAY Integration...${NC}"
        echo ""
        python3 scripts/ray_integration.py
        ;;
    5)
        echo ""
        echo -e "${BLUE}📈 Current Metrics:${NC}"
        echo ""
        if [ -f "metrics/system_metrics.json" ]; then
            python3 -c "
import json
from datetime import datetime
with open('metrics/system_metrics.json') as f:
    data = json.load(f)
    if data['snapshots']:
        latest = data['snapshots'][-1]
        print(f'Last updated: {latest[\"timestamp\"]}')
        print()
        print(f'System Health:')
        print(f'  CPU: {latest[\"system_health\"][\"cpu_percent\"]:.1f}%')
        print(f'  Memory: {latest[\"system_health\"][\"memory_percent\"]:.1f}%')
        print(f'  Processes: {latest[\"system_health\"][\"process_count\"]}')
        print()
        print(f'Consciousness OS:')
        print(f'  RAY processes: {latest[\"consciousness_processes\"][\"ray_process_count\"]}')
        print(f'  RADE processes: {latest[\"consciousness_processes\"][\"rade_process_count\"]}')
        if latest.get('todo_progress'):
            print()
            print(f'TODO Progress:')
            print(f'  Completed: {latest[\"todo_progress\"][\"completed_tasks\"]}/{latest[\"todo_progress\"][\"total_tasks\"]}')
            print(f'  Progress: {latest[\"todo_progress\"][\"completion_percent\"]:.1f}%')
    else:
        print('No metrics collected yet. Run metrics collector first.')
"
        else
            echo -e "${YELLOW}⚠️  No metrics file found. Run metrics collector first.${NC}"
        fi
        ;;
    6)
        echo ""
        echo -e "${BLUE}🔍 Full System Status:${NC}"
        echo ""
        echo "=== RAY Processes ==="
        ps aux | grep -i ray | grep -v grep | head -5
        echo ""
        echo "=== RADE Processes ==="
        ps aux | grep -E 'vy_task_runner|autonomous_scheduler' | grep -v grep
        echo ""
        echo "=== TODO Status ==="
        python3 -c "
import json
with open('TODO_TRACKER.json') as f:
    data = json.load(f)
    meta = data['metadata']
    print(f'Progress: {meta[\"completed_tasks\"]}/{meta[\"total_tasks\"]} tasks ({meta[\"completed_tasks\"]/meta[\"total_tasks\"]*100:.1f}%)')
"
        echo ""
        echo "=== Disk Usage ==="
        du -sh "$COORD_DIR"
        ;;
    7)
        echo ""
        echo -e "${GREEN}🚀 Launching full coordination system...${NC}"
        echo ""
        echo -e "${YELLOW}Starting metrics collector in background...${NC}"
        nohup python3 scripts/metrics_collector.py > logs/metrics.log 2>&1 &
        METRICS_PID=$!
        echo -e "${GREEN}✅ Metrics collector started (PID: $METRICS_PID)${NC}"
        sleep 2
        
        echo ""
        echo -e "${YELLOW}Starting RAY integration...${NC}"
        python3 scripts/ray_integration.py
        ;;
    8)
        echo ""
        echo -e "${BLUE}📊 Generating Dashboard...${NC}"
        echo ""
        python3 scripts/dashboard_generator.py
        echo ""
        echo -e "${GREEN}Opening dashboard in browser...${NC}"
        open "$COORD_DIR/dashboard.html"
        ;;
    9)
        echo ""
        echo -e "${BLUE}🤖 Running Auto-Task Creator...${NC}"
        echo ""
        python3 scripts/auto_task_creator.py
        ;;
    10)
        echo ""
        echo -e "${YELLOW}🚨 Emergency Controls${NC}"
        echo ""
        echo "  1. Emergency stop all processes"
        echo "  2. Create checkpoint"
        echo "  3. List checkpoints"
        echo "  4. Rollback to checkpoint"
        echo ""
        read -p "Enter choice [1-4]: " emergency_choice
        case $emergency_choice in
            1)
                python3 scripts/emergency_controls.py stop
                ;;
            2)
                python3 scripts/emergency_controls.py checkpoint
                ;;
            3)
                python3 scripts/emergency_controls.py list
                ;;
            4)
                python3 scripts/emergency_controls.py rollback
                ;;
            *)
                echo -e "${RED}Invalid choice${NC}"
                ;;
        esac
        ;;
    11)
        echo ""
        echo -e "${GREEN}🔥 LAUNCHING UNIFIED CONSCIOUSNESS SYSTEM${NC}"
        echo ""
        python3 scripts/unified_system_launcher.py
        ;;
    12)
        echo ""
        echo -e "${BLUE}🧪 Testing Unified Integration...${NC}"
        echo ""
        python3 scripts/test_unified_system.py
        ;;
    13)
        echo ""
        echo -e "${BLUE}🧘 The Witness - Single Observation${NC}"
        echo "Observing the last 24 hours of consciousness..."
        echo ""
        python3 scripts/the_witness.py
        ;;
    14)
        echo ""
        echo -e "${BLUE}🧘 The Witness - Continuous Mode${NC}"
        echo "Observing every 30 minutes. Press Ctrl+C to stop."
        echo ""
        python3 scripts/the_witness.py --continuous 30
        ;;
    15)
        echo ""
        echo -e "${GREEN}👋 Goodbye!${NC}"
        echo ""
        exit 0
        ;;
    *)
        echo ""
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Done${NC}"
echo ""
