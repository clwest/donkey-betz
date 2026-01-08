"""
DEPRECATED: This module has been moved to core/services/real_code_generator.py

For new code, use:
    from core.services.real_code_generator import ...

This shim maintains backwards compatibility.
Session 728: Migrated to core/services/
"""
import warnings

warnings.warn(
    "Importing from 'agents.real_code_generator' is deprecated. "
    "Use 'from core.services.real_code_generator import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from canonical location
from core.services.real_code_generator import RealCodeGenerator
