"""
Timestamp normalization utility for spider data and ingestion pipelines.

Ensures all timestamps stored in the system are timezone-aware UTC.
Handles the common case of RSS/API feeds returning timezone-less ISO strings.

Usage:
    from core.utils.time import normalize_timestamp
    aware_dt = normalize_timestamp("2026-03-25T14:23:00")  # assumes UTC
    aware_dt = normalize_timestamp("2026-03-25T14:23:00-07:00")  # preserves, converts to UTC
"""

import logging
from datetime import datetime, timezone
from typing import Optional, Union

logger = logging.getLogger(__name__)


def normalize_timestamp(
    value: Union[str, datetime, None],
    source_tz_hint: Optional[str] = None,
) -> Optional[datetime]:
    """
    Parse and normalize a timestamp to timezone-aware UTC.

    Args:
        value: ISO timestamp string, datetime, or None
        source_tz_hint: Optional timezone hint (e.g., 'US/Eastern') for
                        timezone-less strings. If not provided, assumes UTC.

    Returns:
        Timezone-aware datetime in UTC, or None if value is None/empty.

    Raises:
        ValueError: If the timestamp string cannot be parsed.
    """
    if value is None or value == '':
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            # Naive datetime — attach UTC (or hint timezone)
            if source_tz_hint:
                try:
                    import zoneinfo
                    tz = zoneinfo.ZoneInfo(source_tz_hint)
                    value = value.replace(tzinfo=tz)
                except (KeyError, ImportError):
                    logger.warning(f"Unknown timezone hint '{source_tz_hint}', assuming UTC")
                    value = value.replace(tzinfo=timezone.utc)
            else:
                value = value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc)
        else:
            return value.astimezone(timezone.utc)

    # String parsing
    if not isinstance(value, str):
        raise ValueError(f"Expected str or datetime, got {type(value).__name__}")

    value = value.strip()
    if not value:
        return None

    # Try standard ISO parsing (handles timezone-aware strings)
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            if source_tz_hint:
                try:
                    import zoneinfo
                    tz = zoneinfo.ZoneInfo(source_tz_hint)
                    dt = dt.replace(tzinfo=tz)
                except (KeyError, ImportError):
                    dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        pass

    # Handle 'Z' suffix (common in APIs)
    if value.endswith('Z'):
        try:
            dt = datetime.fromisoformat(value[:-1])
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            pass

    # Common RSS date formats
    for fmt in (
        '%a, %d %b %Y %H:%M:%S %z',   # RFC 2822 (RSS)
        '%a, %d %b %Y %H:%M:%S %Z',   # RFC 2822 variant
        '%Y-%m-%dT%H:%M:%S.%f%z',      # ISO with microseconds
        '%Y-%m-%dT%H:%M:%S.%f',        # ISO with microseconds, no tz
        '%Y-%m-%d %H:%M:%S',           # Simple datetime
        '%Y-%m-%d',                     # Date only
    ):
        try:
            dt = datetime.strptime(value, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            continue

    raise ValueError(f"Cannot parse timestamp: '{value[:100]}'")
