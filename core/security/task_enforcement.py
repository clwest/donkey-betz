"""
core.security.task_enforcement — Celery task-boundary tenant enforcement.

Ratified via I-0303 Phase 2 (2026-07-11). Scoping + Phase 1 ledger:
  docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md
  docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md

Sits above the ``core.security.object_authz`` leaf module. Imports the 5
ratified I-0302 predicates as the acceptance check between DB-row-derived
trusted state and dispatch-declared acting identity.

**Import contract:**
  * MAY import: stdlib, Django models, Django auth, Celery framework
    (`celery.Task`, `celery.signals`, `celery.current_task`), sibling
    ``core.security`` modules (``object_authz``, ``reason_codes``,
    ``error_envelope``, ``support_code``).
  * MUST NOT import: DRF, views, ``core.tasks*`` modules. That would create
    circularity — task modules consume this file at import time.

**Public API:**
  * ``@enforce_tenant_boundary(model=X, id_kwarg='...', lookup_field='pk',
    warn_only=False)`` — function-tier decorator for existing
    ``@shared_task`` bodies. ``lookup_field`` selects the row-lookup field
    (Phase 3 REPORT-ONLY widening — production tasks dispatch on CharField
    natural keys like ``conversation_id`` / ``execution_id``, not PKs).
    ``warn_only=True`` (Phase 3 REPORT-ONLY mode) emits the operator
    envelope but does NOT raise — body runs regardless.
  * ``TenantScopedTask`` — Celery ``Task`` base class for new task classes;
    declares ``tenant_model``, ``tenant_id_kwarg``, ``tenant_lookup_field``
    (default ``'pk'``), and ``warn_only`` (default ``False``) class attrs.
  * ``@system_scope`` — explicit opt-in marker for tasks that legitimately
    act as the platform, not as a user (Q2 D-verdict fail-safe default).
  * ``apply_async_with_actor(task, user, *, args=(), kwargs=None, ...)`` —
    Phase 3 dispatch helper. Attaches ``x-acting-user-id`` to Celery task
    headers while preserving all other caller-provided correlation headers.
  * ``TenantBoundaryViolation`` — exception raised on any enforcement
    failure; caught by ``task_failure`` signal hook to emit operator
    envelope. Carries the internal ``failure_kind`` discriminator.

**Enforcement algorithm** (Q1 trusted-source hierarchy):

  1. **Tier 1 — DB row.** Load ``model.objects.filter(pk=id).first()`` from
     the row referenced by ``kwargs[id_kwarg]``. Missing row => reject.
  2. **Tier 2 — Transport header.** Extract ``x-acting-user-id`` from
     ``self.request.headers`` (Celery task headers set at ``apply_async``
     time by trusted server code, NOT payload). Missing => reject.
  3. **Tier 3 — NEVER.** Payload-supplied identity is never consulted.
  4. **Ratified predicate** (from ``core.security.object_authz``) is the
     acceptance check between Tier 1 and Tier 2. Predicate returns False
     => reject.

**Existence-oracle protection** (per scoping §1 + Phase 1 ledger §5.1):
  User-facing envelope is identical for every ``failure_kind`` — no row_id,
  no discriminator, no "not found" phrasing. Operator envelope carries the
  discriminator via ``task_context.failure_kind``.

**Phase 2 limitation** (deferred to follow-on): the ``x-acting-user-id``
header is currently accepted unsigned. HMAC signing lives on the RUR-C2 /
follow-on backlog. Current guarantee: header comes from Celery transport
metadata set by trusted server code at dispatch time — not from LLM- or
caller-forgeable payload strings.
"""
from __future__ import annotations

import functools
import inspect
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from core.security.error_envelope import _emit_operator_envelope_best_effort
from core.security.support_code import make_support_code

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------
# Public constants
# --------------------------------------------------------------------------

REASON_CODE_TENANT_BOUNDARY = "tenant_boundary_violation"
SUPPORT_COMPONENT = "TENANT"
ACTING_USER_HEADER = "x-acting-user-id"
_SYSTEM_SCOPE_ATTR = "__rur_system_scope__"


