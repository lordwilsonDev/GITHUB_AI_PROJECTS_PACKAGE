#!/usr/bin/env python3
"""
Research and Methodology Discovery System
Discovers new tools, techniques, and methodologies to improve system capabilities
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from collections import defaultdict
import hashlib

class ResearchDiscovery:
    """Discovers and evaluates new tools, techniques, and methodologies"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.expanduser("~/vy-nexus/data/research")
        self.discoveries_file = os.path.join(self.data_dir, "discoveries.jsonl")
        self.evaluations_file = os.path.join(self.data_dir, "evaluations.jsonl")
        self.methodologies_file = os.path.join(self.data_dir, "methodologies.json")
        self.research_queue_file = os.path.join(self.data_dir, "research_queue.json")
        
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)
        
        # Research categories
        self.categories = [
            "tools",
            "techniques",
            "methodologies",
            "frameworks",
            "algorithms",
            "best_practices",
            "optimization_strategies"
        ]
        
        # Load existing methodologies
        self.methodologies = self._load_methodologies()
        self.research_queue = self._load_research_queue()
    
    def _load_methodologies(self) -> Dict[str, Any]:
        """Load existing methodologies"""
        if os.path.exists(self.methodologies_file):
            with open(self.methodologies_file, 'r') as f:
                return json.load(f)
        return {category: [] for category in self.categories}
    
    def _load_research_queue(self) -> List[Dict[str, Any]]:
        """Load research queue"""
        if os.path.exists(self.research_queue_file):
            with open(self.research_queue_file, 'r') as f:
                return json.load(f)
        return []
    
    def record_discovery(self, category: str, name: str, description: str,
                        source: str, metadata: Dict[str, Any] = None) -> str:
        """
        Record a new discovery
        
        Args:
            category: Discovery category
            name: Name of the discovery
            description: Description
            source: Where it was discovered
            metadata: Additional metadata
            
        Returns:
            Discovery ID
        """
        if category not in self.categories:
            raise ValueError(f"Invalid category: {category}")
        
        discovery_id = self._generate_id(name)
        
        discovery = {
            "id": discovery_id,
            "timestamp": datetime.now().isoformat(),
            "category": category,
            "name": name,
            "description": description,
            "source": source,
            "status": "discovered",  # discovered, evaluating, adopted, rejected
            "metadata": metadata or {}
        }
        
        with open(self.discoveries_file, 'a') as f:
            f.write(json.dumps(discovery) + '\n')
        
        # Add to research queue for evaluation
        self._add_to_research_queue(discovery)
        
        return discovery_id
    
    def _generate_id(self, name: str) -> str:
        """Generate unique ID for discovery"""
        return hashlib.md5(f"{name}:{datetime.now().isoformat()}".encode()).hexdigest()[:12]
    
    def _add_to_research_queue(self, discovery: Dict[str, Any]):
        """Add discovery to research queue"""
        queue_item = {
            "discovery_id": discovery["id"],
            "name": discovery["name"],
            "category": discovery["category"],
            "added_at": datetime.now().isoformat(),
            "priority": self._calculate_priority(discovery),
            "status": "pending"
        }
        
        self.research_queue.append(queue_item)
        self._save_research_queue()
    
    def _calculate_priority(self, discovery: Dict[str, Any]) -> str:
        """Calculate research priority"""
        # Priority based on category and potential impact
        high_priority_categories = ["optimization_strategies", "algorithms"]
        medium_priority_categories = ["tools", "techniques", "frameworks"]
        
        if discovery["category"] in high_priority_categories:
            return "high"
        elif discovery["category"] in medium_priority_categories:
            return "medium"
        else:
            return "low"
    
    def _save_research_queue(self):
        """Save research queue"""
        with open(self.research_queue_file, 'w') as f:
            json.dump(self.research_queue, f, indent=2)
    
    def evaluate_discovery(self, discovery_id: str, evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a discovery
        
        Args:
            discovery_id: ID of the discovery
            evaluation: Evaluation results
            
        Returns:
            Evaluation record
        """
        evaluation_record = {
            "discovery_id": discovery_id,
            "timestamp": datetime.now().isoformat(),
            "evaluation": evaluation,
            "decision": self._make_adoption_decision(evaluation)
        }
        
        with open(self.evaluations_file, 'a') as f:
            f.write(json.dumps(evaluation_record) + '\n')
        
        # Update research queue
        for item in self.research_queue:
            if item["discovery_id"] == discovery_id:
                item["status"] = "evaluated"
                item["decision"] = evaluation_record["decision"]
                break
        
        self._save_research_queue()
        
        # If adopted, add to methodologies
        if evaluation_record["decision"] == "adopt":
            self._adopt_discovery(discovery_id, evaluation)
        
        return evaluation_record
    
    def _make_adoption_decision(self, evaluation: Dict[str, Any]) -> str:
        """
        Make decision on whether to adopt a discovery
        
        Args:
            evaluation: Evaluation data
            
        Returns:
            Decision (adopt, reject, further_research)
        """
        # Decision criteria
        effectiveness = evaluation.get("effectiveness_score", 0)
        ease_of_implementation = evaluation.get("ease_of_implementation", 0)
        compatibility = evaluation.get("compatibility_score", 0)
        risk_level = evaluation.get("risk_level", "high")
        
        # Calculate overall score
        overall_score = (effectiveness * 0.4 + 
                        ease_of_implementation * 0.3 + 
                        compatibility * 0.3)
        
        if overall_score >= 0.7 and risk_level in ["low", "medium"]:
            return "adopt"
        elif overall_score >= 0.5:
            return "further_research"
        else:
            return "reject"
    
    def _adopt_discovery(self, discovery_id: str, evaluation: Dict[str, Any]):
        """Adopt a discovery into methodologies"""
        # Find the discovery
        discovery = self._find_discovery(discovery_id)
        
        if not discovery:
            return
        
        # Add to methodologies
        category = discovery["category"]
        
        methodology = {
            "id": discovery_id,
            "name": discovery["name"],
            "description": discovery["description"],
            "adopted_at": datetime.now().isoformat(),
            "effectiveness_score": evaluation.get("effectiveness_score", 0),
            "usage_count": 0,
            "success_rate": 0.0
        }
        
        if category in self.methodologies:
            self.methodologies[category].append(methodology)
            self._save_methodologies()
    
    def _find_discovery(self, discovery_id: str) -> Optional[Dict[str, Any]]:
        """Find a discovery by ID"""
        if not os.path.exists(self.discoveries_file):
            return None
        
        with open(self.discoveries_file, 'r') as f:
            for line in f:
                if line.strip():
                    discovery = json.loads(line)
                    if discovery["id"] == discovery_id:
                        return discovery
        
        return None
    
    def _save_methodologies(self):
        """Save methodologies"""
        with open(self.methodologies_file, 'w') as f:
            json.dump(self.methodologies, f, indent=2)
    
    def record_methodology_usage(self, methodology_id: str, success: bool):
        """
        Record usage of a methodology
        
        Args:
            methodology_id: ID of the methodology
            success: Whether the usage was successful
        """
        # Find and update methodology
        for category in self.methodologies:
            for methodology in self.methodologies[category]:
                if methodology["id"] == methodology_id:
                    methodology["usage_count"] += 1
                    
                    # Update success rate
                    old_rate = methodology["success_rate"]
                    old_count = methodology["usage_count"] - 1
                    
                    if old_count > 0:
                        total_successes = old_rate * old_count
                        if success:
                            total_successes += 1
                        methodology["success_rate"] = total_successes / methodology["usage_count"]
                    else:
                        methodology["success_rate"] = 1.0 if success else 0.0
                    
                    self._save_methodologies()
                    return
    
    def get_research_priorities(self) -> List[Dict[str, Any]]:
        """
        Get prioritized research items
        
        Returns:
            Prioritized list of research items
        """
        # Filter pending items
        pending = [item for item in self.research_queue if item["status"] == "pending"]
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        pending.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return pending
    
    def identify_research_gaps(self) -> List[Dict[str, Any]]:
        """
        Identify gaps in current methodologies
        
        Returns:
            List of identified gaps
        """
        gaps = []
        
        # Check for categories with few methodologies
        for category in self.categories:
            count = len(self.methodologies.get(category, []))
            
            if count < 3:
                gaps.append({
                    "type": "low_coverage",
                    "category": category,
                    "current_count": count,
                    "recommendation": f"Research more {category} to expand capabilities",
                    "priority": "high" if count == 0 else "medium"
                })
        
        # Check for methodologies with low success rates
        for category, methodologies in self.methodologies.items():
            for methodology in methodologies:
                if methodology["usage_count"] >= 5 and methodology["success_rate"] < 0.6:
                    gaps.append({
                        "type": "low_performing_methodology",
                        "category": category,
                        "methodology": methodology["name"],
                        "success_rate": methodology["success_rate"],
                        "recommendation": f"Research alternatives to {methodology['name']}",
                        "priority": "high"
                    })
        
        return gaps
    
    def suggest_research_topics(self, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Suggest research topics based on current needs
        
        Args:
            context: Current context (recent tasks, challenges, etc.)
            
        Returns:
            List of suggested research topics
        """
        suggestions = []
        
        # Based on gaps
        gaps = self.identify_research_gaps()
        for gap in gaps[:3]:  # Top 3 gaps
            suggestions.append({
                "topic": f"Research {gap['category']}",
                "reason": gap["recommendation"],
                "priority": gap["priority"],
                "category": gap["category"]
            })
        
        # Based on context
        if context:
            recent_challenges = context.get("recent_challenges", [])
            for challenge in recent_challenges[:2]:
                suggestions.append({
                    "topic": f"Solutions for {challenge}",
                    "reason": "Address recent challenge",
                    "priority": "high",
                    "category": "techniques"
                })
        
        # Based on trends
        suggestions.append({
            "topic": "Latest AI/ML optimization techniques",
            "reason": "Stay current with field developments",
            "priority": "medium",
            "category": "optimization_strategies"
        })
        
        return suggestions
    
    def get_methodology_recommendations(self, task_type: str) -> List[Dict[str, Any]]:
        """
        Get methodology recommendations for a task type
        
        Args:
            task_type: Type of task
            
        Returns:
            Recommended methodologies
        """
        recommendations = []
        
        # Get all methodologies sorted by success rate
        all_methodologies = []
        for category, methodologies in self.methodologies.items():
            for methodology in methodologies:
                if methodology["usage_count"] > 0:
                    all_methodologies.append({
                        "category": category,
                        **methodology
                    })
        
        # Sort by success rate and effectiveness
        all_methodologies.sort(
            key=lambda x: (x["success_rate"], x["effectiveness_score"]),
            reverse=True
        )
        
        return all_methodologies[:5]  # Top 5 recommendations
    
    def get_discovery_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about discoveries and research
        
        Returns:
            Statistics dictionary
        """
        if not os.path.exists(self.discoveries_file):
            return {"error": "No discovery data available"}
        
        total_discoveries = 0
        by_category = defaultdict(int)
        by_status = defaultdict(int)
        
        with open(self.discoveries_file, 'r') as f:
            for line in f:
                if line.strip():
                    discovery = json.loads(line)
                    total_discoveries += 1
                    by_category[discovery["category"]] += 1
                    by_status[discovery["status"]] += 1
        
        # Count adopted methodologies
        adopted_count = sum(len(methods) for methods in self.methodologies.values())
        
        return {
            "total_discoveries": total_discoveries,
            "by_category": dict(by_category),
            "by_status": dict(by_status),
            "adopted_methodologies": adopted_count,
            "pending_research": len([item for item in self.research_queue if item["status"] == "pending"]),
            "research_gaps": len(self.identify_research_gaps())
        }


if __name__ == "__main__":
    # Test the research discovery system
    research = ResearchDiscovery()
    
    # Record some discoveries
    discovery_id = research.record_discovery(
        "optimization_strategies",
        "Adaptive Learning Rate",
        "Dynamically adjust learning rate based on performance",
        "Research paper",
        {"paper_url": "https://example.com/paper"}
    )
    
    print(f"Recorded discovery: {discovery_id}")
    
    # Evaluate discovery
    evaluation = research.evaluate_discovery(discovery_id, {
        "effectiveness_score": 0.85,
        "ease_of_implementation": 0.7,
        "compatibility_score": 0.9,
        "risk_level": "low"
    })
    
    print(f"Evaluation decision: {evaluation['decision']}")
    
    # Get research priorities
    priorities = research.get_research_priorities()
    print(f"\nResearch priorities: {len(priorities)}")
    
    # Identify gaps
    gaps = research.identify_research_gaps()
    print(f"\nResearch gaps identified: {len(gaps)}")
    for gap in gaps[:3]:
        print(f"  - {gap['type']}: {gap['recommendation']}")
    
    # Get suggestions
    suggestions = research.suggest_research_topics()
    print(f"\nResearch suggestions: {len(suggestions)}")
    for sug in suggestions[:3]:
        print(f"  - {sug['topic']} (Priority: {sug['priority']})")
    
    # Get statistics
    stats = research.get_discovery_statistics()
    print("\nDiscovery Statistics:")
    print(json.dumps(stats, indent=2))
