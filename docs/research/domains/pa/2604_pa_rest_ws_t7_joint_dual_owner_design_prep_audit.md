---
title: "PA REST↔WS T7 Joint Contract SoT (Dual-Owner PA Side) — Design-Prep Audit"
status: active
authority: research
version: v1
session_id: 2604
date_opened: 2026-07-06
date_ratified: 2026-07-06
arc: Research Group 2600 (PA — Cross-Arc Handoff Bundle Consuming CF-2600-PA + CF-D6 + F-B-HIGH-3 + Workspace-Context Authz + REST↔WS T7 Joint Dual-Owner PA Side) — S2604 P4 Cat D
domain_slug: pa
research_group: 2600
child_slot: P4 Cat D
head_sha: cf410660 (post-S2603 docs cascade merge; verified at session open)
companion_anchors:
  - docs/CLAUDE.md
  - docs/PLATFORM_WHAT_IT_IS.md
  - docs/PLATFORM_INVENTORY.md
  - docs/topics/personal-assistant.md
  - docs/topics/frontend.md
  - docs/topics/celery-workers.md
  - docs/topics/infrastructure.md
  - docs/research/ARCHITECTURE_INDEX.md
  - docs/research/OPEN_ARCS.md
  - docs/research/DOMAIN_RESEARCH_PLAYBOOK.md
  - docs/research/process/RESEARCH_OPERATING_SYSTEM.md
related:
  - docs/research/domains/pa/2600_pa_domain_scoping.md   # DIRECT PARENT (§3.D + §5.3 AC + §2.6 lens)
  - docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md   # SIBLING Cat A (§7.2 REST-side "task-based async; NO streaming" + §6.1 F11 34-endpoint canonical)
  - docs/research/domains/pa/2602_pa_client_contract_surface_design_prep_audit.md   # SIBLING Cat B (§6.2 F-B3 U6 canonical + §6.3 F-B3 REST-embedded audio_url + §15.2 CF-D6 debt)
  - docs/research/domains/pa/2603_pa_workspace_authz_session_lifecycle_design_prep_audit.md   # SIBLING Cat C (§7.2 AC-C1-4 T7 REST-side statement + §16.1 F5+F-C7 hard "INVALID" analog)
  - docs/research/domains/api/2504_api_permission_floor_registry_rest_ws_t7_joint_design_prep_audit.md   # CF-D6 ORIGIN (Group 2500 side of dual-owner)
  - docs/research/domains/api/2599_api_canonical_summary.md   # Group 2500 canonical verdict + Cat D γ mechanism-nesting decision
  - docs/research/domains/auth/2402_auth_permission_floor_uniformity_audit.md   # F-B-HIGH-3 origin (Cat C1-owned per parent §5.3 AC#3)
verifier_loop: |
  v1 (2026-07-06, S2604 arc-continue):
  Drafted after Rigby SIGN-preview HIGH confidence + 2 STRENGTHEN folds
  (F-D1 carve-out conditionality + F5-analog observability coupling + F-D2
  AC-D2 denominator scope clamp + 3-part evidence record) + Chris "agree all"
  wholesale ratification 2026-07-06.

  Six-parallel-Explore-agent sweep per playbook §13 dispatched at S2604 open
  turn 2 (after shape-card ratification): Agent 1 Models & Persistence +
  Agent 2 Services & Runtime Flows + Agent 3 APIs/Tools/Tasks/Commands +
  Agent 4 Integrations & Cross-Domain Dependencies + Agent 5 Documentation
  & Prior Research + Agent 6 Drift/Debt/Ownership/Maturity.

  Parent-Claude verifier-loop applied pre-draft per playbook §14 discipline.
  7 verifier corrections logged (VC-1 PA-related Consumer inventory
  expansion beyond Cat B canonical 1-channel to 4-consumer subset +
  VC-2 PersonalAssistantConsumer naming collision at 2 files +
  VC-3 emit sites cross-verified across 6 files +
  VC-4 F-D-WSENVELOPE-1 preserved at all PA WS Consumers +
  VC-5 F-D1 fold streaming-absence CONFIRMED in views_personal_assistant.py +
  VC-6 CODEOWNERS PA WS Consumer files unassigned +
  VC-7 channels_graphql absent + CHANNEL_LAYERS at settings.py:279/289).
  See §14.1 for the full chain and §20.6 for the correction ledger.

  Rigby SIGN cycle 1 CLOSED 2026-07-06 via dedicated fresh SIGN
  isolation pin `pa-e14f943525a84b5a` (TWENTY-EIGHTH-consecutive
  dedicated fresh SIGN pin retirement in Research OS after twenty-seven
  prior). Preemptive 2-batch × 2-Q batching per S2602 + S2603 SUCCESS
  pattern per `feedback_rigby_sign_worker_instability_recovery.md` —
  SINGLE-PIN close achieved (no worker instability observed).

  SIGN cycle 1 verdict per Batch:
  - Batch 1 (Q1 coverage + Q2 maturity): HIGH confidence, 5 STRENGTHEN
    folds (F-D-B1-1 through F-D-B1-5).
  - Batch 2 (Q3 debt + Q4 boundary): HIGH confidence, 6 STRENGTHEN
    folds (F-D-B2-1 through F-D-B2-6).
  Overall confidence: HIGH. Total folds: 11 STRENGTHEN, 0 DIAL-BACK,
  0 REJECT. See §20.8 for full fold ledger.

  Chris "agree all" wholesale ratification 2026-07-06 baked all 11
  folds in-place. Status flipped `draft` → `active` per playbook §16
  draft-first workflow.
owner: claude (drafted S2604 v1 with 2 pre-drafting shape-card folds baked; Rigby SIGN cycle 1 pending)
---

# PA REST↔WS T7 Joint Contract SoT (Dual-Owner PA Side) — Design-Prep Audit

