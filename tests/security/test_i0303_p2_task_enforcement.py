"""
tests/security/test_i0303_p2_task_enforcement.py — I-0303 Phase 2 module
tests for the async-boundary tenant enforcement substrate.

Charter refs:
  docs/research/implementation/tenant_boundary_lockdown/I-0303_scoping.md §8 Phase 2
  docs/research/implementation/tenant_boundary_lockdown/I-030301_task_boundary_audit_ledger.md §9

Four primary paths per the Phase 2 charter:
  1. Happy path — task with @enforce_tenant_boundary succeeds when the
     acting user owns the row.
  2. Cross-tenant — user-A dispatches with user-B's row → rejected
     fail-loud with reason_code='tenant_boundary_violation'; no mutation;
     no existence-oracle in user-facing envelope.
  3. System-scope — task marked with @system_scope succeeds regardless
     of acting identity (Q2 explicit opt-in).
  4. Missing-identity — task naming a user-owned model but with no
     resolvable acting user rejects fail-loud (Q1 hierarchy exhaustion).

Test approach
-------------
The Phase 2 charter is an *algorithm* contract, not a full runtime probe.
Phase 4 harness (I-030304) is where end-to-end Celery-eager dispatch flows
are exercised. Here we test the enforcement algorithm directly via
``_check_boundary`` + the ``@enforce_tenant_boundary`` decorator + the
``TenantScopedTask`` base class — with lightweight stub tasks that avoid
Celery's eager-mode Django-transaction interaction (post_save signals in
some model classes dispatch nested tasks that hang the test worker).

Full Celery-eager sanity — one happy path + one cross-tenant — via
``.apply()`` is deferred to the Phase 4 async-boundary harness where the
regression suite runs under a controlled Celery-eager fixture.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from core.models import ChatConversation
from core.models_deliverables import Deliverable
from core.models_document_registry import Initiative
from core.security.reason_codes import get_reason
from core.security.task_enforcement import (
    ACTING_USER_HEADER,
    REASON_CODE_TENANT_BOUNDARY,
    TenantBoundaryViolation,
    TenantScopedTask,
    _check_boundary,
    enforce_tenant_boundary,
    system_scope,
)


# --------------------------------------------------------------------------
# Primary paths (Phase 2 charter §5.1-§5.4) — algorithm-direct
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_happy_path_user_owns_row(tb_user_a, tb_deliverables_a):
    """Path 1 — user-A on user-A's Deliverable → enforcement passes silently."""
    deliverable = tb_deliverables_a[0]
    _check_boundary(
        model_cls=Deliverable,
        id_kwarg="deliverable_id",
        args=(),
        kwargs={"deliverable_id": deliverable.id},
        headers={ACTING_USER_HEADER: str(tb_user_a.pk)},
        task_name="test_happy_path",
    )


@pytest.mark.django_db
def test_cross_tenant_rejection(tb_user_a, tb_deliverables_b):
    """Path 2 — user-A on user-B's Deliverable → predicate_rejected fail-loud."""
    deliverable = tb_deliverables_b[0]
    with pytest.raises(TenantBoundaryViolation) as exc_info:
        _check_boundary(
            model_cls=Deliverable,
            id_kwarg="deliverable_id",
            args=(),
            kwargs={"deliverable_id": deliverable.id},
            headers={ACTING_USER_HEADER: str(tb_user_a.pk)},
            task_name="test_cross_tenant",
        )
    exc = exc_info.value
    assert exc.reason_code == REASON_CODE_TENANT_BOUNDARY
    assert exc.failure_kind == "predicate_rejected"
    assert exc.model_label == "Deliverable"

    # Existence-oracle protection — user-facing envelope generic
    reason = get_reason(REASON_CODE_TENANT_BOUNDARY)
    assert reason.terminal_state == "DENIED"
    assert reason.typical_status == 403
    assert "not found" not in reason.default_message.lower()
    assert str(deliverable.id) not in reason.default_message
    assert exc.failure_kind not in reason.default_message


@pytest.mark.django_db
def test_system_scope_bypasses_enforcement(tb_deliverables_a):
    """Path 3 — @system_scope function skips enforcement; also verified for
    class-level marker application per the Q-D d2 unified-marker contract."""
    deliverable = tb_deliverables_a[0]

    @system_scope
    def system_task(deliverable_id):
        return {"processed": deliverable_id}

    # No enforce_tenant_boundary wrapper — @system_scope just sets attribute.
    # The unified marker is exercised by TenantScopedTask.__call__ + the
    # decorator's mutual-exclusion check (see test_baseclass_system_scope_bypass).
    assert getattr(system_task, "__rur_system_scope__", False) is True
    result = system_task(deliverable.id)
    assert result["processed"] == deliverable.id


