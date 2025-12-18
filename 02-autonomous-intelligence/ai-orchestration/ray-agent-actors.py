"""Ray Actor Model for Stateful AI Agents

Demonstrates:
- Stateful actors maintaining memory across calls
- Dynamic task spawning from running actors
- GPU-aware scheduling
- Resource management with soft limits
"""

import ray
import asyncio
from typing import Dict, List
import time


@ray.remote(num_cpus=1, memory=512 * 1024 * 1024)  # 512MB soft limit
class AIAgent:
    """Stateful AI agent actor"""

    def __init__(self, agent_id: str, config: dict):
        self.agent_id = agent_id
        self.config = config
        self.memory = []  # Agent maintains state across method calls
        self.task_count = 0
        self.start_time = time.time()

    def process_task(self, task_data: dict) -> dict:
        """Process a task and update internal state"""
        print(f"Agent {self.agent_id} processing: {task_data}")
        
        # Update memory
        self.memory.append({
            "task_id": task_data.get("task_id"),
            "timestamp": time.time(),
            "result": "processed"
        })
        
        self.task_count += 1
        
        # Simulate processing
        time.sleep(0.5)
        
        return {
            "agent_id": self.agent_id,
            "task_id": task_data.get("task_id"),
            "status": "completed",
            "memory_size": len(self.memory)
        }

    def spawn_subtask(self, subtask_data: dict):
        """Dynamically spawn new task from running actor"""
        # This is the key capability Ray provides over Celery
        subtask = process_subtask.remote(subtask_data)
        return ray.get(subtask)

    def get_state(self) -> dict:
        """Query agent state"""
        return {
            "agent_id": self.agent_id,
            "task_count": self.task_count,
            "memory_size": len(self.memory),
            "uptime": time.time() - self.start_time
        }

    def checkpoint_state(self) -> dict:
        """Create state checkpoint for recovery"""
        return {
            "agent_id": self.agent_id,
            "memory": self.memory.copy(),
            "task_count": self.task_count,
            "config": self.config
        }

    def restore_from_checkpoint(self, checkpoint: dict):
        """Restore agent from checkpoint"""
        self.memory = checkpoint["memory"]
        self.task_count = checkpoint["task_count"]
        self.config = checkpoint["config"]
        print(f"Agent {self.agent_id} restored from checkpoint")


@ray.remote
def process_subtask(subtask_data: dict) -> dict:
    """Stateless task spawned by agent"""
    print(f"Processing subtask: {subtask_data}")
    time.sleep(0.2)
    return {"subtask_id": subtask_data.get("id"), "status": "done"}


@ray.remote(num_gpus=0.5)  # Request half a GPU
class GPUAgent:
    """Agent with GPU resource requirements"""

    def __init__(self, model_name: str):
        self.model_name = model_name
        # In real implementation, load ML model here
        print(f"GPU Agent initialized with model: {model_name}")

    def inference(self, input_data: dict) -> dict:
        """Run inference on GPU"""
        # Simulate GPU inference
        time.sleep(1)
        return {
            "model": self.model_name,
            "prediction": "result",
            "confidence": 0.95
        }


class AgentOrchestrator:
    """Orchestrates multiple Ray actors"""

    def __init__(self, num_agents: int = 10):
        self.num_agents = num_agents
        self.agents = []

    def initialize_agents(self):
        """Create agent pool"""
        print(f"Initializing {self.num_agents} agents...")
        
        for i in range(self.num_agents):
            agent = AIAgent.remote(
                agent_id=f"agent-{i:03d}",
                config={"type": "worker", "priority": "normal"}
            )
            self.agents.append(agent)
        
        print(f"Created {len(self.agents)} agents")

    def distribute_tasks(self, tasks: List[dict]):
        """Distribute tasks across agent pool"""
        futures = []
        
        for i, task in enumerate(tasks):
            # Round-robin distribution
            agent = self.agents[i % len(self.agents)]
            future = agent.process_task.remote(task)
            futures.append(future)
        
        # Wait for all tasks to complete
        results = ray.get(futures)
        return results

    def get_cluster_state(self) -> dict:
        """Get state of all agents"""
        state_futures = [agent.get_state.remote() for agent in self.agents]
        states = ray.get(state_futures)
        
        return {
            "total_agents": len(self.agents),
            "agent_states": states,
            "total_tasks": sum(s["task_count"] for s in states)
        }


def main():
    """Example usage"""
    # Initialize Ray with custom config
    ray.init(
        num_cpus=8,  # Limit CPU usage
        object_store_memory=1 * 1024 * 1024 * 1024,  # 1GB object store
        _system_config={
            "automatic_object_spilling_enabled": True,
        }
    )

    print(f"Ray initialized: {ray.cluster_resources()}")

    # Create orchestrator
    orchestrator = AgentOrchestrator(num_agents=10)
    orchestrator.initialize_agents()

    # Create tasks
    tasks = [{"task_id": f"task-{i}", "data": f"payload-{i}"} for i in range(50)]

    # Distribute and process
    print("\nDistributing tasks...")
    results = orchestrator.distribute_tasks(tasks)
    print(f"Completed {len(results)} tasks")

    # Check cluster state
    state = orchestrator.get_cluster_state()
    print(f"\nCluster state: {state['total_tasks']} total tasks processed")

    # Cleanup
    ray.shutdown()


if __name__ == "__main__":
    main()
