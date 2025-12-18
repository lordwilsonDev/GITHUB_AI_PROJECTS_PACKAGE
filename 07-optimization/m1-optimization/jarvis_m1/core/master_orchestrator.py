#!/usr/bin/env python3
"""
Master Orchestrator - Coordinates all autonomous agents in sequence
Runs the complete self-healing, self-optimizing cycle
"""

import os
import sys
import json
from datetime import datetime

# Import all agents
try:
    from discovery_agent import DiscoveryAgent
    from healing_agent import HealingAgent
    from optimization_agent import OptimizationAgent
except ImportError:
    # If running from different directory
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from discovery_agent import DiscoveryAgent
    from healing_agent import HealingAgent
    from optimization_agent import OptimizationAgent

class MasterOrchestrator:
    def __init__(self, base_path="."):
        self.base_path = base_path
        self.cycle_results = {}
        self.start_time = datetime.now()
        
    def print_header(self):
        """Print orchestrator header"""
        print("\n" + "="*70)
        print("🐍 OUROBOROS MASTER ORCHESTRATOR 🐍")
        print("Autonomous Self-Healing & Self-Optimizing System")
        print("="*70)
        print(f"\nStarted at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base path: {os.path.abspath(self.base_path)}")
        print()
    
    def run_initial_assessment(self):
        """Run initial VDR assessment"""
        print("\n" + "-"*70)
        print("🔍 PHASE 0: INITIAL SYSTEM ASSESSMENT")
        print("-"*70)
        
        # Import and run ouroboros
        try:
            sys.path.insert(0, os.path.join(self.base_path, 'core'))
            import ouroboros
            
            print("\nRunning initial VDR calculation...\n")
            initial_vdr = ouroboros.calculate_vdr(self.base_path)
            self.cycle_results['initial_vdr'] = initial_vdr
            
            return initial_vdr
        except Exception as e:
            print(f"⚠️  Error running initial assessment: {e}")
            return 0.0
    
    def run_discovery(self):
        """Run discovery agent"""
        print("\n" + "-"*70)
        print("🔍 PHASE 1: DISCOVERY")
        print("-"*70)
        
        try:
            agent = DiscoveryAgent(self.base_path)
            report = agent.run()
            self.cycle_results['discovery'] = report
            return report
        except Exception as e:
            print(f"⚠️  Discovery failed: {e}")
            return None
    
    def run_healing(self):
        """Run healing agent"""
        print("\n" + "-"*70)
        print("💉 PHASE 2: HEALING")
        print("-"*70)
        
        try:
            agent = HealingAgent(self.base_path)
            report = agent.run()
            self.cycle_results['healing'] = report
            return report
        except Exception as e:
            print(f"⚠️  Healing failed: {e}")
            return None
    
    def run_optimization(self):
        """Run optimization agent"""
        print("\n" + "-"*70)
        print("⚡ PHASE 3: OPTIMIZATION")
        print("-"*70)
        
        try:
            agent = OptimizationAgent(self.base_path)
            report = agent.run()
            self.cycle_results['optimization'] = report
            return report
        except Exception as e:
            print(f"⚠️  Optimization failed: {e}")
            return None
    
    def run_final_assessment(self):
        """Run final VDR assessment"""
        print("\n" + "-"*70)
        print("🧱 PHASE 4: FINAL ASSESSMENT")
        print("-"*70)
        
        try:
            # Reload ouroboros module to get updated code
            import importlib
            import ouroboros
            importlib.reload(ouroboros)
            
            print("\nRunning final VDR calculation...\n")
            final_vdr = ouroboros.calculate_vdr(self.base_path)
            self.cycle_results['final_vdr'] = final_vdr
            
            return final_vdr
        except Exception as e:
            print(f"⚠️  Error running final assessment: {e}")
            return 0.0
    
    def generate_summary(self):
        """Generate cycle summary"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()
        
        print("\n" + "="*70)
        print("🎉 AUTONOMOUS CYCLE COMPLETE")
        print("="*70)
        
        print(f"\n⏱️  Duration: {duration:.2f} seconds")
        
        # VDR comparison
        initial_vdr = self.cycle_results.get('initial_vdr', 0.0)
        final_vdr = self.cycle_results.get('final_vdr', 0.0)
        improvement = final_vdr - initial_vdr
        
        print(f"\n📊 VDR IMPROVEMENT:")
        print(f"   Initial VDR: {initial_vdr:.3f}")
        print(f"   Final VDR:   {final_vdr:.3f}")
        print(f"   Change:      {improvement:+.3f} ({(improvement/max(initial_vdr, 0.001))*100:+.1f}%)")
        
        # Agent summaries
        if 'discovery' in self.cycle_results:
            disc = self.cycle_results['discovery']
            print(f"\n🔍 Discovery:")
            print(f"   Governance cycles found: {disc.get('governance_cycles', 0)}")
            print(f"   Issues identified: {len(disc.get('issues_found', []))}")
        
        if 'healing' in self.cycle_results:
            heal = self.cycle_results['healing']
            print(f"\n💉 Healing:")
            print(f"   Fixes applied: {heal.get('total_fixes', 0)}")
        
        if 'optimization' in self.cycle_results:
            opt = self.cycle_results['optimization']
            print(f"\n⚡ Optimization:")
            print(f"   Optimizations: {opt.get('total_optimizations', 0)}")
            print(f"   Density reduced: {opt.get('density_reduced', 0)} items")
        
        # System status
        print(f"\n🎯 SYSTEM STATUS:")
        if final_vdr >= 1.0:
            print("   ✅ ANTIFRAGILE - System has free energy")
            print("   🚀 Ready for autonomous deployment")
        elif final_vdr >= 0.8:
            print("   🟡 HEALTHY - System is stable")
            print("   🔧 Minor optimizations recommended")
        elif final_vdr >= 0.5:
            print("   🟠 MODERATE - System needs attention")
            print("   ⚠️  Run another healing cycle")
        else:
            print("   🔴 CRITICAL - System requires intervention")
            print("   ⚠️  Manual review recommended")
        
        # Save full report
        report_path = os.path.join(self.base_path, 'orchestrator_report.json')
        full_report = {
            'timestamp': end_time.isoformat(),
            'duration_seconds': duration,
            'initial_vdr': initial_vdr,
            'final_vdr': final_vdr,
            'improvement': improvement,
            'cycle_results': self.cycle_results
        }
        
        with open(report_path, 'w') as f:
            json.dump(full_report, f, indent=2)
        
        print(f"\n📊 Full report saved to: {report_path}")
        print("\n" + "="*70)
        
        return full_report
    
    def run(self):
        """Run complete orchestration cycle"""
        self.print_header()
        
        # Run all phases
        self.run_initial_assessment()
        self.run_discovery()
        self.run_healing()
        self.run_optimization()
        self.run_final_assessment()
        
        # Generate summary
        report = self.generate_summary()
        
        return report

if __name__ == "__main__":
    # Determine base path
    if len(sys.argv) > 1:
        base_path = sys.argv[1]
    else:
        # Go up one level from core directory
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    orchestrator = MasterOrchestrator(base_path)
    orchestrator.run()
