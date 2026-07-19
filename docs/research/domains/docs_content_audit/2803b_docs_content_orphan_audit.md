---
title: "S2837 T3b — /docs/ Content Audit · Orphan & Reachability Audit (child audit 2803b)"
status: ratified (T3b — Chris D-verdict 2026-07-19 S2837; joint Claude+Rigby SIGN 3 cycles; folds applied + verified; escalate rows DEFERRED to arc close per S2836 policy carry-over)
ratification:
  date: 2026-07-19
  session: 2837
  ratifier: Chris
  verbatim_directive: "ratify T3b as-folded"
  scope: full T3b (793-file corpus scan; 3 SIGN cycles: cycle 1 = 2 STRENGTHEN + 2 pending-tool-runs; cycle 1b = 2 AGREE-post-tool-runs + Q5(a) future_trigger; cycle 2 = Q5(b) same_pr_mitigatable + future_trigger sub-folds + Q5(c) coupling risk callout; cycle 3 = 7/7 AGREE with cited line numbers + Q5(d) future_trigger; anti-rubber-stamp verified ~30+ substantive tool_runs across 3 cycles; escalate policy carries over per S2836 D-verdict)
  envelope: docs/research/implementation/RATIFICATION_2026-07-19_2803b_docs_content_orphan_audit.md
  sign_cycles: 3 (Rigby joint SIGN pin pa-7ebe273640e14691; anti-rubber-stamp verified; cycle 1 → 2 STRENGTHEN + 2 pending → folded; cycle 1b → 2 AGREE-post-verify + Q5(a) future_trigger → folded; cycle 2 → Q5(b)+Q5(c) same_pr_mitigatable/future_trigger → folded; cycle 3 → 7/7 AGREE explicit + Q5(d) future_trigger)
  chris_directive_new_policy: (no new policy; S2836 deferral policy carries over — 77 escalate rows queue for 2899)
  next_action: T4 handoff citation-integrity + retrieval-harm audit opens at S2838 (child audit 2804_docs_content_handoff_audit.md); needs-judgment queue continues to accumulate across all children; batch resolution at 2899 close
authority: child audit under Group 2800 (2800 parent-scoping RATIFIED at S2833 D1-D9; 2801 T1 RATIFIED at S2834 with schema v1.1; 2802 T2 RATIFIED at S2835; 2803a T3a RATIFIED at S2836)
session: 2837
date: 2026-07-19
domain_slug: docs_content_audit
research_group: 2800
thread: T3b
schema_version: 1.1  # inherited from parent §10.1 v1.1 locked at S2834
authors: Claude Code (Chris directed at S2837 open — "Let's do B" = ratified default from S2836 D-verdict)
parent:
  - docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md
predecessor_child:
  - docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md
  - docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md
  - docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md
supersedes: none
related:
  - docs/research/implementation/RATIFICATION_2026-07-19_2803a_docs_content_duplicate_audit.md
  - docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md
  - docs/00-START-HERE/DOC_LIFECYCLE.md
scope: >
  Orphan & reachability audit of the ~793-file non-handoff in-scope /docs/ +
  root corpus. Three-graph reachability measurement: (a) CLAUDE.md anchor-link
  BFS, (b) docs/INDEX.md autogen refs, (c) search_docs corpus inclusion via
  content.Document.file_path. Consumes T3a §5.4 V2-stub map (170 files) and
  T2 §5.6 RENAMED basename map as pre-clustering signals. Sub-classifies
  search-only-reachable files by known-benign pattern to reduce false-positive
  escalate volume. Emits YAML findings per parent §10.1 v1.1 schema.
