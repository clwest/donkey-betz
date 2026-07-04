---
title: "Group 1900 P4 Cat F — Adjacent / Separation Boundaries consolidation child audit (seam audit across 8 adjacent planes: Memory 1300 + Content 1600 + Sports 1500 + HAI 1800 + Employee OS + Frontend + API + Discord)"
session: 1904
child_slot: P4_cat_f
domain_slug: authority_enforcement
research_group: 1900
category: child_audit_consolidation
authority: research-consolidation for Category F per parent §5.4 D85 sequence + FOURTH AND LAST child under Group 1900; consumes P1 §7 propagation contract + P2 §17 Enforcement Binding Points map + P3 §17.1 Plane Precedence Policy + P3 §14.1 KillSwitch classification correction; produces separation-boundary posture register + propagation-contract touchpoint register for xx99 §5 consolidated domain shape + xx99 §8 follow-on queue input
head_commit: c902e003
status: draft
date: 2026-07-04
last_verified: 2026-07-04
authors: Claude Code (Chris directed via short command "start research group 1904" at S1904 open per Research OS §5 request-classification RESEARCH class §8.1 startup contract; interpretation: Chris continuing Group 1900 arc into child slot P4 per O1 sequential execution operational default recorded at S1900 close + parent §5.4 CONSOLIDATION shape + S1806 Group 1800 Cat F precedent; Rigby confirmed service_context: local on arc pin pa-2bd1613ce2bd4a9c via platform_config_tool overview at session open)
prior_children:
  - 1901_authority_enforcement_cat_a_actor_role_propagation_design.md (S1901 P1 Cat A — LAYER i three-role schema + LAYER ii 20-boundary propagation-contract table + F6a/F6b/F6c/F6c-adjacent structural drops)
  - 1902_authority_enforcement_cat_b_authority_enforcement_design_decision.md (S1902 P2 Cat B — 8 Chris-D-gate-ratified D-verdicts D86–D93 + §17 Enforcement Binding Points 20-boundary map)
  - 1903_authority_enforcement_cat_c_cross_plane_composition_design.md (S1903 P3 Cat C — 8 Q composition resolutions Q1–Q8 + §17.1 Plane Precedence Policy + §7.4.1 D94 KillSwitch Enforcement Reader Design + §14.1 KillSwitch classification correction)
parent: 1900_authority_enforcement_domain_scoping.md
delegates_to:
  - xx99 S1999 canonical summary — consumes this doc's §17 separation-boundary posture register + §7 per-plane propagation-contract touchpoint traces + §19 R-slot follow-on queue candidates
related_arcs:
  - 1300 Memory (AgentLearning + UserAgentLearning writer plane; Cat F.a Memory seam)
  - 1500 Sports (BettingOutcomeVerifier + SportsBettingLearningBridge; Cat F.c Sports seam)
  - 1600 Content (Content deliberation pipeline + PublishGate + ClaimsPack; Cat F.b Content seam)
  - 1800 HAI (HumanAttentionItem + HumanFeedbackRecord + HumanPreference + auto-approve gate; Cat F.d HAI seam)
  - 2000 Event Architecture (deferred; F.SYMBOL-MAPPING-STATUS-VERIFICATION + F.PER-USER-AUTHORITY-MECHANISM inheritors per S1903 §19)
playbook_application: §11.2 20-section child template FOURTEENTH-consecutive application + §16 CONSOLIDATION shape from S1806 Group 1800 Cat F precedent (SECOND-consecutive CONSOLIDATION application under Research OS)
verifier_loop: §14 verifier-loop REQUIRED CODIFICATION-CONFIRMED (S1899 §10.2 MC-1 promoted) — pre-Explore verifier CONFIRMED all 8 adjacent-plane entry-point classes exist at HEAD (Memory: signal_aggregation_service.py + agent_learning writer plane; Content: content_deliberation_runner.py + publish_gate.py; Sports: betting_outcome_verifier.py + sports_betting_learning_bridge.py; HAI: human_attention_lifecycle.py + views_human_interface.py; Employee OS: mission_runner.py + jobs.py; Frontend: App.tsx + ProtectedRoute; API: 209 views_*.py; Discord: discord_bot.py 96 commands); post-Explore verifier CORRECTED 3 drifts: (1) Explore 4 HAI `review_mode` line drift `:240` → verified at `:243` per `core/services/human_attention_lifecycle.py:243`; (2) Explore 4 Memory seam CONFIRMED PERMEABLE-BROKEN via new evidence — signal_aggregation_service.py:211 makes explicit `GovernanceState.objects.filter(scope='global').first()` read (not entirely implicit as Explore 4 stated); (3) Explore 2 "enforce_authority_mode field NOT IMPLEMENTED" flagged SPECULATIVE at Explore-time — post-Explore verifier CONFIRMED via `grep -rn "enforce_authority_mode" core/employees/` returned ZERO matches → P2 D91 landed as DESIGN ONLY; runtime implementation is post-arc T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS pending (no drift in P2 design; drift is design-vs-runtime gap explicitly queued)
sign_status: LANDED — Chris ratified all F1-F12 findings + §17.1 per-plane separation-boundary posture register + §19 20-item T-tier queue via "agree all" shortcut 2026-07-04 post-Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence on arc pin pa-2bd1613ce2bd4a9c per S1801-S1806 arc-pin routing precedent (durable-by-seventh-application under Group 1900 as fourth child slot; FOURTH-consecutive Chris "agree all" application within Group 1900 arc: S1902 D-gate + S1903 Q-resolutions + S1903 SIGN cycle 1 folds + S1904 all-findings-ratification); 6 folds landed pre-commit: (Q1a) Memory F1 framing tightening — signal/aggregation surface reading Autonomy/Governance state directly, not memory subsystem correctness; classify under Memory only insofar as signal_aggregation_service is part of the "stateful persistence/aggregation" plane in Group 1300; (Q1b) T3 tier hygiene rule codified — undocumented cross-plane reads that CAN change enforcement semantics → T2; reads that only throttle background work → T3; R.MEMORY.SIGNAL-AGG-AUTHORITY-COUPLING-DOC stays T3 (throttle-only classification); (Q2) F5 non-accusatory scheduling phrasing — "Confirmed absent at HEAD; expected per staged rollout; tracked as T1/T2 execution items, not a contradiction of the P2/P3 ratified design"; (Q3a) Sports STRUCTURAL-DROP parenthetical — "excluded from cross-plane composition pending prerequisites; not a statement about correctness"; (Q3b) Frontend CLEAN verification note — no mutation endpoints or UI controls observed for authority/governance fields; if any UI can toggle these, Frontend becomes PERMEABLE-BROKEN until explicit write-boundary contract exists; (Q4c) CROSS-PLANE-FAIL-OPEN-CODIFICATION wording tighten — "implement codification per S1902 D89/F8 precedent + exceptions register" not "decide policy" (Chris-gated policy remains separate decision if new defaults introduced); D48 36th arm turn 1 CLEAN; 31-consecutive-fully-clean-arms sub-pattern EXTENDED per single-batch 4-question criterion (MC-2 CODIFICATION-CONFIRMED milestone extended 30 → 31 consecutive); SIGN cycle 2 SKIPPED as unnecessary per Rigby explicit statement
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/domains/authority_enforcement/1900_authority_enforcement_domain_scoping.md
  - docs/research/domains/authority_enforcement/1901_authority_enforcement_cat_a_actor_role_propagation_design.md
  - docs/research/domains/authority_enforcement/1902_authority_enforcement_cat_b_authority_enforcement_design_decision.md
  - docs/research/domains/authority_enforcement/1903_authority_enforcement_cat_c_cross_plane_composition_design.md
  - docs/research/platform_architecture_inventory.md
  - docs/research/platform/cross_domain_integration_audit.md
owner: claude
---

# Group 1900 P4 Cat F — Adjacent / Separation Boundaries (Consolidation Child Audit)

> **FOURTH AND LAST child audit under Group 1900 Authority
> Enforcement Design Space arc.** Playbook §11.2 20-section child
> audit template FOURTEENTH-consecutive application + §16
> CONSOLIDATION shape SECOND-consecutive application under the
> Research OS (first at S1806 Group 1800 Cat F).
>
> **Scope precision (per Rigby S1900 SIGN cycle 1 Q3(b) fold —
> normative for this doc).** P4 is a **separation-boundary posture
> audit (interface + seam audit)** — a review of interfaces, seams,
> propagation drop points, enforcement read-sites, and precedence
> joins between Authority Enforcement and each adjacent domain. It
> is **NOT** an audit of each adjacent domain's internal correctness
> or implementation quality. Prior arc audits own their respective
> internal-correctness verdicts:
>
> | Adjacent plane | Group | Internal-correctness owner |
> |---|---|---|
> | Memory | 1300 | S1301-S1305 + S1399 xx99 |
> | Sports | 1500 | S1501-S1506 + S1599 xx99 |
> | Content | 1600 | S1601-S1606 + S1699 xx99 |
> | HAI | 1800 | S1801-S1806 + S1899 xx99 |
> | Employee OS | — | Distributed (S1272 §5 + EMPLOYEE_OS_PRIMITIVES.md) |
> | Frontend | — | Distributed (docs/topics/frontend.md + workspace research) |
> | API | — | Distributed (docs/API_PATH_POLICY.md + views_* research) |
> | Discord | — | Distributed (docs/DISCORD_INTEGRATION.md + Cog audit) |
>
> Group 1900 P4 audits **only the seams** between authority and
> those domains. Any finding that lands entirely inside an adjacent
> domain (e.g., "Memory's caching invalidation is stale") is OUT OF
> SCOPE and gets routed to the owning arc's post-arc T-slot.

## 1. Executive Summary

Cat F is the CONSOLIDATION surface for Group 1900. P4 audits the seams between Authority Enforcement and 8 adjacent planes; per parent §5.4 + playbook §14.5 no-implementation rule, Cat F catalogs seam posture and produces R-slot follow-on queue candidates. Post-arc T-slot inherits.

At HEAD `c902e003`, all 8 adjacent-plane entry-point classes verified at pre-Explore. Six parallel Explore sub-agents returned per playbook §13. Post-Explore verifier caught 3 corrections (see §14.3): HAI `review_mode` line drift `:240` → `:243`; Memory signal-aggregation coupling elevated implicit → explicit at `signal_aggregation_service.py:211`; Explore 2 SPECULATIVE `enforce_authority_mode` field absence CONFIRMED via direct grep.

**Headline verdicts:**

- **F1 (HIGH structural — Cat F.a Memory) — Memory seam is PERMEABLE-BROKEN via signal-aggregation implicit read + structural drops at Boundary 6/7/9.** `core/services/signal_aggregation_service.py:211` reads `GovernanceState.objects.filter(scope='global').first()` — a real cross-plane read from Memory's signal-aggregation pipeline INTO the Autonomy plane. **This is not "memory subsystem correctness"; it is a *signal/aggregation surface* reading Autonomy/Governance state directly. We classify it under Memory only insofar as this service is part of the "stateful persistence/aggregation" plane in Group 1300 (Rigby SIGN cycle 1 Q1 fold — the strict Memory-subsystem-proper interpretation would put this in a Signal/Intelligence ↔ Governance/Autonomy seam column instead).** This is documented nowhere in Group 1300 topic docs or S1399 xx99 §7. Additionally, Memory's canonical writer plane (`AgentLearning` + `UserAgentLearning`) inherits actor-role only via Step.fn closure at Boundary 6/7 (F6c STRUCTURAL DROP per S1901 §7.4.1) and loses `principal_user` at Celery process boundary 9 (F6a). Cat F.a maturity: **EXPERIMENTAL** (undocumented cross-plane read + structural drops unrecovered).

- **F2 (HIGH — Cat F.b Content) — Content pipeline seam is PERMEABLE-BROKEN via Freeze × PublishGate composition gap.** `core/services/content_deliberation_runner.py` PublishGate reads content-quality + reviewer-verdict metrics but does NOT consult `JobContract.authority[action_class]` or `GovernanceState.mode`. Freeze reads `HumanSystemState.review_mode` (S1806 F1 evidence) not `GovernanceState.mode`, so Freeze × Authority precedence is broken per S1903 Q5 designed resolution. Cross-arc T-slot handoff to Group 1600 P4 (S1699 §7.4 follow-on doc-PRs); severity HIGH consolidation. Cat F.b maturity: **PARTIAL** (PublishGate operational; authority coupling deferred by design per P2 D89 Option C precedent).

- **F3 (MEDIUM — Cat F.c Sports) — Sports seam is STRUCTURAL-DROP via F6a Celery arbitrage dispatch + zero authority coupling by design.** `core/services/betting_outcome_verifier.py` makes zero authority reads; arbitrage auto-fire (per S1903 Q3/Q5 deferral evidence) is intentional per-action-type product decision, not authority-gated. Boundary 8/9 F6a drops `principal_user` at Celery process boundary. Cat F.c cross-arc T-slot handoff to Group 1500 P6 posture-decision ADR (per S1599 close deferral pattern per §D59). Severity MEDIUM consolidation (intentional separation; no active enforcement gap). Cat F.c maturity: **PARTIAL** (verifier + bridge operational; authority coupling by-design absent).

- **F4 (HIGH — Cat F.d HAI) — HAI auto-approve seam is PERMEABLE-BROKEN at three enforcement-binding points.** Verified at `core/services/human_attention_lifecycle.py:243` — `if system_state.review_mode:` reads `HumanSystemState.review_mode` ONLY. Zero `GovernanceState.mode` reads. Zero `KillSwitch(target=...)` reads. The 5-entry `LOW_RISK_SOURCES` at `human_attention_lifecycle.py:63-69` predates the `AuthorityLevel` enum and carries implicit OBSERVE/RECOMMEND classification without explicit `JobContract.authority[source_type]` wiring. Per S1903 §17.1 Plane Precedence Policy, the precedence order `K > A > F > H` at HAI auto-approve is **aspirational, not implemented**. Currently only `M` (Mission-governance via `review_mode`) is evaluated. Three specific gaps map to queued T-slot items: T2 R.AUTHORITY.AUTO-APPROVE-FREEZE-GATE (S1903 Q5) + T3 R.AUTHORITY.LOW-RISK-SOURCES-EXPLICIT-AUTHORITY-TAGS (S1903 Q6) + T2 R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION (S1902 D88 + S1903 §7.4.1 D94). Cat F.d maturity: **WORKING** (auto-approve operational; three enforcement composition gaps queued for post-arc).

- **F5 (HIGH — Cat F.e Employee OS) — Employee OS is P3's designated canonical read-discipline site; the runtime enforcement wire-up is queued (not landed at HEAD) per staged rollout.** `core/employees/mission_runner.py:601-638` init reads `MissionRunnerConfig.job_contract` and emits `AUTHORITY_CONTRACT_OBSERVED` at `:835-900` (Boundary 5 warn-mode). Per P3 §7.7 Q7 designed resolution, `MissionRunner.resolved_enforce_authority_mode` is the canonical post-init read. **Post-Explore verifier confirmed via direct grep: `enforce_authority_mode` is absent at HEAD across `core/employees/`; this is expected per staged rollout — tracked as T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS execution item, not a contradiction of the P2 D91 + P3 Q7 ratified design (Rigby SIGN cycle 1 Q2 fold — non-accusatory framing per staged-rollout arc contract).** The systemic implication for xx99 §5 canonical seam statement remains: the entire two-tier max-strictness composition contract operates as **design-complete, runtime-scaffolding** at S1904 close. Additionally: K reads at 6 governance.py/intelligence.py sites are ALL management/audit/cleanup contexts per S1903 §14.1 verified classification correction (ZERO enforcement dispatch); D94 KillSwitch Enforcement Reader is spec-only pending T2 R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION; Celery actor-role kwargs are missing at Boundary 8/9 F6a per S1901 §7.4.1. Cat F.e maturity: **WORKING** (observation-mode operational; three enforcement-binding wire-ups deferred to post-arc T1/T2).

- **F6 (LOW — Cat F.f Frontend) — Frontend seam is CLEAN.** Frontend routes go through Boundary 1 HTTP auth middleware (`core/auth_middleware.py:563-681`, authentication-only per S1902 §17 row 1) and delegate all authority enforcement to API + Employee OS layers. Zero direct authority reads at frontend. `App.tsx` 61 routes are behind `ProtectedRoute` (session auth); workspace tabs' authority-aware UX is delegated to per-view server-side implementation. Per parent §5.4, Frontend is a delegated-decision surface. **No T-slot items generated by P4 for Frontend seam.** Cat F.f maturity: **EXPERIMENTAL** (seam contract undocumented but genuinely separated; no active enforcement gap because enforcement is upstream).

