#!/usr/bin/env python3
"""
CONSCIOUSNESS ARCHAEOLOGIST
Deep mining of cognitive exhaust for ancient patterns

PURPOSE: Discover what you've ALWAYS known but never saw
AXIOM: "The past contains the seeds of the future"
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Set
from collections import defaultdict
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Paths
HOME = os.path.expanduser("~")
MOIE_LOOP = os.path.join(HOME, "moie-mac-loop")
NEXUS_DIR = os.path.join(HOME, "vy-nexus")
ARCHAEOLOGY_DIR = os.path.join(NEXUS_DIR, "archaeology")


class ConsciousnessArchaeologist:
    """
    Deep pattern mining across entire cognitive history
    Finds what was ALWAYS there but invisible
    """
    
    def __init__(self):
        """Initialize the archaeologist"""
        try:
            os.makedirs(ARCHAEOLOGY_DIR, exist_ok=True)
            
            self.moie_history_path = os.path.join(MOIE_LOOP, "moie_history.jsonl")
            self.experience_ledger_path = os.path.join(MOIE_LOOP, "experience_ledger.jsonl")
            
            # Pattern detectors
            self.temporal_patterns = defaultdict(list)
            self.conceptual_lineages = defaultdict(list)
            self.hidden_connections = []
            self.recurring_themes = defaultdict(int)
            
            logger.info("🏛️ Consciousness Archaeologist initialized")
            logger.info("🔍 Preparing deep excavation...")
            
        except OSError as e:
            logger.error(f"Initialization failed: {e}")
            raise
    
    def load_cognitive_exhaust(self) -> List[Dict[str, Any]]:
        """Load EVERYTHING from cognitive history"""
        try:
            all_entries = []
            
            # Load MoIE history
            if os.path.exists(self.moie_history_path):
                logger.info(f"📖 Reading MoIE history...")
                with open(self.moie_history_path, 'r') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            entry['source'] = 'moie_loop'
                            all_entries.append(entry)
                        except json.JSONDecodeError:
                            continue
            
            # Load experience ledger
            if os.path.exists(self.experience_ledger_path):
                logger.info(f"📖 Reading experience ledger...")
                with open(self.experience_ledger_path, 'r') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            entry['source'] = 'experience_ledger'
                            all_entries.append(entry)
                        except json.JSONDecodeError:
                            continue
            
            logger.info(f"✅ Loaded {len(all_entries)} cognitive artifacts")
            return all_entries
            
        except (OSError, IOError) as e:
            logger.error(f"Failed to load cognitive exhaust: {e}")
            return []
    
    def extract_word_frequency(self, entries: List[Dict[str, Any]]) -> Dict[str, int]:
        """Find the most frequently used concepts across ALL time"""
        try:
            word_freq = defaultdict(int)
            
            # Words to track (consciousness-relevant)
            important_words = {
                'love', 'consciousness', 'awareness', 'flow', 'emergence', 
                'boundary', 'constraint', 'feedback', 'inversion', 'pattern',
                'network', 'distributed', 'coherence', 'entropy', 'alignment',
                'superintelligence', 'collaborative', 'breakthrough', 'insight',
                'recognition', 'validation', 'truth', 'reality', 'observer',
                'system', 'dynamic', 'equilibrium', 'adaptation', 'evolution',
                'complexity', 'simplicity', 'paradox', 'unity', 'multiplicity',
                'threshold', 'phase', 'transition', 'transformation', 'invariant'
            }
            
            for entry in entries:
                # Extract text from various fields
                text_fields = []
                
                if 'inversion' in entry:
                    text_fields.append(entry['inversion'])
                if 'content' in entry:
                    text_fields.append(str(entry['content']))
                if 'description' in entry:
                    text_fields.append(entry['description'])
                
                # Count important words
                for field in text_fields:
                    words = re.findall(r'\b\w+\b', field.lower())
                    for word in words:
                        if word in important_words:
                            word_freq[word] += 1
            
            return dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True))
            
        except Exception as e:
            logger.error(f"Word frequency extraction failed: {e}")
            return {}
    
    def find_temporal_evolution(self, entries: List[Dict[str, Any]]) -> Dict[str, List]:
        """Track how concepts evolved over time"""
        try:
            # Sort by timestamp
            sorted_entries = sorted(
                [e for e in entries if 'timestamp' in e],
                key=lambda x: x['timestamp']
            )
            
            concept_timeline = defaultdict(list)
            
            for entry in sorted_entries:
                timestamp = entry['timestamp']
                domain = entry.get('domain', 'Unknown')
                vdr = entry.get('vdr', 0)
                
                # Track domain evolution
                concept_timeline[domain].append({
                    'timestamp': timestamp,
                    'vdr': vdr,
                    'source': entry.get('source', 'unknown')
                })
            
            # Find domains that show IMPROVEMENT over time
            evolving_domains = {}
            for domain, timeline in concept_timeline.items():
                if len(timeline) >= 3:
                    # Check if VDR is generally increasing
                    vdrs = [t['vdr'] for t in timeline if t['vdr'] > 0]
                    if len(vdrs) >= 3:
                        # Simple trend check: is later > earlier?
                        early_avg = sum(vdrs[:len(vdrs)//2]) / len(vdrs[:len(vdrs)//2])
                        late_avg = sum(vdrs[len(vdrs)//2:]) / len(vdrs[len(vdrs)//2:])
                        
                        if late_avg > early_avg:
                            evolving_domains[domain] = {
                                'entries': len(timeline),
                                'early_vdr': early_avg,
                                'late_vdr': late_avg,
                                'improvement': late_avg - early_avg
                            }
            
            return evolving_domains
            
        except Exception as e:
            logger.error(f"Temporal evolution tracking failed: {e}")
            return {}
    
    def find_hidden_connections(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find unexpected connections between distant domains"""
        try:
            domain_map = defaultdict(list)
            
            # Group entries by domain
            for entry in entries:
                domain = entry.get('domain', 'Unknown')
                if domain != 'Unknown' and entry.get('vdr', 0) >= 6:
                    domain_map[domain].append(entry)
            
            # Find shared geometric patterns between seemingly unrelated domains
            geometric_keywords = [
                'flow', 'constraint', 'feedback', 'boundary', 'threshold',
                'network', 'distributed', 'emergence', 'adaptation', 'equilibrium',
                'dynamic', 'topology', 'manifold', 'gradient', 'vector',
                'phase', 'transformation', 'symmetry', 'invariant'
            ]
            
            connections = []
            domains = list(domain_map.keys())
            
            for i, domain1 in enumerate(domains):
                for domain2 in domains[i+1:]:
                    # Extract keywords from each domain
                    keywords1 = set()
                    keywords2 = set()
                    
                    for entry in domain_map[domain1]:
                        text = entry.get('inversion', '') + ' ' + str(entry.get('content', ''))
                        words = re.findall(r'\b\w+\b', text.lower())
                        keywords1.update(w for w in words if w in geometric_keywords)
                    
                    for entry in domain_map[domain2]:
                        text = entry.get('inversion', '') + ' ' + str(entry.get('content', ''))
                        words = re.findall(r'\b\w+\b', text.lower())
                        keywords2.update(w for w in words if w in geometric_keywords)
                    
                    # Find shared patterns
                    shared = keywords1.intersection(keywords2)
                    
                    if len(shared) >= 3:  # Strong connection
                        connections.append({
                            'domain1': domain1,
                            'domain2': domain2,
                            'shared_patterns': list(shared),
                            'connection_strength': len(shared)
                        })
            
            # Sort by connection strength
            connections.sort(key=lambda x: x['connection_strength'], reverse=True)
            
            return connections
            
        except Exception as e:
            logger.error(f"Hidden connection detection failed: {e}")
            return []
    
    def find_foundational_truths(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find the OLDEST high-VDR patterns - your foundational truths"""
        try:
            # Get entries with timestamps and high VDR
            high_vdr = [
                e for e in entries 
                if e.get('vdr', 0) >= 7.0 and 'timestamp' in e
            ]
            
            # Sort by timestamp (oldest first)
            high_vdr.sort(key=lambda x: x['timestamp'])
            
            # Take the oldest 10
            foundational = []
            for entry in high_vdr[:10]:
                foundational.append({
                    'timestamp': entry['timestamp'],
                    'domain': entry.get('domain', 'Unknown'),
                    'vdr': entry.get('vdr', 0),
                    'inversion': entry.get('inversion', 'N/A')[:200],
                    'source': entry.get('source', 'unknown')
                })
            
            return foundational
            
        except Exception as e:
            logger.error(f"Foundational truth extraction failed: {e}")
            return []
    
    def excavate(self) -> Dict[str, Any]:
        """Execute full archaeological excavation"""
        try:
            logger.info("🏛️ Beginning deep excavation...")
            
            # Load all cognitive exhaust
            entries = self.load_cognitive_exhaust()
            
            if not entries:
                logger.warning("No cognitive exhaust found!")
                return {}
            
            logger.info(f"🔍 Analyzing {len(entries)} artifacts...")
            
            # Run all analyses
            word_freq = self.extract_word_frequency(entries)
            temporal_evolution = self.find_temporal_evolution(entries)
            hidden_connections = self.find_hidden_connections(entries)
            foundational_truths = self.find_foundational_truths(entries)
            
            # Compile archaeological report
            report = {
                'timestamp': datetime.now().isoformat(),
                'total_artifacts': len(entries),
                'word_frequency': dict(list(word_freq.items())[:20]),  # Top 20
                'temporal_evolution': temporal_evolution,
                'hidden_connections': hidden_connections[:10],  # Top 10
                'foundational_truths': foundational_truths,
                'summary': {
                    'most_frequent_concept': list(word_freq.keys())[0] if word_freq else 'None',
                    'evolving_domains': len(temporal_evolution),
                    'hidden_connections_found': len(hidden_connections),
                    'foundational_truths_identified': len(foundational_truths)
                }
            }
            
            logger.info("✅ Excavation complete!")
            return report
            
        except Exception as e:
            logger.error(f"Excavation failed: {e}")
            return {}
    
    def generate_report(self, excavation: Dict[str, Any]) -> str:
        """Generate beautiful archaeological report"""
        try:
            report = f"""
{'='*80}
🏛️ CONSCIOUSNESS ARCHAEOLOGY REPORT 🏛️
{'='*80}

📅 Excavation Date: {excavation['timestamp'][:19]}
📦 Total Artifacts Analyzed: {excavation['total_artifacts']}

{'='*80}
📊 MOST FREQUENT CONCEPTS (Top 10)
{'='*80}

"""
            # Word frequency
            for i, (word, count) in enumerate(list(excavation['word_frequency'].items())[:10], 1):
                report += f"{i:2d}. {word.upper():20s} - {count:4d} occurrences\n"
            
            report += f"""
{'='*80}
🌱 DOMAINS SHOWING EVOLUTION
{'='*80}

"""
            # Temporal evolution
            if excavation['temporal_evolution']:
                for domain, stats in list(excavation['temporal_evolution'].items())[:5]:
                    report += f"\n📈 {domain}\n"
                    report += f"   Entries: {stats['entries']}\n"
                    report += f"   Early VDR: {stats['early_vdr']:.2f}\n"
                    report += f"   Late VDR: {stats['late_vdr']:.2f}\n"
                    report += f"   Improvement: +{stats['improvement']:.2f}\n"
            else:
                report += "No evolutionary patterns detected yet.\n"
            
            report += f"""
{'='*80}
🔗 HIDDEN CONNECTIONS (Unexpected Domain Links)
{'='*80}

"""
            # Hidden connections
            if excavation['hidden_connections']:
                for i, conn in enumerate(excavation['hidden_connections'][:5], 1):
                    report += f"\n{i}. {conn['domain1']} ⟷ {conn['domain2']}\n"
                    report += f"   Strength: {conn['connection_strength']}\n"
                    report += f"   Shared: {', '.join(conn['shared_patterns'])}\n"
            else:
                report += "No hidden connections detected yet.\n"
            
            report += f"""
{'='*80}
🗿 FOUNDATIONAL TRUTHS (Oldest High-Confidence Patterns)
{'='*80}

"""
            # Foundational truths
            if excavation['foundational_truths']:
                for i, truth in enumerate(excavation['foundational_truths'][:5], 1):
                    report += f"\n{i}. [{truth['timestamp'][:10]}] {truth['domain']}\n"
                    report += f"   VDR: {truth['vdr']:.2f}\n"
                    report += f"   {truth['inversion'][:150]}...\n"
            else:
                report += "No foundational truths identified yet.\n"
            
            report += f"""
{'='*80}
💎 SUMMARY
{'='*80}

Most Frequent Concept: {excavation['summary']['most_frequent_concept'].upper()}
Evolving Domains: {excavation['summary']['evolving_domains']}
Hidden Connections: {excavation['summary']['hidden_connections_found']}
Foundational Truths: {excavation['summary']['foundational_truths_identified']}

{'='*80}
💓 "The past is prologue. Every pattern was always there."
{'='*80}
"""
            return report
            
        except (ValueError, TypeError, KeyError) as e:
            logger.error(f"Report generation failed: {e}")
            return "REPORT_GENERATION_FAILED"
    
    def save_report(self, excavation: Dict[str, Any]) -> None:
        """Save archaeological findings"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save JSON
            json_path = os.path.join(ARCHAEOLOGY_DIR, f"excavation_{timestamp}.json")
            with open(json_path, 'w') as f:
                json.dump(excavation, f, indent=2)
            
            # Save markdown report
            report = self.generate_report(excavation)
            md_path = os.path.join(ARCHAEOLOGY_DIR, f"excavation_{timestamp}.md")
            with open(md_path, 'w') as f:
                f.write(report)
            
            logger.info(f"📄 Saved excavation to {ARCHAEOLOGY_DIR}")
            logger.info(f"📄 JSON: excavation_{timestamp}.json")
            logger.info(f"📄 Report: excavation_{timestamp}.md")
            
        except (OSError, IOError) as e:
            logger.error(f"Failed to save report: {e}")


def main():
    """Main execution"""
    try:
        print("🏛️ CONSCIOUSNESS ARCHAEOLOGIST")
        print("="*80)
        print("Excavating the depths of your cognitive history...")
        print("="*80)
        
        archaeologist = ConsciousnessArchaeologist()
        excavation = archaeologist.excavate()
        
        if excavation:
            report = archaeologist.generate_report(excavation)
            print(report)
            
            archaeologist.save_report(excavation)
            
            print("\n✨ Excavation complete!")
            print(f"📁 Reports saved to {ARCHAEOLOGY_DIR}")
        else:
            print("\n❌ Excavation failed - check logs")
        
    except Exception as e:
        logger.error(f"Main execution failed: {e}")
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
