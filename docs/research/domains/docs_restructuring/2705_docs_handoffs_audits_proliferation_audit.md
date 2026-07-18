---
title: "S2815 /docs/ Handoffs + Audits Proliferation Audit (T5 of Group 2700 arc)"
status: active (audit deliverable — citation graph + decay curve + lifecycle proposal + substrate-integrity finding)
authority: T5 child audit of Group 2700 parent arc
session: 2815
date: 2026-07-18
domain_slug: docs_restructuring
research_group: 2700
thread: T5
authors: Claude Code (Chris directed at S2815 open); Rigby (10-query citation-integrity spot-check + Q1/Q2/Q3 methodology corrections)
supersedes: none
related:
  - docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md   # parent (Chris-locked 2026-07-16; T5 substrate-integrity mandate is Rigby fold 92, future_trigger triggered here)
  - docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md       # T1 predecessor (S2811) — 1033 handoff baseline
  - docs/research/domains/docs_restructuring/2702_docs_research_pattern_extraction_audit.md # T2 predecessor (S2812)
  - docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md   # T3 predecessor (S2813) — retrieval-eligibility ≠ retrieval-behavior
  - docs/research/domains/docs_restructuring/2704_docs_audience_segmentation_audit.md   # T4 predecessor (S2814) — surface counts
  - docs/handoffs/SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md                                 # prior mass-move; §4 T5 substrate-integrity clause pointer
  - docs/00-START-HERE/DOC_LIFECYCLE.md                                                  # handoff/audit governance
scope: T5 = citation graph + decay curve + audit-dir triple + handoff-lifecycle proposal + substrate-integrity spot-check per parent §4
non_goals:
  - executing any file moves, deletions, renames (parent §5 arc non-goals)
  - proposing autogen-based citation-graph generator (canonical summary + downstream implementation)
  - fixing the RAG retrieval-behavior issues from T3 §7 (out of T5 scope)
  - resolving audit-dir triple (T5 measures + tags; canonical summary designs)
delegates_to: T6 (anchor drift); canonical summary 2799 (restructuring proposal + lifecycle-execution plan)
owner: claude+rigby
---

# Session 2815 — /docs/ Handoffs + Audits Proliferation Audit (Group 2700, Thread 5)

> **What this doc is.** T5 measurement — handoff citation graph + bimodal decay curve + audit-dir triple analysis + handoff-lifecycle proposal with severity tags + citation-integrity substrate finding. Rigby is co-evidence-source (10-query spot-check + methodology corrections).
>
> **What this doc is not.** A proposal to move/delete/rename any handoff or audit doc. A rewrite of DOC_LIFECYCLE. Migration executes in follow-up sessions per parent §5.

---

## 1. Why T5 fifth

Per parent doc §4:

> T5 — Handoffs + audits proliferation. Scope: 676+ handoffs + growing `docs/audits/` + `docs/audit-2026/` (April historical) + `docs/archive/`. Write-once-read-rarely triage. Deliverable: proposal for handoff lifecycle (with severity tags: keep-in-place / archive-after-N / eligible-for-deletion). **Substrate integrity check (Rigby fold 92, future_trigger):** handoffs previously mass-moved and chunk IDs reset per `SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md#8`. T5 MUST include a 10-doc citation-integrity spot-check — do old `[docs/handoffs/SESSION_NNN.md#K]` citations still resolve to the intended chunk?

T5 executes the mandate. The substrate-integrity check produced a substantive discovery — see §7.

**Fifth-consecutive OP3 trigger** — two-SIGN cycle applied (S2811-S2814 pattern). Post-authoring SIGN pressure-test follows this authoring.

---

## 2. Anchors T5 cites (never restates)

| Source | What it holds | T5 usage |
|---|---|---|
| Parent doc §4 T5 | Method + deliverable + substrate-integrity mandate | T5 respects; substrate check produced novel finding (§7) |
| T1 §3.1 | 1033 handoffs baseline; 3 audit dirs (10+15+93=118) + 20 loose `*AUDIT.md` at root | Cited as baseline |
| T3 §7 C1-C5 | Retrieval-eligibility ≠ retrieval-behavior | Cited to justify grep-primary methodology |
| T4 §6.1 | ~50 measurable-primary audience-classified docs | Cited for cross-reference |
| `SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md` §8 | Prior mass-move + chunk-ID reset | Cited as the substrate-integrity concern the parent §4 T5 clause references |

