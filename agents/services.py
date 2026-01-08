"""
DEPRECATED: AgentContributionService has been moved to core/services/agent_contribution.py

Session 727: Migration to eliminate deprecated agents/ imports.

Use: from core.services.agent_contribution import AgentContributionService
"""
import warnings

warnings.warn(
    "Importing from 'agents.services' is deprecated. "
    "Use 'from core.services.agent_contribution import AgentContributionService' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export for backwards compatibility
from core.services.agent_contribution import AgentContributionService

__all__ = ['AgentContributionService']
