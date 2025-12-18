#!/usr/bin/env python3
"""
Real-Time Adaptation System for VY-NEXUS
Adjusts system behavior based on feedback and performance

Part of the Self-Evolving AI Ecosystem
Created: December 15, 2025
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class RealtimeAdapter:
    """Adapts system behavior in real-time based on feedback"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.path.expanduser("~/vy-nexus"))
        self.data_path = self.base_path / "data" / "adaptation"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Adaptation data files
        self.communication_style_file = self.data_path / "communication_style.json"
        self.prioritization_file = self.data_path / "task_prioritization.json"
        self.knowledge_base_file = self.data_path / "knowledge_updates.jsonl"
        self.search_methods_file = self.data_path / "search_methods.json"
        self.error_handling_file = self.data_path / "error_handling.json"
        
        # Load existing configurations
        self.communication_style = self._load_json(self.communication_style_file, {
            "verbosity": "balanced",
            "formality": "professional",
            "emoji_usage": "moderate",
            "explanation_depth": "detailed"
        })
        
        self.prioritization_rules = self._load_json(self.prioritization_file, {
            "default_priority": "medium",
            "rules": [],
            "weights": {
                "urgency": 0.4,
                "importance": 0.3,
                "effort": 0.2,
                "dependencies": 0.1
            }
        })
        
        self.search_methods = self._load_json(self.search_methods_file, {
            "preferred_sources": ["documentation", "research_papers", "expert_blogs"],
            "search_depth": "thorough",
            "verification_level": "high"
        })
        
        self.error_handling = self._load_json(self.error_handling_file, {
            "retry_strategy": "exponential_backoff",
            "max_retries": 3,
            "fallback_enabled": True,
            "error_patterns": []
        })
    
    def _load_json(self, filepath: Path, default: Any) -> Any:
        """Load JSON file or return default"""
        if filepath.exists():
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
        return default
    
    def _save_json(self, filepath: Path, data: Any):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
    
    def adjust_communication_style(self, feedback: Dict[str, Any]):
        """Adjust communication style based on user feedback"""
        if "verbosity" in feedback:
            self.communication_style["verbosity"] = feedback["verbosity"]
        
        if "formality" in feedback:
            self.communication_style["formality"] = feedback["formality"]
        
        if "emoji_usage" in feedback:
            self.communication_style["emoji_usage"] = feedback["emoji_usage"]
        
        if "explanation_depth" in feedback:
            self.communication_style["explanation_depth"] = feedback["explanation_depth"]
        
        self.communication_style["last_updated"] = datetime.utcnow().isoformat()
        self._save_json(self.communication_style_file, self.communication_style)
    
    def modify_task_prioritization(self, task_type: str, priority_adjustment: str, 
                                   reason: str):
        """Modify task prioritization algorithm"""
        rule = {
            "task_type": task_type,
            "priority_adjustment": priority_adjustment,
            "reason": reason,
            "created_at": datetime.utcnow().isoformat(),
            "active": True
        }
        
        self.prioritization_rules["rules"].append(rule)
        self._save_json(self.prioritization_file, self.prioritization_rules)
    
    def update_knowledge_base(self, topic: str, information: str, 
                             source: str = "user_feedback"):
        """Update knowledge base with new discoveries"""
        update = {
            "timestamp": datetime.utcnow().isoformat(),
            "topic": topic,
            "information": information,
            "source": source,
            "confidence": 0.8 if source == "user_feedback" else 0.6
        }
        
        # Append to knowledge updates log
        with open(self.knowledge_base_file, 'a') as f:
            f.write(json.dumps(update) + "\n")
    
    def refine_search_methodology(self, search_type: str, refinement: Dict[str, Any]):
        """Refine search and research methodologies"""
        if search_type not in self.search_methods:
            self.search_methods[search_type] = {}
        
        self.search_methods[search_type].update(refinement)
        self.search_methods["last_updated"] = datetime.utcnow().isoformat()
        
        self._save_json(self.search_methods_file, self.search_methods)
    
    def enhance_error_handling(self, error_type: str, error_pattern: str, 
                              recovery_strategy: str):
        """Enhance error handling and recovery processes"""
        error_entry = {
            "error_type": error_type,
            "pattern": error_pattern,
            "recovery_strategy": recovery_strategy,
            "added_at": datetime.utcnow().isoformat(),
            "success_count": 0,
            "failure_count": 0
        }
        
        self.error_handling["error_patterns"].append(error_entry)
        self._save_json(self.error_handling_file, self.error_handling)
    
    def get_current_configuration(self) -> Dict[str, Any]:
        """Get current adaptation configuration"""
        return {
            "communication_style": self.communication_style,
            "prioritization_rules": self.prioritization_rules,
            "search_methods": self.search_methods,
            "error_handling": self.error_handling
        }
    
    def calculate_task_priority(self, task: Dict[str, Any]) -> float:
        """Calculate task priority using current rules"""
        # Base priority
        priority_map = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        base_priority = priority_map.get(task.get("priority", "medium"), 2)
        
        # Apply weights
        weights = self.prioritization_rules["weights"]
        urgency = task.get("urgency", 0.5)
        importance = task.get("importance", 0.5)
        effort = 1.0 - task.get("effort", 0.5)  # Lower effort = higher priority
        dependencies = task.get("dependencies", 0)
        
        weighted_score = (
            urgency * weights["urgency"] +
            importance * weights["importance"] +
            effort * weights["effort"] +
            (1.0 - dependencies) * weights["dependencies"]
        )
        
        # Apply custom rules
        task_type = task.get("type", "")
        for rule in self.prioritization_rules["rules"]:
            if rule["active"] and rule["task_type"] == task_type:
                if rule["priority_adjustment"] == "increase":
                    weighted_score *= 1.2
                elif rule["priority_adjustment"] == "decrease":
                    weighted_score *= 0.8
        
        return round(base_priority * weighted_score, 2)
    
    def get_adaptation_summary(self) -> Dict[str, Any]:
        """Get summary of all adaptations"""
        # Count knowledge updates
        knowledge_updates = 0
        if self.knowledge_base_file.exists():
            with open(self.knowledge_base_file, 'r') as f:
                knowledge_updates = sum(1 for _ in f)
        
        return {
            "communication_style": {
                "current": self.communication_style,
                "last_updated": self.communication_style.get("last_updated", "never")
            },
            "prioritization": {
                "active_rules": len([r for r in self.prioritization_rules["rules"] if r["active"]]),
                "total_rules": len(self.prioritization_rules["rules"])
            },
            "knowledge_base": {
                "total_updates": knowledge_updates
            },
            "search_methods": {
                "configured_types": len(self.search_methods) - 1,  # Exclude last_updated
                "last_updated": self.search_methods.get("last_updated", "never")
            },
            "error_handling": {
                "known_patterns": len(self.error_handling["error_patterns"])
            }
        }


