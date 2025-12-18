#!/usr/bin/env python3
"""
Competitive Intelligence System

This module provides comprehensive competitive intelligence capabilities,
including competitor profiling, competitive positioning analysis, SWOT analysis,
product comparison, market share tracking, and strategic opportunity identification.

Author: Vy-Nexus Self-Evolving AI
Created: December 15, 2025
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Optional, Any
from enum import Enum


class CompetitorSize(Enum):
    """Competitor size categories."""
    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class MarketPosition(Enum):
    """Market position categories."""
    LEADER = "leader"
    CHALLENGER = "challenger"
    FOLLOWER = "follower"
    NICHE = "niche"


class StrategicMove(Enum):
    """Types of strategic moves."""
    PRODUCT_LAUNCH = "product_launch"
    ACQUISITION = "acquisition"
    PARTNERSHIP = "partnership"
    MARKET_EXPANSION = "market_expansion"
    PRICING_CHANGE = "pricing_change"
    REBRANDING = "rebranding"
    TECHNOLOGY_SHIFT = "technology_shift"


class ThreatLevel(Enum):
    """Threat level categories."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


@dataclass
class CompetitorProfile:
    """Profile of a competitor."""
    competitor_id: str
    name: str
    industry: str
    size: str
    market_position: str
    founded_year: Optional[int] = None
    headquarters: Optional[str] = None
    employee_count: Optional[int] = None
    revenue: Optional[float] = None
    market_share: float = 0.0
    products: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    target_markets: List[str] = field(default_factory=list)
    key_technologies: List[str] = field(default_factory=list)
    competitive_advantages: List[str] = field(default_factory=list)
    threat_level: str = ThreatLevel.MEDIUM.value
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class SWOTAnalysis:
    """SWOT analysis for a competitor."""
    analysis_id: str
    competitor_id: str
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]
    overall_assessment: str
    strategic_recommendations: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ProductComparison:
    """Comparison between products."""
    comparison_id: str
    our_product: str
    competitor_product: str
    competitor_id: str
    features_comparison: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    pricing_comparison: Dict[str, float] = field(default_factory=dict)
    performance_comparison: Dict[str, float] = field(default_factory=dict)
    winner: Optional[str] = None
    competitive_gaps: List[str] = field(default_factory=list)
    competitive_advantages: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class StrategicMoveRecord:
    """Record of a competitor's strategic move."""
    move_id: str
    competitor_id: str
    move_type: str
    description: str
    impact_assessment: str
    threat_level: str
    our_response: Optional[str] = None
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class CompetitiveOpportunity:
    """Identified competitive opportunity."""
    opportunity_id: str
    title: str
    description: str
    opportunity_type: str  # market_gap, weakness_exploit, technology_advantage, etc.
    potential_impact: str  # high, medium, low
    required_resources: List[str] = field(default_factory=list)
    estimated_timeframe: Optional[str] = None
    competitors_affected: List[str] = field(default_factory=list)
    identified_at: str = field(default_factory=lambda: datetime.now().isoformat())


