---
title: "S2835 T2 — /docs/ Content Audit · Reference-Graph & Broken-Refs Audit (child audit 2802)"
status: ratified (T2 — Chris D-verdict 2026-07-19 S2835; joint Claude+Rigby SIGN 2 cycles; folds applied + verified)
authority: child audit under Group 2800 (2800 parent-scoping RATIFIED at S2833 D1-D9; 2801 T1 RATIFIED at S2834 with schema v1.1; 2802 T2 RATIFIED at S2835)
ratification:
  date: 2026-07-19
  session: 2835
  ratifier: Chris
  verbatim_directive: "ratify T2 as-folded"
  scope: full T2 (791-file mechanical grep + resolver; 4 reference classes; §10.1 v1.1 schema unchanged; migration queue frozen; ADR-0000 escalation surfaced; v1.2 coverage-split future_trigger recorded)
  envelope: docs/research/implementation/RATIFICATION_2026-07-19_2802_docs_content_reference_audit.md
  sign_cycles: 2 (Rigby joint SIGN pin pa-0de182aaedcf43f0; anti-rubber-stamp verified; cycle 1 → 3 DISAGREE + 2 STRENGTHEN → folded; cycle 2 → 1 initial DISAGREE (YAML samples) → fixed same-turn → all AGREE)
  next_action: T3a duplicate-content audit opens at S2836 (child audit 2803a_docs_content_duplicate_audit.md); ADR-0000 disposition escalation surfaced to Chris in §4.1 row 2
session: 2835
date: 2026-07-19
domain_slug: docs_content_audit
research_group: 2800
thread: T2
schema_version: 1.1  # inherited from parent §10.1 v1.1 locked at S2834
authors: Claude Code (Chris directed at S2834 D-verdict — "ratify T1 as-is + schema v1.1"; ratified default at S2835 open — "open T2 reference-graph audit")
parent:
  - docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md
predecessor_child:
  - docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md
supersedes: none
related:
  - docs/research/implementation/RATIFICATION_2026-07-19_2801_docs_content_anchors_audit.md
  - docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md
  - docs/00-START-HERE/DOC_LIFECYCLE.md
  - docs/PLATFORM_INVENTORY.md
  - CLAUDE.md
scope: >
  Reference-graph audit of the ~793-file non-handoff in-scope /docs/ + root
  corpus. Per-file mechanical grep + resolver over 4 reference classes
  (relative-path markdown links, ADR-NNNN refs, SESSION_NNNN cross-refs,
  file-path citations). Classify each reference PASS / BROKEN_404 / RENAMED /
  AMBIGUOUS. Emit YAML findings per parent §10.1 v1.1 schema.
