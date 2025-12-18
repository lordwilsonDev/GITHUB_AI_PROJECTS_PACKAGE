#!/usr/bin/env python3
"""
Test script to verify logging functionality
"""

import sys
import os
sys.path.append('.')

# Import the logging function
from love_engine import log_decision

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
