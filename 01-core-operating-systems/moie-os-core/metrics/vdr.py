"""VDR (Vitality/Density Ratio) metrics calculation."""

from math import pow
from typing import Optional
from ..core.models import VDRMetrics
from ..core.constants import ALPHA_DEFAULT


def compute_vdr(
    vitality: float,
    density: float,
    alpha: float = ALPHA_DEFAULT,
) -> VDRMetrics:
    """
    Compute VDR metrics.
    
    VDR = V / D^α
    
    where:
        V = Vitality (usefulness, survival value)
        D = Density (complexity: LOC, cyclomatic, Halstead)
        α > 1 (punishes complexity nonlinearly)
    
    Args:
        vitality: Usefulness score (0.0 to 1.0+)
        density: Complexity score (0.0 to 10.0+)
        alpha: Complexity penalty exponent (default 1.5)
    
    Returns:
        VDRMetrics with calculated VDR and SEM
    """
    # Prevent division by zero
    density_safe = max(density, 1e-6)
    
    # Calculate density penalty
    density_penalty = pow(density_safe, alpha)
    
    # Calculate VDR
    vdr = vitality / density_penalty
    
    # Calculate SEM (Simplicity Extraction Metric)
    # SEM is normalized VDR that indicates "prune now" signal
    sem = vdr / (1.0 + vdr)  # Sigmoid-like normalization
    
    return VDRMetrics(
        vitality=vitality,
        density=density,
        alpha=alpha,
        vdr=vdr,
        sem=sem,
    )


def estimate_code_density(
    lines_of_code: int,
    cyclomatic_complexity: Optional[int] = None,
    num_dependencies: Optional[int] = None,
) -> float:
    """
    Estimate density from code metrics.
    
    Args:
        lines_of_code: Total lines of code
        cyclomatic_complexity: McCabe complexity
        num_dependencies: Number of external dependencies
    
    Returns:
        Density score (0.0 to 10.0+)
    """
    # Base density from LOC (normalized to 0-10 scale)
    base_density = min(lines_of_code / 100.0, 10.0)
    
    # Add cyclomatic complexity penalty
    if cyclomatic_complexity:
        complexity_penalty = min(cyclomatic_complexity / 10.0, 5.0)
        base_density += complexity_penalty
    
    # Add dependency penalty
    if num_dependencies:
        dependency_penalty = min(num_dependencies / 5.0, 3.0)
        base_density += dependency_penalty
    
    return min(base_density, 10.0)


def estimate_vitality(
    usage_count: int,
    impact_score: float,
    recency_days: int,
) -> float:
    """
    Estimate vitality from usage metrics.
    
    Args:
        usage_count: Number of times used
        impact_score: Impact/importance score (0.0 to 1.0)
        recency_days: Days since last use
    
    Returns:
        Vitality score (0.0 to 1.0+)
    """
    # Usage contribution (logarithmic)
    usage_contribution = min(pow(usage_count, 0.5) / 10.0, 0.5)
    
    # Impact contribution
    impact_contribution = impact_score * 0.3
    
    # Recency contribution (decay over time)
    recency_contribution = max(0.0, 0.2 * (1.0 - recency_days / 365.0))
    
    return usage_contribution + impact_contribution + recency_contribution