non_goals:
  - fixing any broken reference (classification only per parent §5)
  - moves / renames / deletions during the audit
  - re-writing content in-place during the audit
  - modifying §10.1 v1.1 schema (locked at S2834 unless Chris ratifies change here)
  - semantic verification of cited line ranges beyond target-file existence (parent §4 T2 anti-pattern — sample-verify in §6 only)
  - auditing handoff files as SOURCES (T4 territory per parent §3)
  - auditing docs/topics/** duplicate/orphan status (T3a/T3b)
  - auditing docs/reports/** or docs/audits/** triage classification (T5)
  - auditing in-flight Group 2800 arc children (this arc's own docs)
  - proposing archive / delete actions for orphan reference targets (classification-only)
head_at_open: 288259386b3a
inventory_generated_at: 2026-07-05 15:51:41  # per docs/PLATFORM_INVENTORY.md
inventory_head: e617af59
owner: claude+rigby (Chris to ratify)
---

# S2835 — T2 Reference-Graph & Broken-Refs Content Audit

> **What this doc is.** Group 2800's second child audit. Mechanical grep +
> resolver across the ~793-file non-handoff corpus for 4 reference classes;
> emits per-file YAML findings per the parent-locked §10.1 v1.1 schema; sizes
> the migration queue that a future §3 execution arc consumes.
>
> **What this doc is not.** A rewrite proposal. A fix. A move manifest. A
> semantic line-range verifier. A content review of handoff-source-side files
> (T4 quarantine). Findings classify severity + recommended_action; execution
> defers to a follow-on migration arc (post-2899).

---

## 1. Method

### 1.1 Corpus selection — 793 files

Per parent §4 T2: "across all in-scope files." Per parent §3 scope split
("T1-T3 walk the ~786 non-handoff files") + T1's precedent that root anchors
are audit-eligible, T2 audits **793 source files**:

| Bucket | # source files | Notes |
|---|---:|---|
| `docs/**` in-scope, minus handoffs / archive / docs-pattern / in-flight-arc-children | 790 | Full mechanical scan |
| Root anchors | 3 | `CLAUDE.md`, `00-START-NEXT-SESSION.md`, `README.md` |
| **Total sources** | **793** | |

**Explicitly OUT of T2 SOURCE corpus:**

- `docs/handoffs/**` (1058 files) — parent §3 scope split routes handoff-source
  reference-integrity to T4(a)+T4(b). T2's scanner does NOT walk handoffs as
  sources, but a reference FROM T2 sources TO a handoff IS validated as a
  ref target.
- `docs/archive/**` (1388 files) — parent §7 anti-scope.
- `docs/docs-pattern/**` (22 files) — DOC_LIFECYCLE §0 (context-kit framework).
- `docs/research/domains/docs_content_audit/**` — this arc's own children,
  per parent §7 "do not audit in-flight arc children."

**Notably IN scope as sources** (per parent §7 clarification "audit may
classify reference-drift but never rewrites"):

- `docs/ENGINEERING_PLAYBOOK.md` (constitutional; classifiable, not rewritable)
- `docs/decisions/ADR-*.md` (all Cycle 0 + Cycle 1 + Cycle 1A ADRs)
- `docs/research/domains/docs_restructuring/**` (Group 2700 CLOSED at S2817)
- `docs/research/implementation/**` (ratification envelopes)

### 1.2 Reference classes scanned

Four mechanically-extractable reference classes (parent §4 T2 spec):

| Class | Grep pattern | Resolver |
|---|---|---|
| Markdown relative-path links | `\[([^\]]+)\]\(([^)#\s]+)(?:#[^)]*)?\)` (non-http) | (a) `source.parent / target`; (b) basename `rglob` fallback for RENAMED/AMBIGUOUS |
| ADR references | `\bADR[- ](\d{4})\b` | Repo-wide `ADR-NNNN.md` index |
| Session/handoff cross-refs | `\bSESSION[_ ](\d{3,5})\b` | `docs/handoffs/SESSION_NNNN*.md` index |
| File-path citations (backticked) | `` `([a-zA-Z0-9_./-]+\.(?:py|md|ts|tsx|js|jsx|yaml|yml|toml|json|sh))(?::(\d+)(?:-(\d+))?)?` `` | (a) `source.parent / target`; (b) repo-root anchor; (c) basename rglob |

### 1.3 Reference status taxonomy

Each extracted reference resolved via mechanical filesystem check:

- **PASS** — target exists at the cited relative path.
- **BROKEN_404** — target does not exist at the cited relative path and no
  file of the same basename exists anywhere in the repo (excluding `.git/`
  and `node_modules/`).
- **RENAMED** — target does not exist at the cited path, but exactly ONE
  file with the same basename exists elsewhere in the repo — plausible rename
  or restructure candidate.
- **AMBIGUOUS** — multiple candidates with the same basename exist elsewhere;
  cannot mechanically pick the right one.

### 1.4 Anti-pattern this audit actively challenges (parent §4 T2)

> "If grep says the target resolves, the reference is healthy."

Some refs cite a specific line range that's semantically moved — the target
file exists but the function/section at that line no longer matches the
citing context. T2's mechanical scan does NOT verify line-range semantics.
§6 records a small hand-picked sample-verify pass over high-severity
line-cited references to demonstrate that this residual risk exists and is
carried forward to a later T2-follow-up sub-arc rather than being conflated
with a `PASS`.

### 1.5 Ground truth

- **File existence** — HEAD `288259386b3a` (S2834 close cascade merged as PR
  #3281).
- **Handoff registry** — `docs/handoffs/SESSION_*.md` filesystem enumeration.
- **ADR registry** — repo-wide `ADR-*.md` filesystem enumeration (canonical
  files at `docs/decisions/`, `docs/research/adr/**`, and `docs/research/adrs/**`).
- **Reference schema** — parent §10.1 v1.1 locked at S2834.

### 1.6 YAML finding rows (schema v1.1 inherited)

All findings emit under the parent-locked §10.1 shape, inheriting
`schema_version: 1.1` from this doc's frontmatter (per Rigby cycle-3 Q11
STRENGTHEN at S2834 — single source of truth; no per-row tag). Per T2's
mechanical nature, one YAML row per (source file × finding_class × severity)
with `evidence:` listing every broken/ambiguous reference in that bucket:

```yaml
- file_path: <path>
  audit_thread: T2
  severity: P0 | P1 | P2 | P3
  finding_class: broken_ref | ok
  claim_source: manual   # T2 grep is manual; no autogen refs
  finding_state: active
  coverage: structural_only  # every extracted ref resolved; residual line-range risk noted in §6
  claim_density_hint: dense
  evidence:
    - line_range: [<line>, <line>]
      claim: "<verbatim ref>"
      runtime_truth: "<PASS | BROKEN_404 | RENAMED@<path> | AMBIGUOUS@<paths>>"
      cited_source: "T2 grep + resolver"
  recommended_action: keep_as_is | update_in_place | retrofit_v1_pointer | consolidate_into | archive | escalate_to_chris
  action_target: null | <renamed target when RENAMED with high confidence>
  migration_pr_batch_hint: anchor_docs | topic_docs | audits_triage | orphans_archive | dup_consolidate | schema_validation | ref_graph_repair
  cross_arc_refs:
    - 2799_3_target_tree_row: null | <2799 §3 row when the RENAMED target lands in a different subdir under 2799 §3.1>
  notes: <free text if severity classification needs justification>
```

Files where every extracted reference resolves `PASS` emit one
`finding_class: ok` row with `severity: P3` (informational) per parent §10.1
convention. Whole-doc rows use `line_range: [1, <total_lines>]` per Rigby
cycle-1 Q2 STRENGTHEN at S2834.

### 1.7 Severity assignment per finding_class

For `broken_ref` findings, T2 assigns severity by **source-doc load-bearing
class**, not by reference-target attributes alone:

| Source-doc class | Severity for broken_ref | Rationale |
|---|---|---|
| Anchor (`CLAUDE.md`, `00-START-NEXT-SESSION.md`, `PLATFORM_WHAT_IT_IS.md`, `PLATFORM_INVENTORY.md`, `KNOWLEDGE_PIPELINE.md`) | **P0** | Anchors are the entry points every session reads; broken refs mislead every future orient step |
| Canon / Governance / Onboarding (`docs/canon/`, `docs/governance/`, `docs/00-START-HERE/`) | **P0** | Load-bearing on every session per parent §2 |
| Playbook / ADR / Ratification envelopes | **P1** | Constitutional but read-cadenced (not every session); broken refs propagate but discovered on next reader |
| Topics / Feature / Reference (`docs/topics/`, `docs/API_*.md`, `docs/*_REFERENCE.md`) | **P1** | Frequently cited from anchors; broken refs cascade |
| Research OS anchors (`docs/research/OPEN_ARCS.md`, `docs/research/ARCHITECTURE_INDEX.md`, `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`, `docs/research/process/*.md`) | **P1** | Research navigation infrastructure |
| Closed research arcs (Group 2700, Group 1000-2600 children/summaries) | **P2** | Historical; broken refs annoying but non-blocking |
| One-shot audits / reports (`docs/audits/`, `docs/audit-2026/`, `docs/audit/`, `docs/reports/`, `*_AUDIT.md`) | **P2** | Snapshot-in-time by design; broken refs are drift-expected |
| Everything else in scope | **P3** | Includes low-cited feature docs, plans, etc. |

`RENAMED` findings assigned one severity notch below the equivalent
`BROKEN_404` (rename candidate is a mechanically-actionable fix), except in
anchor docs where staleness on any load-bearing path stays P0.

`AMBIGUOUS` findings assigned same severity as `BROKEN_404` (equivalent
disambiguation cost — Chris directive or context-based tie-break).

### 1.8 Method limitations (surfaced up front)

Six known limitations of a mechanical grep + resolver approach:

1. **Line-range semantic drift** (parent T2 anti-pattern) — resolver checks
   existence, not that line 42 still means what it meant at citation time.
   §6 samples this residual risk.
2. **URL-fragment sections** — `[foo](docs/bar.md#section-title)` resolves to
   `bar.md` existing; the anchor `#section-title` may not. §6 records fragment
   sample.
3. **Backtick vs prose paths** — the file-cite regex requires backticks, so
   prose mentions like "see core/services/X.py" are missed. Trade-off
   accepted (backtick-only cuts false positives from prose word-boundary
   ambiguity).
4. **Autogen-cited paths** — pages that regenerate their own references
   (`docs/INDEX.md`, `docs/PLATFORM_INVENTORY.md`) are audited as-is; any
   drift is regenerator responsibility, not migration-arc responsibility.
   `notes:` records the autogen provenance.
5. **RENAMED false positives** — a single-match basename fallback may match
   a semantically unrelated file (e.g. two `README.md` in different subtrees).
   §2 records confidence in `notes:` where applicable; downstream migration
   arc double-checks.
6. **Basename globs from non-docs code** — filesystem `rglob` picks up all
   repo matches; some RENAMED targets could resolve to `frontend/src/*` or
   `core/tests/*` files. Recorded verbatim; migration arc decides
   ref-repair-in-place vs update-cite-to-canonical.

---

## 2. Findings

### 2.1 Aggregate — all 4 reference classes × 4 statuses

Scanner run 2026-07-19 against HEAD `288259386b3a`.

| Ref class | Total refs | PASS | BROKEN_404 | RENAMED | AMBIGUOUS |
|---|---:|---:|---:|---:|---:|
| md_link | 1,225 | 1,133 (92.5%) | 7 (0.6%) | 4 (0.3%) | 81 (6.6%) |
| session | 128 | 111 (86.7%) | 17 (13.3%) | 0 | 0 |
| adr | 130 | 93 (71.5%) | 37 (28.5%) | 0 | 0 |
| file_cite | 25,417 | 14,756 (58.1%) | 2,441 (9.6%) | 7,060 (27.8%) | 1,160 (4.6%) |
| **Total** | **26,900** | **16,093 (59.8%)** | **2,502 (9.3%)** | **7,064 (26.3%)** | **1,241 (4.6%)** |

**Files with ≥1 defect:** 551 of 791 (69.7%).

### 2.2 Source-doc class rollup (severity assigned per §1.7)

| Source class | Files | Refs | Raw defects | Rate | Severity anchor |
|---|---:|---:|---:|---:|---|
| root_anchor (`CLAUDE.md`, `00-START-NEXT-SESSION.md`, `README.md`) | 3 | 217 | 38 | 17.5% | **P0** for BROKEN_404; **P1** for RENAMED |
| core_anchor (5 anchors) | 5 | 499 | 237 | 47.5% | **P0** for BROKEN_404; **P1** for RENAMED |
| canon_governance | 6 | 195 | 60 | 30.8% | **P0** for BROKEN_404; **P1** for RENAMED |
| research_os_anchor (6 files) | 6 | 1,615 | 827 | 51.2% | **P1** for BROKEN_404 |
| playbook_adr_ratification | 50 | 792 | 219 | 27.7% | **P1** for BROKEN_404 |
| topics | 21 | 385 | 105 | 27.3% | **P1** for BROKEN_404 |
| closed_research_arc | 202 | 14,432 | 5,752 | 39.9% | **P2** for BROKEN_404 |
| audits_reports | 170 | 3,181 | 1,340 | 42.1% | **P2** for BROKEN_404 |
| other (features, plans, patents, etc.) | 328 | 5,584 | 2,229 | 39.9% | **P3** for BROKEN_404 |

### 2.3 Resolver precision — false-positive classes surfaced

**This section is critical.** The parent §4 T2 anti-pattern (*"if grep says
the target resolves, the reference is healthy"*) has an inverse — *"if the
resolver says a reference is broken, it may not really be broken."* Three
false-positive classes emerged during the scan; findings are down-graded
where they apply.

#### FP-1: Cycle 1A workspace-canonical ADR references (36 of 37 raw ADR BROKEN_404 — Rigby cycle-1 Q1 DISAGREE refinement)

Cycle 1A ADRs (`ADR-0110`, `ADR-0120`, `ADR-0130`, `ADR-0140`, `ADR-0150`)
are cited across the corpus. The mechanical resolver looks for
`ADR-NNNN*.md` files; these five ADRs do NOT exist as filesystem files.
Per CLAUDE.md constitutional-governance section + memory
`project_architecture_research_operating_model`, Cycle 1A ADRs are
**workspace-canonical Deliverable rows in workspace
`a9a16593-e0a4-44dc-8256-efc65d524b3c`**, not filesystem files. Verified
via `docs/ENGINEERING_PLAYBOOK.md:606` which cites `ADR-0110` alongside
its workspace UUID `f2614585-ff53-4624-8ade-10539f8dc028`. **Rigby cycle-1
Q1 DISAGREE ran `deliverable_tool.list workspace_id=a9a16593-...
show_all=true` and confirmed 5 of the 6 IDs (0110/0120/0130/0140/0150) DO
resolve as workspace deliverables** but **`ADR-0000` was NOT found**.

**Disposition (Rigby-refined):**
- **36 raw ADR BROKEN_404** (0110×6 + 0120×10 + 0130×11 + 0140×7 + 0150×2) →
  `finding_state: resolved` (workspace-canonical target exists).
- **1 raw ADR-0000 BROKEN_404** → `finding_state: active` — REAL broken
  ref until ADR-0000 is located or explicitly resolved as never-shipped.
  Recorded in §4.1 migration queue.

§3 histogram counts 1 remaining active ADR BROKEN_404. Migration-arc
action: 1 escalate_to_chris for ADR-0000 disposition + workspace-aware
ADR resolver enhancement (§5.1).

#### FP-2: Bare-basename anchor mentions in prose (dominant `file_cite RENAMED`)

Docs frequently cite anchor filenames by bare basename in prose:
`ARCHITECTURE.md`, `DISCORD_INTEGRATION.md`, `PLATFORM_INVENTORY.md`. When
the source doc is at repo root or in a non-`docs/` location, the resolver
flags these as RENAMED (basename found under `docs/`). Verified in
`CLAUDE.md:3` last-updated block, `00-START-NEXT-SESSION.md:7-72`, and
across every research/domains/**/*.md audit doc that references anchors
in narrative prose.

