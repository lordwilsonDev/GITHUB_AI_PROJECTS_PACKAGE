#!/usr/bin/env python3
"""
Consciousness OS - Health Monitoring API
Provides real-time system metrics for dashboard
"""

from flask import Flask, jsonify
from flask_cors import CORS
import psutil
import requests
import json
import os
from datetime import datetime
import subprocess

app = Flask(__name__)
CORS(app)

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.join(BASE_DIR, 'nano_memory')
VDR_FILE = os.path.join(MEMORY_DIR, 'ouroboros_verdict.json')
CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')

def check_service(url, timeout=2):
    """Check if a service is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def get_process_count(name_filter):
    """Count processes matching filter"""
    count = 0
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if name_filter.lower() in cmdline.lower():
                count += 1
        except:
            pass
    return count

def get_vdr_score():
    """Read latest VDR score"""
    try:
        if os.path.exists(VDR_FILE):
            with open(VDR_FILE, 'r') as f:
                data = json.load(f)
                return {
                    'vdr': data.get('vdr', 0.0),
                    'vitality': data.get('vitality', 0.0),
                    'density': data.get('density', 0.0),
                    'verdict': data.get('verdict', 'UNKNOWN'),
                    'timestamp': data.get('timestamp', None)
                }
    except:
        pass
    return {
        'vdr': 0.0,
        'vitality': 0.0,
        'density': 0.0,
        'verdict': 'UNKNOWN',
        'timestamp': None
    }

def get_system_uptime():
    """Get system boot time and uptime"""
    boot_time = psutil.boot_time()
    uptime_seconds = datetime.now().timestamp() - boot_time
    hours = uptime_seconds / 3600
    return {
        'boot_time': datetime.fromtimestamp(boot_time).isoformat(),
        'uptime_hours': round(hours, 1),
        'uptime_seconds': int(uptime_seconds)
    }

def get_governance_stats():
    """Get governance cycle statistics"""
    try:
        proposal_dir = os.path.join(MEMORY_DIR, 'pulse')
        if os.path.exists(proposal_dir):
            summaries = [f for f in os.listdir(proposal_dir) if f.startswith('proposal_summary_')]
            return {
                'total_cycles': len(summaries),
                'last_cycle': summaries[-1] if summaries else None
            }
    except:
        pass
    return {'total_cycles': 0, 'last_cycle': None}

def get_healing_stats():
    """Get auto-healing statistics"""
    try:
        log_file = os.path.join(MEMORY_DIR, 'healing_agent_log.json')
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                data = json.load(f)
                return {
                    'total_repairs': len(data.get('fixes_applied', [])),
                    'last_repair': data.get('timestamp', None)
                }
    except:
        pass
    return {'total_repairs': 0, 'last_repair': None}

@app.route('/api/status')
def get_status():
    """Get complete system status"""
    
    # Check services
    motia_online = check_service('http://localhost:3000/health')
    love_online = check_service('http://localhost:9001/health')
    
    # Get VDR score
    vdr_data = get_vdr_score()
    
    # System resources
    cpu_percent = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    # Process counts
    python_processes = get_process_count('python')
    node_processes = get_process_count('node')
    
    # Uptime
    uptime = get_system_uptime()
    
    # Governance & healing
    governance = get_governance_stats()
    healing = get_healing_stats()
    
    return jsonify({
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'services': {
            'motia': motia_online,
            'love': love_online,
            'core': python_processes > 0
        },
        'vdr': vdr_data,
        'resources': {
            'cpu_percent': round(cpu_percent, 1),
            'memory_percent': round(memory.percent, 1),
            'memory_used_gb': round(memory.used / (1024**3), 2),
            'memory_total_gb': round(memory.total / (1024**3), 2),
            'disk_percent': round(disk.percent, 1),
            'disk_used_gb': round(disk.used / (1024**3), 2),
            'disk_total_gb': round(disk.total / (1024**3), 2)
        },
        'processes': {
            'python': python_processes,
            'node': node_processes,
            'total': python_processes + node_processes
        },
        'uptime': uptime,
        'governance': governance,
        'healing': healing
    })

@app.route('/api/health')
def health_check():
    """Quick health check endpoint"""
    vdr_data = get_vdr_score()
    motia_online = check_service('http://localhost:3000/health')
    love_online = check_service('http://localhost:9001/health')
    
    healthy = (
        motia_online and 
        love_online and 
        vdr_data['vdr'] > 0.0
    )
    
    return jsonify({
        'healthy': healthy,
        'vdr': vdr_data['vdr'],
        'services_online': motia_online and love_online
    })

@app.route('/api/vdr')
def get_vdr():
    """Get VDR score only"""
    return jsonify(get_vdr_score())

@app.route('/api/run-health-check', methods=['POST'])
def run_health_check():
    """Trigger manual VDR calculation"""
    try:
        result = subprocess.run(
            ['python3', os.path.join(BASE_DIR, 'core', 'ouroboros.py')],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            vdr_data = get_vdr_score()
            return jsonify({
                'success': True,
                'vdr': vdr_data,
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/run-governance', methods=['POST'])
def run_governance():
    """Trigger manual governance cycle"""
    try:
        result = subprocess.run(
            ['python3', os.path.join(BASE_DIR, 'core', 'master_orchestrator.py'), 'quick'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/emergency-stop', methods=['POST'])
def emergency_stop():
    """Emergency stop all services"""
    try:
        # Kill all Python processes (except this one)
        current_pid = os.getpid()
        killed = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if (proc.info['pid'] != current_pid and 
                    'python' in proc.info['name'].lower() and
                    ('consciousness-os' in cmdline or 'core' in cmdline)):
                    proc.kill()
                    killed.append(proc.info['pid'])
            except:
                pass
        
        # Kill Node.js processes
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'node' in proc.info['name'].lower() and 'motia' in cmdline:
                    proc.kill()
                    killed.append(proc.info['pid'])
            except:
                pass
        
        return jsonify({
            'success': True,
            'killed_processes': killed,
            'message': 'Emergency stop executed'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/logs')
def get_logs():
    """Get recent system logs"""
    try:
        log_dir = os.path.join(MEMORY_DIR, 'logs')
        system_log = os.path.join(log_dir, 'system.log')
        
        if os.path.exists(system_log):
            with open(system_log, 'r') as f:
                lines = f.readlines()
                # Return last 100 lines
                recent = lines[-100:]
                return jsonify({
                    'logs': [line.strip() for line in recent]
                })
        else:
            return jsonify({'logs': []})
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/')
def index():
    """API info"""
    return jsonify({
        'name': 'Consciousness OS Health API',
        'version': '1.0.0',
        'endpoints': {
            '/api/status': 'Complete system status',
            '/api/health': 'Quick health check',
            '/api/vdr': 'VDR score only',
            '/api/run-health-check': 'Trigger VDR calculation (POST)',
            '/api/run-governance': 'Trigger governance cycle (POST)',
            '/api/emergency-stop': 'Emergency stop all services (POST)',
            '/api/logs': 'Recent system logs'
        }
    })

if __name__ == '__main__':
    print("Starting Consciousness OS Health API on port 8081...")
    print("Dashboard can query: http://localhost:8081/api/status")
    app.run(host='127.0.0.1', port=8081, debug=False)
