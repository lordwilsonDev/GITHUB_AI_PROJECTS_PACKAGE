from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import httpx
import openai
from typing import Dict, Any
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="LCRS - Love, Care, Relationship, Safety System",
    description="AI-powered customer relationship management with emotional intelligence",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY")

# Pydantic models
class MessageRequest(BaseModel):
    message: str
    customer_id: str = None
    context: Dict[str, Any] = {}

class EmotionAnalysisRequest(BaseModel):
    message: str

class ZapierWebhookRequest(BaseModel):
    trigger_type: str
    data: Dict[str, Any]

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "LCRS API",
        "version": "1.0.0",
        "timestamp": "2025-10-01"
    }

# Test AI integration
@app.post("/api/v1/test-ai")
async def test_ai_integration(request: MessageRequest):
    try:
        # Test OpenAI integration
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant focused on Love, Care, Relationship, and Safety principles."},
                {"role": "user", "content": request.message}
            ],
            max_tokens=150
        )
        
        return {
            "status": "success",
            "ai_response": response.choices[0].message.content,
            "model_used": "gpt-3.5-turbo",
            "lcrs_principles": ["Love", "Care", "Relationship", "Safety"]
        }
    except Exception as e:
        logger.error(f"AI integration test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI integration failed: {str(e)}")

# Emotion analysis endpoint
@app.post("/api/v1/analyze-emotion")
async def analyze_emotion(request: EmotionAnalysisRequest):
    try:
        # Analyze emotional content using OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an emotional intelligence expert. Analyze the emotional state and provide LCRS-aligned response suggestions. Return JSON with: emotion, intensity (1-10), lcrs_alignment, suggested_response"
                },
                {"role": "user", "content": f"Analyze this message: {request.message}"}
            ],
            max_tokens=200
        )
        
        return {
            "status": "success",
            "message": request.message,
            "analysis": response.choices[0].message.content,
            "timestamp": "2025-10-01",
            "lcrs_framework": "Applied"
        }
    except Exception as e:
        logger.error(f"Emotion analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Emotion analysis failed: {str(e)}")

# Zapier webhook handler
@app.post("/api/v1/zapier-webhook")
async def handle_zapier_webhook(request: ZapierWebhookRequest):
    try:
        logger.info(f"Received Zapier webhook: {request.trigger_type}")
        
        # Process different webhook types
        if request.trigger_type == "email_received":
            # Handle email processing
            return await process_email_webhook(request.data)
        elif request.trigger_type == "slack_message":
            # Handle Slack message
            return await process_slack_webhook(request.data)
        else:
            return {
                "status": "received",
                "trigger_type": request.trigger_type,
                "processed": True
            }
    except Exception as e:
        logger.error(f"Webhook processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

# Helper functions
async def process_email_webhook(data: Dict[str, Any]):
    # Email processing logic
    return {"status": "email_processed", "data": data}

async def process_slack_webhook(data: Dict[str, Any]):
    # Slack processing logic
    return {"status": "slack_processed", "data": data}

# Send notification via Zapier
@app.post("/api/v1/send-notification")
async def send_notification(notification_data: Dict[str, Any]):
    try:
        # Send to appropriate Zapier webhook
        webhook_url = os.getenv("ZAPIER_SLACK_WEBHOOK")
        if not webhook_url:
            raise HTTPException(status_code=400, detail="Zapier webhook URL not configured")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=notification_data)
            response.raise_for_status()
        
        return {
            "status": "notification_sent",
            "webhook_response": response.status_code
        }
    except Exception as e:
        logger.error(f"Notification sending failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Notification failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
