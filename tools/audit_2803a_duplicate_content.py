#!/usr/bin/env python3
"""
S2836 T3a duplicate-content audit scanner (Group 2800 child 2803a).

Scans in-scope /docs/ + root docs for near-duplicate content pairs using
token-shingling + inverted-index Jaccard. Emits top-K pair candidates for
manual severity review.

Method (per parent §4 T3a):
  1. Enumerate ~791 non-handoff in-scope files (same corpus as T2)
  2. Normalize text: strip frontmatter, strip fenced code blocks (optional),
     lowercase, collapse whitespace
  3. Extract 5-word overlapping token shingles as a set per file
  4. Build inverted index: shingle -> {file_idx}
  5. For each pair of files sharing >= 1 shingle, compute exact Jaccard
     similarity: |A intersection B| / |A union B|
  6. Consume T2's per-file RENAMED map (from /tmp/t2_scan_out.json) as a
     free pre-clustering signal: files sharing basename with high T2
     RENAMED weight are surface-flagged
  7. Emit top-K by Jaccard (default K=200) as JSON for manual review

Severity classification (per parent §4 T3a scope) is NOT applied by this
scanner — this is a candidate detector. Manual review classifies each pair
as:
  - identical
  - near-identical
  - partial-overlap-load-bearing-both
  - partial-overlap-consolidate-candidate

Anti-scope:
  - Does NOT walk handoff files (T4 territory)
  - Does NOT walk docs/archive/, docs/docs-pattern/, in-flight-arc children
  - Does NOT modify any file
  - Does NOT propose merges or deletions (classification only)
"""

from __future__ import annotations

import json
import re
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
    "docs/research/domains/docs_content_audit/",
)

ROOT_INCLUDE = ("CLAUDE.md", "00-START-NEXT-SESSION.md", "README.md")

SHINGLE_SIZE = 5
DEFAULT_TOP_K = 200
DEFAULT_MIN_JACCARD = 0.10
DEFAULT_MIN_FILE_BYTES = 0  # if >0, skip files below this size (V2 stub filter)

FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
TOKEN_RE = re.compile(r"[a-z0-9]+")


def is_in_scope(rel_path: str) -> bool:
    for pfx in EXCLUDE_DIR_PREFIXES:
        if rel_path.startswith(pfx):
            return False
    for marker in IN_FLIGHT_ARC_CHILD_PATH_MARKERS:
        if rel_path.startswith(marker):
            return False
    return rel_path.endswith(".md")


def enumerate_corpus(min_bytes: int = 0) -> list[Path]:
    files: list[Path] = []
    for md in DOCS_ROOT.rglob("*.md"):
        rel = str(md.relative_to(REPO_ROOT))
        if is_in_scope(rel):
            if min_bytes and md.stat().st_size < min_bytes:
                continue
            files.append(md)
    for name in ROOT_INCLUDE:
        p = REPO_ROOT / name
        if p.exists():
            files.append(p)
    return sorted(files)


def normalize_text(raw: str, strip_code: bool = True) -> str:
    text = FRONTMATTER_RE.sub("", raw)
    if strip_code:
        text = FENCED_CODE_RE.sub(" ", text)
    text = MD_LINK_RE.sub(r"\1", text)
    text = text.lower()
    return text


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text)


def shingle_set(tokens: list[str], k: int = SHINGLE_SIZE) -> set[str]:
    if len(tokens) < k:
        return {" ".join(tokens)} if tokens else set()
    return {" ".join(tokens[i : i + k]) for i in range(len(tokens) - k + 1)}


