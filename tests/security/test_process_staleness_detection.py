"""
tests/security/test_process_staleness_detection.py — S2759 unit tests for
the stale-Daphne / stale-Celery detection surface.

Two coverage areas:

1. ``core.services.td_handlers_ops.OpsHandlersMixin._compute_process_staleness``
   — the verdict computation logic (invoked by ``ops_tool.version`` and by
   the ``check_process_staleness`` Beat task).

2. ``core.tasks_beat_health.check_process_staleness`` — the periodic
   Beat task that emits ``OpsRunEvent(label='staleness_warning')`` when
   ``_compute_process_staleness`` reports a non-FRESH verdict.

Test approach (Rigby SIGN F5 continuity): unit-level tests via a
``_Proxy`` binding + monkey-patched ``subprocess.check_output`` returning
synthetic ``git rev-parse HEAD`` / ``git log`` / ``ps`` outputs. E2E via
live Beat dispatch is deferred — this is a diagnostic surface, not a
substrate contract.
"""
from __future__ import annotations

import subprocess
from datetime import datetime, timezone as dt_timezone

import pytest


from core.services.td_handlers_ops import OpsHandlersMixin


class _Proxy:
    """Bind ``_compute_process_staleness`` off the mixin so we can call it
    without instantiating the full tool dispatcher machinery."""

    _compute_process_staleness = OpsHandlersMixin._compute_process_staleness
    _DAPHNE_PROCESS_PATTERN = OpsHandlersMixin._DAPHNE_PROCESS_PATTERN
    _CELERY_WORKER_PROCESS_PATTERN = OpsHandlersMixin._CELERY_WORKER_PROCESS_PATTERN


def _install_fakes(
    monkeypatch,
    *,
    head_sha: str = 'abc123def4567890',
    head_commit_ts: int | None = None,
    processes: list | None = None,
    git_available: bool = True,
    psutil_available: bool = True,
):
    """Monkey-patch ``subprocess.check_output`` for git metadata + install
    a synthetic ``psutil.process_iter`` returning ``processes``.

    ``head_commit_ts`` defaults to "now - 1 hour" so age comparisons are
    meaningful without wall-clock tricks.
    """
    if head_commit_ts is None:
        head_commit_ts = int(datetime.now(tz=dt_timezone.utc).timestamp()) - 3600

    def _fake_check_output(cmd, **kwargs):
        if cmd[:2] == ['git', 'rev-parse']:
            if not git_available:
                raise subprocess.SubprocessError('no git')
            return (head_sha + '\n').encode()
        if cmd[:2] == ['git', 'log']:
            if not git_available:
                raise subprocess.SubprocessError('no git')
            return (str(head_commit_ts) + '\n').encode()
        raise RuntimeError(f'unexpected subprocess.check_output call: {cmd}')

    monkeypatch.setattr(subprocess, 'check_output', _fake_check_output)

    if not psutil_available:
        import builtins
        real_import = builtins.__import__

        def _no_psutil(name, *args, **kwargs):
            if name == 'psutil':
                raise ImportError('psutil unavailable in test')
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, '__import__', _no_psutil)
        return head_commit_ts

    import psutil

    class _FakeProc:
        def __init__(self, info: dict):
            self.info = info

    def _fake_iter(attrs=None):
        for p in (processes or []):
            yield _FakeProc(p)

    monkeypatch.setattr(psutil, 'process_iter', _fake_iter)
    return head_commit_ts


def _proc(pid: int, cmdline: list[str], age_seconds: int):
    """Produce a fake psutil.process_iter row (info dict shape)."""
    now = int(datetime.now(tz=dt_timezone.utc).timestamp())
    return {
        'pid': pid,
        'name': (cmdline[0] if cmdline else ''),
        'cmdline': cmdline,
        'create_time': now - age_seconds,
    }


# --------------------------------------------------------------------------
# Verdict — FRESH (all processes started AFTER HEAD commit time)
# --------------------------------------------------------------------------


def test_verdict_fresh_when_all_processes_post_head_commit(monkeypatch):
    """S2759 F2 — FRESH verdict when Daphne + all Celery workers started
    AFTER the HEAD commit time (they picked up the current code)."""
    # HEAD committed 1 hour ago; processes started 5 min ago (post-commit).
    _install_fakes(monkeypatch, processes=[
        _proc(100, ['/venv/bin/daphne', '-b', '127.0.0.1', '-p', '8000', 'core.asgi:application'], age_seconds=300),
        _proc(101, ['/venv/bin/celery', '-A', 'core', 'worker', '--hostname=default@host'], age_seconds=300),
        _proc(102, ['/venv/bin/celery', '-A', 'core', 'worker', '--hostname=pa@host'], age_seconds=300),
    ])

    result = _Proxy()._compute_process_staleness()

    assert result['staleness_verdict'] == 'FRESH'
    assert result['daphne_started_before_head_commit'] is False
    assert result['daphne_pid'] == 100
    assert len(result['celery_workers_status']) == 2
    for w in result['celery_workers_status']:
        assert w['started_before_head_commit'] is False
    assert 'staleness_fix' not in result
    assert result['head_commit_sha'] == 'abc123def4567890'