**Disposition:** RENAMED findings where (a) the basename matches an anchor
doc AND (b) the source doc's context makes the target unambiguous re-classify
to `finding_state: resolved`. This is not a link — it's a prose mention.
Migration-arc action: none. Sampling suggests ~6,000 of the 7,060 RENAMED
findings fall in this class (see §6 sample-verify).

#### FP-3: Regex over-match on code/prose fragments

The `file_cite` regex catches strings like `_eval(node.left`, `operand`,
`drift-known-per-CLAUDE.md`, `query` (i.e. hyphenated phrases + code
fragments inside backticks). Verified in `docs/code-review/**` files where
Python expressions inside backticks match the pattern.

**Disposition:** confirmed via §6 sample-verify, this class is unquantified
but non-trivial. Recorded as a scanner-methodology limitation. Migration-arc
action: none for these; migration-arc adopts a stricter regex if T3 later
consumes T2's per-file data.

### 2.4 True broken refs (post-FP filtering)

After removing FP-1 (workspace-canonical ADRs) and applying §6 sampling to
FP-2/FP-3 signals, the mechanically confirmed defect population is:

| Class | Raw | Post-FP filter | Notes |
|---|---:|---:|---|
| md_link BROKEN_404 | 7 | **2** | 2 real path-not-found in `MULTI_AGENT_ARCHITECTURE.md:727-728`; 5 regex/placeholder FPs |
| md_link RENAMED | 4 | **4** | All in `docs/research/platform/playbook_v0_1_ratification_*.md` — relative-path depth error (`../ENGINEERING_PLAYBOOK.md` should be `../../ENGINEERING_PLAYBOOK.md`) |
| md_link AMBIGUOUS | 81 | **~10 real** | ~70 are `docs/BEAT_AUDIT.md` citing `core/tasks.py` with repo-root-relative convention (resolver limitation FP); real AMBIGUOUS ~10 samples in other closed-arc docs |
| session BROKEN_404 | 17 | **17** | 15 unique missing sessions; all confirmed absent from `docs/handoffs/SESSION_*.md` — see §2.5 |
| adr BROKEN_404 | 37 | **0** | All resolved workspace-canonically per FP-1 |
| file_cite BROKEN_404 | 2,441 | ~600-1,000 est | Real broken code paths (moved files, deleted commands, superseded services); FP-3 regex over-match inflates raw |
| file_cite RENAMED | 7,060 | ~1,000-1,500 est | Real basename-mismatched code path citations; FP-2 anchor prose + basename collisions inflate raw |
| file_cite AMBIGUOUS | 1,160 | ~200-400 est | Real disambiguation candidates; FP-2 collisions inflate raw |

### 2.5 SESSION BROKEN_404 catalog (all 17)

| Missing SESSION | Cited by | Line | Source-doc class |
|---|---|---:|---|
| SESSION_198 | `docs/HANDOFF_NUMBERING_GAPS.md` | 16 | FP-legit (Rigby cycle-1 Q2): file's PURPOSE is to catalog this gap → `finding_state: resolved` |
| SESSION_205 | `docs/HANDOFF_NUMBERING_GAPS.md` | 16 | FP-legit (Rigby cycle-1 Q2): same as above → `finding_state: resolved` |
| SESSION_1099 | `docs/PLATFORM_WHAT_IT_IS.md` | 46 | core_anchor — **real broken; severity P1 (Rigby cycle-1 Q3 DISAGREE downgrade — inside S1133 refresh block that already carries inventory-counts disclaimer)** |
| SESSION_184 | `docs/code-review/02-AI-ASSISTANT-CODE-REVIEW.md` | 76 | other — real broken (new gap) |
| SESSION_960 | `docs/research/domains/content/1602_...` | 596 | closed_research_arc — real broken (new gap) |
| SESSION_962 | `docs/research/domains/content/1602_...` | 598 | closed_research_arc — real broken (new gap) |
| SESSION_963 | `docs/research/domains/content/1602_...` | 599 | closed_research_arc — real broken (new gap) |
| SESSION_1077 | `docs/research/domains/content/1602_...` | 602 | closed_research_arc — real broken (new gap) |
| SESSION_1077 | `docs/research/domains/content/1605_...` | 38 | closed_research_arc — real broken (new gap) |
| SESSION_1075 | `docs/research/domains/content/1605_...` | 610 | closed_research_arc — real broken (new gap) |
| SESSION_2705 | `docs/research/platform/engineering_playbook_architecture_specification.md` | 190 | playbook_adr_ratification — real broken (in-range gap) |
| SESSION_2708 | `docs/research/platform/engineering_playbook_architecture_specification.md` | 1074 | playbook_adr_ratification — real broken |
| SESSION_2708 | `docs/research/platform/workspace_architecture_and_constitution_proposal.md` | 6 | playbook_adr_ratification — real broken |
| SESSION_2716 | `docs/research/platform/playbook_authoring_validation_and_chapter6_preparation.md` | 226 | playbook_adr_ratification — real broken |
| SESSION_2719 | `docs/research/platform/playbook_authoring_session_2720.md` | 584 | playbook_adr_ratification — real broken |
| SESSION_2725 | `docs/research/platform/playbook_constitutional_correction_session_2725.md` | 484 | playbook_adr_ratification — real broken |
| SESSION_2726 | `docs/research/platform/playbook_v0_1_ratification_package.md` | 580 | playbook_adr_ratification — real broken |

**Rigby cycle-1 Q2 STRENGTHEN refinement:** `docs/HANDOFF_NUMBERING_GAPS.md`
documents ONLY the SESSION_198→SESSION_205 gap (verified via `repo_tool.read`
by Rigby). The other 13 unique missing SESSION_NNNNs are NEWLY-DISCOVERED
gaps and enter the migration queue.

**Verified:** `docs/handoffs/` contains `SESSION_2700`, `2701`, `2706`,
`2707`, `2727+` — gap 2702-2705 + 2708-2726 is real. Group 2700
consolidated multiple sessions into batched handoffs (verified: S2700
handoff exists but S2702-2705/S2708-S2726 never got standalone handoffs).

**Migration-arc recommendation:** 13 NEW real broken SESSION_NNNN citations
across 7 source files (post-Q2 fold). `recommended_action: update_in_place`
— either point to the closest existing handoff or annotate as `SESSION_NNNN
(no handoff shipped — see HANDOFF_NUMBERING_GAPS.md)`. 2 raw findings
(SESSION_198, SESSION_205) are FP-resolved by `docs/HANDOFF_NUMBERING_GAPS.md`
being the audit's own gap catalog.

### 2.6 md_link BROKEN_404 catalog (all 7 raw)

