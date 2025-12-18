from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

app = FastAPI()

model = None
tokenizer = None

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    max_tokens: int = 2048
    temperature: float = 0.7

def load_model():
    global model, tokenizer
    
    print("🧠 Loading GLM-4V-9B model into memory...")
    print("   This takes 30-90 seconds - be patient!")
    model_path = "/Users/lordwilson/sovereign-stack/models/glm-4v-9b"
    
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        trust_remote_code=True
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
        device_map="auto",
        low_cpu_mem_usage=True
    ).eval()
    
    print("✅ Model loaded successfully!")
    print("   Native multimodal cognitive engine ONLINE")

@app.on_event("startup")
async def startup_event():
    load_model()

@app.get("/health")
async def health_check():
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        "status": "healthy",
        "model": "glm-4v-9b",
        "cognitive_engine": "online",
        "native_multimodal": True,
        "context_window": 128000,
        "sovereignty": "full"
    }

@app.post("/v1/chat/completions")
async def chat_completion(request: ChatRequest):
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        conversation = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        inputs = tokenizer.apply_chat_template(
            conversation,
            add_generation_prompt=True,
            tokenize=True,
            return_tensors="pt",
            return_dict=True
        ).to(model.device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=request.max_tokens,
                temperature=request.temperature,
                do_sample=True,
                top_p=0.95
            )
        
        response_text = tokenizer.decode(
            outputs[0][len(inputs['input_ids'][0]):],
            skip_special_tokens=True
        )
        
        return {
            "id": "chatcmpl-glm4v",
            "object": "chat.completion",
            "model": "glm-4v-9b",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.get("/v1/model")
async def get_model_info():
    return {
        "model": "glm-4v-9b",
        "parameters": "9B",
        "context_window": 128000,
        "native_multimodal": True,
        "deployment": "local_sovereign",
        "capabilities": [
            "text_generation",
            "vision_understanding",
            "native_tool_calling",
            "pixel_accurate_replication",
            "128k_context"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 SOVEREIGN COGNITIVE ENGINE - GLM-4V")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=8100)
