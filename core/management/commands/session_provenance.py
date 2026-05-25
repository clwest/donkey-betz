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
    non_docs: dict[str, dict] = OrderedDict()

    # Track per-commit file-touch counts as we walk (rendered later)
    commit_paths_touched: dict[str, int] = {}

    for c in commits:
        sha = c["sha"]
        subject = c["subject"]
        files = git_files_in_commit(sha)
        commit_paths_touched[sha[:8]] = len(files)
        for f in files:
            # Skip docs/ paths under exclude prefixes (per DOC_LIFECYCLE §0)
            if f.startswith("docs/") and any(f.startswith(ex) for ex in excludes):
                continue
            # Pick which bucket the path goes into
            bucket = docs if f.startswith("docs/") else non_docs
            entry = bucket.setdefault(f, {"commits": [], "first_commit_sha": None})
            entry["commits"].append(
                {"sha": sha[:8], "subject": subject, "match": c["match"]}
            )

    # For each doc, find its first-ever introducing commit (with --follow) to
    # decide "created in this session" vs "only modified."
    in_session_shas = {c["sha"][:8] for c in commits}
    docs_created: list[dict] = []
    docs_modified: list[dict] = []

    for path, info in docs.items():
        first = git_first_commit(path)
        info["first_commit_sha"] = first[0][:8] if first else None
        if first and first[0][:8] in in_session_shas:
            docs_created.append({"path": path, **info})
        else:
            docs_modified.append({"path": path, **info})

    # Same split for non-docs paths (code, config, tests, etc.) — so a session
    # like 1144 that ships a code fix has its non-doc surface visible alongside
    # the doc surface. "What did this session produce?" = both.
    non_docs_created: list[dict] = []
    non_docs_modified: list[dict] = []
    for path, info in non_docs.items():
        first = git_first_commit(path)
        info["first_commit_sha"] = first[0][:8] if first else None
        if first and first[0][:8] in in_session_shas:
            non_docs_created.append({"path": path, **info})
        else:
            non_docs_modified.append({"path": path, **info})

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

    subject_matches = sum(1 for c in commits if c["match"] == "subject")
    body_matches = sum(1 for c in commits if c["match"] == "body")
    if body_matches:
        notes.append(
            f"{body_matches} commit(s) matched the session by **body** only (no "
            "session-NNNN tag in subject). These are MEDIUM confidence — verify "
            "they're this session's work and not later commits citing it as context."
        )

    # Explicit hygiene-gap callout — Rigby Session 1144 review: tell the
    # operator out loud when no subject-tagged commits exist at all, so the
    # commit-convention lesson isn't something humans have to infer.
    coverage_warning = subject_matches == 0 and body_matches > 0
    if coverage_warning:
        notes.append(
            "No subject-tagged commits found; provenance is MEDIUM confidence. "
            "Consider tagging commits `session-####` in subject going forward "
            "(e.g. `docs(session-NNNN): ...`)."
        )

    coverage = {
        "matched_commits": len(commits),
        "subject_match_count": subject_matches,
        "body_match_count": body_matches,
        "session_tag_in_subject_rate": (
            round(subject_matches / len(commits), 3) if commits else None
        ),
        "coverage_warning": coverage_warning,
        "commit_hygiene_recommendation": (
            "Tag every session-N commit subject with `session-N` "
            "(e.g. `docs(session-1144): ...`)"
        ),
    }

    return {
        "session": session,
        "handoff_docs": handoffs,
        "commit_count": len(commits),
        # Backwards-compat aliases (deprecated, prefer coverage.*)
        "subject_match_count": subject_matches,
        "body_match_count": body_matches,
        "coverage": coverage,
        "commits": [
            {
                "sha": c["sha"][:8],
                "subject": c["subject"],
                "match": c["match"],
                "match_level": "HIGH" if c["match"] == "subject" else "MEDIUM",
                "match_source": c["match"],
                "session_tag_present": c["match"] == "subject",
                "paths_touched_count": commit_paths_touched.get(c["sha"][:8], 0),
            }
            for c in commits
        ],
        "docs_created": sorted(docs_created, key=lambda d: d["path"]),
        "docs_modified": sorted(docs_modified, key=lambda d: d["path"]),
        "non_docs_created": sorted(non_docs_created, key=lambda d: d["path"]),
        "non_docs_modified": sorted(non_docs_modified, key=lambda d: d["path"]),
        "counts": {
            "docs_created": len(docs_created),
            "docs_modified": len(docs_modified),
            "non_docs_created": len(non_docs_created),
            "non_docs_modified": len(non_docs_modified),
            "frontmatter_only": len(fm_overrides),
        },
        "frontmatter_only": sorted(fm_overrides),
        "scope": {
            "root": "docs/",
            "excludes": excludes,
        },
        "excludes": excludes,  # kept top-level for backwards compat
        "notes": notes,
    }


