#!/usr/bin/env python3
"""
Methodology Analyzer
Analyzes and compares different methodologies for task completion and optimization
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import defaultdict

@dataclass
class Methodology:
    """Represents a methodology or approach"""
    name: str
    domain: str  # software_development, project_management, productivity, etc.
    description: str
    principles: List[str]
    practices: List[str]
    tools_used: List[str]
    success_metrics: List[str]
    adoption_date: str
    effectiveness_score: Optional[float] = None  # 0-10
    use_count: int = 0
    success_rate: Optional[float] = None
    avg_completion_time: Optional[float] = None
    user_satisfaction: Optional[float] = None
    strengths: List[str] = None
    weaknesses: List[str] = None
    best_for: List[str] = None
    avoid_for: List[str] = None
    status: str = "active"  # active, testing, deprecated
    notes: str = ""

@dataclass
class MethodologyComparison:
    """Comparison between methodologies"""
    timestamp: str
    methodologies: List[str]
    context: str
    criteria: List[str]
    scores: Dict[str, Dict[str, float]]  # methodology -> criterion -> score
    winner: str
    reasoning: str

class MethodologyAnalyzer:
    """Analyzes and compares methodologies"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_dir = Path("/Users/lordwilson/vy-nexus/self-evolving-ecosystem/data/methodologies")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.methodologies_file = self.base_dir / "methodologies.jsonl"
        self.comparisons_file = self.base_dir / "comparisons.jsonl"
        self.applications_file = self.base_dir / "applications.jsonl"
        
        self.methodologies: Dict[str, Methodology] = {}
        self.load_methodologies()
        
        self._initialized = True
    
    def load_methodologies(self):
        """Load methodologies from storage"""
        if self.methodologies_file.exists():
            with open(self.methodologies_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        # Handle None values for list fields
                        for field in ['strengths', 'weaknesses', 'best_for', 'avoid_for']:
                            if data.get(field) is None:
                                data[field] = []
                        methodology = Methodology(**data)
                        self.methodologies[methodology.name] = methodology
    
    def add_methodology(self, name: str, domain: str, description: str,
                       principles: List[str], practices: List[str],
                       tools_used: List[str], success_metrics: List[str],
                       **kwargs) -> Methodology:
        """Add a new methodology"""
        
        if name in self.methodologies:
            return self.update_methodology(name, **kwargs)
        
        methodology = Methodology(
            name=name,
            domain=domain,
            description=description,
            principles=principles,
            practices=practices,
            tools_used=tools_used,
            success_metrics=success_metrics,
            adoption_date=datetime.now().isoformat(),
            strengths=kwargs.get('strengths', []),
            weaknesses=kwargs.get('weaknesses', []),
            best_for=kwargs.get('best_for', []),
            avoid_for=kwargs.get('avoid_for', []),
            **{k: v for k, v in kwargs.items() if k not in ['strengths', 'weaknesses', 'best_for', 'avoid_for']}
        )
        
        self.methodologies[name] = methodology
        self._save_methodology(methodology)
        
        return methodology
    
    def update_methodology(self, name: str, **updates) -> Optional[Methodology]:
        """Update methodology information"""
        if name not in self.methodologies:
            return None
        
        methodology = self.methodologies[name]
        for key, value in updates.items():
            if hasattr(methodology, key) and value is not None:
                setattr(methodology, key, value)
        
        self._save_methodology(methodology)
        return methodology
    
    def record_application(self, methodology_name: str, task_type: str,
                          success: bool, completion_time: float,
                          satisfaction: float, notes: str = ""):
        """Record an application of a methodology"""
        if methodology_name not in self.methodologies:
            return False
        
        methodology = self.methodologies[methodology_name]
        methodology.use_count += 1
        
        # Update success rate
        if methodology.success_rate is None:
            methodology.success_rate = 1.0 if success else 0.0
        else:
            total_successes = methodology.success_rate * (methodology.use_count - 1)
            total_successes += 1 if success else 0
            methodology.success_rate = total_successes / methodology.use_count
        
        # Update average completion time
        if methodology.avg_completion_time is None:
            methodology.avg_completion_time = completion_time
        else:
            total_time = methodology.avg_completion_time * (methodology.use_count - 1)
            methodology.avg_completion_time = (total_time + completion_time) / methodology.use_count
        
        # Update user satisfaction
        if methodology.user_satisfaction is None:
            methodology.user_satisfaction = satisfaction
        else:
            total_satisfaction = methodology.user_satisfaction * (methodology.use_count - 1)
            methodology.user_satisfaction = (total_satisfaction + satisfaction) / methodology.use_count
        
        # Calculate effectiveness score
        methodology.effectiveness_score = (
            (methodology.success_rate * 4) +  # 40% weight
            (methodology.user_satisfaction / 10 * 3) +  # 30% weight
            (min(1.0, 60 / max(1, methodology.avg_completion_time)) * 3)  # 30% weight (faster is better)
        )
        
        # Record application
        application = {
            "timestamp": datetime.now().isoformat(),
            "methodology_name": methodology_name,
            "task_type": task_type,
            "success": success,
            "completion_time": completion_time,
            "satisfaction": satisfaction,
            "notes": notes
        }
        
        with open(self.applications_file, 'a') as f:
            f.write(json.dumps(application) + '\n')
        
        self._save_methodology(methodology)
        return True
    
    def compare_methodologies(self, methodology_names: List[str],
                            context: str, criteria: List[str]) -> MethodologyComparison:
        """Compare multiple methodologies"""
        scores = {}
        
        for name in methodology_names:
            if name not in self.methodologies:
                continue
            
            methodology = self.methodologies[name]
            scores[name] = {}
            
            for criterion in criteria:
                # Score based on criterion
                if criterion == "effectiveness":
                    scores[name][criterion] = methodology.effectiveness_score or 5.0
                elif criterion == "success_rate":
                    scores[name][criterion] = (methodology.success_rate or 0.5) * 10
                elif criterion == "speed":
                    if methodology.avg_completion_time:
                        scores[name][criterion] = min(10, 60 / methodology.avg_completion_time)
                    else:
                        scores[name][criterion] = 5.0
                elif criterion == "satisfaction":
                    scores[name][criterion] = methodology.user_satisfaction or 5.0
                else:
                    scores[name][criterion] = 5.0  # Default neutral score
        
        # Calculate winner
        total_scores = {name: sum(criteria_scores.values()) 
                       for name, criteria_scores in scores.items()}
        winner = max(total_scores, key=total_scores.get) if total_scores else ""
        
        comparison = MethodologyComparison(
            timestamp=datetime.now().isoformat(),
            methodologies=methodology_names,
            context=context,
            criteria=criteria,
            scores=scores,
            winner=winner,
            reasoning=f"Winner based on total score across {len(criteria)} criteria"
        )
        
        # Save comparison
        with open(self.comparisons_file, 'a') as f:
            f.write(json.dumps(asdict(comparison)) + '\n')
        
        return comparison
    
    def get_best_methodology_for(self, context: str) -> Optional[Methodology]:
        """Get the best methodology for a given context"""
        candidates = [m for m in self.methodologies.values()
                     if context in m.best_for and m.status == "active"]
        
        if not candidates:
            return None
        
        return max(candidates, key=lambda m: m.effectiveness_score or 0)
    
    def get_methodologies_by_domain(self, domain: str) -> List[Methodology]:
        """Get all methodologies in a domain"""
        return [m for m in self.methodologies.values() if m.domain == domain]
    
    def get_top_methodologies(self, limit: int = 10) -> List[Methodology]:
        """Get top performing methodologies"""
        return sorted(
            [m for m in self.methodologies.values() if m.effectiveness_score is not None],
            key=lambda m: m.effectiveness_score,
            reverse=True
        )[:limit]
    
    def get_analysis_stats(self) -> Dict:
        """Get statistics about methodology analysis"""
        total = len(self.methodologies)
        by_domain = defaultdict(int)
        by_status = defaultdict(int)
        
        total_uses = 0
        avg_effectiveness = 0
        effective_count = 0
        
        for methodology in self.methodologies.values():
            by_domain[methodology.domain] += 1
            by_status[methodology.status] += 1
            total_uses += methodology.use_count
            
            if methodology.effectiveness_score is not None:
                avg_effectiveness += methodology.effectiveness_score
                effective_count += 1
        
        if effective_count > 0:
            avg_effectiveness /= effective_count
        
        return {
            "total_methodologies": total,
            "by_domain": dict(by_domain),
            "by_status": dict(by_status),
            "total_applications": total_uses,
            "average_effectiveness": round(avg_effectiveness, 2)
        }
    
    def _save_methodology(self, methodology: Methodology):
        """Save methodology to storage"""
        with open(self.methodologies_file, 'a') as f:
            f.write(json.dumps(asdict(methodology)) + '\n')
    
    def export_methodology_catalog(self) -> Dict:
        """Export complete methodology catalog"""
        return {
            "generated_at": datetime.now().isoformat(),
            "total_methodologies": len(self.methodologies),
            "methodologies": [asdict(m) for m in self.methodologies.values()],
            "stats": self.get_analysis_stats()
        }

def get_analyzer() -> MethodologyAnalyzer:
    """Get singleton instance of methodology analyzer"""
    return MethodologyAnalyzer()

if __name__ == "__main__":
    # Example usage
    analyzer = get_analyzer()
    
    # Add a methodology
    methodology = analyzer.add_methodology(
        name="Agile Development",
        domain="software_development",
        description="Iterative development methodology with short sprints",
        principles=["Individuals over processes", "Working software over documentation"],
        practices=["Daily standups", "Sprint planning", "Retrospectives"],
        tools_used=["Jira", "Trello", "GitHub"],
        success_metrics=["Sprint velocity", "Bug count", "Customer satisfaction"],
        strengths=["Flexible", "Fast feedback", "Customer-focused"],
        weaknesses=["Can lack documentation", "Requires discipline"],
        best_for=["software_projects", "changing_requirements"]
    )
    
    print(f"Added methodology: {methodology.name}")
    print(f"Stats: {analyzer.get_analysis_stats()}")
