---
title: "S2833 /docs/ Content Audit — Parent Architecture Scoping (Group 2800 mission plan)"
status: ratified (parent — Chris D-verdict 2026-07-19 S2833; D1-D9 locked; T1 opens at S2834)
authority: parent-doc for Group 2800 research arc
session: 2833
date: 2026-07-19
decisions_locked: 2026-07-19
ratification:
  date: 2026-07-19
  session: 2833
  ratifier: Chris
  verbatim_directive: "ratify D1-D9, open T1 next session"
  scope: full parent (D1-D9 including thread taxonomy, session-count estimate, machine-consumable per-file YAML schema, cross-arc consumption contract with §3 target-tree migration arc)
  envelope: docs/research/implementation/RATIFICATION_2026-07-19_2800_docs_content_audit_parent.md
  sign_cycles: 3 (Rigby joint SIGN pin pa-cc1dbcb7d18c4502; substantive tool_runs across all 3 cycles)
  next_action: T1 anchor & canonical-doc content audit opens at S2834 (child audit 2801_docs_content_anchors_audit.md)
domain_slug: docs_content_audit
research_group: 2800
authors: Claude Code (Chris directed at S2832 close — "open file-level audit arc")
supersedes: none
related:
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md
  - docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md      # sibling arc (structural)
  - docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md   # RATIFIED §3 target tree
  - docs/research/implementation/RATIFICATION_2026-07-19_2799_docs_restructuring.md         # S2832 ratification envelope
  - docs/research/OPEN_ARCS.md
  - docs/00-START-HERE/DOC_LIFECYCLE.md
  - docs/canon/INDEX.md
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - CLAUDE.md
  - 00-START-NEXT-SESSION.md
scope: Phase 0 domain-scoping — per-file content audit of the u-d-b `/docs/` corpus (stale-vs-HEAD, broken-refs, duplicate-content, orphan classification), complementing Group 2700's structural/statistical layer
non_goals:
  - the audits themselves (T1-Tn own those)
  - answering the 28 playbook questions verbatim (child audits adapt)
  - any file moves, deletions, renames, or content rewrites during the arc
  - any code or generator changes during the arc
  - redoing Group 2700's structural work (tree shape, subdir consolidation, audience matrix)
  - executing §3 target-tree moves from 2799 (ratification is destination-only; per-PR migration is separate arc)
delegates_to: none
owner: claude+rigby (Chris to ratify N-thread package at S2833 D-verdict)
---

# Session 2833 — /docs/ Content Audit Domain Scoping (Phase 0)

> **What this doc is.** A scoping deliverable produced *before* any child content-audit begins. Chris's exact directive at S2832 close (2026-07-19): *"ratify §3 today, open file-level audit arc"*. Group 2700 arc audited `/docs/` at structural/statistical level (dir tree, file counts, pattern extraction, audience matrix, rule-drift). This arc audits at CONTENT level — what each individual file actually says vs runtime truth, other docs, and reachability from anchors.
>
> **What this doc is not.** The audits themselves (T1-Tn own those). A proposal to rewrite doc content. Any authorization for file operations. A redo of Group 2700.

---

## 1. Why Phase 0

Chris's exact directive at S2832 close (2026-07-19), issued during the 2799 ratification session:

> Ratify §3 today, open file-level audit arc.

Follow-on context from S2832 handoff:

- Group 2700 arc covered `/docs/` at **STRUCTURAL/STATISTICAL** level: T1 inventoried 3247 files, T3/T4 sample-audited, T5 subset-focused, T6 rule-based across surfaces. The arc explicitly did **not** walk every file to check its content against reality — that was never in scope.
- Honest gap identified at S2832: **file-content-level audit** (per-file classification of stale/broken/duplicate/orphan by CONTENT, not by structural position).
- Chris D-verdict scoped narrowly: **§3 target tree RATIFIED** as destination shape only; **§7 anchor updates + §8 follow-on queue DEFERRED** (ratifiable separately); **file-content audit OPENS as separate arc**.