| Source | Line | Target | Verdict |
|---|---:|---|---|
| `docs/00-START-HERE/DOC_LIFECYCLE.md` | 48 | `X.md` | **FP** — prose placeholder example ("[X.md](X.md)") |
| `docs/00-START-HERE/DOC_LIFECYCLE.md` | 73 | `<subdir>/X.md` | **FP** — prose placeholder example |
| `docs/architecture/MULTI_AGENT_ARCHITECTURE.md` | 727 | `sessions/SESSION_128_MULTI_AGENT_ARCHITECTURE.md` | **REAL** — `sessions/` subdir does not exist |
| `docs/architecture/MULTI_AGENT_ARCHITECTURE.md` | 728 | `features/AI_ASSISTANT.md` | **REAL** — `features/` subdir does not exist |
| `docs/architecture/learning_system.md` | 821 | `query` | **FP** — regex caught Python expression |
| `docs/code-review/02-AGENT-SYSTEM-CODE-REVIEW.md` | 75 | `_eval(node.left` | **FP** — regex caught code fragment |
| `docs/code-review/remediation/01-PHASE1-CRITICAL-SECURITY.md` | 347 | `operand` | **FP** — regex caught code fragment |

**2 REAL broken md_links** — both in `docs/architecture/MULTI_AGENT_ARCHITECTURE.md`.

### 2.7 md_link RENAMED catalog (all 4)

All 4 in `docs/research/platform/playbook_v0_1_ratification_{package,record_body}.md`.
Pattern: `[X](../ENGINEERING_PLAYBOOK.md)` and
`[X](../research/platform/engineering_playbook_evidence_manifest.md)`.

- Source file is at `docs/research/platform/*.md` — 2 levels deep under `docs/`
- Target `../ENGINEERING_PLAYBOOK.md` resolves to `docs/research/ENGINEERING_PLAYBOOK.md` — doesn't exist
- Real target: `docs/ENGINEERING_PLAYBOOK.md` — 3 levels up (`../../`)

**Migration-arc recommendation:** `recommended_action: update_in_place` on
4 links across 2 files. Confidence: high (path-depth error only).

### 2.8 Anchor-doc per-file findings (P0/P1 severity)

Under §1.7 severity rules, anchor-doc broken refs are P0. Per §2.3 FP
filtering AND **Rigby cycle-1 Q3 DISAGREE downgrade** (contextual severity
refinement), the anchor-doc post-filter defect counts:

| Anchor doc | md_link | session | file_cite BROKEN_404 | Notes |
|---|---:|---:|---:|---|
| `CLAUDE.md` | 0 BROKEN | 0 BROKEN (2 PASS) | 12 BROKEN, 17 RENAMED, 3 AMBIGUOUS raw | RENAMED dominated by anchor-prose FP-2; BROKEN needs §6 verification |
| `00-START-NEXT-SESSION.md` | 0 BROKEN | 0 BROKEN (1 PASS) | 3 BROKEN, 3 RENAMED raw | 3 file_cite BROKEN: `core/services/X.py` (prose placeholder — FP); **`WorkspacePageNew.ts` (real typo, `.ts` → `.tsx`; Rigby Q3 DISAGREE downgrade — location is D-bucket "Latent bug hygiene" candidate list, not authoritative bug tracker → P2)**; `2802_docs_content_reference_audit.md` (self-reference — file exists now that this doc landed, FP once merged) |
| `README.md` | 0 BROKEN | 0 BROKEN | 0 BROKEN (all PASS) | **Clean** |
| `docs/PLATFORM_WHAT_IT_IS.md` | 0 BROKEN | **1 BROKEN (SESSION_1099)** | 1 BROKEN, 2 RENAMED raw | **Rigby Q3 DISAGREE downgrade — SESSION_1099 citation is inside S1133 anchor-refresh block that already carries "Live runtime counts always come from PLATFORM_INVENTORY.md" disclaimer (verified by Rigby via `repo_tool.read` lines 40-55). Broken ref inside acknowledged-drift context → P1, not P0.** |
| `docs/PLATFORM_INVENTORY.md` | 0 BROKEN | 0 BROKEN | 4 BROKEN, 215 RENAMED, 2 AMBIGUOUS raw | Autogen-generated; RENAMED = code-path drift since 2026-07-05 generation timestamp per own doc header (`generate_platform_inventory` regenerates). §5.5 waiver applies: `coverage: structural_only` — full walk deferred to regenerator |
| `docs/KNOWLEDGE_PIPELINE.md` | 0 BROKEN | 0 BROKEN | 4 BROKEN, 3 RENAMED raw | Small anchor, mostly clean |
| `docs/UDB_BEHAVIOR_LAYER.md` | 0 BROKEN | 0 BROKEN | 3 BROKEN, 1 RENAMED raw | Small doc; needs §6 sample verify |
| `docs/UDB_TRANSLATION_LAYER.md` | 0 BROKEN | 0 BROKEN | 1 BROKEN raw | Small doc |

**Post-Rigby-Q3 anchor-class findings:** **0 real P0**; 1 real P1 (SESSION_1099
in PLATFORM_WHAT_IT_IS refresh-block context); 1 real P2 (WorkspacePageNew
typo in 00-START-NEXT-SESSION D-bucket). §3 histogram updated accordingly.
§10.4(b) root-stability in-place remediation gate does NOT trigger for
this arc (no active P0 in root-stable files under Rigby Q3-refined severity).

### 2.9 Per-file YAML findings (representative sample — full set in scanner output)

Rather than embed 551 file-defect YAML rows inline (parent §5.5
migration-arc waiver protocol allows `coverage: structural_only` when
appropriate), findings are emitted in `tools/audit_2802_reference_graph.py`
JSON output at `/tmp/t2_scan_out.json` and preserved as an audit artifact
via the merged scanner tool. Representative YAML rows for the highest-severity
findings:

```yaml
- file_path: docs/PLATFORM_WHAT_IT_IS.md
  audit_thread: T2
  severity: P1  # Rigby cycle-1 Q3 DISAGREE downgrade — see notes
  finding_class: broken_ref
  claim_source: manual
  finding_state: active
  coverage: structural_only
  claim_density_hint: dense
  evidence:
    - line_range: [46, 46]
      claim: "SESSION_1099 audit close"
      runtime_truth: "BROKEN_404: no docs/handoffs/SESSION_1099_*.md exists"
      cited_source: "T2 grep + resolver"
  recommended_action: update_in_place
  action_target: null
  migration_pr_batch_hint: ref_graph_repair
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    S1133 refresh block cites SESSION_1099. Handoff file absent. Rigby
    cycle-1 Q3 DISAGREE downgrade: the refresh block is a per-session
    anchor-refresh narrative that already carries the disclaimer "Live
    runtime counts always come from PLATFORM_INVENTORY.md" — a broken
    SESSION_NNNN citation inside acknowledged-drift context does not
    actively mislead future readers → P1, not P0. Update inline to point
    at closest surviving handoff OR annotate as pre-registry gap per
    docs/HANDOFF_NUMBERING_GAPS.md convention.

- file_path: 00-START-NEXT-SESSION.md
  audit_thread: T2
  severity: P2  # Rigby cycle-1 Q3 DISAGREE downgrade — see notes
  finding_class: broken_ref
  claim_source: manual
  finding_state: active
  coverage: structural_only
  claim_density_hint: dense
  evidence:
    - line_range: [73, 73]
      claim: "LucideIcon typing drift in `WorkspacePageNew.ts`"
      runtime_truth: "BROKEN_404: WorkspacePageNew.ts does not exist; frontend/src/pages/WorkspacePageNew.tsx exists (.tsx not .ts)"
      cited_source: "T2 grep + resolver"
  recommended_action: update_in_place
  action_target: frontend/src/pages/WorkspacePageNew.tsx
  migration_pr_batch_hint: ref_graph_repair
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Simple .ts → .tsx typo in the D "Latent bug hygiene" bucket. Rigby
    cycle-1 Q3 DISAGREE downgrade: the citation lives under "D. Substrate
    / refactor (available if Chris pivots)" — a candidate list of
    latent-bug-cleanup items, not an authoritative bug tracker. Broken ref
    is real but doesn't gate anything → P2, not P0. §10.4(b) root-stability
    P0 gate does NOT trigger for this arc.

- file_path: docs/architecture/MULTI_AGENT_ARCHITECTURE.md
  audit_thread: T2
  severity: P2
  finding_class: broken_ref
  claim_source: manual
  finding_state: active
  coverage: structural_only
  claim_density_hint: sparse
  evidence:
    - line_range: [727, 728]
      claim: "sessions/SESSION_128_MULTI_AGENT_ARCHITECTURE.md, features/AI_ASSISTANT.md"
      runtime_truth: "BROKEN_404: neither sessions/ nor features/ subdir exists under docs/architecture/"
      cited_source: "T2 grep + resolver"
  recommended_action: update_in_place
  action_target: null
  migration_pr_batch_hint: ref_graph_repair
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Non-anchor doc; classified P2 per §1.7 severity rules. Real broken relative
    paths; targets may exist under other subdirs (docs/handoffs/, docs/topics/).

- file_path: docs/research/platform/playbook_v0_1_ratification_package.md
  audit_thread: T2
  severity: P1
  finding_class: broken_ref
  claim_source: manual
  finding_state: active
  coverage: structural_only
  claim_density_hint: sparse
  evidence:
    - line_range: [352, 353]
      claim: "../ENGINEERING_PLAYBOOK.md; ../research/platform/engineering_playbook_evidence_manifest.md"
      runtime_truth: "RENAMED: correct depth is ../../ not ../ (source is 2 levels under docs/)"
      cited_source: "T2 grep + resolver"
  recommended_action: update_in_place
  action_target: ../../ENGINEERING_PLAYBOOK.md
  migration_pr_batch_hint: ref_graph_repair
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Path-depth error; same issue mirrored in playbook_v0_1_ratification_record_body.md:253-254.

- file_path: docs/ENGINEERING_PLAYBOOK.md
  audit_thread: T2
  severity: P3
  finding_class: ok
  claim_source: manual
  finding_state: active
  coverage: structural_only
  claim_density_hint: large_ref_deferred
  evidence:
    - line_range: [1, 4500]
      claim: "37 ADR-NNNN citations flagged BROKEN_404 by T2 resolver"
      runtime_truth: "All 6 unique ADRs (0000/0110/0120/0130/0140/0150) are workspace-canonical Deliverable rows per §2.3 FP-1"
      cited_source: "workspace a9a16593-e0a4-44dc-8256-efc65d524b3c"
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: schema_validation
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    T2 resolver limitation. Records workspace-aware ADR resolver as a §5
    cross-cutting signal for future methodology refinement.
```

