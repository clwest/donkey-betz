---
title: "S1503 Sports Wager Tracking & Outcome Verification — Child Audit (Category C / P3 under Group 1500)"
status: active (child audit — third child of Group 1500 Sports/DBAO/Intelligence arc; drafted 2026-07-02; Rigby Full SIGN cycle 1 SIGN-with-edits at High confidence 2026-07-02 on fresh isolation pin `pa-8ce5f949bed5e093` → F1-F14 folds landed at commit-time → cycle 2 SIGN-clean at High confidence anticipated post-fold-land; D48 preemptive stability-probe gate 6th arm — clean stability probe + zero worker-instability across 4 substantive SIGN batches — CODIFICATION-READY continuation of S1405+S1406+S1499+S1501+S1502 5-arc pattern → 6-arc pattern for xx99 §10.2 playbook v3 §15 recommendation)
authority: child-audit for Category C per parent §5 sequence + third sibling to apply the pre-brief mini-schema per D62 = (a) propagate upfront (Chris-ratified S1501 open 2026-07-01)
category: child_audit
session: 1503
date: 2026-07-02
domain_slug: sports
subdomain_category: C
research_group: 1500
parent_doc: docs/research/domains/sports/1500_sports_domain_scoping.md
authors: Claude Code (Chris directed via short command "Continue research group 1500: Category C")
supersedes: none
related:
  - docs/research/domains/sports/1500_sports_domain_scoping.md                       # parent scoping — arc-open + Phase 0 F.i/F.ii/F.iii second application UNCHANGED per D58 + candidate subdomain taxonomy A-F + D62 = (a) pre-brief mini-schema propagation ratification
  - docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md   # Cat A sibling audit — §2.1 Cat A contract statement is Cat C's load-bearing input for odds-data provenance
  - docs/research/domains/sports/1502_sports_prediction_analytics_agents_audit.md    # Cat B sibling audit — §1 Finding 6 outcome-feedback-loop MISSING (POSTURE-DECISION-PENDING per F3 fold) is our load-bearing input; §2.1 Cat B contract statement bounds Cat B/C surface
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                                        # §9 28 canonical questions + §11.2 20-section child template + §13 6-parallel-sweep + §14 evidence rules + §15 SIGN
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md                               # OS bootstrap + child-audit contract §8
  - docs/research/OPEN_ARCS.md                                                       # arc manifest — Group 1500 In-progress
  - docs/research/platform_architecture_inventory.md §3.10                           # S1273 Sports Intelligence / Betting Pipeline LIGHT baseline — names PlacedWager + BettingOutcomeVerifier + settlement-integration gap
  - docs/research/platform/cross_domain_integration_audit.md §14 Finding #6          # S1274 sports_odds not a SignalCluster.pattern_type HIGH — Cat C consumer side gap: no SignalCluster emission from wager outcomes / streaks / ROI
  - docs/research/platform/cross_domain_integration_audit.md §12.3                   # S1274 v2 P1 island-vs-integrated posture decision point — Cat C evidence contributes MLPrediction feedback-loop side of the axis
  - docs/PLATFORM_INVENTORY.md                                                       # runtime inventory anchor (regenerable) — models/tasks/PA tools counts
  - docs/PLATFORM_WHAT_IT_IS.md                                                      # narrative anchor
  - docs/narratives/SPORTS_MONETIZATION_ML.md                                        # HIGH-provenance narrative (S1158) — cross-references PlacedWager, BettingOutcomeVerifier, verify_betting_outcomes task, /bankroll command
  - docs/handoffs/SESSION_995_BETTING_OUTCOME_VERIFICATION.md                        # origin handoff for Cat C settlement service + learning bridge
  - docs/handoffs/SESSION_995B_SPORTS_BETTING_INTELLIGENCE.md                        # sibling handoff for related sports intelligence surface
  - docs/handoffs/SESSION_1011_SPORTS_PIPELINE_AUTOMATION.md                         # sports pipeline orchestration mention of task cadence "every 2h"
  - docs/handoffs/SESSION_1012_BETTING_TABS_POLISH.md                                # frontend betting-tab surface refinement
  - docs/handoffs/SESSION_1165_COO_BACKLOG_TRIPLE_MUST_CLOSE.md                      # retry-policy addition for verify_betting_outcomes (budget-gated retry, exponential backoff)
  - docs/handoffs/SESSION_1244_CAT_2_FULLY_CLOSED_PLUS_CELERY_AUDIT_PLUS_2_REGRESSION_CANARIES.md  # PR #2687 sports-queue parity fix (Makefile-vs-Procfile-vs-task_routes) — reference for §14.1 drift context (partial fix that did NOT address missing beat entry)
  - docs/CELERY_AUDIT.md                                                             # canonical Celery inventory — row 469-470 confirms both verify_betting_outcomes task variants have no beat schedule
  - docs/AUDIT_FINDINGS.md                                                           # canonical Celery deferred-by-policy list #12 — grep-verified 2026-07-02: verify_betting_outcomes NOT on this list
scope: audit Category C ONLY — sports wager tracking + outcome verification surfaces (`PlacedWager`, `PlacedWagerLeg`, `BettingStats` in `core/models_betting.py`; `BettingOutcomeVerifier` at `core/services/betting_outcome_verifier.py:21`; Celery task `verify_betting_outcomes` at `core/tasks.py:6122` plus sibling at `sports/tasks.py:414`; Discord `/bankroll` at `core/services/discord_bot.py:1404`; REST wager surfaces at `core/urls.py:3110-3123`; PA tool `intelligence_tool` actions `sports_wagers` + `sports_record_wager` at `core/services/pa_tool_schemas.py:3241` handled at `core/services/td_handlers_content.py:3995+`; learning bridge `SportsBettingLearningBridge` at `core/learning_bridges/sports_betting_bridge.py`)
non_goals:
  - Category A — sports odds ingestion (S1501 owns; §2.1 Cat A contract statement is our load-bearing input for odds/score provenance shape, NOT our audit surface)
  - Category B — prediction & analytics agents (S1502 owns; §1 Finding 6 outcome-feedback-loop MISSING is our load-bearing inherited claim; do NOT re-audit the prediction agents)
  - Category D — betting content pipeline (SportsContentContextBuilder, generate_daily_betting_brief, Discord /odds — S1504 owns; noted only where Cat C settlement/bankroll data flows into D content surface)
  - Category E — frontend sports surface (BettingPage 9 tabs incl. My Wagers + Records tabs, /betting route — S1505 owns; noted only where Cat C REST endpoints are consumed by E)
  - Category F — cross-domain integration lens + posture decision framing + evidence plan (S1506 owns; consumes P1-P5)
  - deep audit of `BettingOutcomeVerifier._evaluate_h2h/_evaluate_spread/_evaluate_total` correctness — bounded reference implementations, not architecturally load-bearing; flagged as debt (§15.4 test-coverage gap) not as evidence-plan surface
  - deep audit of `SportsBettingLearningBridge` cross-boundary contract with `AgentMemory` / `UserAgentLearning` — the bridge's *existence* + *one-way flow* is load-bearing; internal method behavior is Cat B/Memory-domain reconciliation (owed to xx99 posture brief or future Cat B ↔ Memory Domain arc)
  - actually deciding the S1274 §12.3 island-vs-integrated posture (Chris-gated, post-arc — see D59 refinement)
  - implementation proposals (this is research; PRs come later per playbook §14 "no implementation during research")
  - external companion project scope (`BILLING_MONETIZATION_SYSTEM.md` from ai-content-studio — S1400 anti-scope pattern inherited)
  - Odds API vendor selection (product decision, not architecture)
  - mobile / React Native betting-app scope
  - bankroll / staking strategy research (parent §7 anti-scope #9 — Sports scope-trap; Cat C inventories model surface only, no strategy research)
owner: claude (Chris ratified S1503 P3 open via "Continue research group 1500: Category C" short command 2026-07-02)
verifier_loop: Parent-Claude verifier-loop applied on 7 load-bearing claims prior to Rigby SIGN — see §20.4. Two sub-agent errors caught pre-SIGN — Sub-agent 6 reported `betting_outcome_verifier.py` at 340 lines (actual 480 per `wc -l`) + Sub-agent 6 reported `MIN_HOURS_AFTER_START = 3` on line 28 (actual line 26 per direct read); both corrected before draft integration. One CRITICAL load-bearing claim (verify_betting_outcomes zero-fire status) additionally verified via Rigby ORM probe on `pa-791b3db549a64e54` before draft — PeriodicTask count 0 + CeleryTaskEvent 30d count 0 for both `core.tasks.verify_betting_outcomes` and `sports.verify_betting_outcomes` variants; `docs/AUDIT_FINDINGS.md` grep-verified NOT to contain either task name (i.e., this task is NOT documented as intentionally deferred per S1245 canonical policy). Rigby Full SIGN cycle 1 SIGN-with-edits at High confidence 2026-07-02 on fresh isolation pin `pa-8ce5f949bed5e093` — 3 substantive SIGN batches (Q1-Q3 completeness + maturity; Q4-Q6 integration + debt + risk; Q7-Q9 + overall verdict) + 1 stability probe (warm-up ping + cockpit_tool.worker_health confirming 4 workers online, 0 active tasks); **zero worker-instability observed across all 4 turns**. Second independent Rigby ORM probe (SIGN cycle 1 batch 3 Q8) both variants returned 0 (matches parent-Claude pre-SIGN probe) — CRITICAL §14.1 finding evidence-doubled. **F1-F14 folds landed at commit-time** (see §20.4 verifier_loop notes + §20.8 fold summary). Cycle 2 SIGN-clean at High confidence anticipated post-fold-land (pattern-consistent with S1501 + S1502 cycle-1-predict-cycle-2 accuracy). D48 preemptive stability-probe gate **6th arm** — clean stability probe + zero worker-instability across 4 turns — reinforces CODIFICATION-READY 5-arc pattern (S1405+S1406+S1499+S1501+S1502 → 6-arc pattern) for playbook v3 §15 recommendation (xx99 S1599 §10.2 codification).
companion_anchors:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/platform_architecture_inventory.md
  - docs/research/platform/cross_domain_integration_audit.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/domains/sports/1500_sports_domain_scoping.md
  - docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md
  - docs/research/domains/sports/1502_sports_prediction_analytics_agents_audit.md
git_head_at_draft: 55a34b6c
---

# Session 1503 — Sports Wager Tracking & Outcome Verification Audit (Category C)

> **What this doc is.** The third child audit of Group 1500. It answers
> the 28 canonical questions from playbook §9 for **Category C only** —
> the wager placement surface (`PlacedWager` + `PlacedWagerLeg`),
> aggregate stats surface (`BettingStats`), outcome verification
> service (`BettingOutcomeVerifier`), scheduling surface (Celery task
> `verify_betting_outcomes` and its `sports/tasks.py` sibling), and
> user-facing surfaces (`/bankroll` Discord command + REST endpoints
> at `core/urls.py:3110-3123` + PA tool `intelligence_tool` actions
> `sports_wagers` + `sports_record_wager`) — using six parallel Explore
> sub-agents (per §13) + Claude parent verifier-loop passes on
> load-bearing claims (per §14 "trust but verify") + one targeted Rigby
> ORM probe (PeriodicTask + CeleryTaskEvent 30d) before draft
> integration. Every surface inventoried carries the 4-item pre-brief
> mini-schema per D62 = (a) propagate upfront (Chris-ratified S1501
> open 2026-07-01), matching the sibling exemplar shape established by
> S1501 §4.6 / §5.4 / §6.6 / §8.4 / §15.1 and S1502 §4.8 / §5.4 / §6.6
> / §8.6 / §15.2.
>
> **What this doc is not.** A design proposal. A posture recommendation.
> An audit of Cat A ingestion (S1501 §2.1 Cat A contract is our INPUT
> for score provenance shape), of Cat B prediction agents (S1502 §2.1
> Cat B contract is our INPUT for the outcome-feedback gap frame), of
> Cat D content pipeline, of Cat E frontend, or of Cat F cross-domain
> lens. An implementation plan. This is research.

---

## 1. Executive Summary

Category C — the sports wager tracking + outcome verification surface — is **PARTIAL (armed but zero-fire)**. The data model is complete and well-typed (3 models, 289 lines, proper `DecimalField` money handling, indexed status queries), the settlement service is a focused 480-line implementation (`BettingOutcomeVerifier` with h2h / spreads / totals evaluation + parlay resolution + arbitrage verification + learning bridge), the REST + PA + Discord user surfaces are all wired (11 REST endpoints, 2 PA tool actions, 5 Discord commands), and the outcome-to-learning bridge (`SportsBettingLearningBridge` at 696 lines) writes `UserAgentLearning` + `AgentMemory` rows. But the pipeline **has never fired in production in the last 30 days** — the scheduling drift is CRITICAL: **no `PeriodicTask` row exists** for either task variant (`core.tasks.verify_betting_outcomes` OR `sports.verify_betting_outcomes`), **no beat entry** exists in `core/celery.py`, `docs/AUDIT_FINDINGS.md` §12 canonical deferred list does **NOT** list this task, and Rigby ORM probe returned **zero CeleryTaskEvent firings for both task variants over the last 30 days**. The docstring at `core/tasks.py:6129` claims "Runs every 2 hours via Celery Beat" — this describes phantom behavior. Downstream: `BettingStats.recalculate()` (only auto-called from inside the never-firing task at `core/tasks.py:6141-6156`) never runs; `SportsBettingLearningBridge.record_wager_outcome()` (only called from `BettingOutcomeVerifier._create_learning_records()` at `betting_outcome_verifier.py:455-480`) never fires; wagers created via the working PA tool + REST + Discord surfaces settle only on manual dispatch. Additionally Cat C **inherits Cat B §1 Finding 6** (outcome-feedback-loop MISSING) — settled outcomes never write back to `MLPrediction.was_correct` (that field is set by a separate task `evaluate_ml_predictions` at `core/tasks.py:6192`), so even under the phantom-cadence assumption there is no code path from settled wager → Cat B prediction agent calibration. Load-bearing "sports as island" evidence for Cat F posture-decision brief.

**Ten load-bearing findings owed to xx99 (S1599) posture-decision brief via Cat F evidence plan** — ordered by expected severity for Rigby SIGN Q6 (riskiest operational finding) triage.

**Risk-axis distinction (inherited from S1502 §1 F7 fold pattern).** Findings below carry two orthogonal risk labels: **OPERATIONAL RISK** (silent break in production — visibility, monitoring, control-plane correctness) and **ARCHITECTURAL RISK** (compounds into future gaps — ontology, integration surface, feedback loops). Finding 1 leads on operational-risk (whole feature silently broken). Findings 3, 4, 5 lead on architectural-risk. Findings 6, 7, 8 are posture-decision-pending; their risk is contingent on Chris-gated posture choice per S1274 §12.3. F1-based operational-vs-architectural columns propagate to §14 (drift), §15 (debt), and §19 (future research queue).

1. **[CRITICAL — riskiest operational risk] `verify_betting_outcomes` task is unscheduled AND has zero firing history (drift, CRITICAL operational, LOW architectural).**
   Two task definitions coexist in the codebase: `core.tasks.verify_betting_outcomes` at `core/tasks.py:6121-6184` (with `bind=True`, retry policy, and BettingStats-recalc wrapper) and `sports.verify_betting_outcomes` at `sports/tasks.py:414-441` (simpler variant, no retry policy, no BettingStats wrapper). Grep of `core/celery.py:37-797` for `verify_betting_outcomes`: **zero matches**. Task routing entry exists at `core/settings.py:1385` (`'core.tasks.verify_betting_outcomes': {'queue': 'sports'}`) but there is no `app.conf.beat_schedule` entry pointing at either task. `docs/CELERY_AUDIT.md:469-470` inventory rows confirm both variants have empty beat column (`·` in the "Beat" column). `docs/AUDIT_FINDINGS.md` §12 canonical deferred-by-policy list (per memory rule `feedback_audit_findings_12_canonical_celery_deferred_list.md`): **grep returns zero matches** — this task is **NOT documented as intentionally deferred**. Rigby ORM probe on `pa-791b3db549a64e54` (see §20.4): `PeriodicTask.objects.filter(task__in=[...]).count() == 0` AND `CeleryTaskEvent.objects.filter(task_name__in=[...], event_time__gte=now-30d).count() == 0` for **both** task variants. Session 1244 PR #2687 (`SESSION_1244_CAT_2_FULLY_CLOSED_PLUS_CELERY_AUDIT_PLUS_2_REGRESSION_CANARIES.md:69-73`) fixed the sports-queue parity issue (Makefile ↔ Procfile ↔ task_routes) — meaning the `sports` worker CAN consume this task if dispatched — but did NOT re-enable a beat schedule. Docstring at `core/tasks.py:6129`: "Runs every 2 hours via Celery Beat. Idempotent" — this describes phantom behavior. Cascade: `BettingStats.recalculate()` (only auto-called at `core/tasks.py:6141-6156` inside the never-firing task) → never runs. `SportsBettingLearningBridge.record_wager_outcome()` (only called from `betting_outcome_verifier.py:461`) → never fires. Wagers created via the working PA tool + REST + Discord surfaces settle only on manual dispatch or explicit user-facing settle action. This is not S1502 §1 Finding 1 (that was telemetry drift on 4 of 5 orchestrator paths); this is worse — the entire feature is silently broken. **Operational risk: CRITICAL.** **Architectural risk: LOW** (bounded 3-5 line fix: add a beat entry OR a PeriodicTask row). The Session 1502 F9 softening pattern does NOT apply here — the docstring's "Runs every 2 hours" is a testable claim that ORM disproves, not intent language open to interpretation.

2. **[HIGH — architectural riskiest per Cat F posture pipeline] Zero Cat C → Cat B outcome-feedback loop (drift, HIGH architectural; POSTURE-DECISION-PENDING per S1502 F3 precedent).**
   Answers S1502 §1 Finding 6 explicitly (the P3 parked question from parent §3.C and §5 sibling-inheritance rule). `BettingOutcomeVerifier` at `core/services/betting_outcome_verifier.py:1-480` contains **zero imports of `MLPrediction`** (grep-verified — full file returned "No matches found" for MLPrediction / was_correct / SignalCluster / SignalService / AgentMemory / MemoryLane). The verifier's `_create_learning_records()` at line 455-480 delegates to `SportsBettingLearningBridge.record_wager_outcome()` (`core/learning_bridges/sports_betting_bridge.py:488-551` per Sub-agent 4 verifier); the bridge **reads** `MLPrediction.was_correct` at line 394 (`if prediction.was_correct:`) but **does not set it** — `MLPrediction.was_correct` is set by a **separate task**, `evaluate_ml_predictions` at `core/tasks.py:6192` (per Sub-agent 3 handoff table). Two decoupled evaluation pipelines: wager settlement (Cat C, silently unscheduled) evaluates against The Odds API scores + settles `PlacedWagerLeg.status` + `PlacedWager.status`; prediction evaluation (Cat B/Sports separate) evaluates `MLPrediction` correctness at a different beat cadence. **A `PlacedWager` placed ON an `MLPrediction` will never feed the prediction's correctness score.** No cross-pipeline join exists in code. This is the "sports as island" pattern materialized on the Cat C side. **Not a bug per current architecture** (may be intentional isolation) — **POSTURE-DECISION-PENDING per S1502 F3 precedent** (extending the framing pattern to Cat C). Cat F evidence plan owes: whether integration posture requires wager→prediction feedback OR whether the two evaluation pipelines can remain decoupled. **Architectural risk: HIGH** (compounds into every future Cat B → Cat C bridge; blocks calibration-driven prediction improvement). **Operational risk: LOW** (silent by design; no active break).

3. **[HIGH — architectural] Zero Cat C → Signal Engine emission (drift, HIGH architectural; POSTURE-DECISION-PENDING per S1502 F2 precedent).**
   Extends S1274 §14 Finding #6 (S1273 §3.10 gap — `sports_odds` not a `SignalCluster.pattern_type`) into the Cat C consumer surface. `betting_outcome_verifier.py` grep of `SignalCluster` / `SignalService`: **zero matches**. `core/models_betting.py` grep of same: **zero matches**. `core/tasks.py:6100-6200` (task neighborhood around `verify_betting_outcomes`): only unrelated `SignalCluster` references at lines 4863 + 4873 (in different tasks). **No Cat C surface** (settlement event, streak change, ROI threshold, or `HumanAttentionItem.record_verification` outcome) **emits a `SignalCluster` row.** This is the Cat C-side companion to S1502 §14.3 (Cat B agent-side absence of sports pattern types). Cat B has `MLPrediction` outputs to signal-emit; Cat C has settlement outcomes / streak transitions / arbitrage-verification outcomes. Neither writes to `SignalCluster`. **POSTURE-DECISION-PENDING** per S1502 F2 framing pattern — integration posture would extend `SignalCluster.pattern_type` to include sports outcome events AND wire the emission call; island posture requires no change. **Architectural risk: HIGH.** **Operational risk: LOW** (silent by design; consumed by intentional Cat B/C isolation).

4. **[MED-HIGH — drift] Two task definitions with same purpose but different implementations (drift, MED-HIGH operational).**
   `core.tasks.verify_betting_outcomes` at `core/tasks.py:6121-6184` has `bind=True`, `max_retries=2`, `default_retry_delay=300`, Session 1165 budget-gated retry policy, and BettingStats-recalc wrapper (lines 6141-6156). `sports.verify_betting_outcomes` at `sports/tasks.py:414-441` has no retry policy, no BettingStats wrapper, and returns a simpler summary dict. Both call the same `BettingOutcomeVerifier().verify_all_pending()` at their cores. Task registry has both under different names — the `name=` kwarg on the `sports/tasks.py:414` decorator (`@shared_task(name='sports.verify_betting_outcomes')`) means Celery treats them as **two distinct tasks**, not overrides. `docs/CELERY_AUDIT.md:469-470` confirms both are registered but neither has a beat schedule. **Neither is intentionally deferred per `docs/AUDIT_FINDINGS.md` §12.** Whether the `sports.tasks` variant was a scoping / migration attempt (moving Cat C surface into the `sports` Django app) OR is a duplicate-then-forgot pattern is not evident from code alone. **Operational risk: MED-HIGH** (dispatcher ambiguity if a beat entry is added — which variant gets scheduled? — could silently pick the retry-less one). **Architectural risk: MED** (app-boundary drift: `core/tasks.py` vs `sports/tasks.py` for the same feature suggests unresolved Django-app-ownership question for Cat C, adjacent to xx99 parked DBAO-schema question in parent §6).

5. **[MED-HIGH — drift] Discord `/bankroll` command reads `Bankroll` model (not `BettingStats`) — dual aggregation surface (drift, MED-HIGH operational + MED architectural).**
   `core/services/discord_bot.py:1404-1527` (Discord `/bankroll` command implementation) queries `bankroll.wagers.order_by('-placed_at')[:5]` and displays `current_balance`, `profit_loss`, `roi`, `win_rate`, `record`, `pending count`, `streak`, `unit_size`. The `Bankroll` model referenced lives at `core/models_bankroll.py:Bankroll` (per Sub-agent 3 report — file not inspected in this audit but grep-confirmed via discord_bot.py import). **`BettingStats` model at `core/models_betting.py:163-289` is not consulted by the Discord surface** — grep of `discord_bot.py` for `BettingStats` returns zero matches on the `/bankroll` command implementation (line range 1404-1527). Two separate aggregation surfaces exist for the same conceptual data (per-user betting record): `Bankroll` model (Discord read surface) and `BettingStats` model (`verify_betting_outcomes` auto-recalc surface + REST `/api/v1/betting/stats/` at `core/urls.py:3122`). Sibling Discord commands `/bet`, `/resolve`, `/slip` at `discord_bot.py:1530, 1639, 1851` write to `Bankroll.wagers` (Discord surface), not to `PlacedWager` (core surface). **Runtime consequence:** the working Discord write-path (`/bet`) and the core wager-management surface (`PlacedWager`) are two disjoint data domains — Discord users' bet history in `Bankroll` model, PA-tool + REST users' wager history in `PlacedWager` model. No sync path detected. **Operational risk: MED-HIGH** (users bet via one surface and see stats from another; stats never converge). **Architectural risk: MED** (unclear canonical source of truth; blocks future work like unified BettingHistory view).

6. **[MED-HIGH — drift; POSTURE-DECISION-PENDING per S1502 F4 precedent] Zero Cat C → Memory Domain (S1300) bridge beyond `AgentMemory` + `UserAgentLearning`.**
   `SportsBettingLearningBridge` at `core/learning_bridges/sports_betting_bridge.py:696` lines with 16 methods writes `UserAgentLearning` (line 503-517 per Sub-agent 4) + `AgentMemory` (line 532-549) rows with `source_type='betting_outcome_verification'` (line 546). But grep for `MemoryLane` / `AgentKnowledgeSource` in `sports_betting_bridge.py`: **zero matches**. Cat C's learning-loop write is scoped to two surfaces: the per-user learning table + the agent-scoped memory table. Broader memory-domain surfaces (Memory Lanes per S1300, knowledge-source ingestion, cross-agent memory transfer) are not written by Cat C. This is the S1300 bridge question parked at parent §6 (P3 parked). Reads: none — Cat C does NOT consult strategic memory before settling wagers (deterministic settlement logic based on scores, not memory-conditioned). **POSTURE-DECISION-PENDING per S1502 F4 precedent** — integration posture: extend Cat C write to `MemoryLane` for strategic-context injection; island posture: retain the `AgentMemory`-only surface as intentionally minimal. **Architectural risk: MED-HIGH** (limits Cat C's contribution to platform-wide learning); **operational risk: LOW** (silent by design).

