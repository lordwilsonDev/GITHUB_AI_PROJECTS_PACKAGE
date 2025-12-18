#!/usr/bin/env python3
"""
🧬 PATTERN EVOLUTION ENGINE 🧬
Self-modifying code that adapts to pattern changes

PURPOSE: Tools should evolve as patterns evolve
AXIOM: "The code that doesn't adapt is dead code"
"""

import os
import json
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Set
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
HOME = os.path.expanduser("~")
NEXUS_DIR = os.path.join(HOME, "vy-nexus")
SYNTHESIS_DIR = os.path.join(NEXUS_DIR, "synthesis")
TOOLS_DIR = os.path.join(NEXUS_DIR, "genesis", "generated_tools")
EVOLUTION_DIR = os.path.join(NEXUS_DIR, "evolution")


class PatternEvolutionEngine:
    """
    Watches how patterns change over time and updates tools accordingly
    
    INVERSION: Instead of static tools,
    tools that EVOLVE with discovered patterns
    """
    
    def __init__(self):
        """Initialize evolution engine"""
        try:
            os.makedirs(EVOLUTION_DIR, exist_ok=True)
            
            self.pattern_history_file = os.path.join(EVOLUTION_DIR, "pattern_history.jsonl")
            self.evolution_log = os.path.join(EVOLUTION_DIR, "evolution.log")
            
            logger.info("🧬 Pattern Evolution Engine initialized")
            
        except OSError as e:
            logger.error(f"Evolution engine initialization failed: {e}")
            raise
    
    def load_pattern_history(self) -> List[Dict[str, Any]]:
        """Load historical pattern states"""
        try:
            history = []
            
            if os.path.exists(self.pattern_history_file):
                with open(self.pattern_history_file, 'r') as f:
                    for line in f:
                        try:
                            history.append(json.loads(line.strip()))
                        except json.JSONDecodeError:
                            continue
            
            return history
            
        except (OSError, IOError) as e:
            logger.error(f"Pattern history load failed: {e}")
            return []
    
    def snapshot_current_patterns(self) -> Dict[str, Any]:
        """Take a snapshot of current pattern state"""
        try:
            if not os.path.exists(SYNTHESIS_DIR):
                return {}
            
            # Get latest synthesis file
            synthesis_files = sorted([
                f for f in os.listdir(SYNTHESIS_DIR)
                if f.startswith('nexus_synthesis_') and f.endswith('.jsonl')
            ])
            
            if not synthesis_files:
                return {}
            
            latest_file = os.path.join(SYNTHESIS_DIR, synthesis_files[-1])
            
            patterns = {}
            
            with open(latest_file, 'r') as f:
                for line in f:
                    try:
                        synthesis = json.loads(line.strip())
                        concept = synthesis.get('geometric_concept', '').upper()
                        
                        if concept:
                            patterns[concept] = {
                                'avg_vdr': synthesis.get('avg_vdr', 0),
                                'frequency': synthesis.get('frequency', 0),
                                'domains': synthesis.get('spanning_domains', []),
                                'hypothesis': synthesis.get('breakthrough_hypothesis', '')[:200]
                            }
                    except json.JSONDecodeError:
                        continue
            
            snapshot = {
                'timestamp': datetime.now().isoformat(),
                'patterns': patterns,
                'pattern_count': len(patterns),
                'snapshot_hash': hashlib.md5(json.dumps(patterns, sort_keys=True).encode()).hexdigest()
            }
            
            return snapshot
            
        except (OSError, IOError) as e:
            logger.error(f"Pattern snapshot failed: {e}")
            return {}
    
    def detect_pattern_changes(
        self,
        current: Dict[str, Any],
        previous: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Detect how patterns have evolved"""
        try:
            changes = []
            
            current_patterns = current.get('patterns', {})
            previous_patterns = previous.get('patterns', {})
            
            # New patterns emerged
            for pattern in current_patterns:
                if pattern not in previous_patterns:
                    changes.append({
                        'type': 'EMERGENCE',
                        'pattern': pattern,
                        'vdr': current_patterns[pattern]['avg_vdr'],
                        'description': f"New pattern '{pattern}' emerged with VDR {current_patterns[pattern]['avg_vdr']:.2f}"
                    })
            
            # Patterns strengthened
            for pattern in current_patterns:
                if pattern in previous_patterns:
                    current_vdr = current_patterns[pattern]['avg_vdr']
                    previous_vdr = previous_patterns[pattern]['avg_vdr']
                    
                    if current_vdr > previous_vdr + 0.5:  # Significant increase
                        changes.append({
                            'type': 'STRENGTHENING',
                            'pattern': pattern,
                            'previous_vdr': previous_vdr,
                            'current_vdr': current_vdr,
                            'delta': current_vdr - previous_vdr,
                            'description': f"Pattern '{pattern}' strengthened from {previous_vdr:.2f} to {current_vdr:.2f}"
                        })
            
            # Patterns weakened
            for pattern in current_patterns:
                if pattern in previous_patterns:
                    current_vdr = current_patterns[pattern]['avg_vdr']
                    previous_vdr = previous_patterns[pattern]['avg_vdr']
                    
                    if current_vdr < previous_vdr - 0.5:  # Significant decrease
                        changes.append({
                            'type': 'WEAKENING',
                            'pattern': pattern,
                            'previous_vdr': previous_vdr,
                            'current_vdr': current_vdr,
                            'delta': previous_vdr - current_vdr,
                            'description': f"Pattern '{pattern}' weakened from {previous_vdr:.2f} to {current_vdr:.2f}"
                        })
            
            # Patterns disappeared
            for pattern in previous_patterns:
                if pattern not in current_patterns:
                    changes.append({
                        'type': 'DISAPPEARANCE',
                        'pattern': pattern,
                        'previous_vdr': previous_patterns[pattern]['avg_vdr'],
                        'description': f"Pattern '{pattern}' disappeared"
                    })
            
            return changes
            
        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"Pattern change detection failed: {e}")
            return []
    
    def generate_evolution_recommendations(self, changes: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on pattern evolution"""
        try:
            recommendations = []
            
            for change in changes:
                if change['type'] == 'EMERGENCE':
                    recommendations.append(
                        f"🌱 NEW: Create tool for '{change['pattern']}' (VDR {change['vdr']:.2f})"
                    )
                
                elif change['type'] == 'STRENGTHENING':
                    recommendations.append(
                        f"📈 STRENGTHEN: Enhance '{change['pattern']}' tool (VDR +{change['delta']:.2f})"
                    )
                
                elif change['type'] == 'WEAKENING':
                    recommendations.append(
                        f"📉 REVIEW: Consider archiving '{change['pattern']}' tool (VDR -{change['delta']:.2f})"
                    )
                
                elif change['type'] == 'DISAPPEARANCE':
                    recommendations.append(
                        f"💀 DEPRECATE: Archive '{change['pattern']}' tool"
                    )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendation generation failed: {e}")
            return []
    
    def save_snapshot(self, snapshot: Dict[str, Any]) -> None:
        """Save current pattern snapshot to history"""
        try:
            with open(self.pattern_history_file, 'a') as f:
                f.write(json.dumps(snapshot) + '\n')
            
            logger.info(f"📸 Snapshot saved: {snapshot['pattern_count']} patterns")
            
        except (OSError, IOError) as e:
            logger.error(f"Snapshot save failed: {e}")
    
    def log_evolution(self, changes: List[Dict[str, Any]], recommendations: List[str]) -> None:
        """Log evolution events"""
        try:
            with open(self.evolution_log, 'a') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"Evolution Check: {datetime.now().isoformat()}\n")
                f.write(f"{'='*80}\n\n")
                
                if changes:
                    f.write("CHANGES DETECTED:\n")
                    for change in changes:
                        f.write(f"  • {change['description']}\n")
                    f.write("\n")
                else:
                    f.write("No significant changes detected.\n\n")
                
                if recommendations:
                    f.write("RECOMMENDATIONS:\n")
                    for rec in recommendations:
                        f.write(f"  {rec}\n")
                    f.write("\n")
            
            logger.info(f"📝 Evolution logged: {len(changes)} changes")
            
        except (OSError, IOError) as e:
            logger.error(f"Evolution logging failed: {e}")
    
    def run_evolution_check(self) -> Dict[str, Any]:
        """Execute evolution check"""
        try:
            logger.info("🧬 Running pattern evolution check...")
            
            # Take current snapshot
            current_snapshot = self.snapshot_current_patterns()
            
            if not current_snapshot:
                logger.warning("No current patterns to snapshot")
                return {'changes': 0}
            
            # Load history
            history = self.load_pattern_history()
            
            # Save current snapshot
            self.save_snapshot(current_snapshot)
            
            if not history:
                logger.info("First snapshot - no comparison possible")
                return {'changes': 0, 'first_run': True}
            
            # Compare with previous
            previous_snapshot = history[-1]
            
            # Detect changes
            changes = self.detect_pattern_changes(current_snapshot, previous_snapshot)
            
            # Generate recommendations
            recommendations = self.generate_evolution_recommendations(changes)
            
            # Log everything
            self.log_evolution(changes, recommendations)
            
            return {
                'changes': len(changes),
                'change_list': changes,
                'recommendations': recommendations,
                'current_pattern_count': current_snapshot['pattern_count'],
                'previous_pattern_count': previous_snapshot.get('pattern_count', 0)
            }
            
        except Exception as e:
            logger.error(f"Evolution check failed: {e}")
            return {'changes': 0, 'error': str(e)}


