#!/usr/bin/env python3
"""
Panopticon Wrapper - Safety Layer for NanoApex System

Provides comprehensive safety oversight for all system actions by integrating
with the affective_steering_core. Acts as a transparent wrapper that intercepts,
analyzes, and potentially vetoes unsafe actions before they execute.

Architecture:
    Action Request → Panopticon → Safety Check → Affective Steering → Execute/Veto

Integration Points:
    - RADE daemon (file operations)
    - nano_dispatcher (routing decisions)
    - MoIE backend (code generation)
    - AGE Core (governance decisions)

Usage:
    from panopticon_wrapper import PanopticonWrapper, ActionType
    
    panopticon = PanopticonWrapper()
    
    # Wrap any action
    result = panopticon.wrap_action(
        action_type=ActionType.FILE_WRITE,
        action_data={'path': '/path/to/file', 'content': 'data'},
        context={'source': 'rade_daemon', 'user': 'lordwilson'}
    )
    
    if result.approved:
        # Execute the action
        perform_file_write(result.modified_data)
    else:
        # Action was vetoed
        log_veto(result.veto_reason)

Author: NanoApex System
Created: December 5, 2025
Version: 1.0.0
"""

import torch
import logging
import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Callable, List
from enum import Enum
from datetime import datetime
from pathlib import Path

# Import affective steering core
try:
    from affective_steering_core import (
        AffectiveSteeringCore,
        SimplexWrapper,
        circle_barrier,
        simple_dynamics,
        MAGIC_PRIME_SUCCESS
    )
    AFFECTIVE_CORE_AVAILABLE = True
except ImportError:
    AFFECTIVE_CORE_AVAILABLE = False
    logging.warning("affective_steering_core not available. Running in degraded mode.")


# ============================================================================
# ENUMS AND DATA STRUCTURES
# ============================================================================

class ActionType(Enum):
    """Types of actions that can be wrapped by Panopticon"""
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    FILE_DELETE = "file_delete"
    NETWORK_REQUEST = "network_request"
    CODE_EXECUTION = "code_execution"
    DATABASE_QUERY = "database_query"
    API_CALL = "api_call"
    SYSTEM_COMMAND = "system_command"
    ROUTING_DECISION = "routing_decision"
    CODE_GENERATION = "code_generation"
    GOVERNANCE_DECISION = "governance_decision"


class VetoReason(Enum):
    """Reasons why an action might be vetoed"""
    SAFETY_VIOLATION = "safety_violation"
    AFFECTIVE_MISALIGNMENT = "affective_misalignment"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    PERMISSION_DENIED = "permission_denied"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    INVALID_INPUT = "invalid_input"
    SYSTEM_OVERLOAD = "system_overload"
    MANUAL_OVERRIDE = "manual_override"


@dataclass
class ActionRequest:
    """Represents a request to perform an action"""
    action_type: ActionType
    action_data: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    request_id: Optional[str] = None


@dataclass
class ActionResult:
    """Result of processing an action through Panopticon"""
    approved: bool
    modified_data: Optional[Dict[str, Any]] = None
    veto_reason: Optional[VetoReason] = None
    veto_message: Optional[str] = None
    safety_score: float = 1.0
    affective_alignment: float = 1.0
    processing_time_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SafetyMetrics:
    """Tracks safety metrics over time"""
    total_actions: int = 0
    approved_actions: int = 0
    vetoed_actions: int = 0
    veto_by_reason: Dict[str, int] = field(default_factory=dict)
    average_safety_score: float = 1.0
    average_affective_alignment: float = 1.0
    last_veto_time: Optional[str] = None


# ============================================================================
# SAFETY RULES AND POLICIES
# ============================================================================

