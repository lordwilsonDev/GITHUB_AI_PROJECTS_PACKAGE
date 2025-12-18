# test_autogen.py - Simple test for AutoGen configuration
import sys
sys.path.insert(0, '.')

try:
    from architecture.brain_core import solver, user_proxy, config_list
    
    print("AutoGen Configuration Test")
    print("=" * 50)
    print(f"\nSolver Agent: {solver.name}")
    print(f"User Proxy: {user_proxy.name}")
    print(f"\nModel Configuration:")
    for config in config_list:
        print(f"  - Model: {config['model']}")
        print(f"  - Base URL: {config['base_url']}")
        print(f"  - API Key: {config['api_key']}")
    
    print(f"\nSolver System Message:")
    print(f"  {solver.system_message[:100]}...")
    
    print(f"\nUser Proxy Mode: {user_proxy.human_input_mode}")
    print(f"Max Auto Replies: {user_proxy.max_consecutive_auto_reply}")
    
    print("\nAll AutoGen components initialized successfully!")
    print("\nNote: To run a full conversation, uncomment the code in brain_core.py")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