This arc exists because the S2832 ratification pre-committed a destination for `/docs/` restructuring, but the corpus has ~1842 in-scope files whose CONTENT may or may not survive a move to the target tree. Migrating a file with broken references or contradicts-runtime claims propagates the defect; migrating an orphan doc consumes SIGN budget on something no one reads. The content audit produces per-file classification that any subsequent migration PR consumes.

---

## 2. Existing constraints we honor (Cycle 1A verify-before-build)

Per `feedback_cycle_1a_verify_before_build` — end-state constraints already exist. Arc DESIGN operates UNDER them, not around them:

| Constraint | Source | What it locks |
|---|---|---|
| Sole authoritative counts | `DOC_LIFECYCLE.md` §2c | `PLATFORM_INVENTORY.md` + `docs/INDEX.md` are the ONLY counts sources. Audits classify claims-vs-inventory; never emit counts as authoritative. |
| Runtime-coupled paths (NEVER MOVE) | `DOC_LIFECYCLE.md` §2b | `docs/canon/`, `docs/governance/`, `docs/missions/`, `docs/decisions/ADR-*.md`, `docs/ops/` are read by Python at runtime. Content audit MAY classify content issues; MUST NOT propose moves that violate the path contract. |
| Root-stability | `DOC_LIFECYCLE.md` §3 | Anything referenced by `CLAUDE.md` / `00-START-NEXT-SESSION.md` / any `*_AUDIT.md` stays at cited path or leaves a permanent V2 stub. Content audit classifies drift; does not execute. |
| Canon size | `docs/canon/INDEX.md` | Canon is intentionally ≤10 docs. Audit does not inflate canon. |
| Context-kit scope boundary | `DOC_LIFECYCLE.md` §0 | `docs/docs-pattern/**` is context-kit framework, EXCLUDED from this audit. |
| DOC-POINTER-V1 / V2 pointer headers | `DOC_LIFECYCLE.md` §1 | Content-issue classification MAY recommend a V1 banner for stats-drift; V2 relocation is a Group 2700 §3 execution concern, not this arc's. |
| Autogen docs not hand-edited | Various | Files with `<!-- DOC-AUTOGEN -->` are regenerable — audit records staleness by naming the generator and last-run timestamp, not by proposing hand-edits. |
| Twin-pointer discipline | Memory `feedback_twin_deliverable_at_every_ratification` | Arc-close canonical summary needs both repo doc + workspace deliverable mirror. |
| Group 2700 §3 RATIFIED target tree | `2799` §3 + `RATIFICATION_2026-07-19_2799_docs_restructuring.md` | Audit CLASSIFIES per current tree; migration to target tree is a separate arc that consumes this arc's classification. Do not conflate. |
| Playbook v0.8.0 governance | `docs/ENGINEERING_PLAYBOOK.md` | PLAYBOOK-6.10.7/8/9 (zoom-out ask, fold-before-D-verdict, evidence admission) + 7.4.4 (recycle-after-merge) apply to every SIGN cycle. |

Arc scope is **CLASSIFICATION of content-level issues under these constraints, not the fixes themselves.** Any proposal that executes a fix (edit, move, delete) is out-of-scope; the audit records severity + recommended disposition, deferred to a subsequent migration arc.

---

## 3. Baseline evidence — what `/docs/` looks like at arc open (2026-07-19)

**Live `find` counts (this session, HEAD `9e986d5738aa`):**

