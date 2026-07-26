"""Spider diagnostic persistence (S2969 Phase 1).

Prior to S2969, the spider network runner silently skipped
``LegacySpiderData`` persistence when ``unique_items`` was empty.
Combined with dashboards that read ``LegacySpiderData`` row counts,
this made spiders that ran-but-produced-nothing appear as ``never_run``
even though ``SpiderExecutionLog`` had recorded the execution.

This module makes those runs auditable at the ``LegacySpiderData``
plane by persisting lightweight diagnostic rows. Two run classes:

- ``success_empty`` — spider ran but yielded 0 unique items after dedup
  (either the fetch returned nothing, or all items were duplicates)
- ``skipped_missing_credentials`` — spider requires env keys that were
  unset; the runner skipped the fetch entirely

Rows are tagged ``ephemeral_empty_run=True`` in the diagnostic block
when persistence mode is ``diagnostic_7d`` (the default), so the
retention sweep (``core.tasks.cleanup_empty_spider_runs``) can prune
them after seven days without touching real data rows.

Feature flags (env, read at call time so tests can patch):

- ``SPIDER_EMPTY_RUN_PERSISTENCE_MODE`` ∈
  ``{'off', 'diagnostic_7d', 'always'}`` — default ``diagnostic_7d``
- ``SPIDER_SKIP_MISSING_CREDS_LOUDLY`` ∈ ``{'true', 'false'}`` —
  default ``true``
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional


# Opt-in map of spider_name -> required env keys. When any listed key is
# unset AND SPIDER_SKIP_MISSING_CREDS_LOUDLY=true, the runner persists a
# skipped_missing_credentials diagnostic row and skips the fetch entirely.
# Kept small on purpose (spec S2969): only seed spiders where the "silent
# no-op on unset creds" symptom is documented. Broader sweep is a follow-up.
SPIDER_REQUIRED_ENV_KEYS: Dict[str, List[str]] = {
    'github': ['GITHUB_TOKEN'],
    'spotify': ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET'],
    'discord': ['DISCORD_BOT_TOKEN'],
}


EMPTY_RUN_MODE_OFF = 'off'
EMPTY_RUN_MODE_DIAGNOSTIC_7D = 'diagnostic_7d'
EMPTY_RUN_MODE_ALWAYS = 'always'
VALID_EMPTY_RUN_MODES = (
    EMPTY_RUN_MODE_OFF,
    EMPTY_RUN_MODE_DIAGNOSTIC_7D,
    EMPTY_RUN_MODE_ALWAYS,
)

STATUS_SUCCESS = 'success'
STATUS_SUCCESS_EMPTY = 'success_empty'
STATUS_SKIPPED_MISSING_CREDS = 'skipped_missing_credentials'
STATUS_FAILURE = 'failure'

EMPTY_REASON_NO_ITEMS = 'no_items'
EMPTY_REASON_ALL_DEDUPED = 'all_deduped'


def get_empty_run_persistence_mode() -> str:
    """Read persistence mode from env; unknown values fall back to
    ``diagnostic_7d`` (fail-open toward observability, not silence)."""
    mode = os.environ.get(
        'SPIDER_EMPTY_RUN_PERSISTENCE_MODE',
        EMPTY_RUN_MODE_DIAGNOSTIC_7D,
    )
    if mode not in VALID_EMPTY_RUN_MODES:
        return EMPTY_RUN_MODE_DIAGNOSTIC_7D
    return mode


def get_skip_missing_creds_loudly() -> bool:
    """Read skip-loudly toggle from env; default ``true``."""
    return os.environ.get('SPIDER_SKIP_MISSING_CREDS_LOUDLY', 'true').lower() == 'true'


def check_missing_credentials(spider_name: str) -> List[str]:
    """Return env keys required-but-unset for this spider.

    Empty list means: either no keys are declared for this spider, or
    all declared keys are set. Whitespace-only env values count as unset."""
    required = SPIDER_REQUIRED_ENV_KEYS.get(spider_name, [])
    return [key for key in required if not (os.environ.get(key) or '').strip()]


def build_empty_run_diagnostic(
    items_before_dedup: int,
    unique_after_dedup: int,
    duplicates: int,
    execution_log_id: Optional[Any] = None,
    ephemeral: bool = True,
) -> Dict[str, Any]:
    """Build the diagnostic dict for a ``success_empty`` run."""
    empty_reason = (
        EMPTY_REASON_NO_ITEMS if items_before_dedup == 0 else EMPTY_REASON_ALL_DEDUPED
    )
    return {
        'status': STATUS_SUCCESS_EMPTY,
        'empty_reason': empty_reason,
        'items_before_dedup': int(items_before_dedup),
        'unique_after_dedup': int(unique_after_dedup),
        'duplicates': int(duplicates),
        'ephemeral_empty_run': bool(ephemeral),
        'execution_log_id': str(execution_log_id) if execution_log_id else None,
    }


def build_missing_creds_diagnostic(
    missing_keys: List[str],
    execution_log_id: Optional[Any] = None,
    ephemeral: bool = True,
) -> Dict[str, Any]:
    """Build the diagnostic dict for a ``skipped_missing_credentials`` run."""
    return {
        'status': STATUS_SKIPPED_MISSING_CREDS,
        'missing_keys': list(missing_keys),
        'ephemeral_empty_run': bool(ephemeral),
        'execution_log_id': str(execution_log_id) if execution_log_id else None,
    }


def persist_diagnostic_row(
    spider_name: str,
    category: str,
    diagnostic: Dict[str, Any],
    source_url: str = 'internal',
):
    """Create a ``LegacySpiderData`` row with a diagnostic-only payload.

    Diagnostic rows have ``relevance_score=0`` so signal-quality scoring
    naturally ignores them, and are marked with the diagnostic block so
    the retention sweep can find and prune them.
    """
    from core.models_unified_system import LegacySpiderData
    return LegacySpiderData.objects.create(
        spider_name=spider_name,
        data_type=category,
        raw_data={
            'items': [],
            'diagnostic': diagnostic,
            'source': spider_name,
        },
        source_url=source_url,
        relevance_score=0,
    )
