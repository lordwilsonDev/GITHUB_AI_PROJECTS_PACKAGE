#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from datetime import datetime

# CONFIGURATION
BASE_PATH = "/Users/lordwilson/vy-nexus"
STATE_FILE = os.path.join(BASE_PATH, "sovereign_state_v2.json")
LOG_FILE = os.path.join(BASE_PATH, "scheduler.log")

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}\n"
    print(entry.strip())
    with open(LOG_FILE, "a") as f:
        f.write(entry)

def load_state():
    if not os.path.exists(STATE_FILE):
        log("CRITICAL: State file not found.")
        sys.exit(1)
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def verify_cmd(cmd):
    if not cmd or cmd == "false": return False
    try:
        subprocess.check_call(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except:
        return False

def main():
    log("🔵 PULSE INITIATED")
    state = load_state()
    
    current_pid = state['meta']['current_phase']
    phase = next((p for p in state['phases'] if p['id'] == current_pid), None)
    
    if not phase:
        log("ERROR: Current phase ID not found in roadmap.")
        return

    log(f"PHASE {current_pid}: {phase['name']}")
    
    # Check for pending jobs
    pending = [j for j in phase['jobs'] if j['status'] == 'pending']
    
    if not pending:
        # Check for completion of phase
        if all(j['status'] in ['completed', 'cyclic'] for j in phase['jobs']):
            # If we are in the Final Phase (Cyclic), we do not promote. We just log.
            if any(j['status'] == 'cyclic' for j in phase['jobs']):
                log("♾️  SYSTEM IS IN INFINITE MONITORING MODE. IDLING.")
                return

            log(f"✅ PHASE {current_pid} COMPLETE. PROMOTING.")
            state['meta']['current_phase'] += 1
            
            # Unlock next phase
            next_phase = next((p for p in state['phases'] if p['id'] == current_pid + 1), None)
            if next_phase: 
                next_phase['status'] = "active"
                save_state(state)
            else:
                log("🏁 ALL PHASES COMPLETE. ENTERING MAINTENANCE.")
            return

    # Process first pending job
    job = pending[0]
    log(f"TARGET: {job['task']}")
    
    # 1. Shadow Verification (Did you do it already?)
    if verify_cmd(job.get('verification_cmd')):
        log(f"✅ AUTO-VERIFIED: {job['task']}")
        job['status'] = "completed"
        save_state(state)
        return

    # 2. Assign Task to Vy (The Output)
    print("\n" + "="*40)
    print("!!! ACTION REQUIRED !!!")
    print(f"TASK: {job['task']}")
    print(f"DESC: {job['description']}")
    print("="*40 + "\n")
    log(f"WAITING FOR OPERATOR/AGENT: {job['task']}")

if __name__ == "__main__":
    main()