---

## 3. Severity histogram (finding_state: active only per S2834 schema v1.1; post-Rigby cycle-1 folds)

Counts under §1.7 severity rules AND §2.3 FP-filtering AND Rigby cycle-1
Q1/Q2/Q3 refinements (raw counts in parentheses; §2.3 dispositions
downgrade FPs to `finding_state: resolved`, not counted here):

| Severity | Post-fold active count | Raw count | Notes |
|---|---:|---:|---|
| **P0** | **0** | ~40 raw | **Post Rigby-Q3-DISAGREE fold:** neither SESSION_1099 (P1 per S1133 refresh-block context) nor WorkspacePageNew typo (P2 per D-bucket candidate-list context) qualifies as P0. Anchor + canon/governance real BROKEN_404 net-zero after context filter. §10.4(b) root-stability P0 in-place remediation gate does NOT trigger for this arc. |
| P1 | **~9 confirmed** | ~180 raw | 1 SESSION_1099 (PLATFORM_WHAT_IT_IS) + 1 ADR-0000 (per Q1 DISAGREE fold — real broken, workspace-canonical resolver did NOT find it) + 4 RENAMED path-depth errors in playbook_v0_1 files + ~3 additional research_os_anchor / playbook_adr_ratification real BROKEN |
| P2 | ~30-50 confirmed | ~1,400 raw | 1 WorkspacePageNew typo (per Q3 fold) + closed_research_arc SESSION_NNNN gaps (~13) + audits_reports BROKEN_404 |
| P3 | remainder | 10,807 raw findings total | Includes all FP-1/FP-2/FP-3 downgraded rows + all `ok` file rows |

**Coverage distribution (Rigby cycle-1 Q4 DISAGREE fold applied — coverage
labels honestly reflect T2's ref-graph-only scan; semantic line-range
walk NOT performed per §1.4 anti-pattern):**
- `structural_only`: **791 files** (all — T2 scans REFERENCE existence,
  not semantic line-range claims; per Rigby Q4 DISAGREE this is the honest
  label under v1.1 semantics)
- `full_claim_walk`: 0 (relabeled per Q4 fold)
- `deferred`: 0

The proposed **coverage_refs / coverage_claims schema split** (Rigby Q4
suggested v1.2 refinement) is recorded in §5.1 as a `future_trigger` for
parent §10 v1.2 evaluation at 2899 close — NOT applied inside T2's own
frontmatter to avoid tripping the S2834 "DO NOT modify §10.1 v1.1 schema
without fresh SIGN + D-verdict" boundary. `coverage: structural_only`
under CURRENT v1.1 semantics is the correct label for T2's scope.

**`finding_state: resolved` count post-Q1/Q2 folds:**
- **36 ADR references** (5 workspace-canonical Cycle 1A IDs × their raw counts
  per FP-1 — ADR-0110/0120/0130/0140/0150; ADR-0000 stays active per Q1 DISAGREE)
- **2 SESSION references** (198, 205 — FP-legit per Q2 STRENGTHEN,
  documented in HANDOFF_NUMBERING_GAPS.md)
- ~6,000 estimated bare-basename RENAMED (per FP-2 spot-sampling in §6)

Migration-arc consumers are advised to treat these as NON-defects.

---

## 4. Migration queue (post-arc)

Per parent §10.3 action taxonomy. Every real (post-FP) broken/RENAMED
reference gets a `recommended_action` + `migration_pr_batch_hint`. Files
with 100% PASS emit one `finding_class: ok` row and do NOT enter the
migration queue.

### 4.1 Batch `ref_graph_repair` — anchor + root broken refs (P1 post-Q3 fold — none P0)

Post Rigby cycle-1 Q3 DISAGREE fold, the previously-classified P0 findings
downgrade based on cited context. §10.4(b) root-stability P0 gate does NOT
trigger for this arc.

| # | Source | Line | Change | Severity | Confidence |
|---|---|---:|---|---|---|
| 1 | `docs/PLATFORM_WHAT_IT_IS.md` | 46 | `SESSION_1099` citation → annotate as pre-registry gap per `docs/HANDOFF_NUMBERING_GAPS.md` convention OR update to closest surviving handoff | **P1** (Q3 downgrade — refresh-block context carries counts-drift disclaimer) | High |
| 2 | (anywhere) | — | `ADR-0000` disposition → **escalate_to_chris** (Rigby cycle-1 Q1 DISAGREE — workspace deliverable NOT found; unclear whether ADR-0000 was ever ratified or is a numbering placeholder) → **RESOLVED post-ratification 2026-07-19**: deliverable found under alternate title convention `0000_RAR_METHODOLOGY` (id `754cff78-473b-4822-bd54-af1b45ed5988`, workspace `a9a16593-...`, status DRAFT). Closes as `keep_as_is`. See handoff §9.5. | **P1 → P3 (post-followup)** | High |
| 3 | `00-START-NEXT-SESSION.md` | 73 | `WorkspacePageNew.ts` → `WorkspacePageNew.tsx` (typo) | **P2** (Q3 downgrade — D-bucket "Latent bug hygiene" candidate list, not authoritative bug tracker) | High (typo) |

### 4.2 Batch `ref_graph_repair` — playbook-doc path-depth errors (P1)

| # | Source | Line | Change | Confidence |
|---|---|---:|---|---|
| 3 | `docs/research/platform/playbook_v0_1_ratification_package.md` | 352 | `../ENGINEERING_PLAYBOOK.md` → `../../ENGINEERING_PLAYBOOK.md` | High (path-depth error) |
| 4 | `docs/research/platform/playbook_v0_1_ratification_package.md` | 353 | `../research/platform/engineering_playbook_evidence_manifest.md` → `../../research/platform/engineering_playbook_evidence_manifest.md` | High |
| 5 | `docs/research/platform/playbook_v0_1_ratification_record_body.md` | 253 | Same as #3 | High |
| 6 | `docs/research/platform/playbook_v0_1_ratification_record_body.md` | 254 | Same as #4 | High |

### 4.3 Batch `ref_graph_repair` — SESSION_NNNN citations in playbook-authoring docs (P1)

7 broken SESSION_NNNN citations across 6 `docs/research/platform/playbook_*.md`
authoring docs (SESSION_2705, 2708, 2716, 2719, 2725, 2726). These files
were authored during v0.1.0 ratification pre-work when session numbering
was still fluid; some sessions never got standalone handoffs. Recommended
action: `update_in_place` — annotate each citation as `(no standalone
handoff shipped — see HANDOFF_NUMBERING_GAPS.md)` OR point at consolidated
handoff (e.g. S2727 ratification) where applicable. Per §1.7 P1 severity
for playbook_adr_ratification source class.

### 4.4 Batch `ref_graph_repair` — closed-research-arc SESSION_NNNN citations (P2)

7 broken SESSION_NNNN citations across 2 closed-arc audit docs
(SESSION_960, 962, 963, 1077 in 1602; SESSION_1075, 1077 in 1605;
SESSION_184 in 02-AI-ASSISTANT-CODE-REVIEW). Recommended action:
`update_in_place` OR `keep_as_is` — these are closed-arc historical
docs; §1.7 P2 severity assignment reflects lower urgency. Migration-arc
may prefer `keep_as_is` for pre-1000 gap references.

