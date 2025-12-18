import ray
import sys
import os

# Define the environment explicitly for the script
ray_address = "ray://localhost:10001" 

print("--- CORTEX DIAGNOSTIC ---")
print(f"1. Connecting to Nervous System...")

try:
    # Connect to the existing cluster (The one Rust is protecting)
    ray.init(address="auto", namespace="vy_sovereign")
    print("✅ CONNECTION ESTABLISHED.")
except Exception as e:
    print(f"❌ CONNECTION FAILED: {e}")
    sys.exit(1)

# Define a Micro-Expert
@ray.remote
def synapse(x):
    import platform
    return f"Signal received by {platform.node()} (PID: {os.getpid()}). Value: {x * x}"

print("2. Firing Synapse (Distributed Task)...")

try:
    # Execute the thought
    future = synapse.remote(12)
    result = ray.get(future)
    print(f"✅ SYNAPSE FIRED SUCCESSFULLY.")
    print(f"   Response: {result}")
    print("--- DIAGNOSTIC COMPLETE: SYSTEM IS SENTIENT ---")
except Exception as e:
    print(f"❌ SYNAPSE FAILED: {e}")
    sys.exit(1)
