#!/usr/bin/env python3
"""
Collective Problem Solver - New Build 6, Phase 1
Distributed task decomposition, collaborative solution synthesis, and consensus mechanisms
"""

import time
import json
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
from queue import Queue
import hashlib


class TaskComplexity(Enum):
    """Task complexity levels"""
    SIMPLE = 1
    MODERATE = 2
    COMPLEX = 3
    VERY_COMPLEX = 4


class SolutionQuality(Enum):
    """Solution quality ratings"""
    POOR = 1
    ACCEPTABLE = 2
    GOOD = 3
    EXCELLENT = 4


@dataclass
class SubTask:
    """Represents a decomposed subtask"""
    task_id: str
    description: str
    complexity: TaskComplexity
    dependencies: List[str] = field(default_factory=list)
    assigned_agent: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Any = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'task_id': self.task_id,
            'description': self.description,
            'complexity': self.complexity.value,
            'dependencies': self.dependencies,
            'assigned_agent': self.assigned_agent,
            'status': self.status,
            'result': self.result
        }


@dataclass
class Solution:
    """Represents a proposed solution"""
    solution_id: str
    proposer: str
    content: Dict[str, Any]
    quality_score: float  # 0.0 to 1.0
    votes: int = 0
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'solution_id': self.solution_id,
            'proposer': self.proposer,
            'content': self.content,
            'quality_score': self.quality_score,
            'votes': self.votes,
            'timestamp': self.timestamp
        }


class TaskDecomposer:
    """Decomposes complex tasks into manageable subtasks"""
    
    def __init__(self):
        self.decomposition_strategies = {
            'sequential': self._sequential_decomposition,
            'parallel': self._parallel_decomposition,
            'hierarchical': self._hierarchical_decomposition
        }
    
    def decompose(self, task: Dict[str, Any], strategy: str = 'hierarchical') -> List[SubTask]:
        """Decompose a task using specified strategy"""
        if strategy not in self.decomposition_strategies:
            strategy = 'hierarchical'
        
        return self.decomposition_strategies[strategy](task)
    
    def _sequential_decomposition(self, task: Dict[str, Any]) -> List[SubTask]:
        """Break task into sequential steps"""
        subtasks = []
        steps = task.get('steps', [])
        
        for i, step in enumerate(steps):
            task_id = f"seq_{i}"
            dependencies = [f"seq_{i-1}"] if i > 0 else []
            
            subtasks.append(SubTask(
                task_id=task_id,
                description=step,
                complexity=TaskComplexity.MODERATE,
                dependencies=dependencies
            ))
        
        return subtasks
    
    def _parallel_decomposition(self, task: Dict[str, Any]) -> List[SubTask]:
        """Break task into parallel independent subtasks"""
        subtasks = []
        components = task.get('components', [])
        
        for i, component in enumerate(components):
            subtasks.append(SubTask(
                task_id=f"par_{i}",
                description=component,
                complexity=TaskComplexity.SIMPLE,
                dependencies=[]
            ))
        
        return subtasks
    
    def _hierarchical_decomposition(self, task: Dict[str, Any]) -> List[SubTask]:
        """Break task into hierarchical layers"""
        subtasks = []
        
        # Create high-level subtasks
        high_level = task.get('high_level', [])
        for i, hl_task in enumerate(high_level):
            subtasks.append(SubTask(
                task_id=f"hl_{i}",
                description=hl_task,
                complexity=TaskComplexity.COMPLEX,
                dependencies=[]
            ))
        
        # Create detail subtasks that depend on high-level
        details = task.get('details', [])
        for i, detail in enumerate(details):
            parent_idx = i % len(high_level) if high_level else 0
            subtasks.append(SubTask(
                task_id=f"det_{i}",
                description=detail,
                complexity=TaskComplexity.MODERATE,
                dependencies=[f"hl_{parent_idx}"]
            ))
        
        return subtasks