def load_t2_renamed_map(path: str = "/tmp/t2_scan_out.json") -> dict[str, set[str]]:
    """Load T2 RENAMED findings; return basename -> set of resolved-target paths.

    Per T2 §5.6 pre-clustering signal: files sharing basename with real
    duplicate candidates surface via T2's RENAMED classification.
    """
    p = Path(path)
    if not p.exists():
        return {}
    try:
        d = json.loads(p.read_text())
    except Exception:
        return {}
    basename_targets: dict[str, set[str]] = defaultdict(set)
    for row in d.get("results", []):
        for f in row.get("findings", []):
            if f.get("status") == "RENAMED":
                target = f.get("target") or ""
                resolved = f.get("resolved") or ""
                if not target or not resolved:
                    continue
                bn = Path(target).name
                basename_targets[bn].add(resolved)
    return dict(basename_targets)


def build_signatures(files: list[Path]) -> tuple[list[dict], list[set[str]]]:
    """Return (per-file metadata, per-file shingle sets)."""
    meta: list[dict] = []
    signatures: list[set[str]] = []
    for i, f in enumerate(files):
        try:
            raw = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = str(f.relative_to(REPO_ROOT))
        text = normalize_text(raw)
        tokens = tokenize(text)
        shingles = shingle_set(tokens)
        meta.append(
            {
                "idx": i,
                "path": rel,
                "basename": f.name,
                "token_count": len(tokens),
                "shingle_count": len(shingles),
                "size_bytes": len(raw),
            }
        )
        signatures.append(shingles)
    return meta, signatures


def find_candidate_pairs(
    signatures: list[set[str]], min_shared_shingles: int = 20
) -> dict[tuple[int, int], int]:
    """Inverted-index pass: shingle -> file_idx set; count shared shingles per pair.

    min_shared_shingles filters out pairs sharing only a handful of common
    shingles (e.g. boilerplate). Set low enough to catch partial-overlap
    but high enough to skip 1-token noise.
    """
    inv: dict[str, list[int]] = defaultdict(list)
    for i, sh in enumerate(signatures):
        for s in sh:
            inv[s].append(i)

    pair_counts: dict[tuple[int, int], int] = defaultdict(int)
    for shingle, indices in inv.items():
        if len(indices) < 2:
            continue
        # Skip shingles shared by >50% of corpus (boilerplate)
        if len(indices) > len(signatures) * 0.5:
            continue
        for a in range(len(indices)):
            for b in range(a + 1, len(indices)):
                i, j = indices[a], indices[b]
                if i > j:
                    i, j = j, i
                pair_counts[(i, j)] += 1

    return {pair: cnt for pair, cnt in pair_counts.items() if cnt >= min_shared_shingles}


def score_pairs(
    pair_counts: dict[tuple[int, int], int],
    signatures: list[set[str]],
    meta: list[dict],
    min_jaccard: float,
) -> list[dict]:
    results: list[dict] = []
    for (i, j), shared in pair_counts.items():
        a_size = len(signatures[i])
        b_size = len(signatures[j])
        union = a_size + b_size - shared
        if union == 0:
            continue
        jaccard = shared / union
        if jaccard < min_jaccard:
            continue
        # containment scores catch subset overlap
        containment_a = shared / a_size if a_size else 0.0
        containment_b = shared / b_size if b_size else 0.0
        results.append(
            {
                "a": meta[i]["path"],
                "b": meta[j]["path"],
                "shared_shingles": shared,
                "a_shingles": a_size,
                "b_shingles": b_size,
                "jaccard": round(jaccard, 4),
                "containment_a": round(containment_a, 4),
                "containment_b": round(containment_b, 4),
                "basename_match": meta[i]["basename"] == meta[j]["basename"],
                "a_bytes": meta[i]["size_bytes"],
                "b_bytes": meta[j]["size_bytes"],
            }
        )
    # sort by max of jaccard + containment_max (partial-overlap signal)
    def score(r):
        return max(r["jaccard"], r["containment_a"], r["containment_b"])
    results.sort(key=score, reverse=True)
    return results


def annotate_with_t2_map(
    results: list[dict], t2_basename_targets: dict[str, set[str]]
) -> list[dict]:
    """Flag pairs whose basenames appear in T2's RENAMED basename map."""
    for r in results:
        a_bn = Path(r["a"]).name
        b_bn = Path(r["b"]).name
        r["t2_renamed_signal"] = bool(
            t2_basename_targets.get(a_bn) or t2_basename_targets.get(b_bn)
        )
    return results


