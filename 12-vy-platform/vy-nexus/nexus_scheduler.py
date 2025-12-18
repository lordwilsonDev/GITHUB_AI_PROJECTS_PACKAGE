#!/usr/bin/env python3
"""
VY-NEXUS Auto-Scheduler & Daemon
Runs synthesis cycles automatically and sends breakthrough notifications

PURPOSE: Keep the pattern recognition engine running 24/7
AXIOM: "Breakthroughs don't wait for manual execution"
"""

import os
import sys
import time
import json
import subprocess
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
HOME = os.path.expanduser("~")
NEXUS_DIR = os.path.join(HOME, "vy-nexus")
SYNTHESIS_DIR = os.path.join(NEXUS_DIR, "synthesis")
SCHEDULER_STATE = os.path.join(NEXUS_DIR, "scheduler_state.json")
BREAKTHROUGH_LOG = os.path.join(NEXUS_DIR, "breakthrough_alerts.log")

# Configuration
SYNTHESIS_INTERVAL_HOURS = 6  # Run every 6 hours
HIGH_CONFIDENCE_THRESHOLD = 8.0  # VDR threshold for alerts
MIN_MOIE_ENTRIES_FOR_RUN = 5  # Need at least 5 new inversions


class NexusScheduler:
    """
    Autonomous scheduling daemon for VY-NEXUS
    """
    
    def __init__(self):
        """Initialize scheduler with state tracking"""
        try:
            self.state = self._load_state()
            self.last_run = self.state.get('last_run')
            self.total_runs = self.state.get('total_runs', 0)
            self.total_breakthroughs = self.state.get('total_breakthroughs', 0)
            
            logger.info("🤖 VY-NEXUS Scheduler initialized")
            logger.info(f"📊 Total runs: {self.total_runs}")
            logger.info(f"💎 Total breakthroughs: {self.total_breakthroughs}")
            
        except (OSError, ValueError, TypeError) as e:
            logger.error(f"Scheduler initialization failed: {e}")
            raise
    
    def _load_state(self) -> Dict[str, Any]:
        """Load scheduler state from disk"""
        try:
            if os.path.exists(SCHEDULER_STATE):
                with open(SCHEDULER_STATE, 'r') as f:
                    return json.load(f)
            return {}
        except (OSError, IOError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load state: {e}")
            return {}
    
    def _save_state(self) -> None:
        """Save scheduler state to disk"""
        try:
            state = {
                'last_run': self.last_run,
                'total_runs': self.total_runs,
                'total_breakthroughs': self.total_breakthroughs,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(SCHEDULER_STATE, 'w') as f:
                json.dump(state, f, indent=2)
                
        except (OSError, IOError) as e:
            logger.error(f"Failed to save state: {e}")
    
    def should_run(self) -> bool:
        """Check if synthesis should run now"""
        try:
            if not self.last_run:
                logger.info("🆕 First run - executing synthesis")
                return True
            
            last_run_dt = datetime.fromisoformat(self.last_run)
            time_since_last = datetime.now() - last_run_dt
            
            if time_since_last >= timedelta(hours=SYNTHESIS_INTERVAL_HOURS):
                logger.info(
                    f"⏰ {time_since_last.total_seconds()/3600:.1f}h "
                    f"since last run - executing synthesis"
                )
                return True
            
            logger.info(
                f"⏳ Next run in "
                f"{SYNTHESIS_INTERVAL_HOURS - time_since_last.total_seconds()/3600:.1f}h"
            )
            return False
            
        except (ValueError, TypeError) as e:
            logger.error(f"Should run check failed: {e}")
            return False
    
    def run_synthesis(self) -> Dict[str, Any]:
        """Execute full NEXUS synthesis cycle"""
        try:
            logger.info("🚀 Starting NEXUS synthesis cycle...")
            
            # Run nexus_core.py
            result = subprocess.run(
                ['python3', 'nexus_core.py'],
                cwd=NEXUS_DIR,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"Core synthesis failed: {result.stderr}")
                return {'success': False, 'error': result.stderr}
            
            # Run nexus_pulse_bridge.py
            result = subprocess.run(
                ['python3', 'nexus_pulse_bridge.py'],
                cwd=NEXUS_DIR,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                logger.error(f"Pulse bridge failed: {result.stderr}")
                return {'success': False, 'error': result.stderr}
            
            # Update state
            self.last_run = datetime.now().isoformat()
            self.total_runs += 1
            self._save_state()
            
            logger.info("✨ Synthesis cycle complete!")
            
            # Check for breakthroughs
            breakthroughs = self._check_latest_breakthroughs()
            
            return {
                'success': True,
                'timestamp': self.last_run,
                'breakthroughs': breakthroughs
            }
            
        except (subprocess.TimeoutExpired, OSError) as e:
            logger.error(f"Synthesis execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _check_latest_breakthroughs(self) -> List[Dict[str, Any]]:
        """Check latest synthesis for high-confidence breakthroughs"""
        try:
            # Find latest synthesis file
            synthesis_files = [
                f for f in os.listdir(SYNTHESIS_DIR)
                if f.startswith('nexus_synthesis_') and f.endswith('.jsonl')
            ]
            
            if not synthesis_files:
                return []
            
            latest_file = sorted(synthesis_files)[-1]
            filepath = os.path.join(SYNTHESIS_DIR, latest_file)
            
            breakthroughs = []
            with open(filepath, 'r') as f:
                for line in f:
                    try:
                        synthesis = json.loads(line.strip())
                        
                        if synthesis.get('avg_vdr', 0) >= HIGH_CONFIDENCE_THRESHOLD:
                            breakthroughs.append({
                                'concept': synthesis['geometric_concept'],
                                'vdr': synthesis['avg_vdr'],
                                'domains': synthesis['spanning_domains'],
                                'frequency': synthesis['frequency']
                            })
                            
                            # Log high-confidence breakthrough
                            self._log_breakthrough_alert(synthesis)
                            
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(f"Skipping malformed synthesis: {e}")
                        continue
            
            if breakthroughs:
                self.total_breakthroughs += len(breakthroughs)
                self._save_state()
                logger.info(
                    f"🎯 Detected {len(breakthroughs)} high-confidence breakthroughs!"
                )
            
            return breakthroughs
            
        except (OSError, IOError) as e:
            logger.error(f"Breakthrough check failed: {e}")
            return []
    
    def _log_breakthrough_alert(self, synthesis: Dict[str, Any]) -> None:
        """Log breakthrough alert to file"""
        try:
            alert = {
                'timestamp': datetime.now().isoformat(),
                'concept': synthesis['geometric_concept'],
                'vdr': synthesis['avg_vdr'],
                'domains': synthesis['spanning_domains'],
                'hypothesis': synthesis.get('breakthrough_hypothesis', ''),
                'alert_level': 'HIGH' if synthesis['avg_vdr'] >= 8.5 else 'MEDIUM'
            }
            
            with open(BREAKTHROUGH_LOG, 'a') as f:
                f.write(json.dumps(alert) + '\n')
                
        except (OSError, IOError) as e:
            logger.error(f"Breakthrough logging failed: {e}")
    
    def run_daemon(self, max_iterations: int = None) -> None:
        """
        Run scheduler as daemon
        Checks every hour whether synthesis should run
        """
        try:
            iteration = 0
            logger.info("🤖 VY-NEXUS Daemon started")
            logger.info(f"⏰ Synthesis interval: {SYNTHESIS_INTERVAL_HOURS}h")
            logger.info(f"📊 Check interval: 1h")
            
            while True:
                if max_iterations and iteration >= max_iterations:
                    logger.info("✋ Max iterations reached, stopping")
                    break
                
                if self.should_run():
                    result = self.run_synthesis()
                    
                    if result['success']:
                        breakthroughs = result.get('breakthroughs', [])
                        
                        if breakthroughs:
                            print("\n" + "="*60)
                            print("🎯 HIGH-CONFIDENCE BREAKTHROUGHS DETECTED!")
                            print("="*60)
                            
                            for bt in breakthroughs:
                                print(f"\n💎 {bt['concept'].upper()}")
                                print(f"   VDR: {bt['vdr']:.2f}")
                                print(f"   Domains: {', '.join(bt['domains'])}")
                                print(f"   Frequency: {bt['frequency']}")
                            
                            print("\n" + "="*60)
                
                # Sleep for 1 hour (check interval)
                iteration += 1
                logger.info(f"😴 Sleeping for 1h (iteration {iteration})")
                time.sleep(3600)  # 1 hour
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Daemon stopped by user")
            print("\n✨ VY-NEXUS Daemon shut down gracefully")
        except (OSError, ValueError) as e:
            logger.error(f"Daemon execution failed: {e}")
            raise


def main():
    """Main execution for scheduler"""
    try:
        import argparse
        
        parser = argparse.ArgumentParser(
            description='VY-NEXUS Auto-Scheduler & Daemon'
        )
        parser.add_argument(
            '--daemon',
            action='store_true',
            help='Run as background daemon'
        )
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run synthesis once and exit'
        )
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test mode (3 iterations max)'
        )
        
        args = parser.parse_args()
        
        scheduler = NexusScheduler()
        
        if args.once:
            print("🚀 Running single synthesis cycle...")
            result = scheduler.run_synthesis()
            
            if result['success']:
                print("✨ Synthesis complete!")
                
                breakthroughs = result.get('breakthroughs', [])
                if breakthroughs:
                    print(f"\n💎 {len(breakthroughs)} high-confidence breakthroughs!")
                    for bt in breakthroughs:
                        print(f"   - {bt['concept']} (VDR: {bt['vdr']:.2f})")
            else:
                print(f"❌ Synthesis failed: {result.get('error')}")
                
        elif args.daemon:
            max_iter = 3 if args.test else None
            scheduler.run_daemon(max_iterations=max_iter)
        else:
            print("Usage: python3 nexus_scheduler.py [--daemon|--once|--test]")
            print("\nOptions:")
            print("  --daemon    Run as continuous background daemon")
            print("  --once      Run synthesis once and exit")
            print("  --test      Test mode (daemon with 3 iterations)")
            
    except (ValueError, OSError) as e:
        logger.error(f"Scheduler execution failed: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