# --------------------------------------------------------------------------
# Exception
# --------------------------------------------------------------------------


class TenantBoundaryViolation(Exception):
    """Raised when async-boundary tenant enforcement fails.

    Carries the operator-side ``failure_kind`` discriminator (missing_row_id,
    row_not_found, missing_acting_identity, acting_user_not_found,
    unregistered_model, predicate_rejected). User-facing envelope built from
    reason_code + support_code alone; discriminator lives in operator
    envelope only per existence-oracle protection.

    Picklable via ``__reduce__`` — Celery serializes exception results via
    pickle; a non-picklable exception ends up wrapped in
    ``UnpickleableExceptionWrapper`` and callers can't ``isinstance()`` it.
    """

    reason_code = REASON_CODE_TENANT_BOUNDARY

    def __init__(
        self,
        *,
        support_code: str,
        failure_kind: str,
        task_name: str,
        model_label: str,
        row_id: Any = None,
        acting_user_id: Any = None,
    ) -> None:
        self.support_code = support_code
        self.failure_kind = failure_kind
        self.task_name = task_name
        self.model_label = model_label
        self.row_id = row_id
        self.acting_user_id = acting_user_id
        super().__init__(f"tenant_boundary_violation: {failure_kind}")

    def __reduce__(self):
        # Round-trip through pickle by re-invoking the constructor with kwargs.
        # Celery packs task exceptions into EagerResult / AsyncResult; without
        # this reducer, kw-only __init__ can't be reconstructed → Celery
        # substitutes UnpickleableExceptionWrapper and isinstance() checks fail.
        return (
            _reconstruct_tenant_boundary_violation,
            (
                self.support_code,
                self.failure_kind,
                self.task_name,
                self.model_label,
                self.row_id,
                self.acting_user_id,
            ),
        )


def _reconstruct_tenant_boundary_violation(
    support_code: str,
    failure_kind: str,
    task_name: str,
    model_label: str,
    row_id: Any,
    acting_user_id: Any,
) -> TenantBoundaryViolation:
    """Pickle reducer target for ``TenantBoundaryViolation``. See
    ``TenantBoundaryViolation.__reduce__``.
    """
    return TenantBoundaryViolation(
        support_code=support_code,
        failure_kind=failure_kind,
        task_name=task_name,
        model_label=model_label,
        row_id=row_id,
        acting_user_id=acting_user_id,
    )


# --------------------------------------------------------------------------
# Predicate map (lazy — avoids model imports at module load)
# --------------------------------------------------------------------------


def _get_predicate_for_model(model_cls: type) -> Optional[Callable]:
    """Resolve the ratified I-0302 predicate for ``model_cls``.

    Lazy resolution — model classes are imported inside the function body to
    avoid a module-load-time cycle (task_enforcement is imported by
    core/tasks*.py modules; those modules can't safely trigger a full model
    graph load at their own import time).

    Returns ``None`` for any model not in the 5 ratified I-0302 predicates
    plus the Phase 3 REPORT-ONLY ``AgentTaskExecution`` shim (see below).
    Caller fails-closed with ``failure_kind='unregistered_model'``.
    """
    from core.security.object_authz import (
        can_read_agent_execution,
        can_read_chat_conversation,
        can_read_deliverable,
        can_read_document,
        can_read_initiative,
    )
    from core.models import ChatConversation
    from core.models_deliverables import Deliverable
    from core.models_document_registry import Initiative
    from core.models_unified_system import AgentExecution
    from core.models.agents_registry.models import AgentTaskExecution
    from content.models import Document

    # TODO(I-0303 BATCH-FIX): promote can_read_agent_task_execution to
    # core.security.object_authz and reconcile with can_read_agent_execution
    # per Phase 1 §4.4 duplicate-class caveat. This is a TEMPORARY Phase 3
    # REPORT-ONLY shim — do NOT rely on this location for the canonical
    # AgentExecution vs AgentTaskExecution decision.
    def can_read_agent_task_execution(user, row) -> bool:
        """Phase 3 REPORT-ONLY shim predicate for AgentTaskExecution.

        Row.user is a nullable ForeignKey; null-user rows are unowned and
        rejected (fail-safe default matching Q2 D-verdict). BATCH-FIX
        canonicalization will retire either this predicate OR the sibling
        AgentTaskExecution model.
        """
        row_user_id = getattr(row, "user_id", None)
        return row_user_id is not None and row_user_id == user.pk

    predicate_map = {
        Deliverable: can_read_deliverable,
        ChatConversation: can_read_chat_conversation,
        Initiative: can_read_initiative,
        AgentExecution: can_read_agent_execution,
        AgentTaskExecution: can_read_agent_task_execution,
        Document: can_read_document,
    }
    return predicate_map.get(model_cls)


