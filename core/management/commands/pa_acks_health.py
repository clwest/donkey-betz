"""
PA acks-health snapshot for the Session 1159 acks_late=False watch window.

Built Session 1160 (PR #2255 watch). Read-only, on-demand. Consolidates the
observation surface that Rigby's cockpit_tool + ops_tool + Redis health
expose piecewise into a single output suitable for direct inspection or
piping to other tools.

Session 1161 (A) added two ack-behavior proxies — `oldest_queued` and
`inflight_estimate` (received-minus-finished delta) — so queue-depth
alarms don't flap on a single in-flight task. These are advisory-only;
OK/WARN/CRIT thresholds are unchanged until observation supports tuning
(item 3d in `00-START-NEXT-SESSION.md`).

Session 1161 (B) added a `per_worker` rollup that unions inspect-side
workers with DB-side workers active in the window, plus a
`worker_last_event_at` heartbeat proxy on each hang-signature sample.
The rollup localizes WARN/CRIT signals to a specific worker process;
the heartbeat distinguishes "worker stuck" (no events since the hung
task started) from "task wedged but worker alive."

Session 1162 (cosmetic): each per_worker row carries an `is_pa_relevant`
boolean. A worker is PA-relevant if it had any DB event for the focused
task in window OR its hostname starts with the queue prefix (the
`--hostname={queue}@%h` convention the Makefile sets up). The human
summary groups PA-relevant workers in full detail and collapses idle
workers (other queues) to a single line; the JSON output keeps every
worker for debug visibility.

Session 1162 (cosmetic, second pass): each report carries both UTC
(`generated_at`, ISO 8601) AND Mountain time (`generated_at_mt`, human
"YYYY-MM-DD HH:MM:SS MDT" form) so operators reading JSONL during the
acks watch can correlate snapshots against wall-clock work hours
without an in-head TZ conversion. UTC stays canonical for sorting and
machine parsing.

Usage:
    python manage.py pa_acks_health
    python manage.py pa_acks_health --hours 24
    python manage.py pa_acks_health --queue pa --slow-threshold 60
    python manage.py pa_acks_health --hang-max-age-hours 24
    python manage.py pa_acks_health --json

Hang signature interpretation:

A CeleryTaskEvent row in STARTED state with no finished_at means the task
fired task_prerun but never reached task_postrun. Causes include:

  1. Broker-ack-drop ⇒ task stuck in unacked until visibility_timeout.
     This is the failure mode the Session 1159 acks_late=False fix targets.
  2. Worker process died mid-task (SIGKILL during restart, macOS SIGSEGV).
     Independent of the ack pattern.
  3. Task body hung indefinitely (network call without timeout, etc.).

The command surfaces ALL three patterns. To isolate the acks-drop pattern
specifically, cross-reference with Redis broker state (out of scope for
a read-only Django-side tool). The `--hang-max-age-hours` flag bounds the
check so historical reaped-but-not-cleaned rows don't dominate the signal.
Default 24h focuses on "recent enough to be a current issue."

Exit code is always 0 (read-only observation; advisory flags are part of
the summary output, not a failure signal).
"""

import json
import os
from datetime import datetime, timedelta, timezone as _dt_timezone
from zoneinfo import ZoneInfo
from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.utils import timezone

# Session 1162 cosmetic: operator-readable Mountain time alongside the
# canonical UTC timestamp. Matches `TIME_ZONE = 'America/Denver'` in
# core/settings.py + the beat schedule's "America/Denver" wall clock.
_MT_ZONE = ZoneInfo("America/Denver")


