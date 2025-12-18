#!/usr/bin/env python3
"""
Distributed Cognition Engine - Level 16

Enables distributed cognitive processing through:
- Parallel thought processing
- Cognitive load distribution
- Collective problem solving

Part of New Build 8: Collective Consciousness & Universal Integration
"""

import time
import threading
from typing import Dict, List, Any, Optional, Set, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import PriorityQueue
import json


@dataclass
class CognitiveTask:
    """Represents a cognitive task to be processed."""
    task_id: str
    task_type: str  # 'analyze', 'decide', 'learn', 'create', 'optimize'
    input_data: Any
    priority: int = 5  # 1-10, higher is more urgent
    complexity: float = 1.0  # Estimated cognitive load
    dependencies: List[str] = field(default_factory=list)
    assigned_to: Optional[str] = None
    status: str = "pending"  # pending, processing, completed, failed
    result: Optional[Any] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CognitiveAgent:
    """Represents an agent capable of cognitive processing."""
    agent_id: str
    capabilities: Set[str] = field(default_factory=set)
    capacity: float = 1.0  # Maximum cognitive load
    current_load: float = 0.0
    tasks_completed: int = 0
    tasks_failed: int = 0
    active: bool = True
    performance_score: float = 1.0
    specialization: Optional[str] = None


@dataclass
class ThoughtProcess:
    """Represents a distributed thought process."""
    process_id: str
    problem: str
    subtasks: List[str] = field(default_factory=list)
    participating_agents: Set[str] = field(default_factory=set)
    partial_results: Dict[str, Any] = field(default_factory=dict)
    final_result: Optional[Any] = None
    status: str = "active"  # active, completed, failed
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None


class CognitiveLoadBalancer:
    """Balances cognitive load across agents."""
    
    def __init__(self):
        self.agents: Dict[str, CognitiveAgent] = {}
        self.lock = threading.Lock()
    
    def register_agent(self, agent_id: str, capabilities: Set[str],
                      capacity: float = 1.0, specialization: Optional[str] = None) -> bool:
        """Register a cognitive agent."""
        with self.lock:
            if agent_id in self.agents:
                return False
            
            self.agents[agent_id] = CognitiveAgent(
                agent_id=agent_id,
                capabilities=capabilities,
                capacity=capacity,
                specialization=specialization
            )
            return True
    
    def unregister_agent(self, agent_id: str) -> bool:
        """Unregister an agent."""
        with self.lock:
            if agent_id not in self.agents:
                return False
            
            self.agents[agent_id].active = False
            del self.agents[agent_id]
            return True
    
    def find_best_agent(self, task: CognitiveTask) -> Optional[str]:
        """Find the best agent for a task based on load and capabilities."""
        with self.lock:
            candidates = []
            
            for agent_id, agent in self.agents.items():
                if not agent.active:
                    continue
                
                # Check if agent has required capability
                if task.task_type not in agent.capabilities:
                    continue
                
                # Check if agent has capacity
                if agent.current_load + task.complexity > agent.capacity:
                    continue
                
                # Calculate score (lower is better)
                load_score = agent.current_load / agent.capacity
                specialization_bonus = 0.5 if agent.specialization == task.task_type else 0
                performance_factor = agent.performance_score
                
                score = load_score - specialization_bonus - (performance_factor * 0.2)
                candidates.append((agent_id, score))
            
            if not candidates:
                return None
            
            # Return agent with lowest score
            best_agent = min(candidates, key=lambda x: x[1])
            return best_agent[0]
    
    def assign_task(self, agent_id: str, task: CognitiveTask) -> bool:
        """Assign a task to an agent."""
        with self.lock:
            if agent_id not in self.agents:
                return False
            
            agent = self.agents[agent_id]
            if agent.current_load + task.complexity > agent.capacity:
                return False
            
            agent.current_load += task.complexity
            task.assigned_to = agent_id
            task.status = "processing"
            task.started_at = time.time()
            return True
    
    def complete_task(self, agent_id: str, task: CognitiveTask, success: bool = True) -> bool:
        """Mark a task as completed and update agent state."""
        with self.lock:
            if agent_id not in self.agents:
                return False
            
            agent = self.agents[agent_id]
            agent.current_load = max(0, agent.current_load - task.complexity)
            
            if success:
                agent.tasks_completed += 1
                task.status = "completed"
                # Improve performance score
                agent.performance_score = min(2.0, agent.performance_score * 1.01)
            else:
                agent.tasks_failed += 1
                task.status = "failed"
                # Decrease performance score
                agent.performance_score = max(0.5, agent.performance_score * 0.95)
            
            task.completed_at = time.time()
            return True
    
    def get_load_distribution(self) -> Dict[str, float]:
        """Get current load distribution across agents."""
        with self.lock:
            return {agent_id: agent.current_load / agent.capacity 
                   for agent_id, agent in self.agents.items() if agent.active}


