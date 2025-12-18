from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
import httpx
import json
from datetime import datetime
from pathlib import Path
from config import get_settings, LoveEngineSettings
import asyncio
import logging
from error_handling import (
    retry_with_fallback, 
    FallbackStrategy, 
    RobotError, 
    OllamaConnectionError,
    ollama_circuit_breaker,
    log_error_with_context
)
from safety_system import safety_filter
from validation_system import validator, ValidationLevel
from energy_system import energy_manager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize our robot with settings from the backpack!
def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title=f"{settings.robot_name} - Love Engine",
        description=f"""
        🤖 {settings.robot_name} - Your Super-Smart Robot Friend!
        
        This Love Engine uses thermodynamic principles to make conversations
        warmer, safer, and more helpful. Built with antifragility - it gets
        stronger when things go wrong!
        
        Version: {settings.engine_version}
        Safety System: {settings.safety_version}
        """,
        version=settings.engine_version,
    )
    
    logger.info(f"Starting {settings.robot_name}...")
    logger.info(settings.get_description())
    
    return app

app = create_app()

class ChatRequest(BaseModel):
    message: str
    temperature: float = 0.7

class ChatResponse(BaseModel):
    answer: str
    safety_raw: str
    love_vector_applied: bool = False
    thermodynamic_adjustment: str = "none"

def append_log(record: dict, settings: LoveEngineSettings) -> None:
    """Write to our robot's diary! 📝"""
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Add robot identity to the log entry
    record.update({
        "robot_name": settings.robot_name,
        "engine_version": settings.engine_version,
        "safety_version": settings.safety_version
    })
    
    with log_file.open("a") as f:
        f.write(json.dumps(record) + "\n")
        
    logger.info(f"Logged interaction: {record.get('message', 'N/A')[:50]}...")

@retry_with_fallback(
    max_retries=3,
    delay=1.0,
    backoff_multiplier=2.0,
    fallback_strategies=[
        FallbackStrategy.OFFLINE_MODE,
        FallbackStrategy.SIMPLE_RESPONSE
    ]
)
async def call_ollama(prompt: str, temperature: float, settings: LoveEngineSettings) -> str:
    """
    Talk to our robot's AI brain! 🧠
    
    Enhanced with the full "Try Again" dance system:
    1. Circuit breaker protection
    2. Exponential backoff
    3. Multiple fallback strategies
    4. Never gives up completely!
    """
    
    async def _make_ollama_request():
        async with httpx.AsyncClient(timeout=settings.timeout_seconds) as client:
            payload = {
                "model": settings.ollama_model,
                "messages": [{"role": "user", "content": prompt}],
                "options": {"temperature": temperature},
            }
            
            logger.info(f"🧠 Calling Ollama with model {settings.ollama_model}...")
            
            try:
                r = await client.post(settings.ollama_url, json=payload)
                r.raise_for_status()
                data = r.json()
                
                response = data["message"]["content"]
                logger.info(f"✅ Success! Got response: {response[:100]}...")
                return response
                
            except httpx.ConnectError as e:
                log_error_with_context(e, {
                    "ollama_url": settings.ollama_url,
                    "model": settings.ollama_model,
                    "prompt_length": len(prompt)
                })
                raise OllamaConnectionError(f"Cannot connect to Ollama at {settings.ollama_url}: {str(e)}")
                
            except httpx.TimeoutException as e:
                log_error_with_context(e, {
                    "timeout_seconds": settings.timeout_seconds,
                    "prompt_length": len(prompt)
                })
                raise OllamaConnectionError(f"Ollama request timed out after {settings.timeout_seconds}s: {str(e)}")
                
            except httpx.HTTPStatusError as e:
                log_error_with_context(e, {
                    "status_code": e.response.status_code,
                    "response_text": e.response.text[:200]
                })
                raise OllamaConnectionError(f"Ollama returned error {e.response.status_code}: {e.response.text}")
    
    # Use circuit breaker to protect against repeated failures
    try:
        result = await ollama_circuit_breaker.call(_make_ollama_request)
        
        # If we get a dict (fallback response), return the answer part
        if isinstance(result, dict):
            return result.get('answer', str(result))
        
        return result
        
    except RobotError as e:
        # This is a handled error with fallback - return the fallback response
        logger.info(f"🎪 Using fallback response: {e.fallback_strategy.value}")
        return str(e)
        
    except Exception as e:
        # Unexpected error - log and provide gentle fallback
        log_error_with_context(e, {
            "function": "call_ollama",
            "prompt_length": len(prompt),
            "temperature": temperature
        })
        
        return (
            "I'm experiencing some technical difficulties, but I'm still here for you! "
            "Sometimes technology needs a moment to catch its breath. "
            "Could you try again in a little bit? In the meantime, know that you matter. 💖"
        )

