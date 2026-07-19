#!/usr/bin/env python3
"""
S2835 T2 reference-graph audit scanner (Group 2800 child 2802).

Scans in-scope /docs/ + root docs for 4 reference classes and resolves each:
  1. Markdown relative-path links: [text](path)
  2. File-path citations in text: `core/services/X.py:LINE`, bare `docs/foo.md`
  3. ADR references: `ADR-NNNN`
  4. Session/handoff cross-refs: `SESSION_NNNN` or `docs/handoffs/SESSION_NNNN`

Classifies each reference:
  PASS      — target exists
  BROKEN_404 — target does not exist and no equivalent-named file found elsewhere
  RENAMED   — target does not exist at cited path but a file of same basename exists
  AMBIGUOUS — multiple candidates match

Emits JSON summary + per-source-doc defect table + broken-ref catalog.

Method: mechanical grep + resolver only. No line-range semantic verification
(parent T2 anti-pattern is deferred: 'if grep says the target resolves, ref
is healthy' — spot-check reserved for §6 sample verification in the doc).

Anti-scope:
  - Does NOT walk handoff SOURCES (T4 territory)
  - Does NOT walk docs/archive/, docs/docs-pattern/, in-flight-arc children
  - Does NOT modify any file
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = REPO_ROOT / "docs"

EXCLUDE_DIR_PREFIXES = (
    "docs/archive/",
    "docs/docs-pattern/",
    "docs/handoffs/",
)

IN_FLIGHT_ARC_CHILD_PATH_MARKERS = (
    "docs/research/domains/docs_content_audit/",  # Group 2800 in-flight
)

ROOT_INCLUDE = ("CLAUDE.md", "00-START-NEXT-SESSION.md", "README.md")

MD_LINK_RE = re.compile(r"\[([^\]]{0,200}?)\]\(([^)#\s]+)(?:#[^)]*)?\)")
ADR_RE = re.compile(r"\bADR[- ](\d{4})\b")
SESSION_RE = re.compile(r"\bSESSION[_ ](\d{3,5})\b")
FILE_LINE_CITE_RE = re.compile(
    r"`?([a-zA-Z0-9_./-]+\.(?:py|md|ts|tsx|js|jsx|yaml|yml|toml|json|sh))(?::(\d+)(?:-(\d+))?)?`?"
)
BARE_MD_PATH_RE = re.compile(r"`([a-zA-Z0-9_./-]+/[a-zA-Z0-9_.-]+\.(?:md|py|ts|tsx|yaml|yml|sh))(?::\d+(?:-\d+)?)?`")


def is_in_scope(rel_path: str) -> bool:
    for pfx in EXCLUDE_DIR_PREFIXES:
        if rel_path.startswith(pfx):
            return False
    for marker in IN_FLIGHT_ARC_CHILD_PATH_MARKERS:
        if rel_path.startswith(marker):
            return False
    return rel_path.endswith(".md")


def enumerate_corpus() -> list[Path]:
    files: list[Path] = []
    for md in DOCS_ROOT.rglob("*.md"):
        rel = str(md.relative_to(REPO_ROOT))
        if is_in_scope(rel):
            files.append(md)
    for name in ROOT_INCLUDE:
        p = REPO_ROOT / name
        if p.exists():
            files.append(p)
    files.sort()
    return files


def extract_md_links(text: str) -> list[tuple[str, str, int]]:
    out = []
    for m in MD_LINK_RE.finditer(text):
        label = m.group(1)
        target = m.group(2).strip()
        if target.startswith(("http://", "https://", "mailto:", "tel:")):
            continue
        line_no = text.count("\n", 0, m.start()) + 1
        out.append((label, target, line_no))
    return out


def extract_adrs(text: str) -> list[tuple[str, int]]:
    out = []
    for m in ADR_RE.finditer(text):
        line_no = text.count("\n", 0, m.start()) + 1
        out.append((m.group(1), line_no))
    return out


def extract_sessions(text: str) -> list[tuple[str, int]]:
    out = []
    for m in SESSION_RE.finditer(text):
        line_no = text.count("\n", 0, m.start()) + 1
        out.append((m.group(1), line_no))
    return out


def extract_file_line_cites(text: str) -> list[tuple[str, str, str, int]]:
    """Extract backticked file:LINE citations (path, start_line, end_line, source_line)."""
    out = []
    for m in FILE_LINE_CITE_RE.finditer(text):
        path = m.group(1)
        start_line = m.group(2) or ""
        end_line = m.group(3) or ""
        if start_line == "" and not any(seg in path for seg in ("/", ".py", ".md", ".ts")):
            continue
        line_no = text.count("\n", 0, m.start()) + 1
        out.append((path, start_line, end_line, line_no))
    return out


BASENAME_INDEX_CACHE: dict[str, list[Path]] | None = None


def build_basename_index() -> dict[str, list[Path]]:
    """Build one-shot basename → [paths] index over the whole repo.

    Excludes .git/, node_modules/, .venv/, __pycache__/.
    """
    global BASENAME_INDEX_CACHE
    if BASENAME_INDEX_CACHE is not None:
        return BASENAME_INDEX_CACHE
    idx: dict[str, list[Path]] = defaultdict(list)
    exclude_dirs = {".git", "node_modules", ".venv", "venv", "__pycache__",
                     ".mypy_cache", ".pytest_cache", "dist", "build"}
    for path in REPO_ROOT.rglob("*"):
        if not path.is_file():
            continue
        parts = set(path.relative_to(REPO_ROOT).parts)
        if parts & exclude_dirs:
            continue
        idx[path.name].append(path)
    BASENAME_INDEX_CACHE = dict(idx)
    return BASENAME_INDEX_CACHE


def resolve_target(source_path: Path, target: str) -> tuple[str, str]:
    """Return (status, resolved_absolute_path).

    Status: PASS | BROKEN_404 | RENAMED | AMBIGUOUS
    """
    if target.startswith("/"):
        candidate = REPO_ROOT / target.lstrip("/")
    else:
        candidate = (source_path.parent / target).resolve()
    if candidate.exists():
        return ("PASS", str(candidate))

    # Try basename fallback via pre-built index
    basename = Path(target).name
    if not basename or "." not in basename:
        return ("BROKEN_404", str(candidate))

    idx = build_basename_index()
    matches = idx.get(basename, [])
    if len(matches) == 0:
        return ("BROKEN_404", str(candidate))
    if len(matches) == 1:
        return ("RENAMED", str(matches[0].relative_to(REPO_ROOT)))
    return ("AMBIGUOUS", ";".join(str(m.relative_to(REPO_ROOT)) for m in matches[:5]))


ADR_INDEX_CACHE: dict[str, Path] | None = None


def build_adr_index() -> dict[str, Path]:
    global ADR_INDEX_CACHE
    if ADR_INDEX_CACHE is not None:
        return ADR_INDEX_CACHE
    idx: dict[str, Path] = {}
    for p in REPO_ROOT.rglob("ADR-*.md"):
        if ".git/" in str(p):
            continue
        m = re.search(r"ADR-(\d{4})", p.name)
        if m:
            idx[m.group(1)] = p
    ADR_INDEX_CACHE = idx
    return idx


SESSION_INDEX_CACHE: dict[str, list[Path]] | None = None


def build_session_index() -> dict[str, list[Path]]:
    global SESSION_INDEX_CACHE
    if SESSION_INDEX_CACHE is not None:
        return SESSION_INDEX_CACHE
    idx: dict[str, list[Path]] = defaultdict(list)
    handoffs_dir = DOCS_ROOT / "handoffs"
    if handoffs_dir.exists():
        for p in handoffs_dir.rglob("SESSION_*.md"):
            m = re.search(r"SESSION_(\d{3,5})", p.name)
            if m:
                idx[m.group(1)].append(p)
    SESSION_INDEX_CACHE = dict(idx)
    return SESSION_INDEX_CACHE


def resolve_adr(adr_num: str) -> tuple[str, str]:
    idx = build_adr_index()
    if adr_num in idx:
        return ("PASS", str(idx[adr_num].relative_to(REPO_ROOT)))
    return ("BROKEN_404", f"ADR-{adr_num}")


def resolve_session(session_num: str) -> tuple[str, str]:
    idx = build_session_index()
    if session_num in idx and len(idx[session_num]) >= 1:
        return ("PASS", str(idx[session_num][0].relative_to(REPO_ROOT)))
    return ("BROKEN_404", f"SESSION_{session_num}")


def resolve_file_cite(source_path: Path, path: str, start_line: str) -> tuple[str, str]:
    """Existence check for file path; does NOT semantically verify line range (T2 anti-pattern)."""
    candidate = (source_path.parent / path).resolve()
    if candidate.exists():
        return ("PASS", str(candidate))
    candidate = REPO_ROOT / path
    if candidate.exists():
        return ("PASS", str(candidate))
    basename = Path(path).name
    idx = build_basename_index()
    matches = idx.get(basename, [])
    if not matches:
        return ("BROKEN_404", path)
    if len(matches) == 1:
        return ("RENAMED", str(matches[0].relative_to(REPO_ROOT)))
    return ("AMBIGUOUS", ";".join(str(m.relative_to(REPO_ROOT)) for m in matches[:5]))


def scan_file(path: Path) -> dict:
    rel = str(path.relative_to(REPO_ROOT))
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return {"file": rel, "error": str(e), "refs": []}

    per_class_counts: dict[str, dict[str, int]] = {
        "md_link": defaultdict(int),
        "adr": defaultdict(int),
        "session": defaultdict(int),
        "file_cite": defaultdict(int),
    }
    findings: list[dict] = []

    # MD links
    seen_md = set()
    for label, target, line_no in extract_md_links(text):
        key = (target, line_no)
        if key in seen_md:
            continue
        seen_md.add(key)
        status, resolved = resolve_target(path, target)
        per_class_counts["md_link"][status] += 1
        if status != "PASS":
            findings.append(
                {"ref_class": "md_link", "target": target, "line": line_no,
                 "status": status, "resolved": resolved, "label": label[:80]}
            )

    # ADR refs (dedupe by number to avoid double-counting)
    seen_adr = set()
    for num, line_no in extract_adrs(text):
        if num in seen_adr:
            continue
        seen_adr.add(num)
        status, resolved = resolve_adr(num)
        per_class_counts["adr"][status] += 1
        if status != "PASS":
            findings.append(
                {"ref_class": "adr", "target": f"ADR-{num}", "line": line_no,
                 "status": status, "resolved": resolved, "label": ""}
            )

    # Session refs (dedupe by number)
    seen_session = set()
    for num, line_no in extract_sessions(text):
        if num in seen_session:
            continue
        seen_session.add(num)
        status, resolved = resolve_session(num)
        per_class_counts["session"][status] += 1
        if status != "PASS":
            findings.append(
                {"ref_class": "session", "target": f"SESSION_{num}", "line": line_no,
                 "status": status, "resolved": resolved, "label": ""}
            )

    # File-line citations
    seen_cite = set()
    for cite_path, start_line, end_line, line_no in extract_file_line_cites(text):
        key = (cite_path, start_line, end_line)
        if key in seen_cite:
            continue
        seen_cite.add(key)
        status, resolved = resolve_file_cite(path, cite_path, start_line)
        per_class_counts["file_cite"][status] += 1
        if status != "PASS":
            findings.append(
                {"ref_class": "file_cite", "target": f"{cite_path}"
                    + (f":{start_line}" if start_line else "")
                    + (f"-{end_line}" if end_line else ""),
                 "line": line_no, "status": status, "resolved": resolved, "label": ""}
            )

    return {
        "file": rel,
        "line_count": text.count("\n") + 1,
        "counts": {k: dict(v) for k, v in per_class_counts.items()},
        "findings": findings,
    }


def main() -> int:
    corpus = enumerate_corpus()
    print(f"Corpus: {len(corpus)} files", file=sys.stderr)
    print("Building basename index...", file=sys.stderr)
    idx = build_basename_index()
    print(f"  {len(idx)} unique basenames indexed", file=sys.stderr)

    results = []
    for i, path in enumerate(corpus, 1):
        if i % 50 == 0:
            print(f"  scanned {i}/{len(corpus)}", file=sys.stderr)
        results.append(scan_file(path))

    # Aggregate
    total_by_class_status: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    total_refs_by_class: dict[str, int] = defaultdict(int)
    files_with_defects = 0
    total_defects = 0
    per_source_defect_rate: list[tuple[str, int, int, float]] = []

    for r in results:
        if "error" in r:
            continue
        file_defect_count = len(r["findings"])
        file_ref_count = sum(sum(v.values()) for v in r["counts"].values())
        for cls, statuses in r["counts"].items():
            for status, n in statuses.items():
                total_by_class_status[cls][status] += n
                total_refs_by_class[cls] += n
        if file_defect_count > 0:
            files_with_defects += 1
        total_defects += file_defect_count
        if file_ref_count > 0:
            per_source_defect_rate.append((r["file"], file_defect_count, file_ref_count,
                                            file_defect_count / file_ref_count))

    per_source_defect_rate.sort(key=lambda t: (-t[1], -t[3]))

    output = {
        "corpus_size": len(corpus),
        "files_with_defects": files_with_defects,
        "total_refs_by_class": dict(total_refs_by_class),
        "total_by_class_status": {k: dict(v) for k, v in total_by_class_status.items()},
        "total_defects": total_defects,
        "top_50_defective_files": [
            {"file": f, "defects": d, "refs": r, "rate": round(rate, 3)}
            for f, d, r, rate in per_source_defect_rate[:50]
        ],
        "results": results,
    }

    print(json.dumps(output, indent=2, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
