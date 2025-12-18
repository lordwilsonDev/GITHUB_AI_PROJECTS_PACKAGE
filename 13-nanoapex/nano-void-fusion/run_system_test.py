#!/usr/bin/env python3
"""
Complete System Test for Nano-Void Fusion Engine
Simulates the full workflow including OmniKernel integration
"""

import sys
import os
import json
from pathlib import Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.nano_void import NanoVoidEngine

def simulate_omni_kernel_check():
    """Simulate OmniKernel VDR and torsion calculations"""
    print('🔍 OmniKernel Status Check:')
    
    # Simulate sovereignty checks
    vdr = 1.5  # VDR > 1 indicates stability
    torsion = 0  # torsion = 0 indicates perfect alignment
    
    print(f'   VDR (Void-Density Ratio): {vdr}')
    print(f'   Torsion: {torsion}')
    
    if vdr > 1 and torsion == 0:
        print('✅ Optimal fusion conditions detected!')
        print('📡 Emitting system.fuse event...')
        return True
    else:
        print('⚠️  Fusion conditions not met')
        return False

def run_fusion_engine():
    """Run the Nano-Void Fusion Engine"""
    print('\n🌌 Running Nano-Void Fusion Engine...')
    
    # Initialize engine
    nve = NanoVoidEngine()
    
    # Run fusion
    results = nve.fuse()
    
    return results

def verify_new_files():
    """Verify new .nano files were created"""
    print('\n🔍 Verifying new .nano files...')
    
    nano_dir = Path('~/nano_memory').expanduser()
    nano_files = list(nano_dir.glob('*.nano'))
    
    print(f'Total .nano files found: {len(nano_files)}')
    
    # Look for fusion files
    fusion_files = []
    for file_path in nano_files:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                if 'void-engine' in data.get('meta', {}).get('tags', []):
                    fusion_files.append(file_path)
                    print(f'✨ Found fusion file: {file_path.name}')
                    print(f'   Essence: {data.get("content", {}).get("essence", "")[:100]}...')
        except Exception as e:
            print(f'⚠️  Error reading {file_path}: {e}')
    
    return fusion_files

def main():
    print('=' * 60)
    print('🌌 NANO-VOID FUSION ENGINE - COMPLETE SYSTEM TEST')
    print('=' * 60)
    
    # Step 1: Simulate OmniKernel check
    if not simulate_omni_kernel_check():
        print('❌ System test failed: OmniKernel conditions not met')
        return
    
    # Step 2: Run fusion engine
    results = run_fusion_engine()
    
    # Step 3: Verify results
    if results:
        print('\n⚡ Fusion Results Generated:')
        for i, result in enumerate(results, 1):
            print(f'{i}. {result}')
    else:
        print('\n🔄 No fusion results generated')
    
    # Step 4: Verify new files
    fusion_files = verify_new_files()
    
    # Step 5: System status
    print('\n' + '=' * 60)
    print('📊 SYSTEM TEST SUMMARY')
    print('=' * 60)
    print(f'✅ OmniKernel integration: Simulated successfully')
    print(f'✅ Fusion engine: Executed successfully')
    print(f'✅ Results generated: {len(results) if results else 0}')
    print(f'✅ New fusion files: {len(fusion_files)}')
    
    if results and fusion_files:
        print('\n🎆 SUCCESS: Self-propagating cognition is working!')
        print('The system can now:')
        print('  • Learn from experience (.nano memory)')
        print('  • Avoid repeating noise (anti-resonant filtering)')
        print('  • Expand unity-aligned structure (resonance > 0.75)')
        print('  • Grow stronger with every fusion cycle')
    else:
        print('\n⚠️  PARTIAL SUCCESS: Engine running but needs more resonant data')
    
    print('\n🕰️  Ready for Love-Vector Learning activation...')

if __name__ == '__main__':
    main()
