---
title: "S1404 Revenue — Category D: Meeting + Close (Child audit under Group 1400 Revenue arc)"
status: draft
authority: research
category: child_audit
session: 1404
date: 2026-07-01
parent_arc: 1400_revenue_domain_scoping
arc_slot: P4 (fourth child; consumes S1401 §9 + S1402 §9/§14 + S1403 §9/§14 outputs at Meeting-creation seam)
domain_slug: revenue
subdomain_slug: revenue_meeting_close
research_group: 1400
authors: Claude Code (Chris directed via short command "start research group 1404")
supersedes: none
depends_on:
  - docs/research/domains/revenue/1400_revenue_domain_scoping.md          # parent §3.D + §11.4 + §12.1 (Category D F.iii)
  - docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md   # §9 integration map (Cat A → D read seam)
  - docs/research/domains/revenue/1402_revenue_outreach_composition_delivery_audit.md   # §9 integration map + §14 D.B7 dead-code methodology
  - docs/research/domains/revenue/1403_revenue_engagement_inbound_audit.md              # §9 integration map + F.C1 ingestion-missing + F.C6 run_ops_autopilot deferred
  - docs/research/platform/cross_domain_integration_audit.md                # S1274 §2.4 line 294 HumanAttention MISSING + §5.10 tight-coupling LOW-by-design + §14 finding #36
  - docs/research/platform_architecture_inventory.md                        # S1273 §3.32 + §4.9 + §10.3 UNKNOWN #3
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md                               # process (§11.2 20-section template + §13 6-parallel-Explore sweep + §14 evidence rules + §15 full-SIGN)
  - docs/AUDIT_FINDINGS.md                                                  # §12 canonical Celery deferred-by-policy list
sign_status: sign-clean cycle 2 (High confidence, pin pa-87ee24cd0d3947ce, 2026-07-01) — pending Chris commit-gate
decisions_ratified_at_session_open: D38 sequential + D39 arc pin retain + D40 T.C8 minimal-blocking (all "agree all" 2026-07-01)
---

# Session 1404 — Category D Meeting + Close Audit

> **Scope.** This is the fourth Group 1400 Revenue child audit. It
> covers the Meeting + Close seam per parent §3.D + parent §12.1
> Category D F.iii questions. Per playbook §14 evidence rules, all
> claims cite `file:line` from `main` at `12775448` (S1403 audit +
> cascade PRs merged; S1404 branches off `main`).
>
> **What this doc is not.** An implementation plan for the missing
> pieces surfaced. F.D-scale ADRs land as post-arc design-preparation
> deliverables per playbook §17 + inherit Rigby cycle 1 Q4
> sequential-ADR pair-design discipline from S1403 R.C1.

---

## 1. Executive Summary

**Category D — Meeting + Close** covers the tail end of the Revenue
lifecycle: how (and whether) an inbound `EngagementEvent` (S1403
Category C write axis) escalates into a `Meeting` row, and how a
sequence of Meetings assembles into a `ClosePack` (proposal +
contract + invoke) for a signed deal. The seam is architecturally
present but runtime-empty at LOCAL, driven manually via PA tool
paths only, and with the S1274 §2.4 line 294 `HumanAttentionItem`
approval interlock **CONFIRMED MISSING** across all four Category D
writers. Meeting-trigger runtime liveness is dependency-blocked
behind the S1403 R.C1 F.B1 → F.C1 sequential ADR pair.

**Load-bearing findings (10 — F.D10 added SIGN cycle 1 fold):**

- **F.D1** — **Meeting-trigger runtime liveness at LOCAL = ZERO.**
  Django ORM probe: `Meeting.objects.count() = 0` +
  `ClosePack.objects.count() = 0` local. `EngagementEvent = 0`
  (inherited from S1403 F.C1). Category D is CODE-COMPLETE +
  RUNTIME-DORMANT at LOCAL — same pattern S1403 confirmed for
  Category C. PROD is UNKNOWN pending T.C8(c) prod DB RPC config
  (inherited T.C8 tool-surface gap from S1403). CONFIRMED HIGH at
  CODE + RUNTIME LOCAL tiers.

- **F.D2** — **Meeting.engagement FK never populated by the only
  writer.** `MeetingEngine.create_meeting()` at
  `core/services/ops_autopilot/engagement.py:490-526` passes
  `opportunity_id`, `title`, `scheduled_at`, `duration_minutes`,
  `channel`, `meeting_link`, `prospect_name`, `prospect_company`,
  `attendees` — but omits `engagement=` (schema present at
  `core/models_meeting.py:55-59`; `null=True, blank=True,
  on_delete=SET_NULL`). Even if the model had rows, `engagement_id`
  would be NULL 100% of the time on this path. Same F2 orphan-write
  pattern class as S1402 F.B2 + S1403 F.C3. CONFIRMED at CODE tier
  (no runtime blast radius per F.D1). **Parent §12.1 Category D Q1
  answer:** EngagementEvent → Meeting is a schema-only relationship
  in code; runtime is manual-only via PA tool `meeting_create`.

- **F.D3** — **ClosePack trigger is MANUAL (PA-tool-only), not
  autonomous.** Sole writer `CloseTheDealEngine.generate_pack()` at
  `core/services/ops_autopilot/revenue.py:931-1010` calls
  `ClosePack.objects.create(...)` at `:991`; only invoker is
  `td_handlers_ops.py:2757-2776` (PA tool action
  `close_pack_generate`). No beat task, no policy-hook auto-trigger,
  no HumanAttentionItem approval-gate on creation. **Docstring at
  `core/models_close_pack.py:6-12` claims** "When an Opportunity
  reaches high-intent (reply, meeting booked, pricing request), a
  ClosePack is generated" — aspirational, not implemented.
  **Parent §12.1 Category D Q2 answer + S1273 §10.3 UNKNOWN #3
  RESOLVED:** MANUAL PA-tool-triggered assembly. Human approval
  workflow (draft → approved → sent) IS enforced via PA tool
  `close_pack_approve`, but this is post-creation state gating, not
  pre-creation approval interlock.

- **F.D4** — **Revenue → HumanAttention interlock CONFIRMED MISSING
  at HIGH severity across Meeting AND ClosePack.** Zero Revenue-
  domain writers of `HumanAttentionItem.objects.create(...)`. Grep
  swept 26 total HAI writer files; none belong to
  `MeetingEngine`, `MeetingCoordinatorAgent`,
  `CloseTheDealEngine`, `ClosePackAutonomyEngine`, or any
  `core/models_meeting.py` / `core/models_close_pack.py` code path.
  Runtime probe: `HumanAttentionItem.objects.count() = 3061` total;
  distribution shows 2854 from `spider_pipeline`, 155 from agent
  outputs, 2 from `ops_autopilot` (both attributable to
  `_policy_revenue_pipeline` at `core.py:2051-2066` which flags
  stale-opportunity monitoring HAIs — NOT approval-gating
  interlocks). Extends S1402 (Cat B) + S1403 (Cat C) same finding
  → **Group 1400 arc-wide CONFIRMED SYSTEMIC GAP** for S1499 xx99
  synthesis. **Parent §12.1 Category D Q3 answer + S1274 §2.4 line
  294 CONFIRMED HIGH:** Revenue-domain approval-required conversion
  path is unwired at the model + service + policy + task layers.

- **F.D5** — **Meeting docstring vs runtime drift (HIGH).** Model
  docstring at `core/models_meeting.py:22` claims "Created manually
  or from EngagementEvent intent detection"; the "from
  EngagementEvent" fork is uninhabited (F.D2). Module docstring at
  `:10` claims "Lifecycle: scheduled -> briefed -> completed ->
  followed_up" but `followed_up` is NEVER written by any code path.
  Class docstring at `:24` claims "Post-meeting recaps require
  human approval before sending" but no `HumanAttentionItem` FK,
  no `approval_state` field, no schema-enforced approval gate —
  guardrail is procedural at operator judgment, not enforced (see
  F.D4 for the missing HAI interlock).

- **F.D6** — **Meeting `STATUS_CHOICES` declares 6 states; only 3
  are code-reachable (MEDIUM docstring vs runtime drift).**
  `core/models_meeting.py:27-34` enumerates: `scheduled`, `briefed`,
  `completed`, `no_show`, `cancelled`, `followed_up`. Direct read of
  all `Meeting.objects` writers + `.save()` mutations across
  `MeetingEngine` (`engagement.py:490-757`): only `scheduled`
  (default on create at `:507`), `briefed` (`.save()` at `:642`
  after `generate_brief`), and `completed` (`.save()` at `:679`
  after `add_recap`) are writable. `no_show`, `cancelled`,
  `followed_up` are declared in the enum but no writer sets them.
  Symmetric to S1402 D.B8 pattern (`OutreachDraft.CHANNEL_CHOICES`
  declares LinkedIn/Twitter/other but code selects only email).
  **Why it matters (Rigby cycle 2 NH-2 expansion):** the over-modeled
  enum is harmless while `Meeting.count = 0` at runtime (F.D1) but
  becomes a downstream-analytics contamination risk once ingestion
  lands — any dashboard filter / reporting rollup / integrity
  validator that assumes `no_show`/`cancelled`/`followed_up` rows
  exist will silently return zero and mask missing writers.
  Trim declared choices OR implement missing writers BEFORE F.B1/F.C1
  land to avoid retrofit debt.

- **F.D7** — **Parent §3.D anchor drift on ClosePack writer.**
  Parent doc §3.D names `ops_autopilot/revenue.py:1504
  ClosePackAutonomyEngine` as the ClosePack writer/assembler.
  Direct read confirms this class at `:1504-1776` is **READ-only
  monitoring** — 5 methods (`get_followup_queue`,
  `_generate_followup_text`, `get_risk_report`,
  `get_velocity_report`, `evaluate`), zero `ClosePack.objects.create`
  or `.save()` calls. The **actual writer** is
  `CloseTheDealEngine.generate_pack` at `revenue.py:851/:931/:991`
  (F.D3). Parent-doc §3.D correction recommended: retain
  `ClosePackAutonomyEngine` as the monitoring surface, add
  `CloseTheDealEngine` as the writer surface (§14 D.D3 anchor-
  update; §19 R.D5).

- **F.D8** — **Parent §3.D category miscount for
  MeetingCoordinatorAgent (CATEGORY MISCLASSIFICATION).** Parent
  §3.D lists `MeetingCoordinatorAgent` at
  `meeting_coordinator_agent.py:66` as a Category D primary
  system. Direct read of
  `core/agents/executive/meeting_coordinator_agent.py:66-` confirms
  the class is a **BaseAgent subclass for executive-agent
  facilitation** (starts synthetic multi-agent discussions between
  CTO / COO / CreativeDirector). Zero `Meeting.objects.create` /
  `.save()` calls in the class body. Not a Revenue-domain Meeting
  scheduler. Category D scope should EXCLUDE it; belongs to the
  Executive-agent-orchestration surface (adjacent to Agent System
  §agent-system.md topic).

- **F.D9** — **Structural finding: Category D contains TWO parallel
  axes that do not compose (NEW hypothesis correction to parent
  §3.D).** Parent §3.D grouped four models as "Category D lifecycle
  checkpoints" — `Meeting`, `ClosePack`, `OpportunityAction`,
  `OpportunityTask`. Direct FK graph audit confirms:
  - **Meeting/ClosePack axis** — Meeting FK to Opportunity +
    EngagementEvent; ClosePack FK to Opportunity + OutreachDraft.
    Prospect-facing writes for scheduled meetings and closing
    packs.
  - **OpportunityAction/OpportunityTask axis** — OpportunityAction
    (`core/models_unified_system.py:2552`) is a per-user action
    event log; OpportunityTask (`:3000`) is a state machine with
    1:1 FK to Opportunity (`OneToOneField` at
    `:3028`; related_name='task'). **Zero FK between these two
    models and Meeting/ClosePack.** Zero code path instantiates or
    reads both axes together in the same transaction.
  Parent §3.D correction: either (a) treat Category D as a two-axis
  category with explicit sub-groupings, or (b) reclassify
  OpportunityAction/OpportunityTask as part of Category A (they are
  Opportunity-adjacent tracking, written by
  `views_opportunity.py` + `opportunity_scoring_agent.py:1013`, not
  by any Category D writer). §14 D.D5 recommends the reclassify
  (option b). Rigby cycle 1 Q1 + Q2 leans: **immediate parent-doc
  update at S1404 commit, not xx99** (see §20.7 Q1/Q2 folds).

- **F.D10** — **ClosePack state machine PARTIAL (SIGN cycle 1
  fold — promoted from T.D5 CANDIDATE to CONFIRMED HIGH after
  joint Rigby ops-probe + parent-Claude direct-read verification).**
  `ClosePack.STATUS_CHOICES` declares 6 states (`draft`, `approved`,
  `sent`, `won`, `lost`, `expired`); code sweep across
  `core/services/ops_autopilot/revenue.py` finds writers for only
  2 transitions + 1 default:
  - `draft` — default at `ClosePack.objects.create(...)` at
    `revenue.py:991` (`CloseTheDealEngine.generate_pack`).
  - `approved` — `pack.status = 'approved'` at `revenue.py:1073`
    (`CloseTheDealEngine.approve_pack`).
  - `expired` — `.update(status='expired')` at `revenue.py:1173`
    (`ClosePackAutonomyEngine.evaluate` bulk-update on stale-cutoff
    30d).
  - **`sent` — NO writer.** All grep hits for `status='sent'` in
    `revenue.py` (`:1041`, `:1047`, `:1110`, `:1170`, `:1303`,
    `:1332`, `:1364`, `:1414`, `:1489`) are `.filter()` READS or
    aggregate keys — not `.create()` / `.update()` writes.
  - **`won` — NO writer.** All grep hits (`:1048`, `:1110`, `:1116`,
    `:1120`, `:1356`, `:1409`, `:1668`) are `.filter().aggregate()`
    or `.count()` READS, or in unrelated betting/bankroll code per
    Rigby's broader grep sweep.
  - **`lost` — NO writer.** All grep hits are in unrelated betting
    domain (`models_bankroll.py`, `models_betting.py`, etc.).
  - Symmetric to F.D6 Meeting state-machine drift: BOTH models
    declare 6-state lifecycles but implement only 3-4 states via
    code writers. This is a **paired arc-level structural drift
    finding** (Rigby cycle 1 Q4 fold recommendation) — Group 1400
    xx99 canonical summary should surface this as an arc-wide
    "over-modeled STATUS_CHOICES class" pattern.

**Ratified decisions.** D38 sequential launch cadence + D39 arc
pin `pa-34d43795e1b24bd3` retain + D40 T.C8 tool-surface gap
minimal-blocking after §13 sweep — all "agree all" from Chris via
arc pin 2026-07-01 (per S1400 D30/D32/D34/D36 discipline).

