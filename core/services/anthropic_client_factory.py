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
from typing import Optional

import httpx
from anthropic import Anthropic

logger = logging.getLogger(__name__)

ANTHROPIC_CONNECT_TIMEOUT_S = 20.0
ANTHROPIC_READ_TIMEOUT_S = 90.0
ANTHROPIC_WRITE_TIMEOUT_S = 60.0
ANTHROPIC_POOL_TIMEOUT_S = 60.0
ANTHROPIC_MAX_RETRIES = 2


def get_anthropic_client(api_key: Optional[str] = None) -> Anthropic:
    """Return an ``Anthropic`` client with timeout + retry configured.

    The timeout values match the ones already in use by
    ``core.services.llm_provider_registry.AnthropicProvider`` (Session 831).
    Retry count matches too.

    ``api_key`` falls back to the ``ANTHROPIC_API_KEY`` environment
    variable if not provided, matching the SDK default behavior. This lets
    callers that previously used bare ``Anthropic()`` keep the same
    semantics with a one-line change.
    """
    # Fully explicit form — all 4 timeout dimensions named so there is no
    # positional-default ambiguity. Session 1084 round 49 audit note.
    timeout = httpx.Timeout(
        connect=ANTHROPIC_CONNECT_TIMEOUT_S,
        read=ANTHROPIC_READ_TIMEOUT_S,
        write=ANTHROPIC_WRITE_TIMEOUT_S,
        pool=ANTHROPIC_POOL_TIMEOUT_S,
    )
    return Anthropic(
        api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
        timeout=timeout,
        max_retries=ANTHROPIC_MAX_RETRIES,
    )
