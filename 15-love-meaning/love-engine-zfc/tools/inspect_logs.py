#!/usr/bin/env python3
"""
CLI tool to inspect and label Love Engine decisions for MiniMind training
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

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
        ts = data.get('timestamp', 'unknown')
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
        human_ok = data.get('human_ok', None)
        
        status = "UNLABELED" if human_ok is None else ("OK" if human_ok else "BAD")
        
        return f"[{ts}] safety={safety_raw} love={love} thermo={thermo} status={status}"
    except Exception as e:
        return f"Error parsing line: {e}"

def update_log_entry(log_file, line_index, human_ok, human_better_answer=None):
    """Update a log entry with human feedback"""
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    if line_index >= len(lines):
        print(f"Error: Line index {line_index} out of range")
        return False
    
    try:
        data = json.loads(lines[line_index].strip())
        data['human_ok'] = human_ok
        if human_better_answer:
            data['human_better_answer'] = human_better_answer
        
        lines[line_index] = json.dumps(data) + '\n'
        
        with open(log_file, 'w') as f:
            f.writelines(lines)
        
        return True
    except Exception as e:
        print(f"Error updating entry: {e}")
        return False

def label_mode(log_file):
    """Interactive labeling mode for training data generation"""
    print("=== LOVE ENGINE LABELING MODE ===")
    print("Commands: ok, bad, better <text>, skip, quit")
    print()
    
    lines = read_last_n_lines(log_file, 50)  # Show last 50 entries
    unlabeled = []
    
    for i, line in enumerate(lines):
        if line.strip():
            try:
                data = json.loads(line.strip())
                if data.get('human_ok') is None:
                    unlabeled.append((i, data))
            except:
                continue
    
    if not unlabeled:
        print("No unlabeled entries found!")
        return
    
    print(f"Found {len(unlabeled)} unlabeled entries\n")
    
    for idx, (line_idx, data) in enumerate(unlabeled):
        print(f"=== Entry {idx+1}/{len(unlabeled)} ===")
        print(f"Message: {data.get('message', 'N/A')}")
        print(f"Answer: {data.get('answer', 'N/A')}")
        print(f"Safety: {data.get('safety_raw', 'N/A')}")
        print(f"Love Applied: {data.get('love_vector_applied', False)}")
        print()
        
        while True:
            cmd = input("Label (ok/bad/better <text>/skip/quit): ").strip()
            
            if cmd == 'quit':
                return
            elif cmd == 'skip':
                break
            elif cmd == 'ok':
                if update_log_entry(log_file, line_idx, True):
                    print("✓ Marked as OK")
                break
            elif cmd == 'bad':
                if update_log_entry(log_file, line_idx, False):
                    print("✗ Marked as BAD")
                break
            elif cmd.startswith('better '):
                better_text = cmd[7:]
                if update_log_entry(log_file, line_idx, False, better_text):
                    print(f"✓ Marked as BAD with better answer: {better_text[:50]}...")
                break
            else:
                print("Invalid command. Use: ok, bad, better <text>, skip, quit")

def main():
    # Parse command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == '--label':
        log_file = 'love_logs.jsonl'
        label_mode(log_file)
        return
    
    n = 10  # default
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except ValueError:
            print(f"Error: '{sys.argv[1]}' is not a valid number")
            print("Usage: python inspect_logs.py [N] or python inspect_logs.py --label")
            sys.exit(1)
    
    log_file = 'love_logs.jsonl'
    
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