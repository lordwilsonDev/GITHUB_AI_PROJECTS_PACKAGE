#!/usr/bin/env python3
"""
Platform Orchestrator - New Build 6, Phase 3
Multi-platform coordination, resource optimization, and load balancing
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque
import hashlib


class PlatformType(Enum):
    """Types of platforms"""
    CLOUD = "cloud"
    EDGE = "edge"
    ON_PREMISE = "on_premise"
    HYBRID = "hybrid"
    SERVERLESS = "serverless"
    CONTAINER = "container"


class ResourceType(Enum):
    """Types of resources"""
    CPU = "cpu"
    MEMORY = "memory"
    GPU = "gpu"
    STORAGE = "storage"
    NETWORK = "network"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    WEIGHTED = "weighted"
    RANDOM = "random"
    CONSISTENT_HASH = "consistent_hash"


@dataclass
class Platform:
    """Represents a compute platform"""
    platform_id: str
    platform_type: PlatformType
    region: str
    resources: Dict[ResourceType, float] = field(default_factory=dict)
    capacity: Dict[ResourceType, float] = field(default_factory=dict)
    status: str = "active"  # active, inactive, maintenance
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'platform_id': self.platform_id,
            'platform_type': self.platform_type.value,
            'region': self.region,
            'resources': {k.value: v for k, v in self.resources.items()},
            'capacity': {k.value: v for k, v in self.capacity.items()},
            'status': self.status,
            'metadata': self.metadata
        }
    
    def get_utilization(self, resource_type: ResourceType) -> float:
        """Get resource utilization percentage"""
        if resource_type not in self.capacity or self.capacity[resource_type] == 0:
            return 0.0
        used = self.resources.get(resource_type, 0.0)
        return (used / self.capacity[resource_type]) * 100.0
    
    def has_capacity(self, required: Dict[ResourceType, float]) -> bool:
        """Check if platform has required capacity"""
        for resource_type, amount in required.items():
            available = self.capacity.get(resource_type, 0.0) - self.resources.get(resource_type, 0.0)
            if available < amount:
                return False
        return True
    
    def allocate(self, resources: Dict[ResourceType, float]) -> bool:
        """Allocate resources"""
        if not self.has_capacity(resources):
            return False
        
        for resource_type, amount in resources.items():
            current = self.resources.get(resource_type, 0.0)
            self.resources[resource_type] = current + amount
        return True
    
    def deallocate(self, resources: Dict[ResourceType, float]) -> bool:
        """Deallocate resources"""
        for resource_type, amount in resources.items():
            current = self.resources.get(resource_type, 0.0)
            self.resources[resource_type] = max(0.0, current - amount)
        return True


@dataclass
class WorkloadTask:
    """Represents a workload task"""
    task_id: str
    required_resources: Dict[ResourceType, float]
    priority: int = 1
    platform_preference: Optional[PlatformType] = None
    region_preference: Optional[str] = None
    status: str = "pending"  # pending, scheduled, running, completed, failed
    assigned_platform: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'task_id': self.task_id,
            'required_resources': {k.value: v for k, v in self.required_resources.items()},
            'priority': self.priority,
            'platform_preference': self.platform_preference.value if self.platform_preference else None,
            'region_preference': self.region_preference,
            'status': self.status,
            'assigned_platform': self.assigned_platform,
            'timestamp': self.timestamp
        }


class ResourceOptimizer:
    """Optimizes resource allocation across platforms"""
    
    def __init__(self):
        self.optimization_history: List[Dict[str, Any]] = []
        
    def optimize_placement(self, task: WorkloadTask, platforms: List[Platform]) -> Optional[Platform]:
        """Find optimal platform for task placement"""
        candidates = []
        
        for platform in platforms:
            if platform.status != "active":
                continue
            
            # Check platform preference
            if task.platform_preference and platform.platform_type != task.platform_preference:
                continue
            
            # Check region preference
            if task.region_preference and platform.region != task.region_preference:
                continue
            
            # Check capacity
            if not platform.has_capacity(task.required_resources):
                continue
            
            # Calculate score based on utilization
            total_utilization = sum(
                platform.get_utilization(rt) for rt in task.required_resources.keys()
            )
            avg_utilization = total_utilization / len(task.required_resources) if task.required_resources else 0
            
            # Prefer platforms with lower utilization
            score = 100.0 - avg_utilization
            
            candidates.append((platform, score))
        
        if not candidates:
            return None
        
        # Select platform with highest score
        best_platform = max(candidates, key=lambda x: x[1])[0]
        
        self.optimization_history.append({
            'task_id': task.task_id,
            'selected_platform': best_platform.platform_id,
            'candidates': len(candidates),
            'timestamp': time.time()
        })
        
        return best_platform
    
    def rebalance(self, platforms: List[Platform], tasks: List[WorkloadTask]) -> List[Tuple[str, str]]:
        """Rebalance tasks across platforms"""
        migrations = []
        
        # Find overloaded and underloaded platforms
        overloaded = [p for p in platforms if any(p.get_utilization(rt) > 80 for rt in ResourceType)]
        underloaded = [p for p in platforms if all(p.get_utilization(rt) < 50 for rt in ResourceType)]
        
        # Simulate migration recommendations
        for platform in overloaded:
            for task in tasks:
                if task.assigned_platform == platform.platform_id:
                    # Find better platform
                    for target in underloaded:
                        if target.has_capacity(task.required_resources):
                            migrations.append((task.task_id, target.platform_id))
                            break
        
        return migrations
    
    def get_stats(self) -> Dict[str, Any]:
        """Get optimization statistics"""
        return {
            'total_optimizations': len(self.optimization_history)
        }


class LoadBalancer:
    """Load balancer for distributing tasks across platforms"""
    
    def __init__(self, strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_LOADED):
        self.strategy = strategy
        self.round_robin_index = 0
        self.balancing_history: List[Dict[str, Any]] = []
        
    def select_platform(self, platforms: List[Platform], task: WorkloadTask) -> Optional[Platform]:
        """Select platform using load balancing strategy"""
        active_platforms = [p for p in platforms if p.status == "active" and p.has_capacity(task.required_resources)]
        
        if not active_platforms:
            return None
        
        if self.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            selected = self._round_robin(active_platforms)
        elif self.strategy == LoadBalancingStrategy.LEAST_LOADED:
            selected = self._least_loaded(active_platforms, task)
        elif self.strategy == LoadBalancingStrategy.WEIGHTED:
            selected = self._weighted(active_platforms)
        elif self.strategy == LoadBalancingStrategy.RANDOM:
            selected = self._random(active_platforms)
        else:
            selected = self._consistent_hash(active_platforms, task)
        
        self.balancing_history.append({
            'task_id': task.task_id,
            'selected_platform': selected.platform_id if selected else None,
            'strategy': self.strategy.value,
            'timestamp': time.time()
        })
        
        return selected
    
    def _round_robin(self, platforms: List[Platform]) -> Platform:
        """Round-robin selection"""
        selected = platforms[self.round_robin_index % len(platforms)]
        self.round_robin_index += 1
        return selected
    
    def _least_loaded(self, platforms: List[Platform], task: WorkloadTask) -> Platform:
        """Select least loaded platform"""
        def get_load(platform: Platform) -> float:
            total_util = sum(
                platform.get_utilization(rt) for rt in task.required_resources.keys()
            )
            return total_util / len(task.required_resources) if task.required_resources else 0
        
        return min(platforms, key=get_load)
    
    def _weighted(self, platforms: List[Platform]) -> Platform:
        """Weighted selection based on capacity"""
        # Simple implementation: select platform with most total capacity
        def get_total_capacity(platform: Platform) -> float:
            return sum(platform.capacity.values())
        
        return max(platforms, key=get_total_capacity)
    
    def _random(self, platforms: List[Platform]) -> Platform:
        """Random selection"""
        import random
        return random.choice(platforms)
    
    def _consistent_hash(self, platforms: List[Platform], task: WorkloadTask) -> Platform:
        """Consistent hashing"""
        # Simple hash-based selection
        task_hash = int(hashlib.md5(task.task_id.encode()).hexdigest(), 16)
        index = task_hash % len(platforms)
        return platforms[index]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get load balancing statistics"""
        return {
            'strategy': self.strategy.value,
            'total_balancing_decisions': len(self.balancing_history)
        }