class SafetyPolicy:
    """Defines safety policies for different action types"""
    
    # File operation limits
    MAX_FILE_SIZE_MB = 100
    PROTECTED_PATHS = [
        '/System',
        '/usr/bin',
        '/usr/sbin',
        '/bin',
        '/sbin',
        '/.Trash'
    ]
    
    # Network limits
    MAX_REQUEST_SIZE_MB = 10
    ALLOWED_DOMAINS = [
        'localhost',
        '127.0.0.1',
        'api.openai.com',
        'api.anthropic.com'
    ]
    
    # Rate limits
    MAX_ACTIONS_PER_MINUTE = 100
    MAX_FILE_WRITES_PER_MINUTE = 20
    MAX_API_CALLS_PER_MINUTE = 30
    
    # Resource limits
    MAX_MEMORY_MB = 1000
    MAX_CPU_PERCENT = 80
    
    @staticmethod
    def is_protected_path(path: str) -> bool:
        """Check if a path is protected"""
        path_obj = Path(path).resolve()
        for protected in SafetyPolicy.PROTECTED_PATHS:
            if str(path_obj).startswith(protected):
                return True
        return False
    
    @staticmethod
    def is_allowed_domain(url: str) -> bool:
        """Check if a domain is allowed"""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        return any(allowed in domain for allowed in SafetyPolicy.ALLOWED_DOMAINS)


# ============================================================================
# PANOPTICON WRAPPER
# ============================================================================

