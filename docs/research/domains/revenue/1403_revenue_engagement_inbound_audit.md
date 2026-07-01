---
title: "S1403 — Group 1400 Revenue Child C (Engagement Inbound) audit"
status: draft
authority: research
category: child_audit
session: 1403
date: 2026-07-01
parent_arc: docs/research/domains/revenue/1400_revenue_domain_scoping.md
sibling_prior: docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md
playbook: docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
template: playbook §11.2 (20-section child audit)
verifier_loop_applied: true (parent-Claude spot-checks pre-SIGN; Agent 6 T.C4 dead-code overreach caught + Agent 5 F2 CANDIDATE upgraded to CONFIRMED writer-site via direct read + Rigby ops probe mid-draft CONFIRMED F.C6 deferred-by-policy dormancy of `run_ops_autopilot` + Rigby-side cycle 1 must-fix #1 empirical row-count question resolved via parent-Claude Django ORM count on local env — all 4 tables 0 rows, F.C1 CONFIRMED at RUNTIME in addition to CODE)
sign_status: SIGN-clean cycle 2 High confidence (Rigby cycle 1 SIGN-with-edits Medium-High: must-fix 1 empirically CLOSED via parent-Claude Django ORM count + must-fix 2 withdrawn as Rigby cycle-1 response artifact not audit defect; cycle 1 fold applied — Q1/Q4/Q5/Q6 recommendation refinements; cycle 2 verdict 2026-07-01 — 0 residual must-fix + Q7/Q8/Q9 answered + 2 nice-to-haves folded)
head_git_sha: d91d30f7
inherited_findings: 15 (parent §11.4) + 4 (from S1402 F.B1/F.B2/F.B3/F.B4)
---

# S1403 — Group 1400 Revenue Child C (Engagement Inbound)

> **Load-bearing framing (verifier-loop caught pre-SIGN).** Category C is a **read-only monitoring surface layered on a schema-only inbound event log**. `EngagementEvent` (`core/models_engagement.py:18`) is the parent-declared canonical inbound event stream, but it has **ZERO writer sites at HEAD `d91d30f7`** — both its `outreach_draft` FK and its `opportunity` FK are populated by nothing (grep `EngagementEvent.objects.create|EngagementEvent(` returns only the class definition itself; S1402 F.B3 finding CONFIRMED and extended). Two service classes (`EngagementEngine` at `engagement.py:235`; `EngagementAutonomyEngine` at `engagement.py:764`) provide 9 read-only PA tool actions + 2 policy-engine hooks — both `evaluate()` methods are LIVE via `_policy_engagement_engine` (`core.py:2210-2238`) + `_policy_engagement_autonomy` (`core.py:2390-2418`) wired into the ops_autopilot policy registry (`core.py:277+283`). The **canonical inbound event log is architecturally intact but runtime-empty**: schema exists, services are exercised on schedule, but the ingestion path (webhook / poller → `EngagementEvent.objects.create(...)`) **does not exist at HEAD**. This audit's CENTRAL deliverable per parent §12.1 Category C + S1402 §19 R.B5 inheritance is a design-preparation ADR for the F.B3 ingestion path — not a seam-verify but a whole-seam build-out, blocker-gated by F.B1 delivery-path landing first (per S1402 §14 D.B3 refined "no outbound channel at all"). Two independent sub-agents (Agents 1 + 5) refuted parent §3 Cat C's axis-map hypothesis with matching evidence: the working session-aggregation axis lives in **EngagementMetrics + OpportunityInteraction** via the WebSocket consumer at `revenue_opportunities_consumer.py:849/527/694` — **not** via EngagementEvent — and **ContentEngagement** at `models_pipeline_feedback.py:370` is an orthogonal content-pipeline learning surface with no bridge back to inbound engagement.

## 1. Executive Summary

**Runtime state (verified at HEAD `d91d30f7`):**

- **Canonical inbound event log:** `EngagementEvent` at `core/models_engagement.py:18` (147 lines, migration `0294_engagement_event_model.py`, table `core_engagement_event`, indexed on `(status, -created_at)`, `(intent, status)`, `(channel, -created_at)`). **ZERO writer sites at HEAD `d91d30f7`.** Both `outreach_draft` FK (:55-59) and `opportunity` FK (:62-66) are schema-only with no code path populating them. Grep `EngagementEvent.objects.create|EngagementEvent(` → only class definition at line 18.
- **Read-only service surface (WORKING):** `EngagementEngine` at `engagement.py:235-472` — 7 methods (`get_inbox`, `classify_event`, `draft_reply`, `approve_reply`, `disqualify`, `get_metrics_report`, `evaluate`); no LLM invocations (all classification is operator-supplied via `intent` param mapped through `INTENT_ACTIONS` dict at :312); no auto-send (draft_reply → needs_reply → approve_reply is a strict human-gate); auto-close of stale events after 30d via `evaluate`. `EngagementAutonomyEngine` at `engagement.py:764-1008` — 4 methods (`get_sla_queue`, `get_meeting_suggestions`, `get_conversion_report`, `evaluate`); SLA thresholds hardcoded (`SLA_WARNING_HOURS=4`, `SLA_CRITICAL_HOURS=24`, `SLA_BREACH_HOURS=48`); zero persistence surface (no autonomy state written back).
- **Policy engine wiring (LIVE):** ops_autopilot policy registry at `core.py:277` binds `('engagement', 'engagement_engine', '_policy_engagement_engine')` and at `:283` binds `('engagement_autonomy', 'engagement_autonomy', '_policy_engagement_autonomy')`. `_policy_engagement_engine` at `:2210-2238` invokes `EngagementEngine().evaluate(now)` at :2224. `_policy_engagement_autonomy` at `:2390-2418` invokes `EngagementAutonomyEngine().evaluate(now)` at :2404. Both fire on the `run_ops_autopilot` beat cadence (external — Rigby ops probe pending).
- **PA tool surface (9 actions):** 6 EngagementEngine wrappers at `td_handlers_ops.py:2808-2885` (`engagement_inbox`, `engagement_classify`, `engagement_draft_reply`, `engagement_approve_reply`, `engagement_disqualify`, `engagement_metrics_report`) + 3 EngagementAutonomyEngine wrappers at `:3102-3122` (`engagement_sla_queue`, `engagement_meeting_suggestions`, `engagement_conversion_report`). All are read/report actions except classify + draft_reply + approve_reply + disqualify which mutate `EngagementEvent.status`/`intent`/`draft_reply` — but only on existing rows (no create-path exposure).
- **Session-aggregation axis (WORKING but disconnected):** `EngagementMetrics` (`models_engagement_metrics.py:14`) is written by ONE site — `core/revenue_opportunities_consumer.py:849` — on WebSocket connect. `OpportunityInteraction` (`models_engagement_metrics.py:164`) is written by THREE sites: two in the same consumer (`:527` for click, `:694` for apply) with `engagement_session` FK populated, and a third at `core/views_opportunities.py:56-65` in REST `quick_apply()` that **omits `engagement_session` FK entirely** — CONFIRMED F2 orphan-write writer-site per verifier-loop direct read.
- **Content engagement axis (WORKING but orthogonal):** `ContentEngagement` at `models_pipeline_feedback.py:370` is written by ONE site — `core/services/pipeline_learning.py:279` (`PipelineLearningService.record_engagement`). No FK bridges back to `EngagementEvent`/`EngagementMetrics` despite docstring at :374-378 claiming it "closes the learning loop." CONFIRMED docstring-vs-runtime drift.
- **Event bus streams:** ZERO `ENGAGEMENT_*` streams on `core/services/event_bus.py:21-31`. Matches S1402 §10 Q19 finding for outreach; extends symmetrically to engagement.

**Load-bearing findings (five, ranked by runtime severity, verifier-loop applied):**

- **F.C1 — Ingestion path missing (CONFIRMED HIGH, code + runtime local).** No webhook receiver, no polling task, no signal, no consumer produces `EngagementEvent` rows. Grep `EngagementEvent.objects.create|EngagementEvent(` → zero at HEAD `d91d30f7`. Both FKs (`outreach_draft`, `opportunity`) are schema-only. **Empirical runtime CONFIRMATION (Rigby cycle 1 must-fix #1 fold, parent-Claude Django ORM count local env, 2026-07-01):** `EngagementEvent.objects.count() = 0`. Extends S1402 F.B3 with second-FK evidence (parent scoping doc + S1402 both undernamed the `opportunity` FK; this audit records the full schema-vs-runtime gap). CENTRAL S1403 deliverable per parent §12.1 Cat C + S1402 §19 R.B5. **Evidence tier: code-path CONFIRMED (grep) + runtime-local CONFIRMED (Django ORM count) + runtime-prod PENDING (Rigby `db_health_tool env=prod` returned "not configured: missing PA_DB_HEALTH_RPC_URL, PA_DB_HEALTH_RPC_CLIENT_TOKEN" — T.C8 tool-surface gap).**
- **F.C2 — Corrected axis-map (CONFIRMED, dual-agent-verified).** Parent §3 Cat C hypothesized a three-axis map (event log = EngagementEvent; aggregation = EngagementMetrics + ContentEngagement; join = OpportunityInteraction). Two independent sub-agents (§13 sweep Agents 1 + 5) refuted with matching evidence. The runtime axis is **three independent surfaces**: (i) EngagementEvent event-log axis is architecturally-declared but runtime-empty (F.C1); (ii) session-aggregation axis lives in EngagementMetrics + OpportunityInteraction as a WebSocket-consumer dual-write pattern (`revenue_opportunities_consumer.py:849/527/694`), not fed by EngagementEvent; (iii) ContentEngagement is a content-pipeline learning surface, orthogonal to inbound engagement. OpportunityInteraction is a **detail-child of EngagementMetrics** (via nullable `engagement_session` FK), not a join artifact.
- **F.C3 — OpportunityInteraction F2 orphan-write CONFIRMED at `views_opportunities.py:56-65`.** REST `quick_apply()` endpoint creates `OpportunityInteraction` with `user`, `opportunity_id`, `opportunity_title`, `opportunity_platform`, `opportunity_salary`, `interaction_type='apply'`, `was_personalized=True`, `resulted_in_application=True` — but **omits `engagement_session`** which the WebSocket consumer path always populates. Effect: rows created via REST apply are structurally-orphaned from the session-aggregation tree — invisible to EngagementMetrics session rollup. **Runtime blast radius: CONFIRMED ZERO at local env** (Rigby cycle 1 must-fix #1 fold, parent-Claude ORM count: `OpportunityInteraction.objects.count() = 0` — no rows created via either the WebSocket path or the REST path in this env). PROD blast radius unknown pending Rigby prod-DB tool exposure (T.C8). Verifier-loop caught this by direct read after Agent 5 flagged as CANDIDATE. Sibling to S1402 F.B2 pattern (writer-site F2 orphan-write) — matches S1402 F.B2's zero-blast-radius pattern (there via D.B7 dead code; here via zero rows in the parent write path being exercised at all). **Evidence tier: code-path CONFIRMED (direct read line 56-65) + runtime-local CONFIRMED zero (Django ORM) + runtime-prod PENDING.**
- **F.C4 — ContentEngagement "learning loop" docstring drift (CONFIRMED HIGH docstring, MEDIUM runtime).** `models_pipeline_feedback.py:372-378` docstring: "Track engagement metrics for published content. This closes the learning loop: What gets views/completed/shared/converts." Runtime: `ContentEngagement` has FK to `series`/`episode`/`content_package` but **no FK to `EngagementEvent`, `EngagementMetrics`, or `OpportunityInteraction`**. The declared "learning loop" from published content → inbound engagement attribution has no bridge. Consumer reads at `blog_performance_context.py:344` filter by `outcome='published'` for analytics only; no feedback traversal into inbound. Severity: CONFIRMED docstring drift (D.C4); runtime is functional-but-partial for its declared scope.
- **F.C5 — EngagementAutonomyEngine docstring drift (CONFIRMED, LOW-severity).** `engagement.py:774` docstring lists "Reply context builder (outreach, opportunity, meeting history)" as one of four value-adds "sits on top of EngagementEngine." Direct read of class body (`:764-1008`) shows four methods (`get_sla_queue`, `get_meeting_suggestions`, `get_conversion_report`, `evaluate`) — **no reply-context-builder method exists**. Documented at §14 D.C5.
- **F.C6 — `run_ops_autopilot` beat wrapper deferred-by-policy (CONFIRMED, LOAD-BEARING nuance to §5.3 wiring claim).** The Category C policy hooks (`_policy_engagement_engine` + `_policy_engagement_autonomy`) are code-wired to fire on `run_ops_autopilot` cadence — but `run_ops_autopilot` is **NOT registered as PeriodicTask** (Rigby probe: 0 of 92 enabled PeriodicTask rows match `ops_autopilot`; 30d `celery_task_history` → 0 firings). This is **intentional per AUDIT_FINDINGS.md #12** — `core/celery.py:507-509` + `:633-634` explicitly name `run_ops_autopilot` as "deferred for separate green-light" (behavior-changing task suspended pending Chris explicit enablement). Also cross-listed as an orphan task in `docs/CELERY_AUDIT.md:19,37,390` (`⚠` marker; caller count 0). **Consequence:** Category C's read-only monitoring surfaces `evaluate()` never fire on autonomous cadence in the probed environment. They DO fire when Rigby is asked to run the autopilot ad-hoc via PA tool at `core/services/td_handlers_ops.py:1643,1674` (`OpsAutopilot().run()` invocation from operator initiation) — but no autonomous cadence exists. Refinement to §1/§5.3/§7 Flow α/§13 Maturity: split "code-wired vs runtime-dormant-by-policy" for Category C policy surface. This finding is symmetric to S1402 F.B4 dead-code cadence but at a HIGHER level in the invocation tree — S1402 flagged `OutreachSequencer.evaluate` as an orphan method; S1403 extends the pattern to the entire `run_ops_autopilot` policy engine dispatcher. Memory rule `feedback_audit_findings_12_canonical_celery_deferred_list.md` triggered pre-SIGN to correctly classify this as **INHERITED-BY-POLICY** (S1115 batch-3/batch-4 deferred list), not a new bug.

**Inherited findings status (from parent §11.4, 15 findings + S1402's F.B1/F.B2/F.B3/F.B4):**

- **S1402 F.B3 (engagement feedback loop missing):** CONFIRMED HIGH and EXTENDED. S1402 named the `outreach_draft` FK gap; this audit extends to include the `opportunity` FK (also zero writers) and the parallel `EngagementEvent.user` FK (schema-only for the ingestion-created rows — no writer, so untested).
- **S1402 F.B1 (delivery path missing):** BLOCKER dependency for F.C1 ingestion design. Ingestion presupposes sent outreach; F.C1's writer contract must correlate inbound webhook to originating OutreachDraft via `provider_message_id` — a field which does not exist on OutreachDraft (grep `models_outreach.py` for `provider_message_id|message_id` → 0 matches). See §19 R.C1 pair-design recommendation.
- **S1402 F.B4 (cadence declared not realized):** Does NOT extend to Category C's `evaluate` methods. Direct-read verifier-loop CONFIRMED both `EngagementEngine.evaluate` (`engagement.py:442`) and `EngagementAutonomyEngine.evaluate` (`engagement.py:966`) have LIVE invokers via ops_autopilot policy engine at `core.py:2210` + `:2390`. Sub-agent T.C4 (dead-code CANDIDATE for EngagementAutonomyEngine) REFUTED pre-SIGN.
- **S1401 F1 provenance-filter drift lens:** CANDIDATE holds for Category C readers — `EngagementEngine.get_inbox` filters on `suppressed=False`, `status`, `intent`; `EngagementEvent.channel`/`prospect_company`/`trace_id` fields would be provenance-relevant but are not filter targets. Extends S1401 lens to reader-only surface (no writers to drift against).
- **S1401 F2 orphan-write lens:** CONFIRMED at writer site `views_opportunities.py:56-65` for OpportunityInteraction (F.C3 above). Sibling pattern to S1402 F.B2. Repo-wide sweep for other Category C writer sites remains CANDIDATE (bounded by F.C1 — no EngagementEvent writers exist yet).
- **S1401 F3 Redis-only durability lens:** CANDIDATE holds — `revenue_opportunities_consumer.py:302-306` caches opportunities in Redis with 5min TTL (Agent 5 flagged); scoped to consumer, not to engagement state.
- **Ownership gap (S1274 §14 #36 HIGH):** CONFIRMED for Category C. Grep `core/employees/jobs.py` for "engagement" (case-insensitive) → 0 hits. Grep `core/agent_router.py` for engagement-related agent handles → 0 hits. No dedicated Celery queue or beat task routes to engagement. Deferred to Child E per D28 (parent §12.1).
- **Maturity WORKING (S1273 §3.32 baseline):** Split verdict: **WORKING (read-only service surface + session-aggregation via WebSocket consumer) / MISSING (canonical ingestion path)** — mirroring S1402's WORKING/PARTIAL composition/delivery split.
- **Coverage LIGHT (parent §11.3):** upgraded to **MODERATE** for Category C by this audit; still LIGHT for future ingestion path (does not exist yet — S1403 designs it).

**Category C classifications:**

- Coverage: **MODERATE** (read-only services well-documented in `engagement.py` docstrings + PA tool surface + WebSocket consumer session-aggregation code; canonical ingestion path UNKNOWN because MISSING).
- Maturity: **WORKING (services + session aggregation) / MISSING (canonical ingestion)**. EngagementEvent-shaped ingestion has no writer. Session-aggregation via EngagementMetrics fires end-to-end from WebSocket click/apply → aggregated CTR/application_rate; but this is disconnected from the parent-declared canonical inbound event stream.

## 2. Domain Purpose

Category C is the third slot in the Group 1400 Revenue arc, per parent §5 mission sequence A → B → C → D → E → F → xx99. In the mainline pipeline shape declared at S1273 §4.9 (Spider → Opportunity → Outreach → **Engagement** → Meeting → ClosePack → Revenue → ImpactEvent), Category C owns the transition **OutreachDraft → EngagementEvent**: capture inbound prospect signal (reply, click, open, meeting-booking, form-fill) against a previously sent outreach, classify intent, gate on human approval for outbound reply, and roll up funnel metrics.

**Design intent (from model + service docstrings):**

- `core/models_engagement.py:6-14` — `EngagementEvent` docstring: "Captures and classifies inbound prospect interactions (replies, meeting bookings, form fills). Classifies intent (positive, neutral, objection, meeting, unsubscribe). Suggests next actions. Draft replies require approval — never auto-sends."
- `core/services/ops_autopilot/engagement.py:236-244` — `EngagementEngine` docstring: same as above, with explicit PA tool surface enumeration.
- `core/services/ops_autopilot/engagement.py:764-775` — `EngagementAutonomyEngine` docstring: "Automates engagement lifecycle: SLA tracking for reply queue, auto-meeting suggestions for positive/meeting intent, engagement-to-meeting conversion tracking, and reply context assembly. Sits on top of EngagementEngine, adding: SLA-aware reply queue with time-since-receipt; Auto-meeting booking suggestions for high-intent events; Conversion funnel from engagement → meeting → deal; Reply context builder (outreach, opportunity, meeting history)."
- `core/models_pipeline_feedback.py:372-378` — `ContentEngagement` docstring: "Track engagement metrics for published content. This closes the learning loop: What gets views/completed/shared/converts."
- `core/models_engagement_metrics.py:16, 166` — `EngagementMetrics`: "Track user engagement metrics for measuring personalization effectiveness"; `OpportunityInteraction`: "Track individual opportunity interactions for detailed analytics."

**Runtime reality (verifier-loop caught, load-bearing):** the declared purpose of `EngagementEvent`/`EngagementEngine` is "capture and classify inbound prospect engagement" — but no code path captures inbound engagement. `classify_event` at `engagement.py:297-328` takes an **operator-supplied `intent` param** (not an LLM classifier — parent §3 Cat C's implicit LLM-classification assumption is WRONG). The runtime state machine works cleanly on existing rows for classification / draft-reply / approve / disqualify — but there are no existing rows to work on. Documented at §14 D.C1.

Category C also owns a **secondary aggregation surface** — the EngagementMetrics + OpportunityInteraction session-level rollup — that operates independently of EngagementEvent, fed by the Revenue Opportunities WebSocket consumer path (`core/revenue_opportunities_consumer.py`). This surface is functional and exercised end-to-end but is architecturally disconnected from the canonical inbound event log; it captures session-scoped click/apply behavior against Opportunity rows, not the outbound-reply-to-outreach signal the parent-declared model is designed for.

## 3. Canonical Entry Points

Six entry points reach Category C code (three read paths, two mutation paths on existing rows, one scheduled sweep — plus the WebSocket consumer path for the session-aggregation axis):

| # | Entry point | File:line | Trigger | Access shape |
|---|---|---|---|---|
| 1 | PA tool `engagement_inbox` | `td_handlers_ops.py:2808` → `EngagementEngine.get_inbox` (`engagement.py:255`) | Rigby function-call routing from PA chat | Read-only; filter by status; returns up to 20 events + status counts |
| 2 | PA tool `engagement_classify` | `td_handlers_ops.py:2818` → `EngagementEngine.classify_event` (`engagement.py:297`) | Rigby function-call routing | Mutation on existing row; sets `intent`/`summary`/`suggested_action`/`status='classified'`; auto-suppresses on `intent='unsubscribe'` |
| 3 | PA tool `engagement_draft_reply` | `td_handlers_ops.py:2835` → `EngagementEngine.draft_reply` (`engagement.py:330`) | Rigby function-call routing | Mutation; sets `draft_reply` text + `status='needs_reply'`; requires later `approve_reply` before finalization |
| 4 | PA tool `engagement_approve_reply` | `td_handlers_ops.py:2848` → `EngagementEngine.approve_reply` (`engagement.py:352`) | Rigby function-call routing | Mutation; requires `status='needs_reply'`; sets `edited_reply`/`status='actioned'` |
| 5 | PA tool `engagement_disqualify` | `td_handlers_ops.py:2863` → `EngagementEngine.disqualify` (`engagement.py:375`) | Rigby function-call routing | Mutation; sets `status='disqualified'`/`disqualify_reason` |
| 6 | PA tool `engagement_metrics_report` | `td_handlers_ops.py:2878` → `EngagementEngine.get_metrics_report` (`engagement.py:394`) | Rigby function-call routing | Read-only aggregation: total, by_status, by_intent, by_channel, conversion_pct |
| 7 | PA tool `engagement_sla_queue` | `td_handlers_ops.py:3102` → `EngagementAutonomyEngine.get_sla_queue` (`engagement.py:782`) | Rigby function-call routing | Read-only SLA-urgency-ranked queue |
| 8 | PA tool `engagement_meeting_suggestions` | `td_handlers_ops.py:3109` → `EngagementAutonomyEngine.get_meeting_suggestions` (`engagement.py:832`) | Rigby function-call routing | Read-only high-intent candidate list |
| 9 | PA tool `engagement_conversion_report` | `td_handlers_ops.py:3116` → `EngagementAutonomyEngine.get_conversion_report` (`engagement.py:878`) | Rigby function-call routing | Read-only funnel metrics (30d default) |
| 10 | Policy engine `_policy_engagement_engine` | `core.py:2210-2238` (invokes `EngagementEngine.evaluate` at `engagement.py:442`) | `run_ops_autopilot` beat cadence via policy registry `core.py:277` | Scheduled sweep; auto-closes stale-30d events; reports counts |
| 11 | Policy engine `_policy_engagement_autonomy` | `core.py:2390-2418` (invokes `EngagementAutonomyEngine.evaluate` at `engagement.py:966`) | `run_ops_autopilot` beat cadence via policy registry `core.py:283` | Scheduled sweep; reports SLA-breach counts + high-intent-unactioned counts + healthy boolean |
| 12 | WebSocket consumer session lifecycle | `core/revenue_opportunities_consumer.py:849` (`initialize_engagement_session`) → `EngagementMetrics.objects.create(...)` | WebSocket connect to Revenue Opportunities route | Creates one EngagementMetrics row per session; separate axis from EngagementEvent |
| 13 | WebSocket click/apply action | `revenue_opportunities_consumer.py:527` (click) / `:694` (apply) → `OpportunityInteraction.objects.create(...)` + `EngagementMetrics.calculate_metrics()` | User click / apply within active session | Real-time dual-write; populates `engagement_session` FK |
| 14 | REST `quick_apply` view | `core/views_opportunities.py:56-65` → `OpportunityInteraction.objects.create(...)` | POST from Workspace UI | Orphan-write pattern (F.C3): omits `engagement_session` FK |
| 15 | Content-pipeline `record_engagement` | `core/services/pipeline_learning.py:279` → `ContentEngagement.objects.create(...)` | External-platform metrics ingest (YouTube/TikTok/etc) | Independent axis from EngagementEvent; orthogonal learning surface |

**Missing entry points (this is the F.C1 CENTRAL deliverable):**

- No HTTP webhook receiver for reply/click/open ingestion (grep for `/api/webhooks/engagement/`, `EngagementEvent.objects.create` in `views_*.py` → 0 hits).
- No IMAP / polling task for outbound-provider inbound events (grep for `imap`, `sendgrid` inbound handlers → 0 hits in mainline).
- No signal receiver bridging OutreachDraft → EngagementEvent.
- No Celery task producing EngagementEvent rows.

## 4. Major Models

Four models compose the Category C surface area:

### 4.1 `EngagementEvent` (`core/models_engagement.py:18`, table `core_engagement_event`)

Migration: `0294_engagement_event_model.py`. Docstring (:8-14): declares "captures and classifies inbound prospect engagement (replies, meeting bookings, form fills)."

Load-bearing fields:

- `id` (UUIDField primary key)
- `outreach_draft` — FK to `OutreachDraft`, nullable, `on_delete=SET_NULL`, `related_name='engagements'` (:55-59). **Schema exists; ZERO writers at HEAD `d91d30f7`.**
- `opportunity` — FK to `Opportunity`, nullable, `on_delete=SET_NULL` (:62-66). **Schema exists; ZERO writers.**
- `user` — FK to `User`, nullable (:123-126). **Schema exists; ZERO writers (via ingestion path — no ingestion path exists).**
- `channel` — CharField choices (`email`, `linkedin`, `discord`, `other`) (:74-76).
- `intent` — CharField choices (`positive`, `neutral`, `objection`, `meeting`, `unsubscribe`, `unknown`) (:83-85), indexed.
- `status` — CharField choices (`unread`, `classified`, `needs_reply`, `actioned`, `disqualified`, `closed`) (:110-112), indexed.
- `subject_line`, `prospect_name`, `prospect_company`, `prospect_role`, `message_text`, `suggested_action`, `draft_reply`, `edited_reply`, `disqualify_reason` — text fields for content + workflow annotations.
- `suppressed` — BooleanField (:117-120), indexed. Set `True` on `intent='unsubscribe'`.
- `trace_id` — CharField (:116), indexed.
- `created_at` / `updated_at` — DateTimeFields, `created_at` indexed.

Meta: `db_table='core_engagement_event'`, `ordering=['-created_at']`, 3 compound indexes on `(status, -created_at)`, `(intent, status)`, `(channel, -created_at)`.

**Runtime state:** 0 rows written by any code path at HEAD `d91d30f7`. If any row exists in a running database, it was created via Django admin / management command / raw SQL — not through application code. Verified via grep + policy-registry surface: policy engine only *reads* (auto-closes stale-30d via `evaluate`), never creates.

### 4.2 `EngagementMetrics` (`core/models_engagement_metrics.py:14`)

Docstring (:16): "Track user engagement metrics for measuring personalization effectiveness."

Load-bearing fields:

- `id` (UUIDField)
- `user` — FK to User, `on_delete=CASCADE` (:20), non-nullable.
- `session_id` — CharField (`max_length=100`) (:23), indexed.
- `session_start` — DateTimeField `auto_now_add=True`.
- `session_end` — DateTimeField nullable (set on WebSocket disconnect at `revenue_opportunities_consumer.py:862`).
- Counters: `page_views`, `time_on_page`, `opportunities_shown`, `opportunities_clicked`, `opportunities_applied` (:28-34).
- Derived: `ctr`, `application_rate` (:38-39), computed by `calculate_metrics()` at :70-82.
- `personalized_results` (BooleanField), `personalization_boost_applied` (FloatField), `ab_test_group` (CharField choices `control`/`treatment`).
- `potential_revenue` — DecimalField.
- `created_at` / `updated_at`.

Meta: `ordering=['-created_at']`, 3 indexes on `(user, -created_at)`, `(ab_test_group, -created_at)`, `(personalized_results, -created_at)`. No `opportunity` FK.

**Runtime state:** Written by ONE site — `revenue_opportunities_consumer.py:849` `initialize_engagement_session()`. Session-scoped (one row per WebSocket connection). Session end at `:862`. Mutations during session: counter increments + `calculate_metrics()` calls inline (`:522`, `:686`, `:887`). No scheduled aggregation task.

### 4.3 `OpportunityInteraction` (`core/models_engagement_metrics.py:164`)

Docstring (:166): "Track individual opportunity interactions for detailed analytics."

Load-bearing fields:

- `id` (UUIDField)
- `user` — FK to User, `on_delete=CASCADE` (:170).
- `engagement_session` — FK to EngagementMetrics, nullable (:171). **Nullable is load-bearing — F.C3 orphan-write writer-site at `views_opportunities.py:56-65` omits this.**
- `opportunity_id` — CharField (:174). **Denormalized (not a FK to `Opportunity`)** — Agent 1 flagged as CANDIDATE F1 provenance-filter drift risk.
- `opportunity_title`, `opportunity_platform` (indexed), `opportunity_salary`.
- `interaction_type` — CharField choices `view`/`click`/`apply`/`reject` (:180-188), indexed.
- `was_personalized`, `personalization_boost`, `match_score`, `interaction_timestamp`, `time_to_interact`, `resulted_in_application`, `application_success`.

Meta: `ordering=['-interaction_timestamp']`, 3 indexes.

**Runtime state:** Written by THREE sites:
- `revenue_opportunities_consumer.py:527` (click event) — populates `engagement_session` FK.
- `revenue_opportunities_consumer.py:694` (apply event) — populates `engagement_session` FK.
- `views_opportunities.py:56-65` (REST `quick_apply`) — **omits `engagement_session` FK** (F.C3 CONFIRMED writer-site F2 orphan-write).

Readers: `views_analytics.py` (analytics per-user aggregation), `new_pages_consumer.py:406`, `orchestra_consumers.py:968`.

### 4.4 `ContentEngagement` (`core/models_pipeline_feedback.py:370`)

Docstring (:372-378): "Track engagement metrics for published content. This closes the learning loop: What gets views/completed/shared/converts."

Load-bearing fields:

- `series` — FK to `content_series`, nullable, CASCADE (:384-390).
- `episode` — FK, nullable, CASCADE (:391-397).
- `content_package` — FK, nullable, CASCADE (:398-404).
- `platform` — CharField (`youtube`, `tiktok`, `instagram`, etc.) (:407-411), indexed.
- `external_id` — CharField (external-platform-post identifier).
- Metric fields: `views`, `likes`, `shares`, `comments`, `saves`, `avg_watch_time_seconds`, `completion_rate`, `revenue`.
- `outcome` — CharField choices (`PENDING`, `DELIVERED`, `APPROVED`, `REJECTED`, `PUBLISHED`, `VIRAL`).
- `content_context` — JSONField (style_preset, voice, audience at creation).

**Runtime state:** Written by ONE site — `core/services/pipeline_learning.py:279` `PipelineLearningService.record_engagement()`. Manual API-triggered ingestion path (not automated). No FK to `EngagementEvent`, `EngagementMetrics`, or `OpportunityInteraction` — orthogonal to inbound-engagement axis (F.C4 docstring drift).

Readers: `pipeline_learning.py:746, 750`, `blog_performance_context.py:344`.

## 5. Major Services

### 5.1 `EngagementEngine` (`core/services/ops_autopilot/engagement.py:235-472`)

**Class location:** file `engagement.py`, lines 235-472. No base classes, no decorators.

**Docstring (:236-244):** "Captures and classifies inbound prospect engagement with guardrails: no auto-send (approval required), hard opt-out handling, dedup per outreach draft." (Docstring drift — captures presupposes an ingestion path; see D.C1.)

**Method surface (7 methods, 0 LLM invocations):**

| Method | Line | Intent | Read set | Write set | LLM? | Return |
|---|---|---|---|---|---|---|
| `get_inbox(now, status_filter='unread')` | 255 | PA-facing inbox with status filter | `EngagementEvent.objects.filter(suppressed=False, status=...)` | None | No | dict: events[≤20], filter, total_unread/needs_reply/classified, error? |
| `classify_event(event_id, intent, summary='')` | 297 | Classify + route to action | `EngagementEvent.objects.get(id)` | `event.intent`/`summary`/`suggested_action`/`status='classified'`; auto-suppress on `unsubscribe` | **No — operator-supplied `intent` param mapped through `INTENT_ACTIONS` dict at :312** | dict: classified, event_id, intent, suggested_action, suppressed |
| `draft_reply(event_id, reply_text)` | 330 | Store draft reply pending approval | `EngagementEvent.objects.get(id)` | `event.draft_reply`/`status='needs_reply'` | No — caller-supplied `reply_text` | dict: drafted, event_id, status |
| `approve_reply(event_id, edited_text='')` | 352 | Approve/finalize draft | `EngagementEvent.objects.get(id, status='needs_reply')` | `event.edited_reply`/`status='actioned'` | No | dict: approved, event_id, reply_text |
| `disqualify(event_id, reason='')` | 375 | Mark disqualified | `EngagementEvent.objects.get(id)` | `event.status='disqualified'`/`disqualify_reason` | No | dict: disqualified, event_id, reason |
| `get_metrics_report(now)` | 394 | Funnel + channel breakdown | Multiple `EngagementEvent.filter().count()` aggregations | None | No | dict: total, by_status, by_intent, by_channel, conversion_pct, suppressed, error? |
| `evaluate(now)` | 442 | Policy sweep: auto-close 30d-stale unread | `EngagementEvent.objects.filter(status='unread', created_at__lt=cutoff)` | `.update(status='closed')` | No | dict: unread, needs_reply, stale_closed, error? |

**INTENT_ACTIONS dict** (referenced at :312): maps caller-supplied intent string to canonical `suggested_action` value. Verifier-loop caught: this is the source of any classification "intelligence" — no LLM path exists.

**Invocation surface:**
- 6 PA tool actions at `td_handlers_ops.py:2808-2885`.
- Policy engine invoker `_policy_engagement_engine` at `core.py:2210-2238` invokes `evaluate(now)` at :2224.
- No REST endpoint / view / other consumer beyond these two.

### 5.2 `EngagementAutonomyEngine` (`core/services/ops_autopilot/engagement.py:764-1008`)

**Class location:** file `engagement.py`, lines 764-1008. No base classes, no decorators.

**Docstring (:764-775):** "Automates engagement lifecycle: SLA tracking for reply queue, auto-meeting suggestions for positive/meeting intent, engagement-to-meeting conversion tracking, and reply context assembly. Sits on top of EngagementEngine, adding: SLA-aware reply queue with time-since-receipt; Auto-meeting booking suggestions for high-intent events; Conversion funnel from engagement → meeting → deal; **Reply context builder (outreach, opportunity, meeting history)**."

**Runtime reality:** monitoring + reporting only. No "automation" mutations. No "reply context builder" method (F.C5 CONFIRMED docstring drift — see D.C5).

**Hardcoded SLA thresholds (class constants, no runtime lever):**
- `SLA_WARNING_HOURS = 4` (:778)
- `SLA_CRITICAL_HOURS = 24` (:779)
- `SLA_BREACH_HOURS = 48` (:780)

**Method surface (4 methods):**

| Method | Line | Intent | Read set | Write set | LLM? | Return |
|---|---|---|---|---|---|---|
| `get_sla_queue(now=None)` | 782 | SLA-urgency-ranked reply queue | `EngagementEvent.objects.filter(status IN [unread, classified, needs_reply])` + time-since-receipt classification | None | No | dict: events, filter, total, sla_warning, sla_critical, sla_breach |
| `get_meeting_suggestions(now=None)` | 832 | High-intent meeting-eligible candidates | `EngagementEvent.objects.filter(intent IN [positive, meeting])` | None | No | dict: candidates, needs_meeting, error? |
| `get_conversion_report(days=30)` | 878 | Engagement → meeting → deal funnel | `EngagementEvent.objects.filter(created_at__gte=cutoff)` + downstream reads | None | No | dict: period, engagement/meeting/deal counts, conversion rates |
| `evaluate(now)` | 966 | Health assessment: SLA breaches, high-intent unactioned, queue backlog | `EngagementEvent.objects.filter(...).count()` | None | No | dict: healthy (bool), sla_breaches, high_intent_unactioned, issues[] |

**Invocation surface:**
- 3 PA tool actions at `td_handlers_ops.py:3102-3122`.
- Policy engine invoker `_policy_engagement_autonomy` at `core.py:2390-2418` invokes `evaluate(now)` at :2404.

**Governance §3.23 crossover:** NONE. EngagementAutonomyEngine does not read `GovernanceState`, kill-switch, freeze mode, or throttle mode. If Governance §3.23 expects to gate engagement autonomy in the future, no wiring exists.

### 5.3 Ops Autopilot policy engine (`core/services/ops_autopilot/core.py`)

Two policy registry entries pin Category C's scheduled surface to the `run_ops_autopilot` beat cadence:

- `:277` — `('engagement', 'engagement_engine', '_policy_engagement_engine')`
- `:283` — `('engagement_autonomy', 'engagement_autonomy', '_policy_engagement_autonomy')`

`_policy_engagement_engine` (:2210-2238) instantiates `EngagementEngine()` and calls `.evaluate(now)`. Catches exceptions, logs `[OpsAutopilot] Engagement: X unread, Y needs reply, Z auto-closed`, returns result dict.

`_policy_engagement_autonomy` (:2390-2418) instantiates `EngagementAutonomyEngine()` and calls `.evaluate(now)`. Logs SLA breach + high-intent unactioned counts when `healthy=False`.

**Cadence — split verdict per F.C6 (Rigby ops probe CONFIRMED):**

- **Code-declared cadence:** `run_ops_autopilot` task docstring at `core/tasks.py:13090-13091` declares "Every 10 min: evaluate ops policies and take allowed automatic actions."
- **Runtime cadence:** **NONE at autonomous frequency.** `run_ops_autopilot` is DEFERRED-BY-POLICY per `core/celery.py:507-509` + `:633-634` comments referencing AUDIT_FINDINGS.md #12 (S1115 batch-3/batch-4 gated list — behavior-changing tasks require explicit green-light). Rigby telemetry confirms: 0 of 92 enabled PeriodicTask rows match `ops_autopilot`; 30d `celery_task_history` for `run_ops_autopilot` → 0 firings. Cross-listed as orphan in `docs/CELERY_AUDIT.md:19,37,390` (⚠ marker).
- **Ad-hoc invocation path (CONFIRMED LIVE):** `core/services/td_handlers_ops.py:1643,1674` exposes `OpsAutopilot().run()` via PA tool (Rigby-callable on operator initiation). When Chris/Rigby invoke the autopilot on-demand, all policy hooks (including engagement + engagement_autonomy) execute.

**Consequence for Category C:** the read-only surfaces (`EngagementEngine.evaluate` at `engagement.py:442`, `EngagementAutonomyEngine.evaluate` at `engagement.py:966`) execute **only when operator triggers the autopilot** via PA tool — never on autonomous 10min cadence. This is intentional per AUDIT_FINDINGS.md #12 gating; not a bug. See §14 D.C6 for the drift row.

## 6. Major APIs and Interfaces

### 6.1 PA tool surface (9 actions)

All 9 registered in `core/services/td_handlers_ops.py`:

**EngagementEngine wrappers (6):**

| Action | Line | Method | Params |
|---|---|---|---|
| `engagement_inbox` | 2808 | `get_inbox` | `status_filter` (unread\|needs_reply\|classified\|actioned\|all) |
| `engagement_classify` | 2818 | `classify_event` | `event_id`, `intent`, `summary` (optional) |
| `engagement_draft_reply` | 2835 | `draft_reply` | `event_id`, `reply_text` |
| `engagement_approve_reply` | 2848 | `approve_reply` | `event_id`, `edited_text` (optional) |
| `engagement_disqualify` | 2863 | `disqualify` | `event_id`, `reason` (optional) |
| `engagement_metrics_report` | 2878 | `get_metrics_report` | — |

**EngagementAutonomyEngine wrappers (3):**

| Action | Line | Method | Params |
|---|---|---|---|
| `engagement_sla_queue` | 3102 | `get_sla_queue` | — |
| `engagement_meeting_suggestions` | 3109 | `get_meeting_suggestions` | — |
| `engagement_conversion_report` | 3116 | `get_conversion_report` | `days` (default 30) |

Schema declarations in `core/services/pa_tool_schemas.py`. `evaluate()` (both engines) is NOT exposed via PA tool.

### 6.2 REST endpoints

None dedicated to EngagementEvent create-path. Analytics reads via `core/views_analytics.py` (`EngagementMetrics`, `OpportunityInteraction`). `core/views_opportunities.py:56-65` `quick_apply()` writes `OpportunityInteraction` (F.C3 orphan-write writer-site).

### 6.3 WebSocket consumers

`core/revenue_opportunities_consumer.py` — session-aggregation axis producer:
- Connect handler → `initialize_engagement_session()` at :849 creates `EngagementMetrics` row.
- Click action → :527 creates `OpportunityInteraction`, updates `EngagementMetrics.opportunities_clicked`.
- Apply action → :694 creates `OpportunityInteraction`, updates `EngagementMetrics.opportunities_applied`.
- Disconnect → `end_engagement_session()` at :862 sets `session_end`.

### 6.4 Event bus streams

ZERO `ENGAGEMENT_*` streams on `core/services/event_bus.py:21-31`. Symmetric to S1402's outreach finding. See §10 Event Flows for proposed additions.

## 7. Runtime Flows

Category C has three concurrent runtime flows (α = policy sweep, β = session aggregation, γ = ingestion — MISSING).

**Flow α — Policy sweep (POLICY-DEFERRED per F.C6; fires only on operator-initiated PA-tool invocation, not autonomous cadence):**

```
[Autonomous 10min cadence: DEFERRED-BY-POLICY per AUDIT_FINDINGS.md #12]
  run_ops_autopilot beat task exists (core/tasks.py:13090) but NOT registered as PeriodicTask
    → 0 of 92 enabled PeriodicTask rows match ops_autopilot
    → 30d celery_task_history for run_ops_autopilot → 0 firings
    → Rigby ops probe CONFIRMED (S1403 §20.3 verifier-loop item #10)

[Ad-hoc operator-initiated cadence: LIVE via PA tool]
Operator (Chris/Rigby) invokes autopilot via PA tool
  → td_handlers_ops.py:1643 or :1674 OpsAutopilot().run()
    → OpsAutopilot cycle iterates policy registry
      → ('engagement', 'engagement_engine', '_policy_engagement_engine')
        → EngagementEngine().evaluate(now)
          → filter EngagementEvent status='unread' created_at < now - 30d
            → .update(status='closed')
          → count unread, needs_reply, stale_closed
        → return dict → log line "[OpsAutopilot] Engagement: X unread, Y needs reply, Z auto-closed"
      → ('engagement_autonomy', 'engagement_autonomy', '_policy_engagement_autonomy')
        → EngagementAutonomyEngine().evaluate(now)
          → count SLA breaches, high-intent unactioned, queue backlog
          → return healthy boolean
        → log if unhealthy
```

Even under the ad-hoc operator-initiated path, policy hooks execute against the currently-empty `EngagementEvent` table at HEAD `d91d30f7` (F.C1 CENTRAL — no writers exist). Rigby ops probe would return "0 unread / 0 needs_reply / 0 stale_closed" if invoked at HEAD.

**Flow β — Session aggregation (WebSocket-driven, ACTIVE):**

```
User connects to Revenue Opportunities WebSocket
  → revenue_opportunities_consumer.py:849 initialize_engagement_session()
    → EngagementMetrics.objects.create(user, session_id, ab_test_group, personalized_results)

User clicks opportunity card
  → revenue_opportunities_consumer.py:527 handle_opportunity_clicked()
    → OpportunityInteraction.objects.create(user, engagement_session, opportunity_id, opportunity_title, opportunity_platform, opportunity_salary, interaction_type='click', was_personalized, ...)
    → EngagementMetrics.opportunities_clicked += 1
    → EngagementMetrics.calculate_metrics() → recompute ctr

User applies via WebSocket action
  → revenue_opportunities_consumer.py:694 handle_quick_apply()
    → OpportunityInteraction.objects.create(user, engagement_session, ..., interaction_type='apply')
    → EngagementMetrics.opportunities_applied += 1
    → EngagementMetrics.calculate_metrics() → recompute application_rate

User applies via REST endpoint (NOT WebSocket) — F.C3 orphan path
  → views_opportunities.py:56-65 quick_apply()
    → OpportunityInteraction.objects.create(user, opportunity_id, interaction_type='apply', ..., NO engagement_session)
    → EngagementMetrics NOT updated (no session context)
    → row invisible to session-aggregation rollup

User disconnects
  → revenue_opportunities_consumer.py:862 end_engagement_session()
    → EngagementMetrics.session_end = now
```

Independent of EngagementEvent axis. Verifier-loop CONFIRMED — Agents 1 + 5 both mapped this identically.

**Flow γ — Ingestion (MISSING — F.C1 CENTRAL deliverable):**

```
[proposed — does not exist at HEAD d91d30f7]

External provider sends inbound signal (email reply / LinkedIn message / meeting-book form fill)
  → provider dispatches webhook to /api/webhooks/engagement/<provider>/
    → verify HMAC signature (SendGrid / Postmark / Mailgun pattern)
    → parse payload; extract provider_message_id + sender + body
    → lookup: OutreachDraft.objects.filter(provider_message_id=X).first()
      [BLOCKER: OutreachDraft.provider_message_id field does not exist — S1402 F.B1 pair-design dependency]
    → EngagementEvent.objects.create(outreach_draft, opportunity=outreach.opportunity, user=outreach.user, channel, ...)
    → emit EventStream.ENGAGEMENT_REPLIED via event_bus.publish(...)
```

No code path implements this. Category C's canonical inbound event log exists as schema-only shell.

## 8. Data Ownership and Lifecycle

**`EngagementEvent` lifecycle (declared vs implemented):**

- Docstring-declared: `unread → classified → actioned → closed` (from `models_engagement.py:8-14` — implicit).
- Choice enum-declared: `unread`, `classified`, `needs_reply`, `actioned`, `disqualified`, `closed` (6 states).
- Runtime-implemented transitions:
  - `NULL → unread` — MISSING (F.C1 — no writer creates rows at initial state).
  - `unread → classified` via `classify_event` (`engagement.py:313`).
  - `classified → needs_reply` via `draft_reply` (`engagement.py:342`; sets `status='needs_reply'`).
  - `needs_reply → actioned` via `approve_reply` (`engagement.py:365`; requires `status='needs_reply'` filter).
  - `* → disqualified` via `disqualify` (`engagement.py:388`).
  - `* → closed` via `disqualify` (auto-close on `intent='unsubscribe'` at `classify_event`:318) OR via `evaluate` auto-close of stale-30d unread (`engagement.py:442`).

**Runtime state-machine reality:** All lifecycle transitions except `NULL → unread` are implemented. The initial creation path is entirely missing (F.C1). Existing rows (if any exist via admin/SQL) can flow through the full lifecycle cleanly.

**`EngagementMetrics` lifecycle:**

- `NULL → active session` at `revenue_opportunities_consumer.py:849` (WebSocket connect).
- Counter updates during session at `:522`/`:686`/`:887` (click/apply/dashboard refresh).
- `active → ended` at `:862` (WebSocket disconnect; sets `session_end`).
- No archival / cleanup / TTL. Rows accumulate indefinitely.

**`OpportunityInteraction` lifecycle:**

- Created inline during session actions (click/apply) at `revenue_opportunities_consumer.py:527`/`:694`.
- Created (orphan) via REST at `views_opportunities.py:56-65`.
- No mutations after creation. Immutable event log.
- No archival / cleanup.

**`ContentEngagement` lifecycle:**

- Created via `PipelineLearningService.record_engagement()` at `pipeline_learning.py:279`.
- `outcome` field mutates: `PENDING → DELIVERED → APPROVED → REJECTED / PUBLISHED / VIRAL`.
- No archival / cleanup.

## 9. Integrations With Other Domains

Integration map verified against S1274 baseline + S1401 §9.1 + S1402 §9. Verifier-loop applied.

| Adjacent domain | S1274 baseline | S1403 Category C verified | Verdict | Evidence |
|---|---|---|---|---|
| Outreach → EngagementEvent (Category B → Category C write direction) | UNKNOWN | **CONFIRMED MISSING (extends S1402 F.B3)** | CONFIRMED | Grep `EngagementEvent.objects.create\|EngagementEvent(` → only class def at `models_engagement.py:18`. Both `outreach_draft` FK (:55-59) and `opportunity` FK (:62-66) are schema-only. |
| Engagement → Outreach (Category C reads Category B) | UNKNOWN | **CONFIRMED READ-ONLY (S1402 §9 row 6)** | CONFIRMED | `revenue.py:1209-1306` `RevenueOrchestrator.get_full_pipeline` reads `EngagementEvent` for status rollup; `engagement.py:255-472` `EngagementEngine` reads only. |
| Engagement → EventBus | UNKNOWN | **NO STREAMS (matches S1402 §10 Q19 finding)** | CONFIRMED (negative) | `event_bus.py:21-31` `EventStream` enum has zero `ENGAGEMENT_*` or `OUTREACH_*` values. |
| Engagement → Meeting (Category C → Category D) | UNKNOWN | READ-only surface — `EngagementAutonomyEngine.get_meeting_suggestions` at `engagement.py:832` reads high-intent EngagementEvent rows; **no writes to Meeting model** | READ-only CONFIRMED | Direct read of method body. Meeting creation path is Category D scope. |
| Engagement → Governance (§3.23 kill-switch, freeze mode) | Not in S1274 | **NOT WIRED** | CONFIRMED (negative) | Direct read of `engagement.py:764-1008`: `EngagementAutonomyEngine` does not read `GovernanceState`, kill-switch, or freeze mode. If governance is expected to gate engagement autonomy, no wiring exists. |
| Engagement → Observability (`ImpactEvent`) | STRONG (S1274) | UNKNOWN — Category E owns | PARKED | Deferred to S1405. |
| Engagement → HumanAttention | MISSING (parent §11.4 inherited) | UNKNOWN | PARKED | Deferred to S1404. |
| Engagement → Initiative | MISSING (parent §11.4 inherited) | UNKNOWN | PARKED | Deferred to S1405. |
| Engagement → PA (Rigby function-call surface) | Not in S1274 | STRONG (9 tool actions: 6 EngagementEngine wrappers + 3 EngagementAutonomyEngine wrappers) | CONFIRMED | `td_handlers_ops.py:2808-2885` + `:3102-3122` (both surface enumerated). |
| Engagement → Ops Autopilot (policy engine) | Not in S1274 | STRONG (2 policy hooks LIVE) | CONFIRMED | `core.py:277` + `:283` registry entries; `:2210` + `:2390` invoker methods. |
| Revenue Opportunities WebSocket → EngagementMetrics + OpportunityInteraction | Not in S1274 | **STRONG (session-aggregation axis)** | CONFIRMED | `revenue_opportunities_consumer.py:849/527/694` writer inventory. |
| Content pipeline → ContentEngagement (learning loop) | Not in S1274 | STRONG for content axis; NO bridge to inbound engagement axis (F.C4 docstring drift) | CONFIRMED + REFINED | `pipeline_learning.py:279` `record_engagement()`; no FK to EngagementEvent/EngagementMetrics. |

**Producer inventory (writers of Category C models):**

| Model | Writer count | Sites |
|---|---|---|
| EngagementEvent | 0 | (F.C1 CENTRAL) |
| EngagementMetrics | 1 | `revenue_opportunities_consumer.py:849` |
| OpportunityInteraction | 3 | `revenue_opportunities_consumer.py:527`, `:694`; `views_opportunities.py:56-65` (F.C3 orphan) |
| ContentEngagement | 1 | `pipeline_learning.py:279` |

**Consumer inventory (readers of Category C models):**

- `EngagementEvent` reads: `EngagementEngine` (7 methods), `EngagementAutonomyEngine` (4 methods), `RevenueOrchestrator.get_full_pipeline` (`revenue.py:1209-1306`).
- `EngagementMetrics` reads: `views_analytics.py` (analytics dashboard), internal to consumer session state.
- `OpportunityInteraction` reads: `views_analytics.py`, `new_pages_consumer.py:406`, `orchestra_consumers.py:968`.
- `ContentEngagement` reads: `pipeline_learning.py:746, 750`, `blog_performance_context.py:344`, `experiment_metrics.py`.

## 10. Event Flows

**Q19 — What events does Category C emit?**

**None.** `core/services/event_bus.py:21-31` `EventStream` enum defines 8 streams (`SPIDER_DATA`, `OPPORTUNITY_CREATED`, `OPPORTUNITY_SCORED`, `VALIDATION_REQUIRED`, `VALIDATION_DECIDED`, `OUTCOME_RECORDED`, `MODEL_TRAINED`, `SYSTEM_ALERT`). Zero engagement-related streams. Symmetric to S1402 finding on outreach.

**Q20 — What events should Category C emit?**

The F.C1 ingestion design (§19 R.C1) proposes 4 new EventStream additions:

- `ENGAGEMENT_REPLIED` — emit from webhook handler on inbound reply detection; carries `engagement_id`, `outreach_id`, `provider_message_id`, `channel`.
- `ENGAGEMENT_OPENED` — emit from open-tracking webhook; carries `engagement_id`, `outreach_id`, timestamp.
- `ENGAGEMENT_CLICKED` — emit from click-tracking webhook; carries `engagement_id`, `outreach_id`, clicked_url.
- `ENGAGEMENT_CLASSIFIED` — emit from `classify_event` (`engagement.py:313`) after intent is set; carries `engagement_id`, `intent`, `suggested_action`.

Emissions decouple engagement ingestion from downstream consumers (Meeting auto-book / attribution / dashboard). Not implementing them means every future consumer would need to poll `EngagementEvent.status` — coupling grows quadratically.

Post-arc design-preparation candidate: adopt an engagement stream set on `EventStream` **before** wiring providers. Symmetric to S1402 §10 Q20 for outreach streams. Bundle recommendation: `OUTREACH_*` + `ENGAGEMENT_*` stream additions as a single EventBus schema PR.

## 11. Existing Documentation

**Category C has no CANONICAL topic doc.** No `docs/topics/engagement-inbound.md` or `docs/topics/engagement-pipeline.md` — matches parent §11.3 baseline that no Revenue CANONICAL topic doc exists.

**Existing partial coverage:**

| Doc | Category C coverage | Completeness | Cite-forward |
|---|---|---|---|
| `docs/PLATFORM_WHAT_IT_IS.md` | Engagement subsystem unnamed | cursory | S1223 anchor refresh |
| `docs/PLATFORM_INVENTORY.md` | Row 32 "Revenue / Outreach / Engagement Pipeline"; no Category C breakdown | targeted (row-only) | runtime anchor |
| `docs/research/platform_architecture_inventory.md` §3.32 + §4.9 | Category C named in cross-domain flow row; coverage LIGHT | cursory | S1273 v2 |
| `docs/research/platform/cross_domain_integration_audit.md` §2.4 + §5.10 | Tight-coupling classification LOW severity by design | targeted-but-narrow | S1274 |
| `docs/research/domains/revenue/1400_revenue_domain_scoping.md` §3 Cat C + §10.2 + §12.1 Cat C + §11.4 | Cat C 4-model hypothesis + F.iii questions + inherited findings | scoping-stage | S1400 |
| `docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md` | Cat A ↔ Cat B seam; no direct Cat C reference | off-target | S1401 |
| `docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md` §9 + §14 + §19 | F.B3 CONFIRMED HIGH engagement seam missing (CENTRAL S1403 inheritance) | high | S1402 |
| `00-START-NEXT-SESSION.md` (this session's start doc, lines 34-89) | Full S1403 mission spec | high (mission-defining) | S1402 close narrative |
| `docs/handoffs/SESSION_1224_OUTREACH_PIPELINE_AND_TOKEN_BUDGET_SWEEP.md` | Outreach vertical slice; no engagement writers shipped | off-target (partial mention of engagement tools) | S1224 |

**No prior handoff dedicated to Category C architecture.** Sessions 1224 + 1225 record outreach ship events; neither builds engagement writers.

## 12. Research Coverage

**Verdict: MODERATE** — upgraded from LIGHT (S1273 §3.32 baseline).

**Evidence:**

- Read-only service surfaces well-documented in `engagement.py` docstrings + code (7-method + 4-method surfaces).
- Session-aggregation axis code well-exercised at `revenue_opportunities_consumer.py` (WebSocket lifecycle + click/apply handlers).
- S1402 §9 + §14 D.B3 + F.B3 explicitly named the engagement-seam gap.
- 6-parallel-Explore sweep + parent-Claude verifier-loop CONFIRMED the axis map is 3 independent surfaces (not the parent §3 hypothesis).
- This audit synthesizes canonical event log + session aggregation + content orthogonal + ingestion gap in one document.

**Still LIGHT for:**

- Ingestion path (F.C1 CENTRAL — does not exist).
- Reply context builder (F.C5 docstring drift — declared but not built).
- Governance §3.23 crossover (not wired).

**Runtime telemetry pending Rigby ops probe** (§7 Runtime Flows referenced this):
- `run_ops_autopilot` beat cadence + hit history (confirms Flow α is exercised).
- 9 `engagement_*` PA tool usage in 30d (confirms read-only surface is consulted).
- OpportunityInteraction 30d write history split by `engagement_session=NULL` vs populated (scopes F.C3 blast radius).

## 13. Architecture Maturity

**Verdict: WORKING (code) / DEFERRED-BY-POLICY (autonomous runtime) / WORKING (session-aggregation axis) / MISSING (canonical ingestion)** — four-way split verdict per playbook §12 severity nuance and F.C6 policy-gate finding. Extends S1402 §13 WORKING/PARTIAL pattern with the additional deferred-by-policy dimension.

**Evidence FOR WORKING (code half):**

- `EngagementEngine` 7-method surface fully implemented; test references exist in codebase.
- `EngagementAutonomyEngine` 4-method surface fully implemented.
- 9 PA tool actions registered + schemas declared at `td_handlers_ops.py:2808-2885` + `:3102-3122`.
- 2 policy engine hooks (`_policy_engagement_engine` + `_policy_engagement_autonomy`) code-wired at `core.py:2210` + `:2390`; policy registry entries at `core.py:277` + `:283`.

**Evidence FOR DEFERRED-BY-POLICY (autonomous runtime half — F.C6):**

- `run_ops_autopilot` beat wrapper defined at `core/tasks.py:13090` with declared 10min cadence in docstring.
- **NOT registered as PeriodicTask** — Rigby probe: 0 of 92 enabled PeriodicTask rows match `ops_autopilot`; 30d `celery_task_history` for `run_ops_autopilot` → 0 firings.
- **Intentionally deferred per AUDIT_FINDINGS.md #12** — `core/celery.py:507-509` + `:633-634` comments explicitly name the deferral (S1115 batch-3/batch-4 behavior-changing task green-light list).
- Ad-hoc PA-tool invocation path CONFIRMED LIVE at `td_handlers_ops.py:1643,1674` — Rigby-callable via operator initiation.
- Consequence: Category C's `evaluate` sweeps fire only when operator triggers, not on autonomous cadence.

**Evidence FOR WORKING (session-aggregation axis half — CODE tier only; RUNTIME tier is "dormant-in-local, prod-unknown"):**

- Session-aggregation axis WORKING at CODE tier end-to-end: WebSocket connect → EngagementMetrics.create → click/apply → OpportunityInteraction.create + counter update → CTR/application_rate computed → analytics reads via `views_analytics.py`.
- Redis / cache pattern is short-TTL (5min via `revenue_opportunities_consumer.py:302-306`); does not risk long-term staleness.
- All 4 methods on the axis (`initialize_engagement_session`, `handle_opportunity_clicked`, `handle_quick_apply`, `end_engagement_session`) fully wired.
- **Empirical RUNTIME LOCAL check (Rigby cycle 1 must-fix #1 fold, 2026-07-01):** `EngagementMetrics.objects.count() = 0`, `OpportunityInteraction.objects.count() = 0`, `ContentEngagement.objects.count() = 0`. Session-aggregation axis has NEVER been exercised in this local env (nobody has connected to Revenue Opportunities WebSocket). Not a bug — dev env behavior. PROD counts unknown (T.C8 tool gap — Rigby's `db_health_tool env=prod` returns "not configured: PA_DB_HEALTH_RPC_URL, PA_DB_HEALTH_RPC_CLIENT_TOKEN"). **Evidence tier: code-path CONFIRMED WORKING + runtime-local CONFIRMED DORMANT + runtime-prod PENDING.**
- Nuance to §1 executive framing: revise "WORKING but disconnected" to "WORKING (code) / DORMANT (runtime local) / PROD UNKNOWN" — matches the analogous F.C6 4-way-split pattern.

**Evidence FOR MISSING (canonical ingestion half):**

- Zero `EngagementEvent` writer sites at HEAD `d91d30f7` (F.C1 CONFIRMED HIGH) — Rigby ops probe cross-corroborates via repo_tool grep + celery_task_history 30d name_contains=engagement → 0 hits.
- Both `outreach_draft` and `opportunity` FKs are schema-only (extends S1402 F.B3).
- No HTTP webhook receiver, no polling task, no signal, no consumer produces rows.
- No `ENGAGEMENT_*` event streams on event_bus.
- BLOCKER: `OutreachDraft.provider_message_id` field does not exist — required for webhook correlation, must be added as pre-work to F.B1 delivery ADR (pair-design per §19 R.C1).

**No evidence** of critical breakage on services or session aggregation. Canonical ingestion is a **missing subsystem**, not a broken one. Autonomous cadence is deferred by policy, not by bug. WORKING/DEFERRED-BY-POLICY/WORKING/MISSING is accurate.

**Additional Rigby telemetry pending** (PA tool 30d usage for `engagement_*` actions + OpportunityInteraction 30d write split by `engagement_session=NULL`): Rigby noted she does not currently have exposed tools for ToolCallRecord queries or ORM row splits. Deferred; not blocking SIGN. §14 D.C6 tracks the exposed-tool gap as INHERITED debt.

## 14. Known Drift

Drift matrix — where documented claims mismatch runtime reality:

| # | Source doc/claim | Runtime reality | Severity | Recommendation |
|---|---|---|---|---|
| D.C1 | `EngagementEvent` model docstring (`models_engagement.py:6-14`) + `EngagementEngine` docstring (`engagement.py:236-244`) both say "**captures and classifies** inbound prospect engagement." | **Captures presupposes a writer path; no writer exists.** Grep `EngagementEvent.objects.create` → 0. Classification is operator-supplied (not LLM) via `intent` param mapped through `INTENT_ACTIONS` dict at `engagement.py:312`. | **MEDIUM** (docstring overstates by naming behavior that doesn't run at HEAD; not runtime failure since services still work on any manually-created rows) | Update docstrings to reflect implemented lifecycle ("**Classifies** already-ingested prospect engagement" + "ingestion path pending F.B1/F.C1 pair-design ADR"). Bundle with §19 R.C4 doc anchor updates. |
| D.C2 | `EngagementEngine.classify_event` name + parent §3 Cat C phrasing "classify_event LLM path" | **Not an LLM path.** Method takes `intent: str` as caller-supplied parameter (line 297 signature); INTENT_ACTIONS dict (:312) maps intent → suggested_action. No `get_openai_client()` invocation. | **LOW** (naming ambiguity, not functional drift); the method IS a classifier if you consider the caller (operator via PA tool) as the classifier | Rename param `intent` → `intent_from_operator` OR update method docstring to explicitly state "intent supplied by caller (typically operator via PA tool `engagement_classify`), not inferred." |
| D.C3 | `EngagementEvent.STATUS_CHOICES` enum defines 6 states (unread, classified, needs_reply, actioned, disqualified, closed). Docstring at :8-14 names only 4 (`unread → classified → actioned → closed`). | Enum has 6 states; docstring names 4. Actual state-machine implements 5 (`classified → needs_reply` via draft_reply; `needs_reply → actioned` via approve_reply are runtime transitions the docstring omits). | **LOW** (docstring simplifies runtime; not misleading operators, but code readers will find gap between docstring and enum) | Update docstring to enumerate full 6-state machine + transitions. |
| D.C4 | `ContentEngagement` docstring (`models_pipeline_feedback.py:372-378`): "This closes the learning loop: What gets views/completed/shared/converts." | **The loop is NOT closed.** `ContentEngagement` has FK to `series`/`episode`/`content_package` but **no FK to `EngagementEvent`, `EngagementMetrics`, or `OpportunityInteraction`**. Docstring implies a feedback bridge back to inbound engagement attribution; runtime has no such bridge. | **CONFIRMED HIGH docstring / MEDIUM runtime** (functional-but-partial: axis is complete for content-outcome-analytics, but the declared "learning loop" is a partial claim) | Update docstring to accurately describe scope: "Track engagement metrics for published content (views/watch-time/shares/conversions). Independent of inbound engagement (EngagementEvent) — bridge to close full learning loop is a post-arc design-preparation candidate." Alternative: design + implement FK bridge (larger scope; §19 R.C5). |
| D.C5 | `EngagementAutonomyEngine` docstring (`engagement.py:764-775`) lists "**Reply context builder (outreach, opportunity, meeting history)**" as one of four value-adds. | **No reply-context-builder method exists.** Direct read of class body :764-1008 shows only 4 methods (`get_sla_queue`, `get_meeting_suggestions`, `get_conversion_report`, `evaluate`). | **LOW-MEDIUM** (aspirational docstring; the value-add is real for operators but not shipped) | Two forks: (i) delete "Reply context builder" from docstring (accepts the drift) — matches memory rule `feedback_docs_never_delete` compatibly since it's editing a docstring, not deleting a doc; (ii) build the method (post-arc); (iii) reframe docstring as "planned surface" section. |
| D.C6 | `run_ops_autopilot` task docstring at `core/tasks.py:13090-13091` declares "Every 10 min: evaluate ops policies and take allowed automatic actions." | **NOT registered as PeriodicTask at runtime** (Rigby probe: 0 of 92 enabled PeriodicTask rows match `ops_autopilot`; 30d `celery_task_history` → 0 firings). **Intentionally deferred per AUDIT_FINDINGS.md #12** — `core/celery.py:507-509` + `:633-634` name it as a behavior-changing task awaiting explicit green-light. Ad-hoc PA-tool invocation path exists at `td_handlers_ops.py:1643,1674` (operator-initiated). | **DEFERRED-BY-POLICY (not a bug)** — code-vs-runtime drift is intentional and named in AUDIT_FINDINGS.md #12 | **Rigby cycle 1 Q1 lean: (iii) Separate ADR outside G1400 arc.** Flipping `run_ops_autopilot` is a cross-category "big switch" activating many policy hooks simultaneously — architectural/governance scope, not category-specific. Recommendation: (i) update task docstring to match current gating ("Every 10 min WHEN enabled; deferred per AUDIT_FINDINGS.md #12 until explicit green-light") as a small landing NOW; (ii) open dedicated ADR outside G1400 arc for the enable-decision (owns cross-category impact analysis, kill-switch integration with Governance §3.23, cost-model for LLM policy hooks); (iii) G1400 xx99 canonical summary CROSS-LINKS the ADR rather than proposing enablement itself. Memory rule `feedback_audit_findings_12_canonical_celery_deferred_list.md` triggered pre-SIGN to correctly classify. |

## 15. Known Technical Debt

Debt matrix — Category-C-scoped items grounded in code evidence:

| # | Debt | Evidence | Severity | Recommendation |
|---|---|---|---|---|
| T.C1 | F.C3 `views_opportunities.py:56-65` OpportunityInteraction orphan-write writer-site — omits `engagement_session` FK | Direct read: line 56-65 creates row with `user`, `opportunity_id`, `opportunity_title`, `opportunity_platform`, `opportunity_salary`, `interaction_type='apply'`, `was_personalized=True`, `resulted_in_application=True`. No `engagement_session=` argument. Consumer path at `:527`/`:694` always populates it. | **MEDIUM** (runtime blast radius: bounded to REST `quick_apply` flow only; WebSocket path is consistent) | Fix: change REST quick_apply to look up current active EngagementMetrics session for user OR add engagement_session=None explicit + document orphan pattern as intentional. Related work: F1/F2 lens repo-wide sweep. |
| T.C2 | `OpportunityInteraction.opportunity_id` is `CharField(max_length=100)` (`models_engagement_metrics.py:174`) — NOT a FK to `Opportunity` | Direct read; parent `EngagementMetrics` counts `opportunities_shown/clicked/applied` as integer counters (not row-count agg). No shared key for reconciliation between denormalized string + count. | **LOW-MEDIUM** (CANDIDATE F1 provenance-filter drift from Agent 1) | Migration to make `opportunity_id` a `UUIDField` FK to Opportunity. Requires backfill of existing rows + reconciliation. Post-arc design-preparation. |
| T.C3 | `EngagementAutonomyEngine` SLA thresholds hardcoded as class constants (`engagement.py:778-780`); no runtime lever | Direct read: `SLA_WARNING_HOURS = 4`, `SLA_CRITICAL_HOURS = 24`, `SLA_BREACH_HOURS = 48`. No settings.py override, no DB-backed autonomy state, no admin UI. | **LOW** (config-as-code, but for a monitoring surface; not customer-facing SLA declarations) | Convert to `settings.py` variables OR to `EngagementAutonomyConfig` model row (per-workspace scope if needed). Post-arc. |
| T.C4 | Category C has no dedicated Celery queue routing | Grep `task_routes` in `settings.py` for engagement-related routes → 0 matches. `run_ops_autopilot` beat runs against generic queue. | **LOW** (no dedicated queue means engagement policy sweep shares a worker with other ops policies; scaling concern only if engagement telemetry volume grows) | **Rigby cycle 2 Q7 lean: POST-ARC.** Bundle with S1402 T.B8 as potential unified `revenue_ops` queue for A + B + C policy sweeps. Rigby rationale: "Queue unification is a routing/priority coupling change; do it once inbound ingestion + outbound delivery are settled so you don't accidentally change latency/throughput characteristics for unrelated ops tasks." Queue-affinity concern to plan for: today's shared-queue is a blast-radius multiplier; unified `revenue_ops` helps isolate revenue ops from content/stocks — but **only if accompanied by explicit worker sizing + concurrency caps so it doesn't become a single choke point**. |
| T.C5 | `EngagementEvent` fields include `subject_line`, `prospect_name`, `prospect_company`, `prospect_role`, `message_text`, `suggested_action`, `draft_reply`, `edited_reply`, `disqualify_reason` — all schema-only until F.C1 ingestion path lands | Direct read of model at `models_engagement.py:18-140`. F.C1 CONFIRMED zero-writers. | **INHERITED-LOW** (schema breadth is pre-planned for ingestion — not debt until ingestion is implemented + fields prove wrong) | Monitor: when F.C1 ingestion writer contract is designed, verify all these fields are actually populated by the webhook parser. If any are structurally unused, prune in a follow-up migration. |
| T.C6 | S1274 §2.8 EventBus adoption debt (INHERITED-HIGH) applies to Category C's future `ENGAGEMENT_*` streams | S1274 §2.8 v2: EventBus is "partially implemented, weakly adopted, unverified end-to-end." Only 1 of 8 streams has confirmed caller sweep. Category C's proposed 4 new streams would need caller-sweep + observability wiring at add-time. | **INHERITED-MEDIUM** | Bundle EventStream additions with S1402 T.B8 nice-to-have + observability instrumentation. Post-arc. |
| T.C7 | Redis 5min cache TTL in `revenue_opportunities_consumer.py:302-306` (CANDIDATE F3 lens from Agent 5) | Direct read: consumer caches "latest_opportunities" in Redis with `timeout=300`. Impacts real-time analytics if spider network fails; historical analytics unaffected. | **LOW** (short TTL; scoped to consumer, not to engagement state) | Monitor. If real-time engagement metrics show staleness pattern, revisit. |
| T.C8 | Rigby ops-probe tool surface gap — three closure checkboxes (cycle 2 nice-to-have #2 split): **(a) tool query surface** — no exposed way to query PA-tool telemetry (`ToolCallRecord`) by action name for 30d usage; **(b) bounded counts** — no exposed SQL/ORM tool to run bounded read-only `.count()` / grouped counts for common audit patterns (blocked cycle 1 must-fix #1 attempts); **(c) prod reach** — `db_health_tool env=prod` returns "not configured: missing PA_DB_HEALTH_RPC_URL, PA_DB_HEALTH_RPC_CLIENT_TOKEN" — parent-Claude Django ORM count can only reach LOCAL env, so PROD F.C1/F.C3 empirical falsification blocked. | Rigby explicitly stated during F.C6 probe + cycle 1 close: "I don't currently have an exposed ops tool that can query ToolCallRecord/PA tool telemetry" + "I don't have a direct DB query/ORM telemetry tool exposed here to count OpportunityInteraction" + `db_health_tool env=prod` "not configured" error. | **INHERITED-MEDIUM** (blocks 3 verifier-loop questions at S1403 SIGN; not Category C-specific) | **Rigby cycle 2 Q8 lean: IMMEDIATE arc-support tools.** Rigby rationale: "This gap is directly blocking audit verification loops (as you just experienced) and forces manual shell work. Read-only observability surfaces (ToolCallRecord query, safe row-count endpoints, and configured prod DB health RPC) are low-risk, high-leverage — land them now, then later fold deeper observability into Group 1700." Implementation: (a) expose `ops_tool action=tool_call_history name_contains=X window=30d` (mirrors `celery_task_history`); (b) expose bounded read-only ORM-count tool for common audit patterns; (c) configure `PA_DB_HEALTH_RPC_URL` + `PA_DB_HEALTH_RPC_CLIENT_TOKEN` env vars for prod reach. Log to arc-open queue (not post-arc) per Rigby cycle 2 lean. |

## 16. Boundary Violations

None identified within Category C's own scope. Category C is small and read-only-service-heavy — few opportunities for boundary violation.

**Adjacent boundaries checked:**

- Engagement → Outreach: read-only (§9 confirmed).
- Engagement → Meeting: read-only reference (via `get_meeting_suggestions`); write direction is Category D scope.
- Engagement → Opportunity: read-only (via `EngagementEvent.opportunity` FK — currently NULL for all rows since F.C1).

## 17. Duplicate or Overlapping Systems

Three observations:

### 17.1 EngagementMetrics + OpportunityInteraction vs EngagementEvent

**Not duplicates — different axes.** EngagementMetrics + OpportunityInteraction capture session-scoped click/apply behavior against Opportunity rows (WebSocket-driven). EngagementEvent (schema-only) is designed for outbound-outreach-reply signal. Parent §3 hypothesized they'd resolve onto the same axis; verifier-loop refuted. Two independent axes with different write triggers.

**Design question surfaced:** Should the two axes be unified? Options:

- (a) Keep separate — they serve different purposes (session UX telemetry vs prospect-reply attribution).
- (b) Unify — refactor EngagementMetrics to be a rollup of EngagementEvent (which would require F.C1 ingestion path + a UX-telemetry event-source split).
- (c) Bridge — add signal receivers that write EngagementEvent rows for salient session events (e.g., high-intent click → auto-classify as `positive`) — creates flow between the two axes without conflating them.

Post-arc design-preparation candidate: adjudicate (a)/(b)/(c) at S1499 xx99 canonical summary or in a dedicated ADR.

### 17.2 `ContentEngagement` vs `EngagementEvent`/`EngagementMetrics`

**Not duplicates — orthogonal.** ContentEngagement captures published-content outcome analytics (YouTube views, TikTok likes, etc.). No overlap with inbound-prospect-engagement. Docstring drift (F.C4) implies a bridge that doesn't exist; the two axes are actually independent.

### 17.3 `EngagementEngine` vs `EngagementAutonomyEngine` responsibility split

Parent §3 Cat C called these two engines "on top of" each other. Direct read confirms: they operate on the same `EngagementEvent` table but do not delegate methods to each other (Agent 3 verified). Split is doctrinal, not compositional. Reasonable — SLA reporting vs core lifecycle mgmt.

## 18. Ownership Gaps

**Category C has NO runtime owner.** Verifier-loop CONFIRMED:

- **No `JobContract` wiring.** `core/employees/jobs.py` grep for "engagement" (case-insensitive) → 0 hits. None of the 3 shipped employees (Documentation Manager / Platform Auditor / Chief of Staff) name engagement in their `JobContract`.
- **No `AGENT_MAP` entry.** `core/agent_router.py` grep for "engagement" / "Engagement" → 0 hits. Category C is a service, not an agent.
- **No dedicated queue.** `settings.py` `task_routes` has no engagement entries.
- **No beat schedule row.** Category C surfaces are exercised only via the shared `run_ops_autopilot` policy engine cadence — no dedicated engagement beat task.

**Inheritance from S1274 §14 finding #36 (unclear_owner HIGH):** CONFIRMED for Category C. Combined with S1402's identical finding for Category B (composition path also has no dedicated owner), Group 1400's ownership gap is now **CONFIRMED at Categories A + B + C** (S1401 also inherited to Category E per D28).

**Recommendation:** Deferred to S1405 Child E per parent §12.1 D28 arc-scoping decision. S1499 xx99 canonical summary should propose the arc-wide runtime-owner JobContract based on Category E synthesis.

## 19. Recommended Future Research

Category-C-specific design-preparation ADRs + post-arc research items:

### R.C1 — F.C1 Ingestion path ADR (CENTRAL S1403 deliverable — design-preparation, not implementation)

Design the webhook receiver + writer contract + event-bus stream for `EngagementEvent` ingestion. Depends on (must pair-design with):

- **F.B1 delivery-path ADR** (from S1402 §19 R.B1). Ingestion presupposes sent outreach. `OutreachDraft.provider_message_id` field does not exist; must be added as pre-work at F.B1 to enable webhook-side correlation. **Rigby cycle 1 Q4 lean: (ii) Two sequential ADRs — F.B1 delivery first (establishes channel + identifiers), F.C1 inbound ingestion stacked on top (specifies webhook/poller contracts keyed to those identifiers). Rigby rationale: "cleaner dependency ordering and less thrash." Fold: change from "bundle recommendation" to "sequential recommendation" — F.B1 must land + close before F.C1 opens.**

Design content:

- **Provider landscape (Phase 1: email-only):** SendGrid Parse API, Postmark inbound, Mailgun inbound, SES via SNS. LinkedIn deferred (polling-only, rate-limited). Discord DM deferred (gateway event, non-webhook).
- **URL pattern:** `POST /api/webhooks/engagement/<provider>/` (SendGrid, Postmark, Mailgun).
- **Handler location:** new file `core/views_engagement_webhooks.py` — reuse patterns from `core/views_stripe.py:41-53` for `@csrf_exempt` + `@require_POST` + HMAC signature verify.
- **Writer contract:** `EngagementEvent.objects.create(outreach_draft=..., opportunity=outreach.opportunity, user=outreach.user, channel=..., prospect_name=..., message_text=..., subject_line=..., status='unread', intent='unknown', trace_id=outreach.trace_id)`.
- **Idempotency:** `get_or_create(outreach_draft=..., provider_message_id=...)` OR unique_together on (`outreach_draft`, `provider_message_id`).
- **EventStream additions:** `ENGAGEMENT_REPLIED`, `ENGAGEMENT_OPENED`, `ENGAGEMENT_CLICKED`, `ENGAGEMENT_CLASSIFIED` (§10 Q20 above).
- **Aggregation seam:** post_save signal on EngagementEvent → EngagementMetrics update (if unified with session aggregation) OR Celery task rollup on cadence.
- **Feature-gate:** `settings.ENGAGEMENT_INGESTION_ENABLED` per `feedback_workflow_step_sentinel_plus_noncritical_pattern` pattern.

### R.C2 — F.C3 OpportunityInteraction orphan-write fix (small; landable in F.B1 pair)

Direct fix at `views_opportunities.py:56-65`: look up user's current active EngagementMetrics session and populate `engagement_session=` FK. Alternative: document intentional orphaning + change `EngagementMetrics.session_id` to accept a synthetic REST-session ID. Small landing; can go alongside F.B1/F.C1 pair.

### R.C3 — F.C4 ContentEngagement learning-loop bridge (post-arc, dependencies on Category D + E)

Two forks: (i) narrow docstring to match runtime (D.C4 recommendation); (ii) build the FK bridge from `ContentEngagement` → `EngagementEvent` (or `EngagementMetrics`) so published content outcomes can attribute back to inbound engagement. Post-arc — bundle with Category D + E work per parent §12.4 deferred adjacent arcs. **Rigby cycle 1 Q5 lean: (i) narrow docstring NOW; track FK bridge as post-arc build if still desired.** Rigby rationale: "Claiming 'closes the learning loop' is materially misleading without linkage." Fold applied to D.C4 recommendation.

### R.C4 — Documentation anchor updates (immediate — matches S1402 §14 D.B3 anchor-update discipline)

**Rigby cycle 2 Q9 lean applied — expanded §3.32 recommendations:**

- `docs/research/platform_architecture_inventory.md` §3.32: update Revenue → Engagement row to reflect three per-model annotations:
  - **`EngagementEvent`**: schema present; ingestion missing; local runtime count=0 (prod unknown until RPC configured).
  - **`EngagementMetrics` / `OpportunityInteraction`**: aggregation axis; code working; **local runtime count=0 due to no WebSocket activity** — annotation prevents future readers from misclassifying as broken.
  - Short note: "engagement inbound currently relies on session/WebSocket surfaces, not canonical event ingestion."
- Update coverage LIGHT → MODERATE for Category C.
- `docs/research/platform/cross_domain_integration_audit.md`: add row for Engagement → Governance MISSING (§9 verified negative). Update Engagement → EventBus row to CONFIRMED NO STREAMS.
- No PLATFORM_INVENTORY.md update required (research audit only).

### R.C5 — R.C1 blocker resolution: `OutreachDraft.provider_message_id` migration

Explicit micro-ADR:

- Add `provider_message_id = CharField(max_length=200, blank=True, null=True, db_index=True)` to `OutreachDraft`.
- Precedent: `core/models_content_pipeline.py:delivery_message_id` + `mark_delivered()` method (line 50-55) — same pattern.
- Blocks R.C1 CENTRAL. Blocks F.B1 delivery ADR full implementation.
- Small landing (single-field migration).

### R.C6 — EngagementAutonomyEngine "reply context builder" fork (D.C5 resolution)

**Rigby cycle 1 Q6 lean: (iii) Reframe as "planned surface"** (per truncated response — cycle 2 will confirm the trailing clause). Post-arc if build path chosen.

### R.C7 — Governance §3.23 crossover ADR (bundle with Group 1700 Observability arc when it opens)

Should engagement autonomy (SLA thresholds, auto-close behavior) be gated by Governance kill-switch / freeze mode? Currently no wiring. If yes, add read of `GovernanceState` in `EngagementAutonomyEngine.evaluate` — pause auto-close on freeze. Bundle with Group 1700.

### R.C8 — F1 provenance-filter drift repo-wide sweep (S1399 §4 F1 lens application, extends to Category C readers)

Category C readers (`EngagementEngine.get_inbox` etc.) filter on `suppressed`, `status`, `intent`. Repo-wide sweep for EngagementEvent readers using other filter fields (`channel`, `prospect_company`, `trace_id`) may reveal provenance drift. Deferred until F.C1 ingestion writer contract lands (writers must exist before drift can be measured).

## 20. Appendix

### 20.1 Files inspected

- `core/models_engagement.py` (147 lines) — EngagementEvent model
- `core/models_engagement_metrics.py` (250 lines) — EngagementMetrics + OpportunityInteraction models
- `core/models_pipeline_feedback.py` (§370-450 for ContentEngagement)
- `core/services/ops_autopilot/engagement.py` (1008 lines) — EngagementEngine + EngagementAutonomyEngine + MeetingEngine
- `core/services/ops_autopilot/core.py` — policy registry (:277, :283) + policy hooks (:2210, :2390)
- `core/services/td_handlers_ops.py` (:2808-2885 EngagementEngine wrappers; :3102-3122 AutonomyEngine wrappers)
- `core/revenue_opportunities_consumer.py` (:849 init, :527 click, :694 apply, :862 disconnect, :302-306 Redis cache)
- `core/views_opportunities.py` (:56-65 orphan-write writer-site)
- `core/services/pipeline_learning.py` (:279 ContentEngagement writer)
- `core/models_outreach.py` (grep-negative for `provider_message_id`)
- `core/services/event_bus.py` (:21-31 EventStream enum — grep-negative for engagement/outreach streams)
- `core/employees/jobs.py` (grep-negative for engagement JobContract)
- `core/agent_router.py` (grep-negative for engagement agent)
- Migrations: `0294_engagement_event_model.py:140-148` — EngagementEvent FK schema
- Docs referenced: parent scoping `1400_revenue_domain_scoping.md`; sibling S1401 + S1402; S1273 §3.32 + §4.9; S1274 §2.4 + §5.10 + §14 #36; `00-START-NEXT-SESSION.md`

### 20.2 Sub-agent evidence provenance (§13 6-parallel-Explore sweep)

| Agent | Scope | Report length | Key contribution | Corrections applied by verifier-loop |
|---|---|---|---|---|
| 1 | 4 engagement models canonicity + axis | ~1200 words | Refuted parent §3 Cat C axis hypothesis; expanded S1402 F.B3 to include `EngagementEvent.opportunity` FK | none — findings held |
| 2 | EngagementEngine read/write graph | ~1200 words | Confirmed 6 PA tool actions; `evaluate` LIVE via policy engine; `classify_event` is NOT LLM path | Class location :235 not :255 as parent doc said |
| 3 | EngagementAutonomyEngine gating | ~1000 words | Confirmed 4 methods + hardcoded SLA thresholds; no governance §3.23 crossover; D.C5 docstring drift | none — findings held |
| 4 | F.B3 ingestion path design (CENTRAL) | ~1500 words | Full design-preparation deliverable: webhook receiver + EventStream additions + writer contract + idempotency; BLOCKER on `OutreachDraft.provider_message_id` | none — findings held |
| 5 | EngagementMetrics aggregation | ~1000 words | Matched Agent 1's axis-map refutation independently; F2 CANDIDATE identified at `views_opportunities.py:56-65`; F3 CANDIDATE at consumer 5min Redis cache | F2 CANDIDATE upgraded to CONFIRMED via parent-Claude direct read |
| 6 | Docs + prior research + drift/debt/ownership/maturity | ~1200 words | Full ownership gap CONFIRMED; MODERATE coverage upgrade; sub-agent claim T.C4 dead-code risk for EngagementAutonomyEngine | **T.C4 REFUTED** — direct read of `core.py:2390-2418` confirms LIVE invoker; not carried to audit |

### 20.3 Parent-Claude verifier-loop provenance

Pre-SIGN direct-read verifications executed:

1. **EngagementEvent zero-writer** (grep + direct read): CONFIRMED — only class definition at `models_engagement.py:18`.
2. **EngagementEngine.evaluate invoker** (`core.py:2210-2238`): CONFIRMED LIVE.
3. **EngagementAutonomyEngine.evaluate invoker** (`core.py:2390-2418`): CONFIRMED LIVE. **Agent 6 T.C4 dead-code overreach REFUTED.**
4. **OutreachDraft.provider_message_id field** (grep `models_outreach.py`): CONFIRMED MISSING — Agent 4 BLOCKER holds.
5. **F.C3 OpportunityInteraction orphan-write** (direct read `views_opportunities.py:45-65`): CONFIRMED — writer omits `engagement_session` FK. Upgrade Agent 5 CANDIDATE → CONFIRMED.
6. **classify_event LLM claim** (direct read `engagement.py:297-328`): CONFIRMED not LLM — operator-supplied `intent` param via INTENT_ACTIONS dict lookup. Parent §3 Cat C implicit assumption WRONG.
7. **EngagementAutonomyEngine docstring "reply context builder"** (direct read `engagement.py:764-1008`): CONFIRMED docstring drift — no such method exists.
8. **Ownership gap** (grep `jobs.py` + `agent_router.py` + `settings.py` `task_routes`): CONFIRMED HIGH.
9. **PA tool count** (grep `td_handlers_ops.py`): CONFIRMED 9 total (6 EngagementEngine + 3 EngagementAutonomyEngine) — corrects Agent 2's undercount.
10. **F.C6 `run_ops_autopilot` deferred-by-policy dormancy** (Rigby ops probe + parent-Claude direct read `celery.py:507-509,633-634` + `tasks.py:13090` + `CELERY_AUDIT.md:19,37,390` + `td_handlers_ops.py:1643,1674`): CONFIRMED. `run_ops_autopilot` beat wrapper defined + docstring declares 10min cadence, but NOT registered as PeriodicTask + 0 30d firings; deferred per AUDIT_FINDINGS.md #12 gating. Ad-hoc PA-tool path exposes on-demand invocation at `td_handlers_ops.py:1643,1674`. Memory rule `feedback_audit_findings_12_canonical_celery_deferred_list.md` correctly classified this as INHERITED-BY-POLICY, not new bug. This finding is the parent-Claude + Rigby joint verifier-loop CONFIRMATION analog to S1402 D.B7 methodology extension — same joint pattern (Rigby ops probe + parent-Claude direct read jointly CONFIRM runtime-liveness).
11. **F.C1/F.C3 empirical runtime row-count** (parent-Claude Django ORM `.count()` via `manage.py shell`, local env, 2026-07-01, in response to Rigby cycle 1 must-fix #1 — she reported `db_health_tool` returned `row_count=-1` estimated + `ops_tool.sql_query` did not return successfully). Results: `EngagementEvent.objects.count() = 0` (F.C1 CONFIRMED at RUNTIME in addition to CODE); `EngagementMetrics.objects.count() = 0` (§13 WORKING-session-agg CODE tier holds; RUNTIME LOCAL tier DORMANT — nobody has connected to WebSocket in dev); `OpportunityInteraction.objects.count() = 0` (F.C3 orphan-write RUNTIME BLAST RADIUS = ZERO in local — sibling to S1402 F.B2 zero-blast-radius pattern); `ContentEngagement.objects.count() = 0` (F.C4 docstring drift MOOT at runtime locally, code drift still real). **PROD status UNKNOWN** — Rigby's `db_health_tool env=prod` returned "not configured: missing PA_DB_HEALTH_RPC_URL, PA_DB_HEALTH_RPC_CLIENT_TOKEN" — T.C8 debt row extends to include the prod-DB reach gap. Third joint verifier-loop CONFIRMATION cycle (after Rigby ops probe on F.C6 and parent-Claude direct read on multiple sub-agent claims).

Runtime telemetry that Rigby's current tool surface cannot yet reach (deferred to T.C8 post-arc surface additions):
- 30d PA-tool usage counts for `engagement_*` actions (no exposed ToolCallRecord query tool).
- OpportunityInteraction 30d write split by `engagement_session=NULL` vs populated at PROD (blocked by prod-DB tool gap).
- Any Category C row counts at PROD (blocked by prod-DB tool gap).

Fold into §7/§12/§13 completed same-draft (F.C6 add + §5.3 refinement + §7 Flow α refinement + §13 four-way split + D.C6 drift row + T.C8 debt row); cycle 1 fold applied post-Rigby SIGN cycle 1 (evidence-tier markers added to F.C1 + F.C3 + §13 session-agg axis half; D.C6 Q1 (iii) fold; R.C1 Q4 (ii) fold; R.C3 Q5 (i) fold; R.C6 Q6 (iii) fold). Cycle 2 fold applied post-Rigby SIGN cycle 2 SIGN-clean High confidence (T.C4 Q7 fold: post-arc + queue-affinity worker-sizing warning; T.C8 Q8 fold: three-checkbox split (a)/(b)/(c) + immediate arc-support tools lean; R.C4 Q9 fold: expanded §3.32 anchor-update recommendation with per-model annotations for EngagementEvent/EngagementMetrics/OpportunityInteraction + session-vs-canonical clarifying note).

**§20.3.1 Env Coverage Table (cycle 2 nice-to-have #1 add — reusable pattern for future audits):**

| Env | F.C1 (EngagementEvent) | F.C3 (OpportunityInteraction orphan) | Session-agg axis (EngagementMetrics count) | Method | Status |
|---|---|---|---|---|---|
| LOCAL | 0 rows CONFIRMED | 0 rows CONFIRMED (bounded ZERO blast radius) | 0 rows CONFIRMED (dormant, not broken) | parent-Claude Django ORM `.count()` via `manage.py shell` | PROBED 2026-07-01 |
| PROD | UNKNOWN | UNKNOWN | UNKNOWN | Rigby `db_health_tool env=prod` blocked — "PA_DB_HEALTH_RPC_URL, PA_DB_HEALTH_RPC_CLIENT_TOKEN not configured" | BLOCKED (T.C8 (c)) |
| STAGING | N/A | N/A | N/A | Not probed in S1403 scope | DEFERRED |

### 20.4 Category C canonical Q's answered

Parent §12.1 Category C questions (F.iii):

- **Q1 (canonical engagement model identity)?** ANSWERED §1 + §4 + §17: EngagementEvent is the parent-declared canonical inbound event log but is runtime-empty; corrected axis map treats it, EngagementMetrics+OpportunityInteraction, and ContentEngagement as three independent surfaces.
- **Q2 (event stream vs aggregate axis)?** ANSWERED §17.1: not the parent §3 hypothesis; three independent axes (canonical=schema-only; session-agg=WebSocket-driven; content=orthogonal). Options (a)/(b)/(c) surfaced for post-arc adjudication.
- **Q3 (EngagementAutonomyEngine gating + default state)?** ANSWERED §5.2: monitoring + reporting only; NOT gating. SLA thresholds hardcoded (4h/24h/48h). Default state: no autonomy mutations, no autonomous replies. No governance §3.23 crossover.
- **Q4 (F.B3 ingestion path design)?** ANSWERED §19 R.C1: webhook receiver at `/api/webhooks/engagement/<provider>/` reusing Stripe pattern; 4 new EventStream additions; writer contract + idempotency + feature-gate. BLOCKER: `OutreachDraft.provider_message_id` missing (R.C5 micro-migration). Pair-design with F.B1 delivery ADR recommended.

### 20.5 Open questions for Rigby SIGN cycle 1

For Rigby full-SIGN (playbook §15 stage table, 9-question canonical set — refined post-F.C6 fold):

1. F.C6 policy-gate: does Rigby lean (i) update `run_ops_autopilot` docstring to acknowledge gating (accept dormancy), (ii) propose Chris green-light to enable the 10min beat (would activate Cat A/B/C/D/E/F autonomous cadence in one flip), or (iii) leave documented as-is with F.C6 tracking? Group 1400 arc-wide implication: this decision affects all six categories.
2. Any EngagementEvent writes ever, in any historical telemetry Rigby has retention for, that would falsify F.C1? Expected zero.
3. Rigby's read of the corrected axis map (§17.1): does she agree with three-independent-axes verdict OR see a fourth axis / bridge we missed?
4. R.C1 F.B1/F.C1 pair-design recommendation — does Rigby think this should ship as one bundled ADR or two sequential ADRs? Which does she lean?
5. F.C4 ContentEngagement docstring drift: does Rigby lean fix-docstring (D.C4 recommendation) OR build-the-bridge (R.C3)?
6. D.C5 "reply context builder" fork: does Rigby prefer (i) delete docstring line, (ii) build the method, or (iii) reframe as planned surface?
7. T.C4 unified `revenue_ops` queue proposal (bundle S1402 T.B8 + S1403 T.C4): does Rigby see this as immediate or post-arc?
8. T.C8 tool-surface gap (no ToolCallRecord query, no bounded ORM row-count) — does Rigby lean building these as immediate arc-support tools, or bundle with Group 1700 Observability arc?
9. Is there a Cat C-adjacent runtime debt or drift not surfaced that Rigby's telemetry side is aware of?

### 20.6 Frontmatter provenance

- Head SHA `d91d30f7` verified at session start (git log -1).
- Playbook §11.2 20-section child audit template applied.
- 15 inherited findings from parent §11.4 cited (Q1 §11.4 provenance-filter drift; §14 D6 dual-representation; etc.) — none rediscovered.
- 4 inherited findings from S1402 (F.B1/F.B2/F.B3/F.B4) cited — F.B3 extended (added `EngagementEvent.opportunity` FK to zero-writer inventory); F.B1 named as pair-design BLOCKER for R.C1 CENTRAL.
- SIGN cycle 1 fresh isolation pin to be minted per playbook §15 stage table (S1403 SIGN pin — pending §6 task).
- Verifier-loop applied (§20.3): **10 direct-read + Rigby-joint checkpoints**; 1 sub-agent overreach caught (Agent 6 T.C4) + 1 CANDIDATE upgrade to CONFIRMED (Agent 5 F.C3) + 1 new load-bearing finding surfaced mid-draft (F.C6 policy-gate dormancy). Rigby ops probe + parent-Claude direct read jointly CONFIRMED F.C6 (matching S1402 D.B7 joint-verifier-loop methodology extension).
- Memory rules triggered during audit: `feedback_audit_findings_12_canonical_celery_deferred_list.md` (F.C6 classification); `feedback_openai_client_factory.md` (Agent 2 verification path); `feedback_verify_before_deleting_dead_code.md` (Agent 6 T.C4 overreach caught).

### 20.7 Chris decisions locked at S1403 open (2)

| Decision | Verdict | Ratification path |
|---|---|---|
| D36 | Sequential launch cadence — Chris ratified default lean (matches S1301–S1305 + S1401 D30 + S1402 D34 rhythm) | Chris "agree all" 2026-07-01 |
| D37 | Retain arc pin `pa-34d43795e1b24bd3` — Chris ratified default lean (matches D31/D33/D35 retention rhythm; Group 1400 arc continuity through S1499 xx99) | Chris "agree all" 2026-07-01 |
