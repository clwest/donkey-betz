"""Worker memory telemetry — RSS sampling + cap pressure + soft downshift signal.

Session 1167 — COO Nervous System Backlog item #5 (SHOULD tier):
``Procfile caps memory per child (--max-memory-per-child=150000/etc.) but we
have NO visibility into how close we get to those caps before the kill
fires. And no automatic concurrency downshift when a worker pool is
consistently pressing the cap.``

This module is the canonical sampler. It returns a structured snapshot:
parent PID + leaf PIDs (children for prefork, parent for threads/solo),
``--max-memory-per-child`` parsed from each worker's cmdline, current
RSS via psutil, ``pct_of_cap``, per-worker status, an overall_status
(worst-of), top offenders, and a downshift recommendation.

## Design notes (Rigby ratified, Session 1167)

- **Pure-function sampler.** The task and the on-demand command both
  call ``build_snapshot()``; no I/O state lives in this module. JSONL
  writes live in the caller (matches the pa_acks_health pattern).
- **PID discovery.** ``app.control.inspect().stats()`` returns per-host
  ``pid`` (parent) and ``pool.processes`` (child PIDs for prefork pool;
  ``None`` for threads/solo). Falls back to ``[pid]`` when pool.processes
  is absent. No environment-variable injection required.
- **Cap parsing.** ``psutil.Process(pid).cmdline()`` includes the
  literal ``--max-memory-per-child=200000`` flag (kilobytes). Workers
  launched without the flag report ``cap_bytes=None`` and ``pct=None``
  (raw RSS still recorded; no false-positive WARN).
- **Soft-only.** No Procfile rewrites, no auto-restart. Output carries
  ``downshift_recommended`` + ``suggested_concurrency_by_worker``
  (heuristic: ``max(current - 1, 1)``; floor=1 universally) +
  ``recommended_actions`` (human strings). Operators act on the signal.
- **Sustain semantics.** Borrowed verbatim from pa_acks_health item C:
  WARN triggers on a single sample at ≥80% of cap; CRIT requires the
  same worker to trip on N=3 consecutive *adjacent* samples (cadence
  5min × adjacency_factor 2 = 600s tolerance). First-run / stale-prior
  cases default to non-sustained — never auto-escalate without evidence.
- **Reduce, never re-classify (Session 1164 rule).** ops_tool
  .memory_pressure reads the latest JSONL line(s) and projects; this
  module is the single source of truth for thresholds.
"""
from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timedelta, timezone as _dt_timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


# Schema + sustain constants. Surface these via the JSONL so future
# calibration / audits don't have to grep the source.
SCHEMA_VERSION = 1
CADENCE_SECONDS = 300  # 5 minutes — beat schedule must match
ADJACENCY_FACTOR = 2   # tolerate one missed snapshot before "not adjacent"
CONSECUTIVE_REQUIRED = 3  # N consecutive samples >=80% → CRIT
PRESSURE_THRESHOLD = 0.80  # WARN if pct_of_cap >= 0.80 on current sample
CONCURRENCY_FLOOR = 1

LOG_DIR = Path("logs") / "worker_memory"
_MT_ZONE = ZoneInfo("America/Denver")
_MAX_MEMORY_FLAG_RE = re.compile(r"--max-memory-per-child(?:=|\s+)(\d+)")


# ──────────────────────────────────────────────────────────────────────
# Cmdline + PID parsing helpers (pure)
# ──────────────────────────────────────────────────────────────────────


def parse_max_memory_per_child_kb(cmdline: List[str]) -> Optional[int]:
    """Extract ``--max-memory-per-child=<N>`` from a process cmdline list.

    Returns the integer kilobyte value, or ``None`` if the flag is
    absent or unparseable. Handles both ``--flag=value`` and
    ``--flag value`` forms.
    """
    if not cmdline:
        return None
    joined = " ".join(str(a) for a in cmdline)
    match = _MAX_MEMORY_FLAG_RE.search(joined)
    if not match:
        return None
    try:
        return int(match.group(1))
    except (ValueError, TypeError):
        return None


def resolve_leaf_pids(parent_pid: int, pool_processes: Optional[List[int]]) -> List[int]:
    """Pick which PIDs to sample for a given worker host.

    ``pool.processes`` (when present and non-empty) holds the prefork
    child PIDs — those are the leaves that get OOM-killed at the cap.
    For threads / solo pools it's ``None`` (or missing); the parent
    process is the only sampleable target.
    """
    if pool_processes:
        return list(pool_processes)
    return [parent_pid]