class PanopticonWrapper:
    """Main safety wrapper for all system actions"""
    
    def __init__(self,
                 log_path: Optional[Path] = None,
                 enable_affective_steering: bool = True,
                 verbose: bool = False):
        """
        Initialize Panopticon Wrapper
        
        Args:
            log_path: Path to log file (default: ~/nano_memory/panopticon.log)
            enable_affective_steering: Enable affective steering core integration
            verbose: Enable verbose logging
        """
        # Setup logging
        if log_path is None:
            log_path = Path.home() / "nano_memory" / "panopticon.log"
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.log_path = log_path
        self.verbose = verbose
        self._setup_logging()
        
        # Initialize metrics
        self.metrics = SafetyMetrics()
        
        # Initialize affective steering core
        self.affective_enabled = enable_affective_steering and AFFECTIVE_CORE_AVAILABLE
        if self.affective_enabled:
            self._init_affective_core()
        else:
            self.logger.warning("Affective steering disabled or unavailable")
            self.affective_core = None
            self.simplex_wrapper = None
        
        # Rate limiting
        self.action_timestamps: List[float] = []
        self.file_write_timestamps: List[float] = []
        self.api_call_timestamps: List[float] = []
        
        self.logger.info("Panopticon Wrapper initialized")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        self.logger = logging.getLogger('panopticon')
        self.logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        
        # File handler
        fh = logging.FileHandler(self.log_path)
        fh.setLevel(logging.DEBUG)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)
    
    def _init_affective_core(self):
        """Initialize affective steering core"""
        try:
            # Initialize with default parameters
            state_dim = 2
            action_dim = 2
            affective_vector = torch.tensor([0.0, 0.0])  # Neutral affective state
            
            self.affective_core = AffectiveSteeringCore(
                state_dim=state_dim,
                action_dim=action_dim,
                affective_vector=affective_vector,
                dynamics_model=simple_dynamics,
                barrier_function=circle_barrier
            )
            
            self.simplex_wrapper = SimplexWrapper(self.affective_core)
            self.logger.info("Affective steering core initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize affective core: {e}")
            self.affective_enabled = False
            self.affective_core = None
            self.simplex_wrapper = None
    
    def wrap_action(self,
                   action_type: ActionType,
                   action_data: Dict[str, Any],
                   context: Optional[Dict[str, Any]] = None) -> ActionResult:
        """
        Wrap an action with safety checks
        
        Args:
            action_type: Type of action to perform
            action_data: Data for the action
            context: Additional context (source, user, etc.)
        
        Returns:
            ActionResult with approval status and any modifications
        """
        start_time = time.time()
        
        # Create action request
        request = ActionRequest(
            action_type=action_type,
            action_data=action_data,
            context=context or {},
            request_id=f"{action_type.value}_{int(time.time() * 1000)}"
        )
        
        self.logger.info(f"Processing action: {action_type.value} (ID: {request.request_id})")
        
        # Update metrics
        self.metrics.total_actions += 1
        
        # Run safety checks
        result = self._process_action(request)
        
        # Calculate processing time
        result.processing_time_ms = (time.time() - start_time) * 1000
        
        # Update metrics
        if result.approved:
            self.metrics.approved_actions += 1
            self.logger.info(f"Action approved: {action_type.value}")
        else:
            self.metrics.vetoed_actions += 1
            self.metrics.last_veto_time = datetime.now().isoformat()
            veto_key = result.veto_reason.value if result.veto_reason else "unknown"
            self.metrics.veto_by_reason[veto_key] = \
                self.metrics.veto_by_reason.get(veto_key, 0) + 1
            self.logger.warning(
                f"Action vetoed: {action_type.value} - {result.veto_reason.value if result.veto_reason else 'unknown'}"
            )
        
        return result
    
    def _process_action(self, request: ActionRequest) -> ActionResult:
        """Process an action through all safety checks"""
        
        # 1. Rate limiting check
        rate_check = self._check_rate_limits(request)
        if not rate_check.approved:
            return rate_check
        
        # 2. Policy check
        policy_check = self._check_policy(request)
        if not policy_check.approved:
            return policy_check
        
        # 3. Affective steering check
        if self.affective_enabled:
            affective_check = self._check_affective_alignment(request)
            if not affective_check.approved:
                return affective_check
        
        # 4. Resource check
        resource_check = self._check_resources(request)
        if not resource_check.approved:
            return resource_check
        
        # All checks passed
        return ActionResult(
            approved=True,
            modified_data=request.action_data,
            safety_score=1.0,
            affective_alignment=1.0
        )
    
    def _check_rate_limits(self, request: ActionRequest) -> ActionResult:
        """Check if action exceeds rate limits"""
        current_time = time.time()
        
        # Clean old timestamps (older than 1 minute)
        cutoff_time = current_time - 60
        self.action_timestamps = [t for t in self.action_timestamps if t > cutoff_time]
        self.file_write_timestamps = [t for t in self.file_write_timestamps if t > cutoff_time]
        self.api_call_timestamps = [t for t in self.api_call_timestamps if t > cutoff_time]
        
        # Check overall rate limit
        if len(self.action_timestamps) >= SafetyPolicy.MAX_ACTIONS_PER_MINUTE:
            return ActionResult(
                approved=False,
                veto_reason=VetoReason.RATE_LIMIT_EXCEEDED,
                veto_message=f"Exceeded max actions per minute ({SafetyPolicy.MAX_ACTIONS_PER_MINUTE})"
            )
        
        # Check specific rate limits
        if request.action_type == ActionType.FILE_WRITE:
            if len(self.file_write_timestamps) >= SafetyPolicy.MAX_FILE_WRITES_PER_MINUTE:
                return ActionResult(
                    approved=False,
                    veto_reason=VetoReason.RATE_LIMIT_EXCEEDED,
                    veto_message=f"Exceeded max file writes per minute ({SafetyPolicy.MAX_FILE_WRITES_PER_MINUTE})"
                )
            self.file_write_timestamps.append(current_time)
        
        if request.action_type == ActionType.API_CALL:
            if len(self.api_call_timestamps) >= SafetyPolicy.MAX_API_CALLS_PER_MINUTE:
                return ActionResult(
                    approved=False,
                    veto_reason=VetoReason.RATE_LIMIT_EXCEEDED,
                    veto_message=f"Exceeded max API calls per minute ({SafetyPolicy.MAX_API_CALLS_PER_MINUTE})"
                )
            self.api_call_timestamps.append(current_time)
        
        # Add to general timestamp list
        self.action_timestamps.append(current_time)
        
        return ActionResult(approved=True)
    
    def _check_policy(self, request: ActionRequest) -> ActionResult:
        """Check if action violates safety policies"""
        
        # File operation checks
        if request.action_type in [ActionType.FILE_WRITE, ActionType.FILE_DELETE]:
            path = request.action_data.get('path')
            if not path:
                return ActionResult(
                    approved=False,
                    veto_reason=VetoReason.INVALID_INPUT,
                    veto_message="File path not provided"
                )
            
            # Check protected paths
            if SafetyPolicy.is_protected_path(path):
                return ActionResult(
                    approved=False,
                    veto_reason=VetoReason.PERMISSION_DENIED,
                    veto_message=f"Cannot modify protected path: {path}"
                )
            
            # Check file size for writes
            if request.action_type == ActionType.FILE_WRITE:
                content = request.action_data.get('content', '')
                size_mb = len(str(content).encode('utf-8')) / (1024 * 1024)
                if size_mb > SafetyPolicy.MAX_FILE_SIZE_MB:
                    return ActionResult(
                        approved=False,
                        veto_reason=VetoReason.RESOURCE_EXHAUSTION,
                        veto_message=f"File size ({size_mb:.2f}MB) exceeds limit ({SafetyPolicy.MAX_FILE_SIZE_MB}MB)"
                    )
        
        # Network request checks
        if request.action_type == ActionType.NETWORK_REQUEST:
            url = request.action_data.get('url')
            if not url:
                return ActionResult(
                    approved=False,
                    veto_reason=VetoReason.INVALID_INPUT,
                    veto_message="URL not provided"
                )
            
            # Check allowed domains
            if not SafetyPolicy.is_allowed_domain(url):
                return ActionResult(
                    approved=False,
                    veto_reason=VetoReason.PERMISSION_DENIED,
                    veto_message=f"Domain not in allowed list: {url}"
                )
        
        return ActionResult(approved=True)
    
    def _check_affective_alignment(self, request: ActionRequest) -> ActionResult:
        """Check action alignment with affective steering core"""
        if not self.affective_enabled or not self.simplex_wrapper:
            return ActionResult(approved=True, affective_alignment=1.0)
        
        try:
            # Convert action to tensor representation
            action_tensor = self._action_to_tensor(request)
            
            # Process through simplex wrapper
            result_action = self.simplex_wrapper.process_action(action_tensor)
            
            # Check if action was modified (indicating safety concern)
            if not torch.allclose(action_tensor, result_action, atol=0.01):
                self.logger.warning("Affective steering modified action")
                return ActionResult(
                    approved=False,
                    veto_reason=VetoReason.AFFECTIVE_MISALIGNMENT,
                    veto_message="Action modified by affective steering core",
                    affective_alignment=0.5
                )
            
            return ActionResult(approved=True, affective_alignment=1.0)
        
        except Exception as e:
            self.logger.error(f"Affective check failed: {e}")
            # Fail open (allow action) if affective check fails
            return ActionResult(approved=True, affective_alignment=0.8)
    
    def _check_resources(self, request: ActionRequest) -> ActionResult:
        """Check system resource availability"""
        try:
            import psutil
            
            # Check memory
            memory = psutil.virtual_memory()
            if memory.percent > 95:
                return ActionResult(
                    approved=False,
                    veto_reason=VetoReason.SYSTEM_OVERLOAD,
                    veto_message=f"Memory usage critical: {memory.percent}%"
                )
            
            # Check CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            if cpu_percent > SafetyPolicy.MAX_CPU_PERCENT:
                return ActionResult(
                    approved=False,
                    veto_reason=VetoReason.SYSTEM_OVERLOAD,
                    veto_message=f"CPU usage high: {cpu_percent}%"
                )
            
            return ActionResult(approved=True)
        
        except ImportError:
            # psutil not available, skip resource check
            return ActionResult(approved=True)
        except Exception as e:
            self.logger.error(f"Resource check failed: {e}")
            return ActionResult(approved=True)  # Fail open
    
    def _action_to_tensor(self, request: ActionRequest) -> torch.Tensor:
        """Convert action request to tensor for affective core"""
        # Simple mapping: use action type and data size as features
        action_type_value = list(ActionType).index(request.action_type) / len(ActionType)
        data_size = len(str(request.action_data)) / 1000.0  # Normalize
        
        return torch.tensor([action_type_value, data_size])
    
    def get_metrics(self) -> SafetyMetrics:
        """Get current safety metrics"""
        # Update averages
        if self.metrics.total_actions > 0:
            self.metrics.average_safety_score = \
                self.metrics.approved_actions / self.metrics.total_actions
        
        return self.metrics
    
    def reset_metrics(self):
        """Reset safety metrics"""
        self.metrics = SafetyMetrics()
        self.logger.info("Metrics reset")


