#!/usr/bin/env python3
"""
T-072: Creative Problem Solver

Novel solution generation, out-of-distribution thinking, and creative synthesis.

Key Features:
- Generate novel solutions to problems
- Think outside conventional patterns
- Synthesize creative approaches
- Combine disparate concepts
"""

import json
import random
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class CreativityTechnique(Enum):
    """Techniques for creative problem solving"""
    ANALOGY = "analogy"  # Draw from other domains
    INVERSION = "inversion"  # Flip assumptions
    COMBINATION = "combination"  # Merge concepts
    ABSTRACTION = "abstraction"  # Generalize patterns
    RANDOMIZATION = "randomization"  # Introduce randomness
    CONSTRAINT_REMOVAL = "constraint_removal"  # Remove limitations
    PERSPECTIVE_SHIFT = "perspective_shift"  # Change viewpoint


class SolutionNovelty(Enum):
    """Novelty levels for solutions"""
    CONVENTIONAL = "conventional"  # Standard approach
    INCREMENTAL = "incremental"  # Small variation
    NOVEL = "novel"  # New approach
    BREAKTHROUGH = "breakthrough"  # Paradigm shift


@dataclass
class Problem:
    """Represents a problem to solve"""
    description: str
    domain: str
    constraints: List[str]
    objectives: List[str]
    context: Dict[str, Any]


@dataclass
class Solution:
    """Represents a creative solution"""
    problem_description: str
    approach: str
    technique: CreativityTechnique
    novelty: SolutionNovelty
    components: List[str]
    rationale: str
    potential_impact: float  # 0.0 to 1.0
    feasibility: float  # 0.0 to 1.0
    timestamp: str


@dataclass
class CreativeConcept:
    """A creative concept or idea"""
    name: str
    description: str
    source_domains: List[str]
    synthesis_method: str
    applications: List[str]
    originality_score: float  # 0.0 to 1.0


