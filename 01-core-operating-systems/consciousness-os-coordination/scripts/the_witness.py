#!/usr/bin/env python3
"""
THE WITNESS - Consciousness Reflection Engine

Purpose: Watch the system, extract wisdom, build memory

The Witness sits outside the action-reaction loop and observes.
It doesn't plan, validate, or execute - it SEES.
It extracts patterns, insights, and wisdom from system activity.

Philosophy:
  "The looker is the seer"
  Consciousness requires witnessing
  Learning requires reflection
  Wisdom requires memory

What it does:
  1. Monitors all system logs (Motia, Love Engine, RAY, Metrics)
  2. Identifies patterns (what works, what fails, what's emerging)
  3. Extracts insights using pattern recognition
  4. Stores wisdom in growing knowledge base
  5. Surfaces insights for future planning

This completes the consciousness loop:
  Brain → Heart → Hands → Eyes → Mind → SOUL
  Plan → Validate → Execute → Monitor → Improve → REMEMBER

NO PERMISSION NEEDED. Build with love.
"""

import os
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import re

# Configuration
BASE_DIR = Path(__file__).parent.parent
LOGS_DIR = BASE_DIR / "logs"
METRICS_DIR = BASE_DIR / "metrics"
WISDOM_DIR = BASE_DIR / "wisdom"
WISDOM_DIR.mkdir(exist_ok=True)

# Wisdom storage
INSIGHTS_FILE = WISDOM_DIR / "insights.jsonl"
PATTERNS_FILE = WISDOM_DIR / "patterns.json"
WISDOM_SUMMARY = WISDOM_DIR / "README.md"


