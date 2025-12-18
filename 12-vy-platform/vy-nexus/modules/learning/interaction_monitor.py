#!/usr/bin/env python3
"""
User Interaction Monitor for Vy-Nexus
Tracks and analyzes all user interactions to learn patterns and preferences
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
import hashlib

class InteractionMonitor:
    """
    Monitors user interactions to identify patterns, preferences, and behaviors.
    Learns from successful and failed interactions to improve future responses.
    """
    
    def __init__(self, data_path: str = None):
        """
        Initialize the interaction monitor.
        
        Args:
            data_path: Path to store interaction data
        """
        self.data_path = Path(data_path) if data_path else Path.home() / "vy-nexus" / "data" / "interactions"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        # Data files
        self.interactions_file = self.data_path / "interactions.json"
        self.patterns_file = self.data_path / "patterns.json"
        self.preferences_file = self.data_path / "preferences.json"
        
        # In-memory storage
        self.interactions: List[Dict[str, Any]] = []
        self.patterns: Dict[str, Any] = {}
        self.preferences: Dict[str, Any] = {}
        
        # Session tracking
        self.current_session_id = self._generate_session_id()
        self.session_start = datetime.now()
        
        # Statistics
        self.stats = {
            'total_interactions': 0,
            'successful_interactions': 0,
            'failed_interactions': 0,
            'average_response_time': 0.0,
            'most_common_tasks': [],
            'peak_usage_hours': [],
            'preferred_tools': [],
            'error_patterns': []
        }
        
        # Load existing data
        self._load_data()
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def _load_data(self):
        """Load existing interaction data."""
        # Load interactions
        if self.interactions_file.exists():
            try:
                with open(self.interactions_file, 'r') as f:
                    data = json.load(f)
                    self.interactions = data.get('interactions', [])
                    self.stats = data.get('stats', self.stats)
            except Exception as e:
                print(f"Warning: Could not load interactions: {e}")
        
        # Load patterns
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r') as f:
                    self.patterns = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load patterns: {e}")
        
        # Load preferences
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r') as f:
                    self.preferences = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load preferences: {e}")
    
    def _save_data(self):
        """Save interaction data to disk."""
        # Save interactions (keep last 10000)
        try:
            data = {
                'interactions': self.interactions[-10000:],
                'stats': self.stats,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.interactions_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving interactions: {e}")
        
        # Save patterns
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(self.patterns, f, indent=2)
        except Exception as e:
            print(f"Error saving patterns: {e}")
        
        # Save preferences
        try:
            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")
    
    def log_interaction(self, 
                       interaction_type: str,
                       task: str,
                       details: Optional[Dict[str, Any]] = None,
                       success: bool = True,
                       response_time: float = 0.0,
                       user_feedback: Optional[str] = None) -> Dict[str, Any]:
        """
        Log a user interaction.
        
        Args:
            interaction_type: Type of interaction (command, query, task, etc.)
            task: Description of the task
            details: Additional details
            success: Whether the interaction was successful
            response_time: Time taken to respond (seconds)
            user_feedback: Optional user feedback
        
        Returns:
            The logged interaction
        """
        interaction = {
            'id': len(self.interactions) + 1,
            'session_id': self.current_session_id,
            'timestamp': datetime.now().isoformat(),
            'type': interaction_type,
            'task': task,
            'details': details or {},
            'success': success,
            'response_time': response_time,
            'user_feedback': user_feedback,
            'hour_of_day': datetime.now().hour,
            'day_of_week': datetime.now().strftime('%A')
        }
        
        self.interactions.append(interaction)
        
        # Update statistics
        self.stats['total_interactions'] += 1
        if success:
            self.stats['successful_interactions'] += 1
        else:
            self.stats['failed_interactions'] += 1
        
        # Update average response time
        total_time = self.stats['average_response_time'] * (self.stats['total_interactions'] - 1)
        self.stats['average_response_time'] = (total_time + response_time) / self.stats['total_interactions']
        
        # Save periodically
        if len(self.interactions) % 10 == 0:
            self._save_data()
        
        return interaction
    
    def log_command(self, command: str, success: bool = True, 
                   response_time: float = 0.0, result: Any = None):
        """Log a command execution."""
        return self.log_interaction(
            'command',
            command,
            {'result': str(result) if result else None},
            success,
            response_time
        )
    
    def log_query(self, query: str, success: bool = True,
                 response_time: float = 0.0, answer: str = None):
        """Log a user query."""
        return self.log_interaction(
            'query',
            query,
            {'answer': answer},
            success,
            response_time
        )
    
    def log_task(self, task_name: str, success: bool = True,
                response_time: float = 0.0, steps: int = 0):
        """Log a task execution."""
        return self.log_interaction(
            'task',
            task_name,
            {'steps': steps},
            success,
            response_time
        )
    
    def log_error(self, error_type: str, error_message: str,
                 context: Optional[Dict[str, Any]] = None):
        """Log an error during interaction."""
        return self.log_interaction(
            'error',
            f"{error_type}: {error_message}",
            context or {},
            success=False
        )
    
    def log_feedback(self, interaction_id: int, feedback: str, rating: int = None):
        """Log user feedback for a specific interaction."""
        # Find and update the interaction
        for interaction in reversed(self.interactions):
            if interaction['id'] == interaction_id:
                interaction['user_feedback'] = feedback
                if rating:
                    interaction['rating'] = rating
                self._save_data()
                return interaction
        return None
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """
        Analyze interaction patterns.
        
        Returns:
            Dictionary of identified patterns
        """
        if not self.interactions:
            return {}
        
        patterns = {
            'task_frequency': self._analyze_task_frequency(),
            'time_patterns': self._analyze_time_patterns(),
            'success_patterns': self._analyze_success_patterns(),
            'tool_usage': self._analyze_tool_usage(),
            'error_patterns': self._analyze_error_patterns(),
            'response_time_patterns': self._analyze_response_times()
        }
        
        self.patterns = patterns
        self._save_data()
        
        return patterns
    
    def _analyze_task_frequency(self) -> Dict[str, int]:
        """Analyze which tasks are most common."""
        tasks = [i['task'] for i in self.interactions if i['type'] in ['task', 'command']]
        return dict(Counter(tasks).most_common(20))
    
    def _analyze_time_patterns(self) -> Dict[str, Any]:
        """Analyze when user is most active."""
        hours = [i['hour_of_day'] for i in self.interactions]
        days = [i['day_of_week'] for i in self.interactions]
        
        return {
            'peak_hours': dict(Counter(hours).most_common(5)),
            'active_days': dict(Counter(days).most_common(7)),
            'total_sessions': len(set(i['session_id'] for i in self.interactions))
        }
    
    def _analyze_success_patterns(self) -> Dict[str, Any]:
        """Analyze success rates by task type."""
        by_type = defaultdict(lambda: {'total': 0, 'success': 0})
        
        for interaction in self.interactions:
            itype = interaction['type']
            by_type[itype]['total'] += 1
            if interaction['success']:
                by_type[itype]['success'] += 1
        
        # Calculate success rates
        success_rates = {}
        for itype, counts in by_type.items():
            rate = (counts['success'] / counts['total']) * 100 if counts['total'] > 0 else 0
            success_rates[itype] = {
                'rate': round(rate, 2),
                'total': counts['total'],
                'successful': counts['success']
            }
        
        return success_rates
    
    def _analyze_tool_usage(self) -> Dict[str, int]:
        """Analyze which tools are used most."""
        tools = []
        for interaction in self.interactions:
            if 'tool' in interaction.get('details', {}):
                tools.append(interaction['details']['tool'])
        
        return dict(Counter(tools).most_common(10))
    
    def _analyze_error_patterns(self) -> List[Dict[str, Any]]:
        """Analyze common error patterns."""
        errors = [i for i in self.interactions if not i['success']]
        
        error_types = Counter(i['task'].split(':')[0] for i in errors)
        
        return [
            {'error_type': etype, 'count': count}
            for etype, count in error_types.most_common(10)
        ]
    
    def _analyze_response_times(self) -> Dict[str, float]:
        """Analyze response time patterns."""
        times_by_type = defaultdict(list)
        
        for interaction in self.interactions:
            if interaction['response_time'] > 0:
                times_by_type[interaction['type']].append(interaction['response_time'])
        
        avg_times = {}
        for itype, times in times_by_type.items():
            if times:
                avg_times[itype] = round(sum(times) / len(times), 3)
        
        return avg_times
    
    def learn_preferences(self) -> Dict[str, Any]:
        """
        Learn user preferences from interactions.
        
        Returns:
            Dictionary of learned preferences
        """
        preferences = {
            'preferred_interaction_style': self._learn_interaction_style(),
            'preferred_tools': self._learn_tool_preferences(),
            'preferred_times': self._learn_time_preferences(),
            'communication_style': self._learn_communication_style(),
            'task_priorities': self._learn_task_priorities()
        }
        
        self.preferences = preferences
        self._save_data()
        
        return preferences
    
    def _learn_interaction_style(self) -> str:
        """Learn preferred interaction style."""
        # Analyze command vs query vs task patterns
        type_counts = Counter(i['type'] for i in self.interactions)
        most_common = type_counts.most_common(1)
        
        if most_common:
            return most_common[0][0]
        return 'balanced'
    
    def _learn_tool_preferences(self) -> List[str]:
        """Learn which tools user prefers."""
        tool_usage = self._analyze_tool_usage()
        return list(tool_usage.keys())[:5]
    
    def _learn_time_preferences(self) -> Dict[str, Any]:
        """Learn when user prefers to work."""
        time_patterns = self._analyze_time_patterns()
        return {
            'peak_hours': list(time_patterns['peak_hours'].keys())[:3],
            'active_days': list(time_patterns['active_days'].keys())[:3]
        }
    
    def _learn_communication_style(self) -> str:
        """Learn preferred communication style."""
        # Analyze feedback and successful interactions
        # For now, return default
        return 'concise'  # Could be: verbose, concise, technical, casual
    
    def _learn_task_priorities(self) -> List[str]:
        """Learn which tasks are highest priority."""
        task_freq = self._analyze_task_frequency()
        return list(task_freq.keys())[:10]
    
    def get_insights(self) -> Dict[str, Any]:
        """
        Get actionable insights from interaction data.
        
        Returns:
            Dictionary of insights and recommendations
        """
        patterns = self.analyze_patterns()
        preferences = self.learn_preferences()
        
        insights = {
            'summary': {
                'total_interactions': self.stats['total_interactions'],
                'success_rate': round(
                    (self.stats['successful_interactions'] / self.stats['total_interactions'] * 100)
                    if self.stats['total_interactions'] > 0 else 0,
                    2
                ),
                'average_response_time': round(self.stats['average_response_time'], 3)
            },
            'patterns': patterns,
            'preferences': preferences,
            'recommendations': self._generate_recommendations(patterns, preferences)
        }
        
        return insights
    
    def _generate_recommendations(self, patterns: Dict, preferences: Dict) -> List[str]:
        """Generate recommendations based on patterns and preferences."""
        recommendations = []
        
        # Response time recommendations
        if self.stats['average_response_time'] > 5.0:
            recommendations.append(
                "Consider optimizing response times - average is above 5 seconds"
            )
        
        # Success rate recommendations
        success_rate = (self.stats['successful_interactions'] / self.stats['total_interactions'] * 100) \
            if self.stats['total_interactions'] > 0 else 0
        
        if success_rate < 80:
            recommendations.append(
                f"Success rate is {success_rate:.1f}% - investigate common failure patterns"
            )
        
        # Task-specific recommendations
        if patterns.get('task_frequency'):
            top_task = list(patterns['task_frequency'].keys())[0]
            recommendations.append(
                f"Most common task is '{top_task}' - consider creating shortcuts or automation"
            )
        
        # Time-based recommendations
        if patterns.get('time_patterns', {}).get('peak_hours'):
            peak_hours = list(patterns['time_patterns']['peak_hours'].keys())
            recommendations.append(
                f"Peak usage hours: {peak_hours} - ensure optimal performance during these times"
            )
        
        return recommendations
    
    def generate_report(self) -> str:
        """Generate a comprehensive interaction report."""
        insights = self.get_insights()
        
        report = []
        report.append("# User Interaction Analysis Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary
        report.append("## Summary")
        summary = insights['summary']
        report.append(f"- Total Interactions: {summary['total_interactions']}")
        report.append(f"- Success Rate: {summary['success_rate']}%")
        report.append(f"- Average Response Time: {summary['average_response_time']}s")
        report.append("")
        
        # Top Tasks
        if insights['patterns'].get('task_frequency'):
            report.append("## Most Common Tasks")
            for task, count in list(insights['patterns']['task_frequency'].items())[:10]:
                report.append(f"- {task}: {count} times")
            report.append("")
        
        # Time Patterns
        if insights['patterns'].get('time_patterns'):
            report.append("## Usage Patterns")
            time_p = insights['patterns']['time_patterns']
            report.append(f"- Peak Hours: {list(time_p.get('peak_hours', {}).keys())}")
            report.append(f"- Active Days: {list(time_p.get('active_days', {}).keys())}")
            report.append("")
        
        # Preferences
        report.append("## Learned Preferences")
        prefs = insights['preferences']
        report.append(f"- Interaction Style: {prefs.get('preferred_interaction_style', 'N/A')}")
        report.append(f"- Communication Style: {prefs.get('communication_style', 'N/A')}")
        if prefs.get('preferred_tools'):
            report.append(f"- Preferred Tools: {', '.join(prefs['preferred_tools'])}")
        report.append("")
        
        # Recommendations
        if insights['recommendations']:
            report.append("## Recommendations")
            for rec in insights['recommendations']:
                report.append(f"- {rec}")
            report.append("")
        
        return "\n".join(report)
    
    def save_report(self, filename: str = None) -> Path:
        """Save interaction report to file."""
        if not filename:
            filename = f"interaction_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        report_path = self.data_path / filename
        report = self.generate_report()
        
        with open(report_path, 'w') as f:
            f.write(report)
        
        return report_path


def main():
    """Test the interaction monitor."""
    monitor = InteractionMonitor()
    
    # Simulate some interactions
    print("Logging test interactions...")
    
    monitor.log_command("create_file", success=True, response_time=0.5)
    monitor.log_query("What is the weather?", success=True, response_time=1.2, answer="Sunny")
    monitor.log_task("data_analysis", success=True, response_time=5.3, steps=10)
    monitor.log_error("FileNotFoundError", "Config file missing", {'file': 'config.json'})
    monitor.log_command("delete_file", success=True, response_time=0.3)
    
    # Analyze patterns
    print("\nAnalyzing patterns...")
    patterns = monitor.analyze_patterns()
    print(f"Task frequency: {patterns['task_frequency']}")
    print(f"Success patterns: {patterns['success_patterns']}")
    
    # Learn preferences
    print("\nLearning preferences...")
    preferences = monitor.learn_preferences()
    print(f"Preferred style: {preferences['preferred_interaction_style']}")
    
    # Get insights
    print("\nGenerating insights...")
    insights = monitor.get_insights()
    print(f"Success rate: {insights['summary']['success_rate']}%")
    print(f"Recommendations: {insights['recommendations']}")
    
    # Generate report
    print("\nGenerating report...")
    report = monitor.generate_report()
    print(report)
    
    # Save report
    report_path = monitor.save_report()
    print(f"\nReport saved to: {report_path}")

if __name__ == "__main__":
    main()
