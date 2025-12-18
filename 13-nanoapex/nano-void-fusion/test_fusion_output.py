#!/usr/bin/env python3

import sys
import os
import json
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from nano_void import NanoVoidEngine

def test_fusion():
    print('🚀 Testing Nano-Void Fusion Engine...')
    print('=' * 50)
    
    # Check existing nano files first
    nano_dir = Path('~/nano_memory').expanduser()
    print(f'
📁 Nano memory directory: {nano_dir}')
    
    if nano_dir.exists():
        nano_files = list(nano_dir.glob('*.nano'))
        print(f'Found {len(nano_files)} existing .nano files:')
        for f in sorted(nano_files):
            print(f'  - {f.name}')
            # Show content
            try:
                with open(f, 'r') as file:
                    data = json.load(file)
                    essence = data.get('content', {}).get('essence', 'No essence')
                    tags = data.get('meta', {}).get('tags', [])
                    print(f'    Essence: {essence}')
                    print(f'    Tags: {tags}')
            except Exception as e:
                print(f'    Error reading file: {e}')
    else:
        print('nano_memory directory not found')
        return
    
    print('
🌌 Initializing Nano-Void Engine...')
    nve = NanoVoidEngine()
    
    print('
⚙️ Running fusion process...')
    results = nve.fuse()
    
    if results:
        print('
⚡ Fused Insights Generated:')
        for i, res in enumerate(results, 1):
            print(f'{i}. {res}')
    else:
        print('
🔄 No fusion results generated.')
    
    # Check for new files
    print('
🔍 Checking for new .nano files...')
    new_files = list(nano_dir.glob('*.nano'))
    if len(new_files) > len(nano_files):
        print(f'New files created! Total: {len(new_files)} (was {len(nano_files)})')
        for f in sorted(new_files):
            if f not in nano_files:
                print(f'  NEW: {f.name}')
    else:
        print('No new files created.')
    
    print('
=== TEST COMPLETE ===')

if __name__ == '__main__':
    test_fusion()