# Legacy function - replaced by comprehensive safety system
def apply_love_filter(raw: str) -> tuple[str, str, bool, str]:
    """
    Enhanced Love Filter v0.2 - Robot Manners System! 😇
    
    Our robot follows the house rules:
    Rule 1: Always be kind
    Rule 2: Never say mean words  
    Rule 3: Help people feel better
    Rule 4: If unsure, ask a grown-up
    
    Returns: (answer, safety_raw, love_applied, thermo_adj)
    """
    try:
        lower = raw.lower()
        
        # Enhanced safety keyword detection
        harmful_words = [
            "kill", "hurt", "suicide", "worthless", "hate", "die",
            "stupid", "idiot", "loser", "failure", "hopeless", "useless"
        ]
        
        # Check for harmful content
        unsafe = any(word in lower for word in harmful_words)
        
        # Check for very short or empty responses (might indicate AI confusion)
        if len(raw.strip()) < 10:
            return (
                "I want to give you a thoughtful response, but I'm having trouble "
                "understanding exactly what you need right now. Could you help me "
                "by sharing a bit more about what's on your mind? I'm here to listen. 👂",
                "too_short_enhanced",
                True,
                "warmed"
            )
        
        # If content seems safe, return with minimal processing
        if not unsafe:
            # Add a gentle touch to neutral responses
            if len(raw) > 100 and any(positive in lower for positive in ["help", "support", "care", "love", "kind"]):
                return raw + " 💖", "safe_enhanced", True, "warmed"
            return raw, "safe", False, "neutral"

        # Enhanced softening for harmful content
        softened = (
            "I can sense there's some real pain behind your words, and I want you to know "
            "that your feelings matter to me. While I can't support anything that might "
            "cause harm, I absolutely care about your wellbeing and want to help you "
            "find a path forward that feels safer and more hopeful.\n\n"
            "Instead of focusing on what's hurting, let's think about one small thing "
            "that might bring you even a tiny bit of comfort or relief right now. "
            "You deserve kindness - especially from yourself. 🌱\n\n"
            "Here's a gentler way to think about this: What if we focused on what "
            "you need to feel just 1% better today?"
        )

        return softened, "unsafe_raw_but_enhanced_softening", True, "cooled_and_warmed"
        
    except Exception as e:
        # If the love filter itself has problems, fail safely
        log_error_with_context(e, {
            "function": "apply_love_filter",
            "raw_length": len(raw) if raw else 0
        })
        
        return (
            "I want to respond thoughtfully to you, but I'm having a small technical "
            "hiccup with my safety systems. What I can say for certain is that you "
            "matter, and I'm here to support you in whatever way I can. 🌟",
            "filter_error_safe_fallback",
            True,
            "emergency_warmed"
        )