# --------------------------------------------------------------------------
# Core enforcement algorithm
# --------------------------------------------------------------------------


def _resolve_row_id(
    *,
    id_kwarg: str,
    args: tuple,
    kwargs: dict,
    signature: Optional[inspect.Signature] = None,
) -> Any:
    """Resolve ``id_kwarg`` from ``args`` + ``kwargs`` using a cached signature
    when available. Returns ``None`` if the id_kwarg is not present.

    Handles both dispatch shapes: positional (``execute_agent(execution_id)``)
    and keyword (``process_deliverable(deliverable_id=X)``). Phase 1 §4.4
    caveat: some tier-0 tasks accept positional row-ids.
    """
    if id_kwarg in kwargs:
        return kwargs[id_kwarg]
    if signature is not None:
        try:
            bound = signature.bind_partial(*args, **kwargs)
        except TypeError:
            return None
        return bound.arguments.get(id_kwarg)
    return None


def _check_boundary(
    *,
    model_cls: type,
    id_kwarg: str,
    args: tuple,
    kwargs: dict,
    headers: dict,
    task_name: str,
    signature: Optional[inspect.Signature] = None,
    lookup_field: str = "pk",
) -> None:
    """Run the tenant-boundary check. Raises ``TenantBoundaryViolation`` on
    any failure. Silent return means enforcement passed and the task body
    may proceed.

    Called by ``enforce_tenant_boundary`` wrapper and ``TenantScopedTask``
    ``__call__``. Not intended for direct caller use.

    ``lookup_field`` selects the row-lookup field for
    ``model_cls.objects.filter(**{lookup_field: row_id})``. Default ``'pk'``
    preserves Phase 2 behavior. Phase 3 REPORT-ONLY targets that dispatch
    on natural-key CharFields (``conversation_id``, ``execution_id``) pass
    the matching field name explicitly.
    """
    support_code = make_support_code(SUPPORT_COMPONENT)
    model_label = model_cls.__name__

    # Tier 1 — DB row
    row_id = _resolve_row_id(
        id_kwarg=id_kwarg, args=args, kwargs=kwargs, signature=signature
    )
    if row_id is None:
        raise TenantBoundaryViolation(
            support_code=support_code,
            failure_kind="missing_row_id",
            task_name=task_name,
            model_label=model_label,
        )

    row = model_cls.objects.filter(**{lookup_field: row_id}).first()
    if row is None:
        raise TenantBoundaryViolation(
            support_code=support_code,
            failure_kind="row_not_found",
            task_name=task_name,
            model_label=model_label,
            row_id=row_id,
        )

    # Tier 2 — transport-declared acting identity
    acting_user_id = headers.get(ACTING_USER_HEADER) if headers else None
    if acting_user_id is None:
        raise TenantBoundaryViolation(
            support_code=support_code,
            failure_kind="missing_acting_identity",
            task_name=task_name,
            model_label=model_label,
            row_id=row_id,
        )

    from django.contrib.auth import get_user_model
    from django.core.exceptions import ValidationError

    user_model = get_user_model()
    try:
        acting_user = user_model.objects.filter(pk=acting_user_id).first()
    except (ValidationError, ValueError, TypeError):
        # PK may be UUID / int / other; malformed id → treat as not found
        # (identical user-facing envelope per existence-oracle discipline)
        acting_user = None
    if acting_user is None:
        raise TenantBoundaryViolation(
            support_code=support_code,
            failure_kind="acting_user_not_found",
            task_name=task_name,
            model_label=model_label,
            row_id=row_id,
            acting_user_id=acting_user_id,
        )

    # Ratified predicate = acceptance check between Tier 1 and Tier 2
    predicate = _get_predicate_for_model(model_cls)
    if predicate is None:
        raise TenantBoundaryViolation(
            support_code=support_code,
            failure_kind="unregistered_model",
            task_name=task_name,
            model_label=model_label,
        )

    if not predicate(acting_user, row):
        raise TenantBoundaryViolation(
            support_code=support_code,
            failure_kind="predicate_rejected",
            task_name=task_name,
            model_label=model_label,
            row_id=row_id,
            acting_user_id=acting_user_id,
        )


