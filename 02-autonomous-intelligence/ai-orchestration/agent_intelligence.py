#!/usr/bin/env python3
"""
Agent Intelligence Layer - Self-Learning and Improvement
Makes agents smarter over time through experience and collaboration
"""

import asyncio
import json
import time
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional
import random


class AgentMemory:
    """Persistent memory for agents to learn from experience"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.experiences = []
        self.skills = defaultdict(float)  # skill_name -> proficiency (0-1)
        self.success_rate = defaultdict(lambda: {"success": 0, "total": 0})
        self.learned_patterns = []
        
    def record_experience(self, task_type: str, success: bool, duration: float, metadata: Dict = None):
        """Record task outcome to learn from"""
        experience = {
            "timestamp": datetime.now().isoformat(),
            "task_type": task_type,
            "success": success,
            "duration": duration,
            "metadata": metadata or {}
        }
        self.experiences.append(experience)
        
        # Update success rate
        self.success_rate[task_type]["total"] += 1
        if success:
            self.success_rate[task_type]["success"] += 1
            
        # Improve skill based on success
        if success:
            current_skill = self.skills[task_type]
            # Logarithmic improvement - harder to improve as you get better
            improvement = 0.1 * (1 - current_skill)
            self.skills[task_type] = min(1.0, current_skill + improvement)
        
    def get_proficiency(self, task_type: str) -> float:
        """Get agent's proficiency in a task type (0-1)"""
        return self.skills.get(task_type, 0.0)
    
    def get_success_rate(self, task_type: str) -> float:
        """Get historical success rate for task type"""
        stats = self.success_rate[task_type]
        if stats["total"] == 0:
            return 0.5  # Unknown, assume average
        return stats["success"] / stats["total"]
    
    def discover_pattern(self, pattern: str):
        """Agent discovers a useful pattern"""
        if pattern not in self.learned_patterns:
            self.learned_patterns.append(pattern)
            print(f"🧠 Agent {self.agent_id} learned: {pattern}")


class KnowledgeBase:
    """Shared knowledge base for all agents"""
    
    def __init__(self):
        self.collective_knowledge = {}
        self.best_practices = defaultdict(list)
        self.agent_specializations = {}
        
    def share_knowledge(self, agent_id: str, knowledge_type: str, knowledge: Any):
        """Agent shares knowledge with the collective"""
        key = f"{knowledge_type}:{agent_id}"
        self.collective_knowledge[key] = {
            "agent_id": agent_id,
            "type": knowledge_type,
            "data": knowledge,
            "timestamp": datetime.now().isoformat()
        }
        
    def get_expert(self, task_type: str) -> Optional[str]:
        """Find the most skilled agent for a task type"""
        return self.agent_specializations.get(task_type)
    
    def update_specializations(self, agent_id: str, task_type: str, proficiency: float):
        """Update which agent is best at what"""
        current_expert = self.agent_specializations.get(task_type)
        if current_expert is None:
            self.agent_specializations[task_type] = agent_id
        # Could add logic to track top N experts per task
        
    def add_best_practice(self, task_type: str, practice: str):
        """Add a discovered best practice"""
        if practice not in self.best_practices[task_type]:
            self.best_practices[task_type].append(practice)
            print(f"📚 New best practice for {task_type}: {practice}")


