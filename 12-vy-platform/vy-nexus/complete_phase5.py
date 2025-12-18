#!/usr/bin/env python3
"""MOIE-OS Phase 5 Automation Script - INTELLIGENCE & OPTIMIZATION"""

import json
import os
import subprocess
from datetime import datetime

# CONFIGURATION
BASE_PATH = "/Users/lordwilson/vy-nexus"
STATE_FILE = os.path.join(BASE_PATH, "sovereign_state.json")
LOG_DIR = "/Users/lordwilson/research_logs"

def log_to_journal(message):
    """Log message to system journal"""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(os.path.join(LOG_DIR, "system_journal.md"), "a") as f:
        f.write(f"\n- **{timestamp}**: {message}")

def load_state():
    """Load sovereign state from JSON"""
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    """Save sovereign state to JSON"""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def verify_job(command):
    """Verify job completion using shell command"""
    if not command:
        return False
    try:
        subprocess.check_call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def main():
    print("\n" + "="*60)
    print("🚀 MOIE-OS PHASE 5: INTELLIGENCE & OPTIMIZATION")
    print("="*60 + "\n")
    
    # Load current state
    state = load_state()
    
    # Check if Phase 5 exists
    phase5 = next((p for p in state['phases'] if p['id'] == 5), None)
    
    if not phase5:
        print("❌ Phase 5 not found in sovereign_state.json")
        print("\nPlease add Phase 5 definition first.")
        print("See PHASE5_PROPOSAL.md for details.\n")
        return
    
    print(f"🔹 Phase Status: {phase5['status']}")
    print(f"🔹 Total Jobs: {len(phase5['jobs'])}\n")
    
    # Process each job
    for job in phase5['jobs']:
        job_id = job['id']
        task = job['task']
        status = job['status']
        
        print(f"\n{'='*60}")
        print(f"🔸 Job {job_id}: {task}")
        print(f"{'='*60}")
        
        # Skip if already completed
        if status == "completed":
            print("✅ Already completed. Skipping.")
            continue
        
        # Check if already done (shadow verification)
        verification_cmd = job.get('verification_cmd')
        if verification_cmd and verify_job(verification_cmd):
            print("✅ VERIFICATION SUCCESS: Job already complete!")
            job['status'] = "completed"
            save_state(state)
            log_to_journal(f"Phase 5 Job {job_id} verified complete: {task}")
            continue
        
        # Job needs to be done
        print(f"\n⚠️  ACTION REQUIRED")
        print(f"\nDescription: {job['description']}")
        print(f"\nThis job requires manual implementation.")
        print(f"Once complete, run this script again to verify.\n")
        
        # Don't continue to next job
        break
    
    # Check if all jobs complete
    if all(j['status'] == "completed" for j in phase5['jobs']):
        print("\n" + "="*60)
        print("✅ PHASE 5 COMPLETE!")
        print("="*60)
        print("\nAll intelligence and optimization jobs finished.")
        print("System is now smarter, faster, and more maintainable.\n")
        
        phase5['status'] = "completed"
        state['meta']['current_phase'] = 6
        save_state(state)
        log_to_journal("PHASE 5 COMPLETE: INTELLIGENCE & OPTIMIZATION")
        
        print("🚀 Ready for Phase 6: DISTRIBUTED INTELLIGENCE\n")
    else:
        pending = [j for j in phase5['jobs'] if j['status'] == 'pending']
        completed = [j for j in phase5['jobs'] if j['status'] == 'completed']
        print(f"\n📊 Progress: {len(completed)}/{len(phase5['jobs'])} jobs complete")
        print(f"🔹 Remaining: {len(pending)} jobs\n")

if __name__ == "__main__":
    main()
