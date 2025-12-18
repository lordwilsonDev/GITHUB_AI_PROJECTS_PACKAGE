#!/usr/bin/env python3
"""
Evening Learning Report System

Generates comprehensive evening reports summarizing:
- Knowledge acquired during the day
- Patterns and insights discovered
- Optimization opportunities identified
- Experiments conducted and results
- Planned implementations for overnight

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional


class EveningLearningReport:
    """
    Generates evening learning reports.
    
    Features:
    - Daily knowledge acquisition tracking
    - Pattern and insight documentation
    - Optimization opportunity identification
    - Experiment tracking and results
    - Overnight implementation planning
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/evolution_reports"):
        """
        Initialize the evening report system.
        
        Args:
            data_dir: Directory to store report data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.reports_file = os.path.join(self.data_dir, "evening_reports.json")
        self.learnings_file = os.path.join(self.data_dir, "daily_learnings.json")
        self.insights_file = os.path.join(self.data_dir, "insights.json")
        self.experiments_file = os.path.join(self.data_dir, "experiments.json")
        self.plans_file = os.path.join(self.data_dir, "overnight_plans.json")
        
        self.reports = self._load_reports()
        self.learnings = self._load_learnings()
        self.insights = self._load_insights()
        self.experiments = self._load_experiments()
        self.plans = self._load_plans()
    
    def _load_reports(self) -> Dict[str, Any]:
        """Load reports from file."""
        if os.path.exists(self.reports_file):
            with open(self.reports_file, 'r') as f:
                return json.load(f)
        return {"reports": []}
    
    def _save_reports(self):
        """Save reports to file."""
        with open(self.reports_file, 'w') as f:
            json.dump(self.reports, f, indent=2)
    
    def _load_learnings(self) -> Dict[str, Any]:
        """Load learnings from file."""
        if os.path.exists(self.learnings_file):
            with open(self.learnings_file, 'r') as f:
                return json.load(f)
        return {"learnings": []}
    
    def _save_learnings(self):
        """Save learnings to file."""
        with open(self.learnings_file, 'w') as f:
            json.dump(self.learnings, f, indent=2)
    
    def _load_insights(self) -> Dict[str, Any]:
        """Load insights from file."""
        if os.path.exists(self.insights_file):
            with open(self.insights_file, 'r') as f:
                return json.load(f)
        return {"insights": []}
    
    def _save_insights(self):
        """Save insights to file."""
        with open(self.insights_file, 'w') as f:
            json.dump(self.insights, f, indent=2)
    
    def _load_experiments(self) -> Dict[str, Any]:
        """Load experiments from file."""
        if os.path.exists(self.experiments_file):
            with open(self.experiments_file, 'r') as f:
                return json.load(f)
        return {"experiments": []}
    
    def _save_experiments(self):
        """Save experiments to file."""
        with open(self.experiments_file, 'w') as f:
            json.dump(self.experiments, f, indent=2)
    
    def _load_plans(self) -> Dict[str, Any]:
        """Load overnight plans from file."""
        if os.path.exists(self.plans_file):
            with open(self.plans_file, 'r') as f:
                return json.load(f)
        return {"plans": []}
    
    def _save_plans(self):
        """Save plans to file."""
        with open(self.plans_file, 'w') as f:
            json.dump(self.plans, f, indent=2)
    
    def record_learning(self,
                       title: str,
                       description: str,
                       category: str,
                       source: str,
                       confidence: float = 0.8,
                       tags: List[str] = None) -> Dict[str, Any]:
        """
        Record knowledge acquired during the day.
        
        Args:
            title: Learning title
            description: Detailed description
            category: Category (technical, domain, behavioral, methodological)
            source: Source of learning
            confidence: Confidence level (0-1)
            tags: Associated tags
        
        Returns:
            Recorded learning
        """
        learning = {
            "learning_id": f"learn_{len(self.learnings['learnings']) + 1:06d}",
            "title": title,
            "description": description,
            "category": category,
            "source": source,
            "confidence": confidence,
            "tags": tags or [],
            "timestamp": datetime.now().isoformat(),
            "applied": False,
            "validation_count": 0
        }
        
        self.learnings["learnings"].append(learning)
        self._save_learnings()
        
        return learning
    
    def record_insight(self,
                      title: str,
                      description: str,
                      insight_type: str,
                      actionable: bool = True,
                      priority: str = "medium") -> Dict[str, Any]:
        """
        Record an insight discovered.
        
        Args:
            title: Insight title
            description: Detailed description
            insight_type: Type (pattern, optimization, risk, opportunity)
            actionable: Whether insight is actionable
            priority: Priority level
        
        Returns:
            Recorded insight
        """
        insight = {
            "insight_id": f"insight_{len(self.insights['insights']) + 1:06d}",
            "title": title,
            "description": description,
            "type": insight_type,
            "actionable": actionable,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "status": "new",
            "actions_taken": []
        }
        
        self.insights["insights"].append(insight)
        self._save_insights()
        
        return insight
    
    def record_experiment(self,
                         title: str,
                         hypothesis: str,
                         method: str,
                         result: str,
                         success: bool,
                         metrics: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Record an experiment conducted.
        
        Args:
            title: Experiment title
            hypothesis: Hypothesis tested
            method: Method used
            result: Result description
            success: Whether experiment succeeded
            metrics: Associated metrics
        
        Returns:
            Recorded experiment
        """
        experiment = {
            "experiment_id": f"exp_{len(self.experiments['experiments']) + 1:06d}",
            "title": title,
            "hypothesis": hypothesis,
            "method": method,
            "result": result,
            "success": success,
            "metrics": metrics or {},
            "timestamp": datetime.now().isoformat(),
            "learnings_extracted": []
        }
        
        self.experiments["experiments"].append(experiment)
        self._save_experiments()
        
        return experiment
    
    def create_overnight_plan(self,
                             title: str,
                             description: str,
                             tasks: List[Dict[str, Any]],
                             priority: str = "medium",
                             estimated_duration: int = 60) -> Dict[str, Any]:
        """
        Create plan for overnight implementation.
        
        Args:
            title: Plan title
            description: Plan description
            tasks: List of tasks to complete
            priority: Priority level
            estimated_duration: Estimated duration in minutes
        
        Returns:
            Created plan
        """
        plan = {
            "plan_id": f"plan_{len(self.plans['plans']) + 1:06d}",
            "title": title,
            "description": description,
            "tasks": tasks,
            "priority": priority,
            "estimated_duration": estimated_duration,
            "created_at": datetime.now().isoformat(),
            "status": "planned",
            "completion_percentage": 0
        }
        
        self.plans["plans"].append(plan)
        self._save_plans()
        
        return plan
    
    def generate_evening_report(self, date: str = None) -> Dict[str, Any]:
        """
        Generate evening learning report.
        
        Args:
            date: Date for report (defaults to today)
        
        Returns:
            Evening report
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Get today's learnings
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_learnings = [
            learn for learn in self.learnings["learnings"]
            if datetime.fromisoformat(learn["timestamp"]) >= today_start
        ]
        
        # Get today's insights
        today_insights = [
            insight for insight in self.insights["insights"]
            if datetime.fromisoformat(insight["timestamp"]) >= today_start
        ]
        
        # Get today's experiments
        today_experiments = [
            exp for exp in self.experiments["experiments"]
            if datetime.fromisoformat(exp["timestamp"]) >= today_start
        ]
        
        # Categorize learnings
        learnings_by_category = {}
        for learn in today_learnings:
            category = learn["category"]
            if category not in learnings_by_category:
                learnings_by_category[category] = []
            learnings_by_category[category].append(learn)
        
        # Categorize insights
        insights_by_type = {}
        actionable_insights = []
        for insight in today_insights:
            insight_type = insight["type"]
            if insight_type not in insights_by_type:
                insights_by_type[insight_type] = []
            insights_by_type[insight_type].append(insight)
            
            if insight["actionable"]:
                actionable_insights.append(insight)
        
        # Analyze experiments
        successful_experiments = [exp for exp in today_experiments if exp["success"]]
        failed_experiments = [exp for exp in today_experiments if not exp["success"]]
        
        # Get overnight plans
        pending_plans = [plan for plan in self.plans["plans"] if plan["status"] == "planned"]
        
        # Generate optimization opportunities
        optimization_opportunities = self._identify_optimization_opportunities(
            today_learnings, today_insights
        )
        
        # Create report
        report = {
            "report_id": f"evening_{date}",
            "date": date,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_learnings": len(today_learnings),
                "total_insights": len(today_insights),
                "actionable_insights": len(actionable_insights),
                "experiments_conducted": len(today_experiments),
                "successful_experiments": len(successful_experiments),
                "optimization_opportunities": len(optimization_opportunities)
            },
            "knowledge_acquired": {
                "by_category": learnings_by_category,
                "highlights": self._get_learning_highlights(today_learnings)
            },
            "insights_discovered": {
                "by_type": insights_by_type,
                "actionable": actionable_insights
            },
            "experiments": {
                "successful": successful_experiments,
                "failed": failed_experiments,
                "success_rate": (len(successful_experiments) / len(today_experiments) * 100) if today_experiments else 0
            },
            "optimization_opportunities": optimization_opportunities,
            "overnight_plans": pending_plans,
            "recommendations": self._generate_evening_recommendations()
        }
        
        self.reports["reports"].append(report)
        self._save_reports()
        
        return report
    
    def _get_learning_highlights(self, learnings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get top learning highlights.
        
        Args:
            learnings: List of learnings
        
        Returns:
            Top highlights
        """
        # Sort by confidence
        sorted_learnings = sorted(
            learnings,
            key=lambda x: x["confidence"],
            reverse=True
        )
        
        return sorted_learnings[:5]
    
    def _identify_optimization_opportunities(self,
                                            learnings: List[Dict[str, Any]],
                                            insights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identify optimization opportunities from learnings and insights.
        
        Args:
            learnings: Today's learnings
            insights: Today's insights
        
        Returns:
            List of optimization opportunities
        """
        opportunities = []
        
        # From insights
        for insight in insights:
            if insight["type"] == "optimization" and insight["actionable"]:
                opportunities.append({
                    "opportunity_id": f"opp_{len(opportunities) + 1:03d}",
                    "title": insight["title"],
                    "description": insight["description"],
                    "source": "insight",
                    "priority": insight["priority"],
                    "estimated_impact": "medium"
                })
        
        # From learnings (identify patterns)
        technical_learnings = [l for l in learnings if l["category"] == "technical"]
        if len(technical_learnings) >= 3:
            opportunities.append({
                "opportunity_id": f"opp_{len(opportunities) + 1:03d}",
                "title": "Apply technical learnings",
                "description": f"Implement {len(technical_learnings)} technical improvements learned today",
                "source": "learning_pattern",
                "priority": "high",
                "estimated_impact": "high"
            })
        
        return opportunities
    
    def _generate_evening_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate recommendations for overnight work.
        
        Returns:
            List of recommendations
        """
        return [
            {
                "recommendation_id": "rec_1",
                "title": "Implement high-priority optimizations",
                "description": "Focus on optimization opportunities identified today",
                "priority": "high",
                "category": "implementation"
            },
            {
                "recommendation_id": "rec_2",
                "title": "Validate learnings",
                "description": "Test and validate today's learnings through experiments",
                "priority": "medium",
                "category": "validation"
            },
            {
                "recommendation_id": "rec_3",
                "title": "Document insights",
                "description": "Create detailed documentation for actionable insights",
                "priority": "medium",
                "category": "documentation"
            }
        ]
    
    def format_report_text(self, report: Dict[str, Any]) -> str:
        """
        Format report as readable text.
        
        Args:
            report: Report dictionary
        
        Returns:
            Formatted text report
        """
        lines = []
        lines.append("=" * 70)
        lines.append("EVENING LEARNING REPORT")
        lines.append(f"Date: {report['date']}")
        lines.append(f"Generated: {report['generated_at']}")
        lines.append("=" * 70)
        lines.append("")
        
        # Summary
        summary = report["summary"]
        lines.append("DAILY SUMMARY")
        lines.append("-" * 70)
        lines.append(f"Knowledge Acquired: {summary['total_learnings']} learnings")
        lines.append(f"Insights Discovered: {summary['total_insights']} ({summary['actionable_insights']} actionable)")
        lines.append(f"Experiments Conducted: {summary['experiments_conducted']}")
        lines.append(f"Successful Experiments: {summary['successful_experiments']}")
        lines.append(f"Optimization Opportunities: {summary['optimization_opportunities']}")
        lines.append("")
        
        # Knowledge acquired
        lines.append("KNOWLEDGE ACQUIRED")
        lines.append("-" * 70)
        for i, learn in enumerate(report["knowledge_acquired"]["highlights"], 1):
            lines.append(f"{i}. [{learn['category'].upper()}] {learn['title']}")
            lines.append(f"   {learn['description']}")
            lines.append(f"   Confidence: {learn['confidence']*100:.0f}% | Source: {learn['source']}")
            lines.append("")
        
        # Insights discovered
        if report["insights_discovered"]["actionable"]:
            lines.append("ACTIONABLE INSIGHTS")
            lines.append("-" * 70)
            for insight in report["insights_discovered"]["actionable"]:
                lines.append(f"[{insight['priority'].upper()}] {insight['title']}")
                lines.append(f"  {insight['description']}")
                lines.append(f"  Type: {insight['type']}")
                lines.append("")
        
        # Experiments
        experiments = report["experiments"]
        if experiments["successful"] or experiments["failed"]:
            lines.append("EXPERIMENTS CONDUCTED")
            lines.append("-" * 70)
            lines.append(f"Success Rate: {experiments['success_rate']:.1f}%")
            lines.append("")
            
            if experiments["successful"]:
                lines.append("Successful:")
                for exp in experiments["successful"]:
                    lines.append(f"  ✓ {exp['title']}")
                    lines.append(f"    Hypothesis: {exp['hypothesis']}")
                    lines.append(f"    Result: {exp['result']}")
                    lines.append("")
            
            if experiments["failed"]:
                lines.append("Failed:")
                for exp in experiments["failed"]:
                    lines.append(f"  ✗ {exp['title']}")
                    lines.append(f"    Hypothesis: {exp['hypothesis']}")
                    lines.append(f"    Result: {exp['result']}")
                    lines.append("")
        
        # Optimization opportunities
        if report["optimization_opportunities"]:
            lines.append("OPTIMIZATION OPPORTUNITIES")
            lines.append("-" * 70)
            for opp in report["optimization_opportunities"]:
                lines.append(f"[{opp['priority'].upper()}] {opp['title']}")
                lines.append(f"  {opp['description']}")
                lines.append(f"  Impact: {opp['estimated_impact']} | Source: {opp['source']}")
                lines.append("")
        
        # Overnight plans
        if report["overnight_plans"]:
            lines.append("PLANNED FOR OVERNIGHT")
            lines.append("-" * 70)
            for plan in report["overnight_plans"]:
                lines.append(f"[{plan['priority'].upper()}] {plan['title']}")
                lines.append(f"  {plan['description']}")
                lines.append(f"  Tasks: {len(plan['tasks'])} | Est. Duration: {plan['estimated_duration']} min")
                lines.append("")
        
        # Recommendations
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 70)
        for rec in report["recommendations"]:
            lines.append(f"[{rec['priority'].upper()}] {rec['title']}")
            lines.append(f"  {rec['description']}")
            lines.append("")
        
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def get_latest_report(self) -> Optional[Dict[str, Any]]:
        """Get the most recent report."""
        if not self.reports["reports"]:
            return None
        return self.reports["reports"][-1]