@pytest.mark.django_db
def test_missing_acting_identity_rejection(tb_user_a, tb_deliverables_a):
    """Path 4 — user-owned model, valid row, no header → missing_acting_identity."""
    deliverable = tb_deliverables_a[0]
    with pytest.raises(TenantBoundaryViolation) as exc_info:
        _check_boundary(
            model_cls=Deliverable,
            id_kwarg="deliverable_id",
            args=(),
            kwargs={"deliverable_id": deliverable.id},
            headers={},  # No x-acting-user-id
            task_name="test_missing_identity",
        )
    exc = exc_info.value
    assert exc.reason_code == REASON_CODE_TENANT_BOUNDARY
    assert exc.failure_kind == "missing_acting_identity"


# --------------------------------------------------------------------------
# Additional failure-kind coverage (existence-oracle discipline)
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_missing_row_id_rejection(tb_user_a):
    """Row-id kwarg missing from dispatch → missing_row_id."""
    with pytest.raises(TenantBoundaryViolation) as exc_info:
        _check_boundary(
            model_cls=Deliverable,
            id_kwarg="deliverable_id",
            args=(),
            kwargs={},
            headers={ACTING_USER_HEADER: str(tb_user_a.pk)},
            task_name="test_missing_row_id",
        )
    assert exc_info.value.failure_kind == "missing_row_id"
    assert exc_info.value.reason_code == REASON_CODE_TENANT_BOUNDARY


@pytest.mark.django_db
def test_row_not_found_returns_same_envelope(tb_user_a):
    """Nonexistent row → row_not_found; SAME user-facing reason_code as
    predicate_rejected per existence-oracle protection."""
    with pytest.raises(TenantBoundaryViolation) as exc_info:
        _check_boundary(
            model_cls=Deliverable,
            id_kwarg="deliverable_id",
            args=(),
            kwargs={"deliverable_id": 999_999_999},
            headers={ACTING_USER_HEADER: str(tb_user_a.pk)},
            task_name="test_row_not_found",
        )
    assert exc_info.value.failure_kind == "row_not_found"
    assert exc_info.value.reason_code == REASON_CODE_TENANT_BOUNDARY


@pytest.mark.django_db
def test_acting_user_not_found_rejection(tb_user_a, tb_deliverables_a):
    """Header id pointing to nonexistent user → acting_user_not_found.
    Verifies UUID-vs-int PK malformed-id handling (Django User PK may be UUID
    depending on backend; malformed id must not raise ValidationError)."""
    deliverable = tb_deliverables_a[0]
    with pytest.raises(TenantBoundaryViolation) as exc_info:
        _check_boundary(
            model_cls=Deliverable,
            id_kwarg="deliverable_id",
            args=(),
            kwargs={"deliverable_id": deliverable.id},
            headers={ACTING_USER_HEADER: "malformed-id-not-a-real-pk"},
            task_name="test_acting_user_not_found",
        )
    assert exc_info.value.failure_kind == "acting_user_not_found"


# --------------------------------------------------------------------------
# Per-user model coverage (Initiative predicate)
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_per_user_model_happy_path(tb_user_a, tb_initiatives_a):
    """Per-user model (Initiative) — owner matches acting user → passes."""
    initiative = tb_initiatives_a[0]
    _check_boundary(
        model_cls=Initiative,
        id_kwarg="initiative_id",
        args=(),
        kwargs={"initiative_id": initiative.id},
        headers={ACTING_USER_HEADER: str(tb_user_a.pk)},
        task_name="test_per_user_happy",
    )


@pytest.mark.django_db
def test_per_user_model_cross_tenant(tb_user_a, tb_initiatives_b):
    """Per-user model (Initiative) — owner ≠ acting user → predicate_rejected."""
    initiative = tb_initiatives_b[0]
    with pytest.raises(TenantBoundaryViolation) as exc_info:
        _check_boundary(
            model_cls=Initiative,
            id_kwarg="initiative_id",
            args=(),
            kwargs={"initiative_id": initiative.id},
            headers={ACTING_USER_HEADER: str(tb_user_a.pk)},
            task_name="test_per_user_cross_tenant",
        )
    assert exc_info.value.failure_kind == "predicate_rejected"


