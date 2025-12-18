#!/usr/bin/env python3
"""
Resource Allocation Algorithms

Intelligent resource allocation system that optimizes distribution of
computational resources, time, and system capabilities across tasks.

Author: Vy Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict
import heapq
from collections import defaultdict
import numpy as np


class ResourceType(Enum):
    """Types of resources that can be allocated."""
    CPU = "cpu"
    MEMORY = "memory"
    TIME = "time"
    NETWORK = "network"
    STORAGE = "storage"
    PRIORITY = "priority"
    CUSTOM = "custom"


class AllocationStrategy(Enum):
    """Resource allocation strategies."""
    GREEDY = "greedy"  # Allocate to highest priority first
    FAIR_SHARE = "fair_share"  # Equal distribution
    PROPORTIONAL = "proportional"  # Based on weights
    PREDICTIVE = "predictive"  # Based on predicted needs
    ADAPTIVE = "adaptive"  # Learn from patterns
    ROUND_ROBIN = "round_robin"  # Rotate allocations
    PRIORITY_BASED = "priority_based"  # Strict priority ordering


@dataclass
class Resource:
    """Represents a resource that can be allocated."""
    type: ResourceType
    total_capacity: float
    available: float
    unit: str
    min_allocation: float = 0.0
    max_allocation: Optional[float] = None
    
    def allocate(self, amount: float) -> bool:
        """Attempt to allocate resource."""
        if amount <= self.available:
            self.available -= amount
            return True
        return False
    
    def release(self, amount: float):
        """Release allocated resource."""
        self.available = min(self.available + amount, self.total_capacity)
    
    def utilization(self) -> float:
        """Get current utilization percentage."""
        return (self.total_capacity - self.available) / self.total_capacity if self.total_capacity > 0 else 0.0


@dataclass
class AllocationRequest:
    """Represents a request for resource allocation."""
    id: str
    task_id: str
    resource_type: ResourceType
    amount: float
    priority: float  # 0.0 to 1.0
    deadline: Optional[datetime] = None
    min_acceptable: Optional[float] = None
    max_desired: Optional[float] = None
    duration: Optional[timedelta] = None
    constraints: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.constraints is None:
            self.constraints = {}
        if self.min_acceptable is None:
            self.min_acceptable = self.amount * 0.5
        if self.max_desired is None:
            self.max_desired = self.amount * 1.5


@dataclass
class Allocation:
    """Represents an active resource allocation."""
    id: str
    request_id: str
    task_id: str
    resource_type: ResourceType
    amount: float
    allocated_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ResourceAllocator:
    """
    Main resource allocation system.
    
    Manages resource allocation across multiple tasks and processes,
    using configurable strategies and optimization techniques.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the resource allocator.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path or str(Path.home() / "Lords Love" / "resource_allocation_config.json")
        self.config = self._load_config()
        
        # Resource pools
        self.resources: Dict[ResourceType, Resource] = {}
        self._initialize_resources()
        
        # Active allocations
        self.allocations: Dict[str, Allocation] = {}
        
        # Pending requests (priority queue)
        self.pending_requests: List[Tuple[float, AllocationRequest]] = []
        
        # Allocation history
        self.allocation_history: List[Dict] = []
        
        # Metrics
        self.metrics = {
            'total_requests': 0,
            'successful_allocations': 0,
            'failed_allocations': 0,
            'total_allocated': defaultdict(float),
            'peak_utilization': defaultdict(float)
        }
        
        # Strategy
        self.default_strategy = AllocationStrategy[self.config.get('default_strategy', 'PRIORITY_BASED')]
        
        self.logger.info("Resource Allocator initialized")
    
    def _load_config(self) -> Dict:
        """Load configuration from file or create default."""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load config: {e}")
        
        # Default configuration
        default_config = {
            'default_strategy': 'PRIORITY_BASED',
            'resources': {
                'cpu': {'capacity': 100.0, 'unit': 'percent'},
                'memory': {'capacity': 16384.0, 'unit': 'MB'},
                'time': {'capacity': 86400.0, 'unit': 'seconds'},
                'network': {'capacity': 1000.0, 'unit': 'Mbps'},
                'storage': {'capacity': 102400.0, 'unit': 'MB'}
            },
            'allocation_limits': {
                'max_per_task': 0.5,  # Max 50% of any resource per task
                'min_reserve': 0.1,   # Keep 10% in reserve
                'reallocation_threshold': 0.9  # Reallocate at 90% utilization
            },
            'optimization': {
                'enable_predictive': True,
                'enable_adaptive': True,
                'rebalance_interval_seconds': 60,
                'fairness_weight': 0.3,
                'efficiency_weight': 0.7
            }
        }
        
        # Save default config
        try:
            Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
        except Exception as e:
            self.logger.warning(f"Could not save default config: {e}")
        
        return default_config
    
    def _initialize_resources(self):
        """Initialize resource pools from configuration."""
        resource_configs = self.config.get('resources', {})
        
        for resource_name, config in resource_configs.items():
            try:
                resource_type = ResourceType[resource_name.upper()]
                capacity = config.get('capacity', 100.0)
                unit = config.get('unit', 'units')
                
                self.resources[resource_type] = Resource(
                    type=resource_type,
                    total_capacity=capacity,
                    available=capacity,
                    unit=unit
                )
                
                self.logger.info(f"Initialized {resource_type.value}: {capacity} {unit}")
            except KeyError:
                self.logger.warning(f"Unknown resource type: {resource_name}")
    
    def request_allocation(self, 
                          task_id: str,
                          resource_type: ResourceType,
                          amount: float,
                          priority: float = 0.5,
                          **kwargs) -> Optional[str]:
        """
        Request resource allocation.
        
        Args:
            task_id: ID of the task requesting resources
            resource_type: Type of resource needed
            amount: Amount of resource requested
            priority: Priority of request (0.0 to 1.0)
            **kwargs: Additional parameters (deadline, duration, etc.)
        
        Returns:
            Allocation ID if successful, None otherwise
        """
        self.metrics['total_requests'] += 1
        
        # Create request
        request = AllocationRequest(
            id=f"req_{datetime.now().timestamp()}_{task_id}",
            task_id=task_id,
            resource_type=resource_type,
            amount=amount,
            priority=priority,
            **kwargs
        )
        
        # Try immediate allocation
        allocation_id = self._try_allocate(request)
        
        if allocation_id:
            self.metrics['successful_allocations'] += 1
            return allocation_id
        
        # Queue for later
        heapq.heappush(self.pending_requests, (-priority, request))  # Negative for max heap
        self.logger.info(f"Queued request {request.id} for {task_id}")
        
        return None
    
    def _try_allocate(self, request: AllocationRequest) -> Optional[str]:
        """
        Attempt to allocate resources for a request.
        
        Args:
            request: Allocation request
        
        Returns:
            Allocation ID if successful, None otherwise
        """
        resource = self.resources.get(request.resource_type)
        
        if not resource:
            self.logger.error(f"Unknown resource type: {request.resource_type}")
            return None
        
        # Check allocation limits
        max_per_task = self.config.get('allocation_limits', {}).get('max_per_task', 0.5)
        max_allowed = resource.total_capacity * max_per_task
        
        if request.amount > max_allowed:
            self.logger.warning(f"Request exceeds max per task: {request.amount} > {max_allowed}")
            request.amount = max_allowed
        
        # Check reserve
        min_reserve = self.config.get('allocation_limits', {}).get('min_reserve', 0.1)
        reserve_amount = resource.total_capacity * min_reserve
        
        if resource.available - request.amount < reserve_amount:
            # Try to allocate minimum acceptable
            if request.min_acceptable and resource.available - request.min_acceptable >= reserve_amount:
                request.amount = request.min_acceptable
            else:
                return None
        
        # Allocate
        if resource.allocate(request.amount):
            allocation = Allocation(
                id=f"alloc_{datetime.now().timestamp()}_{request.task_id}",
                request_id=request.id,
                task_id=request.task_id,
                resource_type=request.resource_type,
                amount=request.amount,
                allocated_at=datetime.now(),
                expires_at=datetime.now() + request.duration if request.duration else None
            )
            
            self.allocations[allocation.id] = allocation
            
            # Update metrics
            self.metrics['total_allocated'][request.resource_type] += request.amount
            current_util = resource.utilization()
            if current_util > self.metrics['peak_utilization'][request.resource_type]:
                self.metrics['peak_utilization'][request.resource_type] = current_util
            
            # Record history
            self._record_allocation(allocation, request)
            
            self.logger.info(f"Allocated {request.amount} {resource.unit} of {request.resource_type.value} to {request.task_id}")
            
            return allocation.id
        
        return None
    
    def release_allocation(self, allocation_id: str) -> bool:
        """
        Release an active allocation.
        
        Args:
            allocation_id: ID of allocation to release
        
        Returns:
            True if successful, False otherwise
        """
        allocation = self.allocations.get(allocation_id)
        
        if not allocation:
            self.logger.warning(f"Allocation not found: {allocation_id}")
            return False
        
        resource = self.resources.get(allocation.resource_type)
        if resource:
            resource.release(allocation.amount)
            self.logger.info(f"Released {allocation.amount} {resource.unit} of {allocation.resource_type.value}")
        
        del self.allocations[allocation_id]
        
        # Try to process pending requests
        self._process_pending_requests()
        
        return True
    
    def _process_pending_requests(self):
        """Process pending allocation requests."""
        processed = []
        
        while self.pending_requests:
            priority, request = heapq.heappop(self.pending_requests)
            
            allocation_id = self._try_allocate(request)
            
            if allocation_id:
                self.metrics['successful_allocations'] += 1
            else:
                # Put back in queue
                processed.append((priority, request))
        
        # Restore unprocessed requests
        for item in processed:
            heapq.heappush(self.pending_requests, item)
    
    def reallocate_resources(self, strategy: Optional[AllocationStrategy] = None):
        """
        Reallocate resources using specified strategy.
        
        Args:
            strategy: Allocation strategy to use
        """
        strategy = strategy or self.default_strategy
        
        self.logger.info(f"Reallocating resources using {strategy.value} strategy")
        
        if strategy == AllocationStrategy.FAIR_SHARE:
            self._reallocate_fair_share()
        elif strategy == AllocationStrategy.PRIORITY_BASED:
            self._reallocate_priority_based()
        elif strategy == AllocationStrategy.ADAPTIVE:
            self._reallocate_adaptive()
        else:
            self.logger.warning(f"Reallocation not implemented for {strategy.value}")
    
    def _reallocate_fair_share(self):
        """Reallocate resources equally among active allocations."""
        for resource_type, resource in self.resources.items():
            # Get all allocations for this resource
            active = [a for a in self.allocations.values() if a.resource_type == resource_type]
            
            if not active:
                continue
            
            # Calculate fair share
            fair_share = resource.total_capacity / len(active)
            
            # Reallocate
            for allocation in active:
                if allocation.amount != fair_share:
                    # Release current
                    resource.release(allocation.amount)
                    # Allocate fair share
                    resource.allocate(fair_share)
                    allocation.amount = fair_share
    
    def _reallocate_priority_based(self):
        """Reallocate resources based on task priorities."""
        # Group allocations by resource type
        by_resource = defaultdict(list)
        for allocation in self.allocations.values():
            by_resource[allocation.resource_type].append(allocation)
        
        # Reallocate each resource type
        for resource_type, allocations in by_resource.items():
            resource = self.resources[resource_type]
            
            # Sort by priority (would need to track priorities)
            # For now, keep current allocations
            pass
    
    def _reallocate_adaptive(self):
        """Adaptively reallocate based on usage patterns."""
        # Analyze historical usage
        # Predict future needs
        # Reallocate proactively
        # This would integrate with the predictive models
        pass
    
    def get_resource_status(self) -> Dict[str, Any]:
        """Get current status of all resources."""
        status = {}
        
        for resource_type, resource in self.resources.items():
            status[resource_type.value] = {
                'total_capacity': resource.total_capacity,
                'available': resource.available,
                'allocated': resource.total_capacity - resource.available,
                'utilization': resource.utilization(),
                'unit': resource.unit,
                'active_allocations': len([a for a in self.allocations.values() if a.resource_type == resource_type])
            }
        
        return status
    
    def get_allocation_metrics(self) -> Dict[str, Any]:
        """Get allocation metrics and statistics."""
        return {
            'total_requests': self.metrics['total_requests'],
            'successful_allocations': self.metrics['successful_allocations'],
            'failed_allocations': self.metrics['failed_allocations'],
            'success_rate': self.metrics['successful_allocations'] / self.metrics['total_requests'] if self.metrics['total_requests'] > 0 else 0,
            'pending_requests': len(self.pending_requests),
            'active_allocations': len(self.allocations),
            'total_allocated': dict(self.metrics['total_allocated']),
            'peak_utilization': dict(self.metrics['peak_utilization'])
        }
    
    def optimize_allocations(self):
        """Optimize current allocations for better efficiency."""
        # Check for expired allocations
        now = datetime.now()
        expired = [aid for aid, alloc in self.allocations.items() 
                  if alloc.expires_at and alloc.expires_at < now]
        
        for aid in expired:
            self.release_allocation(aid)
        
        # Check if reallocation needed
        for resource_type, resource in self.resources.items():
            threshold = self.config.get('allocation_limits', {}).get('reallocation_threshold', 0.9)
            
            if resource.utilization() > threshold:
                self.logger.info(f"{resource_type.value} utilization high ({resource.utilization():.1%}), reallocating")
                self.reallocate_resources()
                break
    
    def _record_allocation(self, allocation: Allocation, request: AllocationRequest):
        """Record allocation in history."""
        record = {
            'timestamp': datetime.now().isoformat(),
            'allocation_id': allocation.id,
            'task_id': allocation.task_id,
            'resource_type': allocation.resource_type.value,
            'amount': allocation.amount,
            'priority': request.priority,
            'requested_amount': request.amount
        }
        
        self.allocation_history.append(record)
        
        # Keep history manageable
        if len(self.allocation_history) > 10000:
            self.allocation_history = self.allocation_history[-10000:]