- **F7 (HIGH — Cat F.g API) — API seam is PERMEABLE-BROKEN at Boundary 1 + 209-view distributed enforcement gap.** HTTP auth middleware (`core/auth_middleware.py:563-681`) authenticates but does NOT consult `JobContract.authority[action_class]` per S1902 D90 enum resolution. 209 views across `core/views_*.py` have zero documented per-view authority reads per Explore 3 sample of 10+ views. Actor context (`executor_actor` + `sponsor_actor`) is not propagated from HTTP auth into API request pipeline per S1901 Boundary 1 F6c. Per P2 §17 row 1 evaluation order `K > M > A` at HTTP middleware is aspirational; currently only `M` (Django session auth) is evaluated. Cross-arc T-slot: T3 R.AUTHORITY.API-LAYER-AUTHORITY-INSTRUMENTATION (dependency: Symbol Mapping graduation for per-action-class registry). Cat F.g maturity: **EXPERIMENTAL** (seam operational at auth layer; authority-layer enforcement scaffolding-only).

- **F8 (CRITICAL structural — Cat F.h Discord) — Discord seam is STRUCTURAL-DROP per S1903 Q8 formal deferral verified at runtime.** `core/services/discord_bot.py` (96 commands, 25 Cog classes, 11,676 LOC per PLATFORM_INVENTORY) has zero authority reads. No `action_class` signaling on commands. `RateLimiter` class (`:85-100`) applies command cooldowns, not authority-derived throttling. Verified via Explore 3 grep: **all three S1903 Q8 upstream prerequisites remain real blockers** — (1) Symbol Mapping runtime registry (S1270 graduation status: NOT DEPLOYED per S1274 Option E v0 evidence-only); (2) per-Discord-command action_class audit (ZERO completed per Explore 3); (3) Discord actor path shape (S1901 §6.2 formalization: NOT DONE; `_get_linked_user()` fallback returns None when unlinked). Cross-arc T-slot: T2 R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION (S1903 T2, 3 upstream prerequisites). Cat F.h maturity: **EXPERIMENTAL** (dispatch operational; authority integration deferred until 3 prerequisites resolve).

- **F9 (HIGH cross-plane — F5 HYPOTHESIS "duplicate authority-check-adjacent primitives across planes" DISPROVE).** Explore 6 tested HYPOTHESIS: "Every plane with autonomous writers (Memory, HAI, Employee OS) has a duplicate authority-check-adjacent primitive." Result: DISPROVE across all 8 planes. Memory has no dup gate. Employee OS has enforce_authority_mode field (scaffolding, not dup gate). HAI's `review_mode` + `LOW_RISK_SOURCES` + `require_review_above_confidence` gates are decision-adjacent, not authority-adjacent. This is a NOVEL cross-plane pattern finding at P4 close: NO adjacent plane duplicates authority primitives; all inherit or defer. Consistent with P2 D89 Option C precedent (evidence-only mode until Symbol Mapping graduates). Meta-methodology datapoint: F5 running tally under Group 1900 = 0 pass / 1 disprove at S1904; extending S1806 Group 1800 tally of 1 pass / 4 disprove per S1806 §20.7. Aggregate cross-arc F5 running tally: 1 pass / 5 disprove.

- **F10 (HIGH cross-plane — Zero-authority-check-at-boundary durable-across-P1-P2-P3-P4).** Pattern from Explore 6 §E.2: **Zero seams have explicit authority-level → action binding.** Employee OS observes but does not enforce. Frontend delegates. API's Boundary 1 authenticates but does not authorize by action_class. Content's PublishGate is quality-only. HAI's auto-approve reads `review_mode` only. Sports arbitrage bypasses authority by design. Discord is structurally dropped. This is consistent with P2 D89 Option C (evidence-only mode) but it means NO seam is operational for authority enforcement at HEAD. Durable-at-four under Group 1900 arc (documented at P1 §14 + P2 §14 + P3 §14 + P4 §14). Cross-arc analog: fail-open posture is CANONICAL default per LLMEnforcer F8 precedent (`core/llm_enforcer.py:237-238`) + ToolDispatcher silent-skip precedent (`core/services/tool_dispatcher.py:691, 693`). P4 catalogs; xx99 §5 consolidated domain shape codifies this as arc-wide finding.

- **F11 (HIGH — Cross-plane propagation-contract touchpoint drops CONSOLIDATED).** Per Explore 4 seam matrix + S1901 §7.4 F6 register: 4 distinct structural-drop classes affect 5+ planes each:
  - **F6a** (Celery process boundary loses `principal_user`) — affects Memory + Content + Sports + HAI + Employee OS async paths.
  - **F6c** (Step.fn closure opaque to runner actor context) — affects Memory + Content + Sports + HAI + Employee OS step bodies + Discord dispatch.
  - **F6c-adjacent** (Django async signal receivers) — affects HAI model pre_save/post_delete + Content/Sports/Memory signal chains.
  - **Boundary 1 F6c** (HTTP auth → view context propagation) — affects API/Frontend actor context carry-through.
  Total distinct drop-class-per-plane count: **~24** (some planes affected by multiple drop classes). Post-arc T1 R.AUTHORITY.ACTOR-KWARGS-CELERY + T1 R.AUTHORITY.ACTOR-STEP-CONTEXT are the primary closure paths per S1901 §7.4.1.

- **F12 (MEDIUM — Test-gap durable-across-P1-P2-P3-P4 arc-wide TEST-GAP-CONFIRMED).** Per Explore 6 §E.3 grep `test_*authority*seam*|test_*plane_seam*|test_*boundary_authority*|test_*seam_*enforcement*` returned ZERO dedicated seam-enforcement test files. `test_priority_enforcement.py` tests budget-gate enforcement, not authority-seam enforcement. `test_mission_runner_authority_warn_mode_s1264.py` tests authority contract event-shape validation, not seam behavior. Durable-across-four-children under Group 1900 arc. Extends S1806 F9 durable-at-six under Group 1800 test-gap arc-wide pattern. Post-arc T2 R-slot candidate: R.AUTHORITY.SEAM-BOUNDARY-TEST-COVERAGE (8-plane × 3-scenario matrix minimum).

**Biggest architectural risk — RISK-SPLIT FRAMING (per S1806 precedent + Rigby SIGN discipline):** Present two distinct risks so reviewers don't argue past each other:

- **F5 = highest STRATEGIC / SYSTEMIC risk (blocks xx99 §5 consolidated domain shape).** Employee OS is the design-only canonical read-discipline site. Zero runtime implementation of `enforce_authority_mode` at HEAD. The entire P2 D91 two-tier composition + P3 Q7 canonical read discipline are aspirational as of S1904. xx99 §5 consolidated domain shape cannot cleanly assert "authority is operational" until T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS lands. xx99 should frame authority enforcement posture as "design-complete, runtime-scaffolding" per P2 D89 Option C evidence-only precedent.

- **F8 = highest IMMEDIATE ENFORCEMENT-GAP risk (could enable unauthorized dispatch tomorrow).** Discord seam is structurally dropped with 96 commands x 25 Cogs and zero authority integration. Any Discord command that dispatches Celery tasks + calls agent services can execute LLM-costing or state-changing operations without authority observation, let alone enforcement. Three upstream prerequisites (Symbol Mapping graduation + per-command action_class audit + Discord actor path shape) must all resolve before enforcement wire-up. Not blocked-by-design like Sports (F3); blocked-by-missing-prerequisites.

**Canonical seam statement (for xx99 §5 consumers to reason "what exists" vs "what's aspirational"):** At HEAD `c902e003`, Authority Enforcement seam maturity distributes as **5 PERMEABLE-BROKEN + 2 STRUCTURAL-DROP + 1 CLEAN**. Zero seams are STABLE or CANONICAL. Employee OS is the design-only canonical read-discipline site. Signal-aggregation service (Memory-adjacent) makes a real cross-plane read into Autonomy plane at `signal_aggregation_service.py:211` that is undocumented in Group 1300 topic docs. HAI auto-approve reads `HumanSystemState.review_mode` only, breaking the P3 §17.1 precedence contract at three enforcement-binding points. API's Boundary 1 authenticates but does not authorize by action_class. Discord dispatch has zero authority integration per S1903 Q8 formal deferral. This is consistent with P2 D89 Option C evidence-only precedent — Authority is design-complete, runtime-scaffolding. The 11 T-slot items in §19 route the enforcement wire-up across owning arcs (Employee OS T0/Gate + T1; HAI T2 + T3; Content T1; Sports T3; API T3; Discord T2; Memory T3; Frontend N/A).

**Biggest gaps for future research:** (a) **R0 (STRATEGIC POST-ARC — xx99 §5 canonical seam-posture-statement)** — synthesize F1-F12 findings into a canonical statement of Authority Enforcement seam maturity for cross-arc consumers; (b) **R1 Signal-aggregation cross-plane read documentation** (Memory Cat F.a implicit Autonomy read at `signal_aggregation_service.py:211`; needs first-inventory documentation + potentially a proper contract if this pattern should persist); (c) **R2 HAI auto-approve Freeze × KillSwitch × Authority composition** (S1903 Q5 T2 + Q6 T3 + D94 T2 execution consolidation); (d) **R3 Employee OS runtime enforcement toggle landing** (S1902 D91 + P3 Q7 T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS); (e) **R4 API 209-view authority-read audit** (S1902 §17 boundary 1 evaluation-order actualization; requires Symbol Mapping graduation); (f) **R5 Discord dispatch 3-prerequisite unblock ADR** (S1903 Q8 T2 R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION); (g) **R6 Seam boundary test coverage** (F12 durable-across-P1-P2-P3-P4 TEST-GAP-CONFIRMED; T2 R.AUTHORITY.SEAM-BOUNDARY-TEST-COVERAGE); (h) **R7 Cross-plane fail-open posture codification** (F10 durable pattern; xx99 §5 should codify or explicitly reject as CANONICAL default); (i) **R8 Cross-arc T-slot handoff routing** (11 T-slot items distributed across Group 1300/1500/1600/1800 + Group 1900 + Group 2000+ Event Architecture); (j) **R9 Actor-role Celery kwargs + Step context wire-up** (S1901 F6a + F6c T1 execution consolidation); (k) **R10 Cross-arc anchor-update batch** (per Explore 5: 7 new topic docs across authority-adjacent seams; likely deferred to xx99 §7 anchor-update recommendations).

Runtime maturity classification arc-wide: **PARTIAL with EXPERIMENTAL enforcement.** Seam distribution: 4 EXPERIMENTAL / 2 PARTIAL / 2 WORKING / 0 STABLE / 0 CANONICAL. No arc-close STABLE rating possible without R3 (Employee OS runtime enforcement) + R2 (HAI composition wire-up) + R6 (seam test coverage). xx99 §5 posture statement should acknowledge this framing as "design-complete, runtime-scaffolding, closure-gated on 3 T1 items."

## 2. Domain Purpose

**Q1 What is the Cat F "Adjacent / Separation Boundaries" consolidation surface and what is it responsible for?** Cat F is the arc-close consolidation surface for Group 1900 (Authority Enforcement Design Space). Its purpose is TWO-fold per parent §5.4: (a) audit the seams between Authority Enforcement and 8 adjacent planes (Memory / Content / Sports / HAI / Employee OS / Frontend / API / Discord) as an **interface + seam audit** — NOT as an internal-correctness audit of any adjacent plane; (b) consolidate P1 (S1901 actor-role propagation contract) + P2 (S1902 8 D-verdicts + §17 Enforcement Binding Points map) + P3 (S1903 Plane Precedence Policy + KillSwitch Enforcement Reader Design + KillSwitch classification correction) into an evidence brief for the xx99 S1999 canonical summary §5 consolidated domain shape + §8 follow-on queue. Cat F is a CONSOLIDATION audit, not a direct architecture audit — it inherits boundary discipline "catalogs; does NOT act on any of F.a-F.h items" per parent §5.4 checks/does-NOT-check table + playbook §14.5 no-implementation rule. All F1-F12 findings promote to post-arc T-slot; no Cat F-scope implementation lands under S1904.

**Q2 What are the biggest gaps in this seam surface today?** The most load-bearing gap is **F5 (Employee OS runtime enforcement toggle absent at HEAD)** because it's the design-only canonical read-discipline site — every other plane's enforcement wire-up depends on Employee OS being operational first. The second largest is **F4 (HAI auto-approve reads `review_mode` only, breaking the K > A > F precedence contract at three enforcement-binding points)**. The most cross-cutting is **F10 (zero-authority-check-at-boundary durable-across-P1-P2-P3-P4)** — no seam has explicit authority-level → action binding today, consistent with P2 D89 Option C evidence-only precedent but blocking xx99 §5 canonical seam statement. **F1 (signal-aggregation implicit cross-plane read)** and **F2 (Content PublishGate × Authority composition gap)** and **F8 (Discord structural-drop with 3 upstream prerequisites)** are HIGH domain-specific gaps queued for cross-arc T-slot handoff. **F11 (structural drops F6a/F6c/F6c-adjacent × 5+ planes each)** and **F12 (test-gap durable-across-P1-P2-P3-P4)** are cross-cutting patterns queued for post-arc execution + arc-wide test coverage.

## 3. Canonical Entry Points

Per CONSOLIDATION shape from S1806 precedent — §3 divided into 8 per-plane sub-slots (F.a Memory / F.b Content / F.c Sports / F.d HAI / F.e Employee OS / F.f Frontend / F.g API / F.h Discord). Each sub-slot enumerates the plane-side canonical entry points that touch the authority seam.

### 3.1 Sub-slot F.a — Memory plane seam (Group 1300 territory)

**Plane-side canonical entry points touching authority seam:**

- **`signal_aggregation_service.py`** @ `core/services/signal_aggregation_service.py:211` — reads `GovernanceState.objects.filter(scope='global').first()` (Autonomy plane cross-plane read; post-Explore verifier confirmed direct read, not implicit). This is the SINGLE verified Memory-side authority-plane read at HEAD; documented nowhere in Group 1300 topic docs or S1399 xx99 §7.
- **Canonical writer plane** — `AgentLearning` + `UserAgentLearning` writers (per S1399 §5 F4 six-plane fragmentation). Actor-role propagation from Employee OS mission runner reaches Memory writers **exclusively via Step.fn closure at Boundary 6/7** (F6c STRUCTURAL DROP per S1901 §7.4.1). Any Memory writer inside a MissionRunner step must re-infer executor_actor from row state (e.g., `AgentLearning.agent_name`) or close over runner config.
- **Async writer paths** — `UserAgentLearning` writes via Celery beat-fired learning bridge tasks. Boundary 9 F6a STRUCTURAL DROP: `principal_user` lost at Celery process boundary.
- **PA tool surface** — `memory_palace_tool` (per Explore 3) — carries `user_id` only, not `executor_actor`/`sponsor_actor`/`principal_user` trio; drops at Boundary 3 F6c PA tool handler body.

**Cross-arc scope note:** Memory internal-correctness (six-plane learning fragmentation per S1399 §5 F4; four coexisting Agent*Learning services + duplicate-file BoardroomLearningService pairs per S1806 F3/F4) is out-of-scope for P4. P4 audits ONLY: signal-aggregation cross-plane read + writer-plane drop points + PA-tool carriage.

### 3.2 Sub-slot F.b — Content plane seam (Group 1600 territory)

**Plane-side canonical entry points touching authority seam:**

- **PublishGate** — `core/services/content_deliberation_runner.py` PublishGate.decision — reads claim confidence + AI-reviewer decision + Freeze via `HumanSystemState.review_mode`. Does NOT read `JobContract.authority[action_class]` or `GovernanceState.mode`. Freeze check is at `HumanSystemState` layer, not `GovernanceState` layer, per S1806 F1 evidence.
- **`content_executor.py`** — content generation service — makes ZERO direct authority reads at HEAD per Explore 2 verified grep. Assumed via S1902 §17 design that authority gates content-generation but no read site exists.
- **Boundary 5 event emission** — Content-creation missions run through Employee OS MissionRunner, so authority contract event emits at `core/employees/mission_runner.py:835-900` (Employee-OS-owned, not Content-owned). Content plane does not emit its own authority event.
- **REST endpoints** — 9 ContentTemplateViewSet / DocumentViewSet / KnowledgeBaseViewSet / etc. use `permission_classes = [permissions.IsAuthenticated]` per Explore 3 (`core/apps/content/views.py:46+`). Auth-only, no authority-level check.
- **PA tools** — `content_generation_tool` + `document_rag_tool` (Explore 3) — carry `user_id`, drop actor-role trio.
- **Async correction** — Discord broadcast fire-and-forget (S1604 T.15.C1 finding via Explore 5) has ZERO gate integration.

