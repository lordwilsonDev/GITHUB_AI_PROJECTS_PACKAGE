#!/usr/bin/env python3
"""
Tool Research System - Vy-Nexus Technical Learning System

Researches, evaluates, and learns about tools, technologies, and platforms.
Provides recommendations and tracks technology trends.

Author: Vy-Nexus Self-Evolving AI
Created: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum
from collections import defaultdict, Counter
import hashlib


class ToolCategory(Enum):
    """Categories of tools."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    DATABASE = "database"
    CLOUD = "cloud"
    SECURITY = "security"
    PRODUCTIVITY = "productivity"
    AUTOMATION = "automation"
    AI_ML = "ai_ml"


class MaturityLevel(Enum):
    """Maturity level of a tool."""
    EXPERIMENTAL = "experimental"
    ALPHA = "alpha"
    BETA = "beta"
    STABLE = "stable"
    MATURE = "mature"
    LEGACY = "legacy"


@dataclass
class ToolFeature:
    """Represents a feature of a tool."""
    feature_name: str
    description: str
    importance: str  # critical, important, nice_to_have
    availability: bool = True


@dataclass
class ToolProfile:
    """Complete profile of a tool."""
    tool_id: str
    name: str
    category: str
    description: str
    version: str
    maturity_level: str
    
    # Features and capabilities
    features: List[ToolFeature] = field(default_factory=list)
    use_cases: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    
    # Technical details
    languages_supported: List[str] = field(default_factory=list)
    platforms: List[str] = field(default_factory=list)
    integrations: List[str] = field(default_factory=list)
    
    # Evaluation metrics
    learning_curve: str = "medium"  # easy, medium, hard
    performance_rating: float = 0.0  # 0-1
    community_size: str = "medium"  # small, medium, large
    documentation_quality: float = 0.0  # 0-1
    
    # Alternatives and comparisons
    alternatives: List[str] = field(default_factory=list)
    replaces: List[str] = field(default_factory=list)
    
    # Metadata
    researched_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 0
    recommendation_score: float = 0.0


@dataclass
class ToolComparison:
    """Comparison between tools."""
    comparison_id: str
    tools: List[str]
    category: str
    criteria: Dict[str, Dict[str, Any]]  # criterion -> {tool: score}
    winner: Optional[str] = None
    recommendation: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TechnologyTrend:
    """Represents a technology trend."""
    trend_id: str
    technology: str
    category: str
    trend_direction: str  # rising, stable, declining
    momentum: float  # 0-1
    mentions: int = 0
    first_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())


