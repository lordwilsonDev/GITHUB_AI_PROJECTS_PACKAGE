#!/usr/bin/env python3
"""
VY-NEXUS → Motia Integration Bridge
Connects NEXUS breakthrough discoveries to Motia orchestration layer

PURPOSE: Close the full ecosystem loop
AXIOM: "Breakthroughs must flow through all layers of the stack"
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
SYNTHESIS_DIR = os.path.join(NEXUS_DIR, "synthesis")
MOIE_LOOP_DIR = os.path.join(HOME, "moie-mac-loop")
EXPERIENCE_LEDGER = os.path.join(MOIE_LOOP_DIR, "experience_ledger.jsonl")
MOTIA_EVENTS = os.path.join(NEXUS_DIR, "motia_events.jsonl")


class MotiaIntegrationBridge:
    """
    Bridges NEXUS discoveries into Motia event stream
    """
    
    def __init__(self):
        """Initialize Motia bridge"""
        try:
            self.events = []
            
            logger.info("🔗 NEXUS → Motia Bridge initialized")
            
        except (OSError, ValueError) as e:
            logger.error(f"Motia bridge initialization failed: {e}")
            raise
    
    def load_latest_syntheses(self) -> List[Dict[str, Any]]:
        """Load most recent NEXUS syntheses"""
        try:
            if not os.path.exists(SYNTHESIS_DIR):
                return []
            
            synthesis_files = sorted([
                f for f in os.listdir(SYNTHESIS_DIR)
                if f.startswith('nexus_synthesis_') and f.endswith('.jsonl')
            ])
            
            if not synthesis_files:
                return []
            
            latest_file = synthesis_files[-1]
            filepath = os.path.join(SYNTHESIS_DIR, latest_file)
            
            syntheses = []
            with open(filepath, 'r') as f:
                for line in f:
                    try:
                        syntheses.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
            
            logger.info(f"📥 Loaded {len(syntheses)} latest syntheses")
            return syntheses
            
        except (OSError, IOError) as e:
            logger.error(f"Failed to load syntheses: {e}")
            return []
    
    def convert_to_motia_events(
        self, 
        syntheses: List[Dict[str, Any]]
    ) -> None:
        """Convert NEXUS syntheses to Motia event format"""
        try:
            for synthesis in syntheses:
                # Only high-confidence breakthroughs
                if synthesis.get('avg_vdr', 0) < 7.5:
                    continue
                
                event = {
                    'timestamp': datetime.now().isoformat(),
                    'event_type': 'NEXUS_BREAKTHROUGH',
                    'source': 'VY-NEXUS',
                    'data': {
                        'concept': synthesis['geometric_concept'],
                        'vdr_score': synthesis['avg_vdr'],
                        'domains': synthesis['spanning_domains'],
                        'frequency': synthesis['frequency'],
                        'hypothesis': synthesis.get('breakthrough_hypothesis', ''),
                        'synthesis_hash': synthesis.get('synthesis_hash', ''),
                        'alert_level': 'HIGH' if synthesis['avg_vdr'] >= 8.0 else 'MEDIUM'
                    },
                    'meta': {
                        'integration_layer': 'NEXUS_MOTIA_BRIDGE',
                        'ready_for_moie_inversion': True,
                        'constitutional_status': 'PROPOSED'
                    }
                }
                
                self.events.append(event)
            
            logger.info(
                f"🎯 Generated {len(self.events)} Motia events"
            )
            
        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"Event conversion failed: {e}")
            raise
    
    def export_motia_events(self) -> None:
        """Export events to Motia-compatible format"""
        try:
            # Export to NEXUS motia events log
            with open(MOTIA_EVENTS, 'a') as f:
                for event in self.events:
                    f.write(json.dumps(event) + '\n')
            
            logger.info(
                f"💾 Exported {len(self.events)} events to {MOTIA_EVENTS}"
            )
            
            # Try to append to experience ledger if it exists
            if os.path.exists(MOIE_LOOP_DIR):
                try:
                    ledger_path = EXPERIENCE_LEDGER
                    
                    with open(ledger_path, 'a') as f:
                        for event in self.events:
                            # Format for experience ledger
                            ledger_entry = {
                                'timestamp': event['timestamp'],
                                'type': 'nexus_breakthrough',
                                'concept': event['data']['concept'],
                                'vdr': event['data']['vdr_score'],
                                'domains': event['data']['domains'],
                                'source': 'VY-NEXUS-INTEGRATION'
                            }
                            f.write(json.dumps(ledger_entry) + '\n')
                    
                    logger.info(
                        f"📝 Appended to experience ledger: {ledger_path}"
                    )
                    
                except (OSError, IOError) as e:
                    logger.warning(f"Could not write to experience ledger: {e}")
            
        except (OSError, IOError) as e:
            logger.error(f"Motia event export failed: {e}")
            raise
    
    def generate_moie_job_suggestions(self) -> List[Dict[str, Any]]:
        """
        Generate MoIE job suggestions based on breakthroughs
        Feed discoveries back into inversion engine
        """
        try:
            suggestions = []
            
            for event in self.events:
                concept = event['data']['concept']
                domains = event['data']['domains']
                
                # Suggest inversions for each domain
                for domain in domains[:3]:  # Top 3 domains
                    suggestion = {
                        'timestamp': datetime.now().isoformat(),
                        'type': 'MOIE_JOB_SUGGESTION',
                        'source': 'NEXUS_META_ANALYSIS',
                        'domain': domain,
                        'axiom': f"{concept.title()} is the primary organizing principle",
                        'mode': 'reverse_engineering',
                        'rationale': (
                            f"NEXUS detected {concept} as fundamental invariant "
                            f"across {len(domains)} domains. Inverting this axiom "
                            f"in {domain} may reveal deeper geometric truth."
                        ),
                        'priority': 'HIGH' if event['data']['vdr_score'] >= 8.0 else 'MEDIUM'
                    }
                    
                    suggestions.append(suggestion)
            
            logger.info(
                f"💡 Generated {len(suggestions)} MoIE job suggestions"
            )
            
            return suggestions
            
        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"Job suggestion generation failed: {e}")
            return []
    
    def export_moie_suggestions(
        self, 
        suggestions: List[Dict[str, Any]]
    ) -> None:
        """Export MoIE job suggestions"""
        try:
            suggestions_path = os.path.join(
                NEXUS_DIR,
                f"moie_suggestions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )
            
            with open(suggestions_path, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'total_suggestions': len(suggestions),
                    'suggestions': suggestions
                }, f, indent=2)
            
            logger.info(
                f"📋 Exported MoIE suggestions: {suggestions_path}"
            )
            
        except (OSError, IOError) as e:
            logger.error(f"Suggestion export failed: {e}")
            raise


def main():
    """Main execution for Motia bridge"""
    try:
        print("🔗 VY-NEXUS → Motia Integration Bridge")
        print("=" * 60)
        
        bridge = MotiaIntegrationBridge()
        
        print("\n📥 Loading latest syntheses...")
        syntheses = bridge.load_latest_syntheses()
        
        if not syntheses:
            print("\n⚠️  No syntheses available")
            print("   Run nexus_core.py first!")
            return
        
        print(f"\n🎯 Converting {len(syntheses)} syntheses to Motia events...")
        bridge.convert_to_motia_events(syntheses)
        
        if bridge.events:
            print(f"\n💾 Exporting {len(bridge.events)} events...")
            bridge.export_motia_events()
            
            print(f"\n💡 Generating MoIE job suggestions...")
            suggestions = bridge.generate_moie_job_suggestions()
            
            if suggestions:
                bridge.export_moie_suggestions(suggestions)
                
                print(f"\n✨ Integration complete!")
                print(f"   - {len(bridge.events)} Motia events exported")
                print(f"   - {len(suggestions)} MoIE jobs suggested")
                print("\n🔄 Full ecosystem loop closed!")
            
        else:
            print("\n⚠️  No high-confidence events to export")
            print("   (Need VDR ≥ 7.5)")
        
    except (OSError, ValueError, TypeError) as e:
        logger.error(f"Motia bridge execution failed: {e}")
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
