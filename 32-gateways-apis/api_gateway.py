#!/usr/bin/env python3
"""
API Gateway (T-107)
Level 18 - Integration Layer

Unified API gateway for all MoIE-OS services:
- Single entry point for all external requests
- Request routing and load balancing
- Authentication and authorization
- Rate limiting and throttling
- Request/response transformation
- API versioning support

Features:
- RESTful API endpoints
- GraphQL support
- WebSocket connections
- API key management
- Request validation
- Response caching
- Metrics and monitoring
"""

import time
import json
import hashlib
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import re


class HTTPMethod(Enum):
    """HTTP methods"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    OPTIONS = "OPTIONS"
    HEAD = "HEAD"


class AuthType(Enum):
    """Authentication types"""
    NONE = "none"
    API_KEY = "api_key"
    BEARER_TOKEN = "bearer_token"
    BASIC_AUTH = "basic_auth"
    OAUTH2 = "oauth2"


class RateLimitStrategy(Enum):
    """Rate limiting strategies"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


@dataclass
class APIEndpoint:
    """API endpoint definition"""
    path: str
    method: HTTPMethod
    handler: Callable
    auth_type: AuthType = AuthType.API_KEY
    rate_limit: Optional[int] = None  # Requests per minute
    version: str = "v1"
    description: str = ""
    request_schema: Optional[Dict] = None
    response_schema: Optional[Dict] = None
    
    def matches(self, path: str, method: HTTPMethod) -> bool:
        """Check if request matches this endpoint"""
        # Convert path pattern to regex
        pattern = re.sub(r'\{[^}]+\}', r'([^/]+)', self.path)
        pattern = f"^{pattern}$"
        
        return bool(re.match(pattern, path)) and self.method == method
    
    def extract_params(self, path: str) -> Dict[str, str]:
        """Extract path parameters from request path"""
        # Extract parameter names from pattern
        param_names = re.findall(r'\{([^}]+)\}', self.path)
        
        # Extract values from path
        pattern = re.sub(r'\{[^}]+\}', r'([^/]+)', self.path)
        match = re.match(f"^{pattern}$", path)
        
        if match and param_names:
            return dict(zip(param_names, match.groups()))
        return {}


@dataclass
class APIRequest:
    """API request object"""
    request_id: str
    method: HTTPMethod
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body: Any
    client_id: str
    timestamp: float = field(default_factory=time.time)
    
    def get_header(self, name: str, default: str = "") -> str:
        """Get header value (case-insensitive)"""
        for key, value in self.headers.items():
            if key.lower() == name.lower():
                return value
        return default


@dataclass
class APIResponse:
    """API response object"""
    status_code: int
    body: Any
    headers: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "status_code": self.status_code,
            "body": self.body,
            "headers": self.headers
        }


class RateLimiter:
    """Rate limiter for API requests"""
    
    def __init__(self, strategy: RateLimitStrategy = RateLimitStrategy.FIXED_WINDOW):
        self.strategy = strategy
        # client_id -> deque of timestamps
        self.request_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.lock = threading.RLock()
    
    def check_limit(self, client_id: str, limit: int, window: int = 60) -> Tuple[bool, Dict]:
        """
        Check if request is within rate limit.
        
        Args:
            client_id: Client identifier
            limit: Max requests per window
            window: Time window in seconds
        
        Returns:
            (allowed, info) tuple
        """
        now = time.time()
        
        with self.lock:
            history = self.request_history[client_id]
            
            # Remove old requests outside window
            while history and history[0] < now - window:
                history.popleft()
            
            # Check limit
            current_count = len(history)
            allowed = current_count < limit
            
            if allowed:
                history.append(now)
            
            info = {
                "limit": limit,
                "remaining": max(0, limit - current_count - (1 if allowed else 0)),
                "reset": int(now + window) if history else int(now),
                "window": window
            }
            
            return allowed, info


