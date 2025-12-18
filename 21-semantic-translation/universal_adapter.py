#!/usr/bin/env python3
"""
Universal Adapter Framework - Level 18

Enables seamless system integration through:
- Automatic API discovery and integration
- Protocol translation
- Seamless system interoperability

Part of New Build 8: Collective Consciousness & Universal Integration
"""

import time
import threading
from typing import Dict, List, Any, Optional, Set, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json
import hashlib


@dataclass
class APIEndpoint:
    """Represents an API endpoint."""
    endpoint_id: str
    url: str
    method: str  # GET, POST, PUT, DELETE, etc.
    protocol: str  # REST, GraphQL, gRPC, WebSocket, etc.
    parameters: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    authentication: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemInterface:
    """Represents a system interface."""
    system_id: str
    name: str
    protocol: str
    endpoints: List[APIEndpoint] = field(default_factory=list)
    capabilities: Set[str] = field(default_factory=set)
    discovered_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProtocolAdapter:
    """Represents a protocol adapter."""
    adapter_id: str
    source_protocol: str
    target_protocol: str
    translator: Callable
    bidirectional: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationResult:
    """Represents the result of a system integration."""
    integration_id: str
    source_system: str
    target_system: str
    success: bool
    data_transferred: Any
    protocol_used: str
    timestamp: float = field(default_factory=time.time)
    error: Optional[str] = None


class APIDiscovery:
    """Discovers and catalogs APIs automatically."""
    
    def __init__(self):
        self.discovered_systems: Dict[str, SystemInterface] = {}
        self.discovery_methods: List[Callable] = []
        self.lock = threading.Lock()
    
    def register_discovery_method(self, method: Callable) -> bool:
        """Register a method for API discovery."""
        with self.lock:
            self.discovery_methods.append(method)
            return True
    
    def discover_system(self, system_id: str, base_url: str,
                       protocol: str = "REST") -> Optional[SystemInterface]:
        """Discover a system's API."""
        with self.lock:
            # Simulate API discovery
            endpoints = self._discover_endpoints(base_url, protocol)
            capabilities = self._discover_capabilities(endpoints)
            
            system = SystemInterface(
                system_id=system_id,
                name=system_id.replace("_", " ").title(),
                protocol=protocol,
                endpoints=endpoints,
                capabilities=capabilities
            )
            
            self.discovered_systems[system_id] = system
            return system
    
    def _discover_endpoints(self, base_url: str, protocol: str) -> List[APIEndpoint]:
        """Discover endpoints for a system."""
        # Simplified endpoint discovery
        common_paths = ["/api/v1/data", "/api/v1/status", "/api/v1/config"]
        endpoints = []
        
        for i, path in enumerate(common_paths):
            endpoint = APIEndpoint(
                endpoint_id=f"endpoint_{i}",
                url=f"{base_url}{path}",
                method="GET",
                protocol=protocol
            )
            endpoints.append(endpoint)
        
        return endpoints
    
    def _discover_capabilities(self, endpoints: List[APIEndpoint]) -> Set[str]:
        """Discover capabilities from endpoints."""
        capabilities = set()
        
        for endpoint in endpoints:
            if "data" in endpoint.url:
                capabilities.add("data_access")
            if "status" in endpoint.url:
                capabilities.add("health_check")
            if "config" in endpoint.url:
                capabilities.add("configuration")
        
        return capabilities
    
    def find_systems_by_capability(self, capability: str) -> List[SystemInterface]:
        """Find systems with a specific capability."""
        with self.lock:
            return [
                system for system in self.discovered_systems.values()
                if capability in system.capabilities
            ]
    
    def get_discovery_stats(self) -> Dict[str, Any]:
        """Get discovery statistics."""
        with self.lock:
            protocol_counts = defaultdict(int)
            capability_counts = defaultdict(int)
            
            for system in self.discovered_systems.values():
                protocol_counts[system.protocol] += 1
                for cap in system.capabilities:
                    capability_counts[cap] += 1
            
            return {
                "total_systems": len(self.discovered_systems),
                "protocols": dict(protocol_counts),
                "capabilities": dict(capability_counts)
            }


