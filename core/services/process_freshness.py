"""S2775 N15 — process freshness computation (extracted).

Module-level ``compute_process_staleness()`` that answers the question
"are Daphne + Celery worker processes running code from the current
HEAD commit, or from an older revision?"

Extracted from ``core.services.td_handlers_ops.OpsHandler._compute_process_staleness``
so callers outside the tool-dispatch lifecycle (specifically
``core.management.commands.session_lifecycle`` for N15 freshness
telemetry) can invoke the same computation without instantiating
the ops tool handler. Behavior + return shape are byte-identical
to the pre-extraction method.

Threshold rule (unchanged from Rigby S2759 SIGN F2): a process is
stale iff its start time is BEFORE the current HEAD commit time.
No arbitrary "older than N hours" heuristic — the HEAD-commit-time
comparison is deterministic and directly connects "did this process
load the code I just merged?" to the verdict.

Return keys:
  * ``staleness_verdict``: one of ``FRESH`` / ``STALE_DAPHNE`` /
    ``STALE_CELERY`` / ``STALE_BOTH`` / ``UNKNOWN``
  * ``head_commit_sha``, ``head_commit_timestamp`` (ISO)
  * ``daphne_pid``, ``daphne_pid_age_seconds``,
    ``daphne_started_before_head_commit``
  * ``celery_workers_status``: list of {hostname, pid,
    pid_age_seconds, started_before_head_commit}
  * ``staleness_fix``: string hint (only when verdict != FRESH/UNKNOWN)
  * ``staleness_error``: string (only when verdict = UNKNOWN)
"""
from __future__ import annotations

import logging
import os
import re
import subprocess
from datetime import datetime, timezone
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

_DAPHNE_PROCESS_PATTERN = 'daphne'
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def compute_process_staleness() -> Dict[str, Any]:
    """Compare Daphne + Celery worker start times against git HEAD commit."""

    # --- HEAD commit metadata ---
    try:
        head_sha = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            cwd=_REPO_ROOT,
            stderr=subprocess.DEVNULL,
            timeout=5,
        ).decode().strip()
        head_commit_ts_raw = subprocess.check_output(
            ['git', 'log', '-1', '--format=%ct', 'HEAD'],
            cwd=_REPO_ROOT,
            stderr=subprocess.DEVNULL,
            timeout=5,
        ).decode().strip()
        head_commit_timestamp = int(head_commit_ts_raw)
        head_commit_iso = datetime.fromtimestamp(
            head_commit_timestamp, tz=timezone.utc,
        ).isoformat()
    except (subprocess.SubprocessError, ValueError, FileNotFoundError):
        return {
            'staleness_verdict': 'UNKNOWN',
            'staleness_error': 'git HEAD metadata unavailable',
        }

    # --- Process discovery via psutil (cross-platform) ---
    try:
        import psutil
    except ImportError:
        return {
            'staleness_verdict': 'UNKNOWN',
            'staleness_error': 'psutil not available',
        }

    daphne_row = None
    celery_worker_rows: List[Dict[str, Any]] = []
    now_seconds = int(datetime.now(tz=timezone.utc).timestamp())

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
        try:
            info = proc.info
            cmdline = info.get('cmdline') or []
            cmd = ' '.join(cmdline) if cmdline else (info.get('name') or '')
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
        if not cmd:
            continue

        proc_start_ts = int(info.get('create_time') or 0)
        if proc_start_ts == 0:
            continue

        pid_age_seconds = max(0, now_seconds - proc_start_ts)
        is_daphne = _DAPHNE_PROCESS_PATTERN in cmd
        is_celery_worker = (
            'celery' in cmd
            and 'worker' in cmd
            and 'grep' not in cmd
        )

        if is_daphne and daphne_row is None:
            daphne_row = {
                'pid': info.get('pid'),
                'pid_age_seconds': pid_age_seconds,
                'started_at_ts': proc_start_ts,
                'started_before_head_commit':
                    proc_start_ts < head_commit_timestamp,
            }
        elif is_celery_worker:
            hostname_match = re.search(r'hostname=([^\s]+)', cmd)
            hostname = (
                hostname_match.group(1) if hostname_match else 'unknown'
            )
            celery_worker_rows.append({
                'hostname': hostname,
                'pid': info.get('pid'),
                'pid_age_seconds': pid_age_seconds,
                'started_before_head_commit':
                    proc_start_ts < head_commit_timestamp,
            })

    # --- Verdict resolution ---
    daphne_stale = (
        daphne_row is not None
        and daphne_row['started_before_head_commit']
    )
    celery_stale = any(
        w['started_before_head_commit'] for w in celery_worker_rows
    )

    if daphne_row is None and not celery_worker_rows:
        verdict = 'UNKNOWN'
    elif daphne_stale and celery_stale:
        verdict = 'STALE_BOTH'
    elif daphne_stale:
        verdict = 'STALE_DAPHNE'
    elif celery_stale:
        verdict = 'STALE_CELERY'
    else:
        verdict = 'FRESH'

    result: Dict[str, Any] = {
        'staleness_verdict': verdict,
        'head_commit_sha': head_sha,
        'head_commit_timestamp': head_commit_iso,
        'celery_workers_status': celery_worker_rows,
    }
    if daphne_row is not None:
        result['daphne_pid'] = daphne_row['pid']
        result['daphne_pid_age_seconds'] = daphne_row['pid_age_seconds']
        result['daphne_started_before_head_commit'] = (
            daphne_row['started_before_head_commit']
        )
    else:
        result['daphne_pid'] = None
        result['daphne_pid_age_seconds'] = None
        result['daphne_started_before_head_commit'] = None

    if verdict in ('STALE_DAPHNE', 'STALE_CELERY', 'STALE_BOTH'):
        result['staleness_fix'] = (
            'Run `make recycle-all` to bring all local processes to '
            'HEAD-commit-fresh state. `make celery-recycle` alone will '
            'NOT bounce Daphne.'
        )

    return result
