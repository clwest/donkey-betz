"""Smoke tests for the Celery task_failure → AgentExecution bridge.

Session 1219 P1 (deliverable 6b00c112-…). The bridge in
``core/celery_telemetry.on_agent_task_failure_bridge`` marks
AgentExecution rows associated with the failed Celery task as failed —
closing the gap where SoftTimeLimitExceeded / generic task_failure
propagates past the `_FuturesTimeout` cleanup in
``tasks_agents._impl_execute_agent_task`` and leaves the row stuck in
'in_progress' until the 30-min watchdog sweep.
"""

import pytest

from core.celery_telemetry import on_agent_task_failure_bridge
from core.models_unified_system import Agent, AgentExecution


pytestmark = pytest.mark.django_db


@pytest.fixture
def agent(db):
    return Agent.objects.create(
        name='BridgeTestAgent',
        agent_type='research',
        description='Fixture agent for the failure-bridge smoke tests.',
        is_active=True,
    )


def _stale_execution(agent, celery_task_id: str) -> AgentExecution:
    return AgentExecution.objects.create(
        agent=agent,
        task='Smoke test — bridge fires on Celery task_failure',
        status='in_progress',
        input_data={
            'task': 'Smoke test',
            'context': {},
            'source': 'conversation_action_dispatch',
            'celery_task_id': celery_task_id,
        },
    )


def test_bridge_marks_stale_row_failed_on_soft_time_limit_exceeded(agent):
    """A row in 'in_progress' flips to 'failed' when its Celery task fires
    `task_failure` with `SoftTimeLimitExceeded` (the dominant leak case)."""
    from celery.exceptions import SoftTimeLimitExceeded

    execution = _stale_execution(agent, 'celery-task-uuid-soft-limit')

    on_agent_task_failure_bridge(
        sender=None,
        task_id='celery-task-uuid-soft-limit',
        exception=SoftTimeLimitExceeded('soft time limit (3600s) exceeded'),
    )

    execution.refresh_from_db()
    assert execution.status == 'failed'
    assert execution.completed_at is not None
    assert 'SoftTimeLimitExceeded' in execution.error_message
    assert 'Celery task failed' in execution.error_message


def test_bridge_marks_stale_row_failed_on_generic_exception(agent):
    """Same coverage for any other unhandled exception that produces a
    `task_failure` signal — caller doesn't have to enumerate Celery's
    exception hierarchy."""
    execution = _stale_execution(agent, 'celery-task-uuid-generic')

    on_agent_task_failure_bridge(
        sender=None,
        task_id='celery-task-uuid-generic',
        exception=RuntimeError('agent body raised'),
    )

    execution.refresh_from_db()
    assert execution.status == 'failed'
    assert 'RuntimeError' in execution.error_message
    assert 'agent body raised' in execution.error_message


def test_bridge_skips_already_completed_rows(agent):
    """The bridge filters by ``status IN ('running','in_progress')`` — rows
    that already reached 'completed'/'failed' must NOT be re-stamped, so a
    re-fired signal or race with the watchdog cleanup is a no-op."""
    execution = AgentExecution.objects.create(
        agent=agent,
        task='Already completed',
        status='completed',
        input_data={'celery_task_id': 'celery-task-uuid-completed'},
    )
    original_completed_at = execution.completed_at
    original_error = execution.error_message

    on_agent_task_failure_bridge(
        sender=None,
        task_id='celery-task-uuid-completed',
        exception=RuntimeError('should not touch this row'),
    )

    execution.refresh_from_db()
    assert execution.status == 'completed'
    assert execution.completed_at == original_completed_at
    assert execution.error_message == original_error


def test_bridge_no_op_when_no_matching_row(agent):
    """Signal for a task_id with no associated AgentExecution row is a clean
    no-op — non-agent Celery tasks (beat tasks, gateway sub-tasks) must not
    error."""
    _stale_execution(agent, 'celery-task-uuid-unrelated')

    # Different task_id — should not match the row above
    on_agent_task_failure_bridge(
        sender=None,
        task_id='celery-task-uuid-no-match',
        exception=RuntimeError('orthogonal failure'),
    )

    # Original row untouched
    rows = AgentExecution.objects.filter(
        input_data__celery_task_id='celery-task-uuid-unrelated',
    )
    assert rows.count() == 1
    assert rows.first().status == 'in_progress'


def test_bridge_truncates_long_error_messages(agent):
    """error_message field is varchar(2000); the bridge must clamp before
    write so a verbose exception repr can't blow the column."""
    execution = _stale_execution(agent, 'celery-task-uuid-long-msg')

    long_msg = 'x' * 5000  # exceeds both the 200-char repr clamp and the 2000-char DB column
    on_agent_task_failure_bridge(
        sender=None,
        task_id='celery-task-uuid-long-msg',
        exception=RuntimeError(long_msg),
    )

    execution.refresh_from_db()
    assert execution.status == 'failed'
    assert len(execution.error_message) <= 2000
