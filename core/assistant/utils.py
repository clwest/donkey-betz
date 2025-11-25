"""
Utility Functions for AI Assistant
==================================

Shared utility functions for ID resolution, range parsing, and other helpers.
"""

import logging
import uuid as uuid_module
from typing import List

logger = logging.getLogger(__name__)


def resolve_hybrid_image_id(image_id: str, user) -> str:
    """
    Convert sequential image numbers to UUIDs.

    Args:
        image_id: Either a sequential number (e.g., '1', '5') or a UUID string
        user: The Django user to filter images by

    Returns:
        UUID string of the image

    Raises:
        ValueError: If image not found
    """
    if image_id.isdigit():
        from content.models import ImageHistory
        try:
            seq_num = int(image_id)
            image = ImageHistory.objects.filter(user=user).order_by('created_at')[seq_num - 1]
            resolved_id = str(image.id)
            logger.info(f"Converted image #{seq_num} to UUID {resolved_id[:8]}...")
            return resolved_id
        except (IndexError, ImageHistory.DoesNotExist):
            raise ValueError(f'Image #{image_id} not found')
    return image_id


def resolve_hybrid_video_id(video_id: str, user) -> str:
    """
    Convert sequential video numbers to UUIDs.

    Args:
        video_id: Either a sequential number (e.g., '1', '5') or a UUID string
        user: The Django user to filter videos by

    Returns:
        UUID string of the video

    Raises:
        ValueError: If video not found
    """
    if video_id.isdigit():
        from content.models import VideoHistory
        try:
            seq_num = int(video_id)
            video = VideoHistory.objects.filter(user=user).order_by('created_at')[seq_num - 1]
            resolved_id = str(video.id)
            logger.info(f"Converted video #{seq_num} to UUID {resolved_id[:8]}...")
            return resolved_id
        except (IndexError, VideoHistory.DoesNotExist):
            raise ValueError(f'Video #{video_id} not found')
    return video_id


def parse_id_range(id_str: str) -> List[str]:
    """
    Parse image/video ID ranges into list of individual IDs.

    Supports:
    - Single ID: "5" -> ["5"]
    - Range: "20-25" -> ["20", "21", "22", "23", "24", "25"]
    - List: "5, 8, 12" -> ["5", "8", "12"]
    - Combined: "10-15, 20, 25-27" -> ["10", "11", "12", "13", "14", "15", "20", "25", "26", "27"]
    - Spaces are ignored: "20 - 25, 30" -> ["20", "21", "22", "23", "24", "25", "30"]

    Args:
        id_str: String containing IDs, ranges, or lists

    Returns:
        List of individual ID strings

    Raises:
        ValueError: If range is invalid (start > end)
    """
    id_str = id_str.strip()

    # Check if it's a UUID (contains dashes but is a valid UUID format)
    if '-' in id_str and ',' not in id_str:
        try:
            uuid_module.UUID(id_str)
            return [id_str]  # Single UUID
        except ValueError:
            pass  # Not a UUID, parse as range

    # Parse comma-separated segments
    segments = [seg.strip() for seg in id_str.split(',')]
    result = []

    for segment in segments:
        segment = segment.strip()

        # Check if segment contains range (dash between numbers)
        if '-' in segment:
            parts = [p.strip() for p in segment.split('-')]
            if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                start = int(parts[0])
                end = int(parts[1])
                if start > end:
                    raise ValueError(f"Invalid range: {segment} (start > end)")
                result.extend([str(i) for i in range(start, end + 1)])
            else:
                result.append(segment)
        else:
            result.append(segment)

    # Remove duplicates while preserving order
    seen = set()
    unique_result = []
    for id_val in result:
        if id_val not in seen:
            seen.add(id_val)
            unique_result.append(id_val)

    logger.info(f"Parsed ID range '{id_str}' -> {len(unique_result)} IDs: {unique_result[:5]}{'...' if len(unique_result) > 5 else ''}")
    return unique_result


def is_batch_operation(id_str: str) -> bool:
    """
    Determine if an ID string represents a batch operation (range or list).

    Args:
        id_str: The ID string to check

    Returns:
        True if it's a batch operation, False otherwise
    """
    if ',' in id_str:
        return True

    if '-' in id_str:
        # Check if it's a numeric range (not a UUID)
        cleaned = id_str.replace('-', '').replace(' ', '')
        return cleaned.isdigit()

    return False


def format_batch_result(operation: str, successes: int, total: int, failures: int, results: list,
                        successful_ids: list = None, failed_ids: list = None, errors: list = None) -> dict:
    """
    Format batch operation results into a standard structure.

    Args:
        operation: Name of the operation performed
        successes: Number of successful operations
        total: Total number of operations attempted
        failures: Number of failed operations
        results: List of individual operation results
        successful_ids: List of IDs that succeeded (optional)
        failed_ids: List of IDs that failed (optional)
        errors: List of error messages (optional)

    Returns:
        Standardized batch result dictionary
    """
    summary = f"Batch {operation} complete: {successes}/{total} succeeded"
    if failures > 0:
        summary += f", {failures} failed"

    return {
        'success': failures == 0,
        'message': summary,
        'batch': True,
        'total': total,
        'successes': successes,
        'failures': failures,
        'results': results,
        'details': {
            'successful_ids': successful_ids or [],
            'failed_ids': failed_ids or [],
            'errors': errors or []
        }
    }


def safe_json_loads(json_str: str, default: dict = None) -> dict:
    """
    Safely parse JSON string, returning default on failure.

    Args:
        json_str: JSON string to parse
        default: Default value if parsing fails

    Returns:
        Parsed JSON object or default value
    """
    import json
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default or {}
