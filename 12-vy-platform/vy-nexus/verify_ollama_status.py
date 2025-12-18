#!/usr/bin/env python3
"""Verify Ollama installation and check for llama3 model"""

import subprocess
import sys
import json
from datetime import datetime

def run_command(cmd):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def main():
    print("🔍 OLLAMA VERIFICATION SYSTEM")
    print("=" * 50)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "ollama_installed": False,
        "ollama_running": False,
        "llama3_available": False,
        "models": []
    }
    
    # Check if ollama command exists
    print("\n1. Checking Ollama installation...")
    code, stdout, stderr = run_command("which ollama")
    if code == 0 and stdout.strip():
        results["ollama_installed"] = True
        results["ollama_path"] = stdout.strip()
        print(f"   ✅ Ollama found at: {stdout.strip()}")
    else:
        print("   ❌ Ollama not found in PATH")
        print(json.dumps(results, indent=2))
        return results
    
    # Check Ollama version
    print("\n2. Checking Ollama version...")
    code, stdout, stderr = run_command("ollama --version")
    if code == 0:
        results["ollama_version"] = stdout.strip()
        print(f"   ✅ Version: {stdout.strip()}")
    
    # List available models
    print("\n3. Listing available models...")
    code, stdout, stderr = run_command("ollama list")
    if code == 0:
        results["ollama_running"] = True
        print(f"   ✅ Ollama is running")
        print("\n   Available models:")
        
        # Parse the output
        lines = stdout.strip().split('\n')
        if len(lines) > 1:  # Skip header
            for line in lines[1:]:
                if line.strip():
                    print(f"   - {line}")
                    results["models"].append(line.strip())
                    
                    # Check for llama3
                    if 'llama3' in line.lower():
                        results["llama3_available"] = True
        
        if results["llama3_available"]:
            print("\n   ✅ llama3 model is available!")
        else:
            print("\n   ⚠️  llama3 model NOT found")
    else:
        print(f"   ❌ Failed to list models")
        print(f"   Error: {stderr}")
        results["error"] = stderr
    
    # Check if Ollama process is running
    print("\n4. Checking Ollama process...")
    code, stdout, stderr = run_command("ps aux | grep ollama | grep -v grep")
    if code == 0 and stdout.strip():
        print("   ✅ Ollama process is running")
        results["process_running"] = True
    else:
        print("   ⚠️  Ollama process not detected (may still work via launchd)")
        results["process_running"] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"  Ollama Installed: {'✅' if results['ollama_installed'] else '❌'}")
    print(f"  Ollama Running: {'✅' if results['ollama_running'] else '❌'}")
    print(f"  llama3 Available: {'✅' if results['llama3_available'] else '❌'}")
    print(f"  Total Models: {len(results['models'])}")
    print("=" * 50)
    
    # Save results to file
    results_file = "/Users/lordwilson/vy-nexus/ollama_verification_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📝 Results saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    results = main()
    
    # Exit with appropriate code
    if results["ollama_installed"] and results["ollama_running"]:
        sys.exit(0)
    else:
        sys.exit(1)
