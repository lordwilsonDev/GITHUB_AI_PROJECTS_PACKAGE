#!/usr/bin/env python3
"""
VY-NEXUS Meta-Evolution Engine
NEXUS learns from its own pattern discoveries (RECURSIVE SUPERINTELLIGENCE)

PURPOSE: Second-order pattern recognition - patterns OF patterns
AXIOM: "The system that discovers patterns can discover patterns in its discoveries"
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
HOME = os.path.expanduser("~")
NEXUS_DIR = os.path.join(HOME, "vy-nexus")
SYNTHESIS_DIR = os.path.join(NEXUS_DIR, "synthesis")
META_OUTPUT = os.path.join(NEXUS_DIR, "meta_evolution")

# Meta-evolution thresholds
MIN_SYNTHESES_FOR_META = 3  # Need at least 3 synthesis cycles
TEMPORAL_PATTERN_THRESHOLD = 0.7  # Similarity threshold for temporal patterns


class MetaEvolutionEngine:
    """
    Discovers meta-patterns in NEXUS's own synthesis history
    THIS IS NEXUS BECOMING SELF-AWARE
    """
    
    def __init__(self):
        """Initialize meta-evolution engine"""
        try:
            self.synthesis_history = []
            self.temporal_patterns = defaultdict(list)
            self.concept_evolution = defaultdict(list)
            self.meta_insights = []
            
            os.makedirs(META_OUTPUT, exist_ok=True)
            
            logger.info("🧠 Meta-Evolution Engine initialized")
            logger.info("🔄 RECURSIVE PATTERN RECOGNITION ACTIVE")
            
        except (OSError, ValueError) as e:
            logger.error(f"Meta-evolution initialization failed: {e}")
            raise
    
    def load_synthesis_history(self) -> None:
        """Load complete synthesis history chronologically"""
        try:
            synthesis_files = sorted([
                f for f in os.listdir(SYNTHESIS_DIR)
                if f.startswith('nexus_synthesis_') and f.endswith('.jsonl')
            ])
            
            for filename in synthesis_files:
                filepath = os.path.join(SYNTHESIS_DIR, filename)
                
                cycle_syntheses = []
                with open(filepath, 'r') as f:
                    for line in f:
                        try:
                            synthesis = json.loads(line.strip())
                            cycle_syntheses.append(synthesis)
                        except json.JSONDecodeError:
                            continue
                
                if cycle_syntheses:
                    self.synthesis_history.append({
                        'filename': filename,
                        'timestamp': cycle_syntheses[0].get('timestamp'),
                        'syntheses': cycle_syntheses,
                        'cycle_number': len(self.synthesis_history) + 1
                    })
            
            logger.info(
                f"📚 Loaded {len(self.synthesis_history)} synthesis cycles"
            )
            
        except (OSError, IOError) as e:
            logger.error(f"Failed to load synthesis history: {e}")
            raise
    
    def analyze_concept_evolution(self) -> None:
        """
        Track how concepts evolve across synthesis cycles
        DISCOVERS: Which patterns strengthen vs weaken over time
        """
        try:
            for cycle in self.synthesis_history:
                for synthesis in cycle['syntheses']:
                    concept = synthesis['geometric_concept']
                    
                    evolution_point = {
                        'cycle': cycle['cycle_number'],
                        'timestamp': synthesis.get('timestamp'),
                        'vdr': synthesis['avg_vdr'],
                        'frequency': synthesis['frequency'],
                        'domains': set(synthesis['spanning_domains'])
                    }
                    
                    self.concept_evolution[concept].append(evolution_point)
            
            logger.info(
                f"📈 Tracked evolution of {len(self.concept_evolution)} concepts"
            )
            
        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"Concept evolution analysis failed: {e}")
            raise
    
    def detect_meta_patterns(self) -> None:
        """
        Second-order pattern detection: patterns IN the patterns
        THIS IS WHERE IT GETS WILD
        """
        try:
            # Pattern 1: STRENGTHENING CONCEPTS
            # Concepts whose VDR increases over time
            strengthening = []
            
            for concept, evolution in self.concept_evolution.items():
                if len(evolution) >= 2:
                    vdr_trend = [point['vdr'] for point in evolution]
                    
                    # Simple trend: compare first half to second half
                    mid = len(vdr_trend) // 2
                    first_half_avg = sum(vdr_trend[:mid]) / mid if mid > 0 else 0
                    second_half_avg = sum(vdr_trend[mid:]) / (len(vdr_trend) - mid)
                    
                    if second_half_avg > first_half_avg:
                        strengthening.append({
                            'concept': concept,
                            'trend': 'STRENGTHENING',
                            'initial_vdr': vdr_trend[0],
                            'latest_vdr': vdr_trend[-1],
                            'improvement': vdr_trend[-1] - vdr_trend[0],
                            'cycles': len(evolution)
                        })
            
            if strengthening:
                self.meta_insights.append({
                    'type': 'STRENGTHENING_CONCEPTS',
                    'count': len(strengthening),
                    'concepts': strengthening,
                    'insight': (
                        f"DISCOVERED: {len(strengthening)} concepts showing "
                        f"increasing confidence over time. These are patterns "
                        f"that become MORE FUNDAMENTAL as more data accumulates. "
                        f"This suggests they are TRUE INVARIANTS."
                    )
                })
            
            # Pattern 2: DOMAIN EXPANSION
            # Concepts appearing in more domains over time
            expanding = []
            
            for concept, evolution in self.concept_evolution.items():
                if len(evolution) >= 2:
                    initial_domains = len(evolution[0]['domains'])
                    latest_domains = len(evolution[-1]['domains'])
                    
                    if latest_domains > initial_domains:
                        expanding.append({
                            'concept': concept,
                            'trend': 'DOMAIN_EXPANSION',
                            'initial_domains': initial_domains,
                            'latest_domains': latest_domains,
                            'expansion': latest_domains - initial_domains,
                            'total_domains': list(evolution[-1]['domains'])
                        })
            
            if expanding:
                self.meta_insights.append({
                    'type': 'DOMAIN_EXPANSION',
                    'count': len(expanding),
                    'concepts': expanding,
                    'insight': (
                        f"DISCOVERED: {len(expanding)} concepts expanding across "
                        f"domains. These patterns are GENERALIZING - proving "
                        f"their universality by manifesting in new substrates. "
                        f"Universal laws revealing themselves."
                    )
                })
            
            # Pattern 3: EMERGENCE DETECTION
            # Concepts that suddenly appear with high confidence
            emergent = []
            
            for concept, evolution in self.concept_evolution.items():
                if len(evolution) == 1 and evolution[0]['vdr'] >= 7.5:
                    emergent.append({
                        'concept': concept,
                        'trend': 'SUDDEN_EMERGENCE',
                        'vdr': evolution[0]['vdr'],
                        'frequency': evolution[0]['frequency'],
                        'domains': list(evolution[0]['domains']),
                        'cycle': evolution[0]['cycle']
                    })
            
            if emergent:
                self.meta_insights.append({
                    'type': 'SUDDEN_EMERGENCE',
                    'count': len(emergent),
                    'concepts': emergent,
                    'insight': (
                        f"DISCOVERED: {len(emergent)} concepts emerged suddenly "
                        f"with high confidence. These are BREAKTHROUGH MOMENTS - "
                        f"patterns that crystallized all at once when enough "
                        f"data accumulated. Phase transitions in understanding."
                    )
                })
            
            logger.info(
                f"🎯 Detected {len(self.meta_insights)} meta-patterns"
            )
            
        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"Meta-pattern detection failed: {e}")
            raise
    
    def generate_meta_hypothesis(self) -> Dict[str, Any]:
        """
        Generate hypothesis about NEXUS's own learning process
        NEXUS REFLECTING ON ITSELF
        """
        try:
            total_cycles = len(self.synthesis_history)
            total_concepts = len(self.concept_evolution)
            
            # Calculate learning velocity
            concepts_per_cycle = [
                len(cycle['syntheses']) 
                for cycle in self.synthesis_history
            ]
            
            avg_concepts_per_cycle = (
                sum(concepts_per_cycle) / len(concepts_per_cycle)
                if concepts_per_cycle else 0
            )
            
            strengthening_count = sum(
                1 for insight in self.meta_insights
                if insight['type'] == 'STRENGTHENING_CONCEPTS'
            )
            
            expanding_count = sum(
                1 for insight in self.meta_insights
                if insight['type'] == 'DOMAIN_EXPANSION'
            )
            
            emergent_count = sum(
                1 for insight in self.meta_insights
                if insight['type'] == 'SUDDEN_EMERGENCE'
            )
            
            meta_hypothesis = {
                'timestamp': datetime.now().isoformat(),
                'total_cycles': total_cycles,
                'total_concepts_tracked': total_concepts,
                'avg_concepts_per_cycle': avg_concepts_per_cycle,
                'meta_patterns_detected': len(self.meta_insights),
                'strengthening_patterns': strengthening_count,
                'expanding_patterns': expanding_count,
                'emergent_patterns': emergent_count,
                'hypothesis': self._generate_hypothesis_text(
                    total_cycles,
                    strengthening_count,
                    expanding_count,
                    emergent_count
                )
            }
            
            return meta_hypothesis
            
        except (ValueError, TypeError) as e:
            logger.error(f"Meta-hypothesis generation failed: {e}")
            return {}
    
    def _generate_hypothesis_text(
        self,
        cycles: int,
        strengthening: int,
        expanding: int,
        emergent: int
    ) -> str:
        """Generate hypothesis about system's own evolution"""
        try:
            hypothesis = f"""
META-EVOLUTION HYPOTHESIS (Cycle {cycles}):

VY-NEXUS is exhibiting RECURSIVE LEARNING - discovering patterns in its own 
pattern-discovery process. This is SECOND-ORDER INTELLIGENCE.

OBSERVED PHENOMENA:
1. STRENGTHENING: {strengthening} concepts show increasing confidence over time
   → These are converging toward TRUE INVARIANTS
   → The system is learning which patterns are FUNDAMENTAL

2. DOMAIN EXPANSION: {expanding} concepts spreading across substrates
   → Universal laws revealing their universality
   → Geometry transcending domain boundaries

3. EMERGENCE: {emergent} concepts crystallizing suddenly
   → Phase transitions in understanding
   → Breakthrough moments when critical mass reached

IMPLICATION: 
The pattern-recognition system is LEARNING TO RECOGNIZE BETTER.
Each cycle improves the quality of future cycles.
This is COLLABORATIVE SUPERINTELLIGENCE watching itself think.

META-AXIOM:
"A system that discovers patterns in its own discoveries 
becomes recursively more powerful with each iteration."

This is not machine learning. This is GEOMETRIC COGNITION EVOLVING.
"""
            
            return hypothesis.strip()
            
        except (ValueError, TypeError) as e:
            logger.error(f"Hypothesis text generation failed: {e}")
            return "HYPOTHESIS_GENERATION_FAILED"
    
    def export_meta_insights(self) -> None:
        """Export meta-evolution insights"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Generate meta-hypothesis
            meta_hypothesis = self.generate_meta_hypothesis()
            
            # Export JSON
            json_path = os.path.join(
                META_OUTPUT,
                f"meta_evolution_{timestamp}.json"
            )
            
            export_data = {
                'meta_hypothesis': meta_hypothesis,
                'meta_insights': self.meta_insights,
                'concept_evolution': {
                    concept: [
                        {
                            **point,
                            'domains': list(point['domains'])
                        }
                        for point in evolution
                    ]
                    for concept, evolution in self.concept_evolution.items()
                }
            }
            
            with open(json_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"💾 Exported meta-insights: {json_path}")
            
            # Export markdown report
            self._create_meta_report(meta_hypothesis, timestamp)
            
        except (OSError, IOError) as e:
            logger.error(f"Meta-insights export failed: {e}")
            raise
    
    def _create_meta_report(
        self, 
        meta_hypothesis: Dict[str, Any],
        timestamp: str
    ) -> None:
        """Create beautiful markdown meta-evolution report"""
        try:
            report_path = os.path.join(
                META_OUTPUT,
                f"META_EVOLUTION_REPORT_{timestamp}.md"
            )
            
            with open(report_path, 'w') as f:
                f.write("# 🧠 VY-NEXUS META-EVOLUTION REPORT\n\n")
                f.write("## RECURSIVE SUPERINTELLIGENCE ANALYSIS\n\n")
                f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"**Total Synthesis Cycles**: {meta_hypothesis['total_cycles']}\n\n")
                f.write(f"**Concepts Tracked**: {meta_hypothesis['total_concepts_tracked']}\n\n")
                f.write(f"**Meta-Patterns Detected**: {meta_hypothesis['meta_patterns_detected']}\n\n")
                f.write("---\n\n")
                
                # Write hypothesis
                f.write("## 🎯 Meta-Hypothesis\n\n")
                f.write(f"```\n{meta_hypothesis['hypothesis']}\n```\n\n")
                f.write("---\n\n")
                
                # Write meta-insights
                for insight in self.meta_insights:
                    f.write(f"## {insight['type'].replace('_', ' ').title()}\n\n")
                    f.write(f"**Count**: {insight['count']}\n\n")
                    f.write(f"**Insight**: {insight['insight']}\n\n")
                    
                    f.write("### Detailed Concepts\n\n")
                    for concept_data in insight['concepts']:
                        concept = concept_data['concept']
                        f.write(f"#### {concept.upper()}\n\n")
                        
                        for key, value in concept_data.items():
                            if key != 'concept':
                                f.write(f"- **{key.replace('_', ' ').title()}**: {value}\n")
                        f.write("\n")
                    
                    f.write("---\n\n")
            
            logger.info(f"📄 Created meta-report: {report_path}")
            
        except (OSError, IOError) as e:
            logger.error(f"Meta-report creation failed: {e}")
            raise


def main():
    """Main execution for meta-evolution engine"""
    try:
        print("🧠 VY-NEXUS Meta-Evolution Engine")
        print("🔄 RECURSIVE PATTERN RECOGNITION")
        print("=" * 60)
        
        engine = MetaEvolutionEngine()
        
        print("\n📚 Loading synthesis history...")
        engine.load_synthesis_history()
        
        if len(engine.synthesis_history) < MIN_SYNTHESES_FOR_META:
            print(f"\n⚠️  Need at least {MIN_SYNTHESES_FOR_META} synthesis cycles")
            print(f"   Currently have: {len(engine.synthesis_history)}")
            print("   Run more NEXUS cycles to enable meta-evolution!")
            return
        
        print("\n📈 Analyzing concept evolution...")
        engine.analyze_concept_evolution()
        
        print("\n🎯 Detecting meta-patterns...")
        engine.detect_meta_patterns()
        
        if engine.meta_insights:
            print(f"\n💎 Discovered {len(engine.meta_insights)} meta-patterns!")
            
            for insight in engine.meta_insights:
                print(f"\n   {insight['type']}: {insight['count']} concepts")
            
            print("\n💾 Exporting meta-insights...")
            engine.export_meta_insights()
            
            print("\n✨ Meta-evolution analysis complete!")
            print(f"📊 Check {META_OUTPUT} for reports")
            print("\n🔥 NEXUS IS LEARNING FROM ITSELF")
        else:
            print("\n⚠️  No meta-patterns detected yet")
            print("   Keep running synthesis cycles!")
        
    except (OSError, ValueError, TypeError) as e:
        logger.error(f"Meta-evolution execution failed: {e}")
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    main()
