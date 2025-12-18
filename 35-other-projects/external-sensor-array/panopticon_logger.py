#!/usr/bin/env python3
"""
Panopticon Logger Service - Port 9004
Immutable audit trail for agent decisions
Cryptographic hashing and state logging
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import sqlite3
import hashlib
import json

app = FastAPI(title="Panopticon Logger", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DB_PATH = "/Users/lordwilson/external-sensor-array/panopticon.db"

def init_db():
    """Initialize SQLite database for immutable logs"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS decision_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            agent_id TEXT NOT NULL,
            decision_type TEXT NOT NULL,
            goal TEXT,
            action TEXT,
            reasoning TEXT,
            torsion_metric REAL,
            axiom_violations TEXT,
            state_hash TEXT NOT NULL,
            previous_hash TEXT,
            UNIQUE(state_hash)
        )
    ''')
    
    c.execute('''
        CREATE INDEX IF NOT EXISTS idx_timestamp ON decision_log(timestamp)
    ''')
    
    c.execute('''
        CREATE INDEX IF NOT EXISTS idx_agent ON decision_log(agent_id)
    ''')
    
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

class DecisionLog(BaseModel):
    agent_id: str
    decision_type: str  # plan, execute, veto, approve
    goal: Optional[str] = None
    action: Optional[str] = None
    reasoning: Optional[str] = None
    torsion_metric: Optional[float] = 0.0
    axiom_violations: Optional[List[str]] = []

class LogResponse(BaseModel):
    logged: bool
    log_id: int
    state_hash: str
    chain_verified: bool

def calculate_state_hash(log: DecisionLog, previous_hash: str) -> str:
    """
    Creates cryptographic hash of current state + previous hash
    This creates an immutable chain
    """
    state_data = f"{log.agent_id}|{log.decision_type}|{log.goal}|{log.action}|{previous_hash}"
    return hashlib.sha256(state_data.encode()).hexdigest()

def get_latest_hash(agent_id: str) -> Optional[str]:
    """Get the most recent hash for an agent to continue the chain"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT state_hash FROM decision_log 
        WHERE agent_id = ? 
        ORDER BY timestamp DESC 
        LIMIT 1
    ''', (agent_id,))
    
    result = c.fetchone()
    conn.close()
    
    return result[0] if result else None

@app.post("/log", response_model=LogResponse)
async def log_decision(log: DecisionLog):
    """
    Log a decision with cryptographic chaining
    """
    # Get previous hash to continue chain
    previous_hash = get_latest_hash(log.agent_id) or "GENESIS"
    
    # Calculate current state hash
    state_hash = calculate_state_hash(log, previous_hash)
    
    # Store in database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        c.execute('''
            INSERT INTO decision_log 
            (timestamp, agent_id, decision_type, goal, action, reasoning, 
             torsion_metric, axiom_violations, state_hash, previous_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.utcnow().isoformat(),
            log.agent_id,
            log.decision_type,
            log.goal,
            log.action,
            log.reasoning,
            log.torsion_metric,
            json.dumps(log.axiom_violations),
            state_hash,
            previous_hash
        ))
        
        conn.commit()
        log_id = c.lastrowid
        
        # Verify chain integrity
        chain_verified = verify_chain(log.agent_id)
        
        return LogResponse(
            logged=True,
            log_id=log_id,
            state_hash=state_hash,
            chain_verified=chain_verified
        )
    
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=409, detail="Duplicate state hash detected")
    finally:
        conn.close()

def verify_chain(agent_id: str) -> bool:
    """Verify integrity of the entire chain for an agent"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT state_hash, previous_hash 
        FROM decision_log 
        WHERE agent_id = ? 
        ORDER BY timestamp ASC
    ''', (agent_id,))
    
    rows = c.fetchall()
    conn.close()
    
    for i in range(1, len(rows)):
        current_hash, previous_hash = rows[i]
        expected_previous = rows[i-1][0]
        
        if previous_hash != expected_previous:
            return False
    
    return True

@app.get("/audit/{agent_id}")
async def get_audit_trail(agent_id: str, limit: int = 100):
    """
    Retrieve audit trail for an agent
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        SELECT timestamp, decision_type, goal, action, torsion_metric, state_hash
        FROM decision_log 
        WHERE agent_id = ? 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (agent_id, limit))
    
    rows = c.fetchall()
    conn.close()
    
    return {
        "agent_id": agent_id,
        "trail_length": len(rows),
        "chain_verified": verify_chain(agent_id),
        "decisions": [
            {
                "timestamp": row[0],
                "type": row[1],
                "goal": row[2],
                "action": row[3],
                "torsion": row[4],
                "hash": row[5]
            }
            for row in rows
        ]
    }

@app.get("/health")
async def health_check():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM decision_log')
    total_logs = c.fetchone()[0]
    conn.close()
    
    return {
        "status": "operational",
        "service": "Panopticon Logger",
        "port": 9004,
        "total_logs": total_logs,
        "db_path": DB_PATH
    }

if __name__ == "__main__":
    import uvicorn
    print("👁️ Starting Panopticon Logger on port 9004...")
    uvicorn.run(app, host="0.0.0.0", port=9004)