class ToolResearchSystem:
    """System for researching and learning about tools and technologies."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/tool_research"):
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.tools_file = os.path.join(self.data_dir, "tools.json")
        self.comparisons_file = os.path.join(self.data_dir, "comparisons.json")
        self.trends_file = os.path.join(self.data_dir, "trends.json")
        self.research_log_file = os.path.join(self.data_dir, "research_log.json")
        
        self.tools = self._load_tools()
        self.comparisons = self._load_comparisons()
        self.trends = self._load_trends()
        self.research_log = self._load_research_log()
        
        # Initialize with common tools
        self._initialize_common_tools()
    
    def _load_tools(self) -> Dict[str, Dict]:
        """Load tool profiles."""
        if os.path.exists(self.tools_file):
            with open(self.tools_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_tools(self):
        """Save tool profiles."""
        with open(self.tools_file, 'w') as f:
            json.dump(self.tools, f, indent=2)
    
    def _load_comparisons(self) -> Dict[str, Dict]:
        """Load tool comparisons."""
        if os.path.exists(self.comparisons_file):
            with open(self.comparisons_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_comparisons(self):
        """Save tool comparisons."""
        with open(self.comparisons_file, 'w') as f:
            json.dump(self.comparisons, f, indent=2)
    
    def _load_trends(self) -> Dict[str, Dict]:
        """Load technology trends."""
        if os.path.exists(self.trends_file):
            with open(self.trends_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_trends(self):
        """Save technology trends."""
        with open(self.trends_file, 'w') as f:
            json.dump(self.trends, f, indent=2)
    
    def _load_research_log(self) -> List[Dict]:
        """Load research log."""
        if os.path.exists(self.research_log_file):
            with open(self.research_log_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_research_log(self):
        """Save research log."""
        with open(self.research_log_file, 'w') as f:
            json.dump(self.research_log, f, indent=2)
    
    def _initialize_common_tools(self):
        """Initialize with common tools."""
        common_tools = [
            {
                'name': 'Docker',
                'category': ToolCategory.DEPLOYMENT.value,
                'description': 'Container platform',
                'maturity_level': MaturityLevel.MATURE.value,
                'use_cases': ['containerization', 'deployment', 'microservices']
            },
            {
                'name': 'Git',
                'category': ToolCategory.DEVELOPMENT.value,
                'description': 'Version control system',
                'maturity_level': MaturityLevel.MATURE.value,
                'use_cases': ['version_control', 'collaboration', 'code_management']
            },
            {
                'name': 'Kubernetes',
                'category': ToolCategory.DEPLOYMENT.value,
                'description': 'Container orchestration',
                'maturity_level': MaturityLevel.MATURE.value,
                'use_cases': ['orchestration', 'scaling', 'deployment']
            }
        ]
        
        for tool_info in common_tools:
            if tool_info['name'].lower() not in [t['name'].lower() for t in self.tools.values()]:
                self.research_tool(
                    name=tool_info['name'],
                    category=tool_info['category'],
                    description=tool_info['description'],
                    maturity_level=tool_info['maturity_level'],
                    use_cases=tool_info['use_cases']
                )
    
    def research_tool(self, name: str, category: str, description: str,
                     version: str = "latest",
                     maturity_level: str = MaturityLevel.STABLE.value,
                     use_cases: Optional[List[str]] = None,
                     features: Optional[List[Dict]] = None) -> ToolProfile:
        """Research and catalog a new tool."""
        
        tool_id = f"tool_{hashlib.md5(name.lower().encode()).hexdigest()[:12]}"
        
        # Convert feature dicts to ToolFeature objects
        tool_features = []
        if features:
            for f in features:
                tool_features.append(ToolFeature(
                    feature_name=f.get('name', ''),
                    description=f.get('description', ''),
                    importance=f.get('importance', 'nice_to_have')
                ))
        
        profile = ToolProfile(
            tool_id=tool_id,
            name=name,
            category=category,
            description=description,
            version=version,
            maturity_level=maturity_level,
            features=tool_features,
            use_cases=use_cases or []
        )
        
        # Calculate initial recommendation score
        profile.recommendation_score = self._calculate_recommendation_score(profile)
        
        self.tools[tool_id] = asdict(profile)
        
        # Log research
        self._log_research(
            action='research_tool',
            tool_name=name,
            details={'category': category, 'maturity': maturity_level}
        )
        
        self._save_tools()
        
        return profile
    
    def update_tool_info(self, tool_id: str, updates: Dict[str, Any]):
        """Update information about a tool."""
        if tool_id not in self.tools:
            raise ValueError(f"Tool {tool_id} not found")
        
        tool = self.tools[tool_id]
        
        # Update fields
        for key, value in updates.items():
            if key in tool:
                tool[key] = value
        
        tool['last_updated'] = datetime.now().isoformat()
        
        # Recalculate recommendation score
        tool['recommendation_score'] = self._calculate_recommendation_score(
            ToolProfile(**tool)
        )
        
        self._save_tools()
    
    def add_tool_feature(self, tool_id: str, feature_name: str,
                        description: str, importance: str = "nice_to_have"):
        """Add a feature to a tool."""
        if tool_id not in self.tools:
            raise ValueError(f"Tool {tool_id} not found")
        
        feature = ToolFeature(
            feature_name=feature_name,
            description=description,
            importance=importance
        )
        
        self.tools[tool_id]['features'].append(asdict(feature))
        self.tools[tool_id]['last_updated'] = datetime.now().isoformat()
        
        self._save_tools()
    
    def compare_tools(self, tool_ids: List[str],
                     criteria: Optional[List[str]] = None) -> ToolComparison:
        """Compare multiple tools."""
        
        if not all(tid in self.tools for tid in tool_ids):
            raise ValueError("One or more tools not found")
        
        tools = [self.tools[tid] for tid in tool_ids]
        
        # Default criteria
        if not criteria:
            criteria = [
                'learning_curve',
                'performance_rating',
                'documentation_quality',
                'community_size',
                'maturity_level'
            ]
        
        # Build comparison
        comparison_criteria = {}
        
        for criterion in criteria:
            comparison_criteria[criterion] = {}
            
            for tool in tools:
                if criterion in tool:
                    value = tool[criterion]
                    
                    # Normalize values for comparison
                    if criterion == 'learning_curve':
                        score = {'easy': 1.0, 'medium': 0.6, 'hard': 0.3}.get(value, 0.5)
                    elif criterion == 'community_size':
                        score = {'large': 1.0, 'medium': 0.6, 'small': 0.3}.get(value, 0.5)
                    elif criterion == 'maturity_level':
                        score = {
                            MaturityLevel.MATURE.value: 1.0,
                            MaturityLevel.STABLE.value: 0.8,
                            MaturityLevel.BETA.value: 0.5,
                            MaturityLevel.ALPHA.value: 0.3,
                            MaturityLevel.EXPERIMENTAL.value: 0.1
                        }.get(value, 0.5)
                    else:
                        score = float(value) if isinstance(value, (int, float)) else 0.5
                    
                    comparison_criteria[criterion][tool['name']] = score
        
        # Determine winner
        total_scores = defaultdict(float)
        for criterion, scores in comparison_criteria.items():
            for tool_name, score in scores.items():
                total_scores[tool_name] += score
        
        winner = max(total_scores.items(), key=lambda x: x[1])[0] if total_scores else None
        
        # Generate recommendation
        recommendation = self._generate_comparison_recommendation(
            tools, comparison_criteria, winner
        )
        
        comparison_id = f"comp_{hashlib.md5(str(tool_ids).encode()).hexdigest()[:12]}"
        
        comparison = ToolComparison(
            comparison_id=comparison_id,
            tools=[t['name'] for t in tools],
            category=tools[0]['category'],
            criteria=comparison_criteria,
            winner=winner,
            recommendation=recommendation
        )
        
        self.comparisons[comparison_id] = asdict(comparison)
        self._save_comparisons()
        
        return comparison
    
    def find_alternatives(self, tool_id: str, max_results: int = 5) -> List[Dict]:
        """Find alternative tools."""
        if tool_id not in self.tools:
            raise ValueError(f"Tool {tool_id} not found")
        
        target_tool = self.tools[tool_id]
        target_category = target_tool['category']
        target_use_cases = set(target_tool['use_cases'])
        
        alternatives = []
        
        for tid, tool in self.tools.items():
            if tid == tool_id:
                continue
            
            # Same category
            if tool['category'] != target_category:
                continue
            
            # Calculate similarity
            tool_use_cases = set(tool['use_cases'])
            overlap = len(target_use_cases.intersection(tool_use_cases))
            total = len(target_use_cases.union(tool_use_cases))
            
            similarity = overlap / total if total > 0 else 0
            
            if similarity > 0.3:  # At least 30% similar
                alternatives.append({
                    'tool_id': tid,
                    'name': tool['name'],
                    'similarity': similarity,
                    'recommendation_score': tool['recommendation_score']
                })
        
        # Sort by similarity and recommendation score
        alternatives.sort(
            key=lambda x: (x['similarity'], x['recommendation_score']),
            reverse=True
        )
        
        return alternatives[:max_results]
    
    def track_trend(self, technology: str, category: str,
                   context: Optional[str] = None):
        """Track a technology trend."""
        
        trend_id = f"trend_{hashlib.md5(technology.lower().encode()).hexdigest()[:12]}"
        
        if trend_id in self.trends:
            # Update existing trend
            trend = self.trends[trend_id]
            trend['mentions'] += 1
            trend['last_seen'] = datetime.now().isoformat()
            
            # Calculate momentum
            first_seen = datetime.fromisoformat(trend['first_seen'])
            days_tracked = (datetime.now() - first_seen).days + 1
            trend['momentum'] = min(1.0, trend['mentions'] / (days_tracked * 0.5))
            
            # Determine trend direction
            if trend['momentum'] > 0.7:
                trend['trend_direction'] = 'rising'
            elif trend['momentum'] < 0.3:
                trend['trend_direction'] = 'declining'
            else:
                trend['trend_direction'] = 'stable'
        else:
            # Create new trend
            trend = TechnologyTrend(
                trend_id=trend_id,
                technology=technology,
                category=category,
                trend_direction='rising',
                momentum=0.5,
                mentions=1
            )
            self.trends[trend_id] = asdict(trend)
        
        self._save_trends()
    
    def recommend_tool(self, use_case: str, category: Optional[str] = None,
                      constraints: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """Recommend tools for a specific use case."""
        
        constraints = constraints or {}
        recommendations = []
        
        for tool_id, tool in self.tools.items():
            # Filter by category if specified
            if category and tool['category'] != category:
                continue
            
            # Check if tool matches use case
            if use_case.lower() not in [uc.lower() for uc in tool['use_cases']]:
                continue
            
            # Check constraints
            if 'min_maturity' in constraints:
                maturity_order = [
                    MaturityLevel.EXPERIMENTAL.value,
                    MaturityLevel.ALPHA.value,
                    MaturityLevel.BETA.value,
                    MaturityLevel.STABLE.value,
                    MaturityLevel.MATURE.value
                ]
                tool_maturity_idx = maturity_order.index(tool['maturity_level'])
                min_maturity_idx = maturity_order.index(constraints['min_maturity'])
                
                if tool_maturity_idx < min_maturity_idx:
                    continue
            
            if 'max_learning_curve' in constraints:
                curve_order = ['easy', 'medium', 'hard']
                tool_curve_idx = curve_order.index(tool['learning_curve'])
                max_curve_idx = curve_order.index(constraints['max_learning_curve'])
                
                if tool_curve_idx > max_curve_idx:
                    continue
            
            recommendations.append({
                'tool_id': tool_id,
                'name': tool['name'],
                'description': tool['description'],
                'recommendation_score': tool['recommendation_score'],
                'learning_curve': tool['learning_curve'],
                'maturity_level': tool['maturity_level']
            })
        
        # Sort by recommendation score
        recommendations.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        return recommendations
    
    def record_tool_usage(self, tool_id: str, success: bool = True,
                         feedback: Optional[str] = None):
        """Record tool usage to improve recommendations."""
        if tool_id not in self.tools:
            raise ValueError(f"Tool {tool_id} not found")
        
        tool = self.tools[tool_id]
        tool['usage_count'] += 1
        
        # Adjust recommendation score based on success
        if success:
            tool['recommendation_score'] = min(1.0, tool['recommendation_score'] + 0.05)
        else:
            tool['recommendation_score'] = max(0.0, tool['recommendation_score'] - 0.02)
        
        # Log usage
        self._log_research(
            action='tool_usage',
            tool_name=tool['name'],
            details={'success': success, 'feedback': feedback}
        )
        
        self._save_tools()
    
    def _calculate_recommendation_score(self, profile: ToolProfile) -> float:
        """Calculate recommendation score for a tool."""
        score = 0.5  # Base score
        
        # Maturity bonus
        maturity_scores = {
            MaturityLevel.MATURE.value: 0.2,
            MaturityLevel.STABLE.value: 0.15,
            MaturityLevel.BETA.value: 0.05,
            MaturityLevel.ALPHA.value: 0.0,
            MaturityLevel.EXPERIMENTAL.value: -0.1
        }
        score += maturity_scores.get(profile.maturity_level, 0)
        
        # Learning curve bonus (easier is better)
        curve_scores = {'easy': 0.15, 'medium': 0.05, 'hard': -0.05}
        score += curve_scores.get(profile.learning_curve, 0)
        
        # Documentation quality
        score += profile.documentation_quality * 0.1
        
        # Performance rating
        score += profile.performance_rating * 0.1
        
        # Community size
        community_scores = {'large': 0.1, 'medium': 0.05, 'small': 0.0}
        score += community_scores.get(profile.community_size, 0)
        
        return max(0.0, min(1.0, score))
    
    def _generate_comparison_recommendation(self, tools: List[Dict],
                                           criteria: Dict,
                                           winner: Optional[str]) -> str:
        """Generate recommendation text from comparison."""
        if not winner:
            return "No clear winner. Consider specific use case requirements."
        
        recommendation = f"Recommended: {winner}\n\n"
        recommendation += "Reasoning:\n"
        
        # Find winner's strengths
        for criterion, scores in criteria.items():
            if winner in scores:
                winner_score = scores[winner]
                avg_score = sum(scores.values()) / len(scores)
                
                if winner_score > avg_score * 1.2:
                    recommendation += f"- Excels in {criterion.replace('_', ' ')}\n"
        
        return recommendation
    
    def _log_research(self, action: str, tool_name: str, details: Dict[str, Any]):
        """Log research activity."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'tool_name': tool_name,
            'details': details
        }
        
        self.research_log.append(log_entry)
        self._save_research_log()
    
    def get_tool_profile(self, tool_id: str) -> Optional[Dict]:
        """Get complete profile of a tool."""
        return self.tools.get(tool_id)
    
    def get_trending_technologies(self, category: Optional[str] = None,
                                 min_momentum: float = 0.5) -> List[Dict]:
        """Get trending technologies."""
        trends = []
        
        for trend_id, trend in self.trends.items():
            if category and trend['category'] != category:
                continue
            
            if trend['momentum'] >= min_momentum:
                trends.append(trend)
        
        # Sort by momentum
        trends.sort(key=lambda x: x['momentum'], reverse=True)
        
        return trends
    
    def get_research_summary(self) -> Dict[str, Any]:
        """Get summary of research activities."""
        summary = {
            'total_tools': len(self.tools),
            'tools_by_category': defaultdict(int),
            'tools_by_maturity': defaultdict(int),
            'total_comparisons': len(self.comparisons),
            'trending_count': len([t for t in self.trends.values() if t['momentum'] > 0.6]),
            'most_used_tools': [],
            'recent_research': self.research_log[-10:] if len(self.research_log) > 10 else self.research_log
        }
        
        # Categorize tools
        for tool in self.tools.values():
            summary['tools_by_category'][tool['category']] += 1
            summary['tools_by_maturity'][tool['maturity_level']] += 1
        
        # Most used tools
        tools_by_usage = sorted(
            self.tools.items(),
            key=lambda x: x[1]['usage_count'],
            reverse=True
        )[:5]
        
        summary['most_used_tools'] = [
            {'name': t[1]['name'], 'usage_count': t[1]['usage_count']}
            for t in tools_by_usage
        ]
        
        return summary


