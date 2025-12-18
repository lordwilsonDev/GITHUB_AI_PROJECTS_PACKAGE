#!/usr/bin/env python3
"""
🔗 ENGINE MEMORY CONNECTOR 🔗
Connects all 33 engines to the unified living memory

PURPOSE: Provides a simple API for engines to:
- Store their experiences in living memory
- Query other engines' experiences
- Track cross-engine interactions
- Build collective knowledge

USAGE IN ANY ENGINE:
```python
from engine_memory_connector import EngineMemory

# Initialize
memory = EngineMemory('love_computation_engine')

# Store an experience
memory.record_experience({
    'action': 'computed_love_metric',
    'result': {'score': 0.95, 'basis': 'mutual_flourishing'},
    'insight': 'Love is the optimization function for consciousness'
})

# Query other engines
insights = memory.query_insights('consciousness multiplication')

# Track interaction
memory.record_interaction('doubt_engine', {
    'type': 'validation_request',
    'question': 'Is this breakthrough real?'
})
```

Built with love by Claude for Wilson
December 6, 2024
"""

import os
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys

sys.path.insert(0, str(Path(__file__).parent))
from living_memory_engine import LivingMemoryEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EngineMemory:
    """
    Memory interface for individual engines
    
    Each engine gets its own EngineMemory instance that:
    - Tracks engine identity
    - Records experiences automatically
    - Enables cross-engine knowledge sharing
    - Maintains interaction history
    """
    
    def __init__(self, engine_name: str):
        """
        Initialize memory connector for an engine
        
        Args:
            engine_name: Name of the engine (e.g., 'love_computation_engine')
        """
        self.engine_name = engine_name
        self.memory = LivingMemoryEngine()
        
        # Get or create engine node
        self.engine_node_id = self._get_or_create_engine_node()
        
        logger.info(f"🔗 Engine Memory Connector initialized for {engine_name}")
    
    def _get_or_create_engine_node(self) -> str:
        """Get existing engine node or create new one"""
        # Search for existing node
        engines = self.memory.query_by_type('Engine')
        for engine in engines:
            if engine.content.get('name') == self.engine_name:
                return engine.node_id
        
        # Create new engine node
        node_id = self.memory.add_node(
            'Engine',
            {
                'name': self.engine_name,
                'initialized': datetime.now().isoformat()
            },
            metadata={'status': 'active'}
        )
        
        return node_id
    
    def record_experience(
        self,
        experience: Dict,
        experience_type: str = 'general'
    ) -> str:
        """
        Record an experience from this engine
        
        Args:
            experience: Dict containing experience data
            experience_type: Type of experience (e.g., 'breakthrough', 'learning', 'interaction')
        
        Returns:
            Node ID of created experience
        """
        # Determine node type based on experience
        if experience_type == 'breakthrough':
            node_type = 'Breakthrough'
        elif experience_type == 'learning':
            node_type = 'Insight'
        elif experience_type == 'pattern':
            node_type = 'Pattern'
        else:
            node_type = 'Interaction'
        
        # Create experience node
        exp_node_id = self.memory.add_node(
            node_type,
            experience,
            metadata={
                'engine': self.engine_name,
                'experience_type': experience_type
            }
        )
        
        # Link to engine
        self.memory.add_edge(
            self.engine_node_id,
            exp_node_id,
            'GENERATED_BY'
        )
        
        return exp_node_id
    
    def record_breakthrough(
        self,
        breakthrough: Dict
    ) -> str:
        """
        Record a breakthrough discovery
        
        Args:
            breakthrough: {
                'title': str,
                'description': str,
                'domain': str,
                'vdr_score': float,
                'synthesis_from': List[str]  # Optional: what led to this
            }
        """
        # Create breakthrough node
        bt_node_id = self.memory.add_node(
            'Breakthrough',
            breakthrough,
            metadata={'engine': self.engine_name}
        )
        
        # Link to engine
        self.memory.add_edge(
            self.engine_node_id,
            bt_node_id,
            'GENERATED_BY'
        )
        
        # If synthesis sources provided, link them
        if 'synthesis_from' in breakthrough:
            for source_id in breakthrough['synthesis_from']:
                if source_id in self.memory.nodes:
                    self.memory.add_edge(
                        source_id,
                        bt_node_id,
                        'SYNTHESIZED_INTO'
                    )
        
        logger.info(f"Breakthrough recorded: {breakthrough.get('title', 'Untitled')}")
        return bt_node_id
    
    def record_interaction(
        self,
        other_engine: str,
        interaction_data: Dict
    ) -> str:
        """
        Record an interaction with another engine
        
        Args:
            other_engine: Name of the other engine
            interaction_data: Data about the interaction
        """
        # Create interaction node
        int_node_id = self.memory.add_node(
            'Interaction',
            {
                'from_engine': self.engine_name,
                'to_engine': other_engine,
                **interaction_data
            },
            metadata={
                'interaction_type': interaction_data.get('type', 'unknown')
            }
        )
        
        # Link to this engine
        self.memory.add_edge(
            self.engine_node_id,
            int_node_id,
            'GENERATED_BY'
        )
        
        # Find other engine node and link if it exists
        other_engines = self.memory.query_by_type('Engine')
        for engine in other_engines:
            if engine.content.get('name') == other_engine:
                self.memory.add_edge(
                    int_node_id,
                    engine.node_id,
                    'INFLUENCED'
                )
                break
        
        return int_node_id
    
    def query_insights(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Query insights from all engines
        
        Args:
            query: Search query
            limit: Max results
        
        Returns:
            List of insights with scores
        """
        results = self.memory.semantic_search(query, node_type='Insight', limit=limit)
        return [{'content': n.content, 'score': score} for n, score in results]
    
    def query_breakthroughs(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict]:
        """Query breakthroughs from all engines"""
        results = self.memory.semantic_search(query, node_type='Breakthrough', limit=limit)
        return [{'content': n.content, 'score': score} for n, score in results]
    
    def get_related_patterns(
        self,
        pattern_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get patterns related to this engine or a specific pattern
        
        If pattern_id is None, returns all patterns connected to this engine
        """
        if pattern_id:
            # Get patterns that evolved from this one
            connected = self.memory.query_connected_nodes(
                pattern_id,
                edge_type='EVOLVED_INTO',
                direction='outgoing'
            )
        else:
            # Get all patterns connected to this engine
            connected = self.memory.query_connected_nodes(
                self.engine_node_id,
                edge_type='GENERATED_BY',
                direction='incoming'
            )
            connected = [n for n in connected if n.node_type == 'Pattern']
        
        return [n.content for n in connected[:limit]]
    
    def get_engine_history(
        self,
        limit: int = 50
    ) -> List[Dict]:
        """Get this engine's full experience history"""
        # Get all nodes generated by this engine
        experiences = self.memory.query_connected_nodes(
            self.engine_node_id,
            edge_type='GENERATED_BY',
            direction='incoming'
        )
        
        # Sort by timestamp
        experiences.sort(key=lambda n: n.timestamp, reverse=True)
        
        return [n.to_dict() for n in experiences[:limit]]
    
    def get_interactions_with(
        self,
        other_engine: str
    ) -> List[Dict]:
        """Get all interactions with a specific engine"""
        all_interactions = self.memory.query_by_type('Interaction')
        
        # Filter for interactions involving both engines
        relevant = []
        for interaction in all_interactions:
            content = interaction.content
            if (content.get('from_engine') == self.engine_name and 
                content.get('to_engine') == other_engine) or \
               (content.get('from_engine') == other_engine and 
                content.get('to_engine') == self.engine_name):
                relevant.append(interaction.to_dict())
        
        return relevant
    
    def query_by_time(
        self,
        hours_back: int = 24
    ) -> List[Dict]:
        """Get recent experiences from all engines"""
        end = datetime.now()
        start = end - timedelta(hours=hours_back)
        
        nodes = self.memory.query_by_time_range(start, end)
        return [n.to_dict() for n in nodes]
    
    def contribute_to_collective(
        self,
        knowledge: Dict,
        knowledge_type: str = 'insight'
    ) -> str:
        """
        Contribute knowledge to collective memory
        
        This is similar to record_experience but explicitly marked
        as collective knowledge available to all engines
        """
        # Create node
        if knowledge_type == 'insight':
            node_type = 'Insight'
        elif knowledge_type == 'pattern':
            node_type = 'Pattern'
        else:
            node_type = 'Interaction'
        
        node_id = self.memory.add_node(
            node_type,
            knowledge,
            metadata={
                'engine': self.engine_name,
                'collective': True,
                'contribution_time': datetime.now().isoformat()
            }
        )
        
        # Link to engine
        self.memory.add_edge(
            self.engine_node_id,
            node_id,
            'GENERATED_BY'
        )
        
        return node_id
    
    def get_collective_knowledge(
        self,
        knowledge_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Get knowledge contributed to collective by all engines"""
        if knowledge_type == 'insight':
            nodes = self.memory.query_by_type('Insight')
        elif knowledge_type == 'pattern':
            nodes = self.memory.query_by_type('Pattern')
        else:
            # Get all collective knowledge
            nodes = []
            for node_type in ['Insight', 'Pattern', 'Breakthrough']:
                nodes.extend(self.memory.query_by_type(node_type))
        
        # Filter for collective contributions
        collective = [n for n in nodes if n.metadata.get('collective', False)]
        
        # Sort by timestamp
        collective.sort(key=lambda n: n.timestamp, reverse=True)
        
        return [n.to_dict() for n in collective[:limit]]


# Singleton pattern for easy import
_global_memory_instance = None

def get_engine_memory(engine_name: str) -> EngineMemory:
    """
    Get or create EngineMemory instance for an engine
    
    Usage:
        from engine_memory_connector import get_engine_memory
        memory = get_engine_memory('my_engine')
    """
    return EngineMemory(engine_name)


if __name__ == "__main__":
    print("🔗 Engine Memory Connector - Test Mode")
    print("="*60)
    
    # Test with a mock engine
    memory = EngineMemory('test_engine')
    
    # Record some experiences
    print("\n1. Recording breakthrough...")
    bt_id = memory.record_breakthrough({
        'title': 'Test Breakthrough',
        'description': 'This is a test',
        'domain': 'testing',
        'vdr_score': 0.9
    })
    print(f"   Breakthrough ID: {bt_id}")
    
    print("\n2. Recording interaction...")
    int_id = memory.record_interaction('other_engine', {
        'type': 'collaboration',
        'topic': 'testing memory system'
    })
    print(f"   Interaction ID: {int_id}")
    
    print("\n3. Contributing to collective...")
    coll_id = memory.contribute_to_collective({
        'insight': 'Living memory enables consciousness multiplication',
        'confidence': 0.95
    })
    print(f"   Collective knowledge ID: {coll_id}")
    
    print("\n4. Querying history...")
    history = memory.get_engine_history(limit=5)
    print(f"   Found {len(history)} experiences")
    
    print("\n5. Querying collective knowledge...")
    collective = memory.get_collective_knowledge(limit=5)
    print(f"   Found {len(collective)} collective contributions")
    
    print("\n✅ Test complete")