def summarize(results: list[dict], top_k: int, out_path: Path) -> dict:
    """Emit JSON output + histogram summary."""
    # bucket by similarity band
    buckets = {"identical (>=0.95)": 0, "near-identical (0.75-0.95)": 0,
               "high-partial (0.50-0.75)": 0, "moderate-partial (0.25-0.50)": 0,
               "low-partial (0.10-0.25)": 0}
    for r in results:
        s = max(r["jaccard"], r["containment_a"], r["containment_b"])
        if s >= 0.95:
            buckets["identical (>=0.95)"] += 1
        elif s >= 0.75:
            buckets["near-identical (0.75-0.95)"] += 1
        elif s >= 0.50:
            buckets["high-partial (0.50-0.75)"] += 1
        elif s >= 0.25:
            buckets["moderate-partial (0.25-0.50)"] += 1
        else:
            buckets["low-partial (0.10-0.25)"] += 1

    payload = {
        "corpus_size": None,  # filled by caller
        "total_pairs_found": len(results),
        "buckets": buckets,
        "top_k": top_k,
        "results": results[:top_k],
    }
    out_path.write_text(json.dumps(payload, indent=2))
    return payload


def main() -> None:
    top_k = DEFAULT_TOP_K
    min_jaccard = DEFAULT_MIN_JACCARD
    out_path = Path("/tmp/t3a_dup_scan_out.json")

    min_file_bytes = DEFAULT_MIN_FILE_BYTES
    for arg in sys.argv[1:]:
        if arg.startswith("--top-k="):
            top_k = int(arg.split("=", 1)[1])
        elif arg.startswith("--min-jaccard="):
            min_jaccard = float(arg.split("=", 1)[1])
        elif arg.startswith("--out="):
            out_path = Path(arg.split("=", 1)[1])
        elif arg.startswith("--min-file-bytes="):
            min_file_bytes = int(arg.split("=", 1)[1])

    print(f"[T3a scanner] enumerating corpus (min_file_bytes={min_file_bytes})...", file=sys.stderr)
    files = enumerate_corpus(min_bytes=min_file_bytes)
    print(f"[T3a scanner] {len(files)} in-scope files", file=sys.stderr)

    print(f"[T3a scanner] loading T2 RENAMED map from /tmp/t2_scan_out.json...", file=sys.stderr)
    t2_map = load_t2_renamed_map()
    print(f"[T3a scanner] T2 map has {len(t2_map)} basenames", file=sys.stderr)

    print(f"[T3a scanner] building shingle signatures (k={SHINGLE_SIZE})...", file=sys.stderr)
    meta, signatures = build_signatures(files)

    print(f"[T3a scanner] running inverted-index candidate pair search...", file=sys.stderr)
    pair_counts = find_candidate_pairs(signatures)
    print(f"[T3a scanner] {len(pair_counts)} candidate pairs with >=20 shared shingles", file=sys.stderr)

    print(f"[T3a scanner] scoring pairs (min_jaccard={min_jaccard})...", file=sys.stderr)
    results = score_pairs(pair_counts, signatures, meta, min_jaccard)
    print(f"[T3a scanner] {len(results)} pairs above jaccard threshold", file=sys.stderr)

    results = annotate_with_t2_map(results, t2_map)

    payload = summarize(results, top_k, out_path)
    payload["corpus_size"] = len(files)
    out_path.write_text(json.dumps(payload, indent=2))

    print(f"[T3a scanner] wrote {out_path}", file=sys.stderr)
    print(f"[T3a scanner] histogram:", file=sys.stderr)
    for k, v in payload["buckets"].items():
        print(f"  {k}: {v}", file=sys.stderr)


if __name__ == "__main__":
    main()
