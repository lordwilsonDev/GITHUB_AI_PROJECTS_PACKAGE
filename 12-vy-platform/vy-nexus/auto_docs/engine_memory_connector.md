# engine_memory_connector.py

**Location**: `/Users/lordwilson/vy-nexus/engine_memory_connector.py`

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

## Classes

### `EngineMemory`

Memory interface for individual engines

Each engine gets its own EngineMemory instance that:
- Tracks engine identity
- Records experiences automatically
- Enables cross-engine knowledge sharing
- Maintains interaction history

**Methods**:

- `__init__(engine_name)`: Initialize memory connector for an engine
- `_get_or_create_engine_node()`: Get existing engine node or create new one
- `record_experience(experience, experience_type)`: Record an experience from this engine
- `record_breakthrough(breakthrough)`: Record a breakthrough discovery
- `record_interaction(other_engine, interaction_data)`: Record an interaction with another engine
- `query_insights(query, limit)`: Query insights from all engines
- `query_breakthroughs(query, limit)`: Query breakthroughs from all engines
- `get_related_patterns(pattern_id, limit)`: Get patterns related to this engine or a specific pattern
- `get_engine_history(limit)`: Get this engine's full experience history
- `get_interactions_with(other_engine)`: Get all interactions with a specific engine
- `query_by_time(hours_back)`: Get recent experiences from all engines
- `contribute_to_collective(knowledge, knowledge_type)`: Contribute knowledge to collective memory
- `get_collective_knowledge(knowledge_type, limit)`: Get knowledge contributed to collective by all engines

## Functions

### `get_engine_memory(engine_name)`

Get or create EngineMemory instance for an engine

Usage:
    from engine_memory_connector import get_engine_memory
    memory = get_engine_memory('my_engine')

## Dependencies

- `datetime`
- `json`
- `living_memory_engine`
- `logging`
- `os`
- `pathlib`
- `sys`
- `typing`

---
*Auto-generated: 2025-12-18 12:51:48*
