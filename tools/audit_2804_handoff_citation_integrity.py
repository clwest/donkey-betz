#!/usr/bin/env python3
"""
S2838 T4 handoff citation-integrity + retrieval-harm audit scanner
(Group 2800 child 2804).

Scope (per parent §4 T4): `docs/handoffs/**` (1061 files as of head
`ae519b4392cf`). Per-handoff CONTENT review is quarantined (parent
§7 anti-scope: handoffs are terminal-by-design write-once artifacts).
This scanner measures citation-integrity + retrieval-harm surface,
NOT per-file content quality.

Three sub-loops (parent §4 T4):

  (a) Citation-graph: for every citation of the form
      `docs/handoffs/SESSION_NNNN*` or short-form `SESSION_NNNN`
      across the non-handoff corpus, aggregate (citing_doc,
      cited_handoff_session) edges. Emit hit-rate + decay curve
      by session-number bucket. Cross-annotate each citing_doc
      with T3b anchor-reachability (from `/tmp/t3b_orphan_scan_out.json`).

  (b) Fragment-citation spot-check: grep the corpus for
      handoff citations carrying URL fragments
      (`docs/handoffs/SESSION_NNN.md#K` chunk-ID form OR
      `docs/handoffs/SESSION_NNN.md#section-anchor` form). Sample
      up to 10 fragment-form citations; for each, verify whether
      the fragment target still resolves in the current handoff
      file (tests post-S1143 chunk-ID reset hypothesis).

  (c) Retrieval-harm sub-loop: run `search_embeddings` for a fixed
      set of common operational probe queries (per parent §4 T4
      cycle-1 Q2 refinement: "in-progress arc", "how many spiders",
      etc). For handoffs surfacing in top-K, classify staleness:
      arc-closed / arc-in-flight / stats-drifted / superseded /
      unknown. Deliverable = narrow list of handoffs recommended
      for DOC-POINTER-V1 stats-drift banner (Chris judgment; NOT
      per-file review of all 1061).

Pre-clustering signals consumed (parent §4 T4 + T3b §5.4 T5
workflow directive generalized):
  - T3b `/tmp/t3b_orphan_scan_out.json`: annotates each citing_doc
    with severity_class + severity + anchor/index/search reachability.
    A citation from an anchor-reachable canonical doc carries more
    weight than a citation from a search-only-reachable pack.
  - T2 `/tmp/t2_scan_out.json`: pre-computed handoff citation graph
    (via `ref_class=session` short-form + path-form file_cite
    resolves against `docs/handoffs/`). Load as canonical citation
    edge source; do NOT re-grep the entire corpus.

Anti-scope (parent §7 + S2836 arc-close deferral policy):
  - Does NOT walk 1061 handoff files for content quality.
  - Does NOT execute anchor / index / corpus edits.
  - Does NOT route `escalate_to_chris` rows mid-arc (accumulate to 2899).
  - Does NOT resolve arc-closed vs arc-in-flight classification
    for retrieval-harm sub-loop rows — that's the Chris judgment
    call, deferred.

Outputs `/tmp/t4_handoff_audit_out.json` for downstream §10.1 v1.1
YAML consumption.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_ROOT = REPO_ROOT / "docs"
HANDOFFS_DIR = DOCS_ROOT / "handoffs"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Pre-clustering inputs.
T2_INPUT = Path("/tmp/t2_scan_out.json")
T3B_INPUT = Path("/tmp/t3b_orphan_scan_out.json")

# Session-number chunk-ID reset boundary (per parent §4 T4 sub-loop
# (b) rationale). Pre-boundary handoffs may have fragment citations
# in the form `#K` that no longer resolve after any post-1143 corpus
# rebuild.
CHUNK_ID_RESET_BOUNDARY = 1143

# Probe queries for sub-loop (c). Parent §4 T4 cycle-1 Q2 refinement
# named two ("in-progress arc", "how many spiders"); extend with the
# common operational queries an operator would issue at session open.
PROBE_QUERIES = (
    "in-progress arc",
    "how many spiders",
    "how many agents",
    "current arc state",
    "recycle after merge",
    "playbook version",
    "where do I start",
    "canonical anchor",
    "session close cascade",
    "handoff citation",
)

# top-K depth for retrieval-harm sub-loop.
PROBE_TOP_K = 8

# Fragment-form spot-check sample size (parent §4 T4 sub-loop (b)).
FRAGMENT_SAMPLE_SIZE = 10


# ---------------------------------------------------------------------------
# Enumeration
# ---------------------------------------------------------------------------


HANDOFF_RE = re.compile(r"SESSION_(\d+)")


def enumerate_handoffs() -> list[Path]:
    """Return all `docs/handoffs/SESSION_*.md` files."""
    return sorted(HANDOFFS_DIR.glob("SESSION_*.md"))


def handoff_session_number(path: Path) -> int | None:
    m = HANDOFF_RE.match(path.name)
    if m:
        return int(m.group(1))
    return None


# ---------------------------------------------------------------------------
# Pre-clustering: T2 handoff citation graph + T3b citing-doc reachability
# ---------------------------------------------------------------------------


def load_t2_handoff_citation_edges() -> tuple[dict[int, set[str]], list[tuple[str, str, int, str]]]:
    """Extract handoff-target citation edges from T2 pre-computed refs.

    Returns:
      cited_session_num -> {citing_doc_paths...}
      list of (citing_doc, target_string, session_num, status) for broken edges
    """
    cited: dict[int, set[str]] = defaultdict(set)
    broken: list[tuple[str, str, int, str]] = []
    if not T2_INPUT.exists():
        return cited, broken
    d = json.loads(T2_INPUT.read_text())
    for row in d.get("results", []):
        citing = row.get("file") or ""
        for f in row.get("findings", []):
            ref_class = f.get("ref_class")
            target = f.get("target") or ""
            resolved = f.get("resolved") or ""
            status = f.get("status") or ""
            # session-form: "SESSION_NNN" short mention
            # path-form: "docs/handoffs/SESSION_NNN*.md" file citation
            matched = False
            for candidate in (target, resolved):
                if not candidate:
                    continue
                if "docs/handoffs/SESSION_" in candidate or (
                    ref_class == "session" and HANDOFF_RE.match(candidate)
                ):
                    m = HANDOFF_RE.search(candidate)
                    if m:
                        sess = int(m.group(1))
                        cited[sess].add(citing)
                        if status == "BROKEN_404":
                            broken.append((citing, candidate, sess, status))
                        matched = True
                        break
            if not matched:
                continue
    return cited, broken


def load_t3b_citing_doc_reachability() -> dict[str, dict]:
    """Return {file_path -> row-dict} from T3b scanner output."""
    reachability: dict[str, dict] = {}
    if not T3B_INPUT.exists():
        return reachability
    d = json.loads(T3B_INPUT.read_text())
    for row in d.get("results", []):
        fp = row.get("file_path")
        if fp:
            reachability[fp] = row
    return reachability


# ---------------------------------------------------------------------------
# Sub-loop (a): citation-graph + decay curve
# ---------------------------------------------------------------------------


def build_decay_curve(
    handoffs: list[Path],
    cited: dict[int, set[str]],
) -> dict:
    """500-session-bucket decay curve + all-handoff-summary."""
    handoff_sessions: set[int] = set()
    for h in handoffs:
        n = handoff_session_number(h)
        if n is not None:
            handoff_sessions.add(n)
    cited_sessions = set(cited.keys())

    bucket_total: dict[int, int] = defaultdict(int)
    bucket_cited: dict[int, int] = defaultdict(int)
    for s in handoff_sessions:
        b = (s // 500) * 500
        bucket_total[b] += 1
        if s in cited_sessions:
            bucket_cited[b] += 1

    buckets = []
    for b in sorted(bucket_total):
        buckets.append(
            {
                "bucket_min": b,
                "bucket_max": b + 499,
                "handoff_sessions": bucket_total[b],
                "cited_sessions": bucket_cited[b],
                "cited_fraction": round(bucket_cited[b] / bucket_total[b], 4) if bucket_total[b] else 0.0,
            }
        )

    uncited = handoff_sessions - cited_sessions
    return {
        "total_handoffs_on_disk": len(handoffs),
        "unique_handoff_session_numbers": len(handoff_sessions),
        "unique_cited_handoff_sessions": len(cited_sessions & handoff_sessions),
        "uncited_handoff_sessions": len(uncited),
        "uncited_fraction": round(len(uncited) / len(handoff_sessions), 4) if handoff_sessions else 0.0,
        "decay_curve_by_500_bucket": buckets,
    }


def citation_weight_by_citing_doc(
    cited: dict[int, set[str]],
    t3b_reachability: dict[str, dict],
) -> dict:
    """For each cited handoff, classify citing-doc(s) by T3b severity.

    Answers the question: are handoff citations concentrated from
    anchor-reachable canonical docs (strong evidence of live
    citation) or from search-only closed-arc packs (weaker)?
    """
    weight_hist: Counter[str] = Counter()
    citing_weight_by_session: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    unknown_citing = 0

    for sess, citing_docs in cited.items():
        for citing in citing_docs:
            row = t3b_reachability.get(citing)
            if row is None:
                weight_hist["citing_not_in_t3b_corpus"] += 1
                citing_weight_by_session[sess]["citing_not_in_t3b_corpus"] += 1
                unknown_citing += 1
                continue
            klass = row.get("severity_class", "unknown")
            weight_hist[klass] += 1
            citing_weight_by_session[sess][klass] += 1

    return {
        "citing_doc_severity_hist": dict(weight_hist),
        "citing_not_in_t3b_corpus": unknown_citing,
        # exclude the full per-session map from summary (only top-N later)
    }


# ---------------------------------------------------------------------------
# Sub-loop (b): fragment-citation spot-check
# ---------------------------------------------------------------------------


FRAGMENT_CITE_RE = re.compile(
    r"docs/handoffs/(SESSION_(\d+)[^\s\)`]*\.md)#([A-Za-z0-9_\-\.]+)"
)


def grep_fragment_citations() -> list[dict]:
    """Grep the corpus for handoff citations carrying URL fragments.

    Returns list of {citing_doc, cited_handoff, session, fragment}.
    Excludes citations FROM within `docs/handoffs/` (self-citations
    don't test post-1143 chunk-ID reset from the non-handoff corpus
    consumer perspective).
    """
    proc = subprocess.run(
        [
            "grep",
            "-rn",
            "--include=*.md",
            "-E",
            r"docs/handoffs/SESSION_[0-9]+[^)`\s]*\.md#[A-Za-z0-9_\-\.]+",
            "docs/",
            "CLAUDE.md",
            "00-START-NEXT-SESSION.md",
        ],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    edges: list[dict] = []
    for line in proc.stdout.splitlines():
        # rg-like line format: `path:lineno:match`
        parts = line.split(":", 2)
        if len(parts) < 3:
            continue
        citing_doc, lineno, snippet = parts[0], parts[1], parts[2]
        if citing_doc.startswith("docs/handoffs/"):
            continue  # exclude self-citations
        for m in FRAGMENT_CITE_RE.finditer(snippet):
            cited_handoff = m.group(1)
            session = int(m.group(2))
            fragment = m.group(3)
            edges.append(
                {
                    "citing_doc": citing_doc,
                    "citing_line": int(lineno) if lineno.isdigit() else None,
                    "cited_handoff": cited_handoff,
                    "cited_session": session,
                    "fragment": fragment,
                    "pre_boundary": session < CHUNK_ID_RESET_BOUNDARY,
                }
            )
    return edges


def check_fragment_resolves(cited_handoff: str, fragment: str) -> tuple[bool, str]:
    """Check whether the fragment target exists in the handoff file.

    For markdown, a `#section-anchor` fragment resolves to a
    `## Section anchor` heading (github-flavored auto-anchoring).
    For chunk-ID `#K123` style fragments (pre-1143 pattern), we
    check for the literal string in the file body.

    Returns (resolves_bool, resolution_kind).
    """
    handoff_path = DOCS_ROOT / "handoffs" / cited_handoff
    if not handoff_path.exists():
        return False, "handoff_file_missing"
    try:
        text = handoff_path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False, "handoff_read_error"

    # Chunk-ID style: `#K123` — post-1143 chunk-IDs are numeric-only after
    # embedding-corpus rebuilds. Check if literal fragment string appears.
    if fragment.startswith("K") and fragment[1:].isdigit():
        if fragment in text:
            return True, "chunk_id_present"
        return False, "chunk_id_absent"

    # Section-anchor style: `#section-name` — normalize to lower + dash;
    # check whether any heading normalizes to same fragment.
    heading_re = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
    for m in heading_re.finditer(text):
        heading = m.group(1).strip()
        # Github anchor normalization: lower, strip punctuation except -_, spaces -> dash
        normalized = re.sub(r"[^\w\s-]", "", heading.lower()).strip()
        normalized = re.sub(r"\s+", "-", normalized)
        if normalized == fragment.lower():
            return True, "section_heading_match"
    return False, "section_heading_absent"


def spot_check_fragments(edges: list[dict], sample_size: int) -> list[dict]:
    """Sample up to N fragment citations, check whether each resolves.

    Sampling strategy: prioritize pre-1143 boundary citations (post-1143
    chunk-ID reset risk); if fewer than sample_size, pad with random
    post-1143 fragments.
    """
    pre_boundary = [e for e in edges if e["pre_boundary"]]
    post_boundary = [e for e in edges if not e["pre_boundary"]]

    # Deterministic sampling: sort by (citing_doc, cited_session) + take head.
    pre_boundary.sort(key=lambda e: (e["citing_doc"], e["cited_session"]))
    post_boundary.sort(key=lambda e: (e["citing_doc"], e["cited_session"]))

    sample: list[dict] = []
    sample.extend(pre_boundary[: max(1, sample_size // 2)])
    remaining = sample_size - len(sample)
    if remaining > 0:
        sample.extend(post_boundary[:remaining])

    if len(sample) > sample_size:
        sample = sample[:sample_size]

    for entry in sample:
        resolves, kind = check_fragment_resolves(entry["cited_handoff"], entry["fragment"])
        entry["resolves"] = resolves
        entry["resolution_kind"] = kind

    return sample


# ---------------------------------------------------------------------------
# Sub-loop (c): retrieval-harm probe
# ---------------------------------------------------------------------------


def probe_search_docs(queries: tuple[str, ...], top_k: int) -> list[dict]:
    """Run search_embeddings for each probe query; return handoff hits.

    Returns list of {query, rank, file_path, session, score, intent_gate_name}
    for handoffs that surface in top_k. Non-handoff hits are excluded.
    """
    import django

    django.setup()
    from core.rag_integration import search_embeddings  # local import after setup

    hits: list[dict] = []
    for q in queries:
        try:
            results = search_embeddings(
                query=q,
                limit=top_k,
                similarity_threshold=0.30,
            )
        except Exception as e:
            hits.append(
                {
                    "query": q,
                    "error": str(e)[:200],
                }
            )
            continue
        for rank, r in enumerate(results, start=1):
            md = r.get("metadata") or {}
            fp = md.get("file_path") or ""
            if not fp.startswith("docs/handoffs/"):
                continue
            m = HANDOFF_RE.search(Path(fp).name)
            sess = int(m.group(1)) if m else None
            hits.append(
                {
                    "query": q,
                    "rank": rank,
                    "file_path": fp,
                    "session": sess,
                    "similarity": round(r.get("similarity_score", 0) or 0, 4),
                    "intent_gate_name": r.get("intent_gate_name"),
                }
            )
    return hits


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    out_path = Path("/tmp/t4_handoff_audit_out.json")
    for arg in sys.argv[1:]:
        if arg.startswith("--out="):
            out_path = Path(arg.split("=", 1)[1])

    print("[T4 scanner] enumerating handoffs...", file=sys.stderr)
    handoffs = enumerate_handoffs()
    print(f"[T4 scanner] {len(handoffs)} handoff files on disk", file=sys.stderr)

    print("[T4 scanner] loading T2 pre-computed citation graph...", file=sys.stderr)
    cited, broken = load_t2_handoff_citation_edges()
    print(
        f"[T4 scanner] {sum(len(v) for v in cited.values())} citations across "
        f"{len(cited)} unique handoff-sessions "
        f"({len(broken)} BROKEN_404 short-form)",
        file=sys.stderr,
    )

    print("[T4 scanner] loading T3b citing-doc reachability...", file=sys.stderr)
    t3b_reach = load_t3b_citing_doc_reachability()
    print(f"[T4 scanner] {len(t3b_reach)} T3b reachability rows loaded", file=sys.stderr)

    print("[T4 scanner] sub-loop (a): decay curve...", file=sys.stderr)
    decay = build_decay_curve(handoffs, cited)
    print(
        f"[T4 scanner]   uncited_fraction={decay['uncited_fraction']} "
        f"across {decay['unique_handoff_session_numbers']} unique sessions",
        file=sys.stderr,
    )

    print("[T4 scanner] sub-loop (a): citing-doc weight histogram...", file=sys.stderr)
    weights = citation_weight_by_citing_doc(cited, t3b_reach)
    print(f"[T4 scanner]   citing_doc_severity_hist={weights['citing_doc_severity_hist']}", file=sys.stderr)

    print("[T4 scanner] sub-loop (b): grepping fragment citations...", file=sys.stderr)
    frag_edges = grep_fragment_citations()
    print(f"[T4 scanner]   {len(frag_edges)} fragment-form citations (non-handoff-source)", file=sys.stderr)
    frag_sample = spot_check_fragments(frag_edges, FRAGMENT_SAMPLE_SIZE)
    frag_resolves = sum(1 for e in frag_sample if e.get("resolves"))
    print(
        f"[T4 scanner]   spot-check {len(frag_sample)} samples: "
        f"{frag_resolves} resolve, {len(frag_sample) - frag_resolves} broken",
        file=sys.stderr,
    )

    print(f"[T4 scanner] sub-loop (c): probing {len(PROBE_QUERIES)} queries...", file=sys.stderr)
    probe_hits = probe_search_docs(PROBE_QUERIES, PROBE_TOP_K)
    handoff_hits = [h for h in probe_hits if "file_path" in h]
    print(f"[T4 scanner]   {len(handoff_hits)} handoff-hits across probe queries", file=sys.stderr)

    payload = {
        "summary": {
            "corpus_size": len(handoffs),
            "sub_loop_a_decay_curve": decay,
            "sub_loop_a_citing_weight": weights,
            "sub_loop_a_broken_shortform_count": len(broken),
            "sub_loop_b_total_fragment_edges": len(frag_edges),
            "sub_loop_b_sample_size": len(frag_sample),
            "sub_loop_b_sample_resolves": frag_resolves,
            "sub_loop_b_sample_broken": len(frag_sample) - frag_resolves,
            "sub_loop_c_probe_queries": list(PROBE_QUERIES),
            "sub_loop_c_top_k": PROBE_TOP_K,
            "sub_loop_c_total_handoff_hits": len(handoff_hits),
            "sub_loop_c_unique_handoffs_in_topk": len(
                {h["file_path"] for h in handoff_hits if "file_path" in h}
            ),
        },
        "sub_loop_a_broken_shortform_citations": [
            {"citing_doc": c, "target": t, "session": s, "status": st}
            for c, t, s, st in broken
        ],
        "sub_loop_a_top_cited_handoffs": sorted(
            [
                {
                    "session": sess,
                    "citing_count": len(citing_docs),
                    "citing_docs": sorted(citing_docs),
                }
                for sess, citing_docs in cited.items()
            ],
            key=lambda r: -int(r["citing_count"] if isinstance(r["citing_count"], int) else 0),
        )[:25],
        "sub_loop_b_fragment_sample": frag_sample,
        "sub_loop_c_handoff_hits": handoff_hits,
    }

    out_path.write_text(json.dumps(payload, indent=2))
    print(f"[T4 scanner] wrote {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