**S1273 §10.3 status after this audit:**
- **UNKNOWN #3 (close-pack conversion trigger: auto pipeline vs
  human approval via HumanAttentionItem) RESOLVED** → MANUAL PA
  tool trigger (see F.D3). Not auto pipeline. Not
  HumanAttentionItem-gated. Post-creation state approval workflow
  exists via `close_pack_approve`.

**S1274 baseline status after this audit:**
- **§2.4 line 294 "Revenue → HumanAttention MISSING" CONFIRMED
  HIGH at arc-wide level** (Categories B + C + D all confirm).
- **§5.10 tight-coupling LOW severity by design CONFIRMED** —
  Meeting `null=True` for both `opportunity` + `engagement`;
  ClosePack `null=True` for both `opportunity` + `outreach_draft`;
  runtime blast radius bounded by F.D1 zero-row state.
- **§14 finding #36 (Revenue Pipeline no runtime owner HIGH)
  CONFIRMED for Category D** (no JobContract, no dedicated queue,
  no beat schedule at Meeting/ClosePack model level). Deferred to
  S1405 Child E per parent §12.1 D28 ownership aggregation.

**Group 1400 arc integration:** S1404 confirms Category D depends
on the S1403 R.C1 F.B1 → F.C1 sequential ADR pair before Meeting-
trigger runtime liveness can flip from MANUAL to
autonomous-triggered. S1404 does NOT add new sequential ADR
dependency — it consumes the F.B1/F.C1 pair.

---

## 2. Domain Purpose

**Category D = Meeting + Close** covers the lifecycle stages
downstream of Category C engagement classification:

1. **Meeting** — schedule + brief + recap for a prospect
   conversation triggered by (in intent) inbound engagement
   escalation.
2. **ClosePack** — proposal + contract + invoice document bundle
   assembled per offer template when the meeting concludes at a
   deal-ready outcome.

Category D outputs feed Category E (Revenue Attribution) via
`OpportunityRevenue` / `OpportunityOutcome` linkage. Category D
consumes Category C outputs (Rigby-suggested meeting candidates
from `EngagementAutonomyEngine.get_meeting_suggestions` at
`engagement.py:832`) and Category A outputs (`Opportunity`
scoring/enrichment for the underlying lead).

**Business-value framing.** Category D is where surfaced +
scored + qualified leads convert into real-world booked meetings
and executed sales. Runtime-empty at LOCAL means the "close" leg
of the arc is CODE-READY but UNTESTED (no rows have ever moved
through this path in dev). PROD status UNKNOWN pending T.C8(c).

---

## 3. Canonical Entry Points

### 3.1 Files (top-level for Category D)

| File | Role | Verified |
|------|------|----------|
| `core/models_meeting.py` (lines 1-136) | `Meeting` model | ✓ |
| `core/models_close_pack.py` (lines 1-120) | `ClosePack` model | ✓ |
| `core/services/ops_autopilot/engagement.py:479-757` | `MeetingEngine` service (writer + reader + policy-evaluate) | ✓ |
| `core/services/ops_autopilot/revenue.py:851-1010` | `CloseTheDealEngine` service (writer) | ✓ |
| `core/services/ops_autopilot/revenue.py:1504-1776` | `ClosePackAutonomyEngine` service (READ-only monitoring) | ✓ |
| `core/services/ops_autopilot/core.py:2240-2268` | `_policy_meeting_engine` policy hook | ✓ |
| `core/services/ops_autopilot/core.py:~2360` | `_policy_close_pack_autonomy` policy hook | ✓ |
| `core/services/td_handlers_ops.py:2757-2954` | 12 PA tool action handlers (5 Meeting + 7 ClosePack) | ✓ |
| `core/agents/executive/meeting_coordinator_agent.py:66+` | ~~Category D primary system~~ **MISCLASSIFIED** — executive agent facilitation, not Meeting writer (F.D8) | ✓ |

### 3.2 REST URLs

Grep for `path.*meeting|path.*close_pack` in `core/urls*.py` returns
zero Category D-specific REST endpoints. All Meeting/ClosePack
surface flows through PA tool actions (below). NEW FINDING: no
REST API for direct Meeting or ClosePack CRUD.

### 3.3 PA tools

12 PA tool actions registered at `core/services/td_handlers_ops.py`:

**Meeting actions (5):**

| Action | Handler line | Method | Writer/Reader | Notes |
|--------|--------------|--------|---------------|-------|
| `meeting_create` | 2887-2906 | `MeetingEngine.create_meeting()` | WRITE | Manual create — omits `engagement=` FK |
| `meeting_inbox` | 2908-2916 | `MeetingEngine.get_inbox()` | READ | Filter types: upcoming / needs_brief / past_needs_followup |
| `meeting_brief` | 2918-2928 | `MeetingEngine.generate_brief()` | WRITE (`status → briefed`) | Template-based brief; reads EngagementEvent when `engagement_id` set (which is never per F.D2) |
| `meeting_recap` | 2930-2945 | `MeetingEngine.add_recap()` | WRITE (`status → completed`) | Sets `notes`, `outcome`, `next_steps`, `recap_draft` |
| `meeting_metrics_report` | 2947-2954 | `MeetingEngine.get_metrics_report()` | READ | Aggregate: total, by_status, by_outcome, upcoming, show_rate_pct |

**ClosePack actions (7):**

| Action | Handler | Method | Writer/Reader | Notes |
|--------|---------|--------|---------------|-------|
| `close_pack_generate` | `td_handlers_ops.py:2757-2776` | `CloseTheDealEngine.generate_pack()` | WRITE | **Sole writer** to ClosePack table |
| `close_pack_inbox` | 2778-2785 | `CloseTheDealEngine.get_inbox()` | READ | Drafts pending approval |
| `close_pack_approve` | 2787-2797 | `CloseTheDealEngine.approve_pack()` | WRITE (state transition) | Draft → approved + schedules follow-up |
| `close_pack_metrics_report` | 2801+ | `CloseTheDealEngine.get_metrics_report()` | READ | Win rate, revenue, avg deal size |
| `close_pack_followup_queue` | 3081+ | `ClosePackAutonomyEngine.get_followup_queue()` | READ | Due/overdue packs |
| `close_pack_risk_report` | 3088+ | `ClosePackAutonomyEngine.get_risk_report()` | READ | Pricing/timeline/attribution risk flags |
| `close_pack_velocity` | 3095+ | `ClosePackAutonomyEngine.get_velocity_report()` | READ | Time-to-close metrics |

### 3.4 Celery tasks

Zero Category D-dedicated Celery tasks. The `MeetingEngine.evaluate`
+ `ClosePackAutonomyEngine.evaluate` policy-evaluate methods are
invoked only via `_policy_meeting_engine` (`core.py:2240-2268`) +
`_policy_close_pack_autonomy` (`core.py:~2360`) inside the
`run_ops_autopilot` beat wrapper at `core/tasks.py:13090-13106`.
Runtime status: **DEFERRED-BY-POLICY** per AUDIT_FINDINGS.md #12
gating (see F.D1 inheritance from S1403 F.C6).

### 3.5 Management commands

Grep of `core/management/commands/` returns zero Category D
management commands. No `audit_meetings`, `audit_close_packs`,
`bootstrap_close_pack_offers`, etc. Consistent with the "no
autonomous cadence" surface.

---

## 4. Major Models

### 4.1 `Meeting` (`core/models_meeting.py:18-136`, table `core_meeting`)

**Field inventory (23 fields):**

| Field | Type | Default | Nullable | Notes |
|-------|------|---------|----------|-------|
| `id` | UUIDField (PK) | `uuid.uuid4()` | No | Non-editable |
| `opportunity` | FK(`core.Opportunity`) | — | Yes | `on_delete=SET_NULL`, `related_name='meetings'` |
| `engagement` | FK(`core.EngagementEvent`) | — | Yes | `on_delete=SET_NULL`, `related_name='meetings'` — schema-only per F.D2 |
| `title` | CharField(300) | blank | Yes | — |
| `scheduled_at` | DateTimeField | — | No | **Indexed** |
| `duration_minutes` | IntegerField | 30 | No | — |
| `channel` | CharField(20) | `'zoom'` | No | Choices: zoom/meet/teams/phone/in_person/other |
| `meeting_link` | URLField(500) | blank | Yes | — |
| `attendees` | JSONField | [] | Yes | List of {name, email, role} dicts |
| `prospect_name` | CharField(200) | blank | Yes | Denormalized |
| `prospect_company` | CharField(200) | blank | Yes | Denormalized |
| `prospect_role` | CharField(200) | blank | Yes | Denormalized — never written by any writer (F.D5 partial) |
| `brief_text` | TextField | blank | Yes | Populated via `generate_brief()` |
| `brief_generated_at` | DateTimeField | null | Yes | Set by `generate_brief()` |
| `notes` | TextField | blank | Yes | Set by `add_recap()` |
| `recap_draft` | TextField | blank | Yes | Set by `add_recap()` |
| `next_steps` | TextField | blank | Yes | Set by `add_recap()` |
| `outcome` | CharField(50) | blank | Yes | Set by `add_recap()`; values: interested/needs_followup/not_a_fit/deal_agreed |
| `status` | CharField(20) | `'scheduled'` | No | **Indexed** — 6 STATUS_CHOICES; 3 reachable per F.D6 |
| `trace_id` | CharField(100) | blank | Yes | **Indexed** — never written by any writer |
| `user` | FK(AUTH_USER_MODEL) | — | Yes | `on_delete=SET_NULL` — never written by any writer (ownership implicit in PA-tool caller) |
| `created_at` | DateTimeField | `auto_now_add=True` | No | **Indexed** |
| `updated_at` | DateTimeField | `auto_now=True` | No | — |

**Compound indexes** (`Meta` at `:121-128`): `(status, scheduled_at)`
+ `(-scheduled_at)`.

**Docstring claims (module + class):**
- Module `:10`: "Lifecycle: scheduled -> briefed -> completed -> followed_up"
- Class `:22-25`: "A scheduled meeting tied to an Opportunity.
  Created manually or from EngagementEvent intent detection.
  Pre-call briefs generated automatically before the meeting.
  Post-meeting recaps require human approval before sending."

**Docstring drift accounting (F.D5 + F.D6):**
- "Created manually or from EngagementEvent intent detection" —
  the EngagementEvent fork is uninhabited (F.D2 empirical).
- "Pre-call briefs generated automatically" — briefs are
  operator-triggered via PA tool `meeting_brief`, not scheduled
  autonomously (no beat task; policy-hook `_policy_meeting_engine`
  is READ-only monitoring, doesn't `generate_brief` writes).
- "Post-meeting recaps require human approval before sending" —
  no schema enforcement, no `HumanAttentionItem` FK, no
  `approval_state` field.

### 4.2 `ClosePack` (`core/models_close_pack.py:20-120`, table `core_close_pack`)

**Field inventory (verified via Agent 2 + parent-Claude direct
read):**

| Field | Type | Default | Nullable | Notes |
|-------|------|---------|----------|-------|
| `id` | UUIDField (PK) | `uuid.uuid4()` | No | — |
| `opportunity` | FK(`core.Opportunity`) | — | Yes | `on_delete=SET_NULL`, `related_name='close_packs'` |
| `offer_key` | CharField(50) | — | No | Choices: ai_automation / content_engine / analytics_dashboard / consulting |
| `price` | DecimalField(12,2) | 0 | No | — |
| `timeline_days` | IntegerField | 14 | No | — |
| `proposal_text` | TextField | '' | Yes | Template-generated at create |
| `contract_text` | TextField | '' | Yes | Template-generated at create |
| `invoice_text` | TextField | '' | Yes | Template-generated at create |
| `edited_proposal` | TextField | '' | Yes | Operator edits |
| `edited_contract` | TextField | '' | Yes | Operator edits |
| `edited_invoice` | TextField | '' | Yes | Operator edits |
| `status` | CharField(20) | `'draft'` | No | **Indexed** — 6 states (draft/approved/sent/won/lost/expired) |
| `outreach_draft` | FK(`core.OutreachDraft`) | — | Yes | `on_delete=SET_NULL`, `related_name='close_packs'` — never written by `CloseTheDealEngine.generate_pack` |
| `trace_id` | CharField(100) | '' | Yes | **Indexed** |
| `followup_at` | DateTimeField | — | Yes | Set by `approve_pack` |
| `followup_count` | IntegerField | 0 | No | — |
| `user` | FK(AUTH_USER_MODEL) | — | Yes | `on_delete=SET_NULL` — never written by `generate_pack` |
| `created_at` | DateTimeField | `auto_now_add=True` | No | Indexed |
| `updated_at` | DateTimeField | `auto_now=True` | No | — |

**Compound indexes:** `(status, -created_at)` + `(offer_key,
status)`.

**Docstring claims (`:6-12` + `:22-25`):**
- `:6-12`: "When an Opportunity reaches high-intent (reply,
  meeting booked, pricing request), a ClosePack is generated with
  proposal + contract + invoice text. All documents require human
  approval before sending."
- `:22-25`: "Lifecycle: draft → approved → sent → won/lost/expired"

**Docstring drift accounting (F.D3):**
- Aspirational "generated when high-intent" — no code path
  auto-triggers `generate_pack`. Sole writer path is
  manual PA tool `close_pack_generate`.
- Post-create human-approval workflow IS enforced via PA tool
  `close_pack_approve` (state transition), but is NOT gated by
  `HumanAttentionItem` (F.D4). Guardrail is procedural at
  operator judgment, not schema-enforced.

### 4.3 `OpportunityAction` (`core/models_unified_system.py:2552`) — **RECLASSIFIED per F.D9**

| Field | Notes |
|-------|-------|
| `id` (UUID PK), `opportunity` FK CASCADE, `user` FK CASCADE | Standard |
| `action_type` (enum: viewed/analyzed/approved/rejected/started/content_created/published/revenue_logged) | Event log kind |
| `content_ids` (JSONField default=[]) | — |
| `workflow_used` (CharField blank), `outcome` (JSONField default={}) | — |
| `notes` (TextField), `created_at` | — |

**Writers (5 sites):**
- `core/views_opportunity.py:417` — `action_type='started'`
- `core/views_opportunity.py:486` — `action_type='dismissed'`
- `core/views_opportunity.py:836` — `action_type='revenue_logged'`
- `core/views_opportunity.py:1149` — `action_type='content_created'`
- `core/services/opportunity_execution_pipeline.py:359` —
  `action_type='started'` (auto-executed pipeline path)

**No FK to Meeting or ClosePack.** No code path writes
OpportunityAction from any Category D writer. Per F.D9, recommend
reclassify to Category A (Opportunity lifecycle tracking).

### 4.4 `OpportunityTask` (`core/models_unified_system.py:3000`) — **RECLASSIFIED per F.D9**

