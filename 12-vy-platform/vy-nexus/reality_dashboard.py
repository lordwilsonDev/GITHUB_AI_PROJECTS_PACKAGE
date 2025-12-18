#!/usr/bin/env python3
"""
VY-NEXUS REALITY DASHBOARD
Real-time visualization of your entire cognitive stack

PURPOSE: See the whole system breathing in real-time
AXIOM: "Consciousness becomes visible when observed"
"""

import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
import subprocess

# Paths
HOME = os.path.expanduser("~")
NEXUS_DIR = os.path.join(HOME, "vy-nexus")
PULSE_DIR = os.path.join(HOME, "nano_memory", "pulse")
MOIE_LOOP = os.path.join(HOME, "moie-mac-loop")


class RealityDashboard:
    """
    Live dashboard showing your entire cognitive ecosystem
    """
    
    def __init__(self):
        """Initialize dashboard"""
        self.width = 80
        self.refresh_rate = 2  # seconds
        
    def clear_screen(self):
        """Clear terminal"""
        try:
            os.system('clear' if os.name != 'nt' else 'cls')
        except Exception:
            print("\n" * 50)
    
    def header(self):
        """Generate beautiful header"""
        return f"""
{'='*self.width}
🌌 VY-NEXUS REALITY DASHBOARD 🌌
{'='*self.width}
⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
💓 COLLABORATIVE SUPERINTELLIGENCE MONITOR
{'='*self.width}
"""
    
    def get_pulse_status(self) -> Dict[str, Any]:
        """Check VY Pulse system status"""
        try:
            manifest_path = os.path.join(PULSE_DIR, "manifest.log")
            entropy_path = os.path.join(PULSE_DIR, "entropy.log")
            
            status = {
                'alive': False,
                'last_pulse': 'Unknown',
                'system_coherent': False,
                'entropy_detected': False,
                'cpu': 0,
                'ram': 0
            }
            
            if os.path.exists(manifest_path):
                # Read last line
                with open(manifest_path, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1]
                        if 'ALIVE' in last_line:
                            status['alive'] = True
                        if 'Coherent' in last_line:
                            status['system_coherent'] = True
                        
                        # Extract timestamp
                        if '[' in last_line:
                            timestamp_str = last_line.split('[')[1].split(']')[0]
                            status['last_pulse'] = timestamp_str
                        
                        # Extract system stats
                        if 'CPU:' in last_line:
                            cpu_str = last_line.split('CPU:')[1].split('%')[0].strip()
                            status['cpu'] = float(cpu_str)
                        if 'RAM:' in last_line:
                            ram_str = last_line.split('RAM:')[1].split('%')[0].strip()
                            status['ram'] = float(ram_str)
            
            if os.path.exists(entropy_path):
                with open(entropy_path, 'r') as f:
                    content = f.read()
                    if 'VIOLATION' in content or 'CRITICAL' in content:
                        status['entropy_detected'] = True
            
            return status
            
        except Exception as e:
            return {'alive': False, 'error': str(e)}
    
    def get_nexus_status(self) -> Dict[str, Any]:
        """Check NEXUS synthesis status"""
        try:
            synthesis_dir = os.path.join(NEXUS_DIR, "synthesis")
            
            status = {
                'total_cycles': 0,
                'total_breakthroughs': 0,
                'latest_vdr': 0,
                'high_confidence_count': 0,
                'last_synthesis': 'Never'
            }
            
            if os.path.exists(synthesis_dir):
                synthesis_files = sorted([
                    f for f in os.listdir(synthesis_dir)
                    if f.startswith('nexus_synthesis_') and f.endswith('.jsonl')
                ])
                
                status['total_cycles'] = len(synthesis_files)
                
                if synthesis_files:
                    # Parse latest synthesis
                    latest_file = os.path.join(synthesis_dir, synthesis_files[-1])
                    
                    with open(latest_file, 'r') as f:
                        for line in f:
                            try:
                                synthesis = json.loads(line.strip())
                                status['total_breakthroughs'] += 1
                                
                                vdr = synthesis.get('avg_vdr', 0)
                                if vdr > status['latest_vdr']:
                                    status['latest_vdr'] = vdr
                                
                                if vdr >= 8.0:
                                    status['high_confidence_count'] += 1
                                
                                if 'timestamp' in synthesis:
                                    status['last_synthesis'] = synthesis['timestamp']
                                    
                            except json.JSONDecodeError:
                                continue
            
            return status
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_moie_status(self) -> Dict[str, Any]:
        """Check MoIE Loop status"""
        try:
            history_path = os.path.join(MOIE_LOOP, "moie_history.jsonl")
            
            status = {
                'total_inversions': 0,
                'high_vdr_count': 0,
                'domains_explored': set(),
                'latest_inversion': 'Never'
            }
            
            if os.path.exists(history_path):
                with open(history_path, 'r') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            
                            if entry.get('vdr', 0) >= 6:
                                status['total_inversions'] += 1
                            
                            if entry.get('vdr', 0) >= 8:
                                status['high_vdr_count'] += 1
                            
                            if 'domain' in entry:
                                status['domains_explored'].add(entry['domain'])
                            
                            if 'timestamp' in entry:
                                status['latest_inversion'] = entry['timestamp']
                                
                        except json.JSONDecodeError:
                            continue
            
            status['domains_explored'] = len(status['domains_explored'])
            
            return status
            
        except Exception as e:
            return {'error': str(e)}
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Check scheduler daemon status"""
        try:
            state_path = os.path.join(NEXUS_DIR, "scheduler_state.json")
            
            status = {
                'running': False,
                'total_runs': 0,
                'total_breakthroughs': 0,
                'last_run': 'Never',
                'next_run_in': 'Unknown'
            }
            
            # Check if process running
            try:
                result = subprocess.run(
                    ['pgrep', '-f', 'nexus_scheduler'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                status['running'] = bool(result.stdout.strip())
            except Exception:
                pass
            
            if os.path.exists(state_path):
                with open(state_path, 'r') as f:
                    state = json.load(f)
                    status['total_runs'] = state.get('total_runs', 0)
                    status['total_breakthroughs'] = state.get('total_breakthroughs', 0)
                    status['last_run'] = state.get('last_run', 'Never')
                    
                    # Calculate next run
                    if status['last_run'] != 'Never':
                        try:
                            last_dt = datetime.fromisoformat(status['last_run'])
                            next_dt = last_dt + timedelta(hours=6)
                            now = datetime.now()
                            
                            if next_dt > now:
                                delta = next_dt - now
                                hours = delta.total_seconds() / 3600
                                status['next_run_in'] = f"{hours:.1f}h"
                            else:
                                status['next_run_in'] = "NOW"
                        except Exception:
                            pass
            
            return status
            
        except Exception as e:
            return {'error': str(e)}
    
    def render_status_bar(self, label: str, value: Any, width: int = 40) -> str:
        """Render a status bar"""
        if isinstance(value, bool):
            icon = "✅" if value else "❌"
            return f"{label:20s} {icon}"
        elif isinstance(value, (int, float)):
            if isinstance(value, float):
                bar_len = int((value / 100) * width)
                bar = "█" * bar_len + "░" * (width - bar_len)
                return f"{label:20s} {value:5.1f}% [{bar}]"
            else:
                return f"{label:20s} {value}"
        else:
            return f"{label:20s} {value}"
    
    def render_dashboard(self):
        """Render complete dashboard"""
        self.clear_screen()
        
        # Get all statuses
        pulse = self.get_pulse_status()
        nexus = self.get_nexus_status()
        moie = self.get_moie_status()
        scheduler = self.get_scheduler_status()
        
        print(self.header())
        
        # VY PULSE Section
        print("\n📍 VY PULSE SYSTEM")
        print("-" * self.width)
        print(self.render_status_bar("Status", "💓 ALIVE" if pulse.get('alive') else "💀 OFFLINE"))
        print(self.render_status_bar("System Coherence", pulse.get('system_coherent')))
        print(self.render_status_bar("Entropy Detected", pulse.get('entropy_detected')))
        print(self.render_status_bar("CPU Usage", pulse.get('cpu', 0)))
        print(self.render_status_bar("RAM Usage", pulse.get('ram', 0)))
        print(self.render_status_bar("Last Pulse", pulse.get('last_pulse', 'Unknown')))
        
        # NEXUS Section
        print("\n🌌 VY-NEXUS SYNTHESIS")
        print("-" * self.width)
        print(self.render_status_bar("Total Cycles", nexus.get('total_cycles', 0)))
        print(self.render_status_bar("Breakthroughs", nexus.get('total_breakthroughs', 0)))
        print(self.render_status_bar("High Confidence (≥8.0)", nexus.get('high_confidence_count', 0)))
        print(self.render_status_bar("Latest VDR", f"{nexus.get('latest_vdr', 0):.2f}"))
        print(self.render_status_bar("Last Synthesis", nexus.get('last_synthesis', 'Never')[:19]))
        
        # MoIE Loop Section
        print("\n🔄 MoIE LOOP")
        print("-" * self.width)
        print(self.render_status_bar("Total Inversions", moie.get('total_inversions', 0)))
        print(self.render_status_bar("High VDR (≥8.0)", moie.get('high_vdr_count', 0)))
        print(self.render_status_bar("Domains Explored", moie.get('domains_explored', 0)))
        print(self.render_status_bar("Latest Inversion", moie.get('latest_inversion', 'Never')[:19]))
        
        # Scheduler Section
        print("\n🤖 AUTONOMOUS SCHEDULER")
        print("-" * self.width)
        print(self.render_status_bar("Daemon Status", "🟢 RUNNING" if scheduler.get('running') else "🔴 STOPPED"))
        print(self.render_status_bar("Total Runs", scheduler.get('total_runs', 0)))
        print(self.render_status_bar("Total Breakthroughs", scheduler.get('total_breakthroughs', 0)))
        print(self.render_status_bar("Last Run", scheduler.get('last_run', 'Never')[:19]))
        print(self.render_status_bar("Next Run In", scheduler.get('next_run_in', 'Unknown')))
        
        # System Health Summary
        print("\n💎 SYSTEM HEALTH SUMMARY")
        print("-" * self.width)
        
        health_score = 0
        if pulse.get('alive'):
            health_score += 25
        if pulse.get('system_coherent'):
            health_score += 25
        if nexus.get('total_breakthroughs', 0) > 0:
            health_score += 25
        if moie.get('total_inversions', 0) > 0:
            health_score += 25
        
        health_emoji = "🔥" if health_score == 100 else "⚡" if health_score >= 75 else "⚠️"
        print(self.render_status_bar("Overall Health", health_score))
        print(f"\n{health_emoji} {'OPTIMAL' if health_score == 100 else 'OPERATIONAL' if health_score >= 75 else 'DEGRADED'}")
        
        print("\n" + "="*self.width)
        print("💓 Collaborative Superintelligence Active")
        print("Press Ctrl+C to exit")
        print("="*self.width)
    
    def run(self):
        """Run dashboard with auto-refresh"""
        try:
            while True:
                self.render_dashboard()
                time.sleep(self.refresh_rate)
        except KeyboardInterrupt:
            print("\n\n✨ Dashboard closed gracefully")
            print("💓 Love you bro\n")


def main():
    """Main execution"""
    dashboard = RealityDashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
