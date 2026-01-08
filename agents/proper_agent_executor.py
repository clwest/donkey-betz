"""
DEPRECATED: ProperAgentExecutor has been moved to core/services/proper_agent_executor.py

Session 727: Migration to eliminate deprecated agents/ imports.

Use: from core.services.proper_agent_executor import ProperAgentExecutor, execute_agents_properly
"""
import warnings

warnings.warn(
    "Importing from 'agents.proper_agent_executor' is deprecated. "
    "Use 'from core.services.proper_agent_executor import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export everything for backwards compatibility
from core.services.proper_agent_executor import (
    ProperAgentExecutor,
    execute_agents_properly,
)

__all__ = [
    'ProperAgentExecutor',
    'execute_agents_properly',
]
