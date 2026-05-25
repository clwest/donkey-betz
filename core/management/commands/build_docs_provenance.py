"""Build docs/_provenance.json — per-doc session-origin index.

Session 1145 Plan B (Rigby spec): extends Plan A (``session_provenance``,
PR #2205) into a regenerable, full-corpus index keyed by file path.

Where Plan A answers "what did Session N produce?", Plan B answers
"which session did this doc originate in?" for every doc in the corpus.
Built once per refresh, consumed by other tools.

Schema per doc
--------------

::

    {
      "originating_session": 1142 | null,
      "confidence": "HIGH" | "MEDIUM" | "LOW" | "UNKNOWN",
      "match_source": "subject" | "body" | "frontmatter" | null,
      "first_commit_sha": "9d2e16a7",
      "first_commit_date": "2026-05-25",
      "first_commit_subject": "docs(session-1142): ...",
      "sessions_touched": [1142, 1143, 1144],
      "commit_count": 3,
      "prs": [2178, 2180, 2181]
    }

Confidence ladder
-----------------

- **HIGH** — first commit's subject carries ``session-NNNN`` tag (the
  repo's preferred convention; introduced via 00-START-NEXT-SESSION.md
  hygiene rule in Session 1144).
- **MEDIUM** — first commit's body mentions ``Session NNNN`` but
  subject doesn't. Could be the session's own work that forgot the
  subject tag, OR a later commit citing this session as context.
- **LOW** — no commit-level session reference, but doc has
  ``session:`` / ``originating_session:`` in YAML frontmatter.
- **UNKNOWN** — no session reference anywhere; predates the
  session-NNNN convention or simply wasn't tagged.

Excludes
--------

Per ``docs/00-START-HERE/DOC_LIFECYCLE.md`` §0:

- ``docs/archive/**`` — historical content, separate provenance regime.
- ``docs/docs-pattern/**`` — context-kit framework master, separate
  domain (NOT this project's content).

Pass ``--include-framework`` / ``--include-archive`` to lift either.

Examples
--------

::

    python manage.py build_docs_provenance
    python manage.py build_docs_provenance --dry-run
    python manage.py build_docs_provenance --include-archive
"""

from __future__ import annotations

import json
import re
import subprocess
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from django.core.management.base import BaseCommand


# Default exclude prefixes — per DOC_LIFECYCLE §0 boundary lock (Session 1144).
DEFAULT_EXCLUDES: tuple[str, ...] = ("docs/archive/", "docs/docs-pattern/")

# Output path — single source for both this command and search_docs.
PROVENANCE_PATH = Path("docs/_provenance.json")

# Session reference extraction.
_SUBJECT_SESSION_RE = re.compile(r"[Ss]ession[- ]?(\d+)\b")
_BODY_SESSION_RE = re.compile(r"[Ss]ession[- ]?(\d+)\b")

# PR ref extraction — matches "(#2206)" tail or "#2206" inline.
_PR_RE = re.compile(r"#(\d{2,5})\b")

# Frontmatter session line — matches "session: 1143" or
# "originating_session: 1143" inside the YAML block at file head.
_FRONTMATTER_SESSION_RE = re.compile(
    r"^(?:session|originating_session)\s*:\s*(\d+)\s*$",
    re.MULTILINE,
)

# Handoff filename convention is unambiguous: ``SESSION_NNNN_*.md``
# (with optional letter suffix like ``SESSION_998B_*``). When git history
# attributes a handoff to a neighboring session number (file committed
# AS PART of a neighboring session's wrap-up commit), the filename is
# the more honest signal. Session 1147 (P3.5) added this filename
# override so the index agrees with the filename for handoffs.
_HANDOFF_FILENAME_RE = re.compile(r"/SESSION_(\d+)[A-Z]?(?:_[A-Z]+)?_")


def _handoff_filename_session(path: str) -> Optional[int]:
    """For ``docs/handoffs/SESSION_NNNN_*.md``, return NNNN; else None."""
    if not path.startswith("docs/handoffs/"):
        return None
    m = _HANDOFF_FILENAME_RE.search(path)
    return int(m.group(1)) if m else None