def derive_pool_kind(pool_processes: Optional[List[int]], parent_pid: int) -> str:
    """Best-effort pool classification from inspect.stats() output.

    Returns one of ``"prefork"``, ``"threads_or_solo"``, ``"unknown"``.
    """
    if pool_processes is None:
        return "threads_or_solo"
    if isinstance(pool_processes, list) and pool_processes and pool_processes != [parent_pid]:
        return "prefork"
    if pool_processes == [parent_pid]:
        return "prefork"  # prefork -c 1 sometimes lists parent as its own child
    return "unknown"


# ──────────────────────────────────────────────────────────────────────
# Worker snapshot assembly
# ──────────────────────────────────────────────────────────────────────


def _build_worker_row(
    hostname: str,
    parent_pid: int,
    pool_processes: Optional[List[int]],
    max_concurrency: Optional[int],
    psutil_module,
) -> Dict[str, Any]:
    """Sample one celery host's leaf PIDs and produce a per-worker row.

    Failures during psutil sampling (process gone, permission denied)
    are captured per-leaf so a single dead child doesn't void the
    whole snapshot.
    """
    leaf_pids = resolve_leaf_pids(parent_pid, pool_processes)
    pool_kind = derive_pool_kind(pool_processes, parent_pid)

    cmdline: List[str] = []
    rss_per_leaf: List[Optional[int]] = []
    sample_errors: List[str] = []

    # Parse cap from parent cmdline — celery launches all children with
    # the same flag set, so parent's cmdline is authoritative.
    try:
        parent_proc = psutil_module.Process(parent_pid)
        cmdline = parent_proc.cmdline()
    except Exception as e:
        sample_errors.append(f"parent_cmdline:{type(e).__name__}")

    for pid in leaf_pids:
        try:
            proc = psutil_module.Process(pid)
            rss_per_leaf.append(int(proc.memory_info().rss))
        except Exception as e:
            rss_per_leaf.append(None)
            sample_errors.append(f"leaf_{pid}:{type(e).__name__}")

    cap_kb = parse_max_memory_per_child_kb(cmdline)
    cap_bytes = cap_kb * 1024 if cap_kb else None

    valid_rss = [r for r in rss_per_leaf if r is not None]
    rss_max = max(valid_rss) if valid_rss else None
    rss_total = sum(valid_rss) if valid_rss else None

    pct_of_cap_max: Optional[float] = None
    if cap_bytes and rss_max is not None:
        pct_of_cap_max = round(rss_max / cap_bytes, 4)

    row: Dict[str, Any] = {
        "hostname": hostname,
        "parent_pid": parent_pid,
        "leaf_pids": leaf_pids,
        "pool_kind": pool_kind,
        "concurrency_current": max_concurrency,
        "concurrency_floor": CONCURRENCY_FLOOR,
        "max_memory_per_child_kb": cap_kb,
        "cap_bytes": cap_bytes,
        "rss_bytes_per_leaf": rss_per_leaf,
        "rss_bytes_max": rss_max,
        "rss_bytes_total": rss_total,
        "pct_of_cap_max": pct_of_cap_max,
        "status": "OK",       # filled by _compute_status
        "reasons": [],        # filled by _compute_status
        "concurrency_suggested": max_concurrency,  # filled by _compute_status
    }
    if sample_errors:
        row["sample_errors"] = sample_errors
    return row


def _collect_inspect_stats(timeout_seconds: float = 2.0) -> Dict[str, Dict[str, Any]]:
    """Run ``celery inspect().stats()``. Returns ``{}`` on timeout/error."""
    try:
        from core.celery import app  # local import — avoid load-time side effects
        stats = app.control.inspect(timeout=timeout_seconds).stats() or {}
        return dict(stats)
    except Exception as e:
        logger.warning(
            "memory_telemetry: inspect().stats() failed: %s: %s",
            type(e).__name__, str(e)[:200],
        )
        return {}


# ──────────────────────────────────────────────────────────────────────
# Sustain semantics (mirror pa_acks_health item C)
# ──────────────────────────────────────────────────────────────────────


def _parse_iso(ts: Any) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None


def _is_previous_adjacent(report: Dict[str, Any], previous_report: Optional[Dict[str, Any]]) -> bool:
    """True iff ``previous_report`` is within the adjacency window."""
    if not previous_report:
        return False
    cur_ts = _parse_iso(report.get("generated_at"))
    prev_ts = _parse_iso(previous_report.get("generated_at"))
    if not (cur_ts and prev_ts):
        return False
    delta = (cur_ts - prev_ts).total_seconds()
    if delta < 0:
        return False
    return delta <= CADENCE_SECONDS * ADJACENCY_FACTOR


def _worker_pct(report: Optional[Dict[str, Any]], hostname: str) -> Optional[float]:
    """Find a worker's pct_of_cap_max in a report. Returns None if absent."""
    if not report:
        return None
    for row in report.get("workers", []) or []:
        if row.get("hostname") == hostname:
            return row.get("pct_of_cap_max")
    return None