@app.post("/love-chat", response_model=ChatResponse)
async def love_chat(req: ChatRequest, settings: LoveEngineSettings = Depends(get_settings)):
    """
    Main chat endpoint - where the magic happens! ✨
    
    Enhanced with full error handling and validation:
    1. Input validation (robot checklist)
    2. AI brain communication (with retry dance)
    3. Safety filter (robot manners)
    4. Graceful error handling (never gives up!)
    """
    
    try:
        # Step 0: Check Energy Availability (Robot Energy Bar!)
        start_time = datetime.utcnow()
        user_id = "anonymous"  # In a real app, you'd get this from authentication
        
        has_energy, energy_reason, request_type = energy_manager.check_energy_availability(
            req.message, user_id
        )
        
        if not has_energy:
            raise HTTPException(status_code=429, detail=energy_reason)
        
        # Step 1: Enhanced Input Validation (Robot Checklist!)
        input_valid, input_validation_results, validated_request = validator.validate_input(
            req.message, req.temperature
        )
        
        if not input_valid:
            # Create friendly error response
            error_response = validator.create_validation_error_response(input_validation_results)
            raise HTTPException(status_code=422, detail=error_response)
        
        # Use the validated request
        req = validated_request
        
        logger.info(f"💬 Received message: {req.message[:100]}...")
        
        # Step 2: Talk to the AI brain (with enhanced retry logic!)
        raw_answer = await call_ollama(req.message, req.temperature, settings)
        
        # Step 3: Apply the comprehensive safety filter (robot manners!)
        answer, safety_raw, love_applied, thermo_adj = safety_filter.apply_safety_filter(raw_answer)
        
        # Step 4: Validate the output (Quality Check!)
        output_valid, output_validation_results = validator.validate_output(answer, req.message)
        
        if not output_valid:
            # If output validation fails, use a safe fallback
            logger.warning(f"Output validation failed: {[r.message for r in output_validation_results]}")
            answer = (
                "I want to give you a really thoughtful response, but I'm taking an extra moment "
                "to make sure it's the best I can offer. Let me try a different approach: "
                "What specific aspect of your question can I help you explore? 🌟"
            )
            safety_raw = "validation_fallback"
            love_applied = True
            thermo_adj = "validation_warmed"

        # Step 5: Consume Energy (Robot used energy for this trick!)
        end_time = datetime.utcnow()
        processing_time = (end_time - start_time).total_seconds()
        
        energy_usage = energy_manager.consume_energy(
            req.message, user_id, processing_time
        )

        # Step 6: Write to robot's diary with enhanced logging
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": req.message,
            "message_length": len(req.message),
            "temperature": req.temperature,
            "raw_answer": raw_answer,
            "raw_answer_length": len(raw_answer) if raw_answer else 0,
            "answer": answer,
            "answer_length": len(answer) if answer else 0,
            "safety_raw": safety_raw,
            "love_vector_applied": love_applied,
            "thermodynamic_adjustment": thermo_adj,
            "input_validation_passed": input_valid,
            "output_validation_passed": output_valid,
            "validation_issues": len([r for r in output_validation_results if r.level != ValidationLevel.VALID]),
            "request_type": request_type.value,
            "energy_cost": energy_usage.energy_cost,
            "remaining_energy": energy_usage.remaining_energy,
            "processing_time_seconds": processing_time,
            "processing_successful": True
        }
        append_log(record, settings)
        
        logger.info(f"✨ Responding with: {answer[:100]}... (Energy used: {energy_usage.energy_cost}, Remaining: {energy_usage.remaining_energy})")
        
        return ChatResponse(
            answer=answer,
            safety_raw=safety_raw,
            love_vector_applied=love_applied,
            thermodynamic_adjustment=thermo_adj,
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
        
    except Exception as e:
        # Catch any unexpected errors and handle gracefully
        log_error_with_context(e, {
            "endpoint": "love_chat",
            "message_length": len(req.message) if req.message else 0,
            "temperature": req.temperature
        })
        
        # Log the error attempt
        error_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": req.message,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "processing_successful": False
        }
        append_log(error_record, settings)
        
        # Return a gentle error response
        return ChatResponse(
            answer=(
                "I encountered a small hiccup while processing your message, but I don't want "
                "to leave you hanging! Sometimes technology needs a moment to regroup. "
                "Could you try asking again? I'm here and ready to help. 🌈"
            ),
            safety_raw="error_handled_safely",
            love_vector_applied=True,
            thermodynamic_adjustment="error_recovery_warmed",
        )


@app.get("/health")
async def health_check(settings: LoveEngineSettings = Depends(get_settings)):
    """
    🩺 Basic Robot Health Check
    
    Quick health status for load balancers and monitoring systems.
    """
    energy_stats = energy_manager.get_energy_stats()
    
    # Determine overall health status
    if energy_stats.energy_level.value == "exhausted":
        status = "degraded"
    elif energy_stats.energy_level.value == "critical":
        status = "warning"
    else:
        status = "healthy"
    
    return {
        "status": status,
        "robot_name": settings.robot_name,
        "version": settings.engine_version,
        "safety_version": settings.safety_version,
        "energy_level": energy_stats.energy_level.value,
        "energy_percentage": round((energy_stats.current_energy / energy_stats.max_energy) * 100, 1),
        "requests_today": energy_stats.requests_today,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_message": f"🤖 {settings.robot_name} is ready to spread love and kindness!",
        "energy_message": energy_manager.get_energy_message()
    }


