---
title: "S1405 Revenue — Category E: Revenue Attribution + Analytics (Child audit under Group 1400 Revenue arc)"
status: draft
authority: research
category: child_audit
session: 1405
date: 2026-07-01
parent_arc: 1400_revenue_domain_scoping
arc_slot: P5 (fifth child; consumes S1401 §9 + S1402 §9/§14 + S1403 §9/§14 + S1404 §9/§14 outputs at Meeting/Close → Attribution seam)
domain_slug: revenue
subdomain_slug: revenue_attribution_analytics
research_group: 1400
authors: Claude Code (Chris directed via short command "start research group 1405 Child E")
supersedes: none
depends_on:
  - docs/research/domains/revenue/1400_revenue_domain_scoping.md          # parent §3.E + §11.4 + §12.1 (Category E F.iii)
  - docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md   # §9 integration map (Cat A → E read seam)
  - docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md   # §9 integration map + F.B4 cadence-declared-not-realized methodology
  - docs/research/domains/revenue/1403_revenue_engagement_inbound_audit.md              # §9 integration map + F.C6 run_ops_autopilot deferred-by-policy
  - docs/research/domains/revenue/1404_revenue_meeting_close_audit.md                   # §9 integration map + F.D4 arc-wide HAI missing + F.D10 state-machine PARTIAL + §20.10 anchor-corrections pattern
  - docs/research/platform/cross_domain_integration_audit.md                # S1274 §2.4 line 292 STRONG (Revenue → Observability) + §4.3 (revenue_attribution_bridge) + §14 finding #36 (no runtime owner HIGH)
  - docs/research/platform_architecture_inventory.md                        # S1273 §3.32 + §4.9 + §10.3 UNKNOWN attribution algorithm
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                               # process (§11.2 20-section template + §13 6-parallel-Explore sweep + §14 evidence rules + §15 full-SIGN + §20.10 anchor-corrections)
  - docs/AUDIT_FINDINGS.md                                                  # §12 canonical Celery deferred-by-policy list
sign_status: SIGN-with-edits (cycle 1 partial — batch 1 substantive pressure-test on F.E1-F.E3 delivered; batches 2-3 blocked by Rigby SIGN worker instability, deferred to follow-up SIGN addendum per D45 Chris ratification 2026-07-01); F.E3 framing refinement folded at commit-time (see §14.3 + §17 "possible intentional dual-schema" note); F.E2 flagged MUST-FIX before canonical per Rigby cycle 1 Batch 1 pressure-test
decisions_ratified_at_session_open: D41 sequential + D42 arc pin retain + D43 T.C8 minimal-blocking (all "agree all" 2026-07-01)
decisions_ratified_mid_session: D44 SIGN retry cadence — (iii) stripped-down then (i) batched; D45 SIGN partial acceptance — (ii) accept batch 1 substantive pressure-test as SIGN-with-edits cycle 1 verdict; batches 2-3 deferred to follow-up (both "agree all" 2026-07-01)
---

# Session 1405 — Category E Revenue Attribution + Analytics Audit

