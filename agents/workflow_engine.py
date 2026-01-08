"""
DEPRECATED: WorkflowEngine has been moved to core/services/workflow_engine.py

Session 727: Migration to eliminate deprecated agents/ imports.

Use: from core.services.workflow_engine import WorkflowEngine, IntentParser, CONTENT_CONFIGS
"""
import warnings

warnings.warn(
    "Importing from 'agents.workflow_engine' is deprecated. "
    "Use 'from core.services.workflow_engine import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything for backwards compatibility
from core.services.workflow_engine import (
    # Enums and configs
    ContentType,
    ContentConfig,
    CONTENT_CONFIGS,
    # Dataclasses
    UserIntent,
    # Classes
    IntentParser,
    PromptEnhancer,
    WorkflowEngine,
)

__all__ = [
    'ContentType',
    'ContentConfig',
    'CONTENT_CONFIGS',
    'UserIntent',
    'IntentParser',
    'PromptEnhancer',
    'WorkflowEngine',
]