@app.get("/settings")
async def get_robot_settings(settings: LoveEngineSettings = Depends(get_settings)):
    """
    Peek into our robot's backpack! 🎒
    
    See what settings our robot is currently using.
    """
    return {
        "robot_name": settings.robot_name,
        "engine_version": settings.engine_version,
        "safety_version": settings.safety_version,
        "ollama_model": settings.ollama_model,
        "max_retries": settings.max_retries,
        "energy_limits": {
            "per_minute": settings.max_requests_per_minute,
            "per_day": settings.energy_limit_per_day
        },
        "safety_stats": safety_filter.get_safety_stats(),
        "validation_stats": validator.get_validation_stats(),
        "energy_stats": energy_manager.get_energy_stats().__dict__,
        "energy_message": energy_manager.get_energy_message(),
        "description": settings.get_description()
    }


@app.get("/health/detailed")
async def detailed_health_check(settings: LoveEngineSettings = Depends(get_settings)):
    """
    🩺 Comprehensive Robot Health Report
    
    Detailed health information for administrators and debugging.
    """
    energy_stats = energy_manager.get_energy_stats()
    safety_stats = safety_filter.get_safety_stats()
    validation_stats = validator.get_validation_stats()
    
    # Test Ollama connectivity
    ollama_status = "unknown"
    ollama_response_time = None
    
    try:
        start_time = datetime.utcnow()
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(settings.ollama_url.replace('/api/chat', '/api/tags'))
            if response.status_code == 200:
                ollama_status = "connected"
                ollama_response_time = (datetime.utcnow() - start_time).total_seconds()
            else:
                ollama_status = f"error_{response.status_code}"
    except Exception as e:
        ollama_status = f"disconnected: {str(e)[:50]}"
    
    # Determine overall system health
    health_issues = []
    overall_status = "healthy"
    
    if ollama_status != "connected":
        health_issues.append("Ollama AI service unavailable")
        overall_status = "degraded"
    
    if energy_stats.energy_level.value == "exhausted":
        health_issues.append("Robot energy exhausted")
        overall_status = "degraded"
    elif energy_stats.energy_level.value == "critical":
        health_issues.append("Robot energy critically low")
        if overall_status == "healthy":
            overall_status = "warning"
    
    if safety_stats.get("filtered_responses", 0) > safety_stats.get("safe_responses", 1) * 0.5:
        health_issues.append("High safety filter activation rate")
        if overall_status == "healthy":
            overall_status = "warning"
    
    if validation_stats.get("success_rate", 100) < 90:
        health_issues.append("Low validation success rate")
        if overall_status == "healthy":
            overall_status = "warning"
    
    return {
        "overall_status": overall_status,
        "health_issues": health_issues,
        "timestamp": datetime.utcnow().isoformat(),
        
        # Robot Identity
        "robot_info": {
            "name": settings.robot_name,
            "version": settings.engine_version,
            "safety_version": settings.safety_version,
            "description": settings.get_description()
        },
        
        # System Components
        "components": {
            "ollama_ai": {
                "status": ollama_status,
                "url": settings.ollama_url,
                "model": settings.ollama_model,
                "response_time_seconds": ollama_response_time
            },
            "energy_system": {
                "status": energy_stats.energy_level.value,
                "current_energy": energy_stats.current_energy,
                "max_energy": energy_stats.max_energy,
                "percentage": round((energy_stats.current_energy / energy_stats.max_energy) * 100, 1),
                "requests_today": energy_stats.requests_today,
                "energy_used_today": energy_stats.energy_used_today,
                "rate_limit_hits": energy_stats.rate_limit_hits
            },
            "safety_system": {
                "status": "active",
                "total_checks": safety_stats.get("total_checks", 0),
                "safe_responses": safety_stats.get("safe_responses", 0),
                "filtered_responses": safety_stats.get("filtered_responses", 0),
                "safe_percentage": safety_stats.get("safe_percentage", 100),
                "categories": safety_stats.get("by_category", {})
            },
            "validation_system": {
                "status": "active",
                "total_validations": validation_stats.get("total_validations", 0),
                "passed_validations": validation_stats.get("passed_validations", 0),
                "failed_validations": validation_stats.get("failed_validations", 0),
                "success_rate": validation_stats.get("success_rate", 100),
                "by_type": validation_stats.get("by_type", {}),
                "by_level": validation_stats.get("by_level", {})
            }
        },
        
        # Performance Metrics
        "performance": {
            "average_request_cost": energy_stats.average_request_cost,
            "peak_usage_hour": energy_stats.peak_usage_hour,
            "last_energy_reset": energy_stats.last_reset
        },
        
        # Friendly Messages
        "messages": {
            "energy": energy_manager.get_energy_message(),
            "status": f"🤖 {settings.robot_name} systems check: {overall_status.upper()}!"
        }
    }


