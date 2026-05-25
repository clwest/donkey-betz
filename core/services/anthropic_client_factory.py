"""Shared factory for Anthropic SDK client instances.

Session 1084 round 49: Centralize Anthropic client construction so every
call site in the platform gets the same timeout + retry configuration.

Why this exists
---------------
Anthropic's Python SDK defaults to a **600 second** request timeout with
2 retries. Sites that instantiate ``Anthropic()`` with no kwargs can hang
for up to ~30 minutes before raising if the upstream socket is half-dead
(TCP CLOSE_WAIT state). Session 1083 observed a 15-minute wall-clock
hang on a Celery default worker that matched this symptom.

Prior to this module, 8 sites across the codebase instantiated Anthropic
clients independently. Only one of them (``llm_provider_registry.py``)
configured a timeout. Every other site relied on the SDK default, which
is not safe in a Celery worker pool.

Use ``get_anthropic_client()`` everywhere instead of calling ``Anthropic()``
directly. A lint check in the PR description confirms drift back to
bare instantiation will be caught:

    grep -R "Anthropic(" -n core/ | grep -v anthropic_client_factory.py
"""

from __future__ import annotations

import logging
import os
import threading
from typing import Dict, Optional

import httpx
from anthropic import Anthropic

logger = logging.getLogger(__name__)

ANTHROPIC_CONNECT_TIMEOUT_S = 20.0
ANTHROPIC_READ_TIMEOUT_S = 90.0
ANTHROPIC_WRITE_TIMEOUT_S = 60.0
ANTHROPIC_POOL_TIMEOUT_S = 60.0
ANTHROPIC_MAX_RETRIES = 2

# Session 1144: per-process client cache keyed by resolved api_key. Each
# ``Anthropic(...)`` instance owns its own httpx connection pool; calling
# the factory afresh per request meant zero socket reuse and contributed
# to the ~4K TIME_WAIT sockets to :443 observed in the Session 1144 leak
# audit. Same pattern as openai_client_factory.
_CLIENT_CACHE: Dict[Optional[str], Anthropic] = {}
_CLIENT_CACHE_LOCK = threading.Lock()


def get_anthropic_client(api_key: Optional[str] = None) -> Anthropic:
    """Return an ``Anthropic`` client with timeout + retry configured.

    The timeout values match the ones already in use by
    ``core.services.llm_provider_registry.AnthropicProvider`` (Session 831).
    Retry count matches too.

    ``api_key`` falls back to the ``ANTHROPIC_API_KEY`` environment
    variable if not provided, matching the SDK default behavior. This lets
    callers that previously used bare ``Anthropic()`` keep the same
    semantics with a one-line change.

    Session 1144: repeat callers with the same resolved api_key share a
    single client (and therefore a single internal httpx connection pool).
    """
    resolved_key = api_key or os.getenv("ANTHROPIC_API_KEY")

    cached = _CLIENT_CACHE.get(resolved_key)
    if cached is not None:
        return cached

    # Fully explicit form — all 4 timeout dimensions named so there is no
    # positional-default ambiguity. Session 1084 round 49 audit note.
    timeout = httpx.Timeout(
        connect=ANTHROPIC_CONNECT_TIMEOUT_S,
        read=ANTHROPIC_READ_TIMEOUT_S,
        write=ANTHROPIC_WRITE_TIMEOUT_S,
        pool=ANTHROPIC_POOL_TIMEOUT_S,
    )
    client = Anthropic(
        api_key=resolved_key,
        timeout=timeout,
        max_retries=ANTHROPIC_MAX_RETRIES,
    )
    with _CLIENT_CACHE_LOCK:
        # Double-check after acquiring the lock — first writer wins; the
        # loser's client gets GC'd along with its (unused) pool.
        existing = _CLIENT_CACHE.get(resolved_key)
        if existing is not None:
            return existing
        _CLIENT_CACHE[resolved_key] = client
    return client
