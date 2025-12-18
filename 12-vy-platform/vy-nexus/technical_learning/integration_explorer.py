"""
Integration Explorer

This module discovers, learns, and manages integrations between tools, platforms,
services, and technologies. It helps identify integration opportunities, learn
integration patterns, and recommend optimal integration strategies.

Author: Vy Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Any
from datetime import datetime
from enum import Enum
import json
import os


class IntegrationType(Enum):
    """Types of integrations."""
    API = "api"
    WEBHOOK = "webhook"
    SDK = "sdk"
    PLUGIN = "plugin"
    NATIVE = "native"
    DATABASE = "database"
    FILE_BASED = "file_based"
    MESSAGE_QUEUE = "message_queue"
    EVENT_DRIVEN = "event_driven"
    BATCH = "batch"
    STREAMING = "streaming"
    CLI = "cli"


class IntegrationPattern(Enum):
    """Common integration patterns."""
    POINT_TO_POINT = "point_to_point"
    HUB_AND_SPOKE = "hub_and_spoke"
    PUBLISH_SUBSCRIBE = "publish_subscribe"
    REQUEST_RESPONSE = "request_response"
    EVENT_SOURCING = "event_sourcing"
    CQRS = "cqrs"
    SAGA = "saga"
    ORCHESTRATION = "orchestration"
    CHOREOGRAPHY = "choreography"
    ETL = "etl"
    MICROSERVICES = "microservices"


class IntegrationComplexity(Enum):
    """Integration complexity levels."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


class IntegrationStatus(Enum):
    """Integration status."""
    AVAILABLE = "available"
    CONFIGURED = "configured"
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"


class AuthenticationType(Enum):
    """Authentication types for integrations."""
    NONE = "none"
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    JWT = "jwt"
    CERTIFICATE = "certificate"
    CUSTOM = "custom"


@dataclass
class IntegrationRequirement:
    """Represents a requirement for an integration."""
    requirement_id: str
    name: str
    description: str
    type: str  # technical/business/security/performance
    mandatory: bool
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationEndpoint:
    """Represents an integration endpoint."""
    endpoint_id: str
    tool_name: str
    endpoint_type: str  # source/target/bidirectional
    capabilities: List[str] = field(default_factory=list)
    authentication: str = AuthenticationType.NONE.value
    rate_limits: Optional[Dict[str, Any]] = None
    data_formats: List[str] = field(default_factory=list)


@dataclass
class IntegrationProfile:
    """Complete profile of an integration."""
    integration_id: str
    name: str
    source_tool: str
    target_tool: str
    integration_type: str
    pattern: str
    description: str
    use_cases: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    requirements: List[IntegrationRequirement] = field(default_factory=list)
    setup_steps: List[str] = field(default_factory=list)
    configuration: Dict[str, Any] = field(default_factory=dict)
    authentication: str = AuthenticationType.NONE.value
    complexity: str = IntegrationComplexity.MODERATE.value
    status: str = IntegrationStatus.AVAILABLE.value
    bidirectional: bool = False
    real_time: bool = True
    data_formats: List[str] = field(default_factory=list)
    protocols: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    cost: Optional[str] = None
    documentation_url: Optional[str] = None
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 0
    success_rate: float = 0.0
    health_score: float = 1.0


@dataclass
class IntegrationRecommendation:
    """Recommendation for an integration."""
    recommendation_id: str
    integration_id: str
    integration_name: str
    use_case: str
    score: float
    reasoning: str
    benefits: List[str] = field(default_factory=list)
    considerations: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class IntegrationGraph:
    """Represents the integration graph between tools."""
    graph_id: str
    tools: List[str] = field(default_factory=list)
    integrations: List[str] = field(default_factory=list)
    adjacency: Dict[str, List[str]] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


