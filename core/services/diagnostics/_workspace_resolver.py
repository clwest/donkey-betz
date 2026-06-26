"""Shared workspace_id resolver for scheduled diagnostics.

Session 1238 PR-A: Pre-fix, the 3 scheduled diagnostics
(`run_coo_daily_diagnostic`, `run_cto_daily_diagnostic`,
`run_trend_daily_diagnostic`) dispatched their respective agents
with `context['workspace_id']: None` whenever the per-diagnostic
env var (`COO_DIAG_WORKSPACE_ID` / `CTO_DIAG_WORKSPACE_ID` /
`TREND_DIAG_WORKSPACE_ID`) was unset. The router fallback then
picked the user's most-recent-active workspace, causing today's
06-26 COOAgent diagnostic deliverable to leak into the
`cf708a2e-…` debug workspace from the Session 1231 E2E sweep.

This module provides a shared resolver that returns chris's
Morning Brief workspace_id — the natural home for daily
operational diagnostic artifacts (same morning cadence as the
morning_brief workflow itself). Each diagnostic's `build_config()`
wires this into `DiagnosticConfig.workspace_resolver`.

The env-var path is preserved for ops flexibility; the priority
chain in the runner is:
    env var → workspace_resolver() → None
"""

from __future__ import annotations

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def resolve_morning_brief_workspace_id() -> Optional[str]:
    """Return the Morning Brief workspace_id for the sole operator (chris).

    Used as the default `workspace_resolver` for COO / CTO / TrendAnalysis
    daily diagnostics so their deliverables co-locate with the
    morning_brief workflow output Chris reads at 7am MDT each day.

    Returns the str UUID of `ProjectWorkspace(user='chris',
    name='Morning Brief')` if it exists. Returns None on any failure
    (missing user, missing workspace, DB error) — falling through to the
    runner's None handling, which preserves pre-fix behavior rather than
    raising during agent dispatch.

    Lazy ORM imports keep this module importable from
    `core/services/diagnostics/*` without dragging Django setup into
    test-time module loading.
    """
    try:
        from django.apps import apps
        from django.contrib.auth import get_user_model

        User = get_user_model()
        chris = User.objects.filter(username='chris').first()
        if not chris:
            logger.warning(
                'diagnostics workspace resolver: no user named "chris" '
                'found; returning None'
            )
            return None

        ProjectWorkspace = apps.get_model('core', 'ProjectWorkspace')
        ws = ProjectWorkspace.objects.filter(
            user=chris,
            name='Morning Brief',
        ).first()
        if not ws:
            logger.info(
                'diagnostics workspace resolver: chris has no Morning '
                'Brief workspace yet (probably pre-first-fire); '
                'returning None'
            )
            return None

        return str(ws.id)

    except Exception as e:
        logger.warning(
            'diagnostics workspace resolver: unexpected error (%s: %s); '
            'returning None — caller falls through to router default',
            type(e).__name__, e,
        )
        return None
