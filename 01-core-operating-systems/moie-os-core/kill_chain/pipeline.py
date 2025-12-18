"""Main Kill Chain pipeline orchestration."""

import time
from typing import List
from datetime import datetime

from ..core.models import (
    KillChainInput,
    KillChainResult,
    Stage,
    StageResult,
    ExpertType,
)
from ..metrics.vdr import compute_vdr
from ..governance.lord_wilson import evaluate_alignment

from .targeting import TargetingStage
from .hunter import HunterStage
from .alchemist import AlchemistStage
from .judge import JudgeStage


class KillChainPipeline:
    """
    Main Kill Chain pipeline.
    
    Executes 4 stages:
    1. Targeting - Invert problem, build search manifest
    2. Hunter - Find anomalies and positive deviants
    3. Alchemist - Synthesize minimal mechanisms
    4. Judge - Verify, red-team, calculate VDR
    """
    
    def __init__(self):
        self.targeting = TargetingStage()
        self.hunter = HunterStage()
        self.alchemist = AlchemistStage()
        self.judge = JudgeStage()
    
    def execute(self, payload: KillChainInput) -> KillChainResult:
        """
        Execute full Kill Chain pipeline.
        
        Args:
            payload: Kill Chain input
        
        Returns:
            KillChainResult with all stages and metrics
        """
        start_time = time.time()
        stages: List[StageResult] = []
        
        # Stage 1: Targeting
        stage_start = time.time()
        search_manifest = self.targeting.execute(payload)
        stage_duration = (time.time() - stage_start) * 1000
        
        stages.append(StageResult(
            stage=Stage.TARGETING,
            summary=f"Generated {len(search_manifest.inverse_questions)} inverse questions and {len(search_manifest.search_paths)} search paths",
            artifacts={
                "search_manifest": search_manifest.model_dump(),
            },
            experts_used=[ExpertType.ARCHITECT],
            duration_ms=stage_duration,
            vdr_contribution=0.2,
        ))
        
        # Stage 2: Hunter
        stage_start = time.time()
        anomalies = self.hunter.execute(payload, search_manifest)
        stage_duration = (time.time() - stage_start) * 1000
        
        positive_anomalies = [a for a in anomalies if a.is_positive]
        negative_anomalies = [a for a in anomalies if not a.is_positive]
        
        stages.append(StageResult(
            stage=Stage.HUNTER,
            summary=f"Found {len(positive_anomalies)} positive deviants and {len(negative_anomalies)} warnings",
            artifacts={
                "anomalies": [a.model_dump() for a in anomalies],
                "positive_count": len(positive_anomalies),
                "negative_count": len(negative_anomalies),
            },
            experts_used=[ExpertType.HUNTER],
            duration_ms=stage_duration,
            vdr_contribution=0.3,
        ))
        
        # Stage 3: Alchemist
        stage_start = time.time()
        mechanisms = self.alchemist.execute(payload, search_manifest, anomalies)
        stage_duration = (time.time() - stage_start) * 1000
        
        stages.append(StageResult(
            stage=Stage.ALCHEMIST,
            summary=f"Synthesized {len(mechanisms)} mechanisms with avg complexity {sum(m.estimated_complexity for m in mechanisms) / len(mechanisms):.2f}",
            artifacts={
                "mechanisms": [m.model_dump() for m in mechanisms],
                "count": len(mechanisms),
            },
            experts_used=[ExpertType.ALCHEMIST],
            duration_ms=stage_duration,
            vdr_contribution=0.3,
        ))
        
        # Stage 4: Judge
        stage_start = time.time()
        verification = self.judge.execute(payload, mechanisms)
        stage_duration = (time.time() - stage_start) * 1000
        
        # Calculate VDR from mechanisms
        if mechanisms:
            avg_vitality = sum(m.estimated_impact for m in mechanisms) / len(mechanisms)
            avg_density = sum(m.estimated_complexity for m in mechanisms) / len(mechanisms)
            vdr_metrics = compute_vdr(vitality=avg_vitality, density=avg_density * 10.0)
        else:
            vdr_metrics = compute_vdr(vitality=0.0, density=1.0)
        
        stages.append(StageResult(
            stage=Stage.JUDGE,
            summary=f"Verification {'PASSED' if verification.passed else 'FAILED'} with {len(verification.issues)} issues and confidence {verification.confidence:.2f}",
            artifacts={
                "verification": verification.model_dump(),
                "vdr": vdr_metrics.model_dump(),
            },
            experts_used=[ExpertType.JUDGE, ExpertType.SECURITY],
            duration_ms=stage_duration,
            vdr_contribution=0.2,
        ))
        
        # Calculate total execution time
        execution_time = (time.time() - start_time) * 1000
        
        # Create result
        result = KillChainResult(
            input=payload,
            stages=stages,
            vdr_metrics=vdr_metrics,
            alignment=None,  # Will be set by Lord Wilson
            accepted=False,  # Will be set by Lord Wilson
            timestamp=datetime.now(),
            execution_time_ms=execution_time,
        )
        
        # Evaluate alignment with Lord Wilson
        alignment, accepted = evaluate_alignment(result)
        result.alignment = alignment
        result.accepted = accepted
        
        return result


# Global pipeline instance
pipeline = KillChainPipeline()


def run_kill_chain(payload: KillChainInput) -> KillChainResult:
    """
    Convenience function to run Kill Chain using global pipeline.
    
    Args:
        payload: Kill Chain input
    
    Returns:
        KillChainResult
    """
    return pipeline.execute(payload)
