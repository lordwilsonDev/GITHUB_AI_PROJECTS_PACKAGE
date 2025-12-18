#!/usr/bin/env python3
"""
Ecosystem Connectors - New Build 6, Phase 3
API integration framework, protocol adapters, and service mesh integration
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import hashlib


class ConnectorType(Enum):
    """Types of external connectors"""
    REST_API = "rest_api"
    GRAPHQL = "graphql"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    MESSAGE_QUEUE = "message_queue"
    DATABASE = "database"
    CUSTOM = "custom"


class ProtocolType(Enum):
    """Communication protocols"""
    HTTP = "http"
    HTTPS = "https"
    TCP = "tcp"
    UDP = "udp"
    AMQP = "amqp"
    MQTT = "mqtt"
    KAFKA = "kafka"


class AuthMethod(Enum):
    """Authentication methods"""
    NONE = "none"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    JWT = "jwt"
    BASIC = "basic"
    CUSTOM = "custom"


@dataclass
class ConnectionConfig:
    """Configuration for external connection"""
    connector_id: str
    connector_type: ConnectorType
    protocol: ProtocolType
    endpoint: str
    auth_method: AuthMethod = AuthMethod.NONE
    credentials: Dict[str, str] = field(default_factory=dict)
    timeout: int = 30
    retry_count: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'connector_id': self.connector_id,
            'connector_type': self.connector_type.value,
            'protocol': self.protocol.value,
            'endpoint': self.endpoint,
            'auth_method': self.auth_method.value,
            'timeout': self.timeout,
            'retry_count': self.retry_count,
            'metadata': self.metadata
        }


@dataclass
class APIRequest:
    """Represents an API request"""
    request_id: str
    method: str  # GET, POST, PUT, DELETE, etc.
    path: str
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    params: Dict[str, str] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'request_id': self.request_id,
            'method': self.method,
            'path': self.path,
            'headers': self.headers,
            'body': self.body,
            'params': self.params,
            'timestamp': self.timestamp
        }


@dataclass
class APIResponse:
    """Represents an API response"""
    request_id: str
    status_code: int
    headers: Dict[str, str] = field(default_factory=dict)
    body: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    duration: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'request_id': self.request_id,
            'status_code': self.status_code,
            'headers': self.headers,
            'body': self.body,
            'error': self.error,
            'timestamp': self.timestamp,
            'duration': self.duration
        }
    
    def is_success(self) -> bool:
        """Check if response is successful"""
        return 200 <= self.status_code < 300


class BaseConnector:
    """Base class for all connectors"""
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.connected = False
        self.request_history: List[APIRequest] = []
        self.response_history: List[APIResponse] = []
        self.lock = threading.Lock()
        
    def connect(self) -> bool:
        """Establish connection"""
        with self.lock:
            # Simulate connection
            self.connected = True
            return True
    
    def disconnect(self) -> bool:
        """Close connection"""
        with self.lock:
            self.connected = False
            return True
    
    def send_request(self, request: APIRequest) -> APIResponse:
        """Send request to external system"""
        raise NotImplementedError("Subclasses must implement send_request")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get connector statistics"""
        with self.lock:
            success_count = sum(1 for r in self.response_history if r.is_success())
            
            return {
                'connector_id': self.config.connector_id,
                'connector_type': self.config.connector_type.value,
                'connected': self.connected,
                'total_requests': len(self.request_history),
                'successful_requests': success_count,
                'failed_requests': len(self.response_history) - success_count
            }


class RESTAPIConnector(BaseConnector):
    """REST API connector"""
    
    def send_request(self, request: APIRequest) -> APIResponse:
        """Send REST API request"""
        start_time = time.time()
        
        with self.lock:
            self.request_history.append(request)
        
        # Simulate API call
        if not self.connected:
            response = APIResponse(
                request_id=request.request_id,
                status_code=503,
                error="Not connected",
                duration=time.time() - start_time
            )
        else:
            # Simulate successful response
            response = APIResponse(
                request_id=request.request_id,
                status_code=200,
                headers={'Content-Type': 'application/json'},
                body={'status': 'success', 'data': {'result': 'simulated'}},
                duration=time.time() - start_time
            )
        
        with self.lock:
            self.response_history.append(response)
        
        return response