| Bucket | .md count | In-scope? | Notes |
|---|---|---|---|
| `docs/` (total) | 3252 | — | S2811 T1 count was 3247; +5 drift from S2811-S2833 |
| `docs/archive/**` | 1388 | **NO** | Excluded per Group 2700 parent §7 anti-scope |
| `docs/docs-pattern/**` | 22 | **NO** | Excluded per DOC_LIFECYCLE §0 (context-kit framework) |
| **In-scope total** | **~1842** | YES | After the two exclusions |
| `docs/handoffs/**` | 1056 | scoped separately | See §4 T4 |
| `docs/research/**` | 253 | YES, minus in-flight arc children | 2700 + 2800 CHILDREN in progress; audit closed arcs only |
| `docs/audits/**` | 93 | YES | Includes 19 `SESSION_819_SYSTEM_AUDIT_*` cruft candidates (flagged at S2801 open) |
| `docs/reports/**` | 33 | YES (T5 territory) | Rigby cycle-2 Q3 evidence: sample (`3D_GENERATION_VERIFICATION_REPORT.md`) reads as one-shot/superseded snapshots (has V2 pointer) — belongs with audits triage, not with the T3a/T3b full-corpus scans |
| `docs/code-review/**` | 24 | YES (T3 territory) | Rigby cycle-2 Q3 evidence: sample (`00-REVIEW-ORCHESTRATOR.md`) reads as standing process/template material — stays in T3a/T3b scope |
| **Non-handoff in-scope (T1-T3 first cut)** | **~786** | YES | 1842 − 1056 handoffs |

**Deliberate scope split (Rigby SIGN Q1 candidate):**

- **T1-T3 walk the ~786 non-handoff files** — these are the "read-often, cited-often, drift-most" corpus. Contains anchors, topics, guides, features, architecture, plans, reports, patents, etc.
- **T4 addresses handoffs (1056 files) with a CITATION-INTEGRITY spot-check ONLY** — not per-file content review. Rationale: handoffs are terminal-by-design (write-once artifacts from a specific session); their "content" is the session receipt. What matters is (a) their citations still resolve after Group 2700's projected §3 moves, and (b) they aren't dragging stale counts into `search_docs` at the top of retrieval. This aligns with Group 2700 T5's already-proposed handoff lifecycle framework.
- **T-audits addresses `docs/audits/` (93 files) separately** — likely triage-and-archive recommendations rather than content edits.

---

## 4. Thread taxonomy (PROPOSED — pending Chris ratification)

Proposed **6-thread package** (T3 split into T3a/T3b per Rigby cycle-1 Q1 STRENGTHEN refinement — see §8). Each child ships at `2801..280N`. Canonical summary at `2899`. Playbook §9's 28 canonical questions apply, adapted where the child scope makes a question inapplicable.

### T1 — Anchor & canonical-doc content audit (`2801_docs_content_anchors_audit.md`)

- **Scope:** the ~30 "load-bearing" docs — anchors (`PLATFORM_WHAT_IT_IS`, `PLATFORM_INVENTORY`, `KNOWLEDGE_PIPELINE`, `UDB_BEHAVIOR_LAYER`, `UDB_TRANSLATION_LAYER`), canon rows, governance rows, root-README, `00-START-HERE/**`, `CLAUDE.md`. Per-file: does every claim survive against HEAD?
- **Method:** per file, walk each concrete claim (file path, function name, line range, count) and verify against HEAD. Emit finding rows with severity.
- **Deliverable:** per-file finding table + severity histogram + migration-queue notes.
- **First to run** (highest-impact / smallest-corpus).

### T2 — Reference-graph & broken-refs audit (`2802_docs_content_reference_audit.md`)

- **Scope:** relative-path links, ADR references (`ADR-NNNN`), session-handoff cross-refs (`SESSION_NNNN`), file-path citations (`core/services/X.py:LINE`) — across all in-scope files.
- **Method:** mechanical grep + resolver; classify PASS / 404 / renamed-target-exists-elsewhere / ambiguous.
- **Deliverable:** ref-graph table by source doc; per-target defect rate; migration-queue.
- **Anti-pattern to actively challenge:** "if grep says the target resolves, the reference is healthy." Some refs cite a specific line range that's semantically moved; sample-verify.

### T3a — Duplicate-content audit (`2803a_docs_content_duplicate_audit.md`)

