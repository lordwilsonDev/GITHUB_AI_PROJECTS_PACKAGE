#!/usr/bin/env python3
"""
Real-time Dashboard and Monitoring System

Provides:
- Web-based dashboard for system monitoring
- Real-time metrics and statistics
- Agent health monitoring
- Task queue visualization
- Performance analytics
"""

import asyncio
import logging
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects and aggregates system metrics.
    
    Metrics:
    - Task throughput (tasks/second)
    - Agent utilization
    - Queue depth
    - Success/failure rates
    - Response times
    """
    
    def __init__(self):
        self.metrics = {
            'tasks': {
                'submitted': 0,
                'completed': 0,
                'failed': 0,
                'cancelled': 0,
                'throughput': 0.0
            },
            'agents': {
                'total': 0,
                'active': 0,
                'idle': 0,
                'utilization': 0.0
            },
            'queue': {
                'pending': 0,
                'running': 0,
                'depth': 0
            },
            'performance': {
                'avg_task_duration': 0.0,
                'success_rate': 0.0,
                'error_rate': 0.0
            }
        }
        
        self.history = []
        self.max_history = 1000
        self.start_time = time.time()
        
        logger.info("MetricsCollector initialized")
    
    def update_metrics(self, task_queue, agents: List):
        """Update metrics from current system state."""
        # Task metrics
        queue_stats = task_queue.get_queue_stats()
        self.metrics['tasks']['submitted'] = queue_stats['total_submitted']
        self.metrics['tasks']['completed'] = queue_stats['total_completed']
        self.metrics['tasks']['failed'] = queue_stats['total_failed']
        self.metrics['tasks']['cancelled'] = queue_stats['total_cancelled']
        
        # Calculate throughput
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            self.metrics['tasks']['throughput'] = queue_stats['total_completed'] / elapsed
        
        # Agent metrics
        self.metrics['agents']['total'] = len(agents)
        active_agents = sum(1 for agent in agents if agent.status.value == 'busy')
        self.metrics['agents']['active'] = active_agents
        self.metrics['agents']['idle'] = len(agents) - active_agents
        
        if len(agents) > 0:
            self.metrics['agents']['utilization'] = active_agents / len(agents)
        
        # Queue metrics
        self.metrics['queue']['pending'] = queue_stats['pending']
        self.metrics['queue']['running'] = queue_stats['running']
        self.metrics['queue']['depth'] = queue_stats['pending'] + queue_stats['running']
        
        # Performance metrics
        self.metrics['performance']['success_rate'] = queue_stats['success_rate']
        self.metrics['performance']['error_rate'] = 1.0 - queue_stats['success_rate']
        
        # Add to history
        snapshot = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics.copy()
        }
        self.history.append(snapshot)
        
        # Trim history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def get_current_metrics(self) -> Dict:
        """Get current metrics snapshot."""
        return {
            'timestamp': datetime.now().isoformat(),
            'uptime_seconds': time.time() - self.start_time,
            'metrics': self.metrics.copy()
        }
    
    def get_metrics_history(self, duration_seconds: int = 300) -> List[Dict]:
        """Get metrics history for specified duration."""
        cutoff = datetime.now() - timedelta(seconds=duration_seconds)
        
        return [
            snapshot for snapshot in self.history
            if datetime.fromisoformat(snapshot['timestamp']) > cutoff
        ]
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics."""
        return {
            'total_tasks_processed': self.metrics['tasks']['completed'] + self.metrics['tasks']['failed'],
            'success_rate': self.metrics['performance']['success_rate'],
            'avg_throughput': self.metrics['tasks']['throughput'],
            'agent_utilization': self.metrics['agents']['utilization'],
            'uptime_hours': (time.time() - self.start_time) / 3600
        }


