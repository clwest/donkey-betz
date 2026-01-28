"""
API Helper Functions
Common utilities for API responses.

Session 850: Added smart_truncate for cleaner text truncation at sentence boundaries.
"""

import re
from django.http import JsonResponse


def smart_truncate(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Session 850: Truncate text at sentence boundaries for cleaner display.

    Instead of cutting mid-word/sentence, finds the last complete sentence
    that fits within max_length. Falls back to word boundary if no sentence
    fits.

    Args:
        text: The text to truncate
        max_length: Maximum length (default 500)
        suffix: Suffix to add when truncated (default "...")

    Returns:
        Truncated text ending at a sentence boundary when possible
    """
    if not text:
        return ""

    text = str(text).strip()

    # If it fits, return as-is
    if len(text) <= max_length:
        return text

    # Leave room for suffix
    effective_max = max_length - len(suffix)
    if effective_max <= 0:
        return text[:max_length]

    # Get the truncatable portion
    truncated = text[:effective_max]

    # Try to find last sentence boundary (. ! ? followed by space or end)
    # Match sentences that end with punctuation
    sentence_end = re.search(r'[.!?](?:\s|$)', truncated[::-1])
    if sentence_end:
        # Found a sentence boundary - cut there
        cut_pos = effective_max - sentence_end.start()
        if cut_pos > max_length * 0.3:  # At least 30% of content kept
            return text[:cut_pos].rstrip()

    # No sentence boundary - try word boundary
    last_space = truncated.rfind(' ')
    if last_space > max_length * 0.3:  # At least 30% of content kept
        return truncated[:last_space].rstrip() + suffix

    # Fall back to hard cut
    return truncated.rstrip() + suffix


def api_success(data=None, message=None, status=200):
    """Return a success response."""
    response = {'success': True}
    if data is not None:
        response.update(data)
    if message:
        response['message'] = message
    return JsonResponse(response, status=status)


def api_error(message, status=400, errors=None):
    """Return an error response."""
    response = {
        'success': False,
        'error': {'message': message}
    }
    if errors:
        response['error']['details'] = errors
    return JsonResponse(response, status=status)
