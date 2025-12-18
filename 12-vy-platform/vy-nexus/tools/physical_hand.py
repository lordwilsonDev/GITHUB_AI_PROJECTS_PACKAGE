#!/usr/bin/env python3
import sys
import subprocess
import json
from datetime import datetime
import os

def log_action(action, details):
    """Log physical actions to JSONL file"""
    log_dir = os.path.expanduser('~/vy-nexus/physical_agency')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'physical_actions.jsonl')
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'details': details
    }
    
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

def click(x, y):
    """Execute a click at coordinates"""
    try:
        subprocess.run(['cliclick', 'c:' + str(x) + ',' + str(y)], check=True)
        log_action('click', {'x': x, 'y': y})
        print(f"Clicked at ({x}, {y})")
        return True
    except Exception as e:
        print(f"Click failed: {e}", file=sys.stderr)
        return False

def type_text(text):
    """Type text"""
    try:
        subprocess.run(['cliclick', 't:' + text], check=True)
        log_action('type', {'text': text})
        print(f"Typed: {text}")
        return True
    except Exception as e:
        print(f"Type failed: {e}", file=sys.stderr)
        return False

def open_app(app_name):
    """Open an application"""
    try:
        subprocess.run(['open', '-a', app_name], check=True)
        log_action('open', {'app': app_name})
        print(f"Opened: {app_name}")
        return True
    except Exception as e:
        print(f"Open failed: {e}", file=sys.stderr)
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: physical_hand.py <action> [args...]", file=sys.stderr)
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == 'click' and len(sys.argv) == 4:
        click(sys.argv[2], sys.argv[3])
    elif action == 'type' and len(sys.argv) == 3:
        type_text(sys.argv[2])
    elif action == 'open' and len(sys.argv) == 3:
        open_app(sys.argv[2])
    else:
        print(f"Unknown action or invalid arguments: {action}", file=sys.stderr)
        sys.exit(1)
