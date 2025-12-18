"""MoIE-OS Protocol - Core Implementation."""

__version__ = "0.1.0"

from .core import (
    Stage,
    ExpertType,
    Invariant,
    AlignmentState,
    VDRMetrics,
    KillChainInput,
    KillChainResult,
)
from .kill_chain import run_kill_chain
from .metrics import compute_vdr
from .governance import evaluate_alignment

__all__ = [
    "__version__",
    "Stage",
    "ExpertType",
    "Invariant",
    "AlignmentState",
    "VDRMetrics",
    "KillChainInput",
    "KillChainResult",
    "run_kill_chain",
    "compute_vdr",
    "evaluate_alignment",
]
