#!/usr/bin/env python3
"""
VY SOVEREIGNTY COMMAND CENTER - Backend
Unified monitoring and control for the entire cognitive sovereignty stack
"""

import asyncio
import json
import os
import psutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI(title="VY Sovereignty Command Center")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# System paths
HOME = Path.home()
SYSTEMS = {
    "sovereign-stack": HOME / "sovereign-stack",
    "love-engine": HOME / "love-engine-real",
    "cord-project": HOME / "Desktop" / "cord-project",
    "level33": HOME / "level33_sovereign",
    "moie-os": HOME / "moie-os",
    "nanoapex": HOME / "nanoapex",
    "lcrs-system": HOME / "lcrs-system",
    "metadata-universe": HOME / "metadata-universe",
    "jarvis": HOME / "jarvis_m1",
}

def check_docker_containers() -> List[Dict]:
    """Check Docker container status"""
    try:
        result = subprocess.run(
            ["docker", "ps", "-a", "--format", "{{json .}}"],
            capture_output=True,
            text=True,
            timeout=5
        )
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    containers.append(json.loads(line))
                except:
                    pass
        return containers
    except:
        return []

def check_process_running(name: str) -> Optional[Dict]:
    """Check if a process is running by name"""
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            if name.lower() in proc.info['name'].lower():
                return {
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu': proc.info['cpu_percent'],
                    'memory': proc.info['memory_percent']
                }
        except:
            pass
    return None

def get_system_status(system_name: str, path: Path) -> Dict:
    """Get detailed status of a specific system"""
    status = {
        'name': system_name,
        'path': str(path),
        'exists': path.exists(),
        'processes': [],
        'containers': [],
        'health': 'unknown',
        'logs': []
    }
    
    if not path.exists():
        status['health'] = 'missing'
        return status
    
    # Check for running processes
    if system_name == 'sovereign-stack':
        brain = check_process_running('recursive_planner')
        heart = check_process_running('love')
        if brain or heart:
            status['processes'] = [p for p in [brain, heart] if p]
            status['health'] = 'running'
        else:
            status['health'] = 'stopped'
    
    # Check for Docker containers
    containers = check_docker_containers()
    for container in containers:
        if system_name.replace('-', '_') in container.get('Names', '').lower():
            status['containers'].append(container)
            if container.get('State') == 'running':
                status['health'] = 'running'
    
    # Read recent logs if available
    log_paths = [
        path / 'logs',
        path / f'{system_name}.log',
    ]
    for log_path in log_paths:
        if log_path.exists():
            try:
                if log_path.is_dir():
                    for log_file in log_path.glob('*.log'):
                        with open(log_file, 'r') as f:
                            lines = f.readlines()
                            status['logs'].extend(lines[-10:])  # Last 10 lines
                else:
                    with open(log_path, 'r') as f:
                        status['logs'] = f.readlines()[-10:]
            except:
                pass
    
    if status['health'] == 'unknown' and status['exists']:
        status['health'] = 'idle'
    
    return status

def get_system_resources() -> Dict:
    """Get overall system resource usage"""
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        'cpu': {
            'overall': sum(cpu_percent) / len(cpu_percent),
            'per_core': cpu_percent,
            'cores': len(cpu_percent)
        },
        'memory': {
            'total': memory.total,
            'used': memory.used,
            'percent': memory.percent,
            'available': memory.available
        },
        'disk': {
            'total': disk.total,
            'used': disk.used,
            'percent': disk.percent,
            'free': disk.free
        }
    }

@app.get("/api/status")
async def get_status():
    """Get complete system status"""
    status = {
        'timestamp': datetime.now().isoformat(),
        'resources': get_system_resources(),
        'systems': {}
    }
    
    for system_name, path in SYSTEMS.items():
        status['systems'][system_name] = get_system_status(system_name, path)
    
    return status

@app.post("/api/control/{system}/{action}")
async def control_system(system: str, action: str):
    """Control system (start/stop/restart)"""
    if system not in SYSTEMS:
        return {'error': 'Unknown system'}
    
    path = SYSTEMS[system]
    
    if action == 'start':
        # Try to start the system
        start_script = path / 'start.sh'
        if start_script.exists():
            subprocess.Popen(['bash', str(start_script)], cwd=str(path))
            return {'status': 'starting', 'system': system}
    
    elif action == 'stop':
        # Try to stop the system
        stop_script = path / 'stop.sh'
        if stop_script.exists():
            subprocess.Popen(['bash', str(stop_script)], cwd=str(path))
            return {'status': 'stopping', 'system': system}
    
    return {'error': f'Action {action} not implemented for {system}'}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Send status updates every 2 seconds
            status = await get_status()
            await websocket.send_json(status)
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    """Serve the dashboard"""
    return FileResponse("index.html")

@app.get("/index.html")
async def index():
    """Serve the dashboard"""
    return FileResponse("index.html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8888)
