# CRITICAL_PATH_HUB — see docs/CRITICAL_PATH_HUBS.md
# Changes here can break the whole platform. Request Chris review before merge.
"""Shared factory for OpenAI SDK client instances.

Session 1084 round 51: Mirror of ``anthropic_client_factory.py``. Centralize
OpenAI client construction so every call site in the platform gets the same
timeout + retry configuration and cannot drift back to the SDK defaults.

Session 1216 (Phase E): factory-returned clients also install a
**reasoning-contract guard** on their ``chat.completions.create`` methods.
The guard inspects outbound kwargs for params that gpt-5.x reasoning models
reject (``max_tokens``, ``temperature``, ``top_p``, ``frequency_penalty``,
``presence_penalty``) and acts per the ``OPENAI_REASONING_GUARD`` env var:

- ``warn`` (default) — log a structured warning, leave kwargs unchanged
- ``strip`` — remove forbidden kwargs + log, then dispatch
- ``error`` — raise ``ReasoningGuardViolation`` before any network call

Guard only fires when the ``model`` kwarg contains substring ``"gpt-5"`` —
non-reasoning callers see no behavior change. See ``apply_reasoning_guard``
for the pure-function form, and ``_install_reasoning_guard`` for the
method-wrapping behavior applied to factory-returned clients.

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
directly. For async callers, use ``get_async_openai_client()`` instead of
``AsyncOpenAI()``. Both factories apply the same timeout + retry contract.
The factory also supports DeepSeek, Together AI, and any other provider
that uses an OpenAI-compatible SDK interface, by accepting a ``base_url``
override and passing through arbitrary additional kwargs
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
    grep -R "AsyncOpenAI(" -n . --include='*.py' | grep -v openai_client_factory
"""

from __future__ import annotations

import logging
import os
import threading
from typing import Dict, Optional, Tuple

import httpx
from openai import AsyncOpenAI, OpenAI

logger = logging.getLogger(__name__)

OPENAI_CONNECT_TIMEOUT_S = 20.0
OPENAI_READ_TIMEOUT_S = 90.0
OPENAI_WRITE_TIMEOUT_S = 60.0
OPENAI_POOL_TIMEOUT_S = 60.0
OPENAI_MAX_RETRIES = 2

_FORBIDDEN_KWARGS = ("timeout", "max_retries", "api_key")

# Session 1216 Phase E: reasoning-contract guard
_REASONING_FORBIDDEN_KWARGS = (
    "max_tokens",
    "temperature",
    "top_p",
    "frequency_penalty",
    "presence_penalty",
)
_REASONING_MODEL_SUBSTRING = "gpt-5"
_REASONING_GUARD_ENV = "OPENAI_REASONING_GUARD"
_REASONING_GUARD_MODES = ("warn", "strip", "error")
_REASONING_GUARD_DEFAULT_MODE = "warn"
_REASONING_GUARD_LOGGER = logging.getLogger("openai_client_factory.reasoning_guard")


class ReasoningGuardViolation(ValueError):
    """Raised when ``OPENAI_REASONING_GUARD=error`` and a forbidden kwarg
    is passed to a gpt-5.x reasoning model. The exception fires before the
    SDK makes any network call. Subclasses ``ValueError`` so existing
    catch-ValueError sites still see the violation."""


def _resolve_guard_mode() -> str:
    """Read OPENAI_REASONING_GUARD; default ``warn``; unknown values
    coerced to ``warn`` with a one-time deprecation log."""
    raw = (os.getenv(_REASONING_GUARD_ENV) or "").strip().lower()
    if not raw:
        return _REASONING_GUARD_DEFAULT_MODE
    if raw not in _REASONING_GUARD_MODES:
        _REASONING_GUARD_LOGGER.warning(
            "Unknown %s=%r; falling back to %r. Valid modes: %s",
            _REASONING_GUARD_ENV, raw,
            _REASONING_GUARD_DEFAULT_MODE,
            ",".join(_REASONING_GUARD_MODES),
        )
        return _REASONING_GUARD_DEFAULT_MODE
    return raw


