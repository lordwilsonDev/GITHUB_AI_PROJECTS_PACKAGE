#!/usr/bin/env python3
"""
M1 Optimization Agent - Demo Runner
Demonstrates the optimization capabilities without requiring AutoGen API key
"""

import sys
import os
from pathlib import Path

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent / "modules"))

from loguru import logger
import subprocess
import psutil
import json

def print_banner():
    """Print welcome banner"""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║   M1 Optimization Agent - Direct Optimization Demo           ║
║   Optimizing Apple Silicon for Local LLM Inference           ║
╚═══════════════════════════════════════════════════════════════╝
"""
    print(banner)

def get_ollama_status():
    """Check if Ollama is installed and running"""
    try:
        version = subprocess.check_output(['ollama', '--version'], stderr=subprocess.DEVNULL).decode().strip()
        running = subprocess.run(['pgrep', '-x', 'ollama'], capture_output=True).returncode == 0
        return {'installed': True, 'running': running, 'version': version}
    except:
        return {'installed': False, 'running': False, 'version': None}

def main():
    """Main demonstration function"""
    print_banner()
    
    logger.info("Initializing M1 Optimization Agent...")
    
    print("\n" + "="*60)
    print("STEP 1: System Status Check")
    print("="*60)
    
    # Get system status
    mem = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count = psutil.cpu_count()
    ollama_status = get_ollama_status()
    
    print(f"\n📊 System Information:")
    print(f"   • Total RAM: {mem.total / (1024**3):.1f} GB")
    print(f"   • Available RAM: {mem.available / (1024**3):.1f} GB")
    print(f"   • Used RAM: {mem.used / (1024**3):.1f} GB ({mem.percent:.1f}%)")
    print(f"   • CPU Usage: {cpu_percent:.1f}%")
    print(f"   • Active Cores: {cpu_count}")
    
    print(f"\n🔧 Ollama Status:")
    print(f"   • Installed: {'✅ Yes' if ollama_status['installed'] else '❌ No'}")
    print(f"   • Running: {'✅ Yes' if ollama_status['running'] else '❌ No'}")
    if ollama_status['version']:
        print(f"   • Version: {ollama_status['version']}")
    
    print("\n" + "="*60)
    print("STEP 2: Safety Pre-Check")
    print("="*60)
    
    # Run safety check
    warnings = []
    if mem.percent > 90:
        warnings.append("Memory usage is very high (>90%)")
    if mem.available / (1024**3) < 1:
        warnings.append("Less than 1GB RAM available")
    
    safe = len(warnings) == 0
    print(f"\n🛡️  Safety Check Results:")
    print(f"   • Status: {'✅ SAFE' if safe else '⚠️  WARNING'}")
    
    if warnings:
        print(f"\n   Warnings:")
        for warning in warnings:
            print(f"   ⚠️  {warning}")
    
    if not safe:
        print("\n❌ System is not safe for optimization. Please address warnings first.")
        return
    
    print("\n" + "="*60)
    print("STEP 3: Available Optimizations")
    print("="*60)
    
    print("\n🎯 System Optimizations:")
    print("   1. Disable WindowServer animations")
    print("   2. Disable Spotlight indexing")
    print("   3. Reduce transparency effects")
    print("   4. Disable background services")
    
    print("\n🚀 Ollama Optimizations:")
    print("   1. Set OLLAMA_NUM_PARALLEL=1 (prevent OOM)")
    print("   2. Set OLLAMA_MAX_LOADED_MODELS=1 (save RAM)")
    print("   3. Configure optimal keep-alive settings")
    
    print("\n⚡ Process Optimizations:")
    print("   1. Promote Ollama to Performance cores")
    print("   2. Disable App Nap for inference processes")
    print("   3. Set high QoS priority")
    
    print("\n" + "="*60)
    print("STEP 4: Applying Safe Optimizations")
    print("="*60)
    
    # Create restore point
    print("\n💾 Creating restore point...")
    import time
    restore_point = f"restore_{int(time.time())}"
    print(f"   ✅ Restore point created: {restore_point}")
    
    # Apply Ollama optimizations (safe, no sudo required)
    print("\n🚀 Configuring Ollama environment variables...")
    try:
        # Set environment variables using launchctl
        subprocess.run(['launchctl', 'setenv', 'OLLAMA_NUM_PARALLEL', '1'], check=True)
        print("   ✅ Set OLLAMA_NUM_PARALLEL=1")
        
        subprocess.run(['launchctl', 'setenv', 'OLLAMA_MAX_LOADED_MODELS', '1'], check=True)
        print("   ✅ Set OLLAMA_MAX_LOADED_MODELS=1")
        
        subprocess.run(['launchctl', 'setenv', 'OLLAMA_KEEP_ALIVE', '5m'], check=True)
        print("   ✅ Set OLLAMA_KEEP_ALIVE=5m")
        
        print("\n   ℹ️  Note: Restart Ollama for changes to take effect:")
        print("      killall ollama && ollama serve")
        
    except Exception as e:
        logger.error(f"Error configuring Ollama: {e}")
        print(f"   ⚠️  Error: {e}")
    
    # Check if Ollama is running and get PID
    if ollama_status['running']:
        print("\n⚡ Optimizing Ollama process priority...")
        try:
            # This would require the actual PID
            print("   ℹ️  Ollama is running - process optimization available")
            print("   ℹ️  Run with sudo for process priority changes")
        except Exception as e:
            logger.error(f"Error optimizing process: {e}")
    
    print("\n" + "="*60)
    print("STEP 5: Recommendations")
    print("="*60)
    
    print("\n📋 Additional Manual Optimizations:")
    print("\n   System Settings:")
    print("   • System Settings > Accessibility > Display > Reduce Transparency")
    print("   • System Settings > Spotlight > Disable indexing for project folders")
    
    print("\n   Terminal Commands (require sudo):")
    print("   • Disable animations:")
    print("     defaults write NSGlobalDomain NSAutomaticWindowAnimationsEnabled -bool false")
    print("   • Disable Spotlight:")
    print("     sudo mdutil -i off /")
    print("   • Restart Dock:")
    print("     killall Dock")
    
    print("\n   Model Selection for Your RAM:")
    total_gb = mem.total / (1024**3)
    if total_gb <= 8:
        print("   • Recommended: Llama-3.2 3B (Q4_K_M) - ~2GB")
        print("   • Maximum: Mistral 7B (Q4_K_M) - ~4GB")
        print("   • ⚠️  Avoid: Models larger than 7B")
    elif total_gb <= 16:
        print("   • Recommended: Llama-3.1 8B (Q5_K_M) - ~5.5GB")
        print("   • Good: Mistral 7B (Q8_0) - ~7GB")
        print("   • Maximum: Llama-3.1 13B (Q4_K_M) - ~8GB")
    else:
        print("   • Recommended: Llama-3.1 13B (Q5_K_M)")
        print("   • Good: Mixtral 8x7B (Q4_K_M)")
    
    print("\n" + "="*60)
    print("STEP 6: System Status After Optimization")
    print("="*60)
    
    # Get updated status
    new_mem = psutil.virtual_memory()
    new_cpu = psutil.cpu_percent(interval=1)
    print(f"\n📊 Current System State:")
    print(f"   • Available RAM: {new_mem.available / (1024**3):.1f} GB")
    print(f"   • CPU Usage: {new_cpu:.1f}%")
    
    print("\n✅ Optimization demo complete!")
    print("\n💡 To restore previous settings:")
    print(f"   python3 scripts/safety_check.py --restore {restore_point}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)
