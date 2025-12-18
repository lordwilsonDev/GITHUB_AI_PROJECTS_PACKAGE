#!/usr/bin/env python3
"""Complete Phase 2: UPGRADE THE HEART - Automated Execution"""

import subprocess
import json
import os
import sys
from datetime import datetime

BASE_PATH = "/Users/lordwilson/vy-nexus"
STATE_FILE = os.path.join(BASE_PATH, "sovereign_state.json")
LOG_DIR = "/Users/lordwilson/research_logs"

def run_command(cmd, timeout=30):
    """Run a shell command and return output"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def log_to_journal(message):
    """Log message to system journal"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    journal_file = os.path.join(LOG_DIR, "system_journal.md")
    with open(journal_file, "a") as f:
        f.write(f"\n- **{timestamp}**: {message}")

def load_state():
    """Load sovereign state"""
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    """Save sovereign state"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def mark_job_complete(job_id):
    """Mark a job as completed in the state file"""
    state = load_state()
    for phase in state['phases']:
        if phase['id'] == 2:
            for job in phase['jobs']:
                if job['id'] == job_id:
                    job['status'] = 'completed'
                    print(f"✅ Job {job_id} marked as completed")
                    log_to_journal(f"Job {job_id} completed: {job['task']}")
    save_state(state)

def check_ollama_installed():
    """Check if Ollama is installed"""
    print("\n🔍 Checking Ollama installation...")
    code, stdout, stderr = run_command("which ollama")
    
    if code == 0 and stdout.strip():
        print(f"✅ Ollama found at: {stdout.strip()}")
        
        # Get version
        code, version, _ = run_command("ollama --version")
        if code == 0:
            print(f"   Version: {version.strip()}")
        return True
    else:
        print("❌ Ollama not found")
        print("   Please install from: https://ollama.ai")
        return False

def check_llama3_exists():
    """Check if llama3 model already exists"""
    print("\n🔍 Checking for llama3 model...")
    code, stdout, stderr = run_command("ollama list")
    
    if code == 0:
        print("\n📋 Current Ollama models:")
        print(stdout)
        
        if 'llama3' in stdout.lower():
            print("✅ llama3 model is already installed")
            return True
        else:
            print("⚠️  llama3 model NOT found")
            return False
    else:
        print(f"❌ Failed to list models: {stderr}")
        return False

def pull_llama3():
    """Pull llama3 model from Ollama"""
    print("\n📥 Pulling llama3 model...")
    print("   This may take several minutes depending on your connection.")
    print("   Model size: ~4.7GB")
    print("")
    
    # Run with longer timeout for download
    code, stdout, stderr = run_command("ollama pull llama3", timeout=600)
    
    if code == 0:
        print("✅ llama3 model pulled successfully")
        print(stdout)
        return True
    else:
        print(f"❌ Failed to pull llama3: {stderr}")
        return False

def create_config_yaml():
    """Create or update config.yaml with llama3 configuration"""
    print("\n⚙️  Creating/updating config.yaml...")
    
    config_file = os.path.join(BASE_PATH, "config.yaml")
    
    config_content = """# MOIE-OS Configuration
# Phase 2: Upgraded to Llama3
# Generated: {timestamp}

system:
  name: "MOIE-OS Sovereign Intelligence"
  version: "1.0.0"
  operator: "Lord Wilson"
  base_path: "/Users/lordwilson/vy-nexus"

reasoning_core:
  model: "llama3:latest"
  provider: "ollama"
  temperature: 0.7
  max_tokens: 4096
  context_window: 8192

logging:
  level: "info"
  journal_path: "/Users/lordwilson/research_logs/daily.md"
  safety_log: "/Users/lordwilson/research_logs/safety.log"
  system_journal: "/Users/lordwilson/research_logs/system_journal.md"

safety:
  enabled: true
  critical_error_threshold: 3
  auto_shutdown: true
  save_state_on_shutdown: true

file_system:
  safe_mode: true
  allowed_paths:
    - "/Users/lordwilson/vy-nexus"
    - "/Users/lordwilson/research_logs"
  max_file_size: 10485760  # 10MB