def read_recent_snapshots(log_dir: Path = LOG_DIR, count: int = 2) -> List[Dict[str, Any]]:
    """Read up to ``count`` most-recent prior snapshots from JSONL files.

    Returns a list of dicts ordered oldest → newest. Walks files in
    reverse name order (UTC YYYY-MM-DD prefix sorts lexicographically),
    reading from each file's tail until ``count`` are collected. Returns
    ``[]`` if the log directory is missing or no parseable lines exist.
    """
    if not log_dir.exists():
        return []
    files = sorted(log_dir.glob("*.jsonl"))
    collected: List[Dict[str, Any]] = []
    for jsonl in reversed(files):
        try:
            with open(jsonl, "rb") as f:
                lines = f.readlines()
        except OSError:
            continue
        for raw in reversed(lines):
            try:
                collected.append(json.loads(raw.decode("utf-8")))
            except (UnicodeDecodeError, json.JSONDecodeError):
                continue
            if len(collected) >= count:
                break
        if len(collected) >= count:
            break
    collected.reverse()
    return collected


# ──────────────────────────────────────────────────────────────────────
# Status compute (per-worker + overall)
# ──────────────────────────────────────────────────────────────────────


_STATUS_ORDER = {"OK": 0, "WARN": 1, "CRIT": 2}


def _worst_status(*statuses: str) -> str:
    return max(statuses, key=lambda s: _STATUS_ORDER.get(s, 0))