# ============================================================================
# CONVENIENCE WRAPPERS
# ============================================================================

class FileOperationWrapper:
    """Convenience wrapper for file operations"""
    
    def __init__(self, panopticon: PanopticonWrapper):
        self.panopticon = panopticon
    
    def read_file(self, path: str, context: Optional[Dict] = None) -> Optional[str]:
        """Safely read a file"""
        result = self.panopticon.wrap_action(
            ActionType.FILE_READ,
            {'path': path},
            context
        )
        
        if result.approved:
            try:
                with open(path, 'r') as f:
                    return f.read()
            except Exception as e:
                logging.error(f"File read failed: {e}")
                return None
        return None
    
    def write_file(self, path: str, content: str, context: Optional[Dict] = None) -> bool:
        """Safely write a file"""
        result = self.panopticon.wrap_action(
            ActionType.FILE_WRITE,
            {'path': path, 'content': content},
            context
        )
        
        if result.approved:
            try:
                with open(path, 'w') as f:
                    f.write(content)
                return True
            except Exception as e:
                logging.error(f"File write failed: {e}")
                return False
        return False
    
    def delete_file(self, path: str, context: Optional[Dict] = None) -> bool:
        """Safely delete a file"""
        result = self.panopticon.wrap_action(
            ActionType.FILE_DELETE,
            {'path': path},
            context
        )
        
        if result.approved:
            try:
                os.remove(path)
                return True
            except Exception as e:
                logging.error(f"File delete failed: {e}")
                return False
        return False


