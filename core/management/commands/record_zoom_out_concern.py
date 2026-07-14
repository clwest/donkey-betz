"""S2777 N22 — record a single Rigby SIGN zoom-out concern to the append-only
JSONL evidence ledger at ``logs/zoom_out_classifications.jsonl``.

**This is an evidence substrate, not an enforcement mechanism.** The ledger
surfaces the classification pattern that emerged across S2774 (all
same-PR-actionable) → S2775 (all same-PR-mitigatable) → S2776 (1+2+1).
Whether that pattern eventually earns a codified Playbook amendment is a
separate future decision requiring its own ratification. N22 ships the
substrate; N23 (if proposed) would author the rule.

Design decisions (S2777 joint SIGN, Chris D-verdict yes 2026-07-13):

- **Manual write path** (not auto-hook into ratification envelope creation).
  Manual entry keeps human intent explicit and avoids binding the log schema
  to envelope formatting variability. Auto-hook = future-trigger.

- **JSONL over Django model** (matches S2775 ``session_freshness.jsonl``
  precedent). Zero migration cost, easy backfill, minimally committal
  schema. Promote to model when cross-table joins or multi-writer
  concurrency become load-bearing (future-trigger).

- **7-field schema** locked at v1: classification (enum) · session ·
  arc · concern_text · evidence_ref (optional) · schema_version · backfilled.
  Additive-only field evolution; renames route through schema_version bump.

- **CLI-only read path** for v1. PA tool action = future-trigger once
  Chris explicitly wants the streak report inside SIGN review loops.

Anti-tail-wags-dog guardrails (Rigby S2777 zoom-out fold — schema
ossification risk classified same-PR-mitigatable):

- Report language stays advisory ("pattern evidence" not "threshold
  crossed"). Enforced in ``zoom_out_streak_report``, not here.
- No "threshold=N" semantics baked into storage. Streak counts are
  computed at read time.
- ``schema_version`` field lets future N23 evolve the ontology without
  losing longitudinal history via alias mapping.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from django.core.management.base import BaseCommand, CommandError


ZOOM_OUT_LOG_PATH = Path("logs/zoom_out_classifications.jsonl")
SCHEMA_VERSION = 1

VALID_CLASSIFICATIONS = frozenset(
    {"same_pr_actionable", "same_pr_mitigatable", "future_trigger"}
)


class Command(BaseCommand):
    help = (
        "Record a single Rigby SIGN zoom-out concern as an append-only "
        "row in logs/zoom_out_classifications.jsonl. Evidence substrate "
        "for classification-pattern longitudinal analysis. See file "
        "docstring for design decisions + schema."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--session",
            type=int,
            required=True,
            help="Originating session number (e.g., 2774).",
        )
        parser.add_argument(
            "--arc",
            required=True,
            help="Short arc slug (e.g., ops_urlconf_lambda_cleanup).",
        )
        parser.add_argument(
            "--concern",
            required=True,
            help="Concern text (one sentence).",
        )
        parser.add_argument(
            "--classification",
            required=True,
            choices=sorted(VALID_CLASSIFICATIONS),
            help="Classification enum (validated).",
        )
        parser.add_argument(
            "--evidence-ref",
            default=None,
            help="Optional evidence pointer (PR#, envelope §, handoff path).",
        )
        parser.add_argument(
            "--backfilled",
            action="store_true",
            help="Mark this row as historical reconstruction (not live capture).",
        )
        parser.add_argument(
            "--entered-by",
            default=None,
            help="Who entered this row (defaults to $USER).",
        )
        parser.add_argument(
            "--log-path",
            default=None,
            help="Override log file path (tests only).",
        )

    def handle(self, *args, **options):
        classification = options["classification"]
        # argparse choices already validated; belt-and-braces for direct
        # programmatic invocation.
        if classification not in VALID_CLASSIFICATIONS:
            raise CommandError(
                f"invalid classification {classification!r}; "
                f"must be one of {sorted(VALID_CLASSIFICATIONS)}"
            )

        concern_text = (options["concern"] or "").strip()
        if not concern_text:
            raise CommandError("--concern must be non-empty")

        arc_slug = (options["arc"] or "").strip()
        if not arc_slug:
            raise CommandError("--arc must be non-empty")

        entered_by = (
            options.get("entered_by")
            or os.environ.get("USER")
            or "unknown"
        )

        log_path = Path(options.get("log_path") or ZOOM_OUT_LOG_PATH)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        row: Dict[str, Any] = {
            "ts": datetime.now(tz=timezone.utc).isoformat(),
            "schema_version": SCHEMA_VERSION,
            "session": int(options["session"]),
            "arc": arc_slug,
            "classification": classification,
            "concern_text": concern_text,
            "evidence_ref": options.get("evidence_ref") or None,
            "backfilled": bool(options.get("backfilled")),
            "entered_by": entered_by,
        }

        with log_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

        self.stdout.write(
            f"[zoom_out] recorded S{row['session']} · {row['arc']} · "
            f"{row['classification']}"
            + (" (backfilled)" if row["backfilled"] else "")
        )
