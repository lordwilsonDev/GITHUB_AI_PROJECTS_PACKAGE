"""Feature 01: Continuous Learning Engine

This module provides the core continuous learning capabilities for the
self-evolving AI ecosystem. It monitors user interactions, identifies patterns,
learns from successes and failures, and adapts to user preferences.
"""

from .learning_orchestrator import LearningOrchestrator
from .interaction_monitor import InteractionMonitor
from .pattern_analyzer import PatternAnalyzer
from .success_failure_analyzer import SuccessFailureAnalyzer
from .preference_tracker import PreferenceTracker
from .productivity_analyzer import ProductivityAnalyzer

__all__ = [
    'LearningOrchestrator',
    'InteractionMonitor',
    'PatternAnalyzer',
    'SuccessFailureAnalyzer',
    'PreferenceTracker',
    'ProductivityAnalyzer',
]

__version__ = '1.0.0'
