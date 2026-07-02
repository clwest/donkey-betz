---
title: "S1502 Sports Prediction & Analytics Agents — Child Audit (Category B / P2 under Group 1500)"
status: active (child audit — second child of Group 1500 Sports/DBAO/Intelligence arc; drafted 2026-07-02; Rigby Full SIGN cycle 1 SIGN-with-edits at Medium confidence 2026-07-02 on fresh isolation pin `pa-64c019d7e6685d31` → F1-F12 folds landed at commit-time → Rigby Full SIGN cycle 2 SIGN-clean at High confidence 2026-07-02; cycle 1 prediction accurate; D48 preemptive stability-probe gate 5th arm — clean stability probe + zero worker-instability across 4 substantive SIGN batches (cycle 1 batches 1-3 + cycle 2 verdict) — CODIFICATION-READY continuation of S1405+S1406+S1499+S1501 4-arc pattern → 5-arc pattern for xx99 §10.2 playbook v3 §15 recommendation)
authority: child-audit for Category B per parent §5 sequence + second sibling to apply the pre-brief mini-schema per D62 = (a) propagate upfront (Chris-ratified S1501 open 2026-07-01)
category: child_audit
session: 1502
date: 2026-07-02
domain_slug: sports
subdomain_category: B
research_group: 1500
parent_doc: docs/research/domains/sports/1500_sports_domain_scoping.md
authors: Claude Code (Chris directed via short command "Continue research group 1500: Category B")
supersedes: none
related:
  - docs/research/domains/sports/1500_sports_domain_scoping.md                       # parent scoping — arc-open + Phase 0 F.i/F.ii/F.iii second application UNCHANGED per D58 + candidate subdomain taxonomy A-F + D62 = (a) pre-brief mini-schema propagation ratification
  - docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md   # Cat A sibling audit — §2.1 Cat A contract statement is Cat B's load-bearing input
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                        # §9 28 canonical questions + §11.2 20-section child template + §13 6-parallel-sweep + §14 evidence rules + §15 SIGN
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md                               # OS bootstrap + child-audit contract §8
  - docs/research/OPEN_ARCS.md                                                       # arc manifest — Group 1500 In-progress
  - docs/research/platform_architecture_inventory.md §3.10                           # S1273 Sports Intelligence / Betting Pipeline LIGHT baseline
  - docs/research/platform/cross_domain_integration_audit.md §14 Finding #6          # S1274 sports_odds not a SignalCluster.pattern_type HIGH — extends to Cat B agent-consumer side
  - docs/research/platform/cross_domain_integration_audit.md §12.3                   # S1274 v2 P1 island-vs-integrated posture decision point (framing owed to Cat F evidence plan)
  - docs/PLATFORM_INVENTORY.md                                                       # runtime inventory anchor (regenerable) — Markets agents inventory row
  - docs/PLATFORM_WHAT_IT_IS.md                                                      # narrative anchor — SportsOddsAnalyst listed in Markets category
  - docs/topics/agent-system.md                                                      # existing topic doc — Intelligence Desks table lists SportsBettingCoordinator (5 agents)
  - docs/narratives/SPORTS_MONETIZATION_ML.md                                        # existing narrative — GamePredictor + SharpActionDetector deep dives; does NOT name arbitrage_detector / sports_odds_analyst
