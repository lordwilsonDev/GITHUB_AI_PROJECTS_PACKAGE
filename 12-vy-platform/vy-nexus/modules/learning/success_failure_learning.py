#!/usr/bin/env python3
"""
Success/Failure Learning Module
Part of the Self-Evolving AI Ecosystem

This module learns from successful task completions and failures to
improve future performance and avoid repeating mistakes.
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple, Optional
import hashlib


class SuccessFailureLearningSystem:
    """Learns from successes and failures to improve future performance."""
    
    def __init__(self, data_dir: str = None):
        """Initialize the success/failure learning system."""
        if data_dir is None:
            data_dir = os.path.expanduser("~/vy-nexus/data/learning")
        
        self.data_dir = data_dir
        self.successes_file = os.path.join(data_dir, "successes.json")
        self.failures_file = os.path.join(data_dir, "failures.json")
        self.lessons_file = os.path.join(data_dir, "lessons_learned.json")
        self.best_practices_file = os.path.join(data_dir, "best_practices.json")
        self.anti_patterns_file = os.path.join(data_dir, "anti_patterns.json")
        
        # Create directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing data
        self.successes = self._load_json(self.successes_file, [])
        self.failures = self._load_json(self.failures_file, [])
        self.lessons = self._load_json(self.lessons_file, [])
        self.best_practices = self._load_json(self.best_practices_file, [])
        self.anti_patterns = self._load_json(self.anti_patterns_file, [])
    
    def _load_json(self, filepath: str, default: Any) -> Any:
        """Load JSON data from file."""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {filepath}: {e}")
        return default
    
    def _save_json(self, filepath: str, data: Any):
        """Save data to JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {filepath}: {e}")
    
    def _generate_signature(self, task_data: Dict) -> str:
        """Generate a unique signature for a task."""
        key_elements = [
            task_data.get('task_type', ''),
            str(task_data.get('tools_used', [])),
            task_data.get('context', '')
        ]
        signature_str = '|'.join(key_elements)
        return hashlib.md5(signature_str.encode()).hexdigest()[:12]
    
    def record_success(self, task_data: Dict) -> str:
        """
        Record a successful task completion.
        
        Args:
            task_data: Dictionary containing:
                - task_type: Type of task
                - description: What was accomplished
                - tools_used: List of tools/methods used
                - duration: Time taken
                - context: Relevant context
                - key_factors: What made it successful
        
        Returns:
            Success ID
        """
        success_id = self._generate_signature(task_data)
        
        success_record = {
            "id": success_id,
            "timestamp": datetime.now().isoformat(),
            "task_type": task_data.get('task_type', 'unknown'),
            "description": task_data.get('description', ''),
            "tools_used": task_data.get('tools_used', []),
            "duration": task_data.get('duration', 0),
            "context": task_data.get('context', ''),
            "key_factors": task_data.get('key_factors', []),
            "efficiency_score": task_data.get('efficiency_score', 0),
            "user_satisfaction": task_data.get('user_satisfaction', 0)
        }
        
        self.successes.append(success_record)
        self._save_json(self.successes_file, self.successes)
        
        # Analyze for best practices
        self._extract_best_practices(success_record)
        
        return success_id
    
    def record_failure(self, task_data: Dict) -> str:
        """
        Record a failed task attempt.
        
        Args:
            task_data: Dictionary containing:
                - task_type: Type of task
                - description: What was attempted
                - tools_used: List of tools/methods used
                - error_type: Type of error
                - error_message: Error details
                - context: Relevant context
                - root_cause: Identified root cause
                - attempted_solutions: What was tried
        
        Returns:
            Failure ID
        """
        failure_id = self._generate_signature(task_data)
        
        failure_record = {
            "id": failure_id,
            "timestamp": datetime.now().isoformat(),
            "task_type": task_data.get('task_type', 'unknown'),
            "description": task_data.get('description', ''),
            "tools_used": task_data.get('tools_used', []),
            "error_type": task_data.get('error_type', 'unknown'),
            "error_message": task_data.get('error_message', ''),
            "context": task_data.get('context', ''),
            "root_cause": task_data.get('root_cause', ''),
            "attempted_solutions": task_data.get('attempted_solutions', []),
            "severity": task_data.get('severity', 'medium')
        }
        
        self.failures.append(failure_record)
        self._save_json(self.failures_file, self.failures)
        
        # Analyze for anti-patterns
        self._extract_anti_patterns(failure_record)
        
        # Generate lesson learned
        self._generate_lesson(failure_record)
        
        return failure_id
    
    def _extract_best_practices(self, success_record: Dict):
        """Extract best practices from successful tasks."""
        task_type = success_record['task_type']
        key_factors = success_record.get('key_factors', [])
        
        # Find similar successes
        similar_successes = [
            s for s in self.successes
            if s['task_type'] == task_type
            and s['id'] != success_record['id']
        ]
        
        # If we have multiple successes with same factors, it's a best practice
        if len(similar_successes) >= 2:
            common_factors = set(key_factors)
            for success in similar_successes:
                common_factors &= set(success.get('key_factors', []))
            
            if common_factors:
                # Check if this best practice already exists
                existing = False
                for bp in self.best_practices:
                    if (bp['task_type'] == task_type and 
                        set(bp['factors']) == common_factors):
                        bp['occurrences'] += 1
                        bp['last_seen'] = datetime.now().isoformat()
                        existing = True
                        break
                
                if not existing:
                    best_practice = {
                        "id": hashlib.md5(f"{task_type}{''.join(sorted(common_factors))}".encode()).hexdigest()[:12],
                        "task_type": task_type,
                        "title": f"Best practice for {task_type}",
                        "factors": list(common_factors),
                        "description": f"Consistently successful when: {', '.join(common_factors)}",
                        "occurrences": len(similar_successes) + 1,
                        "first_seen": success_record['timestamp'],
                        "last_seen": datetime.now().isoformat(),
                        "confidence": "high" if len(similar_successes) >= 5 else "medium"
                    }
                    self.best_practices.append(best_practice)
                
                self._save_json(self.best_practices_file, self.best_practices)
    
    def _extract_anti_patterns(self, failure_record: Dict):
        """Extract anti-patterns from failed tasks."""
        task_type = failure_record['task_type']
        error_type = failure_record['error_type']
        root_cause = failure_record.get('root_cause', '')
        
        # Find similar failures
        similar_failures = [
            f for f in self.failures
            if f['task_type'] == task_type
            and f['error_type'] == error_type
            and f['id'] != failure_record['id']
        ]
        
        # If we have multiple failures with same pattern, it's an anti-pattern
        if len(similar_failures) >= 1:
            # Check if this anti-pattern already exists
            existing = False
            for ap in self.anti_patterns:
                if (ap['task_type'] == task_type and 
                    ap['error_type'] == error_type):
                    ap['occurrences'] += 1
                    ap['last_seen'] = datetime.now().isoformat()
                    existing = True
                    break
            
            if not existing:
                anti_pattern = {
                    "id": hashlib.md5(f"{task_type}{error_type}".encode()).hexdigest()[:12],
                    "task_type": task_type,
                    "error_type": error_type,
                    "title": f"Anti-pattern: {error_type} in {task_type}",
                    "description": f"Repeatedly fails with {error_type}",
                    "root_cause": root_cause,
                    "occurrences": len(similar_failures) + 1,
                    "first_seen": failure_record['timestamp'],
                    "last_seen": datetime.now().isoformat(),
                    "severity": failure_record.get('severity', 'medium'),
                    "prevention": self._suggest_prevention(failure_record, similar_failures)
                }
                self.anti_patterns.append(anti_pattern)
            
            self._save_json(self.anti_patterns_file, self.anti_patterns)
    
    def _suggest_prevention(self, failure: Dict, similar_failures: List[Dict]) -> str:
        """Suggest how to prevent this type of failure."""
        # Analyze attempted solutions
        all_attempts = failure.get('attempted_solutions', [])
        for f in similar_failures:
            all_attempts.extend(f.get('attempted_solutions', []))
        
        if all_attempts:
            return f"Avoid: {', '.join(set(all_attempts))}. These approaches have failed before."
        
        return "No prevention strategy identified yet. More data needed."
    
    def _generate_lesson(self, failure_record: Dict):
        """Generate a lesson learned from a failure."""
        lesson = {
            "id": failure_record['id'],
            "timestamp": datetime.now().isoformat(),
            "task_type": failure_record['task_type'],
            "title": f"Lesson from {failure_record['task_type']} failure",
            "what_happened": failure_record['description'],
            "why_it_failed": failure_record.get('root_cause', 'Unknown'),
            "what_to_do_instead": self._suggest_alternative(failure_record),
            "severity": failure_record.get('severity', 'medium'),
            "applied": False
        }
        
        self.lessons.append(lesson)
        self._save_json(self.lessons_file, self.lessons)
    
    def _suggest_alternative(self, failure: Dict) -> str:
        """Suggest alternative approach based on successful similar tasks."""
        task_type = failure['task_type']
        
        # Find successful tasks of same type
        successful_similar = [
            s for s in self.successes
            if s['task_type'] == task_type
        ]
        
        if successful_similar:
            # Get most common tools/approaches from successes
            all_tools = []
            for s in successful_similar:
                all_tools.extend(s.get('tools_used', []))
            
            if all_tools:
                common_tools = Counter(all_tools).most_common(3)
                return f"Try using: {', '.join([t for t, _ in common_tools])}"
        
        return "No alternative approach identified yet. Experiment with different methods."
    
    def get_recommendations_for_task(self, task_type: str, context: str = "") -> Dict:
        """
        Get recommendations for a specific task type.
        
        Returns:
            Dictionary with best practices, warnings, and suggestions
        """
        recommendations = {
            "task_type": task_type,
            "best_practices": [],
            "warnings": [],
            "success_rate": 0,
            "average_duration": 0,
            "recommended_tools": [],
            "avoid_tools": []
        }
        
        # Get best practices
        relevant_practices = [
            bp for bp in self.best_practices
            if bp['task_type'] == task_type
        ]
        recommendations['best_practices'] = relevant_practices
        
        # Get warnings from anti-patterns
        relevant_anti_patterns = [
            ap for ap in self.anti_patterns
            if ap['task_type'] == task_type
        ]
        recommendations['warnings'] = [
            {
                "warning": ap['title'],
                "prevention": ap['prevention'],
                "severity": ap['severity']
            }
            for ap in relevant_anti_patterns
        ]
        
        # Calculate success rate
        task_successes = [s for s in self.successes if s['task_type'] == task_type]
        task_failures = [f for f in self.failures if f['task_type'] == task_type]
        total = len(task_successes) + len(task_failures)
        
        if total > 0:
            recommendations['success_rate'] = len(task_successes) / total
        
        # Calculate average duration
        if task_successes:
            durations = [s.get('duration', 0) for s in task_successes if s.get('duration', 0) > 0]
            if durations:
                recommendations['average_duration'] = sum(durations) / len(durations)
        
        # Recommend tools
        success_tools = []
        for s in task_successes:
            success_tools.extend(s.get('tools_used', []))
        
        if success_tools:
            tool_counts = Counter(success_tools)
            recommendations['recommended_tools'] = [
                {"tool": tool, "success_count": count}
                for tool, count in tool_counts.most_common(5)
            ]
        
        # Tools to avoid
        failure_tools = []
        for f in task_failures:
            failure_tools.extend(f.get('tools_used', []))
        
        if failure_tools:
            # Tools that appear more in failures than successes
            failure_counts = Counter(failure_tools)
            success_counts = Counter(success_tools)
            
            avoid = []
            for tool, fail_count in failure_counts.items():
                success_count = success_counts.get(tool, 0)
                if fail_count > success_count:
                    avoid.append({"tool": tool, "failure_count": fail_count})
            
            recommendations['avoid_tools'] = avoid
        
        return recommendations
    
    def analyze_performance_trends(self, days: int = 30) -> Dict:
        """
        Analyze performance trends over time.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dictionary with trend analysis
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter recent data
        recent_successes = [
            s for s in self.successes
            if datetime.fromisoformat(s['timestamp']) > cutoff_date
        ]
        recent_failures = [
            f for f in self.failures
            if datetime.fromisoformat(f['timestamp']) > cutoff_date
        ]
        
        total = len(recent_successes) + len(recent_failures)
        
        trends = {
            "period_days": days,
            "total_tasks": total,
            "successes": len(recent_successes),
            "failures": len(recent_failures),
            "success_rate": len(recent_successes) / total if total > 0 else 0,
            "improvement_areas": [],
            "declining_areas": [],
            "most_successful_tasks": [],
            "most_problematic_tasks": []
        }
        
        # Analyze by task type
        task_performance = defaultdict(lambda: {'success': 0, 'failure': 0})
        
        for s in recent_successes:
            task_performance[s['task_type']]['success'] += 1
        
        for f in recent_failures:
            task_performance[f['task_type']]['failure'] += 1
        
        # Identify most successful and problematic tasks
        for task_type, counts in task_performance.items():
            total_task = counts['success'] + counts['failure']
            success_rate = counts['success'] / total_task if total_task > 0 else 0
            
            if success_rate >= 0.8 and total_task >= 3:
                trends['most_successful_tasks'].append({
                    "task_type": task_type,
                    "success_rate": success_rate,
                    "total_attempts": total_task
                })
            elif success_rate <= 0.5 and total_task >= 3:
                trends['most_problematic_tasks'].append({
                    "task_type": task_type,
                    "success_rate": success_rate,
                    "total_attempts": total_task
                })
        
        return trends
    
    def get_lessons_learned(self, applied_only: bool = False) -> List[Dict]:
        """Get all lessons learned, optionally filtered by applied status."""
        if applied_only:
            return [l for l in self.lessons if l.get('applied', False)]
        return self.lessons
    
    def mark_lesson_applied(self, lesson_id: str):
        """Mark a lesson as applied/implemented."""
        for lesson in self.lessons:
            if lesson['id'] == lesson_id:
                lesson['applied'] = True
                lesson['applied_at'] = datetime.now().isoformat()
                self._save_json(self.lessons_file, self.lessons)
                return True
        return False
    
    def get_statistics(self) -> Dict:
        """Get overall statistics."""
        total = len(self.successes) + len(self.failures)
        
        stats = {
            "total_tasks": total,
            "total_successes": len(self.successes),
            "total_failures": len(self.failures),
            "overall_success_rate": len(self.successes) / total if total > 0 else 0,
            "best_practices_identified": len(self.best_practices),
            "anti_patterns_identified": len(self.anti_patterns),
            "lessons_learned": len(self.lessons),
            "lessons_applied": len([l for l in self.lessons if l.get('applied', False)]),
            "most_common_success_type": None,
            "most_common_failure_type": None
        }
        
        # Most common success type
        if self.successes:
            success_types = Counter([s['task_type'] for s in self.successes])
            stats['most_common_success_type'] = success_types.most_common(1)[0][0]
        
        # Most common failure type
        if self.failures:
            failure_types = Counter([f['task_type'] for f in self.failures])
            stats['most_common_failure_type'] = failure_types.most_common(1)[0][0]
        
        return stats
    
    def export_knowledge_base(self) -> Dict:
        """Export all learned knowledge for sharing or backup."""
        return {
            "exported_at": datetime.now().isoformat(),
            "statistics": self.get_statistics(),
            "best_practices": self.best_practices,
            "anti_patterns": self.anti_patterns,
            "lessons_learned": self.lessons,
            "success_count": len(self.successes),
            "failure_count": len(self.failures)
        }
    
    def import_knowledge_base(self, knowledge_base: Dict):
        """Import knowledge from another system or backup."""
        if 'best_practices' in knowledge_base:
            self.best_practices.extend(knowledge_base['best_practices'])
            self._save_json(self.best_practices_file, self.best_practices)
        
        if 'anti_patterns' in knowledge_base:
            self.anti_patterns.extend(knowledge_base['anti_patterns'])
            self._save_json(self.anti_patterns_file, self.anti_patterns)
        
        if 'lessons_learned' in knowledge_base:
            self.lessons.extend(knowledge_base['lessons_learned'])
            self._save_json(self.lessons_file, self.lessons)


def main():
    """Test the success/failure learning system."""
    print("🎓 Success/Failure Learning System Test")
    print("=" * 50)
    
    # Initialize system
    system = SuccessFailureLearningSystem()
    
    # Record some successes
    print("\n📝 Recording successes...")
    
    success1 = system.record_success({
        "task_type": "file_organization",
        "description": "Organized project files into proper structure",
        "tools_used": ["finder", "terminal"],
        "duration": 180,
        "context": "vy-nexus project",
        "key_factors": ["clear_naming", "logical_structure", "documentation"],
        "efficiency_score": 0.9,
        "user_satisfaction": 0.95
    })
    print(f"  ✅ Success recorded: {success1}")
    
    success2 = system.record_success({
        "task_type": "file_organization",
        "description": "Cleaned up duplicate files",
        "tools_used": ["terminal", "python_script"],
        "duration": 240,
        "context": "duplicate cleanup",
        "key_factors": ["clear_naming", "logical_structure", "automated_checks"],
        "efficiency_score": 0.85,
        "user_satisfaction": 0.9
    })
    print(f"  ✅ Success recorded: {success2}")
    
    # Record some failures
    print("\n📝 Recording failures...")
    
    failure1 = system.record_failure({
        "task_type": "code_execution",
        "description": "Attempted to run Python script",
        "tools_used": ["terminal"],
        "error_type": "module_not_found",
        "error_message": "No module named 'requests'",
        "context": "data processing script",
        "root_cause": "Missing dependency",
        "attempted_solutions": ["direct_execution"],
        "severity": "medium"
    })
    print(f"  ❌ Failure recorded: {failure1}")
    
    failure2 = system.record_failure({
        "task_type": "code_execution",
        "description": "Attempted to run another script",
        "tools_used": ["terminal"],
        "error_type": "module_not_found",
        "error_message": "No module named 'pandas'",
        "context": "data analysis",
        "root_cause": "Missing dependency",
        "attempted_solutions": ["direct_execution"],
        "severity": "medium"
    })
    print(f"  ❌ Failure recorded: {failure2}")
    
    # Get recommendations
    print("\n💡 Getting recommendations for file_organization...")
    recommendations = system.get_recommendations_for_task("file_organization")
    print(f"  Success rate: {recommendations['success_rate']:.1%}")
    print(f"  Best practices: {len(recommendations['best_practices'])}")
    print(f"  Recommended tools: {len(recommendations['recommended_tools'])}")
    
    # Analyze trends
    print("\n📊 Analyzing performance trends...")
    trends = system.analyze_performance_trends(days=30)
    print(f"  Total tasks: {trends['total_tasks']}")
    print(f"  Success rate: {trends['success_rate']:.1%}")
    print(f"  Most successful tasks: {len(trends['most_successful_tasks'])}")
    print(f"  Most problematic tasks: {len(trends['most_problematic_tasks'])}")
    
    # Get statistics
    print("\n📈 Overall Statistics:")
    stats = system.get_statistics()
    print(f"  Total tasks: {stats['total_tasks']}")
    print(f"  Successes: {stats['total_successes']}")
    print(f"  Failures: {stats['total_failures']}")
    print(f"  Success rate: {stats['overall_success_rate']:.1%}")
    print(f"  Best practices: {stats['best_practices_identified']}")
    print(f"  Anti-patterns: {stats['anti_patterns_identified']}")
    print(f"  Lessons learned: {stats['lessons_learned']}")
    
    print("\n✅ Success/Failure learning system is operational!")


if __name__ == "__main__":
    main()