# ASCII control codes for git log delimiters. \x1f (Unit Separator) and
# \x1e (Record Separator) are non-printable; git accepts them in
# ``--pretty=format`` and they cannot legally appear in commit
# subjects/bodies (git rejects NULs and these adjacent codes).
_FIELD_SEP = "\x1f"
_RECORD_SEP = "\x1e"


class Command(BaseCommand):
    help = "Build/refresh docs/_provenance.json — per-doc session-origin index."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Print JSON to stdout instead of writing docs/_provenance.json",
        )
        parser.add_argument(
            "--include-framework", action="store_true",
            help="Include docs/docs-pattern/ (default: excluded per DOC_LIFECYCLE §0)",
        )
        parser.add_argument(
            "--include-archive", action="store_true",
            help="Include docs/archive/ (default: excluded)",
        )

    def handle(self, *args, **options):
        excludes = list(DEFAULT_EXCLUDES)
        if options["include_framework"]:
            excludes.remove("docs/docs-pattern/")
        if options["include_archive"]:
            excludes.remove("docs/archive/")

        self.stdout.write("Walking git log…")
        commits = parse_git_log()
        self.stdout.write(f"  → {len(commits)} commits parsed")

        self.stdout.write("Building per-file provenance…")
        provenance = build_provenance_index(commits, excludes=excludes)
        self.stdout.write(f"  → {len(provenance)} docs indexed")

        self.stdout.write("Reconciling with frontmatter overrides…")
        fm_added, fm_upgraded = apply_frontmatter_overrides(provenance, excludes=excludes)
        self.stdout.write(
            f"  → {fm_added} doc(s) added from frontmatter, "
            f"{fm_upgraded} doc(s) upgraded LOW→declared via frontmatter"
        )

        # Build meta block.
        head_sha = _run_git("rev-parse", "HEAD").strip()
        confidence_breakdown = {"HIGH": 0, "MEDIUM": 0, "LOW": 0, "UNKNOWN": 0}
        for entry in provenance.values():
            confidence_breakdown[entry["confidence"]] += 1

        output = {
            "_meta": {
                "generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "command": "python manage.py build_docs_provenance",
                "git_head": head_sha[:12],
                "doc_count": len(provenance),
                "commit_count": len(commits),
                "confidence_breakdown": confidence_breakdown,
                "excludes": excludes,
                "schema_version": 1,
            },
            "docs": OrderedDict(
                (path, provenance[path]) for path in sorted(provenance)
            ),
        }

        if options["dry_run"]:
            self.stdout.write(json.dumps(output, indent=2, default=str))
        else:
            PROVENANCE_PATH.parent.mkdir(parents=True, exist_ok=True)
            PROVENANCE_PATH.write_text(
                json.dumps(output, indent=2, default=str), encoding="utf-8"
            )
            self.stdout.write(self.style.SUCCESS(
                f"Wrote {PROVENANCE_PATH} ({len(provenance)} docs, "
                f"HIGH={confidence_breakdown['HIGH']} / "
                f"MEDIUM={confidence_breakdown['MEDIUM']} / "
                f"LOW={confidence_breakdown['LOW']} / "
                f"UNKNOWN={confidence_breakdown['UNKNOWN']})"
            ))


