#!/usr/bin/env python3
"""
Pattern Recognition System
Part of the Self-Evolving AI Ecosystem

This module identifies patterns in user behavior, task execution,
and system performance to enable predictive optimization.
"""

import json
import os
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import Dict, List, Any, Tuple
import re


class PatternRecognitionSystem:
    """Identifies and analyzes patterns in user interactions and system behavior."""
    
    def __init__(self, data_dir: str = None):
        """Initialize the pattern recognition system."""
        if data_dir is None:
            data_dir = os.path.expanduser("~/vy-nexus/data/patterns")
        
        self.data_dir = data_dir
        self.patterns_file = os.path.join(data_dir, "recognized_patterns.json")
        self.insights_file = os.path.join(data_dir, "pattern_insights.json")
        
        # Create directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Load existing patterns
        self.patterns = self._load_patterns()
        self.insights = self._load_insights()
    
    def _load_patterns(self) -> Dict:
        """Load existing patterns from file."""
        if os.path.exists(self.patterns_file):
            try:
                with open(self.patterns_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading patterns: {e}")
        
        return {
            "temporal_patterns": [],
            "task_sequences": [],
            "tool_usage_patterns": [],
            "workflow_patterns": [],
            "error_patterns": [],
            "success_patterns": []
        }
    
    def _load_insights(self) -> Dict:
        """Load existing insights from file."""
        if os.path.exists(self.insights_file):
            try:
                with open(self.insights_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading insights: {e}")
        
        return {
            "predictions": [],
            "recommendations": [],
            "anomalies": [],
            "trends": []
        }
    
    def _save_patterns(self):
        """Save patterns to file."""
        try:
            with open(self.patterns_file, 'w') as f:
                json.dump(self.patterns, f, indent=2)
        except Exception as e:
            print(f"Error saving patterns: {e}")
    
    def _save_insights(self):
        """Save insights to file."""
        try:
            with open(self.insights_file, 'w') as f:
                json.dump(self.insights, f, indent=2)
        except Exception as e:
            print(f"Error saving insights: {e}")
    
    def analyze_temporal_patterns(self, interactions: List[Dict]) -> List[Dict]:
        """
        Analyze temporal patterns in user interactions.
        
        Identifies:
        - Peak activity hours
        - Day-of-week patterns
        - Task timing preferences
        - Session duration patterns
        """
        if not interactions:
            return []
        
        # Group by hour of day
        hourly_activity = defaultdict(int)
        daily_activity = defaultdict(int)
        task_timing = defaultdict(list)
        
        for interaction in interactions:
            timestamp = interaction.get('timestamp', '')
            if not timestamp:
                continue
            
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                hour = dt.hour
                day = dt.strftime('%A')
                
                hourly_activity[hour] += 1
                daily_activity[day] += 1
                
                task_type = interaction.get('task_type', 'unknown')
                task_timing[task_type].append(hour)
            except Exception as e:
                continue
        
        # Identify peak hours
        peak_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_days = sorted(daily_activity.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Analyze task timing preferences
        task_preferences = {}
        for task_type, hours in task_timing.items():
            if len(hours) >= 3:
                avg_hour = sum(hours) / len(hours)
                task_preferences[task_type] = {
                    "preferred_hour": round(avg_hour, 1),
                    "occurrences": len(hours)
                }
        
        temporal_pattern = {
            "pattern_type": "temporal",
            "identified_at": datetime.now().isoformat(),
            "peak_hours": [f"{h}:00" for h, _ in peak_hours],
            "peak_days": [d for d, _ in peak_days],
            "task_timing_preferences": task_preferences,
            "total_interactions": len(interactions)
        }
        
        # Add to patterns
        self.patterns["temporal_patterns"].append(temporal_pattern)
        self._save_patterns()
        
        return [temporal_pattern]
    
    def analyze_task_sequences(self, interactions: List[Dict]) -> List[Dict]:
        """
        Identify common sequences of tasks.
        
        Finds:
        - Frequently occurring task chains
        - Task dependencies
        - Workflow sequences
        """
        if len(interactions) < 2:
            return []
        
        # Extract task sequences
        sequences = []
        for i in range(len(interactions) - 1):
            task1 = interactions[i].get('task_type', 'unknown')
            task2 = interactions[i + 1].get('task_type', 'unknown')
            sequences.append((task1, task2))
        
        # Count sequence frequencies
        sequence_counts = Counter(sequences)
        common_sequences = sequence_counts.most_common(10)
        
        # Identify 3-task sequences
        three_task_sequences = []
        for i in range(len(interactions) - 2):
            task1 = interactions[i].get('task_type', 'unknown')
            task2 = interactions[i + 1].get('task_type', 'unknown')
            task3 = interactions[i + 2].get('task_type', 'unknown')
            three_task_sequences.append((task1, task2, task3))
        
        three_task_counts = Counter(three_task_sequences)
        common_three_task = three_task_counts.most_common(5)
        
        sequence_pattern = {
            "pattern_type": "task_sequence",
            "identified_at": datetime.now().isoformat(),
            "common_pairs": [
                {"sequence": f"{s[0]} → {s[1]}", "count": c}
                for s, c in common_sequences if c >= 2
            ],
            "common_triplets": [
                {"sequence": f"{s[0]} → {s[1]} → {s[2]}", "count": c}
                for s, c in common_three_task if c >= 2
            ]
        }
        
        self.patterns["task_sequences"].append(sequence_pattern)
        self._save_patterns()
        
        return [sequence_pattern]
    
    def analyze_tool_usage(self, interactions: List[Dict]) -> List[Dict]:
        """
        Analyze patterns in tool and application usage.
        
        Identifies:
        - Most frequently used tools
        - Tool combinations
        - Tool preferences by task type
        """
        if not interactions:
            return []
        
        tool_usage = defaultdict(int)
        tool_by_task = defaultdict(lambda: defaultdict(int))
        tool_combinations = []
        
        for interaction in interactions:
            tools = interaction.get('tools_used', [])
            task_type = interaction.get('task_type', 'unknown')
            
            for tool in tools:
                tool_usage[tool] += 1
                tool_by_task[task_type][tool] += 1
            
            # Track tool combinations
            if len(tools) >= 2:
                tool_combinations.append(tuple(sorted(tools)))
        
        # Find most common tools
        top_tools = Counter(tool_usage).most_common(10)
        
        # Find common tool combinations
        common_combos = Counter(tool_combinations).most_common(5)
        
        # Analyze tool preferences by task
        task_tool_preferences = {}
        for task_type, tools in tool_by_task.items():
            if sum(tools.values()) >= 3:
                top_task_tools = sorted(tools.items(), key=lambda x: x[1], reverse=True)[:3]
                task_tool_preferences[task_type] = [
                    {"tool": tool, "usage_count": count}
                    for tool, count in top_task_tools
                ]
        
        tool_pattern = {
            "pattern_type": "tool_usage",
            "identified_at": datetime.now().isoformat(),
            "top_tools": [{"tool": t, "count": c} for t, c in top_tools],
            "common_combinations": [
                {"tools": list(combo), "count": c}
                for combo, c in common_combos if c >= 2
            ],
            "task_preferences": task_tool_preferences
        }
        
        self.patterns["tool_usage_patterns"].append(tool_pattern)
        self._save_patterns()
        
        return [tool_pattern]
    
    def analyze_workflow_patterns(self, interactions: List[Dict]) -> List[Dict]:
        """
        Identify recurring workflow patterns.
        
        Finds:
        - Complete workflow sequences
        - Workflow variations
        - Optimization opportunities
        """
        if len(interactions) < 3:
            return []
        
        # Group interactions by session (within 1 hour)
        sessions = []
        current_session = []
        
        for i, interaction in enumerate(interactions):
            if not current_session:
                current_session.append(interaction)
            else:
                last_time = datetime.fromisoformat(
                    current_session[-1].get('timestamp', '').replace('Z', '+00:00')
                )
                current_time = datetime.fromisoformat(
                    interaction.get('timestamp', '').replace('Z', '+00:00')
                )
                
                if (current_time - last_time).total_seconds() <= 3600:
                    current_session.append(interaction)
                else:
                    if len(current_session) >= 3:
                        sessions.append(current_session)
                    current_session = [interaction]
        
        if len(current_session) >= 3:
            sessions.append(current_session)
        
        # Analyze session patterns
        workflow_signatures = []
        for session in sessions:
            signature = " → ".join([i.get('task_type', 'unknown') for i in session])
            workflow_signatures.append(signature)
        
        common_workflows = Counter(workflow_signatures).most_common(5)
        
        workflow_pattern = {
            "pattern_type": "workflow",
            "identified_at": datetime.now().isoformat(),
            "common_workflows": [
                {"workflow": wf, "occurrences": c}
                for wf, c in common_workflows if c >= 2
            ],
            "total_sessions": len(sessions)
        }
        
        self.patterns["workflow_patterns"].append(workflow_pattern)
        self._save_patterns()
        
        return [workflow_pattern]
    
    def analyze_error_patterns(self, interactions: List[Dict]) -> List[Dict]:
        """
        Identify patterns in errors and failures.
        
        Finds:
        - Common error types
        - Error triggers
        - Error contexts
        """
        errors = [i for i in interactions if i.get('status') == 'error']
        
        if not errors:
            return []
        
        error_types = defaultdict(int)
        error_contexts = defaultdict(list)
        
        for error in errors:
            error_type = error.get('error_type', 'unknown')
            task_type = error.get('task_type', 'unknown')
            
            error_types[error_type] += 1
            error_contexts[error_type].append(task_type)
        
        common_errors = sorted(error_types.items(), key=lambda x: x[1], reverse=True)
        
        error_pattern = {
            "pattern_type": "error",
            "identified_at": datetime.now().isoformat(),
            "common_errors": [
                {
                    "error_type": err,
                    "count": count,
                    "contexts": list(set(error_contexts[err]))
                }
                for err, count in common_errors
            ],
            "total_errors": len(errors),
            "error_rate": len(errors) / len(interactions) if interactions else 0
        }
        
        self.patterns["error_patterns"].append(error_pattern)
        self._save_patterns()
        
        return [error_pattern]
    
    def analyze_success_patterns(self, interactions: List[Dict]) -> List[Dict]:
        """
        Identify patterns in successful task completions.
        
        Finds:
        - Success factors
        - Optimal approaches
        - Best practices
        """
        successes = [i for i in interactions if i.get('status') == 'success']
        
        if not successes:
            return []
        
        success_by_task = defaultdict(int)
        success_tools = defaultdict(int)
        success_durations = defaultdict(list)
        
        for success in successes:
            task_type = success.get('task_type', 'unknown')
            tools = success.get('tools_used', [])
            duration = success.get('duration', 0)
            
            success_by_task[task_type] += 1
            for tool in tools:
                success_tools[tool] += 1
            
            if duration > 0:
                success_durations[task_type].append(duration)
        
        # Calculate average durations
        avg_durations = {}
        for task_type, durations in success_durations.items():
            if durations:
                avg_durations[task_type] = sum(durations) / len(durations)
        
        success_pattern = {
            "pattern_type": "success",
            "identified_at": datetime.now().isoformat(),
            "success_by_task": dict(success_by_task),
            "effective_tools": [
                {"tool": tool, "success_count": count}
                for tool, count in sorted(success_tools.items(), key=lambda x: x[1], reverse=True)[:10]
            ],
            "average_durations": avg_durations,
            "total_successes": len(successes),
            "success_rate": len(successes) / len(interactions) if interactions else 0
        }
        
        self.patterns["success_patterns"].append(success_pattern)
        self._save_patterns()
        
        return [success_pattern]
    
    def generate_predictions(self) -> List[Dict]:
        """
        Generate predictions based on identified patterns.
        
        Predicts:
        - Likely next tasks
        - Optimal timing for tasks
        - Resource requirements
        """
        predictions = []
        
        # Predict based on temporal patterns
        if self.patterns["temporal_patterns"]:
            latest_temporal = self.patterns["temporal_patterns"][-1]
            peak_hours = latest_temporal.get("peak_hours", [])
            
            if peak_hours:
                predictions.append({
                    "type": "temporal",
                    "prediction": f"User is most active during {', '.join(peak_hours)}",
                    "confidence": "high",
                    "recommendation": "Schedule important tasks during peak hours"
                })
        
        # Predict based on task sequences
        if self.patterns["task_sequences"]:
            latest_sequences = self.patterns["task_sequences"][-1]
            common_pairs = latest_sequences.get("common_pairs", [])
            
            if common_pairs:
                top_sequence = common_pairs[0]
                predictions.append({
                    "type": "task_sequence",
                    "prediction": f"Common task sequence: {top_sequence['sequence']}",
                    "confidence": "medium",
                    "recommendation": "Prepare resources for the next task in sequence"
                })
        
        # Save predictions
        self.insights["predictions"] = predictions
        self._save_insights()
        
        return predictions
    
    def generate_recommendations(self) -> List[Dict]:
        """
        Generate actionable recommendations based on patterns.
        """
        recommendations = []
        
        # Recommendations from tool usage
        if self.patterns["tool_usage_patterns"]:
            latest_tools = self.patterns["tool_usage_patterns"][-1]
            top_tools = latest_tools.get("top_tools", [])
            
            if len(top_tools) >= 3:
                recommendations.append({
                    "category": "tool_optimization",
                    "recommendation": f"Create shortcuts for frequently used tools: {', '.join([t['tool'] for t in top_tools[:3]])}",
                    "priority": "high",
                    "estimated_impact": "20% time savings"
                })
        
        # Recommendations from error patterns
        if self.patterns["error_patterns"]:
            latest_errors = self.patterns["error_patterns"][-1]
            common_errors = latest_errors.get("common_errors", [])
            
            if common_errors:
                top_error = common_errors[0]
                recommendations.append({
                    "category": "error_prevention",
                    "recommendation": f"Implement safeguards for {top_error['error_type']} errors",
                    "priority": "high",
                    "estimated_impact": "Reduce errors by 30%"
                })
        
        # Recommendations from workflow patterns
        if self.patterns["workflow_patterns"]:
            latest_workflows = self.patterns["workflow_patterns"][-1]
            common_workflows = latest_workflows.get("common_workflows", [])
            
            if common_workflows:
                recommendations.append({
                    "category": "workflow_automation",
                    "recommendation": "Create automation for recurring workflows",
                    "priority": "medium",
                    "estimated_impact": "40% time savings on repeated tasks"
                })
        
        # Save recommendations
        self.insights["recommendations"] = recommendations
        self._save_insights()
        
        return recommendations
    
    def detect_anomalies(self, interactions: List[Dict]) -> List[Dict]:
        """
        Detect anomalous behavior or patterns.
        
        Identifies:
        - Unusual task durations
        - Unexpected error spikes
        - Abnormal usage patterns
        """
        anomalies = []
        
        if not interactions:
            return anomalies
        
        # Check for unusual durations
        durations = [i.get('duration', 0) for i in interactions if i.get('duration', 0) > 0]
        if durations:
            avg_duration = sum(durations) / len(durations)
            for interaction in interactions:
                duration = interaction.get('duration', 0)
                if duration > avg_duration * 3:
                    anomalies.append({
                        "type": "duration_anomaly",
                        "description": f"Task took 3x longer than average",
                        "task": interaction.get('task_type', 'unknown'),
                        "duration": duration,
                        "average": avg_duration
                    })
        
        # Check for error spikes
        recent_errors = [i for i in interactions[-20:] if i.get('status') == 'error']
        if len(recent_errors) > 5:
            anomalies.append({
                "type": "error_spike",
                "description": "Unusual number of errors in recent interactions",
                "error_count": len(recent_errors),
                "threshold": 5
            })
        
        # Save anomalies
        self.insights["anomalies"] = anomalies
        self._save_insights()
        
        return anomalies
    
    def analyze_all_patterns(self, interactions: List[Dict]) -> Dict:
        """
        Run all pattern analysis methods and generate comprehensive insights.
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_interactions": len(interactions),
            "patterns": {},
            "insights": {}
        }
        
        # Run all analyses
        results["patterns"]["temporal"] = self.analyze_temporal_patterns(interactions)
        results["patterns"]["sequences"] = self.analyze_task_sequences(interactions)
        results["patterns"]["tools"] = self.analyze_tool_usage(interactions)
        results["patterns"]["workflows"] = self.analyze_workflow_patterns(interactions)
        results["patterns"]["errors"] = self.analyze_error_patterns(interactions)
        results["patterns"]["successes"] = self.analyze_success_patterns(interactions)
        
        # Generate insights
        results["insights"]["predictions"] = self.generate_predictions()
        results["insights"]["recommendations"] = self.generate_recommendations()
        results["insights"]["anomalies"] = self.detect_anomalies(interactions)
        
        return results
    
    def get_pattern_summary(self) -> Dict:
        """Get a summary of all recognized patterns."""
        summary = {
            "total_patterns": sum(len(v) for v in self.patterns.values()),
            "pattern_types": {
                k: len(v) for k, v in self.patterns.items()
            },
            "latest_insights": {
                "predictions": len(self.insights.get("predictions", [])),
                "recommendations": len(self.insights.get("recommendations", [])),
                "anomalies": len(self.insights.get("anomalies", []))
            }
        }
        return summary


def main():
    """Test the pattern recognition system."""
    print("🔍 Pattern Recognition System Test")
    print("=" * 50)
    
    # Initialize system
    system = PatternRecognitionSystem()
    
    # Create sample interactions
    sample_interactions = [
        {
            "timestamp": "2025-12-15T09:00:00",
            "task_type": "file_management",
            "tools_used": ["finder", "terminal"],
            "status": "success",
            "duration": 120
        },
        {
            "timestamp": "2025-12-15T09:15:00",
            "task_type": "code_analysis",
            "tools_used": ["terminal", "text_editor"],
            "status": "success",
            "duration": 300
        },
        {
            "timestamp": "2025-12-15T09:30:00",
            "task_type": "file_management",
            "tools_used": ["finder"],
            "status": "success",
            "duration": 90
        },
        {
            "timestamp": "2025-12-15T10:00:00",
            "task_type": "code_analysis",
            "tools_used": ["terminal"],
            "status": "error",
            "error_type": "file_not_found",
            "duration": 60
        },
        {
            "timestamp": "2025-12-15T14:00:00",
            "task_type": "documentation",
            "tools_used": ["text_editor"],
            "status": "success",
            "duration": 600
        }
    ]
    
    # Analyze patterns
    print("\n📊 Analyzing patterns...")
    results = system.analyze_all_patterns(sample_interactions)
    
    print(f"\n✅ Analysis complete!")
    print(f"Total interactions analyzed: {results['total_interactions']}")
    
    # Display summary
    summary = system.get_pattern_summary()
    print(f"\n📈 Pattern Summary:")
    print(f"Total patterns identified: {summary['total_patterns']}")
    for pattern_type, count in summary['pattern_types'].items():
        print(f"  - {pattern_type}: {count}")
    
    print(f"\n💡 Insights Generated:")
    print(f"  - Predictions: {summary['latest_insights']['predictions']}")
    print(f"  - Recommendations: {summary['latest_insights']['recommendations']}")
    print(f"  - Anomalies: {summary['latest_insights']['anomalies']}")
    
    print("\n✅ Pattern recognition system is operational!")


if __name__ == "__main__":
    main()
