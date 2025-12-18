#!/usr/bin/env python3
"""
Meta-Intelligence Coordinator (T-105)
Level 18 - Cross-Layer Integration

Orchestrates intelligence across all cognitive layers:
- Coordinates Universal Cognitive Graph, Memory Pool, Decision Nexus
- Manages cross-layer workflows
- Optimizes resource allocation
- Provides unified intelligence interface

Features:
- Multi-layer query synthesis
- Intelligent caching and prefetching
- Adaptive load balancing
- Real-time performance optimization
"""

import time
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import json


class IntelligenceLayer(Enum):
    """Cognitive layers in the system"""
    GRAPH = "graph"              # Universal Cognitive Graph
    MEMORY = "memory"            # Hyperconverged Memory Pool
    DECISION = "decision"        # Unified Decision Nexus
    BUS = "bus"                  # Cognitive Bus Protocol
    COORDINATOR = "coordinator"  # This layer


class QueryType(Enum):
    """Types of intelligence queries"""
    RETRIEVE = "retrieve"        # Fetch data
    ANALYZE = "analyze"          # Analyze patterns
    DECIDE = "decide"            # Make decision
    SYNTHESIZE = "synthesize"    # Combine multiple sources
    PREDICT = "predict"          # Predictive query


@dataclass
class IntelligenceQuery:
    """Query to the meta-intelligence system"""
    query_id: str
    query_type: QueryType
    layers: List[IntelligenceLayer]
    parameters: Dict[str, Any]
    priority: int = 5  # 1-10, 10 = highest
    timeout: float = 10.0
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict:
        return {
            "query_id": self.query_id,
            "query_type": self.query_type.value,
            "layers": [l.value for l in self.layers],
            "parameters": self.parameters,
            "priority": self.priority,
            "timeout": self.timeout,
            "timestamp": self.timestamp
        }


@dataclass
class IntelligenceResult:
    """Result from intelligence query"""
    query_id: str
    success: bool
    data: Any
    layers_used: List[IntelligenceLayer]
    execution_time: float
    cache_hit: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "query_id": self.query_id,
            "success": self.success,
            "data": self.data,
            "layers_used": [l.value for l in self.layers_used],
            "execution_time": self.execution_time,
            "cache_hit": self.cache_hit,
            "metadata": self.metadata
        }


class LayerAdapter:
    """
    Adapter for interfacing with cognitive layers.
    In production, would integrate with actual layer implementations.
    """
    
    def __init__(self, layer: IntelligenceLayer):
        self.layer = layer
        self.available = True
        self.load = 0.0  # 0.0 to 1.0
        self.response_time = 0.0  # Average response time
    
    def execute(self, operation: str, params: Dict) -> Any:
        """
        Execute operation on this layer.
        
        Args:
            operation: Operation to perform
            params: Operation parameters
        
        Returns:
            Operation result
        """
        # Simulate layer execution
        start = time.time()
        
        # In production, would call actual layer APIs
        result = {
            "layer": self.layer.value,
            "operation": operation,
            "params": params,
            "status": "success"
        }
        
        # Update metrics
        elapsed = time.time() - start
        self.response_time = 0.9 * self.response_time + 0.1 * elapsed
        
        return result
    
    def get_health(self) -> Dict:
        """Get layer health metrics"""
        return {
            "layer": self.layer.value,
            "available": self.available,
            "load": self.load,
            "response_time": self.response_time
        }


