"""
PA acks-health snapshot for the Session 1159 acks_late=False watch window.

Built Session 1160 (PR #2255 watch). Read-only, on-demand. Consolidates the
observation surface that Rigby's cockpit_tool + ops_tool + Redis health
expose piecewise into a single output suitable for direct inspection or
piping to other tools.

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
from django.core.management.base import BaseCommand
from django.db.models import Count, Q
from django.utils import timezone


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
        hours = options["hours"]
        queue = options["queue"]
        task_name = options["task"]
        slow_threshold = options["slow_threshold"]
        hang_max_age_hours = options["hang_max_age_hours"]
        since_pidfile = options["since_pidfile"]
        as_json = options["json"]

        pidfile_cutoff = self._pidfile_cutoff(since_pidfile)

        report = {
            "generated_at": timezone.now().isoformat(),
            "window_hours": hours,
            "queue": queue,
            "task_name": task_name,
            "slow_threshold_seconds": slow_threshold,
            "hang_max_age_hours": hang_max_age_hours,
            "since_pidfile": since_pidfile or None,
            "since_pidfile_cutoff": pidfile_cutoff.isoformat() if pidfile_cutoff else None,
            "queue_depth": self._queue_depth(queue),
            "workers": self._worker_snapshot(),
            "task_stats": self._task_stats(task_name, hours),
            "slow_tasks": self._slow_tasks(task_name, hours, slow_threshold),
            "hang_signature": self._hang_signature(
                task_name, slow_threshold, hang_max_age_hours, pidfile_cutoff
            ),
            "advisory_flags": [],
        }

        # Populate advisory flags last so we can reason about everything we
        # gathered. Read-only — never returns a non-zero exit code; flags are
        # signals for the human reader / downstream tooling.
        self._flag_advisory(report)

        if as_json:
            self.stdout.write(json.dumps(report, indent=2, default=str))
        else:
            self._print_human_summary(report)

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
        for worker_name, _worker_stats in (stats or {}).items():
            workers.append(
                {
                    "name": worker_name,
                    "active_count": len(active.get(worker_name, []) or []),
                    "reserved_count": len(reserved.get(worker_name, []) or []),
                }
            )
        return {
            "count": len(workers),
            "workers": workers,
            "total_active": sum(w["active_count"] for w in workers),
            "total_reserved": sum(w["reserved_count"] for w in workers),
        }

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
        samples = [
            {
                "task_id": row.task_id,
                "started_at": row.started_at.isoformat(),
                "age_seconds": (timezone.now() - row.started_at).total_seconds(),
                "worker": row.worker,
            }
            for row in qs
        ]
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

    # ---- Human-readable summary ----

    def _print_human_summary(self, report):
        write = self.stdout.write
        write("PA acks-health snapshot")
        write(f"  generated_at:        {report['generated_at']}")
        write(f"  window:              last {report['window_hours']}h")
        write(f"  queue:               {report['queue']}")
        write(f"  task_name:           {report['task_name']}")
        write(f"  slow_threshold_sec:  {report['slow_threshold_seconds']}")
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
                write(
                    f"  - {row['task_id'][:8]} age={row['age_seconds']:.0f}s "
                    f"started_at={row['started_at']} worker={row['worker']}"
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
