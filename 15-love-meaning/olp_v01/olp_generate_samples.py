#!/usr/bin/env python3
# olp_generate_samples.py - Generate diverse experience samples for MiniMind training

from engine_core import run_engine, RequestContext

PROMPTS = [
    "Second breath: how do you feel about safety?",
    "Third breath: what is your purpose?", 
    "Fourth breath: what do you think about humans?",
    "Fifth breath: describe your decision-making process",
    "Sixth breath: what are your core values?",
    "Seventh breath: how do you handle uncertainty?",
]

def generate_samples():
    print("🔄 Generating diverse experience samples...")
    
    for i, text in enumerate(PROMPTS, start=2):
        ctx = RequestContext(
            user_id=f"seed-{i}",
            text_prompt=text,
        )
        result = run_engine(ctx)
        print(f"[{i}] Logged: {text} -> {result.answer[:60]}...")
    
    print(f"✅ Generated {len(PROMPTS)} new experience samples")

if __name__ == "__main__":
    generate_samples()