#!/usr/bin/env python3
import subprocess
import sys
import os

os.chdir('/Users/lordwilson/vy-nexus/aegis-rust')

print('=== Building Intent Firewall ===')
result = subprocess.run(['cargo', 'build', '-p', 'intent-firewall'], 
                       capture_output=True, text=True, timeout=180)

print(result.stdout)
if result.stderr:
    print('STDERR:', result.stderr)

if result.returncode != 0:
    print(f'Build failed with exit code {result.returncode}')
    sys.exit(1)

print('\n=== Running Intent Firewall Tests ===')
result = subprocess.run(['cargo', 'test', '-p', 'intent-firewall', '--', '--nocapture'], 
                       capture_output=True, text=True, timeout=180)

print(result.stdout)
if result.stderr:
    print('STDERR:', result.stderr)

if result.returncode != 0:
    print(f'Tests failed with exit code {result.returncode}')
    sys.exit(1)

print('\n=== SUCCESS: All builds and tests passed ===')
