import ray
import sys
import warnings
import os

# SILENCE THE NOISE
# Filter out the SSL and Ray accelerator warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")
warnings.filterwarnings("ignore", category=FutureWarning, module="ray")
os.environ["PYTHONWARNINGS"] = "ignore"

# Connect silently
try:
    ray.init(address="auto", namespace="vy_sovereign", logging_level="ERROR")
except:
    print("❌ SYSTEM OFFLINE. (Heartbeat missing?)")
    sys.exit(1)

def query_cortex(prompt):
    try:
        # Grab the persistent brain
        brain = ray.get_actor("Cortex")
        
        # Spinning cursor for "Thinking" state
        print("⚡", end="", flush=True)
        future = brain.think.remote(prompt, context="User CLI Override")
        result = ray.get(future)
        print("\b ", end="", flush=True) # Erase spark
        
        if result.get("status") == "success":
            return result.get("thought")
        else:
            return f"❌ CORTEX ERROR: {result.get('error')}"
            
    except ValueError:
        return "⚠️ CORTEX DETACHED. Run '~/vy-nexus/venv/bin/python3 ~/vy-nexus/cortex_bridge.py' to re-seat the brain."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: vy <thought>")
        sys.exit(1)
        
    prompt = " ".join(sys.argv[1:])
    response = query_cortex(prompt)
    print(response)
