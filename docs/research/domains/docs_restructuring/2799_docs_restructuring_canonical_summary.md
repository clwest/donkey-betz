---
title: "S2817 /docs/ Restructuring — Canonical Summary (Group 2700 arc close)"
status: active (canonical summary — arc close; proposed restructuring plan + twin-pointer workspace deliverable pending Chris ratification)
authority: canonical summary for Group 2700 arc (closes 6-thread child-audit set T1-T6)
session: 2817
date: 2026-07-18
domain_slug: docs_restructuring
research_group: 2700
child_slot: canonical-summary
authors: Claude Code (Chris directed at S2817 open); Rigby (SIGN cycles + workspace_id resolution + coherence-check meta-review)
supersedes: none
related:
  - docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md   # parent (Chris-locked 2026-07-16)
  - docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md       # T1 (S2811)
  - docs/research/domains/docs_restructuring/2702_docs_research_pattern_extraction_audit.md # T2 (S2812)
  - docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md   # T3 (S2813)
  - docs/research/domains/docs_restructuring/2704_docs_audience_segmentation_audit.md   # T4 (S2814)
  - docs/research/domains/docs_restructuring/2705_docs_handoffs_audits_proliferation_audit.md # T5 (S2815)
  - docs/research/domains/docs_restructuring/2706_docs_anchor_drift_audit.md              # T6 (S2816)
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                              # §11.3 canonical summary template
  - docs/00-START-HERE/DOC_LIFECYCLE.md                                                    # §2b/§2c/§3 constraints canonical summary respects
  - docs/PLATFORM_INVENTORY.md                                                             # runtime counts anchor (referenced, not restated)
  - docs/PLATFORM_WHAT_IT_IS.md                                                            # narrative anchor
  - docs/ENGINEERING_PLAYBOOK.md                                                          # v0.8.0 (v0.9 amendment ready per §10.2)
  - CLAUDE.md                                                                              # repo bootstrap
twin_pointer:
  workspace_deliverable_id: TBD (created post-authoring in workspace b4503364-2573-4401-9e28-61a739e0ce50 Donkey Betz per parent §5 D7 + memory feedback_twin_deliverable_at_every_ratification)
  workspace_id: b4503364-2573-4401-9e28-61a739e0ce50
scope: canonical summary for Group 2700 arc — synthesizes T1-T6 findings into ratified /docs/ restructuring proposal; migration executes post-close in follow-up sessions per parent §5
non_goals:
  - re-authoring T1-T6 findings (canonical summary synthesizes; does not re-audit — per Playbook §10 "What does NOT belong in canonical summary")
  - implementation plan / owner assignments / timelines (Playbook §10; keep §8 follow-on queue as "questions + smallest next evidence to collect")
  - new taxonomies beyond what T1-T6 established
  - file moves / deletions / renames / code changes during arc-close session (per parent §5 arc non-goals)
  - editing anchors in this doc (§7 lists proposed edits; ARCHITECTURE_INDEX v-bump commit applies)
  - Playbook v0.9 amendment authoring (separate arc; §10.2 flags readiness)
delegates_to: post-arc migration sessions (per §7 anchor-update recommendations + §8 follow-on queue)
owner: claude+rigby (closed as arc-close per parent §5 D6)
---

# Group 2700 /docs/ Restructuring — Canonical Summary

