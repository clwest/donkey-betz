# `content_writer_agent` — Validation Report (S2928)

**Tool:** `content_writer_agent`
**Schema:** `core/services/pa_tool_schemas.py:1906`
**Handler:** `core/services/tool_dispatcher.py:1196` (`_handle_agent_tool` — SHARED across all Slice 5 agent-forwarding tools)
**Register site:** `core/services/tool_dispatcher.py:333`
**Session:** S2928 (Slice 5 batch 4 — FINAL pair with `image_editing_agent`; CLOSES Slice 5 at 14/14)
**HEAD at validation:** `596e2620b` (2026-07-24 — post S2927 close-cascade amendment)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. **Batch 4 ContentWriterAgent completion-verify representative** — highest-signal candidate for content-shape FAIL 2nd-instance surface (Rigby T0 SIGN Q2 verdict; 1st instance was S2926 CompetitorAnalysisAgent).
**Category upgrade target:** `untested` → `validated_full_with_completion`
**Rigby SIGN:** S2928 T0 SIGN Q1–Q5 verdict — Q1 pair + follow-ups approved (fork A doc-only close, Chris D-verdict); Q2 verdict YES on completion-verify representative (persists Deliverable rows in-agent, rich nested output, content-shape FAIL risk class); Q4 Slice 5 CLOSE artifact recommended; Q5 zoom-out Fold sketch pre-written for content-shape FAIL if triggered.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`content_writer_agent` dispatches `ContentWriterAgent` (`core/agents/content_writer_agent.py:207`) asynchronously via Celery `execute_agent_task` on the `long_running` queue. `ContentWriterAgent` is a **structured content-generation agent** that transforms research context into professional written content across 7 content types (`content_writer_agent.py:130-193`): `blog_post`, `podcast_script`, `video_script`, `article`, `social_thread`, `newsletter`, `internal_document`. The tool also auto-persists output to a `Deliverable` row (`content_writer_agent.py:1193-1202` — `_save_to_deliverable`) as a `document` deliverable_type under `Content Writing` category with tags for content_type + tone. This makes ContentWriterAgent the highest-signal Slice 5 completion-verify representative for content-shape FAIL surfaces (Rigby T0 SIGN Q2 verdict), because it (a) emits nested `AgentResult.data` with `content`/`metadata`/`provenance` fields, (b) separately persists a Deliverable using `generated_content.get('full_text', '')` — a distinct extraction path from the AgentResult data envelope, and (c) is already documented at `td_handlers_agents.py:170-171` as requiring deep extraction (`metadata.content.full_text (or metadata.full_text)`).

Session 1184 PR-D promoted `content_type` from a freeform `context` key to a top-level enum-constrained schema field (`pa_tool_schemas.py:1920-1946`) — before that fix, GPT-5.2 could pick invalid content_types (e.g. `"deliverable"`) which failed dispatch hard and broke provenance forensic runs. The current schema enum enforces one of the 7 known content types.

## Covered actions

`content_writer_agent` is an agent-forwarding tool — the caller passes `task` (writing task string) + optional top-level `content_type` (enum) + optional `context` dict; the tool dispatches `ContentWriterAgent.execute(task, context)` asynchronously. There are no per-tool `action` enum values.

- **`dispatch` (implicit, only mode)** — **in scope this ship — receipt-shape verified live + end-to-end completion verified.** Envelope: `{task_id: <uuid>, mode: 'async', agent: 'ContentWriterAgent', auto_followup: <bool>, follow_up_will_fire: <bool>, message: 'ContentWriterAgent dispatched (task <uuid>). Use job_status to check progress.'}`. Follow-up `job_status` returns AgentResult carrying `content_type`, `title`, `word_count`, `tone`, `target_audience`, `content` (dict with `full_text` and content-type-specific structure), `metadata` (nested with `topic`/`quality_tier`/`confidence`/`truncated`), `provenance` (dict), `publishable` (bool), `validation_status` (str) keys (`content_writer_agent.py:1121-1143`). Parallel side-effect: `Deliverable` row INSERT with `full_text` extraction (`:1193-1202`) — Deliverable id is NOT surfaced in AgentResult.data (secondary-identifier UX gap; documented as Ledger candidate).

## 3. Schema notes

Shared shape as all Slice 5 agent-forwarding tools **plus** one Slice-5-unique top-level enum field:

- **Required:** `task` (per schema `required: ['task']` at `pa_tool_schemas.py:1952`). Handler still accepts `payload.get('task') or payload.get('prompt') or payload.get('query', '')` at `tool_dispatcher.py:1224`.
- **Optional top-level enum (Slice-5-unique):** `content_type` — enum-constrained to `['blog_post', 'podcast_script', 'video_script', 'article', 'social_thread', 'newsletter', 'internal_document']` per schema at `pa_tool_schemas.py:1930-1946`. Promoted to top-level in Session 1184 PR-D to prevent GPT-5.2 from injecting invalid values via freeform `context`. Present in `_CONTEXT_PROMOTE_KEYS` at `tool_dispatcher.py:1186` so it flows through the wrapper into the agent's context dict.
- **Optional:** `context` (dict). Root-level promotable keys per `_CONTEXT_PROMOTE_KEYS` at `tool_dispatcher.py:1184-1194` — `tone`, `target_audience`, `word_count`, `topic`, `keywords`, `content`, `research`, `research_summary`, `blog_id`, `focus_areas`, plus `workspace_id`/`workspace`/`conversation_id`/`auto_followup`.
- **User scoping:** `context['user_id'] = str(user_id)` injected at `tool_dispatcher.py:1234-1235` when `user_id` present.
- **Evidence-first override:** if `_evidence_context_override` is set on the agent instance, spider/domain/performance context injection is skipped (`content_writer_agent.py:451-505`). This is a Session 1103 hardening — spider URLs contaminate output when evidence is available.
- **Tool_name is NOT propagated to ContentWriterAgent** — the wrapper resolves tool_name → agent class name via `_tool_to_agent_name` at `td_handlers_agents.py:115` and dispatches `execute_agent_task.apply_async(args=['ContentWriterAgent', task_text, context], queue='long_running')`. Content-type routing therefore comes exclusively from `context.content_type` (via the promoted top-level enum) — no per-tool differentiation at dispatch.

## 4. Golden-path examples

**Example 1 — blog post with explicit content_type + tone:**
```json
{"task": "Write a blog post about workflow orchestration patterns in modern AI platforms", "content_type": "blog_post", "context": {"tone": "professional", "target_audience": "senior engineers", "word_count": 1200, "workspace_id": "<uuid>"}}
```
Expected dispatch envelope: `{"task_id": "<celery-uuid>", "mode": "async", "agent": "ContentWriterAgent", "auto_followup": true, "follow_up_will_fire": <bool>, "message": "ContentWriterAgent dispatched (task <celery-uuid>). Use job_status to check progress."}`.

Follow-up completion via `job_status`: AgentResult with `data.content_type = "blog_post"`, `data.title = "<generated>"`, `data.word_count = <int>`, `data.content = {full_text: "...", ...}` (blog_post structure includes headers/sections/conclusion/SEO metadata per `content_writer_agent.py:132-149`), `data.metadata.quality_tier`, `data.provenance` (dict), `data.publishable` (bool). Deliverable row inserted with title `"blog_post: Write a blog post about workflow orchestration patterns..."` (`:1196`), `deliverable_type='document'`, `category='Content Writing'`, `tags=['blog_post', 'professional']`.

**Example 2 — internal document (diagnostic/planning):**
```json
{"task": "Write an internal handoff document summarizing the S2927 workflow_orchestration_agent mapping fix", "content_type": "internal_document", "context": {"tone": "technical", "target_audience": "engineering team", "word_count": 800, "workspace_id": "<uuid>"}}
```
Expected: identical envelope shape to Example 1. `internal_document` content_type routes through `content_writer_agent.py:188-193` (structure: `title`, `executive_summary`, `sections`, `key_findings`, `recommendations`). Non-publishable — appropriate for handoffs, technical specs, planning notes.

## 5. Failure / empty-state / pagination notes

