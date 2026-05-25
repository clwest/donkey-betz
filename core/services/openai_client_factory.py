"""Shared factory for OpenAI SDK client instances.

Session 1084 round 51: Mirror of ``anthropic_client_factory.py``. Centralize
OpenAI client construction so every call site in the platform gets the same
timeout + retry configuration and cannot drift back to the SDK defaults.

Why this exists
---------------
OpenAI's Python SDK defaults to a **600 second** request timeout with 2
retries. Sites that instantiate ``OpenAI()`` with no timeout configured can
hang for up to ~30 minutes before raising if the upstream socket is half-dead
(TCP CLOSE_WAIT state). This is the same hang class that PR #1893 fixed for
Anthropic. An audit on April 15 2026 found ~94 OpenAI client instantiation
sites across ``core/``; only ``llm_provider_registry.py`` (Session 831) had
explicit timeouts. The rest were drifting on the SDK default.

Use ``get_openai_client()`` everywhere instead of calling ``OpenAI()``
directly. The factory also supports DeepSeek, Together AI, and any other
provider that uses an OpenAI-compatible SDK interface, by accepting a
``base_url`` override and passing through arbitrary additional kwargs
(``default_headers``, ``organization``, ``project``, etc).

Forbidden kwargs
----------------
Callers may not override ``timeout``, ``max_retries``, or ``api_key`` via
``**kwargs``. These are the reliability invariants this factory exists to
enforce. Passing any of them raises ``ValueError``.

Drift audit command
-------------------
::

    grep -R "OpenAI(" -n core/ --include='*.py' | grep -v openai_client_factory
"""

from __future__ import annotations

import logging
import os
import threading
from typing import Dict, Optional, Tuple

import httpx
from openai import OpenAI

logger = logging.getLogger(__name__)

OPENAI_CONNECT_TIMEOUT_S = 20.0
OPENAI_READ_TIMEOUT_S = 90.0
OPENAI_WRITE_TIMEOUT_S = 60.0
OPENAI_POOL_TIMEOUT_S = 60.0
OPENAI_MAX_RETRIES = 2

_FORBIDDEN_KWARGS = ("timeout", "max_retries", "api_key")

# Session 1144: per-process client cache. Every ``OpenAI(...)`` instance
# carries its own internal httpx connection pool — so calling the factory
# afresh for every request meant zero socket reuse and contributed to the
# ~4K TIME_WAIT sockets to :443 observed during the Session 1144 leak
# audit. Cache key is ``(api_key, base_url)`` so callers using different
# providers (OpenAI / DeepSeek / Together) still get isolated clients,
# and ``**kwargs`` calls bypass the cache (rare path, hard to key safely).
_CLIENT_CACHE: Dict[Tuple[str, Optional[str]], OpenAI] = {}
_CLIENT_CACHE_LOCK = threading.Lock()


def get_openai_client(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs,
) -> OpenAI:
    """Return an ``OpenAI`` client with timeout + retry centrally configured.

    ``api_key`` falls back to the ``OPENAI_API_KEY`` environment variable if
    not provided. If neither is set, raises ``RuntimeError`` rather than
    letting the SDK produce a cryptic error at first-request time.

    ``base_url`` is optional and supports DeepSeek/Together AI/any
    OpenAI-compatible provider.

    Additional ``**kwargs`` are passed through to ``OpenAI(...)`` for
    uncommon options like ``default_headers``, ``organization``, or
    ``project``. The reliability invariants (``timeout``, ``max_retries``,
    ``api_key``) are centrally managed and cannot be overridden via kwargs.
    """
    resolved_key = api_key or os.getenv("OPENAI_API_KEY")
    if not resolved_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set and no api_key was provided to "
            "get_openai_client()"
        )

    for forbidden in _FORBIDDEN_KWARGS:
        if forbidden in kwargs:
            raise ValueError(
                f"Do not pass {forbidden!r} to get_openai_client(); it is "
                f"centrally managed by the factory"
            )

    # Cache hit path — repeat callers with the same (api_key, base_url)
    # share one client and therefore one internal httpx connection pool.
    # Skipped when caller passes extra kwargs (default_headers / organization /
    # project) since those would need to be part of the key.
    cache_key = (resolved_key, base_url)
    if not kwargs:
        cached = _CLIENT_CACHE.get(cache_key)
        if cached is not None:
            return cached

    timeout = httpx.Timeout(
        connect=OPENAI_CONNECT_TIMEOUT_S,
        read=OPENAI_READ_TIMEOUT_S,
        write=OPENAI_WRITE_TIMEOUT_S,
        pool=OPENAI_POOL_TIMEOUT_S,
    )

    ctor_kwargs = {
        "api_key": resolved_key,
        "timeout": timeout,
        "max_retries": OPENAI_MAX_RETRIES,
    }
    if base_url:
        ctor_kwargs["base_url"] = base_url
    ctor_kwargs.update(kwargs)  # safe — forbidden keys already rejected above

    client = OpenAI(**ctor_kwargs)
    if not kwargs:
        with _CLIENT_CACHE_LOCK:
            # Double-check after acquiring the lock to avoid two concurrent
            # constructors racing — first writer wins; the loser's client is
            # GC'd along with its (unused) pool.
            existing = _CLIENT_CACHE.get(cache_key)
            if existing is not None:
                return existing
            _CLIENT_CACHE[cache_key] = client
    return client
