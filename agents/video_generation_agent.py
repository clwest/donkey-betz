"""
DEPRECATED: VideoGenerationAgent was merged into VideoAgent.

Use core.agents.video_agent instead.
This shim redirects to the unified VideoAgent for backwards compatibility.
"""
import warnings

warnings.warn(
    "Importing from 'agents.video_generation_agent' is deprecated. "
    "VideoGenerationAgent was merged into VideoAgent. "
    "Use 'from core.agents import VideoAgent' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export VideoAgent as VideoGenerationAgent for backwards compatibility
from agents._deprecated.video_agent import VideoAgent as VideoGenerationAgent

__all__ = ['VideoGenerationAgent']