heartbeat:
  enabled: true
  interval_minutes: 10
  state_file: "/Users/lordwilson/vy-nexus/sovereign_state.json"
""".format(timestamp=datetime.now().isoformat())
    
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print(f"✅ config.yaml created at: {config_file}")
    
    # Verify
    code, stdout, stderr = run_command(f"grep 'llama3' {config_file}")
    if code == 0:
        print("✅ Verification: config.yaml contains llama3 reference")
        return True
    else:
        print("❌ Verification failed")
        return False

def complete_phase2():
    """Mark Phase 2 as complete and promote to Phase 3"""
    print("\n🎯 Completing Phase 2...")
    
    state = load_state()
    
    # Check if all Phase 2 jobs are complete
    phase2 = next(p for p in state['phases'] if p['id'] == 2)
    all_complete = all(j['status'] == 'completed' for j in phase2['jobs'])
    
    if all_complete:
        # Mark Phase 2 as completed
        phase2['status'] = 'completed'
        
        # Promote to Phase 3
        state['meta']['current_phase'] = 3
        
        # Unlock Phase 3
        phase3 = next(p for p in state['phases'] if p['id'] == 3)
        phase3['status'] = 'active'
        
        # Update heartbeat
        state['meta']['last_heartbeat'] = datetime.now().isoformat()
        
        save_state(state)
        
        print("✅ Phase 2 COMPLETED")
        print("✅ Promoted to Phase 3: THE MoIE ARCHITECTURE")
        log_to_journal("PHASE 2 COMPLETED - Promoted to Phase 3")
        return True
    else:
        print("⚠️  Not all Phase 2 jobs are complete:")
        for job in phase2['jobs']:
            status_icon = "✅" if job['status'] == 'completed' else "❌"
            print(f"  {status_icon} {job['id']}: {job['status']}")
        return False

def main():
    print("="*60)
    print("🔋 MOIE-OS PHASE 2: UPGRADE THE HEART")
    print("="*60)
    
    # Job 2.1: Pull Llama3 on Ollama
    print("\n" + "="*60)
    print("📦 JOB 2.1: Pull Llama3 on Ollama")
    print("="*60)
    
    # Step 1: Check Ollama installation
    if not check_ollama_installed():
        print("\n❌ Cannot proceed without Ollama. Exiting.")
        sys.exit(1)
    
    # Step 2: Check if llama3 exists
    llama3_exists = check_llama3_exists()
    
    # Step 3: Pull llama3 if needed
    if not llama3_exists:
        if not pull_llama3():
            print("\n❌ Failed to pull llama3. Exiting.")
            sys.exit(1)
    
    # Step 4: Verify llama3 is available
    print("\n🔍 Final verification of llama3...")
    code, stdout, stderr = run_command("ollama list | grep llama3")
    if code == 0:
        print("✅ llama3 verified and ready")
        print(f"   {stdout.strip()}")
        mark_job_complete('2.1')
    else:
        print("❌ llama3 verification failed")
        sys.exit(1)
    
    # Job 2.2: Update Config to Llama3
    print("\n" + "="*60)
    print("⚙️  JOB 2.2: Update Config to Llama3")
    print("="*60)
    
    if create_config_yaml():
        mark_job_complete('2.2')
    else:
        print("❌ Failed to create config.yaml")
        sys.exit(1)
    
    # Complete Phase 2
    print("\n" + "="*60)
    print("🏁 PHASE 2 COMPLETION")
    print("="*60)
    
    if complete_phase2():
        print("\n" + "="*60)
        print("🎉 SUCCESS! PHASE 2 COMPLETE")
        print("="*60)
        print("\nNext steps:")
        print("  1. Review sovereign_state.json")
        print("  2. Run: python3 vy_pulse.py")
        print("  3. Begin Phase 3: THE MoIE ARCHITECTURE")
        print("")
        sys.exit(0)
    else:
        print("\n❌ Phase 2 completion failed")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
