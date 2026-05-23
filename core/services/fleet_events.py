"""Fleet event emit + subscribe (Move 3 Round 1).

Implements the event layer of
`docs/specs/FLEET_MOVE_2_ROUND_2_SPEC.md` follow-up + Rigby's Move 3
MLC: persisted `FleetEvent` rows + Redis pub/sub fan-out.

Public surface:
- `emit_event(event_type, app_slug, payload, source_artifact=None)`
  — write FleetEvent row first (commit), then publish to Redis.
- `subscribe_events(app_slug, ...)` — async generator yielding
  events from Redis (consumed by the SSE endpoint).

Locked design (Rigby, conversation pa-d19c1674b936):
- BOTH persisted DB rows AND Redis pub/sub — DB gives audit + replay,
  Redis gives low-latency fanout.
- Redis is OPTIONAL — if it's down we still write the DB row + log
  a warning. Subscribers fall back to polling (Round 2+).
- Emit AFTER DB commit so subscribers can't see an event for a row
  that doesn't exist yet.
- Event payload should include enough metadata that subscribers
  don't need a follow-up fetch.
- Filter at consuming app — u-d-b emits at app_slug granularity;
  per-user filtering is Move 4 territory.
"""
from __future__ import annotations

import json
import logging
import time
from typing import Optional

logger = logging.getLogger(__name__)


REDIS_CHANNEL_PREFIX = "fleet_events"


def _channel_name(app_slug: str) -> str:
    """Per-app channel; subscribers filter to their own app."""
    return f"{REDIS_CHANNEL_PREFIX}:{app_slug}"


def _redis_client():
    """Return a raw redis-py client built from settings.REDIS_URL, or None.

    The project uses Django's native `django.core.cache.backends.redis.RedisCache`
    (not django-redis), so `get_redis_connection` isn't available. We
    instead construct a redis-py client from the same URL used for the
    cache backend. This works whether Redis is configured or not — on
    failure we return None and the caller drops to the silent fallback.
    """
    try:
        import redis
        from django.conf import settings
        url = getattr(settings, "REDIS_URL", None) or "redis://localhost:6379/1"
        client = redis.from_url(
            url,
            socket_connect_timeout=2,
            socket_timeout=5,
            socket_keepalive=True,
        )
        # Ping once to confirm it actually works. If Redis is down we
        # want None, not a half-broken client.
        client.ping()
        return client
    except Exception as e:
        logger.debug(f"[fleet-events] Redis unavailable: {e}")
        return None


def emit_event(
    *,
    event_type: str,
    app_slug: str,
    payload: Optional[dict] = None,
    source_artifact=None,
) -> Optional[str]:
    """Emit a fleet lifecycle event.

    1. Write FleetEvent row (DB-first for audit + replay).
    2. Publish to Redis pub/sub (best-effort; failure logs but doesn't raise).

    Returns the event id on success, None on failure (DB write failure
    is the only thing that can fail this — Redis is best-effort).
    """
    from core.models.fleet import FleetEvent

    payload = payload or {}

    try:
        row = FleetEvent.objects.create(
            event_type=event_type,
            app_slug=app_slug,
            payload=payload,
            source_artifact=source_artifact,
        )
    except Exception as e:
        logger.exception(f"[fleet-events] emit failed for {event_type} app={app_slug}: {e}")
        return None

    # Now publish to Redis. Best-effort — never block the caller.
    # `seq` is the canonical cursor (Move 3 R2 / Session 1130 lock with
    # Rigby). `event_id` (UUID) is kept for FK-style joins back to the
    # FleetEvent row, but client replay is keyed on `seq`.
    envelope = {
        "event_id": str(row.id),
        "seq": row.seq,
        "type": event_type,
        "created_at": row.created_at.isoformat(),
        "app_slug": app_slug,
        "payload": payload,
    }
    try:
        client = _redis_client()
        if client is not None:
            channel = _channel_name(app_slug)
            client.publish(channel, json.dumps(envelope))
            logger.debug(
                "[fleet-events] published type=%s app=%s event_id=%s",
                event_type, app_slug, row.id,
            )
    except Exception as e:
        logger.warning(
            "[fleet-events] Redis publish failed (DB row persisted) "
            "type=%s app=%s event_id=%s: %s",
            event_type, app_slug, row.id, e,
        )

    return str(row.id)


