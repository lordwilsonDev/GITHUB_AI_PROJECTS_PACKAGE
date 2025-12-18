#!/usr/bin/env python3
"""
Autonomous Planning System
Agents that plan, execute, and adapt without human intervention
"""

import asyncio
import random
from datetime import datetime
from typing import Dict, List, Optional, Set
import time


class Goal:
    """Represents a goal to achieve"""
    
    def __init__(self, goal_id: str, description: str, success_criteria: Dict):
        self.goal_id = goal_id
        self.description = description
        self.success_criteria = success_criteria
        self.status = "pending"
        self.progress = 0.0
        self.subgoals = []
        
    def is_achieved(self) -> bool:
        """Check if goal is achieved"""
        return self.progress >= 1.0
    
    def update_progress(self, delta: float):
        """Update goal progress"""
        self.progress = min(1.0, self.progress + delta)
        if self.is_achieved():
            self.status = "achieved"


class Plan:
    """A plan to achieve a goal"""
    
    def __init__(self, plan_id: str, goal: Goal):
        self.plan_id = plan_id
        self.goal = goal
        self.steps = []
        self.current_step = 0
        self.created_at = datetime.now()
        self.adaptations = []
        
    def add_step(self, step: Dict):
        """Add a step to the plan"""
        self.steps.append(step)
    
    def get_next_step(self) -> Optional[Dict]:
        """Get next step to execute"""
        if self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None
    
    def complete_step(self):
        """Mark current step as complete"""
        self.current_step += 1
    
    def adapt(self, reason: str, new_steps: List[Dict]):
        """Adapt plan based on new information"""
        self.adaptations.append({
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "steps_added": len(new_steps)
        })
        self.steps.extend(new_steps)
        print(f"📝 Plan {self.plan_id} adapted: {reason}")


class AutonomousAgent:
    """Agent that can plan and execute autonomously"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.goals = []
        self.plans = {}
        self.knowledge = set()
        self.capabilities = {
            "planning": 0.6,
            "execution": 0.7,
            "adaptation": 0.5,
            "learning": 0.6
        }
        self.decisions_made = []
        
    async def create_plan(self, goal: Goal) -> Plan:
        """Autonomously create a plan to achieve goal"""
        print(f"🎯 {self.agent_id} planning for: {goal.description}")
        
        plan = Plan(f"plan_{len(self.plans)}", goal)
        
        # Decompose goal into steps
        complexity = goal.success_criteria.get("complexity", 0.5)
        num_steps = int(3 + complexity * 7)  # 3-10 steps
        
        for i in range(num_steps):
            step = {
                "step_id": i,
                "action": f"step_{i}",
                "description": f"Execute phase {i+1} of {num_steps}",
                "estimated_duration": random.uniform(0.1, 0.5)
            }
            plan.add_step(step)
        
        self.plans[plan.plan_id] = plan
        
        await asyncio.sleep(0.1)  # Simulate planning time
        
        print(f"   ✓ Created plan with {len(plan.steps)} steps")
        return plan
    
    async def execute_plan(self, plan: Plan) -> bool:
        """Execute a plan autonomously"""
        print(f"\n⚡ {self.agent_id} executing plan {plan.plan_id}")
        
        while True:
            step = plan.get_next_step()
            if not step:
                break
            
            # Execute step
            success = await self.execute_step(step)
            
            if success:
                plan.complete_step()
                plan.goal.update_progress(1.0 / len(plan.steps))
                print(f"   ✓ Step {step['step_id']} complete ({plan.goal.progress*100:.0f}%)")
            else:
                # Adapt plan if step fails
                await self.adapt_plan(plan, f"Step {step['step_id']} failed")
            
            # Learn from execution
            self.learn_from_execution(step, success)
        
        return plan.goal.is_achieved()
    
    async def execute_step(self, step: Dict) -> bool:
        """Execute a single step"""
        duration = step.get("estimated_duration", 0.2)
        await asyncio.sleep(duration)
        
        # Success probability based on execution capability
        success_prob = 0.7 + self.capabilities["execution"] * 0.2
        return random.random() < success_prob
    
    async def adapt_plan(self, plan: Plan, reason: str):
        """Adapt plan when things don't go as expected"""
        adaptation_skill = self.capabilities["adaptation"]
        
        # Create alternative steps
        new_steps = []
        if random.random() < adaptation_skill:
            new_steps.append({
                "step_id": len(plan.steps),
                "action": "alternative_approach",
                "description": "Try alternative approach",
                "estimated_duration": 0.3
            })
            plan.adapt(reason, new_steps)
    
    def learn_from_execution(self, step: Dict, success: bool):
        """Learn from execution outcomes"""
        if success:
            self.capabilities["execution"] = min(1.0, self.capabilities["execution"] + 0.01)
        else:
            self.capabilities["adaptation"] = min(1.0, self.capabilities["adaptation"] + 0.02)
    
    async def autonomous_decision(self, situation: Dict) -> Dict:
        """Make autonomous decision based on situation"""
        decision = {
            "timestamp": datetime.now().isoformat(),
            "situation": situation,
            "decision": None,
            "reasoning": None
        }
        
        # Analyze situation
        if situation.get("type") == "obstacle":
            decision["decision"] = "adapt_and_continue"
            decision["reasoning"] = "Obstacle detected, adapting approach"
        elif situation.get("type") == "opportunity":
            decision["decision"] = "exploit_opportunity"
            decision["reasoning"] = "Opportunity identified, adjusting plan"
        else:
            decision["decision"] = "continue_as_planned"
            decision["reasoning"] = "No changes needed"
        
        self.decisions_made.append(decision)
        print(f"🤔 {self.agent_id} decided: {decision['decision']}")
        
        return decision


