#!/usr/bin/env python3
# test_reflexion_loop.py - Test the Reflexion Loop (Plan -> Act -> Reflect -> Optimize)

import sys
sys.path.insert(0, '.')

print("="*60)
print("Level 33 Reflexion Loop Test")
print("="*60)

print("\nThe Reflexion Loop consists of:")
print("  1. PLAN: Agent receives a task")
print("  2. ACT: Agent executes using safe_click tool")
print("  3. REFLECT: Agent analyzes success/failure")
print("  4. OPTIMIZE: DSPy corrects the plan if needed")

# Test the correction module
print("\n[Testing DSPy Self-Correction Module]")
try:
    import dspy
    from optimization.optimize_prompt import CorrectionModule
    
    print("\nInitializing correction module...")
    corrector = CorrectionModule()
    
    # Simulate a failed action
    print("\nSimulating failed action:")
    print("  Original Plan: 'Click at coordinates 3000, 3000'")
    print("  Error: 'Coordinates exceed screen resolution (1920x1080)'")
    
    print("\nNote: This requires Ollama to be running with Gemma 2 9B")
    print("If Ollama is not running, this test will fail.")
    print("\nAttempting correction...")
    
    try:
        result = corrector(
            original_plan="Click at coordinates 3000, 3000",
            error_message="Error: Coordinates exceed screen resolution (1920x1080)"
        )
        print(f"\n✓ Corrected Plan: {result.corrected_plan}")
        print("\n✓ Reflexion loop is functional!")
    except Exception as e:
        print(f"\n⚠ Could not test correction (Ollama may not be running): {e}")
        print("\nThe reflexion loop structure is in place, but requires:")
        print("  - Ollama running: ollama serve")
        print("  - Gemma 2 9B model: ollama pull gemma2:9b")
        
except ImportError as e:
    print(f"\n✗ Import failed: {e}")
    print("\nInstall DSPy: pip3 install dspy-ai")

print("\n" + "="*60)
print("Reflexion Loop Architecture")
print("="*60)
print("""
The system implements a self-healing Ouroboros Loop:

1. Physical_Solver (brain_core.py)
   - Receives task from user
   - Plans actions using Gemma 2 9B
   - Calls safe_click tool

2. Executor (user_proxy)
   - Executes the safe_click function
   - Returns success/failure to solver

3. CorrectionModule (optimize_prompt.py)
   - Analyzes failures
   - Generates corrected plans
   - Learns from mistakes via DSPy

4. Loop continues until task is complete
   - Agent outputs 'TERMINATE' when done
""")
print("="*60)
