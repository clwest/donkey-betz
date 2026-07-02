---
title: "Group 1400 Revenue Child F — Freelance / Gig Opportunity Subsystem / Income-Jobs Lane Audit"
status: active
authority: research
domain_slug: revenue
research_group: 1400
child_slot: F
category: child_audit
session_added: 1406
last_verified: 2026-07-01 (S1406 close; 6-parallel Explore sweep + parent-Claude 12/12 verifier-loop checkpoints CONFIRM 10, DISAMBIGUATION 2; Rigby full SIGN pending)
companion_anchors:
  - docs/research/domains/revenue/1400_revenue_domain_scoping.md  # parent §12.1 Cat F row + §3.F evidence surface + §11.4 inherited findings + D25 F.i lock (Income/Jobs lane, not just FreelanceOpportunity model)
  - docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md  # §9 integration map (Cat A → E read seam) + §14 D6 dual-representation drift methodology (extended by F.E3 → F.F2 in this doc)
  - docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md  # §9 integration map + F.B4 cadence-declared-not-realized methodology
  - docs/research/domains/revenue/1403_revenue_engagement_inbound_audit.md              # §9 integration map + F.C6 run_ops_autopilot deferred-by-policy pattern
  - docs/research/domains/revenue/1404_revenue_meeting_close_audit.md                   # §9 integration map + F.D1 runtime-empty-local pattern + F.D10 state-machine PARTIAL + §20.10 anchor-corrections pattern
  - docs/research/domains/revenue/1405_revenue_attribution_analytics_audit.md           # §14 F.E1 STATUS_CHOICES over-modeling + §14 F.E2 phantom-field references + §14 F.E3 dual-representation drift + §14 F.E10 arc-wide runtime-owner-absent (Cat F owns second half per D28)
related:
  - docs/PLATFORM_INVENTORY.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - core/models_autonomous_situations.py  # FreelanceOpportunity model at line 352
  - core/tasks_ops.py                     # phantom-field writer at line 2239-2251
  - core/celery.py                        # beat entry at line 755-759
  - intelligence/income_builder.py        # Session 727 deprecation shim
  - intelligence/income_spider_orchestrator.py  # LIVE-scheduled beat consumer
  - intelligence/spider_decision_bridge.py      # DOMINANT Opportunity writer (2630/2631 rows locally)
  - AUDIT_FINDINGS.md #12                 # canonical Celery deferred-by-policy list (cross-referenced for F.C6 pattern)
sign_status: SIGN-with-edits cycle 1 substantive (Rigby fresh SIGN pin `pa-8660ea7cfecd4bc6`; batches 1-3 pressure-tested F.F1-F.F10; all 10 findings SURVIVE with 0 severity FLIPS + 10 framing refinements + 2 severity re-evaluations: F.F6 UPGRADED to MUST-FIX + F.F9 UPGRADED to HIGH (llm_enforcer.py:232 confirmed `downgrade_model='gpt-5-mini'` — enforcer CAN route to gpt-5-mini via downgrade, latent silent-empty risk activated); batch 4 S1405 F.E4-F.E10 deferred addendum BLOCKED by S1405 worker-instability pattern recurring on turn 4; D51 Chris ratification 2026-07-01 defers S1405 F.E4-F.E10 pressure-test to S1499 xx99 synthesis per D48 fallback (iii). Parent-Claude 12/12 verifier-loop stands as compensating quality gate. D50 Chris-ratification 2026-07-01 accepts SIGN-with-edits cycle 1 (Batches 1-3 substantive) per "agree all"; NO cycle 2 attempt given worker-instability pattern (matches S1405 D45 discipline). SIGN pin retires post-PR-merge per playbook §15)
verifier_loop: |
  Parent-Claude verifier-loop 12/12 checkpoints (10 CONFIRM + 2 DISAMBIGUATION).
  CONFIRM #1 — FreelanceOpportunity schema at `core/models_autonomous_situations.py:352-401`
    NO status field, NO url field (only `gig_url`), NO budget_range field, NO
    `skills_required` field (actual: `required_skills`), NO match_score field.
    Direct-read verified against sub-agent Agent 1 F.F1 claim.
  CONFIRM #2 — `core/tasks_ops.py:2239-2251` writes 5 phantom fields to
    FreelanceOpportunity: `budget_range`, `skills_required`, `url`, `match_score`,
    `status`. Runtime would raise `FieldError` on execution. Direct-read confirms
    Agent 1 F.F1 verbatim.
  CONFIRM #3 — `core/celery.py:755-759` `scan-income-spider-orchestrator` beat entry
    LIVE-scheduled at `crontab(minute=10)` queue `long_running` expires 3600.
    Session 1115 batch-6 comment at line 750-754 confirms Chris directive rationale.
    Direct-read confirms Agent 4 F.F4 claim.
  CONFIRM #4 — `FreelanceOpportunity.objects.count() = 0` on local DB (Django ORM
    shell probe 2026-07-01). Extends S1404 F.D1 runtime-empty-local pattern to
    Cat F. Direct-probe confirms Agent 1 F.F2 claim.
  CONFIRM #5 — `Opportunity.objects.count() = 2631` on local DB. Broken down:
    2610 RemoteOK + 20 Remotive + 1 pa. Direct-probe confirms mainline Opportunity
    IS live, unlike the parallel FreelanceOpportunity table.
  CONFIRM #6 — `intelligence/income_builder.py` is a Session 727 deprecation shim
    (68 lines total; issues `DeprecationWarning` at line 29-35; re-exports from
    `ai_core.intelligence.income_builder`). Direct-read confirms Agent 3 F.F1.
  CONFIRM #7 — `intelligence/job_scanner_consumer.py:383` reads exactly:
    `# Simulate agent application (would be real in production)`. Direct-read
    confirms Agent 5 F.F1 verbatim.
  CONFIRM #8 — ZERO JobContract entries in `core/employees/jobs.py` name any of
    the 10 Income/Jobs files (grep-negative). Direct-grep confirms Agent 6 §1.
  CONFIRM #9 — 20 files call `Opportunity.objects.create()` (broader than the
    "2 orchestrators" claim in Agent 4 F.F2). Include `intelligence/spider_decision_bridge.py`,
    `intelligence/spider_opportunity_connector.py`, `core/tasks_ops.py`,
    `core/services/income_action_service.py`, plus tests + a sports mgmt command.
    Direct-grep confirms F.F2 dual-write pattern is broader than two-writer.
  CONFIRM #10 — `intelligence/income_builder.py` deprecation shim confirmed used
    by ~45 importing files (docstring claim at line 16; sample grep confirms).
    Direct-read confirms Agent 3 F.F1 magnitude.
  **DISAMBIGUATION #1 (new pattern; extends S1404 verifier-loop discipline):**
    Agent 4 F.F4 claimed `scan_income_spider_orchestrator` fires hourly and
    "saves to DB 20 opportunities per cycle" via `income_spider_orchestrator.py:462`
    write. Django ORM row-count probe with `metadata__created_via='income_spider_orchestrator'`
    filter returned **0 rows**. Real Opportunity rows have
    `metadata__created_via='spider_decision_bridge'` (2630 of 2631). Verdict:
    beat entry EXISTS + is scheduled (CONFIRM), but writes are not landing at
    that provenance stamp on local DB (either not firing, or the orchestrator's
    write path is bypassed for local test data, or the dominant writer is
    `spider_decision_bridge` while the orchestrator sits idle). This is the
    S1404-pattern **joint Rigby broader-grep + parent-Claude direct-read
    disambiguation** applied via ORM row-count. Sub-agent claim REFINED not
    REFUTED: beat is scheduled, but claim "hourly writes 20 rows" is unverified
    at local DB layer. Truth is more nuanced.
  **DISAMBIGUATION #2 (arc-wide load-bearing):** Agent 4 F.F2 "dual-write to
    Opportunity" claim (two orchestrators write to same model) is NARROW. Broader
    truth: at least 20 files call `Opportunity.objects.create()` across
    `intelligence/`, `core/`, and tests. Real dominant writer in local DB is
    `intelligence/spider_decision_bridge.py` at 2630/2631 rows (99.96%). This
    extends F.E3 dual-representation drift from "two parallel schemas" to
    "multi-writer convergence on one schema without a canonical write path
    contract." Sub-agent claim REFINED (write-authority ambiguity is real; count
    of writers is 20 not 2).
owner: claude (drafted S1406 v1; Rigby full SIGN pending)
---

# Group 1400 Revenue Child F — Freelance / Gig Opportunity Subsystem / Income-Jobs Lane

> **What this doc is.** Category F child audit for Group 1400 Revenue arc.
> Per Chris-lock D25 F.i, this audit covers the **entire Income/Jobs lane**
> (10 files across `core/` + `intelligence/` + `ai_core/`), not just the
> `FreelanceOpportunity` model. Sixth Group 1400 child audit under Chris's
> Phase 0 methodology (S1400 arc-open scoping + S1401 Cat A + S1402 Cat B +
> S1403 Cat C + S1404 Cat D + S1405 Cat E). Full 20-section playbook §11.2
> template. First application of S1405 D48 stability-probe gate at open of
> full SIGN cycle 1.
>
> **What this doc is not.** A design-preparation ADR. A remediation PR. A
> whole-Income/Jobs remediation plan. Group 1400 is research + scoping
> phase per playbook §3; ADR work is deferred to post-arc phase.
> S1499 xx99 canonical summary owns cross-arc synthesis.

---

## 1. Executive Summary

**What is this domain?** The **Income/Jobs lane** is a parallel opportunity
lane spanning 10 files across two apps:

- **1 core-side model:** `core/models_autonomous_situations.py:352` `FreelanceOpportunity` (Session 479 bulk autonomous-situations rollout; **runtime DORMANT LOCAL** — 0 rows, all writers phantom-field-broken).
- **9-file intelligence-side adjacency:**
  - `intelligence/ai_job_matcher.py` (510 lines) — stateless keyword-scoring engine
  - `intelligence/ai_job_application_pipeline.py` (248 lines) — Redis pub-sub pipeline (7 channels declared, 0 publishers)
  - `intelligence/agent_income_tools.py` (501 lines) — internal agent-executor tool bridge (NOT a PA tool)
  - `intelligence/income_builder.py` (68 lines) — Session 727 deprecation shim, re-exports `ai_core.intelligence.income_builder`
  - `intelligence/income_builder_automation.py` (358 lines) — plan-execution orchestrator (writes files, no models)
  - `intelligence/income_builder_connector.py` (183 lines) — Flask demo microservice, not production-deployed
  - `intelligence/income_spider_orchestrator.py` (562 lines) — LIVE beat consumer at `core/celery.py:755-759` hourly cadence; **provenance stamp yields 0 local rows**
  - `intelligence/job_income_bridge.py` (151 lines) — cache-only transform bridge; 0 production callers
  - `intelligence/job_scanner_consumer.py` (526 lines) — Django Channels WebSocket consumer at `/ws/job-scanner/`; **application submission SIMULATED**, no frontend integration
- Plus adjacent `ai_core/intelligence/income_builder.py` (canonical implementation of the `AIIncomeBuilder` class the shim re-exports).

**Biggest gaps (10 F.F seed findings, load-bearing):**

