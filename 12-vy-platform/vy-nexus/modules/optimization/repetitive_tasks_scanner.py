#!/usr/bin/env python3
"""
Repetitive Tasks Scanner
Identifies repetitive tasks and patterns that can be automated.

This module analyzes user interactions and task history to identify:
- Frequently repeated tasks
- Similar task sequences
- Manual processes that could be automated
- Time-consuming repetitive operations
"""

import json
import os
from datetime import datetime, timedelta
from collections import Counter, defaultdict
from typing import Dict, List, Any, Tuple
import re


class RepetitiveTasksScanner:
    """Scans for repetitive tasks and automation opportunities."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/optimization"):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Data files
        self.tasks_file = os.path.join(self.data_dir, "tasks.json")
        self.patterns_file = os.path.join(self.data_dir, "repetitive_patterns.json")
        self.opportunities_file = os.path.join(self.data_dir, "automation_opportunities.json")
        self.statistics_file = os.path.join(self.data_dir, "scanner_statistics.json")
        
        # Load existing data
        self.tasks = self._load_json(self.tasks_file, [])
        self.patterns = self._load_json(self.patterns_file, [])
        self.opportunities = self._load_json(self.opportunities_file, [])
        self.statistics = self._load_json(self.statistics_file, {
            "total_tasks_scanned": 0,
            "repetitive_patterns_found": 0,
            "automation_opportunities": 0,
            "potential_time_saved": 0,
            "last_scan": None
        })
    
    def _load_json(self, filepath: str, default: Any) -> Any:
        """Load JSON data from file."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
        return default
    
    def _save_json(self, filepath: str, data: Any) -> None:
        """Save JSON data to file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
    
    def record_task(self, task_type: str, description: str, 
                   duration: float = None, steps: List[str] = None,
                   tools_used: List[str] = None, context: Dict = None) -> str:
        """Record a task for analysis."""
        task_id = f"task_{len(self.tasks) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        task = {
            "id": task_id,
            "type": task_type,
            "description": description,
            "duration": duration,
            "steps": steps or [],
            "tools_used": tools_used or [],
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
            "analyzed": False
        }
        
        self.tasks.append(task)
        self._save_json(self.tasks_file, self.tasks)
        self.statistics["total_tasks_scanned"] += 1
        self._save_json(self.statistics_file, self.statistics)
        
        return task_id
    
    def scan_for_repetitive_patterns(self, time_window_days: int = 30) -> List[Dict]:
        """Scan tasks for repetitive patterns."""
        cutoff_date = datetime.now() - timedelta(days=time_window_days)
        recent_tasks = [
            t for t in self.tasks 
            if datetime.fromisoformat(t["timestamp"]) > cutoff_date
        ]
        
        patterns_found = []
        
        # 1. Identify frequently repeated task types
        task_type_patterns = self._find_task_type_patterns(recent_tasks)
        patterns_found.extend(task_type_patterns)
        
        # 2. Identify similar task sequences
        sequence_patterns = self._find_sequence_patterns(recent_tasks)
        patterns_found.extend(sequence_patterns)
        
        # 3. Identify repeated tool combinations
        tool_patterns = self._find_tool_patterns(recent_tasks)
        patterns_found.extend(tool_patterns)
        
        # 4. Identify time-consuming repetitive tasks
        time_consuming_patterns = self._find_time_consuming_patterns(recent_tasks)
        patterns_found.extend(time_consuming_patterns)
        
        # 5. Identify similar descriptions (semantic similarity)
        description_patterns = self._find_description_patterns(recent_tasks)
        patterns_found.extend(description_patterns)
        
        # Save patterns
        for pattern in patterns_found:
            if pattern not in self.patterns:
                self.patterns.append(pattern)
        
        self._save_json(self.patterns_file, self.patterns)
        self.statistics["repetitive_patterns_found"] = len(self.patterns)
        self.statistics["last_scan"] = datetime.now().isoformat()
        self._save_json(self.statistics_file, self.statistics)
        
        return patterns_found
    
    def _find_task_type_patterns(self, tasks: List[Dict]) -> List[Dict]:
        """Find frequently repeated task types."""
        task_types = [t["type"] for t in tasks]
        type_counts = Counter(task_types)
        
        patterns = []
        for task_type, count in type_counts.items():
            if count >= 3:  # Threshold for repetition
                # Calculate average duration
                type_tasks = [t for t in tasks if t["type"] == task_type]
                durations = [t["duration"] for t in type_tasks if t["duration"]]
                avg_duration = sum(durations) / len(durations) if durations else 0
                
                patterns.append({
                    "pattern_type": "task_type_repetition",
                    "task_type": task_type,
                    "frequency": count,
                    "average_duration": avg_duration,
                    "total_time_spent": sum(durations),
                    "automation_potential": "high" if count >= 5 else "medium",
                    "identified_at": datetime.now().isoformat()
                })
        
        return patterns
    
    def _find_sequence_patterns(self, tasks: List[Dict]) -> List[Dict]:
        """Find repeated sequences of tasks."""
        patterns = []
        
        # Look for sequences of 2-5 tasks
        for seq_length in range(2, 6):
            sequences = []
            for i in range(len(tasks) - seq_length + 1):
                seq = tuple(t["type"] for t in tasks[i:i+seq_length])
                sequences.append(seq)
            
            seq_counts = Counter(sequences)
            for sequence, count in seq_counts.items():
                if count >= 2:  # Found at least twice
                    patterns.append({
                        "pattern_type": "task_sequence",
                        "sequence": list(sequence),
                        "sequence_length": seq_length,
                        "frequency": count,
                        "automation_potential": "high" if count >= 3 else "medium",
                        "identified_at": datetime.now().isoformat()
                    })
        
        return patterns
    
    def _find_tool_patterns(self, tasks: List[Dict]) -> List[Dict]:
        """Find repeated tool combinations."""
        patterns = []
        tool_combinations = []
        
        for task in tasks:
            if task["tools_used"]:
                tool_combo = tuple(sorted(task["tools_used"]))
                tool_combinations.append(tool_combo)
        
        combo_counts = Counter(tool_combinations)
        for combo, count in combo_counts.items():
            if count >= 3 and len(combo) > 1:
                patterns.append({
                    "pattern_type": "tool_combination",
                    "tools": list(combo),
                    "frequency": count,
                    "automation_potential": "medium",
                    "identified_at": datetime.now().isoformat()
                })
        
        return patterns
    
    def _find_time_consuming_patterns(self, tasks: List[Dict]) -> List[Dict]:
        """Find time-consuming repetitive tasks."""
        patterns = []
        
        # Group by task type and calculate total time
        time_by_type = defaultdict(lambda: {"count": 0, "total_time": 0, "tasks": []})
        
        for task in tasks:
            if task["duration"]:
                task_type = task["type"]
                time_by_type[task_type]["count"] += 1
                time_by_type[task_type]["total_time"] += task["duration"]
                time_by_type[task_type]["tasks"].append(task["id"])
        
        # Find tasks that are both repetitive and time-consuming
        for task_type, data in time_by_type.items():
            if data["count"] >= 3 and data["total_time"] >= 300:  # 5+ minutes total
                patterns.append({
                    "pattern_type": "time_consuming_repetition",
                    "task_type": task_type,
                    "frequency": data["count"],
                    "total_time_spent": data["total_time"],
                    "average_time": data["total_time"] / data["count"],
                    "automation_potential": "high",
                    "priority": "high",
                    "identified_at": datetime.now().isoformat()
                })
        
        return patterns
    
    def _find_description_patterns(self, tasks: List[Dict]) -> List[Dict]:
        """Find tasks with similar descriptions."""
        patterns = []
        
        # Simple keyword-based similarity
        description_groups = defaultdict(list)
        
        for task in tasks:
            # Extract key words (simple approach)
            words = re.findall(r'\b\w{4,}\b', task["description"].lower())
            key_words = tuple(sorted(set(words))[:5])  # Top 5 unique words
            
            if key_words:
                description_groups[key_words].append(task)
        
        for key_words, group_tasks in description_groups.items():
            if len(group_tasks) >= 3:
                patterns.append({
                    "pattern_type": "similar_descriptions",
                    "key_words": list(key_words),
                    "frequency": len(group_tasks),
                    "task_ids": [t["id"] for t in group_tasks],
                    "automation_potential": "medium",
                    "identified_at": datetime.now().isoformat()
                })
        
        return patterns
    
    def identify_automation_opportunities(self) -> List[Dict]:
        """Identify specific automation opportunities from patterns."""
        opportunities = []
        
        for pattern in self.patterns:
            opportunity = self._pattern_to_opportunity(pattern)
            if opportunity and opportunity not in self.opportunities:
                opportunities.append(opportunity)
                self.opportunities.append(opportunity)
        
        self._save_json(self.opportunities_file, self.opportunities)
        self.statistics["automation_opportunities"] = len(self.opportunities)
        self._save_json(self.statistics_file, self.statistics)
        
        return opportunities
    
    def _pattern_to_opportunity(self, pattern: Dict) -> Dict:
        """Convert a pattern into an automation opportunity."""
        pattern_type = pattern["pattern_type"]
        
        if pattern_type == "task_type_repetition":
            return {
                "opportunity_id": f"auto_{len(self.opportunities) + 1}",
                "type": "task_automation",
                "title": f"Automate {pattern['task_type']} tasks",
                "description": f"This task type occurs {pattern['frequency']} times. Consider creating an automation.",
                "potential_time_saved": pattern.get("total_time_spent", 0),
                "priority": pattern.get("automation_potential", "medium"),
                "implementation_suggestions": [
                    "Create a script or macro",
                    "Build a workflow template",
                    "Use keyboard shortcuts"
                ],
                "pattern_reference": pattern,
                "created_at": datetime.now().isoformat()
            }
        
        elif pattern_type == "task_sequence":
            return {
                "opportunity_id": f"auto_{len(self.opportunities) + 1}",
                "type": "workflow_automation",
                "title": f"Automate sequence: {' → '.join(pattern['sequence'])}",
                "description": f"This sequence occurs {pattern['frequency']} times. Create a workflow.",
                "priority": pattern.get("automation_potential", "medium"),
                "implementation_suggestions": [
                    "Create a workflow template",
                    "Build a multi-step automation",
                    "Use task chaining"
                ],
                "pattern_reference": pattern,
                "created_at": datetime.now().isoformat()
            }
        
        elif pattern_type == "time_consuming_repetition":
            return {
                "opportunity_id": f"auto_{len(self.opportunities) + 1}",
                "type": "high_priority_automation",
                "title": f"Automate time-consuming {pattern['task_type']}",
                "description": f"This task takes {pattern['total_time_spent']:.1f}s total. High ROI for automation.",
                "potential_time_saved": pattern["total_time_spent"],
                "priority": "high",
                "implementation_suggestions": [
                    "Create dedicated automation script",
                    "Optimize existing process",
                    "Use batch processing"
                ],
                "pattern_reference": pattern,
                "created_at": datetime.now().isoformat()
            }
        
        elif pattern_type == "tool_combination":
            return {
                "opportunity_id": f"auto_{len(self.opportunities) + 1}",
                "type": "tool_integration",
                "title": f"Integrate tools: {', '.join(pattern['tools'])}",
                "description": f"These tools are used together {pattern['frequency']} times.",
                "priority": "medium",
                "implementation_suggestions": [
                    "Create tool integration",
                    "Build unified interface",
                    "Use API connections"
                ],
                "pattern_reference": pattern,
                "created_at": datetime.now().isoformat()
            }
        
        return None
    
    def get_top_opportunities(self, limit: int = 10) -> List[Dict]:
        """Get top automation opportunities by priority and time savings."""
        # Sort by priority and potential time saved
        priority_order = {"high": 3, "medium": 2, "low": 1}
        
        sorted_opportunities = sorted(
            self.opportunities,
            key=lambda x: (
                priority_order.get(x.get("priority", "low"), 0),
                x.get("potential_time_saved", 0)
            ),
            reverse=True
        )
        
        return sorted_opportunities[:limit]
    
    def generate_report(self) -> Dict:
        """Generate a comprehensive report on repetitive tasks and opportunities."""
        total_time_saved = sum(
            opp.get("potential_time_saved", 0) 
            for opp in self.opportunities
        )
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_tasks_scanned": self.statistics["total_tasks_scanned"],
                "repetitive_patterns_found": len(self.patterns),
                "automation_opportunities": len(self.opportunities),
                "potential_time_saved_seconds": total_time_saved,
                "potential_time_saved_hours": total_time_saved / 3600
            },
            "pattern_breakdown": self._get_pattern_breakdown(),
            "top_opportunities": self.get_top_opportunities(5),
            "recommendations": self._generate_recommendations()
        }
        
        return report
    
    def _get_pattern_breakdown(self) -> Dict:
        """Get breakdown of patterns by type."""
        breakdown = defaultdict(int)
        for pattern in self.patterns:
            breakdown[pattern["pattern_type"]] += 1
        return dict(breakdown)
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        high_priority_opps = [
            opp for opp in self.opportunities 
            if opp.get("priority") == "high"
        ]
        
        if high_priority_opps:
            recommendations.append(
                f"Focus on {len(high_priority_opps)} high-priority automation opportunities first"
            )
        
        time_consuming = [
            p for p in self.patterns 
            if p.get("pattern_type") == "time_consuming_repetition"
        ]
        
        if time_consuming:
            recommendations.append(
                f"Prioritize automating {len(time_consuming)} time-consuming repetitive tasks"
            )
        
        sequences = [
            p for p in self.patterns 
            if p.get("pattern_type") == "task_sequence"
        ]
        
        if sequences:
            recommendations.append(
                f"Create workflow templates for {len(sequences)} repeated task sequences"
            )
        
        if not recommendations:
            recommendations.append("Continue monitoring for repetitive patterns")
        
        return recommendations


if __name__ == "__main__":
    # Test the scanner
    scanner = RepetitiveTasksScanner()
    
    # Record some sample tasks
    print("Recording sample tasks...")
    scanner.record_task(
        "file_organization",
        "Organize files in downloads folder",
        duration=120,
        steps=["open_finder", "select_files", "move_to_folder"],
        tools_used=["Finder"]
    )
    
    scanner.record_task(
        "file_organization",
        "Organize project files",
        duration=150,
        steps=["open_finder", "select_files", "move_to_folder"],
        tools_used=["Finder"]
    )
    
    scanner.record_task(
        "data_analysis",
        "Analyze sales data",
        duration=300,
        steps=["open_excel", "load_data", "create_charts"],
        tools_used=["Excel", "Python"]
    )
    
    scanner.record_task(
        "file_organization",
        "Clean up desktop files",
        duration=90,
        steps=["open_finder", "select_files", "move_to_folder"],
        tools_used=["Finder"]
    )
    
    scanner.record_task(
        "email_management",
        "Process inbox emails",
        duration=180,
        steps=["open_mail", "read_emails", "categorize"],
        tools_used=["Mail"]
    )
    
    # Scan for patterns
    print("\nScanning for repetitive patterns...")
    patterns = scanner.scan_for_repetitive_patterns()
    print(f"Found {len(patterns)} patterns")
    
    # Identify opportunities
    print("\nIdentifying automation opportunities...")
    opportunities = scanner.identify_automation_opportunities()
    print(f"Found {len(opportunities)} opportunities")
    
    # Generate report
    print("\nGenerating report...")
    report = scanner.generate_report()
    
    print("\n" + "="*50)
    print("REPETITIVE TASKS SCANNER REPORT")
    print("="*50)
    print(f"\nTotal tasks scanned: {report['summary']['total_tasks_scanned']}")
    print(f"Patterns found: {report['summary']['repetitive_patterns_found']}")
    print(f"Automation opportunities: {report['summary']['automation_opportunities']}")
    print(f"Potential time saved: {report['summary']['potential_time_saved_hours']:.2f} hours")
    
    print("\nTop Opportunities:")
    for i, opp in enumerate(report['top_opportunities'], 1):
        print(f"  {i}. [{opp['priority'].upper()}] {opp['title']}")
        print(f"     {opp['description']}")
    
    print("\nRecommendations:")
    for rec in report['recommendations']:
        print(f"  - {rec}")
    
    print("\n✅ Repetitive tasks scanner is operational!")
