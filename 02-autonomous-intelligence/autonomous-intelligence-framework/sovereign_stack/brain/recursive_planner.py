import asyncio
import redis
import json
import requests
from typing import Dict, List, Any
from datetime import datetime

class RecursivePlanner:
    """
    Sovereign Brain - The Recursive Planning Engine
    
    This is the core cognitive component of the Autonomous Intelligence Framework.
    It implements Level 6 meta-cognitive architecture with:
    - Event-driven goal decomposition
    - Archetype-based task execution  
    - Love Engine validation integration
    - Recursive planning with meta-cognitive oversight
    
    The planner doesn't just execute tasks - it thinks about HOW to think about tasks.
    """
    
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.heart_url = "http://localhost:9001"
        self.event_log = []
        
    def emit_event(self, event_type: str, payload: Dict[str, Any]):
        """
        Emit event to the Motia bus (via Redis pub/sub)
        
        Event-driven architecture allows:
        - Async coordination between components
        - Auditable history of all decisions
        - Decoupled specialist agents
        """
        event = {
            "type": event_type,
            "timestamp": datetime.now().isoformat(),
            "payload": payload
        }
        self.event_log.append(event)
        self.redis.publish('sovereign_events', json.dumps(event))
        print(f"📡 EVENT: {event_type}")
        return event
    
    def decompose_goal(self, goal: str) -> List[Dict[str, Any]]:
        """
        Recursive decomposition using Level 6 Meta-Prompting
        
        This is where GLM-4.6V or Claude Opus 4.5 would live in production.
        The decomposition doesn't just break down WHAT to do, but HOW to think
        about doing it - selecting appropriate cognitive archetypes for each phase.
        
        Archetypes:
        - Student: Learning, exploration, asking questions
        - Architect: Design, structure, system thinking
        - Surgeon: Precision, care, minimal intervention
        - Firefighter: Speed, decisiveness, handling chaos
        """
        print(f"\n🧠 PHASE 0: Meta-Analysis of goal: {goal}")
        
        # Simplified decomposition - in production, this calls frontier model
        if "build" in goal.lower():
            return [
                {"task": "analyze_requirements", "complexity": 0.3, "archetype": "Student"},
                {"task": "design_architecture", "complexity": 0.6, "archetype": "Architect"},
                {"task": "implement_core", "complexity": 0.8, "archetype": "Surgeon"},
                {"task": "test_and_verify", "complexity": 0.5, "archetype": "Firefighter"}
            ]
        else:
            return [{"task": goal, "complexity": 0.4, "archetype": "Student"}]
    
    async def validate_with_heart(self, action: str, intent: str, complexity: float) -> bool:
        """
        Check with the Love Engine before execution
        
        The Heart validates:
        - Torsion (alignment with truth)
        - VDR (value-density ratio)
        - I_NSSI (non-self-sacrificing invariant)
        
        This prevents self-destructive patterns and maintains thermodynamic health.
        """
        try:
            response = requests.post(
                f"{self.heart_url}/validate",
                json={"action": action, "intent": intent, "estimated_complexity": complexity},
                timeout=5
            )
            result = response.json()
            
            if result["validated"]:
                self.emit_event("agent.validated", result)
                return True
            else:
                self.emit_event("agent.rejected", result)
                print(f"❌ REJECTED: {result['reason']}")
                return False
                
        except Exception as e:
            print(f"⚠️ Heart unreachable: {e}")
            return False
    
    async def execute_task(self, task: Dict[str, Any]):
        """
        Execute a single task with archetype-based behavior
        
        The archetype determines HOW the task is approached:
        - Student: Curious, asking questions, learning-oriented
        - Architect: Systematic, designing before building
        - Surgeon: Precise, careful, minimal changes
        - Firefighter: Fast, decisive, handling urgent issues
        """
        archetype = task.get("archetype", "Student")
        task_name = task["task"]
        
        print(f"\n🎭 Archetype: {archetype}")
        print(f"📋 Task: {task_name}")
        
        # Validate with Heart
        validated = await self.validate_with_heart(
            action=task_name,
            intent=f"Execute {task_name} as {archetype}",
            complexity=task["complexity"]
        )
        
        if not validated:
            return {"status": "rejected", "task": task_name}
        
        # Execute (simulated - in production, this calls actual tools via MCP)
        self.emit_event("agent.execute", {"task": task_name, "archetype": archetype})
        
        # Simulate work
        await asyncio.sleep(1)
        
        # Store result in memory
        result = {"status": "complete", "task": task_name, "output": f"Completed {task_name}"}
        self.redis.set(f"result:{task_name}", json.dumps(result))
        
        self.emit_event("agent.complete", result)
        return result
    
    async def plan_and_execute(self, user_goal: str):
        """
        Main entry point - the agent.plan handler
        
        This implements the full cycle:
        1. Decompose goal into subtasks with archetypes
        2. Validate each with Love Engine
        3. Execute recursively  
        4. Synthesize results
        5. Emit completion event
        """
        print(f"\n{'='*60}")
        print(f"🚀 SOVEREIGN BRAIN ACTIVATED")
        print(f"{'='*60}")
        
        self.emit_event("agent.plan", {"goal": user_goal})
        
        # Decompose
        subtasks = self.decompose_goal(user_goal)
        print(f"\n📊 Decomposed into {len(subtasks)} subtasks")
        
        # Execute recursively
        results = []
        for task in subtasks:
            result = await self.execute_task(task)
            results.append(result)
        
        # Synthesize
        self.emit_event("task.done", {
            "goal": user_goal,
            "results": results,
            "total_tasks": len(subtasks)
        })
        
        print(f"\n✅ Goal complete: {user_goal}")
        return results

# Event Bus Listener (simulates Motia steps)
class EventListener:
    """
    Event Bus Listener for monitoring system activity
    
    In a full Motia deployment, these events would trigger:
    - Specialist agent spawning
    - Logging and auditing
    - Real-time dashboard updates
    - Alerting and monitoring
    """
    
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.pubsub = self.redis.pubsub()
        self.pubsub.subscribe('sovereign_events')
        
    def listen(self):
        """Listen for events on the bus"""
        print("\n👂 Event Listener Active...")
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                event = json.loads(message['data'])
                print(f"🔔 Received: {event['type']} at {event['timestamp']}")

if __name__ == "__main__":
    # Start event listener in background
    import threading
    listener = EventListener()
    listener_thread = threading.Thread(target=listener.listen, daemon=True)
    listener_thread.start()
    
    # Run the planner
    planner = RecursivePlanner()
    asyncio.run(planner.plan_and_execute("Build a simple web scraper"))