class AutonomousSwarm:
    """Swarm of agents that coordinate autonomously"""
    
    def __init__(self, num_agents: int = 10):
        self.agents = [AutonomousAgent(f"agent_{i}") for i in range(num_agents)]
        self.shared_goals = []
        self.coordination_events = []
        
    async def assign_goal(self, goal: Goal) -> AutonomousAgent:
        """Autonomously assign goal to best agent"""
        # Find agent with highest planning capability
        best_agent = max(self.agents, key=lambda a: a.capabilities["planning"])
        best_agent.goals.append(goal)
        return best_agent
    
    async def coordinate(self, agents: List[AutonomousAgent]):
        """Agents coordinate autonomously"""
        print("\n🤝 Agents coordinating...")
        
        # Share knowledge
        all_knowledge = set()
        for agent in agents:
            all_knowledge.update(agent.knowledge)
        
        for agent in agents:
            agent.knowledge = all_knowledge.copy()
        
        self.coordination_events.append({
            "timestamp": datetime.now().isoformat(),
            "agents": [a.agent_id for a in agents],
            "knowledge_shared": len(all_knowledge)
        })
        
        print(f"   ✓ {len(agents)} agents synchronized knowledge")
    
    async def autonomous_workflow(self, goals: List[Goal]):
        """Execute workflow autonomously"""
        print(f"\n🚀 Starting autonomous workflow with {len(goals)} goals")
        print("=" * 70)
        
        # Assign goals
        assignments = []
        for goal in goals:
            agent = await self.assign_goal(goal)
            assignments.append((agent, goal))
            print(f"   {goal.description} → {agent.agent_id}")
        
        # Agents create plans
        plans = []
        for agent, goal in assignments:
            plan = await agent.create_plan(goal)
            plans.append((agent, plan))
        
        # Coordinate before execution
        await self.coordinate([a for a, _ in assignments])
        
        # Execute plans in parallel
        print("\n⚡ Executing plans...")
        tasks = [agent.execute_plan(plan) for agent, plan in plans]
        results = await asyncio.gather(*tasks)
        
        # Report results
        success_count = sum(1 for r in results if r)
        print(f"\n✅ Workflow complete: {success_count}/{len(goals)} goals achieved")
        
        return results


async def demo_autonomous_planning():
    """Demonstrate autonomous planning and execution"""
    print("🤖 Autonomous Planning System")
    print("=" * 70)
    
    # Part 1: Single agent autonomous planning
    print("\n📋 Part 1: Single Agent Autonomous Planning")
    print("-" * 70)
    
    agent = AutonomousAgent("alpha")
    
    goal = Goal(
        "goal_1",
        "Optimize system performance",
        {"complexity": 0.7, "priority": "high"}
    )
    
    plan = await agent.create_plan(goal)
    success = await agent.execute_plan(plan)
    
    print(f"\n📊 Results:")
    print(f"   Goal achieved: {success}")
    print(f"   Steps executed: {plan.current_step}")
    print(f"   Plan adaptations: {len(plan.adaptations)}")
    print(f"   Agent decisions: {len(agent.decisions_made)}")
    
    # Part 2: Autonomous swarm coordination
    print("\n\n🌊 Part 2: Autonomous Swarm Coordination")
    print("-" * 70)
    
    swarm = AutonomousSwarm(num_agents=10)
    
    goals = [
        Goal("goal_1", "Process data pipeline", {"complexity": 0.5}),
        Goal("goal_2", "Generate reports", {"complexity": 0.4}),
        Goal("goal_3", "Optimize algorithms", {"complexity": 0.8}),
        Goal("goal_4", "Monitor systems", {"complexity": 0.3}),
        Goal("goal_5", "Deploy updates", {"complexity": 0.6}),
    ]
    
    start_time = time.time()
    results = await swarm.autonomous_workflow(goals)
    duration = time.time() - start_time
    
    print(f"\n⏱️  Total time: {duration:.2f} seconds")
    print(f"📈 Success rate: {sum(results)/len(results)*100:.0f}%")
    print(f"🤝 Coordination events: {len(swarm.coordination_events)}")
    
    # Show agent capabilities after learning
    print(f"\n🧠 Agent Capabilities (after learning):")
    for agent in swarm.agents[:3]:  # Show first 3
        print(f"\n   {agent.agent_id}:")
        for cap, level in agent.capabilities.items():
            bar = "█" * int(level * 20)
            print(f"      {cap:12s} {bar} {level:.3f}")
    
    print("\n" + "=" * 70)
    print("🎉 Autonomous planning demonstration complete!")
    print("\nKey insights:")
    print("  • Agents plan without human intervention")
    print("  • Plans adapt when obstacles arise")
    print("  • Swarm coordinates autonomously")
    print("  • Learning improves future performance")


if __name__ == "__main__":
    asyncio.run(demo_autonomous_planning())
