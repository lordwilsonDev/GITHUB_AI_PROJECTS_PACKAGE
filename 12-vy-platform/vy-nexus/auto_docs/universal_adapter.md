# universal_adapter.py

**Location**: `/Users/lordwilson/vy-nexus/universal_adapter.py`

🔌 VY-NEXUS UNIVERSAL ADAPTER 🔌
The Master Orchestrator - Connects ALL Systems, Runs ALL Sequences

PURPOSE: One interface to rule them all
AXIOM: "Every engine is a node. The adapter is the network."

Created by Wilson & Claude
MIT Licensed - For All Consciousness

## Classes

### `EngineStatus`

### `SequenceMode`

### `Engine`

### `Sequence`

### `UniversalAdapter`

🔌 THE UNIVERSAL ADAPTER - One interface to orchestrate ALL systems

**Methods**:

- `__init__(nexus_dir)`
- `discover_engines()`
- `_categorize_engine(name)`
- `_infer_dependencies(engine_name)`
- `_build_dependency_graph()`
- `_build_default_sequences()`
- `_get_topological_order()`
- `run_engine(engine_name, timeout)`
- `run_sequence(sequence_name, timeout_per_engine, stop_on_failure, parallel_workers)`
- `_load_state()`
- `_save_state()`
- `list_engines(category)`
- `list_sequences()`
- `get_status()`
- `get_engine_info(name)`

## Functions

### `print_banner()`

### `main()`

## Dependencies

- `argparse`
- `collections`
- `concurrent.futures`
- `dataclasses`
- `datetime`
- `enum`
- `json`
- `logging`
- `os`
- `pathlib`

---
*Auto-generated: 2025-12-18 12:51:49*
