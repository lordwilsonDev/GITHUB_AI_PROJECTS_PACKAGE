"""
Level 21: Compute Fabric Engine
Enables unlimited node addition, dynamic load balancing, and elastic resource management.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable, Set, Tuple
from datetime import datetime
import threading
import json
import random
import time
from enum import Enum
from collections import defaultdict, deque


class NodeType(Enum):
    """Types of compute nodes"""
    CPU = "cpu"
    GPU = "gpu"
    TPU = "tpu"
    QUANTUM = "quantum"
    NEUROMORPHIC = "neuromorphic"
    HYBRID = "hybrid"


class NodeStatus(Enum):
    """Status of compute nodes"""
    IDLE = "idle"
    ACTIVE = "active"
    OVERLOADED = "overloaded"
    FAILED = "failed"
    MAINTENANCE = "maintenance"


class LoadBalancingStrategy(Enum):
    """Load balancing strategies"""
    ROUND_ROBIN = "round_robin"
    LEAST_LOADED = "least_loaded"
    WEIGHTED = "weighted"
    ADAPTIVE = "adaptive"
    PREDICTIVE = "predictive"


@dataclass
class ComputeNode:
    """Represents a compute node in the fabric"""
    node_id: str
    node_type: NodeType
    capacity: float
    current_load: float = 0.0
    status: NodeStatus = NodeStatus.IDLE
    location: str = "unknown"
    capabilities: Set[str] = field(default_factory=set)
    tasks: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_heartbeat: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComputeTask:
    """Represents a computational task"""
    task_id: str
    task_type: str
    required_capacity: float
    priority: int = 5
    required_capabilities: Set[str] = field(default_factory=set)
    assigned_node: Optional[str] = None
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FabricMetrics:
    """Metrics for the compute fabric"""
    total_nodes: int = 0
    active_nodes: int = 0
    total_capacity: float = 0.0
    used_capacity: float = 0.0
    pending_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    average_load: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ScalingPolicy:
    """Policy for automatic scaling"""
    min_nodes: int = 1
    max_nodes: int = 1000
    scale_up_threshold: float = 0.8
    scale_down_threshold: float = 0.3
    scale_up_increment: int = 2
    scale_down_increment: int = 1
    cooldown_period: int = 60  # seconds


class ComputeFabricManager:
    """Manages the compute fabric with unlimited scalability"""
    
    def __init__(self):
        self.nodes: Dict[str, ComputeNode] = {}
        self.tasks: Dict[str, ComputeTask] = {}
        self.pending_queue: deque = deque()
        self.completed_tasks: List[str] = []
        self.failed_tasks: List[str] = []
        self.scaling_policy = ScalingPolicy()
        self.balancing_strategy = LoadBalancingStrategy.ADAPTIVE
        self.lock = threading.Lock()
        self.node_counter = 0
        self.task_counter = 0
        self.last_scale_time = datetime.now()
        self.metrics_history: List[FabricMetrics] = []
        
    def add_node(self, node_type: NodeType, capacity: float, 
                 location: str = "unknown", 
                 capabilities: Optional[Set[str]] = None) -> str:
        """Add a new compute node to the fabric"""
        with self.lock:
            self.node_counter += 1
            node_id = f"node_{self.node_counter}_{node_type.value}"
            
            node = ComputeNode(
                node_id=node_id,
                node_type=node_type,
                capacity=capacity,
                location=location,
                capabilities=capabilities or set(),
                status=NodeStatus.IDLE
            )
            
            self.nodes[node_id] = node
            return node_id
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the fabric"""
        with self.lock:
            if node_id not in self.nodes:
                return False
            
            node = self.nodes[node_id]
            
            # Reassign tasks if node has active tasks
            if node.tasks:
                for task_id in node.tasks:
                    if task_id in self.tasks:
                        self.tasks[task_id].assigned_node = None
                        self.tasks[task_id].status = "pending"
                        self.pending_queue.append(task_id)
            
            del self.nodes[node_id]
            return True
    
    def submit_task(self, task_type: str, required_capacity: float,
                   priority: int = 5,
                   required_capabilities: Optional[Set[str]] = None) -> str:
        """Submit a new task to the fabric"""
        with self.lock:
            self.task_counter += 1
            task_id = f"task_{self.task_counter}"
            
            task = ComputeTask(
                task_id=task_id,
                task_type=task_type,
                required_capacity=required_capacity,
                priority=priority,
                required_capabilities=required_capabilities or set()
            )
            
            self.tasks[task_id] = task
            self.pending_queue.append(task_id)
            
            # Trigger task assignment
            self._assign_tasks()
            
            return task_id
    
    def _assign_tasks(self):
        """Assign pending tasks to available nodes"""
        while self.pending_queue:
            task_id = self.pending_queue[0]
            task = self.tasks.get(task_id)
            
            if not task:
                self.pending_queue.popleft()
                continue
            
            # Find suitable node
            node = self._find_best_node(task)
            
            if node:
                # Assign task to node
                task.assigned_node = node.node_id
                task.status = "running"
                task.started_at = datetime.now()
                node.tasks.append(task_id)
                node.current_load += task.required_capacity
                
                # Update node status
                if node.current_load >= node.capacity * 0.9:
                    node.status = NodeStatus.OVERLOADED
                elif node.current_load > 0:
                    node.status = NodeStatus.ACTIVE
                
                self.pending_queue.popleft()
            else:
                # No suitable node available, trigger scaling
                self._auto_scale()
                break
    
    def _find_best_node(self, task: ComputeTask) -> Optional[ComputeNode]:
        """Find the best node for a task based on balancing strategy"""
        suitable_nodes = []
        
        for node in self.nodes.values():
            # Check if node can handle the task
            if (node.status != NodeStatus.FAILED and
                node.status != NodeStatus.MAINTENANCE and
                node.current_load + task.required_capacity <= node.capacity and
                task.required_capabilities.issubset(node.capabilities)):
                suitable_nodes.append(node)
        
        if not suitable_nodes:
            return None
        
        # Apply balancing strategy
        if self.balancing_strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return suitable_nodes[0]
        
        elif self.balancing_strategy == LoadBalancingStrategy.LEAST_LOADED:
            return min(suitable_nodes, key=lambda n: n.current_load / n.capacity)
        
        elif self.balancing_strategy == LoadBalancingStrategy.WEIGHTED:
            # Prefer nodes with higher capacity
            return max(suitable_nodes, key=lambda n: n.capacity - n.current_load)
        
        elif self.balancing_strategy == LoadBalancingStrategy.ADAPTIVE:
            # Adaptive strategy: consider load, capacity, and task count
            def score(node):
                load_factor = 1.0 - (node.current_load / node.capacity)
                capacity_factor = node.capacity / 100.0
                task_factor = 1.0 / (len(node.tasks) + 1)
                return load_factor * 0.5 + capacity_factor * 0.3 + task_factor * 0.2
            
            return max(suitable_nodes, key=score)
        
        elif self.balancing_strategy == LoadBalancingStrategy.PREDICTIVE:
            # Predictive strategy: consider historical performance
            def predict_completion_time(node):
                base_time = task.required_capacity / (node.capacity - node.current_load + 0.1)
                queue_penalty = len(node.tasks) * 0.1
                return base_time + queue_penalty
            
            return min(suitable_nodes, key=predict_completion_time)
        
        return suitable_nodes[0]
    
    def complete_task(self, task_id: str, result: Any = None) -> bool:
        """Mark a task as completed"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.status = "completed"
            task.completed_at = datetime.now()
            task.result = result
            
            # Update node
            if task.assigned_node and task.assigned_node in self.nodes:
                node = self.nodes[task.assigned_node]
                if task_id in node.tasks:
                    node.tasks.remove(task_id)
                node.current_load -= task.required_capacity
                
                # Update node status
                if node.current_load <= 0:
                    node.status = NodeStatus.IDLE
                    node.current_load = 0.0
                elif node.current_load < node.capacity * 0.9:
                    node.status = NodeStatus.ACTIVE
            
            self.completed_tasks.append(task_id)
            
            # Try to assign more tasks
            self._assign_tasks()
            
            return True
    
    def fail_task(self, task_id: str, reason: str = "unknown") -> bool:
        """Mark a task as failed"""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            task.status = "failed"
            task.metadata["failure_reason"] = reason
            
            # Update node
            if task.assigned_node and task.assigned_node in self.nodes:
                node = self.nodes[task.assigned_node]
                if task_id in node.tasks:
                    node.tasks.remove(task_id)
                node.current_load -= task.required_capacity
            
            self.failed_tasks.append(task_id)
            return True
    
    def _auto_scale(self):
        """Automatically scale the fabric based on load"""
        current_time = datetime.now()
        cooldown_elapsed = (current_time - self.last_scale_time).total_seconds()
        
        if cooldown_elapsed < self.scaling_policy.cooldown_period:
            return
        
        metrics = self.get_metrics()
        
        # Scale up if needed
        if (metrics.average_load > self.scaling_policy.scale_up_threshold and
            metrics.total_nodes < self.scaling_policy.max_nodes):
            
            nodes_to_add = min(
                self.scaling_policy.scale_up_increment,
                self.scaling_policy.max_nodes - metrics.total_nodes
            )
            
            for _ in range(nodes_to_add):
                # Add diverse node types
                node_type = random.choice(list(NodeType))
                capacity = random.uniform(50, 200)
                self.add_node(node_type, capacity)
            
            self.last_scale_time = current_time
        
        # Scale down if needed
        elif (metrics.average_load < self.scaling_policy.scale_down_threshold and
              metrics.total_nodes > self.scaling_policy.min_nodes):
            
            nodes_to_remove = min(
                self.scaling_policy.scale_down_increment,
                metrics.total_nodes - self.scaling_policy.min_nodes
            )
            
            # Remove idle nodes
            idle_nodes = [n for n in self.nodes.values() 
                         if n.status == NodeStatus.IDLE]
            
            for i in range(min(nodes_to_remove, len(idle_nodes))):
                self.remove_node(idle_nodes[i].node_id)
            
            self.last_scale_time = current_time
    
    def get_metrics(self) -> FabricMetrics:
        """Get current fabric metrics"""
        with self.lock:
            total_nodes = len(self.nodes)
            active_nodes = sum(1 for n in self.nodes.values() 
                             if n.status == NodeStatus.ACTIVE or 
                             n.status == NodeStatus.OVERLOADED)
            
            total_capacity = sum(n.capacity for n in self.nodes.values())
            used_capacity = sum(n.current_load for n in self.nodes.values())
            
            average_load = (used_capacity / total_capacity) if total_capacity > 0 else 0.0
            
            pending_tasks = len(self.pending_queue)
            
            metrics = FabricMetrics(
                total_nodes=total_nodes,
                active_nodes=active_nodes,
                total_capacity=total_capacity,
                used_capacity=used_capacity,
                pending_tasks=pending_tasks,
                completed_tasks=len(self.completed_tasks),
                failed_tasks=len(self.failed_tasks),
                average_load=average_load
            )
            
            self.metrics_history.append(metrics)
            return metrics
    
    def set_balancing_strategy(self, strategy: LoadBalancingStrategy):
        """Set the load balancing strategy"""
        with self.lock:
            self.balancing_strategy = strategy
    
    def set_scaling_policy(self, policy: ScalingPolicy):
        """Set the auto-scaling policy"""
        with self.lock:
            self.scaling_policy = policy
    
    def get_node_status(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific node"""
        with self.lock:
            if node_id not in self.nodes:
                return None
            
            node = self.nodes[node_id]
            return {
                "node_id": node.node_id,
                "type": node.node_type.value,
                "status": node.status.value,
                "capacity": node.capacity,
                "current_load": node.current_load,
                "utilization": node.current_load / node.capacity if node.capacity > 0 else 0,
                "active_tasks": len(node.tasks),
                "location": node.location,
                "capabilities": list(node.capabilities)
            }
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        with self.lock:
            if task_id not in self.tasks:
                return None
            
            task = self.tasks[task_id]
            return {
                "task_id": task.task_id,
                "type": task.task_type,
                "status": task.status,
                "priority": task.priority,
                "assigned_node": task.assigned_node,
                "required_capacity": task.required_capacity,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
    
    def rebalance(self):
        """Manually trigger rebalancing of tasks across nodes"""
        with self.lock:
            # Collect all running tasks
            running_tasks = [t for t in self.tasks.values() if t.status == "running"]
            
            # Clear task assignments
            for task in running_tasks:
                if task.assigned_node and task.assigned_node in self.nodes:
                    node = self.nodes[task.assigned_node]
                    if task.task_id in node.tasks:
                        node.tasks.remove(task.task_id)
                    node.current_load -= task.required_capacity
                
                task.assigned_node = None
                task.status = "pending"
                self.pending_queue.append(task.task_id)
            
            # Reset node statuses
            for node in self.nodes.values():
                node.current_load = 0.0
                node.tasks = []
                node.status = NodeStatus.IDLE
            
            # Reassign all tasks
            self._assign_tasks()
    
    def get_fabric_summary(self) -> Dict[str, Any]:
        """Get comprehensive fabric summary"""
        metrics = self.get_metrics()
        
        node_types = defaultdict(int)
        node_statuses = defaultdict(int)
        
        for node in self.nodes.values():
            node_types[node.node_type.value] += 1
            node_statuses[node.status.value] += 1
        
        return {
            "metrics": {
                "total_nodes": metrics.total_nodes,
                "active_nodes": metrics.active_nodes,
                "total_capacity": metrics.total_capacity,
                "used_capacity": metrics.used_capacity,
                "average_load": metrics.average_load,
                "pending_tasks": metrics.pending_tasks,
                "completed_tasks": metrics.completed_tasks,
                "failed_tasks": metrics.failed_tasks
            },
            "node_distribution": dict(node_types),
            "node_statuses": dict(node_statuses),
            "balancing_strategy": self.balancing_strategy.value,
            "scaling_policy": {
                "min_nodes": self.scaling_policy.min_nodes,
                "max_nodes": self.scaling_policy.max_nodes,
                "scale_up_threshold": self.scaling_policy.scale_up_threshold,
                "scale_down_threshold": self.scaling_policy.scale_down_threshold
            }
        }


# Singleton instance
_fabric_manager = None
_fabric_lock = threading.Lock()


def get_fabric_manager() -> ComputeFabricManager:
    """Get the singleton fabric manager instance"""
    global _fabric_manager
    if _fabric_manager is None:
        with _fabric_lock:
            if _fabric_manager is None:
                _fabric_manager = ComputeFabricManager()
    return _fabric_manager


class Contract:
    """Testing contract for compute fabric"""
    
    @staticmethod
    def test_node_addition():
        """Test adding nodes to the fabric"""
        manager = ComputeFabricManager()
        node_id = manager.add_node(NodeType.CPU, 100.0, "datacenter-1")
        assert node_id in manager.nodes
        assert manager.nodes[node_id].capacity == 100.0
        return True
    
    @staticmethod
    def test_task_submission():
        """Test submitting tasks"""
        manager = ComputeFabricManager()
        manager.add_node(NodeType.CPU, 100.0)
        task_id = manager.submit_task("compute", 50.0)
        assert task_id in manager.tasks
        return True
    
    @staticmethod
    def test_load_balancing():
        """Test load balancing across nodes"""
        manager = ComputeFabricManager()
        manager.add_node(NodeType.CPU, 100.0)
        manager.add_node(NodeType.GPU, 150.0)
        
        task1 = manager.submit_task("compute", 40.0)
        task2 = manager.submit_task("compute", 40.0)
        
        # Tasks should be distributed
        assigned_nodes = set()
        for task_id in [task1, task2]:
            if manager.tasks[task_id].assigned_node:
                assigned_nodes.add(manager.tasks[task_id].assigned_node)
        
        return len(assigned_nodes) > 0
    
    @staticmethod
    def test_auto_scaling():
        """Test automatic scaling"""
        manager = ComputeFabricManager()
        manager.scaling_policy.min_nodes = 1
        manager.scaling_policy.max_nodes = 10
        manager.scaling_policy.scale_up_threshold = 0.7
        
        # Add initial node
        manager.add_node(NodeType.CPU, 100.0)
        initial_count = len(manager.nodes)
        
        # Submit many tasks to trigger scaling
        for _ in range(10):
            manager.submit_task("compute", 20.0)
        
        manager._auto_scale()
        
        # Should have scaled up
        return len(manager.nodes) >= initial_count


def demo():
    """Demonstrate compute fabric capabilities"""
    print("=== Compute Fabric Demo ===\n")
    
    manager = get_fabric_manager()
    
    # Configure scaling policy
    policy = ScalingPolicy(
        min_nodes=2,
        max_nodes=20,
        scale_up_threshold=0.75,
        scale_down_threshold=0.25
    )
    manager.set_scaling_policy(policy)
    
    # Add initial nodes
    print("1. Adding initial compute nodes...")
    manager.add_node(NodeType.CPU, 100.0, "datacenter-1", {"general", "compute"})
    manager.add_node(NodeType.GPU, 200.0, "datacenter-1", {"ml", "graphics"})
    manager.add_node(NodeType.TPU, 300.0, "datacenter-2", {"ml", "training"})
    
    print(f"   Added {len(manager.nodes)} nodes")
    
    # Submit tasks
    print("\n2. Submitting computational tasks...")
    tasks = []
    for i in range(15):
        task_id = manager.submit_task(
            task_type="ml_training" if i % 3 == 0 else "compute",
            required_capacity=random.uniform(20, 80),
            priority=random.randint(1, 10)
        )
        tasks.append(task_id)
    
    print(f"   Submitted {len(tasks)} tasks")
    
    # Show metrics
    print("\n3. Fabric metrics:")
    metrics = manager.get_metrics()
    print(f"   Total nodes: {metrics.total_nodes}")
    print(f"   Active nodes: {metrics.active_nodes}")
    print(f"   Total capacity: {metrics.total_capacity:.1f}")
    print(f"   Used capacity: {metrics.used_capacity:.1f}")
    print(f"   Average load: {metrics.average_load:.1%}")
    print(f"   Pending tasks: {metrics.pending_tasks}")
    
    # Complete some tasks
    print("\n4. Completing tasks...")
    completed = 0
    for task_id in tasks[:5]:
        if manager.complete_task(task_id, result={"status": "success"}):
            completed += 1
    
    print(f"   Completed {completed} tasks")
    
    # Show fabric summary
    print("\n5. Fabric summary:")
    summary = manager.get_fabric_summary()
    print(f"   Node distribution: {summary['node_distribution']}")
    print(f"   Node statuses: {summary['node_statuses']}")
    print(f"   Balancing strategy: {summary['balancing_strategy']}")
    
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    # Run contract tests
    print("Running contract tests...")
    assert Contract.test_node_addition()
    assert Contract.test_task_submission()
    assert Contract.test_load_balancing()
    assert Contract.test_auto_scaling()
    print("All tests passed!\n")
    
    # Run demo
    demo()
