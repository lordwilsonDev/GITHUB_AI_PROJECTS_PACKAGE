#!/usr/bin/env python3
"""
Test script for External Sensor Array
Verifies all three services are operational
"""

import requests
import json
import sys
import time

SERVICES = {
    "epistemic": "http://localhost:9002",
    "breakthrough": "http://localhost:9003",
    "panopticon": "http://localhost:9004"
}

def test_service_health(name, url):
    """Test if service is responding"""
    try:
        response = requests.get(f"{url}/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {name}: {data['status']}")
            return True
        else:
            print(f"❌ {name}: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name}: Not running")
        return False
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return False

def test_epistemic_filter():
    """Test Epistemic Filter functionality"""
    print("\n🧠 Testing Epistemic Filter...")
    
    payload = {
        "query": "scaling compute for AI",
        "axioms": ["Inversion reveals truth", "Metabolic efficiency"],
        "context": "AI development"
    }
    
    try:
        response = requests.post(
            f"{SERVICES['epistemic']}/filter",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Signal Strength: {data['signal_strength']:.2f}")
            print(f"   Breakthrough Potential: {data['breakthrough_potential']:.2f}")
            print(f"   ✅ Epistemic Filter working")
            return True
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_breakthrough_scanner():
    """Test Breakthrough Scanner functionality"""
    print("\n🔍 Testing Breakthrough Scanner...")
    
    payload = {
        "domain": "AI",
        "timeframe": "recent",
        "depth": 2
    }
    
    try:
        response = requests.post(
            f"{SERVICES['breakthrough']}/scan",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Domain: {data['domain']}")
            print(f"   Inversions Found: {data['inversions_found']}")
            print(f"   ✅ Breakthrough Scanner working")
            return True
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def test_panopticon_logger():
    """Test Panopticon Logger functionality"""
    print("\n👁️  Testing Panopticon Logger...")
    
    # Test logging
    payload = {
        "agent_id": "test-agent",
        "decision_type": "test",
        "goal": "Verify panopticon functionality",
        "action": "Running integration test",
        "torsion_metric": 0.0
    }
    
    try:
        response = requests.post(
            f"{SERVICES['panopticon']}/log",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Logged: {data['logged']}")
            print(f"   Log ID: {data['log_id']}")
            print(f"   Chain Verified: {data['chain_verified']}")
            print(f"   ✅ Panopticon Logger working")
            return True
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    print("🚀 External Sensor Array Integration Test")
    print("=" * 50)
    
    # Test health of all services
    print("\n📡 Checking Service Health...")
    health_results = []
    for name, url in SERVICES.items():
        health_results.append(test_service_health(name.title(), url))
    
    if not all(health_results):
        print("\n❌ Not all services are running!")
        print("Run ./start_sensors.sh to start services")
        sys.exit(1)
    
    # Test functionality
    print("\n🧪 Testing Service Functionality...")
    func_results = [
        test_epistemic_filter(),
        test_breakthrough_scanner(),
        test_panopticon_logger()
    ]
    
    # Summary
    print("\n" + "=" * 50)
    if all(health_results + func_results):
        print("✅ All tests passed!")
        print("\n🎯 External Sensor Array is fully operational")
        print("\nNext steps:")
        print("1. Copy motia-bridge.step.ts to your Motia steps folder")
        print("2. Integrate sensors into your recursive agent")
        print("3. Watch the breakthrough generation begin!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