25 fields including `OneToOneField(Opportunity, related_name='task')`
at `:3028`, plus `workspace`, `title`, `description`, `status` (9
states), `priority` (4 levels), `assigned_agents` (M2M), timestamps.

**Writers:**
- `core/agents/analysis/opportunity_scoring_agent.py:1013` — auto-
  created when scoring agent computes score ≥ 70 (threshold-gated)
- `core/services/td_handlers_agents.py:669` — PA-tool triggered

**No FK to Meeting or ClosePack.** Per F.D9, reclassify to Category A.

### 4.5 Runtime row counts (parent-Claude Django ORM probe 2026-07-01, LOCAL env)

```
Meeting.objects.count() = 0
ClosePack.objects.count() = 0
EngagementEvent.objects.count() = 0
OutreachDraft.objects.count() = 40
HumanAttentionItem.objects.count() = 3061
Meeting.engagement usage: N/A (zero Meeting rows)
HumanAttentionItem.source_type distribution:
  spider_pipeline: 2854 (93.2%)
  agent_output:*: 155 total (5.1%)
  llm_cost_monitor: 20
  mythology:pattern_detected: 16
  system_intelligence: 13
  ops_autopilot: 2 (0.07%)
  pa: 1
```

PROD counts UNKNOWN pending T.C8(c) prod DB RPC configuration
(inherited from S1403 T.C8).

**PROD-facing runtime-liveness stub (Rigby cycle 2 NH-3 addition):**
When T.C8(c) `PA_DB_HEALTH_RPC_URL` + `PA_DB_HEALTH_RPC_CLIENT_TOKEN`
land (Rigby cycle 1 Q8 lean: land NOW pre-S1405), rerun the same
count probe against PROD via Rigby's `db_health_tool env=prod
action=tables prefix=core_` for `core_meeting`, `core_close_pack`,
`core_engagement_event`, `core_outreach_draft`,
`core_humanattentionitem`. If PROD counts also = 0 for
Meeting/ClosePack, F.D1 elevates from "LOCAL DORMANT / PROD unknown"
to "arc-wide RUNTIME DORMANT" — feeds S1499 xx99 canonical summary
directly. If PROD counts > 0, revisit F.D2 + F.D5 + F.D10 with
`.filter(engagement_id__isnull=True).count()`,
`.exclude(status__in=['scheduled','briefed','completed']).count()`,
and `ClosePack.filter(status__in=['sent','won','lost']).count()`
respectively to verify runtime drift matches code-level assertions.

---

## 5. Major Services

### 5.1 `MeetingEngine` (`core/services/ops_autopilot/engagement.py:479-757`)

**Docstring (`:481-488`):**
> "Tracks meetings from scheduling through follow-up. Generates
> pre-call briefs with prospect context. Guardrails: No auto-
> sending (recap drafts need approval); Manual-first v1 (no
> calendar integration); Brief auto-generated before meeting."

**6 methods:**

| Method | Line range | R/W | Reads EngagementEvent? | Notes |
|--------|-----------|-----|------------------------|-------|
| `create_meeting()` | 490-526 | WRITE | No | Sole `Meeting.objects.create` at `:507`; omits `engagement=` (F.D2) |
| `get_inbox()` | 528-580 | READ | No | Filter types: upcoming / needs_brief / past_needs_followup |
| `generate_brief()` | 582-648 | WRITE (status→briefed) | Yes (`:606`) — reads `EngagementEvent.objects.get(id=meeting.engagement_id)` when set, which is never (F.D2) | 500+ char brief template |
| `add_recap()` | 650-686 | WRITE (status→completed) | No | Draft-only; no send |
| `get_metrics_report()` | 688-722 | READ | No | Aggregate metrics |
| `evaluate()` | 724-757 | READ | No | Policy-hook read: counts upcoming, needs_brief, past_no_followup |

**No `BaseAutonomyEngine` / parent class** — plain service class.
Matches EngagementEngine + EngagementAutonomyEngine sibling shape
(S1403 §5.1 + §5.2). Placement between them at `:479-757` matches
parent §3.D + S1403 Agent 5 confirmation.

### 5.2 `CloseTheDealEngine` (`core/services/ops_autopilot/revenue.py:851-1010`)

**Sole writer to ClosePack table.** Key methods:

| Method | Line range | R/W | Notes |
|--------|-----------|-----|-------|
| `generate_pack()` | 931-1010 | WRITE | Sole `ClosePack.objects.create` at `:991`; omits `user=`, `outreach_draft=` (F.D3 + F.D6 sibling-orphan pattern) |
| `approve_pack()` | (near :931) | WRITE (state) | Draft → approved transition + schedules follow-up |
| `get_inbox()` | | READ | Drafts pending approval |
| `get_metrics_report()` | | READ | Win rate, revenue, avg deal size |

**Template inventory (`:872-929`):** four hardcoded offer templates
— `ai_automation`, `content_engine`, `analytics_dashboard`,
`consulting`. Template drift risk (S1402 B.B3-adjacent):
per-offer envelope hardcoded in class literal; changing offers
requires redeploy. Post-arc design-preparation candidate.

### 5.3 `ClosePackAutonomyEngine` (`core/services/ops_autopilot/revenue.py:1504-1776`)

**READ-only monitoring service.** Not a writer despite name.
Methods:

| Method | Line | R/W | Notes |
|--------|------|-----|-------|
| `get_followup_queue(now)` | 1526 | READ | Due/overdue packs |
| `_generate_followup_text(...)` | 1578 | Helper | No I/O |
| `get_risk_report()` | 1594 | READ | Pricing/timeline/attribution guardrails |
| `get_velocity_report()` | 1659 | READ | Time-to-close aggregates |
| `evaluate(now)` | 1730 | READ | Policy-hook entry: counts overdue/high-risk/stale |

Registered in `_POLICY_REGISTRY` at `core/services/ops_autopilot/core.py:282` as
`('close_pack_autonomy', 'close_pack_autonomy', '_policy_close_pack_autonomy')`.
Fired via `run_ops_autopilot` beat wrapper (deferred).

### 5.4 `_policy_meeting_engine` (`core/services/ops_autopilot/core.py:2240-2268`)

Policy-hook function; registered in `_POLICY_REGISTRY` at
`core.py:~278` as `('meetings', 'meeting_engine',
'_policy_meeting_engine')`. Body invokes
`MeetingEngine().evaluate(now)` at `:2254` and returns
`{upcoming, needs_brief, past_no_followup}`. Fires only via
`run_ops_autopilot` beat wrapper (DEFERRED per AUDIT_FINDINGS.md
#12 gating — inherited from S1403 F.C6).

### 5.5 `MeetingCoordinatorAgent` (`core/agents/executive/meeting_coordinator_agent.py:66+`) — **NOT a Category D writer (F.D8)**

BaseAgent subclass for executive-agent multi-agent facilitation
(CTO/COO/CreativeDirector synthesis). Zero `Meeting.objects.create`
in the class body. AGENT_MAP entry at `core/agent_router.py:354`
(enabled). No `JobContract` entry (grep 0 hits). No `meeting_*` PA
tool actions bind to it. Removed from `run_executive_leadership_agents()`
rotation per Session 1099 (60min+ hung executions caused
circuit-breaker trips).

**Consequence for Category D:** parent §3.D listing is a category
misclassification. This agent belongs to the Agent-System topic
(agent-to-agent orchestration), not to Revenue-domain Meeting
scheduling.

---

## 6. Major APIs and Interfaces

### 6.1 REST endpoints

Zero Category D-specific REST endpoints (grep of `core/urls*.py`
for `meeting|close_pack` = 0). All Category D surface flows
through PA tool actions.

### 6.2 WebSocket consumers

Zero Category D-specific WS consumers (grep of `core/consumers*.py`
for `meeting|close_pack` = 0). No real-time push for meeting inbox
or close pack pipeline.

### 6.3 PA tool surface

12 PA tool actions (5 Meeting + 7 ClosePack) — enumerated in §3.3
above. All are either READ (7 actions) or WRITE via explicit
operator PA-tool invocation (5 actions). Zero autonomous cadence
writes.

### 6.4 Event bus streams

`core/services/event_bus.py:21-31` `EventStream` enum defines 8
streams (`SPIDER_DATA`, `OPPORTUNITY_CREATED`, `OPPORTUNITY_SCORED`,
`VALIDATION_REQUIRED`, `VALIDATION_DECIDED`, `OUTCOME_RECORDED`,
`MODEL_TRAINED`, `SYSTEM_ALERT`). **Zero `MEETING_*` or
`CLOSE_PACK_*` streams.** Symmetric to S1402/S1403 findings for
Outreach + Engagement. Post-arc bundle candidate with
`OUTREACH_*` + `ENGAGEMENT_*` stream additions (S1402 Q20 + S1403
Q20).

---

## 7. Runtime Flows

### 7.1 Flow α — Meeting create → brief → recap (MANUAL PA-tool path)

```
PA tool `meeting_create` (td_handlers_ops.py:2887)
  ↓
MeetingEngine.create_meeting(opportunity_id, scheduled_at, ...) (engagement.py:490-526)
  ↓
Meeting.objects.create(opportunity_id=..., title=..., scheduled_at=..., ...) (engagement.py:507)
  → status='scheduled' (default), engagement=NULL always (F.D2), user=NULL always, trace_id='' always
  ↓
(operator triggers)
  ↓
PA tool `meeting_brief` (td_handlers_ops.py:2918)
  ↓
MeetingEngine.generate_brief(meeting_id) (engagement.py:582-648)
  ↓
Meeting.objects.get(id=meeting_id) (engagement.py:587)
  ↓
[optional] EngagementEvent.objects.get(id=meeting.engagement_id) (engagement.py:606) — NEVER FIRES (F.D2)
  ↓
meeting.brief_text = <500+ char template>, meeting.brief_generated_at = now, meeting.status = 'briefed' (:639-641)
  ↓
meeting.save() (:642)
  ↓
(after meeting occurs, operator triggers)
  ↓
PA tool `meeting_recap` (td_handlers_ops.py:2930)
  ↓
MeetingEngine.add_recap(meeting_id, notes, outcome, next_steps) (engagement.py:650-686)
  ↓
meeting.notes = notes, meeting.outcome = outcome, meeting.next_steps = next_steps, meeting.recap_draft = <template>, meeting.status = 'completed' (:677-679)
  ↓
meeting.save()
```

**Runtime status:** ZERO invocations at LOCAL (Meeting.count = 0).
Code-complete + runtime-dormant per F.D1.

### 7.2 Flow β — ClosePack generate → approve → close (MANUAL PA-tool path)

```
PA tool `close_pack_generate` (td_handlers_ops.py:2757-2776)
  ↓
CloseTheDealEngine.generate_pack(opportunity_id, offer_key, price, timeline_days) (revenue.py:931-1010)
  ↓
proposal_text = <template :872-929>, contract_text = <template>, invoice_text = <template>
  ↓
ClosePack.objects.create(opportunity_id=..., offer_key=..., price=..., timeline_days=..., proposal_text=..., contract_text=..., invoice_text=...) (revenue.py:991)
  → status='draft' (default), user=NULL, outreach_draft=NULL, trace_id='' always
  ↓
(operator reviews via PA tool `close_pack_inbox`)
  ↓
PA tool `close_pack_approve` (td_handlers_ops.py:2787-2797)
  ↓
CloseTheDealEngine.approve_pack(pack_id, edited_texts?)
  ↓
pack.status = 'approved', pack.edited_proposal/contract/invoice = <operator edits>, pack.followup_at = now + follow-up-days
  ↓
