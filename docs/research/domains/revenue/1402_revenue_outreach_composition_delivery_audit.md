---
title: "S1402 — Group 1400 Revenue Child B (Outreach Composition + Delivery) audit"
status: draft
authority: research
category: child_audit
session: 1402
date: 2026-07-01
parent_arc: docs/research/domains/revenue/1400_revenue_domain_scoping.md
sibling_prior: docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md
playbook: docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
template: playbook §11.2 (20-section child audit)
verifier_loop_applied: true (parent-Claude spot-checks pre-SIGN; 2 NEW drifts caught before Rigby routing)
sign_status: SIGN-clean cycle 2 High confidence (Rigby SIGN cycle 1 SIGN-with-edits 2 must-fix folded + D.B7 dead-code evidence added; cycle 2 5 Q-answer folds applied; SIGN-clean verdict 2026-07-01)
head_git_sha: beda00e5
inherited_findings: 15 (parent §11.4)
---

# S1402 — Group 1400 Revenue Child B (Outreach Composition + Delivery)

> **Load-bearing framing (verifier-loop + SIGN cycle 1 caught).** Category B is a **composition-only system with no delivery** — grep-negative at HEAD `beda00e5` for all send patterns across mainline. OpportunityDraftGenerator composes touch-1 drafts via single-shot LLM; OutreachSequencer manages approve/reject state. Only Touch 1 fires at runtime — Touches 2–4 declared by the sequencer are **dead code at runtime** (D.B7 CONFIRMED post-Rigby probe: zero PeriodicTask wrapper, zero CeleryTaskEvent 30d, zero PA tool action wraps `.evaluate`, zero grep hits for `sequencer.evaluate`). The follow-up materialization code path at `revenue.py:812-829` is a **CONFIRMED writer-site F2 orphan-write pattern** (omits `opportunity=parent.opportunity` on create; writes literal `body_text = "Draft follow-up message needed."`) — but its **runtime blast radius is zero** until an `evaluate` invoker is wired. S1274 §2.4 line 293 "Revenue → Inbox MISSING" is **CONFIRMED HIGH and REFINED** (evidence complete; not CANDIDATE): the missing wire is not just Inbox — the *entire outbound channel is missing*. Approved drafts accumulate at `status='approved'` until they expire 30 days later.

## 1. Executive Summary

**Runtime state (verified at HEAD `beda00e5`):**

- **Composition path (touch 1):** single-shot LLM via `OpportunityDraftGenerator.render_email` (`core/services/ops_autopilot/outreach_generation.py:340`). No Content Deliberation, no reviewer chain. Uses `get_openai_client()` factory (correct per memory rule `feedback_openai_client_factory`). Model `gpt-5-mini`; `max_completion_tokens=4000` (meets reasoning floor per `feedback_gpt5_max_completion_tokens_floor`); `response_format='json_object'`. On LLM failure returns deterministic skeleton via `_fallback_email` (not silent None per `feedback_factory_silent_none_footgun`).
- **Sequencing:** `OutreachSequencer` (`core/services/ops_autopilot/revenue.py:605`) — `MAX_TOUCHES=4`, `TOUCH_DAYS=[0,3,7,14]`, `DAILY_APPROVE_CAP=10`. State transitions: `draft → approved` (line 686), `draft → rejected` (line 720), `approved → expired` (line 838). **No `approved → sent` transition exists in the codebase.**
- **Beat schedule:** `generate-outreach-drafts-daily` at `core/celery.py:457-461` — crontab `hour=7, minute=30` (America/Denver), queue `content`, expires 3600s. Fires `core.tasks.generate_outreach_drafts_daily` → `OpportunityDraftGenerator.generate(limit=5, ...)`.
- **Model:** `OutreachDraft` (`core/models_outreach.py:18`, table `core_outreach_draft`, migration `0292_outreach_draft_model.py`). Sequencer state lives entirely in-model (`touch_number`, `next_touch_at`, `parent_draft` self-FK). Provenance surface: `spider_data_id` (NOT NULL) + `trace_id` + `lead_source` (static seed name `'opportunity_outreach_seed'`). **No `generated_by`, `source_run_id`, `sent_at`, `replied_at` fields.**
- **Outbound channel:** **NONE.** Grep across mainline for `send_outreach|dispatch_outreach|deliver_outreach|outreach\.send|outreach_send` → zero hits. Grep for `sendgrid|postmark|mailgun|smtplib|EMAIL_BACKEND` in mainline (excluding `archive/`, `external-project-docs/`, `ai_core/`) → zero hits. `core/settings.py` defines no `EMAIL_BACKEND`, `SENDGRID_*`, `SES_*`, `MAILGUN_*`, `LINKEDIN_*` credentials.
- **Engagement feedback loop:** **NONE.** `EngagementEvent.outreach_draft` FK exists (`core/models_engagement.py:55-59`, migration `0294_engagement_event_model.py`) but grep across mainline for `EngagementEvent.objects.create|EngagementEvent(` → **zero writer sites** (only the class definition itself). Zero outreach-related `EventStream` values on `core/services/event_bus.py`.

**Load-bearing findings (four, ranked by runtime severity after Rigby SIGN cycle 1 folds):**

- **F.B1 — Delivery path missing (CONFIRMED HIGH, runtime).** OutreachDraft never reaches any recipient. **CONFIRMED HIGH** (not CANDIDATE — evidence complete): grep-negative at HEAD `beda00e5` across mainline for `send_outreach|dispatch_outreach|deliver_outreach|outreach\.send|outreach_send` (0 hits) + `sendgrid|postmark|mailgun|smtplib|EMAIL_BACKEND` (0 mainline hits, only `archive/`+`external-project-docs/`+`ai_core/`) + no provider SDK imports + no send call sites. S1274 §2.4 line 293 CONFIRMED and REFINED (not just Inbox — no outbound wire at all).
- **F.B3 — Engagement feedback loop missing (CONFIRMED HIGH, runtime).** No reply/click/open ingestion path exists. `EngagementEvent.outreach_draft` FK is populated by nothing (`EngagementEvent.objects.create|EngagementEvent(` grep → only the class definition at `core/models_engagement.py:18`, zero writer sites). Category C S1403 will inherit the entire seam build-out as its scope.
- **F.B4 — Cadence declared but not realized at runtime (CONFIRMED via D.B7 probe).** OutreachSequencer declares a 4-touch cadence (Touch 1 day 0, Touch 2 day 3, Touch 3 day 7, Touch 4 day 14) and `MAX_TOUCHES=4`. **Only Touch 1 fires at runtime.** Touches 2–4 depend on `OutreachSequencer.evaluate` being invoked, and no invoker exists: Rigby ops probe shows PeriodicTask.filter(icontains='outreach') → single row `generate-outreach-drafts-daily` (Touch 1 generator); celery_task_history 30d filter=outreach → 7 events all `generate_outreach_drafts_daily`; parent-Claude direct read of `core/services/td_handlers_ops.py:2699-2755` → zero PA tool action wraps `.evaluate` (only `get_inbox`/`approve_draft`/`reject_draft`/`get_metrics_report` exposed); repo-wide grep for `sequencer.evaluate` / `OutreachSequencer().evaluate` → 0 hits. Declared cadence vs implemented cadence divergence.
- **F.B2 — Follow-up composition writer-site is a CONFIRMED F2 orphan-write + literal-stub pattern (code HIGH; runtime blast radius ZERO due to F.B4).** `OutreachSequencer.evaluate()` at `revenue.py:812-829` creates follow-up `OutreachDraft` rows with `body_text = "Draft follow-up message needed."` (TODO-as-production-data) and does **not** pass `opportunity=parent.opportunity` — every follow-up draft would be created with `opportunity=None`. **CONFIRMED writer-site** for F2 orphan-write pattern (not CANDIDATE — code path is deterministic + directly readable at cited line). Repo-wide F2 sweep across other create sites remains CANDIDATE per S1399 §4 F2 lens. **Runtime blast radius is zero** because `evaluate` is dead code per F.B4 above — the orphan-write pattern is present in the codebase but never executes. Post-arc decision-preparation: fix the writer site AND wire `evaluate` (making follow-ups fire, then also fixing the stub content), OR delete `evaluate` + narrow sequencer's declared cadence.

**Inherited findings status (from parent §11.4, 15 findings):**

