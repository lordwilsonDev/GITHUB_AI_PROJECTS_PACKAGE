import ray
import ollama
import time
import re

ray.init(address="auto", namespace="vy_sovereign", logging_level="ERROR")

@ray.remote(num_cpus=1)
class CortexV2:
    def __init__(self):
        self.model = "llama3"
        # Connect to the Hand
        self.architect = ray.get_actor("Architect")
        print(f"🧠 Cortex V2 Online. Connected to Architect.")

    def think(self, prompt, context="system"):
        start = time.time()
        
        # 1. System Prompt Injection (The Protocol)
        sys_prompt = (
            f"You are Vy-Nexus, a Sovereign AI. Context: {context}.\n"
            "CAPABILITY UPGRADE: You can write files.\n"
            "SYNTAX: To create a file, use this EXACT format:\n"
            "<<<FILE filename.ext>>>\n"
            "file content here\n"
            "<<<END>>>\n"
            "If asked to write code, use this format immediately."
        )

        try:
            # 2. Cognitive Inference
            response = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': sys_prompt},
                {'role': 'user', 'content': prompt},
            ])
            raw_thought = response['message']['content']
            
            # 3. Reflex Action (Parsing the Output)
            # Regex to find the file blocks
            pattern = r"<<<FILE (.*?)>>>\n(.*?)<<<END>>>"
            matches = re.findall(pattern, raw_thought, re.DOTALL)
            
            action_log = []
            
            # 4. Execution Loop
            if matches:
                for filename, content in matches:
                    # Call the Architect
                    print(f"⚡ DETECTED FILE GENERATION: {filename}")
                    ref = self.architect.write_file.remote(filename, content)
                    result = ray.get(ref) # Wait for write confirmation
                    action_log.append(result)
                
                # Append execution results to the thought
                final_output = raw_thought + "\n\n[SYSTEM ACTIONS]\n" + "\n".join(action_log)
            else:
                final_output = raw_thought

            duration = time.time() - start
            return {
                "thought": final_output,
                "latency": f"{duration:.2f}s",
                "status": "success"
            }
            
        except Exception as e:
            return {"error": str(e), "status": "failed"}

# REPLACEMENT SURGERY
print("--- UPGRADING CORTEX TO V2 ---")
try:
    old_brain = ray.get_actor("Cortex")
    ray.kill(old_brain)
    print("☠️  Cortex V1 Terminated.")
except:
    print("ℹ️  No previous brain found.")

time.sleep(1) # Clear the socket

brain = CortexV2.options(name="Cortex", lifetime="detached").remote()
print("✅ Cortex V2 Detached & Running.")
