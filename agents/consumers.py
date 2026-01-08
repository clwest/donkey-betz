"""
DEPRECATED: This module has been moved to core/consumers_agents.py

For new code, use:
    from core.consumers_agents import ...

This shim maintains backwards compatibility.
Session 728: Migrated to core/
"""
import warnings

warnings.warn(
    "Importing from 'agents.consumers' is deprecated. "
    "Use 'from core.consumers_agents import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical location
from core.consumers_agents import *