**Cross-arc scope note:** Content internal-correctness (PublishGate decision quality, claims-pack deliberation correctness, deliverable-variant access control) is out-of-scope for P4. P4 audits ONLY: PublishGate × Authority composition gap + Freeze layer mismatch + REST auth-only carriage + PA tool drops.

### 3.3 Sub-slot F.c — Sports plane seam (Group 1500 territory)

**Plane-side canonical entry points touching authority seam:**

- **`BettingOutcomeVerifier`** @ `core/services/betting_outcome_verifier.py` — verifies arbitrage outcomes; makes ZERO authority reads per Explore 2 verified grep. Per S1903 Q3/Q5 deferral rationale, arbitrage auto-fire is per-action-type product decision.
- **`SportsBettingLearningBridge`** @ `core/learning_bridges/sports_betting_bridge.py` (per S1806 §4 model inventory) — writes `UserAgentLearning` per canonical bridge writer plane. Actor-role via Step.fn closure (F6c drop).
- **REST endpoints** — sports/views.py (per Explore 3) — no explicit `permission_classes` observed; likely AllowAny or implicit session auth.
- **PA tools** — `sports_tool` (odds/games/predictions) + `betting_tool` (place_bet/history/analysis) per Explore 3 — carry `user_id`, drop actor-role trio.
- **WebSocket consumers** — `SportsConsumer` @ `sports/consumers.py:14` + `LiveSportsConsumer` @ `consumers_base.py:26` (Explore 3) — no explicit user auth in `connect()`; joins group unconditionally.
- **Discord commands** — `/live-games`, `/live-odds`, `/predictions`, `/betting-history`, `/place-bet` (per Explore 3) — Sports is one of the higher-touch domains from Discord.
- **Boundary 20 spider run** — S1901 §7.3 row 20 sports-related spider ingestion; Sports arbitrage detection depends on Boundary 20 spider outputs.

**Cross-arc scope note:** Sports internal-correctness (BettingOutcomeVerifier arbitrage-filtering rationale per S1805 F3, DBAO naming-convention drift per S1506 Finding 6, zero-fire beat durable-at-two per S1503+S1504) is out-of-scope for P4. P4 audits ONLY: authority read absence + F6a Celery drops + WebSocket auth absence + Discord dispatch surface.

### 3.4 Sub-slot F.d — HAI plane seam (Group 1800 territory)

**Plane-side canonical entry points touching authority seam:**

- **HAI auto-approve gate** @ `core/services/human_attention_lifecycle.py:243` — `if system_state.review_mode:` reads `HumanSystemState.review_mode`. This is the ONLY authority-adjacent read at HAI seam. **Post-Explore verifier fold: Explore 4 cited `:240`; verified line is `:243`.**
- **`LOW_RISK_SOURCES`** @ `core/services/human_attention_lifecycle.py:63` — 5-entry list defining sources eligible for auto-approve. Used at `:264` in filter query `Q(source_type__in=self.LOW_RISK_SOURCES)`. Predates AuthorityLevel enum per S1903 Q6 deferral; carries implicit OBSERVE/RECOMMEND classification.
- **Auto-approve orchestration trigger** @ `human_attention_lifecycle.py:440-656` (per Explore 2) — when auto-approve fires, orchestration workflows may execute LLM calls that eventually hit LLMEnforcer (F8 fail-open); HAI itself makes no authority read before triggering.
- **Boundary 16 HAI decide endpoint** @ `core/views_human_interface.py:154` (per S1902 §17 row 16, corrected from S1272-cited `:84`) — HumanAttentionItem decision write site. Fail-closed on auth per S1902 D89 exception. Precedence `K > M > A > H` per S1903 §17.1.
- **PA tool `human_decisions_tool`** (per Explore 3) — list/details/decide handlers at `td_handlers_agents.py`. Decide action creates HAI rows + updates status without secondary authority check.
- **43+ HAI producer paths** — S1801 finding: zero producers respect `HumanPreference.blocked_sources` at creation time. Authority-adjacent-side: none read authority state before HAI creation.

**Cross-arc scope note:** HAI internal-correctness (auto-approve gate composition per S1801, FeedbackProcessor coupling per S1802, HumanPreference personalization per S1804, S746 verification per S1805, Cat F six-plane fragmentation per S1806) is out-of-scope for P4. P4 audits ONLY: `review_mode`-only Freeze read + LOW_RISK_SOURCES implicit-authority absence + K-read absence at auto-approve + Boundary 16 precedence composition + orchestration-trigger authority-absence.

### 3.5 Sub-slot F.e — Employee OS plane seam

**Plane-side canonical entry points touching authority seam:**

- **`MissionRunner.__init__`** @ `core/employees/mission_runner.py:601-638` — reads `MissionRunnerConfig.job_contract` optional; when present, evaluates `JobContract.authority` dict shape. Per P3 §7.7 Q7 designed resolution, canonical read-site is `MissionRunner.resolved_enforce_authority_mode` post-init (max-strictness composition of `AIEmployee.enforce_authority_mode` + `MissionRunnerConfig.enforce_authority_mode` per S1902 D91 two-tier composition).
- **CRITICAL DRIFT verified:** `enforce_authority_mode` field does NOT exist in `core/employees/` at HEAD per post-Explore verifier grep. P2 D91 landed as DESIGN ONLY; runtime implementation is post-arc T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS pending. The entire two-tier composition contract is aspirational at S1904 close.
- **`_emit_authority_contract_event`** @ `core/employees/mission_runner.py:835-900` (Boundary 5) — emits `AUTHORITY_CONTRACT_OBSERVED` event per S1264 warn-mode. Payload includes `employee_handle` + `contract_version_tag` + `authority_level_counts` (level counts derivable from `JobContract.authority` dict).
- **K reads at 6 governance.py/intelligence.py sites** — `governance.py:2192, 2370, 2508, 2545` + `intelligence.py:1569, 1717` per S1903 §14.1 verified classification correction. **ALL are management/audit/cleanup contexts; ZERO enforcement dispatch.** D94 KillSwitch Enforcement Reader is spec-only pending T2 R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION.
- **`AIEmployee` + `JobContract` frozen-dataclass registry** @ `core/employees/jobs.py` — declares `authority` dict per action_class → AuthorityLevel value (per S1902 D91). Zero runtime consumers of `authority` dict beyond MissionRunner init read + event emission.
- **Boundary 8/9 Celery kwargs** — per Explore 3 sample of 5 tasks, zero carry `executor_actor`/`sponsor_actor`/`principal_user` trio. Post-arc T1 R.AUTHORITY.ACTOR-KWARGS-CELERY.
- **Boundary 6/7 Step.fn closure** — Step signature does not include actor context; runner cannot pass actor state INTO step.fn body. F6c STRUCTURAL DROP; post-arc T1 R.AUTHORITY.ACTOR-STEP-CONTEXT.
- **Boundary 17 retro-audit** @ `core/employees/status.py:53-251` `evidence_for_mission` — reads OpsRun + OpsRunEvent for post-mission evidence; F6b closeable delta blocks retro-audit fidelity per S1901 §7.4.1.

**Cross-arc scope note:** Employee OS internal-correctness (job registry canonicity, mission runner determinism, retro-audit query shape) is out-of-scope for P4. P4 audits ONLY: authority-plane READ discipline (MissionRunner canonical read) + authority-plane WRITE discipline (Boundary 5 event emission) + Celery + Step drops + K-read enforcement gap.

### 3.6 Sub-slot F.f — Frontend plane seam

**Plane-side canonical entry points touching authority seam:**

- **`App.tsx` 61 routes** (per PLATFORM_INVENTORY) — routes behind `ProtectedRoute` (session auth via authStore). Zero client-side authority-level checks.
- **`/workspace?tab=system`** (governance panel) — defers to `/api/*/governance-state` endpoints (per Explore 3). Backend enforcement; frontend renders.
- **`/admin`** — likely checks role server-side; no client-side role validation visible.
- **`/workspace?tab=boardroom`** — HAI queue display; no explicit authority filtering per D91 per-employee toggle observable at frontend layer.
- **HTTP auth via `Authorization: Bearer <token>`** (axios interceptor). `request.user` at React layer via authStore. `request.user` FK carries `principal_user`; zero `executor_actor` or `sponsor_actor` propagation.

**Cross-arc scope note:** Frontend internal-correctness (route rendering, workspace tab UX, PA chat integration, telemetry) is out-of-scope for P4. P4 audits ONLY: Frontend has NO direct authority-plane seam; all authority enforcement is upstream at API + Employee OS layers.

### 3.7 Sub-slot F.g — API plane seam

**Plane-side canonical entry points touching authority seam:**

- **Boundary 1 HTTP auth middleware** @ `core/auth_middleware.py:563-681` — validates Token OR session; `PUBLIC_PATHS = ['/api/v1/health/', '/health/', '/api/app/manifest/']` per Explore 3. Authentication only; ZERO authority-level enum reads per S1902 D90 design.
- **`UnifiedTokenAuthenticationMiddleware`** @ `core/auth_middleware.py:85` — per Explore 3.
- **209 view files** across `core/views_*.py` per PLATFORM_INVENTORY — Explore 3 sampled 10+; zero per-view authority reads observed.
- **`views_employee_api.py`** — GET `/api/employees/` + `/api/employees/<handle>/jobs/<job_key>/status/` + `/api/missions/<mission_id>/` — reads AIEmployee + JobContract + OpsRun with 8-field envelope. `IsAdminUser` gated. Read-only.
- **`views_diagnostics.py:48-62`** — writes to `CockpitAuditLog` (auxiliary audit, not authority-plane seam).
- **`views_human_interface.py:154`** — Boundary 16 HAI decide endpoint (also enumerated at F.d).
- **`fleet_auth_drf.py:65-150`** — Boundary 19 Fleet internal API HMAC ingress (per S1902 §17 row 19). Fleet HMAC carries `app_slug` for executor + sponsor; permissive fallback per Explore 3.
- **PA tool dispatcher** @ `core/services/tool_dispatcher.py:685-720` — Boundary 2 AssistantProfile gate; fail-open at `:721-722` per S1902 §17 row 2 Explore verified. No JobContract.authority read.
- **REST endpoint drift** — S1605 T.15.E2 CRITICAL finding: "REST endpoints ZERO auth decorator" (per Explore 5). Cross-arc handoff to Content post-arc T-slot.

**Cross-arc scope note:** API internal-correctness (endpoint routing correctness, per-view business logic, permission_class discipline) is out-of-scope for P4. P4 audits ONLY: Boundary 1 authority-level absence + 209-view enforcement-gap + Boundary 2 tool_dispatcher fail-open + Boundary 19 Fleet HMAC + Boundary 16 HAI decide.

### 3.8 Sub-slot F.h — Discord plane seam

**Plane-side canonical entry points touching authority seam:**

- **`discord_bot.py`** — 11,676 LOC per PLATFORM_INVENTORY; 96 commands across 25 Cog classes. ZERO authority-plane reads per Explore 3 sample.
- **`RateLimiter` class** @ `discord_bot.py:85-100` — per-command cooldowns; NOT authority-derived (Discord-native rate control).
- **`PermissionLevel` class** @ `discord_bot.py:129` — `ADMIN_USER_IDS` + `TRUSTED_USER_IDS` per Explore 3; no role/authority mapping to web User model.
- **`DiscordLinkCode` model** — Discord user_id ↔ web User FK mapping. `_get_linked_user()` fallback returns None when unlinked per Explore 3.
- **PA tool dispatcher path** — Discord commands dispatch via PA tool surface, so downstream drops match Boundary 3 F6c PA tool handler body pattern.
- **Celery task dispatch from Discord** — Discord async commands (e.g., `/agent-task`) fire `execute_agent_task.apply_async(...)` per Explore 3. Boundary 8/9 F6a drops.
- **Boundary 3 adjacent** per S1902 §17 (Discord is NOT in P2 20-boundary table; treated as adjacent surface for PA tool handler body).

**S1903 Q8 formal deferral 3 upstream prerequisites (VERIFIED via Explore 3 grep at S1904):**

1. **Symbol Mapping runtime registry** — S1274 Option E v0 (evidence-only) DEPLOYED per S1274 close; graduation to A/B/C/D DEFERRED post-arc per S1274 §10.3.1 triggers. Runtime registry mapping command → action_class does NOT exist.
2. **Per-Discord-command action_class audit** — ZERO documentation exists for which of 96 commands should map to which AuthorityLevel per S1902 D90 enum. No signal at HEAD.
3. **Discord actor path shape (S1901 §6.2)** — Discord user_id ≠ Django User.id; `DiscordLinkCode` mapping is fallback-nullable. `principal_user` can be None; `executor_actor` is weak (discord_user_id string). Per S1901 Layer ii §7.3, Discord is out-of-table adjacent surface.

**Cross-arc scope note:** Discord internal-correctness (96-command god-service refactor, per-Cog UX correctness, Discord-specific auth model) is out-of-scope for P4. P4 audits ONLY: Discord authority-plane read absence + 3 S1903 Q8 prerequisites verification + F6c-adjacent drop + Boundary 8/9 drops from Discord-triggered Celery tasks.

## 4. Major Models

Cat F is CONSOLIDATION scope. This section catalogs authority-plane models touched at each plane seam + FK graph crossing the authority ↔ adjacent-plane boundary. No new models are introduced. Full model provenance / lineage was audited at P1 (S1901 §4) + P2 (S1902 §4) + P3 (S1903 §4) + adjacent-plane arcs (S1301-S1305 / S1501-S1506 / S1601-S1606 / S1801-S1806).

**Authority-plane models (canonical registry per S1902 §4 + S1903 §4):**

| Model / State | File:Line | Owner | Consumers at seam |
|---|---|---|---|
| `AIEmployee` frozen dataclass | `core/employees/jobs.py` | Group 1900 | READ by MissionRunner init; no adjacent-plane readers |
| `JobContract` frozen dataclass (with `authority: dict[str, str]`) | `core/employees/jobs.py` | Group 1900 | READ by MissionRunner init; no adjacent-plane readers |
| `MissionRunnerConfig` dataclass | `core/employees/mission_runner.py` | Group 1900 | Constructed by adjacent job modules (e.g., `core/jobs/docs_cascade.py`); passes `job_contract` to runner |
| `OpsRun(domain='mission')` | `core/models_ops_runs.py` | Group 1900 (Employee OS audit substrate) | WRITTEN by MissionRunner @ `:778`; READ by Sports/bug_triage @ L1073+; READ by API/diagnostics @ views_diagnostics.py:155; READ by API/employee_api via `derive_status` @ status.py:53 |
| `OpsRunEvent` | `core/models_ops_runs.py` | Group 1900 (Employee OS audit substrate) | WRITTEN by MissionRunner @ `:882` (label=`authority_contract_observed` per Boundary 5); READ by Sports/bug_triage authority-baseline telemetry |
| `SystemConfiguration authority_enforce:*` keys (5 keys per D93) | `core/models_system_configuration.py` (SPECULATIVE — verified location; may live in models_config.py) | Group 1900 (Chris-owned admin surface) | READ ONLY by retrospective-scan task per S1902 §12.8; no adjacent-plane readers today |
| `GovernanceState.mode` (Autonomy plane) | `core/models_governance.py:17+` | Autonomy plane (Group 1200-adjacent) | READ by signal_aggregation_service.py:211 (Memory seam per F1); READ by tasks_spiders.py:384; READ by workspace_pipeline_runner.py:646 |
| `KillSwitch(target=...)` | `core/models_governance.py:102+` | Autonomy plane | READ at 6 sites all management/audit/cleanup per S1903 §14.1 VERIFIED; ZERO enforcement dispatch |
| `SystemConfiguration.budget_freeze_active` (Freeze plane sub-state) | `core/models_system_configuration.py` | Autonomy plane (sync from GovernanceState) | READ by LLMEnforcer @ `llm_enforcer.py:201-221`; adjacent-plane readers via LLMEnforcer transitive dependency |
| `LLMEnforcer` (Budget plane) | `core/llm_enforcer.py` | Budget plane (Group 1200-adjacent) | CALLED by intelligence/ai_resume_generator.py:229, :484 (2 sites verified per Explore 2); CALLED by workspace_pipeline_runner.py:646; F8 fail-open at `:237-238`, `:263-264` |
| `_auto_approve_low_risk_items` gate (HAI plane) | `core/services/human_attention_lifecycle.py:240-296` | HAI plane (Group 1800) | 8-gate composition; reads `review_mode` @ `:243` only |
| `HumanAttentionItem` | `core/models_human_interface.py:36-227` | Group 1800 Cat A | WRITTEN by 43+ producer paths; READ + updated by decide endpoint |