class PlatformOrchestrator:
    """Main platform orchestration system"""
    
    def __init__(self, balancing_strategy: LoadBalancingStrategy = LoadBalancingStrategy.LEAST_LOADED):
        self.platforms: Dict[str, Platform] = {}
        self.tasks: Dict[str, WorkloadTask] = {}
        self.optimizer = ResourceOptimizer()
        self.load_balancer = LoadBalancer(balancing_strategy)
        self.lock = threading.Lock()
        
    def register_platform(self, platform: Platform) -> bool:
        """Register a platform"""
        with self.lock:
            self.platforms[platform.platform_id] = platform
            return True
    
    def unregister_platform(self, platform_id: str) -> bool:
        """Unregister a platform"""
        with self.lock:
            if platform_id in self.platforms:
                del self.platforms[platform_id]
                return True
            return False
    
    def submit_task(self, task: WorkloadTask) -> bool:
        """Submit a task for scheduling"""
        with self.lock:
            self.tasks[task.task_id] = task
        
        # Schedule task
        return self.schedule_task(task.task_id)
    
    def schedule_task(self, task_id: str) -> bool:
        """Schedule a task to a platform"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            platforms_list = list(self.platforms.values())
        
        # Use optimizer to find best platform
        platform = self.optimizer.optimize_placement(task, platforms_list)
        
        if not platform:
            # Fallback to load balancer
            platform = self.load_balancer.select_platform(platforms_list, task)
        
        if not platform:
            return False
        
        # Allocate resources
        with self.lock:
            if platform.allocate(task.required_resources):
                task.status = "scheduled"
                task.assigned_platform = platform.platform_id
                return True
        
        return False
    
    def complete_task(self, task_id: str) -> bool:
        """Mark task as complete and deallocate resources"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            
            if task.assigned_platform and task.assigned_platform in self.platforms:
                platform = self.platforms[task.assigned_platform]
                platform.deallocate(task.required_resources)
                task.status = "completed"
                return True
        
        return False
    
    def rebalance_workloads(self) -> List[Tuple[str, str]]:
        """Rebalance workloads across platforms"""
        with self.lock:
            platforms_list = list(self.platforms.values())
            tasks_list = [t for t in self.tasks.values() if t.status == "scheduled"]
        
        return self.optimizer.rebalance(platforms_list, tasks_list)
    
    def get_platform_stats(self, platform_id: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific platform"""
        with self.lock:
            if platform_id not in self.platforms:
                return None
            
            platform = self.platforms[platform_id]
            
            # Count tasks on this platform
            task_count = sum(1 for t in self.tasks.values() if t.assigned_platform == platform_id)
            
            return {
                'platform_id': platform_id,
                'platform_type': platform.platform_type.value,
                'status': platform.status,
                'tasks': task_count,
                'utilization': {
                    rt.value: platform.get_utilization(rt)
                    for rt in platform.capacity.keys()
                }
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics"""
        with self.lock:
            platform_stats = {
                pid: self.get_platform_stats(pid)
                for pid in self.platforms.keys()
            }
            
            task_status_counts = defaultdict(int)
            for task in self.tasks.values():
                task_status_counts[task.status] += 1
            
            return {
                'total_platforms': len(self.platforms),
                'total_tasks': len(self.tasks),
                'task_status': dict(task_status_counts),
                'optimizer': self.optimizer.get_stats(),
                'load_balancer': self.load_balancer.get_stats(),
                'platforms': platform_stats
            }
    
    def demo(self) -> Dict[str, Any]:
        """Demonstrate platform orchestration capabilities"""
        print("\n=== Platform Orchestrator Demo ===")
        
        # 1. Register platforms
        print("\n1. Registering platforms...")
        cloud_platform = Platform(
            platform_id="cloud_1",
            platform_type=PlatformType.CLOUD,
            region="us-east-1",
            capacity={
                ResourceType.CPU: 100.0,
                ResourceType.MEMORY: 256.0,
                ResourceType.GPU: 8.0
            }
        )
        self.register_platform(cloud_platform)
        
        edge_platform = Platform(
            platform_id="edge_1",
            platform_type=PlatformType.EDGE,
            region="us-west-1",
            capacity={
                ResourceType.CPU: 50.0,
                ResourceType.MEMORY: 128.0,
                ResourceType.GPU: 4.0
            }
        )
        self.register_platform(edge_platform)
        
        container_platform = Platform(
            platform_id="container_1",
            platform_type=PlatformType.CONTAINER,
            region="us-east-1",
            capacity={
                ResourceType.CPU: 75.0,
                ResourceType.MEMORY: 192.0,
                ResourceType.GPU: 0.0
            }
        )
        self.register_platform(container_platform)
        
        print(f"   Registered 3 platforms")
        
        # 2. Submit tasks
        print("\n2. Submitting tasks...")
        task1 = WorkloadTask(
            task_id="task_1",
            required_resources={
                ResourceType.CPU: 10.0,
                ResourceType.MEMORY: 32.0,
                ResourceType.GPU: 1.0
            },
            priority=5
        )
        self.submit_task(task1)
        
        task2 = WorkloadTask(
            task_id="task_2",
            required_resources={
                ResourceType.CPU: 20.0,
                ResourceType.MEMORY: 64.0
            },
            priority=3,
            platform_preference=PlatformType.EDGE
        )
        self.submit_task(task2)
        
        task3 = WorkloadTask(
            task_id="task_3",
            required_resources={
                ResourceType.CPU: 15.0,
                ResourceType.MEMORY: 48.0
            },
            priority=7
        )
        self.submit_task(task3)
        
        print(f"   Submitted 3 tasks")
        
        # 3. Check platform utilization
        print("\n3. Platform utilization:")
        for platform_id in self.platforms.keys():
            stats = self.get_platform_stats(platform_id)
            print(f"   {platform_id}: {stats['tasks']} tasks")
            for resource, util in stats['utilization'].items():
                print(f"      {resource}: {util:.1f}%")
        
        # 4. Complete a task
        print("\n4. Completing task_1...")
        self.complete_task("task_1")
        print(f"   Task completed and resources deallocated")
        
        # 5. Rebalance workloads
        print("\n5. Checking for rebalancing opportunities...")
        migrations = self.rebalance_workloads()
        print(f"   Recommended migrations: {len(migrations)}")
        
        # 6. Get statistics
        print("\n6. System statistics:")
        stats = self.get_stats()
        print(f"   Total platforms: {stats['total_platforms']}")
        print(f"   Total tasks: {stats['total_tasks']}")
        print(f"   Task status: {stats['task_status']}")
        print(f"   Load balancing strategy: {stats['load_balancer']['strategy']}")
        
        print("\n=== Demo Complete ===")
        return stats


class PlatformOrchestratorContract:
    """Contract interface for testing"""
    
    @staticmethod
    def create() -> PlatformOrchestrator:
        """Create a platform orchestrator instance"""
        return PlatformOrchestrator()
    
    @staticmethod
    def verify() -> bool:
        """Verify platform orchestrator functionality"""
        po = PlatformOrchestrator()
        
        # Test platform registration
        platform = Platform(
            platform_id="test_platform",
            platform_type=PlatformType.CLOUD,
            region="test-region",
            capacity={ResourceType.CPU: 100.0, ResourceType.MEMORY: 256.0}
        )
        if not po.register_platform(platform):
            return False
        
        # Test task submission
        task = WorkloadTask(
            task_id="test_task",
            required_resources={ResourceType.CPU: 10.0, ResourceType.MEMORY: 32.0}
        )
        if not po.submit_task(task):
            return False
        
        # Test task completion
        if not po.complete_task("test_task"):
            return False
        
        # Test statistics
        stats = po.get_stats()
        if stats['total_platforms'] != 1:
            return False
        if stats['total_tasks'] != 1:
            return False
        
        return True


if __name__ == "__main__":
    # Run demo
    po = PlatformOrchestrator()
    po.demo()
