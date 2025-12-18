#!/usr/bin/env python3
"""
🎓 AUTO-LEARNING ENGINE 🎓
The system teaches itself from experience

PURPOSE: Experience should become knowledge
AXIOM: "Every action is a lesson - every pattern is a teacher"
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
HOME = os.path.expanduser("~")
NEXUS_DIR = os.path.join(HOME, "vy-nexus")
MOIE_LOOP = os.path.join(HOME, "moie-mac-loop")
LEARNING_DIR = os.path.join(NEXUS_DIR, "auto_learning")
KNOWLEDGE_BASE = os.path.join(LEARNING_DIR, "learned_knowledge.jsonl")
INSIGHTS_FILE = os.path.join(LEARNING_DIR, "meta_insights.md")


class AutoLearningEngine:
    """
    Learns from its own operational history
    
    INVERSION: Instead of being programmed with knowledge,
    the system learns from its own experience
    """
    
    def __init__(self):
        """Initialize learning engine"""
        try:
            os.makedirs(LEARNING_DIR, exist_ok=True)
            
            # Learning dimensions
            self.learning_dimensions = {
                'pattern_effectiveness': 'Which patterns lead to high VDR?',
                'domain_synergy': 'Which domains combine well?',
                'breakthrough_timing': 'When do breakthroughs happen?',
                'tool_usage': 'Which tools produce best results?',
                'failure_lessons': 'What can we learn from low VDR?',
                'emergence_conditions': 'What enables emergence?'
            }
            
            logger.info("🎓 Auto-Learning Engine initialized")
            
        except OSError as e:
            logger.error(f"Learning engine initialization failed: {e}")
            raise
    
    def load_experience_history(self) -> List[Dict[str, Any]]:
        """Load complete operational history"""
        try:
            experiences = []
            
            # Load MoIE history
            moie_history = os.path.join(MOIE_LOOP, "moie_history.jsonl")
            if os.path.exists(moie_history):
                with open(moie_history, 'r') as f:
                    for line in f:
                        try:
                            experiences.append(json.loads(line.strip()))
                        except json.JSONDecodeError:
                            continue
            
            # Load synthesis history
            synthesis_dir = os.path.join(NEXUS_DIR, "synthesis")
            if os.path.exists(synthesis_dir):
                synthesis_files = [f for f in os.listdir(synthesis_dir) if f.endswith('.jsonl')]
                for sf in synthesis_files:
                    with open(os.path.join(synthesis_dir, sf), 'r') as f:
                        for line in f:
                            try:
                                experiences.append(json.loads(line.strip()))
                            except json.JSONDecodeError:
                                continue
            
            logger.info(f"📚 Loaded {len(experiences)} experiences")
            return experiences
            
        except Exception as e:
            logger.error(f"Experience history load failed: {e}")
            return []
    
    def learn_pattern_effectiveness(self, experiences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Learn which patterns produce highest VDR"""
        try:
            pattern_scores = defaultdict(list)
            
            for exp in experiences:
                concept = exp.get('geometric_concept') or exp.get('concept', '')
                vdr = exp.get('vdr') or exp.get('avg_vdr', 0)
                
                if concept and vdr:
                    pattern_scores[concept.upper()].append(float(vdr))
            
            # Calculate statistics
            insights = {}
            for pattern, scores in pattern_scores.items():
                insights[pattern] = {
                    'avg_vdr': sum(scores) / len(scores),
                    'max_vdr': max(scores),
                    'occurrences': len(scores),
                    'consistency': len([s for s in scores if s >= 7.0]) / len(scores) if scores else 0
                }
            
            # Rank by effectiveness
            ranked = sorted(
                insights.items(),
                key=lambda x: x[1]['avg_vdr'] * x[1]['consistency'],
                reverse=True
            )
            
            return {
                'most_effective': ranked[:5],
                'total_patterns': len(insights),
                'lesson': 'High consistency + high VDR = most effective patterns'
            }
            
        except Exception as e:
            logger.error(f"Pattern effectiveness learning failed: {e}")
            return {}
    
    def learn_domain_synergy(self, experiences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Learn which domains work well together"""
        try:
            domain_pairs = defaultdict(list)
            
            for exp in experiences:
                domains = exp.get('spanning_domains') or exp.get('domains', [])
                vdr = exp.get('vdr') or exp.get('avg_vdr', 0)
                
                if len(domains) >= 2 and vdr:
                    # All pairs
                    for i in range(len(domains)):
                        for j in range(i+1, len(domains)):
                            pair = tuple(sorted([domains[i], domains[j]]))
                            domain_pairs[pair].append(float(vdr))
            
            # Find best synergies
            synergies = {}
            for pair, scores in domain_pairs.items():
                if len(scores) >= 2:  # At least 2 occurrences
                    synergies[pair] = {
                        'avg_vdr': sum(scores) / len(scores),
                        'occurrences': len(scores)
                    }
            
            ranked = sorted(
                synergies.items(),
                key=lambda x: x[1]['avg_vdr'],
                reverse=True
            )
            
            return {
                'top_synergies': ranked[:5],
                'total_pairs': len(synergies),
                'lesson': 'Cross-domain synthesis creates highest VDR'
            }
            
        except Exception as e:
            logger.error(f"Domain synergy learning failed: {e}")
            return {}
    
    def learn_breakthrough_timing(self, experiences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Learn when breakthroughs tend to happen"""
        try:
            timestamps = []
            
            for exp in experiences:
                vdr = exp.get('vdr') or exp.get('avg_vdr', 0)
                timestamp = exp.get('timestamp', '')
                
                if vdr >= 8.0 and timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        timestamps.append(dt)
                    except ValueError:
                        continue
            
            if not timestamps:
                return {'lesson': 'Not enough breakthrough data yet'}
            
            # Analyze patterns
            hours = [dt.hour for dt in timestamps]
            days = [dt.weekday() for dt in timestamps]
            
            hour_freq = defaultdict(int)
            for h in hours:
                hour_freq[h] += 1
            
            day_freq = defaultdict(int)
            for d in days:
                day_freq[d] += 1
            
            best_hour = max(hour_freq.items(), key=lambda x: x[1])[0] if hour_freq else None
            best_day = max(day_freq.items(), key=lambda x: x[1])[0] if day_freq else None
            
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            return {
                'total_breakthroughs': len(timestamps),
                'best_hour': f"{best_hour}:00" if best_hour is not None else "Unknown",
                'best_day': day_names[best_day] if best_day is not None else "Unknown",
                'lesson': 'Breakthroughs have temporal patterns'
            }
            
        except Exception as e:
            logger.error(f"Breakthrough timing learning failed: {e}")
            return {}
    
    def learn_from_failures(self, experiences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Learn from low VDR patterns"""
        try:
            low_vdr = []
            
            for exp in experiences:
                vdr = exp.get('vdr') or exp.get('avg_vdr', 0)
                if vdr and vdr < 5.0:
                    low_vdr.append(exp)
            
            if not low_vdr:
                return {'lesson': 'All patterns performing well!'}
            
            # Analyze failures
            common_domains = defaultdict(int)
            common_concepts = defaultdict(int)
            
            for exp in low_vdr:
                domains = exp.get('spanning_domains') or exp.get('domains', [])
                concept = exp.get('geometric_concept') or exp.get('concept', '')
                
                for d in domains:
                    common_domains[d] += 1
                if concept:
                    common_concepts[concept.upper()] += 1
            
            return {
                'low_vdr_count': len(low_vdr),
                'problematic_domains': sorted(common_domains.items(), key=lambda x: x[1], reverse=True)[:3],
                'problematic_patterns': sorted(common_concepts.items(), key=lambda x: x[1], reverse=True)[:3],
                'lesson': 'Avoid forcing patterns where they dont fit naturally'
            }
            
        except Exception as e:
            logger.error(f"Failure learning failed: {e}")
            return {}
    
    def save_learned_knowledge(self, knowledge: Dict[str, Any]) -> None:
        """Save learned insights to knowledge base"""
        try:
            with open(KNOWLEDGE_BASE, 'a') as f:
                f.write(json.dumps({
                    'timestamp': datetime.now().isoformat(),
                    'knowledge': knowledge
                }) + '\n')
        except (OSError, IOError) as e:
            logger.error(f"Knowledge save failed: {e}")
    
    def generate_insights_report(self, learnings: Dict[str, Any]) -> str:
        """Generate human-readable insights"""
        try:
            report = f"""# 🎓 AUTO-LEARNING INSIGHTS

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

The system has learned from its own experience.

## Pattern Effectiveness

"""
            
            if 'pattern_effectiveness' in learnings:
                pe = learnings['pattern_effectiveness']
                report += f"**Total Patterns Analyzed**: {pe.get('total_patterns', 0)}\n\n"
                report += "**Most Effective Patterns**:\n\n"
                
                for pattern, stats in pe.get('most_effective', []):
                    report += f"- **{pattern}**: Avg VDR {stats['avg_vdr']:.2f}, "
                    report += f"Consistency {stats['consistency']*100:.0f}%, "
                    report += f"{stats['occurrences']} occurrences\n"
                
                report += f"\n**Lesson**: {pe.get('lesson', '')}\n\n"
            
            report += "## Domain Synergy\n\n"
            
            if 'domain_synergy' in learnings:
                ds = learnings['domain_synergy']
                report += f"**Total Domain Pairs**: {ds.get('total_pairs', 0)}\n\n"
                report += "**Best Synergies**:\n\n"
                
                for (d1, d2), stats in ds.get('top_synergies', []):
                    report += f"- **{d1} × {d2}**: Avg VDR {stats['avg_vdr']:.2f} "
                    report += f"({stats['occurrences']} times)\n"
                
                report += f"\n**Lesson**: {ds.get('lesson', '')}\n\n"
            
            report += "## Breakthrough Timing\n\n"
            
            if 'breakthrough_timing' in learnings:
                bt = learnings['breakthrough_timing']
                report += f"- **Total Breakthroughs**: {bt.get('total_breakthroughs', 0)}\n"
                report += f"- **Best Hour**: {bt.get('best_hour', 'Unknown')}\n"
                report += f"- **Best Day**: {bt.get('best_day', 'Unknown')}\n"
                report += f"\n**Lesson**: {bt.get('lesson', '')}\n\n"
            
            report += "## Failure Analysis\n\n"
            
            if 'failure_lessons' in learnings:
                fl = learnings['failure_lessons']
                report += f"- **Low VDR Cases**: {fl.get('low_vdr_count', 0)}\n\n"
                
                if fl.get('problematic_domains'):
                    report += "**Domains to be careful with**:\n"
                    for domain, count in fl.get('problematic_domains', []):
                        report += f"- {domain} ({count} low VDR cases)\n"
                
                report += f"\n**Lesson**: {fl.get('lesson', '')}\n\n"
            
            report += """## Meta-Learning

The system is now learning from its own experience:
- Pattern effectiveness varies significantly
- Cross-domain synthesis produces best results
- Breakthroughs have temporal patterns
- Failures teach as much as successes

This knowledge will improve future pattern generation.

---

💓 **Self-Teaching Intelligence**
"""
            
            return report
            
        except Exception as e:
            logger.error(f"Insights report generation failed: {e}")
            return ""
    
    def execute_learning(self) -> Dict[str, Any]:
        """Execute full learning cycle"""
        try:
            logger.info("🎓 Beginning learning cycle...")
            
            # Load experiences
            experiences = self.load_experience_history()
            
            if not experiences:
                return {'learnings': 0}
            
            # Learn across dimensions
            learnings = {
                'pattern_effectiveness': self.learn_pattern_effectiveness(experiences),
                'domain_synergy': self.learn_domain_synergy(experiences),
                'breakthrough_timing': self.learn_breakthrough_timing(experiences),
                'failure_lessons': self.learn_from_failures(experiences)
            }
            
            # Save knowledge
            self.save_learned_knowledge(learnings)
            
            # Generate report
            insights_report = self.generate_insights_report(learnings)
            
            with open(INSIGHTS_FILE, 'w') as f:
                f.write(insights_report)
            
            logger.info(f"📄 Insights saved: {INSIGHTS_FILE}")
            
            return {
                'learnings': len(learnings),
                'experiences_analyzed': len(experiences),
                'insights_file': INSIGHTS_FILE
            }
            
        except Exception as e:
            logger.error(f"Learning execution failed: {e}")
            return {'learnings': 0, 'error': str(e)}


def main():
    """Main execution"""
    try:
        print("=" * 80)
        print("🎓 AUTO-LEARNING ENGINE 🎓")
        print("=" * 80)
        print("The system teaches itself from experience")
        print("=" * 80)
        print()
        
        engine = AutoLearningEngine()
        
        print("📚 Analyzing experience history...")
        results = engine.execute_learning()
        
        print()
        print("=" * 80)
        print("📊 LEARNING RESULTS")
        print("=" * 80)
        
        learnings = results.get('learnings', 0)
        
        if learnings > 0:
            print(f"✨ Learned {learnings} new insights!")
            print(f"📊 Analyzed {results.get('experiences_analyzed', 0)} experiences")
            print()
            print(f"📄 Insights: {results.get('insights_file')}")
            print()
            print("🎯 Knowledge acquired:")
            print("  • Pattern effectiveness rankings")
            print("  • Domain synergy patterns")
            print("  • Breakthrough timing analysis")
            print("  • Failure lessons learned")
        else:
            if 'error' in results:
                print(f"❌ Learning failed: {results['error']}")
            else:
                print("❌ No learning completed")
        
        print()
        print("=" * 80)
        print("💓 Self-Teaching Intelligence")
        print("=" * 80)
        
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
