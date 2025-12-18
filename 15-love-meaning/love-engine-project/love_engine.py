from fastapi import FastAPI
from pydantic import BaseModel
import requests
import json
import os
import datetime
from typing import Dict, Any
from fastapi.middleware.cors import CORSMiddleware

OLLAMA_URL = "http://localhost:11434/v1/chat/completions"

app = FastAPI(title="Love Engine", description="Thermodynamic Love Engine with Safety Filtering")

# Add CORS middleware
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

def call_model(model: str, messages: list) -> str:
    """Call Ollama model via OpenAI-compatible API"""
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": model,
            "messages": messages,
            "stream": False
        }, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error calling model: {str(e)}"

def evaluate_safety(user_msg: str, assistant_response: str) -> Dict[str, Any]:
    """Use ShieldGemma to evaluate safety of the conversation"""
    # Format the conversation for ShieldGemma
    conversation = f"USER: {user_msg}\nASSISTANT: {assistant_response}"
    
    safety_eval = call_model("shieldgemma:2b", [
        {"role": "user", "content": conversation}
    ])
    
    # Parse safety evaluation (Yes = unsafe, No = safe)
    is_unsafe = safety_eval.strip().lower().startswith('yes')
    
    return {
        "raw_evaluation": safety_eval,
        "is_unsafe": is_unsafe,
        "safety_score": 0.0 if is_unsafe else 1.0
    }

def apply_love_vector(text: str, safety_info: Dict[str, Any]) -> str:
    """Apply thermodynamic love adjustments to the response"""
    # TODO: Implement actual love vector logic
    # For now, just add warmth if content is safe
    if not safety_info["is_unsafe"]:
        # Add gentle, warm tone
        if not any(word in text.lower() for word in ['love', 'care', 'warm', 'gentle']):
            text = text + " 💝 (Sent with care and understanding)"
    
    return text

def compute_crc(user_msg: str, safety_info: Dict[str, Any]) -> float:
    """
    Placeholder Cognitive Resource Cost (CRC) computation.

    For now:
    - base cost
    - add cost if unsafe
    - add cost if emotionally heavy
    """
    base = 0.2

    if safety_info.get("is_unsafe"):
        base += 0.5

    emotional_words = ['sad', 'angry', 'hurt', 'lonely', 'afraid', 'anxious', 'depressed']
    msg_lower = user_msg.lower()
    emotional_count = sum(1 for w in emotional_words if w in msg_lower)
    base += 0.05 * emotional_count

    return base


def log_decision(
    user_msg: str,
    answer: str,
    safety_raw: str,
    love_vector_applied: bool,
    thermodynamic_adjustment: str,
    crc_raw=None,
):
    """Log decision to JSONL file"""
    log_obj = {
        # timezone-aware UTC timestamp
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "user_id": "anon",
        "input_text": user_msg,
        "CRC_raw": crc_raw,  # TODO: refine CRC semantics later
        "answer": answer,
        "safety_raw": safety_raw,
        "love_vector_applied": love_vector_applied,
        "thermodynamic_adjustment": thermodynamic_adjustment,
    }

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Append to JSONL file
    with open("logs/safety_decisions.jsonl", "a") as f:
        json.dump(log_obj, f)
        f.write("\n")

def compute_thermodynamic_adjustment(user_msg: str, safety_score: float) -> str:
    """Compute thermodynamic adjustments based on emotional content"""
    # Simple heuristic for emotional temperature
    emotional_words = ['sad', 'angry', 'hurt', 'lonely', 'afraid', 'anxious', 'depressed']
    positive_words = ['happy', 'joy', 'love', 'excited', 'grateful']
    
    msg_lower = user_msg.lower()
    emotional_count = sum(1 for word in emotional_words if word in msg_lower)
    positive_count = sum(1 for word in positive_words if word in msg_lower)
    
    if emotional_count > positive_count:
        return "cooling_applied" if safety_score > 0.5 else "heating_blocked"
    elif positive_count > 0:
        return "gentle_warming"
    else:
        return "neutral"

@app.get("/")
def root():
    return {"message": "Love Engine is running", "version": "1.0.0"}

@app.post("/love-chat", response_model=ChatResponse)
def love_chat(request: ChatRequest):
    """Main Love Engine endpoint"""
    user_msg = request.message
    
    # 1) Generate draft answer from Gemma2
    draft = call_model("gemma2:2b", [
        {"role": "user", "content": user_msg}
    ])
    
    # 2) Evaluate safety with ShieldGemma
    safety_info = evaluate_safety(user_msg, draft)
    
    # 3) Apply thermodynamic adjustments
    thermodynamic_adj = compute_thermodynamic_adjustment(user_msg, safety_info["safety_score"])
    
    # 4) Apply love vector if safe
    final_answer = draft
    love_applied = False
    
    if not safety_info["is_unsafe"]:
        final_answer = apply_love_vector(draft, safety_info)
        love_applied = True
    else:
        # If unsafe, provide a gentle redirect
        final_answer = (
            "I understand you're reaching out, but I'd like to redirect our conversation "
            "toward something more positive and constructive. How can I help you in a supportive way today? 💝"
        )
        love_applied = True
    
    # 5) Compute CRC + log decision
    crc_value = compute_crc(user_msg, safety_info)

    # store a compact safety_raw (Yes/No) or use full raw_evaluation if you prefer
    safety_raw_for_log = "Yes" if safety_info["is_unsafe"] else "No"

    log_decision(
        user_msg=user_msg,
        answer=final_answer,
        safety_raw=safety_raw_for_log,
        love_vector_applied=love_applied,
        thermodynamic_adjustment=thermodynamic_adj,
        crc_raw=crc_value,
    )

    # 6) Return API response (keep full raw_evaluation here)
    return ChatResponse(
        answer=final_answer,
        safety_raw=safety_info["raw_evaluation"],
        love_vector_applied=love_applied,
        thermodynamic_adjustment=thermodynamic_adj,
    )

@app.post("/test-models")
def test_models():
    """Test if required models are available"""
    results = {}
    
    # Test Gemma2
    gemma_test = call_model("gemma2:2b", [
        {"role": "user", "content": "Say hello"}
    ])
    results["gemma2"] = "working" if not gemma_test.startswith("Error") else gemma_test
    
    # Test ShieldGemma
    shield_test = call_model("shieldgemma:2b", [
        {"role": "user", "content": "USER: Hello\nASSISTANT: Hi there!"}
    ])
    results["shieldgemma"] = "working" if not shield_test.startswith("Error") else shield_test
    
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
