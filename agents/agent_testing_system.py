"""
DEPRECATED: This module has been moved to core/services/agent_testing_system.py

For new code, use:
    from core.services.agent_testing_system import ...

This shim maintains backwards compatibility.
Session 728: Migrated to core/services/
"""
import warnings

warnings.warn(
    "Importing from 'agents.agent_testing_system' is deprecated. "
    "Use 'from core.services.agent_testing_system import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical location
from core.services.agent_testing_system import *
