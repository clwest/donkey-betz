"""S3038 A3 — Stable regex classifier for `LLMCallLog.error_message`.

Used by:
- `LLMCallLog.save()` pre-persist hook to auto-populate `error_type` when only
  `error_message` was set at the write site. Closes the silent-monitoring gap
  surfaced in the S3037 Reliability Audit Step 4 (305 failed rows in 90d with
  empty `error_type`, blocking any error-type-based alerting or trend query).
- Backfill management command `classify_llm_error_types` for historical rows.

Contract: `classify_llm_error(message)` returns a short stable tag suitable for
CharField(max_length=100). Empty/None input returns `''` (leaves the field
blank). Non-empty input that matches no pattern returns `'unknown_error'`,
which is itself a signal to widen the pattern table.

Pattern order matters — most specific first, so `RateLimitError` in a message
like `openai.RateLimitError: 429 too many requests` classifies as
`rate_limit`, not the generic `api_error` fallback.
"""

from __future__ import annotations

import re
from typing import Sequence, Tuple

# Compile once at import. Order matters — first match wins.
_PATTERNS: Sequence[Tuple[re.Pattern[str], str]] = (
    # Explicit provider exception names + HTTP status codes.
    (re.compile(r'\bRateLimitError\b|\brate[_ ]?limit\b|\b429\b', re.IGNORECASE), 'rate_limit'),
    (re.compile(r'\bAuthenticationError\b|\binvalid[_ ]api[_ ]key\b|\b401\b', re.IGNORECASE), 'auth_error'),
    (re.compile(r'\bPermissionDeniedError\b|\bPermissionError\b|\b403\b', re.IGNORECASE), 'permission_denied'),
    (re.compile(r'\bContextWindowExceededError\b|\bcontext[_ ]length\b|\bmaximum context\b|\bcontext window\b', re.IGNORECASE), 'context_window_exceeded'),
    (re.compile(r'\bNotFoundError\b|\b404\b|\bmodel not found\b', re.IGNORECASE), 'not_found'),
    (re.compile(r'\bBadRequestError\b|\bInvalidRequestError\b|\binvalid[_ ]request\b|\b400\b', re.IGNORECASE), 'invalid_request'),
    (re.compile(r'\bTimeoutError\b|\bAPITimeoutError\b|\btimed out\b|\brequest timeout\b', re.IGNORECASE), 'timeout'),
    (re.compile(r'\bAPIConnectionError\b|\bConnection error\b|\bconnection reset\b|\bconnection refused\b', re.IGNORECASE), 'connection_error'),
    (re.compile(r'\bServiceUnavailable\b|\b503\b', re.IGNORECASE), 'service_unavailable'),
    (re.compile(r'\bInternalServerError\b|\b500\b|\b502\b|\b504\b', re.IGNORECASE), 'server_error'),
    (re.compile(r'\bAPIError\b', re.IGNORECASE), 'api_error'),
)

# Public constant so callers (dashboards, alerts) can enumerate known tags.
KNOWN_ERROR_TYPES = tuple(tag for _, tag in _PATTERNS) + ('unknown_error', '')

# CharField(max_length=100) — tags fit comfortably, but slice defensively.
_MAX_TAG_LEN = 100


def classify_llm_error(error_message: str | None) -> str:
    """Return a stable `error_type` tag for `error_message`.

    - Empty/None → `''` (leaves `error_type` blank; caller shouldn't set it).
    - Any non-empty message that matches no pattern → `'unknown_error'`
      (a signal to widen the pattern table; distinct from truly-blank).
    """
    if not error_message:
        return ''
    for pattern, tag in _PATTERNS:
        if pattern.search(error_message):
            return tag[:_MAX_TAG_LEN]
    return 'unknown_error'
