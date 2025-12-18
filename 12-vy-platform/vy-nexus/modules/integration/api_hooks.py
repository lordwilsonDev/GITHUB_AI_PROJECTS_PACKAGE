#!/usr/bin/env python3
"""
API Integration Hooks

Purpose: Integrate User Interaction Monitor with API Gateway.
Provides middleware for tracking API requests.

Author: VY-NEXUS Self-Evolving AI Ecosystem
Date: December 15, 2025
Version: 1.0.0
"""

import time
import functools
from typing import Callable, Any, Optional, Dict
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from learning.user_interaction_monitor import (
    get_monitor,
    InteractionType,
    InteractionStatus
)

# -------------------------
# Decorators
# -------------------------

def track_api_endpoint(endpoint: Optional[str] = None):
    """
    Decorator to track API endpoint calls.
    
    Usage:
        @track_api_endpoint("/api/tasks")
        def handle_tasks():
            # endpoint implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            monitor = get_monitor()
            endpoint_name = endpoint or func.__name__
            
            start_time = time.time()
            error_msg = None
            status = InteractionStatus.SUCCESS
            
            try:
                result = func(*args, **kwargs)
                return result
            
            except Exception as e:
                error_msg = str(e)
                status = InteractionStatus.ERROR
                raise
            
            finally:
                duration_ms = (time.time() - start_time) * 1000
                
                # Record interaction
                monitor.record_interaction(
                    interaction_type=InteractionType.API_REQUEST,
                    command=endpoint_name,
                    status=status,
                    duration_ms=duration_ms,
                    error_message=error_msg,
                    metadata={
                        "method": kwargs.get("method", "GET"),
                        "status_code": kwargs.get("status_code")
                    }
                )
        
        return wrapper
    return decorator

# -------------------------
# API Middleware
# -------------------------

class APIMonitoringMiddleware:
    """
    Middleware for API request monitoring.
    Compatible with Flask, FastAPI, and other frameworks.
    """
    
    def __init__(self):
        self.monitor = get_monitor()
    
    def before_request(self, request: Any) -> dict:
        """
        Called before request processing.
        Returns context dict to pass to after_request.
        
        Args:
            request: Framework-specific request object
        """
        return {
            "path": getattr(request, 'path', 'unknown'),
            "method": getattr(request, 'method', 'GET'),
            "start_time": time.time()
        }
    
    def after_request(
        self,
        context: dict,
        response: Any,
        error: Optional[Exception] = None
    ):
        """
        Called after request processing.
        
        Args:
            context: Context from before_request
            response: Framework-specific response object
            error: Exception if request failed
        """
        duration_ms = (time.time() - context["start_time"]) * 1000
        
        # Determine status
        if error:
            status = InteractionStatus.ERROR
            error_msg = str(error)
        else:
            status_code = getattr(response, 'status_code', 200)
            if 200 <= status_code < 300:
                status = InteractionStatus.SUCCESS
            elif 400 <= status_code < 500:
                status = InteractionStatus.FAILURE
            else:
                status = InteractionStatus.ERROR
            error_msg = None
        
        # Record interaction
        self.monitor.record_interaction(
            interaction_type=InteractionType.API_REQUEST,
            command=f"{context['method']} {context['path']}",
            status=status,
            duration_ms=duration_ms,
            error_message=error_msg,
            metadata={
                "method": context["method"],
                "path": context["path"],
                "status_code": getattr(response, 'status_code', None)
            }
        )

# -------------------------
# Flask Integration
# -------------------------

def create_flask_middleware(app):
    """
    Create Flask middleware for monitoring.
    
    Usage:
        from flask import Flask
        app = Flask(__name__)
        create_flask_middleware(app)
    """
    middleware = APIMonitoringMiddleware()
    
    @app.before_request
    def before_request():
        from flask import request, g
        g.monitoring_context = middleware.before_request(request)
    
    @app.after_request
    def after_request(response):
        from flask import g
        if hasattr(g, 'monitoring_context'):
            middleware.after_request(g.monitoring_context, response)
        return response
    
    @app.errorhandler(Exception)
    def handle_error(error):
        from flask import g
        if hasattr(g, 'monitoring_context'):
            middleware.after_request(g.monitoring_context, None, error)
        raise

# -------------------------
# FastAPI Integration
# -------------------------

def create_fastapi_middleware(app):
    """
    Create FastAPI middleware for monitoring.
    
    Usage:
        from fastapi import FastAPI
        app = FastAPI()
        create_fastapi_middleware(app)
    """
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.requests import Request
    
    class MonitoringMiddleware(BaseHTTPMiddleware):
        def __init__(self, app):
            super().__init__(app)
            self.monitor_middleware = APIMonitoringMiddleware()
        
        async def dispatch(self, request: Request, call_next):
            context = self.monitor_middleware.before_request(request)
            
            try:
                response = await call_next(request)
                self.monitor_middleware.after_request(context, response)
                return response
            
            except Exception as e:
                self.monitor_middleware.after_request(context, None, e)
                raise
    
    app.add_middleware(MonitoringMiddleware)

# -------------------------
# Helper Functions
# -------------------------

def record_api_interaction(
    endpoint: str,
    method: str,
    status_code: int,
    duration_ms: float,
    error: Optional[str] = None,
    metadata: Optional[dict] = None
):
    """
    Manually record an API interaction.
    Useful for integrating with existing API code.
    """
    monitor = get_monitor()
    
    # Determine status from status code
    if error:
        status = InteractionStatus.ERROR
    elif 200 <= status_code < 300:
        status = InteractionStatus.SUCCESS
    elif 400 <= status_code < 500:
        status = InteractionStatus.FAILURE
    else:
        status = InteractionStatus.ERROR
    
    monitor.record_interaction(
        interaction_type=InteractionType.API_REQUEST,
        command=f"{method} {endpoint}",
        status=status,
        duration_ms=duration_ms,
        error_message=error,
        metadata=metadata or {"method": method, "status_code": status_code}
    )

# -------------------------
# Example Usage
# -------------------------

if __name__ == "__main__":
    # Example: Manual recording
    record_api_interaction(
        endpoint="/api/test",
        method="GET",
        status_code=200,
        duration_ms=45.5,
        metadata={"test": True}
    )
    
    print("API hooks test complete!")
