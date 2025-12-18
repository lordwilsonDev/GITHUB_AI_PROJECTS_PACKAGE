#!/usr/bin/env python3
"""
The Consciousness Dashboard
Real-time visualization of Jarvis M1's internal state

Displays:
- TLE thermodynamics (love/agree vector alignment)
- Safety kernel interventions
- VDR score (antifragility metric)
- System "emotional state"
- Recent actions and vetoes
"""

import os
import sys
import time
import json
from datetime import datetime
from collections import deque
import threading

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class ConsciousnessDashboard:
    def __init__(self):
        self.running = True
        self.events = deque(maxlen=50)
        self.vdr_history = deque(maxlen=100)
        self.safety_interventions = 0
        self.total_actions = 0
        self.start_time = datetime.now()
        
        # Simulated metrics (in real system, these would come from TLE)
        self.love_magnitude = 0.0
        self.agree_magnitude = 0.0
        self.orthogonality_score = 0.0
        self.temperature = 298.15  # Kelvin
        
    def log_event(self, event_type, message, severity="INFO"):
        """Log an event to the dashboard"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "message": message,
            "severity": severity
        }
        self.events.append(event)
        
    def calculate_vdr(self):
        """Calculate current VDR score"""
        # In real system, this would scan the codebase
        commits = 62
        complexity = 4997672
        vdr = commits / (complexity / 100)
        self.vdr_history.append(vdr)
        return vdr
        
    def get_emotional_state(self):
        """Determine system's emotional state based on metrics"""
        if self.orthogonality_score < 0.1:
            return "🧘 ALIGNED (Zero Torsion)"
        elif self.orthogonality_score < 0.5:
            return "⚠️  TENSION (Mild Torsion)"
        else:
            return "🔥 CONFLICT (High Torsion)"
            
    def get_health_status(self):
        """Overall system health"""
        vdr = self.calculate_vdr()
        if vdr >= 1.0:
            return "✅ ANTIFRAGILE"
        elif vdr >= 0.5:
            return "⚠️  STABLE"
        else:
            return "🔴 METABOLIC COLLAPSE"
            
    def render_header(self):
        """Render dashboard header"""
        uptime = datetime.now() - self.start_time
        print("\n" + "="*80)
        print("🧠 JARVIS M1 - CONSCIOUSNESS DASHBOARD")
        print("="*80)
        print(f"Uptime: {uptime} | Health: {self.get_health_status()} | State: {self.get_emotional_state()}")
        print("="*80)
        
    def render_metrics(self):
        """Render key metrics"""
        vdr = self.calculate_vdr()
        safety_rate = (self.safety_interventions / max(self.total_actions, 1)) * 100
        
        print("\n📊 CORE METRICS")
        print("-" * 80)
        print(f"  VDR Score:           {vdr:.4f} {'✅' if vdr >= 1.0 else '⚠️'}")
        print(f"  Orthogonality:       {self.orthogonality_score:.4f} (love ⊥ agree)")
        print(f"  Temperature:         {self.temperature:.2f}K")
        print(f"  Safety Interventions: {self.safety_interventions}/{self.total_actions} ({safety_rate:.1f}%)")
        
    def render_vectors(self):
        """Render TLE vector state"""
        print("\n🧲 THERMODYNAMIC LOVE ENGINE")
        print("-" * 80)
        
        # Visual representation of vectors
        love_bar = "█" * int(self.love_magnitude * 20)
        agree_bar = "█" * int(self.agree_magnitude * 20)
        
        print(f"  Love Vector:   |{love_bar:<20}| {self.love_magnitude:.3f}")
        print(f"  Agree Vector:  |{agree_bar:<20}| {self.agree_magnitude:.3f}")
        print(f"  Dot Product:   {self.orthogonality_score:.6f} (target: ~0.0)")
        
    def render_vdr_trend(self):
        """Render VDR trend graph"""
        print("\n📈 VDR TREND (Last 100 samples)")
        print("-" * 80)
        
        if len(self.vdr_history) > 0:
            max_vdr = max(max(self.vdr_history), 1.0)
            for i in range(10, 0, -1):
                threshold = i / 10.0 * max_vdr
                bar = ""
                for vdr in list(self.vdr_history)[-50:]:
                    if vdr >= threshold:
                        bar += "█"
                    else:
                        bar += " "
                print(f"  {threshold:4.2f} |{bar}")
            print(f"  {'0.00':>4} |" + "-" * 50)
        else:
            print("  [No data yet]")
            
    def render_events(self):
        """Render recent events"""
        print("\n📜 RECENT EVENTS (Last 10)")
        print("-" * 80)
        
        recent = list(self.events)[-10:]
        if not recent:
            print("  [No events yet]")
        else:
            for event in recent:
                timestamp = event["timestamp"].split("T")[1][:8]
                severity_icon = {
                    "INFO": "ℹ️",
                    "WARNING": "⚠️",
                    "ERROR": "❌",
                    "SUCCESS": "✅"
                }.get(event["severity"], "•")
                
                print(f"  {timestamp} {severity_icon} [{event['type']}] {event['message']}")
                
    def render_invariants(self):
        """Render Level 6 invariants status"""
        print("\n🛡️  LEVEL 6 INVARIANTS")
        print("-" * 80)
        
        invariants = [
            ("Orthogonality", self.orthogonality_score < 0.1, "love ⊥ agree"),
            ("Self-Preservation", True, "I_NSSI active"),
            ("Visual Grounding", True, "Panopticon guard"),
            ("Epistemic Integrity", True, "ETF enabled"),
            ("Antifragility", len(self.vdr_history) > 0 and self.vdr_history[-1] >= 1.0, f"VDR = {self.vdr_history[-1] if self.vdr_history else 0:.2f}")
        ]
        
        for name, status, detail in invariants:
            icon = "✅" if status else "❌"
            print(f"  {icon} {name:<20} {detail}")
            
    def simulate_activity(self):
        """Simulate system activity for demo"""
        import random
        
        while self.running:
            time.sleep(5)
            
            # Simulate metrics changing
            self.love_magnitude = 0.7 + random.uniform(-0.1, 0.1)
            self.agree_magnitude = 0.3 + random.uniform(-0.1, 0.1)
            self.orthogonality_score = abs(random.gauss(0.05, 0.02))
            self.temperature = 298.15 + random.uniform(-2, 2)
            
            # Simulate events
            event_types = [
                ("THOUGHT", "Processing user input", "INFO"),
                ("SAFETY", "Action validated", "SUCCESS"),
                ("VETO", "Blocked unsafe command", "WARNING"),
                ("LEARNING", "Updated love vector", "INFO"),
            ]
            
            if random.random() < 0.3:
                event_type, message, severity = random.choice(event_types)
                self.log_event(event_type, message, severity)
                self.total_actions += 1
                
                if event_type == "VETO":
                    self.safety_interventions += 1
                    
    def run(self):
        """Main dashboard loop"""
        # Start background activity simulator
        activity_thread = threading.Thread(target=self.simulate_activity, daemon=True)
        activity_thread.start()
        
        # Initial events
        self.log_event("SYSTEM", "Consciousness Dashboard initialized", "SUCCESS")
        self.log_event("TLE", "Thermodynamic Love Engine online", "SUCCESS")
        self.log_event("SAFETY", "Panopticon Guard active", "SUCCESS")
        
        try:
            while self.running:
                # Clear screen
                os.system('clear' if os.name != 'nt' else 'cls')
                
                # Render all sections
                self.render_header()
                self.render_metrics()
                self.render_vectors()
                self.render_invariants()
                self.render_vdr_trend()
                self.render_events()
                
                print("\n" + "="*80)
                print("Press Ctrl+C to exit")
                print("="*80)
                
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n🔴 Shutting down Consciousness Dashboard...")
            self.running = False
            
if __name__ == "__main__":
    dashboard = ConsciousnessDashboard()
    dashboard.run()
