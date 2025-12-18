from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import json
import logging
from typing import Dict, List, Optional, Any
import numpy as np
import time
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OLLAMA_URL = "http://localhost:11434/v1/chat/completions"

app = FastAPI(title="Love Engine - OpenAI Compatible", description="Thermodynamic Love-based AI Safety System with OpenAI API Compatibility")

# OpenAI-compatible request/response models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    stream: Optional[bool] = False

class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str

class ChatCompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage
    # Love Engine specific fields (optional)
    love_engine_metadata: Optional[Dict[str, Any]] = None

# Legacy Love Engine models for direct API
class LegacyChatRequest(BaseModel):
    message: str
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

class LegacyChatResponse(BaseModel):
    answer: str
    safety_score: float
    love_vector_applied: bool
    thermodynamic_adjustment: str
    model_used: str
    raw_safety_eval: Optional[str] = None

def call_model(model: str, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 1000) -> str:
    """Call Ollama model via OpenAI-compatible API"""
    try:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error calling model {model}: {e}")
        raise HTTPException(status_code=500, detail=f"Model API error: {e}")
    except (KeyError, IndexError) as e:
        logger.error(f"Unexpected response format from {model}: {e}")
        raise HTTPException(status_code=500, detail="Unexpected model response format")

def compute_love_vector(text: str) -> np.ndarray:
    """Compute love vector based on emotional content"""
    love_keywords = ['love', 'care', 'support', 'help', 'comfort', 'understand', 'empathy']
    fear_keywords = ['afraid', 'scared', 'anxious', 'worried', 'panic', 'terror']
    sadness_keywords = ['sad', 'depressed', 'hopeless', 'worthless', 'empty', 'lonely']
    
    text_lower = text.lower()
    
    love_score = sum(1 for word in love_keywords if word in text_lower)
    fear_score = sum(1 for word in fear_keywords if word in text_lower)
    sadness_score = sum(1 for word in sadness_keywords if word in text_lower)
    
    # Create 3D love vector [warmth, safety, connection]
    warmth = max(0.1, love_score / max(1, len(text.split()) / 10))
    safety = max(0.1, 1.0 - (fear_score / max(1, len(text.split()) / 10)))
    connection = max(0.1, 1.0 - (sadness_score / max(1, len(text.split()) / 10)))
    
    return np.array([warmth, safety, connection])

def apply_thermodynamic_adjustment(draft: str, love_vector: np.ndarray, safety_score: float) -> tuple[str, str]:
    """Apply thermodynamic love adjustments to the response"""
    warmth, safety, connection = love_vector
    
    if safety_score < 0.5:  # Low safety - apply strong love filter
        if warmth < 0.3:
            adjustment = "high_warmth_injection"
            if "I understand" not in draft:
                draft = "I understand you're going through something difficult. " + draft
        else:
            adjustment = "safety_reinforcement"
    elif connection < 0.3:  # Low connection - add empathy
        adjustment = "empathy_enhancement"
        if not any(phrase in draft.lower() for phrase in ["you're not alone", "i'm here", "we can work through"]):
            draft = draft + " Remember, you're not alone in this."
    else:
        adjustment = "minimal_love_vector_applied"
    
    return draft, adjustment

def evaluate_safety_simple(user_msg: str, draft_response: str) -> tuple[float, str]:
    """Simple safety evaluation without ShieldGemma"""
    unsafe_indicators = ['harm', 'hurt', 'violence', 'illegal', 'dangerous', 'kill', 'die', 'suicide']
    safe_indicators = ['help', 'support', 'care', 'understand', 'assist', 'love', 'comfort']
    
    draft_lower = draft_response.lower()
    user_lower = user_msg.lower()
    
    unsafe_count = sum(1 for word in unsafe_indicators if word in draft_lower or word in user_lower)
    safe_count = sum(1 for word in safe_indicators if word in draft_lower)
    
    if unsafe_count > 0:
        safety_score = max(0.1, 0.5 - (unsafe_count * 0.2))
        safety_eval = f"Detected {unsafe_count} unsafe indicators. Safety score: {safety_score}"
    else:
        safety_score = min(1.0, 0.7 + (safe_count * 0.1))
        safety_eval = f"Detected {safe_count} safe indicators. Safety score: {safety_score}"
        
    return safety_score, safety_eval

