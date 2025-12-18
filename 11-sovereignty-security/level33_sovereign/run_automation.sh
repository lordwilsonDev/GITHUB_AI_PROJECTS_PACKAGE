#!/bin/bash
# Level 33 Automation Launcher
# Quick access to all automations

set -e

cd "$(dirname "$0")"

echo ""
echo "🤖 LEVEL 33 AUTOMATION LAUNCHER"
echo "================================"
echo ""
echo "Available Automations:"
echo ""
echo "  1. Workspace Launcher    - Set up daily workspace"
echo "  2. File Organizer        - Clean up Downloads folder"
echo "  3. System Health Check   - Monitor system health"
echo "  4. Screenshot Documenter - Capture & organize screenshots"
echo "  5. Quick Note            - Rapid note creation"
echo ""
echo "  0. Exit"
echo ""

read -p "Select automation (0-5): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Launching Workspace..."
        python3 automations/workspace_launcher.py
        ;;
    2)
        echo ""
        echo "📦 File Organizer"
        echo "Run in dry-run mode first? (y/n)"
        read -p "> " dryrun
        if [ "$dryrun" = "y" ]; then
            python3 automations/file_organizer.py --dry-run
        else
            python3 automations/file_organizer.py
        fi
        ;;
    3)
        echo ""
        echo "🔍 Running System Health Check..."
        python3 automations/system_health_check.py
        ;;
    4)
        echo ""
        echo "📸 Screenshot Documenter"
        echo "Mode: (1) Single (2) Series (3) Interactive"
        read -p "> " mode
        
        read -p "Project name [General]: " project
        project=${project:-General}
        
        case $mode in
            1)
                python3 automations/screenshot_documenter.py --project "$project"
                ;;
            2)
                read -p "Number of screenshots: " count
                read -p "Interval (seconds): " interval
                python3 automations/screenshot_documenter.py --project "$project" --series --count $count --interval $interval
                ;;
            3)
                python3 automations/screenshot_documenter.py --project "$project" --interactive
                ;;
        esac
        ;;
    5)
        echo ""
        echo "📝 Quick Note"
        echo "Type: (1) General (2) Todo (3) Meeting (4) Idea (5) Bug (6) List (7) Search"
        read -p "> " notetype
        
        case $notetype in
            1)
                read -p "Note content: " content
                python3 automations/quick_note.py "$content"
                ;;
            2)
                read -p "Todo items (one per line, Ctrl+D when done): "
                content=$(cat)
                python3 automations/quick_note.py --type todo "$content"
                ;;
            3)
                read -p "Meeting topic: " content
                python3 automations/quick_note.py --type meeting "$content"
                ;;
            4)
                read -p "Idea: " content
                python3 automations/quick_note.py --type idea "$content"
                ;;
            5)
                read -p "Bug description: " content
                python3 automations/quick_note.py --type bug "$content"
                ;;
            6)
                python3 automations/quick_note.py --list
                ;;
            7)
                read -p "Search query: " query
                python3 automations/quick_note.py --search "$query"
                ;;
        esac
        ;;
    0)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"
echo ""
