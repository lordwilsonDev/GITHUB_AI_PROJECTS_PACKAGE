#!/usr/bin/env python3
"""
Multi-Modal Agent System
Agents that process text, code, data, and reason across modalities
"""

import asyncio
import json
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
import time


class MultiModalAgent:
    """Agent that can process multiple types of information"""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.modalities = {
            "text": 0.5,
            "code": 0.3,
            "data": 0.4,
            "reasoning": 0.6
        }
        self.cross_modal_skills = []
        self.processed_tasks = []
        
    async def process_text(self, text: str) -> Dict:
        """Process natural language"""
        skill = self.modalities["text"]
        
        # Simulate text understanding
        await asyncio.sleep(0.1)
        
        return {
            "modality": "text",
            "length": len(text),
            "sentiment": random.choice(["positive", "neutral", "negative"]),
            "key_concepts": random.randint(3, 8),
            "confidence": skill
        }
    
    async def process_code(self, code: str) -> Dict:
        """Analyze and understand code"""
        skill = self.modalities["code"]
        
        await asyncio.sleep(0.1)
        
        return {
            "modality": "code",
            "lines": len(code.split('\n')),
            "complexity": random.choice(["low", "medium", "high"]),
            "bugs_found": random.randint(0, 3),
            "confidence": skill
        }
    
    async def process_data(self, data: List[float]) -> Dict:
        """Analyze numerical data"""
        skill = self.modalities["data"]
        
        await asyncio.sleep(0.1)
        
        if data:
            avg = sum(data) / len(data)
            trend = "increasing" if data[-1] > data[0] else "decreasing"
        else:
            avg = 0
            trend = "stable"
        
        return {
            "modality": "data",
            "points": len(data),
            "average": avg,
            "trend": trend,
            "confidence": skill
        }
    
    async def cross_modal_reasoning(self, inputs: Dict[str, Any]) -> Dict:
        """Reason across multiple modalities"""
        reasoning_skill = self.modalities["reasoning"]
        
        # Combine insights from different modalities
        modalities_used = list(inputs.keys())
        
        # Cross-modal insight emerges
        if len(modalities_used) >= 2:
            cross_modal_skill = f"cross_{'+'.join(sorted(modalities_used))}"
            if cross_modal_skill not in self.cross_modal_skills:
                self.cross_modal_skills.append(cross_modal_skill)
                print(f"🔗 {self.agent_id} developed cross-modal skill: {cross_modal_skill}")
        
        await asyncio.sleep(0.15)
        
        return {
            "modality": "cross_modal",
            "inputs": modalities_used,
            "synthesis": f"Integrated {len(modalities_used)} modalities",
            "confidence": reasoning_skill,
            "novel_insight": len(modalities_used) >= 3
        }
    
    async def process_multimodal_task(self, task: Dict) -> Dict:
        """Process a task that requires multiple modalities"""
        results = {}
        
        if "text" in task:
            results["text"] = await self.process_text(task["text"])
        
        if "code" in task:
            results["code"] = await self.process_code(task["code"])
        
        if "data" in task:
            results["data"] = await self.process_data(task["data"])
        
        # Cross-modal reasoning
        if len(results) > 1:
            results["reasoning"] = await self.cross_modal_reasoning(results)
        
        self.processed_tasks.append({
            "timestamp": datetime.now().isoformat(),
            "modalities": list(results.keys()),
            "task_id": task.get("id")
        })
        
        # Improve skills
        for modality in results.keys():
            if modality in self.modalities:
                self.modalities[modality] = min(1.0, self.modalities[modality] + 0.02)
        
        return results
    
    def get_capabilities(self) -> Dict:
        """Get agent's multimodal capabilities"""
        return {
            "agent_id": self.agent_id,
            "modalities": self.modalities,
            "cross_modal_skills": self.cross_modal_skills,
            "tasks_processed": len(self.processed_tasks)
        }


class MultiModalSwarm:
    """Swarm of agents with complementary modal strengths"""
    
    def __init__(self, num_agents: int = 20):
        self.agents = []
        
        # Create agents with different specializations
        specializations = ["text", "code", "data", "reasoning"]
        
        for i in range(num_agents):
            agent = MultiModalAgent(f"agent_{i}")
            
            # Specialize some agents
            if i < len(specializations) * 3:
                specialty = specializations[i % len(specializations)]
                agent.modalities[specialty] = 0.8
            
            self.agents.append(agent)
        
        self.task_queue = asyncio.Queue()
        self.results = []
    
    async def add_task(self, task: Dict):
        """Add multimodal task"""
        await self.task_queue.put(task)
    
    async def worker(self, agent: MultiModalAgent):
        """Worker that processes multimodal tasks"""
        while True:
            try:
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                result = await agent.process_multimodal_task(task)
                self.results.append({
                    "agent_id": agent.agent_id,
                    "task_id": task.get("id"),
                    "result": result
                })
                self.task_queue.task_done()
            except asyncio.TimeoutError:
                break
    
    async def process_tasks(self, tasks: List[Dict]):
        """Process all tasks with swarm"""
        for task in tasks:
            await self.add_task(task)
        
        workers = [asyncio.create_task(self.worker(agent)) for agent in self.agents]
        await self.task_queue.join()
        
        for w in workers:
            w.cancel()
        
        return self.results
    
    def get_swarm_capabilities(self) -> Dict:
        """Get collective capabilities"""
        all_skills = []
        modality_strengths = {"text": [], "code": [], "data": [], "reasoning": []}
        
        for agent in self.agents:
            caps = agent.get_capabilities()
            all_skills.extend(caps["cross_modal_skills"])
            
            for modality, strength in caps["modalities"].items():
                if modality in modality_strengths:
                    modality_strengths[modality].append(strength)
        
        avg_strengths = {m: sum(s)/len(s) for m, s in modality_strengths.items()}
        
        return {
            "total_agents": len(self.agents),
            "unique_cross_modal_skills": len(set(all_skills)),
            "average_modality_strengths": avg_strengths,
            "total_tasks_processed": sum(len(a.processed_tasks) for a in self.agents)
        }