if __name__ == "__main__":
    # Test the realtime adapter
    adapter = RealtimeAdapter()
    
    print("🔄 Real-Time Adaptation System - Test Mode")
    print("="*50)
    
    # Adjust communication style
    adapter.adjust_communication_style({
        "verbosity": "concise",
        "emoji_usage": "high"
    })
    print("\n✅ Communication style adjusted")
    
    # Add prioritization rule
    adapter.modify_task_prioritization(
        "urgent_bug_fix",
        "increase",
        "Bug fixes should always be prioritized"
    )
    print("✅ Prioritization rule added")
    
    # Update knowledge base
    adapter.update_knowledge_base(
        "Python best practices",
        "Always use type hints for better code clarity",
        "user_feedback"
    )
    print("✅ Knowledge base updated")
    
    # Enhance error handling
    adapter.enhance_error_handling(
        "network_timeout",
        "Connection timeout after 30s",
        "Retry with exponential backoff, max 3 attempts"
    )
    print("✅ Error handling enhanced")
    
    # Get summary
    summary = adapter.get_adaptation_summary()
    print(f"\n📊 Adaptation Summary:")
    print(f"  Active prioritization rules: {summary['prioritization']['active_rules']}")
    print(f"  Knowledge updates: {summary['knowledge_base']['total_updates']}")
    print(f"  Known error patterns: {summary['error_handling']['known_patterns']}")
    
    # Test priority calculation
    test_task = {
        "type": "urgent_bug_fix",
        "priority": "high",
        "urgency": 0.9,
        "importance": 0.8,
        "effort": 0.3,
        "dependencies": 0.1
    }
    priority_score = adapter.calculate_task_priority(test_task)
    print(f"\n🎯 Test task priority score: {priority_score}")
    
    print("\n✨ Real-time adapter test complete!")
