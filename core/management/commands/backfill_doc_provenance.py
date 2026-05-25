"""Selectively add ``originating_session: N`` to YAML frontmatter for
HIGH-confidence docs (Session 1145 Plan B / P3).

Rigby's rules for this command (Session 1145 conversation pa-4b4784ecd989):

1) HIGH confidence only — only docs whose ``originating_session`` was
   derived from a subject-tagged commit (the repo's preferred
   ``session-NNNN`` convention).
2) Cap (default 25) — do not "session-tag the world." This is a
   precision-over-recall move; the bulk of attribution lives in
   ``docs/_provenance.json``, not in every doc's frontmatter.
3) Existing frontmatter only — do **not** create new YAML frontmatter
   blocks in docs that don't have one. Adding metadata blocks to
   narrative-only markdown is invasive and ambiguous in tone.
4) Skip docs that already carry ``session:`` or ``originating_session:``
   in their frontmatter — don't touch what someone already declared.
5) Dry-run by default would be nice but we want easy CI; default is
   write, ``--dry-run`` opts out.

Output: list of docs updated + their assigned ``originating_session``,
plus a tally. Use the output verbatim in the PR description so reviewers
can see exactly what was touched.

Examples
--------

::

    python manage.py backfill_doc_provenance --dry-run
    python manage.py backfill_doc_provenance --limit 25
    python manage.py backfill_doc_provenance --provenance docs/_provenance.json
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from django.core.management.base import BaseCommand


DEFAULT_PROVENANCE = Path("docs/_provenance.json")

# Match lines like "session: 1143" or "originating_session: 1143" inside
# the YAML frontmatter. Anchored at line start (with optional whitespace)
# so we don't match keys like ``session_drafted`` or ``unique_session``.
_FM_SESSION_KEY_RE = re.compile(r"^\s*(?:session|originating_session)\s*:")


class Command(BaseCommand):
    help = "Add `originating_session: N` to HIGH-confidence docs that have YAML frontmatter."

    def add_arguments(self, parser):
        parser.add_argument(
            "--provenance", default=str(DEFAULT_PROVENANCE),
            help="Path to docs/_provenance.json (default: docs/_provenance.json)",
        )
        parser.add_argument(
            "--limit", type=int, default=25,
            help="Max docs to update in one pass (Rigby's cap rule).",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Print the proposed changes without writing.",
        )

    def handle(self, *args, **options):
        prov_path = Path(options["provenance"])
        if not prov_path.exists():
            self.stderr.write(self.style.ERROR(
                f"Provenance file not found at {prov_path}. "
                "Run `python manage.py build_docs_provenance` first."
            ))
            return

        data = json.loads(prov_path.read_text(encoding="utf-8"))
        docs = data.get("docs", {})

        candidates: list[tuple[str, int, int]] = []  # (path, session, fm_end_lineno)
        skipped_no_fm = 0
        skipped_already_tagged = 0
        skipped_not_high = 0
        skipped_missing_file = 0

        for path, meta in docs.items():
            if meta.get("confidence") != "HIGH":
                skipped_not_high += 1
                continue
            session = meta.get("originating_session")
            if session is None:
                skipped_not_high += 1
                continue
            if not path.endswith(".md"):
                continue
            md_path = Path(path)
            if not md_path.exists():
                skipped_missing_file += 1
                continue
            try:
                text = md_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                skipped_missing_file += 1
                continue
            lines = text.splitlines()
            if not lines or lines[0].strip() != "---":
                skipped_no_fm += 1
                continue

            fm_end_idx = None
            already_tagged = False
            for i in range(1, min(60, len(lines))):
                if lines[i].strip() == "---":
                    fm_end_idx = i
                    break
                if _FM_SESSION_KEY_RE.match(lines[i]):
                    already_tagged = True
                    break
            if already_tagged:
                skipped_already_tagged += 1
                continue
            if fm_end_idx is None:
                # Frontmatter never closed within first 60 lines — bail.
                skipped_no_fm += 1
                continue

            candidates.append((path, int(session), fm_end_idx))

        # Sort by originating session DESC (most recent first) so we
        # backfill the highest-signal docs when capped.
        candidates.sort(key=lambda c: c[1], reverse=True)
        chosen = candidates[: options["limit"]]

        if not chosen:
            self.stdout.write(self.style.WARNING(
                "No backfill candidates. Survey: "
                f"skipped_not_high={skipped_not_high}, "
                f"skipped_no_fm={skipped_no_fm}, "
                f"skipped_already_tagged={skipped_already_tagged}, "
                f"skipped_missing_file={skipped_missing_file}"
            ))
            return

        self.stdout.write(self.style.SUCCESS(
            f"Backfilling {len(chosen)} of {len(candidates)} eligible doc(s) "
            f"(cap={options['limit']})"
        ))
        self.stdout.write("")

        for path, session, fm_end_idx in chosen:
            md_path = Path(path)
            text = md_path.read_text(encoding="utf-8")
            lines = text.splitlines(keepends=True)
            had_trailing_newline = text.endswith("\n")

            # Insert the new key just before the closing "---" line.
            insert_line = f"originating_session: {session}\n"
            # Preserve original line endings of surrounding lines.
            new_lines = lines[:fm_end_idx] + [insert_line] + lines[fm_end_idx:]
            new_text = "".join(new_lines)
            if had_trailing_newline and not new_text.endswith("\n"):
                new_text += "\n"

            verb = "[DRY-RUN] would update" if options["dry_run"] else "Updated"
            self.stdout.write(f"  {verb} {path} → originating_session: {session}")
            if not options["dry_run"]:
                md_path.write_text(new_text, encoding="utf-8")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Survey: {len(candidates)} eligible / "
            f"{skipped_not_high} not-HIGH / "
            f"{skipped_no_fm} no-frontmatter / "
            f"{skipped_already_tagged} already-tagged / "
            f"{skipped_missing_file} missing-file"
        ))