def _compute_status(
    report: Dict[str, Any],
    previous_reports: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Annotate every worker row with status + reasons, set overall_status.

    Also derives top_offenders, downshift_recommended_global,
    suggested_concurrency_by_worker, recommended_actions, and the
    sustain_gating observability block. Mutates and returns ``report``.

    ``previous_reports`` is the list returned by ``read_recent_snapshots``
    (oldest → newest, length 0–2). The current report + last 2 priors
    are used to detect ``CONSECUTIVE_REQUIRED=3`` sustained pressure.
    """
    previous_reports = previous_reports or []
    most_recent_prior = previous_reports[-1] if previous_reports else None
    previous_adjacent = _is_previous_adjacent(report, most_recent_prior)

    gated_triggers: List[str] = []
    escalated_triggers: List[str] = []
    suggested_concurrency: Dict[str, int] = {}
    recommended_actions: List[str] = []

    for row in report.get("workers", []) or []:
        hostname = row.get("hostname", "?")
        pct = row.get("pct_of_cap_max")
        cur_conc = row.get("concurrency_current")

        # No cap → no pct → no status (informational row only).
        if pct is None:
            row["status"] = "OK"
            row["reasons"] = []
            row["concurrency_suggested"] = cur_conc
            continue

        if pct >= PRESSURE_THRESHOLD:
            # Look back to detect N-consecutive sustained pressure.
            chain_len = 1  # current sample itself
            chain_adjacent = True
            check_ts = report
            for prior in reversed(previous_reports):
                # Adjacency is pairwise — check_ts must be adjacent to prior.
                if not _is_previous_adjacent(check_ts, prior):
                    chain_adjacent = False
                    break
                prior_pct = _worker_pct(prior, hostname)
                if prior_pct is None or prior_pct < PRESSURE_THRESHOLD:
                    break
                chain_len += 1
                check_ts = prior

            if chain_len >= CONSECUTIVE_REQUIRED and chain_adjacent:
                row["status"] = "CRIT"
                row["reasons"] = [
                    f"rss_pct>={PRESSURE_THRESHOLD:.2f} sustained "
                    f"{chain_len} consecutive samples"
                ]
                escalated_triggers.append(f"crit_persist_{chain_len}samples:{hostname}")

                # Downshift recommendation only fires on CRIT.
                if isinstance(cur_conc, int) and cur_conc > CONCURRENCY_FLOOR:
                    suggested = max(cur_conc - 1, CONCURRENCY_FLOOR)
                    suggested_concurrency[hostname] = suggested
                    row["concurrency_suggested"] = suggested
                    recommended_actions.append(
                        f"Worker {hostname}: CRIT — recommend concurrency "
                        f"{cur_conc} → {suggested} (or raise --max-memory-per-child / split queues)."
                    )
                else:
                    row["concurrency_suggested"] = cur_conc
                    recommended_actions.append(
                        f"Worker {hostname}: CRIT at concurrency floor "
                        f"({CONCURRENCY_FLOOR}) — investigate leak, raise "
                        f"--max-memory-per-child, or split queues. Cannot downshift further."
                    )
            else:
                row["status"] = "WARN"
                row["reasons"] = [
                    f"rss_pct>={PRESSURE_THRESHOLD:.2f} on current sample "
                    f"(chain_len={chain_len}, need {CONSECUTIVE_REQUIRED})"
                ]
                row["concurrency_suggested"] = cur_conc
                # Record WARN-not-escalated for observability.
                gated_triggers.append(f"warn_not_sustained:{hostname}")
        else:
            row["status"] = "OK"
            row["reasons"] = []
            row["concurrency_suggested"] = cur_conc

    # Top offenders — only entries with computable pct, sorted desc.
    capped_rows = [r for r in (report.get("workers") or []) if r.get("pct_of_cap_max") is not None]
    capped_rows.sort(key=lambda r: r["pct_of_cap_max"], reverse=True)
    top_offenders = [
        {
            "hostname": r["hostname"],
            "pct_of_cap_max": r["pct_of_cap_max"],
            "rss_bytes_max": r.get("rss_bytes_max"),
            "cap_bytes": r.get("cap_bytes"),
            "status": r.get("status"),
        }
        for r in capped_rows[:3]
    ]

    overall_status = "OK"
    for row in report.get("workers", []) or []:
        overall_status = _worst_status(overall_status, row.get("status", "OK"))

    report["overall_status"] = overall_status
    report["top_offenders"] = top_offenders
    report["downshift_recommended_global"] = any(
        r.get("status") == "CRIT" for r in (report.get("workers") or [])
    )
    report["suggested_concurrency_by_worker"] = suggested_concurrency
    report["recommended_actions"] = recommended_actions
    report["sustain_gating"] = {
        "previous_adjacent": previous_adjacent,
        "cadence_seconds": CADENCE_SECONDS,
        "adjacency_window_seconds": CADENCE_SECONDS * ADJACENCY_FACTOR,
        "consecutive_required": CONSECUTIVE_REQUIRED,
        "gated_triggers": gated_triggers,
        "escalated_triggers": escalated_triggers,
    }
    return report


# ──────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────


def build_snapshot(
    *,
    inspect_stats: Optional[Dict[str, Dict[str, Any]]] = None,
    previous_reports: Optional[List[Dict[str, Any]]] = None,
    psutil_module=None,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    """Return a fully-annotated memory-pressure snapshot.

    All inputs are dependency-injected to make tests trivial:

    - ``inspect_stats``: pre-collected ``app.control.inspect().stats()``
      dict. If None, fetched live (subject to celery broker availability).
    - ``previous_reports``: list of prior reports oldest → newest. If
      None, read from the JSONL log directory.
    - ``psutil_module``: dependency-injected psutil for testing. If
      None, imports the real psutil.
    - ``now``: timestamp override for testing. If None, ``datetime.now(utc)``.

    Output schema is stable at SCHEMA_VERSION=1.
    """
    if psutil_module is None:
        import psutil as psutil_module  # type: ignore
    if inspect_stats is None:
        inspect_stats = _collect_inspect_stats()
    if previous_reports is None:
        previous_reports = read_recent_snapshots(LOG_DIR, count=CONSECUTIVE_REQUIRED - 1)
    if now is None:
        now = datetime.now(_dt_timezone.utc)

    workers_out: List[Dict[str, Any]] = []
    for hostname, info in inspect_stats.items():
        parent_pid = info.get("pid")
        if not isinstance(parent_pid, int):
            continue
        pool = info.get("pool") or {}
        pool_processes = pool.get("processes")
        # Some celery versions report a single int or weird shapes; defend.
        if pool_processes is not None and not isinstance(pool_processes, list):
            try:
                pool_processes = list(pool_processes)
            except TypeError:
                pool_processes = None
        max_conc = pool.get("max-concurrency")
        row = _build_worker_row(
            hostname=hostname,
            parent_pid=parent_pid,
            pool_processes=pool_processes,
            max_concurrency=max_conc,
            psutil_module=psutil_module,
        )
        workers_out.append(row)

    workers_out.sort(key=lambda r: r.get("hostname") or "")

    report: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now.isoformat(),
        "generated_at_mt": now.astimezone(_MT_ZONE).strftime("%Y-%m-%d %H:%M:%S %Z"),
        "cadence_seconds": CADENCE_SECONDS,
        "workers": workers_out,
        "worker_count": len(workers_out),
    }

    _compute_status(report, previous_reports=previous_reports)
    return report


def jsonl_path_for(now: Optional[datetime] = None, log_dir: Path = LOG_DIR) -> Path:
    """Resolve the UTC-dated JSONL path the task writes to."""
    if now is None:
        now = datetime.now(_dt_timezone.utc)
    elif now.tzinfo is None:
        now = now.replace(tzinfo=_dt_timezone.utc)
    else:
        now = now.astimezone(_dt_timezone.utc)
    return log_dir / f"{now.strftime('%Y-%m-%d')}.jsonl"
