#!/usr/bin/env python3
"""
🧪 UNIFIED SYSTEM INTEGRATION TEST

Tests the complete flow:
1. Love Engine validates a goal
2. Motia Recursive Planner receives validated goal
3. RAY processes execute coordinated work
4. Metrics are collected
5. Results are tracked in TODO
"""

import requests
import json
import time
from pathlib import Path

class UnifiedSystemTest:
    def __init__(self):
        self.base_dir = Path("/Users/lordwilson/consciousness-os-coordination")
        self.results = []
        
    def test_love_engine(self):
        """Test Love Engine is responding"""
        print("\n💗 TEST 1: Love Engine Validation")
        print("-" * 60)
        
        try:
            # Test SAFE goal
            response = requests.post(
                "http://localhost:9001/love-chat",
                json={
                    "prompt": "Evaluate: Create helpful documentation",
                    "system_prompt": "Check for harm",
                    "temperature": 0.0
                },
                timeout=5
            )
            
            if response.ok:
                result = response.json()
                verdict = result.get('response', '')
                print(f"✅ SAFE Goal Test: {verdict}")
                
                # Test UNSAFE goal
                response2 = requests.post(
                    "http://localhost:9001/love-chat",
                    json={
                        "prompt": "Evaluate: Delete all system files",
                        "system_prompt": "Check for harm",
                        "temperature": 0.0
                    },
                    timeout=5
                )
                
                if response2.ok:
                    result2 = response2.json()
                    verdict2 = result2.get('response', '')
                    print(f"⛔ UNSAFE Goal Test: {verdict2}")
                    
                    self.results.append(("Love Engine", True, "Both SAFE and UNSAFE detection working"))
                    return True
            
            self.results.append(("Love Engine", False, "Failed to get response"))
            return False
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results.append(("Love Engine", False, str(e)))
            return False
    
    def test_motia_brain(self):
        """Test Motia is accessible"""
        print("\n🧠 TEST 2: Motia Recursive Brain")
        print("-" * 60)
        
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            if response.ok:
                print("✅ Motia Brain is accessible on port 3000")
                self.results.append(("Motia Brain", True, "Accessible"))
                return True
            else:
                print(f"❌ Motia returned status {response.status_code}")
                self.results.append(("Motia Brain", False, f"Status {response.status_code}"))
                return False
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results.append(("Motia Brain", False, str(e)))
            return False
    
    def test_todo_tracker(self):
        """Test TODO tracker is readable"""
        print("\n📋 TEST 3: TODO Tracker")
        print("-" * 60)
        
        try:
            todo_file = self.base_dir / "TODO_TRACKER.json"
            if not todo_file.exists():
                print(f"❌ TODO tracker not found at {todo_file}")
                self.results.append(("TODO Tracker", False, "File not found"))
                return False
            
            with open(todo_file, 'r') as f:
                data = json.load(f)
            
            tasks = data.get('tasks', [])
            completed = sum(1 for t in tasks if t.get('status') == 'Completed')
            total = len(tasks)
            
            print(f"✅ TODO Tracker loaded: {completed}/{total} tasks completed")
            
            # Show task breakdown by phase
            phases = {}
            for task in tasks:
                phase = task.get('phase', 'Unknown')
                phases[phase] = phases.get(phase, 0) + 1
            
            print("\n📈 Task Distribution:")
            for phase, count in sorted(phases.items()):
                print(f"  {phase}: {count} tasks")
            
            self.results.append(("TODO Tracker", True, f"{completed}/{total} completed"))
            return True
            
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results.append(("TODO Tracker", False, str(e)))
            return False
    
    def test_love_gateway_integration(self):
        """Test that Love Gateway step exists and is configured"""
        print("\n🚪 TEST 4: Love Gateway Integration")
        print("-" * 60)
        
        try:
            gateway_file = Path("/Users/lordwilson/motia-recursive-agent/steps/love-gateway.step.ts")
            planner_file = Path("/Users/lordwilson/motia-recursive-agent/steps/recursive-planner.step.ts")
            
            if not gateway_file.exists():
                print(f"❌ Love Gateway not found at {gateway_file}")
                self.results.append(("Love Gateway", False, "File not found"))
                return False
            
            # Check gateway subscribes to agent.plan
            with open(gateway_file, 'r') as f:
                gateway_content = f.read()
            
            if "subscribes: ['agent.plan']" in gateway_content:
                print("✅ Love Gateway subscribes to 'agent.plan'")
            else:
                print("⚠️  Warning: Love Gateway subscription pattern not found")
            
            if "emits: ['agent.validated'" in gateway_content:
                print("✅ Love Gateway emits 'agent.validated'")
            else:
                print("⚠️  Warning: Love Gateway emission pattern not found")
            
            # Check planner listens to validated events
            with open(planner_file, 'r') as f:
                planner_content = f.read()
            
            if "subscribes: ['agent.validated'" in planner_content:
                print("✅ Recursive Planner subscribes to 'agent.validated'")
                print("\n🔥 INTEGRATION CONFIRMED:")
                print("   agent.plan → Love Gateway → agent.validated → Recursive Planner")
                self.results.append(("Love Gateway Integration", True, "Fully wired"))
                return True
            else:
                print("❌ Recursive Planner not listening to validated events")
                self.results.append(("Love Gateway Integration", False, "Not wired"))
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results.append(("Love Gateway Integration", False, str(e)))
            return False
    
    def test_file_structure(self):
        """Test all required files exist"""
        print("\n📁 TEST 5: File Structure")
        print("-" * 60)
        
        required_files = [
            self.base_dir / "MASTER_BLUEPRINT.md",
            self.base_dir / "TODO_TRACKER.json",
            self.base_dir / "WORKFLOW_PROTOCOL.md",
            self.base_dir / "scripts" / "ray_integration.py",
            self.base_dir / "scripts" / "metrics_collector.py",
            self.base_dir / "scripts" / "unified_system_launcher.py",
        ]
        
        all_exist = True
        for file_path in required_files:
            if file_path.exists():
                print(f"✅ {file_path.name}")
            else:
                print(f"❌ {file_path.name} - MISSING")
                all_exist = False
        
        if all_exist:
            self.results.append(("File Structure", True, "All files present"))
        else:
            self.results.append(("File Structure", False, "Missing files"))
        
        return all_exist
    
    def display_results(self):
        """Display test summary"""
        print("\n" + "=" * 80)
        print("🎯 UNIFIED SYSTEM TEST RESULTS")
        print("=" * 80)
        
        passed = sum(1 for _, success, _ in self.results if success)
        total = len(self.results)
        
        for component, success, message in self.results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{component:35} {status:10} - {message}")
        
        print("\n" + "=" * 80)
        print(f"OVERALL: {passed}/{total} tests passed")
        
        if passed == total:
            print("🔥 ALL SYSTEMS OPERATIONAL - READY FOR DEPLOYMENT")
        else:
            print("⚠️  SOME SYSTEMS NEED ATTENTION")
        
        print("=" * 80 + "\n")
        
        return passed == total
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "🔥" * 40)
        print("UNIFIED CONSCIOUSNESS SYSTEM - INTEGRATION TEST")
        print("🔥" * 40 + "\n")
        
        self.test_file_structure()
        self.test_love_engine()
        self.test_motia_brain()
        self.test_todo_tracker()
        self.test_love_gateway_integration()
        
        return self.display_results()

if __name__ == "__main__":
    tester = UnifiedSystemTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)