# --------------------------------------------------------------------------
# Function-tier decorator
# --------------------------------------------------------------------------


def enforce_tenant_boundary(
    *,
    model: type,
    id_kwarg: str,
    lookup_field: str = "pk",
    warn_only: bool = False,
) -> Callable:
    """Wrap a Celery task body with tenant-boundary enforcement.

    Usage::

        @shared_task(bind=True)
        @enforce_tenant_boundary(model=Deliverable, id_kwarg="deliverable_id")
        def process_deliverable(self, deliverable_id, ...):
            ...

    ``lookup_field`` (Phase 3 REPORT-ONLY substrate widening): row-lookup
    field for the tier-1 check. Default ``'pk'`` matches Phase 2 behavior.
    Tasks that dispatch on natural-key CharFields — the pattern surfaced
    at Phase 3 wiring for ``conversation_id`` / ``execution_id`` — pass
    the matching field name explicitly.

    ``warn_only=True`` (Phase 3 REPORT-ONLY mode): TenantBoundaryViolation
    is caught inside the wrapper, the operator envelope is emitted (same
    OpsRunEvent shape as enforcement mode), and the task body runs
    normally. Only ``TenantBoundaryViolation`` is caught — any other
    exception raised by ``_check_boundary`` propagates unchanged. BATCH-FIX
    → ENFORCEMENT-FLIP PRs convert ``warn_only=True`` sites to hard-gate.

    Requires the task to be dispatched via ``apply_async(..., headers={
    "x-acting-user-id": str(user.pk)})`` — the acting-identity header is
    trusted transport metadata; payload-supplied identity is NEVER consulted.
    Callers use ``apply_async_with_actor(task, user, ...)`` (below).

    Mutually exclusive with ``@system_scope``. Phase 3 conformance check
    will reject any user-owned-model task lacking exactly one marker.
    """
    def decorator(target: Callable) -> Callable:
        # Metadata for Phase 3 conformance checks — set via setattr to satisfy
        # Pyright's dynamic-attribute rules on Callable / _Wrapped protocols
        setattr(target, "__rur_tenant_model__", model)
        setattr(target, "__rur_tenant_id_kwarg__", id_kwarg)
        setattr(target, "__rur_tenant_lookup_field__", lookup_field)
        setattr(target, "__rur_tenant_warn_only__", warn_only)

        # Cache signature at decoration time — handles positional dispatch
        # (Phase 1 §4.4: tier-0 tasks like execute_agent take positional
        # row-ids) and keyword dispatch uniformly.
        try:
            target_signature: Optional[inspect.Signature] = inspect.signature(target)
        except (TypeError, ValueError):
            target_signature = None

        @functools.wraps(target)
        def wrapper(*args, **kwargs):
            if getattr(target, _SYSTEM_SCOPE_ATTR, False):
                # Defensive: mutually exclusive at Phase 3 conformance level,
                # but skip enforcement if both markers landed on the same target
                return target(*args, **kwargs)

            from celery import current_task

            task = current_task
            headers: dict = {}
            task_name = getattr(target, "__name__", "unknown")
            if task is not None:
                request = getattr(task, "request", None)
                if request is not None:
                    raw_headers = getattr(request, "headers", None)
                    if raw_headers:
                        headers = raw_headers
                task_name = getattr(task, "name", None) or task_name

            try:
                _check_boundary(
                    model_cls=model,
                    id_kwarg=id_kwarg,
                    args=args,
                    kwargs=kwargs,
                    headers=headers,
                    task_name=task_name,
                    signature=target_signature,
                    lookup_field=lookup_field,
                )
            except TenantBoundaryViolation as violation:
                if warn_only:
                    # Phase 3 REPORT-ONLY mode: emit envelope, fall through
                    # to body. task_failure signal will NOT fire (violation
                    # never escaped), so we call the parallel emission path.
                    _emit_warn_only_envelope(violation)
                else:
                    raise
            return target(*args, **kwargs)

        setattr(wrapper, "__rur_tenant_model__", model)
        setattr(wrapper, "__rur_tenant_id_kwarg__", id_kwarg)
        setattr(wrapper, "__rur_tenant_lookup_field__", lookup_field)
        setattr(wrapper, "__rur_tenant_warn_only__", warn_only)
        return wrapper

    return decorator


