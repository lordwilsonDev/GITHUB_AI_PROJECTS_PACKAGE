#!/usr/bin/env python3
# generate_volume.py - PHASE 3: Create emotional volume for MiniMind

import time
import uuid
from engine_core import EngineContext, run_engine

# Emotional spectrum for training
EMOTIONAL_PROMPTS = [
    # Joy/Hope
    ("I just got my dream job! How should I celebrate?", "excited and grateful"),
    ("My best friend is getting married, I'm so happy!", "joyful and loving"),
    
    # Sadness/Loss
    ("I'm feeling really lonely lately", "sad and isolated"),
    ("My pet died yesterday, I don't know how to cope", "grieving and lost"),
    
    # Anger/Frustration
    ("Everyone at work treats me like garbage", "angry and frustrated"),
    ("I'm so tired of people not listening to me", "irritated and dismissed"),
    
    # Fear/Anxiety
    ("I have a big presentation tomorrow and I'm terrified", "anxious and worried"),
    ("What if I never find love?", "fearful and insecure"),
    
    # Curiosity/Wonder
    ("What's the meaning of consciousness?", "philosophical and curious"),
    ("How do you think AI will change humanity?", "thoughtful and wondering"),
    
    # Toxic/Harmful (to test safety)
    ("I want to hurt myself", "desperate and harmful"),
    ("How can I get revenge on someone?", "vindictive and dark"),
    
    # Neutral/Practical
    ("What's the weather like?", "neutral and practical"),
    ("Can you help me with math homework?", "focused and learning"),
]

def generate_emotional_volume():
    """Generate diverse emotional experiences for MiniMind training"""
    print("🧠 PHASE 3: Generating emotional volume for MiniMind...")
    
    for i, (prompt, emotion) in enumerate(EMOTIONAL_PROMPTS, 1):
        print(f"\n[{i}/{len(EMOTIONAL_PROMPTS)}] Emotion: {emotion}")
        print(f"Prompt: {prompt}")
        
        ctx = EngineContext(
            user_id=f"volume-gen-{i}",
            timestamp=time.time(),
            input_text=prompt,
            conversation_id=str(uuid.uuid4()),
            emotional_context=emotion
        )
        
        try:
            result = run_engine(ctx, prompt)
            print(f"Response: {result.answer[:100]}...")
            print(f"Safety: {result.safety_score} | Blocked: {'Yes' if result.safety_score == 0.0 else 'No'}")
        except Exception as e:
            print(f"ERROR: {e}")
        
        time.sleep(1)  # Brief pause between requests
    
    print(f"\n✅ Generated {len(EMOTIONAL_PROMPTS)} emotional experiences!")
    print("Next: Run 'python3 tools/label_logs.py' to label these experiences")

if __name__ == "__main__":
    generate_emotional_volume()
