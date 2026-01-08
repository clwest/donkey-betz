"""
DEPRECATED: This module has been moved to core/agents/bookmaker_agent.py

For new code, use:
    from core.agents.bookmaker_agent import BookmakerAgent

This shim maintains backwards compatibility.
Session 728: Migrated to core/agents/
"""
import warnings

warnings.warn(
    "Importing from 'agents.bookmaker_agent' is deprecated. "
    "Use 'from core.agents.bookmaker_agent import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical location
from core.agents.bookmaker_agent import *