class GraphQLConnector(BaseConnector):
    """GraphQL connector"""
    
    def send_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> APIResponse:
        """Send GraphQL query"""
        request = APIRequest(
            request_id=f"gql_{len(self.request_history)}",
            method="POST",
            path="/graphql",
            body={'query': query, 'variables': variables or {}}
        )
        
        return self.send_request(request)
    
    def send_request(self, request: APIRequest) -> APIResponse:
        """Send GraphQL request"""
        start_time = time.time()
        
        with self.lock:
            self.request_history.append(request)
        
        if not self.connected:
            response = APIResponse(
                request_id=request.request_id,
                status_code=503,
                error="Not connected",
                duration=time.time() - start_time
            )
        else:
            response = APIResponse(
                request_id=request.request_id,
                status_code=200,
                body={'data': {'result': 'simulated GraphQL response'}},
                duration=time.time() - start_time
            )
        
        with self.lock:
            self.response_history.append(response)
        
        return response


class MessageQueueConnector(BaseConnector):
    """Message queue connector"""
    
    def __init__(self, config: ConnectionConfig):
        super().__init__(config)
        self.message_queue: List[Dict[str, Any]] = []
        
    def publish(self, topic: str, message: Dict[str, Any]) -> bool:
        """Publish message to queue"""
        with self.lock:
            if not self.connected:
                return False
            
            self.message_queue.append({
                'topic': topic,
                'message': message,
                'timestamp': time.time()
            })
            return True
    
    def subscribe(self, topic: str) -> List[Dict[str, Any]]:
        """Subscribe to topic and get messages"""
        with self.lock:
            if not self.connected:
                return []
            
            return [
                msg for msg in self.message_queue
                if msg['topic'] == topic
            ]
    
    def send_request(self, request: APIRequest) -> APIResponse:
        """Send request via message queue"""
        start_time = time.time()
        
        # Convert request to message
        success = self.publish(
            topic=request.path,
            message=request.to_dict()
        )
        
        response = APIResponse(
            request_id=request.request_id,
            status_code=200 if success else 503,
            body={'published': success},
            duration=time.time() - start_time
        )
        
        with self.lock:
            self.response_history.append(response)
        
        return response


class ProtocolAdapter:
    """Adapts between different protocols"""
    
    def __init__(self):
        self.adapters: Dict[Tuple[ProtocolType, ProtocolType], Callable] = {}
        self.adaptation_history: List[Dict[str, Any]] = []
        
    def register_adapter(self, from_protocol: ProtocolType, to_protocol: ProtocolType, adapter_func: Callable):
        """Register a protocol adapter"""
        self.adapters[(from_protocol, to_protocol)] = adapter_func
    
    def adapt(self, data: Any, from_protocol: ProtocolType, to_protocol: ProtocolType) -> Any:
        """Adapt data from one protocol to another"""
        adapter_key = (from_protocol, to_protocol)
        
        if adapter_key in self.adapters:
            adapted_data = self.adapters[adapter_key](data)
        else:
            # Default: pass through
            adapted_data = data
        
        self.adaptation_history.append({
            'from': from_protocol.value,
            'to': to_protocol.value,
            'timestamp': time.time()
        })
        
        return adapted_data
    
    def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics"""
        return {
            'registered_adapters': len(self.adapters),
            'total_adaptations': len(self.adaptation_history)
        }


class ServiceMeshIntegration:
    """Service mesh integration layer"""
    
    def __init__(self):
        self.services: Dict[str, BaseConnector] = {}
        self.routing_table: Dict[str, str] = {}  # path -> service_id
        self.lock = threading.Lock()
        
    def register_service(self, service_id: str, connector: BaseConnector) -> bool:
        """Register a service in the mesh"""
        with self.lock:
            self.services[service_id] = connector
            return True
    
    def add_route(self, path: str, service_id: str) -> bool:
        """Add routing rule"""
        with self.lock:
            if service_id not in self.services:
                return False
            self.routing_table[path] = service_id
            return True
    
    def route_request(self, request: APIRequest) -> Optional[APIResponse]:
        """Route request to appropriate service"""
        with self.lock:
            service_id = self.routing_table.get(request.path)
            
            if not service_id or service_id not in self.services:
                return APIResponse(
                    request_id=request.request_id,
                    status_code=404,
                    error="Service not found"
                )
            
            connector = self.services[service_id]
        
        # Send request outside lock
        return connector.send_request(request)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get service mesh statistics"""
        with self.lock:
            service_stats = {
                service_id: connector.get_stats()
                for service_id, connector in self.services.items()
            }
            
            return {
                'total_services': len(self.services),
                'total_routes': len(self.routing_table),
                'services': service_stats
            }


