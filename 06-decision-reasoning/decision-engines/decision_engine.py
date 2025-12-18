#!/usr/bin/env python3
"""
Decision Engine: Autonomous Decision-Making for Level 9

Multi-criteria optimization engine for autonomous system decisions.
Makes intelligent choices about repairs, resource allocation, and task prioritization.

Author: MoIE-OS Architecture Team
Date: 2025-12-15
Version: 1.0.0
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Types of autonomous decisions."""
    REPAIR = "repair"
    RESOURCE_ALLOCATION = "resource_allocation"
    TASK_PRIORITY = "task_priority"
    MODEL_SELECTION = "model_selection"
    CLEANUP = "cleanup"


class RiskLevel(Enum):
    """Risk levels for decisions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DecisionCriteria:
    """Criteria for evaluating decisions."""
    effectiveness: float  # 0-1: How well does this solve the problem?
    safety: float  # 0-1: How safe is this action?
    speed: float  # 0-1: How quickly can this be executed?
    reversibility: float  # 0-1: How easily can this be undone?
    resource_cost: float  # 0-1: How much resources does this consume?
    
    def weighted_score(self, weights: Dict[str, float]) -> float:
        """Calculate weighted score based on criteria weights."""
        return (
            self.effectiveness * weights.get('effectiveness', 0.3) +
            self.safety * weights.get('safety', 0.3) +
            self.speed * weights.get('speed', 0.15) +
            self.reversibility * weights.get('reversibility', 0.15) +
            (1 - self.resource_cost) * weights.get('resource_cost', 0.1)
        )


@dataclass
class DecisionOption:
    """A possible decision option."""
    option_id: str
    decision_type: DecisionType
    description: str
    criteria: DecisionCriteria
    estimated_duration: float
    prerequisites: List[str]
    side_effects: List[str]
    confidence: float


@dataclass
class Decision:
    """A made decision with full context."""
    decision_id: str
    decision_type: DecisionType
    selected_option: DecisionOption
    alternatives_considered: List[DecisionOption]
    final_score: float
    risk_level: RiskLevel
    reasoning: str
    timestamp: str
    sha256_receipt: str


class DecisionEngine:
    """
    Autonomous decision-making engine.
    
    Uses multi-criteria optimization to select the best action
    from available options, considering safety, effectiveness,
    speed, reversibility, and resource costs.
    """
    
    def __init__(self, config_path: str = "decision_config.json"):
        self.config_path = Path(config_path)
        self.home_dir = Path.home()
        self.decisions_dir = self.home_dir / ".moie-os" / "decisions"
        self.decisions_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = self._load_config()
        self.decision_history: List[Decision] = []
        
        logger.info("Decision Engine initialized")
    
    def _load_config(self) -> Dict:
        """Load decision engine configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        else:
            default_config = {
                "criteria_weights": {
                    "effectiveness": 0.30,
                    "safety": 0.30,
                    "speed": 0.15,
                    "reversibility": 0.15,
                    "resource_cost": 0.10
                },
                "risk_thresholds": {
                    "low": 0.85,
                    "medium": 0.70,
                    "high": 0.50
                },
                "minimum_confidence": 0.75,
                "require_human_approval_above_risk": "high",
                "enable_learning": True
            }
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config
    
    def evaluate_option(self, option: DecisionOption) -> float:
        """Evaluate a decision option using weighted criteria."""
        weights = self.config["criteria_weights"]
        return option.criteria.weighted_score(weights)
    
    def assess_risk(self, option: DecisionOption) -> RiskLevel:
        """Assess risk level of a decision option."""
        # Risk is inverse of safety and reversibility
        risk_score = 1 - ((option.criteria.safety + option.criteria.reversibility) / 2)
        
        if risk_score < 0.15:
            return RiskLevel.LOW
        elif risk_score < 0.30:
            return RiskLevel.MEDIUM
        elif risk_score < 0.50:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def make_decision(
        self,
        decision_type: DecisionType,
        options: List[DecisionOption],
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Decision]:
        """
        Make an autonomous decision from available options.
        
        Returns the best decision, or None if no option meets criteria.
        """
        if not options:
            logger.warning(f"No options provided for {decision_type.value} decision")
            return None
        
        logger.info(f"Making decision: {decision_type.value} ({len(options)} options)")
        
        # Evaluate all options
        scored_options = []
        for option in options:
            score = self.evaluate_option(option)
            risk = self.assess_risk(option)
            scored_options.append((option, score, risk))
        
        # Sort by score (descending)
        scored_options.sort(key=lambda x: x[1], reverse=True)
        
        # Select best option
        best_option, best_score, best_risk = scored_options[0]
        
        # Check if meets minimum confidence
        if best_option.confidence < self.config["minimum_confidence"]:
            logger.warning(f"Best option confidence too low: {best_option.confidence:.2f}")
            return None
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            best_option, best_score, best_risk, scored_options[1:]
        )
        
        # Create decision
        decision = Decision(
            decision_id=self._generate_id(decision_type.value),
            decision_type=decision_type,
            selected_option=best_option,
            alternatives_considered=[opt for opt, _, _ in scored_options[1:]],
            final_score=best_score,
            risk_level=best_risk,
            reasoning=reasoning,
            timestamp=datetime.now().isoformat(),
            sha256_receipt=""  # Will be set after
        )
        
        # Generate cryptographic receipt
        decision.sha256_receipt = self._generate_receipt(decision)
        
        # Store decision
        self.decision_history.append(decision)
        self._save_decision(decision)
        
        logger.info(f"Decision made: {best_option.description} (score: {best_score:.3f}, risk: {best_risk.value})")
        
        return decision
    
    def _generate_reasoning(self, 
                           selected: DecisionOption,
                           score: float,
                           risk: RiskLevel,
                           alternatives: List[Tuple[DecisionOption, float, RiskLevel]]) -> str:
        """Generate human-readable reasoning for decision."""
        reasoning = f"Selected '{selected.description}' with score {score:.3f} and {risk.value} risk.\n"
        reasoning += f"Criteria: effectiveness={selected.criteria.effectiveness:.2f}, "
        reasoning += f"safety={selected.criteria.safety:.2f}, "
        reasoning += f"speed={selected.criteria.speed:.2f}, "
        reasoning += f"reversibility={selected.criteria.reversibility:.2f}.\n"
        
        if alternatives:
            reasoning += f"Considered {len(alternatives)} alternatives:\n"
            for alt, alt_score, alt_risk in alternatives[:3]:  # Top 3
                reasoning += f"  - {alt.description}: score={alt_score:.3f}, risk={alt_risk.value}\n"
        
        return reasoning
    
    def _generate_id(self, prefix: str) -> str:
        """Generate unique decision ID."""
        timestamp = datetime.now().isoformat()
        data = f"{prefix}_{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _generate_receipt(self, decision: Decision) -> str:
        """Generate cryptographic receipt for decision."""
        # Create a copy without the receipt field for hashing
        decision_dict = asdict(decision)
        decision_dict['sha256_receipt'] = ''  # Exclude from hash
        data = json.dumps(decision_dict, sort_keys=True)
        return hashlib.sha256(data.encode()).hexdigest()
    
    def _save_decision(self, decision: Decision):
        """Save decision to disk for audit trail."""
        filename = f"decision_{decision.decision_id}.json"
        filepath = self.decisions_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(asdict(decision), f, indent=2, default=str)
    
    def get_decision_stats(self) -> Dict[str, Any]:
        """Get statistics about decisions made."""
        if not self.decision_history:
            return {"total_decisions": 0}
        
        by_type = {}
        by_risk = {}
        
        for decision in self.decision_history:
            # Count by type
            dtype = decision.decision_type.value
            by_type[dtype] = by_type.get(dtype, 0) + 1
            
            # Count by risk
            risk = decision.risk_level.value
            by_risk[risk] = by_risk.get(risk, 0) + 1
        
        avg_score = np.mean([d.final_score for d in self.decision_history])
        avg_confidence = np.mean([d.selected_option.confidence for d in self.decision_history])
        
        return {
            "total_decisions": len(self.decision_history),
            "by_type": by_type,
            "by_risk": by_risk,
            "average_score": float(avg_score),
            "average_confidence": float(avg_confidence)
        }