class DashboardServer:
    """
    Web-based dashboard server.
    
    Provides:
    - Real-time metrics display
    - System status overview
    - Agent monitoring
    - Task queue visualization
    """
    
    def __init__(self, metrics_collector: MetricsCollector, port: int = 8080):
        self.metrics = metrics_collector
        self.port = port
        self.app = None
        self.server_task = None
        
        logger.info(f"DashboardServer initialized (port: {port})")
    
    async def start(self):
        """Start the dashboard server."""
        try:
            # Try to import FastAPI
            from fastapi import FastAPI
            from fastapi.responses import HTMLResponse, JSONResponse
            import uvicorn
            
            self.app = FastAPI(title="AI Agent Orchestration Dashboard")
            
            @self.app.get("/")
            async def root():
                return HTMLResponse(self._generate_html())
            
            @self.app.get("/api/metrics")
            async def get_metrics():
                return JSONResponse(self.metrics.get_current_metrics())
            
            @self.app.get("/api/history")
            async def get_history(duration: int = 300):
                return JSONResponse(self.metrics.get_metrics_history(duration))
            
            @self.app.get("/api/summary")
            async def get_summary():
                return JSONResponse(self.metrics.get_summary_stats())
            
            # Start server in background
            config = uvicorn.Config(self.app, host="0.0.0.0", port=self.port, log_level="warning")
            server = uvicorn.Server(config)
            
            self.server_task = asyncio.create_task(server.serve())
            
            logger.info(f"✅ Dashboard server started: http://localhost:{self.port}")
            
        except ImportError:
            logger.warning("⚠️ FastAPI not installed - dashboard server disabled")
            logger.info("Install with: pip install fastapi uvicorn")
    
    async def stop(self):
        """Stop the dashboard server."""
        if self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass
            logger.info("✅ Dashboard server stopped")
    
    def _generate_html(self) -> str:
        """Generate dashboard HTML."""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>AI Agent Orchestration Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 {
            font-size: 2rem;
            margin-bottom: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: #1e293b;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        .card h2 {
            font-size: 1.2rem;
            margin-bottom: 16px;
            color: #94a3b8;
        }
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #334155;
        }
        .metric:last-child { border-bottom: none; }
        .metric-label { color: #94a3b8; }
        .metric-value {
            font-size: 1.5rem;
            font-weight: 600;
            color: #10b981;
        }
        .status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.875rem;
            font-weight: 500;
        }
        .status-running { background: #10b981; color: white; }
        .status-idle { background: #6366f1; color: white; }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #334155;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 8px;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }
        .timestamp {
            text-align: center;
            color: #64748b;
            margin-top: 20px;
            font-size: 0.875rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 AI Agent Orchestration Dashboard</h1>
        
        <div class="grid">
            <div class="card">
                <h2>System Status</h2>
                <div class="metric">
                    <span class="metric-label">Status</span>
                    <span class="status status-running" id="system-status">Running</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Uptime</span>
                    <span class="metric-value" id="uptime">0h 0m</span>
                </div>
            </div>
            
            <div class="card">
                <h2>Tasks</h2>
                <div class="metric">
                    <span class="metric-label">Completed</span>
                    <span class="metric-value" id="tasks-completed">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Throughput</span>
                    <span class="metric-value" id="throughput">0.0/s</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Success Rate</span>
                    <span class="metric-value" id="success-rate">0%</span>
                </div>
            </div>
            
            <div class="card">
                <h2>Agents</h2>
                <div class="metric">
                    <span class="metric-label">Total</span>
                    <span class="metric-value" id="agents-total">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Active</span>
                    <span class="metric-value" id="agents-active">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Utilization</span>
                    <span class="metric-value" id="utilization">0%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="utilization-bar" style="width: 0%"></div>
                </div>
            </div>
            
            <div class="card">
                <h2>Queue</h2>
                <div class="metric">
                    <span class="metric-label">Pending</span>
                    <span class="metric-value" id="queue-pending">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Running</span>
                    <span class="metric-value" id="queue-running">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Depth</span>
                    <span class="metric-value" id="queue-depth">0</span>
                </div>
            </div>
        </div>
        
        <div class="timestamp" id="last-update">Last updated: --</div>
    </div>
    
    <script>
        async function updateDashboard() {
            try {
                const response = await fetch('/api/metrics');
                const data = await response.json();
                
                // Update uptime
                const hours = Math.floor(data.uptime_seconds / 3600);
                const minutes = Math.floor((data.uptime_seconds % 3600) / 60);
                document.getElementById('uptime').textContent = `${hours}h ${minutes}m`;
                
                // Update tasks
                document.getElementById('tasks-completed').textContent = data.metrics.tasks.completed;
                document.getElementById('throughput').textContent = data.metrics.tasks.throughput.toFixed(2) + '/s';
                document.getElementById('success-rate').textContent = (data.metrics.performance.success_rate * 100).toFixed(1) + '%';
                
                // Update agents
                document.getElementById('agents-total').textContent = data.metrics.agents.total;
                document.getElementById('agents-active').textContent = data.metrics.agents.active;
                const utilization = (data.metrics.agents.utilization * 100).toFixed(1);
                document.getElementById('utilization').textContent = utilization + '%';
                document.getElementById('utilization-bar').style.width = utilization + '%';
                
                // Update queue
                document.getElementById('queue-pending').textContent = data.metrics.queue.pending;
                document.getElementById('queue-running').textContent = data.metrics.queue.running;
                document.getElementById('queue-depth').textContent = data.metrics.queue.depth;
                
                // Update timestamp
                const now = new Date();
                document.getElementById('last-update').textContent = `Last updated: ${now.toLocaleTimeString()}`;
                
            } catch (error) {
                console.error('Error updating dashboard:', error);
            }
        }
        
        // Update every 2 seconds
        updateDashboard();
        setInterval(updateDashboard, 2000);
    </script>
</body>
</html>
        """


class MonitoringSystem:
    """
    Complete monitoring system integrating metrics and dashboard.
    """
    
    def __init__(self, task_queue, agents: List, port: int = 8080):
        self.task_queue = task_queue
        self.agents = agents
        
        self.metrics = MetricsCollector()
        self.dashboard = DashboardServer(self.metrics, port)
        
        self.monitoring_task = None
        self.running = False
        
        logger.info("MonitoringSystem initialized")
    
    async def start(self):
        """Start monitoring system."""
        self.running = True
        
        # Start dashboard server
        await self.dashboard.start()
        
        # Start metrics collection loop
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        logger.info("✅ Monitoring system started")
    
    async def stop(self):
        """Stop monitoring system."""
        self.running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        await self.dashboard.stop()
        
        logger.info("✅ Monitoring system stopped")
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                # Update metrics
                self.metrics.update_metrics(self.task_queue, self.agents)
                
                # Sleep before next update
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)
    
    def get_current_status(self) -> Dict:
        """Get current system status."""
        return {
            'metrics': self.metrics.get_current_metrics(),
            'summary': self.metrics.get_summary_stats()
        }


# Example usage and testing
async def test_monitoring():
    """Test monitoring system."""
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*60)
    print("Testing Monitoring System")
    print("="*60)
    
    # Create test components
    from task_queue import TaskQueue, Task, TaskPriority
    from agent_framework import WorkerAgent, AgentCapability
    
    print("\n[1/4] Creating task queue and agents...")
    task_queue = TaskQueue()
    agents = []
    
    for i in range(10):
        agent = WorkerAgent(f"test_agent_{i}", [AgentCapability.ANALYSIS])
        await agent.initialize()
        agents.append(agent)
    
    # Create monitoring system
    print("\n[2/4] Creating monitoring system...")
    monitoring = MonitoringSystem(task_queue, agents, port=8080)
    
    # Start monitoring
    print("\n[3/4] Starting monitoring system...")
    await monitoring.start()
    
    print("\n" + "="*60)
    print("Dashboard available at: http://localhost:8080")
    print("="*60)
    
    # Simulate some activity
    print("\n[4/4] Simulating activity...")
    for i in range(20):
        task = Task(
            task_id=f"test_task_{i}",
            task_type="analysis",
            payload={'data': f'test {i}'},
            priority=TaskPriority.NORMAL
        )
        await task_queue.submit_task(task)
    
    # Process some tasks
    for i in range(10):
        task = task_queue.get_next_task(f"test_agent_{i % 10}", ['analysis'])
        if task:
            await task_queue.mark_task_running(task.task_id)
            await task_queue.complete_task(task.task_id, {'result': 'success'})
    
    # Show status
    print("\nCurrent Status:")
    status = monitoring.get_current_status()
    print(json.dumps(status, indent=2))
    
    # Keep running
    print("\n" + "="*60)
    print("Monitoring system running. Press Ctrl+C to stop.")
    print("Open http://localhost:8080 in your browser")
    print("="*60)
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n\nShutting down...")
    finally:
        await monitoring.stop()
        for agent in agents:
            await agent.shutdown()
        print("\n✅ Shutdown complete")


if __name__ == '__main__':
    asyncio.run(test_monitoring())
