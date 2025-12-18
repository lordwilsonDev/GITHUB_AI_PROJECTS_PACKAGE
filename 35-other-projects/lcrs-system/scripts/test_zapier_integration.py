#!/usr/bin/env python3
"""
Zapier Integration Test Script for LCRS System
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def test_zapier_webhooks():
    base_url = "http://localhost:8000"
    
    test_data = {
        "gmail": {
            "trigger_type": "email_received",
            "data": {
                "from": "customer@example.com",
                "subject": "Need help with my order",
                "body": "I'm frustrated with the delay in my order delivery"
            }
        }
    }
    
    print("Testing Zapier Integration...")
    
    for webhook_type, payload in test_data.items():
        try:
            response = requests.post(
                f"{base_url}/api/v1/zapier-webhook",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print(f"SUCCESS: {webhook_type.upper()} webhook test passed")
            else:
                print(f"FAILED: {webhook_type.upper()} webhook test failed")
        except Exception as e:
            print(f"ERROR: {webhook_type.upper()} webhook test error: {str(e)}")

if __name__ == "__main__":
    test_zapier_webhooks()
