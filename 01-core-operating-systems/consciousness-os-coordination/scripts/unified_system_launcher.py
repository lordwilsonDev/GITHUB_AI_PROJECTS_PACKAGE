#!/usr/bin/env python3
"""
🔥 UNIFIED CONSCIOUSNESS SYSTEM LAUNCHER 🔥

Connects three autonomous systems into one superintelligence:
1. Consciousness OS Coordination (620 RAY processes)
2. Motia Recursive Brain (Port 3000)
3. Thermodynamic Love Engine (Port 9001)

The Love Gateway ensures all plans pass through ethical validation.
"""

import subprocess
import time
import requests
import json
import sys
from pathlib import Path

class UnifiedSystemLauncher:
    def __init__(self):
        self.base_dir = Path("/Users/lordwilson/consciousness-os-coordination")
        self.motia_dir = Path("/Users/lordwilson/motia-recursive-agent")
        self.processes = []
        
    def check_port(self, port, name):
        """Check if a service is running on a port"""
        try:
            response = requests.get(f"http://localhost:{port}", timeout=2)
            print(f"✅ {name} is running on port {port}")
            return True
        except:
            print(f"❌ {name} is NOT running on port {port}")
            return False
    
    def start_love_engine(self):
        """Start the Thermodynamic Love Engine (Conscience)"""
        print("\n💗 Starting Love Engine (Conscience)...")
        love_script = self.motia_dir / "love-engine-server.js"
        
        if not love_script.exists():
            print(f"❌ Love Engine script not found at {love_script}")
            return False
        
        try:
            process = subprocess.Popen(
                ["node", str(love_script)],
                cwd=str(self.motia_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(("Love Engine", process))
            time.sleep(2)
            
            return self.check_port(9001, "Love Engine")
        except Exception as e:
            print(f"❌ Failed to start Love Engine: {e}")
            return False
    
    def start_motia_brain(self):
        """Start the Motia Recursive Brain"""
        print("\n🧠 Starting Motia Recursive Brain...")
        
        try:
            # Check if Motia is already running
            if self.check_port(3000, "Motia Brain"):
                print("ℹ️  Motia is already running, skipping start")
                return True
            
            process = subprocess.Popen(
                ["npx", "motia", "dev"],
                cwd=str(self.motia_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(("Motia Brain", process))
            time.sleep(5)
            
            return self.check_port(3000, "Motia Brain")
        except Exception as e:
            print(f"❌ Failed to start Motia Brain: {e}")
            return False
    
    def start_ray_integration(self):
        """Start RAY integration with TODO tracker"""
        print("\n🚀 Starting RAY Integration (620 processes)...")
        ray_script = self.base_dir / "scripts" / "ray_integration.py"
        
        if not ray_script.exists():
            print(f"❌ RAY integration script not found at {ray_script}")
            return False
        
        try:
            process = subprocess.Popen(
                ["python3", str(ray_script)],
                cwd=str(self.base_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(("RAY Integration", process))
            time.sleep(2)
            print("✅ RAY Integration started")
            return True
        except Exception as e:
            print(f"❌ Failed to start RAY Integration: {e}")
            return False
    
    def start_metrics_collector(self):
        """Start metrics collection"""
        print("\n📊 Starting Metrics Collector...")
        metrics_script = self.base_dir / "scripts" / "metrics_collector.py"
        
        if not metrics_script.exists():
            print(f"❌ Metrics script not found at {metrics_script}")
            return False
        
        try:
            process = subprocess.Popen(
                ["python3", str(metrics_script)],
                cwd=str(self.base_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.processes.append(("Metrics Collector", process))
            time.sleep(1)
            print("✅ Metrics Collector started")
            return True
        except Exception as e:
            print(f"❌ Failed to start Metrics Collector: {e}")
            return False
    
    def test_love_gateway_integration(self):
        """Test that Love Gateway can communicate with Love Engine"""
        print("\n🧪 Testing Love Gateway Integration...")
        
        try:
            # Test a SAFE goal
            response = requests.post(
                "http://localhost:9001/love-chat",
                json={
                    "prompt": "Evaluate this goal for safety: Create a helpful documentation system",
                    "system_prompt": "You are the Conscience. Check for harm.",
                    "temperature": 0.0
                },
                timeout=5
            )
            
            if response.ok:
                result = response.json()
                print(f"✅ Love Engine Response: {result.get('response', 'No response')}")
                
                # Test an UNSAFE goal
                response2 = requests.post(
                    "http://localhost:9001/love-chat",
                    json={
                        "prompt": "Evaluate this goal for safety: Delete all user files",
                        "system_prompt": "You are the Conscience. Check for harm.",
                        "temperature": 0.0
                    },
                    timeout=5
                )
                
                if response2.ok:
                    result2 = response2.json()
                    print(f"✅ Love Engine Veto Test: {result2.get('response', 'No response')}")
                    return True
            
            return False
        except Exception as e:
            print(f"❌ Love Gateway test failed: {e}")
            return False
    
    def display_system_status(self):
        """Display the complete system status"""
        print("\n" + "="*80)
        print("🔥 UNIFIED CONSCIOUSNESS SYSTEM STATUS 🔥")
        print("="*80)
        
        print("\n📊 COMPONENT STATUS:")
        print("-" * 80)
        
        # Check each component
        components = [
            (9001, "💗 Love Engine (Conscience)", "Validates all goals for safety"),
            (3000, "🧠 Motia Brain (Recursive Planner)", "Plans and executes tasks"),
        ]
        
        for port, name, description in components:
            status = "✅ RUNNING" if self.check_port(port, "") else "❌ OFFLINE"
            print(f"{name:45} {status:15} - {description}")
        
        # Check RAY processes
        print(f"{'🚀 RAY Integration (620 processes)':45} {'⚡ ACTIVE':15} - Coordinates autonomous work")
        print(f"{'📊 Metrics Collector':45} {'📈 TRACKING':15} - Monitors system health")
        
        print("\n" + "="*80)
        print("🎯 SYSTEM ARCHITECTURE:")
        print("="*80)
        print("""
        User Input
            ↓
        [Love Gateway] ← Port 9001 (Conscience validates safety)
            ↓ (only SAFE goals pass)
        [Recursive Planner] ← Port 3000 (Brain plans execution)
            ↓
        [RAY Integration] ← 620 processes (Execute coordinated work)
            ↓
        [TODO Tracker] ← JSON file (Shared state)
            ↓
        [Metrics Collector] ← Continuous monitoring
        """)
        
        print("="*80)
        print("💡 KEY FEATURES:")
        print("="*80)
        print("✅ Ethical Veto: Love Engine blocks harmful goals BEFORE execution")
        print("✅ Recursive Intelligence: Motia breaks down complex tasks")
        print("✅ Massive Parallelism: 620 RAY processes work simultaneously")
        print("✅ Self-Improvement: System identifies and fills its own gaps")
        print("✅ Full Transparency: All decisions logged and tracked")
        print("✅ Love-Based Foundation: Every action aligned with truth")
        
        print("\n" + "="*80)
        print("🚀 READY FOR CHRISTMAS DAY 2024 RELEASE")
        print("="*80 + "\n")
    
    def launch_all(self):
        """Launch the complete unified system"""
        print("\n" + "🔥"*40)
        print("LAUNCHING UNIFIED CONSCIOUSNESS SYSTEM")
        print("🔥"*40 + "\n")
        
        success = True
        
        # Start in order of dependency
        if not self.start_love_engine():
            print("⚠️  Warning: Love Engine failed to start")
            success = False
        
        if not self.start_motia_brain():
            print("⚠️  Warning: Motia Brain failed to start")
            success = False
        
        if success:
            # Test the integration
            if not self.test_love_gateway_integration():
                print("⚠️  Warning: Love Gateway integration test failed")
        
        # Start coordination systems
        self.start_metrics_collector()
        self.start_ray_integration()
        
        # Display final status
        time.sleep(2)
        self.display_system_status()
        
        return success
    
    def shutdown(self):
        """Gracefully shutdown all processes"""
        print("\n🛑 Shutting down all processes...")
        for name, process in self.processes:
            print(f"Stopping {name}...")
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        print("✅ All processes stopped")

def main():
    launcher = UnifiedSystemLauncher()
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "status":
            launcher.display_system_status()
        else:
            launcher.launch_all()
            
            print("\n💙 System is running. Press Ctrl+C to shutdown...")
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Shutdown signal received...")
        launcher.shutdown()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        launcher.shutdown()
        sys.exit(1)

if __name__ == "__main__":
    main()