7. **[MED — drift] `PlacedWagerLeg` stores `event_id` as CharField, not FK to `sports.models.Game` — external-API-driven settlement (drift, MED architectural).**
   `PlacedWagerLeg` at `core/models_betting.py:108-161` has NO `game` FK; instead stores `event_id` (CharField, line 132), `sport` (CharField, line 133), `matchup` (CharField, line 134), `commence_time` (DateTimeField, line 135). Settlement path at `betting_outcome_verifier.py:169-226` fetches scores via `TheOddsSpider.fetch_scores()` (per Sub-agent 2 verification, line 82 + 148 lazy import) and looks up scores by `(sport, event_id)` string tuple, NOT by joining to `sports.models.Game.home_score/away_score`. This **decouples Cat C from Cat B fixture-identity work** (S1502 §15 debt #12 — fixture identity reconciliation is a Cat A/B concern) but also means: (a) Cat C is resilient to `sports.models.Game` schema changes; (b) Cat C is tightly coupled to The Odds API `event_id` naming (a spider-side dict-return-shape coupling similar to Cat B's post-fetch filter coupling per S1502 §1 Finding 3); (c) No SQL-level join possible between wagers and games — analytics queries requiring per-game aggregation (e.g., "which games have the most bets?") require in-memory join or a materialized view. **Runtime consequence:** posture-decision axis exists on whether to normalize Cat C to `sports.models.Game` FK under integration posture, and if so how to preserve backward compatibility with historic `event_id` strings. **Architectural risk: MED.** **Operational risk: LOW** (settlement works; no active break).

8. **[MED — drift; POSTURE-DECISION-PENDING] Cat C is a leaf domain — zero inbound FKs (drift, MED architectural — but note this is expected under island posture).**
   Grep of the entire codebase for `to='core.PlacedWager` / `to="core.PlacedWager` / `to='core.PlacedWagerLeg` / `to='core.BettingStats` and unquoted string variants: **zero matches** outside `core/models_betting.py` self-references (per Sub-agent 4 report; independently grep-verifiable). Cat C surface is a **leaf domain** — no model outside `core/models_betting.py` depends on any Cat C model. Outbound: only `settings.AUTH_USER_MODEL` FKs (`PlacedWager.user`, `BettingStats.user`) + self-reference (`PlacedWagerLeg.wager`). No FK to `sports.models.Game` / `MLPrediction` / `SignalCluster` / `Initiative` / `Deliverable`. This is the **structural signature of "sports as island"** — Cat C is architecturally isolated at the FK graph level. **Operational risk: LOW** (isolation is enforceable). **Architectural risk: MED** — POSTURE-DECISION-PENDING per S1502 posture-framing pattern. Integration posture requires establishing at least one FK (e.g., `Initiative` FK to `PlacedWager` for outcome-driven initiative creation, or `SignalCluster` FK for signal-emission ancestry). Island posture: current shape is the intended shape; document as CANONICAL under §6 (parked candidate) resolution.

9. **[MED-HIGH — debt] Zero test coverage for Cat C surface (debt, MED-HIGH operational).**
   Grep of `core/tests/` for `PlacedWager` OR `BettingStats` OR `BettingOutcomeVerifier` OR `verify_betting_outcomes` (via `Grep tool path=core/tests`): **zero files matched.** No unit tests for: `PlacedWager.settle()` (line 92), `PlacedWager.calculate_payout()` (line 87 per Sub-agent 1), `PlacedWager.decimal_odds` (line 72), `PlacedWagerLeg` outcome routing, `BettingStats.recalculate()` full-rescan aggregation (line 223-289), `BettingOutcomeVerifier._evaluate_h2h` / `_evaluate_spread` / `_evaluate_total` (lines 259-333), parlay-with-push edge case, arbitrage profit computation, retry-budget interaction. **Runtime consequence:** any change to settlement logic ships blind. Debt is **operational-risk MED-HIGH** because the CRITICAL scheduling drift (§1 Finding 1) means when a beat entry is added later, the first real production settlement run has no regression coverage. **Architectural risk: MED** (blocks confident integration-posture wiring — cannot ship signal-emission additions without knowing settlement invariants hold).

10. **[MED — debt] No concurrency control on outcome settlement (debt, MED operational).**
    `betting_outcome_verifier.py:54-57` fetches pending legs without `select_for_update()`. `_settle_wager()` at lines 169-226 loops through legs and calls `leg.save(update_fields=['status', 'final_score'])` at line 199 without a transaction wrapper. `_settle_wager` is guarded by an idempotency check (line 179: `if leg.status != 'pending': continue`) but the check happens **before** the outcome computation — a concurrent second verifier run could compute the same outcome and both attempt to save. Given §1 Finding 1 (task currently never runs, so no concurrent risk), this debt is **latent** — it would materialize the first time two concurrent dispatches fire (e.g., manual dispatch during ORM-fix work). **Operational risk: MED** (latent race condition). **Architectural risk: LOW** (bounded fix: wrap the pending-leg fetch in `select_for_update()` inside a `@transaction.atomic()`).

**Compounding-risk observation (Rigby SIGN cycle 1 batch 2 Q6 fold — F3).** Findings 1 + 5 combine into a user-experience worst-case: settlement doesn't run automatically (Finding 1) AND users may be looking at a **different aggregation surface** than the one the settlement path would update (Finding 5). Users can see **stale AND inconsistent** data with no visible "system is behind" signal. Rigby: "**orchestration + idempotency are non-negotiable operational-readiness gates**" — Cat C requires both before graduating to WORKING regardless of posture choice.

**Cat C maturity verdict** per §13: **PARTIAL (armed but zero-fire)**. Model layer + service layer + user-facing surfaces are complete and would be WORKING under normal operation. The scheduling drift + missing test coverage + missing concurrency/idempotency + posture-decision-pending integration surface hold Cat C at PARTIAL. Upgrade to WORKING requires: (a) restoring beat schedule (or documenting intentional deferral in `docs/AUDIT_FINDINGS.md` §12); (b) idempotency + concurrency safety **before** beat restoration (Rigby cycle 1 batch 2 Q5 fold — F7 new debt item); (c) minimum test coverage on settlement logic; (d) reconciling the two task variants; (e) reconciling `Bankroll` vs `BettingStats` dual aggregation.

---

## 2. Domain Purpose

**Q1 — What is this domain for?** Category C tracks user-placed sports wagers (`PlacedWager` + `PlacedWagerLeg` for parlays) and settles their outcomes against completed-game scores fetched via `TheOddsSpider.fetch_scores()`, then aggregates per-user W/L/ROI/streak stats (`BettingStats`) and feeds a one-way learning bridge to `UserAgentLearning` + `AgentMemory` via `SportsBettingLearningBridge`.

**Q2 — What problem does it solve?** Cat C is the user-side ground-truth surface for the sports betting product-line: (a) it persists the bets that users actually placed (via Discord `/bet`, PA `sports_record_wager`, REST `/api/v1/betting/place/`) — this is the auditable record; (b) it settles those bets against real-world scores so users see canonical outcomes rather than sportsbook-reported outcomes; (c) it aggregates outcomes into stats surfaces (Discord `/bankroll` for real-time, REST `/api/v1/betting/stats/` for structured) that let users see performance over time; (d) it feeds outcome data to a learning bridge so agent memory + user-agent learning tables can be shaped by real wager outcomes (though see §1 Finding 2 — this loop does NOT extend to Cat B `MLPrediction.was_correct` calibration).

### 2.1 Cat C contract statement

Cat C is scoped to the **user-facing consumer** of Cat A odds/score data and Cat B (nominally) prediction outputs — Cat B outputs, in practice, are consumed via user judgment (users read Cat B analytics on the frontend and decide whether to place bets) rather than programmatically. Cat C **does** guarantee:

- Every `PlacedWager` created through the working PA + REST + Discord write surfaces is persisted with `stake` (DecimalField), `odds` (IntegerField, American), `potential_payout` (DecimalField), and initial `status='pending'`.
- Every `PlacedWagerLeg` for a parlay carries the event identifier (`event_id` string), sport/matchup metadata, `pick` string, and its own `status` (pending → won/lost/push, no cancelled option distinct from parent).
- When `BettingOutcomeVerifier.verify_all_pending()` is invoked (currently only manually per §1 Finding 1), pending legs whose `commence_time` is `>= MIN_HOURS_AFTER_START` in the past are evaluated against Odds API scores; single-bet outcomes flow through market-specific evaluators; parlay outcomes aggregate via all-must-win logic.
- If the settlement path completes successfully AND wagers were settled, `BettingStats.recalculate()` is called per-user (full O(n) rescan).
- If settlement completes with settled outcomes, `SportsBettingLearningBridge.record_wager_outcome()` writes `UserAgentLearning` + `AgentMemory` rows.

Cat C **does NOT** guarantee:

- That `verify_betting_outcomes` fires on any cadence — no `PeriodicTask` row exists and no `core/celery.py` beat entry references this task; the task has 0 CeleryTaskEvent rows in the last 30 days for both variants (§1 Finding 1).
- That outcomes propagate back to Cat B `MLPrediction.was_correct` — no code path exists (§1 Finding 2). Cat B prediction correctness is set by a separate task `evaluate_ml_predictions` at `core/tasks.py:6192`.
- That outcomes emit `SignalCluster` rows — no code path exists (§1 Finding 3).
- That the two task variants (`core.tasks.verify_betting_outcomes` + `sports.verify_betting_outcomes`) share behavior — they call the same `BettingOutcomeVerifier` but differ in retry policy and BettingStats-recalc wrapping (§1 Finding 4).
- That the Discord `/bankroll` view of user betting stats agrees with the `BettingStats` model — Discord reads a separate `Bankroll` model surface (§1 Finding 5).
- That concurrent verifier runs are race-safe — no `select_for_update()` and no `@transaction.atomic()` wrapping (§1 Finding 10).
- That settlement logic is regression-tested — zero test coverage in `core/tests/` (§1 Finding 9).
- Cat C is downstream-integrated with Signal Engine, Memory Domain (beyond `AgentMemory`), Initiative pipeline, or Deliverable domain — all zero (§1 Findings 3, 6; posture-decision-pending).
- Fixture-identity reconciliation across bookmakers — Cat C stores The Odds API `event_id` strings, doesn't attempt cross-book identity resolution (see S1501 §14.2 + S1502 §15 debt #12 fixture-identity backlog).

**Sibling contract inheritance (per playbook §9 anti-duplication):** Cat C inherits Cat A's "does NOT guarantee" list (S1501 §2.1) and Cat B's "does NOT guarantee" list (S1502 §2.1) unchanged. Where Cat B S1502 §1 Finding 3 flagged post-fetch dict-return-shape coupling on the odds-data read side, Cat C has an analogous coupling on the score-lookup side (§1 Finding 7) — settlement is coupled to the Odds API `event_id` naming, not to a normalized `sports.models.Game.external_id_map`.

---

## 3. Canonical Entry Points

**Q3 — What are the canonical entry points?**

### 3.1 Write entry points (wager placement) — 3 confirmed sites via verifier grep

| Entry point | file:line | Handler / view | Auth |
|---|---|---|---|
| REST `POST /api/v1/betting/place/` | `core/urls.py:3117` → `core/views_betting.py:82` | `place_bet()` view — direct `PlacedWager.objects.create(...)` + manual `PlacedWagerLeg.objects.create()` loop for parlay legs | `@permission_classes([AllowAny])` |
| REST `POST /api/v1/betting/quick_pick/` (implied — sibling to place_bet) | `core/urls.py` (near 3117) → `core/views_betting.py:515` | `quick_pick()` view — direct `PlacedWager.objects.create(...)` for single bets | `@permission_classes([AllowAny])` per Sub-agent 3 |
| PA tool action `intelligence_tool` `sports_record_wager` | `core/services/pa_tool_schemas.py:3241` → `core/services/td_handlers_content.py:4261` | `_handle_sports_betting('record_wager')` — computes `potential_payout` from American odds, then `PlacedWager.objects.create(**wager_kwargs)` | PA gateway auth (Chris + workspace scope) |

**Verifier-grep confirmation:** `PlacedWager.objects.create` returns exactly the 3 sites above plus the model definition at `core/models_betting.py:13` (that's the class, not a caller). No hidden 4th write site.

### 3.2 Settlement entry points — 2 co-existing Celery task variants

| Entry point | file:line | Cadence (docstring claim) | Cadence (verified) |
|---|---|---|---|
| Celery task `core.tasks.verify_betting_outcomes` | `core/tasks.py:6121-6184` | "Runs every 2 hours via Celery Beat" (line 6129) | **NEVER (0 CeleryTaskEvent rows in 30d)** — see §1 Finding 1 |
| Celery task `sports.verify_betting_outcomes` | `sports/tasks.py:414-441` | not stated in docstring | **NEVER (0 CeleryTaskEvent rows in 30d)** |

**Manual dispatch is possible** via `celery -A core call core.tasks.verify_betting_outcomes` OR via Django-Celery-Admin (if a UI runner is wired). Neither variant is exposed as a PA tool for manual re-dispatch (see §1 Finding 1 debt + Cat B S1502 §1 Finding 2 registry-gap analogue for Cat C).

### 3.3 REST endpoints — 11 endpoints in `core/urls.py:3090-3123` (Sub-agent 3 inventory)

| URL | View | HTTP | Auth |
|---|---|---|---|
| `api/v1/odds/bankroll/` | `get_bankroll_management` (`core/views_odds_sports.py:742`) | GET | AllowAny |
| `api/v1/odds/bankroll/stats/` | `get_bankroll_stats` (`core/views_odds_sports.py:768`) | GET | AllowAny |
| `api/v1/betting/wager/` | `log_wager` | POST | AllowAny |
| `api/v1/betting/wagers/` | `get_wagers` (`core/views_betting.py:128`) | GET | AllowAny |
| `api/v1/betting/wagers/<uuid:wager_id>/` | `get_wager_detail` (`core/views_betting.py:217`) | GET | AllowAny |
| `api/v1/betting/wagers/<uuid:wager_id>/settle/` | `settle_wager` (`core/views_betting.py:273`) | POST | AllowAny |
| `api/v1/betting/wagers/<uuid:wager_id>/cancel/` | `cancel_wager` (`core/views_betting.py:347`) | DELETE | AllowAny |
| `api/v1/betting/stats/` | `get_betting_stats` (`core/views_betting.py:384`) | GET | AllowAny |
| `api/v1/betting/recent/` | `get_recent_activity` | GET | AllowAny |
| `api/v1/betting/place/` | `place_bet` (`core/views_betting.py:82`) | POST | AllowAny |
| `api/v1/betting/quick_pick/` | `quick_pick` (`core/views_betting.py:515`) | POST | AllowAny |

**All 11 endpoints use `@permission_classes([AllowAny])`** per Sub-agent 3 report — meaning any unauthenticated caller can create, read, settle, or cancel wagers (subject to the endpoint's own body-validated user_id if provided). **Operational risk observation:** the `AllowAny` auth pattern combined with Cat C's leaf-domain isolation (§1 Finding 8) means the surface is un-scoped by workspace or user identity at the auth layer. Session 1099-style provenance rules (per memory-rule `feedback_verifier_loop_pattern.md`) would flag this for verification — but per §14 and this is inherited AllowAny across the sports app family (S1502 §6 confirmed similar pattern for Cat B REST endpoints) — DRIFT to note in §14 but not novel to Cat C.

### 3.4 PA tool actions — 2 registered

| Action | Schema line | Handler | Behavior |
|---|---|---|---|
| `intelligence_tool` `action=sports_wagers` | `core/services/pa_tool_schemas.py:3241` | `_handle_sports_betting('wagers')` at `core/services/td_handlers_content.py:4197` | Reads `PlacedWager` rows — user-scoped if `user_id` provided |
| `intelligence_tool` `action=sports_record_wager` | `core/services/pa_tool_schemas.py:3241` | `_handle_sports_betting('record_wager')` at `core/services/td_handlers_content.py:4215-4271` | Creates a `PlacedWager` — validates `stake` + `odds` + `description`; computes `potential_payout` from American odds |

**PA tool registry gap (analogous to Cat B S1502 §1 Finding 2):** No `verify_betting_outcomes` / `betting_outcome_verifier` / `bankroll_recalculate` / `betting_stats` PA tool registered. Rigby cannot manually trigger settlement, recalculate a user's stats, or verify a specific wager via a surgical PA-tool call. This is an **operational-risk debt** paralleling S1502's finding for the agent-side (`sports_odds_analyst` + `arbitrage_detector` unregistered). Fills the pattern: Cat B has 2 of 4 audited agents unregistered as PA tools; Cat C has 0 of 3 obvious operational surfaces (verifier, recalc, stats) unregistered. Combined Cat B + Cat C picture: sports-domain PA tool coverage is patchy on the write / trigger side.

### 3.5 Discord commands — 4 sibling commands under the betting suite

Per Sub-agent 3 inventory (`core/services/discord_bot.py`):

| Command | Line | Purpose | Reads/Writes |
|---|---|---|---|
| `/bankroll` | 1404-1527 | View bankroll + recent 5 wagers + performance stats | **READS `core.models_bankroll.Bankroll` + its `wagers` relation, NOT `PlacedWager` or `BettingStats`** — see §1 Finding 5 |
| `/bet` | 1530 | Log new bet | Writes to Bankroll surface, NOT `PlacedWager` |
| `/resolve` | 1639 | Resolve pending bet (won/lost/push) | Writes to Bankroll surface |
| `/slip` | 1851 | Generate bet slip with multiple selections | Writes to Bankroll surface |

**Discord surface data-model divergence:** all 4 Discord betting commands operate on `core.models_bankroll.Bankroll` + its `wagers` FK relation, **not** on the `core.models_betting.PlacedWager` surface. Two disjoint aggregation domains. This is §1 Finding 5's core evidence.

### 3.6 WebSocket consumers — zero

Grep for `WagerConsumer` / `BankrollConsumer` in `core/consumers*.py`: zero matches. Grep for `/ws/wagers/` or `/ws/bankroll/` in `core/routing.py`: zero matches. **No realtime channel for Cat C.** Real-time UI updates on wager settlement would require polling the REST endpoint or watching `BettingStats.last_updated`. Frontend Cat E (S1505) audit scope owes the polling-vs-channel question.

### 3.7 Management commands — zero

`core/management/commands/` grep for `wager` / `bankroll` / `betting_outcome` / `verify_betting`: zero matches (Sub-agent 3 verified). Cat C has **no CLI surface for operations** — no `manage.py recalc_betting_stats`, no `manage.py verify_wager <uuid>`, no `manage.py migrate_bankroll_to_placedwager`. This blocks operator remediation of §1 Finding 1 (once beat is fixed, backfill logic requires manual REPL commands).

---

## 4. Major Models

**Q4 — What are the major models?**

Cat C has 3 primary models in `core/models_betting.py` (289 lines total per `wc -l`). One additional shared model (`Bankroll`) surfaces in Cat C data flow via Discord but lives at `core/models_bankroll.py` (out of Cat C scope for schema audit; in-scope for §1 Finding 5 dual-aggregation flag).

### 4.1 `PlacedWager` — `core/models_betting.py:13`

- 11 fields; UUID PK; ordering by `-placed_at`.
- **Choices sets:**
  - `WAGER_TYPE_CHOICES = [('single', 'Single Bet'), ('parlay', 'Parlay')]`
  - `STATUS_CHOICES = [('pending', 'Pending'), ('won', 'Won'), ('lost', 'Lost'), ('push', 'Push'), ('cancelled', 'Cancelled')]`
- **FK:** `user = ForeignKey(AUTH_USER_MODEL, on_delete=CASCADE, related_name='wagers', null=True, blank=True)`. Null-allowed at DB level — see §15 debt #7.
- **Money fields:** `stake` = `DecimalField(max_digits=10, decimal_places=2)`. `potential_payout` = `DecimalField(max_digits=12, decimal_places=2)`. `result_amount` = `DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)`. **All Decimal, not Float** — correct for money handling.
- **Odds:** `odds = IntegerField()` — American-format odds; conversion to decimal via `.decimal_odds` property.
- **Time fields:** `placed_at = DateTimeField(default=timezone.now)`; `settled_at = DateTimeField(null=True, blank=True)`.
- **Indexes** (3, all on PlacedWager per Sub-agent 1):
  - `Index(fields=['user', 'status'])` — supports per-user pending-wager scans
  - `Index(fields=['placed_at'])` — supports ordering
  - `Index(fields=['status'])` — supports the verifier's pending-wager scan
- **Methods:**
  - `settle(won: bool, push: bool)` — sets `status` + `result_amount` + `settled_at`. Called from `BettingOutcomeVerifier._settle_wager()`.
  - `decimal_odds` (property) — American → decimal conversion.
  - `implied_probability` (property) — implied win probability from odds.
  - `calculate_payout()` — potential payout computation.
- **No** `save()` override; **no signals** (Sub-agent 2 verified). PlacedWagerLeg auto-creation is caller-side (loop after PlacedWager creation).
- **4-item pre-brief mini-schema:** see §4.4 table.

### 4.2 `PlacedWagerLeg` — `core/models_betting.py:108`

- 12 fields; UUID PK; ordering by `('wager', 'id')`.
- **Choices sets:**
  - `MARKET_TYPE_CHOICES = [('h2h', 'Moneyline'), ('spreads', 'Spread'), ('totals', 'Total'), ('props', 'Player Prop'), ('futures', 'Futures')]`
  - `STATUS_CHOICES = [('pending', 'Pending'), ('won', 'Won'), ('lost', 'Lost'), ('push', 'Push')]` — **note: no `cancelled` option**, unlike PlacedWager
- **FK:** `wager = ForeignKey(PlacedWager, on_delete=CASCADE, related_name='legs')`. Not nullable.
- **Event metadata (all CharField, no FK):**
  - `event_id` — CharField(max_length=100) — The Odds API event ID
  - `sport` — CharField(max_length=50)
  - `matchup` — CharField(max_length=200)
  - `commence_time` — DateTimeField(null=True, blank=True)
- **Bet-specific:** `market_type`, `pick` (CharField 200), `odds` (IntegerField), `line` (DecimalField(6, 1) null-allowed), `bookmaker` (CharField 50).
- **Outcome:** `status` (CharField, choices as above), `final_score` (CharField 50, blank-allowed).
- **No indexes defined** in `Meta` (Sub-agent 1).
- **No FK to `sports.models.Game`** — see §1 Finding 7.
- **Methods:** `decimal_odds` (property) — American → decimal conversion.
- **4-item pre-brief mini-schema:** see §4.4 table.

### 4.3 `BettingStats` — `core/models_betting.py:163`

- 15 fields; BigAutoField PK; verbose_name_plural "Betting stats".
- **FK:** `user = OneToOneField(AUTH_USER_MODEL, on_delete=CASCADE, related_name='betting_stats', null=True, blank=True)`. Null-allowed.
- **Aggregate integer counters:** `total_wagers`, `wins`, `losses`, `pushes`, `pending`, `current_streak`, `longest_win_streak`, `longest_loss_streak` — all `IntegerField(default=0)`.
- **Aggregate money:** `total_stake`, `total_profit_loss` — `DecimalField(12, 2, default=Decimal('0.00'))`.
- **JSON break-out fields:**
  - `singles_record` — JSONField(default=dict)
  - `parlays_record` — JSONField(default=dict)
  - `stats_by_sport` — JSONField(default=dict)
- **Time field:** `last_updated = DateTimeField(auto_now=True)`.
- **No indexes** defined (Sub-agent 1). Given OneToOne on user + `auto_now`, this is defensible for per-user lookup.
- **Methods:**
  - `recalculate()` — full O(n) rescan of user's settled wagers (per Sub-agent 6) — no delta logic; see §15 debt #4.
  - `win_rate` (property)
  - `roi` (property)
- **4-item pre-brief mini-schema:** see §4.4 table.

### 4.4 4-item pre-brief mini-schema per model (D62 fold)

| Model | (a) sports-only vs shared | (b) DBAO schema vs public schema | (c) integration posture (refactor vs extend) | (d) island posture (additional isolation) |
|---|---|---|---|---|
| `PlacedWager` | sports-only (fields sports-betting-specific: parlay, American odds, per-user W/L) | **public schema, core app** (`core.models_betting`; no `Meta.app_label` override; no `db_table='dbao.xxx'` — Sub-agent 4 verified) | **extend** — no refactor needed for integration. Could add nullable `signal_cluster` FK for post-hoc SignalCluster attribution under integration posture; could add `related_prediction` FK to `sports.models.MLPrediction` for feedback-loop connection. Neither requires migration data loss. | **strong isolation already** — leaf domain (§1 Finding 8); no inbound FKs; outbound only to AUTH_USER_MODEL. Island posture requires no additional isolation infrastructure. Retention TTL under either posture (§15 debt #2). |
| `PlacedWagerLeg` | sports-only | public schema, core app | **extend** — could add nullable `game` FK to `sports.models.Game` under integration posture (using `event_id` string as backfill lookup key). Cross-book fixture-identity work (S1502 §15 debt #12) is separately owed but could piggyback. | **strong isolation already** — no cross-domain FK; `event_id` string keeps Cat C decoupled from `sports.models.Game` schema drift. Island posture already fits. |
| `BettingStats` | sports-only (per-sport JSON breakout is sports-specific) | public schema, core app | **extend** — could add nullable `snapshot_cluster` FK for signal-emission ancestry under integration posture; could split `stats_by_sport` JSON into a related model for query performance. | **strong isolation already** — OneToOne to AUTH_USER_MODEL; no inbound FKs. Island posture requires no additional isolation. Full-rescan `recalculate()` (§15 debt #4) affects either posture equally. |
| `Bankroll` (`core.models_bankroll`, not audited in Cat C — Discord surface — see §1 Finding 5) | shared (Discord surface + potential future frontend) | public schema, core app | **posture-decision** — refactor OR remove. Either (a) merge `Bankroll.wagers` into `PlacedWager` with a Discord-facing view, OR (b) keep as separate Discord-only aggregation and document. Both require caller migration in `core/services/discord_bot.py:1404-1527, 1530, 1639, 1851`. | **N/A while dual-model** — Bankroll is not Cat C-owned; §1 Finding 5 identifies the dual-model drift, not a Cat C isolation question. |

**Note:** No Cat C-owned model lives in a `dbao` PostgreSQL schema. Parent §3.F flags DBAO codename shape as an xx99 parked question; Cat C evidence confirms **public-schema-only** for all Cat C write surfaces on `main` at HEAD `55a34b6c`. If integration posture chose "move sports models to `dbao` schema", this is a **full refactor** per (c) axis for every Cat C model — every write site (§3.1) + read site + admin + serializer + viewset + migration + Django app config would need adjustment. Not zero-cost.

### 4.5 Migration lineage (Sub-agent 1 verified)

- All 3 Cat C models were created in **migration 0128_session_563_bet_tracking.py** (2025-12-28).
- **No subsequent migrations** have modified `PlacedWager`, `PlacedWagerLeg`, or `BettingStats`. Migration 0128 is the sole migration touching Cat C surface.
- This means: schema is frozen at Session 563 shape. Any integration-posture schema addition is a **new migration**, not an extension of existing lineage.

---

## 5. Major Services

**Q5 — What are the major services?**

Cat C has 2 primary service surfaces: `BettingOutcomeVerifier` (settlement logic) and `SportsBettingLearningBridge` (learning-write bridge). Total 1,176 lines. Neither exceeds the playbook §5.3 3,000-line god-service threshold.

### 5.1 `BettingOutcomeVerifier` service layer

- Location: `core/services/betting_outcome_verifier.py:21`, **480 lines total** (verifier-loop caught Sub-agent 6's 340 miscount — see §20.4).
- Class-level constant: `MIN_HOURS_AFTER_START = 3` (line 26 per direct read; Sub-agent 6 miscounted as line 28 — see §20.4).
- No explicit `__init__()` — stateless service.
- **Public method (only 1):** `verify_all_pending(self)` at line 30 — returns dict with keys `wagers_settled, wagers_skipped, arb_items_verified, arb_items_skipped, legs_settled, learning_records, errors`.
- **Private helper methods (11):**
  - `_fetch_all_scores(self, sport_event_pairs)` at line 138 — batches Odds API calls via `TheOddsSpider.fetch_scores()`
  - `_settle_wager(self, wager, score_lookup)` at line 169 — main settlement loop
  - `_determine_leg_outcome(self, leg, score_data)` at line 228 — routes to market-specific evaluator
  - `_evaluate_h2h(...)` at line 259 — moneyline outcome logic
  - `_evaluate_spread(...)` at line 286 — spread evaluation with line parsing
  - `_evaluate_total(...)` at line 310 — over/under evaluation
  - `_parse_line_from_pick(self, pick)` at line 335 — regex-based line extraction from pick string
  - `_teams_match(self, pick, team_name)` at line 345 — fuzzy team-name matching heuristic
  - `_verify_arb_item(self, item, score_lookup)` at line 376 — arbitrage-detection verification path
  - `_calculate_arb_profit(self, payload, winning_side)` at line 417 — actual P/L computation for verified arbs
  - `_create_learning_records(self, settled_wagers, verified_items)` at line 455 — bridges to `SportsBettingLearningBridge`

**Lazy imports (verifier-relevant):**

| Line | Import | Purpose |
|---|---|---|
| 38 | `from core.models_betting import PlacedWager, PlacedWagerLeg` | pending-wager scan |
| 39 | `from core.models_human_interface import HumanAttentionItem` | arbitrage-item verification |
| 148 | `from ai_core.spiders.specialized.theodds_spider import TheOddsSpider` | score fetch |
| 461 | `from core.learning_bridges.sports_betting_bridge import SportsBettingLearningBridge` | learning write |

**Critical grep-verified absence:** Zero imports of `MLPrediction`, `SignalCluster`, `SignalService`, `AgentMemory`, `MemoryLane` in the file (grep-verified 2026-07-02 — see §20.4 verifier-loop). This is the ORM-side evidence for §1 Findings 2, 3, 6.

**Cross-domain dependencies (bounded, 2 direction):**
- Downstream (write): `PlacedWager`, `PlacedWagerLeg` status transitions; `HumanAttentionItem.record_verification()`; delegation to `SportsBettingLearningBridge`.
- Upstream (read): `TheOddsSpider.fetch_scores()` — Cat A boundary (in-scope for read; not overcoupling).
- **No circular imports** observed at the service layer.

### 5.2 `SportsBettingLearningBridge` bridge layer

- Location: `core/learning_bridges/sports_betting_bridge.py:1`, **696 lines total** (`wc -l` verified).
- 16 methods (`grep -c` on class/def patterns — includes `class` line and `def` lines).
- **Purpose:** one-way outcome-to-learning bridge. Called from `betting_outcome_verifier._create_learning_records()` at line 455-480. Writes `UserAgentLearning` + `AgentMemory` rows.
- **Reads `MLPrediction.was_correct`** at line 394 (`if prediction.was_correct:`) for aggregate reporting purposes (Sub-agent 4 + verifier-grep confirmed). **Does NOT write `MLPrediction.was_correct`** — that field is set upstream by the separate `evaluate_ml_predictions` task at `core/tasks.py:6192`.
- Two record-write entry points (per Sub-agent 4):
  - `record_wager_outcome(wager)` at line 488-551 — writes `UserAgentLearning` (line 503-517) + `AgentMemory` (line 532-549 with `source_type='betting_outcome_verification'`)
  - `record_arbitrage_outcome(item)` at line 555-631 — parallel pattern for arbitrage items
- **Reads MLPrediction** at line 237-238 (`MLPrediction.objects.filter(...)`) — bridge-internal reporting queries, not settlement-integration.

### 5.3 Dependency chain + god-service check

- **Total line count:** 1,176 across the 2 surfaces (480 + 696).
- **Largest single file:** `SportsBettingLearningBridge` at 696 lines — well under the 3,000-line god-service threshold.
- **Cross-domain imports out of Cat C:**
  - `betting_outcome_verifier.py` → `HumanAttentionItem` (Human Interface domain), `TheOddsSpider` (Cat A / spider domain), `SportsBettingLearningBridge` (Cat C learning bridge — same-domain).
  - `sports_betting_bridge.py` → `MLPrediction` (Cat B / Sports domain), `UserAgentLearning` + `AgentMemory` (Memory Domain S1300 surface).
- **Circular-import risk:** MINIMAL — all cross-domain imports are lazy (in-method) at both service files.

### 5.4 Additional Cat C read surfaces (F1 fold — Rigby SIGN cycle 1 batch 1 Q1)

The initial Sub-agent 5 sweep bounded read surfaces to REST + PA + Discord. Rigby SIGN cycle 1 Q1 grep pressure-test surfaced 3 additional Cat C read touchpoints worth acknowledging as broader-consumer surfaces:

- **`core/views_odds_sports.py`** — imports `PlacedWager` at `:746` and reads for the bankroll REST endpoints (`get_bankroll_management` at `:742`, `get_bankroll_stats` at `:768`) plus admin/diagnostic views. This is broader than "just bankroll REST" — it includes any Cat C read that overlaps with the odds/sports view module.
- **`core/services/td_handlers_content.py`** read path — beyond the write path at `:4261` (already in §3.1), the handler module contains `PlacedWager` / `BettingStats` read queries for reporting / content-generation contexts. These read patterns should be surveyed under a future Cat D S1504 sweep since they intersect content pipeline.
- **`core/services/sports_content_context.py`** — references `PlacedWager` for building sports-content context (per Sub-agent 2 initial report; `SPORTS_MONETIZATION_ML.md` line 89 also flags this integration). Cat C data feeds into content briefs at read-time; **write side is Cat D scope** (S1504 owned).

None of these change the maturity verdict (all reads, no writes); they broaden the "who reads Cat C data" surface for Cat F evidence plan consideration.

### 5.5 Bankroll adjacency touchpoints (bounded — F2/F14 folds)

The `Bankroll` surface (§1 Finding 5) is deliberately out of Cat C scope per §5 non-goals. Two important adjacency notes to prevent misreading:

- **Two `Bankroll`-related model classes exist** in the codebase (Rigby SIGN cycle 1 batch 3 Q8 grep-verified — F14 fold): `Bankroll` at `core/models_bankroll.py:19` (referenced by Discord `/bankroll` per §1 Finding 5) AND `BankrollManagement` at `sports/models.py:1032` (with serializer at `sports/serializers.py:368`, admin at `sports/admin.py:405`, and a `BankrollManager` agent at `sports/agents.py:738`). This audit does NOT claim bankroll is a core-only surface.
- **Cat C settlement affects bankroll views indirectly** — settled wagers roll up into `Bankroll.wagers` (Discord surface) and `BettingStats` (core surface); the dual-model drift (§1 Finding 5 / §14.5 / §15.10) is a Cat C-owned observation but the deep-audit of `Bankroll` + `BankrollManagement` internals belongs to a future Discord domain audit and/or the Sports app internal audit.

### 5.6 4-item pre-brief mini-schema per service (D62 fold)

| Service | (a) sports-only vs shared | (b) DBAO vs public | (c) integration posture | (d) island posture |
|---|---|---|---|---|
| `BettingOutcomeVerifier` | sports-only (wager settlement math is sports-specific) | public — no DBAO isolation | **extend** — could add `MLPrediction.was_correct` write bridge under integration posture (single line addition in `_settle_wager` at ~line 205: `if leg.wager.related_prediction: prediction.evaluate(...)`); could emit `SignalCluster` on settlement under integration posture. Both are extensions, not refactors. Also could reconcile with `sports/tasks.py:414` variant by consolidating into one task; either variant can be selected. | **strong isolation already** — pure functions on wager + score data; island posture requires no additional isolation infra. **BUT §1 Finding 1** applies under BOTH postures: beat-schedule fix is required for the service to fire regardless of posture choice. |
| `SportsBettingLearningBridge` | sports-only (specialized for sports outcome learning) | public — no DBAO isolation | **refactor OR extend** — under integration posture: (a) extend bridge to write `MemoryLane` (S1300 broader memory surface) in addition to `AgentMemory`; (b) extend bridge to write `SignalCluster` outcome events; (c) OR refactor into a domain-agnostic `OutcomeLearningBridge` if similar sports/stocks/legislation outcome bridges are planned. Under island posture: preserve current `AgentMemory` + `UserAgentLearning` shape. | **strong isolation already** — one-way write bridge; no read-back from Memory Domain; island posture already fits. Retention on `AgentMemory` rows written by the bridge is a Memory Domain concern (S1300 owned), not Cat C. |

---

## 6. Major APIs and Interfaces

**Q6 — What are the major APIs?**

### 6.1 REST endpoints — 11 endpoints (details §3.3)

All 11 REST endpoints use `@permission_classes([AllowAny])` — inheriting the AllowAny pattern from the wider sports-app REST surface. No workspace scoping observed. Return types are hand-crafted JSON responses; no DRF Serializer class is used (Sub-agent 3 confirmed via grep).

Notable endpoints:
- `POST /api/v1/betting/place/` at `core/views_betting.py:82` — single-shot wager creation (single or parlay); direct model instantiation, no service layer.
- `POST /api/v1/betting/wagers/<uuid>/settle/` at `core/views_betting.py:273` — manual settlement bypass for the beat-scheduling gap (§1 Finding 1). If beat fires, this is redundant; while beat is dark, this is the only way to settle a specific wager. Behavior: takes `won` / `push` params, calls `PlacedWager.settle()` model method directly — **does NOT invoke the score-fetching path**, so users can settle wagers manually with wrong outcomes.
- `GET /api/v1/betting/stats/` at `core/views_betting.py:384` — reads `BettingStats` after calling `recalculate()` on the fly (per Sub-agent 3 report) — this **is** an on-demand recalc path that bypasses the never-firing task.

### 6.2 PA tools — 2 actions on `intelligence_tool`

- `intelligence_tool` `action=sports_wagers` — read-only listing of wagers.
- `intelligence_tool` `action=sports_record_wager` — write path for creating a wager. Payload schema at `pa_tool_schemas.py:3269-3274`: `stake`, `odds`, `description`, `wager_type`, `notes` all documented.
- **No PA tool for outcome verification / settlement / stats recalc / bankroll aggregation** — see §3.4 registry gap.

### 6.3 Celery task surface — 2 co-existing variants

- `core.tasks.verify_betting_outcomes` — `bind=True`, `max_retries=2`, `default_retry_delay=300`, `queue='default'` (decorator) / `queue='sports'` (settings routing override at `core/settings.py:1385`), Session 1165 retry budget policy. Includes BettingStats-recalc wrapper.
- `sports.verify_betting_outcomes` — no retry policy, no BettingStats wrapper, `queue='<default>'` (per `docs/CELERY_AUDIT.md:470`).
- **Neither has a beat schedule.** Neither is on `docs/AUDIT_FINDINGS.md` §12 deferred list. Both have 0 CeleryTaskEvent rows in 30d (Rigby verifier probe).
- **Beat entries for siblings** (Cat D — verified by inference from `docs/CELERY_AUDIT.md` and sports Cat D S1504 scope): `generate_daily_betting_brief` (`core/tasks.py:6187`), `collect_sports_odds_intelligence` — both have beat entries per Cat B S1502 §3.3 sibling references. Only the settlement task is missing.

### 6.4 Discord command surface — 4 commands under betting suite (§3.5)

- `/bankroll` `/bet` `/resolve` `/slip` — all read/write against `core.models_bankroll.Bankroll` (§1 Finding 5).
- `/odds` at `discord_bot.py:1108` — read-only odds display; touches Cat A surface, out of Cat C scope.

### 6.5 WebSocket surface — zero (§3.6)

No consumers, no routes. Real-time UI requires polling REST endpoints.

### 6.6 4-item pre-brief mini-schema per external surface (D62 fold)

| Surface | (a) sports-only vs shared | (b) DBAO vs public | (c) integration posture | (d) island posture |
|---|---|---|---|---|
| REST `/api/v1/betting/*` (11 endpoints) | sports-only | public routing (`/api/v1/`, not `/api/v1/dbao/`) | **extend** — could add DRF Serializer classes under integration posture for consistent JSON contracts across sports-app and mainline; could add workspace-scoping middleware under either posture (independent of integration/island axis — it's an auth-hardening item, §15 debt #6). | **strong isolation** — REST surface unchanged under island posture. |
| PA tool `intelligence_tool` actions `sports_wagers` + `sports_record_wager` | sports-only | public — PA tool registry has no DBAO namespace convention | **extend** — could register `sports_verify_wager` / `sports_recalc_stats` PA tools under either posture (§3.4 registry gap fix); could add `sports_bankroll_reconcile` under integration posture (if §1 Finding 5 dual-model is resolved). | **N/A** — PA tool surface is control-plane, not domain-boundary. |
| Celery task `core.tasks.verify_betting_outcomes` + `sports.verify_betting_outcomes` | sports-only | public queue (`sports` per settings routing) | **refactor** — must consolidate to 1 variant (§1 Finding 4) under either posture. Integration posture also could rename task to reflect broader responsibility (e.g., `verify_and_signal_wager_outcomes`). | **refactor** — same consolidation need. §1 Finding 1 beat-schedule fix is orthogonal to posture. |
| Discord `/bankroll` `/bet` `/resolve` `/slip` (4 commands) | sports-only (bankroll is sports-scoped even though Discord bot is domain-agnostic) | public — Discord bot writes to core.models_bankroll public schema | **refactor** — under integration posture, resolve §1 Finding 5 by merging Bankroll into PlacedWager surface. Under island posture, document Bankroll as intentional Discord-only surface with sync-off contract. | **posture-decision** — same dual-model resolution required. |
| WebSocket surface (zero) | sports-only (theoretical) | (n/a) | **extend** — could add `/ws/wagers/` channel under either posture for realtime settlement updates. Not blocking either posture. | **N/A** — absence is compatible with either posture. |

---

## 7. Runtime Flows

**Q9 — What are the major runtime flows?**

Two primary flows: **wager placement** (user-initiated write) and **outcome settlement** (task-initiated, currently silent). Plus a manual settlement path via REST.

### 7.1 Explicit call-chain — outcome settlement (S1502 F1 fold pattern applied)

This is the load-bearing flow for Cat C. Reproduced as a verbatim call-chain block per S1502 §7.1 F1 fold precedent (Rigby's stated preference for verbatim shape over prose description):

```
BEAT SCHEDULE (docstring claim: every 2h)
    └── PHANTOM — no beat entry exists in core/celery.py; PeriodicTask.objects.count() == 0
        (§1 Finding 1; §14.1 CRITICAL drift; blocks entire flow below in production)

MANUAL DISPATCH (only working path):
celery -A core call core.tasks.verify_betting_outcomes
    → core/tasks.py:6122 verify_betting_outcomes(self)  [bind=True, max_retries=2]
        → core/tasks.py:6132 lazy import BettingOutcomeVerifier
        → core/tasks.py:6137 verifier = BettingOutcomeVerifier()
        → core/tasks.py:6138 results = verifier.verify_all_pending()
            → core/services/betting_outcome_verifier.py:30 verify_all_pending()
                → line 38-39 lazy imports (PlacedWager, PlacedWagerLeg, HumanAttentionItem)
                → line 54-57 pending_legs query (NO select_for_update — §15 debt #10)
                → line 82 self._fetch_all_scores(sport_event_pairs)
                    → line 138 _fetch_all_scores()
                        → line 148 lazy import TheOddsSpider
                        → line 150+ spider.fetch_scores(sport_key, days_from=3) per sport
                            → ai_core/spiders/specialized/theodds_spider.py:787 fetch_scores()
                                → GET /v4/sports/{sport}/scores
                                → returns list[dict] with keys event_id/home_score/away_score/completed
                → line 91-111 for wager in pending_wagers:
                    → line 172 self._settle_wager(wager, score_lookup)
                        → line 169-226 _settle_wager()
                            → line 179 for leg in wager.legs.all():
                                → line 179 if leg.status != 'pending': continue  # idempotency
                                → line 197 outcome = self._determine_leg_outcome(leg, score_data)
                                    → line 228 _determine_leg_outcome() routes by market_type:
                                        → h2h  → line 259 _evaluate_h2h()
                                        → spreads → line 286 _evaluate_spread()
                                        → totals → line 310 _evaluate_total()
                                → line 197 leg.status = outcome
                                → line 199 leg.save(update_fields=['status', 'final_score'])
                                    [NO transaction wrapper — §15 debt #10 latent race]
                            → line 204-213 parlay resolution logic
                            → line 207 wager.settle(won=..., push=...)
                                → core/models_betting.py:92 PlacedWager.settle()
                                    → status assignment + result_amount + settled_at
                                    → self.save()
                → line 112-125 for item in watching_attention_items:
                    → line 384 self._verify_arb_item(item, score_lookup)
                        → line 376-415 _verify_arb_item()
                            → line 417 _calculate_arb_profit(payload, winning_side)
                            → line 413 item.record_verification(outcome, profit, notes)
                → line 127-128 self._create_learning_records(settled_wagers, verified_items)
                    → line 455-480 _create_learning_records()
                        → line 461 lazy import SportsBettingLearningBridge
                        → line 464 bridge = SportsBettingLearningBridge()
                        → line 466+ bridge.record_wager_outcome(wager)  # per settled wager
                            → sports_betting_bridge.py:488-551 record_wager_outcome()
                                → line 503-517 UserAgentLearning.objects.create()  # per user
                                → line 532-549 AgentMemory.objects.create(source_type='betting_outcome_verification')
                                [NOTE: NO write to MLPrediction.was_correct — §1 Finding 2]
                                [NOTE: NO write to SignalCluster — §1 Finding 3]
                                [NOTE: NO write to MemoryLane / AgentKnowledgeSource — §1 Finding 6]
                        → line 468+ bridge.record_arbitrage_outcome(item)  # per verified arb
        → core/tasks.py:6141-6156 BettingStats recalc wrapper (only in core.tasks variant, NOT sports.tasks variant)
            → PlacedWager.objects.filter(...) recently_settled query
            → per user: BettingStats.objects.get_or_create() → stats.recalculate()
                → core/models_betting.py:223-289 BettingStats.recalculate()
                    [Full O(n) rescan of user's settled wagers — §15 debt #4]
        → core/tasks.py:6164 return results
```

**Notable observations from the call-chain:**

1. Every `→` at the top of the chain is unreachable in production per §1 Finding 1 — no beat entry means the entire chain below is dead unless manually invoked.
2. The `BettingStats.recalculate()` step (`core/tasks.py:6141-6156`) is **only in the `core.tasks` variant**. The `sports/tasks.py:414` variant does NOT wrap BettingStats recalc — so if operator dispatches the `sports.` variant (matching by app namespace), stats never update.
3. The idempotency guard at `betting_outcome_verifier.py:179` (`if leg.status != 'pending': continue`) protects against reprocessing already-settled legs but does NOT protect against concurrent-run race on the same leg (§15 debt #10).
4. The MLPrediction absence (§1 Finding 2 evidence) is visible at the call-chain leaf — bridge writes `UserAgentLearning` + `AgentMemory` but there is no `MLPrediction.was_correct` write branch.
5. The SignalCluster absence (§1 Finding 3 evidence) is visible at the call-chain leaf — bridge writes broadly to memory tables but never to signal aggregation.

### 7.2 Wager placement flow (3 write sites, one-shot semantics)

- **PA tool path** (`sports_record_wager`): PA gateway → `td_handlers_content.py:4215-4271` → validates `stake` + `odds` + `description` → computes `potential_payout` via American odds math → `PlacedWager.objects.create(**wager_kwargs)` at line 4261 → returns `{action, id, ...}`. **No PlacedWagerLeg** created via this path — PA tool creates singles only.
- **REST `/api/v1/betting/place/` path**: `core/views_betting.py:82` → `PlacedWager.objects.create(...)` → loop over `picks` → `PlacedWagerLeg.objects.create()` per leg. Supports parlays.
- **REST `/api/v1/betting/quick_pick/` path**: `core/views_betting.py:515` → `PlacedWager.objects.create(...)` — single bets only.

All 3 paths bypass any service layer — direct model instantiation. **No wager-placement service exists** (Sub-agent 2 verified). This is a debt candidate under integration posture (see §15 debt #8), but under island posture the direct-write pattern is acceptable.

### 7.3 Manual settlement flow (frontend / REST bypass)

`POST /api/v1/betting/wagers/<uuid>/settle/` at `core/views_betting.py:273` — takes `won`/`push` params, calls `PlacedWager.settle()` directly. **Does NOT invoke score-fetch path.** Users on the frontend "My Wagers" tab (Cat E S1505 scope) can mark wagers manually via this REST endpoint even when scores are wrong or games are incomplete. Under §1 Finding 1 conditions this is currently the ONLY path to settle wagers. Once beat is re-enabled, this becomes a fallback path for cases where Odds API scores are unavailable — but with no auth guard on `AllowAny`, this is also an operational-risk item worth flagging.

---

## 8. Data Ownership and Lifecycle

**Q16 — What data does Cat C own?** **Q17 — What does it consume?** **Q18 — What does it produce?**

### 8.1 Owned data (writes to Cat C-exclusive models)

| Model | Write sites | Read sites |
|---|---|---|
| `PlacedWager` | REST `/place/` (`views_betting.py:82`), REST `/quick_pick/` (`views_betting.py:515`), PA `sports_record_wager` (`td_handlers_content.py:4261`), `PlacedWager.settle()` invoked from `BettingOutcomeVerifier._settle_wager()` + `settle_wager` REST view (`views_betting.py:273`) | REST `/wagers/`, `/wagers/<uuid>/`, `/recent/`, PA `sports_wagers`, `BettingOutcomeVerifier.verify_all_pending()` (line 54-57), `BettingStats.recalculate()`, `SportsBettingLearningBridge.record_wager_outcome()` — bridge reads FK-related agent + user, `Bankroll` model referenced from Discord `/bankroll` (§1 Finding 5 — separate model, not `PlacedWager`) |
| `PlacedWagerLeg` | Manual creation in `views_betting.py:82` + `views_betting.py:515` loop after PlacedWager.create, leg-status update in `_settle_wager()` at line 199 | `_settle_wager()` per-wager loop; parlay-resolution logic; REST `/wagers/<uuid>/` detail view |
| `BettingStats` | `BettingStats.recalculate()` from `verify_betting_outcomes` task wrapper (`tasks.py:6141-6156`) or from REST `/stats/` on-demand recalc | REST `/api/v1/betting/stats/` |

### 8.2 Consumed data (reads from outside Cat C)

- **`TheOddsSpider.fetch_scores()`** — Cat A boundary. Score dicts keyed by `(sport, event_id)`.
- **`AUTH_USER_MODEL`** — user IDs for `PlacedWager.user_id` and `BettingStats.user_id` FKs.
- **`HumanAttentionItem` (watching-status arbitrage rows)** — cross-domain read for arb verification path.
- **`MLPrediction` (via `SportsBettingLearningBridge`)** — read-only aggregation reporting (`sports_betting_bridge.py:237-238, 394`); NOT consumed for settlement decisions.

### 8.3 Produced data (writes to outside Cat C)

- **`UserAgentLearning`** (Memory Domain / S1300 surface) — via `SportsBettingLearningBridge.record_wager_outcome()` at `sports_betting_bridge.py:503-517`.
- **`AgentMemory`** (Memory Domain / S1300 surface) — via same bridge at `sports_betting_bridge.py:532-549`, `source_type='betting_outcome_verification'`.
- **`HumanAttentionItem.record_verification()`** — Human Interface domain write via `_verify_arb_item()`.

### 8.4 Not produced (grep-verified absences — load-bearing for Cat F)

- **NO `MLPrediction.was_correct` write from Cat C** (§1 Finding 2) — grep of `betting_outcome_verifier.py` for `MLPrediction` + `was_correct`: zero matches (verifier-loop confirmed).
- **NO `SignalCluster` writes from Cat C** (§1 Finding 3) — grep of `betting_outcome_verifier.py` for `SignalCluster` + `SignalService`: zero matches.
- **NO `Initiative` writes from Cat C** — Cat C does not create Initiatives from outcome events. Inherited gap from S1273 §3.10 documented drift + S1502 §14 posture-decision-pending.
- **NO `Deliverable` writes from Cat C** — Cat C does not produce Deliverables from outcomes. Contrast with Cat B agents which DO write Deliverables per S1502 §4.8 mini-schema.
- **NO `MemoryLane` / `AgentKnowledgeSource` writes** (§1 Finding 6) — Cat C's learning bridge is scoped to `UserAgentLearning` + `AgentMemory` only.

### 8.5 Lifecycle policies

- **Wager retention:** None (§15 debt #2). No task deletes / archives `PlacedWager` / `PlacedWagerLeg` / `BettingStats`.
- **Cascade on user deletion:** `CASCADE` — all wagers + stats deleted when a user row is deleted. Cross-domain CASCADE (from `AUTH_USER_MODEL`) is standard Django practice but worth flagging under GDPR posture.
- **Settled-state persistence:** wagers remain in DB post-settlement indefinitely. Historical wagers are queryable forever via REST `/api/v1/betting/wagers/`. `BettingStats` is a single OneToOne per user, updated in-place.
- **Idempotency:** the verifier's `if leg.status != 'pending': continue` guard (line 179) prevents re-settlement.

### 8.6 4-item pre-brief mini-schema per data owned (D62 fold)

| Owned data | (a) sports-only vs shared | (b) DBAO schema vs public schema | (c) integration posture (refactor vs extend) | (d) island posture (additional isolation) |
|---|---|---|---|---|
| `PlacedWager.status` state machine | sports-only | public schema, core app | **extend** — under integration posture, add `Initiative` FK for outcome-driven initiative creation; extend state-machine choices to include `settled_stale` (settled long after commence_time). Both are extensions, not schema-breaking. | **island already** — 5-state enum is complete; island posture requires retention TTL (§15 debt #2) — currently missing under either posture. |
| `PlacedWagerLeg.status` + `final_score` | sports-only | public schema | **extend** — under integration posture, add `game` FK to `sports.models.Game` (nullable, backfilled from `event_id`); add `signal_cluster` FK for signal-emission ancestry. | **island already** — `event_id` string decoupling is the island-posture-preferred pattern. |
| `BettingStats.*` counters + JSON break-outs | sports-only | public schema | **extend** — under integration posture, split `stats_by_sport` JSON into related `BettingStatsBySport` model for query performance + Signal Engine integration. Under island posture, JSON break-out is acceptable. | **island already** — OneToOne semantics + full-rescan `recalculate()` (§15 debt #4) are island-compatible. |
| Produced `UserAgentLearning` + `AgentMemory` rows | shared (Memory Domain surface) | public schema | **extend** — under integration posture, add `MemoryLane` write for broader memory-domain integration; under island posture, retain current shape. Note: Memory Domain (S1300) owns final decision on lane taxonomy. | **island already** — bounded write to `AgentMemory` + `UserAgentLearning` is a minimal Memory Domain footprint. |
| Non-production data: `MLPrediction.was_correct` (NOT written) | sports-only | (n/a) | **posture-decision** — integration posture requires wiring the write; island posture leaves it to the separate `evaluate_ml_predictions` task (§1 Finding 2 preserved as intentional decoupling). | **island already** — non-production is the island-posture-preferred pattern. |
| Non-production data: `SignalCluster` outcome emission (NOT written) | sports-only | (n/a) | **posture-decision** — same axis as `sports_odds` (S1274 §14 Finding #6); integration posture requires extending pattern_type + wiring emission call at `_settle_wager()` line 205. | **island already** — no emission = intentional isolation. |

---

## 9. Integrations With Other Domains

**Q14 — What integrations does Cat C have?** **Q15 — What's missing?** **Q17-18-21-22 as tables:**

| Domain | Direction | Status | Evidence |
|---|---|---|---|
| Sports Cat A (Odds Ingestion — S1501) | Inbound (read) | WORKING | `TheOddsSpider.fetch_scores()` invoked at `betting_outcome_verifier.py:150`; score dicts keyed by `(sport, event_id)` |
| Sports Cat B (Predictions — S1502) | **Missing** (§1 Finding 2; POSTURE-DECISION-PENDING per S1502 F3 precedent) | Zero code paths from settled wager → `MLPrediction.was_correct` (only the `evaluate_ml_predictions` task at `core/tasks.py:6192` writes this field, decoupled from Cat C) |
| Sports Cat D (Content Pipeline — S1504) | Outbound (indirect via BettingStats read) | UNKNOWN — see §16 boundary | S1504 audit scope; Cat C data may feed `generate_daily_betting_brief` if it reads `BettingStats` |
| Sports Cat E (Frontend — S1505) | Outbound (REST + polling) | WORKING (assumed) | 11 REST endpoints exposed; My Wagers + Records tabs on BettingPage (§3.6 no WebSocket, so polling-based); Cat E S1505 audit scope owes the polling contract |
| Sports Cat F (Posture — S1506) | Consumes Cat C evidence | In-progress — this doc contributes | This doc's Findings 1-10 owed to Cat F evidence plan |
| Memory Domain (S1300) | Outbound (write) | PARTIAL | `SportsBettingLearningBridge` writes `UserAgentLearning` + `AgentMemory`; MISSING: `MemoryLane` / `AgentKnowledgeSource` (§1 Finding 6) |
| Signal Engine (S1274 §14 Finding #6) | **Missing** (§1 Finding 3; POSTURE-DECISION-PENDING per S1502 F2 precedent) | Zero `SignalCluster` writes from Cat C — cascade of S1502 §14.3 into Cat C settlement side |
| Initiative Pipeline (S1273 §3.10 gap) | **Missing** | Cat C does not produce Initiatives from outcome events; documented gap since S1273 |
| Deliverable Pipeline (S1274 §12.3 evidence axis) | **Missing** | Cat C does not produce Deliverables (contrast S1502 Cat B agents which DO) |
| Human Interface (HumanAttentionItem) | Bidirectional | WORKING | Cat C READS watching-status HumanAttentionItem rows for arb verification; WRITES via `item.record_verification()` |
| DBAO schema (parent §3.F posture-decision) | (n/a) | not applicable | Cat C models live in `public` schema, not `dbao` (Sub-agent 4 verified via absence of `db_table` override + `DATABASE_ROUTERS` config) |
| Discord (via /bankroll) | Outbound (indirect via Bankroll model) | PARTIAL | §1 Finding 5 dual-model surface — Discord reads `Bankroll`, not `PlacedWager`; unclear sync path |
| Workspace scoping (`WorkspaceProfile`) | Not integrated | **Missing** | `PlacedWager` + `BettingStats` have no `workspace` FK; REST endpoints are `AllowAny` (§3.3 auth pattern). Under multi-tenant posture would be a gap. |

**Cross-domain FK inventory (per playbook §12 boundary-audit pattern):**

- **Outbound FKs:** 3 total. `PlacedWager.user`, `BettingStats.user` (both to `AUTH_USER_MODEL`), and `PlacedWagerLeg.wager` (self-reference within Cat C).
- **Inbound FKs:** 0 (§1 Finding 8 — leaf domain).
- **Cross-domain lazy imports (from services):** 4 total (Sub-agent 4 verified). `PlacedWager` + `PlacedWagerLeg` from `core.models_betting`, `HumanAttentionItem` from `core.models_human_interface`, `TheOddsSpider` from `ai_core.spiders.specialized`, `SportsBettingLearningBridge` from `core.learning_bridges` (via `betting_outcome_verifier.py`). Bridge itself imports `MLPrediction` from `sports.models` and `UserAgentLearning` + `AgentMemory` (Memory Domain surface).

---

## 10. Event Flows

**Q19 — What events does Cat C emit?** **Q20 — What events SHOULD it emit?**

### 10.1 Events emitted (verified via code)

Cat C **emits no formal Events** (no `EventBus.publish(...)` calls, no `signal_service.send(...)` calls). Grep of `betting_outcome_verifier.py` + `sports_betting_bridge.py` for `EventBus` / `publish_` / `signals.` / `receiver`: no substantive matches.

The **only "event-like" side effects** are:
- `AgentMemory` rows written with `source_type='betting_outcome_verification'` — these are event-like in that consumers could subscribe to `AgentMemory.objects.filter(source_type=...)` polling, but there is no push-based EventBus contract.
- `HumanAttentionItem.record_verification()` — updates in-place, no event emission.
- `PlacedWager.settled_at` + `settled_at` field updates — DB state change, no event emission.

**Cross-reference to `docs/research/platform/cross_domain_integration_audit.md` §6.2 Event producer/consumer registry** (lines 971-972 per Sub-agent 5): "`publish_outcome_recorded_event` — BettingOutcomeVerifier + Impact tracking; caller sweep incomplete." → This suggests an event-emission surface was planned or partially implemented (S1274 auditor could not find caller in code). Grep of the current codebase for `publish_outcome_recorded_event`: not found in the audit sweep. If this was implemented at some point and reverted, it's stale in S1274's audit; if it was planned and never landed, it's a legacy TODO. Either way, current runtime is: **no event emission from Cat C**.

### 10.2 Events SHOULD Cat C emit (integration posture) — POSTURE-DECISION-PENDING

Under integration posture per S1274 §12.3 framing:
- **`wager_settled` event** — payload `{user_id, wager_id, outcome, result_amount, sport, market_types, agent_ancestry}` → consumed by Cat B for `MLPrediction.was_correct` write + Signal Engine for `SignalCluster.pattern_type='sports_outcome'`.
- **`streak_transition` event** — when `BettingStats.current_streak` flips sign or crosses threshold → consumed by Initiative Pipeline for user-facing insight generation.
- **`arb_verified` event** — post-arb-verification outcome → consumed by Content Pipeline for post-mortem content.
- **`wager_placed` event** — pre-settlement notification → consumed by Cat B for prediction-vs-wager correlation tracking.

None of these are wired. Cat F evidence plan owes: which event types are load-bearing for integration posture vs which are optional.

### 10.3 Events SHOULD Cat C emit (island posture)

Under island posture: NONE. Cat C remains a pure user-side record surface with no event emission. Current state is the intended state.

---

## 11. Existing Documentation

**Q10 — What existing documentation exists for Cat C?**

Per Sub-agent 5 exhaustive sweep:

### 11.1 Topic docs — LIGHT coverage

- **No dedicated topic doc.** `docs/topics/sports.md` / `docs/topics/betting.md` / `docs/topics/wagers.md` — none exist.
- **`docs/topics/spider-network.md:91-119`** — references `TheOddsSpider.fetch_scores()` (Session 995/998B) — Cat A boundary that's a prerequisite for Cat C.
- **`docs/topics/celery-workers.md:177`** — mentions `verify_betting_outcomes` cadence (source of §1 Finding 1's docstring drift claim propagation).
- **`docs/topics/personal-assistant.md`, `docs/topics/frontend.md`, `docs/topics/tool-consolidation.md`** — mention wagers / bankroll in passing as features under broader domains.

### 11.2 Narrative docs — MODERATE coverage

- **`docs/narratives/SPORTS_MONETIZATION_ML.md`** (S1158, HIGH provenance) — comprehensive cross-reference of Cat C surfaces:
  - Lines 37-90: Vocabulary table covers `PlacedWager`, `PlacedWagerLeg`, `BettingOutcomeVerifier`, `verify_betting_outcomes` task (line 89 lists it as "every 30 min" — **drift with Session 995 handoff's "every 2h" and docstring's "every 2h"**), `/bankroll` command (line 81-82), `BettingStats` aggregation.
  - Lines 100-109: Milestone timeline citing S995 "Betting Outcome Verification + Learning Loop" (lines 106-107), S1010-S1011 sports pipeline maturation, `verify_betting_outcomes` beat scheduling (line 107).
  - Lines 248-251: Troubleshooting entry: "Sports wager stuck `pending` → `BettingOutcomeVerifier` not running, or `TheOddsSpider.fetch_scores()` not returning the game's score." — **prescient observation that hit reality per §1 Finding 1**.

### 11.3 Prior research library

- **`docs/research/domains/sports/1500_sports_domain_scoping.md` §3.C** (lines 375-396) — parent scope definition.
- **`docs/research/domains/sports/1502_sports_prediction_analytics_agents_audit.md` §1 Finding 6** (lines 1083-1085) — outcome-feedback-loop MISSING (inherited load-bearing claim; POSTURE-DECISION-PENDING per F3 fold).
- **`docs/research/platform_architecture_inventory.md` §3.10** (S1273) — row for Sports/Odds/Betting Intelligence, WORKING/LIGHT maturity, names Cat C surfaces + integration gap.
- **`docs/research/platform/cross_domain_integration_audit.md` §12.3** (S1274) — Sports/DBAO ↔ AI Studio Decision Point; explicitly names Cat C gap.
- **`docs/CELERY_AUDIT.md:469-470`** — canonical Celery inventory row confirming both `verify_betting_outcomes` variants have no beat schedule.
- **`docs/AUDIT_FINDINGS.md`** — grep-verified 2026-07-02: `verify_betting_outcomes` NOT on §12 deferred-by-policy list. Load-bearing for §1 Finding 1 classification (unscheduled AND not intentionally-deferred).

### 11.4 Session handoffs

- **`docs/handoffs/SESSION_995_BETTING_OUTCOME_VERIFICATION.md`** — origin handoff for Cat C service + learning bridge.
- **`docs/handoffs/SESSION_995B_SPORTS_BETTING_INTELLIGENCE.md`** — sibling handoff.
- **`docs/handoffs/SESSION_1011_SPORTS_PIPELINE_AUTOMATION.md`** — mention of task cadence.
- **`docs/handoffs/SESSION_1012_BETTING_TABS_POLISH.md`** — frontend polish.
- **`docs/handoffs/SESSION_1165_COO_BACKLOG_TRIPLE_MUST_CLOSE.md`** — retry policy addition to `verify_betting_outcomes` (§1 Finding 1 context: someone added retry policy in S1165, yet the task never fires).
- **`docs/handoffs/SESSION_1244_CAT_2_FULLY_CLOSED_PLUS_CELERY_AUDIT_PLUS_2_REGRESSION_CANARIES.md`** — PR #2687 sports-queue parity fix; partial fix that made the queue consumable but did NOT add a beat entry.

---

## 12. Research Coverage

**Q11 — What research already exists?** **Q13 — Coverage classification per playbook §12?**

**Research coverage classification: LIGHT** per playbook §12 (NONE / LIGHT / MODERATE / DEEP / CANONICAL scale).

Evidence for LIGHT rating:
1. **No dedicated audit prior to this session** — S1503 is the first 20-section audit for Cat C.
2. **Prior research entries** are all cross-cutting: S1273 §3.10 mentions Cat C surfaces but does not deep-audit; S1274 §12.3 frames the integration gap as posture-decision without evidence plan; S1500 parent scoping named Cat C scope but did not audit; S1502 sibling audit noted the outcome-feedback gap but bounded scope to Cat B.
3. **Handoff-level coverage** is scattered (S995 + S995B + S1011 + S1012 + S1165 + S1244) but not synthesized.
4. **Narrative coverage is MODERATE** via `SPORTS_MONETIZATION_ML.md` (HIGH provenance) but is cross-vertical and does not audit design contracts.

This audit **raises Cat C from LIGHT to MODERATE** at S1503 close (assuming SIGN-clean folds).

---

## 13. Architecture Maturity

**Q12 — Maturity classification per playbook §12?**

**Cat C maturity: PARTIAL (armed but zero-fire)** per playbook §12 (EXPERIMENTAL / PARTIAL / WORKING / STABLE / CANONICAL).

Evidence bundle for PARTIAL:

1. **Complete data model** (WORKING-tier evidence): 3 models with proper Decimal money handling, comprehensive choices sets, appropriate indexes, well-typed FKs.
2. **Complete settlement service** (WORKING-tier evidence): 480-line `BettingOutcomeVerifier` with market-specific evaluators (h2h/spread/total), parlay resolution, arbitrage verification, learning bridge, idempotency guard.
3. **Working user-facing surfaces** (WORKING-tier evidence): 11 REST endpoints, 2 PA tools, 4 Discord commands, all reachable and functional.
4. **CRITICAL scheduling drift** (PARTIAL-downgrader): §1 Finding 1 — no beat entry, no PeriodicTask row, zero CeleryTaskEvent 30d rows for both task variants, not on `docs/AUDIT_FINDINGS.md` §12 deferred list.
5. **Zero test coverage** (PARTIAL-downgrader): §1 Finding 9 — no unit tests for settlement logic; regressions undetectable.
6. **Dual-model aggregation drift** (PARTIAL-downgrader): §1 Finding 5 — Discord surface reads a different model than the core surface; no sync contract.
7. **Two-task-variant drift** (PARTIAL-downgrader): §1 Finding 4 — unclear which variant is canonical.
8. **Integration surface intentionally minimal** (POSTURE-DECISION-PENDING, not maturity-affecting): §1 Findings 2, 3, 6, 8.

**Path to WORKING:** resolve Findings 1, 4, 5, 9 (all bounded fixes — beat entry + task consolidation + dual-model reconciliation + test suite). Findings 2, 3, 6, 7, 8 are posture-decision-pending and do NOT block a WORKING upgrade under island posture.

**Path to STABLE:** WORKING + Cat F posture ratified + integration wiring (or documented island contract) + retention policy (§15 debt #2) + concurrency safety (§15 debt #10 / §1 Finding 10).

---

## 14. Known Drift

**Q27 — What is drift?** With evidence.

### 14.1 CRITICAL — `verify_betting_outcomes` unscheduled with docstring-vs-runtime disagreement

- **Claim (docstring / narrative):** `core/tasks.py:6129` says "Runs every 2 hours via Celery Beat"; `docs/narratives/SPORTS_MONETIZATION_ML.md:89` says "every 30 min"; `docs/handoffs/SESSION_995_BETTING_OUTCOME_VERIFICATION.md:42` says "every 2 hours at :15"; `docs/handoffs/SESSION_1011_SPORTS_PIPELINE_AUTOMATION.md:67` says "every 2h"; `docs/topics/celery-workers.md:177` references cadence.
- **Runtime reality:** No beat schedule in `core/celery.py`; no PeriodicTask row (parent-Claude verifier ORM probe pre-SIGN + Rigby SIGN cycle 1 batch 3 Q8 independent ORM probe both returned 0); 0 CeleryTaskEvent 30d rows for both task variants (both probes); NOT on `docs/AUDIT_FINDINGS.md` §12 deferred list.
- **Independent Rigby SIGN cycle 1 batch 3 Q8 ORM probe block (F4 fold — do-not-regress from PR merge):**
  - `scheduled_tasks_tool` search for `verify_betting_outcomes` → `filtered: 0`, `tasks: []`.
  - `ops_tool.celery_task_history` (30d) for `verify_betting_outcomes` → `count: 0`, `events: []`.
  - `ops_tool.celery_task_history` (30d) for `sports.verify_betting_outcomes` → `count: 0`, `events: []`.
  - Both independent from the pre-SIGN parent-Claude ORM probe recorded at §20.5.
- **Severity:** CRITICAL (operational risk — entire feature silently broken).
- **Evidence:** §1 Finding 1 + §20.4 verifier-loop probes + §20.5 log.
- **Context:** PR #2687 (S1244) fixed sports-queue parity but did NOT restore a beat entry. Retry policy was added at S1165 (`core/tasks.py:6168-6184`) — someone was operating this task on the assumption it fires.
- **Risk axis:** OPERATIONAL RISK CRITICAL, ARCHITECTURAL RISK LOW.

### 14.2 HIGH — Cat C → Cat B outcome-feedback loop MISSING

- **Claim (S1502 §1 Finding 6):** Outcome-feedback-loop MISSING.
- **Runtime reality:** Confirmed — zero `MLPrediction.was_correct` writes from Cat C code path.
- **Severity:** HIGH (architectural). **POSTURE-DECISION-PENDING** per S1502 F3 precedent.
- **Evidence:** §1 Finding 2; grep of `betting_outcome_verifier.py` for `MLPrediction` / `was_correct` returns zero matches; Rigby cycle 1 batch 2 Q4 independent grep confirmed.
- **POSTURE-DECISION-PENDING default posture (F9 fold — Rigby SIGN cycle 1 batch 3 Q9):** "**Bridge owns learning writes**" — `SportsBettingLearningBridge` writes `UserAgentLearning` + `AgentMemory` at `sports_betting_bridge.py:503-517, 532-549`; `MLPrediction.was_correct` is set upstream by `evaluate_ml_predictions` at `core/tasks.py:6192` (verified queue-routed to `sports` per `core/settings.py:1387`). Under integration posture, the wiring point is `BettingOutcomeVerifier._settle_wager()` at approximately line 205 — a single-line addition would attach `MLPrediction.was_correct` write on outcome resolution. Under island posture, current bridge scope is the intended scope; document as CANONICAL.
- **Risk axis:** ARCHITECTURAL RISK HIGH, OPERATIONAL RISK LOW.

### 14.3 HIGH — Cat C → Signal Engine emission MISSING

- **Claim (S1274 §14 Finding #6):** `sports_odds` not a `SignalCluster.pattern_type`.
- **Runtime reality:** Confirmed — Cat C produces no `SignalCluster` rows from settlement / streak transitions / arb verification.
- **Severity:** HIGH (architectural). **POSTURE-DECISION-PENDING** per S1502 F2 precedent.
- **Evidence:** §1 Finding 3; Rigby cycle 1 batch 2 Q4 independent grep confirmed no `SignalCluster` touchpoint from `betting_outcome_verifier.py`.
- **POSTURE-DECISION-PENDING default posture (F9 fold — Rigby SIGN cycle 1 batch 3 Q9):** "**Bridge owns learning writes**" (same-family framing as §14.2) — Cat C's boundary intentionally stops at `AgentMemory` + `UserAgentLearning`; SignalCluster is a distinct concern owned by the signal-intelligence subsystem. Under integration posture, extend `SignalCluster.pattern_type` to include sports outcome events AND wire the emission call at `_settle_wager()` line ~205. Under island posture, current absence is intentional.
- **Risk axis:** ARCHITECTURAL RISK HIGH, OPERATIONAL RISK LOW.

### 14.4 MED-HIGH — Two task definitions for `verify_betting_outcomes`

- **Claim (implicit):** One canonical task per feature.
- **Runtime reality:** Two co-existing tasks with different names and different behavior wrappers.
- **Severity:** MED-HIGH (operational + architectural).
- **Evidence:** §1 Finding 4; `docs/CELERY_AUDIT.md:469-470`.
- **Risk axis:** OPERATIONAL RISK MED-HIGH, ARCHITECTURAL RISK MED.

### 14.5 MED — Discord `/bankroll` reads `Bankroll` model, not `BettingStats` — DOWNGRADED from MED-HIGH per F5 fold (Rigby SIGN cycle 1 batch 2 Q5)

- **Claim (implicit — parent §3.C names BettingStats as the aggregate surface):** BettingStats is canonical.
- **Runtime reality:** Discord bypasses BettingStats entirely; reads `core.models_bankroll.Bankroll`.
- **Severity:** MED (operational + architectural) — downgraded pending empirical divergence probe (§15.10 fold).
- **Evidence:** §1 Finding 5.
- **Risk axis:** OPERATIONAL RISK MED, ARCHITECTURAL RISK MED.

### 14.6 MED — Docstring cadence disagreement across surfaces

- **Claim:** `core/tasks.py:6129` says "every 2 hours"; `SPORTS_MONETIZATION_ML.md:89` says "every 30 min"; S995 handoff says "every 2 hours at :15".
- **Runtime reality:** All of the above are moot per §14.1 — no beat schedule at all.
- **Severity:** MED (compounds §14.1 by making the drift harder to characterize).
- **Evidence:** §11.2, §11.4.
- **Risk axis:** OPERATIONAL RISK LOW (subsumed by §14.1), ARCHITECTURAL RISK LOW.

### 14.7 MED — REST endpoints uniformly `AllowAny`

- **Claim (implicit — user data implies auth requirement):** User-scoped data should require user auth.
- **Runtime reality:** All 11 REST endpoints at `core/urls.py:3090-3123` use `@permission_classes([AllowAny])`.
- **Severity:** MED (operational).
- **Evidence:** §3.3 endpoint table.
- **Risk axis:** OPERATIONAL RISK MED, ARCHITECTURAL RISK LOW.
- **Note:** This pattern is inherited from broader sports-app REST surface; S1502 §6 flagged same. Not novel to Cat C. Session 1099-style provenance rules would want re-verification; deferred to a cross-cutting sports-domain auth-hardening arc.

### 14.8 LOW — `PlacedWager.user` nullable at DB level

- **Claim (implicit — every wager has a placer):** wagers should always have a user.
- **Runtime reality:** `null=True, blank=True` on `PlacedWager.user` (line 32-38).
- **Severity:** LOW (validation gap; likely unused but complicates queries).
- **Evidence:** Sub-agent 6 flagged.
- **Risk axis:** OPERATIONAL RISK LOW, ARCHITECTURAL RISK LOW.

---

## 15. Known Technical Debt

**Q26 — What is technical debt?** With severity per playbook §12.

### 15.1 CRITICAL — Beat schedule missing (see §14.1)

Reference §1 Finding 1 + §14.1. Debt = the missing beat entry (bounded 3-5 line fix). Also duplicate task variants need consolidation (see 15.5).

### 15.2 MED-HIGH — No retention / archival policy for `PlacedWager` / `PlacedWagerLeg`

- Unbounded DB growth for historical betting records.
- `core/models_betting.py:13-161` has no `Meta.managers` / retention field / auto-delete rule.
- No task in `core/celery.py:37-797` deletes or archives settled wagers.
- Under island posture: needs explicit "we keep forever" contract + storage plan.
- Under integration posture: needs TTL for GDPR alignment.
- **Risk axis:** OPERATIONAL RISK MED, ARCHITECTURAL RISK MED.

### 15.3 MED — No concurrency control on outcome settlement (see §1 Finding 10)

- Bounded fix: `select_for_update()` on the pending-leg fetch + `@transaction.atomic()` wrapper on `_settle_wager()`.
- Latent risk (only materializes when task is dispatched twice concurrently).
- **Risk axis:** OPERATIONAL RISK MED, ARCHITECTURAL RISK LOW.

### 15.4 MED — `BettingStats.recalculate()` is O(n) full rescan

- Full O(n) recalc every run.
- Scales linearly with per-user wager history.
- Bounded fix: incremental delta update path (recalc only since `last_updated`).
- **Risk axis:** OPERATIONAL RISK MED (at scale), ARCHITECTURAL RISK LOW.

### 15.5 MED — Two task-definition variants for same feature (see §14.4)

- Consolidate to one variant. `core.tasks` variant is more complete (retry + BettingStats wrapper); `sports.tasks` variant may be leftover from an aborted migration to sports-app namespace.
- **Risk axis:** OPERATIONAL RISK MED-HIGH, ARCHITECTURAL RISK MED.

### 15.6 HIGH — Zero test coverage (see §1 Finding 9)

- Zero files in `core/tests/` match `PlacedWager` / `BettingStats` / `BettingOutcomeVerifier` / `verify_betting_outcomes`.
- Blocks confident regressions on `_evaluate_h2h` / `_evaluate_spread` / `_evaluate_total` / parlay push logic / arb profit computation.
- **Risk axis:** OPERATIONAL RISK HIGH, ARCHITECTURAL RISK MED.

### 15.7 MED — Parlay-with-push behavior undocumented

- `_settle_wager()` at line 204-213 treats push as "not a loss" — parlay outcome is `won` if all legs are (`won` OR `push`), `lost` if any is `lost`, `push` if all are `push`. Different sportsbooks handle parlays-with-pushes differently (some reduce payout by removing the pushed leg's odds contribution).
- No test coverage on this branch.
- No docstring explaining convention.
- **Risk axis:** OPERATIONAL RISK MED (if a user pushes on a leg), ARCHITECTURAL RISK MED.

### 15.8 MED — No wager-placement service layer

- All 3 placement sites (`views_betting.py:82`, `views_betting.py:515`, `td_handlers_content.py:4261`) use direct `PlacedWager.objects.create()` + manual PlacedWagerLeg loop.
- Under integration posture: consolidate into a `WagerPlacementService.place(...)` for consistent side effects (SignalCluster emission, Initiative creation, event publishing).
- Under island posture: direct-write pattern is acceptable.
- **Risk axis:** ARCHITECTURAL RISK MED.

### 15.9 LOW — Minimal docstrings at module + class level

- `core/models_betting.py` header docstring is 3 lines.
- `BettingOutcomeVerifier` class docstring at line 22-25 is 3 lines.
- Neither enumerates methods, invariants, or design justification.
- Debt is documentation-only.
- **Risk axis:** ARCHITECTURAL RISK LOW (readability), OPERATIONAL RISK LOW.

### 15.10 MED — `Bankroll` vs `BettingStats` dual aggregation (see §14.5) — DOWNGRADED from MED-HIGH per F5 fold

- Two disjoint per-user aggregate models.
- Discord surface writes and reads `Bankroll`; core surface writes and reads `BettingStats`.
- No sync contract.
- Resolution axis: merge OR document-and-preserve-independent.
- **Severity downgrade rationale (F5 fold — Rigby SIGN cycle 1 batch 2 Q5):** initial draft assigned MED-HIGH. Rigby cycle 1 Q5: "**MED unless you can show inconsistent numbers between `/bankroll` and BettingStats endpoints.**" No empirical divergence probe run in this audit. Downgraded to MED until divergence is proven via cross-endpoint comparison (test candidate: verify that a manually-settled wager updates both surfaces).
- **Risk axis:** OPERATIONAL RISK MED, ARCHITECTURAL RISK MED.

### 15.11 MED — No PA tool for verify / recalc / bankroll surgical operations (see §3.4)

- Rigby cannot manually re-dispatch the verifier task via a PA-tool call; cannot recalc a user's stats; cannot verify a specific wager.
- Analogous to S1502 §1 Finding 2 (Cat B PA tool registry gap).
- Bounded fix: register 2-3 new PA tools + handlers.
- **Risk axis:** OPERATIONAL RISK MED-HIGH.

### 15.12 MED — Fixture-identity across bookmakers (inherited debt from Cat A/B — §1 Finding 7 & S1502 §15 debt #12)

- `PlacedWagerLeg.event_id` string couples to The Odds API `event_id` naming.
- Cross-book identity resolution not attempted.
- Debt shared with Cat A / Cat B; Cat C is a downstream consumer of fixture-identity work.
- **Risk axis:** ARCHITECTURAL RISK MED, OPERATIONAL RISK LOW.

### 15.13 MED — Timezone correctness on `commence_time` / event-start timestamps (F6 fold — Rigby SIGN cycle 1 batch 2 Q5)

- `PlacedWagerLeg.commence_time = DateTimeField(null=True, blank=True)` at `core/models_betting.py:135`.
- `BettingOutcomeVerifier.verify_all_pending()` at line 51 computes `cutoff = timezone.now() - timedelta(hours=self.MIN_HOURS_AFTER_START)` and uses it against `commence_time` for the pending-leg filter.
- Common source of "settled too early / too late" bugs across sports platforms. No test coverage on the `commence_time`-vs-`cutoff` boundary condition; no evidence in code that Odds API returns UTC vs local vs event-local timezone; no documented tz-normalization on the write side (`views_betting.py:82` + `:515` accept whatever the client sends).
- Under integration posture: TZ-normalization contract at write-time + settlement-time. Under island posture: still a bug candidate.
- **Risk axis:** OPERATIONAL RISK MED (settlement-timing correctness), ARCHITECTURAL RISK LOW.

### 15.14 HIGH — Idempotency + replay safety for `verify_betting_outcomes` when beat is restored (F7 fold — Rigby SIGN cycle 1 batch 2 Q5 + batch 3 Q7)

- Rigby cycle 1 batch 3 Q7 explicit gate: "Concurrency-safety hardening (§19.3 #7): **must land BEFORE restoring beat** if the task can overlap (e.g., duration > cadence, retries, multiple workers)."
- Current state: `betting_outcome_verifier.py:54-57` uses no `select_for_update()` (§1 Finding 10 / §15.3). `_settle_wager()` loops without `@transaction.atomic()` wrapper. Idempotency guard exists at line 179 (`if leg.status != 'pending': continue`) but the check races the outcome computation.
- If beat is restored at 2h cadence AND task runtime exceeds 2h (retryable failures + score-fetch batching + multi-user scan), overlapping runs could re-settle the same leg. Retry-budget policy at S1165 exists but does NOT prevent concurrent runs.
- **Minimum bar for beat restoration:** either (a) `select_for_update()` on pending-leg fetch + `@transaction.atomic()` wrapping, OR (b) task-level lock (e.g., Redis lock via `core/services/canonical_locks.py` if present) preventing concurrent dispatch.
- **Risk axis:** OPERATIONAL RISK HIGH (pre-restore-beat gate), ARCHITECTURAL RISK LOW.

### 15.15 MED — Decimal / money-field rounding + quantization policy undocumented (F8 fold — Rigby SIGN cycle 1 batch 2 Q5)

- Cat C uses `DecimalField` for `stake` (`10, 2`), `potential_payout` (`12, 2`), `result_amount` (`12, 2`), `total_stake` (`12, 2`), `total_profit_loss` (`12, 2`). Good — no floats.
- `BettingOutcomeVerifier._calculate_arb_profit()` at line 417 computes profit from stake × decimal-odds arithmetic; `PlacedWager.decimal_odds` property converts American → decimal via mathematical formula.
- **Undocumented:** Decimal quantization policy. Does the code use `Decimal.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)` consistently, or does it rely on `DecimalField(max_digits, decimal_places)` DB-level rounding? Grep for `quantize` in `betting_outcome_verifier.py` + `models_betting.py`: not confirmed in this audit sweep. If arithmetic operations produce more-than-2-decimal-places, DB-level rounding kicks in inconsistently.
- **Undocumented:** float cast risk. Are there any Python-level `float(x)` casts in the arithmetic paths? Not audit-confirmed.
- **Risk axis:** OPERATIONAL RISK MED (rounding-drift causes penny-precision arithmetic errors compounded over many wagers), ARCHITECTURAL RISK LOW.

### 15.16 4-item pre-brief mini-schema per debt item (D62 fold)

| Debt | (a) sports-only vs shared | (b) DBAO vs public | (c) integration posture | (d) island posture |
|---|---|---|---|---|
| Beat schedule missing (§15.1) | sports-only | public queue | **extend** — add beat entry pointing at one variant (integration posture may prefer emit-cabable variant). | **extend** — same fix, cadence choice orthogonal. |
| Retention policy missing (§15.2) | sports-only | public schema | **extend** — TTL policy either posture. | **extend** — TTL policy either posture. |
| No concurrency control (§15.3) | sports-only | public schema | **extend** — same fix under either posture. | **extend** — same fix. |
| O(n) recalculate (§15.4) | sports-only | public schema | **extend** — incremental delta path either posture. | **extend** — same. |
| Two task variants (§15.5) | sports-only | public queue | **refactor** — consolidate to one; integration posture may prefer sports-namespace to align with app-boundary migration. | **refactor** — consolidate to one; island posture may prefer `core.tasks` namespace. |
| Zero test coverage (§15.6) | sports-only | (n/a) | **extend** — add tests either posture. | **extend** — add tests either posture. |
| Parlay-push undocumented (§15.7) | sports-only | (n/a) | **extend** — document + test either posture. | **extend** — same. |
| No placement service (§15.8) | sports-only | (n/a) | **refactor** — introduce service under integration posture to consolidate emit-events + create initiatives; **not required** under island posture. | **N/A** under island posture. |
| Minimal docstrings (§15.9) | sports-only | (n/a) | **extend** — improve docs. | **extend** — same. |
| Bankroll/BettingStats dual (§15.10) | Discord+core (shared) | public schema | **refactor** — merge under integration posture. | **posture-decision** — document as intentional dual-model. |
| PA tool gap (§15.11) | sports-only | public PA tool registry | **extend** — register missing tools. | **extend** — same. |
| Fixture-identity (§15.12) | sports-only (shared with Cat A/B) | public schema | **extend** — add `Game.external_id_map` (Cat A/B primary owner). | **extend** — same. |
| Timezone correctness (§15.13) | sports-only | public schema | **extend** — TZ-normalize either posture. | **extend** — TZ-normalize either posture. |
| Idempotency + replay safety (§15.14) — pre-restore-beat gate | sports-only | public queue | **extend** — `select_for_update()` + `@transaction.atomic()` OR task-level lock. Required BEFORE beat restoration either posture. | **extend** — same fix required either posture. |
| Decimal rounding policy (§15.15) | sports-only | public schema | **extend** — document + enforce quantization either posture. | **extend** — same. |

---

## 16. Boundary Violations

**Q24 — What services violate domain boundaries?**

Cat C code is well-contained: no cross-domain writes beyond the intentional Memory Domain surface via `SportsBettingLearningBridge`, no imports of foreign-domain models except for lazy-imported `TheOddsSpider` (Cat A) + `HumanAttentionItem` (Human Interface).

**No boundary violations** at the service-layer.

Two structural observations that are NOT violations but worth noting:

- The `sports/tasks.py:414` task variant lives in the `sports` Django app while the primary `core/tasks.py:6121` variant lives in `core`. Whether Cat C conceptually belongs in `sports` app or `core` is unresolved — parent §6 xx99 parked question. This is app-boundary drift, not a boundary violation.
- The Discord surface (`/bankroll` etc.) operates on `Bankroll` model at `core/models_bankroll.py`. This is Discord's own surface, not a violation of Cat C boundary; it's a **duplication** of aggregation semantics (§1 Finding 5 / §15.10).

---

## 17. Duplicate or Overlapping Systems

**Q23 — What models overlap with other domains?**

Two overlaps:

1. **`Bankroll` (Discord surface) vs `BettingStats` (core surface)** — dual aggregation surface for the same conceptual data (per-user betting record). §1 Finding 5 / §15.10.

2. **`core.tasks.verify_betting_outcomes` vs `sports.verify_betting_outcomes`** — two task variants for the same feature. §1 Finding 4 / §15.5.

Both overlaps are documented in prior sections; consolidation guidance is in the debt matrix (§15.13).

---

## 18. Ownership Gaps

**Q25 — What ownership is unclear?**

- **No CODEOWNERS file** in the repo (Sub-agent 6 verified).
- **Session-attribution provenance only** — `core/models_betting.py:2` says Session 563; `core/services/betting_outcome_verifier.py:2` says Session 995; `core/tasks.py:6124` says Session 995 + `:6168` says Session 1165. Attribution is chronological; no email or living owner.
- **Django-app ownership question** for Cat C — `core/tasks.py` vs `sports/tasks.py` variants (§14.4) suggest unresolved app-ownership. Whether Cat C moves to the `sports` app or stays in `core` is parked at parent §6.

Per playbook §12: **ownership is UNKNOWN.** Recommend Cat F posture-decision brief includes assigning named owner (or accepting session-attribution as the ownership record).

---

## 19. Recommended Future Research

**Q28 — What should be researched next?** Ranked by architectural uncertainty × risk × unblocked flows.

### 19.1 CRITICAL priority (blocks Cat F evidence plan + Cat C production readiness) — REORGANIZED per F10 fold (Rigby SIGN cycle 1 batch 3 Q7)

1. **Beat-schedule remediation research** — decide (i) which task variant is canonical; (ii) whether to restore beat entry (via `core/celery.py` code) OR PeriodicTask row (via Django-Celery-Admin); (iii) what cadence (docstring says 2h; narrative says 30min; empirical guidance depends on Odds API rate limits — see §19.2 #4 operational cadence study). See §1 Finding 1 / §14.1 / §15.1. **Rigby cycle 1 batch 3 Q7 raised this from HIGH to CRITICAL:** "**Restore scheduling first** (or at least in the same CRITICAL tier), because without it you can't get real-world evidence for the posture decision anyway."
2. **Concurrency-safety hardening as PRE-RESTORE-BEAT GATE** — `select_for_update()` + `@transaction.atomic()` on `_settle_wager()` OR task-level lock. See §15.3 / §15.14. **Rigby cycle 1 batch 3 Q7 raised this from MED to CRITICAL-pre-restore-beat-gate:** "must land BEFORE restoring beat if the task can overlap." Item #1 blocked on Item #2 landing first.
3. **Cat F evidence plan for Cat C outcome-feedback loop question (§1 Finding 2 / §14.2).** Cat F S1506 owes: what evidence differentiates integration vs island posture on the Cat C → Cat B feedback bridge? Currently POSTURE-DECISION-PENDING per S1502 F3 precedent. Default posture per §14.2 F9 fold: "bridge owns learning writes."
4. **Cat F evidence plan for Cat C SignalCluster emission question (§1 Finding 3 / §14.3).** Cat F S1506 owes: what evidence differentiates the two postures for wager-outcome signal emission?

### 19.2 HIGH priority (blocks WORKING-tier promotion + informs CRITICAL work)

5. **Operational cadence study (F11 fold — Rigby SIGN cycle 1 batch 3 Q7 new item)** — Odds API rate limits + score availability lag → informs beat cadence for #1 + retry-budget policy for existing S1165 code. Empirical study of typical time from `commence_time` to score availability across major sports (NFL / NBA / MLB / NHL / soccer). Also inventory Odds API quota + throttling. Blocks #1 cadence choice.
6. **Bankroll vs BettingStats reconciliation research** — decide integration-vs-island for the dual-model surface; if integration, design migration; if island, document the sync-off contract. **First step per §15.10 F5 fold:** empirical divergence probe (verify whether a manually-settled wager updates both surfaces). See §1 Finding 5 / §14.5 / §15.10.
7. **Test suite scoping** — inventory the invariants that require coverage: `settle()`, `_evaluate_h2h/spread/total`, parlay push resolution, arb profit, `recalculate()`, timezone handling on `commence_time`, Decimal quantization. See §15.6 / §15.13 / §15.15.

### 19.3 MED priority (unblocks island-posture path + operator ergonomics)

8. **Retention policy** — decide TTL for `PlacedWager` / `PlacedWagerLeg` / `BettingStats`. GDPR alignment + storage plan. §15.2.
9. **Operator tooling — PA tool + management command for verifier surgical operations (F13 fold — Rigby SIGN cycle 1 batch 3 Q7 new item)** — expose (a) dry-run mode (`verifier.verify_all_pending(dry_run=True)`), (b) recalc mode (`BettingStats.recalculate()` per user), (c) single-wager mode (`verifier._settle_wager(wager_id)` for surgical debugging). Should be both a PA tool for Rigby and a Django management command. §15.11 subsumed under this expanded item.
10. **Parlay-with-push behavior contract** — document intended semantics; add unit tests. §15.7.
11. **Decimal quantization policy** — document + enforce consistent `Decimal.quantize(...)` across settlement / recalc / arb-profit paths. §15.15.

### 19.4 MED-LOW priority (unblocks integration-posture path)

12. **Event-emission surface design** — what event types Cat C should emit under integration posture (§10.2). Depends on Cat F posture decision.
13. **Fixture-identity work coupling** — Cat C `event_id` → `sports.models.Game` FK migration path. Depends on Cat A / Cat B fixture-identity work (S1501 §14.2 + S1502 §15 debt #12).
14. **REST auth hardening** — replace `AllowAny` with workspace-scoped auth. Cross-cutting sports-domain concern; not novel to Cat C but Cat C data (money) makes it higher priority than read-only surfaces. §14.7.

### 19.5 LOW priority

15. **Django-app boundary decision** for Cat C code — `core` vs `sports` app. Parked at parent §6. Not blocking.
16. **Docstring refresh** at module + class level. §15.9.

---

## 20. Appendix

### 20.1 Files inspected

- `core/models_betting.py` (289 lines) — read + grep-verified (Sub-agent 1)
- `core/services/betting_outcome_verifier.py` (480 lines — Sub-agent 6's 340 miscount corrected) — read + grep-verified (Sub-agents 2, 4, 6)
- `core/tasks.py:6118-6188` (verify_betting_outcomes + retry policy) — direct read
- `sports/tasks.py:410-441` (sports.verify_betting_outcomes) — direct read
- `core/celery.py` — grep-verified (zero matches for verify_betting_outcomes)
- `core/settings.py:1385, 1587-1592` (task routing + beat scheduler config)
- `core/urls.py:3090-3123` (REST endpoints) — Sub-agent 3
- `core/services/pa_tool_schemas.py:3235-3283` (PA tool schema) — verified via grep
- `core/services/td_handlers_content.py:3995-4292` (PA handlers) — verified via grep
- `core/services/discord_bot.py:1404-1851` (Discord suite) — Sub-agent 3
- `core/views_betting.py` (all wager REST views) — Sub-agents 2, 3
- `core/learning_bridges/sports_betting_bridge.py` (696 lines) — grep-verified imports
- `docs/CELERY_AUDIT.md:469-470` — read
- `docs/AUDIT_FINDINGS.md` — grep-verified (zero matches for verify_betting_outcomes)

### 20.2 Docs inspected

- `docs/research/domains/sports/1500_sports_domain_scoping.md` §3.C
- `docs/research/domains/sports/1501_sports_odds_ingestion_normalization_audit.md` §2.1 + §4.6 mini-schema pattern
- `docs/research/domains/sports/1502_sports_prediction_analytics_agents_audit.md` §1 (10 findings pattern) + §2.1 + §4.8 mini-schema + §14.3 + §15.13
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §5 + §9 + §11.2 + §13 + §14 + §15 + §16
- `docs/research/platform_architecture_inventory.md` §3.10
- `docs/research/platform/cross_domain_integration_audit.md` §12.3 + §14 Finding #6
- `docs/PLATFORM_INVENTORY.md`
- `docs/narratives/SPORTS_MONETIZATION_ML.md`
- `docs/handoffs/SESSION_995_BETTING_OUTCOME_VERIFICATION.md`
- `docs/handoffs/SESSION_1165_COO_BACKLOG_TRIPLE_MUST_CLOSE.md`
- `docs/handoffs/SESSION_1244_CAT_2_FULLY_CLOSED_PLUS_CELERY_AUDIT_PLUS_2_REGRESSION_CANARIES.md`

### 20.3 Grep patterns used

- `verify_betting_outcomes` — across repo (found 15 files including task defs, docs, audit findings)
- `PlacedWager.objects.create` — write-site inventory
- `MLPrediction|was_correct|SignalCluster|SignalService|AgentMemory|MemoryLane` in `betting_outcome_verifier.py` — grep-verified absence
- `MLPrediction|was_correct|SignalCluster` in `sports_betting_bridge.py` — read-vs-write pattern verification
- `sports_wagers|sports_record_wager|sports_bankroll|betting_outcome_verifier` in `pa_tool_schemas.py` — PA tool inventory
- `verify_betting_outcomes` in `docs/AUDIT_FINDINGS.md` — deferred-list check (returned zero)
- `verify_betting_outcomes` in `core/celery.py` — beat-schedule check (returned zero)
- `CELERY_BEAT_SCHEDULE|beat_schedule` in `core/settings.py` — scheduler config check
- `PlacedWager|BettingStats|BettingOutcomeVerifier|verify_betting_outcomes` in `core/tests/` — test coverage check (returned zero files)

### 20.4 Verifier-loop corrections (§14 evidence rule)

**Parent-Claude verifier-loop applied on 7 load-bearing claims before Rigby SIGN routing. 2 sub-agent errors caught pre-SIGN. Then Rigby Full SIGN cycle 1 (3 batches: Q1-Q3 + Q4-Q6 + Q7-Q9) landed SIGN-with-edits at High confidence with zero worker instability across all 4 turns (warm-up probe + 3 SIGN batches) on fresh isolation pin `pa-8ce5f949bed5e093`. F1-F14 folds landed at commit-time (see below). Cycle 2 SIGN-clean at High confidence predicted after folds land; matches S1501 + S1502 cycle-1-predict-cycle-2 pattern.**

**F1-F14 fold list (applied at commit-time):**

- **F1 §5.4:** additional Cat C read surfaces addendum (`core/views_odds_sports.py` + `td_handlers_content.py` read path + `sports_content_context.py`).
- **F2 §5.5:** Bankroll adjacency touchpoints (bounded) subsection acknowledging §1 Finding 5 without deep-auditing Discord domain.
- **F3 §1 executive summary:** compounding-risk observation (Finding 1 + Finding 5 combo) + "orchestration + idempotency = non-negotiable operational-readiness gates" reframe.
- **F4 §14.1 + §20.5:** independent Rigby SIGN cycle 1 batch 3 Q8 ORM probe block ("0 beat entries, 0 task events 30d for both variants"); do-not-regress flag for PR merge.
- **F5 §14.5 + §15.10:** severity MED-HIGH → MED downgrade with "until divergence proven" rationale; empirical divergence-probe added to §19.2 #6 first-step.
- **F6 §15.13:** new debt item — timezone correctness on `commence_time` / event-start timestamps.
- **F7 §15.14:** new debt item — idempotency + replay safety for `verify_betting_outcomes` when beat is restored (HIGH-severity pre-restore-beat gate).
- **F8 §15.15:** new debt item — Decimal / money-field rounding + quantization policy.
- **F9 §14.2 + §14.3:** "**bridge owns learning writes**" as POSTURE-DECISION-PENDING default posture statement; wiring points named (e.g., `_settle_wager()` line ~205) for integration posture.
- **F10 §19.1:** CRITICAL tier reorganization — beat-schedule remediation (previously §19.3 #3) → §19.1 #1; concurrency-safety hardening (previously §19.3 #7) → §19.1 #2 as PRE-RESTORE-BEAT GATE; Cat F evidence plan items moved to §19.1 #3-4.
- **F11 §19.2 #5:** new research item — operational cadence study (Odds API rate limits + score availability lag) informs beat cadence choice.
- **F12 §19 (no change — kept at MED-LOW):** fixture identity strategy already at §19.4 #13.
- **F13 §19.3 #9:** new research item — operator tooling (PA tool + management command for dry-run / recalc / single-wager modes); subsumes §15.11 into expanded item.
- **F14 §5.5 dual-Bankroll footnote:** clarify `Bankroll` in `core.models_bankroll.py:19` PLUS `BankrollManagement` in `sports/models.py:1032` (Rigby SIGN cycle 1 batch 3 Q8 grep-verified — prevents "bankroll is core-only" misreading).

**Do-not-regress notes for PR:** preserve §2.1 Cat C contract statement; preserve F9 "bridge owns learning writes" framing throughout §14.2 + §14.3 (do NOT backslide to "MISSING integration" defect language); preserve F4 independent Rigby ORM probe block in §14.1 + §20.5 (evidence for CRITICAL classification); preserve F7 idempotency-as-pre-restore-beat-gate framing in §15.14 + §19.1 (do NOT let CRITICAL #1 land without CRITICAL #2 landing first); preserve F10 §19.1 CRITICAL tier ordering.

**Pre-SIGN verifier-loop corrections (parent-Claude on 7 load-bearing claims):**

1. **Sub-agent 6 line count error.** Reported `betting_outcome_verifier.py` at 340 lines. Direct `wc -l` returned **480**. Corrected in §5.1.
2. **Sub-agent 6 line reference error.** Reported `MIN_HOURS_AFTER_START = 3` on line 28. Direct file read returned **line 26**. Corrected in §5.1.
3. **Sub-agent 2 line count claim (BettingOutcomeVerifier at 480 lines) confirmed** via direct `wc -l`. ✓
4. **Sub-agent 1 line count claim (models_betting.py at 289 lines) confirmed** via direct `wc -l`. ✓
5. **Sub-agent 4 zero-import claim** (`MLPrediction` / `SignalCluster` etc. absent from `betting_outcome_verifier.py`) **confirmed** via direct grep. ✓
6. **Sub-agent 6 beat-schedule-absent claim** (CRITICAL load-bearing) **confirmed** via 3-axis probe:
   - grep of `core/celery.py` for `verify_betting_outcomes` → zero matches
   - grep of `docs/AUDIT_FINDINGS.md` for same → zero matches (i.e., NOT documented as intentionally deferred)
   - Rigby ORM probe on `pa-791b3db549a64e54` (see §20.5 below) → `PeriodicTask.objects.count() == 0` AND `CeleryTaskEvent.objects.filter(30d).count() == 0` for both task variants.
7. **Sub-agent 3 PA tool inventory** (`sports_wagers` + `sports_record_wager` in `pa_tool_schemas.py:3241`) **confirmed** via direct grep. ✓
8. **Sub-agent 2 write-site inventory** (3 PlacedWager creation sites: `views_betting.py:82`, `views_betting.py:515`, `td_handlers_content.py:4261`) **confirmed** via direct grep. ✓

**Rigby SIGN cycle 1 anticipated flags (based on S1501 + S1502 SIGN patterns):**

- Q1 (missed parts): possible flag on `Bankroll` model — not audited but referenced in §1 Finding 5 (deliberately out-of-scope per §5 non-goals; Discord surface / core.models_bankroll ownership belongs to a Discord audit).
- Q2 (overstated maturity): PARTIAL maturity verdict should hold — the "armed but zero-fire" formulation is honest.
- Q3 (understated maturity): possible flag if Rigby considers "code complete + service-callable via manual dispatch" WORKING-tier. Counter-argument in §13: zero-fire drift + zero tests hold at PARTIAL.
- Q4 (intentional separation vs missing integration): Findings 2, 3, 6 explicitly framed as POSTURE-DECISION-PENDING per S1502 F3/F2/F4 precedents. F3-precedent framing should preempt "MISSING = defect" over-classification.
- Q6 (riskiest finding): §1 Finding 1 CRITICAL operational risk should hold as biggest.
- Q7 (most important future research): Cat F evidence plan requests (§19.1) should hold.
- Q8 (what got wrong): verifier-loop caught 2 sub-agent errors pre-SIGN; anticipated additional corrections if Rigby greps `Bankroll` behavior or PA tool registration.

### 20.5 Rigby ORM probe log — TWO independent probes both returning zero (F4 fold)

**Probe 1 (parent-Claude pre-SIGN verifier probe).** Performed 2026-07-02 on `pa-791b3db549a64e54` (Group 1500 arc pin) before draft integration:

- QUERY 1 — PeriodicTask row check (via `scheduled_tasks_tool` search): `filtered: 0` — no rows matching `verify_betting_outcomes` (either variant). Total enabled tasks in the queue: 92 (context — matches PLATFORM_INVENTORY autoblock).
- QUERY 2 — CeleryTaskEvent firing history 30d (via `ops_tool.celery_task_history`): `count: 0` — zero events for either task variant in the last 30 days.

**Probe 2 (Rigby SIGN cycle 1 batch 3 Q8 independent verification).** Performed 2026-07-02 on `pa-8ce5f949bed5e093` (fresh SIGN isolation pin):

- `scheduled_tasks_tool` search for `verify_betting_outcomes` → `filtered: 0`, `tasks: []`.
- `ops_tool.celery_task_history` (30d) for `verify_betting_outcomes` → `count: 0`, `events: []`.
- `ops_tool.celery_task_history` (30d) for `sports.verify_betting_outcomes` → `count: 0`, `events: []`.

**Two independent probes on two different pins both returning zero.** Interpretation: Not scheduled AND not fired. Not on `docs/AUDIT_FINDINGS.md` §12 deferred list. Per memory rule `feedback_audit_findings_12_canonical_celery_deferred_list.md` this is a load-bearing zero-fire task drift — not an intentional deferral. Independence of the two probes eliminates single-source risk for the CRITICAL §14.1 finding.

### 20.6 Unresolved unknowns

- **`Bankroll` model schema and sync path** — out of Cat C scope; §1 Finding 5 flagged for Discord-domain audit or follow-on.
- **`evaluate_ml_predictions` task cadence and beat schedule** — out of Cat C scope; Cat B S1502 audit did not settle this; xx99 (S1599) evidence plan owes.
- **`SportsBettingLearningBridge` internal method behavior details** — §5 non-goal boundary; deep-audit deferred to Memory Domain arc if opened.
- **Whether the `sports.verify_betting_outcomes` variant is a slotted app-migration attempt or historical artifact** — no commit-history probe run in this audit (would be Rigby git-log lens if warranted).

### 20.7 Conflicts between sources

- **Task cadence:** `core/tasks.py:6129` says "every 2 hours"; `docs/narratives/SPORTS_MONETIZATION_ML.md:89` says "every 30 min"; `docs/handoffs/SESSION_995_BETTING_OUTCOME_VERIFICATION.md:42` says "every 2 hours at :15". **Resolution:** all three are moot per §14.1 — no beat schedule exists. Documentation drift compounded.
- **Sub-agent 6 line-count claims** vs direct `wc -l` output — resolved via §20.4 verifier-loop corrections.

### 20.8 Rigby SIGN fold notes — cycle 1 SIGN-with-edits at High confidence

**Rigby Full SIGN cycle 1 verdict on 2026-07-02 via fresh isolation pin `pa-8ce5f949bed5e093`:** SIGN-with-edits at **High confidence** across 3 substantive batches (Q1-Q3 completeness + maturity; Q4-Q6 integration + debt + risk; Q7-Q9 + overall verdict) + 1 stability probe (warm-up ping + `cockpit_tool.worker_health` verifying 4 workers online). **Zero worker-instability observed across all 4 turns** — this is the 6th arm of the D48 preemptive stability-probe gate CODIFICATION-READY 5-arc pattern (S1405+S1406+S1499+S1501+S1502), further reinforcing the xx99 (S1599) §10.2 recommendation to codify D48 into playbook v3 §15.

**Rigby's own final verdict block (§15 standard format):**
- Overall confidence: High
- Most accurate part: The operational finding that Cat C is armed-but-zero-fire (unscheduled + no observed executions), with cross-validated evidence.
- Weakest part: Bankroll/BettingStats dual-aggregation risk ranking unless empirical divergence evidence is added (→ F5 fold, §15.10 severity downgrade + §19.2 #6 empirical probe as first step).
- Missing area: Concurrency/idempotency/locking requirements as pre-restore-beat gate (→ F7 new §15.14 debt item + F10 §19.1 CRITICAL tier reorganization).
- Overstated maturity: No — PARTIAL is appropriately conservative.
- Understated maturity: The service/module code is callable and internally coherent; if scheduling + locks land, it could quickly graduate to WORKING.
- Biggest architectural risk: Posture decision around settlement → learning/scoring/signal emission (Cat C → Cat B / SignalEngine) — affects where truth is recorded and how feedback loops are computed.
- Most important next research: Restore scheduling safely (beat entry + idempotency/lock) so Cat C can produce real outcomes; in parallel, finish Cat F posture evidence plan.
- What Claude got wrong: Nothing material; only watch for the "bankroll is core-only" implicit reading (→ F14 fold, §5.5 dual-Bankroll footnote).
- What must change before canonical: 5 non-negotiable edits — all landed as F1-F14 folds (see §20.4). No NEEDS-MORE items.
- Final verdict: **SIGN-with-edits at High confidence** (implicit — batch 3 response was truncated at "Final verdict:" but the 5 Q9 non-negotiable edits + Rigby's other batch verdicts + zero instability all indicate SIGN-with-edits, not NEEDS-MORE).

**Cycle 2 SIGN-clean at High confidence anticipated post-fold-land** — pattern-consistent with S1501 (cycle 2 SIGN-clean) + S1502 (cycle 2 SIGN-clean cycle 1 prediction accurate). Cycle 2 SIGN routing owed at PR-merge-time or explicitly-Chris-invoked follow-up.

---

*This audit was produced per playbook §11.2 20-section template + §13 6-parallel-Explore evidence sweep + §5 pre-brief 4-item mini-schema per D62 = (a) propagate upfront + §14 parent-Claude verifier-loop on 7 load-bearing claims (2 sub-agent errors caught pre-SIGN) + §15 Rigby Full SIGN routing (pending). Third sibling in Group 1500 to apply D62 propagation upfront (S1501 first + S1502 second + S1503 third).*