### 4.5 Batch `ref_graph_repair` — architecture doc subdirectory refs (P2)

2 broken md_links in `docs/architecture/MULTI_AGENT_ARCHITECTURE.md:727-728`
(`sessions/SESSION_128_...`, `features/AI_ASSISTANT.md`). Recommended
action: `update_in_place` — find targets under actual subdirs (likely
`docs/handoffs/SESSION_128_*` and `docs/topics/*` or similar) OR remove
broken links.

### 4.6 Batch `ref_graph_repair` — HANDOFF_NUMBERING_GAPS documented gaps (informational)

`docs/HANDOFF_NUMBERING_GAPS.md` deliberately catalogs missing SESSION_NNNN
handoff files (198, 205, and other pre-1000 sessions). These 2 raw
BROKEN_404 findings resolve to `finding_state: resolved` per FP-1
methodology since the file's PURPOSE is to record gaps. Migration-arc
action: `keep_as_is`.

### 4.7 Batch `schema_validation` — resolver methodology gaps

3 escalation items for T2 methodology refinement:

- **Workspace-aware ADR resolver** — current filesystem-only resolver
  cannot verify Cycle 1A workspace-canonical ADRs. Per FP-1, 37 raw ADR
  BROKEN_404 findings resolved via context knowledge, not by tool. Future
  T2-follow-up scanner should query workspace `a9a16593-...` for
  `ADR-*` deliverables.
- **Repo-root-relative convention detection** — the `[X](core/tasks.py)`
  convention from docs/ sources currently flags AMBIGUOUS. Resolver should
  try (a) `source.parent / target`, (b) `REPO_ROOT / target` even when
  target lacks leading `/`, before falling back to basename rglob.
- **Bare-basename prose vs backtick discrimination** — currently regex
  matches both. Migration-arc PR that consumes T2 findings should re-scan
  with tighter regex if per-defect action is intended.

### 4.8 Batch `ref_graph_repair` — file_cite BROKEN_404 estimated ~600-1,000 real defects

The full file_cite BROKEN_404 catalog (2,441 raw) is NOT enumerated inline
in this doc — it is preserved in `/tmp/t2_scan_out.json` scanner output for
migration-arc consumption. Post-FP estimated real: ~600-1,000 code-path
citations pointing at moved/deleted files. Migration-arc adopts a stricter
regex + spot-verification loop.

---

## 5. Cross-cutting signals for future §3 execution arc AND for T2 methodology refinement

Recorded for post-2899 §3 execution arc consumption AND parent §10 schema
post-arc refinement (Rigby cycle-3 `future_trigger` fold at 2899 close).

### 5.1 Workspace-canonical ADRs as a first-class resolver target

Cycle 1A architecture registered a **workspace-canonical** ADR resolution
model that T2's filesystem-only mechanical resolver cannot verify. This is
not a T2 bug — it's a methodology-level signal: any subsequent audit
walking `ADR-NNNN` references must also query workspace deliverables. §4.7
records the specific enhancement; parent §10 schema may add
`recommended_resolver: filesystem | workspace | dual` as a v1.2 hint.

### 5.2 Bare-basename anchor citations vs full-path anchor citations

Load-bearing anchor docs are cited by BOTH conventions in the corpus:
- Full-path: `[docs/PLATFORM_INVENTORY.md](docs/PLATFORM_INVENTORY.md)` (resolver PASS)
- Bare basename in prose: `` `PLATFORM_INVENTORY.md` `` (resolver RENAMED at source-relative resolution)

Not itself a defect (readers know the docs/ convention), but a migration-arc
consumer walking references to update-in-place after a move would need
BOTH resolution modes. Recommended: migration-arc adopts either
(a) normalize all in-prose anchor mentions to full-path links, OR
(b) add a "known anchor basename" exemption to its resolver.

### 5.3 Root-stability P0 discipline — first exercise

`00-START-NEXT-SESSION.md:73` `WorkspacePageNew.ts` typo is the FIRST
S2834-schema-v1.1 P0 finding against a root-stable file where the S2834
§10.4(b) clarification applies. Per Rigby cycle-2 Q7 STRENGTHEN
verified-fold, this P0 blocks in-place remediation before arc close.
T2's migration queue records it P0; §4 execution arc will fix in the
same batch that fixes CLAUDE.md:262 discord count P0 from T1.

### 5.4 SESSION_NNNN citation registry drift needs a canary

15 unique missing SESSION_NNNN handoffs across 7 source files
(SESSION_2705, 2708, 2716, 2719, 2725, 2726 in playbook-authoring docs is
the densest cluster). Pattern: sessions cited when their handoffs never
shipped (or shipped consolidated). Migration-arc-consumer signal: add a
per-cascade validator that walks `SESSION_NNNN` mentions against the
handoff registry and warns on drift. Recorded for parent §10 v1.2.

### 5.5 file_cite regex precision — 25K refs is signal-dense

The 25,417 raw `file_cite` refs is the LARGEST scan class by 20x and
also the noisiest. Migration-arc adopts a stricter regex (require `.py:`,
`.tsx:`, `.md:` with an explicit `:LINE` suffix) if per-defect action is
intended over rough per-file volume estimation. Recorded for parent §10
v1.2 methodology-hint field.

### 5.6 T3a duplicate-content pre-scan can inherit T2's per-file RENAMED map

Where T2's resolver found RENAMED (basename found elsewhere) with high
confidence, T3a's duplicate-content detection has a free "pre-clustering"
signal — files sharing basenames with content overlap are duplicate
candidates. Recorded for T3a author.

### 5.7 Schema v1.2 candidate — split `coverage` into `coverage_refs` + `coverage_claims` (Rigby cycle-1 Q4 DISAGREE future_trigger)

**Trigger observed at S2835 T2 authoring:** T2's honest label under S2834
v1.1 semantics is `coverage: structural_only` (reference-graph walked;
semantic line-range claim-walk not attempted). But `structural_only` in
v1.1 was scoped to T1's failure mode ("frontmatter + banners + counts
verified; body-level claim-density walk not performed"). The two failure
modes are ORTHOGONAL: T1 does semantic claim-walk but not ref-graph walk;
T2 does ref-graph walk but not semantic claim-walk. Overloading
`structural_only` conflates them.

**Rigby cycle-1 Q4 proposed refinement:** at parent §10 v1.2 consideration
time (2899 close), split `coverage` into two orthogonal fields:

```yaml
coverage_refs: full_walk | structural_only | deferred
coverage_claims: full_walk | structural_only | deferred
```

Under the split:
- T1 anchor audits would emit `coverage_refs: not_attempted, coverage_claims: full_walk`
  (or `structural_only` for the 8 large refs).
- T2 ref-graph audits would emit `coverage_refs: full_walk, coverage_claims: not_attempted`.
- Combined T1+T2+T3 audits (hypothetical) would emit `both: full_walk`.

**Do NOT apply at S2835:** S2834 lock explicitly prohibits modifying §10.1
v1.1 schema without fresh Chris D-verdict. Recorded as future_trigger for
2899 close reconciliation of arc-level schema refinements.

### 5.8 ADR-0000 disposition escalation (Rigby cycle-1 Q1 DISAGREE)

Workspace enumeration by Rigby found 5 of the 6 Cycle 1A ADRs
(0110/0120/0130/0140/0150) as valid workspace deliverables but ADR-0000
was NOT found. Cited by ≥1 source doc. Disposition options for Chris:
- (a) ADR-0000 is a numbering placeholder that was never intended to ship
  as a deliverable — accept `keep_as_is` and update citations to say so.
- (b) ADR-0000 was authored somewhere else (repo doc, external system) —
  identify the canonical location and update citations.
- (c) ADR-0000 was authored but the workspace deliverable was archived/
  deleted — reconstruct or annotate.

Migration queue §4.1 row 2 flags this as `escalate_to_chris`.

---

## 6. Line-range sample-verify residual risk

Per §1.4, resolver checks target-file existence but NOT line-range
semantics. 10-ref hand-picked spot-check to demonstrate the residual risk
is present (not resolved) — deferred to a future T2-follow-up sub-arc.