> **Scope.** This is the fifth Group 1400 Revenue child audit. It
> covers the Revenue Attribution + Analytics surface per parent §3.E
> + parent §12.1 Category E F.iii questions. Per playbook §14 evidence
> rules, all claims cite `file:line` from `main` at `2355f5be` (S1404
> audit + cascade PRs #2793 + #2794 merged; S1405 branches off `main`).
>
> **What this doc is not.** An implementation plan for the missing
> pieces surfaced. F.E-scale ADRs land as post-arc design-preparation
> deliverables per playbook §17 + inherit S1403 R.C1 + S1404 R.D6
> sequential-ADR pair-design discipline (F.B1 delivery ADR → F.C1
> ingestion ADR → F.D6 HAI interlock ADR → F.E5 view-file
> consolidation ADR chain).
>
> **Load-bearing S1404 inheritance at this audit's open.** F.D1
> (runtime empty locally: Meeting=0, ClosePack=0, EngagementEvent=0)
> + F.D3 (ClosePack MANUAL trigger only) + F.D4 (arc-wide HAI writers
> missing empirically) + F.D10 (ClosePack state machine PARTIAL —
> `sent`/`won`/`lost` unreachable). Category E extends F.D10 lens to
> `OpportunityRevenue` + `OpportunityOutcome`; refines F.D4 with
> code-layer HAI writer discovery in `ops_autopilot/core.py`.

---

## 1. Executive Summary

Category E covers Revenue Attribution + Analytics — the final seam of
the Group 1400 mainline pipeline where Meeting/ClosePack outcomes
convert to tracked revenue rows, attribution credit is allocated
across upstream agents/desks, and the whole pipeline surfaces to
frontend dashboards + governance HumanAttention items.

**Maturity verdict.** Four-way split extending S1403's four-way
pattern: **WORKING (attribution algorithm in `impact.py` +
`revenue_attribution_bridge` signal) / MISSING (unified revenue write
path: 2 parallel bridges + 2 core models + 1 intelligence-side
`RevenueRecord` never converged) / DEFERRED-BY-POLICY (ops_autopilot
revenue policies gated behind dormant `run_ops_autopilot` beat per
F.C6) / DORMANT LOCAL RUNTIME (revenue tables empty locally per
F.D1 extension)**.

**Load-bearing findings (10 F.E findings; 6 CONFIRMED HIGH, 3
CONFIRMED MEDIUM, 1 CONFIRMED PARENT-DOC DRIFT ×2 anchor corrections):**

- **F.E1 (CONFIRMED HIGH — arc-wide extension of S1404 F.D10):**
  Over-modeled STATUS_CHOICES pattern now confirmed across
  **3 revenue-domain models** (arc-wide). `OpportunityRevenue`
  declares 5 states (`pending`/`received`/`partial`/`cancelled`/
  `refunded`), only `'received'` reachable — 4 of 5 UNREACHABLE
  at `core/models_unified_system.py:2621-2627`.
  `OpportunityOutcome` declares 5 states (`won`/`lost`/`expired`/
  `cancelled`/`partial`), only `won` + `lost` reachable — 3 of 5
  UNREACHABLE at `:3405-3407`. Pattern paired with ClosePack
  (S1404 F.D10): 3-model arc-wide over-modeling pattern.

- **F.E2 (CONFIRMED HIGH — new class of drift, worse than S1399 F1):**
  **Phantom field references** — 4 code sites reference schema
  fields that DON'T EXIST on the target model, would raise
  `FieldError`/`TypeError`/`AttributeError` at runtime:
  (a) `ml_scoring_engine.py:1240-1242` filters `OpportunityOutcome.
  recorded_at` (schema has `created_at` only); (b) `event_handlers.
  py:290-292` filters `OpportunityOutcome.actual_outcome` (schema has
  `outcome` only); (c) `epa_handlers_tools.py:3583-3593` passes
  `notes=` kwarg to `OpportunityRevenue.objects.create()` (schema
  field is `description`); (d) `epa_handlers_tools.py:3727-3730` +
  `revenue_attribution_bridge.py:102-104` reference `revenue.metadata`
  attribute (no such field). Runtime blast radius LOW-TO-ZERO
  currently because Revenue tables are empty locally (F.D1 pattern
  extension); latent bugs waiting for first real invocation.

- **F.E3 (CONFIRMED HIGH — dual-representation drift extends S1401 D6
  to Revenue domain; Rigby cycle 1 Batch 1 framing refinement folded):**
  Two revenue pipelines with a documented integration gap. Core has
  `OpportunityRevenue` (`:2613`) + `OpportunityOutcome` (`:3394`);
  `intelligence/` has parallel `RevenueRecord`
  (`intelligence/revenue_tracking_bridge.py:29`) + `RevenueSource`
  (`:16`) + `ProposalTracker` (`:57`) + `RevenueDashboardMetrics`
  (`:83`). `revenue_attribution_bridge.py:227` post_save signal fires
  on core `Revenue` — NOT on `RevenueRecord`. Intelligence-side
  revenue never triggers `UserAgentLearning` updates. **Rigby cycle 1
  Batch 1 framing refinement:** the dual-schema pattern MAY be
  intentional (core = finalized accounting truth; intelligence-side =
  external attribution ingestion / analytics shadow). If intentional,
  the gap reframes from "missing integration" to **"missing explicit
  contract + mapping + source-of-truth hierarchy"** — remediation ADR
  scope shifts accordingly. Load-bearing observation either way: **no
  declared source-of-truth hierarchy across the parallel schemas** →
  silent analytic inconsistency risk. Which framing is correct is a
  Chris/Rigby architectural decision at post-arc design-preparation
  phase.

- **F.E4 (CONFIRMED — PARENT-DOC ANCHOR CORRECTION #1):** Parent §3.E
  named 4 frontend routes (`/revenue`, `/revenue-dashboard`,
  `/revenue-opportunities`, `/opportunity-detail`) that **DO NOT
  EXIST** in `frontend/src/App.tsx` (grep: 0 matches). Revenue features
  are surfaced via `/analytics` + `/intelligence` routes. Landing
  parent-doc correction at commit-time per S1404 §20.10 pattern.

- **F.E5 (CONFIRMED HIGH — 3-view-file overlap analysis, answers Q3):**
  `views_revenue.py` + `views_revenue_tracking.py` provide **DUPLICATE
  endpoint pairs**: POST `/api/revenue/create/` vs POST
  `/api/v1/revenue/track/` (both create; different models + response
  formats); GET `/api/revenue/summary/` vs GET `/api/v1/revenue/stats/`
  (both aggregate; different granularities). `views_revenue_analytics.
  py` is architecturally distinct (7 endpoints: platform distribution +
  forecasting + ROI + goals + export). `views_revenue_tracking.py`
  has ZERO docstrings on all 4 class-based views + calls a MISSING
  `Revenue.get_user_total()` method (unresolved external reference).

- **F.E6 (CONFIRMED — PARENT-DOC ANCHOR CORRECTION #2):** Parent §3.E
  + §12.1 named `ops_autopilot/revenue.py` as the location of the
  "revenue attribution algorithm." **Actual algorithm is at
  `core/services/ops_autopilot/impact.py:1233-1290`
  (`MultiTouchAttributor._attribute_event`)** — 70% last-touch +
  30% assist split (evenly among upstream via `trace_id`,
  `deliverable→initiative/dream`, `agent_chain`). Writes to
  `ImpactCredit` at `core/models_impact_credit.py`. `ops_autopilot/
  revenue.py` contains pipeline forecasting classes only
  (`RevenuePipelineAutomator`, `OutboundLeadEngine`,
  `OutreachSequencer`, `CloseTheDealEngine`, `RevenueOrchestrator`,
  `ClosePackAutonomyEngine`). Landing parent-doc correction at
  commit-time per §20.10 pattern.

- **F.E7 (F.D4 REFINEMENT — code-exists-but-dormant, arc-wide):**
  S1404 F.D4 said "zero Revenue-domain HAI writers arc-wide"
  based on empirical HAI table probe (2 of 3061 rows from
  ops_autopilot only). S1405 refines at CODE LAYER: HAI writers
  DO EXIST at **6 sites in `core/services/ops_autopilot/core.py`**
  (`:1561` impact_portfolio; `:1673` attribution_debt; `:2051`
  revenue_pipeline critical_stale; `:2117` outbound_leads
  high-value; `:2237` release_governor; `:2361` policy_arbitrator).
  Runtime dormancy is via F.C6 (`run_ops_autopilot` deferred per
  AUDIT_FINDINGS.md #12), not code absence. **F.D4 refined:
  CODE-LAYER WRITER-EXISTS at 6 sites; RUNTIME-LAYER DORMANT via
  F.C6.** S1499 xx99 synthesis inherits this refinement.

- **F.E8 (CONFIRMED — Q2 answer, S1274 §2.4 STRONG verified):**
  Revenue → Observability STRONG classification verified with
  mechanism. Emitter chain: `ImpactCollector` (`impact.py:238-505`)
  writes `ImpactEvent` from Wager (`:375`), DeliverableEvent
  (`:431`), Revenue (`:488`) sources → `ImpactEvent` at
  `core/models_impact_events.py:21-120` → 6+ readers
  (`PortfolioAllocator.compute_desk_iqroi` at `:582`,
  `MultiTouchAttributor.attribute_recent` at `:1209`,
  `ROIEnforcer` at `budget.py:644`, `ExperimentEngine` at
  `experiment.py:641`) → attribution report at
  `MultiTouchAttributor.get_attribution_report:1457` → HAI in
  `_policy_attribution_debt` (F.E7 :1673).

- **F.E9 (CONFIRMED — S1274 §4.3 verified with 2-path mechanism):**
  `revenue_attribution_bridge.py:227` @receiver(post_save,
  sender=Revenue) fires on core `Revenue` create/completed. Writes
  `UserAgentLearning` via **2 paths**: (1) `_update_agent_learning`
  at `:147-170` with `learning_domain='revenue_optimization'`;
  (2) `_update_user_revenue_patterns` at `:181-210` with
  `learning_domain='success_factors'`. Docstring claim "Feeds
  insights to UnifiedLearningPipeline" is CANDIDATE drift —
  `_generate_insights:122-140` returns strings but never
  dispatches to a pipeline.

- **F.E10 (CONFIRMED HIGH — S1274 §14 finding #36 answer, Q4):**
  **Revenue pipeline runtime owner is ABSENT arc-wide.** Zero
  JobContract in `core/employees/jobs.py` (only docstring context
  mentions); zero AGENT_MAP entries in `core/agent_router.py`;
  zero task_routes assignment in `core/settings.py`; no dedicated
  Celery queue (`calculate_daily_revenue_metrics` uses `'default'`
  queue at `core/celery.py:620`). Only ownership signal: PA tool
  `revenue_tracker_tool` at `core/services/pa_tool_schemas.py:188-208`
  routing to `intelligence_enricher` + `proactive_intelligence`
  queues (workspace-scoped, not a JobContract). Cat E owns
  arc-wide ownership synthesis per parent D28 lock — this is
  the primary Cat E deliverable inherited from S1274 §14 #36 HIGH.

**Arc-wide implications for S1499 xx99 synthesis.** With Categories
A/B/C/D/E now converged, the arc trajectory statement from S1404
§20.11 gains a fifth pillar: **(v) attribution + analytics is
STRONG at ImpactEvent → ImpactCredit level but MISSING at core
Revenue schema wire-up level; dual-representation drift persists;
runtime owner absent.** S1499 remediation plan candidates:
(a) activate the revenue lifecycle via F.B1 → F.C1 → F.D6 → F.E5
sequential ADR chain; (b) enforce approval/attention gating via
F.E7 refinement (enable `run_ops_autopilot` behind explicit
green-light + attribution-debt threshold gate); (c) assign
runtime owner via Revenue Employee JobContract (F.E10); (d) close
phantom-field bugs via F.E2 fix arc (4-site cleanup, low-effort).

**Anchor corrections landing at S1405 commit-time** per S1404
§20.10 pattern: **F.E4 parent §3.E frontend routes → replace with
`/analytics` + `/intelligence` actual routes;** **F.E6 parent §3.E
+ §12.1 attribution algorithm location → replace `ops_autopilot/
revenue.py` with `ops_autopilot/impact.py::MultiTouchAttributor`.**

## 2. Domain Purpose

Category E (Revenue Attribution + Analytics) exists to answer four
questions for downstream consumers:

1. **How much revenue did we actually earn?** Per user, per
   platform, per opportunity, per time window. Answered by
   `OpportunityRevenue` (`models_unified_system.py:2613`) as the
   core schema + `views_revenue_analytics.py` as the primary
   read surface.

2. **Which upstream work drove which revenue?** Per agent, per
   desk, per orchestration trace. Answered by `ImpactEvent`
   (`models_impact_events.py`) + `MultiTouchAttributor`
   (`impact.py:1163-1480`) + `ImpactCredit`
   (`models_impact_credit.py`) writing credit shares (70%
   last-touch + 30% assist evenly split).

3. **What outcomes did the pipeline produce?** Won/lost/expired
   deals per opportunity, with revenue-variance + loss-reason +
   lessons-learned for downstream learning. Answered by
   `OpportunityOutcome` (`models_unified_system.py:3394`), written
   only via `OpportunityTask.mark_won:3166` + `.mark_lost:3199`.

4. **What did we learn that improves scoring?**
   `revenue_attribution_bridge.py:227` post_save signal on core
   `Revenue` → `UserAgentLearning` writes at `:147` + `:181`
   under two `learning_domain` axes.

The domain is **downstream of all four prior Group 1400 categories**:
Category A produces opportunities, B composes outreach, C receives
engagement, D creates meetings + closes, E tracks resulting revenue
+ allocates attribution + surfaces analytics. It is also **upstream
of the Observability domain** (S1274 §2.4 STRONG classification via
`ImpactEvent`) + **upstream of the Learning domain** (via
`revenue_attribution_bridge`).

**What Category E is not.** It is not the payment-processing seam
(that's platform-integration domain — Stripe/PayPal/etc.). It is
not the deal-flow orchestration seam (that's Category B/C/D). It
is not the frontend rendering layer (that's the presentation
domain — although 3 view files + reachable frontend routes
`/analytics` + `/intelligence` live in the same repo).

## 3. Canonical Entry Points

Category E has three canonical entry-point classes: **write entries**
(where revenue rows get created), **attribution entries** (where
credit gets allocated), and **read entries** (where downstream
consumers query attribution/analytics).

### 3.1 Write entries — where OpportunityRevenue rows are created

Two write sites confirmed at direct read:

1. **`core/views_opportunity.py:770-815`** — POST handler for
   `/api/opportunities/{opp_id}/revenue/`. Manually invoked via
   frontend/API. Instantiates `OpportunityRevenue(...)` at `:780`,
   calls `.save()` at `:815`. Fields set: opportunity, user, amount,
   currency, platform_fee (default 0), content_type, platform,
   description, sale_date, external_reference, image_history
   (optional FK), video_history (optional FK), estimated_revenue.
   Status field NOT explicitly set → defaults to `'received'` per
   model at `:2688`. Side effect: `.save()` override at
   `:2767-2802` updates related `Opportunity.status='earning'`
   at `:2783-2785`.

2. **`core/epa_handlers_tools.py:3583`** — `_handle_revenue_tracker_tool`
   agent tool action `log_revenue`. Called via PA function-calling
   loop when Rigby dispatches `revenue_tracker_tool` with
   `action='log_revenue'`. `OpportunityRevenue.objects.create(...)`
   at `:3583`. Status field NOT explicitly set → defaults to
   `'received'`. **F.E2 phantom field bug**: passes `notes=` kwarg
   at `:3592` but schema field is `description` — would raise
   `TypeError: OpportunityRevenue() got unexpected keyword argument
   'notes'` at first invocation. Side effect: sets
   `opp.status='accepted'` at `:3596-3597`.

Parallel intelligence-side write (F.E3 dual-representation):

3. **`intelligence/revenue_tracking_bridge.py:131`** —
   `RevenueTrackingBridge.record_revenue()` writes `RevenueRecord`
   (a parallel schema, NOT `OpportunityRevenue`). Only caller:
   `intelligence/real_execution_engine.py:106` in
   `_execute_job_applications()` — conditional on
   `apply_to_jobs` execution type.

### 3.2 Attribution entries — where ImpactEvent + ImpactCredit rows are created

1. **`core/services/ops_autopilot/impact.py:238-505`** —
   `ImpactCollector` class harvests impact events into
   `ImpactEvent` rows:
   - `_collect_wager_impacts(window_start):345-393` → writes
     `ImpactEvent(impact_type='wager_profit', desk='sports')` at
     `:375`.
   - `_collect_deliverable_impacts(window_start):395-453` → writes
     content_save/export/share/action → `ImpactEvent(desk='content')`
     at `:431`.
   - `_collect_revenue_impacts(window_start):455-504` → writes
     `Revenue` → `ImpactEvent(impact_type='revenue_confirmed',
     desk=mapped)` at `:488`.
   - `collect_all(now, window_hours=24):263-300` — driver method,
     idempotent dedup on `source_object_type` + `source_object_id`.

2. **`core/services/ops_autopilot/impact.py:1233-1290`** —
   `MultiTouchAttributor._attribute_event(event)` — **THE
   attribution algorithm** (F.E6 correction; parent doc named
   `ops_autopilot/revenue.py` incorrectly). Writes 1-N
   `ImpactCredit` rows per event:
   - No upstream → 100% last-touch credit at `:1250-1260`.
   - Upstream exists → 70% last-touch at `:1263-1273` (uses
     `LAST_TOUCH_SHARE` class constant); 30% assist evenly split
     across upstream at `:1276-1288` (uses `ASSIST_SHARE / len(upstream)`).
   - Upstream discovery via `_find_upstream(event):1292+` — uses
     `trace_id`, `deliverable→initiative/dream`, `agent_chain`
     with `MAX_HOPS` cap.

### 3.3 Read entries — attribution/analytics consumers

**View-layer readers** (F.E5 analysis):

1. **`core/views_revenue.py:16-70` — `create_revenue`** — POST
   `/api/revenue/create/` (duplicate pair with view file #3 below).
2. **`core/views_revenue.py:73-124` — `get_revenue_summary`** — GET
   `/api/revenue/summary/?days=30` (duplicate pair below).
3. **`core/views_revenue_analytics.py:1-754`** — 7 endpoints,
   architecturally distinct: `revenue_dashboard:39-156`,
   `platform_revenue_detail:163-293`, `compare_platforms:300-415`,
   `calculate_roi:422-513`, `revenue_forecast:520-601`,
   `revenue_goals:608-689`, `export_revenue_data:696-753`.
4. **`core/views_revenue_tracking.py:18-269`** — 4 class-based
   views (F.E5 F.E5 zero-docstring pattern): `RevenueStatsView.get:
   18-86`, `TrackRevenueView.post:89-145`, `UpdateRevenueStatusView.
   post:148-205`, `RevenueHistoryView.get:208-269`.

**Analytics-layer readers** (attribution + IQROI + ML training):

5. **`core/services/ops_autopilot/impact.py:565-699`** —
   `PortfolioAllocator.compute_desk_iqroi(now, window_hours=72)`
   reads `ImpactEvent` at `:582` + `LLMCallLog` for cost side,
   computes desk IQROI = (impact_value_usd + impact_points ×
   point_usd_value) / cost_usd.
6. **`core/services/ml_scoring_engine.py:585-588`** — reads
   `OpportunityOutcome.filter(outcome='won', task__opportunity__
   spider_data__isnull=False)` for ML retraining signal.
7. **`core/services/ml_scoring_engine.py:673-675`** — reads
   `OpportunityOutcome.filter(task__opportunity__spider_data__
   spider_name=spider_name).values('outcome').annotate(count)` for
   adaptive scoring by spider source.
8. **`core/services/ml_scoring_engine.py:1240-1242`** — **F.E2
   phantom field bug**: reads
   `OpportunityOutcome.filter(recorded_at__gte=cutoff)` — schema
   field is `created_at` not `recorded_at`. Would raise
   `FieldError` at first invocation.
9. **`core/services/event_handlers.py:290-292`** — **F.E2 phantom
   field bug**: reads
   `OpportunityOutcome.filter(actual_outcome__isnull=False)` —
   schema field is `outcome` not `actual_outcome`. Would raise
   `FieldError`.
10. **`core/tasks_ops.py:1576-1581`** — reads OpportunityOutcome
    for daily digest stats (tasks_won, tasks_lost, win_rate,
    total_revenue).
11. **`core/views_opportunity.py:1766-1774`** — reads for dashboard
    win/loss stats per user.

**Attribution/learning bridge readers/writers:**

12. **`core/learning_bridges/revenue_attribution_bridge.py:147+:181`** —
    `_update_agent_learning` + `_update_user_revenue_patterns` write
    `UserAgentLearning` on `Revenue.post_save` signal. F.E9
    verified.

## 4. Major Models

Cat E's evidence surface enumerates **6 canonical models** in the
core Revenue namespace + **4 parallel intelligence-side models**
(F.E3 dual-representation):

### 4.1 Core-namespace revenue models

**`OpportunityRevenue`** — `core/models_unified_system.py:2613-2802`
(Session 224). 19 fields. **REVENUE_STATUS_CHOICES has 5 declared,
1 REACHABLE (F.E1):**

| Field | Type | Notes |
|---|---|---|
| id | UUIDField PK | uuid4 |
| opportunity | FK → Opportunity | CASCADE |
| user | FK → AUTH_USER_MODEL | CASCADE |
| amount | DecimalField(12,2) | required |
| currency | CharField(3) | default 'USD' |
| platform_fee | DecimalField(10,2) | default 0 |
| net_amount | DecimalField(12,2) | required; auto-calculated in save() at `:2773` if None |
| **status** | CharField(20) | **choices = REVENUE_STATUS_CHOICES; default 'received' — F.E1: only `'received'` reachable** |
| content_type | CharField(20) | choices CONTENT_TYPE_CHOICES (11 values) |
| platform | CharField(30) | choices PLATFORM_CHOICES (11 values); default 'direct' |
| image_history | FK → content.ImageHistory | SET_NULL, nullable |
| video_history | FK → content.VideoHistory | SET_NULL, nullable |
| content_ids | JSONField | default list |
| estimated_revenue | DecimalField(12,2) | nullable |
| prediction_accuracy | FloatField | nullable; auto-calculated in save() |
| description | TextField | blank |
| sale_date | DateTimeField | required |
| payment_received_date | DateTimeField | nullable |
| external_reference | CharField(200) | blank |
| created_at | DateTimeField | auto_now_add |
| updated_at | DateTimeField | auto_now |

Meta at `:2758-2765`: `ordering=['-sale_date']`, 3 indexes on
`(opportunity, status)` + `(user, sale_date)` + `(platform, status)`.
Custom `save()` at `:2767-2802`: auto-calculates net_amount +
prediction_accuracy + updates related `Opportunity.status='earning'`
side effect.

**REVENUE_STATUS_CHOICES verification** (F.E1 direct-read):

| State | Writers | Reachability |
|---|---|---|
| `'pending'` | 0 | UNREACHABLE |
| `'received'` | 2 (default at `:2688`; 2 writers rely on default) | REACHABLE |
| `'partial'` | 0 | UNREACHABLE |
| `'cancelled'` | 0 | UNREACHABLE |
| `'refunded'` | 0 | UNREACHABLE |

Parent-Claude broadened grep for OpportunityRevenue writes with
non-default status: 0 hits (F.E1 verified against
S1401-broadened-grep methodology; no false positives).

**`OpportunityOutcome`** — `core/models_unified_system.py:3394-3490`
(Session 425). 13 fields. **OUTCOME_CHOICES has 5 declared, 2
REACHABLE (F.E1):**

| Field | Type | Notes |
|---|---|---|
| id | UUIDField PK | uuid4 |
| task | OneToOneField → OpportunityTask | CASCADE, related_name='outcome' |
| **outcome** | CharField(20) | **choices = OUTCOME_CHOICES; F.E1: only `won` + `lost` reachable** |
| actual_revenue | DecimalField(12,2) | nullable |
| predicted_revenue | DecimalField(12,2) | nullable |
| revenue_variance | DecimalField(12,2) | help_text="Actual - Predicted"; auto-calculated in save() |
| loss_reason | CharField(20) | choices LOSS_REASON_CHOICES; blank |
| days_to_outcome | IntegerField | nullable; auto-calculated in save() |
| notes | TextField | blank |
| lessons_learned | JSONField | default list |
| metadata | JSONField | default dict |
| created_at | DateTimeField | auto_now_add |

Meta at `:3472-3474`: `ordering=['-created_at']`. Custom `save()` at
`:3476-3487` auto-calculates `revenue_variance` (actual -
predicted_revenue from task.opportunity.potential_revenue) +
`days_to_outcome` from task.created_at.

**OUTCOME_CHOICES verification** (F.E1 direct-read):

| State | Writers | Reachability |
|---|---|---|
| `'won'` | 2 (`OpportunityTask.mark_won:3166,3168`) | REACHABLE |
| `'lost'` | 2 (`OpportunityTask.mark_lost:3199,3201`) | REACHABLE |
| `'expired'` | 0 | UNREACHABLE |
| `'cancelled'` | 0 | UNREACHABLE |
| `'partial'` | 0 | UNREACHABLE (parent-Claude broadened grep flagged `tasks.py:6631` + `tasks_misc.py:162` as candidates — both disambiguated to `PilotExecution` model, unrelated to `OpportunityOutcome`; no false positives) |

**`OpportunityContent`** — `core/models_unified_system.py:2805-2903`
(Session 224). 14 fields. Related to Cat E via `total_revenue`
property at `:2889-2895` (sums linked ImageHistory/VideoHistory
`opportunity_revenues` backref). CONTENT_TYPE_CHOICES has 6
declared, all 6 REACHABLE via single writer point at
`views_opportunity.py:1115` (F.E1 does NOT extend here — normal
choices coverage).

**`ImpactEvent`** — `core/models_impact_events.py:21-120`. Fields:
`impact_type` (choices: wager_profit, revenue_confirmed,
content_action/save/export/share, prediction_hit), `desk` (choices:
sports, content, research, career, trading, general), `value_usd`
(nullable, can be negative), `impact_points` (int), `agent_name`,
`source_object_type` (Wager/DeliverableEvent/Revenue/Deliverable),
`source_object_id` (UUID), `trace_id` (UUID), `attributed_cost_usd`
(denormalized LLM cost), `user` FK, `metadata` JSONField,
`created_at` (indexed).

**`ImpactCredit`** — `core/models_impact_credit.py`. Written by
`MultiTouchAttributor._attribute_event:1250-1288`. Fields include:
`impact_event` FK, `desk`, `agent_name`, `credit_type`
(`last_touch`/`assist`), `credit_usd`, `credit_points`,
`credit_share`, `hop_distance`, `link_type`.

**`Revenue`** (core mainline) — separate from `OpportunityRevenue`.
Referenced by `revenue_attribution_bridge.py:227` post_save signal.
`ImpactCollector._collect_revenue_impacts` at `impact.py:455-504`
reads `Revenue` (not OpportunityRevenue). Two Revenue schemas
co-exist in core namespace — F.E3 note; not a new drift but
adjacent to the intelligence-side parallel schema.

### 4.2 Intelligence-namespace parallel revenue models (F.E3)

**`RevenueSource`** — `intelligence/revenue_tracking_bridge.py:16`
(Django model). Tracks revenue sources (freelance/job/income_stream/
passive).

**`RevenueRecord`** — `intelligence/revenue_tracking_bridge.py:29`
(Django model, PARALLEL SCHEMA to OpportunityRevenue). Custom
`save()` at `:48` auto-computes `net_amount`.

**`ProposalTracker`** — `intelligence/revenue_tracking_bridge.py:57`
(Django model). Tracks proposals + outcomes.

**`RevenueDashboardMetrics`** — `intelligence/revenue_tracking_bridge.
py:83` (Django model). Aggregate dashboard metrics.

**Ownership**: These 4 models are in the `intelligence` app, not
`core`. Only 1 known caller: `real_execution_engine.py:106` in
`_execute_job_applications()`. **Post_save signal on `Revenue`
does NOT fire on `RevenueRecord`.** Two disconnected pipelines.

**`ActionPlan`** — model at `intelligence/…` (written by
`revenue_integration.py:225`). Parallel to `OpportunityAction`
in core.

## 5. Major Services

### 5.1 `ops_autopilot/impact.py` (attribution engine)

**`ImpactCollector` (`impact.py:238-505`)** — 24h impact harvester.
- `collect_all(now, window_hours=24):263-300` — driver.
- `backfill(days=14):303-343` — idempotent replay.
- `_collect_wager_impacts:345-393` — Wager → ImpactEvent (sports desk).
- `_collect_deliverable_impacts:395-453` — DeliverableEvent →
  ImpactEvent (content desk).
- `_collect_revenue_impacts:455-504` — Revenue → ImpactEvent
  (desk mapped via REVENUE_SOURCE_DESK).

**`PortfolioAllocator` (`impact.py:509-841`)** — desk-level IQROI +
budget re-allocation.
- `compute_desk_iqroi(now, window_hours=72):565-699` — IQROI =
  (impact_value_usd + impact_points × point_usd_value) / cost_usd;
  EWMA-smoothed.

**`GoalAwareAllocator` (`impact.py:842-1162`)** — system-goal
weighted allocation (revenue, sports_profit, content_engagement,
quality, freshness).

**`MultiTouchAttributor` (`impact.py:1163-1480`)** — F.E6 canonical
attribution algorithm.
- `attribute_recent(...):1192-1231` — driver.
- `_attribute_event(event):1233-1290` — 70/30 last-touch/assist split.
- `_find_upstream(event):1292+` — trace_id/deliverable/dream/agent
  chain walk with `MAX_HOPS` cap.
- `get_attribution_report(...):1425-1471` — desk-level credit sum.

**`AttributionDebtController` (`impact.py:1481+`)** — LLM spend
attribution-debt monitor. Debt > 40% blocks reallocation; > 20%
warns via HAI.

### 5.2 `ops_autopilot/revenue.py` (pipeline engines, NOT attribution)

Six pipeline-side engine classes; NONE compute attribution
(F.E6 correction):

- `RevenuePipelineAutomator (:236-383)` — stale-opportunity monitor.
- `OutboundLeadEngine (:389-599)` — lead discovery + scoring
  (recency/revenue-signal/channel-fit/source-quality).
- `OutreachSequencer (:605-850)` — 4-touch cadence (Day 0/3/7/14)
  + daily approval cap 10.
- `CloseTheDealEngine (:851-1185)` — S1404 F.D7 CONFIRMED writer
  for ClosePack `draft`+`approved`; 4 offer templates.
- `RevenueOrchestrator (:1186-1502)` — unified funnel view;
  `get_revenue_forecast:1389-1450` uses hardcoded conversion rates
  (probabilistic forecasting, NOT attribution).
- `ClosePackAutonomyEngine (:1504+)` — S1404 F.D7/F.D10 CONFIRMED
  writer for ClosePack `expired`.

### 5.3 Bridge services (F.E3 dual-representation)

**`core/learning_bridges/revenue_attribution_bridge.py`** — signal-
driven learning bridge.
- `RevenueAttributionLearningLoop.process_event(revenue):58`.
- `_update_agent_learning:147-170` — writes UserAgentLearning
  (`learning_domain='revenue_optimization'`).
- `_update_user_revenue_patterns:181-210` — writes UserAgentLearning
  (`learning_domain='success_factors'`).
- `on_revenue_saved:228` @receiver(post_save, sender=Revenue)
  fires on any Revenue create or status='completed'.
- **Zero HAI writers** (F.D4 CONFIRMED at bridge layer).
- **Docstring drift (F.D6-analog)**: line-4 claim "Feeds insights
  to UnifiedLearningPipeline" is unfulfilled — `_generate_insights`
  returns list of strings, never dispatches.

**`intelligence/revenue_tracking_bridge.py`** — parallel-schema
async bridge (F.E3).
- `RevenueTrackingBridge.record_revenue():120-159` — writes
  RevenueRecord + RevenueDashboardMetrics + WebSocket notify.
- `track_proposal():199-231` — writes ProposalTracker.
- `update_proposal_status():233-266` — writes ProposalTracker.
- `_update_daily_metrics():268-347` — writes
  RevenueDashboardMetrics.
- `_notify_revenue_generated():350+` — WebSocket only.
- **Zero HAI writers** + **`_REDIS_URL:18` defined but unused**
  (F3 lens hit — dead import).

**`intelligence/revenue_integration.py`** — orchestrator (F.E3).
- `RevenueIncomeIntegration.process_opportunity(async):63` — entry point.
- `create_revenue_action_plan(async):156-231` — writes `ActionPlan`
  at `:225`. Zero writes to Revenue.
- `track_proposal(async):283-304` — delegates to
  `self.revenue_tracker.track_opportunity()` (mock RevenueTracker,
  NOT the real bridge).
- **Docstring drift (CONFIRMED)**: line 13-21 claims full pipeline
  "Spider Data → Opportunity → Score → Action → Revenue →
  Learning"; code stops at ActionPlan.objects.create at `:225`.
  Never writes Revenue; never calls learning bridges.

### 5.4 Ownership-signal service

**`core/services/pa_tool_schemas.py:188-208`** — `revenue_tracker_tool`
PA tool schema. Actions: `log_revenue`, `list_revenue`, `stats`,
`link_content`. Routes to `intelligence_enricher` +
`proactive_intelligence` queues at `:5087`. Module tag
`'opportunities'` at `:5194`. **This is the ONLY owner-side
signal for the Revenue domain** (F.E10).

## 6. Major APIs and Interfaces

### 6.1 REST endpoints (3 view files + `core/urls.py`)

| Endpoint | Method | View | Notes |
|---|---|---|---|
| `/api/revenue/create/` | POST | `views_revenue.create_revenue:16-70` | F.E5 duplicate pair |
| `/api/revenue/summary/?days=30` | GET | `views_revenue.get_revenue_summary:73-124` | F.E5 duplicate pair |
| `/api/v1/revenue/track/` | POST | `views_revenue_tracking.TrackRevenueView.post:89-145` | F.E5 duplicate pair; broadcasts WebSocket |
| `/api/v1/revenue/stats/` | GET | `views_revenue_tracking.RevenueStatsView.get:18-86` | F.E5 duplicate pair; calls MISSING `Revenue.get_user_total()` |
| `/api/v1/revenue/<uuid:revenue_id>/update-status/` | POST | `views_revenue_tracking.UpdateRevenueStatusView.post:148-205` | Status transitions + broadcast |
| `/api/v1/revenue/history/` | GET | `views_revenue_tracking.RevenueHistoryView.get:208-269` | Paginated + filtered |
| `/api/distribution/revenue/dashboard/` | GET | `views_revenue_analytics.revenue_dashboard:39-156` | DISTINCT surface |
| `/api/distribution/revenue/platform/<str:platform_name>/` | GET | `views_revenue_analytics.platform_revenue_detail:163-293` | DISTINCT |
| `/api/distribution/revenue/compare/` | GET | `views_revenue_analytics.compare_platforms:300-415` | DISTINCT |
| `/api/distribution/revenue/roi/` | GET/POST | `views_revenue_analytics.calculate_roi:422-513` | DISTINCT |
| `/api/distribution/revenue/forecast/` | GET | `views_revenue_analytics.revenue_forecast:520-601` | DISTINCT; 7/30/90-day |
| `/api/distribution/revenue/goals/` | GET/POST | `views_revenue_analytics.revenue_goals:608-689` | DISTINCT; session-stored |
| `/api/distribution/revenue/export/` | GET | `views_revenue_analytics.export_revenue_data:696-753` | DISTINCT; JSON export |
| `/api/v1/analytics/charts/revenue/` | GET | (external — served by analytics dispatcher) | Called from AnalyticsDashboardPage |

### 6.2 WebSocket surfaces

- `revenue_dashboard_{user_id}` — broadcast on
  `TrackRevenueView.post` + `UpdateRevenueStatusView.post`
  (F.E5-adjacent).
- Async notification path in `intelligence/revenue_tracking_bridge.
  py:_notify_revenue_generated:350+` (F.E3).

### 6.3 PA tool surface

- `revenue_tracker_tool` at `core/services/pa_tool_schemas.py:188-208`
  — 4 actions (`log_revenue`, `list_revenue`, `stats`,
  `link_content`); routes to `intelligence_enricher` +
  `proactive_intelligence` queues.

## 7. Runtime Flows

### 7.1 Revenue creation flow (manual)

```
User/agent → POST /api/revenue/create/ (or /api/v1/revenue/track/ — F.E5 duplicate)
    ↓
views_revenue.create_revenue:16-70 (or TrackRevenueView.post:89-145)
    ↓
OpportunityRevenue(status=default 'received').save()
    ↓ (in save() override at :2767-2802)
Opportunity.status = 'earning'
    ↓ (post_save signal fires on Revenue — separate model)
revenue_attribution_bridge.py:on_revenue_saved:228 → RevenueAttributionLearningLoop.process_event
    ↓
_update_agent_learning:147 + _update_user_revenue_patterns:181 → UserAgentLearning writes
    ↓
_generate_insights:122 → strings (never dispatched — CANDIDATE drift F.E9)
```

### 7.2 Revenue creation flow (PA tool)

```
Rigby → run_agent revenue_tracker_tool action=log_revenue
    ↓
core/epa_handlers_tools.py:_handle_revenue_tracker_tool → dispatches to intelligence_enricher/proactive_intelligence queue
    ↓
OpportunityRevenue.objects.create(...notes=arguments.get('notes', ''))  ← F.E2 phantom field: TypeError on first invocation
    ↓ (never reached if TypeError fires; if reached...)
opp.status = 'accepted'  (at :3596)
```

### 7.3 Outcome creation flow (won/lost only — F.E1 reachable states)

```
User/agent → OpportunityTask.mark_won(actual_amount, notes) at :3166
    ↓
OpportunityOutcome(outcome='won', ...).save()  ← at :3166; save() at :3476 auto-calculates variance + days
    ↓
Opportunity.mark_as_accepted(actual_amount) at :3174 → creates OpportunityRevenue
    ↓
Discord notification (per S1404 §7 finding)
```

Or, symmetrically:

```
User/agent → OpportunityTask.mark_lost(reason, notes) at :3199
    ↓
OpportunityOutcome(outcome='lost', loss_reason, ...).save()  ← at :3199
    ↓
Opportunity.status = 'rejected'
```

**Note:** `expired`, `cancelled`, `partial` outcome states have
zero triggers — F.E1 arc-wide extension of F.D10.

### 7.4 Attribution flow (`impact.py`)

```
Wager/DeliverableEvent/Revenue models produce data
    ↓
ImpactCollector.collect_all(now, window_hours=24) at :263  ← driver; run by _policy_impact_portfolio in core.py:1521 (F.C6 DORMANT — beat deferred)
    ↓
_collect_wager_impacts:345 → ImpactEvent(desk='sports')
_collect_deliverable_impacts:395 → ImpactEvent(desk='content')
_collect_revenue_impacts:455 → ImpactEvent(desk=mapped, impact_type='revenue_confirmed')
    ↓
MultiTouchAttributor.attribute_recent:1192  ← driver
    ↓ for each unattributed ImpactEvent
_attribute_event:1233 → ImpactCredit rows (70% last-touch + 30% assist split)
    ↓
get_attribution_report:1425 → desk-level credit sum
    ↓ if debt > 40% → _create_attention_item at :1673 → HumanAttentionItem (F.E7)
```

**Runtime status:** F.C6 gate. `_policy_impact_portfolio` and
`_policy_attribution_debt` fire only when `run_ops_autopilot`
beat runs. That beat is DEFERRED per AUDIT_FINDINGS.md #12
(`core/celery.py:634`). Ad-hoc paths via `td_handlers_ops.py`
exist for PA-tool invocation (F.C6 continuation).

### 7.5 Beat task flow (`calculate-daily-revenue-metrics`)

```
Celery beat crontab(hour=0, minute=15) at core/celery.py:617-620
    ↓
intelligence.tasks.calculate_daily_revenue_metrics:1462-1495 at 12:15 AM Denver, queue='default'
    ↓
RevenueMetrics.update_metrics_for_date(today)  ← delegates to model method
    ↓
returns dict {opportunities, proposals, conversions, revenue}
```

**Independent path** — NOT connected to `ops_autopilot/revenue.py`
(F.C6 dormant beat) NOR to `ImpactEvent` pipeline (F.E8 attribution
chain). This is a **third revenue pipeline** at runtime alongside
core + intelligence-side (F.E3 refinement).

## 8. Data Ownership and Lifecycle

### 8.1 OpportunityRevenue lifecycle

| Stage | Trigger | Writer | Result |
|---|---|---|---|
| Create | POST endpoint or PA tool | `views_opportunity.py:780` or `epa_handlers_tools.py:3583` | status='received' (default) |
| Read (analytics) | Frontend dashboard | `views_revenue_analytics.revenue_dashboard:86` | filters status='received' |
| Read (stats) | Frontend + PA | `views_opportunity.py:967` + `epa_handlers_tools.py:3638` | aggregates by platform + content_type |
| Update (linked content) | PA tool `link_content` | `epa_handlers_tools.py:3722-3730` | **F.E2 AttributeError on `.metadata`** |
| **NO update to non-'received' states** | — | — | pending/partial/cancelled/refunded UNREACHABLE (F.E1) |

### 8.2 OpportunityOutcome lifecycle

| Stage | Trigger | Writer | Result |
|---|---|---|---|
| Create (won) | User/agent decision | `OpportunityTask.mark_won:3166` | outcome='won' + revenue linked |
| Create (lost) | User/agent decision | `OpportunityTask.mark_lost:3199` | outcome='lost' + loss_reason |
| Read (ML training) | Batch retraining | `ml_scoring_engine.py:585` | filters won only |
| Read (per-spider) | Adaptive scoring | `ml_scoring_engine.py:673` | annotates by spider |
| Read (ML training, broken) | Attempted retraining | `ml_scoring_engine.py:1240-1242` | **F.E2 FieldError on `recorded_at`** |
| Read (retraining trigger, broken) | Post-outcome hook | `event_handlers.py:290-292` | **F.E2 FieldError on `actual_outcome`** |
| Read (digest) | Daily digest | `tasks_ops.py:1576-1581` | by date range + outcome type |
| Read (dashboard) | User view | `views_opportunity.py:1766-1774` | win/loss stats |
| **NO update to non-won/lost states** | — | — | expired/cancelled/partial UNREACHABLE (F.E1) |

### 8.3 ImpactEvent + ImpactCredit lifecycle

| Stage | Trigger | Writer | Result |
|---|---|---|---|
| Emit | 24h harvest | `ImpactCollector.collect_all:263` | 3 write sites (`:375`, `:431`, `:488`); idempotent dedup |
| Attribute | Batch attribution | `MultiTouchAttributor.attribute_recent:1192` | 1-N ImpactCredit rows per event |
| Read (allocation) | 72h IQROI | `PortfolioAllocator.compute_desk_iqroi:565` | desk-level allocation dict |
| Read (report) | Governance | `get_attribution_report:1425` | desk-level credit sum |
| Read (A/B tests) | Experiment eval | `experiment.py:641` | metric collection |
| Read (budget) | ROI enforcement | `budget.py:644` | filter by desk + created_at |
| **Governance write** | Debt > 20% or 40% | `_policy_attribution_debt` → `_create_attention_item:1673` | HumanAttentionItem |

## 9. Integrations With Other Domains

### 9.1 Integration map (Cat E ↔ upstream + downstream)

| Row | Direction | From | To | File:line | Semantic | Confidence |
|---|---|---|---|---|---|---|
| 1 | ← A (upstream) | Opportunity | OpportunityRevenue.opportunity | `:2624` FK | Every revenue row is per-opportunity | CONFIRMED |
| 2 | ← A (upstream) | Opportunity | OpportunityContent.opportunity | `:2823` FK | Every content row is per-opportunity | CONFIRMED |
| 3 | ← D (upstream) | OpportunityTask.mark_won | OpportunityOutcome(outcome='won') | `:3166` write | Won transitions create outcome | CONFIRMED |
| 4 | ← D (upstream) | OpportunityTask.mark_won | Opportunity.mark_as_accepted → OpportunityRevenue | `:3174` chained | Won also creates revenue row | CONFIRMED |
| 5 | ← D (upstream) | ClosePack `won`/`lost`/`sent` states | (would transition here) | — | F.D10 UNREACHABLE — no ClosePack → OpportunityRevenue trigger | CONFIRMED MISSING |
| 6 | ← B (upstream) | OutreachDraft.status transitions | (would connect via HumanAttention approval) | — | F.B1 + F.C1 + F.D6 ADR chain must land first | CONFIRMED PARKED |
| 7 | → Observability (downstream) | ImpactEvent | PortfolioAllocator + budget.py + experiment.py | 6+ readers | S1274 §2.4 STRONG classification VERIFIED (F.E8) | CONFIRMED |
| 8 | → Learning (downstream) | Revenue.post_save | UserAgentLearning | `revenue_attribution_bridge.py:227,147,181` | 2-path write to learning; F.E9 VERIFIED | CONFIRMED |
| 9 | → HumanAttention (downstream) | _policy_attribution_debt | HumanAttentionItem | `core.py:1673` | Debt gating; F.E7 CODE-EXISTS/RUNTIME-DORMANT | CONFIRMED (dormant runtime via F.C6) |
| 10 | → HumanAttention (downstream) | _policy_revenue_pipeline | HumanAttentionItem | `core.py:2051` | Stale-opp gating; F.E7 CODE-EXISTS/RUNTIME-DORMANT | CONFIRMED (dormant runtime via F.C6) |
| 11 | → Learning (broken) | Revenue.metadata attribution | (fails at attribute lookup) | `revenue_attribution_bridge.py:102-104` | F.E2 phantom field (guarded by hasattr) | CONFIRMED broken; low blast radius |
| 12 | → Analytics (frontend) | OpportunityRevenue | `/analytics` route | `AnalyticsDashboardPage → /api/v1/analytics/charts/revenue/` | F.E4 correction — NOT the 4 named routes | CONFIRMED (parent-doc drift) |

### 9.2 Parallel-schema disconnection (F.E3)

| Core-side path | Intelligence-side path | Bridged? |
|---|---|---|
| `OpportunityRevenue` (core.models_unified_system) | `RevenueRecord` (intelligence.revenue_tracking_bridge) | NO |
| `Revenue` (core; post_save fires attribution bridge) | `RevenueRecord.post_save` (never triggers bridge) | NO |
| `OpportunityAction` (core, S1404 finding) | `ActionPlan` (intelligence.revenue_integration:225) | NO |
| `views_revenue*` (core, 3 files) | `intelligence/revenue_tracking_bridge` async surface | NO |

**Two disconnected revenue pipelines exist in the same repo.**
Extends S1401 D6 dual-representation drift (which was for
`Opportunity` model) to the Revenue domain.

## 10. Event Flows

### 10.1 `post_save` signals

- `revenue_attribution_bridge.py:227` — @receiver(post_save,
  sender=Revenue). Fires on any Revenue create OR any Revenue
  status='completed' transition. NOT on `OpportunityRevenue`
  post_save. NOT on `RevenueRecord` post_save.

### 10.2 `ImpactEvent` emission events

- No `event_bus.py` events for revenue emission. `ImpactEvent`
  is a persistent model, not an event bus stream. Reads are via
  ORM query, not event subscription.

### 10.3 WebSocket broadcast events

- `revenue_dashboard_{user_id}` broadcast on
  `TrackRevenueView.post` + `UpdateRevenueStatusView.post`
  (async surface via channels).

### 10.4 Deferred/dormant events (F.C6)

- `_policy_impact_portfolio` (`core.py:1521`) — reads ImpactEvent,
  writes ImpactCredit + HAI. Fires when `run_ops_autopilot` beat
  runs. DEFERRED per AUDIT_FINDINGS.md #12.
- `_policy_attribution_debt` (`core.py:1673`) — reads
  attribution debt, writes HAI. Same deferral.
- `_policy_revenue_pipeline` (`core.py:2022`) — reads stale opps,
  writes HAI. Same deferral.
- Ad-hoc PA-tool paths exist for these policies via
  `td_handlers_ops.py` (F.C6 pattern from S1403).

## 11. Existing Documentation

### 11.1 Narrative anchor

- `docs/PLATFORM_WHAT_IT_IS.md` — mentions revenue at high level
  but no attribution-algorithm depth.

### 11.2 Inventory anchor

- `docs/PLATFORM_INVENTORY.md` — enumerates OpportunityRevenue +
  OpportunityOutcome + OpportunityContent in models list (588
  concrete models); does not enumerate intelligence-side
  RevenueRecord/ProposalTracker.

### 11.3 Prior research

- **S1273 platform_architecture_inventory §3.32 Revenue Pipeline
  row** — LIGHT coverage; §4.9 flow includes "ImpactEvent" step;
  §10.3 UNKNOWN #3 (attribution algorithm) RESOLVED by F.E6.
- **S1274 cross_domain_integration_audit §2.4** — line 292
  Revenue → Observability STRONG (F.E8 VERIFIED); §4.3
  revenue_attribution_bridge writes Revenue → UserAgentLearning
  (F.E9 VERIFIED); §14 finding #36 no runtime owner HIGH (F.E10
  VERIFIED at code layer).
- **S1401 audit** — Cat A read seam; introduced D6 dual-representation
  drift methodology which F.E3 extends to Revenue.
- **S1402 audit** — Cat B; F.B4 cadence-declared-not-realized
  methodology (analogous to F.E1 states-declared-not-reached).
- **S1403 audit** — Cat C; F.C6 `run_ops_autopilot` deferred-by-
  policy inherited as F.E7 dormancy classification.
- **S1404 audit** — Cat D; F.D1 runtime-empty locally (extends to
  Cat E); F.D4 arc-wide HAI missing (F.E7 refines to code-exists);
  F.D10 ClosePack state-machine PARTIAL (F.E1 extends arc-wide
  to 3 models).

### 11.4 Docstring evidence

- `OpportunityRevenue` docstring at `:2614-2618`: "Track actual
  revenue generated from opportunities … closing the loop between
  discovered opportunities and real income" — matches code intent;
  no load-bearing drift.
- `OpportunityOutcome` docstring at `:3395-3400`: "Track final
  outcomes … enable the system to learn from outcomes and improve
  scoring" — matches intent; but readers reference phantom fields
  (F.E2) breaking the claimed learning feedback path.
- `OpportunityContent` docstring at `:2806-2811`: "Link content
  created from opportunities … enabling revenue attribution when
  that content generates income" — matches intent; MINIMAL drift.
- `ops_autopilot/revenue.py` docstring lines 1-218: "Ops Autopilot
  v8 module … All actions create HumanAttentionItem for governance
  visibility." — F.D6-analog drift: only true at core.py dispatch
  layer, NOT at engine classes (F.E7 arc-wide refinement).
- `revenue_attribution_bridge.py:1-16`: "Feeds insights to
  UnifiedLearningPipeline" — CANDIDATE drift (F.E9): insights
  generated but never dispatched.
- `intelligence/revenue_integration.py:13-21`: pipeline claim
  "Spider Data → Opportunity → Score → Action → Revenue → Learning"
  — CONFIRMED drift: code stops at ActionPlan (F.E3).

## 12. Research Coverage

### 12.1 Parent §12.1 Category E F.iii questions answered

- **Q1: What is the revenue attribution algorithm
  (`ops_autopilot/revenue.py`)?**
  **ANSWER (F.E6):** Algorithm is NOT in `revenue.py` (parent-doc
  drift). Actual algorithm at `core/services/ops_autopilot/impact.
  py:1233-1290` (`MultiTouchAttributor._attribute_event`). 70%
  last-touch + 30% assist evenly split among upstream discovered
  via trace_id + deliverable→initiative/dream + agent_chain
  (`_find_upstream:1292+`, MAX_HOPS cap). Writes ImpactCredit rows
  (`core/models_impact_credit.py`) — 1-N rows per event. Resolves
  S1273 §3.32 UNKNOWN drift (via anchor correction at commit-time).

- **Q2: How does `ImpactEvent` emission work (write/read
  registry)?**
  **ANSWER (F.E8):** ImpactCollector at `impact.py:238-505`
  harvests from Wager (`:375`), DeliverableEvent (`:431`), Revenue
  (`:488`) sources into ImpactEvent at `core/models_impact_events.
  py:21-120`. Idempotent dedup by (source_object_type,
  source_object_id). 6+ readers: PortfolioAllocator IQROI
  (`impact.py:582`), MultiTouchAttributor.attribute_recent
  (`impact.py:1209`), ROIEnforcer (`budget.py:644`),
  ExperimentEngine (`experiment.py:641`), get_attribution_report
  (`impact.py:1457`). Governance write via _policy_attribution_debt
  (`core.py:1673`) → HAI. S1274 §2.4 STRONG classification VERIFIED
  end-to-end.

- **Q3: How do 4 frontend routes + 3 view files serve distinct vs
  overlapping needs?**
  **ANSWER (F.E4 + F.E5):** The 4 routes named in parent §3.E do
  NOT exist (F.E4 parent-doc drift; correction at commit-time).
  Revenue features are surfaced via `/analytics` +
  `/intelligence` routes. Among the 3 view files:
  `views_revenue_analytics.py` is architecturally distinct (7
  endpoints for platform distribution, forecasting, ROI, goals,
  export); `views_revenue.py` + `views_revenue_tracking.py`
  provide DUPLICATE endpoints (POST create + GET summary/stats
  pairs) with different models + response formats + URL
  namespaces (F.E5 CONFIRMED HIGH; consolidation ADR proposed at
  §19 R.E2).

- **Q4: What is the runtime owner recommendation (S1274 §14
  finding #36 HIGH)?**
  **ANSWER (F.E10):** Runtime owner is ABSENT arc-wide. Zero
  JobContract in `core/employees/jobs.py`; zero AGENT_MAP entries
  in `core/agent_router.py`; zero task_routes for revenue; no
  dedicated queue (`calculate_daily_revenue_metrics` uses
  `'default'` at `core/celery.py:620`). Only ownership signal:
  PA tool `revenue_tracker_tool` at `pa_tool_schemas.py:188-208`.
  **Recommendation: assign dedicated Revenue Employee under
  Employee OS** (JobContract owning revenue lifecycle:
  create/track/attribute/summarize/forecast) with dedicated
  Celery queue. See §19 R.E1 ADR.

- **INHERITED from S1404: How does Cat E reason about Revenue
  Attribution runtime liveness given F.D1/F.D3/F.D4/F.D10?**
  **ANSWER:** Cat E inherits F.D1 empirical runtime dormancy
  (Meeting=0, ClosePack=0, EngagementEvent=0 locally) which
  extends to OpportunityRevenue + OpportunityOutcome (likely
  also zero locally, unverified due to T.C8 minimal-blocking
  D43 lean). Revenue attribution presupposes ClosePack
  `sent`→`won`/`lost` transitions that F.D10 confirmed
  unreachable in code. So the attribution chain is CODE-COMPLETE
  end-to-end at the `impact.py` layer but RUNTIME-STARVED at the
  ClosePack/Revenue source-of-truth layer. F.E7 refines F.D4 to
  code-exists/runtime-dormant. F.E1 extends F.D10 to
  OpportunityRevenue + OpportunityOutcome (arc-wide 3-model
  over-modeling pattern).

### 12.2 Parent §11.4 inherited findings — resolutions

| Finding | Source | S1405 resolution |
|---|---|---|
| Revenue → Observability STRONG via ImpactEvent | S1274 §2.4 line 292 | F.E8 CONFIRMED end-to-end |
| Revenue → HumanAttention MISSING | S1274 §2.4 line 294 | F.E7 REFINED: code-exists/runtime-dormant (6 sites in `core.py`; gated on F.C6 dormancy) |
| Revenue Pipeline has no runtime owner HIGH | S1274 §14 #36 | F.E10 CONFIRMED at Cat E code layer; Cat E owns arc-wide synthesis per parent D28 |
| revenue_attribution_bridge writes Revenue → UserAgentLearning | S1274 §4.3 | F.E9 CONFIRMED (2-path write, signal-driven); docstring drift on "insights → pipeline" |
| Revenue Pipeline extraction readiness LOW | S1274 §9.6 | Confirmed (F.E3 dual-representation drift + F.E5 duplicate views + F.E10 no owner all argue LOW readiness) |
| S1399 F1 (provenance-filter drift) lens | S1399 §4 F1 | F.E2 is a MORE SEVERE variant (readers filter on fields that don't exist) |
| S1399 F2 (row-level orphan-write) lens | S1399 §4 F2 | Applied — several unattributed ImpactEvent writes if bridge dormant (F.C6 gate) |
| S1399 F3 (Redis-only durability + `@lru_cache`) lens | S1399 §4 F3 | `_REDIS_URL` in `revenue_tracking_bridge.py:18` is UNUSED dead code (minor hit) |
| S1399 F4 (CANDIDATE + severity-correction discipline) | S1399 §4 F4 | Applied throughout; verifier-loop caught zero refutations |

## 13. Architecture Maturity

**Verdict: FOUR-WAY SPLIT** extending S1403's four-way pattern.

- **WORKING** — attribution algorithm at `impact.py:
  MultiTouchAttributor` complete + `revenue_attribution_bridge`
  signal-driven UserAgentLearning writes + `views_revenue_analytics.
  py` 7-endpoint dashboard surface + `calculate_daily_revenue_metrics`
  beat task functional.
- **MISSING** — unified revenue write path (F.E3 two disconnected
  pipelines: core + intelligence + a third via
  `calculate_daily_revenue_metrics` → `RevenueMetrics` — all three
  isolated); state-machine over-modeling (F.E1 3-model UNREACHABLE
  states arc-wide); phantom-field bugs (F.E2 four sites).
- **DEFERRED-BY-POLICY** — `ops_autopilot/core.py` policies for
  revenue (F.E7 refinement of F.D4): 6 HAI-writer sites exist in
  code but are gated behind `run_ops_autopilot` beat which is
  deferred per AUDIT_FINDINGS.md #12.
- **DORMANT LOCAL RUNTIME** — Revenue tables likely empty
  locally per F.D1 pattern (Meeting=0, ClosePack=0,
  EngagementEvent=0). Direct `.count()` probes on
  OpportunityRevenue/OpportunityOutcome deferred per D43 minimal-
  blocking lean; parent-Claude verifier-loop did NOT run a runtime
  probe this session. Ad-hoc PA-tool paths remain live.

**Coverage rating: MEDIUM.** Analytics reads well-covered (7
endpoints + 4 more); attribution engine well-covered (single
canonical algorithm). Writes fragmented (F.E3 + F.E5). Ownership
absent (F.E10).

## 14. Known Drift

### 14.1 F.E1 — Over-modeled STATUS_CHOICES pattern (arc-wide 3-model)

| Model | Field | Declared | Reachable | Unreachable |
|---|---|---|---|---|
| ClosePack (S1404 F.D10) | status | 6 | 3 (draft/approved/expired) | 3 (sent/won/lost) |
| OpportunityRevenue | status | 5 | 1 (received) | 4 (pending/partial/cancelled/refunded) |
| OpportunityOutcome | outcome | 5 | 2 (won/lost) | 3 (expired/cancelled/partial) |

**Combined:** 16 states declared, 6 reachable, 10 UNREACHABLE
(62%). Arc-wide CONFIRMED HIGH pattern.

### 14.2 F.E2 — Phantom field references (4 sites)

| File:line | Reference | Actual schema field | Runtime error class |
|---|---|---|---|
| `ml_scoring_engine.py:1240-1242` | `OpportunityOutcome.recorded_at` | `created_at` (only) | FieldError |
| `event_handlers.py:290-292` | `OpportunityOutcome.actual_outcome` | `outcome` (only) | FieldError |
| `epa_handlers_tools.py:3583-3593` | `OpportunityRevenue(notes=...)` kwarg | `description` (only) | TypeError |
| `epa_handlers_tools.py:3722-3730` | `revenue.metadata['linked_content_id']` | (no metadata field) | AttributeError |
| `revenue_attribution_bridge.py:102-104` | `revenue.metadata.get(...)` (hasattr-guarded) | (no metadata field) | silent — intent unmet |

**Blast radius:** LOW-TO-ZERO currently (F.D1 pattern: Revenue
tables likely empty locally). LATENT bugs waiting for first real
invocation.

### 14.3 F.E3 — Dual-representation drift (parallel schemas)

Two revenue pipelines with documented integration gap:
- **Core:** `Revenue` + `OpportunityRevenue` + `OpportunityOutcome`
  in `core/models_unified_system.py`.
- **Intelligence:** `RevenueSource` + `RevenueRecord` +
  `ProposalTracker` + `RevenueDashboardMetrics` in
  `intelligence/revenue_tracking_bridge.py:16-108`.

`revenue_attribution_bridge.py:227` fires on core `Revenue` only.
Extends S1401 D6 dual-representation methodology from
`Opportunity` to `Revenue`.

**Rigby cycle 1 Batch 1 framing refinement (folded at S1405
commit-time):** the dual-schema pattern MAY be intentional design,
NOT missing integration. Two candidate interpretations:

- **(a) Missing integration** — original F.E3 framing. The
  intelligence-side pipeline should feed into core Revenue but the
  wiring is absent. Remediation: build the bridge (post_save on
  RevenueRecord → core Revenue → attribution bridge).
- **(b) Intentional dual-schema** — Rigby cycle 1 alternative
  framing. `RevenueRecord` could represent **external attribution
  ingestion** (job applications, freelance income, ad-hoc revenue
  events from spider pipelines) while core `Revenue` represents
  **finalized accounting truth** (bookkeeping-grade). In this
  reading, the gap is NOT "missing integration" but **"missing
  explicit contract + mapping + source-of-truth hierarchy"**.
  Remediation: document the source-of-truth rules + add explicit
  reconciliation policy + define analytic-query axis (which
  schema wins for which question).

**Load-bearing observation either way:** no declared
source-of-truth hierarchy across the parallel schemas → silent
analytic inconsistency risk. Which framing is correct is a
Chris/Rigby architectural decision at post-arc
design-preparation phase (see §19 R.E-3 revised scope).

### 14.4 F.E4 — Parent-doc frontend route drift (anchor correction #1)

Parent §3.E line 431 names 4 routes; ZERO exist in
`frontend/src/App.tsx`. Actual revenue features via `/analytics`
+ `/intelligence` routes. Landing correction at S1405 commit-time
per S1404 §20.10 pattern.

### 14.5 F.E6 — Parent-doc attribution algorithm location drift (anchor correction #2)

Parent §3.E + §12.1 name `ops_autopilot/revenue.py`; actual
algorithm at `ops_autopilot/impact.py::MultiTouchAttributor`.
Landing correction at commit-time.

### 14.6 Docstring drift

- `ops_autopilot/revenue.py` module docstring claims "All actions
  create HumanAttentionItem" — only true at `core.py` dispatch layer.
- `revenue_attribution_bridge.py:1-16` claims "Feeds insights to
  UnifiedLearningPipeline" — insights generated but never dispatched.
- `intelligence/revenue_integration.py:13-21` claims full pipeline
  "Spider Data → Opportunity → Score → Action → Revenue → Learning"
  — code stops at ActionPlan.
- `views_revenue_tracking.py` — all 4 class-based views have ZERO
  docstrings; F.E5 note.
- `calculate_daily_revenue_metrics:1462-1495` — docstring says
  "Runs daily at midnight" but schedule is 12:15 AM Denver (minor).

## 15. Known Technical Debt

- **T.E1 — 4 phantom-field bugs latent (F.E2).** Low-effort fixes;
  bundle into single PR post-arc. All 4 fixes are 1-line changes.
- **T.E2 — 10 UNREACHABLE STATUS_CHOICES entries across 3 models
  (F.E1).** Decision: (i) prune unreachable states from choices
  tuple (aligns choices with reachability); (ii) implement writers
  for unreachable states (aligns behavior with declared shape);
  (iii) leave as-is (declared for future). Deferred to S1499 xx99
  arc-wide synthesis.
- **T.E3 — Dual-representation drift (F.E3).** Not resolvable in
  a single ADR; requires arc-wide dual-schema consolidation
  design-preparation phase. Bundle with F.E5 view consolidation.
- **T.E4 — F.E5 duplicate view file endpoints.** Two POST-create
  paths, two GET-summary paths, different models. Consolidation
  ADR proposed at §19 R.E2.
- **T.E5 — `_REDIS_URL` in `revenue_tracking_bridge.py:18` UNUSED
  dead code.** Trivial cleanup; low-effort.
- **T.E6 — Missing `Revenue.get_user_total()` method** referenced
  by `views_revenue_tracking.py:RevenueStatsView.get`. Either
  add method to Revenue model OR remove reader (dead code).
- **T.E7 — `intelligence/revenue_integration.py` incomplete
  pipeline.** Docstring promises Revenue+Learning; code stops at
  ActionPlan. Either (i) complete the pipeline; (ii) update
  docstring to reflect actual scope.
- **T.E8 — No dedicated Celery queue for revenue pipeline
  (F.E10).** `calculate_daily_revenue_metrics` uses 'default'.
  Bundle with T.E9.
- **T.E9 — No JobContract for Revenue Employee (F.E10 core).**
  R.E1 ADR proposed at §19.

## 16. Boundary Violations

- **`OpportunityRevenue.save()` mutates related `Opportunity`
  state** (`:2783-2785`: `Opportunity.status = 'earning'`) —
  cross-model side effect. Not a violation per se (S1274 §5.10
  LOW-by-design classification carries) but a boundary crossing
  worth noting.
- **`OpportunityTask.mark_won:3174` chains
  `Opportunity.mark_as_accepted` which itself creates
  `OpportunityRevenue`** — 3-hop transaction depth in one call.
  If any step fails, atomicity is unclear.
- **`epa_handlers_tools.py:3596` sets `opp.status='accepted'`
  from PA tool** — direct writer to `Opportunity.status` outside
  Cat A's Opportunity ownership scope. S1401 §14 D2 read-seam
  discipline note applies.

## 17. Duplicate or Overlapping Systems

- **F.E5 duplicate endpoint pairs.** See §6.1 table. Consolidation
  ADR R.E2 proposed.
- **F.E3 duplicate revenue schemas.** Core (Revenue +
  OpportunityRevenue) + intelligence (RevenueRecord). Bridging
  ADR bundled with T.E3.
- **Third revenue pipeline** — `calculate_daily_revenue_metrics`
  beat task writes `RevenueMetrics.update_metrics_for_date`
  (yet another model) at `intelligence/tasks.py:1462-1495`.
  Isolated from core + intelligence bridges. Fourth revenue
  representation.
- **Attribution vs Forecasting**
  (`impact.py::MultiTouchAttributor.attribute_recent` vs
  `ops_autopilot/revenue.py::RevenueOrchestrator.
  get_revenue_forecast`) — distinct concerns; attribution =
  post-hoc credit; forecasting = probabilistic projection with
  hardcoded conversion rates. No overlap but parent-doc drift
  named `revenue.py` for both which was misleading.

## 18. Ownership Gaps

- **F.E10 arc-wide ownership gap CONFIRMED HIGH.** Zero
  JobContract, zero AGENT_MAP entry, zero task_routes, no
  dedicated queue. Only PA-tool ownership signal
  (`revenue_tracker_tool`). Cat E owns arc-wide synthesis per
  D28 lock.
- **OpportunityRevenue writer ownership fragmented.** 3 writer
  paths (`views_opportunity.py` + `epa_handlers_tools.py` +
  `OpportunityTask.mark_won`) with different validation +
  side-effect chains. No single writer-side owner.
- **OpportunityOutcome writer ownership** concentrated in
  `OpportunityTask.mark_won/.mark_lost` methods — SINGLE
  ownership signal — good. But 5 readers across ml_scoring_engine
  + tasks_ops + views_opportunity all assume shape.
- **ImpactEvent + ImpactCredit writer ownership** concentrated
  in `impact.py` classes (ImpactCollector + MultiTouchAttributor)
  — SINGLE ownership signal — good. But dependent on F.C6
  dormant beat.
- **RevenueRecord (intelligence-side) ownership** — 1 caller in
  `real_execution_engine.py:106`. No JobContract; no beat;
  conditional invocation only.

## 19. Recommended Future Research

### 19.1 Post-arc design-preparation ADR chain (extends S1403 R.C1 + S1404 R.D6 sequential-ADR pair-design discipline)

The Group 1400 arc now has a **5-node sequential ADR chain**:

1. **R.E-1: Revenue Employee JobContract ADR** (F.E10, HIGH).
   Assign dedicated Revenue Employee under Employee OS. Owns
   revenue lifecycle end-to-end: create/track/attribute/
   summarize/forecast. Dedicated Celery queue.

2. **R.E-2: View-file consolidation ADR** (F.E5, HIGH). Merge
   `views_revenue.py` + `views_revenue_tracking.py` into a
   single unified surface. Retain `views_revenue_analytics.py`
   as distinct analytics surface. Retire duplicate endpoints
   with grace period + URL redirects.

3. **R.E-3: Dual-representation reconciliation ADR** (F.E3, HIGH;
   scope revised per Rigby cycle 1 Batch 1 framing refinement).
   Two-part ADR: **(3a) Framing decision** — is the parallel schema
   intentional (Rigby cycle 1 alternative interpretation) or drift
   (original F.E3 framing)? Chris ratifies. **(3b) Remediation
   depending on 3a outcome**: if drift → build integration wiring
   (post_save RevenueRecord → core Revenue); if intentional →
   document source-of-truth hierarchy + reconciliation policy +
   analytic-query axis rules. Bundle 3b implementation with F.E5
   view-file consolidation.

4. **R.E-4: F.E1 STATUS_CHOICES cleanup ADR** (arc-wide, 3 models).
   Decision matrix: prune vs implement vs leave. Bundle with
   S1499 xx99 synthesis.

5. **R.E-5: F.E2 phantom-field fix PR** (LOW-effort, high-value).
   Single PR with 4 file:line edits. Post-arc. Sibling to
   S1402 NH-1 nice-to-have discipline.

6. **R.E-6: F.C6 `run_ops_autopilot` enable-decision ADR** (from
   S1403). Cat E adds the attribution-debt + revenue-pipeline
   HAI-write angles as inputs to that decision. Cross-arc: land
   as separate ADR outside Group 1400 per S1403 Rigby Q1 lean.

7. **R.E-7: `intelligence/revenue_integration.py` completion or
   scope-reduction ADR** (T.E7).

Sequential-dependency graph:
- R.E-3 (dual-representation) BLOCKS R.E-2 (view consolidation).
- R.E-2 BLOCKS R.E-1 (Employee JobContract needs single
  ownership surface).
- R.E-4 + R.E-5 are independent quick wins.
- R.E-6 is orthogonal (cross-arc).
- Chain: R.E-5 (independent) + R.E-3 → R.E-2 → R.E-1 → R.E-4 →
  R.E-7.

### 19.2 S1499 xx99 arc-wide synthesis inputs

- Consolidate F.D4 + F.E7 into single "Revenue → HumanAttention
  interlock" narrative: code exists at 6 core.py sites; runtime
  dormancy via F.C6.
- Consolidate F.D10 + F.E1 into single "over-modeled
  STATUS_CHOICES" pattern arc-wide (3 models, 16 declared, 6
  reachable, 10 unreachable).
- Merge F.E3 (Revenue dual-rep) with S1401 D6 (Opportunity
  dual-rep) into single "dual-representation drift" arc-wide
  pattern.
- F.E10 arc-wide ownership synthesis is Cat E's designated
  contribution to xx99 per D28.

### 19.3 Downstream integration signals

- **Learning bridge signal completion** — `revenue_attribution_
  bridge._generate_insights` should either dispatch to a real
  UnifiedLearningPipeline OR drop the docstring claim. Design
  question: is UnifiedLearningPipeline a real subsystem, or
  aspirational?
- **`_REDIS_URL` in bridge**: unused; either remove or wire up
  a real Redis-backed cache for the bridge.

## 20. Appendix

### 20.1 Frontmatter provenance

- **Session:** 1405 (Group 1400 Revenue Child E — fifth of six
  children + xx99).
- **Chris directive:** "start research group 1405 Child E"
  (short command per playbook §22 default queue + parent §5
  P5 slot).
- **Baseline SHA:** `main @ 2355f5be` (post-S1404 audit + cascade
  PRs #2793 + #2794 merged).
- **Playbook version:** v2 (§11.2 20-section template + §13
  6-parallel-Explore sweep + §14 evidence rules + §15 full-SIGN +
  §16 commit gate + §20.10 anchor-corrections pattern).
- **Research OS version:** v1 (installed at S1279).
- **Anchor: ARCHITECTURE_INDEX** v23 (last bumped at S1404 close;
  §1.26 S1404 row; §8 timeline).

### 20.2 Sub-agent §13 sweep manifest

Six parallel Explore agents dispatched at session open:

| # | Surface | Agent ID | Verdict |
|---|---|---|---|
| 1 | `OpportunityRevenue` schema + writers + readers | a406a9a78b8b6feec | 8-section report; F.E1 + F.E2 seeds |
| 2 | `OpportunityOutcome` schema + writers + readers | a756fdc881722dbb0 | 9-section report; F.E1 + F.E2 seeds |
| 3 | `OpportunityContent` schema + Cat E ownership | a1beec72989e5dea7 | 8-section report; minimal F.E hits |
| 4 | `ops_autopilot/revenue.py` + `impact.py` + ImpactEvent | acd08c23a6ee0efb8 | 8-section report; F.E6 + F.E7 + F.E8 seeds |
| 5 | Attribution bridges (revenue_integration + revenue_tracking + revenue_attribution) | ad9a686e62168845d | 9-section report; F.E3 + F.E9 seeds |
| 6 | 3 view files + 4 frontend routes + beat task | aa0b7ae688c0feb10 | 9-section report; F.E4 + F.E5 + F.E10 seeds |

### 20.3 Parent-Claude verifier-loop pre-SIGN checkpoints

12-checkpoint discipline extended from S1404 (S1404 = 12; S1405
= 12; pattern stable). Every sub-agent CANDIDATE HIGH claim
verified by parent-Claude direct read before drafting the audit
finding.

| # | Sub-agent claim | Verifier method | Result |
|---|---|---|---|
| 1 | Agent 2: `OpportunityOutcome.recorded_at` phantom field | Direct Read `ml_scoring_engine.py:1235-1249` | CONFIRMED — `.filter(recorded_at__gte=cutoff)` at `:1241` |
| 2 | Agent 2: `OpportunityOutcome.actual_outcome` phantom field | Direct Read `event_handlers.py:285-299` | CONFIRMED — `.filter(actual_outcome__isnull=False)` at `:291` |
| 3 | Agent 1: `OpportunityRevenue` `notes=` kwarg phantom field | Direct Read `epa_handlers_tools.py:3580-3599` | CONFIRMED — `notes=arguments.get('notes', '')` at `:3592` |
| 4 | Agent 1: `revenue.metadata` phantom field | Direct Read `epa_handlers_tools.py:3718-3732` | CONFIRMED — `revenue.metadata['linked_content_id']` at `:3729` |
| 5 | Agent 6: 4 frontend routes absent from App.tsx | Direct Grep `frontend/src/App.tsx` for revenue routes | CONFIRMED — 0 matches |
| 6 | Agent 4: attribution algorithm at `impact.py:1233-1290` | Direct Read `impact.py:1230-1294` | CONFIRMED — `_attribute_event` with 70/30 split verbatim |
| 7 | Agent 4: HAI writer at `core.py:2051` (revenue_pipeline) | Direct Read `core.py:2045-2059` | CONFIRMED — `HumanAttentionItem.objects.create(source='ops_autopilot', category='revenue_pipeline')` |
| 8 | Agent 4: HAI writer at `core.py:1673` (attribution_debt) | Direct Read `core.py:1668-1682` | CONFIRMED — `self._create_attention_item(title="Attribution debt…")` |
| 9 | Agent 6: no revenue JobContract | Grep `core/employees/jobs.py` for "revenue" | CONFIRMED — 2 hits, both docstring context only |
| 10 | Agent 6: no revenue AGENT_MAP entry | Grep `core/agent_router.py` for "revenue" | CONFIRMED — 0 matches |
| 11 | Agent 2: `outcome='partial'` zero writers | Broadened Grep for `outcome\s*=\s*['\"]partial['\"]\|` across repo | 2 hits found → both disambiguated to `PilotExecution` model at `tasks.py:6631` + `tasks_misc.py:162`; neither is OpportunityOutcome. **Sub-agent claim UPHELD after direct-read disambiguation** (extends S1404 substring-ambiguous-grep-hits methodology) |
| 12 | Agent 4: `ImpactEvent` + `ImpactCredit` as separate model files | Direct ls | CONFIRMED — `core/models_impact_events.py` + `core/models_impact_credit.py` both exist |

**Result: 12 CONFIRMED, 0 REFUTED, 1 disambiguation (F.E1 partial
outcome false-positive candidates cleared).** Extends S1404
12-checkpoint pattern; adds pattern **broadened-grep with direct-
read disambiguation on model-context ambiguity** (F.E1
`outcome='partial'` hit on `PilotExecution` disambiguated from
`OpportunityOutcome`).

### 20.4 Anchor corrections landing at S1405 commit-time (per §20.10 S1404 pattern)

Two parent-doc anchor corrections land in the same commit as this
audit (per S1404 §20.10 pattern):

1. **F.E4 correction** — parent `docs/research/domains/revenue/
   1400_revenue_domain_scoping.md` §3.E line 431 update:
   REMOVE 4 named frontend routes (`/revenue`, `/revenue-dashboard`,
   `/revenue-opportunities`, `/opportunity-detail`); REPLACE with
   `/analytics` route (calls `/api/v1/analytics/charts/revenue/`)
   + `/intelligence` route (opportunity discovery, does NOT call
   revenue endpoints).

2. **F.E6 correction** — parent §3.E lines 425-433 + §12.1 lines
   1150-1152 update: CHANGE "revenue attribution algorithm in
   `ops_autopilot/revenue.py`" → "revenue attribution algorithm
   in `core/services/ops_autopilot/impact.py::MultiTouchAttributor.
   _attribute_event:1233-1290` (70% last-touch + 30% assist split);
   `ops_autopilot/revenue.py` contains pipeline forecasting
   engines, NOT attribution."

### 20.5 Arc trajectory statement (draft for S1499 xx99)

**After 5 Group 1400 children (A/B/C/D/E), the arc has converged
on a coherent Revenue-pipeline narrative:**

1. **Discovery layer (Cat A)** works but has 5-consumer-site dual
   representation drift + F1/F2/F3 CANDIDATE HIGH cluster.
2. **Outreach layer (Cat B)** has drafts, no outbound channel
   (F.B1 CONFIRMED HIGH); cadence declared but not realized
   (F.B4).
3. **Engagement layer (Cat C)** has schema present but ingestion
   missing (F.C1 CONFIRMED HIGH CODE + RUNTIME LOCAL); session-
   aggregation axis WORKING (code) + DORMANT (runtime).
4. **Meeting + Close layer (Cat D)** has code but zero runtime
   locally (F.D1); ClosePack state machine PARTIAL (F.D10:
   sent/won/lost unreachable); arc-wide HAI missing empirically
   (F.D4).
5. **Attribution + Analytics layer (Cat E)** has attribution
   algorithm working end-to-end (F.E8 + F.E6); but revenue
   source-of-truth is fragmented across 3 disconnected
   pipelines (F.E3); duplicate view files (F.E5); phantom-field
   bugs (F.E2); arc-wide over-modeling (F.E1 extends F.D10);
   HAI writers exist in code but runtime-dormant (F.E7 refines
   F.D4); runtime owner absent (F.E10).

**S1499 xx99 unified remediation plan candidates:**
- **Track 1 — Activate revenue lifecycle:** F.B1 (delivery ADR)
  → F.C1 (ingestion ADR) → F.D6 (HAI interlock ADR) → F.E3
  (dual-representation reconciliation ADR) → F.E2 (phantom
  cleanup PR).
- **Track 2 — Assign runtime owner:** F.E10 (Revenue Employee
  JobContract ADR).
- **Track 3 — Enable governance interlock:** F.E7 (`run_ops_
  autopilot` enable-decision ADR, cross-arc per S1403 Rigby Q1
  lean).
- **Track 4 — Consolidate presentation surface:** F.E5 (view-
  file consolidation ADR, blocks R.E-3).
- **Track 5 — Cleanup over-modeling:** F.E1 (arc-wide 3-model
  STATUS_CHOICES cleanup, deferred to xx99).

### 20.6 Nice-to-haves recorded for post-arc pickup

- **NH-E1:** F.E5 `views_revenue_tracking.py` — add docstrings
  to 4 class-based views (cheap fix).
- **NH-E2:** F.E9 `revenue_attribution_bridge.py:1-16` docstring
  correction — remove UnifiedLearningPipeline claim OR wire up
  a real pipeline.
- **NH-E3:** T.E5 `_REDIS_URL` unused dead-import cleanup in
  `revenue_tracking_bridge.py:18`.
- **NH-E4:** F.E7 `ops_autopilot/revenue.py` module docstring
  correction (line 213: "All actions create HumanAttentionItem"
  only true at dispatch layer).
- **NH-E5:** `calculate_daily_revenue_metrics` docstring update
  ("Runs daily at midnight" → "Runs at 12:15 AM Denver").

### 20.7 §10 Meta-methodology extension notes (retrofit at S1499)

Per feedback rule `feedback_xx99_meta_methodology_section.md`,
S1499 canonical summary must include §10 "What This Research
Taught Us About How to Do Research" with 5 subsections.
Preliminary notes for S1499 inheritance:

- **What worked:** 12-checkpoint verifier-loop; broadened-grep
  with disambiguation (S1404 pattern + S1405 model-context
  disambiguation on `PilotExecution` vs `OpportunityOutcome`);
  6-parallel-Explore §13 sweep on discrete evidence surfaces;
  §20.10 anchor-corrections pattern (2 corrections this
  session, both cheap).
- **What to codify into playbook v3:** consider extending §11.2
  20-section template to formalize anchor-correction section as
  a required section when parent-doc drift is caught (currently
  under §20 Appendix). Two triggers now (S1404 §20.10 + S1405
  §20.4).
- **Anti-patterns to avoid:** don't trust parent-doc file-path
  claims without direct verification (F.E4 + F.E6 both were
  parent-doc drift). Don't skip runtime-liveness probes when
  the audit spans PA-tool paths (F.E2 phantom fields would fire
  the moment those paths execute — the tables being empty
  today doesn't mean the bugs are latent forever).

### 20.8 Environment coverage

| Env | Verifier method | Coverage |
|---|---|---|
| LOCAL (dev) | Not run this session per D43 minimal-blocking lean; F.D1 empirical pattern inherited (Revenue tables likely empty locally) | UNVERIFIED |
| PROD | Not probed per D43; T.C8(c) inherited from S1403 (no PA_DB_HEALTH_RPC_URL config) | UNKNOWN |
| CI | Not applicable | N/A |
| Code layer (main @ 2355f5be) | Direct-read of all F.E claim sites; 12/12 verifier-loop CONFIRM | COMPLETE |

### 20.9 Rigby SIGN cycle log

**Cycle 1 (partial) — SIGN-with-edits, confidence Medium-High
(constrained by Batch 1 scope), Batch 1 substantive pressure-test
delivered; Batches 2-3 blocked by Rigby worker instability.**

**SIGN pin log:**
- **First SIGN pin** `pa-4bdd5ad264674ce8` (minted mid-S1405; two
  substantive Rigby turns; second turn stalled in placeholder-loop
  pattern claiming lines 0-500 retention despite tool-block showing
  full-doc read; third turn generic-errored; pin retired at
  `updated_count: 10`).
- **Second SIGN pin** `pa-637331c5f9574a10` (batched retry per D44
  Chris ratification; Batch 1 substantive pressure-test delivered
  on F.E1 + F.E2 + F.E3; Batches 2-3 generic-errored on retry;
  pin retirement queued at S1405 close per D45 Chris ratification
  option (ii)).

**Batch 1 Rigby pressure-test (verbatim intake):**
- **F.E1:** HIGH confidence tech-debt / integrity issue. Three
  potential nuances (read-only enums, external mutation, legacy
  freeze) that could soften severity — but 3-model combination +
  large unreachable share + ClosePack precedent make "intentional"
  implausible without explicit ADR/comment trail. Unreachable
  states create false affordances for analytics + UI filters.
  **Verdict: CONFIRMED HIGH stands.**
- **F.E2:** STRONG. Canonical "latent crash" class. Each subcase
  has predictable exception type (FieldError × 2, TypeError,
  AttributeError). Only possible gotchas: dynamic properties /
  aliased imports (unlikely for Django ORM filter + `.create`
  kwarg). "Blast radius LOW-TO-ZERO currently" is plausible per
  F.D1 pattern, but severity remains high because bug is
  deterministic when triggered. **Verdict: MUST-FIX before
  canonical unless proven dead code.**
- **F.E3:** Classic architecture drift. Potential intentionality:
  `RevenueRecord` could represent external attribution ingestion
  while core `Revenue` represents finalized accounting truth. If
  intentional, gap reframes from "missing integration" to
  "missing explicit contract + mapping + source-of-truth rules".
  Absence of declared source-of-truth hierarchy + multiple writers
  implies inevitable analytic inconsistencies. **Verdict:
  CONFIRMED HIGH with framing refinement folded at S1405
  commit-time (see §14.3 above + §19 R.E-3 scope revision).**

**Batches 2-3 status:** DEFERRED to follow-up SIGN addendum per
D45 Chris ratification. F.E4 + F.E5 + F.E6 + F.E7 + F.E8 + F.E9 +
F.E10 have parent-Claude 12/12 verifier-loop confirmation but no
Rigby pressure-test yet. When Rigby SIGN worker stabilizes, retry
Batches 2 (F.E4-F.E6) + 3 (F.E7-F.E10) as follow-up.

**Cycle 1 must-fix (blocking cycle 2 SIGN-clean OR follow-up SIGN
addendum):**
- **MF1 (F.E2):** Treat all 4 phantom-field references as
  MUST-FIX before canonical. Bundle into single low-effort PR
  post-arc. If any of the 4 code paths is actually dead code,
  document that with `feedback_verify_before_deleting_dead_code.md`
  cross-references and remove the reader/writer. If live,
  correct the field name to match schema.
- **MF2 (F.E3):** Fold framing refinement — landed in this commit
  at §14.3 + §19 R.E-3 scope revision (COMPLETED at commit-time).
- **MF3 (F.E1):** Rigby's 3 potential-nuance exceptions
  (read-only enum / external mutation / legacy freeze) need
  disambiguation for each of the 3 models before R.E-4 STATUS_CHOICES
  cleanup ADR lands. **Fold at commit-time (below):** each of
  ClosePack + OpportunityRevenue + OpportunityOutcome should be
  probed for: (a) any admin/mgmt-command writer paths beyond code;
  (b) any documented intent to freeze legacy states; (c) any ADR
  or comment establishing the choices as read-only enum. If none,
  R.E-4 remediation defaults to "prune unreachable states."

**Cycle 1 nice-to-haves (advisory, from Batch 1):**
- **NH-B1:** F.E1 severity framing could be split by model —
  ClosePack (S1404 F.D10, already CONFIRMED HIGH) vs new
  OpportunityRevenue/OpportunityOutcome (S1405 F.E1). Consider
  whether they're one arc-wide finding or three separate
  same-shape findings for xx99 synthesis granularity.
- **NH-B2:** F.E2 add a diagnostic "runtime probe" step at
  post-arc: when Revenue tables get their first row locally
  (from real testing or manual insertion), run the 4 code paths
  once to confirm the exceptions actually fire — turns "latent"
  into "empirically confirmed live bug" for stronger MUST-FIX
  justification.

### 20.10 Anchor corrections to upstream parent

See §20.4 above. Two corrections land in the same commit as this
audit:
1. Parent §3.E frontend-routes list (F.E4).
2. Parent §3.E + §12.1 attribution-algorithm location (F.E6).

Rigby cycle 1 Q1 + Q2 leans expected to ratify both corrections
per S1404 discipline.

### 20.11 Arc trajectory statement (final draft for S1404 §20.11 continuation)

Per S1404 §20.11 Rigby verbatim inherited trajectory: "With
Categories A/B/C/D now converging on (i) missing Revenue →
HumanAttention approval/interlock, (ii) ownership gaps, and
(iii) runtime-liveness breaks preventing Meeting/ClosePack from
being populated, S1499 should synthesize a single 'activate the
revenue lifecycle + enforce approval/attention gating'
remediation plan."

**S1405 extension:** Category E adds attribution-lens findings
that both confirm and refine this trajectory:
- Attribution engine is CODE-COMPLETE end-to-end (F.E8 verifies
  S1274 §2.4 STRONG; F.E6 locates the canonical algorithm at
  `impact.py::MultiTouchAttributor`).
- But attribution is STARVED at the source (Revenue tables
  empty locally per F.D1; ClosePack states unreachable per
  F.D10 → OpportunityRevenue/OpportunityOutcome extend the
  over-modeling pattern per F.E1).
- Governance interlock CODE-EXISTS at 6 core.py sites (F.E7
  refines F.D4) but RUNTIME-DORMANT via F.C6 (`run_ops_autopilot`
  deferred beat).
- Revenue write path is FRAGMENTED across 3 disconnected
  pipelines (F.E3 core + intelligence + `calculate_daily_
  revenue_metrics`); duplicate view files reinforce
  fragmentation (F.E5).
- No runtime owner arc-wide (F.E10 confirms S1274 §14 #36 at
  code layer).

**S1499 unified plan** should combine "activate lifecycle +
approval gating" (S1404 §20.11) with "consolidate revenue write
path + assign runtime owner + fix phantom-field bugs" (S1405).

---
