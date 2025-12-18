#!/bin/bash
# First, let's see where we are and what's here
cd /Users/lordwilson/metadata-universe
echo "=== CURRENT DIRECTORY STRUCTURE ==="
ls -la
echo ""

echo "=== PYTHON ENVIRONMENT CHECK ==="
python3 --version
pip3 list | grep -E "(metadata|pydantic|fastapi|sqlalchemy)" || echo "No relevant packages found"
echo ""

echo "=== CHECK IF MODULE EXISTS ==="
python3 -c "import sys; print('Python path:', sys.path)"
echo ""

echo "=== ATTEMPT TO LOAD THE METADATA_ENTITY MODULE ==="
python3 -c "
try:
    import metadata_entity
    print('✓ metadata_entity module loads successfully')
    
    # Try to list what's in it
    import inspect
    members = inspect.getmembers(metadata_entity)
    print(f'Module has {len(members)} members')
    
    # Check for Met class specifically
    if hasattr(metadata_entity, 'Met'):
        print('✓ Met class exists in metadata_entity')
    else:
        print('✗ Met class NOT found in metadata_entity')
        print('Available classes:', [name for name, obj in members if inspect.isclass(obj)])
        
except ImportError as e:
    print(f'✗ Failed to import metadata_entity: {e}')
    print('Looking for Python files...')
    import os
    py_files = [f for f in os.listdir('.') if f.endswith('.py')]
    print(f'Python files in current directory: {py_files}')
    
    # Check for file directly
    if 'metadata_entity.py' in py_files:
        print('Found metadata_entity.py file, checking contents...')
        with open('metadata_entity.py', 'r') as f:
            first_lines = [next(f) for _ in range(10)]
        print('First 10 lines:', first_lines)
"
echo ""

# If the file exists, let's examine it more closely
if [ -f "metadata_entity.py" ]; then
    echo "=== ANALYZING metadata_entity.py ==="
    echo "Line count:" && wc -l metadata_entity.py
    echo ""
    echo "Looking for class definitions:"
    grep -n "class " metadata_entity.py
    echo ""
    
    # Check for Met class specifically
    if grep -q "class Met" metadata_entity.py; then
        echo "✓ Found 'class Met' definition"
        # Show the class definition
        echo "Met class definition context:"
        grep -A 10 "class Met" metadata_entity.py
    else
        echo "✗ No 'class Met' found in the file"
        echo "Looking for similar classes:"
        grep -i "class.*met" metadata_entity.py || echo "No class containing 'met' found"
    fi
fi

echo "=== CHECKING FOR RELATED FILES ==="
find . -name "*.py" -type f | head -20
echo ""

echo "=== CHECKING IMPORTS AND DEPENDENCIES ==="
if [ -f "requirements.txt" ]; then
    echo "Requirements.txt found:"
    cat requirements.txt
    echo ""
elif [ -f "setup.py" ]; then
    echo "setup.py found:"
    grep -i "install_requires" setup.py
    echo ""
fi

echo "=== TEST DIRECT IMPORT WITH FULL PATH ==="
python3 -c "
import sys
sys.path.insert(0, '.')  # Add current directory to path

try:
    # Try different import styles
    print('Attempt 1: Direct import')
    from metadata_entity import Met
    print('✓ Success! Met class imported')
    
    # Try to instantiate it
    try:
        m = Met()
        print(f'✓ Met instance created: {m}')
        
        # Check its methods
        if hasattr(m, '__dict__'):
            print(f'Met instance attributes: {m.__dict__.keys()}')
        
    except Exception as e:
        print(f'✗ Could not instantiate Met: {e}')
        
except ImportError as e:
    print(f'✗ Import failed: {e}')
    
    print('\\nAttempt 2: Import module first')
    try:
        import metadata_entity as me
        print(f'Module imported: {me}')
        print('Module contents:', dir(me))
    except Exception as e2:
        print(f'✗ Module import failed: {e2}')
        
    print('\\nAttempt 3: Check if file exists and is readable')
    import os
    if os.path.exists('metadata_entity.py'):
        print('File exists, checking readability...')
        try:
            with open('metadata_entity.py', 'r') as f:
                content = f.read(500)
                print(f'First 500 chars: {content[:500]}...')
        except Exception as e3:
            print(f'✗ Cannot read file: {e3}')
    else:
        print('✗ metadata_entity.py does not exist in current directory')
        print('Current files:')
        for f in os.listdir('.'):
            if f.endswith('.py'):
                print(f'  - {f}')
"
echo ""

echo "=== CHECKING FOR __init__.py FILES ==="
find . -name "__init__.py" -type f | head -10
echo ""

echo "=== ALTERNATIVE APPROACH: RUN AS MODULE ==="
python3 -m metadata_entity 2>&1 | head -20 || echo "Could not run as module"
echo ""

echo "=== FINAL DIAGNOSTIC SUMMARY ==="
echo "To fix potential issues, try:"
echo "1. Ensure you're in the correct directory: /Users/lordwilson/metadata-universe"
echo "2. Check if metadata_entity.py actually contains 'class Met'"
echo "3. Try: python3 -c 'import sys; sys.path.append(\".\"); from metadata_entity import Met; print(Met)'"
echo "4. If it's a package, try: python3 -c 'from .metadata_entity import Met'"
echo "5. Check Python version compatibility"