- **Missing task text:** `task_text` reaches ContentWriterAgent as empty string; the agent returns `success=False` with `error` field populated from the caught exception.
- **Invalid content_type:** schema enum at `pa_tool_schemas.py:1932-1940` enforces client-side (GPT-5.2 tool-call validation); any invalid value received at handler level would key-miss in `CONTENT_TYPES` (`content_writer_agent.py:130-193`) and produce a KeyError caught by the outer try (`:1206-1213`).
- **LLM timeout:** `llm_timeout = 180.0` (`content_writer_agent.py:218`) — long-form content generation may exceed the default. Session 1074 raised the ceiling; if breached, the OpenAI HTTP call raises TimeoutError caught by the outer try.
- **Deliverable persistence failure:** `_save_to_deliverable` at `:1193-1202` runs AFTER the AgentResult is constructed. A DB error at persistence time is caught by the outer try and rewrites the return as `success=False` — but the AgentResult was already constructed with a valid content payload; that content is **lost** in the failure path (documented behavior — Session 1006).
- **Blocked agent / focus mode / demo mode / circuit breaker:** downstream gates in `_impl_execute_agent_task` may short-circuit; envelope surfaces `error_code` distinct from `AGENT_EXECUTION_FAILED`.
- **`follow_up_will_fire: false`:** if `context.conversation_id` is absent OR `context.auto_followup == False`, the S1178 auto-wake subscription will NOT fire.
- **Evidence-vs-spider contention (Session 1103):** if both `_evidence_context_override` AND spider/domain context are supplied, evidence wins; spider context is discarded to prevent URL contamination.
- **Provenance stale threshold:** `stale_threshold_hours=72.0` (`content_writer_agent.py:1098`) — content sources older than 72 h mark the AgentResult as `publishable=False` regardless of content quality.

## 5a. Mutation containment (per Rigby SIGN Q3 — §5a 4-tier blast-radius taxonomy; Slice 5 classification = end-to-end wrapper + mapped agent behavior)

`content_writer_agent` is classified `external` when scored end-to-end, and **amplified** by (i) LLM egress per invocation, (ii) auto-Deliverable INSERT with post_save signal cascade, and (iii) AgentMemory INSERT for content memory (`content_writer_agent.py:1297-1299`).

| Facet | Wrapper (`_handle_agent_tool`) | Downstream (`ContentWriterAgent` + Celery task + Deliverable + AgentMemory) | End-to-end tier |
|---|---|---|---|
| Process boundary | Same-process | Celery worker (`long_running`) | `external` |
| Data mutation | None | AgentExecution + AgentResult INSERTs; Deliverable INSERT (auto — `_save_to_deliverable`); AgentMemory INSERT (`_create_content_memory`); LLMCallLog rows per LLM call; SharedKnowledge INSERT (`_share_knowledge`) | `spreading` → `cascading` (downstream, amplified — Deliverable post_save signal chain fires deliverable_status_signals + deliverable_mirror_signals + document_processing_signals) |
| Signal cascade | None | Agent lifecycle signals; **Deliverable post_save chain** (deliverable_status + deliverable_mirror + document_processing); AgentMemory post_save; potential AttentionItem creation (`_maybe_create_attention_item`); potential AgentFollowupSubscription INSERT | `cascading` (downstream, amplified — Deliverable is a high-fanout signal target) |
| Network egress | None | OpenAI/Anthropic LLM API call (`llm_timeout=180s`); optional web_search / spider queries (skipped in evidence-first mode) | `external` |

**End-to-end classification:** `external`. Amplification is bounded by (a) single LLM call per invocation (no fanout to sub-agents at the Slice 5 boundary — ContentWriterAgent may internally invoke `delegate_to_specialist` per its system prompt at `content_writer_agent.py:247-255`, but that path is agent-internal and not exercised at receipt-verify), (b) one Deliverable per invocation, (c) one AgentMemory per invocation. Per Rigby S2925 Q2 authoring guidance: Slice 5 tools MUST be classified end-to-end; ContentWriterAgent's blast radius extends into Deliverable-mirror post_save cascade, which is why it is a high-signal completion-verify representative (S2928 Rigby T0 SIGN Q2 verdict).

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `self._tool_to_agent_name('content_writer_agent')` → `'ContentWriterAgent'` | `read` | `tool_dispatcher.py:1222` + `td_handlers_agents.py:115` | Name resolution; no side effect |
| `context[<promoted keys>] = payload[<key>]` incl. `content_type` enum | `read` | `tool_dispatcher.py:1230-1232` + `_CONTEXT_PROMOTE_KEYS:1184-1194` | In-memory dict; no persistence |
| `reroute_synthesis_to_content_writer(...)` | `read` | `tool_dispatcher.py:1245-1250` | Pure function; NB — this reroute TARGETS this handler for Editor→ContentWriter re-routes |
| `apply_smoke_allowlist(context)` | `read` | `tool_dispatcher.py:1325-1326` | Context filter; no persistence |
| `execute_agent_task.apply_async(args=['ContentWriterAgent', task_text, context], queue='long_running')` | `dispatch` | `tool_dispatcher.py:1330` | Celery async dispatch; opaque callee — see Appendix A |

### Appendix A — Async-Fanout (first-hop = Celery `apply_async`)

