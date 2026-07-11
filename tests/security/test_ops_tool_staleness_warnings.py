"""
tests/security/test_ops_tool_staleness_warnings.py — S2760 C3 unit tests for
the new ``ops_tool.staleness_warnings`` handler.

Parallel-shape lift from ``test_ops_tool_tenant_boundary_violations.py``
(S2758). Handler under test:
``core.services.td_handlers_ops.OpsHandlersMixin._ops_staleness_warnings``.

Reads ``OpsRunEvent(label='staleness_warning')`` rows emitted by the
S2759 ``check_process_staleness`` Beat task (30-min cadence). Aggregates
by ``verdict`` (STALE_DAPHNE / STALE_CELERY / STALE_BOTH) + by
``head_commit_sha`` (which merge did the operator forget to recycle after).
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from core.services.td_handlers_ops import OpsHandlersMixin


class _OpsProxy:
    _ops_staleness_warnings = OpsHandlersMixin._ops_staleness_warnings
    _STALENESS_WARNING_VERDICTS = OpsHandlersMixin._STALENESS_WARNING_VERDICTS


def _make_warning(
    *,
    verdict: str,
    head_commit_sha: str = 'abc123def4567890fedcba0987654321abcdef00',
    head_commit_timestamp: str | None = None,
    daphne_pid: int | None = 100,
    daphne_pid_age_seconds: int | None = 14400,
    daphne_started_before_head_commit: bool | None = True,
    celery_workers_status: list | None = None,
    fix: str | None = None,
    minutes_ago: int = 0,
):
    """Create a staleness_warning OpsRunEvent row shaped like the S2759
    Beat task's real emission."""
    from datetime import timedelta
    from django.utils import timezone
    from core.models_ops_runs import OpsRunEvent
    from core.security.error_envelope import _get_or_create_rur_failure_run

    run = _get_or_create_rur_failure_run()
    event = OpsRunEvent.objects.create(
        run=run,
        event_type='step_fail',
        label='staleness_warning',
        detail={
            'source': 'check_process_staleness_beat',
            'verdict': verdict,
            'head_commit_sha': head_commit_sha,
            'head_commit_timestamp': head_commit_timestamp or '2026-07-11T19:00:00+00:00',
            'daphne_pid': daphne_pid,
            'daphne_pid_age_seconds': daphne_pid_age_seconds,
            'daphne_started_before_head_commit': daphne_started_before_head_commit,
            'celery_workers_status': celery_workers_status or [
                {
                    'hostname': 'default@host',
                    'pid': 200,
                    'pid_age_seconds': 14400,
                    'started_before_head_commit': True,
                },
            ],
            'fix': fix or (
                'Run `make recycle-all` to bring all local processes to '
                'HEAD-commit-fresh state. `make celery-recycle` alone will '
                'NOT bounce Daphne.'
            ),
        },
    )
    if minutes_ago > 0:
        event.created_at = timezone.now() - timedelta(minutes=minutes_ago)
        event.save(update_fields=['created_at'])
    return event


# --------------------------------------------------------------------------
# Empty state
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_empty_state_returns_note_and_zero_counts():
    """C3 F6 — empty state returns diagnostic note + zero aggregates.
    Cross-references ops_tool.version per the empty-state phrasing."""
    result = _OpsProxy()._ops_staleness_warnings({'window': '24h'}, trace_id='t')

    assert result['action'] == 'staleness_warnings'
    assert result['total_count'] == 0
    assert result['by_verdict'] == {}
    assert result['by_head_commit_sha'] == {}
    assert result['sample_events'] == []
    assert 'note' in result
    assert 'ops_tool.version' in result['note']


# --------------------------------------------------------------------------
# Aggregation shape (Rigby F3 — by_verdict + by_head_commit_sha)
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_aggregates_by_verdict_and_head_commit_sha():
    """C3 F3 — both aggregate buckets populate. by_head_commit_sha is the
    operational money bucket ('which merge did we forget to recycle after?').
    """
    _make_warning(verdict='STALE_DAPHNE', head_commit_sha='aaaa1111bbbb2222cccc3333dddd4444eeee5555')
    _make_warning(verdict='STALE_DAPHNE', head_commit_sha='aaaa1111bbbb2222cccc3333dddd4444eeee5555')
    _make_warning(verdict='STALE_BOTH', head_commit_sha='aaaa1111bbbb2222cccc3333dddd4444eeee5555')
    _make_warning(verdict='STALE_CELERY', head_commit_sha='ffff9999eeee8888dddd7777cccc6666bbbb5555')

    result = _OpsProxy()._ops_staleness_warnings({'window': '24h'}, trace_id='t')

    assert result['total_count'] == 4
    assert result['by_verdict'] == {
        'STALE_DAPHNE': 2,
        'STALE_BOTH': 1,
        'STALE_CELERY': 1,
    }
    # SHA truncated to 12 chars in the aggregate key
    assert result['by_head_commit_sha'] == {
        'aaaa1111bbbb': 3,
        'ffff9999eeee': 1,
    }