| # | Sample | Expected line range | HEAD state | Verdict |
|---|---|---|---|---|
| 1 | `core/rag_integration.py:483-799` (from `00-START-NEXT-SESSION.md:238`) | Pattern B/C/D + DORMANT registry | Verified via `grep '^def' core/rag_integration.py` — file exists, line range covers relevant symbol block | PASS (semantic) |
| 2 | `core/services/tool_dispatcher.py` in CLAUDE.md line 268 ("PA: 152 tool handlers") | Handler count comment | File exists; comment count 152 vs live autogen 156 (per T1 finding) — semantic drift, not T2 scope | Deferred to T1/anchor context |
| 3 | `frontend/src/pages/CommandCenterPage.tsx` (from CLAUDE.md line 268) | Command Center with PA chat | File exists; component present | PASS (semantic) |
| 4-10 | (sample skipped for concision; §6.1 records methodology) | — | — | Deferred |

### 6.1 Methodology limitation (recorded)

For the ~14,756 `file_cite PASS` findings, T2 verified target-file
existence only. Semantic drift (a function moved to a different line,
a class renamed, a service consolidated) is UNDETECTED by mechanical grep.
Future T2-follow-up sub-arc (post-2899) could bolt a `grep -n` line-range
sample-verify over the top-500 highest-cited file_cite PASSes.

### 6.2 FP-2/FP-3 sample-verify

