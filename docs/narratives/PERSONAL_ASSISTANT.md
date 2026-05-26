---
title: "Personal Assistant (Rigby) — narrative pilot (batch D)"
status: draft (batch D of Session 1158 corpus-narrative program)
last_updated: 2026-05-25
session: 1158
audience: future-operator (future-Claude / future-hire / future-Chris) — cannot access UI
template_version: v1-LOCKED (Rigby, Session 1158)
companion_docs:
  - docs/topics/personal-assistant.md
  - docs/narratives/AGENTS_AND_AUTONOMY.md
  - docs/narratives/CONTENT_PIPELINE.md
  - docs/narratives/SIGNAL_INTELLIGENCE.md
  - docs/PLATFORM_INVENTORY.md
provenance_confidence: HIGH (anchored to topics doc + named handoff files + PLATFORM_INVENTORY)
provenance_note: Batch D narrative. Center of gravity is Session 1036 — when keyword routing was replaced by GPT-5.2 function calling. Companions A/B/C cover what runs / what gets published / where work comes from; this doc covers who orchestrates it all. Counts anchored to PLATFORM_INVENTORY 2026-05-25 (git HEAD d513cd7f). Uncertainty labelled inline.
---

# Personal Assistant (Rigby)

> Fourth companion narrative. The agent doc covered *what runs*;
> the content-pipeline doc covered *what gets published*; the
> signal-intelligence doc covered *where work comes from*. This
> doc covers *who orchestrates all of it* — the Personal
> Assistant, named Rigby. She is the user-facing surface of the
> platform: every chat message, every "do X for me" command,
> every "what's stuck" question routes through her. The
> 8-milestone arc traces her evolution from a 506-line keyword
> router into a GPT-5.2 function-calling agent that sees 106 tool
> schemas, dispatches across 171 handlers, and orchestrates eight
> intelligence services worth of context before the model writes
> a single token.

---

## 1. What this is

The Personal Assistant is the conversational entry point. A user
(currently donkeyking; ultimately external Suite consumers in the
fleet) sends a message to `POST /api/pa/chat/`. The endpoint
queues an async Celery task (the dedicated `pa` queue exists for
exactly this — Railway's proxy times out around 30 s, so the API
returns a `task_id` and the frontend polls
`GET /api/pa/chat/status/<task_id>/` every 2 s). The task runs
`UnifiedPAEntrypoint` end-to-end: it builds context (profile,
knowledge, system stats, doc retrieval — each with a 5 s
timeout); it assembles a messages array (system prompt +
conversation history + user message); it calls the GPT-5.2
Responses API with all 106 tool schemas; if the model returns
tool calls, it dispatches them through `ToolDispatcher`, feeds
the results back, and loops up to five iterations; once the
model returns text, it runs the enrichment pipeline (intent
inferred from which tools fired); and it returns a `PAResponse`.

Rigby has two scopes: `global` and `workspace`. Workspace mode
activates only from explicit workspace context (`workspace_id`,
`AssistantProfile.workspace`, or workspace-aware UI context).
Scope is never inferred from message text alone.

She is the closest thing the platform has to a single
operating surface. Every other subsystem in this corpus is
either upstream (gives her data) or downstream (gets called by
her). The eight milestones below trace how she got from a
keyword router to that position.

---

## 2. Core objects & vocabulary

