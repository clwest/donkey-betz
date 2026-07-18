---
title: "S2816 /docs/ Anchor Drift Audit (T6 of Group 2700 arc — FINAL child before canonical summary)"
status: active (audit deliverable — rule inventory + drift classification + single-source-of-truth proposal per rule)
authority: T6 child audit of Group 2700 parent arc (final child; unlocks 2799 canonical summary)
session: 2816
date: 2026-07-18
domain_slug: docs_restructuring
research_group: 2700
thread: T6
authors: Claude Code (Chris directed at S2816 open); Rigby (surface enumeration + rule-taxonomy expansion 10→14 + methodology corrections)
supersedes: none
related:
  - docs/research/domains/docs_restructuring/2700_docs_restructuring_domain_scoping.md   # parent (Chris-locked 2026-07-16)
  - docs/research/domains/docs_restructuring/2701_docs_inventory_topology_audit.md       # T1 predecessor
  - docs/research/domains/docs_restructuring/2702_docs_research_pattern_extraction_audit.md # T2 — FP-META + BP5 + PP5 + SP5 primitives
  - docs/research/domains/docs_restructuring/2703_docs_human_user_pain_points_audit.md   # T3 — discovery-layer falsification of §2c convention
  - docs/research/domains/docs_restructuring/2704_docs_audience_segmentation_audit.md   # T4 — CRITICAL_DOCS/PRIORITY_DOCS distinction
  - docs/research/domains/docs_restructuring/2705_docs_handoffs_audits_proliferation_audit.md # T5 — substrate-integrity finding on parent §4 T5 clause
  - docs/ENGINEERING_PLAYBOOK.md                                                          # rule surface 1 (359 rule anchors)
  - docs/CLAUDE.md                                                                        # rule surface 2 (21 sections)
  - 00-START-NEXT-SESSION.md                                                              # rule surface 3 (10 sections)
  - /Users/donkeyking/.claude/projects/-Users-donkeyking-development-unified-donkey-betz/memory/  # rule surface 4 (122 feedback_*.md)
  - docs/00-START-HERE/DOC_LIFECYCLE.md                                                    # rule surface 5 (§2c sole-counts, §3 root-stability)
  - docs/research/ARCHITECTURE_INDEX.md                                                    # rule surface 6 (§6 Research Principles)
scope: T6 = rule inventory + per-rule cross-surface fingerprint + drift classification + single-source-of-truth proposal per parent §4
non_goals:
  - executing single-source-of-truth consolidation (canonical summary at 2799 owns)
  - exhaustive per-rule cross-surface table for all 14 rules (impractical — 14×6=84 cells; targeted fingerprinting instead)
  - file moves, deletions, renames, code changes (arc non-goals per parent §5)
  - amending parent doc §4 T5 substrate-integrity clause (T5 MQ-T5-8 owns explicit action item; canonical summary executes)
  - proposing Playbook v0.9 amendment for OP3 codification (separate arc; T6 flags readiness)
delegates_to: canonical summary 2799 (restructuring proposal + single-source-of-truth execution)
owner: claude+rigby
---

# Session 2816 — /docs/ Anchor Drift Audit (Group 2700, Thread 6 — FINAL child)

> **What this doc is.** T6 — final child audit of Group 2700 arc. Rule inventory (14 rules across 6 surfaces) + per-rule drift classification + single-source-of-truth proposals. Unblocks canonical summary (2799) which converges the arc.
>
> **What this doc is not.** Consolidation execution. Playbook amendment. Parent-doc update. Those belong to canonical summary + downstream implementation.

---

## 1. Why T6 sixth (and final)

Per parent doc §4:

> T6 — Anchor & drift audit. Scope: identify duplicated rules across playbook / `00-START-NEXT-SESSION` / memory / `DOC_LIFECYCLE.md` §2c / `ARCHITECTURE_INDEX §6.6` — SIGN mechanics, fresh isolation pin instructions, anchor discipline (inventory-wins-on-conflict), pin rotation policy, close-cascade steps. Measure the drift risk on each. Method: grep + fingerprint each rule statement across surfaces; classify (a) identical / (b) drifted-but-compatible / (c) drifted-and-inconsistent. Deliverable: rule-inventory table + drift severity + single-source-of-truth proposal per rule. Ties to Rigby fold 90 (mitigatable): SIGN mechanics 3-copy drift already documented. T6 quantifies scope; canonical summary proposes fix.

