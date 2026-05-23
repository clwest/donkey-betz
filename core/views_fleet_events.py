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


def _format_sse_event(envelope: dict) -> bytes:
    """Format an event envelope into SSE wire format."""
    event_id = envelope.get("event_id", "")
    event_type = envelope.get("type", "fleet_event")
    data_json = json.dumps(envelope, separators=(",", ":"))
    return (
        f"id: {event_id}\n"
        f"event: {event_type}\n"
        f"data: {data_json}\n\n"
    ).encode("utf-8")


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
    logger.info("[fleet-events] SSE subscriber connected app=%s", app_slug)

    async def event_generator():
        # Initial "hello" envelope so clients know the stream is up.
        hello = {
            "event_id": "hello",
            "type": "stream.opened",
            "created_at": "",
            "app_slug": app_slug,
            "payload": {"app_slug": app_slug},
        }
        yield _format_sse_event(hello)

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


__all__ = ["fleet_events_stream"]