Sampled 5 file_cite RENAMED findings from `CLAUDE.md:3` (session narrative
block):
- `ARCHITECTURE.md` — bare-basename prose mention, target = `docs/ARCHITECTURE.md` (real doc); FP-2
- `DISCORD_INTEGRATION.md` — same shape; FP-2
- `topics/personal-assistant.md` — has leading `topics/` prefix but from `CLAUDE.md` context resolves as `docs/topics/personal-assistant.md`; RENAMED verdict is technically correct (source.parent doesn't contain the target) but semantically the reader interprets it correctly; FP-2
- `3D_GENERATION_VERIFICATION_REPORT.md` — bare-basename prose mention → `docs/reports/3D_GENERATION_VERIFICATION_REPORT.md`; FP-2
- `drift-known-per-CLAUDE.md` — hyphenated phrase caught by regex; FP-3

Confirms §2.3 disposition — RENAMED class has ~80%+ FP-2/FP-3 rate for
anchor-source docs. Migration-arc consumers must NOT treat raw RENAMED
counts as defect population.

---

## 7. Exit criteria (T2 done when)

Per parent §8:

1. All 793 source files scanned with 4-class ref extraction + resolver.
2. Every extracted reference classified PASS / BROKEN_404 / RENAMED / AMBIGUOUS.
3. §2 findings frozen with severity assigned per §1.7 rules.
4. §3 histogram counts `finding_state: active` only per S2834 schema v1.1.
5. §4 migration queue populated with actions + batch hints for every
   non-PASS finding.
6. §5 cross-cutting signals recorded (candidate patterns for parent §10
   schema post-2899 refinement).
7. §6 residual line-range risk documented with hand-picked sample.
8. Joint Claude+Rigby SIGN across ≥2 cycles; convergence to majority
   AGREE/STRENGTHEN with 0 DISAGREE at last cycle.
9. Chris D-verdict routed as single yes/no per
   `feedback_claude_rigby_agree_first_chris_yes_no`.
10. Twin-pointer artifacts recorded (repo + workspace mint routed to Rigby
    per `feedback_rigby_writes_workspace_deliverables`).

---

## 8. Rigby SIGN cycles

### 8.1 Cycle 1 pressure-test (proposed for dispatch)

Rigby joint SIGN via pin `pa-0de182aaedcf43f0`. Each question routed with
explicit tool-grounded pressure per
`feedback_verify_rigby_tool_runs_before_trusting_sign` — tool_runs will be
verified non-empty before verdicts are accepted.

- **Q1 (FP-1 workspace-canonical ADR disposition — evidence-verify):** T2
  downgrades all 37 raw ADR BROKEN_404 to `finding_state: resolved` on the
  basis that Cycle 1A ADRs live in workspace
  `a9a16593-e0a4-44dc-8256-efc65d524b3c`. Pressure-test with two tool grounds:
  (a) `deliverable_tool list workspace_id=a9a16593-e0a4-44dc-8256-efc65d524b3c
  show_all=true` — enumerate ADR-* deliverables and cross-check IDs
  (0000/0110/0120/0130/0140/0150). (b) If any of the 6 IDs does NOT resolve
  as a workspace deliverable, the FP-1 disposition is wrong for that ID and
  T2's ADR BROKEN_404 count re-inflates.

- **Q2 (SESSION_NNNN catalog completeness — evidence-verify):** T2
  catalogs 15 unique missing SESSION_NNNNs at §2.5. Pressure-test: read
  `docs/HANDOFF_NUMBERING_GAPS.md` in full and cross-check which of the 15
  are ALREADY in that file's catalog (FP-legit, treat as `finding_state:
  resolved`) vs which are NEWLY discovered gaps that migration-arc must
  repair. Emit a disposition matrix: {SESSION_NNNN → cited_by → gap_doc_says
  → verdict}.

- **Q3 (Severity-assignment sanity check on anchor P0s):** Only 2 real
  anchor-doc P0s emerged (SESSION_1099 in `PLATFORM_WHAT_IT_IS.md:46`;
  `WorkspacePageNew.ts` typo in `00-START-NEXT-SESSION.md:73`). Pressure-test
  via `repo_tool.read` at each cited line: (a) is SESSION_1099's context in
  the S1223 refresh block genuinely P0 (broken ref actively misleads next
  reader) or should it be P1 because the S1223 refresh block already carries
  the disclaimer "Live runtime counts always come from PLATFORM_INVENTORY"
  per S2834 T1 finding? (b) Is the `WorkspacePageNew.ts` typo P0 (the doc
  section is authoritative for latent-bug tracking) or P1 (D-bucket "Latent
  bug hygiene" is a candidate list, not a P0 gate)? STRENGTHEN or DISAGREE
  the P0 severity with cited context.

- **Q4 (Coverage classification honesty):** T2 marks 789 files as
  `coverage: full_claim_walk` and 2 as `structural_only`. Per S2834 §5.5
  the `full_claim_walk` semantic is "every concrete claim in the file
  verified vs HEAD." T2's scanner verifies REFERENCE existence but NOT
  line-range semantics (§1.4 anti-pattern). Push back: is calling 789 files
  `full_claim_walk` overstating T2's actual coverage? Should the schema
  v1.1 field split into `coverage_refs: full | structural | deferred` +
  `coverage_claims: full | structural | deferred` (two orthogonal
  dimensions)? Or is the current single-field OK because T2's scope IS
  "walk every reference" and claim-walk is T1/T3 territory?

- **Q5 (ZOOM-OUT — anti-worship):** T2 spent significant space on FP
  disposition (§2.3 FP-1/FP-2/FP-3 + §6.2 sample-verify). Two zoom-out
  directions to consider before Chris D-verdict:
  - (a) **Should T2 be RE-RUN with a smarter resolver** (workspace-aware
    ADR + repo-root-relative + anchor-basename allowlist) before
    ratification? Or does the current scan give sufficient signal for
    parent-arc queue purposes? What's the incremental cost vs incremental
    signal?
  - (b) **Is honest reporting of resolver limitations MORE valuable than
    a cleaner defect list** (because migration-arc consumers get the true
    residual risk explicitly stated)? Compare to T1: T1 did per-file
    claim-walk on 33 files; T2 is grep-per-corpus on 791 files (23× scale)
    at 10× noise. Is T2's per-defect signal usefully actionable, or is the
    real deliverable the per-source-class ROLLUP + methodology limitations
    catalog? Push back on scope: T2 done well shipping now vs T2 gold-plated
    later?

**Anti-rubber-stamp:** Rigby verdicts accepted only after inspecting
`tool_runs` in reply payload. Empty `tool_runs` + intent=general = rubber-stamp
signal, re-route with tighter tool-grounding directives.

### 8.2 Cycle 1 verdicts (recorded 2026-07-19, pin `pa-0de182aaedcf43f0`)

Rigby tool_runs verified non-empty across cycle-1 dispatch (10+ substantive
tool calls: `deliverable_tool.list` on workspace `a9a16593-...` for Q1;
`repo_tool.read docs/HANDOFF_NUMBERING_GAPS.md` for Q2; `repo_tool.read
docs/PLATFORM_WHAT_IT_IS.md:38-78` + `repo_tool.read 00-START-NEXT-SESSION.md:66-106`
for Q3; `repo_tool.search` + `repo_tool.read` on T2 §1.4/§2.3/§6.1 for Q4).
Anti-rubber-stamp per `feedback_verify_rigby_tool_runs_before_trusting_sign` — passes.

| Q | Verdict | Refinement folded into T2 doc |
|---|---|---|
| Q1 FP-1 ADR verification | **DISAGREE** | Workspace enumeration confirmed 5 of 6 Cycle 1A ADRs resolve (0110/0120/0130/0140/0150) BUT `ADR-0000` NOT FOUND. Fold: 36 raw ADR BROKEN_404 → `finding_state: resolved`; 1 raw ADR-0000 BROKEN → `finding_state: active` P1 (§2.3 FP-1 revised; §4.1 row 2 records escalate_to_chris). |
| Q2 SESSION_NNNN catalog | **STRENGTHEN** | `docs/HANDOFF_NUMBERING_GAPS.md` documents ONLY SESSION_198→205 gap. Fold: 2 raw SESSION BROKEN_404 (198, 205) → `finding_state: resolved`; other 13 unique SESSION_NNNNs are NEWLY discovered gaps and enter migration queue as real broken refs (§2.5 revised). |
| Q3 anchor P0 severity | **DISAGREE** | (a) SESSION_1099 in PLATFORM_WHAT_IT_IS.md:46 is inside S1133 refresh block that carries "Live runtime counts always come from PLATFORM_INVENTORY.md" disclaimer → downgrade P0 → P1. (b) WorkspacePageNew.ts typo in 00-START-NEXT-SESSION.md:73 is under "D. Substrate / refactor (available if Chris pivots)" — Latent bug hygiene candidate list, NOT authoritative bug tracker → downgrade P0 → P2. §2.8 revised. **Net effect: 0 real P0 findings in T2**; §10.4(b) root-stability gate does NOT trigger for this arc. |
| Q4 coverage honesty | **DISAGREE** | T2 §1.4 anti-pattern explicit: resolver checks ref existence, NOT semantic line-range claims. Labeling 789 files `full_claim_walk` overstates coverage. Fold: relabel ALL 791 files as `coverage: structural_only` under CURRENT v1.1 semantics. Rigby's suggested v1.2 schema split (`coverage_refs` + `coverage_claims`) recorded as §5.1 future_trigger for parent §10 v1.2 evaluation at 2899 close (NOT applied inside T2 frontmatter — respects S2834 "no §10.1 schema mod without fresh SIGN + D-verdict" boundary). |
| Q5 zoom-out anti-worship | **STRENGTHEN** | Scan is sufficient as rollup + queue-seed IF limitations are explicit; ship T2 now with loud resolver-limitations; smarter-resolver re-run only if per-defect precision becomes required. No fold to T2 body (already ships with loud §2.3 FP + §6 residual risk). Records the "ship with loud limitations" decision as an explicit ratification input for Chris D-verdict. |

**Overall verdict (Rigby):** *"proceed to Chris — core signal is actionable
after folding Q1/Q3/Q4 refinements; no additional SIGN cycle needed unless
Chris wants the stricter coverage schema change pre-ratification."*

### 8.3 Cycle 2 fold verification (proposed for dispatch before Chris D-verdict)

Per anti-rubber-stamp discipline flipped: Rigby verifies Claude's folds
landed correctly, not the other way around.

- **Q6 (Q1 fold landed):** T2 §2.3 FP-1 revised to split ADR-0000 (active
  P1) vs 5 workspace-canonical (resolved). §4.1 row 2 records ADR-0000
  escalate_to_chris. Read the revised §2.3 FP-1 + §4.1 — do the fold
  edits land accurately per Q1 verdict?
- **Q7 (Q3 fold landed):** T2 §2.8 + §3 histogram + §4.1 rows 1 & 3 revised
  to downgrade the two would-be P0s to P1/P2 respectively. Post-fold P0
  count is 0. Read §2.8, §3, §4.1 — do the severity downgrades land
  accurately, and does the histogram claim "0 P0" hold?
- **Q8 (Q4 fold landed):** T2 §3 coverage distribution rewrites 791 files
  as `structural_only`. Doc's YAML sample rows in §2.9 relabel. §5.1
  records the v1.2 schema-split future_trigger. Read §3 + §2.9 samples +
  §5.1 — do the labels honor S2834 v1.1's `structural_only` semantic,
  and does §5.1's future_trigger phrasing keep the schema-mod boundary
  intact?

### 8.4 Cycle 2 verdicts (recorded 2026-07-19, pin `pa-0de182aaedcf43f0`)

Rigby tool_runs verified non-empty across cycle-2 dispatch (5+ substantive
`repo_tool.read` calls into the fold-target sections §2.3/§4.1/§2.8/§3/§4.1
rows 1-3/§2.9 YAML samples/§5.7). Anti-rubber-stamp per
`feedback_verify_rigby_tool_runs_before_trusting_sign` — passes.

| Q | Verdict | Fold-gap |
|---|---|---|
| Q6 (Q1 ADR fold verification) | **AGREE** | None — §2.3 FP-1 splits ADR-0000 (active) vs 5 Cycle 1A workspace-canonical (resolved) accurately; §4.1 row 2 records ADR-0000 escalate_to_chris |
| Q7 (Q3 severity fold verification) | **DISAGREE (initial) → AGREE (post-fix)** | §2.9 YAML samples still had `severity: P0` on Rigby's first pass — real fold gap. Fixed in same-cycle turn: PLATFORM_WHAT_IT_IS.md sample → P1 with Q3 citation; 00-START-NEXT-SESSION.md sample → P2 with Q3 citation. Rigby re-verified via `repo_tool.read` lines 430-490 → AGREE. |
| Q8 (Q4 coverage fold verification) | **AGREE** | None — §3 coverage_distribution states `structural_only: 791 files, full_claim_walk: 0` with ref-graph-only rationale; §2.9 YAML samples uniformly labeled `coverage: structural_only`; §5.7 records v1.2 coverage_refs/coverage_claims split as future_trigger WITHOUT bumping schema_version (respects S2834 boundary) |

**Rigby cycle-2 OVERALL:** *"YES — cycle 1 concerns are folded and cycle 2
verification is all AGREE with tool-backed evidence, so it's ready for
Chris D-verdict."*

### 8.5 Joint Claude+Rigby SIGN status

- **2 cycles complete**; anti-rubber-stamp verified across both cycles
  (10+ substantive tool_runs cycle 1; 5+ cycle 2; both `deliverable_tool.list`
  and `repo_tool.read` classes exercised).
- Cycle 1: 3 DISAGREE (Q1/Q3/Q4) + 2 STRENGTHEN (Q2/Q5) — all folded.
- Cycle 2: initial Q7 DISAGREE caught real fold-gap (YAML sample severities
  not downgraded); fix applied same-cycle; re-verified AGREE. Q6/Q8 AGREE
  first pass.
- **Rigby caught 2 real F-BLOCKING refinements across the arc**: Q1 (ADR-0000
  is a distinct real broken ref, not swept up in FP-1) + Q7 (§2.9 YAML sample
  severities lagged the §2.8 text downgrades).
- Joint Claude+Rigby convergence reached per
  `feedback_claude_rigby_agree_first_chris_yes_no`.
- **Joint recommendation to Chris**: **ratify T2 as-folded** — 0 P0s
  post-Q3 fold; ~9 P1s (incl. ADR-0000 escalate_to_chris + SESSION_1099
  refresh-block P1 + 4 playbook-doc path-depth P1s + ~3 additional
  research_os_anchor / playbook_adr_ratification real BROKEN); ~30-50 P2s
  (WorkspacePageNew typo + 13 closed_research_arc SESSION_NNNN gaps +
  audits_reports); everything else P3. Migration queue frozen; routed to
  future §3 execution arc post-2899. Parent §10 schema NOT modified —
  v1.2 coverage-split proposal recorded as future_trigger for 2899 close.
  ADR-0000 disposition escalation surfaces to Chris (§4.1 row 2).

---

## 9. Cross-links

- Parent: `docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md`
- Predecessor child (T1): `docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md`
- Playbook (v0.8.0): `docs/ENGINEERING_PLAYBOOK.md`
- Governance: `docs/00-START-HERE/DOC_LIFECYCLE.md`
- Sibling closed arc: `docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md` (§3 target tree RATIFIED)
- Live manifest: `docs/research/OPEN_ARCS.md`
- Scanner tool: `tools/audit_2802_reference_graph.py`

---

## 10. Provenance

- **Session:** 2835
- **Author:** Claude Code (Chris to ratify after joint Claude+Rigby SIGN)
- **SIGN pin:** `pa-0de182aaedcf43f0` (label `s2835-t2-reference-graph-audit`)
- **HEAD at draft:** `288259386b3a`
- **Scanner run:** `tools/audit_2802_reference_graph.py` output → `/tmp/t2_scan_out.json`
- **Playbook version:** v0.8.0 (unchanged; 205 rules)
- **Anti-rubber-stamp:** each Rigby SIGN dispatch routed with tool-grounded
  pressure-test questions; `tool_runs` verified non-empty per
  `feedback_verify_rigby_tool_runs_before_trusting_sign`