def main():
    """Main execution"""
    try:
        print("=" * 80)
        print("🧬 PATTERN EVOLUTION ENGINE 🧬")
        print("=" * 80)
        print("Self-modifying intelligence")
        print("=" * 80)
        print()
        
        engine = PatternEvolutionEngine()
        
        print("🔍 Checking pattern evolution...")
        result = engine.run_evolution_check()
        
        print()
        print("=" * 80)
        print("📊 EVOLUTION RESULTS")
        print("=" * 80)
        
        if result.get('first_run'):
            print("✨ First run - baseline established")
            print(f"📸 Captured {result.get('current_pattern_count', 0)} patterns")
        else:
            changes = result.get('changes', 0)
            
            if changes > 0:
                print(f"🔥 Detected {changes} pattern evolution events!")
                print()
                
                print("CHANGES:")
                for change in result.get('change_list', []):
                    print(f"  • {change['description']}")
                
                print()
                print("RECOMMENDATIONS:")
                for rec in result.get('recommendations', []):
                    print(f"  {rec}")
            else:
                print("✨ Patterns are stable - no significant changes")
            
            print()
            print(f"Current patterns: {result.get('current_pattern_count', 0)}")
            print(f"Previous patterns: {result.get('previous_pattern_count', 0)}")
        
        print()
        print("=" * 80)
        print("💓 Tools Evolving With Patterns")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
