---
title: "Real User Readiness Campaign — parent engineering program"
status: draft
authority: draft-planning  # NOT ratified. Becomes 'constitutional' only after Chris D-verdict + Rigby SIGN close per §13.
session_added: 2741
last_updated: 2026-07-10
program_id: RUR
parent_workspace: "Real User Readiness Campaign"
parent_workspace_id: 638e9e90-47b4-4bd4-a872-bf16181cf3b5
research_predecessor: session_transcript_only  # S2740 assessment was produced as an in-session response during S2746; not persisted as a separate repo file. Reconstruction path: session handoff for S2746 + this doc's §1 + §11.
framing: gated-alpha (Rigby-framed, Chris-accepted at S2741 open)
constraint: planning-only until Chris ratifies Wave 1 mission opens
implementation_arc_prefix: I-03xx  # first child arc opens as I-0300
sign_history:
  - session: 2741
    reviewer: rigby
    verdict: SIGN-with-amendments (7 amendments applied in this rev; new divergence added to §11 per SIGN)
---

# Real User Readiness Campaign

> **DRAFT — planning-only until Chris ratifies.** Authored S2741 as the proposed parent campaign. Rigby SIGN-with-amendments landed the same session and the amendments were folded into this revision. This becomes the constitutional reference for the Real User Readiness program only after Chris D-verdict on §12 open questions.
>
> **This document does not implement anything.** It defines the program, its exit criteria, its dependency graph, its verification philosophy, its alpha bar, and its rules of engagement. Missions are proposed here; they open elsewhere. Sub-campaigns cross-reference this document once ratified.

---

## §1. Executive Summary

### Why this campaign exists

The Donkey Betz platform has completed a multi-quarter research phase (Sessions ~1268 through 2740) that established the architectural ground truth: what agents exist, how the PA loop runs, how spiders ingest, how workspaces scope, how Employee OS orchestrates missions, how the docs cascade preserves knowledge, and how governance works. The research artifacts under `docs/research/` — architecture inventory, capability graph, playbook, cross-domain integration audit, and per-domain arcs (auth, api, pa, frontend, observability, etc.) — collectively answer the question **"what does the platform do?"**

The next phase answers a different question:

> **"What engineering work must be completed before real users can safely trust and use the platform?"**

The two questions have almost no overlap. The first is descriptive; the second is prescriptive. The first accumulated evidence about existing behavior; the second demands changes to behavior. This campaign is the bridge.

### The transition

- **Research phase** (~S1268–S2740): 12+ domain arcs closed, engineering playbook v0.4.1 ratified with 196 rules across 11 chapters, capability graph maintained, cross-domain integration audit complete. Substrate: `docs/research/`, `docs/research/domains/<slug>/`, `docs/research/platform/`, `docs/research/implementation/` (I-0100 observability spine + I-0200 RAG corpus already closed).
- **Engineering phase** (S2741+): the Real User Readiness program. Substrate: `docs/research/implementation/real_user_readiness/` + child implementation arcs (I-0300, I-0400, ...) as they spawn.

### The overall mission

Bring the platform to a bar where a small allowlisted alpha (target: single-digit concurrent users, single-digit workspaces) can trust it. Specifically, close the invariant gaps that Rigby's S2740 framing identifies as trust-destroying: tenant isolation, async convergence, fail-loud discipline, idempotent side effects, WebSocket auth, cost caps, and a validated golden path.

Rigby's framing pushback at S2740 §F is **accepted**: this program prepares the platform for a **gated alpha**, not unrestricted self-service. Self-serve is a distinct future program; conflating the two would mis-scope the work and produce a demo-shaped result instead of an invariants-shaped result.

### Research predecessor

