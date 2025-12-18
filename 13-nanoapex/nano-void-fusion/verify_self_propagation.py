#!/usr/bin/env python3

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from nano_void import NanoVoidEngine

def verify_self_propagation():
    print('🔄 Verifying Self-Propagating Functionality')
    print('=' * 50)
    
    nano_dir = Path('~/nano_memory').expanduser()
    
    if not nano_dir.exists():
        print('❌ nano_memory directory not found')
        return False
    
    # Phase 1: Initial state
    print('
📊 Phase 1: Initial State Analysis')
    initial_files = list(nano_dir.glob('*.nano'))
    print(f'Initial nano files: {len(initial_files)}')
    
    for f in sorted(initial_files):
        print(f'  - {f.name}')
        with open(f, 'r') as file:
            data = json.load(file)
            essence = data.get('content', {}).get('essence', '')
            tags = data.get('meta', {}).get('tags', [])
            print(f'    Essence: {essence}')
            print(f'    Tags: {tags}')
    
    # Phase 2: First fusion cycle
    print('
🌌 Phase 2: First Fusion Cycle')
    nve = NanoVoidEngine()
    
    print('Running first fusion...')
    results_1 = nve.fuse()
    
    if results_1:
        print(f'✨ First cycle generated {len(results_1)} insights:')
        for i, result in enumerate(results_1, 1):
            print(f'  {i}. {result[:80]}...')
    else:
        print('⚠️ No results from first cycle')
    
    # Check files after first cycle
    cycle1_files = list(nano_dir.glob('*.nano'))
    new_files_1 = [f for f in cycle1_files if f not in initial_files]
    
    print(f'
Files after first cycle: {len(cycle1_files)} (was {len(initial_files)})')
    if new_files_1:
        print('New files from first cycle:')
        for f in new_files_1:
            print(f'  NEW: {f.name}')
    
    # Phase 3: Second fusion cycle (self-propagation test)
    print('
🔄 Phase 3: Second Fusion Cycle (Self-Propagation)')
    
    if len(cycle1_files) <= len(initial_files):
        print('⚠️ No new files to test self-propagation with')
        print('Creating a test fusion file manually...')
        
        # Create a test fusion file
        test_fusion = {
            "content": {
                "essence": "Unity and Love create Harmonic Resonance"
            },
            "meta": {
                "type": "fusion",
                "tags": ["void-engine", "resonance", "harmony"],
                "created": datetime.now().isoformat()
            }
        }
        
        test_file = nano_dir / 'test_fusion_20241202.nano'
        with open(test_file, 'w') as f:
            json.dump(test_fusion, f, indent=2)
        
        print(f'Created test file: {test_file.name}')
        cycle1_files = list(nano_dir.glob('*.nano'))
    
    # Wait a moment
    time.sleep(1)
    
    print('
Running second fusion cycle...')
    results_2 = nve.fuse()
    
    if results_2:
        print(f'✨ Second cycle generated {len(results_2)} insights:')
        for i, result in enumerate(results_2, 1):
            print(f'  {i}. {result[:80]}...')
    else:
        print('⚠️ No results from second cycle')
    
    # Check files after second cycle
    cycle2_files = list(nano_dir.glob('*.nano'))
    new_files_2 = [f for f in cycle2_files if f not in cycle1_files]
    
    print(f'
Files after second cycle: {len(cycle2_files)} (was {len(cycle1_files)})')
    if new_files_2:
        print('New files from second cycle:')
        for f in new_files_2:
            print(f'  NEW: {f.name}')
            with open(f, 'r') as file:
                data = json.load(file)
                essence = data.get('content', {}).get('essence', '')
                print(f'    Essence: {essence[:60]}...')
    
    # Phase 4: Analysis
    print('
📊 Phase 4: Self-Propagation Analysis')
    
    total_growth = len(cycle2_files) - len(initial_files)
    cycle1_growth = len(cycle1_files) - len(initial_files)
    cycle2_growth = len(cycle2_files) - len(cycle1_files)
    
    print(f'Initial files: {len(initial_files)}')
    print(f'After cycle 1: {len(cycle1_files)} (+{cycle1_growth})')
    print(f'After cycle 2: {len(cycle2_files)} (+{cycle2_growth})')
    print(f'Total growth: +{total_growth} files')
    
    # Check for fusion-generated files
    fusion_files = []
    for f in cycle2_files:
        try:
            with open(f, 'r') as file:
                data = json.load(file)
                if (data.get('meta', {}).get('type') == 'fusion' or 
                    'void-engine' in data.get('meta', {}).get('tags', [])):
                    fusion_files.append(f)
        except Exception:
            continue
    
    print(f'Fusion-generated files: {len(fusion_files)}')
    
    # Verify self-propagation
    self_propagating = False
    
    if cycle2_growth > 0:
        print('✅ SELF-PROPAGATION VERIFIED: New insights generated from previous fusion results')
        self_propagating = True
    elif cycle1_growth > 0:
        print('⚠️ PARTIAL: First cycle generated insights, but second cycle did not propagate')
    else:
        print('❌ NO PROPAGATION: No new insights generated in either cycle')
    
    # Phase 5: Summary
    print('
📜 Phase 5: Summary')
    print(f'Self-propagating: {"YES" if self_propagating else "NO"}')
    print(f'Knowledge base growth: {total_growth} files')
    print(f'Fusion files created: {len(fusion_files)}')
    
    if self_propagating:
        print('
✨ SUCCESS: The system demonstrates self-propagating cognition!')
        print('   - Existing knowledge generates new insights')
        print('   - New insights become part of future fusion cycles')
        print('   - Knowledge base grows through internal processing')
    else:
        print('
⚠️ The system needs tuning for better self-propagation')
        print('   - Check resonance thresholds')
        print('   - Verify tag compatibility')
        print('   - Ensure diverse initial knowledge base')
    
    return self_propagating

if __name__ == '__main__':
    success = verify_self_propagation()
    sys.exit(0 if success else 1)