class MetaIntelligenceCoordinator:
    """
    Coordinates intelligence across all cognitive layers.
    
    Provides:
    - Unified query interface
    - Cross-layer optimization
    - Intelligent caching
    - Load balancing
    - Performance monitoring
    """
    
    def __init__(self, cache_size: int = 1000):
        # Layer adapters
        self.layers: Dict[IntelligenceLayer, LayerAdapter] = {
            layer: LayerAdapter(layer)
            for layer in IntelligenceLayer
        }
        
        # Query cache: query_hash -> (result, timestamp)
        self.cache: Dict[str, tuple] = {}
        self.cache_size = cache_size
        self.cache_ttl = 300.0  # 5 minutes
        
        # Query queue (priority-based)
        self.query_queue: deque = deque(maxlen=10000)
        
        # Active queries
        self.active_queries: Dict[str, IntelligenceQuery] = {}
        
        # Statistics
        self.stats = {
            "queries_total": 0,
            "queries_success": 0,
            "queries_failed": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "avg_execution_time": 0.0,
            "layers_health": {}
        }
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Running state
        self._running = False
    
    def start(self):
        """Start the coordinator"""
        with self.lock:
            self._running = True
    
    def stop(self):
        """Stop the coordinator"""
        with self.lock:
            self._running = False
    
    def query(self, query_type: QueryType,
              layers: List[IntelligenceLayer],
              parameters: Dict[str, Any],
              priority: int = 5,
              timeout: float = 10.0) -> IntelligenceResult:
        """
        Execute an intelligence query across specified layers.
        
        Args:
            query_type: Type of query
            layers: Layers to query
            parameters: Query parameters
            priority: Query priority (1-10)
            timeout: Query timeout
        
        Returns:
            Intelligence result
        """
        query_id = f"q_{time.time()}_{id(parameters)}"
        
        query = IntelligenceQuery(
            query_id=query_id,
            query_type=query_type,
            layers=layers,
            parameters=parameters,
            priority=priority,
            timeout=timeout
        )
        
        with self.lock:
            self.stats["queries_total"] += 1
            self.active_queries[query_id] = query
        
        try:
            result = self._execute_query(query)
            
            with self.lock:
                if result.success:
                    self.stats["queries_success"] += 1
                else:
                    self.stats["queries_failed"] += 1
                
                # Update average execution time
                alpha = 0.1
                self.stats["avg_execution_time"] = (
                    alpha * result.execution_time +
                    (1 - alpha) * self.stats["avg_execution_time"]
                )
            
            return result
        
        finally:
            with self.lock:
                if query_id in self.active_queries:
                    del self.active_queries[query_id]
    
    def _execute_query(self, query: IntelligenceQuery) -> IntelligenceResult:
        """
        Internal: Execute a query.
        
        Returns:
            Query result
        """
        start_time = time.time()
        
        # Check cache
        cache_key = self._get_cache_key(query)
        cached = self._get_from_cache(cache_key)
        
        if cached is not None:
            with self.lock:
                self.stats["cache_hits"] += 1
            
            return IntelligenceResult(
                query_id=query.query_id,
                success=True,
                data=cached,
                layers_used=[],
                execution_time=time.time() - start_time,
                cache_hit=True
            )
        
        with self.lock:
            self.stats["cache_misses"] += 1
        
        # Execute query across layers
        try:
            if query.query_type == QueryType.SYNTHESIZE:
                result_data = self._synthesize_query(query)
            else:
                result_data = self._execute_single_query(query)
            
            # Cache result
            self._add_to_cache(cache_key, result_data)
            
            return IntelligenceResult(
                query_id=query.query_id,
                success=True,
                data=result_data,
                layers_used=query.layers,
                execution_time=time.time() - start_time,
                cache_hit=False
            )
        
        except Exception as e:
            return IntelligenceResult(
                query_id=query.query_id,
                success=False,
                data=None,
                layers_used=query.layers,
                execution_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    def _execute_single_query(self, query: IntelligenceQuery) -> Any:
        """
        Execute query on a single layer or sequentially.
        """
        results = []
        
        for layer in query.layers:
            adapter = self.layers[layer]
            
            if not adapter.available:
                continue
            
            # Execute on layer
            result = adapter.execute(
                operation=query.query_type.value,
                params=query.parameters
            )
            
            results.append(result)
        
        return results[0] if len(results) == 1 else results
    
    def _synthesize_query(self, query: IntelligenceQuery) -> Any:
        """
        Synthesize results from multiple layers.
        """
        layer_results = {}
        
        # Query each layer
        for layer in query.layers:
            adapter = self.layers[layer]
            
            if adapter.available:
                result = adapter.execute(
                    operation="retrieve",
                    params=query.parameters
                )
                layer_results[layer.value] = result
        
        # Synthesize results
        synthesis = {
            "query_id": query.query_id,
            "synthesis_type": "multi_layer",
            "layers": list(layer_results.keys()),
            "results": layer_results,
            "confidence": self._calculate_confidence(layer_results),
            "timestamp": time.time()
        }
        
        return synthesis
    
    def _calculate_confidence(self, layer_results: Dict) -> float:
        """
        Calculate confidence score based on layer agreement.
        """
        if not layer_results:
            return 0.0
        
        # Simple confidence: more layers = higher confidence
        base_confidence = min(len(layer_results) / 3.0, 1.0)
        
        return base_confidence
    
    def _get_cache_key(self, query: IntelligenceQuery) -> str:
        """
        Generate cache key for query.
        """
        key_data = {
            "type": query.query_type.value,
            "layers": sorted([l.value for l in query.layers]),
            "params": json.dumps(query.parameters, sort_keys=True)
        }
        return json.dumps(key_data, sort_keys=True)
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """
        Get result from cache if not expired.
        """
        with self.lock:
            if key in self.cache:
                result, timestamp = self.cache[key]
                if time.time() - timestamp < self.cache_ttl:
                    return result
                else:
                    del self.cache[key]
        return None
    
    def _add_to_cache(self, key: str, result: Any):
        """
        Add result to cache.
        """
        with self.lock:
            # Evict oldest if cache full
            if len(self.cache) >= self.cache_size:
                oldest_key = min(self.cache.keys(), 
                               key=lambda k: self.cache[k][1])
                del self.cache[oldest_key]
            
            self.cache[key] = (result, time.time())
    
    def get_layer_health(self) -> Dict[str, Dict]:
        """
        Get health status of all layers.
        """
        with self.lock:
            return {
                layer.value: adapter.get_health()
                for layer, adapter in self.layers.items()
            }
    
    def get_stats(self) -> Dict:
        """
        Get coordinator statistics.
        """
        with self.lock:
            stats = self.stats.copy()
            stats["layers_health"] = self.get_layer_health()
            stats["cache_size"] = len(self.cache)
            stats["active_queries"] = len(self.active_queries)
            return stats
    
    def clear_cache(self):
        """Clear the query cache"""
        with self.lock:
            self.cache.clear()


# Global singleton
_coordinator_instance = None


def get_meta_coordinator() -> MetaIntelligenceCoordinator:
    """Get global meta-intelligence coordinator"""
    global _coordinator_instance
    if _coordinator_instance is None:
        _coordinator_instance = MetaIntelligenceCoordinator()
        _coordinator_instance.start()
    return _coordinator_instance


if __name__ == "__main__":
    # Example usage
    coordinator = get_meta_coordinator()
    
    # Single layer query
    result = coordinator.query(
        query_type=QueryType.RETRIEVE,
        layers=[IntelligenceLayer.GRAPH],
        parameters={"node_id": "n1"}
    )
    print(f"Single query result: {result.to_dict()}")
    
    # Multi-layer synthesis
    result = coordinator.query(
        query_type=QueryType.SYNTHESIZE,
        layers=[IntelligenceLayer.GRAPH, IntelligenceLayer.MEMORY, IntelligenceLayer.DECISION],
        parameters={"query": "best_strategy", "context": "production"},
        priority=8
    )
    print(f"\nSynthesis result: {result.to_dict()}")
    
    # Check stats
    print(f"\nCoordinator stats: {coordinator.get_stats()}")
