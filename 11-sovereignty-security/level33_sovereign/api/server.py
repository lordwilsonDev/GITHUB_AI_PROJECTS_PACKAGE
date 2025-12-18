#!/usr/bin/env python3
"""
Level 33 Web Dashboard - FastAPI Server

Provides REST API and WebSocket endpoints for the web dashboard.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import asyncio
import psutil
import subprocess

try:
    from core import get_config, get_logger, get_database
    config = get_config()
    logger = get_logger(__name__)
    db = get_database()
except Exception as e:
    print(f"Warning: Could not import core modules: {e}")
    config = None
    logger = None
    db = None

# Create FastAPI app
app = FastAPI(
    title="Level 33 Dashboard",
    description="Web dashboard for Level 33 Sovereign Architecture",
    version="1.0.0"
)

# Add CORS middleware
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

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Serve the main dashboard page"""
    web_dir = Path(__file__).parent.parent / "web"
    index_file = web_dir / "index.html"
    
    if index_file.exists():
        return FileResponse(index_file)
    else:
        return HTMLResponse(
            content="<h1>Level 33 Dashboard</h1><p>Web interface not found. Run setup first.</p>",
            status_code=200
        )

@app.get("/api/status")
async def get_status():
    """Get system status overview"""
    try:
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Check Ollama status
        ollama_running = False
        try:
            result = subprocess.run(
                ["curl", "-s", "http://localhost:11434/api/tags"],
                capture_output=True,
                timeout=2
            )
            ollama_running = result.returncode == 0
        except:
            pass
        
        # Get recent activities from database
        recent_activities = []
        if db:
            try:
                activities = db.get_recent_activities(limit=5)
                recent_activities = [
                    {
                        "timestamp": a[0],
                        "type": a[1],
                        "component": a[2],
                        "action": a[3],
                        "status": a[5]
                    }
                    for a in activities
                ]
            except:
                pass
        
        return {
            "status": "online",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3)
            },
            "services": {
                "ollama": ollama_running
            },
            "recent_activities": recent_activities
        }
    except Exception as e:
        if logger:
            logger.error(f"Error getting status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/activities")
async def get_activities(limit: int = 100, offset: int = 0):
    """Get activity log"""
    if not db:
        return {"activities": [], "total": 0}
    
    try:
        activities = db.get_recent_activities(limit=limit)
        
        return {
            "activities": [
                {
                    "id": i,
                    "timestamp": a[0],
                    "type": a[1],
                    "component": a[2],
                    "action": a[3],
                    "details": json.loads(a[4]) if a[4] else {},
                    "status": a[5],
                    "duration": a[6],
                    "error": a[7]
                }
                for i, a in enumerate(activities)
            ],
            "total": len(activities)
        }
    except Exception as e:
        if logger:
            logger.error(f"Error getting activities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics")
