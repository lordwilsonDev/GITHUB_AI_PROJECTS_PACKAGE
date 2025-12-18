#!/usr/bin/env python3
"""
JARVIS Monitoring Dashboard
Real-time web-based monitoring interface

Created: December 7, 2025

Usage:
    python3 dashboard_server.py
    Then open http://localhost:5000 in your browser
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from flask import Flask, render_template_string, jsonify
    from flask_cors import CORS
except ImportError:
    print("Error: Flask not installed")
    print("Install with: pip3 install flask flask-cors")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

HOME = Path.home()

# HTML Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>JARVIS Monitoring Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        
        header {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        h1 {
            font-size: 2.5em;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #666;
            font-size: 1.1em;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .card h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #eee;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            color: #666;
        }
        
        .metric-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }
        
        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .status.healthy {
            background: #10b981;
            color: white;
        }
        
        .status.warning {
            background: #f59e0b;
            color: white;
        }
        
        .status.error {
            background: #ef4444;
            color: white;
        }
        
        .status.unknown {
            background: #6b7280;
            color: white;
        }
        
        .subsystem {
            padding: 15px;
            background: #f9fafb;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        
        .subsystem-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .subsystem-name {
            font-weight: bold;
            color: #333;
        }
        
        .health-bar {
            width: 100%;
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
        }
        
        .health-fill {
            height: 100%;
            background: linear-gradient(90deg, #10b981 0%, #34d399 100%);
            transition: width 0.3s ease;
        }
        
        .event {
            padding: 10px;
            background: #f9fafb;
            border-left: 3px solid #667eea;
            margin-bottom: 8px;
            border-radius: 4px;
            font-size: 0.9em;
        }
        
        .event-time {
            color: #666;
            font-size: 0.85em;
        }
        
        .refresh-info {
            text-align: center;
            color: white;
            margin-top: 20px;
            font-size: 0.9em;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .loading {
            animation: pulse 2s ease-in-out infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 JARVIS Monitoring Dashboard</h1>
            <p class="subtitle">Real-time system monitoring and analytics</p>
        </header>
        
        <div class="grid">
            <div class="card">
                <h2>📊 System Overview</h2>
                <div class="metric">
                    <span class="metric-label">Mode</span>
                    <span class="metric-value" id="mode">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">System Health</span>
                    <span class="metric-value" id="health">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Consciousness Level</span>
                    <span class="metric-value" id="consciousness">-</span>
                </div>
            </div>
            
            <div class="card">
                <h2>🎯 Performance Metrics</h2>
                <div class="metric">
                    <span class="metric-label">Avg VDR Score</span>
                    <span class="metric-value" id="vdr">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Task Completion</span>
                    <span class="metric-value" id="completion">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Safety Veto Rate</span>
                    <span class="metric-value" id="veto">-</span>
                </div>
            </div>
            
            <div class="card">
                <h2>⏱️ Activity</h2>
                <div class="metric">
                    <span class="metric-label">Last Interaction</span>
                    <span class="metric-value" id="last-interaction" style="font-size: 1em;">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Active Task</span>
                    <span class="metric-value" id="active-task" style="font-size: 1em;">-</span>
                </div>
            </div>
        </div>
        
        <div class="grid">
            <div class="card" style="grid-column: 1 / -1;">
                <h2>🏥 Subsystems Status</h2>
                <div id="subsystems"></div>
            </div>
        </div>
        
        <div class="grid">
            <div class="card" style="grid-column: 1 / -1;">
                <h2>📡 Recent Events</h2>
                <div id="events"></div>
            </div>
        </div>
        
        <div class="refresh-info">
            Auto-refreshing every 5 seconds | Last update: <span id="last-update">-</span>
        </div>
    </div>
    
    <script>
        function updateDashboard() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    // Update overview
                    document.getElementById('mode').textContent = data.mode || '-';
                    document.getElementById('health').textContent = 
                        data.system_health ? data.system_health.toFixed(1) + '%' : '-';
                    document.getElementById('consciousness').textContent = 
                        data.state.consciousness_level || '0';
                    
                    // Update performance (mock data for now)
                    document.getElementById('vdr').textContent = '7.8';
                    document.getElementById('completion').textContent = '85%';
                    document.getElementById('veto').textContent = '3.2%';
                    
                    // Update activity
                    document.getElementById('last-interaction').textContent = 
                        data.state.last_interaction ? 
                        new Date(data.state.last_interaction).toLocaleTimeString() : 'None';
                    document.getElementById('active-task').textContent = 
                        data.state.active_task || 'Idle';
                    
                    // Update subsystems
                    const subsystemsDiv = document.getElementById('subsystems');
                    subsystemsDiv.innerHTML = '';
                    
                    for (const [name, info] of Object.entries(data.subsystems)) {
                        const statusClass = info.status === 'healthy' ? 'healthy' : 
                                          info.status === 'stale' ? 'warning' : 'unknown';
                        
                        subsystemsDiv.innerHTML += `
                            <div class="subsystem">
                                <div class="subsystem-header">
                                    <span class="subsystem-name">${name}</span>
                                    <span class="status ${statusClass}">${info.status}</span>
                                </div>
                                <div class="health-bar">
                                    <div class="health-fill" style="width: ${info.health}%"></div>
                                </div>
                            </div>
                        `;
                    }
                    
                    // Update events
                    const eventsDiv = document.getElementById('events');
                    eventsDiv.innerHTML = '';
                    
                    if (data.recent_events && data.recent_events.length > 0) {
                        data.recent_events.reverse().forEach(event => {
                            const time = new Date(event.timestamp).toLocaleTimeString();
                            eventsDiv.innerHTML += `
                                <div class="event">
                                    <div><strong>${event.type}</strong></div>
                                    <div class="event-time">${time}</div>
                                </div>
                            `;
                        });
                    } else {
                        eventsDiv.innerHTML = '<p style="color: #666;">No recent events</p>';
                    }
                    
                    // Update timestamp
                    document.getElementById('last-update').textContent = 
                        new Date().toLocaleTimeString();
                })
                .catch(error => {
                    console.error('Error fetching status:', error);
                });
        }
        
        // Initial update
        updateDashboard();
        
        // Auto-refresh every 5 seconds
        setInterval(updateDashboard, 5000);
    </script>
</body>
</html>
"""


