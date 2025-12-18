#!/usr/bin/env python3

# Simple test to verify target_finder works
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from target_finder import TargetFinder
    
    print("✅ TargetFinder imported successfully")
    
    # Test with rade_engine.py
    tf = TargetFinder()
    found = tf.list_functions("rade_engine.py")
    print(f"[Finder] Functions detected: {found}")
    
    # Verify we found the expected function
    if "start_rade" in found:
        print("✅ Successfully detected start_rade function!")
    else:
        print("❌ Failed to detect start_rade function")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure tree_sitter and tree_sitter_python are installed:")
    print("pip install tree-sitter tree-sitter-python")
    
except Exception as e:
    print(f"❌ Error: {e}")