| Term | Meaning |
|---|---|
| **`UnifiedPAEntrypoint`** | The async loop in `core/services/unified_pa_entrypoint.py`. Builds context, assembles messages, calls the model, dispatches tools, runs enrichment, returns `PAResponse`. Use `get_unified_pa()` (threading.Lock-guarded — Session 1142) to instantiate; do not construct directly. |
| **`ToolDispatcher`** | `core/services/tool_dispatcher.py`. 171 registered handlers. Every handler returns a `ToolResult` (structured response, never a raw string). Handlers register via `self.register(name, fn)` in `__init__`. |
| **`PA_TOOL_SCHEMAS`** | The 106-entry list in `core/services/pa_tool_schemas.py`. Each entry: `name` (matches a dispatcher handler), `description` (the natural-language hint GPT-5.2 uses to decide when to call), `parameters` (JSON schema with action enums + optional filters). |
| **`TOOL_TO_INTENT_MAP`** | The reverse map (tool → canonical intent). The enrichment pipeline reads this to pick which intelligence services to run after the model finishes. |
| **6 gateway tools (Session 1079)** | `governance_tool`, `work_tool`, `content_tool`, `intelligence_tool`, `ops_tool`, `studio_tool`. Each gateway absorbed a cluster of pre-1079 single-purpose tools (e.g., `governance_tool` = `boardroom_tool` + `human_decisions_tool`). Consolidation reduces schema budget and routing complexity. |
| **`run_agent` meta-tool** | Single tool with an `agent_name` enum. Routes to the actual agent. Session 1100 expanded it to 77 agents across 12 domains. Lets the model invoke any routable agent without each agent needing its own schema entry. |
| **Telemetry tools** | `agent_introspection_tool` (stats / list / details / capabilities — Session 1035 introduced the disjoint taxonomy), `status_snapshot_tool`, `check_resource_budget`, `pipeline_orchestrator_tool`, `task_breakdown_tool`. The model's eyes on the platform's runtime. |
| **`http_smoke_test` tool** | Endpoint smoke tests against Railway prod or localhost. Three built-in suites (cockpit_health, cockpit_incidents_crud, pa_tools_smoke). SSRF allowlist (*.railway.app, localhost), 50-step cap, 20s timeout. The PA can verify the platform's own health from inside a chat. |
| **`search_docs` tool (Session 1142)** | Chunked retrieval over the `/docs/` corpus with inline citations. Backed by `.rag/corpus.jsonl` + the `Document` table (852/14149 chunks at Session 1142). Complements `kb_tool`'s Document-table browse. The PA can answer "where is this documented?" without a context-window dump. |
| **Enrichment pipeline (8 services)** | Eight intelligence services that inject context **after** tool dispatch and **before** the formatting LLM call: `intelligence_enricher`, `blog_performance`, `domain_context` (9 domains), `spider_trends`, `advisor` (25 advisors), `strategic_memory`, `proactive_intelligence`, `platform_briefing`. Each enrichment fires for specific intents per a mapping. Relevance gate: 15% keyword overlap (skipped for content intents). |
| **Async via `pa` Celery queue** | `POST /api/pa/chat/` returns `{task_id}` immediately. `process_pa_chat_task` runs with `time_limit=300s`, `soft_time_limit=280s`. Uses `new_event_loop()` + `run_until_complete()`, **not** `async_to_sync` (which deadlocks). |
| **`ChatConversation` model** | The persistence row. Carries `conversation_id`, `session_title` (auto-generated by LLM on first message), `metadata` with `tool_calls` list (each `{name, arguments, call_id, ok}`) and `response_id` (Session 1036 — feeds `previous_response_id` for cached-input pricing). |
| **`previous_response_id` caching** | GPT-5.2 mechanism. When set, follow-up turns hit a 90% cached-input discount ($0.18/1M vs $1.75/1M). PA stores the prior `response_id` in `ChatConversation.metadata` and threads it back on the next turn. |
| **`global` vs `workspace` modes** | Scope discriminator. Global = no workspace_id; workspace = explicit workspace context (`workspace_id`, `AssistantProfile.workspace`, or workspace-aware UI). Never inferred from message text. Workspace-scoped tools (initiative_list, deliverable_list, file_tool) honor the scope. |
| **Tool count drift** | Three different numbers float in the docs: 104 (PLATFORM_INVENTORY 2026-05-25), 106 (topic doc / Session 1142 note), 171 handlers. They're not contradictory: schemas count tool *definitions* the model sees, handlers count dispatcher entries (some handlers correspond to action enums *inside* a single schema). PLATFORM_INVENTORY is authoritative for both. |
| **`PA_USE_FUNCTION_CALLING` flag** | Env var. `true` (default on Railway) → GPT-5.2 function calling path. `false` → falls back to the pre-Session-1036 506-line keyword router. Both paths still exist in code. |
| **PA-chat audit table** | The warn-only audit log of every PA call's auth posture, fleet origin, and validation result. Session 1131-1133 arc. Reject-mode flip queued for after ≥ 3 days of clean telemetry. |
| **Fleet HMAC sign-key** | Required for every fleet-app→u-d-b call. Sign key = `sha256(raw_secret).hexdigest()`, **not** the raw secret. `FleetServiceKey.secret_hash` stores the hex digest. Wrong key → 401 `signature_mismatch`. |

---

## 3. Milestone timeline

