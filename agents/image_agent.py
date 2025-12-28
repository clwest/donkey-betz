"""
DEPRECATED: This module has been moved to agents/_deprecated/image_agent.py

For new code, use:
    from core.agents import ImageAgent

This shim maintains backwards compatibility while emitting deprecation warnings.
"""
import warnings

warnings.warn(
    "Importing from 'agents.image_agent' is deprecated. "
    "Use 'from core.agents import ImageAgent' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from deprecated location for backwards compatibility
