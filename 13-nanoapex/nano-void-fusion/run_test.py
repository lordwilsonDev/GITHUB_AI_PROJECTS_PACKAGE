#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from nano_void import NanoVoidEngine

if __name__ == '__main__':
    print('🚀 Testing Nano-Void Fusion Engine...')
    print('=' * 50)
    
    # Initialize engine
    nve = NanoVoidEngine()
    
    # Run fusion
    results = nve.fuse()
    
    if results:
        print('
⚡ Fused Insights Generated:')
        for i, res in enumerate(results, 1):
            print(f'{i}. {res}')
    else:
        print('
🔄 No fusion results generated.')
    
    print('
📁 Checking nano_memory directory:')
    nano_dir = Path('~/nano_memory').expanduser()
    if nano_dir.exists():
        nano_files = list(nano_dir.glob('*.nano'))
        print(f'Found {len(nano_files)} .nano files:')
        for f in sorted(nano_files):
            print(f'  - {f.name}')
    else:
        print('nano_memory directory not found')
