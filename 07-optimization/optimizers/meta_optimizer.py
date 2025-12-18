#!/usr/bin/env python3
"""
Meta-Optimizer - Level 12 Component
Optimizes the optimization process itself (meta-learning)
"""

import json
import os
from typing import Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import statistics

@dataclass
class OptimizationResult:
    strategy: str
    success: bool
    improvement: float
    time_taken: float
    timestamp: str

class MetaOptimizer:
    """Learns which optimization strategies work best"""
    
    def __init__(self, history_path: str = ".meta_optimization_history.json"):
        self.history_path = history_path
        self.history: List[Dict] = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        if os.path.exists(self.history_path):
            with open(self.history_path, 'r') as f:
                return json.load(f)
        return []
    
    def record_result(self, result: OptimizationResult):
        """Record an optimization result"""
        self.history.append(asdict(result))
        self._save_history()
    
    def _save_history(self):
        with open(self.history_path, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def get_best_strategies(self) -> List[str]:
        """Identify most successful strategies"""
        if not self.history:
            return []
        
        # Group by strategy
        by_strategy = {}
        for result in self.history:
            strategy = result['strategy']
            if strategy not in by_strategy:
                by_strategy[strategy] = []
            by_strategy[strategy].append(result)
        
        # Calculate success rates
        strategy_scores = []
        for strategy, results in by_strategy.items():
            success_rate = sum(1 for r in results if r['success']) / len(results)
            avg_improvement = statistics.mean([r['improvement'] for r in results if r['success']])
            score = success_rate * avg_improvement
            strategy_scores.append((strategy, score))
        
        # Sort by score
        strategy_scores.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in strategy_scores]
    
    def recommend_strategy(self, context: Dict[str, Any]) -> str:
        """Recommend best strategy for given context"""
        best_strategies = self.get_best_strategies()
        if best_strategies:
            return best_strategies[0]
        return "default"
    
    def generate_report(self) -> str:
        """Generate meta-learning report"""
        report = []
        report.append("# Meta-Optimization Report\n")
        report.append(f"Total Optimizations: {len(self.history)}\n")
        
        if self.history:
            success_rate = sum(1 for r in self.history if r['success']) / len(self.history)
            report.append(f"Overall Success Rate: {success_rate:.1%}\n")
            
            best_strategies = self.get_best_strategies()
            report.append("\n## Best Strategies\n")
            for i, strategy in enumerate(best_strategies[:5], 1):
                report.append(f"{i}. {strategy}\n")
        
        return "".join(report)

if __name__ == "__main__":
    print("META-OPTIMIZER - LEVEL 12")
    meta = MetaOptimizer()
    
    # Demo: Record some results
    meta.record_result(OptimizationResult(
        strategy="list_comprehension",
        success=True,
        improvement=0.15,
        time_taken=0.5,
        timestamp=datetime.now().isoformat()
    ))
    
    meta.record_result(OptimizationResult(
        strategy="caching",
        success=True,
        improvement=0.45,
        time_taken=1.2,
        timestamp=datetime.now().isoformat()
    ))
    
    print(meta.generate_report())
    print("✅ Meta-optimizer initialized with demo data")
