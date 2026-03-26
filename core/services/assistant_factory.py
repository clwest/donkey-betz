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
    """Create a properly wired PA instance.

    Args:
        user: Django User object
        mode: 'default' (PersonalAIAssistant) or 'enhanced' (EnhancedPersonalAIAssistant)

    Returns:
        An assistant instance with registries properly injected.
    """
    if mode == 'enhanced':
        try:
            from core.personal_ai_assistant_enhanced import EnhancedPersonalAIAssistant
            return EnhancedPersonalAIAssistant(user)
        except Exception as e:
            logger.warning(f"Enhanced assistant failed, falling back to default: {e}")

    from core.personal_ai_assistant import PersonalAIAssistant
    return PersonalAIAssistant(user)
