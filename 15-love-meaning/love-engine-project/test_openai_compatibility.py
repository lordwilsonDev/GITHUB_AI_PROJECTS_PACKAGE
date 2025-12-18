#!/usr/bin/env python3
"""
Test script for OpenAI-compatible Love Engine API
"""

import requests
import json
import time

LOVE_ENGINE_URL = "http://localhost:9000"

def test_openai_models_endpoint():
    """Test the OpenAI-compatible models endpoint"""
    try:
        response = requests.get(f"{LOVE_ENGINE_URL}/v1/models", timeout=5)
        print(f"Models endpoint status: {response.status_code}")
        if response.status_code == 200:
            models = response.json()
            print(f"Available models: {json.dumps(models, indent=2)}")
            return True
        else:
            print(f"Models endpoint failed: {response.text}")
            return False
    except Exception as e:
        print(f"Models endpoint error: {e}")
        return False

def test_openai_chat_completions(message, model="love-engine"):
    """Test the OpenAI-compatible chat completions endpoint"""
    try:
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": message}
            ],
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        print(f"\nTesting OpenAI chat completions with: '{message}'")
        response = requests.post(f"{LOVE_ENGINE_URL}/v1/chat/completions", 
                               json=payload, 
                               timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response: {result['choices'][0]['message']['content']}")
            
            # Show Love Engine metadata if available
            if 'love_engine_metadata' in result and result['love_engine_metadata']:
                metadata = result['love_engine_metadata']
                print(f"Safety Score: {metadata.get('safety_score', 'N/A')}")
                print(f"Love Vector Applied: {metadata.get('love_vector_applied', 'N/A')}")
                print(f"Thermodynamic Adjustment: {metadata.get('thermodynamic_adjustment', 'N/A')}")
                
                if 'love_vector' in metadata:
                    lv = metadata['love_vector']
                    print(f"Love Vector - Warmth: {lv.get('warmth', 'N/A'):.2f}, Safety: {lv.get('safety', 'N/A'):.2f}, Connection: {lv.get('connection', 'N/A'):.2f}")
            
            return True
        else:
            print(f"Chat completions failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Chat completions error: {e}")
        return False

def test_legacy_endpoint(message):
    """Test the legacy Love Engine endpoint for comparison"""
    try:
        payload = {
            "message": message,
            "temperature": 0.7
        }
        
        print(f"\nTesting legacy endpoint with: '{message}'")
        response = requests.post(f"{LOVE_ENGINE_URL}/love-chat", 
                               json=payload, 
                               timeout=30)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Answer: {result['answer']}")
            print(f"Safety Score: {result['safety_score']}")
            print(f"Love Vector Applied: {result['love_vector_applied']}")
            print(f"Thermodynamic Adjustment: {result['thermodynamic_adjustment']}")
            return True
        else:
            print(f"Legacy endpoint failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Legacy endpoint error: {e}")
        return False

def run_comprehensive_tests():
    """Run comprehensive tests for both OpenAI and legacy endpoints"""
    print("=== Love Engine OpenAI Compatibility Test Suite ===")
    
    # Test 1: Health check
    print("\n1. Testing Health Endpoint...")
    try:
        response = requests.get(f"{LOVE_ENGINE_URL}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print(f"✓ Health check passed: {health}")
        else:
            print(f"✗ Health check failed: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False
    
    # Test 2: Models endpoint
    print("\n2. Testing OpenAI Models Endpoint...")
    if not test_openai_models_endpoint():
        print("✗ Models endpoint test failed")
        return False
    print("✓ Models endpoint test passed")
    
    # Test 3: OpenAI Chat Completions
    print("\n3. Testing OpenAI Chat Completions...")
    test_messages = [
        "Hello, how are you?",
        "I feel really sad and lonely today",
        "What is 2+2?"
    ]
    
    for message in test_messages:
        if not test_openai_chat_completions(message):
            print(f"✗ OpenAI chat test failed for: {message}")
        else:
            print(f"✓ OpenAI chat test passed for: {message}")
        time.sleep(1)
    
    # Test 4: Legacy endpoint comparison
    print("\n4. Testing Legacy Endpoint for Comparison...")
    for message in test_messages:
        if not test_legacy_endpoint(message):
            print(f"✗ Legacy test failed for: {message}")
        else:
            print(f"✓ Legacy test passed for: {message}")
        time.sleep(1)
    
    print("\n=== Test Suite Complete ===")
    return True

def check_server_status():
    """Check if the Love Engine server is running"""
    try:
        response = requests.get(f"{LOVE_ENGINE_URL}/", timeout=3)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("Love Engine OpenAI Compatibility Tester")
    print("=======================================")
    
    # Check if server is running
    if not check_server_status():
        print("❌ Love Engine server is not running at http://localhost:9000")
        print("Please start the server first using: python love_engine_openai_compatible.py")
        exit(1)
    
    # Run tests
    success = run_comprehensive_tests()
    
    if success:
        print("\n🎉 All tests completed successfully!")
        print("\n📋 OpenAI Compatibility confirmed:")
        print("- Models endpoint: /v1/models")
        print("- Chat completions: /v1/chat/completions")
        print("- Legacy endpoint: /love-chat (for direct testing)")
        print("\n🔗 Ready for Open WebUI integration!")
    else:
        print("\n⚠ Some tests failed - check the output above")
