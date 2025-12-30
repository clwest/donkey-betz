"""
Session 617: Title cleaning utility.

Removes redundant prefixes from dashboard titles like:
- "Experiment: Discussion: [Learned] Research: Research topic: ..."
- "Pilot: Panel: [Learned] ..."

Usage:
    from core.utils.title_cleaner import clean_title
    clean_name = clean_title(messy_name)
"""

import re
from typing import Optional


# Prefixes to strip (in order of application)
REDUNDANT_PREFIXES = [
    r'^Experiment:\s*',
    r'^Pilot:\s*',
    r'^Discussion:\s*',
    r'^Panel:\s*',
    r'^\[Learned\]\s*',
    r'^\[Synthesis\]\s*',
    r'^Research:\s*',
    r'^Research topic:\s*',
    r'^Topic:\s*',
    r'^Depth:\s*\w+\.\s*',
    r'^Context:\s*\w+\s*',
    r'^HiveMind session:\s*',
    r'^Decision:\s*',
]


def clean_title(title: Optional[str], max_length: Optional[int] = None) -> str:
    """
    Remove redundant prefixes from a title.

    Args:
        title: The title to clean
        max_length: Optional max length to truncate to

    Returns:
        Cleaned title with prefixes removed
    """
    if not title:
        return ''

    cleaned = title.strip()

    # Keep cleaning until no more prefixes match
    max_iterations = 10  # Prevent infinite loops
    for _ in range(max_iterations):
        original = cleaned
        for pattern in REDUNDANT_PREFIXES:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE).strip()
        if cleaned == original:
            break

    # Capitalize first letter if needed
    if cleaned and cleaned[0].islower():
        cleaned = cleaned[0].upper() + cleaned[1:]

    # Truncate if max_length specified
    if max_length and len(cleaned) > max_length:
        cleaned = cleaned[:max_length - 3] + '...'

    return cleaned


def clean_titles_dict(data: dict, title_keys: list = None) -> dict:
    """
    Clean titles in a dictionary.

    Args:
        data: Dictionary containing title fields
        title_keys: List of keys to clean (defaults to common title fields)

    Returns:
        Dictionary with cleaned titles
    """
    if title_keys is None:
        title_keys = ['name', 'title', 'topic', 'summary', 'question']

    result = data.copy()
    for key in title_keys:
        if key in result and isinstance(result[key], str):
            result[key] = clean_title(result[key])

    return result
