#!/usr/bin/env python3
"""
Script to install and run Open WebUI with Docker
"""

import subprocess
import time
import requests

def run_command(cmd, description):
    """Run a shell command and return success status"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            print(f"✓ {description} completed successfully")
            if result.stdout.strip():
                print(f"Output: {result.stdout.strip()}")
            return True
        else:
            print(f"✗ {description} failed")
            print(f"Error: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ {description} timed out")
        return False
    except Exception as e:
        print(f"✗ {description} failed with exception: {e}")
        return False

def check_docker():
    """Check if Docker is running"""
    return run_command("docker --version", "Checking Docker installation")

def pull_openwebui():
    """Pull the Open WebUI Docker image"""
    return run_command(
        "docker pull ghcr.io/open-webui/open-webui:main",
        "Pulling Open WebUI Docker image"
    )

def stop_existing_container():
    """Stop and remove existing Open WebUI container if it exists"""
    print("\nChecking for existing Open WebUI container...")
    
    # Check if container exists
    result = subprocess.run(
        "docker ps -a --filter name=open-webui --format '{{.Names}}'",
        shell=True, capture_output=True, text=True
    )
    
    if "open-webui" in result.stdout:
        print("Found existing container, stopping and removing...")
        run_command("docker stop open-webui", "Stopping existing container")
        run_command("docker rm open-webui", "Removing existing container")
    else:
        print("No existing container found")

def run_openwebui():
    """Run Open WebUI container with connection to local Ollama"""
    # Use OLLAMA_BASE_URL to connect to local Ollama instance
    cmd = (
        "docker run -d -p 3000:8080 "
        "-e OLLAMA_BASE_URL=http://host.docker.internal:11434 "
        "-v open-webui:/app/backend/data "
        "--name open-webui "
        "--restart always "
        "ghcr.io/open-webui/open-webui:main"
    )
    
    return run_command(cmd, "Starting Open WebUI container")

def wait_for_webui(max_attempts=30):
    """Wait for Open WebUI to be accessible"""
    print("\nWaiting for Open WebUI to start...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            if response.status_code == 200:
                print(f"✓ Open WebUI is accessible at http://localhost:3000")
                return True
        except:
            pass
        
        print(f"Attempt {attempt + 1}/{max_attempts} - waiting...")
        time.sleep(2)
    
    print("✗ Open WebUI did not become accessible within the timeout period")
    return False

def check_container_logs():
    """Check Open WebUI container logs for any issues"""
    print("\nChecking container logs...")
    result = subprocess.run(
        "docker logs open-webui --tail 20",
        shell=True, capture_output=True, text=True
    )
    
    if result.stdout:
        print("Recent logs:")
        print(result.stdout)
    if result.stderr:
        print("Error logs:")
        print(result.stderr)

def main():
    """Main installation process"""
    print("=== Open WebUI Installation Script ===")
    
    # Step 1: Check Docker
    if not check_docker():
        print("\n❌ Docker is not available. Please install Docker first.")
        return False
    
    # Step 2: Stop existing container
    stop_existing_container()
    
    # Step 3: Pull image
    if not pull_openwebui():
        print("\n❌ Failed to pull Open WebUI image")
        return False
    
    # Step 4: Run container
    if not run_openwebui():
        print("\n❌ Failed to start Open WebUI container")
        return False
    
    # Step 5: Wait for startup
    if not wait_for_webui():
        print("\n❌ Open WebUI failed to start properly")
        check_container_logs()
        return False
    
    print("\n🎉 Open WebUI installation completed successfully!")
    print("\n📋 Next steps:")
    print("1. Open your browser and go to: http://localhost:3000")
    print("2. Create your admin account (first user becomes admin)")
    print("3. Configure connection to your Love Engine at http://host.docker.internal:9000")
    print("\n🔧 Container management:")
    print("- View logs: docker logs open-webui")
    print("- Stop: docker stop open-webui")
    print("- Start: docker start open-webui")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
