"""
DEPRECATED: This module has been moved to core/serializers_agents.py

For new code, use:
    from core.serializers_agents import ...

This shim maintains backwards compatibility.
Session 728: Migrated to core/
"""
import warnings

warnings.warn(
    "Importing from 'agents.serializers' is deprecated. "
    "Use 'from core.serializers_agents import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical location
from core.serializers_agents import *
