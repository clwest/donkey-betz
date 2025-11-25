"""
Centralized hybrid ID resolution.
Phase 2 High Priority - Task 2.13

Supports resolution of both UUIDs and human-friendly numeric IDs
(e.g., "image 5", "video #3", "the fifth video").

This module replaces 6+ duplicate implementations across the codebase.
"""

import re
from typing import Optional, Tuple, Union, Type
from uuid import UUID
import logging

logger = logging.getLogger(__name__)

# Patterns for extracting numeric IDs from natural language
NUMERIC_ID_PATTERNS = [
    (r'^#?(\d+)$', 'simple'),  # "5" or "#5"
    (r'(?:image|video|model|asset|project)\s*#?\s*(\d+)', 'prefixed'),  # "image 5", "video #3"
    (r'(?:the\s+)?(\d+)(?:st|nd|rd|th)', 'ordinal'),  # "the 5th", "3rd"
    (r'number\s*(\d+)', 'numbered'),  # "number 5"
]

# Word to number mapping for natural language
WORD_TO_NUMBER = {
    'first': 1, 'second': 2, 'third': 3, 'fourth': 4, 'fifth': 5,
    'sixth': 6, 'seventh': 7, 'eighth': 8, 'ninth': 9, 'tenth': 10,
    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
}


def parse_identifier(identifier: str) -> Tuple[Optional[str], Optional[int]]:
    """
    Parse an identifier string to determine if it's a UUID or numeric ID.

    Args:
        identifier: User-provided identifier (UUID string or numeric reference)

    Returns:
        Tuple of (uuid_string, numeric_id) - one will be None
    """
    if not identifier:
        return None, None

    identifier = str(identifier).strip()

    # Try UUID first
    try:
        uuid_obj = UUID(identifier)
        return str(uuid_obj), None
    except (ValueError, TypeError):
        pass

    # Try numeric patterns
    for pattern, pattern_type in NUMERIC_ID_PATTERNS:
        match = re.search(pattern, identifier, re.IGNORECASE)
        if match:
            try:
                num = int(match.group(1))
                if num >= 1:
                    return None, num
            except ValueError:
                continue

    # Try word numbers (first, second, etc.)
    lower_id = identifier.lower()
    for word, num in WORD_TO_NUMBER.items():
        if word in lower_id:
            return None, num

    return None, None


def resolve_content_id(
    identifier: Union[str, int],
    model_class: Type,
    user=None,
    project=None,
    order_by: str = 'created_at'
) -> Tuple[Optional[object], Optional[str]]:
    """
    Resolve hybrid identifier to model instance.

    Supports:
    - Full UUID: "550e8400-e29b-41d4-a716-446655440000"
    - Numeric: "5", "#5", "image 5"
    - Natural language: "the fifth image", "image number 5"

    Args:
        identifier: User-provided identifier
        model_class: Django model class (e.g., ImageHistory, VideoHistory)
        user: User to filter by (optional but recommended)
        project: Project to filter by (optional)
        order_by: Field to order by when resolving numeric IDs (default: 'created_at')

    Returns:
        Tuple of (instance or None, error_message or None)

    Example:
        from content.models import ImageHistory
        from core.utils.id_resolver import resolve_content_id

        image, error = resolve_content_id("image 5", ImageHistory, user=request.user)
        if error:
            return JsonResponse({'error': error}, status=400)
    """
    if not identifier:
        return None, "No identifier provided"

    identifier = str(identifier).strip()

    # Parse the identifier
    uuid_str, numeric_id = parse_identifier(identifier)

    if uuid_str:
        # Direct UUID lookup
        try:
            queryset = model_class.objects.all()
            if user:
                queryset = queryset.filter(user=user)
            if project:
                queryset = queryset.filter(project=project)

            instance = queryset.filter(id=uuid_str).first()
            if instance:
                return instance, None
            return None, f"{model_class.__name__} with ID {uuid_str} not found"

        except Exception as e:
            logger.error(f"Error resolving UUID {uuid_str}: {e}")
            return None, f"Error resolving ID: {str(e)}"

    elif numeric_id:
        # Numeric ID lookup
        try:
            queryset = model_class.objects.all()
            if user:
                queryset = queryset.filter(user=user)
            if project:
                queryset = queryset.filter(project=project)

            # Try sequential_number field first (if model has it)
            if hasattr(model_class, 'sequential_number'):
                instance = queryset.filter(sequential_number=numeric_id).first()
                if instance:
                    return instance, None

            # Fall back to ordering by created_at and taking nth item
            # Note: numeric_id is 1-based, list index is 0-based
            queryset = queryset.order_by(order_by)
            instances = list(queryset[numeric_id - 1:numeric_id])

            if instances:
                return instances[0], None

            return None, f"{model_class.__name__} #{numeric_id} not found"

        except Exception as e:
            logger.error(f"Error resolving numeric ID {numeric_id}: {e}")
            return None, f"Error resolving ID: {str(e)}"

    return None, f"Could not parse identifier: {identifier}"


