"""
AI Income Builder System - DEPRECATION SHIM

Session 727 Consolidation:
This module has been consolidated into ai_core/intelligence/income_builder.py
to eliminate duplicate implementations that were causing import confusion.

The ai_core version is now canonical and contains:
- Real integrations with agent_registry, advisor_registry, embeddings
- OpenAI integration for AI content generation
- Web search and news API tools for market research
- File generation for portfolios and action plans
- Enhanced ML pipeline with real model connections

All imports are re-exported from the canonical location for backwards compatibility.
The ~45 files importing from intelligence.income_builder will continue to work.

To update your imports (recommended):
    # Old (deprecated):
    from intelligence.income_builder import AIIncomeBuilder

    # New (preferred):
    from ai_core.intelligence.income_builder import AIIncomeBuilder
"""

import warnings

# Issue deprecation warning on import
warnings.warn(
    "intelligence.income_builder is deprecated. "
    "Use ai_core.intelligence.income_builder instead. "
    "(Session 727 consolidation)",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything from the canonical location
# (Session 1086: openai_client removed — now lazy via _get_openai_client() in canonical module)
from ai_core.intelligence.income_builder import (
    # Classes
    WorkflowStep,
    StepType,
    MLPipeline,
    IncomeStream,
    SkillLevel,
    IncomeOpportunity,
    UserProfile,
    AIIncomeBuilder,
    # Module-level objects
    OPENAI_AVAILABLE,
    logger,
    income_builder,
)

# Re-export all for "from intelligence.income_builder import *"
__all__ = [
    'WorkflowStep',
    'StepType',
    'MLPipeline',
    'IncomeStream',
    'SkillLevel',
    'IncomeOpportunity',
    'UserProfile',
    'AIIncomeBuilder',
    'OPENAI_AVAILABLE',
    'logger',
    'income_builder',
]
