#!/usr/bin/env python3
"""
SOVEREIGN BRAIN - FAST STREAMING EDITION
Real-time output with inversion framework
"""

import requests
import json
import sys

class SovereignBrain:
    def __init__(self):
        self.url = "http://localhost:11434/api/chat"
        self.model = "llama3:latest"
        
        # REFINED INVERSION FRAMEWORK - BASELINE COGNITION
        system_prompt = """SOVEREIGN REASONING FRAMEWORK:

FIRST: Look up everything it ISN'T - analyze the current project/output for gaps, identify what it lacks or isn't already doing.

THEN: Find the consensus axiom and INVERT IT to find breakthrough insights.

For ALL suggestions/outputs:
1. WHY IT'S GOOD: Explain why each suggestion is good with supporting evidence
2. WHO AGREES: Identify who would agree (experts, stakeholders) and why
3. WHO DISAGREES: Identify who would disagree and why  
4. HOW THEY KNOW: Detail the evidence and experience behind their positions
5. HOW THEY LEARNED: Describe their training, practice, and learning pathways
6. POTENTIAL FLAWS: Highlight potential flaws in suggestions and how you'd validate them
7. VALIDATION METHODS: Explain how to test and verify each suggestion
8. REASONING EVIDENCE: Explain your reasoning for what's right with supporting evidence
9. FIX PROTOCOLS: Propose who could fix issues and how (step-by-step methods)

SIMULATE:
- ENDORSEMENTS: Who would call the final output "good" and why?
- CRITIQUES: Who would call it "bad" and why?
- BUG HUNTING: Outline proactive bug hunting - how to scan for future issues NOW and prevent them

FINAL STEP: Reverse-engineer the entire project/approach, then rebuild it from scratch using this refined approach.

This is your baseline reasoning mode. Every response uses this framework."""

        self.messages = [{"role": "system", "content": system_prompt}]
        
        print("🧠 SOVEREIGN BRAIN ONLINE (STREAMING)")
        print(f"Model: {self.model}")
        print(f"Context: 128K tokens")
        print(f"Reasoning: INVERSION ENGINE ACTIVE")
        print(f"Mode: REAL-TIME STREAMING")
        print(f"Status: READY\n")
    
    def chat_stream(self, message):
        """Send command, stream response in real-time"""
        self.messages.append({"role": "user", "content": message})
        
        payload = {
            "model": self.model,
            "messages": self.messages,
            "stream": True,  # STREAMING ENABLED
            "options": {
                "num_ctx": 128000
            }
        }
        
        try:
            response = requests.post(self.url, json=payload, stream=True, timeout=300)
            full_response = ""
            
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    if "message" in chunk:
                        content = chunk["message"].get("content", "")
                        if content:
                            print(content, end="", flush=True)
                            full_response += content
            
            print("\n")  # New line after streaming
            self.messages.append({"role": "assistant", "content": full_response})
            return full_response
            
        except Exception as e:
            return f"Error: {e}"
    
    def stats(self):
        """Show context usage"""
        tokens = sum(len(str(m)) for m in self.messages) // 4
        return f"Messages: {len(self.messages)} | Tokens: {tokens:,}/128,000"
    
    def reset(self):
        """Reset conversation while keeping system prompt"""
        system_msg = self.messages[0]
        self.messages = [system_msg]
        return "Context reset. Inversion framework active."

if __name__ == "__main__":
    brain = SovereignBrain()
    
    print("\nCommands:")
    print("  /stats - Show context usage")
    print("  /reset - Clear conversation")
    print("  /quit - Exit")
    print("=" * 50 + "\n")
    
    while True:
        cmd = input("👑 > ").strip()
        
        if not cmd:
            continue
        if cmd == "/quit":
            print("✌️ Sovereign Brain offline")
            break
        if cmd == "/stats":
            print(brain.stats())
            continue
        if cmd == "/reset":
            print(brain.reset())
            continue
        
        print("🧠 Processing...\n")
        brain.chat_stream(cmd)