if __name__ == "__main__":
    # Example usage
    research = ToolResearchSystem()
    
    # Research a new tool
    tool = research.research_tool(
        name="Terraform",
        category=ToolCategory.DEPLOYMENT.value,
        description="Infrastructure as Code tool",
        maturity_level=MaturityLevel.MATURE.value,
        use_cases=['infrastructure', 'cloud', 'automation'],
        features=[
            {'name': 'multi_cloud', 'description': 'Works with multiple cloud providers', 'importance': 'critical'},
            {'name': 'state_management', 'description': 'Tracks infrastructure state', 'importance': 'important'}
        ]
    )
    
    print(f"\nResearched tool: {tool.name}")
    print(f"Recommendation score: {tool.recommendation_score:.2f}")
    
    # Find alternatives
    alternatives = research.find_alternatives(tool.tool_id)
    print(f"\nAlternatives to {tool.name}:")
    for alt in alternatives:
        print(f"- {alt['name']} (similarity: {alt['similarity']:.2f})")
    
    # Get recommendations
    recommendations = research.recommend_tool(
        use_case='deployment',
        constraints={'min_maturity': MaturityLevel.STABLE.value}
    )
    
    print(f"\nRecommended tools for deployment:")
    for rec in recommendations[:3]:
        print(f"- {rec['name']}: {rec['recommendation_score']:.2f}")
    
    # Track trend
    research.track_trend('AI Agents', ToolCategory.AI_ML.value)
    
    # Get summary
    summary = research.get_research_summary()
    print(f"\nResearch Summary:")
    print(f"Total tools: {summary['total_tools']}")
    print(f"Total comparisons: {summary['total_comparisons']}")
    print(f"Trending technologies: {summary['trending_count']}")
