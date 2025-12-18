#!/usr/bin/env python3
"""
Framework Understanding Module

This module learns and understands software frameworks, their architectures,
patterns, and best practices. It enables the AI to provide expert guidance
on framework usage and integration.

Author: Vy-Nexus Self-Evolving AI
Created: December 15, 2025
"""

import json
import os
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime
from enum import Enum
import hashlib


class FrameworkType(Enum):
    """Types of frameworks."""
    WEB_FRONTEND = "web_frontend"
    WEB_BACKEND = "web_backend"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    DATA_SCIENCE = "data_science"
    MACHINE_LEARNING = "machine_learning"
    TESTING = "testing"
    BUILD_TOOL = "build_tool"
    ORM = "orm"
    API = "api"
    UI_COMPONENT = "ui_component"
    STATE_MANAGEMENT = "state_management"
    OTHER = "other"


class ArchitecturePattern(Enum):
    """Common architecture patterns."""
    MVC = "mvc"
    MVVM = "mvvm"
    MVP = "mvp"
    FLUX = "flux"
    REDUX = "redux"
    CLEAN_ARCHITECTURE = "clean_architecture"
    HEXAGONAL = "hexagonal"
    LAYERED = "layered"
    MICROSERVICES = "microservices"
    MONOLITHIC = "monolithic"
    EVENT_DRIVEN = "event_driven"
    PIPE_AND_FILTER = "pipe_and_filter"


class DesignPattern(Enum):
    """Common design patterns."""
    SINGLETON = "singleton"
    FACTORY = "factory"
    OBSERVER = "observer"
    DECORATOR = "decorator"
    ADAPTER = "adapter"
    STRATEGY = "strategy"
    COMMAND = "command"
    REPOSITORY = "repository"
    DEPENDENCY_INJECTION = "dependency_injection"
    MIDDLEWARE = "middleware"
    PLUGIN = "plugin"
    TEMPLATE_METHOD = "template_method"


@dataclass
class Component:
    """Represents a framework component."""
    component_id: str
    name: str
    purpose: str
    dependencies: List[str] = field(default_factory=list)
    interfaces: List[str] = field(default_factory=list)
    patterns_used: List[str] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)
    common_pitfalls: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


@dataclass
class BestPractice:
    """Represents a framework best practice."""
    practice_id: str
    title: str
    description: str
    category: str
    importance: str  # critical, important, recommended
    examples: List[str] = field(default_factory=list)
    anti_patterns: List[str] = field(default_factory=list)
    related_patterns: List[str] = field(default_factory=list)


@dataclass
class MigrationPath:
    """Represents a migration path between frameworks."""
    path_id: str
    from_framework: str
    to_framework: str
    difficulty: str  # easy, moderate, hard, very_hard
    estimated_effort: str
    key_differences: List[str] = field(default_factory=list)
    migration_steps: List[str] = field(default_factory=list)
    gotchas: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)