def subscribe_events(app_slug: str, *, poll_interval: float = 0.5):
    """Iterator yielding event envelopes for a single app_slug.

    Used by the SSE endpoint. Returns dicts of the shape:
        {event_id, type, created_at, app_slug, payload}

    Behavior:
    - Subscribes to the per-app Redis channel.
    - Blocks waiting for messages with a short timeout so the caller
      (SSE generator) can send keep-alive pings between events.
    - When Redis is unreachable, yields nothing and the caller can
      retry / fall back. (For MLC, we don't implement the polling
      fallback — Round 2 can add it.)

    The generator is a plain Python generator (sync); callers using
    FastAPI/StreamingResponse with a sync generator can iterate it
    directly.
    """
    client = _redis_client()
    if client is None:
        # No Redis → no live events. SSE keep-alive will still fire
        # from the caller side. Yield nothing.
        logger.warning(
            "[fleet-events] subscribe_events: Redis unavailable for app=%s",
            app_slug,
        )
        return

    channel = _channel_name(app_slug)
    pubsub = client.pubsub(ignore_subscribe_messages=True)
    pubsub.subscribe(channel)
    logger.info("[fleet-events] subscribed app=%s channel=%s", app_slug, channel)

    try:
        while True:
            # get_message with timeout returns None on idle ticks.
            msg = pubsub.get_message(timeout=poll_interval)
            if msg is None:
                # Heartbeat tick — let caller send a keep-alive.
                yield None
                continue
            if msg.get("type") != "message":
                continue
            raw = msg.get("data")
            if raw is None:
                continue
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            try:
                envelope = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning(
                    "[fleet-events] dropping malformed message on %s: %r", channel, raw[:200]
                )
                continue
            yield envelope
    finally:
        try:
            pubsub.unsubscribe(channel)
            pubsub.close()
        except Exception:
            pass


def _async_redis_client():
    """redis.asyncio client built from settings.REDIS_URL, or None.

    Mirrors `_redis_client()` but returns an async-capable client so the
    SSE view can yield control to daphne's event loop between polls
    instead of blocking the worker thread.
    """
    try:
        import redis.asyncio as aredis
        from django.conf import settings
        url = getattr(settings, "REDIS_URL", None) or "redis://localhost:6379/1"
        client = aredis.from_url(
            url,
            socket_connect_timeout=2,
            socket_timeout=5,
            socket_keepalive=True,
        )
        return client
    except Exception as e:
        logger.debug(f"[fleet-events] async Redis unavailable: {e}")
        return None


async def asubscribe_events(app_slug: str, *, poll_interval: float = 0.5):
    """Async iterator yielding event envelopes for a single app_slug.

    Same contract as `subscribe_events` but uses redis.asyncio so it
    doesn't block daphne's event loop. Yields `None` on idle ticks so
    the SSE generator can send keep-alives.
    """
    import asyncio

    client = _async_redis_client()
    if client is None:
        logger.warning(
            "[fleet-events] asubscribe_events: Redis unavailable for app=%s",
            app_slug,
        )
        return

    channel = _channel_name(app_slug)
    pubsub = client.pubsub(ignore_subscribe_messages=True)
    await pubsub.subscribe(channel)
    logger.info(
        "[fleet-events] async subscribed app=%s channel=%s", app_slug, channel
    )

    try:
        while True:
            try:
                msg = await pubsub.get_message(timeout=poll_interval)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                logger.warning(
                    "[fleet-events] async get_message error app=%s: %s",
                    app_slug, e,
                )
                yield None
                await asyncio.sleep(poll_interval)
                continue
            if msg is None:
                yield None
                continue
            if msg.get("type") != "message":
                continue
            raw = msg.get("data")
            if raw is None:
                continue
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
            try:
                envelope = json.loads(raw)
            except json.JSONDecodeError:
                logger.warning(
                    "[fleet-events] dropping malformed async message on %s: %r",
                    channel, raw[:200],
                )
                continue
            yield envelope
    finally:
        try:
            await pubsub.unsubscribe(channel)
            await pubsub.close()
            await client.close()
        except Exception:
            pass


__all__ = ["emit_event", "subscribe_events", "asubscribe_events"]