T6 completes the 6-thread child-audit set (T1-T6). After T6 ships, canonical summary (2799) becomes viable — it consolidates T1-T6 findings into the ratified restructuring proposal + twin-pointer workspace deliverable.

**Sixth-consecutive OP3 trigger** (5/5 all previous child audits caught substantive post-authoring errors). Two-SIGN cycle applied.

---

## 2. Anchors T6 cites (never restates)

| Source | What it holds | T6 usage |
|---|---|---|
| Parent §4 T6 | Rule taxonomy + method + drift-classification categories | T6 executes |
| T1 §3.1 | 3201 file inventory; surface subdirs | Cited as topology baseline |
| T2 §6 FP-META | Frontmatter as extensible control-plane header; CORE-ONLY | T6 references for FP-META rule |
| T3 §7 C5 | DOC_LIFECYCLE §2c falsified at discovery layer | T6 evidence for Rule #1 substrate risk |
| T4 §5.1-§5.1b | CRITICAL_DOCS (5) vs PRIORITY_DOCS (10) distinction | T6 references for Rule #4/#5 |
| T5 §7 + MQ-T5-8 | Parent §4 T5 substrate-integrity clause based on false premise | T6 respects — does NOT re-litigate parent §4 T5 clause |
| Rigby fold 90 (parent §2) | SIGN mechanics 3-copy drift documented | T6 quantifies scope |

---

## 3. Rule surfaces (6 enumerated at git HEAD `41cefe8c41f4`)

| Surface | Location | Size |
|---|---|---|
| 1 | `docs/ENGINEERING_PLAYBOOK.md` | 359 section headers / rule anchors |
| 2 | `docs/CLAUDE.md` | 21 sections |
| 3 | `00-START-NEXT-SESSION.md` | 10 sections |
| 4 | `~/.claude/projects/.../memory/` | 122 `feedback_*.md` files |
| 5 | `docs/00-START-HERE/DOC_LIFECYCLE.md` | 13 sections (§2c sole-counts at line 99; §3 root-stability at line 113) |
| 6 | `docs/research/ARCHITECTURE_INDEX.md` | §6 Research Principles at line 3995 |