class ParallelThoughtProcessor:
    """Processes thoughts in parallel across multiple agents."""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_queue: PriorityQueue = PriorityQueue()
        self.results: Dict[str, Any] = {}
        self.lock = threading.Lock()
    
    def submit_thought(self, thought_id: str, processor: Callable, 
                      data: Any, priority: int = 5) -> bool:
        """Submit a thought for parallel processing."""
        # Priority queue uses lower numbers for higher priority
        self.task_queue.put((-priority, thought_id, processor, data))
        return True
    
    def process_parallel(self, timeout: Optional[float] = None) -> Dict[str, Any]:
        """Process all queued thoughts in parallel."""
        futures = {}
        
        # Submit all tasks
        while not self.task_queue.empty():
            try:
                priority, thought_id, processor, data = self.task_queue.get_nowait()
                future = self.executor.submit(processor, data)
                futures[future] = thought_id
            except:
                break
        
        # Collect results
        results = {}
        for future in as_completed(futures, timeout=timeout):
            thought_id = futures[future]
            try:
                result = future.result()
                results[thought_id] = {"status": "success", "result": result}
            except Exception as e:
                results[thought_id] = {"status": "error", "error": str(e)}
        
        with self.lock:
            self.results.update(results)
        
        return results
    
    def get_result(self, thought_id: str) -> Optional[Dict[str, Any]]:
        """Get result of a processed thought."""
        with self.lock:
            return self.results.get(thought_id)
    
    def shutdown(self):
        """Shutdown the processor."""
        self.executor.shutdown(wait=True)


