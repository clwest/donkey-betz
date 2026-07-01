---
session: 1401
status: closed (S1401 Child A Opportunity Discovery + Scoring audit shipped; Rigby SIGN-clean cycle 2 High confidence after 4-fold cycle 1 fold — 2 must-fix + 2 nice-to-have; Chris commit-gated via "commit it"; ARCHITECTURE_INDEX v19 → v20 bump landed same-commit; ARC pin `pa-34d43795e1b24bd3` retained through S1401 per D31; isolation pin `pa-16d8b24d30e7a7d8` retired at close per playbook §15)
date: 2026-07-01
arc: Research Group 1400 (Revenue / Outreach / Engagement) — Child A: Opportunity Discovery + Scoring. **First Group 1400 child audit under Chris's Phase 0 methodology** (S1400 was arc-opening scoping). Playbook §11.2 20-section child audit template + §13 6-parallel-Explore sweep + parent-Claude verifier-loop pre-SIGN discipline + Rigby full-SIGN routing per §15 stage table.
---

# Session 1401 — Group 1400 Revenue Child A (Opportunity Discovery + Scoring Audit)

## What shipped

- **Child audit** at `docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md` (6,500+ words after folds; 20 sections per playbook §11.2 template; all 28 canonical Q's + all 6 parent §12.1 Category A F.iii Q's answered; all 15 inherited findings cited not rediscovered; `status: draft` at close → `active` on Chris merge; `authority: research`; `category: child_audit`; `sign_status: SIGN-clean cycle 2 High confidence`).
- **ARCHITECTURE_INDEX v19 → v20 bump** landed same-commit: added §1.22 for S1400 parent scoping (was omitted at S1400 open; retroactively added here) + §1.23 for S1401 child audit + §8 timeline S1400 + S1401 rows + frontmatter `last_verified` + `owner` update + comprehensive v20 change note.
- **`OPEN_ARCS.md` rotation** — Group 1400 In-progress row current-child field advanced from "S1401 queued next" → "S1401 SIGN-clean cycle 2 (commit-gated) + S1402 queued next"; frontmatter `last_updated` updated with S1401 close reconciliation; §Recent reconciliations 2026-07-01 (S1401 close) entry added.
- **`00-START-NEXT-SESSION.md` rotation** — S1402 Child B (Outreach Composition + Delivery) mission spec + D32/D33 launch decisions surfaced + first-action punch list + reference block updated.
- **This handoff** at `docs/handoffs/SESSION_1401_REVENUE_OPPORTUNITY_DISCOVERY_SCORING.md`.

## Chris decisions Chris-locked this session (2)

| Decision | Verdict | Ratification path |
|---|---|---|
| D30 | Sequential launch cadence — Chris ratified default lean (matches S1301–S1305 rhythm from Group 1300) | Chris "agree all" 2026-07-01 |
| D31 | Retain arc pin `pa-34d43795e1b24bd3` — Chris ratified default lean (matches S1301–S1399 retention rhythm; kickoff-fresh state = no rotation reason) | Chris "agree all" 2026-07-01 |

Chris commit-gate ratified via "commit it" 2026-07-01.

## Rigby SIGN cycles

**Full SIGN cycle 1 (child audit doc v1, ~5,500 words):**

- **Fresh isolation pin:** `pa-16d8b24d30e7a7d8` (generated via `python3 -c "import secrets; print(f'pa-{secrets.token_hex(8)}')"` per playbook §15 rule).
- **Verdict:** SIGN-with-edits at **High confidence**.
- **Rigby's independent spot-check verifications** (all 4 primary citations grep-verified via `repo_tool.search` + `repo_tool.read_file`):
  1. Sports lane `intelligence/sports_opportunity_generator.py:83` → `OpportunityTracking.objects.create(...)` CONFIRMED.
  2. Dual opportunity representation `intelligence_engine.get_current_opportunities()` — **broadened finding from 1 to 5 consumer sites** in `consumers_base.py` (lines 1696, 1730, 2541, 2557, 2597). This changed R1 from "single-consumer local bug" to "arc-wide contract question."
  3. Celery duplicate `settings.py:1277` (`long_running`) + `:1484` (`content`) CONFIRMED.
  4. OPPORTUNITY_SCORED registry `event_bus.py:25` stream def + `event_bus.py:581` Event assembly + `event_handlers.py:536` `create_validation_worker` subscription CONFIRMED. She could NOT independently verify the handler registry mapping in that spot-check scope; I re-verified independently at `event_handlers.py:48` (`self.register('opportunity_scored', handle_opportunity_scored_event)`).
