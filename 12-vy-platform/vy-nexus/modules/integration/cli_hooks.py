#!/usr/bin/env python3
"""
CLI Integration Hooks

Purpose: Integrate User Interaction Monitor with CLI interface.
Provides decorators and middleware for tracking CLI commands.

Author: VY-NEXUS Self-Evolving AI Ecosystem
Date: December 15, 2025
Version: 1.0.0
"""

import time
import functools
from typing import Callable, Any, Optional
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

def track_cli_command(command_name: Optional[str] = None):
    """
    Decorator to track CLI command execution.
    
    Usage:
        @track_cli_command("status")
        def handle_status_command():
            # command implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            monitor = get_monitor()
            cmd_name = command_name or func.__name__
            
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
                    interaction_type=InteractionType.CLI_COMMAND,
                    command=cmd_name,
                    status=status,
                    duration_ms=duration_ms,
                    error_message=error_msg,
                    metadata={
                        "args": str(args) if args else None,
                        "kwargs": str(kwargs) if kwargs else None
                    }
                )
        
        return wrapper
    return decorator

# -------------------------
# CLI Middleware
# -------------------------

class CLIMonitoringMiddleware:
    """
    Middleware for CLI command monitoring.
    Can be integrated into existing CLI frameworks.
    """
    
    def __init__(self):
        self.monitor = get_monitor()
    
    def before_command(self, command: str, args: list, kwargs: dict) -> dict:
        """
        Called before command execution.
        Returns context dict to pass to after_command.
        """
        return {
            "command": command,
            "start_time": time.time(),
            "args": args,
            "kwargs": kwargs
        }
    
    def after_command(
        self,
        context: dict,
        success: bool,
        error: Optional[Exception] = None
    ):
        """
        Called after command execution.
        """
        duration_ms = (time.time() - context["start_time"]) * 1000
        
        status = InteractionStatus.SUCCESS if success else InteractionStatus.ERROR
        error_msg = str(error) if error else None
        
        self.monitor.record_interaction(
            interaction_type=InteractionType.CLI_COMMAND,
            command=context["command"],
            status=status,
            duration_ms=duration_ms,
            error_message=error_msg,
            metadata={
                "args": str(context.get("args")),
                "kwargs": str(context.get("kwargs"))
            }
        )

# -------------------------
# Helper Functions
# -------------------------

def record_cli_interaction(
    command: str,
    success: bool,
    duration_ms: float,
    error: Optional[str] = None,
    metadata: Optional[dict] = None
):
    """
    Manually record a CLI interaction.
    Useful for integrating with existing CLI code.
    """
    monitor = get_monitor()
    status = InteractionStatus.SUCCESS if success else InteractionStatus.ERROR
    
    monitor.record_interaction(
        interaction_type=InteractionType.CLI_COMMAND,
        command=command,
        status=status,
        duration_ms=duration_ms,
        error_message=error,
        metadata=metadata or {}
    )

# -------------------------
# Example Usage
# -------------------------

if __name__ == "__main__":
    # Example 1: Using decorator
    @track_cli_command("test_command")
    def test_command():
        print("Executing test command...")
        time.sleep(0.1)
        return "Success"
    
    # Example 2: Using middleware
    middleware = CLIMonitoringMiddleware()
    
    # Simulate command execution
    context = middleware.before_command("status", [], {})
    time.sleep(0.05)
    middleware.after_command(context, success=True)
    
    # Example 3: Manual recording
    record_cli_interaction(
        command="manual_test",
        success=True,
        duration_ms=50.0,
        metadata={"test": True}
    )
    
    print("CLI hooks test complete!")