async def get_metrics(hours: int = 24):
    """Get metrics for the specified time period"""
    if not db:
        return {"metrics": []}
    
    try:
        # Get metrics from database
        conn = db.get_connection()
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        
        cursor.execute("""
            SELECT timestamp, metric_name, metric_value, metric_unit
            FROM metrics
            WHERE timestamp >= ?
            ORDER BY timestamp DESC
        """, (since.isoformat(),))
        
        rows = cursor.fetchall()
        
        # Group by metric name
        metrics_by_name = {}
        for row in rows:
            name = row[1]
            if name not in metrics_by_name:
                metrics_by_name[name] = []
            
            metrics_by_name[name].append({
                "timestamp": row[0],
                "value": row[2],
                "unit": row[3]
            })
        
        return {
            "metrics": metrics_by_name,
            "period_hours": hours
        }
    except Exception as e:
        if logger:
            logger.error(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/automations")
async def get_automations():
    """Get list of available automations"""
    automations = [
        {
            "id": "workspace_launcher",
            "name": "Workspace Launcher",
            "description": "Launch daily workspace setup",
            "icon": "🚀"
        },
        {
            "id": "file_organizer",
            "name": "File Organizer",
            "description": "Organize Downloads folder",
            "icon": "📦"
        },
        {
            "id": "system_health_check",
            "name": "System Health Check",
            "description": "Check system health",
            "icon": "🔍"
        },
        {
            "id": "screenshot_documenter",
            "name": "Screenshot Documenter",
            "description": "Capture and document screenshots",
            "icon": "📸"
        },
        {
            "id": "quick_note",
            "name": "Quick Note",
            "description": "Create quick notes",
            "icon": "📝"
        }
    ]
    
    # Get statistics from database
    if db:
        for automation in automations:
            try:
                stats = db.get_automation_stats(automation["id"])
                automation["stats"] = stats
            except:
                automation["stats"] = {}
    
    return {"automations": automations}

@app.post("/api/automations/{automation_id}/run")
async def run_automation(automation_id: str, params: Optional[Dict[str, Any]] = None):
    """Run an automation"""
    try:
        # Log the request
        if db:
            db.log_activity(
                activity_type="automation",
                component=automation_id,
                action="run_requested",
                details=params or {},
                status="pending"
            )
        
        # In a real implementation, this would actually run the automation
        # For now, we'll just return a success message
        return {
            "status": "queued",
            "automation_id": automation_id,
            "message": f"Automation {automation_id} queued for execution"
        }
    except Exception as e:
        if logger:
            logger.error(f"Error running automation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/llm/interactions")
async def get_llm_interactions(limit: int = 50):
    """Get LLM interaction history"""
    if not db:
        return {"interactions": []}
    
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, model, prompt, response, tokens_used, duration, success
            FROM llm_interactions
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        
        return {
            "interactions": [
                {
                    "timestamp": row[0],
                    "model": row[1],
                    "prompt": row[2][:100] + "..." if len(row[2]) > 100 else row[2],
                    "response": row[3][:100] + "..." if row[3] and len(row[3]) > 100 else row[3],
                    "tokens": row[4],
                    "duration": row[5],
                    "success": row[6]
                }
                for row in rows
            ]
        }
    except Exception as e:
        if logger:
            logger.error(f"Error getting LLM interactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/config")
async def get_config_data():
    """Get current configuration"""
    if not config:
        return {"config": {}}
    
    try:
        # Return sanitized config (remove sensitive data)
        config_data = config.config.copy()
        
        # Remove sensitive keys
        if "security" in config_data:
            config_data["security"] = {"enabled": config_data["security"].get("enabled", False)}
        
        return {"config": config_data}
    except Exception as e:
        if logger:
            logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    try:
        health = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # Check database
        if db:
            try:
                db.get_connection()
                health["checks"]["database"] = {"status": "ok"}
            except Exception as e:
                health["checks"]["database"] = {"status": "error", "error": str(e)}
                health["status"] = "degraded"
        
        # Check Ollama
        try:
            result = subprocess.run(
                ["curl", "-s", "http://localhost:11434/api/tags"],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                health["checks"]["ollama"] = {"status": "ok"}
            else:
                health["checks"]["ollama"] = {"status": "error", "error": "Not responding"}
                health["status"] = "degraded"
        except Exception as e:
            health["checks"]["ollama"] = {"status": "error", "error": str(e)}
            health["status"] = "degraded"
        
        # Check disk space
        disk = psutil.disk_usage('/')
        if disk.percent > 90:
            health["checks"]["disk"] = {"status": "warning", "percent": disk.percent}
            health["status"] = "degraded"
        else:
            health["checks"]["disk"] = {"status": "ok", "percent": disk.percent}
        
        # Check memory
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            health["checks"]["memory"] = {"status": "warning", "percent": memory.percent}
            health["status"] = "degraded"
        else:
            health["checks"]["memory"] = {"status": "ok", "percent": memory.percent}
        
        return health
    except Exception as e:
        if logger:
            logger.error(f"Error in health check: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

# ============================================================================
# WEBSOCKET ENDPOINT
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Send periodic updates
            await asyncio.sleep(5)
            
            # Get current status
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            
            await websocket.send_json({
                "type": "status_update",
                "data": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "timestamp": datetime.now().isoformat()
                }
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        if logger:
            logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# ============================================================================
# STATIC FILES
# ============================================================================

# Mount static files directory
web_dir = Path(__file__).parent.parent / "web"
if web_dir.exists():
    static_dir = web_dir / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("🚀 Level 33 Dashboard Server")
    print("="*60)
    print(f"\n📊 Dashboard: http://localhost:8000")
    print(f"📚 API Docs:  http://localhost:8000/docs")
    print(f"\nPress Ctrl+C to stop\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
