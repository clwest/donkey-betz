"""
DEPRECATED: AgentPreferenceManager has been moved to core/services/preference_manager.py

Session 727: Migration to eliminate deprecated agents/ imports.

Use: from core.services.preference_manager import AgentPreferenceManager
"""
import warnings

warnings.warn(
    "Importing from 'agents.preference_manager' is deprecated. "
    "Use 'from core.services.preference_manager import AgentPreferenceManager' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export for backwards compatibility
from core.services.preference_manager import (
    AgentPreferenceManager,
    get_user_preferences,
    apply_user_preferences,
)

__all__ = [
    'AgentPreferenceManager',
    'get_user_preferences',
    'apply_user_preferences',
]