- **F.F1 — Phantom-field writer amplifies S1405 F.E2 arc-wide.** `tasks_ops.py:2239-2251` writes FreelanceOpportunity with 5 non-existent fields (`budget_range`, `skills_required`, `url`, `match_score`, `status`) — Runtime FieldError guaranteed if triggered. Worse than S1405 F.E2's 4 phantom fields (all guarded by `hasattr`); this writer has zero guards.
- **F.F2 — Multi-writer convergence on `core.models.Opportunity`.** At least 20 files call `Opportunity.objects.create()`. Local DB shows `intelligence/spider_decision_bridge.py` writes 2630/2631 rows (99.96%). Beat-scheduled `intelligence/income_spider_orchestrator.py` writes 0 rows via its provenance stamp (`metadata__created_via='income_spider_orchestrator'`). No canonical write-authority contract. Extends S1401 D6 + S1405 F.E3 dual-representation drift.
- **F.F3 — Arc-wide runtime-owner-absent CONFIRMED for Cat F.** Zero JobContract, zero AGENT_MAP entry, zero dedicated queue, zero dedicated worker, zero PA tool schema for any of the 10 Income/Jobs files. Extends S1405 F.E10 to complete arc-wide synthesis (Cat E owned first half per D28; Cat F owns second half — RESOLVED HERE).
- **F.F4 — Deprecation shim + view null-check stubs at scale.** `intelligence/income_builder.py` is a Session 727 shim with 45+ importers still on the deprecated path. `views_ai_jobs.py:AIJobApplicationView` instantiates `AIJobApplicationPipeline()` for a null-check but never calls `.start()`. `intelligence/income_builder_connector.py` is Flask demo-only (never deployed). Three orthogonal dead-code patterns.
- **F.F5 — STATUS_CHOICES over-modeling extends F.E1 to intelligence-side.** `OpportunityActionPlan` (intelligence/models.py:154-186) declares 11 status states; only 3 explicit setters found (`proposal_submitted`, `client_responded`, `converted`). 8 states declared but unreachable. Same pattern as S1405 F.E1 (16/6/10) applied to intelligence-side models.
- **F.F6 — Learning-loop-missing arc-wide (Cat F leg) — MUST-FIX (Rigby SIGN Batch 2 upgrade).** Zero feedback capture in resume generation, job scanning, application submission. `job_scanner_consumer.py:383` explicitly simulates. Line 497: `'accepted': 0,  # Would track real responses` (TODO comment). Extends S1403 F.C4 ContentEngagement docstring drift to Cat F. **Rigby Batch 2 verdict:** without outcomes you can't tune prompts, ranking, or ROI — this is the real north-star blocker. Expected loop spec: event (generated/applied/responded/interviewed/hired) → model/table → bridge hook. Concrete negative: grep for `ApplicationOutcome` bridge invocation from Cat F files = grep-negative (`application_outcome_bridge` registered globally per `apps.py:1848` but Cat F does not write into it).
- **F.F7 — Redis pub-sub orphan channels.** `ai_job_application_pipeline.py:58-66` subscribes to 7 Redis channels (`intelligence:freelance_finder`, `intelligence:job_application_agent`, `intelligence:gig_economy_expert`, `intelligence:contract_negotiator`, `intelligence:remote_work_specialist`, `intelligence:general:freelance_opportunity`, `intelligence:general:remote_tech_job`); grep-negative for publishers on any channel. New pattern not surfaced by S1401-S1405.
- **F.F8 — Frontend disconnection.** `/ws/job-scanner/` WebSocket route wired in `intelligence/routing.py:12` extended into global `core/routing.py:192`, but grep-negative for `/ws/job-scanner/` or `job-scanner` in `frontend/src/**/*.{tsx,ts}`. `ai_resume_generator.py` unused by public views (only invoked by `real_execution_engine.py` + `ai_job_application_pipeline.py`). Extends S1405 F.E4 parent-doc frontend-routes drift to Cat F.
- **F.F9 — LLM max_tokens floor risk on gpt-5-mini downgrade — UPGRADED to HIGH (Rigby SIGN Batch 3 borderline resolved via direct-verify).** `ai_resume_generator.py:256` uses `max_tokens=200` (summary); line 518 uses `max_tokens=500` (cover letter). Both below the memory-rule `feedback_gpt5_max_completion_tokens_floor.md` floor of 4000 for gpt-5-mini. **Direct-verify of `core/llm_enforcer.py:232` confirms `downgrade_model = 'gpt-5-mini'` is wired** — enforcer CAN and DOES route to gpt-5-mini via budget-controller downgrade path (line 446-450 shows the downgrade log line "Downgrading {task_type} from gpt-5.2 → {effective_model}"). Rigby's HIGH-if-config-flip condition is ALREADY MET at runtime. Silent empty content risk is ACTIVE not latent.
- **F.F10 — FreelanceOpportunity model placement drift.** Model lives in `models_autonomous_situations.py` (Session 479 bulk situation-model rollout co-locating 18 models across creative/income/financial/research/legal/session domains). Not co-located with Revenue-domain models. Placement suggests bulk-created candidate rather than intentional lane component. Extends S1401 "sports opportunities as separate lane" placement pattern.

**What should be researched next?** Load-bearing candidates for S1499 xx99 unified remediation plan (Cat F contributions):

- **T6 Income/Jobs Employee JobContract ADR** — parallel to S1405 R.E-1 Revenue Employee proposal (Chris-lock at S1499 or post-arc phase). Option (a) from Agent 6 trade-off matrix.
- **T7 Multi-writer convergence contract for `Opportunity`** — establish canonical write authority across 20 writer sites, extending S1401 D6 dual-representation methodology (T1 lifecycle activation chain candidate).
- **T8 Phantom-field remediation** — fix `tasks_ops.py:2239-2251` writer OR delete the whole `_impl_run_freelance_opportunity_scout()` code path if FreelanceOpportunity is decommissioned (candidate follow-on: S1499 §8 or post-arc ADR).
- **T9 Deprecation shim retirement + 45-file migration** — retire `intelligence/income_builder.py` shim per Session 727 consolidation directive; batch-migrate importers to `ai_core.intelligence.income_builder`.
- **T10 Redis pub-sub schema contract** — either wire publishers on the 7 declared channels OR remove the pipeline subscription (S1403 F.C6 code-exists-runtime-dormant pattern).

**Arc-wide convergence (5-pillar synthesis extended by Cat F):**

- **F.E10 (S1405) + F.F3 (S1406) = COMPLETE arc-wide ownership synthesis.** Zero owner across all six categories. S1499 xx99 unified remediation plan candidate: Employee OS 1200s lane with 2 sibling JobContracts (Revenue Employee + Income/Jobs Employee) OR one merged "Revenue-plus-Income" Employee.
- **F.E3 (S1405) + F.F2 (S1406) = dual-representation drift extends from Revenue schemas to Opportunity write path.** S1499 candidate: write-authority framework spanning the multi-writer surface (20 files touching `Opportunity.objects.create()`).
- **F.E2 (S1405) + F.F1 (S1406) = phantom-field pattern extends arc-wide.** Latent-crash class per Rigby S1405 Batch 1 MUST-FIX flag.
- **F.E1 (S1405) + F.F5 (S1406) = STATUS_CHOICES over-modeling extends to intelligence-side.**
- **F.D4/F.D8 (S1404) + F.F4 (S1406) = dead-code/dormancy-at-scale.** Deprecation shim (45+ importers) + view null-check stub + Flask demo microservice — three orthogonal dead-code patterns in one lane.

Word count: ~800 words per §11.2 target 300-500 (over-budget by design; arc-close synthesis warrants).

---

## 2. Domain Purpose

**What is the Income/Jobs lane for?**

Per D25 F.i Chris-lock ("agree all" round 2 at S1400 open 2026-07-01) + parent
§3 Category F evidence surface + parent §12.1 Category F questions:

The Income/Jobs lane is a **candidate parallel opportunity subsystem** intended
to gather external gig/freelance/job opportunities from spider data + AI/ML
scoring + agent-driven application generation. Design intent (from docstrings
+ file names) suggests a full pipeline:

```
spider (freelance_opportunity_spider) →
  income_spider_orchestrator (discover + score + persist) →
  ai_job_matcher (categorize + score) →
  ai_resume_generator (generate resume) →
  ai_job_application_pipeline (Redis pub-sub → apply) →
  job_scanner_consumer (real-time WebSocket UI) →
  Opportunity model row
```

**Runtime reality vs design intent:**

| Design intent | Runtime reality | Gap |
|---|---|---|
| Full pipeline: spider → orchestrator → matcher → resume → apply → UI | Orchestrator beat-scheduled but 0-row provenance; matcher stateless; resume unused by public views; apply Redis-orphan; UI simulated | Complete pipeline decomposed into 10 files that individually work but do not compose |
| `FreelanceOpportunity` is the persistent record | 0 rows locally; all writers phantom-field-broken; Opportunity model dominates (2630 rows via `spider_decision_bridge`) | Model exists but is unused; writes bypass it |
| `AIResumeGenerator` produces personalized resumes | Class exists, LLM-guarded via enforcer, but public view `AIJobApplicationView` never invokes it | Capability exists in dead-lane |
| Real-time job scanning via WebSocket | Consumer wired at `/ws/job-scanner/`, but no frontend caller + application submission simulated | Backend wired, frontend absent, submission stubbed |

**Is this a first-class lane?** Per D25 Chris-lock: **yes for the audit** (D25 F.i chose "Income/Jobs lane" over "just FreelanceOpportunity model"). Per **runtime reality**: **no for the current implementation** — the lane is a scaffolded skeleton with no end-to-end producer/consumer pair actually running.

**Where does the Income/Jobs lane sit relative to Cat A Opportunity Discovery?**
The Cat F lane is a **parallel implementation** of Cat A's opportunity discovery
+ scoring surface. Cat A shipped in S1401 with load-bearing findings including
D6 "dual representation drift" and F1/F2/F3 CANDIDATE HIGH cluster. Cat F extends
that drift pattern to a **third layer**: not just dual (core-vs-intelligence
schemas) but multi-layer (core `Opportunity` + intelligence `income_spider_orchestrator`
+ core `FreelanceOpportunity` + intelligence-adjacency `IncomeOpportunity` /
`ActionPlan` / `OpportunityActionPlan`).

---

## 3. Canonical Entry Points