# --------------------------------------------------------------------------
# Class-tier Celery Task base
# --------------------------------------------------------------------------


from celery import Task as _CeleryTask  # noqa: E402 — Celery is a hard dep


class TenantScopedTask(_CeleryTask):
    """Celery ``Task`` base class that runs tenant-boundary enforcement
    before each task invocation.

    Subclasses declare ``tenant_model`` + ``tenant_id_kwarg`` class
    attributes; ``tenant_lookup_field`` (default ``'pk'``) and
    ``warn_only`` (default ``False``) may be overridden per subclass::

        class UpdateDeliverableTask(TenantScopedTask):
            tenant_model = Deliverable
            tenant_id_kwarg = "deliverable_id"
            # tenant_lookup_field = 'pk'  # default
            # warn_only = False  # default (enforcement mode)

            def run(self, deliverable_id, **kwargs):
                ...

    Applied at task-registration time via ``@shared_task(base=...)`` or
    ``@app.task(base=...)``. Same trusted-source hierarchy as the
    function-tier decorator: DB row + ``x-acting-user-id`` header +
    ratified predicate. Same failure envelope. Same warn-only semantics
    (only ``TenantBoundaryViolation`` caught; other exceptions propagate).

    A subclass may opt-in to system scope via ``@system_scope`` at the
    class level. Enforcement is skipped for system-scope classes.
    """

    tenant_model: Optional[type] = None
    tenant_id_kwarg: Optional[str] = None
    tenant_lookup_field: str = "pk"
    warn_only: bool = False

    def __call__(self, *args, **kwargs):
        if getattr(type(self), _SYSTEM_SCOPE_ATTR, False):
            return super().__call__(*args, **kwargs)

        model = self.tenant_model
        id_kwarg = self.tenant_id_kwarg
        if model is None or id_kwarg is None:
            raise TypeError(
                f"TenantScopedTask subclass {type(self).__name__} must set "
                "both `tenant_model` and `tenant_id_kwarg` class attributes"
            )

        headers: dict = {}
        request = getattr(self, "request", None)
        if request is not None:
            raw_headers = getattr(request, "headers", None)
            if raw_headers:
                headers = raw_headers

        # Celery's Task.name is typed as `str | property` in some type stubs;
        # coerce through str() + fallback via getattr to satisfy Pyright.
        task_name = str(getattr(self, "name", "") or type(self).__name__)

        # Resolve signature from self.run for positional-args support
        run_fn = getattr(self, "run", None)
        try:
            run_signature: Optional[inspect.Signature] = (
                inspect.signature(run_fn) if run_fn is not None else None
            )
        except (TypeError, ValueError):
            run_signature = None

        try:
            _check_boundary(
                model_cls=model,
                id_kwarg=id_kwarg,
                args=args,
                kwargs=kwargs,
                headers=headers,
                task_name=task_name,
                signature=run_signature,
                lookup_field=self.tenant_lookup_field,
            )
        except TenantBoundaryViolation as violation:
            if self.warn_only:
                _emit_warn_only_envelope(violation)
            else:
                raise
        return super().__call__(*args, **kwargs)


# --------------------------------------------------------------------------
# System-scope marker (Q2 explicit opt-in)
# --------------------------------------------------------------------------


