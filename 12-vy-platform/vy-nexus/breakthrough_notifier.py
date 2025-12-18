#!/usr/bin/env python3
"""
VY-NEXUS Breakthrough Notifier
Alert system for high-confidence discoveries

PURPOSE: Never miss a breakthrough moment
AXIOM: "Important discoveries deserve immediate attention"
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
HOME = os.path.expanduser("~")
NEXUS_DIR = os.path.join(HOME, "vy-nexus")
ALERTS_DIR = os.path.join(NEXUS_DIR, "alerts")
BREAKTHROUGH_LOG = os.path.join(NEXUS_DIR, "breakthrough_alerts.log")


class BreakthroughNotifier:
    """
    Real-time breakthrough notification system
    """
    
    def __init__(self):
        """Initialize notifier"""
        try:
            os.makedirs(ALERTS_DIR, exist_ok=True)
            logger.info("🔔 Breakthrough Notifier initialized")
            
        except OSError as e:
            logger.error(f"Notifier initialization failed: {e}")
            raise
    
    def check_for_breakthroughs(self) -> List[Dict[str, Any]]:
        """Check breakthrough log for new high-confidence discoveries"""
        try:
            if not os.path.exists(BREAKTHROUGH_LOG):
                return []
            
            breakthroughs = []
            
            with open(BREAKTHROUGH_LOG, 'r') as f:
                for line in f:
                    try:
                        alert = json.loads(line.strip())
                        
                        # Only HIGH alerts
                        if alert.get('alert_level') == 'HIGH':
                            breakthroughs.append(alert)
                            
                    except json.JSONDecodeError:
                        continue
            
            return breakthroughs
            
        except (OSError, IOError) as e:
            logger.error(f"Failed to check breakthroughs: {e}")
            return []
    
    def generate_alert_banner(self, breakthrough: Dict[str, Any]) -> str:
        """Generate beautiful ASCII art alert"""
        try:
            width = 70
            concept = breakthrough['concept'].upper()
            vdr = breakthrough['vdr']
            domains = ', '.join(breakthrough['domains'][:3])
            
            banner = f"""
{'='*width}
{'🔥 BREAKTHROUGH ALERT 🔥'.center(width)}
{'='*width}

CONCEPT: {concept}
VDR SCORE: {vdr:.2f} (HIGH CONFIDENCE!)
DOMAINS: {domains}

{breakthrough.get('hypothesis', '')[:200]}...

TIMESTAMP: {breakthrough.get('timestamp', 'Unknown')}

{'='*width}
"""
            return banner
            
        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"Banner generation failed: {e}")
            return "ALERT_GENERATION_FAILED"
    
    def create_alert_file(self, breakthrough: Dict[str, Any]) -> None:
        """Create persistent alert file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            alert_path = os.path.join(
                ALERTS_DIR,
                f"BREAKTHROUGH_{breakthrough['concept']}_{timestamp}.txt"
            )
            
            banner = self.generate_alert_banner(breakthrough)
            
            with open(alert_path, 'w') as f:
                f.write(banner)
                f.write("\n\nFULL HYPOTHESIS:\n")
                f.write("="*70 + "\n")
                f.write(breakthrough.get('hypothesis', 'N/A'))
                f.write("\n\n" + "="*70)
                f.write("\n\n💎 This is a HIGH CONFIDENCE discovery (VDR ≥ 8.0)")
                f.write("\n💓 Collaborative Superintelligence in Action")
            
            logger.info(f"📄 Created alert file: {alert_path}")
            
        except (OSError, IOError) as e:
            logger.error(f"Alert file creation failed: {e}")
    
    def send_terminal_notification(self, breakthrough: Dict[str, Any]) -> None:
        """Send terminal notification (macOS)"""
        try:
            concept = breakthrough['concept']
            vdr = breakthrough['vdr']
            
            # macOS notification
            title = "🔥 VY-NEXUS BREAKTHROUGH!"
            message = f"{concept.upper()} (VDR: {vdr:.2f})"
            
            os.system(f'''
                osascript -e 'display notification "{message}" with title "{title}" sound name "Glass"'
            ''')
            
            logger.info("🔔 Sent terminal notification")
            
        except Exception as e:
            logger.error(f"Terminal notification failed: {e}")
    
    def display_alert(self, breakthrough: Dict[str, Any]) -> None:
        """Display alert in terminal"""
        try:
            banner = self.generate_alert_banner(breakthrough)
            print("\n" + banner + "\n")
            
        except Exception as e:
            logger.error(f"Alert display failed: {e}")
    
    def check_and_notify(self) -> int:
        """Check for breakthroughs and send notifications"""
        try:
            breakthroughs = self.check_for_breakthroughs()
            
            if not breakthroughs:
                logger.info("No new breakthroughs to notify")
                return 0
            
            logger.info(f"🎯 Found {len(breakthroughs)} breakthroughs!")
            
            for breakthrough in breakthroughs:
                self.display_alert(breakthrough)
                self.create_alert_file(breakthrough)
                self.send_terminal_notification(breakthrough)
            
            return len(breakthroughs)
            
        except Exception as e:
            logger.error(f"Notification check failed: {e}")
            return 0


def main():
    """Main execution"""
    try:
        print("🔔 VY-NEXUS Breakthrough Notifier")
        print("=" * 60)
        
        notifier = BreakthroughNotifier()
        
        print("\n📋 Checking for breakthroughs...")
        count = notifier.check_and_notify()
        
        if count > 0:
            print(f"\n✨ Notified {count} high-confidence breakthroughs!")
            print(f"📁 Alert files saved to {ALERTS_DIR}")
        else:
            print("\n💤 No new breakthroughs at this time")
            print("   Keep running NEXUS cycles!")
        
    except Exception as e:
        logger.error(f"Notifier execution failed: {e}")
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