| When | Change shipped | Why | Outcome | Status | Pointers |
|---|---|---|---|---|---|
| **Foundation — keyword router era** *(pre-Session 1036)* | PA exists as a chat layer with a 506-line `_detect_intent_and_route()` if/elif keyword matcher and a 590-line intent-specific tool-payload builder. Tool dispatcher and tool schemas exist; the LLM **does not** see tools — it sees only a formatted prompt after a heuristic intent route picks the tool and runs it. The PA layer-1 surface map, platform-awareness spec, and 6-layer systems map were captured in handoffs (`PA_LAYER1_SURFACE_MAP.md`, `PA_PLATFORM_AWARENESS_SPEC.md`, `PA_SYSTEMS_MAP_6_LAYER.md`). | The first version needed deterministic routing — function calling was either not yet trustworthy at this scale, or the team didn't have a single chokepoint that could dispatch consistently. Hand-rolled keyword routing was the safest first cut. | Functional PA with structured tool returns; predictable behavior; covered the most common request paths. But: long if/elif chains drifted with every new tool; couldn't compose tools mid-turn; couldn't follow up naturally. Every new capability meant a code change in the router. | **Active as fallback path** — both paths still exist. Gated by `PA_USE_FUNCTION_CALLING` env var. The legacy path is the fallback if the flag is `false`. | `docs/handoffs/PA_LAYER1_SURFACE_MAP.md`, `PA_PLATFORM_AWARENESS_SPEC.md`, `PA_SYSTEMS_MAP_6_LAYER.md`; `core/services/unified_pa_entrypoint.py` (`_detect_intent_and_route`, `_build_tool_payload`) |
| **Session 969 — orchestration + enrichment pipeline** | Eight intelligence services consolidated into a single enrichment pipeline that fires post-tool / pre-format: `intelligence_enricher`, `blog_performance`, `domain_context` (9 domains), `spider_trends`, `advisor` (25 advisors), `strategic_memory`, `proactive_intelligence`, `platform_briefing`. Each maps to specific intents. Relevance gating (15% keyword overlap) added to avoid irrelevant injection on non-content intents. | The PA could call tools but couldn't ground its formatting in the platform's wider context. Eight different teams of enrichment data existed; PA wasn't reading any of them automatically. The enrichment pipeline made post-tool context-injection a structured pass instead of ad-hoc concatenation. | The PA's output now lands in-context: a stocks query returns analyst opinions + spider trends + advisor wisdom + memory of prior decisions, not just the raw tool output. Content intents skip the relevance gate; everything else passes through it. | **Active** — enrichment pipeline is part of the standard PA loop. | `docs/handoffs/SESSION_969_ORCHESTRATION_ENRICHMENT.md`; `docs/topics/personal-assistant.md` §"Enrichment Pipeline" |
| **Sessions 987, 993 — wiring completion + capability gaps audit** | (987) Tool-handler↔schema↔intent mapping rounded out so every registered handler has a schema and every schema has a TOOL_TO_INTENT_MAP entry. Removed orphan entries; covered the long tail of platform actions through the PA. (993) Capability-gap audit: PA had no path for proactive recommendations, no calendar/scheduling tool, no campaign orchestration, no experiment tracking, no concept-forge ideation. Gaps documented as the input list for the next push. | The PA was structurally complete but coverage was uneven — some actions had two tools, some had none. The audit gave the next session a prioritized fill-in list. | The PA could now reach the major surfaces of the platform; the audit named what was missing. Sessions 1035-W2 acted on the gap list. | **Active** — wiring conventions stuck; the gap audit's deliverables shipped. | `docs/handoffs/SESSION_987_PA_WIRING_COMPLETION.md`; `docs/handoffs/SESSION_993_PA_CAPABILITY_GAPS.md` |
| **Sessions 1006, 1030, 1035, 1035-W2 — reliability + persistence + introspection** | (1006) **Enrichment caps raised 300–600 → 1500–2000 chars per section.** The lower caps were discarding 85–95% of enriched data before the model saw it. (1030) **DB-backed conversation memory.** `_load_conversation_history_from_db()` loads the last 10 `ChatConversation` rows on PA init, so context survives Celery `max_tasks_per_child` worker recycling. (1035) **Timeouts everywhere.** Every DB-touching context step gets `asyncio.wait_for`: 5 s for profile/stats/docs, 3 s for knowledge, 5 s for sync conversation history with `SET LOCAL statement_timeout`. Each step degrades gracefully — PA still works if any single context call fails. Also introduced the **agent introspection taxonomy** (disjoint categories: `blocked_agents` + `rerouted_agents` + `fully_enabled_count` sum to `router_routable_total`). (1035-W2) **Eleven new tools** added across the gap list: proactive, distribution, calendar, experiment, podcast, campaign, audit, conceptforge, profile, self_awareness, ats. | The PA was usable but unreliable in three distinct ways: (1) it was throwing away most of its enrichment data on a stale char cap; (2) it lost context every time a Celery worker recycled (observed on Railway every few hours); (3) it would hang for 134 s on a single bad Postgres query during context-building. All three were silent failures from the user's perspective — the PA either gave thin answers, forgot the conversation, or just timed out. | Latency tail tamed: profile load 5 s max, knowledge 3 s, stats 5 s, docs 5 s. Conversation survives worker recycling. Enrichment data actually reaches the model. Agent introspection produces internally consistent counts (the disjoint taxonomy is checked at runtime — the reconciliation string is part of the tool result). | **Active** — all four mechanisms are standard. Enrichment caps and timeouts are non-negotiable; DB memory is the only path that survives Railway worker recycling. | `docs/topics/personal-assistant.md` §"Context Building (_build_context)", §"Enrichment caps", §"Agent Introspection Taxonomy" |
| **Session 1036 — GPT-5.2 function calling (architectural watershed)** | Replaced the 506-line keyword router with GPT-5.2 Responses-API function calling. The model now sees all 106 tool schemas and decides which to call. Multi-tool turns supported (model calls tool, sees result, decides next call). Max 5 iterations per turn. `previous_response_id` threaded through `ChatConversation.metadata.response_id` for the 90% cached-input discount on follow-ups. Tool-call audit trail: every call recorded in `ChatConversation.metadata.tool_calls` as `{name, arguments, call_id, ok}`. Feature flag `PA_USE_FUNCTION_CALLING=true` toggles between paths (legacy fallback retained). | The keyword router couldn't compose. A user asking "what's blocking my top initiative AND what's the SLO status" had to be split into two separate intents. The router also drifted with every new tool: each new capability required code changes in the if/elif chain. Function calling pushes routing into the model, where the tool *descriptions* become the natural language for "when to call this." Adding a tool now means adding a schema entry, not editing routing code. | Production latency: single tool ~6 s, 5-tool operator report ~16 s, multi-turn cached follow-up ~6 s. Cost per first turn: ~$0.027 (12K tokens). Cached follow-up: ~$0.009. Composability is real — the model now strings together tool calls naturally ("get blockers, then get SLO, then summarize"). | **Active** — function calling is the default path on Railway and locally. The legacy 506-line router is the documented fallback. | `docs/topics/personal-assistant.md` §"Flow (Function Calling — Active)" and §"Conversation History" and §"Cost (GPT-5.2)" |
| **Session 1079 — 6-gateway consolidation** | The single-purpose tool sprawl (separate `boardroom_tool`, `human_decisions_tool`, `initiative_tool`, `content_review_tool`, `generate_blog_tool`, `deliverables_tool`, `stock_intelligence_tool`, `sports_betting_tool`, `legislation_tool`, `rag_query_tool`, `spider_data_tool`, `system_health_tool`, `error_summary_tool`, …) was absorbed into six gateway tools: `governance_tool`, `work_tool`, `content_tool`, `intelligence_tool`, `ops_tool`, `studio_tool`. Each gateway exposes its absorbed actions via an `action` enum. | The schema budget was getting large (~30+ separate tools by then), and the model was sometimes calling redundant tools because the boundaries weren't clean (`boardroom_tool` vs `human_decisions_tool`, for instance — overlapping concepts). Six gateways gave the model fewer "wrong choices" while keeping the action surface complete. | Schema budget reduced; routing decisions cleaner; the gateway model became the canonical pattern. Subsequent tools (Session 1100's `cockpit_tool`, `narrative_tool`) follow the same pattern: one tool, multiple actions. | **Active** — six gateways are the standard. New action-set tools follow the same pattern. | `docs/topics/personal-assistant.md` §"Key tools (6 gateways — Session 1079 consolidation)" |
| **Session 1100 — `run_agent` expansion + cockpit + narrative tools** | `run_agent` meta-tool expanded to 77 agents across 12 domains. Added `cockpit_tool` (Celery ops — queue depths, worker health, beat status) and `narrative_tool` (drift analysis — what claims in docs no longer match runtime). Expanded the intelligence / work / content / governance gateways with additional actions. | The PA could call the platform's agents but had no clean way to call all of them. Operational tools (Celery ops) were happening in the terminal, not in chat — the PA couldn't help debug. Narrative/drift was a known concern (Session 1099 had introduced `verify_doc_claims`) but had no PA tool. | The PA can now: (1) run any of 77 agents by name, (2) check Celery operational health from inside a conversation, (3) ask about doc drift directly. The "operator surface" framing crystallized — Rigby is the platform's debugger as well as its conversational interface. | **Active** — `run_agent` is heavily used; `cockpit_tool` and `narrative_tool` are part of the standard ops kit. | `docs/topics/personal-assistant.md` §1 (Session 1100 reference) |
| **Sessions 1128–1133, 1142 — audit + fleet auth + search_docs** | (1128) Auth-gate-before-UI rule established for security-boundary features: service-token verification ranks above UI affordance when a feature lets system A make system B do something. (1129) Fleet auth + artifacts + SSE event stream. (1131–1133) **PA-chat audit table** — every PA call records auth posture, fleet origin, validation result. Warn-only mode pending ≥ 3 days clean telemetry before reject-mode flip. All 7 fleet repos now HMAC-sign PA chat using canonical `FLEET_APP_SLUG` / `KEY_ID` / `SERVICE_SECRET` env. **Fleet HMAC sign-key gotcha** (saved in memory): the sign key must be `sha256(raw_secret).hexdigest()`, **not** the raw secret. (1142) **`search_docs` PA tool** — chunked retrieval over `/docs/` (`.rag/corpus.jsonl` + Document table, 852/14149 chunks) with inline citations. Also `threading.Lock` on `get_unified_pa()` to make PA initialization concurrency-safe. | The PA had been a single-tenant tool. Now: fleet apps need to call her; she needs to know which fleet app called and verify the call; users need to be able to ask her "where is this documented?" without scrolling 685k-line `INDEX.md`. Three different needs, three different sessions. | The PA is now a fleet-aware service: HMAC-signed calls from 7 sibling repos, audit trail on every call, search-docs answers grounded in the corpus with citations. The audit table is warm; reject-mode flip is gated on telemetry. Concurrency safety (1142 lock) closed a class of init race that was visible in production logs. | **Active** — fleet HMAC is required for every fleet→u-d-b call; audit table is being written on every PA call; search_docs is part of the standard tool set. Reject-mode flip pending. | MEMORY.md "Session 1131-1133 arc" + "Session 1142" + `feedback_fleet_hmac_sign_with_secret_hash.md` + `feedback_auth_before_ui_security_features.md`; `docs/handoffs/SESSION_1129_*` |

