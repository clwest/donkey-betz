#!/usr/bin/env python3
"""
S2837 T3b orphan-reachability audit scanner (Group 2800 child 2803b).

Determines reachability of each in-scope /docs/ + root doc from three
independent graphs, then classifies severity per T3b spec (parent §4).

Reachability graphs:
  (a) CLAUDE.md anchor graph — BFS from CLAUDE.md following markdown
      links + backtick-quoted paths across all in-scope .md files.
      "cited" means "reachable in this closure."
  (b) docs/INDEX.md autogen references — parse the autogen table; every
      file listed is "reachable-from-index."
  (c) search_docs corpus inclusion — a file is "corpus-included" iff
      an active content.Document row exists with that file_path.
      Top-K retrieval frequency for probe queries is deferred to
      future_trigger (see §6 limitations); corpus-inclusion is the
      load-bearing measurement.

Severity classes (per parent §4 T3b):
  - `unreachable-from-all-3-graphs`  → real orphan candidate (P1-P2)
  - `reachable-from-search-only`     → V2-stub-shaped (P3 by design)
  - `cited-but-search-invisible`     → cited by anchor/index but no
                                       Document row (P1 — retrieval blind)
  - `cited-multi-graph-OK`           → healthy (P3)

Pre-clustering signals consumed (parent §4 T3b + T3a §5.4):
  - T3a V2-stub cluster (110+ files from §2.3): pre-marked as
    reachable-only-from-search BY DESIGN. `is_v2_stub=true` overrides
    severity classification: even if unreachable from CLAUDE + INDEX,
    a V2 stub is `reachable-from-search-only` (P3), NOT an orphan.
  - T2 RENAMED basename map: annotates each file with whether a T2
    RENAMED classification exists on its basename (surface signal).

Anti-scope (per S2836 close pointer + T3a↔T5 boundary rule):
  - Does NOT execute archive / anchor edits — classification only.
  - Does NOT finalize disposition for T5-territory files
    (`docs/audits/**`, `docs/reports/**`). Findings for those paths
    carry `t5_may_override: YES` in migration-queue rows.
  - Does NOT walk handoff files (T4 territory).
  - Does NOT walk docs/archive/, docs/docs-pattern/, in-flight-arc
    children (2800 own thread docs).
  - Does NOT modify any file.
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict, deque
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = REPO_ROOT / "docs"

# So `django.setup()` can find core.settings.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

EXCLUDE_DIR_PREFIXES = (
    "docs/archive/",
    "docs/docs-pattern/",
    "docs/handoffs/",
)

IN_FLIGHT_ARC_CHILD_PATH_MARKERS = (
    "docs/research/domains/docs_content_audit/",
)

T5_TERRITORY_PREFIXES = (
    "docs/audits/",
    "docs/audit-2026/",
    "docs/audit/",
    "docs/reports/",
)

ROOT_INCLUDE = ("CLAUDE.md", "00-START-NEXT-SESSION.md", "README.md")

# Anchor entry points for graph (a). Parent §4 T3b names "CLAUDE.md anchor
# graph"; we start the BFS from CLAUDE.md only. Files reachable via
# link-transitivity from CLAUDE.md are the "reachable-from-anchor" set.
ANCHOR_ENTRY_POINTS = ("CLAUDE.md",)

# Markdown link + backtick-quoted path patterns. We treat both as
# citation edges: an anchor doc referencing `docs/topics/foo.md`
# either as [text](docs/topics/foo.md) or `docs/topics/foo.md` counts
# as citation.
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
BACKTICK_PATH_RE = re.compile(r"`([^`\n]+\.md)`")


def is_in_scope(rel_path: str) -> bool:
    """T3b in-scope = same as T2/T3a (~792 files)."""
    for pfx in EXCLUDE_DIR_PREFIXES:
        if rel_path.startswith(pfx):
            return False
    for marker in IN_FLIGHT_ARC_CHILD_PATH_MARKERS:
        if rel_path.startswith(marker):
            return False
    if rel_path in ROOT_INCLUDE:
        return True
    return rel_path.startswith("docs/") and rel_path.endswith(".md")


def is_t5_territory(rel_path: str) -> bool:
    """T3a↔T5 boundary rule generalized to T3b."""
    return any(rel_path.startswith(p) for p in T5_TERRITORY_PREFIXES)


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
    # sort for deterministic ordering
    return sorted(set(files), key=lambda p: str(p))


def extract_link_targets(md_text: str, source_dir: Path) -> set[str]:
    """Return set of relative-to-repo-root .md paths cited from md_text.

    Handles:
      - [text](path.md)
      - [text](../path.md)
      - `path.md`
    Ignores http(s):// and mailto: URIs.
    """
    targets: set[str] = set()

    def _normalize(candidate: str) -> str | None:
        # Strip fragment
        if "#" in candidate:
            candidate = candidate.split("#", 1)[0]
        candidate = candidate.strip()
        if not candidate.endswith(".md"):
            return None
        if candidate.startswith(("http://", "https://", "mailto:")):
            return None
        # Resolve relative to source_dir; but if it starts with docs/
        # or CLAUDE.md-style, treat as repo-root-relative.
        if candidate.startswith(("docs/", "CLAUDE.md", "00-START-NEXT-SESSION.md", "README.md")):
            return candidate
        # Otherwise resolve relative to source_dir
        try:
            resolved = (source_dir / candidate).resolve()
            rel = resolved.relative_to(REPO_ROOT)
            return str(rel)
        except (ValueError, OSError):
            return None

    for m in MD_LINK_RE.finditer(md_text):
        norm = _normalize(m.group(1))
        if norm:
            targets.add(norm)

    for m in BACKTICK_PATH_RE.finditer(md_text):
        norm = _normalize(m.group(1))
        if norm:
            targets.add(norm)

    return targets


def bfs_from_anchor(
    anchor_paths: tuple[str, ...], in_scope_paths: set[str]
) -> set[str]:
    """BFS from anchor entry points through .md link graph.

    Returns the set of paths (as repo-root-relative strings) reachable
    from any anchor entry point via markdown-link or backtick-path
    citations, restricted to in-scope paths.
    """
    reached: set[str] = set()
    queue: deque[str] = deque()

    for anchor in anchor_paths:
        anchor_abs = REPO_ROOT / anchor
        if anchor_abs.exists() and anchor in in_scope_paths:
            reached.add(anchor)
            queue.append(anchor)

    while queue:
        current = queue.popleft()
        current_abs = REPO_ROOT / current
        try:
            text = current_abs.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        source_dir = current_abs.parent
        targets = extract_link_targets(text, source_dir)
        for tgt in targets:
            if tgt in in_scope_paths and tgt not in reached:
                reached.add(tgt)
                queue.append(tgt)

    return reached


def extract_docs_index_refs(index_path: Path, in_scope_paths: set[str]) -> set[str]:
    """Parse docs/INDEX.md autogen references. All cited .md paths.

    docs/INDEX.md is an autogen'd markdown index; we treat every
    referenced .md path in it as a reachability edge from graph (b).
    """
    if not index_path.exists():
        return set()
    text = index_path.read_text(encoding="utf-8", errors="replace")
    refs = extract_link_targets(text, index_path.parent)
    return {r for r in refs if r in in_scope_paths}


def load_search_corpus_paths() -> set[str]:
    """Return set of file_path values from active content.Document rows.

    A file's presence in this set = "search_docs would find it if the
    similarity search hits its embedded chunks."
    """
    import django
    django.setup()
    from content.models import Document

    paths = set(
        Document.objects.filter(is_active=True)
        .values_list("file_path", flat=True)
    )
    # normalize None + strip
    return {p.strip() for p in paths if p}


def load_v2_stub_paths() -> set[str]:
    """Return the set of file paths that are DOC-POINTER-V2 stubs.

    Detected by scanning the corpus for the V2 marker string. Matches
    T3a §2.3 cluster (~110 files).
    """
    v2_paths: set[str] = set()
    marker = "<!-- DOC-POINTER-V2"
    for md in DOCS_ROOT.rglob("*.md"):
        rel = str(md.relative_to(REPO_ROOT))
        if not is_in_scope(rel):
            continue
        try:
            # Only read first 1KB — V2 marker is at top
            with md.open("rb") as f:
                head = f.read(1024).decode("utf-8", errors="replace")
        except OSError:
            continue
        if marker in head:
            v2_paths.add(rel)
    return v2_paths


def load_t2_renamed_basenames(path: str = "/tmp/t2_scan_out.json") -> set[str]:
    """Load T2 RENAMED basenames as surface annotation signal."""
    p = Path(path)
    if not p.exists():
        return set()
    try:
        d = json.loads(p.read_text())
    except Exception:
        return set()
    basenames: set[str] = set()
    for row in d.get("results", []):
        for f in row.get("findings", []):
            if f.get("status") == "RENAMED":
                target = f.get("target") or ""
                if target:
                    basenames.add(Path(target).name)
    return basenames


SEARCH_ONLY_BENIGN_PATTERNS = (
    # Ratification envelope archives — search-only by design (historical
    # governance artifacts; retrieved via search, not navigated via anchor).
    # High-confidence classification: RATIFICATION_ prefix is unambiguous.
    ("docs/research/implementation/RATIFICATION_", "ratification_envelope"),
    # Implementation-arc children — closed arc artifacts persist in-tree
    # for search-based retrieval; not intended as anchor-navigable.
    ("docs/research/implementation/", "implementation_arc_artifact"),
    # Domain research arc children (closed arcs) — persistent, search-reachable.
    # Closed arc children live under domains/ + discovery_layer/ + platform/
    # after their arc closes; consumed via search_docs, not anchor navigation.
    ("docs/research/domains/", "closed_research_arc_child"),
    ("docs/research/discovery_layer/", "closed_research_arc_child"),
    ("docs/research/platform/", "closed_research_arc_child"),
    # Narrowed at S2837 T3b Rigby cycle-1 Q2 fold: docs/research/tools/
    # contains BOTH closed validation-campaign artifacts (validation/
    # subdir, 22 files) AND active campaign-plan / pressure-test docs
    # (top-level tools_*.md, 4 files) that are "awaiting Chris approval"
    # per Rigby-verified counterevidence in
    # `docs/research/tools/tools_validation_engineering_campaign_plan.md`
    # lines 3-5. Only the validation/ subdir is the closed-artifact
    # cluster; the 4 top-level campaign docs get unclassified so their
    # anchor-visibility is a Chris judgment call.
    ("docs/research/tools/validation/", "closed_research_arc_tool"),
    # Closed-pack archives (one-shot session packs kept for reference).
    # High-confidence: these are known closed arcs from S1099-era cleanup
    # and S1200-era code review whose contents remain valuable to search
    # but were never intended as anchor-navigable running documentation.
    ("docs/cleanup/", "closed_arc_pack"),
    ("docs/code-review/", "closed_arc_pack"),
    # Note: docs/spokesperson/, docs/audit-2026/, docs/audit/ are
    # deliberately NOT auto-classified as benign — they are
    # subject-matter subdirs whose intended anchor-visibility is a
    # Chris judgment call (deferred to 2899).
)


def search_only_pattern_kind(rel_path: str) -> str | None:
    """Sub-classify a search-only-reachable path against known benign patterns.

    Returns pattern label if the file is in a known search-only-by-design
    location (envelope archive, closed arc child, one-shot pack); None
    if the file is genuinely unclassifiable (real escalate candidate).
    """
    for prefix, label in SEARCH_ONLY_BENIGN_PATTERNS:
        if rel_path.startswith(prefix):
            return label
    return None


def classify(
    rel_path: str,
    reachable_anchor: bool,
    reachable_index: bool,
    reachable_search: bool,
    is_v2_stub: bool,
    is_t5: bool,
) -> tuple[str, str, str, str]:
    """Return (severity_class, severity, recommended_action, notes).

    Anti-pattern challenged (parent §4 T3b): "unreachable = orphan =
    archive." V2 pointer stubs are reachable-only-from-search BY
    DESIGN; several other patterns (ratification envelopes, closed
    research-arc children, one-shot packs) also intentionally live
    in search-only reachability.
    """
    # V2-stub pre-classification override (T3a §5.4 signal): V2 stubs
    # are ALWAYS P3 keep_as_is regardless of anchor/index reachability;
    # severity_class reflects actual reachability so downstream tooling
    # sees the honest measurement, not the disposition-override.
    if is_v2_stub:
        if reachable_anchor or reachable_index:
            sev_class = "cited-multi-graph-OK" if reachable_search else "cited-but-search-invisible"
        elif reachable_search:
            sev_class = "reachable-from-search-only"
        else:
            sev_class = "unreachable-from-all-3-graphs"
        return (
            sev_class,
            "P3",
            "keep_as_is",
            "V2 pointer stub (DOC_LIFECYCLE §1) — always P3 keep_as_is",
        )

    # Multi-graph reachable
    if reachable_anchor and reachable_index and reachable_search:
        return ("cited-multi-graph-OK", "P3", "keep_as_is", "reachable from all 3 graphs")

    # Reachable from anchor or index but not from search corpus
    if (reachable_anchor or reachable_index) and not reachable_search:
        return (
            "cited-but-search-invisible",
            "P1",
            "escalate_to_chris",
            "cited by anchor/index but no active Document row — retrieval blind",
        )

    # Reachable from anchor + index but search-corpus OK
    if (reachable_anchor or reachable_index) and reachable_search:
        return (
            "cited-multi-graph-OK",
            "P3",
            "keep_as_is",
            "reachable from anchor/index + search",
        )

    # Reachable from search corpus only — sub-classify against known benign patterns
    if reachable_search and not reachable_anchor and not reachable_index:
        # T3a↔T5 boundary rule: T5-territory files carry t5_may_override
        # regardless of sub-pattern
        if is_t5:
            return (
                "reachable-from-search-only",
                "P3",
                "keep_as_is",
                "T5-territory search-only — disposition deferred to T5 (t5_may_override)",
            )
        pattern = search_only_pattern_kind(rel_path)
        if pattern is not None:
            return (
                "reachable-from-search-only",
                "P3",
                "keep_as_is",
                f"search-only-by-design ({pattern}) — persistent artifact intentionally not anchor-navigable",
            )
        # Not V2, not T5, not in known benign pattern — real escalate candidate
        return (
            "reachable-from-search-only",
            "P2",
            "escalate_to_chris",
            "search-only reachable, no known benign pattern — Chris judgment needed",
        )

    # Unreachable from all 3 graphs — real orphan candidate
    return (
        "unreachable-from-all-3-graphs",
        "P1",
        "escalate_to_chris",
        "no reachability signal from anchor/index/search — real orphan candidate",
    )


def build_report(
    corpus: list[Path],
    reachable_anchor: set[str],
    reachable_index: set[str],
    corpus_paths: set[str],
    v2_stubs: set[str],
    t2_renamed_bn: set[str],
) -> list[dict]:
    """Return per-file classification rows."""
    rows: list[dict] = []
    for f in corpus:
        rel = str(f.relative_to(REPO_ROOT))
        is_v2 = rel in v2_stubs
        is_t5 = is_t5_territory(rel)
        r_anchor = rel in reachable_anchor
        r_index = rel in reachable_index
        r_search = rel in corpus_paths
        t2_signal = f.name in t2_renamed_bn

        severity_class, severity, action, notes = classify(
            rel, r_anchor, r_index, r_search, is_v2, is_t5
        )

        search_only_kind = None
        if severity_class == "reachable-from-search-only":
            if is_v2:
                search_only_kind = "v2_pointer_stub"
            elif is_t5:
                search_only_kind = "t5_territory"
            else:
                search_only_kind = search_only_pattern_kind(rel) or "unclassified"

        rows.append(
            {
                "file_path": rel,
                "severity_class": severity_class,
                "severity": severity,
                "recommended_action": action,
                "reachable_from_claude_md_anchor": r_anchor,
                "reachable_from_docs_index": r_index,
                "reachable_from_search_corpus": r_search,
                "is_v2_pointer_stub": is_v2,
                "is_t5_territory": is_t5,
                "t5_may_override": is_t5,
                "t2_renamed_basename_signal": t2_signal,
                "search_only_kind": search_only_kind,
                "notes": notes,
            }
        )
    return rows


def summarize(rows: list[dict]) -> dict:
    """Emit histograms + counts for §2 audit body."""
    sev_class_hist: dict[str, int] = defaultdict(int)
    sev_hist: dict[str, int] = defaultdict(int)
    action_hist: dict[str, int] = defaultdict(int)
    v2_stub_count = 0
    t5_territory_count = 0
    both_v2_and_t5 = 0
    t2_renamed_flagged = 0

    for r in rows:
        sev_class_hist[r["severity_class"]] += 1
        sev_hist[r["severity"]] += 1
        action_hist[r["recommended_action"]] += 1
        if r["is_v2_pointer_stub"]:
            v2_stub_count += 1
        if r["is_t5_territory"]:
            t5_territory_count += 1
        if r["is_v2_pointer_stub"] and r["is_t5_territory"]:
            both_v2_and_t5 += 1
        if r["t2_renamed_basename_signal"]:
            t2_renamed_flagged += 1

    search_only_kind_hist: dict[str, int] = defaultdict(int)
    for r in rows:
        kind = r.get("search_only_kind")
        if kind:
            search_only_kind_hist[kind] += 1

    return {
        "corpus_size": len(rows),
        "by_severity_class": dict(sev_class_hist),
        "by_severity": dict(sev_hist),
        "by_recommended_action": dict(action_hist),
        "by_search_only_kind": dict(search_only_kind_hist),
        "v2_stub_count": v2_stub_count,
        "t5_territory_count": t5_territory_count,
        "both_v2_and_t5": both_v2_and_t5,
        "t2_renamed_basename_signal_count": t2_renamed_flagged,
    }


def main() -> None:
    out_path = Path("/tmp/t3b_orphan_scan_out.json")
    for arg in sys.argv[1:]:
        if arg.startswith("--out="):
            out_path = Path(arg.split("=", 1)[1])

    print(f"[T3b scanner] enumerating corpus...", file=sys.stderr)
    corpus = enumerate_corpus()
    in_scope_paths = {str(f.relative_to(REPO_ROOT)) for f in corpus}
    print(f"[T3b scanner] {len(corpus)} in-scope files", file=sys.stderr)

    print(f"[T3b scanner] pre-clustering: loading V2-stub set...", file=sys.stderr)
    v2_stubs = load_v2_stub_paths()
    print(f"[T3b scanner] {len(v2_stubs)} V2-stub files pre-classified", file=sys.stderr)

    print(f"[T3b scanner] pre-clustering: loading T2 RENAMED basenames...", file=sys.stderr)
    t2_renamed_bn = load_t2_renamed_basenames()
    print(f"[T3b scanner] {len(t2_renamed_bn)} T2 RENAMED basenames", file=sys.stderr)

    print(f"[T3b scanner] graph (a): BFS from CLAUDE.md...", file=sys.stderr)
    reachable_anchor = bfs_from_anchor(ANCHOR_ENTRY_POINTS, in_scope_paths)
    print(f"[T3b scanner] {len(reachable_anchor)} files reachable from anchor graph", file=sys.stderr)

    print(f"[T3b scanner] graph (b): parsing docs/INDEX.md...", file=sys.stderr)
    reachable_index = extract_docs_index_refs(DOCS_ROOT / "INDEX.md", in_scope_paths)
    print(f"[T3b scanner] {len(reachable_index)} files cited from docs/INDEX.md", file=sys.stderr)

    print(f"[T3b scanner] graph (c): loading search corpus (Document.file_path)...", file=sys.stderr)
    corpus_paths_all = load_search_corpus_paths()
    corpus_paths = corpus_paths_all & in_scope_paths
    print(f"[T3b scanner] {len(corpus_paths)}/{len(corpus_paths_all)} corpus rows in-scope", file=sys.stderr)

    print(f"[T3b scanner] classifying...", file=sys.stderr)
    rows = build_report(
        corpus,
        reachable_anchor,
        reachable_index,
        corpus_paths,
        v2_stubs,
        t2_renamed_bn,
    )

    summary = summarize(rows)
    payload = {"summary": summary, "results": rows}
    out_path.write_text(json.dumps(payload, indent=2))

    print(f"[T3b scanner] wrote {out_path}", file=sys.stderr)
    print(f"[T3b scanner] summary:", file=sys.stderr)
    for k, v in summary.items():
        print(f"  {k}: {v}", file=sys.stderr)


if __name__ == "__main__":
    main()
