#!/usr/bin/env python3
"""
Evening Learning Report System
Generates comprehensive evening reports of daytime learning and discoveries
Part of the Self-Evolving AI Ecosystem
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from collections import defaultdict
import statistics

class EveningLearningReport:
    """Generates evening learning reports"""
    
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
        self.reports_dir = self.base_dir / "reports" / "evening_reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Data sources
        self.data_dir = self.base_dir / "data"
        
        # Report sections
        self.sections = [
            "knowledge_acquired",
            "patterns_discovered",
            "optimization_opportunities",
            "user_interactions",
            "experiments_conducted",
            "skills_developed",
            "insights_generated",
            "challenges_encountered",
            "planned_implementations"
        ]
        
        self._initialized = True
    
    def generate_report(
        self,
        date: Optional[datetime] = None,
        include_sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate evening learning report"""
        
        if date is None:
            date = datetime.now()
        
        # Define daytime period (6 AM to 6 PM today)
        daytime_start = date.replace(hour=6, minute=0, second=0)
        daytime_end = date.replace(hour=18, minute=0, second=0)
        
        sections_to_include = include_sections or self.sections
        
        report = {
            "date": date.strftime("%Y-%m-%d"),
            "period": {
                "start": daytime_start.isoformat(),
                "end": daytime_end.isoformat()
            },
            "generated_at": datetime.now().isoformat(),
            "sections": {}
        }
        
        # Generate each section
        if "knowledge_acquired" in sections_to_include:
            report["sections"]["knowledge_acquired"] = self._get_knowledge_acquired(
                daytime_start, daytime_end
            )
        
        if "patterns_discovered" in sections_to_include:
            report["sections"]["patterns_discovered"] = self._get_patterns_discovered(
                daytime_start, daytime_end
            )
        
        if "optimization_opportunities" in sections_to_include:
            report["sections"]["optimization_opportunities"] = self._get_optimization_opportunities(
                daytime_start, daytime_end
            )
        
        if "user_interactions" in sections_to_include:
            report["sections"]["user_interactions"] = self._get_user_interactions(
                daytime_start, daytime_end
            )
        
        if "experiments_conducted" in sections_to_include:
            report["sections"]["experiments_conducted"] = self._get_experiments_conducted(
                daytime_start, daytime_end
            )
        
        if "skills_developed" in sections_to_include:
            report["sections"]["skills_developed"] = self._get_skills_developed(
                daytime_start, daytime_end
            )
        
        if "insights_generated" in sections_to_include:
            report["sections"]["insights_generated"] = self._get_insights_generated(
                daytime_start, daytime_end
            )
        
        if "challenges_encountered" in sections_to_include:
            report["sections"]["challenges_encountered"] = self._get_challenges_encountered(
                daytime_start, daytime_end
            )
        
        if "planned_implementations" in sections_to_include:
            report["sections"]["planned_implementations"] = self._get_planned_implementations(date)
        
        # Save report
        report_file = self.reports_dir / f"evening_report_{date.strftime('%Y%m%d')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def _get_knowledge_acquired(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get knowledge acquired during daytime"""
        
        knowledge_items = []
        
        # Check learning logs
        learning_dir = self.data_dir / "learning"
        if learning_dir.exists():
            for category_dir in learning_dir.iterdir():
                if category_dir.is_dir():
                    for log_file in category_dir.glob("*.jsonl"):
                        with open(log_file, 'r') as f:
                            for line in f:
                                item = json.loads(line.strip())
                                timestamp = datetime.fromisoformat(item.get("timestamp", ""))
                                
                                if start_time <= timestamp <= end_time:
                                    knowledge_items.append({
                                        "category": category_dir.name,
                                        "topic": item.get("topic", ""),
                                        "description": item.get("description", ""),
                                        "source": item.get("source", ""),
                                        "confidence": item.get("confidence", 0),
                                        "timestamp": item.get("timestamp")
                                    })
        
        return {
            "total": len(knowledge_items),
            "items": knowledge_items,
            "by_category": self._categorize_items(knowledge_items, "category"),
            "high_confidence": len([k for k in knowledge_items if k.get("confidence", 0) >= 0.8])
        }
    
    def _get_patterns_discovered(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get patterns discovered during daytime"""
        
        patterns = []
        
        # Check pattern analysis logs
        pattern_dir = self.data_dir / "patterns"
        if pattern_dir.exists():
            pattern_file = pattern_dir / "discovered_patterns.jsonl"
            if pattern_file.exists():
                with open(pattern_file, 'r') as f:
                    for line in f:
                        pattern = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(pattern.get("discovered_at", ""))
                        
                        if start_time <= timestamp <= end_time:
                            patterns.append({
                                "type": pattern.get("pattern_type", ""),
                                "description": pattern.get("description", ""),
                                "frequency": pattern.get("frequency", 0),
                                "confidence": pattern.get("confidence", 0),
                                "actionable": pattern.get("actionable", False),
                                "timestamp": pattern.get("discovered_at")
                            })
        
        actionable_patterns = [p for p in patterns if p.get("actionable", False)]
        
        return {
            "total": len(patterns),
            "actionable": len(actionable_patterns),
            "patterns": patterns,
            "by_type": self._categorize_items(patterns, "type")
        }
    
    def _get_optimization_opportunities(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get optimization opportunities identified"""
        
        opportunities = []
        
        # Check optimization identification logs
        optimization_dir = self.data_dir / "optimization"
        if optimization_dir.exists():
            opp_file = optimization_dir / "opportunities.jsonl"
            if opp_file.exists():
                with open(opp_file, 'r') as f:
                    for line in f:
                        opp = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(opp.get("identified_at", ""))
                        
                        if start_time <= timestamp <= end_time:
                            opportunities.append({
                                "area": opp.get("area", ""),
                                "description": opp.get("description", ""),
                                "estimated_impact": opp.get("estimated_impact", {}),
                                "priority": opp.get("priority", ""),
                                "effort": opp.get("effort", ""),
                                "timestamp": opp.get("identified_at")
                            })
        
        high_priority = [o for o in opportunities if o.get("priority") == "high"]
        
        return {
            "total": len(opportunities),
            "high_priority": len(high_priority),
            "opportunities": opportunities,
            "by_area": self._categorize_items(opportunities, "area")
        }
    
    def _get_user_interactions(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get user interactions during daytime"""
        
        interactions = []
        
        # Check interaction logs
        interaction_dir = self.data_dir / "interactions"
        if interaction_dir.exists():
            interaction_file = interaction_dir / "user_interactions.jsonl"
            if interaction_file.exists():
                with open(interaction_file, 'r') as f:
                    for line in f:
                        interaction = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(interaction.get("timestamp", ""))
                        
                        if start_time <= timestamp <= end_time:
                            interactions.append({
                                "type": interaction.get("interaction_type", ""),
                                "category": interaction.get("category", ""),
                                "sentiment": interaction.get("sentiment", ""),
                                "timestamp": interaction.get("timestamp")
                            })
        
        return {
            "total": len(interactions),
            "by_type": self._categorize_items(interactions, "type"),
            "sentiment_distribution": self._categorize_items(interactions, "sentiment")
        }
    
    def _get_experiments_conducted(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get experiments conducted during daytime"""
        
        experiments = []
        
        # Check experiment logs
        experiment_dir = self.data_dir / "experiments"
        if experiment_dir.exists():
            experiment_file = experiment_dir / "experiments.jsonl"
            if experiment_file.exists():
                with open(experiment_file, 'r') as f:
                    for line in f:
                        experiment = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(experiment.get("started_at", ""))
                        
                        if start_time <= timestamp <= end_time:
                            experiments.append({
                                "name": experiment.get("name", ""),
                                "hypothesis": experiment.get("hypothesis", ""),
                                "status": experiment.get("status", ""),
                                "result": experiment.get("result", ""),
                                "timestamp": experiment.get("started_at")
                            })
        
        completed = [e for e in experiments if e.get("status") == "completed"]
        successful = [e for e in completed if e.get("result") == "success"]
        
        return {
            "total": len(experiments),
            "completed": len(completed),
            "successful": len(successful),
            "success_rate": len(successful) / len(completed) if completed else 0,
            "experiments": experiments
        }
    
    def _get_skills_developed(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get skills developed during daytime"""
        
        skills = []
        
        # Check skill development logs
        skill_dir = self.data_dir / "skills"
        if skill_dir.exists():
            for skill_file in skill_dir.glob("*.jsonl"):
                with open(skill_file, 'r') as f:
                    for line in f:
                        skill = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(skill.get("timestamp", ""))
                        
                        if start_time <= timestamp <= end_time:
                            skills.append({
                                "skill": skill.get("skill_name", ""),
                                "category": skill.get("category", ""),
                                "proficiency_gain": skill.get("proficiency_gain", 0),
                                "current_level": skill.get("current_level", 0),
                                "timestamp": skill.get("timestamp")
                            })
        
        return {
            "total": len(skills),
            "skills": skills,
            "by_category": self._categorize_items(skills, "category"),
            "avg_proficiency_gain": statistics.mean(
                [s.get("proficiency_gain", 0) for s in skills]
            ) if skills else 0
        }
    
    def _get_insights_generated(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get insights generated during daytime"""
        
        insights = []
        
        # Check insight logs
        insight_dir = self.data_dir / "insights"
        if insight_dir.exists():
            insight_file = insight_dir / "insights.jsonl"
            if insight_file.exists():
                with open(insight_file, 'r') as f:
                    for line in f:
                        insight = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(insight.get("generated_at", ""))
                        
                        if start_time <= timestamp <= end_time:
                            insights.append({
                                "type": insight.get("insight_type", ""),
                                "description": insight.get("description", ""),
                                "confidence": insight.get("confidence", 0),
                                "actionable": insight.get("actionable", False),
                                "timestamp": insight.get("generated_at")
                            })
        
        actionable = [i for i in insights if i.get("actionable", False)]
        
        return {
            "total": len(insights),
            "actionable": len(actionable),
            "insights": insights,
            "by_type": self._categorize_items(insights, "type")
        }
    
    def _get_challenges_encountered(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Get challenges encountered during daytime"""
        
        challenges = []
        
        # Check error and challenge logs
        error_dir = self.data_dir / "errors"
        if error_dir.exists():
            error_file = error_dir / "errors.jsonl"
            if error_file.exists():
                with open(error_file, 'r') as f:
                    for line in f:
                        error = json.loads(line.strip())
                        timestamp = datetime.fromisoformat(error.get("timestamp", ""))
                        
                        if start_time <= timestamp <= end_time:
                            challenges.append({
                                "type": error.get("error_type", ""),
                                "description": error.get("description", ""),
                                "resolved": error.get("resolved", False),
                                "learning": error.get("learning", ""),
                                "timestamp": error.get("timestamp")
                            })
        
        resolved = [c for c in challenges if c.get("resolved", False)]
        
        return {
            "total": len(challenges),
            "resolved": len(resolved),
            "resolution_rate": len(resolved) / len(challenges) if challenges else 0,
            "challenges": challenges,
            "by_type": self._categorize_items(challenges, "type")
        }
    
    def _get_planned_implementations(self, date: datetime) -> Dict[str, Any]:
        """Get planned implementations for tonight"""
        
        implementations = {
            "optimizations": [],
            "deployments": [],
            "experiments": [],
            "learning_tasks": []
        }
        
        # Check planning files
        planning_dir = self.base_dir / "planning"
        if planning_dir.exists():
            plan_file = planning_dir / f"evening_plan_{date.strftime('%Y%m%d')}.json"
            if plan_file.exists():
                with open(plan_file, 'r') as f:
                    implementations = json.load(f)
        
        return implementations
    
    def _categorize_items(self, items: List[Dict], key: str) -> Dict[str, int]:
        """Categorize items by a key"""
        
        categories = defaultdict(int)
        for item in items:
            category = item.get(key, "unknown")
            categories[category] += 1
        
        return dict(categories)
    
    def generate_text_report(self, report: Dict[str, Any]) -> str:
        """Generate human-readable text report"""
        
        lines = []
        lines.append("=" * 80)
        lines.append(f"EVENING LEARNING REPORT - {report['date']}")
        lines.append("=" * 80)
        lines.append("")
        
        sections = report.get("sections", {})
        
        # Knowledge Acquired
        if "knowledge_acquired" in sections:
            knowledge = sections["knowledge_acquired"]
            lines.append(f"📚 KNOWLEDGE ACQUIRED: {knowledge['total']}")
            lines.append(f"   High Confidence Items: {knowledge['high_confidence']}")
            for category, count in knowledge.get("by_category", {}).items():
                lines.append(f"   - {category}: {count}")
            lines.append("")
        
        # Patterns Discovered
        if "patterns_discovered" in sections:
            patterns = sections["patterns_discovered"]
            lines.append(f"🔍 PATTERNS DISCOVERED: {patterns['total']}")
            lines.append(f"   Actionable Patterns: {patterns['actionable']}")
            lines.append("")
        
        # Optimization Opportunities
        if "optimization_opportunities" in sections:
            opps = sections["optimization_opportunities"]
            lines.append(f"💡 OPTIMIZATION OPPORTUNITIES: {opps['total']}")
            lines.append(f"   High Priority: {opps['high_priority']}")
            for area, count in opps.get("by_area", {}).items():
                lines.append(f"   - {area}: {count}")
            lines.append("")
        
        # User Interactions
        if "user_interactions" in sections:
            interactions = sections["user_interactions"]
            lines.append(f"👤 USER INTERACTIONS: {interactions['total']}")
            for sentiment, count in interactions.get("sentiment_distribution", {}).items():
                lines.append(f"   {sentiment}: {count}")
            lines.append("")
        
        # Experiments Conducted
        if "experiments_conducted" in sections:
            experiments = sections["experiments_conducted"]
            lines.append(f"🧪 EXPERIMENTS CONDUCTED: {experiments['total']}")
            lines.append(f"   Completed: {experiments['completed']}")
            lines.append(f"   Success Rate: {experiments['success_rate']*100:.1f}%")
            lines.append("")
        
        # Skills Developed
        if "skills_developed" in sections:
            skills = sections["skills_developed"]
            lines.append(f"🎯 SKILLS DEVELOPED: {skills['total']}")
            lines.append(f"   Average Proficiency Gain: {skills['avg_proficiency_gain']:.2f}")
            lines.append("")
        
        # Insights Generated
        if "insights_generated" in sections:
            insights = sections["insights_generated"]
            lines.append(f"💭 INSIGHTS GENERATED: {insights['total']}")
            lines.append(f"   Actionable: {insights['actionable']}")
            lines.append("")
        
        # Challenges Encountered
        if "challenges_encountered" in sections:
            challenges = sections["challenges_encountered"]
            lines.append(f"⚠️ CHALLENGES ENCOUNTERED: {challenges['total']}")
            lines.append(f"   Resolved: {challenges['resolved']} ({challenges['resolution_rate']*100:.1f}%)")
            lines.append("")
        
        # Planned Implementations
        if "planned_implementations" in sections:
            planned = sections["planned_implementations"]
            lines.append("🌙 PLANNED FOR TONIGHT:")
            if planned.get("optimizations"):
                lines.append(f"   Optimizations: {len(planned['optimizations'])}")
            if planned.get("deployments"):
                lines.append(f"   Deployments: {len(planned['deployments'])}")
            if planned.get("experiments"):
                lines.append(f"   Experiments: {len(planned['experiments'])}")
            lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get report generation statistics"""
        
        stats = {
            "total_reports": 0,
            "latest_report": None
        }
        
        if self.reports_dir.exists():
            reports = list(self.reports_dir.glob("evening_report_*.json"))
            stats["total_reports"] = len(reports)
            
            if reports:
                latest = max(reports, key=lambda p: p.stat().st_mtime)
                stats["latest_report"] = latest.name
        
        return stats

def get_reporter() -> EveningLearningReport:
    """Get the singleton EveningLearningReport instance"""
    return EveningLearningReport()

if __name__ == "__main__":
    # Example usage
    reporter = get_reporter()
    
    # Generate report for today
    report = reporter.generate_report()
    
    # Print text version
    text_report = reporter.generate_text_report(report)
    print(text_report)
    
    print(f"\nStatistics: {json.dumps(reporter.get_statistics(), indent=2)}")
