---
title: "S2836 T3a — /docs/ Content Audit · Duplicate-Content Audit (child audit 2803a)"
status: ratified (T3a — Chris D-verdict 2026-07-19 S2836; joint Claude+Rigby SIGN 2 cycles; folds applied + verified; needs-judgment escalations DEFERRED to arc close per Chris D-verdict)
authority: child audit under Group 2800 (2800 parent-scoping RATIFIED at S2833 D1-D9; 2801 T1 RATIFIED at S2834 with schema v1.1; 2802 T2 RATIFIED at S2835; 2803a T3a RATIFIED at S2836)
ratification:
  date: 2026-07-19
  session: 2836
  ratifier: Chris
  verbatim_directive: "Continue on but let's defer the two issue and any others like it until we have the /docs/ audit completed incase other issues come up"
  scope: full T3a (792-file corpus scan; 1 AGREE + 4 STRENGTHEN folded in cycle 1; 4 AGREE in cycle 2; needs-judgment escalations DEFER-UNTIL-ARC-CLOSE per D-verdict; T3a↔T5 boundary rule adopted; §10.1 v1.1 schema unchanged; v1.2 acceptance criteria codified in §5.3)
  envelope: docs/research/implementation/RATIFICATION_2026-07-19_2803a_docs_content_duplicate_audit.md
  sign_cycles: 2 (Rigby joint SIGN pin pa-90ea529a09234d57; anti-rubber-stamp verified; cycle 1 → 1 AGREE + 4 STRENGTHEN → folded; cycle 2 → 4/4 AGREE)
  chris_directive_new_policy: "needs-judgment escalations across T3a/T3b/T4/T5 defer to arc close (2899 canonical summary time), NOT resolved child-by-child; other T-thread findings may inform the judgment"
  next_action: T3b orphan & reachability audit opens at S2837 (child audit 2803b_docs_content_orphan_audit.md); needs-judgment queue accumulates across all children; batch resolution at 2899 close
session: 2836
date: 2026-07-19
domain_slug: docs_content_audit
research_group: 2800
thread: T3a
schema_version: 1.1  # inherited from parent §10.1 v1.1 locked at S2834
authors: Claude Code (Chris directed at S2836 open — "Let's continue with B" = ratified default from S2835 D-verdict)
parent:
  - docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md
predecessor_child:
  - docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md
  - docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md
supersedes: none
related:
  - docs/research/implementation/RATIFICATION_2026-07-19_2802_docs_content_reference_audit.md
  - docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md
  - docs/00-START-HERE/DOC_LIFECYCLE.md
scope: >
  Duplicate-content audit of the ~792-file non-handoff in-scope /docs/ + root
  corpus. Token-shingling / inverted-index Jaccard near-duplicate detection.
  Consumes T2 §5.6 pre-clustering signal (RENAMED basename map). Classifies
  candidate pairs by severity (identical / near-identical / partial-overlap-
  load-bearing-both / partial-overlap-consolidate-candidate) per parent §4
  T3a rubric. Emits YAML findings per parent §10.1 v1.1 schema.