class IntelligentAgent:
    """Enhanced agent with learning capabilities"""
    
    def __init__(self, agent_id: str, knowledge_base: KnowledgeBase):
        self.agent_id = agent_id
        self.memory = AgentMemory(agent_id)
        self.knowledge_base = knowledge_base
        self.current_task = None
        
    async def execute_task(self, task: Dict) -> Dict:
        """Execute task and learn from the experience"""
        task_type = task.get("type", "unknown")
        start_time = time.time()
        
        self.current_task = task
        
        # Check if we should ask an expert
        proficiency = self.memory.get_proficiency(task_type)
        if proficiency < 0.3:
            expert = self.knowledge_base.get_expert(task_type)
            if expert and expert != self.agent_id:
                print(f"🤝 Agent {self.agent_id} consulting expert {expert} for {task_type}")
        
        # Simulate task execution with skill-based success probability
        success_probability = 0.5 + (proficiency * 0.4)  # 50-90% based on skill
        success = random.random() < success_probability
        
        # Simulate work
        await asyncio.sleep(random.uniform(0.1, 0.5))
        
        duration = time.time() - start_time
        
        # Learn from experience
        self.memory.record_experience(task_type, success, duration, task)
        
        # Share knowledge if we're getting good at this
        if proficiency > 0.7:
            self.knowledge_base.update_specializations(self.agent_id, task_type, proficiency)
            
        # Discover patterns occasionally
        if success and random.random() < 0.1:
            pattern = f"Efficient {task_type} execution pattern"
            self.memory.discover_pattern(pattern)
            self.knowledge_base.add_best_practice(task_type, pattern)
        
        result = {
            "agent_id": self.agent_id,
            "task_id": task.get("id"),
            "success": success,
            "duration": duration,
            "proficiency": proficiency,
            "learned": proficiency > self.memory.get_proficiency(task_type)
        }
        
        self.current_task = None
        return result
    
    def get_stats(self) -> Dict:
        """Get agent statistics"""
        return {
            "agent_id": self.agent_id,
            "skills": dict(self.memory.skills),
            "success_rates": {k: v["success"]/v["total"] if v["total"] > 0 else 0 
                            for k, v in self.memory.success_rate.items()},
            "experiences": len(self.memory.experiences),
            "patterns_learned": len(self.memory.learned_patterns)
        }


class CollaborativeSwarm:
    """Swarm of agents that learn and collaborate"""
    
    def __init__(self, num_agents: int = 50):
        self.knowledge_base = KnowledgeBase()
        self.agents = [IntelligentAgent(f"agent_{i}", self.knowledge_base) 
                      for i in range(num_agents)]
        self.task_queue = asyncio.Queue()
        self.results = []
        
    async def add_task(self, task: Dict):
        """Add task to queue"""
        await self.task_queue.put(task)
    
    async def worker(self, agent: IntelligentAgent):
        """Worker loop for an agent"""
        while True:
            try:
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                result = await agent.execute_task(task)
                self.results.append(result)
                self.task_queue.task_done()
            except asyncio.TimeoutError:
                break
    
    async def process_tasks(self, tasks: List[Dict]):
        """Process tasks with collaborative learning"""
        # Add all tasks
        for task in tasks:
            await self.add_task(task)
        
        # Start all workers
        workers = [asyncio.create_task(self.worker(agent)) for agent in self.agents]
        
        # Wait for completion
        await self.task_queue.join()
        
        # Cancel workers
        for w in workers:
            w.cancel()
        
        return self.results
    
    def get_swarm_intelligence(self) -> Dict:
        """Get collective intelligence metrics"""
        all_stats = [agent.get_stats() for agent in self.agents]
        
        # Aggregate skills
        all_skills = defaultdict(list)
        for stats in all_stats:
            for skill, level in stats["skills"].items():
                all_skills[skill].append(level)
        
        avg_skills = {skill: sum(levels)/len(levels) 
                     for skill, levels in all_skills.items()}
        
        return {
            "total_agents": len(self.agents),
            "total_experiences": sum(s["experiences"] for s in all_stats),
            "total_patterns": sum(s["patterns_learned"] for s in all_stats),
            "average_skills": avg_skills,
            "specializations": dict(self.knowledge_base.agent_specializations),
            "best_practices": dict(self.knowledge_base.best_practices)
        }