- **Fold-summary:** 4 folds — 2 must-fix + 2 nice-to-have:
  - **Fold M1 (must-fix, §1 + §7.3 + §9.1 D5 + §14 D5 + §17.2)** — sports lane wording clarification: S1274 §2.4 line 270 MISSING classification REMAINS ACCURATE for mainline `Opportunity`; refinement is "separate lane" framing (sports IS persisted in `OpportunityTracking`; cross-wire to mainline is what's missing). Prevents readers from misreading "separate lane" as "integration solved."
  - **Fold M2 (must-fix, §10.1)** — EventBus overreach correction:
    - Added handler-to-event-type registration citation `event_handlers.py:48` (`self.register('opportunity_scored', handle_opportunity_scored_event)`).
    - Added payload composition citation `event_bus.py:581` (Event assembly with `stream=EventStream.OPPORTUNITY_SCORED`).
    - **Corrected handler action from v1's "routes confidence 50-85% → HITL VALIDATION_REQUIRED event"** to DETECTS + LOGS only per `event_handlers.py:186-188` inline comment ("The HITL service will have already created the validation request. This handler is for analytics and notifications.").
    - Downgraded `scoring_workers` + `analytics_workers` group claims from S1274 §6.2 baseline to CANDIDATE (not re-verified in this audit); only `create_validation_worker` at `event_handlers.py:521+` region verified this session.
  - **Fold NH #3 (nice-to-have, §15 T5)** — operational consequence note on `content` vs `long_running` queue mismatch: different concurrency limits, memory profiles, and workload assumptions per `settings.py:1268-1273` comments. A 100-item ML scoring pass under `content` semantics may cause latency regression, OR may be intentional post-Session-1063 optimization. Follow-on PR should verify via git blame.
  - **Fold NH #4 (nice-to-have, §19 R1+R4 umbrella collapse)** — R1 (F1 provenance drift) + R4 (dual opportunity representation) merged into single umbrella R1 "Dual-representation + provenance contract" with prerequisite sub-task R1.0 = "identify origin/lifecycle of `intelligence_engine.get_current_opportunities()`." Rigby rationale: "if the WS scanner path is in-memory and readers ignore provenance, you cannot reason globally about opportunity truth/provenance." Subsequent R-numbers shifted -1; added new R8 for T5 Celery route cleanup (Rigby: "important-but-contained unless proven to cause starvation/latency regressions").
  - **Bonus fold (§14 D6):** Rigby cycle 1 grep broadened dual-representation finding — v1 named 1 consumer site (`consumers_base.py:2541`); Rigby found 5 sites (1696, 1730, 2541, 2557, 2597). §14 D6 + §1 exec summary updated to reflect the broader scope.

**Full SIGN cycle 2 (post-fold summary):**

- **Verdict:** SIGN-clean at **High confidence**. Cycle 2 unnecessary per Rigby's explicit statement: "SIGN-clean (cycle 2 unnecessary; ship to Chris commit-gate). No remaining blockers based on your fold summary."
- **Isolation pin `pa-16d8b24d30e7a7d8` retired at S1401 close** per playbook §15 (Rigby SIGN cycle 2 explicit: "You can retire the S1401 isolation pin at close per playbook §15.").

## Parent-Claude verifier-loop pre-SIGN corrections (5)

Applied BEFORE Rigby SIGN cycle 1 launched:

1. **Agent 3 beat-schedule negative claim downgraded to UNKNOWN.** Agent 3 said `score_opportunities_from_spider_data` NOT SCHEDULED — on-demand only. Cross-check of `docs/WIREMAP.md:170`, `docs/handoffs/SESSION_872_COMPLETE.md:147`, `docs/archive/sessions/SESSION_223_OPPORTUNITY_ENGINE.md:124` all state the task IS scheduled hourly. Agent 3's negative claim downgraded to UNKNOWN pending Rigby-side `PeriodicTask` row inspection (source tree doesn't carry django-celery-beat DB state). §14 D4 + §19 R4.
2. **Agent 6 orchestrator-overlap claim resolved as COMPLEMENTARY via Agent 2 direct read.** Agent 6 flagged `OpportunityPipelineOrchestrator` (1,848 LOC) and `OpportunityExecutionPipeline` (541 LOC) as duplication candidate. Agent 2's direct code read showed complementary roles: Orchestrator = transform Dict → Dict (5-stage agent routing); ExecutionPipeline = materialize Opportunity instance → PartnershipProject + CustomWorkflow. Different signatures, different downstream side effects. §17.3.
3. **Agent 3 EventBus publisher line clarified.** Agent 3 named `:282, :480`; direct read of `scoring_dispatcher.py:41` confirms primary invocation at line 41 (called from `_publish_scoring_event` helper at line 21). Lines 282, 480 are S1274 §6.2 higher-level caller-of-helper lines — both correct but naming different things. Audit uses line 41 as the load-bearing citation. §14 verifier-loop record.
4. **NEW load-bearing finding surfaced: dual opportunity representation drift.** Direct read of `consumers_base.py:2540` revealed `OpportunityScannerConsumer` streams from `intelligence.realtime_engine.intelligence_engine.get_current_opportunities()` — an in-memory realtime source distinct from persistent Django `Opportunity`. This was NOT flagged by any sub-agent as a load-bearing finding. Rigby SIGN cycle 1 grep then broadened it from 1 → 5 consumer sites. §14 D6 + §19 R1 umbrella.
5. **NEW debt finding surfaced: Celery queue-routing duplicate.** Direct grep of `core/settings.py` found `score_opportunities_from_spider_data` defined TWICE in `task_routes` at line 1277 (`long_running`) + line 1484 (`content`). Later definition wins → effective queue `content`. Silent drift-prone bug — no runtime error. §15 T5.

