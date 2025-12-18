#!/usr/bin/env python3
import os
import sys

print("=== QUICK DIAGNOSTIC CHECK ===")
print(f"Current directory: {os.getcwd()}")
print(f"Python version: {sys.version}")
print()

print("=== FILES IN CURRENT DIRECTORY ===")
for item in sorted(os.listdir('.')):
    full_path = os.path.join('.', item)
    if os.path.isfile(full_path):
        size = os.path.getsize(full_path)
        print(f"  FILE: {item} ({size} bytes)")
    else:
        print(f"  DIR:  {item}/")
print()

print("=== LOOKING FOR PYTHON FILES ===")
py_files = [f for f in os.listdir('.') if f.endswith('.py')]
if py_files:
    print(f"Found {len(py_files)} Python files:")
    for pf in py_files:
        print(f"  - {pf}")
else:
    print("No Python files found in current directory")
print()

print("=== CHECKING FOR metadata_entity.py ===")
if os.path.exists('metadata_entity.py'):
    print("✓ metadata_entity.py EXISTS")
    print(f"  Size: {os.path.getsize('metadata_entity.py')} bytes")
    print("\n  First 50 lines:")
    with open('metadata_entity.py', 'r') as f:
        for i, line in enumerate(f, 1):
            if i <= 50:
                print(f"  {i:3d}: {line.rstrip()}")
            else:
                break
    print()
    
    print("=== SEARCHING FOR 'class Met' ===")
    with open('metadata_entity.py', 'r') as f:
        content = f.read()
        if 'class Met' in content:
            print("✓ Found 'class Met' in file")
            # Find and show the line
            for i, line in enumerate(content.split('\n'), 1):
                if 'class Met' in line:
                    print(f"  Line {i}: {line}")
        else:
            print("✗ 'class Met' NOT found in file")
    print()
    
    print("=== ATTEMPTING IMPORT ===")
    sys.path.insert(0, '.')
    try:
        import metadata_entity
        print("✓ Successfully imported metadata_entity module")
        print(f"  Module location: {metadata_entity.__file__ if hasattr(metadata_entity, '__file__') else 'unknown'}")
        print(f"  Module contents: {dir(metadata_entity)}")
        
        if hasattr(metadata_entity, 'Met'):
            print("\n✓ Met class found in module")
            Met = metadata_entity.Met
            print(f"  Met class: {Met}")
            
            try:
                instance = Met()
                print(f"  ✓ Created instance: {instance}")
                print(f"  Instance type: {type(instance)}")
                print(f"  Instance attributes: {list(instance.__dict__.keys()) if hasattr(instance, '__dict__') else 'N/A'}")
            except Exception as e:
                print(f"  ✗ Could not instantiate Met: {e}")
        else:
            print("\n✗ Met class NOT found in module")
            classes = [name for name in dir(metadata_entity) if not name.startswith('_')]
            print(f"  Available items: {classes}")
            
    except ImportError as e:
        print(f"✗ Failed to import: {e}")
        import traceback
        traceback.print_exc()
else:
    print("✗ metadata_entity.py does NOT exist")
    print("\nSearching for similar files...")
    for root, dirs, files in os.walk('.'):
        for file in files:
            if 'metadata' in file.lower() or 'entity' in file.lower():
                print(f"  Found: {os.path.join(root, file)}")
