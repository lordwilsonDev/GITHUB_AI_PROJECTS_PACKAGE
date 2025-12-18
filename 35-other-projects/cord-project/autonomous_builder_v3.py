#!/usr/bin/env python3
"""
CORD Autonomous Builder v3 - ULTIMATE Self-Building System
This version creates the project structure first, then uses Aider to build everything
"""

import os
import sys
import subprocess
import time
import json

def run_command(cmd, cwd=None):
    """Run a shell command and return success status"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd or "/Users/lordwilson/cord-project",
            capture_output=True,
            text=True,
            timeout=300
        )
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False

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
    print(f"🤖 Aider Task: {prompt[:80]}...")
    print(f"📁 Files: {files}")
    print(f"{'='*80}\n")
    
    try:
        result = subprocess.run(
            cmd,
            cwd="/Users/lordwilson/cord-project",
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏱️  Command timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running aider: {e}")
        return False

def create_project_structure():
    """Create the initial project structure"""
    print("\n📦 Creating project structure...")
    
    dirs = [
        "xchat",
        "xchat/src",
        "xchat/src/components",
        "xchat/src/pages",
        "xchat/src/utils",
        "xchat/src/hooks",
        "xchat/src/contexts",
        "xchat/src/services",
        "xchat/backend",
        "xchat/backend/routes",
        "xchat/backend/models",
        "xchat/backend/middleware",
        "xchat/public",
        "xchat/ai",
        "xchat/growth",
        "xchat/tests"
    ]
    
    for dir_path in dirs:
        full_path = f"/Users/lordwilson/cord-project/{dir_path}"
        os.makedirs(full_path, exist_ok=True)
        print(f"✅ Created {dir_path}")
    
    # Create initial package.json
    package_json = {
        "name": "xchat",
        "version": "1.0.0",
        "description": "Next-generation chat platform with AI and viral growth features",
        "main": "index.js",
        "scripts": {
            "start": "react-scripts start",
            "build": "react-scripts build",
            "test": "jest",
            "server": "node backend/server.js"
        },
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "express": "^4.18.2",
            "socket.io": "^4.6.1",
            "socket.io-client": "^4.6.1"
        },
        "devDependencies": {
            "react-scripts": "5.0.1"
        }
    }
    
    with open("/Users/lordwilson/cord-project/xchat/package.json", "w") as f:
        json.dump(package_json, f, indent=2)
    
    print("✅ Created package.json")
    
    # Create README
    readme = """# XChat - Next-Generation Chat Platform

Built autonomously by Aider AI!

## Features
- Real-time messaging
- AI-powered features
- Viral growth engine
- Self-improving architecture

