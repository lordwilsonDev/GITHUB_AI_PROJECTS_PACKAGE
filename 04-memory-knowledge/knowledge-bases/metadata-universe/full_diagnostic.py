#!/usr/bin/env python3
import os
import sys
import subprocess

print("=== METADATA UNIVERSE SYSTEM DIAGNOSTIC ===")
print(f"Working directory: {os.getcwd()}")
print(f"Python: {sys.version}")
print()

# Check all files including hidden
print("=== ALL FILES (including hidden) ===")
try:
    result = subprocess.run(['ls', '-la'], capture_output=True, text=True, cwd='/Users/lordwilson/metadata-universe')
    print(result.stdout)
except Exception as e:
    print(f"Error: {e}")
    # Fallback to Python
    for item in os.listdir('/Users/lordwilson/metadata-universe'):
        print(f"  {item}")
print()

# Find all Python files
print("=== SEARCHING FOR PYTHON FILES ===")
for root, dirs, files in os.walk('/Users/lordwilson/metadata-universe'):
    for file in files:
        if file.endswith('.py'):
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, '/Users/lordwilson/metadata-universe')
            size = os.path.getsize(full_path)
            print(f"  {rel_path} ({size} bytes)")
print()

# Check for metadata_entity.py specifically
metadata_entity_path = '/Users/lordwilson/metadata-universe/metadata_entity.py'
print("=== CHECKING FOR metadata_entity.py ===")
if os.path.exists(metadata_entity_path):
    print("✓ FILE EXISTS")
    print(f"  Size: {os.path.getsize(metadata_entity_path)} bytes")
    print()
    print("  Content preview (first 100 lines):")
    with open(metadata_entity_path, 'r') as f:
        for i, line in enumerate(f, 1):
            if i <= 100:
                print(f"    {i:3d}: {line.rstrip()}")
            else:
                print(f"    ... ({sum(1 for _ in f) + 100} total lines)")
                break
    print()
    
    # Search for class Met
    print("  Searching for 'class Met':")
    with open(metadata_entity_path, 'r') as f:
        for i, line in enumerate(f, 1):
            if 'class Met' in line:
                print(f"    Line {i}: {line.strip()}")
    print()
    
    # Try to import
    print("=== ATTEMPTING IMPORT ===")
    sys.path.insert(0, '/Users/lordwilson/metadata-universe')
    try:
        import metadata_entity
        print("✓ Import successful")
        print(f"  Module: {metadata_entity}")
        print(f"  Location: {getattr(metadata_entity, '__file__', 'unknown')}")
        print(f"  Contents: {[x for x in dir(metadata_entity) if not x.startswith('_')]}")
        
        if hasattr(metadata_entity, 'Met'):
            print("\n✓ Met class found")
            Met = metadata_entity.Met
            print(f"  Class: {Met}")
            print(f"  MRO: {Met.__mro__}")
            
            # Try instantiation
            try:
                obj = Met()
                print(f"\n✓ Instance created: {obj}")
                print(f"  Type: {type(obj)}")
                if hasattr(obj, '__dict__'):
                    print(f"  Attributes: {list(obj.__dict__.keys())}")
                methods = [m for m in dir(obj) if not m.startswith('_') and callable(getattr(obj, m))]
                print(f"  Methods: {methods[:10]}" + (" ..." if len(methods) > 10 else ""))
            except TypeError as e:
                print(f"\n⚠ Met() requires arguments: {e}")
                print("  Checking __init__ signature...")
                import inspect
                sig = inspect.signature(Met.__init__)
                print(f"  Signature: {sig}")
            except Exception as e:
                print(f"\n✗ Instantiation failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("\n✗ Met class NOT found in module")
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("✗ FILE DOES NOT EXIST")
    print("\n  Searching for similar files...")
    for root, dirs, files in os.walk('/Users/lordwilson/metadata-universe'):
        for file in files:
            if 'metadata' in file.lower() or 'entity' in file.lower() or 'met' in file.lower():
                print(f"    {os.path.join(root, file)}")

print("\n=== DIAGNOSTIC COMPLETE ===")
