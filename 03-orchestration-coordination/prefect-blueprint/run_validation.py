#!/usr/bin/env python3
import subprocess
import os

# Change to project directory
os.chdir('/Users/lordwilson/prefect-blueprint')

# Activate virtual environment and run prefect version
activate_cmd = 'source .venv/bin/activate && prefect version'

try:
    result = subprocess.run(
        activate_cmd,
        shell=True,
        executable='/bin/bash',
        capture_output=True,
        text=True,
        timeout=30
    )
    
    print('=== PREFECT VERSION OUTPUT ===')
    print(result.stdout)
    if result.stderr:
        print('=== STDERR ===')
        print(result.stderr)
    print('=== RETURN CODE ===')
    print(result.returncode)
    
    # Save output to file
    with open('/Users/lordwilson/prefect-blueprint/version_output.txt', 'w') as f:
        f.write(result.stdout)
        if result.stderr:
            f.write('\n=== STDERR ===\n')
            f.write(result.stderr)
            
except Exception as e:
    print(f'Error: {e}')