- **Scope:** the ~786 non-handoff + 24 code-review = ~810 in-scope files. Substantial content overlap between two docs (governance drift risk per Group 2700 §4.4).
- **Method:** token-shingling / MinHash-style near-dup detection → top-K pair candidates → manual severity review on top ~100 pairs.
- **Deliverable:** duplicate-cluster catalog with severity (identical / near-identical / partial-overlap-load-bearing-both / partial-overlap-consolidate-candidate).
- **Explicitly out:** proposing merges or deletions — classification only.
- **Split rationale (Rigby cycle-1 Q1):** T3 originally bundled duplicate + orphan as two orthogonal full-corpus passes over the same ~800 files; splitting gives independent schedule control and lets T3b start on the mechanical reverse-index while T3a's manual review continues.

### T3b — Orphan & reachability audit (`2803b_docs_content_orphan_audit.md`)

- **Scope:** same ~810-file corpus as T3a.
- **Method:** reverse-index build → for each file, determine reachability from (a) CLAUDE.md anchor graph, (b) `docs/INDEX.md` autogen references, (c) `search_docs` corpus inclusion + top-K retrieval frequency for probe queries.
- **Deliverable:** orphan list with severity (unreachable-from-all-3-graphs / reachable-from-search-only / cited-but-search-invisible / cited-multi-graph-OK) + recommended disposition (candidate-for-archive / candidate-for-anchor-link / keep-as-is / unclear).
- **Explicitly out:** executing archive / anchor edits — classification only.

### T4 — Handoff citation-integrity + retrieval-harm audit (`2804_docs_content_handoff_audit.md`)

- **Scope:** the 1056 `docs/handoffs/*.md` files. Per-file content NOT reviewed except as noted in sub-loop (c).
- **Method:**
  - **(a) Citation-graph:** `grep` in-corpus for citations of the form `docs/handoffs/SESSION_NNNN*` and measure hit rate + decay curve.
  - **(b) Citation-integrity spot-check:** 10-doc sample per Group 2700 T5 substrate concern — do old `[docs/handoffs/SESSION_NNN.md#K]` fragment citations still resolve after any post-1143 chunk-ID resets?
  - **(c) Retrieval-harm / staleness-banner sub-loop (Rigby cycle-1 Q2 STRENGTHEN refinement):** for the top-K handoffs that surface in `search_docs` results for common operational queries (e.g. `"in-progress arc"`, `"how many spiders"`), inspect whether the handoff's claim-context is stale (arc closed, count drifted, superseded by later handoff) — evidence: Rigby's cycle-1 tool_run surfaced `SESSION_1301_MEMORY_RAG_RETRIEVAL_LANES.md` + `SESSION_368_DREAM_VALIDATION_UI.md` (archive) as top hits for `"in-progress arc"`. Deliverable = narrow list of handoffs recommended for DOC-POINTER-V1 stats-drift banner (not content edit; not per-file review of all 1056).
- **Deliverable:** citation-graph summary + spot-check results + retrieval-contribution histogram + retrieval-harm banner list.
- **Explicitly out:** per-handoff content review across the full 1056 corpus (still terminal-by-design; Group 2700 T5 already proposed lifecycle).

### T5 — Reports + audits triage (`2805_docs_content_reports_audits_triage.md`)

- **Scope:** `docs/audits/**` (93 files) + `docs/audit-2026/**` (15 files) + `docs/audit/**` (10 files) + 20 root-level `*_AUDIT.md` + **`docs/reports/**` (33 files — Rigby cycle-2 Q3 STRENGTHEN refinement; sample `3D_GENERATION_VERIFICATION_REPORT.md` has DOC-POINTER-V2 supersession banner already, read as one-shot snapshots)**. Includes the 19 `SESSION_819_SYSTEM_AUDIT_*` files currently untracked.
- **Method:** classify each by (a) one-shot session snapshot vs standing reference; (b) referenced from anchor graph vs orphan; (c) content-stale vs still-valid; (d) whether existing V1/V2 pointer already tells the right story.
- **Deliverable:** triage table + recommended disposition (archive / consolidate / keep-in-place / retrofit-V2-pointer) — deferred, not executed.