class EcosystemConnectors:
    """Main ecosystem connectors system"""
    
    def __init__(self):
        self.connectors: Dict[str, BaseConnector] = {}
        self.protocol_adapter = ProtocolAdapter()
        self.service_mesh = ServiceMeshIntegration()
        self.lock = threading.Lock()
        
    def create_connector(self, config: ConnectionConfig) -> BaseConnector:
        """Create a connector based on configuration"""
        if config.connector_type == ConnectorType.REST_API:
            connector = RESTAPIConnector(config)
        elif config.connector_type == ConnectorType.GRAPHQL:
            connector = GraphQLConnector(config)
        elif config.connector_type == ConnectorType.MESSAGE_QUEUE:
            connector = MessageQueueConnector(config)
        else:
            connector = BaseConnector(config)
        
        with self.lock:
            self.connectors[config.connector_id] = connector
        
        return connector
    
    def get_connector(self, connector_id: str) -> Optional[BaseConnector]:
        """Get connector by ID"""
        with self.lock:
            return self.connectors.get(connector_id)
    
    def connect_all(self) -> Dict[str, bool]:
        """Connect all connectors"""
        results = {}
        with self.lock:
            connectors = list(self.connectors.items())
        
        for connector_id, connector in connectors:
            results[connector_id] = connector.connect()
        
        return results
    
    def disconnect_all(self) -> Dict[str, bool]:
        """Disconnect all connectors"""
        results = {}
        with self.lock:
            connectors = list(self.connectors.items())
        
        for connector_id, connector in connectors:
            results[connector_id] = connector.disconnect()
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        with self.lock:
            connector_stats = {
                connector_id: connector.get_stats()
                for connector_id, connector in self.connectors.items()
            }
        
        return {
            'total_connectors': len(self.connectors),
            'protocol_adapter': self.protocol_adapter.get_stats(),
            'service_mesh': self.service_mesh.get_stats(),
            'connectors': connector_stats
        }
    
    def demo(self) -> Dict[str, Any]:
        """Demonstrate ecosystem connectors capabilities"""
        print("\n=== Ecosystem Connectors Demo ===")
        
        # 1. Create REST API connector
        print("\n1. Creating REST API connector...")
        rest_config = ConnectionConfig(
            connector_id="rest_api_1",
            connector_type=ConnectorType.REST_API,
            protocol=ProtocolType.HTTPS,
            endpoint="https://api.example.com",
            auth_method=AuthMethod.API_KEY,
            credentials={'api_key': 'test_key_123'}
        )
        rest_connector = self.create_connector(rest_config)
        rest_connector.connect()
        print(f"   Created and connected: {rest_config.connector_id}")
        
        # 2. Create GraphQL connector
        print("\n2. Creating GraphQL connector...")
        graphql_config = ConnectionConfig(
            connector_id="graphql_1",
            connector_type=ConnectorType.GRAPHQL,
            protocol=ProtocolType.HTTPS,
            endpoint="https://graphql.example.com"
        )
        graphql_connector = self.create_connector(graphql_config)
        graphql_connector.connect()
        print(f"   Created and connected: {graphql_config.connector_id}")
        
        # 3. Create message queue connector
        print("\n3. Creating message queue connector...")
        mq_config = ConnectionConfig(
            connector_id="mq_1",
            connector_type=ConnectorType.MESSAGE_QUEUE,
            protocol=ProtocolType.AMQP,
            endpoint="amqp://localhost:5672"
        )
        mq_connector = self.create_connector(mq_config)
        mq_connector.connect()
        print(f"   Created and connected: {mq_config.connector_id}")
        
        # 4. Send requests
        print("\n4. Sending requests...")
        rest_request = APIRequest(
            request_id="req_1",
            method="GET",
            path="/api/data"
        )
        rest_response = rest_connector.send_request(rest_request)
        print(f"   REST response: {rest_response.status_code} ({rest_response.duration:.3f}s)")
        
        graphql_response = graphql_connector.send_query("{ user { name } }")
        print(f"   GraphQL response: {graphql_response.status_code} ({graphql_response.duration:.3f}s)")
        
        mq_connector.publish("test_topic", {"message": "Hello"})
        messages = mq_connector.subscribe("test_topic")
        print(f"   Message queue: Published and retrieved {len(messages)} messages")
        
        # 5. Service mesh integration
        print("\n5. Setting up service mesh...")
        self.service_mesh.register_service("rest_api_1", rest_connector)
        self.service_mesh.register_service("graphql_1", graphql_connector)
        self.service_mesh.add_route("/api/data", "rest_api_1")
        self.service_mesh.add_route("/graphql", "graphql_1")
        print(f"   Registered 2 services with 2 routes")
        
        # 6. Route request through mesh
        print("\n6. Routing request through service mesh...")
        mesh_request = APIRequest(
            request_id="mesh_req_1",
            method="GET",
            path="/api/data"
        )
        mesh_response = self.service_mesh.route_request(mesh_request)
        print(f"   Mesh routed response: {mesh_response.status_code}")
        
        # 7. Get statistics
        print("\n7. System statistics:")
        stats = self.get_stats()
        print(f"   Total connectors: {stats['total_connectors']}")
        print(f"   Service mesh services: {stats['service_mesh']['total_services']}")
        print(f"   Service mesh routes: {stats['service_mesh']['total_routes']}")
        
        print("\n=== Demo Complete ===")
        return stats


