"""
DEPRECATED: Use core.agents.video_editing_agent instead.

This shim redirects to the clean architecture version.
"""
import warnings

warnings.warn(
    "Importing from 'agents.video_editing_agent' is deprecated. "
    "Use 'from core.agents import VideoEditingAgent' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Redirect to clean architecture
from core.agents.video_editing_agent import VideoEditingAgent

__all__ = ['VideoEditingAgent']