# --------------------------------------------------------------------------
# Verdict — STALE_DAPHNE (Daphne only)
# --------------------------------------------------------------------------


def test_verdict_stale_daphne_when_only_daphne_pre_head(monkeypatch):
    """Verdict STALE_DAPHNE when Daphne started BEFORE HEAD commit but
    Celery workers are fresh (matches the S2755/S2756/S2757 pattern —
    make celery-recycle bounced Celery only)."""
    _install_fakes(monkeypatch, processes=[
        _proc(100, ['/venv/bin/daphne', '-b', '127.0.0.1', '-p', '8000', 'core.asgi:application'], age_seconds=14400),
        _proc(101, ['/venv/bin/celery', '-A', 'core', 'worker', '--hostname=default@host'], age_seconds=300),
    ])

    result = _Proxy()._compute_process_staleness()

    assert result['staleness_verdict'] == 'STALE_DAPHNE'
    assert result['daphne_started_before_head_commit'] is True
    assert result['celery_workers_status'][0]['started_before_head_commit'] is False
    assert 'staleness_fix' in result
    assert 'make recycle-all' in result['staleness_fix']


# --------------------------------------------------------------------------
# Verdict — STALE_CELERY (workers only)
# --------------------------------------------------------------------------


def test_verdict_stale_celery_when_only_workers_pre_head(monkeypatch):
    """Verdict STALE_CELERY when Daphne is fresh but at least one Celery
    worker is pre-HEAD-commit (inverse of the STALE_DAPHNE class)."""
    _install_fakes(monkeypatch, processes=[
        _proc(100, ['/venv/bin/daphne', '-b', '127.0.0.1', '-p', '8000', 'core.asgi:application'], age_seconds=300),
        _proc(101, ['/venv/bin/celery', '-A', 'core', 'worker', '--hostname=default@host'], age_seconds=14400),
        _proc(102, ['/venv/bin/celery', '-A', 'core', 'worker', '--hostname=pa@host'], age_seconds=300),
    ])

    result = _Proxy()._compute_process_staleness()

    assert result['staleness_verdict'] == 'STALE_CELERY'
    assert result['daphne_started_before_head_commit'] is False
    stale_workers = [
        w for w in result['celery_workers_status']
        if w['started_before_head_commit']
    ]
    assert len(stale_workers) == 1
    assert stale_workers[0]['hostname'] == 'default@host'


# --------------------------------------------------------------------------
# Verdict — STALE_BOTH
# --------------------------------------------------------------------------


def test_verdict_stale_both_when_daphne_and_workers_pre_head(monkeypatch):
    """Verdict STALE_BOTH when Daphne AND workers are pre-HEAD-commit."""
    _install_fakes(monkeypatch, processes=[
        _proc(100, ['/venv/bin/daphne', '-b', '127.0.0.1', '-p', '8000', 'core.asgi:application'], age_seconds=14400),
        _proc(101, ['/venv/bin/celery', '-A', 'core', 'worker', '--hostname=default@host'], age_seconds=14400),
    ])

    result = _Proxy()._compute_process_staleness()

    assert result['staleness_verdict'] == 'STALE_BOTH'
    assert result['daphne_started_before_head_commit'] is True
    assert result['celery_workers_status'][0]['started_before_head_commit'] is True
    assert 'make recycle-all' in result['staleness_fix']


# --------------------------------------------------------------------------
# Verdict — UNKNOWN (git or ps unavailable)
# --------------------------------------------------------------------------


def test_verdict_unknown_when_git_metadata_unavailable(monkeypatch):
    """Verdict UNKNOWN when git rev-parse fails (no repo / no git binary)."""
    _install_fakes(monkeypatch, processes=[], git_available=False)

    result = _Proxy()._compute_process_staleness()

    assert result['staleness_verdict'] == 'UNKNOWN'
    assert 'staleness_error' in result


def test_verdict_unknown_when_no_processes_found(monkeypatch):
    """Verdict UNKNOWN when neither Daphne nor Celery workers are running."""
    _install_fakes(monkeypatch, processes=[
        _proc(999, ['/bin/some-unrelated-process', 'arg1'], age_seconds=60),
    ])

    result = _Proxy()._compute_process_staleness()

    assert result['staleness_verdict'] == 'UNKNOWN'
    assert result['daphne_pid'] is None
    assert result['celery_workers_status'] == []


