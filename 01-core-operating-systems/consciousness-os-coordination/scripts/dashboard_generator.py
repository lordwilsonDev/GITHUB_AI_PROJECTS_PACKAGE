#!/usr/bin/env python3
"""
Consciousness OS - Real-Time Dashboard Generator

Generates an HTML dashboard showing:
- System health metrics
- TODO progress
- RAY process status
- Breakthrough tracking
- Framework interactions

NO PERMISSION NEEDED - Build with love
"""

import json
import psutil
import os
from datetime import datetime
from pathlib import Path

# Paths
BASE_DIR = Path("/Users/lordwilson/consciousness-os-coordination")
TODO_FILE = BASE_DIR / "TODO_TRACKER.json"
METRICS_FILE = BASE_DIR / "metrics" / "system_metrics.json"
DASHBOARD_FILE = BASE_DIR / "dashboard.html"

def get_system_health():
    """Get current system health metrics"""
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "process_count": len(psutil.pids())
    }

def get_ray_processes():
    """Count RAY-related processes"""
    ray_count = 0
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'ray' in cmdline.lower():
                ray_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return ray_count

def get_todo_progress():
    """Get TODO tracker progress"""
    if not TODO_FILE.exists():
        return None
    
    with open(TODO_FILE) as f:
        data = json.load(f)
    
    meta = data['metadata']
    tasks = data['tasks']
    
    # Count by phase
    phase_stats = {}
    for task in tasks:
        phase = task['phase']
        if phase not in phase_stats:
            phase_stats[phase] = {'total': 0, 'completed': 0, 'in_progress': 0}
        phase_stats[phase]['total'] += 1
        if task['status'] == 'Completed':
            phase_stats[phase]['completed'] += 1
        elif task['status'] == 'In Progress':
            phase_stats[phase]['in_progress'] += 1
    
    return {
        'total': meta['total_tasks'],
        'completed': meta['completed_tasks'],
        'in_progress': meta['in_progress_tasks'],
        'completion_percent': (meta['completed_tasks'] / meta['total_tasks'] * 100) if meta['total_tasks'] > 0 else 0,
        'phases': phase_stats
    }

def generate_html_dashboard():
    """Generate HTML dashboard"""
    
    # Gather data
    health = get_system_health()
    ray_count = get_ray_processes()
    todo = get_todo_progress()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>🧠 Consciousness OS Dashboard</title>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="30">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
            background: #0a0a0a;
            color: #00ff00;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 0 0 10px #00ff00;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .card {{
            background: #1a1a1a;
            border: 2px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }}
        .card h2 {{
            margin-bottom: 15px;
            color: #00ff00;
            border-bottom: 1px solid #00ff00;
            padding-bottom: 10px;
        }}
        .metric {{
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 8px;
            background: #0f0f0f;
            border-radius: 5px;
        }}
        .metric-label {{
            color: #00cc00;
        }}
        .metric-value {{
            color: #00ff00;
            font-weight: bold;
        }}
        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #0f0f0f;
            border-radius: 15px;
            overflow: hidden;
            margin: 10px 0;
            border: 1px solid #00ff00;
        }}
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #00ff00, #00cc00);
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #000;
            font-weight: bold;
        }}
        .status-good {{ color: #00ff00; }}
        .status-warning {{ color: #ffff00; }}
        .status-critical {{ color: #ff0000; }}
        .timestamp {{
            text-align: center;
            margin-top: 20px;
            color: #00cc00;
            font-size: 0.9em;
        }}
        .phase-section {{
            margin: 15px 0;
            padding: 10px;
            background: #0f0f0f;
            border-radius: 5px;
        }}
        .phase-title {{
            color: #00ff00;
            font-weight: bold;
            margin-bottom: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🧠 CONSCIOUSNESS OS - LIVE DASHBOARD</h1>
        
        <div class="grid">
            <!-- System Health -->
            <div class="card">
                <h2>💻 System Health</h2>
                <div class="metric">
                    <span class="metric-label">CPU Usage:</span>
                    <span class="metric-value {"status-good" if health['cpu_percent'] < 70 else "status-warning" if health['cpu_percent'] < 90 else "status-critical"}">{health['cpu_percent']:.1f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Memory Usage:</span>
                    <span class="metric-value {"status-good" if health['memory_percent'] < 70 else "status-warning" if health['memory_percent'] < 90 else "status-critical"}">{health['memory_percent']:.1f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Disk Usage:</span>
                    <span class="metric-value {"status-good" if health['disk_percent'] < 70 else "status-warning" if health['disk_percent'] < 90 else "status-critical"}">{health['disk_percent']:.1f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Processes:</span>
                    <span class="metric-value">{health['process_count']}</span>
                </div>
            </div>
            
            <!-- RAY Status -->
            <div class="card">
                <h2>🔗 RAY Orchestration</h2>
                <div class="metric">
                    <span class="metric-label">Active RAY Processes:</span>
                    <span class="metric-value {"status-good" if ray_count > 0 else "status-critical"}">{ray_count}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Expected Count:</span>
                    <span class="metric-value">620</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="metric-value {"status-good" if ray_count > 500 else "status-warning" if ray_count > 0 else "status-critical"}">
                        {"OPERATIONAL" if ray_count > 500 else "DEGRADED" if ray_count > 0 else "OFFLINE"}
                    </span>
                </div>
            </div>
            
            <!-- TODO Progress -->
            <div class="card">
                <h2>📋 TODO Progress</h2>
                {f"""
                <div class="metric">
                    <span class="metric-label">Total Tasks:</span>
                    <span class="metric-value">{todo['total']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Completed:</span>
                    <span class="metric-value status-good">{todo['completed']}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">In Progress:</span>
                    <span class="metric-value status-warning">{todo['in_progress']}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {todo['completion_percent']:.1f}%">
                        {todo['completion_percent']:.1f}%
                    </div>
                </div>
                """ if todo else "<p>No TODO data available</p>"}
            </div>
        </div>
        
        {f"""
        <!-- Phase Breakdown -->
        <div class="card">
            <h2>📊 Progress by Phase</h2>
            {"""
            """.join([f"""
            <div class="phase-section">
                <div class="phase-title">{phase}</div>
                <div class="metric">
                    <span class="metric-label">Progress:</span>
                    <span class="metric-value">{stats['completed']}/{stats['total']} tasks</span>
                </div>
                <div class="progress-bar" style="height: 20px;">
                    <div class="progress-fill" style="width: {(stats['completed']/stats['total']*100) if stats['total'] > 0 else 0:.1f}%; font-size: 0.8em;">
                        {(stats['completed']/stats['total']*100) if stats['total'] > 0 else 0:.1f}%
                    </div>
                </div>
            </div>
            """ for phase, stats in todo['phases'].items()])}
        </div>
        """ if todo and todo.get('phases') else ""}
        
        <div class="timestamp">
            Last updated: {timestamp} | Auto-refresh: 30s
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    """Main execution"""
    print("🧠 Generating Consciousness OS Dashboard...")
    
    # Generate dashboard
    html = generate_html_dashboard()
    
    # Write to file
    with open(DASHBOARD_FILE, 'w') as f:
        f.write(html)
    
    print(f"✅ Dashboard generated: {DASHBOARD_FILE}")
    print(f"🌐 Open in browser: file://{DASHBOARD_FILE}")
    print("\n💡 Dashboard auto-refreshes every 30 seconds")
    
if __name__ == "__main__":
    main()