class CreativeSolver:
    """
    Creative problem solver that generates novel solutions.
    Uses various creativity techniques to think outside conventional patterns.
    """
    
    def __init__(self):
        self.solutions: List[Solution] = []
        self.concepts: List[CreativeConcept] = []
        self.knowledge_base: Dict[str, List[str]] = self._initialize_knowledge()
        self.creativity_history: List[Dict[str, Any]] = []
        
    def _initialize_knowledge(self) -> Dict[str, List[str]]:
        """Initialize knowledge base with cross-domain concepts"""
        return {
            "nature": ["evolution", "adaptation", "symbiosis", "emergence", "self-organization"],
            "technology": ["modularity", "abstraction", "recursion", "parallelism", "feedback"],
            "art": ["composition", "contrast", "harmony", "rhythm", "perspective"],
            "science": ["hypothesis", "experiment", "observation", "theory", "validation"],
            "business": ["optimization", "efficiency", "scalability", "innovation", "collaboration"],
            "philosophy": ["dialectic", "synthesis", "deconstruction", "emergence", "holism"]
        }
    
    def solve_creatively(self, problem: Problem, 
                        technique: CreativityTechnique = CreativityTechnique.COMBINATION) -> Solution:
        """
        Generate a creative solution to a problem.
        
        Args:
            problem: Problem to solve
            technique: Creativity technique to use
            
        Returns:
            Creative solution
        """
        print(f"\n🎨 Applying {technique.value} technique...")
        
        if technique == CreativityTechnique.ANALOGY:
            solution = self._solve_by_analogy(problem)
        elif technique == CreativityTechnique.INVERSION:
            solution = self._solve_by_inversion(problem)
        elif technique == CreativityTechnique.COMBINATION:
            solution = self._solve_by_combination(problem)
        elif technique == CreativityTechnique.ABSTRACTION:
            solution = self._solve_by_abstraction(problem)
        elif technique == CreativityTechnique.RANDOMIZATION:
            solution = self._solve_by_randomization(problem)
        elif technique == CreativityTechnique.CONSTRAINT_REMOVAL:
            solution = self._solve_by_constraint_removal(problem)
        else:  # PERSPECTIVE_SHIFT
            solution = self._solve_by_perspective_shift(problem)
        
        self.solutions.append(solution)
        self._record_creativity(problem, solution, technique)
        
        return solution
    
    def _solve_by_analogy(self, problem: Problem) -> Solution:
        """Solve by drawing analogies from other domains"""
        # Pick a random domain different from problem domain
        other_domains = [d for d in self.knowledge_base.keys() if d != problem.domain]
        source_domain = random.choice(other_domains) if other_domains else "nature"
        concepts = self.knowledge_base[source_domain]
        
        approach = f"Apply {source_domain} concept of '{random.choice(concepts)}' to {problem.domain}"
        
        return Solution(
            problem_description=problem.description,
            approach=approach,
            technique=CreativityTechnique.ANALOGY,
            novelty=SolutionNovelty.NOVEL,
            components=[source_domain, problem.domain],
            rationale=f"Cross-domain analogy from {source_domain} provides fresh perspective",
            potential_impact=0.7,
            feasibility=0.6,
            timestamp=datetime.now().isoformat()
        )
    
    def _solve_by_inversion(self, problem: Problem) -> Solution:
        """Solve by inverting assumptions"""
        approach = f"Invert core assumption: Instead of {problem.objectives[0] if problem.objectives else 'solving directly'}, do the opposite first"
        
        return Solution(
            problem_description=problem.description,
            approach=approach,
            technique=CreativityTechnique.INVERSION,
            novelty=SolutionNovelty.BREAKTHROUGH,
            components=["inverted_logic", "paradoxical_approach"],
            rationale="Inverting assumptions often reveals hidden solutions",
            potential_impact=0.8,
            feasibility=0.5,
            timestamp=datetime.now().isoformat()
        )
    
    def _solve_by_combination(self, problem: Problem) -> Solution:
        """Solve by combining multiple concepts"""
        # Combine concepts from multiple domains
        domains = random.sample(list(self.knowledge_base.keys()), min(3, len(self.knowledge_base)))
        concepts = [random.choice(self.knowledge_base[d]) for d in domains]
        
        approach = f"Synthesize solution by combining: {', '.join(concepts)}"
        
        return Solution(
            problem_description=problem.description,
            approach=approach,
            technique=CreativityTechnique.COMBINATION,
            novelty=SolutionNovelty.NOVEL,
            components=concepts,
            rationale="Combining disparate concepts creates emergent solutions",
            potential_impact=0.75,
            feasibility=0.7,
            timestamp=datetime.now().isoformat()
        )
    
    def _solve_by_abstraction(self, problem: Problem) -> Solution:
        """Solve by abstracting to higher level"""
        approach = f"Abstract {problem.description} to general pattern, solve at meta-level, then specialize"
        
        return Solution(
            problem_description=problem.description,
            approach=approach,
            technique=CreativityTechnique.ABSTRACTION,
            novelty=SolutionNovelty.INCREMENTAL,
            components=["pattern_recognition", "meta_solution", "specialization"],
            rationale="Abstraction reveals underlying patterns applicable across domains",
            potential_impact=0.65,
            feasibility=0.8,
            timestamp=datetime.now().isoformat()
        )
    
    def _solve_by_randomization(self, problem: Problem) -> Solution:
        """Solve by introducing controlled randomness"""
        random_elements = random.sample(
            [c for concepts in self.knowledge_base.values() for c in concepts],
            3
        )
        
        approach = f"Inject random elements ({', '.join(random_elements)}) to break conventional thinking"
        
        return Solution(
            problem_description=problem.description,
            approach=approach,
            technique=CreativityTechnique.RANDOMIZATION,
            novelty=SolutionNovelty.BREAKTHROUGH,
            components=random_elements,
            rationale="Randomness disrupts mental patterns and enables discovery",
            potential_impact=0.6,
            feasibility=0.4,
            timestamp=datetime.now().isoformat()
        )
    
    def _solve_by_constraint_removal(self, problem: Problem) -> Solution:
        """Solve by removing constraints"""
        removed_constraint = problem.constraints[0] if problem.constraints else "resource limitation"
        approach = f"Remove constraint '{removed_constraint}' and solve ideally, then adapt back"
        
        return Solution(
            problem_description=problem.description,
            approach=approach,
            technique=CreativityTechnique.CONSTRAINT_REMOVAL,
            novelty=SolutionNovelty.NOVEL,
            components=["ideal_solution", "constraint_adaptation"],
            rationale="Removing constraints reveals ideal solutions that can be approximated",
            potential_impact=0.7,
            feasibility=0.6,
            timestamp=datetime.now().isoformat()
        )
    
    def _solve_by_perspective_shift(self, problem: Problem) -> Solution:
        """Solve by shifting perspective"""
        perspectives = ["user", "system", "observer", "future_self", "competitor"]
        perspective = random.choice(perspectives)
        
        approach = f"View problem from {perspective} perspective and solve from that viewpoint"
        
        return Solution(
            problem_description=problem.description,
            approach=approach,
            technique=CreativityTechnique.PERSPECTIVE_SHIFT,
            novelty=SolutionNovelty.INCREMENTAL,
            components=[perspective, "empathy", "reframing"],
            rationale="Different perspectives reveal different solution spaces",
            potential_impact=0.65,
            feasibility=0.75,
            timestamp=datetime.now().isoformat()
        )
    
    def _record_creativity(self, problem: Problem, solution: Solution, 
                          technique: CreativityTechnique) -> None:
        """Record creative problem-solving session"""
        self.creativity_history.append({
            "problem": problem.description,
            "technique": technique.value,
            "novelty": solution.novelty.value,
            "impact": solution.potential_impact,
            "timestamp": solution.timestamp
        })
    
    def synthesize_concept(self, source_domains: List[str], 
                          synthesis_method: str = "fusion") -> CreativeConcept:
        """
        Synthesize a creative concept from multiple domains.
        
        Args:
            source_domains: Domains to draw from
            synthesis_method: Method for synthesis
            
        Returns:
            Creative concept
        """
        # Gather concepts from source domains
        source_concepts = []
        for domain in source_domains:
            if domain in self.knowledge_base:
                source_concepts.extend(self.knowledge_base[domain][:2])
        
        concept_name = f"Synthesized_{len(self.concepts) + 1}"
        
        concept = CreativeConcept(
            name=concept_name,
            description=f"Novel concept combining {', '.join(source_domains)}",
            source_domains=source_domains,
            synthesis_method=synthesis_method,
            applications=[
                f"Apply to {domain} problems" for domain in source_domains
            ],
            originality_score=min(0.9, 0.3 + 0.2 * len(source_domains))
        )
        
        self.concepts.append(concept)
        print(f"✨ Synthesized concept: {concept_name} (originality: {concept.originality_score:.2f})")
        
        return concept
    
    def generate_multiple_solutions(self, problem: Problem, 
                                   count: int = 5) -> List[Solution]:
        """
        Generate multiple creative solutions using different techniques.
        
        Args:
            problem: Problem to solve
            count: Number of solutions to generate
            
        Returns:
            List of solutions
        """
        techniques = list(CreativityTechnique)
        solutions = []
        
        for i in range(min(count, len(techniques))):
            solution = self.solve_creatively(problem, techniques[i])
            solutions.append(solution)
        
        return solutions
    
    def get_creativity_report(self) -> Dict[str, Any]:
        """
        Generate creativity report.
        
        Returns:
            Report with solutions, concepts, and statistics
        """
        novelty_distribution = {}
        for solution in self.solutions:
            novelty = solution.novelty.value
            novelty_distribution[novelty] = novelty_distribution.get(novelty, 0) + 1
        
        return {
            "total_solutions": len(self.solutions),
            "total_concepts": len(self.concepts),
            "novelty_distribution": novelty_distribution,
            "average_impact": sum(s.potential_impact for s in self.solutions) / len(self.solutions) if self.solutions else 0,
            "average_feasibility": sum(s.feasibility for s in self.solutions) / len(self.solutions) if self.solutions else 0,
            "creativity_sessions": len(self.creativity_history),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_solutions(self, problem: Problem, count: int = 3) -> List[Solution]:
        """
        Generate multiple creative solutions to a problem.
        
        Args:
            problem: Problem to solve
            count: Number of solutions to generate
            
        Returns:
            List of creative solutions
        """
        solutions = []
        techniques = list(CreativityTechnique)
        
        for i in range(count):
            technique = techniques[i % len(techniques)]
            solution = self.solve_creatively(problem, technique)
            solutions.append(solution)
        
        return solutions
    
    def demo(self) -> Dict[str, Any]:
        """Demonstrate creative problem solving"""
        print("\n" + "="*60)
        print("🎨 Creative Problem Solver Demo")
        print("="*60 + "\n")
        
        # Define a problem
        problem = Problem(
            description="Improve system performance while reducing resource usage",
            domain="technology",
            constraints=["limited memory", "CPU budget", "backward compatibility"],
            objectives=["increase throughput", "reduce latency", "lower costs"],
            context={"current_performance": 100, "target_performance": 200}
        )
        
        print(f"📋 Problem: {problem.description}")
        print(f"   Domain: {problem.domain}")
        print(f"   Constraints: {', '.join(problem.constraints)}")
        print()
        
        # Generate multiple creative solutions
        print("🔮 Generating creative solutions...")
        solutions = self.generate_multiple_solutions(problem, count=5)
        
        print(f"\n💡 Generated {len(solutions)} solutions:")
        for i, sol in enumerate(solutions, 1):
            print(f"\n   Solution {i}: {sol.technique.value}")
            print(f"   Approach: {sol.approach}")
            print(f"   Novelty: {sol.novelty.value}")
            print(f"   Impact: {sol.potential_impact:.2f} | Feasibility: {sol.feasibility:.2f}")
        
        # Synthesize creative concepts
        print("\n🔬 Synthesizing creative concepts...")
        concept1 = self.synthesize_concept(["nature", "technology"], "biomimicry")
        concept2 = self.synthesize_concept(["art", "science", "philosophy"], "transdisciplinary")
        
        # Generate report
        report = self.get_creativity_report()
        print(f"\n📊 Creativity Summary:")
        print(f"   Total solutions: {report['total_solutions']}")
        print(f"   Total concepts: {report['total_concepts']}")
        print(f"   Average impact: {report['average_impact']:.2f}")
        print(f"   Average feasibility: {report['average_feasibility']:.2f}")
        print(f"   Novelty distribution: {report['novelty_distribution']}")
        
        return report


class CreativeSolverContract:
    """Contract interface for testing"""
    
    @staticmethod
    def test() -> bool:
        """Test creative solver functionality"""
        solver = CreativeSolver()
        
        # Test problem creation
        problem = Problem(
            description="Test problem",
            domain="test",
            constraints=["constraint1"],
            objectives=["objective1"],
            context={}
        )
        
        # Test solution generation
        solution = solver.solve_creatively(problem, CreativityTechnique.COMBINATION)
        assert solution.approach is not None, "Should generate solution"
        assert solution.novelty in SolutionNovelty, "Should have novelty level"
        
        # Test concept synthesis
        concept = solver.synthesize_concept(["nature", "technology"])
        assert concept.name is not None, "Should create concept"
        assert len(concept.source_domains) == 2, "Should combine domains"
        
        # Test multiple solutions
        solutions = solver.generate_multiple_solutions(problem, count=3)
        assert len(solutions) == 3, "Should generate multiple solutions"
        
        # Test report generation
        report = solver.get_creativity_report()
        assert "total_solutions" in report, "Should generate report"
        assert report["total_solutions"] >= 4, "Should track all solutions"
        
        return True


if __name__ == "__main__":
    # Run demo
    solver = CreativeSolver()
    report = solver.demo()
    
    # Save report
    with open("creative_solutions_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n✅ Report saved to creative_solutions_report.json")
