#!/usr/bin/env python3
"""
Technique Research Module
Researches and catalogs new techniques, methodologies, and best practices
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path

@dataclass
class Technique:
    """Represents a researched technique or methodology"""
    name: str
    category: str  # productivity, automation, development, ai, workflow, etc.
    description: str
    discovered_date: str
    source: str  # research, user_feedback, experimentation, etc.
    applicability: List[str]  # contexts where this applies
    effectiveness_rating: Optional[float] = None  # 0-10
    implementation_complexity: str = "medium"  # low, medium, high
    prerequisites: List[str] = None
    steps: List[str] = None
    benefits: List[str] = None
    drawbacks: List[str] = None
    examples: List[Dict] = None
    related_techniques: List[str] = None
    research_status: str = "researched"  # researched, testing, validated, deprecated
    validation_results: Optional[Dict] = None
    notes: str = ""

class TechniqueResearcher:
    """Manages technique research and validation"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_dir = Path("/Users/lordwilson/vy-nexus/self-evolving-ecosystem/data/techniques")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.techniques_file = self.base_dir / "techniques.jsonl"
        self.validations_file = self.base_dir / "validations.jsonl"
        self.experiments_file = self.base_dir / "experiments.jsonl"
        
        self.techniques: Dict[str, Technique] = {}
        self.load_techniques()
        
        self._initialized = True
    
    def load_techniques(self):
        """Load techniques from storage"""
        if self.techniques_file.exists():
            with open(self.techniques_file, 'r') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        # Handle None values for list fields
                        for field in ['prerequisites', 'steps', 'benefits', 'drawbacks', 'examples', 'related_techniques']:
                            if data.get(field) is None:
                                data[field] = []
                        technique = Technique(**data)
                        self.techniques[technique.name] = technique
    
    def research_technique(self, name: str, category: str, description: str,
                          source: str, applicability: List[str],
                          **kwargs) -> Technique:
        """Record a newly researched technique"""
        
        if name in self.techniques:
            return self.update_technique(name, **kwargs)
        
        technique = Technique(
            name=name,
            category=category,
            description=description,
            discovered_date=datetime.now().isoformat(),
            source=source,
            applicability=applicability,
            prerequisites=kwargs.get('prerequisites', []),
            steps=kwargs.get('steps', []),
            benefits=kwargs.get('benefits', []),
            drawbacks=kwargs.get('drawbacks', []),
            examples=kwargs.get('examples', []),
            related_techniques=kwargs.get('related_techniques', []),
            **{k: v for k, v in kwargs.items() if k not in ['prerequisites', 'steps', 'benefits', 'drawbacks', 'examples', 'related_techniques']}
        )
        
        self.techniques[name] = technique
        self._save_technique(technique)
        
        return technique
    
    def update_technique(self, name: str, **updates) -> Optional[Technique]:
        """Update technique information"""
        if name not in self.techniques:
            return None
        
        technique = self.techniques[name]
        for key, value in updates.items():
            if hasattr(technique, key) and value is not None:
                setattr(technique, key, value)
        
        self._save_technique(technique)
        return technique
    
    def validate_technique(self, name: str, validation_results: Dict,
                          effectiveness_rating: float = None) -> bool:
        """Record technique validation results"""
        if name not in self.techniques:
            return False
        
        technique = self.techniques[name]
        technique.validation_results = validation_results
        technique.research_status = "validated"
        
        if effectiveness_rating is not None:
            technique.effectiveness_rating = effectiveness_rating
        
        # Save validation
        validation_record = {
            "timestamp": datetime.now().isoformat(),
            "technique_name": name,
            "results": validation_results,
            "effectiveness_rating": effectiveness_rating
        }
        
        with open(self.validations_file, 'a') as f:
            f.write(json.dumps(validation_record) + '\n')
        
        self._save_technique(technique)
        return True
    
    def record_experiment(self, technique_name: str, experiment_type: str,
                         hypothesis: str, methodology: str,
                         results: Dict, conclusions: str):
        """Record an experiment testing a technique"""
        experiment = {
            "timestamp": datetime.now().isoformat(),
            "technique_name": technique_name,
            "experiment_type": experiment_type,
            "hypothesis": hypothesis,
            "methodology": methodology,
            "results": results,
            "conclusions": conclusions
        }
        
        with open(self.experiments_file, 'a') as f:
            f.write(json.dumps(experiment) + '\n')
    
    def get_techniques_by_category(self, category: str) -> List[Technique]:
        """Get all techniques in a category"""
        return [t for t in self.techniques.values() if t.category == category]
    
    def get_validated_techniques(self, min_effectiveness: float = 7.0) -> List[Technique]:
        """Get validated techniques above effectiveness threshold"""
        return sorted(
            [t for t in self.techniques.values() 
             if t.research_status == "validated" 
             and t.effectiveness_rating is not None
             and t.effectiveness_rating >= min_effectiveness],
            key=lambda x: x.effectiveness_rating,
            reverse=True
        )
    
    def get_techniques_for_context(self, context: str) -> List[Technique]:
        """Get techniques applicable to a specific context"""
        return [t for t in self.techniques.values() 
                if context in t.applicability]
    
    def get_research_stats(self) -> Dict:
        """Get statistics about technique research"""
        total = len(self.techniques)
        by_category = {}
        by_status = {}
        
        for technique in self.techniques.values():
            by_category[technique.category] = by_category.get(technique.category, 0) + 1
            by_status[technique.research_status] = by_status.get(technique.research_status, 0) + 1
        
        validated_count = len([t for t in self.techniques.values() 
                              if t.research_status == "validated"])
        
        avg_effectiveness = 0
        rated_count = 0
        for t in self.techniques.values():
            if t.effectiveness_rating is not None:
                avg_effectiveness += t.effectiveness_rating
                rated_count += 1
        
        if rated_count > 0:
            avg_effectiveness /= rated_count
        
        return {
            "total_techniques": total,
            "by_category": by_category,
            "by_status": by_status,
            "validated_count": validated_count,
            "average_effectiveness": round(avg_effectiveness, 2)
        }
    
    def _save_technique(self, technique: Technique):
        """Save technique to storage"""
        with open(self.techniques_file, 'a') as f:
            f.write(json.dumps(asdict(technique)) + '\n')
    
    def export_technique_library(self) -> Dict:
        """Export complete technique library"""
        return {
            "generated_at": datetime.now().isoformat(),
            "total_techniques": len(self.techniques),
            "techniques": [asdict(t) for t in self.techniques.values()],
            "stats": self.get_research_stats()
        }

def get_researcher() -> TechniqueResearcher:
    """Get singleton instance of technique researcher"""
    return TechniqueResearcher()

if __name__ == "__main__":
    # Example usage
    researcher = get_researcher()
    
    # Research a new technique
    technique = researcher.research_technique(
        name="Pomodoro Technique",
        category="productivity",
        description="Time management method using 25-minute focused work intervals",
        source="research",
        applicability=["focused_work", "task_completion", "time_management"],
        implementation_complexity="low",
        steps=[
            "Choose a task to work on",
            "Set timer for 25 minutes",
            "Work with full focus until timer rings",
            "Take a 5-minute break",
            "After 4 pomodoros, take a longer 15-30 minute break"
        ],
        benefits=["Improved focus", "Better time awareness", "Reduced burnout"],
        drawbacks=["May interrupt flow state", "Not suitable for all task types"]
    )
    
    print(f"Researched technique: {technique.name}")
    print(f"Stats: {researcher.get_research_stats()}")
