#!/usr/bin/env python3
"""MOIE-OS Heartbeat - Autonomous Phase Progression System"""

import json
import os
import subprocess
from datetime import datetime

# CONFIGURATION
# Base Metal Path - Adjust to your actual path
BASE_PATH = "/Users/lordwilson/vy-nexus"
STATE_FILE = os.path.join(BASE_PATH, "sovereign_state_v2.json")
LOG_DIR = "/Users/lordwilson/research_logs"

def load_state():
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def log_heartbeat(message):
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(os.path.join(LOG_DIR, "system_journal.md"), "a") as f:
        f.write(f"\n- **{timestamp}**: {message}")

def verify_job(command):
    """Runs a shell command to see if the job is actually done."""
    if not command: 
        return False
    try:
        # Simple verification: if command returns exit code 0, it's done.
        subprocess.check_call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def main():
    print("🔋 MOIE-OS HEARTBEAT INITIATED...")
    state = load_state()
    state['meta']['last_heartbeat'] = datetime.now().isoformat()
    
    current_phase_id = state['meta']['current_phase']
    active_phase = next((p for p in state['phases'] if p['id'] == current_phase_id), None)
    
    if not active_phase:
        print("ALL PHASES COMPLETE. SYSTEM IS SOVEREIGN.")
        return

    print(f"🔹 PHASE {current_phase_id}: {active_phase['name']}")
    
    # Find next pending job
    next_job = next((j for j in active_phase['jobs'] if j['status'] == "pending"), None)
    
    # Check for cyclic jobs (eternal monitoring tasks)
    cyclic_job = next((j for j in active_phase['jobs'] if j['status'] == "cyclic"), None)
    
    if not next_job:
        # If we have a cyclic job, execute it
        if cyclic_job:
            print(f"🔄 CYCLIC JOB ACTIVE: {cyclic_job['task']}")
            print(f"📝 DESCRIPTION: {cyclic_job['description']}")
            print("\n!!! CYCLIC EXECUTION !!!")
            print(f"TASK: {cyclic_job['task']}")
            print(f"CONTEXT: {cyclic_job['description']}")
            print(f"This job runs perpetually and never completes.")
            log_heartbeat(f"CYCLIC EXECUTION: {cyclic_job['task']}")
            save_state(state)
            return
        
        # If no pending jobs in this phase, check if all are completed or cyclic
        if all(j['status'] in ["completed", "cyclic"] for j in active_phase['jobs']):
            print("✅ Phase Complete. Promoting to next phase.")
            state['meta']['current_phase'] += 1
            # Unlock next phase
            next_phase = next((p for p in state['phases'] if p['id'] == current_phase_id + 1), None)
            if next_phase: 
                next_phase['status'] = "active"
            save_state(state)
            log_heartbeat(f"COMPLETED PHASE {current_phase_id}. PROMOTING.")
            return
        else:
            print("⚠️ Logic Error: No pending jobs, but phase not complete.")
            print(f"Job statuses: {[j['status'] for j in active_phase['jobs']]}")
            return

    # WE HAVE A JOB
    print(f"🔸 TARGET ACQUIRED: {next_job['task']}")
    print(f"📝 DESCRIPTION: {next_job['description']}")
    
    # First: Check if it was already done (Shadow Verification)
    if verify_job(next_job.get('verification_cmd')):
        print(f"✅ VERIFICATION SUCCESS: {next_job['task']} is already done.")
        next_job['status'] = "completed"
        save_state(state)
        log_heartbeat(f"VERIFIED & CLOSED: {next_job['task']}")
        return

    # If not done, this output becomes the prompt for Vy
    print("\n!!! ACTION REQUIRED !!!")
    print(f"Vy, please execute the following task strictly:\n")
    print(f"TASK: {next_job['task']}")
    print(f"CONTEXT: {next_job['description']}")
    print(f"Once you have written the code/run the command, run this script again to verify.")

    save_state(state)

if __name__ == "__main__":
    main()
