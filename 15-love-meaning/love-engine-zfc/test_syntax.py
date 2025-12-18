#!/usr/bin/env python3
"""
Syntax validation for ZFC Shell components
"""

import ast
import sys
from pathlib import Path

def test_syntax(file_path):
    """Test if a Python file has valid syntax"""
    try:
        with open(file_path, 'r') as f:
            source = f.read()
        
        ast.parse(source)
        print(f"✓ {file_path.name}: Valid syntax")
        return True
    except SyntaxError as e:
        print(f"✗ {file_path.name}: Syntax error - {e}")
        return False
    except Exception as e:
        print(f"⚠ {file_path.name}: Error - {e}")
        return False

def main():
    print("🔍 TESTING ZFC SHELL SYNTAX")
    print("=" * 40)
    
    files_to_test = [
        Path('main.py'),
        Path('start_zfc.py'),
        Path('tools/inspect_logs.py'),
        Path('minimind/extract_dataset.py'),
        Path('minimind/train_minimind.py'),
        Path('tests/test_zfc_engine.py'),
        Path('tests/test_safety_scenarios.py')
    ]
    
    results = []
    for file_path in files_to_test:
        if file_path.exists():
            result = test_syntax(file_path)
            results.append((file_path.name, result))
        else:
            print(f"⚠ {file_path.name}: File not found")
            results.append((file_path.name, False))
    
    print("\n=== SYNTAX TEST RESULTS ===")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for filename, result in results:
        status = "PASS" if result else "FAIL"
        print(f"  {filename}: {status}")
    
    print(f"\nOverall: {passed}/{total} files passed syntax validation")
    
    if passed == total:
        print("🎉 All files have valid syntax!")
        return True
    else:
        print("⚠ Some files have syntax errors")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)