non_goals:
  - proposing merges or deletions (classification only per parent §5)
  - moves / renames / rewrites during the audit
  - orphan / reachability classification (T3b territory)
  - reference-graph validation (T2 territory)
  - anchor / canonical-doc content walk (T1 territory)
  - modifying §10.1 v1.1 schema (locked at S2834)
  - auditing handoff-source content (T4 territory)
  - reports / audits triage classification (T5 territory)
  - auditing in-flight Group 2800 arc children (this arc's own docs)
head_at_open: 13e0cc52b7e3  # S2835 close cascade
inventory_generated_at: 2026-07-05 15:51:41  # per docs/PLATFORM_INVENTORY.md
inventory_head: e617af59
scanner_tool: tools/audit_2803a_duplicate_content.py
scanner_out: /tmp/t3a_dup_scan_out_full.json
scanner_out_substantive: /tmp/t3a_dup_scan_substantive.json  # V2-stub-filtered
t2_pre_clustering_seed: /tmp/t2_scan_out.json  # RENAMED basename map per T2 §5.6
owner: claude+rigby (Chris to ratify)
---

# S2836 — T3a Duplicate-Content Audit

> **What this doc is.** Group 2800's third child audit. Token-shingling +
> inverted-index Jaccard near-duplicate detection across the ~792-file
> non-handoff corpus; emits per-pair severity classification per parent
> §4 T3a rubric; sizes the consolidate-vs-keep migration queue that a
> future §3 execution arc consumes.
>
> **What this doc is not.** A merge proposal. A deletion manifest. A
> content rewrite. An orphan/reachability audit (that's T3b). A
> reference-graph audit (T2 territory). Findings classify severity +
> `recommended_action`; execution defers to a follow-on migration arc
> (post-2899).

---

## 1. Method

### 1.1 Corpus selection — 792 source files (same as T2 non-handoff scope)

Per parent §4 T3a scope ("the ~786 non-handoff + 24 code-review = ~810
in-scope files"), T3a scans the same non-handoff corpus as T2:

| Bucket | # source files | Notes |
|---|---:|---|
| `docs/**` in-scope, minus handoffs / archive / docs-pattern / in-flight-arc-children | 789 | Same rglob + exclusion rules as T2 scanner |
| Root anchors | 3 | `CLAUDE.md`, `00-START-NEXT-SESSION.md`, `README.md` |
| **Total sources** | **792** | (T2 had 791; +1 drift is likely new file since S2835 close) |

**Explicitly OUT of T3a corpus (identical to T2 exclusions):**

- `docs/handoffs/**` (1058 files) — parent §3 scope split routes handoffs to T4.
- `docs/archive/**` (1388 files) — parent §7 anti-scope.
- `docs/docs-pattern/**` (22 files) — DOC_LIFECYCLE §0 (context-kit framework).
- `docs/research/domains/docs_content_audit/**` — this arc's own children,
  per parent §7 "do not audit in-flight arc children."

**Notably IN scope:** `docs/ENGINEERING_PLAYBOOK.md`, `docs/decisions/ADR-*.md`,
`docs/research/domains/docs_restructuring/**` (Group 2700 CLOSED), and
`docs/research/implementation/**` (ratification envelopes).

### 1.2 Text normalization

Per line 84-91 of `tools/audit_2803a_duplicate_content.py`:

1. Strip YAML frontmatter (`\A---\n.*?\n---\n`).
2. Strip fenced code blocks (` ``` … ``` `). Rationale: code blocks are
   high-signal for reference-graph work (T2) but drive false-positive
   duplicate detection here (identical import blocks across two unrelated
   docs). T3a discards them.
3. Preserve markdown link labels; discard link targets.
4. Lowercase, whitespace-collapse.

### 1.3 Shingling

5-word overlapping token shingles as a Python `set`. Rationale (per
parent §4 T3a): standard MinHash-family choice for near-duplicate
detection; shingle size 5 balances precision (rare shingles = strong
match signal) with recall (short overlap regions still detectable).
Higher shingle sizes (7, 10) tested by prior art but 5 is the working
default for markdown corpora.

### 1.4 Similarity metric

For each pair sharing ≥1 shingle, compute exact Jaccard similarity:

```
J(A, B) = |shingles(A) ∩ shingles(B)| / |shingles(A) ∪ shingles(B)|
```

Also compute two **containment scores** to catch subset-overlap
(one file is largely contained within a longer file):

```
containment_A = |A ∩ B| / |A|
containment_B = |A ∩ B| / |B|
```

Ranking uses `max(jaccard, containment_A, containment_B)` — this catches
both symmetric near-identicals AND asymmetric subset-overlaps. Sibling
V2-pointer-stub docs (identical 8-line templates differing only in a
target-path line) score max ≥ 0.90 via Jaccard; a 20KB doc containing a
2KB stub as its opening block would score containment_B ≈ 1.0 with
low Jaccard.

**Design note (recorded — Rigby anticipated challenge):** the
containment metric is the OPPOSITE of a Jaccard-only ranker. Jaccard
alone treats size asymmetry as a negative signal; containment surfaces
it. Both matter for the T3a rubric (identical vs near-identical need
Jaccard; partial-overlap-consolidate-candidate needs containment).

### 1.5 Pre-clustering signal from T2 (per parent §5.6)

T2's `/tmp/t2_scan_out.json` per-file findings include a `RENAMED`
classification: reference target's basename EXISTS elsewhere in the
corpus. Scanner extracts a `basename → {resolved-paths}` map (3,745
basenames at S2835 T2 close) and flags each T3a pair whose either-side
basename appears in T2's map with `t2_renamed_signal: true`. This is a
FREE pre-clustering hint (no additional grep pass) that surfaces
basename-collision candidates without waiting for the Jaccard score.

**Consumption note:** the flag is **advisory** — a `true` value
correlates with duplicate-candidate density but does not classify by
itself. Manual review still owns severity.

### 1.6 Severity taxonomy (per parent §4 T3a rubric)

Per parent §4 T3a lock:

| Severity | Meaning | Recommended action |
|---|---|---|
| `identical` | Jaccard ≥ 0.95; content substantively duplicated | `consolidate_into <target>` (canonical file kept, others archived); OR `escalate_to_chris` for redundancy justification |
| `near-identical` | 0.75 ≤ Jaccard < 0.95; substantial overlap; small deltas (per-session snapshots, timestamp variants) | `consolidate_into <target>` (usually latest is canonical) |
| `partial-overlap-load-bearing-both` | Both files serve independent purposes despite content overlap (e.g. intentional template stubs, source-vs-summary pairs, authoring-vs-canonical) | `keep_as_is` |
| `partial-overlap-consolidate-candidate` | One file substantially subsumed by other; likely obsolete draft/split | `consolidate_into <target>` |

### 1.7 Anti-pattern to actively challenge (per parent §4 T3a)

Parent explicitly warns: *"identical content = trivially deletable
duplicate. Some near-duplicates are intentional load-bearing-both."*

**T3a stance:** the top-ranked results include ~1,800 V2-pointer-stub
pairs at Jaccard ~0.86. These are INTENTIONAL Session 1143 DOC-POINTER-V2
supersession forwarders (see §2.3). Naïve classification would flag
them all as consolidate candidates. Manual review reclassifies as
`partial-overlap-load-bearing-both` — the boilerplate IS the point
(link-rot prevention); the differing line IS the payload.

**Rule of thumb applied by manual review:**
- If both files are <800 bytes AND contain a `DOC-POINTER-V2` header →
  `partial-overlap-load-bearing-both`, action `keep_as_is`.
- If one file's DELTA vs the other is a functional payload (a specific
  target path, a specific session_id, a specific claim) that would be
  LOST on merge → `partial-overlap-load-bearing-both`.
- Otherwise → default to `consolidate_into <target>`.

---

## 2. Findings

Findings grouped by severity class. All rows emit under §10.1 v1.1
schema (§4 migration queue and §7 YAML samples below). Whole-doc
severity summary in §3.

### 2.1 SESSION_819_SYSTEM_AUDIT_* cluster — 19 files, 171 IDENTICAL pairs (P1)

The 19 untracked `docs/audits/SESSION_819_SYSTEM_AUDIT_YYYYMMDD_HHMMSS.md`
files first flagged at S2801 open (`git status ??` list) surface as the
single largest duplicate cluster in the corpus:

- **File count:** 19
- **Pair count:** 19 × 18 / 2 = **171 pair combinations**
- **Jaccard range:** 0.928 – 0.960 (all above 0.95 identity threshold or
  just below at 0.93+)
- **File size:** ~2 KB each; ~38 KB total footprint
- **Filename convention:** `SESSION_819_SYSTEM_AUDIT_<YYYYMMDD>_<HHMMSS>.md`
  — 15 timestamped snapshots between 2026-07-14 22:31 UTC and 2026-07-16 12:57 UTC

**Sample pair (rank 1):**
- `docs/audits/SESSION_819_SYSTEM_AUDIT_20260716_024835.md`
- `docs/audits/SESSION_819_SYSTEM_AUDIT_20260716_024836.md`
- Jaccard 0.960 · containment_A 0.979 · containment_B 0.979
- Timestamps differ by 1 second

**Content type:** Each file is a repeated audit-runner snapshot (script
output, not authored by a session). The header line and 1-2 metric
lines drift across snapshots; the rest is identical structural output.

**Classification:** `identical` at cluster level. All 19 rows collapse
to a single migration-queue action.

**Recommended action:** `archive` — move to
`docs/archive/2026-07/audits/session_819_snapshots/`. Rationale (per
DOC_LIFECYCLE): (a) these are one-shot script outputs, not authored
docs; (b) if the audit is worth preserving as a signal, the LATEST
snapshot is canonical and prior ones are redundant; (c) if the audit
runner is still active, its NEXT snapshot supersedes ALL prior ones.

**Escalate to Chris:** was the SESSION_819 audit-runner supposed to
be idempotent (overwrite one file) or accumulating (one per run)?
Answer determines whether the runner needs a scripted fix in addition
to the archive.

**Runner-independence proof (Rigby cycle-1 Q2 STRENGTHEN fold):**
Rigby's tool-grounded search of `core/management/commands/` for
`SESSION_819` returned **zero matches** — no runtime/runner code
references the SESSION_819 snapshot paths. Archive of the 19 files is
therefore safe from runner-code dependency; the archive can ship
independently of the runner-fix follow-up. Both work-items track in
parallel (archive PR + runner-fix ticket), not sequentially.

**Migration queue batch hint:** `audits_triage` (per parent §10.3;
T5 territory has the audits-triage bucket). Per Rigby cycle-1 Q5
STRENGTHEN (T3a↔T5 boundary): T3a's `archive` recommendation here is
the DUPLICATE-level classification — T5 (reports+audits triage) may
override with a different disposition (e.g. rotate-and-retain latest 3
snapshots vs archive all) if audits-context reveals value in a rolling
snapshot window. T3a defers final disposition to T5.

### 2.2 PA_TOOLS_GAP_MAP_S2795 / S2796 — 1 near-identical consecutive-session pair (P1)

- `docs/audits/PA_TOOLS_GAP_MAP_S2795.md` (19 KB, 308 lines)
- `docs/audits/PA_TOOLS_GAP_MAP_S2796.md` (19 KB, 305 lines)
- Jaccard 0.912 · containment_A 0.956 · containment_B 0.952

Two consecutive session snapshots of a PA-tools gap analysis. Near-
identical content with small session-delta.

**Classification:** `near-identical`.

**Recommended action:** `consolidate_into docs/audits/PA_TOOLS_GAP_MAP_S2796.md`
(most recent) — the S2795 file supersedes to the S2796 revision.
Alternative: `retrofit_v2_pointer` on S2795 pointing at S2796 (per
DOC_LIFECYCLE §1 pattern).

**Migration queue batch hint:** `audits_triage`.

### 2.3 DOC-POINTER-V2 stub cluster — 110 files, ~1,770 pair combinations (P3 · load-bearing-both)

At Jaccard ~0.86 the scanner surfaces the **Session 1143 Phase 2B-1
archive pointer** cluster: 110 tiny (typically 8-line) files whose sole
purpose is to redirect readers away from an in-repo path to an archived
canonical version. Boilerplate template (7 lines) + 1 changing line
(target archive path) drives the ~0.86 Jaccard.

**Cluster shape (per T3a scanner V2-stub filter):**

| Subdir | # V2 stubs |
|---|---:|
| `docs/guides/` | 18 |
| `docs/features/` | 18 |
| `docs/agents/` | 8 |
| `docs/apis/` | 8 |
| `docs/pre-launch/` | 8 |
| `docs/body/` | 6 |
| `docs/BUGS/`, `docs/integrations/`, `docs/workflows/` | 2 each |
| Root-level `docs/*.md` V2 stubs | 30+ (single-file entries; each pairs with sibling stubs) |
| **Total files** | **110+** |
| **Total pair combinations in top-2000** | **~1,770** |

**Sample V2 stub body (identical across cluster except one line):**

```markdown
<!-- DOC-POINTER-V2 (Session 1143) -->
> **Status:** Moved
> **Originally:** subdir doc frozen since Jan/Feb 2026; identified by
> Session 1143 corpus audit as Phase 2B-1 archive candidate
> **Last verified:** Session 1143 (2026-05-25)
> **Current canon:** [`../archive/superseded-2026-05/…/<FILENAME>.md`](…)
> — read this instead.
> **Change reason:** subdir frozen since Jan/Feb 2026; archived to
> reduce active surface area.
> **Preserved because:** white-paper corpus / link-rot prevention.
> **Caveat:** Prior RAG citations may no longer resolve to the same chunk_id.
---
```

**Classification:** `partial-overlap-load-bearing-both` at cluster level.

**Rationale — why this is NOT a consolidate-candidate cluster:**

1. **Link-rot prevention IS the point.** Each stub occupies the historical
   repo path so that pre-1143 external references (RAG citations, ADR
   citations, `search_docs` hits, ChatGPT/Claude session references) still
   resolve to *something* — a machine-readable pointer to the true canon.
2. **The delta line IS the payload.** The ONE line that differs across
   stubs — the target archive path — is the functional content. Merging
   would destroy the payload.
3. **DOC_LIFECYCLE §1 codifies the pattern.** V2 pointers are a
   first-class governance mechanism; per DOC_LIFECYCLE §1 the pattern
   is intended to persist indefinitely for the docs affected.

**Recommended action:** `keep_as_is` for all 110 files.

**Cross-cutting signal (recorded for T3a own §5):** V2-stub-vs-V2-stub
pairs dominate raw Jaccard rankings. A future T3a-follow-up scanner
could pre-filter files matching `<!-- DOC-POINTER-V2` to make the
substantive-vs-boilerplate ratio cleaner. **Not applied here** — kept
in the scan so downstream reviewers can see the noise floor.

**Migration queue batch hint:** none (`keep_as_is`).

### 2.4 SYSTEM_ARCHITECTURE_MAP.md vs SYSTEM_MAP.md — architecture-subdir consolidate candidate (P2)

- `docs/architecture/SYSTEM_ARCHITECTURE_MAP.md` (25 KB)
- `docs/architecture/SYSTEM_MAP.md` (26 KB)
- Jaccard 0.163 · containment_max 0.418

Two `docs/architecture/` docs with substantial overlap by containment
metric. Same subdir, similar naming, likely two authored answers to the
same question.

**Classification:** `partial-overlap-consolidate-candidate` (pending
spot-verify — see §6). Sub-classification (Rigby cycle-1 Q3 STRENGTHEN):
this row is `needs-judgment` (canonical-ambiguous), NOT
`consolidate-into-known-target`. See §5.7 for the v1.2 candidate
severity split.

**Recommended action:** `escalate_to_chris` — determine which is
canonical; consolidate the other. Not `consolidate_into` directly
because subject-matter judgment needed (which map is right?).

**Migration queue batch hint:** `topic_docs` (T1 anchor batch hint;
architecture docs are semi-anchor).

### 2.5 CLAUDE_CONTEXT_SYSTEM_PACK.md vs SYSTEM_FULL_ACTIVATION_PLAN.md — plans-subdir subset (P2)

- `docs/plans/CLAUDE_CONTEXT_SYSTEM_PACK.md` (63 KB)
- `docs/plans/SYSTEM_FULL_ACTIVATION_PLAN.md` (19 KB)
- Jaccard 0.217 · containment_A 0.164 · containment_B 0.694

The smaller SYSTEM_FULL_ACTIVATION_PLAN.md is ~69% contained within the
larger CLAUDE_CONTEXT_SYSTEM_PACK.md. Likely one is a chapter/subset of
the other.

**Classification:** `partial-overlap-consolidate-candidate`.
Sub-classification (Rigby cycle-1 Q3 STRENGTHEN): `needs-judgment`
per §5.7 v1.2 candidate.

**Recommended action:** `escalate_to_chris` — one candidate is
subject-matter subset of other; verify which is source-of-truth and
recommend `consolidate_into` or `retrofit_v2_pointer`.

**Migration queue batch hint:** `topic_docs`.

### 2.6 ENGINEERING_PLAYBOOK.md vs playbook_authoring_session_2716/2718/2720 — load-bearing-both (P3)

- `docs/ENGINEERING_PLAYBOOK.md` (175 KB, constitutional)
- `docs/research/platform/playbook_authoring_session_2716.md` (54 KB)
- `docs/research/platform/playbook_authoring_session_2718.md` (47 KB)
- `docs/research/platform/playbook_authoring_session_2720.md` (67 KB)
- Containment_B range: 0.42 – 0.69 (playbook contains substantial
  authoring content per session)

**Classification:** `partial-overlap-load-bearing-both`.

**Rationale:** the ENGINEERING_PLAYBOOK.md is the CURRENT constitutional
text; the authoring session docs are the HISTORICAL RECORD of how each
rule was authored (evidence trail, verdict provenance, Chris ratification
context). Per Playbook v0.1.0 ratification methodology (S2727), the
authoring record is preserved as evidence for future methodology reviews.
Neither is redundant to the other — they serve orthogonal purposes.

**Recommended action:** `keep_as_is` for all four files.

**Migration queue batch hint:** none.

### 2.7 I-0100 phase acceptance docs vs their siblings — load-bearing-both (P3)

- `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_p3_local_activation_acceptance.md` (15 KB)
- `docs/research/implementation/observability_spine_mission_evidence_substrate/I-0100_p4_local_activation_acceptance.md` (9 KB)
- Jaccard 0.176 · containment_max 0.377

Sibling phase acceptance docs. Structurally similar template + different
phase evidence.

**Classification:** `partial-overlap-load-bearing-both`.

**Rationale:** each phase is a distinct ratification checkpoint; per
IOS methodology (v1.5) both are canonical records for their respective
phases. Overlap is template + shared constraint text; deltas are the
phase-specific evidence.

**Recommended action:** `keep_as_is`.

Same pattern applies to `RATIFICATION_2026-07-10_i0302_arc_close.md` +
`RATIFICATION_2026-07-10_i0302_phase4_close.md` (rank 10, containment_max
0.320) — sibling ratification envelopes for adjacent phase + arc close.

**Migration queue batch hint:** none.

### 2.8 App-brief template family — load-bearing-both (P3)

- `docs/apps/compliancesentinel_BRIEF.md` (12 KB)
- `docs/apps/sellerpilot_BRIEF.md` (10 KB)
- `docs/apps/dealflowtracker_BRIEF.md` (8 KB)
- `docs/apps/pitchdeckforge_BRIEF.md` (8 KB)
- `docs/apps/mentorforge_BRIEF.md` (9 KB)
- Containment_max range: 0.30 – 0.37 across pairs (5 pairs surfaced
  in top-2000 non-cluster results)

**Classification:** `partial-overlap-load-bearing-both`.

**Rationale:** `docs/apps/` is a Suite-consumer template family — each
BRIEF is a distinct product spec authored to a common template. Overlap
= template scaffolding (positioning, ICP, monetization, integration
surface); delta = product-specific content. Deleting one destroys a
canonical product spec.

**Recommended action:** `keep_as_is` for all files in this family.

**Migration queue batch hint:** none.

### 2.9 Cross-domain audit siblings — load-bearing-both (P3)

- `docs/research/domains/authority_enforcement/1904_authority_enforcement_cat_f_adjacent_separation_boundaries_child_audit.md` (119 KB)
- `docs/research/domains/event_integration_architecture/2004_event_integration_architecture_cat_f_adjacent_separation_boundaries_child_audit.md` (189 KB)
- Jaccard 0.101 · containment_max 0.227

Same audit taxonomy (Cat-F adjacent-separation-boundaries) applied to
two different research domains. Overlap = shared method / boundary
concept text; delta = domain-specific findings.

**Classification:** `partial-overlap-load-bearing-both`.

**Recommended action:** `keep_as_is` — each is domain-canonical.

Same pattern for `docs/research/domains/content/1606_content_cross_domain_integration_lens_audit.md`
+ `docs/research/domains/content/1699_content_canonical_summary.md`
(rank 15, containment_max 0.209) — child audit vs its own arc's canonical
summary; both canonical for their respective slots.

**Migration queue batch hint:** none.

### 2.10 YAML samples (§10.1 v1.1 schema)

Sample rows for the top 3 classifications:

```yaml
- file_path: docs/audits/SESSION_819_SYSTEM_AUDIT_20260714_223131.md
  audit_thread: T3a
  severity: P1
  finding_class: duplicate_content
  schema_version: 1.1
  claim_source: manual
  finding_state: active
  coverage: structural_only  # v1.1 semantics — pairwise Jaccard, not per-claim walk
  line_range: [1, 68]  # whole-doc finding
  evidence:
    - claim: "1-of-19 SESSION_819_SYSTEM_AUDIT_* cluster; Jaccard 0.928-0.960 vs 18 sibling snapshots"
      runtime_truth: "Cluster represents redundant audit-runner snapshots; latest is canonical"
      cited_source: "/tmp/t3a_dup_scan_out_full.json ranks 1-171"
  recommended_action: archive
  action_target: docs/archive/2026-07/audits/session_819_snapshots/
  migration_pr_batch_hint: audits_triage
  cross_arc_refs:
    - 2799_3_target_tree_row: null  # audits triage is T5 territory per §3 target tree
  notes: |
    All 19 files collapse to one migration action. Escalate_to_chris
    on whether audit-runner should be fixed to be idempotent going
    forward.
- file_path: docs/audits/PA_TOOLS_GAP_MAP_S2795.md
  audit_thread: T3a
  severity: P1
  finding_class: duplicate_content
  schema_version: 1.1
  claim_source: manual
  finding_state: active
  coverage: structural_only
  line_range: [1, 308]
  evidence:
    - claim: "Near-identical (Jaccard 0.912) to PA_TOOLS_GAP_MAP_S2796.md"
      runtime_truth: "Consecutive-session snapshot supersession pattern"
      cited_source: "/tmp/t3a_dup_scan_substantive.json rank 1"
  recommended_action: consolidate_into
  action_target: docs/audits/PA_TOOLS_GAP_MAP_S2796.md
  migration_pr_batch_hint: audits_triage
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Alternative: retrofit_v2_pointer instead of consolidate. Migration
    arc picks based on whether S2795 has external citations.
- file_path: docs/features/AUDIO_GENERATION.md
  audit_thread: T3a
  severity: P3
  finding_class: duplicate_content
  schema_version: 1.1
  claim_source: manual
  finding_state: active  # active-but-load-bearing per §2.3
  coverage: structural_only
  line_range: [1, 8]  # whole-doc finding
  evidence:
    - claim: "1-of-110 DOC-POINTER-V2 stub cluster; pairs at Jaccard ~0.86 with sibling stubs"
      runtime_truth: "Intentional Session 1143 Phase 2B-1 link-rot prevention stub per DOC_LIFECYCLE §1"
      cited_source: "/tmp/t3a_dup_scan_out_full.json V2-stub cluster"
  recommended_action: keep_as_is
  action_target: null
  migration_pr_batch_hint: null
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Boilerplate is the point; delta line is the payload. Applies to
    all 110 V2-stub files in §2.3 cluster.
- file_path: docs/architecture/SYSTEM_ARCHITECTURE_MAP.md
  audit_thread: T3a
  severity: P2
  finding_class: duplicate_content
  schema_version: 1.1
  claim_source: manual
  finding_state: active
  coverage: structural_only
  line_range: [1, 892]  # whole-doc finding
  evidence:
    - claim: "Partial-overlap with docs/architecture/SYSTEM_MAP.md (containment_max 0.418)"
      runtime_truth: "Both are docs/architecture/ system-map docs; canonical designation unknown"
      cited_source: "/tmp/t3a_dup_scan_substantive.json rank 6"
  recommended_action: escalate_to_chris
  action_target: null
  migration_pr_batch_hint: topic_docs
  cross_arc_refs:
    - 2799_3_target_tree_row: null
  notes: |
    Rigby cycle-1 Q3 STRENGTHEN sub-classification: `needs-judgment`
    per §5.7 v1.2 candidate. Under current v1.1 semantics emits
    recommended_action: escalate_to_chris; v1.2 Option C would add
    judgment_state: ambiguous field.
```

---

## 3. Severity histogram (post-manual-classification)

Counts under §1.6 severity taxonomy AND §1.7 anti-pattern discipline
(raw candidate pairs in parentheses; V2-stub reclassification per §2.3):

| Severity | Post-classification active pairs | Raw candidate pairs (top-2000) | Notes |
|---|---:|---:|---|
| **P0** | **0** | 0 raw | **§10.4(b) root-stability P0 gate does NOT trigger for this arc.** No duplicate-content finding falls on a root-stable/NEVER-MOVE anchor (none of CLAUDE.md, 00-START-NEXT-SESSION.md, PLATFORM_INVENTORY.md, PLATFORM_WHAT_IT_IS.md appear in any pair above Jaccard 0.10). |
| **P1** | **~2 classes / ~172 pair rows** | 171+1 raw | (a) SESSION_819 cluster (19 files, 171 pairs; ARCHIVE one class) + (b) PA_TOOLS_GAP_MAP_S2795/S2796 pair (1 pair; CONSOLIDATE class). Both drive real migration-queue work in `audits_triage` batch. |
| **P2** | **~2 classes / ~2 pairs** | 2 raw | SYSTEM_ARCHITECTURE_MAP vs SYSTEM_MAP + CLAUDE_CONTEXT_SYSTEM_PACK vs SYSTEM_FULL_ACTIVATION_PLAN. Both `escalate_to_chris` for subject-matter judgment. |
| **P3** | **~1,800 pairs (LOAD-BEARING-BOTH)** | 1,828 raw V2-stub-vs-stub + ~10 sibling-doc rows | Includes V2-stub cluster (§2.3), playbook authoring siblings (§2.6), phase acceptance siblings (§2.7), app-brief template family (§2.8), cross-domain audit siblings (§2.9). All `keep_as_is`. |

**Post-fold real migration-queue impact:**

- **1 audits_triage batch PR** (SESSION_819 archive; PA_TOOLS_GAP_MAP consolidation)
- **2 escalate_to_chris rows** (SYSTEM_ARCHITECTURE_MAP; CLAUDE_CONTEXT_SYSTEM_PACK)
- **0 P0 in-place remediations**
- **~1,800 pairs classified as load-bearing-both** — no migration action

**Coverage distribution (v1.1 semantics per §1.4):**

- `structural_only`: **792 files** (all — T3a scans PAIRWISE similarity,
  not per-claim walk; T2 §5.7 note re: v1.2 `coverage_content_dup` split
  applies here identically)
- `full_claim_walk`: 0 (out of scope for pairwise similarity method)
- `deferred`: 0

**`finding_state: resolved` count:** 0 at authoring time. Any pairs
where subsequent T2 §5.1 workspace-canonical ADR context (or similar
future evidence) reveals a false-positive would migrate to `resolved`
in a follow-up pass.

---

## 4. Migration queue (post-arc)

Per parent §10.3 action taxonomy. Real (post-manual-classification)
migration actions:

### 4.1 Batch `audits_triage` — audits/ subdir consolidate + archive (P1)

| # | Files | Action | Target | Confidence | T5 may override? |
|---|---|---|---|---|---|
| 1 | 19 × `docs/audits/SESSION_819_SYSTEM_AUDIT_YYYYMMDD_HHMMSS.md` | `archive` | `docs/archive/2026-07/audits/session_819_snapshots/` | High | **YES** (per §5.6 T3a↔T5 boundary rule; T5 owns final disposition on all `docs/audits/**`) |
| 2 | `docs/audits/PA_TOOLS_GAP_MAP_S2795.md` | `consolidate_into` | `docs/audits/PA_TOOLS_GAP_MAP_S2796.md` | Medium (alternative: retrofit_v2_pointer) | **YES** (per §5.6 T3a↔T5 boundary rule) |

**Migration-arc note:** row 1 also carries an `escalate_to_chris` sub-item
— was the SESSION_819 audit-runner supposed to be idempotent? Fix at
the source, not just at the file-tree level. **Runner-independence
verified** (Rigby cycle-1 Q2 STRENGTHEN): no `SESSION_819` references
in `core/management/commands/` — archive PR can ship in parallel with
runner-fix ticket, not sequentially.

### 4.2 Batch `topic_docs` — architecture / plans consolidate candidates (P2)

| # | Files | Action | Confidence |
|---|---|---|---|
| 3 | `docs/architecture/SYSTEM_ARCHITECTURE_MAP.md` + `docs/architecture/SYSTEM_MAP.md` | `escalate_to_chris` (subject-matter judgment: which is canonical?) | High (real overlap) / Medium (canonical designation) |
| 4 | `docs/plans/CLAUDE_CONTEXT_SYSTEM_PACK.md` + `docs/plans/SYSTEM_FULL_ACTIVATION_PLAN.md` | `escalate_to_chris` (which is source-of-truth?) | High (containment 0.69) / Medium (canonical designation) |

### 4.3 Batch `keep_as_is` — 1,800+ pairs classified `load-bearing-both` (P3)

Not enumerated inline (see §2.3 for V2-stub cluster; §2.6-2.9 for other
classes). Load-bearing-both classification means the migration arc does
NOT consume these findings.

### 4.4 Chris D-verdict deferral policy (S2836 — NEW RULE)

Chris D-verdict at S2836 close introduced a NEW ARC-LEVEL POLICY:

> "Continue on but let's defer the two issue and any others like it
> until we have the /docs/ audit completed in case other issues come up."

**Interpretation applied:**

- All `recommended_action: escalate_to_chris` rows across Group 2800
  child audits (T3a, T3b, T4, T5) **DEFER** to arc close (`2899`
  canonical summary session), NOT resolved child-by-child.
- Rationale: judgment on canonical designation (SYSTEM_ARCH_MAP vs
  SYSTEM_MAP; CLAUDE_CONTEXT_SYSTEM_PACK vs SYSTEM_FULL_ACTIVATION_PLAN;
  future T3b orphan-vs-load-bearing edge cases; T5 audits-triage
  dispositions) benefits from cross-child context that only emerges
  AFTER T3b/T4/T5 complete their scans.
- Batch resolution at `2899` close = single "Chris judgment session
  workshop" ratifying all deferred rows together with full cross-child
  context.

**Consumed by T3a rows §4.2 (this arc's 2 escalate_to_chris rows):**

| # | Files | v1.1 recommended_action | Deferred until |
|---|---|---|---|
| 3 | `docs/architecture/SYSTEM_ARCHITECTURE_MAP.md` + `SYSTEM_MAP.md` | `escalate_to_chris` | `2899` canonical summary session |
| 4 | `docs/plans/CLAUDE_CONTEXT_SYSTEM_PACK.md` + `SYSTEM_FULL_ACTIVATION_PLAN.md` | `escalate_to_chris` | `2899` canonical summary session |

**Consumed by T3b/T4/T5 future authors:** any `escalate_to_chris` rows
your audit produces inherit the deferral. Do NOT loop Chris in mid-arc
on canonical-ambiguous findings; accumulate them for arc close.

**Consumed by 2899 canonical summary:** the summary MUST include a
consolidated "Chris judgment queue" section listing all deferred rows
across all T-threads with their cross-child context, ready for a
single-session workshop.

### 4.5 Non-actions

Per parent §5: no direct file operations from this arc. All actions
above defer to a follow-on migration arc (post-2899) OR to a Chris-
directed one-off cleanup PR. Per §4.4 S2836 D-verdict policy,
`escalate_to_chris` rows additionally accumulate to arc close (`2899`),
not resolved child-by-child.

---

## 5. Cross-cutting signals for future §3 execution arc AND for T3a/parent methodology refinement

Recorded for post-2899 §3 execution arc consumption AND parent §10
schema post-arc refinement (Rigby cycle-3 `future_trigger` fold at 2899
close).

### 5.1 V2-stub cluster is a corpus-shape signal, not a defect

110+ V2 pointer stubs (14% of the ~792 in-scope corpus) drive ~1,800
raw pair rankings but classify uniformly as `keep_as_is`. The naïve
Jaccard-only ranker is drowned by them. A future T3a-follow-up
scanner MAY:

- Pre-classify files matching `<!-- DOC-POINTER-V\d` on line 1 as
  `v2_stub` and skip them in the pair-generation phase.
- Report `v2_stub_pair_count` separately from `substantive_pair_count`.

**Not applied here** — kept unfiltered in the raw scan so downstream
consumers see the ratio (~90% of raw candidate pairs are V2-stub-vs-V2-
stub noise). Recorded for parent §10 schema v1.2 evaluation at 2899
close.

### 5.2 SESSION_819 audit-runner is likely still active

The 19-file cluster spans 2026-07-14 through 2026-07-16 timestamps —
i.e. active within the last 6 days at authoring time. This is not a
historical cruft cluster; a runner is producing new snapshots. A
Chris-facing followup is warranted BEFORE the archive step (see
§4.1 row 1 sub-note).

**Escalate to Chris:** locate the SESSION_819 audit runner (grep in
`core/management/commands/` and `tools/`), determine whether the
overwrite-vs-append policy is intentional, and either (a) fix runner to
overwrite one file or (b) accept append pattern + rotate old snapshots
to archive on close.

### 5.3 Schema v1.1 fits T3a without amendment (with acceptance criteria for future v1.2 change — Rigby cycle-1 Q4 STRENGTHEN)

Under S2834-locked §10.1 v1.1 semantics, `coverage: structural_only`
is the honest label for T3a (pairwise similarity walk; not per-claim
walk). Same conflation risk with T2's `structural_only` label applies
(T2 §5.7). If v1.2 (2899-eligible refinement) splits `coverage` into
`coverage_refs` / `coverage_claims`, T3a would emit
`coverage_content_dup: full_walk` — proposing extension to a THIRD
axis (per-doc semantic overlap detection).

**Not applied here** per S2834 §10.1 v1.1 lock. Recorded as
`future_trigger` for 2899 close.

**Acceptance criteria for any 2899 v1.2 amendment (Rigby cycle-1 Q4
STRENGTHEN):**
- (i) **Purely additive** — no removal or rename of v1.1 fields
- (ii) **Backward-compatible** — v1.1 consumers reading v1.2 rows
  MUST NOT break (unknown-key tolerance in the YAML parser is the
  practical test)
- (iii) **Parser-compat plan** — any v1.1 consumer script/tool listed in
  the amendment envelope; smoke-test evidence that each consumer still
  parses v1.2 rows correctly BEFORE ratification
- (iv) **Documented deprecation path** — for any field whose semantics
  shift, keep the old field, add the new, mark the old deprecated but
  still populated by emitters until 2999 or later close
- Absent any of (i)-(iv), deferral to a later close is the safer default
  than a mid-arc amendment.

### 5.4 T3b consumes T3a's V2-stub map

T3b (orphan / reachability audit) will need to distinguish "orphan
because ignored" (bad) vs "orphan because SUPERSEDED and only the
V2 stub remains in-tree" (expected). T3a's V2-stub file list
(§2.3) IS that pre-classification signal for T3b:

- Files in §2.3 cluster (110+ V2 stubs) → skip orphan check;
  they're expected to be reachable-only-from-search (the V2 pointer's
  raison d'être).
- Files NOT in §2.3 that surface as unreachable → real orphan candidates.

Recorded for T3b author's consumption. Free pre-clustering signal
identical in shape to T2 §5.6 pattern.

### 5.5 App-brief template family suggests a template-vs-instance schema field

The 5-file app-brief cluster (§2.8) surfaced structural-similarity
without any semantic drift risk — the "template" is the point. Per
parent §10.1 schema this classifies as `finding_class: duplicate_content`
with `recommended_action: keep_as_is`, which loses signal
("template-family, don't merge" ≠ "coincidental overlap, don't merge").

**Future §10.1 refinement candidate:** add `template_family: <slug>`
field for load-bearing-both rows that share a common origin template.
Consumers can then flag "does the template itself need consolidation?"
as a distinct question.

**Not applied here** per S2834 v1.1 lock. Recorded as `future_trigger`
for 2899 close.

### 5.6 T3a↔T5 boundary discipline (Rigby cycle-1 Q5 STRENGTHEN)

Rigby cycle-1 Q5 zoom-out surfaced a real coupling risk: T3a
classifies content-duplication severity but must NOT preempt T5's
disposition authority for `docs/audits/**` + `docs/reports/**` files.

**Boundary rule adopted:**
- **T3a's job:** classify DUPLICATE-level severity (identical / near-
  identical / partial-overlap-*) and RECOMMEND a first-pass action.
- **T5's job:** dispose all `docs/audits/**` + `docs/reports/**` files
  under audits-triage semantics (rotate / retain-latest-N / archive /
  consolidate) using T3a's classification as ONE input among several
  (also citation-graph, retrieval-harm, staleness).
- **T3a MUST NOT** finalize disposition for T5-territory files. T3a
  entries in §2.1 (SESSION_819) + §2.2 (PA_TOOLS_GAP_MAP) carry a
  `t5_may_override` note in their migration-queue rows.
- **T3a MAY finalize disposition** for non-T5 files (§2.3 V2 stubs;
  §2.6 playbook siblings; §2.8 app briefs; §2.9 cross-domain audits)
  where T5 has no claim.

**Scope-creep guard:** T3a MUST NOT extend into "merge planning" or
"which files should exist post-migration." That's execution-arc
territory (post-2899); T3a stops at classification + action-hint.

Recorded as `future_trigger` for parent §7 anti-scope refinement at
2899 close.

### 5.7 `needs_judgment` severity/finding_class — v1.2 candidate (Rigby cycle-1 Q3 STRENGTHEN)

Rigby cycle-1 Q3 STRENGTHEN identified that under current v1.1 semantics
the 2 `escalate_to_chris` rows in §2.4-§2.5 conflate two distinct
signals:

- **(a) Real duplication + known-canonical-target** — direction is
  clear; only Chris ratification is needed to authorize the action.
- **(b) Real duplication + canonical-ambiguous** — direction is NOT
  clear; Chris needs to make a subject-matter judgment BEFORE
  action can be scoped.

Both currently emit `recommended_action: escalate_to_chris`, which
downstream migration-arc tooling can't distinguish. This means:

- Metrics collapse two distinct workflow states into one bucket
- Migration-arc PR planning can't batch (b) rows into a "Chris
  judgment session" workshop separately from (a) rows

**v1.2 candidate refinement:**

Option A — new **severity class** `NEEDS_JUDGMENT` between P1 and P2
(indicates real duplication, direction unclear).

Option B — new **finding_class** value `duplicate_content_needs_judgment`.

Option C — new **field** `judgment_state: known | ambiguous` on
`duplicate_content` rows.

Option C is the most additive (backward-compatible with v1.1 consumers).
Deferred to 2899 close per §5.3 acceptance criteria; not applied here.

**T3a in-arc treatment:** the 2 `needs-judgment` rows (§2.4, §2.5)
carry an inline `notes:` field flagging them as ambiguous-canonical
under v1.1 semantics. T3b MAY inherit this pattern.

### 5.8 Scanner cost is acceptable for future re-runs

Full T3a scanner run on 792 files completes in ~3 seconds (inverted-
index Jaccard). Rerun cost as `/docs/` grows: linear in shingles
(one time-step per file × unique shingles). No optimization needed
at S2836 corpus scale; MinHash-based approximation only warranted
if corpus reaches ~5,000+ files.

---

## 6. Residual risk / limitations

### 6.1 Method limitations (recorded)

1. **Semantic paraphrase misses.** Two docs stating the same fact in
   entirely different vocabulary would score Jaccard ≈ 0 and never
   surface. T3a detects LEXICAL overlap, not SEMANTIC overlap. Embedding-
   based similarity (via existing `search_embeddings` corpus) could catch
   paraphrase but adds a whole different measurement axis; deferred to
   `future_trigger` for 2899.
2. **Code-block strip loses signal in code-heavy docs.** Per §1.2 we
   strip fenced code blocks to reduce false positives from shared
   import statements. But for docs whose PAYLOAD is code (e.g. spider
   templates, Django command examples), this may hide real duplication.
   Sample-verify §6.3 addresses one spot-check.
3. **Frontmatter strip removes YAML-schema-similarity signal.** Two docs
   with different frontmatter but identical bodies would still match on
   body content; two docs with identical frontmatter but different
   bodies would NOT match. This is intentional (frontmatter is
   metadata, not content) but recorded for surprise avoidance.
4. **Manual severity review sampled top ~40 non-cluster pairs.** The
   full result set is 7,246 pairs above Jaccard 0.10; we manually
   reviewed only ~40 highest-ranked substantive pairs. Long-tail
   pairs (Jaccard 0.10-0.25) are NOT hand-classified. Expected FP
   rate is high in this band.

### 6.2 Spot-verify sample (top-40 non-SESSION_819 non-V2-stub pairs)

Reviewed pairs 1-15 (all non-cluster substantive pairs above Jaccard
0.10):

| Rank | Pair | Manual verdict | Classification |
|---|---|---|---|
| 1 | PA_TOOLS_GAP_MAP_S2795/S2796 | Consecutive session snapshots (real dup) | `near-identical` / consolidate |
| 2 | CLAUDE_CONTEXT_SYSTEM_PACK / SYSTEM_FULL_ACTIVATION_PLAN | Subject-matter subset (real dup, needs judgment) | `partial-overlap-consolidate-candidate` / escalate |
| 3-5 | ENGINEERING_PLAYBOOK / playbook_authoring_sessions | Authoring vs canonical (load-bearing) | `partial-overlap-load-bearing-both` / keep |
| 6 | SYSTEM_ARCHITECTURE_MAP / SYSTEM_MAP | Same-subdir arch docs (real dup, needs judgment) | `partial-overlap-consolidate-candidate` / escalate |
| 7 | I-0100_p3 / I-0100_p4 acceptance | Sibling phase docs (load-bearing) | `partial-overlap-load-bearing-both` / keep |
| 8-9 | apps/*_BRIEF pairs | Template family (load-bearing) | `partial-overlap-load-bearing-both` / keep |
| 10 | i0302_arc_close / i0302_phase4_close ratification | Sibling ratification envelopes (load-bearing) | `partial-overlap-load-bearing-both` / keep |
| 11-12 | More apps/*_BRIEF pairs | Same as 8-9 | `partial-overlap-load-bearing-both` / keep |
| 13 | playbook_authoring_2716 / playbook_v0_1_body_corrected | Authoring vs body (load-bearing) | `partial-overlap-load-bearing-both` / keep |
| 14-15 | Cross-domain audit siblings | Same taxonomy, different domain (load-bearing) | `partial-overlap-load-bearing-both` / keep |

**Post-verify hit rate:**
- 2 of 15 pairs are actionable duplicates (13%)
- 4 of 15 are `escalate_to_chris` for subject-matter judgment (27%)
- 9 of 15 are `load-bearing-both` (60%)

### 6.3 Code-block-strip false negative spot check (one sample)

Manually inspected `docs/features/AUDIO_GENERATION.md` (V2 stub) vs
`docs/features/IMAGE_GENERATION.md` (V2 stub) — code-block strip does
not apply (both are prose-only). No FN observed for this pair. Broader
FN sampling deferred to `future_trigger`.

---

## 7. Rigby joint SIGN cycle 1 — actual verdicts

Per `feedback_verify_rigby_tool_runs_before_trusting_sign` — Rigby SIGN
tool_runs verified non-empty across all 5 verdicts (substantive
`repo_tool.read` + `repo_tool.search` + `search_docs` grounding).
Anti-rubber-stamp check passed.

**Verdict table:**

| Q# | Dimension | Verdict | Fold |
|---|---|---|---|
| Q1 | V2-stub classification | **AGREE** — DOC-POINTER-V2 stubs are load-bearing per DOC_LIFECYCLE §1; scale is not a consolidate signal | No change |
| Q2 | SESSION_819 archive-vs-runner-fix ordering | **STRENGTHEN** — archive-first is fine BUT needs runner-independence proof + explicit follow-up | §2.1 runner-independence proof added; §4.1 archive/runner-fix parallel-track note added |
| Q3 | escalate_to_chris as its own severity class | **STRENGTHEN** — v1.1 conflates known-target vs canonical-ambiguous | §2.4-§2.5 flagged with `needs-judgment` sub-classification; §5.7 records v1.2 candidate (Option C most additive) |
| Q4 | v1.2 schema mid-arc amendment | **STRENGTHEN** — three-witness signal is real BUT amendment must satisfy additive/backward-compat/parser-compat/deprecation-path criteria | §5.3 acceptance criteria (i)-(iv) codified; deferral to 2899 remains default |
| Q5 | Zoom-out: scope creep + T3a↔T5 coupling | **STRENGTHEN** — T3a must not preempt T5 disposition on audits/reports | §5.6 T3a↔T5 boundary rule added; §4.1 rows carry `t5_may_override: YES` |

**Cycle 1 evidence base (Rigby tool_runs — anti-rubber-stamp verified):**
- `repo_tool.read` — DOC_LIFECYCLE.md §1 + 3 sample V2 stubs
  (docs/features/AUDIO_GENERATION.md, docs/guides/DAVINCI_PHASE_3_PLAN.md,
  docs/agents/INDEX.md, all lines 1-8)
- `repo_tool.search "SESSION_819"` in `core/management/commands/` →
  **zero matches** (runner-independence confirmed)
- `repo_tool.read` — 2800 parent §4 T3a rubric text
- `search_docs "schema v1.1 locked"` → 5 chunks
- `repo_tool.read` — 2801 §10.1 language + 2800 §4 T5 spec

**Overall Rigby recommendation:** "Proceed, but tighten the rubric
around (a) 'needs judgment' as its own severity/finding class, (b)
archive-vs-runner proof requirements, (c) explicit T3a↔T5 coupling
rules to prevent consolidation-scope creep."

All three items folded in the sections cited above.

Cycle 2 verification will re-read YAML sample rows (§2.10) against
severity histogram (§3) after this fold — per S2835 Q7 lesson.

---

## 8. What this T3a deliberately leaves open

- **Long-tail Jaccard 0.10-0.25 pairs (~5,000 raw)** — sample coverage
  ≤1%. FP rate expected to be high in this band; manual review beyond
  40 pairs is out-of-scope. If Chris ratifies with intent to
  strengthen coverage, spawn a T3a-follow-up sub-arc after 2899.
- **Semantic paraphrase detection** — deferred to `future_trigger`.
- **SESSION_819 runner fix** — separate PR / ticket, distinct from
  the archive migration.
- **`template_family` schema extension (§5.5)** — future_trigger for
  §10.1 v1.2 candidate.
- **V2-stub pre-filter in scanner (§5.1)** — future_trigger.
- **Cross-arc T3b consumption of §2.3 V2-stub map (§5.4)** — recorded
  for T3b author; no T3a author-side action.

---

## 9. Cross-links

- Parent scoping: `docs/research/domains/docs_content_audit/2800_docs_content_audit_domain_scoping.md`
- Predecessor T1: `docs/research/domains/docs_content_audit/2801_docs_content_anchors_audit.md` (§4.1a T3a pre-scan hint honored via §1 method + §2.3 V2-stub cluster classification)
- Predecessor T2: `docs/research/domains/docs_content_audit/2802_docs_content_reference_audit.md` (§5.6 basename map consumed as §1.5 pre-clustering signal; §5.7 future_trigger reinforced in §5.3)
- Sibling target-tree arc: `docs/research/domains/docs_restructuring/2799_docs_restructuring_canonical_summary.md`
- Ratification envelope (this arc — pending Chris D-verdict): `docs/research/implementation/RATIFICATION_2026-07-19_2803a_docs_content_duplicate_audit.md`
- Scanner tool: `tools/audit_2803a_duplicate_content.py`
- Scanner output (raw): `/tmp/t3a_dup_scan_out_full.json` (top-2000)
- Scanner output (V2-stub-filtered): `/tmp/t3a_dup_scan_substantive.json` (top-300)
- T2 pre-clustering seed: `/tmp/t2_scan_out.json`
- Governance canonical: `docs/00-START-HERE/DOC_LIFECYCLE.md` (§1 V2 pointer pattern; §2c inventory authority; §3 root-stability)
- Playbook (v0.8.0): `docs/ENGINEERING_PLAYBOOK.md` (PLAYBOOK-6.10.7/8/9 zoom-out ask / fold-before-D-verdict / evidence admission apply here)
- Live manifest: `docs/research/OPEN_ARCS.md` (Group 2800 In-progress, 3/6 shipped pre-T3a; 4/6 post-ratification)
