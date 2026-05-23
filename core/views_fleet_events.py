"""Fleet event SSE endpoint (Move 3 Round 1).

`GET /api/fleet/events/stream` — Server-Sent Events stream of fleet
lifecycle events, scoped to the caller's `app_slug` (derived from the
verified fleet signature). Fan-out via Redis pub/sub; the consuming
app filters per-user locally.

This endpoint is **fleet-only** (`FleetSignatureExclusiveAuthentication`).
End-user UIs do NOT subscribe here directly — they go through their
app's backend (the 2-hop pattern locked with Rigby).

Per Rigby's gotcha on SSE proxy/CDN headers:
    Content-Type: text/event-stream
    Cache-Control: no-cache
    Connection: keep-alive
    X-Accel-Buffering: no       (nginx-style; harmless elsewhere)

Format follows the SSE spec:
    id: <event_id>\\n
    event: <event_type>\\n
    data: <json>\\n
    \\n
"""
from __future__ import annotations

import json
import logging
import time
from typing import Optional

from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from core.services.fleet_auth import (
    DENY_STATUS_CODES,
    DenyCode,
    persist_audit_row,
    verify_signed_request,
)
from core.services.fleet_events import asubscribe_events

logger = logging.getLogger(__name__)


# Keep-alive ping cadence — SSE comment line `: ping` every N seconds
# so middle-boxes (nginx, load balancers, browser tabs) don't reap
# an idle connection.
KEEPALIVE_INTERVAL_SEC = 15.0

# Cap on best-effort SSE replay when a client reconnects with
# Last-Event-ID. Longer backlogs should use GET /api/fleet/events/
# instead — the SSE handler shouldn't buffer unbounded history.
SSE_REPLAY_CAP = 200


async def _replay_since(app_slug: str, last_seq: int):
    """Yield FleetEvent envelopes with seq > last_seq, capped + ordered.

    Move 3 R2: best-effort replay path for short reconnects. The
    canonical replay endpoint is `GET /api/fleet/events/`; this is the
    EventSource convenience hook. Caps at SSE_REPLAY_CAP events; if the
    backlog is larger the client should explicitly GET the replay
    endpoint instead.
    """
    from asgiref.sync import sync_to_async

    @sync_to_async
    def _fetch_rows():
        # Lazy import — match the pattern elsewhere in the file.
        from core.models.fleet import FleetEvent
        rows = list(
            FleetEvent.objects.filter(
                app_slug=app_slug,
                seq__gt=last_seq,
            )
            .order_by("seq")[: SSE_REPLAY_CAP + 1]
        )
        return rows

    rows = await _fetch_rows()
    # If we hit the cap, drop the last row and signal truncation so the
    # client knows it should fall back to GET /api/fleet/events/.
    truncated = len(rows) > SSE_REPLAY_CAP
    if truncated:
        rows = rows[:SSE_REPLAY_CAP]
    for row in rows:
        yield {
            "event_id": str(row.id),
            "seq": row.seq,
            "type": row.event_type,
            "created_at": row.created_at.isoformat(),
            "app_slug": row.app_slug,
            "payload": row.payload or {},
        }
    if truncated:
        # Sentinel envelope — no seq so EventSource won't advance its
        # cursor on this row, and the type tells the client to call
        # the explicit replay endpoint.
        yield {
            "event_id": "replay-truncated",
            "seq": None,
            "type": "stream.replay_truncated",
            "created_at": "",
            "app_slug": app_slug,
            "payload": {
                "cap": SSE_REPLAY_CAP,
                "hint": "GET /api/fleet/events/?since=<last_seq> for full backlog",
            },
        }


def _format_sse_event(envelope: dict) -> bytes:
    """Format an event envelope into SSE wire format.

    Move 3 R2 (Session 1130): the SSE `id:` field carries the monotonic
    `seq` value, not the UUID `event_id`. EventSource auto-tracks the
    last `id:` it saw and resends it as `Last-Event-ID` on reconnect —
    that's what `_parse_last_event_id_seq()` extracts. UUID stays in the
    `data:` body for callers who want to join back to FleetEvent rows.
    """
    seq = envelope.get("seq")
    sse_id = str(seq) if seq is not None else envelope.get("event_id", "")
    event_type = envelope.get("type", "fleet_event")
    data_json = json.dumps(envelope, separators=(",", ":"))
    return (
        f"id: {sse_id}\n"
        f"event: {event_type}\n"
        f"data: {data_json}\n\n"
    ).encode("utf-8")


