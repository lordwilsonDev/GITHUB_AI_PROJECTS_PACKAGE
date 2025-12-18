#!/usr/bin/env python3
"""
Distributed Execution Support for MoIE-OS Enterprise
Enables network-based agent coordination and remote task execution
"""

import json
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum
import uuid

class NodeStatus(Enum):
    ONLINE = 'online'
    OFFLINE = 'offline'
    BUSY = 'busy'

@dataclass
class RemoteNode:
    """Represents a remote execution node"""
    node_id: str
    host: str
    port: int
    status: NodeStatus
    capabilities: List[str]
    last_heartbeat: float
    active_tasks: int = 0
    
class DistributedCoordinator:
    """Coordinates distributed task execution across network nodes"""
    
    def __init__(self, host: str = 'localhost', port: int = 5555):
        self.host = host
        self.port = port
        self.node_id = str(uuid.uuid4())
        self.nodes: Dict[str, RemoteNode] = {}
        self.running = False
        self.heartbeat_thread = None
        
    def start(self):
        """Start the distributed coordinator"""
        print(f"\n🌐 Starting Distributed Coordinator")
        print(f"   Node ID: {self.node_id}")
        print(f"   Listening on: {self.host}:{self.port}")
        
        self.running = True
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_monitor, daemon=True)
        self.heartbeat_thread.start()
        
        print("✅ Distributed Coordinator started")
        
    def register_node(self, host: str, port: int, capabilities: List[str]) -> str:
        """Register a remote execution node"""
        node_id = str(uuid.uuid4())
        
        node = RemoteNode(
            node_id=node_id,
            host=host,
            port=port,
            status=NodeStatus.ONLINE,
            capabilities=capabilities,
            last_heartbeat=time.time()
        )
        
        self.nodes[node_id] = node
        print(f"✅ Registered node {node_id[:8]}... at {host}:{port}")
        print(f"   Capabilities: {', '.join(capabilities)}")
        
        return node_id
    
    def find_capable_node(self, required_capability: str) -> Optional[RemoteNode]:
        """Find an available node with the required capability"""
        available_nodes = [
            node for node in self.nodes.values()
            if node.status == NodeStatus.ONLINE
            and required_capability in node.capabilities
        ]
        
        if not available_nodes:
            return None
        
        return min(available_nodes, key=lambda n: n.active_tasks)
    
    def distribute_task(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Distribute a task to an appropriate remote node"""
        node = self.find_capable_node(task_type)
        
        if not node:
            return {
                'success': False,
                'error': f'No available node with capability: {task_type}',
                'fallback': 'local'
            }
        
        task_id = str(uuid.uuid4())
        
        print(f"📤 Distributing task {task_id[:8]}... to node {node.node_id[:8]}...")
        print(f"   Type: {task_type}")
        
        node.active_tasks += 1
        node.status = NodeStatus.BUSY
        
        result = self._execute_remote_task(node, task_type, task_data)
        
        node.active_tasks -= 1
        if node.active_tasks == 0:
            node.status = NodeStatus.ONLINE
        
        return result
    
    def _execute_remote_task(self, node: RemoteNode, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task on remote node (simulated for now)"""
        time.sleep(0.1)  # Simulate network latency
        
        return {
            'success': True,
            'task_type': task_type,
            'node_id': node.node_id,
            'result': f'Task executed remotely on {node.host}:{node.port}',
            'execution_time': 0.1
        }
    
    def _heartbeat_monitor(self):
        """Monitor node heartbeats"""
        while self.running:
            time.sleep(5)
            current_time = time.time()
            timeout = 30
            
            for node in self.nodes.values():
                if current_time - node.last_heartbeat > timeout:
                    if node.status != NodeStatus.OFFLINE:
                        print(f"⚠️  Node {node.node_id[:8]}... marked offline")
                        node.status = NodeStatus.OFFLINE
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get status of the distributed cluster"""
        return {
            'coordinator_id': self.node_id,
            'total_nodes': len(self.nodes),
            'online_nodes': sum(1 for n in self.nodes.values() if n.status == NodeStatus.ONLINE),
            'busy_nodes': sum(1 for n in self.nodes.values() if n.status == NodeStatus.BUSY),
            'offline_nodes': sum(1 for n in self.nodes.values() if n.status == NodeStatus.OFFLINE),
            'total_active_tasks': sum(n.active_tasks for n in self.nodes.values()),
            'nodes': [
                {
                    'id': node.node_id[:8] + '...',
                    'host': node.host,
                    'port': node.port,
                    'status': node.status.value,
                    'capabilities': node.capabilities,
                    'active_tasks': node.active_tasks
                }
                for node in self.nodes.values()
            ]
        }
    
    def shutdown(self):
        """Shutdown the coordinator"""
        print("\n🛑 Shutting down Distributed Coordinator...")
        self.running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=2)
        print("✅ Shutdown complete")


if __name__ == '__main__':
    print("="*60)
    print("MoIE-OS Distributed Execution Demo")
    print("="*60)
    
    coordinator = DistributedCoordinator()
    coordinator.start()
    
    # Register worker nodes
    print("\n📋 Registering worker nodes...")
    node1 = coordinator.register_node('worker1.local', 5001, ['compute', 'ml_inference'])
    node2 = coordinator.register_node('worker2.local', 5002, ['compute', 'data_processing'])
    node3 = coordinator.register_node('worker3.local', 5003, ['ml_inference', 'data_processing'])
    
    # Show cluster status
    print("\n📊 Cluster Status:")
    status = coordinator.get_cluster_status()
    print(f"   Total Nodes: {status['total_nodes']}")
    print(f"   Online: {status['online_nodes']}")
    
    # Execute distributed tasks
    print("\n🚀 Executing distributed tasks...")
    tasks = [
        {'type': 'compute', 'data': 'task1'},
        {'type': 'ml_inference', 'data': 'task2'},
        {'type': 'data_processing', 'data': 'task3'},
    ]
    
    results = []
    for task in tasks:
        result = coordinator.distribute_task(task['type'], task)
        results.append(result)
    
    print("\n✅ Results:")
    for i, result in enumerate(results, 1):
        if result.get('success'):
            print(f"   Task {i}: SUCCESS")
    
    coordinator.shutdown()
    print("\n✅ Demo Complete!")
