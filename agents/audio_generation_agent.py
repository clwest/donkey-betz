"""
DEPRECATED: AudioGenerationAgent is provided by AudioAgent.

Use core.agents.audio_agent instead.
This shim redirects to the AudioAgent for backwards compatibility.
"""
import warnings

warnings.warn(
    "Importing from 'agents.audio_generation_agent' is deprecated. "
    "Use 'from core.agents import AudioAgent' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export AudioAgent as AudioGenerationAgent for backwards compatibility
from agents._deprecated.audio_agent import AudioAgent as AudioGenerationAgent

# Also export get_audio_agent if it exists
try:
    from agents._deprecated.audio_agent import get_audio_agent
except ImportError:
    get_audio_agent = None

__all__ = ['AudioGenerationAgent']
if get_audio_agent:
    __all__.append('get_audio_agent')
