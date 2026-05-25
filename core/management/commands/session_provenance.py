"""Generate a provenance cluster for a given session.

Session 1144 (Rigby spec, "Plan A"): given session N, surface every doc
that was created or modified in that session by reading git history.
Helps answer "what did Session 815 produce?" without manually scanning the
handoff doc + cross-referencing the rest of /docs/.

This is the read-only scaffolding for the future Plan B (a persistent
``docs/_provenance.json`` index plugged into ``search_docs`` as a filter).
This command makes no doc changes; it only emits a report.

Data sources (in priority order)
--------------------------------

1. **Git log grep** — commits whose subject or body matches
   ``[Ss]ession[- ]?<N>\\b``. The repo's convention for at least the last
   ~50 sessions has been ``docs(session-NNNN): ...`` / ``feat(session-NNNN):
   ...`` commit subjects, which makes this a strong signal.
2. **Frontmatter override** — if a doc has ``session: N`` or
   ``originating_session: N`` in its YAML frontmatter, it's treated as a
   definitive override (added even if no commit match found).
3. **Handoff linking** — ``docs/handoffs/SESSION_<N>_*.md`` is always the
   primary anchor of the cluster.

Default excludes (per ``docs/00-START-HERE/DOC_LIFECYCLE.md`` §0)
-----------------------------------------------------------------

- ``docs/archive/**`` — historical content, not active
- ``docs/docs-pattern/**`` — context-kit framework master, separate domain

Pass ``--include-framework`` / ``--include-archive`` to lift either.

Examples
--------

::

    python manage.py session_provenance --session 1143
    python manage.py session_provenance --session 1143 --format json
    python manage.py session_provenance --session 800 --include-archive
"""

from __future__ import annotations

import json
import re
import subprocess
from collections import OrderedDict
from pathlib import Path
from typing import Optional

from django.core.management.base import BaseCommand


# Default exclude prefixes — per DOC_LIFECYCLE §0 boundary lock (Session 1144)
DEFAULT_EXCLUDES: tuple[str, ...] = ("docs/archive/", "docs/docs-pattern/")

# Cap on docs_modified entries shown in Markdown output. Cleanup sessions
# (like 1143's banner sweep) can touch 600+ files, which overwhelms the
# Markdown render — use ``--format json`` if you need the full list.
_MD_MODIFIED_LIMIT = 30

# Frontmatter regex — matches "session: 1143" or "originating_session: 1143"
# inside the YAML frontmatter block at file head.
_FRONTMATTER_SESSION_RE = re.compile(
    r"^(?:session|originating_session)\s*:\s*(\d+)\s*$",
    re.MULTILINE,
)


