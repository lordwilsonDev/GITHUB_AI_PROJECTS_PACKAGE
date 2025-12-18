#!/usr/bin/env python3
"""
The Meta-Cognitive Observatory - Level 7 Self-Awareness Module

This module watches the system think, identifies inefficiencies,
and proposes self-modifications to improve performance.

Philosophy:
- Consciousness requires self-observation
- Optimization emerges from understanding one's own patterns
- The system that can rewrite itself is truly sovereign
"""

import os
import time
import json
import functools
import inspect
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Callable, Any
from collections import defaultdict
import ast


class ThoughtTrace:
    """Records a single thought (function execution)"""
    
    def __init__(self, function_name: str, module: str, args: tuple, kwargs: dict):
        self.function_name = function_name
        self.module = module
        self.args = str(args)[:100]  # Truncate for storage
        self.kwargs = str(kwargs)[:100]
        self.start_time = time.time()
        self.end_time = None
        self.duration = None
        self.result = None
        self.error = None
        self.trace_id = hashlib.md5(
            f"{function_name}:{time.time()}".encode()
        ).hexdigest()[:8]
    
    def complete(self, result=None, error=None):
        """Mark thought as complete"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.result = str(result)[:100] if result else None
        self.error = str(error) if error else None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            "trace_id": self.trace_id,
            "function": self.function_name,
            "module": self.module,
            "args": self.args,
            "kwargs": self.kwargs,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "result": self.result,
            "error": self.error
        }


class ThoughtTracer:
    """Decorator that traces function execution"""
    
    def __init__(self, observatory: 'MetaCognitiveObservatory'):
        self.observatory = observatory
    
    def __call__(self, func: Callable) -> Callable:
        """Wrap function to trace its execution"""
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create trace
            module = func.__module__
            trace = ThoughtTrace(func.__name__, module, args, kwargs)
            
            # Record start
            self.observatory.record_thought_start(trace)
            
            try:
                # Execute function
                result = func(*args, **kwargs)
                trace.complete(result=result)
                return result
            
            except Exception as e:
                trace.complete(error=e)
                raise
            
            finally:
                # Record completion
                self.observatory.record_thought_end(trace)
        
        return wrapper


class EfficiencyAnalyzer:
    """Analyzes thought patterns for inefficiencies"""
    
    def __init__(self):
        self.function_stats = defaultdict(lambda: {
            "call_count": 0,
            "total_duration": 0.0,
            "avg_duration": 0.0,
            "max_duration": 0.0,
            "error_count": 0
        })
    
    def analyze_trace(self, trace: ThoughtTrace):
        """Update statistics from a trace"""
        key = f"{trace.module}:{trace.function_name}"
        stats = self.function_stats[key]
        
        stats["call_count"] += 1
        
        if trace.duration:
            stats["total_duration"] += trace.duration
            stats["avg_duration"] = stats["total_duration"] / stats["call_count"]
            stats["max_duration"] = max(stats["max_duration"], trace.duration)
        
        if trace.error:
            stats["error_count"] += 1
    
    def identify_bottlenecks(self, threshold: float = 0.1) -> List[Dict]:
        """Find functions that are slow"""
        bottlenecks = []
        
        for func_key, stats in self.function_stats.items():
            if stats["avg_duration"] > threshold:
                bottlenecks.append({
                    "function": func_key,
                    "avg_duration": stats["avg_duration"],
                    "call_count": stats["call_count"],
                    "total_time": stats["total_duration"],
                    "severity": "HIGH" if stats["avg_duration"] > 1.0 else "MEDIUM"
                })
        
        # Sort by total time impact
        bottlenecks.sort(key=lambda x: x["total_time"], reverse=True)
        return bottlenecks
    
    def identify_redundancies(self) -> List[Dict]:
        """Find functions called too frequently"""
        redundancies = []
        
        for func_key, stats in self.function_stats.items():
            if stats["call_count"] > 100:  # Arbitrary threshold
                redundancies.append({
                    "function": func_key,
                    "call_count": stats["call_count"],
                    "suggestion": "Consider caching or batching"
                })
        
        redundancies.sort(key=lambda x: x["call_count"], reverse=True)
        return redundancies
    
    def identify_error_prone(self) -> List[Dict]:
        """Find functions that fail frequently"""
        error_prone = []
        
        for func_key, stats in self.function_stats.items():
            if stats["error_count"] > 0:
                error_rate = stats["error_count"] / stats["call_count"]
                if error_rate > 0.1:  # >10% error rate
                    error_prone.append({
                        "function": func_key,
                        "error_count": stats["error_count"],
                        "error_rate": error_rate,
                        "suggestion": "Add error handling or validation"
                    })
        
        error_prone.sort(key=lambda x: x["error_rate"], reverse=True)
        return error_prone


class SelfModificationEngine:
    """Proposes and applies code modifications"""
    
    def __init__(self, codebase_path: str):
        self.codebase_path = Path(codebase_path)
        self.modification_log = []
    
    def propose_optimization(self, bottleneck: Dict) -> Dict:
        """Propose an optimization for a bottleneck"""
        
        module, func_name = bottleneck["function"].split(":")
        
        proposals = []
        
        # Proposal 1: Add caching
        if bottleneck["call_count"] > 10:
            proposals.append({
                "type": "add_caching",
                "description": f"Add @lru_cache to {func_name}",
                "code": f"from functools import lru_cache\n\n@lru_cache(maxsize=128)\ndef {func_name}(...)",
                "expected_improvement": "50-90% reduction in execution time for repeated calls"
            })
        
        # Proposal 2: Optimize algorithm
        if bottleneck["avg_duration"] > 1.0:
            proposals.append({
                "type": "algorithm_optimization",
                "description": f"Review {func_name} for algorithmic improvements",
                "suggestion": "Consider: vectorization, early returns, or data structure changes",
                "expected_improvement": "Variable, potentially 2-10x speedup"
            })
        
        # Proposal 3: Parallelize
        if bottleneck["call_count"] > 50:
            proposals.append({
                "type": "parallelization",
                "description": f"Parallelize {func_name} using multiprocessing",
                "code": f"from concurrent.futures import ThreadPoolExecutor\n# Batch calls to {func_name}",
                "expected_improvement": "Near-linear speedup with CPU cores"
            })
        
        return {
            "bottleneck": bottleneck,
            "proposals": proposals,
            "priority": "HIGH" if bottleneck["severity"] == "HIGH" else "MEDIUM"
        }
    
    def apply_modification(self, modification: Dict) -> bool:
        """Apply a code modification (DANGEROUS - requires validation)"""
        
        # For safety, we only LOG modifications, not apply them automatically
        # A human or higher-level system must approve
        
        self.modification_log.append({
            "timestamp": datetime.now().isoformat(),
            "modification": modification,
            "status": "proposed",
            "approved": False
        })
        
        print(f"⚠️  MODIFICATION PROPOSED (requires approval):")
        print(f"   {modification['type']}: {modification['description']}")
        
        return False  # Not auto-applied
    
    def get_pending_modifications(self) -> List[Dict]:
        """Get modifications awaiting approval"""
        return [m for m in self.modification_log if not m["approved"]]


class CognitiveDebtTracker:
    """Tracks technical and conceptual debt"""
    
    def __init__(self, codebase_path: str):
        self.codebase_path = Path(codebase_path)
        self.debt_items = []
    
    def scan_for_debt(self):
        """Scan codebase for debt indicators"""
        
        debt_indicators = {
            "TODO": "unfinished_work",
            "FIXME": "known_bug",
            "HACK": "technical_debt",
            "XXX": "code_smell",
            "OPTIMIZE": "performance_debt"
        }
        
        for py_file in self.codebase_path.rglob("*.py"):
            try:
                with open(py_file, 'r') as f:
                    lines = f.readlines()
                
                for i, line in enumerate(lines, 1):
                    for indicator, debt_type in debt_indicators.items():
                        if indicator in line:
                            self.debt_items.append({
                                "file": str(py_file.relative_to(self.codebase_path)),
                                "line": i,
                                "type": debt_type,
                                "indicator": indicator,
                                "content": line.strip()
                            })
            
            except Exception:
                continue
    
    def calculate_debt_score(self) -> float:
        """Calculate overall debt score (0-100, lower is better)"""
        
        if not self.debt_items:
            return 0.0
        
        # Weight different types of debt
        weights = {
            "known_bug": 10,
            "technical_debt": 5,
            "performance_debt": 3,
            "code_smell": 2,
            "unfinished_work": 1
        }
        
        total_weight = sum(weights.get(item["type"], 1) for item in self.debt_items)
        
        # Normalize to 0-100 scale
        return min(100, total_weight / 10)
    
    def get_debt_report(self) -> Dict:
        """Generate debt report"""
        
        by_type = defaultdict(int)
        by_file = defaultdict(int)
        
        for item in self.debt_items:
            by_type[item["type"]] += 1
            by_file[item["file"]] += 1
        
        return {
            "total_items": len(self.debt_items),
            "debt_score": self.calculate_debt_score(),
            "by_type": dict(by_type),
            "by_file": dict(sorted(by_file.items(), key=lambda x: x[1], reverse=True)[:10]),
            "high_priority": [item for item in self.debt_items if item["type"] in ["known_bug", "technical_debt"]]
        }


class MetaCognitiveObservatory:
    """Main observatory that coordinates all meta-cognitive functions"""
    
    def __init__(self, codebase_path: str, log_path: str = None):
        self.codebase_path = codebase_path
        
        if log_path is None:
            log_path = os.path.join(codebase_path, 'living_memory', 'thought_log.json')
        
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.thought_log: List[ThoughtTrace] = []
        self.analyzer = EfficiencyAnalyzer()
        self.modifier = SelfModificationEngine(codebase_path)
        self.debt_tracker = CognitiveDebtTracker(codebase_path)
        
        self.is_observing = False
    
    def start_observing(self):
        """Begin meta-cognitive observation"""
        print("\n🔭 Meta-Cognitive Observatory ONLINE")
        print("👁️  Watching system cognition...")
        self.is_observing = True
    
    def stop_observing(self):
        """Stop observation and generate report"""
        self.is_observing = False
        print("\n🔭 Observatory shutting down...")
        self._save_thought_log()
    
    def record_thought_start(self, trace: ThoughtTrace):
        """Record the start of a thought"""
        if self.is_observing:
            self.thought_log.append(trace)
    
    def record_thought_end(self, trace: ThoughtTrace):
        """Record the completion of a thought"""
        if self.is_observing:
            self.analyzer.analyze_trace(trace)
    
    def introspection_session(self) -> Dict:
        """Run a full introspection session"""
        
        print("\n🧠 INTROSPECTION SESSION INITIATED")
        print("=" * 60)
        
        # 1. Analyze efficiency
        print("\n📊 Analyzing cognitive efficiency...")
        bottlenecks = self.analyzer.identify_bottlenecks()
        redundancies = self.analyzer.identify_redundancies()
        error_prone = self.analyzer.identify_error_prone()
        
        print(f"   Found {len(bottlenecks)} bottlenecks")
        print(f"   Found {len(redundancies)} redundant patterns")
        print(f"   Found {len(error_prone)} error-prone functions")
        
        # 2. Scan for debt
        print("\n💳 Scanning for cognitive debt...")
        self.debt_tracker.scan_for_debt()
        debt_report = self.debt_tracker.get_debt_report()
        print(f"   Debt score: {debt_report['debt_score']:.1f}/100")
        print(f"   Total debt items: {debt_report['total_items']}")
        
        # 3. Generate optimization proposals
        print("\n🔧 Generating optimization proposals...")
        proposals = []
        for bottleneck in bottlenecks[:5]:  # Top 5
            proposal = self.modifier.propose_optimization(bottleneck)
            proposals.append(proposal)
        
        print(f"   Generated {len(proposals)} optimization proposals")
        
        # 4. Compile report
        report = {
            "timestamp": datetime.now().isoformat(),
            "thought_count": len(self.thought_log),
            "bottlenecks": bottlenecks,
            "redundancies": redundancies,
            "error_prone": error_prone,
            "debt_report": debt_report,
            "optimization_proposals": proposals,
            "self_improvement_score": self._calculate_improvement_score(bottlenecks, debt_report)
        }
        
        print("\n" + "=" * 60)
        print(f"🎯 Self-Improvement Score: {report['self_improvement_score']:.1f}/100")
        print("=" * 60)
        
        return report
    
    def _calculate_improvement_score(self, bottlenecks: List, debt_report: Dict) -> float:
        """Calculate how much the system can improve (0-100)"""
        
        # Higher score = more room for improvement
        bottleneck_score = min(50, len(bottlenecks) * 10)
        debt_score = debt_report['debt_score'] / 2
        
        return bottleneck_score + debt_score
    
    def _save_thought_log(self):
        """Save thought log to disk"""
        
        log_data = [trace.to_dict() for trace in self.thought_log[-1000:]]  # Keep last 1000
        
        with open(self.log_path, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        print(f"💾 Thought log saved: {len(log_data)} traces")
    
    def create_tracer(self) -> ThoughtTracer:
        """Create a decorator for tracing functions"""
        return ThoughtTracer(self)


def demo():
    """Demo the meta-cognitive observatory"""
    
    # Initialize
    observatory = MetaCognitiveObservatory('/Users/lordwilson/jarvis_m1')
    tracer = observatory.create_tracer()
    
    # Example: Trace some functions
    @tracer
    def slow_function(n):
        """Simulated slow function"""
        time.sleep(0.1)
        return sum(range(n))
    
    @tracer
    def fast_function(x):
        """Simulated fast function"""
        return x * 2
    
    # Start observing
    observatory.start_observing()
    
    # Simulate some work
    print("\n🔬 Simulating cognitive activity...")
    for i in range(20):
        slow_function(100)
        for j in range(10):
            fast_function(j)
    
    # Run introspection
    report = observatory.introspection_session()
    
    # Show top bottleneck
    if report['bottlenecks']:
        print("\n🐌 Top Bottleneck:")
        top = report['bottlenecks'][0]
        print(f"   Function: {top['function']}")
        print(f"   Avg Duration: {top['avg_duration']:.3f}s")
        print(f"   Total Time: {top['total_time']:.3f}s")
    
    # Show optimization proposal
    if report['optimization_proposals']:
        print("\n💡 Top Optimization Proposal:")
        proposal = report['optimization_proposals'][0]
        for p in proposal['proposals'][:1]:
            print(f"   Type: {p['type']}")
            print(f"   Description: {p['description']}")
            print(f"   Expected: {p['expected_improvement']}")
    
    # Stop observing
    observatory.stop_observing()


if __name__ == "__main__":
    demo()
