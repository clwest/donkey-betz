"""
DEPRECATED: WorkflowOrchestrationAgent has been moved to core/services/workflow_orchestration_agent.py

Session 727: Migration to eliminate deprecated agents/ imports.

Use: from core.services.workflow_orchestration_agent import WorkflowOrchestrationAgent
"""
import warnings

warnings.warn(
    "Importing from 'agents.workflow_orchestration_agent' is deprecated. "
    "Use 'from core.services.workflow_orchestration_agent import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything for backwards compatibility
from core.services.workflow_orchestration_agent import (
    WorkflowOrchestrationAgent,
)

__all__ = ['WorkflowOrchestrationAgent']
