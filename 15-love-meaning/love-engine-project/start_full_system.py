#!/usr/bin/env python3
"""
Script to start the complete Love Engine system:
1. Verify Ollama is running
2. Start Love Engine (OpenAI-compatible)
3. Start Open WebUI (if not running)
4. Provide configuration instructions
"""

import subprocess
import time
import requests
import sys
import os

def check_service(url, name, timeout=5):
    """Check if a service is running"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✓ {name} is running")
            return True
        else:
            print(f"✗ {name} returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ {name} is not accessible: {e}")
        return False

def start_love_engine():
    """Start the Love Engine in the background"""
    print("\nStarting Love Engine (OpenAI-compatible)...")
    try:
        # Change to project directory
        project_dir = "/Users/lordwilson/love-engine-project"
        os.chdir(project_dir)
        
        # Start Love Engine in background
        process = subprocess.Popen([
            sys.executable, "love_engine_openai_compatible.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Give it time to start
        time.sleep(3)
        
        # Check if it's running
        if check_service("http://localhost:9000/health", "Love Engine"):
            print(f"✓ Love Engine started successfully (PID: {process.pid})")
            return process
        else:
            print("✗ Love Engine failed to start")
            stdout, stderr = process.communicate(timeout=1)
            if stdout:
                print(f"STDOUT: {stdout.decode()}")
            if stderr:
                print(f"STDERR: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"✗ Error starting Love Engine: {e}")
        return None

def start_open_webui():
    """Start Open WebUI with Docker"""
    print("\nStarting Open WebUI...")
    try:
        # Check if container already exists
        result = subprocess.run(
            "docker ps -a --filter name=open-webui --format '{{.Names}}'",
            shell=True, capture_output=True, text=True
        )
        
        if "open-webui" in result.stdout:
            print("Found existing Open WebUI container, starting it...")
            subprocess.run("docker start open-webui", shell=True, check=True)
        else:
            print("Creating new Open WebUI container...")
            cmd = (
                "docker run -d -p 3000:8080 "
                "-e OLLAMA_BASE_URL=http://host.docker.internal:11434 "
                "-v open-webui:/app/backend/data "
                "--name open-webui "
                "--restart always "
                "ghcr.io/open-webui/open-webui:main"
            )
            subprocess.run(cmd, shell=True, check=True)
        
        # Wait for it to start
        print("Waiting for Open WebUI to start...")
        for i in range(30):
            if check_service("http://localhost:3000", "Open WebUI", timeout=3):
                print("✓ Open WebUI started successfully")
                return True
            time.sleep(2)
            print(f"Attempt {i+1}/30...")
        
        print("✗ Open WebUI failed to start within timeout")
        return False
        
    except Exception as e:
        print(f"✗ Error starting Open WebUI: {e}")
        return False

def print_configuration_instructions():
    """Print instructions for configuring the system"""
    print("\n" + "="*60)
    print("🎉 LOVE ENGINE SYSTEM READY!")
    print("="*60)
    
    print("\n📋 SYSTEM STATUS:")
    print("- Ollama: http://localhost:11434 (with tinyllama:latest)")
    print("- Love Engine: http://localhost:9000 (OpenAI-compatible)")
    print("- Open WebUI: http://localhost:3000")
    
    print("\n🔧 CONFIGURATION STEPS:")
    print("1. Open your browser and go to: http://localhost:3000")
    print("2. Create your admin account (first user becomes admin)")
    print("3. Go to Settings → Admin Settings → Models")
    print("4. Add a new OpenAI-compatible API:")
    print("   - Name: Love Engine")
    print("   - Base URL: http://host.docker.internal:9000")
    print("   - API Key: (leave blank or use 'dummy')")
    print("   - Model: love-engine")
    
    print("\n🧪 TESTING:")
    print("1. Select 'Love Engine' model in Open WebUI")
    print("2. Try these test messages:")
    print("   - 'Hello, how are you?'")
    print("   - 'I feel sad and lonely today'")
    print("   - 'What is 2+2?'")
    
    print("\n🔍 VERIFICATION:")
    print("- Direct Love Engine test: python test_openai_compatibility.py")
    print("- Check Love Engine logs for thermodynamic adjustments")
    print("- Verify safety scores and love vector applications")
    
    print("\n🛠️ MANAGEMENT:")
    print("- Stop Love Engine: Ctrl+C in this terminal")
    print("- Stop Open WebUI: docker stop open-webui")
    print("- View Open WebUI logs: docker logs open-webui")
    print("- Restart system: python start_full_system.py")
    
    print("\n💡 WHAT TO EXPECT:")
    print("When you send a message through Open WebUI:")
    print("1. Open WebUI → Love Engine (/v1/chat/completions)")
    print("2. Love Engine → Computes love vector from your message")
    print("3. Love Engine → Ollama (tinyllama:latest) for draft response")
    print("4. Love Engine → Applies safety evaluation")
    print("5. Love Engine → Applies thermodynamic love adjustments")
    print("6. Love Engine → Returns 'love-filtered' response")
    print("7. Open WebUI → Displays the enhanced response")
    
    print("\n🎯 SUCCESS INDICATORS:")
    print("- Emotional messages get empathetic responses")
    print("- Safety scores are computed and logged")
    print("- Love vector adjustments are applied")
    print("- Responses include warmth, safety, and connection")
    
    print("\n" + "="*60)

def main():
    """Main system startup process"""
    print("🚀 Love Engine System Startup")
    print("=============================")
    
    # Step 1: Check Ollama
    print("\n1. Checking Ollama...")
    if not check_service("http://localhost:11434/api/tags", "Ollama"):
        print("❌ Ollama is not running. Please start Ollama first.")
        print("Run: ollama serve")
        return False
    
    # Step 2: Start Love Engine
    print("\n2. Starting Love Engine...")
    love_engine_process = start_love_engine()
    if not love_engine_process:
        print("❌ Failed to start Love Engine")
        return False
    
    # Step 3: Check/Start Open WebUI
    print("\n3. Checking/Starting Open WebUI...")
    if not check_service("http://localhost:3000", "Open WebUI", timeout=3):
        if not start_open_webui():
            print("❌ Failed to start Open WebUI")
            return False
    else:
        print("✓ Open WebUI is already running")
    
    # Step 4: Final verification
    print("\n4. Final system verification...")
    all_good = True
    all_good &= check_service("http://localhost:11434/api/tags", "Ollama")
    all_good &= check_service("http://localhost:9000/health", "Love Engine")
    all_good &= check_service("http://localhost:3000", "Open WebUI")
    
    if all_good:
        print_configuration_instructions()
        
        # Keep Love Engine running
        try:
            print("\n⏳ Love Engine is running. Press Ctrl+C to stop...")
            love_engine_process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping Love Engine...")
            love_engine_process.terminate()
            love_engine_process.wait()
            print("✓ Love Engine stopped")
        
        return True
    else:
        print("❌ System verification failed")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
