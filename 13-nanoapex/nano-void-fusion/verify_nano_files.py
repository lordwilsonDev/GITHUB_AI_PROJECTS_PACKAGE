#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from nano_void import NanoVoidEngine

def verify_nano_files():
    print('🔍 Verifying Nano Files Generation')
    print('=' * 40)
    
    nano_dir = Path('~/nano_memory').expanduser()
    
    if not nano_dir.exists():
        print('❌ nano_memory directory not found')
        return False
    
    # Get all nano files
    nano_files = list(nano_dir.glob('*.nano'))
    print(f'
📁 Found {len(nano_files)} .nano files:')
    
    valid_files = 0
    fusion_files = 0
    
    for nano_file in sorted(nano_files):
        print(f'
📄 {nano_file.name}')
        
        try:
            with open(nano_file, 'r') as f:
                data = json.load(f)
            
            # Validate structure
            if 'content' not in data or 'meta' not in data:
                print('  ❌ Invalid structure: missing content or meta')
                continue
                
            if 'essence' not in data['content']:
                print('  ❌ Invalid structure: missing essence')
                continue
                
            essence = data['content']['essence']
            meta = data['meta']
            
            print(f'  ✅ Valid structure')
            print(f'  Essence: {essence[:80]}...' if len(essence) > 80 else f'  Essence: {essence}')
            print(f'  Type: {meta.get("type", "unknown")}')
            print(f'  Tags: {meta.get("tags", [])}')
            print(f'  Created: {meta.get("created", "unknown")}')
            
            valid_files += 1
            
            # Check if it's a fusion-generated file
            if meta.get('type') == 'fusion' or 'void-engine' in meta.get('tags', []):
                fusion_files += 1
                print('  ✨ FUSION GENERATED FILE')
                
        except json.JSONDecodeError as e:
            print(f'  ❌ JSON decode error: {e}')
        except Exception as e:
            print(f'  ❌ Error reading file: {e}')
    
    print(f'
📊 Summary:')
    print(f'  Total files: {len(nano_files)}')
    print(f'  Valid files: {valid_files}')
    print(f'  Fusion-generated files: {fusion_files}')
    
    # Test fusion engine to potentially generate new files
    print(f'
🌌 Testing fusion engine...')
    try:
        nve = NanoVoidEngine()
        results = nve.fuse()
        
        if results:
            print(f'  ✨ Generated {len(results)} new insights')
            for i, result in enumerate(results, 1):
                print(f'    {i}. {result[:60]}...')
        else:
            print('  ⚠️ No new insights generated')
            
    except Exception as e:
        print(f'  ❌ Fusion engine error: {e}')
    
    # Check for new files after fusion
    new_nano_files = list(nano_dir.glob('*.nano'))
    if len(new_nano_files) > len(nano_files):
        print(f'
✨ NEW FILES CREATED! Total now: {len(new_nano_files)}')
        for f in sorted(new_nano_files):
            if f not in nano_files:
                print(f'  NEW: {f.name}')
                try:
                    with open(f, 'r') as file:
                        data = json.load(file)
                        essence = data.get('content', {}).get('essence', '')
                        print(f'    Essence: {essence[:60]}...')
                except Exception as e:
                    print(f'    Error reading: {e}')
    
    print('
✅ Verification complete!')
    return valid_files > 0

if __name__ == '__main__':
    verify_nano_files()