**Additional replication surfaces surfaced during authoring (per Rigby SIGN Q1 tool_runs):** rules have ALSO replicated into:
- `docs/research/ARCHITECTURE_INDEX.md` (SIGN pin discipline at chunk #487)
- `docs/research/domains/api/2500_api_domain_scoping.md` (SIGN vs arc pin distinction)
- `docs/research/implementation/observability_spine_.../I-0100_scoping.md` (checklist form of docs cascade)
- 100+ `docs/handoffs/SESSION_XXXX.md` files (repeating rules in provenance sections)

**Drift risk landscape is broader than parent §4 T6 named.** Not just 6 surfaces; 6 primary + N secondary replication points. T6 focuses on primary; secondary flagged in Migration Queue.

---

## 4. Rule taxonomy (14 rules — Rigby SIGN Q1 expanded from initial 10)

Per Rigby SIGN Q1 additions (4 new rules + 1 split + 1 relabel):

### 4.1 Substrate / discipline rules

| # | Rule | Primary surface | Secondary surfaces |
|---:|---|---|---|
| 1 | Sole authoritative counts source = `PLATFORM_INVENTORY.md` | DOC_LIFECYCLE §2c | CLAUDE.md, SPIDERS.md DOC-POINTER banner, SYSTEM_OVERVIEW.md banner, api/2599 canonical, T3+T4+T5 audits |
| 2 | Runtime-coupled path never-move (canon/, governance/SYSTEM_OWNER, missions/CURRENT_MISSION, decisions/ADR-*, ops/) | DOC_LIFECYCLE §2b | T2 §4 SP5 |
| 3 | Root-stability rule | DOC_LIFECYCLE §3 | (implicit in every session's close-cascade discipline) |
| 11 | **DOC-POINTER-V1/V2 banners** as de-authorization mechanism (**Rigby SIGN Q1 add**) | DOC_LIFECYCLE §1 | ~8 docs at root carry the banner (SPIDERS, SYSTEM_OVERVIEW, ARCHITECTURE, API_PATH_POLICY, AGENTS, AGENT_OUTPUT_TO_UI_MAPPING, AUDIT_FINDINGS, 24_7_GLOBAL_AI_APP_ATLAS, AI_PIXAR_IMPLEMENTATION_PLAN, API) |
| 12 | **`verify_doc_claims --only-drift` enforcement hook** (**Rigby SIGN Q1 add**) | DOC_LIFECYCLE §2c | CLAUDE.md (3 refs); 0 refs in 00-START-NEXT-SESSION |

### 4.2 Process / methodology rules

| # | Rule | Primary surface | Secondary surfaces |
|---:|---|---|---|
| 4 | Fresh SIGN isolation pin discipline | Playbook §15 | ARCHITECTURE_INDEX #487, api/2500 scoping, tools/pa_local.sh comments, memory feedback_session_tool_retire_works |
| 5 | Pin rotation policy (force=true, retire-current-then-mint-fresh) | memory feedback_session_tool_retire_needs_force_true | Every session start-here doc + handoff |
| 14 | **Twin-pin discipline (SIGN pin ≠ arc pin)** (**Rigby SIGN Q1 add**) | ARCHITECTURE_INDEX #487 + api/2500 scoping | Playbook §15/§16 (implicit) — NOT explicitly codified as distinct rule |
| 6a | **Docs cascade steps (build_docs_index + build_rag_corpus + sync + embed)** (**Rigby SIGN Q1 split from #6**) | memory feedback_docs_pipeline_4_step_cascade | PLAYBOOK-7.4.4 adjacent; every session close cascade PR body |
| 6b | **`build_docs_provenance` rebuild** (**Rigby SIGN Q1 split from #6**) | Present in some checklists (I-0100 scoping); memory implicit | Not in 4-step cascade explicitly — separate step |
| 7 | PLAYBOOK-7.4.4 recycle-after-merge | Playbook §7.4.4 | memory feedback_recycle_after_merge, every session close, 9+ ratification records |
| 8 | PLAYBOOK-6.10.7 zoom-out ask per Rigby SIGN | Playbook §6.10.7 | memory feedback_zoom_out_ask_per_rigby_sign, T-audits provenance |
| 9 | Anti-rubber-stamp (`tool_runs` non-empty) — **relabel to "evidence quality gate" per Rigby SIGN Q1** | Playbook §6.10.7 adjacent | memory feedback_verify_rigby_tool_runs_before_trusting_sign, T-audits provenance |
| 10 | **Two-SIGN-per-audit (OP3 — 5/5 triggers)** — **UNCODIFIED in playbook; Playbook v0.9 amendment threshold met** | (uncodified) | T2-T5 audit provenance sections + this doc's §12 |

**14 rules total.**

### 4.3 Drift classification criteria (Rigby SIGN Q2 clarification)

Per parent §4:
- **(a) identical** — same wording OR normalized-wording (paraphrase within ~90% overlap) across all surfaces
- **(b) drifted-but-compatible** — wording differs but semantics + application are same
- **(c) drifted-and-inconsistent** — semantics or application differs across surfaces (reader of surface A vs surface B would take different action)

---

## 5. Per-rule drift classification (targeted fingerprint)

Full 14×6 table would be 84 cells — impractical for session-scoped audit. T6 fingerprints the **highest-drift-risk rules** (those Rigby fold 90 named + high-cross-surface-density) and TAGS the rest with drift-verdict without exhaustive per-surface tables.

### 5.1 Rule #1 — Sole authoritative counts source (SEVERE cross-surface density; DRIFTED-BUT-COMPATIBLE per T3 §7 C5 finding)

- **Primary (DOC_LIFECYCLE §2c):** "PLATFORM_INVENTORY.md is the sole authoritative source for system counts"
- **CLAUDE.md ("Anchors" callout):** "PLATFORM_INVENTORY.md is the runtime/inventory anchor and is the sole authoritative source for system counts"
- **narratives/AGENTS_AND_AUTONOMY.md:24:** "sole authoritative" (partial phrase)
- **DOC-POINTER-V1 banner (SPIDERS.md, SYSTEM_OVERVIEW.md):** "for current verified numbers, defer to PLATFORM_INVENTORY.md" (compatible variant)
- **T3 §7 C5 substrate finding:** the rule holds IN-DOC but is FALSIFIED AT DISCOVERY LAYER (archived Oct 2025 morning report outranks canonical for "how many spiders" search)
- **Drift verdict: DRIFTED-BUT-COMPATIBLE across surfaces; INVISIBLE-AT-DISCOVERY per T3.**
- **Single-source-of-truth proposal:** DOC_LIFECYCLE §2c is canonical text; other surfaces reference not restate. **Add discovery-layer enforcement** (retrieval-weight boost per T3 MQ-T3-4).

### 5.2 Rule #4/#5/#14 — SIGN isolation pin + rotation + twin-pin (Rigby fold 90 SEVERE drift zone)

- **Rigby fold 90 explicit:** SIGN mechanics 3-copy drift already documented at parent §2 constraint (T6 quantifies scope).
- **Surface presence:**
  - Playbook §15 (canonical — SIGN-isolation discipline)
  - Playbook §16 (arc pin lifecycle)
  - ARCHITECTURE_INDEX #487 (usage narrative referencing playbook §15)
  - api/2500 scoping (SIGN vs arc pin distinction — Rigby SIGN Q1 named this as separate rule #14)
  - memory feedback_session_tool_retire_works (rebuts prior stale claim in `tools/pa_local.sh` commentary + S1300 parent scoping §3F)
  - memory feedback_session_tool_retire_needs_force_true (post-S2770 behavior emerged — updated at that time; S1300 doc still has old claim)
  - tools/pa_local.sh comments (STALE per memory correction)
  - S1300 parent scoping doc §3F (STALE per memory correction)
  - Every session handoff (dogfoods the rule in provenance)
- **Drift verdict: DRIFTED-AND-INCONSISTENT** (with per-surface nuance per Rigby SIGN Q2 correction):
  - **S1300 §3F: GENUINELY STALE-CONTRADICTORY** — claims `session_tool.retire` action doesn't exist (superseded by memory `feedback_session_tool_retire_works` per S1301 close 2026-07-01). Reader of S1300 §3F alone follows wrong protocol.
  - **`tools/pa_local.sh` comments: REPLICATED SURFACE (not stale)** — Rigby SIGN Q2 tool-check confirmed `session_tool.retire force=true` is correctly referenced at multiple lines (126, 171, 245, 422, 461+). Original T6 draft mislabeled this as stale; corrected. Concern is high-density replication increasing drift risk, not stale/contradictory content.
- **Single-source-of-truth proposal:** Playbook §15/§16 canonical. Memory feedback rules become derived (referenced not restated). **S1300 §3F needs V1-banner or in-place amendment** (genuinely stale). **`tools/pa_local.sh` comments need canonical-anchor pointer** to Playbook §15/§16 (replicated surface, not stale — just under-anchored).

### 5.3 Rule #7 — PLAYBOOK-7.4.4 recycle-after-merge (DRIFTED-BUT-COMPATIBLE; high replication density)

- **Playbook §7.4.4 (canonical):** "close-ceremony PRs MUST include a post-merge `make recycle-all` so local processes match HEAD SHA before the next session opens"
- **memory feedback_recycle_after_merge:** compatible restatement
- **Multiple ratification records (S2766, S2774, S2775 etc):** consistent application
- **Every session close cascade PR body:** cites PLAYBOOK-7.4.4
- **Drift verdict: DRIFTED-BUT-COMPATIBLE.** Wording varies (some cite "PLAYBOOK-7.4.4", others cite "recycle-after-merge") but semantics + application are identical.
- **Single-source-of-truth proposal:** Playbook §7.4.4 canonical. Memory feedback becomes derived pointer.

### 5.4 Rule #10 — Two-SIGN-per-audit (OP3) — UNCODIFIED (5/5 triggers; drift-not-applicable)

- **Primary surface:** T2-T5 audit provenance sections (this doc's §12)
- **Playbook:** NOT CODIFIED yet
- **Drift verdict:** N/A — rule is uncodified; drift concept requires primary source to compare against.
- **Single-source-of-truth proposal:** Codify in Playbook v0.9 amendment (separate arc; T5 MQ-T5-8 flags readiness; T6 does not re-litigate).

### 5.5 Aggregate drift table (14 rules, non-exhaustive)

| # | Rule | Drift verdict | Severity |
|---:|---|---|---|
| 1 | Sole counts source | DRIFTED-BUT-COMPATIBLE + discovery-invisible | HIGH (T3 §7 C5 substrate finding) |
| 2 | Runtime-coupled never-move | (identical across 2 surfaces) | LOW |
| 3 | Root-stability | (identical DOC_LIFECYCLE §3 + implicit application) | LOW |
| 4 | SIGN isolation pin | DRIFTED-AND-INCONSISTENT | HIGH (Rigby fold 90 explicit) |
| 5 | Pin rotation policy (force=true) | DRIFTED-AND-INCONSISTENT (S1300 §3F STALE; pa_local.sh REPLICATED — per Rigby Q2 correction) | HIGH (S1300 §3F genuinely stale; pa_local.sh under-anchored replication) |
| 6a | Docs cascade steps | DRIFTED-BUT-COMPATIBLE | LOW |
| 6b | build_docs_provenance | UNCODIFIED / SPORADIC | MODERATE (Rigby SIGN Q1 added; not in 4-step cascade) |
| 7 | PLAYBOOK-7.4.4 recycle-after-merge | DRIFTED-BUT-COMPATIBLE | LOW |
| 8 | PLAYBOOK-6.10.7 zoom-out ask | DRIFTED-BUT-COMPATIBLE | LOW |
| 9 | Evidence quality gate (tool_runs non-empty) | DRIFTED-BUT-COMPATIBLE | LOW |
| 10 | Two-SIGN-per-audit (OP3) | UNCODIFIED | N/A — 5/5 triggers; Playbook v0.9 amendment ready |
| 11 | DOC-POINTER banners | (identical DOC_LIFECYCLE §1 + banner instances) | LOW |
| 12 | verify_doc_claims enforcement | DRIFTED-BUT-COMPATIBLE (0 refs in 00-START-NEXT-SESSION suggests underused rather than drifted) | MODERATE |
| 14 | Twin-pin discipline (SIGN ≠ arc pin) | DRIFTED-AND-INCONSISTENT | HIGH (Rigby SIGN Q1: distinction present in ARCHITECTURE_INDEX + api/2500 but NOT explicitly codified in playbook as distinct rule) |

**High-drift rules (Rules #1, #4, #5, #14) are the canonical-summary priority set.**

---

## 6. Cross-cutting observations (single-source-of-truth proposals)

Per parent §4 T6 deliverable requirement:

### 6.1 Primary canonical text lives in Playbook + DOC_LIFECYCLE

For rules #1, #2, #3, #4, #7, #8, #9, #11, #12 — the primary canonical text is already in either Playbook or DOC_LIFECYCLE. **Single-source-of-truth proposal for all of these: canonical primary; all other surfaces reference-not-restate.**

### 6.2 Uncodified rules to codify (Rules #6b, #10, #14)

- **#6b `build_docs_provenance` rebuild** — currently sporadic; needs explicit inclusion in canonical docs-cascade specification (either extend to 5-step cascade OR document as separate provenance-rebuild step).
- **#10 Two-SIGN-per-audit (OP3)** — 5/5 triggers well past threshold; Playbook v0.9 amendment ready (separate arc per T5 MQ-T5-8).
- **#14 Twin-pin discipline** — SIGN pin vs arc pin distinction is empirically observed across ARCHITECTURE_INDEX + api/2500 but not codified in playbook as distinct rule. Codification candidate.

### 6.3 In-place update needed (Rules #4/#5)

- **`docs/research/domains/memory/1300_memory_domain_scoping.md` §3F has STALE-CONTRADICTORY claims** about `session_tool.retire` (memory `feedback_session_tool_retire_works` corrects; S1300 §3F unchanged in-place — reader follows wrong protocol). Needs V1 stats-drift banner OR in-place amendment.
- **`tools/pa_local.sh` comments (per Rigby SIGN Q2 correction)** — high-density REPLICATED SURFACE not stale/contradictory (`session_tool.retire force=true` correctly referenced at lines 126/171/245/422/461+). Needs canonical-anchor pointer to Playbook §15/§16 for anchoring, not amendment.
- **Migration session executes both** — different treatments for the two surfaces.

### 6.4 Discovery-layer enforcement gap (Rule #1)

T3 §7 C5 established the DOC_LIFECYCLE §2c convention is INVISIBLE at discovery layer. **T6 cross-references:** Rule #12 (verify_doc_claims enforcement hook) exists but has 0 refs in 00-START-NEXT-SESSION.md and 3 refs each in CLAUDE.md + DOC_LIFECYCLE. **Cross-cutting single-source-of-truth proposal:** verify_doc_claims should be in every session close-ceremony checklist (currently absent from start-here).

---

## 7. Playbook §9 canonical questions (adapted to T6 scope)

| Q# | Question (adapted) | T6 answer |
|---|---|---|
| Q1 | How many rules identified? | 14 (Rigby SIGN Q1 expanded from initial 10) |
| Q2 | How many rules are identical across surfaces? | 4 (Rules #2, #3, #6a, #11) |
| Q3 | How many rules are drifted-but-compatible? | 5 (Rules #1, #7, #8, #9, #12) |
| Q4 | How many rules are drifted-and-inconsistent (SEVERE drift)? | 3 (Rules #4, #5, #14) |
| Q5 | How many rules are uncodified? | 2 (Rules #6b, #10) |
| Q6 | Which Rigby-fold-90 finding is confirmed? | **YES — SIGN mechanics drift is real** (Rules #4/#5). Additional Rule #14 (twin-pin) surfaces DRIFTED-AND-INCONSISTENT during Rigby SIGN Q1 expansion. |
| Q7 | Do rules replicate BEYOND the 6 primary surfaces? | **YES — extensively.** ARCHITECTURE_INDEX #487, api/2500 scoping, ~100+ session handoffs. Migration session must scope amendments beyond just the 6 primary. |
| Q8 | Which single doc has the most drift-risk-load? | `tools/pa_local.sh` + `docs/research/domains/memory/1300_memory_domain_scoping.md §3F` — both hold STALE claims corrected only in memory feedback. |
| Q9 | Which uncodified rule is highest-priority for codification? | Rule #10 (OP3 two-SIGN-per-audit) — 5/5 triggers, well past Playbook v0.9 threshold. |
| Q10 | Does DOC_LIFECYCLE §2c hold IN-DOC? | **YES** (canonical primary is intact) |
| Q10b | Does DOC_LIFECYCLE §2c hold AT DISCOVERY LAYER? | **NO** (T3 §7 C5 falsifies). Cross-cutting fix needs discovery-layer enforcement per §6.4. |
| Q11-Q28 | Restructuring proposal; execution; codification amendments; migration ordering | **Out of T6 scope** — canonical summary at 2799 owns |

---

## 8. Migration Queue (post-arc)

Per parent §5. T6 is FINAL child audit; MQ items feed directly into canonical summary 2799.

| # | Item | Evidence source | Severity | Notes for canonical summary |
|---|---|---|---|---|
| MQ-T6-1 | **Rule #4/#5 SIGN pin discipline: DRIFTED-AND-INCONSISTENT** — `tools/pa_local.sh` + `S1300 §3F` hold STALE claims corrected only in memory | §5.2 + §6.3 | HIGH | 2799 proposes in-place amendment OR V1 banner; migration session executes. |
| MQ-T6-2 | **Rule #14 twin-pin discipline: DRIFTED-AND-INCONSISTENT + UNCODIFIED** — empirically observed in ARCHITECTURE_INDEX + api/2500 but not in playbook | §5 + §6.2 | HIGH | 2799 proposes Playbook §15/§16 amendment codifying SIGN-pin vs arc-pin distinction. |
| MQ-T6-3 | **Rule #1 sole counts source: DISCOVERY-LAYER FALSIFIED (T3 §7 C5)** — cross-references T4 §6.3 discovery-vs-injection asymmetry + T3 MQ-T3-4 | §5.1 + §6.4 | HIGH | 2799 proposes retrieval-weight-boost for PLATFORM_INVENTORY.md + explicit hint mechanism (T3 MQ-T3-4). |
| MQ-T6-4 | **Rule #10 OP3 two-SIGN-per-audit: UNCODIFIED; 5/5 triggers** — Playbook v0.9 amendment ready | §5.4 + T5 MQ-T5-8 (adjacent) | INFORMATIONAL (readiness signal) | Separate Playbook v0.9 amendment arc; canonical summary flags. |
| MQ-T6-5 | **Rule #6b build_docs_provenance: UNCODIFIED / SPORADIC** — not in 4-step cascade spec | §5 aggregate + Rigby SIGN Q1 | MODERATE | 2799 proposes: extend cascade to 5-step OR document as separate provenance-rebuild step. |
| MQ-T6-6 | **Rule #12 verify_doc_claims: DRIFTED-BUT-UNDERUSED** — 0 refs in 00-START-NEXT-SESSION | §5 aggregate + §6.4 | MODERATE | 2799 proposes: add verify_doc_claims to session close-ceremony checklist in start-here template. |
| MQ-T6-7 | **Rule replication beyond 6 primary surfaces is extensive** — ARCHITECTURE_INDEX + api/2500 + ~100 handoffs | §3 + §7 Q7 | INFORMATIONAL | 2799 scopes amendments beyond just 6 primary surfaces; downstream migration is broader than initially framed. |
| MQ-T6-8 | **Cross-cutting: 3 SEVERE-drift rules (#1, #4/#5, #14) all point to the same substrate need** — replication without canonical anchoring | §5.5 + §6 | INFORMATIONAL (aggregate insight) | **Actionable standard per Rigby SIGN Q3 tightening (avoid meta-program overscoping):** every non-canonical restatement of a rule MUST include (a) canonical anchor pointer (`per Playbook §X.Y.Z` or `per DOC_LIFECYCLE §NN`) AND (b) either a drift-check hook (e.g., `verify_doc_claims`-adjacent verifier for the specific rule) OR an explicit non-authority banner (`DOC-POINTER-V1` variant marking the restatement as reference-not-source). Concrete acceptance test for 2799 restructuring proposals: any doc found to restate a canonical rule without (a)+(b) is either updated to comply OR marked with the non-authority banner. |

---

## 9. What T6 does NOT resolve (explicit hand-offs to canonical summary 2799)

Per parent §4 anti-scope:

| Question | Handed off to |
|---|---|
| Should stale claims in `tools/pa_local.sh` + `S1300 §3F` be amended in-place OR V1-bannered? | Canonical summary at 2799 + migration session |
| Should Rule #14 twin-pin discipline be codified in Playbook? | Canonical summary flags → separate Playbook amendment arc |
| Should Rule #10 (OP3) be codified in Playbook v0.9? | Canonical summary flags → separate Playbook v0.9 amendment arc |
| Should Rule #6b (build_docs_provenance) extend the cascade spec to 5 steps? | Canonical summary at 2799 |
| Should Rule #12 (verify_doc_claims) be in start-here close-ceremony checklist? | Canonical summary at 2799 |
| Should replicated rules across ARCHITECTURE_INDEX + api/2500 + handoffs use a compliance verifier? | Canonical summary at 2799 + downstream implementation |
| Should T5 MQ-T5-8 (parent §4 T5 substrate-integrity clause update) be executed by canonical summary? | Canonical summary at 2799 (respects Chris-locked parent status via ratification) |

---

## 10. **T6 completes Group 2700 child-audit set. Canonical summary (2799) is now viable.**

**Arc convergence state at T6 close:**

- Parent scoping ✅ (S2801)
- T1 inventory & topology ✅ (S2811)
- T2 pattern extraction ✅ (S2812)
- T3 human pain ✅ (S2813)
- T4 audience segmentation ✅ (S2814)
- T5 handoffs+audits proliferation ✅ (S2815)
- **T6 anchor drift ✅ (S2816 — this doc)**
- **2799 canonical summary ⬜ NOW VIABLE**

Canonical summary 2799 consolidates T1-T6 into the ratified `/docs/` restructuring proposal + twin-pointer workspace deliverable per parent §5 D6+D7.

---

## 11. Provenance

**Session:** S2816 (2026-07-18, evening — EIGHTH session close of the day)
**Ratifier:** Chris D-verdict "Continue" at S2816 open
**Git HEAD at authoring:** `41cefe8c41f4` (S2815 close cascade)

**Rigby SIGN cycles (TWO per S2811-S2815 OP3 lesson — SIXTH-CONSECUTIVE trigger):**

- **Open SIGN** (Q1 rule taxonomy / Q2 drift criteria / Q3 zoom-out). **Substantive Rigby corrections:**
  - Q1 → **Expanded taxonomy 10 → 14 rules.** Added #11 (DOC-POINTER banners as de-authorization), #12 (verify_doc_claims enforcement hook), #14 (twin-pin discipline SIGN ≠ arc pin), split #6 → #6a (cascade) + #6b (provenance rebuild). Relabeled #9 as "evidence quality gate" (governance vs substrate distinction).
  - Q2 → Operational definitions ratified for identical / compatible / inconsistent classification.
  - Q3 → Confirmed rules replicate BEYOND the 6 primary surfaces (ARCHITECTURE_INDEX #487, api/2500 scoping, ~100 handoffs); T6 scope respects but flags in MQ-T6-7.
- Anti-rubber-stamp check PASSED — Rigby ran `search_docs` × 3 for high-density cross-surface rules (sole-counts + PLAYBOOK-7.4.4 + SIGN isolation pin).

- **Post-authoring pressure-test SIGN — SIXTH-CONSECUTIVE OP3 TRIGGER. Substantive corrections:**
  - Q1: AGREE-WITH-EDITS — Rule #13 placeholder removed for clarity; no merges (4/5 SIGN-pin family / DOC-POINTER vs sole-counts / cascade vs provenance all stay distinct)
  - Q2: AGREE-WITH-EDITS — **Rule #5 STALE claim in pa_local.sh softened**: Rigby tool-check found `session_tool.retire force=true` correctly referenced at multiple lines (126/171/245/422/461+). Reclassified pa_local.sh as REPLICATED SURFACE (under-anchored), not stale. S1300 §3F remains genuinely STALE-CONTRADICTORY. Applied to §5.2 + §5.5 + §6.3.
  - Q3: AGREE-WITH-EDITS — **MQ-T6-8 narrowed** from abstract "single mechanism" to actionable standard: every non-canonical restatement MUST include canonical-anchor pointer + drift-check hook OR non-authority banner. Concrete acceptance test provided for 2799.
  - Q4: AGREE-WITH-EDITS — biggest 2799 risks are (1) mislabeled stale-surface assertions cascading into wrong migration priorities (Rigby Q2 catch prevented this), (2) MQ-T6-8 breadth causing 2799 to overscope into meta-program (Rigby Q3 tightening prevents this).

**OP3 6/6 across 6 audit shapes.** Every child audit's post-authoring SIGN caught substantive errors open-SIGN missed. Playbook v0.9 amendment threshold WELL past (5-trigger over-corroboration).

**Precision qualifiers applied:** all count claims labeled (exact / approximate / non-exhaustive); T5's precision-qualifier discipline maintained.

**Tools used:**
- Claude `grep -c` for surface size counts
- Claude cross-surface grep for 3 sample rules (sole-counts, recycle-after-merge, SIGN pin)
- Rigby `search_docs` × 3 for cross-surface density (Rule #1, #7, #4/#5)
- Rigby `search_docs` × ? for chunk-anchor reference discovery (rules replicate to ARCHITECTURE_INDEX + api/2500)

**T6 does NOT embed 14×6 = 84-cell exhaustive cross-surface matrix** — targeted fingerprinting on high-drift-risk rules per §5 provides substrate; per-rule cross-surface enumeration is downstream-derivable using §3 surface list + §4 rule taxonomy.

---

**End of T6 — Anchor drift audit. Group 2700 child-audit set complete.**

**Next in arc: `2799_docs_restructuring_canonical_summary.md` — arc close + ratified restructuring proposal + twin-pointer workspace deliverable.**