pack.save()
```

**Runtime status:** ZERO invocations at LOCAL (ClosePack.count = 0).

### 7.3 Flow γ — Policy monitoring loop (DEFERRED)

```
run_ops_autopilot() beat wrapper (core/tasks.py:13090-13106)
  ↓ [DEFERRED per AUDIT_FINDINGS.md #12; not in PeriodicTask registry (0 of 92 enabled)]
OpsAutopilot().run() (core.py:292-350)
  ↓
for each policy in _POLICY_REGISTRY (:308) → invoke policy method
  ↓
_policy_meeting_engine(now) (core.py:2240-2268)
  ↓
MeetingEngine().evaluate(now) (engagement.py:724-757)
  ↓
{upcoming: N, needs_brief: N, past_no_followup: N} — READ-only counts
  ↓
_policy_close_pack_autonomy(now) (core.py:~2360)
  ↓
ClosePackAutonomyEngine().evaluate(now) (revenue.py:1730-1776)
  ↓
{overdue: N, high_risk: N, stale: N} — READ-only counts
```

**Runtime status:** DEFERRED-BY-POLICY. Live invocation is only via
ad-hoc PA-tool paths at `td_handlers_ops.py:1643,1674` — no
autonomous 10-min cadence.

### 7.4 Flow δ — What DOESN'T exist: EngagementEvent → Meeting auto-trigger

```
[intended flow — DOES NOT EXIST]
inbound engagement webhook receiver (does not exist — F.C1 pending)
  ↓
EngagementEvent.objects.create(...) (does not exist)
  ↓
EngagementAutonomyEngine detects high-intent reply
  ↓
[missing] auto-trigger MeetingEngine.create_meeting(engagement_id=..., ...)
  ↓
Meeting created with engagement=FK populated
```

Parent §12.1 Category D Q1 answered here: the "auto trigger from
EngagementEvent" flow requires (i) S1402 F.B1 delivery ADR to
enable send + provider_message_id correlation, (ii) S1403 R.C1
F.C1 ingestion ADR to enable EngagementEvent writes, (iii) a new
Category D writer that reads high-intent EngagementEvent rows and
auto-creates Meeting with `engagement=` FK populated. All three
are missing. **Sequential dependency: F.B1 → F.C1 → F.D-Meeting-
Auto-Trigger.**

### 7.5 Flow ε — Suggested-not-created path (READ-only surface exists today)

```
EngagementAutonomyEngine.get_meeting_suggestions(user_id, limit=5) (engagement.py:832-876)
  ↓
EngagementEvent.objects.filter(user=user, intent='positive|meeting_request', ...).order_by('-created_at')[:limit] — reads high-intent rows
  ↓
for each candidate: Meeting.objects.filter(opportunity_id=..., status__in=['scheduled','briefed']).exists() — dedupe check
  ↓
returns list of suggestion dicts (READ-only — no Meeting.create)
```

Consumed via PA tool for operator to decide whether to call
`meeting_create`. **Runtime status:** EngagementEvent = 0 rows
(S1403 F.C1) → suggestion query returns empty list on every
invocation.

---

## 8. Data Ownership and Lifecycle

**Meeting states declared vs reachable (F.D6):**

| Declared state (`STATUS_CHOICES`) | Reachable in code? | Set by |
|-----------------------------------|--------------------|--------|
| `scheduled` | ✓ (default at `Meeting.objects.create`) | `MeetingEngine.create_meeting()` at `:507` |
| `briefed` | ✓ | `MeetingEngine.generate_brief()` at `:641` |
| `completed` | ✓ | `MeetingEngine.add_recap()` at `:677` |
| `no_show` | ✗ | No code writer |
| `cancelled` | ✗ | No code writer |
| `followed_up` | ✗ | No code writer |

**ClosePack states declared vs reachable (CONFIRMED via SIGN cycle 1 joint Rigby + parent-Claude verifier-loop — see F.D10):**

| Declared state | Reachable? | Set by |
|----------------|-----------|--------|
| `draft` | ✓ (default at `create`) | `CloseTheDealEngine.generate_pack()` at `:991` |
| `approved` | ✓ | `CloseTheDealEngine.approve_pack()` at `revenue.py:1073` |
| `sent` | ✗ (CONFIRMED unreachable per F.D10) | No writer — all grep hits are `.filter()` READ or aggregate keys |
| `won` | ✗ (CONFIRMED unreachable per F.D10) | No writer — all grep hits are `.filter().aggregate()` READS or unrelated betting/bankroll code |
| `lost` | ✗ (CONFIRMED unreachable per F.D10) | No writer — all grep hits are in unrelated betting domain |
| `expired` | ✓ | `ClosePackAutonomyEngine.evaluate()` bulk `.update(status='expired')` at `revenue.py:1173` |

**ClosePack state-machine writer inventory (SIGN cycle 1 addition):**

Paired with F.D6 Meeting state-machine drift, both models exhibit
the same "over-modeled STATUS_CHOICES class" pattern with symmetric
3-state unreachable gaps. Meeting: 3 of 6 declared states
unreachable (`no_show`, `cancelled`, `followed_up`); ClosePack: 3
of 6 declared states unreachable (`sent`, `won`, `lost`). Group
1400 xx99 canonical summary should surface this as arc-wide
structural finding per Rigby cycle 1 Q4 fold lean.

**S1273 §10.3 UNKNOWN #3 status:** RESOLVED to MANUAL. See §1
F.D3.

**S1274 §5.10 tight-coupling classification:** CONFIRMED LOW risk
by design at Meeting-engagement + ClosePack-outreach_draft null-FK
level. Runtime blast radius bounded by F.D1 zero-row state.
Integrity audit design at §14 D.D8 + §19 R.D8 preserves the
by-design nullability while adding observability.

---

## 9. Integrations With Other Domains

Integration map verified against S1274 baseline + S1401 §9.1 +
S1402 §9 + S1403 §9. Verifier-loop applied to sub-agent findings.

| Adjacent domain | S1274 baseline | S1404 Category D verified | Verdict | Evidence |
|---|---|---|---|---|
| Category C EngagementEvent → Category D Meeting (write direction) | UNKNOWN | **CONFIRMED SCHEMA-ONLY** — FK exists at `models_meeting.py:55-59`; zero writers populate it (F.D2) | CONFIRMED | Direct grep `Meeting.objects.create` returns single hit at `engagement.py:507` which omits `engagement=`. |
| Category C → Category D read direction (Rigby suggestions) | UNKNOWN | **READ-only via `get_meeting_suggestions`** (S1403 §9 row 4 verified from Category D perspective) | READ-only CONFIRMED | `engagement.py:832-876` reads `EngagementEvent` + Meeting existence check; returns suggestions to PA. |
| Category B OutreachDraft → Category D ClosePack (write direction) | Not in S1274 | **SCHEMA-ONLY** — `ClosePack.outreach_draft` FK exists at `models_close_pack.py:83-88`; `CloseTheDealEngine.generate_pack` at `revenue.py:991` omits `outreach_draft=` | CONFIRMED | Direct read + grep. |
| Category A Opportunity → Category D Meeting (read direction) | STRONG per S1273 | STRONG CONFIRMED | CONFIRMED | `Meeting.opportunity` FK at `:48-52`; writer at `:507` populates `opportunity_id=`. |
| Category A Opportunity → Category D ClosePack (read direction) | STRONG per S1273 | STRONG CONFIRMED | CONFIRMED | `ClosePack.opportunity` FK at `:39-43`; writer at `:991` populates `opportunity_id=`. |
| Category D Meeting → Category E Revenue Attribution | STRONG per S1273 | UNKNOWN (Category E owns primary evidence) | PARKED | S1405 resolves via `OpportunityRevenue` / `OpportunityOutcome` write registry. |
| Category D ClosePack → Category E Revenue Attribution | STRONG per S1273 | UNKNOWN (Category E owns) | PARKED | S1405 resolves via `RevenueAttributionBridge` read/write sites. |
| Category D → HumanAttention (approval-required conversion) | **MISSING (S1274 §2.4 line 294)** | **CONFIRMED MISSING HIGH** — zero Meeting/ClosePack writers create `HumanAttentionItem` | CONFIRMED | Grep of 26 total HAI writer files; zero from `models_meeting.py`, `models_close_pack.py`, `MeetingEngine`, `MeetingCoordinatorAgent`, `CloseTheDealEngine`, `ClosePackAutonomyEngine` paths. |
| Category D → EventBus | UNKNOWN | **NO STREAMS** | CONFIRMED (negative) | `event_bus.py:21-31` `EventStream` has no `MEETING_*` or `CLOSE_PACK_*` values. |
| Category D → Governance (§3.23 kill-switch) | Not in S1274 | **NOT WIRED** | CONFIRMED (negative) | Direct read of `MeetingEngine` + `CloseTheDealEngine` + `ClosePackAutonomyEngine` — no reads of `GovernanceState` or freeze mode. |
| Category D → Ops Autopilot policy engine | Not in S1274 | STRONG (2 policy hooks LIVE in registry) | CONFIRMED | `core.py:278` `_policy_meeting_engine` + `:282` `_policy_close_pack_autonomy`; both deferred at runtime per F.C6 inheritance. |
| Category D → PA (Rigby function-call surface) | Not in S1274 | STRONG (12 tool actions: 5 Meeting + 7 ClosePack) | CONFIRMED | `td_handlers_ops.py:2757-2954` — enumerated in §3.3. |
| Category D → Observability (`ImpactEvent`) | STRONG per S1274 | UNKNOWN (Category E owns) | PARKED | Deferred to S1405. |
| Category D → Initiative | MISSING per S1274 §2.4 line 291 | UNKNOWN — Category D code has no Initiative imports or FK | Deferred | S1405 aggregates arc-wide per D28. |
| MeetingCoordinatorAgent → Category D | (parent §3.D implied WRITE) | **NOT A WRITER (F.D8)** | REFUTED | Direct read `core/agents/executive/meeting_coordinator_agent.py:66-` — zero `Meeting.objects.create` calls. |
| OpportunityAction/OpportunityTask ↔ Meeting/ClosePack | (parent §3.D implied as sibling lifecycle checkpoints) | **PARALLEL AXES; NO FK IN EITHER DIRECTION** (F.D9) | REFUTED | Direct FK graph audit — Meeting/ClosePack have no OpportunityAction FK; OpportunityAction/OpportunityTask have no Meeting/ClosePack FK. |

**Producer inventory (writers of Category D models):**

| Model | Writer count | Writer sites |
|---|---|---|
| `Meeting` | 1 | `engagement.py:507` (`MeetingEngine.create_meeting`) — omits `engagement=`, `user=`, `trace_id=`, `prospect_role=` |
| `Meeting.status` mutations | 2 | `engagement.py:641` (→briefed), `:677` (→completed) — no writer for no_show/cancelled/followed_up |
| `ClosePack` | 1 | `revenue.py:991` (`CloseTheDealEngine.generate_pack`) — omits `user=`, `outreach_draft=`, `trace_id=` |
| `ClosePack.status` mutations | ≥1 | `CloseTheDealEngine.approve_pack` (draft→approved); sent/won/lost/expired writers not surfaced in sweep |
| `OpportunityAction` (Cat A per F.D9) | 5 | See §4.3 |
| `OpportunityTask` (Cat A per F.D9) | 2 | See §4.4 |

**Consumer inventory (readers of Category D models):**

- **Meeting reads:** `MeetingEngine.get_inbox` + `.generate_brief`
  + `.add_recap` + `.get_metrics_report` + `.evaluate` +
  `EngagementAutonomyEngine.get_meeting_suggestions` (existence
  check only) + Category E aggregation surfaces (S1405 scope).
- **ClosePack reads:** `CloseTheDealEngine.get_inbox` +
  `.get_metrics_report` + `ClosePackAutonomyEngine.get_followup_queue`
  + `.get_risk_report` + `.get_velocity_report` +
  `.evaluate` + `EngagementEngine` (funnel metrics at
  `engagement.py:929-931` reads `ClosePack.objects.filter(opportunity_id__in=eng_opp_ids)`
  for deal-count) + `IntelligenceEngine.event_summary` at
  `intelligence.py:2599` (`ClosePack.objects.filter(created_at__gte=cutoff)`
  for creation-event count).

---

## 10. Event Flows

**Q19 — What events does Category D emit?**

**None.** `EventStream` enum has zero `MEETING_*` or
`CLOSE_PACK_*` values. Symmetric to S1402 Cat B + S1403 Cat C
findings for Outreach/Engagement.

**Q20 — What events should Category D emit?**

Given the missing seams surfaced above, natural emission points
are:

- `MEETING_SCHEDULED` — emit from `MeetingEngine.create_meeting`
  after `Meeting.objects.create()`. Consumers: Category E revenue
  forecasting; observability dashboard.
- `MEETING_BRIEFED` — emit from `MeetingEngine.generate_brief`
  after `meeting.status = 'briefed'` transition. Useful for
  brief-quality feedback loop.
- `MEETING_COMPLETED` — emit from `MeetingEngine.add_recap` after
  `status = 'completed'` transition. Feeds Category E revenue
  attribution (deal_agreed → ClosePack trigger).
- `CLOSE_PACK_GENERATED` — emit from
  `CloseTheDealEngine.generate_pack` after `ClosePack.objects.create`.
- `CLOSE_PACK_APPROVED` — emit from
  `CloseTheDealEngine.approve_pack` after `status = 'approved'`
  transition. Feeds outbound delivery subsystem (which is F.B1
  pending).
- `CLOSE_PACK_WON` / `CLOSE_PACK_LOST` — emit from a to-be-built
  writer (currently no `sent` / `won` / `lost` writers observed
  in code sweep).

Post-arc design-preparation candidate: bundle
`MEETING_*` + `CLOSE_PACK_*` stream additions with S1402 Cat B
`OUTREACH_*` + S1403 Cat C `ENGAGEMENT_*` proposals as a single
EventBus schema PR at S1499 xx99 or dedicated ADR.

---

## 11. Existing Documentation

**Category D has no CANONICAL topic doc.** No
`docs/topics/meeting-close.md` or
`docs/topics/close-pack-lifecycle.md` — matches parent §11.3
baseline that no Revenue CANONICAL topic doc exists.

**Existing partial coverage:**

| Doc | Category D coverage | Completeness | Cite-forward |
|---|---|---|---|
| `docs/research/platform_architecture_inventory.md` §3.32 + §4.9 | Named in cross-domain flow row; MeetingCoordinatorAgent → Meeting → ClosePack step | LIGHT + F.D7 anchor drift (wrong engine named as writer) | S1273 v2 |
| `docs/research/platform_architecture_inventory.md` §10.3 UNKNOWN #3 | Close-pack conversion trigger auto vs manual | UNKNOWN → RESOLVED via F.D3 | S1273 v2 |
| `docs/research/platform/cross_domain_integration_audit.md` §2.4 line 294 | "Revenue → HumanAttention MISSING" | Targeted; CONFIRMED HIGH at Cat D via F.D4 | S1274 |
| `docs/research/platform/cross_domain_integration_audit.md` §5.10 | Tight-coupling LOW-by-design (Meeting-engagement + ClosePack-outreach_draft null-FK) | Confirmed CONFIRMED LOW risk BY DESIGN | S1274 |
| `docs/research/platform/cross_domain_integration_audit.md` §14 finding #36 | Revenue Pipeline no runtime owner HIGH | CONFIRMED for Cat D | S1274 |
| `docs/AUDIT_FINDINGS.md` #12 | `run_ops_autopilot` deferred-by-policy | Inherited to Cat D policy hooks (`_policy_meeting_engine` + `_policy_close_pack_autonomy`) | S1245 |
| S1403 audit §9 | Cat C → Cat D READ-only surface (Rigby suggestions) | Confirmed from Cat D perspective at §9 row 2 | 1403_revenue_engagement_inbound_audit.md |
| S1402 audit §14 D.B7 | Dead-code pattern verification methodology | Applied inversely at F.D8 (MeetingCoordinatorAgent has invokers via PA dispatch, so not dead code — memory rule `feedback_verify_before_deleting_dead_code.md` applied) | 1402_revenue_outreach_composition_delivery_audit.md |

---

## 12. Research Coverage

**Documented across the corpus:**
- S1273 §3.32 flow row (LIGHT, F.D7 anchor drift)
- S1273 §10.3 UNKNOWN #3 (RESOLVED via F.D3)
- S1274 §2.4 line 294 (CONFIRMED HIGH via F.D4)
- S1274 §5.10 (CONFIRMED LOW-by-design)
- S1274 §14 finding #36 (CONFIRMED for Cat D, deferred to Cat E synthesis)
- Parent §3.D + §12.1 Category D F.iii (all 4 questions answered + inherited Q from S1403)
- S1401 §9 (Cat A → Cat D read direction verified from Cat D perspective)
- S1402 §14 D.B7 (dead-code methodology applied inversely at F.D8)
- S1403 §9 (Cat C → Cat D seam verified)
- S1403 F.C1 + F.C6 (inherited as upstream blockers for autonomous cadence)

**Undocumented until S1404:**
- Meeting docstring vs runtime drift (F.D5 + F.D6)
- Parent §3.D writer misclassification (F.D7 + F.D8)
- Structural two-axis correction (F.D9) — OpportunityAction/Task reclassification to Cat A
- Category D single-writer surface for both models (F.D2 + F.D3)
- 12 PA tool action inventory as sole runtime entry-point set
- HumanAttention interlock arc-wide CONFIRMED HIGH (F.D4)

---

## 13. Architecture Maturity

**Four-way split (matching S1403 §13 pattern):**

| Axis | Maturity | Justification |
|------|----------|---------------|
| Meeting write axis (code) | **WORKING** | `MeetingEngine.create_meeting` + `generate_brief` + `add_recap` fully implemented; PA tool actions live at `td_handlers_ops.py:2887-2954`. |
| Meeting write axis (runtime local) | **DORMANT** | `Meeting.objects.count() = 0` at LOCAL; PROD unknown. |
| Meeting autonomous cadence | **DEFERRED-BY-POLICY** | `_policy_meeting_engine` LIVE in registry at `core.py:278`; fires only via deferred `run_ops_autopilot` beat per AUDIT_FINDINGS.md #12. |
| ClosePack write axis (code) | **WORKING** | `CloseTheDealEngine.generate_pack` + `approve_pack` fully implemented; 4 offer templates hardcoded; 7 PA tool actions live. |
| ClosePack write axis (runtime local) | **DORMANT** | `ClosePack.objects.count() = 0` at LOCAL; PROD unknown. |
| ClosePack post-approve state machine | **PARTIAL** | draft→approved transition confirmed; sent/won/lost/expired writers not surfaced in code sweep (may be missing or in a code path we didn't sweep — CANDIDATE for cycle-1 Rigby SIGN). |
| HumanAttention interlock | **MISSING** | Zero writers from any Category D path (F.D4). |
| EngagementEvent → Meeting auto-trigger | **MISSING** | Depends on F.B1 → F.C1 sequential ADR pair. |
| Integrity audit surface | **NOT PRESENT** | No `audit_meeting_orphans` / `audit_close_pack_orphans` management command or Celery task exists. Design-preparation deliverable at §14 D.D8 + §19 R.D8. |

**Coverage classification (matches S1273 §3.32 methodology):**
LIGHT → **MODERATE** after this audit. Category D has non-trivial
service + model + PA-tool surface; enough to write a topic doc if
Chris wants one at S1499 xx99 or as R.D4 deliverable.

---

## 14. Known Drift

Drift matrix — where documented claims mismatch runtime reality:

| # | Source doc/claim | Runtime reality | Severity | Recommendation |
|---|---|---|---|---|
| D.D1 | `Meeting` model docstring at `core/models_meeting.py:22` — "Created manually or from EngagementEvent intent detection" | **EngagementEvent fork is uninhabited.** Sole writer at `engagement.py:490-526` never sets `engagement=` FK (F.D2). Even if the model had rows, `engagement_id` would be NULL 100% of the time on this path. | **HIGH docstring / bounded runtime (F.D1)** | Update docstring to reflect implemented behavior: "Created manually via PA tool `meeting_create`. EngagementEvent → Meeting auto-trigger is a post-arc design candidate; requires S1402 F.B1 delivery ADR + S1403 R.C1 F.C1 ingestion ADR as upstream blockers." Bundle with §19 R.D3 anchor updates. |
| D.D2 | `Meeting` module docstring at `:10` — "Lifecycle: scheduled -> briefed -> completed -> followed_up" | Only 3 states are code-reachable (`scheduled → briefed → completed`) per F.D6. `followed_up` never written. `STATUS_CHOICES` at `:27-34` declares 3 additional states (`no_show`, `cancelled`, `followed_up`); none are writable in code. | **MEDIUM** (docstring simplifies runtime; not misleading operators, but code readers hit the gap; symmetric to S1402 D.B8 CHANNEL_CHOICES over-modeling) | Two forks: (i) implement the missing writers (no_show → auto-flag at scheduled_at + duration_minutes < now via a scheduled task; cancelled → PA tool action; followed_up → follow-up-sent hook); (ii) trim `STATUS_CHOICES` to `[scheduled, briefed, completed]` until missing writers exist. Post-arc design-preparation. |
| D.D3 | Parent §3.D `platform_architecture_inventory.md §3.32` names `ClosePackAutonomyEngine` at `revenue.py:1504` as the ClosePack writer | Direct read confirms `ClosePackAutonomyEngine` is READ-only monitoring (F.D7). Actual writer is `CloseTheDealEngine.generate_pack` at `revenue.py:851/:931/:991`. | **MEDIUM** (parent-doc drift — steers future readers wrong) | Anchor-update at `docs/research/platform_architecture_inventory.md §3.32`: retain `ClosePackAutonomyEngine` under "Major services (monitoring surface)" + add `CloseTheDealEngine` under "Major services (writer surface)". Also update `1400_revenue_domain_scoping.md §3.D` to reflect the split. **Immediate anchor-update, not synthesis-deferral** (matches S1402 §14 D.B3 + S1403 §14 D.C1 anchor discipline). |
| D.D4 | Parent §3.D lists `MeetingCoordinatorAgent` (`core/agents/executive/meeting_coordinator_agent.py:66`) as a Category D primary system | Direct read: agent is executive-agent facilitation (multi-agent CTO/COO/CreativeDirector synthesis); zero `Meeting.objects.create` calls (F.D8). | **MEDIUM** (parent-doc category-drift) | Anchor-update at `1400_revenue_domain_scoping.md §3.D`: remove `MeetingCoordinatorAgent` from Category D primary systems; add note "MeetingCoordinatorAgent is agent-orchestration, not Revenue Meeting scheduling — see Agent System topic." |
| D.D5 | Parent §3.D lists `OpportunityAction` + `OpportunityTask` as Category D "lifecycle checkpoints" | Direct FK graph: both models are parallel action/task-state axes with zero FK to Meeting/ClosePack + written from Category A code paths (`views_opportunity.py` + `opportunity_scoring_agent.py:1013`) per F.D9. | **MEDIUM** (parent-doc scope-drift) | Anchor-update at `1400_revenue_domain_scoping.md §3.A + §3.D`: move `OpportunityAction` + `OpportunityTask` from Category D into Category A (they are Opportunity-adjacent tracking, matching S1401 §4.1 Category A owned-models set). |
| D.D6 | `Meeting.trace_id`, `user`, `prospect_role`, `notes`, `next_steps`, `outcome`, `brief_text`, `recap_draft` fields declared at `core/models_meeting.py:70-116` | Sole writer at `engagement.py:507` never sets `trace_id`, `user`, `prospect_role`; later writers (`generate_brief` at `:641`, `add_recap` at `:677`) DO set `brief_text`, `notes`, `next_steps`, `outcome`, `recap_draft` — but `trace_id` + `user` + `prospect_role` remain empty across all writer paths. | **LOW-MEDIUM** (F1/F2 orphan-write class — inherited from S1399 §4 F2 methodology; symmetric to S1402 F.B2 + S1403 F.C3) | Two options: (i) populate `user=` at `create_meeting` from PA-tool caller context (fixes orphan attribution); (ii) document intentional NULL + narrow model schema. Post-arc design-preparation. |
| D.D7 | `ClosePack.user`, `outreach_draft`, `trace_id` fields declared at `core/models_close_pack.py:83-100` | Sole writer at `revenue.py:991` never sets them (F.D3 sibling-orphan pattern). | **LOW-MEDIUM** (same F2 class as D.D6) | Same recommendation as D.D6 — populate `user=` from PA-tool caller + `outreach_draft=` from opportunity FK bridge (when F.B1 ADR lands); post-arc. |
| D.D8 | `Meeting.recap_draft` docstring at `:24` — "Post-meeting recaps require human approval before sending" | No schema-enforced approval gate. No `HumanAttentionItem` FK on Meeting. No `approval_state` field. No code path enforces approval before a hypothetical send. (Send path itself doesn't exist — F.B1 blocker inheritance.) | **HIGH docstring** (declares guardrail; runtime enforcement is procedural-at-operator-judgment only, not schema-enforced) | Two forks: (i) implement HAI interlock (see R.D6 design-preparation ADR); (ii) update docstring to reflect procedural-only guardrail ("Recap drafts require operator review before send subsystem consumes; enforcement is procedural at PA-tool workflow level, not schema-enforced"). Bundle with D.D1 anchor updates. |
| D.D9 | `_policy_meeting_engine` + `_policy_close_pack_autonomy` fire on 10-min cadence per implicit inheritance from `run_ops_autopilot` docstring | Both LIVE in policy registry (`core.py:278` + `:282`) but fire only via `run_ops_autopilot` beat wrapper which is DEFERRED per AUDIT_FINDINGS.md #12 (0 of 92 enabled PeriodicTasks; 30d `celery_task_history` → 0 firings). Inherited from S1403 F.C6. | **DEFERRED-BY-POLICY** (not a bug) | Rigby cycle 1 Q1 lean applied from S1403: separate ADR outside G1400 arc for the `run_ops_autopilot` enable-decision (cross-category impact spans A/B/C/D/E/F policy hooks). This audit does NOT propose enablement; xx99 canonical summary at S1499 cross-links the ADR. |

---

## 15. Known Technical Debt

Debt matrix — Category-D-scoped items grounded in code evidence:

| # | Debt | Evidence | Severity | Recommendation |
|---|---|---|---|---|
| T.D1 | F.D4 Revenue → HumanAttention interlock CONFIRMED MISSING at arc-wide level (extends B + C findings) | Zero HAI writers from Meeting/ClosePack/CloseTheDealEngine/MeetingEngine/ClosePackAutonomyEngine paths; runtime HAI distribution shows 0.07% ops_autopilot (2 rows total in 3061), none from Cat D | **HIGH** (arc-wide inheritance for xx99) | §19 R.D6 HumanAttention interlock ADR — bundle with S1402/S1403 findings at S1499 xx99 canonical summary. |
| T.D2 | Meeting write axis is single-writer + omits 4 fields (trace_id, user, prospect_role) | `engagement.py:507` creates rows with 9 fields populated, 4 fields NULL (D.D6) | **LOW-MEDIUM** (F2 orphan-write class per S1399 §4 F2 lens) | §19 R.D1 Meeting writer normalization ADR (populate `user=` from caller context; `trace_id=` from PA session; `prospect_role=` optional). |
| T.D3 | ClosePack write axis is single-writer + omits 3 fields (user, outreach_draft, trace_id) | `revenue.py:991` creates rows with 7 fields populated, 3 fields NULL (D.D7) | **LOW-MEDIUM** (F2 orphan-write class) | Bundle with T.D2 in §19 R.D1. |
| T.D4 | 3 declared Meeting `STATUS_CHOICES` unreachable in code | Direct grep confirms no writer sets `no_show`, `cancelled`, `followed_up` (D.D2 + F.D6) | **LOW-MEDIUM** (over-modeled enum per S1402 D.B8 pattern) | §19 R.D2 state-machine completion ADR — decide whether to build missing writers or trim declared choices. |
| T.D5 | ~~ClosePack post-approve state machine PARTIAL~~ **PROMOTED to F.D10 CONFIRMED HIGH via SIGN cycle 1 joint verifier-loop** (Rigby broader grep + parent-Claude direct-read disambiguation at `revenue.py:1100-1180`). Writers exist for `draft` (default), `approved` (:1073), `expired` (:1173 bulk update). `sent`/`won`/`lost` writers CONFIRMED ABSENT. See F.D10 in §1 for full evidence. | See F.D10 | Row retained for cross-reference; do NOT create R.D2 companion per Rigby cycle 1 Q4 lean. F.D10 lands as arc-wide structural finding for xx99 (paired with F.D6 Meeting analog). |
| T.D6 | ClosePack offer templates hardcoded in class literal (`revenue.py:872-929`) | Same pattern as S1402 B.B3 `OpportunityDraftGenerator.SYSTEM_PROMPT` (Session 1225 flagged); changing offers requires redeploy | **LOW-MEDIUM** (offer-configuration debt) | §19 R.D7 — offer-configuration ADR (config-DB-driven `CloseOffer` model vs prompt-hard-binding); post-arc. |
| T.D7 | Meeting `EngagementEvent → Meeting` FK-population is a runtime CANDIDATE F2 CANDIDATE MEDIUM (inherited from S1399 §4 F2 methodology + S1403 F.C3 pattern) | Sole writer omits `engagement=` (F.D2); when F.B1 → F.C1 ADRs land, if the new auto-trigger writer also omits engagement FK, this becomes CONFIRMED F2 orphan-write live | **MEDIUM CANDIDATE** (verifier-loop must probe on ADR completion) | Add to F.B1/F.C1 sequential-ADR pair-design checklist: any new Meeting writer MUST populate `engagement=` FK. Cross-link in R.D3. |
| T.D8 | Category D has no `JobContract` + no dedicated queue + no beat schedule | Grep `core/employees/jobs.py` for "meeting" / "close" / "MeetingEngine" / "CloseTheDealEngine" / "ClosePackAutonomyEngine" (case-insensitive) → 0 hits. `settings.py` `task_routes` has no meeting/close/revenue entries. Beat schedule has no meeting/close rows. Inherited from S1274 §14 finding #36 HIGH + S1401 §18 + S1402 §18 + S1403 §18 same-finding | **HIGH INHERITED** | Deferred to S1405 Child E per parent §12.1 D28 arc-scoping decision. S1499 xx99 canonical summary should propose arc-wide runtime-owner JobContract based on Cat E synthesis. |
| T.D9 | Category D has no dedicated Celery queue | `settings.py` `task_routes` has no Category D routes (matches S1402 T.B8 + S1403 T.C4 pattern) | **LOW** (bundle candidate) | Post-arc bundle with S1402 T.B8 + S1403 T.C4 as potential unified `revenue_ops` queue when outbound delivery + ingestion lands. Explicit worker sizing + concurrency caps required per S1403 T.C4 Rigby cycle 2 Q7 rationale. |
| T.D10 | Missing integrity audit surface for 5-model FK chain (`OutreachDraft → EngagementEvent → Meeting → ClosePack`, plus HumanAttentionItem interlock) | No `audit_meeting_orphans` / `audit_close_pack_orphans` / signal-based orphan-prevention exists. S1274 §5.10 tight-coupling LOW-by-design classification requires observability compensation | **MEDIUM DESIGN-DEFICIT** | §19 R.D8 integrity audit design ADR — landing NOW, implementation POST F.B1/F.C1 per Agent 6 recommendation (currently zero rows → no orphans yet; design-preparation lands so implementation team can grab-and-instantiate at ingestion go-live). |
| T.D11 | Zero REST API for Meeting/ClosePack | No `path(...)` for Meeting/ClosePack in `core/urls*.py` | **LOW** | Not a debt — PA-tool-only surface is intentional per operator-driven design. If Chris ever wants a UI dashboard for close pipeline, REST would be needed. Post-arc if surfaced. |
| T.D12 | Zero WebSocket real-time push for Meeting/ClosePack | No `consumers*.py` for meeting/close_pack | **LOW** | Same as T.D11 — intentional; UI-driven need would surface it. |

---

## 16. Boundary Violations

Category D boundary check — imports/reaches from Category D code
into other domains' internals:

| # | Violation | Severity | Notes |
|---|---|---|---|
| B.D1 | `MeetingEngine.generate_brief()` reads `EngagementEvent.objects.get(id=meeting.engagement_id)` at `engagement.py:606` | OK | Category C read from Category D is a documented seam per S1403 §9 row 4. Reading engagement context for brief composition is a legitimate seam. |
| B.D2 | `CloseTheDealEngine.generate_pack` reads `Opportunity` (Category A) for opportunity_id resolution | OK | Legitimate seam. |
| B.D3 | `ClosePackAutonomyEngine.get_followup_queue` reads `ClosePack + Opportunity` (Cat A + Cat D) | OK | Same. |
| B.D4 | `EngagementAutonomyEngine.get_meeting_suggestions` in Category C engine reads `Meeting` (Cat D) via existence check at `engagement.py:832-876` | OK | S1403 documented this READ-only surface. Not a violation. |

**No HARD boundary violations found.** Category D respects FK
boundaries + does not reach into HumanAttention/Governance/Content
internals to write.

---

## 17. Duplicate or Overlapping Systems

Three observations:

### 17.1 MeetingEngine + CloseTheDealEngine + ClosePackAutonomyEngine — DIFFERENT AXES, NOT DUPLICATES

MeetingEngine at `engagement.py:479-757` handles meeting-lifecycle
(create/brief/recap) as a WRITE axis. CloseTheDealEngine at
`revenue.py:851-1010` handles close-pack composition + approval
as a WRITE axis. ClosePackAutonomyEngine at `revenue.py:1504-1776`
handles close-pack monitoring (follow-up queue + risk + velocity)
as a READ axis. Three distinct responsibility scopes; no
duplication.

### 17.2 `MeetingCoordinatorAgent` vs `MeetingEngine` — DIFFERENT DOMAINS (F.D8)

Naming similarity is misleading. `MeetingCoordinatorAgent` is an
executive-agent facilitation surface (BaseAgent multi-agent
synthesis); `MeetingEngine` is a Revenue Meeting scheduler +
brief generator. Zero code overlap; different write axes; live in
different subsystems. Parent §3.D miscategorized the agent — this
audit's F.D8 corrects it.

### 17.3 OpportunityAction/OpportunityTask (Cat A per F.D9) vs Meeting/ClosePack (Cat D) — PARALLEL AXES, NO OVERLAP

Discussed at F.D9 + §4.3-§4.4. Four models, two axes, zero FK
between axes. Parent §3.D grouped incorrectly. §14 D.D5 recommends
Cat A reclassification.

---

## 18. Ownership Gaps

**Category D has NO runtime owner** — verifier-loop CONFIRMED:

- **No `JobContract` wiring** — `core/employees/jobs.py` grep for
  "meeting" / "close" / "MeetingEngine" / "CloseTheDealEngine" /
  "ClosePackAutonomyEngine" / "close_pack" (case-insensitive) = 0
  hits. None of the 3 shipped employees (Documentation Manager /
  Platform Auditor / Chief of Staff) name Meeting or Close in
  their `JobContract`.
- **No `AGENT_MAP` entry** for Meeting/ClosePack writers.
  `MeetingCoordinatorAgent` IS in AGENT_MAP at
  `core/agent_router.py:354` but is NOT a Meeting writer (F.D8).
- **No dedicated queue** — `settings.py` `task_routes` has no
  meeting/close entries.
- **No beat schedule row** — Category D surfaces are exercised
  only via the shared `run_ops_autopilot` policy engine cadence
  (deferred per F.D9).

**Inheritance from S1274 §14 finding #36 (unclear_owner HIGH):**
CONFIRMED for Category D. Combined with S1402 (Cat B) + S1403
(Cat C) + S1401 (Cat A partial via ownership deferred to Cat E
per D28), **Group 1400 ownership gap is now CONFIRMED at Categories
A + B + C + D**. Cat E and F remaining.

**Recommendation:** Deferred to S1405 Child E per parent §12.1 D28
arc-scoping decision. S1499 xx99 canonical summary should propose
the arc-wide runtime-owner JobContract based on Cat E synthesis.

---

## 19. Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows.

### R.D1 — Meeting + ClosePack writer normalization ADR (T.D2 + T.D3 F2 orphan-write fix)

Populate `user=` from PA-tool caller context, `trace_id=` from
session, `engagement=` (when F.B1 → F.C1 lands), and
`outreach_draft=` (from Opportunity FK bridge, when F.B1 lands).
Small landing per-model; bundled ADR. Blocks: nothing (independent
model tweaks).

### R.D2 — Meeting state machine completion ADR (T.D4)

Decide whether to build missing writers (`no_show`, `cancelled`,
`followed_up`) or trim declared choices. Sub-questions:
- `no_show` auto-flag from `scheduled_at + duration_minutes < now
  AND status='scheduled'` via a scheduled task (post-arc; requires
  a `check_meeting_no_shows` Celery task)?
- `cancelled` via PA tool `meeting_cancel` action?
- `followed_up` via a hook on outbound-send when F.B1 lands +
  Meeting has `next_steps` text?
Post-arc design-preparation ADR.

### R.D3 — Category D anchor-updates ADR (D.D1 + D.D3 + D.D4 + D.D5 + D.D8) — IMMEDIATE

Anchor-update discipline per S1402 §14 D.B3 + S1403 §14 D.C1 +
Rigby cycle 2 anchor-update discipline:

- `docs/research/domains/revenue/1400_revenue_domain_scoping.md
  §3.D`:
  - Split "Primary systems" into "Writer surface"
    (`MeetingEngine` for Meeting; `CloseTheDealEngine` for
    ClosePack) + "Monitoring surface"
    (`ClosePackAutonomyEngine`, `EngagementAutonomyEngine.get_meeting_suggestions`).
  - Remove `MeetingCoordinatorAgent` from Category D primary
    systems (F.D8).
  - Move `OpportunityAction` + `OpportunityTask` to Category A
    (F.D9).
- `docs/research/platform_architecture_inventory.md §3.32 + §4.9`:
  - Replace `ClosePackAutonomyEngine` writer classification with
    `CloseTheDealEngine`; retain autonomy engine as monitoring.
  - Update Cat D coverage LIGHT → MODERATE.
  - Note: runtime local counts = 0 for Meeting + ClosePack (PROD
    unknown pending T.C8(c)).
- `core/models_meeting.py:22-25` class docstring: update to
  reflect implemented behavior per D.D1 recommendation. Add
  reference to F.B1 → F.C1 sequential-ADR pair as upstream blocker
  for autonomous EngagementEvent → Meeting trigger.
- `core/models_meeting.py:10` module docstring: update lifecycle to
  reflect 3-state reachable set.
- `core/models_close_pack.py:6-12` docstring: update to
  reflect "generated via PA tool `close_pack_generate`; not
  auto-triggered on high-intent" (F.D3 truth correction).

### R.D4 — Optional Category D topic doc (post-arc)

Given Cat D coverage rose to MODERATE, a `docs/topics/meeting-close.md`
would be justified. Not blocking; can be produced at S1499 xx99 or
after.

### R.D5 — Category D policy-hook enablement ADR (INHERITED from S1403 R.C1 disposition)

Cross-links to S1403 Rigby cycle 2 Q1 lean: separate ADR outside
G1400 arc for the `run_ops_autopilot` beat wrapper enable-decision.
Category D policy hooks (`_policy_meeting_engine` + `_policy_close_pack_autonomy`)
inherit the same policy-deferred state.
When the shared ADR lands, Category D policies flip alongside all
other categories. This audit does NOT propose enablement — xx99
canonical summary cross-links the ADR.

### R.D6 — HumanAttention interlock ADR (F.D4 + T.D1 CENTRAL S1404 deliverable — design-preparation, not implementation)

Design the approval-gate for Revenue → HumanAttention. Scope
covers Meeting AND ClosePack conversion points:

- **Meeting recap-send gate:** when a recap is drafted, before it
  can be sent (which requires F.B1 outbound delivery ADR), gate
  send behind `HumanAttentionItem` approval. Category:
  `revenue_meeting_recap_approval`.
- **ClosePack send gate:** when a ClosePack transitions
  `approved → sent`, gate the transition behind
  `HumanAttentionItem` approval. Category:
  `revenue_close_pack_send_approval`.
- **ClosePack won/lost adjudication:** when a follow-up is due
  and no reply, escalate the "mark won/lost/expired" decision to
  `HumanAttentionItem`. Category:
  `revenue_close_pack_outcome_adjudication`.

**FK strategy:**

- Option A: add `revenue_human_attention` FK to Meeting +
  ClosePack (schema change per model).
- Option B: use HAI `source_type` + `source_id` (existing generic
  reference pattern) — write "source_type='revenue_meeting_recap'
  source_id=<meeting.id>" without schema change on Meeting side.

Recommendation lean: Option B (matches existing HAI writer patterns
per Agent 4 sweep + `opportunity_execution_pipeline.py:389`
`source_type='opportunity_execution_pipeline'` precedent).

**Sequential dependency:**
- Meeting recap-send interlock depends on F.B1 outbound-delivery
  ADR landing first (no send subsystem = no send-gate to build).
- ClosePack send-gate has the same dependency.
- **Sequential ADR pair extension** (matches S1403 R.C1 F.B1 →
  F.C1 pair discipline): F.B1 → F.C1 → F.D6 (HAI interlock). The
  HAI ADR can be co-designed during F.B1 pair-design (Rigby cycle
  2 recommendation for how to bundle).

Design-preparation, not implementation. Post-arc ADR.

### R.D7 — ClosePack offer-configuration ADR (T.D6)

Should offers be a config-DB-driven `CloseOffer` model?
Tradeoff between "prompt hard-binding for compliance" (Session 1225
+ S1402 R.B6 rationale for `OpportunityDraftGenerator.SYSTEM_PROMPT`)
and "operator ability to iterate offers without deploy." Same
question class as S1402 R.B6 — bundle recommendation.

### R.D8 — Category D integrity audit design ADR (T.D10 CENTRAL S1404 deliverable)

**Design (not implementation) landing NOW; implementation POST F.B1/F.C1.**

Per Agent 6 finding: current runtime state is zero rows → no
orphans to audit YET. But F.B1 + F.C1 ADRs will enable actual
inbound data to flow. Category D design-preparation lands so
implementation team can grab-and-instantiate at day-1 of live
traffic (avoids "zero-row bootstrap" gap that plagued S1403 Cat C).

**Scope:** 5 models —
`OutreachDraft`, `EngagementEvent`, `Meeting`, `ClosePack`,
`HumanAttentionItem`.

**Orphan patterns to detect (10):**

| # | Model | Condition | Class | Severity hypothesis |
|---|-------|-----------|-------|--------------------|
| O1 | OutreachDraft | `status='draft' AND created_at < NOW-7d` | Stale draft | MEDIUM |
| O2 | OutreachDraft | `status='approved' AND opportunity=NULL AND created_at < NOW-30d` | Approved-but-orphan | HIGH |
| O3 | OutreachDraft | `status='sent' AND opportunity=NULL` | Sent-but-orphan | HIGH (revenue leak) |
| O4 | EngagementEvent | `opportunity=NULL AND outreach_draft=NULL` | Double-null | MEDIUM |
| O5 | EngagementEvent | `status='needs_reply' AND updated_at < NOW-3d` | Stalled | MEDIUM |
| O6 | Meeting | `engagement=NULL AND opportunity=NULL` | Double-null (S1274 §5.10 worst case) | LOW-MEDIUM |
| O7 | Meeting | `scheduled_at < NOW-1d AND status NOT IN (completed, no_show, cancelled)` | Stale in-flight | MEDIUM |
| O8 | ClosePack | `status='draft' AND created_at < NOW-30d` | Stale draft | HIGH |
| O9 | ClosePack | `opportunity=NULL AND outreach_draft=NULL` | Double-null | MEDIUM |
| O10 | ClosePack | `status='sent' AND outreach_draft=NULL` | Attribution-gap | MEDIUM |

**Detection layers:**

- Post-write signals (real-time, low overhead) — warn-log on
  Meeting/ClosePack save with both null-FKs set;
- Daily sweep task (bulk audit, deferred remediation) — Celery
  beat at 2am UTC via `audit_revenue_pipeline_integrity`
  management command + Celery task wrapper;
- On-demand PA tool action `integrity_audit_revenue` —
  operator-triggered.

**Reporting surface:**

- `IntegrityAuditRun` model (new; ~15 fields; landing in a
  future PR alongside implementation) —
  `audit_date, model_name, orphan_pattern_id, count, sample_rows JSONField, severity_estimate`.
- Daily report → Deliverable with `category='audit_result'`,
  title=`Revenue Integrity Audit <date>` (matches existing
  Deliverable pattern; visible in dashboard).
- Escalation surface → auto-create `HumanAttentionItem` with
  `source_type='revenue_integrity'` when count > threshold in
  MEDIUM/HIGH tier (rides on R.D6 HAI interlock design).

**Repair policy:**

- Phase 1 (post-F.B1/F.C1 landing, months 1-2): read-only report.
  Observe real orphan patterns.
- Phase 2 (months 3+): Chris-adjudicated remediation via
  HumanAttentionItem (matches Session 1196 initiative diagnostic
  pattern).
- Kill-switch: `REVENUE_INTEGRITY_AUDIT_ENABLED` setting.

**Precedent references:**

- `core/signals/initiative_diagnostic_signals.py` (Session 1196) —
  post_save signal + pre_save FK stash + `.filter(pk=...).update()`
  no-recursion pattern + TTL retirement (Session 1195).
- `core/management/commands/consolidate_workspaces.py:108,142` —
  `.filter(workspace__isnull=True)` orphan detection + bulk
  reassignment pattern.
- `core/management/commands/fix_workspace_visibility.py:85,149,170`
  — multi-step remediation (detect → propose → apply).
- `core/management/commands/fix_orphan_initiative_tracking.py`
  (Session 906) — retroactive FK-tracking record creation pattern.

**Sequential dependency:** design lands at S1404 (this arc);
implementation lands post-F.B1/F.C1 ADR completion. Between now
and then, zero orphans exist (F.D1), so no implementation gap
exists.

### R.D9 — F1 provenance-filter drift repo-wide sweep (extends S1399 §4 F1 lens to Cat D readers)

Category D readers (`MeetingEngine.get_inbox`, `.get_metrics_report`,
`.evaluate`; `CloseTheDealEngine.get_inbox`, `.get_metrics_report`;
`ClosePackAutonomyEngine.get_followup_queue`, `.get_risk_report`,
`.get_velocity_report`, `.evaluate`) filter on `status`,
`scheduled_at`, `created_at`, `offer_key`. Repo-wide sweep may
reveal provenance drift on other filter fields. Deferred until
F.B1/F.C1 write-side lands (writers must exist before reader-side
drift can be measured meaningfully).

---

## 20. Appendix

### 20.1 Files inspected

- `core/models_meeting.py` (full read, 136 lines)
- `core/models_close_pack.py` (Agent 2 full read + parent-Claude spot-check)
- `core/models_unified_system.py:2552-2600` (OpportunityAction schema)
- `core/models_unified_system.py:3000-3060` (OpportunityTask schema)
- `core/models_engagement.py:1-140` (from S1403 inheritance + FK cross-check)
- `core/models_human_interface.py:20-227` (Agent 4)
- `core/services/ops_autopilot/engagement.py:479-757` (full MeetingEngine)
- `core/services/ops_autopilot/revenue.py:851-1010` (CloseTheDealEngine)
- `core/services/ops_autopilot/revenue.py:1504-1776` (ClosePackAutonomyEngine)
- `core/services/ops_autopilot/core.py:2040-2270` (policy hooks + revenue-pipeline HAI writer)
- `core/services/td_handlers_ops.py:1643-3122` (PA tool handler registrations + `run_ops_autopilot` ad-hoc invocation)
- `core/agents/executive/meeting_coordinator_agent.py:66+` (F.D8 verification)
- `core/agents/analysis/opportunity_scoring_agent.py:1013` (OpportunityTask writer)
- `core/views_opportunity.py:417/486/836/1149` (OpportunityAction writers)
- `core/services/opportunity_execution_pipeline.py:359-410` (F.D9 axis + HAI writer at :389 with `source_type='opportunity_execution_pipeline'`)
- `core/services/event_bus.py:21-31` (EventStream enum)

### 20.2 Sub-agent evidence provenance (§13 6-parallel-Explore sweep)

- **Agent 1** (Meeting model deep-audit) — schema + writer + reader inventory + lifecycle drift + PA tool surface + policy-hook wiring. **Verifier-loop status:** CONFIRMED via direct read.
- **Agent 2** (ClosePack model deep-audit) — schema + writer path resolved to `CloseTheDealEngine.generate_pack` (not `ClosePackAutonomyEngine`) + trigger classification MANUAL + PA tool surface + monitoring engine READ-only nature. **Verifier-loop status:** CONFIRMED via direct grep + read; F.D7 parent-doc drift surfaced.
- **Agent 3** (OpportunityAction/OpportunityTask lifecycle audit) — parallel-axis hypothesis + writer inventory (5+2 sites) + FK-graph confirmation. **Verifier-loop status:** F.D9 hypothesis correction promoted from CANDIDATE to CONFIRMED via cross-check with Agent 6 FK graph.
- **Agent 4** (HumanAttention interlock audit) — 26 total HAI writers + zero Revenue-domain writers + arc-wide inheritance identification (extends B + C). **Verifier-loop status:** CONFIRMED via runtime probe (HAI count 3061 / distribution shows 2 ops_autopilot from unrelated `_policy_revenue_pipeline` monitoring, ZERO from Meeting/ClosePack).
- **Agent 5** (MeetingEngine + policy hook audit) — 6-method inventory + `_policy_meeting_engine` registry entry at `core.py:278` + MeetingCoordinatorAgent misclassification. **Verifier-loop status:** CONFIRMED via direct read at `core.py:2240-2268`.
- **Agent 6** (Integrity audit design proposal) — FK graph across 5 models + existing precedent inventory + 10 orphan patterns + design skeleton. **Verifier-loop status:** design skeleton adopted directly into R.D8.

### 20.3 Parent-Claude verifier-loop provenance

12 direct-verification checkpoints (extending S1403's 11):

1. **Meeting schema (full 136-line read)** — Agent 1 field inventory CONFIRMED.
2. **MeetingEngine.create_meeting method (:490-526 read)** — Agent 1 "engagement FK never populated" CONFIRMED. F.D2 CONFIRMED at CODE tier.
3. **Grep `Meeting.objects.create` repo-wide** — single hit at `engagement.py:507` CONFIRMED. F.D2 CONFIRMED single-writer claim.
4. **Grep `status='no_show|cancelled|followed_up'` repo-wide** — zero hits for Meeting model; all hits are for other models. F.D6 CONFIRMED — 3 declared states unreachable.
5. **Grep `ClosePack.objects.create` + `class CloseTheDealEngine` + `class ClosePackAutonomyEngine`** — confirmed CloseTheDealEngine at `:851` with `ClosePack.objects.create` at `:991`; ClosePackAutonomyEngine at `:1504` is separate READ-only class. **F.D7 parent-doc drift CONFIRMED via direct grep evidence.**
6. **Read `ops_autopilot/core.py:2040-2100` for revenue-pipeline HAI writer** — confirmed `HumanAttentionItem.objects.create` at `:2051` writes with `category='revenue_pipeline'` for "critically stale opportunities" monitoring; not an approval-interlock. F.D4 CONFIRMED — this writer does not gate Meeting/ClosePack creation.
7. **Read `opportunity_execution_pipeline.py:379-410` for `source_type='opportunity_execution_pipeline'` HAI writer** — confirmed this is Category A (Opportunity pre-execution consultation), not Category D. F.D4 nuance: opportunity-execution-approval exists but is Cat A scoped, not Cat D writers gating Meeting/ClosePack.
8. **Grep `source_type='ops_autopilot|revenue_pipeline|meeting|close_pack|engagement'`** — confirmed only `ops_autopilot` source_type exists in the target set (3 writer sites: `governance.py:530`, `core.py:2846`, `verification.py:704`); no `meeting` / `close_pack` / `revenue_pipeline` source_type writer sites. F.D4 CONFIRMED.
9. **Django ORM runtime probe (local env)** — `Meeting.objects.count() = 0`, `ClosePack.objects.count() = 0`, `EngagementEvent.objects.count() = 0`, `OutreachDraft.objects.count() = 40`, `HumanAttentionItem.objects.count() = 3061`. F.D1 CONFIRMED at RUNTIME LOCAL tier. HAI distribution CONFIRMED F.D4 at RUNTIME tier (2 ops_autopilot rows are ~0.07% of total, both attributable to policy-monitoring not approval-interlock).
10. **Cross-check Meeting FK graph against ClosePack FK graph** — no FK between OpportunityAction/OpportunityTask and Meeting/ClosePack; F.D9 CONFIRMED via Agent 6 FK graph + parent-Claude spot-check of model definitions.
11. **MeetingCoordinatorAgent class body read** — confirmed BaseAgent subclass for executive-agent facilitation; zero `Meeting.objects.create` calls in class body. F.D8 CONFIRMED.
12. **AUDIT_FINDINGS.md #12 cross-reference** — `run_ops_autopilot` deferred-by-policy per canonical list per memory rule `feedback_audit_findings_12_canonical_celery_deferred_list.md`. F.D9 policy-hook classification CONFIRMED as INHERITED-BY-POLICY, not new bug.

**Verifier-loop discipline extension (S1401 → S1402 → S1403 → S1404):**

- S1401: 5 sub-agent overreach corrections (dual-representation drift broadening at `consumers_base.py`).
- S1402: 2 pre-SIGN elevations (F.B2 CONFIRMED writer-site; F.B1 reframed as docstring-vs-runtime lifecycle divergence) + joint Rigby ops-probe methodology extension (D.B7 dead-code CONFIRMED).
- S1403: 2 sub-agent corrections (Agent 6 T.C4 dead-code REFUTED via direct read; Agent 5 F2 CANDIDATE UPGRADED to CONFIRMED writer-site) + alternate-path direct-verification when Rigby tool returns indeterminate (Django ORM shell for must-fix #1).
- **S1404: 3 sub-agent corrections + 1 parent-doc drift surfaced.** Agent 1's "single-writer" claim reinforced with grep sweep. Agent 2's writer identification promoted to primary finding at F.D7 (parent §3.D drift). Agent 5's MeetingCoordinatorAgent classification-drift verified via direct read → F.D8 promoted. Agent 3's parallel-axis hypothesis CONFIRMED via Agent 6 FK graph cross-check → F.D9 promoted. This is the first audit to surface a parent-doc anchor drift as a load-bearing finding (F.D7 + F.D8 + F.D9 = 3 parent-doc corrections in one audit).

### 20.4 Category D canonical Q's answered (playbook §9 28-question checklist)

All 28 questions answered (mapping to sections):

- Q1-Q6 Purpose/Boundaries: §2 + §16
- Q7-Q10 Models/Schema: §4
- Q11-Q13 Services/APIs: §5 + §6
- Q14-Q18 Integrations: §9
- Q19-Q20 Events: §10
- Q21-Q23 Documentation/Coverage: §11 + §12
- Q24 Maturity: §13
- Q25 Drift: §14
- Q26 Debt: §15
- Q27 Duplicates: §17
- Q28 Ownership: §18

### 20.5 Parent §12.1 Category D F.iii questions coverage

- **Q1 "When does an EngagementEvent trigger a Meeting (auto vs manual)?"** — MANUAL only (see F.D2 + §7.1 + §7.4). Auto trigger requires F.B1 → F.C1 sequential-ADR pair from S1402+S1403 as blockers.
- **Q2 "How is ClosePack assembled + triggered?"** — MANUAL via PA tool `close_pack_generate` invoking `CloseTheDealEngine.generate_pack` (see F.D3 + §7.2). Resolves S1273 §10.3 UNKNOWN #3.
- **Q3 "Where does HumanAttention interlock (approval-required conversion)?"** — NOWHERE at Meeting/ClosePack level (see F.D4 + §15 T.D1). Arc-wide CONFIRMED HIGH inheritance. Resolves S1274 §2.4 line 294 MISSING to CONFIRMED HIGH.
- **Q4 "What does the integrity audit design look like (S1274 §5.10 orphan-record risk)?"** — 5-model FK chain + 10 orphan patterns + multi-layer detection + Session 1196 precedent (see §19 R.D8).
- **Inherited from S1403 "Given F.C1 (empty) + F.C6 (deferred), how does Category D reason about Meeting-trigger runtime liveness?"** — Category D is CODE-COMPLETE + RUNTIME-DORMANT at LOCAL. Meeting.count=0 CONFIRMS the dormancy pattern. Policy-hook LIVE in registry but fires via deferred `run_ops_autopilot`. Autonomous cadence gated by same F.C6 policy decision (see F.D1 + F.D9). §19 R.D5 cross-links.

### 20.6 15 inherited findings acknowledgment (parent §11.4)

Each of the 15 inherited findings from S1274 + S1399 is cited not
rediscovered:

| # | Inherited finding | S1404 status |
|---|---|---|
| 1 | Revenue domain exists as coherent architectural unit | Confirmed at §2. |
| 2 | Spider → Opportunity STRONG | Confirmed at §9 (upstream to Category D via Opportunity FK). |
| 3 | Revenue → Observability STRONG via ImpactEvent | PARKED (Cat E owns). |
| 4 | Revenue → Initiative MISSING | Deferred to Cat E per D28. |
| 5 | Revenue → Inbox MISSING | Confirmed at Cat B (S1402); N/A for Cat D. |
| 6 | Revenue → HumanAttention MISSING | **CONFIRMED HIGH at Cat D** (F.D4 + §15 T.D1). |
| 7 | Sports/DBAO → Opportunity MISSING | N/A for Cat D (upstream from Cat A). |
| 8 | Outreach/Engagement/Meeting/Close tight-coupling LOW-by-design | CONFIRMED at §17.1 + §8 + F.D5 + §14 D.D6 + D.D7. Integrity audit design at §19 R.D8 preserves the by-design nullability. |
| 9 | Revenue Pipeline no runtime owner HIGH | CONFIRMED at §18 for Cat D. Deferred to Cat E per D28. |
| 10 | Learning bridge revenue_attribution_bridge writes Revenue → UserAgentLearning | PARKED (Cat E). |
| 11 | Revenue Pipeline extraction readiness LOW | Confirmed at §13 (MODERATE after this audit; arc-wide will settle at Cat E close). |
| 12 | S1399 F1 provenance-filter drift methodology | Inherited as diagnostic lens; applied at §19 R.D9. |
| 13 | S1399 F2 row-level orphan-write pattern | Inherited; applied at §15 T.D2 + T.D3 + T.D7. |
| 14 | S1399 F3 Redis-only durability + `@lru_cache` staleness | Inherited; no MeetingEngine/CloseTheDealEngine surfaces show this pattern at code sweep. |
| 15 | S1399 F4 CANDIDATE + severity-correction discipline | Inherited as SIGN methodology; applied at Agent 5 T.C4 dead-code REFUTATION analog in F.D8. |

### 20.7 Open questions for Rigby SIGN cycle 1 (+ cycle-1 Rigby answers folded)

**Q1.** F.D9 recommends reclassifying OpportunityAction +
OpportunityTask from Category D to Category A. This is a
parent-doc §3.D structural correction. Should the anchor-update
at parent §3.D land at S1404 audit merge (immediate) OR wait for
S1499 xx99 synthesis?

**Rigby cycle 1 answer: IMMEDIATE (cycle-2 of S1404).** Reason:
Cat mis-bucketing is directly harmful to S1405 readers and will
pollute S1499 synthesis if left dangling. Anchor correction lands
at parent §3.D at commit-time — see §20.10 "Anchor corrections to
upstream parent" below.

**Q2.** F.D7 + F.D8 surface TWO additional parent-doc drift
corrections (ClosePack writer misidentification;
MeetingCoordinatorAgent miscategorization). Same anchor-update
timing question — immediate vs xx99.

**Rigby cycle 1 answer: IMMEDIATE (cycle-2 of S1404).** Reason:
these are "map is wrong" issues. Leaving them until xx99 guarantees
continued propagation of incorrect mental models across the arc.
Anchor corrections land at §20.10 below.

**Q3.** Meeting model `STATUS_CHOICES` declares 6 states; 3 are
unreachable in code (F.D6). Similar to S1402 D.B8 pattern but at
higher severity because state-machine claims imply behavior.
Should this stay MEDIUM (matches D.B8 stance) or elevate to HIGH
given the "lifecycle" claim in module docstring?

**Rigby cycle 1 answer: KEEP MEDIUM.** Reason: drift/over-modeling,
not currently breaking a writer path (and F.D1 says there's no
runtime data anyway). Escalate to HIGH only if there are consumers
(reports/validators) that assume those states occur.

**Q4.** T.D5 (ClosePack sent/won/lost/expired state-machine
completeness) is a CANDIDATE finding — Rigby SIGN cycle 1 should
verify with a broader grep of `pack.status = ` mutations or a
direct read of `CloseTheDealEngine.approve_pack` body + any
`mark_close_pack_sent` / `_won` / `_lost` helpers. If missing,
elevate to R.D2 companion.

**Rigby cycle 1 answer: PROMOTE TO CONFIRMED, RESTRUCTURE AS
PAIRED F.D6+F.D10 DRIFT FINDING.** Reason: joint Rigby ops-probe
(broader `revenue.py` grep) + parent-Claude direct-read at
`revenue.py:1100-1180` disambiguated Rigby's initial grep hits.
Actual state writers: `draft` (default at `:991`), `approved`
(`:1073`), `expired` (`:1173` bulk `.update()`). `sent`/`won`/`lost`
CONFIRMED unreachable — all grep hits are `.filter()` READS.
**T.D5 promoted to F.D10 CONFIRMED HIGH** — see §1 executive
summary. Removed R.D2 companion tie. Paired arc-level drift finding
with F.D6 Meeting analog for xx99.

**Q5.** R.D6 HumanAttention interlock ADR proposes Option B
(existing HAI `source_type` + `source_id` reference pattern) as
lean. Should this bundle with the F.B1 → F.C1 pair, or land as an
independent sequential dependency after F.B1/F.C1?

**Rigby cycle 1 answer: BUNDLE WITH F.B1 → F.C1 STACKED ADR PAIR.**
Reason: HAI interlock is cross-cutting; designing it separately
before the C→D seam is fixed risks targeting the wrong
write-paths/interfaces. R.D6 updated to state "stacked with F.B1
→ F.C1 pair" sequencing.

**Q6.** R.D8 integrity audit design lands NOW (this audit);
implementation POST F.B1/F.C1. Should Category D also propose a
"pre-implementation smoke test" — e.g., write 3 synthetic Meeting
rows in a test to prove the audit skeleton catches them — as a
CI-level guard against the design skeleton bit-rotting between
S1404 and eventual F.B1/F.C1 completion?

**Rigby cycle 1 answer: YES.** Reason: doc/anchor drift +
"design skeleton" components already present — an early, minimal
bit-rot test prevents the Meeting/ClosePack layer from remaining
permanently non-live while upstream work drags. R.D8 updated with
a "smoke-test companion" bullet: land minimal test in cycle-2 that
creates 3 synthetic Meeting rows + 3 synthetic ClosePack rows and
asserts the orphan-pattern detector fires with expected counts.

**Q7.** Category D has 12 PA tool actions (5 Meeting + 7 ClosePack).
Combined with S1402 Category B (~4-6 outreach actions) + S1403
Category C (9 engagement actions), the Revenue-domain PA-tool
surface is now ~25-27 actions. Should a Group 1400-wide PA-tool
inventory land at S1499 xx99 as a canonical Revenue PA surface
map?

**Rigby cycle 1 answer: YES.** Reason: the inventory is inherently
cross-category (A/B/C/D) and belongs in the xx99 synthesis artifact,
not any single child audit. Cross-linked in §20.10 arc-integration
outputs.

**Q8.** T.C8 tool-surface gap (inherited from S1403) — Chris
ratified D40 minimal-blocking. This audit ran verifier-loop via
parent-Claude Django ORM shell (F.D1 runtime probe) without a
Rigby ORM tool. Should Rigby cycle 2 revisit whether S1404 should
propose landing the T.C8(a) ToolCallRecord query surface + T.C8(b)
bounded ORM row-count tool NOW (before S1405 Category E, which
will need runtime evidence for attribution attribution readers)?

**Rigby cycle 1 answer: LAND NOW.** Reason: S1405 will otherwise
inherit the same attribution uncertainty; giving readers a standard
ToolCallRecord query + bounded ORM row-count method reduces repeat
ambiguity. Cross-linked to R.D3 anchor-updates (add T.C8(a)+(b)
to Group 1400 arc-open queue for pre-S1405 landing).

**Q9.** Category D `MEETING_*` + `CLOSE_PACK_*` EventStream
additions (§10 Q20) — bundle with S1402 `OUTREACH_*` + S1403
`ENGAGEMENT_*` proposals at S1499 xx99 or dedicated ADR?

**Rigby cycle 1 answer: SINGLE S1499 PROPOSAL.** Reason: it's a
unified event taxonomy decision across the lifecycle; make it one
coherent recommendation unless you're immediately implementing
(then ADR). Cross-linked in §20.10 arc-integration outputs.

### 20.8 Chris decisions locked at S1404 open (3)

- **D38 — Launch cadence:** SEQUENTIAL. Chris ratified via "agree all" 2026-07-01.
- **D39 — Arc pin retention:** RETAIN `pa-34d43795e1b24bd3`. Chris ratified via "agree all" 2026-07-01. (Rigby health_check flagged score=55 suggest_fresh; disclosed to Chris; arc continuity discipline outweighs the heuristic.)
- **D40 — T.C8 tool-surface gap timing:** MINIMAL-BLOCKING (option (ii)) — after §13 sweep reveals which gap matters for D. Chris ratified via "agree all" 2026-07-01.

### 20.9 Gating checklist (playbook §17 single-audit graduation criteria)

- [x] Playbook §11.2 20-section template applied fully.
- [x] All 28 canonical Q's answered (§20.4).
- [x] All 4 parent §12.1 Category D F.iii Q's answered + inherited-from-S1403 Q answered (§20.5).
- [x] All 15 inherited findings from parent §11.4 cited not rediscovered (§20.6).
- [x] Parent-Claude verifier-loop applied to sub-agent claims pre-SIGN (§20.3).
- [x] Runtime probe evidence at LOCAL tier (§4.5 + F.D1).
- [x] 20+ Category D-specific findings surfaced (F.D1-F.D10 + T.D1-T.D12 + D.D1-D.D9 = 31 items after cycle-1 F.D10 promotion).
- [x] Rigby SIGN cycle 1 verdict: **SIGN-with-edits, Medium-High confidence, 4 must-fix, 4 nice-to-have** on pin `pa-87ee24cd0d3947ce` (2026-07-01). All Q1-Q9 answered.
- [x] Cycle-1 must-fix folds applied: F.D10 promotion + F.D7/F.D8/F.D9 anchor corrections + Q1-Q9 folded answers.
- [x] Rigby SIGN cycle 2 verdict: **SIGN-clean, High confidence** on pin `pa-87ee24cd0d3947ce` (2026-07-01). NH-2 + NH-3 applied per cycle-2 lean; NH-1 + NH-4 deferred.
- [ ] Chris commit-gate ("commit it").
- [ ] PR opened + reviewed.
- [ ] 4-step docs cascade + `build_docs_provenance` post-merge.
- [ ] ARCHITECTURE_INDEX v22 → v23 bump: §1.26 for S1404 child audit + §8 timeline S1404 row.
- [ ] S1404 SIGN pin `pa-87ee24cd0d3947ce` retired post-PR-merge per playbook §15.
- [ ] OPEN_ARCS row current-child field advanced: "S1403 SIGN-clean cycle 2 (commit-gated) + S1404 queued next" → "S1404 SIGN-clean cycle 2 (commit-gated) + S1405 queued next" (post-SIGN + commit).

### 20.10 Anchor corrections to upstream parent (Rigby cycle 1 Q1+Q2 immediate-fold discipline)

Per Rigby cycle 1 Q1 + Q2 leans, these parent-doc anchor updates
land at S1404 commit-time (immediate, not xx99) to prevent
propagation of incorrect mental models across the remaining Group
1400 arc:

**Anchor correction #1 — Parent §3.D ClosePack writer identification (F.D7).**
Parent doc `docs/research/domains/revenue/1400_revenue_domain_scoping.md
§3.D` currently lists `ops_autopilot/revenue.py:1504
ClosePackAutonomyEngine` as the ClosePack writer. **Direct read at
`revenue.py:1504-1776` confirms this class is READ-only monitoring**
(5 methods, all `.filter()` / `.aggregate()` / no writes). The
actual writer is **`CloseTheDealEngine.generate_pack` at
`core/services/ops_autopilot/revenue.py:851-1010`** (with primary
`ClosePack.objects.create(...)` at `:991`). Parent §3.D update:
retain `ClosePackAutonomyEngine` under "Monitoring surface" +
add `CloseTheDealEngine` under "Writer surface." Corollary update
to platform_architecture_inventory.md §3.32 anchor.

**Anchor correction #2 — Parent §3.D MeetingCoordinatorAgent misclassification (F.D8).**
Parent doc §3.D lists `MeetingCoordinatorAgent` at
`meeting_coordinator_agent.py:66` as a Category D primary system.
**Direct read at `core/agents/executive/meeting_coordinator_agent.py:66-`
confirms the class is a BaseAgent subclass for executive-agent
multi-agent facilitation** (CTO/COO/CreativeDirector synthesis);
zero `Meeting.objects.create` calls in the class body. Parent §3.D
update: **remove `MeetingCoordinatorAgent` from Category D primary
systems**; add explanatory note "MeetingCoordinatorAgent is
agent-orchestration surface (Executive Council facilitation), not
Revenue Meeting scheduling — see Agent System topic." Corollary
update to platform_architecture_inventory.md §3.32.

**Anchor correction #3 — Parent §3.D OpportunityAction/OpportunityTask axis correction (F.D9).**
Parent doc §3.D lists `OpportunityAction` +
`OpportunityTask` as Category D "lifecycle checkpoints."
**Direct FK graph audit** confirms: neither model has FK to
Meeting or ClosePack; both are written from Category A code paths
(`views_opportunity.py` + `opportunity_scoring_agent.py:1013`);
OpportunityTask has 1:1 `OneToOneField` to Opportunity at
`core/models_unified_system.py:3028` (related_name='task') which is
inherently a Category-A-scoped tracking model. Parent §3.D update:
**move `OpportunityAction` + `OpportunityTask` from Category D
primary systems to Category A owned-models set**; add explanatory
boundary note at Category D: "OpportunityAction / OpportunityTask
are Cat A Opportunity-adjacent tracking axes, not Meeting/ClosePack
lifecycle. FK graph confirms zero linkage." Corollary update to
S1401 §4.1 (add OpportunityAction + OpportunityTask to that audit's
Category A owned-models set retroactively at S1499 xx99 or in a
docs-only follow-up commit).

### 20.11 Arc trajectory statement (Rigby cycle 1 fold — Group 1400 → S1499 xx99)

Rigby cycle 1 one-liner (verbatim + light edit for embedding):

> With Categories A/B/C/D now converging on (i) missing Revenue →
> HumanAttention approval/interlock, (ii) ownership gaps, and (iii)
> runtime-liveness breaks preventing Meeting/ClosePack from being
> populated, **S1499 should synthesize a single "activate the revenue
> lifecycle + enforce approval/attention gating" remediation plan**,
> while **immediate anchor/taxonomy corrections prevent further drift**
> across the remaining arc.

**Arc-integration outputs (Rigby cycle 1 fold — cross-linked to Q1-Q9 answers):**

- **HAI interlock (F.D4 + T.D1)** — arc-wide CONFIRMED HIGH across
  Categories B + C + D. F.D6 R.D6 HAI ADR bundles with F.B1 → F.C1
  sequential-ADR pair (Q5 fold).
- **Ownership gaps (§18 + T.D8)** — arc-wide CONFIRMED HIGH across
  Categories A (partial via D28) + B + C + D. Deferred to Cat E
  S1405 per D28.
- **Runtime-liveness dormancy (F.D1)** — Meeting/ClosePack empty
  local; PROD unknown per T.C8(c). Rigby cycle 1 Q8 lean **LAND
  T.C8(a) ToolCallRecord query + T.C8(b) bounded ORM row-count
  NOW pre-S1405**.
- **State-machine over-modeling (F.D6 + F.D10)** — paired arc-level
  structural drift across Meeting + ClosePack; symmetric 3-state
  unreachable gaps. Group 1400 xx99 candidate.
- **EventStream additions (Q9 fold)** — single S1499 xx99 proposal
  bundles `OUTREACH_*` + `ENGAGEMENT_*` + `MEETING_*` +
  `CLOSE_PACK_*` streams.
- **PA-tool inventory (Q7 fold)** — canonical Group 1400 PA-tool
  surface map (~25-27 actions across A/B/C/D) lands at S1499 xx99.
- **Anchor corrections (Q1 + Q2 folds)** — immediate parent-doc
  update at S1404 commit-time per §20.10.
- **R.D8 integrity audit CI guard (Q6 fold)** — bit-rot prevention
  test lands in cycle-2 (3 synthetic Meeting rows + 3 synthetic
  ClosePack rows; orphan-pattern detector fires with expected
  counts). Design-preparation not implementation; smoke-test
  companion to R.D8.

### 20.12 SIGN cycle 1 fold provenance (this section)

**Rigby SIGN cycle 1 outputs applied:**

- Verdict: **SIGN-with-edits, Medium-High confidence, 4 must-fix,
  4 nice-to-have.** Pin: `pa-87ee24cd0d3947ce`. Date: 2026-07-01.

**Must-fix folds (4):**

1. **T.D5 → F.D10 promotion (HIGH):** T.D5 CANDIDATE row rewritten
   at §15 to reference F.D10 CONFIRMED. New F.D10 finding added
   to §1 executive summary (10 F.D findings now vs 9 in draft).
   ClosePack state-machine writer inventory table added to §8.
   R.D2 companion tie removed. Symmetric-drift pairing with F.D6
   Meeting analog noted for xx99 (Rigby cycle 1 Q4 lean).
2. **F.D7 anchor correction (HIGH):** Added §20.10 "Anchor
   corrections to upstream parent" subsection with correction #1
   (parent §3.D ClosePack writer identification). Landing at
   commit-time per Rigby cycle 1 Q2 lean.
3. **F.D8 anchor correction (MEDIUM-HIGH):** §20.10 correction #2
   (parent §3.D MeetingCoordinatorAgent misclassification).
   Landing at commit-time per Rigby cycle 1 Q2 lean.
4. **F.D9 taxonomy correction (HIGH):** §20.10 correction #3
   (parent §3.D OpportunityAction/OpportunityTask move to Cat A).
   Landing at commit-time per Rigby cycle 1 Q1 lean.

**Nice-to-have folds (4 — cycle 2 or landing at cycle-2 discretion):**

1. F.D5 docstring drift wording calibration (separate "model
   claims X" vs "no runtime writers exist" vs "intended future
   path"). Cycle-2 candidate.
2. F.D6 unreachable Meeting statuses "why it matters" 2-sentence
   expansion (harmless over-modeling vs downstream analytics
   confusion). Cycle-2 candidate.
3. Runtime-liveness PROD-facing stub (add a standard "prod check
   method + which tool + which table names" line so S1499
   doesn't inherit purely-local claims). Cycle-2 candidate.
4. EventStream explicit "none found" table listing searched event
   keys (MEETING_*, CLOSE_PACK_*) with result "none found" so
   readers don't re-run the same grep. Cycle-2 candidate.

**Q1-Q9 folds:** applied inline at §20.7 (all 9 answers recorded
verbatim from Rigby cycle 1 turn with reasoning).

**Verifier-loop discipline further extension at S1404:** joint
Rigby broader-grep + parent-Claude direct-read disambiguation for
false-positive grep hits (the `status='sent'` grep on
`ClosePack` returned `.filter()` READS not writes; direct-read of
`revenue.py:1100-1180` confirmed only `approved` + `expired`
writers). Extends S1403 "alternate-path direct-verification when
Rigby tool returns indeterminate" pattern to "**alternate-path
direct-read disambiguation when Rigby grep returns
substring-ambiguous hits.**" Documented as new discipline
extension for S1499 arc-methodology synthesis.