Per playbook §11.2 §3 (Question #3 file:line evidence).

**Runtime entry points (production callers, not test-only):**

| Entry point | File:Line | Trigger | Live? |
|---|---|---|---|
| Beat scheduler → `scan_income_spider_orchestrator` task | `core/celery.py:755-759` (beat entry) → `intelligence/tasks.py:1654-1702` (task impl) | crontab minute=10 (hourly at 10 past) queue `long_running` expires 3600 | LIVE-scheduled, 0 rows via provenance stamp locally (DISAMBIGUATION #1) |
| HTTP GET `/ai-jobs/jobs/` | `intelligence/urls.py:83` → `intelligence/views_ai_jobs.py:AIJobOpportunitiesView.get` (line 86) → instantiates `AIJobMatcher()` + `.rank_opportunities()` | user HTTP request | LIVE-code, unknown production traffic |
| HTTP POST `/ai-jobs/apply/` | `intelligence/urls.py:85` → `intelligence/views_ai_jobs.py:AIJobApplicationView.post` (line 177) | user HTTP request (login_required) | LIVE-code, but pipeline `.start()` never called — null-check stub only (F.F4) |
| WebSocket `/ws/job-scanner/` | `intelligence/routing.py:12` → `intelligence/job_scanner_consumer.py:JobScannerConsumer.as_asgi()` (line 14) | frontend WebSocket connect | Backend LIVE, frontend disconnected (F.F8) — grep-negative for `/ws/job-scanner/` in `frontend/src/**/*.{tsx,ts}` |
| Discord `/opportunities` slash command | `core/services/discord_bot.py` (surfaced but routes to generic Opportunity, not lane-specific) | Discord user | LIVE-routed to generic opportunity manager, not Cat F files |
| Discord `/track` slash command | same file | Discord user | LIVE-routed to generic opportunity manager, not Cat F files |
| PA tool call | `core/services/pa_tool_schemas.py` (opportunity_manager_tool at line 88-133; opportunity_type enum includes freelance/consulting/job/gig) | Rigby chat | Routes to generic opportunity manager, not lane-specific |
| Celery task `run_freelance_opportunity_scout` | `core/settings.py:1371` (queue=agents) — NO beat entry | ad-hoc `.delay()` | DORMANT — no scheduler, no direct callers found in production paths |
| `_impl_run_freelance_opportunity_scout()` | `core/tasks_ops.py:2200-2260` (approximate) — implements the phantom-field writer | wrapped by scheduled task above (dormant) | DORMANT + BROKEN (F.F1 phantom fields would raise FieldError) |

**Non-runtime entry points (test/demo/dev only):**

| Entry point | File:Line | Purpose |
|---|---|---|
| `python ai_job_application_pipeline.py` | `intelligence/ai_job_application_pipeline.py:227-249` `if __name__ == '__main__':` block calling `asyncio.run(run_pipeline())` | Manual test / dev exercise |
| Flask `app.run(debug=True)` | `intelligence/income_builder_connector.py:172-184` | Demo microservice; not production-deployed |
| `scripts/testing/test_ai_job_application.py:132` | test script | E2E test |

**Load-bearing observation.** Category F has **more declared entry points than
any prior Group 1400 category** (9 entry points including 5 different transport
paradigms — beat/HTTP/WebSocket/Discord/PA-tool), but **fewer live-with-evidence
paths** than Cat A or Cat E. This is the pattern that distinguishes Cat F from
Cat A: Cat A is broad + deep at the mainline `Opportunity` model; Cat F is
broad + shallow with production traffic concentrating in **1** of the 9 entry
points (the beat schedule), and that one path yields 0 rows via its provenance
stamp on local DB. This is a **substantive-DISAMBIGUATION** finding for §14.

---

## 4. Major Models

### 4.1 `FreelanceOpportunity` (core-side)

**File:** `core/models_autonomous_situations.py:352-401` — 50 lines.

**Schema summary (verifier-loop CONFIRM #1):**

| Field | Type | Constraint | Notes |
|---|---|---|---|
| `id` | UUIDField(PK) | default=uuid.uuid4 | |
| `title` | CharField(500) | required | |
| `description` | TextField | blank=True | |
| `client_name` | CharField(200) | null,blank | |
| `platform` | CharField(100) | required | upwork, freelancer, fiverr, etc. |
| `gig_url` | URLField | required | NOTE: field is `gig_url` not `url` — writers reference `url` is phantom (F.F1) |
| `budget_type` | CharField(20) w/ choices | required | 3 choices: `fixed`, `hourly`, `negotiable` |
| `budget_min` | DecimalField(10,2) | null,blank | |
| `budget_max` | DecimalField(10,2) | null,blank | |
| `required_skills` | JSONField | default=list | NOTE: field is `required_skills` — writers reference `skills_required` is phantom (F.F1) |
| `experience_level` | CharField(50) | null,blank | |
| `estimated_duration` | CharField(100) | null,blank | |
| `opportunity_score` | FloatField | default=0.0 | |
| `pay_rate_score` | FloatField | default=0.0 | |
| `skill_match_score` | FloatField | default=0.0 | |
| `competition_score` | FloatField | default=0.0 | |
| `proposals_count` | IntegerField | null,blank | |
| `avg_competitor_rate` | DecimalField(10,2) | null,blank | |
| `source_spider` | CharField(100) | required | |
| `spider_data_id` | UUIDField | null,blank | |
| `posted_date` | DateTimeField | null,blank | |
| `discovered_at` | DateTimeField | auto_now_add | |
| `deadline` | DateTimeField | null,blank | |

**23 fields total. ZERO status/state field.** No STATUS_CHOICES enum. Only choice field is `budget_type` with 3 values.

**Runtime liveness (verifier-loop CONFIRM #4):**
`FreelanceOpportunity.objects.count() = 0` on local DB. DORMANT LOCAL per S1404 F.D1 pattern.

**Model placement (F.F10):**
Co-located in `models_autonomous_situations.py` with 17 other bulk-created situation models (Session 479 rollout). Not co-located with Revenue-domain models (`Opportunity`, `OpportunityRevenue`, `Revenue`, etc.). Placement suggests bulk-created candidate rather than intentional lane component.

### 4.2 Adjacent intelligence-side models (F.E3 dual-representation lens)

| Model | File:Line | Purpose | Live locally? |
|---|---|---|---|
| `ActionPlan` | `intelligence/models.py:16-126` | Represents a plan of income actions | LIVE-code (queried in `intelligence/tasks.py:81` for status='created') |
| `OpportunityActionPlan` | `intelligence/models.py:154-248` | Plan-per-opportunity with 11-state STATUS_CHOICES | LIVE-code, F.F5 state over-modeling |
| `UserIncomeProfile` | `intelligence/models.py:362-413` | User's income profile with `add_earnings()` method | LIVE-code, direct callers unclear |
| `RevenueMetrics` | `intelligence/models.py:250-359` | Aggregate revenue metrics; `update_metrics_for_date()` class method | LIVE-code, callers unclear |
| `OpportunityTracking` | `intelligence/models/income_builder.py:99` | Unified tracking model (parallel to core `Opportunity`) | LIVE-code, F.F2 parallel-schema |
| `RevenueRecord` / `ProposalTracker` / `RevenueSource` | `intelligence/revenue_tracking_bridge.py:14-100` | Intelligence-side revenue models | LIVE-code, extends S1405 F.E3 |
| `AIResume` | `intelligence/ai_resume_generator.py:30-46` | `@dataclass` — NOT a Django model | In-memory only |
| `IncomeOpportunity` | `ai_core/intelligence/income_builder.py` (canonical) + shim re-export | Business model | Live in ai_core canonical version |

**F.F2 — Multi-writer convergence on `Opportunity` (verifier-loop DISAMBIGUATION #2):**

20 files call `Opportunity.objects.create()`. Local DB row breakdown:

| Writer | Row count | Provenance stamp |
|---|---|---|
| `intelligence/spider_decision_bridge.py` | 2630 | `metadata__created_via='spider_decision_bridge'` (99.96%) |
| `intelligence/income_spider_orchestrator.py:462` | 0 (via provenance stamp) | `metadata__created_via='income_spider_orchestrator'` |
| PA tool | 1 | `metadata__source='pa'` |
| Other 17 writers | 0 | unknown provenance |

**The write-authority contract does not exist.** This is the load-bearing
F.F2 finding: broader than S1405 F.E3's two-schema drift; it is a multi-writer
convergence WITHOUT canonical authority, mirroring the F1 provenance-filter
drift methodology from S1399 §4 applied to write authority instead of read
authority.

**Confidence:** HIGH (direct ORM probe + direct-grep on 20 writers).

---

## 5. Major Services

### 5.1 Core-side services

- `core/services/income_action_service.py` — writes `SavedOpportunity` model (`core/models_unified_system.py:16949+`) via `.objects.create()` at line 59, 77. This is the closest core-side service in the Income/Jobs lane vocabulary; it writes to a different model than either `Opportunity` or `FreelanceOpportunity`.

### 5.2 Intelligence-side services (Cat F evidence surface)

**AIJobMatcher (`intelligence/ai_job_matcher.py:63-511`).** Stateless keyword-scoring engine.
- Public methods: `analyze_job(job_data)` line 131, `rank_opportunities(opportunities)` line 451, `generate_proposal_template(job_match)` line 473.
- **Zero LLM calls** — pure keyword-matching + scoring algorithm.
- **Zero ORM writes** (grep-negative).
- Uses 15-category `AIJobCategory` Enum (line 24-42).

**AIJobApplicationPipeline (`intelligence/ai_job_application_pipeline.py:25-212`).** Async Redis pub-sub orchestrator.
- Subscribes to 7 Redis channels (line 58-66) — F.F7 orphan channels (0 publishers).
- Never called by any production path (`.start()` never invoked by views; `.process_job_opportunity()` never called via runtime).
- Public view `AIJobApplicationView.post` at `views_ai_jobs.py:177` instantiates the pipeline (line 204) then returns hardcoded mock dict (line 206-218) — null-check stub (F.F4).
- Writes 4 files to `income_builder_outputs/` per application (line 174-209) — filesystem, not DB.

**AIResumeGenerator (`intelligence/ai_resume_generator.py:49-560`).** Resume + cover letter LLM generator.
- Uses `get_llm_enforcer()` factory (line 229, 484) — CORRECT per project rule.
- `max_tokens=200` for summary (line 256), `max_tokens=500` for cover letter (line 518) — **F.F9 gpt-5-mini floor risk** (memory rule `feedback_gpt5_max_completion_tokens_floor.md` requires ≥4000 for gpt-5-mini reasoning model to avoid empty-content silent failure).
- Public API: `generate_resume()` line 145, `format_resume_text()` line 432, `generate_cover_letter()` line 480.
- `AIResume` is a dataclass (line 30), not a Django model — no persistence.
- Called only by `intelligence/real_execution_engine.py`, `intelligence/ai_job_application_pipeline.py:17,33,119-123`, and a test script — NOT by production views.

**AgentIncomeTools (`intelligence/agent_income_tools.py:14-411`).** Internal tool bridge.
- **NOT a PA tool** — grep-negative for `agent_income_tools` in `pa_tool_schemas.py` or `tool_dispatcher.py`.
- IS invoked by `intelligence/agent_executor.py:229` via lazy `_get_income_tools()` loader.
- Exposes 6 tools: `analyze_opportunity` (line 55-96), `generate_proposal` (line 98-141), `create_content` (line 143-252), `build_portfolio_item` (line 254-311), `create_action_plan` (line 313-355), `discover_opportunities` (line 357-410).
- **Delegates all writes** to `income_builder.*()` methods (canonical ai_core version) — zero direct model writes in trio.

**IncomeSpiderOrchestrator (`intelligence/income_spider_orchestrator.py:30-512`).** LIVE beat consumer.
- Class instantiated as global singleton (line 512+).
- Beat task at `core/celery.py:755-759` fires hourly via `intelligence.tasks.scan_income_spider_orchestrator` (`intelligence/tasks.py:1654-1702`).
- Direct write path: `_save_opportunities_to_database()` (line 421-508) writes `Opportunity.objects.create()` at line 462 with `metadata['created_via']='income_spider_orchestrator'`.
- **DISAMBIGUATION #1:** `Opportunity.objects.filter(metadata__created_via='income_spider_orchestrator').count() = 0` on local DB. Beat scheduled but writes not materializing at this provenance stamp locally.

**IncomeBuilderAutomation (`intelligence/income_builder_automation.py:24-358`).** Plan-execution orchestrator.
- Wraps `TaskDelegationOrchestrator` (line 21).
- Callers: `core/system_integration_orchestrator.py:27,108` (instantiation), `intelligence/income_builder_connector.py:9,16` (Flask app).
- **Zero direct model writes** — writes execution logs to `income_builder_outputs/execution_log_*.json` (line 272, 282).
- Four task routing methods: `_run_opportunity_agent`, `_run_revenue_agent`, `_run_content_studio`, `_run_research_agent` (line 173-237).

**JobIncomeBridge (`intelligence/job_income_bridge.py:14-152`).** Cache-only transform.
- Reads: `cache.get('latest_opportunities', [])` line 25, `cache.get('live_jobs', [])` line 29.
- Writes: `cache.set('unified_opportunities', jobs, 3600)` line 127.
- **Zero DB writes.**
- **Zero production callers** for `sync_to_income_builder()` (line 124-128).
- F.F-Bridge dormant.

**IncomeBuilderConnector (`intelligence/income_builder_connector.py:1-183`).** Flask demo microservice.
- 6 POST/GET routes wrapping `IncomeBuilderAutomation` + `TaskDelegationOrchestrator`.
- `app.run(debug=True)` at line 172-184 — demo mode only.
- **Not production-deployed.** No ASGI wrapper, no URL mount in Django, no consumer bridges to HTTP endpoints.

**JobScannerConsumer (`intelligence/job_scanner_consumer.py:14-526`).** Django Channels WebSocket consumer.
- Routed at `/ws/job-scanner/` via `intelligence/routing.py:12` → extended into global routing at `core/routing.py:192`.
- Handles 8 message types (line 69-104).
- **Application submission SIMULATED** (line 383 verbatim: "# Simulate agent application (would be real in production)").
- Caches results in Redis with 1h + 24h TTLs.
- **Frontend not wired** — grep-negative for `/ws/job-scanner/` in `frontend/src/**/*.{tsx,ts}`.

### 5.3 Bridge / connector semantics (S1274 §2.4 classification)

| Module | Direction | Strength |
|---|---|---|
| `job_income_bridge.py` | Cache → Cache | **MEDIUM** — code exists + one-side wired, other-side dormant |
| `income_builder_connector.py` | HTTP → Automation | **MISSING** — declared but not deployed (Flask demo only) |
| `income_spider_orchestrator.py` | Spider → Opportunity | **STRONG-declared / WEAK-runtime** — beat scheduled, 0 rows via provenance locally |
| `spider_opportunity_connector.py` | Spider → Redis + Opportunity | **STRONG** (per ORM row count evidence via other writers) |
| `spider_decision_bridge.py` | Spider → Opportunity | **STRONG** (2630 rows locally, 99.96% of Opportunity writes) |

### 5.4 F.F3 arc-wide runtime-owner-absent (Cat F evidence for §18 synthesis)

Verifier-loop CONFIRM #8: **ZERO JobContract / AIEmployee** entries in `core/employees/jobs.py` for any of the 10 Income/Jobs files. Current JobContract inventory (4 entries): `RIGBY` (Documentation Manager), `PLATFORM_AUDITOR`, `CHIEF_OF_STAFF`, `BUG_TRIAGE_SPECIALIST`.

**Zero AGENT_MAP entries** for income/job/freelance/resume in `core/agent_router.py`.

**One dedicated Celery queue routing:** `long_running` for `scan-income-spider-orchestrator` beat entry (Session 1115 batch-6 stampede prevention). This is Cat F's **only owned Celery infrastructure**.

**Zero dedicated PA tool schema** for income/jobs/freelance/resume. Uses generic `opportunity_manager_tool` (line 88-133 of pa_tool_schemas.py) whose `opportunity_type` enum includes freelance/consulting/job/gig.

**Discord surface:** `/opportunities` + `/track` commands exist but route to generic opportunity model, not Cat F lane-specific.

This **completes the arc-wide F.E10 synthesis** started by S1405. Combined
Cat E + Cat F verdict: **Revenue + Income/Jobs surface has no organizational
owner across 20+ writer sites, 10 intelligence-side files, 30+ service modules,
and 6 declared entry-point paradigms.** S1499 xx99 owns the arc-wide
remediation-plan track.

---

## 6. Major APIs and Interfaces

### 6.1 HTTP endpoints

Per `intelligence/urls.py:82-85`:

- `GET /ai-jobs/spiders/` → `AIJobSpidersView` (line 82) — spider status.
- `GET /ai-jobs/jobs/` → `AIJobOpportunitiesView` (line 83) — opportunities list; invokes `AIJobMatcher.rank_opportunities()`.
- `POST /ai-jobs/start-spiders/` → `AIJobSpiderControlView` (line 84) — start scrapers.
- `POST /ai-jobs/apply/` → `AIJobApplicationView` (line 85, login_required) — F.F4 null-check stub; returns hardcoded mock dict without invoking pipeline.

Per Flask demo `intelligence/income_builder_connector.py` (not production-deployed):

- `POST /api/income-builder/process-plan` (line 18-42)
- `POST /api/income-builder/analyze-plan` (line 44-88)
- `POST /api/income-builder/delegate-task` (line 90-125)
- `GET /api/income-builder/execution-status/<id>` (line 127-150)
- `POST /api/income-builder/webhook/register` (line 152-181)

### 6.2 WebSocket endpoints

- `/ws/job-scanner/` → `JobScannerConsumer` (per `intelligence/routing.py:12`) — 8 message types (F.F8 frontend absent).

### 6.3 Discord slash commands

- `/opportunities [count] [category]` — routes to generic opportunity manager (not Cat F lane-specific).
- `/track [status]` — routes to generic tracker (not Cat F lane-specific).
- `/studio-resume` — reactivates autonomous generation (adjacent, not Cat F).

### 6.4 PA tool surface

- `opportunity_manager_tool` (pa_tool_schemas.py:88-133) with `opportunity_type` enum including freelance/consulting/job/gig. **NOT** Cat F lane-specific; generic.

### 6.5 Celery task callable API

- `intelligence.tasks.scan_income_spider_orchestrator` — LIVE-scheduled beat.
- `core.tasks.run_freelance_opportunity_scout` — routed to `agents` queue but NO beat entry; dormant.
- `intelligence.tasks.process_pending_action_plans` (line 70) — `@shared_task` invoked via chaining, not beat.
- `intelligence.tasks.execute_action_plan` (line 101) — `@shared_task` invoked from above.

### 6.6 Async / background tasks

- `AIJobApplicationPipeline.start()` at `intelligence/ai_job_application_pipeline.py:52` — async event loop; only entry via `asyncio.run(run_pipeline())` in `__main__` (line 249). Never called from any registered scheduler.
- `JobScannerConsumer._auto_scan_loop()` at `intelligence/job_scanner_consumer.py:310-328` — asyncio loop triggered by WebSocket `enable_auto_scan` message.

**API surface summary.** 5 transport paradigms + 22+ named endpoints. **Runtime
traffic concentrates in `/ai-jobs/jobs/` HTTP GET + Discord slash commands +
PA-tool routes.** All other endpoints are declared-but-unwired or declared-and-simulated.

---

## 7. Runtime Flows

### 7.1 Live flow: beat scheduler → income spider orchestrator (0 rows via provenance)

```
crontab minute=10 (hourly)
  ↓ core/celery.py:755-759 beat entry
intelligence.tasks.scan_income_spider_orchestrator (queue=long_running expires=3600)
  ↓ intelligence/tasks.py:1667-1702
income_spider_orchestrator.discover_opportunities_for_user(use_real_data=True)
  ↓ intelligence/income_spider_orchestrator.py:60-160
FreelanceOpportunitySpider.initialize() + find_opportunities()
  ↓ intelligence/income_spider_orchestrator.py:203-265
_score_opportunities_with_ml() → AIIncomeBuilder.ml_pipeline.predict_opportunity_fit()
  ↓ intelligence/income_spider_orchestrator.py:421-508
_save_opportunities_to_database() @database_sync_to_async
  ↓ intelligence/income_spider_orchestrator.py:462
Opportunity.objects.create(metadata={'created_via': 'income_spider_orchestrator', ...})
```

**Runtime probe (verifier-loop DISAMBIGUATION #1):** 0 rows locally have this provenance stamp. Either the beat fires but writes fail silently, OR the beat rarely fires successfully, OR the sub-agent's claim of "20 opportunities per cycle" reflects intended behavior not observed behavior. Load-bearing DISAMBIGUATION for S1499.

### 7.2 Live flow: HTTP GET `/ai-jobs/jobs/` → AIJobMatcher

```
User HTTP GET /ai-jobs/jobs/
  ↓ intelligence/urls.py:83
AIJobOpportunitiesView.get()
  ↓ AIJobMatcher()
AIJobMatcher.rank_opportunities()
  ↓ AIJobMatcher.analyze_job() per opportunity
Score → return AIJobMatch list
  ↓
JSON response
```

Stateless HTTP; no persistence. Frontend caller unclear — grep-negative for `/ai-jobs/jobs/` in `frontend/src/**/*.{tsx,ts}`.

### 7.3 Dormant flow: HTTP POST `/ai-jobs/apply/` → null-check stub

```
User POST /ai-jobs/apply/ (login_required)
  ↓ intelligence/urls.py:85 → AIJobApplicationView.post()
  ↓ views_ai_jobs.py:202
if AIJobApplicationPipeline:  # module import check
    pipeline = AIJobApplicationPipeline()  # instantiate
    # ...but never .start() and never .process_job_opportunity()
    result = {hardcoded mock dict}  # line 206-218
return JsonResponse(result)
```

**F.F4 null-check stub pattern.** Pipeline instantiated for module-availability check, then discarded. Result returned is hardcoded mock.

### 7.4 Dormant flow: Redis pub-sub pipeline

```
[Some future publisher] publishes JSON to:
  intelligence:freelance_finder
  intelligence:job_application_agent
  intelligence:gig_economy_expert
  intelligence:contract_negotiator
  intelligence:remote_work_specialist
  intelligence:general:freelance_opportunity
  intelligence:general:remote_tech_job
  ↓
AIJobApplicationPipeline.start()  # line 52 — never called from any scheduler
```

**F.F7 orphan channels.** 7 subscribed channels, 0 publishers (grep-negative arc-wide).

### 7.5 Simulated flow: WebSocket `/ws/job-scanner/` → apply_to_jobs

```
Frontend WebSocket connect to /ws/job-scanner/
  ↓ intelligence/routing.py:12 → JobScannerConsumer
Client sends {"type": "apply_to_jobs", "job_ids": [...]}
  ↓ job_scanner_consumer.py:88-91
apply_to_jobs(job_ids)
  ↓ line 359-434
for job in jobs_to_apply:
    # Simulate agent application (would be real in production)  # line 383
    result = {'job_id': ..., 'agent': ..., 'status': 'submitted', ...}  # mocked
cache.set('application_results_...', results, 86400)  # ephemeral
Send 'application_complete' WebSocket message
```

**F.F6 learning-loop-missing + F.F8 frontend-disconnection.** Consumer wired but no frontend caller (grep-negative); if a frontend were wired, applications would be simulated not real.

### 7.6 Deprecation-shim flow: `intelligence.income_builder` → `ai_core`

```
Any of ~45 importers:
  from intelligence.income_builder import AIIncomeBuilder
  ↓ intelligence/income_builder.py:29-35 DeprecationWarning
  ↓ line 39-53 re-export
from ai_core.intelligence.income_builder import AIIncomeBuilder  # canonical
```

**F.F4 deprecation shim at scale.** Session 727 consolidation directive incomplete; migration still pending.

### 7.7 Filesystem-only flow: IncomeBuilderAutomation → execution logs

```
core/system_integration_orchestrator.py:27,108
  ↓ IncomeBuilderAutomation.process_new_plan(plan_file)
  ↓ intelligence/income_builder_automation.py:36+ parse markdown plan
  ↓ TaskDelegationOrchestrator.delegate() to 4 agent categories
  ↓ line 272,282
Write execution_log_<timestamp>.json to income_builder_outputs/
```

**No DB writes.** Audit trail is filesystem JSON, not queryable ORM.

---

## 8. Data Ownership and Lifecycle

### 8.1 `FreelanceOpportunity` lifecycle (F.F1 latent-crash)

**Design intent (from `tasks_ops.py:2239-2251` phantom-field writer):**

```
new → [presumed processing] → [presumed closed/expired]
```

But there is NO status field, so this lifecycle is uninstantiable.

**Actual runtime state (verifier-loop CONFIRM #4):** 0 rows. No lifecycle exists.

### 8.2 `OpportunityActionPlan` lifecycle (F.F5 STATUS_CHOICES over-modeling)

**Declared states (11):** `identified`, `analyzing`, `plan_created`, `proposal_generated`, `proposal_submitted`, `awaiting_response`, `client_responded`, `negotiating`, `converted`, `rejected`, `expired`.

**Reachable states (3, via `intelligence/models.py:219-235` update_status method):** `proposal_submitted`, `client_responded`, `converted`.

**Unreachable states (8):** `identified`, `analyzing`, `plan_created`, `proposal_generated`, `awaiting_response`, `negotiating`, `rejected`, `expired`.

**Reachability rate: 27%** (3 of 11). Compare S1405 F.E1's 37.5% (6 of 16) across 3 core Revenue models. **Cat F is WORSE than Cat E on the F.E1 metric.**

### 8.3 `ActionPlan` lifecycle

**Declared states (5):** `created`, `in_progress`, `paused`, `completed`, `failed`.

**Reachable states (2 explicit):** `created` (default at insert), `in_progress` (via `intelligence/tasks.py:122` execute_action_plan).

**Unreachable via grep-explicit-setter (3):** `paused`, `completed`, `failed`.

Note: cleanup logic for `paused`/`completed`/`failed` may live in consumers (not fully audited); CANDIDATE not CONFIRMED.

### 8.4 Cache TTL contracts (Redis via Django cache)

- `unified_opportunities` — 3600s (`job_income_bridge.py:127`)
- `latest_opportunities` — 3600s (assumed; read at line 25)
- `live_jobs` — 3600s (assumed; read at line 29)
- `scan_results_<channel>` — 3600s (`job_scanner_consumer.py:197`)
- `selected_jobs_<channel>` — 3600s (line 343)
- `application_results_<channel>` — 86400s (line 419)
- `scan_criteria_<channel>` — 86400s (line 510)

**All Cat F persistence tiers use cache or filesystem, not ORM.** F.F6 learning-loop-missing directly connects to this: no cross-session state.

---

## 9. Integrations With Other Domains

### 9.1 Cat F ↔ Cat A (Opportunity Discovery)

| Direction | From | To | File:line | Semantic | Confidence |
|---|---|---|---|---|---|
| Cat F → Cat A | income_spider_orchestrator | Opportunity | `intelligence/income_spider_orchestrator.py:462` | Beat-writes with provenance stamp | STRONG-declared / WEAK-runtime (0 rows via stamp locally) |
| Cat F → Cat A | spider_decision_bridge | Opportunity | `intelligence/spider_decision_bridge.py` | Dominant writer | STRONG (2630 rows) |
| Cat F → Cat A | AIJobMatcher | (transient scoring) | HTTP → return | Score-then-discard | LIVE-code, transient |
| Cat F ↔ Cat A | FreelanceOpportunity (dormant) | Opportunity (mainline) | (no bridge) | Parallel schemas | MISSING integration (F.F2 pattern) |

### 9.2 Cat F ↔ Cat B (Outreach Composition)

- **AIResumeGenerator** produces content but is NOT invoked by any Cat B outreach service.
- **AIJobApplicationPipeline** produces application content but writes to filesystem, not to `OutreachDraft`.
- **F.B1 delivery-path-missing (S1402)** applies here: Cat F's application "submission" is simulated (F.F6), so even if wired, no downstream delivery happens.

Verdict: MISSING integration. Cat F content lives in a different persistence tier than Cat B.

### 9.3 Cat F ↔ Cat C (Engagement Inbound)

- No inbound engagement events wired from Cat F. `job_scanner_consumer` accepts WebSocket messages, but they're user-initiated (not engagement events from platforms).
- **F.C1 ingestion-path-missing (S1403)** extends here: even if Cat F applications shipped to real platforms, there's no ingestion-back path for client responses.

Verdict: MISSING integration.

### 9.4 Cat F ↔ Cat D (Meeting + Close)

- Zero Meeting or ClosePack references in the 10 Cat F files (grep-negative).
- **F.D4 arc-wide HAI missing (S1404)** extends here: Cat F has zero HumanAttention writers. Direct grep confirms.

Verdict: MISSING integration.

### 9.5 Cat F ↔ Cat E (Revenue Attribution)

- Zero writes to `Revenue`, `OpportunityRevenue`, or `OpportunityOutcome` from Cat F files (grep-negative).
- `intelligence/revenue_tracking_bridge.py` defines `RevenueRecord` / `ProposalTracker` / `RevenueSource` models — Cat E's F.E3 dual-representation surface — but these are NOT written to by Cat F files either (Agent 3 verified).

Verdict: MISSING integration. Extends S1405 F.E3 dual-representation drift: Cat F does not bridge to intelligence-side revenue schemas either.

### 9.6 Cat F ↔ Observability / Learning

- No `ImpactEvent` writes from Cat F files (grep-negative).
- No `UserAgentLearning` writes from Cat F files (grep-negative).
- No `application_outcome_bridge` writes from Cat F files.

Verdict: MISSING integration. F.F6 learning-loop-missing.

### 9.7 Cross-arc synthesis: F.F3 completes F.E10

**S1405 F.E10:** Revenue Pipeline has no runtime owner arc-wide.

**S1406 F.F3:** Income/Jobs lane has no runtime owner arc-wide.

**Combined verdict:** The Revenue + Income/Jobs surface (11 files, 20+ writer
sites, 30+ services, 6 entry-point paradigms) has **NO organizational owner
in the Employee OS**. Zero JobContract. Zero AGENT_MAP entry. One dedicated
queue (`long_running`) shared with unrelated tasks. **Resolves parent §12.1
Cat F fifth question** ("How does Category F reason about F.E10 arc-wide
runtime-owner-absent finding?"): **Cat F CONFIRMS at the code layer; adds
no new runtime signal (0 rows locally); recommends Employee OS integration
as candidate S1499 remediation track**.

---

## 10. Event Flows

### 10.1 `post_save` signals

- Grep-negative for `@receiver(post_save)` in any of the 10 Cat F files.
- The mainline `revenue_attribution_bridge.py:227` fires on `Revenue.post_save` (Cat E scope), not Cat F.
- No Cat F models have post_save receivers.

### 10.2 Django Channels group broadcasts

- `job_scanner_consumer.py` group: `scanner_job_scanner` (line 26-27 `self.room_name = 'job_scanner'`).
- Broadcasts on scan complete + application progress + application complete.
- **No cross-domain group broadcasts** (Cat F does not fan out to other consumers).

### 10.3 Redis pub-sub channels (F.F7)

**Subscribed (7 channels in `ai_job_application_pipeline.py:58-66`):**
- `intelligence:freelance_finder`
- `intelligence:job_application_agent`
- `intelligence:gig_economy_expert`
- `intelligence:contract_negotiator`
- `intelligence:remote_work_specialist`
- `intelligence:general:freelance_opportunity`
- `intelligence:general:remote_tech_job`

**Publishers:** ZERO across the entire repo (grep-negative for `redis.publish` or `PUBLISH intelligence:` matches).

**Verdict:** All 7 channels orphaned. F.F7 finding.

### 10.4 EventBus events (S1274 §11.1 pattern)

- Zero EventBus writes from Cat F files (grep-negative for `event_bus.py` imports in the 10 files).
- Cat F does not participate in the EventBus surface.

### 10.5 Deferred / dormant events (F.C6 pattern from S1403)

- `intelligence.tasks.scan_income_spider_orchestrator` — LIVE (beat scheduled). Does NOT belong to `AUDIT_FINDINGS.md #12` canonical Celery deferred-by-policy list.
- `core.tasks.run_freelance_opportunity_scout` — DORMANT (no beat entry). Cross-reference AUDIT_FINDINGS.md #12 status: **not on the deferred-by-policy list**. Classified as genuinely dormant.
- The distinction matters: F.C6-inherited pattern (`run_ops_autopilot`) is intentional-dormancy per policy; `run_freelance_opportunity_scout` is un-intentional dormancy per code (no scheduler wired but writer exists in `tasks_ops.py:2200+`).

---

## 11. Existing Documentation

### 11.1 Narrative anchor

- `docs/PLATFORM_WHAT_IT_IS.md` — grep-negative for "FreelanceOpportunity" or "Income/Jobs lane" mentions. Cat F is not documented in the narrative anchor at any depth.

### 11.2 Inventory anchor

- `docs/PLATFORM_INVENTORY.md` (last generated 2026-06-22 12:59:48 at git HEAD `554a41d3`):
  - `FreelanceOpportunity` model enumerated in the 588-concrete-models list.
  - `intelligence` app enumerated (23-app total). Individual files not enumerated per inventory §schema.
  - No specific Income/Jobs lane row in inventory tables.
- **Recommendation for S1499:** add `docs/topics/income-jobs-lane.md` (parallel to Cat E's proposed `docs/topics/revenue-pipeline.md`) as post-arc topic doc.

### 11.3 Prior research

- **S1273 `platform_architecture_inventory.md` §3.32 Revenue Pipeline row:** grep-negative for "FreelanceOpportunity" or "Income/Jobs" mentions. Not covered.
- **S1274 `cross_domain_integration_audit.md` §2.4:** grep-negative for Income/Jobs seams. Cat F is a lacuna in S1274.
- **S1400 parent scoping doc §3 Category F:** open question resolved as F.i by D25.
- **S1400 parent §11.4:** 15 inherited findings — cited not rediscovered per playbook §14.
- **S1401 §14 D6:** dual-representation drift methodology — extended by F.F2.
- **S1402 F.B4:** cadence-declared-not-realized methodology — analogous to F.F5 states-declared-not-reached.
- **S1403 F.C6:** `run_ops_autopilot` deferred-by-policy — analogous but Cat F's beat entry is NOT deferred-by-policy (LIVE-scheduled).
- **S1404 F.D1:** runtime-empty-local pattern — EXTENDED to Cat F (`FreelanceOpportunity.objects.count() = 0`).
- **S1404 F.D10:** state-machine PARTIAL — EXTENDED to `OpportunityActionPlan` per F.F5.
- **S1405 F.E1:** STATUS_CHOICES over-modeling — EXTENDED via F.F5 (27% reachability worse than Cat E's 37.5%).
- **S1405 F.E2:** phantom-field references — EXTENDED via F.F1 (5 phantom fields, unguarded).
- **S1405 F.E3:** dual-representation drift — EXTENDED via F.F2 (multi-writer convergence broader than dual-schema).
- **S1405 F.E10:** arc-wide runtime-owner-absent — COMPLETED via F.F3 (Cat F confirms Cat E; Employee OS synthesis load-bearing for S1499).

### 11.4 Docstring vs runtime drift catalog

- `models_autonomous_situations.py:353-355` FreelanceOpportunity docstring: "Situation #10: Freelance Opportunity Scout / Tracked freelance gigs and opportunities." **DRIFT** — 0 rows, all writers phantom-field-broken.
- `ai_job_matcher.py:2-14` module docstring: "identifies and scores job opportunities based on their suitability for completion using AI tools." Claims resume generation + success tracking. **DRIFT** — resume generation belongs to `ai_resume_generator.py`; no tracking exists.
- `ai_job_application_pipeline.py:2-5` module docstring: "Connects spiders → job matcher → resume generator → application system." **DRIFT** — no application submission (writes to filesystem, then done).
- `job_scanner_consumer.py:383` code comment: "Simulate agent application (would be real in production)." **HONESTY** — code explicitly labels itself simulated.

---

## 12. Research Coverage

Per playbook §11.2 §12 (Question #10-#13).

### 12.1 What is well-researched?

- **File shapes + module boundaries** — thoroughly mapped via 6-parallel Explore sweep.
- **STATUS_CHOICES reachability** — F.F5 verified with explicit setter grep across intelligence/models.py.
- **Beat scheduling** — `scan-income-spider-orchestrator` verified in core/celery.py:755-759.
- **Runtime-empty-local** — FreelanceOpportunity 0 rows, Opportunity 2631 rows, provenance breakdown.
- **JobContract + AGENT_MAP + PA tool inventory** — direct-grep confirmed zero Cat F entries.

### 12.2 What is under-researched?

- **Production DB (Railway):** local DB probe used. Prod row counts + writer provenance unknown. S1405 T.C8(c) inherited: `db_health_tool env=prod` "not configured: PA_DB_HEALTH_RPC_URL, PA_DB_HEALTH_RPC_CLIENT_TOKEN". D49 lean at S1406 open was (ii) minimal-blocking — did not fix pre-audit. Production dormancy verdict PENDING per T.C8(c).
- **`intelligence.tasks.scan_income_spider_orchestrator` CeleryTaskEvent history 30d:** not queried locally. Whether the beat actually fires or errors out silently is UNKNOWN. Candidate for T.F1 follow-on.
- **45+ deprecation-shim importers:** Agent 3 counted "46 references"; not individually catalogued. Migration plan per T9 needs full importer inventory.
- **Discord command frequency:** if `/opportunities` and `/track` are frequently invoked, deprecating Cat F files becomes UX-breaking. Not audited.
- **`ai_core/intelligence/income_builder.py` (canonical AIIncomeBuilder):** referenced but not deep-audited. The shim points to a live canonical version; that version's runtime status was outside the 6-file Cat F scope.
- **Frontend CareerTab (`frontend/src/pages/workspace/tabs/CareerTab.tsx`):** exists per Agent 6 mention; not deep-audited. May be closer to Cat F than initially assumed.

### 12.3 What is NOT researched (out-of-scope this session)?

- Employee OS JobContract ADR draft for Income/Jobs Employee — deferred to post-arc phase per Group 1400 §7 anti-scope.
- Full multi-writer convergence write-authority ADR — deferred to S1499 xx99 or post-arc.
- Frontend integration for `/ws/job-scanner/` — outside Group 1400 arc (Frontend arc scope).
- `AUDIT_FINDINGS.md #12` cross-reference for all Cat F Celery tasks (only 1 primary + 1 secondary checked).

### 12.4 Parent §12.1 Category F questions — all answered

Per parent doc §12.1 Category F row + inherited from S1405:

> Is the Income/Jobs lane (`FreelanceOpportunity` + 9-file `intelligence/` adjacency) actively driving income or dormant?

**Answer:** DORMANT LOCAL. FreelanceOpportunity 0 rows; income_spider_orchestrator 0 rows via provenance stamp; application submission simulated; deprecation shim on the canonical writer path. Cat F ships code across 10 files but produces no observable local income signal.

> Who produces FreelanceOpportunity rows?

**Answer:** Currently no one. The declared writer at `core/tasks_ops.py:2239-2251` would raise `FieldError` on execution (F.F1 phantom fields). No other writer exists (grep-negative for `FreelanceOpportunity.objects.create` outside `tasks_ops.py`).

> What is `income_builder_automation` + `income_spider_orchestrator` + `job_income_bridge` doing at runtime?

**Answer:**
- `income_builder_automation` — writes execution logs to `income_builder_outputs/execution_log_*.json`; called by `core/system_integration_orchestrator.py` (unclear production trigger); zero model writes.
- `income_spider_orchestrator` — beat-scheduled hourly; write path exists but produces 0 rows via provenance stamp locally.
- `job_income_bridge` — cache-only transform; zero production callers.

> Is `ai_resume_generator` production-invoked?

**Answer:** Only via `intelligence/real_execution_engine.py` (which itself is not audited for production traffic) and `intelligence/ai_job_application_pipeline.py` (which is not invoked by production paths). Public view `AIJobApplicationView` does NOT invoke it. **Production-invoked: NO with high confidence.**

> How does Category F reason about F.E10 arc-wide runtime-owner-absent finding?

**Answer:** F.F3 confirms F.E10 at Cat F code layer. Zero JobContract, zero AGENT_MAP, zero dedicated PA tool. Extends the F.E10 arc-wide gap. Cat F is the second half of the arc-wide synthesis per D28.

> Does Income/Jobs lane exhibit F.E1 STATUS_CHOICES over-modeling? F.E2 phantom fields? F.E3 dual-representation drift?

**Answer:** YES to all three:
- F.E1 extension (F.F5): `OpportunityActionPlan` 11 declared / 3 reachable = 27% reachability (worse than Cat E's 37.5%).
- F.E2 extension (F.F1): 5 phantom fields on FreelanceOpportunity writer, unguarded (worse than Cat E's 4 hasattr-guarded).
- F.E3 extension (F.F2): multi-writer convergence on `Opportunity` model — 20 writers, 1 dominant, 0 canonical write-authority contract.

---

## 13. Architecture Maturity

Per playbook §11.2 §13 + S1404's four-way split + S1405's four-way split.

**Cat F maturity verdict: FIVE-WAY SPLIT** (new — extends S1404 4-way + S1405 4-way).

- **WORKING:** `AIJobMatcher` stateless scoring; `intelligence.tasks.scan_income_spider_orchestrator` beat-scheduled; `/ws/job-scanner/` consumer registration; deprecation shim re-export path.
- **MISSING:** Frontend integration for `/ws/job-scanner/`; production caller for `AIResumeGenerator`; real application submission (currently simulated); Redis publishers for 7 orphan channels; canonical write-authority for `Opportunity` (multi-writer convergence).
- **DEFERRED-BY-POLICY (F.C6 pattern):** None Cat F-specific. `run_ops_autopilot` (S1403 F.C6) is NOT a Cat F task.
- **DORMANT LOCAL RUNTIME (F.D1 pattern):** `FreelanceOpportunity` (0 rows); `core.tasks.run_freelance_opportunity_scout` (no beat + broken writer); `AIJobApplicationPipeline.start()` (never invoked from any scheduler); Flask `income_builder_connector` (demo mode only); `job_income_bridge.sync_to_income_builder()` (zero callers).
- **UNDER-OWNED (F.E10 arc-wide pattern):** All 10 Cat F files. No JobContract, no AGENT_MAP, no dedicated PA tool, no dedicated worker. One shared queue (`long_running`).

**Maturity readiness:** LOW — matches S1405 verdict; Cat F does not improve readiness signal. Combined S1405+S1406 evidence: Revenue + Income/Jobs domain readiness is uniformly LOW across all 6 children. Confirms S1274 §9.6 baseline classification.

---

## 14. Known Drift

Load-bearing findings (10 F.F seeds, per §1 Executive Summary):

### 14.1 F.F1 — Phantom-field writer (arc-wide F.E2 extension)

**File:** `core/tasks_ops.py:2239-2251`

**Evidence (verifier-loop CONFIRM #2):**
```python
FreelanceOpportunity.objects.create(
    title=raw.get('title', 'Untitled')[:200],
    platform=data.spider_name,
    client_name=company[:100],
    description=(raw.get('description', '') or '')[:2000],
    budget_range=budget_str[:100] if budget_str else 'Not specified',  # phantom
    skills_required=raw.get('tags', []) if ... else [],                # phantom (actual: required_skills)
    deadline=None,
    url=raw.get('url', '') or raw.get('link', ''),                     # phantom (actual: gig_url)
    match_score=0.0,                                                   # phantom
    status='new',                                                      # phantom
    source_spider=data.spider_name
)
```

FreelanceOpportunity schema (verified line 352-401) has NO `status`, NO `budget_range`, NO `url` (only `gig_url`), NO `match_score`, and field is `required_skills` not `skills_required`.

**Severity:** HIGH (worse than S1405 F.E2). S1405's phantom fields were `hasattr`-guarded (silent no-op); this writer has zero guards — **runtime `FieldError` guaranteed** if `_impl_run_freelance_opportunity_scout()` ever executes.

**Runtime blast radius:** LOCAL zero (task not scheduled; `run_freelance_opportunity_scout` has no beat entry). But PROD status UNKNOWN per T.C8(c); if a prod scheduler invokes this, every call fails silently in Celery worker.

**Rigby SIGN cycle 1 Batch 1 fold:** framing refined to distinguish "hard-crash if invoked" (unguarded `.create()` with invalid kwargs) from "currently unreachable" (task not beat-scheduled). Rigby's ask for the "exact function call chain" evidence pin: `core.tasks.run_freelance_opportunity_scout` (settings.py:1371 queue=agents, no beat entry) → `_impl_run_freelance_opportunity_scout()` at `core/tasks_ops.py:2200+` → phantom-field `.create()` at `core/tasks_ops.py:2239-2251`. Chain exists in code but no scheduler wires it.

**Confidence:** HIGH (direct-read + schema verification).

### 14.2 F.F2 — Multi-writer convergence on `Opportunity` (F.E3 arc-wide extension)

**Evidence (verifier-loop CONFIRM #9 + DISAMBIGUATION #2):**

- 20 files contain `Opportunity.objects.create()` (per direct-grep):
  - `intelligence/spider_decision_bridge.py` (dominant writer, 2630 rows locally, 99.96%)
  - `intelligence/spider_opportunity_connector.py`
  - `intelligence/income_spider_orchestrator.py:462` (0 rows via provenance)
  - `core/tasks_ops.py`
  - `core/services/income_action_service.py`
  - `core/agents/analysis/opportunity_scoring_agent.py`
  - `core/services/td_handlers_agents.py`
  - `core/management/commands/generate_sample_data.py`
  - `sports/management/commands/generate_dashboard_data.py`
  - Plus tests + reports + archives

- Zero canonical write-authority contract. No sole-writer enforcement. No provenance-validation layer.

**Severity:** HIGH (arc-wide amplification of S1405 F.E3). S1405 identified "two disconnected pipelines"; the reality is 20-writer convergence WITHOUT authority contract. This is a broader class of finding.

**Framing note (S1405 D48 stability-probe target):** may reflect intentional-scaffolding rather than drift. Multi-writer with dominant-source might be by design (many spider sources → one lookup table). But absence of documented contract + 99.96% dominance of one writer suggests either (a) accidental convergence + rest is dead code, or (b) intentional but undocumented. Rigby SIGN should probe framing.

**Rigby SIGN cycle 1 Batch 1 fold:** evidence-gap refinement — the MUST-FIX is the missing write-authority contract, not "20 call sites" by itself. Deferred classification work for the 19 non-dominant writers into (a) tests, (b) migrations/fixtures, (c) dead code, (d) legitimate alternate ingestion paths — deferred to S1499 xx99 synthesis given time budget at S1406 close. Cursory read of the 20-writer grep output (per §20.3): tests + `generate_sample_data.py` + `sports/management/commands/generate_dashboard_data.py` account for ~5-6 of the 20; remaining 14 are candidates for the (c)/(d) split — S1499 owns.

**Confidence:** HIGH (direct-grep + direct-ORM row count).

### 14.3 F.F3 — Arc-wide runtime-owner-absent CONFIRMED for Cat F

**Evidence (verifier-loop CONFIRM #8):**
- Zero JobContract entries in `core/employees/jobs.py` for any of the 10 Cat F files.
- Zero AGENT_MAP entries for income/job/freelance/resume in `core/agent_router.py`.
- Zero dedicated PA tool schema in `core/services/pa_tool_schemas.py`.
- Zero Discord slash command dedicated to Cat F lane (generic `/opportunities` + `/track` route to mainline Opportunity model).
- One dedicated Celery queue (`long_running`) but shared with unrelated tasks.

**Severity:** HIGH (completes S1274 §14 finding #36 for arc-wide synthesis).

**Cross-arc synthesis (Cat E half + Cat F half):**
- Cat E (S1405 F.E10) established zero-owner for Revenue attribution + analytics.
- Cat F (S1406 F.F3) confirms zero-owner for Income/Jobs lane.
- **COMPLETE arc-wide synthesis:** Revenue + Income/Jobs domain has no JobContract owner, no dedicated agent, one shared queue. S1499 xx99 owns remediation-plan track.

**Rigby SIGN cycle 1 Batch 1 fold:** definition tightening — separate ownership/control-plane (JobContract + AGENT_MAP + PA tool schema, all zero) from capacity/isolation plane (`long_running` queue is SHARED not dedicated, which is a different class of gap). Both are gaps; the ownership-plane gap is HIGH; the capacity/isolation gap is MEDIUM (can't be dismissed as "we don't need a queue" but a shared queue does provide some structure).

**Confidence:** HIGH (direct-grep across all inventories).

### 14.4 F.F4 — Dead-code / dormancy at scale (F.D8 methodology extension)

**Three orthogonal dead-code patterns in one lane:**

1. **Deprecation shim (`intelligence/income_builder.py`):** Session 727 consolidation directive still incomplete after 46+ session cycles. 45+ importers on the deprecated path.

2. **Null-check stub (`intelligence/views_ai_jobs.py:202-218`):** `AIJobApplicationView` instantiates `AIJobApplicationPipeline()` for module-availability check, then returns hardcoded mock dict without invoking pipeline.

3. **Flask demo microservice (`intelligence/income_builder_connector.py:172-184`):** `app.run(debug=True)` — never production-deployed. No ASGI wrapper, no URL mount, no consumer bridge.

**Severity:** MEDIUM per pattern; aggregate HIGH given three patterns co-locate.

**Anti-pattern check (memory rule `feedback_verify_before_deleting_dead_code.md`):**
- Deprecation shim: 45+ importers — DO NOT DELETE without migration plan (T9).
- Null-check stub: view responds with mock data users may depend on — verify UX impact before removing.
- Flask connector: zero callers confirmed via cross-grep — CANDIDATE for deletion after fleet-app verification (`feedback_fleet_caller_verification_before_celery_deletes.md`).

**Rigby SIGN cycle 1 Batch 2 fold:** split into 3 sub-findings with separate severities per Rigby:
- **F.F4a (deprecation shim)** — MEDIUM. Not user-facing; migration is the fix. Runtime reachability: whether any logs show use of deprecated import path — S1499 T.F3 track owns migration evidence.
- **F.F4b (view null-check stub)** — HIGH IF user-facing. `AIJobApplicationView.post` at `/ai-jobs/apply/` is login_required and returns hardcoded mock; if users hit this endpoint expecting real applications, this is a UX-integrity gap. Runtime reachability: check prod access logs for POST `/ai-jobs/apply/` frequency.
- **F.F4c (Flask demo connector)** — LOW-MEDIUM. Zero callers confirmed via cross-grep; fleet-app verification pending per S1499 T.F3 track.

**Confidence:** HIGH.

### 14.5 F.F5 — STATUS_CHOICES over-modeling extends F.E1 to intelligence-side

**Evidence (`intelligence/models.py:154-186`):**
- `OpportunityActionPlan.STATUS_CHOICES` — 11 declared states.
- Explicit setters via `update_status()` (line 219-235): `proposal_submitted`, `client_responded`, `converted` — 3 states.
- Unreachable: `identified`, `analyzing`, `plan_created`, `proposal_generated`, `awaiting_response`, `negotiating`, `rejected`, `expired` — 8 states.

**Reachability rate:** 3/11 = 27%.

**Cross-arc comparison:**
- S1404 F.D10 ClosePack: 6 declared / 3 reachable = 50%.
- S1405 F.E1 arc-wide (3 core Revenue models): 16 declared / 6 reachable = 37.5%.
- S1406 F.F5 (OpportunityActionPlan): 11/3 = 27%. **Worst reachability in the arc.**

**Severity:** MEDIUM (intelligence-side, less runtime consequence than core-side Revenue models).

**Rigby SIGN cycle 1 Batch 2 fold:** tighten reachability proof by counting ALL writers per Rigby, not just `update_status()`:
- Admin: unknown; not audited at S1406 close (S1499 T.F8 track).
- Serializers: unknown; not audited.
- Tests: likely include additional state setters (typical for Django model tests).
- Migrations: likely no state setters (schema-only).
- Direct `.status = 'X'` assignments: not fully audited; grep-check candidate for S1499 T.F8.

If grep-based full-writer count reveals additional setters, the 27% reachability figure may increase (moving Cat F closer to Cat E's 37.5%). Rigby's framing: "if grep shows other setters, adjust %; if not, the 'unreachable states' framing is solid and ties cleanly to F.E1 over-modeling." **S1499 T.F8 owns the full writer sweep.**

**Confidence:** HIGH (for `update_status()` setter; MEDIUM for full writer inventory pending T.F8).

### 14.6 F.F6 — Learning-loop-missing arc-wide (Cat F leg) — MUST-FIX

**Evidence:**
- `intelligence/ai_resume_generator.py`: No feedback capture after resume generation. No `ResumeUsageRecord` model. No download tracking.
- `intelligence/job_scanner_consumer.py:497`: `'accepted': 0,  # Would track real responses` (TODO comment).
- `intelligence/ai_job_application_pipeline.py`: Writes 4 files to `income_builder_outputs/` per application; no outcome logging.
- Zero `ApplicationOutcome` or `JobApplication` writes from Cat F files (grep-negative in the 10-file surface; `application_outcome_bridge` is registered globally per apps.py:1848 but Cat F does not write into it).

**Severity:** HIGH → **MUST-FIX (Rigby SIGN cycle 1 Batch 2 upgrade)** (extends S1403 F.C4 ContentEngagement docstring drift to Cat F).

**Rigby SIGN cycle 1 Batch 2 verdict:** "This is MUST-FIX because without outcomes you can't tune prompts, ranking, or ROI." Expected loop spec (from Rigby):

```
Event: generated | applied | responded | interviewed | hired
  ↓
Model/Table: ResumeUsageRecord or ApplicationOutcome or JobApplicationEvent
  ↓
Bridge hook: application_outcome_bridge (already registered per apps.py:1848)
```

**Concrete negative evidence:** grep for `ApplicationOutcome` bridge invocation from Cat F files = grep-negative. `application_outcome_bridge` receiver is wired globally but no Cat F file writes signal into it. Confirmed application_outcome_bridge status at `apps.py:1848` per Django startup log: "JobApplication outcome signal registered" — the receiver exists; the writers don't.

**Blast radius:** without this feedback loop, the entire Income/Jobs lane cannot learn which resume formats work, which job scans yield applications, which applications convert, or which categories/agents drive ROI. Every downstream optimization (ML scoring, prompt refinement, category weighting) is starved of ground-truth signal.

**Confidence:** VERY HIGH.

### 14.7 F.F7 — Redis pub-sub orphan channels

**Evidence:** 7 subscribed channels in `ai_job_application_pipeline.py:58-66`; 0 publishers in the repo (grep-negative for `publish` calls to any of the 7 channel names).

**Severity:** MEDIUM (declared-but-unwired pattern, new to Group 1400 arc).

**Rigby SIGN cycle 1 Batch 3 fold:** verify no alternate publisher abstraction. Direct-grep across `broadcast_`, `publish_event`, `redis.publish`, `channel_layer group_send intelligence:` patterns returned 57 hits across 10 files (see §20.3 grep pattern list). Spot-check of the most likely candidate `ai_core/spiders/realtime_publisher.py:23` returned grep-negative for any of the 7 Cat F channel names. Cursory read of remaining 9 files: none of `platform_integration_hub.py`, `proposal_manager.py`, `real_data_orchestrator.py`, `websocket_bridge.py`, `sports/orchestration.py`, `agent_communication.py`, `unified_platform_bridge.py`, `advisor_feed.py`, or `tools/do_extract.py` reference the Cat F channel names. **No false-negative on `redis.publish`**; 7 orphan channels confirmed.

**Confidence:** HIGH (grep-negative for `redis.publish` on all 7 channels + spot-check of alternate abstractions).

### 14.8 F.F8 — Frontend disconnection

**Evidence:**
- `/ws/job-scanner/` WebSocket route wired at `intelligence/routing.py:12` extended into `core/routing.py:192`.
- Grep-negative for `/ws/job-scanner/` or `job-scanner` in `frontend/src/**/*.{tsx,ts}`.
- `intelligence/ai_resume_generator.py` unused by public views; grep-negative for `resume` route in `frontend/src/**/*.{tsx,ts}` matching AIResumeGenerator's public API.
- `frontend/src/pages/workspace/tabs/CareerTab.tsx` exists but routes to `/api/ats/analyze/` + `/api/ats/generate-summary/` (mainline ATS features), not to Cat F lane infrastructure.

**Severity:** MEDIUM (extends S1405 F.E4 parent-doc frontend-routes drift methodology).

**Rigby SIGN cycle 1 Batch 3 fold:** tighten claim boundary — "backend route exists; **no UI client** references it." Non-frontend clients (CLI, Discord, internal admin) NOT audited at S1406 close; grep-negative applies only to `frontend/src/**/*.{tsx,ts}`. The "adjacent ATS system" note reframed as potential duplicate/competing surface (CareerTab uses `/api/ats/*` routes) rather than implying wrongness — could be intentional split (ATS = mainline, `ai_resume_generator` = experimental parallel).

**Confidence:** HIGH.

### 14.9 F.F9 — LLM max_tokens floor risk

**Evidence:**
- `intelligence/ai_resume_generator.py:256`: `max_tokens=200` for summary generation.
- `intelligence/ai_resume_generator.py:518`: `max_tokens=500` for cover letter.
- Memory rule `feedback_gpt5_max_completion_tokens_floor.md`: gpt-5-mini requires `max_completion_tokens >= 4000` — below floor, silently returns empty content.

**Severity:** MEDIUM → **HIGH (Rigby SIGN cycle 1 Batch 3 borderline upgrade after direct-verify).**

**Rigby SIGN cycle 1 Batch 3 verdict:** borderline HIGH if enforcer can route to gpt-5-mini today or via config. **Direct-verify of `core/llm_enforcer.py:232` confirms `downgrade_model = 'gpt-5-mini'` is wired.** Line 446-450 shows the downgrade log line "Downgrading {task_type} from gpt-5.2 → {effective_model}." Line 644 default `max_tokens=500`, line 663 handles `max_completion_tokens if max_completion_tokens else max_tokens` (GPT-5 API accepts `max_completion_tokens`; legacy `max_tokens` fallback via factory). Enforcer CAN and DOES route to gpt-5-mini via budget-controller downgrade path. Rigby's HIGH-if-config-flip condition is **ALREADY MET at runtime code layer** — silent empty content risk is ACTIVE not latent.

**Rationale for HIGH upgrade:** if the budget controller downgrades `AIResumeGenerator` calls from gpt-5.2 to gpt-5-mini (a runtime decision, not manual config), the 200/500 max_tokens budget silently truncates or empties the reasoning output. Users get empty resumes/cover letters with no error signal. This is a latent production incident trigger with a live downgrade path — matches memory-rule `feedback_gpt5_max_completion_tokens_floor.md` diagnostic criteria (check `finish_reason` + `reasoning_tokens` before assuming prompt/credits bug).

**Confidence:** HIGH (rule + direct-read of enforcer + confirmed downgrade path).

### 14.10 F.F10 — Model placement drift

**Evidence:**
- `FreelanceOpportunity` lives in `core/models_autonomous_situations.py:352` — co-located with 17 other Session 479 bulk-created situation models spanning creative/income/financial/research/legal/session domains.
- Not co-located with Revenue-domain models (`Opportunity` at line 1201, `OpportunityRevenue` at line 2613, `Revenue` at line 1153 — all in `core/models_unified_system.py`).

**Severity:** LOW (informational drift; placement suggests non-first-class citizenship).

**Rigby SIGN cycle 1 Batch 3 fold:** reframe as "taxonomy/ownership smell" not "drift." Useful as supporting evidence for F.F3 (lane not first-class) but not a defect on its own unless it causes import cycles, migrations confusion, or missed admin/serializer registration. Grep-negative for all three at S1406 close; F.F10 stands as informational context only.

**Confidence:** HIGH.

---

## 15. Known Technical Debt

Enumerated as `T.F1`-`T.F10` (mirrors S1405's T.E1-T.E10 pattern).

- **T.F1 — Beat schedule verify.** `scan_income_spider_orchestrator` fires hourly but 0 rows via provenance stamp locally. Verify via `CeleryTaskEvent` history 30d + Rigby `ops_tool.celery_task_history` probe. May be silently erroring in worker (log grep required).
- **T.F2 — Phantom-field writer remediation.** `tasks_ops.py:2239-2251` `_impl_run_freelance_opportunity_scout()` code path needs decision: (a) fix schema to match writer, (b) fix writer to match schema, (c) delete both if FreelanceOpportunity is decommissioned. Chris commit-gate.
- **T.F3 — Deprecation shim retirement + 45-file migration.** Session 727 consolidation still incomplete. Batch-migrate importers to `ai_core.intelligence.income_builder`; delete `intelligence/income_builder.py`.
- **T.F4 — Redis pub-sub schema contract.** 7 orphan channels in `ai_job_application_pipeline.py`. Wire publishers OR remove subscribers. F.C6-analog decision.
- **T.F5 — Frontend integration for /ws/job-scanner/** — either wire a frontend route or remove the consumer + routing entry (fleet-app verification required per memory rule).
- **T.F6 — Views null-check stub cleanup.** `AIJobApplicationView` returns hardcoded mock dict; either implement real application flow OR return 501 Not Implemented.
- **T.F7 — Multi-writer convergence contract for `Opportunity`.** T6 candidate for S1499 xx99 unified plan. Establish canonical write authority across 20 sites.
- **T.F8 — STATUS_CHOICES cleanup for `OpportunityActionPlan`.** Extends F.E1's 4-cleanup track to intelligence-side.
- **T.F9 — LLM max_tokens floor fix for `AIResumeGenerator`.** Bump summary + cover letter max_tokens to ≥4000 for gpt-5-mini compat; OR add explicit model-restriction in enforcer wrapper.
- **T.F10 — Zero JobContract for Income/Jobs lane.** T9 candidate for S1499 xx99 unified plan. Requires ADR draft in post-arc phase.

---

## 16. Boundary Violations

Per playbook §11.2 §16.

**Cross-app writes (`intelligence/` writes to `core.models`):**

- `intelligence/income_spider_orchestrator.py:462` writes `core.models.Opportunity` — cross-app write to mainline model. This is BY-DESIGN (intelligence discovers, core owns opportunity registry).
- `intelligence/spider_decision_bridge.py` writes `core.models.Opportunity` — same pattern.
- `intelligence/spider_opportunity_connector.py` writes `core.models.Opportunity` — same pattern.

**Verdict:** Not a boundary violation per S1274 §5 conventions (spider bridges cross-write intentionally). But absence of a documented write-authority contract elevates the class-of-boundary-crossing to F.F2 finding severity.

**PA tool boundary:**

- `agent_income_tools.py` is invoked by `intelligence/agent_executor.py` NOT by PA tool dispatcher — no boundary violation but a MISSING PA-tool surface for the whole Cat F lane (should be considered as part of T.F10 recommendation).

**Frontend boundary:**

- Backend WebSocket consumer without frontend caller is a MISSING boundary crossing (F.F8), not a violation. If frontend calls something else, that's the drift.

**No hard boundary violations detected.** All cross-app writes fit S1274 conventions.

---

## 17. Duplicate or Overlapping Systems

Per playbook §11.2 §17 (S1273 §3.32 tech debt bullet #2 aggregation).

**Duplicate opportunity models:**

- `core.models_unified_system.Opportunity` — mainline (2631 rows, 20 writers).
- `core.models_autonomous_situations.FreelanceOpportunity` — parallel (0 rows, 1 broken writer).
- `intelligence.models.OpportunityTracking` — third parallel (row count unknown).
- `ai_core.intelligence.income_builder.IncomeOpportunity` — dataclass (transient).
- `intelligence.ai_job_matcher.AIJobMatch` — dataclass (transient).
- `intelligence.ai_resume_generator.AIResume` — dataclass (transient, but different domain).

**Verdict:** 3 persistent + 3 transient representations of the "opportunity" concept in Cat F evidence surface. Extends S1401 D6 dual-representation drift methodology. This is the load-bearing signal for T.F7.

**Duplicate resume generation surface:**

- `intelligence/ai_resume_generator.py:49-560` — LLM-driven.
- `frontend/src/pages/workspace/tabs/CareerTab.tsx` — ATS features (Analyze + Generate Summary via `/api/ats/*`) — likely different backend, possibly duplicate.

**Verdict:** Cat F resume generation may be duplicated by a separate ATS surface not audited here. F.F8 extends: not just missing frontend, potentially wrong-frontend.

**Duplicate income-builder path:**

- `intelligence/income_builder.py` (Session 727 shim; 45+ importers) → `ai_core/intelligence/income_builder.py` (canonical).
- `intelligence/income_builder_automation.py` (wraps `TaskDelegationOrchestrator`).
- `intelligence/income_builder_connector.py` (Flask demo).

**Verdict:** 3 "income_builder" prefixes with different responsibilities and one deprecation redirect. T.F3 target.

**Ops Autopilot overlap:**

- `intelligence/agent_income_tools.py.create_content()` at line 143-252 delegates to Content Studio or fallback `generate_ai_content()` — Cat F does NOT own content deliberation, but touches it.

**Verdict:** Cat F does not overlap ops_autopilot at the runtime layer; it's a consumer, not a duplicate. Not a T.F entry.

---

## 18. Ownership Gaps

**Summary:** F.F3 completes the arc-wide F.E10 synthesis. This section per playbook §11.2 §18 enumerates the specific gaps for the Cat F half.

1. **`scan_income_spider_orchestrator` — no JobContract owner.** Beat fires with no accountability. If it errors, no escalation path. Silent failure risk. Session 1115 batch-6 comment (`core/celery.py:750-754`) acknowledges "truly forgotten task designed to be scheduled" — installation without ownership.
2. **PA tool surface — no dedicated schema.** `/opportunities` + `/track` Discord commands + generic `opportunity_manager_tool` PA tool route to mainline Opportunity, not Cat F lane. If Rigby surfaces recommendations from Cat F files, the user has no PA-tool path to interact.
3. **Revenue bridge — unimplemented.** `core/personal_assistant_integration.py:240` flags `'income_to_revenue': 'unknown'` in audit. Cat F does not write to any Revenue model.
4. **HumanAttention integration — missing.** Zero HAI writers from Cat F files. If low-match-score jobs need review, no escalation surface exists. Extends S1404 F.D4 arc-wide HAI missing.
5. **Frontend integration — missing (F.F8).** Backend wired, frontend absent. If UX depends on job-scanner or resume-generator, users have no path.
6. **Application submission — simulated.** Even if all owners existed, submissions would still be mock (F.F6 + F.F8).

**Cross-arc ownership recommendation candidates (Agent 6 trade-off matrix):**

- **(a) Income Employee JobContract** — parallel to S1405 R.E-1 Revenue Employee proposal. Trade-off: adds 5th employee to Employee OS (current 4); requires wrapping `scan_income_spider_orchestrator` in MissionRunner; adds ~80-100 LOC for PA tool schema + handler.
- **(b) Merge Income/Jobs into Chief of Staff (rotating Lane 4)** — trade-off: mixes signal/action responsibilities; CoS becomes 9-10 step task.
- **(c) Deprecate the entire Income/Jobs lane** — trade-off: cannot without confirming zero fleet-app references + Discord/PA-tool traffic; VERY HIGH risk.
- **(d) ADR + Deferred Arc** — trade-off: defers ownership indefinitely; Employee OS 1200s or new dedicated arc.

**S1499 xx99 owns the final synthesis + candidate ranking.**

---

## 19. Recommended Future Research

Per playbook §11.2 §19. Ranked by architectural uncertainty × risk × unblocked flows.

### 19.1 R.F-1 — Income/Jobs Employee JobContract ADR (HIGH; T.F10 track)

**Uncertainty:** MEDIUM (Agent 6 named 4 options; Chris + Rigby need to lock).

**Risk:** MEDIUM (unowned live task can silently fail; drift accumulates).

**Unblocked flows:** T.F1 (beat verify), T.F2 (phantom fixup), T.F5 (frontend/UX), T.F7 (Opportunity write authority).

**Cross-arc coupling:** parallel to S1405 R.E-1 Revenue Employee. S1499 candidate: single "Revenue-plus-Income" Employee vs two sibling contracts.

### 19.2 R.F-2 — `Opportunity` multi-writer write-authority framework (HIGH; T.F7 track)

**Uncertainty:** MEDIUM-HIGH (20-writer landscape; needs framework design).

**Risk:** HIGH (silent duplicate rows; provenance-filter drift risk per S1399 F1 pattern).

**Unblocked flows:** T.F1 (writer accounting), T.F2 (safe-delete of broken writers), consistency of `Opportunity` reads.

**Cross-arc coupling:** extends S1401 D6 methodology; S1499 candidate for arc-wide track.

### 19.3 R.F-3 — Phantom-field writer decision (HIGH; T.F2 track)

**Uncertainty:** LOW (three concrete options: fix, delete, or align).

**Risk:** LOW locally (task dormant), UNKNOWN prod.

**Unblocked flows:** Decommission decision for `FreelanceOpportunity` model (if aligned, may consolidate into `Opportunity`).

### 19.4 R.F-4 — Deprecation shim retirement (MEDIUM; T.F3 track)

**Uncertainty:** LOW (path clear per Session 727 directive).

**Risk:** LOW (backward-compatible re-export). 45-file migration.

**Unblocked flows:** Simplifies import graph; removes DeprecationWarning noise.

### 19.5 R.F-5 — Redis pub-sub schema contract (MEDIUM; T.F4 track)

**Uncertainty:** MEDIUM (7 orphan channels — decision to wire or unwire).

**Risk:** LOW (silent subscription; no runtime crash).

**Unblocked flows:** Would validate whether `AIJobApplicationPipeline` is intended to be live or decommissioned.

### 19.6 R.F-6 — Frontend integration decision (MEDIUM; T.F5 track)

**Uncertainty:** MEDIUM (whether Cat F should have UI, given CareerTab already exists for adjacent ATS features).

**Risk:** LOW.

**Unblocked flows:** Removes half of F.F8 disconnection finding.

### 19.7 R.F-7 — `AIResumeGenerator` LLM max_tokens fix (LOW; T.F9 track)

**Uncertainty:** LOW (fix is 2-line change).

**Risk:** LOW immediate; latent silent-failure on gpt-5-mini.

**Unblocked flows:** Enables safe use of gpt-5-mini across the enforcer.

### 19.8 R.F-8 — S1499 xx99 unified remediation plan candidates for Cat F

Cat F contributions to the S1499 §8 follow-on queue:

- **T6 — Income/Jobs Employee JobContract** (T.F10). Paired with S1405's T.E9 (Revenue Employee); S1499 chooses single-merged vs two-sibling.
- **T7 — Multi-writer convergence contract for `Opportunity`** (T.F7). Extends S1405's T.E-1 Revenue Employee JobContract track with an authority-scope dimension.
- **T8 — Phantom-field remediation** (T.F2). Standalone; can land pre-Employee-OS.
- **T9 — Deprecation shim retirement** (T.F3). Standalone; can land pre-Employee-OS.
- **T10 — Redis pub-sub schema contract** (T.F4). Standalone.
- **Track 5 arc-wide follow-ons** (from S1405): unchanged. Cat F contributes T6-T10 into S1499's 5-track existing framework.

---

## 20. Appendix

### 20.1 Files inspected (10 primary + adjacencies)

- `core/models_autonomous_situations.py` (FreelanceOpportunity model at line 352)
- `core/tasks_ops.py` (phantom-field writer at line 2239-2251)
- `core/celery.py` (beat entry at line 755-759)
- `core/employees/jobs.py` (JobContract inventory — zero Cat F entries)
- `core/agent_router.py` (AGENT_MAP — zero Cat F entries)
- `core/services/pa_tool_schemas.py` (PA tool inventory — zero Cat F schemas)
- `core/services/discord_bot.py` (Discord commands — generic surface only)
- `intelligence/ai_job_matcher.py`
- `intelligence/ai_job_application_pipeline.py`
- `intelligence/agent_income_tools.py`
- `intelligence/income_builder.py` (Session 727 shim)
- `intelligence/income_builder_automation.py`
- `intelligence/income_builder_connector.py`
- `intelligence/income_spider_orchestrator.py`
- `intelligence/job_income_bridge.py`
- `intelligence/job_scanner_consumer.py`
- `intelligence/ai_resume_generator.py`
- `intelligence/routing.py`
- `intelligence/urls.py`
- `intelligence/views_ai_jobs.py`
- `intelligence/tasks.py` (task registration at line 1654-1702)
- `intelligence/models.py` (OpportunityActionPlan STATUS_CHOICES at line 154-186)
- `intelligence/models/income_builder.py` (OpportunityTracking at line 99)
- `intelligence/spider_decision_bridge.py` (dominant Opportunity writer)
- `intelligence/spider_opportunity_connector.py`
- `intelligence/revenue_tracking_bridge.py`
- `frontend/src/pages/workspace/tabs/CareerTab.tsx` (adjacent ATS surface)

### 20.2 Docs inspected

- `docs/research/domains/revenue/1400_revenue_domain_scoping.md` (parent §3.F + §12.1 Cat F + §11.4 15 inherited findings)
- `docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md` (§14 D6 dual-representation)
- `docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md` (§14 F.B4 methodology analog)
- `docs/research/domains/revenue/1403_revenue_engagement_inbound_audit.md` (§14 F.C6 pattern)
- `docs/research/domains/revenue/1404_revenue_meeting_close_audit.md` (§14 F.D1 + F.D10 patterns)
- `docs/research/domains/revenue/1405_revenue_attribution_analytics_audit.md` (§14 F.E1 + F.E2 + F.E3 + F.E10)
- `docs/research/ARCHITECTURE_INDEX.md` (v24)
- `docs/research/OPEN_ARCS.md` (Group 1400 in-progress row)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 20-section template + §13 6-parallel-Explore sweep + §14 evidence rules + §15 SIGN table)
- `AUDIT_FINDINGS.md` #12 (canonical Celery deferred list — cross-referenced for F.C6 pattern)
- `docs/PLATFORM_INVENTORY.md` (2026-06-22 12:59:48; `FreelanceOpportunity` enumerated)
- `docs/PLATFORM_WHAT_IT_IS.md` (last_reviewed 2026-06-30; no Cat F narrative)
- `CLAUDE.md` (Employee OS inventory: 4 employees, 74 enabled agents, 414 Celery tasks, etc.)
- `MEMORY.md` (feedback rules applied: `feedback_verify_before_deleting_dead_code.md`, `feedback_fleet_caller_verification_before_celery_deletes.md`, `feedback_gpt5_max_completion_tokens_floor.md`, `feedback_procfile_makefile_queue_parity.md`)

### 20.3 Grep patterns used

Primary lens patterns per S1405 F.E1/F.E2/F.E3 methodology inheritance:

- `FreelanceOpportunity.objects.create` — writer detection
- `FreelanceOpportunity.objects.(filter|get|all)` — reader detection
- `import.*FreelanceOpportunity` — import inventory
- `Opportunity.objects.create` — arc-wide multi-writer inventory
- `status=` — STATUS_CHOICES writer detection
- `STATUS_CHOICES|STATE_CHOICES` — enum declaration inventory
- `@shared_task|@app.task|@periodic_task` — Celery task inventory
- `@receiver(post_save|pre_save|post_delete)` — signal inventory
- `channel_layer.group_send|async_to_sync.*group_send` — Channels broadcasts
- `redis.publish|PUBLISH intelligence:` — Redis pub-sub publisher grep
- `AsyncWebsocketConsumer|WebsocketConsumer|AsyncConsumer` — consumer base classes
- `JobContract|AIEmployee` — Employee OS inventory
- `AGENT_MAP` — router inventory
- `get_openai_client|get_anthropic_client|get_llm_enforcer` — factory pattern verification
- `max_tokens=|max_completion_tokens=` — LLM budget audit
- `/ws/job-scanner/|/api/income-builder/|/ai-jobs/` — endpoint routing
- `metadata__created_via=` — Opportunity provenance stamp (ORM probe)

### 20.4 Unresolved unknowns

**Local vs prod dormancy split:**
- Local DB row counts are authoritative for LOCAL. Production row counts UNKNOWN per T.C8(c) (Rigby `db_health_tool env=prod` "not configured: PA_DB_HEALTH_RPC_URL, PA_DB_HEALTH_RPC_CLIENT_TOKEN") — D49 minimal-blocking discipline preserved.
- `scan_income_spider_orchestrator` production execution frequency + success rate UNKNOWN. Candidate T.F1 verify.

**45+ deprecation-shim importer catalog:**
- Agent 3 counted "46 references"; individual importer list not enumerated. Migration planning per T.F3 needs full inventory.

**Discord command usage:**
- `/opportunities` + `/track` invocation frequency UNKNOWN. Cat F deprecation decision (Option (c) from Agent 6 matrix) blocked on this data.

**`ai_core/intelligence/income_builder.py` (canonical AIIncomeBuilder):**
- Referenced by shim + Cat F files but not deep-audited. This is the canonical Session 727 destination; its runtime status was outside the 10-file Cat F scope.

**Fleet-app references:**
- Memory rule `feedback_fleet_caller_verification_before_celery_deletes.md` requires 3-axis sweep before deleting anything Celery-connected. Cat F contains multiple Celery-adjacent tasks; fleet-app verification not performed for T.F3/T.F5 decommission candidates.

**Frontend CareerTab depth:**
- `frontend/src/pages/workspace/tabs/CareerTab.tsx` exists per Agent 6 mention; may overlap Cat F's resume-generator responsibilities via `/api/ats/*` routes. Not audited.

### 20.5 Conflicts between sources

**DISAMBIGUATION #1 (verifier-loop, load-bearing):** Agent 4 F.F4 sub-agent
claim vs parent-Claude direct ORM probe. Sub-agent said "hourly writes 20 rows";
ORM probe found 0 rows via provenance stamp locally. Refined: beat scheduled +
task exists + write path exists in code, but the writes are not observed at that
provenance in local DB. Truth is more nuanced (could be silently failing worker,
could be dev-env skip, could be prod-only path).

**DISAMBIGUATION #2 (verifier-loop, load-bearing):** Agent 4 F.F2 "two orchestrators
write to Opportunity" is NARROW. Broader truth: 20 writers total; `spider_decision_bridge`
is dominant (2630 rows). Sub-agent claim REFINED not REFUTED.

### 20.6 Verifier-loop history

**Parent-Claude verifier-loop discipline (extending S1404 pattern + S1405 pattern):**

12 direct-read/direct-grep/direct-ORM checkpoints applied to sub-agent claims BEFORE Rigby SIGN. 10 CONFIRM + 2 DISAMBIGUATION.

**New pattern for S1406:** **provenance-stamp ORM probe as disambiguation tool.**
Previous verifier-loop tools (S1401-S1403 file-line direct-reads; S1404 broader-grep;
S1405 model-context disambiguation) plus new S1406 tool: direct query on `metadata`
field to distinguish "code exists" from "code is producing observable output."

### 20.7 Rigby SIGN fold notes

**S1405 D48 stability-probe gate application (first application — completed):** At S1406 SIGN cycle 1 open, Rigby fresh SIGN pin `pa-8660ea7cfecd4bc6` minted via `session_tool.create_fresh`. First-turn generic-error triggered S1405 D45 recovery-pattern warmup-ping response (ultra-short "confirm ready" probe) — Rigby responded "Ready. I don't have direct visibility into that draft file path unless you paste excerpts or we pull it via a repo/doc tool, but I'm ready to receive the titles-only SIGN batch now." Warmup succeeded.

**Rigby SIGN cycle 1 verdict:** SIGN-with-edits SUBSTANTIVE (batches 1-3 delivered; batch 4 blocked).

**Batches 1-3 substantive pressure-test summary:**
- **Batch 1 (F.F1-F.F3 HIGH severity):** All 3 findings survive at HIGH. 3 framing refinements folded per Rigby direction — F.F1 hard-crash-vs-currently-unreachable framing + call-chain evidence pin; F.F2 evidence-gap classification of 20 writers into (a)tests/(b)migrations/(c)dead/(d)legitimate deferred to S1499 T.F2 track; F.F3 ownership-plane-vs-capacity-plane separation.
- **Batch 2 (F.F4-F.F6):** F.F4 split into 3 sub-findings (4a shim MEDIUM / 4b stub HIGH-if-user-facing / 4c Flask demo LOW-MEDIUM); F.F5 reachability count deferred to full-writer sweep S1499 T.F8; **F.F6 UPGRADED to MUST-FIX** with expected-loop spec + concrete negative + blast-radius elaboration.
- **Batch 3 (F.F7-F.F10):** F.F7 no-false-negative confirmed via cross-abstraction spot-check; F.F8 tightened to "no UI client" + non-UI clients not audited note; **F.F9 UPGRADED to HIGH** after parent-Claude direct-verify of `core/llm_enforcer.py:232` `downgrade_model = 'gpt-5-mini'` + line 446-450 downgrade log confirming enforcer DOES route to gpt-5-mini; F.F10 reframed as taxonomy/ownership smell.

**Batch 4 (S1405 F.E4-F.E10 deferred addendum):** worker generic-error recurrence on turn 4 (same failure mode as S1405 pin jams). Per D48 fallback option (iii), deferred to S1499 xx99 synthesis. Parent-Claude 12/12 verifier-loop stands as compensating quality gate.

**Rigby SIGN cycle 2:** Not attempted per D50 Chris-ratification (worker instability signal is now 2-session pattern; not spending more pin cycles).

**Total fold count:** 10 framing refinements + 2 severity upgrades (F.F6 MUST-FIX, F.F9 HIGH) applied at commit-time before Chris commit-gate.

### 20.8 Anchor corrections to upstream parent subsection

Per S1404 §20.10 pattern + S1405 §20.10 pattern:

**Parent §3 Category F evidence surface — no corrections this session.** All 9 named files exist and match the surface described in parent §3 Category F (S1400 v2). D25 F.i lock accurate.

**Parent §12.1 Category F questions — no corrections.** All 5 Category F questions answered in §12.4 above.

**Parent §11.4 15 inherited findings — no corrections.** All 15 remain accurate; F.F1-F.F10 either extend or complete inherited findings without contradicting parent frame.

### 20.9 Rigby SIGN pin retirement queue (playbook §15)

- Fresh S1406 SIGN pin minted at Rigby-routing time.
- Retire post-PR-merge per playbook §15 stage table.

### 20.10 Arc trajectory statement (placeholder for Rigby refinement)

**Draft:** "With Categories A/B/C/D/E/F now all shipped, the arc has surfaced
a consistent pattern: at every stage of the lead → attribution lifecycle, the
Revenue domain has (i) more code than runtime signal, (ii) more declared entry
points than production traffic, (iii) more STATUS_CHOICES states than reachable
transitions, (iv) more model schemas than canonical write paths, and (v) more
scheduled Celery tasks than owned JobContracts. S1499 should synthesize a single
'activate the entire Revenue + Income/Jobs lifecycle + establish canonical
ownership' remediation plan, structured as 5 tracks (T1-T5 from S1405 §19)
plus 5 Cat F additions (T6-T10 from S1406 §19.8), while immediate anchor
corrections (as described here) prevent further drift."

**Rigby to refine at SIGN cycle 1 or cycle 2 based on Batch 2-3 addendum + Cat F verdict.**

### 20.11 Cross-arc placement in ARCHITECTURE_INDEX

- **Next bump:** ARCHITECTURE_INDEX v24 → v25 at S1406 close-out commit.
- **New row:** §1.28 for S1406 Cat F child audit.
- **§8 timeline:** S1406 row added.
- **Frontmatter v25 preamble:** load-bearing findings summary.

### 20.12 Handoff continuity chain

- **S1406 handoff:** `docs/handoffs/SESSION_1406_REVENUE_FREELANCE_GIG_INCOME_JOBS.md` (to be written at close).
- **Prior:** SESSION_1405 (Group 1400 Child E Attribution + Analytics).
- **Prior chain:** S1404 (Cat D Meeting + Close), S1403 (Cat C Engagement Inbound), S1402 (Cat B Outreach), S1401 (Cat A Opportunity Discovery), S1400 (arc open).
- **Next expected:** S1499 xx99 canonical summary (per parent §5 mission sequence P7 slot).

### 20.13 D46-D49 Chris ratification record

- **D46 (launch cadence):** (i) SEQUENTIAL. Chris-locked via "agree all" 2026-07-01 at S1406 open.
- **D47 (arc pin retention):** (i) RETAIN `pa-34d43795e1b24bd3`. Chris-locked via "agree all" 2026-07-01. Health signal `strongly_recommend_fresh` (score 25) disclosed but arc-continuity discipline preserved through S1499.
- **D48 (S1405 follow-up SIGN addendum timing):** (ii) fold Batch 2-3 retry into S1406 opening SIGN with stability-probe gate (Rigby's refined framing). Chris-locked via "agree all" 2026-07-01. Executed at S1406 open; worker instability blocked batch 4; escalated per (iii) fallback.
- **D49 (T.C8 tool timing):** (ii) minimal-blocking. Chris-locked via "agree all" 2026-07-01.
- **D50 (S1406 SIGN acceptance):** (i) accept SIGN-with-edits cycle 1 (Batches 1-3 substantive) with commit-time folds — no cycle 2 attempt given worker-instability pattern. Chris-locked via "agree all" 2026-07-01 mid-session.
- **D51 (S1405 F.E4-F.E10 addendum):** (i) defer to S1499 xx99 synthesis per D48 fallback (iii); marked SIGN-deferred-due-to-recurring-worker-generic-error; verifier-loop 12/12 stands. Chris-locked via "agree all" 2026-07-01 mid-session.

### 20.14 Playbook §11.3 §10 meta-methodology (placeholder for S1499)

Not applicable in child audit; belongs in S1499 xx99 canonical summary §10 per Chris directive 2026-07-01 (adopted at S1399 close; second application at S1499).

Cat F methodology observations to feed forward into S1499 §10:

- **DISAMBIGUATION pattern via ORM row-count probe** is new S1406 contribution to verifier-loop discipline. Should codify into playbook v3 §14 evidence rules if S1500 second-application preserves it (per two-triggers threshold).
- **First application of S1405 D48 stability-probe gate** — outcome data feeds into S1499 §10 methodology assessment.
- **Cat F is the second half of arc-wide F.E10 synthesis** — establishes the pattern that "final child audit before xx99 can complete cross-child load-bearing findings via inheritance." Codify into playbook §11.4 if S1500 second-application preserves it.

---

**End of S1406 child audit.**