class MetaLearner:
    """System that learns about the learning process itself"""
    
    def __init__(self):
        self.optimization_history = []
        self.performance_metrics = []
        
    def analyze_swarm_performance(self, swarm: CollaborativeSwarm) -> Dict:
        """Analyze how well the swarm is learning"""
        intelligence = swarm.get_swarm_intelligence()
        
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "learning_rate": self._calculate_learning_rate(swarm),
            "skill_distribution": intelligence["average_skills"],
            "specialization_coverage": len(intelligence["specializations"]),
            "knowledge_sharing": len(intelligence["best_practices"])
        }
        
        self.performance_metrics.append(analysis)
        return analysis
    
    def _calculate_learning_rate(self, swarm: CollaborativeSwarm) -> float:
        """Calculate how fast agents are improving"""
        recent_results = swarm.results[-100:] if len(swarm.results) > 100 else swarm.results
        if not recent_results:
            return 0.0
        
        learning_events = sum(1 for r in recent_results if r.get("learned", False))
        return learning_events / len(recent_results)
    
    def suggest_optimizations(self, swarm: CollaborativeSwarm) -> List[str]:
        """Suggest ways to improve the system"""
        suggestions = []
        intelligence = swarm.get_swarm_intelligence()
        
        # Check for skill gaps
        if len(intelligence["specializations"]) < 5:
            suggestions.append("Increase task diversity to develop more specializations")
        
        # Check learning rate
        if len(self.performance_metrics) > 0:
            latest = self.performance_metrics[-1]
            if latest["learning_rate"] < 0.1:
                suggestions.append("Learning rate low - consider more challenging tasks")
        
        # Check knowledge sharing
        if intelligence["total_patterns"] < intelligence["total_agents"] * 0.5:
            suggestions.append("Increase knowledge sharing between agents")
        
        return suggestions


async def demo_intelligent_swarm():
    """Demonstrate self-improving agent swarm"""
    print("🚀 Initializing Intelligent Agent Swarm")
    print("=" * 60)
    
    # Create swarm
    swarm = CollaborativeSwarm(num_agents=50)
    meta_learner = MetaLearner()
    
    # Create diverse tasks
    task_types = ["content_creation", "data_analysis", "code_review", "research", "optimization"]
    tasks = []
    
    for i in range(200):
        tasks.append({
            "id": f"task_{i}",
            "type": random.choice(task_types),
            "complexity": random.uniform(0.3, 1.0)
        })
    
    print(f"\n📋 Processing {len(tasks)} tasks across {len(task_types)} types")
    print(f"👥 {len(swarm.agents)} agents learning and collaborating\n")
    
    # Process tasks
    start_time = time.time()
    results = await swarm.process_tasks(tasks)
    duration = time.time() - start_time
    
    # Analyze results
    print(f"\n✅ Completed in {duration:.2f} seconds")
    print(f"📊 Success rate: {sum(1 for r in results if r['success'])/len(results)*100:.1f}%")
    
    # Show swarm intelligence
    intelligence = swarm.get_swarm_intelligence()
    print(f"\n🧠 Swarm Intelligence:")
    print(f"   Total experiences: {intelligence['total_experiences']}")
    print(f"   Patterns discovered: {intelligence['total_patterns']}")
    print(f"   Specializations developed: {len(intelligence['specializations'])}")
    
    print(f"\n📈 Average Skill Levels:")
    for skill, level in sorted(intelligence['average_skills'].items(), key=lambda x: x[1], reverse=True):
        bar = "█" * int(level * 20)
        print(f"   {skill:20s} {bar} {level:.2f}")
    
    print(f"\n🎯 Specialized Experts:")
    for task_type, expert in intelligence['specializations'].items():
        print(f"   {task_type:20s} → {expert}")
    
    # Meta-learning analysis
    analysis = meta_learner.analyze_swarm_performance(swarm)
    print(f"\n🔬 Meta-Learning Analysis:")
    print(f"   Learning rate: {analysis['learning_rate']:.2%}")
    print(f"   Specialization coverage: {analysis['specialization_coverage']} task types")
    
    suggestions = meta_learner.suggest_optimizations(swarm)
    if suggestions:
        print(f"\n💡 Optimization Suggestions:")
        for suggestion in suggestions:
            print(f"   • {suggestion}")
    
    print("\n" + "=" * 60)
    print("🎉 Intelligent swarm demonstration complete!")
    print("Agents are now smarter and continue learning from each task.")


if __name__ == "__main__":
    asyncio.run(demo_intelligent_swarm())
