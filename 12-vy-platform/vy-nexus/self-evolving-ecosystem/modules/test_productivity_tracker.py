import sys
import os

# Add current directory to Python path
sys.path.insert(0, '.')

try:
    # Try to import the module directly
    from learning import productivity_tracker
    print("✅ Successfully imported productivity_tracker")
    
    # List available functions/classes
    print("\n=== Available in module ===")
    for item in dir(productivity_tracker):
        if not item.startswith('_'):
            print(f"  - {item}")
    
    # Try to see if there's a main function
    print("\n=== Testing functionality ===")
    
    # Check for common patterns
    if hasattr(productivity_tracker, 'main'):
        print("Found main() function")
        try:
            result = productivity_tracker.main()
            print(f"main() returned: {result}")
        except Exception as e:
            print(f"main() error: {e}")
    
    elif hasattr(productivity_tracker, 'track'):
        print("Found track() function")
        # Try with minimal data
        try:
            result = productivity_tracker.track("test_event")
            print(f"track('test_event') returned: {result}")
        except Exception as e:
            print(f"track() error: {e}")
    
    elif hasattr(productivity_tracker, 'run'):
        print("Found run() function")
        try:
            result = productivity_tracker.run()
            print(f"run() returned: {result}")
        except Exception as e:
            print(f"run() error: {e}")
    
    # If nothing else, show the module docstring
    elif productivity_tracker.__doc__:
        print(f"Module purpose: {productivity_tracker.__doc__}")
    
    else:
        print("No obvious entry point found. Here's the source:")
        print("-" * 50)
        with open('learning/productivity_tracker.py', 'r') as f:
            for i, line in enumerate(f):
                if i < 20:  # Show first 20 lines
                    print(line.rstrip())
                else:
                    print("...")
                    break
    
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("\n=== Directory structure ===")
    os.system("find . -type f -name '*.py' | head -10")
    
    print("\n=== Trying alternative import ===")
    # Maybe it's a script, not a module
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("productivity_tracker", 
                                                      "./learning/productivity_tracker.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("✅ Loaded as standalone script")
        
        # List contents
        for item in dir(module):
            if not item.startswith('_'):
                print(f"  - {item}")
    except Exception as e2:
        print(f"Still failed: {e2}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
