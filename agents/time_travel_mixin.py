"""
DEPRECATED: TimeTravelMixin has been moved to core/agents/time_travel_mixin.py

Session 727: Migration to eliminate deprecated agents/ imports.

Use: from core.agents.time_travel_mixin import TimeTravelMixin
"""
import warnings

warnings.warn(
    "Importing from 'agents.time_travel_mixin' is deprecated. "
    "Use 'from core.agents.time_travel_mixin import TimeTravelMixin' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export for backwards compatibility
from core.agents.time_travel_mixin import TimeTravelMixin, time_travel_tracked

__all__ = ['TimeTravelMixin', 'time_travel_tracked']
