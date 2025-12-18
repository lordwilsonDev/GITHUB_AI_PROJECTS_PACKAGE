# memory_query_interface.py

**Location**: `/Users/lordwilson/vy-nexus/memory_query_interface.py`

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

## Classes

### `MemoryQueryInterface`

Natural language interface to living memory

Parses queries like:
- "Show me all breakthroughs from last week"
- "What engines influenced the love computation discovery?"
- "Trace the evolution of consciousness multiplication"
- "Find dreams about reality co-creation"
- "Show the lineage of consciousness_child_20251206_041358"

**Methods**:

- `__init__()`
- `query(query_str)`: Process a natural language query
- `_parse_query(query_str)`: Parse natural language query into structured format
- `_parse_temporal_query(query_str)`: Parse temporal query
- `_parse_semantic_query(query_str)`: Parse semantic search query
- `_parse_relationship_query(query_str)`: Parse relationship traversal query
- `_parse_lineage_query(query_str)`: Parse lineage tracking query
- `_parse_stats_query(query_str)`: Parse statistics query
- `_extract_node_type(query_str)`: Extract node type from query if specified
- `_execute_temporal_query(parsed)`: Execute temporal query
- `_execute_semantic_query(parsed)`: Execute semantic search
- `_execute_relationship_query(parsed)`: Execute relationship traversal
- `_execute_lineage_query(parsed)`: Execute lineage tracking
- `_execute_stats_query(parsed)`: Execute statistics query
- `pretty_print_results(results_dict)`: Format results for display

## Dependencies

- `datetime`
- `json`
- `living_memory_engine`
- `logging`
- `os`
- `pathlib`
- `re`
- `sys`
- `typing`

---
*Auto-generated: 2025-12-18 12:51:48*
