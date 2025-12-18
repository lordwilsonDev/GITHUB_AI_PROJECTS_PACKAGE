"""
Methodology Analyzer

This module provides a comprehensive system for learning, analyzing, and recommending
software development methodologies, best practices, and workflows.

Author: Vy Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Tuple
from pathlib import Path


class MethodologyType(Enum):
    """Types of software development methodologies."""
    AGILE = "agile"
    SCRUM = "scrum"
    KANBAN = "kanban"
    WATERFALL = "waterfall"
    DEVOPS = "devops"
    LEAN = "lean"
    XP = "extreme_programming"
    SPIRAL = "spiral"
    RAD = "rapid_application_development"
    FEATURE_DRIVEN = "feature_driven_development"
    CRYSTAL = "crystal"
    SAFE = "scaled_agile_framework"


class PracticeCategory(Enum):
    """Categories of software development practices."""
    PLANNING = "planning"
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    COLLABORATION = "collaboration"
    DOCUMENTATION = "documentation"
    CODE_REVIEW = "code_review"
    CONTINUOUS_INTEGRATION = "continuous_integration"
    CONTINUOUS_DELIVERY = "continuous_delivery"


class EffectivenessLevel(Enum):
    """Effectiveness levels for practices and methodologies."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


class TeamSize(Enum):
    """Team size categories."""
    SMALL = "small"  # 1-5 people
    MEDIUM = "medium"  # 6-15 people
    LARGE = "large"  # 16-50 people
    ENTERPRISE = "enterprise"  # 50+ people