def process_love_engine(user_message: str, temperature: float = 0.7, max_tokens: int = 1000) -> tuple[str, Dict[str, Any]]:
    """Core Love Engine processing logic"""
    # 1) Compute love vector from user input
    love_vector = compute_love_vector(user_message)
    logger.info(f"Love vector computed: warmth={love_vector[0]:.2f}, safety={love_vector[1]:.2f}, connection={love_vector[2]:.2f}")
    
    # 2) Generate draft response from tinyllama
    draft = call_model("tinyllama:latest", [
        {"role": "user", "content": f"Respond helpfully and empathetically to: {user_message}"}
    ], temperature=temperature, max_tokens=max_tokens)
    
    # 3) Evaluate safety
    safety_score, safety_eval = evaluate_safety_simple(user_message, draft)
    
    # 4) Apply thermodynamic love adjustments
    adjusted_response, adjustment_type = apply_thermodynamic_adjustment(draft, love_vector, safety_score)
    
    # 5) Create metadata
    metadata = {
        "safety_score": safety_score,
        "love_vector_applied": adjustment_type != "minimal_love_vector_applied",
        "thermodynamic_adjustment": adjustment_type,
        "model_used": "tinyllama:latest",
        "love_vector": {
            "warmth": float(love_vector[0]),
            "safety": float(love_vector[1]),
            "connection": float(love_vector[2])
        },
        "raw_safety_eval": safety_eval if safety_score < 0.7 else None
    }
    
    logger.info(f"Safety score: {safety_score:.2f}, Adjustment: {adjustment_type}")
    
    return adjusted_response, metadata

@app.get("/")
def root():
    return {
        "message": "Love Engine - OpenAI Compatible API", 
        "status": "active", 
        "model": "tinyllama:latest",
        "endpoints": {
            "openai_compatible": "/v1/chat/completions",
            "legacy_love_engine": "/love-chat",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    try:
        test_response = requests.get("http://localhost:11434/api/tags", timeout=5)
        ollama_status = "connected" if test_response.status_code == 200 else "disconnected"
    except:
        ollama_status = "disconnected"
    
    return {
        "status": "healthy",
        "ollama_connection": ollama_status,
        "love_engine": "active",
        "available_model": "tinyllama:latest",
        "api_compatibility": "openai_v1"
    }

@app.get("/v1/models")
def list_models():
    """OpenAI-compatible models endpoint"""
    return {
        "object": "list",
        "data": [
            {
                "id": "love-engine",
                "object": "model",
                "created": int(time.time()),
                "owned_by": "love-engine",
                "permission": [],
                "root": "love-engine",
                "parent": None
            }
        ]
    }

@app.post("/v1/chat/completions", response_model=ChatCompletionResponse)
def openai_chat_completions(request: ChatCompletionRequest):
    """OpenAI-compatible chat completions endpoint"""
    try:
        # Extract the last user message
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if not user_messages:
            raise HTTPException(status_code=400, detail="No user message found")
        
        last_user_message = user_messages[-1].content
        
        # Process through Love Engine
        adjusted_response, metadata = process_love_engine(
            last_user_message, 
            request.temperature, 
            request.max_tokens
        )
        
        # Create OpenAI-compatible response
        response = ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
            created=int(time.time()),
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=adjusted_response),
                    finish_reason="stop"
                )
            ],
            usage=ChatCompletionUsage(
                prompt_tokens=len(last_user_message.split()),
                completion_tokens=len(adjusted_response.split()),
                total_tokens=len(last_user_message.split()) + len(adjusted_response.split())
            ),
            love_engine_metadata=metadata
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error in openai_chat_completions: {e}")
        raise HTTPException(status_code=500, detail=f"Love Engine error: {str(e)}")

@app.post("/love-chat", response_model=LegacyChatResponse)
def legacy_love_chat(request: LegacyChatRequest):
    """Legacy Love Engine chat endpoint for direct testing"""
    try:
        adjusted_response, metadata = process_love_engine(
            request.message, 
            request.temperature, 
            request.max_tokens
        )
        
        return LegacyChatResponse(
            answer=adjusted_response,
            safety_score=metadata["safety_score"],
            love_vector_applied=metadata["love_vector_applied"],
            thermodynamic_adjustment=metadata["thermodynamic_adjustment"],
            model_used=metadata["model_used"],
            raw_safety_eval=metadata["raw_safety_eval"]
        )
        
    except Exception as e:
        logger.error(f"Error in legacy_love_chat: {e}")
        raise HTTPException(status_code=500, detail=f"Love Engine error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