- **A1. Dispatch target type(s):** `agent_task_wrapper` — `execute_agent_task` (`core/tasks.py:1131`) → `_impl_execute_agent_task` (`core/tasks_agents.py:2077`) → `ContentWriterAgent.execute` (`core/agents/content_writer_agent.py`).
- **A2. Queue name(s) + priority:** `long_running` queue. Priority not set.
- **A3. Task_id envelope + polling contract:**
  - (a) **Identifiers returned:** `task_id` (Celery UUID). **Secondary domain identifier NOT surfaced:** the auto-created Deliverable id (from `_save_to_deliverable`) is NOT in the AgentResult data — callers must query `Deliverable.objects.filter(...)` by title/tags/timing to find it. This is a known secondary-identifier UX gap (same shape as other content-tier tools).
  - (b) **Polling endpoint(s):** `job_status` PA tool for parent completion; ORM traversal `Deliverable.objects.filter(agent_source='ContentWriterAgent', ...)` for the auto-persisted document.
  - (c) **Idempotency stance:** `none`. Repeat dispatches = independent Celery tasks + AgentExecution rows + duplicated Deliverable rows (auto-persistence has no dedup).
- **A4. Downstream side-effect boundary** (per `_impl_execute_agent_task` + `ContentWriterAgent.execute`):
  - Parent AgentExecution INSERT + status transitions.
  - LLM planning call (LLMCallLog INSERT).
  - AgentResult INSERT (post-run) with `content_type`, `title`, `word_count`, `tone`, `target_audience`, `content` (dict), `metadata`, `provenance`, `publishable`, `validation_status`.
  - **Deliverable INSERT** via `_save_to_deliverable` (`:1195-1202`) — triggers deliverable_status_signals + deliverable_mirror_signals + document_processing_signals post_save chains.
  - **AgentMemory INSERT** via `_create_content_memory` (`:1215+`) — post_save signal cascade.
  - SharedKnowledge INSERT via `_share_knowledge` (`:1178-1188`).
  - Optional AttentionItem creation via `_maybe_create_attention_item` (`:1191`).
  - Optional AgentFollowupSubscription INSERT if `conversation_id` set + `auto_followup` not `False`.
- **A5. Observability + cancel semantics + revisit triggers:**
  - (a) **Observability contract:** parent AgentExecution + AgentResult keyed on parent `celery_task_id`. Deliverable row lookup via `agent_source` + title match. `job_status` surfaces the parent composite view via `_get_agent_execution_output` deep extraction (`td_handlers_agents.py:165-174` documents `ContentWriterAgent: metadata.content.full_text (or metadata.full_text)` extraction — path-tolerance for the known shape variance).
  - (b) **Cancel semantics:** `celery.control.revoke(task_id, terminate=False)` on the parent halts the Celery task. If revoke fires AFTER LLM call completes but BEFORE `_save_to_deliverable` runs, the AgentResult was constructed but Deliverable will not persist — a partial-state hazard. No compensating rollback.
  - (c) **Revisit triggers:** `_handle_agent_tool` changes; `_tool_to_agent_name` row at `td_handlers_agents.py:115`; `execute_agent_task` routing; `_CONTEXT_PROMOTE_KEYS` at `tool_dispatcher.py:1184-1194` (especially `content_type`/`tone`/`target_audience`/`word_count`); `CONTENT_TYPES` structure at `content_writer_agent.py:130-193`; content_type schema enum at `pa_tool_schemas.py:1930-1946`; `_save_to_deliverable` behavior; Session 1103 evidence-first mode; deep-extraction contract at `td_handlers_agents.py:165-174`.

## 6. Evidence

Doc-only sweep this ship, plus **end-to-end completion verification** as batch 4's ContentWriterAgent completion-verify representative (Rigby T0 SIGN Q2 verdict — highest-signal content-shape FAIL 2nd-instance surface).

Post-merge Rigby live-dispatch verification protocol:

1. Dispatch `content_writer_agent` with a minimal `task` string + `content_type='internal_document'` (least resource-intensive) + `context` with `tone`/`target_audience`/`word_count` via PA. Confirm dispatch envelope matches `{task_id, mode: 'async', agent: 'ContentWriterAgent', auto_followup, follow_up_will_fire, message}`. **Critical: confirm `agent` field is `'ContentWriterAgent'`** (mapping verification per S2927 PR #3487 pattern).
2. Poll `job_status` with the returned `task_id` until completion or timeout. Confirm completion payload contains ContentWriterAgent AgentResult with the structured data keys (`content_type`, `title`, `word_count`, `tone`, `target_audience`, `content`, `metadata`, `provenance`, `publishable`, `validation_status`).
3. **Content-shape FAIL 2nd-instance check (Q5 Fold trigger):** compare AgentResult `data.content` extraction path with the deep-extraction contract at `td_handlers_agents.py:170-171`. If the completion payload surfaces content at `data.content.full_text` (dict-shape) OR at `data.metadata.content.full_text` (nested shape) OR only at the auto-persisted Deliverable (no top-level content) — this is a **content-shape FAIL 2nd instance** (1st was S2926 CompetitorAnalysisAgent). Per Rigby T0 SIGN Q5 pre-written Fold sketch: promote to Fold in the same batch PR.
4. **Deliverable auto-persistence verification:** ORM query `Deliverable.objects.filter(agent_source='ContentWriterAgent', created_at__gte=<dispatch_time>).order_by('-created_at').first()` — confirm a Deliverable row was auto-inserted with `deliverable_type='document'`, `category='Content Writing'`, tags including the content_type + tone values. If Deliverable is absent despite AgentResult success — persistence-vs-envelope decoupling hazard confirmed.
5. **`_save_to_deliverable` full_text extraction check:** confirm the auto-persisted Deliverable's `content` field is non-empty. Path is `generated_content.get('full_text', '')` at `:1194`; if `generated_content` is a plain string OR lacks a `full_text` key, the Deliverable body falls back to `result.message` (per `:1197`) — a degraded-content shape not documented in the schema.

## Related

- **Adjacent tool (same Slice 5 batch 4):** `image_editing_agent` (media-family; receipt-verify only).
- **Sibling content-tier tools (Slice 5):** `content_strategy_agent` (S2927 batch 3 receipt-verify — ContentStrategyAgent), `marketing_strategy_agent` (S2927 batch 3 receipt-verify — content-shape FAIL 2nd-instance flagged; bundled completion-verify this ship), `strategic_review` (S2927 batch 3 receipt-verify — ContentStrategyAgent alias), `brand_strategy_agent` (S2925 batch 1 — BaseBusinessResearchAgent), `competitor_analysis_agent` (S2925 batch 1 — content-shape FAIL 1st instance surfaced at S2926 completion-verify).
- **Content-shape FAIL Fold ladder (pre-written per Rigby T0 SIGN Q5(i)):** if this ship's completion-verify OR the bundled `marketing_strategy_agent` completion-verify surfaces a 2nd content-shape FAIL instance (schema-vs-actual-output envelope mismatch: `data.content` vs `metadata.content.full_text` vs `output.content`), promote as a distinct Fold. Standardization candidate: `{ metadata: { content: { full_text, title, sections? }, ... }, deliverable_id? }` with schema validation + lint.
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1); `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 5 = 2 untested pre-batch-4).
- **Prior ratifications:** S2892 Path B open; S2917 Slice 3 CLOSE; S2924 Slice 4 CLOSE; S2921 §5a 4-tier taxonomy; S2925 Slice 5 batch 1 quartet; S2926 Slice 5 batch 2 quartet; S2927 Slice 5 batch 3 quartet (advanced Slice 5 to 12/14).
- **Shared infrastructure notes:** shared `_handle_agent_tool` at `tool_dispatcher.py:1196`; shared `_tool_to_agent_name` at `td_handlers_agents.py:83-163`; ContentWriterAgent implementation at `core/agents/content_writer_agent.py` (2,419 lines — the largest Slice 5 agent by size). Deep-extraction contract at `td_handlers_agents.py:165-174` explicitly names ContentWriterAgent + shape variance the extractor tolerates.
- **Ledger rows relevant to this ship:**
  - **Content-shape FAIL Fold candidate** — ladder at 1/2 pre-batch-4 (S2926 CompetitorAnalysisAgent). This ship's completion-verify + the bundled `marketing_strategy_agent` completion-verify are the 2nd-instance triggers. If either fires, ship the Fold promotion in the same batch PR.
  - **Secondary-identifier UX gap** — auto-created Deliverable id is not surfaced in AgentResult.data; callers must ORM-query. Same shape as other content-tier tools; ladder unchanged at 1st documented.
  - **Deliverable-persistence-vs-AgentResult decoupling** — Deliverable persistence failure after AgentResult construction loses the content payload. 1st documented instance this ship; watch for 2nd in Slice 6+ auto-persisting tools.
