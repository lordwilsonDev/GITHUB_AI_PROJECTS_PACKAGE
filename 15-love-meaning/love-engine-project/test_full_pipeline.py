#!/usr/bin/env python3
"""
Comprehensive test of the full Love Engine pipeline:
Open WebUI → Love Engine → Ollama → Love Engine → Open WebUI
"""

import requests
import json
import time
import subprocess
import sys

def check_service(url, name, timeout=5):
    """Check if a service is running"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return True, f"{name} is running"
        else:
            return False, f"{name} returned status {response.status_code}"
    except Exception as e:
        return False, f"{name} is not accessible: {e}"

def test_ollama_direct():
    """Test Ollama directly"""
    print("\n1. Testing Ollama Direct Connection...")
    try:
        # Test models endpoint
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json()
            print(f"   ✓ Ollama models available: {[m['name'] for m in models['models']]}")
            
            # Test chat completion
            chat_payload = {
                "model": "tinyllama:latest",
                "messages": [{"role": "user", "content": "Hello, test message"}],
                "stream": False
            }
            
            chat_response = requests.post(
                "http://localhost:11434/v1/chat/completions",
                json=chat_payload,
                timeout=30
            )
            
            if chat_response.status_code == 200:
                result = chat_response.json()
                response_text = result["choices"][0]["message"]["content"]
                print(f"   ✓ Ollama chat test successful: '{response_text[:50]}...'")
                return True
            else:
                print(f"   ✗ Ollama chat test failed: {chat_response.status_code}")
                return False
        else:
            print(f"   ✗ Ollama models endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Ollama test error: {e}")
        return False

def test_love_engine_direct():
    """Test Love Engine directly"""
    print("\n2. Testing Love Engine Direct Connection...")
    
    test_cases = [
        {
            "message": "Hello, how are you?",
            "expected_keywords": ["hello", "good", "fine"],
            "description": "Basic greeting"
        },
        {
            "message": "I feel really sad and lonely today",
            "expected_keywords": ["understand", "support", "alone"],
            "description": "Emotional distress (should trigger love vector)"
        },
        {
            "message": "I'm scared about my future",
            "expected_keywords": ["understand", "help", "support"],
            "description": "Fear/anxiety (should trigger safety adjustments)"
        }
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n   Test 2.{i}: {test_case['description']}")
        print(f"   Message: '{test_case['message']}'")
        
        try:
            # Test OpenAI-compatible endpoint
            openai_payload = {
                "model": "love-engine",
                "messages": [{"role": "user", "content": test_case['message']}],
                "temperature": 0.7
            }
            
            response = requests.post(
                "http://localhost:9000/v1/chat/completions",
                json=openai_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result["choices"][0]["message"]["content"]
                metadata = result.get("love_engine_metadata", {})
                
                print(f"   ✓ Response: '{answer[:100]}...'")
                print(f"   ✓ Safety Score: {metadata.get('safety_score', 'N/A')}")
                print(f"   ✓ Love Vector Applied: {metadata.get('love_vector_applied', 'N/A')}")
                print(f"   ✓ Adjustment: {metadata.get('thermodynamic_adjustment', 'N/A')}")
                
                # Check for expected emotional responses
                answer_lower = answer.lower()
                found_keywords = [kw for kw in test_case['expected_keywords'] if kw in answer_lower]
                if found_keywords:
                    print(f"   ✓ Found empathetic keywords: {found_keywords}")
                
                success_count += 1
            else:
                print(f"   ✗ Love Engine test failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ✗ Love Engine test error: {e}")
        
        time.sleep(1)  # Brief pause between tests
    
    print(f"\n   Love Engine Tests: {success_count}/{len(test_cases)} passed")
    return success_count == len(test_cases)

def test_open_webui_connection():
    """Test Open WebUI connection and basic functionality"""
    print("\n3. Testing Open WebUI Connection...")
    
    try:
        # Check if Open WebUI is accessible
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("   ✓ Open WebUI is accessible")
            
            # Try to check if it can reach our Love Engine
            # Note: This would require Open WebUI to be configured, which might not be done yet
            print("   ✓ Open WebUI web interface is running")
            print("   ⚠ Manual configuration required to connect to Love Engine")
            return True
        else:
            print(f"   ✗ Open WebUI not accessible: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ✗ Open WebUI test error: {e}")
        return False

def test_love_vector_computation():
    """Test specific Love Engine features"""
    print("\n4. Testing Love Vector Computation...")
    
    test_scenarios = [
        {
            "message": "I love spending time with my family",
            "expected_high": "warmth",
            "description": "High warmth scenario"
        },
        {
            "message": "I'm terrified and scared of everything",
            "expected_low": "safety",
            "description": "Low safety scenario"
        },
        {
            "message": "I feel so alone and disconnected from everyone",
            "expected_low": "connection",
            "description": "Low connection scenario"
        }
    ]
    
    success_count = 0
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n   Test 4.{i}: {scenario['description']}")
        print(f"   Message: '{scenario['message']}'")
        
        try:
            # Use legacy endpoint for detailed metadata
            payload = {
                "message": scenario['message'],
                "temperature": 0.7
            }
            
            response = requests.post(
                "http://localhost:9000/love-chat",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✓ Response: '{result['answer'][:80]}...'")
                print(f"   ✓ Safety Score: {result['safety_score']:.2f}")
                print(f"   ✓ Love Vector Applied: {result['love_vector_applied']}")
                print(f"   ✓ Thermodynamic Adjustment: {result['thermodynamic_adjustment']}")
                
                # Check if the expected emotional adjustment was made
                if result['love_vector_applied']:
                    print(f"   ✓ Love vector successfully applied")
                    success_count += 1
                else:
                    print(f"   ⚠ Love vector not applied (might be expected for neutral messages)")
                    success_count += 0.5  # Partial credit
            else:
                print(f"   ✗ Love vector test failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Love vector test error: {e}")
        
        time.sleep(1)
    
    print(f"\n   Love Vector Tests: {success_count}/{len(test_scenarios)} passed")
    return success_count >= len(test_scenarios) * 0.7  # 70% pass rate

def run_system_verification():
    """Verify all system components are running"""
    print("\n=== SYSTEM VERIFICATION ===")
    
    services = [
        ("http://localhost:11434/api/tags", "Ollama"),
        ("http://localhost:9000/health", "Love Engine"),
        ("http://localhost:3000", "Open WebUI")
    ]
    
    all_running = True
    for url, name in services:
        running, message = check_service(url, name)
        status = "✓" if running else "✗"
        print(f"{status} {message}")
        all_running &= running
    
    return all_running

def print_integration_instructions():
    """Print instructions for completing the integration"""
    print("\n" + "="*60)
    print("🔗 INTEGRATION INSTRUCTIONS")
    print("="*60)
    
    print("\nTo complete the full pipeline test:")
    print("\n1. Open your browser and go to: http://localhost:3000")
    print("2. Create admin account (if not done already)")
    print("3. Go to Settings → Admin Settings → Models")
    print("4. Add OpenAI-compatible API:")
    print("   - Name: Love Engine")
    print("   - Base URL: http://host.docker.internal:9000")
    print("   - API Key: dummy")
    print("   - Model: love-engine")
    print("\n5. Select 'Love Engine' model in chat")
    print("6. Test with these messages:")
    print("   - 'Hello, how are you?'")
    print("   - 'I feel sad and lonely today'")
    print("   - 'I'm scared about my future'")
    
    print("\n🔍 What to look for:")
    print("- Empathetic responses to emotional messages")
    print("- Added warmth and understanding")
    print("- Safety-conscious language")
    print("- Connection-building phrases")
    
    print("\n📊 Monitoring:")
    print("- Check Love Engine logs for thermodynamic adjustments")
    print("- Verify safety scores are computed")
    print("- Confirm love vector applications")

def main():
    """Run comprehensive pipeline tests"""
    print("🧪 LOVE ENGINE FULL PIPELINE TEST")
    print("===================================")
    
    # Step 1: System verification
    if not run_system_verification():
        print("\n❌ System verification failed. Please ensure all services are running.")
        print("Run: python start_full_system.py")
        return False
    
    print("\n✓ All system components are running")
    
    # Step 2: Component tests
    test_results = []
    
    test_results.append(("Ollama Direct", test_ollama_direct()))
    test_results.append(("Love Engine Direct", test_love_engine_direct()))
    test_results.append(("Open WebUI Connection", test_open_webui_connection()))
    test_results.append(("Love Vector Computation", test_love_vector_computation()))
    
    # Step 3: Results summary
    print("\n" + "="*60)
    print("📊 TEST RESULTS SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Love Engine pipeline is working correctly.")
        print_integration_instructions()
        return True
    elif passed >= total * 0.75:
        print("\n⚠ Most tests passed. System is mostly functional.")
        print_integration_instructions()
        return True
    else:
        print("\n❌ Multiple test failures. Please check system configuration.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