# Predefined decision templates for common scenarios
class DecisionTemplates:
    """Common decision templates for typical scenarios."""
    
    @staticmethod
    def disk_cleanup_options() -> List[DecisionOption]:
        """Options for disk cleanup decisions."""
        return [
            DecisionOption(
                option_id="cleanup_temp",
                decision_type=DecisionType.CLEANUP,
                description="Clean temporary files and caches",
                criteria=DecisionCriteria(
                    effectiveness=0.85,
                    safety=0.95,
                    speed=0.90,
                    reversibility=0.70,
                    resource_cost=0.10
                ),
                estimated_duration=60.0,
                prerequisites=[],
                side_effects=["May need to re-download cached data"],
                confidence=0.92
            ),
            DecisionOption(
                option_id="cleanup_logs",
                decision_type=DecisionType.CLEANUP,
                description="Archive and compress old logs",
                criteria=DecisionCriteria(
                    effectiveness=0.75,
                    safety=0.90,
                    speed=0.70,
                    reversibility=0.85,
                    resource_cost=0.15
                ),
                estimated_duration=120.0,
                prerequisites=[],
                side_effects=["Logs will be compressed"],
                confidence=0.88
            ),
            DecisionOption(
                option_id="cleanup_venv",
                decision_type=DecisionType.CLEANUP,
                description="Remove unused virtual environments",
                criteria=DecisionCriteria(
                    effectiveness=0.90,
                    safety=0.85,
                    speed=0.80,
                    reversibility=0.60,
                    resource_cost=0.05
                ),
                estimated_duration=90.0,
                prerequisites=["Identify unused venvs"],
                side_effects=["May need to recreate venvs"],
                confidence=0.85
            )
        ]
    
    @staticmethod
    def memory_optimization_options() -> List[DecisionOption]:
        """Options for memory optimization decisions."""
        return [
            DecisionOption(
                option_id="clear_caches",
                decision_type=DecisionType.RESOURCE_ALLOCATION,
                description="Clear system and application caches",
                criteria=DecisionCriteria(
                    effectiveness=0.80,
                    safety=0.95,
                    speed=0.95,
                    reversibility=0.90,
                    resource_cost=0.05
                ),
                estimated_duration=30.0,
                prerequisites=[],
                side_effects=["Temporary performance impact"],
                confidence=0.90
            ),
            DecisionOption(
                option_id="restart_services",
                decision_type=DecisionType.RESOURCE_ALLOCATION,
                description="Restart memory-intensive services",
                criteria=DecisionCriteria(
                    effectiveness=0.85,
                    safety=0.75,
                    speed=0.70,
                    reversibility=0.95,
                    resource_cost=0.20
                ),
                estimated_duration=60.0,
                prerequisites=["Identify services to restart"],
                side_effects=["Brief service interruption"],
                confidence=0.82
            )
        ]


if __name__ == "__main__":
    print("=== Decision Engine Demo ===")
    
    engine = DecisionEngine()
    
    print("\nScenario: Disk space critical, need cleanup strategy")
    options = DecisionTemplates.disk_cleanup_options()
    
    print(f"Evaluating {len(options)} options...")
    decision = engine.make_decision(DecisionType.CLEANUP, options)
    
    if decision:
        print(f"\nDecision made: {decision.selected_option.description}")
        print(f"Score: {decision.final_score:.3f}")
        print(f"Risk: {decision.risk_level.value}")
        print(f"Confidence: {decision.selected_option.confidence:.2f}")
        print(f"\nReasoning:\n{decision.reasoning}")
        print(f"\nReceipt: {decision.sha256_receipt}")
    
    print("\nDecision statistics:")
    stats = engine.get_decision_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
