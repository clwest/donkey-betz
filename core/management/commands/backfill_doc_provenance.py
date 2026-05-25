"""Selectively add ``originating_session: N`` to YAML frontmatter for
HIGH-confidence docs.

History
-------

- **Session 1145 (Plan B / P3, PR #2213):** initial command. HIGH-only,
  cap 25, **existing frontmatter only** (no NEW blocks), skip
  already-tagged.
- **Session 1147 (Plan B / P3.5, this PR):** extended with opt-in
  ``--add-frontmatter`` flag for backfilling NEW frontmatter blocks
  (Rigby spec: handoffs/specs/canon only, cap 50, minimal YAML).

Default behavior (no new flags) is unchanged from PR #2213: update
existing FM blocks only, cap 25. The P3.5 invocation opts in via
``--add-frontmatter --paths-include docs/handoffs/,docs/specs/,docs/canon/
--limit 50 --with-confidence --with-note "auto-added by backfill_doc_provenance"``.

Rigby's standing rules (unchanged):

1) HIGH confidence only — only docs whose ``originating_session`` was
   derived from a subject-tagged commit.
2) Cap is enforced — do not "session-tag the world." Precision over
   recall; the bulk of attribution lives in ``docs/_provenance.json``.
3) Skip docs that already declare ``session:`` or ``originating_session:``
   in frontmatter — don't touch what someone already declared.
4) Default is write; ``--dry-run`` opts out.

Examples
--------

::

    # Default (P3 behavior — existing-FM only, cap 25)
    python manage.py backfill_doc_provenance --dry-run

    # P3.5 invocation (new FM blocks in scoped paths, cap 50)
    python manage.py backfill_doc_provenance \\
        --add-frontmatter \\
        --paths-include docs/handoffs/,docs/specs/,docs/canon/ \\
        --limit 50 \\
        --with-confidence \\
        --with-note "auto-added by backfill_doc_provenance" \\
        --dry-run
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

# Note: the handoff filename override that catches SESSION_NNNN_*.md
# files attributed by git to a neighboring session now lives upstream
# in ``build_docs_provenance.py`` (Session 1147 P3.5). Trust the index.


class Command(BaseCommand):
    help = "Add `originating_session: N` to HIGH-confidence docs (existing FM by default; opt in to NEW FM via --add-frontmatter)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--provenance", default=str(DEFAULT_PROVENANCE),
            help="Path to docs/_provenance.json (default: docs/_provenance.json)",
        )
        parser.add_argument(
            "--limit", type=int, default=25,
            help="Max docs to update in one pass (Rigby's cap rule). Default 25.",
        )
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Print proposed changes without writing.",
        )
        parser.add_argument(
            "--add-frontmatter", action="store_true",
            help=(
                "Opt-in (Session 1147 P3.5): also write NEW frontmatter "
                "blocks for docs without any. Default off for safety."
            ),
        )
        parser.add_argument(
            "--paths-include", default="",
            help=(
                "Comma-separated path prefixes to restrict to "
                "(e.g. 'docs/handoffs/,docs/specs/,docs/canon/'). "
                "Default: all docs."
            ),
        )
        parser.add_argument(
            "--with-confidence", action="store_true",
            help=(
                "When adding NEW frontmatter, also include "
                "'provenance_confidence: HIGH'."
            ),
        )
        parser.add_argument(
            "--with-note", default="",
            help=(
                "When adding NEW frontmatter, also include "
                "'provenance_note: <text>'. Empty = omit."
            ),
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

        path_prefixes: tuple[str, ...] = tuple(
            p.strip() for p in options["paths_include"].split(",") if p.strip()
        )
        add_fm_enabled: bool = options["add_frontmatter"]

        # Two candidate buckets — kept distinct so the report shows what
        # was an update vs a new-block insertion.
        update_existing: list[tuple[str, int, int]] = []  # (path, session, fm_end_idx)
        add_new: list[tuple[str, int]] = []               # (path, session)

        skipped_no_fm = 0
        skipped_already_tagged = 0
        skipped_not_high = 0
        skipped_missing_file = 0
        skipped_path_filter = 0

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
            if path_prefixes and not any(path.startswith(p) for p in path_prefixes):
                skipped_path_filter += 1
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
            has_opening_fm = bool(lines) and lines[0].strip() == "---"

            if has_opening_fm:
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
                    # FM never closed within 60 lines — treat as no-FM.
                    if add_fm_enabled:
                        add_new.append((path, int(session)))
                    else:
                        skipped_no_fm += 1
                    continue
                update_existing.append((path, int(session), fm_end_idx))
            else:
                # No frontmatter at all.
                if add_fm_enabled:
                    add_new.append((path, int(session)))
                else:
                    skipped_no_fm += 1

        # Sort each bucket by session DESC (most recent first) for capping.
        update_existing.sort(key=lambda c: c[1], reverse=True)
        add_new.sort(key=lambda c: c[1], reverse=True)

        # Apply the global cap across both buckets, updates first then
        # new-FM additions — keeps the safer operation prioritized.
        limit = options["limit"]
        chosen_updates = update_existing[:limit]
        remaining = max(0, limit - len(chosen_updates))
        chosen_adds = add_new[:remaining] if add_fm_enabled else []

        total_chosen = len(chosen_updates) + len(chosen_adds)
        total_eligible = len(update_existing) + len(add_new)

        if total_chosen == 0:
            self.stdout.write(self.style.WARNING(
                "No backfill candidates. Survey: "
                f"skipped_not_high={skipped_not_high}, "
                f"skipped_no_fm={skipped_no_fm}, "
                f"skipped_already_tagged={skipped_already_tagged}, "
                f"skipped_missing_file={skipped_missing_file}, "
                f"skipped_path_filter={skipped_path_filter}, "
                f"add_frontmatter={'on' if add_fm_enabled else 'off'}"
            ))
            return

        self.stdout.write(self.style.SUCCESS(
            f"Backfilling {total_chosen} of {total_eligible} eligible doc(s) "
            f"(cap={limit}) — {len(chosen_updates)} update + {len(chosen_adds)} add-new"
        ))
        if path_prefixes:
            self.stdout.write(f"Path filter: {', '.join(path_prefixes)}")
        self.stdout.write("")

        # 1) Update existing FM blocks (Session 1145 P3 behavior).
        for path, session, fm_end_idx in chosen_updates:
            md_path = Path(path)
            text = md_path.read_text(encoding="utf-8")
            lines = text.splitlines(keepends=True)
            had_trailing_newline = text.endswith("\n")

            insert_line = f"originating_session: {session}\n"
            new_lines = lines[:fm_end_idx] + [insert_line] + lines[fm_end_idx:]
            new_text = "".join(new_lines)
            if had_trailing_newline and not new_text.endswith("\n"):
                new_text += "\n"

            verb = "[DRY-RUN] would update" if options["dry_run"] else "Updated"
            self.stdout.write(f"  {verb} {path} → originating_session: {session}")
            if not options["dry_run"]:
                md_path.write_text(new_text, encoding="utf-8")

        # 2) Add NEW FM blocks (Session 1147 P3.5 behavior).
        for path, session in chosen_adds:
            md_path = Path(path)
            text = md_path.read_text(encoding="utf-8")
            had_trailing_newline = text.endswith("\n")

            fm_lines = ["---", f"originating_session: {session}"]
            if options["with_confidence"]:
                fm_lines.append("provenance_confidence: HIGH")
            if options["with_note"]:
                fm_lines.append(f"provenance_note: {options['with_note']}")
            fm_lines.append("---")
            fm_lines.append("")  # blank line between FM block and existing content
            fm_block = "\n".join(fm_lines) + "\n"

            new_text = fm_block + text
            if had_trailing_newline and not new_text.endswith("\n"):
                new_text += "\n"

            verb = "[DRY-RUN] would ADD-FM" if options["dry_run"] else "Added FM to"
            self.stdout.write(f"  {verb} {path} → originating_session: {session}")
            if not options["dry_run"]:
                md_path.write_text(new_text, encoding="utf-8")

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(
            f"Survey: "
            f"{len(update_existing)} update-eligible + {len(add_new)} add-eligible / "
            f"{skipped_not_high} not-HIGH / "
            f"{skipped_no_fm} no-frontmatter / "
            f"{skipped_already_tagged} already-tagged / "
            f"{skipped_missing_file} missing-file / "
            f"{skipped_path_filter} path-filter-skip"
        ))
