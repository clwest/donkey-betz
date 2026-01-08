"""
DEPRECATED: This module has been moved to core/services/platform_integration.py

For new code, use:
    from core.services.platform_integration import ...

This shim maintains backwards compatibility.
Session 728: Migrated to core/services/
"""
import warnings

warnings.warn(
    "Importing from 'agents.platform_integration' is deprecated. "
    "Use 'from core.services.platform_integration import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical location
from core.services.platform_integration import (
    PlatformIntegration,
    platform_integration,
    get_platform_integration,
    inject_platform_tools_prompt,
)