---

## 4. What came of it

### Wins

- **The PA composes.** Session 1036 turned single-shot keyword
  matches into multi-tool turns. A user query that used to need
  two round-trips now resolves in one. The model picks the
  composition; the platform doesn't have to enumerate every
  possible combination in code.
- **Adding a capability is adding a schema.** Pre-1036, every
  new tool required editing the 506-line router. Post-1036,
  it's a schema entry + a dispatcher handler + an intent map
  line. The marginal cost of new PA capability dropped to near-
  zero.
- **Six gateways instead of thirty single-purpose tools** make
  routing decisions cleaner and the schema budget smaller. The
  pattern (one gateway, many actions) is the standard for new
  tool work.
- **The PA is the platform's debugger.** `cockpit_tool` +
  `narrative_tool` + `http_smoke_test` + `agent_introspection_tool`
  + `pipeline_orchestrator_tool` mean almost every operational
  question can be answered in chat instead of in a terminal.
- **Latency is tamed.** Five-second timeouts on every DB
  context step, plus 90% cached-input discount on follow-ups,
  plus async via the `pa` Celery queue, plus async polling on
  the frontend — the Railway 30-s proxy timeout no longer
  bites.
- **The PA survives worker recycling.** DB-backed memory
  (Session 1030) means a Celery `max_tasks_per_child` cycle
  doesn't blank the conversation.