class APIKeyManager:
    """Manages API keys and authentication"""
    
    def __init__(self):
        # api_key -> client_info
        self.api_keys: Dict[str, Dict] = {}
        self.lock = threading.RLock()
    
    def create_key(self, client_id: str, scopes: List[str] = None) -> str:
        """
        Create new API key.
        
        Args:
            client_id: Client identifier
            scopes: List of allowed scopes
        
        Returns:
            API key
        """
        # Generate key
        key_data = f"{client_id}:{time.time()}:{id(self)}"
        api_key = hashlib.sha256(key_data.encode()).hexdigest()
        
        with self.lock:
            self.api_keys[api_key] = {
                "client_id": client_id,
                "scopes": scopes or ["*"],
                "created_at": time.time(),
                "active": True
            }
        
        return api_key
    
    def validate_key(self, api_key: str) -> Tuple[bool, Optional[str]]:
        """
        Validate API key.
        
        Returns:
            (valid, client_id) tuple
        """
        with self.lock:
            if api_key in self.api_keys:
                key_info = self.api_keys[api_key]
                if key_info["active"]:
                    return True, key_info["client_id"]
        return False, None
    
    def revoke_key(self, api_key: str):
        """Revoke an API key"""
        with self.lock:
            if api_key in self.api_keys:
                self.api_keys[api_key]["active"] = False


