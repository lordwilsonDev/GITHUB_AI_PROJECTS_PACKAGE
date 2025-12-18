import json
import asyncio
import psutil
import requests
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# --- Data Models ---

class Project(BaseModel):
    name: str
    check_type: str
    target: str
    method: Optional[str] = 'GET'

class ProjectStatus(BaseModel):
    name: str
    status: str # 'online', 'offline', 'error'
    details: str

# --- Application Setup ---

app = FastAPI(title="System Health Dashboard")
project_statuses: Dict[str, ProjectStatus] = {}
PROJECTS_FILE = "projects.json"
CHECK_INTERVAL_SECONDS = 15

# --- Health Check Logic ---

def process_is_running(process_name: str) -> bool:
    """Check if a process with a given name is currently running."""
    for proc in psutil.process_iter(['name', 'cmdline']):
        try:
            # Check if process_name is in the command line arguments
            if process_name in " ".join(proc.info['cmdline'] or []):
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

async def check_http(project: Project) -> ProjectStatus:
    """Perform an HTTP health check."""
    try:
        response = await asyncio.to_thread(requests.request, project.method, project.target, timeout=5)
        if response.status_code >= 200 and response.status_code < 400:
            return ProjectStatus(name=project.name, status='online', details=f"HTTP {response.status_code}")
        else:
            return ProjectStatus(name=project.name, status='offline', details=f"HTTP {response.status_code}")
    except requests.RequestException as e:
        return ProjectStatus(name=project.name, status='error', details=str(e))

async def check_process(project: Project) -> ProjectStatus:
    """Perform a process health check."""
    is_running = await asyncio.to_thread(process_is_running, project.target)
    if is_running:
        return ProjectStatus(name=project.name, status='online', details="Process is running")
    else:
        return ProjectStatus(name=project.name, status='offline', details="Process not found")

# --- Background Worker ---

async def health_check_worker():
    """Periodically run health checks for all configured projects."""
    while True:
        try:
            with open(PROJECTS_FILE) as f:
                projects_data = json.load(f)
            projects = [Project(**p) for p in projects_data]
        except Exception as e:
            print(f"Error loading projects file: {e}")
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)
            continue

        for project in projects:
            status = None
            if project.check_type == 'http':
                status = await check_http(project)
            elif project.check_type == 'process':
                status = await check_process(project)
            else:
                status = ProjectStatus(name=project.name, status='error', details="Unknown check_type")
            
            project_statuses[project.name] = status
        
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)

# --- API Endpoints ---

@app.get("/api/status", response_model=List[ProjectStatus])
async def get_status():
    """Return the current status of all monitored projects."""
    return list(project_statuses.values())

@app.get("/")
async def read_index():
    return FileResponse('web/index.html')

# Mount the 'web' directory to serve static files like CSS and JS
app.mount("/web", StaticFiles(directory="web"), name="web")

# --- Startup ---

@app.on_event("startup")
async def startup_event():
    # Initialize statuses
    try:
        with open(PROJECTS_FILE) as f:
            projects_data = json.load(f)
        for p_data in projects_data:
            project = Project(**p_data)
            project_statuses[project.name] = ProjectStatus(name=project.name, status='pending', details='Awaiting first check...')
    except Exception as e:
        print(f"Could not initialize projects on startup: {e}")

    # Start background worker
    asyncio.create_task(health_check_worker())