# --------------------------------------------------------------------------
# Positional-args dispatch (Phase 1 §4.4 tier-0 pattern)
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_positional_args_dispatch(tb_user_a, tb_deliverables_a):
    """Positional row-id dispatch (like execute_agent(execution_id)) — signature
    binding resolves the row-id from args, not kwargs. Same acceptance path."""
    deliverable = tb_deliverables_a[0]

    @enforce_tenant_boundary(model=Deliverable, id_kwarg="deliverable_id")
    def positional_task(deliverable_id):
        return {"id": deliverable_id, "shape": "positional"}

    # Manually construct headers via a stub current_task; the decorator
    # reads current_task via celery.current_task at invocation. For a
    # non-Celery direct call, current_task is None and we route through
    # the missing-identity path. Instead, patch celery.current_task.
    fake_task = MagicMock()
    fake_task.request.headers = {ACTING_USER_HEADER: str(tb_user_a.pk)}
    fake_task.name = "positional_task"

    import celery
    original_current_task = celery.current_task
    celery.current_task = fake_task
    try:
        result = positional_task(deliverable.id)  # positional
    finally:
        celery.current_task = original_current_task

    assert result["shape"] == "positional"
    assert result["id"] == deliverable.id


@pytest.mark.django_db
def test_positional_args_cross_tenant(tb_user_a, tb_deliverables_b):
    """Positional dispatch on cross-tenant row → predicate_rejected fail-loud."""
    deliverable = tb_deliverables_b[0]

    @enforce_tenant_boundary(model=Deliverable, id_kwarg="deliverable_id")
    def positional_task(deliverable_id):
        return {"processed": deliverable_id}

    fake_task = MagicMock()
    fake_task.request.headers = {ACTING_USER_HEADER: str(tb_user_a.pk)}
    fake_task.name = "positional_task"

    import celery
    original_current_task = celery.current_task
    celery.current_task = fake_task
    try:
        with pytest.raises(TenantBoundaryViolation) as exc_info:
            positional_task(deliverable.id)
    finally:
        celery.current_task = original_current_task

    assert exc_info.value.failure_kind == "predicate_rejected"


# --------------------------------------------------------------------------
# TenantScopedTask base-class parity
# --------------------------------------------------------------------------


class _TBP2DeliverableBaseTask(TenantScopedTask):
    """Test-only base class — TenantScopedTask subclass with tenant attrs."""

    tenant_model = Deliverable
    tenant_id_kwarg = "deliverable_id"
    name = "test.tb_p2_deliverable_base"


@system_scope
class _TBP2SystemBaseTask(TenantScopedTask):
    """Test-only @system_scope-marked TenantScopedTask subclass."""

    name = "test.tb_p2_system_base"


def _install_task_request(task, headers: dict) -> None:
    """Attach a stub request context to an unbound Celery Task instance.

    Celery's ``Task.request`` is a read-only property backed by a
    thread-local ``LocalStack`` on ``task.request_stack``. Unbound task
    instances (``MyTask()`` without a Celery app) have ``request_stack ==
    None`` — ``push_request`` fails. Initialize a fresh ``LocalStack`` +
    push a ``Context`` so ``self.request.headers`` resolves correctly
    inside ``__call__``.
    """
    from celery.app.task import Context
    from celery.utils.threads import LocalStack

    if getattr(task, "request_stack", None) is None:
        task.request_stack = LocalStack()
    task.request_stack.push(Context(headers=headers))


@pytest.mark.django_db
def test_baseclass_happy_path(tb_user_a, tb_deliverables_a):
    """Base-class variant — TenantScopedTask.__call__ runs enforcement, then
    calls super().__call__ which invokes self.run. Same acceptance path
    as decorator (uniform contract per scoping §4)."""
    deliverable = tb_deliverables_a[0]

    task = _TBP2DeliverableBaseTask()
    task.run = lambda deliverable_id: {"id": deliverable_id, "via": "base_class"}
    _install_task_request(task, {ACTING_USER_HEADER: str(tb_user_a.pk)})
    try:
        result = task(deliverable_id=deliverable.id)
    finally:
        task.request_stack.pop()

    assert result["via"] == "base_class"
    assert result["id"] == deliverable.id