The S2740 assessment (produced during S2746 as a planning-only response to Chris's Real User Readiness Campaign brief) established:
- 5 readiness gate categories (§A)
- Top-10 ranked risk inventory (§B, formula: `Impact × Likelihood × Blast / Effort`)
- Candidate campaign list (§C, 7-8 campaigns)
- Async pipeline audit table (§D, 12 pipelines cross-referenced)
- Non-obvious risks Rigby surfaced from operational memory (§E)
- Framing pushback toward gated alpha (§F, accepted)
- Mission sequencing proposal in waves (§6, Claude-authored)
- Vertical slice validation shape (§7)
- 5 open questions requiring Chris D-verdict (§8)

The S2740 collision surfaced convergence on Risks #1 + #2 (auth boundaries + silent async failure, tied at score 33) and material divergence on effort estimates + prerequisite graph. This CAMPAIGN document reconciles both perspectives; disagreements that survived reconciliation are recorded in §11 (Pressure Testing) so implementation missions inherit them explicitly.

---

## §2. Definition of Ready (readiness gates, grounded in repo evidence)

"Ready for real users" means: **an allowlisted alpha cohort can concurrently exercise one primary user journey end-to-end without cross-tenant leakage, silent async failure, runaway compute cost, or supportability collapse — with an operator able to answer "what happened to request X" from durable telemetry in under two minutes.**

Each gate below has a pass condition, a user-visible fail signature, and repo-evidence anchors that established the gap.

### G1 — Tenant Isolation (HARD BLOCKER)

**Pass condition:** every user-visible queryset is scoped by `(user_id, workspace_id)` OR has an explicit, audited global-superuser pathway. Object-level permissions exist and are exercised for Deliverable, Initiative, ChatConversation, AgentExecution, and Document models. Async tasks reject payloads without workspace scope and re-verify ownership at execution time against the committed DB row (not the LLM-supplied payload).

**Fail signatures:**
- "I see other people's deliverables in my workspace"
- "A run I didn't start appeared in my execution list"
- "The system took an action on my behalf using someone else's context"

**Repo evidence for the gap:**
- 26 `AllowAny` endpoints across 8 files (`grep permission_classes = [AllowAny]`), including `intelligence/views.py:179` `ActionPlanPersistenceView` which reads user action plans from filesystem globs with no auth
- Self-labeled acknowledgment in `core/views_content_learning.py:30` comment: *"Public for debugging, change to IsAuthenticated in production"* (appears 4× in that file)
- `ai_core/api/autonomous_system_api.py` — 4 `AllowAny` endpoints on a "revenue system" (currently mock; dangerous when wired live)
- No `Meta.permissions` custom classes detected via grep on the top 5 user-owned models; object-level authz enforcement is at best implicit via view-level `queryset` scoping
- No systematic evidence that Celery task handlers re-verify `workspace_id` against DB row ownership before mutation

### G2 — Async Convergence (HARD BLOCKER)

**Pass condition:** every Celery task has a durable state machine `PENDING → RUNNING → SUCCEEDED | FAILED | CANCELLED` with timestamps. `AgentExecution.status` cannot sit `in_progress` past a wall-clock timeout without a runtime watchdog emitting a failure event. No task returns success without post-condition verification (i.e., no "SUCCEEDED with empty output" — Rigby's S2740 §E1 "Succeeded but wrong" class).

**Fail signatures:**
- "It says generating forever" (UI stuck on `in_progress`)
- "Nothing happened but the button said success"
- "The system reports success but the output is empty / low-signal / wrong"

**Repo evidence for the gap:**
- `core/management/commands/cleanup_stuck_executions.py` exists as a manual dev-ops command (origin S866). Its existence proves `AgentExecution` rows get stuck `in_progress` with no auto-detection at runtime; UI shows "Running" indefinitely until an operator runs this command.
- 748 `except` clauses across 15 `core/tasks*.py` files. Only ~29 references to `OpsRunEvent.objects.create` in the same codebase (Rigby's S2740 §A2 telemetry gap corroboration).
- Rigby S2740 §A2 evidence anchor: `ops_tool.slo_status` (7-day window) shows Celery task success at 26,009/26,010 (99.9962%) with **only 1 recorded IntegrityError**. Given the 748 except-clause density, the "healthy SLO" hypothesis is dominated by the "swallowed failure" hypothesis until proven otherwise.

### G3 — Fail-Loud (HARD BLOCKER)

**Pass condition:** every task failure produces (a) a durable `OpsRunEvent`-class row with `reason_code`, `human_message`, and `trace_id`; (b) a user-visible surface via a canonical error component (`GlobalAlertBanner`, `Toast`, or per-view `ErrorState`); (c) is retryable from UI where the underlying task is idempotent.

**Fail signatures:**
- "It just disappeared" (task exception logged internally, no user signal)
- "I got a raw JSON stacktrace" (developer error shown as-is)
- "I don't know why it failed and I can't retry"

**Repo evidence for the gap:**
- OpsRunEvent as structured status is concentrated in Employee OS and Rigby delegation surfaces (~29 refs), not universal across user-triggered Celery tasks
- Memory rule `feedback_auto_followup_false_suppresses_banner.md` documents a known failure mode: when `auto_followup=False` on an agent tool call, no `AgentFollowupSubscription` arms and the user sees no completion alert. This is a substrate-level fail-loud gap — not per-task.
- Frontend has 5 error/alert components (`ErrorState`, `GlobalAlertBanner`, `TodayErrorsCard`, `Toast`, `AlertsPage`) — substrate exists but per-flow coverage is unknown and Rigby's S2740 §D audit table marks 8 of 12 major pipelines as "user-visible status: No" or "Sometimes"

### G4 — Idempotency (HARD BLOCKER for external users)

**Pass condition:** every side-effect task (deliverable create, publish, outreach send, spend, agent dispatch) has an idempotency key column or apply-once guard. Retries — Celery-automatic or user-initiated — are safe by construction.

**Fail signatures:**
- Duplicate deliverables from a single user click
- Double-charged / double-billed / double-outreach
- Retry storms that amplify cost (Rigby S2740 §E7 "thundering herd")

**Repo evidence for the gap:**
- No universal `idempotency_key` column present on the top-5 side-effect models (verified via grep; no matches on `idempotency_key = models` in `core/models*.py`)
- Rigby's operational memory (§E7) flags this as a known amplification vector on transient provider outages

### G5 — Cost Safety (HARD BLOCKER for external users at scale)

**Pass condition:** per-workspace budget caps enforced at the task-dispatch layer (not just monitor). High-cost flows require confirmation. Runaway detection kills tasks before the cap blows.

**Fail signatures:**
- Silent — but bankruptcy is the fail signature. Rigby's S2740 §A3 anchor: cost enforcement is currently monitor-only per closeout deliverable `b826b744-a18f-4f59-8442-5bb088fec9fc`.

**Repo evidence for the state:**
- `cost_thresholds` management command (S2744) exposes the config surface but only for the platform-wide default; no per-workspace cap column exists on `SystemConfiguration`
- `cost_threshold_monitor` service + `check_cost_thresholds` beat task (S2743) implements the monitor-only path
- Observation period opened 2026-07-10 07:35 MDT at `month: $500 / monitor` — data accumulating, but no enforcement wired

### G6 — Realtime Auth (HARD BLOCKER)

**Pass condition:** every WebSocket consumer authenticates in `connect()`. Group names include workspace scope. Message handlers reject cross-workspace sends. Anonymous connects close with `4401`.

**Fail signatures:**
- "I got someone else's notifications"
- "WS drops silently and I don't know why"
- "The system responded to a message I didn't send"

**Repo evidence for the gap:**
- 17 consumer files (`ls **/consumers*.py`); only 9 reference `scope["user"]` or `is_authenticated`
- Concrete evidence: `sports_betting/consumers.py:29` accepts WebSocket with zero auth — `channel_layer.group_add` + `self.accept()` and nothing else
- Content consumers (`content/consumers.py:26, 417`) DO enforce; coverage is uneven, not absent

### G7 — Observability (ENABLER; soft blocker until support scales)

**Pass condition:** `trace_id` propagated from HTTP request → Celery task → deliverable / notification. Operator can answer "what happened to request X" in under 2 minutes from durable telemetry alone.

**Repo evidence for the state:**
- Multiple partial telemetry substrates exist (`LLMCallEvent`, `CeleryTaskEvent`, `OpsRun`/`OpsRunEvent`, `HAIDispatchLog` from S2737)
- None compose into a unified per-request trace view
- The observability spine implementation arc (I-0100) closed at S2707 with partial coverage — see `docs/research/implementation/observability_spine_mission_evidence_substrate/I-010099_observability_spine_implementation_close.md`

### G8 — Supportable Errors (ENABLER)

**Pass condition:** every user-facing error carries a `support_code` the user can quote. Operator can trace `support_code → trace_id → full context`.

**Repo evidence for the gap:**
- No `support_code` field found across error surfaces via grep
- Rigby's S2740 §E10 "supportability gap": no user-readable error/report artifact for ticket resolution

---

**Gate priority contract (two layers, per Rigby SIGN):**

- **Alpha-open gates:** G1–G6 must be fully verified. G7 + G8 may be partial if operator-side triage is documented and manageable at cohort size.
- **Campaign-close gates:** G1–G8 fully verified. E5 + E9 (which require `support_code` + `trace_id` end-to-end) map to G7 + G8, so campaign close cannot skip them.

The alpha-open vs campaign-close split resolves the S2740 §11 Divergence 6 contradiction (see §11) between "G7/G8 are enablers" and "E5/E9 are hard exit criteria." Both are true — at different gates.

---

## §3. Definition of Done (measurable exit criteria)

The campaign closes when every criterion below is verifiably met.

### Exit Criteria (numbered for cross-reference from child arcs)

Each exit criterion below carries an explicit **probe** — the named test, tool, or measurement that produces the pass/fail signal. This addresses Rigby SIGN §2 measurability audit: no criterion is testable-in-principle; each is testable with a specific artifact.

- **E1 — No cross-tenant data exposure.**
  - **Probe:** `tests/security/test_cross_tenant_regression.py` (new suite, ships with RUR-C1). Exercises a pinned snapshot list of user-facing HTTP endpoints, all WebSocket consumers, and the top 10 Celery task boundaries as user-A attempting to read/write user-B's rows.
  - **Endpoint scope:** snapshot list pinned in `tests/security/endpoints_covered.txt` at RUR-C1 mission open. Auto-derived from `grep permission_classes` output + manual curation for view-only endpoints without explicit decls; frozen at mission close.
  - **Pass threshold:** zero cross-user reads/writes succeed. Suite runs in CI; PR merge blocked on any failure.

- **E2 — Object-level authorization verified.**
  - **Probe:** every model in the enumerated set (below) has either a `Meta.permissions` custom class exercised by E1's suite, OR view-level scoping with a specific per-model cross-user leakage test in `tests/security/test_object_level_authz.py`.
  - **Enumerated model set:** `Deliverable`, `Initiative`, `ChatConversation`, `AgentExecution`, `Document`. Additions require RUR-C1 mission-open decision.
  - **Pass threshold:** every model in the set has ≥1 leakage test attributed to it in the test suite. CI-blocking.

- **E3 — Async lifecycle deterministic.**
  - **Probe:** production observation window ≥ 7 days shows zero `AgentExecution.status = 'in_progress'` rows with `updated_at` older than the documented per-task-family timeout (default 15min, overridable per task).
  - **Companion probe:** `cleanup_stuck_executions` runs daily in staging; must be a no-op for 7 consecutive days. Command retained (per Rigby SIGN §2 — deletion is not measurable) but must have a comment linking to RUR-C3 completion.
  - **Pass threshold:** both probes green for 7d.

- **E4 — No silent failures on covered surfaces.**
  - **Probe:** `tests/reliability/test_fail_loud_coverage.py` iterates the pinned top-20-by-volume task list (snapshot at RUR-C2 mission open from `ops_tool.overview` 30-day window) and verifies each task's decorator emits an `OpsRunEvent` on both success and failure paths.
  - **Chaos probe:** `tests/chaos/test_worker_kill_visibility.py` kills a Celery worker mid-task and asserts a user-visible FAILED state materializes via API or WS.
  - **Pass threshold:** unit test 100% pass; chaos test surfaces failed state within 30s of worker kill.

- **E5 — User-visible support artifacts.**
  - **Probe:** `tests/frontend/test_support_code_coverage.tsx` exercises each enumerated user-facing error surface. Surface set: WebSocket close codes (4401/4403/4500), REST 4xx/5xx JSON responses, async task failure banners, permission denial modals. Each surface must render a `support_code` prop.
  - **Operator lookup path:** documented in `docs/runbooks/support_code_lookup.md` (created at RUR-C2 close) with sample invocation.
  - **Pass threshold:** every enumerated surface renders a `support_code`; operator can quote a `support_code` and retrieve trace via documented path.

- **E6 — WebSocket authentication complete.**
  - **Probe:** `tests/security/test_ws_auth_coverage.py` iterates every consumer class (`ls **/consumers*.py` snapshot at RUR-C5 open); anonymous connect must close `4401`; cross-workspace group send must be rejected.
  - **Coverage denominator:** all 17 currently-known consumer files. Regression test compares consumer file list at test-time vs snapshot; new consumers added later automatically enter the test.
  - **Pass threshold:** all consumers reject anonymous; all group names contain workspace scope; regression suite CI-blocking.

- **E7 — Idempotent side effects.**
  - **Probe:** `tests/reliability/test_idempotency_key.py` fires the same task with the same `idempotency_key` three times concurrently for each of the pinned top-5 side-effect tasks; asserts exactly one row created.
  - **Task set:** deliverable create, deliverable publish, outreach send, spend record, agent dispatch. Pinned at RUR-C4 open.
  - **Pass threshold:** 3× concurrent fire → 1 row for each of 5 tasks.

- **E8 — Cost enforcement active.**
  - **Probe:** per-workspace cost cap enforcement fires at task-dispatch layer. Invariant framing (per Rigby SIGN §2 note — do not over-specify data model): "per-workspace stored cap exists AND enforcement fires at dispatch AND user-visible reason surfaces on breach."
  - **Runtime test:** synthetic workspace with $1 cap; trigger LLM-call-generating flow; assert hard-stop before second call; assert user-visible `support_code` returned.
  - **Pass threshold:** synthetic runaway hard-stopped; observation-period gate in §12 Q5 met numerically.

- **E9 — End-to-end traceability.**
  - **Probe:** `tests/observability/test_trace_id_propagation.py` fires an HTTP request with an injected `trace_id`, follows through Celery task → Deliverable → notification, asserts `trace_id` present at every hop.
  - **Operator lookup:** named tool/command exists — `python manage.py trace_lookup <support_code>` returns full trace context in <10s wall-clock.
  - **Pass threshold:** trace_id propagates through all documented hops; lookup returns context.

- **E10 — Golden Path validated.**
  - **Probe:** `tests/e2e/test_alpha_golden_path.py` (load test harness). 10 concurrent simulated users exercise the chosen golden path (§12 Q4 determines which); each iteration runs full path end-to-end.
  - **Chaos overlay:** during load exercise, chaos-inject one worker kill, one WS drop, one cost-cap breach. All must surface as user-visible failures within SLA.
  - **Pass threshold:** zero cross-tenant leakage across all users; zero `in_progress` executions older than 15min; cost caps enforce on synthetic runaway; all chaos injections surface within 30s.

- **E11 — Alpha readiness ratified.**
  - **Probe:** ratification record produced at `docs/research/implementation/RATIFICATION_YYYY-MM-DD_real_user_readiness_alpha.md` per Playbook cadence; workspace deliverable status flipped `completed`; Chris D-verdict recorded on campaign closeout.
  - **Pass threshold:** all three artifacts exist and are linked from this doc's §13.

**Exit contract:** the campaign is done when E1–E11 all pass their named probes. Nothing about "feature complete" or "looks correct" enters exit criteria; only invariants + verifications with named probes.

**Invariant vs solution-shape discipline (per Rigby SIGN §1 secondary note):** where possible, criteria specify the invariant, not the data model / decorator / class-name choice. Sub-campaigns retain design authority over solution shape as long as the invariant is met. E4/E5 mention specific artifacts (`OpsRunEvent`, `support_code`) because they are already established substrate the campaign extends, not new decisions being forced by this doc.

---

## §4. Campaign Map (approved mission slots)

Seven engineering campaigns, refined from the S2740 §C candidate list. Each becomes its own implementation arc (I-03xx sibling under `docs/research/implementation/`) when opened.

| ID | Campaign | Scope | S2740 origin | Prereq | Effort | Arc slot |
|---|---|---|---|---|---|---|
| **RUR-C1** | Tenant Boundary Lockdown | Fix 26 `AllowAny` endpoints (audit each: legit-public vs. gap); add object-level perms on top-5 user-owned models; add async task-boundary scoping check | S2740 §C1 | none | L (multi-mission likely) | I-0300 (parent) with sub-arcs I-0301–I-0303 possible |
| **RUR-C2** | Async State + Fail-Loud + Traceability | Canonical `OpsRunEvent` failure emission via decorator on top-20 volume tasks; standardize `PENDING → RUNNING → SUCCEEDED\|FAILED\|CANCELLED`; propagate `support_code + reason_code + trace_id` to UI. **Explicit scope EXCLUSION:** SRE dashboards, infra metrics, and platform-wide observability outside user-facing work. Traceability here means "user-visible failure + support_code lookup," NOT full-platform observability. | S2740 §C2 + Rigby SIGN §4 rename | parallel-possible pending Chris D-verdict (see §11 Div 1) | M-L | I-0400 |
| **RUR-C3** | Execution Convergence | Wall-clock watchdog on AgentExecution + OpsRun; auto-FAIL after N min; cancellation propagation. Retires `cleanup_stuck_executions` | S2740 §C3 | RUR-C2 (needs state machine standardized) | M | I-0500 |
| **RUR-C4** | Idempotency Hardening | `idempotency_key` on top-5 side-effect models; apply-once guards on external calls | S2740 §C4 | RUR-C2 (retries observable via fail-loud substrate) | M | I-0600 |
| **RUR-C5** | Channels Auth Hardening | `AuthMiddlewareStack` verified on every consumer; workspace scope in group names; reject anon connects | S2740 §C5 | RUR-C1 partial (need auth surface audit output) | M | I-0700 |
| **RUR-C6** | Cost Enforcement | Per-workspace budget cap on SystemConfiguration; enforce at task dispatch; observation-period complete (S2735 §17 gate) | S2740 §C6 | RUR-C2 (needs failure surface for user-visible cap breach reason) | L | I-0800 |
| **RUR-C7** | Golden Path Alpha (validator) | ONE flawless user journey end-to-end; allowlist-gated; instrumented success/failure funnel. This is the *vertical slice that proves the campaign*, not another feature. | S2740 §C7 + Rigby §F framing accepted | RUR-C1 + RUR-C2 minimum | M | I-0900 |

**S2740 candidate list changes at reconciliation:**
- **Kept:** all seven from S2740 §C
- **Rejected:** "Observability as separate campaign" (folded into RUR-C2 — fail-loud IS the user-facing observability layer)
- **Deferred out of alpha scope:** "Backpressure + user-visible progress UI" (S2740 §C8 candidate; Rigby ranked it #8, real-user risk but not top-tier for allowlist alpha with cohort-size operator triage)

---

## §5. Campaign Dependency Graph

### Wave structure

```
Wave 1 (parallel-possible pending Chris D-verdict on §11 Div 1):
  ┌─────────────────────────────────────┐
  │ RUR-C1  Tenant Boundary Lockdown    │──┐
  │ RUR-C2  Async State + Fail-Loud +   │──┤   ← parallel-possible; NOT parallel-default.
  │         Traceability                │  │   ← Chris D-verdict resolves parallel vs serial.
  └─────────────────────────────────────┘  │
                                            │
Wave 2 (depends on Wave 1):                 ▼
  ┌─────────────────────────────────────┐
  │ RUR-C3  Execution Convergence       │◄─── needs RUR-C2 state machine
  │ RUR-C5  Channels Auth Hardening     │◄─── needs RUR-C1 audit output
  └─────────────────────────────────────┘
                                            │
Wave 3 (depends on Wave 2):                 ▼
  ┌─────────────────────────────────────┐
  │ RUR-C4  Idempotency Hardening       │◄─── needs RUR-C2 fail-loud (observable retries)
  │ RUR-C6  Cost Enforcement            │◄─── needs RUR-C2 failure surface
  └─────────────────────────────────────┘
                                            │
Wave 4 (validation):                        ▼
  ┌─────────────────────────────────────┐
  │ RUR-C7  Golden Path Alpha           │◄─── proves Waves 1-3, does NOT replace them
  └─────────────────────────────────────┘
```

### Dependency reasoning

- **RUR-C1 and RUR-C2: parallel-possible pending D-verdict.** Claude challenged Rigby's S2740 sequencing that placed C1 as prereq for C2 (reasoning: fail-loud can be *scoped-by-design*). Rigby SIGN at S2741 flagged that the previous draft biased toward parallel before Chris ruled. This draft is corrected: neither default is baked in. Div 1 in §11 records both positions; Chris D-verdict at Wave 1 open resolves.
- **RUR-C3 blocked by RUR-C2** because the convergence watchdog needs a canonical state machine to detect "stuck" against. Without C2's state machine, "stuck" is ambiguous.
- **RUR-C5 blocked by RUR-C1** because the WebSocket auth audit consumes the AllowAny audit output (which endpoints are legit-public tells us which WS consumers should be similarly labeled).
- **RUR-C4 blocked by RUR-C2** because idempotency verification requires observable retries — otherwise a duplicated side effect looks like two independent successes.
- **RUR-C6 blocked by RUR-C2** because a cap-breach with no user-visible failure reason is worse than no cap (silent kill).
- **RUR-C7 depends on RUR-C1 + RUR-C2 minimum.** A golden path validator that runs before tenant boundaries + fail-loud land is a demo, not an invariant proof.

### Non-blocking parallel work

Within a wave, sub-arcs may fan out. RUR-C1 in particular is `L` and likely splits into:
- **I-0301** — AllowAny audit + endpoint remediation (26 endpoints)
- **I-0302** — Object-level perms on top-5 user-owned models
- **I-0303** — Celery task boundary scoping check

Chris D-verdict at Wave 1 open determines whether these ship as one arc or three siblings.

---

## §6. Mission Planning (per-campaign mission templates)

Each mission below is expressed in the shape it will take when it becomes its own implementation arc under `docs/research/implementation/<arc_slug>/I-NNNN_scoping.md`. This section is a template; the actual arc scoping is authored at mission open.

### RUR-C1 — Tenant Boundary Lockdown (I-0300 parent)

- **Objective:** eliminate cross-tenant data exposure across HTTP, WebSocket, and Celery task boundaries.
- **Scope:**
  - Audit + remediate 26 `AllowAny` endpoints across 8 files
  - Add object-level permissions on Deliverable, Initiative, ChatConversation, AgentExecution, Document
  - Add async task-boundary check: reject task payloads without `workspace_id`; re-verify ownership against DB row before mutation
- **Expected outcome:** exit criterion **E1** + **E2** verified via regression suite
- **Verification strategy:** automated regression suite in CI. Test as user-A attempting to read/write user-B's rows across every user-facing endpoint. Manual review of every remaining `AllowAny` with written justification.
- **Completion criteria:** zero cross-user reads pass. Regression suite green. Every retained `AllowAny` has justification comment in-code + review sign-off.
- **Expected deliverables:**
  - Endpoint audit ledger (workspace deliverable)
  - Custom permission classes committed
  - Regression suite committed
  - Ratification record + closeout deliverable
  - Implementation close doc: `I-030099_tenant_boundary_lockdown_implementation_close.md`

### RUR-C2 — Async State + Fail-Loud + Traceability (I-0400)

- **Objective:** eliminate silent failures on user-triggered async pipelines.
- **Scope:**
  - Base decorator: `@fail_loud_task(support_code_prefix, retryable=True/False)` applied to top-20 volume tasks
  - Canonical state machine `PENDING → RUNNING → SUCCEEDED | FAILED | CANCELLED` with timestamps
  - `OpsRunEvent` emission on success + failure with `trace_id`, `reason_code`, `human_message`, `support_code`
  - UI surface: canonical error component reads latest `OpsRunEvent` and renders `support_code + human_message`
- **Expected outcome:** exit criteria **E4** + **E5** + **E9** partial
- **Verification strategy:** chaos test — kill worker mid-task; user must see FAILED status with `support_code` in UI. Operator can look up `support_code` in <2 min.
- **Completion criteria:** top-20 volume tasks all emit failure events. UI displays `support_code` on failure. Chaos test green.
- **Expected deliverables:**
  - `fail_loud_task` decorator committed
  - State machine migration on `AgentExecution` + `OpsRun` if needed
  - UI error component updated
  - Chaos test suite committed
  - Ratification + closeout
  - `I-040099_async_fail_loud_implementation_close.md`

### RUR-C3 — Execution Convergence (I-0500)

- **Objective:** no execution sits `in_progress` past a documented wall-clock timeout.
- **Scope:** runtime watchdog on `AgentExecution` + `OpsRun`. Auto-FAIL after timeout. Cancellation propagation.
- **Expected outcome:** exit criterion **E3** verified; `cleanup_stuck_executions` command retires.
- **Verification strategy:** integration test — start execution, kill worker, wait > timeout, verify status flipped FAILED. Runtime: monitor for `in_progress` age > timeout for 7d; zero incidents.
- **Completion criteria:** watchdog task running in beat. Timeout config per task family. `cleanup_stuck_executions` deleted with justification comment. 7-day observation shows no stuck rows.
- **Expected deliverables:**
  - Watchdog task + config committed
  - Manual cleanup command deleted (with commit message pointer)
  - Ratification + closeout
  - `I-050099_execution_convergence_implementation_close.md`

### RUR-C4 — Idempotency Hardening (I-0600)

- **Objective:** side-effect tasks are retry-safe by construction.
- **Scope:** `idempotency_key` column on top-5 side-effect models. Apply-once guards on external calls (LLM providers, outreach sends, spend).
- **Expected outcome:** exit criterion **E7** verified.
- **Verification strategy:** test — fire same task with same `idempotency_key` 3× concurrently; verify exactly one side effect. Provider outage simulation → verify retry storm produces one side effect.
- **Completion criteria:** top-5 side-effect tasks accept `idempotency_key`. Test suite green. Concurrency test with 3× fire produces one row.
- **Expected deliverables:**
  - Migrations for `idempotency_key` column
  - Task decorators updated
  - Test suite committed
  - Ratification + closeout
  - `I-060099_idempotency_hardening_implementation_close.md`

### RUR-C5 — Channels Auth Hardening (I-0700)

- **Objective:** every WebSocket consumer authenticates + scopes.
- **Scope:** audit all 17 consumers. Fix 8 that don't reference `scope["user"]`. Ensure group names include workspace scope. Reject anonymous connects with `4401`.
- **Expected outcome:** exit criterion **E6** verified.
- **Verification strategy:** regression test — anonymous WS connect must close `4401`. Cross-workspace group send must fail. All 17 consumers exercised.
- **Completion criteria:** 17-consumer audit complete. Regression test green. `sports_betting/consumers.py:29` specifically fixed as canonical example.
- **Expected deliverables:**
  - Consumer audit ledger
  - Consumer code fixes
  - Regression test suite committed
  - Ratification + closeout
  - `I-070099_channels_auth_hardening_implementation_close.md`

### RUR-C6 — Cost Enforcement (I-0800)

- **Objective:** per-workspace budget caps enforced at task dispatch.
- **Scope:**
  - `SystemConfiguration` per-workspace cap column
  - Enforcement at `enqueue_llm_call` / `dispatch_agent_task` dispatch
  - High-cost flow confirmation UI
  - Observation period complete (per S2735 §17 gate); Chris D-verdict on monitor→freeze flip is a Wave 3 open precondition
- **Expected outcome:** exit criterion **E8** verified.
- **Verification strategy:** runtime — set low cap on synthetic workspace; trigger flow; verify hard-stop with user-visible `support_code`. Provider retry simulation → verify cap catches before amplification.
- **Completion criteria:** per-workspace cap column exists. Enforcement fires in monitor + freeze modes. Cap-breach `support_code` reaches UI.
- **Expected deliverables:**
  - Migration for per-workspace cap
  - Enforcement middleware / decorator
  - UI cap-breach surface
  - Ratification + closeout
  - `I-080099_cost_enforcement_implementation_close.md`

### RUR-C7 — Golden Path Alpha (I-0900, validator arc)

- **Objective:** prove Waves 1–3 by running 10 concurrent alpha users through one flawless end-to-end journey.
- **Scope:** ONE journey (defined at Wave 4 open based on Chris's pick; candidates in §7). Allowlist gating. Instrumented funnel.
- **Expected outcome:** exit criteria **E10** + **E11** verified.
- **Verification strategy:** live alpha cohort exercises journey. Chaos injection during exercise. Runtime monitoring. See §7 for full acceptance shape.
- **Completion criteria:** 10 alpha users complete journey concurrently. Zero cross-tenant leakage. Zero `in_progress` > 15min. Cost caps enforce on synthetic runaway. Chris ratifies alpha ready.
- **Expected deliverables:**
  - Allowlist mechanism
  - Instrumented journey funnel
  - Alpha cohort feedback
  - Ratification record
  - `I-090099_golden_path_alpha_implementation_close.md`

---

## §7. Verification Philosophy

Every campaign proves success through verifiable, observable evidence. This program does not accept "looks correct" as a completion signal.

### Preference hierarchy (top wins)

1. **Automated CI regression tests** — merge-blocking. Fastest feedback, hardest to game.
2. **Runtime observation with metric SLOs** — 7-day windows with numerical pass/fail thresholds. Grounded in `ops_tool.slo_status` substrate.
3. **Operational verification** — operator runs a scripted playbook against staging + records outcomes.
4. **Failure injection / chaos tests** — deliberate breakage to prove the failure signal fires.
5. **Cohort-driven validation** — allowlist alpha users exercise the golden path (Wave 4 only).

### Verification anti-patterns (rejected)

- "The code compiles" — necessary, not sufficient
- "The manual test passed" — not repeatable; not merge-blocking
- "It looked correct in the demo" — Rigby's S2740 §E1 "Succeeded but wrong" class
- "The SLO is green" without corroboration — S2740 §A2 evidence that green SLOs may reflect swallowed failures rather than working systems

### Specific verification patterns adopted

- **Chaos worker-kill** for fail-loud (RUR-C2 completion): kill Celery worker mid-task, user must see FAILED with `support_code`
- **Concurrency 3× same-key fire** for idempotency (RUR-C4 completion): three concurrent identical dispatches must produce one row
- **Cross-user regression suite** for tenant lockdown (RUR-C1 completion): user-A cannot read user-B's rows across every user-facing endpoint
- **Runaway synthetic** for cost enforcement (RUR-C6 completion): synthetic workspace with $1 cap must hard-stop the runaway with user-visible reason
- **Anonymous WS close** for channels hardening (RUR-C5 completion): anonymous connect must close `4401` on every consumer
- **Concurrent 10-user alpha exercise** for validator (RUR-C7 completion): 10 users through the golden path with zero invariant violations

### Verification cadence

- Regression tests run per-PR merge
- SLO windows evaluated at each Wave close
- Chaos tests run at least once per Wave close on staging
- Alpha exercise runs at RUR-C7 open

---

## §8. Alpha Readiness

Rigby's S2740 §F framing pushback is **accepted**. This campaign prepares the platform for a **gated allowlist alpha**, not unrestricted self-service. Self-serve is a distinct future program not scoped here.

### Expected user journey (alpha)

The exact journey is picked at RUR-C7 open. Candidates from the platform's user-facing surface:

- **Candidate A — Content generation.** Sign in → land in workspace → create a content initiative → run the pipeline → see the published deliverable → next-action pointer.
- **Candidate B — Deliverable produce+approve.** Sign in → land in workspace → produce a deliverable via agent dispatch → review → approve → downstream artifact appears.
- **Candidate C — Rigby chat.** Sign in → open PA chat → issue a task → receive a completion banner → see the result deliverable in workspace.

Each candidate is 5–10 clicks. Each must pass exit criteria E1–E9 in the journey path.

### Operational expectations

- **Cohort size:** 10 concurrent users during exercise; up to ~25 provisioned allowlist entries
- **Duration:** 2 weeks minimum observation window post-cohort exercise
- **Rollback:** allowlist can be revoked per-user without deploy
- **Support cadence:** operator reachable within 24h; incident SLO defined at Wave 4 open

### Alpha operating mode mitigation (added at Rigby SIGN §4)

Because backpressure + user-visible progress UI was **deferred out of program scope**, alpha exposure requires a compensating operational-mode contract. Proposed default (subject to §12 Q8 Chris D-verdict):

- **Autonomy throttling:** scheduled autonomous agent runs (beats) reduced to minimum cadence during alpha exercise. User-initiated dispatches take worker priority.
- **Spider cadence reduction:** background ingest cadence reduced so worker slots are available for user-triggered work.
- **Governor throttling:** agent-dispatch governor set to conservative cap.
- **Backpressure fallback:** if queue depth exceeds threshold, user-facing dispatches return a hard-fail `support_code` with actionable message ("system busy, retry in N min") rather than silently queueing.

If Chris rules against throttled operating mode at §12 Q8, backpressure re-enters program scope and RUR-C8 opens as its own campaign (not currently planned).

### Engineering expectations

- Every hard-blocker gate (G1–G6) passes on production before cohort access opens
- Observability + support (G7 + G8) partial acceptable if operator-side triage is documented
- No known open cross-tenant bug at cohort open
- No known open silent-failure surface on any journey-path task

### Support expectations

- User can quote a `support_code` from any error surface
- Operator can retrieve full trace from `support_code` in <2 min
- Common failure modes have runbook entries

### Monitoring expectations

- `ops_tool.slo_status` covers task success rate, agent timeout rate, and one new SLO added by this campaign: **cross-tenant regression suite pass rate = 100% or halt**
- Per-workspace cost accumulation visible to operator
- Anomaly alerts on: `AgentExecution` age > timeout, `OpsRunEvent` failure spike > 3σ, cost-cap breach events

---

## §9. Engineering Philosophy

The campaign optimizes for:

- **Trust** — users can rely on the platform to do what it says
- **Correctness** — outputs match intent; no "SUCCEEDED with wrong content"
- **Observability** — every action traceable end-to-end
- **Recoverability** — retries safe; failures visible; support paths exist
- **Determinism** — same input → same behavior; no context-drift surprises
- **Tenant safety** — no cross-user data exposure under any code path
- **Operator confidence** — incidents diagnosable in minutes, not hours

The campaign does NOT optimize for:

- New user-facing features
- Aesthetic polish
- Additional AI agent capabilities
- Novel architecture experiments

**When invariant-strengthening tension is chosen against feature-shipping tension, invariant-strengthening wins.** This is Chris's directive at S2741 open.

Playbook alignment: this program is consistent with PLAYBOOK-6.10.6 verify-before-build (every campaign leads with existing-implementation analysis), Cat A discipline (do not add new substrate when existing substrate can be extended or corrected), and the S2745 engineering-pivot memory rule (this program is net-new engineering, not audit-of-what-exists — the S2740 assessment was the audit; the campaigns are the builds).

---

## §10. Future Campaign Structure

This document is the constitutional reference for the Real User Readiness program. Its stability contract:

- **Location:** `docs/research/implementation/real_user_readiness/CAMPAIGN.md` — do not rename or relocate without updating CLAUDE.md L7 anchor
- **Authority:** constitutional (per frontmatter). Sub-campaign implementation arcs cross-reference this doc; this doc does not incorporate sub-campaign detail
- **Amendment discipline:** changes to §2 (Definition of Ready), §3 (Definition of Done), §4 (Campaign Map), or §5 (Dependency Graph) require Chris D-verdict. Changes to §6 (Mission Planning templates) require ratification if any campaign is mid-implementation
- **Cross-references FROM sub-arcs:** every I-03xx arc opened under this campaign includes a top-of-file pointer to this document + the sub-campaign ID (RUR-C1..C7). This lets any future reader trace a sub-arc back to its parent invariant
- **Cross-references TO sub-arcs:** §4 Campaign Map above holds arc-slot placeholders (I-0300, I-0400, etc.). When an arc opens, the corresponding row is updated with the arc file path

Each approved campaign eventually spawns:

- Its own workspace (or sub-workspace under `Real User Readiness Campaign`)
- Its own implementation arc doc under `docs/research/implementation/<arc_slug>/`
- Its own mission sequence (per IOS convention: scoping → design-prep → Pn stages → implementation close)
- Its own verification cycle
- Its own ratification record under `docs/research/implementation/RATIFICATION_*.md`
- Its own merge/PR trail

The parent CAMPAIGN.md acts as the invariant-preservation gate against sub-campaign scope drift.

---

## §11. Pressure Testing — Recorded Divergences from S2740 Reconciliation

Per Chris's directive at S2741 open, Claude and Rigby operated independently before converging. Where reconciliation did not fully close disagreement, the divergence is recorded here so implementation missions inherit it explicitly rather than resolving it silently.

### Divergence 1 — Wave 1 prerequisite graph (Claude vs Rigby)

- **Rigby S2740 §C position:** RUR-C2 (Async Fail-Loud) has prereq of RUR-C1 (Tenant Lockdown). Reasoning: fail-loud surfaces may leak foreign-workspace data in error messages.
- **Claude S2740 §0 push-back:** fail-loud can ship *scoped-by-design*. If the failure surface never renders workspace-adjacent data (only `support_code + reason_code + human_message`), no prereq is required.
- **Reconciliation:** Wave 1 lists RUR-C1 + RUR-C2 as parallel-safe. Chris D-verdict required at Wave 1 open. If Chris agrees with Rigby, RUR-C1 gates RUR-C2. If Chris agrees with Claude, they run in parallel.
- **Implication for planning:** if Rigby's view wins, calendar extends by RUR-C1's L effort before RUR-C2 can start. If Claude's view wins, both waves progress in parallel.

### Divergence 2 — Tenant Lockdown effort estimate

- **Rigby S2740:** RUR-C1 effort = **M**.
- **Claude S2740 §0:** RUR-C1 effort = **L**, likely splits into 3 sibling arcs (I-0301 AllowAny audit + I-0302 object-level perms + I-0303 async boundary). 26 endpoints + 17 consumers + task boundary checks + 585 models makes M implausible.
- **Reconciliation:** classified as **L** in §4 Campaign Map. Split into I-0301/2/3 is a Chris D-verdict at RUR-C1 open, not pre-decided.
- **Implication for planning:** if Rigby's M is right, RUR-C1 completes in a single arc; if Claude's L is right, RUR-C1 is a mini-program of its own.

### Divergence 3 — Backpressure + progress UI campaign

- **Rigby S2740 §C8:** "Backpressure + user-visible progress" as its own campaign #8.
- **Claude S2740 §0:** rejected — not top-tier for gated alpha with cohort-size operator triage.
- **Reconciliation:** deferred out of alpha scope. Recorded as follow-on program candidate.
- **Implication:** if alpha exercise reveals backpressure as a real trust-blocker, it re-opens as a post-alpha campaign.

### Divergence 4 — "Succeeded but wrong" detection

- **Rigby S2740 §E1:** flagged as major risk class — jobs return SUCCEEDED with empty/low-signal outputs. No fix without content-level validation.
- **Claude S2740 §8:** flagged as open question requiring Chris D-verdict on how detection ships (or whether it's post-alpha).
- **Reconciliation:** treated as post-alpha risk in current program scope. Alpha operator-side quality review is the interim mitigation. Recorded as follow-on program candidate.
- **Implication:** the E1 risk class is NOT covered by any campaign in this program. Alpha users may hit it. Explicit tradeoff.

### Divergence 5 — S2741 initialization framing itself

- **Rigby S2740 §F:** "Ready for real users?" is under-specified; correct framing is "gated alpha" not "self-serve."
- **Claude S2740 §7:** designed the vertical slice assuming self-serve-adjacent language.
- **Chris D-verdict at S2741 open:** Rigby's framing accepted.
- **Implication:** RUR-C7 (Golden Path Alpha) is the correct scope-endpoint for THIS program. Self-serve is not scoped here. Cost cap enforcement (RUR-C6) is scoped for allowlist, not for arbitrary user provisioning.

### Divergence 6 — G7/G8 enabler-vs-blocker contradiction (surfaced at Rigby S2741 SIGN)

- **Claude first draft §2:** labeled G7 (Observability) + G8 (Supportable Errors) as ENABLERS, not blockers.
- **Claude first draft §3:** made E5 (`support_code` everywhere) + E9 (end-to-end `trace_id`) hard campaign exit criteria.
- **Rigby S2741 SIGN §1:** these positions contradict — if E5 + E9 are hard campaign-close requirements, G7 + G8 are functionally blocking at campaign-close even if enabling-only at alpha-open.
- **Reconciliation:** two-layer gate contract adopted in §2. Alpha-open gates = G1–G6 hard + G7/G8 partial acceptable. Campaign-close gates = G1–G8 hard (E5/E9 map to G7/G8). Contradiction resolved by making the two-layer contract explicit rather than pretending one layer suffices.
- **Implication:** RUR-C2 scope now includes traceability substrate for E9 (renamed to reflect this). RUR-C2 is materially larger than "just fail-loud."
- **This divergence MUST resolve before Wave 1 sequencing begins** — otherwise sub-campaigns inherit ambiguity about which gate they're paying down.

### Reconciliation contract

Divergences 1, 2, and 6 above surface at Wave 1 open and require Chris D-verdict before RUR-C1 or RUR-C2 arcs can open. This document does not force resolution; it forces visibility. Div 3, 4, 5 are already resolved (Chris D-verdict or deferred-out-of-scope).

---

## §12. Open Questions Requiring Chris D-Verdict Before Wave 1 Opens

1. **Divergence 1 (Wave 1 prereq graph):** RUR-C1 and RUR-C2 parallel, or RUR-C1 gates RUR-C2?
2. **Divergence 2 (RUR-C1 effort):** single arc, or split into I-0301/2/3?
3. **Wave 1 open sequencing:** do we open RUR-C1 or RUR-C2 first (independent of parallel-vs-serial question)? Different sub-teams could work them; if only one arc can be actively worked, which?
4. **Golden path candidate:** A (content), B (deliverable produce+approve), or C (Rigby chat)? Determines RUR-C7 shape.
5. **Cost enforcement cadence:** RUR-C6 currently sits in Wave 3. Observation period closes 2026-07-11. If observation is clean, do we pull RUR-C6 forward as Wave 1B parallel with RUR-C1/C2?
6. **"Succeeded but wrong" risk:** accepted as post-alpha risk per §11 Div 4? Or open a new campaign in this program?
7. **Alpha cohort provisioning:** who / how many? Determines RUR-C7 acceptance criteria specifics.
8. **Alpha operating mode (added at Rigby SIGN §12):** since backpressure is deferred out of program scope, we need an explicit mitigation. Should alpha default to throttled autonomy / reduced spider cadence / governor-throttled agent dispatch? If yes, define the throttle contract. If no, accept that a runaway autonomous run could degrade cohort UX.
9. **Cost-enforcement clean-observation numeric threshold (added at Rigby SIGN §12):** current phrasing "if observation goes clean" is subjective. Define numerically: e.g., "if 7-day observation shows peak-hour spend < $X and no threshold breaches at $500/month monitor level."

---

## §13. Ratification Contract

This CAMPAIGN.md is a planning artifact until Chris ratifies it. Ratification signals:

- Chris D-verdict on §12 open questions (at minimum on Q1, Q2, Q3, Q4 to open Wave 1)
- Rigby SIGN pressure-test recorded (per Chris directive at S2741 open — "Claude and Rigby should continue operating independently before converging. If one recommends a campaign, the other should attempt to falsify it.")
- Workspace `Real User Readiness Campaign` created + linked to this doc
- Registration in `docs/INDEX.md` (via `build_docs_index`) + Rigby-searchable via cascade (per S1802 rule)

Post-ratification, this document becomes the constitutional reference against which every sub-campaign's scope drift is measured.

---

**End of parent CAMPAIGN.md. Sub-campaigns open as `docs/research/implementation/<arc_slug>/I-NNNN_scoping.md` files with a top-of-file pointer back to this doc.**
