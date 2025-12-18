#!/usr/bin/env python3
"""
Evening Learning Report System

Generates comprehensive evening reports summarizing:
- Knowledge acquired during the day
- Patterns and insights discovered
- Optimization opportunities identified
- Experiments conducted and results
- Planned implementations for overnight
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path

class EveningReportSystem:
    def __init__(self, data_dir="/Users/lordwilson/vy-nexus/data/reporting"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.reports_file = self.data_dir / "evening_reports.json"
        self.reports = self._load_reports()
        
    def _load_reports(self):
        """Load existing reports"""
        if self.reports_file.exists():
            with open(self.reports_file, 'r') as f:
                return json.load(f)
        return {"reports": []}
    
    def _save_reports(self):
        """Save reports to file"""
        with open(self.reports_file, 'w') as f:
            json.dump(self.reports, f, indent=2)
    
    def generate_report(self, date=None):
        """Generate evening learning report"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        # Collect data from various sources
        knowledge_acquired = self._collect_knowledge_acquired()
        patterns_discovered = self._collect_patterns_discovered()
        optimization_opportunities = self._collect_optimization_opportunities()
        experiments_conducted = self._collect_experiments_conducted()
        planned_implementations = self._collect_planned_implementations()
        
        report = {
            "report_id": f"evening_{date}_{datetime.now().strftime('%H%M%S')}",
            "date": date,
            "generated_at": datetime.now().isoformat(),
            "knowledge_acquired": knowledge_acquired,
            "patterns_discovered": patterns_discovered,
            "optimization_opportunities": optimization_opportunities,
            "experiments_conducted": experiments_conducted,
            "planned_implementations": planned_implementations,
            "report_text": self._format_report_text(
                knowledge_acquired, patterns_discovered, optimization_opportunities,
                experiments_conducted, planned_implementations
            )
        }
        
        self.reports["reports"].append(report)
        self._save_reports()
        
        return report
    
    def _collect_knowledge_acquired(self):
        """Collect knowledge acquired during the day"""
        knowledge = {
            "technical_skills": [],
            "domain_expertise": [],
            "research_completed": [],
            "total_learning_time": 0.0
        }
        
        # Check technical learning
        skills_file = Path("/Users/lordwilson/vy-nexus/data/knowledge/skills.json")
        if skills_file.exists():
            with open(skills_file, 'r') as f:
                data = json.load(f)
                for skill in data.get("skills", []):
                    knowledge["technical_skills"].append({
                        "skill": skill.get("name"),
                        "proficiency": skill.get("proficiency", 0),
                        "last_practiced": skill.get("last_practiced")
                    })
        
        # Check domain expertise
        domains_file = Path("/Users/lordwilson/vy-nexus/data/knowledge/domains.json")
        if domains_file.exists():
            with open(domains_file, 'r') as f:
                data = json.load(f)
                for domain in data.get("domains", []):
                    knowledge["domain_expertise"].append({
                        "domain": domain.get("name"),
                        "expertise_level": domain.get("expertise_level", 0),
                        "research_count": len(domain.get("research", []))
                    })
        
        # Check research automation
        research_file = Path("/Users/lordwilson/vy-nexus/data/learning/research_completed.json")
        if research_file.exists():
            with open(research_file, 'r') as f:
                data = json.load(f)
                for research in data.get("completed", []):
                    knowledge["research_completed"].append({
                        "topic": research.get("topic"),
                        "findings": research.get("findings"),
                        "completed_at": research.get("completed_at")
                    })
        
        # Check learning sessions
        sessions_file = Path("/Users/lordwilson/vy-nexus/data/knowledge/learning_sessions.json")
        if sessions_file.exists():
            with open(sessions_file, 'r') as f:
                data = json.load(f)
                for session in data.get("sessions", []):
                    knowledge["total_learning_time"] += session.get("duration_minutes", 0) / 60.0
        
        return knowledge
    
    def _collect_patterns_discovered(self):
        """Collect patterns and insights discovered"""
        patterns = {
            "user_patterns": [],
            "workflow_patterns": [],
            "performance_patterns": [],
            "total_patterns": 0
        }
        
        # Check pattern recognition system
        pattern_file = Path("/Users/lordwilson/vy-nexus/data/learning/patterns.json")
        if pattern_file.exists():
            with open(pattern_file, 'r') as f:
                data = json.load(f)
                all_patterns = data.get("patterns", [])
                patterns["total_patterns"] = len(all_patterns)
                
                for pattern in all_patterns:
                    pattern_type = pattern.get("type")
                    pattern_info = {
                        "type": pattern_type,
                        "description": pattern.get("description"),
                        "frequency": pattern.get("frequency", 0),
                        "confidence": pattern.get("confidence", 0)
                    }
                    
                    if pattern_type in ["temporal", "user_behavior"]:
                        patterns["user_patterns"].append(pattern_info)
                    elif pattern_type in ["sequence", "workflow"]:
                        patterns["workflow_patterns"].append(pattern_info)
                    elif pattern_type in ["performance", "error"]:
                        patterns["performance_patterns"].append(pattern_info)
        
        return patterns
    
    def _collect_optimization_opportunities(self):
        """Collect optimization opportunities identified"""
        opportunities = {
            "automation_opportunities": [],
            "process_optimizations": [],
            "bottlenecks_identified": [],
            "total_opportunities": 0
        }
        
        # Check repetitive tasks scanner
        tasks_file = Path("/Users/lordwilson/vy-nexus/data/optimization/repetitive_tasks.json")
        if tasks_file.exists():
            with open(tasks_file, 'r') as f:
                data = json.load(f)
                for opp in data.get("opportunities", []):
                    opportunities["automation_opportunities"].append({
                        "task": opp.get("task_name"),
                        "frequency": opp.get("frequency"),
                        "time_saved_potential": opp.get("time_saved_potential"),
                        "priority": opp.get("priority")
                    })
        
        # Check process optimization engine
        process_file = Path("/Users/lordwilson/vy-nexus/data/optimization/processes.json")
        if process_file.exists():
            with open(process_file, 'r') as f:
                data = json.load(f)
                # Handle both list and dict formats
                processes = data if isinstance(data, list) else data.get("processes", [])
                for process in processes:
                    for opt in process.get("recommendations", []):
                        opportunities["process_optimizations"].append({
                            "process": process.get("name"),
                            "optimization": opt.get("type"),
                            "impact": opt.get("impact"),
                            "effort": opt.get("effort")
                        })
                    
                    for bottleneck in process.get("bottlenecks", []):
                        opportunities["bottlenecks_identified"].append({
                            "process": process.get("name"),
                            "step": bottleneck.get("step"),
                            "severity": bottleneck.get("severity")
                        })
        
        opportunities["total_opportunities"] = (
            len(opportunities["automation_opportunities"]) +
            len(opportunities["process_optimizations"]) +
            len(opportunities["bottlenecks_identified"])
        )
        
        return opportunities
    
    def _collect_experiments_conducted(self):
        """Collect experiments conducted and results"""
        experiments = {
            "total_experiments": 0,
            "successful_experiments": 0,
            "failed_experiments": 0,
            "experiments": []
        }
        
        # Check experiment designer
        experiment_file = Path("/Users/lordwilson/vy-nexus/data/self_improvement/experiments.json")
        if experiment_file.exists():
            with open(experiment_file, 'r') as f:
                data = json.load(f)
                # Handle both list and dict formats
                exps = data if isinstance(data, list) else data.get("experiments", [])
                for exp in exps:
                    status = exp.get("status")
                    experiments["total_experiments"] += 1
                    
                    if status == "completed":
                        results = exp.get("results", [])
                        success = any(r.get("success", False) for r in results)
                        if success:
                            experiments["successful_experiments"] += 1
                        else:
                            experiments["failed_experiments"] += 1
                    
                    experiments["experiments"].append({
                        "name": exp.get("name"),
                        "hypothesis": exp.get("hypothesis"),
                        "status": status,
                        "results_count": len(exp.get("results", [])),
                        "created_at": exp.get("created_at")
                    })
        
        return experiments
    
    def _collect_planned_implementations(self):
        """Collect planned implementations for overnight"""
        implementations = {
            "deployments_planned": [],
            "automations_ready": [],
            "optimizations_staged": [],
            "total_planned": 0
        }
        
        # Check deployment system
        deployment_file = Path("/Users/lordwilson/vy-nexus/data/deployment/deployments.json")
        if deployment_file.exists():
            with open(deployment_file, 'r') as f:
                data = json.load(f)
                # Handle both list and dict formats
                deployments = data if isinstance(data, list) else data.get("deployments", [])
                for deployment in deployments:
                    if deployment.get("status") in ["staged", "testing"]:
                        implementations["deployments_planned"].append({
                            "name": deployment.get("name"),
                            "description": deployment.get("description"),
                            "status": deployment.get("status"),
                            "rollout_strategy": deployment.get("rollout_strategy")
                        })
        
        # Check automation script deployer
        automation_file = Path("/Users/lordwilson/vy-nexus/data/deployment/automation_scripts.json")
        if automation_file.exists():
            with open(automation_file, 'r') as f:
                data = json.load(f)
                # Handle both list and dict formats
                scripts = data if isinstance(data, list) else data.get("scripts", [])
                for script in scripts:
                    if script.get("status") == "validated":
                        implementations["automations_ready"].append({
                            "name": script.get("name"),
                            "type": script.get("type"),
                            "validated_at": script.get("validated_at")
                        })
        
        # Check process optimization engine
        process_file = Path("/Users/lordwilson/vy-nexus/data/optimization/processes.json")
        if process_file.exists():
            with open(process_file, 'r') as f:
                data = json.load(f)
                # Handle both list and dict formats
                processes = data if isinstance(data, list) else data.get("processes", [])
                for process in processes:
                    for opt in process.get("recommendations", []):
                        if opt.get("status") == "approved":
                            implementations["optimizations_staged"].append({
                                "process": process.get("name"),
                                "optimization": opt.get("type"),
                                "impact": opt.get("impact")
                            })
        
        implementations["total_planned"] = (
            len(implementations["deployments_planned"]) +
            len(implementations["automations_ready"]) +
            len(implementations["optimizations_staged"])
        )
        
        return implementations
    
    def _format_report_text(self, knowledge, patterns, opportunities, experiments, implementations):
        """Format report as readable text"""
        lines = []
        lines.append("=" * 80)
        lines.append("EVENING LEARNING REPORT")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 80)
        lines.append("")
        
        # Knowledge acquired section
        lines.append("KNOWLEDGE ACQUIRED TODAY:")
        lines.append(f"  Total Learning Time: {knowledge['total_learning_time']:.2f} hours")
        lines.append(f"  Technical Skills: {len(knowledge['technical_skills'])}")
        for skill in knowledge["technical_skills"][:5]:  # Top 5
            lines.append(f"    - {skill['skill']}: {skill['proficiency']}% proficiency")
        lines.append(f"  Domain Expertise: {len(knowledge['domain_expertise'])}")
        for domain in knowledge["domain_expertise"][:5]:  # Top 5
            lines.append(f"    - {domain['domain']}: Level {domain['expertise_level']}")
        lines.append(f"  Research Completed: {len(knowledge['research_completed'])}")
        for research in knowledge["research_completed"][:3]:  # Top 3
            lines.append(f"    - {research['topic']}")
        lines.append("")
        
        # Patterns discovered section
        lines.append("PATTERNS & INSIGHTS DISCOVERED:")
        lines.append(f"  Total Patterns: {patterns['total_patterns']}")
        lines.append(f"  User Patterns: {len(patterns['user_patterns'])}")
        for pattern in patterns["user_patterns"][:3]:  # Top 3
            lines.append(f"    - {pattern['description']} (Confidence: {pattern['confidence']:.1f}%)")
        lines.append(f"  Workflow Patterns: {len(patterns['workflow_patterns'])}")
        for pattern in patterns["workflow_patterns"][:3]:  # Top 3
            lines.append(f"    - {pattern['description']} (Frequency: {pattern['frequency']})")
        lines.append(f"  Performance Patterns: {len(patterns['performance_patterns'])}")
        lines.append("")
        
        # Optimization opportunities section
        lines.append("OPTIMIZATION OPPORTUNITIES IDENTIFIED:")
        lines.append(f"  Total Opportunities: {opportunities['total_opportunities']}")
        lines.append(f"  Automation Opportunities: {len(opportunities['automation_opportunities'])}")
        for opp in opportunities["automation_opportunities"][:3]:  # Top 3
            lines.append(f"    - {opp['task']} (Priority: {opp['priority']}, Time Saved: {opp['time_saved_potential']:.1f}h)")
        lines.append(f"  Process Optimizations: {len(opportunities['process_optimizations'])}")
        for opt in opportunities["process_optimizations"][:3]:  # Top 3
            lines.append(f"    - {opt['process']}: {opt['optimization']} (Impact: {opt['impact']})")
        lines.append(f"  Bottlenecks Identified: {len(opportunities['bottlenecks_identified'])}")
        lines.append("")
        
        # Experiments conducted section
        lines.append("EXPERIMENTS CONDUCTED:")
        lines.append(f"  Total Experiments: {experiments['total_experiments']}")
        lines.append(f"  Successful: {experiments['successful_experiments']}")
        lines.append(f"  Failed: {experiments['failed_experiments']}")
        if experiments["experiments"]:
            lines.append("  Details:")
            for exp in experiments["experiments"][:5]:  # Top 5
                lines.append(f"    - {exp['name']}: {exp['status']} ({exp['results_count']} results)")
        lines.append("")
        
        # Planned implementations section
        lines.append("PLANNED IMPLEMENTATIONS FOR OVERNIGHT:")
        lines.append(f"  Total Planned: {implementations['total_planned']}")
        lines.append(f"  Deployments: {len(implementations['deployments_planned'])}")
        for deployment in implementations["deployments_planned"]:
            lines.append(f"    - {deployment['name']}: {deployment['description']}")
        lines.append(f"  Automations Ready: {len(implementations['automations_ready'])}")
        for automation in implementations["automations_ready"]:
            lines.append(f"    - {automation['name']} ({automation['type']})")
        lines.append(f"  Optimizations Staged: {len(implementations['optimizations_staged'])}")
        for opt in implementations["optimizations_staged"]:
            lines.append(f"    - {opt['process']}: {opt['optimization']}")
        lines.append("")
        
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def get_report(self, report_id):
        """Get a specific report by ID"""
        for report in self.reports["reports"]:
            if report["report_id"] == report_id:
                return report
        return None
    
    def get_recent_reports(self, days=7):
        """Get reports from the last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = []
        
        for report in self.reports["reports"]:
            report_date = datetime.fromisoformat(report["generated_at"])
            if report_date >= cutoff:
                recent.append(report)
        
        return sorted(recent, key=lambda x: x["generated_at"], reverse=True)
    
    def get_statistics(self):
        """Get statistics about evening reports"""
        if not self.reports["reports"]:
            return {"total_reports": 0}
        
        total_knowledge = sum(len(r["knowledge_acquired"]["technical_skills"]) for r in self.reports["reports"])
        total_patterns = sum(r["patterns_discovered"]["total_patterns"] for r in self.reports["reports"])
        total_opportunities = sum(r["optimization_opportunities"]["total_opportunities"] for r in self.reports["reports"])
        total_experiments = sum(r["experiments_conducted"]["total_experiments"] for r in self.reports["reports"])
        
        return {
            "total_reports": len(self.reports["reports"]),
            "total_knowledge_items": total_knowledge,
            "total_patterns": total_patterns,
            "total_opportunities": total_opportunities,
            "total_experiments": total_experiments,
            "avg_knowledge_per_day": total_knowledge / len(self.reports["reports"]),
            "avg_patterns_per_day": total_patterns / len(self.reports["reports"]),
            "avg_opportunities_per_day": total_opportunities / len(self.reports["reports"])
        }

if __name__ == "__main__":
    print("Testing Evening Report System...")
    print()
    
    system = EveningReportSystem()
    
    # Generate an evening report
    print("1. Generating evening report...")
    report = system.generate_report()
    print(f"   Report ID: {report['report_id']}")
    print()
    
    # Display the formatted report
    print("2. Formatted Report:")
    print(report["report_text"])
    print()
    
    # Get statistics
    print("3. Getting statistics...")
    stats = system.get_statistics()
    print(f"   Total reports: {stats['total_reports']}")
    print(f"   Total knowledge items: {stats['total_knowledge_items']}")
    print(f"   Total patterns: {stats['total_patterns']}")
    print(f"   Total opportunities: {stats['total_opportunities']}")
    print(f"   Total experiments: {stats['total_experiments']}")
    print()
    
    print("=" * 50)
    print("All tests completed successfully!")
    print("=" * 50)