class Command(BaseCommand):
    help = (
        "Snapshot health of the PA acks_late=False watch window. "
        "Reports queue depth, worker activity, recent process_pa_chat_task "
        "completions, and hang-signature candidates."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--hours",
            type=int,
            default=6,
            help="Lookback window in hours for task event stats (default: 6)",
        )
        parser.add_argument(
            "--queue",
            type=str,
            default="pa",
            help="Queue name to inspect (default: pa)",
        )
        parser.add_argument(
            "--task",
            type=str,
            default="core.tasks.process_pa_chat_task",
            help=(
                "Task name to focus the completion stats on "
                "(default: core.tasks.process_pa_chat_task)"
            ),
        )
        parser.add_argument(
            "--slow-threshold",
            type=int,
            default=60,
            help=(
                "Tasks slower than this (seconds) get flagged in the slow-tasks "
                "list (default: 60). Also used as the 'hang signature' age cutoff."
            ),
        )
        parser.add_argument(
            "--hang-max-age-hours",
            type=int,
            default=24,
            help=(
                "Upper bound (hours) on hang-signature row age — older rows "
                "are excluded because they're typically restart casualties, "
                "not current issues (default: 24). Overridden by "
                "--since-pidfile when that file exists."
            ),
        )
        parser.add_argument(
            "--since-pidfile",
            type=str,
            default=".celery-pa.pid",
            help=(
                "Path to a pid file whose mtime is used as the hang-signature "
                "lower bound (default: .celery-pa.pid). If the file exists, "
                "only hangs started after the current worker restart are "
                "flagged. Pass an empty string to disable."
            ),
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Emit machine-readable JSON instead of the human-readable summary.",
        )

    def handle(self, *args, **options):
        report = self.build_report(
            hours=options["hours"],
            queue=options["queue"],
            task_name=options["task"],
            slow_threshold=options["slow_threshold"],
            hang_max_age_hours=options["hang_max_age_hours"],
            since_pidfile=options["since_pidfile"],
        )

        if options["json"]:
            self.stdout.write(json.dumps(report, indent=2, default=str))
        else:
            self._print_human_summary(report)

    def build_report(
        self,
        *,
        hours=6,
        queue="pa",
        task_name="core.tasks.process_pa_chat_task",
        slow_threshold=60,
        hang_max_age_hours=24,
        since_pidfile=".celery-pa.pid",
    ):
        """
        Session 1161 cadence wrapper: assembles + returns the report dict.

        Public entry point for callers that need the structured report
        without going through CLI option parsing or stdout capture (e.g.,
        the `capture_pa_acks_health_snapshot` Celery beat task that runs
        every 30 minutes during the acks_late=False watch window). All
        args have CLI-matching defaults so a no-arg call is equivalent
        to running `python manage.py pa_acks_health` with no flags.

        Read-only — same semantics as `handle()`. Advisory flags + status
        are populated last so they reflect everything else in the report.
        """
        pidfile_cutoff = self._pidfile_cutoff(since_pidfile)

        task_stats = self._task_stats(task_name, hours)
        workers_snapshot = self._worker_snapshot()
        now_utc = timezone.now()
        report = {
            "generated_at": now_utc.isoformat(),
            "generated_at_mt": now_utc.astimezone(_MT_ZONE).strftime(
                "%Y-%m-%d %H:%M:%S %Z"
            ),
            "window_hours": hours,
            "queue": queue,
            "task_name": task_name,
            "slow_threshold_seconds": slow_threshold,
            "hang_max_age_hours": hang_max_age_hours,
            "since_pidfile": since_pidfile or None,
            "since_pidfile_cutoff": pidfile_cutoff.isoformat() if pidfile_cutoff else None,
            "queue_depth": self._queue_depth(queue),
            "workers": workers_snapshot,
            "per_worker": self._per_worker_rollup(
                task_name, hours, slow_threshold, workers_snapshot, queue
            ),
            "task_stats": task_stats,
            "oldest_queued": self._oldest_queued(task_name),
            "inflight_estimate": self._inflight_estimate(task_stats),
            "slow_tasks": self._slow_tasks(task_name, hours, slow_threshold),
            "hang_signature": self._hang_signature(
                task_name, slow_threshold, hang_max_age_hours, pidfile_cutoff
            ),
            "advisory_flags": [],
            "status": "OK",
        }

        self._flag_advisory(report)
        self._compute_status(report)
        return report

    # ---- Data gatherers (read-only) ----

    def _queue_depth(self, queue):
        try:
            import redis
        except ImportError:
            return {"error": "redis package not importable"}
        try:
            broker = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
            client = redis.Redis.from_url(broker)
            depth = client.llen(queue)
            return {"queue": queue, "depth": depth, "broker": broker}
        except Exception as exc:
            return {"queue": queue, "error": str(exc)}

    def _worker_snapshot(self):
        try:
            from core.celery import app as celery_app
        except Exception as exc:
            return {"error": f"celery app import failed: {exc}"}

        try:
            inspect = celery_app.control.inspect(timeout=3)
            stats = inspect.stats() or {}
            active = inspect.active() or {}
            reserved = inspect.reserved() or {}
        except Exception as exc:
            return {"error": f"inspect failed: {exc}"}

        workers = []
        by_name = {}
        for worker_name, _worker_stats in (stats or {}).items():
            row = {
                "name": worker_name,
                "active_count": len(active.get(worker_name, []) or []),
                "reserved_count": len(reserved.get(worker_name, []) or []),
            }
            workers.append(row)
            by_name[worker_name] = row
        return {
            "count": len(workers),
            "workers": workers,
            "by_name": by_name,
            "total_active": sum(w["active_count"] for w in workers),
            "total_reserved": sum(w["reserved_count"] for w in workers),
        }

    def _per_worker_rollup(self, task_name, hours, slow_threshold, workers_snapshot, queue):
        """
        Session 1161 (B): per-worker attribution. Unions inspect-side
        workers (currently-online) with DB-side workers (active in the
        window). Each row carries enough to localize a WARN/CRIT to a
        specific worker process.

        Fields per worker:
          - online: bool — present in inspect stats
          - active_count, reserved_count: from inspect (None when offline)
          - started_still: STARTED-not-finished rows for this worker
          - slow_completed: SUCCESS|FAILURE with duration >= slow_threshold
          - oldest_started_age_seconds: max age of started-but-not-finished
          - last_event_at: most recent started_at OR finished_at — heartbeat
            proxy. None means the worker has touched no task this window.
          - is_pa_relevant: bool — added Session 1162. True if this worker
            either has any DB event for the focused task in window OR its
            hostname starts with `{queue}@` (the celery `--hostname=pa@%h`
            convention used in the Makefile). Lets downstream tools focus
            diff/alert noise on workers that actually serve this queue;
            irrelevant workers stay in the rollup for debug visibility.

        Returns a list ordered by name. Empty list is a valid result
        (e.g., no workers and no DB events in the window).
        """
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
            from django.db.models import Max
        except Exception as exc:
            return {"error": f"CeleryTaskEvent import failed: {exc}"}

        inspect_by_name = (workers_snapshot or {}).get("by_name") or {}
        if "error" in (workers_snapshot or {}):
            inspect_by_name = {}

        since = timezone.now() - timedelta(hours=hours)
        db_workers = set(
            CeleryTaskEvent.objects.filter(
                task_name=task_name, started_at__gte=since
            )
            .exclude(worker="")
            .values_list("worker", flat=True)
            .distinct()
        )
        all_workers = sorted(set(inspect_by_name.keys()) | db_workers)

        # Session 1162 (cosmetic): PA-relevance heuristic uses both DB
        # activity AND the celery `--hostname={queue}@%h` naming convention
        # the Makefile sets up. A worker is PA-relevant if it either had
        # an event for this task in window OR its hostname starts with
        # the queue prefix.
        hostname_prefix = f"{queue}@" if queue else None

        rows = []
        now = timezone.now()
        for worker in all_workers:
            inspect_row = inspect_by_name.get(worker)
            qs = CeleryTaskEvent.objects.filter(
                task_name=task_name, started_at__gte=since, worker=worker
            )
            started_still = qs.filter(
                status="STARTED", finished_at__isnull=True
            ).count()
            slow_completed = qs.filter(
                status__in=("SUCCESS", "FAILURE"),
                duration_seconds__gte=slow_threshold,
            ).count()
            oldest_started = (
                qs.filter(status="STARTED", finished_at__isnull=True)
                .order_by("started_at")
                .first()
            )
            oldest_age = (
                (now - oldest_started.started_at).total_seconds()
                if oldest_started
                else None
            )
            last_event_agg = qs.aggregate(
                last_started=Max("started_at"),
                last_finished=Max("finished_at"),
            )
            event_candidates = [
                v
                for v in (
                    last_event_agg["last_started"],
                    last_event_agg["last_finished"],
                )
                if v
            ]
            last_event_at = max(event_candidates).isoformat() if event_candidates else None

            is_pa_relevant = (
                worker in db_workers
                or (hostname_prefix is not None and worker.startswith(hostname_prefix))
            )

            rows.append(
                {
                    "name": worker,
                    "online": worker in inspect_by_name,
                    "active_count": inspect_row["active_count"] if inspect_row else None,
                    "reserved_count": inspect_row["reserved_count"] if inspect_row else None,
                    "started_still": started_still,
                    "slow_completed": slow_completed,
                    "oldest_started_age_seconds": oldest_age,
                    "last_event_at": last_event_at,
                    "is_pa_relevant": is_pa_relevant,
                }
            )
        return rows

    def _task_stats(self, task_name, hours):
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
        except Exception as exc:
            return {"error": f"CeleryTaskEvent import failed: {exc}"}

        since = timezone.now() - timedelta(hours=hours)
        qs = CeleryTaskEvent.objects.filter(
            task_name=task_name, started_at__gte=since
        )
        counts = qs.aggregate(
            total=Count("id"),
            success=Count("id", filter=Q(status="SUCCESS")),
            failure=Count("id", filter=Q(status="FAILURE")),
            started=Count("id", filter=Q(status="STARTED")),
            revoked=Count("id", filter=Q(status="REVOKED")),
            queued=Count("id", filter=Q(status="QUEUED")),
        )
        return {
            "since": since.isoformat(),
            "total": counts["total"],
            "success": counts["success"],
            "failure": counts["failure"],
            "started_still": counts["started"],
            "revoked": counts["revoked"],
            "queued": counts["queued"],
        }

    def _oldest_queued(self, task_name):
        """
        Session 1161 (A): age of the oldest CeleryTaskEvent row with
        status=QUEUED for this task_name. A growing oldest-age means
        the broker is accepting tasks faster than workers are picking
        them up — independent of total depth. Returns None when no
        queued rows exist.

        Not bounded by the window because a queued row that's been
        sitting for hours is exactly the signal we want to surface,
        even if it predates the lookback.
        """
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
        except Exception as exc:
            return {"error": f"CeleryTaskEvent import failed: {exc}"}

        row = (
            CeleryTaskEvent.objects.filter(task_name=task_name, status="QUEUED")
            .order_by("started_at")
            .first()
        )
        if row is None:
            return {"present": False, "age_seconds": None, "started_at": None}
        return {
            "present": True,
            "task_id": row.task_id,
            "age_seconds": (timezone.now() - row.started_at).total_seconds(),
            "started_at": row.started_at.isoformat(),
        }

    def _inflight_estimate(self, task_stats):
        """
        Session 1161 (A): received-minus-finished delta over the window.
        Implemented as `total − (success + failure + revoked)` from the
        already-aggregated counts so we don't re-query. Equivalent to
        `started_still + queued` over the window plus any row that hit a
        status outside the five known states. Used to make queue-depth
        alarms less flappy: a single STARTED task that ran 90s shouldn't
        trip the same alarm as a real backlog.
        """
        if "error" in task_stats:
            return {"error": task_stats["error"]}
        total = task_stats.get("total", 0) or 0
        finished = (
            (task_stats.get("success", 0) or 0)
            + (task_stats.get("failure", 0) or 0)
            + (task_stats.get("revoked", 0) or 0)
        )
        return {
            "total": total,
            "finished": finished,
            "delta": total - finished,
        }

    def _slow_tasks(self, task_name, hours, slow_threshold):
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
        except Exception:
            return []

        since = timezone.now() - timedelta(hours=hours)
        qs = (
            CeleryTaskEvent.objects.filter(
                task_name=task_name,
                started_at__gte=since,
                duration_seconds__gte=slow_threshold,
            )
            .order_by("-duration_seconds")[:10]
        )
        return [
            {
                "task_id": row.task_id,
                "status": row.status,
                "started_at": row.started_at.isoformat(),
                "finished_at": row.finished_at.isoformat() if row.finished_at else None,
                "duration_seconds": row.duration_seconds,
                "worker": row.worker,
            }
            for row in qs
        ]

    def _pidfile_cutoff(self, pidfile_path):
        """
        Return the pidfile's mtime as a timezone-aware datetime, or None if the
        path is empty / missing. Used as the lower bound for hang-signature so
        restart casualties from prior worker runs don't dominate the signal.
        """
        if not pidfile_path:
            return None
        try:
            if not os.path.exists(pidfile_path):
                return None
            mtime = os.path.getmtime(pidfile_path)
            return datetime.fromtimestamp(mtime, tz=_dt_timezone.utc)
        except Exception:
            return None

    def _hang_signature(self, task_name, slow_threshold, max_age_hours, pidfile_cutoff):
        """
        Tasks in STARTED state with no finished_at and an age between
        slow_threshold (lower bound) and either max_age_hours or pidfile mtime
        (upper bound). Catches any task that didn't reach postrun —
        broker-ack-drop, worker SIGKILL, and genuine task-body hangs all
        produce this row shape. See module docstring for interpretation.

        When pidfile_cutoff is provided, it overrides max_age_hours as the
        lower bound (i.e., we only consider hangs that the currently-running
        worker process could have caused).
        """
        try:
            from core.models_celery_telemetry import CeleryTaskEvent
            from django.db.models import Max
        except Exception:
            return {"count": 0, "samples": [], "note": "import failed"}

        now = timezone.now()
        upper_cutoff = now - timedelta(seconds=slow_threshold)
        if pidfile_cutoff is not None:
            lower_cutoff = pidfile_cutoff
        else:
            lower_cutoff = now - timedelta(hours=max_age_hours)
        qs = (
            CeleryTaskEvent.objects.filter(
                task_name=task_name,
                status="STARTED",
                finished_at__isnull=True,
                started_at__lt=upper_cutoff,
                started_at__gte=lower_cutoff,
            )
            .order_by("started_at")[:20]
        )
        # Session 1161 (B): for each hung row, look up the most recent event
        # from the same worker (across all task_names) as a heartbeat proxy.
        # If worker_last_event_at == started_at, the worker has done nothing
        # since the hung task started — strong signal that the worker process
        # itself is stuck. If it's later, the task is wedged but the worker
        # is alive. Single Max() per distinct worker.
        sample_workers = sorted({row.worker for row in qs if row.worker})
        worker_last_seen = {}
        for worker in sample_workers:
            agg = CeleryTaskEvent.objects.filter(worker=worker).aggregate(
                last_started=Max("started_at"),
                last_finished=Max("finished_at"),
            )
            candidates = [
                v for v in (agg["last_started"], agg["last_finished"]) if v
            ]
            worker_last_seen[worker] = max(candidates) if candidates else None

        samples = []
        for row in qs:
            last_seen = worker_last_seen.get(row.worker)
            samples.append(
                {
                    "task_id": row.task_id,
                    "started_at": row.started_at.isoformat(),
                    "age_seconds": (timezone.now() - row.started_at).total_seconds(),
                    "worker": row.worker,
                    "worker_last_event_at": last_seen.isoformat() if last_seen else None,
                }
            )
        return {"count": len(samples), "samples": samples}

    # ---- Advisory flag logic ----

    def _flag_advisory(self, report):
        flags = report["advisory_flags"]

        depth = report.get("queue_depth", {}).get("depth")
        if isinstance(depth, int) and depth > 10:
            flags.append(
                f"queue '{report['queue']}' depth is {depth} — backlog forming"
            )

        stats = report.get("task_stats", {})
        if stats.get("failure", 0) > 0:
            flags.append(
                f"{stats['failure']} FAILURE event(s) for {report['task_name']} "
                f"in the last {report['window_hours']}h"
            )

        hang_count = report.get("hang_signature", {}).get("count", 0)
        if hang_count > 0:
            flags.append(
                f"{hang_count} hang-signature task(s) (STARTED, no finished_at, "
                f"age > {report['slow_threshold_seconds']}s) — investigate"
            )

        workers = report.get("workers", {})
        if isinstance(workers, dict) and workers.get("count", 0) == 0:
            flags.append("no celery workers responded to inspect — worker outage?")

        # Session 1161 (A): advisory-only — flag a stale-queued row that's
        # been sitting longer than slow_threshold. Threshold tuning (whether
        # this should also escalate OK→WARN) is deferred to item 3d after
        # observation; this surfaces the signal without changing existing
        # OK/WARN/CRIT semantics.
        oldest = report.get("oldest_queued") or {}
        if oldest.get("present") and (oldest.get("age_seconds") or 0) >= report["slow_threshold_seconds"]:
            flags.append(
                f"oldest queued row is {oldest['age_seconds']:.0f}s old "
                f"(> slow_threshold={report['slow_threshold_seconds']}s) — workers may be lagging"
            )

    # ---- Status thresholds (Rigby's session-1160 watch-window proposal) ----
    #
    # Important: slow_tasks (already-completed) does NOT trip status. A task
    # that ran 80s and SUCCEEDED is informational, not a warning. The hang
    # signature (STARTED-not-finished) captures the "currently running too
    # long" case, and the oldest-hang-age is what determines CRIT.

    # WARN thresholds — any of these conditions trips WARN.
    _WARN_HANG_COUNT = 1            # any current hang is suspicious
    _WARN_FAILURE_COUNT = 1         # any failure in the window
    _WARN_QUEUE_DEPTH = 1           # any queued message at snapshot time
    _WARN_NO_WORKERS = True         # zero workers = WARN at minimum

    # CRIT thresholds — any of these escalates from WARN to CRIT.
    _CRIT_HANG_COUNT = 3            # multiple concurrent hangs
    _CRIT_FAILURE_COUNT = 3         # failure spike
    _CRIT_HANG_AGE_SEC = 180        # any currently-running hang > 3x threshold
    _CRIT_QUEUE_DEPTH = 20          # serious backlog
    _CRIT_NO_WORKERS = True         # zero workers = CRIT if sustained

    def _compute_status(self, report):
        """
        Roll the snapshot into a single OK / WARN / CRIT verdict so downstream
        tooling can act on the result without parsing the advisory_flags list.
        Per Rigby's Session 1160 feedback on PR #2266.
        """
        depth = (report.get("queue_depth") or {}).get("depth")
        depth = depth if isinstance(depth, int) else 0
        stats = report.get("task_stats") or {}
        failures = stats.get("failure", 0)
        hang = report.get("hang_signature") or {}
        hang_count = hang.get("count", 0)
        hang_samples = hang.get("samples", []) or []
        oldest_hang_age = max(
            (s.get("age_seconds", 0.0) or 0.0) for s in hang_samples
        ) if hang_samples else 0.0
        worker_count = (report.get("workers") or {}).get("count", 0) or 0

        # CRIT conditions first — short-circuit on any hit.
        if (
            hang_count >= self._CRIT_HANG_COUNT
            or failures >= self._CRIT_FAILURE_COUNT
            or oldest_hang_age >= self._CRIT_HANG_AGE_SEC
            or depth >= self._CRIT_QUEUE_DEPTH
            or (worker_count == 0 and self._CRIT_NO_WORKERS)
        ):
            report["status"] = "CRIT"
            return

        # WARN conditions.
        if (
            hang_count >= self._WARN_HANG_COUNT
            or failures >= self._WARN_FAILURE_COUNT
            or depth >= self._WARN_QUEUE_DEPTH
            or (worker_count == 0 and self._WARN_NO_WORKERS)
        ):
            report["status"] = "WARN"
            return

        report["status"] = "OK"

    # ---- Human-readable summary ----

    def _print_human_summary(self, report):
        write = self.stdout.write
        write(f"PA acks-health snapshot  [status: {report['status']}]")
        write(f"  generated_at:        {report['generated_at']}")
        if report.get("generated_at_mt"):
            write(f"  generated_at (MT):   {report['generated_at_mt']}")
        write(f"  window:              last {report['window_hours']}h")
        write(f"  queue:               {report['queue']}")
        write(f"  task_name:           {report['task_name']}")
        write(f"  slow_threshold_sec:  {report['slow_threshold_seconds']}")
        if report.get("since_pidfile_cutoff"):
            write(
                f"  hang cutoff:         {report['since_pidfile_cutoff']} "
                f"(from {report['since_pidfile']} mtime)"
            )
        else:
            write(
                f"  hang cutoff:         max-age-hours={report['hang_max_age_hours']} "
                f"(pidfile not found)"
            )
        write("")

        depth_block = report["queue_depth"]
        if "error" in depth_block:
            write(f"queue depth:  error — {depth_block['error']}")
        else:
            write(f"queue depth:  {depth_block['depth']}  (queue={depth_block['queue']})")

        workers = report["workers"]
        if "error" in workers:
            write(f"workers:      error — {workers['error']}")
        else:
            write(
                f"workers:      {workers['count']} online, "
                f"{workers['total_active']} active, "
                f"{workers['total_reserved']} reserved"
            )

        # Session 1161 (B): per-worker rollup
        # Session 1162 cosmetic: group PA-relevant workers in full detail,
        # collapse PA-irrelevant ones to a single line so the readout
        # focuses on workers that actually serve this queue.
        per_worker = report.get("per_worker") or []
        if isinstance(per_worker, dict) and "error" in per_worker:
            write(f"per-worker:   error — {per_worker['error']}")
        elif per_worker:
            relevant = [r for r in per_worker if r.get("is_pa_relevant")]
            idle = [r for r in per_worker if not r.get("is_pa_relevant")]
            write(
                f"per-worker:   {len(relevant)} pa-relevant, "
                f"{len(idle)} idle (other queues)"
            )
            for row in relevant:
                online_marker = "online" if row["online"] else "OFFLINE"
                oldest = row.get("oldest_started_age_seconds")
                oldest_str = f"oldest_started={oldest:.0f}s" if oldest else "oldest_started=–"
                last_seen = row.get("last_event_at") or "—"
                write(
                    f"  - {row['name']}  [{online_marker}]  "
                    f"started_still={row['started_still']} "
                    f"slow_completed={row['slow_completed']} "
                    f"{oldest_str} "
                    f"last_event_at={last_seen}"
                )
            if idle:
                idle_names = ", ".join(r["name"] for r in idle)
                write(f"  + {len(idle)} idle: {idle_names}")
        else:
            write("per-worker:   no workers or events in window")

        stats = report["task_stats"]
        if "error" in stats:
            write(f"task stats:   error — {stats['error']}")
        else:
            write(
                "task stats:   "
                f"total={stats['total']} "
                f"success={stats['success']} "
                f"failure={stats['failure']} "
                f"started_still={stats['started_still']} "
                f"revoked={stats['revoked']}"
            )

        inflight = report.get("inflight_estimate") or {}
        if "error" in inflight:
            write(f"inflight:     error — {inflight['error']}")
        else:
            write(
                "inflight:     "
                f"recv−finished={inflight.get('delta', 0)} "
                f"(total={inflight.get('total', 0)} finished={inflight.get('finished', 0)})"
            )

        oldest_q = report.get("oldest_queued") or {}
        if "error" in oldest_q:
            write(f"oldest queued: error — {oldest_q['error']}")
        elif oldest_q.get("present"):
            write(
                f"oldest queued: age={oldest_q['age_seconds']:.0f}s "
                f"started_at={oldest_q['started_at']}"
            )
        else:
            write("oldest queued: none — queue clear")

        slow = report["slow_tasks"]
        if slow:
            write(f"slow tasks (>{report['slow_threshold_seconds']}s):  {len(slow)} in window")
            for row in slow[:5]:
                write(
                    f"  - {row['task_id'][:8]} {row['status']:8s} "
                    f"{row['duration_seconds']:.1f}s  {row['started_at']}"
                )
        else:
            write(f"slow tasks (>{report['slow_threshold_seconds']}s):  0 in window")

        hang = report["hang_signature"]
        if hang["count"] > 0:
            write(f"hang signature:  {hang['count']} task(s) — INVESTIGATE")
            for row in hang["samples"][:5]:
                last_seen = row.get("worker_last_event_at") or "—"
                write(
                    f"  - {row['task_id'][:8]} age={row['age_seconds']:.0f}s "
                    f"started_at={row['started_at']} worker={row['worker']} "
                    f"worker_last_event_at={last_seen}"
                )
        else:
            write("hang signature:  0 — clean")

        flags = report["advisory_flags"]
        write("")
        if flags:
            write(f"advisory flags:  {len(flags)}")
            for flag in flags:
                write(f"  ! {flag}")
        else:
            write("advisory flags:  none — baseline healthy")
