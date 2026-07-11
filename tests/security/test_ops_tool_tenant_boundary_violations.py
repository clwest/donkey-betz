"""
tests/security/test_ops_tool_tenant_boundary_violations.py — S2758 unit tests
for the new ``ops_tool.tenant_boundary_violations`` handler.

Handler location: ``core/services/td_handlers_ops.py``, method
``_ops_tenant_boundary_violations``. Schema entry:
``core/services/pa_tool_schemas.py`` under ``ops_tool`` action enum.

Test approach (Rigby SIGN F5):
  Handler-level unit test only. Synthetic ``OpsRunEvent`` rows are seeded
  directly via the ORM; the handler is invoked with a mixin proxy that
  binds ``_ops_tenant_boundary_violations`` to a stub instance. E2E dispatch
  through the PA loop is deferred — same rationale as Phase 2/3 tests
  (post_save-signal-dispatched nested tasks hang the eager Celery worker).
"""
from __future__ import annotations

from datetime import timedelta

import pytest
from django.utils import timezone


# Bring in the handler under test as a module-level function (bind self later).
from core.services.td_handlers_ops import OpsHandlersMixin


class _OpsProxy:
    """Minimal binding for the handler — lets us call the method without
    instantiating the full tool dispatcher machinery."""

    _ops_tenant_boundary_violations = OpsHandlersMixin._ops_tenant_boundary_violations
    _TENANT_BOUNDARY_FAILURE_KINDS = OpsHandlersMixin._TENANT_BOUNDARY_FAILURE_KINDS


def _make_event(
    *,
    task_name: str,
    failure_kind: str,
    model_label: str = 'ChatConversation',
    row_id: str | None = None,
    acting_user_id: str | None = None,
    support_code: str | None = None,
    trace_id: str | None = None,
    minutes_ago: int = 0,
):
    """Create a tenant_boundary_violation OpsRunEvent row.

    Mirrors the envelope shape emitted by
    ``core.security.task_enforcement._build_task_operator_envelope`` so
    the aggregation walks realistic ``detail.task_context`` structures.
    """
    from core.models_ops_runs import OpsRunEvent
    from core.security.error_envelope import _get_or_create_rur_failure_run

    run = _get_or_create_rur_failure_run()
    event = OpsRunEvent.objects.create(
        run=run,
        event_type='step_fail',
        label='tenant_boundary_violation',
        detail={
            'support_code': support_code or 'RUR-TENANT-260711-test',
            'trace_id': trace_id or 'trace-test',
            'reason_code': 'tenant_boundary_violation',
            'exception_class': 'TenantBoundaryViolation',
            'exception_message': f'tenant_boundary_violation: {failure_kind}',
            'task_context': {
                'task_name': task_name,
                'task_id': None,
                'model_label': model_label,
                'row_id': row_id,
                'acting_user_id': acting_user_id,
                'failure_kind': failure_kind,
            },
        },
    )
    if minutes_ago > 0:
        # Backdate for time-window filter tests.
        event.created_at = timezone.now() - timedelta(minutes=minutes_ago)
        event.save(update_fields=['created_at'])
    return event


# --------------------------------------------------------------------------
# Empty state
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_empty_state_returns_note_and_zero_counts():
    """S2758 F6 — empty state returns diagnostic note + zero aggregates."""
    result = _OpsProxy()._ops_tenant_boundary_violations({'window': '24h'}, trace_id='t')

    assert result['action'] == 'tenant_boundary_violations'
    assert result['total_count'] == 0
    assert result['by_task_name'] == {}
    assert result['by_failure_kind'] == {}
    assert result['by_task_and_kind'] == {}
    assert result['sample_events'] == []
    assert 'note' in result
    assert '24h' in result['note']


# --------------------------------------------------------------------------
# Aggregation shape
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_aggregates_by_task_name_failure_kind_and_composite():
    """Aggregation buckets populate correctly for multi-task, multi-kind data."""
    _make_event(task_name='core.tasks.summarize_conversation_task', failure_kind='row_not_found')
    _make_event(task_name='core.tasks.summarize_conversation_task', failure_kind='row_not_found')
    _make_event(task_name='core.tasks.summarize_conversation_task', failure_kind='predicate_rejected')
    _make_event(task_name='core.tasks.process_pa_chat_task', failure_kind='predicate_rejected')

    result = _OpsProxy()._ops_tenant_boundary_violations({'window': '24h'}, trace_id='t')

    assert result['total_count'] == 4
    assert result['by_task_name'] == {
        'core.tasks.summarize_conversation_task': 3,
        'core.tasks.process_pa_chat_task': 1,
    }
    assert result['by_failure_kind'] == {
        'row_not_found': 2,
        'predicate_rejected': 2,
    }
    assert result['by_task_and_kind'] == {
        'core.tasks.summarize_conversation_task/row_not_found': 2,
        'core.tasks.summarize_conversation_task/predicate_rejected': 1,
        'core.tasks.process_pa_chat_task/predicate_rejected': 1,
    }


