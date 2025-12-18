#!/usr/bin/env python3

# Simple test to verify nano-void fusion functionality
import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from nano_void import NanoVoidEngine, NanoFileSystem
    print('✓ Successfully imported NanoVoidEngine and NanoFileSystem')
except ImportError as e:
    print(f'✗ Import failed: {e}')
    sys.exit(1)

# Test basic functionality
print('
🚀 Testing Nano-Void Fusion Engine...')
print('=' * 50)

# Check nano memory directory
nano_dir = Path('~/nano_memory').expanduser()
print(f'
📁 Nano memory directory: {nano_dir}')
print(f'Directory exists: {nano_dir.exists()}')

if nano_dir.exists():
    nano_files = list(nano_dir.glob('*.nano'))
    print(f'Found {len(nano_files)} .nano files:')
    
    for f in sorted(nano_files):
        print(f'  - {f.name}')
        try:
            with open(f, 'r') as file:
                data = json.load(file)
                essence = data.get('content', {}).get('essence', 'No essence')
                tags = data.get('meta', {}).get('tags', [])
                print(f'    Essence: {essence}')
                print(f'    Tags: {tags}')
        except Exception as e:
            print(f'    Error reading: {e}')
    
    # Test engine initialization
    print('
🌌 Initializing engine...')
    try:
        nve = NanoVoidEngine()
        print('✓ Engine initialized successfully')
    except Exception as e:
        print(f'✗ Engine initialization failed: {e}')
        sys.exit(1)
    
    # Test fusion
    print('
⚙️ Testing fusion process...')
    try:
        results = nve.fuse()
        if results:
            print(f'✓ Fusion successful! Generated {len(results)} insights:')
            for i, result in enumerate(results, 1):
                print(f'  {i}. {result[:100]}...')
        else:
            print('⚠️ No fusion results (this may be expected)')
    except Exception as e:
        print(f'✗ Fusion failed: {e}')
        import traceback
        traceback.print_exc()
    
    # Check for new files
    print('
🔍 Checking for new files...')
    new_files = list(nano_dir.glob('*.nano'))
    if len(new_files) > len(nano_files):
        print(f'✓ New files created! Total: {len(new_files)} (was {len(nano_files)})')
        for f in sorted(new_files):
            if f not in nano_files:
                print(f'  NEW: {f.name}')
    else:
        print('⚠️ No new files created')
else:
    print('✗ nano_memory directory not found')

print('
=== TEST COMPLETE ===')
