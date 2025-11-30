"""
DEPRECATED: This module has been moved to agents/_deprecated/

For new code, use imports from core.agents instead.
This shim maintains backwards compatibility while emitting deprecation warnings.
"""
import warnings

warnings.warn(
    f"Importing from 'agents.content_strategy_agent' is deprecated. "
    "Use imports from 'core.agents' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export from deprecated location for backwards compatibility
from agents._deprecated.content_strategy_agent import *
