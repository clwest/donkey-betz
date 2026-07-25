"""Django management command: scan agent capability drift.

CLI wrapper around ``core.services.agent_capability_drift.AgentCapabilityDriftScanner``.
Ratified at S2953. Rigby SIGN-refined single-codepath design — the Django test
wrapper and PA-callable audit tool both call the same scanner service.

Usage
-----
    python manage.py scan_agent_capability_drift              # human-readable text report
    python manage.py scan_agent_capability_drift --json       # machine-readable JSON
    python manage.py scan_agent_capability_drift --fail-on-drift  # nonzero exit on any active finding

CI usage (once we're ready to enforce): add ``--fail-on-drift`` to a workflow
step. Until then, run without the flag and treat warnings as advisory.
"""

from __future__ import annotations

import json
import sys
from typing import Any

from django.core.management.base import BaseCommand

from core.services.agent_capability_drift import (
    DEFAULT_RECENT_WINDOW_DAYS,
    AgentCapabilityDriftScanner,
)


class Command(BaseCommand):
    help = "Scan for agent capability drift (AGENT_MAP ↔ enum ↔ mapping ↔ Agent row ↔ recent execution)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--json",
            action="store_true",
            help="Emit the full report as JSON on stdout (default is human-readable text).",
        )
        parser.add_argument(
            "--fail-on-drift",
            action="store_true",
            help="Exit with code 1 if any non-suppressed finding exists (for CI enforcement).",
        )
        parser.add_argument(
            "--recent-window-days",
            type=int,
            default=DEFAULT_RECENT_WINDOW_DAYS,
            help=f"Days back to check recent-execution invariant (default: {DEFAULT_RECENT_WINDOW_DAYS}).",
        )

    def handle(self, *args, **options):
        scanner = AgentCapabilityDriftScanner(
            recent_window_days=options["recent_window_days"],
        )
        report = scanner.run_all()

        if options["json"]:
            self.stdout.write(json.dumps(report.to_dict(), indent=2, sort_keys=True))
        else:
            self._render_text(report)

        if options["fail_on_drift"] and report.has_active_failures:
            sys.exit(1)
        # `warn`-only findings do not fail even with --fail-on-drift; only `fail` severity does.
        # The scanner emits warnings by default; graduate specific invariants to `fail`
        # severity when Tier-1 agents are defined.

    def _render_text(self, report) -> None:
        d: Any = report.to_dict()
        totals = d["totals"]
        self.stdout.write("=" * 72)
        self.stdout.write(f"Agent Capability Drift Report — {d['scanned_at']}")
        self.stdout.write("=" * 72)
        self.stdout.write(
            f"AGENT_MAP entries: {totals['agent_map_entries']}   "
            f"Agent DB rows: {totals['agent_db_rows']}   "
            f"run_agent enum: {totals['run_agent_enum_entries']}   "
            f"Exceptions loaded: {totals['exceptions_loaded']}"
        )
        self.stdout.write(
            f"Active findings: {totals['active_findings']}   "
            f"Suppressed by allowlist: {totals['suppressed_findings']}"
        )
        self.stdout.write("")

        if not d["findings"] and not d["suppressed_findings"]:
            self.stdout.write(self.style.SUCCESS("✔ No drift detected. All invariants pass."))
            return

        if d["findings"]:
            self.stdout.write(self.style.WARNING("Active findings"))
            self.stdout.write("-" * 72)
            self._group_and_print(d["findings"])
            self.stdout.write("")

        if d["suppressed_findings"]:
            self.stdout.write(self.style.NOTICE(
                f"Suppressed by allowlist ({len(d['suppressed_findings'])})"
            ))
            self.stdout.write("-" * 72)
            self._group_and_print(d["suppressed_findings"], show_reason=True)

    def _group_and_print(self, findings, show_reason: bool = False) -> None:
        by_invariant: dict = {}
        for f in findings:
            by_invariant.setdefault(f["invariant"], []).append(f)
        for invariant, items in sorted(by_invariant.items()):
            self.stdout.write(f"\n[{invariant}] ({len(items)})")
            for f in items:
                line = f"  • {f['agent_class']}: {f['message']}"
                if show_reason and f.get("exception_reason"):
                    line += f"  (allowlist: {f['exception_reason']})"
                self.stdout.write(line)