- **S1274 §2.4 line 293 (Revenue → Inbox MISSING):** CONFIRMED HIGH + REFINED to "no outbound at all." Evidence complete at HEAD `beda00e5`; not CANDIDATE. Wording refinement recommended at anchor-update.
- **S1401 F1 provenance-filter drift lens:** CANDIDATE holds for Category B — `OpportunityDraftGenerator.select_candidate_queryset` filters on `match_score`, `potential_revenue`, `created_at`; no provenance filter on `source` or `metadata['spider_source']`.
- **S1401 F2 orphan-write lens:** **CONFIRMED at writer site `revenue.py:812-829`** (specific code path); **CANDIDATE at repo-wide scope** (other create sites not swept in this audit). **Runtime blast radius bounded to zero** by D.B7 dead-code finding — the orphan-write code path never executes because `evaluate` has no invoker.
- **S1401 F3 Redis-only durability lens:** CLEAN for Category B — verified zero `cache.set` / `redis.set` in `OutreachSequencer` and `OpportunityDraftGenerator`; all state is DB-persistent.
- **S1401 §14 D6 (dual-representation drift):** DOES NOT extend to Category B — `OpportunityDraftGenerator` reads persistent `Opportunity.objects.filter(...)` only; no `intelligence_engine.get_current_opportunities()` consumption.
- **Ownership gap (S1274 §14 #36 HIGH):** CONFIRMED for Category B — no `JobContract` wires `OpportunityDraftGenerator` / `OutreachSequencer`; queue routing to shared `content` (no dedicated outreach queue). Deferred to Child E per D28.
- **Maturity WORKING (S1273 §3.32 baseline):** WORKING with named delivery gap; sub-verdict "WORKING for composition, PARTIAL for delivery" (§13).
- **Coverage LIGHT (parent §11.3):** upgraded to **MODERATE** for Category B by this audit; still LIGHT for delivery + engagement seam. S1499 xx99 aggregate coverage claim to include this.

**Category B classifications:**

- Coverage: **MODERATE** (composition well-documented in S1224/S1225 handoffs + working tests; delivery + engagement seam UNKNOWN/MISSING).
- Maturity: **WORKING (composition) / PARTIAL (delivery)**. Approved drafts accumulate but never leave the database. UI + PA tool + beat + LLM path all fire cleanly.

## 2. Domain Purpose

Category B is the second slot in the Group 1400 Revenue arc, per parent §5 mission sequence A → B → C → D → E → F → xx99. In the mainline pipeline shape declared at S1273 §4.9 (Spider → Opportunity → Outreach → Engagement → Meeting → ClosePack → Revenue → ImpactEvent), Category B owns the transition **Opportunity → OutreachDraft**: given a scored, contactable Opportunity row, compose a first-touch outreach message, gate it behind human approval, and schedule the follow-up cadence.

**Design intent (from model + service docstrings):**

- `core/models_outreach.py:1-11` — "Approval-based outreach sequencing … Never auto-sends — all outreach requires explicit human approval. Lifecycle: draft → approved → sent → replied/expired."
- `core/services/ops_autopilot/revenue.py:605-620` (OutreachSequencer docstring) — "Touch cadence: Touch 1: Day 0 … Touch 4: Day 14 (close the loop). Guardrails: Never auto-sends without approval; Max 4 touches per lead; Daily approval cap: 10; Dedup: won't create draft for spider_data_id with existing active drafts."

**Runtime reality (verifier-loop caught, load-bearing):** the docstring lifecycle names five states (`draft → approved → sent → replied/expired`); the runtime state machine implements three (`draft → approved`, `draft → rejected`, `approved → expired`). No code path advances `status` to `sent` or `replied`. Human approval is the last state transition an OutreachDraft ever experiences before expiry. Documented at §14 D-Docstring drift.

## 3. Canonical Entry Points

Three entry points reach Category B code:

| # | Entry point | File:line | Trigger | Composition invoked? |
|---|---|---|---|---|
| 1 | Beat task `generate-outreach-drafts-daily` | `core/celery.py:457-461` → `core.tasks.generate_outreach_drafts_daily` | crontab `7:30 America/Denver` daily; queue `content`; expires 3600s | Yes (LLM path); `limit=5, scope='all', offers=None` |
| 2 | Cockpit REST endpoint | `core/views_outreach.py:80-96` `outreach_generate()` (POST `/api/cockpit/outreach/generate/`) | User-triggered from Workspace UI (auth-required) | Yes (LLM path); `limit`, `scope`, `offers` from request body |
| 3 | PA tool via `td_handlers_ops.py` (`autopilot_tool` action `outreach_generate`) | Registered handler surfacing OpportunityDraftGenerator to Rigby | Rigby function-call routing from PA chat | Yes (LLM path); parameters from Rigby's tool call args |

A **fourth entry point** exists but does not invoke composition: `OutreachSequencer.evaluate(now)` (`revenue.py:781`) runs from the same beat window and creates **follow-up stub drafts** for approved rows with due `next_touch_at`. This path does not call the LLM; it clones parent-row fields and overwrites `body_text` with the literal placeholder string (see §14 D.B2).

## 4. Major Models

**Sole model: `OutreachDraft`** (`core/models_outreach.py:18`, table `core_outreach_draft`, introduced by `migrations/0292_outreach_draft_model.py`).

**Schema (verified against source, 125 lines total):**

| Field | Type | Constraints | Role |
|---|---|---|---|
| `id` | UUIDField | primary_key, default=uuid.uuid4, editable=False | identity |
| `spider_data_id` | UUIDField | db_index=True, NOT NULL (no blank/null) | **PROVENANCE (only hard-anchored FK)** — SpiderData item that sourced the lead |
| `lead_title` | CharField(200) | NOT NULL | display denormalization |
| `lead_source` | CharField(100) | blank=True | provenance (static string `'opportunity_outreach_seed'` on LLM path) |
| `lead_url` | URLField(500) | blank=True | display denormalization |
| `lead_score` | IntegerField | default=0 | scoring surface |
| `offer_key` | CharField(50) | blank=True | composition (`'ai_automation'` / `'consulting'` / `'content_engine'`) |
| `subject_line` | CharField(200) | blank=True | composition |
| `body_text` | TextField | NOT NULL | composition |
| `channel` | CharField(20) | choices=(email/linkedin/twitter/other), default='email' | delivery channel (declared, unused; see §14 D.B1) |
| `touch_number` | IntegerField | default=1 | sequencer state (1=initial, 2–4=follow-up) |
| `parent_draft` | FK(self) | null=True, blank=True, SET_NULL, related_name='follow_ups' | sequencer state (touch chain) |
| `next_touch_at` | DateTimeField | null=True, blank=True | sequencer state (when next follow-up should generate) |
| `status` | CharField(20) | choices=(draft/approved/rejected/sent/replied/expired), default='draft', db_index=True | lifecycle |
| `rejection_reason` | CharField(200) | blank=True | lifecycle |
| `edited_text` | TextField | blank=True | approval-time override |
| `opportunity` | FK(core.Opportunity) | **null=True, blank=True**, SET_NULL, related_name='outreach_drafts' | **F2 orphan-write CANDIDATE / CONFIRMED at follow-ups (see §14 D.B2)** |
| `trace_id` | CharField(100) | blank=True, db_index=True | provenance (`f"opp_gen:{YYYYMMDD}:{N}"` on LLM path) |
| `user` | FK(AUTH_USER_MODEL) | null=True, blank=True, SET_NULL, no related_name | ownership |
| `created_at` | DateTimeField | auto_now_add=True, db_index=True | audit |
| `updated_at` | DateTimeField | auto_now=True | audit |

**Indexes:** `(status, -created_at)`, `(spider_data_id)`, `(touch_number, status)`.

**Missing fields (§14 D.B4 / §15 T.B3 debt):** No `sent_at`, `replied_at`, `bounced_at`, `provider_id`, `provider_response_json`, `delivery_status`. No `generated_by`, `source_run_id`, `source_agent`. Send-side and replier-side observability are not modeled at all.

**No sibling models.** No `OutreachSchedule`, `OutreachAttempt`, `OutreachSequenceStep`, `OutreachDispatch`, `OutreachDelivery`. Sequencer state is embedded in `OutreachDraft` columns. (`OutreachDraft` is a self-contained sequencer for a system that does not deliver — the model is coherent for its actual runtime state; docstring drift is the design-vs-runtime gap.)

## 5. Major Services

Two service classes plus one Celery task.

### 5.1 `OpportunityDraftGenerator` (`core/services/ops_autopilot/outreach_generation.py:92`)

- **Shape:** stateless utility class; all `@classmethod`.
- **Constants:** `DAILY_GENERATE_CAP=5`, `OFFER_KEYS=('ai_automation', 'content_engine', 'consulting')`, `SEED_SPIDER_NAME='opportunity_outreach_seed'`, `LLM_MODEL='gpt-5-mini'`, `MAX_CANDIDATES_WALKED=200`.
- **Public API:**
  - `generate(limit, scope, offers, user, now)` (line 429) — main entry; returns dict `{created, drafts, errors, skipped_uncontactable, ...}`.
  - `render_email(opportunity, offer_key)` (line 340) — LLM invocation; returns `{'subject': str, 'body': str, 'fallback': bool}`.
  - `is_contactable(opportunity)` (line 178) — 3-branch predicate on email / real domain / company+url.
  - `select_candidate_queryset(scope, user)` (line 221) — Opportunity selection; ordered `match_score desc, potential_revenue desc, created_at desc`. **No provenance filter** (§14 D.B5 / F1 lens).
  - `ensure_spider_data_seed(opportunity)` (line 258) — idempotent LegacySpiderData row creation for the synthetic seed identity `opportunity_outreach_seed`.
  - `build_prompt_payload(opportunity, offer_key)` (line 292) — constructs the user-message JSON.
  - `daily_generated_count(now)` (line 241) — DAILY_GENERATE_CAP accounting.
- **Composition path — RESOLUTION of S1273 §10.3 UNKNOWN #1:** **SINGLE-SHOT LLM. No Content Deliberation, no reviewer chain.** `render_email` at `outreach_generation.py:340-370` calls `client.chat.completions.create(model='gpt-5-mini', messages=[system, user], max_completion_tokens=4000, response_format={'type': 'json_object'})` directly, via `get_openai_client()` factory. No `content_deliberation_runner` import, no `content_review` invocation.
- **Prompt shape:** `SYSTEM_PROMPT` at `outreach_generation.py:116-171` — hard-binds per-offer delivery envelope (WHAT / DEFINITION OF DONE / EXPLICITLY NOT INCLUDED / REQUIRED CHECKPOINT QUESTION); forbids guaranteed-outcome phrases; enforces subject ≤ 7 words, body 120–180 words, "Chris / Donkey Betz" signature. Session 1225 Rigby envelope contribution (documented at file comment lines 111–115).
- **Fallback:** `_fallback_email` at `outreach_generation.py:391-422` returns deterministic skeleton with per-offer `_FALLBACK_QUESTIONS`. On LLM exception: logs warning + returns fallback (**not silent None**; compliant with memory rule `feedback_factory_silent_none_footgun`).
- **Output write:** `generate` at line 491-509 calls `OutreachDraft.objects.create(spider_data_id=seed.id, opportunity=opp, lead_title=..., subject_line=rendered['subject'], body_text=rendered['body'], channel='email', touch_number=1, status='draft', user=opp.user, trace_id=f"opp_gen:{YYYYMMDD}:{N}", ...)`. **On the LLM/touch-1 path, `opportunity=opp` is populated** — no orphan-write here.
- **Test coverage:** `core/tests/test_outreach_generation.py` (~349 lines, 8 major test cases): contactability variants, seed idempotency, selection filtering, generation cap, round-robin offers, fallback on LLM failure, RemoteOK anti-scrape sanitizer. Separate `core/tests/test_generate_outreach_drafts_daily.py` (~39 lines) exercises the beat-task wrapper.

### 5.2 `OutreachSequencer` (`core/services/ops_autopilot/revenue.py:605`)

- **Shape:** stateful service class (no `__init__` args). Constants: `MAX_TOUCHES=4`, `TOUCH_DAYS=[0, 3, 7, 14]`, `DAILY_APPROVE_CAP=10`.
- **Public API:**
  - `get_inbox(now)` (line 626) — PA-facing pending-drafts view + status_counts rollup + `today_approved` + `remaining_approvals`. Reads counts for `total_sent` (line 666) and `total_replied` (line 667), both of which are **perpetually 0** because nothing writes those statuses (see §14 D.B6).
  - `approve_draft(draft_id, edited_text='')` (line 677) — transitions `status='draft' → 'approved'`; schedules `next_touch_at = now + timedelta(days=TOUCH_DAYS[touch_number])` if `touch_number < MAX_TOUCHES`. **No dispatch, no send, no `apply_async`.**
  - `reject_draft(draft_id, reason='')` (line 720) — transitions `status='draft' → 'rejected'`.
  - `get_metrics_report(now)` (line 766) — reply rate + channel breakdown reads.
  - `evaluate(now)` (line 781) — beat-side follow-up materialization. Selects `OutreachDraft.objects.filter(status='approved', next_touch_at__lte=now, touch_number__lt=MAX_TOUCHES)` (max 10 per cycle), and for each parent creates a follow-up row (see §14 D.B2 for the stub + orphan pattern). Also expires stale approved rows (`updated_at < now - 30d, next_touch_at IS NULL`) via `.update(status='expired')`.
- **Celery integration:** **zero.** No `apply_async` / `countdown` / `eta` calls in `revenue.py`. Grep of `core/services/ops_autopilot/` for `apply_async` returns only remediation.py, verification.py, core.py — all `verify_autopilot_action.apply_async` (Category-A-adjacent, not outreach).
- **F3 durability lens:** CLEAN. Zero `cache.set` / `redis.set` in the sequencer. All state DB-persistent; survives Redis restart.

### 5.3 Celery beat task `generate_outreach_drafts_daily` (`core/tasks.py:~1400-1412`)

- **Decorator:** `@shared_task`.
- **Body:** thin wrapper that invokes `OpportunityDraftGenerator.generate(limit=5, scope='all', offers=None, user=None, now=...)`.
- **Beat entry:** `core/celery.py:457-461` — `'generate-outreach-drafts-daily'` → `crontab(hour=7, minute=30)` America/Denver → queue `'content'` → `expires: 3600`.
- **Timezone-trap history (S1233 pattern):** file comment at `core/celery.py:449-456` notes prior PR #2548 confused UTC vs Denver-local; pinned to Denver-local per operator-edge convention.

## 6. Major APIs and Interfaces

**REST (`core/views_outreach.py`):**

| Endpoint | Method | Handler | Purpose |
|---|---|---|---|
| `/api/cockpit/outreach/generate/` | POST | `outreach_generate()` (~line 80) | Trigger `OpportunityDraftGenerator.generate(limit, scope, offers)` |
| `/api/cockpit/outreach/inbox/` | GET | `outreach_inbox()` | Serve `OutreachSequencer.get_inbox(now)` |
| `/api/cockpit/outreach/approve/` | POST | `outreach_approve()` (~line 50) | Transition `draft → approved` via `sequencer.approve_draft(draft_id, edited_text)` |
| `/api/cockpit/outreach/reject/` | POST | `outreach_reject()` | Transition `draft → rejected` |
| `/api/cockpit/outreach/metrics/` | GET | `outreach_metrics()` | Serve `sequencer.get_metrics_report(now)` |

All auth-required (per SESSION_1224 handoff line 104).

**PA tool (`core/services/td_handlers_ops.py`):** `autopilot_tool` action `outreach_generate` (mirrors REST POST) — Rigby function-call surface. Actions `outreach_inbox`, `outreach_approve`, `outreach_reject`, `outreach_metrics` likely follow the same pattern; see Category B §11 handoff coverage for full inventory (SESSION_1224).

**Workspace UI:** SESSION_1224 shipped end-to-end vertical slice through to a Workspace panel; specific route/component names not audited in this session.

**No dispatch API.** No endpoint / task / PA tool action for `outreach_send`, `outreach_dispatch`, `outreach_deliver`. See §14 D.B1.

## 7. Runtime Flows

**Flow α — Daily composition (LLM path, touch 1):**

```
crontab(hour=7, minute=30 Denver) at core/celery.py:459
  → beat fires generate-outreach-drafts-daily → queue 'content'
  → generate_outreach_drafts_daily (core/tasks.py)
  → OpportunityDraftGenerator.generate(limit=5, scope='all', offers=None)
    → select_candidate_queryset(scope='all', user=None)
       — orders by (match_score desc, potential_revenue desc, created_at desc)
       — filters out opps with existing touch-1 draft (dedup)
    → for each candidate ≤ DAILY_GENERATE_CAP:
        → is_contactable(opp) gate
        → ensure_spider_data_seed(opp) → LegacySpiderData row idempotent
        → build_prompt_payload(opp, offer_key)  # round-robin OFFER_KEYS
        → render_email(opp, offer_key)
           → get_openai_client() → gpt-5-mini @ max_completion_tokens=4000, json_object
           → on Exception → _fallback_email() (deterministic skeleton, fallback=True)
        → OutreachDraft.objects.create(
             spider_data_id=seed.id, opportunity=opp,
             subject_line=rendered['subject'], body_text=rendered['body'],
             channel='email', touch_number=1, status='draft',
             trace_id=f"opp_gen:{YYYYMMDD}:{N}", user=opp.user
           )
```

**Flow β — Human approval (from UI or PA tool):**

```
Workspace UI or Rigby chat
  → POST /api/cockpit/outreach/approve/ (or autopilot_tool action=outreach_approve)
  → OutreachSequencer.approve_draft(draft_id, edited_text)
    → OutreachDraft.get(id=draft_id, status='draft')
    → draft.status = 'approved'
    → if touch_number < MAX_TOUCHES:
        draft.next_touch_at = now + timedelta(days=TOUCH_DAYS[touch_number])
    → draft.save()
    → return {approved: True, ...}
[END OF DRAFT'S OBSERVABLE LIFECYCLE UNTIL EXPIRY OR FOLLOW-UP MATERIALIZATION]
```

**Flow γ — Follow-up materialization (evaluate cadence — CONFIRMED DEAD CODE per §14 D.B7 post-Rigby probe; this flow does not execute at runtime):**

```
OutreachSequencer.evaluate(now):
  → count status='draft' → pending_drafts
  → select status='approved' AND next_touch_at <= now AND touch_number < MAX_TOUCHES (max 10)
  → for each parent:
      if OutreachDraft.filter(parent_draft=parent).exists(): continue
      OutreachDraft.objects.create(
        spider_data_id=parent.spider_data_id,
        lead_title=parent.lead_title, lead_source=parent.lead_source,
        lead_url=parent.lead_url, lead_score=parent.lead_score,
        offer_key=parent.offer_key, channel=parent.channel,
        touch_number=parent.touch_number + 1,
        parent_draft=parent,
        body_text="[Follow-up #N for: <lead_title>]\n\nDraft follow-up message needed.",
        trace_id=parent.trace_id, user=parent.user,
        # ⚠️ opportunity NOT PASSED → opportunity=None → ORPHAN
        # ⚠️ subject_line NOT PASSED → blank
      )
  → expire stale approved (updated_at < now - 30d, next_touch_at IS NULL) → status='expired'
```

**Flow δ — Delivery (DOES NOT EXIST):**

```
There is no Flow δ. approve_draft() saves and returns. evaluate() creates
stubs and returns. No task, no endpoint, no PA action calls any provider
send() method. The status='sent' and status='replied' enum values are
declared on OutreachDraft.STATUS_CHOICES but no code writes them.
```

**Flow ε — Engagement feedback (DOES NOT EXIST):**

```
EngagementEvent.outreach_draft FK (core/models_engagement.py:55-59) is
declared. Zero writer sites across the codebase. No webhook receiver, no
polling task, no event-bus stream (event_bus.py has no OUTREACH_* stream).
```

## 8. Data Ownership and Lifecycle

**Owner of `OutreachDraft` rows:** ambiguous. On LLM path (touch 1), rows have `user=opp.user` (a real end-user FK). On follow-up path (touches 2–4), rows inherit `user=parent.user` — but note: `opportunity=NULL`, `subject_line=""`, `body_text=<placeholder>`.

**Lifecycle (declared vs runtime):**

- **Declared** (model docstring line 10 + OutreachSequencer docstring): `draft → approved → sent → replied/expired`.
- **Runtime** (verified via grep of `status = '<value>'` assignments in mainline):
  - `status='draft'` → created state (LLM path: touch-1 with full content; evaluate path: touch-2+ with stub content).
  - `status='approved'` written at `revenue.py:686` by `approve_draft`.
  - `status='rejected'` written at `revenue.py:720` by `reject_draft`.
  - `status='expired'` written at `revenue.py:838` by `evaluate` bulk-update on stale approved rows.
  - `status='sent'` → **zero writers.**
  - `status='replied'` → **zero writers.**

**Terminal states (runtime):** `rejected`, `expired`. There is no `sent` terminal because there is no send.

**Retention:** no explicit deletion path. Rows accumulate; approved-without-next-touch rows expire after 30 days.

**Provenance surface (F1 lens):**

- `spider_data_id` — hard-anchored NOT NULL. Points at `LegacySpiderData` row (either real spider ingestion, or synthetic seed at name `opportunity_outreach_seed`).
- `lead_source` — static `'opportunity_outreach_seed'` on LLM path; inherited from parent on follow-up path.
- `trace_id` — `f"opp_gen:{YYYYMMDD}:{N}"` on LLM path; inherited from parent on follow-up path.
- **No `generated_by`, `source_run_id`, `source_agent` fields.** Cannot distinguish LLM path from fallback path at the row level (only in the ephemeral `fallback=True/False` dict returned to caller, not persisted).

## 9. Integrations With Other Domains

Integration map verified against S1274 baseline + S1401 §9.1; verifier-loop applied.

| Adjacent domain | S1274 baseline | S1402 Category B verified | Verdict | Evidence |
|---|---|---|---|---|
| Opportunity → Outreach (Category A → Category B) | STRONG-mediated | STRONG CONFIRMED | CONFIRMED | `outreach_generation.py:475-509` writes `OutreachDraft(opportunity=opp)`; select_candidate_queryset reads persistent `Opportunity.objects.filter(...)`. |
| Outreach → Content (Category B → Content Pipeline) | UNKNOWN — reviewer chain question | **NOT INTEGRATED** — no Content Deliberation invocation | RESOLVED (negative) | Grep of `outreach_generation.py` for `content_deliberation_runner`, `content_review`, `reviewer_chain` returns 0 hits. Single-shot LLM only. |
| Outreach → Email/LinkedIn/Discord (outbound channel) | MISSING (S1274 §2.4 line 293) | **CONFIRMED MISSING — no channel wired at all** | CONFIRMED + REFINED | Zero grep hits for send patterns; no `EMAIL_BACKEND` / provider SDK imports in mainline. |
| Outreach → Inbox (S1274 §2.4 line 293) | MISSING | Reclassified — MISSING is a subset of the broader "no outbound wire" finding | CONFIRMED + REFINED | Same evidence as above. Anchor-update: wording should clarify "no outbound channel of any kind." |
| Outreach → EngagementEvent (Category B → Category C write direction) | UNKNOWN | **CONFIRMED MISSING** — FK exists (`EngagementEvent.outreach_draft`), zero writers | CONFIRMED | Grep across mainline for `EngagementEvent.objects.create|EngagementEvent(` returns only class definition at `core/models_engagement.py:18`. Migration `0294_engagement_event_model.py:140-148` creates FK schema. |
| Engagement → Outreach (Category C reads) | UNKNOWN | **CONFIRMED READ-ONLY** direction — Engagement reads Outreach, Outreach never writes Engagement | CONFIRMED | `revenue.py:1209-1306` `RevenueOrchestrator.get_full_pipeline` reads `EngagementEvent` for status rollup; `ops_autopilot/engagement.py:255-440` `EngagementEngine` reads only. |
| Outreach → EventBus | UNKNOWN | **NO STREAMS** | CONFIRMED (negative) | `core/services/event_bus.py:21-31` `EventStream` enum has zero `OUTREACH_*` values. |
| Outreach → Initiative | MISSING (parent §11.4 inherited) | UNKNOWN (not in Category B code scope; Category E owns per D28) | PARKED | Deferred to S1405. |
| Outreach → HumanAttention | MISSING (parent §11.4 inherited) | UNKNOWN (Category D owns Meeting/Close boundary) | PARKED | Deferred to S1404. |
| Outreach → Observability (`ImpactEvent`) | STRONG (S1274) | UNKNOWN (Category E owns) | PARKED | Deferred to S1405. |
| Outreach → PA (Rigby function-call surface) | Not in S1274 | STRONG (three tool actions: `outreach_generate`, `outreach_inbox`, `outreach_approve` at minimum) | CONFIRMED | `td_handlers_ops.py` handler registration (per SESSION_1224 line 30). |

**Producer inventory (writers of `OutreachDraft.objects.create(...)`):**

1. `OpportunityDraftGenerator.generate` (`outreach_generation.py:~491-509`) — touch-1 LLM composition; **populates `opportunity=opp` (not orphan-writable on this path)**.
2. `OutreachSequencer.evaluate` (`revenue.py:812-829`) — touch-2+ follow-up stubs; **does NOT pass `opportunity=` → orphan-writes** (see §14 D.B2).

**Consumer inventory (readers of `OutreachDraft`):**

- `OutreachSequencer.get_inbox` — status='draft' pending list + status counts.
- `OutreachSequencer.approve_draft` / `reject_draft` — individual row transitions.
- `OutreachSequencer.evaluate` — status='approved' due-follow-up scan.
- `OutreachSequencer.get_metrics_report` — reply-rate + channel breakdown.
- `RevenueOrchestrator.get_full_pipeline` (`revenue.py:1209+`) — dashboard rollup.

## 10. Event Flows

**Q19 — What events does Category B emit?**

**None.** `core/services/event_bus.py` `EventStream` enum defines: `SPIDER_DATA`, `OPPORTUNITY_CREATED`, `OPPORTUNITY_SCORED`, `VALIDATION_REQUIRED`, `VALIDATION_DECIDED`, `OUTCOME_RECORDED`, `MODEL_TRAINED`, `SYSTEM_ALERT`. Zero outreach-related streams.

**Q20 — What events should Category B emit?**

Given the missing send + engagement seams, the natural emission points are:

- `OUTREACH_APPROVED` — emit from `approve_draft` at revenue.py:699 (after `draft.save()`). Would let a delivery subsystem subscribe without coupling to sequencer internals.
- `OUTREACH_SENT` — emit from a delivery task (when built). Would let observability + analytics + engagement layers subscribe.
- `OUTREACH_REPLIED` — emit from an inbound-reply webhook / ingestion path (when built). Would trigger Category C engagement writes.
- `OUTREACH_OPENED` / `OUTREACH_CLICKED` — provider-webhook-driven; would populate engagement metrics.

Emissions of these events are the natural coupling seam between Category B and (a) a future dispatch subsystem, (b) Category C engagement layer. Not implementing them means every future consumer would need to poll `OutreachDraft.status` — coupling grows quadratically.

Post-arc design-preparation candidate: adopt an outreach stream set on `EventStream` before wiring providers.

## 11. Existing Documentation

**Category B has no CANONICAL topic doc.** No `docs/topics/outreach-composition.md` or `docs/topics/outreach-delivery.md` — matches parent §11.3 baseline that no Revenue CANONICAL topic doc exists.

**Existing partial coverage:**

| Doc | Category B coverage | Completeness | Cite-forward |
|---|---|---|---|
| `docs/research/platform_architecture_inventory.md` §3.32 + §4.9 | Category B named in cross-domain flow row; coverage LIGHT | cursory | S1273 v2 |
| `docs/research/platform/cross_domain_integration_audit.md` §2.4 line 293 | "Revenue → Inbox MISSING; outreach outbound channel is UNKNOWN" (verbatim) | targeted-but-narrow | S1274 |
| `docs/research/domains/revenue/1400_revenue_domain_scoping.md` | §10.2 Category B evidence surface + §12.1 Q's + 15 inherited findings | scoping-stage | S1400 |
| `docs/handoffs/SESSION_1224_OUTREACH_PIPELINE_AND_TOKEN_BUDGET_SWEEP.md` | End-to-end vertical slice ship record (backend generator → 5 REST endpoints → Workspace UI → live LLM emails "landing in the inbox"); daily cap 5/5 | high | S1224 |
| `docs/handoffs/SESSION_1225_OUTREACH_REFINEMENT_AND_CONVERSATION_ROTATION.md` | Rigby-envelope hardening (per-offer delivery scopes hard-bound to `SYSTEM_PROMPT`); anti-scrape sanitizer; conversation rotation; **flagged: "OutreachSequencer.evaluate() handles touches 2-4 with hardcoded text — no prompt to enforce there"** | targeted | S1225 |
| `docs/handoffs/SESSION_1208_CAMPAIGN_ORCHESTRATOR_OUTBOUND_PACK_HARDENING.md` | Campaign orchestrator hardening (distinct system: not opportunity outreach) | off-target | S1208 |
| `docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md` | Category A ↔ Category B seam evidence at §9.1 (Opportunity → Content WEAK-mediated CONFIRMED); §14 D6 dual-representation (does NOT extend to Category B); §19 R1 umbrella (F1 provenance-drift extends to Category B reader surface) | partial (seam-only) | S1401 |
| `docs/PLATFORM_INVENTORY.md` | `OutreachDraft` listed among 588 models; `generate_outreach_drafts_daily` listed among Beat Schedule rows | mention-only | inventory anchor |

**No prior handoff dedicated to Category B architecture.** SESSION_1224 and SESSION_1225 record ship events but do not synthesize the delivery-gap.

## 12. Research Coverage

**Verdict: MODERATE** — upgraded from LIGHT (S1273 §3.32 baseline).

**Evidence:**

- Two implementation-focused handoffs (S1224 + S1225) document the composition vertical slice end-to-end with concrete file-line references and test coverage.
- Two test files exist (`test_outreach_generation.py`, `test_generate_outreach_drafts_daily.py`) with 8+ test cases exercising contactability, seed idempotency, generation cap, offer round-robin, fallback path.
- S1274 §2.4 named the outbound-channel gap.
- S1401 §9.1 named the Category A ↔ Category B seam.
- This audit synthesizes composition + sequencer + delivery-gap + engagement-gap in one document.

**Still LIGHT for:**

- Delivery / outbound channel (does not exist).
- Engagement seam (Category C S1403 scope).
- Follow-up composition (touches 2–4 are stubs by design; separate composition system implied but not built).

## 13. Architecture Maturity

**Verdict: WORKING (composition) / PARTIAL (delivery)** — split verdict per playbook §12 severity nuance.

**Evidence FOR WORKING (composition half):**

- LLM path deployed end-to-end; live production LLM invocations verified in S1224 handoff.
- Beat task fires daily; production PeriodicTask row confirmed by S1225 (post first-fire 2026-06-24).
- Guardrails enforced: contactability gate, daily cap, prompt envelope scope, approval-required gate.
- Test suite passes (per S1224/S1225 PRs).
- Fallback path deterministic — no silent-None footgun.

**Evidence FOR PARTIAL (delivery half):**

- Zero delivery code path — approved drafts terminate at DB row without being sent (F.B1 CONFIRMED HIGH; grep-negative evidence complete).
- OutreachDraft docstring names five states; runtime implements three (D.B1).
- OutreachSequencer declares 4-touch cadence but only Touch 1 fires at runtime — Touches 2–4 depend on `evaluate` which is CONFIRMED DEAD CODE per D.B7 (F.B4).
- Follow-up composition writer-site (`revenue.py:812-829`) is a CONFIRMED F2 orphan-write + literal-stub pattern in the codebase (F.B2), but its runtime blast radius is zero because the containing `evaluate` method has no invoker.
- No email/LinkedIn/Discord/etc credentials configured.
- No event-bus streams for outreach.
- No engagement writer for reply/click/open ingestion (F.B3 CONFIRMED HIGH).

**No evidence** of critical breakage on composition. Delivery half is a **missing subsystem**, not a broken one. WORKING/PARTIAL is accurate.

## 14. Known Drift

Drift matrix — where documented claims mismatch runtime reality:

| # | Source doc/claim | Runtime reality | Severity | Recommendation |
|---|---|---|---|---|
| D.B1 | `OutreachDraft` model docstring (`models_outreach.py:10`) + `OutreachSequencer` docstring (`revenue.py:606-620`) — lifecycle "draft → approved → sent → replied/expired" | **Zero code writes `status='sent'` or `status='replied'`** in mainline. Grep verified. | **MEDIUM** (per Rigby SIGN cycle 2 Q3: docstring-vs-runtime is misleading but not a runtime failure; **elevates to HIGH** only if any UI/ops surface relies on the declared 5-state lifecycle for compliance or customer-facing guarantees) | Update docstring to reflect implemented lifecycle (`draft → {approved, rejected} → expired`) OR build the delivery subsystem to match declared lifecycle. §19 R.B1 covers the design-preparation ADR path. |
| D.B2 | Follow-up drafts (touches 2–4) should carry meaningful outreach content and preserve `opportunity` FK to source lead | `OutreachSequencer.evaluate` at `revenue.py:812-829` writes `body_text = f"[Follow-up #N for: <lead_title>]\n\nDraft follow-up message needed."` (literal placeholder string) **AND** omits `opportunity=` on the create call → every follow-up row would be created with `opportunity=None`. **CONFIRMED F2 orphan-write pattern at this specific writer site (code path).** Also omits `subject_line=` → follow-ups always have empty subjects. **Runtime blast radius: ZERO** — per D.B7 confirmation below, `evaluate` has no invoker; this code path never executes at runtime. Repo-wide F2 sweep across other create sites remains CANDIDATE (S1399 §4 F2 lens). | **HIGH (code) / ZERO (runtime blast radius bounded by D.B7)** | §19 R.B2 covers follow-up composition subsystem design. Two forks depending on T.B5 disposition: (i) if `evaluate` gets wired to a beat task → fix the writer site (pass `opportunity=parent.opportunity`; either invoke LLM composition or explicitly document the placeholder pattern as intentional); (ii) if `evaluate` gets deleted as dead code → this drift is closed by removal + narrow the sequencer's declared cadence to Touch 1 only. |
| D.B3 | S1274 §2.4 line 293 "Revenue → Inbox MISSING; outreach outbound channel is UNKNOWN" | **CONFIRMED + REFINED.** The missing wire is not just Inbox — the *entire outbound channel is missing.* No provider SDK imports, no `EMAIL_BACKEND`, no send call sites in mainline. | **MEDIUM** (S1274 wording accuracy, not runtime severity — runtime severity is CONFIRMED HIGH per F.B1) | **Anchor-update IMMEDIATELY at S1274 §2.4 line 293** (per Rigby SIGN cycle 2 Q7 lean: truth correction, not synthesis-deferral; do not wait for S1499 xx99). Change wording from "Revenue → Inbox MISSING" to "Revenue → any outbound channel MISSING" with backref note that S1402 confirms the stronger claim. |
| D.B4 | Any observability of send success/failure/bounce | `OutreachDraft` model has no `sent_at`, `replied_at`, `bounced_at`, `provider_id`, `provider_response_json`, `delivery_status` fields. Even if a send were built, no telemetry surface would capture the result. | MEDIUM | Design-preparation: add send-side observability fields at model level *before* wiring a provider. §19 R.B1 sub-question. |
| D.B5 | F1 provenance-filter drift lens (S1399 §4 F1 methodology) | `OpportunityDraftGenerator.select_candidate_queryset` filters by `match_score`, `potential_revenue`, `created_at`; **no filter on `source` or `metadata['spider_source']`.** Category A S1401 §14 D8 CANDIDATE HIGH extends to Category B reader surface. | HIGH (CANDIDATE, inherited) | §19 R.B3 — reader-side provenance filter is a Group-1400-wide design-preparation ADR (Category A + B share the risk). |
| D.B6 | `OutreachSequencer.get_inbox` at `revenue.py:666-667` returns `total_sent` and `total_replied` counts to PA / UI | Both counts are perpetually 0 because nothing writes those statuses. UI/PA display "Sent: 0 / Replied: 0" as ground-truth. | LOW-MEDIUM | Either build the send subsystem (resolves at the source) OR hide/gate the fields until data exists (avoids "always 0" false-signal). |
| D.B7 | `OutreachSequencer.evaluate` trigger cadence | **CONFIRMED DEAD CODE post-Rigby ops probe + parent-Claude direct-read verification.** Evidence bundle: (a) `ops_tool.celery_task_history` 30d filter=outreach → 7 events, all `generate_outreach_drafts_daily` (zero events for any evaluate-wrapping task); (b) `PeriodicTask.filter(icontains='outreach')` → single row `generate-outreach-drafts-daily` (queue=content, enabled=true, 7 total_runs) — no evaluate wrapper; (c) parent-Claude direct read of `core/services/td_handlers_ops.py:2699-2755` → four PA tool actions expose OutreachSequencer methods (`outreach_inbox` → `get_inbox`, `outreach_approve` → `approve_draft`, `outreach_reject` → `reject_draft`, `outreach_metrics_report` → `get_metrics_report`); **zero PA tool action wraps `.evaluate`**; (d) repo-wide `repo_tool.search "OutreachSequencer().evaluate"` → 0 hits; `.evaluate(now` grep across `core/` returned only `revenue.py:366` + `revenue.py:552` which are `self.evaluate(now)` calls from *different classes* (Rigby verified — not OutreachSequencer). Follow-up materialization code path (`revenue.py:781-844`) is executable but never invoked at runtime. | **LOW (CONFIRMED dead-code, not runtime bug)** | Post-arc decision-preparation: (i) wire `evaluate` to a beat task (making the follow-up cadence actually fire, then fixing D.B2 becomes urgent); OR (ii) delete `evaluate` + narrow OutreachSequencer's declared cadence to Touch 1 only + retire declared `MAX_TOUCHES=4` / `TOUCH_DAYS=[0,3,7,14]` constants. Feeds R.B2 scope selection. |
| D.B8 | `OutreachDraft.CHANNEL_CHOICES` declares `linkedin`, `twitter`, `other` alongside `email` | All rows created on both paths hardcode `channel='email'`; no code path selects a non-email channel. LinkedIn/Twitter/other are declared but never chosen. | LOW | Either implement multi-channel selection OR trim CHANNEL_CHOICES to `[email]` until other channels have delivery paths. Post-arc design-preparation. |
| D.B9 | S1401 §14 D6 (dual-representation drift — `intelligence_engine.get_current_opportunities()`) | Does **NOT** extend to Category B. `OpportunityDraftGenerator.select_candidate_queryset` reads persistent `Opportunity.objects.filter(...)` only; no `intelligence_engine` consumption. Ruled out as verifier-loop spot-check finding. | OK | None. |

## 15. Known Technical Debt

| # | Debt item | Category | Severity | Evidence | Recommendation |
|---|---|---|---|---|---|
| T.B1 | Delivery subsystem missing entirely (composition-only pipeline) | missing_subsystem | HIGH | §14 D.B1; grep of send patterns returns 0 mainline hits | §19 R.B1 — build outbound channel; adopt event-bus stream set (§10 Q20). Design-preparation ADR post-arc close. |
| T.B2 | Follow-up drafts (touch ≥2) are literal placeholder strings AND orphan-writes | F2_confirmed_writer_site + missing_subsystem | HIGH (code) / ZERO (runtime — blast radius bounded by T.B5 dead-code) | `revenue.py:812-829` | Two forks per D.B7 disposition. If T.B5 wired → §19 R.B2 build follow-up composition subsystem OR document placeholder pattern as intentional + add explicit `is_stub` boolean field to signal intent at row level. If T.B5 deleted → T.B2 closes by removal (no code path → no orphan-write). |
| T.B3 | Provenance surface is minimal — no `generated_by`, `source_run_id`, `source_agent`, no `sent_at`/`replied_at` timestamps | provenance_debt / observability_debt | MEDIUM | §4 schema table | Add fields as part of §19 R.B1 model expansion. |
| T.B4 | F1 provenance-filter drift on Category B reader | F1_candidate (inherited from S1401 §14 D8) | HIGH (CANDIDATE) | §14 D.B5 | Group-1400-wide reader-side filter ADR (Category A + B share). Post-arc. |
| T.B5 | `OutreachSequencer.evaluate` — CONFIRMED DEAD CODE (no invoker) | dead_code_confirmed | LOW (CONFIRMED; post-arc decision required) | §14 D.B7 evidence bundle (ops probe + PeriodicTask ORM + PA tool direct read + repo-wide grep) | Post-arc decision-preparation ADR: either wire `evaluate` to a beat task (making Touch 2–4 cadence fire, elevating T.B2 to runtime severity) OR delete `evaluate` + narrow declared cadence to Touch 1 only. Feeds R.B2 scope. |
| T.B6 | `CHANNEL_CHOICES` declares LinkedIn/Twitter/Other but no code selects non-email | over-modeled_choices | LOW | §14 D.B8 | Post-arc trim OR wire multi-channel dispatch. |
| T.B7 | `get_inbox` surfaces `total_sent` / `total_replied` perpetually-0 counts | UI-visible always-0 | LOW-MEDIUM | §14 D.B6 | Hide/gate until send subsystem exists. |
| T.B8 | `OutreachSequencer` has no dedicated Celery queue; beat task routes to shared `content` queue | queue_routing_debt (matches S1401 §18 finding pattern) | LOW-MEDIUM | `core/celery.py:460` `options: {'queue': 'content'}` | **Document NOW (pre-Employee-OS)** per Rigby SIGN cycle 2 Q6 lean: note current queue routing (`content`) + absence of dedicated outreach queue; mark as "future hardening" tied to D28 / Employee OS decision if/when outbound delivery is implemented (i.e., when there's actual dispatch load to route). |
| T.B9 | Test suite covers composition path + fallback; **no test covers the missing send path or asserts that no code writes status='sent'** (which would make the current absence explicit) | test_coverage_debt | LOW | `test_outreach_generation.py` | Add a "delivery gap fence" test that asserts no `.filter(status='sent').update(...)` or `create(..., status='sent')` exists (character-level fence pattern). |

## 16. Boundary Violations

Category B boundary check — imports/reaches from Category B code into other domains' internals:

| # | Violation | Severity | Notes |
|---|---|---|---|
| B.B1 | `OpportunityDraftGenerator` imports `Opportunity` from `core.models` (Category A domain) | OK | Reading Opportunity is Category B's job; not a violation. |
| B.B2 | `OpportunityDraftGenerator` imports `LegacySpiderData` for seed creation | WEAK | `LegacySpiderData` is spider-domain; synthetic seed pattern reaches across. Design intent is clear (create pseudo-lead identity for auto-generated outreach); low risk. |
| B.B3 | `OpportunityDraftGenerator.SYSTEM_PROMPT` hard-codes per-offer envelope inside the class literal (not sourced from an `Offer` model or config table) | design_debt (not boundary) | Session 1225 flagged; if offers change, prompt must be redeployed. Documented at §15 T.B6-adjacent (offer configuration debt). |

**No HARD boundary violations found.** Category B code respects Django FK boundaries + does not reach into Category C engagement internals to write.

## 17. Duplicate or Overlapping Systems

### 17.1 Touch-1 composition path (LLM) vs Touch ≥2 composition path (stub)

**PARALLEL, NOT DUPLICATE.** Touch-1 rows are LLM-composed by `OpportunityDraftGenerator.render_email` with full envelope. Touch ≥2 rows are stub-composed by `OutreachSequencer.evaluate` with literal `"Draft follow-up message needed."`. Different composition subsystems, different quality bar, different orphan-write behavior. §14 D.B2 documents this as a debt (T.B2), not an intentional duplicate.

### 17.2 `OpportunityDraftGenerator` (touch-1 producer) vs `CampaignOrchestrator` outbound pack (S1208)

**DIFFERENT SUBSYSTEMS.** Session 1208 hardened a "campaign orchestrator outbound pack" system that is distinct from opportunity outreach (per Agent 6 finding). Not overlapping — different use cases (broadcast campaign vs 1:1 lead outreach).

### 17.3 `OutreachDraft` vs `MessageDraft` / `RigbyMessage` / inbox notification models

No dedicated grep performed in this audit; no obvious overlap surfaced. If future work adds a general Rigby-to-user messaging surface, watch for representational overlap.

## 18. Ownership Gaps

Category B specific verification against S1274 §14 finding #36 (HIGH severity, inherited via parent §11.4).

| Dimension | Verified state | Gap? |
|---|---|---|
| JobContract wiring | Grep of `core/employees/jobs.py` for `OpportunityDraftGenerator`, `OutreachSequencer`, `generate_outreach_drafts_daily` — zero mentions | **GAP CONFIRMED.** |
| Dedicated Celery queue | Beat task routes to shared `content` queue (`core/celery.py:460`); no `outreach_queue` or `revenue_queue` | **GAP CONFIRMED.** |
| Documented ownership artifact | No `docs/topics/outreach*.md`; no CODEOWNERS-style artifact; SESSION_1224/1225 handoffs record ship events but not runtime-operational ownership | **GAP CONFIRMED.** |
| Employee OS / MissionRunner integration | Neither `OpportunityDraftGenerator` nor `OutreachSequencer` inherits from MissionRunner-aware base; no `OpsRun` / `OpsRunEvent` wiring | **GAP CONFIRMED.** |

**Category B recommendation for the parent-arc ownership question:** Child E (S1405) aggregates the parent-arc runtime-owner recommendation per D28. Category B's specific input: propose a dedicated `OutreachComposerOwner` JobContract that (a) owns `generate_outreach_drafts_daily` beat + a to-be-built `dispatch_pending_outreach` beat, (b) owns the future `OUTREACH_*` event-bus stream set, (c) owns follow-up composition quality (touches 2–4 not being placeholder strings). Design-preparation input to Child E; not implementation.

## 19. Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows.

| # | Research | Uncertainty × Risk | Unblocks | Owner |
|---|---|---|---|---|
| R.B1 | **Outreach delivery subsystem design ADR (umbrella)** — resolve D.B1 (docstring vs runtime) + D.B3 (S1274 line 293 refinement) + D.B4 (send observability model expansion) + D.B6 (perpetually-0 counts) + D.B8 (channel-choice implementation) as one architectural piece. Sub-questions: (a) which channel(s) — email vs LinkedIn vs Rigby-DM vs in-app? (b) which provider — SendGrid/Postmark/SES/Resend for email? (c) model expansion (`sent_at`, `provider_id`, `provider_response_json`, `bounced_at`, `delivery_status`); (d) event-bus stream set (`OUTREACH_APPROVED`, `OUTREACH_SENT`, `OUTREACH_REPLIED`, `OUTREACH_OPENED`); (e) dispatch task shape (Celery beat sweep vs `apply_async` on approve). | HIGH × HIGH | Unblocks 100% of Category B's declared purpose. Prerequisite for R.B4 engagement ingestion. Prerequisite for meaningful S1499 xx99 "Revenue → Inbox" resolution. | Post-arc design-preparation ADR |
| R.B2 | **Follow-up composition subsystem** — resolve D.B2 (stub content + orphan-write). Sub-questions: (a) should touches 2–4 also be LLM-composed with a "follow-up envelope" system prompt referencing the parent draft? (b) should the parent draft's reply-status inform the follow-up shape (e.g., "no-reply-yet" vs "opened-but-no-reply")? (c) opportunity FK preservation on evaluate() create; (d) touch-cadence customization per opp segment. | HIGH × MEDIUM | Restores meaningful follow-up content; eliminates live F2 orphan-write pattern; enables end-to-end sequence quality measurement (post-R.B1) | Post-arc design-preparation ADR |
| R.B3 | **F1 reader-side provenance filter (Category-B-scoped for now per Rigby SIGN cycle 2 Q5)** — `OpportunityDraftGenerator.select_candidate_queryset` should be able to filter Opportunity by `source` / `metadata['spider_source']` / `metadata['created_by']`. Design a filter framework for Category B's Opportunity reader path. Elevate to Group-1400-wide only if the same "missing provenance/source filter" pattern appears in other revenue-category readers (Children C/D/E) — do not preemptively globalize. | HIGH × MEDIUM | Prevents silent quality drift from untrusted-source Opportunities into outreach. Closes an F1 CANDIDATE for Category B. | Post-arc design-preparation ADR (Category-B-scoped; elevate to Group-1400-wide only on evidence from S1403–S1405) |
| R.B4 | **`OutreachSequencer.evaluate` cadence probe** — **RESOLVED (SIGN cycle 1 executed).** Rigby ops probe + parent-Claude direct-read verification jointly confirmed: `evaluate` has no invoker at runtime (see §14 D.B7 evidence bundle). Cycle 1 fold outcome: T.B5 upgraded from `dead_code_candidate MEDIUM` → `dead_code_confirmed LOW`; T.B2 clarified as CONFIRMED writer-site with ZERO runtime blast radius; F.B4 added to §1 executive summary. Post-arc decision-preparation ADR gates the two-fork choice (wire vs delete). | RESOLVED (probe complete; decision-preparation gates disposition) | R.B2 scope depends on this — if T.B5 wired, R.B2 must design LLM-based follow-up composition envelope; if T.B5 deleted, R.B2 narrows to Touch 1 only | Complete |
| R.B5 | **Engagement ingestion path (Category C S1403 scope)** — reciprocal to R.B1. Once outreach ships, replies/clicks/opens must flow back to `EngagementEvent` writers. Currently zero writers (§9 verified). S1403 owns the full seam build-out; Category B ownership is limited to (a) emitting `OUTREACH_SENT`/`OUTREACH_REPLIED` events (b) exposing `outreach_draft` FK on EngagementEvent (already present). | HIGH × HIGH (blocked on R.B1) | Closes the feedback loop; enables Category C metrics; feeds Category E revenue attribution | Category C S1403 owns |
| R.B6 | **Prompt envelope drift + offer-configuration debt** — `SYSTEM_PROMPT` per-offer envelope lives inside `OpportunityDraftGenerator` class literal; changing offers requires redeploy. Should offers be a config-DB-driven `OutreachOffer` model? Tradeoff between "prompt hard-binding for compliance" (Session 1225 rationale) and "operator ability to iterate offers without deploy." | MEDIUM × LOW | Enables faster offer iteration | Post-arc design-preparation ADR |
| R.B7 | **Send-gap fence test** — add a repository-level test that asserts no code writes `status='sent'` or `status='replied'` until R.B1 ships. Prevents accidental partial-delivery ship that would give false-signal analytics before R.B1's model expansion lands. | LOW × MEDIUM | Guards against silent partial implementation | **Bundle with R.B1** (per Rigby SIGN cycle 2 Q9 lean: fence tests are most useful once the guard/contract is explicit; otherwise you encode current no-send behavior without a stable abstraction to test against). |

## 20. Appendix

### 20.1 Files inspected

**Load-bearing runtime files (verified at HEAD `beda00e5`):**

- `core/models_outreach.py` (125 lines, full read) — `OutreachDraft` model.
- `core/services/ops_autopilot/outreach_generation.py` (~530 lines, spot-read at lines 85–215, 292–422, 475–525) — `OpportunityDraftGenerator`.
- `core/services/ops_autopilot/revenue.py` (spot-read at lines 605–729, 781–844) — `OutreachSequencer`, `evaluate`, `approve_draft`, `reject_draft`, `get_inbox`.
- `core/celery.py` (spot-read at lines 449–479) — beat schedule entry `generate-outreach-drafts-daily`.
- `core/models_engagement.py` (spot-read at line 18 + line 55–59 for `EngagementEvent.outreach_draft` FK) — engagement-side FK schema.
- `core/services/event_bus.py` (spot-read at lines 21–31 for `EventStream` enum).

**Verifier-loop negative-evidence checks (parent-Claude direct greps at HEAD `beda00e5`):**

- `send_outreach|dispatch_outreach|deliver_outreach|outreach\.send|outreach_send` across the repo → 0 mainline hits (archive/ + external-project-docs/ hits do not count).
- `sendgrid|postmark|mailgun|smtplib|EMAIL_BACKEND` in mainline (excluding `.venv/`, `archive/`, `external-project-docs/`, `ai_core/`) → 0 mainline hits.
- `EngagementEvent\.objects\.create|EngagementEvent\(` across the repo → 1 hit (the class definition itself at `core/models_engagement.py:18`), 0 writer sites.
- `apply_async` in `core/services/ops_autopilot/` → 3 hits (all `verify_autopilot_action.apply_async`, none related to outreach).

**Prior-research inheritance (read for cite/inherit):**

- `docs/research/domains/revenue/1400_revenue_domain_scoping.md` — §10.2 Category B evidence surface + §11.4 15 inherited findings + §12.1 Category B F.iii questions.
- `docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md` — §9.1 integration map + §14 D6 dual-representation drift + §19 R1 umbrella.
- `docs/research/platform_architecture_inventory.md` §3.32 + §4.9 (S1273 v2 Revenue row).
- `docs/research/platform/cross_domain_integration_audit.md` §2.4 line 293 (S1274).

### 20.2 Sub-agent evidence provenance (§13 6-parallel-Explore sweep)

Six parallel Explore agents produced initial evidence per playbook §13. Parent-Claude verifier-loop pre-SIGN caught **two NEW load-bearing drifts** before Rigby routing:

- **NEW D.B2 promotion** — Agent 6 (via SESSION_1225 quote) named "OutreachSequencer.evaluate() handles touches 2-4 with hardcoded text." Parent-Claude direct read of `revenue.py:812-829` confirmed AND ELEVATED: not just hardcoded, but the literal string `"Draft follow-up message needed."` AND the create call omits `opportunity=` → live F2 orphan-write pattern. Agent 6's statement was accurate but understated the finding shape.
- **NEW D.B1 promotion** — Agent 4 named "no outbound channel wired." Parent-Claude direct read of `models_outreach.py:10` docstring caught the *docstring-vs-runtime* framing: the model itself declares a five-state lifecycle that includes `sent` and `replied`, but the runtime state machine only implements three states. Agent 4's negative claim was correct but framed as "channel missing"; parent-Claude reframed as "declared lifecycle vs implemented lifecycle divergence" — same evidence, sharper claim.

**Verifier-loop cost:** ~5 minutes of parent-Claude direct reads; **outcome:** two load-bearing findings sharpened before Rigby SIGN — matches S1401 methodology inheritance (§9.1 of S1401 documented the pattern of "corrected 5 sub-agent claims BEFORE Rigby SIGN").

### 20.5 SIGN cycle 1 fold provenance

**Rigby SIGN cycle 1 verdict (fresh isolation pin `pa-4a0a28edcb7a45ec` at 2026-07-01T20:37Z):** SIGN-with-edits, High confidence, 2 must-fix + 3 nice-to-have. Seed message truncated at storage layer mid-Must-fix #2; parent-Claude reconstructed the fold pass from (a) verbatim Must-fix #1 content (F.B2 CANDIDATE vs CONFIRMED classification drift, cited audit lines 20, 36-37, 42-44), (b) inferred Must-fix #2 direction (F.B1 delivery-path severity: audit incorrectly labeled CANDIDATE HIGH when grep-negative evidence is complete → should be CONFIRMED HIGH), (c) D.B7 dead-code confirmation via Rigby's ops probe (celery_task_history + PeriodicTask ORM) + parent-Claude direct read (td_handlers_ops.py:2699-2755 + repo-wide grep).

**Cycle 1 folds applied (this document):**

- **Must-fix #1 fold** — F.B2 classification split: **CONFIRMED writer-site** at `revenue.py:812-829` (specific code path is deterministic + directly readable) + **CANDIDATE repo-wide** (other create sites not swept in this audit). Audit lines 20 (load-bearing framing), 36-37 (F.B2 in Exec Summary), 42-44 (inherited findings), §14 D.B2 (Known Drift row), §15 T.B2 (Debt row) all updated.
- **Must-fix #2 fold (inferred)** — F.B1 delivery-path elevated from "CANDIDATE HIGH per S1399 §4 F4 methodology" → **CONFIRMED HIGH** — grep-negative evidence is complete at HEAD `beda00e5`; S1399 §4 F4 CANDIDATE-elevation not needed. Audit line 36 (F.B1 in Exec Summary) + inherited findings status (S1274 §2.4 line 293) updated.
- **D.B7 dead-code upgrade fold** — F.B4 NEW load-bearing finding added to §1 Executive Summary; §14 D.B7 severity re-verdicted MEDIUM UNKNOWN → LOW CONFIRMED with full evidence bundle; §15 T.B5 upgraded `dead_code_candidate` → `dead_code_confirmed`; §15 T.B2 blast-radius clarified ZERO at runtime + two-fork disposition documented; §7 Flow γ prefix note added ("DEAD CODE per §14 D.B7"); §13 Architecture Maturity delivery-half evidence rewritten; §19 R.B4 marked RESOLVED (probe complete).

**Rigby SIGN cycle 2 verdict:** **SIGN-clean (post-folds), High confidence** (arc pin reply 2026-07-01).

**Cycle 2 fold outcomes (5 Q-answer folds applied to this document):**

- **Q3 fold** — D.B1 severity downgraded HIGH → MEDIUM. Rigby rationale: "Docstring-vs-runtime is misleading but not a runtime failure; it becomes HIGH only if any UI/ops process relies on the stated 5-state lifecycle for compliance or customer-facing guarantees."
- **Q5 fold** — R.B3 F1 reader-side filter narrowed from Group-1400-wide → Category-B-scoped. Elevate to Group-1400-wide only if same pattern surfaces in Children C/D/E.
- **Q6 fold** — T.B8 recommendation changed from "post-arc, depends on D28" → "document NOW (pre-Employee-OS)". Note current queue routing + gap + tie to future hardening.
- **Q7 fold** — D.B3 anchor-update timing changed from "recommended" → "IMMEDIATELY at S1274" (truth correction, not synthesis; don't wait for S1499 xx99).
- **Q9 fold** — R.B7 send-gap fence test disposition changed from "immediate pre-R.B1 guard" → "bundle with R.B1". Rigby rationale: fence tests are most useful once the guard/contract is explicit.

**Cycle 2 3 nice-to-haves (recorded for post-arc pickup, not blocking merge):**

- **NH-1:** Add provenance fields to `OutreachDraft` (`generated_by`, `source_run_id`, `sent_at`, `replied_at`) or explicitly document why they're absent; today the model reads like a full lifecycle system, but the stored data can't support lifecycle analytics or audits. Feeds R.B1 model expansion scope.
- **NH-2:** Document (and/or enforce) the "composition-only" contract in code: rename UI/API surfaces from "outreach delivery" to "outreach drafts," and add an explicit "no outbound channel implemented" banner to prevent operators assuming "approved" implies sent. Also elevates D.B1 severity discipline — if the banner is added, the docstring-vs-runtime drift becomes operationally visible + safe.
- **NH-3:** Add a lightweight integrity check/report: daily count of `approved` drafts older than X days + oldest-age, so the backlog/expiry behavior is visible; this prevents silent accumulation and makes the "no delivery path" reality operationally obvious.

**Cycle 2 SIGN pin retention:** `pa-4a0a28edcb7a45ec` — retire post-PR-merge per playbook §15 fresh isolation pin retirement rule.

### 20.3 Open questions for Rigby SIGN cycle 1

Nine canonical questions per playbook §15 SIGN stage table:

1. **Evidence sufficiency:** are §9 integration-map verdicts (CONFIRMED / CONFIRMED+REFINED / RESOLVED/negative / PARKED / MISSING) grounded in direct reads at HEAD `beda00e5`? Flag any that would benefit from Rigby-side grep-expansion (S1401 pattern: dual-representation grew 1→5 sites during SIGN cycle 1).
2. **F.B2 orphan-write CONFIRMATION:** does Rigby agree that omitting `opportunity=` on `revenue.py:812-829` is a live F2 orphan-write pattern per S1399 §4 F2 methodology? Any grep expansion of the pattern to other touch-numbered create call sites?
3. **F.B1 docstring-vs-runtime severity:** is HIGH severity correct for D.B1, or should this drop to MEDIUM given the docstring is descriptive not enforcing?
4. **D.B7 evaluate cadence:** can Rigby probe `CeleryTaskEvent` history + `PeriodicTask` ORM for any task wrapping `OutreachSequencer.evaluate`? If not wired, T.B2 (follow-up stubs + orphans) never fires at runtime — a significant reduction in T.B2 blast radius.
5. **R.B3 F1 reader-side filter:** should this be Group-1400-wide (spanning Category A + B) or Category-B-scoped? S1401 §19 R1 umbrella framing implies wide.
6. **T.B8 dedicated outreach queue:** should this be documented pre-Employee-OS or wait for ownership decision (D28)? Rigby's lean on staging.
7. **Wording for D.B3 anchor-update:** proposed change is "Revenue → Inbox MISSING" → "Revenue → any outbound channel MISSING." Rigby's lean on staging (S1274 anchor-update immediately vs at S1499 xx99).
8. **§14 D.B9 spot-check confidence:** does Rigby want to broaden the check for `intelligence_engine.get_current_opportunities()` consumption beyond `OpportunityDraftGenerator` to full Category B code surface (evaluate, get_inbox, approve_draft) as a defensive verifier-loop expansion?
9. **§19 R.B7 send-gap fence test:** immediate (pre-R.B1 guard) vs deferred (with R.B1 as one package)? Prevention-value of the fence test is highest before R.B1 ships.

### 20.4 Frontmatter provenance

- Head SHA: `beda00e5` (post-S1401 merge, verified `git log --oneline -5`).
- Branch: `docs/session-1402-revenue-outreach-composition-delivery` (off `main`).
- Chris ratifications (D32 sequential + D33 arc pin retain) via arc pin `pa-34d43795e1b24bd3` 2026-07-01 ("agree all").
- SIGN pin: fresh mint per playbook §15 stage table (S1402 SIGN pin at mid-session cycle 1).
- Playbook version: current at `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` (§11.2 20-section template + §13 6-parallel-Explore + §14 evidence rules + §15 full-SIGN stage table + §16 commit policy).
- Sibling prior: `docs/research/domains/revenue/1401_revenue_opportunity_discovery_scoring_audit.md` (Category A ↔ Category B seam evidence at §9.1).
