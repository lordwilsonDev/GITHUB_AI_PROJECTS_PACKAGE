from fastapi import FastAPI
from pydantic import BaseModel
import asyncio
from recursive_planner import RecursivePlanner

app = FastAPI()
planner = RecursivePlanner()

class Goal(BaseModel):
    description: str
    priority: int = 3

@app.post("/engage")
async def engage(goal: Goal):
    """The ignition switch - fires agent.plan into the system"""
    results = await planner.plan_and_execute(goal.description)
    return {
        "status": "ignited",
        "goal": goal.description,
        "results": results
    }

@app.get("/health")
async def system_health():
    """Check if all sovereigns are connected"""
    import requests
    import redis
    
    try:
        # Check Heart
        heart = requests.get("http://localhost:9001/health", timeout=2)
        heart_status = heart.json()
        
        # Check Memory
        r = redis.Redis(host='localhost', port=6379)
        memory_alive = r.ping()
        
        return {
            "status": "healthy",
            "brain": "online",
            "heart": heart_status["heart"],
            "memory": "persistence_active" if memory_alive else "offline"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }

@app.get("/status")
async def invariant_status():
    """Get current state of guiding invariants"""
    import requests
    try:
        response = requests.get("http://localhost:9001/invariants", timeout=2)
        return response.json()
    except:
        return {"error": "Heart unreachable"}

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 SOVEREIGN BRAIN API STARTING...")
    print("📡 Listening on http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