## Load-bearing findings

1. **Sports lane resolved (§12.1 Q6 + §14 D5 + §17.2):** `intelligence/sports_opportunity_generator.py:83` writes `OpportunityTracking.objects.create(...)` — a separate model in the `intelligence` app label, NOT mainline `Opportunity`. S1274 §2.4 line 270 MISSING classification REMAINS ACCURATE for mainline; refinement is "separate lane" wording rather than "missing implementation."
2. **NEW dual opportunity representation drift (§14 D6 + §19 R1 umbrella):** 5 consumer sites in `consumers_base.py` (lines 1696, 1730, 2541, 2557, 2597) stream from `intelligence_engine.get_current_opportunities()` in-memory realtime source, NOT persistent Django `Opportunity`. Synchronization contract UNKNOWN. Rigby SIGN cycle 1 grep broadened finding from 1 → 5 sites.
3. **F1 provenance-filter drift CANDIDATE HIGH (§14 D8 + §15 T4):** writers tag `source` + `metadata['spider_source']` inconsistently across producers (spider connector complete; agents + PA-tool paths sparse); readers (`OpportunityExecutionPipeline`, `OpportunityScannerConsumer`, `OpportunityDraftGenerator`) do not filter on provenance. Per S1399 §4 F1 methodology.
4. **F3 Redis-only durability CANDIDATE HIGH (§15 T3):** `intelligence/spider_opportunity_connector.py` uses async Redis (`aioredis.from_url()` + `cache_timeout=300`), no DB fallback. If Redis expires before DB write, opportunity data lost silently. Per S1399 §4 F3 methodology.
5. **F2 orphan-write cluster CANDIDATE HIGH (§15 T2):** 10-variant Opportunity family + Session Pre-38 partnership_* fields (partnership_mode, ai_contribution_potential, collaboration_feasibility, partnership_workflow, required_human_skills, ai_capabilities_match, estimated_solo_hours, estimated_partnership_hours, time_multiplier). Requires sibling verifier-loop per S1399 F4 before hardening. Per S1399 §4 F2 methodology.
6. **OpportunityPipelineOrchestrator vs OpportunityExecutionPipeline COMPLEMENTARY, not overlapping (§17.3):** Orchestrator = transform Dict → Dict (5-stage agent routing, 1,848 LOC); ExecutionPipeline = materialize Opportunity → PartnershipProject + CustomWorkflow (541 LOC). Not consolidation candidates.
7. **NEW debt T5 (§15 T5):** `core/settings.py` `task_routes` defines `score_opportunities_from_spider_data` TWICE — line 1277 (`long_running`) + line 1484 (`content`); later wins → effective queue `content`. Follow-on cleanup PR needed.
8. **Ownership gap CONFIRMED (§18 + S1274 §14 #36 inherited):** no JobContract wiring for `OpportunityScoringAgent` or `OpportunityPipelineAgent`; no dedicated Category A beat queue; no CODEOWNERS-style artifact. Deferred to Child E aggregate per D28.
9. **Maturity WORKING** (S1273 §3.32 baseline preserved; no upgrade or downgrade for Category A).
10. **Research coverage LIGHT** (matches parent §11.3; no CANONICAL topic doc; upgrade candidate at S1499 xx99).

## Category A F.iii questions all 6 answered (§20.7)

1. **What IS an Opportunity?** Mainline `Opportunity` at `core/models_unified_system.py:1201` with 27 core fields + 10-variant family enumerated at §4.
2. **Who produces Opportunities?** 4 confirmed writers of mainline `Opportunity.objects.create(...)` — spider connector (STRONG); OpportunityScoringAgent (WEAK NEW); td_handlers_agents PA tool (WEAK NEW); income_action_service PA tool (WEAK NEW). Category F Income/Jobs surface handoff to S1406 for full inventory.
3. **How does scoring flow through OpportunityScoringAgent + OpportunityPipelineAgent + ML categorizer?** §7 Flows α + β + δ enumerated.
4. **What does OPPORTUNITY_SCORED event carry + who consumes?** §10.1 fully cited (handler registry `event_handlers.py:48`; worker subscription `event_handlers.py:536`; payload composition `event_bus.py:581`).
5. **What is OpportunityScannerConsumer for?** READ-ONLY WebSocket listener streaming from `intelligence_engine.get_current_opportunities()` in-memory source (NOT persistent `Opportunity` model). §6.2 + §7.5 + §14 D6.
6. **Does sports_opportunity_generator produce into mainline Opportunity or a separate lane?** SEPARATE LANE — writes `OpportunityTracking` (intelligence app), not mainline. §7.3 + §9.1 D5.

## Follow-on queue (next-session actionable)

- **S1402 Child B** — Outreach Composition + Delivery audit per parent §12.1 Category B questions + playbook §11.2 20-section template + §13 6-parallel-Explore sweep on 6 evidence surfaces (see `00-START-NEXT-SESSION.md` for the surfaces).
- **D32 launch cadence** — sequential (default) vs parallel-with-S1403. Ratifies at S1402 open.
- **D33 arc pin retention** — retain `pa-34d43795e1b24bd3` (default) vs mint fresh. Ratifies at S1402 open.
- **Post-arc design-preparation:** R1 umbrella "Dual-representation + provenance contract" ADR (highest severity follow-on; prerequisite R1.0 = identify origin/lifecycle of `intelligence_engine.get_current_opportunities()`).
- **Immediate Rigby probes** (S1402 open or standalone): R2 scoring rate telemetry (`OpportunityScore` count vs `Opportunity` count + `CeleryTaskEvent` history for `score_opportunities_from_spider_data`); R4 PeriodicTask row verification; R5 `OpportunityAIAnalyzer` liveness (`LLMCallEvent` grep); R7 `OPPORTUNITY_CREATED` stream disposition.
- **Follow-on cleanup PR** (design-preparation, not scoped to Group 1400): R8 T5 Celery route duplicate dedupe (`settings.py:1277` vs `:1484`).

## Load-bearing methodology outputs of this session

- **Parent-Claude verifier-loop pre-SIGN discipline** — 5 sub-agent claims corrected BEFORE Rigby SIGN. Pattern: catch evidence overreach parent-side first so Rigby SIGN cycles focus on substantive edges, not evidence corrections. Extends S1303/S1304 methodology (which caught Agent-6 overreaches BEFORE Rigby) — S1401 formalizes as first-class pattern for Group 1400 remaining children.
- **Rigby-side grep-expansion of dual-representation finding** — S1401 v1 named 1 consumer site (`consumers_base.py:2541`); Rigby cycle 1 grep found 5 sites (1696, 1730, 2541, 2557, 2597). Follow-on pattern for future audits: expect Rigby to broaden hypothesis scope when the finding is a search-pattern class (not a single-instance bug). This changed §19 R1 from "single-consumer local bug" to "arc-wide contract question."
- **S1274 baseline preservation with wording refinement** — S1401 M1 fold established the "S1274 baseline holds; wording refinement" pattern for future child audits inheriting S1274 findings. When a S1274 MISSING classification is materially confirmed at the mainline layer but sports/adjacent-lane presence is also confirmed, the correct move is "MISSING remains accurate for mainline; refinement is separate lane" rather than "reclassification" or "upgrade."

## What "start Group 1500" (or S1402 Child B) inherits from this session

- **Parent-Claude verifier-loop discipline** as required pre-SIGN step for all Group 1400 remaining children (S1402–S1406). Sub-agent claims must be spot-checked at file:line before Rigby SIGN.
- **Rigby-side hypothesis-expansion expectation** when the finding is a search-pattern class (F1 provenance drift, F2 orphan-write, F3 Redis-only durability, dual representation). Draft the finding with "at least N sites" language and expect Rigby to broaden it.
- **S1274 baseline preservation pattern** for future child audits inheriting S1274 classifications.
- **R1 umbrella "Dual-representation + provenance contract"** as arc-wide follow-on ADR. Group 1400 children S1402–S1406 may contribute additional evidence to the umbrella (each category has its own read/write consumer sites).

## Session close criteria — met

- [x] Child audit drafted per playbook §11.2 20-section template + Chris's Phase 0 methodology inheritance
- [x] All 28 canonical questions answered (§20.6)
- [x] All 6 parent §12.1 Category A F.iii questions answered explicitly (§20.7)
- [x] All 15 inherited findings cited, not rediscovered (§20.8)
- [x] Chris-facing decisions (D30 D31) locked via "agree all"
- [x] Rigby full SIGN cycles 1 + 2 completed — SIGN-clean cycle 2 High confidence
- [x] Fresh isolation pin `pa-16d8b24d30e7a7d8` minted + retired at close per playbook §15
- [x] `ARCHITECTURE_INDEX.md` v19 → v20 bumped (added §1.22 S1400 + §1.23 S1401 + timeline rows S1400 + S1401)
- [x] `OPEN_ARCS.md` rotated (In-progress row current-child field advanced + reconciliation note)
- [x] `00-START-NEXT-SESSION.md` rotated (S1402 mission spec + D32/D33 + first-action punch list)
- [x] Session handoff shipped (this doc)
- [x] Chris commit-gate ratified ("commit it" 2026-07-01)
- [ ] Docs cascade after PR merge (build_docs_index → build_rag_corpus → sync_docs_index_to_documents → embed_documents + build_docs_provenance) per memory rule `feedback_docs_cascade_at_every_close.md`

## Playbook §17 graduation criteria — single-audit criteria (this audit)

Applies to S1401 Child A audit itself (per playbook §17 for-single-audit-groups; Group 1400 as a whole graduates at S1499 close per for-parent-with-children-groups):

- [x] Audit file exists at `docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md`
- [ ] Frontmatter carries `status: active` + `authority: research` — **currently `draft`; flips at Chris merge**
- [x] `verifier_loop` records Rigby SIGN status — SIGN-clean cycle 2 High confidence after 4-fold cycle 1
- [x] All 28 canonical questions answered — with cite, reference, or explicit UNKNOWN (§20.6 checklist)
- [ ] Doc committed to the branch — **pending Chris merge; commit landing this session**
- [x] `ARCHITECTURE_INDEX.md` bumped: v19 → v20 with §1.23 row + §8 timeline row (+ §1.22 for S1400 retroactively)
- [x] Follow-on research queue captured in §19 of the audit (8 items ranked)
