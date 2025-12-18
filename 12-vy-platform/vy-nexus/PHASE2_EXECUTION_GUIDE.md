# Phase 2: UPGRADE THE HEART - Execution Guide

## Overview
This phase upgrades the reasoning core to use Llama3 via Ollama.

## Prerequisites
- Ollama must be installed on the system
- Terminal access to run commands

## Job 2.1: Pull Llama3 on Ollama

### Step 1: Verify Ollama Installation
```bash
which ollama
ollama --version
```

### Step 2: Check Current Models
```bash
ollama list
```

### Step 3: Pull Llama3 Model (if not present)
```bash
ollama pull llama3
```

This will download the Llama3 8B model. It may take several minutes depending on your internet connection.

### Step 4: Verify Llama3 is Available
```bash
ollama list | grep llama3
```

You should see output like:
```
llama3:latest    ...
```

### Step 5: Mark Job 2.1 as Complete
Run the verification script:
```bash
cd /Users/lordwilson/vy-nexus
python3 verify_ollama_status.py
```

Or manually update sovereign_state.json:
```bash
python3 << 'EOF'
import json

state_file = '/Users/lordwilson/vy-nexus/sovereign_state.json'
with open(state_file, 'r') as f:
    state = json.load(f)

# Mark job 2.1 as completed
for phase in state['phases']:
    if phase['id'] == 2:
        for job in phase['jobs']:
            if job['id'] == '2.1':
                job['status'] = 'completed'
                print(f"✅ Marked job {job['id']} as completed")

with open(state_file, 'w') as f:
    json.dump(state, f, indent=2)

print("State file updated successfully")
EOF
```

---

## Job 2.2: Update Config to Llama3

### Step 1: Check if config.yaml Exists
```bash
ls -la /Users/lordwilson/vy-nexus/config.yaml
```

### Step 2: Create or Update config.yaml

If the file doesn't exist, create it:
```bash
cat > /Users/lordwilson/vy-nexus/config.yaml << 'EOF'
# MOIE-OS Configuration
# Phase 2: Upgraded to Llama3

reasoning_core:
  model: llama3:latest
  provider: ollama
  temperature: 0.7
  max_tokens: 2048
  
system:
  base_path: /Users/lordwilson/vy-nexus
  log_path: /Users/lordwilson/research_logs
  
safety:
  enabled: true
  critical_error_threshold: 3
  
heartbeat:
  interval_minutes: 10
  enabled: true
EOF
```

If it exists, update the reasoning_core section:
```bash
python3 << 'EOF'
import yaml
import os

config_file = '/Users/lordwilson/vy-nexus/config.yaml'

if os.path.exists(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f) or {}
else:
    config = {}

# Update reasoning_core to use llama3
config['reasoning_core'] = {
    'model': 'llama3:latest',
    'provider': 'ollama',
    'temperature': 0.7,
    'max_tokens': 2048
}

with open(config_file, 'w') as f:
    yaml.dump(config, f, default_flow_style=False)

print("✅ config.yaml updated with llama3:latest")
EOF
```

### Step 3: Verify Configuration
```bash
grep 'llama3' /Users/lordwilson/vy-nexus/config.yaml
```

You should see:
```
  model: llama3:latest
```

### Step 4: Mark Job 2.2 as Complete
```bash
python3 << 'EOF'
import json

state_file = '/Users/lordwilson/vy-nexus/sovereign_state.json'
with open(state_file, 'r') as f:
    state = json.load(f)

# Mark job 2.2 as completed
for phase in state['phases']:
    if phase['id'] == 2:
        for job in phase['jobs']:
            if job['id'] == '2.2':
                job['status'] = 'completed'
                print(f"✅ Marked job {job['id']} as completed")

with open(state_file, 'w') as f:
    json.dump(state, f, indent=2)

print("State file updated successfully")
EOF
```

---

## Phase 2 Completion

### Verify All Jobs Complete
```bash
cd /Users/lordwilson/vy-nexus
python3 vy_pulse.py
```

This should show:
```
✅ Phase Complete. Promoting to next phase.
```

### Manual Phase Promotion (if needed)
```bash
python3 << 'EOF'
import json
from datetime import datetime

state_file = '/Users/lordwilson/vy-nexus/sovereign_state.json'
with open(state_file, 'r') as f:
    state = json.load(f)

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
    
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    print("✅ Phase 2 completed and promoted to Phase 3")
else:
    print("⚠️  Not all Phase 2 jobs are complete")
    for job in phase2['jobs']:
        print(f"  {job['id']}: {job['status']}")
EOF
```

---

## Quick Execution Script

For convenience, you can run this all-in-one script:

```bash
cd /Users/lordwilson/vy-nexus
bash execute_phase2.sh
```

---

## Troubleshooting

### Ollama Not Found
If `which ollama` returns nothing:
1. Install Ollama from https://ollama.ai
2. Or check if it's installed but not in PATH: `ls -la /usr/local/bin/ollama`

### Ollama Service Not Running
Start Ollama:
```bash
ollama serve &
```

Or check if it's running:
```bash
ps aux | grep ollama
```

### Model Download Fails
Check your internet connection and try again:
```bash
ollama pull llama3
```

### YAML Module Not Found
Install PyYAML:
```bash
pip3 install pyyaml
```