- **Fleet-aware.** Sessions 1128–1133 turned the PA from a
  single-tenant chat into a service that knows which fleet app
  is calling and can verify the call cryptographically. The
  audit table is the foundation for reject-mode enforcement.

### Tradeoffs

- **Two execution paths still exist.** `PA_USE_FUNCTION_CALLING`
  toggles between GPT-5.2 function calling and the legacy
  keyword router. The fallback is documented as a safety net,
  but it carries the same drift risk as v1/v2 in the content
  pipeline — anyone running with the flag off bypasses every
  Session-1036+ improvement.
- **Tool count drift across docs.** PLATFORM_INVENTORY says
  104 schemas / 169 handlers (2026-05-25); AGENTS.md says
  105 / 170; the topic doc says 106 / 171; the architecture
  intro says "101 OpenAI function-calling schemas." None of
  these are wrong at the moment they were written; the
  authoritative source is `python manage.py
  generate_platform_inventory`.
- **ContentWriterAgent prompt-builder coupling.** Covered in
  the content-pipeline narrative; surfaced here because the PA
  routes content-generation requests through `generate_blog`
  inside `content_tool`. Anyone debugging "I told Rigby X and
  the blog doesn't reflect it" should remember
  ContentWriterAgent does **not** use
  `BaseAgent._build_intelligent_prompt()`.
- **5-iteration cap on multi-tool turns.** Most operator
  requests resolve in 1–3 calls. Genuinely complex
  multi-system queries can hit the cap; the model truncates
  and answers with what it has. There's no warning visible
  to the user.
- **`previous_response_id` is the cache key.** If the chain is
  broken (e.g., a worker restart that loses the response_id
  before the next turn), the follow-up pays full input price
  rather than the 90%-discounted cached-input price. The DB
  memory (Session 1030) reduces but doesn't eliminate this.
- **Workspace mode never inferred from text.** This is by
  design (Session 1124+); it means a user saying "in my Donkey
  Betz workspace, …" without a workspace_id will be answered
  in global scope. The behavior is correct; the UX cost is
  that users must select the workspace, not name it.
- **Reject-mode for the PA-chat audit is queued, not active.**
  Warn-mode means a misconfigured fleet app can still call the
  PA — the audit notes it but the call is not blocked. Reject
  mode is gated on ≥ 3 days of clean telemetry; Session 1134
  was supposed to flip but is in carryover.

### Follow-on systems enabled

- **The agent narrative (A)** — `run_agent` plus the 6 gateways
  are how every routable agent gets reached from chat. The PA
  is the user-facing form of "what runs."
- **The content pipeline (B)** — `content_tool` and
  `generate_blog` are how Rigby invokes deliberation. PA
  triggers the `ClaimsPack → ContentWriterAgent → 3-reviewer →
  DecisionEnforcer → PublishGate` chain.
- **The signal-intelligence chain (C)** — `work_tool` actions
  (`initiative_list`, `flow_metrics`, `assign_owner`, etc.)
  surface the entire initiative pipeline through chat.
- **The fleet** — Sessions 1128–1133's HMAC + audit table mean
  the 7 sibling Docker apps can each route their own PA-style
  calls back to Rigby with cryptographic identity. The PA is
  the fleet's brain bridge.
- **The corpus-narrative program (this doc)** — `search_docs`
  + the citation discipline of the v1 narrative template are
  Rigby's reading interface to the same corpus this doc lives
  in. When a future operator asks her "where's this
  documented?", she answers from `search_docs` over `/docs/`.

---

## 5. Current state snapshot

> Source for counts: `PLATFORM_INVENTORY.md` snapshot
> 2026-05-25 (git HEAD `d513cd7f`).

**Tool surface.** 104 tool schemas + 169 registered handlers in
the inventory snapshot. Topic doc / Session 1142 note: 106
schemas + 171 handlers. Discrepancy is timing — regenerate the
inventory for authoritative counts. 8 enrichment services
unchanged.

