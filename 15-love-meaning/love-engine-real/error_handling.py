# 🤖 Robot Error Handling - The "Try Again" Dance System
"""
This module implements the "Try Again" dance for our robot friend!

When our robot falls down, it doesn't just cry and give up. Instead, it:
1. Counts to 3 and tries again
2. If still falls → tries a different way  
3. If REALLY can't do it → does a simpler trick instead
4. Never just cries and quits!
"""

import asyncio
import logging
from typing import Any, Callable, Optional, Union, Dict, List
from functools import wraps
from datetime import datetime, timedelta
try:
    import httpx
except ImportError:
    httpx = None
from enum import Enum

logger = logging.getLogger(__name__)

class FallbackStrategy(Enum):
    """Different ways our robot can handle problems"""
    SIMPLE_RESPONSE = "simple_response"
    CACHED_RESPONSE = "cached_response"
    OFFLINE_MODE = "offline_mode"
    GRACEFUL_DEGRADATION = "graceful_degradation"

class RobotError(Exception):
    """Base exception for when our robot has problems"""
    def __init__(self, message: str, fallback_strategy: FallbackStrategy = FallbackStrategy.SIMPLE_RESPONSE):
        super().__init__(message)
        self.fallback_strategy = fallback_strategy
        self.timestamp = datetime.utcnow()

class OllamaConnectionError(RobotError):
    """When our robot can't talk to its AI brain"""
    def __init__(self, message: str):
        super().__init__(message, FallbackStrategy.OFFLINE_MODE)

class SafetyFilterError(RobotError):
    """When our robot's safety system has problems"""
    def __init__(self, message: str):
        super().__init__(message, FallbackStrategy.GRACEFUL_DEGRADATION)

class RateLimitError(RobotError):
    """When our robot is too tired and needs to rest"""
    def __init__(self, message: str):
        super().__init__(message, FallbackStrategy.SIMPLE_RESPONSE)

def retry_with_fallback(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff_multiplier: float = 2.0,
    fallback_strategies: Optional[List[FallbackStrategy]] = None
):
    """
    🎭 The "Try Again" Dance Decorator!
    
    This decorator teaches any function to do the try-again dance:
    1. Try the function
    2. If it fails, wait a bit and try again
    3. If it keeps failing, try different strategies
    4. Never give up completely!
    
    Args:
        max_retries: How many times to try again
        delay: How long to wait between tries (in seconds)
        backoff_multiplier: How much longer to wait each time
        fallback_strategies: What to do if everything fails
    """
    if fallback_strategies is None:
        fallback_strategies = [FallbackStrategy.SIMPLE_RESPONSE]
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_error = None
            current_delay = delay
            
            # Try the main function multiple times
            for attempt in range(max_retries + 1):
                try:
                    logger.info(f"🤖 Attempt {attempt + 1}/{max_retries + 1}: Trying {func.__name__}...")
                    result = await func(*args, **kwargs)
                    
                    if attempt > 0:
                        logger.info(f"🎉 Success after {attempt + 1} attempts!")
                    
                    return result
                    
                except Exception as e:
                    last_error = e
                    logger.warning(f"💔 Attempt {attempt + 1} failed: {str(e)}")
                    
                    if attempt < max_retries:
                        logger.info(f"🕺 Doing the Try-Again dance... waiting {current_delay}s")
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff_multiplier
                    else:
                        logger.error(f"😢 All {max_retries + 1} attempts failed!")
            
            # If we get here, all retries failed - time for fallback strategies!
            logger.info("🎪 Time for Plan B! Trying fallback strategies...")
            
            for strategy in fallback_strategies:
                try:
                    fallback_result = await _execute_fallback_strategy(
                        strategy, func.__name__, last_error, *args, **kwargs
                    )
                    logger.info(f"✨ Fallback strategy '{strategy.value}' worked!")
                    return fallback_result
                    
                except Exception as fallback_error:
                    logger.warning(f"🤷 Fallback strategy '{strategy.value}' also failed: {fallback_error}")
                    continue
            
            # If even fallbacks fail, return a gentle error message
            logger.error("😔 Even our backup plans didn't work. Being honest with the user.")
            raise RobotError(
                f"I tried my best, but I'm having trouble with {func.__name__} right now. "
                f"This might be temporary - please try again in a moment. "
                f"Original error: {str(last_error)}"
            )
        
        return wrapper
    return decorator

async def _execute_fallback_strategy(
    strategy: FallbackStrategy,
    function_name: str,
    original_error: Exception,
    *args,
    **kwargs
) -> Any:
    """
    🎪 Execute a specific fallback strategy when the main function fails
    """
    
    if strategy == FallbackStrategy.SIMPLE_RESPONSE:
        return _get_simple_response(function_name, original_error)
    
    elif strategy == FallbackStrategy.CACHED_RESPONSE:
        return await _get_cached_response(function_name, *args, **kwargs)
    
    elif strategy == FallbackStrategy.OFFLINE_MODE:
        return _get_offline_response(function_name, original_error)
    
    elif strategy == FallbackStrategy.GRACEFUL_DEGRADATION:
        return _get_degraded_response(function_name, original_error)
    
    else:
        raise ValueError(f"Unknown fallback strategy: {strategy}")

