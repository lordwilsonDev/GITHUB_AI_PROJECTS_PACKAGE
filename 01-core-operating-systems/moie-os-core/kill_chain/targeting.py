"""Stage 1: Targeting - Invert the problem and build search manifest."""

from typing import List
from ..core.models import KillChainInput, SearchManifest


class TargetingStage:
    """
    Targeting stage inverts the problem.
    
    Instead of "How do I solve X?", ask:
    - "What must be true for X to be trivial?"
    - "What would make this problem disappear?"
    - "What am I assuming that might be wrong?"
    """
    
    def execute(self, input_data: KillChainInput) -> SearchManifest:
        """
        Execute targeting stage.
        
        Args:
            input_data: Kill Chain input
        
        Returns:
            SearchManifest with inverted questions
        """
        problem = input_data.problem_statement
        
        # Generate inverse questions
        inverse_questions = self._generate_inverse_questions(problem)
        
        # Identify conditions for trivial solution
        must_be_true = self._identify_trivial_conditions(problem, input_data.context)
        
        # Generate search paths
        search_paths = self._generate_search_paths(problem, input_data.constraints)
        
        # Identify anti-patterns
        anti_patterns = self._identify_anti_patterns(problem)
        
        return SearchManifest(
            inverse_questions=inverse_questions,
            must_be_true=must_be_true,
            search_paths=search_paths,
            anti_patterns=anti_patterns,
        )
    
    def _generate_inverse_questions(self, problem: str) -> List[str]:
        """
        Generate questions that invert the problem.
        
        Args:
            problem: Problem statement
        
        Returns:
            List of inverse questions
        """
        questions = [
            f"What must be true for '{problem}' to be trivial?",
            f"What would make '{problem}' disappear entirely?",
            f"What am I assuming about '{problem}' that might be wrong?",
            f"What is the opposite of '{problem}' and why might that be better?",
            f"If '{problem}' were already solved, what would that look like?",
        ]
        
        # Add context-specific inversions
        if "optimize" in problem.lower():
            questions.append("What if we removed complexity instead of adding optimization?")
        
        if "build" in problem.lower():
            questions.append("What existing solution could we adapt instead of building?")
        
        if "fix" in problem.lower():
            questions.append("What if we prevented the problem instead of fixing it?")
        
        return questions
    
    def _identify_trivial_conditions(self, problem: str, context: dict) -> List[str]:
        """
        Identify conditions that would make the problem trivial.
        
        Args:
            problem: Problem statement
            context: Additional context
        
        Returns:
            List of conditions
        """
        conditions = []
        
        # Generic conditions
        conditions.append("The problem is already solved by an existing tool")
        conditions.append("The problem doesn't actually need to be solved")
        conditions.append("The constraints can be relaxed")
        
        # Context-specific conditions
        if "ram" in context or "memory" in problem.lower():
            conditions.append("Memory is unlimited")
            conditions.append("The workload fits in available memory")
        
        if "performance" in problem.lower() or "optimize" in problem.lower():
            conditions.append("The current performance is already acceptable")
            conditions.append("The bottleneck is elsewhere")
        
        return conditions
    
    def _generate_search_paths(self, problem: str, constraints: List[str]) -> List[str]:
        """
        Generate paths to explore.
        
        Args:
            problem: Problem statement
            constraints: Hard constraints
        
        Returns:
            List of search paths
        """
        paths = [
            "Via negativa: What can we remove?",
            "Positive deviants: Who solved this differently?",
            "First principles: What are the fundamental constraints?",
            "Inversion: What if we did the opposite?",
        ]
        
        # Add constraint-aware paths
        if constraints:
            paths.append(f"Constraint relaxation: Can we negotiate {len(constraints)} constraints?")
        
        return paths
    
    def _identify_anti_patterns(self, problem: str) -> List[str]:
        """
        Identify what NOT to do.
        
        Args:
            problem: Problem statement
        
        Returns:
            List of anti-patterns
        """
        anti_patterns = [
            "Don't add complexity before removing it",
            "Don't optimize before measuring",
            "Don't build before searching for existing solutions",
            "Don't assume the problem statement is correct",
        ]
        
        if "optimize" in problem.lower():
            anti_patterns.append("Don't micro-optimize before profiling")
        
        if "scale" in problem.lower():
            anti_patterns.append("Don't scale before validating the core works")
        
        return anti_patterns
