"""
Manual entry point for Rigby's Documentation Manager daily routine.

Session 1252 PR 2 — thin CLI wrapper around
``rigby_documentation_manager_daily`` Celery task. Runs the task
synchronously (no broker) so Chris or Claude can verify the cascade
end-to-end before flipping the PeriodicTask to ``enabled=True``.

Usage::

    # Real run — actually executes the 4-step cascade.
    python manage.py run_docs_manager_daily

    # Preview only — prints the would-execute plan + exits 0.
    python manage.py run_docs_manager_daily --dry-run
"""

from __future__ import annotations

import json
from django.core.management.base import BaseCommand

from core.employees import DOCUMENTATION_MANAGER


class Command(BaseCommand):
    help = "Run Rigby's Documentation Manager daily routine synchronously."

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print what would run and exit without executing.",
        )

    def handle(self, *args, **options) -> None:
        if options.get("dry_run"):
            self._dry_run()
            return

        # Lazy import — keeps Django startup snappy for --dry-run.
        from core.tasks_documentation_manager import (
            rigby_documentation_manager_daily,
        )

        self.stdout.write(
            self.style.NOTICE(
                "Running Documentation Manager mission synchronously…"
            )
        )
        result = rigby_documentation_manager_daily.apply().get()
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("─" * 70))
        self.stdout.write(
            self.style.SUCCESS(
                f"mission_id   : {result.get('mission_id')}"
            )
        )
        self.stdout.write(
            f"status       : {result.get('status')}"
        )
        if result.get("already_ran"):
            self.stdout.write(
                self.style.WARNING(
                    "already_ran=True — a mission already exists for today; "
                    "cascade was not re-executed."
                )
            )
        else:
            self.stdout.write(
                f"verdict      : {result.get('verdict')}"
            )
            self.stdout.write(
                f"wall_time_ms : {result.get('wall_time_ms')}"
            )
        summary = result.get("summary") or {}
        if summary:
            self.stdout.write("")
            self.stdout.write("summary:")
            self.stdout.write(
                json.dumps(summary, indent=2, sort_keys=True, default=str)
            )
        self.stdout.write(self.style.SUCCESS("─" * 70))

    def _dry_run(self) -> None:
        self.stdout.write(
            self.style.WARNING("DRY RUN — no commands executed.")
        )
        self.stdout.write("")
        self.stdout.write("Would execute (in order):")
        for step in DOCUMENTATION_MANAGER.daily_routine:
            self.stdout.write(f"  - {step}")
        self.stdout.write("")
        self.stdout.write(
            "Would emit OpsRunEvent timeline:\n"
            "  run_started\n"
            "  step_1_index_started / step_1_index_passed\n"
            "  step_2_corpus_started / step_2_corpus_passed\n"
            "  step_3_sync_started / step_3_sync_passed\n"
            "  step_4_embed_started / step_4_embed_passed\n"
            "  step_5_drift_observed\n"
            "  verdict_issued:certified\n"
        )
        self.stdout.write(
            "On failure: escalation_emitted + verdict_issued:rejected, "
            "plus the appropriate step_*_skipped markers."
        )
        self.stdout.write("")
        self.stdout.write(
            "Step 4 timeout: warning at "
            f"{DOCUMENTATION_MANAGER.embed_step_timeout.get('warning_seconds', 600)}s, "
            "hard kill at "
            f"{DOCUMENTATION_MANAGER.embed_step_timeout.get('hard_seconds', 1800)}s."
        )
        self.stdout.write(self.style.WARNING("No DB writes performed."))
