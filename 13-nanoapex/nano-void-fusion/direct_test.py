#!/usr/bin/env python3

import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

print('🚀 Direct Nano-Void Fusion Test')
print('=' * 40)

try:
    from nano_void import NanoVoidEngine
    print('✓ Successfully imported NanoVoidEngine')
except Exception as e:
    print(f'✗ Import failed: {e}')
    sys.exit(1)

# Check nano files before
nano_dir = Path('~/nano_memory').expanduser()
print(f'
📁 Nano directory: {nano_dir}')

if nano_dir.exists():
    before_files = list(nano_dir.glob('*.nano'))
    print(f'Files before fusion: {len(before_files)}')
    for f in sorted(before_files):
        print(f'  - {f.name}')
        with open(f, 'r') as file:
            data = json.load(file)
            essence = data.get('content', {}).get('essence', '')
            tags = data.get('meta', {}).get('tags', [])
            print(f'    Essence: {essence}')
            print(f'    Tags: {tags}')
else:
    print('nano_memory directory not found')
    sys.exit(1)

# Initialize and run fusion
print('
🌌 Initializing Nano-Void Engine...')
nve = NanoVoidEngine()

print('
⚙️ Running fusion...')
results = nve.fuse()

if results:
    print(f'
✨ Fusion generated {len(results)} insights:')
    for i, result in enumerate(results, 1):
        print(f'{i}. {result}')
else:
    print('
⚠️ No fusion results generated')

# Check files after
after_files = list(nano_dir.glob('*.nano'))
print(f'
📊 Files after fusion: {len(after_files)}')

if len(after_files) > len(before_files):
    print('✓ New files created!')
    for f in sorted(after_files):
        if f not in before_files:
            print(f'  NEW: {f.name}')
            with open(f, 'r') as file:
                data = json.load(file)
                essence = data.get('content', {}).get('essence', '')
                print(f'    Essence: {essence}')
else:
    print('⚠️ No new files created')

print('
✅ Test complete!')