def find_session_commits(session: int) -> list[dict]:
    """Find commits that reference this session — subject first, body fallback.

    Two-tier match (each commit tagged with its match source so the caller
    can show confidence):

    - **subject** — commit's ``%s`` matches ``[Ss]ession[- ]?N\\b``. HIGH
      confidence; this is the repo's preferred convention
      (``docs(session-1143): ...``, ``feat(session-1143-phaseN): ...``).
    - **body** — commit's full message contains ``Session N`` but subject
      doesn't. MEDIUM confidence; could be the session's own work that
      forgot the subject tag, OR a later commit citing this session as
      context. Caller should display these with a "body-match" label so a
      reviewer can sanity-check.

    Returns a list of dicts: ``{"sha", "subject", "match": "subject"|"body"}``.
    """
    pattern = re.compile(rf"[Ss]ession[- ]?{session}\b")
    # Pull every commit subject (cheap).
    subject_out = _run_git("log", "--all", "--pretty=format:%H|%s")
    subject_matches: dict[str, str] = OrderedDict()  # sha -> subject
    all_subjects: dict[str, str] = {}
    for line in subject_out.splitlines():
        if "|" not in line:
            continue
        sha, subject = line.split("|", 1)
        sha, subject = sha.strip(), subject.strip()
        all_subjects[sha] = subject
        if pattern.search(subject):
            subject_matches[sha] = subject

    # Body fallback — use git's --grep on the full message, then filter out
    # any commits already caught by the subject pass. Anything left is a
    # body-only mention. POSIX ERE doesn't support `\b`, so use a manual
    # non-digit lookahead via character class instead.
    body_grep_out = _run_git(
        "log", "--all", "--pretty=format:%H",
        f"--grep=[Ss]ession[- ]?{session}([^0-9]|$)", "-E",
    )
    body_only_shas = [
        sha.strip() for sha in body_grep_out.splitlines()
        if sha.strip() and sha.strip() not in subject_matches
    ]

    result: list[dict] = []
    for sha, subject in subject_matches.items():
        result.append({"sha": sha, "subject": subject, "match": "subject"})
    for sha in body_only_shas:
        result.append({
            "sha": sha,
            "subject": all_subjects.get(sha, "(subject unavailable)"),
            "match": "body",
        })
    return result


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

    subj_n = p.get("subject_match_count", 0)
    body_n = p.get("body_match_count", 0)
    confidence = f"subject: {subj_n}, body-only: {body_n}"
    out.append(f"## Commits ({p['commit_count']} — {confidence})\n")
    if p["commits"]:
        for c in p["commits"][:50]:
            label = "" if c.get("match") == "subject" else " _(body-match)_"
            out.append(f"- `{c['sha']}` — {c['subject']}{label}")
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

    if p["non_docs_created"]:
        out.append(f"## Non-doc files created in this session ({len(p['non_docs_created'])})\n")
        for d in p["non_docs_created"][:_MD_MODIFIED_LIMIT]:
            n = len(d["commits"])
            first = d["first_commit_sha"] or "?"
            out.append(f"- `{d['path']}` _(first: {first}, {n} commit{'' if n == 1 else 's'} this session)_")
        if len(p["non_docs_created"]) > _MD_MODIFIED_LIMIT:
            extra = len(p["non_docs_created"]) - _MD_MODIFIED_LIMIT
            out.append(f"- _... and {extra} more — use `--format json` for the complete list_")
        out.append("")

    if p["non_docs_modified"]:
        out.append(f"## Non-doc files modified in this session ({len(p['non_docs_modified'])})\n")
        for d in p["non_docs_modified"][:_MD_MODIFIED_LIMIT]:
            n = len(d["commits"])
            first = d["first_commit_sha"] or "?"
            out.append(f"- `{d['path']}` _(first: {first}, {n} commit{'' if n == 1 else 's'} this session)_")
        if len(p["non_docs_modified"]) > _MD_MODIFIED_LIMIT:
            extra = len(p["non_docs_modified"]) - _MD_MODIFIED_LIMIT
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
