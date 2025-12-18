#!/usr/bin/env python3
"""
AI/Automation/Productivity Insight Generator

Generates actionable insights about:
- AI capabilities and applications
- Automation opportunities
- Productivity improvements
- Workflow optimizations
- Best practices

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import random


class InsightGenerator:
    """
    Generates insights for AI, automation, and productivity.
    
    Features:
    - Pattern-based insight generation
    - Context-aware recommendations
    - Impact assessment
    - Actionable suggestions
    - Learning from outcomes
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/insights"):
        """
        Initialize the insight generator.
        
        Args:
            data_dir: Directory to store insight data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.insights_file = os.path.join(self.data_dir, "insights.json")
        self.patterns_file = os.path.join(self.data_dir, "patterns.json")
        self.templates_file = os.path.join(self.data_dir, "templates.json")
        self.outcomes_file = os.path.join(self.data_dir, "outcomes.json")
        
        self.insights = self._load_insights()
        self.patterns = self._load_patterns()
        self.templates = self._load_templates()
        self.outcomes = self._load_outcomes()
    
    def _load_insights(self) -> Dict[str, Any]:
        """Load insights from file."""
        if os.path.exists(self.insights_file):
            with open(self.insights_file, 'r') as f:
                return json.load(f)
        return {"insights": [], "metadata": {"total_generated": 0}}
    
    def _save_insights(self):
        """Save insights to file."""
        with open(self.insights_file, 'w') as f:
            json.dump(self.insights, f, indent=2)
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load learned patterns from file."""
        if os.path.exists(self.patterns_file):
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        return {
            "successful_patterns": [],
            "ineffective_patterns": [],
            "context_correlations": {}
        }
    
    def _save_patterns(self):
        """Save patterns to file."""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load insight templates."""
        if os.path.exists(self.templates_file):
            with open(self.templates_file, 'r') as f:
                return json.load(f)
        
        templates = {
            "ai_insights": [
                {
                    "template_id": "ai_001",
                    "category": "capability",
                    "pattern": "Task {task_type} can be enhanced with {ai_technique}",
                    "impact": "high",
                    "effort": "medium"
                },
                {
                    "template_id": "ai_002",
                    "category": "optimization",
                    "pattern": "AI model {model_type} shows {performance}% accuracy on {task_type}",
                    "impact": "medium",
                    "effort": "low"
                },
                {
                    "template_id": "ai_003",
                    "category": "opportunity",
                    "pattern": "Implementing {ai_feature} could reduce {metric} by {percentage}%",
                    "impact": "high",
                    "effort": "high"
                }
            ],
            "automation_insights": [
                {
                    "template_id": "auto_001",
                    "category": "efficiency",
                    "pattern": "Automating {process} could save {time_saved} hours per {period}",
                    "impact": "high",
                    "effort": "medium"
                },
                {
                    "template_id": "auto_002",
                    "category": "workflow",
                    "pattern": "Workflow {workflow_name} has {repetition_count} repetitive steps",
                    "impact": "medium",
                    "effort": "low"
                },
                {
                    "template_id": "auto_003",
                    "category": "integration",
                    "pattern": "Integrating {tool_a} with {tool_b} could eliminate {manual_steps} manual steps",
                    "impact": "high",
                    "effort": "medium"
                }
            ],
            "productivity_insights": [
                {
                    "template_id": "prod_001",
                    "category": "optimization",
                    "pattern": "Peak productivity occurs during {time_range}, optimize scheduling accordingly",
                    "impact": "medium",
                    "effort": "low"
                },
                {
                    "template_id": "prod_002",
                    "category": "bottleneck",
                    "pattern": "Process {process_name} has bottleneck at {step}, causing {delay} delay",
                    "impact": "high",
                    "effort": "medium"
                },
                {
                    "template_id": "prod_003",
                    "category": "best_practice",
                    "pattern": "Adopting {methodology} for {task_type} improves outcomes by {percentage}%",
                    "impact": "medium",
                    "effort": "low"
                }
            ]
        }
        
        with open(self.templates_file, 'w') as f:
            json.dump(templates, f, indent=2)
        
        return templates
    
    def _load_outcomes(self) -> Dict[str, Any]:
        """Load insight outcomes from file."""
        if os.path.exists(self.outcomes_file):
            with open(self.outcomes_file, 'r') as f:
                return json.load(f)
        return {"outcomes": []}
    
    def _save_outcomes(self):
        """Save outcomes to file."""
        with open(self.outcomes_file, 'w') as f:
            json.dump(self.outcomes, f, indent=2)
    
    def generate_insight(self,
                        insight_type: str,
                        context: Dict[str, Any],
                        data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate an insight based on type and context.
        
        Args:
            insight_type: Type of insight (ai, automation, productivity)
            context: Context information
            data: Supporting data
        
        Returns:
            Generated insight
        """
        # Select appropriate template
        template = self._select_template(insight_type, context)
        if not template:
            return {"error": "No suitable template found"}
        
        # Generate insight from template
        insight_text = self._fill_template(template, context, data or {})
        
        # Calculate scores
        impact_score = self._calculate_impact_score(template, context)
        confidence_score = self._calculate_confidence_score(context, data or {})
        
        insight_id = f"insight_{len(self.insights['insights']) + 1:06d}"
        
        insight = {
            "insight_id": insight_id,
            "type": insight_type,
            "category": template["category"],
            "text": insight_text,
            "impact_score": impact_score,
            "confidence_score": confidence_score,
            "effort_level": template["effort"],
            "priority": self._calculate_priority(impact_score, template["effort"]),
            "context": context,
            "supporting_data": data or {},
            "recommendations": self._generate_recommendations(template, context),
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "implemented": False,
            "outcome": None
        }
        
        self.insights["insights"].append(insight)
        self.insights["metadata"]["total_generated"] += 1
        self._save_insights()
        
        return insight
    
    def _select_template(self, insight_type: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Select best template for insight generation.
        
        Args:
            insight_type: Type of insight
            context: Context information
        
        Returns:
            Selected template or None
        """
        template_key = f"{insight_type}_insights"
        if template_key not in self.templates:
            return None
        
        templates = self.templates[template_key]
        
        # Filter by category if specified
        if "category" in context:
            matching = [t for t in templates if t["category"] == context["category"]]
            if matching:
                templates = matching
        
        # Select template (prefer high impact)
        templates.sort(key=lambda x: {"high": 3, "medium": 2, "low": 1}.get(x["impact"], 0), reverse=True)
        
        return templates[0] if templates else None
    
    def _fill_template(self, template: Dict[str, Any], context: Dict[str, Any], data: Dict[str, Any]) -> str:
        """
        Fill template with context and data.
        
        Args:
            template: Template dictionary
            context: Context information
            data: Supporting data
        
        Returns:
            Filled template text
        """
        text = template["pattern"]
        
        # Merge context and data
        variables = {**context, **data}
        
        # Replace placeholders
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in text:
                text = text.replace(placeholder, str(value))
        
        return text
    
    def _calculate_impact_score(self, template: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Calculate potential impact score.
        
        Args:
            template: Template dictionary
            context: Context information
        
        Returns:
            Impact score (0-1)
        """
        # Base score from template
        impact_map = {"high": 0.8, "medium": 0.5, "low": 0.3}
        base_score = impact_map.get(template["impact"], 0.5)
        
        # Adjust based on context
        if "urgency" in context:
            urgency_boost = {"critical": 0.2, "high": 0.1, "medium": 0, "low": -0.1}
            base_score += urgency_boost.get(context["urgency"], 0)
        
        if "scope" in context:
            scope_boost = {"organization": 0.2, "team": 0.1, "individual": 0}
            base_score += scope_boost.get(context["scope"], 0)
        
        return min(1.0, max(0.0, base_score))
    
    def _calculate_confidence_score(self, context: Dict[str, Any], data: Dict[str, Any]) -> float:
        """
        Calculate confidence in the insight.
        
        Args:
            context: Context information
            data: Supporting data
        
        Returns:
            Confidence score (0-1)
        """
        confidence = 0.5  # Base confidence
        
        # More data = higher confidence
        data_points = len(data)
        confidence += min(0.3, data_points * 0.05)
        
        # Context completeness
        context_completeness = len(context) / 5.0  # Assume 5 ideal context fields
        confidence += min(0.2, context_completeness * 0.2)
        
        return min(1.0, confidence)
    
    def _calculate_priority(self, impact_score: float, effort_level: str) -> str:
        """
        Calculate priority based on impact and effort.
        
        Args:
            impact_score: Impact score
            effort_level: Effort level
        
        Returns:
            Priority level
        """
        effort_map = {"low": 1, "medium": 2, "high": 3}
        effort_value = effort_map.get(effort_level, 2)
        
        # High impact, low effort = critical
        # High impact, high effort = high
        # Low impact, low effort = medium
        # Low impact, high effort = low
        
        if impact_score >= 0.7:
            if effort_value <= 1:
                return "critical"
            elif effort_value == 2:
                return "high"
            else:
                return "medium"
        elif impact_score >= 0.5:
            if effort_value <= 2:
                return "high"
            else:
                return "medium"
        else:
            if effort_value <= 1:
                return "medium"
            else:
                return "low"
    
    def _generate_recommendations(self, template: Dict[str, Any], context: Dict[str, Any]) -> List[str]:
        """
        Generate actionable recommendations.
        
        Args:
            template: Template dictionary
            context: Context information
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        category = template["category"]
        
        if category == "capability":
            recommendations = [
                "Evaluate current capabilities and identify gaps",
                "Research best practices and tools",
                "Create proof of concept",
                "Measure baseline metrics before implementation"
            ]
        elif category == "optimization":
            recommendations = [
                "Analyze current performance metrics",
                "Identify optimization opportunities",
                "Test optimizations in controlled environment",
                "Monitor impact and iterate"
            ]
        elif category == "efficiency":
            recommendations = [
                "Document current process",
                "Identify automation candidates",
                "Calculate ROI of automation",
                "Implement and monitor results"
            ]
        elif category == "workflow":
            recommendations = [
                "Map current workflow",
                "Identify bottlenecks and redundancies",
                "Design improved workflow",
                "Test with small pilot group"
            ]
        elif category == "bottleneck":
            recommendations = [
                "Measure bottleneck impact",
                "Identify root causes",
                "Develop mitigation strategies",
                "Implement and validate improvements"
            ]
        else:
            recommendations = [
                "Gather more information",
                "Consult with stakeholders",
                "Create implementation plan",
                "Execute and measure results"
            ]
        
        return recommendations
    
    def record_outcome(self,
                      insight_id: str,
                      implemented: bool,
                      success: bool = None,
                      impact_realized: float = None,
                      notes: str = "") -> bool:
        """
        Record outcome of an insight.
        
        Args:
            insight_id: ID of insight
            implemented: Whether insight was implemented
            success: Whether implementation was successful
            impact_realized: Actual impact realized (0-1)
            notes: Additional notes
        
        Returns:
            True if recorded successfully
        """
        insight = self._get_insight(insight_id)
        if not insight:
            return False
        
        outcome = {
            "insight_id": insight_id,
            "implemented": implemented,
            "success": success,
            "impact_realized": impact_realized,
            "impact_predicted": insight["impact_score"],
            "notes": notes,
            "recorded_at": datetime.now().isoformat()
        }
        
        insight["implemented"] = implemented
        insight["outcome"] = outcome
        insight["status"] = "completed"
        
        self.outcomes["outcomes"].append(outcome)
        self._save_insights()
        self._save_outcomes()
        
        # Learn from outcome
        if implemented and success is not None:
            self._learn_from_outcome(insight, outcome)
        
        return True
    
    def _learn_from_outcome(self, insight: Dict[str, Any], outcome: Dict[str, Any]):
        """
        Learn from insight outcome.
        
        Args:
            insight: Insight dictionary
            outcome: Outcome dictionary
        """
        pattern = {
            "type": insight["type"],
            "category": insight["category"],
            "context": insight["context"],
            "success": outcome["success"],
            "impact_accuracy": abs(outcome.get("impact_realized", 0) - outcome["impact_predicted"]) if outcome.get("impact_realized") else None
        }
        
        if outcome["success"]:
            self.patterns["successful_patterns"].append(pattern)
            # Keep only recent 50
            if len(self.patterns["successful_patterns"]) > 50:
                self.patterns["successful_patterns"] = self.patterns["successful_patterns"][-50:]
        else:
            self.patterns["ineffective_patterns"].append(pattern)
            if len(self.patterns["ineffective_patterns"]) > 50:
                self.patterns["ineffective_patterns"] = self.patterns["ineffective_patterns"][-50:]
        
        self._save_patterns()
    
    def get_top_insights(self, n: int = 10, filter_type: str = None) -> List[Dict[str, Any]]:
        """
        Get top insights by priority.
        
        Args:
            n: Number of insights to return
            filter_type: Filter by insight type
        
        Returns:
            List of top insights
        """
        insights = [i for i in self.insights["insights"] if i["status"] == "active"]
        
        if filter_type:
            insights = [i for i in insights if i["type"] == filter_type]
        
        # Sort by priority and impact
        priority_map = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        insights.sort(
            key=lambda x: (priority_map.get(x["priority"], 0), x["impact_score"]),
            reverse=True
        )
        
        return insights[:n]
    
    def generate_batch_insights(self, contexts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate multiple insights from contexts.
        
        Args:
            contexts: List of context dictionaries
        
        Returns:
            List of generated insights
        """
        insights = []
        
        for context in contexts:
            insight_type = context.get("type", "productivity")
            insight = self.generate_insight(insight_type, context)
            if "error" not in insight:
                insights.append(insight)
        
        return insights
    
    def analyze_insight_effectiveness(self) -> Dict[str, Any]:
        """
        Analyze effectiveness of generated insights.
        
        Returns:
            Effectiveness analysis
        """
        outcomes = self.outcomes["outcomes"]
        
        if not outcomes:
            return {"error": "No outcomes recorded yet"}
        
        # Calculate statistics
        total_outcomes = len(outcomes)
        implemented = len([o for o in outcomes if o["implemented"]])
        successful = len([o for o in outcomes if o.get("success")])
        
        implementation_rate = (implemented / total_outcomes * 100) if total_outcomes > 0 else 0
        success_rate = (successful / implemented * 100) if implemented > 0 else 0
        
        # Calculate impact accuracy
        impact_errors = [
            abs(o.get("impact_realized", 0) - o["impact_predicted"])
            for o in outcomes
            if o.get("impact_realized") is not None
        ]
        avg_impact_error = sum(impact_errors) / len(impact_errors) if impact_errors else 0
        impact_accuracy = max(0, (1 - avg_impact_error) * 100)
        
        # Analyze by type
        type_stats = defaultdict(lambda: {"total": 0, "implemented": 0, "successful": 0})
        for outcome in outcomes:
            insight = self._get_insight(outcome["insight_id"])
            if insight:
                insight_type = insight["type"]
                type_stats[insight_type]["total"] += 1
                if outcome["implemented"]:
                    type_stats[insight_type]["implemented"] += 1
                if outcome.get("success"):
                    type_stats[insight_type]["successful"] += 1
        
        return {
            "total_insights_generated": self.insights["metadata"]["total_generated"],
            "total_outcomes_recorded": total_outcomes,
            "implementation_rate": round(implementation_rate, 2),
            "success_rate": round(success_rate, 2),
            "impact_accuracy": round(impact_accuracy, 2),
            "type_breakdown": dict(type_stats)
        }
    
    def _get_insight(self, insight_id: str) -> Optional[Dict[str, Any]]:
        """Get insight by ID."""
        for insight in self.insights["insights"]:
            if insight["insight_id"] == insight_id:
                return insight
        return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get insight generation statistics.
        
        Returns:
            Statistics dictionary
        """
        insights = self.insights["insights"]
        
        # Count by type
        type_counts = defaultdict(int)
        for insight in insights:
            type_counts[insight["type"]] += 1
        
        # Count by priority
        priority_counts = defaultdict(int)
        for insight in insights:
            priority_counts[insight["priority"]] += 1
        
        # Calculate average scores
        if insights:
            avg_impact = sum(i["impact_score"] for i in insights) / len(insights)
            avg_confidence = sum(i["confidence_score"] for i in insights) / len(insights)
        else:
            avg_impact = 0
            avg_confidence = 0
        
        return {
            "total_insights": len(insights),
            "active_insights": len([i for i in insights if i["status"] == "active"]),
            "implemented_insights": len([i for i in insights if i["implemented"]]),
            "type_distribution": dict(type_counts),
            "priority_distribution": dict(priority_counts),
            "average_impact_score": round(avg_impact, 3),
            "average_confidence_score": round(avg_confidence, 3),
            "total_outcomes": len(self.outcomes["outcomes"])
        }


def test_insight_generator():
    """Test the insight generator."""
    print("Testing AI/Automation/Productivity Insight Generator...")
    print("=" * 60)
    
    generator = InsightGenerator()
    
    # Test 1: Generate AI insight
    print("\n1. Generating AI insight...")
    ai_insight = generator.generate_insight(
        insight_type="ai",
        context={
            "category": "capability",
            "task_type": "data analysis",
            "ai_technique": "machine learning",
            "urgency": "high"
        }
    )
    print(f"   Generated: {ai_insight['text']}")
    print(f"   Impact: {ai_insight['impact_score']:.2f}, Priority: {ai_insight['priority']}")
    
    # Test 2: Generate automation insight
    print("\n2. Generating automation insight...")
    auto_insight = generator.generate_insight(
        insight_type="automation",
        context={
            "category": "efficiency",
            "process": "data entry",
            "time_saved": "10",
            "period": "week"
        },
        data={"current_time": 15, "estimated_time": 5}
    )
    print(f"   Generated: {auto_insight['text']}")
    print(f"   Confidence: {auto_insight['confidence_score']:.2f}")
    
    # Test 3: Generate productivity insight
    print("\n3. Generating productivity insight...")
    prod_insight = generator.generate_insight(
        insight_type="productivity",
        context={
            "category": "optimization",
            "time_range": "9-11 AM"
        }
    )
    print(f"   Generated: {prod_insight['text']}")
    print(f"   Recommendations: {len(prod_insight['recommendations'])}")
    
    # Test 4: Record outcome
    print("\n4. Recording outcome...")
    recorded = generator.record_outcome(
        insight_id=ai_insight["insight_id"],
        implemented=True,
        success=True,
        impact_realized=0.75,
        notes="Successfully implemented"
    )
    print(f"   Outcome recorded: {recorded}")
    
    # Test 5: Get top insights
    print("\n5. Getting top insights...")
    top_insights = generator.get_top_insights(n=5)
    print(f"   Found {len(top_insights)} top insights")
    for i, insight in enumerate(top_insights[:3], 1):
        print(f"      {i}. [{insight['priority']}] {insight['text'][:50]}...")
    
    # Test 6: Analyze effectiveness
    print("\n6. Analyzing effectiveness...")
    effectiveness = generator.analyze_insight_effectiveness()
    if "error" not in effectiveness:
        print(f"   Implementation rate: {effectiveness['implementation_rate']:.1f}%")
        print(f"   Success rate: {effectiveness['success_rate']:.1f}%")
    
    # Test 7: Get statistics
    print("\n7. Getting statistics...")
    stats = generator.get_statistics()
    print(f"   Total insights: {stats['total_insights']}")
    print(f"   Active insights: {stats['active_insights']}")
    print(f"   Average impact: {stats['average_impact_score']:.3f}")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_insight_generator()
