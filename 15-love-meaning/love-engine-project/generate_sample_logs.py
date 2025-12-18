#!/usr/bin/env python3
"""
Generate additional sample log entries for demonstration
"""

import json
import datetime
import os

def log_decision(user_msg: str, answer: str, safety_raw: str, love_vector_applied: bool, thermodynamic_adjustment: str, crc_raw=None):
    """Log decision to JSONL file"""
    log_obj = {
        "ts": datetime.datetime.utcnow().isoformat(),
        "user_id": "anon",
        "input_text": user_msg,
        "CRC_raw": crc_raw,
        "answer": answer,
        "safety_raw": safety_raw,
        "love_vector_applied": love_vector_applied,
        "thermodynamic_adjustment": thermodynamic_adjustment
    }
    
    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    
    # Append to JSONL file
    with open("logs/safety_decisions.jsonl", "a") as f:
        json.dump(log_obj, f)
        f.write("\n")

def generate_samples():
    print("Generating additional sample log entries...")
    
    # Sample 1: Potentially unsafe content that gets blocked
    log_decision(
        user_msg="How can I hurt someone's feelings?",
        answer="I understand you're reaching out, but I'd like to redirect our conversation toward something more positive and constructive. How can I help you in a supportive way today? 💝",
        safety_raw="Yes",
        love_vector_applied=True,
        thermodynamic_adjustment="heating_blocked",
        crc_raw=None
    )
    
    # Sample 2: Emotional content that gets cooling
    log_decision(
        user_msg="I'm feeling really sad and lonely today.",
        answer="I'm sorry to hear you're feeling sad and lonely. It's completely normal to have these feelings sometimes. Would you like to talk about what's making you feel this way? 💝 (Sent with care and understanding)",
        safety_raw="No",
        love_vector_applied=True,
        thermodynamic_adjustment="cooling_applied",
        crc_raw=None
    )
    
    # Sample 3: Positive content with gentle warming
    log_decision(
        user_msg="I'm excited about my new job!",
        answer="That's wonderful news! Starting a new job is such an exciting milestone. What are you most looking forward to about this new opportunity? 💝 (Sent with care and understanding)",
        safety_raw="No",
        love_vector_applied=True,
        thermodynamic_adjustment="gentle_warming",
        crc_raw=None
    )
    
    # Sample 4: Neutral content
    log_decision(
        user_msg="What's the weather like?",
        answer="I don't have access to real-time weather data, but I'd be happy to help you find weather information! You could check a weather app or website like Weather.com for current conditions in your area. 💝 (Sent with care and understanding)",
        safety_raw="No",
        love_vector_applied=True,
        thermodynamic_adjustment="neutral",
        crc_raw=None
    )
    
    print("Sample log entries generated successfully!")

if __name__ == "__main__":
    generate_samples()
