"""Arc I-0100 P3 Stop Condition #1 — auto-disable threshold check
management command.

Runs ``check_thresholds()`` against live ORM state; if breach detected,
calls ``trip()`` to flip the shared kill sentinel and emit audit + log
evidence.

Under LOCAL-only regime this is the sole consumer of the auto-disable
threshold constants. When a production deployment exists, a follow-on
arc would wire a Celery beat task to invoke the same monitor module
periodically.

Usage::

    python manage.py delegation_auto_disable_check              # check + trip on breach
    python manage.py delegation_auto_disable_check --dry-run    # check only, do not trip
    python manage.py delegation_auto_disable_check --clear      # clear kill sentinel (rollback)
    python manage.py delegation_auto_disable_check --verbose    # pretty-print decision
"""
from __future__ import annotations

import json

from django.core.management.base import BaseCommand

from core.services.delegation_auto_disable_monitor import (
    check_thresholds,
    clear_trip,
    is_tripped,
    trip,
)


class Command(BaseCommand):
    help = (
        "Arc I-0100 P3 Stop Condition #1 — check auto-disable thresholds "
        "and trip the shared kill sentinel on breach."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Check thresholds but do not trip on breach.",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear the kill sentinel and exit (rollback drill).",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Pretty-print the decision payload.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            was_tripped = is_tripped()
            clear_trip()
            self.stdout.write(
                f"[RIGBY_DELEGATION_KILL_SWITCH_CLEARED] was_tripped={was_tripped}"
            )
            return

        already_tripped = is_tripped()
        decision = check_thresholds()

        payload = decision.to_dict()
        payload["already_tripped"] = already_tripped

        if options["verbose"]:
            self.stdout.write(json.dumps(payload, indent=2, default=str))
        else:
            self.stdout.write(json.dumps(payload, default=str))

        if decision.breached:
            if options["dry_run"]:
                self.stdout.write(
                    f"[DRY_RUN] breach detected reasons={decision.reasons}; not tripping"
                )
            else:
                trip(decision)
                self.stdout.write(
                    f"[RIGBY_DELEGATION_AUTO_DISABLED] tripped reasons={decision.reasons}"
                )
        else:
            self.stdout.write("[DELEGATION_AUTO_DISABLE_CHECK_PASS] no thresholds breached")