def _parse_last_event_id_seq(request) -> Optional[int]:
    """Parse the `Last-Event-ID` header into an integer seq cursor.

    EventSource clients send this automatically on reconnect. We honor
    it as a *best-effort* convenience per Rigby's lock #3 — the
    canonical recovery path is still an explicit GET to
    `/api/fleet/events/?since=<seq>` followed by a fresh subscribe.
    Returns None if header missing or unparseable; the stream then
    just starts fresh from "now".
    """
    raw = request.META.get("HTTP_LAST_EVENT_ID")
    if not raw:
        return None
    try:
        value = int(raw)
        return value if value >= 0 else None
    except (TypeError, ValueError):
        return None


def _format_keepalive() -> bytes:
    return b": ping\n\n"


@csrf_exempt
@require_http_methods(["GET"])
def fleet_events_stream(request):
    """SSE stream of fleet events for the caller's app_slug.

    Uses a plain Django view (not DRF @api_view) because DRF's
    content negotiation rejects `text/event-stream` with a 406. We
    invoke the fleet signature verifier directly + write the audit
    row inline. Same security posture as the DRF auth class.
    """
    # ─── Fleet signature verification (manual, since we can't use
    #      the DRF auth class with StreamingHttpResponse). ──────────
    import time as _time
    start_ms = _time.monotonic()
    body = request.body or b""
    outcome = verify_signed_request(
        method=request.method or "GET",
        path=request.path,
        query=request.META.get("QUERY_STRING", "") or "",
        headers=request.META,
        body=body,
    )
    # Persist the audit row regardless of outcome.
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
            latency_ms=int((_time.monotonic() - start_ms) * 1000),
        )
    except Exception as e:  # pragma: no cover
        logger.exception(f"[fleet-events] audit row persist failed: {e}")

    if not outcome.ok:
        status = DENY_STATUS_CODES.get(outcome.deny_code, 401)
        return JsonResponse(
            {"error": {"code": outcome.deny_code, "message": outcome.message}},
            status=status,
        )

    app_slug = outcome.app_slug_resolved
    last_event_id_seq = _parse_last_event_id_seq(request)
    logger.info(
        "[fleet-events] SSE subscriber connected app=%s last_event_id=%s",
        app_slug, last_event_id_seq,
    )

    async def event_generator():
        # Initial "hello" envelope so clients know the stream is up.
        # No `seq` on hello — it isn't a FleetEvent row.
        hello = {
            "event_id": "hello",
            "seq": None,
            "type": "stream.opened",
            "created_at": "",
            "app_slug": app_slug,
            "payload": {
                "app_slug": app_slug,
                "last_event_id_seq": last_event_id_seq,
            },
        }
        yield _format_sse_event(hello)

        # Best-effort replay for short disconnects (Rigby's lock #3).
        # If Last-Event-ID was sent we emit any FleetEvent rows with
        # seq > last_event_id_seq, capped at SSE_REPLAY_CAP. For longer
        # backlogs the client should use GET /api/fleet/events/ — this
        # path stays bounded so the SSE handler never buffers a huge
        # backlog into memory.
        if last_event_id_seq is not None:
            try:
                async for envelope in _replay_since(app_slug, last_event_id_seq):
                    yield _format_sse_event(envelope)
            except Exception as e:
                logger.warning(
                    "[fleet-events] replay failed app=%s since=%s: %s",
                    app_slug, last_event_id_seq, e,
                )

        last_keepalive = time.monotonic()
        try:
            async for envelope in asubscribe_events(app_slug, poll_interval=1.0):
                if envelope is None:
                    # Heartbeat tick — send keep-alive if idle long enough.
                    now = time.monotonic()
                    if now - last_keepalive >= KEEPALIVE_INTERVAL_SEC:
                        yield _format_keepalive()
                        last_keepalive = now
                    continue
                yield _format_sse_event(envelope)
                last_keepalive = time.monotonic()
        except GeneratorExit:
            logger.info(
                "[fleet-events] SSE subscriber disconnected app=%s", app_slug
            )
            raise
        except Exception as e:
            logger.exception(
                "[fleet-events] SSE generator crashed app=%s: %s", app_slug, e
            )
            try:
                yield _format_sse_event({
                    "event_id": "error",
                    "type": "stream.error",
                    "created_at": "",
                    "app_slug": app_slug,
                    "payload": {"error": str(e)},
                })
            except Exception:
                pass

    response = StreamingHttpResponse(
        event_generator(),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    response["Connection"] = "keep-alive"
    response["X-Accel-Buffering"] = "no"
    return response


# ─── GET /api/fleet/events/ — replay endpoint (Move 3 R2). ─────────────
#
# Locked with Rigby (conversation pa-d19c1674b936):
# - `since` is EXCLUSIVE: returns events where `seq > since`.
# - Ordered by seq ASC (monotonic). No secondary sort needed.
# - Default limit 100, hard max 500 (configurable via env later).
# - Response includes `next_since` (last seq in page) so clients can
#   page without re-parsing the events array.
# - `has_more` is True when len(events) == limit (cheap probe; the
#   client should keep paging until len < limit, then attach SSE).
# - Auto-scoped to caller's app_slug from the verified fleet signature.
# - Signed-only (fleet identity), same posture as the stream view.

REPLAY_DEFAULT_LIMIT = 100
REPLAY_MAX_LIMIT = 500


def _parse_replay_query(request) -> tuple[int, int, Optional[str]]:
    """Parse since + limit query params. Returns (since, limit, error_msg).

    `since` defaults to 0 (replay everything from the start). `limit`
    clamps to [1, REPLAY_MAX_LIMIT]. On parse failure returns an error
    message; the caller turns that into a 400 JSON response.
    """
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
def fleet_events_replay(request):
    """GET /api/fleet/events/ — paginated replay scoped to caller's app_slug.

    Query params:
        since (int, default 0): exclusive cursor — returns events with
            seq > since.
        limit (int, default 100, max 500): page size.

    Response shape:
        {
            "events": [{event_id, seq, type, created_at, app_slug, payload}, ...],
            "next_since": <int>,   # last seq in page; same as since if empty
            "has_more": <bool>,    # True when len(events) == limit
            "app_slug": "<caller>"
        }
    """
    import time as _time
    from core.models.fleet import FleetEvent

    start_ms = _time.monotonic()
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
            latency_ms=int((_time.monotonic() - start_ms) * 1000),
        )
    except Exception as e:  # pragma: no cover
        logger.exception(f"[fleet-events] replay audit persist failed: {e}")

    if not outcome.ok:
        status = DENY_STATUS_CODES.get(outcome.deny_code, 401)
        return JsonResponse(
            {"error": {"code": outcome.deny_code, "message": outcome.message}},
            status=status,
        )

    app_slug = outcome.app_slug_resolved
    since, limit, err = _parse_replay_query(request)
    if err is not None:
        return JsonResponse(
            {"error": {"code": "invalid_query", "message": err}},
            status=400,
        )

    rows = list(
        FleetEvent.objects.filter(
            app_slug=app_slug,
            seq__gt=since,
        )
        .order_by("seq")[:limit]
    )

    events = [
        {
            "event_id": str(r.id),
            "seq": r.seq,
            "type": r.event_type,
            "created_at": r.created_at.isoformat(),
            "app_slug": r.app_slug,
            "payload": r.payload or {},
        }
        for r in rows
    ]
    # next_since: last seq in this page (Rigby's freebie). If the page
    # is empty we echo `since` back so the client doesn't accidentally
    # advance its cursor.
    next_since = rows[-1].seq if rows else since
    has_more = len(rows) == limit

    return JsonResponse({
        "events": events,
        "next_since": next_since,
        "has_more": has_more,
        "app_slug": app_slug,
    })


__all__ = ["fleet_events_stream", "fleet_events_replay"]