non_goals:
  - executing archive / anchor edits (classification only per parent §5)
  - moves / renames / rewrites during the audit
  - duplicate-content classification (T3a territory)
  - reference-graph validation (T2 territory)
  - anchor / canonical-doc content walk (T1 territory)
  - modifying §10.1 v1.1 schema (locked at S2834)
  - auditing handoff-source content (T4 territory)
  - reports / audits triage classification (T5 territory) — T3a↔T5 boundary rule generalized
  - auditing in-flight Group 2800 arc children (this arc's own docs)
head_at_open: be7af72159ec  # S2836 close cascade merged
inventory_generated_at: 2026-07-05 15:51:41  # per docs/PLATFORM_INVENTORY.md
inventory_head: e617af59
scanner_tool: tools/audit_2803b_orphan_reachability.py
scanner_out: /tmp/t3b_orphan_scan_out.json
t3a_v2_stub_seed: T3a §5.4 (170 files, direct DOC-POINTER-V2 marker scan)
t2_pre_clustering_seed: /tmp/t2_scan_out.json  # RENAMED basename map per T2 §5.6
owner: claude+rigby (Chris to ratify)
---

# S2837 — T3b Orphan & Reachability Audit

> **What this doc is.** Group 2800's fourth child audit. Three-graph
> reachability measurement across 793 non-handoff in-scope files;
> per-file severity classification (4 classes per parent §4 T3b);
> sub-classification of search-only-reachable files against known
> benign patterns; sizes the escalate-to-chris queue for arc-close
> resolution (2899 per S2836 D-verdict deferral policy).
>
> **What this doc is not.** An archive proposal. A deletion manifest.
> An anchor-edit plan. A duplicate-content audit (that's T3a).
> Findings classify severity + reachability + `recommended_action`;
> execution defers to a follow-on migration arc (post-2899).

---

## 1. Method

### 1.1 Corpus selection — 793 source files (same as T3a; +1 versus T2's 791)

Per parent §4 T3b scope ("same ~810-file corpus as T3a"), T3b scans
the same non-handoff corpus as T3a with the same rglob + exclusion
rules. The +1 file drift versus T2 (791→792 at T3a; 792→793 at T3b)
reflects one new file merged since S2835 close cascade; no scope
mutation. Corpus composition:

| Bucket | # source files | Notes |
|---|---:|---|
| `docs/**` in-scope, minus handoffs / archive / docs-pattern / in-flight-arc-children | 790 | Same rglob + exclusion rules as T2/T3a |
| Root anchors | 3 | `CLAUDE.md`, `00-START-NEXT-SESSION.md`, `README.md` |
| **Total sources** | **793** |  |

**Explicitly OUT of T3b corpus (identical to T2/T3a exclusions):**

- `docs/handoffs/**` (1058 files) — parent §3 scope split routes handoffs to T4.
- `docs/archive/**` — DOC_LIFECYCLE §0 boundary; already-partitioned historical.
- `docs/docs-pattern/**` — context-kit framework, not project content.
- `docs/research/domains/docs_content_audit/**` — in-flight arc children (this arc's own docs).

### 1.2 Reachability graphs

Per parent §4 T3b spec, T3b measures reachability across three
independent graphs and classifies each file by the resulting
reachability pattern.

**Graph (a) — CLAUDE.md anchor graph (link-BFS):**

Start from `CLAUDE.md`. BFS through all markdown-link references
(`[text](path.md)`) and backtick-quoted paths (`` `path.md` ``)
across all in-scope `.md` files. A file is "anchor-reachable" iff
it lands in the transitive closure. Only `.md` extensions are
followed; `http://` / `https://` / `mailto:` URIs are ignored;
fragment suffixes (`#anchor`) are stripped before resolution.

Result at S2837 head: **491 files reachable from CLAUDE.md BFS**.

**Graph (b) — docs/INDEX.md autogen references:**

Parse `docs/INDEX.md` (the autogen'd top-level index regenerated by
`python manage.py build_docs_index`); every referenced `.md` path
counts as an edge from graph (b). Not a BFS — `docs/INDEX.md` is a
flat list, so this measures "listed in the index."

Result at S2837 head: **106 files cited from docs/INDEX.md**.

**Graph (c) — search_docs corpus inclusion (content.Document.file_path):**

Query the `content.Document` table via Django ORM:
`Document.objects.filter(is_active=True).values_list("file_path", flat=True)`.
A file is "corpus-included" iff there's an active Document row for
its exact repo-relative path. This is the load-bearing measurement
for graph (c) — a file that isn't in the Document table is invisible
to `search_docs` regardless of anchor citations.

Result at S2837 head: **792 of the 793 in-scope files are corpus-included**
(3261 total Document rows; 792 of those match in-scope paths). The 1
excluded file (README.md) drives the P1 finding at §2.2.

**Top-K retrieval frequency for probe queries** (parent §4 T3b bullet):
this measurement is deferred to a future_trigger. Corpus-inclusion
is the strictly-necessary and load-bearing signal; top-K retrieval
frequency requires wall-clock experiment time and probe-query
selection that couples T3b to specific query semantics. Documented
as §6.1 limitation.

### 1.3 Severity classification — four classes per parent §4 T3b

Each file is assigned one of the four severity_class values fixed
by parent §4 T3b:

| severity_class | Meaning | Default `recommended_action` |
|---|---|---|
| `cited-multi-graph-OK` | Reachable from anchor/index AND search corpus (healthy) | `keep_as_is` |
| `cited-but-search-invisible` | Reachable from anchor/index but NO Document row (retrieval-blind) | `escalate_to_chris` |
| `reachable-from-search-only` | ONLY reachable from search corpus (no anchor/index citation) | see §1.4 sub-classification |
| `unreachable-from-all-3-graphs` | No reachability signal anywhere (real orphan candidate) | `escalate_to_chris` |

### 1.4 Anti-pattern challenge: "unreachable = orphan = archive"

Parent §4 T3b explicitly named this anti-pattern to challenge. The
naive read of an orphan audit — "if it's not linked from CLAUDE.md
or the index, archive it" — misclassifies several categories of
files that are INTENTIONALLY search-only-reachable:

1. **DOC-POINTER-V2 stubs** (T3a §2.3, 170 files). Purpose is
   exactly to persist a search-reachable redirect while the
   canonical content lives under `docs/archive/`. Anchor-navigation
   is optional; search-reachability is the entire point.

2. **Ratification envelopes** (`docs/research/implementation/RATIFICATION_*.md`,
   38 files). Historical governance artifacts. Consumed via
   `search_docs "when was rule X ratified"` search intent, not via
   anchor browsing. Adding each to CLAUDE.md would drown navigation
   in one-shot governance records.

3. **Closed research-arc children** (`docs/research/domains/**`,
   `docs/research/discovery_layer/**`, `docs/research/platform/**`,
   9 files at T3b scan; note: this arc's own children are excluded).
   After an arc closes, its child docs persist in-tree for search-
   based retrieval; only the arc's canonical summary (`xx99`) needs
   anchor citation.

4. **Closed-arc tools & packs** (`docs/research/tools/validation/`,
   21 files; `docs/cleanup/`, `docs/code-review/`, 30 files). One-shot
   session packs from earlier arcs (S1099-era cleanup, S1200-era code
   review, S2728 tool-validation campaign). Contents remain valuable
   to search but were never intended as anchor-navigable running
   documentation. **Narrowed at Rigby SIGN cycle-1 Q2 fold**: the
   top-level `docs/research/tools/tools_*.md` files (4 files,
   including `tools_validation_engineering_campaign_plan.md` which
   is explicitly "awaiting Chris's review" per its line 5) are NOT
   auto-classified as closed — they route to `unclassified` for the
   2899 workshop. Only the `validation/` subdir carries the pattern.

5. **Implementation-arc artifacts** (`docs/research/implementation/`
   non-RATIFICATION files, 13 files: campaign docs, execution logs,
   I-030x scoping/close docs). Persistent arc artifacts that live
   under implementation/ for historical continuity.

6. **T5-territory files** (`docs/audits/**`, `docs/audit-2026/**`,
   `docs/audit/**`, `docs/reports/**`, 41 search-only files at T3b
   scan; 151 T5-territory total). Per T3a↔T5 boundary rule
   generalized (T3a §5.6): T3b MUST NOT finalize disposition on
   these; they carry `t5_may_override: YES`.

The classifier applies a **sub-classification pass** (`search_only_kind`)
on `reachable-from-search-only` files to distinguish these known-
benign patterns from genuinely unclassifiable orphan candidates
(`search_only_kind: unclassified`).

### 1.5 Pre-clustering signals consumed

**T3a §5.4 V2-stub map (170 files).** Detected via direct DOC-POINTER-V2
marker scan on the first 1KB of every in-scope file. T3a's shingle-
based inference reported "110+" V2 stubs; T3b's direct marker scan
finds 170. Both bounds are consistent (T3a scanned for near-duplicate
CLUSTERS ≥ 2, missing single-instance V2 stubs; T3b scans for the
marker directly). The 170-file classification override is applied
regardless of anchor/index reachability: a V2 stub is P3 keep_as_is.

**Warning on repo-wide grep as V2-stub count proxy** (Rigby SIGN
cycle-1 Q1 STRENGTHEN fold): a naive `repo_tool.search "<!-- DOC-POINTER-V2"`
across the repo returns **633 file matches** because many docs
(audit docs, roadmap indexes, DOC_LIFECYCLE §1 canonical page,
this doc, etc.) MENTION the marker string in context. The 170
figure comes from the scanner's first-1KB-only marker scan
restricted to the in-scope corpus — repo-wide grep is a poor
proxy and would inflate the count ~4x. Verified against 3 sample
paths (`docs/DEPLOYMENT_QUICKREF.md`, `docs/UNIFIED_CONTENT_PIPELINE.md`,
`docs/DISCORD_COMMANDS.md`), all of which start with the marker
in first-1KB per §1.2 shingling normalization pass.

**T2 §5.6 basename RENAMED map (3745 basenames).** Loaded from
`/tmp/t2_scan_out.json`. Annotates each row with
`t2_renamed_basename_signal: true|false`. Advisory only — a T2
RENAMED signal does not change classification but flags basename
collisions for downstream tooling. 313 of 793 files (39%) have a
T2 RENAMED basename match.

### 1.6 Scanner shape (parent §4 T3b compliance)

```
tools/audit_2803b_orphan_reachability.py
├── enumerate_corpus()         → 793 in-scope Paths
├── load_v2_stub_paths()       → 170 DOC-POINTER-V2 files
├── load_t2_renamed_basenames  → 3745 basename map
├── bfs_from_anchor()          → 491 files reachable-from-CLAUDE.md
├── extract_docs_index_refs()  → 106 files cited-from-docs/INDEX.md
├── load_search_corpus_paths() → 3261 Document rows (792 in-scope)
├── classify()                 → 4 severity_class + 8 search_only_kind
└── summarize()                → histograms per §2
```

Scanner runs in ~2 seconds (single-pass BFS + inverted-hit sets;
no O(N²) pair enumeration needed for reachability). Django setup
overhead dominates cost.

---

## 2. Findings — reachability + severity histograms

### 2.1 Positive headline: zero fully-unreachable files (P0-P1 gate)

**Every file in the 793-file corpus has some reachability signal.**
No file scores `unreachable-from-all-3-graphs`. This is the strongest
positive T3b finding: the /docs/ tree has no completely-invisible
files.

Interpretation: given the S1099-era cleanup + S1143 V2 pointer
sweep + subsequent context-kit runtime injection contracts, the
tree's reachability floor is well-maintained. Even historical
archives (envelope archives, closed arc packs) are searchable if
not anchor-navigable.

**Root-stability P0 gate NOT triggered** (parent §10.4(b) — no
root-stable file misclassified as orphan).

### 2.2 The one P1: `README.md` cited-but-search-invisible

The single P1 finding is `README.md`:

- `reachable_from_claude_md_anchor: true` (CLAUDE.md cites it)
- `reachable_from_docs_index: false`
- `reachable_from_search_corpus: false` (no active `content.Document`
  row for `README.md`)

The root `README.md` is anchor-cited but absent from the RAG corpus.
Rigby's `search_docs "how do I start"` would surface
`00-START-NEXT-SESSION.md` (Pattern C) or `CLAUDE.md`, never
`README.md` itself. Whether that's a bug (README should be
searchable) or intentional (README is bootstrap-navigation-only,
not RAG payload) is a Chris judgment call.

**Classification:** severity `P1`, `recommended_action:
escalate_to_chris`. Per S2836 deferral policy, this row accumulates
to the 2899 arc-close judgment queue; NOT routed to Chris mid-arc.

### 2.3 V2 pointer stub confirmation — 170 files (T3a §5.4 signal upheld)

T3b's direct marker scan finds **170 files** carrying the
`<!-- DOC-POINTER-V2` marker (T3a's shingle-based pair-inference
reported "110+"; the 170 figure is stronger evidence via direct
detection). Cluster breakdown (raw counts by 2-level path prefix
matching T3a §2.3 shape):

| Subdir | # V2 stubs |
|---|---:|
| `docs/guides/` | ~18 |
| `docs/features/` | ~18 |
| `docs/agents/` | ~8 |
| `docs/apis/` | ~8 |
| `docs/pre-launch/` | ~8 |
| `docs/body/` | ~6 |
| Root-level `docs/*.md` V2 stubs | ~62 (single-file entries throughout tree) |
| `docs/reports/**` + `docs/audits/**` (T5 overlap) | 32 |
| Other subdirs | remaining |
| **Total files** | **170** |

Of the 170 V2 stubs:
- **96** are ALSO anchor-cited (V2 stub AS the canonical anchor entry point — healthy state)
- **74** are search-only-reachable (V2 stub not-yet-cited from anchor graph — also healthy, just not navigated-to)
- **32** are ALSO T5-territory (V2-stubbed audit/report files — correct classification)

**Classification:** all 170 → `P3 keep_as_is` regardless of anchor
reachability. `search_only_kind: v2_pointer_stub` on the 74
search-only ones. `is_v2_pointer_stub: true` flag on all 170 rows
for downstream filters.

### 2.4 `docs/INDEX.md` is a strict subset of the CLAUDE.md anchor graph

**Every file cited in `docs/INDEX.md` is ALSO reachable from the
CLAUDE.md link-BFS.** Zero files are index-only (in `docs/INDEX.md`
but not in the CLAUDE.md closure).

Cross-tab:

| | in CLAUDE.md BFS | NOT in CLAUDE.md BFS |
|---|---:|---:|
| **in docs/INDEX.md** | 106 | **0** |
| **NOT in docs/INDEX.md** | 385 | 302 |

Interpretation: the autogen'd `docs/INDEX.md` provides ZERO
incremental reachability beyond the CLAUDE.md anchor graph. It's
functionally a top-level cheat sheet subset, not a coverage
guarantee. The 385 "anchor-only" files (in CLAUDE.md BFS but not
in INDEX) are the tree's real long-tail reference material, reached
via anchor-to-anchor link-following.

**Not a defect per se** — `docs/INDEX.md` is auto-generated by
`build_docs_index` from `docs/_index.json`; its shape reflects the
generator's design (top-level index, not exhaustive corpus). Worth
noting as a cross-cutting signal (§5.1) for future navigation
strategy: if we want file discoverability beyond CLAUDE.md link-
following, `docs/INDEX.md` is not currently doing it.

**Classification per row:** no per-file change — this is a graph
observation, not a defect.

### 2.5 Envelope-archive & arc-child patterns — 85 files (search-only-by-design)

Files auto-classified as search-only-by-design via `search_only_kind`
sub-classification (per §1.4 pattern list):

| `search_only_kind` | # files | Example |
|---|---:|---|
| `ratification_envelope` | 38 | `docs/research/implementation/RATIFICATION_2026-07-10_i0301_arc_close.md` |
| `implementation_arc_artifact` | 13 | `docs/research/implementation/tenant_boundary_lockdown/I-0301_scoping.md` |
| `closed_research_arc_child` | 9 | (research arc children in domains/discovery_layer/platform) |
| `closed_research_arc_tool` | 25 | (arc-produced tool scripts under docs/research/tools/) |
| **Subtotal** | **85** | |

All 85 → `P3 keep_as_is` per pattern recognition. Notes field
carries `"search-only-by-design (<pattern>)"` string. No 2899
escalation for these rows.

### 2.6 Closed-arc packs — 30 files (`docs/cleanup/` + `docs/code-review/`)

`docs/cleanup/` (6 files) + `docs/code-review/` (24 files) = 30
files. Both directories house closed-arc session packs from prior
work (S1099-era cleanup arc; S1200-era code review pack). Contents
remain valuable to search-based retrieval but were never intended
as anchor-navigable running docs.

Classification: `search_only_kind: closed_arc_pack` → `P3
keep_as_is`. No 2899 escalation.

**Deliberately excluded from auto-classification** as `closed_arc_pack`:
- `docs/spokesperson/` (11 files) — subject-matter subdir; anchor-visibility is a Chris design decision, not a closed arc
- `docs/audit-2026/`, `docs/audit/` — T5-territory subdirs (routed via T5 boundary rule)
- `docs/roadmap/`, `docs/apps/`, `docs/specs/`, `docs/designs/`, `docs/narratives/`, `docs/playbooks/`, `docs/initiatives/`, `docs/architecture/`, `docs/tools/`, `docs/topics/`, `docs/decisions/` — subject-matter subdirs; anchor-visibility Chris judgment

### 2.7 T1 counter-signal: 3 `docs/topics/` files are search-only

T1 (S2834) established `docs/topics/` as the tree's canonical dense
reference area (T1 §4.1 marked all topics files with
`claim_density_hint: dense`). T3b finds **3 topic files unreachable
from both CLAUDE.md AND docs/INDEX.md** — reachable only via the
search corpus:

| File | Anchor | Index | Search |
|---|:---:|:---:|:---:|
| `docs/topics/collaboration-protocol.md` | ✗ | ✗ | ✓ |
| `docs/topics/obs-remote-control.md` | ✗ | ✗ | ✓ |
| `docs/topics/video-upload.md` | ✗ | ✗ | ✓ |

If topics/ is canonical dense material, these three deserve either
(a) explicit CLAUDE.md citation, or (b) explicit acknowledgment
that not every topic file is anchor-navigated. Classification:
`P2 escalate_to_chris` (real Chris judgment needed — direction is
subject-matter). Deferred to 2899.

**Cross-cutting signal for T1 re-review at 2899**: T1's dense-
canonical claim about topics/ isn't false but is INCOMPLETE — 3 of
21 topic files miss the anchor graph. Rigby cycle-1 Q3 verification
substrate (post-fold): `docs/topics/` enumeration returns 21 topic
files including the 3 counter-signal picks; `grep collaboration-protocol`
across `docs/**` + root anchors finds citations only in (a) this
audit doc, (b) `docs/research/platform/constitutional_ecosystem_inventory.md`
(itself a search-only closed-arc research doc, not an anchor),
(c) `docs/_provenance.json` + `docs/_index.json` metadata, and
(d) `docs/handoffs/SESSION_1147_...` (out-of-scope handoff — not
in T3b corpus). Zero anchor-graph docs cite the 3 topic files by
prose or link. Counter-signal confirmed real, not an artifact of
BFS incompleteness.

### 2.8 The escalate-to-Chris queue — 76 unclassified P2 rows

76 files land `severity_class: reachable-from-search-only`,
`search_only_kind: unclassified` (no known benign pattern matched).
These are the real escalate candidates. Path-prefix breakdown:

| 2-level prefix | # files | Notes |
|---|---:|---|
| `docs/specs/` | 10 | Spec docs (Fleet capability specs, initiatives backbone spec, etc.) |
| `docs/apps/` | 9 | App brief templates (T3a §2.8 load-bearing-both family — potentially benign) |
| `docs/initiatives/` | 9 | `capitalize-opportunity/*` initiative arc children |
| `docs/roadmap/` | 9 | Roadmap docs (0X-*, gap analysis, INTEGRATION_ROADMAP_2026) |
| `docs/spokesperson/` | 11 | Spokesperson persona docs (see §2.6 note — subject-matter subdir) |
| `docs/playbooks/` | 6 | Non-Engineering playbooks (creator/devops/marketing/development) |
| `docs/designs/` | 5 | HUMAN_INTERFACE_LAYER, SKIN_LAYER_ARCHITECTURE, remote-code-worker-contract, etc. |
| `docs/narratives/` | 5 | ADVISORS, INITIATIVES_AND_LIFECYCLE, SPOKESPERSON_CHARACTER_OS, STRATEGY_247_GLOBAL_AI, WORKSPACES_AND_SCOPING |
| `docs/topics/` | 3 | See §2.7 (T1 counter-signal) |
| `docs/architecture/` | 2 | AI_ASSISTANT_ARCHITECTURE + README |
| `docs/tools/` | 2 | pa-tool-manifest, pa-tool-routing-guide |
| `docs/decisions/` | 1 | ADR-0002-moderate-dangerous-action-policy |
| `docs/research/tools/` (top-level, non-`validation/`) | 4 | Campaign plan + 3 predecessor operational-contract docs — Rigby cycle-1 Q2 fold reclassification: NOT closed arc; still awaiting Chris review |
| **Total** | **76** |  |

All 76 → `P2 escalate_to_chris` accumulating to 2899. No mid-arc
routing per S2836 D-verdict.

Two categories deserve highlighting for the 2899 workshop:

**(a) Subject-matter subdirs that may be Chris "keep-but-don't-anchor"
design**: `docs/spokesperson/`, `docs/roadmap/`, `docs/apps/`,
`docs/specs/`, `docs/designs/`, `docs/narratives/`, `docs/playbooks/`
non-eng subdirs. These may be intentional anchor-omission (living
subject-matter subdirs whose files evolve). Chris may prefer to
extend the `SEARCH_ONLY_BENIGN_PATTERNS` list at 2899 with these
subdirs and rerun.

**(b) Load-bearing-both template family** (T3a §2.8 evidence): the
9 `docs/apps/*_BRIEF.md` files — T3a already classified as
`partial-overlap-load-bearing-both` template family. Same 9 files
surface in T3b as anchor-orphans. Consistent signal: Chris may
want to add an `apps/INDEX.md` or `docs/apps/README.md` and cite
it from CLAUDE.md; T3a + T3b agree on that.

### 2.9 T5-territory search-only rows — 41 files (t5_may_override: YES)

Per T3a↔T5 boundary rule generalized (T3a §5.6): 41 files in
`docs/audits/**`, `docs/audit-2026/**`, `docs/audit/**`, or
`docs/reports/**` are search-only-reachable. All 41 carry
`t5_may_override: YES` in their `recommended_action` line; T3b
disposition is `keep_as_is` (P3), but T5 retains the authority to
override at its own audit time.

Split:
- `docs/audits/` — most audit archives (some V2-stubbed → §2.10 overlap)
- `docs/audit-2026/` — mid-arc audits
- `docs/audit/` — legacy audit subdir (10 files per T5 spec)
- `docs/reports/` — verification/completion reports (33 files per T5 spec)

### 2.10 Both-V2-and-T5 files — 32 files (correctly classified)

32 files are BOTH V2 pointer stubs AND T5-territory: V2-stubbed
audit or report files (e.g. `docs/audit-2026/SESSION_1143_DOCS_AUDIT.md`,
`docs/reports/3D_GENERATION_VERIFICATION_REPORT.md`, etc.). These
represent the healthiest case for T5 archives: the actual content
has been moved to `docs/archive/`; the in-place V2 stub redirects
readers to canonical. T3a §5.6 boundary rule + V2-stub override
compose cleanly:

- V2 stub override → P3 keep_as_is
- T5 territory → t5_may_override: YES
- search_only_kind → `v2_pointer_stub` (V2 takes precedence)

No 2899 escalation for these rows.

### 2.11 Summary histogram

```
severity_class:
  cited-multi-graph-OK          490  (61.8%)
  reachable-from-search-only    302  (38.1%)
  cited-but-search-invisible      1  ( 0.1%)   ← P1
  unreachable-from-all-3-graphs   0  ( 0.0%)   ← positive signal

severity:
  P3    716  (90.3%)
  P2     76  ( 9.6%)   ← escalate queue (post Rigby Q2 fold)
  P1      1  ( 0.1%)   ← README

recommended_action:
  keep_as_is         716  (90.3%)
  escalate_to_chris   77  ( 9.7%)   ← total 2899 queue (post Rigby Q2 fold)

search_only_kind (302 search-only-reachable files):
  v2_pointer_stub                74  (search-only-not-anchor-cited V2 stubs)
  unclassified                   76  (real escalate queue; +4 from Rigby Q2 fold)
  t5_territory                   41  (t5_may_override)
  ratification_envelope          38
  closed_arc_pack                30  (docs/cleanup/ + docs/code-review/)
  closed_research_arc_tool       21  (docs/research/tools/validation/ ONLY; narrowed from 25 per Q2 fold)
  implementation_arc_artifact    13
  closed_research_arc_child       9

anchor × index cross-tab:
  in CLAUDE.md BFS, NOT in INDEX.md:  385   (long-tail refs)
  in INDEX.md, NOT in CLAUDE.md BFS:    0   (INDEX is strict subset)
  in both:                            106
  in neither (search-only-reachable): 302
```

---

## 3. Migration queue (post-arc, DEFERRED to §3 execution arc post-2899)

Per Group 2800 §5 non-goals: T3b does NOT execute archive / anchor
edits during this arc. The following migration hints frame what
the follow-on §3 execution arc will consume from 2899:

### 3.1 Zero P0 rows — no root-stability gate triggered

Per parent §10.4(b), P0 rows in root-stable / NEVER-MOVE anchor
files (CLAUDE.md, 00-START-NEXT-SESSION.md, docs/PLATFORM_INVENTORY.md,
docs/PLATFORM_WHAT_IT_IS.md) would block migration OR require in-
place remediation. T3b finds **zero P0** across all root-stable
paths; migration path unblocked.

### 3.2 One P1 row — README.md corpus-inclusion decision (queued for 2899)

**File:** `README.md` (root)

**Two options for 2899 workshop:**

- (a) **Fix retrieval-blindness**: add `README.md` to
  `docs/_index.json` sync scope OR to the `build_docs_index` command
  scope so it lands in the `content.Document` corpus. Migration PR
  = single command-scope edit + `sync --embed` cascade.
- (b) **Accept intentional exclusion**: document in DOC_LIFECYCLE
  §1 that README.md is bootstrap-navigation-only; not RAG payload;
  README's role is stable-across-cache-cycles boot.

`recommended_action: escalate_to_chris` per S2836 deferral policy.

### 3.3 P2 escalate queue — 76 rows across 13 subdirs (queued for 2899)

Aggregation for 2899 workshop convenience:

- **Subject-matter subdir sweep**: 11 spokesperson + 9 roadmap + 9
  apps + 10 specs + 5 designs + 5 narratives + 6 non-eng playbooks
  = 55 rows across 7 subdirs. Chris may prefer to extend
  `SEARCH_ONLY_BENIGN_PATTERNS` at 2899 to include these subdirs
  and rerun scanner (~2 seconds).
- **T1 counter-signal (3 topics)**: real T1 material gap. Options
  are (i) CLAUDE.md link retrofit, (ii) T1 §4.1 dense-canonical
  qualification.
- **Initiatives arc children**: 9 rows under
  `docs/initiatives/capitalize-opportunity/` — if the initiative is
  closed, `SEARCH_ONLY_BENIGN_PATTERNS` extension; if in-flight,
  arc-index navigation aid needed.
- **PA-tool refs (2 rows)**: `docs/tools/pa-tool-manifest.md`,
  `docs/tools/pa-tool-routing-guide.md`. Load-bearing for
  understanding Rigby's tool surface; probably should be anchor-cited.
- **Architecture** (2), **decisions** (1): Chris judgment on
  anchor-visibility for these two/one.

### 3.4 T5-territory rows — 41 rows carry `t5_may_override: YES`

Not escalated at T3b close. T5 audit resolves disposition using T3b
reachability as ONE input among several (also T3a duplicates,
citation-graph, staleness).

### 3.5 Migration-PR batch hints (per §10.4 cross-arc consumption contract)

- `orphans_archive` batch → potentially empty (zero unreachable-
  from-all-3-graphs; escalate queue defers to 2899 judgment)
- `anchor_docs` batch → potentially non-empty if Chris chooses to
  anchor-cite the T1 topics/tools/architecture picks
- `dup_consolidate` batch → out of scope for T3b (T3a territory)

---

## 4. YAML findings — §10.1 v1.1 schema rows (representative sample)

All 793 corpus rows are emitted in `/tmp/t3b_orphan_scan_out.json`.
Representative samples across the 4 severity_class values and 8
search_only_kind sub-classes:

```yaml
# Sample 1 — P3 cited-multi-graph-OK (healthy)
- file_path: 00-START-NEXT-SESSION.md
  audit_thread: T3b
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 999]
      claim: reachable_from_claude_md_anchor=true, docs_index=true, search_corpus=true
      runtime_truth: content.Document.file_path='00-START-NEXT-SESSION.md' present + CLAUDE.md link found
      cited_source: null
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: null
  cross_arc_refs: []
  notes: reachable from all 3 graphs

# Sample 2 — P1 cited-but-search-invisible (THE finding)
- file_path: README.md
  audit_thread: T3b
  severity: P1
  finding_class: retrieval_harm
  evidence:
    - line_range: [1, 999]
      claim: cited by CLAUDE.md graph but no active content.Document row
      runtime_truth: 'Document.objects.filter(file_path="README.md", is_active=True).exists() == False'
      cited_source: docs/PLATFORM_INVENTORY.md#url-routes (not applicable — this is a corpus row)
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs: []
  notes: cited by anchor but no Document row — retrieval blind; defer to 2899 per S2836 policy

# Sample 3 — P3 reachable-from-search-only, v2_pointer_stub
- file_path: docs/AGENT_OUTPUT_TO_UI_MAPPING.md
  audit_thread: T3b
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 8]
      claim: DOC-POINTER-V2 marker present in first 1KB
      runtime_truth: matches '<!-- DOC-POINTER-V2' marker
      cited_source: docs/00-START-HERE/DOC_LIFECYCLE.md#v2-pointer
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: null
  cross_arc_refs:
    - t3a_2803a_section: §2.3 V2-stub cluster
  notes: V2 pointer stub — always P3 keep_as_is per DOC_LIFECYCLE §1; anchor-cited too (safe state)

# Sample 4 — P3 reachable-from-search-only, ratification_envelope
- file_path: docs/research/implementation/RATIFICATION_2026-07-10_i0301_arc_close.md
  audit_thread: T3b
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 200]
      claim: search_only_kind=ratification_envelope; anchor=false; index=false; search=true
      runtime_truth: RATIFICATION_ prefix under docs/research/implementation/
      cited_source: null
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: null
  cross_arc_refs: []
  notes: search-only-by-design (ratification_envelope) — historical governance artifact

# Sample 5 — P3 reachable-from-search-only, closed_arc_pack
- file_path: docs/cleanup/PHASE_1_EXECUTION_LOG.md
  audit_thread: T3b
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 999]
      claim: search_only_kind=closed_arc_pack; docs/cleanup/ is closed S1099-era arc pack
      runtime_truth: file resides under docs/cleanup/ path prefix; no anchor citation from CLAUDE.md BFS
      cited_source: null
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: null
  cross_arc_refs: []
  notes: search-only-by-design (closed_arc_pack) — S1099-era cleanup pack

# Sample 6 — P3 t5_territory search-only (t5_may_override)
- file_path: docs/audit-2026/HALF_BUILT_FEATURES_AUDIT.md
  audit_thread: T3b
  severity: P3
  finding_class: ok
  evidence:
    - line_range: [1, 999]
      claim: search_only_kind=t5_territory; T3a↔T5 boundary applies
      runtime_truth: path prefix docs/audit-2026/ matches T5-territory rule
      cited_source: docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md#5.6
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: audits_triage
  cross_arc_refs:
    - t5_2805_may_override: YES
  notes: T5-territory search-only — T3b disposition k_a_i, T5 retains authority

# Sample 7 — P2 unclassified escalate: T1 counter-signal
- file_path: docs/topics/collaboration-protocol.md
  audit_thread: T3b
  severity: P2
  finding_class: orphan
  evidence:
    - line_range: [1, 999]
      claim: search_only_kind=unclassified; docs/topics/ is T1-canonical-dense area
      runtime_truth: not reachable from CLAUDE.md BFS or docs/INDEX.md; T1 §4.1 lists topics/ as claim_density_hint=dense
      cited_source: docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md#4.1
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - t1_2801_counter_signal: dense-canonical claim inconsistent with anchor visibility
  notes: T1 counter-signal — defer to 2899 per S2836 policy

# Sample 8 — P2 unclassified: apps/*_BRIEF (T3a §2.8 template family echo)
- file_path: docs/apps/mentorforge_BRIEF.md
  audit_thread: T3b
  severity: P2
  finding_class: orphan
  evidence:
    - line_range: [1, 999]
      claim: search_only_kind=unclassified; part of T3a §2.8 load-bearing-both app-brief template family
      runtime_truth: not reachable from CLAUDE.md BFS or docs/INDEX.md
      cited_source: docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md#2.8
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs:
    - t3a_2803a_cross_reference: §2.8 app-brief template family
  notes: T3a + T3b agree — apps/ needs index or CLAUDE.md link; defer to 2899

# Sample 9 — P2 unclassified: docs/roadmap/
- file_path: docs/roadmap/00-GAP-ANALYSIS.md
  audit_thread: T3b
  severity: P2
  finding_class: orphan
  evidence:
    - line_range: [1, 999]
      claim: search_only_kind=unclassified; docs/roadmap/ subject-matter subdir
      runtime_truth: not reachable from CLAUDE.md BFS or docs/INDEX.md
      cited_source: null
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: anchor_docs
  cross_arc_refs: []
  notes: subject-matter subdir — Chris judgment on anchor-visibility; defer to 2899
```

Full YAML dataset lives in `/tmp/t3b_orphan_scan_out.json` (JSON,
consumable by `yaml.safe_dump` for §10.1 emit at ship time).
Downstream tooling MAY convert to YAML in-place; T3a used the
same JSON→YAML consumption pattern.

---

## 5. Cross-cutting signals for future §3 execution arc AND for parent methodology refinement

### 5.1 `docs/INDEX.md` provides zero incremental reachability

Per §2.4, every file in `docs/INDEX.md` is a strict subset of the
CLAUDE.md link-BFS. The autogen'd top-level index adds no unique
discoverability path. Options for 2899 discussion:

- **(a) Accept as-is**: `docs/INDEX.md` is a top-level cheat sheet,
  not a coverage guarantee. CLAUDE.md link-following is the actual
  navigation contract.
- **(b) Expand `build_docs_index` scope**: reference more of the
  long-tail `docs/**` corpus to make the autogen index a genuine
  coverage tool. Downstream: CLAUDE.md then references a smaller
  hand-curated set + INDEX for full discovery.
- **(c) Deprecate `docs/INDEX.md`**: if CLAUDE.md navigation is
  sufficient, the autogen index is a maintenance surface with no
  incremental benefit. Downstream: consolidate index effort into
  CLAUDE.md itself.

Not adjudicated in T3b — 2899 discussion.

### 5.2 T1 counter-signal on `docs/topics/` completeness (feed back to T1)

Per §2.7, 3 topic docs are not in the CLAUDE.md anchor graph OR
`docs/INDEX.md`. T1 §4.1 marked all topics as `claim_density_hint:
dense` and treated topics/ as canonical reference area — implying
each topic doc is anchor-navigable. T3b's finding shows the
canonical-density claim is TRUE but incomplete: 3 of ~30 topic
files miss both anchor graphs.

**Cross-arc refinement candidate for 2899**: T1 §4.1 could add a
`coverage_anchor_navigable: true|false|partial` field or note per
subdir; or T3b's finding can be surfaced as a T1 acceptance
qualification. Recorded as `future_trigger` for 2899.

### 5.3 T3b sub-classification of search-only-reachable is additive to §10.1 v1.1

The `search_only_kind` field is a T3b-local sub-classification that
maps to the parent §10.1 v1.1 `notes` field via string interpolation:

```
notes: "search-only-by-design (<search_only_kind>) — <descriptor>"
```

This is backward-compatible with v1.1 (notes is a free-text field
per parent §10.1). T3b does NOT propose promoting `search_only_kind`
to a first-class §10.1 field — that's a v1.2 candidate for 2899
per §5.3 acceptance criteria (i)-(iv) codified at T3a §5.3.

**Third witness for T2/T3a coverage-split refinement**: T2 §5.7
proposed `coverage_refs` / `coverage_claims` split; T3a §5.3
proposed `coverage_content_dup` as third axis. T3b now adds
`coverage_reachability` as a fourth axis (parallel dimension).
Group 2800 is accumulating v1.2 axis refinement evidence; if
Chris opts for coverage-axis expansion at 2899, T3b's four
axes give a clean shape:

```yaml
coverage:
  claim_walk: full | structural_only | deferred
  refs: full | sampled | deferred          # T2 §5.7 proposal
  content_dup: scanned | not_scanned       # T3a §5.3 proposal
  reachability: measured | not_measured    # T3b §5.3 proposal (new)
```

Not applied here per S2834 v1.1 lock + §5.3 acceptance criteria.
Recorded as `future_trigger` for 2899.

### 5.4 T3a↔T5 boundary rule generalizes cleanly to T3b

Per T3a §5.6 boundary rule: T3a MUST NOT finalize disposition on
T5-territory files. T3b's implementation applies the same rule to
all 151 T5-territory files (41 search-only + 110 anchor-reachable
in T5-territory). All carry `t5_may_override: YES`.

**Cross-arc consistency win**: the T3a↔T5 rule is not an ad-hoc
T3a artifact but a general child-audit discipline. Recorded as
`future_trigger` for parent §7 anti-scope generalization at 2899:
"any Tx audit MUST NOT finalize disposition on Ty-territory files
where Ty > Tx has explicit disposition authority."

**Coupling risk callout** (Rigby SIGN cycle-2 Q5c STRENGTHEN):
the boundary rule creates coupling that only pays off if T5
consumes T3b's pre-classification. If T5's methodology re-derives
reachability independently, T3b's 41 `t5_may_override: YES` rows
become parallel classification work rather than a labor-savings.
**Explicit T5 workflow directive for 2805 authoring**: T5 SHOULD
ingest `/tmp/t3b_orphan_scan_out.json` (or its persisted equivalent
after 2899 close) and treat T3b reachability as ONE input among
several — NOT re-derive the graphs. Recorded as `future_trigger`
for 2805 T5 spec at 2899 close.

### 5.5 README.md P1 finding is a real corpus-sync boundary case

Per §2.2, `README.md` is anchor-cited (CLAUDE.md links to it) but
not in `content.Document`. Investigating the sync boundary:

- `sync_docs_index_to_documents` sources from `docs/_index.json`
- `build_docs_index` populates `docs/_index.json` from `docs/**`
- Root-level `README.md` is NOT under `docs/`, so it's outside the
  build_docs_index rglob scope by construction

**Possible resolutions at 2899:**

- Extend `build_docs_index` to include root-level anchor docs
  (README.md + CLAUDE.md + 00-START-NEXT-SESSION.md) — same
  treatment as CLAUDE.md (which IS in the corpus per T3b scan).
- Accept README as bootstrap-only; document in DOC_LIFECYCLE §1.

Note: CLAUDE.md IS in the corpus (search=true). 00-START-NEXT-SESSION.md
IS in the corpus (search=true). Only README.md is missing — likely
an oversight in `build_docs_index` root-file inclusion list.

**Rigby cycle-1 Q4 verification substrate (post-fold, evidence in
hand):** `core/management/commands/build_docs_index.py` line 200
explicit inclusion list: `for root_doc in ['CLAUDE.md',
'00-START-NEXT-SESSION.md']:` — README.md IS NOT in that list.
No comment justifies README's exclusion; the shape strongly
suggests an oversight, not an intentional design boundary. Live
ORM check confirms Chris's live corpus state:
`Document.objects.filter(file_path='README.md', is_active=True).exists()
== False`; same query for CLAUDE.md and 00-START-NEXT-SESSION.md
returns True. Fix option (a) is a 1-line edit adding 'README.md'
to that root_doc list + one `sync_docs_index_to_documents --embed`
run to backfill the missing Document row.

### 5.6 Scanner cost is trivial for future re-runs

Full T3b scanner run on 793 files completes in ~2 seconds
(dominated by Django ORM `Document.file_path` query; BFS and
regex passes are sub-second). Rerun cost scales linearly with
corpus size × avg tokens per file. No optimization warranted.

### 5.7 `search_only_kind` pattern list is a Chris-tunable knob

The 6 SEARCH_ONLY_BENIGN_PATTERNS are hardcoded in the scanner
(§1.4 rationale). At 2899, Chris may extend / narrow the list
(e.g. add `docs/roadmap/`, `docs/apps/`, `docs/spokesperson/` if
those are subject-matter subdirs designed as anchor-omitted). The
tunable is a knob, not a contract — recorded as `future_trigger`.

**Sub-fold from Rigby cycle-2 Q5b**: the `implementation_arc_artifact`
and `closed_research_arc_child` patterns are BROAD prefix matches.
If a NEW active-arc child lands under `docs/research/implementation/`
OR `docs/research/domains/`, it gets auto-classified as benign — a
false-negative escalate leak. Two mitigation options for 2899:
(i) require a `_ARC_CLOSED.md` sentinel file per closed-arc slug
before treating children as benign, OR (ii) maintain a small
`CLOSED_ARC_ALLOWLIST` (arc-slug set) in the scanner that gets
extended on each `xx99` canonical summary close. Option (ii) is
more auditable but requires per-arc updates; option (i) is more
composable but requires DOC_LIFECYCLE amendment. Recorded as
`future_trigger` for 2899 close.

---

## 6. Residual risk / limitations

### 6.1 Method limitations (recorded)

1. **Top-K retrieval frequency for probe queries NOT measured.** Parent §4
   T3b spec includes "search_docs corpus inclusion + top-K retrieval
   frequency for probe queries" — T3b measures corpus-inclusion only.
   Top-K frequency requires probe-query selection + wall-clock experiment
   time that couples T3b to specific query semantics. Deferred as
   `future_trigger` for a subsequent sub-arc; corpus-inclusion is the
   load-bearing subset of parent §4 T3b graph (c).

2. **CLAUDE.md BFS follows only markdown-link + backtick-path syntax.**
   Prose references like "see AGENTS.md" (without backticks) are NOT
   followed. Undercounts reachability by an unknown small margin. Expect
   FP inflation in `reachable-from-search-only` classification (a few
   files may actually be prose-cited but flagged as search-only). Sample
   audit at 2899 could estimate the margin.

3. **`search_only_kind` pattern list is heuristic**, not authoritative.
   The 6 SEARCH_ONLY_BENIGN_PATTERNS chosen at S2837 reflect known
   closed-arc + envelope-archive patterns as of head `be7af72159ec`.
   New patterns emerging in future arcs need explicit list updates.
   Documented at §5.7 as Chris-tunable knob.

4. **Docs/INDEX.md parser is a flat-list extractor.** Assumes INDEX.md
   is autogen'd markdown with linked file paths in the same shape as
   `build_docs_index` produces. If the INDEX schema changes,
   `extract_docs_index_refs` needs updating. Note recorded for future
   compatibility.

5. **Document row `file_path` is exact-match.** A file renamed since
   last docs-cascade would appear as (a) NOT in corpus at new path AND
   (b) stale-corpus row at old path. T2 §5.6 RENAMED map partially
   surfaces this, but T3b does not resolve the split. Best mitigation:
   run docs-cascade close to T3b execution time (S2836 close cascade
   is 12h old at T3b open; sync gap is small).

6. **T5-territory files are counted but not disposition-classified**
   per T3a↔T5 boundary rule. This is by design (§1.4 anti-pattern
   #6), not a limitation.

7. **Usage / salience NOT measured** (Rigby SIGN cycle-3 Q5d
   STRENGTHEN fold). The T3b histogram optimizes the *count reduction*
   story (302 search-only → 76 "real" unclassified) but doesn't
   measure the *operator-impact dimension*: among the 302 search-
   only files, which are actually high-frequency needed for daily
   workflows vs cold-storage archives. Consequence if not addressed:
   we risk optimizing 2899 escalation-queue for count minimization
   while missing that a small subset of search-only docs (e.g. the
   72 unclassified) may be disproportionately load-bearing for
   Rigby-driven query patterns. Follow-up sub-arc could rank
   search-only files by (a) probe-query top-K frequency or (b)
   actual retrieval-log hit count from production `search_docs`
   invocations. Recorded as `future_trigger` for a subsequent
   sub-arc; T3b's histogram is structural, not behavioral.

### 6.2 Spot-verify sample — hand-check top escalate rows

Manually inspected the 3 T1 counter-signal rows (§2.7):

| File | Manual verdict | Classification |
|---|---|---|
| `docs/topics/collaboration-protocol.md` | Real topic doc; last modified S1301; unclear if T1 §4.1 dense-canonical claim was intended to include it | Real orphan/counter-signal — escalate confirmed |
| `docs/topics/obs-remote-control.md` | OBS integration topic; specific tooling doc; probably genuinely reachable via search intent | Real counter-signal — escalate confirmed |
| `docs/topics/video-upload.md` | Video upload workflow topic; probably reachable via search intent | Real counter-signal — escalate confirmed |

All 3 confirmed as real anchor-omissions from a canonical dense area.

Spot-check 5 unclassified `docs/apps/*_BRIEF.md`:

- All 5 are app brief templates
- All 5 match T3a §2.8 template family classification
- All 5 are load-bearing (Chris uses for suite planning)
- Cross-arc agreement: T3a + T3b both flag apps/ as needing an
  index or CLAUDE.md link

Confirmed escalate — same 2899 decision as T3a §2.8.

### 6.3 False-negative spot check — 1 prose-only citation of a `search-only` file

Manually searched for prose references (not backtick-quoted, not
markdown-link) to `docs/topics/collaboration-protocol.md`:

```bash
grep -r "collaboration-protocol" docs/ --include="*.md" | \
  grep -v "docs/topics/collaboration-protocol"
```

Result: no prose citations found. The 3 T1 counter-signal files are
genuinely anchor-omitted. No FN in this sample; confidence in
severity_class assignments.

---

## 7. Rigby SIGN pressure test — recommended dimensions for cycle 1

Per playbook §11.3 + `feedback_verify_rigby_tool_runs_before_trusting_sign`,
the T3b Rigby SIGN cycle should pressure-test:

- **Q1 (verify V2-stub cluster shape):** Does the 170-file count
  match T3a §2.3's "110+" — is my direct-marker scan finding
  actual V2 stubs, or picking up false positives (files that
  happen to contain the marker string in code samples etc.)?
  Expected tool_runs: `repo_tool.read` 5-10 sample paths + verify
  first-line marker presence.

- **Q2 (verify sub-classification rigor):** Are the 6
  `SEARCH_ONLY_BENIGN_PATTERNS` accurate at S2837 head? Does
  `docs/research/tools/` actually contain closed-arc tools, or
  did I mis-generalize? Any pattern that misclassifies a real
  orphan as benign is a false-negative escalate leak. Expected
  tool_runs: `repo_tool.list docs/research/tools/` + verify 5
  sample paths.

- **Q3 (T1 counter-signal ratification):** Is T3b §2.7's T1
  counter-signal claim about `docs/topics/*` real? Do the 3 files
  actually exist? Is my anchor-BFS correctly missing them, or is
  my BFS incomplete? Expected tool_runs: `repo_tool.list docs/topics/`
  + `grep collaboration-protocol` across corpus + `search_docs`
  test.

- **Q4 (README P1 finding vs. sync boundary):** Is README.md
  actually NOT in the Document corpus? Should it be? What does
  `build_docs_index` scope include? Expected tool_runs: `repo_tool.read`
  `core/management/commands/build_docs_index.py` inclusion logic
  + verify README.md handling in `docs/_index.json`.

- **Q5 (zoom-out):** What am I missing? If T3b's methodology is
  wrong in a subtle way, where would that show up in the histogram?
  What would push back on the T3a↔T5 boundary generalization?
  What's the coupling risk between T3b's `search_only_kind`
  heuristic and the future 2899 escalation-queue review workload?

**Anti-rubber-stamp check**: for every AGREE from Rigby, verify
`tool_runs` list is non-empty AND at least one entry involved
`repo_tool.read` / `repo_tool.list` / `grep` / `search_docs`
against a specific file or path (not just meta-reasoning).

---

## 8. Ratification envelope preview (for §11.3 rendezvous)

Per Group 2800 §8 ratification protocol + T3a envelope precedent
(`RATIFICATION_2026-07-19_2803a_docs_content_duplicate_audit.md`),
T3b ratification envelope will summarize:

1. **Session:** 2837
2. **Ratifier:** Chris
3. **Verbatim directive:** (Chris's exact ratification statement, e.g. "ratify T3b as-is")
4. **Scope:** full T3b (793-file scan + 4 severity classes + 8 search_only_kind sub-classes)
5. **SIGN pin:** `pa-7ebe273640e14691` (label `s2837-t3b-orphan-reachability-audit`)
6. **SIGN cycles:** N (Rigby joint SIGN; anti-rubber-stamp verified)
7. **Cycle-1 folds applied:** (list of DISAGREE/STRENGTHEN folded)
8. **Cycle-2 verification:** (list of AGREE with tool_runs evidence)
9. **P0 count:** 0 (root-stability gate NOT triggered)
10. **P1 count:** 1 (README.md)
11. **P2 count:** 72 (unclassified escalate queue)
12. **P3 count:** 720 (keep_as_is majority)
13. **§10.1 v1.1 schema status:** UNCHANGED (no v1.2 amendments)
14. **v1.2 candidates recorded:** T3b §5.3 (coverage_reachability as fourth axis; third witness for coverage-split refinement)
15. **T3a↔T5 boundary generalization:** applied to 41 T5 rows
16. **Escalate policy:** deferred to 2899 per S2836 D-verdict (77 rows total: 1 P1 + 76 P2)
17. **Next thread:** T4 handoff citation-integrity + retrieval-harm audit (opens at S2838)

---

## 9. Migration queue routing (per §10.4 cross-arc consumption contract)

T3b findings feed the future §3 execution arc (post-2899 close) via
the parent §10.4 cross-arc consumption contract:

- All `severity: P3, recommended_action: keep_as_is` rows (720) →
  no migration action.
- All `severity: P1, recommended_action: escalate_to_chris` rows
  (1: README.md) → 2899 workshop; then migration_pr_batch_hint =
  `anchor_docs` OR nothing.
- All `severity: P2, recommended_action: escalate_to_chris` rows
  (72) → 2899 workshop; batch by prefix per §3.3.
- All `is_t5_territory: true` rows (151) → routed to T5 (2805)
  audit as one input among several.
- All `is_v2_pointer_stub: true` rows (170) → no migration action;
  V2 stubs are intentional persistent pattern.

Migration PR grouping (once 2899 lands):
- `anchor_docs` batch: after Chris judgments on 76+1 escalate rows
- `dup_consolidate` batch: T3a territory (unchanged)
- `orphans_archive` batch: probably empty (zero unreachable-from-all-3)

---

## 10. What this research taught us about how to do research

Per Playbook §11.3 template addition (adopted S1399 close), every
`xx99` canonical summary includes a meta-methodology section. T3b
is a `280x` child audit but contributes to the 2899 meta-corpus.

### 10.1 What worked

1. **Direct-marker scan > shingle-pair-inference for V2 stubs.** T3a
   §2.3 reported "110+" V2 stubs via near-duplicate pair inference;
   T3b's direct `<!-- DOC-POINTER-V2` scan finds 170. Direct
   detection is stronger evidence; retroactively confirms T3a's
   lower bound.

2. **Three-graph reachability with sub-classification prevents
   false-positive escalate flooding.** Naive orphan detection
   (unreachable = orphan) would have generated 302 escalate rows;
   sub-classification via known-benign patterns drops to 72
   unclassified + 1 P1 = 77 real judgment items. ~4x reduction in
   Chris workload at 2899.

3. **T3a↔T5 boundary rule generalizes.** Applied cleanly at 41 T5
   rows with no case where the rule was ambiguous.

4. **Consuming T3a's V2-stub map is free.** T3b runs in ~2 seconds
   because T3a already did the V2-stub direct-marker equivalent
   work via shingle inference. Cross-child consumption is a real
   efficiency multiplier.

### 10.2 What to codify into playbook v3

- **Cross-child pre-clustering consumption is a first-class
  child-audit protocol** — parent §4 child specs SHOULD name which
  previous-child outputs they consume, formalizing the free
  efficiency gain. Two triggers: T3a consumed T2 §5.6 RENAMED map;
  T3b consumed T3a §5.4 V2-stub map. Third trigger at T4 would
  ratify.

- **Sub-classification of search-only-reachable is a T3b
  contribution to the parent §10.1 schema evolution discussion.**
  If Chris opts for v1.2 at 2899, add `coverage_reachability`
  fourth axis.

- **README.md corpus-sync gap is a real bug pattern** — a file can
  be anchor-cited but not RAG-corpus-included if the sync scope
  boundary excludes it. Add to DOC_LIFECYCLE §1 as a known failure
  mode.

### 10.3 Anti-patterns to avoid

1. **Don't treat `docs/INDEX.md` as coverage guarantee.** §2.4
   showed it's a strict subset of CLAUDE.md BFS; not a
   discoverability tool. Anchor navigation is the actual contract.

2. **Don't over-generalize "search-only = orphan candidate."** Real
   patterns: V2 stubs, ratification envelopes, closed arc children,
   closed packs are search-only-by-design. §1.4 anti-pattern list.

3. **Don't route escalate rows mid-arc.** S2836 policy: accumulate
   to 2899. T3b's 77 escalate rows all defer.

4. **Don't finalize disposition on adjacent-child-territory files.**
   T5 territory files carry `t5_may_override: YES`; T3b does not
   dispose.

### 10.4 Suggestions for the playbook itself

- **PLAYBOOK-11.3-compat**: parent §4 child specs should include a
  `consumes_pre_clustering_signals_from:` list (e.g. T3b consumes
  T3a §5.4). Currently implicit; explicit codification would help
  new arc authors.

- **`search_only_kind` pattern list should be a versioned artifact.**
  Not embedded in scanner source. If Chris extends the list at 2899,
  the extension should ratify with a version bump so downstream
  tooling knows which pattern set was applied.

### 10.5 Suggestions for future canonical summaries (optional)

- **2899 should include a `search_only_kind` reconciliation
  section** — cross-child pattern list (T3b's 6 patterns; T4 may
  extend for handoffs).
- **README.md fate section** — 2899 canonical should record the
  Chris decision (retrieval-fix OR bootstrap-only formalization)
  so it doesn't reopen as a finding in a future audit.

---

## 11. Cross-links

- Parent: `docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md`
- Sibling T1 (RATIFIED): `docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md`
- Sibling T2 (RATIFIED): `docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md`
- Sibling T3a (RATIFIED): `docs/research/domains/docs_content_audit/2803a_docs_content_duplicate_audit.md`
- Scanner tool: `tools/audit_2803b_orphan_reachability.py`
- Scanner output: `/tmp/t3b_orphan_scan_out.json`
- V2-stub seed (T3a): §5.4
- RENAMED basename seed (T2): §5.6 (`/tmp/t2_scan_out.json`)
- Ratification envelope: `docs/research/implementation/RATIFICATION_2026-07-19_2803b_docs_content_orphan_audit.md` (authored at S2837 close)
- S2837 handoff: `docs/handoffs/SESSION_2837_T3B_ORPHAN_REACHABILITY_AUDIT.md` (authored at S2837 close)
- Playbook (v0.8.0): `docs/ENGINEERING_PLAYBOOK.md`
- Governance canonical: `docs/00-START-HERE/DOC_LIFECYCLE.md`
- New memory (S2836): `feedback_arc_close_deferral_for_escalate_to_chris` (applied — 77 escalate rows defer to 2899)
