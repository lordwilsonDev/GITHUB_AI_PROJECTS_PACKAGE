#!/usr/bin/env python3
"""
Knowledge Gap Identifier
Identifies gaps in knowledge and learning priorities
Part of the Self-Evolving AI Ecosystem
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from collections import defaultdict

class KnowledgeGapIdentifier:
    """Identifies and prioritizes knowledge gaps"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.base_dir = Path("/Users/lordwilson/vy-nexus/self-evolving-ecosystem")
        self.data_dir = self.base_dir / "data" / "knowledge_gaps"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Knowledge tracking
        self.knowledge_base_file = self.data_dir / "knowledge_base.jsonl"
        self.gaps_file = self.data_dir / "identified_gaps.jsonl"
        self.learning_priorities_file = self.data_dir / "learning_priorities.json"
        self.failed_tasks_file = self.data_dir / "failed_tasks.jsonl"
        
        # Knowledge domains
        self.domains = [
            "technical_skills",
            "domain_expertise",
            "user_preferences",
            "workflow_optimization",
            "tool_usage",
            "problem_solving",
            "communication",
            "automation"
        ]
        
        # Gap severity levels
        self.severity_levels = {
            "critical": 5,  # Blocking current tasks
            "high": 4,      # Significantly impacting performance
            "medium": 3,    # Moderate impact
            "low": 2,       # Minor impact
            "informational": 1  # Nice to have
        }
        
        self._initialized = True
    
    def register_knowledge(
        self,
        knowledge_id: str,
        domain: str,
        topic: str,
        description: str,
        proficiency_level: int = 1,  # 1-5 scale
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Register knowledge in the knowledge base"""
        
        if domain not in self.domains:
            return {
                "success": False,
                "error": f"Invalid domain: {domain}"
            }
        
        knowledge = {
            "knowledge_id": knowledge_id,
            "domain": domain,
            "topic": topic,
            "description": description,
            "proficiency_level": proficiency_level,
            "acquired_at": datetime.now().isoformat(),
            "last_used": None,
            "usage_count": 0,
            "metadata": metadata or {}
        }
        
        # Save knowledge
        with open(self.knowledge_base_file, 'a') as f:
            f.write(json.dumps(knowledge) + '\n')
        
        return {
            "success": True,
            "knowledge_id": knowledge_id,
            "knowledge": knowledge
        }
    
    def record_failed_task(
        self,
        task_id: str,
        task_description: str,
        failure_reason: str,
        missing_knowledge: List[str],
        domain: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Record a failed task to identify knowledge gaps"""
        
        failed_task = {
            "task_id": task_id,
            "task_description": task_description,
            "failure_reason": failure_reason,
            "missing_knowledge": missing_knowledge,
            "domain": domain,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        # Save failed task
        with open(self.failed_tasks_file, 'a') as f:
            f.write(json.dumps(failed_task) + '\n')
        
        # Identify gaps from this failure
        for knowledge_topic in missing_knowledge:
            self._identify_gap_from_failure(
                domain=domain,
                topic=knowledge_topic,
                task_id=task_id,
                failure_reason=failure_reason
            )
        
        return {
            "success": True,
            "task_id": task_id,
            "gaps_identified": len(missing_knowledge)
        }
    
    def _identify_gap_from_failure(
        self,
        domain: str,
        topic: str,
        task_id: str,
        failure_reason: str
    ):
        """Identify a knowledge gap from a task failure"""
        
        gap_id = f"gap_{domain}_{topic.replace(' ', '_')}"
        
        # Check if gap already exists
        existing_gap = self._load_gap(gap_id)
        
        if existing_gap:
            # Update existing gap
            existing_gap["occurrence_count"] = existing_gap.get("occurrence_count", 1) + 1
            existing_gap["last_occurred"] = datetime.now().isoformat()
            existing_gap["related_tasks"].append(task_id)
            
            # Increase severity if recurring
            if existing_gap["occurrence_count"] > 3:
                existing_gap["severity"] = "high"
            elif existing_gap["occurrence_count"] > 5:
                existing_gap["severity"] = "critical"
            
            gap = existing_gap
        else:
            # Create new gap
            gap = {
                "gap_id": gap_id,
                "domain": domain,
                "topic": topic,
                "description": f"Missing knowledge about {topic}",
                "severity": "medium",
                "identified_at": datetime.now().isoformat(),
                "last_occurred": datetime.now().isoformat(),
                "occurrence_count": 1,
                "related_tasks": [task_id],
                "status": "open",
                "learning_resources": []
            }
        
        # Save gap
        with open(self.gaps_file, 'a') as f:
            f.write(json.dumps(gap) + '\n')
    
    def identify_gaps_from_usage_patterns(self) -> Dict[str, Any]:
        """Identify knowledge gaps from usage patterns"""
        
        gaps_identified = []
        
        # Analyze knowledge base for underutilized areas
        knowledge_by_domain = defaultdict(list)
        
        if self.knowledge_base_file.exists():
            with open(self.knowledge_base_file, 'r') as f:
                for line in f:
                    knowledge = json.loads(line.strip())
                    domain = knowledge.get("domain")
                    knowledge_by_domain[domain].append(knowledge)
        
        # Check for domains with low coverage
        for domain in self.domains:
            knowledge_items = knowledge_by_domain.get(domain, [])
            
            if len(knowledge_items) < 3:
                gap = {
                    "gap_id": f"gap_domain_{domain}",
                    "domain": domain,
                    "topic": f"General {domain} knowledge",
                    "description": f"Limited knowledge in {domain} domain",
                    "severity": "medium",
                    "identified_at": datetime.now().isoformat(),
                    "status": "open",
                    "gap_type": "domain_coverage"
                }
                gaps_identified.append(gap)
                
                with open(self.gaps_file, 'a') as f:
                    f.write(json.dumps(gap) + '\n')
        
        # Check for low proficiency areas
        for domain, items in knowledge_by_domain.items():
            low_proficiency = [k for k in items if k.get("proficiency_level", 0) < 3]
            
            if len(low_proficiency) > 0:
                for knowledge in low_proficiency:
                    gap = {
                        "gap_id": f"gap_proficiency_{knowledge['knowledge_id']}",
                        "domain": domain,
                        "topic": knowledge.get("topic"),
                        "description": f"Low proficiency in {knowledge.get('topic')}",
                        "severity": "low",
                        "identified_at": datetime.now().isoformat(),
                        "status": "open",
                        "gap_type": "low_proficiency",
                        "current_proficiency": knowledge.get("proficiency_level")
                    }
                    gaps_identified.append(gap)
                    
                    with open(self.gaps_file, 'a') as f:
                        f.write(json.dumps(gap) + '\n')
        
        return {
            "success": True,
            "gaps_identified": len(gaps_identified),
            "gaps": gaps_identified
        }
    
    def prioritize_learning(self) -> Dict[str, Any]:
        """Prioritize knowledge gaps for learning"""
        
        # Get all open gaps
        gaps = self._get_all_gaps(status="open")
        
        if not gaps:
            return {
                "success": True,
                "priorities": [],
                "message": "No open knowledge gaps"
            }
        
        # Calculate priority scores
        scored_gaps = []
        for gap in gaps:
            score = self._calculate_priority_score(gap)
            scored_gaps.append({
                "gap": gap,
                "priority_score": score
            })
        
        # Sort by priority score
        sorted_gaps = sorted(
            scored_gaps,
            key=lambda x: x["priority_score"],
            reverse=True
        )
        
        # Create learning priorities
        priorities = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        for item in sorted_gaps:
            gap = item["gap"]
            severity = gap.get("severity", "medium")
            
            priority_item = {
                "gap_id": gap["gap_id"],
                "domain": gap["domain"],
                "topic": gap["topic"],
                "priority_score": item["priority_score"],
                "severity": severity
            }
            
            if severity in priorities:
                priorities[severity].append(priority_item)
        
        # Save priorities
        priority_data = {
            "priorities": priorities,
            "generated_at": datetime.now().isoformat(),
            "total_gaps": len(gaps)
        }
        
        with open(self.learning_priorities_file, 'w') as f:
            json.dump(priority_data, f, indent=2)
        
        return {
            "success": True,
            "priorities": priorities,
            "total_gaps": len(gaps)
        }
    
    def _calculate_priority_score(self, gap: Dict) -> float:
        """Calculate priority score for a knowledge gap"""
        
        score = 0.0
        
        # Severity weight (0-50 points)
        severity = gap.get("severity", "medium")
        score += self.severity_levels.get(severity, 3) * 10
        
        # Occurrence frequency (0-30 points)
        occurrence_count = gap.get("occurrence_count", 1)
        score += min(occurrence_count * 5, 30)
        
        # Recency (0-20 points)
        last_occurred = gap.get("last_occurred")
        if last_occurred:
            days_ago = (datetime.now() - datetime.fromisoformat(last_occurred)).days
            recency_score = max(20 - days_ago, 0)
            score += recency_score
        
        # Impact on tasks (0-20 points)
        related_tasks = gap.get("related_tasks", [])
        score += min(len(related_tasks) * 4, 20)
        
        return score
    
    def suggest_learning_resources(
        self,
        gap_id: str
    ) -> Dict[str, Any]:
        """Suggest learning resources for a knowledge gap"""
        
        gap = self._load_gap(gap_id)
        if not gap:
            return {"success": False, "error": "Gap not found"}
        
        domain = gap.get("domain")
        topic = gap.get("topic")
        
        # Generate resource suggestions based on domain and topic
        resources = self._generate_resource_suggestions(domain, topic)
        
        # Update gap with resources
        gap["learning_resources"] = resources
        gap["resources_suggested_at"] = datetime.now().isoformat()
        
        with open(self.gaps_file, 'a') as f:
            f.write(json.dumps(gap) + '\n')
        
        return {
            "success": True,
            "gap_id": gap_id,
            "resources": resources
        }
    
    def _generate_resource_suggestions(
        self,
        domain: str,
        topic: str
    ) -> List[Dict[str, str]]:
        """Generate learning resource suggestions"""
        
        resources = []
        
        # Domain-specific resource suggestions
        if domain == "technical_skills":
            resources.extend([
                {
                    "type": "documentation",
                    "description": f"Official documentation for {topic}",
                    "priority": "high"
                },
                {
                    "type": "tutorial",
                    "description": f"Interactive tutorials on {topic}",
                    "priority": "medium"
                },
                {
                    "type": "practice",
                    "description": f"Hands-on practice exercises for {topic}",
                    "priority": "high"
                }
            ])
        elif domain == "domain_expertise":
            resources.extend([
                {
                    "type": "research",
                    "description": f"Research papers and articles on {topic}",
                    "priority": "medium"
                },
                {
                    "type": "case_studies",
                    "description": f"Case studies related to {topic}",
                    "priority": "high"
                }
            ])
        elif domain == "user_preferences":
            resources.extend([
                {
                    "type": "observation",
                    "description": f"Observe user behavior related to {topic}",
                    "priority": "high"
                },
                {
                    "type": "feedback",
                    "description": f"Collect user feedback on {topic}",
                    "priority": "high"
                }
            ])
        else:
            resources.append({
                "type": "general",
                "description": f"General learning resources for {topic}",
                "priority": "medium"
            })
        
        return resources
    
    def mark_gap_addressed(
        self,
        gap_id: str,
        learning_method: str,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Mark a knowledge gap as addressed"""
        
        gap = self._load_gap(gap_id)
        if not gap:
            return {"success": False, "error": "Gap not found"}
        
        gap["status"] = "addressed"
        gap["addressed_at"] = datetime.now().isoformat()
        gap["learning_method"] = learning_method
        gap["notes"] = notes
        
        with open(self.gaps_file, 'a') as f:
            f.write(json.dumps(gap) + '\n')
        
        return {
            "success": True,
            "gap_id": gap_id
        }
    
    def _load_gap(self, gap_id: str) -> Optional[Dict]:
        """Load a knowledge gap by ID"""
        
        if not self.gaps_file.exists():
            return None
        
        gaps = []
        with open(self.gaps_file, 'r') as f:
            for line in f:
                gap = json.loads(line.strip())
                if gap.get("gap_id") == gap_id:
                    gaps.append(gap)
        
        if not gaps:
            return None
        
        # Return most recent version
        return max(gaps, key=lambda x: x.get("identified_at", ""))
    
    def _get_all_gaps(self, status: Optional[str] = None) -> List[Dict]:
        """Get all knowledge gaps, optionally filtered by status"""
        
        gaps = {}
        
        if self.gaps_file.exists():
            with open(self.gaps_file, 'r') as f:
                for line in f:
                    gap = json.loads(line.strip())
                    gap_id = gap.get("gap_id")
                    
                    # Keep only latest version
                    if gap_id not in gaps or \
                       gap.get("identified_at", "") > gaps[gap_id].get("identified_at", ""):
                        gaps[gap_id] = gap
        
        all_gaps = list(gaps.values())
        
        if status:
            return [g for g in all_gaps if g.get("status") == status]
        
        return all_gaps
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge gap statistics"""
        
        stats = {
            "total_gaps": 0,
            "open_gaps": 0,
            "addressed_gaps": 0,
            "by_domain": {},
            "by_severity": {},
            "top_priority_gaps": []
        }
        
        gaps = self._get_all_gaps()
        stats["total_gaps"] = len(gaps)
        
        for gap in gaps:
            status = gap.get("status", "open")
            if status == "open":
                stats["open_gaps"] += 1
            elif status == "addressed":
                stats["addressed_gaps"] += 1
            
            domain = gap.get("domain", "unknown")
            stats["by_domain"][domain] = stats["by_domain"].get(domain, 0) + 1
            
            severity = gap.get("severity", "medium")
            stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1
        
        # Get top priority gaps
        open_gaps = [g for g in gaps if g.get("status") == "open"]
        scored_gaps = [
            {
                "gap_id": g["gap_id"],
                "topic": g["topic"],
                "domain": g["domain"],
                "severity": g.get("severity"),
                "priority_score": self._calculate_priority_score(g)
            }
            for g in open_gaps
        ]
        
        stats["top_priority_gaps"] = sorted(
            scored_gaps,
            key=lambda x: x["priority_score"],
            reverse=True
        )[:5]
        
        return stats

def get_identifier() -> KnowledgeGapIdentifier:
    """Get the singleton KnowledgeGapIdentifier instance"""
    return KnowledgeGapIdentifier()

if __name__ == "__main__":
    # Example usage
    identifier = get_identifier()
    
    # Register some knowledge
    identifier.register_knowledge(
        knowledge_id="python_basics",
        domain="technical_skills",
        topic="Python Programming",
        description="Basic Python programming skills",
        proficiency_level=3
    )
    
    # Record a failed task
    identifier.record_failed_task(
        task_id="task_001",
        task_description="Implement advanced data analysis",
        failure_reason="Lack of pandas expertise",
        missing_knowledge=["pandas", "data visualization"],
        domain="technical_skills"
    )
    
    print(f"Statistics: {json.dumps(identifier.get_statistics(), indent=2)}")