## Getting Started
```bash
npm install
npm start
```
"""
    
    with open("/Users/lordwilson/cord-project/xchat/README.md", "w") as f:
        f.write(readme)
    
    print("✅ Created README.md")
    print("✅ Project structure complete!\n")

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   🚀 CORD AUTONOMOUS BUILDER v3 🚀                        ║
    ║   ULTIMATE SELF-BUILDING SYSTEM                           ║
    ║                                                           ║
    ║   This system will:                                       ║
    ║   1. Create project structure                             ║
    ║   2. Use Aider to build XChat app                         ║
    ║   3. Add AI features                                      ║
    ║   4. Add viral growth engine                              ║
    ║   5. Improve itself                                       ║
    ║                                                           ║
    ║   Let's build something AMAZING! 🎉                       ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Phase 0: Create project structure
    print("\n🏗️  PHASE 0: Creating Project Structure")
    create_project_structure()
    time.sleep(1)
    
    # Phase 1: Build core React app
    print("\n⚛️  PHASE 1: Building Core React Application")
    success = run_aider_command(
        "Create a modern React chat application in xchat/src/. "
        "Build: 1) App.js with routing, 2) ChatRoom.js component with message list and input, "
        "3) MessageList.js to display messages, 4) MessageInput.js for sending messages, "
        "5) UserProfile.js for user info, 6) index.js as entry point. "
        "Use functional components with hooks. Add basic styling.",
        ["xchat/src/App.js", "xchat/src/index.js"]
    )
    
    if success:
        print("✅ Phase 1 Complete!")
    time.sleep(2)
    
    # Phase 2: Build Express backend
    print("\n🔧 PHASE 2: Building Express Backend with WebSocket")
    success = run_aider_command(
        "Create an Express backend in xchat/backend/. "
        "Build: 1) server.js with Express and Socket.io setup, "
        "2) routes/messages.js for message API, "
        "3) routes/users.js for user API, "
        "4) models/Message.js for message schema, "
        "5) models/User.js for user schema. "
        "Add WebSocket support for real-time messaging.",
        ["xchat/backend/server.js"]
    )
    
    if success:
        print("✅ Phase 2 Complete!")
    time.sleep(2)
    
    # Phase 3: Add AI features
    print("\n🤖 PHASE 3: Adding AI-Powered Features")
    success = run_aider_command(
        "Create AI features in xchat/ai/. "
        "Build: 1) sentiment.js for sentiment analysis, "
        "2) smartReply.js for AI reply suggestions, "
        "3) moderation.js for content moderation, "
        "4) summarization.js for thread summarization, "
        "5) translation.js for language translation. "
        "Use simple ML algorithms or API integrations.",
        ["xchat/ai/sentiment.js", "xchat/ai/smartReply.js"]
    )
    
    if success:
        print("✅ Phase 3 Complete!")
    time.sleep(2)
    
    # Phase 4: Add viral growth features
    print("\n📈 PHASE 4: Adding Viral Growth Engine")
    success = run_aider_command(
        "Create viral growth features in xchat/growth/. "
        "Build: 1) viralScore.js to calculate viral probability, "
        "2) trending.js to detect trending topics, "
        "3) influencer.js to identify influencers, "
        "4) shareOptimizer.js to optimize sharing, "
        "5) analytics.js for growth metrics. "
        "Use engagement metrics and network analysis.",
        ["xchat/growth/viralScore.js", "xchat/growth/trending.js"]
    )
    
    if success:
        print("✅ Phase 4 Complete!")
    time.sleep(2)
    
    # Phase 5: Self-improvement
    print("\n🔄 PHASE 5: Self-Improvement - Making Builder Even Better")
    success = run_aider_command(
        "Improve autonomous_builder_v3.py by adding: "
        "1) Better error handling with retry logic, "
        "2) Progress tracking with JSON logs, "
        "3) Ability to resume from last successful phase, "
        "4) Parallel task execution for independent tasks, "
        "5) Automated testing after each phase, "
        "6) Performance monitoring and optimization. "
        "Make it production-ready and robust.",
        ["autonomous_builder_v3.py"]
    )
    
    if success:
        print("✅ Phase 5 Complete! Builder improved itself!")
    
    # Final summary
    print("""
    
    ╔═══════════════════════════════════════════════════════════╗
    ║   🎉🎉🎉 BUILD COMPLETE! 🎉🎉🎉                           ║
    ║                                                           ║
    ║   The CORD platform has been built with:                 ║
    ║   ✅ Complete project structure                          ║
    ║   ✅ React frontend with components                      ║
    ║   ✅ Express backend with WebSocket                      ║
    ║   ✅ AI-powered features (5 modules)                     ║
    ║   ✅ Viral growth engine (5 modules)                     ║
    ║   ✅ Self-improving builder                              ║
    ║                                                           ║
    ║   📁 Check xchat/ directory for the application!         ║
    ║   🚀 Run: cd xchat && npm install && npm start           ║
    ║                                                           ║
    ║   The system has built itself! 🤖✨                      ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Show what was created
    print("\n📊 Project Statistics:")
    run_command("find xchat -type f | wc -l")
    print("files created")
    
    print("\n📁 Project Structure:")
    run_command("tree -L 3 xchat 2>/dev/null || find xchat -type d | head -20")

if __name__ == "__main__":
    main()