class IntegrationExplorer:
    """
    Main class for discovering, learning, and managing integrations.
    
    This system helps identify integration opportunities, learn integration
    patterns, and recommend optimal integration strategies.
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/integration_explorer"):
        """Initialize the integration explorer."""
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.integrations: Dict[str, IntegrationProfile] = {}
        self.recommendations: Dict[str, IntegrationRecommendation] = {}
        self.integration_graph: Optional[IntegrationGraph] = None
        
        self._load_integrations()
        self._load_recommendations()
        self._load_graph()
        
        # Initialize with some common integrations
        if not self.integrations:
            self._initialize_common_integrations()
    
    def discover_integration(
        self,
        name: str,
        source_tool: str,
        target_tool: str,
        integration_type: str,
        pattern: str,
        description: str,
        use_cases: Optional[List[str]] = None,
        setup_steps: Optional[List[str]] = None,
        **kwargs
    ) -> IntegrationProfile:
        """
        Discover and catalog a new integration.
        
        Args:
            name: Integration name
            source_tool: Source tool name
            target_tool: Target tool name
            integration_type: Type of integration
            pattern: Integration pattern
            description: Integration description
            use_cases: List of use cases
            setup_steps: Setup instructions
            **kwargs: Additional integration properties
            
        Returns:
            IntegrationProfile object
        """
        integration_id = f"{source_tool}_{target_tool}_{integration_type}".lower().replace(" ", "_")
        
        integration = IntegrationProfile(
            integration_id=integration_id,
            name=name,
            source_tool=source_tool,
            target_tool=target_tool,
            integration_type=integration_type,
            pattern=pattern,
            description=description,
            use_cases=use_cases or [],
            setup_steps=setup_steps or [],
            **{k: v for k, v in kwargs.items() if hasattr(IntegrationProfile, k)}
        )
        
        self.integrations[integration_id] = integration
        self._update_graph(source_tool, target_tool, integration_id)
        self._save_integrations()
        self._save_graph()
        
        return integration
    
    def learn_integration_pattern(
        self,
        pattern_name: str,
        pattern_type: str,
        description: str,
        use_cases: List[str],
        benefits: List[str],
        considerations: List[str]
    ) -> Dict[str, Any]:
        """
        Learn a new integration pattern.
        
        Args:
            pattern_name: Pattern name
            pattern_type: Pattern type
            description: Pattern description
            use_cases: When to use this pattern
            benefits: Pattern benefits
            considerations: Important considerations
            
        Returns:
            Pattern information dictionary
        """
        pattern = {
            'name': pattern_name,
            'type': pattern_type,
            'description': description,
            'use_cases': use_cases,
            'benefits': benefits,
            'considerations': considerations,
            'learned_at': datetime.now().isoformat()
        }
        
        return pattern
    
    def check_compatibility(
        self,
        tool1: str,
        tool2: str
    ) -> Dict[str, Any]:
        """
        Check if two tools can be integrated.
        
        Args:
            tool1: First tool name
            tool2: Second tool name
            
        Returns:
            Compatibility information
        """
        # Find existing integrations
        existing = []
        for integration in self.integrations.values():
            if (integration.source_tool == tool1 and integration.target_tool == tool2) or \
               (integration.source_tool == tool2 and integration.target_tool == tool1):
                existing.append(integration.integration_id)
        
        compatible = len(existing) > 0
        
        return {
            'tool1': tool1,
            'tool2': tool2,
            'compatible': compatible,
            'existing_integrations': existing,
            'integration_count': len(existing),
            'checked_at': datetime.now().isoformat()
        }
    
    def recommend_integration(
        self,
        use_case: str,
        source_tool: Optional[str] = None,
        target_tool: Optional[str] = None,
        requirements: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Recommend integrations for a use case.
        
        Args:
            use_case: The use case to solve
            source_tool: Optional source tool filter
            target_tool: Optional target tool filter
            requirements: Optional requirements list
            
        Returns:
            List of recommended integrations with scores
        """
        recommendations = []
        requirements = requirements or []
        
        for integration in self.integrations.values():
            # Filter by tools if specified
            if source_tool and integration.source_tool != source_tool:
                continue
            if target_tool and integration.target_tool != target_tool:
                continue
            
            # Calculate score based on use case match
            score = 0.0
            
            # Use case matching
            use_case_lower = use_case.lower()
            for uc in integration.use_cases:
                if use_case_lower in uc.lower() or uc.lower() in use_case_lower:
                    score += 0.3
            
            # Requirement matching
            for req in requirements:
                req_lower = req.lower()
                if any(req_lower in benefit.lower() for benefit in integration.benefits):
                    score += 0.2
            
            # Success rate bonus
            score += integration.success_rate * 0.3
            
            # Health score bonus
            score += integration.health_score * 0.2
            
            # Normalize score
            score = min(score, 1.0)
            
            if score > 0.0:
                recommendations.append({
                    'integration_id': integration.integration_id,
                    'name': integration.name,
                    'source_tool': integration.source_tool,
                    'target_tool': integration.target_tool,
                    'score': score,
                    'use_cases': integration.use_cases,
                    'benefits': integration.benefits,
                    'complexity': integration.complexity,
                    'status': integration.status
                })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations
    
    def get_integration_path(
        self,
        source_tool: str,
        target_tool: str
    ) -> List[List[str]]:
        """
        Find integration paths between two tools.
        
        Args:
            source_tool: Source tool
            target_tool: Target tool
            
        Returns:
            List of integration paths (each path is a list of tool names)
        """
        if not self.integration_graph:
            return []
        
        # Simple BFS to find paths
        paths = []
        queue = [([source_tool], set([source_tool]))]
        
        while queue:
            path, visited = queue.pop(0)
            current = path[-1]
            
            if current == target_tool:
                paths.append(path)
                continue
            
            # Get neighbors
            neighbors = self.integration_graph.adjacency.get(current, [])
            
            for neighbor in neighbors:
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    new_visited = visited | {neighbor}
                    queue.append((new_path, new_visited))
        
        return paths
    
    def get_integration(self, integration_id: str) -> Optional[IntegrationProfile]:
        """Get integration by ID."""
        return self.integrations.get(integration_id)
    
    def get_integrations_for_tool(
        self,
        tool_name: str,
        direction: str = "both"  # source/target/both
    ) -> List[IntegrationProfile]:
        """
        Get all integrations for a specific tool.
        
        Args:
            tool_name: Tool name
            direction: Filter by direction (source/target/both)
            
        Returns:
            List of integrations
        """
        integrations = []
        
        for integration in self.integrations.values():
            if direction in ["source", "both"] and integration.source_tool == tool_name:
                integrations.append(integration)
            elif direction in ["target", "both"] and integration.target_tool == tool_name:
                integrations.append(integration)
        
        return integrations
    
    def get_integrations_by_type(
        self,
        integration_type: str
    ) -> List[IntegrationProfile]:
        """Get integrations by type."""
        return [
            integration for integration in self.integrations.values()
            if integration.integration_type == integration_type
        ]
    
    def get_integrations_by_pattern(
        self,
        pattern: str
    ) -> List[IntegrationProfile]:
        """Get integrations by pattern."""
        return [
            integration for integration in self.integrations.values()
            if integration.pattern == pattern
        ]
    
    def track_integration_usage(
        self,
        integration_id: str,
        success: bool = True
    ) -> None:
        """
        Track integration usage and success.
        
        Args:
            integration_id: Integration ID
            success: Whether the integration was successful
        """
        if integration_id not in self.integrations:
            return
        
        integration = self.integrations[integration_id]
        integration.usage_count += 1
        
        # Update success rate (exponential moving average)
        alpha = 0.1
        new_value = 1.0 if success else 0.0
        integration.success_rate = (
            alpha * new_value + (1 - alpha) * integration.success_rate
        )
        
        integration.last_updated = datetime.now().isoformat()
        self._save_integrations()
    
    def update_integration_health(
        self,
        integration_id: str,
        health_score: float
    ) -> None:
        """
        Update integration health score.
        
        Args:
            integration_id: Integration ID
            health_score: Health score (0.0-1.0)
        """
        if integration_id not in self.integrations:
            return
        
        integration = self.integrations[integration_id]
        integration.health_score = max(0.0, min(1.0, health_score))
        integration.last_updated = datetime.now().isoformat()
        self._save_integrations()
    
    def get_integration_summary(self) -> Dict[str, Any]:
        """Get summary of all integrations."""
        type_counts = {}
        pattern_counts = {}
        status_counts = {}
        
        for integration in self.integrations.values():
            # Count by type
            type_counts[integration.integration_type] = \
                type_counts.get(integration.integration_type, 0) + 1
            
            # Count by pattern
            pattern_counts[integration.pattern] = \
                pattern_counts.get(integration.pattern, 0) + 1
            
            # Count by status
            status_counts[integration.status] = \
                status_counts.get(integration.status, 0) + 1
        
        return {
            'total_integrations': len(self.integrations),
            'by_type': type_counts,
            'by_pattern': pattern_counts,
            'by_status': status_counts,
            'total_tools': len(self.integration_graph.tools) if self.integration_graph else 0,
            'avg_success_rate': sum(i.success_rate for i in self.integrations.values()) / len(self.integrations) if self.integrations else 0.0,
            'avg_health_score': sum(i.health_score for i in self.integrations.values()) / len(self.integrations) if self.integrations else 0.0
        }
    
    def _update_graph(
        self,
        source_tool: str,
        target_tool: str,
        integration_id: str
    ) -> None:
        """Update the integration graph."""
        if not self.integration_graph:
            self.integration_graph = IntegrationGraph(
                graph_id="main_graph",
                tools=[],
                integrations=[],
                adjacency={}
            )
        
        # Add tools
        if source_tool not in self.integration_graph.tools:
            self.integration_graph.tools.append(source_tool)
        if target_tool not in self.integration_graph.tools:
            self.integration_graph.tools.append(target_tool)
        
        # Add integration
        if integration_id not in self.integration_graph.integrations:
            self.integration_graph.integrations.append(integration_id)
        
        # Update adjacency
        if source_tool not in self.integration_graph.adjacency:
            self.integration_graph.adjacency[source_tool] = []
        if target_tool not in self.integration_graph.adjacency[source_tool]:
            self.integration_graph.adjacency[source_tool].append(target_tool)
        
        # If bidirectional, add reverse edge
        integration = self.integrations.get(integration_id)
        if integration and integration.bidirectional:
            if target_tool not in self.integration_graph.adjacency:
                self.integration_graph.adjacency[target_tool] = []
            if source_tool not in self.integration_graph.adjacency[target_tool]:
                self.integration_graph.adjacency[target_tool].append(source_tool)
        
        self.integration_graph.last_updated = datetime.now().isoformat()
    
    def _initialize_common_integrations(self) -> None:
        """Initialize with common integrations."""
        # GitHub + CI/CD
        self.discover_integration(
            name="GitHub Actions Integration",
            source_tool="GitHub",
            target_tool="CI/CD",
            integration_type=IntegrationType.NATIVE.value,
            pattern=IntegrationPattern.EVENT_DRIVEN.value,
            description="Native CI/CD integration with GitHub Actions",
            use_cases=["continuous_integration", "automated_testing", "deployment"],
            benefits=["Native integration", "Easy setup", "Free for public repos"],
            setup_steps=[
                "Create .github/workflows directory",
                "Add workflow YAML file",
                "Configure triggers and jobs"
            ],
            complexity=IntegrationComplexity.SIMPLE.value,
            bidirectional=False,
            real_time=True
        )
        
        # Docker + Kubernetes
        self.discover_integration(
            name="Docker to Kubernetes",
            source_tool="Docker",
            target_tool="Kubernetes",
            integration_type=IntegrationType.NATIVE.value,
            pattern=IntegrationPattern.ORCHESTRATION.value,
            description="Container orchestration with Kubernetes",
            use_cases=["container_orchestration", "scaling", "deployment"],
            benefits=["Automated scaling", "Self-healing", "Load balancing"],
            setup_steps=[
                "Create Kubernetes cluster",
                "Build Docker images",
                "Create Kubernetes manifests",
                "Deploy to cluster"
            ],
            complexity=IntegrationComplexity.COMPLEX.value,
            bidirectional=False,
            real_time=True
        )
        
        # PostgreSQL + Application
        self.discover_integration(
            name="PostgreSQL Database Integration",
            source_tool="Application",
            target_tool="PostgreSQL",
            integration_type=IntegrationType.DATABASE.value,
            pattern=IntegrationPattern.REQUEST_RESPONSE.value,
            description="Database integration for data persistence",
            use_cases=["data_storage", "querying", "transactions"],
            benefits=["ACID compliance", "Reliability", "Performance"],
            setup_steps=[
                "Install PostgreSQL",
                "Create database",
                "Configure connection string",
                "Run migrations"
            ],
            complexity=IntegrationComplexity.MODERATE.value,
            bidirectional=True,
            real_time=True
        )
    
    def _load_integrations(self) -> None:
        """Load integrations from file."""
        filepath = os.path.join(self.data_dir, "integrations.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    for integration_data in data:
                        # Convert requirements
                        if 'requirements' in integration_data:
                            integration_data['requirements'] = [
                                IntegrationRequirement(**req) if isinstance(req, dict) else req
                                for req in integration_data['requirements']
                            ]
                        integration = IntegrationProfile(**integration_data)
                        self.integrations[integration.integration_id] = integration
            except Exception as e:
                print(f"Error loading integrations: {e}")
    
    def _save_integrations(self) -> None:
        """Save integrations to file."""
        filepath = os.path.join(self.data_dir, "integrations.json")
        try:
            data = []
            for integration in self.integrations.values():
                integration_dict = {
                    'integration_id': integration.integration_id,
                    'name': integration.name,
                    'source_tool': integration.source_tool,
                    'target_tool': integration.target_tool,
                    'integration_type': integration.integration_type,
                    'pattern': integration.pattern,
                    'description': integration.description,
                    'use_cases': integration.use_cases,
                    'benefits': integration.benefits,
                    'requirements': [
                        {
                            'requirement_id': req.requirement_id,
                            'name': req.name,
                            'description': req.description,
                            'type': req.type,
                            'mandatory': req.mandatory,
                            'details': req.details
                        } for req in integration.requirements
                    ],
                    'setup_steps': integration.setup_steps,
                    'configuration': integration.configuration,
                    'authentication': integration.authentication,
                    'complexity': integration.complexity,
                    'status': integration.status,
                    'bidirectional': integration.bidirectional,
                    'real_time': integration.real_time,
                    'data_formats': integration.data_formats,
                    'protocols': integration.protocols,
                    'dependencies': integration.dependencies,
                    'limitations': integration.limitations,
                    'performance_metrics': integration.performance_metrics,
                    'cost': integration.cost,
                    'documentation_url': integration.documentation_url,
                    'discovered_at': integration.discovered_at,
                    'last_updated': integration.last_updated,
                    'usage_count': integration.usage_count,
                    'success_rate': integration.success_rate,
                    'health_score': integration.health_score
                }
                data.append(integration_dict)
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving integrations: {e}")
    
    def _load_recommendations(self) -> None:
        """Load recommendations from file."""
        filepath = os.path.join(self.data_dir, "recommendations.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    for rec_data in data:
                        rec = IntegrationRecommendation(**rec_data)
                        self.recommendations[rec.recommendation_id] = rec
            except Exception as e:
                print(f"Error loading recommendations: {e}")
    
    def _save_recommendations(self) -> None:
        """Save recommendations to file."""
        filepath = os.path.join(self.data_dir, "recommendations.json")
        try:
            data = [
                {
                    'recommendation_id': rec.recommendation_id,
                    'integration_id': rec.integration_id,
                    'integration_name': rec.integration_name,
                    'use_case': rec.use_case,
                    'score': rec.score,
                    'reasoning': rec.reasoning,
                    'benefits': rec.benefits,
                    'considerations': rec.considerations,
                    'alternatives': rec.alternatives,
                    'created_at': rec.created_at
                }
                for rec in self.recommendations.values()
            ]
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving recommendations: {e}")
    
    def _load_graph(self) -> None:
        """Load integration graph from file."""
        filepath = os.path.join(self.data_dir, "graph.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    self.integration_graph = IntegrationGraph(**data)
            except Exception as e:
                print(f"Error loading graph: {e}")
    
    def _save_graph(self) -> None:
        """Save integration graph to file."""
        if not self.integration_graph:
            return
        
        filepath = os.path.join(self.data_dir, "graph.json")
        try:
            data = {
                'graph_id': self.integration_graph.graph_id,
                'tools': self.integration_graph.tools,
                'integrations': self.integration_graph.integrations,
                'adjacency': self.integration_graph.adjacency,
                'created_at': self.integration_graph.created_at,
                'last_updated': self.integration_graph.last_updated
            }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving graph: {e}")


if __name__ == "__main__":
    # Example usage
    explorer = IntegrationExplorer()
    
    # Discover a new integration
    integration = explorer.discover_integration(
        name="Slack Notifications",
        source_tool="CI/CD",
        target_tool="Slack",
        integration_type=IntegrationType.WEBHOOK.value,
        pattern=IntegrationPattern.EVENT_DRIVEN.value,
        description="Send build notifications to Slack",
        use_cases=["notifications", "team_communication", "alerts"],
        benefits=["Real-time updates", "Team visibility", "Easy setup"],
        setup_steps=[
            "Create Slack webhook URL",
            "Configure CI/CD to send webhooks",
            "Test notification"
        ],
        complexity=IntegrationComplexity.SIMPLE.value
    )
    
    print(f"\nDiscovered integration: {integration.name}")
    print(f"Complexity: {integration.complexity}")
    
    # Check compatibility
    compatibility = explorer.check_compatibility("GitHub", "CI/CD")
    print(f"\nGitHub + CI/CD compatible: {compatibility['compatible']}")
    print(f"Existing integrations: {compatibility['integration_count']}")
    
    # Get recommendations
    recommendations = explorer.recommend_integration(
        use_case="continuous_integration",
        requirements=["automated_testing", "easy_setup"]
    )
    
    print(f"\nRecommendations for continuous integration:")
    for rec in recommendations[:3]:
        print(f"- {rec['name']}: {rec['score']:.2f}")
    
    # Get integration path
    paths = explorer.get_integration_path("GitHub", "Kubernetes")
    if paths:
        print(f"\nIntegration paths from GitHub to Kubernetes:")
        for path in paths[:3]:
            print(f"- {' -> '.join(path)}")
    
    # Get summary
    summary = explorer.get_integration_summary()
    print(f"\nIntegration Summary:")
    print(f"Total integrations: {summary['total_integrations']}")
    print(f"Total tools: {summary['total_tools']}")
    print(f"Avg success rate: {summary['avg_success_rate']:.2f}")
