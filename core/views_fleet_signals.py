"""Fleet signal-cluster replay endpoint (Session 1131 Phase 1, Rigby's path B).

`GET /api/fleet/signals/clusters?since=<seq>&limit=50`

Returns a paginated cursor of `SignalCluster` rows that pass Rigby's
quality bar (locked Session 1131): `status=active AND cluster_size>=3
AND strength>=0.6`. Mirrors the Move 3 R2 FleetEvent.replay contract
exactly so signal-studio's consumer reuses the same cursor pattern.

Auth posture:
    - Fleet HMAC signature verification (same `verify_signed_request`
      used by views_fleet_events / views_fleet_artifacts).
    - App-slug allowlist: only `signal-studio` can call this endpoint
      (Rigby's gotcha B — the cluster firehose is not a thing other
      fleet apps should subscribe to by default).
    - Audit row persisted regardless of outcome.
"""
from __future__ import annotations

import logging
import time
from typing import Optional

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from core.services.fleet_auth import (
    DENY_STATUS_CODES,
    persist_audit_row,
    verify_signed_request,
)
from core.services.fleet_signals import (
    QUALITY_BAR_MIN_STRENGTH,
    QUALITY_BAR_STATUS,
    iter_cluster_envelopes,
)

logger = logging.getLogger(__name__)


# Defaults mirror fleet_events_replay so callers see one consistent
# contract across `/api/fleet/events/` and `/api/fleet/signals/clusters`.
REPLAY_DEFAULT_LIMIT = 50
REPLAY_MAX_LIMIT = 200

# Only signal-studio is allowlisted for the cluster firehose (Rigby's
# gotcha B). Easy to broaden later via FleetServiceIdentity.capabilities
# once we know which apps need clusters.
ALLOWED_APP_SLUGS = {"signal-studio"}


def _parse_replay_query(request) -> tuple[int, int, Optional[str]]:
    """Parse `since` + `limit`. Returns (since, limit, error_msg)."""
    raw_since = request.GET.get("since", "0")
    raw_limit = request.GET.get("limit", str(REPLAY_DEFAULT_LIMIT))
    try:
        since = int(raw_since)
    except (TypeError, ValueError):
        return 0, REPLAY_DEFAULT_LIMIT, f"invalid since={raw_since!r}; must be integer"
    if since < 0:
        return 0, REPLAY_DEFAULT_LIMIT, "since must be >= 0"
    try:
        limit = int(raw_limit)
    except (TypeError, ValueError):
        return since, REPLAY_DEFAULT_LIMIT, f"invalid limit={raw_limit!r}; must be integer"
    if limit < 1:
        limit = 1
    elif limit > REPLAY_MAX_LIMIT:
        limit = REPLAY_MAX_LIMIT
    return since, limit, None


@csrf_exempt
@require_http_methods(["GET"])
def fleet_signals_clusters_replay(request):
    """GET /api/fleet/signals/clusters — paginated cluster cursor.

    Query params:
        since (int, default 0): exclusive cursor — returns clusters
            with seq > since.
        limit (int, default 50, max 200): page size.

    Response shape (mirrors `/api/fleet/events/` for consistency):
        {
            "clusters": [<envelope>, ...],
            "next_since": <int>,
            "has_more": <bool>,
            "app_slug": "<caller>"
        }

    Auth: fleet signature required; app_slug must be in ALLOWED_APP_SLUGS.
    """
    from core.models_signal_intelligence import SignalCluster

    start_ms = time.monotonic()
    body = request.body or b""
    outcome = verify_signed_request(
        method=request.method or "GET",
        path=request.path,
        query=request.META.get("QUERY_STRING", "") or "",
        headers=request.META,
        body=body,
    )
    try:
        persist_audit_row(
            outcome,
            method=request.method or "GET",
            path=request.path,
            query=request.META.get("QUERY_STRING", "") or "",
            request_id=request.META.get("HTTP_X_REQUEST_ID", "") or "",
            ip=(request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
                or request.META.get("REMOTE_ADDR") or None),
            user_agent=request.META.get("HTTP_USER_AGENT", "") or "",
            latency_ms=int((time.monotonic() - start_ms) * 1000),
        )
    except Exception as e:  # pragma: no cover
        logger.exception("[fleet-signals] audit row persist failed: %s", e)

    if not outcome.ok:
        status = DENY_STATUS_CODES.get(outcome.deny_code, 401)
        return JsonResponse(
            {"error": {"code": outcome.deny_code, "message": outcome.message}},
            status=status,
        )

    app_slug = outcome.app_slug_resolved
    if app_slug not in ALLOWED_APP_SLUGS:
        # Authentic fleet caller but not on the allowlist. 403 is the
        # right code: signature was valid, capability was not granted.
        logger.warning(
            "[fleet-signals] forbidden app_slug=%s (allowlist=%s)",
            app_slug, sorted(ALLOWED_APP_SLUGS),
        )
        return JsonResponse(
            {"error": {
                "code": "app_slug_forbidden",
                "message": (
                    f"app_slug={app_slug!r} is not allowlisted for the "
                    f"signal-cluster firehose; current allowlist: "
                    f"{sorted(ALLOWED_APP_SLUGS)}"
                ),
            }},
            status=403,
        )

    since, limit, err = _parse_replay_query(request)
    if err is not None:
        return JsonResponse(
            {"error": {"code": "invalid_query", "message": err}},
            status=400,
        )

    # Quality bar in SQL: status + strength. cluster_size floor is
    # re-checked in the translator (see fleet_signals.cluster_envelope).
    rows = list(
        SignalCluster.objects.filter(
            seq__gt=since,
            status=QUALITY_BAR_STATUS,
            strength__gte=QUALITY_BAR_MIN_STRENGTH,
        ).order_by("seq")[:limit]
    )

    clusters = iter_cluster_envelopes(rows)

    # next_since: last seq of the SQL page (not the translated list) so
    # the cursor still advances even when a row gets dropped by the
    # cluster_size guard. If the page was empty, echo `since` back.
    next_since = rows[-1].seq if rows else since
    has_more = len(rows) == limit

    return JsonResponse({
        "clusters": clusters,
        "next_since": next_since,
        "has_more": has_more,
        "app_slug": app_slug,
    })


__all__ = ["fleet_signals_clusters_replay"]