@dataclass
class FrameworkProfile:
    """Complete profile of a framework."""
    framework_id: str
    name: str
    framework_type: str
    version: str
    description: str
    architecture_pattern: str
    core_concepts: List[str] = field(default_factory=list)
    components: List[Component] = field(default_factory=list)
    design_patterns: List[str] = field(default_factory=list)
    best_practices: List[BestPractice] = field(default_factory=list)
    learning_curve: str = "moderate"  # easy, moderate, steep, very_steep
    ecosystem_size: str = "medium"  # small, medium, large, very_large
    community_support: float = 0.5
    documentation_quality: float = 0.5
    maturity: str = "stable"
    use_cases: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    integrations: Dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class FrameworkUnderstanding:
    """
    System for learning and understanding software frameworks.
    
    This system analyzes frameworks, identifies patterns, extracts best practices,
    and provides expert guidance on framework usage and integration.
    """
    
    def __init__(self, data_dir: str = None):
        """Initialize the framework understanding system."""
        if data_dir is None:
            data_dir = os.path.expanduser("~/vy-nexus/data/frameworks")
        
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self.frameworks: Dict[str, Dict] = {}
        self.components: Dict[str, Dict] = {}
        self.best_practices: Dict[str, Dict] = {}
        self.migration_paths: Dict[str, Dict] = {}
        self.pattern_library: Dict[str, List[str]] = {}
        self.integration_strategies: Dict[str, Dict] = {}
        self.learning_log: List[Dict] = []
        
        self._load_data()
        self._initialize_common_frameworks()
    
    def _load_data(self):
        """Load saved framework data."""
        frameworks_file = os.path.join(self.data_dir, "frameworks.json")
        if os.path.exists(frameworks_file):
            with open(frameworks_file, 'r') as f:
                data = json.load(f)
                self.frameworks = data.get('frameworks', {})
                self.components = data.get('components', {})
                self.best_practices = data.get('best_practices', {})
                self.migration_paths = data.get('migration_paths', {})
                self.pattern_library = data.get('pattern_library', {})
                self.integration_strategies = data.get('integration_strategies', {})
                self.learning_log = data.get('learning_log', [])
    
    def _save_data(self):
        """Save framework data."""
        frameworks_file = os.path.join(self.data_dir, "frameworks.json")
        with open(frameworks_file, 'w') as f:
            json.dump({
                'frameworks': self.frameworks,
                'components': self.components,
                'best_practices': self.best_practices,
                'migration_paths': self.migration_paths,
                'pattern_library': self.pattern_library,
                'integration_strategies': self.integration_strategies,
                'learning_log': self.learning_log
            }, f, indent=2)
    
    def _initialize_common_frameworks(self):
        """Initialize knowledge of common frameworks."""
        if not self.frameworks:
            # React
            self.learn_framework(
                name="React",
                framework_type=FrameworkType.WEB_FRONTEND.value,
                version="18.x",
                description="A JavaScript library for building user interfaces",
                architecture_pattern=ArchitecturePattern.FLUX.value,
                core_concepts=['components', 'props', 'state', 'hooks', 'virtual_dom'],
                design_patterns=[DesignPattern.OBSERVER.value, DesignPattern.DECORATOR.value]
            )
            
            # Django
            self.learn_framework(
                name="Django",
                framework_type=FrameworkType.WEB_BACKEND.value,
                version="4.x",
                description="High-level Python web framework",
                architecture_pattern=ArchitecturePattern.MVC.value,
                core_concepts=['models', 'views', 'templates', 'orm', 'middleware'],
                design_patterns=[DesignPattern.REPOSITORY.value, DesignPattern.MIDDLEWARE.value]
            )
    
    def learn_framework(
        self,
        name: str,
        framework_type: str,
        version: str,
        description: str,
        architecture_pattern: str,
        core_concepts: List[str] = None,
        design_patterns: List[str] = None,
        **kwargs
    ) -> FrameworkProfile:
        """Learn about a new framework."""
        framework_id = self._generate_id(f"{name}_{version}")
        
        profile = FrameworkProfile(
            framework_id=framework_id,
            name=name,
            framework_type=framework_type,
            version=version,
            description=description,
            architecture_pattern=architecture_pattern,
            core_concepts=core_concepts or [],
            design_patterns=design_patterns or [],
            **kwargs
        )
        
        self.frameworks[framework_id] = asdict(profile)
        
        # Log learning activity
        self.learning_log.append({
            'timestamp': datetime.now().isoformat(),
            'action': 'learn_framework',
            'framework': name,
            'framework_id': framework_id
        })
        
        self._save_data()
        return profile
    
    def add_component(
        self,
        framework_id: str,
        name: str,
        purpose: str,
        dependencies: List[str] = None,
        patterns_used: List[str] = None,
        best_practices: List[str] = None
    ) -> Component:
        """Add a component to a framework."""
        component_id = self._generate_id(f"{framework_id}_{name}")
        
        component = Component(
            component_id=component_id,
            name=name,
            purpose=purpose,
            dependencies=dependencies or [],
            patterns_used=patterns_used or [],
            best_practices=best_practices or []
        )
        
        self.components[component_id] = asdict(component)
        
        # Add to framework
        if framework_id in self.frameworks:
            if 'components' not in self.frameworks[framework_id]:
                self.frameworks[framework_id]['components'] = []
            self.frameworks[framework_id]['components'].append(asdict(component))
        
        self._save_data()
        return component
    
    def add_best_practice(
        self,
        framework_id: str,
        title: str,
        description: str,
        category: str,
        importance: str = "recommended",
        examples: List[str] = None,
        anti_patterns: List[str] = None
    ) -> BestPractice:
        """Add a best practice for a framework."""
        practice_id = self._generate_id(f"{framework_id}_{title}")
        
        practice = BestPractice(
            practice_id=practice_id,
            title=title,
            description=description,
            category=category,
            importance=importance,
            examples=examples or [],
            anti_patterns=anti_patterns or []
        )
        
        self.best_practices[practice_id] = asdict(practice)
        
        # Add to framework
        if framework_id in self.frameworks:
            if 'best_practices' not in self.frameworks[framework_id]:
                self.frameworks[framework_id]['best_practices'] = []
            self.frameworks[framework_id]['best_practices'].append(asdict(practice))
        
        self._save_data()
        return practice
    
    def create_migration_path(
        self,
        from_framework: str,
        to_framework: str,
        difficulty: str,
        estimated_effort: str,
        key_differences: List[str] = None,
        migration_steps: List[str] = None,
        gotchas: List[str] = None
    ) -> MigrationPath:
        """Create a migration path between frameworks."""
        path_id = self._generate_id(f"{from_framework}_to_{to_framework}")
        
        path = MigrationPath(
            path_id=path_id,
            from_framework=from_framework,
            to_framework=to_framework,
            difficulty=difficulty,
            estimated_effort=estimated_effort,
            key_differences=key_differences or [],
            migration_steps=migration_steps or [],
            gotchas=gotchas or []
        )
        
        self.migration_paths[path_id] = asdict(path)
        self._save_data()
        return path
    
    def analyze_architecture(self, framework_id: str) -> Dict[str, Any]:
        """Analyze the architecture of a framework."""
        if framework_id not in self.frameworks:
            return {}
        
        framework = self.frameworks[framework_id]
        
        analysis = {
            'framework': framework['name'],
            'architecture_pattern': framework['architecture_pattern'],
            'component_count': len(framework.get('components', [])),
            'design_patterns': framework.get('design_patterns', []),
            'complexity': self._assess_complexity(framework),
            'modularity': self._assess_modularity(framework),
            'extensibility': self._assess_extensibility(framework),
            'component_relationships': self._map_component_relationships(framework_id)
        }
        
        return analysis
    
    def _assess_complexity(self, framework: Dict) -> str:
        """Assess framework complexity."""
        score = 0
        
        # More components = more complex
        component_count = len(framework.get('components', []))
        if component_count > 20:
            score += 3
        elif component_count > 10:
            score += 2
        elif component_count > 5:
            score += 1
        
        # More patterns = more complex
        pattern_count = len(framework.get('design_patterns', []))
        if pattern_count > 5:
            score += 2
        elif pattern_count > 3:
            score += 1
        
        # Learning curve
        learning_curve = framework.get('learning_curve', 'moderate')
        if learning_curve in ['steep', 'very_steep']:
            score += 2
        elif learning_curve == 'moderate':
            score += 1
        
        if score >= 6:
            return "very_high"
        elif score >= 4:
            return "high"
        elif score >= 2:
            return "moderate"
        else:
            return "low"
    
    def _assess_modularity(self, framework: Dict) -> float:
        """Assess framework modularity (0-1)."""
        components = framework.get('components', [])
        if not components:
            return 0.5
        
        # Check component independence
        total_deps = sum(len(c.get('dependencies', [])) for c in components)
        avg_deps = total_deps / len(components) if components else 0
        
        # Lower average dependencies = higher modularity
        if avg_deps < 1:
            return 0.9
        elif avg_deps < 2:
            return 0.7
        elif avg_deps < 3:
            return 0.5
        else:
            return 0.3
    
    def _assess_extensibility(self, framework: Dict) -> float:
        """Assess framework extensibility (0-1)."""
        score = 0.5
        
        # Check for plugin pattern
        patterns = framework.get('design_patterns', [])
        if DesignPattern.PLUGIN.value in patterns:
            score += 0.2
        if DesignPattern.DECORATOR.value in patterns:
            score += 0.1
        if DesignPattern.STRATEGY.value in patterns:
            score += 0.1
        
        # Check integrations
        integrations = framework.get('integrations', {})
        if len(integrations) > 10:
            score += 0.1
        
        return min(score, 1.0)
    
    def _map_component_relationships(self, framework_id: str) -> Dict[str, List[str]]:
        """Map relationships between components."""
        if framework_id not in self.frameworks:
            return {}
        
        framework = self.frameworks[framework_id]
        components = framework.get('components', [])
        
        relationships = {}
        for component in components:
            comp_name = component['name']
            relationships[comp_name] = component.get('dependencies', [])
        
        return relationships
    
    def identify_patterns(self, framework_id: str) -> List[Dict[str, Any]]:
        """Identify design patterns used in a framework."""
        if framework_id not in self.frameworks:
            return []
        
        framework = self.frameworks[framework_id]
        patterns = []
        
        # Framework-level patterns
        for pattern in framework.get('design_patterns', []):
            patterns.append({
                'pattern': pattern,
                'level': 'framework',
                'description': self._get_pattern_description(pattern)
            })
        
        # Component-level patterns
        for component in framework.get('components', []):
            for pattern in component.get('patterns_used', []):
                patterns.append({
                    'pattern': pattern,
                    'level': 'component',
                    'component': component['name'],
                    'description': self._get_pattern_description(pattern)
                })
        
        return patterns
    
    def _get_pattern_description(self, pattern: str) -> str:
        """Get description of a design pattern."""
        descriptions = {
            DesignPattern.SINGLETON.value: "Ensures a class has only one instance",
            DesignPattern.FACTORY.value: "Creates objects without specifying exact class",
            DesignPattern.OBSERVER.value: "Defines one-to-many dependency between objects",
            DesignPattern.DECORATOR.value: "Adds behavior to objects dynamically",
            DesignPattern.ADAPTER.value: "Converts interface of a class into another",
            DesignPattern.STRATEGY.value: "Defines family of algorithms, makes them interchangeable",
            DesignPattern.REPOSITORY.value: "Mediates between domain and data mapping layers",
            DesignPattern.DEPENDENCY_INJECTION.value: "Provides dependencies from outside",
            DesignPattern.MIDDLEWARE.value: "Processes requests in a pipeline",
            DesignPattern.PLUGIN.value: "Allows extending functionality through plugins"
        }
        return descriptions.get(pattern, "Design pattern")
    
    def compare_frameworks(
        self,
        framework_ids: List[str],
        criteria: List[str] = None
    ) -> Dict[str, Any]:
        """Compare multiple frameworks."""
        if not framework_ids:
            return {}
        
        frameworks = [self.frameworks.get(fid) for fid in framework_ids if fid in self.frameworks]
        if not frameworks:
            return {}
        
        if criteria is None:
            criteria = [
                'learning_curve', 'ecosystem_size', 'community_support',
                'documentation_quality', 'maturity'
            ]
        
        comparison = {
            'frameworks': [f['name'] for f in frameworks],
            'criteria': {},
            'winner': None,
            'recommendation': ''
        }
        
        # Compare each criterion
        for criterion in criteria:
            comparison['criteria'][criterion] = {}
            for framework in frameworks:
                value = framework.get(criterion, 'unknown')
                comparison['criteria'][criterion][framework['name']] = value
        
        # Determine winner
        scores = {f['name']: 0 for f in frameworks}
        for framework in frameworks:
            # Higher is better for these metrics
            if framework.get('community_support', 0) > 0.7:
                scores[framework['name']] += 2
            if framework.get('documentation_quality', 0) > 0.7:
                scores[framework['name']] += 2
            if framework.get('ecosystem_size') in ['large', 'very_large']:
                scores[framework['name']] += 2
            if framework.get('learning_curve') in ['easy', 'moderate']:
                scores[framework['name']] += 1
        
        comparison['winner'] = max(scores, key=scores.get)
        comparison['scores'] = scores
        
        return comparison
    
    def find_integration_strategy(
        self,
        framework1_id: str,
        framework2_id: str
    ) -> Dict[str, Any]:
        """Find or create integration strategy between frameworks."""
        strategy_id = self._generate_id(f"{framework1_id}_{framework2_id}")
        
        if strategy_id in self.integration_strategies:
            return self.integration_strategies[strategy_id]
        
        # Create new strategy
        f1 = self.frameworks.get(framework1_id, {})
        f2 = self.frameworks.get(framework2_id, {})
        
        strategy = {
            'strategy_id': strategy_id,
            'framework1': f1.get('name', 'Unknown'),
            'framework2': f2.get('name', 'Unknown'),
            'compatibility': self._assess_compatibility(f1, f2),
            'integration_points': self._identify_integration_points(f1, f2),
            'recommended_approach': self._recommend_integration_approach(f1, f2),
            'potential_issues': [],
            'best_practices': []
        }
        
        self.integration_strategies[strategy_id] = strategy
        self._save_data()
        
        return strategy
    
    def _assess_compatibility(self, f1: Dict, f2: Dict) -> str:
        """Assess compatibility between frameworks."""
        # Check if they're in complementary categories
        type1 = f1.get('framework_type', '')
        type2 = f2.get('framework_type', '')
        
        complementary_pairs = [
            (FrameworkType.WEB_FRONTEND.value, FrameworkType.WEB_BACKEND.value),
            (FrameworkType.WEB_BACKEND.value, FrameworkType.ORM.value),
            (FrameworkType.WEB_FRONTEND.value, FrameworkType.STATE_MANAGEMENT.value)
        ]
        
        if (type1, type2) in complementary_pairs or (type2, type1) in complementary_pairs:
            return "high"
        elif type1 == type2:
            return "low"  # Usually don't integrate same-type frameworks
        else:
            return "moderate"
    
    def _identify_integration_points(self, f1: Dict, f2: Dict) -> List[str]:
        """Identify potential integration points."""
        points = []
        
        # Check for API integration
        if f1.get('framework_type') == FrameworkType.WEB_FRONTEND.value:
            if f2.get('framework_type') == FrameworkType.WEB_BACKEND.value:
                points.append("REST API")
                points.append("GraphQL")
        
        # Check for data layer integration
        if f2.get('framework_type') == FrameworkType.ORM.value:
            points.append("Database Layer")
        
        # Check for state management
        if f2.get('framework_type') == FrameworkType.STATE_MANAGEMENT.value:
            points.append("Application State")
        
        return points
    
    def _recommend_integration_approach(self, f1: Dict, f2: Dict) -> str:
        """Recommend integration approach."""
        type1 = f1.get('framework_type', '')
        type2 = f2.get('framework_type', '')
        
        if type1 == FrameworkType.WEB_FRONTEND.value and type2 == FrameworkType.WEB_BACKEND.value:
            return "Use REST API or GraphQL for communication between frontend and backend"
        elif type2 == FrameworkType.STATE_MANAGEMENT.value:
            return "Integrate state management library into component lifecycle"
        elif type2 == FrameworkType.ORM.value:
            return "Use ORM in data access layer of backend framework"
        else:
            return "Evaluate integration points and use appropriate adapter pattern"
    
    def get_best_practices(
        self,
        framework_id: str,
        category: str = None,
        min_importance: str = None
    ) -> List[Dict]:
        """Get best practices for a framework."""
        if framework_id not in self.frameworks:
            return []
        
        practices = self.frameworks[framework_id].get('best_practices', [])
        
        # Filter by category
        if category:
            practices = [p for p in practices if p.get('category') == category]
        
        # Filter by importance
        if min_importance:
            importance_order = ['recommended', 'important', 'critical']
            min_idx = importance_order.index(min_importance)
            practices = [
                p for p in practices
                if importance_order.index(p.get('importance', 'recommended')) >= min_idx
            ]
        
        return practices
    
    def detect_anti_patterns(self, framework_id: str, code_sample: str = None) -> List[Dict]:
        """Detect anti-patterns in framework usage."""
        anti_patterns = []
        
        if framework_id not in self.frameworks:
            return anti_patterns
        
        # Get known anti-patterns from best practices
        practices = self.frameworks[framework_id].get('best_practices', [])
        for practice in practices:
            for anti_pattern in practice.get('anti_patterns', []):
                anti_patterns.append({
                    'anti_pattern': anti_pattern,
                    'related_practice': practice['title'],
                    'severity': practice.get('importance', 'recommended')
                })
        
        return anti_patterns
    
    def get_learning_path(self, framework_id: str) -> Dict[str, Any]:
        """Get recommended learning path for a framework."""
        if framework_id not in self.frameworks:
            return {}
        
        framework = self.frameworks[framework_id]
        
        path = {
            'framework': framework['name'],
            'difficulty': framework.get('learning_curve', 'moderate'),
            'prerequisites': self._identify_prerequisites(framework),
            'learning_stages': [
                {
                    'stage': 'Fundamentals',
                    'topics': framework.get('core_concepts', [])[:3],
                    'duration': '1-2 weeks'
                },
                {
                    'stage': 'Core Concepts',
                    'topics': framework.get('core_concepts', []),
                    'duration': '2-4 weeks'
                },
                {
                    'stage': 'Advanced Patterns',
                    'topics': framework.get('design_patterns', []),
                    'duration': '2-3 weeks'
                },
                {
                    'stage': 'Best Practices',
                    'topics': [p['title'] for p in framework.get('best_practices', [])[:5]],
                    'duration': '1-2 weeks'
                }
            ],
            'resources': self._recommend_learning_resources(framework),
            'practice_projects': self._suggest_practice_projects(framework)
        }
        
        return path
    
    def _identify_prerequisites(self, framework: Dict) -> List[str]:
        """Identify prerequisites for learning a framework."""
        prereqs = []
        
        framework_type = framework.get('framework_type', '')
        
        if framework_type == FrameworkType.WEB_FRONTEND.value:
            prereqs.extend(['HTML', 'CSS', 'JavaScript'])
        elif framework_type == FrameworkType.WEB_BACKEND.value:
            prereqs.extend(['HTTP', 'Databases', 'Server concepts'])
        elif framework_type == FrameworkType.MACHINE_LEARNING.value:
            prereqs.extend(['Python', 'Mathematics', 'Statistics'])
        
        return prereqs
    
    def _recommend_learning_resources(self, framework: Dict) -> List[str]:
        """Recommend learning resources."""
        return [
            f"Official {framework['name']} documentation",
            f"{framework['name']} tutorial series",
            f"{framework['name']} best practices guide",
            "Community forums and discussions"
        ]
    
    def _suggest_practice_projects(self, framework: Dict) -> List[str]:
        """Suggest practice projects."""
        framework_type = framework.get('framework_type', '')
        
        if framework_type == FrameworkType.WEB_FRONTEND.value:
            return ["Todo app", "Blog platform", "E-commerce site"]
        elif framework_type == FrameworkType.WEB_BACKEND.value:
            return ["REST API", "Authentication system", "Real-time chat"]
        else:
            return ["Simple application", "Feature implementation", "Integration project"]
    
    def get_framework_summary(self, framework_id: str) -> Dict[str, Any]:
        """Get comprehensive summary of a framework."""
        if framework_id not in self.frameworks:
            return {}
        
        framework = self.frameworks[framework_id]
        
        return {
            'name': framework['name'],
            'type': framework['framework_type'],
            'version': framework['version'],
            'description': framework['description'],
            'architecture': framework['architecture_pattern'],
            'complexity': self._assess_complexity(framework),
            'learning_curve': framework.get('learning_curve', 'moderate'),
            'component_count': len(framework.get('components', [])),
            'pattern_count': len(framework.get('design_patterns', [])),
            'best_practice_count': len(framework.get('best_practices', [])),
            'strengths': framework.get('strengths', []),
            'weaknesses': framework.get('weaknesses', []),
            'use_cases': framework.get('use_cases', []),
            'alternatives': framework.get('alternatives', [])
        }
    
    def _generate_id(self, seed: str) -> str:
        """Generate unique ID."""
        return hashlib.md5(seed.encode()).hexdigest()[:16]


if __name__ == "__main__":
    # Example usage
    understanding = FrameworkUnderstanding()
    
    # Learn about a framework
    react = understanding.learn_framework(
        name="React",
        framework_type=FrameworkType.WEB_FRONTEND.value,
        version="18.2",
        description="JavaScript library for building UIs",
        architecture_pattern=ArchitecturePattern.FLUX.value,
        core_concepts=['components', 'props', 'state', 'hooks'],
        learning_curve="moderate",
        ecosystem_size="very_large"
    )
    
    print(f"Learned about {react.name}")
    
    # Analyze architecture
    analysis = understanding.analyze_architecture(react.framework_id)
    print(f"\nArchitecture analysis: {analysis}")