class SolutionSynthesizer:
    """Synthesizes solutions from multiple agent contributions"""
    
    def __init__(self):
        self.solutions: Dict[str, List[Solution]] = {}
        self.lock = threading.Lock()
    
    def propose_solution(self, problem_id: str, solution: Solution) -> bool:
        """Propose a solution for a problem"""
        with self.lock:
            if problem_id not in self.solutions:
                self.solutions[problem_id] = []
            self.solutions[problem_id].append(solution)
            return True
    
    def vote_for_solution(self, problem_id: str, solution_id: str) -> bool:
        """Vote for a specific solution"""
        with self.lock:
            if problem_id not in self.solutions:
                return False
            
            for solution in self.solutions[problem_id]:
                if solution.solution_id == solution_id:
                    solution.votes += 1
                    return True
            return False
    
    def synthesize(self, problem_id: str, method: str = 'voting') -> Optional[Solution]:
        """Synthesize final solution using specified method"""
        with self.lock:
            if problem_id not in self.solutions or not self.solutions[problem_id]:
                return None
            
            if method == 'voting':
                return max(self.solutions[problem_id], key=lambda s: s.votes)
            elif method == 'quality':
                return max(self.solutions[problem_id], key=lambda s: s.quality_score)
            elif method == 'hybrid':
                # Combine votes and quality
                return max(self.solutions[problem_id], 
                          key=lambda s: s.votes * 0.5 + s.quality_score * 0.5)
            else:
                return self.solutions[problem_id][0]
    
    def merge_solutions(self, problem_id: str) -> Optional[Dict[str, Any]]:
        """Merge multiple solutions into a comprehensive solution"""
        with self.lock:
            if problem_id not in self.solutions or not self.solutions[problem_id]:
                return None
            
            merged = {
                'components': [],
                'contributors': [],
                'combined_quality': 0.0,
                'total_votes': 0
            }
            
            for solution in self.solutions[problem_id]:
                merged['components'].append(solution.content)
                merged['contributors'].append(solution.proposer)
                merged['combined_quality'] += solution.quality_score
                merged['total_votes'] += solution.votes
            
            merged['combined_quality'] /= len(self.solutions[problem_id])
            
            return merged


class ConsensusEngine:
    """Reaches consensus among multiple agents"""
    
    def __init__(self):
        self.proposals: Dict[str, Dict[str, Any]] = {}
        self.votes: Dict[str, Dict[str, str]] = {}  # decision_id -> {agent_id: vote}
        self.lock = threading.Lock()
    
    def propose(self, decision_id: str, proposal: Dict[str, Any], proposer: str) -> bool:
        """Propose a decision for consensus"""
        with self.lock:
            if decision_id in self.proposals:
                return False
            
            self.proposals[decision_id] = {
                'proposal': proposal,
                'proposer': proposer,
                'timestamp': time.time(),
                'status': 'voting'
            }
            self.votes[decision_id] = {}
            return True
    
    def vote(self, decision_id: str, agent_id: str, vote: str, weight: float = 1.0) -> bool:
        """Cast a weighted vote"""
        with self.lock:
            if decision_id not in self.proposals:
                return False
            
            self.votes[decision_id][agent_id] = {
                'vote': vote,
                'weight': weight,
                'timestamp': time.time()
            }
            return True
    
    def reach_consensus(self, decision_id: str, threshold: float = 0.66) -> Optional[str]:
        """Determine if consensus is reached"""
        with self.lock:
            if decision_id not in self.votes or not self.votes[decision_id]:
                return None
            
            vote_counts = {}
            total_weight = 0.0
            
            for agent_vote in self.votes[decision_id].values():
                vote = agent_vote['vote']
                weight = agent_vote['weight']
                vote_counts[vote] = vote_counts.get(vote, 0.0) + weight
                total_weight += weight
            
            if total_weight == 0:
                return None
            
            # Find majority vote
            for vote, count in vote_counts.items():
                if count / total_weight >= threshold:
                    self.proposals[decision_id]['status'] = 'consensus_reached'
                    self.proposals[decision_id]['result'] = vote
                    return vote
            
            return None
    
    def get_consensus_strength(self, decision_id: str) -> float:
        """Calculate strength of consensus (0.0 to 1.0)"""
        with self.lock:
            if decision_id not in self.votes or not self.votes[decision_id]:
                return 0.0
            
            vote_counts = {}
            total_weight = 0.0
            
            for agent_vote in self.votes[decision_id].values():
                vote = agent_vote['vote']
                weight = agent_vote['weight']
                vote_counts[vote] = vote_counts.get(vote, 0.0) + weight
                total_weight += weight
            
            if total_weight == 0:
                return 0.0
            
            max_votes = max(vote_counts.values())
            return max_votes / total_weight