> **Positioning.** P4 Cat D of Group 2600 PA arc. TWENTY-FOURTH-consecutive
> playbook §11.2 20-section child-audit application (after S1301/S1401/
> S1501/S1601/S1701/S1801/S1901/S2001/S2101/S2102/S2103/S2104/S2201/S2202/
> S2203/S2204/S2401/S2402/S2403/S2404/S2501/S2601/S2602/S2603 twenty-three
> prior). Terminal child before S2699 xx99 close per parent §5.1 child
> mission sequence.
>
> **Positioning boundary.** Cat D owns the **contract-shape** of PA WS
> message envelope declaration + REST↔WS T7 joint consistency rule
> (dual-owner PA side; Group 2500 side owned by S2504 arc-close
> design-prep). Cat D does NOT own PA behavior mutations (Cat-D-6),
> agent-registry mutations (Cat-D anti-scope inherits parent #4),
> TokenAuthMiddlewareStack modifications (Cat-D-2), F-B-HIGH-3 closure
> (Cat C1-owned per parent §5.3 AC#3 + Cat C §16.1), or S2504 γ mechanism
> content re-litigation (Cat-D-4). See §16.4 for the nine explicit
> Cat-D-1..9 micro-anti-scope items.

---

## 1. Executive Summary

**What Cat D is.** The PA REST↔WS T7 joint contract SoT audit closes the PA-slice application of CF-D6 dual-owner arrangement declared at S2504 §18.2 + R10. Cat D enumerates the PA-related WS surface (subset of platform 120 WS routes + 87 Consumer classes per S2504 §6.3), grades envelope-shape SoT declaration state at HEAD `cf410660`, records Path A/B/C+observability-compensation eligibility per PA-client canonical message class (Cat B §6.2 F-B3), and produces the T7 cross-transport consistency rule across 3 §3.5 probes. Cat D is EVIDENCE-ONLY + CHRIS-D-VERDICT-DEFERRED; the Path A/B/C+observability-compensation verdict lands at S2699 xx99.

**Biggest gaps at HEAD (Rigby SIGN cycle 1 severity-upgrade folds baked 2026-07-06).**
1. **DEBT-D-1 F-D-WSENVELOPE-1 PA-slice preservation — HIGH severity (F-D-B2-1 fold: MEDIUM → HIGH + finding_type → missing_contract).** Zero `TypedDict` / `Protocol` / `BaseModel` / `@dataclass` declared across all PA WS Consumer files (VC-4). All 3 Cat B canonical message classes emit `observed-JSON-only` shape at HEAD. Cat D DECLARATION-plane maturity is EXPERIMENTAL (§13.1 axis (ii)). PA WS is CLAUDE.md canonical operator entry + primary real-time surface for web ChatUI — envelope integrity is high-leverage boundary.
2. **DEBT-D-9 WS envelope SoT registry ABSENT — HIGH severity (F-D-B2-4 fold NEW row).** No `core/services/ws_envelope_registry.py` or equivalent at HEAD (§5.6). Distinct class of gap from DEBT-D-1: org-wide SoT mechanism vs PA-slice envelope contract. xx99 must declare whether PA creates local SoT (Path A/B local) or waits for Group 1700 platform registry.
3. **DEBT-D-4 REST↔WS parallel-delivery reconciliation gap — HIGH severity (F-D-B2-2 fold: MEDIUM → HIGH + closure text addition).** Cat B §7.1 evidence baseline: task completion fires via both REST poll AND WS event, with client-side dedup only via `seenCompletions` 50-item bounded ring — no server-side reconciliation logic at HEAD. User-visible risk (duplicate renders, missed completions, "ghost" events) + silent failure mode. xx99 Path selection must explicitly choose dedup/reconciliation posture (marker vs telemetry vs acceptance).
4. **Path C+carve-out collapses to Path C non-streaming per F-D1 fold conditional (§7.1 + VC-5).** Cat A §7.2 REST-side statement "task-based async; NO streaming" is mirrored at PA WS: `views_personal_assistant.py` has zero `StreamingHttpResponse` / `text/event-stream` / `Transfer-Encoding: chunked`; `PAConversationConsumer.message_created()` calls `send(text_data=json.dumps(...))` atomically per event. Path C-pure is **HARD-INVALID / NON-SELECTABLE** per F5-analog (§16.2).
5. **Observability-plane maturity ABSENT/EXPERIMENTAL (F-D-B1-5 fold — §13 3-axis split).** Zero envelope-shape telemetry to Group 1700 at HEAD. Zero shape-version fields emitted at any canonical class. If Path C+observability-compensation ratified at xx99, observability axis moves ABSENT → REQUIRED per AC-D4 spec.
6. **PersonalAssistantConsumer naming collision at 2 files (§17.1 + VC-2).** `PersonalAssistantConsumer` class exists at both `core/consumers_unified_v2.py:20` and `core/personal_assistant_consumer.py:14` — routing.py:27 import-as alias avoids Python-level clash but introduces cognitive-load drift (DEBT-D-5 LOW).

**What should be researched next.**
- **CRITICAL (§19.1):** S2699 xx99 Chris-D-verdict on Path A / Path B / Path C+observability-compensation for PA WS envelope strictness. F5-analog per F-D1 fold blocks Path C-pure. Verdict couples to Cat C1 coupling axis (§9.3) if evidence surfaces.
- **HIGH (§19.2):** Group 1700 Observability T4 arc scope declaration for envelope-shape telemetry emit-signature (AC-D8 canonical).
- **MEDIUM (§19.3):** Post-arc docs cascade for `docs/topics/personal-assistant.md` WS-envelope subsection SPEC + `docs/topics/frontend.md` PA WS documentation drift closure (Agent 5 gap analysis).

**Cat D verdict path per parent §5.3 AC#2 + F-D1 fold analog:** Chris-D-verdict at S2699 xx99 selects one of {Path A / Path B / Path C+observability-compensation}. Path C-pure (SoT-declared WITHOUT observability compensation) is **HARD-INVALID / NON-SELECTABLE** per F5-analog ratified by Chris "agree all" 2026-07-06 (F-D1 fold second clause).

---

## 2. Domain Purpose

### 2.1 What Cat D captures

Cat D captures the PA WS message-contract SoT DECLARATION state at HEAD `cf410660` — where is envelope shape declared (or not) for PA-related WS channels, and what is the T7 cross-transport consistency rule between REST-side (Cat A §7.2 "task-based async; NO streaming") and WS-side (Cat D scope). Cat D produces evidence artifacts consumable by S2699 xx99 for Chris-D-verdict + Group 1700 Observability T4 handoff.

### 2.2 Why Cat D matters

- **F-D-WSENVELOPE-1 PA-slice preservation** (S2504 §14.2 canonical zero-baseline): 0% envelope conformance across 120 WS routes / 87 Consumer classes at HEAD. Cat D verifies PA-slice preservation + records enforcement-point declaration state per canonical message class.
- **Cat C §7.2 AC-C1-4 T7 REST-side statement** explicitly delegated WS-side declaration to Cat D: *"REST-side workspace-context enforcement is handler-internal implicit-gate; WS-side enforcement is UNKNOWN pending Cat D S2604 evidence."*
- **Parent §2.6.B delta-decision** on whether PA warrants stricter WS envelope declaration than the S2504 baseline (0% conformance) — Cat D produces the evidence for xx99 verdict.
- **CF-D6 dual-owner arrangement** (S2504 §18.2 + R10): Group 2500 side owned by S2504; Group 2600 side owned by S2604 PA-slice application.

---

## 3. Canonical Entry Points

### 3.1 PA-related WS routes at HEAD `cf410660` (VC-1 — expanded from Cat B canonical 1-channel)

Per Cat-D-3 anti-scope, Cat D cites platform 120-route denominator from S2504 §6.3 canonical + filters PA-related subset only. Per Cat B §6.2 F-B3 canonical (§6.2), the CLIENT-CONSUMED subset is 1 channel; per VC-1 verifier-loop correction, the PA-RELATED subset (routes referencing PA / assistant / personal-assistant) at `core/routing.py` is 5 URL patterns routing to 4 distinct Consumer classes:

| # | Route pattern | File:line | Consumer class | Consumer file:line | Client-consumed? |
|---|---|---|---|---|---|
| 1 | `ws/pa/conversations/(?P<conversation_id>[^/]+)/$` | `core/routing.py:135` | `PAConversationConsumer` | `core/consumers_pa_conversation.py:175` | **YES** (Cat B §6.2 F-B3 canonical: `frontend/src/pages/CommandCenterPage.tsx:682-764`) |
| 2 | `ws/assistant/$` | `core/routing.py:138` | `PersonalAssistantV2Consumer` (alias for `PersonalAssistantConsumer` via routing.py:27 import-as) | `core/consumers_unified_v2.py:20` | UNKNOWN at HEAD (no client subscription found via grep on literal path — dynamic URL construction possible; verifier-loop next-step) |
| 3 | `ws/ai-assistant/$` | `core/routing.py:141` | `consumers.AssistantChatConsumer` | `core/consumers_base.py:390` | UNKNOWN (see #2 caveat) |
| 4 | `ws/interview/$` | `core/routing.py:144` | `consumers.AssistantChatConsumer` (SAME class as #3 — alias route) | `core/consumers_base.py:390` | UNKNOWN (see #2 caveat) |
| 5 | `ws/personal-assistant/$` | `core/routing.py:363` | `PersonalAssistantConsumer` (from `core/personal_assistant_consumer.py:14`) | `core/personal_assistant_consumer.py:14` | UNKNOWN (see #2 caveat) |

**PA-related WS route count at HEAD: 5 URL patterns (subset of platform 120 per S2504 §6.3).**
**PA-related Consumer class count at HEAD: 4 distinct classes (subset of platform 87 per S2504 §6.3).**

**Denominator vs perimeter distinction (F-D-B1-3 fold ratified 2026-07-06 — Rigby SIGN cycle 1 Batch 1 Q1c STRENGTHEN, Chris "agree all" wholesale):**

- **Denominator (F4 target — F-D2 canonical scope):** Cat B canonical 3 message classes + Consumer #1 (PAConversationConsumer) — the CLIENT-CONSUMED subset for which envelope-declared-vs-absent state is verified at HEAD. This is what F-D2 fold F4 target (0 UNKNOWN on envelope-declaration-existence) applies to.
- **Perimeter (VC-1 partial sample):** the 4 distinct PA-related Consumer classes / 5 URL patterns are **route/consumer inventory evidence** that Cat D has surveyed the PA WS boundary and found more surface area, but Cat D does NOT claim full envelope-declaration verification across Consumers #2-4 (§6.1.2 with-pointer DEBT). Perimeter is context, not F4-met coverage.

**Naming-collision caveat (VC-2, §17.1):** `PersonalAssistantConsumer` class exists in BOTH `core/consumers_unified_v2.py:20` AND `core/personal_assistant_consumer.py:14`. The routing.py import-as alias at line 27 (`from .consumers_unified_v2 import PersonalAssistantConsumer as PersonalAssistantV2Consumer`) resolves the import collision; both classes are ROUTED simultaneously (routes #2 + #5 above).

### 3.2 Cat B canonical WS message-class inventory (F-B3 canonical artifact — CITED, NOT re-inventoried per Cat-D-7)

Per Cat B §6.2 F-B3 canonical (`docs/research/domains/pa/2602_pa_client_contract_surface_design_prep_audit.md:452-480`) — the CLIENT-CONSUMED subset for PAConversationConsumer:

| # | Class label | Event `type` string | Envelope-grade at HEAD | Cat B canonical citation |
|---|---|---|---|---|
| 1 | chat-response streaming | `message.created` | `observed-JSON-only` | Cat B §6.2 F-B3 canonical |
| 2 | task-status broadcast | `agent.completed` | `observed-JSON-only` | Cat B §6.2 F-B3 canonical |
| 3 | rigby.tool.* lifecycle | `rigby.tool.started` + `rigby.tool.completed` | `observed-JSON-only` | Cat B §6.2 F-B3 canonical (Session 1172 seed) |

**Cat B §6.3 F-B3 relabel evidence (RE-VERIFIED at HEAD `cf410660`):** `audio_url` is REST-embedded in `/api/pa/chat/status/<task_id>/` poll response body (Cat A §7.3 evidence at line 402-415), NOT WS-broadcast. Cat B §6.3 F-B3 relabel preserved at HEAD.

### 3.3 F8-analog baseline codification test

Cat A §3.3 F8 baseline codification test was: does `/api/pa/chat/` already have any documented OpenAPI operationId or schema declaration outside `@extend_schema`? If NONE exists, Path C-pure is strictly worse than Path C+island.

Cat D F8-analog test: does `/ws/pa/conversations/<conversation_id>/` have any documented WS envelope schema declaration outside a hypothetical typed envelope model? Evidence at HEAD:
- **Zero envelope-SoT models declared** at PA WS Consumer files (VC-4 grep verified — §4.1).
- **Zero client-side TypeScript interface** declared for the 3 canonical WS message classes at `frontend/src/pages/CommandCenterPage.tsx` (Cat B §6.2 evidence + Agent 1 verified).
- **Zero WS envelope `.schema.json`** files for PA-related channels (Agent 1 verified).

**F8-analog codification result:** at HEAD, Path C-pure at Cat D is strictly worse than Path C+observability-compensation per F-D1 fold ratified 2026-07-06. Path C-pure is **NON-RATIFIABLE** per F5-analog.

---

## 4. Major Models

### 4.1 Envelope-SoT model check (F-D-WSENVELOPE-1 PA-slice verification — VC-4)

Per Agent 1 + parent-Claude verifier-loop grep on `core/consumers*.py` for `TypedDict`, `Protocol`, `BaseModel`, `@dataclass`:

- **ZERO matches** across `core/consumers_pa_conversation.py`, `core/consumers_unified_v2.py`, `core/consumers_base.py`, `core/personal_assistant_consumer.py`.
- **ZERO matches** in `core/services/pa_status_events.py` for typed envelope models on emit path.
- **ZERO matches** in `frontend/src/pages/CommandCenterPage.tsx` + `frontend/src/lib/api.ts` + `frontend/src/stores/paStore.ts` + `frontend/src/hooks/useWebSocket.ts` for `interface WSMessage*` / `type WSMessage*` declarations for the 3 canonical PA WS message classes.
- **ZERO `.schema.json`** files for PA WS message types (application-specific).

**F-D-WSENVELOPE-1 PA-slice preservation VERIFIED at HEAD `cf410660`.** PA-slice fully inherits the S2504 §14.2 canonical zero-baseline: "WS message-contract SoT ABSENT at HEAD."

### 4.2 PA WS-emission-relevant Django models

Per Agent 1 evidence + parent-Claude verifier-loop:

| Model | File:line | Key fields | WS event class it feeds |
|---|---|---|---|
| `ChatConversation` | `core/models/conversations/models.py:59` | `conversation_id` (line 76, db_index), `user` FK (line 69, NOT NULL), `session_active` (line 139, default=True, db_index), `workspace` FK (line 146, nullable), `source` (line 89: 'pa' choice), `created_at` (line 169, auto_now_add), `metadata` JSONB (line 158) | `message.created` (user + PA post persistence); `agent.completed` (server-side persist via `create_completion_row()` at `core/consumers_pa_conversation.py:149-154`) |
| `AgentExecution` | `core/models_unified_system.py:882-1006` | `id` UUID PK (line 891), `conversation_id` CharField denormalized (line ~1001, non-null for PA executions), `status` (terminal: completed/failed/error), `created_at`, `user` FK | `agent.completed` — WS broadcast fired by `fire_agent_followup_subscriptions()` at `core/tasks_agents.py:336-491` when execution transitions to terminal state |
| `AgentFollowupSubscription` | `core/models_unified_system.py:1017-1096` | `id` UUID PK (line 1067), `execution` FK (line 1069), `conversation_id` CharField denormalized (line 1077, db_index), `state` (STATE_ARMED / FIRED / EXPIRED / CANCELLED — line 1079), `expires_at` DateTimeField (line 1085, null=True for auto-wake execution-lifecycle-bound) | `agent.completed` — signal handler flips 'armed' → 'fired' on terminal AgentExecution state; broadcast trigger |
| `ToolCallRecord` | `core/models_tool_calls.py:19-118` | `id` UUID PK (line 44), `trace_id` UUID (line 47, db_index — join key for ticker dedup), `conversation_id` UUID (line 51, db_index), `tool_name` (line 63, db_index), `latency_ms` (line 105), `success` Boolean (line 91), `created_at` (line 117, auto_now_add, db_index) | **NOT** the direct WS source. Sourced by `core/services/tool_dispatcher.py` (Session 1172 seed); emit via `core/services/pa_status_events.py:116-182` using `trace_id` as join key for `rigby.tool.*` lifecycle events |

**Key finding:** `ChatConversation` is the canonical WS-emission row sink; `AgentExecution` + `AgentFollowupSubscription` are the canonical `agent.completed` trigger pair; `ToolCallRecord` is logged post-hoc (not the WS emit source — `trace_id` threading through dispatcher is the source per Agent 1).

### 4.3 Channels layer + WS broker persistence

Per Agent 1 verified evidence:
- **`channels_graphql`:** ABSENT (`requirements*.txt` grep zero matches at HEAD — VC-7).
- **`CHANNEL_LAYERS` config at `core/settings.py:279-293`** (VC-7): Production = `'BACKEND': 'channels_redis.core.RedisChannelLayer'` with `REDIS_URL` env var (line 281); Fallback = `'BACKEND': 'channels.layers.InMemoryChannelLayer'` if Redis import fails (line 291).
- **Layer state:** EPHEMERAL. Channels does not persist WS message payload; Redis is in-memory dispatch only. No `.schema.json` files for WS message types.

### 4.4 PA WS emission persistence (retention-impact surfaces)

- **WS events themselves (`message.created` + `agent.completed` + `rigby.tool.*`):** EPHEMERAL. Dispatched via Redis channel layer; NOT logged to DB. Channels is broadcast-only.
- **DB-side persistence:**
  - `message.created`: rows persisted DIRECTLY by caller to `ChatConversation` table BEFORE WS emit at `core/views_personal_assistant.py:567-579` (verified via Agent 2 emit-site enumeration). User posts create rows synchronously; WS emit is post-creation notification.
  - `agent.completed`: **dual persistence path** per Agent 1 evidence: (i) server-side eager write via `fire_agent_followup_subscriptions()` at `core/tasks_agents.py:410-465` (writes Rigby-authored ChatConversation row with `metadata={'kind': 'agent_completion', 'execution_id': ...}` — idempotent via metadata lookup per PR #2350 Session 1180); (ii) consumer-side fallback via `PAConversationConsumer.agent_completed()` at `core/consumers_pa_conversation.py:345` (calls `create_completion_row()` again with idempotent guard preventing duplicates).
  - `rigby.tool.*`: **NOT persisted** at emit time. Ticker events are live-only; `ToolCallRecord` is logged separately by `tool_dispatcher` post-execution (out of WS scope).
- **Retention window (inherited from Cat C §8.4 + §8.7):** `ChatConversation.get_or_create_session()` at `core/models/conversations/models.py:212` uses 24-hour hardcoded lookback (Cat C §8.7 F-C5 fold — mechanism constant, NOT policy declaration). `agent.completed` rows persist past 24h if session_active=False transitions occur.

---

## 5. Major Services

### 5.1 PAConversationConsumer runtime service (Cat B §6.2 canonical Consumer)

**Location:** `core/consumers_pa_conversation.py:175` — `class PAConversationConsumer(AsyncWebsocketConsumer)` (VC-1 primary Consumer at 372 total lines).

**Handshake auth chain (Agent 3 verified, VC-6):**
- Line 182: `self.user = self.scope.get("user")` (populated by TokenAuthMiddleware at ASGI layer per S2504 §3.3 baseline).
- Line 183-184: if `not self.user or isinstance(self.user, AnonymousUser)`: `await self.close(code=4001)` (VERIFIED explicit close-with-code — NOT silent-degrade).
- Line 189: if missing `conversation_id`: `await self.close(code=4002)` (VERIFIED second close-with-code discipline).
- Line 198: `await self.accept()` (otherwise).

**Group name pattern:** `pa_conversation_{conversation_id}` (Agent 3 verified). All 3 canonical PA WS message class handlers dispatch through this group.

**Handler methods on PAConversationConsumer:**
- `async def message_created(self, event)` — line 243 (broadcasts `message.created` events).
- `async def agent_completed(self, event)` — line 320 (dual-write agent.completed with idempotent fallback at line 345).
- `async def rigby_tool_started(self, event)` — line 274 (ticker for tool start lifecycle).
- `async def rigby_tool_completed(self, event)` — line 286 (ticker for tool completion lifecycle).

### 5.2 pa_status_events emit service (rigby.tool.* lifecycle emit)

**Location:** `core/services/pa_status_events.py` (Session 1172 seed).

- Line 104: `await layer.group_send(group, payload)` (VERIFIED emit path via Bash grep).
- Line 116-147: `emit_tool_started()` async — payload keys: `trace_id`, `seq`, `tool_call_id`, `tool_name`, `started_at`, `arg_summary`.
- Line 150-182: `emit_tool_completed()` async — payload keys: `trace_id`, `seq`, `tool_call_id`, `tool_name`, `latency_ms`, `status`, `result_summary`.

**Emit semantics:** fire-and-forget to `pa_conversation_{conversation_id}` group via `channel_layer.group_send(...)`. If channel layer unavailable, tool execution never blocks (fail-open per Agent 2).

### 5.3 tool_dispatcher invocation site

`core/services/tool_dispatcher.py:ToolDispatcher.execute()` calls `await emit_tool_started(...)` + `await emit_tool_completed(...)` inline during PA tool dispatch. Session 1172 seed pattern; `trace_id` threaded through dispatcher call chain enables client-side ticker dedup on reconnect.

### 5.4 fire_agent_followup_subscriptions Celery emit path (agent.completed broadcast)

**Location:** `core/tasks_agents.py:336-491` — sync function (no `@shared_task`); called from Celery task context.

Step-by-step flow (Agent 3 verified):
1. Line 384-394: atomic queryset update — `AgentFollowupSubscription.filter(state='armed', expires_at NULL|>now).update(state='fired')`.
2. Line 399-465: server-side persist BEFORE broadcast — resolves user, checks background-completion flag, calls `create_completion_row()` from `core.consumers_pa_conversation` (imports across module boundary).
3. Line 471-485: `async_to_sync(channel_layer.group_send)` broadcast to `pa_conversation_{conversation_id}` with `type="agent.completed"` + envelope keys `execution_id`, `agent_name`, `status`, `completed_at`, `error_signature`, `artifact_pointers`, `timestamp`.

**Task decorator:** `@shared_task(bind=True, base=AgentExecutionTask, max_retries=3)` (Agent 3 verified at line 493). No explicit `queue=` — uses default broker routing.

### 5.5 UnifiedPAEntrypoint god-service ranking (Agent 2 evidence)

- `core/services/unified_pa_entrypoint.py`: 7,613 lines (EXCEEDS 3000-line playbook §13 god-service threshold).
- Scope: `process_message` dispatch, context resolution, tool authorization. NOT WS-envelope specific but consolidated PA orchestration hub — WS emit is downstream of this service.
- Cat D observation: god-service exists; NOT Cat D-scope for refactor (Cat-D-6 anti-scope preserved).

### 5.6 Envelope-SoT registry service presence check

**Absent at HEAD `cf410660`.** No `core/services/ws_envelope_registry.py` or equivalent envelope-SoT coordination layer. Agent 2 grep-verified:
- `core/services/urc_envelope.py` (183 lines): unrelated (document/artifact envelope, not WS).
- `core/services/artifact_envelope.py`: artifact storage, not WS contract.
- Zero WS-message-shape registry / central schema store.

**F-D-WSENVELOPE-1 status at services layer:** ABSENT — S2504 §14.2 canonical baseline PRESERVED at PA slice.

---

## 6. Major APIs and Interfaces — F-D2 Canonical Artifact (AC-D2 canonical)

### 6.1 F-D2 fold canonical matrix (Rigby SIGN-preview STRENGTHEN 2026-07-06 + Chris "agree all" wholesale)

Per F-D2 fold ratified 2026-07-06: AC-D2 scope-clamp to **Cat B canonical 3 message classes + Cat D enumerated PA-related Consumer subset only** (NOT the platform-wide 87 Consumer classes / 120 WS routes — those remain S2504 §6.3 canonical, respected per Cat-D-3 anti-scope). For each entry, record: **(i) observed payload keys at HEAD**, **(ii) whether the observed shape matches any declared envelope contract (if present)**, **(iii) envelope-grade classification**. F4 target: 0 UNKNOWN on whether envelope contract is declared or absent.

#### 6.1.1 Cat B canonical 3-class × envelope-grade × strictness-disposition matrix (F-D-B1-1 + F-D-B1-4 folds baked)

**F-D-B1-1 fold ratified 2026-07-06 (Rigby SIGN cycle 1 Batch 1 Q1a STRENGTHEN, Chris "agree all" wholesale):** matrix extended with **Consumer(s)** column (transport-anchored) + **schema versioning** micro-field (versioned: yes/no — substitute for compile-time schema when Path C+observability-compensation selected).

**Aux events footnote (F-D-B1-1 fold):** `participant.typing` + `participant.joined` (Cat D §10.1 rows 2+3) are **intentionally excluded from the Cat B canonical 3-class denominator**; tracked separately in §10.1 as auxiliary events, not envelope-decision inputs. This exclusion prevents downstream reviewers from re-litigating "missing rows" as an omission — the denominator is F-B3 canonical + Cat D VC-1 evidence-perimeter distinction preserved.

| # | Class | Emit-site file:line | Consumer(s) parsing | (i) Observed payload keys at HEAD | (ii) Matches declared envelope contract? | (iii) Envelope-grade | Schema versioned? | Strictness-disposition eligibility |
|---|---|---|---|---|---|---|---|---|
| 1 | `message.created` (chat-response) | `core/views_personal_assistant.py:567-579` + `core/tasks_misc.py:4859-4881` + `core/services/claude_code_engineer.py:1203-1215` | `PAConversationConsumer.message_created()` at `core/consumers_pa_conversation.py:243`; client-side untyped parse at `frontend/src/pages/CommandCenterPage.tsx:747` | `type`, `message` {`id`, `role`, `content`, `source`, `[tools_used]`, `timestamp`} | **No declared envelope contract exists** (N-A per (ii); no `interface WSMessage*` or TypedDict) | **`observed-JSON-only`** | **no** (no shape-version field emitted) | Path A eligible (typed retrofit); Path B eligible (connect-only); Path C+observability-compensation eligible (SoT-declared, NON-STREAMING per F-D1 fold + VC-5 evidence — no carve-out justification available); **Path C-pure: HARD-INVALID / NON-SELECTABLE (per F5-analog)** |
| 2 | `agent.completed` (task-status broadcast) | `core/tasks_agents.py:473-485` (single canonical emit-site via `fire_agent_followup_subscriptions()`) | `PAConversationConsumer.agent_completed()` at `core/consumers_pa_conversation.py:320-372`; client-side untyped parse | `type`, `execution_id`, `agent_name`, `status`, `completed_at`, `error_signature`, `artifact_pointers`, `timestamp` | **No declared envelope contract exists** (N-A per (ii); server-side `create_completion_row()` persists metadata dict shape but no runtime validator) | **`observed-JSON-only`** | **no** (no shape-version field emitted) | Path A eligible; Path B eligible; Path C+observability-compensation eligible (SoT-declared, always non-streaming); **Path C-pure: HARD-INVALID / NON-SELECTABLE (per F5-analog)** |
| 3 | `rigby.tool.started` + `rigby.tool.completed` (tool-ticker lifecycle) | `core/services/pa_status_events.py:116-147` (started) + `pa_status_events.py:150-182` (completed) — 2 async emit functions | `PAConversationConsumer.rigby_tool_started()` at `consumers_pa_conversation.py:274` + `rigby_tool_completed()` at line 286; client-side dedup via `(trace_id, seq)` at `frontend/src/stores/paStore.ts` | started: `type`, `trace_id`, `seq`, `tool_call_id`, `tool_name`, `started_at`, `arg_summary`; completed: `type`, `trace_id`, `seq`, `tool_call_id`, `tool_name`, `latency_ms`, `status`, `result_summary` | **No declared envelope contract exists** (N-A; `ToolTickerEvent` inline interface at `paStore.ts:49-77` is Zustand store state shape, NOT WS envelope SoT — Cat B §6.2 evidence + Agent 1 verified) | **no** (no shape-version field emitted) | **`observed-JSON-only`** | Path A eligible; Path B eligible; Path C+observability-compensation eligible (SoT-declared, always non-streaming — tool lifecycle is discrete events, not streaming); **Path C-pure: HARD-INVALID / NON-SELECTABLE (per F5-analog)** |

**F4 target achievement:** 3-of-3 entries with **0 UNKNOWN on whether envelope contract is declared or absent** for the Cat B canonical denominator (matches F-D2 fold F4 target). All 3 classes at HEAD `cf410660` are UNVERSIONED — if Chris-D-verdict at S2699 xx99 selects Path C+observability-compensation, `versioned: yes` field becomes REQUIRED per AC-D4 spec (envelope-shape telemetry emit-signature MUST include shape-version for compat tracking).

#### 6.1.2 Cat D PA-related Consumer subset × envelope emit-signature matrix (VC-1)

| # | Consumer class | File:line | Consumer-level envelope declaration | Emit-signature type annotation | Envelope-grade | Sample status (F-D-B1-2 fold) |
|---|---|---|---|---|---|---|
| 1 | `PAConversationConsumer` | `core/consumers_pa_conversation.py:175` | None (no TypedDict / Protocol / BaseModel at class scope) | Emit sites (lines 245-248 + 274-284 + 286-297 + 363-372): `await self.send(text_data=json.dumps({...}))` — inline dict literals, no type annotation | `observed-JSON-only` (VC-4 verified) | **F4-met** (Cat B canonical denominator) |
| 2 | `PersonalAssistantConsumer` (via V2 alias) | `core/consumers_unified_v2.py:20` | UNKNOWN (Consumer body not read in full at S2604 opening — Agent 3 deferred; verifier-loop next-step) | UNKNOWN | UNKNOWN (§20.4 next-verify) | **VC-1 partial sample DEBT (bounded, pointer-ready)** |
| 3 | `AssistantChatConsumer` | `core/consumers_base.py:390` | UNKNOWN (Consumer body not read in full) | UNKNOWN | UNKNOWN (§20.4 next-verify) | **VC-1 partial sample DEBT (bounded, pointer-ready)** |
| 4 | `PersonalAssistantConsumer` (direct) | `core/personal_assistant_consumer.py:14` | UNKNOWN (Consumer body not read in full) | UNKNOWN | UNKNOWN (§20.4 next-verify) | **VC-1 partial sample DEBT (bounded, pointer-ready)** |

**Denominator-scope UNKNOWN caveat (F-D-B1-2 fold ratified 2026-07-06 — Rigby SIGN cycle 1 Batch 1 Q1b STRENGTHEN, Chris "agree all" wholesale):** Cat D S2604 verifies Consumer #1 (PAConversationConsumer — Cat B canonical) at HEAD. Consumers #2-4 have **UNKNOWN on Consumer-level envelope declaration + emit-signature** at Cat D open, explicitly labeled as **VC-1 partial sample DEBT (bounded, pointer-ready)** per F-D-B1-2 fold discipline. F4 target for Cat D scope MET for Cat B canonical row (Consumer #1); Consumers #2-4 UNKNOWN is with-pointer.

**Close condition (F-D-B1-2 fold):** *"Cat D close does not require exhausting Consumer #2-4 verification; it requires preserving pointers (§20.4 next-verify entries) and preventing false claims of coverage. VC-1 is perimeter inventory; §6.1.2 rows 2-4 are DEBT (DEBT-D-2), not F4 gaps. Chris-D-verdict at S2699 xx99 may proceed on Cat B canonical denominator alone; Consumers #2-4 are post-arc T-slot follow-on candidates."*

### 6.2 Envelope-grade classification key

Per S2504 §14.2 F-D-WSENVELOPE-1 canonical vocabulary + Cat D convention:
- **`observed-JSON-only`** — shape observed at emit-site; no declared contract (TypedDict / Protocol / BaseModel / TypeScript interface) enforces or documents the shape at HEAD. Client-side parse is `data as {...}` untyped assertion.
- **`island-declared`** — envelope contract declared at CONNECT handshake OR consumer class body (Python) OR consumer subscription hook (TypeScript) but NOT SoT-registered platform-wide.
- **`SoT-declared`** — envelope contract declared at platform-wide envelope-SoT registry (e.g., hypothetical `core/services/ws_envelope_registry.py`) with runtime validator + client-side conformance check.

### 6.3 REST↔WS parallel delivery pattern evidence (Cat B §7.1 inheritance + Agent 4 verified)

Per Cat B §7.1 (`docs/research/domains/pa/2602_pa_client_contract_surface_design_prep_audit.md:556-575`) + Agent 4 evidence:

**Task completion fires via BOTH channels in parallel:**
- **REST poll (Cat A §7.3 evidence):** `/api/pa/chat/status/<task_id>/` returns `{"success": T/F, "status": "completed|failed|processing", **task_result}` at 200 status. Client-side polling at N-second interval.
- **WS broadcast (Cat D §5.4 + §7.2 evidence):** `agent.completed` event via `fire_agent_followup_subscriptions()` → `pa_conversation_{conversation_id}` group.

**Client-side dedup pattern:**
- `paStore.ts:68 seenCompletions: string[]` — 50-item bounded ring (partialize via `.slice(-50)` at line 113 per Agent 6 evidence).
- Dedup key: `execution_id`.
- **NO server-side reconciliation logic at HEAD** — Cat B §7.1 evidence: "REST polling + WS broadcast are PARALLEL delivery channels ... UI treats them additively; Session 1175/1181 pattern seed."

**Cat D observation:** parallel-delivery reconciliation gap is Cat D scope for T7 cross-transport consistency check (§7.4 AC-D5 canonical). Reconciliation-layer ownership is UNOWNED at HEAD; candidates: Group 1700 Observability + Cat D S2604 handoff (§18.2).

### 6.4 Cat A §6.1 F11 canonical REST endpoint inventory (CITED — NOT re-inventoried per Cat-D-9 + Cat-D-3)

Cat A §6.1 F11 canonical 34-row PA-path REST endpoint inventory is upstream input for T7 cross-transport consistency check. Cat D §7.4 AC-D5 references Cat A §6.1 rows 16-17 (`POST /api/pa/chat/` + `GET /api/pa/chat/status/<task_id>/`) for the REST-side of probe 1 (streaming semantics) + probe 2 (task-status polling contract).

---

## 7. Runtime Flows

### 7.1 `message.created` flow (F-D1 fold conditional VERIFIED non-streaming — VC-5)

Per Agent 2 + parent-Claude verifier-loop:

1. User posts message via REST `POST /api/assistant/conversations/<id>/messages/` (`pa_conversation_post_message` at `core/views_personal_assistant.py:521`) OR `unified_pa_chat()` at line 267.
2. Message persisted to `ChatConversation` table BEFORE WS emit (line 567 evidence).
3. `async_to_sync(channel_layer.group_send)("pa_conversation_{conversation_id}", {"type": "message.created", "message": {...}})` fires (line 567-579).
4. Django Channels routes `message.created` type → `PAConversationConsumer.message_created()` at `core/consumers_pa_conversation.py:243`.
5. `await self.send(text_data=json.dumps({type, message}))` — **atomic send per event** (line 245-248).
6. WS frame reaches connected client; JavaScript parses via `event.type === 'message.created'` check at `CommandCenterPage.tsx:747` (untyped `data as {message: {...}}` assertion).

**F-D1 fold streaming-absence VERIFICATION (VC-5):**
- Parent-Claude grep for `StreamingHttpResponse` in `core/views_personal_assistant.py` → **ZERO matches**.
- Parent-Claude grep for `text/event-stream` in same file → **ZERO matches**.
- Parent-Claude grep for `Transfer-Encoding.*chunked` → **ZERO matches**.
- Agent 2 verified: no iteration in emit path; all `message.created` emit sites construct single dict with full `content` field (no loop, no partial-message iteration, no chunk emission).

**F-D1 fold verdict at HEAD `cf410660`:** `message.created` delivers **BUFFERED COMPLETE MESSAGES**, not token-by-token or chunked incremental content. Per F-D1 fold conditional clause: **Path C+carve-out collapses to Path C (non-streaming) at Cat D S2604** — the streaming carve-out is NOT justified by evidence at HEAD.

### 7.2 `agent.completed` flow (dual-persistence idempotent per Agent 1)

1. `AgentExecution` reaches terminal state (completed / failed / error).
2. `_impl_execute_agent_task()` in `core/tasks_agents.py` (multiple call sites: 2362 / 2730 / 2811 / 2838) calls `fire_agent_followup_subscriptions(execution_record)` at line 336.
3. Line 384-394: atomic queryset update — `AgentFollowupSubscription.filter(state='armed', expires_at NULL|>now).update(state='fired')`.
4. Line 399-465: **server-side eager persist** — `create_completion_row()` writes Rigby-authored `ChatConversation` row with `metadata={'kind': 'agent_completion', 'execution_id': ...}` (idempotent via metadata_contains lookup per PR #2350 Session 1180).
5. Line 471-485: `async_to_sync(channel_layer.group_send)("pa_conversation_{conversation_id}", {"type": "agent.completed", **envelope_keys})` — envelope keys per §6.1.1 row 2.
6. `PAConversationConsumer.agent_completed()` at `core/consumers_pa_conversation.py:320-372` fires:
   - Consumer-side fallback persist (idempotent guard prevents duplicate row) — Session 1175 PR-2b-2 design.
   - `await self.send(text_data=json.dumps({...}))` broadcasts WS frame to client.
7. Client renders live banner + updates chat history via `paStore.seenCompletions` dedup (`execution_id` key).

**Cat D observation:** dual-persistence pattern (server-side + consumer-side) survives browser tab dedup + page-refresh (Session 1180 rationale). Idempotency via `metadata__contains` at row level; no conflict risk at DB layer. WS emit is fail-open at consumer (persistence exception ≠ broadcast exception per Agent 6).

### 7.3 `rigby.tool.*` lifecycle flow (Session 1172 seed)

1. PA pipeline calls `tool_dispatcher.execute(..., pa_trace_id, conversation_id)` at PA tool dispatch site.
2. On tool start: `emit_tool_started()` queues `seq` via `_next_seq(trace_id)` at `core/services/pa_status_events.py:116-147`. Payload: `type`, `trace_id`, `seq`, `tool_call_id`, `tool_name`, `started_at`, `arg_summary`.
3. Line 104: `await layer.group_send("pa_conversation_{conversation_id}", payload)` — fire-and-forget.
4. `PAConversationConsumer.rigby_tool_started()` at line 274-284 broadcasts frame to client via `await self.send(text_data=json.dumps({...}))`.
5. On tool completion: `emit_tool_completed()` similar pattern at `pa_status_events.py:150-182`. Payload adds `latency_ms`, `status`, `result_summary`.
6. `PAConversationConsumer.rigby_tool_completed()` at line 286-297 broadcasts frame.
7. Client dedupes via `(trace_id, seq)` tuple + renders tool ticker.

**Cat D observation:** `_next_seq()` uses per-process in-memory counter with FIFO eviction at 1024 traces (Agent 2 evidence). Seq wraparound risk across process boundaries is UNKNOWN at Cat D scope (§20.4 next-verify). Fail-open semantics: if channel layer unavailable, tool execution proceeds (never blocks).

### 7.4 T7 cross-transport consistency check per parent §5.3 AC#8 F12 fold (AC-D5 canonical)

Per parent §5.3 AC#8 F12 fold discipline: for each of the 3 parent §3.5 PA-adjacent probes, Cat D produces an explicit REST-side + WS-side request/response/envelope sketch AND a stated consistency rule across REST↔WS.

#### 7.4.1 Probe 1 — `/pa/chat/` streaming semantics

| Transport | Statement | Evidence | Envelope shape |
|---|---|---|---|
| **REST-side** | "task-based async; NO streaming" | Cat A §7.2 canonical verified (`docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md:391-400`) | `{"success": True, "task_id": "<uuid>", "status": "processing"}` at 200 (Cat A §7.3 evidence) |
| **WS-side** | `message.created` delivers **BUFFERED COMPLETE MESSAGES**, NOT streaming (F-D1 fold VERIFIED per VC-5) | Cat D §7.1 evidence + Agent 2 streaming-machinery verdict + parent-Claude grep on `StreamingHttpResponse` / `text/event-stream` / `Transfer-Encoding: chunked` all ZERO | `{type: 'message.created', message: {id, role, content, source, [tools_used], timestamp}}` (Cat B §6.2 F-B3 canonical) |
| **Consistency rule** | REST + WS are **BOTH NON-STREAMING at PA-slice**. `message.created` is buffered emit (post-persist notification), not chunked delivery. Path C+carve-out at Cat D **collapses to Path C non-streaming** per F-D1 fold conditional. |

#### 7.4.2 Probe 2 — Task-status polling contract at `/pa/chat/status/<id>/`

| Transport | Statement | Evidence | Envelope shape |
|---|---|---|---|
| **REST-side** | Polling body at 200 status: `{"success": T/F, "status": "completed\|failed\|processing", **task_result}` | Cat A §7.3 canonical verified | `{"success": True, "status": "completed", **task_result}` (Cat A §7.3) |
| **WS-side** | `agent.completed` broadcast envelope | Cat D §7.2 + Cat B §6.2 F-B3 canonical | `{type: 'agent.completed', execution_id, agent_name, status, completed_at, error_signature?, artifact_pointers?, timestamp?}` |
| **Consistency rule** | REST + WS are **PARALLEL delivery channels** for task completion signal. Client-side dedup only via `paStore.seenCompletions` ring at `paStore.ts:68` (50-item bounded, keyed on `execution_id`). **NO server-side reconciliation logic at HEAD** — Cat B §7.1 canonical statement + Agent 4 evidence. **T7 CONSISTENCY GAP:** parallel-delivery reconciliation is UNOWNED at HEAD — Cat D §18.2 handoff to Group 1700 Observability T4 arc for envelope-shape telemetry + reconciliation-layer ownership. |

#### 7.4.3 Probe 3 — WS channel authentication handshake

| Transport | Statement | Evidence | Envelope shape |
|---|---|---|---|
| **REST-side** | `@permission_classes([IsAuthenticated])` uniformly at all 34 PA-path endpoints + DRF Family A `{"detail"}` 401 shape | Cat A §6.1 F11 canonical verified | Family A: `{"detail": "Authentication credentials were not provided."}` at 401 |
| **WS-side** | `TokenAuthMiddlewareStack` (S2504 §3.3 baseline) + silent-degrade AnonymousUser fallback at middleware layer + **explicit close-with-code 4001 at PAConversationConsumer.connect() line 184** (VC-6 verified) | Cat D §5.1 + Agent 3 + parent-Claude grep at `core/consumers_pa_conversation.py:183-184` | close code 4001 (no envelope body — close frame) |
| **Consistency rule** | REST 401 + WS close(4001) are **STRUCTURALLY DIFFERENT** (REST returns typed HTTP response envelope; WS closes connection with numeric code). PA Consumer is EXCEPTION to platform WS silent-degrade default (per S2504 §5.3 canonical: "silent-degrade at middleware layer; per-consumer discretion"). **T7 CONSISTENCY OBSERVATION:** PA explicitly rejects unauthenticated WS connect via close(4001), rather than accepting anonymous with per-message downgrade — this is a stronger auth-boundary than the platform default. Documented in Cat B §16.1 F-B10 fold (Cat B §16.1 attribution). |

---

## 8. Data Ownership and Lifecycle

### 8.1 PA WS ephemeral vs persisted state

Per Agent 1 verified evidence:

| Data class | Lifecycle | Persistence tier |
|---|---|---|
| WS events (`message.created`, `agent.completed`, `rigby.tool.*`) | EPHEMERAL — Redis channel-layer dispatch only | NOT persisted; Channels is broadcast-only |
| `ChatConversation` rows (message.created + agent.completed persistence) | DB-persisted; scoped by `session_active` + 24h resumption window | PostgreSQL primary; retention per Cat C §8.7 F-C5 mechanism-constant hardcoded |
| `AgentFollowupSubscription` state | DB-persisted; state='armed' → 'fired' → 'expired' → 'cancelled' | PostgreSQL |
| `ToolCallRecord` (post-hoc log) | DB-persisted post-execution | PostgreSQL; NOT WS-emit-tied |
| Client-side `paStore.seenCompletions` ring | localStorage OR memory (paStore partialize per Cat B §4.1) | Bounded 50-item ring; TTL: none, evict via `.slice(-50)` |
| Client-side `activeTool` / `recentTool` / `seenSeqs` | Memory-only (Cat B §8.4) | Component unmount / page refresh |

### 8.2 Retention window inheritance from Cat C §8.7

Cat D INHERITS Cat C §8.7 retention window declarations (`docs/research/domains/pa/2603_pa_workspace_authz_session_lifecycle_design_prep_audit.md:542-553`) as upstream input. Cat D does NOT re-litigate C2 retention verdict per Cat-D-4 anti-scope-analog (C2 is Cat C2-owned).

**Retention-window at HEAD (Cat C canonical):**
- `ChatConversation` session resumption: 24-hour lookback hardcoded at `core/models/conversations/models.py:212` (F-C5 mechanism constant, NOT policy declaration).
- `AgentFollowupSubscription` TTL: `DEFAULT_TTL_SECONDS=60` + `MAX_TTL_SECONDS=600` at `core/models_unified_system.py:1063-1065` (documented via docstring; not cascade to user-logout).
- PA WS ephemeral events: no retention (channel-layer broadcast only).

### 8.3 T7 cross-transport parallel-delivery reconciliation gap (§7.4.2 canonical)

Cat D observation (per §7.4.2 + Cat B §7.1 canonical): REST poll + WS broadcast for `agent.completed` are PARALLEL delivery channels; client-side dedup via `paStore.seenCompletions` 50-item ring (`execution_id` key); **NO server-side reconciliation logic at HEAD**. This is a T7 cross-transport consistency GAP (§14.2 D2 debt).

**Cat D coupling axis to Group 1700 Observability T4 (§18.2 handoff):** reconciliation-layer ownership is UNOWNED at HEAD. If Cat D S2699 xx99 selects Path A (typed envelope) or Path C+observability-compensation, envelope-shape telemetry + parallel-delivery reconciliation logic are candidates for Group 1700 T4 arc scope declaration.

---

## 9. Integrations With Other Domains

### 9.1 Integration classification matrix (per Agent 4)

Per playbook §12 vocabulary + Agent 4 evidence:

| Pair | Strength | Rationale |
|---|---|---|
| PA ↔ Group 2500 API (S2504 CF-D6 REST↔WS T7 joint) | **DUAL-OWNED** | Both REST + WS routes under same chat endpoint; shared `conversation_id` group name; single token auth model; **BUT** message-contract strictness is NOT synchronized (REST typed envelope ≠ WS raw dict). S2504 §18.2 + R10 dual-owner declaration canonical. Cat D S2604 owns PA-slice application. |
| PA ↔ Group 2400 Auth (TokenAuthMiddlewareStack + WS handshake) | **STRONG** | `TokenAuthMiddlewareStack` wraps `AuthMiddlewareStack` at ASGI layer (S2504 §3.3 canonical). DRF Token model shared. `PAConversationConsumer.connect()` explicit close(4001) at line 184 EXCEPTION to platform silent-degrade default (Cat B §16.1 F-B10 fold — stronger auth-boundary at PA). |
| PA ↔ Group 2300 Mobile (parallel arc, secondary stakeholder per parent §3.D) | **WEAK** | No mobile-specific PA WS client interception evidence at HEAD. Grep in `frontend/src` for literal WS route paths returned zero matches (likely dynamic URL construction). Mobile PA client (if it exists) uses same ASGI route; no platform-specific subscription branching detected at Cat D open. §20.4 next-verify. |
| PA ↔ Group 1700 Observability (envelope-shape telemetry + T4 arc, secondary stakeholder per parent §3.D) | **MISSING** | S2504 §7.4 measurement handoff canonical: "define a WS unauthorized-connect metric (attempts/week, anonymous fallbacks/week, per-consumer reject codes) to bound prevalence." Cat D §18.2 extends to envelope-shape telemetry + per-Consumer conformance metrics. PA WS emit path (Cat D §5.2) fires zero telemetry to Group 1700 measurement layer at HEAD. |
| PA ↔ Group 1300 Memory (embeddings adjacent) | **ADJACENT (NO DIRECT WS EMIT)** | `PAConversationConsumer.create_completion_row()` writes `ChatConversation` directly (Agent 1 evidence). `ChatConversation` has zero `post_save` signals (Session 1175 Q-C investigation confirmed per `core/consumers_pa_conversation.py:129` docstring: "the write is fire-and-forget — no token/embedding/unread side effects to mirror"). Currently decoupled. |
| PA ↔ Group 1600 Content (content pipeline) | **ADJACENT (FRONTEND-ONLY CONSUMPTION)** | `message.created` + `agent.completed` WS events consumed by React ChatUI frontend only. Zero backend content-pipeline subscribers found (grep: 0 matches in content/models.py, content/tasks.py, content/consumers.py). PA content-dispatch is REST POST-triggered, not WS-emit-triggered. |

### 9.2 Cross-arc coordination flags status at S2604 close

- **CF-D6** (S2504 §18.2 + R10): Cat D S2604 owns PA-side application per parent §3.D. Cat D output (§6.1 canonical F-D2 matrix + §7.4 T7 consistency rule) delivers PA-side inheritance to xx99 for Chris-D-verdict.
- **CF-2600-PA** (S2501 Cat A): out-of-scope for Cat D (Cat A-owned). Cat D cites Cat A §6.1 F11 canonical + §7.2 REST-side statement.
- **F-B-HIGH-3** (S2402 preserved): out-of-scope for Cat D (Cat C1-owned per parent §5.3 AC#3 + Cat-D-5 anti-scope). Cat D §9.3 records coupling axis only per AC-D6.
- **CF-C2** (S2503): out-of-scope for Cat D (Cat C2-owned). Cat D inherits Cat C §8.7 retention window.

### 9.3 Cat C1 coupling axis pressure-test evidence (per AC-D6)

**Question:** Does WS auth layer at PA (`PAConversationConsumer.connect()`) share ANY code path with REST-side workspace-context authz at `execute_with_workspace()`?

**Answer at HEAD `cf410660`: NO (disjoint code paths)** per Agent 4 verified evidence:

1. **WS connect() auth boundary** (`core/consumers_pa_conversation.py:181-200`): checks `self.user = self.scope.get("user")`; if `AnonymousUser` or missing → `await self.close(code=4001)`; scopes by `conversation_id` from URL route. **No workspace-membership check.**
2. **REST `execute_with_workspace()` auth boundary** (Cat C §7.2 canonical at `core/agents/base_agent.py:5355`): called by workspace-aware agents (20 in `WORKSPACE_AWARE_AGENTS`); resolves workspace via `WorkspaceManager.get_active_workspace()`; enforces membership check via implicit gate. **No shared utility function between WS + REST paths.**
3. **Scoping difference:** WS uses `conversation_id`; REST uses `workspace_id`. **No shared workspace-resolver.**
4. **DEBT-C1-8 (S2603 §2 canonical):** `PAConversationConsumer.connect()` does not resolve or enforce workspace context; `conversation_id` parameter alone gates access.

**AC-D6 statement per §7.4.3 + Cat C §7.2 AC-C1-4 inheritance:**

> *"At HEAD `cf410660`, PA WS-side workspace-context enforcement is NOT declared at handshake — `PAConversationConsumer.connect()` scopes by `conversation_id` (URL parameter) + user-authentication (TokenAuthMiddleware + close 4001 on AnonymousUser), NOT by workspace-membership. Cat C §7.2 AC-C1-4 REST-side statement paired with Cat D WS-side statement: PA REST-side is handler-internal implicit-gate at `execute_with_workspace()`; PA WS-side is NO workspace-context enforcement at all. Cat D + Cat C1 verdicts are ORTHOGONAL at HEAD — no coupling evidence surfaces. If Chris ratifies Cat C1 Path A (WorkspaceMember DRF class) at S2699 xx99, Cat D adopts symmetric WS-side WorkspaceMember-enforcement at connect handshake (natural coupling axis to consider); if Cat C1 Path C+compensating, Cat D adopts WS-side implicit-gate with compensating controls (envelope-shape telemetry + audit-log hook per Group 1700 T4 handoff)."*

---

## 10. Event Flows

### 10.1 Inbound event triggers (what fires PA WS emits)

Per Agent 4 verified evidence:

1. **`message.created`** ← REST `POST /api/assistant/conversations/<id>/messages/` (`pa_conversation_post_message`, `core/views_personal_assistant.py:567-579`)
2. **`participant.typing`** ← WS client `receive()` with `type='typing'` (`core/consumers_pa_conversation.py:227-237`) — auxiliary event, not Cat B F-B3 canonical
3. **`participant.joined`** ← WS client `connect()` (`core/consumers_pa_conversation.py:202-211`) — auxiliary event, not Cat B F-B3 canonical
4. **`rigby.tool.started`** ← async `emit_tool_started()` from `tool_dispatcher.execute()` (`core/services/pa_status_events.py:116-147`)
5. **`rigby.tool.completed`** ← async `emit_tool_completed()` from `tool_dispatcher.execute()` (`core/services/pa_status_events.py:150-182`)
6. **`agent.completed`** ← Signal handler `fire_agent_followup_subscriptions()` on `AgentExecution` terminal-state save; atomic queryset update on `AgentFollowupSubscription(state='armed')` (`core/tasks_agents.py:336-491`)

### 10.2 Outbound event consumers verified (per Agent 4)

- **React ChatUI frontend:** `useWebSocket()` hook (`frontend/src/hooks/useWebSocket.ts`); primary subscription at `frontend/src/pages/CommandCenterPage.tsx:682-764` per Cat B §6.2 F-B3 canonical.
- **Live tool ticker (rigby.tool.*):** Session 1172 chat UI banner/progress indicator (frontend only).
- **Completion banner (agent.completed):** Session 1175 PR-2b-2 live banner + persisted `ChatConversation` row (dual-write per §7.2).

### 10.3 Missing connections (per Agent 4)

| Missing Consumer | Should consume | Impact | Severity |
|---|---|---|---|
| Group 1700 Observability measurement bus | `agent.completed` + `rigby.tool.*` envelope-shape telemetry (measurement-bus-formatted) | No centralized observability for PA WS completion metrics; Group 1700 SoT (if exists) is blind to PA event volume, latency, status distribution | MEDIUM (S2504 §7.4 measurement-handoff canonical; Cat D §18.2 extends) |
| Content pipeline orchestrator | `message.created` (for content-extraction on user messages); `agent.completed` (for artifact-routing) | Content pipeline is REST-explicit-dispatch-driven (tools produce artifacts downstream); no WS-event-triggered content ingestion | LOW (current design: WS broadcast is read-only for frontend) |
| Memory embeddings pipeline | `agent.completed` + `message.created` | `ChatConversation` rows written to DB but zero `post_save` hook to embeddings layer; memory must poll or be explicitly triggered | LOW (explicit deferred coupling per Session 1175) |

### 10.4 Events that could be emitted (evidence for §19)

Group 1700 Observability T4 arc scope candidates (Cat D handoff-only per Cat-D-8 anti-scope):
- `pa.ws.envelope.conformance.grade` — per-Consumer envelope conformance metric.
- `pa.ws.unauthorized_connect.count` — extends S2504 §7.4 measurement-handoff (WS unauthorized-connect metric).
- `pa.ws.emit.latency_histogram` — per-canonical-class emit latency.
- `pa.ws.agent_completed.reconciliation_delta` — REST-poll vs WS-broadcast timing delta at client-side dedup.

---

## 11. Existing Documentation

### 11.1 Topic doc coverage classification (per Agent 5)

| Doc | Coverage | Evidence |
|---|---|---|
| `docs/topics/personal-assistant.md` | **NONE** on PA WS layer | Extensive PA architecture docs (function calling, tool schemas, enrichment, async processing, cost) — **zero WS mentions**. PA documented purely from REST/Celery perspective. |
| `docs/topics/frontend.md` | **LIGHT** on PA WS | Lines 61-71 mention `GlobalPADock` + REST POST; sub-section on WebSocket Consumer Surface (lines 117-126) is generic (~20% PA coverage in 8 sites / 40 consumers) but NOT PA-specific. |
| `docs/topics/celery-workers.md` | **NONE** on PA WS | Lines 298-306: "PA async: polling every 2s; latency 3-64s" — polling documented as primary, WS streaming absent from doc claims. |
| `docs/topics/infrastructure.md` | **NONE** on PA WS specificity | ASGI + Redis 3-DB + Django + pgvector; line 12 "Channel layer uses default" — no PA-specific channel config, no PA Consumer registration. |

### 11.2 Prior research library entries (per Agent 5)

| Entry | Relevance |
|---|---|
| `docs/research/domains/api/2504_api_permission_floor_registry_rest_ws_t7_joint_design_prep_audit.md` §3.3 + §5.3 + §6.3 + §14.2 + §18.2 + R10 | **CF-D6 ORIGIN** — Group 2500 side of dual-owner arrangement; Cat D S2604 PA-slice inherits + applies. |
| `docs/research/domains/pa/2602_pa_client_contract_surface_design_prep_audit.md` §6.2 + §6.3 + §7.1 + §15.2 + §16.4 | **Cat B canonical** — U6 WS envelope inventory (F-B3) + REST-embedded audio_url + REST↔WS parallel delivery + CF-D6 debt + Cat-B-1..9 anti-scope precedent |
| `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md` §6.1 + §7.2 + §16.1 | **Cat A canonical** — F11 34-endpoint inventory + REST-side "task-based async; NO streaming" statement + F-B-HIGH-3 attribution |
| `docs/research/domains/pa/2603_pa_workspace_authz_session_lifecycle_design_prep_audit.md` §7.2 + §8.7 + §16.1 | **Cat C canonical** — AC-C1-4 T7 REST-side statement + retention window + F5+F-C7 hard "INVALID" analog for Path C-pure |
| `docs/research/domains/frontend/2202_frontend_websocket_consumer_ui_render_hint_envelope_audit.md` §14 F3 | **S2099 F16 baseline** — 0/40 emit sites conform to `ui.render_hint` envelope contract |
| `docs/research/domains/observability/1704_observability_cat_d_tool_call_record_audit.md` §8.3 + §14.4 | **Session 1172 emission pattern** — `pa_status_events.py` `rigby.tool.*` UI-ticker semantics; joined by `pa_trace_id` |
| `docs/research/domains/auth/2401_authentication_surface_trust_boundaries_audit.md` §6.2 + §14.2 | **PA WS auth exception** — PAConversationConsumer close(4001) discipline vs platform silent-degrade default |

### 11.3 Prior handoffs mentioning PA WS (recent 30)

Per Agent 5 grep on `docs/handoffs/SESSION_*.md` for PA WS keywords:
- `SESSION_2603_PA_CAT_C_WORKSPACE_AUTHZ_SESSION_LIFECYCLE.md` — AC-C1-4 delegated WS-side to Cat D.
- `SESSION_2602_PA_CAT_B_CLIENT_CONTRACT_SURFACE.md` — F-B3 canonical WS envelope inventory.
- `SESSION_2202_FRONTEND_WEBSOCKET_CONSUMER_UI_RENDER_HINT_ENVELOPE_AUDIT.md` — R5 PA WS↔polling consolidation follow-on.
- `SESSION_1172_RIGBY_LIVE_TOOL_STATUS.md` — Session 1172 seed; PAConversationConsumer.rigby_tool_{started,completed} wiring.
- `SESSION_1174_FOLLOWUP_WAKE_PR1_SHIP.md` — PAConversationConsumer.agent_completed handler.
- `SESSION_1175_AGENT_FOLLOWUP_DEMO.md` — agent.completed dual-write persistence + metadata.kind bubble badge.
- `SESSION_1262_CLAUDE_CODE_TASK_RECEIPT_RELIABILITY.md` — PAConversationConsumer.agent_completed real authenticated user.

---

## 12. Research Coverage

Per playbook §12 vocabulary + Agent 5 evidence:

- **PA WS envelope-shape SoT declaration:** **NONE** in topic docs (zero WS mentions at `docs/topics/personal-assistant.md`); **MODERATE** in prior research library (S2504 CF-D6 ORIGIN + Cat B §6.2 F-B3 canonical + S2202 F3 preserved).
- **PA WS handshake auth close-with-code discipline:** **LIGHT** — S2401 §6.2 documents close(4001) exception; not surfaced in topic docs.
- **PA WS streaming semantics:** **NONE** in topic docs; **LIGHT** in prior research (Cat A §7.2 REST-side statement partially covers via absence).
- **REST↔WS parallel delivery reconciliation:** **LIGHT** — Cat B §7.1 evidence baseline; not surfaced in topic docs.

**Overall PA WS-layer research coverage classification: MODERATE (prior research library) + NONE-to-LIGHT (topic docs).**

---

## 13. Architecture Maturity

Per playbook §12 vocabulary + §13.5 correctness-vs-governance-axis framing (Cat C §13 precedent):

### 13.1 PA WS-layer maturity (F-D-B1-5 fold — 3-axis split ratified 2026-07-06)

**F-D-B1-5 fold ratified 2026-07-06 (Rigby SIGN cycle 1 Batch 1 Q2a STRENGTHEN, Chris "agree all" wholesale):** §13 split from 2 axes (mechanism/declaration) into **3 axes: (i) Mechanism (runtime correctness), (ii) Declaration (envelope SoT / typed contracts), (iii) Observability (shape telemetry + enforcement signals)**. Rationale: Path C+observability-compensation is a real branch in the decision tree — making observability a first-class axis reduces hand-waving + improves internal consistency with §5.2 telemetry references + §10.3-§10.4 Group 1700 handoff references.

| # | Axis | Rating | Rationale |
|---|---|---|---|
| (i) | **Mechanism (runtime correctness)** | **WORKING** | PAConversationConsumer.connect() explicit close-with-code discipline (4001 anonymous / 4002 missing conversation_id / accept otherwise per §5.1 evidence). 3 canonical PA WS message classes emit + persist correctly per §7 flows. `fire_agent_followup_subscriptions()` atomic + idempotent dual-persistence. Fail-open channel-layer semantics. No runtime failure observed. |
| (ii) | **Declaration (envelope SoT / typed contracts)** | **EXPERIMENTAL** | Zero TypedDict / Protocol / BaseModel / dataclass declared at PA WS Consumer layer (VC-4). Zero TypeScript interface for 3 canonical WS message classes at client-side parse (Cat B §6.2 evidence). Zero envelope-SoT registry service (§5.6). F-D-WSENVELOPE-1 PA-slice preservation VERIFIED. This is not "partial declaration"; it's essentially **declaration absent** at the WS envelope boundary. |
| (iii) | **Observability (shape telemetry + enforcement signals)** | **EXPERIMENTAL / ABSENT** | Zero envelope-shape telemetry to Group 1700 (§10.3 missing-consumers finding). Zero shape-version fields emitted at any of the 3 canonical classes (§6.1.1 versioned=no all rows). No `pa.ws.envelope.conformance.grade` metric (§10.4 T4 candidate). No `pa.ws.unauthorized_connect.count` metric extension of S2504 §7.4 baseline. No `pa.ws.emit.latency_histogram` per-canonical-class. If Path C+observability-compensation ratified at xx99, observability axis moves from ABSENT → REQUIRED per AC-D4 spec. |
| — | **Overall PA WS-layer maturity** | **PARTIAL** | MECHANISM WORKING + DECLARATION EXPERIMENTAL + OBSERVABILITY EXPERIMENTAL/ABSENT. Cat D Chris-D-verdict at S2699 xx99 determines DECLARATION + OBSERVABILITY upgrade path (Path A / Path B / Path C+observability-compensation; **Path C-pure: HARD-INVALID / NON-SELECTABLE per F5-analog**). |

**Distinguish from Cat A §13 endpoint-declaration maturity:** Cat A assessed PA REST-endpoint contract-SoT at PARTIAL (0/34 @extend_schema at HEAD). Cat B assessed PA-client contract typing at PARTIAL (5/20 assistantApi typed = 25%). Cat C assessed workspace-context authz + session-lifecycle at PARTIAL both. Cat D assesses ENVELOPE-DECLARATION-layer + T7 CROSS-TRANSPORT-CONSISTENCY-layer + OBSERVABILITY-layer at PARTIAL overall (with per-axis grades per F-D-B1-5 fold). All four sibling Cat verdicts converge on PARTIAL — MECHANISM working + DECLARATION experimental across all 4 sub-domains. This is the Group 2600 arc characteristic pattern; xx99 canonical summary synthesizes.

---

## 14. Known Drift

### 14.1 Drift resolved by verifier-loop pre-draft (7 corrections)

Per playbook §14 discipline: "Direct source verification for important findings" + "Grep-verify binary claims before shipping to Rigby." Parent-Claude verifier-loop 7-correction chain applied pre-draft (§20.6 full ledger):

- **VC-1** Cat D PA-related Consumer inventory EXPANDED beyond Cat B canonical 1-channel to **4 distinct classes** (subset of platform 87 per S2504 §6.3): PAConversationConsumer + PersonalAssistantV2Consumer (via alias) + AssistantChatConsumer + PersonalAssistantConsumer (direct). Cat B §6.2 F-B3 was CLIENT-CONSUMED scope; Cat D is PA-RELATED scope (§3.1 above).
- **VC-2** PersonalAssistantConsumer naming collision at 2 files (`core/consumers_unified_v2.py:20` + `core/personal_assistant_consumer.py:14`) → §17.1 Duplicate/Overlapping systems.
- **VC-3** message.created/agent.completed/rigby.tool.* emit-site coverage: 6 files verified via grep — `core/services/claude_code_engineer.py`, `core/tasks_agents.py`, `core/tasks_misc.py`, `core/views_personal_assistant.py`, `core/consumers_pa_conversation.py`, `core/services/claude_code_agent.py`.
- **VC-4** F-D-WSENVELOPE-1 PA-slice preservation VERIFIED via grep for TypedDict/Protocol/BaseModel/@dataclass across `core/consumers*.py` — ZERO matches (§4.1).
- **VC-5** F-D1 fold streaming-absence CONFIRMED via grep for StreamingHttpResponse/text-event-stream/Transfer-Encoding-chunked in `core/views_personal_assistant.py` — ZERO matches (§7.1). Path C+carve-out collapses to Path C non-streaming per F-D1 fold conditional.
- **VC-6** CODEOWNERS at repo root (47 lines): PA WS Consumer files UNASSIGNED (default `* @clwest` only); `ws_auth_middleware.py` assigned at line 28; frontend PA WS surface (CommandCenterPage / paStore / useWebSocket) NOT covered per S2499 §7.4 Cat D F-D-OWN-1 remediation baseline (§18.1).
- **VC-7** `channels_graphql` ABSENT + `CHANNEL_LAYERS` at `core/settings.py:279-293` (Redis + InMemory fallback per Agent 1 correct).

### 14.2 Drift confirmed at HEAD (Cat D evidence)

- **D1: `docs/topics/frontend.md:65` claim "Rigby chat uses `POST /api/pa/chat/` everywhere"** — DRIFT confirmed at HEAD. `/ws/pa/conversations/<id>/` is primary real-time channel for web ChatUI per Cat B §6.2 F-B3 canonical + Agent 5 evidence. Polling is fallback for CLI wrapper (Cat B §6.2 evidence). Severity MEDIUM; §19.3 follow-on for docs cascade.
- **D2: `docs/topics/personal-assistant.md` §92-105 "PA async processing (Celery + polling)" positioning** — DRIFT confirmed at HEAD. WS streaming on `message.created` provides sub-second updates per Cat B §7.1 canonical; polling is secondary reconciliation. Doc positions polling as primary. Severity HIGH; §19.3 follow-on for docs cascade.
- **D3: `docs/topics/celery-workers.md:298-306` "PA async: polling every 2s; latency 3-64s"** — DRIFT confirmed at HEAD. Latency claim omits WS streaming behavior (buffered non-streaming per F-D1 fold + §7.1); perceived latency to user is WS-broadcast latency + final completion, not polling-only. Severity HIGH; §19.3 follow-on for docs cascade.
- **D4: `docs/topics/infrastructure.md:12` "Channel layer uses default"** — DRIFT partial. `CHANNEL_LAYERS` at `core/settings.py:279-293` (Redis primary + InMemory fallback per VC-7) — declarative config exists but topic doc suggests generic default. Severity LOW; documentation-gap not runtime-drift.
- **D5: Cat B §14.2 tool-schema-count drift (104 in personal-assistant.md:13 vs 109 vs 101 in PLATFORM_WHAT_IT_IS.md vs runtime 113)** — INHERITED from Cat A §14.2 + Cat B §14.2 + Cat C §14.2; PRESERVED at HEAD. Not Cat D-scope but noted for docs cascade completeness.

### 14.3 Drift observation from Agent 6 verify_doc_claims cross-check

Per Agent 6 evidence: `verify_doc_claims` at HEAD does NOT surface any PA WS envelope claim OR PA WS Consumer maturity claim. Declaration-layer drift detection for PA WS is UNMONITORED at HEAD. Cat D records + §19.3 follow-on: register PA WS envelope-shape claims for future drift detection.

---

## 15. Known Technical Debt

### 15.1 PA WS envelope-SoT declaration debt (Cat D boundary scope) — F-D-B2-1 + F-D-B2-2 + F-D-B2-3 + F-D-B2-4 folds baked

Per Agent 6 debt matrix + parent-Claude verifier-loop + Rigby SIGN cycle 1 Batch 2 STRENGTHEN folds ratified 2026-07-06 (Chris "agree all" wholesale):

| Debt item | file:line | Severity | finding_type | Cat D closure requirement |
|---|---|---|---|---|
| **DEBT-D-1** F-D-WSENVELOPE-1 PA-slice preservation (F-D-B2-1 fold: MEDIUM → **HIGH** + missing_connection → **missing_contract**) | `core/consumers_pa_conversation.py:242-298` (emit sites) + `core/services/pa_status_events.py:104-182` (emit) | **HIGH** | **missing_contract** | Cat D S2604 records evidence; Chris-D-verdict at S2699 xx99 selects Path A / Path B / Path C+observability-compensation. **Path C-pure: HARD-INVALID / NON-SELECTABLE (per F5-analog).** Severity HIGH per F-D-B2-1: PA WS is CLAUDE.md canonical operator entry-point + primary real-time surface for web ChatUI; envelope integrity is **high-leverage boundary**, not "average platform WS." |
| **DEBT-D-2** PA WS Consumer subset #2-4 envelope-declaration UNKNOWN (VC-1 partial sample) | `core/consumers_unified_v2.py:20` + `core/consumers_base.py:390` + `core/personal_assistant_consumer.py:14` | LOW | unknown | Verifier-loop next-step (§20.4). F-D2 fold F4 target met for Consumer #1 (Cat B canonical); Consumers #2-4 UNKNOWN is with-pointer per F-D-B1-2 close-condition discipline. Post-arc T-slot maintainer-decision batch candidate. |
| **DEBT-D-3** Envelope-shape telemetry emit-signature ABSENT | `core/services/pa_status_events.py` (candidate emit-point for Group 1700 handoff) | MEDIUM | missing_connection | Group 1700 Observability T4 arc scope declaration (Cat D §18.2 handoff-only per Cat-D-8 anti-scope). Cat D specifies emit-point candidates per AC-D8 canonical. |
| **DEBT-D-4** REST↔WS parallel-delivery reconciliation gap (F-D-B2-2 fold: MEDIUM → **HIGH** + closure text addition) | `frontend/src/stores/paStore.ts:68` (`seenCompletions` 50-item bounded ring) + `core/tasks_agents.py:473-485` (server-side emit — no cross-transport dedup marker) | **HIGH** | technical_debt | Cat D §7.4.2 canonical T7 consistency GAP; reconciliation-layer ownership UNOWNED at HEAD. **xx99 Path selection must explicitly choose a dedup/reconciliation posture (marker vs telemetry vs acceptance).** Severity HIGH per F-D-B2-2: user-visible risk (duplicate renders, missed completions, inconsistent UI state, "ghost" events) + silent failure mode. Group 1700 Observability T4 candidate. |
| **DEBT-D-5** PAConversationConsumer naming collision boundary | `core/consumers_unified_v2.py:20` + `core/personal_assistant_consumer.py:14` (VC-2) | LOW | overcoupling | §17.1 Duplicate/Overlapping systems; alias resolution via routing.py:27 avoids import collision but introduces cognitive-load drift. Post-arc T-slot maintainer-decision batch candidate. |
| **DEBT-D-6** PA WS Consumer files CODEOWNERS unassignment | `core/consumers_pa_conversation.py` + `core/consumers_unified_v2.py` + `core/consumers_base.py` + `core/personal_assistant_consumer.py` (all default @clwest via `*`) | LOW | unclear_owner | §18.1 CODEOWNERS state; post-S2499 F-D-OWN-1 remediation baseline. Frontend PA WS surface (CommandCenterPage / paStore / useWebSocket) also unassigned. S2600+ T-slot maintainer-decision batch candidate. |
| **DEBT-D-7** `_next_seq()` wraparound risk across process boundaries | `core/services/pa_status_events.py` (in-memory counter with FIFO eviction at 1024 traces per Agent 2) | LOW | unknown | Verifier-loop next-step (§20.4): multi-replica verification; seq wraparound could cause client-side dedup failure on `(trace_id, seq)` tuple. |
| **DEBT-D-9** WS envelope SoT registry ABSENT (F-D-B2-4 fold NEW row) | `core/services/` (no `ws_envelope_registry.py` or equivalent at HEAD — §5.6 evidence) | **HIGH** | **missing_contract_system** | xx99 must declare whether PA is allowed to create a **local SoT (Path A/B local)** or must wait for **Group 1700 platform registry**; if waiting, must pick Path C+observability-compensation with explicit telemetry plan. Distinct class of gap from DEBT-D-1: DEBT-D-1 is PA-slice envelope contract absence; DEBT-D-9 is org-wide SoT mechanism absence. Blurring these blurs xx99 verdict interpretation. |

**Note (F-D-B2-3 fold ratified 2026-07-06):** DEBT-D-8 (PA WS auth-close-with-code discipline exception) has been **REMOVED from the debt matrix** and relocated to **§15.2 Observations / intentional divergences** subsection below. Rationale: PA close(4001) is stronger-than-baseline + intentional design (Cat B §16.1 F-B10 fold); leaving it in debt table creates taxonomy confusion — debt register is for items requiring remediation or explicit risk acceptance, not intentional divergences.

### 15.2 Observations / intentional divergences (F-D-B2-3 fold — new subsection)

**F-D-B2-3 fold ratified 2026-07-06 (Rigby SIGN cycle 1 Batch 2 Q3c STRENGTHEN, Chris "agree all" wholesale):** items that diverge from platform baseline but are intentional (stronger-than-baseline design choices), not debt. Recorded for platform-wide consistency review scope (e.g., Group 1700 T4 arc audit boundary) — NOT for remediation.

| Observation | file:line | Divergence | Rationale |
|---|---|---|---|
| **OBS-D-1** PA WS auth-close-with-code discipline exception (formerly DEBT-D-8) | `core/consumers_pa_conversation.py:184` (close 4001) + `:189` (close 4002) vs S2504 §5.3 canonical baseline (per-consumer discretion; silent-degrade default at middleware layer) | PA Consumer EXPLICITLY rejects unauthenticated WS connect via close-with-code; platform default is silent AnonymousUser fallback + per-consumer per-message downgrade discretion | Stronger auth-boundary at PA scope. INTENTIONAL design per Cat B §16.1 F-B10 fold. NOT debt; documented for cross-consumer consistency review at Group 1700 T4 arc scope. |

### 15.3 Cross-arc coordination debt (adjacent to Cat D)

- **CF-D6** REST↔WS T7 joint SoT — DUAL-OWNED (Group 2500 side by S2504; Group 2600 side by S2604). Cat D S2604 delivers PA-side artifact (§6.1 F-D2 canonical + §7.4 T7 consistency rule) for S2699 xx99 verdict.
- **CF-C2** (S2503 preserved) — Cat C2-owned; Cat D §8.2 inherits retention window as upstream input. Cat D does NOT re-litigate per Cat-D-5 analog anti-scope.
- **F-B-HIGH-3** (S2402 preserved) — Cat C1-owned per parent §5.3 AC#3. Cat D §9.3 records coupling axis only per AC-D6.
- **T4 Group 1700 Observability handoff** — Cat D §18.2 canonical handoff for envelope-shape telemetry emit-signature + per-Consumer conformance metrics + REST↔WS parallel-delivery reconciliation-layer ownership.

---

## 16. Boundary Violations

### 16.1 F-D-WSENVELOPE-1 PA-slice preservation (from S2504 preserved)

**Location:** `core/consumers_pa_conversation.py:242-298` (emit sites) + `core/services/pa_status_events.py:104-182` (emit service) + `frontend/src/pages/CommandCenterPage.tsx:682-764` (client parse) + `frontend/src/stores/paStore.ts:49-77` (Zustand store).

**HTTP-analog boundary state at PA WS layer (Cat D VC-4 verified):**
- Zero `TypedDict` / `Protocol` / `BaseModel` / `@dataclass` declared at PA WS Consumer files.
- Zero `interface WSMessage*` / `type WSMessage*` declared at frontend PA WS parse sites for the 3 Cat B canonical message classes.
- Zero envelope-SoT registry service (`core/services/ws_envelope_registry.py` etc.).
- Zero `.schema.json` files for PA WS message types.

**Classification:** NOT a violation per se (F-D-WSENVELOPE-1 PA-slice preservation matches S2504 §14.2 canonical platform-wide zero baseline). But contract-DECLARATION at WS boundary DOES NOT declare envelope shape. **Cat D S2604 records evidence; Chris-D-verdict at S2699 xx99 OWNS Path A / Path B / Path C+observability-compensation selection per parent §5.3 AC#2 + F-D1 fold F5-analog closure discipline.** Path C-pure (SoT-declared WITHOUT observability compensation) is **NON-RATIFIABLE per F5-analog ratified 2026-07-06 (F-D1 fold second clause).**

### 16.2 F-D1 fold F5-analog hard "HARD-INVALID / NON-SELECTABLE" language for Path C-pure (F-D-B1-4 + F-D-B2-6 folds — normalization ratified 2026-07-06)

**F-D-B1-4 + F-D-B2-6 folds ratified 2026-07-06 (Rigby SIGN cycle 1 Batch 1 Q1d + Batch 2 Q4b STRENGTHEN, Chris "agree all" wholesale):** normalize "INVALID" language to **"HARD-INVALID / NON-SELECTABLE"** everywhere Path C-pure discussed — matches Cat C §16.1 F5+F-C7 hard-INVALID discipline exact phrasing across §6.1.1 strictness-disposition column + §16.2 (this section).

Per F-D1 fold second clause ratified 2026-07-06 (Rigby SIGN-preview STRENGTHEN, Chris "agree all" wholesale, baked at shape card v1 Q1 pre-drafting):

**F5-analog closure discipline enforcement:** Chris-D-verdict at S2699 xx99 must select one of the following:

- **Path A** — Typed WS envelope schema at all PA-related consumers (TypedDict / Protocol / BaseModel).
- **Path B** — Envelope declared at CONNECT handshake only; message-shape SoT-declared but non-enforced.
- **Path C+observability-compensation** — WS message-contract SoT-declared for all PA-related channels + observability compensation (envelope-shape telemetry per Group 1700 T4 handoff evidence). Non-streaming per F-D1 fold conditional (VC-5 confirmed message.created is buffered complete-messages at HEAD, so Path C+carve-out collapses to Path C non-streaming).

**Path C-pure (SoT-declared WITHOUT observability compensation) is HARD-INVALID / NON-SELECTABLE under F5-analog** per F-D1 fold second clause: selecting Path C-pure at S2699 xx99 **fails closure and must be recorded as "rejected / non-ratifiable."** Only Path C+observability-compensation is admissible on the Path-C axis (parallel to Cat C1 Path C+compensating structural discipline). F5-analog blocks paper-victory; there is no "defer without observability compensation" landing spot for PA WS envelope SoT at Cat D scope. This is not a "discouraged" verdict — it is a **NON-SELECTABLE** verdict. Cat D records this constraint; Chris cannot ratify Path C-pure at xx99 without violating F5-analog closure discipline.

### 16.3 PA-adjacent boundary preservation (anti-scope verification)

- **Cat-D-1..9 micro-anti-scope preserved** (§16.4 below).
- **Parent §7 anti-scope items #1-#10 preserved** — PA behavior mutations + prompt engineering + memory persistence + agent-registry mutations + Discord bot PA + Content Studio PA + Fleet HMAC PA signature + PA/auth token rotation + LLM provider policy + agent timeout tuning ALL out-of-scope at Cat D.
- **Cat-C-1..9 inheritance** — Cat D does NOT re-litigate any Cat C1 or Cat C2 verdicts per Cat-D-5 anti-scope-analog.
- **Cat-B-1..9 inheritance** — Cat D does NOT re-litigate Cat B typing verdicts per Cat-D-7 anti-scope-analog.
- **Cat A F7 fold inheritance** — Cat D does NOT re-inventory PA-path REST endpoints; cites Cat A §6.1 F11 canonical.

### 16.4 Cat-D micro-anti-scope enumeration (Cat-D-1..9 ID-stable list)

Cat D inherits parent §7 anti-scope items #1-#10 unchanged. Additional Cat-D-specific micro-anti-scope (Cat-D-1 through Cat-D-9, ID-stable per F-B9 fold precedent from Cat B §16.4 + Cat C §16.4):

- **Cat-D-1** — Cat D does NOT retrofit typed WS envelope schema code (TypedDict / Protocol / BaseModel at consumers; TypeScript `interface WSMessage*` at client) (evidence-only; retrofit is post-verdict Path A implementation scope).
- **Cat-D-2** — Cat D does NOT modify TokenAuthMiddlewareStack behavior at `core/ws_auth_middleware.py:24` (WS auth-layer mutations preserved per parent anti-scope #8 + S2504 canonical baseline).
- **Cat-D-3** — Cat D does NOT re-inventory the platform 120 WS route entries OR the 87 Consumer class definitions (S2504 §6.3 canonical artifact; Cat D-scope = PA-related subset filter only, NOT re-enumeration).
- **Cat-D-4** — Cat D does NOT re-litigate S2504 Cat D γ mechanism-nesting decision CONTENT — only the PA-application decision (COUPLE / DECOUPLE / PRESERVE ORTHOGONAL per AC-D3). S2504 §9.1 is upstream input; Cat D uses as inheritance.
- **Cat-D-5** — Cat D does NOT re-litigate F-B-HIGH-3 workspace-membership implicit-gate closure verdict (Cat C1 S2603 owned per parent §5.3 AC#3 + Cat C §16.1 F5+F-C7 hard-INVALID discipline). Cat D §9.3 AC-D6 records Cat C1 coupling axis only.
- **Cat-D-6** — Cat D does NOT modify PA WS Consumer class code at `core/consumers_pa_conversation.py`, `core/consumers_unified_v2.py`, `core/consumers_base.py`, or `core/personal_assistant_consumer.py` (evidence-only per Cat-C-3 precedent + PA behavior mutations preserved per parent anti-scope #1).
- **Cat-D-7** — Cat D does NOT enumerate Cat B U6 WS envelope inventory beyond re-verification at HEAD (Cat B §6.2 F-B3 canonical; Cat D uses as denominator only per §6.1.1 citation discipline).
- **Cat-D-8** — Cat D does NOT commit to Group 1700 Observability envelope-shape telemetry SPEC delivery (Group 1700 T4 arc scope; Cat D AC-D4 + AC-D8 handoff-only per S2504 §7.4 measurement-handoff precedent).
- **Cat-D-9** — Cat D does NOT create new `docs/topics/personal-assistant.md` WS-envelope documentation section (Path C+observability-compensation specifies as REQUIREMENT per AC-D4, not deliverable; documentation update is post-xx99 anchor-update cascade scope per S2603 close residual AU-C2 + AU-C3 pattern).
- **Cat-D-10** (F-D-B2-5 fold ratified 2026-07-06) — Cat D does NOT propose alternate transport (SSE / long-poll / HTTP/2 push) or WS protocol replacement. Envelope-declaration + observability discussion stays focused; transport-swap arguments are out-of-scope. Prevents reviewer reruns of "we should just use SSE instead" tangential debates.
- **Cat-D-11** (F-D-B2-5 fold ratified 2026-07-06) — Cat D does NOT propose changes to channel layer / Redis / pubsub mechanics (`core/settings.py:279-293` CHANNEL_LAYERS config + `channels_redis.core.RedisChannelLayer` + `InMemoryChannelLayer` fallback). Infrastructure debate is separate scope; keeps Cat D focus on envelope-declaration + observability.

---

## 17. Duplicate or Overlapping Systems

### 17.1 PersonalAssistantConsumer naming collision at 2 files (VC-2)

Two distinct `PersonalAssistantConsumer` class definitions exist at HEAD:

| File | Line | Import at routing.py | Route |
|---|---|---|---|
| `core/consumers_unified_v2.py` | 20 | `from .consumers_unified_v2 import PersonalAssistantConsumer as PersonalAssistantV2Consumer` (line 27) | `ws/assistant/$` (line 138) |
| `core/personal_assistant_consumer.py` | 14 | `from .personal_assistant_consumer import PersonalAssistantConsumer` (line 353) | `ws/personal-assistant/$` (line 363) |

**Cat D observation:** the routing.py import-as alias at line 27 resolves the Python import collision (naming Python-level clash prevented by rename); both classes are ROUTED simultaneously to distinct URL patterns. This is NOT a runtime bug but creates cognitive-load drift for maintainers reading the codebase. Adjacent-domain (V1 legacy vs V2 unified) preservation; DEBT-D-5 records.

### 17.2 Alias routes `ws/ai-assistant/$` + `ws/interview/$` → same AssistantChatConsumer

`core/routing.py:141` + `core/routing.py:144` both route to `consumers.AssistantChatConsumer` at `core/consumers_base.py:390`. Two URL patterns; one Consumer class. `ws/ai-assistant/$` + `ws/interview/$` are alias routes for the same handler.

**Cat D observation:** alias-route pattern is intentional design (2 URL paths for the same behavior). NOT a duplication; NOT drift. Recorded for §17 completeness.

### 17.3 REST poll + WS broadcast parallel-delivery for `agent.completed` (inherited from Cat B §7.1)

Cat B §7.1 canonical evidence: REST polling + WS broadcast are PARALLEL delivery channels for task completion signal. Client-side dedup only via `paStore.seenCompletions` 50-item ring (`execution_id` key). NO server-side reconciliation logic at HEAD.

**Cat D observation:** parallel-delivery pattern is DEBT-D-4 (§15.1); Cat D §7.4.2 canonical T7 consistency GAP. Recorded for §17 as duplicate/overlapping systems flag.

---

## 18. Ownership Gaps

### 18.1 CODEOWNERS assignment status at HEAD `cf410660` (VC-6)

Per parent-Claude verification of `/CODEOWNERS` (47 lines):

| File | Assignment status | CODEOWNERS line |
|---|---|---|
| `/core/consumers_pa_conversation.py` | **UNASSIGNED** (default `* @clwest` at line 18 only) | N/A — no specific PA Consumer entry |
| `/core/consumers_unified_v2.py` | **UNASSIGNED** (default only) | N/A |
| `/core/consumers_base.py` | **UNASSIGNED** (default only) | N/A |
| `/core/personal_assistant_consumer.py` | **UNASSIGNED** (default only) | N/A |
| `/core/ws_auth_middleware.py` | **ASSIGNED to @clwest** | line 28 (under "Auth surface" section) |
| `/core/services/pa_status_events.py` | **UNASSIGNED** (default only) | N/A |
| `/core/tasks_agents.py` | **UNASSIGNED** (default only) | N/A |
| `/frontend/src/pages/CommandCenterPage.tsx` | **UNASSIGNED** (no frontend/src/pages/* entry) | N/A |
| `/frontend/src/stores/paStore.ts` | **UNASSIGNED** (no frontend/src/stores/paStore.ts entry) | N/A |
| `/frontend/src/hooks/useWebSocket.ts` | **UNASSIGNED** (no frontend/src/hooks/* entry) | N/A |

**Baseline compliance:** CODEOWNERS was established at S2499 Group 2400 Auth arc close per Cat D F-D-OWN-1 remediation (AU-D5 anchor-update). Per S2499 §7.4 canonical statement: *"Full ownership refinement lives in follow-on T-slot batch ... Frontend-specific ownership (api.ts + authStore.ts + Sidebar.tsx) refined at S2600+ per Group 2200 T-slot maintainer-decision batch."*

**Cat D observation:** PA WS Consumer implementation files are ONLY covered by default `* @clwest`. PA WS auth middleware (`ws_auth_middleware.py`) IS explicitly assigned at line 28. Frontend PA WS surface has zero coverage. DEBT-D-6 records; §19.3 MEDIUM follow-on for S2699 xx99 anchor-update cascade or post-arc T-slot batch.

### 18.2 Cat D-specific ownership handoff to Group 1700 Observability T4 arc

Per S2504 §7.4 measurement-handoff canonical + Cat D §10.4 events-that-could-be-emitted evidence:

**Group 1700 Observability T4 arc scope candidates (Cat D handoff-only per Cat-D-8 anti-scope):**
- Envelope-shape conformance metric per PA-related Consumer class.
- WS unauthorized-connect metric (extends S2504 §7.4 baseline).
- Per-canonical-class emit latency histogram.
- REST-poll vs WS-broadcast `agent.completed` reconciliation timing delta at client-side dedup.
- Envelope-shape SoT drift detection (register PA WS envelope claims for `verify_doc_claims` future coverage per §14.3).

**Cat D output for T4 handoff:** `docs/research/domains/pa/2604_pa_rest_ws_t7_joint_dual_owner_design_prep_audit.md` §6.1 F-D2 canonical matrix + §7.4 T7 consistency rule table + §10.4 emit-signature candidates.

---

## 19. Recommended Future Research

Ranked by architectural uncertainty × risk × unblocked flows per playbook §11.2 §19 discipline.

### 19.1 CRITICAL — Blocks Chris-D-verdict at S2699 xx99

1. **S2699 xx99 Chris-D-verdict on PA WS envelope strictness Path A / Path B / Path C+observability-compensation.** F-D1 fold F5-analog blocks Path C-pure. Cat D §6.1 F-D2 canonical matrix + §7.4 T7 consistency rule + §13 maturity verdict are canonical evidence baselines.
2. **Cat C1 coupling axis re-assessment at S2699 xx99.** Cat D §9.3 records ORTHOGONAL at HEAD; if Cat C1 Path A ratified at xx99, Cat D natural coupling to symmetric WS-side WorkspaceMember-enforcement at connect handshake is candidate re-examination.

### 19.2 HIGH — Enables Chris-D-verdict at S2699 xx99

3. **Consumer body verification for PA-related Consumer subset #2-4** (DEBT-D-2). Read `core/consumers_unified_v2.py:20` + `core/consumers_base.py:390` + `core/personal_assistant_consumer.py:14` Consumer bodies to determine envelope-declaration state per Consumer beyond PAConversationConsumer. Extends §6.1.2 UNKNOWN entries to F4-target-met status.
4. **Client-subscription verification for PA-related WS routes #2-5** (§3.1 UNKNOWN column). Determine which of `ws/assistant/`, `ws/ai-assistant/`, `ws/interview/`, `ws/personal-assistant/` are actively subscribed by React frontend + mobile PA client (if present). Extends VC-1 evidence baseline.
5. **Group 1700 Observability T4 arc scope declaration** (Cat D §18.2 handoff). Envelope-shape telemetry emit-signature + per-Consumer conformance metrics + REST↔WS parallel-delivery reconciliation-layer ownership.

### 19.3 MEDIUM — Post-arc follow-on

6. **Docs cascade for `docs/topics/personal-assistant.md` §92-105 PA async processing drift** (D2 §14.2). Reposition polling as secondary, WS streaming (or WS broadcast) as primary for web ChatUI.
7. **Docs cascade for `docs/topics/frontend.md:65` "Rigby chat uses `POST /api/pa/chat/` everywhere" drift** (D1 §14.2). Add WS supplementary delivery + client-side dedup pattern.
8. **Docs cascade for `docs/topics/celery-workers.md:298-306` latency claim omitting WS behavior** (D3 §14.2).
9. **Register PA WS envelope-shape claims for `verify_doc_claims` future coverage** (§14.3). Enable declaration-layer drift detection for PA WS envelope SoT.
10. **Post-arc T-slot maintainer-decision batch for CODEOWNERS PA WS Consumer files + frontend PA WS surface** (DEBT-D-6, §18.1).
11. **Post-arc T-slot maintainer-decision for `_next_seq()` wraparound risk across process boundaries** (DEBT-D-7, §20.4 next-verify).
12. **Post-arc T-slot maintainer-decision for PersonalAssistantConsumer naming collision boundary** (DEBT-D-5, §17.1).

---

## 20. Appendix

### 20.1 Files inspected

Python (backend):
- `core/consumers_pa_conversation.py:175, 181-198, 227-237, 243-248, 274-284, 286-297, 320-372` — PAConversationConsumer canonical Consumer
- `core/consumers_unified_v2.py:20` — PersonalAssistantConsumer (V2 alias)
- `core/consumers_base.py:390` — AssistantChatConsumer
- `core/personal_assistant_consumer.py:14` — PersonalAssistantConsumer (direct)
- `core/services/pa_status_events.py:104, 116-182` — rigby.tool.* emit service
- `core/views_personal_assistant.py:267, 521, 567-579` — REST-side PA views + message.created emit
- `core/tasks_agents.py:336-491, 471-485, 493` — fire_agent_followup_subscriptions + agent.completed emit
- `core/tasks_misc.py:4859-4881` — message.created secondary emit from PA task completion
- `core/services/claude_code_engineer.py:1203-1215` — message.created Claude Code message persist
- `core/models/conversations/models.py:59-222` — ChatConversation model
- `core/models_unified_system.py:882-1096` — AgentExecution + AgentFollowupSubscription
- `core/models_tool_calls.py:19-118` — ToolCallRecord
- `core/routing.py:27, 135, 138, 141, 144, 353, 363` — PA-related WS routes
- `core/ws_auth_middleware.py:14-52` — TokenAuthMiddleware (S2504 §3.3 canonical inheritance)
- `core/asgi.py:14-33` — ProtocolTypeRouter WS mount
- `core/settings.py:279-293` — CHANNEL_LAYERS config
- `core/services/unified_pa_entrypoint.py` — 7,613 lines (god-service per §5.5)

Frontend (TypeScript):
- `frontend/src/pages/CommandCenterPage.tsx:682-764` — PA WS subscription site (Cat B §6.2 F-B3 canonical)
- `frontend/src/hooks/useWebSocket.ts:4-22` — Generic WS hook (event type is `unknown` at line 21)
- `frontend/src/stores/paStore.ts:49-77, 68, 113` — Zustand store + seenCompletions dedup ring
- `frontend/src/lib/api.ts:1115` — PAChatStatusResponse.audio_url REST-embedded (Cat B §6.3)

CODEOWNERS:
- `/CODEOWNERS` (47 lines)

### 20.2 Docs inspected

- `docs/CLAUDE.md`
- `docs/PLATFORM_WHAT_IT_IS.md`
- `docs/PLATFORM_INVENTORY.md`
- `docs/topics/personal-assistant.md`
- `docs/topics/frontend.md`
- `docs/topics/celery-workers.md`
- `docs/topics/infrastructure.md`
- `docs/research/domains/pa/2600_pa_domain_scoping.md` (parent scoping)
- `docs/research/domains/pa/2601_pa_backend_endpoint_contract_sot_design_prep_audit.md` (Cat A sibling)
- `docs/research/domains/pa/2602_pa_client_contract_surface_design_prep_audit.md` (Cat B sibling)
- `docs/research/domains/pa/2603_pa_workspace_authz_session_lifecycle_design_prep_audit.md` (Cat C sibling)
- `docs/research/domains/api/2504_api_permission_floor_registry_rest_ws_t7_joint_design_prep_audit.md` (CF-D6 ORIGIN)
- `docs/research/domains/api/2599_api_canonical_summary.md` (Group 2500 canonical verdict)
- `docs/research/DOMAIN_RESEARCH_PLAYBOOK.md` §11.2 + §13 + §14 + §15 + §16 + §21
- `docs/handoffs/SESSION_2603_PA_CAT_C_WORKSPACE_AUTHZ_SESSION_LIFECYCLE.md`

### 20.3 Grep patterns used (parent-Claude direct greps)

- `^class \w+Consumer` in `core/consumers_pa_conversation.py` + `core/consumers_unified_v2.py` + `core/consumers_base.py` + `core/personal_assistant_consumer.py`
- `await self\.close\(code=|await self\.accept\(\)|scope\.get\("user"\)|AnonymousUser` in `core/consumers_pa_conversation.py`
- `^\s*re_path\(|^\s*path\(` in `core/routing.py`
- `'message\.created'|"message\.created"|'agent\.completed'|"agent\.completed"|'rigby\.tool` across `**/*.py`
- `StreamingHttpResponse|text/event-stream|Transfer-Encoding.*chunked` in `core/*personal_assistant*.py`
- `TypedDict|Protocol\)|BaseModel\)|@dataclass` in `core/consumers*.py`
- `channels_graphql|CHANNEL_LAYERS` in `requirements*.txt` + `settings*.py` + `pyproject.toml`
- `group_send\(` in `core/services/pa_status_events.py`
- `PAConversationConsumer|PersonalAssistantV2Consumer|AssistantChatConsumer|PersonalAssistantConsumer` in `core/routing.py`
- `ws/pa/conversations|ws/assistant|ws/ai-assistant|ws/interview|ws/personal-assistant` in `frontend/src`
- `class AssistantChatConsumer|class PersonalAssistantConsumer` in `core/**/*.py`

### 20.4 Unresolved unknowns

1. **PA-related Consumer subset #2-4 Consumer body content** (DEBT-D-2). Consumer bodies for `PersonalAssistantV2Consumer` (`consumers_unified_v2.py:20`) + `AssistantChatConsumer` (`consumers_base.py:390`) + `PersonalAssistantConsumer` (`personal_assistant_consumer.py:14`) not read in full at Cat D S2604 opening. Envelope-declaration state + emit-signature state UNKNOWN. §6.1.2 UNKNOWN entries.
2. **Client-subscription state for PA-related WS routes #2-5** (§3.1 Client-consumed column UNKNOWN for 4 of 5 routes). Grep in `frontend/src` for literal WS route paths returned zero matches; dynamic URL construction is likely but not verified.
3. **`_next_seq()` wraparound risk across process boundaries** (DEBT-D-7). Multi-replica seq collision risk on `(trace_id, seq)` client-side dedup tuple.
4. **`artifact_pointers` field format stability** in `agent.completed` envelope. No spec doc found (Session 1181 PR5 rationale not fully verified).
5. **WS frame size limits on `artifact_pointers`** for large payloads (e.g., 1000+ media IDs). No chunking observed at emit time.
6. **Mobile PA client subscription evidence** at HEAD. No mobile-specific PA WS client interception found; parent §3.D lists Mobile as "secondary stakeholder"; evidence-only at Cat D open.
7. **Metadata schema for `agent.completed` rows** (`ChatConversation.metadata` JSONB stores `{'kind': 'agent_completion', 'execution_id': ...}`). No JSON schema definition or Pydantic validator enforces shape.
8. **`ChatConversation` `conversation_id` format namespacing** — potential group naming collision risk if `conversation_id` overlaps with non-PA "conversation-*" identifiers. Cross-system uniqueness not verified.

### 20.5 Conflicts between sources

- **Cat B §6.2 F-B3 "1 PA-client WS channel" vs Cat D §3.1 VC-1 "5 PA-related WS routes / 4 distinct Consumers"** — RESOLVED at Cat D §3.1: Cat B was CLIENT-CONSUMED scope; Cat D is PA-RELATED scope. Both statements correct within their respective scopes.
- **Agent 1 "PAMessage / ChatMessage NOT FOUND"** vs **Cat A §6.1 F11 row 16-17 references `unified_pa_chat`** — RESOLVED: `ChatConversation` is the unified message container (per line 59 docstring "storing chat conversations"); no separate PAMessage table. Agent 1 §6 next-verify #1 addressed.
- **S2504 §14.2 F-D-WSENVELOPE-1 "0/40 unique consumer classes with `group_send` conform to `ui.render_hint` envelope"** vs **Cat D §4.1 "F-D-WSENVELOPE-1 PA-slice preservation VERIFIED"** — CONSISTENT: PA-slice preservation of S2504 canonical zero baseline is expected AND confirmed. Cat D matches S2504 baseline at PA scope.

### 20.6 Verifier-loop corrections summary

Parent-Claude verifier-loop 7-correction chain applied pre-draft:

1. **VC-1** Cat D PA-related Consumer inventory expanded to 4 distinct classes (§3.1 + §14.1)
2. **VC-2** PersonalAssistantConsumer naming collision at 2 files (§17.1 + §14.1)
3. **VC-3** Emit-site cross-verified across 6 files (§14.1 evidence baseline)
4. **VC-4** F-D-WSENVELOPE-1 PA-slice preservation verified (§4.1 + §14.1)
5. **VC-5** F-D1 fold streaming-absence CONFIRMED (§7.1 + §14.1)
6. **VC-6** CODEOWNERS state at HEAD (§18.1 + §14.1)
7. **VC-7** channels_graphql absent + CHANNEL_LAYERS at settings.py:279/289 (§4.3 + §14.1)

All 7 corrections logged; no re-inventorying performed. Playbook §14 discipline: "Direct source verification for important findings" + "Grep-verify binary claims before shipping to Rigby" applied throughout.

### 20.7 Cat D boundary discipline confirmed

Cat D output stays within EVIDENCE-ONLY + CHRIS-D-VERDICT-DEFERRED per Cat-D-1..9 anti-scope. No code retrofit proposed. No S2504 Cat D γ mechanism content re-litigation. No F-B-HIGH-3 closure verdict. No PAConversationConsumer / other PA WS Consumer code modification. No re-inventorying of platform 120 WS routes / 87 Consumer classes / 34 PA-path REST endpoints. Cat D §6.1 F-D2 canonical matrix uses Cat B §6.2 F-B3 canonical denominator + adds Cat D VC-1 PA-related Consumer subset per F-D2 fold discipline.

### 20.8 SIGN cycle 1 fold record (CLOSED 2026-07-06)

**Shape-card SIGN-preview fold record (2 folds Chris-ratified 2026-07-06 "agree all" wholesale — pre-drafting):**

| Fold | Q | Direction | Adoption |
|---|---|---|---|
| F-D1 | Q1 Path C+carve-out + Path C-pure | STRENGTHEN carve-out conditionality + F5-analog observability coupling | ✅ Baked into §7.1 F-D1 streaming-absence VERIFICATION + §16.2 F5-analog HARD-INVALID/NON-SELECTABLE language + §6.1.1 strictness-disposition column |
| F-D2 | Q3 AC-D2 | STRENGTHEN denominator scope clamp + 3-part evidence record | ✅ Baked into §6.1 F-D2 canonical matrix + §6.1.1 (i)/(ii)/(iii) 3-part evidence columns |

**SIGN cycle 1 full-audit fold record (CLOSED 2026-07-06):**

- **Dedicated SIGN pin ID:** `pa-e14f943525a84b5a` (created 2026-07-06 via `session_tool action=create_fresh title='Cat D S2604 PA REST↔WS T7 joint dual-owner design-prep audit SIGN cycle 1'`).
- **SIGN batch structure:** Preemptive 2-batch × 2-Q per S2602 + S2603 SUCCESS pattern per `feedback_rigby_sign_worker_instability_recovery.md` — SINGLE-PIN close (no worker instability observed).
- **SIGN verdict per Batch:**
  - Batch 1 (Q1 coverage + Q2 maturity): **HIGH confidence** — 5 STRENGTHEN folds (F-D-B1-1 through F-D-B1-5).
  - Batch 2 (Q3 debt + Q4 boundary): **HIGH confidence** — 6 STRENGTHEN folds (F-D-B2-1 through F-D-B2-6).
- **Overall confidence:** **HIGH**.
- **Total folds:** 11 STRENGTHEN + 0 DIAL-BACK + 0 REJECT.
- **Chris ratification:** "agree all" wholesale 2026-07-06 — all 11 folds baked in-place.

**Full-audit SIGN cycle 1 fold table:**

| Fold | Batch | Q | Direction | Adoption |
|---|---|---|---|---|
| F-D-B1-1 | B1 | Q1a §6.1.1 | STRENGTHEN | ✅ Consumer(s) column + schema versioning micro-field + aux-events footnote in §6.1.1 |
| F-D-B1-2 | B1 | Q1b §6.1.2 | STRENGTHEN | ✅ Close condition note + Consumers #2-4 relabeled as VC-1 partial sample DEBT (bounded, pointer-ready) in §6.1.2 |
| F-D-B1-3 | B1 | Q1c §3.1 + §6.1 | STRENGTHEN | ✅ Denominator (F4) vs perimeter (VC-1) distinction — appended to §3.1 |
| F-D-B1-4 | B1 | Q1d §6.1.1 + §16.2 | STRENGTHEN | ✅ HARD-INVALID / NON-SELECTABLE language upgrade normalized across §6.1.1 strictness column + §7.1 + §13 + §16.2 + §19.1 |
| F-D-B1-5 | B1 | Q2a §13 | STRENGTHEN | ✅ §13 split into 3 axes (Mechanism / Declaration / Observability); Overall = PARTIAL preserved |
| F-D-B2-1 | B2 | Q3a §15.1 DEBT-D-1 | STRENGTHEN | ✅ Severity MEDIUM → HIGH; finding_type missing_connection → missing_contract |
| F-D-B2-2 | B2 | Q3b §15.1 DEBT-D-4 | STRENGTHEN | ✅ Severity MEDIUM → HIGH; closure text "xx99 Path selection must explicitly choose dedup/reconciliation posture" added |
| F-D-B2-3 | B2 | Q3c §15.1 DEBT-D-8 | STRENGTHEN | ✅ REMOVED from §15.1 debt matrix; relocated to new §15.2 Observations / intentional divergences subsection as OBS-D-1 |
| F-D-B2-4 | B2 | Q3d §15.1 NEW | STRENGTHEN | ✅ DEBT-D-9 WS envelope SoT registry ABSENT — HIGH — missing_contract_system added to §15.1 |
| F-D-B2-5 | B2 | Q4a §16.4 NEW | STRENGTHEN | ✅ Cat-D-10 (does NOT propose alternate transport) + Cat-D-11 (does NOT change channel-layer / Redis / pubsub) added to §16.4 |
| F-D-B2-6 | B2 | Q4b §16.2 | STRENGTHEN | ✅ HARD-INVALID / NON-SELECTABLE normalization (paired with F-D-B1-4 baked once, applied to all Path C-pure references) |

**Implicit AGREE (no fold) verdicts:** Q2b Declaration=EXPERIMENTAL correctly graded for Cat D WS-slice scope. Q2c T7 consistency subsumed under Declaration+Observability axes (no separate 4th axis). Q4c probe 4 for audio_url (Cat B scope, not Cat D). Q4d Cat C1 coupling axis ORTHOGONAL-with-conditional language sufficient. Q4e §17.3 placement for parallel-delivery pattern correct (not §14.2 D6 drift).

**SIGN pin retirement:** Retired at S2604 close via `session_tool.retire force=true` — TWENTY-EIGHTH consecutive dedicated fresh SIGN pin retirement in Research OS candidate after S1399/S1499/S1599/S1699/S1799/S1899/S1999/S2099/S2199/S2299/S2400/S2401/S2402/S2403/S2404/S2499/S2500/S2501/S2502/S2503/S2504/S2599/S2600/S2601/S2602/S2603 twenty-seven prior.

**Chris ratification card:** Presented post-fold — "agree all" 2026-07-06 wholesale ratification. On ratification, frontmatter `status: draft` → `status: active` per playbook §16 draft-first workflow.

---

**End of Cat D S2604 v1 draft.**
