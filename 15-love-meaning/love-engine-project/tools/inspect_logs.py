#!/usr/bin/env python3
"""
CLI tool to inspect recent Love Engine safety decisions
"""

import json
import sys
import os
from datetime import datetime

def read_last_n_lines(file_path, n):
    """Read the last N lines from a file"""
    if not os.path.exists(file_path):
        return []
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    return lines[-n:] if len(lines) >= n else lines

def format_decision_line(json_line):
    """Format a decision log line for human-readable output"""
    try:
        data = json.loads(json_line.strip())
        
        # Extract timestamp and format it
        ts = data.get('ts', 'unknown')
        if ts != 'unknown':
            try:
                dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                ts = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                pass
        
        # Extract key fields
        safety_raw = data.get('safety_raw', 'unknown')[:20] + '...' if len(str(data.get('safety_raw', ''))) > 20 else data.get('safety_raw', 'unknown')
        love = data.get('love_vector_applied', False)
        thermo = data.get('thermodynamic_adjustment', 'unknown')
        crc_raw = data.get('CRC_raw', 'null')
        
        return f"[{ts}] safety_raw={safety_raw} love={love} thermo={thermo} CRC_raw={crc_raw}"
    except Exception as e:
        return f"Error parsing line: {e}"

def main():
    # Parse command line arguments
    n = 10  # default
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print(f"Error: '{sys.argv[1]}' is not a valid number")
            sys.exit(1)
    
    log_file = 'logs/safety_decisions.jsonl'
    
    print(f"Inspecting last {n} decisions from {log_file}...")
    print()
    
    lines = read_last_n_lines(log_file, n)
    
    if not lines:
        print("No log entries found.")
        return
    
    for line in lines:
        if line.strip():
            print(format_decision_line(line))

if __name__ == '__main__':
    main()
