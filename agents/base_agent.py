"""
DEPRECATED: This module has been moved to core/agents/base_content_agent.py

For new code, use:
    from core.agents.base_content_agent import ...

This shim maintains backwards compatibility.
Session 728: Migrated to core/agents/
"""
import warnings

warnings.warn(
    "Importing from 'agents.base_agent' is deprecated. "
    "Use 'from core.agents.base_content_agent import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical location
from core.agents.base_content_agent import (
    AgentResult,
    BaseContentAgent,
)
