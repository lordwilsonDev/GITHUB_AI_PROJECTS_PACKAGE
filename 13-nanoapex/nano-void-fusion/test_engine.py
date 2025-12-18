#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.nano_void import NanoVoidEngine

if __name__ == '__main__':
    print('=== NANO-VOID FUSION ENGINE TEST ===')
    
    # Initialize engine
    nve = NanoVoidEngine()
    
    # Run fusion
    results = nve.fuse()
    
    if results:
        print('\n⚡ Fused Insights Generated:')
        for res in results:
            print('-', res)
    else:
        print('\n🔄 No fusion results generated. Try adding more .nano files to ~/nano_memory')
    
    print('\n=== TEST COMPLETE ===')