class ModalityFusion:
    """Fuses information from multiple modalities for deeper understanding"""
    
    def __init__(self):
        self.fusion_patterns = []
        
    async def fuse(self, text_result: Dict, code_result: Dict, data_result: Dict) -> Dict:
        """Fuse insights from text, code, and data"""
        print("🔮 Fusing multi-modal insights...")
        
        await asyncio.sleep(0.2)
        
        # Create unified understanding
        fusion = {
            "timestamp": datetime.now().isoformat(),
            "modalities_fused": ["text", "code", "data"],
            "unified_insight": {
                "text_sentiment": text_result.get("sentiment"),
                "code_quality": code_result.get("complexity"),
                "data_trend": data_result.get("trend")
            },
            "confidence": (
                text_result.get("confidence", 0) +
                code_result.get("confidence", 0) +
                data_result.get("confidence", 0)
            ) / 3,
            "emergent_understanding": "Holistic view across all modalities"
        }
        
        self.fusion_patterns.append(fusion)
        return fusion


async def demo_multimodal_agents():
    """Demonstrate multi-modal agent capabilities"""
    print("🎨 Multi-Modal Agent System")
    print("=" * 70)
    
    # Part 1: Single agent processing multiple modalities
    print("\n📊 Part 1: Single Agent Multi-Modal Processing")
    print("-" * 70)
    
    agent = MultiModalAgent("alpha")
    
    task = {
        "id": "task_001",
        "text": "This is a complex analysis requiring deep understanding of patterns.",
        "code": "def analyze(data):\n    return sum(data) / len(data)\n",
        "data": [1.2, 2.3, 3.4, 4.5, 5.6]
    }
    
    print("\nProcessing multi-modal task...")
    result = await agent.process_multimodal_task(task)
    
    print("\n✅ Results:")
    for modality, output in result.items():
        print(f"   {modality}: {output}")
    
    # Part 2: Swarm processing
    print("\n\n🌊 Part 2: Multi-Modal Swarm Processing")
    print("-" * 70)
    
    swarm = MultiModalSwarm(num_agents=20)
    
    # Create diverse tasks
    tasks = []
    for i in range(50):
        task = {"id": f"task_{i}"}
        
        # Mix of modalities
        if random.random() < 0.7:
            task["text"] = f"Sample text for task {i}"
        if random.random() < 0.5:
            task["code"] = f"# Code for task {i}\nresult = process()\n"
        if random.random() < 0.6:
            task["data"] = [random.uniform(0, 10) for _ in range(10)]
        
        tasks.append(task)
    
    print(f"\nProcessing {len(tasks)} multi-modal tasks...")
    start_time = time.time()
    results = await swarm.process_tasks(tasks)
    duration = time.time() - start_time
    
    print(f"\n✅ Completed in {duration:.2f} seconds")
    print(f"   Tasks processed: {len(results)}")
    
    # Show swarm capabilities
    capabilities = swarm.get_swarm_capabilities()
    print(f"\n🧠 Swarm Capabilities:")
    print(f"   Total agents: {capabilities['total_agents']}")
    print(f"   Cross-modal skills developed: {capabilities['unique_cross_modal_skills']}")
    print(f"   Total tasks processed: {capabilities['total_tasks_processed']}")
    
    print(f"\n📈 Average Modality Strengths:")
    for modality, strength in capabilities['average_modality_strengths'].items():
        bar = "█" * int(strength * 30)
        print(f"   {modality:12s} {bar} {strength:.3f}")
    
    # Part 3: Modality fusion
    print("\n\n🔮 Part 3: Modality Fusion")
    print("-" * 70)
    
    fusion_engine = ModalityFusion()
    
    text_result = {"sentiment": "positive", "confidence": 0.85}
    code_result = {"complexity": "medium", "confidence": 0.78}
    data_result = {"trend": "increasing", "confidence": 0.92}
    
    fused = await fusion_engine.fuse(text_result, code_result, data_result)
    
    print("\n✨ Fused Understanding:")
    print(f"   Modalities: {', '.join(fused['modalities_fused'])}")
    print(f"   Confidence: {fused['confidence']:.3f}")
    print(f"   Insight: {fused['emergent_understanding']}")
    print(f"   Unified view: {fused['unified_insight']}")
    
    print("\n" + "=" * 70)
    print("🎉 Multi-modal demonstration complete!")
    print("\nKey insights:")
    print("  • Agents process text, code, and data seamlessly")
    print("  • Cross-modal skills emerge from integration")
    print("  • Fusion creates deeper understanding")
    print("  • Specialization + collaboration = powerful system")


if __name__ == "__main__":
    asyncio.run(demo_multimodal_agents())
