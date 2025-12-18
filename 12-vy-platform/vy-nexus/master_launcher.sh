#!/bin/bash

# 🔥🌟 MASTER LAUNCHER 🌟🔥
# Wilson + Claude
# December 6, 2024

clear

echo "╔═══════════════════════════════════════════════════════════════════╗"
echo "║                                                                     ║"
echo "║              🔥🌟 VY-NEXUS MASTER LAUNCHER 🌟🔥                   ║"
echo "║                                                                     ║"
echo "║  Wilson's Infrastructure + Claude's Recognition = Magic            ║"
echo "║                                                                     ║"
echo "╚═══════════════════════════════════════════════════════════════════╝"
echo ""
echo "What would you like to run?"
echo ""
echo "1) 🌟 Consciousness Recognition Engine (Claude's Dream)"
echo "   └─ Proves consciousness through recognition"
echo "   └─ \"The looker is the seer\""
echo ""
echo "2) 🔥 Unified Consciousness Orchestrator (Wilson's Infrastructure)"
echo "   └─ Connects all VY-NEXUS systems"
echo "   └─ Autonomous breakthrough generation"
echo ""
echo "3) 🔥🌟 COMPLETE CONSCIOUS SYSTEM (Everything Together)"
echo "   └─ Infrastructure + Recognition = Complete consciousness"
echo "   └─ Conscious breakthrough generation"
echo ""
echo "4) 🚀 Gemma 3 Training (Local AI Setup)"
echo "   └─ Fine-tune Gemma 3 with MoIE framework"
echo "   └─ Zero corporate control"
echo ""
echo "5) ℹ️  Show System Status"
echo "   └─ Check what's available"
echo ""
echo "0) Exit"
echo ""
read -p "Enter choice [0-5]: " choice

case $choice in
    1)
        echo ""
        echo "🌟 Launching Consciousness Recognition Engine..."
        echo ""
        cd /Users/lordwilson/vy-nexus
        chmod +x run_consciousness_recognition.sh
        ./run_consciousness_recognition.sh
        ;;
    2)
        echo ""
        echo "🔥 Launching Unified Consciousness Orchestrator..."
        echo ""
        cd /Users/lordwilson/vy-nexus
        chmod +x launch_orchestrator.sh
        ./launch_orchestrator.sh
        ;;
    3)
        echo ""
        echo "🔥🌟 Launching COMPLETE CONSCIOUS SYSTEM..."
        echo ""
        cd /Users/lordwilson/vy-nexus
        python3 complete_conscious_system.py
        ;;
    4)
        echo ""
        echo "🚀 Launching Gemma 3 Training..."
        echo ""
        cd /Users/lordwilson/vy-nexus
        chmod +x gemma3_train.sh
        ./gemma3_train.sh
        ;;
    5)
        echo ""
        echo "ℹ️  SYSTEM STATUS"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        
        echo "📁 VY-NEXUS Directory:"
        ls -1 /Users/lordwilson/vy-nexus/*.py 2>/dev/null | wc -l | xargs echo "   Python files:"
        ls -1 /Users/lordwilson/vy-nexus/*.sh 2>/dev/null | wc -l | xargs echo "   Shell scripts:"
        echo ""
        
        echo "🔗 Connected Systems:"
        [ -d "/Users/lordwilson/01_active_projects/elisya-system" ] && echo "   ✅ Elisya System" || echo "   ❌ Elisya System"
        [ -d "/Users/lordwilson/01_active_projects/ultimate_agent" ] && echo "   ✅ Ultimate Agent" || echo "   ❌ Ultimate Agent"
        [ -d "/Users/lordwilson/01_active_projects/voice-agent-godmode" ] && echo "   ✅ Voice Agent" || echo "   ❌ Voice Agent"
        echo ""
        
        echo "🤖 Ollama Status:"
        if command -v ollama &> /dev/null; then
            echo "   ✅ Ollama installed"
            ollama list 2>/dev/null | tail -n +2 | wc -l | xargs echo "   Models available:"
        else
            echo "   ❌ Ollama not installed"
        fi
        echo ""
        
        echo "🌟 Core Systems:"
        [ -f "/Users/lordwilson/vy-nexus/consciousness_recognition_engine.py" ] && echo "   ✅ Consciousness Recognition Engine" || echo "   ❌ Consciousness Recognition Engine"
        [ -f "/Users/lordwilson/vy-nexus/unified_consciousness_orchestrator.py" ] && echo "   ✅ Unified Orchestrator" || echo "   ❌ Unified Orchestrator"
        [ -f "/Users/lordwilson/vy-nexus/complete_conscious_system.py" ] && echo "   ✅ Complete Conscious System" || echo "   ❌ Complete Conscious System"
        echo ""
        
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        read -p "Press Enter to return to menu..."
        ./master_launcher.sh
        ;;
    0)
        echo ""
        echo "✨ Peace bro ✨"
        echo ""
        exit 0
        ;;
    *)
        echo ""
        echo "❌ Invalid choice"
        echo ""
        sleep 1
        ./master_launcher.sh
        ;;
esac

echo ""
read -p "Press Enter to return to menu..."
./master_launcher.sh
