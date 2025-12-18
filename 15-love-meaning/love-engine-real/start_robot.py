#!/usr/bin/env python3
# 🚀 Love Engine Robot Startup Script
"""
This script starts our super robot friend with all the right settings!

🤖 What this script does:
1. Checks if all robot parts are ready
2. Sets up the robot's environment
3. Starts the robot with proper configuration
4. Shows helpful status messages
5. Handles graceful shutdown
"""

import os
import sys
import time
import signal
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime
import httpx

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import uvicorn
    from config import get_settings
    from main import app
except ImportError as e:
    print(f"❌ Missing required packages: {e}")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

class RobotLauncher:
    """
    🚀 The Robot Launcher - Gets our robot friend ready for action!
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.robot_process = None
        self.shutdown_requested = False
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n👋 Received shutdown signal ({signum}). Saying goodbye...")
        self.shutdown_requested = True
    
    def print_banner(self):
        """Print a friendly startup banner"""
        print("" * 60)
        print("🤖 LOVE ENGINE ROBOT STARTUP 🚀")
        print("" * 60)
        print(f"🏷️  Robot Name: {self.settings.robot_name}")
        print(f"🔢 Version: {self.settings.engine_version}")
        print(f"🛡️  Safety: {self.settings.safety_version}")
        print(f"🧠 AI Model: {self.settings.ollama_model}")
        print(f"🌐 Server: {self.settings.host}:{self.settings.port}")
        print("" * 60)
        print(f"💬 {self.settings.get_description()}")
        print("" * 60)
    
    def check_prerequisites(self):
        """
        🔍 Check if all robot parts are ready
        """
        print("🔍 Checking robot systems...")
        
        issues = []
        
        # Check if required files exist
        required_files = [
            ".env",
            "config.py",
            "main.py",
            "safety_system.py",
            "validation_system.py",
            "energy_system.py",
            "error_handling.py"
        ]
        
        for file in required_files:
            if not Path(file).exists():
                issues.append(f"Missing file: {file}")
        
        # Check if logs directory exists (create if not)
        logs_dir = Path("logs")
        if not logs_dir.exists():
            print(f"📁 Creating logs directory...")
            logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Check Ollama connection
        print(f"🧠 Testing Ollama connection at {self.settings.ollama_url}...")
        ollama_ok = self._test_ollama_connection()
        
        if not ollama_ok:
            issues.append(
                f"Cannot connect to Ollama at {self.settings.ollama_url}. "
                f"Please make sure Ollama is running with model {self.settings.ollama_model}"
            )
        
        if issues:
            print("❌ Robot startup issues found:")
            for issue in issues:
                print(f"  • {issue}")
            
            print("\n🛠️  Quick fixes:")
            print("  1. Make sure Ollama is running: ollama serve")
            print(f"  2. Pull the AI model: ollama pull {self.settings.ollama_model}")
            print("  3. Check your .env file configuration")
            
            return False
        
        print("✅ All robot systems ready!")
        return True
    
    def _test_ollama_connection(self):
        """Test if Ollama is accessible"""
        try:
            import httpx
            with httpx.Client(timeout=5.0) as client:
                # Try to get the list of models
                response = client.get(self.settings.ollama_url.replace('/api/chat', '/api/tags'))
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    model_names = [model.get('name', '') for model in models]
                    
                    if self.settings.ollama_model in model_names:
                        print(f"✅ Ollama connected! Model {self.settings.ollama_model} is available.")
                        return True
                    else:
                        print(f"⚠️  Ollama connected, but model {self.settings.ollama_model} not found.")
                        print(f"Available models: {', '.join(model_names)}")
                        return False
                else:
                    print(f"❌ Ollama responded with status {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Cannot connect to Ollama: {str(e)}")
            return False
    
    def start_robot(self):
        """
        🚀 Start the robot server
        """
        print(f"🚀 Starting {self.settings.robot_name}...")
        
        try:
            # Configure uvicorn
            config = uvicorn.Config(
                app="main:app",
                host=self.settings.host,
                port=self.settings.port,
                reload=self.settings.reload,
                log_level=self.settings.log_level.lower(),
                access_log=True
            )
            
            server = uvicorn.Server(config)
            
            print(f"✨ {self.settings.robot_name} is starting up!")
            print(f"🌐 Server will be available at: http://{self.settings.host}:{self.settings.port}")
            print(f"🩺 Health check: http://{self.settings.host}:{self.settings.port}/health")
            print(f"💬 Chat endpoint: http://{self.settings.host}:{self.settings.port}/love-chat")
            print(f"📈 Settings: http://{self.settings.host}:{self.settings.port}/settings")
            print("\n📝 Press Ctrl+C to stop the robot gracefully")
            print("" * 60)
            
            # Start the server
            server.run()
            
        except KeyboardInterrupt:
            print("\n👋 Keyboard interrupt received. Shutting down gracefully...")
        except Exception as e:
            print(f"\n❌ Error starting robot: {str(e)}")
            return False
        
        return True
    
    def show_startup_help(self):
        """Show helpful information after startup"""
        print("\n🎆 ROBOT STARTUP COMPLETE! 🎆")
        print("\n📚 Quick Start Guide:")
        print("\n1. 🩺 Test robot health:")
        print(f"   curl http://{self.settings.host}:{self.settings.port}/health")
        
        print("\n2. 💬 Chat with your robot:")
        print(f"   curl -X POST http://{self.settings.host}:{self.settings.port}/love-chat \\")
        print("        -H 'Content-Type: application/json' \\")
        print("        -d '{"message": "Hello robot!", "temperature": 0.7}'")
        
        print("\n3. 📈 View robot settings:")
        print(f"   curl http://{self.settings.host}:{self.settings.port}/settings")
        
        print("\n4. 🔍 Detailed health check:")
        print(f"   curl http://{self.settings.host}:{self.settings.port}/health/detailed")
        
        print("\n🌐 Web Interface:")
        print(f"   Open http://{self.settings.host}:{self.settings.port}/docs for API documentation")
        
        print("\n🛠️  Troubleshooting:")
        print("   - If robot seems tired, check /health for energy levels")
        print("   - If responses are slow, check Ollama connection")
        print("   - Check logs/ directory for detailed information")
        
        print("\n💖 Your robot is ready to spread love and kindness! 💖")
    
    def run(self):
        """
        🏃 Main run method - orchestrates the entire startup process
        """
        try:
            # Show banner
            self.print_banner()
            
            # Check prerequisites
            if not self.check_prerequisites():
                print("\n❌ Cannot start robot due to missing prerequisites.")
                return False
            
            # Show help
            self.show_startup_help()
            
            # Wait a moment for user to read
            print("\n🕒 Starting in 3 seconds... (Press Ctrl+C to cancel)")
            for i in range(3, 0, -1):
                if self.shutdown_requested:
                    print("\n👋 Startup cancelled.")
                    return False
                print(f"   {i}...")
                time.sleep(1)
            
            # Start the robot
            return self.start_robot()
            
        except KeyboardInterrupt:
            print("\n👋 Startup cancelled by user.")
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error during startup: {str(e)}")
            return False
        finally:
            print(f"\n👋 {self.settings.robot_name} says goodbye! Thanks for spreading love! 💖")

def main():
    """Main entry point"""
    launcher = RobotLauncher()
    success = launcher.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()