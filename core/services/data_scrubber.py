"""
Session G2: Central Data Scrubber — redaction + outbound guards.

Single entry point for PII/secret removal used by:
- Deliverable saves
- Tool call logging (ToolCallRecord payloads)
- Discord posting (outbound message guard)

Usage:
    from core.services.data_scrubber import scrub, is_safe_for_external

    clean_text = scrub(raw_text)
    if is_safe_for_external(deliverable):
        post_to_discord(clean_text)
"""

import re
import logging

logger = logging.getLogger(__name__)

# ── PII / Secret patterns ───────────────────────────────────────────────────

_PATTERNS = [
    # API keys / tokens (generic)
    (re.compile(r'\b(sk-[a-zA-Z0-9]{20,})\b'), '[REDACTED_API_KEY]'),
    (re.compile(r'\b(xoxb-[a-zA-Z0-9\-]+)\b'), '[REDACTED_SLACK_TOKEN]'),
    (re.compile(r'\b(ghp_[a-zA-Z0-9]{36,})\b'), '[REDACTED_GITHUB_TOKEN]'),
    (re.compile(r'\b(ghs_[a-zA-Z0-9]{36,})\b'), '[REDACTED_GITHUB_TOKEN]'),

    # AWS keys
    (re.compile(r'\b(AKIA[0-9A-Z]{16})\b'), '[REDACTED_AWS_KEY]'),

    # Bearer tokens in headers
    (re.compile(r'(Bearer\s+)[a-zA-Z0-9\-_.~+/]+=*', re.IGNORECASE), r'\1[REDACTED_TOKEN]'),

    # Email addresses
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[REDACTED_EMAIL]'),

    # Phone numbers (US format)
    (re.compile(r'\b(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'), '[REDACTED_PHONE]'),

    # SSN
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), '[REDACTED_SSN]'),

    # Credit card numbers (basic)
    (re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'), '[REDACTED_CC]'),

    # Database connection strings
    (re.compile(r'postgres(ql)?://[^\s]+', re.IGNORECASE), '[REDACTED_DB_URL]'),
    (re.compile(r'redis://[^\s]+', re.IGNORECASE), '[REDACTED_REDIS_URL]'),

    # Generic password fields in JSON/dicts
    (re.compile(r'(["\']?password["\']?\s*[:=]\s*)["\'][^"\']+["\']', re.IGNORECASE),
     r'\1"[REDACTED]"'),
    (re.compile(r'(["\']?secret["\']?\s*[:=]\s*)["\'][^"\']+["\']', re.IGNORECASE),
     r'\1"[REDACTED]"'),
]


def scrub(text: str) -> str:
    """Remove PII and secrets from text. Returns cleaned copy."""
    if not text:
        return text
    result = text
    for pattern, replacement in _PATTERNS:
        result = pattern.sub(replacement, result)
    return result


def scrub_dict(data: dict, max_depth: int = 5) -> dict:
    """Recursively scrub string values in a dict."""
    if max_depth <= 0:
        return data
    result = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = scrub(value)
        elif isinstance(value, dict):
            result[key] = scrub_dict(value, max_depth - 1)
        elif isinstance(value, list):
            result[key] = [
                scrub(v) if isinstance(v, str)
                else scrub_dict(v, max_depth - 1) if isinstance(v, dict)
                else v
                for v in value
            ]
        else:
            result[key] = value
    return result


# ── Outbound guards ─────────────────────────────────────────────────────────

# Sensitivity levels that block external posting of content excerpts
_EXTERNAL_BLOCKED = frozenset(['confidential', 'restricted'])


def is_safe_for_external(obj) -> bool:
    """Check if an object's content can be posted externally (Discord, etc.).

    Args:
        obj: A Document or Deliverable instance (anything with data_sensitivity).

    Returns:
        True if content excerpts can be shared externally.
    """
    sensitivity = getattr(obj, 'data_sensitivity', 'internal')
    return sensitivity not in _EXTERNAL_BLOCKED


def guard_external_message(obj, message: str) -> str:
    """Prepare a message for external posting, respecting sensitivity.

    If the object is confidential/restricted, strips content excerpts
    and returns only IDs/links/correlation info.
    """
    if is_safe_for_external(obj):
        return scrub(message)

    # For confidential/restricted: only allow ID references
    obj_id = getattr(obj, 'id', getattr(obj, 'pk', 'unknown'))
    obj_type = type(obj).__name__
    return f"[{obj_type} id={obj_id}] — content redacted (sensitivity: {getattr(obj, 'data_sensitivity', 'unknown')})"


# ── Persistence guard (Phase 3: external data leakage prevention) ──────────

# Origins that indicate external data
_EXTERNAL_ORIGINS = frozenset([
    'tool:web_search', 'tool:web_fetch', 'tool:spider_data',
    'tool:competitor_research', 'tool:auto_research',
])


def is_external_origin(origin: str) -> bool:
    """Check if an origin string indicates external data."""
    if not origin:
        return False
    origin_lower = origin.lower()
    if origin_lower in _EXTERNAL_ORIGINS:
        return True
    return origin_lower.startswith(('spider:', 'tool:web', 'api:', 'external:'))


def guard_persistence(
    content: str,
    origin: str = '',
    provenance: dict = None,
    metadata: dict = None,
) -> dict:
    """
    Gate for persisting content. Scrubs PII/secrets, attaches provenance,
    and recommends promotion_status based on origin.

    Args:
        content: The text to persist.
        origin: Where the data came from (e.g., 'tool:web_search', 'spider:reddit', 'internal').
        provenance: Optional dict with source_url, spider_name, retrieved_at, etc.
        metadata: Existing metadata dict to merge provenance into.

    Returns:
        dict with:
            scrubbed_content: cleaned text
            metadata: merged metadata with provenance attached
            promotion_status: 'promoted' (internal) or 'staged' (external)
            is_external: bool
    """
    scrubbed = scrub(content) if content else ''
    external = is_external_origin(origin)

    merged_meta = dict(metadata or {})
    if origin:
        merged_meta['_origin'] = origin
    if external:
        merged_meta['_external'] = True
        merged_meta['_provenance'] = provenance or {}

    return {
        'scrubbed_content': scrubbed,
        'metadata': merged_meta,
        'promotion_status': 'staged' if external else 'promoted',
        'is_external': external,
    }


def should_persist_payload() -> bool:
    """Check if tool call payloads should be persisted based on RECORDING_MODE."""
    from django.conf import settings
    mode = getattr(settings, 'RECORDING_MODE', 'off')
    return mode in ('on', 'public_safe')


def scrub_for_recording(text: str) -> str:
    """Scrub text according to recording mode.

    - off: no-op (shouldn't be called, but safe)
    - on: pass through (full fidelity)
    - public_safe: scrub PII/secrets
    """
    from django.conf import settings
    mode = getattr(settings, 'RECORDING_MODE', 'off')
    if mode == 'public_safe':
        return scrub(text)
    return text
