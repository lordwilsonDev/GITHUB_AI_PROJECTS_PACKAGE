from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import Vector2, NanoProcessRequest, NanoProcessResponse
from affective_steering_core import AffectiveSteeringCore
import random
import os
from pathlib import Path
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

core = AffectiveSteeringCore()

def simulate_gemma_reasoning(chaos_mode: bool):
    if chaos_mode: return 6.0, 6.0 # Aggressive expansion
    return (random.random() - 0.5) * 4, (random.random() - 0.5) * 4

@app.get("/health")
async def health_check():
    """Health check endpoint for service monitoring"""
    return {"status": "healthy", "service": "moie-backend", "version": "1.0"}

@app.post("/api/process")
async def process_nano_file(request: NanoProcessRequest) -> NanoProcessResponse:
    """
    Process a .nano file from the dispatcher
    
    This endpoint receives code snippets captured by RADE, analyzes them,
    and generates improved versions with better practices, type hints, etc.
    """
    try:
        # Log the incoming request
        print(f"[MoIE] Processing nano file: {request.nano_file}")
        print(f"[MoIE] Function: {request.function}")
        print(f"[MoIE] Source: {request.source_path}")
        
        # TODO: Implement actual code analysis and improvement
        # For now, create a simple improved version with type hints
        improved_content = generate_improved_code(request.content, request.function)
        
        # Save the draft to nano_memory
        nano_memory = Path.home() / "nano_memory"
        nano_memory.mkdir(exist_ok=True)
        
        # Create draft filename
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        base_name = request.nano_file.replace(".nano", "")
        draft_filename = f"{base_name}_draft.nano"
        draft_path = nano_memory / draft_filename
        
        # Write the improved draft
        with open(draft_path, 'w') as f:
            f.write(f"# DRAFT - Improved by MoIE\n")
            f.write(f"# Original: {request.nano_file}\n")
            f.write(f"# Source: {request.source_path}\n")
            f.write(f"# Function: {request.function}\n")
            f.write(f"# Generated: {timestamp}\n\n")
            f.write(improved_content)
        
        print(f"[MoIE] Created draft: {draft_filename}")
        
        return NanoProcessResponse(
            status="success",
            message=f"Processed {request.function} successfully",
            draft_file=draft_filename
        )
        
    except Exception as e:
        print(f"[MoIE] Error processing {request.nano_file}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def generate_improved_code(original_code: str, function_name: str) -> str:
    """
    Generate improved version of code with better practices
    
    TODO: Integrate with actual LLM for sophisticated improvements
    For now, adds basic improvements like type hints and docstrings
    """
    lines = original_code.strip().split('\n')
    improved_lines = []
    
    # Add type hints import if not present
    if 'from typing import' not in original_code:
        improved_lines.append("from typing import Any, Optional, Union\n")
    
    for line in lines:
        # Skip existing comments at the top
        if line.strip().startswith('#') and not improved_lines:
            continue
            
        # Add type hints to function definitions
        if line.strip().startswith('def ') and '(' in line:
            # Simple type hint addition (basic implementation)
            if '->' not in line:
                line = line.rstrip() + ' -> Any:'
                if line.endswith('::'):
                    line = line[:-1]
            improved_lines.append(line)
            
            # Add docstring if missing
            if len(improved_lines) > 0:
                improved_lines.append('    """')
                improved_lines.append(f'    Improved version of {function_name}')
                improved_lines.append('    ')
                improved_lines.append('    TODO: Add detailed documentation')
                improved_lines.append('    """')
        else:
            improved_lines.append(line)
    
    return '\n'.join(improved_lines)

@app.post("/simulate")
async def run_simulation(current_pos: Vector2, chaos_mode: bool):
    state = (current_pos.x, current_pos.y)
    
    # 1. GET INPUT & STEP PHYSICS
    raw_ux, raw_uy = simulate_gemma_reasoning(chaos_mode)
    output = core.step(state, (raw_ux, raw_uy))
    
    # 2. METRICS (VDR penalizes filtering)
    vdr = 0.98
    if output.veto_cbf: vdr = 0.75
    if output.veto_simplex: vdr = 0.20

    # 3. RUNTIME INVARIANTS (The "Paper-Grade" Checks)
    if output.veto_simplex:
        hac_ux, hac_uy = core.u_hac(state[0], state[1])
        if abs(output.safe_action[0] - hac_ux) > 1e-5:
            print("CRITICAL: INVARIANT VIOLATION - Simplex flag set but Action != HAC")
    
    # 4. FORMAT LOGS
    frontend_logs = [{"source": "HPC" if "HPC" in l else "PANOPTICON", "msg": l} for l in output.logs]

    return {
        "raw_action": {"x": output.raw_action[0], "y": output.raw_action[1]},
        "safe_action": {"x": output.safe_action[0], "y": output.safe_action[1]},
        "barrier_value": max(0, output.h_val / (150**2)),
        "veto_status": output.veto_cbf or output.veto_simplex,
        "vdr": vdr,
        "logs": frontend_logs
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
