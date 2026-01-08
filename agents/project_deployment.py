"""
DEPRECATED: This module has been moved to core/services/project_deployment.py

For new code, use:
    from core.services.project_deployment import ...

This shim maintains backwards compatibility.
Session 728: Migrated to core/services/
"""
import warnings

warnings.warn(
    "Importing from 'agents.project_deployment' is deprecated. "
    "Use 'from core.services.project_deployment import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical location
from core.services.project_deployment import *