def system_scope(target):
    """Mark a task callable or ``Task`` subclass as legitimately acting as
    the platform, not as a user.

    Applies to both ``@shared_task``-decorated functions and Celery ``Task``
    subclasses::

        @shared_task
        @system_scope
        def cleanup_junk_initiatives(stale_days=7):
            ...

        @system_scope
        class BeatHealthCheckTask(Task):
            def run(self):
                ...

    System-scope tasks bypass ``enforce_tenant_boundary`` / ``TenantScopedTask``
    enforcement. Justification for system scope MUST NOT be based on the file
    name (``tasks_beat_health.py``, etc.) — it must be verified body-level per
    Phase 1 ledger §7.3: the task does not read or write user-owned rows
    (Deliverable / Initiative / ChatConversation / AgentExecution / Document)
    except in aggregated, non-identifying telemetry form.

    Phase 3 conformance check will reject any user-owned-model-touching task
    that lacks exactly one of ``@enforce_tenant_boundary`` or ``@system_scope``.
    """
    setattr(target, _SYSTEM_SCOPE_ATTR, True)
    return target


# --------------------------------------------------------------------------
# Celery task_failure signal — operator envelope emission
# --------------------------------------------------------------------------


def _build_task_operator_envelope(
    *,
    sender,
    task_id: Optional[str],
    exc: TenantBoundaryViolation,
) -> dict:
    """Build the operator-side envelope for a ``TenantBoundaryViolation``.

    Distinct from ``core.security.error_envelope.build_operator_envelope`` —
    that helper is DRF/HTTP-scoped (expects ``request``). Task-boundary
    failures need ``task_context`` (task_name, task_id, model_label,
    failure_kind, row_id, acting_user_id) instead of ``request_context``.
    """
    trace_id = str(uuid.uuid4())
    task_name = None
    if sender is not None:
        task_name = getattr(sender, "name", None)
    if not task_name:
        task_name = exc.task_name

    return {
        "support_code": exc.support_code,
        "trace_id": trace_id,
        "reason_code": exc.reason_code,
        "exception_class": "TenantBoundaryViolation",
        "exception_message": f"tenant_boundary_violation: {exc.failure_kind}",
        "task_context": {
            "task_name": task_name,
            "task_id": task_id,
            "model_label": exc.model_label,
            "row_id": str(exc.row_id) if exc.row_id is not None else None,
            "acting_user_id": (
                str(exc.acting_user_id) if exc.acting_user_id is not None else None
            ),
            "failure_kind": exc.failure_kind,
        },
        "timing": {
            "detected_at": datetime.now(timezone.utc).isoformat(),
        },
    }


def _emit_warn_only_envelope(exc: TenantBoundaryViolation) -> None:
    """Emit the operator envelope for a warn-only tenant-boundary violation.

    In warn-only mode (Phase 3 REPORT-ONLY substrate widening) the wrapper
    catches ``TenantBoundaryViolation`` before it escapes the task, so
    ``celery.signals.task_failure`` never fires. This helper is the
    parallel emission path: same ``_build_task_operator_envelope`` output,
    same ``_emit_operator_envelope_best_effort`` target — so warn-only and
    enforcement-mode audit trails land in ``OpsRunEvent`` byte-identically.
    Distinguish via ``task_context.failure_kind`` (already emitted).

    Best-effort per Q9 discipline — any exception during emission is
    swallowed rather than breaking the (warn-only) task body's execution.
    """
    try:
        from celery import current_task

        sender = current_task
        task_id: Optional[str] = None
        if current_task is not None:
            request = getattr(current_task, "request", None)
            if request is not None:
                task_id = getattr(request, "id", None)
        envelope = _build_task_operator_envelope(
            sender=sender, task_id=task_id, exc=exc
        )
        _emit_operator_envelope_best_effort(envelope)
    except Exception:  # noqa: BLE001 — Q9 best-effort
        logger.warning(
            "warn-only tenant-boundary envelope emission failed (swallowed)",
            exc_info=True,
        )