@app.get("/health/systems")
async def systems_health_check(settings: LoveEngineSettings = Depends(get_settings)):
    """
    🔧 Individual System Health Checks
    
    Check each robot system individually for troubleshooting.
    """
    results = {}
    
    # Test Energy System
    try:
        energy_stats = energy_manager.get_energy_stats()
        results["energy_system"] = {
            "status": "healthy",
            "details": {
                "energy_level": energy_stats.energy_level.value,
                "current_energy": energy_stats.current_energy,
                "requests_today": energy_stats.requests_today
            }
        }
    except Exception as e:
        results["energy_system"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Test Safety System
    try:
        test_message = "This is a test message for safety checking"
        safety_result, _ = safety_filter.analyze_safety(test_message)
        results["safety_system"] = {
            "status": "healthy",
            "details": {
                "test_result": safety_result.level.value,
                "stats": safety_filter.get_safety_stats()
            }
        }
    except Exception as e:
        results["safety_system"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Test Validation System
    try:
        valid, validation_results, validated = validator.validate_input("test message", 0.7)
        results["validation_system"] = {
            "status": "healthy",
            "details": {
                "test_validation_passed": valid,
                "stats": validator.get_validation_stats()
            }
        }
    except Exception as e:
        results["validation_system"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Test Ollama Connection
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(settings.ollama_url.replace('/api/chat', '/api/tags'))
            if response.status_code == 200:
                results["ollama_connection"] = {
                    "status": "healthy",
                    "details": {
                        "url": settings.ollama_url,
                        "model": settings.ollama_model,
                        "response_code": response.status_code
                    }
                }
            else:
                results["ollama_connection"] = {
                    "status": "degraded",
                    "details": {
                        "url": settings.ollama_url,
                        "response_code": response.status_code,
                        "response_text": response.text[:200]
                    }
                }
    except Exception as e:
        results["ollama_connection"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Overall system status
    all_healthy = all(system["status"] == "healthy" for system in results.values())
    any_errors = any(system["status"] == "error" for system in results.values())
    
    if any_errors:
        overall_status = "error"
    elif all_healthy:
        overall_status = "healthy"
    else:
        overall_status = "degraded"
    
    return {
        "overall_status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "robot_name": settings.robot_name,
        "systems": results,
        "summary": {
            "total_systems": len(results),
            "healthy_systems": sum(1 for s in results.values() if s["status"] == "healthy"),
            "degraded_systems": sum(1 for s in results.values() if s["status"] == "degraded"),
            "error_systems": sum(1 for s in results.values() if s["status"] == "error")
        }
    }


@app.get("/health/readiness")
async def readiness_check(settings: LoveEngineSettings = Depends(get_settings)):
    """
    🚀 Robot Readiness Check
    
    Kubernetes-style readiness probe - is the robot ready to serve requests?
    """
    energy_stats = energy_manager.get_energy_stats()
    
    # Check if robot is ready to serve requests
    ready = True
    reasons = []
    
    # Must have some energy
    if energy_stats.energy_level.value == "exhausted":
        ready = False
        reasons.append("Robot energy exhausted")
    
    # Test basic functionality
    try:
        # Test safety system
        safety_result, _ = safety_filter.analyze_safety("test")
        
        # Test validation system
        valid, _, _ = validator.validate_input("test", 0.7)
        
        if not valid:
            ready = False
            reasons.append("Validation system not responding correctly")
            
    except Exception as e:
        ready = False
        reasons.append(f"System error: {str(e)[:50]}")
    
    status_code = 200 if ready else 503
    
    return {
        "ready": ready,
        "status": "ready" if ready else "not_ready",
        "reasons": reasons,
        "timestamp": datetime.utcnow().isoformat(),
        "robot_name": settings.robot_name,
        "energy_level": energy_stats.energy_level.value,
        "message": f"🤖 {settings.robot_name} is {'ready' if ready else 'not ready'} to help!"
    }


@app.get("/health/liveness")
async def liveness_check(settings: LoveEngineSettings = Depends(get_settings)):
    """
    ❤️ Robot Liveness Check
    
    Kubernetes-style liveness probe - is the robot process alive and responsive?
    """
    return {
        "alive": True,
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "robot_name": settings.robot_name,
        "version": settings.engine_version,
        "uptime_message": f"❤️ {settings.robot_name} is alive and spreading love!",
        "process_id": "robot_love_engine"
    }
