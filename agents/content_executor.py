"""
DEPRECATED: This module has been moved to core/services/content_executor.py

For new code, use:
    from core.services.content_executor import ...

This shim maintains backwards compatibility.
Session 728: Migrated to core/services/
"""
import warnings

warnings.warn(
    "Importing from 'agents.content_executor' is deprecated. "
    "Use 'from core.services.content_executor import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical location
from core.services.content_executor import (
    ContentExecutorLearningMixin,
    DonkeyBetzContentExecutor,
    get_content_executor,
    execute_donkey_betz_content,
)