class AllocationOptimizer:
    """
    Optimizes resource allocation decisions using various algorithms.
    """
    
    def __init__(self, allocator: ResourceAllocator):
        """
        Initialize the optimizer.
        
        Args:
            allocator: Resource allocator to optimize
        """
        self.allocator = allocator
        self.logger = logging.getLogger(__name__)
    
    def optimize_for_throughput(self) -> List[Dict]:
        """
        Optimize allocations to maximize throughput.
        
        Returns:
            List of optimization recommendations
        """
        recommendations = []
        
        # Analyze current allocations
        status = self.allocator.get_resource_status()
        
        for resource_type, info in status.items():
            if info['utilization'] < 0.5:
                recommendations.append({
                    'type': 'increase_allocation',
                    'resource': resource_type,
                    'reason': f"Low utilization ({info['utilization']:.1%})",
                    'suggestion': 'Allocate more tasks to this resource'
                })
            elif info['utilization'] > 0.9:
                recommendations.append({
                    'type': 'reduce_allocation',
                    'resource': resource_type,
                    'reason': f"High utilization ({info['utilization']:.1%})",
                    'suggestion': 'Consider adding capacity or reducing load'
                })
        
        return recommendations
    
    def optimize_for_fairness(self) -> Dict[str, float]:
        """
        Calculate fair share allocations.
        
        Returns:
            Dictionary mapping task IDs to fair share amounts
        """
        fair_shares = {}
        
        # Group by resource type
        by_resource = defaultdict(list)
        for allocation in self.allocator.allocations.values():
            by_resource[allocation.resource_type].append(allocation)
        
        # Calculate fair shares
        for resource_type, allocations in by_resource.items():
            resource = self.allocator.resources[resource_type]
            fair_share = resource.total_capacity / len(allocations) if allocations else 0
            
            for allocation in allocations:
                fair_shares[allocation.task_id] = fair_share
        
        return fair_shares
    
    def predict_resource_needs(self, task_id: str, horizon_hours: int = 24) -> Dict[ResourceType, float]:
        """
        Predict future resource needs for a task.
        
        Args:
            task_id: Task to predict for
            horizon_hours: Prediction horizon in hours
        
        Returns:
            Predicted resource needs by type
        """
        # Analyze historical usage
        task_history = [r for r in self.allocator.allocation_history 
                       if r.get('task_id') == task_id]
        
        predictions = {}
        
        if task_history:
            # Simple average-based prediction
            by_type = defaultdict(list)
            for record in task_history:
                resource_type = ResourceType(record['resource_type'])
                by_type[resource_type].append(record['amount'])
            
            for resource_type, amounts in by_type.items():
                predictions[resource_type] = np.mean(amounts) * 1.2  # 20% buffer
        
        return predictions


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Create allocator
    allocator = ResourceAllocator()
    
    # Request some allocations
    alloc1 = allocator.request_allocation(
        task_id="task_1",
        resource_type=ResourceType.CPU,
        amount=30.0,
        priority=0.8
    )
    
    alloc2 = allocator.request_allocation(
        task_id="task_2",
        resource_type=ResourceType.MEMORY,
        amount=4096.0,
        priority=0.6
    )
    
    # Get status
    status = allocator.get_resource_status()
    print("\nResource Status:")
    for resource, info in status.items():
        print(f"  {resource}: {info['utilization']:.1%} utilized")
    
    # Get metrics
    metrics = allocator.get_allocation_metrics()
    print(f"\nMetrics:")
    print(f"  Success rate: {metrics['success_rate']:.1%}")
    print(f"  Active allocations: {metrics['active_allocations']}")
    
    # Optimize
    optimizer = AllocationOptimizer(allocator)
    recommendations = optimizer.optimize_for_throughput()
    print(f"\nOptimization Recommendations: {len(recommendations)}")
    for rec in recommendations:
        print(f"  - {rec['type']}: {rec['suggestion']}")
