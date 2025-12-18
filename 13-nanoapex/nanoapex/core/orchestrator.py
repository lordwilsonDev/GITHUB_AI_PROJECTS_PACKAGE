#!/usr/bin/env python3
"""
NanoApex Phase IV - Cognitive Orchestrator
Implements Observe-Orient-Decide-Act loop with Blink Protocol memory management
"""

import subprocess
import json
import time
import gc
from pathlib import Path
from datetime import datetime

class NanoApexOrchestrator:
    def __init__(self):
        self.base_dir = Path.home() / "nanoapex"
        self.config_dir = self.base_dir / "config"
        self.log_dir = self.base_dir / "logs"
        self.episodic_memory = self.log_dir / "episodic_memory.json"
        
        # Load system prompt
        with open(self.config_dir / "system_prompt.txt", "r") as f:
            self.system_prompt = f.read()
        
        # Initialize episodic memory
        if not self.episodic_memory.exists():
            self._save_episode([])
    
    def _save_episode(self, episodes):
        """Save episodic memory to disk"""
        with open(self.episodic_memory, "w") as f:
            json.dump(episodes, f, indent=2)
    
    def _load_episodes(self):
        """Load episodic memory from disk"""
        with open(self.episodic_memory, "r") as f:
            return json.load(f)
    
    def observe(self):
        """Phase II - Vision: Capture screen state"""
        print("🔍 OBSERVE: Loading Moondream...")
        
        # Call Moondream vision model
        result = subprocess.run(
            ["python3", str(self.base_dir / "core" / "vision.py")],
            capture_output=True,
            text=True
        )
        
        # Unload vision model (Blink Protocol)
        gc.collect()
        
        return result.stdout.strip()
    
    def decide(self, observation, goal, history):
        """Phase IV - Reasoning: Make next decision"""
        print("🧠 DECIDE: Loading Llama-3...")
        
        # Build context
        context = f"""GOAL: {goal}

CURRENT SCREEN STATE:
{observation}

PREVIOUS ACTIONS:
{json.dumps(history[-5:], indent=2) if history else "None"}

What is the next atomic step?"""
        
        # Call Ollama with JSON mode
        prompt = f"{self.system_prompt}\n\n{context}"
        
        result = subprocess.run(
            [
                "ollama", "run", "llama3.2:latest",
                "--format", "json",
                prompt
            ],
            capture_output=True,
            text=True
        )
        
        # Unload reasoning model (Blink Protocol)
        gc.collect()
        
        try:
            decision = json.loads(result.stdout.strip())
            return decision
        except json.JSONDecodeError:
            print(f"❌ JSON decode failed: {result.stdout}")
            return {"step": "DONE", "reason": "error in reasoning"}
    
    def act(self, decision):
        """Phase II - Kinetic: Execute action"""
        print(f"⚡ ACT: {decision['step']}")
        
        step = decision['step']
        
        if step == "DONE":
            return True
        
        elif step == "click":
            # Use Phase III vision to locate, then Phase II kinetic to click
            query = decision['query']
            
            # Vision: Find coordinates
            coords_result = subprocess.run(
                ["python3", str(self.base_dir / "core" / "locate.py"), query],
                capture_output=True,
                text=True
            )
            coords = coords_result.stdout.strip()
            
            # Kinetic: Execute click
            if coords:
                x, y = coords.split(",")
                subprocess.run(["cliclick", "c:" + coords])
                time.sleep(0.5)
        
        elif step == "type":
            text = decision['text']
            subprocess.run(["cliclick", f"t:{text}"])
            time.sleep(0.3)
        
        return False
    
    def run(self, goal, max_steps=20):
        """Main OODA loop"""
        print(f"\n{'='*60}")
        print(f"🎯 GOAL: {goal}")
        print(f"{'='*60}\n")
        
        episodes = self._load_episodes()
        history = []
        
        for step_num in range(max_steps):
            print(f"\n--- Step {step_num + 1}/{max_steps} ---")
            
            # OBSERVE
            observation = self.observe()
            
            # ORIENT (implicit in decision context)
            
            # DECIDE
            decision = self.decide(observation, goal, history)
            
            # Log episode
            episode = {
                "timestamp": datetime.now().isoformat(),
                "step": step_num + 1,
                "observation": observation[:200] + "..." if len(observation) > 200 else observation,
                "decision": decision
            }
            history.append(episode)
            
            # ACT
            done = self.act(decision)
            
            if done:
                print(f"\n✅ Goal achieved: {decision['reason']}")
                break
            
            # Prevent runaway
            time.sleep(1.0)
        
        # Save all episodes
        episodes.extend(history)
        self._save_episode(episodes)
        
        return history

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 orchestrator.py 'your goal here'")
        sys.exit(1)
    
    goal = " ".join(sys.argv[1:])
    orchestrator = NanoApexOrchestrator()
    orchestrator.run(goal)