class CollectiveProblemSolver:
    """Solves problems collectively using distributed cognition."""
    
    def __init__(self):
        self.processes: Dict[str, ThoughtProcess] = {}
        self.lock = threading.Lock()
    
    def decompose_problem(self, problem: str, strategy: str = "parallel") -> List[str]:
        """Decompose a problem into subtasks."""
        # Simple decomposition strategies
        if strategy == "parallel":
            # Break into independent parallel tasks
            return [
                f"{problem}_analysis",
                f"{problem}_evaluation",
                f"{problem}_synthesis"
            ]
        elif strategy == "sequential":
            # Break into sequential dependent tasks
            return [
                f"{problem}_step1",
                f"{problem}_step2",
                f"{problem}_step3"
            ]
        elif strategy == "hierarchical":
            # Break into hierarchical tasks
            return [
                f"{problem}_high_level",
                f"{problem}_mid_level",
                f"{problem}_low_level"
            ]
        else:
            return [problem]
    
    def start_process(self, process_id: str, problem: str,
                     strategy: str = "parallel") -> bool:
        """Start a distributed thought process."""
        with self.lock:
            if process_id in self.processes:
                return False
            
            subtasks = self.decompose_problem(problem, strategy)
            self.processes[process_id] = ThoughtProcess(
                process_id=process_id,
                problem=problem,
                subtasks=subtasks
            )
            return True
    
    def contribute_result(self, process_id: str, agent_id: str,
                         subtask_id: str, result: Any) -> bool:
        """Contribute a partial result to a process."""
        with self.lock:
            if process_id not in self.processes:
                return False
            
            process = self.processes[process_id]
            process.participating_agents.add(agent_id)
            process.partial_results[subtask_id] = result
            return True
    
    def synthesize_solution(self, process_id: str) -> Optional[Any]:
        """Synthesize final solution from partial results."""
        with self.lock:
            if process_id not in self.processes:
                return None
            
            process = self.processes[process_id]
            
            # Check if all subtasks completed
            if len(process.partial_results) < len(process.subtasks):
                return None
            
            # Simple synthesis: combine all results
            synthesis = {
                "problem": process.problem,
                "subtasks_completed": len(process.partial_results),
                "participating_agents": list(process.participating_agents),
                "partial_results": process.partial_results,
                "synthesis_method": "collective_aggregation"
            }
            
            process.final_result = synthesis
            process.status = "completed"
            process.completed_at = time.time()
            
            return synthesis
    
    def get_process_status(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a thought process."""
        with self.lock:
            if process_id not in self.processes:
                return None
            
            process = self.processes[process_id]
            return {
                "process_id": process_id,
                "problem": process.problem,
                "status": process.status,
                "subtasks_total": len(process.subtasks),
                "subtasks_completed": len(process.partial_results),
                "agents_participating": len(process.participating_agents),
                "has_final_result": process.final_result is not None
            }


class DistributedCognition:
    """Main distributed cognition engine."""
    
    def __init__(self, max_workers: int = 4):
        self.load_balancer = CognitiveLoadBalancer()
        self.thought_processor = ParallelThoughtProcessor(max_workers)
        self.problem_solver = CollectiveProblemSolver()
        self.tasks: Dict[str, CognitiveTask] = {}
        self.lock = threading.Lock()
        self.active = True
    
    def register_agent(self, agent_id: str, capabilities: Set[str],
                      capacity: float = 1.0, specialization: Optional[str] = None) -> bool:
        """Register a cognitive agent."""
        return self.load_balancer.register_agent(agent_id, capabilities, capacity, specialization)
    
    def submit_task(self, task_id: str, task_type: str, input_data: Any,
                   priority: int = 5, complexity: float = 1.0) -> bool:
        """Submit a cognitive task."""
        with self.lock:
            if task_id in self.tasks:
                return False
            
            task = CognitiveTask(
                task_id=task_id,
                task_type=task_type,
                input_data=input_data,
                priority=priority,
                complexity=complexity
            )
            
            # Find best agent
            agent_id = self.load_balancer.find_best_agent(task)
            if not agent_id:
                return False
            
            # Assign task
            if not self.load_balancer.assign_task(agent_id, task):
                return False
            
            self.tasks[task_id] = task
            return True
    
    def complete_task(self, task_id: str, result: Any, success: bool = True) -> bool:
        """Mark a task as completed."""
        with self.lock:
            if task_id not in self.tasks:
                return False
            
            task = self.tasks[task_id]
            if not task.assigned_to:
                return False
            
            task.result = result
            return self.load_balancer.complete_task(task.assigned_to, task, success)
    
    def process_thoughts_parallel(self, thoughts: Dict[str, Tuple[Callable, Any]],
                                 priority: int = 5) -> Dict[str, Any]:
        """Process multiple thoughts in parallel."""
        for thought_id, (processor, data) in thoughts.items():
            self.thought_processor.submit_thought(thought_id, processor, data, priority)
        
        return self.thought_processor.process_parallel()
    
    def solve_problem_collectively(self, problem_id: str, problem: str,
                                  strategy: str = "parallel") -> bool:
        """Start collective problem solving."""
        return self.problem_solver.start_process(problem_id, problem, strategy)
    
    def contribute_solution(self, problem_id: str, agent_id: str,
                          subtask_id: str, result: Any) -> bool:
        """Contribute to collective problem solving."""
        return self.problem_solver.contribute_result(problem_id, agent_id, subtask_id, result)
    
    def get_solution(self, problem_id: str) -> Optional[Any]:
        """Get synthesized solution."""
        return self.problem_solver.synthesize_solution(problem_id)
    
    def get_system_state(self) -> Dict[str, Any]:
        """Get current system state."""
        load_dist = self.load_balancer.get_load_distribution()
        
        with self.lock:
            return {
                "active": self.active,
                "agents": len(self.load_balancer.agents),
                "tasks_total": len(self.tasks),
                "tasks_pending": len([t for t in self.tasks.values() if t.status == "pending"]),
                "tasks_processing": len([t for t in self.tasks.values() if t.status == "processing"]),
                "tasks_completed": len([t for t in self.tasks.values() if t.status == "completed"]),
                "load_distribution": load_dist,
                "avg_load": sum(load_dist.values()) / len(load_dist) if load_dist else 0
            }
    
    def shutdown(self):
        """Shutdown the distributed cognition engine."""
        self.active = False
        self.thought_processor.shutdown()


# Singleton pattern
_engines: Dict[str, DistributedCognition] = {}
_engine_lock = threading.Lock()


def get_distributed_cognition(engine_id: str = "default", max_workers: int = 4) -> DistributedCognition:
    """Get or create a distributed cognition engine."""
    with _engine_lock:
        if engine_id not in _engines:
            _engines[engine_id] = DistributedCognition(max_workers)
        return _engines[engine_id]


class DistributedCognitionContract:
    """Contract interface for testing."""
    
    @staticmethod
    def distribute_load(agents: List[str], tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Distribute cognitive load across agents."""
        engine = get_distributed_cognition("test")
        
        # Register agents
        for agent_id in agents:
            engine.register_agent(agent_id, {"analyze", "decide", "learn"})
        
        # Submit tasks
        for i, task_data in enumerate(tasks):
            engine.submit_task(
                f"task_{i}",
                task_data.get("type", "analyze"),
                task_data.get("data"),
                complexity=task_data.get("complexity", 1.0)
            )
        
        # Complete tasks
        for i in range(len(tasks)):
            engine.complete_task(f"task_{i}", f"result_{i}")
        
        state = engine.get_system_state()
        engine.shutdown()
        return state
    
    @staticmethod
    def process_parallel(thought_count: int) -> Dict[str, Any]:
        """Process thoughts in parallel."""
        engine = get_distributed_cognition("test")
        
        # Create thoughts
        thoughts = {
            f"thought_{i}": (lambda x: x * 2, i)
            for i in range(thought_count)
        }
        
        results = engine.process_thoughts_parallel(thoughts)
        engine.shutdown()
        return results
    
    @staticmethod
    def solve_collectively(problem: str, agent_count: int) -> Dict[str, Any]:
        """Solve problem collectively."""
        engine = get_distributed_cognition("test")
        
        # Start problem solving
        engine.solve_problem_collectively("prob_001", problem)
        
        # Get subtasks
        status = engine.problem_solver.get_process_status("prob_001")
        subtasks = engine.problem_solver.processes["prob_001"].subtasks
        
        # Agents contribute
        for i in range(min(agent_count, len(subtasks))):
            engine.contribute_solution(
                "prob_001",
                f"agent_{i}",
                subtasks[i],
                f"solution_part_{i}"
            )
        
        # Get solution
        solution = engine.get_solution("prob_001")
        engine.shutdown()
        return solution


def demo():
    """Demonstrate distributed cognition capabilities."""
    print("=== Distributed Cognition Engine Demo ===")
    print()
    
    engine = get_distributed_cognition("demo", max_workers=4)
    
    # Register agents
    print("1. Registering cognitive agents...")
    engine.register_agent("analyzer", {"analyze"}, capacity=2.0, specialization="analyze")
    engine.register_agent("decider", {"decide"}, capacity=1.5, specialization="decide")
    engine.register_agent("learner", {"learn"}, capacity=1.0, specialization="learn")
    engine.register_agent("generalist", {"analyze", "decide", "learn"}, capacity=3.0)
    print("   Registered 4 agents\n")
    
    # Submit tasks
    print("2. Submitting cognitive tasks...")
    engine.submit_task("task_1", "analyze", {"data": "pattern_1"}, complexity=0.5)
    engine.submit_task("task_2", "decide", {"options": ["A", "B"]}, complexity=0.8)
    engine.submit_task("task_3", "learn", {"examples": [1, 2, 3]}, complexity=1.0)
    print("   Submitted 3 tasks\n")
    
    # Check state
    state = engine.get_system_state()
    print(f"3. System state:")
    print(f"   Agents: {state['agents']}")
    print(f"   Tasks processing: {state['tasks_processing']}")
    print(f"   Average load: {state['avg_load']:.2f}\n")
    
    # Complete tasks
    print("4. Completing tasks...")
    engine.complete_task("task_1", "pattern_detected")
    engine.complete_task("task_2", "option_A")
    engine.complete_task("task_3", "model_updated")
    print("   All tasks completed\n")
    
    # Parallel processing
    print("5. Parallel thought processing...")
    thoughts = {
        f"thought_{i}": (lambda x: x ** 2, i)
        for i in range(5)
    }
    results = engine.process_thoughts_parallel(thoughts)
    print(f"   Processed {len(results)} thoughts in parallel\n")
    
    # Collective problem solving
    print("6. Collective problem solving...")
    engine.solve_problem_collectively("complex_problem", "Optimize system performance")
    engine.contribute_solution("complex_problem", "analyzer", "Optimize system performance_analysis", "bottleneck_found")
    engine.contribute_solution("complex_problem", "decider", "Optimize system performance_evaluation", "solution_viable")
    engine.contribute_solution("complex_problem", "learner", "Optimize system performance_synthesis", "improvements_identified")
    solution = engine.get_solution("complex_problem")
    print(f"   Solution synthesized from {solution['subtasks_completed']} subtasks\n")
    
    # Final state
    final_state = engine.get_system_state()
    print("7. Final state:")
    print(f"   Tasks completed: {final_state['tasks_completed']}")
    print(f"   Average load: {final_state['avg_load']:.2f}")
    
    engine.shutdown()
    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    demo()
