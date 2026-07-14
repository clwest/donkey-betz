"""S2777 N22 — read-side companion to ``record_zoom_out_concern``.

Prints a longitudinal report of Rigby SIGN zoom-out concerns grouped by
classification. Report language is **advisory** by explicit design: rows
are "pattern evidence for review," not "threshold crossed → codify." The
distinction matters — see the sibling command docstring for the
tail-wags-dog risk fold that shaped this stance.

Read paths:

* ``--last N`` (default 20) — most recent N rows across all sessions.
* ``--classification <enum>`` — filter to one classification.
* ``--session <n>`` — filter to one session.
* ``--json`` — emit rows + counts as JSON for downstream consumption
  (still evidence, still advisory).

No PA tool action is exposed for v1. Promotion to a PA-tool read
surface is a future-trigger gated on Chris explicitly wanting the
streak report inside SIGN review loops.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Dict, Iterable, List

from django.core.management.base import BaseCommand


ZOOM_OUT_LOG_PATH = Path("logs/zoom_out_classifications.jsonl")

ADVISORY_HEADER = (
    "Rigby SIGN zoom-out concern ledger — pattern evidence for review. "
    "Rows are longitudinal signal, not automatic escalation triggers. "
    "Any Playbook codification decision requires its own ratification."
)


class Command(BaseCommand):
    help = (
        "Print recent Rigby SIGN zoom-out concerns from the JSONL ledger "
        "grouped by classification. Read-only. See file docstring for the "
        "advisory-only stance and read paths."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--last",
            type=int,
            default=20,
            help="Show the last N rows (default 20).",
        )
        parser.add_argument(
            "--classification",
            default=None,
            help="Filter to one classification enum.",
        )
        parser.add_argument(
            "--session",
            type=int,
            default=None,
            help="Filter to one session number.",
        )
        parser.add_argument(
            "--as-json",
            action="store_true",
            help="Emit rows + counts as JSON on stdout.",
        )
        parser.add_argument(
            "--log-path",
            default=None,
            help="Override log file path (tests only).",
        )

    def handle(self, *args, **options):
        log_path = Path(options.get("log_path") or ZOOM_OUT_LOG_PATH)
        rows = list(_read_rows(log_path))

        if options.get("classification"):
            rows = [r for r in rows if r.get("classification") == options["classification"]]
        if options.get("session") is not None:
            rows = [r for r in rows if r.get("session") == options["session"]]

        counts: Counter[str] = Counter(
            r.get("classification", "unknown") for r in rows
        )

        last_n = int(options.get("last") or 20)
        recent = rows[-last_n:]

        if options.get("as_json"):
            payload: Dict[str, Any] = {
                "advisory": ADVISORY_HEADER,
                "total_rows": len(rows),
                "counts_by_classification": dict(counts),
                "rows": recent,
            }
            self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
            return

        self._print_report(rows, recent, counts, last_n)

    # ─────────────────────────── helpers ───────────────────────────── #

    def _print_report(
        self,
        all_rows: List[Dict[str, Any]],
        recent: List[Dict[str, Any]],
        counts: Counter[str],
        last_n: int,
    ) -> None:
        self.stdout.write(ADVISORY_HEADER)
        self.stdout.write("")
        self.stdout.write(f"Total rows: {len(all_rows)}")
        self.stdout.write("Counts by classification (pattern evidence, not gates):")
        for classification in sorted(counts):
            self.stdout.write(f"  {classification:26s}  {counts[classification]}")

        if not recent:
            self.stdout.write("")
            self.stdout.write("No rows match filter.")
            return

        self.stdout.write("")
        self.stdout.write(f"Last {min(last_n, len(all_rows))} rows:")
        for row in recent:
            session = row.get("session", "?")
            arc = row.get("arc", "?")
            classification = row.get("classification", "?")
            concern = (row.get("concern_text") or "").replace("\n", " ")
            if len(concern) > 90:
                concern = concern[:87] + "..."
            backfilled_marker = " [backfilled]" if row.get("backfilled") else ""
            evidence = row.get("evidence_ref") or ""
            evidence_marker = f" · {evidence}" if evidence else ""
            self.stdout.write(
                f"  S{session}  {arc:36s}  {classification:22s}  "
                f"{concern}{backfilled_marker}{evidence_marker}"
            )


def _read_rows(log_path: Path) -> Iterable[Dict[str, Any]]:
    if not log_path.exists():
        return []
    out: List[Dict[str, Any]] = []
    with log_path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                # skip corrupt lines silently — advisory ledger, not audit log
                continue
    return out
