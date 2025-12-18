#!/usr/bin/env python3
"""
Decision-Making Pattern Analyzer

Analyzes user decision-making patterns to understand:
- Decision types and contexts
- Factors influencing decisions
- Decision quality and outcomes
- Patterns and preferences
- Learning from past decisions

Author: Self-Evolving AI Ecosystem
Date: December 15, 2025
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict, Counter
from enum import Enum


class DecisionType(Enum):
    """Types of decisions."""
    STRATEGIC = "strategic"  # Long-term, high-impact
    TACTICAL = "tactical"  # Medium-term, moderate impact
    OPERATIONAL = "operational"  # Short-term, day-to-day
    CREATIVE = "creative"  # Innovation, design
    ANALYTICAL = "analytical"  # Data-driven, logical
    INTUITIVE = "intuitive"  # Gut feeling, experience-based
    COLLABORATIVE = "collaborative"  # Team-based
    INDEPENDENT = "independent"  # Solo decision


class DecisionOutcome(Enum):
    """Decision outcomes."""
    EXCELLENT = "excellent"
    GOOD = "good"
    NEUTRAL = "neutral"
    POOR = "poor"
    UNKNOWN = "unknown"


class DecisionPatternAnalyzer:
    """
    Analyzes decision-making patterns and preferences.
    
    Features:
    - Decision tracking and categorization
    - Pattern identification
    - Factor analysis
    - Outcome correlation
    - Recommendation generation
    """
    
    def __init__(self, data_dir: str = "~/vy-nexus/data/behavioral_learning"):
        """
        Initialize the decision pattern analyzer.
        
        Args:
            data_dir: Directory to store decision data
        """
        self.data_dir = os.path.expanduser(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.decisions_file = os.path.join(self.data_dir, "decisions.json")
        self.patterns_file = os.path.join(self.data_dir, "decision_patterns.json")
        self.factors_file = os.path.join(self.data_dir, "decision_factors.json")
        self.recommendations_file = os.path.join(self.data_dir, "decision_recommendations.json")
        
        self.decisions = self._load_decisions()
        self.patterns = self._load_patterns()
        self.factors = self._load_factors()
        self.recommendations = self._load_recommendations()
    
    def _load_decisions(self) -> Dict[str, Any]:
        """Load decisions history."""
        if os.path.exists(self.decisions_file):
            with open(self.decisions_file, 'r') as f:
                return json.load(f)
        return {"decisions": []}
    
    def _save_decisions(self):
        """Save decisions."""
        with open(self.decisions_file, 'w') as f:
            json.dump(self.decisions, f, indent=2)
    
    def _load_patterns(self) -> Dict[str, Any]:
        """Load identified patterns."""
        if os.path.exists(self.patterns_file):
            with open(self.patterns_file, 'r') as f:
                return json.load(f)
        return {"patterns": []}
    
    def _save_patterns(self):
        """Save patterns."""
        with open(self.patterns_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def _load_factors(self) -> Dict[str, Any]:
        """Load decision factors."""
        if os.path.exists(self.factors_file):
            with open(self.factors_file, 'r') as f:
                return json.load(f)
        return {"factors": {}}
    
    def _save_factors(self):
        """Save factors."""
        with open(self.factors_file, 'w') as f:
            json.dump(self.factors, f, indent=2)
    
    def _load_recommendations(self) -> Dict[str, Any]:
        """Load recommendations."""
        if os.path.exists(self.recommendations_file):
            with open(self.recommendations_file, 'r') as f:
                return json.load(f)
        return {"recommendations": []}
    
    def _save_recommendations(self):
        """Save recommendations."""
        with open(self.recommendations_file, 'w') as f:
            json.dump(self.recommendations, f, indent=2)
    
    def record_decision(self,
                       decision_type: str,
                       description: str,
                       context: Dict[str, Any],
                       factors_considered: List[str],
                       time_taken_minutes: float,
                       confidence_level: float,
                       alternatives_considered: int = 1,
                       outcome: str = "unknown") -> Dict[str, Any]:
        """
        Record a decision.
        
        Args:
            decision_type: Type of decision
            description: Decision description
            context: Context information
            factors_considered: Factors that influenced decision
            time_taken_minutes: Time spent on decision
            confidence_level: Confidence (0-100)
            alternatives_considered: Number of alternatives evaluated
            outcome: Decision outcome
        
        Returns:
            Decision record
        """
        decision = {
            "decision_id": f"dec_{len(self.decisions['decisions']) + 1:06d}",
            "decision_type": decision_type,
            "description": description,
            "context": context,
            "factors_considered": factors_considered,
            "time_taken_minutes": time_taken_minutes,
            "confidence_level": confidence_level,
            "alternatives_considered": alternatives_considered,
            "outcome": outcome,
            "timestamp": datetime.now().isoformat(),
            "updated_at": None
        }
        
        self.decisions["decisions"].append(decision)
        self._save_decisions()
        
        # Update factor tracking
        for factor in factors_considered:
            if factor not in self.factors["factors"]:
                self.factors["factors"][factor] = {
                    "usage_count": 0,
                    "avg_confidence": 0.0,
                    "outcomes": []
                }
            
            factor_data = self.factors["factors"][factor]
            factor_data["usage_count"] += 1
            factor_data["outcomes"].append(outcome)
            
            # Update average confidence
            all_decisions_with_factor = [d for d in self.decisions["decisions"]
                                        if factor in d["factors_considered"]]
            avg_conf = sum(d["confidence_level"] for d in all_decisions_with_factor) / len(all_decisions_with_factor)
            factor_data["avg_confidence"] = avg_conf
        
        self._save_factors()
        
        # Trigger pattern analysis if enough decisions
        if len(self.decisions["decisions"]) % 10 == 0:
            self.analyze_patterns()
        
        return decision
    
    def update_decision_outcome(self, decision_id: str, outcome: str, notes: str = "") -> bool:
        """
        Update the outcome of a decision.
        
        Args:
            decision_id: Decision to update
            outcome: New outcome
            notes: Additional notes
        
        Returns:
            Success status
        """
        for decision in self.decisions["decisions"]:
            if decision["decision_id"] == decision_id:
                decision["outcome"] = outcome
                decision["outcome_notes"] = notes
                decision["updated_at"] = datetime.now().isoformat()
                self._save_decisions()
                
                # Update factor outcomes
                for factor in decision["factors_considered"]:
                    if factor in self.factors["factors"]:
                        self.factors["factors"][factor]["outcomes"].append(outcome)
                self._save_factors()
                
                return True
        
        return False
    
    def analyze_patterns(self) -> List[Dict[str, Any]]:
        """
        Analyze decision-making patterns.
        
        Returns:
            List of identified patterns
        """
        if len(self.decisions["decisions"]) < 5:
            return []
        
        patterns = []
        
        # Pattern 1: Decision type preferences
        type_counts = Counter(d["decision_type"] for d in self.decisions["decisions"])
        if type_counts:
            most_common_type = type_counts.most_common(1)[0]
            patterns.append({
                "pattern_id": f"pat_{len(patterns) + 1:03d}",
                "pattern_type": "type_preference",
                "description": f"Prefers {most_common_type[0]} decisions",
                "frequency": most_common_type[1],
                "confidence": (most_common_type[1] / len(self.decisions["decisions"])) * 100,
                "identified_at": datetime.now().isoformat()
            })
        
        # Pattern 2: Time investment patterns
        avg_time_by_type = defaultdict(list)
        for d in self.decisions["decisions"]:
            avg_time_by_type[d["decision_type"]].append(d["time_taken_minutes"])
        
        for dec_type, times in avg_time_by_type.items():
            avg_time = sum(times) / len(times)
            if avg_time > 30:  # Significant time investment
                patterns.append({
                    "pattern_id": f"pat_{len(patterns) + 1:03d}",
                    "pattern_type": "time_investment",
                    "description": f"Invests significant time in {dec_type} decisions",
                    "average_time_minutes": avg_time,
                    "confidence": 80.0,
                    "identified_at": datetime.now().isoformat()
                })
        
        # Pattern 3: Confidence patterns
        high_confidence_decisions = [d for d in self.decisions["decisions"]
                                    if d["confidence_level"] >= 80]
        if len(high_confidence_decisions) > len(self.decisions["decisions"]) * 0.6:
            patterns.append({
                "pattern_id": f"pat_{len(patterns) + 1:03d}",
                "pattern_type": "confidence_level",
                "description": "Generally makes decisions with high confidence",
                "percentage": (len(high_confidence_decisions) / len(self.decisions["decisions"])) * 100,
                "confidence": 85.0,
                "identified_at": datetime.now().isoformat()
            })
        
        # Pattern 4: Alternative consideration
        avg_alternatives = sum(d["alternatives_considered"] for d in self.decisions["decisions"]) / len(self.decisions["decisions"])
        if avg_alternatives >= 3:
            patterns.append({
                "pattern_id": f"pat_{len(patterns) + 1:03d}",
                "pattern_type": "thorough_evaluation",
                "description": "Thoroughly evaluates multiple alternatives",
                "average_alternatives": avg_alternatives,
                "confidence": 90.0,
                "identified_at": datetime.now().isoformat()
            })
        
        # Pattern 5: Outcome success rate by type
        for dec_type in type_counts.keys():
            type_decisions = [d for d in self.decisions["decisions"]
                            if d["decision_type"] == dec_type and d["outcome"] != "unknown"]
            if type_decisions:
                successful = sum(1 for d in type_decisions
                               if d["outcome"] in ["excellent", "good"])
                success_rate = (successful / len(type_decisions)) * 100
                
                if success_rate >= 75:
                    patterns.append({
                        "pattern_id": f"pat_{len(patterns) + 1:03d}",
                        "pattern_type": "success_rate",
                        "description": f"High success rate in {dec_type} decisions",
                        "success_rate": success_rate,
                        "confidence": 85.0,
                        "identified_at": datetime.now().isoformat()
                    })
        
        # Save patterns
        self.patterns["patterns"] = patterns
        self._save_patterns()
        
        return patterns
    
    def get_factor_analysis(self) -> Dict[str, Any]:
        """
        Analyze decision factors.
        
        Returns:
            Factor analysis results
        """
        if not self.factors["factors"]:
            return {"message": "No factors tracked yet"}
        
        # Sort factors by usage
        sorted_factors = sorted(
            self.factors["factors"].items(),
            key=lambda x: x[1]["usage_count"],
            reverse=True
        )
        
        # Calculate success rates
        factor_analysis = []
        for factor_name, factor_data in sorted_factors:
            outcomes = factor_data["outcomes"]
            if outcomes:
                successful = sum(1 for o in outcomes if o in ["excellent", "good"])
                success_rate = (successful / len(outcomes)) * 100 if outcomes else 0
            else:
                success_rate = 0
            
            factor_analysis.append({
                "factor": factor_name,
                "usage_count": factor_data["usage_count"],
                "avg_confidence": factor_data["avg_confidence"],
                "success_rate": success_rate,
                "total_outcomes": len(outcomes)
            })
        
        return {
            "total_factors": len(self.factors["factors"]),
            "factors": factor_analysis[:10],  # Top 10
            "most_used_factor": factor_analysis[0] if factor_analysis else None
        }
    
    def generate_recommendations(self, context: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Generate decision-making recommendations.
        
        Args:
            context: Current context
        
        Returns:
            List of recommendations
        """
        recommendations = []
        
        if len(self.decisions["decisions"]) < 5:
            return [{"message": "Need more decision data for recommendations"}]
        
        # Analyze recent decisions
        recent_decisions = self.decisions["decisions"][-20:]
        
        # Recommendation 1: Time management
        avg_time = sum(d["time_taken_minutes"] for d in recent_decisions) / len(recent_decisions)
        if avg_time > 60:
            recommendations.append({
                "recommendation_id": f"rec_{len(recommendations) + 1:03d}",
                "type": "time_management",
                "priority": "medium",
                "description": "Consider setting time limits for decisions",
                "rationale": f"Average decision time is {avg_time:.1f} minutes",
                "suggested_action": "Use timeboxing for non-critical decisions"
            })
        
        # Recommendation 2: Confidence calibration
        decisions_with_outcomes = [d for d in recent_decisions if d["outcome"] != "unknown"]
        if decisions_with_outcomes:
            high_conf_poor_outcome = sum(1 for d in decisions_with_outcomes
                                        if d["confidence_level"] >= 80 and d["outcome"] == "poor")
            if high_conf_poor_outcome > len(decisions_with_outcomes) * 0.2:
                recommendations.append({
                    "recommendation_id": f"rec_{len(recommendations) + 1:03d}",
                    "type": "confidence_calibration",
                    "priority": "high",
                    "description": "Recalibrate confidence assessment",
                    "rationale": "High confidence doesn't always correlate with good outcomes",
                    "suggested_action": "Seek additional perspectives before finalizing decisions"
                })
        
        # Recommendation 3: Alternative exploration
        low_alternatives = sum(1 for d in recent_decisions if d["alternatives_considered"] < 2)
        if low_alternatives > len(recent_decisions) * 0.5:
            recommendations.append({
                "recommendation_id": f"rec_{len(recommendations) + 1:03d}",
                "type": "alternative_exploration",
                "priority": "medium",
                "description": "Explore more alternatives",
                "rationale": "Often considering only one option",
                "suggested_action": "Generate at least 2-3 alternatives for each decision"
            })
        
        # Recommendation 4: Factor consistency
        factor_usage = defaultdict(int)
        for d in recent_decisions:
            for factor in d["factors_considered"]:
                factor_usage[factor] += 1
        
        if len(factor_usage) > 20:  # Too many different factors
            recommendations.append({
                "recommendation_id": f"rec_{len(recommendations) + 1:03d}",
                "type": "factor_consistency",
                "priority": "low",
                "description": "Develop consistent decision framework",
                "rationale": "Using many different factors across decisions",
                "suggested_action": "Identify core factors that matter most"
            })
        
        self.recommendations["recommendations"] = recommendations
        self._save_recommendations()
        
        return recommendations
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get decision-making statistics."""
        if not self.decisions["decisions"]:
            return {"message": "No decisions recorded yet"}
        
        total_decisions = len(self.decisions["decisions"])
        
        # Type distribution
        type_dist = Counter(d["decision_type"] for d in self.decisions["decisions"])
        
        # Average metrics
        avg_time = sum(d["time_taken_minutes"] for d in self.decisions["decisions"]) / total_decisions
        avg_confidence = sum(d["confidence_level"] for d in self.decisions["decisions"]) / total_decisions
        avg_alternatives = sum(d["alternatives_considered"] for d in self.decisions["decisions"]) / total_decisions
        
        # Outcome analysis
        decisions_with_outcomes = [d for d in self.decisions["decisions"] if d["outcome"] != "unknown"]
        if decisions_with_outcomes:
            outcome_dist = Counter(d["outcome"] for d in decisions_with_outcomes)
            success_rate = (sum(outcome_dist[o] for o in ["excellent", "good"]) / len(decisions_with_outcomes)) * 100
        else:
            outcome_dist = {}
            success_rate = 0
        
        return {
            "total_decisions": total_decisions,
            "type_distribution": dict(type_dist),
            "average_time_minutes": avg_time,
            "average_confidence": avg_confidence,
            "average_alternatives_considered": avg_alternatives,
            "decisions_with_outcomes": len(decisions_with_outcomes),
            "outcome_distribution": dict(outcome_dist),
            "success_rate": success_rate,
            "total_patterns_identified": len(self.patterns["patterns"]),
            "total_factors_tracked": len(self.factors["factors"])
        }


def test_decision_pattern_analyzer():
    """Test the decision pattern analyzer."""
    print("=" * 60)
    print("Testing Decision Pattern Analyzer")
    print("=" * 60)
    
    analyzer = DecisionPatternAnalyzer()
    
    # Test 1: Record decision
    print("\n1. Testing decision recording...")
    decision = analyzer.record_decision(
        decision_type="strategic",
        description="Choose new technology stack for project",
        context={"project": "vy-nexus", "urgency": "medium"},
        factors_considered=["scalability", "team_expertise", "cost", "community_support"],
        time_taken_minutes=120,
        confidence_level=85,
        alternatives_considered=3,
        outcome="unknown"
    )
    print(f"   Decision ID: {decision['decision_id']}")
    print(f"   Type: {decision['decision_type']}")
    print(f"   Confidence: {decision['confidence_level']}%")
    print(f"   Factors: {len(decision['factors_considered'])}")
    
    # Test 2: Record more decisions
    print("\n2. Recording additional decisions...")
    for i in range(5):
        analyzer.record_decision(
            decision_type="operational",
            description=f"Daily task prioritization {i+1}",
            context={"day": f"day_{i+1}"},
            factors_considered=["urgency", "impact", "effort"],
            time_taken_minutes=15,
            confidence_level=75,
            alternatives_considered=2,
            outcome="good"
        )
    print(f"   Recorded 5 additional decisions")
    
    # Test 3: Update outcome
    print("\n3. Testing outcome update...")
    success = analyzer.update_decision_outcome(
        decision['decision_id'],
        outcome="excellent",
        notes="Project launched successfully"
    )
    print(f"   Update successful: {success}")
    
    # Test 4: Analyze patterns
    print("\n4. Testing pattern analysis...")
    patterns = analyzer.analyze_patterns()
    print(f"   Patterns identified: {len(patterns)}")
    if patterns:
        print(f"   First pattern: {patterns[0]['description']}")
        print(f"   Confidence: {patterns[0]['confidence']:.1f}%")
    
    # Test 5: Factor analysis
    print("\n5. Testing factor analysis...")
    factor_analysis = analyzer.get_factor_analysis()
    print(f"   Total factors: {factor_analysis['total_factors']}")
    if factor_analysis.get('most_used_factor'):
        most_used = factor_analysis['most_used_factor']
        print(f"   Most used: {most_used['factor']} ({most_used['usage_count']} times)")
    
    # Test 6: Generate recommendations
    print("\n6. Testing recommendation generation...")
    recommendations = analyzer.generate_recommendations()
    print(f"   Recommendations: {len(recommendations)}")
    if recommendations and 'recommendation_id' in recommendations[0]:
        print(f"   First: {recommendations[0]['description']}")
        print(f"   Priority: {recommendations[0]['priority']}")
    
    # Test 7: Get statistics
    print("\n7. Testing statistics...")
    stats = analyzer.get_statistics()
    print(f"   Total decisions: {stats['total_decisions']}")
    print(f"   Average time: {stats['average_time_minutes']:.1f} minutes")
    print(f"   Average confidence: {stats['average_confidence']:.1f}%")
    print(f"   Success rate: {stats['success_rate']:.1f}%")
    
    print("\n" + "=" * 60)
    print("✓ All tests completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_decision_pattern_analyzer()