class EcosystemConnectorsContract:
    """Contract interface for testing"""
    
    @staticmethod
    def create() -> EcosystemConnectors:
        """Create an ecosystem connectors instance"""
        return EcosystemConnectors()
    
    @staticmethod
    def verify() -> bool:
        """Verify ecosystem connectors functionality"""
        ec = EcosystemConnectors()
        
        # Test connector creation
        config = ConnectionConfig(
            connector_id="test_1",
            connector_type=ConnectorType.REST_API,
            protocol=ProtocolType.HTTPS,
            endpoint="https://test.example.com"
        )
        connector = ec.create_connector(config)
        if not connector:
            return False
        
        # Test connection
        if not connector.connect():
            return False
        
        # Test request
        request = APIRequest(
            request_id="test_req",
            method="GET",
            path="/test"
        )
        response = connector.send_request(request)
        if not response:
            return False
        
        # Test service mesh
        ec.service_mesh.register_service("test_1", connector)
        ec.service_mesh.add_route("/test", "test_1")
        mesh_response = ec.service_mesh.route_request(request)
        if not mesh_response:
            return False
        
        # Test statistics
        stats = ec.get_stats()
        if stats['total_connectors'] != 1:
            return False
        
        return True


if __name__ == "__main__":
    # Run demo
    ec = EcosystemConnectors()
    ec.demo()
