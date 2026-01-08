"""
DEPRECATED: OpportunityPipelineOrchestrator has been moved to core/services/opportunity_pipeline_orchestrator.py

Session 727: Migration to eliminate deprecated agents/ imports.

Use: from core.services.opportunity_pipeline_orchestrator import OpportunityPipelineOrchestrator
"""
import warnings

warnings.warn(
    "Importing from 'agents.opportunity_pipeline_orchestrator' is deprecated. "
    "Use 'from core.services.opportunity_pipeline_orchestrator import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything for backwards compatibility
from core.services.opportunity_pipeline_orchestrator import (
    # Mixins
    PipelineLearningMixin,
    # Enums
    PipelineStage,
    # Dataclasses
    OpportunityContext,
    StageResult,
    # Main class
    OpportunityPipelineOrchestrator,
)

__all__ = [
    'PipelineLearningMixin',
    'PipelineStage',
    'OpportunityContext',
    'StageResult',
    'OpportunityPipelineOrchestrator',
]
