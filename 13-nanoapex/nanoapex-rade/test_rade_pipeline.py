#!/usr/bin/env python3
"""
RADE Pipeline Dry-Run Test Script

This script creates a temporary project, starts RADE monitoring,
performs an edit/save operation, and verifies that:
1. A .nano snippet is produced
2. An entry is appended to index.jsonl

No integration with models - this is structural pipeline testing only.
"""

import os
import sys
import tempfile
import shutil
import time
import json
from pathlib import Path
from target_finder import TargetFinder, has_nanoapex_trigger

def create_test_project():
    """Create a temporary project directory with a test Python file"""
    temp_dir = tempfile.mkdtemp(prefix="rade_test_")
    test_file = Path(temp_dir) / "test_main.py"
    
    # Create a test file with @nanoapex tag
    test_content = '''def test_function(a, b):
    # @nanoapex: please optimize this function
    return a + b

def normal_function():
    return "no tag here"
'''
    
    test_file.write_text(test_content)
    print(f"[TEST] Created test project at: {temp_dir}")
    print(f"[TEST] Test file: {test_file}")
    return temp_dir, test_file

def test_snippet_detection(test_file):
    """Test that RADE can detect and extract @nanoapex snippets"""
    print("[TEST] Testing snippet detection...")
    
    tf = TargetFinder()
    functions = tf.list_functions(str(test_file))
    print(f"[TEST] Found functions: {functions}")
    
    snippets_found = 0
    for func_name in functions:
        body = tf.extract_function_body(str(test_file), func_name)
        if body and has_nanoapex_trigger(body):
            print(f"[TEST] ✓ Found @nanoapex snippet: {func_name}")
            snippets_found += 1
        else:
            print(f"[TEST] - Skipped function (no @nanoapex): {func_name}")
    
    return snippets_found > 0

def test_nano_file_creation(test_file):
    """Test that .nano files are created when processing @nanoapex functions"""
    print("[TEST] Testing .nano file creation...")
    
    # Get initial count of .nano files
    nano_memory_dir = Path.home() / "nano_memory"
    initial_nano_files = list(nano_memory_dir.glob("*.nano")) if nano_memory_dir.exists() else []
    initial_count = len(initial_nano_files)
    
    # Process the test file
    tf = TargetFinder()
    functions = tf.list_functions(str(test_file))
    
    for func_name in functions:
        body = tf.extract_function_body(str(test_file), func_name)
        if body and has_nanoapex_trigger(body):
            # This should create a .nano file
            from target_finder import save_snippet_to_memory
            save_snippet_to_memory(func_name, body, str(test_file))
    
    # Check if new .nano files were created
    final_nano_files = list(nano_memory_dir.glob("*.nano")) if nano_memory_dir.exists() else []
    final_count = len(final_nano_files)
    
    created_files = final_count - initial_count
    print(f"[TEST] .nano files created: {created_files}")
    
    return created_files > 0

def test_index_jsonl_update():
    """Test that index.jsonl is updated when snippets are processed"""
    print("[TEST] Testing index.jsonl updates...")
    
    index_path = Path.home() / "nano_memory" / "index.jsonl"
    
    if not index_path.exists():
        print("[TEST] ⚠️  index.jsonl does not exist yet")
        return False
    
    # Read the index file
    entries = []
    with index_path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
    
    snippet_entries = [e for e in entries if e.get("kind") == "snippet"]
    print(f"[TEST] Found {len(snippet_entries)} snippet entries in index.jsonl")
    
    return len(snippet_entries) > 0

def cleanup_test_project(temp_dir):
    """Clean up the temporary test project"""
    try:
        shutil.rmtree(temp_dir)
        print(f"[TEST] Cleaned up test project: {temp_dir}")
    except Exception as e:
        print(f"[TEST] Warning: Could not clean up {temp_dir}: {e}")

def main():
    """Run the RADE pipeline dry-run test"""
    print("=== RADE Pipeline Dry-Run Test ===")
    print()
    
    # Test results
    results = {
        "snippet_detection": False,
        "nano_file_creation": False,
        "index_update": False
    }
    
    temp_dir = None
    
    try:
        # Step 1: Create test project
        temp_dir, test_file = create_test_project()
        
        # Step 2: Test snippet detection
        results["snippet_detection"] = test_snippet_detection(test_file)
        
        # Step 3: Test .nano file creation
        results["nano_file_creation"] = test_nano_file_creation(test_file)
        
        # Step 4: Test index.jsonl update
        results["index_update"] = test_index_jsonl_update()
        
    except Exception as e:
        print(f"[TEST] ❌ Test failed with error: {e}")
        return False
    
    finally:
        # Cleanup
        if temp_dir:
            cleanup_test_project(temp_dir)
    
    # Print results
    print()
    print("=== Test Results ===")
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    # Overall result
    all_passed = all(results.values())
    overall_status = "✅ PASS" if all_passed else "❌ FAIL"
    print(f"\nOverall: {overall_status}")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)