class ProtocolTranslator:
    """Translates between different protocols."""
    
    def __init__(self):
        self.adapters: Dict[Tuple[str, str], ProtocolAdapter] = {}
        self.translation_history: List[Dict[str, Any]] = []
        self.lock = threading.Lock()
    
    def register_adapter(self, adapter_id: str, source_protocol: str,
                        target_protocol: str, translator: Callable,
                        bidirectional: bool = False) -> bool:
        """Register a protocol adapter."""
        with self.lock:
            adapter = ProtocolAdapter(
                adapter_id=adapter_id,
                source_protocol=source_protocol,
                target_protocol=target_protocol,
                translator=translator,
                bidirectional=bidirectional
            )
            
            self.adapters[(source_protocol, target_protocol)] = adapter
            
            if bidirectional:
                # Create reverse adapter
                reverse_adapter = ProtocolAdapter(
                    adapter_id=f"{adapter_id}_reverse",
                    source_protocol=target_protocol,
                    target_protocol=source_protocol,
                    translator=translator,
                    bidirectional=True
                )
                self.adapters[(target_protocol, source_protocol)] = reverse_adapter
            
            return True
    
    def translate(self, data: Any, source_protocol: str,
                 target_protocol: str) -> Optional[Any]:
        """Translate data between protocols."""
        with self.lock:
            adapter_key = (source_protocol, target_protocol)
            
            if adapter_key not in self.adapters:
                # Try to find a path through intermediate protocols
                translated = self._translate_via_path(data, source_protocol, target_protocol)
            else:
                adapter = self.adapters[adapter_key]
                translated = adapter.translator(data)
            
            # Record translation
            self.translation_history.append({
                "source_protocol": source_protocol,
                "target_protocol": target_protocol,
                "timestamp": time.time(),
                "success": translated is not None
            })
            
            return translated
    
    def _translate_via_path(self, data: Any, source: str, target: str) -> Optional[Any]:
        """Translate via intermediate protocols."""
        # Simple BFS to find translation path
        queue = [(source, data, [source])]
        visited = {source}
        
        while queue:
            current_protocol, current_data, path = queue.pop(0)
            
            if current_protocol == target:
                return current_data
            
            # Find next hops
            for (src, tgt), adapter in self.adapters.items():
                if src == current_protocol and tgt not in visited:
                    translated = adapter.translator(current_data)
                    if translated is not None:
                        visited.add(tgt)
                        queue.append((tgt, translated, path + [tgt]))
        
        return None
    
    def get_supported_protocols(self) -> Set[str]:
        """Get all supported protocols."""
        with self.lock:
            protocols = set()
            for src, tgt in self.adapters.keys():
                protocols.add(src)
                protocols.add(tgt)
            return protocols
    
    def get_translation_stats(self) -> Dict[str, Any]:
        """Get translation statistics."""
        with self.lock:
            if not self.translation_history:
                return {"total_translations": 0, "success_rate": 0.0}
            
            successful = sum(1 for t in self.translation_history if t["success"])
            
            return {
                "total_translations": len(self.translation_history),
                "success_rate": successful / len(self.translation_history),
                "supported_protocols": len(self.get_supported_protocols())
            }