> **What this doc is.** Arc-close canonical summary for Group 2700 /docs/ restructuring. Synthesizes T1-T6 findings into ratified restructuring proposal + anchor-update recommendations + follow-on research queue. **Twin-pointer:** this repo doc + workspace deliverable in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`) per parent §5 D7.
>
> **What this doc is not.** Another audit. New evidence sweep. Implementation plan. Design decisions. Migration execution.

---

## 1. Executive Summary

The Group 2700 /docs/ restructuring arc opened at Chris's directive S2800 close (2026-07-16) and closed 17 sessions later at S2817 (2026-07-18). Parent scoping doc (`2700_docs_restructuring_domain_scoping.md`) locked at S2801 with a 6-thread child-audit package (T1-T6). All 6 child audits + this canonical summary shipped on 2026-07-18, closing the arc in 8 same-day sessions (S2809-S2817 including two Colorado warm-up ships that preceded arc reopen).

**What the arc answered.** The `/docs/` corpus (3210 files at arc close, up from 3197 at arc open) exhibits three substrate concerns: (1) **sprawl** (99 loose files at root, 48 top-level subdirs, 3 parallel audit dirs + 20 loose `*AUDIT.md`, 6 parallel forward-planning subdirs); (2) **discoverability failure** (8 of 13 realistic user-query scenarios failed success@3 — 62% failure rate; canonical convention "PLATFORM_INVENTORY.md is sole authoritative counts source" holds in-doc but is FALSIFIED at the discovery layer where archived Oct 2025 morning report outranks canonical for "how many spiders" queries); (3) **rule drift** across 6 primary surfaces with 3 SEVERE drifted-and-inconsistent rules (SIGN pin discipline, pin rotation, twin-pin discipline).

**What changed about domain understanding.** The `/docs/research/` substrate that Chris identified as "the good pattern" was reverse-engineered to 31 transferable primitives (T2) — of which ~5 are WHOLE-transferable (title/status/authority/related core frontmatter, numbered sections), ~15 are CORE-ONLY (extendable with adaptations), and ~11 are RESEARCH-ONLY BY DESIGN (extending would break research-arc semantics). Highest-leverage transferable primitive is **FP-META** (frontmatter as extensible control-plane header) with HARD guardrail against autogen/runtime-coupled paths. Audience segmentation (T4) showed ~5 Rigby-structural + ~5 Rigby-high-priority + ~35 Claude-primary + ~5 Multi + ≤1730 Human-primary (upper bound) — the corpus is overwhelmingly human-audience by default. Handoff citation-graph (T5) is bimodal: foundational-era + recent handoffs are heavily-cited-forever; middle-range handoffs are lightly-cited-forever; **no range is completely zero-cited** (post-authoring correction from original grep bug).

**What remains open.** (a) migration execution (file moves per §3 target tree — multi-session follow-up); (b) Playbook v0.9 amendment for OP3 two-SIGN-per-audit (6/6 triggers across arc; separate arc); (c) parent §4 T5 substrate-integrity clause update per T5 MQ-T5-8 (requires Chris re-ratification per parent §5 Chris-lock); (d) discovery-layer enforcement of DOC_LIFECYCLE §2c (retrieval-weight boost + `verify_doc_claims` in start-here checklist); (e) per-handoff citation_health verification for the ~98 uncited S2500-2600 range.

**Core principle for migration:** **Canonical structure is the target; migration is staged; generator/runtime paths get compatibility-first treatment.** Per Rigby SIGN coherence-check: aggressive consolidation is bounded by DOC_LIFECYCLE §2b (runtime-coupled never-move) + T2 FP-META HARD guardrail (excludes autogen/runtime-coupled from frontmatter mandate). Every migration PR must verify these invariants BEFORE landing.

---

## 2. What This Arc Answered

Per-child rollup:

| Child | Session | Substance |
|---|---|---|
| **T1** (2701 inventory & topology) | S2811 | 3201 total files (1813 non-archive + 1388 archive); 99 loose root files; 48 top-level subdirs; ~4% autogen; bimodal size (33% <50 LOC / 5% 1000-5000 LOC); bimodal freshness (60% touched 30-90 days); 3 audit dirs + 20 loose AUDIT files + 6 forward-planning subdirs identified as arc-restart candidates |
| **T2** (2702 pattern extraction) | S2812 | 31 transferable primitives across 6 categories; per-primitive load-bearing + challenge + verdict (WHOLE/CORE-ONLY/REJECT/RESEARCH-ONLY BY DESIGN); FP-META highest-leverage with HARD autogen guardrail; ~10 primitives OFF-LIMITS for verbatim extension |
| **T3** (2703 human pain) | S2813 | 13 concrete user-query scenarios across Chris/Claude/Rigby audiences; 62% success@3 failure rate; 5-type pain taxonomy (Invisibility / Ambiguity / Drift / Rot / Misleading-meta-dominance); 3 catastrophic Rigby search_docs findings (C3 self-name query FAILS; C4 literal filename FAILS; C5 archived Oct 2025 morning report outranks canonical PLATFORM_INVENTORY for count queries) |
| **T4** (2704 audience segmentation) | S2814 | 5 discovery surfaces enumerated (RAG corpus 3217 docs / CRITICAL_DOCS 5 / PRIORITY_DOCS 10 / CLAUDE.md pointer graph 45 refs / PLATFORM_WHAT_IT_IS narrative 7 refs / runtime prompt-pack); Primary+Secondary audience framing; ~5+5+35+5+≤1730 by primary; discovery-vs-injection asymmetry (3 CRITICAL_DOCS + 2 PRIORITY_DOCS not in CLAUDE.md); Rot signal: docs/current/ referenced but doesn't exist |
| **T5** (2705 handoffs+audits proliferation) | S2815 | 1037 handoffs; 1306 corpus docs cite SESSION_NNNN; bimodal decay curve (post-corrected — no range zero-cited; S2500-2600 lowest at 2 sessions / 3 refs); 3 severity tags + 2 boolean attributes proposal; **SUBSTRATE FINDING**: parent §4 T5 chunk-anchor citation-integrity concern was based on false premise (pattern never adopted in corpus) — MQ-T5-8 explicit parent-clause update action item |
| **T6** (2706 anchor drift) | S2816 | 14-rule inventory (Rigby SIGN Q1 expanded 10→14) across 6 primary surfaces; 4 identical/low-drift + 5 drifted-but-compatible + 3 SEVERE drifted-and-inconsistent (#4 SIGN pin, #5 pin rotation, #14 twin-pin) + 2 uncodified (#6b build_docs_provenance, #10 OP3 two-SIGN); MQ-T6-8 actionable standard for replicated-rule anchoring |

**Cross-child arc-close observation:** T1 → T2 → T3 → T4 → T5 → T6 sequence deliberately built substrate incrementally. T1's inventory feeds T2's primitive extraction; T2's pattern extraction feeds T3's pain measurement + T4's audience classification; T3+T4's substrate feeds T5's citation-graph work; T5's substrate-integrity finding + T6's rule drift together set the migration-priority for this summary.

---

## 3. Consolidated Domain Shape — PROPOSED /docs/ TREE (pending Chris ratification)

**Core principle** (per Rigby SIGN coherence-check + post-authoring Q4 disclaimer): **Canonical structure is the target; migration is STAGED with compatibility-first treatment for generator/runtime paths; no move ships without per-PR verification of DOC_LIFECYCLE §2b + T2 FP-META guardrails.** This section describes the destination, not a mass-move script. Future readers: do NOT interpret §3 as instruction to move files immediately.

**Runtime-coupling scoping (Rigby SIGN post-authoring Q2 clarification):** DOC_LIFECYCLE §2b runtime-coupled constraint applies to the SPECIFIC PATH CONTRACT (e.g., `docs/decisions/ADR-*.md`), not the entire subdir. Merging `docs/adr/` into `docs/decisions/` is safe IF the ADR-* filename contract stays intact at `docs/decisions/ADR-*.md`. The invariant to preserve: **decisions/ is the canonical ADR home; do NOT relocate ADR-* once there.**

### 3.1 Target subdir layout

```
docs/
├── PLATFORM_WHAT_IT_IS.md     # narrative anchor (Multi-primary; SIGN-audit-cleared)
├── PLATFORM_INVENTORY.md      # runtime-counts anchor (Multi-primary; SIGN-audit-cleared)
├── CLAUDE.md                  # (currently at repo root; NOT moved)
├── INDEX.md                   # sole canonical docs-corpus index (auto-generated; Multi-primary)
├── 00-START-HERE/             # onboarding entry point (KEEP)
│   ├── DOC_LIFECYCLE.md       # governance canonical (§2b + §2c + §3 rule anchors)
│   └── README.md              # (new — routing README for onboarding intent)
├── canon/                     # runtime-coupled — NEVER MOVE (DOC_LIFECYCLE §2b)
├── governance/                # runtime-coupled — NEVER MOVE
├── missions/                  # runtime-coupled — NEVER MOVE
├── decisions/                 # runtime-coupled ADR-* — NEVER MOVE (KEEP; MERGE with adr/ per §3.3)
├── ops/                       # runtime-coupled — NEVER MOVE
├── research/                  # WORKING PATTERN — KEEP; T2 substrate
│   ├── ARCHITECTURE_INDEX.md
│   ├── DOMAIN_RESEARCH_PLAYBOOK.md
│   ├── OPEN_ARCS.md
│   ├── domains/               # per-domain slugs (14 currently)
│   ├── implementation/
│   ├── platform/
│   ├── process/
│   └── tools/
├── topics/                    # per-subsystem narrative (KEEP; 11 files; Claude-primary)
├── handoffs/                  # 1037 files; per-handoff citation_health + is_superseded tagging (post-arc; no bulk moves)
├── audits/                    # CONSOLIDATED — absorbs audit/ + audit-2026/ per §3.2
│   ├── legacy/                # (new) — 25 files from audit/ + audit-2026/
│   └── (94 current active audits + 20 root *AUDIT.md — see §3.4 below)
├── plans/                     # CONSOLIDATED — absorbs specs/ + designs/ + roadmap/ + roadmaps/ + pre-launch/ per §3.3
│   ├── specs/
│   ├── designs/
│   ├── roadmaps/
│   └── pre-launch/
├── narratives/                # KEEP (19 files; Human/Multi-primary)
├── guides/                    # KEEP (18 files)
├── features/                  # KEEP (18 files)
├── architecture/              # KEEP (24 files; overlaps with ARCHITECTURE.md at root — see §3.4)
├── code-review/               # KEEP (24 files; likely Human-primary)
├── reports/                   # KEEP (33 files; Human-primary)
├── patents/                   # KEEP (17 files; Human-primary)
├── docs-pattern/              # context-kit framework — EXCLUDED per DOC_LIFECYCLE §0 (KEEP; DO NOT TOUCH)
├── archive/                   # 1388 files — already-partitioned; LEAVE ALONE per parent §7 anti-scope
│   └── (20+ dated subdirs — see T1 §3.1)
└── (~10 loose files max at root — see §3.4)
```

**Root file reduction target:** 99 loose `.md` files → ~10 (anchors + INDEX + generated manifests only). Non-anchor loose files migrate to appropriate subdirs per §3.4.

### 3.2 Audits consolidation (§3.1 detail)

**Current:** `docs/audit/` (10) + `docs/audit-2026/` (15) + `docs/audits/` (93) = 118 files across 3 parallel dirs, plus 20 loose `*AUDIT.md` at root = 138 files across 4 surfaces.

**Target:**
- `docs/audits/` — single canonical subdir
- `docs/audits/legacy/` — 25 files from `audit/` + `audit-2026/` (preserve for historical reference; add README noting these are legacy per Chris arc-restart pattern)
- **20 loose root `*AUDIT.md`** — MOST are DOC-AUTOGEN outputs per T1 §4. Move requires generator updates. **Staged migration:** phase 1 update generators to write into `docs/audits/`; phase 2 remove root files. Do NOT bulk-move without generator coordination.
- **File duplication resolution:** `SESSION_1143_DOCS_AUDIT.md` in both `audit/` + `audit-2026/` (T5 §6). Consolidate: keep one canonical; mark other with V2 stub pointing to canonical.

### 3.3 Forward-planning consolidation (§3.1 detail)

**Current:** `docs/plans/` (13) + `docs/specs/` (10) + `docs/designs/` (5) + `docs/roadmap/` (10) + `docs/roadmaps/` (2) + `docs/pre-launch/` (8) + `docs/ROADMAP_IDEAS.md` (1 root file) = 6 subdirs + 1 loose file = 49 files across 7 surfaces.

**Target:**
- `docs/plans/` — single canonical parent
- `docs/plans/specs/`, `docs/plans/designs/`, `docs/plans/roadmaps/`, `docs/plans/pre-launch/` — subdirs (Rigby SIGN Q1 suggestion)
- **Merge `docs/roadmap/` + `docs/roadmaps/` + `ROADMAP_IDEAS.md`** into `docs/plans/roadmaps/`

### 3.4 Miscellaneous file resolution (§3.1 detail)

| Case | Current | Target |
|---|---|---|
| `docs/adr/` (4) vs `docs/decisions/` (2) — real convention collision per T3 B3 | 2 parallel dirs | **Merge to `docs/decisions/`** (runtime-coupled per DOC_LIFECYCLE §2b); `docs/adr/` files migrate with V2-stub redirects |
| `docs/operations/` (1) vs `docs/ops/` (2) | 2 singleton dirs | **Merge to `docs/ops/`** (runtime-coupled); `docs/operations/` file moves with V2 stub |
| Root anchors (~5) | `ARCHITECTURE.md`, `AGENTS.md`, `SPIDERS.md`, `SERVICES.md`, `MODELS.md` at root vs subdirs | **Root anchors keep pointer role; substance lives in subdir** (`agents/`, `architecture/`, etc.). Root files become brief pointer stubs. |
| Doubled root files | `AGENTS.md` + `AGENTS_REFERENCE.md`; `MODELS.md` + `DATABASE_MODEL_REFERENCE.md`; `SPIDERS.md` + `SPIDER_AUDIT.md`; 3 MERGE_PROPOSAL_*.md | Per-file review; likely merge OR keep one + supersede other with V2 stub |
| Session-loose at root | `SESSION_780_PLATFORM_STATUS.md`, `SESSION_1251_CLAUDE_STARTUP_CONTEXT_PROPOSAL.md` | **Move to `docs/handoffs/`** (their intended home) |

### 3.5 Cross-audience navigation

Per T4 findings: audiences do NOT get separate subdirs (avoid duplicating what CLAUDE.md graph does). Instead:
- **`docs/INDEX.md`** — sole canonical docs-corpus index (per T3 A6 finding: 4 candidate index locations → collapse to 1)
- **Per-subdir `README.md`** — routing README explaining subdir purpose + audience (proposed as `<subdir>/README.md` pattern per Rigby SIGN Q1)
- **CLAUDE.md** — Claude bootstrap graph (unchanged; but ADD the 5 missing CRITICAL_DOCS + PRIORITY_DOCS per T4 §6.3 asymmetry)

---

## 4. Cross-Cutting Patterns

Patterns visible only across multiple children:

### 4.1 Discovery-vs-source-of-truth asymmetry (T3 + T4)

The `/docs/` corpus has conventions (DOC_LIFECYCLE §2c sole-counts-source, T4 CRITICAL_DOCS injection) that hold IN-DOC but fail at the RETRIEVAL/DISCOVERY layer. T3 C5 evidence: `search_docs("How many spiders")` returns archived Oct 2025 morning report as top-1, not PLATFORM_INVENTORY. T4 §6.3 evidence: 3 CRITICAL_DOCS + 2 PRIORITY_DOCS get unconditionally injected into every agent's prompt but are absent from CLAUDE.md's bootstrap graph. **Pattern:** conventions require BOTH in-doc discipline AND surface-layer enforcement.

### 4.2 Autogen-vs-handwritten treatment differential (T2 + T4 + T5)

Autogen outputs (~4% of non-archive corpus per T1 §4; 20 loose `*AUDIT.md` at root; `docs/INDEX.md`; `docs/canon/INDEX.md`) obey different constraints than human-authored docs: they cannot receive frontmatter mandates (T2 FP-META HARD guardrail), their moves require generator updates (T4 MQ-T4-2), their citation-integrity risk differs (T5 §5 top-cited handoffs are handwritten). **Pattern:** every restructuring rule needs "human-authored" vs "autogen" scoping.

### 4.3 Bimodal distribution (T3 + T5)

Both handoff citations (T5 §5) AND user-query success (T3 §7) show bimodal patterns: heavily-used-or-not, with no meaningful middle. Handoffs: foundational-era + recent-era heavily-cited; middle sparse. Queries: some queries succeed easily (habit-Chris opens PLATFORM_INVENTORY.md directly); others catastrophically fail (Rigby returns archived stale answers). **Pattern:** substrate treatment should optimize for the bimodal shape — don't chase middle-ground defaults.

### 4.4 Rule replication drift (T6 + T5)

Rules replicate across surfaces (T6 14 rules × 6 primary surfaces + N secondary replication points). Replication without canonical anchoring produces drift (T6 §5 3 SEVERE cases). T5 substrate-integrity finding is a special case: parent §4 T5 clause replicated a rule (chunk-anchor citation check) that was itself template-only, never adopted in the corpus. **Pattern:** replicated-rule anchoring requires (a) canonical-anchor pointer + (b) drift-check hook OR non-authority banner — per MQ-T6-8 actionable standard.

### 4.5 Post-authoring SIGN as first-class discipline (OP3 6/6 across T1-T6)

Every child audit's post-authoring SIGN caught substantive errors that open-SIGN missed: T1 ghost reference (factual), T2 missing primitives + guardrail gap (coverage), T3 6 substantive edits (mixed), T4 same-file conflation (factual), T5 systematic grep bug (methodology), T6 classification nuance (surface-scope). **Pattern:** for arc-audit shape, post-authoring SIGN is empirically load-bearing across all failure-mode classes. **Playbook v0.9 amendment ready.**

---

## 5. Resolved Contradictions

Where children disagreed on maturity, ownership, or classification, canonical picks + rationale:

### 5.1 Handoff lifecycle framing

- **Parent §4 T5 hypothesis:** "write-once-read-rarely triage" (implies most handoffs archive-after-N).
- **T5 §5 evidence (corrected):** bimodal — foundational-era + recent heavily-cited-forever; middle less; no range zero-cited.
- **Canonical verdict:** Reject "write-once-read-rarely" as blanket default. Handoffs are bimodal-cited; severity-tag per T5 §8 (3 tags + 2 boolean attributes) with **per-doc citation_health verification** before archive-after-N or eligible-for-deletion applies.

### 5.2 Parent §4 T5 chunk-anchor substrate concern

- **Parent §4 T5 clause:** "handoffs previously mass-moved and chunk IDs reset per SESSION_1143_...#8. T5 MUST include 10-doc citation-integrity spot-check on `[docs/handoffs/SESSION_NNN.md#K]` citations."
- **T5 §7 evidence:** chunk-anchor pattern was TEMPLATE-ONLY, never adopted in corpus. Rigby ran 10 targeted searches; 0 matches.
- **Canonical verdict:** Parent §4 T5 clause is based on false premise for chunk anchors. Real citation risk shifted to plain-path filename drift. **Explicit action item MQ-T5-8:** update parent §4 T5 substrate-integrity mandate to target actual citation patterns (requires Chris re-ratification per parent §5 Chris-lock).

### 5.3 Audience segmentation vs discoverability

- **T4 §6.1 finding:** ~5 Rigby-structural + ~5 Rigby-high-priority + ~35 Claude-primary + ≤1730 Human upper-bound.
- **T3 §7 C5 finding:** discovery layer FAILS for high-priority docs (PLATFORM_INVENTORY not retrieved for count queries).
- **T4 §6.3 finding:** discovery-vs-injection asymmetry (5 CRITICAL/PRIORITY docs not in CLAUDE.md graph).
- **Canonical verdict:** Audience-segmentation classification is one lens; discoverability enforcement is a separate concern that must be addressed EARLIER in migration ordering (per Rigby SIGN Q2 Migration Order tweak: move discovery-layer fix to position #2, before file-moves).

### 5.4 SEVERE ≠ INCONSISTENT (Rigby SIGN post-authoring Q1 clarification)

T6 §5 flags Rule #1 (sole counts source) as **SEVERE cross-surface density + DRIFTED-BUT-COMPATIBLE** — the severity comes from discovery-layer failure (T3 §7 C5), not from in-doc drift. The 3 SEVERE-classified rules in T6 have TWO different underlying causes: Rule #1 = discovery-layer failure; Rules #4/#5/#14 = actual DRIFTED-AND-INCONSISTENT wording across surfaces. Canonical summary treats them differently in §7 anchor updates (Rule #1 needs discovery-layer enforcement per T3 MQ-T3-4; Rules #4/#5/#14 need in-doc canonical-anchor pointers per T6 MQ-T6-8).

### 5.5 Rule #5 `tools/pa_local.sh` — STALE vs REPLICATED

- **T6 §5.2 open-SIGN classification:** DRIFTED-AND-INCONSISTENT with STALE claims in `tools/pa_local.sh` comments + S1300 §3F.
- **Rigby post-authoring Q2 correction:** `tools/pa_local.sh` correctly references `session_tool.retire force=true` at multiple lines. Reclassified as REPLICATED SURFACE (under-anchored), NOT stale. S1300 §3F remains genuinely STALE-CONTRADICTORY.
- **Canonical verdict:** Two-treatment-path — `tools/pa_local.sh` needs canonical-anchor pointer (per MQ-T6-8 standard); S1300 §3F needs in-place amendment or V1 banner.

---

## 6. Unresolved Unknowns

Explicit list (promoted to §8 follow-on queue):

1. **Per-handoff citation_health verification** for the ~98 uncited S2500-2600 range — T5 §8.3 recommends per-doc review before any bulk-deletion action; T5 MQ-T5-1 severity moderated post-authoring after decay-curve correction.
2. **`docs/current/` reference** — T4 §5.3 found PLATFORM_WHAT_IT_IS.md references `docs/current/` which is NOT in T1 §3.1 subdir inventory. Rot signal — T6 didn't verify; flagged for post-arc.
3. **Retrieval-frequency telemetry** — T4 §7 Q6 established this doesn't exist; retrieval-proven classification cannot happen until telemetry added.
4. **Full enumeration of surface (5) runtime-injection** beyond CRITICAL_DOCS — T4 §3.5 bounded to CRITICAL_DOCS for T4 scope; latent unenumerated paths (agent-specific injections in `base_agent.py`, PA-specific injections in `unified_pa_entrypoint.py`) remain uncounted.
5. **Non-`docs/` citations of handoffs** — T5 §5 grep methodology only measured `docs/`-scoped citations; handoffs may be cited in code comments, PR bodies, external references. Total citation surface may be larger than measured.

---

## 7. Anchor-Update Recommendations

Per Playbook §10: canonical summary lists proposed anchor edits; the summary itself does NOT edit anchors. ARCHITECTURE_INDEX v-bump commit applies.

### 7.1 `docs/PLATFORM_INVENTORY.md` (runtime counts anchor)

**Additions proposed:**
- Add section noting Group 2700 arc completion date (2026-07-18) as a governance-timeline entry
- No count-specific changes (T1-T6 didn't produce runtime-count updates; T1 measured docs corpus not platform inventory)

### 7.2 `docs/PLATFORM_WHAT_IT_IS.md` (narrative anchor)

**Additions proposed:**
- Add reference to Group 2700 arc canonical summary (this doc) in narrative anchor's Companion Docs section
- **Verify + correct** `docs/current/` reference per §6.4 Rot signal (Unresolved Unknown #2)

### 7.3 `docs/research/ARCHITECTURE_INDEX.md`

**Additions proposed:**
- Register Group 2700 arc parent + T1-T6 + this canonical summary in §1.N (arc registrations)
- Update §7 decision matrix to route "/docs/ restructuring" intent to this canonical summary
- Update §3 domain map with docs_restructuring domain (per DOMAIN_RESEARCH_PLAYBOOK §7)

### 7.4 Other affected docs

- **CLAUDE.md** — ADD the 5 CRITICAL_DOCS + PRIORITY_DOCS missing from pointer graph per T4 §6.3 (SYSTEM_OWNER, CURRENT_MISSION, USER_FEEDBACK_QUEUE, CAPABILITIES, DATABASE_MODEL_REFERENCE)
- **`docs/00-START-HERE/DOC_LIFECYCLE.md` §2c** — ADD discovery-layer enforcement clause per T3 MQ-T3-4 (retrieval-weight boost or explicit hint mechanism)
- **`00-START-NEXT-SESSION.md` template** — ADD `verify_doc_claims --only-drift` to close-ceremony checklist per T6 MQ-T6-6 (currently 0 refs in start-here template)
- **Parent §4 T5 clause** — UPDATE substrate-integrity mandate per T5 MQ-T5-8 (requires Chris re-ratification)
- **Playbook §15/§16** — CODIFY Rule #14 twin-pin discipline (SIGN pin ≠ arc pin) per T6 MQ-T6-2

---

## 8. Follow-On Research Queue

Ranked next-mission list. **Per Playbook §10:** questions + smallest next evidence to collect (NOT implementation plan). Migration execution is separate (see §7).

**Ranked by architectural uncertainty × risk × unblocked flows:**

1. **Discovery-layer enforcement for DOC_LIFECYCLE §2c** — smallest next evidence: propose 1-doc retrieval-weight boost for PLATFORM_INVENTORY.md; measure post-boost success@3 rate on T3 (c) scenarios. Uncertainty: HIGH (mechanism unknown); Risk: HIGH (T3 C5 evidence — archived stale outranks canonical); Unblocked flows: HIGH (fixes discovery for every counts-query scenario).
2. **HIGH-DRIFT rule canonicalization** (Rules #4, #5, #14 per T6 §5.5) — smallest next evidence: apply MQ-T6-8 actionable standard to 1 STALE surface (S1300 §3F) as pilot; measure downstream reader behavior. Uncertainty: MEDIUM; Risk: HIGH (per T6 Rigby fold 90); Unblocked flows: MEDIUM.
3. **Playbook v0.9 OP3 amendment** — smallest next evidence: draft amendment doc; solo-arc scope. Uncertainty: LOW (6/6 triggers over-corroborated); Risk: LOW (governance-only); Unblocked flows: MEDIUM (formalizes what's already practiced).
4. **Parent §4 T5 clause update** (MQ-T5-8) — smallest next evidence: draft amendment text; route to Chris for re-ratification per parent §5 Chris-lock. Uncertainty: LOW; Risk: LOW; Unblocked flows: LOW (mostly clarification).
5. **File moves per §3 target tree** — smallest next evidence: pilot 1 consolidation (proposed: `docs/adr/` → `docs/decisions/` — smallest scope with real convention collision); measure downstream migration surface area + generator/reader impact.
6. **Per-handoff citation_health verification for S2500-2600 range** — smallest next evidence: pick 10 uncited handoffs; run non-`docs/` citation search (code / PR bodies); classify healthy/brittle/broken. Uncertainty: HIGH (unknown until measured); Risk: LOW (informational tagging); Unblocked flows: LOW (per-doc archive decisions).
7. **Retrieval-frequency telemetry design** — smallest next evidence: propose schema for retrieval-count logging on `search_docs` corpus. Uncertainty: HIGH; Risk: MEDIUM (schema drift if wrong); Unblocked flows: MEDIUM (unlocks retrieval-proven classification for future audits).
8. **Generator/automation coordination for autogen output moves** (Rigby SIGN post-authoring Q3 addition) — smallest next evidence: enumerate every management command (`build_docs_index`, `refresh_doc_inventory_blocks`, `build_advisor_audit`, etc.) that writes to a `docs/*_AUDIT.md` root path; map to migration ordering for §3.4 root-file reduction. Uncertainty: MEDIUM; Risk: HIGH (unmapped generator writes will overwrite migrated files back to root); Unblocked flows: HIGH (blocks §3.2 audit consolidation + §3.4 root-file reduction until enumerated).

---

## 9. Cross-Links to Delegated Arcs

Per parent §2: arc respects DOC_LIFECYCLE constraints as canonical (delegates governance-of-governance to that doc rather than re-authoring). **Delegated arcs:**

- **DOC_LIFECYCLE governance** — `docs/00-START-HERE/DOC_LIFECYCLE.md` §2b/§2c/§3 — canonical primary; canonical summary respects but does not amend
- **Playbook governance** — `docs/ENGINEERING_PLAYBOOK.md` — canonical primary; v0.9 amendment for OP3 belongs to separate arc (§8 follow-on queue item #3)
- **Playbook v0.9 amendment arc** — separate arc, uncodified rule #10 (OP3 two-SIGN-per-audit) with 6/6 triggers; belongs to future ratification cycle

---

## 10. What This Research Taught Us About How to Do Research

Per S1399 Chris directive: every xx99 canonical summary includes this section. Meta-methodology retrospective.

### 10.1 What worked (methodology validated across this arc)

1. **Two-SIGN-per-audit (OP3) pattern.** Established at S2811 T1, ratified across T2-T6 (6/6 triggers). Empirically load-bearing across ALL audit shapes (measurement / primitive extraction / behavioral pain / audience classification / citation-graph + substrate integrity / rule inventory + drift). Post-authoring SIGN caught substantive errors open-SIGN missed every single time.
2. **Rigby-as-first-class-evidence-source methodology.** Established at T3 (Rigby ran empirical `search_docs` scenarios); extended at T4 (`kb_tool.stats` for corpus enumeration + targeted greps for asymmetry verification); T5 (mandated 10-doc substrate-integrity spot-check); T6 (rule-taxonomy expansion + STALE-vs-REPLICATED reclassification). 4 arc triggers — formalizable as first-class arc-audit pattern for behavioral substrate audits.
3. **Precision qualifier discipline.** Started at T4 (Rigby SIGN Q4 caught false-precision on ~1730 Human-primary count); adopted across T5+T6 (upper-bound labels; contamination disclaimers; approximate/exact distinction). Prevents downstream authors from overfitting to point counts.
4. **Anchor-verify at every scope decision point.** Now 15-session trend (S2806 onwards). T5's grep `\b` bug caught only because post-authoring re-verified. T4's CRITICAL_DOCS vs PRIORITY_DOCS conflation same class. Applying anchor-verify to author-Claude claims (not just predecessor framings) is what post-authoring SIGN operationalizes.
5. **Fold persistence + zoom-out ask per SIGN cycle (PLAYBOOK-6.10.7 + 6.10.8 + 6.10.9).** Held across arc; produced 5 arc triggers of Rigby zoom-out surfacing missed primitives / substrate concerns / MQ items.

### 10.2 What to codify into playbook v0.9 (per §20 two-triggers rule)

- **OP3 two-SIGN-per-audit** — 6/6 triggers, well over threshold. **Ready for Playbook v0.9 amendment as separate arc** (per §8 follow-on queue item #3).
- **Rigby-as-first-class-evidence-source** — 4 arc triggers (T3, T4, T5, T6). Below two-triggers threshold per §20 rule (which requires triggers across DIFFERENT ARCS not just child audits within one arc); wait for corroboration in another domain arc before codification.
- **Precision-qualifier discipline** — 3 arc triggers (T4, T5, T6). Below cross-arc threshold; observe in next domain arc.
- **MQ-T6-8 actionable standard for replicated-rule anchoring** — 1 arc trigger; below threshold; observe.

### 10.3 What didn't work / anti-patterns to avoid

- **`grep \b` word-boundary for `SESSION_NNNN` patterns** — T5 systematic decay-curve undercount 2×-16×. `\b` excludes matches followed by `_` (word char). **Anti-pattern:** use `\b` in citation-pattern greps without verifying the pattern-suffix is a non-word character. **Recovery:** use `[_.]` character class OR grep broader and filter.
- **`ls -la` `total NNNNN` line misread as directory name** — S2811 T1 `docs/18960/` ghost. Anti-pattern: pattern-match on `ls -la` header lines. Recovery: cross-check with `ls -d */` or `find -maxdepth 1 -type d`.
- **Attributing STALE labels to REPLICATED SURFACES without tool-verification** — T6 §5.2 (`tools/pa_local.sh` mislabel caught by Rigby Q2 tool-check). Anti-pattern: assume replicated ≡ stale without checking current content. Recovery: greppin the surface for current-correct patterns before labeling STALE.
- **Conflating similarly-named data structures in same source file** — T4 CRITICAL_DOCS (line 362) vs PRIORITY_DOCS (line 176) in `docs_context_builder.py`. Anti-pattern: read one, assume the other has same shape. Recovery: enumerate each independently with tool-verified line-anchored evidence.

### 10.4 Suggestions for the playbook itself

- **Add "audit-shape sessions require post-authoring SIGN" as PLAYBOOK-6.10.10** (per §10.2 codification proposal). Amendment text should note the failure-mode class variety (factual / coverage / methodology / classification) that only post-authoring catches.
- **Consider explicit "canonical structure vs migration staging" principle** (per §3 core principle) as a Playbook governance rule for any restructuring-shape work. Currently implicit in DOC_LIFECYCLE §2b + T2 FP-META HARD guardrail; making it explicit would prevent future arcs from over-scoping consolidation into runtime-coupled break paths.

### 10.5 Suggestions for future canonical summaries

- **Aggregate MQ items with severity + cross-child correlation** — this arc had ~46 MQ items across T1-T6. §7 anchor updates + §8 follow-on queue synthesized to ~10 actionable clusters. Future canonical summaries should aim for the same aggregation ratio (~5:1) — don't restate all MQ items; synthesize by cross-child pattern (per §4).
- **Explicit "twin-pointer discipline" checklist step** — per parent §5 D7 + memory `feedback_twin_deliverable_at_every_ratification`. Canonical summary should end with both (a) repo doc URL + (b) workspace deliverable UUID as a machine-readable twin_pointer frontmatter block.

---

## 11. Arc Change Log

| Session | Child | PR | SHA | Rigby SIGN verdict | Notable fold edits |
|---|---|---|---:|---|---|
| S2801 | Parent scoping | (pre-PR era) | — | Open SIGN — 6-thread package ratified via joint Claude+Rigby AGREE; Chris D-verdict "go ahead" | 6 threads locked; anti-scope defined; DOC_LIFECYCLE constraints inherited |
| S2811 | T1 inventory | #3239 | `8d5c89386` | Open + post-authoring; AGREE-WITH-EDITS post-authoring | **`docs/18960/` ghost reference REMOVED** (misread of `ls -la` block-count line) + Snapshot warning added |
| S2812 | T2 pattern extraction | #3241 | `a70b01265` | Open + post-authoring; AGREE-WITH-EDITS post-authoring | Added SP5 (runtime-coupled anchor stability) + OP4 (registration/visibility mechanics); FP-META HARD guardrail against autogen |
| S2813 | T3 human pain | #3243 | `82ae21a2b` | Open + post-authoring; AGREE-WITH-EDITS post-authoring (6 substantive edits) | Rigby ran 5 empirical search_docs C1-C5; drift spot-check confirmed structural not query-fragility; 5-pain-type taxonomy adopted |
| S2814 | T4 audience segmentation | #3245 | `bcc82a1a8` | Open + post-authoring; DISAGREE on Q1 post-authoring | **CRITICAL_DOCS (5) vs PRIORITY_DOCS (10) distinction corrected** (open-SIGN had conflated); FP-META HARD guardrail scoped; discovery-vs-injection asymmetry surfaced |
| S2815 | T5 handoffs+audits proliferation | #3247 | `c1e1ceab3` | Open + post-authoring; **DISAGREE on Q3 decay-curve claim** | **grep `\b` bug caught** — decay-curve corrected across §5+§8+§9; chunk-anchor citation-integrity finding VALIDATED (parent §4 T5 based on false premise); MQ-T5-8 explicit action item added |
| S2816 | T6 anchor drift | #3249 | `6a9f2b000` | Open + post-authoring; AGREE-WITH-EDITS post-authoring | **Rule #5 `tools/pa_local.sh` reclassified** from STALE to REPLICATED SURFACE (Rigby tool-check); Rule #13 placeholder dropped; MQ-T6-8 narrowed from meta-program to actionable standard |
| S2817 | 2799 canonical summary | (this doc) | (pending) | Open — AGREE with 4 tweaks; post-authoring pending | Migration ordering swap (#4 → #2); target tree calibrated with runtime-coupled constraints; workspace_id resolved (Donkey Betz `b4503364-...`); core principle "canonical structure = target; migration = staged; generator/runtime = compatibility-first" made explicit |

---

## 12. Appendix — Provenance

**Session:** S2817 (2026-07-18, night — NINTH session close of the day)
**Git HEAD at authoring:** `443525618c72` (S2816 close cascade)
**Ratifier:** Chris D-verdict "Let's do 2799" at S2817 open
**Arc timeline:** S2800 directive (2026-07-16) → S2801 parent-scoping (2026-07-16) → 14 Colorado sessions bumped → S2811-S2816 T1-T6 (all 2026-07-18) → **S2817 canonical summary (this doc, 2026-07-18)**. **8-session arc-close-to-arc-close; 17 calendar sessions from S2800 directive to close.**

**Rigby SIGN cycles applied:** Open SIGN Q1 (§3 target tree calibration) / Q2 (migration ordering) / Q3 (over-scope risks + workspace_id resolution). AGREE with 4 tweaks all applied inline. Post-authoring pressure-test SIGN — SEVENTH-CONSECUTIVE OP3 trigger — routed after this authoring completes.

**Twin-pointer discipline** per parent §5 D7 + memory `feedback_twin_deliverable_at_every_ratification`:
- **Repo doc:** this file at git HEAD `443525618c72` + successor close-cascade SHA
- **Workspace deliverable:** to be created in Donkey Betz workspace (`b4503364-2573-4401-9e28-61a739e0ce50`) via ORM-direct create per memory `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic` (bypasses pa_deliverables_tool diagnostic-flag bug). ID filled at close.

**Tools used:**
- Claude Read of Playbook §10 + §11.3 for canonical summary template
- Claude cross-child synthesis (T1-T6 all read before authoring; per Rigby SIGN Q3 no re-audit — synthesis only)
- Rigby `workspace_tool.list` for workspace_id resolution (Donkey Betz identified)
- Rigby coherence-check meta-review (surfaced the "canonical structure vs migration staging" contradiction to resolve explicitly in §3 core principle)

**Non-goals held throughout authoring** per Playbook §10:
- No re-audit of T1-T6 evidence (§2 rollup cites; §3-§7 synthesize)
- No implementation plan / owner assignments / timelines (§8 kept as "questions + smallest next evidence")
- No new taxonomies beyond T1-T6 established (§3 target tree maps to real paths; §4-§5 use existing terminology)
- No file moves during arc close (per parent §5)
- No anchor edits in this doc (§7 lists proposed; ARCHITECTURE_INDEX v-bump applies)

---

**End of 2799 — Group 2700 canonical summary. Arc CLOSES with this deliverable.**

**Post-arc: migration execution per §7 anchor updates + §8 follow-on queue. Playbook v0.9 amendment (OP3) queued as separate arc per §10.2.**