# --------------------------------------------------------------------------
# Discriminator preservation (Rigby F4 — internal operator surface)
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_sample_events_preserve_discriminator_fields():
    """S2758 F4 — sample_events include row_id + acting_user_id + support_code
    + trace_id + failure_kind + model_label. Internal operator surface per
    Phase 2 §2.1 (user-facing envelope uniform; operator envelope keeps
    discriminator)."""
    _make_event(
        task_name='core.tasks.execute_agent',
        failure_kind='predicate_rejected',
        model_label='AgentTaskExecution',
        row_id='exec-abc-123',
        acting_user_id='42',
        support_code='RUR-TENANT-260711-b2b0',
        trace_id='trace-preserve-test',
    )

    result = _OpsProxy()._ops_tenant_boundary_violations({'window': '24h'}, trace_id='t')

    assert result['total_count'] == 1
    assert len(result['sample_events']) == 1
    sample = result['sample_events'][0]
    assert sample['task_name'] == 'core.tasks.execute_agent'
    assert sample['failure_kind'] == 'predicate_rejected'
    assert sample['model_label'] == 'AgentTaskExecution'
    assert sample['row_id'] == 'exec-abc-123'
    assert sample['acting_user_id'] == '42'
    assert sample['support_code'] == 'RUR-TENANT-260711-b2b0'
    assert sample['trace_id'] == 'trace-preserve-test'
    assert sample['created_at'] is not None


@pytest.mark.django_db
def test_sample_events_ordered_most_recent_first():
    """sample_events ordered by created_at DESC (matches queryset)."""
    _make_event(task_name='oldest', failure_kind='row_not_found', minutes_ago=60)
    _make_event(task_name='middle', failure_kind='row_not_found', minutes_ago=30)
    _make_event(task_name='newest', failure_kind='row_not_found', minutes_ago=0)

    result = _OpsProxy()._ops_tenant_boundary_violations({'window': '24h'}, trace_id='t')

    task_names = [s['task_name'] for s in result['sample_events']]
    assert task_names == ['newest', 'middle', 'oldest']


# --------------------------------------------------------------------------
# Filters
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_task_name_filter_matches_substring():
    """task_name filter uses icontains (substring match). Matches
    convention with sibling _ops_celery_task_history + parallels Rigby
    F2 clarification (icontains if used elsewhere)."""
    _make_event(task_name='core.tasks.summarize_conversation_task', failure_kind='row_not_found')
    _make_event(task_name='core.tasks.process_pa_chat_task', failure_kind='row_not_found')
    _make_event(task_name='core.tasks_agents.execute_agent', failure_kind='row_not_found')

    result = _OpsProxy()._ops_tenant_boundary_violations(
        {'window': '24h', 'task_name': 'summarize'},
        trace_id='t',
    )

    assert result['total_count'] == 1
    assert result['task_name_filter'] == 'summarize'
    assert 'core.tasks.summarize_conversation_task' in result['by_task_name']
    assert 'core.tasks.process_pa_chat_task' not in result['by_task_name']


@pytest.mark.django_db
def test_failure_kind_filter_matches_exact():
    """failure_kind filter is exact match against the 6 Phase 2 kinds."""
    _make_event(task_name='task-a', failure_kind='row_not_found')
    _make_event(task_name='task-b', failure_kind='predicate_rejected')
    _make_event(task_name='task-c', failure_kind='missing_acting_identity')

    result = _OpsProxy()._ops_tenant_boundary_violations(
        {'window': '24h', 'failure_kind': 'predicate_rejected'},
        trace_id='t',
    )

    assert result['total_count'] == 1
    assert result['failure_kind_filter'] == 'predicate_rejected'
    assert list(result['by_task_name'].keys()) == ['task-b']


@pytest.mark.django_db
def test_invalid_failure_kind_returns_error():
    """Invalid failure_kind enum returns error (guards against typos)."""
    result = _OpsProxy()._ops_tenant_boundary_violations(
        {'window': '24h', 'failure_kind': 'not_a_real_kind'},
        trace_id='t',
    )

    assert 'error' in result
    assert 'not_a_real_kind' in result['error']
    assert 'missing_row_id' in result['error']  # allowed list is shown


@pytest.mark.django_db
def test_window_filter_excludes_old_events():
    """window filter (1h) excludes events older than the cutoff."""
    _make_event(task_name='recent', failure_kind='row_not_found', minutes_ago=30)
    _make_event(task_name='old', failure_kind='row_not_found', minutes_ago=180)

    result = _OpsProxy()._ops_tenant_boundary_violations(
        {'window': '1h'},
        trace_id='t',
    )

    assert result['total_count'] == 1
    assert 'recent' in result['by_task_name']
    assert 'old' not in result['by_task_name']


# --------------------------------------------------------------------------
# Limit clamping + defaults
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_limit_defaults_to_20_and_caps_at_100():
    """limit default is 20, max is 100 (rejects out-of-range with clamp)."""
    for i in range(25):
        _make_event(task_name=f'task-{i:02d}', failure_kind='row_not_found')

    # Default limit → 20
    result = _OpsProxy()._ops_tenant_boundary_violations({'window': '24h'}, trace_id='t')
    assert result['total_count'] == 25
    assert len(result['sample_events']) == 20

    # Cap at 100
    result_hi = _OpsProxy()._ops_tenant_boundary_violations(
        {'window': '24h', 'limit': 500}, trace_id='t',
    )
    assert len(result_hi['sample_events']) == 25  # only 25 rows exist; cap is upper bound


@pytest.mark.django_db
def test_limit_min_clamps_to_one():
    """limit min is 1 (defensive clamp against 0 or negative values)."""
    _make_event(task_name='only', failure_kind='row_not_found')

    result = _OpsProxy()._ops_tenant_boundary_violations(
        {'window': '24h', 'limit': 0}, trace_id='t',
    )
    assert result['total_count'] == 1
    # limit=0 clamped to 1 — still returns at least the row
    assert len(result['sample_events']) == 1