class CollectiveSolver:
    """Main collective problem-solving system"""
    
    def __init__(self):
        self.decomposer = TaskDecomposer()
        self.synthesizer = SolutionSynthesizer()
        self.consensus = ConsensusEngine()
        self.active_problems: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
    
    def solve_problem(self, problem: Dict[str, Any], agents: List[str]) -> Dict[str, Any]:
        """Collectively solve a problem"""
        problem_id = hashlib.md5(json.dumps(problem, sort_keys=True).encode()).hexdigest()[:8]
        
        with self.lock:
            self.active_problems[problem_id] = {
                'problem': problem,
                'agents': agents,
                'status': 'decomposing',
                'start_time': time.time()
            }
        
        # Step 1: Decompose problem
        subtasks = self.decomposer.decompose(problem, strategy='hierarchical')
        
        # Step 2: Assign subtasks to agents (round-robin)
        for i, subtask in enumerate(subtasks):
            subtask.assigned_agent = agents[i % len(agents)]
            subtask.status = 'assigned'
        
        # Step 3: Simulate solution proposals
        for i, agent in enumerate(agents):
            solution = Solution(
                solution_id=f"sol_{i}",
                proposer=agent,
                content={'approach': f'approach_{i}', 'steps': subtasks[:2]},
                quality_score=0.7 + (i * 0.1) % 0.3
            )
            self.synthesizer.propose_solution(problem_id, solution)
        
        # Step 4: Vote on solutions
        for agent in agents:
            # Each agent votes for best solution
            best_sol_id = f"sol_{len(agents)-1}"  # Vote for last (highest quality)
            self.synthesizer.vote_for_solution(problem_id, best_sol_id)
        
        # Step 5: Synthesize final solution
        final_solution = self.synthesizer.synthesize(problem_id, method='hybrid')
        
        # Step 6: Reach consensus
        self.consensus.propose(problem_id, {'solution': final_solution.to_dict()}, 'system')
        for agent in agents:
            self.consensus.vote(problem_id, agent, 'approve', weight=1.0)
        
        consensus_result = self.consensus.reach_consensus(problem_id, threshold=0.66)
        consensus_strength = self.consensus.get_consensus_strength(problem_id)
        
        with self.lock:
            self.active_problems[problem_id]['status'] = 'completed'
            self.active_problems[problem_id]['end_time'] = time.time()
        
        return {
            'problem_id': problem_id,
            'subtasks': [st.to_dict() for st in subtasks],
            'solutions_proposed': len(self.synthesizer.solutions.get(problem_id, [])),
            'final_solution': final_solution.to_dict() if final_solution else None,
            'consensus': consensus_result,
            'consensus_strength': consensus_strength,
            'agents_involved': len(agents)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get collective solver statistics"""
        with self.lock:
            return {
                'active_problems': len([p for p in self.active_problems.values() if p['status'] != 'completed']),
                'completed_problems': len([p for p in self.active_problems.values() if p['status'] == 'completed']),
                'total_solutions': sum(len(sols) for sols in self.synthesizer.solutions.values()),
                'consensus_decisions': len(self.consensus.proposals)
            }
    
    def demo(self) -> Dict[str, Any]:
        """Demonstration of collective problem solving"""
        print("\n🧩 Collective Problem Solver Demo")
        print("=" * 60)
        
        # Define a complex problem
        problem = {
            'name': 'Build Distributed System',
            'high_level': [
                'Design architecture',
                'Implement core services',
                'Deploy infrastructure'
            ],
            'details': [
                'Define API contracts',
                'Setup databases',
                'Configure load balancers',
                'Implement monitoring'
            ]
        }
        
        # Create agent team
        agents = ['agent_alpha', 'agent_beta', 'agent_gamma', 'agent_delta']
        
        print(f"\n📋 Problem: {problem['name']}")
        print(f"👥 Agent Team: {', '.join(agents)}")
        
        # Solve problem collectively
        result = self.solve_problem(problem, agents)
        
        print(f"\n✅ Problem Decomposed:")
        print(f"   Subtasks Created: {len(result['subtasks'])}")
        for st in result['subtasks'][:3]:  # Show first 3
            print(f"   - {st['task_id']}: {st['description']}")
        
        print(f"\n💡 Solution Synthesis:")
        print(f"   Solutions Proposed: {result['solutions_proposed']}")
        print(f"   Final Solution Quality: {result['final_solution']['quality_score']:.2f}")
        
        print(f"\n🤝 Consensus:")
        print(f"   Result: {result['consensus']}")
        print(f"   Strength: {result['consensus_strength']:.1%}")
        print(f"   Agents Involved: {result['agents_involved']}")
        
        # Get statistics
        stats = self.get_statistics()
        print(f"\n📊 System Statistics:")
        print(f"   Active Problems: {stats['active_problems']}")
        print(f"   Completed Problems: {stats['completed_problems']}")
        print(f"   Total Solutions: {stats['total_solutions']}")
        print(f"   Consensus Decisions: {stats['consensus_decisions']}")
        
        print("\n✅ Collective Problem Solver operational")
        return result


# Contract test interface
class CollectiveSolverContract:
    """Contract interface for testing"""
    
    @staticmethod
    def create() -> CollectiveSolver:
        """Create instance"""
        return CollectiveSolver()
    
    @staticmethod
    def test_basic_operations() -> bool:
        """Test basic operations"""
        solver = CollectiveSolver()
        
        # Test problem solving
        problem = {
            'name': 'Test Problem',
            'high_level': ['Task 1', 'Task 2'],
            'details': ['Detail 1', 'Detail 2']
        }
        agents = ['agent_1', 'agent_2', 'agent_3']
        
        result = solver.solve_problem(problem, agents)
        
        assert result['problem_id'] is not None
        assert len(result['subtasks']) > 0
        assert result['consensus'] is not None
        assert result['consensus_strength'] > 0
        
        return True


if __name__ == '__main__':
    # Run demo
    solver = CollectiveSolver()
    solver.demo()
