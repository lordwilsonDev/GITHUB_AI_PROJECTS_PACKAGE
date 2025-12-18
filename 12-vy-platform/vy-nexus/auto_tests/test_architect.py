#!/usr/bin/env python3
"""
Auto-generated test for architect
Generated: 2025-12-18 12:53:21
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_import():
    """Test that module can be imported"""
    try:
        import architect
        print("✅ Import successful")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_module_attributes():
    """Test that module has expected structure"""
    try:
        import architect
        
        # Check for main function or class
        has_main = hasattr(architect, 'main')
        has_class = any(
            hasattr(architect, attr) and 
            type(getattr(architect, attr)).__name__ == 'type'
            for attr in dir(architect)
            if not attr.startswith('_')
        )
        
        if has_main or has_class:
            print("✅ Module structure valid")
            return True
        else:
            print("⚠️  No main function or class found")
            return False
            
    except Exception as e:
        print(f"❌ Structure check failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print(f"Testing: architect")
    print("="*60)
    
    results = []
    
    print("\n1. Import Test")
    results.append(test_import())
    
    print("\n2. Structure Test")
    results.append(test_module_attributes())
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"Results: {passed}/{total} tests passed")
    print("="*60)
    
    sys.exit(0 if all(results) else 1)
