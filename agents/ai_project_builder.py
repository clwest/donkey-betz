"""
DEPRECATED: This module has been moved to core/services/ai_project_builder.py

For new code, use:
    from core.services.ai_project_builder import ...

This shim maintains backwards compatibility.
Session 728: Migrated to core/services/
"""
import warnings

warnings.warn(
    "Importing from 'agents.ai_project_builder' is deprecated. "
    "Use 'from core.services.ai_project_builder import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical location
from core.services.ai_project_builder import (
    ProjectBuilderLearningMixin,
    AIProjectBuilder,
)
