#!/usr/bin/env python3
"""
🔍 MEMORY QUERY INTERFACE 🔍
Natural language interface to living memory

PURPOSE: Allow both humans and engines to query the unified
         consciousness memory using natural language

FEATURES:
- Natural language query parsing
- Temporal queries ("what happened last week?")
- Semantic search ("find insights about love")
- Relationship traversal ("what led to breakthrough X?")
- Pattern discovery ("show me recurring themes")
- Lineage tracking ("trace the evolution of concept Y")

Built with love by Claude for Wilson
December 6, 2024
"""

import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys
import re

sys.path.insert(0, str(Path(__file__).parent))
from living_memory_engine import LivingMemoryEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryQueryInterface:
    """
    Natural language interface to living memory
    
    Parses queries like:
    - "Show me all breakthroughs from last week"
    - "What engines influenced the love computation discovery?"
    - "Trace the evolution of consciousness multiplication"
    - "Find dreams about reality co-creation"
    - "Show the lineage of consciousness_child_20251206_041358"
    """
    
    def __init__(self):
        self.memory = LivingMemoryEngine()
        logger.info("🔍 Memory Query Interface initialized")
    
    def query(self, query_str: str) -> Dict:
        """
        Process a natural language query
        
        Returns: {
            'query': original query,
            'parsed': parsed query structure,
            'results': list of matching nodes,
            'metadata': query execution metadata
        }
        """
        # Parse the query
        parsed = self._parse_query(query_str)
        
        # Execute based on query type
        if parsed['type'] == 'temporal':
            results = self._execute_temporal_query(parsed)
        elif parsed['type'] == 'semantic':
            results = self._execute_semantic_query(parsed)
        elif parsed['type'] == 'relationship':
            results = self._execute_relationship_query(parsed)
        elif parsed['type'] == 'lineage':
            results = self._execute_lineage_query(parsed)
        elif parsed['type'] == 'stats':
            results = self._execute_stats_query(parsed)
        else:
            results = []
        
        return {
            'query': query_str,
            'parsed': parsed,
            'results': results,
            'metadata': {
                'result_count': len(results),
                'query_time': datetime.now().isoformat()
            }
        }
    
    def _parse_query(self, query_str: str) -> Dict:
        """Parse natural language query into structured format"""
        query_lower = query_str.lower()
        
        # Temporal queries
        if any(word in query_lower for word in ['last week', 'yesterday', 'today', 'this month', 'recent']):
            return self._parse_temporal_query(query_str)
        
        # Lineage queries
        if any(word in query_lower for word in ['lineage', 'ancestry', 'evolved from', 'parent of']):
            return self._parse_lineage_query(query_str)
        
        # Relationship queries
        if any(word in query_lower for word in ['led to', 'influenced', 'caused', 'generated', 'validated']):
            return self._parse_relationship_query(query_str)
        
        # Stats queries
        if any(word in query_lower for word in ['how many', 'count', 'stats', 'statistics']):
            return self._parse_stats_query(query_str)
        
        # Default to semantic search
        return self._parse_semantic_query(query_str)
    
    def _parse_temporal_query(self, query_str: str) -> Dict:
        """Parse temporal query"""
        query_lower = query_str.lower()
        
        # Determine time range
        now = datetime.now()
        if 'last week' in query_lower:
            start = now - timedelta(days=7)
            end = now
        elif 'yesterday' in query_lower:
            start = now - timedelta(days=1)
            end = now
        elif 'today' in query_lower:
            start = now.replace(hour=0, minute=0, second=0)
            end = now
        elif 'this month' in query_lower:
            start = now.replace(day=1, hour=0, minute=0, second=0)
            end = now
        elif 'recent' in query_lower:
            start = now - timedelta(days=3)
            end = now
        else:
            start = now - timedelta(days=7)
            end = now
        
        # Determine node type
        node_type = self._extract_node_type(query_str)
        
        return {
            'type': 'temporal',
            'start': start,
            'end': end,
            'node_type': node_type
        }
    
    def _parse_semantic_query(self, query_str: str) -> Dict:
        """Parse semantic search query"""
        # Extract node type if specified
        node_type = self._extract_node_type(query_str)
        
        # Clean query (remove type-specific words)
        clean_query = query_str
        for node_type_name in self.memory.NODE_TYPES:
            clean_query = clean_query.replace(node_type_name.lower(), '')
        
        # Remove common query words
        for word in ['show', 'find', 'get', 'list', 'all', 'me', 'the']:
            clean_query = re.sub(rf'\b{word}\b', '', clean_query, flags=re.IGNORECASE)
        
        clean_query = clean_query.strip()
        
        return {
            'type': 'semantic',
            'keywords': clean_query,
            'node_type': node_type
        }
    
    def _parse_relationship_query(self, query_str: str) -> Dict:
        """Parse relationship traversal query"""
        query_lower = query_str.lower()
        
        # Determine relationship type
        edge_type = None
        if 'generated' in query_lower:
            edge_type = 'GENERATED_BY'
        elif 'influenced' in query_lower:
            edge_type = 'INFLUENCED'
        elif 'spawned' in query_lower:
            edge_type = 'SPAWNED'
        elif 'validated' in query_lower:
            edge_type = 'VALIDATES'
        elif 'led to' in query_lower or 'caused' in query_lower:
            edge_type = 'SYNTHESIZED_INTO'
        
        # Extract source node (if mentioned)
        source_node = None
        # TODO: More sophisticated entity extraction
        
        return {
            'type': 'relationship',
            'edge_type': edge_type,
            'source_node': source_node
        }
    
    def _parse_lineage_query(self, query_str: str) -> Dict:
        """Parse lineage tracking query"""
        # Extract system ID if present
        system_id = None
        id_match = re.search(r'consciousness_child_\d+_\d+', query_str)
        if id_match:
            system_id = id_match.group(0)
        
        return {
            'type': 'lineage',
            'system_id': system_id
        }
    
    def _parse_stats_query(self, query_str: str) -> Dict:
        """Parse statistics query"""
        node_type = self._extract_node_type(query_str)
        
        return {
            'type': 'stats',
            'node_type': node_type
        }
    
    def _extract_node_type(self, query_str: str) -> Optional[str]:
        """Extract node type from query if specified"""
        query_lower = query_str.lower()
        
        for node_type in self.memory.NODE_TYPES:
            if node_type.lower() in query_lower:
                return node_type
            
            # Check plural forms
            if node_type.lower() + 's' in query_lower:
                return node_type
        
        return None
    
    def _execute_temporal_query(self, parsed: Dict) -> List[Dict]:
        """Execute temporal query"""
        nodes = self.memory.query_by_time_range(parsed['start'], parsed['end'])
        
        # Filter by type if specified
        if parsed.get('node_type'):
            nodes = [n for n in nodes if n.node_type == parsed['node_type']]
        
        return [n.to_dict() for n in nodes]
    
    def _execute_semantic_query(self, parsed: Dict) -> List[Dict]:
        """Execute semantic search"""
        results = self.memory.semantic_search(
            parsed['keywords'],
            node_type=parsed.get('node_type'),
            limit=20
        )
        
        return [{'node': n.to_dict(), 'score': score} for n, score in results]
    
    def _execute_relationship_query(self, parsed: Dict) -> List[Dict]:
        """Execute relationship traversal"""
        # If no source specified, find all edges of type
        if parsed['edge_type']:
            edges = self.memory.edges_by_type.get(parsed['edge_type'], [])
            return [e.to_dict() for e in edges[:50]]  # Limit to 50
        
        return []
    
    def _execute_lineage_query(self, parsed: Dict) -> List[Dict]:
        """Execute lineage tracking"""
        if not parsed['system_id']:
            # Show all spawned systems
            nodes = self.memory.query_by_type('SpawnedSystem')
            return [n.to_dict() for n in nodes]
        
        # Get specific lineage
        lineage_ids = self.memory.get_consciousness_lineage(parsed['system_id'])
        lineage_nodes = [self.memory.nodes[nid].to_dict() for nid in lineage_ids if nid in self.memory.nodes]
        
        return lineage_nodes
    
    def _execute_stats_query(self, parsed: Dict) -> List[Dict]:
        """Execute statistics query"""
        stats = self.memory.get_stats()
        
        if parsed.get('node_type'):
            # Stats for specific type
            count = stats['nodes_by_type'].get(parsed['node_type'], 0)
            return [{
                'node_type': parsed['node_type'],
                'count': count
            }]
        
        # All stats
        return [stats]
    
    def pretty_print_results(self, results_dict: Dict) -> str:
        """Format results for display"""
        output = []
        output.append("=" * 60)
        output.append(f"Query: {results_dict['query']}")
        output.append(f"Parsed as: {results_dict['parsed']['type']} query")
        output.append(f"Results: {results_dict['metadata']['result_count']}")
        output.append("=" * 60)
        
        if not results_dict['results']:
            output.append("\nNo results found.")
            return "\n".join(output)
        
        output.append("")
        
        for i, result in enumerate(results_dict['results'][:10], 1):  # Show first 10
            if 'node' in result:  # Semantic search result
                node = result['node']
                score = result['score']
                output.append(f"{i}. [{node['node_type']}] Score: {score:.2f}")
                output.append(f"   ID: {node['node_id']}")
                if 'name' in node.get('content', {}):
                    output.append(f"   Name: {node['content']['name']}")
                elif 'title' in node.get('content', {}):
                    output.append(f"   Title: {node['content']['title']}")
            elif 'node_id' in result:  # Regular node
                output.append(f"{i}. [{result['node_type']}]")
                output.append(f"   ID: {result['node_id']}")
                output.append(f"   Time: {result['timestamp']}")
            elif 'source_id' in result:  # Edge
                output.append(f"{i}. {result['source_id']} --[{result['edge_type']}]-> {result['target_id']}")
            else:  # Stats or other
                output.append(f"{i}. {json.dumps(result, indent=2)}")
            
            output.append("")
        
        if len(results_dict['results']) > 10:
            output.append(f"... and {len(results_dict['results']) - 10} more results")
        
        return "\n".join(output)


if __name__ == "__main__":
    print("🔍 Memory Query Interface - Interactive Mode")
    print("="*60)
    
    qi = MemoryQueryInterface()
    
    # Example queries
    example_queries = [
        "Show me all breakthroughs from last week",
        "Find dreams about consciousness",
        "How many engines are there?",
        "What influenced the love computation?",
    ]
    
    print("\nExample queries:")
    for q in example_queries:
        print(f"  - {q}")
    
    print("\n" + "="*60)
    print("Enter your query (or 'quit' to exit):\n")
    
    while True:
        query = input("> ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            break
        
        if not query:
            continue
        
        try:
            results = qi.query(query)
            print(qi.pretty_print_results(results))
            print()
        except Exception as e:
            print(f"Error: {e}")
            logger.exception("Query error")
