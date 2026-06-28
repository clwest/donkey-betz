"""
rigby_intake_status — Local observation harness for Rigby Event Intake.

PR 9 of the Rigby Event Intake arc. Read-only. No writes. No side
effects.

Reports on recent intake MissionRuns:
- domain='mission', run_kind='intake'
- source event_ref
- decision (from MissionRun.summary['decision'])
- mission_impact
- status (running / passed / failed)
- timeline event count
- whether a RigbyWorkItem exists for the source event_ref
- aggregates (last 24h / 7d) + decision breakdown + stuck-running count

Usage::

    python manage.py rigby_intake_status
    python manage.py rigby_intake_status --limit 20
    python manage.py rigby_intake_status --json
"""

from __future__ import annotations

import json
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = (
        "Report on recent Rigby Event Intake MissionRuns. Read-only. "
        "PR 9 local observation harness."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit", type=int, default=10,
            help="Latest N intake MissionRuns to list (default 10).",
        )
        parser.add_argument(
            "--json", action="store_true", dest="output_json",
            help="Emit the report as JSON.",
        )

    def handle(self, *args, **options):
        from core.models_ops_runs import OpsRun, OpsRunEvent
        from core.models_rigby_work_items import RigbyWorkItem

        limit = max(1, int(options.get("limit") or 10))
        output_json = bool(options.get("output_json"))

        now = timezone.now()
        cutoff_24h = now - timedelta(hours=24)
        cutoff_7d = now - timedelta(days=7)

        intake_qs = OpsRun.objects.filter(
            domain="mission", run_kind="intake",
        )

        report = {
            "generated_at": now.isoformat(),
            "flags": {
                "RIGBY_EVENT_INTAKE_ENABLED": bool(
                    getattr(settings, "RIGBY_EVENT_INTAKE_ENABLED", False)
                ),
                "RIGBY_INTERNAL_WORK_QUEUE_ENABLED": bool(
                    getattr(settings, "RIGBY_INTERNAL_WORK_QUEUE_ENABLED", False)
                ),
                "RIGBY_WORK_QUEUE_REVIEW_ENABLED": bool(
                    getattr(settings, "RIGBY_WORK_QUEUE_REVIEW_ENABLED", False)
                ),
                "RIGBY_DELEGATION_ENABLED": bool(
                    getattr(settings, "RIGBY_DELEGATION_ENABLED", False)
                ),
            },
            "totals": {
                "all_time": intake_qs.count(),
                "last_24h": intake_qs.filter(started_at__gte=cutoff_24h).count(),
                "last_7d": intake_qs.filter(started_at__gte=cutoff_7d).count(),
                "running_count": intake_qs.filter(status="running").count(),
            },
            "decision_breakdown_7d": _decision_breakdown(intake_qs.filter(
                started_at__gte=cutoff_7d,
            )),
            "recent": [],
        }

        # Pull recent rows + per-row event counts in a single sweep.
        for run in intake_qs.order_by("-started_at")[:limit]:
            summary = run.summary or {}
            event_ref = summary.get("event_ref")
            decision = summary.get("decision")
            mission_impact = summary.get("mission_impact")

            event_count = OpsRunEvent.objects.filter(run=run).count()

            # Look up RigbyWorkItem only if we have an event_ref to key on.
            has_work_item = False
            if event_ref:
                has_work_item = RigbyWorkItem.objects.filter(
                    source_event_ref=event_ref,
                ).exists()

            report["recent"].append({
                "mission_run_id": str(run.id),
                "started_at": run.started_at.isoformat() if run.started_at else None,
                "finished_at": (
                    run.finished_at.isoformat() if run.finished_at else None
                ),
                "status": run.status,
                "source_event_ref": event_ref,
                "decision": decision,
                "mission_impact": mission_impact,
                "timeline_event_count": event_count,
                "has_work_item": has_work_item,
                "mission_id": str(run.mission_id) if run.mission_id else None,
            })

        if output_json:
            self.stdout.write(json.dumps(report, indent=2, default=str))
            return

        # Human-readable output.
        self._render_human(report)

    def _render_human(self, report):
        self.stdout.write(self.style.SUCCESS("Rigby Intake Status"))
        self.stdout.write(f"  generated: {report['generated_at']}")
        self.stdout.write("")
        self.stdout.write("Flags:")
        for flag, val in report["flags"].items():
            marker = "ON " if val else "off"
            self.stdout.write(f"  [{marker}]  {flag}")
        self.stdout.write("")
        t = report["totals"]
        self.stdout.write("Totals:")
        self.stdout.write(f"  all-time intake runs : {t['all_time']}")
        self.stdout.write(f"  last 24h             : {t['last_24h']}")
        self.stdout.write(f"  last 7d              : {t['last_7d']}")
        running_marker = (
            self.style.WARNING(str(t["running_count"]))
            if t["running_count"] > 0 else "0"
        )
        self.stdout.write(f"  currently running    : {running_marker}")
        self.stdout.write("")
        self.stdout.write("Decision breakdown (7d):")
        breakdown = report["decision_breakdown_7d"]
        if not breakdown:
            self.stdout.write("  (no decisions in window)")
        else:
            for decision, count in sorted(breakdown.items()):
                self.stdout.write(f"  {decision:<28}  {count}")
        self.stdout.write("")
        self.stdout.write(f"Recent intake runs (latest {len(report['recent'])}):")
        if not report["recent"]:
            self.stdout.write("  (no rows)")
        for row in report["recent"]:
            mid = row["mission_run_id"][:12]
            decision = row["decision"] or "-"
            impact = row["mission_impact"] or "-"
            wi = "✓" if row["has_work_item"] else "·"
            ec = row["timeline_event_count"]
            self.stdout.write(
                f"  {mid}.. status={row['status']:<8} "
                f"decision={decision:<10} impact={impact:<8} "
                f"events={ec:<3} work_item={wi} "
                f"event_ref={row['source_event_ref'] or '(none)'}"
            )


def _decision_breakdown(qs) -> dict[str, int]:
    """Tally MissionRun.summary['decision'] values across a queryset.

    Uses an in-Python tally because the decision lives inside a JSON
    field — Postgres can do this with a GROUP BY on the JSON path but
    that's overkill for the volumes we expect in v0.
    """
    counts: dict[str, int] = {}
    for run in qs.only("summary"):
        summary = run.summary or {}
        decision = summary.get("decision")
        if decision is None:
            decision = "(no decision recorded)"
        counts[decision] = counts.get(decision, 0) + 1
    return counts
