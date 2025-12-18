#!/usr/bin/env python3
# test_full_stack.py - Integration test for Level 33 Sovereign Architecture

import sys
sys.path.insert(0, '.')

print("="*60)
print("Level 33 Sovereign Architecture - Full Stack Test")
print("="*60)

# Test 1: Import all components
print("\n[Test 1] Importing components...")
try:
    from architecture.brain_core import solver, user_proxy, config_list
    from tools.physical_hand import safe_click
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Verify configuration
print("\n[Test 2] Verifying configuration...")
try:
    assert solver.name == "Physical_Solver"
    assert user_proxy.name == "Executor"
    assert config_list[0]['model'] == "gemma2:9b"
    assert user_proxy._code_execution_config.get('use_docker') == False
    print("✓ Configuration verified")
    print(f"  - Docker disabled: {user_proxy._code_execution_config.get('use_docker') == False}")
    print(f"  - Model: {config_list[0]['model']}")
    print(f"  - Base URL: {config_list[0]['base_url']}")
except AssertionError as e:
    print(f"✗ Configuration check failed: {e}")
    sys.exit(1)

# Test 3: Test physical_hand tool
print("\n[Test 3] Testing physical_hand tool...")
try:
    # Test with invalid coordinates (should return error)
    result = safe_click(-10, -10, confirm=False)
    assert "Error" in result
    print("✓ Physical hand tool working (negative coordinate check passed)")
except Exception as e:
    print(f"✗ Physical hand test failed: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check Ollama connection
print("\n[Test 4] Checking Ollama connection...")
try:
    import requests
    response = requests.get('http://localhost:11434/api/tags', timeout=5)
    if response.status_code == 200:
        print("✓ Ollama is running")
        models = response.json().get('models', [])
        gemma_found = any('gemma2:9b' in str(m.get('name', '')) for m in models)
        if gemma_found:
            print("✓ Gemma 2 9B model found")
        else:
            print("⚠ Gemma 2 9B model not found. Run: ollama pull gemma2:9b")
    else:
        print("⚠ Ollama responded but with unexpected status")
except requests.exceptions.ConnectionError:
    print("⚠ Ollama is not running. Start it with: ollama serve")
except Exception as e:
    print(f"⚠ Could not check Ollama: {e}")

# Test 5: DSPy module check
print("\n[Test 5] Checking DSPy optimization module...")
try:
    import dspy
    from optimization.optimize_prompt import CorrectionModule
    print("✓ DSPy module imports successfully")
except Exception as e:
    print(f"⚠ DSPy check failed: {e}")
    print("  Install with: pip3 install dspy-ai")

print("\n" + "="*60)
print("Test Summary")
print("="*60)
print("\nCore Fix Applied:")
print("  ✓ Docker requirement disabled in brain_core.py")
print("\nNext Steps:")
print("  1. Ensure Ollama is running: ollama serve")
print("  2. Pull Gemma 2 9B model: ollama pull gemma2:9b")
print("  3. Install dependencies: pip3 install pyautogen dspy-ai requests")
print("  4. Install cliclick: brew install cliclick")
print("\nTo run the agent:")
print("  cd ~/level33_sovereign")
print("  python3 architecture/brain_core.py")
print("\n" + "="*60)
