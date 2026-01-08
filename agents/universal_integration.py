"""
DEPRECATED: This module has been moved to core/services/universal_integration.py

For new code, use:
    from core.services.universal_integration import ...

This shim maintains backwards compatibility.
Session 728: Migrated to core/services/
"""
import warnings

warnings.warn(
    "Importing from 'agents.universal_integration' is deprecated. "
    "Use 'from core.services.universal_integration import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical location
from core.services.universal_integration import *