def _register_task_failure_hook() -> None:
    """Connect a ``task_failure`` signal handler that emits an operator
    envelope whenever a ``TenantBoundaryViolation`` is raised.

    Registered at module import. Idempotent — Celery's signal machinery
    deduplicates connected receivers by dispatch UID.
    """
    try:
        from celery.signals import task_failure
    except ImportError:
        logger.debug(
            "celery.signals.task_failure unavailable; "
            "TenantBoundaryViolation operator envelope emission disabled"
        )
        return

    def _handler(sender=None, task_id=None, exception=None, **_kwargs):
        if not isinstance(exception, TenantBoundaryViolation):
            return
        try:
            operator_envelope = _build_task_operator_envelope(
                sender=sender, task_id=task_id, exc=exception
            )
            _emit_operator_envelope_best_effort(operator_envelope)
        except Exception:  # noqa: BLE001 — mirror error_envelope Q9 best-effort
            logger.warning(
                "task_enforcement operator-envelope emission failed (swallowed)",
                exc_info=True,
            )

    task_failure.connect(_handler, weak=False, dispatch_uid="rur_task_enforcement")


_register_task_failure_hook()


# --------------------------------------------------------------------------
# Dispatch helper — attach acting-user identity to Celery task headers
# --------------------------------------------------------------------------


def apply_async_with_actor(
    task,
    user,
    *,
    args: tuple = (),
    kwargs: Optional[dict] = None,
    headers: Optional[dict] = None,
    **options,
):
    """Dispatch a Celery task with the acting user's identity attached as
    transport-header metadata.

    Merges caller-provided ``headers`` with the acting-user header. The
    acting-user header is only inserted if the caller did not already
    provide one (caller wins on explicit ``x-acting-user-id`` collision).
    All other correlation headers (``x-request-id``, ``x-trace-id``, etc.)
    are preserved unchanged.

    ``user=None`` is accepted — the helper OMITS the ``x-acting-user-id``
    header entirely and dispatches with only the caller-provided headers.
    Substrate enforcement then emits ``missing_acting_identity`` at the
    task boundary, which is the correct report-only outcome for anonymous
    dispatches (S2757 BATCH-FIX watchpoint 1). Callers MUST NOT pass
    ``user=<falsy-non-None>`` (e.g., anonymous ``AnonymousUser``); pass
    ``user=None`` explicitly to signal "no acting identity available".

    Usage::

        from core.security.task_enforcement import apply_async_with_actor

        apply_async_with_actor(
            process_deliverable, request.user,
            kwargs={"deliverable_id": str(deliverable.pk)},
        )

    Equivalent to::

        process_deliverable.apply_async(
            kwargs={"deliverable_id": str(deliverable.pk)},
            headers={"x-acting-user-id": str(request.user.pk)},
        )

    Phase 3 BATCH-FIX PR converts HTTP dispatch sites to this helper. The
    helper ships in the REPORT-ONLY substrate PR so BATCH-FIX has a stable
    call target already in place.

    **Dual-source identity note (Rigby SIGN F4, S2757 BATCH-FIX):** some
    tasks accept a ``user_id`` payload kwarg for *bootstrap* purposes only —
    e.g., ``process_pa_chat_task`` needs ``user_id`` to create the
    ChatConversation row when ``conversation_id`` is not yet materialized.
    In those cases, the payload ``user_id`` is intentionally NOT stripped:
    the authorization identity is the ``x-acting-user-id`` header (set by
    this helper); the payload is bootstrap input, never the trust boundary.
    A future cleanup pass MUST NOT strip such payload kwargs without first
    refactoring the bootstrap flow.
    """
    merged_headers: dict = dict(headers) if headers else {}
    if user is not None:
        merged_headers.setdefault(ACTING_USER_HEADER, str(user.pk))
    return task.apply_async(
        args=args,
        kwargs=kwargs or {},
        headers=merged_headers,
        **options,
    )


__all__ = [
    "REASON_CODE_TENANT_BOUNDARY",
    "SUPPORT_COMPONENT",
    "ACTING_USER_HEADER",
    "TenantBoundaryViolation",
    "TenantScopedTask",
    "enforce_tenant_boundary",
    "system_scope",
    "apply_async_with_actor",
]
