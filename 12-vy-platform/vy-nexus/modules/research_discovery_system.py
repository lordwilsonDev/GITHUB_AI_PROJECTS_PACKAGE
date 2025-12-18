#!/usr/bin/env python3
"""
Research and Methodology Discovery System
Automatically discovers new tools, techniques, and methodologies
Learns from research and applies findings

Part of Phase 2: Continuous Learning Engine
Created: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from collections import defaultdict, Counter
import hashlib
import re


class ResearchDiscoverySystem:
    """
    Discovers and learns from new research, tools, and methodologies.
    Continuously expands knowledge base with validated findings.
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.path.expanduser("~/vy-nexus"))
        self.data_path = self.base_path / "data" / "research"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Research storage
        self.discoveries_file = self.data_path / "discoveries.jsonl"
        self.methodologies_file = self.data_path / "methodologies.json"
        self.tools_file = self.data_path / "tools_database.json"
        self.techniques_file = self.data_path / "techniques.json"
        self.research_queue_file = self.data_path / "research_queue.json"
        
        # Load existing data
        self.methodologies = self._load_json(self.methodologies_file, [])
        self.tools_database = self._load_json(self.tools_file, {})
        self.techniques = self._load_json(self.techniques_file, [])
        self.research_queue = self._load_json(self.research_queue_file, [])
        
        # Research categories
        self.categories = [
            "programming_languages",
            "frameworks_libraries",
            "algorithms",
            "design_patterns",
            "best_practices",
            "optimization_techniques",
            "testing_methodologies",
            "deployment_strategies",
            "ai_ml_techniques",
            "productivity_tools"
        ]
        
        print("✅ Research Discovery System initialized")
    
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
    
    def record_discovery(self, discovery_type: str, title: str,
                        description: str, source: str = "unknown",
                        category: str = None, tags: List[str] = None,
                        confidence: float = 0.7) -> Dict[str, Any]:
        """
        Record a new discovery.
        
        Args:
            discovery_type: Type (tool, technique, methodology, best_practice)
            title: Discovery title
            description: Detailed description
            source: Source of discovery
            category: Category classification
            tags: Associated tags
            confidence: Confidence in discovery validity (0-1)
        
        Returns:
            Discovery record
        """
        discovery = {
            "discovery_id": self._generate_discovery_id(title),
            "type": discovery_type,
            "title": title,
            "description": description,
            "source": source,
            "category": category,
            "tags": tags or [],
            "confidence": confidence,
            "discovered_at": datetime.utcnow().isoformat(),
            "validation_status": "pending",
            "applied_count": 0,
            "success_rate": None,
            "metadata": {
                "last_updated": datetime.utcnow().isoformat()
            }
        }
        
        # Persist discovery
        with open(self.discoveries_file, 'a') as f:
            f.write(json.dumps(discovery) + "\n")
        
        # Add to appropriate collection
        if discovery_type == "methodology":
            self.methodologies.append(discovery)
            self._save_json(self.methodologies_file, self.methodologies)
        elif discovery_type == "tool":
            tool_key = discovery["discovery_id"]
            self.tools_database[tool_key] = discovery
            self._save_json(self.tools_file, self.tools_database)
        elif discovery_type == "technique":
            self.techniques.append(discovery)
            self._save_json(self.techniques_file, self.techniques)
        
        print(f"✅ Recorded discovery: {title}")
        
        return discovery
    
    def _generate_discovery_id(self, title: str) -> str:
        """Generate unique discovery ID"""
        content = f"{title}:{datetime.utcnow().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def validate_discovery(self, discovery_id: str, validation_result: Dict[str, Any]) -> bool:
        """
        Validate a discovery through testing or application.
        
        Args:
            discovery_id: Discovery identifier
            validation_result: Validation results
        
        Returns:
            Success status
        """
        success = validation_result.get("success", False)
        notes = validation_result.get("notes", "")
        
        # Update discovery in all collections
        updated = False
        
        # Update in methodologies
        for methodology in self.methodologies:
            if methodology["discovery_id"] == discovery_id:
                methodology["validation_status"] = "validated" if success else "failed"
                methodology["applied_count"] += 1
                methodology["metadata"]["validation_notes"] = notes
                methodology["metadata"]["last_validated"] = datetime.utcnow().isoformat()
                updated = True
        
        if updated:
            self._save_json(self.methodologies_file, self.methodologies)
        
        # Update in tools
        if discovery_id in self.tools_database:
            self.tools_database[discovery_id]["validation_status"] = "validated" if success else "failed"
            self.tools_database[discovery_id]["applied_count"] += 1
            self._save_json(self.tools_file, self.tools_database)
            updated = True
        
        # Update in techniques
        for technique in self.techniques:
            if technique["discovery_id"] == discovery_id:
                technique["validation_status"] = "validated" if success else "failed"
                technique["applied_count"] += 1
                updated = True
        
        if updated:
            self._save_json(self.techniques_file, self.techniques)
        
        if updated:
            print(f"✅ Discovery validated: {discovery_id} - {'Success' if success else 'Failed'}")
        else:
            print(f"⚠️ Discovery not found: {discovery_id}")
        
        return updated
    
    def add_to_research_queue(self, topic: str, priority: str = "medium",
                             reason: str = None, related_to: str = None) -> Dict[str, Any]:
        """
        Add a topic to the research queue.
        
        Args:
            topic: Research topic
            priority: Priority level (low, medium, high, critical)
            reason: Reason for research
            related_to: Related discovery or task
        
        Returns:
            Queue entry
        """
        entry = {
            "queue_id": hashlib.sha256(
                f"{topic}:{datetime.utcnow().isoformat()}".encode()
            ).hexdigest()[:16],
            "topic": topic,
            "priority": priority,
            "reason": reason,
            "related_to": related_to,
            "status": "queued",
            "added_at": datetime.utcnow().isoformat(),
            "started_at": None,
            "completed_at": None
        }
        
        self.research_queue.append(entry)
        self._save_json(self.research_queue_file, self.research_queue)
        
        print(f"📚 Added to research queue: {topic} (priority: {priority})")
        
        return entry
    
    def get_research_recommendations(self, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Get research recommendations based on current context.
        
        Args:
            context: Current context (task types, challenges, etc.)
        
        Returns:
            List of research recommendations
        """
        recommendations = []
        
        # Analyze recent failures to suggest research
        if context and "recent_failures" in context:
            for failure in context["recent_failures"]:
                error_type = failure.get("error_type", "")
                recommendations.append({
                    "priority": "high",
                    "topic": f"Solutions for {error_type} errors",
                    "reason": f"Recurring failure pattern detected",
                    "category": "problem_solving"
                })
        
        # Suggest research for frequently used but unoptimized tasks
        if context and "frequent_tasks" in context:
            for task in context["frequent_tasks"][:3]:
                recommendations.append({
                    "priority": "medium",
                    "topic": f"Optimization techniques for {task['task_type']}",
                    "reason": f"Task performed {task['count']} times",
                    "category": "optimization"
                })
        
        # Suggest emerging technology research
        recommendations.append({
            "priority": "low",
            "topic": "Latest AI/ML frameworks and tools",
            "reason": "Stay current with technology trends",
            "category": "technology_trends"
        })
        
        return recommendations
    
    def discover_from_interaction(self, interaction: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Automatically discover insights from user interactions.
        
        Args:
            interaction: Interaction record
        
        Returns:
            Discovery if any
        """
        interaction_type = interaction.get("type", "")
        data = interaction.get("data", {})
        
        discovery = None
        
        # Discover from user queries
        if interaction_type == "query":
            query_text = data.get("query_text", "").lower()
            
            # Check for tool/library mentions
            tool_patterns = [
                r"using (\w+)",
                r"with (\w+)",
                r"(\w+) library",
                r"(\w+) framework"
            ]
            
            for pattern in tool_patterns:
                matches = re.findall(pattern, query_text)
                for match in matches:
                    if len(match) > 3:  # Filter out short words
                        discovery = self.record_discovery(
                            "tool",
                            match.capitalize(),
                            f"Tool mentioned in user query: {query_text[:100]}",
                            source="user_interaction",
                            confidence=0.5
                        )
                        break
        
        # Discover from successful task completions
        elif interaction_type == "task_completion" and data.get("success"):
            task_type = data.get("task_type", "")
            if data.get("result_quality", 0) > 0.9:
                discovery = self.record_discovery(
                    "best_practice",
                    f"High-quality {task_type} approach",
                    f"Achieved {data.get('result_quality', 0):.1%} quality",
                    source="successful_execution",
                    category=task_type,
                    confidence=0.8
                )
        
        return discovery
    
    def search_discoveries(self, query: str = None, discovery_type: str = None,
                          category: str = None, min_confidence: float = 0.0,
                          validated_only: bool = False) -> List[Dict[str, Any]]:
        """
        Search through discoveries.
        
        Args:
            query: Search query
            discovery_type: Filter by type
            category: Filter by category
            min_confidence: Minimum confidence threshold
            validated_only: Only return validated discoveries
        
        Returns:
            List of matching discoveries
        """
        results = []
        
        if not self.discoveries_file.exists():
            return results
        
        with open(self.discoveries_file, 'r') as f:
            for line in f:
                try:
                    discovery = json.loads(line.strip())
                    
                    # Apply filters
                    if discovery_type and discovery.get("type") != discovery_type:
                        continue
                    
                    if category and discovery.get("category") != category:
                        continue
                    
                    if discovery.get("confidence", 0) < min_confidence:
                        continue
                    
                    if validated_only and discovery.get("validation_status") != "validated":
                        continue
                    
                    if query:
                        query_lower = query.lower()
                        title_match = query_lower in discovery.get("title", "").lower()
                        desc_match = query_lower in discovery.get("description", "").lower()
                        tag_match = any(query_lower in tag.lower() for tag in discovery.get("tags", []))
                        
                        if not (title_match or desc_match or tag_match):
                            continue
                    
                    results.append(discovery)
                    
                except:
                    continue
        
        return results
    
    def get_methodology_recommendations(self, task_type: str) -> List[Dict[str, Any]]:
        """
        Get methodology recommendations for a specific task type.
        
        Args:
            task_type: Type of task
        
        Returns:
            List of recommended methodologies
        """
        recommendations = []
        
        # Search for validated methodologies
        relevant = self.search_discoveries(
            query=task_type,
            discovery_type="methodology",
            validated_only=True,
            min_confidence=0.7
        )
        
        # Sort by success rate and applied count
        for methodology in relevant:
            score = (
                methodology.get("confidence", 0) * 0.4 +
                (methodology.get("success_rate", 0) or 0) * 0.4 +
                min(methodology.get("applied_count", 0) / 10, 1.0) * 0.2
            )
            
            recommendations.append({
                "methodology": methodology,
                "recommendation_score": round(score, 2),
                "reason": f"Validated methodology with {methodology.get('applied_count', 0)} applications"
            })
        
        # Sort by score
        recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)
        
        return recommendations[:5]
    
    def generate_research_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive research report.
        
        Returns:
            Research report
        """
        print("\n📊 Generating research report...")
        
        # Count discoveries by type
        type_counts = Counter()
        category_counts = Counter()
        validated_count = 0
        total_discoveries = 0
        
        if self.discoveries_file.exists():
            with open(self.discoveries_file, 'r') as f:
                for line in f:
                    try:
                        discovery = json.loads(line.strip())
                        total_discoveries += 1
                        type_counts[discovery.get("type", "unknown")] += 1
                        if discovery.get("category"):
                            category_counts[discovery.get("category")] += 1
                        if discovery.get("validation_status") == "validated":
                            validated_count += 1
                    except:
                        continue
        
        # Research queue statistics
        queue_stats = {
            "total": len(self.research_queue),
            "queued": len([q for q in self.research_queue if q["status"] == "queued"]),
            "in_progress": len([q for q in self.research_queue if q["status"] == "in_progress"]),
            "completed": len([q for q in self.research_queue if q["status"] == "completed"])
        }
        
        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_discoveries": total_discoveries,
            "validated_discoveries": validated_count,
            "validation_rate": round(validated_count / total_discoveries * 100, 2) if total_discoveries > 0 else 0,
            "discoveries_by_type": dict(type_counts),
            "discoveries_by_category": dict(category_counts.most_common(10)),
            "research_queue_stats": queue_stats,
            "top_methodologies": self.methodologies[:5],
            "tools_count": len(self.tools_database),
            "techniques_count": len(self.techniques)
        }
        
        # Save report
        report_path = self.data_path / f"research_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        self._save_json(report_path, report)
        
        print(f"✅ Report saved: {report_path}")
        
        return report
    
    def get_discovery_insights(self) -> List[str]:
        """
        Generate insights from discoveries.
        
        Returns:
            List of insight strings
        """
        insights = []
        
        # Most validated type
        type_validation = defaultdict(lambda: {"total": 0, "validated": 0})
        
        if self.discoveries_file.exists():
            with open(self.discoveries_file, 'r') as f:
                for line in f:
                    try:
                        discovery = json.loads(line.strip())
                        dtype = discovery.get("type", "unknown")
                        type_validation[dtype]["total"] += 1
                        if discovery.get("validation_status") == "validated":
                            type_validation[dtype]["validated"] += 1
                    except:
                        continue
        
        # Generate insights
        for dtype, stats in type_validation.items():
            if stats["total"] >= 3:
                rate = stats["validated"] / stats["total"] * 100
                insights.append(
                    f"{dtype.capitalize()} discoveries have {rate:.0f}% validation rate "
                    f"({stats['validated']}/{stats['total']})"
                )
        
        # Research queue insights
        if len(self.research_queue) > 5:
            insights.append(
                f"Research queue has {len(self.research_queue)} items - "
                f"consider prioritizing high-priority research"
            )
        
        # Tool database insights
        if len(self.tools_database) > 10:
            insights.append(
                f"Tool database contains {len(self.tools_database)} tools - "
                f"rich resource for task execution"
            )
        
        return insights


if __name__ == "__main__":
    print("🔬 Research Discovery System - Test Mode")
    print("="*60)
    
    system = ResearchDiscoverySystem()
    
    # Record discoveries
    print("\n📝 Recording discoveries...")
    
    system.record_discovery(
        "methodology",
        "Test-Driven Development",
        "Write tests before implementation to ensure code quality",
        source="best_practices_research",
        category="testing_methodologies",
        tags=["testing", "quality", "development"],
        confidence=0.9
    )
    
    system.record_discovery(
        "tool",
        "pytest",
        "Python testing framework with powerful features",
        source="tool_research",
        category="testing",
        tags=["python", "testing"],
        confidence=0.95
    )
    
    system.record_discovery(
        "technique",
        "Caching Strategy",
        "Cache frequently accessed data to improve performance",
        source="optimization_research",
        category="optimization_techniques",
        tags=["performance", "caching"],
        confidence=0.85
    )
    
    print("✅ Discoveries recorded")
    
    # Add to research queue
    print("\n📚 Adding to research queue...")
    system.add_to_research_queue(
        "Advanced Python async patterns",
        priority="high",
        reason="Improve concurrent task handling"
    )
    
    system.add_to_research_queue(
        "Machine learning model optimization",
        priority="medium",
        reason="Enhance AI capabilities"
    )
    
    print("✅ Research items queued")
    
    # Search discoveries
    print("\n🔍 Searching discoveries...")
    results = system.search_discoveries(query="testing", min_confidence=0.7)
    print(f"  Found {len(results)} discoveries matching 'testing'")
    
    # Get recommendations
    print("\n💡 Getting research recommendations...")
    context = {
        "recent_failures": [{"error_type": "timeout"}],
        "frequent_tasks": [{"task_type": "data_processing", "count": 15}]
    }
    recommendations = system.get_research_recommendations(context)
    print(f"  Generated {len(recommendations)} recommendations")
    for rec in recommendations[:3]:
        print(f"    [{rec['priority']}] {rec['topic']}")
    
    # Generate report
    print("\n📊 Generating research report...")
    report = system.generate_research_report()
    print(f"  Total discoveries: {report['total_discoveries']}")
    print(f"  Validation rate: {report['validation_rate']}%")
    print(f"  Tools in database: {report['tools_count']}")
    
    # Get insights
    print("\n💡 Discovery Insights:")
    insights = system.get_discovery_insights()
    for insight in insights:
        print(f"  - {insight}")
    
    print("\n✨ Research discovery system test complete!")
