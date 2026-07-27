"""
Research Arcs Scanner — Session 2984 / PR3 spec `be68f1d1-1c88-4d72-a908-e57f6ce310dc`.

Scans a research-domains root (default `docs/research/domains/`) and returns
one arc-descriptor per immediate subfolder. Purely automatic: no manual
overrides in PR3 per Chris directive #1.

Status buckets (spec §Status computation):
    - active  — days_since_touched <= ACTIVE_DAYS
    - stale   — days_since_touched >= STALE_DAYS or unknown
    - done    — has_canonical_summary AND open_questions_markers == 0
                AND NOT stale
    - hanging — anything else

`last_touched_at` is preferred from `git log -1 --format=%cI` (via GitPython)
and falls back to max file mtime inside the folder. The mode used is logged
so operators can see whether the runtime environment has git access.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


ACTIVE_DAYS = 14
STALE_DAYS = 60

# Case-insensitive markers per spec §Status computation.
_OPEN_QUESTIONS_RE = re.compile(
    r"\bOPEN QUESTIONS\b|\bOPEN_QUESTION\b|\bTBD\b|\bTODO\b|\bWIP\b",
    re.IGNORECASE,
)

_CANONICAL_SUMMARY_RE = re.compile(r"canonical_summary", re.IGNORECASE)


@dataclass
class ArcEntrypoint:
    label: str
    path: str


@dataclass
class Arc:
    arc_id: str
    title: str
    path: str
    status: str
    last_touched_at: str | None
    days_since_touched: int | None
    entrypoints: list[ArcEntrypoint] = field(default_factory=list)
    signals: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "arc_id": self.arc_id,
            "title": self.title,
            "path": self.path,
            "status": self.status,
            "last_touched_at": self.last_touched_at,
            "days_since_touched": self.days_since_touched,
            "entrypoints": [{"label": e.label, "path": e.path} for e in self.entrypoints],
            "signals": self.signals,
        }


def _git_last_touched(repo_root: Path, arc_path: Path) -> str | None:
    """Return ISO-8601 timestamp of last commit touching arc_path, or None."""
    try:
        from git import Repo  # GitPython 3.1.45 (requirements.txt:114)
    except Exception:
        logger.debug("git.Repo import failed", exc_info=True)
        return None

    try:
        repo = Repo(str(repo_root), search_parent_directories=True)
        work_tree = repo.working_tree_dir
        if work_tree is None:
            return None
        rel = arc_path.relative_to(Path(str(work_tree)))
        # `git log -1 --format=%cI -- <path>` — commit ISO-8601 date.
        out = repo.git.log("-1", "--format=%cI", "--", str(rel))
        out = out.strip()
        return out or None
    except Exception:
        logger.debug("git last_touched failed for %s", arc_path, exc_info=True)
        return None


def _mtime_last_touched(arc_path: Path) -> str | None:
    """Fallback: max mtime among .md files in the arc folder (recursive)."""
    max_mtime: float | None = None
    for md in arc_path.rglob("*.md"):
        if not md.is_file():
            continue
        try:
            mt = md.stat().st_mtime
        except OSError:
            continue
        if max_mtime is None or mt > max_mtime:
            max_mtime = mt
    if max_mtime is None:
        return None
    return datetime.fromtimestamp(max_mtime, tz=timezone.utc).isoformat()


def _pick_entrypoints(arc_path: Path, root: Path) -> list[ArcEntrypoint]:
    """
    Spec §Entrypoint selection:
      - Canonical summary: first case-insensitive *canonical_summary*.md
      - Index: README.md
      - Open questions: OPEN_QUESTIONS.md
      - Fallback: most-recently-touched .md if none of the above
    All returned paths are POSIX-style relative to `root.parent.parent.parent`
    (i.e. the repo root) so the frontend can pass them straight to the
    doc viewer.
    """
    repo_root = root.parent.parent.parent  # docs/research/domains -> repo root
    entries: list[ArcEntrypoint] = []
    md_files = sorted(p for p in arc_path.iterdir() if p.is_file() and p.suffix.lower() == ".md")

    def rel(p: Path) -> str:
        return p.relative_to(repo_root).as_posix()

    canonical = next((p for p in md_files if _CANONICAL_SUMMARY_RE.search(p.name)), None)
    if canonical is not None:
        entries.append(ArcEntrypoint(label="Canonical summary", path=rel(canonical)))

    readme = arc_path / "README.md"
    if readme.is_file():
        entries.append(ArcEntrypoint(label="Index", path=rel(readme)))

    open_qs = arc_path / "OPEN_QUESTIONS.md"
    if open_qs.is_file():
        entries.append(ArcEntrypoint(label="Open questions", path=rel(open_qs)))

    if not entries:
        # Fallback: most-recently-touched .md by mtime.
        best: Path | None = None
        best_mt = -1.0
        for md in md_files:
            try:
                mt = md.stat().st_mtime
            except OSError:
                continue
            if mt > best_mt:
                best_mt = mt
                best = md
        if best is not None:
            entries.append(ArcEntrypoint(label="Latest doc", path=rel(best)))

    return entries


def _count_signals(arc_path: Path) -> dict[str, Any]:
    """Count spec §Status computation signals across all .md files in arc."""
    has_canonical = False
    open_q_hits = 0
    todo_hits = 0

    for md in arc_path.rglob("*.md"):
        if not md.is_file():
            continue
        if _CANONICAL_SUMMARY_RE.search(md.name):
            has_canonical = True
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for match in _OPEN_QUESTIONS_RE.finditer(text):
            token = match.group(0).upper()
            open_q_hits += 1
            if token in ("TODO", "TBD", "WIP"):
                todo_hits += 1

    return {
        "has_canonical_summary": has_canonical,
        "open_questions_markers": open_q_hits,
        "todo_hits": todo_hits,
    }


def _compute_status(days_since: int | None, has_canonical: bool, open_q: int) -> str:
    """Deterministic status per spec §Status computation."""
    if days_since is None or days_since >= STALE_DAYS:
        return "stale"
    if days_since <= ACTIVE_DAYS:
        return "active"
    # 15..59 days window: done if canonical + no open questions, else hanging.
    if has_canonical and open_q == 0:
        return "done"
    return "hanging"


def _days_since(iso_ts: str | None, now: datetime | None = None) -> int | None:
    if iso_ts is None:
        return None
    try:
        ts = datetime.fromisoformat(iso_ts)
    except ValueError:
        return None
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    now_ = now or datetime.now(tz=timezone.utc)
    delta = now_ - ts
    return max(0, delta.days)


def scan_research_arcs(
    root: Path,
    *,
    now: datetime | None = None,
    active_days: int = ACTIVE_DAYS,
    stale_days: int = STALE_DAYS,
) -> dict[str, Any]:
    """
    Scan `root` for arc subfolders and return the spec §Response JSON shape.

    Deterministic ordering: arcs sorted by arc_id (folder name).
    """
    generated_at = (now or datetime.now(tz=timezone.utc)).isoformat()

    if not root.is_dir():
        logger.warning("research_arcs_scanner: root %s missing", root)
        return {
            "generated_at": generated_at,
            "root": str(root),
            "active_days": active_days,
            "stale_days": stale_days,
            "arcs": [],
        }

    git_mode_hits = 0
    mtime_mode_hits = 0
    arcs: list[Arc] = []

    for child in sorted(root.iterdir(), key=lambda p: p.name):
        if not child.is_dir():
            continue
        arc_id = child.name

        touched = _git_last_touched(root, child)
        if touched is not None:
            git_mode_hits += 1
        else:
            touched = _mtime_last_touched(child)
            if touched is not None:
                mtime_mode_hits += 1

        days_since = _days_since(touched, now=now)
        signals = _count_signals(child)
        status = _compute_status(
            days_since, signals["has_canonical_summary"], signals["open_questions_markers"]
        )
        entrypoints = _pick_entrypoints(child, root)

        arcs.append(
            Arc(
                arc_id=arc_id,
                title=arc_id,  # spec: title = slug (Chris directive #1 purely automatic)
                path=child.relative_to(root.parent.parent.parent).as_posix(),
                status=status,
                last_touched_at=touched,
                days_since_touched=days_since,
                entrypoints=entrypoints,
                signals=signals,
            )
        )

    if arcs:
        logger.info(
            "research_arcs_scanner: %d arcs scanned (git=%d, mtime=%d)",
            len(arcs), git_mode_hits, mtime_mode_hits,
        )

    return {
        "generated_at": generated_at,
        "root": str(root),
        "active_days": active_days,
        "stale_days": stale_days,
        "arcs": [a.to_dict() for a in arcs],
    }