@pytest.mark.django_db
def test_baseclass_cross_tenant_uniform_envelope(tb_user_a, tb_deliverables_b):
    """Base-class variant — cross-tenant rejects with SAME reason_code +
    failure_kind as decorator path. Uniform contract per scoping §4."""
    deliverable = tb_deliverables_b[0]

    task = _TBP2DeliverableBaseTask()
    task.run = lambda deliverable_id: {"should": "not_be_called"}
    _install_task_request(task, {ACTING_USER_HEADER: str(tb_user_a.pk)})
    try:
        with pytest.raises(TenantBoundaryViolation) as exc_info:
            task(deliverable_id=deliverable.id)
    finally:
        task.request_stack.pop()

    assert exc_info.value.reason_code == REASON_CODE_TENANT_BOUNDARY
    assert exc_info.value.failure_kind == "predicate_rejected"
    assert exc_info.value.model_label == "Deliverable"


@pytest.mark.django_db
def test_baseclass_missing_identity(tb_deliverables_a):
    """Base-class variant — missing header rejects with missing_acting_identity."""
    deliverable = tb_deliverables_a[0]

    task = _TBP2DeliverableBaseTask()
    task.run = lambda deliverable_id: {"should": "not_be_called"}
    _install_task_request(task, {})  # No x-acting-user-id
    try:
        with pytest.raises(TenantBoundaryViolation) as exc_info:
            task(deliverable_id=deliverable.id)
    finally:
        task.request_stack.pop()

    assert exc_info.value.failure_kind == "missing_acting_identity"


@pytest.mark.django_db
def test_baseclass_system_scope_bypass(tb_deliverables_a):
    """@system_scope applied to a TenantScopedTask class → __call__ bypasses
    enforcement. Proves d2 unified marker: same decorator works on functions
    AND classes."""
    deliverable = tb_deliverables_a[0]

    task = _TBP2SystemBaseTask()
    task.run = lambda deliverable_id: {"scope": "system_baseclass"}
    _install_task_request(task, {})
    try:
        result = task(deliverable_id=deliverable.id)
    finally:
        task.request_stack.pop()

    assert result["scope"] == "system_baseclass"


# --------------------------------------------------------------------------
# Pickle round-trip (Celery serialization contract)
# --------------------------------------------------------------------------


def test_tenant_boundary_violation_is_picklable():
    """Celery packs task exceptions via pickle. Without __reduce__ on
    TenantBoundaryViolation, kw-only __init__ can't be reconstructed and
    Celery substitutes UnpickleableExceptionWrapper — callers can't
    isinstance() the exception. This test guards the contract."""
    import pickle

    original = TenantBoundaryViolation(
        support_code="RUR-TENANT-260711-abcd",
        failure_kind="predicate_rejected",
        task_name="test.task",
        model_label="Deliverable",
        row_id=42,
        acting_user_id="user-x",
    )

    round_tripped = pickle.loads(pickle.dumps(original))
    assert isinstance(round_tripped, TenantBoundaryViolation)
    assert round_tripped.reason_code == REASON_CODE_TENANT_BOUNDARY
    assert round_tripped.support_code == original.support_code
    assert round_tripped.failure_kind == original.failure_kind
    assert round_tripped.task_name == original.task_name
    assert round_tripped.model_label == original.model_label
    assert round_tripped.row_id == original.row_id
    assert round_tripped.acting_user_id == original.acting_user_id


# --------------------------------------------------------------------------
# Reason-code enum amendment verification
# --------------------------------------------------------------------------


def test_tenant_boundary_violation_registered_in_enum():
    """`tenant_boundary_violation` is a ratified reason code per contract §10
    amendment landed with Phase 2. Verifies default_message is safe (no
    existence-oracle leak) and terminal_state = DENIED / status = 403."""
    reason = get_reason(REASON_CODE_TENANT_BOUNDARY)
    assert reason.code == "tenant_boundary_violation"
    assert reason.terminal_state == "DENIED"
    assert reason.typical_status == 403
    assert reason.retryable is False
    # Existence-oracle safety — generic message with no discriminator hints
    msg = reason.default_message.lower()
    for banned in ("not found", "boundary", "cross-tenant", "workspace", "model"):
        assert banned not in msg, (
            f"reason default_message must not leak discriminator '{banned}'"
        )


def test_tenant_support_code_component_registered():
    """`TENANT` is a ratified support_code component per contract §10 amendment."""
    from core.security.support_code import make_support_code

    code = make_support_code("TENANT")
    assert code.startswith("RUR-TENANT-")