def _get_simple_response(function_name: str, error: Exception) -> Dict[str, Any]:
    """
    🤗 Simple, honest response when things don't work
    """
    return {
        "answer": (
            "I'm having some technical difficulties right now, but I'm still here to help! "
            "Sometimes technology needs a little break. Could you try asking again in a moment? "
            "In the meantime, remember that you're valued and I care about helping you. 💖"
        ),
        "safety_raw": "fallback_safe",
        "love_vector_applied": True,
        "thermodynamic_adjustment": "warmed",
        "fallback_used": "simple_response",
        "original_error": str(error)
    }

async def _get_cached_response(function_name: str, *args, **kwargs) -> Dict[str, Any]:
    """
    📚 Try to find a similar previous response (future enhancement)
    """
    # For now, return a helpful cached-style response
    # In the future, this could check a database of previous responses
    return {
        "answer": (
            "I'm drawing from my memory of similar conversations to help you. "
            "While I can't access my full capabilities right now, I can still offer support. "
            "What specific aspect of your question can I help clarify? 🤔"
        ),
        "safety_raw": "cached_safe",
        "love_vector_applied": True,
        "thermodynamic_adjustment": "neutral",
        "fallback_used": "cached_response"
    }

def _get_offline_response(function_name: str, error: Exception) -> Dict[str, Any]:
    """
    📱 Offline mode - work without external services
    """
    return {
        "answer": (
            "I'm currently in offline mode, which means I can't access my full AI capabilities. "
            "However, I can still help with basic questions and provide emotional support. "
            "My core mission is to spread love and kindness, and that doesn't require any fancy technology! "
            "What's on your mind? 💝"
        ),
        "safety_raw": "offline_safe",
        "love_vector_applied": True,
        "thermodynamic_adjustment": "warmed",
        "fallback_used": "offline_mode",
        "technical_note": "Ollama service unavailable"
    }

def _get_degraded_response(function_name: str, error: Exception) -> Dict[str, Any]:
    """
    🔧 Graceful degradation - simpler version of the service
    """
    return {
        "answer": (
            "I'm running in simplified mode right now. While some of my advanced features "
            "aren't available, my core purpose remains the same: to be helpful, kind, and supportive. "
            "I might not have all the answers, but I'm here to listen and care. "
            "How can I support you today? 🌟"
        ),
        "safety_raw": "degraded_safe",
        "love_vector_applied": True,
        "thermodynamic_adjustment": "stable",
        "fallback_used": "graceful_degradation"
    }

class CircuitBreaker:
    """
    🔌 Circuit Breaker Pattern - Protects our robot from overload
    
    Like a fuse in your house, this stops trying to do something that's
    clearly broken, giving it time to heal before trying again.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        🔌 Call a function through the circuit breaker
        """
        if self.state == "OPEN":
            if self._should_attempt_reset():
                self.state = "HALF_OPEN"
                logger.info("🔄 Circuit breaker: Attempting reset...")
            else:
                raise RobotError(
                    f"Circuit breaker is OPEN. Service unavailable for {self.recovery_timeout}s after repeated failures.",
                    FallbackStrategy.OFFLINE_MODE
                )
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
            
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try again"""
        if self.last_failure_time is None:
            return True
        
        time_since_failure = datetime.utcnow() - self.last_failure_time
        return time_since_failure.total_seconds() >= self.recovery_timeout
    
    def _on_success(self):
        """Reset the circuit breaker on success"""
        self.failure_count = 0
        self.state = "CLOSED"
        logger.info("✅ Circuit breaker: Reset to CLOSED state")
    
    def _on_failure(self):
        """Handle failure - maybe open the circuit"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"🚨 Circuit breaker: OPENED after {self.failure_count} failures")

# Global circuit breaker for Ollama connections
# Global circuit breaker for Ollama connections
if httpx:
    ollama_circuit_breaker = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=30,
        expected_exception=httpx.RequestError
    )
else:
    ollama_circuit_breaker = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=30,
        expected_exception=Exception
    )

def log_error_with_context(error: Exception, context: Dict[str, Any]) -> None:
    """
    📝 Log errors with helpful context for debugging
    """
    error_info = {
        "timestamp": datetime.utcnow().isoformat(),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "robot_status": "learning_from_failure"
    }
    
    logger.error(f"🤖 Robot Error Log: {error_info}")
    
    # In a real system, this could also:
    # - Send alerts to monitoring systems
    # - Update health metrics
    # - Trigger automatic recovery procedures