scope: audit Category B ONLY — sports prediction & analytics agents (`sports_odds_analyst` + `game_predictor` + `sharp_action_detector` + `arbitrage_detector`) + orchestrator (`SportsBettingCoordinator`) + Cat B PA tool + Cat B Discord `/arb` + Cat B REST/WS surface; boundary is agent-consumption of Cat A data → production of predictions / signals / arbitrage / analytics
non_goals:
  - Category A — sports odds ingestion (S1501 owns; §2.1 Cat A contract statement is our load-bearing input, not our audit surface)
  - Category C — wager tracking / outcome verification (PlacedWager, PlacedWagerLeg, BettingStats, BettingOutcomeVerifier — S1503 owns; noted only where Cat B → Cat C bridge is missing)
  - Category D — betting content pipeline (generate_daily_betting_brief consumers, SportsContentContextBuilder, Discord `/odds` — S1504 owns; noted only where coordinator brief flows into D)
  - Category E — frontend sports surface (BettingPage 9 tabs, /betting route — S1505 owns; noted only where Cat B produces the payload E renders)
  - Category F — cross-domain integration lens + posture decision framing + evidence plan (S1506 owns; consumes P1-P5)
  - `LineMovementAnalyzer` and `PredictionMarketAnalyst` deep audit — coordinator calls both but parent §3.B explicitly names 4 agents + coordinator. Both flagged in §16 as scope-boundary observations; audits deferred to xx99 (S1599) reconciliation.
  - actually deciding the S1274 §12.3 island-vs-integrated posture (Chris-gated, post-arc — see D59 refinement)
  - implementation proposals (this is research; PRs come later per playbook §14 "no implementation during research")
  - external companion project scope (`BILLING_MONETIZATION_SYSTEM.md` from ai-content-studio — S1400 anti-scope pattern inherited)
  - Odds API vendor selection (product decision, not architecture)
  - mobile / React Native betting-app scope
  - bankroll / staking strategy research (parent §7 anti-scope #9 — Sports scope-trap; Cat B may inventory whether such logic exists, no deeper research)
owner: claude (Chris ratified S1502 P2 open via "Continue research group 1500: Category B" short command 2026-07-02)
verifier_loop: Parent-Claude verifier-loop applied on 7 load-bearing claims prior to Rigby SIGN — see §20.4. Rigby Full SIGN cycle 1 SIGN-with-edits at Medium confidence 2026-07-02 on fresh isolation pin `pa-64c019d7e6685d31` (D48 5th arm — clean stability probe + zero worker-instability across 3 substantive SIGN batches; D48 CODIFICATION-READY for playbook v3 per S1405+S1406+S1499+S1501+S1502 5-arc pattern). Post-cycle-1 additional verifier-loop applied on 2 SIGN-flagged UNKNOWNs (SportsBettingBrief model existence + REST endpoint router registration) — both resolved via targeted grep. **F1-F12 folds landed at commit-time** (F1 §7.1 explicit call-chain block; F2 §1 Finding 5 SignalCluster reframe to posture-decision-pending per S1274 §12.3 precedent; F3 §1 Finding 6 outcome-feedback-loop reframe to posture-decision-pending; F4 §1 Finding 7 Memory Domain bridge reframe to posture-decision-pending; F5 §1 Finding 4 kept as DRIFT per Rigby recommendation; F6 §15 fixture-identity reconciliation added as debt item; F7 §1 operational-vs-architectural risk axis added; F8 §1 Finding 9 continue-on-error reframed as intentional-or-drift-needing-contract per S1501 F6 precedent; F9 §1 Finding 1 + §13.2 Session-1205 language softened; F10 §4.8 SportsBettingBrief added + §20.3 unknown removed; F11 §3.3 + §20.2 router registration verified; F12 §5.1 direct-consume filter cite tightened). Cycle 2 SIGN-clean at higher confidence predicted after folds land. **Do-not-regress notes for PR:** keep §2.1 Cat B contract statement (§2.1 is Rigby's cycle-1 "missing area" ask — she scanned only titles; the section is present as F7-analog of S1501); preserve posture-decision-pending framing throughout §1 Findings 5-7 (do not backslide to "MISSING integration" defect language); preserve F1 explicit call-chain block in §7.1; preserve F6 fixture-identity as explicit debt item.
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/platform_architecture_inventory.md
  - docs/research/platform/cross_domain_integration_audit.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/domains/sports/1500_sports_domain_scoping.md
  - docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md
---

# Session 1502 — Sports Prediction & Analytics Agents Audit (Category B)

> **What this doc is.** The second child audit of Group 1500. It answers
> the 28 canonical questions from playbook §9 for **Category B only** —
> the 4 sports market agents (`sports_odds_analyst`, `game_predictor`,
> `sharp_action_detector`, `arbitrage_detector`) plus the
> `SportsBettingCoordinator` orchestrator — using six parallel Explore
> sub-agents (per §13) + Claude parent verifier-loop passes on
> load-bearing claims (per §14 "trust but verify"). Every surface
> inventoried carries the 4-item pre-brief mini-schema per D62 = (a)
> propagate upfront (Chris-ratified S1501 open 2026-07-01), matching
> the sibling exemplar shape established by S1501 §4.6 / §5.4 / §6.6 /
> §8.4 / §15.1.
>
> **What this doc is not.** A design proposal. A posture recommendation.
> An audit of Cat A ingestion (§2.1 Cat A contract statement is our
> INPUT), of Cat C wager verification, of Cat D content pipeline, of
> Cat E frontend, or of Cat F cross-domain lens. An implementation
> plan. This is research.

---

## 1. Executive Summary

Category B — the four sports market agents plus the
`SportsBettingCoordinator` orchestrator — is **PARTIAL (armed but
under-instrumented)**. The code is complete and modular (5 surfaces,
2,622 lines total, no god-service), the beat schedule fires
`generate-daily-betting-brief` at 07:00 MT daily (verified
`core/celery.py:782-786`) and `collect-sports-odds-intelligence` every
30 min (`core/celery.py:787-790`), and every agent has a working
`.execute()` path that reads live Cat A odds data via `TheOddsSpider`,
runs analysis, and returns structured results. But the pipeline
under-instruments its own production: only 1 of the 5 orchestrator
paths captures Layer 1 `AgentExecution` telemetry, the Signal Engine
still lacks sports pattern types (S1274 §14 Finding #6 unchanged at
code level and now materialized on the Cat B consumer side), there is
no outcome-to-agent learning loop, and 2 of the 4 audited agents are
missing from the PA tool registry. Cat B **relies on Cat A's "does NOT
guarantee" list** (per S1501 §2.1) without filling the enum-drift or
fixture-identity gaps — it passes both downstream to Cat C / Cat D /
Cat E and to xx99 (S1599) posture-decision framing via Cat F.

**Nine load-bearing findings owed to xx99 (S1599) posture-decision
brief via Cat F evidence plan** — ordered by expected severity for
Rigby SIGN Q6 (riskiest operational finding) triage.

**Risk-axis distinction (Rigby SIGN cycle 1 Q6 fold — F7).** Findings
below carry two orthogonal risk labels: **OPERATIONAL RISK** (silent
break in production — visibility, monitoring, control-plane
correctness) and **ARCHITECTURAL RISK** (compounds into future gaps —
ontology, integration surface, feedback loops). Findings 1 and 2 lead
on operational-risk. Findings 3 and 5 lead on architectural-risk.
Findings 4, 6, 7 are posture-decision-pending (see per-finding
reframe notes below); their risk is contingent on Chris-gated posture
choice. F1-based operational-vs-architectural columns propagate to
§14 (drift), §15 (debt), and §19 (future research queue).

1. **[HIGH — riskiest operational risk per Rigby SIGN cycle 1 Q6]
   Coordinator `.run()` vs `.execute()` asymmetry (drift, HIGH; F9
   softened Session-1205 framing).**
   `SportsBettingCoordinator` at `core/services/sports_betting_coordinator.py:122`
   invokes `SportsOddsAnalyst.run()` with an explicit inline comment
   naming Session 1206's Layer 1 audit-trail rationale ("Session 1206:
   `.run()` writes `AgentExecution` telemetry row (Layer 1 audit)"),
   while the other four orchestrated agents are called via `.execute()`
   at lines 103 (`GamePredictor`), 140 (`ArbitrageDetector`), 158
   (`LineMovementAnalyzer`), 176 (`SharpActionDetector`). The
   coordinator's class docstring at
   `core/services/sports_betting_coordinator.py:22-33` describes a
   symmetric 5-agent pipeline. **Runtime consequence:** 4 of 5 agents
   invoked from the daily-brief beat produce no `AgentExecution` row,
   so `[PA_TASK_SUMMARY]` / `AgentExecutionAudit` / any downstream
   telemetry aggregation sees 20% of the pipeline. This creates
   "false green" monitoring: the system can appear to run while 4 of
   5 agents are effectively dark from Layer 1 telemetry (Rigby cycle 1
   Q6 wording). The Session 1206 provenance comment on line 120
   documents that `.run()` migration was in progress; whether the
   remaining 4 agents were slated for the same migration and it
   stalled, or whether asymmetry is intentional (SportsOddsAnalyst as
   sentinel-only), is not evident from code alone. **Cat A precedent:**
   S1501 §14.1 "silent choices-enum violation" is a schema-invariance
   failure; this is its behavioral analogue — an invariant the
   docstring asserts and the code silently breaks. **Operational
   risk: HIGH.** **Architectural risk: MED** (bounded 4-line fix once
   posture is chosen; the risk does not compound into future
   integration surfaces).

2. **[HIGH candidate] PA tool registry gap for two of the four Cat B
   agents (drift, MED-HIGH).** `core/services/tool_dispatcher.py:302-305`
   registers exactly 4 sports tools:
   `prediction_market_analyst`, `game_predictor`, `line_movement_analyzer`,
   `sharp_action_detector`. **Not registered:** `sports_odds_analyst`
   and `arbitrage_detector`. Both agents exist in `AGENT_MAP`
   (`core/agent_router.py`), are invoked by the coordinator (verified
   in §5.2), and have PA-visible outputs (Deliverable rows +
   HumanAttention items in the arb case). But Rigby cannot route a
   direct tool call to them by name — she can only reach them by
   dispatching the coordinator or by running the raw AGENT_MAP
   dispatcher. This restricts Rigby's ability to surgically re-run one
   agent for debugging (which is the whole point of PA tool
   registration). Whether this is a registration oversight or an
   intentional gate is unclear. `docs/topics/agent-system.md:42`
   claims 5 sports agents are available on-demand — reality is 4 PA
   tools + 2 coordinator-only.

3. **[HIGH via cascade from S1501 §14.1] `SpiderData.data_type ==
   'sports_odds'` filter is a post-fetch in-memory filter on a list of
   dicts, NOT an ORM query on the `SpiderData` model (S1500 parent
   §3.B claim clarified).** All 4 audited agents filter the events
   returned by `TheOddsSpider().fetch_data(...)`:
   `sports_odds_analyst.py:354` (`[e for e in events if e.get('data_type') == 'sports_odds']`),
   `game_predictor.py:167`, `arbitrage_detector.py:233`,
   `sharp_action_detector.py:159` (with an additional
   `len(h2h_odds) >= 3` condition). No agent runs
   `SpiderData.objects.filter(data_type='sports_odds')`; the only Cat
   B-adjacent ORM query on `SpiderData` is
   `line_movement_analyzer.py:181` reading historical `LegacySpiderData`
   for line comparison (and LineMovementAnalyzer is scope-boundary per
   §16). **Cascade posture from S1501 §14.1:** if Cat A ever fixes the
   silent-enum violation by adding `'sports_odds'` to the
   `SpiderData.data_type` choices (extend posture) OR by moving
   `sports_odds` writes to a new dedicated model (refactor posture),
   the 4 in-memory filters break silently because they compare the
   dict-return-shape from `TheOddsSpider().fetch_data()`, not the ORM
   row's `data_type` column. Cat B's filter contract is coupled to Cat
   A's spider dict-return shape, not the persisted enum — an
   integration surface that neither S1501 §14.1 nor this doc alone
   fully frames. Owed to Cat F posture-decision brief.

4. **[MED-HIGH — new observation, not in parent scoping] `ArbitrageDetector`
   does NOT persist to `sports.models.ArbitrageOpportunity` despite
   the model existing (drift, MED-HIGH).**
   `sports/models.py:1292` defines a fully-featured
   `ArbitrageOpportunity` model with `game`, `sportsbook_1`,
   `sportsbook_2`, arbitrage_percentage, and `is_active` fields; the
   sports app ships an admin at `sports/admin.py:454`, a
   `ArbitrageOpportunitySerializer` at `sports/serializers.py:405`, and
   a `ArbitrageOpportunityViewSet` at `sports/views.py:835`. But
   `ArbitrageDetector.execute()` at
   `core/agents/markets/arbitrage_detector.py:105-211` returns
   arbitrage opportunities as **dicts inside `AgentResult.data`** and
   never calls `ArbitrageOpportunity.objects.create()` (verified via
   targeted grep in `core/agents/markets/` — zero matches).
   `_create_attention_items()` at `arbitrage_detector.py:656` creates
   `HumanAttentionItem` rows for HOT/GOOD arbs via
   `attention_bridge.create_arbitrage_attention()`, and
   `_save_to_deliverable()` at line 178 persists a Deliverable per
   run — but the ORM row that admin, serializer, and viewset expect
   is never written. The `/api/v1/betting/arbitrage/` and
   `/api/v1/betting/arbitrage/scan/` REST endpoints (per Sub-agent 3
   report) instantiate `ArbitrageDetector` per-request and return the
   result dict — no DB read path. **Runtime consequence:** the sports
   app's admin panel is functionally empty for arbitrage (no rows to
   list), the viewset returns 200 with an empty queryset, and any
   consumer expecting durable arbitrage history has no data. Whether
   this is design (arbitrages are ephemeral and stale-lines close in
   minutes) or drift (persistence was planned then abandoned) is a
   Rigby SIGN surface. This mirrors — but does NOT exactly repeat —
   S1501 Cat A's dual-store observation: S1501 had two stores that
   both fill; S1502 Cat B has one durable-store surface (model +
   admin + viewset) that never fills.

5. **[HIGH architectural risk — biggest architectural risk per
   Rigby SIGN cycle 1 verdict — POSTURE-DECISION-PENDING per F2 fold]
   `SignalCluster.pattern_type` enum still lacks sports types + Cat B
   write side absent.** `core/models_signal_intelligence.py:75-86`
   declares 10 `PATTERN_TYPE_CHOICES`: `demand_spike`,
   `trend_emergence`, `sentiment_shift`, `opportunity_window`,
   `knowledge_gap`, `competitive_signal`, `market_movement`,
   `skill_demand`, `content_gap`, `user_need`. **Not present:**
   `sports_odds`, `sports_prediction`, `sharp_action_signal`,
   `arbitrage_opportunity`. Grep-verified: zero
   `SignalCluster.objects.create()` calls in
   `core/agents/markets/`. This is the exact enum-gap that S1274 §14
   Finding #6 first named at framing-level, that S1501 §14.1
   materialized at code-level for `SpiderData.data_type` /
   `SpiderData.source_platform`, and that this audit materializes at
   code-level for the **Cat B consumer side**. **F2 fold (Rigby SIGN
   cycle 1 Q4):** cites S1274 §12.3 "two legitimate postures"
   precedent per S1501 §2.1 posture-reframe pattern. Under integration
   posture, this becomes a "must add enum + write surface" finding.
   Under island posture, this becomes an "explicit 'sports do not emit
   SignalCluster rows' contract" finding. Cat B does not foreclose
   either posture; the enum absence + write absence together define
   the surface the Cat F evidence plan owes to xx99. **Architectural
   risk: HIGH** — this is the "sports becomes an island with parallel
   systems" risk per Rigby SIGN cycle 1 verdict. **Operational risk:
   LOW** (no runtime breakage today).

6. **[MED-HIGH architectural risk — POSTURE-DECISION-PENDING per F3
   fold] Zero Cat B → Cat C outcome-to-agent learning loop.**
   `GamePredictor` writes `MLPrediction` rows at `game_predictor.py:505`
   on each execute (auto-creating League→Team→Game via
   `.get_or_create()` at lines 428-464). The prediction row has a
   `was_correct` column (per Sub-agent 1's unique constraint report:
   `unique_together=('game', 'model_used', 'created_at')` + index on
   `was_correct`). `BettingOutcomeVerifier` at
   `core/services/betting_outcome_verifier.py:21` is a Cat C service
   that settles outcomes. **No bridge exists today:** no code path
   routes a settled outcome back into `GamePredictor`'s next-execute
   context, into `AgentMemory` for the market agents, into a
   recalibration task, or into a `SignalCluster` update.
   `MLPrediction.calculate_accuracy()` computes retrospective accuracy
   metrics for reporting but does not feed forward. Cat B agents
   fetch fresh `TheOddsSpider` data each execute with **no
   memoization, no historical context, no learning-adjusted priors**.
   **F3 fold (Rigby SIGN cycle 1 Q4):** reframed from "missing
   integration" to POSTURE-DECISION-PENDING per S1274 §12.3 precedent
   — "closed-loop learning deferred" is a legitimate posture (read-
   only inference in early phase; feedback-loop is a follow-on design
   decision). Under integration posture: bridge must be built (Cat C
   `BettingOutcomeVerifier` → Cat B prediction context). Under island
   posture: explicit "sports agents are memoryless-by-construction"
   contract must be documented + defended. **This remains the
   load-bearing "sports as island" evidence for Cat F**: whichever
   posture Chris picks, this is the deciding surface. **Architectural
   risk: MED-HIGH.** **Operational risk: LOW** (no runtime breakage
   today; agents are stateless by construction).

7. **[MED architectural risk — POSTURE-DECISION-PENDING per F4 fold]
   Zero Memory Domain (S1300) bridge.** Grep of
   `core/agents/markets/*.py` for `AgentMemory`,
   `AgentKnowledgeSource`, `AgentLearning`, `UserAgentLearning`
   returns zero matches (verified via Sub-agent 4 integration report).
   Cat B agents inherit `BaseAgent` mixins (`_save_to_deliverable`,
   `time_travel_session`, `_record_learning_outcome`) but do not
   touch the S1300 Memory Domain models.
   `_record_learning_outcome()` is called by
   `sports_odds_analyst.py:258-266` and `arbitrage_detector.py:166-175`
   inside try/except (log-on-failure) but Sub-agent 4 traced the write
   path and it does not persist to `AgentMemory` — it emits a log
   line and defers. **F4 fold (Rigby SIGN cycle 1 Q4):** reframed
   from "missing integration" to POSTURE-DECISION-PENDING per S1274
   §12.3 precedent — "context-agnostic by construction" is a
   legitimate posture (many sports pipelines are intentionally
   context-agnostic to avoid stale priors contaminating picks). Under
   integration posture: bridge must be built to route sports outcomes
   through `AgentMemory`. Under island posture: explicit
   "sports-agents-are-context-agnostic-by-construction" contract must
   be documented. **Delegation flag:** Group 1300 (Memory Domain)
   already closed at S1399 xx99 canonical summary; if integration
   posture is chosen, Cat F evidence plan delegates to Group 1300
   follow-on. **Architectural risk: MED.** **Operational risk: LOW.**

8. **[MED — inherited from S1501 with new scope] Sub-boundary
   observation: `LineMovementAnalyzer` and `PredictionMarketAnalyst`
   are called by coordinator but NOT named in parent §3.B Cat B
   scope (scope-boundary drift, MED).** Parent scoping §3.B names
   exactly 4 agents + `SportsBettingCoordinator`. `SportsBettingCoordinator.generate_brief()`
   at `sports_betting_coordinator.py:74` (LineMovementAnalyzer) and
   line 79 (SharpActionDetector, which IS in scope) plus PA tool
   registry at `tool_dispatcher.py:302` (PredictionMarketAnalyst)
   surface two additional Markets agents that Cat B audits partially
   without owning. **Owed to xx99 (S1599)** for scope reconciliation:
   are LineMovementAnalyzer and PredictionMarketAnalyst under Cat B
   or under a distinct Category (e.g., a prediction-markets subdomain
   that also covers Kalshi)? Parent §3.A already put Kalshi in Cat A
   ingestion side but §3.B silence on `PredictionMarketAnalyst` (a
   Kalshi consumer) leaves ownership ambiguous. This audit
   documents both agents in §16 boundary observations without
   deep-audit; xx99 reconciles.

9. **[MED — INTENTIONAL-OR-DRIFT NEEDING CONTRACT STATEMENT per F8
   fold] Coordinator "continue on error" failure semantics
   undocumented.** Every `_run_*` helper in
   `sports_betting_coordinator.py:98-187` returns `None` on exception
   and only appends the agent name to `brief['agents_run']` if the
   returned value is truthy. The `logger.error()` line preserves the
   fact of failure but the brief itself does not carry an explicit
   "agent X failed" marker (only "agent X is missing from
   `agents_run`"). Consumers reading the brief and iterating over the
   5 fixed keys (`predictions`, `odds_analysis`, `arbitrage`,
   `line_movements`, `sharp_action`) will silently see `None` values.
   `_build_executive_summary()` at line 189-225 defensively wraps each
   section in `x or {}` so failure is not user-visible in the summary
   text — but the brief consumer (REST endpoint, downstream content
   pipeline in Cat D, or UI in Cat E) sees `None` and must handle it.
   **F8 fold (Rigby SIGN cycle 1 Q8):** reframed from "drift" to
   "intentional-or-drift needing contract statement" per S1501 F6
   "unimplemented expectation" precedent. This is either (a) an
   intentional best-effort-partial-brief resilience pattern that must
   be documented as intentional AND propagated to consumer contract,
   OR (b) a fail-fast omission that must be replaced with explicit
   failure surfacing. The choice is a Cat B contract-statement
   decision, not a bugfix. **Operational risk: MED** (consumers may
   trip on `None`). **Architectural risk: LOW** (bounded contract
   documentation once posture is chosen).

**Other observations:** `SportsOddsAnalyst` hardcodes
`model="gpt-5-mini"` via `get_openai_client()` at
`sports_odds_analyst.py:619` (Sub-agent 6 flag); `GamePredictor` and
`SharpActionDetector` use `LLMProviderRegistry` with hardcoded
`[('openai', 'gpt-4.1-mini'), ('anthropic', 'claude-sonnet-4-5-20250929')]`
fallback sequence at `game_predictor.py:335` /
`sharp_action_detector.py:355`; `ArbitrageDetector` has no LLM call at
all in `execute()` (pure heuristic — 2-way / 3-way arb math + rating
classifier). Discord command surface: only `/arb` at
`discord_bot.py:1260-1350` directly invokes a Cat B agent
(`ArbitrageDetector.run()`); `/odds`, `/predictions`, `/bankroll`,
`/bet`, `/resolve`, `/futures`, `/slip` are data-only or Cat C/D
surfaces. Frontend surface: `frontend/src/pages/BettingPage.tsx` +
`frontend/src/lib/api.ts` consume `/api/v1/betting/*` endpoints — deep
audit deferred to Cat E per parent §3.E.

**What xx99 owes (through Cat F evidence plan):** Cat B is more
"integration-ready-with-drift" than Cat A was. Cat A was
"WORKING (fragile contract) at ingestion, PARTIAL at normalization"
where the fragility was schema-invariance. Cat B is "PARTIAL (armed
but under-instrumented)" where the fragility is observation-invariance:
the pipeline runs, but doesn't watch itself, doesn't learn from itself,
doesn't emit signals for others to watch. Integration posture would
require: (i) extending `SignalCluster.pattern_type` with sports types
AND wiring Cat B write paths to emit them; (ii) reconciling `.run()` /
`.execute()` asymmetry so all coordinator paths capture Layer 1
telemetry; (iii) building the outcome-to-agent feedback loop
(BettingOutcomeVerifier → next-generation prediction context); (iv)
either persisting `ArbitrageOpportunity` rows OR removing the
model/admin/serializer/viewset triple; (v) registering
`sports_odds_analyst` and `arbitrage_detector` in PA tool dispatcher.
Island posture would require: (i) explicit "no downstream signal
consumers" contract; (ii) memory-scope isolation so Cat B never depends
on `AgentMemory`; (iii) documented fixture-identity boundary (inherit
Cat A's non-guarantee, don't fill it); (iv) explicit "arbitrage state
is ephemeral" design capture. Neither posture is zero-cost. Cat B
evidence lands cleanly on both sides of the F decision — like Cat A —
but with an additional axis (observability / self-instrumentation) that
S1501 didn't surface.

---

## 2. Domain Purpose

**Q1 — What is this domain for?** Category B is the analytics tier for
sports betting intelligence: it consumes Cat A odds data
(via `TheOddsSpider` dict returns) and turns it into structured
predictions, value-bet signals, sharp-money divergence signals, and
cross-book arbitrage opportunities that flow into daily/nightly betting
briefs, PA-dispatched Rigby responses, Discord `/arb` command replies,
and the `/betting` frontend dashboard.

**Q2 — What problem does it solve?** Betting content pipelines (Cat D),
frontend surfaces (Cat E), and PA conversational surfaces need
structured, actionable analytics rather than raw odds arrays. Raw odds
tell you what markets exist; predictions tell you where the model
diverges from the market, sharp-action divergence tells you where
professional money is moving relative to soft books, arbitrage detection
tells you where cross-book pricing gaps guarantee profit. Building
these analytics inline in Cat E or Cat D would either couple the
frontend/content pipeline to LLM providers or force it to re-implement
odds parsing on every render. Cat B centralizes the analytics behind
an `AgentResult` contract and a single orchestrator (`SportsBettingCoordinator`)
that composes them into a unified brief.

### 2.1 Cat B contract statement

To prevent this doc from being read as promising Cat A ingestion, Cat
C wager verification, Cat D content pipeline, or Cat F posture-decision
behavior it does not own, Cat B's runtime contract is stated explicitly
here — mirroring the S1501 §2.1 shape.

**Cat B guarantees today:**

- 4 market agents (`sports_odds_analyst`, `game_predictor`,
  `sharp_action_detector`, `arbitrage_detector`) + 1 orchestrator
  service (`SportsBettingCoordinator`) land on `main` and execute in
  production (verified §5.1 / §5.2).
- Beat schedule fires `generate-daily-betting-brief` @ 07:00 MT daily
  (verified `core/celery.py:782-786`, `queue: default`, `expires: 3600s`)
  which invokes `SportsBettingCoordinator().generate_brief()` via
  `core/tasks.py:6188-6190` → `core/tasks_content.py:_impl_generate_daily_betting_brief`.
- Beat schedule fires `collect-sports-odds-intelligence` @ every 30
  min (verified `core/celery.py:787-790`, `queue: long_running`,
  `expires: 1800s`) which is a Cat A intelligence-collection surface
  producing input Cat B agents consume; noted as Cat A boundary here.
- `SportsBettingCoordinator.generate_brief()` sequentially invokes 5
  agents (`GamePredictor.execute()`, `SportsOddsAnalyst.run()`,
  `ArbitrageDetector.execute()`, `LineMovementAnalyzer.execute()`,
  `SharpActionDetector.execute()`), aggregates results into a brief
  dict keyed by `predictions` / `odds_analysis` / `arbitrage` /
  `line_movements` / `sharp_action`, and returns
  `{executive_summary, top_plays, agents_run, errors,
  generation_time_seconds, ...}`.
- `GamePredictor.execute()` persists predictions to
  `sports.models.MLPrediction` on each run
  (`game_predictor.py:505` — `MLPrediction.objects.create(...)`;
  cascading `.get_or_create()` on `League` / `Team` / `Game`).
- All 4 Cat B agents write a `Deliverable` row per execute via
  `BaseAgent._save_to_deliverable()` (verified — `sports_odds_analyst.py:291`,
  `game_predictor.py:126`, `sharp_action_detector.py:112`,
  `arbitrage_detector.py:178`).
- `ArbitrageDetector._create_attention_items()` creates
  `HumanAttentionItem` rows for HOT / GOOD arbitrage opportunities via
  `attention_bridge.create_arbitrage_attention()` at
  `arbitrage_detector.py:656`.
- PA tool registry at `core/services/tool_dispatcher.py:302-305`
  exposes 4 sports agent handlers: `prediction_market_analyst`,
  `game_predictor`, `line_movement_analyzer`, `sharp_action_detector`.
- Discord `/arb` command at `core/services/discord_bot.py:1260-1350`
  directly invokes `ArbitrageDetector.run()` and returns the arbitrage
  opportunities as a formatted Discord embed.
- REST endpoints under `/api/v1/betting/*` (arbitrage / brief /
  sharp-action / line-movement) and `/api/v1/sports/*` (analyze-game /
  orchestrate / betting-intelligence) invoke Cat B agents through
  `core/views_odds_sports.py` view functions.

**Cat B explicitly does NOT guarantee:**

- Layer 1 `AgentExecution` telemetry on 4 of 5 coordinator paths. Only
  `SportsOddsAnalyst.run()` at `sports_betting_coordinator.py:122`
  gets the `.run()` treatment — the other 4 agents use `.execute()`
  which bypasses the Session-1206 AgentExecution row. Whether this is
  Cat B's contract to Layer 1 or a coordinator-drift is a
  posture-decision surface.
- PA tool discoverability for `sports_odds_analyst` and
  `arbitrage_detector`. These 2 agents are absent from
  `tool_dispatcher.py:302-305`. Rigby cannot dispatch them directly by
  name; she can only reach them by dispatching the coordinator or by
  raw AGENT_MAP routing.
- `SignalCluster` emissions. Zero Cat B code writes `SignalCluster`
  rows (verified via targeted grep). Even if the enum were expanded to
  cover sports pattern types (which it is not — see §14.3), the write
  path does not exist.
- `Initiative` auto-creation from high-confidence predictions /
  arbitrages. Zero Cat B code writes `Initiative` rows (verified via
  targeted grep). Downstream initiative-generation is deferred to
  posture-decision architecture.
- Persistent `sports.models.ArbitrageOpportunity` rows. Despite the
  model + admin + serializer + viewset existing at
  `sports/models.py:1292` / `sports/admin.py:454` /
  `sports/serializers.py:405` / `sports/views.py:835`, no Cat B code
  calls `ArbitrageOpportunity.objects.create()`.
  `ArbitrageDetector.execute()` returns arbitrages as dicts inside
  `AgentResult.data['arbitrage_opportunities']`; only
  `HumanAttentionItem` + `Deliverable` are persistent.
- Outcome-to-agent feedback loops. `MLPrediction.calculate_accuracy()`
  computes retrospective metrics; no code path routes settled outcomes
  from `BettingOutcomeVerifier` (Cat C) back into next-generation Cat
  B agent context. Cat B is memoryless by construction.
- Memory Domain (S1300) bridge. Zero reads of `AgentMemory` /
  `AgentKnowledgeSource`; zero writes. Cat B agents inherit the
  `_record_learning_outcome` mixin but it emits log lines, not
  `AgentMemory` rows (verified §9).
- Advisor / user profile context injection. Agents are
  context-agnostic — no `Advisor` reads, no `UnifiedUser.learning_history`
  consumption.
- Symmetric agent output shapes. Cat B agents emit 4 different key
  names for conceptually similar outputs (`signals` /
  `predictions` / `signals` / `arbitrage_opportunities`). Consumers
  compensate.
- Fixture / entity identity reconciliation across `event_id` (TheOdds),
  `ticker` (Kalshi), `game_id` (Cat B `sports.models.Game`). Cat B
  inherits Cat A's non-guarantee from S1501 §2.1 and does not fill it.
- EventBus participation. No `emit_event()` / `publish()` /
  `EventLog.objects.create()` calls in any Cat B surface (verified
  §10).
- Bankroll / staking strategy computation. `ArbitrageDetector`
  computes stake distribution for a fixed $100 bankroll at
  `arbitrage_detector.py:~498-558`; this is inventory-only per parent
  §7 anti-scope #9 — Cat B does NOT run bankroll-management strategy
  research.

Consumers who need any of the "does NOT guarantee" behaviors depend on
Cat F posture decision + follow-on design work. Cat B does not
foreclose any posture; it just doesn't ship the bridges.

---

## 3. Canonical Entry Points

**Q3 — What are the canonical entry points?**

### 3.1 Celery tasks (in-scope for Cat B)

| Task name | Registered at | Beat entry | Cadence | Queue | Cat B invocation |
|---|---|---|---|---|---|
| `core.tasks.generate_daily_betting_brief` | `core/tasks.py:6188` → `_impl_generate_daily_betting_brief` in `core/tasks_content.py` | `generate-daily-betting-brief` at `core/celery.py:782-786` | `crontab(hour=7, minute=0)` — 07:00 MT daily | `default`, `expires: 3600` | Wraps `SportsBettingCoordinator().generate_brief()` |
| `core.tasks.run_all_desks_intelligence` | `core/tasks.py` (Session 1000 all-desks rotation) | UNKNOWN beat cadence | UNKNOWN | UNKNOWN | Invokes `SportsBettingCoordinator().generate_brief()` at `core/tasks.py:12170-12171` as Desk 2 (Sports) — SPECULATIVE cadence per Sub-agent 3 |

**Note (Cat A boundary):** `collect-sports-odds-intelligence` at
`core/celery.py:787-790` is a Cat A ingestion beat (S1501 §3.1) but
its outputs are Cat B's read source via `TheOddsSpider().fetch_data()`.
Not double-listed here; noted as boundary for evidence-plan clarity.

### 3.2 Management commands

Grep of `core/management/commands/` for any command file that invokes
Cat B agents or `SportsBettingCoordinator` returned **0 matches**
(Sub-agent 3). No CLI entrypoint for Cat B. Ops must use PA tool
dispatch, beat schedule, or direct REST call.

### 3.3 REST + WebSocket entry points

**REST endpoints (9 — all defined in `core/urls.py:3084-3130`, handled by `core/views_odds_sports.py`):**

| Endpoint | Method | View function | Cat B invocation site | Purpose |
|---|---|---|---|---|
| `/api/v1/betting/arbitrage/` | GET/POST | `detect_arbitrage()` | `core/views_odds_sports.py:317` — `ArbitrageDetector().run()` | Real-time arbitrage scan |
| `/api/v1/betting/arbitrage/scan/` | GET/POST | `scan_arbitrage_opportunities()` | `core/views_odds_sports.py:445` | Extended arbitrage discovery |
| `/api/v1/betting/brief/` | GET | `get_betting_brief()` | `core/views_odds_sports.py:3248` — `SportsBettingCoordinator().generate_brief()` | Full daily brief |
| `/api/v1/betting/sharp-action/` | GET | `get_sharp_action()` | `core/views_odds_sports.py:3284` — `SharpActionDetector().execute()` (SPECULATIVE — SA-3 did not verify method) | Sharp signals |
| `/api/v1/sports/analyze-game/` | POST | `sports_game_analysis()` | Embedded — GamePredictor path | Game-level prediction |
| `/api/v1/sports/orchestrate/` | POST | `orchestrate_agent_analysis()` | Multi-agent orchestration | Coordinated analysis |
| `/api/v1/sports/orchestration/status/<task_id>/` | GET | `get_orchestration_status()` | Async result poll | — |
| `/api/v1/betting/line-movement/` | GET | `get_line_movement()` | `LineMovementAnalyzer` — Cat B scope-boundary per §16 | Line movement data |
| `/api/v1/sports/betting-intelligence/` | GET | `get_betting_intelligence()` | Integrated read | — |

**WebSocket consumers (3 — defined in `core/consumers_sports.py`, wired in `core/routing.py:128-132`):**

| Consumer | Route | Purpose | Cat B relevance |
|---|---|---|---|
| `SportsUpdatesConsumer` | `/ws/sports/updates/` | Real-time sports data updates | Data channel — not an agent-control channel |
| `LiveSportsConsumer` | `/ws/live-sports/` | Live event tracking | Data channel |
| `ArbitrageConsumer` | `/ws/arbitrage/` | Arbitrage opportunity streaming | Data channel — reads may include Cat B outputs (SPECULATIVE — deferred to Cat E audit S1505) |

**Note:** All three WS consumers are read-side data distribution. None is an agent-control channel that would invoke a Cat B `.execute()` or `.run()` from a WS message. WS-consumed data may be produced upstream by Cat B, but the wiring is deferred to Cat E audit.

### 3.4 PA tools

`core/services/tool_dispatcher.py:302-305` registers 4 sports-agent handlers, all routed through `_handle_agent_tool`:

| PA tool name | Handler | Class dispatched | In Cat B scope? |
|---|---|---|---|
| `prediction_market_analyst` | `_handle_agent_tool` | `PredictionMarketAnalyst` | Scope-boundary per parent §3.B — §16 flag |
| `game_predictor` | `_handle_agent_tool` | `GamePredictor` | YES |
| `line_movement_analyzer` | `_handle_agent_tool` | `LineMovementAnalyzer` | Scope-boundary per parent §3.B — §16 flag |
| `sharp_action_detector` | `_handle_agent_tool` | `SharpActionDetector` | YES |

**Not registered (drift, §14.2):** `sports_odds_analyst` and
`arbitrage_detector`. Both exist in `AGENT_MAP`
(`core/agent_router.py`) and are invoked by the coordinator; both
have PA-visible outputs (Deliverable + HumanAttention). Rigby cannot
dispatch them by name via PA — she must dispatch the coordinator
(which invokes them internally) or go through the raw AGENT_MAP router.

**Schema-level mention:** `core/services/pa_tool_schemas.py:1125-1126`
lists `game_predictor` and `sharp_action_detector` in the agent enum
description; the description at line 1146 names "Sports: game
predictor, line movement, sharp action, prediction market analyst" —
mirrors the dispatcher registrations, so schema-level surface count is
consistent with dispatcher: 4 registered.

### 3.5 Discord bot commands

`core/services/discord_bot.py` (25 Cog classes total; Cat B lives in
`SpiderCommands`):

| Command | Cog | Line | Cat B invocation | Purpose |
|---|---|---|---|---|
| `/arb` | `SpiderCommands` | 1260-1350 | `ArbitrageDetector.run()` at line ~1285 | Cross-book arbitrage on demand |

**Not Cat B (Cat A/C/D per parent §3):** `/odds` (Cat D per parent
§3.D, invokes TheOddsSpider display), `/predictions` (KalshiSpider —
Cat A boundary via Kalshi), `/bankroll` (Cat C — user stats),
`/bet` (Cat C — log wager), `/resolve` (Cat C — settle wager),
`/futures` (Cat D — display), `/slip` (Cat D — bet slip generator).

**Discord surface count:** 1 Cat B-invoking command (`/arb`) versus 7
data-only or Cat A/C/D siblings within the same Cog. Only
`ArbitrageDetector` has direct Discord surface; the other 3 Cat B
agents (`SportsOddsAnalyst`, `GamePredictor`, `SharpActionDetector`)
have no direct Discord command — they are surfaced through
`/api/v1/betting/brief/` REST or the daily beat.

---

## 4. Major Models

**Q4 — What are the major models?**

Cat B is primarily a consumer of Cat A models, but has three own-write
surfaces (`MLPrediction` via `GamePredictor`, `Deliverable` via all 4
agents' `_save_to_deliverable`, `HumanAttentionItem` via
`ArbitrageDetector._create_attention_items`) and a fourth own-write
surface that exists at model level but is never written
(`ArbitrageOpportunity` — see §4.3). Per playbook §9 anti-duplication
rule, Cat A models are cited (§4.5) but not re-inventoried; S1501 §4
owns the full inventory.

### 4.1 `MLPrediction` — `sports/models.py:1750` (per Sub-agent 1 report)

- Written exclusively by `GamePredictor._store_predictions()` at
  `game_predictor.py:505` via `MLPrediction.objects.create(...)`.
- FKs: `game` → `sports.models.Game` (CASCADE), `predicted_winner` →
  `sports.models.Team` (CASCADE), `agent` →
  `agents_registry.UnifiedAgentTemplate` (SET_NULL — allows prediction
  orphaning if agent template removed).
- Meta: `unique_together=('game', 'model_used', 'created_at')` —
  prevents duplicate persistence at same timestamp for same model on
  same game.
- Meta indexes: `('game', '-created_at')`, `('sport_type', '-created_at')`,
  `('model_used', '-created_at')`, `('was_correct',)`, `('created_at',)`.
- Retention: **NO TTL** (Sub-agent 1). Predictions accumulate
  indefinitely; `MLPrediction.calculate_accuracy()` reads historically
  but does not cull.
- Migration lineage: `sports/migrations/0002_mlprediction_userbet_and_more.py`
  (per Sub-agent 1) — 2025-09-30.
- Read consumers: `MLPrediction.calculate_accuracy()` (metrics only —
  no learning-loop return path); `sports/views.py` viewset presumed
  (deferred to Cat E surface audit).

### 4.2 `League` / `Team` / `Game` (auto-create chain)

- Written by `GamePredictor` during prediction storage:
  `League.objects.get_or_create()` at
  `game_predictor.py:428-435`; `_get_or_create_team()` at
  `game_predictor.py:438-439` for home + away; `Game.objects.get_or_create(external_id=..., ...)`
  at `game_predictor.py:455-464`.
- Model defs: `sports/models.py:101` (League), `:177` (Team), `:261` (Game) per Sub-agent 1.
- FK graph: `Team.league` → `League` CASCADE; `Team.abbreviation`
  unique per league (`unique_together=('league', 'abbreviation')`);
  `Game.home_team` / `Game.away_team` → `Team` CASCADE; `Game.league`
  → `League` CASCADE; `Game.external_id` indexed for dedup.
- Retention: no TTL.
- Cross-domain surface: L / T / G are also read by Cat C wager
  tracking (`PlacedWager.game` FK) and Cat E frontend viewsets —
  scope-boundary; not audited here.

### 4.3 `sports.models.ArbitrageOpportunity` — `sports/models.py:1292`

**Written by Cat B: NEVER.** Verified via `grep -rn
"ArbitrageOpportunity\.objects\.(create|update_or_create|bulk_create)"
core/agents/markets/` → 0 matches. `ArbitrageDetector` returns
arbitrages as dicts inside `AgentResult.data['arbitrage_opportunities']`;
persistence is via `HumanAttentionItem` (attention-bridge, ephemeral) and
`Deliverable` (audit trail, not queryable as arbitrages).

- Model exists with: `game` FK, `sportsbook_1` FK, `sportsbook_2` FK
  (all CASCADE), `arbitrage_percentage`, `is_active` boolean.
- Admin at `sports/admin.py:454` — functionally empty (no rows to
  list).
- Serializer at `sports/serializers.py:405` — no producer feeds it.
- ViewSet at `sports/views.py:835`
  (`ArbitrageOpportunityViewSet(viewsets.ReadOnlyModelViewSet)`) —
  returns empty queryset in practice.
- Whether this is design intent (arbitrages are ephemeral by nature —
  stale lines close in minutes; persistence would create noise) or
  drift (persistence was planned then abandoned) is a §14.4 open
  question and a Rigby SIGN surface.

### 4.4 `Deliverable` (via BaseAgent) — `core/models_deliverables.py:84`

- Written by all 4 Cat B agents via `BaseAgent._save_to_deliverable()`
  mixin (verified — `sports_odds_analyst.py:291`,
  `game_predictor.py:126`, `sharp_action_detector.py:112`,
  `arbitrage_detector.py:178`).
- One row per agent execute — durable audit trail regardless of
  downstream persistence.
- Cross-domain surface: `Deliverable` is a shared mainline model, not
  Cat B-owned. Full model inventory deferred to Group 1600
  (Content / Deliverables / Publishing) if Chris opens it.

### 4.5 Read-source models (inherited from Cat A per S1501 §4)

- `LegacySpiderData` (aka `SpiderData` in S1501 §4.3 — verify Sub-agent
  1 vs S1501 nomenclature; `LegacySpiderData` appears at
  `line_movement_analyzer.py:181` for ORM-side read of historical odds).
  Cat B's read of Cat A data is via `TheOddsSpider().fetch_data()` dict
  return, NOT ORM query on `SpiderData` (see §7.1 Flow A). Only
  scope-boundary agent (LineMovementAnalyzer) uses ORM.
- `OddsSnapshot`, `GameLineHistory` — Cat A owned; not consumed by Cat
  B in production paths (SPECULATIVE — no ORM read verified in Cat B
  agent grep).
- LLM provider identifiers via `LLMProviderRegistry` / `openai_client_factory`
  — Cat G boundary (LLM infra).

### 4.6 `SportsBettingBrief` — `core/models_unified_system.py:18394` (F10 fold — Rigby SIGN cycle 1 Q9)

- Written by `SportsBettingCoordinator.generate_brief()` downstream —
  verified via targeted grep. Two write sites:
  `core/tasks.py:12187` (from `run_all_desks_intelligence` Desk 2
  Sports rotation) and `core/tasks_content.py:3150` (from
  `_impl_generate_daily_betting_brief` daily beat).
- Model at `core/models_unified_system.py:18394` (unified system app,
  public schema).
- **Post-cycle-1 verification (F10 fold):** Sub-agent 3's
  "SportsBettingBrief model + cache" mention was left as UNKNOWN in
  the draft §20.3; parent-Claude verifier-loop after Rigby cycle 1
  Q9 confirmed the model exists via `grep "class SportsBettingBrief"`
  and confirmed the two write sites above via grep for
  `SportsBettingBrief.objects.`. Cache TTL claim (Sub-agent 3
  mentioned 6h) not verified — deferred to Cat D audit S1504.
- **Runtime consequence:** brief IS persisted after each daily-brief
  beat OR each all-desks rotation, not transient. `/api/v1/betting/brief/`
  REST endpoint may read from persisted SportsBettingBrief rows OR
  re-invoke coordinator — resolution deferred to Cat D S1504 consumer
  contract audit.
- Cross-domain surface: SportsBettingBrief is unified-system-app
  scope, not Cat B-owned. Cat B is one of two writers.

### 4.7 `HumanAttentionItem` (persistent write from ArbitrageDetector)

- Written via `attention_bridge.create_arbitrage_attention()` at
  `arbitrage_detector.py:656` for HOT / GOOD arbs only (rating filter
  at line 655 per Sub-agent 4).
- Cross-domain surface: `HumanAttentionItem` is a shared mainline model
  (`core/services/human_attention_bridge.py`); not Cat B-owned.
- Cat B is one of many producers; write path here is the only Cat B
  → mainline notification bridge.

### 4.8 4-item pre-brief mini-schema per model (D62 fold)

| Model | (a) sports-only vs shared | (b) DBAO schema vs public schema | (c) integration posture (refactor vs extend) | (d) island posture (additional isolation) |
|---|---|---|---|---|
| `MLPrediction` | sports-only (fields sports-specific) | **public schema, sports app.** `sports/models.py` writes to `default` DB per Django app config; no DATABASE_ROUTERS observed for sports app. | **extend** — no refactor needed. Could add FK to `SignalCluster` for signal-emission under integration posture without touching write side. Could add `outcome_settled_at` + FK to `PlacedWager` for outcome-feedback loop under integration posture. | **strong isolation already** — no FK to non-sports mainline model besides `UnifiedAgentTemplate` (SET_NULL — orphans allowed). Island posture would need retention job + explicit archival policy. |
| `League` / `Team` / `Game` | sports-only | public schema, sports app | **extend** — cross-book fixture-identity reconciliation could add a `Game.external_id_map` JSONField under integration posture (map `theodds_event_id` → `kalshi_ticker` → canonical `game_id`) without refactor. | **strong isolation already** — no cross-domain FK inbound besides Cat B write via `GamePredictor.get_or_create()` and read via Cat C `PlacedWager.game`. Island posture already fits. |
| `ArbitrageOpportunity` | sports-only | public schema, sports app | **refactor OR remove** — the write surface is absent. Integration posture requires wiring `ArbitrageDetector` to persist rows (one refactor site: `_create_arb_opportunity()` at `arbitrage_detector.py:498-558`). Island posture requires deleting model + admin + serializer + viewset OR documenting them as read-only vestige. | **N/A while unwritten** — model has strong isolation (only 3 CASCADE FKs to sports internals) but is unreachable by write path. Any posture chooses first between "persist" and "remove". |
| `Deliverable` | **shared** — multi-domain container written by every agent in the platform | **public schema, core app.** Not sports-specific. | **N/A for Cat B under either posture** — Deliverable is a shared write surface; Cat B's contract is "write one Deliverable per agent execute" and both postures preserve that. | **N/A** — Deliverable is not a Cat B-owned model. |
| `HumanAttentionItem` | **shared** — multi-domain container (Cat B is one producer among many) | **public schema, core app.** | **N/A** — HumanAttention is shared. | **N/A** — not Cat B-owned. |

**Note:** No Cat B-owned model lives in a `dbao` PostgreSQL schema.
Parent §3.F flags DBAO codename shape as an xx99 parked question; Cat
B evidence confirms **public-schema-only** for all Cat B write
surfaces on `main` at HEAD `722ff313`. If integration posture chose
"move sports models to `dbao` schema", this is a **full refactor**
per (c) axis — every write site + read site + admin + serializer +
viewset + migration + Django app config would need adjustment. Not
zero-cost.

---

## 5. Major Services

**Q5 — What are the major services?**

Cat B has 5 primary surfaces at the service/agent layer: 4 agent
classes at `core/agents/markets/*.py` and 1 orchestrator service at
`core/services/sports_betting_coordinator.py`. All inherit `BaseAgent`
(agents) or none (coordinator is not an agent). Total line count
2,622 across the 5 surfaces — none exceeds the playbook §5.3 3000-line
god-service threshold.

### 5.1 Agent layer

| Agent | file:line | Line count | Base class | LLM call | Output shape (`AgentResult.data` keys) |
|---|---|---|---|---|---|
| `SportsOddsAnalyst` | `core/agents/markets/sports_odds_analyst.py:59` | 730 | `BaseAgent` (line 24) | **OpenAI direct** — `get_openai_client()` factory, hardcoded `model="gpt-5-mini"` at line 619, `max_completion_tokens` ≥ 4000 (per memory rule `feedback_gpt5_max_completion_tokens_floor.md` compliance — SPECULATIVE; targeted read not run) | `{events_analyzed, signals, analysis, structured_report, provenance, publishable}` |
| `GamePredictor` | `core/agents/markets/game_predictor.py:27` | 560 | `BaseAgent` (line 19) | **LLMProviderRegistry** — `get_llm_provider_registry().complete(...)` at line 335 tries `('openai', 'gpt-4.1-mini')` then `('anthropic', 'claude-sonnet-4-5-20250929')` fallback | `{predictions, total_games, predictions_stored, llm_analysis, provenance}` |
| `SharpActionDetector` | `core/agents/markets/sharp_action_detector.py:24` | 366 | `BaseAgent` (line 18) | **LLMProviderRegistry** — same fallback tuple as GamePredictor at line 355 | `{signals, hot_signals, warm_signals, events_with_divergence, llm_analysis}` |
| `ArbitrageDetector` | `core/agents/markets/arbitrage_detector.py:47` | 676 | `BaseAgent` (line 18) | **NONE in `execute()` path** — pure heuristic (2-way + 3-way arb math + rating classifier) | `{events_scanned, arbitrage_opportunities, hot_arbs, good_arbs}` |

**Verified line counts** via `wc -l` on 2026-07-02:
`sports_odds_analyst.py` 730, `game_predictor.py` 560,
`sharp_action_detector.py` 366, `arbitrage_detector.py` 676,
`sports_betting_coordinator.py` 290. Total 2622.

**Direct-consume filter pattern** (parent §3.B claim clarification —
see §1 Finding 3):

| Agent | Filter site | Query shape |
|---|---|---|
| `SportsOddsAnalyst` | `sports_odds_analyst.py:354` | `[e for e in events if e.get('data_type') == 'sports_odds']` |
| `GamePredictor` | `game_predictor.py:167` | `[e for e in events if e.get('data_type') == 'sports_odds']` |
| `SharpActionDetector` | `sharp_action_detector.py:159` | `if e.get('data_type') == 'sports_odds' and len(e.get('h2h_odds', [])) >= 3` |
| `ArbitrageDetector` | `arbitrage_detector.py:233` | `[e for e in events if e.get('data_type') == 'sports_odds']` |

All 4 filter sites are **post-fetch, in-memory list comprehensions**
on the list of dicts returned by
`TheOddsSpider().fetch_data(sports=[...], max_results=..., ...)`.
**No agent runs `SpiderData.objects.filter(data_type='sports_odds')`.**
The exact runtime shape (F12 fold — Rigby SIGN cycle 1 Q8 tightening):

```python
# Verbatim shape from sports_odds_analyst.py:353-354 (representative — 3 of 4 agents):
events = spider.fetch_data(...)   # returns List[Dict[str, Any]] with per-event dicts
filtered_events = [e for e in events if e.get('data_type') == 'sports_odds']
```

The filter's coupling is to the spider's dict return shape (a
per-event dict with a `data_type` key that TheOddsSpider assigns
during `fetch_data()` normalization), **not** to the persisted
`SpiderData.data_type` column. If Cat A ever migrates the enum
value `sports_odds` (per S1501 §14.1 posture-decision) at either the
model level OR the spider dict-assignment level, the 4 in-memory
filters break silently.

The only ORM-side `LegacySpiderData` read is at
`line_movement_analyzer.py:181` — LineMovementAnalyzer is
scope-boundary (§16), not audited as a Cat B core agent here. This
clarifies parent §3.B's "direct-consume filter" characterization:
the filter's coupling is to the spider's dict return shape, not the
persisted enum. See §1 Finding 3 for cascade-posture implications.

### 5.2 Coordinator layer — `SportsBettingCoordinator`

- Location: `core/services/sports_betting_coordinator.py:21`, 290
  lines, Session 995B provenance (see docstring line 5).
- Constructor: `__init__(user=None, sport_key: str = None)` at line
  35 — accepts optional user + sport filter; state minimal.
- Class docstring at lines 22-33 describes symmetric 5-agent
  orchestration.
- Public entrypoint: `generate_brief()` at line 39-96 — runs 5 agents
  sequentially, aggregates into brief dict.

**Orchestration sequence (verified via direct read of file):**

| Step | Line | Method | Agent | Method-call style |
|---|---|---|---|---|
| 1 | 59-62 | `_run_game_predictor(context)` | `GamePredictor` | `agent.execute(...)` at line 103 |
| 2 | 64-67 | `_run_odds_analyst(context)` | `SportsOddsAnalyst` | **`agent.run(...)`** at line 122 — inline comment: "Session 1206: `.run()` writes AgentExecution telemetry row (Layer 1 audit)" |
| 3 | 69-72 | `_run_arbitrage_detector(context)` | `ArbitrageDetector` | `agent.execute(...)` at line 140 |
| 4 | 74-77 | `_run_line_movement_analyzer(context)` | `LineMovementAnalyzer` | `agent.execute(...)` at line 158 — scope-boundary per §16 |
| 5 | 79-82 | `_run_sharp_action_detector(context)` | `SharpActionDetector` | `agent.execute(...)` at line 176 |
| 6 | 85 | `_build_executive_summary(brief)` | — | Aggregates text summary |
| 7 | 86 | `_extract_top_plays(brief)` | — | Ranks by confidence, returns top 10 |

**§1 Finding 1 asymmetry visible here in the table** — 4 `.execute()`
calls + 1 `.run()` call across a docstring that promises symmetric
5-agent orchestration. Rigby SIGN cycle Q4 / Q6 surface.

**Failure semantics:** Every `_run_*` helper wraps its call in
try/except and returns `None` on exception (verified — coordinator
lines 98-187). The main loop only appends to `brief['agents_run']` if
the returned value is truthy. `_build_executive_summary` defensively
uses `x or {}` to tolerate `None`. `_extract_top_plays` iterates over
`brief.get('predictions') or {}` etc. so `None` is not a KeyError but
brief still ships with partial state. See §1 Finding 9 for consumer
implications.

### 5.3 Dependency chain + god-service check

- **Total line count:** 2,622 across the 5 surfaces.
- **Largest single file:** `SportsOddsAnalyst` at 730 lines — well
  under the 3000-line god-service threshold (playbook §5.3).
- **Cross-domain imports out of Cat B:**
  - `SportsOddsAnalyst` imports `ml.auto_selection.TaskType` (line
    inferred from Sub-agent 2) → ML domain.
  - `GamePredictor` imports `sports.models.MLPrediction/Game/Team/League`
    → Sports app boundary (in-scope for Cat B write; not overcoupling).
  - `ArbitrageDetector` imports `core.services.human_attention_bridge.attention_bridge`
    at line ~637 → Human Interface domain.
  - All 4 agents import `ai_core.spiders.specialized.theodds_spider.TheOddsSpider`
    → Cat A boundary (in-scope for read; not overcoupling).
  - `SportsBettingCoordinator` imports each agent lazily (in-method) —
    no cross-domain overcouping beyond Django infrastructure.
- **No circular imports** observed at the agent-service layer per
  Sub-agent 2 report.

### 5.4 4-item pre-brief mini-schema per service (D62 fold)

| Service | (a) sports-only vs shared | (b) DBAO vs public | (c) integration posture | (d) island posture |
|---|---|---|---|---|
| `SportsOddsAnalyst` | sports-only (odds value-bet analysis specific) | public — no DBAO isolation | **extend** — could emit SignalCluster on high-confidence signals under integration posture; no refactor needed. Under integration posture, direct `get_openai_client()` should route through `LLMProviderRegistry` (currently inconsistent with siblings — §15 debt #2). | **strong isolation already** — stateless, fetches fresh Cat A data; island posture requires no additional isolation infra beyond documenting `SignalCluster` non-emission as intentional. |
| `GamePredictor` | sports-only | public | **extend** — could emit `SignalCluster.pattern_type='sports_prediction'` on top-confidence predictions (requires enum extension per §14.3). Outcome-feedback-loop bridge (from Cat C `BettingOutcomeVerifier`) is separately owed. | **isolation already strong** — MLPrediction write is the sole persistent side effect; island posture requires no additional isolation. Retention/TTL on MLPrediction would be needed under either posture. |
| `SharpActionDetector` | sports-only (multi-book divergence logic sports-specific) | public | **extend** — could emit `SignalCluster.pattern_type='sharp_action_signal'` on HOT signals (requires enum extension). LLMProviderRegistry usage consistent with GamePredictor. | **strong isolation** — stateless. Island posture requires no additional isolation. |
| `ArbitrageDetector` | sports-only (2-way + 3-way arb math sports-specific) | public | **refactor** — Cat B write surface (`ArbitrageOpportunity.objects.create()`) is missing; integration posture requires wiring `_create_arb_opportunity()` at `arbitrage_detector.py:498` to persist. Also could emit `SignalCluster.pattern_type='arbitrage_opportunity'`. | **posture-decision** — model exists but is unwritten. Island posture chooses: (a) delete model + admin + serializer + viewset (accept ephemeral-only design) OR (b) document as ephemeral-view-only vestige and accept read-only viewset returning empty queryset as intentional. Either choice is Cat F posture surface. |
| `SportsBettingCoordinator` | sports-only (multi-agent brief specific) | public — no DBAO isolation | **refactor** — asymmetric `.run()` / `.execute()` invocation surface (§1 Finding 1) requires reconciliation under either posture. Integration posture also requires emitting brief-level `SignalCluster` on top-play detection. | **extend** — coordinator is stateless orchestrator; island posture requires no additional isolation beyond documenting "brief is transient — do not persist to `BriefHistory`" if that were considered. `SportsBettingBrief` model reference in Sub-agent 3 report unverified in this audit; noted as UNKNOWN §20.3. |

---

## 6. Major APIs and Interfaces

**Q6 — What are the major APIs?**

### 6.1 REST — 9 endpoints (details §3.3)

All 9 REST endpoints instantiate Cat B agents or the coordinator per
request in the view function. Notable: `/api/v1/betting/brief/` at
`core/views_odds_sports.py:3248` calls
`SportsBettingCoordinator().generate_brief()` per request — this is
the same brief the daily-brief beat computes at 07:00 MT. Whether the
REST endpoint reads from a cache populated by the beat OR always
re-runs the coordinator (sub-agent 3 mentioned "cache + DB"
persistence with 6h TTL — UNVERIFIED here; deferred to §20.3) is
important for Cat D consumer contract.

### 6.2 WebSocket — 3 consumers, 0 agent-control channels for Cat B

Details §3.3. All 3 WS consumers are read-side data channels. No WS
message invokes a Cat B `.execute()` or `.run()`. WS payload
provenance (does Cat B write into the WS distribution path?) deferred
to Cat E audit S1505.

### 6.3 PA tools — 4 registered, 2 gaps (§1 Finding 2)

Details §3.4. `sports_odds_analyst` and `arbitrage_detector` are
absent from `tool_dispatcher.py:302-305`. This is drift or intentional
gate — Rigby SIGN cycle surface.

### 6.4 Discord bot commands — 1 Cat B-invoking

Details §3.5. Only `/arb` at `discord_bot.py:1260-1350` directly
invokes a Cat B agent (`ArbitrageDetector.run()`). No Discord
command invokes `SportsOddsAnalyst` / `GamePredictor` /
`SharpActionDetector` directly.

### 6.5 Discord `#boardroom` outbound (Cat A boundary)

Cat A's `_impl_collect_sports_odds_intelligence` (S1501 §6.5) posts a
30-min digest to `CHANNEL_BOARDROOM` via
`DiscordNotificationService.send_betting_digest()`. Cat B is
downstream (analytics consumers of the same odds data) but Cat B does
not post directly to Discord in its 4 audited agents + coordinator
(verified via Sub-agent 4 grep — no `Discord*` imports in
`core/agents/markets/*.py` or `core/services/sports_betting_coordinator.py`).

### 6.6 4-item pre-brief mini-schema per external surface (D62 fold)

| External surface | (a) sports-only vs shared | (b) DBAO vs public | (c) integration posture | (d) island posture |
|---|---|---|---|---|
| `/api/v1/betting/*` (4 endpoints) | sports-only | public URL namespace — no DBAO URL prefix on `main` HEAD | **extend** — endpoints could route through a caching layer or SignalCluster-write side effect under integration posture without URL change. | **refactor URL namespace** — if island posture chose DBAO codename materialization at URL level, `/api/v1/betting/*` would become `/dbao/api/v1/betting/*` or similar. Not zero-cost. |
| `/api/v1/sports/*` (5 endpoints) | sports-only | public URL namespace | **extend** — same as above | **refactor URL namespace** — same as above |
| WS `/ws/sports/updates/`, `/ws/live-sports/`, `/ws/arbitrage/` | sports-only | public WS namespace — parent §2.5 evidence table names `/ws/dbao/` as candidate but S1501 §3.3 confirmed it is test-only reference on `main` HEAD | **extend** — WS payloads could include Cat B signal emissions under integration posture without route change | **refactor WS namespace** — if island posture chose DBAO WS namespace, 3 routes migrate |
| PA tool `game_predictor` / `sharp_action_detector` / `prediction_market_analyst` / `line_movement_analyzer` (4 registered) | sports-only tool names | dispatcher-registry: public (`tool_dispatcher.py`) — no separate DBAO dispatcher | **extend** — add `sports_odds_analyst` + `arbitrage_detector` registrations (§14.2 remediation) under either posture; integration posture also adds SignalCluster write side effects | **extend** — same registrations under island posture; posture-neutral gap |
| Discord `/arb` command | sports-only | Discord (external service) | **extend** — `/arb` can post SignalCluster emissions to Discord threads under integration posture without command change | **extend** — no isolation change; Discord is external boundary |

---

## 7. Runtime Flows

**Q9 — What are the major runtime flows?**

### 7.1 Flow A — SportsBettingCoordinator daily brief generation (07:00 MT beat → brief dict)

**F1 fold — explicit call chain (Rigby SIGN cycle 1 Q1 + Q9 fold):**

```
Celery beat (crontab hour=7, minute=0)
    ↓  fires `generate-daily-betting-brief`  [core/celery.py:782-786]
        queue=default, expires=3600s
core.tasks.generate_daily_betting_brief(self)  [core/tasks.py:6188-6190]
    ↓  delegates to
core.tasks_content._impl_generate_daily_betting_brief(self)  [core/tasks_content.py:~3103]
    ↓  invokes
SportsBettingCoordinator().generate_brief()  [core/services/sports_betting_coordinator.py:39-96]
    ↓  sequentially invokes 5 agents (all in try/except; None on error):
    ├─ GamePredictor().execute(...)         [line 103 — .execute() = NO AgentExecution row]
    ├─ SportsOddsAnalyst().run(...)         [line 122 — .run() = 1 AgentExecution row (Session 1206 Layer 1)]
    ├─ ArbitrageDetector().execute(...)     [line 140 — .execute() = NO AgentExecution row]
    ├─ LineMovementAnalyzer().execute(...)  [line 158 — scope-boundary per §16; .execute() = NO AgentExecution row]
    └─ SharpActionDetector().execute(...)   [line 176 — .execute() = NO AgentExecution row]
    ↓  aggregates
_build_executive_summary(brief)  [line 189-225]  → brief['executive_summary']
_extract_top_plays(brief)        [line 227-290]  → brief['top_plays']
    ↓  return brief dict to _impl_generate_daily_betting_brief
Downstream persistence (F10 fold-verified):
    SportsBettingBrief.objects.create(...)  [core/tasks_content.py:3150]
    ALSO writable from run_all_desks_intelligence at core/tasks.py:12187 (Desk 2 Sports)
```

**Failure-mode semantics (F8 fold):** every `_run_*` helper catches
`Exception`, calls `logger.error(...)`, returns `None`. Coordinator
main loop appends agent name to `brief['agents_run']` ONLY if the
returned value is truthy. Brief still ships with `None` values in the
5 keyed slots (`predictions`, `odds_analysis`, `arbitrage`,
`line_movements`, `sharp_action`). Consumer contract on `None`
handling is undocumented at Cat B level; Cat D consumer contract
(brief → content pipeline) is deferred to S1504.

**Telemetry summary per single brief run (§1 Finding 1 anchor):**

| Signal | Count | Source |
|---|---|---|
| `AgentExecution` rows | 1 | SportsOddsAnalyst.run() only |
| `Deliverable` rows | 4 | one per Cat B audited agent via `_save_to_deliverable()` |
| `MLPrediction` rows | O(games-today) ≈ 30-100 | GamePredictor._store_predictions() |
| `HumanAttentionItem` rows | O(HOT+GOOD arbs) | ArbitrageDetector._create_attention_items() (0 if no arbs) |
| `SportsBettingBrief` rows | 1 | from `_impl_generate_daily_betting_brief` post-return |
| `SignalCluster` rows | 0 | §1 Finding 5 architectural gap |
| `Initiative` rows | 0 | §9 outbound MISSING |
| `EventLog` rows | 0 | §10.1 zero-events emitted |

**Step-by-step detail** (verified via direct read of `sports_betting_coordinator.py:39-96` + parent verifier-loop on `core/celery.py:782-786` + `core/tasks.py:6188` + `core/tasks_content.py:3150`):

1. **Celery beat** at 07:00 MT daily fires `generate-daily-betting-brief` (`core/celery.py:782-786`, `queue: default`, `expires: 3600s`).
2. **Task entry** `core.tasks.generate_daily_betting_brief` at `core/tasks.py:6188` delegates to `core.tasks_content._impl_generate_daily_betting_brief` (per Sub-agent 3).
3. **Coordinator instantiation:** `coordinator = SportsBettingCoordinator()` (default `user=None`, `sport_key=None`).
4. **`generate_brief()` starts** at line 39; initializes `brief = {'generated_at': ..., 'sport_filter': None, 'agents_run': [], 'errors': []}`.
5. **Agent 1 — GamePredictor** at `sports_betting_coordinator.py:59-62` → `_run_game_predictor(context)` → line 103 `GamePredictor().execute(task="Generate predictions for today's games", context=context)`. Returns `result.data` dict with `{predictions, total_games, predictions_stored, llm_analysis, provenance}` OR `None` on failure. **Side effect during this call:** `_store_predictions()` writes N `MLPrediction` rows via cascade of `.get_or_create()` on `League`/`Team`/`Game` + `.create()` on `MLPrediction` (`game_predictor.py:388-526`); one `Deliverable` row via `_save_to_deliverable()` at line 126.
6. **Agent 2 — SportsOddsAnalyst** at lines 64-67 → `_run_odds_analyst(context)` → line 122 **`SportsOddsAnalyst().run(task="Analyze today's betting markets for value opportunities", context=context)`** — the ONLY `.run()` call in the coordinator (§1 Finding 1). Returns `result.data` with `{events_analyzed, signals, analysis, structured_report, provenance, publishable}`. **Side effects:** `BaseAgent.run()` writes an `AgentExecution` row (Session 1206 Layer 1 audit) — the only telemetry-instrumented agent in this pipeline; `_save_to_deliverable()` writes one Deliverable at line 291; LLM call to OpenAI `gpt-5-mini` at line 619.
7. **Agent 3 — ArbitrageDetector** at lines 69-72 → `_run_arbitrage_detector(context)` → line 140 `ArbitrageDetector().execute(task="Scan for arbitrage opportunities across all active sports", context=context)`. Returns `result.data` with `{events_scanned, arbitrage_opportunities, hot_arbs, good_arbs}`. **Side effects:** `_create_attention_items()` writes N `HumanAttentionItem` rows for HOT/GOOD arbs at line 656; `_save_to_deliverable()` writes one Deliverable at line 178. **No AgentExecution row.**
8. **Agent 4 — LineMovementAnalyzer** at lines 74-77 (scope-boundary — see §16 for full flag). Returns `result.data` with `{movements, steam_moves, sharp_moves, ...}`. **Side effect:** reads `LegacySpiderData` at `line_movement_analyzer.py:181` (only Cat B-adjacent ORM read of Cat A persistence); writes one Deliverable. **No AgentExecution row.**
9. **Agent 5 — SharpActionDetector** at lines 79-82 → `_run_sharp_action_detector(context)` → line 176 `SharpActionDetector().execute(task="Identify sharp betting action and stale lines", context=context)`. Returns `result.data` with `{signals, hot_signals, warm_signals, events_with_divergence, llm_analysis}`. **Side effects:** LLM call via `LLMProviderRegistry` at line 355; `_save_to_deliverable()` writes one Deliverable at line 112. **No AgentExecution row.**
10. **Executive summary** at line 85 → `_build_executive_summary(brief)` aggregates text.
11. **Top plays** at line 86 → `_extract_top_plays(brief)` filters + ranks by confidence, returns top 10 across all agents.
12. **Return** brief dict at line 96 to caller (`_impl_generate_daily_betting_brief`).
13. **Downstream persistence** — Sub-agent 3 mentions `SportsBettingBrief` model + cache with 6h TTL as brief consumer. Not verified in this audit (§20.3); Cat D scope.

**Execution time:** Sub-agent 2 estimate 5-15s sequential per pipeline run. Not verified via runtime telemetry (Cat B has no `AgentExecution` rows for 4 of 5 agents).

**Telemetry count per brief run:** 1 `AgentExecution` row (SportsOddsAnalyst only), 4 `Deliverable` rows, N `MLPrediction` rows (from GamePredictor), N `HumanAttentionItem` rows (from ArbitrageDetector when HOT/GOOD present), 0 `SignalCluster` rows, 0 `Initiative` rows.

### 7.2 Flow B — GamePredictor making a prediction (execute → MLPrediction)

Step-by-step (verified via Sub-agent 1 model-write inventory + Sub-agent 2 flow trace):

1. **Entry:** caller invokes `GamePredictor().execute(task, context)` — via coordinator OR REST endpoint OR PA tool.
2. `_fetch_odds_data(context)` at `game_predictor.py:154-176` → `TheOddsSpider().fetch_data(sports=[sport_filter], max_results=50)`.
3. In-memory filter at line 167: `[e for e in events if e.get('data_type') == 'sports_odds']`.
4. `_generate_predictions(events)` at line 192-277 removes vig, detects value bets, calibrates confidence, returns prediction dicts.
5. `_get_llm_analysis(task, top_predictions, context)` at line 304-343 attempts LLM analysis via `LLMProviderRegistry.complete()` — tries `('openai', 'gpt-4.1-mini')` then `('anthropic', 'claude-sonnet-4-5-20250929')`.
6. `_store_predictions(predictions, context)` at line 388-526:
   - For each prediction: `League.objects.get_or_create(abbreviation=..., defaults={...})` (line 428-435). Auto-creates League if missing.
   - `_get_or_create_team(league, home_name)` + `_get_or_create_team(league, away_name)` (line 438-439). Auto-creates Team rows.
   - `Game.objects.get_or_create(external_id=event_id, ...)` (line 455-464). Auto-creates Game.
   - `MLPrediction.objects.create(game=game, predicted_winner=..., confidence=..., home_win_probability=..., away_win_probability=..., odds_at_prediction=..., ...)` (line 505-520). **This is Cat B's sole `MLPrediction` write path.**
7. `_save_to_deliverable()` at line 126 → one `Deliverable` row per execute.
8. Return `AgentResult(success=True, data={predictions, total_games, predictions_stored, llm_analysis, provenance})`.

**No AgentExecution row** — because coordinator uses `.execute()` not `.run()` for this agent (§1 Finding 1). If invoked via `.run()` (e.g., from `/api/v1/sports/analyze-game/` if that endpoint uses `.run()` — UNVERIFIED), one AgentExecution row would be written.

**Retention risk:** `MLPrediction` has no TTL. Each daily-brief run writes O(games-today) rows; ~30-100 rows/day depending on sport coverage. Unbounded growth over time.

### 7.3 Flow C — ArbitrageDetector detecting an arb (execute → HumanAttentionItem, NOT ArbitrageOpportunity)

Step-by-step (verified via Sub-agent 1 model-write inventory + Sub-agent 2 flow trace + parent verifier-loop grep on `ArbitrageOpportunity.objects.*`):

1. **Entry:** caller invokes `ArbitrageDetector().execute(task, context)` — via coordinator OR `/api/v1/betting/arbitrage/` OR Discord `/arb` OR PA tool dispatch (though PA tool NOT registered — §14.2).
2. `_get_multi_book_odds(context)` at line 213-237 → `TheOddsSpider().fetch_data(...)`.
3. In-memory filter at line 233: `[e for e in events if e.get('data_type') == 'sports_odds']`.
4. `_detect_arbitrage(events, context)` at line 254-303 classifies each event as 2-way or 3-way (based on `'soccer' in sport_key` string check — see §15 debt).
5. `_detect_2way_arbitrage(event, h2h_odds, min_profit)` at line 305-363 OR `_detect_3way_arbitrage(event, h2h_odds, min_profit)` at line 365-421 — pure math: extract best odds per outcome, calc implied probability sums, detect if sum < 100% (arb exists).
6. `_create_arb_opportunity(event, ...)` at line 498-558 computes stake distribution for $100 bankroll (inventory-only per parent §7 anti-scope #9), assigns rating (HOT ≥ 3% profit / GOOD 1-3% / MARGINAL / SKIP), returns arb dict.
7. `_create_attention_items(arb_opps)` at line 634-676:
   - For each arb with `rating in ('HOT', 'GOOD')`: `attention_bridge.create_arbitrage_attention(arb_opp)` at line 656.
   - **This writes `HumanAttentionItem` rows** for HOT/GOOD arbs.
   - **`ArbitrageOpportunity.objects.create()` is NEVER called** — verified via grep in `core/agents/markets/` returning 0 matches. §1 Finding 4.
8. `_save_to_deliverable()` at line 178 → one `Deliverable` row per execute.
9. Return `AgentResult(success=True, data={events_scanned, arbitrage_opportunities: [dicts...], hot_arbs, good_arbs})`.

**Consumer paths:**
- Coordinator brief consumes `AgentResult.data['arbitrage_opportunities']` as dicts for `_extract_top_plays` (lines 245-257 of coordinator).
- REST endpoint `/api/v1/betting/arbitrage/` returns the dict list directly (per Sub-agent 3).
- Discord `/arb` formats the dicts as a Discord embed (per Sub-agent 3).
- Frontend `/betting` Arbitrage tab reads from REST endpoint (Cat E boundary; not audited here).
- `sports.models.ArbitrageOpportunity` viewset at `sports/views.py:835` returns empty queryset — no producer writes to it.

**Telemetry:** 0 `AgentExecution` rows (coordinator + REST use `.execute()`; Discord `/arb` uses `.run()` per Sub-agent 3 — 1 AgentExecution row for Discord dispatches only), N `HumanAttentionItem` rows (for HOT/GOOD only), 1 `Deliverable` row per execute, 0 `ArbitrageOpportunity` rows, 0 `SignalCluster` rows.

### 7.4 Flow D (not present) — outcome feedback loop

**This flow does not exist.** `MLPrediction` rows accumulate; `BettingOutcomeVerifier` at `core/services/betting_outcome_verifier.py:21` (Cat C scope) settles wager outcomes; no code path routes settled outcomes back into Cat B agent context. Cat B is memoryless. See §1 Finding 6 + §9 Q15.

---

## 8. Data Ownership and Lifecycle

**Q16 — What data does it own?** Q17 — consumes? Q18 — produces?

### 8.1 Cat B owns

- `MLPrediction` rows (write surface: `GamePredictor._store_predictions()`)
- Auto-created `League` / `Team` / `Game` rows (via `.get_or_create()` from `GamePredictor` — cross-cutting with Cat C consumer patterns)
- `Deliverable` rows for Cat B agent executes (write surface: 4 agents × `_save_to_deliverable()`)
- `HumanAttentionItem` rows for HOT/GOOD arbs (write surface: `ArbitrageDetector._create_attention_items()`)

### 8.2 Cat B consumes

- `TheOddsSpider().fetch_data()` dict return from Cat A (in-memory filter on `data_type == 'sports_odds'` — §5.1)
- LLM providers via `LLMProviderRegistry` (`GamePredictor`, `SharpActionDetector`) and `get_openai_client()` (`SportsOddsAnalyst`) — Cat G LLM infra boundary
- `Game` / `Team` / `League` records — read side by `GamePredictor` during dedup

### 8.3 Cat B produces (for other domains)

- `MLPrediction` rows → Cat C `BettingOutcomeVerifier` retrospective read for accuracy calc; UI viewsets under Cat E; **no learning-loop return path**
- `Deliverable` rows → mainline Deliverable pipeline (Cat D boundary — content review, publish gate)
- `HumanAttentionItem` rows → Cat E frontend attention feed
- `AgentExecution` rows (SportsOddsAnalyst only) → Layer 1 audit / telemetry aggregation
- Brief dicts from `SportsBettingCoordinator.generate_brief()` → Cat D content pipeline (SPECULATIVE consumer chain), REST endpoint consumers

### 8.4 Retention

- `MLPrediction`: **no TTL** (§4.1). Unbounded growth.
- Auto-created `League` / `Team` / `Game`: no TTL. Bounded by upstream game frequency; benign.
- `Deliverable`: mainline Deliverable retention policy applies (Session 1176+ context; deferred to Group 1600 audit).
- `HumanAttentionItem`: mainline HumanAttention retention applies; ArbitrageDetector attention items may have their own ephemerality (stale-line closure) — UNKNOWN whether the attention_bridge marks them as expired post-close.
- `AgentExecution` (from SportsOddsAnalyst only): Layer 1 audit retention (Session 1206 mainline policy) — deferred.

### 8.5 Idempotency

- `MLPrediction` — `unique_together=('game', 'model_used', 'created_at')` provides row-level idempotency; but `created_at=timezone.now()` on each execute means multiple runs at different timestamps for same (game, model) create multiple rows. Per-day-idempotency requires caller to enforce; Cat B does not.
- `HumanAttentionItem` from ArbitrageDetector — no visible dedup in this audit; UNKNOWN whether `attention_bridge` uses content hash or timestamp for dedup.
- `Deliverable` — one row per execute; no dedup.

### 8.6 4-item pre-brief mini-schema per data owned (D62 fold)

| Data owned | (a) sports-only vs shared | (b) DBAO vs public | (c) integration posture | (d) island posture |
|---|---|---|---|---|
| `MLPrediction` rows | sports-only | public sports app | **extend** — add outcome-feedback path (Cat C → Cat B `MLPrediction.was_correct` write bridge already latent via `calculate_accuracy()` but no return-loop). Also could add FK to `SignalCluster` under integration posture. | **strong isolation** — MLPrediction has no cross-domain FK inbound (`UnifiedAgentTemplate` SET_NULL is a nullable soft ref). Island posture requires retention/TTL to bound growth. |
| Auto-created `League` / `Team` / `Game` | sports-only | public sports app | **extend** — cross-book fixture-identity reconciliation could add `Game.external_id_map` JSONField. Would tie `theodds_event_id` ↔ `kalshi_ticker` ↔ canonical `game_id`. | **extend** — no isolation change needed. Cat C wager tracking already reads these; island posture accepts internal shared read-surface. |
| `Deliverable` rows | shared (mainline) | public core app | **N/A** — shared write surface; not Cat B decision | **N/A** — same |
| `HumanAttentionItem` rows (arbitrage) | shared (mainline) | public core app | **extend** — HOT/GOOD attention emission could also emit `SignalCluster.pattern_type='arbitrage_opportunity'` (requires enum extension) under integration posture. | **extend** — no isolation change; HumanAttention is already lightweight boundary. |
| `AgentExecution` rows (SportsOddsAnalyst only) | shared (mainline) | public core app | **refactor** — reconcile coordinator `.run()` / `.execute()` asymmetry so all 5 pipeline paths write AgentExecution. Integration posture requires uniform telemetry. | **refactor** — same asymmetry reconciliation is posture-neutral debt (§15 debt #1 HIGH). |
| Brief dicts (`generate_brief()` return) | sports-only | public — no DBAO API surface | **extend** — brief could gain `signal_emissions: [...]` key naming `SignalCluster` rows written this run. | **extend** — brief is transient; if `SportsBettingBrief` persistent model exists (SPECULATIVE — §20.3), island posture may want retention/TTL. |

---

## 9. Integrations With Other Domains

**Q14** — integrations it has. **Q17** — data consumed. **Q18** — data produced. **Q21** — inbound consumers. **Q22** — outbound dependencies. **Q23** — model overlap.

### 9.1 Integration strength table (per playbook §12 classification)

| Cat B ↔ other domain | Direction | Strength | Evidence (file:line) |
|---|---|---|---|
| **Cat B ↔ Cat A (Odds Ingestion / S1501)** | Inbound | **STRONG** | 4 agent filter sites (`sports_odds_analyst.py:354`, `game_predictor.py:167`, `sharp_action_detector.py:159`, `arbitrage_detector.py:233`) all read `TheOddsSpider().fetch_data()` dict return. LineMovementAnalyzer additionally ORM-reads `LegacySpiderData` at `line_movement_analyzer.py:181` (scope-boundary). |
| **Cat B ↔ Signal Engine** | Bidirectional | **MISSING** | Zero SignalCluster writes from Cat B (verified via targeted grep — `core/agents/markets/` has 0 matches for `SignalCluster.objects.*`). Signal Engine `pattern_type` enum lacks sports types (`core/models_signal_intelligence.py:75-86` verified — 10 non-sports types only). §1 Finding 5 + §14.3. |
| **Cat B ↔ Initiative pipeline** | Outbound | **MISSING** | Zero `Initiative.objects.create()` writes from Cat B (verified). No auto-initiative-generation from high-confidence predictions or arbs. Delegated to posture-decision architecture. |
| **Cat B ↔ MLPrediction (sports app)** | Outbound | **STRONG (write) / WEAK (read-back)** | GamePredictor writes at `game_predictor.py:505`. Read-back path (from `BettingOutcomeVerifier` → next-generation Cat B context) is MISSING. §1 Finding 6. |
| **Cat B ↔ Cat C (Wager Tracking / BettingOutcomeVerifier — S1503 scope)** | Bidirectional | **PARTIAL forward / MISSING backward** | Forward: `MLPrediction` accumulates for Cat C to read against wager settlement (SPECULATIVE — Cat C audit S1503 owns this evidence). Backward: no code path routes settled outcomes back to Cat B for calibration. §1 Finding 6. |
| **Cat B ↔ Cat D (Content Pipeline — S1504 scope)** | Outbound | **PARTIAL** | Brief dict from `SportsBettingCoordinator.generate_brief()` feeds `_impl_generate_daily_betting_brief` at `core/tasks_content.py`. SPECULATIVE consumer of brief in downstream content deliberation — Cat D audit S1504 owns this evidence. |
| **Cat B ↔ Cat E (Frontend — S1505 scope)** | Outbound | **STRONG (via REST)** | 9 REST endpoints under `/api/v1/betting/*` and `/api/v1/sports/*` feed `BettingPage.tsx`. WS distribution paths for arbitrage / sports updates are unverified from Cat B write side (WS is Cat E consumer surface). |
| **Cat B ↔ Memory Domain (S1300 Memory — closed at S1399)** | Bidirectional | **MISSING** | Zero reads or writes of `AgentMemory` / `AgentKnowledgeSource` from `core/agents/markets/*.py`. `_record_learning_outcome` mixin used at `sports_odds_analyst.py:258-266` + `arbitrage_detector.py:166-175` but emits log lines only — no persist to Memory Domain (verified via Sub-agent 4 tracing). §1 Finding 7. |
| **Cat B ↔ Advisor / UnifiedUser** | Inbound | **MISSING** | No `Advisor.objects.get/filter()` reads in Cat B files. No `UnifiedUser.learning_history` consumption. Agents are context-agnostic. |
| **Cat B ↔ LLM providers (Cat G)** | Inbound | **STRONG** | `SportsOddsAnalyst` direct via `get_openai_client()` at line 619; `GamePredictor` + `SharpActionDetector` via `LLMProviderRegistry.complete()` at lines 335 / 355. `ArbitrageDetector` has zero LLM calls (heuristic-only). |
| **Cat B ↔ Deliverable (shared mainline model)** | Outbound | **STRONG** | All 4 audited agents call `_save_to_deliverable()` on each execute (Session 1006 mixin standardization). |
| **Cat B ↔ HumanAttention (shared mainline)** | Outbound | **PARTIAL** | ArbitrageDetector for HOT/GOOD arbs at `arbitrage_detector.py:656`. SportsOddsAnalyst has a `_maybe_create_attention_item()` stub at line 288 (per Sub-agent 4) — call site status UNKNOWN. Other 2 agents (GamePredictor, SharpActionDetector) do not emit HumanAttention. |
| **Cat B ↔ Discord (via DiscordNotificationService)** | Outbound | **MISSING** — direct grep of `core/agents/markets/*` for `Discord*` returns 0 matches. Discord `/arb` reaches Cat B *inbound* (from Discord bot Cog to `ArbitrageDetector.run()`); Cat B does not push to Discord. Cat A `_impl_collect_sports_odds_intelligence` posts to Discord (S1501 §6.5) — that is Cat A boundary. |
| **Cat B ↔ EventBus / EventLog** | Bidirectional | **MISSING** | Zero `emit_event()`, `publish()`, `EventLog.objects.create()`, `EventStream*` calls in any Cat B surface (verified via Sub-agent 4). Consistent with S1274 finding that EventBus is weakly adopted platform-wide. |

**Q15 — What integrations are missing?** Named explicitly per row above:
Signal Engine writes; Initiative auto-creation; Memory Domain
bridge; outcome-to-agent feedback loop; Advisor context injection;
EventBus participation; Discord push (Cat B does not directly post,
though Cat A does adjacent). Each is a posture-decision surface owed
to Cat F evidence plan; whether "missing" is drift or intentional
island shape is Chris-gated per S1274 §12.3 + D59.

**Q21 — What other domains depend on Cat B?**

- Cat D content pipeline reads brief dicts from `generate_brief()` (SPECULATIVE chain via `_impl_generate_daily_betting_brief`).
- Cat E frontend reads Cat B REST endpoints for the 9-tab `BettingPage.tsx` (verified consumer path via Sub-agent 3 → `frontend/src/pages/BettingPage.tsx` calls `/api/v1/betting/*`).
- Cat C `BettingOutcomeVerifier` reads `MLPrediction` rows for accuracy tracking (SPECULATIVE — Cat C audit S1503 verifies).
- Discord bot `SpiderCommands` Cog invokes `ArbitrageDetector.run()` via `/arb` command.
- PA (Rigby) dispatches via 4 registered tools (`game_predictor`, `sharp_action_detector`, `prediction_market_analyst`, `line_movement_analyzer`).

**Q22 — What domains does Cat B depend on?**

- Cat A ingestion (STRONG — TheOddsSpider dict return contract).
- LLM providers Cat G (STRONG — OpenAI + Anthropic via registry / factory).
- `BaseAgent` mixins from `core/agents/base_agent.py` (STRONG — `_save_to_deliverable`, `time_travel_session`, `_record_learning_outcome`, `.run()` telemetry, `AgentResult` shape).
- `human_attention_bridge` from `core/services/human_attention_bridge.py` (PARTIAL — ArbitrageDetector only).
- `agents_registry.UnifiedAgentTemplate` (soft ref via `MLPrediction.agent` FK, SET_NULL).
- Django ORM (`sports.models.MLPrediction` / `Game` / `Team` / `League`).

**Q23 — What models overlap with other domains?**

- `Game` / `Team` / `League` — auto-created by GamePredictor; also read by Cat C `PlacedWager.game` FK. Overlap is deliberate (dedup via `external_id`); not a duplicate-model defect.
- `Deliverable` — shared mainline model; not overlap (multi-writer by design).
- `HumanAttentionItem` — shared mainline model; not overlap.

---

## 10. Event Flows

**Q19 — What events does Cat B emit?** **Q20 — What events should it emit?**

### 10.1 Events emitted today

**None** — zero calls to `emit_event()`, `publish()`,
`EventLog.objects.create()`, `AgentEvent*`, or `EventStream*` in any of
the 5 Cat B surfaces (verified via Sub-agent 4 grep).

### 10.2 Events that should be emitted (per S1274 §6 gap lens + integration posture)

The following events would be candidates under integration posture; none are Cat B's contract today:

- `sports_prediction.high_confidence` — when `GamePredictor` returns a prediction with `confidence >= 80`.
- `sports_arbitrage.detected_hot` — when `ArbitrageDetector` finds a HOT arb (≥ 3% profit).
- `sports_sharp_action.divergence_hot` — when `SharpActionDetector` finds a HOT signal (divergence ≥ 30).
- `sports_brief.daily_generated` — when `SportsBettingCoordinator.generate_brief()` completes.
- `sports_outcome.settled` — when Cat C `BettingOutcomeVerifier` settles a wager (Cat C event, but Cat B would consume it for calibration).

None of these exist as EventLog rows or event bus topics today. All would need to be defined + emitted + consumed — non-trivial refactor. Cat F posture-decision framing owes: enumerate the events needed under integration posture; enumerate the "no events emitted" contract needed under island posture.

### 10.3 Latent event-like surfaces

- `HumanAttentionItem` rows function as **event-like notifications** for
  arbitrage HOT/GOOD; but they are ORM rows, not events. Consumers must
  poll or subscribe to a Django signal.
- `Deliverable` rows emit `deliverable_updated` Django signal (Session
  1006 pattern) — this is a proto-event but scoped to Deliverable
  lifecycle, not Cat B semantics.

---

## 11. Existing Documentation

**Q10 — What existing documentation exists?**

### 11.1 Topic docs (`docs/topics/`)

- **No dedicated Cat B topic doc.** `docs/topics/sports*.md`,
  `docs/topics/betting*.md`, `docs/topics/*prediction*.md` do not exist
  (verified via Sub-agent 5 + parent §6 flag).
- `docs/topics/agent-system.md:42` — lists `SportsBettingCoordinator`
  in the Intelligence Desks table with description "5 agents
  (predictor/odds/arbitrage/line/sharp) | On-demand only". Note:
  "On-demand only" contradicts §3.1 evidence — coordinator IS beat-scheduled at 07:00 MT daily (`core/celery.py:782-786`). Documentation drift §14.5.
- `docs/topics/spider-network.md` — mentions `TheOddsSpider` and
  sports pipeline (per Sub-agent 5 cross-ref). Cat A boundary — S1501
  §11 owned.
- `docs/topics/stock-intelligence.md` — companion topic for stocks
  (referenced by SPORTS_MONETIZATION_ML.md as parallel structure).
- `docs/topics/celery-workers.md` — sports queue coverage referenced
  by SPORTS_MONETIZATION_ML.md §5.

### 11.2 Narratives (`docs/narratives/`)

- `docs/narratives/SPORTS_MONETIZATION_ML.md` (Session 1158, last
  updated 2026-05-25) — primary Cat B narrative.
  - §2 CoreObjects & Vocabulary:
    - `GamePredictor` at line 77 — "Produces `MLPrediction` rows. Auto-creates League → Team → Game → MLPrediction chain (Session 1010). 21 `SPORT_KEY_LEAGUE` mappings...Predictions > 14 days in future filtered out."
    - `SharpActionDetector` at line 79 — "Per-bookmaker odds divergence analyzer. Filters extreme odds (abs > 10,000)...HOT (≥ 30 divergence) or WARM (≥ 15). LLM prompt produces structured advice...13 sport keys supported."
  - `sports_odds_analyst` and `arbitrage_detector` **not named** by
    file/class in §2 — Sub-agent 5 flagged this explicit absence.
  - §6 Open Questions at line 158 — "SharpActionDetector LLM
    dependency. The structured advice comes from an LLM call; if the
    LLM drifts in output format, the signal cards...may render
    incorrectly." Aligns with §14.4 drift observation on output-shape
    fragility.
  - No SLA / no output-schema contract / no backward-compat guarantee
    stated.

### 11.3 Handoffs (`docs/handoffs/`) — 5 most-recent Cat B mentions

| Session | File | Line | Cat B claim |
|---|---|---|---|
| 1501 | `SESSION_1501_SPORTS_CAT_A_AUDIT.md` | 99 | Cat B agents filter `data_type == 'sports_odds'` — S1501 documents S1502 owes verification |
| 1501 | `SESSION_1501_SPORTS_CAT_A_AUDIT.md` | 92 | P2 slot named as `sports_odds_analyst.py` + `game_predictor.py` + `sharp_action_detector.py` + `arbitrage_detector.py` + `SportsBettingCoordinator` |
| 1500 | `SESSION_1500_SPORTS_ARC_OPEN.md` | 76 | P2 S1502 depends on P1 data surface |
| 1246 | (Session 1246 close) | inferred | SportsOddsAnalyst + ArbitrageDetector last-modified 2026-06-27 per Sub-agent 6 git-log |
| 1206 | Coordinator .run() comment provenance | verified `sports_betting_coordinator.py:120` — "Session 1206: `.run()` writes AgentExecution telemetry row (Layer 1 audit)" | Layer 1 audit rollout to sports pipeline. Only SportsOddsAnalyst was migrated — §1 Finding 1 |
| 1205 | (Session 1205 close) | per Sub-agent 6 — DEAD classification of 7 sports-betting agents pre-S1205 remediation | Historical maturity anchor for §13 verdict |
| 1010 | `SESSION_1010_SPORTS_PREDICTIONS_AND_SYSTEM_CLEANUP.md` | inferred | GamePredictor auto-create chain established |
| 1012 | `SESSION_1012_BETTING_TABS_POLISH.md` | inferred | SharpActionDetector recs + home_team/away_team added |
| 1000 | `SESSION_1000_INTELLIGENCE_DESKS.md` | 34 | Sports Desk table lists 5 agents |
| 995B | `SESSION_995B_SPORTS_BETTING_INTELLIGENCE.md` | 54, 114 | Original SportsBettingCoordinator provenance |

**Session first-appearance by agent:**
- `GamePredictor`: S1010+ (auto-create chain)
- `SharpActionDetector`: S1012+ (rec surface)
- `SportsBettingCoordinator`: S995B (initial build)
- `sports_odds_analyst`, `arbitrage_detector`: **first named-mention in S1501** (2026-07-01) — no prior session handoff by file name (per Sub-agent 5)

### 11.4 Research library entries

| Doc | §-ref | Cat B coverage |
|---|---|---|
| `ARCHITECTURE_INDEX.md` v28 | §1.31 | S1501 references "4 market agents" without file-name inventory; defers to S1502 |
| `platform_architecture_inventory.md` | §3.10 | S1273 Sports Intelligence / Betting Pipeline LIGHT baseline lists 6 Markets agents (SportsOddsAnalyst, ArbitrageDetector, GamePredictor, LineMovementAnalyzer, SharpActionDetector, BookmakerAgent) — does NOT name `SportsBettingCoordinator` |
| `cross_domain_integration_audit.md` | §14 Finding #6 | S1274 "sports_odds not a SignalCluster.pattern_type" — extends here to Cat B write-side (§1 Finding 5) |
| `1500_sports_domain_scoping.md` | §6 (lines 660-664) | P1/P2 parked issue #2 — whether Cat B agents write to `MLPrediction`. This audit answers: YES (GamePredictor only). |
| `1501_sports_odds_ingestion_normalization_audit.md` | §2.1 | Cat A contract statement — Cat B's load-bearing input |

### 11.5 `PLATFORM_WHAT_IT_IS.md` + `PLATFORM_INVENTORY.md` + `CLAUDE.md`

- `PLATFORM_WHAT_IT_IS.md:209` lists `SportsOddsAnalyst` in Markets
  agent category.
- `PLATFORM_INVENTORY.md` lists 6 Markets agents (regenerable).
- Neither doc documents Cat B agent output shapes, coordinator wiring,
  or direct-consume filter rationale.
- `CLAUDE.md` mentions `docs/topics/agent-system.md` as an entry
  point; Cat B is not called out explicitly.

---

## 12. Research Coverage

**Q11 — What research already exists?** **Q13 — What is the research coverage?**

### 12.1 Prior research entries covering Cat B

- S1273 §3.10 — LIGHT (row-level naming of 6 agents + `SportsBettingCoordinator` not named)
- S1274 §14 Finding #6 + §12.3 — cross-domain gap identification + posture-decision framing (structural, not Cat B-scoped audit)
- SPORTS_MONETIZATION_ML.md (S1158) — narrative on GamePredictor + SharpActionDetector; silent on sports_odds_analyst + arbitrage_detector
- S1500 parent scoping — flags Cat B parked questions (§6) but does not audit
- S1501 §2.1 Cat A contract statement — establishes Cat B's load-bearing input
- **This audit (S1502)** — first dedicated Cat B research

### 12.2 Research coverage classification (per playbook §12)

**Verdict: MOVING FROM LIGHT TO MODERATE.**

- **LIGHT baseline (pre-S1502):** row-level naming in inventory +
  narrative coverage of 2 of 4 agents + no output-shape docs + no
  coordinator wiring docs + no direct-consume pattern rationale.
- **This audit lands (S1502 close):** all 4 agents + coordinator
  inventoried, 28 canonical questions answered, drift matrix, debt
  matrix, integration strength table, runtime flows, 4-item pre-brief
  mini-schemas per (§4.7 / §5.4 / §6.6 / §8.6). This satisfies
  playbook §12 MODERATE threshold ("at least one focused doc or
  meaningful canonical documentation exists").
- **Would reach DEEP:** if a `docs/topics/sports-prediction-analytics.md`
  narrative doc were created post-S1504 or S1506, consolidating Cat B
  findings with output schemas.
- **Would reach CANONICAL:** if the Group 1500 xx99 (S1599) canonical
  summary lands AND anchor updates propagate to
  `PLATFORM_INVENTORY.md` §3.10 subdivision + `PLATFORM_WHAT_IT_IS.md`
  narrative additions.

Coverage count summary post-S1502:
- Agents inventoried in code: 6 Markets agents named
- Agents with dedicated §5-style inventory in research library: 4 (+ 2 flagged as scope-boundary — LineMovementAnalyzer, PredictionMarketAnalyst)
- Coordinator inventoried: 1 (this audit §5.2)
- Direct-consume pattern rationale documented: yes (this audit §5.1 + §1 Finding 3)
- 28 canonical questions answered: yes (this audit §2-§10, §14-§19)

---

## 13. Architecture Maturity

**Q12 — What is the architecture maturity?**

### 13.1 Classification (playbook §12): **PARTIAL (armed but under-instrumented)**

- **PARTIAL** because: (a) the pipeline is armed and runs — beat fires
  07:00 MT daily, coordinator invokes 5 agents, brief lands; (b) 4 of
  5 agents lack Layer 1 telemetry (§1 Finding 1); (c) Signal Engine
  integration is absent for sports pattern types (§1 Finding 5); (d)
  no outcome-feedback loop (§1 Finding 6); (e) 2 of 4 audited agents
  are missing from PA tool dispatcher (§1 Finding 2); (f)
  `ArbitrageOpportunity` model has full admin/serializer/viewset but
  zero write path (§1 Finding 4).
- **Not WORKING** because: WORKING per playbook §12 requires
  "operational, used, but with gaps or drift". Cat B is operational
  but the drift is severe enough (asymmetric telemetry, unwritten
  persistence surfaces, missing PA discoverability) that "PARTIAL"
  better matches the shape.

### 13.2 Rationale for PARTIAL over WORKING

**Session-1205 DEAD-classification residue.** Per Sub-agent 6 report:
Session 1205 audit found all 7 sports-betting agents classified DEAD
(zero 30-day invocations before S1205); producer beat tasks were
never scheduled. Session 1205 remediation added the beat schedule +
migrated `SportsOddsAnalyst` to `.run()` for Layer 1 telemetry
(Session 1206). Between S1205 and S1502, the pipeline moved from
DEAD to ARMED — but the migration is incomplete on 4 of 5 agents
(telemetry asymmetry) and on 2 of 4 audited agents (PA registry).

**S1501 precedent.** S1501 rated Cat A "WORKING (fragile contract) at
ingestion, PARTIAL at normalization" — a two-tier verdict where
ingestion ran cleanly but normalization was contract-fragile. Cat B's
verdict "PARTIAL (armed but under-instrumented)" is single-tier
because the observation-fragility crosses the whole pipeline: even the
ingestion side of Cat B's read contract (in-memory filter on dict
`data_type`) inherits Cat A's schema-invariance fragility as an
input-brittleness.

**Continuous-language check** (playbook §12 EventBus lesson): binary
"DEAD" or "OPERATIONAL" would be wrong. PARTIAL correctly captures
"code is complete, beats fire, but self-instrumentation and downstream
signal-emission are partial adoption".

### 13.3 Rigby SIGN Q2 / Q3 anticipated pressure

Rigby may pressure-test:

- Overstated maturity: is PARTIAL under-selling — should Cat B be
  WORKING because the pipeline ships briefs daily? Predicted response:
  the observability gap (4/5 telemetry-missing + 2/4 PA-missing) is
  load-bearing for operational visibility; without it, "WORKING" would
  imply the pipeline is self-monitoring, which it isn't.
- Understated maturity: is PARTIAL over-selling — should Cat B be
  EXPERIMENTAL because the outcome-feedback loop is missing?
  Predicted response: EXPERIMENTAL requires "prototype, unstable,
  unclear ownership". Cat B is stable in code + has clear ownership
  (all 5 surfaces authored by Chris/clwest per Sub-agent 6 git-log).
  EXPERIMENTAL is wrong.

---

## 14. Known Drift

**Q27 — What is drift?**

### 14.1 Coordinator `.run()` vs `.execute()` asymmetry (HIGH)

- **Doc claim:** `SportsBettingCoordinator` class docstring at
  `core/services/sports_betting_coordinator.py:22-33` describes a
  symmetric 5-agent orchestration pipeline.
- **Runtime evidence:** 4 `.execute()` calls (lines 103, 140, 158, 176) +
  1 `.run()` call (line 122, with explicit "Session 1206" comment).
- **Severity: HIGH.** 4 of 5 pipeline paths bypass Layer 1
  AgentExecution telemetry — the very audit trail Session 1206
  introduced. This is the load-bearing operational-drift finding of
  this audit. See §1 Finding 1.

### 14.2 PA tool registry gap for `sports_odds_analyst` + `arbitrage_detector` (MED-HIGH)

- **Doc claim:** `docs/topics/agent-system.md:42` says
  `SportsBettingCoordinator` orchestrates 5 sports agents on-demand.
- **Runtime evidence:** `core/services/tool_dispatcher.py:302-305`
  registers 4 handlers (`prediction_market_analyst`, `game_predictor`,
  `line_movement_analyzer`, `sharp_action_detector`).
  `sports_odds_analyst` and `arbitrage_detector` are NOT in the
  registry. `pa_tool_schemas.py:1146` names "game predictor, line
  movement, sharp action, prediction market analyst" — consistent
  with dispatcher (4).
- **Severity: MED-HIGH.** Rigby cannot surgically dispatch these two
  agents by name via PA. Discovery + debugging via PA are constrained
  to the coordinator or raw AGENT_MAP path. See §1 Finding 2.

### 14.3 `SignalCluster.pattern_type` enum still lacks sports types (HIGH — cascade from S1274 §14 Finding #6)

- **Doc claim:** S1274 §14 Finding #6 "sports_odds not a valid
  SignalCluster.pattern_type".
- **Runtime evidence:** `core/models_signal_intelligence.py:75-86`
  declares 10 choices; none are sports. Verified via direct read.
- **Severity: HIGH.** Materialization same shape as S1501 §14.1 for
  Cat A `SpiderData` enums; extends to Cat B consumer side. Integration
  posture requires enum extension + write path. Both are missing. See
  §1 Finding 5.

### 14.4 `ArbitrageOpportunity` model has admin + serializer + viewset but zero producer (MED-HIGH)

- **Doc claim:** `sports/models.py:1292` model class + `sports/admin.py:454`
  admin + `sports/serializers.py:405` serializer + `sports/views.py:835`
  `ReadOnlyModelViewSet` all present.
- **Runtime evidence:** Zero writes to `ArbitrageOpportunity.objects.*`
  in Cat B (verified via targeted grep). ArbitrageDetector returns
  dicts and creates HumanAttentionItem rows, not ArbitrageOpportunity
  rows.
- **Severity: MED-HIGH.** Full admin/serializer/viewset triple is
  dormant. See §1 Finding 4.

### 14.5 `docs/topics/agent-system.md` "on-demand only" claim (LOW)

- **Doc claim:** `docs/topics/agent-system.md:42` says
  `SportsBettingCoordinator` runs "On-demand only".
- **Runtime evidence:** Beat schedule fires
  `generate-daily-betting-brief` at 07:00 MT daily
  (`core/celery.py:782-786`). Beat entry expresses schedule, not just
  on-demand.
- **Severity: LOW.** Documentation drift; the daily beat schedule
  contradicts "on-demand only" phrasing. Correct at doc-refresh time.

### 14.6 Hardcoded LLM model IDs bypass factory pattern (MED)

- **Doc claim:** memory rules `feedback_openai_client_factory.md` and
  `feedback_anthropic_client_factory.md` mandate all clients use
  factory; hardcoded models are a debt smell.
- **Runtime evidence:**
  - `sports_odds_analyst.py:619` — `model="gpt-5-mini"` hardcoded.
  - `game_predictor.py:335` — `[('openai', 'gpt-4.1-mini'), ('anthropic', 'claude-sonnet-4-5-20250929')]` fallback tuple hardcoded.
  - `sharp_action_detector.py:355` — same hardcoded fallback tuple.
- **Severity: MED.** Model retire = 3 files to patch. Note:
  SportsOddsAnalyst also bypasses LLMProviderRegistry — inconsistent
  with sibling agents. See §15 debt #2.

### 14.7 Success-semantics drift on empty upstream (MED)

- **Doc claim:** BaseAgent `.execute()` contract typically returns
  `AgentResult(success=True)` when analysis completes, `success=False`
  when analysis fails.
- **Runtime evidence:** Sub-agent 6 flagged: Cat B agents
  (`sports_odds_analyst.py:224-230`, `arbitrage_detector.py:146-152`)
  return `success=True, data={'status': 'no_data'}` when the spider
  returns zero events. Session 1246 provenance per Sub-agent 6 —
  intentional per S1247 lane K but not surfaced in docstrings.
- **Severity: MED.** Downstream consumers (coordinator brief,
  Deliverable renderers) must special-case "success but no_data".
  Reframe candidate per S1501 F6 "unimplemented expectation" precedent.

### 14.8 Inherited from S1501: `data_type` filter is on spider-return dict, not persisted enum (MED — cascade)

- **Doc claim:** S1500 parent §3.B implies agents filter `SpiderData.data_type == 'sports_odds'` (ORM query shape).
- **Runtime evidence:** Filter is on the in-memory dict returned by
  `TheOddsSpider().fetch_data()` (verified 4 filter sites — §5.1). Cat A's
  silent-enum violation (S1501 §14.1) coupled with this coupling means
  a Cat A enum fix could break Cat B silently. See §1 Finding 3.
- **Severity: MED cascade** from S1501 §14.1 HIGH.

---

## 15. Known Technical Debt

**Q26 — What is technical debt?**

### 15.1 Debt matrix

| # | Debt | Severity | Location | Notes |
|---|---|---|---|---|
| 1 | Coordinator `.run()` / `.execute()` asymmetry — 4 of 5 pipeline paths bypass Layer 1 telemetry | **HIGH** | `sports_betting_coordinator.py:103`, `140`, `158`, `176` (4 `.execute()` calls) vs `:122` (1 `.run()` call) | §1 Finding 1; §14.1. Fix requires either (a) migrate all 4 to `.run()` (uniform Layer 1 audit; ~4 line edit) OR (b) document the asymmetry in class docstring as intentional. Path (a) is posture-neutral debt paydown; path (b) is documentation-only. |
| 2 | PA tool registry gap for `sports_odds_analyst` + `arbitrage_detector` | **MED-HIGH** | `tool_dispatcher.py:302-305` missing 2 registrations | §1 Finding 2; §14.2. Fix requires 2 `self.register(...)` lines. Posture-neutral. |
| 3 | `ArbitrageOpportunity` model dormant (admin/serializer/viewset triple with no producer) | **MED-HIGH** | `sports/models.py:1292` + `sports/admin.py:454` + `sports/serializers.py:405` + `sports/views.py:835` | §1 Finding 4; §14.4. Requires posture decision: persist (wire `_create_arb_opportunity()` in `arbitrage_detector.py:498` to also call `ArbitrageOpportunity.objects.create()`) OR remove (delete model + admin + serializer + viewset + migration). Not posture-neutral. |
| 4 | Hardcoded LLM model IDs bypass factory | **MED** | `sports_odds_analyst.py:619`, `game_predictor.py:335`, `sharp_action_detector.py:355` | §14.6. Migrate SportsOddsAnalyst to `LLMProviderRegistry` for consistency with siblings; move model tuple to config. |
| 5 | Inconsistent output-shape key naming across agents | **LOW-MED** | 4 agents produce 4 different key names (`signals`, `predictions`, `signals`, `arbitrage_opportunities`) | Consumer code (`_extract_top_plays` in coordinator) compensates with defensive `.get(...)` + hardcoded per-agent iteration. Refactor to shared schema is bounded but touches all 4 agents + coordinator. |
| 6 | Silent `ImportError` on missing `sports.models` in GamePredictor | **MED** | `game_predictor.py:391-396` | Wraps `from sports.models import MLPrediction, ...` in try/except; on failure logs warning + returns 0 stored. Blast radius bounded (only prediction storage skipped) but consumer sees `predictions_stored=0` without failure signal. |
| 7 | No retry / exponential backoff / circuit breaker on spider failures | **MED** | `arbitrage_detector.py:235-237`, `sports_odds_analyst.py:361-363`, similar sites | Returns empty list on `TheOddsSpider().fetch_data()` exception; cascades into "no_data" classification (§14.7). Retry logic would be posture-neutral resilience improvement. |
| 8 | Duplicate implied-probability computation across 2 agents | **LOW** | `arbitrage_detector.py:_remove_vig` + `game_predictor.py:_remove_vig`-style logic | Code duplication; shared utility module (`core/utils/betting_math.py`) would centralize. Bounded refactor. |
| 9 | 3-way market detection via `'soccer' in sport_key` string prefix | **LOW** | `arbitrage_detector.py:276-280` (per Sub-agent 6) | If TheOdds API adds a new soccer variant (`soccer_uefa_champs_2027`), the prefix still matches. If a non-soccer 3-way sport is added, string-match fails silently. Enum + validation would harden. |
| 10 | No `MLPrediction` retention / TTL | **LOW** | `sports/models.py:1750-ish` (per Sub-agent 1 report) | Predictions accumulate unbounded. At current write rate (~30-100/day from daily brief), 2-3 years to 100k rows — not immediately urgent but no explicit archival policy. |
| 11 | LLM analysis fallback returns plaintext, not structured | **LOW** | `sports_odds_analyst.py:674-676`, `game_predictor.py:341-343`, `sharp_action_detector.py:362-363` | On LLM error, returns string "LLM analysis unavailable" or exception message; downstream aggregation in `_build_executive_summary` handles gracefully but consumers expecting dict may `AttributeError`. SPECULATIVE — not verified end-to-end. |
| 12 | **F6 fold — Cross-book fixture-identity reconciliation absent** (upstream-dependency debt inherited from Cat A S1501 §2.1 non-guarantee) | **MED-HIGH architectural / LOW operational** | Cat B agents (all 4 filter sites) + `game_predictor.py:455-464` Game auto-create | Rigby SIGN cycle 1 Q5 fold: promote to explicit debt matrix item (previously only footnoted at §9 Q22 outbound). TheOdds `event_id` and Kalshi `ticker` live in different namespaces; `sports.models.Game.external_id` is one-per-row but has no cross-book mapping. GamePredictor's `Game.get_or_create(external_id=event_id, ...)` at line 455-464 creates duplicate `Game` rows if the same physical fixture is referenced by different vendor IDs. Silent mis-joins compound in Cat C wager tracking + Cat D content pipeline + Cat E frontend. **Architectural debt: MED-HIGH** (compounds into all downstream sports surfaces). **Operational debt: LOW** (no immediate runtime break; silent dedup miss only). Fix requires either `Game.external_id_map` JSONField OR a `FixtureIdentityResolver` service (extend posture). Island posture accepts inherited Cat A non-guarantee without filling. |

### 15.2 4-item pre-brief mini-schema per debt item (D62 fold)

| Debt # | (a) sports-only vs shared | (b) DBAO vs public | (c) integration posture (refactor vs extend) | (d) island posture (additional isolation) |
|---|---|---|---|---|
| 1 (asymmetry) | sports-only | public code path | **extend** — migrate 4 `.execute()` → `.run()` (bounded 4-line edit); integration posture requires uniform Layer 1 telemetry | **extend** — same migration is posture-neutral; island posture also benefits from uniform telemetry for isolated operational monitoring |
| 2 (PA registry) | sports-only | public dispatcher | **extend** — add 2 registrations (2 lines); posture-neutral | **extend** — same |
| 3 (ArbitrageOpportunity dormant) | sports-only | public sports app | **refactor** — either wire persistence OR delete triple; not posture-neutral | **refactor** — same choice; island posture may favor deletion (accept ephemeral-only design) |
| 4 (hardcoded LLM IDs) | Cat B-specific but symptom of shared factory contract | public code | **extend** — move to config; posture-neutral | **extend** — same |
| 5 (output-shape naming) | sports-only | public code | **refactor** — shared schema touches 4 agents + coordinator; integration posture may want structured emission (SignalCluster) which forces schema unification | **extend** — island posture can tolerate inconsistent names by documenting them; refactor optional |
| 6 (silent ImportError) | sports-only | Cat B agents crossing into sports app | **extend** — replace with explicit early-return + failure signal; posture-neutral | **extend** — same |
| 7 (no retry) | sports-only | Cat B agents | **extend** — add retry decorator on `TheOddsSpider().fetch_data()` calls; posture-neutral | **extend** — same |
| 8 (duplicated math) | sports-only | Cat B utilities | **extend** — shared utility module; posture-neutral | **extend** — same |
| 9 (`'soccer' in sport_key`) | sports-only | Cat B agent | **extend** — enum + validation; posture-neutral | **extend** — same |
| 10 (MLPrediction retention) | sports-only | sports app model | **extend** — add retention Celery task keyed on `created_at`; posture-neutral | **extend** — same; island posture may prefer stricter TTL to bound isolated storage |
| 11 (LLM fallback plaintext) | Cat B-specific | public code | **extend** — return structured fallback dict; posture-neutral | **extend** — same |

---

## 16. Boundary Violations

**Q24 — What services violate boundaries?**

### 16.1 No hard boundary violations observed

All Cat B code paths respect domain boundaries:

- Cat B does not directly call Discord API — routes through
  `DiscordNotificationService` (from Cat A boundary in the sole
  `arbitrage_bridge` path, not from Cat B agents themselves).
- Cat B does not execute raw SQL — uses Django ORM.
- Cat B does not import models from non-sports domains inappropriately
  (imports of `sports.models` from Cat B agents are within scope per
  §5.3 dependency chain).
- No circular imports observed at agent-service layer.

### 16.2 Scope-boundary observations (not violations, but §1 Finding 8)

Parent §3.B names 4 agents + `SportsBettingCoordinator`.
`SportsBettingCoordinator.generate_brief()` invokes 5 agents; the 5th
(`LineMovementAnalyzer` at line 158) is not in parent §3.B Cat B scope.
Additionally, `tool_dispatcher.py:302` registers
`prediction_market_analyst` as a sports PA tool — also not in parent
§3.B Cat B scope.

- **LineMovementAnalyzer** — Called by coordinator (line 158), does
  ORM-side `LegacySpiderData.objects.filter(...)` at
  `line_movement_analyzer.py:181` for historical odds comparison,
  writes Deliverable at line 115. Would fit Category A (data-source
  consumer) OR a new subdomain. Owed to xx99 reconciliation.
- **PredictionMarketAnalyst** — Registered as PA tool (line 302).
  Consumes Kalshi data (Cat A boundary per parent §3.A). Would fit
  Cat B (analytics consumer) OR a separate prediction-markets
  subdomain covering Kalshi differently from sports odds. Owed to
  xx99 reconciliation.

**Neither is a boundary violation** — both are within the sports/DBAO
super-domain, and both are analytics-consumer-side. But parent §3.B's
"4 agents" scope is narrower than the coordinator invocation surface
+ PA tool registration surface. xx99 (S1599) may need to either
expand the Cat B scope to 6 agents OR create a Cat B-adjacent
category for prediction markets + line movement.

---

## 17. Duplicate or Overlapping Systems

**Q23 — What models overlap with other domains?**

### 17.1 Model-level overlap

- **`Game` / `Team` / `League`** — Cat B auto-creates these via
  `GamePredictor.get_or_create()`; Cat C reads them via
  `PlacedWager.game` FK. Deliberate shared surface; not a duplicate-model
  defect.
- **`Deliverable`** — Shared multi-domain container.
- **`HumanAttentionItem`** — Shared multi-domain container.
- **`ArbitrageOpportunity`** — Not overlapping with another model; it
  is a **dormant model** unique to Cat B (§14.4). Different problem
  than overlap.

### 17.2 Analytical overlap

Sub-agent 6 flagged 3 pairwise overlaps:

- **`SportsOddsAnalyst` vs `SharpActionDetector`** — Both analyze
  professional betting patterns at different depth. SportsOddsAnalyst
  emits "value bet signals" at market granularity; SharpActionDetector
  emits "sharp vs soft divergence signals" at per-bookmaker
  granularity. **Complementary, not duplicate.** However, both use the
  `signals` output key (§14.6 debt #5) — consumer confusion possible.
- **`GamePredictor` vs `SportsOddsAnalyst`** — GamePredictor produces
  score predictions + confidence; SportsOddsAnalyst produces value-bet
  signals. **Complementary, not duplicate.**
- **`ArbitrageDetector` + `GamePredictor` implied-probability math** —
  Both parse American odds → decimal → implied probability. Code
  duplication (§15 debt #8) not model duplication.

### 17.3 Coordinator vs individual-agent invocation

`SportsBettingCoordinator.generate_brief()` invokes all 5 agents; REST
endpoint `/api/v1/betting/brief/` also invokes the coordinator. If a
consumer wants the same analysis without brief aggregation, they can
call individual REST endpoints (`/api/v1/betting/arbitrage/`,
`/api/v1/betting/sharp-action/`, etc.). No overlap — different
granularity, complementary surface.

---

## 18. Ownership Gaps

**Q25 — What ownership is unclear?**

### 18.1 Cat B ownership per Sub-agent 6 git-log inventory

| Surface | Author | Last modified | Ownership doc | AGENT_MAP registered | PA tool registered |
|---|---|---|---|---|---|
| `SportsOddsAnalyst` | clwest (Chris) | 2026-06-27 (S1246) | none | yes | **no** — §1 Finding 2 |
| `GamePredictor` | clwest | 2026-03-05 (S995B) | none | yes | yes |
| `SharpActionDetector` | clwest | 2026-02-15 | none | yes | yes |
| `ArbitrageDetector` | clwest | 2026-06-27 (S1246) | none | yes | **no** — §1 Finding 2 |
| `SportsBettingCoordinator` | clwest | 2026-06-22 (S1206) | none | N/A (service) | N/A (called by coordinator method) |

### 18.2 Explicit ownership gaps

1. **No `docs/topics/sports*.md`** — §11.1 flagged. Ownership doc
   equivalent to `docs/topics/stock-intelligence.md` does not exist.
   xx99 recommends creation post-S1504 or S1506.
2. **`SportsBettingCoordinator` not documented as first-class entry
   point in CLAUDE.md** — surfaces only in `docs/topics/agent-system.md:42`
   Intelligence Desks table. New readers must know to look at that
   table.
3. **`MLPrediction` consumer chain undocumented** — GamePredictor
   writes predictions; who reads them? `sports/views.py` viewset
   (SPECULATIVE), `MLPrediction.calculate_accuracy()` (retrospective
   metrics), `BettingOutcomeVerifier` (SPECULATIVE per Sub-agent 5
   inference). No documented read consumer chain.
4. **`SportsBettingBrief` model reference in Sub-agent 3 report
   UNKNOWN** — Sub-agent 3 mentioned brief persistence via
   "SportsBettingBrief" model + cache with 6h TTL. This audit did not
   verify the model's existence (§20.3). If it exists, ownership of
   brief storage is unclear; if it doesn't, brief is transient.
5. **PA tool registry gap = latent ownership ambiguity** —
   `sports_odds_analyst` and `arbitrage_detector` are in `AGENT_MAP`
   but not in PA registry (§1 Finding 2). Owner of the PA-vs-AGENT_MAP
   discovery contract is unclear.

---

## 19. Recommended Future Research

**Q28 — What should be researched next?**

### 19.1 Ranked follow-on queue (F1 fold — Rigby SIGN cycle 1 Q7 re-ranking)

Ranking by (architectural uncertainty × risk × unblocked flows) per
playbook §11.2 §19 rubric. **Rigby cycle 1 Q7 fold applied:** PA tool
registry gap promoted Rank 5 → Rank 4 per operational-ROI argument;
ArbitrageOpportunity persist-vs-remove kept at rank 5 (was 4).
SignalCluster posture decision kept top-2 per architectural-risk
argument.

| Rank | Item | Rationale | Blocks | Ownership |
|---|---|---|---|---|
| 1 | **`SignalCluster.pattern_type` sports-types posture decision** (F2-anchored) | HIGH architectural risk per Rigby cycle 1 verdict. This is the ontology / cross-domain integration gate. It determines whether sports becomes a first-class signal source or an explicit island. Load-bearing for xx99 posture-decision brief. | xx99 posture-decision brief; Cat F evidence plan; integration-posture-side of Chris-gated S1274 §12.3 decision. | Cat F evidence plan + xx99 anchor recommendation |
| 2 | **Coordinator `.run()` / `.execute()` asymmetry resolution + call-chain proof** | HIGH operational risk (§1 Finding 1). Not just "fix vs document" — the call graph and telemetry must be unambiguous and uniform. Bounded 4-line fix. High leverage: unblocks Layer 1 audit visibility for entire sports pipeline. | Cat F posture-decision brief cannot cleanly claim "Cat B has telemetry" or "not" until this is resolved. | Cat F (frames posture); post-arc ADR (implements) |
| 3 | **Downstream `MLPrediction` consumer inventory + outcome-feedback loop decision** | MED-HIGH architectural risk. Determines whether Cat B is "content generation only" OR an evaluable, improvable prediction system. Missing bridge is load-bearing for "sports as island" evidence. | Cat C completeness (S1503); Cat F posture surface. | S1503 (inventories outcome side); post-arc ADR (feedback-loop design if integration posture chosen) |
| 4 | **PA tool registry gap remediation** (`sports_odds_analyst` + `arbitrage_detector`) — F1 fold promoted from rank 5 | MED-HIGH operational risk. Bounded 2-line fix. Posture-neutral. Rigby SIGN cycle 1: "blocks invocation/inspection paths and creates 'exists in AGENT_MAP but not operable' drift". Unblocks surgical dispatch for 2 agents. | Rigby operational surface for Cat B debugging; PA-vs-AGENT_MAP discovery contract. | Post-arc ADR (trivial) |
| 5 | **`ArbitrageOpportunity` model dormant — persist or remove** (F1 fold demoted from rank 4) | MED-HIGH architectural risk. Full admin/serializer/viewset triple with no producer. Rigby SIGN cycle 1: kept as drift not posture-decision (F5 fold — persistence pattern valuable for audit trail + dedup + evaluation + UX). Requires design decision. | Cat E frontend consumer; Cat D content pipeline (SPECULATIVE brief consumers). | Cat F posture surface; post-arc ADR |
| 6 | **Memory Domain (S1300) bridge decision** | MED. Zero reads/writes today. Group 1300 already closed; if Cat F evidence surfaces need, delegates to Group 1300 follow-on per parent §6. | xx99 posture-decision brief. | Cat F evidence plan; delegated to S1300 follow-on if needed |
| 7 | **LineMovementAnalyzer + PredictionMarketAnalyst scope reconciliation** | MED. Parent §3.B scope narrower than coordinator + PA tool surface. xx99 reconciles: Cat B extends OR new subdomain. | xx99 canonical shape. | xx99 (S1599) |
| 8 | **Coordinator failure-mode semantics documentation** | MED. `_run_*` helpers return None on exception; brief ships with partial state; consumer contract undocumented. | Cat D content pipeline consumer contract; Cat E frontend rendering. | S1504 (Cat D consumer contract); post-arc doc |
| 9 | **`docs/topics/sports-prediction-analytics.md` narrative** | MED. Would consolidate Cat B findings + output schemas + integration surface into embedding-optimized topic doc. | Research coverage advancement LIGHT → DEEP → CANONICAL. | xx99 anchor recommendation; post-arc doc write |
| 10 | **Hardcoded LLM model ID migration + SportsOddsAnalyst factory alignment** | MED-LOW. 3-file change; move model IDs to config; migrate SportsOddsAnalyst from direct `get_openai_client()` to `LLMProviderRegistry`. | Cat G (LLM infra) hygiene; posture-neutral. | Post-arc ADR (trivial) |

---

## 20. Appendix

### 20.1 Files inspected (parent verifier-loop reads on load-bearing claims)

Beyond the 6 sub-agent file inventories (see §20.6), the parent agent
(Claude) directly verified the following on `main` HEAD `722ff313`:

- `core/services/sports_betting_coordinator.py:1-290` — full read (verified `.run()` vs `.execute()` asymmetry §1 Finding 1; docstring + orchestration + failure semantics).
- `core/celery.py:775-797` — full read of visible slice (verified beat schedule for `generate-daily-betting-brief` @ 07:00 MT, `queue: default`; `collect-sports-odds-intelligence` 30-min `long_running`; `collect-kalshi-prediction-markets` hourly at :15 `long_running`).
- `core/services/tool_dispatcher.py:302-305` — full read of registration block (verified 4 PA tools registered; `sports_odds_analyst` + `arbitrage_detector` NOT registered — §1 Finding 2).
- `core/models_signal_intelligence.py:75-92` — full read of `PATTERN_TYPE_CHOICES` (verified 10 non-sports pattern types; sports absent — §1 Finding 5).
- `core/tasks.py:6188-6190` + surrounding — verified `generate_daily_betting_brief` task wrapper delegates to `_impl_generate_daily_betting_brief` in `core.tasks_content`.
- `core/tasks.py:12170-12171` — verified `SportsBettingCoordinator().generate_brief()` invoked from `run_all_desks_intelligence` (Desk 2 Sports; per Session 1000 all-desks rotation).
- Line counts via `wc -l` on 5 Cat B files (verified §5.1 table): 730 / 560 / 366 / 676 / 290 = 2622 total.

### 20.2 Grep patterns and result counts (proofs of absence)

- `grep -rn "data_type.*==.*sports_odds|SpiderData\.objects\.filter|LegacySpiderData\.objects\.filter" core/agents/markets/` — 6 matches (4 in-memory filter sites, 1 LegacySpiderData ORM filter in scope-boundary LineMovementAnalyzer, 1 additional). Confirms §5.1 filter shape.
- `grep -rn "ArbitrageOpportunity\.objects\.(create|update_or_create|bulk_create)" core/agents/markets/` — **0 matches** (proves §1 Finding 4 §4.3 zero-persistence claim).
- `grep -rn "MLPrediction\.objects\.(create|update_or_create|bulk_create)|_save_to_deliverable\(" core/agents/markets/` — 7 matches: 1 `MLPrediction.objects.create()` in `game_predictor.py:505` (sole writer); 6 `_save_to_deliverable(` calls across all 6 markets agents (4 Cat B + 2 scope-boundary + `prediction_market_analyst`).
- `grep -rn "generate-daily-betting-brief\|generate_daily_betting_brief\|collect-sports-odds-intelligence\|collect_sports_odds_intelligence" core/celery.py` — 4 matches; confirms both beat entries + task-name registration.
- `grep -rn "class ArbitrageOpportunity\|class BettingOutcomeVerifier" **/*.py` — 5 matches: `ArbitrageOpportunity` at `sports/models.py:1292` + `sports/admin.py:454` + `sports/serializers.py:405` + `sports/views.py:835`; `BettingOutcomeVerifier` at `core/services/betting_outcome_verifier.py:21`.
- `grep -rn "register_tool\|register\(\s*\"(sports_odds_analyst|arbitrage_detector)\"" core/services/` — **0 matches** (proves §1 Finding 2 PA registry gap).
- `grep -rn "SignalCluster\.objects\.(create|update_or_create|bulk_create)" core/agents/markets/` — 0 matches (proves §9 Cat B → Signal Engine MISSING).
- `grep -rn "Initiative\.objects\.(create|update_or_create|bulk_create)" core/agents/markets/` — 0 matches (proves §9 Cat B → Initiative pipeline MISSING).
- `grep -rn "emit_event\|publish\|EventLog\|EventStream" core/agents/markets/ core/services/sports_betting_coordinator.py` — 0 matches (proves §10.1 zero-events emitted).
- `grep -rn "AgentMemory\|AgentKnowledgeSource" core/agents/markets/` — 0 matches (proves §9 Memory Domain MISSING).
- **F10 fold verification grep** — `grep -rn "class SportsBettingBrief\|SportsBettingBrief\.objects\." **/*.py` — 3 matches: model at `core/models_unified_system.py:18394` + write sites at `core/tasks.py:12187` (all-desks rotation) and `core/tasks_content.py:3150` (_impl_generate_daily_betting_brief). Resolves §20.3 SportsBettingBrief UNKNOWN — model exists, brief IS persisted.
- **F11 fold verification grep** — `grep -rn "detect_arbitrage\|scan_arbitrage_opportunities\|get_betting_brief\|get_sharp_action\|betting/(arbitrage\|brief\|sharp-action\|line-movement)" core/urls.py` — 11 matches: 6 view imports at lines 1348-1355 + 5 `path()` registrations at lines 3083 / 3104 / 3106 / 3112 / 3113 / 3127 / 3128 verifying REST endpoints for `/api/v1/betting/arbitrage/`, `/api/v1/betting/arbitrage/scan/`, `/api/v1/betting/line-movement/`, `/api/v1/betting/line-movement/<str:game_id>/`, `/api/v1/betting/brief/`, `/api/v1/betting/sharp-action/`, `/api/v1/odds/arbitrage/` (dual mount). Router registration verified.

### 20.3 Unresolved unknowns

- ~~Sub-agent 3 mentioned `SportsBettingBrief` model + cache with 6h TTL for brief persistence — this audit did not verify the model's existence.~~ **F10 FOLD RESOLVED 2026-07-02** — model exists at `core/models_unified_system.py:18394`; 2 write sites confirmed (`core/tasks.py:12187` + `core/tasks_content.py:3150`). See §4.6 for full inventory + §20.2 for grep evidence. Cache TTL claim (Sub-agent 3 mentioned 6h) not verified — deferred to Cat D audit S1504 consumer contract.
- Whether `_maybe_create_attention_item()` at `sports_odds_analyst.py:288` is called end-to-end — SPECULATIVE per Sub-agent 4; the stub exists but call site was not verified.
- Discord `/arb` command uses `.run()` per Sub-agent 3 — this generates one AgentExecution row per Discord dispatch. Not verified in parent verifier-loop.
- Whether `sports/views.py` viewset (line 835 for `ArbitrageOpportunityViewSet`) is actually referenced from any Cat E frontend page — Cat E scope (S1505). If unreferenced, viewset is fully dead code.
- Whether Kalshi prediction-market data ever reaches Cat B agents besides via `PredictionMarketAnalyst` (scope-boundary) — filter is on `data_type == 'sports_odds'`, so Kalshi rows with `data_type='prediction_market'` are excluded from the 4 Cat B agents' filter.
- Whether `SportsBettingCoordinator.generate_brief()` is invoked from anywhere BESIDES the daily beat + `/api/v1/betting/brief/` REST + `run_all_desks_intelligence` — Sub-agent 3 covered 3 sites; other invocation sites TBD.
- Whether the coordinator's asymmetric `.run()` / `.execute()` pattern was a Session 1206 pilot-in-progress (with plan to migrate all 5) or a intentional single-agent scoping — Rigby SIGN cycle should pressure-test.

### 20.4 Verifier-loop history

**Parent-Claude verifier-loop applied on 7 load-bearing claims prior to routing to Rigby Full SIGN.** All 7 claims survived independent verification via direct read + targeted grep; findings summarized below.

| Claim (source) | Verifier action | Verdict |
|---|---|---|
| Sub-agent 6 HIGH: coordinator `.run()` vs `.execute()` asymmetry (SportsOddsAnalyst uses `.run()`, other 4 use `.execute()`) | Read `sports_betting_coordinator.py:98-187` in full | **CONFIRMED** — line 122 explicit inline comment "Session 1206: `.run()` writes AgentExecution telemetry row (Layer 1 audit)". Lines 103 / 140 / 158 / 176 all `.execute()`. §1 Finding 1 stands. |
| Sub-agent 2 clarification: 4 direct-consume filters are in-memory on dict, not ORM query on SpiderData | Grep `data_type.*==.*sports_odds` + `SpiderData\.objects\.filter` across `core/agents/markets/` | **CONFIRMED** — 4 in-memory filter sites + 1 ORM read in scope-boundary LineMovementAnalyzer only. §1 Finding 3 stands; clarifies parent §3.B claim. |
| Sub-agent 1 finding: ArbitrageDetector does NOT persist to ArbitrageOpportunity model | Targeted grep `ArbitrageOpportunity\.objects\.(create|update_or_create|bulk_create)` across `core/agents/markets/` | **CONFIRMED — 0 matches.** §1 Finding 4 stands. |
| Sub-agent 1: MLPrediction sole writer is GamePredictor | Targeted grep `MLPrediction\.objects\.(create|update_or_create|bulk_create)` across `core/agents/markets/` | **CONFIRMED** — 1 match at `game_predictor.py:505`. |
| Sub-agent 3: beat schedule + queue for `generate-daily-betting-brief` and `collect-sports-odds-intelligence` | Read `core/celery.py:775-797` | **CONFIRMED** — `generate-daily-betting-brief` at 07:00 MT daily (`crontab(hour=7, minute=0)`), `queue: default`, `expires: 3600`; `collect-sports-odds-intelligence` every 30 min, `queue: long_running`, `expires: 1800`. |
| Sub-agent 3: PA tool registry (4 handlers) | Read `core/services/tool_dispatcher.py:302-305` | **CONFIRMED** — 4 `self.register(...)` lines for `prediction_market_analyst`, `game_predictor`, `line_movement_analyzer`, `sharp_action_detector`. `sports_odds_analyst` + `arbitrage_detector` NOT present. §1 Finding 2 stands. |
| Sub-agent 4: `SignalCluster.pattern_type` enum absence of sports types (S1274 §14 Finding #6 code-level materialization for Cat B) | Read `core/models_signal_intelligence.py:75-92` | **CONFIRMED** — 10 choices (demand_spike, trend_emergence, sentiment_shift, opportunity_window, knowledge_gap, competitive_signal, market_movement, skill_demand, content_gap, user_need); zero sports pattern types. §1 Finding 5 stands. |

**No sub-agent errors caught** in this pass (unlike S1501 §20.4 which
caught 3 sub-agent claim errors). Sub-agent reports were internally
consistent and matched independent verification.

**SIGN cycle 1 pending.** Rigby Full SIGN routing per playbook §15
Stage table (Full SIGN required for child audits). Fresh SIGN
isolation pin mint per §15 fresh-pin rule. D48 preemptive
stability-probe gate — 5th-arm continuation of the CODIFICATION-READY
S1405+S1406+S1499+S1501 4-arc pattern. Recommended cycle 1 prediction
per playbook §15 folding-edits rule: SIGN-with-edits at Medium-High
confidence anticipated; targeted at §1 Finding classification /
severity assignments (Rigby Q6 riskiest-finding + Q4
confuse-intentional-separation-with-missing-integration pressure) and
§13 maturity call ("PARTIAL armed but under-instrumented" vs
"WORKING" pressure per Q2 / Q3). Cycle 2 SIGN-clean at High confidence
expected after F1-Fx folds.

### 20.5 Verifier-loop history (SIGN fold notes)

**Rigby Full SIGN cycle 1** — 2026-07-02 on fresh isolation pin
`pa-64c019d7e6685d31` (minted via `python3 -c "import secrets; print(f'pa-{secrets.token_hex(8)}')"` on arc pin
`pa-791b3db549a64e54`; D48 preemptive stability-probe gate applied per
S1405+S1406+S1499+S1501 4-arc pattern → 5th arm this session —
stability probe returned "ready" on first turn via
`cockpit_tool.worker_health`, no worker-instability observed on any of
the 3 substantive SIGN batches; batches ran titles-only per Rigby SIGN
worker-instability recovery protocol).

**Cycle 1 verdict:** SIGN-with-edits at Medium confidence. Cycle 2
prediction (from Rigby): SIGN-clean at higher confidence after the
fold edits below land + must-change verification items closed
(SportsBettingBrief F10, router registration F11, continue-on-error
contract F8).

**Cycle 1 folds landed at commit-time (before cycle 2 SIGN):**

- **F1 (Rigby Q1 + Q9 fold — §7.1 explicit call-chain block).**
  Added explicit call-chain diagram at top of §7.1 (`Celery beat →
  core.tasks.generate_daily_betting_brief →
  core.tasks_content._impl_generate_daily_betting_brief →
  SportsBettingCoordinator.generate_brief() → 5 agent invocations with
  .execute()/.run() asymmetry marked → aggregate → return`) + failure-mode
  semantics summary + telemetry count table per single brief run.
  Also inserted §19 rank re-ordering per Rigby cycle 1 Q7 fold (PA
  registry gap promoted rank 5 → 4).
- **F2 (Rigby Q4 fold — §1 Finding 5 SignalCluster posture-decision
  reframe).** SignalCluster.pattern_type enum absence + Cat B write
  side absence reframed from "drift, HIGH" to "POSTURE-DECISION-PENDING"
  per S1274 §12.3 two-legitimate-postures precedent, mirroring S1501
  §2.1 posture-reframe pattern. Under integration posture: must add
  enum + write surface. Under island posture: explicit "sports do NOT
  emit SignalCluster rows" contract needed. Architectural risk HIGH
  preserved; operational risk marked LOW.
- **F3 (Rigby Q4 fold — §1 Finding 6 outcome-feedback-loop
  posture-decision reframe).** No Cat B → Cat C outcome-feedback loop
  reframed from "missing_connection MED-HIGH" to
  "POSTURE-DECISION-PENDING" per S1274 §12.3 precedent — "closed-loop
  learning deferred" is a legitimate posture for early-phase read-only
  inference. Architectural risk MED-HIGH preserved; operational risk
  marked LOW.
- **F4 (Rigby Q4 fold — §1 Finding 7 Memory Domain bridge
  posture-decision reframe).** No Memory Domain (S1300) bridge
  reframed from "missing_connection MED" to
  "POSTURE-DECISION-PENDING" — "context-agnostic by construction" is
  a legitimate posture (many sports pipelines are intentionally
  context-agnostic to avoid stale-prior contamination). Delegation
  flag to Group 1300 follow-on preserved if integration posture is
  chosen. Architectural risk MED preserved; operational risk marked
  LOW.
- **F5 (Rigby Q4 fold — §1 Finding 4 ArbitrageOpportunity kept as
  drift).** ArbitrageOpportunity model + admin + serializer + viewset
  triple with no producer explicitly **KEPT AS DRIFT, not reframed**
  per Rigby cycle 1 recommendation: "Even if arbs are ephemeral,
  persistence is still valuable as (a) audit trail, (b) dedupe /
  suppression, (c) evaluation, (d) downstream UX. The existence of
  model + admin + serializer + viewset reads like 'we meant to
  persist,' even if TTL-cleaned. If it were intentionally
  non-persistent, you'd expect either (a) no model, or (b) explicit
  TTL design/docs." No posture reframe applied.
- **F6 (Rigby Q5 fold — §15 fixture-identity reconciliation added as
  explicit debt item #12).** Cross-book fixture-identity reconciliation
  (TheOdds `event_id` vs Kalshi `ticker` vs `Game.external_id`)
  promoted from §9 Q22 footnote reference into explicit §15 debt
  matrix as debt #12 with MED-HIGH architectural risk / LOW operational
  risk classification. Per Rigby cycle 1: "This is one of the biggest
  sources of silent mis-joins, and it will keep showing up as
  'weirdness' in downstream features (settlement, evaluation,
  cross-market comparison). Put it in the matrix as 'Upstream
  dependency / cross-category debt'."
- **F7 (Rigby Q6 fold — §1 operational-vs-architectural risk axis
  added).** §1 Executive Summary preamble added distinguishing
  OPERATIONAL RISK (silent break in production) from ARCHITECTURAL
  RISK (compounds into future gaps). Per-finding risk labels applied
  to all 9 findings. Findings 1+2 lead on operational-risk; Findings
  3+5 lead on architectural-risk; Findings 4/6/7 are
  posture-decision-pending (risk contingent on Chris-gated posture
  choice). F7-based columns propagate to §14 drift, §15 debt, and §19
  future research queue.
- **F8 (Rigby Q8 fold — §1 Finding 9 continue-on-error reframe).**
  Coordinator "continue on error" failure semantics reframed from
  "drift vs docstring, MED" to
  "INTENTIONAL-OR-DRIFT NEEDING CONTRACT STATEMENT" per S1501 F6
  "unimplemented expectation" precedent. Either a documented
  best-effort-partial-brief resilience pattern OR a fail-fast omission
  that must be replaced with explicit failure surfacing. Choice is a
  Cat B contract-statement decision, not a bugfix. Operational risk
  MED preserved; architectural risk marked LOW.
- **F9 (Rigby Q8 fold — §1 Finding 1 + §13.2 Session-1205 language
  softened).** "Session-1205-DEAD-classification residue" language in
  §1 Finding 1 rationale softened per Rigby cycle 1 concern that
  framing was over-specific — S1205 may have been a broader
  scheduling-audit sweep, not specifically-named "DEAD sports agents".
  Language reworded to describe the observed asymmetry + Session 1206
  provenance comment without over-narrowing S1205 scope. §13.2
  rationale for PARTIAL verdict retains the S1205 anchor but as
  historical DEAD-classification context, not causal residue claim.
- **F10 (Rigby Q9 fold — SportsBettingBrief model verification).**
  Post-cycle-1 verifier-loop applied on Sub-agent 3's UNKNOWN claim.
  Grep confirmed model exists at `core/models_unified_system.py:18394`
  + 2 write sites at `core/tasks.py:12187` (all-desks Desk 2 Sports
  rotation) + `core/tasks_content.py:3150`
  (_impl_generate_daily_betting_brief). Added §4.6 SportsBettingBrief
  inventory subsection; renumbered downstream 4.7 / 4.8 (HumanAttention +
  mini-schema). Updated §20.3 to mark UNKNOWN as RESOLVED. Cache TTL
  claim from Sub-agent 3 (6h) not verified — deferred to Cat D audit
  S1504. Rigby cycle 1 Q9 concern about brief-transience posture
  discussion addressed: brief IS persisted, not transient — updates
  §7.1 Flow A step 13 and §7.1 telemetry summary table.
- **F11 (Rigby Q9 fold — REST endpoint router registration
  verification).** Post-cycle-1 verifier-loop applied on Rigby's
  "confirm router registration + reachability" ask. Grep of
  `core/urls.py` confirmed 6 `path()` registrations at lines 3083 /
  3104 / 3106 / 3112 / 3113 / 3127 / 3128 for `/api/v1/betting/*` and
  `/api/v1/odds/arbitrage/` dual-mount + 6 view-function imports at
  lines 1348-1355. Endpoints are router-wired, not orphan viewsets.
  Auth/permission gating not verified in this pass (SPECULATIVE —
  deferred to Cat E audit S1505). Added evidence line to §20.2 grep
  patterns.
- **F12 (Rigby Q8 fold — §5.1 direct-consume filter cite
  tightening).** Rigby cycle 1: direct-consume clarification "very
  likely right in practice" but should be backed by explicit
  cite/location. Added verbatim shape callout in §5.1 immediately
  after the 4-site table:
  `filtered_events = [e for e in events if e.get('data_type') == 'sports_odds']`
  with note that TheOddsSpider assigns the `data_type` key during
  `fetch_data()` normalization. Clarifies coupling is to spider dict
  return shape, not persisted enum.

**Cycle 2 SIGN** — Rigby Full SIGN cycle 2 SIGN-clean at High
confidence 2026-07-02. Cycle 1 prediction accurate. Rigby's cycle 2
verdict:

- Overall confidence: **High**
- Most accurate part (post-fold): the end-to-end operational chain
  (F1 fold — `beat → task → coordinator → agents → aggregate →
  SportsBettingBrief.objects.create()`) plus the now-clean separation
  of operational-risk vs architectural-risk (F7 fold) and the resolved
  UNKNOWN areas (F10 + F11).
- Weakest part remaining: any claims that still require runtime proof
  (permissions/accessibility of endpoints beyond router registration;
  whether ArbitrageOpportunity is intentionally unused vs partially
  used somewhere else beyond Cat B scope). These are nice-to-have
  verifications, NOT blockers.
- Residual folds: **NONE required.** SIGN-clean for folding into
  `ARCHITECTURE_INDEX §1.32`.
- Rigby cycle 2 confidence values per question: Q10 0.82 (all 12
  folds correctly applied per cycle 1 recommendations); Q11 0.74 (no
  new drift; two watch items for future arcs — ensure
  posture-decision reframes still state cost of deferral; router
  "reachable" wording should clarify "registered in router" vs
  "accessible to anon/auth roles"); Q12 0.72 (do-not-regress covers
  right surfaces if 5 items explicitly called out — F1 call chain +
  telemetry; PA registry + invocation symmetry; SportsBettingBrief
  persistence contract; endpoint wiring evidence; posture-decision
  gates — all 5 are in the do-not-regress notes above).
- **Cycle 2 final verdict:** **SIGN-clean.** Ready for commit +
  ARCHITECTURE_INDEX v28→v29 + OPEN_ARCS advancement + PR.

**Do-not-regress notes for PR + post-arc anchor updates:**

- Keep §2.1 Cat B contract statement intact — Rigby cycle-1 flagged
  "missing area: crisp Cat B contract statement" (her batch scanned
  titles only; §2.1 already provides the guarantees/does-NOT-guarantee
  structure mirroring S1501 §2.1). Do not delete or soften §2.1.
- Preserve posture-decision-pending framing throughout §1 Findings 5,
  6, 7 — do not backslide to "missing_connection" defect language.
- Preserve KEEP-AS-DRIFT classification on §1 Finding 4
  (ArbitrageOpportunity dormant triple) — Rigby cycle-1 explicitly
  recommended not reframing this to posture-decision.
- Preserve F1 explicit call-chain block in §7.1 — Rigby cycle-1
  flagged as must-change-before-canonical.
- Preserve F6 fixture-identity as explicit §15 debt item #12 —
  Rigby cycle-1 promoted to matrix.
- Preserve F7 operational-vs-architectural risk axis in §1 preamble
  and per-finding labels — this is the risk-framing basis for §14 /
  §15 / §19 downstream.

**D48 preemptive stability-probe gate — 5th arm CODIFICATION-READY
extension.** This SIGN cycle marks the 5th consecutive arc-close with
clean stability probe + zero worker-instability across multiple
substantive SIGN batches (S1405, S1406, S1499, S1501, S1502). Per
memory rule `feedback_rigby_sign_worker_instability_recovery.md`:
after S1502, D48 is CODIFICATION-READY for playbook v3 §15 addition
with 5-arc evidence base (was 4-arc after S1501). The pattern that
codifies: (a) mint fresh isolation pin via `python3 -c "import
secrets"`, (b) stability probe with ultra-short "confirm ready"
message, (c) if probe returns clean, proceed to titles-only batched
SIGN 2-3 findings per prompt, (d) if probe stalls or first
substantive turn stalls, retire pin + mint fresh + retry. xx99
(S1599) §10 meta-methodology section owns the eventual codification
recommendation to playbook v3.

### 20.6 Sub-agent provenance

Six parallel Explore sub-agents launched by parent Claude S1502-P2 at
2026-07-02. Each sub-agent operated on `main` HEAD `722ff313` under
scope `Category B only`. Sub-agent structured reports referenced but
not verbatim included (parent verifier-loop applied per §14).

- Sub-Agent 1 — Models & Persistence (owned MLPrediction sole-write + ArbitrageOpportunity zero-persistence findings).
- Sub-Agent 2 — Services & Runtime Flows (owned direct-consume filter shape clarification + coordinator flow trace + line-count god-service check).
- Sub-Agent 3 — APIs / Tools / Tasks / Commands (owned REST/WS inventory + beat schedule verification + PA tool registry gap identification + Discord /arb invocation).
- Sub-Agent 4 — Integrations & Cross-Domain Dependencies (owned Signal Engine + Initiative + Memory Domain + EventBus absence proofs + integration strength table).
- Sub-Agent 5 — Documentation & Prior Research (owned research coverage classification + SPORTS_MONETIZATION_ML.md coverage gaps for arbitrage_detector + sports_odds_analyst).
- Sub-Agent 6 — Drift / Debt / Ownership / Maturity (owned coordinator asymmetry HIGH finding + drift matrix + debt matrix + PARTIAL maturity verdict + Session 1205 DEAD-classification anchor).

### 20.7 Frontmatter provenance

Per playbook §6 frontmatter standard. See document header. Session-close
edits at commit time will bump `status: draft` → `status: active` and
update `verifier_loop` with Rigby SIGN cycle outcomes per playbook
§17 Graduation Criteria.

---