**Six gateways (Session 1079).** `governance_tool` (12+
actions), `work_tool` (8+), `content_tool` (14+),
`intelligence_tool` (10+), `ops_tool` (4), `studio_tool` (2).
Plus meta-tools: `run_agent`, `agent_introspection_tool`,
`status_snapshot_tool`, `check_resource_budget`,
`pipeline_orchestrator_tool`, `task_breakdown_tool`,
`brainstorm_tool`, `http_smoke_test`, `cockpit_tool`,
`narrative_tool`, `search_docs`, plus per-domain tools
(proactive, distribution, calendar, experiment, podcast,
campaign, audit, conceptforge, profile, self_awareness, ats).

**Three files own the architecture.**
- `core/services/unified_pa_entrypoint.py` — the agentic loop,
  context builder, enrichment orchestrator.
- `core/services/tool_dispatcher.py` — the 169–171 handler
  registry.
- `core/services/pa_tool_schemas.py` — the 104–106 schema list
  + intent map.

**Async path.** `POST /api/pa/chat/` → `process_pa_chat_task`
on the dedicated `pa` Celery queue with `time_limit=300 s` /
`soft_time_limit=280 s`. Frontend polls `GET
/api/pa/chat/status/<task_id>/` every 2 s. The PA worker uses
`new_event_loop()` + `run_until_complete()` — *not*
`async_to_sync`, which deadlocks.

**Execution path (function calling, default).**
`message → _build_context() → _build_messages_array() →
Responses API with the tool schema list → if tool_calls execute
via ToolDispatcher → loop up to N iterations (current cap 5) → if text,
enrichment by intent → PAResponse`. Current model: GPT-5.2 (the
default; configurable via provider registry). Schema count and
iteration cap are constants in code — treat them as authoritative
over this prose.

**Routing Truth (canonical entry → debug entrypoints).**

| Question | Canonical answer |
|---|---|
| What request path does an interactive PA call take? | `POST /api/pa/chat/` → `process_pa_chat_task` on the `pa` Celery queue → `UnifiedPAEntrypoint` agentic loop → GPT-5.2 function calling (`PA_USE_FUNCTION_CALLING=true` is the default). |
| Is there a legacy path? | Yes. The 506-line keyword router still exists, gated by `PA_USE_FUNCTION_CALLING=false`. It is not the default and should not be relied on. |
| If a tool call is "not registered" — where? | `core/services/tool_dispatcher.py`. Tool registration is per-process at import; restart workers AND daphne after schema or handler changes. |
| If a context-build step times out — where? | `_build_context()` in `core/services/unified_pa_entrypoint.py` — each step is wrapped in `asyncio.wait_for` (profile / knowledge / stats / docs / history). Adjust per-step timeouts in code, not in prose. |
| If a fleet app gets 401 — where? | HMAC sign-key validation in `core/views/pa_chat.py` (or equivalent). Key must be `sha256(raw_secret).hexdigest()`, not the raw secret. |
| If conversation cache discount is missing mid-thread — where? | `ChatConversation.metadata.response_id` was not threaded into the next turn's `previous_response_id`. Check `_apply_response_id()` or equivalent in the entrypoint. |
| If tool calls never fire / Responses API returns 429 or 5xx — where? | Provider registry config (model selection + rate limits) and the Responses-API call site in `UnifiedPAEntrypoint`. Check request logging around the model call; check for provider-side rate-limit headers. |
| If output truncates after tool calls / model stops early — where? | Multi-tool iteration cap (currently 5) in the agentic loop. Check whether the cap was hit (count `metadata.tool_calls` entries) and whether the truncation matches the cap constant. |


**Context-building timeouts.** Profile, knowledge, stats, docs
(RAG), and history each get `asyncio.wait_for` wrappers. Current
values (as-of 2026-05-25): profile 5 s, knowledge 3 s, stats 5 s,
docs 5 s, history 5 s with `SET LOCAL statement_timeout`. The
constants live in `_build_context()` — treat the code as
authoritative; this prose is a snapshot. Each step degrades
gracefully (PA continues if any one step times out).

**Enrichment pipeline (8 services).** intelligence_enricher,
blog_performance, domain_context (9 domains), spider_trends,
advisor (25 advisors), strategic_memory, proactive_intelligence,
platform_briefing. Relevance gate 15% keyword overlap on all
non-content intents.

**Conversation history.** `ChatConversation` rows with
`metadata.tool_calls` (list of `{name, arguments, call_id, ok}`),
`metadata.response_id` (for `previous_response_id` cached-input
pricing). On PA init, last 10 rows are loaded from DB to survive
Celery worker recycling.

**Cost.** First-turn: ~$0.027 / ~12K tokens. Cached follow-up:
~$0.009 (90% input discount via `previous_response_id`).

**Scopes.** `global` (default) and `workspace`. Workspace
activates only on explicit `workspace_id` /
`AssistantProfile.workspace` / workspace-aware UI context.
Workspace scope should not be inferred from message text — if you
observe message-text scope inference, that is a regression; file
it against the entrypoint's scope-resolution path.

**Fleet identity.** Every fleet-app→PA call must HMAC-sign with
`sha256(raw_secret).hexdigest()` as the key, not the raw secret.
`FleetServiceKey.secret_hash` stores the digest. Wrong key →
401 `signature_mismatch`. Required env: `FLEET_APP_SLUG`,
`KEY_ID`, `SERVICE_SECRET`. Reference impl:
`contract-concierge/backend/app/fleet_signer.py:141`.