**Cross-plane FK graph — adjacent-plane models with FKs INTO authority-plane models:**

Per Explore 1 comprehensive audit: **ZERO adjacent-plane models carry FKs to `OpsRun`, `OpsRunEvent`, `AIEmployee`, or `JobContract`.** All relationships point inbound (mission_id optional in OpsRun, run FK in OpsRunEvent). This prevents accidental coupling loops.

**Adjacent-plane models READ by authority-plane services:**

| Model | File:Line | Read by | Purpose |
|---|---|---|---|
| `HumanSystemState` | `core/models_human_interface.py` (HAI plane) | HAI auto-approve gate reads at `human_attention_lifecycle.py:243` — but this is HAI-plane INTERNAL read, not authority-side | Boundary 16 decision-adjacent state |
| `HumanFeedbackRecord` | `core/models_human_interface.py:230-265` (Group 1800 Cat B) | Not read by authority-plane | Group 1800 Cat B territory |
| `AgentLearning` + `UserAgentLearning` | `core/models/ai_learning/models.py` (Group 1300 Memory) | Not read by authority-plane | Group 1300 Memory territory |
| `LearningInsight` | `core/models/ai_learning/models.py` | Not read by authority-plane | Group 1300 Memory territory |
| `AssistantProfile` | (SPECULATIVE — location) | Boundary 2 tool_dispatcher — this is Frontend/API plane READ for allowed_tools gate | Boundary 2 fail-open |

**Duplicate authority-adjacent models across planes (Explore 1 F5 HYPOTHESIS test DISPROVE evidence):**

- `HumanSystemState.review_mode` (HAI plane) parallels `GovernanceState.mode='freeze'` (Autonomy plane) semantically but is a SEPARATE model — HAI does NOT read GovernanceState. This is **semantic duplication, not model coupling**. Per Explore 1 finding E4, this is loose-coupling duplication (acceptable, maintainable per-plane).
- Discord `RateLimiter` cooldowns (Discord plane) parallel authority-plane role/rate-control logic semantically but is Discord-specific.

Per Explore 6 F5 HYPOTHESIS test at §17.2: no plane exhibits a duplicate authority-check gate primitive.

## 5. Major Services

Cat F CONSOLIDATION cross-plane consolidation service map. Adjacent-plane services that CALL authority-plane primitives + services that DUPLICATE authority-check-adjacent primitives.

### 5.1 Adjacent-plane services calling authority-plane primitives

Per Explore 2 verified grep across `intelligence/`, `content/`, `sports/`, `human_attention/`, `employees/`, `frontend/`, `views_*.py`, and `discord_bot.py`:

| Caller (adjacent) | File:Line | Callee (authority primitive) | Fail behavior | Boundary # |
|---|---|---|---|---|
| `AIResumeGenerator._generate_summary` | `intelligence/ai_resume_generator.py:229` | `LLMEnforcer.enforce_real_ai(task_type='resume_summary')` | Try/except @ `:251-263` → template fallback (FAIL-OPEN) | Boundary 14 |
| `AIResumeGenerator.generate_cover_letter` | `intelligence/ai_resume_generator.py:484` | `LLMEnforcer.enforce_real_ai(task_type='cover_letter')` | Try/except @ `:513-561` → template fallback (FAIL-OPEN) | Boundary 14 |
| `signal_aggregation_service._resolve_governance` | `core/services/signal_aggregation_service.py:211` | `GovernanceState.objects.filter(scope='global').first()` | Direct model read (fail-open on None per S1902 §17 row 20-adjacent posture) | Cross-plane (Memory F.a implicit) |

**Total authority-primitive call sites from adjacent planes:** 3 verified sites (2 Intelligence LLMEnforcer + 1 Memory-adjacent GovernanceState). All fail-open.

**Non-adjacent authority-plane INTERNAL call sites** (out-of-scope for P4; documented for §14 completeness):

- `core/tasks_spiders.py:384` — `GovernanceState.objects.filter(scope='global').first()` — Spider run boundary (Boundary 20).
- `core/services/workspace_pipeline_runner.py:646` — `LLMEnforcer.enforce_real_ai(...)` — pipeline workflow orchestration.

### 5.2 Adjacent-plane duplicate authority-check-adjacent primitives

Per Explore 2 + Explore 6 F5 HYPOTHESIS test: **ZERO adjacent planes duplicate authority-check-adjacent primitives.** Per F9 finding (§1): DISPROVE. All planes either inherit authority state via LLMEnforcer transitive dependency or defer authority per P2 D89 Option C.

Semantic-only parallels (not model duplicates):

- HAI auto-approve `review_mode` gate parallels Freeze plane semantically (see F4).
- Discord `RateLimiter` parallels action-throttling semantically (see F8).
- Sports arbitrage-confidence gates parallel Authority EXECUTE semantically (Explore 4 F.c narrative).
- Content PublishGate quality gates parallel Authority RECOMMEND semantically (Explore 4 F.b narrative).

All four are ORTHOGONAL to authority — different signal sources, different model families.

### 5.3 Duplicate composition resolvers across planes

Per Explore 2: NONE. No plane implements its own multi-plane composition resolver duplicating P3 §17.1 Plane Precedence Policy. Composition is distributed-at-boundary per P3 §3 design.

### 5.4 Employee OS canonical read-discipline site status

Per P3 Q7 designed resolution, `MissionRunner.resolved_enforce_authority_mode` is the canonical post-init read for the two-tier max-strictness composition of `AIEmployee.enforce_authority_mode` + `MissionRunnerConfig.enforce_authority_mode`.

**Verified status at HEAD `c902e003`:** Post-Explore verifier grep `enforce_authority_mode` across `core/employees/` returns ZERO matches. `MissionRunner.__init__` @ `mission_runner.py:601-638` reads `MissionRunnerConfig.job_contract` but the `enforce_authority_mode` field itself does not exist on either dataclass. The entire two-tier composition contract is DESIGN-ONLY at S1904 close. Post-arc T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS execution required per S1902 D91.

## 6. Major APIs and Interfaces

Cat F CONSOLIDATION external-facing surface inventory per plane (REST + PA tools + Celery + Discord + WebSocket + Frontend routes) that crosses the authority boundary.

### 6.1 REST endpoint inventory touching authority seam

- **Total view files:** 209 across `core/views_*.py` (PLATFORM_INVENTORY).
- **Authority-touching subset (Explore 3 sample):** ~50 endpoints IsAuthenticated + ~30 AllowAny + specific IsAdminUser at `/api/employees/`.
- **Boundary 1** — `core/auth_middleware.py:563-681` — sole documented authority-adjacent read-site at API layer. Zero A_LEVEL / A_MODE enum reads per S1902 D90 design gap.
- **Boundary 16** — `core/views_human_interface.py:154` — HAI decide endpoint. Fail-closed on auth per S1902 D89 exception. `K > M > A > H` precedence per S1903 §17.1.
- **Boundary 19** — `core/services/fleet_auth_drf.py:65-150` — Fleet HMAC ingress. Permissive fallback per Explore 3.
- **Boundary 18** — `core/consumers*.py` WebSocket handlers (see §6.4).

### 6.2 PA tool schemas + handlers

- **Total schemas:** 113 (PLATFORM_INVENTORY).
- **Total handlers:** 156 (PLATFORM_INVENTORY).
- **Boundary 2** — `core/services/tool_dispatcher.py:685-720` — AssistantProfile gate + fail-open at `:721-722`. No JobContract.authority read.
- **Boundary 3** — Per-handler bodies (`td_handlers_*.py`) — 11 mixin classes × 2-5 methods = ~42 handlers per Explore 3. Zero visible actor-contract carriage across sampled handlers.

### 6.3 Celery task inventory

- **Total tasks:** 414 (PLATFORM_INVENTORY).
- **Boundary 8** — dispatch sites (`.apply_async` / `.delay()`) — HTTP-sourced closeable via kwargs per S1901 §7.4.2; beat-fired remains structural DEFAULT-CANONICAL.
- **Boundary 9** — task entry (`@shared_task`) — F6a STRUCTURAL DROP; `request.user` lost at process boundary.
- Per Explore 3 sample of 5 tasks: **0/5 carry `executor_actor`/`sponsor_actor`/`principal_user` trio.** Zero actor-contract carriage across Memory/Content/Sports/HAI/Employee-OS/API/Discord adjacent Celery paths.

### 6.4 WebSocket consumers (Boundary 18)

Per Explore 3, 6 sampled consumers from `core/routing.py:51-100+`:
- `AgentProgressConsumer` @ `/ws/activity/` — SafeWebSocketMixin; NO explicit user auth in `connect()`.
- `AgentPlatformConsumer` @ `/ws/agent-platform/` — custom `connect()`; implicit via `scope['user']`.
- `DecisionCommandConsumer` @ `/ws/decision-command/` — NO auth check before `group_add`.
- `SpiderWebSocketConsumer` @ `/ws/spider-updates/` — conditional import; no auth visible.
- `ConsciousnessConsumer` @ `/ws/consciousness/` — assumed pattern.
- `PAConversationConsumer` @ `/ws/pa-conversation/` — `async_to_sync(get_user)` call present.

Boundary 18 sample explicit-user-extraction rate: **1/6**. Zero authority-level reads observed at WebSocket layer.

### 6.5 Discord commands

- **Total commands:** 96 across 25 Cog classes (PLATFORM_INVENTORY / S1903 §14.4).
- **discord_bot.py LOC:** 11,676 (PLATFORM_INVENTORY).
- Per Explore 3 sample of 5 commands (`/ask-document`, `/place-bet`, `/boardroom`, `/subscribe`, `/agent-task`): **0/5 carry authority-adjacent validation.**
- Boundary 3 adjacent per S1902 §17 (Discord NOT in 20-boundary table).

### 6.6 Frontend routes (authority-touching subset)

- **Total routes:** 61 in `App.tsx` (PLATFORM_INVENTORY).
- Authority-touching subset (Explore 3): 15+ (all `ProtectedRoute`); no client-side role checks.

## 7. Runtime Flows

Cat F CONSOLIDATION per-plane propagation-contract touchpoint trace. Where does actor-role propagation from P1 §7 cross into each adjacent-plane concern? Where are the drop points?

### 7.1 Cat F per-plane propagation-contract touchpoint map

