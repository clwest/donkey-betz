"""T5 reports+audits triage scanner (Group 2800 sixth child audit).

Classifies each in-scope file on parent §4 T5 four axes:
  (a) one_shot vs standing_reference
  (b) anchor-reachable vs orphan
  (c) content_stale vs still_valid
  (d) v1_v2_pointer_present

Consumes T3b reachability substrate + T4 handoff-adjacent banner signal
(load-only; does NOT re-derive per §5.4 T5 workflow directive).

Emits /tmp/t5_reports_audits_scan_out.json with per-file finding rows
consumable as §10.1 v1.1 YAML at audit-doc author time.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable

# --- Configuration ---------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
T3B_OUT = Path("/tmp/t3b_orphan_scan_out.json")
T4_OUT = Path("/tmp/t4_handoff_audit_out.json")
OUT_PATH = Path("/tmp/t5_reports_audits_scan_out.json")

# Corpus enumeration per parent §4 T5:
#   docs/audits/**                     (93 .md files; includes 19 untracked SESSION_819_*)
#   docs/audit-2026/**                 (15 .md files)
#   docs/audit/**                      (10 .md files)
#   docs/reports/**                    (33 .md files — cycle-2 Q3 STRENGTHEN)
#   docs/*_AUDIT.md                    (18 .md files — root-level anchor-linked)
# Total = 169 (parent §4 T5 said ~171; -2 drift at root-level count).

SUBDIRS_RECURSIVE = ["docs/audit-2026", "docs/audit", "docs/reports"]
SUBDIR_FLAT = "docs/audits"
DOCS_ROOT_GLOB = "docs/*_AUDIT.md"


# --- Axis (a) — one_shot vs standing_reference ------------------------------

ONE_SHOT_NAME_PATTERNS = [
    re.compile(r"^SESSION_\d+"),                    # SESSION_NNN_*
    re.compile(r"^\d{8}_\d{6}"),                    # timestamped 20260714_223131
    re.compile(r"^\d{4}-\d{2}-\d{2}"),              # dated 2026-04-20
    re.compile(r"_REPORT\.md$"),                     # *_REPORT.md
    re.compile(r"_ASSESSMENT\.md$"),                 # *_ASSESSMENT.md
    re.compile(r"_SNAPSHOT\.md$"),                   # *_SNAPSHOT.md
    re.compile(r"_STATUS\.md$"),                     # *_STATUS.md (session-scoped state readout)
    re.compile(r"_20\d{6}", re.IGNORECASE),          # embedded YYYYMMDD
]

STANDING_NAME_PATTERNS = [
    re.compile(r"^00-"),                             # 00-AUDIT-PLAN, 00-REVIEW-ORCHESTRATOR
    re.compile(r"_PLAN\.md$"),                       # *_PLAN.md
    re.compile(r"_PATTERN\.md$"),                    # *_PATTERN.md
    re.compile(r"_ORCHESTRATOR\.md$"),               # *_ORCHESTRATOR.md
    re.compile(r"^[A-Z_]+_AUDIT\.md$"),              # ADVISOR_AUDIT, BODY_SYSTEM_AUDIT etc.
    re.compile(r"^INDEX\.md$", re.IGNORECASE),       # INDEX
    re.compile(r"^README\.md$", re.IGNORECASE),      # README
    re.compile(r"CHECKLIST\.md$"),                   # *_CHECKLIST.md
    re.compile(r"^AUDIT_V\d+\.md$"),                 # AUDIT_V1.md / AUDIT_V2.md at docs/audit/
]


def classify_shape(path: str) -> str:
    """Return 'one_shot' | 'standing_reference' | 'ambiguous'."""
    name = Path(path).name
    one_shot_hit = any(p.search(name) for p in ONE_SHOT_NAME_PATTERNS)
    standing_hit = any(p.search(name) for p in STANDING_NAME_PATTERNS)
    if standing_hit and not one_shot_hit:
        return "standing_reference"
    if one_shot_hit and not standing_hit:
        return "one_shot"
    if one_shot_hit and standing_hit:  # e.g. STATUS + PLAN — pick standing bias
        return "ambiguous"
    return "ambiguous"


# --- Axis (b) — reachability via T3b ----------------------------------------

def classify_reach(t3b_row: dict | None) -> str:
    """Return 'multi_graph' | 'search_only' | 'anchor_only' | 'orphan' | 'not_in_t3b'."""
    if t3b_row is None:
        return "not_in_t3b"
    r_cmd = t3b_row.get("reachable_from_claude_md_anchor")
    r_idx = t3b_row.get("reachable_from_docs_index")
    r_src = t3b_row.get("reachable_from_search_corpus")
    if r_cmd and r_idx and r_src:
        return "multi_graph"
    if r_cmd or r_idx:
        return "anchor_only"
    if r_src and not (r_cmd or r_idx):
        return "search_only"
    return "orphan"


# --- Axis (c) — content_stale heuristics ------------------------------------

STALE_PHRASE_PATTERNS = [
    re.compile(r"IN[- ]PROGRESS", re.IGNORECASE),
    re.compile(r"^\s*(?:status|state):\s*(?:in[- ]progress|planning|planned|open)", re.IGNORECASE | re.MULTILINE),
    re.compile(r"TODO(?:\s*\(URGENT\))?", re.IGNORECASE),
    re.compile(r"NEXT STEPS?:", re.IGNORECASE),
]

SESSION_TAG_RE = re.compile(r"Session[_ -]?(\d{2,5})", re.IGNORECASE)
DATE_TAG_RE = re.compile(r"(20\d{2}[-_]?\d{2}[-_]?\d{2})")

# Stale-session threshold: files that claim state from pre-S2000 (older than
# the auth-enforcement arc era) OR that carry no session/date tag AND are
# session-shaped by name are candidate-stale. Threshold is Chris-tunable.
STALE_SESSION_THRESHOLD = 2500  # anything referencing < this in title is presumed stale


def classify_stale(path: Path, head: str, shape: str) -> tuple[str, str]:
    """Return (stale_kind, notes).

    stale_kind ∈ {'stale_pre_s2500', 'stale_in_progress_marker', 'still_valid', 'unclear'}
    """
    name = path.name

    # Session-tagged filename → oldest signal
    m_name = SESSION_TAG_RE.search(name)
    if m_name and shape == "one_shot":
        sess = int(m_name.group(1))
        if sess < STALE_SESSION_THRESHOLD:
            return "stale_pre_s2500", f"filename session tag S{sess}"

    # In-progress / TODO markers in head
    for p in STALE_PHRASE_PATTERNS:
        m = p.search(head)
        if m:
            return "stale_in_progress_marker", f"matched {p.pattern[:40]!r}"

    # Session tag inside head (frontmatter session: NNNN)
    m_head_sess = re.search(r"^session:\s*(\d+)", head, re.IGNORECASE | re.MULTILINE)
    if m_head_sess:
        sess = int(m_head_sess.group(1))
        if sess < STALE_SESSION_THRESHOLD and shape == "one_shot":
            return "stale_pre_s2500", f"frontmatter session S{sess}"

    if shape == "standing_reference":
        return "still_valid", "standing reference; content-freshness not axis-c load-bearing"

    return "unclear", "no stale signal + no still-valid signal"


# --- Axis (d) — V1/V2 pointer marker ----------------------------------------

V2_POINTER_RE = re.compile(r"DOC-POINTER-V2", re.MULTILINE)
V1_POINTER_RE = re.compile(r"DOC-POINTER-V1", re.MULTILINE)


def classify_pointer(head: str) -> str:
    """Return 'v2_pointer' | 'v1_pointer' | 'none'."""
    if V2_POINTER_RE.search(head):
        return "v2_pointer"
    if V1_POINTER_RE.search(head):
        return "v1_pointer"
    return "none"


# --- Recommended action derivation ------------------------------------------

def derive_action(shape: str, reach: str, stale: str, pointer: str) -> tuple[str, str]:
    """Return (recommended_action, severity) per parent §10.3 + §10.2.

    Anti-pattern (parent §4 T5): T5 is TRIAGE only — classify + recommend
    disposition. Actions are derived from axis combination; content quality
    is NOT walked per-file.
    """
    # Already has V1 or V2 pointer → already tells the right story
    # V1 = stats-drift banner (in-place); V2 = supersession/relocation.
    # Both satisfy axis (d) "existing pointer tells the right story."
    if pointer in ("v1_pointer", "v2_pointer"):
        return "keep_as_is", "P3"

    # Standing reference at anchor path → keep
    if shape == "standing_reference" and reach in ("multi_graph", "anchor_only"):
        if stale == "still_valid" or stale == "unclear":
            return "keep_as_is", "P3"
        return "escalate_to_chris", "P2"  # standing but stale — Chris judgment

    # One-shot session snapshot classifications
    if shape == "one_shot":
        # Old + orphan → archive candidate (Chris judgment)
        if stale == "stale_pre_s2500" and reach in ("search_only", "orphan"):
            return "escalate_to_chris", "P2"
        # Old + anchor-reachable → V2 retrofit candidate (Chris judgment)
        if stale == "stale_pre_s2500" and reach in ("multi_graph", "anchor_only"):
            return "escalate_to_chris", "P2"
        # In-progress marker on a session-scoped doc → likely superseded
        if stale == "stale_in_progress_marker":
            return "escalate_to_chris", "P2"
        # Recent one-shot with no pointer → keep (write-once historical value)
        if stale in ("still_valid", "unclear") and reach in ("multi_graph", "anchor_only"):
            return "keep_as_is", "P3"
        # Recent one-shot but search-only reachable — softer keep, note for review
        if reach == "search_only":
            return "escalate_to_chris", "P2"

    # Ambiguous shape → escalate
    return "escalate_to_chris", "P2"


# --- Content-stale derived-class mapping ------------------------------------

def finding_class(shape: str, reach: str, stale: str, pointer: str) -> str:
    """Map to §10.1 v1.1 finding_class taxonomy."""
    if pointer == "v2_pointer":
        return "superseded_untagged"  # already tagged, but keeps the class
    if stale in ("stale_pre_s2500", "stale_in_progress_marker"):
        return "superseded_untagged"
    if reach in ("search_only", "orphan"):
        return "orphan"
    return "ok"


# --- Corpus enumeration -----------------------------------------------------

def enumerate_corpus() -> list[str]:
    files: list[str] = []
    files += [str(p.relative_to(REPO_ROOT)) for p in (REPO_ROOT / SUBDIR_FLAT).glob("*.md")]
    for sub in SUBDIRS_RECURSIVE:
        base = REPO_ROOT / sub
        if base.exists():
            files += [str(p.relative_to(REPO_ROOT)) for p in base.rglob("*.md")]
    # docs/*_AUDIT.md (flat; excludes subdirs like docs/audits/)
    files += [
        str(p.relative_to(REPO_ROOT))
        for p in (REPO_ROOT / "docs").glob("*_AUDIT.md")
    ]
    return sorted(set(files))


# --- T3b + T4 substrate load ------------------------------------------------

def load_t3b_index() -> dict[str, dict]:
    if not T3B_OUT.exists():
        print(f"WARN: {T3B_OUT} missing — reachability signal unavailable", file=sys.stderr)
        return {}
    data = json.loads(T3B_OUT.read_text())
    return {row["file_path"]: row for row in data.get("results", [])}


def load_t4_banner_handoffs() -> set[str]:
    """T4 §2.5 banner-candidate handoff basenames — informational only for T5."""
    if not T4_OUT.exists():
        return set()
    data = json.loads(T4_OUT.read_text())
    hits = data.get("sub_loop_c_handoff_hits", [])
    return {h.get("handoff_basename") for h in hits if h.get("handoff_basename")}


# --- Scan driver ------------------------------------------------------------

def read_head(path: Path, n_bytes: int = 4096) -> str:
    try:
        return path.read_text(errors="replace")[:n_bytes]
    except OSError as exc:
        return f"<read-failed: {exc}>"


def scan() -> dict:
    corpus = enumerate_corpus()
    t3b = load_t3b_index()
    t4_banner = load_t4_banner_handoffs()

    results: list[dict] = []
    sev_counter: Counter = Counter()
    action_counter: Counter = Counter()
    class_counter: Counter = Counter()
    shape_counter: Counter = Counter()
    reach_counter: Counter = Counter()
    stale_counter: Counter = Counter()
    pointer_counter: Counter = Counter()
    banner_intersect = 0

    for rel in corpus:
        p = REPO_ROOT / rel
        head = read_head(p)
        shape = classify_shape(rel)
        t3b_row = t3b.get(rel)
        reach = classify_reach(t3b_row)
        stale, stale_note = classify_stale(p, head, shape)
        pointer = classify_pointer(head)
        action, severity = derive_action(shape, reach, stale, pointer)
        klass = finding_class(shape, reach, stale, pointer)

        basename = Path(rel).name
        t4_flag = basename in t4_banner
        if t4_flag:
            banner_intersect += 1

        results.append(
            {
                "file_path": rel,
                "shape": shape,
                "reach": reach,
                "stale": stale,
                "stale_note": stale_note,
                "pointer": pointer,
                "severity": severity,
                "finding_class": klass,
                "recommended_action": action,
                "t3b_severity_class": (t3b_row or {}).get("severity_class"),
                "t3b_recommended_action": (t3b_row or {}).get("recommended_action"),
                "t3b_search_only_kind": (t3b_row or {}).get("search_only_kind"),
                "t3b_t5_may_override": (t3b_row or {}).get("t5_may_override"),
                "t4_banner_adjacent": t4_flag,
                "subdir": rel.split("/", 2)[1] if rel.startswith("docs/") and "/" in rel[5:] else "docs_root",
            }
        )
        sev_counter[severity] += 1
        action_counter[action] += 1
        class_counter[klass] += 1
        shape_counter[shape] += 1
        reach_counter[reach] += 1
        stale_counter[stale] += 1
        pointer_counter[pointer] += 1

    # Subdir cross-tabs
    by_subdir_action: dict[str, Counter] = {}
    for r in results:
        by_subdir_action.setdefault(r["subdir"], Counter())[r["recommended_action"]] += 1

    summary = {
        "corpus_size": len(corpus),
        "by_severity": dict(sev_counter),
        "by_recommended_action": dict(action_counter),
        "by_finding_class": dict(class_counter),
        "by_shape_axis_a": dict(shape_counter),
        "by_reach_axis_b": dict(reach_counter),
        "by_stale_axis_c": dict(stale_counter),
        "by_pointer_axis_d": dict(pointer_counter),
        "by_subdir_action": {k: dict(v) for k, v in by_subdir_action.items()},
        "t4_banner_adjacent_count": banner_intersect,
        "t3b_coverage": sum(1 for r in results if r["t3b_severity_class"] is not None),
    }
    return {"summary": summary, "results": results}


def main(argv: Iterable[str]) -> int:
    out = scan()
    OUT_PATH.write_text(json.dumps(out, indent=2))
    s = out["summary"]
    print(f"[T5 scan] corpus_size = {s['corpus_size']}")
    print(f"[T5 scan] T3b coverage = {s['t3b_coverage']} / {s['corpus_size']}")
    print(f"[T5 scan] T4 banner-adjacent (handoff-basename intersection) = {s['t4_banner_adjacent_count']}")
    print(f"[T5 scan] by_severity = {s['by_severity']}")
    print(f"[T5 scan] by_recommended_action = {s['by_recommended_action']}")
    print(f"[T5 scan] by_finding_class = {s['by_finding_class']}")
    print(f"[T5 scan] by_shape_axis_a = {s['by_shape_axis_a']}")
    print(f"[T5 scan] by_reach_axis_b = {s['by_reach_axis_b']}")
    print(f"[T5 scan] by_stale_axis_c = {s['by_stale_axis_c']}")
    print(f"[T5 scan] by_pointer_axis_d = {s['by_pointer_axis_d']}")
    print(f"[T5 scan] by_subdir_action = {json.dumps(s['by_subdir_action'], indent=2)}")
    print(f"[T5 scan] wrote {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
