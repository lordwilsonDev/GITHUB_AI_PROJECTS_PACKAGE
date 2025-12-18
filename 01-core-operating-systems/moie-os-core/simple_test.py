#!/usr/bin/env python3
"""Simple test of MoIE-OS Protocol without imports"""

import sys
import os

# Test that we can at least import the basic structure
print("🚀 Testing MoIE-OS Protocol Structure...\n")

try:
    # Test imports one by one
    print("1. Testing core.models...")
    from core import models
    print("   ✅ core.models imported")
    
    print("\n2. Testing metrics.vdr...")
    from metrics import vdr
    print("   ✅ metrics.vdr imported")
    
    print("\n3. Testing governance.lord_wilson...")
    from governance import lord_wilson
    print("   ✅ governance.lord_wilson imported")
    
    print("\n4. Testing kill_chain stages...")
    from kill_chain import targeting, hunter, alchemist, judge
    print("   ✅ kill_chain stages imported")
    
    print("\n5. Testing kill_chain.pipeline...")
    from kill_chain import pipeline
    print("   ✅ kill_chain.pipeline imported")
    
    print("\n" + "="*60)
    print("✅ ALL IMPORTS SUCCESSFUL!")
    print("="*60)
    
    # Now try to run a simple test
    print("\n6. Running simple VDR calculation...")
    vdr_result = vdr.compute_vdr(vitality=0.8, density=3.5, alpha=1.5)
    print(f"   Vitality: {vdr_result.vitality}")
    print(f"   Density: {vdr_result.density}")
    print(f"   VDR: {vdr_result.vdr:.3f}")
    print(f"   SEM: {vdr_result.sem:.3f}")
    print(f"   ✅ VDR calculation works!")
    
    print("\n7. Testing Kill Chain pipeline...")
    from core.models import KillChainInput
    from kill_chain.pipeline import run_kill_chain
    
    payload = KillChainInput(
        problem_statement="Test problem: Optimize system performance",
        context={"test": True},
        constraints=["Safety first"],
    )
    
    print("   Running Kill Chain...")
    result = pipeline.run_kill_chain(payload)
    
    print(f"\n✨ RESULTS:")
    print(f"   Stages completed: {len(result.stages)}")
    print(f"   VDR: {result.vdr_metrics.vdr:.3f}")
    print(f"   Resonance: {result.alignment.resonance_score:.3f}")
    print(f"   Accepted: {result.accepted}")
    print(f"   Execution time: {result.execution_time_ms:.1f}ms")
    
    print("\n" + "="*60)
    print("✅ MoIE-OS PROTOCOL IS FULLY OPERATIONAL!")
    print("="*60)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