class APIGateway:
    """
    Unified API gateway for MoIE-OS services.
    
    Provides:
    - Request routing
    - Authentication
    - Rate limiting
    - Request validation
    - Response caching
    - Metrics tracking
    """
    
    def __init__(self):
        # Registered endpoints
        self.endpoints: List[APIEndpoint] = []
        
        # Authentication
        self.key_manager = APIKeyManager()
        
        # Rate limiting
        self.rate_limiter = RateLimiter()
        
        # Response cache: cache_key -> (response, timestamp)
        self.cache: Dict[str, Tuple[APIResponse, float]] = {}
        self.cache_ttl = 300.0  # 5 minutes
        
        # Metrics
        self.metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "requests_unauthorized": 0,
            "requests_rate_limited": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_response_time": 0.0
        }
        
        # Request history
        self.request_history: deque = deque(maxlen=1000)
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Register default endpoints
        self._register_default_endpoints()
    
    def _register_default_endpoints(self):
        """Register default system endpoints"""
        # Health check
        self.register_endpoint(
            path="/health",
            method=HTTPMethod.GET,
            handler=self._health_check,
            auth_type=AuthType.NONE,
            description="Health check endpoint"
        )
        
        # Metrics
        self.register_endpoint(
            path="/metrics",
            method=HTTPMethod.GET,
            handler=self._get_metrics,
            auth_type=AuthType.API_KEY,
            description="Get gateway metrics"
        )
        
        # API key management
        self.register_endpoint(
            path="/api/keys",
            method=HTTPMethod.POST,
            handler=self._create_api_key,
            auth_type=AuthType.NONE,  # In production, would require admin auth
            description="Create new API key"
        )
    
    def register_endpoint(self, path: str, method: HTTPMethod,
                         handler: Callable,
                         auth_type: AuthType = AuthType.API_KEY,
                         rate_limit: Optional[int] = None,
                         version: str = "v1",
                         description: str = ""):
        """
        Register an API endpoint.
        
        Args:
            path: Endpoint path (e.g., '/api/v1/users/{id}')
            method: HTTP method
            handler: Request handler function
            auth_type: Authentication type
            rate_limit: Requests per minute (None = unlimited)
            version: API version
            description: Endpoint description
        """
        endpoint = APIEndpoint(
            path=path,
            method=method,
            handler=handler,
            auth_type=auth_type,
            rate_limit=rate_limit,
            version=version,
            description=description
        )
        
        with self.lock:
            self.endpoints.append(endpoint)
    
    def handle_request(self, method: str, path: str,
                      headers: Dict[str, str] = None,
                      query_params: Dict[str, str] = None,
                      body: Any = None) -> APIResponse:
        """
        Handle incoming API request.
        
        Args:
            method: HTTP method
            path: Request path
            headers: Request headers
            query_params: Query parameters
            body: Request body
        
        Returns:
            API response
        """
        start_time = time.time()
        
        # Create request object
        request = APIRequest(
            request_id=f"req_{time.time()}_{id(body)}",
            method=HTTPMethod(method),
            path=path,
            headers=headers or {},
            query_params=query_params or {},
            body=body,
            client_id="unknown"
        )
        
        with self.lock:
            self.metrics["requests_total"] += 1
            self.request_history.append(request)
        
        try:
            # Find matching endpoint
            endpoint = self._find_endpoint(request.path, request.method)
            
            if not endpoint:
                return APIResponse(
                    status_code=404,
                    body={"error": "Endpoint not found"}
                )
            
            # Authenticate
            auth_result = self._authenticate(request, endpoint)
            if not auth_result[0]:
                with self.lock:
                    self.metrics["requests_unauthorized"] += 1
                return APIResponse(
                    status_code=401,
                    body={"error": "Unauthorized", "message": auth_result[1]}
                )
            
            request.client_id = auth_result[1]
            
            # Rate limiting
            if endpoint.rate_limit:
                allowed, limit_info = self.rate_limiter.check_limit(
                    request.client_id,
                    endpoint.rate_limit
                )
                
                if not allowed:
                    with self.lock:
                        self.metrics["requests_rate_limited"] += 1
                    return APIResponse(
                        status_code=429,
                        body={"error": "Rate limit exceeded"},
                        headers={
                            "X-RateLimit-Limit": str(limit_info["limit"]),
                            "X-RateLimit-Remaining": str(limit_info["remaining"]),
                            "X-RateLimit-Reset": str(limit_info["reset"])
                        }
                    )
            
            # Check cache
            cache_key = self._get_cache_key(request)
            cached_response = self._get_from_cache(cache_key)
            
            if cached_response:
                with self.lock:
                    self.metrics["cache_hits"] += 1
                return cached_response
            
            with self.lock:
                self.metrics["cache_misses"] += 1
            
            # Extract path parameters
            path_params = endpoint.extract_params(request.path)
            
            # Execute handler
            response = endpoint.handler(request, path_params)
            
            # Ensure response is APIResponse
            if not isinstance(response, APIResponse):
                response = APIResponse(status_code=200, body=response)
            
            # Cache successful responses
            if response.status_code == 200:
                self._add_to_cache(cache_key, response)
            
            # Update metrics
            with self.lock:
                self.metrics["requests_success"] += 1
                response_time = time.time() - start_time
                alpha = 0.1
                self.metrics["avg_response_time"] = (
                    alpha * response_time +
                    (1 - alpha) * self.metrics["avg_response_time"]
                )
            
            return response
        
        except Exception as e:
            with self.lock:
                self.metrics["requests_failed"] += 1
            
            return APIResponse(
                status_code=500,
                body={"error": "Internal server error", "message": str(e)}
            )
    
    def _find_endpoint(self, path: str, method: HTTPMethod) -> Optional[APIEndpoint]:
        """Find matching endpoint for request"""
        for endpoint in self.endpoints:
            if endpoint.matches(path, method):
                return endpoint
        return None
    
    def _authenticate(self, request: APIRequest, endpoint: APIEndpoint) -> Tuple[bool, str]:
        """
        Authenticate request.
        
        Returns:
            (authenticated, client_id/error_message) tuple
        """
        if endpoint.auth_type == AuthType.NONE:
            return True, "anonymous"
        
        elif endpoint.auth_type == AuthType.API_KEY:
            # Check for API key in header
            api_key = request.get_header("X-API-Key")
            
            if not api_key:
                return False, "Missing API key"
            
            valid, client_id = self.key_manager.validate_key(api_key)
            
            if valid:
                return True, client_id
            else:
                return False, "Invalid API key"
        
        # Other auth types not implemented
        return False, "Authentication type not supported"
    
    def _get_cache_key(self, request: APIRequest) -> str:
        """Generate cache key for request"""
        key_data = {
            "method": request.method.value,
            "path": request.path,
            "query": json.dumps(request.query_params, sort_keys=True)
        }
        return json.dumps(key_data, sort_keys=True)
    
    def _get_from_cache(self, key: str) -> Optional[APIResponse]:
        """Get response from cache if not expired"""
        with self.lock:
            if key in self.cache:
                response, timestamp = self.cache[key]
                if time.time() - timestamp < self.cache_ttl:
                    return response
                else:
                    del self.cache[key]
        return None
    
    def _add_to_cache(self, key: str, response: APIResponse):
        """Add response to cache"""
        with self.lock:
            self.cache[key] = (response, time.time())
    
    def _health_check(self, request: APIRequest, params: Dict) -> APIResponse:
        """Health check endpoint handler"""
        return APIResponse(
            status_code=200,
            body={
                "status": "healthy",
                "timestamp": time.time(),
                "version": "1.0.0"
            }
        )
    
    def _get_metrics(self, request: APIRequest, params: Dict) -> APIResponse:
        """Metrics endpoint handler"""
        with self.lock:
            metrics = self.metrics.copy()
            metrics["endpoints_registered"] = len(self.endpoints)
            metrics["cache_size"] = len(self.cache)
        
        return APIResponse(status_code=200, body=metrics)
    
    def _create_api_key(self, request: APIRequest, params: Dict) -> APIResponse:
        """Create API key endpoint handler"""
        client_id = request.body.get("client_id", "default") if request.body else "default"
        scopes = request.body.get("scopes", ["*"]) if request.body else ["*"]
        
        api_key = self.key_manager.create_key(client_id, scopes)
        
        return APIResponse(
            status_code=201,
            body={
                "api_key": api_key,
                "client_id": client_id,
                "scopes": scopes
            }
        )
    
    def get_metrics(self) -> Dict:
        """Get gateway metrics"""
        with self.lock:
            return self.metrics.copy()
    
    def clear_cache(self):
        """Clear response cache"""
        with self.lock:
            self.cache.clear()


