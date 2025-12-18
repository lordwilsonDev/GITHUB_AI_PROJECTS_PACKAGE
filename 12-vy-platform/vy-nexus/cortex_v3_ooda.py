import ray
import ollama
import time
import re

ray.init(address="auto", namespace="vy_sovereign", logging_level="ERROR")

@ray.remote(num_cpus=1)
class CortexV3:
    def __init__(self):
        self.model = "llama3"
        self.architect = ray.get_actor("Architect")
        print(f"🧠 Cortex V3.2 (Universal Parser) Online.")

    def think(self, prompt, context="system"):
        # SIMPLIFIED PROMPT: Less text, clearer instructions
        sys_prompt = (
            f"You are Vy-Nexus. Context: {context}.\n"
            "MANDATORY SYNTAX FOR ACTIONS:\n"
            "To write a file:\n"
            "<<<FILE filename.ext>>>\n"
            "content\n"
            "<<<END>>>\n\n"
            "To run a file:\n"
            "<<<EXECUTE filename.ext>>>\n"
            "Do NOT output markdown code blocks (```). Just use the tags."
        )

        try:
            response = ollama.chat(model=self.model, messages=[
                {'role': 'system', 'content': sys_prompt},
                {'role': 'user', 'content': prompt},
            ])
            raw_thought = response['message']['content']
            
            action_log = []
            
            # --- PARSING LOGIC UPGRADE ---
            
            # 1. Catch STRICT format (<<<FILE name>>> content <<<END>>>)
            strict_files = re.findall(r"<<<FILE (.*?)>>>\n(.*?)<<<END>>>", raw_thought, re.DOTALL)
            
            # 2. Catch LAZY format (WRITE: name ... END) - Fallback
            lazy_files = re.findall(r"WRITE: (.*?)\n(.*?)END", raw_thought, re.DOTALL)
            
            # Merge and Dedup
            all_files = strict_files + lazy_files
            
            for filename, content in all_files:
                filename = filename.strip()
                # Remove markdown fences if the AI added them
                content = content.replace("```python", "").replace("```", "")
                
                print(f"⚡ ACTION: Writing {filename}")
                ref = self.architect.write_file.remote(filename, content)
                action_log.append(ray.get(ref))
            
            # 3. Handle Execution (Catch <<<EXECUTE name>>>, <<<RUN name>>>, EXECUTE: name)
            # This regex is messy but robust
            exec_patterns = [
                r"<<<(?:EXECUTE|RUN) (.*?)>>>",
                r"(?:EXECUTE|RUN): (.*?)$"
            ]
            
            for pattern in exec_patterns:
                matches = re.findall(pattern, raw_thought, re.MULTILINE)
                for cmd in matches:
                    filename = cmd.replace("python ", "").replace("`", "").strip()
                    if filename:
                        print(f"⚡ ACTION: Executing {filename}")
                        ref = self.architect.execute_file.remote(filename)
                        action_log.append(ray.get(ref))

            if action_log:
                final_output = raw_thought + "\n\n[SYSTEM ACTIONS]\n" + "\n".join(action_log)
            else:
                final_output = raw_thought

            return {"thought": final_output, "status": "success"}
            
        except Exception as e:
            return {"error": str(e), "status": "failed"}

# Hot Swap
try:
    ray.kill(ray.get_actor("Cortex"))
except:
    pass
time.sleep(1)
CortexV3.options(name="Cortex", lifetime="detached").remote()
print("✅ Cortex V3.2 Detached & Ready.")
