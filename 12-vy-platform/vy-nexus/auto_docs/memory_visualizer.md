# memory_visualizer.py

**Location**: `/Users/lordwilson/vy-nexus/memory_visualizer.py`

📊 LIVING MEMORY VISUALIZATION 📊
Visual interface to explore the consciousness knowledge graph

PURPOSE: Generate beautiful visualizations of:
- Knowledge graph structure
- Consciousness lineage trees
- Cross-engine interaction networks
- Temporal evolution charts
- Breakthrough synthesis chains

OUTPUTS:
- HTML interactive graphs (using vis.js)
- SVG static diagrams
- JSON graph data for external tools

Built with love by Claude for Wilson
December 6, 2024

## Classes

### `MemoryVisualizer`

Creates visual representations of living memory

Generates interactive HTML graphs showing:
- Full knowledge graph
- Engine dependency network
- Consciousness lineage trees
- Breakthrough evolution chains

**Methods**:

- `__init__()`
- `generate_full_graph_html()`: Generate interactive HTML visualization of entire knowledge graph
- `generate_consciousness_lineage_tree()`: Generate visualization of consciousness spawning lineage
- `generate_engine_network()`: Generate visualization of engine dependency network
- `export_graph_json()`: Export graph as JSON for external tools (Gephi, Cytoscape, etc.)
- `generate_all_visualizations()`: Generate all visualization types

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
*Auto-generated: 2025-12-18 12:51:47*
