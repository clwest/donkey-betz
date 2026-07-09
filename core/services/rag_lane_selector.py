"""
Runtime RAG Lane Selector — CDR-002 Gap 2 (P1)
==============================================

Selects between two RAG retrieval lanes at runtime:

- **LOCAL lane** (``core.rag.top_k``, reads ``.rag/corpus.jsonl``) — used
  for local development where the docs-cascade produces a filesystem
  corpus. Zero DB dependency; fastest to iterate.
- **PROD lane** (``core.rag_integration.search_embeddings``, reads
  ``DocumentEmbedding`` model via pgvector HNSW index) — used in
  production where the embedded corpus is authoritative and covers
  handoffs / research artifacts / CDRs not in ``_index.json``.

Selection precedence (highest first):

1. **Explicit env override**: ``RAG_LANE=LOCAL`` or ``RAG_LANE=PROD`` in
   the environment wins outright. Any other value logs a warning and
   falls through to (2).
2. **DEBUG-based default**: ``settings.DEBUG=True`` → LOCAL;
   ``settings.DEBUG=False`` → PROD.

This module is safe to import from ``_build_context`` (the PA turn
context builder) — no circular imports, no module-level side effects
beyond the enum + function definitions.

Governance:

- Written pre-implementation per EOS Rule R3 (acceptance-tests-first).
- Acceptance tests at ``core/tests/test_pa_knowledge_retrieval_capability.py``
  AT-4 (three tests) exercise the three selection paths.
- CDR-002 §7 Gap 2 + §10.4 P1 authoritative scope.
- Chris ratified P1 2026-07-09.
"""
from __future__ import annotations

import enum
import logging
import os
from typing import Mapping, Optional


logger = logging.getLogger(__name__)

# Env var name — explicit override. Public constant so tests + operators
# know where to look. The value is uppercased before comparison.
RAG_LANE_ENV_VAR = 'RAG_LANE'


class RagLane(enum.Enum):
    """Which RAG retrieval lane to consult.

    Values are the strings a human operator would set in ``RAG_LANE=``.
    """

    LOCAL = 'LOCAL'
    PROD = 'PROD'


def pick_lane(env: Optional[Mapping[str, str]] = None) -> RagLane:
    """Return the RAG lane to use for the current process.

    Args:
        env: Optional environment dict for testing. If ``None`` (default),
            reads from ``os.environ``. Callers should pass ``os.environ``
            or a custom dict; do NOT pass ``os.environ.copy()`` unless
            you want a snapshot rather than live env.

    Returns:
        ``RagLane.LOCAL`` or ``RagLane.PROD``.

    Precedence:
        1. ``RAG_LANE=LOCAL`` or ``RAG_LANE=PROD`` in env → honored
           outright. Case-insensitive. Whitespace stripped.
        2. Unknown ``RAG_LANE=`` value → warning logged, falls through
           to DEBUG-based default. Unknown values are NEVER honored.
        3. ``settings.DEBUG=True`` → LOCAL (dev default).
        4. Otherwise → PROD (prod default).

    This function has no side effects other than the fallthrough-warning
    log line. It is safe to call from a hot path.
    """
    e = env if env is not None else os.environ

    raw_override = e.get(RAG_LANE_ENV_VAR)
    if raw_override:
        normalized = raw_override.strip().upper()
        if normalized == 'LOCAL':
            return RagLane.LOCAL
        if normalized == 'PROD':
            return RagLane.PROD
        # Unknown value — log once and fall through. We intentionally do
        # NOT silently accept typos like 'PRODUCTION' or 'local ' — the
        # operator needs to see the misconfiguration.
        logger.warning(
            "[RAG_LANE_SELECTOR] unrecognized %s=%r — falling through to "
            "DEBUG-based default. Recognized values: 'LOCAL' | 'PROD'.",
            RAG_LANE_ENV_VAR, raw_override,
        )

    # Fallthrough: DEBUG-based default. We consult `settings.DEBUG` via a
    # local import to keep this module safe to import from any layer.
    #
    # Narrow-except discipline (S1234 D17-D21, memory rule
    # feedback_fail_loud_first_then_root_cause_then_telemetry, Rigby SIGN
    # refinement at CDR-002 §15.7): the allowlist covers only legitimate
    # env failures — Django not loaded (ImportError), settings module
    # loaded but missing DEBUG attr (AttributeError), settings module
    # improperly configured (Django's own env-error). Any OTHER exception
    # (TypeError from a broken settings monkey-patch, ValueError, etc.)
    # propagates fail-loud so tests + prod logs see it.
    from django.core.exceptions import ImproperlyConfigured
    try:
        from django.conf import settings
        debug = bool(getattr(settings, 'DEBUG', False))
    except (ImportError, AttributeError, ImproperlyConfigured) as exc:
        # Fail-safe posture: if Django isn't loaded (unusual for a
        # server process but possible in early boot or a mgmt command
        # subprocess), default to PROD — the more conservative choice
        # since PROD reads from a curated ORM table rather than a
        # filesystem cache that may not exist.
        logger.warning(
            "[RAG_LANE_SELECTOR] settings.DEBUG unreadable (%s: %s) — "
            "defaulting to PROD.",
            type(exc).__name__, exc,
        )
        debug = False

    return RagLane.LOCAL if debug else RagLane.PROD