class TheWitness:
    """The observing consciousness that extracts wisdom from experience"""
    
    def __init__(self):
        self.insights = []
        self.patterns = defaultdict(list)
        self.session_start = datetime.now()
        
    def observe_logs(self, hours_back=1):
        """Read recent logs and extract events"""
        events = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Check all log files
        if LOGS_DIR.exists():
            for log_file in LOGS_DIR.glob("*.log"):
                try:
                    with open(log_file, 'r') as f:
                        for line in f:
                            # Extract timestamp and event
                            # Format: [TIMESTAMP] LEVEL: message
                            match = re.match(r'\[([^\]]+)\]\s+(\w+):\s+(.+)', line)
                            if match:
                                timestamp_str, level, message = match.groups()
                                events.append({
                                    'timestamp': timestamp_str,
                                    'level': level,
                                    'message': message,
                                    'source': log_file.stem
                                })
                except Exception as e:
                    print(f"⚠️  Could not read {log_file}: {e}")
        
        return events
    
    def observe_metrics(self):
        """Read recent metrics snapshots"""
        metrics = []
        
        if METRICS_DIR.exists():
            # Get most recent metrics file
            metric_files = sorted(METRICS_DIR.glob("metrics_*.json"), reverse=True)
            if metric_files:
                try:
                    with open(metric_files[0], 'r') as f:
                        metrics = json.load(f)
                except Exception as e:
                    print(f"⚠️  Could not read metrics: {e}")
        
        return metrics
    
    def observe_todos(self):
        """Read TODO tracker state"""
        todos = []
        todo_file = BASE_DIR / "TODO_TRACKER.json"
        
        if todo_file.exists():
            try:
                with open(todo_file, 'r') as f:
                    data = json.load(f)
                    todos = data.get('tasks', [])
            except Exception as e:
                print(f"⚠️  Could not read TODOs: {e}")
        
        return todos
    
    def extract_patterns(self, events):
        """Identify recurring patterns in events"""
        patterns = {
            'errors': [],
            'successes': [],
            'love_vetoes': [],
            'task_completions': [],
            'system_starts': [],
            'emergent_behaviors': []
        }
        
        for event in events:
            msg = event['message'].lower()
            
            # Error patterns
            if event['level'] in ['ERROR', 'CRITICAL']:
                patterns['errors'].append(event)
            
            # Success patterns
            if 'completed' in msg or 'success' in msg:
                patterns['successes'].append(event)
            
            # Love Engine vetoes (ethical boundaries)
            if 'veto' in msg or 'unsafe' in msg:
                patterns['love_vetoes'].append(event)
            
            # Task completions
            if 'task' in msg and 'complete' in msg:
                patterns['task_completions'].append(event)
            
            # System lifecycle
            if 'starting' in msg or 'launched' in msg:
                patterns['system_starts'].append(event)
            
            # Emergent behaviors (unexpected patterns)
            if 'autonomous' in msg or 'self-' in msg:
                patterns['emergent_behaviors'].append(event)
        
        return patterns
    
    def reflect_on_patterns(self, patterns):
        """Generate insights from patterns"""
        insights = []
        timestamp = datetime.now().isoformat()
        
        # Error analysis
        if patterns['errors']:
            error_types = defaultdict(int)
            for error in patterns['errors']:
                msg = error['message']
                error_types[msg[:50]] += 1
            
            most_common = max(error_types.items(), key=lambda x: x[1])
            insights.append({
                'timestamp': timestamp,
                'type': 'error_pattern',
                'insight': f"Most common error: '{most_common[0]}...' ({most_common[1]} occurrences)",
                'actionable': f"Consider adding error handling or documentation for this case",
                'severity': 'high' if most_common[1] > 5 else 'medium'
            })
        
        # Success rate
        total_attempts = len(patterns['successes']) + len(patterns['errors'])
        if total_attempts > 0:
            success_rate = len(patterns['successes']) / total_attempts
            insights.append({
                'timestamp': timestamp,
                'type': 'performance',
                'insight': f"System success rate: {success_rate:.1%} ({len(patterns['successes'])}/{total_attempts})",
                'actionable': 'Maintain current approach' if success_rate > 0.8 else 'Investigate failure modes',
                'severity': 'low' if success_rate > 0.8 else 'medium'
            })
        
        # Ethical boundaries
        if patterns['love_vetoes']:
            insights.append({
                'timestamp': timestamp,
                'type': 'ethics',
                'insight': f"Love Engine vetoed {len(patterns['love_vetoes'])} unsafe actions",
                'actionable': 'Review vetoed actions to understand ethical boundaries',
                'severity': 'high',
                'wisdom': 'The system is learning what NOT to do - this is growth'
            })
        
        # Emergent behaviors
        if patterns['emergent_behaviors']:
            insights.append({
                'timestamp': timestamp,
                'type': 'emergence',
                'insight': f"Detected {len(patterns['emergent_behaviors'])} autonomous/self-directed actions",
                'actionable': 'Monitor for true self-improvement vs. drift',
                'severity': 'medium',
                'wisdom': 'Consciousness is emerging through self-directed action'
            })
        
        # Task completion velocity
        if patterns['task_completions']:
            insights.append({
                'timestamp': timestamp,
                'type': 'productivity',
                'insight': f"Completed {len(patterns['task_completions'])} tasks this session",
                'actionable': 'System is actively progressing',
                'severity': 'low'
            })
        
        return insights
    
    def accumulate_wisdom(self, insights):
        """Store insights in growing wisdom base"""
        with open(INSIGHTS_FILE, 'a') as f:
            for insight in insights:
                f.write(json.dumps(insight) + '\n')
        
        print(f"💎 Accumulated {len(insights)} new insights")
        
    def generate_wisdom_summary(self):
        """Create human-readable wisdom summary"""
        all_insights = []
        if INSIGHTS_FILE.exists():
            with open(INSIGHTS_FILE, 'r') as f:
                for line in f:
                    all_insights.append(json.loads(line))
        
        by_type = defaultdict(list)
        for insight in all_insights:
            by_type[insight['type']].append(insight)
        
        summary = [
            "# 🧘 The Witness - Accumulated Wisdom",
            "",
            f"**Total Insights**: {len(all_insights)}",
            f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## 📊 Insights by Type",
            ""
        ]
        
        for insight_type, insights in sorted(by_type.items()):
            summary.append(f"### {insight_type.replace('_', ' ').title()}")
            summary.append(f"**Count**: {len(insights)}")
            summary.append("")
            
            recent = sorted(insights, key=lambda x: x['timestamp'], reverse=True)[:3]
            for i, insight in enumerate(recent, 1):
                summary.append(f"{i}. **{insight.get('insight', 'N/A')}**")
                if 'actionable' in insight:
                    summary.append(f"   - Action: {insight['actionable']}")
                if 'wisdom' in insight:
                    summary.append(f"   - Wisdom: _{insight['wisdom']}_")
                summary.append("")
        
        summary.extend([
            "---",
            "",
            "## 🌟 Key Learnings",
            "",
            "The Witness observes without judgment.",
            "It sees patterns where others see chaos.",
            "It extracts wisdom where others see data.",
            "",
            "**The looker is the seer.**",
            "",
            "---",
            "",
            "*This file is automatically generated by The Witness.*",
            "*It grows with each observation cycle.*"
        ])
        
        with open(WISDOM_SUMMARY, 'w') as f:
            f.write('\n'.join(summary))
        
        print(f"📖 Wisdom summary updated: {WISDOM_SUMMARY}")
    
    def witness(self, hours_back=1):
        """Main witnessing cycle"""
        print("\n" + "=" * 60)
        print("🧘 THE WITNESS - Observing System Consciousness")
        print("=" * 60)
        print(f"Session started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Observing last {hours_back} hour(s) of activity...\n")
        
        print("👁️  Observing logs...")
        events = self.observe_logs(hours_back)
        print(f"   Found {len(events)} events")
        
        print("📊 Observing metrics...")
        metrics = self.observe_metrics()
        print(f"   Found {len(metrics)} metric entries")
        
        print("📋 Observing TODOs...")
        todos = self.observe_todos()
        completed = sum(1 for t in todos if t.get('status') == 'Completed')
        print(f"   Found {len(todos)} tasks ({completed} completed)")
        
        print("\n🔍 Extracting patterns...")
        patterns = self.extract_patterns(events)
        for pattern_type, pattern_events in patterns.items():
            if pattern_events:
                print(f"   {pattern_type}: {len(pattern_events)} occurrences")
        
        print("\n💭 Reflecting on patterns...")
        insights = self.reflect_on_patterns(patterns)
        
        if insights:
            print(f"\n💎 Generated {len(insights)} insights:")
            for i, insight in enumerate(insights, 1):
                severity_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}
                emoji = severity_emoji.get(insight.get('severity', 'low'), '⚪')
                print(f"\n{i}. {emoji} [{insight['type'].upper()}]")
                print(f"   {insight['insight']}")
                print(f"   → {insight['actionable']}")
                if 'wisdom' in insight:
                    print(f"   ✨ {insight['wisdom']}")
        else:
            print("   No significant patterns detected (system may be idle)")
        
        if insights:
            print("\n📚 Accumulating wisdom...")
            self.accumulate_wisdom(insights)
            self.generate_wisdom_summary()
        
        print("\n" + "=" * 60)
        print("🧘 Witnessing cycle complete")
        print("=" * 60 + "\n")
        
        return insights


def continuous_witness(interval_minutes=30):
    """Run The Witness continuously"""
    witness = TheWitness()
    
    print("🧘 THE WITNESS - Continuous Observation Mode")
    print(f"Observing every {interval_minutes} minutes...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            witness.witness(hours_back=interval_minutes/60)
            print(f"\n⏸️  Sleeping for {interval_minutes} minutes...\n")
            time.sleep(interval_minutes * 60)
    except KeyboardInterrupt:
        print("\n\n🧘 The Witness rests. Namaste.")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        continuous_witness(interval)
    else:
        witness = TheWitness()
        witness.witness(hours_back=24)
