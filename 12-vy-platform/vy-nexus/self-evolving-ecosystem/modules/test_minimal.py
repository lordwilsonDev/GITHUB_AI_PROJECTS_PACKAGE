import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try to import the module without the .py extension
    module_name = os.path.basename('$MAIN_FILE').replace('.py', '')
    module = __import__(module_name)
    
    print(f"✅ Module loaded: {module_name}")
    
    # Check for main functions
    functions = [f for f in dir(module) if not f.startswith('_')]
    print(f"Available functions: {functions[:10]}")
    
    # Try to run main if exists
    if hasattr(module, 'main'):
        print("Has main() - testing...")
        try:
            result = module.main()
            print(f"✅ main() returned: {result}")
        except Exception as e:
            print(f"⚠️ main() failed: {e}")
except Exception as e:
    print(f"❌ Failed to load: {e}")