class ProjectComplexity(Enum):
    """Project complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


@dataclass
class Principle:
    """Represents a methodology principle."""
    principle_id: str
    name: str
    description: str
    importance: str  # critical, important, nice_to_have
    examples: List[str] = field(default_factory=list)


@dataclass
class BestPractice:
    """Represents a best practice."""
    practice_id: str
    name: str
    category: str
    description: str
    benefits: List[str]
    implementation_steps: List[str]
    prerequisites: List[str] = field(default_factory=list)
    tools_required: List[str] = field(default_factory=list)
    effectiveness: str = EffectivenessLevel.MEDIUM.value
    applicable_methodologies: List[str] = field(default_factory=list)
    team_size_fit: List[str] = field(default_factory=list)
    complexity_fit: List[str] = field(default_factory=list)
    adoption_difficulty: str = "medium"  # easy, medium, hard
    time_to_value: str = "medium"  # immediate, short, medium, long
    learned_at: str = field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 0
    success_rate: float = 0.0


@dataclass
class AntiPattern:
    """Represents an anti-pattern to avoid."""
    pattern_id: str
    name: str
    description: str
    symptoms: List[str]
    consequences: List[str]
    solutions: List[str]
    related_practices: List[str] = field(default_factory=list)
    severity: str = "medium"  # low, medium, high, critical
    detection_difficulty: str = "medium"  # easy, medium, hard
    identified_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Workflow:
    """Represents a workflow or process."""
    workflow_id: str
    name: str
    methodology: str
    description: str
    phases: List[Dict[str, any]]
    roles: List[str]
    artifacts: List[str]
    ceremonies: List[Dict[str, any]] = field(default_factory=list)
    metrics: List[str] = field(default_factory=list)
    effectiveness: float = 0.0
    team_size: str = TeamSize.MEDIUM.value
    complexity: str = ProjectComplexity.MODERATE.value
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_used: Optional[str] = None
    usage_count: int = 0


@dataclass
class Methodology:
    """Represents a software development methodology."""
    methodology_id: str
    name: str
    type: str
    description: str
    principles: List[Principle]
    core_practices: List[str]
    values: List[str]
    strengths: List[str]
    weaknesses: List[str]
    best_for: List[str]
    not_recommended_for: List[str]
    team_size_fit: List[str]
    complexity_fit: List[str]
    typical_workflows: List[str] = field(default_factory=list)
    required_roles: List[str] = field(default_factory=list)
    key_metrics: List[str] = field(default_factory=list)
    adoption_difficulty: str = "medium"
    maturity_level: str = "mature"
    popularity_score: float = 0.5
    effectiveness_score: float = 0.0
    learned_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 0


@dataclass
class MethodologyComparison:
    """Comparison between methodologies."""
    comparison_id: str
    methodologies: List[str]
    criteria: Dict[str, Dict[str, float]]  # criterion -> {methodology: score}
    context: Dict[str, any]
    recommendation: str
    reasoning: str
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class MethodologyAnalyzer:
    """Main class for analyzing and recommending software development methodologies."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/methodology_analysis"):
        """Initialize the methodology analyzer."""
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.methodologies: Dict[str, Methodology] = {}
        self.best_practices: Dict[str, BestPractice] = {}
        self.anti_patterns: Dict[str, AntiPattern] = {}
        self.workflows: Dict[str, Workflow] = {}
        self.comparisons: Dict[str, MethodologyComparison] = {}
        
        self._load_data()
        self._initialize_base_knowledge()
    
    def _load_data(self):
        """Load data from JSON files."""
        # Load methodologies
        methodologies_file = self.data_dir / "methodologies.json"
        if methodologies_file.exists():
            with open(methodologies_file, 'r') as f:
                data = json.load(f)
                self.methodologies = {
                    k: Methodology(**v) for k, v in data.items()
                }
        
        # Load best practices
        practices_file = self.data_dir / "best_practices.json"
        if practices_file.exists():
            with open(practices_file, 'r') as f:
                data = json.load(f)
                self.best_practices = {
                    k: BestPractice(**v) for k, v in data.items()
                }
        
        # Load anti-patterns
        antipatterns_file = self.data_dir / "anti_patterns.json"
        if antipatterns_file.exists():
            with open(antipatterns_file, 'r') as f:
                data = json.load(f)
                self.anti_patterns = {
                    k: AntiPattern(**v) for k, v in data.items()
                }
        
        # Load workflows
        workflows_file = self.data_dir / "workflows.json"
        if workflows_file.exists():
            with open(workflows_file, 'r') as f:
                data = json.load(f)
                self.workflows = {
                    k: Workflow(**v) for k, v in data.items()
                }
        
        # Load comparisons
        comparisons_file = self.data_dir / "comparisons.json"
        if comparisons_file.exists():
            with open(comparisons_file, 'r') as f:
                data = json.load(f)
                self.comparisons = {
                    k: MethodologyComparison(**v) for k, v in data.items()
                }
    
    def _save_data(self):
        """Save data to JSON files."""
        # Save methodologies
        with open(self.data_dir / "methodologies.json", 'w') as f:
            json.dump(
                {k: asdict(v) for k, v in self.methodologies.items()},
                f, indent=2
            )
        
        # Save best practices
        with open(self.data_dir / "best_practices.json", 'w') as f:
            json.dump(
                {k: asdict(v) for k, v in self.best_practices.items()},
                f, indent=2
            )
        
        # Save anti-patterns
        with open(self.data_dir / "anti_patterns.json", 'w') as f:
            json.dump(
                {k: asdict(v) for k, v in self.anti_patterns.items()},
                f, indent=2
            )
        
        # Save workflows
        with open(self.data_dir / "workflows.json", 'w') as f:
            json.dump(
                {k: asdict(v) for k, v in self.workflows.items()},
                f, indent=2
            )
        
        # Save comparisons
        with open(self.data_dir / "comparisons.json", 'w') as f:
            json.dump(
                {k: asdict(v) for k, v in self.comparisons.items()},
                f, indent=2
            )
    
    def _initialize_base_knowledge(self):
        """Initialize with base knowledge of common methodologies."""
        if not self.methodologies:
            # Add Scrum
            self.learn_methodology(
                name="Scrum",
                methodology_type=MethodologyType.SCRUM.value,
                description="Iterative and incremental agile framework",
                principles=[
                    {"name": "Transparency", "description": "All aspects visible to those responsible", "importance": "critical"},
                    {"name": "Inspection", "description": "Regular inspection of artifacts", "importance": "critical"},
                    {"name": "Adaptation", "description": "Adjust process based on inspection", "importance": "critical"}
                ],
                values=["Commitment", "Courage", "Focus", "Openness", "Respect"],
                strengths=["Clear roles", "Regular feedback", "Adaptable", "Team collaboration"],
                weaknesses=["Requires discipline", "Can be rigid", "Overhead for small teams"],
                best_for=["Complex projects", "Changing requirements", "Cross-functional teams"],
                team_size_fit=[TeamSize.SMALL.value, TeamSize.MEDIUM.value]
            )
            
            # Add Kanban
            self.learn_methodology(
                name="Kanban",
                methodology_type=MethodologyType.KANBAN.value,
                description="Visual workflow management method",
                principles=[
                    {"name": "Visualize work", "description": "Make work visible on board", "importance": "critical"},
                    {"name": "Limit WIP", "description": "Limit work in progress", "importance": "critical"},
                    {"name": "Manage flow", "description": "Optimize flow of work", "importance": "important"}
                ],
                values=["Transparency", "Balance", "Collaboration", "Customer focus", "Flow"],
                strengths=["Flexible", "Visual", "Continuous delivery", "Easy to adopt"],
                weaknesses=["Less structure", "Requires discipline", "Can lack planning"],
                best_for=["Continuous flow", "Support teams", "Maintenance work"],
                team_size_fit=[TeamSize.SMALL.value, TeamSize.MEDIUM.value, TeamSize.LARGE.value]
            )
    
    def learn_methodology(
        self,
        name: str,
        methodology_type: str,
        description: str,
        principles: List[Dict],
        values: List[str],
        strengths: List[str],
        weaknesses: List[str],
        best_for: List[str],
        team_size_fit: List[str],
        not_recommended_for: List[str] = None,
        complexity_fit: List[str] = None,
        core_practices: List[str] = None,
        required_roles: List[str] = None
    ) -> Methodology:
        """Learn a new methodology."""
        methodology_id = f"methodology_{len(self.methodologies) + 1}"
        
        # Convert principle dicts to Principle objects
        principle_objects = [
            Principle(
                principle_id=f"{methodology_id}_principle_{i}",
                name=p['name'],
                description=p['description'],
                importance=p.get('importance', 'important'),
                examples=p.get('examples', [])
            )
            for i, p in enumerate(principles)
        ]
        
        methodology = Methodology(
            methodology_id=methodology_id,
            name=name,
            type=methodology_type,
            description=description,
            principles=principle_objects,
            core_practices=core_practices or [],
            values=values,
            strengths=strengths,
            weaknesses=weaknesses,
            best_for=best_for,
            not_recommended_for=not_recommended_for or [],
            team_size_fit=team_size_fit,
            complexity_fit=complexity_fit or [ProjectComplexity.MODERATE.value, ProjectComplexity.COMPLEX.value],
            required_roles=required_roles or []
        )
        
        self.methodologies[methodology_id] = methodology
        self._save_data()
        return methodology
    
    def learn_best_practice(
        self,
        name: str,
        category: str,
        description: str,
        benefits: List[str],
        implementation_steps: List[str],
        applicable_methodologies: List[str] = None,
        prerequisites: List[str] = None,
        tools_required: List[str] = None,
        effectiveness: str = EffectivenessLevel.MEDIUM.value
    ) -> BestPractice:
        """Learn a new best practice."""
        practice_id = f"practice_{len(self.best_practices) + 1}"
        
        practice = BestPractice(
            practice_id=practice_id,
            name=name,
            category=category,
            description=description,
            benefits=benefits,
            implementation_steps=implementation_steps,
            applicable_methodologies=applicable_methodologies or [],
            prerequisites=prerequisites or [],
            tools_required=tools_required or [],
            effectiveness=effectiveness
        )
        
        self.best_practices[practice_id] = practice
        self._save_data()
        return practice
    
    def identify_anti_pattern(
        self,
        name: str,
        description: str,
        symptoms: List[str],
        consequences: List[str],
        solutions: List[str],
        severity: str = "medium"
    ) -> AntiPattern:
        """Identify and record an anti-pattern."""
        pattern_id = f"antipattern_{len(self.anti_patterns) + 1}"
        
        anti_pattern = AntiPattern(
            pattern_id=pattern_id,
            name=name,
            description=description,
            symptoms=symptoms,
            consequences=consequences,
            solutions=solutions,
            severity=severity
        )
        
        self.anti_patterns[pattern_id] = anti_pattern
        self._save_data()
        return anti_pattern
    
    def create_workflow(
        self,
        name: str,
        methodology: str,
        description: str,
        phases: List[Dict],
        roles: List[str],
        artifacts: List[str],
        ceremonies: List[Dict] = None,
        team_size: str = TeamSize.MEDIUM.value,
        complexity: str = ProjectComplexity.MODERATE.value
    ) -> Workflow:
        """Create a workflow template."""
        workflow_id = f"workflow_{len(self.workflows) + 1}"
        
        workflow = Workflow(
            workflow_id=workflow_id,
            name=name,
            methodology=methodology,
            description=description,
            phases=phases,
            roles=roles,
            artifacts=artifacts,
            ceremonies=ceremonies or [],
            team_size=team_size,
            complexity=complexity
        )
        
        self.workflows[workflow_id] = workflow
        self._save_data()
        return workflow
    
    def compare_methodologies(
        self,
        methodology_names: List[str],
        context: Dict[str, any],
        criteria: List[str] = None
    ) -> MethodologyComparison:
        """Compare multiple methodologies for a given context."""
        if criteria is None:
            criteria = [
                'flexibility', 'structure', 'team_collaboration',
                'documentation', 'speed_to_market', 'quality_focus',
                'scalability', 'ease_of_adoption'
            ]
        
        # Find methodologies
        methodologies_to_compare = []
        for name in methodology_names:
            for m in self.methodologies.values():
                if m.name.lower() == name.lower():
                    methodologies_to_compare.append(m)
                    break
        
        if len(methodologies_to_compare) < 2:
            raise ValueError("Need at least 2 methodologies to compare")
        
        # Score each methodology on each criterion
        scores = {}
        for criterion in criteria:
            scores[criterion] = {}
            for methodology in methodologies_to_compare:
                score = self._score_methodology(methodology, criterion, context)
                scores[criterion][methodology.name] = score
        
        # Calculate overall scores
        overall_scores = {}
        for methodology in methodologies_to_compare:
            total = sum(scores[c][methodology.name] for c in criteria)
            overall_scores[methodology.name] = total / len(criteria)
        
        # Determine recommendation
        recommended = max(overall_scores, key=overall_scores.get)
        
        # Generate reasoning
        reasoning = self._generate_comparison_reasoning(
            methodologies_to_compare, scores, overall_scores, context
        )
        
        comparison_id = f"comparison_{len(self.comparisons) + 1}"
        comparison = MethodologyComparison(
            comparison_id=comparison_id,
            methodologies=[m.name for m in methodologies_to_compare],
            criteria=scores,
            context=context,
            recommendation=recommended,
            reasoning=reasoning
        )
        
        self.comparisons[comparison_id] = comparison
        self._save_data()
        return comparison
    
    def _score_methodology(
        self,
        methodology: Methodology,
        criterion: str,
        context: Dict[str, any]
    ) -> float:
        """Score a methodology on a specific criterion."""
        score = 0.5  # Base score
        
        team_size = context.get('team_size', TeamSize.MEDIUM.value)
        complexity = context.get('complexity', ProjectComplexity.MODERATE.value)
        
        # Adjust based on team size fit
        if team_size in methodology.team_size_fit:
            score += 0.2
        
        # Adjust based on complexity fit
        if complexity in methodology.complexity_fit:
            score += 0.2
        
        # Criterion-specific scoring
        if criterion == 'flexibility':
            if methodology.type in [MethodologyType.KANBAN.value, MethodologyType.AGILE.value]:
                score += 0.3
        elif criterion == 'structure':
            if methodology.type in [MethodologyType.SCRUM.value, MethodologyType.WATERFALL.value]:
                score += 0.3
        elif criterion == 'team_collaboration':
            if methodology.type in [MethodologyType.SCRUM.value, MethodologyType.AGILE.value]:
                score += 0.3
        elif criterion == 'speed_to_market':
            if methodology.type in [MethodologyType.KANBAN.value, MethodologyType.AGILE.value]:
                score += 0.3
        
        return min(1.0, score)
    
    def _generate_comparison_reasoning(
        self,
        methodologies: List[Methodology],
        scores: Dict,
        overall_scores: Dict,
        context: Dict
    ) -> str:
        """Generate reasoning for methodology comparison."""
        recommended = max(overall_scores, key=overall_scores.get)
        
        reasoning = f"Based on the context (team size: {context.get('team_size', 'unknown')}, "
        reasoning += f"complexity: {context.get('complexity', 'unknown')}), "
        reasoning += f"{recommended} is recommended. "
        
        # Find best criteria for recommended methodology
        best_criteria = []
        for criterion, method_scores in scores.items():
            if method_scores[recommended] >= 0.7:
                best_criteria.append(criterion)
        
        if best_criteria:
            reasoning += f"It excels in: {', '.join(best_criteria[:3])}. "
        
        return reasoning
    
    def recommend_methodology(
        self,
        team_size: str,
        complexity: str,
        requirements: List[str] = None
    ) -> Dict:
        """Recommend a methodology based on context."""
        context = {
            'team_size': team_size,
            'complexity': complexity,
            'requirements': requirements or []
        }
        
        scores = {}
        for methodology in self.methodologies.values():
            score = 0.0
            
            # Team size fit
            if team_size in methodology.team_size_fit:
                score += 0.4
            
            # Complexity fit
            if complexity in methodology.complexity_fit:
                score += 0.4
            
            # Requirements match
            if requirements:
                matches = sum(1 for req in requirements if req in methodology.best_for)
                score += 0.2 * (matches / len(requirements))
            
            scores[methodology.name] = score
        
        if not scores:
            return {'recommendation': None, 'score': 0.0, 'reasoning': 'No methodologies available'}
        
        recommended = max(scores, key=scores.get)
        
        return {
            'recommendation': recommended,
            'score': scores[recommended],
            'reasoning': f"Best fit for team size {team_size} and complexity {complexity}",
            'all_scores': scores
        }
    
    def get_best_practices_for_methodology(
        self,
        methodology_name: str,
        category: str = None
    ) -> List[BestPractice]:
        """Get best practices applicable to a methodology."""
        practices = []
        for practice in self.best_practices.values():
            if methodology_name in practice.applicable_methodologies:
                if category is None or practice.category == category:
                    practices.append(practice)
        
        # Sort by effectiveness
        effectiveness_order = {
            EffectivenessLevel.VERY_HIGH.value: 4,
            EffectivenessLevel.HIGH.value: 3,
            EffectivenessLevel.MEDIUM.value: 2,
            EffectivenessLevel.LOW.value: 1
        }
        practices.sort(
            key=lambda p: effectiveness_order.get(p.effectiveness, 0),
            reverse=True
        )
        
        return practices
    
    def detect_anti_patterns(
        self,
        observed_symptoms: List[str]
    ) -> List[AntiPattern]:
        """Detect anti-patterns based on observed symptoms."""
        detected = []
        for anti_pattern in self.anti_patterns.values():
            # Check if any symptoms match
            matches = sum(1 for symptom in observed_symptoms if symptom in anti_pattern.symptoms)
            if matches > 0:
                detected.append({
                    'anti_pattern': anti_pattern,
                    'match_count': matches,
                    'confidence': matches / len(anti_pattern.symptoms)
                })
        
        # Sort by confidence
        detected.sort(key=lambda x: x['confidence'], reverse=True)
        return [d['anti_pattern'] for d in detected]
    
    def get_workflow_template(
        self,
        methodology: str,
        team_size: str = None,
        complexity: str = None
    ) -> Optional[Workflow]:
        """Get a workflow template for a methodology."""
        matching_workflows = []
        for workflow in self.workflows.values():
            if workflow.methodology.lower() == methodology.lower():
                if team_size and workflow.team_size != team_size:
                    continue
                if complexity and workflow.complexity != complexity:
                    continue
                matching_workflows.append(workflow)
        
        if matching_workflows:
            # Return most effective or most used
            return max(matching_workflows, key=lambda w: (w.effectiveness, w.usage_count))
        
        return None
    
    def track_practice_usage(
        self,
        practice_id: str,
        success: bool
    ):
        """Track usage and success of a best practice."""
        if practice_id in self.best_practices:
            practice = self.best_practices[practice_id]
            practice.usage_count += 1
            
            # Update success rate
            total_successes = practice.success_rate * (practice.usage_count - 1)
            if success:
                total_successes += 1
            practice.success_rate = total_successes / practice.usage_count
            
            self._save_data()
    
    def get_methodology_summary(self) -> Dict:
        """Get summary of learned methodologies."""
        return {
            'total_methodologies': len(self.methodologies),
            'total_best_practices': len(self.best_practices),
            'total_anti_patterns': len(self.anti_patterns),
            'total_workflows': len(self.workflows),
            'total_comparisons': len(self.comparisons),
            'methodologies_by_type': self._count_by_type(),
            'practices_by_category': self._count_practices_by_category()
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """Count methodologies by type."""
        counts = {}
        for methodology in self.methodologies.values():
            counts[methodology.type] = counts.get(methodology.type, 0) + 1
        return counts
    
    def _count_practices_by_category(self) -> Dict[str, int]:
        """Count practices by category."""
        counts = {}
        for practice in self.best_practices.values():
            counts[practice.category] = counts.get(practice.category, 0) + 1
        return counts


if __name__ == "__main__":
    # Example usage
    analyzer = MethodologyAnalyzer()
    
    # Learn a best practice
    practice = analyzer.learn_best_practice(
        name="Daily Standup",
        category=PracticeCategory.COLLABORATION.value,
        description="Daily team synchronization meeting",
        benefits=["Team alignment", "Quick problem identification", "Transparency"],
        implementation_steps=[
            "Schedule 15-minute daily meeting",
            "Each member answers: What did I do? What will I do? Any blockers?",
            "Keep it time-boxed"
        ],
        applicable_methodologies=["Scrum", "Agile"],
        effectiveness=EffectivenessLevel.HIGH.value
    )
    
    print(f"Learned practice: {practice.name}")
    
    # Recommend methodology
    recommendation = analyzer.recommend_methodology(
        team_size=TeamSize.SMALL.value,
        complexity=ProjectComplexity.MODERATE.value,
        requirements=['flexibility', 'continuous_delivery']
    )
    
    print(f"\nRecommended methodology: {recommendation['recommendation']}")
    print(f"Score: {recommendation['score']:.2f}")
    
    # Get summary
    summary = analyzer.get_methodology_summary()
    print(f"\nMethodology Summary:")
    print(f"Total methodologies: {summary['total_methodologies']}")
    print(f"Total best practices: {summary['total_best_practices']}")
    print(f"Total anti-patterns: {summary['total_anti_patterns']}")