class CompetitiveIntelligence:
    """System for competitive intelligence and analysis."""
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/competitive_intelligence"):
        """Initialize the competitive intelligence system."""
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.competitors: Dict[str, Dict] = {}
        self.swot_analyses: Dict[str, Dict] = {}
        self.product_comparisons: Dict[str, Dict] = {}
        self.strategic_moves: Dict[str, Dict] = {}
        self.opportunities: Dict[str, Dict] = {}
        self.intelligence_log: List[Dict] = []
        
        self._load_data()
        self._initialize_common_competitors()
    
    def _load_data(self):
        """Load existing data from disk."""
        files = {
            'competitors.json': 'competitors',
            'swot_analyses.json': 'swot_analyses',
            'product_comparisons.json': 'product_comparisons',
            'strategic_moves.json': 'strategic_moves',
            'opportunities.json': 'opportunities',
            'intelligence_log.json': 'intelligence_log'
        }
        
        for filename, attr in files.items():
            filepath = os.path.join(self.data_dir, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    setattr(self, attr, json.load(f))
    
    def _save_data(self):
        """Save data to disk."""
        data = {
            'competitors.json': self.competitors,
            'swot_analyses.json': self.swot_analyses,
            'product_comparisons.json': self.product_comparisons,
            'strategic_moves.json': self.strategic_moves,
            'opportunities.json': self.opportunities,
            'intelligence_log.json': self.intelligence_log
        }
        
        for filename, content in data.items():
            filepath = os.path.join(self.data_dir, filename)
            with open(filepath, 'w') as f:
                json.dump(content, f, indent=2)
    
    def _initialize_common_competitors(self):
        """Initialize with common competitor examples."""
        if not self.competitors:
            # Example competitors in AI/Tech space
            examples = [
                {
                    'name': 'OpenAI',
                    'industry': 'Artificial Intelligence',
                    'size': CompetitorSize.LARGE.value,
                    'market_position': MarketPosition.LEADER.value,
                    'products': ['ChatGPT', 'GPT-4', 'DALL-E', 'API'],
                    'strengths': ['Advanced AI models', 'Strong brand', 'Microsoft partnership'],
                    'weaknesses': ['High costs', 'API reliability issues'],
                    'key_technologies': ['Large Language Models', 'Reinforcement Learning'],
                    'threat_level': ThreatLevel.HIGH.value
                },
                {
                    'name': 'Anthropic',
                    'industry': 'Artificial Intelligence',
                    'size': CompetitorSize.MEDIUM.value,
                    'market_position': MarketPosition.CHALLENGER.value,
                    'products': ['Claude', 'Claude API'],
                    'strengths': ['Safety-focused', 'Constitutional AI', 'Strong research'],
                    'weaknesses': ['Smaller market share', 'Limited product range'],
                    'key_technologies': ['Constitutional AI', 'Large Language Models'],
                    'threat_level': ThreatLevel.MEDIUM.value
                }
            ]
            
            for example in examples:
                self.profile_competitor(**example)
    
    def profile_competitor(
        self,
        name: str,
        industry: str,
        size: str,
        market_position: str,
        **kwargs
    ) -> CompetitorProfile:
        """Create or update a competitor profile."""
        competitor_id = f"comp_{len(self.competitors) + 1:04d}"
        
        profile = CompetitorProfile(
            competitor_id=competitor_id,
            name=name,
            industry=industry,
            size=size,
            market_position=market_position,
            **kwargs
        )
        
        self.competitors[competitor_id] = asdict(profile)
        
        self._log_activity(
            'competitor_profiled',
            f"Profiled competitor: {name}",
            {'competitor_id': competitor_id}
        )
        
        self._save_data()
        return profile
    
    def update_competitor(
        self,
        competitor_id: str,
        updates: Dict[str, Any]
    ):
        """Update competitor information."""
        if competitor_id not in self.competitors:
            raise ValueError(f"Competitor {competitor_id} not found")
        
        self.competitors[competitor_id].update(updates)
        self.competitors[competitor_id]['last_updated'] = datetime.now().isoformat()
        
        self._log_activity(
            'competitor_updated',
            f"Updated competitor: {self.competitors[competitor_id]['name']}",
            {'competitor_id': competitor_id, 'updates': list(updates.keys())}
        )
        
        self._save_data()
    
    def conduct_swot_analysis(
        self,
        competitor_id: str,
        strengths: List[str],
        weaknesses: List[str],
        opportunities: List[str],
        threats: List[str],
        overall_assessment: str,
        strategic_recommendations: Optional[List[str]] = None
    ) -> SWOTAnalysis:
        """Conduct SWOT analysis for a competitor."""
        if competitor_id not in self.competitors:
            raise ValueError(f"Competitor {competitor_id} not found")
        
        analysis_id = f"swot_{len(self.swot_analyses) + 1:04d}"
        
        analysis = SWOTAnalysis(
            analysis_id=analysis_id,
            competitor_id=competitor_id,
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=opportunities,
            threats=threats,
            overall_assessment=overall_assessment,
            strategic_recommendations=strategic_recommendations or []
        )
        
        self.swot_analyses[analysis_id] = asdict(analysis)
        
        self._log_activity(
            'swot_conducted',
            f"SWOT analysis for {self.competitors[competitor_id]['name']}",
            {'analysis_id': analysis_id}
        )
        
        self._save_data()
        return analysis
    
    def compare_products(
        self,
        our_product: str,
        competitor_product: str,
        competitor_id: str,
        features: Optional[Dict[str, Dict[str, Any]]] = None,
        pricing: Optional[Dict[str, float]] = None,
        performance: Optional[Dict[str, float]] = None
    ) -> ProductComparison:
        """Compare our product with a competitor's product."""
        if competitor_id not in self.competitors:
            raise ValueError(f"Competitor {competitor_id} not found")
        
        comparison_id = f"comp_{len(self.product_comparisons) + 1:04d}"
        
        # Determine winner based on features, pricing, and performance
        winner = self._determine_product_winner(features, pricing, performance)
        
        # Identify gaps and advantages
        gaps, advantages = self._analyze_product_differences(
            features, pricing, performance
        )
        
        comparison = ProductComparison(
            comparison_id=comparison_id,
            our_product=our_product,
            competitor_product=competitor_product,
            competitor_id=competitor_id,
            features_comparison=features or {},
            pricing_comparison=pricing or {},
            performance_comparison=performance or {},
            winner=winner,
            competitive_gaps=gaps,
            competitive_advantages=advantages
        )
        
        self.product_comparisons[comparison_id] = asdict(comparison)
        
        self._log_activity(
            'product_compared',
            f"Compared {our_product} vs {competitor_product}",
            {'comparison_id': comparison_id, 'winner': winner}
        )
        
        self._save_data()
        return comparison
    
    def _determine_product_winner(
        self,
        features: Optional[Dict],
        pricing: Optional[Dict],
        performance: Optional[Dict]
    ) -> str:
        """Determine which product wins the comparison."""
        our_score = 0
        competitor_score = 0
        
        # Features comparison (40% weight)
        if features:
            for feature, values in features.items():
                if values.get('ours', 0) > values.get('theirs', 0):
                    our_score += 0.4
                elif values.get('theirs', 0) > values.get('ours', 0):
                    competitor_score += 0.4
        
        # Pricing comparison (30% weight) - lower is better
        if pricing:
            our_price = pricing.get('ours', float('inf'))
            their_price = pricing.get('theirs', float('inf'))
            if our_price < their_price:
                our_score += 0.3
            elif their_price < our_price:
                competitor_score += 0.3
        
        # Performance comparison (30% weight)
        if performance:
            for metric, values in performance.items():
                if isinstance(values, dict):
                    if values.get('ours', 0) > values.get('theirs', 0):
                        our_score += 0.3
                    elif values.get('theirs', 0) > values.get('ours', 0):
                        competitor_score += 0.3
        
        if our_score > competitor_score:
            return 'ours'
        elif competitor_score > our_score:
            return 'theirs'
        else:
            return 'tie'
    
    def _analyze_product_differences(
        self,
        features: Optional[Dict],
        pricing: Optional[Dict],
        performance: Optional[Dict]
    ) -> tuple:
        """Analyze gaps and advantages in product comparison."""
        gaps = []
        advantages = []
        
        if features:
            for feature, values in features.items():
                if values.get('theirs', 0) > values.get('ours', 0):
                    gaps.append(f"Feature gap: {feature}")
                elif values.get('ours', 0) > values.get('theirs', 0):
                    advantages.append(f"Feature advantage: {feature}")
        
        if pricing:
            our_price = pricing.get('ours', 0)
            their_price = pricing.get('theirs', 0)
            if our_price > their_price:
                gaps.append(f"Pricing gap: ${our_price - their_price} more expensive")
            elif our_price < their_price:
                advantages.append(f"Pricing advantage: ${their_price - our_price} cheaper")
        
        if performance:
            for metric, values in performance.items():
                if isinstance(values, dict):
                    if values.get('theirs', 0) > values.get('ours', 0):
                        gaps.append(f"Performance gap: {metric}")
                    elif values.get('ours', 0) > values.get('theirs', 0):
                        advantages.append(f"Performance advantage: {metric}")
        
        return gaps, advantages
    
    def track_strategic_move(
        self,
        competitor_id: str,
        move_type: str,
        description: str,
        impact_assessment: str,
        threat_level: str,
        our_response: Optional[str] = None
    ) -> StrategicMoveRecord:
        """Track a competitor's strategic move."""
        if competitor_id not in self.competitors:
            raise ValueError(f"Competitor {competitor_id} not found")
        
        move_id = f"move_{len(self.strategic_moves) + 1:04d}"
        
        move = StrategicMoveRecord(
            move_id=move_id,
            competitor_id=competitor_id,
            move_type=move_type,
            description=description,
            impact_assessment=impact_assessment,
            threat_level=threat_level,
            our_response=our_response
        )
        
        self.strategic_moves[move_id] = asdict(move)
        
        # Update competitor threat level if needed
        if threat_level in [ThreatLevel.CRITICAL.value, ThreatLevel.HIGH.value]:
            self.update_competitor(competitor_id, {'threat_level': threat_level})
        
        self._log_activity(
            'strategic_move_tracked',
            f"Tracked {move_type} by {self.competitors[competitor_id]['name']}",
            {'move_id': move_id, 'threat_level': threat_level}
        )
        
        self._save_data()
        return move
    
    def identify_opportunity(
        self,
        title: str,
        description: str,
        opportunity_type: str,
        potential_impact: str,
        required_resources: Optional[List[str]] = None,
        estimated_timeframe: Optional[str] = None,
        competitors_affected: Optional[List[str]] = None
    ) -> CompetitiveOpportunity:
        """Identify a competitive opportunity."""
        opportunity_id = f"opp_{len(self.opportunities) + 1:04d}"
        
        opportunity = CompetitiveOpportunity(
            opportunity_id=opportunity_id,
            title=title,
            description=description,
            opportunity_type=opportunity_type,
            potential_impact=potential_impact,
            required_resources=required_resources or [],
            estimated_timeframe=estimated_timeframe,
            competitors_affected=competitors_affected or []
        )
        
        self.opportunities[opportunity_id] = asdict(opportunity)
        
        self._log_activity(
            'opportunity_identified',
            f"Identified opportunity: {title}",
            {'opportunity_id': opportunity_id, 'impact': potential_impact}
        )
        
        self._save_data()
        return opportunity
    
    def analyze_market_position(
        self,
        our_market_share: float,
        our_strengths: List[str],
        our_weaknesses: List[str]
    ) -> Dict[str, Any]:
        """Analyze our market position relative to competitors."""
        analysis = {
            'our_market_share': our_market_share,
            'our_strengths': our_strengths,
            'our_weaknesses': our_weaknesses,
            'competitors_by_threat': {},
            'market_leaders': [],
            'competitive_gaps': [],
            'competitive_advantages': [],
            'strategic_recommendations': []
        }
        
        # Group competitors by threat level
        for comp_id, comp in self.competitors.items():
            threat = comp['threat_level']
            if threat not in analysis['competitors_by_threat']:
                analysis['competitors_by_threat'][threat] = []
            analysis['competitors_by_threat'][threat].append(comp['name'])
        
        # Identify market leaders
        leaders = [
            comp for comp in self.competitors.values()
            if comp['market_position'] == MarketPosition.LEADER.value
        ]
        analysis['market_leaders'] = [l['name'] for l in leaders]
        
        # Analyze competitive gaps and advantages
        for comp in self.competitors.values():
            for strength in comp['strengths']:
                if strength not in our_strengths:
                    analysis['competitive_gaps'].append(
                        f"{comp['name']}: {strength}"
                    )
            
            for weakness in comp['weaknesses']:
                if weakness not in our_weaknesses:
                    analysis['competitive_advantages'].append(
                        f"Advantage over {comp['name']}: They have {weakness}"
                    )
        
        # Generate strategic recommendations
        analysis['strategic_recommendations'] = self._generate_strategic_recommendations(
            our_market_share,
            our_strengths,
            our_weaknesses,
            analysis['competitive_gaps']
        )
        
        return analysis
    
    def _generate_strategic_recommendations(
        self,
        market_share: float,
        strengths: List[str],
        weaknesses: List[str],
        gaps: List[str]
    ) -> List[str]:
        """Generate strategic recommendations based on analysis."""
        recommendations = []
        
        # Market share based recommendations
        if market_share < 0.1:
            recommendations.append(
                "Focus on niche markets and differentiation to gain initial traction"
            )
        elif market_share < 0.25:
            recommendations.append(
                "Invest in marketing and partnerships to increase market presence"
            )
        else:
            recommendations.append(
                "Maintain market leadership through innovation and customer retention"
            )
        
        # Weakness-based recommendations
        if len(weaknesses) > len(strengths):
            recommendations.append(
                "Prioritize addressing critical weaknesses before pursuing new opportunities"
            )
        
        # Gap-based recommendations
        if len(gaps) > 5:
            recommendations.append(
                "Significant competitive gaps identified - consider strategic partnerships or acquisitions"
            )
        
        return recommendations
    
    def get_competitor_intelligence(
        self,
        competitor_id: str
    ) -> Dict[str, Any]:
        """Get comprehensive intelligence on a competitor."""
        if competitor_id not in self.competitors:
            raise ValueError(f"Competitor {competitor_id} not found")
        
        competitor = self.competitors[competitor_id]
        
        # Get related SWOT analyses
        swot = [
            s for s in self.swot_analyses.values()
            if s['competitor_id'] == competitor_id
        ]
        
        # Get product comparisons
        comparisons = [
            c for c in self.product_comparisons.values()
            if c['competitor_id'] == competitor_id
        ]
        
        # Get strategic moves
        moves = [
            m for m in self.strategic_moves.values()
            if m['competitor_id'] == competitor_id
        ]
        
        return {
            'profile': competitor,
            'swot_analyses': swot,
            'product_comparisons': comparisons,
            'strategic_moves': moves,
            'threat_assessment': self._assess_overall_threat(competitor, moves)
        }
    
    def _assess_overall_threat(
        self,
        competitor: Dict,
        moves: List[Dict]
    ) -> Dict[str, Any]:
        """Assess overall threat level from a competitor."""
        threat_factors = []
        
        # Market position factor
        if competitor['market_position'] == MarketPosition.LEADER.value:
            threat_factors.append("Market leader position")
        
        # Market share factor
        if competitor.get('market_share', 0) > 0.3:
            threat_factors.append("High market share")
        
        # Recent strategic moves
        recent_moves = [
            m for m in moves
            if m['threat_level'] in [ThreatLevel.HIGH.value, ThreatLevel.CRITICAL.value]
        ]
        if recent_moves:
            threat_factors.append(f"{len(recent_moves)} high-threat strategic moves")
        
        # Competitive advantages
        if len(competitor.get('competitive_advantages', [])) > 3:
            threat_factors.append("Multiple competitive advantages")
        
        return {
            'current_threat_level': competitor['threat_level'],
            'threat_factors': threat_factors,
            'recommendation': self._get_threat_response_recommendation(
                competitor['threat_level']
            )
        }
    
    def _get_threat_response_recommendation(self, threat_level: str) -> str:
        """Get recommendation for responding to threat level."""
        responses = {
            ThreatLevel.CRITICAL.value: "Immediate strategic response required - consider major initiatives",
            ThreatLevel.HIGH.value: "Active monitoring and defensive strategies needed",
            ThreatLevel.MEDIUM.value: "Regular monitoring and incremental improvements",
            ThreatLevel.LOW.value: "Periodic monitoring sufficient",
            ThreatLevel.MINIMAL.value: "Minimal attention required"
        }
        return responses.get(threat_level, "Monitor situation")
    
    def find_competitors(
        self,
        industry: Optional[str] = None,
        market_position: Optional[str] = None,
        min_threat_level: Optional[str] = None,
        size: Optional[str] = None
    ) -> List[Dict]:
        """Find competitors matching criteria."""
        results = []
        
        threat_order = {
            ThreatLevel.CRITICAL.value: 5,
            ThreatLevel.HIGH.value: 4,
            ThreatLevel.MEDIUM.value: 3,
            ThreatLevel.LOW.value: 2,
            ThreatLevel.MINIMAL.value: 1
        }
        
        min_threat_value = threat_order.get(min_threat_level, 0) if min_threat_level else 0
        
        for comp_id, comp in self.competitors.items():
            # Apply filters
            if industry and comp['industry'] != industry:
                continue
            if market_position and comp['market_position'] != market_position:
                continue
            if size and comp['size'] != size:
                continue
            if min_threat_level:
                comp_threat_value = threat_order.get(comp['threat_level'], 0)
                if comp_threat_value < min_threat_value:
                    continue
            
            results.append({
                'competitor_id': comp_id,
                **comp
            })
        
        # Sort by threat level (highest first)
        results.sort(
            key=lambda x: threat_order.get(x['threat_level'], 0),
            reverse=True
        )
        
        return results
    
    def get_intelligence_summary(self) -> Dict[str, Any]:
        """Get summary of competitive intelligence."""
        return {
            'total_competitors': len(self.competitors),
            'competitors_by_position': self._count_by_field('market_position'),
            'competitors_by_threat': self._count_by_field('threat_level'),
            'competitors_by_size': self._count_by_field('size'),
            'total_swot_analyses': len(self.swot_analyses),
            'total_product_comparisons': len(self.product_comparisons),
            'total_strategic_moves': len(self.strategic_moves),
            'total_opportunities': len(self.opportunities),
            'high_threat_competitors': len([
                c for c in self.competitors.values()
                if c['threat_level'] in [ThreatLevel.HIGH.value, ThreatLevel.CRITICAL.value]
            ]),
            'recent_activities': len([
                log for log in self.intelligence_log[-10:]
            ])
        }
    
    def _count_by_field(self, field: str) -> Dict[str, int]:
        """Count competitors by a specific field."""
        counts = {}
        for comp in self.competitors.values():
            value = comp.get(field, 'unknown')
            counts[value] = counts.get(value, 0) + 1
        return counts
    
    def _log_activity(self, activity_type: str, description: str, metadata: Dict):
        """Log an intelligence activity."""
        self.intelligence_log.append({
            'timestamp': datetime.now().isoformat(),
            'activity_type': activity_type,
            'description': description,
            'metadata': metadata
        })


if __name__ == '__main__':
    # Example usage
    ci = CompetitiveIntelligence()
    
    # Profile a competitor
    competitor = ci.profile_competitor(
        name="Example Corp",
        industry="Technology",
        size=CompetitorSize.LARGE.value,
        market_position=MarketPosition.CHALLENGER.value,
        products=["Product A", "Product B"],
        strengths=["Strong brand", "Large customer base"],
        weaknesses=["High prices", "Slow innovation"]
    )
    
    print(f"Profiled competitor: {competitor.name}")
    
    # Conduct SWOT analysis
    swot = ci.conduct_swot_analysis(
        competitor.competitor_id,
        strengths=["Market presence", "Resources"],
        weaknesses=["Legacy systems", "Bureaucracy"],
        opportunities=["New markets", "Technology trends"],
        threats=["Disruption", "Competition"],
        overall_assessment="Strong but vulnerable to disruption"
    )
    
    print(f"SWOT analysis completed: {swot.analysis_id}")
    
    # Get summary
    summary = ci.get_intelligence_summary()
    print(f"\nIntelligence Summary:")
    print(f"Total competitors: {summary['total_competitors']}")
    print(f"High threat competitors: {summary['high_threat_competitors']}")