def resolve_image_id(
    identifier: Union[str, int],
    user=None,
    project=None
) -> Tuple[Optional[object], Optional[str]]:
    """
    Resolve an image identifier to ImageHistory instance.

    Convenience wrapper for resolve_content_id with ImageHistory model.

    Args:
        identifier: User-provided identifier
        user: User to filter by
        project: Project to filter by

    Returns:
        Tuple of (ImageHistory instance or None, error_message or None)
    """
    from content.models import ImageHistory
    return resolve_content_id(identifier, ImageHistory, user=user, project=project)


def resolve_video_id(
    identifier: Union[str, int],
    user=None,
    project=None
) -> Tuple[Optional[object], Optional[str]]:
    """
    Resolve a video identifier to VideoHistory instance.

    Convenience wrapper for resolve_content_id with VideoHistory model.

    Args:
        identifier: User-provided identifier
        user: User to filter by
        project: Project to filter by

    Returns:
        Tuple of (VideoHistory instance or None, error_message or None)
    """
    from content.models import VideoHistory
    return resolve_content_id(identifier, VideoHistory, user=user, project=project)


def resolve_project_id(
    identifier: Union[str, int],
    user=None
) -> Tuple[Optional[object], Optional[str]]:
    """
    Resolve a project identifier to CreativeProject instance.

    Args:
        identifier: User-provided identifier
        user: User to filter by

    Returns:
        Tuple of (CreativeProject instance or None, error_message or None)
    """
    from content.models import CreativeProject
    return resolve_content_id(identifier, CreativeProject, user=user)


def resolve_multiple_ids(
    identifiers: list,
    model_class: Type,
    user=None,
    project=None
) -> Tuple[list, list]:
    """
    Resolve multiple identifiers to model instances.

    Args:
        identifiers: List of identifiers
        model_class: Django model class
        user: User to filter by
        project: Project to filter by

    Returns:
        Tuple of (resolved_instances, errors)
        - resolved_instances: List of successfully resolved instances
        - errors: List of (identifier, error_message) tuples for failures
    """
    resolved = []
    errors = []

    for identifier in identifiers:
        instance, error = resolve_content_id(
            identifier, model_class, user=user, project=project
        )
        if instance:
            resolved.append(instance)
        else:
            errors.append((identifier, error))

    return resolved, errors


def parse_id_range(range_str: str) -> list:
    """
    Parse an ID range string into individual IDs.

    Supports:
    - Single IDs: "5"
    - Comma-separated: "1, 2, 3"
    - Ranges: "1-5"
    - Combined: "1-3, 5, 7-9"

    Args:
        range_str: Range string to parse

    Returns:
        List of individual numeric IDs

    Example:
        parse_id_range("1-3, 5, 7-9") -> [1, 2, 3, 5, 7, 8, 9]
    """
    if not range_str:
        return []

    result = []
    parts = [p.strip() for p in str(range_str).split(',')]

    for part in parts:
        if '-' in part:
            # Handle range
            try:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                result.extend(range(start, end + 1))
            except ValueError:
                continue
        else:
            # Handle single number
            try:
                result.append(int(part))
            except ValueError:
                continue

    # Remove duplicates and sort
    return sorted(set(result))


def extract_ids_from_text(text: str) -> list:
    """
    Extract numeric IDs from natural language text.

    Handles phrases like:
    - "images 1, 2, and 3"
    - "videos 5-10"
    - "image 1 through 5"

    Args:
        text: Natural language text containing IDs

    Returns:
        List of extracted numeric IDs
    """
    if not text:
        return []

    result = []

    # Find explicit ranges (e.g., "1-5", "5 through 10")
    range_pattern = r'(\d+)\s*(?:-|to|through)\s*(\d+)'
    for match in re.finditer(range_pattern, text, re.IGNORECASE):
        start = int(match.group(1))
        end = int(match.group(2))
        result.extend(range(start, end + 1))

    # Find comma/and separated lists (e.g., "1, 2, and 3")
    list_pattern = r'(\d+)(?:\s*,\s*|\s+and\s+)'
    text_copy = text
    for match in re.finditer(list_pattern, text_copy, re.IGNORECASE):
        result.append(int(match.group(1)))

    # Find standalone numbers not part of ranges
    standalone_pattern = r'(?<!\d-)\b(\d+)\b(?!-\d)'
    for match in re.finditer(standalone_pattern, text):
        num = int(match.group(1))
        if num not in result:
            result.append(num)

    # Remove duplicates and sort
    return sorted(set(result))