# --------------------------------------------------------------------------
# Guard: grep-worker rows are excluded (we don't want to detect our own
# ps + grep pipeline as a Celery worker)
# --------------------------------------------------------------------------


def test_grep_matching_celery_word_is_excluded(monkeypatch):
    """A shell pipe like `ps aux | grep celery` produces a grep row that
    matches naive substring detection. Verify our filter excludes it."""
    _install_fakes(monkeypatch, processes=[
        _proc(100, ['/venv/bin/daphne', '-b', '127.0.0.1', '-p', '8000', 'core.asgi:application'], age_seconds=300),
        _proc(999, ['grep', '--color=auto', 'celery.*worker'], age_seconds=5),
    ])

    result = _Proxy()._compute_process_staleness()

    assert result['celery_workers_status'] == []
    # Daphne alone is present and fresh
    assert result['staleness_verdict'] == 'FRESH'


# --------------------------------------------------------------------------
# check_process_staleness Beat task
# --------------------------------------------------------------------------


@pytest.mark.django_db
def test_beat_task_returns_fresh_verdict_no_ops_run_event(monkeypatch):
    """Beat task returns verdict but does NOT emit OpsRunEvent when FRESH."""
    from core.tasks_beat_health import check_process_staleness
    from core.models_ops_runs import OpsRunEvent

    _install_fakes(monkeypatch, processes=[
        _proc(100, ['/venv/bin/daphne', '-b', '127.0.0.1', '-p', '8000', 'core.asgi:application'], age_seconds=300),
        _proc(101, ['/venv/bin/celery', '-A', 'core', 'worker', '--hostname=default@host'], age_seconds=300),
    ])

    before = OpsRunEvent.objects.filter(label='staleness_warning').count()

    result = check_process_staleness()

    after = OpsRunEvent.objects.filter(label='staleness_warning').count()
    assert result['verdict'] == 'FRESH'
    assert after == before, 'FRESH verdict must not emit OpsRunEvent'


@pytest.mark.django_db
def test_beat_task_emits_ops_run_event_on_stale_verdict(monkeypatch):
    """Beat task emits OpsRunEvent(label='staleness_warning') when verdict
    != FRESH — the passive 'nobody remembered' defense in depth."""
    from core.tasks_beat_health import check_process_staleness
    from core.models_ops_runs import OpsRunEvent

    _install_fakes(monkeypatch, processes=[
        _proc(100, ['/venv/bin/daphne', '-b', '127.0.0.1', '-p', '8000', 'core.asgi:application'], age_seconds=14400),
        _proc(101, ['/venv/bin/celery', '-A', 'core', 'worker', '--hostname=default@host'], age_seconds=300),
    ])

    before = OpsRunEvent.objects.filter(label='staleness_warning').count()

    result = check_process_staleness()

    after = OpsRunEvent.objects.filter(label='staleness_warning').count()
    assert result['verdict'] == 'STALE_DAPHNE'
    assert result['ops_run_event_emitted'] is True
    assert after == before + 1

    latest = OpsRunEvent.objects.filter(
        label='staleness_warning',
    ).order_by('-created_at').first()
    assert latest is not None
    detail = latest.detail
    assert detail['source'] == 'check_process_staleness_beat'
    assert detail['verdict'] == 'STALE_DAPHNE'
    assert detail['head_commit_sha'] == 'abc123def4567890'
    assert detail['daphne_pid'] == 100
    assert 'make recycle-all' in (detail.get('fix') or '')


@pytest.mark.django_db
def test_beat_task_soft_fails_on_compute_exception(monkeypatch):
    """Beat task fails soft: unexpected compute exception is caught + returns
    skipped payload. Monitor-failure-must-not-crashloop discipline (mirrors
    check_beat_health).

    The ``_compute_process_staleness`` helper catches subprocess errors and
    returns verdict=UNKNOWN, so we simulate a truly-unexpected exception
    (RuntimeError) that escapes the helper. The Beat task's own outer
    try/except swallows and returns a ``skipped`` payload.
    """
    from core.tasks_beat_health import check_process_staleness

    def _fake_boom(*args, **kwargs):
        raise RuntimeError('synthetic-compute-failure')

    # Patch the helper directly (not subprocess) so we escape the helper's
    # own SubprocessError handling and exercise the Beat task's outer guard.
    import core.tasks_beat_health as tbh
    from core.services.td_handlers_ops import OpsHandlersMixin

    monkeypatch.setattr(
        OpsHandlersMixin, '_compute_process_staleness', _fake_boom,
    )

    result = check_process_staleness()

    assert 'skipped' in result
    assert 'compute_error' in result['skipped']
