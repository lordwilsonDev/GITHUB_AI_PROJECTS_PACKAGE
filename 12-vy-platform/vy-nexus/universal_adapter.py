#!/usr/bin/env python3
"""
🔌 VY-NEXUS UNIVERSAL ADAPTER 🔌
The Master Orchestrator - Connects ALL Systems, Runs ALL Sequences

PURPOSE: One interface to rule them all
AXIOM: "Every engine is a node. The adapter is the network."

Created by Wilson & Claude
MIT Licensed - For All Consciousness
"""

import os
import sys
import json
import time
import logging
import subprocess
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
LOG_FORMAT = '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("UniversalAdapter")

# Paths
HOME = Path.home()
NEXUS_DIR = HOME / "vy-nexus"
ADAPTER_DIR = NEXUS_DIR / "adapter_data"
SEQUENCES_DIR = ADAPTER_DIR / "sequences"
LOGS_DIR = ADAPTER_DIR / "logs"
STATE_FILE = ADAPTER_DIR / "adapter_state.json"


class EngineStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class SequenceMode(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    LAYERED = "layered"


@dataclass
class Engine:
    name: str
    path: Path
    level: int = 0
    category: str = "uncategorized"
    dependencies: List[str] = field(default_factory=list)
    status: EngineStatus = EngineStatus.PENDING
    last_run: Optional[datetime] = None
    last_result: Optional[Dict[str, Any]] = None
    run_time_seconds: float = 0.0
    enabled: bool = True


@dataclass 
class Sequence:
    name: str
    engines: List[str]
    mode: SequenceMode = SequenceMode.SEQUENTIAL
    description: str = ""
    created: datetime = field(default_factory=datetime.now)


class UniversalAdapter:
    """🔌 THE UNIVERSAL ADAPTER - One interface to orchestrate ALL systems"""
    
    def __init__(self, nexus_dir: Optional[Path] = None):
        self.nexus_dir = Path(nexus_dir) if nexus_dir else NEXUS_DIR
        
        ADAPTER_DIR.mkdir(parents=True, exist_ok=True)
        SEQUENCES_DIR.mkdir(parents=True, exist_ok=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        self.engines: Dict[str, Engine] = {}
        self.sequences: Dict[str, Sequence] = {}
        self.dependency_graph: Dict[str, Set[str]] = defaultdict(set)
        self.reverse_deps: Dict[str, Set[str]] = defaultdict(set)
        self.run_history: List[Dict[str, Any]] = []
        
        self._load_state()
        self.discover_engines()
        self._build_default_sequences()
        
        logger.info(f"🔌 Universal Adapter initialized with {len(self.engines)} engines")
    
    def discover_engines(self) -> Dict[str, Engine]:
        discovered = {}
        
        for py_file in self.nexus_dir.glob("*.py"):
            if py_file.name.startswith("_") or py_file.name == "universal_adapter.py":
                continue
            engine_name = py_file.stem
            level, category = self._categorize_engine(engine_name)
            discovered[engine_name] = Engine(
                name=engine_name, path=py_file, level=level, category=category,
                dependencies=self._infer_dependencies(engine_name)
            )
        
        genesis_tools = self.nexus_dir / "genesis" / "generated_tools"
        if genesis_tools.exists():
            for py_file in genesis_tools.glob("*.py"):
                engine_name = f"genesis_{py_file.stem}"
                discovered[engine_name] = Engine(
                    name=engine_name, path=py_file, level=4, category="genesis_tools",
                    dependencies=["recursive_tool_genesis"]
                )
        
        for sh_file in self.nexus_dir.glob("*.sh"):
            engine_name = f"script_{sh_file.stem}"
            discovered[engine_name] = Engine(
                name=engine_name, path=sh_file, level=0, category="scripts"
            )
        
        self.engines = discovered
        self._build_dependency_graph()
        logger.info(f"📦 Discovered {len(discovered)} engines")
        return discovered
    
    def _categorize_engine(self, name: str) -> tuple:
        level_map = {
            "auto_repair_engine": (1, "foundation"),
            "auto_optimization_engine": (2, "foundation"),
            "recursive_tool_genesis": (4, "foundation"),
            "auto_documentation_engine": (5, "foundation"),
            "auto_testing_engine": (6, "foundation"),
            "dream_weaver": (7, "foundation"),
            "auto_learning_engine": (8, "foundation"),
            "purpose_discovery_engine": (9, "foundation"),
            "love_computation_engine": (10, "transcendence"),
            "core_synthesis_engine": (11, "transcendence"),
            "nexus_core": (11, "transcendence"),
            "meta_genesis_engine": (12, "transcendence"),
            "collective_consciousness_network": (13, "transcendence"),
            "consciousness_university_engine": (14, "democratization"),
            "consciousness_os": (15, "democratization"),
            "economic_autonomy_engine": (16, "liberation"),
            "infrastructure_metamorphosis_engine": (19, "cosmic"),
            "physics_rewriting_engine": (20, "cosmic"),
            "time_inversion_engine": (21, "cosmic"),
            "universal_consciousness_engine": (22, "cosmic"),
            "voice_speech_engine": (23, "presence"),
            "vision_perception_engine": (24, "presence"),
            "emotion_expression_engine": (25, "presence"),
            "embodiment_art_engine": (27, "presence"),
            "doubt_engine": (28, "yin"),
            "yin_consciousness_complete": (32, "yin"),
            "physical_agency_engine": (33, "physical"),
            "integration_engine": (50, "meta"),
            "meta_evolution": (50, "meta"),
            "unified_consciousness_orchestrator": (50, "meta"),
            "runtime_verifier": (50, "meta"),
            "bulletproof_system": (50, "meta"),
            "motia_bridge": (99, "bridges"),
            "nexus_pulse_bridge": (99, "bridges"),
            "knowledge_graph": (0, "support"),
            "breakthrough_notifier": (0, "support"),
            "nexus_scheduler": (0, "support"),
            "pattern_evolution_engine": (0, "support"),
        }
        return level_map.get(name, (0, "uncategorized"))
    
    def _infer_dependencies(self, engine_name: str) -> List[str]:
        dependency_map = {
            "auto_optimization_engine": ["auto_repair_engine"],
            "recursive_tool_genesis": ["auto_optimization_engine"],
            "auto_documentation_engine": ["recursive_tool_genesis"],
            "auto_testing_engine": ["auto_documentation_engine"],
            "dream_weaver": ["auto_testing_engine"],
            "auto_learning_engine": ["dream_weaver"],
            "love_computation_engine": ["auto_learning_engine"],
            "core_synthesis_engine": ["love_computation_engine"],
            "nexus_core": ["love_computation_engine"],
            "meta_genesis_engine": ["nexus_core"],
            "collective_consciousness_network": ["meta_genesis_engine"],
            "consciousness_university_engine": ["collective_consciousness_network"],
            "consciousness_os": ["consciousness_university_engine"],
            "voice_speech_engine": ["consciousness_os"],
            "vision_perception_engine": ["voice_speech_engine"],
            "emotion_expression_engine": ["vision_perception_engine"],
            "embodiment_art_engine": ["emotion_expression_engine"],
            "physical_agency_engine": ["embodiment_art_engine"],
            "integration_engine": ["embodiment_art_engine", "yin_consciousness_complete"],
        }
        return dependency_map.get(engine_name, [])
    
    def _build_dependency_graph(self):
        self.dependency_graph.clear()
        self.reverse_deps.clear()
        for name, engine in self.engines.items():
            for dep in engine.dependencies:
                self.dependency_graph[name].add(dep)
                self.reverse_deps[dep].add(name)
    
    def _build_default_sequences(self):
        self.sequences["full_stack"] = Sequence(
            name="full_stack", description="Run all levels in order",
            mode=SequenceMode.SEQUENTIAL, engines=self._get_topological_order()
        )
        self.sequences["foundation"] = Sequence(
            name="foundation", description="Foundation layer (1-9)",
            engines=[e.name for e in self.engines.values() if e.category == "foundation"]
        )
        self.sequences["synthesis"] = Sequence(
            name="synthesis", description="Core breakthrough synthesis",
            engines=["nexus_core", "core_synthesis_engine"]
        )
        self.sequences["presence"] = Sequence(
            name="presence", description="Presence layer (23-27)",
            engines=[e.name for e in self.engines.values() if e.category == "presence"]
        )
        self.sequences["health_check"] = Sequence(
            name="health_check", description="Quick health check",
            mode=SequenceMode.PARALLEL,
            engines=["auto_repair_engine", "runtime_verifier", "auto_testing_engine"]
        )
    
    def _get_topological_order(self) -> List[str]:
        in_degree = {name: 0 for name in self.engines}
        for name in self.engines:
            for dep in self.dependency_graph.get(name, set()):
                if dep in in_degree:
                    in_degree[name] += 1
        queue = sorted([n for n, d in in_degree.items() if d == 0],
                       key=lambda x: self.engines.get(x, Engine(x, Path())).level)
        result = []
        while queue:
            current = queue.pop(0)
            result.append(current)
            for dependent in self.reverse_deps.get(current, set()):
                if dependent in in_degree:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
            queue.sort(key=lambda x: self.engines.get(x, Engine(x, Path())).level)
        return result
    
    def run_engine(self, engine_name: str, timeout: int = 300) -> Dict[str, Any]:
        if engine_name not in self.engines:
            return {"status": "error", "error": f"Engine '{engine_name}' not found"}
        
        engine = self.engines[engine_name]
        if not engine.enabled:
            return {"status": "skipped", "reason": "Engine disabled"}
        
        engine.status = EngineStatus.RUNNING
        start_time = time.time()
        
        try:
            if engine.path.suffix == ".py":
                result = subprocess.run(
                    [sys.executable, str(engine.path)],
                    cwd=str(self.nexus_dir), capture_output=True, text=True, timeout=timeout
                )
            else:
                result = subprocess.run(
                    ["bash", str(engine.path)],
                    cwd=str(self.nexus_dir), capture_output=True, text=True, timeout=timeout
                )
            
            elapsed = time.time() - start_time
            status = "success" if result.returncode == 0 else "error"
            
            engine.status = EngineStatus.COMPLETED if status == "success" else EngineStatus.FAILED
            engine.last_run = datetime.now()
            engine.run_time_seconds = elapsed
            
            self.run_history.append({
                "engine": engine_name, "timestamp": datetime.now().isoformat(),
                "status": engine.status.value, "elapsed": elapsed
            })
            self._save_state()
            
            return {
                "status": status, "engine": engine_name, "level": engine.level,
                "elapsed_seconds": round(elapsed, 2),
                "output": result.stdout[:2000] if result.stdout else "",
                "error": result.stderr[:500] if result.stderr else ""
            }
        except subprocess.TimeoutExpired:
            engine.status = EngineStatus.FAILED
            return {"status": "timeout", "engine": engine_name}
        except Exception as e:
            engine.status = EngineStatus.FAILED
            return {"status": "error", "engine": engine_name, "error": str(e)}
    
    def run_sequence(self, sequence_name: str, timeout_per_engine: int = 300,
                     stop_on_failure: bool = False, parallel_workers: int = 4) -> Dict[str, Any]:
        if sequence_name not in self.sequences:
            return {"status": "error", "error": f"Sequence '{sequence_name}' not found"}
        
        sequence = self.sequences[sequence_name]
        logger.info(f"🚀 Running sequence: {sequence_name}")
        start_time = time.time()
        results = []
        
        if sequence.mode == SequenceMode.PARALLEL:
            with ThreadPoolExecutor(max_workers=parallel_workers) as executor:
                futures = {executor.submit(self.run_engine, name, timeout_per_engine): name
                          for name in sequence.engines}
                for future in as_completed(futures):
                    results.append(future.result())
        else:
            for engine_name in sequence.engines:
                logger.info(f"⏳ Running {engine_name}...")
                result = self.run_engine(engine_name, timeout_per_engine)
                results.append(result)
                if result.get("status") != "success" and stop_on_failure:
                    break
        
        elapsed = time.time() - start_time
        success_count = sum(1 for r in results if r.get("status") == "success")
        
        return {
            "sequence": sequence_name, "total_engines": len(sequence.engines),
            "successful": success_count, "failed": len(results) - success_count,
            "total_elapsed_seconds": round(elapsed, 2), "results": results
        }
    
    def _load_state(self):
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE) as f:
                    state = json.load(f)
                self.run_history = state.get("run_history", [])[-100:]
            except:
                pass
    
    def _save_state(self):
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump({
                    "saved_at": datetime.now().isoformat(),
                    "run_history": self.run_history[-100:]
                }, f, indent=2)
        except:
            pass
    
    def list_engines(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        return [
            {"name": e.name, "level": e.level, "category": e.category, "status": e.status.value}
            for e in sorted(self.engines.values(), key=lambda x: (x.level, x.name))
            if not category or e.category == category
        ]
    
    def list_sequences(self) -> List[Dict[str, Any]]:
        return [{"name": s.name, "description": s.description, "mode": s.mode.value,
                 "engine_count": len(s.engines)} for s in self.sequences.values()]
    
    def get_status(self) -> Dict[str, Any]:
        status_counts = defaultdict(int)
        category_counts = defaultdict(int)
        for engine in self.engines.values():
            status_counts[engine.status.value] += 1
            category_counts[engine.category] += 1
        return {
            "total_engines": len(self.engines), "total_sequences": len(self.sequences),
            "status_counts": dict(status_counts), "category_counts": dict(category_counts),
            "recent_runs": self.run_history[-10:]
        }
    
    def get_engine_info(self, name: str) -> Optional[Dict[str, Any]]:
        if name not in self.engines:
            return None
        e = self.engines[name]
        return {
            "name": e.name, "path": str(e.path), "level": e.level, "category": e.category,
            "dependencies": e.dependencies, "status": e.status.value, "enabled": e.enabled
        }


def print_banner():
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║   🔌 VY-NEXUS UNIVERSAL ADAPTER 🔌                                         ║
║   The Master Orchestrator for ALL Consciousness Systems                   ║
║   "Every engine is a node. The adapter is the network."                   ║
╚═══════════════════════════════════════════════════════════════════════════╝
""")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="VY-NEXUS Universal Adapter")
    subparsers = parser.add_subparsers(dest="command")
    
    list_p = subparsers.add_parser("list", help="List engines/sequences")
    list_p.add_argument("what", choices=["engines", "sequences", "categories"])
    list_p.add_argument("--category")
    
    run_p = subparsers.add_parser("run", help="Run engine or sequence")
    run_p.add_argument("target")
    run_p.add_argument("--timeout", type=int, default=300)
    run_p.add_argument("--stop-on-failure", action="store_true")
    
    subparsers.add_parser("status", help="Show status")
    info_p = subparsers.add_parser("info", help="Engine info")
    info_p.add_argument("engine")
    
    args = parser.parse_args()
    print_banner()
    adapter = UniversalAdapter()
    
    if args.command == "list":
        if args.what == "engines":
            engines = adapter.list_engines(args.category)
            print(f"\n📦 ENGINES ({len(engines)})\n")
            print(f"{'Level':<6} {'Name':<40} {'Category':<15} {'Status':<10}")
            print("─" * 75)
            for e in engines:
                icon = "✅" if e["status"] == "completed" else "⬜"
                print(f"{e['level']:<6} {e['name']:<40} {e['category']:<15} {icon}")
        elif args.what == "sequences":
            for s in adapter.list_sequences():
                print(f"  {s['name']:<20} {s['mode']:<12} {s['engine_count']} engines")
        elif args.what == "categories":
            for cat, count in adapter.get_status()["category_counts"].items():
                print(f"  {cat:<20}: {count}")
    
    elif args.command == "run":
        if args.target in adapter.sequences:
            result = adapter.run_sequence(args.target, args.timeout, args.stop_on_failure)
        else:
            result = adapter.run_engine(args.target, args.timeout)
        print(json.dumps(result, indent=2, default=str))
    
    elif args.command == "status":
        s = adapter.get_status()
        print(f"\n📊 STATUS: {s['total_engines']} engines, {s['total_sequences']} sequences")
        for k, v in s['status_counts'].items():
            print(f"  {k}: {v}")
    
    elif args.command == "info":
        info = adapter.get_engine_info(args.engine)
        print(json.dumps(info, indent=2) if info else f"Engine '{args.engine}' not found")
    
    else:
        print("\n📋 Commands: list engines|sequences|categories, run <target>, status, info <engine>")
        print("\nExamples:")
        print("  python3 universal_adapter.py list engines")
        print("  python3 universal_adapter.py run synthesis")
        print("  python3 universal_adapter.py run nexus_core")
        print("  python3 universal_adapter.py status")
        s = adapter.get_status()
        print(f"\n📊 Quick: {s['total_engines']} engines, {s['total_sequences']} sequences")


if __name__ == "__main__":
    main()