def apply_reasoning_guard(
    kwargs: Dict[str, object],
    model: Optional[str],
    caller_label: str = "",
) -> Dict[str, object]:
    """Inspect ``kwargs`` for params that gpt-5.x reasoning models reject.

    Mode controlled by the ``OPENAI_REASONING_GUARD`` env var:

    - ``warn`` (default): log a structured warning, return ``kwargs`` unchanged.
    - ``strip``: remove forbidden keys, log what was removed, return modified dict.
    - ``error``: raise ``ReasoningGuardViolation`` before the SDK call.

    The guard only fires when ``model`` contains substring ``"gpt-5"``. If
    ``model`` is missing or None, returns ``kwargs`` unchanged — avoids
    false positives on non-OpenAI provider routing.

    Returns the (possibly modified) kwargs dict. Caller dispatches to the
    SDK with the result.
    """
    if not model or _REASONING_MODEL_SUBSTRING not in model.lower():
        return kwargs

    present = [k for k in _REASONING_FORBIDDEN_KWARGS if k in kwargs]
    if not present:
        return kwargs

    mode = _resolve_guard_mode()
    label = caller_label or "unknown"

    if mode == "error":
        raise ReasoningGuardViolation(
            f"{label}: gpt-5.x reasoning model {model!r} rejects "
            f"{present!r}. Use 'max_completion_tokens'; omit "
            f"temperature/top_p/penalties."
        )

    if mode == "strip":
        stripped = {k: kwargs[k] for k in present}
        new_kwargs = {k: v for k, v in kwargs.items() if k not in present}
        _REASONING_GUARD_LOGGER.warning(
            "[reasoning_guard] mode=strip caller=%s model=%s stripped=%s",
            label, model, list(stripped.keys()),
        )
        return new_kwargs

    # warn (default)
    _REASONING_GUARD_LOGGER.warning(
        "[reasoning_guard] mode=warn caller=%s model=%s forbidden_present=%s",
        label, model, present,
    )
    return kwargs


def _install_reasoning_guard(client, async_create: bool = False) -> None:
    """Wrap the SDK's chat-completions creator with the reasoning guard.

    Applied once per client at construction time. The wrapped method
    forwards all args/kwargs to the original after guarding. Cached
    clients (per the factory's ``(api_key, base_url)`` cache) get the
    guard installed exactly once.
    """
    completions = client.chat.completions
    original_create = completions.create

    if async_create:
        async def _guarded_async_create(*args, **kwargs):
            model = kwargs.get("model")
            kwargs = apply_reasoning_guard(
                kwargs, model, caller_label="async_chat.completions.create",
            )
            return await original_create(*args, **kwargs)
        completions.create = _guarded_async_create
    else:
        def _guarded_sync_create(*args, **kwargs):
            model = kwargs.get("model")
            kwargs = apply_reasoning_guard(
                kwargs, model, caller_label="chat.completions.create",
            )
            return original_create(*args, **kwargs)
        completions.create = _guarded_sync_create

# Session 1144: per-process client cache. Every ``OpenAI(...)`` instance
# carries its own internal httpx connection pool — so calling the factory
# afresh for every request meant zero socket reuse and contributed to the
# ~4K TIME_WAIT sockets to :443 observed during the Session 1144 leak
# audit. Cache key is ``(api_key, base_url)`` so callers using different
# providers (OpenAI / DeepSeek / Together) still get isolated clients,
# and ``**kwargs`` calls bypass the cache (rare path, hard to key safely).
_CLIENT_CACHE: Dict[Tuple[str, Optional[str]], OpenAI] = {}
_CLIENT_CACHE_LOCK = threading.Lock()

# Session 1214 Phase B: async cache parallel to the sync one. AsyncOpenAI
# wraps an internal httpx.AsyncClient with its own connection pool. Kept in
# a separate dict because OpenAI and AsyncOpenAI are not interchangeable —
# returning the wrong type would silently break callers. The underlying
# async httpx pool, like the sync one, is a process-global singleton and is
# not explicitly aclose()'d (matches sync behavior — pool dies with process).
_ASYNC_CLIENT_CACHE: Dict[Tuple[str, Optional[str]], AsyncOpenAI] = {}
_ASYNC_CLIENT_CACHE_LOCK = threading.Lock()


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
    _install_reasoning_guard(client, async_create=False)
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


def get_async_openai_client(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    **kwargs,
) -> AsyncOpenAI:
    """Return an ``AsyncOpenAI`` client with the same timeout + retry contract
    as :func:`get_openai_client`.

    Semantics mirror the sync factory: ``api_key`` falls back to the
    ``OPENAI_API_KEY`` environment variable, raises ``RuntimeError`` if
    missing, rejects forbidden kwargs (``timeout``, ``max_retries``,
    ``api_key``), and caches per ``(api_key, base_url)`` so repeat callers
    share one ``AsyncOpenAI`` instance and therefore one ``httpx.AsyncClient``
    connection pool.
    """
    resolved_key = api_key or os.getenv("OPENAI_API_KEY")
    if not resolved_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set and no api_key was provided to "
            "get_async_openai_client()"
        )

    for forbidden in _FORBIDDEN_KWARGS:
        if forbidden in kwargs:
            raise ValueError(
                f"Do not pass {forbidden!r} to get_async_openai_client(); it "
                f"is centrally managed by the factory"
            )

    cache_key = (resolved_key, base_url)
    if not kwargs:
        cached = _ASYNC_CLIENT_CACHE.get(cache_key)
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
    ctor_kwargs.update(kwargs)

    client = AsyncOpenAI(**ctor_kwargs)
    _install_reasoning_guard(client, async_create=True)
    if not kwargs:
        with _ASYNC_CLIENT_CACHE_LOCK:
            existing = _ASYNC_CLIENT_CACHE.get(cache_key)
            if existing is not None:
                return existing
            _ASYNC_CLIENT_CACHE[cache_key] = client
    return client
