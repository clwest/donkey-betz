"""Smoke tests for the Session 1221 P2 LLMCallEvent cleanup watchdog.

The watchdog at ``core/tasks_agents._impl_cleanup_stale_llm_calls`` marks
``LLMCallEvent`` rows that have been in ``status='STARTED'`` past the
threshold as ``FAILED`` with ``error_type='timeout'`` and a clear
``error_message``. Mirror of the existing
``_impl_cleanup_stale_agent_executions``. Beat-scheduled every 10 min via
``core/celery.py``.
"""

from datetime import timedelta
from unittest.mock import MagicMock

import pytest
from django.utils import timezone

from core.models_llm_telemetry import LLMCallEvent
from core.tasks_agents import _impl_cleanup_stale_llm_calls


pytestmark = pytest.mark.django_db


def _mock_self(task_id: str = 'test-task-id'):
    """Build a stand-in for the bound Celery `self` parameter."""
    self_mock = MagicMock()
    self_mock.request.id = task_id
    return self_mock


def _stale_call(minutes_ago: int, **kwargs) -> LLMCallEvent:
    """Create an LLMCallEvent row started ``minutes_ago`` minutes in the past."""
    defaults = dict(
        agent_name='TestAgent',
        provider='openai',
        model='gpt-5-mini',
        status='STARTED',
        started_at=timezone.now() - timedelta(minutes=minutes_ago),
    )
    defaults.update(kwargs)
    return LLMCallEvent.objects.create(**defaults)


def test_marks_stale_started_row_as_failed():
    call = _stale_call(minutes_ago=15)  # 15 min old, > 10-min default

    result = _impl_cleanup_stale_llm_calls(_mock_self(), minutes_threshold=10)

    call.refresh_from_db()
    assert call.status == 'FAILED'
    assert call.error_type == 'timeout'
    assert 'watchdog_cleanup' in call.error_message
    assert call.finished_at is not None
    assert call.cancelled is True
    assert result['cleaned'] == 1


def test_skips_fresh_started_row():
    """A row started less than ``minutes_threshold`` ago must not be touched
    — those calls may still legitimately be in flight."""
    fresh = _stale_call(minutes_ago=2)

    result = _impl_cleanup_stale_llm_calls(_mock_self(), minutes_threshold=10)

    fresh.refresh_from_db()
    assert fresh.status == 'STARTED'
    assert fresh.finished_at is None
    assert result['cleaned'] == 0


def test_skips_already_completed_rows():
    """The watchdog only targets STARTED. SUCCESS / FAILED / CANCELLED rows
    are terminal and must not be re-stamped on re-fire."""
    success = _stale_call(
        minutes_ago=30,
        status='SUCCESS',
        finished_at=timezone.now() - timedelta(minutes=29),
        duration_ms=60_000,
    )
    failed = _stale_call(
        minutes_ago=30,
        status='FAILED',
        error_type='api_error',
        error_message='rate limit',
        finished_at=timezone.now() - timedelta(minutes=29),
    )

    _impl_cleanup_stale_llm_calls(_mock_self(), minutes_threshold=10)

    success.refresh_from_db()
    failed.refresh_from_db()
    assert success.status == 'SUCCESS'  # untouched
    assert failed.error_message == 'rate limit'  # untouched
    assert failed.error_type == 'api_error'  # untouched


def test_handles_multiple_stale_rows_in_one_sweep():
    for _ in range(5):
        _stale_call(minutes_ago=20)
    _stale_call(minutes_ago=1)  # fresh, should be skipped

    result = _impl_cleanup_stale_llm_calls(_mock_self(), minutes_threshold=10)

    assert result['cleaned'] == 5
    assert LLMCallEvent.objects.filter(status='STARTED').count() == 1
    assert LLMCallEvent.objects.filter(
        status='FAILED', error_type='timeout',
    ).count() == 5


def test_no_op_when_no_rows_exist():
    result = _impl_cleanup_stale_llm_calls(_mock_self(), minutes_threshold=10)
    assert result['cleaned'] == 0


def test_threshold_kwarg_is_respected():
    """Calling with ``minutes_threshold=30`` must spare rows 15min old."""
    call = _stale_call(minutes_ago=15)

    result = _impl_cleanup_stale_llm_calls(_mock_self(), minutes_threshold=30)

    call.refresh_from_db()
    assert call.status == 'STARTED'  # untouched at the wider threshold
    assert result['cleaned'] == 0


def test_error_message_names_the_threshold():
    """Operators reading the row should be able to figure out which run of
    the watchdog caught it (the threshold value tells them the cadence)."""
    call = _stale_call(minutes_ago=20)

    _impl_cleanup_stale_llm_calls(_mock_self(), minutes_threshold=10)

    call.refresh_from_db()
    assert '10+ minutes' in call.error_message