### `2899` — Canonical summary (arc close)

- **Scope:** cross-cutting synthesis + ratified content-audit findings + per-file classification catalog + migration-queue that Group 2700 §3 execution arc consumes.
- **Deliverable:** ratified content-audit output, twinned as workspace deliverable per `feedback_twin_deliverable_at_every_ratification`.
- **Ship shape:** migration/fixes execute in follow-up sessions, NOT during this arc.

---

## 5. Non-goals discipline (hard-line defer)

Per §7 anti-scope + Group 2700 parent §5 precedent:

- **NO file moves during arc.** Even obvious cruft stays in place. Note + defer to migration arc.
- **NO deletions during arc.** Same rule.
- **NO renames during arc.** Same rule.
- **NO content rewrites during arc.** No fixing a stale count in-line, no updating a broken link — classify + defer.
- **NO code / generator / autogen-rebuild changes during arc.** No `manage.py` command tweaks; no `docs_context_builder.py` edits; no forced `build_docs_index` runs (regular close-cascade runs are fine).
- **Each child audit ships a `## Migration Queue (post-arc)` section** — severity + exact path + rationale + recommended disposition.
- **NO redo of Group 2700 structural work.** If a content audit uncovers a structural issue not surfaced by 2700, note it in `## Cross-Cutting Signals for Group 2700 Retrospective` — do not re-open the parent.
- **PLAYBOOK-6.10.8 discipline preserved:** in-arc zoom-out folds MAY classify as `same_pr_mitigatable` for the CHILD DOC; never for `/docs/` file operations.

---

## 6. Recorded decisions (PROPOSED — Chris to lock at ratification)

| # | Decision | Rationale (proposed) |
|---|---|---|
| D1 | Content-audit arc opens at S2833 | Chris D-verdict S2832: "open file-level audit arc" |
| D2 | Arc group number = `2800` | Adjacent to Group 2700 structural sibling for navigation coherence; 2900 alternative rejected |
| D3 | Folder = `docs/research/domains/docs_content_audit/` | Matches existing NNxx domains convention |
| D4 | **6 threads** (T1 anchors / T2 refs / T3a duplicates / T3b orphans / T4 handoff-citations+retrieval-harm / T5 reports+audits triage) | Splits ~1842 corpus into severity-batched sub-arcs; T3 split (Rigby cycle-1 Q1); T4 adds retrieval-harm banner sub-loop (cycle-1 Q2); T5 absorbs `docs/reports/` (cycle-2 Q3) |
| D5 | Non-goals hard-line defer (no moves / deletes / renames / edits / code changes during arc) | Chris directive precedent from Group 2700 |
| D6 | Canonical summary at `2899` = ratified content-audit output | Migration ships as follow-up sessions post arc-close |
| D7 | Twin-pointer discipline for arc close | Content doc + workspace deliverable per `feedback_twin_deliverable_at_every_ratification` |
| D8 | **Session-count estimate ≥ 6 sessions** (revised from 4 per Rigby cycle-2 Q4 DISAGREE) | Mechanical greps fit in 1 session; T3a manual-confirm on top-100 dup pairs + T3b reachability grade-work + T5 triage each realistically take ≥1 session; canonical summary its own close cascade |
| D9 | **Output = machine-consumable per-file classification schema** (Rigby cycle-2 Q5 STRENGTHEN refinement — see §10; §10.1 locks YAML row shape per Rigby cycle-3 fold_class=future_trigger) | The future §3 execution arc CONSUMES this arc's output; without a defined schema at parent-scoping time, migration PRs re-litigate "what action per file?" |

---

## 7. Anti-scope

Out of Group 2800 even under the parent shape:

