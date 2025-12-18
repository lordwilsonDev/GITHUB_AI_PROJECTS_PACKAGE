#!/usr/bin/env python3
"""
VY-NEXUS → VY-PULSE Integration Bridge
Feeds breakthrough syntheses back into constitutional validation

PURPOSE: Close the loop - discoveries become new constitutional principles
AXIOM: "Breakthroughs that survive pulse validation become new laws"
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
HOME = os.path.expanduser("~")
NEXUS_OUTPUT = os.path.join(HOME, "vy-nexus", "synthesis")
PULSE_DIR = os.path.join(HOME, "nano_memory", "pulse")
CONSTITUTION_PATH = os.path.join(PULSE_DIR, "constitution.md")
PROPOSALS_PATH = os.path.join(PULSE_DIR, "constitution_proposals.jsonl")


class NexusPulseBridge:
    """
    Bridges breakthrough discoveries into constitutional proposals
    """
    
    def __init__(self):
        """Initialize bridge with safety checks"""
        try:
            self.proposals = []
            
            # Ensure pulse directory exists
            os.makedirs(PULSE_DIR, exist_ok=True)
            
            logger.info("🌉 VY-NEXUS → PULSE Bridge initialized")
            
        except (OSError, ValueError) as e:
            logger.error(f"Bridge initialization failed: {e}")
            raise
    
    def load_latest_synthesis(self) -> List[Dict[str, Any]]:
        """Load the most recent NEXUS synthesis"""
        try:
            if not os.path.exists(NEXUS_OUTPUT):
                logger.warning("No NEXUS synthesis directory found")
                return []
            
            # Find latest synthesis file
            synthesis_files = [
                f for f in os.listdir(NEXUS_OUTPUT)
                if f.startswith('nexus_synthesis_') and f.endswith('.jsonl')
            ]
            
            if not synthesis_files:
                logger.warning("No synthesis files found")
                return []
            
            latest_file = sorted(synthesis_files)[-1]
            filepath = os.path.join(NEXUS_OUTPUT, latest_file)
            
            syntheses = []
            with open(filepath, 'r') as f:
                for line in f:
                    try:
                        syntheses.append(json.loads(line.strip()))
                    except (json.JSONDecodeError, ValueError) as e:
                        logger.warning(f"Skipping malformed synthesis: {e}")
                        continue
            
            logger.info(f"📥 Loaded {len(syntheses)} syntheses from {latest_file}")
            return syntheses
            
        except (OSError, IOError) as e:
            logger.error(f"Failed to load synthesis: {e}")
            return []
    
    def convert_to_constitutional_proposals(
        self, 
        syntheses: List[Dict[str, Any]]
    ) -> None:
        """Convert breakthrough syntheses into constitutional rule proposals"""
        try:
            for synthesis in syntheses:
                # Only high-confidence patterns become proposals
                if synthesis.get('avg_vdr', 0) < 7.0:
                    continue
                
                concept = synthesis['geometric_concept']
                domains = synthesis['spanning_domains']
                
                # Generate constitutional rule proposal
                proposal = {
                    'timestamp': datetime.now().isoformat(),
                    'type': 'CONSTITUTIONAL_PROPOSAL',
                    'source': 'NEXUS_SYNTHESIS',
                    'geometric_concept': concept,
                    'spanning_domains': domains,
                    'avg_vdr': synthesis['avg_vdr'],
                    'synthesis_hash': synthesis['synthesis_hash'],
                    'proposed_rule': self._generate_constitutional_rule(
                        concept, 
                        domains
                    ),
                    'rationale': synthesis['breakthrough_hypothesis'],
                    'status': 'PENDING_VALIDATION'
                }
                
                self.proposals.append(proposal)
            
            logger.info(
                f"📝 Generated {len(self.proposals)} constitutional proposals"
            )
            
        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"Proposal conversion failed: {e}")
            raise
    
    def _generate_constitutional_rule(
        self, 
        concept: str, 
        domains: List[str]
    ) -> str:
        """Generate a constitutional rule from geometric concept"""
        try:
            rule = (
                f"All code implementing {concept}-based patterns must "
                f"maintain consistency with geometric invariants observed "
                f"across {', '.join(domains)}. Violations of {concept} "
                f"principles indicate entropy and require immediate healing."
            )
            
            return rule
            
        except (ValueError, TypeError) as e:
            logger.error(f"Rule generation failed: {e}")
            return "RULE_GENERATION_FAILED"
    
    def export_proposals(self) -> None:
        """Export proposals to pulse system for validation"""
        try:
            with open(PROPOSALS_PATH, 'a') as f:
                for proposal in self.proposals:
                    f.write(json.dumps(proposal) + '\n')
            
            logger.info(
                f"💾 Exported {len(self.proposals)} proposals to {PROPOSALS_PATH}"
            )
            
            # Create human-readable summary
            self._create_proposal_summary()
            
        except (OSError, IOError) as e:
            logger.error(f"Proposal export failed: {e}")
            raise
    
    def _create_proposal_summary(self) -> None:
        """Create markdown summary of proposals"""
        try:
            summary_path = os.path.join(
                PULSE_DIR,
                f"proposal_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            )
            
            with open(summary_path, 'w') as f:
                f.write("# 📋 CONSTITUTIONAL PROPOSALS FROM NEXUS\n\n")
                f.write(f"**Generated**: {datetime.now()}\n\n")
                f.write(f"**Total Proposals**: {len(self.proposals)}\n\n")
                f.write("---\n\n")
                
                for idx, proposal in enumerate(self.proposals, 1):
                    f.write(f"## Proposal #{idx}\n\n")
                    f.write(f"**Concept**: {proposal['geometric_concept']}\n\n")
                    f.write(f"**Domains**: {', '.join(proposal['spanning_domains'])}\n\n")
                    f.write(f"**VDR Score**: {proposal['avg_vdr']:.2f}\n\n")
                    f.write("**Proposed Rule**:\n")
                    f.write(f"> {proposal['proposed_rule']}\n\n")
                    f.write("**Rationale**:\n")
                    f.write(f"{proposal['rationale']}\n\n")
                    f.write("---\n\n")
            
            logger.info(f"📄 Created proposal summary: {summary_path}")
            
        except (OSError, IOError) as e:
            logger.error(f"Summary creation failed: {e}")
            raise


def main():
    """Main execution for NEXUS → PULSE bridge"""
    try:
        print("🌉 VY-NEXUS → PULSE Bridge")
        print("=" * 60)
        
        bridge = NexusPulseBridge()
        
        print("\n📥 Loading latest NEXUS synthesis...")
        syntheses = bridge.load_latest_synthesis()
        
        if not syntheses:
            print("\n⚠️  No syntheses available yet.")
            print("    Run nexus_core.py first to generate syntheses!")
            return
        
        print(f"\n📝 Converting {len(syntheses)} syntheses to proposals...")
        bridge.convert_to_constitutional_proposals(syntheses)
        
        if bridge.proposals:
            print(f"\n💾 Exporting {len(bridge.proposals)} proposals...")
            bridge.export_proposals()
            
            print("\n✨ Bridge complete!")
            print(f"📊 Proposals written to {PROPOSALS_PATH}")
            print("\n🔄 These proposals can now be validated by VY Pulse")
        else:
            print("\n⚠️  No high-confidence proposals generated")
            print("    (Need avg_vdr >= 7.0)")
        
    except (OSError, ValueError, TypeError) as e:
        logger.error(f"Bridge execution failed: {e}")
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