---

## 3. Baseline (at git HEAD `386b16cf8980`)

- **1037 handoff files** in `docs/handoffs/` (up from T1's 1033; +4 from S2811-S2814 daily arc adds)
- **1306 corpus docs** contain `SESSION_NNNN` references (dense citation graph)
- **3 audit directories:** `docs/audit/` (10 files) + `docs/audit-2026/` (15 files) + `docs/audits/` (93 files) = **118 files across 3 parallel dirs**
- **20 loose `*AUDIT.md`** at `docs/` root

**Total T5-scoped corpus: ~1175 files** (1037 handoffs + 118 audits + 20 loose AUDIT).

---

## 4. Handoff citation graph — top-cited (grep-only per Rigby SIGN Q1 AGREE)

**Method:** `grep -rho "SESSION_[0-9]+" docs --include="*.md" | sort | uniq -c | sort -rn`. Counts inbound `SESSION_NNNN` references across the entire `/docs/` corpus. Excludes self-references only if the pattern includes the specific filename; bare-`SESSION_NNNN` count includes self-refs (a handoff's own frontmatter). Precision qualifier: **approximate**, not exact.

**Top-cited handoffs (bare-`SESSION_NNNN` mentions across corpus, includes self-refs + templates — per Rigby SIGN Q2 correction):**

**Contamination disclaimer:** counts below are TOTAL corpus mentions of the session-string pattern, not distinct inbound link-citations. Includes bare references, templates, self-mentions in ratification handoffs, and repeated mentions within a single doc. Treat as *popularity/centrality* signal, not exact inbound-citation count.

| Rank | Handoff | Mentions (~) | Interpretation |
|---:|---|---:|---|
| 1 | SESSION_2707 | ~128 | Very recent; heavily-mentioned (bootstrap-adjacent + I-0100 ratification cluster) |
| 2 | SESSION_2701 | ~51 | Recent; Cycle 1A ratification cluster |
| 3 | SESSION_1143 | ~45 | **THE docs-cleanup handoff — Chris's prior audit + governance ancestor** |
| 4 | SESSION_25 | ~44 | Very early; foundational-era doc |
| 5 | SESSION_37 | ~33 | Foundational-era |
| 6 | SESSION_28 | ~30 | Foundational-era |
| 7 | SESSION_2751 | ~30 | Recent Playbook-era |
| 8 | SESSION_20 | ~30 | Foundational-era |
| 9 | SESSION_40 | ~28 | Foundational-era |
| 10 | SESSION_38 | ~28 | Foundational-era |
| 11 | SESSION_2700 | ~28 | Group 2700 arc-adjacent |
| 12 | SESSION_1264 | ~25 | Mid-era; Playbook precursor |

**Bracket-path citations (`[docs/handoffs/SESSION_...md]` form, most-cited):**

| Handoff | Refs |
|---|---:|
| SESSION_1264_AUTHORITY_WARN_MODE.md | 16 |
| SESSION_2701_CYCLE_1A_IMPLEMENTATION_HANDOFF.md | 14 |
| SESSION_2750_I0302_PHASE_4_SUB_PHASE_3_CLOSED.md | 10 |
| SESSION_1137_JESSICA_PHASES_1_4_RATIFICATION.md | 10 |
| SESSION_2751_I0302_PHASE_4_CLOSED.md | 9 |

**Observation: handoffs are NOT write-once-read-never.** Foundational-era handoffs (SESSION_20-40) are still cited 28-44 times each. Playbook-era + recent-arc handoffs dominate the top. **The parent §4 T5 hypothesis "write-once-read-rarely triage" is only partly correct — some handoffs are heavily load-bearing forever.**

---

## 5. Bimodal decay curve (age vs citation count)

**Method:** Per-100-session bucket, sum `SESSION_NNNN` references across corpus, average per cited session.

| Session range | Cited sessions | Total refs | Avg refs/session | Interpretation |
|---|---:|---:|---:|---|
| S1-100 | 83 | 666 | **8** | Foundational — heavily cited, high avg |
| S500-600 | 63 | 168 | 2-3 | Modest but broad — many sessions cited |
| S1000-1100 | 21 | 80 | ~3 | Playbook-precursor era |
| S1400-1500 | 9 | 19 | 2 | Modest |
| S1800-1900 | 9 | 23 | 2 | Modest |
| S2200-2300 | 5 | 10 | 2 | Low breadth (few sessions cited) |
| S2500-2600 | **2** | **3** | 1 | **Very low — only 2 sessions cited** |
| S2700-2800 | 74 | 412 | **5** | Recent — heavily cited, second-highest avg |

**Post-authoring correction (per Rigby SIGN Q3 drift spot-check):** Original T5 draft claimed S2500-2600 had ZERO cited sessions. Rigby ran `search_docs("SESSION_2500")` at post-authoring SIGN → 1 match found (`docs/research/domains/api/2500_api_domain_scoping.md:1162`). Investigation traced root cause: my original grep used `\b` word-boundary which excludes matches where `SESSION_NNNN` is followed by `_` (underscore is a word char). Since canonical handoff citations are `SESSION_NNNN_TOPIC.md`, the `\b` pattern excluded ALL canonical link-form citations. Corrected grep uses `[_.]` character class → new counts above. **All original decay-curve counts undercounted by 2×-16×.**

**Bimodal pattern (corrected):**
- **Both ends heavy:** foundational (S1-100 at 83 sessions / 666 refs) + recent (S2700-2800 at 74 sessions / 412 refs) show high citation activity
- **Middle less concentrated but not zero:** S1400-1500 through S2500-2600 all show some citation, with S2500-2600 lowest (2 sessions / 3 refs)
- **No range is completely zero-cited.** Original "100 handoffs never referenced" claim was a grep-methodology artifact, not a real substrate finding.

**Chris's `project_half_finished_arcs_from_life_interruptions` memory + corrected T5 evidence:** The middle-range low-citation pattern (especially S2500-2600 with only 2 of 100 sessions cited) remains a **suggestive but weaker** abandoned-arc signal. Per-doc review needed before any bulk-deletion action.

**Precision qualifier:** even the corrected counts are approximate. New grep excludes some valid patterns (SESSION_NNNN followed by comma, quote, end-of-line). Total corpus mention counts are floors, not exact values.

---

## 6. Audit-dir triple analysis

**Method:** Enumerate all `*.md` files in each of the 3 audit dirs; grep each filename across corpus; report top citations.

### 6.1 `docs/audit/` (10 files)

| File | Refs | Notes |
|---|---:|---|
| `README.md` | 363 | **CONTAMINATED count** — matches every "README.md" across corpus |
| `CLEANUP_PLAN.md` | 45 | High — governance-ish doc |
| `AUDIT_V1.md` | 12 | Explicit V1 labeling; low citation |
| `SESSION_1143_DOCS_AUDIT.md` | 11 | **DUPLICATE — also in `docs/audit-2026/`** |
| `SESSION_1143_ABANDONED_FEATURES_AUDIT.md` | 4 | |
| `SESSION_1143_REDUNDANCY_HUNT.md` | 3 | |
| `SESSION_1143_PHASE5_EXECUTION_PLAN.md` | 1 | |
| `SESSION_1143_HANDOFFS_RETENTION_OPTIONS.md` | 1 | |
| `TRUTH_PROPAGATION_PRINCIPLES.md` | **0** | Zero-cited candidate |
| `TRUTH_PROPAGATION_PHASE.md` | **0** | Zero-cited candidate |

### 6.2 `docs/audit-2026/` (15 files — April 2026 structured attempt)

| File | Refs | Notes |
|---|---:|---|
| `04-content-pipeline.md` | 13 | Most-cited of the structured set |
| `SESSION_1143_DOCS_AUDIT.md` | 11 | **DUPLICATE with `docs/audit/`** |
| `12-infrastructure.md` | 7 | |
| `01-celery.md` | 6 | |
| `00-AUDIT-PLAN.md` | 6 | Plan doc; moderate |
| `HALF_BUILT_FEATURES_AUDIT.md` | 2 | |
| `08-personal-assistant.md` | 2 | |
| `11-frontend-workspaces.md` | 1 | |
| `10-conceptforge.md` | 1 | |
| `09-signals-initiatives.md` | 1 | |
| (5 other numbered audit files) | ≤5 each | Lower-cited |

### 6.3 `docs/audits/` (93 files — ad-hoc accumulator)

| File | Refs | Notes |
|---|---:|---|
| `INDEX.md` | 894 | **CONTAMINATED count** — matches every "INDEX.md" across corpus |
| `SYSTEM_AUDIT_PLAN.md` | 24 | Highest-cited actual audit doc |
| `PA_TOOLS_GAP_MAP_S2795.md` | 10 | |
| `UI_GAPS_AGENTS_MIGRATION.md` | 6 | |
| `PUBLIC_PATHS_AUDIT_S2789.md` | 6 | |
| `PA_TOOLS_GAP_MAP_S2796.md` | 6 | |
| `discovery_discord_commands.md` | 6 | |
| `discovery_celery_tasks.md` | 6 | |
| `discovery_backend_services.md` | 6 | |
| `discovery_api_endpoints.md` | 6 | |

**Cross-dir findings:**

- **File duplication:** `SESSION_1143_DOCS_AUDIT.md` appears in BOTH `docs/audit/` AND `docs/audit-2026/`. Both cited 11 times. Real duplication — same filename, likely divergent copies.
- **Cluster: `SESSION_1143_*.md` group** (5 files in `docs/audit/`, 1 duplicated in `docs/audit-2026/`) — all descend from Chris's 2026-01 docs-audit arc. Preserved as historical governance artifacts.
- **Autogen-heavy files at root** (20 loose `*AUDIT.md`) are the current-arc equivalent of `docs/audit-2026/`'s numbered set — but as loose root files, they're subject to T3 root-sprawl finding.
- **Zero-cited candidates:** `TRUTH_PROPAGATION_PRINCIPLES.md` + `TRUTH_PROPAGATION_PHASE.md` in `docs/audit/` — write-once-never-cited.
- **INDEX.md + README.md counts are contaminated** — matching filename appears in many places; not useful signal.

---

## 7. SUBSTRATE-INTEGRITY FINDING (parent §4 T5 mandate)

**Parent §4 T5 substrate-integrity clause (Rigby fold 92, future_trigger triggered here):**

> Handoffs previously mass-moved and chunk IDs reset per `SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md#8`. T5 MUST include a 10-doc citation-integrity spot-check — do old `[docs/handoffs/SESSION_NNN.md#K]` citations still resolve to the intended chunk?

**T5 finding (major substrate discovery via Rigby's 10-query tool_runs):**

**The `[docs/handoffs/SESSION_NNN.md#K]` chunk-anchor citation pattern IS NOT USED IN THE CORPUS.** Rigby ran 10 targeted `repo_tool.search` queries against the pattern for SESSION_1143, SESSION_25, SESSION_1234, SESSION_819, SESSION_1098, SESSION_555, SESSION_1264, SESSION_1137, SESSION_2707, SESSION_2701 — ALL RETURNED 0 MATCHES.

**Follow-up grep evidence:**
- **Actual `#K` chunk-anchor citations:** 4 total, ALL LITERAL TEMPLATE PLACEHOLDERS (`[docs/handoffs/SESSION_NNN.md#K]` with literal "NNN" and "K") in docs describing the pattern.
- **Actual section-heading `#N` anchors:** DO exist — `SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md#8` appears multiple times in corpus (parent §4 T5 clause itself uses this format).
- **Most actual citations:** plain-path bracket form `[docs/handoffs/SESSION_XXX_TOPIC.md]` with NO anchor. Top-cited (§4): SESSION_1264 (16 bracket-path refs), SESSION_2701 (14), SESSION_2750 (10).

**Substrate-integrity implication:**

- The parent §4 T5 concern about "chunk-ID reset after mass-move" was **based on a citation pattern that never got adopted**. The concern is moot for chunk-anchor citations because they don't exist in production.
- The concern IS still valid for **section-heading `#N` anchors** (small population; e.g., `SESSION_1143_...#8`). Spot-check: `SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md` has 12+ `##` headings; the 8th is "What changed in the corpus (numerically)". If `#8` = 8th `##` heading (Markdown auto-anchor convention), the citation resolves. **PASS for this citation.**
- **Broader implication:** any future mass-move that renames files DOES break the plain-path `[docs/handoffs/SESSION_XXX_TOPIC.md]` citations (16+14+10+... refs at stake for the top-cited handoffs). The substrate-integrity risk shifted from chunk-ID drift to filename drift when the citation pattern shifted from `#K` chunks to plain paths.

**Citation-integrity taxonomy (per Rigby SIGN Q3 AGREE — `citation_health` boolean attribute preserved without adding a 4th severity tag):**

| Citation form | Volume | Failure mode | Health |
|---|---:|---|---|
| Chunk-anchor `#K` | ~0 (only template placeholders) | N/A — pattern not adopted | HEALTHY (moot) |
| Section-heading `#N` | Small (dozens) | Heading structure change | HEALTHY at HEAD (spot-check PASS) |
| Plain-path `[docs/handoffs/SESSION_XXX.md]` | High (thousands) | Filename change / mass-move | BRITTLE — any future move breaks |

---

## 8. Handoff lifecycle proposal (per parent §4 T5 deliverable)

**3 severity tags** (per Chris ratification via parent §5 D6) + **1 citation_health boolean** (per Rigby SIGN Q3 AGREE — attribute not tag).

### 8.1 Severity tag definitions (post-Rigby SIGN Q2+Q4 AGREE-WITH-EDITS)

| Tag | Criteria | Action |
|---|---|---|
| **keep-in-place** | mentions **≥3** (hardcoded boundary — Rigby SIGN Q4 clarity) OR governance/ratification/playbook-adjacent OR linked from CLAUDE.md, ENGINEERING_PLAYBOOK, or DOC_LIFECYCLE OR referenced by any governance-index doc (Rigby SIGN Q4 override) OR is legally/compliance relevant (Rigby SIGN Q2 override) | No action; retain at current path |
| **archive-after-N** (N = 12 months) | mentions 1-2 AND age > 12 months AND not covered by any keep-in-place criterion above | Move to `docs/archive/handoffs-YYYY/` in a future migration session |
| **eligible-for-deletion** | mentions 0 AND age > 12 months AND not governance/ratification/legally-relevant | Optionally delete OR move to `archive/`; canonical summary decides |

**Boolean attributes (Rigby SIGN Q3+Q4 AGREE — attributes not tags):**

- `citation_health: healthy` — no known anchor drift; plain-path citations resolve to existing file
- `citation_health: brittle` — plain-path citations exist but file is a mass-move candidate (mid-range sessions with low mentions)
- `citation_health: broken` — anchor no longer resolves (currently: 0 known; future risk if migration executes)
- `is_superseded: false | true | pending` (optional, per Rigby SIGN Q4 optional nuance) — flag if a keep-in-place doc has a known replacement in progress; enables archive-eligibility once replacement is stable

### 8.2 citation_health boolean (Rigby SIGN Q3 AGREE — attribute, not tag)

- `citation_health: healthy` — no known anchor drift; plain-path citations resolve to existing file
- `citation_health: brittle` — plain-path citations exist but file is a mass-move candidate (mid-range sessions with low citation)
- `citation_health: broken` — anchor no longer resolves (currently: 0 known; future risk if migration executes)

### 8.3 Applied to T5 evidence

| Session range | Recommended tag | Rationale (post-decay-correction) |
|---|---|---|
| S1-100 (foundational) | keep-in-place | 83 cited sessions / 666 refs / avg 8 — high citation ancestor context |
| S500-600 | mixed (per-doc review) | 63 cited sessions / 168 refs / avg 2-3 — broader citation than original claim suggested; not blanket-archivable |
| S1000-1100 (Playbook-precursor) | keep-in-place mostly | 21 cited sessions / 80 refs; ratification handoffs concentrated here |
| S1400-1500 | mixed (per-doc review) | 9 cited sessions / 19 refs; some referenced, most not — case-by-case |
| S1800-1900 | mixed (per-doc review) | 9 cited sessions / 23 refs; similar to S1400 |
| S2200-2300 | archive-after-N (mostly) | 5 cited sessions / 10 refs; low citation breadth |
| **S2500-2600 (very-low)** | **archive-after-N default; per-doc review for eligible-for-deletion** | Corrected: 2 cited sessions / 3 refs (not zero). ~98 handoffs uncited but ≠ "never referenced" (some may be cited only in code / PR bodies / non-`docs/` locations). Per-doc review before deletion. |
| S2700-2800 (recent) | keep-in-place | 74 cited sessions / 412 refs / avg 5 — active, high citation |

**Explicit non-goal per parent §5:** T5 does NOT execute any of these classifications. Canonical summary at 2799 decides; migration session implements.

---

## 9. Playbook §9 canonical questions (adapted to T5 scope)

| Q# | Question (adapted) | T5 answer |
|---|---|---|
| Q1 | How many handoffs total? | 1037 (T1 baseline 1033 + 4 daily arc adds) |
| Q2 | How many corpus docs cite handoffs? | 1306 |
| Q3 | Are handoffs write-once-read-never? | **NO** — top-cited handoffs range from S25 (44 refs) to S2707 (128 refs). Foundational + recent both heavily load-bearing. |
| Q4 | Is there a decay curve? | **Bimodal** — foundational + recent high; middle-ranges (S500-600, S2200-2300, S2500-2600) low or zero. |
| Q5 | Are any 100-session ranges completely zero-cited? | **NO** (post-authoring correction — original claim was a grep-methodology artifact). S2500-2600 is the lowest at 2 cited sessions / 3 refs; other ranges have 5-83 cited sessions. |
| Q6 | Do parallel audit dirs (audit/ + audit-2026/ + audits/) have file duplication? | **YES** — `SESSION_1143_DOCS_AUDIT.md` exists in both `docs/audit/` AND `docs/audit-2026/`, both cited 11 times. |
| Q7 | Do old `[docs/handoffs/SESSION_NNN.md#K]` chunk-anchor citations still resolve? | **N/A — the chunk-anchor pattern was NEVER ADOPTED.** All 4 corpus matches for `#K` are literal template placeholders. Parent §4 T5 substrate-integrity concern is moot for chunk-anchor citations. Real citation risk shifted to plain-path filename drift. |
| Q8 | Do section-heading `#N` anchors still resolve? | **Spot-check PASS** — `SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md#8` = "What changed in the corpus" section per current heading structure. |
| Q9 | What is the substrate-integrity risk NOW? | Plain-path `[docs/handoffs/SESSION_XXX_TOPIC.md]` citations (thousands) — any future rename breaks them. citation_health BRITTLE for mass-move-candidate handoffs. |
| Q10 | Is `docs/archive/` (1388 files) integrated into RAG search per T3? | **YES** (T3 §7 C5 evidence — archive content outranks canonical). Any handoff moved to `docs/archive/handoffs-YYYY/` will REMAIN in RAG corpus unless archive-corpus segregation happens (T3 MQ-T3-1). |
| Q11-Q28 | Restructuring proposal; migration ordering; retrieval telemetry; per-doc tagging execution | **Out of T5 scope** — T6 / canonical summary owns |

---

## 10. Migration Queue (post-arc)

Per parent §5. T5 items are **classification + lifecycle proposals**, not migration execution. **Severity: INFORMATIONAL.**

| # | Item | Evidence source (this doc) | Severity | Notes |
|---|---|---|---|---|
| MQ-T5-1 | **S2500-2600 range: 2 cited sessions of ~100 (very-low citation, NOT zero — post-authoring correction).** Weaker bulk-abandonment signal than original T5 draft claimed. Per-doc citation_health verification still needed; default tag = archive-after-N; eligible-for-deletion requires explicit per-doc review. | §5 + §8.3 | INFORMATIONAL (moderate signal, downgraded from "high" after decay correction) | Canonical summary decides per-doc review approach; migration session executes with per-doc gate + non-`docs/` citation check (code / PR bodies). |
| **MQ-T5-8 (NEW — Rigby SIGN Q5 DISAGREE)** | **Parent doc §4 T5 substrate-integrity clause is based on a false premise.** Chunk-anchor `[docs/handoffs/SESSION_NNN.md#K]` pattern is template-only, not a real corpus pattern (§7). Leaving as quiet-flag risks repeated future OP3 triggers chasing wrong anchor family + policy drift where the "mandate" stays mis-specified in canon. **Explicit action item for canonical summary at 2799:** update parent §4 T5 substrate-integrity mandate to target *actual* handoff citation patterns in use (session-string mentions, filename links, real anchor styles), NOT the template `[...#K]` form. Preserves the spirit (substrate integrity matters) while correcting the mechanism. | §7 + §11 (T5 does NOT resolve — canonical summary owns) | INFORMATIONAL (**explicit canonical-summary action item, not just flag**) | Canonical summary at 2799 authors the parent doc amendment; requires Chris ratification per parent §5 (parent is Chris-locked S2801). |
| MQ-T5-2 | **Audit-dir triple + 20 loose `*AUDIT.md` at root = 138 files across 4 surfaces.** T1 §7.1 already flagged; T5 adds citation counts (INDEX.md/README.md contaminated, actual audit content 6-45 refs each). | §6 | INFORMATIONAL | Consolidation decision at canonical summary. |
| MQ-T5-3 | **`SESSION_1143_DOCS_AUDIT.md` exists in BOTH `docs/audit/` AND `docs/audit-2026/`.** Real file duplication (both cited 11 times). Content likely divergent. | §6.1 + §6.2 | LOW-MODERATE | Migration session reconciles: keep one, superseded-mark other. |
| MQ-T5-4 | **Substrate-integrity finding: chunk-anchor `#K` citation pattern was NEVER ADOPTED.** Parent §4 T5 concern moot for chunk anchors; still valid for plain-path filename drift. | §7 | INFORMATIONAL (major substrate discovery) | Canonical summary updates parent §4 T5 clause; migration session ensures rename-safety for plain-path citations (redirect stubs OR pre-move citation-graph re-write). |
| MQ-T5-5 | **Handoffs are NOT write-once-read-never.** Some foundational-era handoffs (SESSION_20-40) are cited 28-44 times. keep-in-place is the correct default for cited handoffs regardless of age. | §4 + §5 + §8.3 | INFORMATIONAL | Confirms parent §4 T5 hypothesis was overly pessimistic. |
| MQ-T5-6 | **Zero-cited audit docs** in `docs/audit/`: `TRUTH_PROPAGATION_PRINCIPLES.md` + `TRUTH_PROPAGATION_PHASE.md`. Never referenced from anywhere in corpus. | §6.1 | LOW | Migration session considers deletion or archive-move; per-doc review. |
| MQ-T5-7 | **Archive is NOT segregated from RAG corpus** (T3 §7 C5 finding). Any handoff moved to `archive/handoffs-YYYY/` REMAINS retrievable via `search_docs`. Migration to archive is filesystem-partition-only, not search-partition. | §9 Q10 + T3 §7 C5 | INFORMATIONAL | Cross-reference to T3 MQ-T3-1. Canonical summary decides archive-corpus segregation approach. |

---

## 11. What T5 does NOT resolve (explicit hand-offs)

Per parent §4 anti-scope:

| Question | Handed off to |
|---|---|
| Which specific S2500-2600 handoffs are safe to delete? | Canonical summary at 2799 (per-doc review) + migration session (execution) |
| Should audit-dir triple consolidate into one canonical `docs/audits/`? | Canonical summary at 2799 |
| Should `SESSION_1143_DOCS_AUDIT.md` duplicate be reconciled? | Canonical summary + migration session |
| Should plain-path citations be pre-rewritten to redirect stubs before any mass-move? | Canonical summary at 2799 (substrate-integrity plan) |
| Should the parent §4 T5 substrate-integrity clause be updated to reflect the moot chunk-anchor finding? | Canonical summary at 2799 (parent doc is Chris-locked; update requires ratification) |
| Which specific docs get `citation_health: brittle` flag? | Canonical summary + downstream implementation (per-doc tagging) |
| Should mid-range zero-cited handoffs (S500-600, S2200-2300) get bulk-archive without per-doc review? | Canonical summary at 2799 |
| Should archive-corpus segregation happen for RAG search? | Canonical summary + downstream implementation session |

---

## 12. Provenance

**Session:** S2815 (2026-07-18, evening, immediately post-S2814-close)
**Ratifier:** Chris D-verdict "Let's continue" at S2815 open
**Git HEAD at authoring:** `386b16cf8980` (S2814 close cascade)

**Rigby SIGN cycles (TWO per S2811-S2814 OP3 lesson — 5/5 pattern):**

- **Open SIGN** (Q1 methodology / Q2 severity tag thresholds / Q3 zoom-out + mandated 10-doc citation-integrity spot-check).
  - Q1: AGREE grep-only primary + retrieval sanity-check on 3/10 for citation-integrity docs
  - Q2: AGREE thresholds with tweak — added "legally/compliance relevant" override in keep-in-place criteria
  - Q3: AGREE — S500-600 + S2200-2300 + S2500-2600 flagged as abandoned-arc candidates; **DISAGREE with 4th severity tag**, propose `citation_health` boolean attribute instead
  - **Substrate spot-check mandate: Rigby ran 10 `repo_tool.search` queries for `docs/handoffs/SESSION_NNN.md#K` pattern across 10 sessions → ALL RETURNED 0 MATCHES. Chunk-anchor pattern never adopted in corpus.**
- **Post-authoring pressure-test SIGN — FIFTH-CONSECUTIVE OP3 trigger. Substantive corrections:**
  - **Q1 (drift spot-check on substrate finding):** AGREE — chunk-anchor pattern absence validated under drift re-check (1 match found, in parent 2700 doc itself as template reference).
  - **Q2 (SESSION_2707 128-count integrity):** AGREE-WITH-EDITS — rephrase "128 refs" as "~128 corpus mentions (grep-count; includes bare session-string mentions, not just link citations)" + contamination disclaimer. Applied throughout §4.
  - **Q3 (S2500-2600 zero-cited claim):** **DISAGREE — decay-curve was systematically wrong.** My original grep used `\b` word-boundary which excluded ALL canonical `SESSION_NNNN_TOPIC.md` matches (underscore is a word character). Corrected grep with `[_.]` character class → all decay-curve counts undercounted 2×-16×. S2500-2600 has 2 cited sessions / 3 refs, not zero. Applied throughout §5 + §8.3 + §9 Q5 + §10 MQ-T5-1.
  - **Q4 (severity tag calibration):** AGREE-WITH-EDITS — hardcoded "≥3 = keep-in-place" boundary for clarity; added governance-index override; added optional `is_superseded` boolean nuance. Applied to §8.1.
  - **Q5 (F-BLOCKING zoom-out on parent §4 T5 clause update):** **DISAGREE — quietly-flagging is NOT sufficient.** T5 must recommend explicit canonical-summary action item to update parent doc §4 T5 substrate-integrity mandate. Reason: parent clause encodes premise-level requirement (chunk-anchor check) that's template-only; leaving as quiet-flag risks repeated OP3 triggers + policy drift. Added MQ-T5-8 (new) with explicit action-item severity.

**Fifth-consecutive OP3 trigger fully justified.** Beyond the 3-trigger Playbook v0.9 promotion threshold met at S2813, T4 caught CRITICAL_DOCS/PRIORITY_DOCS conflation, and T5 caught a SYSTEMATIC decay-curve error (grep `\b` bug) that would have propagated false "100 handoffs zero-cited" claim into canonical summary + potential mass-deletion policy. **Post-authoring SIGN discipline is now empirically load-bearing across every audit shape.**

**Novel substrate finding:** parent §4 T5's chunk-anchor citation-integrity concern was based on a citation pattern that was documented (in S1143 audit at line `#8`) but never adopted in practice. Rigby's 10-query spot-check confirmed. **This finding may itself warrant a canonical-summary-level update to parent §4 T5 clause** — the substrate-integrity concern needs to be re-scoped to plain-path filename-drift risk, not chunk-anchor drift.

**Precision qualifiers applied throughout (T4 lesson):**
- Section §4 top-cited counts: approximate (contamination on common filenames noted)
- Section §5 decay-curve: approximate (bucket-boundary + non-`docs/` citations not measured)
- Section §6 audit-dir counts: precise for enumerated actual audit docs; contaminated for INDEX.md / README.md
- Section §8 severity tag counts: approximate (per-doc review needed for execution)

**Tools used:**
- Claude `grep -rho`, `ls`, per-100-session-bucket loop for surfaces enumeration
- Rigby `repo_tool.search` × 10 for chunk-anchor citation-integrity spot-check (all 0 matches)
- Claude `grep -rho "\[docs/handoffs/SESSION_[^]]*\]"` for actual citation-pattern enumeration
- Claude `Grep` for `SESSION_1143_DOCS_AUDIT_AND_CLEANUP.md` section-heading verification (#8 resolves to "What changed in the corpus")

**T5 does NOT embed per-handoff matrix** — 1037 rows would be impractical. Aggregate counts + top-N + severity-tag proposal per session-range provide the substrate; per-doc classification is downstream-derivable.

---

**End of T5 — Handoffs + audits proliferation. T6 (`2706_docs_anchor_drift_audit.md`) opens next in the audit sequence.**