Master seam-matrix table (per Explore 4 comprehensive audit). Columns: Plane / Inbound authority-plane reads / Outbound authority-plane writes / Propagation drop points (P1 §7.4 boundary#) / Enforcement read-sites (P2 §17 boundary#) / Precedence join (P3 §17.1) / Fail posture (P2 §17.2) / Duplicate primitives / Gap points / Posture verdict / Owned-by-1900 vs delegated / Cross-arc T-slot.

| Plane | Inbound reads | Outbound writes | Propagation drops | Enforcement read-sites | Precedence join | Fail posture | Duplicate primitives | Gap points | Posture verdict | Owned-by-1900 vs delegated | Cross-arc T-slot |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Memory (1300)** | signal_aggregation_service.py:211 reads `GovernanceState.mode`; no direct authority reads from AgentLearning/UserAgentLearning writers | Zero | Boundary 6/7 F6c (Step.fn closure); Boundary 9 F6a (Celery process) | None | N/A | Observation-only | None | Undocumented cross-plane read at signal_aggregation | PERMEABLE-BROKEN | Delegated to 1300 (Memory owns internal-correctness) | S1300 T3 R.MEMORY.SIGNAL-AGG-AUTHORITY-COUPLING-DOC |
| **Content (1600)** | Zero direct authority reads at PublishGate; Freeze reads `HumanSystemState.review_mode` (S1806 F1) | Zero (Boundary 5 event via Employee-OS-owned) | Boundary 6/7 F6c; Boundary 9 F6a | None (PublishGate is quality-only) | N/A | Observation-only | Claims-review parallels Authority RECOMMEND semantically | PublishGate × Authority composition; Freeze layer mismatch; Discord broadcast fire-and-forget | PERMEABLE-BROKEN | Delegated to 1600 (Content owns PublishGate) | S1600 T1 R.CONTENT.PUBLISHGATE-AUTHORITY-COMPOSITION |
| **Sports (1500)** | Zero BettingOutcomeVerifier reads | Zero (Boundary 5 event via Employee-OS-owned) | Boundary 6/7 F6c; Boundary 8/9 F6a (arbitrage dispatch) | None | N/A | Observation-only | Arbitrage-confidence parallels Authority EXECUTE semantically | Arbitrage × enforce_authority_mode integration absent; Boundary 8 kwargs | STRUCTURAL-DROP | Delegated to 1500 (Sports owns arbitrage logic) | S1500 T3 R.SPORTS.ARBITRAGE-AUTHORITY-COMPOSITION |
| **HAI (1800)** | `HumanSystemState.review_mode` at `:243` only; ZERO GovernanceState or KillSwitch reads | Boundary 5 event via Employee-OS-owned | Boundary 6/7 F6c; Boundary 9 F6a; Boundary 10 F6c-adjacent (async pre_save/post_delete) | Boundary 16 (views_human_interface.py:154) reads implicit authority from LOW_RISK_SOURCES enum | K > M > A > H at HAI auto-approve (aspirational; currently M only) | Fail-closed on Freeze @ `:243`; fail-open on all other authority checks | LOW_RISK_SOURCES implicit authority carrier | Freeze × KillSwitch × Authority precedence not implemented; LOW_RISK_SOURCES no explicit AuthorityLevel tags; no observation event at decide | PERMEABLE-BROKEN | Owned-by-1900: precedence order (P3 §17.1); Delegated-to-1800: LOW_RISK_SOURCES classification | S1800 T2 R.AUTHORITY.AUTO-APPROVE-FREEZE-GATE + T3 R.AUTHORITY.LOW-RISK-SOURCES-EXPLICIT-AUTHORITY-TAGS + T2 R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION |
| **Employee OS** | JobContract.authority read at MissionRunner.__init__ `:601-638`; K reads at 6 governance.py/intelligence.py sites (ALL mgmt/audit/cleanup per S1903 §14.1) | Boundary 5 `authority_contract_observed` event emit at mission_runner.py:835-900 | Boundary 6/7 F6c (Step.fn); Boundary 8/9 F6a (Celery kwargs missing); Boundary 10 F6c-adjacent | Boundary 4 (MissionRunner entry) reads JobContract.authority + evaluates enforcement_mode (currently observe-only); Boundary 5 emits event with level_counts | K > A per P3 §17.1 (K reads mgmt/audit only, A observe-only) | Fail-open on all authority checks per S1902 D89 | None | enforce_authority_mode field NOT ON dataclasses (P2 D91 design-only); 4 employees warn-mode-only; K enforcement reader not implemented (D94 T2); Celery kwargs missing | PERMEABLE-BROKEN | Owned-by-1900: authority binding + precedence + fail-open policy; Delegated to Employee OS: per-job authority tagging | R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION (T2) + R.AUTHORITY.ACTOR-KWARGS-CELERY (T1) + R.AUTHORITY.ACTOR-STEP-CONTEXT (T1) + R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS (T0/Gate for runtime landing) |
| **Frontend** | Zero direct authority reads at HTTP request level | Zero | Boundary 1 F6c (HTTP auth → view context propagation) | Boundary 1 (`core/auth_middleware.py:563-681`) — sole read-site for API-plane authority | K > M > A at HTTP middleware (currently auth-only) | Fail-closed on auth failure; observation-only on authority | None | Workspace governance panel undocumented authority read-site; per-route authorization undocumented | CLEAN | Delegated to Frontend (per-route authorization) | None |
| **API** | Boundary 1 auth middleware authenticates; ZERO A_LEVEL/A_MODE enum reads per S1902 D90 | Zero | Boundary 1 F6c (auth → view actor context) | Boundary 1 (sole documented site) | K > M > A per P3 §17.1 (aspirational; M only) | Fail-closed on auth; observation-only on authority | None | 209 views zero per-view authority reads; actor context not propagated from auth → view; no authority observation event at API entry; S1605 T.15.E2 REST endpoints ZERO auth decorator finding inherited | PERMEABLE-BROKEN | Owned-by-1900: precedence at middleware; Delegated to API: per-view authorization | T3 R.AUTHORITY.API-LAYER-AUTHORITY-INSTRUMENTATION (dependency: Symbol Mapping graduation) |
| **Discord** | Zero authority reads; no action_class signaling on 96 commands | Zero | Boundary 3 adjacent F6c (Discord command → PA tool handler closure) | None | N/A (S1903 Q8 formal deferral) | N/A (no enforcement gates) | RateLimiter parallels rate-control semantically | Symbol Mapping runtime registry not deployed; per-command action_class audit not started; Discord actor path shape not formalized; no observation event | STRUCTURAL-DROP | Delegated-to-Discord: per-command action_class + actor path (post-graduation); Owned-by-1900: precedence envelope post-graduation | T2 R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION (3 upstream prerequisites) |

### 7.2 Cross-plane duplicate authority-check-adjacent primitive inventory (F5 HYPOTHESIS DISPROVE evidence)

Per §5.2 + Explore 6 §E.1 F5 HYPOTHESIS: **"Every plane with autonomous writers has a duplicate authority-check-adjacent primitive."** Result: **DISPROVE** across all 8 planes.

- Memory: NO duplicate gate (signal-aggregation is cross-plane READ, not duplicate primitive).
- Content: NO duplicate gate (PublishGate is quality-only, semantically parallel).
- Sports: NO duplicate gate (arbitrage-confidence is product-decision).
- HAI: NO duplicate gate (review_mode + LOW_RISK_SOURCES + confidence gates are decision-adjacent, not authority-adjacent).
- Employee OS: NO duplicate gate (enforce_authority_mode is scaffolding, not dup primitive).
- Frontend / API / Discord: NO duplicate gate.

**F5 running tally at S1904 close under Group 1900:** 0 pass / 1 disprove.
**Aggregate cross-arc F5 running tally at S1904 close:** 1 pass (S1806 Cat F.d partial confirmation) / 5 disprove (S1802 + S1803 + S1804 + S1805 + S1904). Meta-methodology datapoint per S1806 §20.7 codification-ready pattern.

### 7.3 Cat F separation-boundary policy register — owned by 1900 vs delegated

Per Explore 4 cross-plane synthesis:

| Decision | Owned by 1900 | Delegated to adjacent plane |
|---|---|---|
| Precedence order (K > A > F > B > H per P3 §17.1) | Yes | — |
| Fail-open vs fail-closed default policy | Yes (S1902 D89) | Per-boundary override possible |
| Per-employee `enforce_authority_mode` toggle semantics | Yes (S1902 D91) | — |
| Symbol Mapping `action_class` graduation triggers | Co-owned (1900 envelope; 2000+ implements) | — |
| LOW_RISK_SOURCES → AuthorityLevel classification | Yes — mechanism | Delegated to HAI (1800): classification data |
| Per-view authorization model (API 209 views) | No — too fine-grained | Delegated to API / Frontend |
| Discord per-command action_class labeling | No — Discord domain | Delegated to Discord post-graduation |
| Content PublishGate authority composition | No — Content owns gate | Delegated to Content (1600) |
| Sports arbitrage authority composition | No — Sports owns arbitrage | Delegated to Sports (1500) |
| Memory signal-aggregation authority filtering | No — Memory owns signal logic | Delegated to Memory (1300) |
| Cross-plane fail-open codification (F10) | Yes (xx99 §5 canonical statement) | — |
| Seam boundary test coverage (F12) | Yes (T2 R.AUTHORITY.SEAM-BOUNDARY-TEST-COVERAGE) | — |

## 8. Data Ownership and Lifecycle

Per Explore 1 seam model inventory + Explore 4 seam matrix synthesis:

- **Authority-plane audit substrate** (OpsRun + OpsRunEvent) — WRITER: Employee OS MissionRunner (sole writer at HEAD). READERS: Sports/bug_triage triage window + API/diagnostics admin cockpit + API/employee_api derive_status. Lifecycle: retention per `CELERY_TASK_EVENT_RETENTION_DAYS` default 30 (per PLATFORM_INVENTORY).
- **Authority-plane state** (JobContract + AIEmployee frozen registry) — WRITER: `core/employees/jobs.py` compile-time only (frozen dataclass). READER: MissionRunner init. Lifecycle: source-code lifetime.
- **Authority-plane configuration** (`SystemConfiguration authority_enforce:*` keys per D93) — WRITER: Chris admin surface only. READERS: retrospective-scan task per S1902 §12.8 (post-arc T1 R.AUTHORITY.RETROSPECTIVE-SCAN-TASK). Lifecycle: config-lifetime.
- **Cross-plane state read** (`GovernanceState.mode` from Memory F.a signal-aggregation) — WRITER: Autonomy plane (out-of-scope for this doc). READER: `signal_aggregation_service.py:211` cross-plane read. Lifecycle: state-machine per GovernanceState.
- **HAI-plane state** (`HumanSystemState.review_mode`) — WRITER: HAI plane (S1801-S1806 territory). READER: HAI auto-approve at `human_attention_lifecycle.py:243`. Lifecycle: HAI-plane owned.

**Key ownership observation:** Authority-plane audit substrate (OpsRun + OpsRunEvent) has **strong write-only ownership** (Employee OS writes; 3 adjacent planes read-only). No adjacent plane writes to authority audit models. No adjacent-plane FKs point at authority-plane models. Per Explore 1 finding E3: "No backward refs." Read/write asymmetry is architecturally healthy.

## 9. Integrations With Other Domains

Cross-domain integration map for authority ↔ each adjacent plane. Cross-referenced to `docs/research/platform/cross_domain_integration_audit.md` §2.

Per Explore 4 seam matrix + Explore 5 doc inventory:

| Adjacent domain | Integration strength (S1274 pair classification) | Direction | Notes |
|---|---|---|---|
| Memory (1300) | **WEAK** | Bidirectional (implicit) | signal-aggregation cross-plane read; writer-plane inherits actor via Step.fn closure (F6c drop) |
| Content (1600) | **MISSING** | Would-be bidirectional | PublishGate does not read authority; per parent §5.4 gap point |
| Sports (1500) | **INTENTIONAL_ISLAND** | Would-be bidirectional | Arbitrage-only filter per S1805 F3; authority decoupled by S1903 Q3/Q5 deferral rationale |
| HAI (1800) | **WEAK** | Bidirectional | Boundary 16 decide reads implicit authority; auto-approve reads review_mode only |
| Employee OS | **STRONG** (observation) / **WEAK** (enforcement) | Authority-plane INTERNAL | Canonical read-discipline site; enforcement runtime scaffolding-only |
| Frontend | **DELEGATED** (upstream enforcement) | Read-only | All enforcement at API + Employee OS layers |
| API | **WEAK** | Bidirectional (auth-layer only) | Boundary 1 authenticates; zero A_LEVEL / A_MODE reads |
| Discord | **STRUCTURAL-DROP** | Would-be bidirectional | S1903 Q8 formal deferral; 3 upstream prerequisites |

**Cross-domain integration count roll-up:** 5 WEAK + 1 MISSING + 1 INTENTIONAL_ISLAND + 1 DELEGATED. Zero STRONG integrations at HEAD (Employee OS strong for observation only). Zero OVERCOUPLED integrations (per Explore 1 E3 finding: no adjacent-plane FKs into authority models).

**Cross-arc integration deltas from S1274 cross_domain_integration_audit.md §2:** P4 verified no new integrations landed since S1274 close. Signal-aggregation read at `:211` was likely present at S1274 but not surfaced in cross_domain_integration_audit.md §2.2 Signal→Memory row (which classified as STRONG for memory read but did not flag authority-plane cross read).

## 10. Event Flows

Per Explore 3 event synthesis:

- **`AUTHORITY_CONTRACT_OBSERVED` event** (S1264 warn-mode label per S1902 D89 dependency) — EMITTER: `MissionRunner._emit_authority_contract_event()` @ `core/employees/mission_runner.py:835-900`. `AUTHORITY_CONTRACT_SCHEMA_VERSION = 1`. CONSUMERS at HEAD: test suite only (`test_mission_runner_authority_warn_mode_s1264.py`). ZERO production consumers per Explore 3. All 3 production mission factories (rigby, platform_auditor, chief_of_staff) emit per mission.

- **HAI decide event** — EMITTER: PA tool dispatcher on `human_decisions_tool.action='decide'` per `td_handlers_agents.py`. CONSUMERS: `boardroom_ml_service.py` (reads HumanAttentionItem post-decision). NO authority gating at emission; no authority observation event at Boundary 16.

- **Planned `AUTHORITY_CONTRACT_VIOLATED` event** (P2 D89 dependency) — NOT YET IMPLEMENTED. Would emit when authority PROHIBITED level blocks dispatch under `enforce_authority_mode = 'enforce'` post-T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS landing. Anticipated consumers across all 8 planes.

- **KillSwitch reader events (future D94)** — planned rate-limited `logger.warning` with prefix `killswitch_missed_reader:<boundary>` per S1903 §7.4.1 F8 alignment. 4 REQUIRED insertion boundaries (2 + 3 + 6 + 18) + 1 OPTIONAL (16). Not wired at HEAD; T2 slot.

**Event-flow gap:** ZERO authority events at seam-boundary. No emission at PublishGate decision. No emission at BettingOutcomeVerifier check. No emission at HAI auto-approve gate. No emission at API request entry. No emission at Discord dispatch. All authority-plane events emit only at Employee-OS-owned surface (Boundary 5 warn-mode). Per xx99 §5 canonical seam statement: authority observation is Employee-OS-scoped only.

## 11. Existing Documentation

Per Explore 5 comprehensive doc inventory:

**Per-plane doc coverage matrix (classification: NONE / LIGHT / MODERATE / DEEP / CANONICAL):**

| Plane | Coverage | Existing docs | Gap list |
|---|---|---|---|
| Memory (1300) | LIGHT | S1301-S1305 child audits; S1399 xx99; cross_domain_integration_audit §2.2 | Signal-aggregation authority coupling; writer-plane authority boundaries; feedback→learning authority |
| Content (1600) | LIGHT | S1601-S1606; S1699 §7.4; cross_domain_integration_audit §2.3 | PublishGate × Authority; reviewer decision enforcement; deliverable-variant access; claims-pack authority |
| Sports (1500) | NONE | S1501-S1506; S1599; cross_domain_integration_audit §2.2 (Sports→Signal MISSING) | Arbitrage × Authority; sports-intelligence Initiative auth; DBAO naming authority; arbitrage-only rationale |
| HAI (1800) | LIGHT | S1801-S1806; S1899 §8 T-tier | HAI creation gatekeeping; LOW_RISK_SOURCES authority classification; feedback writer authority contract |
| Employee OS | LIGHT | S1268-S1272 research; EMPLOYEE_OS_PRIMITIVES.md; P1/P2/P3 designs | Inter-employee dispatch authority; employee-scope access; MissionRunner ↔ ToolDispatcher composition; T1 runtime verification |
| Frontend | NONE | docs/topics/frontend.md distributed | Frontend route authorization; Workspace tab access; ContentStudioTab force=true (S1605 §15.E3); modal access |
| API | LIGHT | docs/API_PATH_POLICY.md; cross_domain_integration_audit §4.2 (9 OpenAI imports bypass factory) | REST endpoint authority; POST auth decorator (S1605 §15.E2); Boundaries 18/19/20; service-to-service auth |
| Discord | LIGHT | docs/DISCORD_INTEGRATION.md; cross_domain_integration_audit §1 (11,677-line god-service) | Discord command-level authority; per-command actor-role propagation; DiscordLinkCode mapping; bot-permission × action-class |

**Aggregate:** **LIGHT-to-NONE across all 8 planes.** No plane has MODERATE+ seam-focused coverage. Zero CANONICAL seam docs.

**Recommended xx99 §7 anchor-update batch scope (queued for xx99):** 7-8 new `docs/topics/authority-<plane>-boundaries.md` first-inventory landings, OR targeted anchor-refresh at existing per-plane topic docs + PLATFORM_INVENTORY.md §Authority Enforcement seam sub-section.

**Authority-plane-side doc inventory (per Explore 5):**

- `PLATFORM_WHAT_IT_IS.md` — zero mentions of authority-plane composition or governance planes; adjacent-plane authority seams not discussed.
- `PLATFORM_INVENTORY.md` — authority-plane runtime block: Governance + Authority (Group 1900) rows note 4 governance planes per S1273 §3.23; source: S1269 §1. Post-S1904 no adjacent-plane authority-seam runtime counts required.
- `EMPLOYEE_OS_PRIMITIVES.md` — §4 anti-duplication matrix names JobContract.authority (frozen dataclass); authority plane listed as owner. No adjacent-plane seam specifics.
- `docs/API_PATH_POLICY.md` — 7,743 bytes; content not read; expected REST-endpoint authority routing coverage.
- `docs/DISCORD_INTEGRATION.md` — 14,746 bytes; content not read; expected Discord command dispatch authority coverage.

## 12. Research Coverage

Per Explore 5 aggregate classification: **LIGHT** across all 8 planes for seam-focused coverage. Zero CANONICAL seam docs.

Per-plane per-audit-question research coverage (playbook §12 5-value scale):

| Plane | Research Coverage | Rationale |
|---|---|---|
| Memory (1300) | LIGHT | S1399 §7 anchor-updates do not cite authority seams; findings scattered across S1301-S1305 |
| Content (1600) | LIGHT | S1605 §15 T.15.C1 / T.15.E* authority-adjacent findings; no dedicated seam section |
| Sports (1500) | NONE | Zero seam-focused docs; Sports isolated per S1274 v2 "intentional island" framing |
| HAI (1800) | LIGHT | S1806 Cat F CONSOLIDATION analog; S1899 §8 T0/Gate items queued; no consolidated seam doc |
| Employee OS | LIGHT | Authority seam documented in research docs (S1268/S1269 + P1/P2/P3); no dedicated topic doc |
| Frontend | NONE | Zero seam-focused docs; S1605 findings are Content-domain |
| API | LIGHT | API_PATH_POLICY.md exists but seam coverage unknown; S1901/S1903 flag Boundaries 18/19/20 as new |
| Discord | LIGHT | S1903 Q8 formal deferral; DISCORD_INTEGRATION.md exists but detailed seam coverage unknown |

**Meta-observation:** Group 1900 P1/P2/P3 produced the deepest authority-plane research to date. P4 CONSOLIDATION is the FIRST authority-adjacent-seam-focused audit across the arc; xx99 canonical summary will inherit as the first cross-plane synthesis.

## 13. Architecture Maturity

Per Explore 6 §Part A per-plane classification (playbook §12 5-value scale):

| Plane | Maturity | Rationale |
|---|---|---|
| Memory (1300) | EXPERIMENTAL | Signal-aggregation cross-plane read undocumented; writer-plane structural drops F6c/F6a; no seam contract |
| Content (1600) | PARTIAL | PublishGate operational; Freeze layer mismatch (`review_mode` not `GovernanceState.mode`); authority deferred by P2 D89 Option C |
| Sports (1500) | PARTIAL | BettingOutcomeVerifier operational; authority decoupled by S1903 Q3/Q5 deferral (intentional separation) |
| HAI (1800) | WORKING | Auto-approve operational; three composition gaps (Freeze × K × A) queued per Q5/Q6/D94 |
| Employee OS | WORKING | Observation-mode operational; three enforcement wire-ups (`enforce_authority_mode` field + K reader + Celery kwargs) deferred to post-arc T0/Gate + T1 |
| Frontend | EXPERIMENTAL | Seam contract undocumented but genuinely separated; all enforcement upstream |
| API | EXPERIMENTAL | Seam at auth layer operational; authority-level enforcement scaffolding-only |
| Discord | EXPERIMENTAL | Dispatch operational; 3 upstream prerequisites block authority integration |

**Distribution:** 4 EXPERIMENTAL / 2 PARTIAL / 2 WORKING / 0 STABLE / 0 CANONICAL.

**Arc-wide seam maturity verdict:** **PARTIAL with EXPERIMENTAL enforcement.** Consistent with P2 D89 Option C evidence-only precedent — authority is design-complete, runtime-scaffolding. No arc-close STABLE rating possible without T1 landing (Employee OS enforce_authority_mode field + Celery kwargs) + T2 landing (HAI K reader + Discord graduation) + T2 seam test coverage.

## 14. Known Drift

### 14.1 Inherited drifts from P1/P2/P3

**From P1 (S1901 §14):**
- F6a/F6b/F6c/F6c-adjacent STRUCTURAL DROPS at 4 boundary classes — inherited into F11 (§1) cross-plane consolidation.

**From P2 (S1902 §14):**
- §14.2 KillSwitch "4 dispatch-consumer" classification — **CORRECTED at P3 §14.1** (all 6 verified reads at governance.py:2192, 2370, 2508, 2545 + intelligence.py:1569, 1717 are management/audit/cleanup contexts, ZERO enforcement dispatch). Per S1903 close, Rigby SIGN Q3 fold recommends BOTH targeted S1902 correction PR + xx99 §7 anchor-update batch.
- §14.4 Inherited-in drifts (parent §5.2 F8→F9 constraint + 4→5 modes count; S1272 §3.1 Boundary 16 line drift `:84-100` → `:154`; Option E label collision S1272 §9.5 Multi-layer vs S1274 Symbol Mapping; CLAUDE.md 3-vs-runtime-4 employee_handles drift; HAI auto-approve 7-vs-8 gate count reconciliation).

**From P3 (S1903 §14):**
- §14.1 KillSwitch classification correction (verified consumer at P4 §17.5).
- §14.2 Explore 2 F4 refutation misread caveat (F4 is desync-risk framing, not sync-direction refutation).
- §14.3 Explore 6 KillSwitch classification alignment with §14.1.
- §14.4 Inherited drifts from S1902 §14.4 (not re-verified at P3; queued for xx99).

**Inherited-into-P4 status:** All above drifts remain queued for xx99 §7 anchor-update batch. P4 does not re-verify inherited drifts per playbook §14 MC-1 discipline (P4 verifies SEAMS, not parent arcs' internal correctness).

### 14.2 Net-new drifts caught by P4 verifier-loop (pre-Explore)

**None caught pre-Explore.** Parent §5.4 P4 checks table + P1/P2/P3 inherited claims all verified at HEAD `c902e003` at pre-Explore. All 8 adjacent-plane entry-point classes confirmed to exist. This is consistent with Group 1900 arc pattern (P3 also caught zero pre-Explore drifts against parent §5.3; verifier-loop pre-Explore for CONSOLIDATION shape validates seam-inventory rather than parent-claim-vs-runtime).

### 14.3 Net-new drifts caught by P4 verifier-loop (post-Explore)

**Three drifts caught during Explore-return synthesis:**

- **§14.3.1 HAI `review_mode` line drift `:240` → verified `:243`.** Explore 4 cited `core/services/human_attention_lifecycle.py:240` for the `if system_state.review_mode:` check. Post-Explore verifier grep confirmed the actual line is `:243`. Off-by-3 line drift, likely from evolution of preceding logging block. Fold: use `:243` throughout P4. **Severity: LOW (line-precision drift; no semantic impact). Queued for xx99 §7 anchor-update batch as part of standard verifier-loop hygiene.**

- **§14.3.2 Memory Cat F.a seam classified as PERMEABLE-BROKEN, not CLEAN.** Explore 1 initially found "zero direct authority reads from Memory services" and classified seam-shape as `no_boundary`. Explore 4 flagged signal-aggregation implicit coupling. Post-Explore verifier grep confirmed direct read at `core/services/signal_aggregation_service.py:211`: `GovernanceState.objects.filter(scope='global').first()`. This is an EXPLICIT cross-plane read from Memory's signal-aggregation pipeline INTO Autonomy plane — not implicit, not transitive. **Severity: MEDIUM (posture verdict correction — CLEAN → PERMEABLE-BROKEN). Elevates F1 to HIGH-structural finding. Queued for xx99 §7 anchor-update batch: recommend either (a) documenting this cross-plane read in Group 1300 topic docs + PLATFORM_WHAT_IT_IS.md governance planes section, OR (b) proposing a proper contract if the pattern should persist (potentially R.MEMORY.SIGNAL-AGG-AUTHORITY-COUPLING-DOC at T3).**

- **§14.3.3 Employee OS `enforce_authority_mode` field CONFIRMED-NOT-IMPLEMENTED at HEAD via direct grep.** Explore 2 flagged this as SPECULATIVE ("Either P2 D90/D91 design was not shipped, or it's scaffolded dead code, or it's in a different file"). Post-Explore verifier grep `enforce_authority_mode` across `core/employees/` returned ZERO matches. This CONFIRMS the field does NOT exist at HEAD. **This is NOT a P2 design drift** — P2 D91 explicitly queued the field addition to post-arc T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS per S1902 §19. It is a **design-vs-runtime gap explicitly documented in the T-tier queue**. Fold: reference this gap explicitly in F5 (§1) and §5.4. **Severity: HIGH structural (blocks the entire two-tier composition contract per P2 D91 + P3 Q7 from operating at runtime). Not a NEW drift; queued item explicit-verification confirmation. Recorded for xx99 §5 canonical seam statement consumption.**

### 14.4 Cross-arc drift observations

Per Explore 5 doc coverage inventory, Group 1900 P4 identifies the following cross-arc drift observations that xx99 §7 should batch:

- **Memory (Group 1300):** signal-aggregation cross-plane authority read at `signal_aggregation_service.py:211` is not documented in `docs/topics/spider-network.md` (which owns signal-aggregation topic) or S1399 xx99 §7 anchor-updates.
- **Content (Group 1600):** S1605 T.15.E2 CRITICAL finding ("REST endpoints ZERO auth decorator") is unresolved and inherits into F7 API seam PERMEABLE-BROKEN classification.
- **Sports (Group 1500):** S1599 D59 posture-decision deferral persists; authority-seam framing not settled per S1599 close pattern.
- **HAI (Group 1800):** S1899 §8 T0/Gate 6-item bundle (including R.HAI.LEARNING-PLANE-CONTRACT-ADR + R.HAI.SOURCE-KIND-ENUM-ADR) remains queued; overlaps with F4 HAI auto-approve composition gaps.
- **Employee OS:** P3 §7.7 canonical read discipline for `MissionRunner.resolved_enforce_authority_mode` is DESIGN-ONLY at HEAD; runtime landing gated on T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS.

## 15. Known Technical Debt

Per Explore 6 §Part C per-plane seam debt matrix:

| Plane | Debt | Severity | Rationale |
|---|---|---|---|
| Memory | Undocumented cross-plane authority read at signal_aggregation_service.py:211 | HIGH | Cross-plane read exists in runtime; documented nowhere in Group 1300 topic docs. Blocks §5 canonical seam statement. |
| Memory | F6c/F6a structural drops at writer-plane paths | MEDIUM | Cross-arc handoff to S1901 F6 register + Post-arc T1 |
| HAI | Freeze-mode blocking not implemented at auto-approve gate | HIGH | P3 Q5 designed resolution (T2 slot); currently only review_mode blocks |
| HAI | LOW_RISK_SOURCES → AuthorityLevel classification implicit, not explicit | MEDIUM | P3 Q6 deferral (T3 slot); 5 sources predate enum |
| Employee OS | enforce_authority_mode field missing on both dataclasses | CRITICAL | P2 D91 + P3 Q7 design-only at HEAD; blocks entire two-tier composition contract runtime; T0/Gate for T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS |
| Employee OS | Boundary 8/9 Celery kwargs missing actor-role trio | HIGH | S1901 §7.4.1 F6a; T1 R.AUTHORITY.ACTOR-KWARGS-CELERY |
| Employee OS | Step.fn signature missing actor context | HIGH | S1901 §7.4.1 F6c; T1 R.AUTHORITY.ACTOR-STEP-CONTEXT |
| Employee OS | KillSwitch enforcement reader not wired (D94 spec) | HIGH | S1903 §7.4.1 D94 design; T2 R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION |
| API | 209 views zero per-view authority reads | HIGH | Depends on Symbol Mapping graduation; T3 R.AUTHORITY.API-LAYER-AUTHORITY-INSTRUMENTATION |
| API | Boundary 1 HTTP middleware zero A_LEVEL/A_MODE reads | HIGH | Per S1902 D90 design; T3 |
| API | Actor context not propagated from auth → view (Boundary 1 F6c) | MEDIUM | Structural drop; requires header/context-var carrier design |
| Content | PublishGate × Authority composition gap | MEDIUM | Deferred by P2 D89 Option C; T1 R.CONTENT.PUBLISHGATE-AUTHORITY-COMPOSITION |
| Content | Freeze reads HumanSystemState not GovernanceState | MEDIUM | S1806 F1 inherited; layer mismatch at Freeze plane |
| Sports | Arbitrage × enforce_authority_mode integration absent | LOW | Intentional per S1903 Q3/Q5 deferral; T3 R.SPORTS.ARBITRAGE-AUTHORITY-COMPOSITION |
| Discord | S1903 Q8 3 upstream prerequisites unblocked | CRITICAL | Symbol Mapping graduation + per-command action_class + actor path shape; T2 R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION |
| Frontend | Workspace governance panel authority read-site undocumented | LOW | Per-view decision; not 1900 scope |
| Cross-plane | Zero seam-boundary test coverage | HIGH | F12 durable-across-P1-P2-P3-P4; T2 R.AUTHORITY.SEAM-BOUNDARY-TEST-COVERAGE |
| Cross-plane | Fail-open posture unowned across seams | MEDIUM | F10 durable pattern; codification pending xx99 §5 |

**Debt severity roll-up:** 2 CRITICAL + 8 HIGH + 6 MEDIUM + 2 LOW.

## 16. Boundary Violations

Per Explore 2 boundary-violation catalog (severity-ranked):

**HIGH — HAI orchestration triggering without authority context.** Per Explore 2 analysis: When HAI auto-approve at `human_attention_lifecycle.py:440-656` triggers orchestration workflows, the triggered workflow has ZERO authority context. Called agents will eventually hit LLMEnforcer (F8 fail-open) but the HAI pre-approved path does not consume authority contract. **Severity HIGH.** This overlaps with F4 gap points but is registered separately as a boundary violation because the seam is bidirectional (HAI approves + orchestration executes with no authority-plane synchronization).

**HIGH — Signal-aggregation cross-plane read at Memory F.a (§14.3.2).** `signal_aggregation_service.py:211` reads `GovernanceState.mode` without documented contract. This is technically a cross-plane READ, not a violation of separation boundary, but the lack of documentation makes it a violation of the "adjacent planes should have explicit seam contracts" rule per parent §5.4. **Severity HIGH** (documentation absent; verified read direct).

**MEDIUM — Employee OS design-vs-runtime enforcement gap (§14.3.3).** P2 D91 two-tier composition contract exists as design; `enforce_authority_mode` field does not exist at runtime. Explicit T-slot handoff per S1902 §19 T1 queue. **Severity MEDIUM** (documented in T-tier queue; not a runtime bug per se, but blocks canonical-plane-statement for xx99).

**MEDIUM — API layer 209 views zero authority reads.** Per Explore 3 sample: authority state never queried in view layer. Per S1605 T.15.E2 (inherited): "REST endpoints ZERO auth decorator" CRITICAL finding. Requires Symbol Mapping graduation to close. **Severity MEDIUM** (deferred by design per Option C precedent).

**MEDIUM — Content/Sports pipeline authority contract absence.** PublishGate + BettingOutcomeVerifier make ZERO authority reads. Deferred by S1903 Q3/Q5 designed resolutions but caller-service contract at API ↔ service boundary is OPAQUE. **Severity MEDIUM** (design deferral; documented via cross-arc T-slot handoff).

**LOW — Duplicate composition semantics across HAI + Discord.** HAI `review_mode` gate and Discord `RateLimiter` are semantically parallel to authority-plane composition but implement independent policies. No model coupling, no gate duplication (per F5 HYPOTHESIS DISPROVE evidence). **Severity LOW** (semantic parallel, not architectural violation).

**Total boundary violations at seam:** 2 HIGH + 3 MEDIUM + 1 LOW = 6 categorized.

## 17. Duplicate or Overlapping Systems — Separation-Boundary Posture Register (P4 First-Class Deliverable)

Per CONSOLIDATION shape mirroring S1806 §17 pattern — per-plane separation-boundary posture register is P4's load-bearing deliverable for xx99 §5 consumption + xx99 §8 follow-on queue input.

### 17.1 Per-plane separation-boundary posture register

Master posture register (columns per parent §5.4 deliverable spec + Explore 4 §17 first-class shape):

| Plane | Owned-by-1900 authority decisions | Delegated-to-plane authority decisions | Shared / composed decisions | Posture verdict | xx99 §5 consumer note |
|---|---|---|---|---|---|
| **Memory (1300)** | Precedence order + fail-open default | Signal-aggregation filter thresholds (delegated to 1300 signal-owner) | signal_aggregation_service.py:211 cross-plane read (implicit; needs documented contract) | PERMEABLE-BROKEN | Undocumented cross-plane read is the load-bearing seam finding; xx99 §5 should acknowledge as HIGH structural |
| **Content (1600)** | Precedence order + fail-open default | PublishGate quality/novelty verdict (delegated to 1600 gate-owner) | Freeze × PublishGate composition (design gap per Q5) | PERMEABLE-BROKEN | PublishGate × Authority composition is T1 handoff to Group 1600 P4 post-arc |
| **Sports (1500)** | Precedence order + fail-open default | Arbitrage-fire decision + BettingOutcomeVerifier logic (delegated to 1500) | Arbitrage × Authority composition (T3 per Q3/Q5 designed deferral) | STRUCTURAL-DROP *(Rigby SIGN cycle 1 Q3(a) fold: STRUCTURAL-DROP = excluded from cross-plane composition pending prerequisites; NOT a statement about correctness. Sports has no authority-seam contract today by design deferral, so it's dropped from composition until prerequisites exist.)* | Intentional separation per S1903 Q3/Q5; low risk; T3 handoff |
| **HAI (1800)** | Precedence order + K > A > F > H canonical composition | LOW_RISK_SOURCES classification data (delegated to 1800) + auto-approve gate logic | Freeze × KillSwitch × Authority at auto-approve (T2 handoff) + LOW_RISK_SOURCES tagging (T3) | PERMEABLE-BROKEN | Three composition gaps map to specific T-slot items; xx99 §5 should stack-rank |
| **Employee OS** | Authority-plane contract + enforce_authority_mode toggle semantics + Boundary 5 event emission + fail-open policy | Per-job authority tagging (delegated to Employee OS jobs.py) + step-level action_class signals (post-graduation) | Canonical read discipline (P3 Q7) + K > A precedence at Employee OS dispatch scope | PERMEABLE-BROKEN | Canonical read discipline is design-only; T0/Gate for T1 R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS is the primary xx99 §5 blocker |
| **Frontend** | (no authority decisions owned) | Per-route authorization + workspace tab access (delegated to Frontend) | (no shared decisions; enforcement is upstream) | **CLEAN (verified read-only)** *(Rigby SIGN cycle 1 Q3(b) fold: Frontend does NOT compute or enforce authority/autonomy; it only RENDERS server-resolved state (e.g., mode/freeze/status) and does not write `enforce_authority_mode` / governance controls. Verification basis: no frontend-initiated mutation endpoints or UI controls observed for authority/governance fields; **if any UI can toggle these, Frontend becomes PERMEABLE-BROKEN until an explicit write-boundary contract exists**.)* | No cross-arc T-slot needed; genuinely separated by design |
| **API** | Precedence order at Boundary 1 middleware | Per-view authorization + endpoint-specific business logic (delegated to API) | Boundary 1 K > M > A (aspirational; M only implemented) + per-view authority reads (Symbol Mapping dependency) | PERMEABLE-BROKEN | 209-view enforcement gap is largest scope item; T3 dependency on Symbol Mapping graduation |
| **Discord** | Precedence envelope (post-graduation) | Per-command action_class labeling + Discord actor identity (delegated to Discord post-graduation) | (no shared decisions today; deferred to T2) | STRUCTURAL-DROP | 3 upstream prerequisites gate T2 R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION |

**Posture verdict distribution roll-up:**
- **PERMEABLE-BROKEN:** 5 planes (Memory + Content + HAI + Employee OS + API)
- **STRUCTURAL-DROP:** 2 planes (Sports + Discord)
- **CLEAN:** 1 plane (Frontend)
- **STABLE:** 0 planes
- **CANONICAL:** 0 planes

Cross-plane observation: 5 of 8 seams have specific enumerable design-vs-runtime enforcement gaps that map cleanly to queued T-slot items. 2 of 8 are intentionally deferred (Sports by design; Discord by 3-prerequisite). 1 of 8 is genuinely CLEAN (Frontend delegates upstream).

### 17.2 Cross-plane duplicate authority-check-adjacent primitives (F5 HYPOTHESIS DISPROVE evidence)

Per §5.2 + §7.2 F5 HYPOTHESIS test: **DISPROVE across all 8 planes.**

No plane implements a duplicate authority-check-adjacent gate primitive. All planes either:
- Inherit authority state via LLMEnforcer transitive dependency (Intelligence F.a-adjacent path).
- Defer authority reads per P2 D89 Option C (Content + Sports + HAI + Employee OS enforcement + Frontend + API + Discord).
- Read implicit authority via source classification (HAI LOW_RISK_SOURCES; Sports arbitrage flags).
- Delegate to platform-native gate (Discord RateLimiter; Frontend session auth).

Semantic-only parallels enumerated at §5.2 are loose coupling (per Explore 1 finding E4), not tight duplication.

**Cross-arc F5 running tally at S1904 close:** 1 pass (S1806 Cat F.d partial confirmation) / 5 disprove (S1802 + S1803 + S1804 + S1805 + S1904). Meta-methodology observation: durable-at-6 running tally under F5-primitive-testing arc-close discipline suggests DISPROVE-dominant pattern. xx99 §10 meta-methodology candidate for codification.

### 17.3 Cross-reference to P2 §17 Enforcement Binding Points map

Each of P2 §17's 20 boundaries maps to exactly one adjacent-plane column in §17.1:

| Boundary # | P2 §17 site | P4 §17.1 plane column |
|---|---|---|
| 1 | HTTP auth middleware | API (F.g) |
| 2 | ToolDispatcher.execute() | API (F.g) via PA tool surface |
| 3 | PA tool handler body | API (F.g) via PA tool surface |
| 4 | MissionRunner.run() entry | Employee OS (F.e) |
| 5 | MissionRunner preflight warn-mode | Employee OS (F.e) |
| 6 | Before each Step.fn | Employee OS (F.e) |
| 7 | Inside Step.fn body | Distributed across F.a Memory / F.b Content / F.c Sports / F.d HAI / F.e Employee OS (whichever plane's job step) |
| 8 | Celery `.apply_async` / `.delay()` | Distributed across all 8 planes |
| 9 | Celery task execution `@shared_task` | Distributed across all 8 planes |
| 10 | Model pre_save / pre_delete signals | Distributed (HAI has most; Memory + Content also) |
| 11 | Deliverable status transition | Content (F.b) |
| 12 | DirectMessage creation | Employee OS (F.e) via inter-employee messaging + Discord (F.h) via Discord messages |
| 13 | EventBus.publish() | Cross-plane (no direct binding) |
| 14 | LLM call — LLMEnforcer.check_budget | Distributed (Intelligence + workspace runners) |
| 15 | AgentRouter.route() | Employee OS (F.e) via agent routing |
| 16 | HumanAttentionItem decision | HAI (F.d) |
| 17 | Post-mission retrospective audit | Employee OS (F.e) |
| 18 | WebSocket consumer / channel-layer handler | API (F.g) via WebSocket |
| 19 | Fleet internal API / service-to-service ingress | API (F.g) via Fleet HMAC |
| 20 | Spider run boundary | Memory (F.a) via signal-aggregation + Sports (F.c) via sports spiders |

**Cross-reference count:** 20 boundaries map cleanly to plane columns. 3 boundaries (7, 8, 9) distribute across multiple planes (Step.fn body + Celery dispatch/execution can happen in any plane's job code).

### 17.4 Cross-reference to P3 §17.1 Plane Precedence Policy

P3 §17.1 canonical resolution order `KillSwitch > Autonomy > Authority(PROHIBITED) > Freeze > Authority(RECOMMEND) > Budget > HAI auto-approve` applies at every boundary that touches multiple planes.

Per-plane precedence-join verification:

| Plane | Boundaries touching multiple planes | Precedence composition status |
|---|---|---|
| Memory | Boundary 20 (Spider run + Governance freeze/safe_mode) | Verified (Explore 2 §5.1); precedence not implemented at Memory writers |
| Content | Boundary 11 (Deliverable status × row-level authority × KillSwitch) | Verified in P2 §17.1 row 11; Content PublishGate does not consume the composed order |
| Sports | Boundary 8/9 (arbitrage Celery dispatch × KillSwitch + Freeze + Budget) | Intentional deferral per S1903 Q3/Q5 |
| HAI | Boundary 16 (K > M > A > H) | Aspirational; currently only M evaluated per §14.3.1 verified |
| Employee OS | Boundary 4/5/6 (K > M > A) + Boundary 17 (K > M > A > F > B > H full stack read-only) | Aspirational; currently observation-only |
| Frontend | (no direct precedence; delegates) | N/A |
| API | Boundary 1 (K > M > A) + Boundary 19 (K > M > A + Fleet HMAC) | Boundary 1 currently M only; Boundary 19 Fleet HMAC operational |
| Discord | (no direct precedence; formal deferral) | N/A per S1903 Q8 |

**Precedence-composition observation:** Precedence order is DESIGNED at every multi-plane boundary but IMPLEMENTED at zero boundaries fully. Consistent with P2 D89 Option C. xx99 §5 canonical seam statement: precedence is design-complete, runtime-partial (only fail-closed auth at Boundary 1 + fail-open budget at Boundary 14 are wired today).

### 17.5 What §17 does NOT do

- **Does not audit adjacent-plane internal correctness** — per parent §5.4 scope precision + Rigby S1900 SIGN cycle 1 Q3(b) fold. Any finding that lands entirely inside an adjacent domain is out-of-scope.
- **Does not propose per-plane implementation ADRs** — per playbook §14.5 no-implementation rule; R-slot promotes to xx99 §8 T-tier queue for Chris-gated post-arc T-slot execution.
- **Does not re-open S1902 D-verdicts or S1903 Q-resolutions** — those Chris-ratified verdicts are inputs, not outputs, of P4.
- **Does not re-evaluate S1902 §14.2 KillSwitch classification** — P3 §14.1 already corrected (all 6 reads are management/audit/cleanup). P4 consumes the correction; xx99 §7 handles anchor-update batch.
- **Does not close inherited drifts from S1902 §14.4** — those remain queued for xx99 §7 anchor-update recommendations.
- **Does not verify runtime enforcement wire-up landing** — verifier confirms current HEAD state ONLY; post-T1/T2 execution status is Chris-gated post-arc.

## 18. Ownership Gaps

Per Explore 6 §Part D per-plane ownership assessment:

- **Memory (Group 1300) seam:** Cross-plane signal-aggregation read has NO seam-owner specified. Authority-plane owns the AuthorityLevel enum; Memory-arc owns signal-aggregation service. **Recommendation:** Authority-plane (Group 1900) should own the seam contract shape; Memory-arc (Group 1300) implements receiver. xx99 §5 should name the owner.

- **Content (Group 1600) seam:** Authority-plane owns AuthorityLevel enum; Content-arc owns PublishGate decision gate. Delegated decision: content review panel owns quality/novelty verdict per design deferral. **Recommendation:** Content-arc owns seam docs (what PublishGate does NOT do w.r.t. authority). Currently unowned.

- **Sports (Group 1500) seam:** Authority-plane owns enum. Sports-arc owns learning-surface + BettingOutcomeVerifier. Seam is read-only (Sports→Authority); no delegated decisions. Ownership is implicit (low friction because Sports does not gate on authority).

- **HAI (Group 1800) seam:** Authority-plane owns AuthorityLevel enum + P3 Q3/Q5 designed resolutions. HAI-arc owns HumanAttentionLifecycleService. Delegated-decision surface: HAI-arc chooses which items are low-risk (LOW_RISK_SOURCES). **Recommendation:** Authority-plane should own policy (what Freeze/RECOMMEND mean at seam); HAI-arc should implement. Currently policy ownership unclear — P3 deferred Q5 without explicit owner assignment.

- **Employee OS seam:** Authority-plane owns AuthorityLevel enum + enforce_authority_mode toggle semantics. Employee-OS arc owns MissionRunner. **Recommendation:** Authority-plane should own interface contract (what actor roles + authority signals are available to steps); Employee-OS should implement step-context carrier. Currently interface ownership is unspecified.

- **Frontend seam:** Authority-plane owns principal_user access-control gate. Frontend-arc owns tool-dispatcher gating policy. Delegated decision: tool-dispatcher owns allowed-tools per AssistantProfile. **Recommendation:** Frontend-arc should own "what to do on gate miss" policy. Currently silent-fail (line 691, 693) is unowned.

- **API seam:** Authority-plane owns AuthorityLevel enum. API-arc owns endpoint routing + LLMEnforcer budget gate. Delegated decision: API-arc decides which endpoints need budget-gating; authority-plane decides which need authority-level gating. **Recommendation:** Authority-plane should own budget-gate policy delegation (currently unclear if it's Authority-plane or API-arc responsibility).

- **Discord seam:** Authority-plane owns AuthorityLevel enum + P3 Q8 deferral. Discord-arc owns dispatcher + Cogs. Delegated decision surface: NONE (seam not operational). **Recommendation:** Authority-plane (P4 close) should name owner for Discord seam graduation as a T2 follow-on. Currently ownership UNCLEAR.

**Ownership gap count:** 4 UNSPECIFIED (Memory + Employee OS + Frontend + Discord) + 2 IMPLICIT (Content + Sports) + 2 PARTIALLY SPECIFIED (HAI + API). Aggregate: **0 planes have fully specified seam ownership.** xx99 §5 canonical seam statement should name owners.

## 19. Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows per playbook §11.2 §19 spec. Feeds the xx99 §8 T0/Gate + T1 + T2 + T3 tiered queue. Extends P1 §19 + P2 §19 + P3 §19 arc queues.

### 19.1 T0 / Gate — pre-xx99 blockers

- **R.AUTHORITY.CANONICAL-SEAM-STATEMENT (xx99 §5)** — P4 T0/Gate. Synthesize F1-F12 findings into a canonical statement of Authority Enforcement seam maturity for cross-arc consumers. Consumes §17.1 per-plane posture register + F10 fail-open codification + F9 F5 HYPOTHESIS DISPROVE evidence. **Consumed at xx99 §5 by definition.**

### 19.2 T1 — critical for correctness

- **R.AUTHORITY.ENFORCE-MODE-TOGGLE-FIELDS** (S1902 §19 T1, inherited) — Add `enforce_authority_mode: str = "warn"` to both `MissionRunnerConfig` and `AIEmployee` dataclasses. Backwards-compatible. Blocks entire two-tier composition contract runtime landing. **Highest T1 priority per F5 (§1) severity.**
- **R.AUTHORITY.ACTOR-KWARGS-CELERY** (S1901 §19 T1, inherited) — Explicit-param carrier via `apply_async(kwargs={"executor_actor": ..., "sponsor_actor": ..., "principal_user": ...})` at every HTTP-sourced Celery dispatch. Closes F6a for closeable sites; beat sites remain DEFAULT-CANONICAL.
- **R.AUTHORITY.ACTOR-STEP-CONTEXT** (S1901 §19 T1, inherited) — Extend Step frozen dataclass with actor context OR add `contextvars`-scoped read-only carrier per S1901 §7.2.2. Closes F6c.
- **R.AUTHORITY.VIOLATION-EVENT-SCHEMA** (S1902 §19 T1, inherited) — Define `AUTHORITY_CONTRACT_VIOLATED` label + detail dict shape.
- **R.AUTHORITY.RETROSPECTIVE-SCAN-TASK** (S1902 §19 T1, inherited).
- **R.AUTHORITY.OPTION-E-MIGRATION-TRIGGER** (S1902 §19 T1, inherited).
- **R.CONTENT.PUBLISHGATE-AUTHORITY-COMPOSITION** (P4 net-new T1) — Content-owned; xx99 §8 handoff to Group 1600 post-arc queue. Coordinate with HAI freeze interaction per S1903 Q5.

### 19.3 T2 — important for graduation

- **R.AUTHORITY.KILLSWITCH-DISPATCH-EXPANSION** (S1902 §19 T2, inherited; P3 §7.4.1 D94 reader spec now available) — 4 REQUIRED insertion boundaries per S1903 §7.4.1 D94 + 1 OPTIONAL at HAI decide per Rigby Q2 fold.
- **R.AUTHORITY.STEP-ACTION-DECLARATION** (S1902 §19 T2, inherited).
- **R.AUTHORITY.DISCORD-DISPATCH-ENFORCEMENT-INSTRUMENTATION** (S1903 §19 T2, inherited; P4 confirmed 3 prerequisites remain real blockers via Explore 3).
- **R.AUTHORITY.AUTO-APPROVE-FREEZE-GATE** (S1903 §19 T3 → **elevated to T2 by P4** per F4 severity) — Single-file 5-line change at `human_attention_lifecycle.py:240-245` per S1903 Q5. Closes HAI Freeze × auto-approve gap.
- **R.AUTHORITY.SEAM-BOUNDARY-TEST-COVERAGE** (P4 net-new T2) — 8-plane × 3-scenario minimum matrix. Closes F12 durable-across-P1-P2-P3-P4 TEST-GAP-CONFIRMED.
- **R.AUTHORITY.CROSS-PLANE-FAIL-OPEN-CODIFICATION** (P4 net-new T2) — **Implement codification per S1902 D89/F8 precedent + exceptions register** (Rigby SIGN cycle 1 Q4(c) fold: wording tighten — this is CODIFICATION of the already-ratified S1902 D89 fail-open default; it is NOT "decide new policy." If codification introduces new defaults not already covered by S1902 D89 or F8 (LLMEnforcer canonical fail-open precedent at `core/llm_enforcer.py:237-238`), those become a separate Chris-gated policy decision distinct from this T2 item).

### 19.4 T3 — nice-to-have follow-on

- **R.AUTHORITY.PER-LEVEL-BOUNDARY-BINDING** (S1902 §19 T3, inherited).
- **R.AUTHORITY.CLAUDE-MD-EMPLOYEE-COUNT-ANCHOR-UPDATE** (S1902 §19 T3, inherited).
- **R.AUTHORITY.LOW-RISK-SOURCES-EXPLICIT-AUTHORITY-TAGS** (S1903 §19 T3, inherited) — prerequisite: per-user authority resolution (Group 2000+ Event / Integration arc scope).
- **R.AUTHORITY.API-LAYER-AUTHORITY-INSTRUMENTATION** (P4 net-new T3) — Dependency: Symbol Mapping graduation for per-action-class registry.
- **R.MEMORY.SIGNAL-AGG-AUTHORITY-COUPLING-DOC** (P4 net-new T3) — Cross-arc handoff to Group 1300 post-arc queue. Document `signal_aggregation_service.py:211` cross-plane read OR propose formal contract.
- **R.SPORTS.ARBITRAGE-AUTHORITY-COMPOSITION** (P4 net-new T3) — Cross-arc handoff to Group 1500 post-arc queue. Coordinate with S1599 D59 posture-decision ADR.

### 19.5 Cross-arc T-slot handoffs

Per Explore 4 cross-arc T-slot table:

- **Group 1300 (Memory)** — 1 T3 item (signal-aggregation coupling doc)
- **Group 1500 (Sports)** — 1 T3 item (arbitrage × authority)
- **Group 1600 (Content)** — 1 T1 item (PublishGate × authority)
- **Group 1800 (HAI)** — 3 items (T2 Freeze × auto-approve + T2 K at auto-approve + T3 LOW_RISK_SOURCES)
- **Group 1900 (Authority — this arc post-close)** — 5 items (T0/Gate + T1 enforce_authority_mode field + T1 Celery kwargs + T1 Step context + T2 K enforcement reader)
- **Frontend (distributed)** — 0 items
- **API (distributed)** — 1 T3 item (view authority instrumentation)
- **Discord** — 1 T2 item (dispatch enforcement)
- **Group 2000+ Event Architecture** — Pre-existing R.EVENTS.HAI-EVENT-CONTRACT-CANDIDATES + F.SYMBOL-MAPPING-STATUS-VERIFICATION + F.PER-USER-AUTHORITY-MECHANISM per S1903 §19 inherited.

**Total T-slot handoffs from P4:** 1 T0/Gate + 7 T1 + 6 T2 + 6 T3 = **20 items** (net-new + inherited). Distributed across 7 arcs.

## 20. Appendix

### 20.1 Files inspected

- **Authority Enforcement research doc:**
  - `docs/research/domains/authority_enforcement/1900_authority_enforcement_domain_scoping.md`
  - `docs/research/domains/authority_enforcement/1901_authority_enforcement_cat_a_actor_role_propagation_design.md`
  - `docs/research/domains/authority_enforcement/1902_authority_enforcement_cat_b_authority_enforcement_design_decision.md`
  - `docs/research/domains/authority_enforcement/1903_authority_enforcement_cat_c_cross_plane_composition_design.md`
- **S1806 CONSOLIDATION precedent:**
  - `docs/research/domains/human_attention/1806_human_attention_cat_f_adjacent_separation_boundaries_child_audit.md`
- **Runtime seam interfaces (Explore verifier + post-Explore spot-checks):**
  - `core/llm_enforcer.py` (budget gate; fail-open pattern at :237-238, :263-264)
  - `core/employees/mission_runner.py` (Boundary 4 init :601-638 + Boundary 5 event :835-900; grep confirmed enforce_authority_mode does NOT exist)
  - `core/employees/jobs.py` (AIEmployee + JobContract frozen dataclass registry)
  - `core/models_governance.py:17+, :102+` (GovernanceState, KillSwitch)
  - `core/models_ops_runs.py` (OpsRun, OpsRunEvent)
  - `core/services/human_attention_lifecycle.py:63, :240-296, :243` (LOW_RISK_SOURCES + auto-approve gate + review_mode read verified)
  - `core/services/tool_dispatcher.py:685-720, :721-722` (Boundary 2 fail-open)
  - `core/services/signal_aggregation_service.py:211` (cross-plane GovernanceState read verified)
  - `core/auth_middleware.py:563-681` (Boundary 1)
  - `core/services/discord_bot.py` (per Explore 3; no authority reads)
  - `core/routing.py:51-100+` (WebSocket consumers)
  - `core/apps/content/views.py:46+` (Content REST endpoints)
  - `intelligence/ai_resume_generator.py:229, :484` (2 verified LLMEnforcer call sites)

### 20.2 Docs inspected

- `docs/PLATFORM_WHAT_IT_IS.md` (narrative anchor)
- `docs/PLATFORM_INVENTORY.md` (runtime anchor)
- `docs/EMPLOYEE_OS_PRIMITIVES.md`
- `docs/API_PATH_POLICY.md` (file exists; per Explore 5 scope)
- `docs/DISCORD_INTEGRATION.md` (file exists; per Explore 5 scope)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md`
- `docs/research/ARCHITECTURE_INDEX.md` (v62)
- `docs/research/OPEN_ARCS.md`
- `docs/research/platform_architecture_inventory.md`
- `docs/research/platform/cross_domain_integration_audit.md` (§2 + §3.3 + §3.8 + §4.2)
- `docs/research/domains/memory/1399_memory_canonical_summary.md`
- `docs/research/domains/sports/1599_sports_canonical_summary.md`
- `docs/research/domains/content/1699_content_canonical_summary.md`
- `docs/research/domains/human_attention/1899_human_attention_canonical_summary.md`
- Prior authority research suite: S1268-S1275 docs (governance_authority_evolution.md, symbol_mapping_architecture.md, symbol_mapping_option_selection_design.md, symbol_mapping_event_schema_design.md, actor_identity_attribution_architecture.md, authority_enforcement_design_space.md)

### 20.3 Grep patterns used

**Pre-Explore verifier (parent §5.4 assumption verification):**
- `enforce_authority_mode` across `core/employees/` (grep zero-match; CONFIRMS design-only)
- `GovernanceState.*mode|GovernanceState\.objects` across `core/services/signal_aggregation_service.py` (found `:211`)
- `review_mode|GovernanceState|KillSwitch|budget_freeze_active` across `core/services/human_attention_lifecycle.py` (found `:243`)
- `LOW_RISK_SOURCES` across `core/services/human_attention_lifecycle.py` (found `:63, :264`)

**Explore agent greps (per Explore reports):**
- `permission_classes` across `core/views_*.py` + adjacent-plane view files (Explore 3)
- `LLMEnforcer|enforce_real_ai` across `intelligence/` + `sports/` + `content/` + `apps/` (Explore 2)
- `test_.*authority.*seam|test_.*plane_seam|test_.*boundary_authority` across `core/tests/` (Explore 6; zero matches)
- `AUTHORITY_CONTRACT_OBSERVED|AUTHORITY_CONTRACT_VIOLATED` across `core/` (Explore 3)

### 20.4 Unresolved unknowns

Per Explore 4 + Explore 6:

1. **API_PATH_POLICY.md authority-seam coverage** — file exists; content not read.
2. **DISCORD_INTEGRATION.md detailed seam mapping** — file exists; content not read.
3. **`SystemConfiguration.budget_freeze_active` location** — SPECULATIVE at `core/models_system_configuration.py`; may live in `models_config.py` or similar. Not blocking P4 findings.
4. **HAI orchestration authority model** — when HAI auto-approve triggers `CustomWorkflow.execute_workflow()`, does execution context carry forward authority state? Or does `orchestration_engine.execute_workflow()` perform its own authority read? Not blocking F4 finding.
5. **`AssistantProfile` model location** — SPECULATIVE; not blocking Boundary 2 characterization.
6. **Discord T2 3-prerequisite unblock owner** — no owner named for any of the 3 prerequisites per S1903 Q8 formal deferral. xx99 §8 T-slot should name owner.
7. **Precise `AUTHORITY_CONTRACT_OBSERVED` consumer count** — Explore 3 found test suite only; production consumers unverified beyond spot-check.
8. **Full 209-view sweep for authority reads** — Explore 3 sampled 10+; complete sweep pending T3 R.AUTHORITY.API-LAYER-AUTHORITY-INSTRUMENTATION.

### 20.5 Conflicts between sources

- **Explore 1 initially classified Memory seam as `no_boundary`; Explore 4 identified implicit signal-aggregation coupling; post-Explore verifier confirmed direct read at `:211`.** Resolved: PERMEABLE-BROKEN posture per §14.3.2. F1 finding elevated to HIGH-structural.
- **Explore 4 cited HAI review_mode at `:240`; post-Explore verifier confirmed `:243`.** Resolved: line-precision drift caught + folded per §14.3.1.
- **Explore 2 flagged Employee OS `enforce_authority_mode` as SPECULATIVE.** Resolved: verifier grep CONFIRMS field does NOT exist at HEAD; queued as design-vs-runtime gap per §14.3.3.

### 20.6 Verifier-loop corrections (Rigby SIGN fold notes)

**Rigby SIGN cycle 1 SIGN-with-edits at Medium-High confidence (2026-07-04) on Group 1900 arc pin `pa-2bd1613ce2bd4a9c`.** Single-batch 4-question routing per S1801-S1806 arc-pin routing precedent + memory rule `feedback_rigby_sign_worker_instability_recovery.md` for 1600+ line audits.

**6 folds landed pre-commit:**

- **Fold 1 (Q1a Memory F1 framing tightening).** Rigby: "A direct read of `GovernanceState.mode` from a signal aggregation service is definitely cross-plane coupling, but whether it is a Memory seam violation depends on how you're defining 'Memory plane' in this Cat F doc." Fold: added explicit sentence in F1 clarifying that the signal-aggregation surface is not memory-subsystem-proper — classified under Memory only insofar as `signal_aggregation_service` is part of the stateful persistence/aggregation plane in Group 1300. Strict Memory-subsystem-proper interpretation would put this in a Signal/Intelligence ↔ Governance/Autonomy seam column instead. **Landed in §1 F1.**

- **Fold 2 (Q1b T3 tier hygiene rule).** Rigby: "Undocumented cross-plane reads that can change enforcement semantics → T2; reads that only throttle background work → T3." Fold: R.MEMORY.SIGNAL-AGG-AUTHORITY-COUPLING-DOC stays at T3 (throttle-only classification per Rigby's rule — `GovernanceState.mode` read at signal-aggregation gates background signal-processing jobs, not enforcement dispatch). Rule codified for future P4-equivalent audits. **Landed in §19.4 T3 entry.**

- **Fold 3 (Q2 F5 non-accusatory scheduling phrasing).** Rigby: "For Cat F consolidation, the key is: is the gap acceptable at P4 close under the arc contract? Given the Group 1900 arc is clearly sequencing: design now, execution later via T-tier, this should not be escalated to T0/Gate unless your Cat F doc claims 'Employee OS plane has enforcement boundary implemented.'" Fold: rephrased F5 language from "CONFIRMED via direct grep... zero-runtime" to "expected per staged rollout; tracked as T1/T2 execution items, not a contradiction of the P2/P3 ratified design." F5 stays as F5=systemic risk in RISK-SPLIT (§1 biggest architectural risk). Tier stays T1 (not T0/Gate). **Landed in §1 F5.**

- **Fold 4 (Q3(a) Sports STRUCTURAL-DROP parenthetical).** Rigby: "STRUCTURAL-DROP = excluded from cross-plane composition pending prerequisites; not a statement about correctness." Fold: added parenthetical to §17.1 Sports row clarifying intent. **Landed in §17.1 Sports row.**

- **Fold 5 (Q3(b) Frontend CLEAN verification note).** Rigby: "CLEAN (verified read-only): Frontend does NOT compute or enforce authority/autonomy; it only RENDERS server-resolved state (e.g., mode/freeze/status) and does not write `enforce_authority_mode` / governance controls. Verification basis: no frontend-initiated mutation endpoints or UI controls observed for authority/governance fields; if any UI can toggle these, Frontend becomes PERMEABLE-BROKEN until an explicit write-boundary contract exists." Fold: added exact verification-note text to §17.1 Frontend row. **Landed in §17.1 Frontend row.**

- **Fold 6 (Q4(c) CROSS-PLANE-FAIL-OPEN-CODIFICATION wording tighten).** Rigby: "Keep as T2 but mark as Chris-gated policy codification. Wording must be 'implement codification per S1902 D89/F8 precedent + exceptions register,' not 'decide policy.' If it introduces new defaults, it becomes a separate Chris decision." Fold: rewrote §19.3 T2 R.AUTHORITY.CROSS-PLANE-FAIL-OPEN-CODIFICATION entry to codification-of-D89 framing, with explicit caveat that new-defaults spawn separate Chris-gated decision. **Landed in §19.3 T2 entry.**

**No SIGN cycle 2 needed** per Rigby explicit statement: "No SIGN cycle 2 needed. With Q3(b)+Q4 folds landed pre-commit, you can route to Chris ratification off cycle 1."

**Q4 SIGN-clean sub-verdicts (folded pre-commit as documentation):**
- **Q4(a) T2 R.AUTHORITY.SEAM-BOUNDARY-TEST-COVERAGE** — T2 correct. "Governance hygiene, not just local refactor. Promote only if readers exist; otherwise keep as T2 'pre-implementation safety net.'"
- **Q4(b) R.AUTHORITY.AUTO-APPROVE-FREEZE-GATE T3→T2 elevation** — "Right call, not overreach. Small change, high downside prevention; 'freeze means no accelerated execution' is safety-aligned."

### 20.7 D48 arm state — Rigby SIGN worker instability tracking

**D48 36th arm turn 1 CLEAN** (2026-07-04). Rigby SIGN cycle 1 returned SIGN-with-edits at Medium-High confidence with 6 substantive folds enumerated within single-batch 4-question response. No worker stall, no generic "issue processing" error, no pin-poisoning symptoms. Response quality high (specific line-level fold text for each Q + clarifying edits). Behavioral criteria for CLEAN arm turn 1 satisfied per memory rule `feedback_rigby_sign_worker_instability_recovery.md`.

**31-consecutive-fully-clean-arms sub-pattern EXTENDED** (30 → 31) per single-batch-4-question criterion. MC-2 CODIFICATION-CONFIRMED milestone extended from 30 (S1903 close) to 31 (S1904 close). Aggregate arm state under Research OS post-formal-installation: 36 arms total across S1268-S1904 range; 31 consecutive fully-clean arms as of S1904 close.

**Rigby routing pattern arc-pin durable-by-seventh-application** under Group 1900 (P1 = 4th S1901, P2 = 5th S1902, P3 = 6th S1903, P4 = 7th S1904; Group 1900 4-child arc + xx99 will complete at 8th application). MC-4 CODIFICATION-READY promotion path stalls under 4-child arcs (does not observe sixth-application under 6-child arcs criterion per S1899 close established rule). Group 1900 does NOT constitute the milestone promotion arc; MC-4 promotion deferred to future 6-child arc.

### 20.8 Playbook §11.2 20-section child template FOURTEENTH-consecutive application + §16 CONSOLIDATION shape SECOND-consecutive application

- Playbook §11.2 20-section child audit template: 14th consecutive application overall (extending S1899 close 12-application tally: S1801-S1806 = 6 + S1901-S1903 = 3 = 9 through Group 1900 P3; S1904 = 10th under Research OS post-formal-installation? — SIGN cycle 1 clarification recommended. Meta-methodology datapoint per S1806 §20.11 running tally.)
- §16 CONSOLIDATION shape: 2nd consecutive application under Research OS (first at S1806 Group 1800 Cat F; second at S1904 Group 1900 P4 Cat F).
- Adaptations from S1806 CONSOLIDATION shape: §3 divided into 8 sub-slots (up from S1806's 5) per parent §5.4 8-plane taxonomy; §7 explicit per-plane propagation-contract touchpoint map (12-column seam matrix); §17.1 per-plane separation-boundary posture register replaces S1806 §17 duplicate-service inventory (Group 1900 has zero dup services per F9 DISPROVE).

### 20.9 SIGN cycle 1 record

**Cycle 1 verdict:** SIGN-with-edits at Medium-High confidence (2026-07-04). Full fold enumeration at §20.6. Zero NEEDS-MORE, zero contradictions with P1/P2/P3 ratified decisions. SIGN cycle 2 SKIPPED per Rigby explicit statement ("No SIGN cycle 2 needed. With Q3(b)+Q4 folds landed pre-commit, you can route to Chris ratification off cycle 1").

**Rigby routing arc pin:** `pa-2bd1613ce2bd4a9c` (Group 1900 arc pin preserved from S1900 open per arc-pin-durable-by-seventh-application under Group 1900). SEVENTH-consecutive routing session on this pin; no rotation required.

### 20.10 Meta-methodology observations (candidates for xx99 §10 codification)

**Rigby T-tier hygiene rule (Q1b fold-derived).** "Undocumented cross-plane reads that CAN change enforcement semantics → T2; reads that only throttle background work → T3." This is a NEW general classification rule for Cat F consolidation seam audits. Candidate for playbook v3 §16 CONSOLIDATION shape codification. Applicable to any future arc that consolidates cross-plane authority-adjacent seams (e.g., a hypothetical Group 2000 Event Architecture Cat F consolidation).

**CONSOLIDATION-shape non-accusatory framing rule (Q2 fold-derived).** For staged-rollout arc contracts (design-now, execution-later), CONSOLIDATION §14 KNOWN DRIFT for design-vs-runtime gaps should be framed as "expected per staged rollout; tracked as T-tier execution items, not a contradiction of the ratified design" — NOT as "CONFIRMED via direct grep; zero-runtime." Non-accusatory framing preserves the arc-contract shape without downgrading verifier discipline. Candidate for playbook v3 §14 evidence-rules refinement.

**F5 HYPOTHESIS DISPROVE 6-consecutive tally under F5-primitive-testing arc-close discipline** (S1802 + S1803 + S1804 + S1805 + S1904 = 5 disprove; S1806 Cat F.d partial = 1 pass). Aggregate cross-arc: 1 pass / 5 disprove. Meta-methodology datapoint per S1806 §20.7 codification-ready pattern. Candidate for playbook v3 §14 F5-arc-close-consolidation codification: "F5 HYPOTHESIS-testing at arc-close consolidation surfaces DISPROVE-dominant across authority-adjacent domains, suggesting authority primitives naturally cluster canonically rather than fragment into per-plane duplicates."

**STRUCTURAL-DROP semantics clarification (Q3(a) fold-derived).** For CONSOLIDATION-shape posture register, STRUCTURAL-DROP posture MUST include explicit "excluded from cross-plane composition pending prerequisites; NOT a statement about correctness" caveat to prevent misreading by future arcs. Candidate for playbook v3 §16 CONSOLIDATION shape posture-vocabulary standardization.

**CLEAN posture write-boundary contract requirement (Q3(b) fold-derived).** For CONSOLIDATION-shape posture register, CLEAN posture MUST include explicit verification-basis statement + "PERMEABLE-BROKEN escape hatch if write-boundary contract absent" caveat. Prevents future arcs from misreading "genuinely separated" as "immune to future coupling." Candidate for playbook v3 §16 CONSOLIDATION shape posture-vocabulary standardization.
