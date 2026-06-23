"""Smoke tests for the Session 1220 P1 zombie agent-thread monitor.

The monitor lives at ``core/services/zombie_thread_monitor.py`` and is
surfaced via ``ops_tool.zombie_thread_rate`` in
``core/services/td_handlers_ops.py``. Wired into both ``_FuturesTimeout``
catch sites in ``core/tasks_agents.py:2425`` and
``core/agent_router.py:1551``.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
from django.core.cache import cache

from core.services.zombie_thread_monitor import (
    _counter_key,
    _hour_bucket,
    _now_utc,
    _registry_key,
    get_zombie_rate,
    record_zombie_thread,
)


@pytest.fixture(autouse=True)
def _clear_cache():
    """Each test gets a fresh cache."""
    cache.clear()
    yield
    cache.clear()


def test_record_zombie_thread_creates_hourly_counter():
    record_zombie_thread('CTOAgent')

    bucket = _hour_bucket(_now_utc())
    assert cache.get(_counter_key('CTOAgent', bucket)) == 1

    # Registry should now know about the agent.
    day = bucket[:8]
    assert 'CTOAgent' in (cache.get(_registry_key(day)) or [])


def test_record_zombie_thread_increments_existing_counter():
    record_zombie_thread('COOAgent')
    record_zombie_thread('COOAgent')
    record_zombie_thread('COOAgent')

    bucket = _hour_bucket(_now_utc())
    assert cache.get(_counter_key('COOAgent', bucket)) == 3


def test_record_zombie_thread_separates_agents():
    record_zombie_thread('CTOAgent')
    record_zombie_thread('COOAgent')
    record_zombie_thread('COOAgent')

    bucket = _hour_bucket(_now_utc())
    assert cache.get(_counter_key('CTOAgent', bucket)) == 1
    assert cache.get(_counter_key('COOAgent', bucket)) == 2


def test_record_zombie_thread_ignores_empty_agent_name():
    record_zombie_thread('')
    record_zombie_thread(None)  # type: ignore[arg-type]

    bucket = _hour_bucket(_now_utc())
    assert cache.get(_counter_key('', bucket)) is None
    # No registry entry created
    assert cache.get(_registry_key(bucket[:8])) is None


def test_get_zombie_rate_returns_empty_when_no_activity():
    result = get_zombie_rate(hours=24)

    assert result['window_hours'] == 24
    assert result['by_agent'] == {}
    assert result['top_offenders'] == []


def test_get_zombie_rate_aggregates_current_hour():
    record_zombie_thread('CTOAgent')
    record_zombie_thread('CTOAgent')
    record_zombie_thread('COOAgent')

    result = get_zombie_rate(hours=24)

    assert 'CTOAgent' in result['by_agent']
    assert result['by_agent']['CTOAgent']['total'] == 2
    assert 'COOAgent' in result['by_agent']
    assert result['by_agent']['COOAgent']['total'] == 1

    top = result['top_offenders']
    assert top[0]['agent_name'] == 'CTOAgent'
    assert top[0]['total'] == 2


def test_get_zombie_rate_filters_by_agent_name():
    record_zombie_thread('CTOAgent')
    record_zombie_thread('COOAgent')

    result = get_zombie_rate(hours=24, agent_name='CTOAgent')

    assert 'CTOAgent' in result['by_agent']
    assert 'COOAgent' not in result['by_agent']


def test_get_zombie_rate_clamps_hours():
    # Below floor
    r1 = get_zombie_rate(hours=0)
    assert r1['window_hours'] == 1
    # Above ceiling (168 = 7d)
    r2 = get_zombie_rate(hours=10_000)
    assert r2['window_hours'] == 168


def test_get_zombie_rate_includes_historic_hours():
    """A counter set in a prior hour should still show up in the
    multi-hour window query."""
    # Manually write an entry under a synthetic "1 hour ago" key.
    one_hr_ago = _now_utc() - timedelta(hours=1)
    historic_hb = _hour_bucket(one_hr_ago)
    cache.set(_counter_key('AudioAgent', historic_hb), 4, timeout=3600)
    cache.set(_registry_key(historic_hb[:8]), ['AudioAgent'], timeout=3600)

    # And a current-hour entry too.
    record_zombie_thread('AudioAgent')

    result = get_zombie_rate(hours=24)
    assert result['by_agent']['AudioAgent']['total'] == 5  # 4 historic + 1 current
    assert historic_hb in result['by_agent']['AudioAgent']['by_hour']


def test_get_zombie_rate_fails_open_on_cache_error():
    """Cache exceptions must not break the query path — return an empty
    result with an error marker instead."""
    with patch(
        'core.services.zombie_thread_monitor.cache.get',
        side_effect=RuntimeError('cache down'),
    ):
        result = get_zombie_rate(hours=24)

    assert result['by_agent'] == {}
    assert 'error' in result


def test_record_zombie_thread_fails_open_on_cache_error():
    """Cache exceptions must not break dispatch — record_zombie_thread
    swallows everything."""
    with patch(
        'core.services.zombie_thread_monitor.cache.add',
        side_effect=RuntimeError('cache down'),
    ):
        # Should not raise
        record_zombie_thread('CTOAgent')