- **Context-kit framework** (`docs/docs-pattern/**`) — excluded per DOC_LIFECYCLE §0.
- **Archive tree** (`docs/archive/**`) — excluded per Group 2700 parent §7 anti-scope. Content is already-partitioned historical.
- **Per-handoff content review** — quarantined to citation-integrity only (T4). Handoffs are terminal-by-design write-once artifacts.
- **Runtime-coupled path movement** — DOC_LIFECYCLE §2b 5 rows are never-move under any output of this arc.
- **§3 target-tree execution** — that's a separate migration arc that consumes this arc's classification, not this arc's job.
- **Playbook governance surfaces** — `docs/ENGINEERING_PLAYBOOK.md` + ratification records are constitutional; audit may classify reference-drift but cannot propose content rewrites.
- **In-flight arc children** — Group 2700 child audits (2701-2706) and this arc's own children (2801-2805) are audited only after their own arc closes; do not audit in-flight children.
- **PLATFORM_INVENTORY.md counts editing** — audit classifies claims-vs-inventory drift; never rewrites the inventory itself (§2c).

---

## 8. Ratification protocol

**Joint Claude+Rigby SIGN before Chris D-verdict** (per `feedback_claude_rigby_agree_first_chris_yes_no`):

Rigby pressure-test questions proposed:

- **Q1 (scope split):** Is the 5-thread split the right shape, or does T3 (duplicate + orphan combined) risk running long? Split candidate: T3a duplicate / T3b orphan.
- **Q2 (T4 quarantine):** Is quarantining handoffs to citation-integrity only correct, or does per-handoff staleness (e.g., handoffs claiming an in-progress arc that already closed) leak into search_docs top-K and warrant content review?
- **Q3 (T5 audits scope):** Should T5 include `docs/code-review/` (24 files) and `docs/reports/` (33 files) since those are also session-artifact-like, or keep those in T3?
- **Q4 (session-count estimate):** With ~786 non-handoff files across T1-T3 + T4 automated citation scan + T5 triage, is a 4-session shape realistic (T1 + T2 + T3 + close cascade), or does T3's ~700-file walk need its own sub-arc split?
- **Q5 (zoom-out per `feedback_zoom_out_ask_per_rigby_sign`):** Where is this arc likely to accrete scope creep? What structural concern does the "content vs structural" split itself hide? Is there a coupling with the Group 2700 §3 migration arc that we're under-designing at parent-scoping time?

**Anti-rubber-stamp check per `feedback_verify_rigby_tool_runs_before_trusting_sign`:** Verify `tool_runs` non-empty on Rigby's SIGN reply before accepting AGREE/DISAGREE verdicts.

**Chris D-verdict slot:** ratifies thread taxonomy + session-count estimate + any Rigby refinements → child audits open in subsequent sessions.

---

## 9. What this parent scoping deliberately leaves open

- **T1..T5 in-thread rubric structures** — child audits author their own detection methodology per playbook §9's 28 questions (adapted); parent locks the per-file **output** schema (§10) but not the internal thread-specific detection approach.
- **Cross-arc dependencies** — if T2 (refs) flags a target that T1 (anchor) also flagged, canonical summary reconciles; parent does not preordain the reconciliation rule.
- **Post-arc migration arc number** — parent-scoping for that arc is out-of-scope here; opens after `2899` closes.
- **Which docs cross the P0/P1 severity line for the anchor set** — T1 authors that judgment.

**Deliberately LOCKED at parent (Rigby cycle-2 refinements):**

- Thread count = 6 (D4)
- Session count ≥ 6 (D8)
- Per-file output schema + severity + action taxonomies (§10 / D9)

---

## 10. Classification schema + action-recommendations (Rigby cycle-2 Q5 refinement)

**Why this section exists:** Rigby cycle-2 Q5 STRENGTHEN identified that this parent under-designs the machine-consumable output shape that Group 2700 §3 migration execution will consume. Without a defined schema at parent-scoping time, migration PRs re-litigate "what action per file?" and the audit's classification work leaks into every migration PR review. Locking the schema here forces each child audit (T1..T5) to emit findings in this shape.

### 10.1 Per-file finding row (canonical schema — all child audits MUST emit findings as a YAML block, one row per finding; parseable by downstream tooling per Rigby cycle-3 fold_class=future_trigger)

