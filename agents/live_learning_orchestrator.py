"""
DEPRECATED: LiveLearningOrchestrator has been moved to core/services/live_learning_orchestrator.py

Session 727: Migration to eliminate deprecated agents/ imports.

Use: from core.services.live_learning_orchestrator import LiveLearningOrchestrator
"""
import warnings

warnings.warn(
    "Importing from 'agents.live_learning_orchestrator' is deprecated. "
    "Use 'from core.services.live_learning_orchestrator import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything for backwards compatibility
from core.services.live_learning_orchestrator import (
    LiveLearningLearningMixin,
    LiveLearningOrchestrator,
    run_live_learning_demo,
)

__all__ = [
    'LiveLearningLearningMixin',
    'LiveLearningOrchestrator',
    'run_live_learning_demo',
]
