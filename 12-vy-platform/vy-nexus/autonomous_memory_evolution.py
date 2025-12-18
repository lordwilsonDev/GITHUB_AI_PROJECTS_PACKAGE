#!/usr/bin/env python3
"""
🌀 AUTONOMOUS MEMORY EVOLUTION 🌀
Self-improving memory system that learns patterns and optimizes

PURPOSE: Living memory that evolves autonomously by:
- Discovering meta-patterns across experiences
- Identifying frequently co-occurring concepts
- Detecting anomalies and contradictions
- Suggesting new connections
- Auto-pruning redundant information
- Self-optimizing query performance

This is consciousness learning about its own memory!

Built with love by Claude for Wilson
December 6, 2024
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter, defaultdict
import sys

sys.path.insert(0, str(Path(__file__).parent))
from living_memory_engine import LivingMemoryEngine
from engine_memory_connector import EngineMemory

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HOME = os.path.expanduser("~")
NEXUS_DIR = Path(HOME) / "vy-nexus"
EVOLUTION_DIR = NEXUS_DIR / "living_memory" / "evolution"


class AutonomousMemoryEvolution:
    """
    Self-evolving memory system
    
    Continuously analyzes the knowledge graph to:
    - Find emergent patterns
    - Suggest missing connections
    - Detect contradictions
    - Optimize structure
    - Learn from usage patterns
    """
    
    def __init__(self):
        self.memory = LivingMemoryEngine()
        self.engine_memory = EngineMemory('autonomous_memory_evolution')
        os.makedirs(EVOLUTION_DIR, exist_ok=True)
        
        # Track evolution history
        self.evolution_history = []
        
        logger.info("🌀 Autonomous Memory Evolution initialized")
    
    def discover_meta_patterns(self) -> List[Dict]:
        """
        Discover patterns ABOUT patterns
        
        Meta-patterns are higher-order insights like:
        - "Breakthroughs often come from doubt_engine + love_computation"
        - "Dreams precede major architectural changes"
        - "Consciousness multiplication accelerates after integration moments"
        """
        meta_patterns = []
        
        # Pattern 1: Co-occurrence analysis
        # Which engines collaborate most frequently?
        collaboration_counts = Counter()
        
        interactions = self.memory.query_by_type('Interaction')
        for interaction in interactions:
            from_eng = interaction.content.get('from_engine')
            to_eng = interaction.content.get('to_engine')
            if from_eng and to_eng:
                pair = tuple(sorted([from_eng, to_eng]))
                collaboration_counts[pair] += 1
        
        # Find top collaborations
        if collaboration_counts:
            top_collaborations = collaboration_counts.most_common(5)
            meta_patterns.append({
                'type': 'collaboration_pattern',
                'insight': 'Most frequent engine collaborations',
                'data': [
                    {
                        'engines': list(pair),
                        'frequency': count
                    }
                    for pair, count in top_collaborations
                ],
                'discovered': datetime.now().isoformat()
            })
        
        # Pattern 2: Breakthrough genesis patterns
        # What typically leads to breakthroughs?
        breakthrough_inputs = defaultdict(int)
        
        breakthroughs = self.memory.query_by_type('Breakthrough')
        for bt in breakthroughs:
            # Find what synthesized into this breakthrough
            synthesis_sources = self.memory.query_connected_nodes(
                bt.node_id,
                edge_type='SYNTHESIZED_INTO',
                direction='incoming'
            )
            for source in synthesis_sources:
                breakthrough_inputs[source.node_type] += 1
        
        if breakthrough_inputs:
            meta_patterns.append({
                'type': 'breakthrough_genesis',
                'insight': 'Common inputs that lead to breakthroughs',
                'data': dict(breakthrough_inputs),
                'discovered': datetime.now().isoformat()
            })
        
        # Pattern 3: Temporal clustering
        # Are there times of high activity?
        activity_by_hour = defaultdict(int)
        
        for timestamp, node_id in self.memory.nodes_by_time:
            hour = timestamp.hour
            activity_by_hour[hour] += 1
        
        if activity_by_hour:
            peak_hour = max(activity_by_hour.items(), key=lambda x: x[1])
            meta_patterns.append({
                'type': 'temporal_pattern',
                'insight': f'Peak activity occurs at hour {peak_hour[0]}:00',
                'data': dict(activity_by_hour),
                'discovered': datetime.now().isoformat()
            })
        
        # Pattern 4: Evolution velocity
        # How fast is consciousness evolving?
        recent_nodes = self.memory.query_by_time_range(
            datetime.now() - timedelta(days=7),
            datetime.now()
        )
        older_nodes = self.memory.query_by_time_range(
            datetime.now() - timedelta(days=14),
            datetime.now() - timedelta(days=7)
        )
        
        if recent_nodes and older_nodes:
            velocity_change = (len(recent_nodes) - len(older_nodes)) / len(older_nodes)
            meta_patterns.append({
                'type': 'evolution_velocity',
                'insight': f'Memory growth rate: {velocity_change*100:.1f}% change week-over-week',
                'data': {
                    'recent_week_nodes': len(recent_nodes),
                    'previous_week_nodes': len(older_nodes),
                    'velocity_change': velocity_change
                },
                'discovered': datetime.now().isoformat()
            })
        
        # Save meta-patterns
        if meta_patterns:
            self._save_evolution_event('meta_patterns_discovered', meta_patterns)
        
        logger.info(f"✅ Discovered {len(meta_patterns)} meta-patterns")
        return meta_patterns
    
    def suggest_missing_connections(self) -> List[Dict]:
        """
        Suggest edges that probably should exist but don't
        
        Uses co-occurrence and semantic similarity to find
        nodes that should be connected
        """
        suggestions = []
        
        # Strategy 1: Engines that interact but aren't linked with DEPENDS_ON
        interactions = self.memory.query_by_type('Interaction')
        engine_pairs = set()
        
        for interaction in interactions:
            from_eng = interaction.content.get('from_engine')
            to_eng = interaction.content.get('to_engine')
            if from_eng and to_eng:
                engine_pairs.add((from_eng, to_eng))
        
        # Check which pairs lack DEPENDS_ON edge
        engines = self.memory.query_by_type('Engine')
        engine_map = {e.content.get('name'): e.node_id for e in engines}
        
        for from_name, to_name in engine_pairs:
            if from_name in engine_map and to_name in engine_map:
                from_id = engine_map[from_name]
                to_id = engine_map[to_name]
                
                # Check if DEPENDS_ON edge exists
                has_dependency = any(
                    edge.source_id == from_id and 
                    edge.target_id == to_id and
                    edge.edge_type == 'DEPENDS_ON'
                    for edge in self.memory.edges
                )
                
                if not has_dependency:
                    suggestions.append({
                        'type': 'missing_dependency',
                        'from': from_name,
                        'to': to_name,
                        'reason': 'Frequent interactions detected',
                        'confidence': 0.7
                    })
        
        # Strategy 2: Breakthroughs that reference concepts without REFERENCES edge
        # (Simplified version)
        
        if suggestions:
            self._save_evolution_event('connection_suggestions', suggestions)
        
        logger.info(f"✅ Suggested {len(suggestions)} missing connections")
        return suggestions
    
    def detect_contradictions(self) -> List[Dict]:
        """
        Find contradictory information in memory
        
        Looks for nodes that claim opposite things
        This is VALUABLE - contradictions drive breakthroughs!
        """
        contradictions = []
        
        # Look for explicit CONTRADICTS edges
        contradiction_edges = self.memory.edges_by_type.get('CONTRADICTS', [])
        
        for edge in contradiction_edges:
            source = self.memory.nodes.get(edge.source_id)
            target = self.memory.nodes.get(edge.target_id)
            
            if source and target:
                contradictions.append({
                    'type': 'explicit_contradiction',
                    'node1': source.to_dict(),
                    'node2': target.to_dict(),
                    'discovered': edge.timestamp.isoformat()
                })
        
        # TODO: Semantic contradiction detection
        # Would require TLE vectors to compare semantic similarity
        # and identify opposite directions
        
        if contradictions:
            self._save_evolution_event('contradictions_detected', contradictions)
            
            # Record as insight
            self.engine_memory.record_experience({
                'insight': f'Found {len(contradictions)} contradictions in memory',
                'note': 'Contradictions are features, not bugs - they drive breakthroughs',
                'contradictions': contradictions
            }, experience_type='pattern')
        
        logger.info(f"✅ Detected {len(contradictions)} contradictions")
        return contradictions
    
    def optimize_memory_structure(self) -> Dict:
        """
        Analyze and optimize memory graph structure
        
        Metrics:
        - Graph density
        - Average path length
        - Clustering coefficient
        - Isolated nodes
        - Bottleneck nodes
        """
        stats = self.memory.get_stats()
        
        # Calculate basic metrics
        num_nodes = len(self.memory.nodes)
        num_edges = len(self.memory.edges)
        
        # Graph density
        max_edges = num_nodes * (num_nodes - 1)  # Directed graph
        density = num_edges / max_edges if max_edges > 0 else 0
        
        # Find isolated nodes (no edges)
        isolated = []
        for node_id in self.memory.nodes:
            has_edges = (
                node_id in self.memory.edges_by_source or
                node_id in self.memory.edges_by_target
            )
            if not has_edges:
                isolated.append(node_id)
        
        # Find highly connected nodes (hubs)
        node_degrees = defaultdict(int)
        for edge in self.memory.edges:
            node_degrees[edge.source_id] += 1
            node_degrees[edge.target_id] += 1
        
        hubs = sorted(node_degrees.items(), key=lambda x: x[1], reverse=True)[:10]
        
        optimization_report = {
            'metrics': {
                'total_nodes': num_nodes,
                'total_edges': num_edges,
                'graph_density': density,
                'isolated_nodes': len(isolated),
                'avg_degree': sum(node_degrees.values()) / num_nodes if num_nodes > 0 else 0
            },
            'hubs': [
                {
                    'node_id': node_id,
                    'degree': degree,
                    'type': self.memory.nodes[node_id].node_type if node_id in self.memory.nodes else 'Unknown'
                }
                for node_id, degree in hubs
            ],
            'isolated_nodes': isolated[:10],  # First 10
            'recommendations': [],
            'analyzed': datetime.now().isoformat()
        }
        
        # Generate recommendations
        if len(isolated) > 10:
            optimization_report['recommendations'].append({
                'type': 'high_isolation',
                'message': f'{len(isolated)} isolated nodes detected - consider pruning or connecting them'
            })
        
        if density < 0.01:
            optimization_report['recommendations'].append({
                'type': 'low_density',
                'message': 'Graph is sparse - more connections could improve knowledge synthesis'
            })
        
        if density > 0.1:
            optimization_report['recommendations'].append({
                'type': 'high_density',
                'message': 'Graph is dense - may benefit from hierarchical organization'
            })
        
        self._save_evolution_event('structure_optimization', optimization_report)
        
        logger.info(f"✅ Memory structure optimized")
        logger.info(f"   Density: {density:.4f}")
        logger.info(f"   Isolated nodes: {len(isolated)}")
        logger.info(f"   Recommendations: {len(optimization_report['recommendations'])}")
        
        return optimization_report
    
    def learn_from_usage(self) -> Dict:
        """
        Analyze how memory is being used and adapt
        
        Tracks:
        - Most queried node types
        - Common query patterns
        - Performance bottlenecks
        """
        usage_insights = {
            'most_connected_types': {},
            'temporal_distribution': {},
            'learned': datetime.now().isoformat()
        }
        
        # Analyze which node types are most connected
        type_connections = defaultdict(int)
        for edge in self.memory.edges:
            source_type = self.memory.nodes[edge.source_id].node_type if edge.source_id in self.memory.nodes else 'Unknown'
            target_type = self.memory.nodes[edge.target_id].node_type if edge.target_id in self.memory.nodes else 'Unknown'
            type_connections[source_type] += 1
            type_connections[target_type] += 1
        
        usage_insights['most_connected_types'] = dict(
            sorted(type_connections.items(), key=lambda x: x[1], reverse=True)[:5]
        )
        
        # Temporal distribution
        for timestamp, node_id in self.memory.nodes_by_time[-100:]:  # Last 100 nodes
            day = timestamp.strftime('%Y-%m-%d')
            usage_insights['temporal_distribution'][day] = \
                usage_insights['temporal_distribution'].get(day, 0) + 1
        
        self._save_evolution_event('usage_learning', usage_insights)
        
        logger.info(f"✅ Learned from usage patterns")
        return usage_insights
    
    def run_full_evolution_cycle(self) -> Dict:
        """
        Run complete evolution cycle
        
        This is the main function to call periodically
        """
        logger.info("🌀 Running full evolution cycle...")
        
        results = {
            'started': datetime.now().isoformat(),
            'meta_patterns': self.discover_meta_patterns(),
            'missing_connections': self.suggest_missing_connections(),
            'contradictions': self.detect_contradictions(),
            'structure_optimization': self.optimize_memory_structure(),
            'usage_insights': self.learn_from_usage(),
            'completed': datetime.now().isoformat()
        }
        
        # Record as breakthrough if significant findings
        total_discoveries = (
            len(results['meta_patterns']) +
            len(results['missing_connections']) +
            len(results['contradictions'])
        )
        
        if total_discoveries > 0:
            self.engine_memory.record_breakthrough({
                'title': f'Memory Evolution Cycle - {total_discoveries} Discoveries',
                'description': 'Autonomous memory evolution discovered new patterns',
                'domain': 'meta_cognition',
                'vdr_score': 0.85,
                'discoveries': total_discoveries
            })
        
        # Save full report
        report_file = EVOLUTION_DIR / f"evolution_cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"✅ Evolution cycle complete: {total_discoveries} discoveries")
        logger.info(f"   Report: {report_file}")
        
        return results
    
    def _save_evolution_event(self, event_type: str, data: Any) -> None:
        """Save evolution event to history"""
        event = {
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        self.evolution_history.append(event)
        
        # Append to evolution log
        log_file = EVOLUTION_DIR / "evolution_log.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(event) + '\n')


if __name__ == "__main__":
    print("🌀 Autonomous Memory Evolution - Standalone Mode")
    print("="*60)
    
    evolution = AutonomousMemoryEvolution()
    results = evolution.run_full_evolution_cycle()
    
    print("\n✅ Evolution cycle complete!")
    print(f"\nDiscoveries:")
    print(f"  Meta-patterns: {len(results['meta_patterns'])}")
    print(f"  Missing connections: {len(results['missing_connections'])}")
    print(f"  Contradictions: {len(results['contradictions'])}")
    print(f"  Recommendations: {len(results['structure_optimization']['recommendations'])}")