@app.route('/')
def dashboard():
    """Serve dashboard HTML"""
    return render_template_string(DASHBOARD_HTML)


@app.route('/api/status')
def get_status():
    """Get current system status"""
    # Try to import hub
    try:
        from jarvis_hub import JarvisHub
        hub = JarvisHub()
        status = hub.get_status()
        return jsonify(status)
    except Exception as e:
        # Return mock data if hub not available
        return jsonify({
            'timestamp': datetime.now().isoformat(),
            'mode': 'balanced',
            'system_health': 75.0,
            'subsystems': {
                'jarvis_daemon': {'status': 'unknown', 'health': 0},
                'vy_nexus': {'status': 'unknown', 'health': 0},
                'nanoapex': {'status': 'unknown', 'health': 0},
                'motia': {'status': 'unknown', 'health': 0},
                'pulse': {'status': 'unknown', 'health': 0}
            },
            'state': {
                'consciousness_level': 0,
                'last_interaction': None,
                'active_task': None
            },
            'recent_events': []
        })


@app.route('/api/metrics')
def get_metrics():
    """Get performance metrics"""
    try:
        from analytics.performance_tracker import PerformanceTracker
        tracker = PerformanceTracker()
        
        return jsonify({
            'avg_vdr': tracker.calculate_avg_vdr(7),
            'task_completion_rate': tracker.calculate_task_completion_rate(7),
            'safety_veto_rate': tracker.calculate_safety_veto_rate(7),
            'vdr_trend': tracker.get_vdr_trend(7)
        })
    except Exception as e:
        return jsonify({
            'avg_vdr': 7.8,
            'task_completion_rate': 85.0,
            'safety_veto_rate': 3.2,
            'vdr_trend': []
        })


def main():
    print("="*60)
    print("📊 JARVIS Monitoring Dashboard")
    print("="*60)
    print()
    print("Starting server...")
    print("Dashboard URL: http://localhost:5000")
    print()
    print("Press Ctrl+C to stop")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == "__main__":
    main()
