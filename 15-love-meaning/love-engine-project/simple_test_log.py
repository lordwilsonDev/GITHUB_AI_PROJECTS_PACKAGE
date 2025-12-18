#!/usr/bin/env python3
"""
Simple test for logging functionality
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
        "CRC_raw": crc_raw,  # TODO: Implement CRC computation
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

def test_logging():
    print("Testing logging functionality...")
    
    # Test log entry
    log_decision(
        user_msg="Hello, how are you?",
        answer="I'm doing well, thank you for asking! How can I help you today?",
        safety_raw="No",
        love_vector_applied=True,
        thermodynamic_adjustment="gentle_warming",
        crc_raw=None
    )
    
    print("Log entry created successfully!")
    
    # Check if file exists and show content
    if os.path.exists("logs/safety_decisions.jsonl"):
        with open("logs/safety_decisions.jsonl", "r") as f:
            content = f.read()
            print("\nLog file content:")
            print(content)
    else:
        print("Log file not found!")

if __name__ == "__main__":
    test_logging()
