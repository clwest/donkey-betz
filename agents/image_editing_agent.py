"""
DEPRECATED: Use core.agents.image_editing_agent instead.

This shim redirects to the clean architecture version.
"""
import warnings

warnings.warn(
    "Importing from 'agents.image_editing_agent' is deprecated. "
    "Use 'from core.agents import ImageEditingAgent' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Redirect to clean architecture
from core.agents.image_editing_agent import ImageEditingAgent

__all__ = ['ImageEditingAgent']