class SystemInteroperability:
    """Manages interoperability between systems."""
    
    def __init__(self):
        self.integrations: List[IntegrationResult] = []
        self.connection_map: Dict[str, Set[str]] = defaultdict(set)
        self.lock = threading.Lock()
    
    def integrate_systems(self, source_system: str, target_system: str,
                         data: Any, protocol: str) -> IntegrationResult:
        """Integrate two systems."""
        with self.lock:
            # Simulate integration
            success = True
            error = None
            
            try:
                # In real implementation, this would make actual API calls
                transferred_data = self._transfer_data(data, protocol)
            except Exception as e:
                success = False
                error = str(e)
                transferred_data = None
            
            result = IntegrationResult(
                integration_id=f"integration_{len(self.integrations)}",
                source_system=source_system,
                target_system=target_system,
                success=success,
                data_transferred=transferred_data,
                protocol_used=protocol,
                error=error
            )
            
            self.integrations.append(result)
            
            if success:
                self.connection_map[source_system].add(target_system)
            
            return result
    
    def _transfer_data(self, data: Any, protocol: str) -> Any:
        """Transfer data using specified protocol."""
        # Simplified data transfer simulation
        if protocol == "REST":
            return {"status": "success", "data": data}
        elif protocol == "GraphQL":
            return {"data": data, "errors": []}
        elif protocol == "gRPC":
            return {"result": data, "status": "OK"}
        else:
            return data
    
    def get_connected_systems(self, system_id: str) -> Set[str]:
        """Get systems connected to a given system."""
        with self.lock:
            return self.connection_map.get(system_id, set())
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration statistics."""
        with self.lock:
            if not self.integrations:
                return {"total_integrations": 0, "success_rate": 0.0}
            
            successful = sum(1 for i in self.integrations if i.success)
            protocol_counts = defaultdict(int)
            
            for integration in self.integrations:
                protocol_counts[integration.protocol_used] += 1
            
            return {
                "total_integrations": len(self.integrations),
                "success_rate": successful / len(self.integrations),
                "protocols_used": dict(protocol_counts),
                "connected_systems": len(self.connection_map)
            }


class UniversalAdapter:
    """Main universal adapter framework."""
    
    def __init__(self):
        self.api_discovery = APIDiscovery()
        self.protocol_translator = ProtocolTranslator()
        self.interoperability = SystemInteroperability()
        self.lock = threading.Lock()
        self.active = True
        
        # Register default protocol adapters
        self._register_default_adapters()
    
    def _register_default_adapters(self):
        """Register default protocol adapters."""
        # REST to GraphQL
        self.protocol_translator.register_adapter(
            "rest_to_graphql",
            "REST",
            "GraphQL",
            lambda data: {"query": data},
            bidirectional=False
        )
        
        # REST to gRPC
        self.protocol_translator.register_adapter(
            "rest_to_grpc",
            "REST",
            "gRPC",
            lambda data: {"message": data},
            bidirectional=False
        )
        
        # GraphQL to REST
        self.protocol_translator.register_adapter(
            "graphql_to_rest",
            "GraphQL",
            "REST",
            lambda data: data.get("data", data),
            bidirectional=False
        )
    
    def discover_and_integrate(self, system_id: str, base_url: str,
                              protocol: str = "REST") -> Optional[SystemInterface]:
        """Discover a system and prepare for integration."""
        return self.api_discovery.discover_system(system_id, base_url, protocol)
    
    def integrate(self, source_system: str, target_system: str,
                 data: Any, source_protocol: str,
                 target_protocol: str) -> IntegrationResult:
        """Integrate two systems with protocol translation."""
        # Translate protocol if needed
        if source_protocol != target_protocol:
            translated_data = self.protocol_translator.translate(
                data, source_protocol, target_protocol
            )
            if translated_data is None:
                return IntegrationResult(
                    integration_id="failed",
                    source_system=source_system,
                    target_system=target_system,
                    success=False,
                    data_transferred=None,
                    protocol_used=target_protocol,
                    error="Protocol translation failed"
                )
        else:
            translated_data = data
        
        # Perform integration
        return self.interoperability.integrate_systems(
            source_system,
            target_system,
            translated_data,
            target_protocol
        )
    
    def register_protocol_adapter(self, adapter_id: str, source_protocol: str,
                                 target_protocol: str, translator: Callable) -> bool:
        """Register a custom protocol adapter."""
        return self.protocol_translator.register_adapter(
            adapter_id, source_protocol, target_protocol, translator
        )
    
    def find_integration_path(self, source_system: str,
                            target_system: str) -> Optional[List[str]]:
        """Find integration path between systems."""
        # Simple path finding through connected systems
        queue = [([source_system], {source_system})]
        
        while queue:
            path, visited = queue.pop(0)
            current = path[-1]
            
            if current == target_system:
                return path
            
            # Get connected systems
            connected = self.interoperability.get_connected_systems(current)
            for next_system in connected:
                if next_system not in visited:
                    new_path = path + [next_system]
                    new_visited = visited | {next_system}
                    queue.append((new_path, new_visited))
        
        return None
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        with self.lock:
            return {
                "active": self.active,
                "discovery_stats": self.api_discovery.get_discovery_stats(),
                "translation_stats": self.protocol_translator.get_translation_stats(),
                "integration_stats": self.interoperability.get_integration_stats()
            }
    
    def shutdown(self):
        """Shutdown the adapter."""
        with self.lock:
            self.active = False


# Singleton pattern
_adapters: Dict[str, UniversalAdapter] = {}
_adapter_lock = threading.Lock()


def get_universal_adapter(adapter_id: str = "default") -> UniversalAdapter:
    """Get or create a universal adapter."""
    with _adapter_lock:
        if adapter_id not in _adapters:
            _adapters[adapter_id] = UniversalAdapter()
        return _adapters[adapter_id]


class UniversalAdapterContract:
    """Contract interface for testing."""
    
    @staticmethod
    def discover_api(system_id: str, base_url: str) -> Dict[str, Any]:
        """Discover an API."""
        adapter = get_universal_adapter("test")
        
        system = adapter.discover_and_integrate(system_id, base_url, "REST")
        
        adapter.shutdown()
        
        if system:
            return {
                "system_id": system.system_id,
                "protocol": system.protocol,
                "endpoints": len(system.endpoints),
                "capabilities": list(system.capabilities)
            }
        return {}
    
    @staticmethod
    def translate_protocol(source_protocol: str, target_protocol: str) -> Dict[str, Any]:
        """Translate between protocols."""
        adapter = get_universal_adapter("test")
        
        test_data = {"key": "value", "number": 42}
        translated = adapter.protocol_translator.translate(
            test_data, source_protocol, target_protocol
        )
        
        adapter.shutdown()
        
        return {
            "source_protocol": source_protocol,
            "target_protocol": target_protocol,
            "success": translated is not None,
            "translated_data": translated
        }
    
    @staticmethod
    def integrate_systems(system_count: int) -> Dict[str, Any]:
        """Integrate multiple systems."""
        adapter = get_universal_adapter("test")
        
        # Discover systems
        for i in range(system_count):
            adapter.discover_and_integrate(
                f"system_{i}",
                f"http://api{i}.example.com",
                "REST"
            )
        
        # Integrate systems
        results = []
        for i in range(system_count - 1):
            result = adapter.integrate(
                f"system_{i}",
                f"system_{i+1}",
                {"data": f"from_system_{i}"},
                "REST",
                "REST"
            )
            results.append(result)
        
        stats = adapter.get_system_stats()
        adapter.shutdown()
        
        return {
            "systems_integrated": system_count,
            "integrations_performed": len(results),
            "success_rate": sum(1 for r in results if r.success) / len(results) if results else 0,
            "stats": stats
        }


def demo():
    """Demonstrate universal adapter capabilities."""
    print("=== Universal Adapter Framework Demo ===")
    print()
    
    adapter = get_universal_adapter("demo")
    
    # Discover systems
    print("1. Discovering systems...")
    system1 = adapter.discover_and_integrate("payment_api", "https://api.payment.com", "REST")
    system2 = adapter.discover_and_integrate("analytics_api", "https://api.analytics.com", "GraphQL")
    system3 = adapter.discover_and_integrate("messaging_api", "https://api.messaging.com", "gRPC")
    print(f"   Discovered 3 systems\n")
    
    # Show discovered capabilities
    print("2. System capabilities:")
    if system1:
        print(f"   {system1.name}: {system1.capabilities}")
    if system2:
        print(f"   {system2.name}: {system2.capabilities}")
    if system3:
        print(f"   {system3.name}: {system3.capabilities}")
    print()
    
    # Protocol translation
    print("3. Protocol translation...")
    test_data = {"transaction_id": "12345", "amount": 100.00}
    translated = adapter.protocol_translator.translate(test_data, "REST", "GraphQL")
    print(f"   REST data: {test_data}")
    print(f"   GraphQL data: {translated}\n")
    
    # System integration
    print("4. Integrating systems...")
    result1 = adapter.integrate(
        "payment_api",
        "analytics_api",
        {"event": "payment_processed"},
        "REST",
        "GraphQL"
    )
    print(f"   Payment → Analytics: {result1.success}")
    
    result2 = adapter.integrate(
        "analytics_api",
        "messaging_api",
        {"notification": "alert"},
        "GraphQL",
        "gRPC"
    )
    print(f"   Analytics → Messaging: {result2.success}\n")
    
    # Find integration path
    print("5. Finding integration path...")
    path = adapter.find_integration_path("payment_api", "messaging_api")
    if path:
        print(f"   Path: {' → '.join(path)}\n")
    
    # System statistics
    print("6. System statistics:")
    stats = adapter.get_system_stats()
    print(f"   Discovered systems: {stats['discovery_stats']['total_systems']}")
    print(f"   Supported protocols: {stats['translation_stats']['supported_protocols']}")
    print(f"   Total integrations: {stats['integration_stats']['total_integrations']}")
    print(f"   Success rate: {stats['integration_stats']['success_rate']:.1%}")
    
    adapter.shutdown()
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    demo()
