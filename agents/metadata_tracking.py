"""
DEPRECATED: This module has been moved to core/services/metadata_tracking.py

For new code, use:
    from core.services.metadata_tracking import ...

This shim maintains backwards compatibility.
Session 728: Migrated to core/services/
"""
import warnings

warnings.warn(
    "Importing from 'agents.metadata_tracking' is deprecated. "
    "Use 'from core.services.metadata_tracking import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical location
from core.services.metadata_tracking import *
