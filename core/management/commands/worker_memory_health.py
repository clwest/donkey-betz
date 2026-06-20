"""On-demand worker memory pressure snapshot.

Session 1167 — COO Nervous System Backlog item #5 (SHOULD tier).
Companion to ``pa_acks_health``: prints the current per-worker RSS,
``--max-memory-per-child`` cap, ``pct_of_cap``, status (OK/WARN/CRIT),
and any active downshift recommendation. Read-only.

Sampling logic lives in ``core/services/memory_telemetry.py`` so the
beat-scheduled ``capture_worker_memory_snapshot`` task and this CLI
share the exact same code path.
"""
from __future__ import annotations

import json

from django.core.management.base import BaseCommand

from core.services.memory_telemetry import build_snapshot


class Command(BaseCommand):
    help = (
        "Snapshot worker memory pressure (per-host RSS vs "
        "--max-memory-per-child cap). Surfaces sustained-pressure CRIT "
        "and a soft downshift recommendation. Read-only."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--json",
            action="store_true",
            help="Emit machine-readable JSON instead of the human summary.",
        )

    def handle(self, *args, **options):
        report = build_snapshot()
        if options["json"]:
            self.stdout.write(json.dumps(report, indent=2, default=str))
            return
        self._print_human_summary(report)

    def _print_human_summary(self, report):
        overall = report.get("overall_status", "OK")
        marker = {"OK": "✓", "WARN": "!", "CRIT": "✗"}.get(overall, "?")
        self.stdout.write(f"\n[{marker}] Worker memory pressure — overall: {overall}")
        self.stdout.write(f"    generated_at_mt: {report.get('generated_at_mt')}")
        self.stdout.write(
            f"    cadence_seconds: {report.get('cadence_seconds')}  "
            f"workers_sampled: {report.get('worker_count')}"
        )

        sg = report.get("sustain_gating") or {}
        self.stdout.write(
            "    sustain: previous_adjacent={pa} "
            "consecutive_required={cr} "
            "escalated_triggers={et}".format(
                pa=sg.get("previous_adjacent"),
                cr=sg.get("consecutive_required"),
                et=sg.get("escalated_triggers") or [],
            )
        )

        workers = report.get("workers") or []
        if not workers:
            self.stdout.write("\n  (no celery hosts reported by inspect.stats — broker down?)")
            return

        self.stdout.write("\n  Per-worker:")
        header = (
            "    {:<32} {:<6} {:>8} {:>8} {:>7} {:<5} {:>4}/{:<4} reasons"
            .format("hostname", "pool", "rss_mb", "cap_mb", "pct", "stat", "cur", "sug")
        )
        self.stdout.write(header)
        for row in workers:
            rss_mb = (row.get("rss_bytes_max") or 0) / (1024 * 1024)
            cap_mb = (row.get("cap_bytes") or 0) / (1024 * 1024) if row.get("cap_bytes") else 0.0
            pct = row.get("pct_of_cap_max")
            pct_str = f"{pct:.2f}" if isinstance(pct, (int, float)) else "—"
            reasons = "; ".join(row.get("reasons") or []) or ""
            self.stdout.write(
                "    {:<32} {:<6} {:>8.1f} {:>8.1f} {:>7} {:<5} {:>4}/{:<4} {}".format(
                    str(row.get("hostname"))[:32],
                    str(row.get("pool_kind", "?"))[:6],
                    rss_mb,
                    cap_mb,
                    pct_str,
                    str(row.get("status", "OK"))[:5],
                    row.get("concurrency_current"),
                    row.get("concurrency_suggested"),
                    reasons[:60],
                )
            )

        offenders = report.get("top_offenders") or []
        if offenders:
            self.stdout.write("\n  Top offenders (by pct_of_cap_max):")
            for o in offenders:
                pct = o.get("pct_of_cap_max")
                pct_str = f"{pct:.2f}" if isinstance(pct, (int, float)) else "—"
                self.stdout.write(
                    f"    - {o.get('hostname')}  pct={pct_str}  status={o.get('status')}"
                )

        actions = report.get("recommended_actions") or []
        if actions:
            self.stdout.write("\n  Recommended actions:")
            for a in actions:
                self.stdout.write(f"    • {a}")

        if report.get("downshift_recommended_global"):
            self.stdout.write(
                "\n  ⚠ DOWNSHIFT RECOMMENDED — see suggested_concurrency_by_worker."
            )
