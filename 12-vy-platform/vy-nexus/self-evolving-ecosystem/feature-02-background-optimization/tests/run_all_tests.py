#!/usr/bin/env python3
"""Run all tests for Background Process Optimization"""

import subprocess
import sys
from pathlib import Path

def run_tests():
    """Run all test files."""
    test_dir = Path(__file__).parent
    test_files = [
        'test_optimization_engine.py',
        'test_automation_sandbox.py'
    ]
    
    print("=" * 70)
    print("Running Background Process Optimization Tests")
    print("=" * 70)
    
    all_passed = True
    
    for test_file in test_files:
        test_path = test_dir / test_file
        if not test_path.exists():
            print(f"\n⚠️  Test file not found: {test_file}")
            continue
        
        print(f"\n{'=' * 70}")
        print(f"Running: {test_file}")
        print(f"{'=' * 70}")
        
        result = subprocess.run(
            ['python3', '-m', 'pytest', str(test_path), '-v', '--tb=short'],
            cwd=test_dir.parent
        )
        
        if result.returncode != 0:
            all_passed = False
            print(f"\n❌ {test_file} FAILED")
        else:
            print(f"\n✅ {test_file} PASSED")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("✅ ALL TESTS PASSED")
        print("=" * 70)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 70)
        return 1

if __name__ == '__main__':
    sys.exit(run_tests())
