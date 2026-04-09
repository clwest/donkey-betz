"""
Assistant Factory — centralized instantiation for all PA variants.

Prevents property/inheritance conflicts by ensuring registries are
injected consistently regardless of which assistant class is used.

Usage:
    from core.services.assistant_factory import get_assistant
    assistant = get_assistant(user)
    response = assistant.process_message("hello", context)
"""

import logging

logger = logging.getLogger(__name__)


def get_assistant(user, mode='default'):
    """DEPRECATED: Legacy PA factory — all traffic routes through Rigby.

    Returns None. Callers should use /api/pa/chat/ endpoint instead.
    """
    logger.warning(
        "get_assistant() is deprecated — legacy PA removed. "
        "All PA traffic routes through Rigby via /api/pa/chat/"
    )
    return None