def test_evening_learning_report():
    """Test the evening learning report system."""
    print("Testing Evening Learning Report System...")
    print("=" * 70)
    
    # Initialize system
    system = EveningLearningReport()
    
    # Test 1: Record learnings
    print("\n1. Testing learning recording...")
    learn1 = system.record_learning(
        title="Learned new optimization technique",
        description="Discovered caching strategy that reduces API calls by 60%",
        category="technical",
        source="experimentation",
        confidence=0.9,
        tags=["optimization", "caching", "api"]
    )
    print(f"   Recorded learning: {learn1['learning_id']}")
    
    learn2 = system.record_learning(
        title="User prefers concise communication",
        description="Analysis shows user responds better to brief, direct messages",
        category="behavioral",
        source="pattern_analysis",
        confidence=0.85
    )
    print(f"   Recorded learning: {learn2['learning_id']}")
    
    # Test 2: Record insights
    print("\n2. Testing insight recording...")
    insight1 = system.record_insight(
        title="Database queries can be optimized",
        description="Identified 15 slow queries that can be improved with indexing",
        insight_type="optimization",
        actionable=True,
        priority="high"
    )
    print(f"   Recorded insight: {insight1['insight_id']}")
    
    # Test 3: Record experiments
    print("\n3. Testing experiment recording...")
    exp1 = system.record_experiment(
        title="Test caching strategy",
        hypothesis="Implementing Redis cache will reduce response time by 50%",
        method="A/B testing with 100 requests",
        result="Response time reduced by 58%, hypothesis confirmed",
        success=True,
        metrics={"response_time_before": 250, "response_time_after": 105}
    )
    print(f"   Recorded experiment: {exp1['experiment_id']}")
    
    # Test 4: Create overnight plan
    print("\n4. Testing overnight plan creation...")
    plan1 = system.create_overnight_plan(
        title="Implement database optimizations",
        description="Apply indexing to identified slow queries",
        tasks=[
            {"task": "Add indexes to user table", "estimated_time": 15},
            {"task": "Optimize join queries", "estimated_time": 20},
            {"task": "Test performance improvements", "estimated_time": 10}
        ],
        priority="high",
        estimated_duration=45
    )
    print(f"   Created plan: {plan1['plan_id']}")
    
    # Test 5: Generate evening report
    print("\n5. Testing report generation...")
    report = system.generate_evening_report()
    print(f"   Generated report: {report['report_id']}")
    print(f"   Total learnings: {report['summary']['total_learnings']}")
    print(f"   Total insights: {report['summary']['total_insights']}")
    print(f"   Experiments: {report['summary']['experiments_conducted']}")
    
    # Test 6: Format report as text
    print("\n6. Testing text formatting...")
    text_report = system.format_report_text(report)
    print("   Report formatted successfully")
    print(f"   Report length: {len(text_report)} characters")
    
    # Display formatted report
    print("\n7. Displaying formatted report...")
    print("\n" + text_report)
    
    print("\n" + "=" * 70)
    print("✓ All tests completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    test_evening_learning_report()
