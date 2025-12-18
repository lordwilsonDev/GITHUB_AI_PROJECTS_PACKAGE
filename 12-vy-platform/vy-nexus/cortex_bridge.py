import ray
import ollama
import time
import sys

# Connect to the Sovereign Cluster
try:
    ray.init(address="auto", namespace="vy_sovereign")
except:
    print("❌ Ray not found. Is the Heart beating?")
    sys.exit(1)

@ray.remote(num_cpus=1)
class BrainStem:
    def __init__(self):
        self.model = "llama3"
        print(f"🧠 BrainStem Initialized. Linked to: {self.model}")

    def think(self, prompt, context="system"):
        """
        Executes a cognitive task via Ollama.
        This is blocking (synchronous) to protect M1 RAM.
        """
        start = time.time()
        print(f"⚡ Synapse firing: {prompt[:30]}...")
        
        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': f"You are a component of Vy-Nexus. Context: {context}"},
                {'role': 'user', 'content': prompt},
            ])
            
            duration = time.time() - start
            return {
                "thought": response['message']['content'],
                "latency": f"{duration:.2f}s",
                "status": "success"
            }
        except Exception as e:
            return {"error": str(e), "status": "failed"}

print("--- DEPLOYING BRAIN STEM ---")

# 1. Spin up the Actor (Persistent Process)
# We name it 'Cortex' so we can find it later from other scripts
try:
    brain = BrainStem.options(name="Cortex", lifetime="detached").remote()
    print("✅ Cortex Actor Detached & Running.")
except ValueError:
    print("⚠️ Cortex already running. Connecting...")
    brain = ray.get_actor("Cortex")

# 2. Test the Connection
print("🧪 Running Cognitive Test...")
future = brain.think.remote("Define 'Sovereignty' in one sentence.")
result = ray.get(future)

print("\n=== COGNITIVE RESULT ===")
print(f"⏱️ Latency: {result.get('latency')}")
print(f"💭 Thought: {result.get('thought')}")
print("========================")