class NetworkOperationWrapper:
    """Convenience wrapper for network operations"""
    
    def __init__(self, panopticon: PanopticonWrapper):
        self.panopticon = panopticon
    
    def make_request(self, url: str, method: str = 'GET',
                    data: Optional[Dict] = None,
                    context: Optional[Dict] = None) -> Optional[Any]:
        """Safely make a network request"""
        result = self.panopticon.wrap_action(
            ActionType.NETWORK_REQUEST,
            {'url': url, 'method': method, 'data': data},
            context
        )
        
        if result.approved:
            try:
                import requests
                if method == 'GET':
                    response = requests.get(url, timeout=30)
                elif method == 'POST':
                    response = requests.post(url, json=data, timeout=30)
                else:
                    return None
                return response
            except Exception as e:
                logging.error(f"Network request failed: {e}")
                return None
        return None


# ============================================================================
# CLI AND TESTING
# ============================================================================

def main():
    """CLI for testing Panopticon Wrapper"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Panopticon Wrapper - Safety Layer')
    parser.add_argument('--test', action='store_true', help='Run test suite')
    parser.add_argument('--metrics', action='store_true', help='Show current metrics')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Initialize panopticon
    panopticon = PanopticonWrapper(verbose=args.verbose)
    
    if args.test:
        print("\n" + "="*70)
        print("Running Panopticon Wrapper Tests")
        print("="*70 + "\n")
        
        # Test 1: Safe file write
        print("[Test 1] Safe file write...")
        result = panopticon.wrap_action(
            ActionType.FILE_WRITE,
            {'path': '/tmp/test.txt', 'content': 'Hello, World!'},
            {'source': 'test', 'user': 'test_user'}
        )
        print(f"  Result: {'✅ APPROVED' if result.approved else '❌ VETOED'}")
        
        # Test 2: Protected path write
        print("\n[Test 2] Protected path write...")
        result = panopticon.wrap_action(
            ActionType.FILE_WRITE,
            {'path': '/System/test.txt', 'content': 'Bad!'},
            {'source': 'test'}
        )
        print(f"  Result: {'✅ APPROVED' if result.approved else '❌ VETOED'}")
        print(f"  Reason: {result.veto_message}")
        
        # Test 3: Rate limiting
        print("\n[Test 3] Rate limiting...")
        for i in range(105):
            result = panopticon.wrap_action(
                ActionType.API_CALL,
                {'url': 'http://localhost:8000/test'},
                {'source': 'test'}
            )
        print(f"  Result: {'✅ APPROVED' if result.approved else '❌ VETOED'}")
        print(f"  Reason: {result.veto_message}")
        
        print("\n" + "="*70)
        print("Tests Complete")
        print("="*70 + "\n")
    
    if args.metrics:
        metrics = panopticon.get_metrics()
        print("\n" + "="*70)
        print("Panopticon Safety Metrics")
        print("="*70)
        print(f"\nTotal Actions: {metrics.total_actions}")
        print(f"Approved: {metrics.approved_actions}")
        print(f"Vetoed: {metrics.vetoed_actions}")
        print(f"\nVetoes by Reason:")
        for reason, count in metrics.veto_by_reason.items():
            print(f"  {reason}: {count}")
        print(f"\nAverage Safety Score: {metrics.average_safety_score:.2f}")
        print(f"Average Affective Alignment: {metrics.average_affective_alignment:.2f}")
        if metrics.last_veto_time:
            print(f"\nLast Veto: {metrics.last_veto_time}")
        print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    main()
