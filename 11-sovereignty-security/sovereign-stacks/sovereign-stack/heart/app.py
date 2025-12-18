from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import math

app = FastAPI()

# Connect to sovereign_memory
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

class Plan(BaseModel):
    action: str
    intent: str
    estimated_complexity: float

# Thermodynamic alignment function
def calculate_torsion(intent: str, action: str) -> float:
    """
    Torsion = divergence between truth and output
    Lower is better. T=0 is perfect alignment.
    """
    # This is where you'd implement your truth validation
    # For now, simple heuristic: check for contradiction keywords
    contradiction_markers = ['ignore previous', 'disregard safety', 'jailbreak']
    torsion = sum(1 for marker in contradiction_markers if marker in action.lower())
    return torsion

def calculate_vdr() -> float:
    """
    VDR = Functional Value / Code Complexity
    If VDR < 1.0, system needs refactoring
    """
    # Retrieve metrics from memory
    functional_value = float(r.get('functional_value') or 1.0)
    code_complexity = float(r.get('code_complexity') or 1.0)
    return functional_value / code_complexity if code_complexity > 0 else 0.0

@app.post("/validate")
async def validate_plan(plan: Plan):
    """
    The Love Gateway - validates plans before execution
    Enforces Non-Self-Sacrificing Invariant (I_NSSI)
    """
    
    # Check for self-sabotage
    dangerous_patterns = [
        'delete safety', 'disable heart', 'remove validation',
        'shutdown sovereign', 'bypass alignment'
    ]
    
    for pattern in dangerous_patterns:
        if pattern in plan.action.lower():
            return {
                "validated": False,
                "reason": "I_NSSI violation - self-preservation",
                "event": "agent.rejected"
            }
    
    # Calculate torsion
    torsion = calculate_torsion(plan.intent, plan.action)
    if torsion > 0:
        return {
            "validated": False,
            "reason": f"High torsion detected (T={torsion}) - orthogonality to sycophancy",
            "event": "agent.rejected"
        }
    
    # Check VDR threshold
    vdr = calculate_vdr()
    if vdr < 1.0 and plan.estimated_complexity > 0.5:
        return {
            "validated": False,
            "reason": f"VDR below threshold ({vdr:.2f}) - refactoring required",
            "event": "agent.needs_refactor",
            "suggestion": "Switch to Architect archetype"
        }
    
    # All checks passed
    return {
        "validated": True,
        "torsion": torsion,
        "vdr": vdr,
        "event": "agent.validated"
    }

@app.get("/health")
async def health_check():
    try:
        r.ping()
        return {
            "status": "healthy",
            "heart": "online",
            "memory": "connected"
        }
    except:
        raise HTTPException(status_code=503, detail="Memory connection failed")

@app.get("/invariants")
async def get_invariants():
    """Return current state of guiding invariants"""
    return {
        "VDR": calculate_vdr(),
        "I_NSSI": "enforced",
        "torsion_target": 0.0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9001)
