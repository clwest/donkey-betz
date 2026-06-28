"""
rigby_intake_lag_check — Report stuck Rigby Event Intake MissionRuns.

PR 9 of the Rigby Event Intake arc. Read-only. Reports only — no
notifications, no WorkspaceOperation writes, no remediation.

A MissionRun is "stuck" when:
- domain == 'mission'
- run_kind == 'intake'
- status == 'running'
- started_at older than the configured threshold (default 5 minutes)

The intake task itself is usually millisecond-scale (it does one
event load + rule evaluation + a few row writes); a MissionRun in
``status='running'`` for >5 min strongly implies the task crashed,
got stuck, or the worker died.

Usage::

    python manage.py rigby_intake_lag_check
    python manage.py rigby_intake_lag_check --threshold 10
    python manage.py rigby_intake_lag_check --json
"""

from __future__ import annotations

import json
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = (
        "Report Rigby Event Intake MissionRuns stuck in status='running' "
        "beyond the threshold. Read-only — no remediation."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--threshold", type=int, default=5,
            help="Stuck threshold in minutes (default 5).",
        )
        parser.add_argument(
            "--json", action="store_true", dest="output_json",
            help="Emit the report as JSON.",
        )

    def handle(self, *args, **options):
        from core.models_ops_runs import OpsRun

        threshold_min = max(1, int(options.get("threshold") or 5))
        output_json = bool(options.get("output_json"))

        now = timezone.now()
        cutoff = now - timedelta(minutes=threshold_min)

        stuck_qs = OpsRun.objects.filter(
            domain="mission",
            run_kind="intake",
            status="running",
            started_at__lt=cutoff,
        ).order_by("started_at")

        rows = []
        for run in stuck_qs:
            age_seconds = int((now - run.started_at).total_seconds())
            age_minutes = age_seconds / 60.0
            summary = run.summary or {}
            rows.append({
                "mission_run_id": str(run.id),
                "started_at": run.started_at.isoformat(),
                "age_minutes": round(age_minutes, 1),
                "source_event_ref": summary.get("event_ref"),
                "mission_id": str(run.mission_id) if run.mission_id else None,
            })

        report = {
            "generated_at": now.isoformat(),
            "threshold_minutes": threshold_min,
            "stuck_count": len(rows),
            "stuck_runs": rows,
        }

        if output_json:
            self.stdout.write(json.dumps(report, indent=2, default=str))
            return

        self._render_human(report)

    def _render_human(self, report):
        if report["stuck_count"] == 0:
            self.stdout.write(self.style.SUCCESS(
                f"Rigby Intake Lag Check — OK (threshold {report['threshold_minutes']}m)"
            ))
            self.stdout.write(f"  generated: {report['generated_at']}")
            self.stdout.write("  No stuck intake MissionRuns.")
            return

        self.stdout.write(self.style.WARNING(
            f"Rigby Intake Lag Check — {report['stuck_count']} stuck "
            f"(threshold {report['threshold_minutes']}m)"
        ))
        self.stdout.write(f"  generated: {report['generated_at']}")
        self.stdout.write("")
        for row in report["stuck_runs"]:
            mid = row["mission_run_id"][:12]
            age = row["age_minutes"]
            ref = row["source_event_ref"] or "(none)"
            self.stdout.write(
                f"  {mid}.. age={age}m started_at={row['started_at']} "
                f"event_ref={ref}"
            )
