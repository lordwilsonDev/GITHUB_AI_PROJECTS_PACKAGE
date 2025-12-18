"""Background Process Optimization Feature.

This module provides automated task identification, micro-automation generation,
and workflow optimization capabilities.
"""

from .task_identifier import RepetitiveTaskIdentifier
from .automation_generator import MicroAutomationGenerator
from .automation_sandbox import AutomationSandbox
from .performance_monitor import PerformanceMonitor
from .workflow_analyzer import WorkflowAnalyzer
from .optimization_engine import OptimizationEngine
from .efficiency_tracker import EfficiencyTracker

__all__ = [
    'RepetitiveTaskIdentifier',
    'MicroAutomationGenerator',
    'AutomationSandbox',
    'PerformanceMonitor',
    'WorkflowAnalyzer',
    'OptimizationEngine',
    'EfficiencyTracker',
]