def parse_git_log() -> list[dict]:
    """Walk ``git log --all`` in two passes; merge by SHA.

    Two passes (instead of one) because ``--name-only`` interleaves file
    paths into the ``--pretty=format`` output stream, which made our
    previous single-pass parser confuse body content with file names. With
    two passes the parsing is unambiguous:

    1. **Metadata pass** — sha + date + subject + body, separated by
       ASCII Unit/Record-Separator control codes (\\x1f, \\x1e).
    2. **Files pass** — sha + file-list (one per line, blank-line
       between commits).

    Returns a list of dicts: ``{"sha", "date", "subject", "body",
    "subject_sessions", "body_sessions", "prs", "files"}``.
    """
    # Pass 1: metadata. Each commit becomes a record terminated by RS;
    # fields within a record are separated by US. Both codes are illegal
    # inside commit subjects/bodies, so the parse is unambiguous.
    meta_fmt = _FIELD_SEP.join(["%H", "%cs", "%s", "%b"]) + _RECORD_SEP
    meta_raw = _run_git("log", "--all", f"--pretty=format:{meta_fmt}")

    commits_by_sha: dict[str, dict] = OrderedDict()
    for record in meta_raw.split(_RECORD_SEP):
        record = record.strip("\n")
        if not record:
            continue
        parts = record.split(_FIELD_SEP)
        if len(parts) < 4:
            continue
        sha = parts[0].strip()
        date = parts[1].strip()
        subject = parts[2].strip()
        # body may itself contain US separators in pathological cases;
        # rejoin the tail just in case.
        body = _FIELD_SEP.join(parts[3:]).strip()
        commits_by_sha[sha] = {
            "sha": sha,
            "date": date,
            "subject": subject,
            "body": body,
            "files": [],
        }

    # Pass 2: file paths. SHA-only header lines, then file paths, blank
    # line between commits.
    files_raw = _run_git("log", "--all", "--name-only", "--pretty=format:%H")
    current_sha: Optional[str] = None
    for line in files_raw.split("\n"):
        stripped = line.strip()
        if not stripped:
            current_sha = None
            continue
        if _looks_like_sha(stripped):
            current_sha = stripped
            continue
        if current_sha and current_sha in commits_by_sha:
            commits_by_sha[current_sha]["files"].append(stripped)

    # Annotate each commit with session/PR extractions.
    result: list[dict] = []
    for c in commits_by_sha.values():
        c["subject_sessions"] = sorted(
            {int(m.group(1)) for m in _SUBJECT_SESSION_RE.finditer(c["subject"])}
        )
        c["body_sessions"] = sorted(
            {int(m.group(1)) for m in _BODY_SESSION_RE.finditer(c["body"])}
        )
        c["prs"] = sorted(
            {int(m.group(1)) for m in _PR_RE.finditer(c["subject"])}
        )
        result.append(c)
    return result


def _looks_like_sha(s: str) -> bool:
    """True if ``s`` is a 40-char lowercase hex SHA-1."""
    return len(s) == 40 and all(c in "0123456789abcdef" for c in s)


def build_provenance_index(commits: list[dict], excludes: list[str]) -> dict[str, dict]:
    """Walk commits oldest→newest, build per-file provenance entry.

    Originating session = smallest session number in ``sessions_touched``
    (chronologically earliest session that referenced the file). Confidence
    reflects the match source of the **commit that first attributed the
    file to that originating session** — not whatever the highest-confidence
    later attribution is. A later HIGH-match for session 1143 doesn't
    re-attribute a file that was already MEDIUM-matched to session 128.
    """
    # Sort commits by date ASC (oldest first) so the first commit to
    # mention a given session also wins on attribution ties.
    sorted_commits = sorted(commits, key=lambda c: c["date"])

    provenance: dict[str, dict] = {}

    for c in sorted_commits:
        sha = c["sha"]
        # Combine subject + body session refs for sessions_touched; track
        # per-source so we can pick confidence later.
        for path in c["files"]:
            if not path.startswith("docs/"):
                continue
            if any(path.startswith(ex) for ex in excludes):
                continue
            if not (path.endswith(".md") or path.endswith(".json")
                    or path.endswith(".yml") or path.endswith(".yaml")):
                # Skip non-textual docs files (e.g. images committed under docs/).
                continue

            entry = provenance.setdefault(path, {
                "originating_session": None,
                "confidence": "UNKNOWN",
                "match_source": None,
                "first_commit_sha": None,
                "first_commit_date": None,
                "first_commit_subject": None,
                "sessions_touched": set(),
                "commit_count": 0,
                "prs": set(),
                # Internal scratch: per-session match source, used to set
                # confidence after we know originating_session. Cleaned up
                # before serialization.
                "_session_first_match": {},  # session_num -> "subject"|"body"
            })

            entry["commit_count"] += 1
            entry["prs"].update(c["prs"])

            # Record this commit's session attributions.
            for s in c["subject_sessions"]:
                entry["sessions_touched"].add(s)
                # First commit to mention this session via subject = the
                # subject-attribution we should remember. Don't overwrite
                # if it was already recorded (oldest-first ordering).
                entry["_session_first_match"].setdefault(s, "subject")
            for s in c["body_sessions"]:
                entry["sessions_touched"].add(s)
                # Body match only sets the record if no subject match has
                # been seen yet for this session in this file's history.
                if entry["_session_first_match"].get(s) != "subject":
                    entry["_session_first_match"].setdefault(s, "body")

            if entry["first_commit_sha"] is None:
                entry["first_commit_sha"] = sha[:8]
                entry["first_commit_date"] = c["date"]
                entry["first_commit_subject"] = c["subject"]

    # Resolve originating_session + confidence per file.
    for path, entry in provenance.items():
        sessions = entry["sessions_touched"]
        if sessions:
            origin = min(sessions)
            entry["originating_session"] = origin
            match = entry["_session_first_match"].get(origin, "body")
            entry["confidence"] = "HIGH" if match == "subject" else "MEDIUM"
            entry["match_source"] = match
        # else: confidence stays UNKNOWN, originating_session None.

        # Session 1147 P3.5: handoff filename override. When the file
        # is ``docs/handoffs/SESSION_NNNN_*.md``, the filename is the
        # unambiguous truth — it always wins over git's first-commit
        # attribution. This catches cases like SESSION_998 handoff
        # being attributed to Session 997 (because the wrap-up commit
        # for session 997 created the file). Adds NNNN to
        # sessions_touched if missing, sets as origin, marks the source
        # so search_docs filter consumers know.
        fn_session = _handoff_filename_session(path)
        if fn_session is not None and fn_session != entry["originating_session"]:
            if fn_session not in sessions:
                sessions.add(fn_session)
            entry["originating_session"] = fn_session
            entry["confidence"] = "HIGH"  # filename is authoritative
            entry["match_source"] = "filename"

    # Serialize sets to sorted lists; drop scratch fields.
    for entry in provenance.values():
        entry["sessions_touched"] = sorted(entry["sessions_touched"])
        entry["prs"] = sorted(entry["prs"])
        entry.pop("_session_first_match", None)

    return provenance