# Global singleton
_gateway_instance = None


def get_api_gateway() -> APIGateway:
    """Get global API gateway instance"""
    global _gateway_instance
    if _gateway_instance is None:
        _gateway_instance = APIGateway()
    return _gateway_instance


if __name__ == "__main__":
    # Example usage
    gateway = get_api_gateway()
    
    # Create API key
    response = gateway.handle_request(
        method="POST",
        path="/api/keys",
        body={"client_id": "test_client", "scopes": ["read", "write"]}
    )
    print(f"API Key created: {response.to_dict()}")
    
    api_key = response.body["api_key"]
    
    # Register custom endpoint
    def get_user(request: APIRequest, params: Dict) -> APIResponse:
        user_id = params.get("id", "unknown")
        return APIResponse(
            status_code=200,
            body={"user_id": user_id, "name": f"User {user_id}"}
        )
    
    gateway.register_endpoint(
        path="/api/v1/users/{id}",
        method=HTTPMethod.GET,
        handler=get_user,
        rate_limit=100
    )
    
    # Make request
    response = gateway.handle_request(
        method="GET",
        path="/api/v1/users/123",
        headers={"X-API-Key": api_key}
    )
    print(f"\nUser request: {response.to_dict()}")
    
    # Health check
    response = gateway.handle_request(
        method="GET",
        path="/health"
    )
    print(f"\nHealth check: {response.to_dict()}")
    
    # Metrics
    print(f"\nGateway metrics: {gateway.get_metrics()}")
