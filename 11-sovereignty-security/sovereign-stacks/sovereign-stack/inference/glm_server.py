from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import uvicorn

app = FastAPI()
model = None
tokenizer = None

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    max_tokens: int = 512
    temperature: float = 0.7

def load_model():
    global model, tokenizer
    print("🚀 Loading GLM-4V-9B... (This will take a minute)")
    # UPDATE THIS PATH if your model is elsewhere
    model_path = "/Users/lordwilson/sovereign-stack/models/glm-4v-9b"
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
            device_map="auto"
        ).eval()
        print("✅ Model loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading model: {e}")

@app.on_event("startup")
async def startup_event():
    load_model()

@app.get("/health")
async def health_check():
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    return {"status": "healthy", "model": "glm-4v-9b"}

@app.post("/v1/chat/completions")
async def chat_completion(request: ChatRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
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
            temperature=request.temperature
        )
    
    response_text = tokenizer.decode(outputs[0][len(inputs["input_ids"][0]):], skip_special_tokens=True)
    
    return {"choices": [{"message": {"role": "assistant", "content": response_text}}]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8100)
