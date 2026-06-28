"""
platform_event_view — read-only normalized view over existing event tables.

PR 2 of the Rigby Event Intake arc. Documentation lives in
``docs/EVENT_SYSTEM_INVENTORY.md``.

Goals:
- Provide a single read API that yields a normalized event shape across
  multiple existing event tables, so future intake / decision layers do
  not have to know per-table column names.
- Strictly read-only. No writes, no migrations, no side effects.
- Watermark-friendly: callers resume from a (ts, source_id) pair.
- Deterministic ordering: ``ts ASC, source_id ASC``.
- Memory-safe: queries are filtered by watermark + optional ``limit``
  and consumed via ``.iterator()``; no ``Model.objects.all()`` scans
  without a watermark for high-volume sources.

PR 2 ships exactly two adapters:
- ``deliverable_event`` over ``core.models_deliverables.DeliverableEvent``
- ``ops_run_event`` over ``core.models_ops_runs.OpsRunEvent``

Session 1250 PR 3 adds optional ``domain`` filtering on
``source='ops_run_event'`` — caller can request ops-domain or
mission-domain rows only. The DeliverableEvent adapter is unchanged
(no domain concept); passing ``domain`` on any other source raises
``ValueError``.

Per the v0 direction in EVENT_SYSTEM_INVENTORY §4, these are deferred:
``celery_task_event``, ``llm_call_event``, ``impact_event``,
``fleet_event``, ``trigger_event``, the Cockpit family, and anything
sourced from the Redis EventBus.

Forbidden imports in this module (enforced by tests):
- ``anthropic`` / ``openai`` / any LLM client
- ``core.services.event_bus``
- ``core.models_cockpit_*``
- ``llm_call_wrapper`` and other writers

The module also performs no writes (no ``.save()``, ``.create()``,
``.delete()``, ``.bulk_create()``, ``.bulk_update()``,
``.get_or_create()``, ``.update_or_create()``).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator, Mapping, Optional


SUPPORTED_SEVERITIES: frozenset[str] = frozenset(
    {"debug", "info", "notice", "warn", "error", "critical", "unknown"}
)
SUPPORTED_VOLUME_CLASSES: frozenset[str] = frozenset({"low", "medium", "high"})

# Session 1250 PR 3: ops vs mission scope filter for OpsRunEvent only.
# DeliverableEvent does not support this filter — passing ``domain`` on
# any other source raises ValueError at the public ``iter_events``
# entrypoint.
SUPPORTED_DOMAINS: frozenset[str] = frozenset({"ops", "mission"})
DOMAIN_FILTER_SOURCES: frozenset[str] = frozenset({"ops_run_event"})

_DEFAULT_CHUNK_SIZE = 200


@dataclass(frozen=True)
class PlatformEvent:
    """Normalized event record yielded by adapters.

    Fields:
        source:         Adapter name (``deliverable_event`` / ``ops_run_event``).
        source_id:      String form of the source row's primary key.
        kind:           Source event type, verbatim (e.g. ``status_transition``,
                        ``step_fail``). Not remapped.
        severity:       One of ``SUPPORTED_SEVERITIES``. ``unknown`` when the
                        source row does not evidence a mapped severity.
        ts:             Source row's timestamp (timezone-aware datetime).
        payload:        Per-source payload dict. Keys are stable per adapter
                        but the shape differs between sources by design —
                        callers do their own per-source interpretation.
        correlation_id: Best-effort cross-source correlation key. Resolution
                        order: ``metadata['trace_id']`` →
                        ``metadata['execution_id']`` →
                        ``metadata['ctx']['trace_id']`` →
                        ``metadata['ctx']['execution_id']`` → ``None``.
        raw_ref:        Stable string handle for the source row.
                        Format: ``<source>:<source_id>``.
    """

    source: str
    source_id: str
    kind: str
    severity: str
    ts: datetime
    payload: Mapping[str, Any]
    correlation_id: Optional[str]
    raw_ref: str


def _coerce_correlation_id(*candidates: Any) -> Optional[str]:
    """Return the first non-empty candidate coerced to ``str``, else ``None``.

    None / empty-string / empty-dict candidates are skipped.
    """
    for c in candidates:
        if c is None:
            continue
        s = str(c).strip()
        if s:
            return s
    return None


class BaseAdapter(ABC):
    """Per-source adapter contract.

    Subclasses set ``source`` and ``volume_class`` at the class level and
    implement ``iter_events``. They MUST NOT perform writes of any kind.
    """

    source: str = ""
    volume_class: str = "low"

    @abstractmethod
    def iter_events(
        self,
        *,
        since_ts: Optional[datetime] = None,
        since_id: Optional[str] = None,
        limit: Optional[int] = None,
        domain: Optional[str] = None,
    ) -> Iterator[PlatformEvent]:
        ...


class DeliverableEventAdapter(BaseAdapter):
    """Adapter over ``core.models_deliverables.DeliverableEvent``.

    Severity mapping:
    - ``status_transition``: derived from ``metadata['direction']``
      (``forward`` → info, ``backward`` → warn, ``terminal`` → notice,
      ``same`` → info, anything else → unknown).
    - Other event types: per ``_SEVERITY_BY_EVENT_TYPE`` table below.
      Unrecognized event types map to ``unknown``.
    """

    source = "deliverable_event"
    volume_class = "low"

    _SEVERITY_BY_DIRECTION: dict[str, str] = {
        "forward": "info",
        "backward": "warn",
        "terminal": "notice",
        "same": "info",
    }
    _SEVERITY_BY_EVENT_TYPE: dict[str, str] = {
        "synthesis_viewed": "info",
        "deliverable_saved": "info",
        "deliverable_exported": "info",
        "shared": "info",
        "task_created": "notice",
        "followup_created": "notice",
        "action_taken": "notice",
    }

    def iter_events(
        self,
        *,
        since_ts: Optional[datetime] = None,
        since_id: Optional[str] = None,
        limit: Optional[int] = None,
        domain: Optional[str] = None,
    ) -> Iterator[PlatformEvent]:
        # PR 3 note: the public ``iter_events`` rejects ``domain`` for
        # this source before we ever get here. The kwarg is accepted to
        # satisfy the BaseAdapter contract; we ignore it.
        del domain
        # Lazy import keeps module import cheap and isolates Django setup.
        from core.models_deliverables import DeliverableEvent
        from django.db.models import Q

        qs = DeliverableEvent.objects.order_by("created_at", "id")
        if since_ts is not None and since_id is not None:
            qs = qs.filter(
                Q(created_at__gt=since_ts)
                | (Q(created_at=since_ts) & Q(id__gt=since_id))
            )
        elif since_ts is not None:
            qs = qs.filter(created_at__gt=since_ts)

        if limit is not None:
            if limit < 0:
                raise ValueError("limit must be non-negative")
            qs = qs[:limit]
            # Sliced QuerySets cannot use .iterator(); a list is bounded.
            for row in list(qs):
                yield self._normalize(row)
            return

        for row in qs.iterator(chunk_size=_DEFAULT_CHUNK_SIZE):
            yield self._normalize(row)

    def _normalize(self, row: Any) -> PlatformEvent:
        metadata: Mapping[str, Any] = row.metadata or {}
        ctx_raw = metadata.get("ctx")
        ctx: Mapping[str, Any] = ctx_raw if isinstance(ctx_raw, Mapping) else {}

        if row.event_type == "status_transition":
            direction = metadata.get("direction")
            severity = self._SEVERITY_BY_DIRECTION.get(direction or "", "unknown")
        else:
            severity = self._SEVERITY_BY_EVENT_TYPE.get(row.event_type, "unknown")

        correlation_id = _coerce_correlation_id(
            metadata.get("trace_id"),
            metadata.get("execution_id"),
            ctx.get("trace_id") if isinstance(ctx, Mapping) else None,
            ctx.get("execution_id") if isinstance(ctx, Mapping) else None,
        )

        payload: dict[str, Any] = {
            "deliverable_id": str(row.deliverable_id),
            "user_id": row.user_id,
            "event_source": row.source,
            "metadata": dict(metadata),
        }

        return PlatformEvent(
            source=self.source,
            source_id=str(row.id),
            kind=row.event_type,
            severity=severity,
            ts=row.created_at,
            payload=payload,
            correlation_id=correlation_id,
            raw_ref=f"{self.source}:{row.id}",
        )


class OpsRunEventAdapter(BaseAdapter):
    """Adapter over ``core.models_ops_runs.OpsRunEvent``.

    Severity mapping:
    - ``step_fail`` → error
    - ``step_pass`` → info
    - ``step_start`` → debug
    - ``heartbeat`` → debug
    - ``info`` → info
    - Anything else → unknown
    """

    source = "ops_run_event"
    volume_class = "medium"

    _SEVERITY_BY_EVENT_TYPE: dict[str, str] = {
        "step_start": "debug",
        "step_pass": "info",
        "step_fail": "error",
        "info": "info",
        "heartbeat": "debug",
    }

    def iter_events(
        self,
        *,
        since_ts: Optional[datetime] = None,
        since_id: Optional[str] = None,
        limit: Optional[int] = None,
        domain: Optional[str] = None,
    ) -> Iterator[PlatformEvent]:
        from core.models_ops_runs import OpsRunEvent
        from django.db.models import Q

        qs = OpsRunEvent.objects.order_by("created_at", "id")
        # Session 1250 PR 3: domain filter joins to parent OpsRun.domain.
        # ``None`` preserves PR 2 behavior (all rows).
        if domain is not None:
            qs = qs.filter(run__domain=domain)
        if since_ts is not None and since_id is not None:
            qs = qs.filter(
                Q(created_at__gt=since_ts)
                | (Q(created_at=since_ts) & Q(id__gt=since_id))
            )
        elif since_ts is not None:
            qs = qs.filter(created_at__gt=since_ts)

        if limit is not None:
            if limit < 0:
                raise ValueError("limit must be non-negative")
            qs = qs[:limit]
            for row in list(qs):
                yield self._normalize(row)
            return

        for row in qs.iterator(chunk_size=_DEFAULT_CHUNK_SIZE):
            yield self._normalize(row)

    def _normalize(self, row: Any) -> PlatformEvent:
        detail: Mapping[str, Any] = row.detail or {}
        ctx_raw = detail.get("ctx")
        ctx: Mapping[str, Any] = ctx_raw if isinstance(ctx_raw, Mapping) else {}

        severity = self._SEVERITY_BY_EVENT_TYPE.get(row.event_type, "unknown")

        correlation_id = _coerce_correlation_id(
            detail.get("trace_id"),
            detail.get("execution_id"),
            ctx.get("trace_id") if isinstance(ctx, Mapping) else None,
            ctx.get("execution_id") if isinstance(ctx, Mapping) else None,
        )

        payload: dict[str, Any] = {
            "run_id": str(row.run_id),
            "label": row.label,
            "detail": dict(detail),
        }

        return PlatformEvent(
            source=self.source,
            source_id=str(row.id),
            kind=row.event_type,
            severity=severity,
            ts=row.created_at,
            payload=payload,
            correlation_id=correlation_id,
            raw_ref=f"{self.source}:{row.id}",
        )


_ADAPTERS: dict[str, BaseAdapter] = {
    DeliverableEventAdapter.source: DeliverableEventAdapter(),
    OpsRunEventAdapter.source: OpsRunEventAdapter(),
}


def supported_sources() -> list[str]:
    """Return the list of supported adapter source names."""
    return list(_ADAPTERS.keys())


def volume_class(source: str) -> str:
    """Return the declared volume class for ``source``.

    Raises ``ValueError`` if ``source`` is not registered.
    """
    if source not in _ADAPTERS:
        raise ValueError(
            f"Unknown source: {source!r}. Supported: {sorted(_ADAPTERS)}"
        )
    return _ADAPTERS[source].volume_class


def iter_events(
    source: str,
    *,
    since_ts: Optional[datetime] = None,
    since_id: Optional[str] = None,
    limit: Optional[int] = None,
    domain: Optional[str] = None,
) -> Iterator[PlatformEvent]:
    """Yield ``PlatformEvent`` records from ``source`` in deterministic order.

    Ordering: ``ts ASC, source_id ASC``.

    Watermark semantics:
        - ``since_ts`` and ``since_id`` together: strict resume after the
          ``(ts, source_id)`` pair. Boundary tie (``ts == since_ts``) is
          handled by ``source_id > since_id``.
        - ``since_ts`` alone: strict ``ts > since_ts``.
        - Both ``None``: from the beginning.

    Session 1250 PR 3: optional ``domain`` filter.
        - ``None`` (default): preserves PR 2 behavior — yields all rows
          for the source.
        - ``'ops'`` / ``'mission'``: limits OpsRunEvent rows to those
          whose parent ``OpsRun.domain`` matches. Only supported on
          ``source='ops_run_event'``.
        - Any other value: raises ``ValueError``.
        - Passing a non-None ``domain`` on a source other than
          ``ops_run_event`` raises ``ValueError`` (DeliverableEvent has
          no domain concept).

    Idempotent — the same arguments yield the same records in the same
    order assuming the underlying rows do not change.

    Memory: queries use ``.iterator()`` with ``chunk_size=200`` for
    unbounded reads; ``limit`` is applied as a slice and materialized to
    a list (since sliced QuerySets cannot use ``.iterator()`` in
    older Django versions and the bound makes it safe).

    Raises ``ValueError`` if ``source`` is not registered, or if
    ``domain`` is invalid for the source.
    """
    if source not in _ADAPTERS:
        raise ValueError(
            f"Unknown source: {source!r}. Supported: {sorted(_ADAPTERS)}"
        )
    if domain is not None:
        if domain not in SUPPORTED_DOMAINS:
            raise ValueError(
                f"Unknown domain: {domain!r}. Supported: {sorted(SUPPORTED_DOMAINS)}"
            )
        if source not in DOMAIN_FILTER_SOURCES:
            raise ValueError(
                f"domain= filter is not supported for source={source!r}. "
                f"Supported sources: {sorted(DOMAIN_FILTER_SOURCES)}"
            )
    return _ADAPTERS[source].iter_events(
        since_ts=since_ts, since_id=since_id, limit=limit, domain=domain
    )