**PA-chat audit table.** Warn-only mode. Every call records
auth posture, fleet origin, validation result. Reject-mode
flip queued on ≥ 3 days clean telemetry post-merge.

**`PA_USE_FUNCTION_CALLING` flag.** `true` (default on Railway
+ locally) → GPT-5.2 path. `false` → 506-line legacy keyword
router. Both paths still in code.

**Initialization concurrency.** `get_unified_pa()` is guarded
by `threading.Lock` (Session 1142). Call `clear_pa_cache()` to
reset state when tool registration changes during development.

**Where to look when something stops working.**
- PA returns "task_id" but status never completes → check
  the `pa` Celery queue depth + worker log; per memory rule
  `feedback_celery_pid_cache_blocks_restart`, the `pa` worker
  needs `pkill -9 -f celery; rm -f .celery*.pid; make celery`
  on tool registration changes.
- PA gives terse answers / loses prior context → check
  `ChatConversation` rows; if they exist but PA doesn't load
  them, Session 1030's `_load_conversation_history_from_db()`
  is the culprit.
- Tool calls always say "not registered" → restart workers
  AND daphne; tool registration is a per-process import.
- Fleet app gets 401 `signature_mismatch` → wrong sign key.
  Use `sha256(raw_secret).hexdigest()`, not the raw secret.
- Conversation loses cache discount mid-thread → check that
  `metadata.response_id` is being threaded into the next
  `previous_response_id`. If absent, follow-up pays full
  input price.
- Hangs on context-build for ~2+ minutes → pre-Session-1035
  state. Should not happen on current code; if it does, check the
  `asyncio.wait_for` timeouts on profile/stats/docs — one of the
  wrappers was likely removed or the underlying query is bypassing
  the `SET LOCAL statement_timeout`.
- "Search the docs" answers feel hallucinated → check
  `search_docs` returns. If empty, the embedding chunk wasn't
  found; the corpus may have drifted from the index. Run
  `python manage.py build_docs_index`.

---

## 6. Open questions / unknown outcomes

- **Tool count drift across docs.** *Known:* PLATFORM_INVENTORY
  is authoritative; topic doc / AGENTS.md / Session 1142 note
  give different numbers because they were written at
  different snapshots. *Unknown:* which exact session added
  the schemas between the snapshots — the topic doc summary
  attributes "Session 1100" for `cockpit_tool` and
  `narrative_tool` but doesn't enumerate every additional
  schema since 1100. A `git log -S "PA_TOOL_SCHEMAS"` would
  reconstruct the timeline. Worth doing once for canonical
  history.
- **Reject-mode flip for PA-chat audit.** *Known:* queued for
  Session 1134 after ≥ 3 days clean telemetry; deferred into
  carryover. *Unknown:* current telemetry status (clean? dirty?
  silent?). A `flow_metrics`-like surface for the audit table
  would surface this. Not currently exposed.
- **Cache-hit rate on `previous_response_id`.** *Known:* 90%
  discount when threaded. *Unknown:* what proportion of
  production follow-ups actually hit the cached price vs pay
  full input. Could be derived from token-accounting telemetry
  if it exists; not surfaced in the corpus.
- **Legacy keyword router usage.** *Known:* `PA_USE_FUNCTION_CALLING`
  defaults to `true`; legacy fallback still exists. *Unknown:*
  whether anything in production currently runs with the flag
  off, and whether there's any guard against it being silently
  toggled. The fallback was retained for safety; whether it's
  ever the actual execution path is not visible from the
  corpus.
- **The 5-iteration multi-tool cap.** *Known:* model truncates
  and answers from what it has. *Unknown:* how often the cap
  is hit in production, and whether truncated answers are
  detectably worse. No per-conversation cap-hit metric is
  visible in `ChatConversation.metadata`.
- **`workspace` mode discoverability.** *Known:* workspace is
  never inferred from text. *Unknown:* whether users routinely
  realize they're in global scope when they intended workspace.
  No telemetry on "user named a workspace but call was global"
  is recorded. Would surface as a UX paper-cut.
- **Enrichment cap of 1500–2000 chars per section.** *Known:*
  raised from 300–600 (Session 1006) because the lower cap
  discarded 85–95% of data. *Unknown:* whether the new cap is
  *also* discarding meaningful data on long-context intents,
  or whether 1500–2000 is close enough to the model's
  effective window for the typical query. No recent
  re-evaluation in the corpus.
- **`get_unified_pa()` lock contention.** *Known:* the lock
  (Session 1142) makes init concurrency-safe. *Unknown:* whether
  the lock is hot in production under multi-worker load. If so,
  the lock could become a bottleneck on cold-start. Not
  measured in the corpus.

---

## 7. Source index

### Primary doc sources

- `docs/topics/personal-assistant.md` — current-state topic
  doc; the closest companion to this narrative. Most session
  citations originate there.
- `docs/AGENTS.md` — `PersonalAssistantAgent` entry; covers
  delegation intent keywords from the pre-function-calling era.
- `docs/PLATFORM_INVENTORY.md` — runtime-derived inventory.
  Authoritative for tool counts.