# --------------------------------------------------------------------------
# Sample events (Rigby F4 — process detail preserved; short SHA)
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_sample_events_preserve_full_process_detail():
    """C3 F4 — sample_events include verdict + head_commit_sha_short (12ch) +
    head_commit_timestamp + daphne_pid + daphne_pid_age_seconds +
    daphne_started_before_head_commit + celery_workers_status + fix +
    created_at. Full detail per operator-debug intent."""
    workers = [
        {'hostname': 'pa@host', 'pid': 300, 'pid_age_seconds': 21600, 'started_before_head_commit': True},
        {'hostname': 'default@host', 'pid': 301, 'pid_age_seconds': 21610, 'started_before_head_commit': True},
    ]
    _make_warning(
        verdict='STALE_BOTH',
        head_commit_sha='1234567890abcdef1234567890abcdef12345678',
        head_commit_timestamp='2026-07-11T18:30:00+00:00',
        daphne_pid=42,
        daphne_pid_age_seconds=21600,
        daphne_started_before_head_commit=True,
        celery_workers_status=workers,
    )

    result = _OpsProxy()._ops_staleness_warnings({'window': '24h'}, trace_id='t')

    assert len(result['sample_events']) == 1
    s = result['sample_events'][0]
    assert s['verdict'] == 'STALE_BOTH'
    assert s['head_commit_sha_short'] == '1234567890ab'
    assert s['head_commit_timestamp'] == '2026-07-11T18:30:00+00:00'
    assert s['daphne_pid'] == 42
    assert s['daphne_pid_age_seconds'] == 21600
    assert s['daphne_started_before_head_commit'] is True
    assert s['celery_workers_status'] == workers
    assert 'make recycle-all' in (s['fix'] or '')
    assert s['created_at'] is not None


@pytest.mark.django_db
def test_sample_events_ordered_most_recent_first():
    """Sample events ordered by created_at DESC (matches queryset)."""
    _make_warning(verdict='STALE_DAPHNE', head_commit_sha='oldest_sha_' + 'a' * 30, minutes_ago=90)
    _make_warning(verdict='STALE_DAPHNE', head_commit_sha='middle_sha_' + 'b' * 30, minutes_ago=45)
    _make_warning(verdict='STALE_DAPHNE', head_commit_sha='newest_sha_' + 'c' * 30, minutes_ago=0)

    result = _OpsProxy()._ops_staleness_warnings({'window': '24h'}, trace_id='t')

    order = [s['head_commit_sha_short'] for s in result['sample_events']]
    assert order == ['newest_sha_c', 'middle_sha_b', 'oldest_sha_a']


# --------------------------------------------------------------------------
# Filters (Rigby F2)
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_verdict_filter_matches_exact_enum():
    """verdict filter is exact enum match against the 3 stale kinds."""
    _make_warning(verdict='STALE_DAPHNE')
    _make_warning(verdict='STALE_CELERY')
    _make_warning(verdict='STALE_BOTH')

    result = _OpsProxy()._ops_staleness_warnings(
        {'window': '24h', 'verdict': 'STALE_CELERY'},
        trace_id='t',
    )

    assert result['total_count'] == 1
    assert result['verdict_filter'] == 'STALE_CELERY'
    assert list(result['by_verdict'].keys()) == ['STALE_CELERY']


@pytest.mark.django_db
def test_invalid_verdict_returns_error():
    """Invalid verdict enum returns error with allowed list. Guards against
    typos; parallels the S2758 failure_kind guard."""
    result = _OpsProxy()._ops_staleness_warnings(
        {'window': '24h', 'verdict': 'STALE_TYPO'},
        trace_id='t',
    )

    assert 'error' in result
    assert 'STALE_TYPO' in result['error']
    assert 'STALE_DAPHNE' in result['error']  # allowed list is shown


@pytest.mark.django_db
def test_window_filter_excludes_old_events():
    """window filter (1h) excludes events older than the cutoff."""
    _make_warning(verdict='STALE_DAPHNE', head_commit_sha='recent_' + 'a' * 34, minutes_ago=30)
    _make_warning(verdict='STALE_DAPHNE', head_commit_sha='old_' + 'b' * 37, minutes_ago=180)

    result = _OpsProxy()._ops_staleness_warnings({'window': '1h'}, trace_id='t')

    assert result['total_count'] == 1
    assert 'recent_aaaaa' in result['by_head_commit_sha']
    assert 'old_bbbbbbbb' not in result['by_head_commit_sha']


# --------------------------------------------------------------------------
# Limit clamping + defaults
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_limit_defaults_to_20_and_caps_at_100():
    """limit default is 20, max is 100 (parallel S2758)."""
    for i in range(25):
        _make_warning(verdict='STALE_DAPHNE', head_commit_sha=f'sha_{i:02d}_' + 'x' * 34)

    result = _OpsProxy()._ops_staleness_warnings({'window': '24h'}, trace_id='t')
    assert result['total_count'] == 25
    assert len(result['sample_events']) == 20

    result_hi = _OpsProxy()._ops_staleness_warnings(
        {'window': '24h', 'limit': 500}, trace_id='t',
    )
    assert len(result_hi['sample_events']) == 25


@pytest.mark.django_db
def test_limit_min_clamps_to_one():
    """limit min is 1 (defensive clamp against 0 or negative values)."""
    _make_warning(verdict='STALE_DAPHNE')

    result = _OpsProxy()._ops_staleness_warnings(
        {'window': '24h', 'limit': 0}, trace_id='t',
    )
    assert result['total_count'] == 1
    assert len(result['sample_events']) == 1
