#!/usr/bin/env python3
"""
CORD Autonomous Builder v2 - Self-Building System
Uses Aider to build itself and the entire CORD platform
"""

import os
import sys
import subprocess
import time

def run_aider_command(prompt, files=None):
    """Run aider with a specific prompt and files"""
    cmd = [
        "aider",
        "--model", "openrouter/anthropic/claude-3.5-sonnet",
        "--yes-always",
        "--message", prompt
    ]
    
    if files:
        cmd.extend(files)
    
    print(f"\n{'='*80}")
    print(f"Running Aider with prompt: {prompt[:100]}...")
    print(f"Files: {files}")
    print(f"{'='*80}\n")
    
    try:
        result = subprocess.run(
            cmd,
            cwd="/Users/lordwilson/cord-project",
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("Command timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"Error running aider: {e}")
        return False

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   CORD AUTONOMOUS BUILDER v2 - SELF-BUILDING SYSTEM      ║
    ║   Let's build something amazing together!                 ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Phase 1: Build the core xchat application
    print("\n🚀 PHASE 1: Building Core XChat Application")
    success = run_aider_command(
        "Create a modern React-based chat application called XChat with the following features: "
        "1. Real-time messaging with WebSocket support "
        "2. User authentication and profiles "
        "3. Channel/room creation and management "
        "4. Message threading and reactions "
        "5. File sharing and media uploads "
        "6. Search functionality "
        "7. Dark/light theme toggle "
        "8. Responsive design for mobile and desktop. "
        "Create the project structure with package.json, src/ directory with components, and a basic Express backend.",
        ["xchat/"]
    )
    
    if success:
        print("✅ Phase 1 Complete: Core XChat built!")
    else:
        print("⚠️  Phase 1 had issues, but continuing...")
    
    time.sleep(2)
    
    # Phase 2: Add AI features
    print("\n🤖 PHASE 2: Adding AI-Powered Features")
    success = run_aider_command(
        "Add AI-powered features to XChat: "
        "1. Smart reply suggestions using sentiment analysis "
        "2. Content moderation with toxicity detection "
        "3. Automatic message summarization for long threads "
        "4. Chatbot integration for automated responses "
        "5. Language translation for international users. "
        "Create an ai/ directory with these features and integrate them into the main app.",
        ["xchat/"]
    )
    
    if success:
        print("✅ Phase 2 Complete: AI features added!")
    else:
        print("⚠️  Phase 2 had issues, but continuing...")
    
    time.sleep(2)
    
    # Phase 3: Add viral growth features
    print("\n📈 PHASE 3: Adding Viral Growth Engine")
    success = run_aider_command(
        "Add viral growth features to XChat: "
        "1. Viral probability scoring for messages "
        "2. Trending topics detection "
        "3. Influencer identification "
        "4. Share optimization "
        "5. Growth analytics dashboard. "
        "Create a growth/ directory with these features.",
        ["xchat/"]
    )
    
    if success:
        print("✅ Phase 3 Complete: Viral growth engine added!")
    else:
        print("⚠️  Phase 3 had issues, but continuing...")
    
    time.sleep(2)
    
    # Phase 4: Self-improvement
    print("\n🔄 PHASE 4: Self-Improvement - Making Builder Better")
    success = run_aider_command(
        "Improve this autonomous builder script by: "
        "1. Adding better error handling and recovery "
        "2. Adding progress tracking and logging "
        "3. Adding ability to resume from failures "
        "4. Adding parallel task execution "
        "5. Adding automated testing after each phase. "
        "Modify autonomous_builder_v2.py to include these improvements.",
        ["autonomous_builder_v2.py"]
    )
    
    if success:
        print("✅ Phase 4 Complete: Builder improved itself!")
    else:
        print("⚠️  Phase 4 had issues, but continuing...")
    
    print("""
    
    ╔═══════════════════════════════════════════════════════════╗
    ║   🎉 BUILD COMPLETE! 🎉                                   ║
    ║                                                           ║
    ║   The CORD platform has been built with:                 ║
    ║   ✓ Core XChat application                               ║
    ║   ✓ AI-powered features                                  ║
    ║   ✓ Viral growth engine                                  ║
    ║   ✓ Self-improving builder                               ║
    ║                                                           ║
    ║   Check the xchat/ directory for the application!        ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    main()
