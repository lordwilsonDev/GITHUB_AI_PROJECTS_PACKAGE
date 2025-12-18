"""
Semantic Router: Task Routing via Embedding Similarity

Routes tasks to expert repositories using transformer embeddings.

Author: MoIE-OS Architecture Team
Date: 2025-12-15
Version: 1.0.0
"""

import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from transformer_core import TransformerCore


@dataclass
class ExpertProfile:
    """Profile of an expert repository with capability embeddings."""
    name: str
    repository_path: str
    capabilities: List[str]
    capability_embeddings: Optional[List[List[float]]] = None
    routing_threshold: float = 0.75


class SemanticRouter:
    """Routes tasks to expert repositories using semantic similarity."""
    
    def __init__(self, experts_config_path: str = "experts_config.json"):
        self.config_path = Path(experts_config_path)
        self.transformer_core = TransformerCore()
        self.experts: Dict[str, ExpertProfile] = {}
        
        self._load_experts()
        self._compute_capability_embeddings()
    
    def _load_experts(self):
        """Load expert profiles from config file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                experts_data = json.load(f)
                for name, data in experts_data.items():
                    self.experts[name] = ExpertProfile(**data)
        else:
            self._create_default_experts()
    
    def _create_default_experts(self):
        """Create default expert profiles for the 4 repositories."""
        default_experts = {
            "prefect-blueprint": ExpertProfile(
                name="prefect-blueprint",
                repository_path="~/prefect-blueprint",
                capabilities=[
                    "data pipeline orchestration",
                    "ETL workflows",
                    "data validation and quality checks"
                ],
                routing_threshold=0.75
            ),
            "love-engine-real": ExpertProfile(
                name="love-engine-real",
                repository_path="~/love-engine-real",
                capabilities=[
                    "energy system optimization",
                    "constraint satisfaction",
                    "safety-critical systems"
                ],
                routing_threshold=0.75
            ),
            "system-dashboard": ExpertProfile(
                name="system-dashboard",
                repository_path="~/system-dashboard",
                capabilities=[
                    "data visualization",
                    "dashboard creation",
                    "reporting and analytics"
                ],
                routing_threshold=0.75
            ),
            "nanoapex-rade": ExpertProfile(
                name="nanoapex-rade",
                repository_path="~/nanoapex-rade",
                capabilities=[
                    "autonomous agent development",
                    "code generation and synthesis",
                    "recursive self-improvement"
                ],
                routing_threshold=0.75
            )
        }
        
        self.experts = default_experts
        
        with open(self.config_path, 'w') as f:
            json.dump({k: asdict(v) for k, v in default_experts.items()}, f, indent=2)
    
    def _compute_capability_embeddings(self):
        """Precompute embeddings for all expert capabilities."""
        print("Computing capability embeddings for all experts...")
        
        for expert_name, expert in self.experts.items():
            if expert.capability_embeddings is None:
                embeddings = []
                for capability in expert.capabilities:
                    emb = self.transformer_core.get_embedding(capability)
                    if emb:
                        embeddings.append(emb)
                
                expert.capability_embeddings = embeddings
                print(f"  ✅ {expert_name}: {len(embeddings)} capabilities embedded")
    
    def route_task(self, task_description: str) -> Tuple[Optional[str], float, Dict]:
        """Route a task to the most appropriate expert."""
        task_embedding = self.transformer_core.get_embedding(task_description)
        if not task_embedding:
            return None, 0.0, {"error": "Failed to embed task"}
        
        expert_scores = {}
        
        for expert_name, expert in self.experts.items():
            if not expert.capability_embeddings:
                continue
            
            similarities = []
            for cap_emb in expert.capability_embeddings:
                sim = self._cosine_similarity(task_embedding, cap_emb)
                similarities.append(sim)
            
            max_sim = max(similarities) if similarities else 0.0
            expert_scores[expert_name] = max_sim
        
        if not expert_scores:
            return None, 0.0, {"error": "No experts available"}
        
        best_expert = max(expert_scores, key=expert_scores.get)
        best_score = expert_scores[best_expert]
        
        threshold = self.experts[best_expert].routing_threshold
        
        routing_details = {
            "task": task_description,
            "all_scores": expert_scores,
            "threshold": threshold,
            "passed_threshold": best_score >= threshold
        }
        
        if best_score >= threshold:
            return best_expert, best_score, routing_details
        else:
            return None, best_score, routing_details
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        
        dot_product = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def route(self, task_description: str):
        """Route a task (alias for route_task, test contract method)"""
        return self.route_task(task_description)


if __name__ == "__main__":
    print("=== Semantic Router Demo ===")
    
    router = SemanticRouter()
    
    print("\nExperts loaded:")
    for name, expert in router.experts.items():
        print(f"  - {name}: {len(expert.capabilities)} capabilities")
    
    test_tasks = [
        "Build a data pipeline to process customer transactions",
        "Create a dashboard to visualize sales metrics",
        "Optimize energy consumption with safety constraints",
        "Generate code for a recursive learning agent"
    ]
    
    print("\nTesting task routing:")
    for task in test_tasks:
        expert, score, details = router.route_task(task)
        print(f"\nTask: {task}")
        print(f"  → Routed to: {expert} (score: {score:.3f})")

    def route(self, task_description: str):
        """Route a task (alias for route_task, test contract method)"""
        return self.route_task(task_description)