```yaml
- file_path: docs/topics/personal-assistant.md
  audit_thread: T1 | T2 | T3a | T3b | T4 | T5
  severity: P0 | P1 | P2 | P3
  finding_class: stale_vs_head | broken_ref | duplicate_content | orphan | superseded_untagged | retrieval_harm | ok
  evidence:
    - line_range: [45, 62]
      claim: "PA tools count = 152 handlers"
      runtime_truth: "156 handlers per PLATFORM_INVENTORY.md"
      cited_source: docs/PLATFORM_INVENTORY.md
  recommended_action: keep_as_is | update_in_place | retrofit_v1_pointer | retrofit_v2_pointer | consolidate_into | archive | delete | escalate_to_chris
  action_target: null | <destination path when action = retrofit_v2_pointer or consolidate_into>
  migration_pr_batch_hint: anchor_docs | topic_docs | audits_triage | handoffs_banner | orphans_archive | dup_consolidate
  cross_arc_refs:
    - 2799_3_target_tree_row: <row-ID from 2799 §3.1 if the recommended_action lands the file in a different subdir under §3>
  notes: <free text if severity classification needs justification>
```

### 10.2 Severity taxonomy

- **P0** — actively misleading (e.g. count claim contradicts PLATFORM_INVENTORY; broken ref in a load-bearing anchor; orphan cited by a P0 doc)
- **P1** — stale but non-misleading (superseded content that lacks a V1/V2 pointer; near-duplicate of a stronger doc)
- **P2** — cosmetic / low-impact (broken ref in a low-cited doc; orphan with no downstream consumers)
- **P3** — informational only (documented-as-historical; already has V2 pointer; audit outcome = OK)

### 10.3 Action taxonomy

Actions map 1:1 to a migration-PR class the follow-on §3 execution arc consumes:

- `keep_as_is` — no migration action
- `update_in_place` — content edit (fix stale count, broken ref, etc.) — separate PR per doc, small
- `retrofit_v1_pointer` — stats-drift banner per DOC_LIFECYCLE §1 (in-place)
- `retrofit_v2_pointer` — supersession/relocation pointer per DOC_LIFECYCLE §1 (in-place)
- `consolidate_into <target>` — merge candidate into named target (requires action_target)
- `archive` — move to `docs/archive/YYYY-MM/`
- `delete` — hard delete (rare; only when zero cited references and file is unambiguous cruft)
- `escalate_to_chris` — audit can't classify without Chris directive (e.g. subject-matter judgment)

### 10.4 Cross-arc consumption contract

Group 2700 §3 target-tree migration arc, when it opens, will read this arc's canonical summary (`2899`) as its input contract:

- For every ratified §3 target-tree row (2799 §3.1), the migration arc queries "for every file currently in the source path that 2799 §3 would move to this target path, what's the 2800 recommended_action?"
- Migration PRs group by `migration_pr_batch_hint` — one PR per batch, easier review, obvious scope.
- Files with `severity=P0` block the destination subdir migration until fixed; P1 flow through; P2/P3 non-blocking.

This is the contract 2800 exists to produce. Without it, §3 execution is a re-audit-in-line-of-PR-review; with it, §3 execution is mechanical.

---

## 11. Cross-links

- Sibling structural arc: `docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md` (§3 RATIFIED destination; §7/§8 DEFERRED)
- Ratification envelope: `docs/research/implementation/RATIFICATION_2026-07-19_2799_docs_restructuring.md`
- S2832 handoff: `docs/handoffs/SESSION_2832_RATIFY_2799_DOCS_RESTRUCTURING.md`
- Playbook (v0.8.0): `docs/ENGINEERING_PLAYBOOK.md`
- Governance canonical: `docs/00-START-HERE/DOC_LIFECYCLE.md`
- Live manifest: `docs/research/OPEN_ARCS.md` (this arc registered post-Chris-D-verdict)