- `docs/narratives/AGENTS_AND_AUTONOMY.md` — companion (A).
  PA cross-refs on `run_agent`, gateway routing.
- `docs/narratives/CONTENT_PIPELINE.md` — companion (B). PA
  cross-refs on `content_tool` / `generate_blog`; relevant
  footgun on ContentWriterAgent's parallel prompt-builder.
- `docs/narratives/SIGNAL_INTELLIGENCE.md` — companion (C). PA
  cross-refs on `work_tool` initiative actions + flow_metrics.

### Named session handoffs cited above

- `docs/handoffs/PA_LAYER1_SURFACE_MAP.md`
- `docs/handoffs/PA_PLATFORM_AWARENESS_SPEC.md`
- `docs/handoffs/PA_SYSTEMS_MAP_6_LAYER.md`
- `docs/handoffs/SESSION_969_ORCHESTRATION_ENRICHMENT.md`
- `docs/handoffs/SESSION_987_PA_WIRING_COMPLETION.md`
- `docs/handoffs/SESSION_993_PA_CAPABILITY_GAPS.md`
- Session 1006 — enrichment caps; topic-doc reference.
- Session 1030 — DB-backed conversation memory; topic-doc
  reference.
- Session 1035 / 1035-W2 — timeouts, agent introspection
  taxonomy, 11 new tools; topic-doc reference.
- Session 1036 — GPT-5.2 function calling; topic-doc §"Flow
  (Function Calling — Active)".
- Session 1079 — 6-gateway consolidation; topic-doc §"Key
  tools (6 gateways)".
- Session 1100 — `run_agent` expansion, `cockpit_tool`,
  `narrative_tool`; topic-doc reference.
- `docs/handoffs/SESSION_1129_*` — fleet auth + artifacts +
  SSE.
- MEMORY.md entries:
  `project_session_1131_1133_arc.md`,
  `project_session_1142_docs_hygiene_and_search_docs.md`,
  `feedback_fleet_hmac_sign_with_secret_hash.md`,
  `feedback_auth_before_ui_security_features.md`,
  `feedback_celery_pid_cache_blocks_restart.md`.

### Code anchors

- `core/services/unified_pa_entrypoint.py` — `UnifiedPAEntrypoint`
  agentic loop, context builder, enrichment orchestrator,
  `get_unified_pa()` (lock-guarded), `clear_pa_cache()`.
- `core/services/tool_dispatcher.py` — `ToolDispatcher` with
  the 169–171 handler registry.
- `core/services/pa_tool_schemas.py` — `PA_TOOL_SCHEMAS`
  (104–106 entries) + `TOOL_TO_INTENT_MAP`.
- `core/tools/http_smoke_test.py` — smoke-test runner with
  SSRF allowlist + step-dependency tracking.
- `core/tasks.py` — `process_pa_chat_task` on the `pa` queue.
- `tools/pa_chat.py` — CLI for Claude-Code → Rigby calls.
  Defaults to PROD; **must** be invoked with
  `PA_API_URL=http://localhost:8000` + local token for local
  work. `tools/pa_local.sh` is the canonical local wrapper.

### Verification commands

- `python manage.py generate_platform_inventory` — regenerate
  authoritative PA tool counts.
- `python manage.py verify_doc_claims --only-drift` — list
  which claims about the PA (counts, tools, behaviors) drift
  from runtime.
- `python manage.py build_docs_index` — refresh `docs/INDEX.md`
  + `_index.json` after any doc edit.
- `platform_config_tool overview` (PA tool, in chat) — confirm
  `service_context: local` before any local PA work. Session-
  open ritual per the LOCAL-vs-PROD trap rule.

---

## 8. Canonical sources (for future editors)

> **Reading this doc for ops decisions?** Treat code and config as
> canonical, not prose. The narrative captures *why* the PA is
> the shape it is; runtime captures *what she is now*.

| Question | Canonical source (code/config wins over prose) |
|---|---|
| Tool schema + handler counts (104 / 106 / 169 / 171) | `python manage.py generate_platform_inventory` |
| LLM model + provider (e.g., "GPT-5.2") | Provider registry config — model is configurable |
| Context-build timeouts (5 s / 3 s / 5 s / 5 s / 5 s) | Constants in `_build_context()` |
| Multi-tool iteration cap (currently 5) | Constant in `UnifiedPAEntrypoint` agentic loop |
| Frontend poll cadence (every 2 s) | Constant in the frontend PA chat client |
| Railway proxy timeout (~30 s) | Railway platform config, not application code |
| Enrichment char caps (1500–2000) | Constants in enrichment service modules |
| Cached-input discount math (90%) | OpenAI Responses-API pricing — see provider docs |
| Fleet HMAC sign-key recipe | `sha256(raw_secret).hexdigest()` — code path in `core/services/fleet_*` |
| `PA_USE_FUNCTION_CALLING` default | Env var; default is `true` on Railway + locally |
| PA-chat audit table mode (warn vs reject) | Config flag + the audit middleware |

If you spot drift between this doc and code/config, **code wins**
and this doc should be corrected. See
[`docs/narratives/EDITING_GUARDRAILS.md`](EDITING_GUARDRAILS.md)
for the editing contract.

