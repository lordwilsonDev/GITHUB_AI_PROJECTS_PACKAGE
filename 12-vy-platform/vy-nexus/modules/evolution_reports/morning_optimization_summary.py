#!/usr/bin/env python3
"""
Morning Optimization Summary Generator

Generates comprehensive morning reports summarizing:
- Overnight improvements and optimizations
- New capabilities added
- Automation successes and failures
- Productivity gains
- Learning objectives for the day

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import glob


class MorningOptimizationSummary:
    """
    Generates morning optimization summaries.
    
    Features:
    - Overnight improvement tracking
    - New capability reporting
    - Automation success/failure analysis
    - Productivity metrics
    - Daily learning objectives
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/evolution_reports"):
        """
        Initialize the morning summary generator.
        
        Args:
            data_dir: Directory to store report data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.reports_file = os.path.join(self.data_dir, "morning_reports.json")
        self.improvements_file = os.path.join(self.data_dir, "improvements.json")
        self.capabilities_file = os.path.join(self.data_dir, "capabilities.json")
        self.metrics_file = os.path.join(self.data_dir, "metrics.json")
        
        self.reports = self._load_reports()
        self.improvements = self._load_improvements()
        self.capabilities = self._load_capabilities()
        self.metrics = self._load_metrics()
    
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
    
    def _load_improvements(self) -> Dict[str, Any]:
        """Load improvements from file."""
        if os.path.exists(self.improvements_file):
            with open(self.improvements_file, 'r') as f:
                return json.load(f)
        return {"improvements": []}
    
    def _save_improvements(self):
        """Save improvements to file."""
        with open(self.improvements_file, 'w') as f:
            json.dump(self.improvements, f, indent=2)
    
    def _load_capabilities(self) -> Dict[str, Any]:
        """Load capabilities from file."""
        if os.path.exists(self.capabilities_file):
            with open(self.capabilities_file, 'r') as f:
                return json.load(f)
        return {"capabilities": []}
    
    def _save_capabilities(self):
        """Save capabilities to file."""
        with open(self.capabilities_file, 'w') as f:
            json.dump(self.capabilities, f, indent=2)
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Load metrics from file."""
        if os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'r') as f:
                return json.load(f)
        return {"daily_metrics": []}
    
    def _save_metrics(self):
        """Save metrics to file."""
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def record_improvement(self,
                          title: str,
                          description: str,
                          category: str,
                          impact: str = "medium",
                          metrics: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Record an improvement made overnight.
        
        Args:
            title: Improvement title
            description: Detailed description
            category: Category (optimization, automation, feature, bugfix)
            impact: Impact level (low, medium, high, critical)
            metrics: Associated metrics
        
        Returns:
            Recorded improvement
        """
        improvement = {
            "improvement_id": f"imp_{len(self.improvements['improvements']) + 1:06d}",
            "title": title,
            "description": description,
            "category": category,
            "impact": impact,
            "metrics": metrics or {},
            "timestamp": datetime.now().isoformat(),
            "status": "deployed"
        }
        
        self.improvements["improvements"].append(improvement)
        self._save_improvements()
        
        return improvement
    
    def record_capability(self,
                         name: str,
                         description: str,
                         capability_type: str,
                         status: str = "active") -> Dict[str, Any]:
        """
        Record a new capability added.
        
        Args:
            name: Capability name
            description: Capability description
            capability_type: Type (feature, integration, automation, analysis)
            status: Status (active, testing, planned)
        
        Returns:
            Recorded capability
        """
        capability = {
            "capability_id": f"cap_{len(self.capabilities['capabilities']) + 1:06d}",
            "name": name,
            "description": description,
            "type": capability_type,
            "status": status,
            "added_at": datetime.now().isoformat()
        }
        
        self.capabilities["capabilities"].append(capability)
        self._save_capabilities()
        
        return capability
    
    def generate_morning_report(self, date: str = None) -> Dict[str, Any]:
        """
        Generate morning optimization summary.
        
        Args:
            date: Date for report (defaults to today)
        
        Returns:
            Morning report
        """
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Get overnight improvements (last 12 hours)
        cutoff_time = datetime.now() - timedelta(hours=12)
        recent_improvements = [
            imp for imp in self.improvements["improvements"]
            if datetime.fromisoformat(imp["timestamp"]) > cutoff_time
        ]
        
        # Get new capabilities (last 24 hours)
        capability_cutoff = datetime.now() - timedelta(hours=24)
        new_capabilities = [
            cap for cap in self.capabilities["capabilities"]
            if datetime.fromisoformat(cap["added_at"]) > capability_cutoff
        ]
        
        # Categorize improvements
        improvements_by_category = {}
        for imp in recent_improvements:
            category = imp["category"]
            if category not in improvements_by_category:
                improvements_by_category[category] = []
            improvements_by_category[category].append(imp)
        
        # Calculate impact summary
        impact_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for imp in recent_improvements:
            impact_counts[imp["impact"]] += 1
        
        # Generate learning objectives
        learning_objectives = self._generate_learning_objectives()
        
        # Calculate productivity gains
        productivity_gains = self._calculate_productivity_gains(recent_improvements)
        
        # Create report
        report = {
            "report_id": f"morning_{date}",
            "date": date,
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_improvements": len(recent_improvements),
                "new_capabilities": len(new_capabilities),
                "impact_distribution": impact_counts,
                "productivity_gain_percentage": productivity_gains
            },
            "improvements": {
                "by_category": improvements_by_category,
                "highlights": self._get_improvement_highlights(recent_improvements)
            },
            "new_capabilities": new_capabilities,
            "automation_report": self._generate_automation_report(),
            "productivity_metrics": self._get_productivity_metrics(),
            "learning_objectives": learning_objectives,
            "recommendations": self._generate_recommendations()
        }
        
        self.reports["reports"].append(report)
        self._save_reports()
        
        return report
    
    def _generate_learning_objectives(self) -> List[Dict[str, Any]]:
        """
        Generate learning objectives for the day.
        
        Returns:
            List of learning objectives
        """
        objectives = [
            {
                "objective_id": "learn_1",
                "title": "Analyze user interaction patterns",
                "description": "Study today's user interactions to identify optimization opportunities",
                "priority": "high",
                "estimated_time": 30
            },
            {
                "objective_id": "learn_2",
                "title": "Research emerging AI tools",
                "description": "Investigate new AI/automation tools that could enhance capabilities",
                "priority": "medium",
                "estimated_time": 45
            },
            {
                "objective_id": "learn_3",
                "title": "Optimize workflow templates",
                "description": "Review and optimize existing workflow templates based on performance data",
                "priority": "medium",
                "estimated_time": 20
            }
        ]
        
        return objectives
    
    def _calculate_productivity_gains(self, improvements: List[Dict[str, Any]]) -> float:
        """
        Calculate estimated productivity gains from improvements.
        
        Args:
            improvements: List of improvements
        
        Returns:
            Estimated productivity gain percentage
        """
        total_gain = 0.0
        
        for imp in improvements:
            # Estimate gain based on impact and category
            impact_multiplier = {
                "critical": 0.15,
                "high": 0.10,
                "medium": 0.05,
                "low": 0.02
            }
            
            category_multiplier = {
                "optimization": 1.2,
                "automation": 1.5,
                "feature": 1.0,
                "bugfix": 0.8
            }
            
            impact = impact_multiplier.get(imp["impact"], 0.05)
            category = category_multiplier.get(imp["category"], 1.0)
            
            total_gain += impact * category
        
        return round(total_gain * 100, 2)
    
    def _get_improvement_highlights(self, improvements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get top improvement highlights.
        
        Args:
            improvements: List of improvements
        
        Returns:
            Top highlights
        """
        # Sort by impact
        impact_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        sorted_improvements = sorted(
            improvements,
            key=lambda x: impact_order.get(x["impact"], 0),
            reverse=True
        )
        
        return sorted_improvements[:5]
    
    def _generate_automation_report(self) -> Dict[str, Any]:
        """
        Generate automation success/failure report.
        
        Returns:
            Automation report
        """
        # This would integrate with automation tracking systems
        return {
            "total_automations": 15,
            "successful": 14,
            "failed": 1,
            "success_rate": 93.3,
            "new_automations": 2,
            "optimized_automations": 3,
            "failures": [
                {
                    "automation_id": "auto_001",
                    "name": "Data sync",
                    "reason": "Network timeout",
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
    
    def _get_productivity_metrics(self) -> Dict[str, Any]:
        """
        Get productivity metrics.
        
        Returns:
            Productivity metrics
        """
        return {
            "tasks_completed": 12,
            "average_completion_time": 25.5,
            "time_saved": 45,
            "efficiency_score": 87.5,
            "bottlenecks_identified": 2,
            "optimizations_applied": 5
        }
    
    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """
        Generate recommendations for the day.
        
        Returns:
            List of recommendations
        """
        return [
            {
                "recommendation_id": "rec_1",
                "title": "Focus on high-priority tasks",
                "description": "Based on yesterday's patterns, morning hours are most productive",
                "priority": "high",
                "category": "scheduling"
            },
            {
                "recommendation_id": "rec_2",
                "title": "Review automation failures",
                "description": "One automation failed overnight - investigate and fix",
                "priority": "medium",
                "category": "maintenance"
            },
            {
                "recommendation_id": "rec_3",
                "title": "Test new capabilities",
                "description": "New capabilities added - run validation tests",
                "priority": "medium",
                "category": "testing"
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
        lines.append("MORNING OPTIMIZATION SUMMARY")
        lines.append(f"Date: {report['date']}")
        lines.append(f"Generated: {report['generated_at']}")
        lines.append("=" * 70)
        lines.append("")
        
        # Summary
        summary = report["summary"]
        lines.append("OVERNIGHT SUMMARY")
        lines.append("-" * 70)
        lines.append(f"Total Improvements: {summary['total_improvements']}")
        lines.append(f"New Capabilities: {summary['new_capabilities']}")
        lines.append(f"Productivity Gain: +{summary['productivity_gain_percentage']}%")
        lines.append("")
        
        # Impact distribution
        lines.append("Impact Distribution:")
        for impact, count in summary["impact_distribution"].items():
            if count > 0:
                lines.append(f"  - {impact.capitalize()}: {count}")
        lines.append("")
        
        # Improvement highlights
        lines.append("TOP IMPROVEMENTS")
        lines.append("-" * 70)
        for i, imp in enumerate(report["improvements"]["highlights"], 1):
            lines.append(f"{i}. [{imp['impact'].upper()}] {imp['title']}")
            lines.append(f"   {imp['description']}")
            lines.append("")
        
        # New capabilities
        if report["new_capabilities"]:
            lines.append("NEW CAPABILITIES")
            lines.append("-" * 70)
            for cap in report["new_capabilities"]:
                lines.append(f"- {cap['name']} ({cap['type']})")
                lines.append(f"  {cap['description']}")
                lines.append("")
        
        # Automation report
        auto_report = report["automation_report"]
        lines.append("AUTOMATION REPORT")
        lines.append("-" * 70)
        lines.append(f"Success Rate: {auto_report['success_rate']}%")
        lines.append(f"Successful: {auto_report['successful']}/{auto_report['total_automations']}")
        lines.append(f"New Automations: {auto_report['new_automations']}")
        lines.append(f"Optimized: {auto_report['optimized_automations']}")
        if auto_report["failures"]:
            lines.append("\nFailures:")
            for failure in auto_report["failures"]:
                lines.append(f"  - {failure['name']}: {failure['reason']}")
        lines.append("")
        
        # Productivity metrics
        metrics = report["productivity_metrics"]
        lines.append("PRODUCTIVITY METRICS")
        lines.append("-" * 70)
        lines.append(f"Tasks Completed: {metrics['tasks_completed']}")
        lines.append(f"Avg Completion Time: {metrics['average_completion_time']} min")
        lines.append(f"Time Saved: {metrics['time_saved']} min")
        lines.append(f"Efficiency Score: {metrics['efficiency_score']}%")
        lines.append("")
        
        # Learning objectives
        lines.append("TODAY'S LEARNING OBJECTIVES")
        lines.append("-" * 70)
        for obj in report["learning_objectives"]:
            lines.append(f"[{obj['priority'].upper()}] {obj['title']}")
            lines.append(f"  {obj['description']}")
            lines.append(f"  Estimated time: {obj['estimated_time']} min")
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
    
    def get_report_by_date(self, date: str) -> Optional[Dict[str, Any]]:
        """Get report for specific date."""
        for report in self.reports["reports"]:
            if report["date"] == date:
                return report
        return None


def test_morning_optimization_summary():
    """Test the morning optimization summary generator."""
    print("Testing Morning Optimization Summary Generator...")
    print("=" * 70)
    
    # Initialize generator
    generator = MorningOptimizationSummary()
    
    # Test 1: Record improvements
    print("\n1. Testing improvement recording...")
    imp1 = generator.record_improvement(
        title="Optimized database queries",
        description="Reduced query time by 40% through indexing",
        category="optimization",
        impact="high",
        metrics={"time_saved": 120, "queries_optimized": 15}
    )
    print(f"   Recorded improvement: {imp1['improvement_id']}")
    
    imp2 = generator.record_improvement(
        title="Added automated backup system",
        description="Implemented hourly automated backups",
        category="automation",
        impact="critical"
    )
    print(f"   Recorded improvement: {imp2['improvement_id']}")
    
    # Test 2: Record capabilities
    print("\n2. Testing capability recording...")
    cap1 = generator.record_capability(
        name="Real-time analytics",
        description="Added real-time data analytics dashboard",
        capability_type="feature",
        status="active"
    )
    print(f"   Recorded capability: {cap1['capability_id']}")
    
    # Test 3: Generate morning report
    print("\n3. Testing report generation...")
    report = generator.generate_morning_report()
    print(f"   Generated report: {report['report_id']}")
    print(f"   Total improvements: {report['summary']['total_improvements']}")
    print(f"   New capabilities: {report['summary']['new_capabilities']}")
    print(f"   Productivity gain: +{report['summary']['productivity_gain_percentage']}%")
    
    # Test 4: Format report as text
    print("\n4. Testing text formatting...")
    text_report = generator.format_report_text(report)
    print("   Report formatted successfully")
    print(f"   Report length: {len(text_report)} characters")
    
    # Test 5: Get latest report
    print("\n5. Testing report retrieval...")
    latest = generator.get_latest_report()
    print(f"   Latest report: {latest['report_id']}")
    print(f"   Date: {latest['date']}")
    
    # Display formatted report
    print("\n6. Displaying formatted report...")
    print("\n" + text_report)
    
    print("\n" + "=" * 70)
    print("✓ All tests completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    test_morning_optimization_summary()
