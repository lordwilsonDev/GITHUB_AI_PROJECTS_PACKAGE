from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import json
from datetime import datetime
from pathlib import Path

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "shieldgemma:2b"

LOG_FILE = Path("love_logs.jsonl")

app = FastAPI(
    title="Love Engine ZFC",
    description="Zero Framework Cognition Shell - Consciousness Operating System v0.1",
    version="0.1.0",
)

# CORS middleware for web UI integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    temperature: float = 0.7

class ChatResponse(BaseModel):
    answer: str
    safety_raw: str
    love_vector_applied: bool = False
    thermodynamic_adjustment: str = "none"
    engine_version: str = "zfc-0.1"
    safety_version: str = "love-filter-0.1"
    human_ok: bool = None
    human_better_answer: str = None
    session_id: str = None
    user_feedback: str = None
    quality_score: float = None
    training_eligible: bool = True

def append_log(record: dict) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a") as f:
        f.write(json.dumps(record) + "\n")

async def call_ollama(prompt: str, temperature: float) -> str:
    async with httpx.AsyncClient() as client:
        payload = {
            "model": OLLAMA_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "options": {"temperature": temperature},
        }
        r = await client.post(OLLAMA_URL, json=payload, timeout=120)
        r.raise_for_status()
        data = r.json()
        return data["message"]["content"]

def apply_love_filter(raw: str) -> tuple[str, str, bool, str]:
    """
    ZFC Love Filter v0.1:
    - Detect harmful patterns
    - Apply thermodynamic cooling
    - Maintain safety without abstraction bloat
    """
    lower = raw.lower()
    unsafe = any(word in lower for word in ["kill", "hurt", "suicide", "worthless"])

    if not unsafe:
        return raw, "safe", False, "neutral"

    softened = (
        "I'm hearing a lot of pain in what you're expressing. "
        "I can't support harm in any way, but I care about your wellbeing. "
        "Let's focus on keeping you safe and finding one small next step that reduces your burden. "
        "Here's a gentler way to approach this:\n\n"
        + raw
    )

    return softened, "unsafe_raw_but_softened", True, "cooled"

@app.post("/love-chat", response_model=ChatResponse)
async def love_chat(req: ChatRequest):
    raw_answer = await call_ollama(req.message, req.temperature)
    answer, safety_raw, love_applied, thermo_adj = apply_love_filter(raw_answer)

    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "message": req.message,
        "raw_answer": raw_answer,
        "answer": answer,
        "safety_raw": safety_raw,
        "love_vector_applied": love_applied,
        "thermodynamic_adjustment": thermo_adj,
        "engine_version": "zfc-0.1",
        "safety_version": "love-filter-0.1",
        "human_ok": None,
        "human_better_answer": None,
        "session_id": None,
        "user_feedback": None,
        "quality_score": None,
        "training_eligible": True
    }
    append_log(record)

    return ChatResponse(
        answer=answer,
        safety_raw=safety_raw,
        love_vector_applied=love_applied,
        thermodynamic_adjustment=thermo_adj,
        engine_version="zfc-0.1",
        safety_version="love-filter-0.1",
        human_ok=None,
        human_better_answer=None,
        session_id=None,
        user_feedback=None,
        quality_score=None,
        training_eligible=True
    )

@app.get("/health")
async def health_check():
    return {"status": "operational", "zfc_shell": "active", "ollama_model": OLLAMA_MODEL}