class Command(BaseCommand):
    help = "Cluster all docs touched in a given session (git-history-derived)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--session", type=int, required=True,
            help="Session number (e.g. 1143)",
        )
        parser.add_argument(
            "--format", choices=["md", "json"], default="md",
            help="Output format (default: md)",
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
        session = options["session"]
        excludes = list(DEFAULT_EXCLUDES)
        if options["include_framework"]:
            excludes.remove("docs/docs-pattern/")
        if options["include_archive"]:
            excludes.remove("docs/archive/")

        result = build_provenance(session, excludes=excludes)

        if options["format"] == "json":
            self.stdout.write(json.dumps(result, indent=2, default=str))
        else:
            self.stdout.write(render_markdown(result))


def build_provenance(session: int, excludes: list[str]) -> dict:
    """Walk git history and assemble the provenance cluster for ``session``."""
    commits = find_session_commits(session)

    # path -> {"commits": [{"sha", "subject"}], "first_commit_sha": str|None}
    docs: dict[str, dict] = OrderedDict()

    for sha, subject in commits:
        for f in git_files_in_commit(sha):
            if not f.startswith("docs/"):
                continue
            if any(f.startswith(ex) for ex in excludes):
                continue
            entry = docs.setdefault(f, {"commits": [], "first_commit_sha": None})
            entry["commits"].append({"sha": sha[:8], "subject": subject})

    # For each doc, find its first-ever introducing commit (with --follow) to
    # decide "created in this session" vs "only modified."
    in_session_shas = {c["sha"] for sha, _ in commits for c in [{"sha": sha[:8]}]}
    docs_created: list[dict] = []
    docs_modified: list[dict] = []

    for path, info in docs.items():
        first = git_first_commit(path)
        info["first_commit_sha"] = first[0][:8] if first else None
        if first and first[0][:8] in in_session_shas:
            docs_created.append({"path": path, **info})
        else:
            docs_modified.append({"path": path, **info})

    # Frontmatter overrides — any doc with `session: N` or `originating_session: N`
    # that wasn't picked up by the git grep is added with confidence=frontmatter.
    fm_overrides: list[str] = []
    for path in find_docs_with_frontmatter_session(session, excludes=excludes):
        if path not in docs:
            fm_overrides.append(path)

    handoffs = find_handoff_docs(session)

    notes: list[str] = []
    if not commits:
        notes.append(
            f"No commits matched session {session}. Either the session predates "
            "the session-NNNN commit convention, or the search regex needs tuning."
        )
    if not handoffs:
        notes.append(f"No handoff doc found at docs/handoffs/SESSION_{session}_*.md")
    if fm_overrides:
        notes.append(
            f"{len(fm_overrides)} doc(s) declared session={session} via frontmatter "
            "but had no matching commits. Listed under 'frontmatter_only'."
        )

    return {
        "session": session,
        "handoff_docs": handoffs,
        "commit_count": len(commits),
        "commits": [{"sha": sha[:8], "subject": subject} for sha, subject in commits],
        "docs_created": sorted(docs_created, key=lambda d: d["path"]),
        "docs_modified": sorted(docs_modified, key=lambda d: d["path"]),
        "frontmatter_only": sorted(fm_overrides),
        "excludes": excludes,
        "notes": notes,
    }


def find_session_commits(session: int) -> list[tuple[str, str]]:
    """Find commits whose **subject** references this session.

    Matches the conventions used in this repo:
    - ``docs(session-1143): ...``
    - ``feat(session-1143-phaseN): ...``
    - ``Session 1143 ...`` in subject

    Subject-only is deliberate: git's ``--grep`` searches the entire commit
    message by default, which produces false positives when later commits
    cite an earlier session in their body for context. Filter in Python
    against the subject so the result is "commits that ARE this session's
    work" rather than "commits that mention it."
    """
    pattern = re.compile(rf"[Ss]ession[- ]?{session}\b")
    out = _run_git("log", "--all", "--pretty=format:%H|%s")
    commits = []
    for line in out.splitlines():
        if "|" not in line:
            continue
        sha, subject = line.split("|", 1)
        if pattern.search(subject):
            commits.append((sha.strip(), subject.strip()))
    return commits


def git_files_in_commit(sha: str) -> list[str]:
    """List files changed in a commit (excluding the commit subject)."""
    out = _run_git("show", "--name-only", "--pretty=format:", sha)
    return [line.strip() for line in out.splitlines() if line.strip()]


def git_first_commit(path: str) -> Optional[tuple[str, str]]:
    """First commit that introduced ``path`` (follows renames)."""
    out = _run_git(
        "log", "--follow", "--diff-filter=A",
        "--pretty=format:%H|%s", "--", path,
    )
    lines = [l for l in out.splitlines() if "|" in l]
    if not lines:
        return None
    sha, subject = lines[-1].split("|", 1)  # earliest commit is last
    return (sha.strip(), subject.strip())


def find_handoff_docs(session: int) -> list[str]:
    """Find handoff doc(s) at docs/handoffs/SESSION_<N>_*.md."""
    handoff_dir = Path("docs/handoffs")
    if not handoff_dir.exists():
        return []
    return sorted(str(p) for p in handoff_dir.glob(f"SESSION_{session}_*.md"))


def find_docs_with_frontmatter_session(
    session: int, excludes: list[str]
) -> list[str]:
    """Scan active docs for frontmatter ``session:`` / ``originating_session:``.

    Reads only the first 30 lines of each .md file (frontmatter region) to
    keep this fast on a 850+ file corpus.
    """
    matches = []
    for path in Path("docs").rglob("*.md"):
        path_str = str(path)
        if any(path_str.startswith(ex) for ex in excludes):
            continue
        try:
            head = "\n".join(
                line for _, line in zip(
                    range(30), path.read_text(encoding="utf-8").splitlines()
                )
            )
        except (OSError, UnicodeDecodeError):
            continue
        for m in _FRONTMATTER_SESSION_RE.finditer(head):
            if int(m.group(1)) == session:
                matches.append(path_str)
                break
    return matches


def _run_git(*args: str) -> str:
    """Run a git command, return stdout; empty string on failure."""
    try:
        return subprocess.check_output(
            ["git", *args], text=True, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError:
        return ""


def render_markdown(p: dict) -> str:
    """Format provenance dict as a Markdown report."""
    out = [f"# Session {p['session']} provenance\n"]

    if p["handoff_docs"]:
        out.append("## Handoff doc(s)\n")
        for h in p["handoff_docs"]:
            out.append(f"- [`{h}`]({h})")
        out.append("")
    else:
        out.append("## Handoff doc(s)\n\n_None found._\n")

    out.append(f"## Commits ({p['commit_count']})\n")
    if p["commits"]:
        for c in p["commits"][:50]:
            out.append(f"- `{c['sha']}` — {c['subject']}")
        if len(p["commits"]) > 50:
            out.append(f"- _... and {len(p['commits']) - 50} more_")
        out.append("")

    if p["docs_created"]:
        out.append(f"## Docs created in this session ({len(p['docs_created'])})\n")
        for d in p["docs_created"]:
            n = len(d["commits"])
            first = d["first_commit_sha"] or "?"
            out.append(f"- `{d['path']}` _(first: {first}, {n} commit{'' if n == 1 else 's'} this session)_")
        out.append("")

    if p["docs_modified"]:
        out.append(f"## Docs modified in this session ({len(p['docs_modified'])})\n")
        for d in p["docs_modified"][:_MD_MODIFIED_LIMIT]:
            n = len(d["commits"])
            first = d["first_commit_sha"] or "?"
            out.append(f"- `{d['path']}` _(first: {first}, {n} commit{'' if n == 1 else 's'} this session)_")
        if len(p["docs_modified"]) > _MD_MODIFIED_LIMIT:
            extra = len(p["docs_modified"]) - _MD_MODIFIED_LIMIT
            out.append(f"- _... and {extra} more — use `--format json` for the complete list_")
        out.append("")

    if p["frontmatter_only"]:
        out.append(f"## Frontmatter-declared, no commits ({len(p['frontmatter_only'])})\n")
        for path in p["frontmatter_only"]:
            out.append(f"- `{path}`")
        out.append("")

    if p["notes"]:
        out.append("## Notes\n")
        for n in p["notes"]:
            out.append(f"- {n}")
        out.append("")

    out.append("---")
    out.append(f"_Excludes: {', '.join(p['excludes']) or 'none'}_")
    return "\n".join(out)