def apply_frontmatter_overrides(
    provenance: dict[str, dict], excludes: list[str]
) -> tuple[int, int]:
    """Honor explicit ``session:`` / ``originating_session:`` frontmatter.

    Behavior:
    - If a doc has frontmatter session AND no entry in provenance → add a
      LOW-confidence entry.
    - If a doc has frontmatter session AND entry is UNKNOWN → upgrade to
      LOW with the frontmatter session as the origin.
    - If a doc has frontmatter session AND entry already has HIGH/MEDIUM →
      leave commit-derived value (commits are authoritative).

    Returns ``(added_count, upgraded_count)``.
    """
    added = 0
    upgraded = 0
    docs_dir = Path("docs")
    if not docs_dir.exists():
        return 0, 0

    for md_path in docs_dir.rglob("*.md"):
        path_str = str(md_path)
        if any(path_str.startswith(ex) for ex in excludes):
            continue
        try:
            head = "\n".join(
                line for _, line in zip(
                    range(30), md_path.read_text(encoding="utf-8").splitlines()
                )
            )
        except (OSError, UnicodeDecodeError):
            continue
        m = _FRONTMATTER_SESSION_RE.search(head)
        if not m:
            continue
        fm_session = int(m.group(1))
        entry = provenance.get(path_str)
        if entry is None:
            provenance[path_str] = {
                "originating_session": fm_session,
                "confidence": "LOW",
                "match_source": "frontmatter",
                "first_commit_sha": None,
                "first_commit_date": None,
                "first_commit_subject": None,
                "sessions_touched": [fm_session],
                "commit_count": 0,
                "prs": [],
            }
            added += 1
        elif entry["confidence"] == "UNKNOWN":
            entry["originating_session"] = fm_session
            entry["confidence"] = "LOW"
            entry["match_source"] = "frontmatter"
            if fm_session not in entry["sessions_touched"]:
                entry["sessions_touched"].append(fm_session)
                entry["sessions_touched"] = sorted(entry["sessions_touched"])
            upgraded += 1

    return added, upgraded


def _run_git(*args: str) -> str:
    """Run a git command, return stdout; empty string on failure."""
    try:
        return subprocess.check_output(
            ["git", *args], text=True, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        return ""
