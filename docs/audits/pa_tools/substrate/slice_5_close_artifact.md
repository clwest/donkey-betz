# Slice 5 CLOSE artifact — agent-forwarding authoring pattern (S2928)

**Purpose:** Codify the Slice 5 authoring/runtime conventions for agent-forwarding tools so Slice 6+ sweep does not drift from the shape ratified across batches 1-4. Analogous to S2924's Slice 4 CLOSE §5a tier distribution table — this artifact captures Slice 5's distinct architectural shape (single shared handler + single shared mapping + shared async envelope + shared post-persistence extension points).

**Slice 5 scope:** 14 tools registered in `core/services/tool_dispatcher.py`, all dispatching through `_handle_agent_tool` at `tool_dispatcher.py:1196`, all resolving tool_name → agent class via `_tool_to_agent_name` at `core/services/td_handlers_agents.py:83-163`, all async on the `long_running` Celery queue.

**Structural shift from Slices 1-4:** Slices 1-4 used per-file multi-action handlers (e.g. `td_handlers_ops.py` had ~17 tools each with a per-action handler and per-tool internal action-enum switch). Slice 5 collapses to **one handler function serving 14 tools**, with the only per-tool differentiation being the agent class name resolved at dispatch time. This changes the blast radius of a change inside `_handle_agent_tool` from 1-2 tools (Slices 1-4) to all 14 Slice 5 tools + any Slice 6+ tools that adopt the same shape.

**Rigby T0 SIGN Q4 verdict (S2928):** RECOMMEND ship as Slice-close artifact. Rationale: "If you don't write this artifact, you're relying on tacit knowledge right before Slice 6+ expands the surface area." Fork A (doc-only close) ratified by Chris at S2928 T0.

---

## 1. Slice 5 tool inventory (14 tools, 4 batches)

| # | Tool | Batch | Session | Agent class | Register site | Mapping row | Doc |
|---|---|---|---|---|---|---|---|
| 1 | `brand_strategy_agent` | 1 | S2925 | `BrandStrategyAgent` | `tool_dispatcher.py:330` | `td_handlers_agents.py:112` | [brand_strategy_agent_validation.md](../../research/tools/validation/brand_strategy_agent_validation.md) |
| 2 | `competitor_analysis_agent` | 1 | S2925 | `CompetitorAnalysisAgent` | `:328` | `:110` | [competitor_analysis_agent_validation.md](../../research/tools/validation/competitor_analysis_agent_validation.md) |
| 3 | `customer_research_agent` | 1 | S2925 | `CustomerResearchAgent` | `:329` | `:111` | [customer_research_agent_validation.md](../../research/tools/validation/customer_research_agent_validation.md) |
| 4 | `create_project_from_research` | 1 | S2925 | `WorkflowAgent` | `:457` | `:130` | [create_project_from_research_validation.md](../../research/tools/validation/create_project_from_research_validation.md) |
| 5 | `create_brand_video` | 2 | S2926 | `WorkflowAgent` | `:456` | `:129` | [create_brand_video_validation.md](../../research/tools/validation/create_brand_video_validation.md) |
| 6 | `video_editing_agent` | 2 | S2926 | `VideoEditingAgent` | `:315` | `:90` | [video_editing_agent_validation.md](../../research/tools/validation/video_editing_agent_validation.md) |
| 7 | `three_d_generation_agent` | 2 | S2926 | `ThreeDAgent` | `:319` | `:93` | [three_d_generation_agent_validation.md](../../research/tools/validation/three_d_generation_agent_validation.md) |
| 8 | `character_training_agent` | 2 | S2926 | `CharacterTrainingAgent` | `:320` | `:94` | [character_training_agent_validation.md](../../research/tools/validation/character_training_agent_validation.md) |
| 9 | `workflow_orchestration_agent` | 3 | S2927 | `WorkflowOrchestrationAgent` | `:455` | `:126` | [workflow_orchestration_agent_validation.md](../../research/tools/validation/workflow_orchestration_agent_validation.md) |
| 10 | `content_strategy_agent` | 3 | S2927 | `ContentStrategyAgent` | `:331` | `:113` | [content_strategy_agent_validation.md](../../research/tools/validation/content_strategy_agent_validation.md) |
| 11 | `marketing_strategy_agent` | 3 | S2927 | `MarketingStrategyAgent` | `:332` | `:114` | [marketing_strategy_agent_validation.md](../../research/tools/validation/marketing_strategy_agent_validation.md) |
| 12 | `strategic_review` | 3 | S2927 | `ContentStrategyAgent` (alias) | `:458` | `:131` | [strategic_review_validation.md](../../research/tools/validation/strategic_review_validation.md) |
| 13 | `content_writer_agent` | 4 | S2928 | `ContentWriterAgent` | `:333` | `:115` | [content_writer_agent_validation.md](../../research/tools/validation/content_writer_agent_validation.md) |
| 14 | `image_editing_agent` | 4 | S2928 | `ImageEditingAgent` | `:313` | `:88` | [image_editing_agent_validation.md](../../research/tools/validation/image_editing_agent_validation.md) |

**Family distribution:** 5 media (image/video/3D/character training) · 5 strategy/content (brand/competitor/customer research/content strategy/marketing) · 2 workflow orchestrators (WorkflowAgent LLM-planner + WorkflowOrchestrationAgent template) · 1 content writer · 1 alias.

**Multi-tool → single-class instances (mapping-level):** 3 verified in the mapping at `td_handlers_agents.py:83-163`:
1. `content_strategy_agent` + `strategic_review` → `ContentStrategyAgent` (S2927 batch 3 — 2nd instance at Chris's validation-based ladder; the alias is Session 1068 legacy).
2. `security_agent` + `memory_isolation_agent` → `MemoryIsolationAgent` (mapping at `:158-159` — NOT in Slice 5; candidate 3rd instance when Slice 6+ validates `security_agent`).
3. `create_brand_video` + `create_project_from_research` → `WorkflowAgent` (S2925 + S2926 — validated at both endpoints; intentional per delegate-pattern rationale).

---

## 2. Shared dispatcher contract (`_handle_agent_tool`)

**Location:** `core/services/tool_dispatcher.py:1196-1330+`.

**Signature (behavior contract, not literal Python):**
```
_handle_agent_tool(tool_name: str, payload: dict, user_id: Optional[int], timeout: Optional[int]) -> ToolResult
  where ToolResult.result = {
    'task_id': <celery_uuid>,
    'mode': 'async',
    'agent': <resolved_agent_class_name>,   # from _tool_to_agent_name
    'auto_followup': <bool>,
    'follow_up_will_fire': <bool>,
    'message': f"{agent_class_name} dispatched (task {celery_uuid}). Use job_status to check progress."
  }
```

**Invariants (verified across 14 tools):**
1. **Envelope shape is uniform.** `task_id` + `mode='async'` + `agent` + `auto_followup` + `follow_up_will_fire` + `message`. No tool deviates. This is the receipt-verify signal for all Slice 5 tools.
2. **`agent` field always reflects the resolved class name.** This is the primary integrity signal — S2927 PR #3487 fixed a case where `workflow_orchestration_agent` incorrectly resolved to `WorkflowAgent` instead of `WorkflowOrchestrationAgent`. The fix + regression test (`core/tests/test_tool_to_agent_name_mapping.py`) established the pattern: envelope `agent` field is the ground truth for mapping correctness.
3. **Dispatch is always Celery `apply_async(queue='long_running')`.** No Slice 5 tool routes to a different queue. `tool_dispatcher.py:1330`.
4. **User scoping is uniform.** `context['user_id'] = str(user_id)` injection at `:1234-1235` for authenticated calls; no per-tool override.
5. **Context promotion is uniform.** `_CONTEXT_PROMOTE_KEYS` at `:1184-1194` — root-level payload keys pulled into `context` dict before dispatch. Currently promotes `workspace_id`, `workspace`, `conversation_id`, `content_type`, `tone`, `target_audience`, `word_count`, `topic`, `keywords`, `blog_id`, `focus_areas`, `content`, `research`, `research_summary`, `auto_followup`. Any Slice-6+ tool needing a top-level key must extend this list (schema addition + `_CONTEXT_PROMOTE_KEYS` addition).
6. **Editor→ContentWriter reroute is Slice-5-active.** `reroute_synthesis_to_content_writer` at `:1245-1250` applies to Editor-agent invocations. No other reroutes exist in the handler.
7. **Smoke allowlist filter runs post-promote.** `apply_smoke_allowlist(context)` at `:1325-1326` — filters context for smoke-test invocations; no-op in production.

**Blast radius of a change to `_handle_agent_tool`:** 14 Slice 5 tools + any Slice 6+ tools that adopt the same handler. This centralization is deliberate; it also means shape drift is 14x amplified.

---

## 3. Shared tool→agent mapping (`_tool_to_agent_name`)

**Location:** `core/services/td_handlers_agents.py:83-163` (single dict `mappings`).

**Contract:** `_tool_to_agent_name(tool_name: str) -> str` returns the agent class name to dispatch. Fallback (line 163) is `tool_name.replace('_agent', '').title() + 'Agent'` — this is a **naming-convention inference** used for un-mapped tool names; any mismatch between the fallback shape and the actual class name is a latent bug (S2927 PR #3487 pattern).

**Sections in the mappings dict (Slice 5-relevant):**
- **Media Creation & Editing** (`:87-95`) — 9 tools, all end with `_agent`.
- **Research & Analysis** (`:97-101`) — 5 tools, all end with `_agent`.
- **Strategy & Content** (`:103-108`) — 6 tools.
- **Business Research** (`:110-115`) — 6 tools (includes content_writer_agent + Slice 5 batch 1 quartet + marketing_strategy_agent).
- **Executive & Orchestration** (`:117-126`) — 7 tools (includes workflow_orchestration_agent — the WorkflowOrchestrationAgent-family representative).
- **Legacy aliases** (`:128-132`) — includes `strategic_review → ContentStrategyAgent` (multi-tool-single-class).

**Regression test coverage:** `core/tests/test_tool_to_agent_name_mapping.py` (3 tests, shipped at S2927 PR #3487). Verifies workflow_orchestration_agent → WorkflowOrchestrationAgent + docstring pattern + full-mapping snapshot. **This is the only executable invariant currently protecting the Slice 5 mapping.** Fork A close-shape defers additional invariants (schema lint / output-envelope assertion) to a dedicated Slice 5-hardening session before Slice 6 opens.

**Adding a new Slice-6+ agent-forwarding tool checklist:**
1. Add schema in `core/services/pa_tool_schemas.py` (follow the shape at `:1674` or `:1906`).
2. Add mapping in `_tool_to_agent_name` at `td_handlers_agents.py` (place under the matching section header comment).
3. Register handler in `tool_dispatcher.py` — `self.register("<tool_name>", self._handle_agent_tool)`.
4. Optionally extend `_CONTEXT_PROMOTE_KEYS` at `tool_dispatcher.py:1184-1194` if the new tool needs a top-level promotable key.
5. Extend `core/tests/test_tool_to_agent_name_mapping.py` if the new mapping is non-obvious (aliases, multi-tool-single-class, or `_agent`-suffix asymmetries).

---

## 4. Output envelope expectations (`AgentExecution.output_data` deep-extraction contract)

**Location:** `core/services/td_handlers_agents.py:165-200+` (`_get_agent_execution_output` — the completion-verify surface).

**Deep-extraction contract (Session 1088-1089):**
- `ContentWriterAgent`: `metadata.content.full_text (or metadata.full_text)` — path-tolerant extraction for the known Session-1006 shape variance.
- `ImageAgent`: `metadata.images[*].url`.
- `VideoAgent` / `AudioAgent` / `TalkingCharacterAgent`: metadata media URLs.
- `WorkflowOrchestrationAgent`: `data.workflow` + `data.step_results` + `data.image_ids` + `data.video_ids` + `data.project_created` + `data.summary` (template-driven bounded fanout envelope; `workflow_orchestration_agent.py:313-320`).
- `WorkflowAgent`: LLM-planner unbounded fanout envelope (details in `create_brand_video_validation.md` + `create_project_from_research_validation.md`).

**Slice 5 completion-verify signal:** the envelope-shape variance is a known-tolerated surface. Content-shape FAIL (schema-vs-actual-output envelope mismatch) is the diagnostic pattern; ladder at 1st documented instance post-S2926 (CompetitorAnalysisAgent). S2928 batch 4 completion-verify of `content_writer_agent` + bundled `marketing_strategy_agent` completion-verify are the 2nd-instance triggers.

**Content-shape FAIL Fold sketch (pre-written per Rigby T0 SIGN Q5(i)):**
- **Trigger:** AgentExecution output cannot be normalized into the expected content envelope for downstream extraction/publishing.
- **Signature:** mismatch between where content is stored (`data.content` vs `metadata.content.full_text` vs `output.content`), OR required fields missing after dispatcher context-promote step.
- **Standardization candidate (if promoted):** enforce `{ metadata: { content: { full_text, title, sections? }, ... }, deliverable_id? }` shape for content agents via schema validation + lint gate.
- **Executable invariant candidate (deferred to Slice 5-hardening session per fork A):** output-envelope assertion test for content agents.

---

## 5. Known reroutes + context promotion rules

**Editor→ContentWriter reroute:** `reroute_synthesis_to_content_writer` at `tool_dispatcher.py:1245-1250` — if the resolved agent is `EditorAgent` AND the task text matches "synthesis" heuristic, reroute to `ContentWriterAgent`. Slice-5-active but not commonly triggered (no `editor_agent` in Slice 5; only relevant when Editor delegation chains through the dispatcher).

**Smoke allowlist:** `apply_smoke_allowlist(context)` at `:1325-1326` — filters context for smoke-test invocations to prevent smoke tests from persisting production side effects. Uses `context['smoke_test']` marker; no-op if absent.

**Context promotion order (verified):**
1. Payload arrives at handler with top-level keys.
2. `_CONTEXT_PROMOTE_KEYS` list drives promotion: root-level keys are moved into `context` dict (`:1230-1232`).
3. `user_id` injection follows (`:1234-1235`).
4. Reroute check (`:1245-1250`).
5. Smoke allowlist filter (`:1325-1326`).
6. Celery `apply_async` (`:1330`).

**Context promotion asymmetries observed (non-blocking, documented):**
- `content_type` was promoted at S1184 PR-D to prevent GPT-5.2 from picking invalid values.
- Media-family tools do NOT have `image_id` or `image_url` in the promote list — media identifiers must be nested under `context` explicitly (documented in `image_editing_agent_validation.md` §3).
- Slice 6+ tools that add new top-level params must be added to `_CONTEXT_PROMOTE_KEYS` OR receive them via `context` nesting.

---

## 6. Known UX gaps + Fold candidates (carried forward from Slice 5 sweep)

Slice 5 batches surfaced these gaps; none reached Fold promotion during the sweep. All are documented in per-tool validation docs + this artifact for continuity into Slice 6+.

- **Sub-agent AgentExecution rows not auto-enumerated in `job_status`** (1st documented instance: S2925 `create_project_from_research`; corroborated across batches 2-3 authoring — WorkflowAgent-family + WorkflowOrchestrationAgent-family both exhibit this). ORM traversal via `parent_execution_id` is required for sub-agent enumeration.
- **Cancel is not recursive across sub-agent tree** (WorkflowAgent-family + WorkflowOrchestrationAgent-family). Parent revoke does NOT cascade; each sub-agent `celery_task_id` requires individual revoke.
- **Secondary domain identifier not surfaced in receipt envelope** — e.g., `content_writer_agent` auto-creates a Deliverable but the Deliverable id is not in AgentResult.data; callers must ORM-query. Media-family tools have Cloudinary URLs only surfaced at completion.
- **Content-shape FAIL** — at 1/2 pre-batch-4; S2928 completion-verifies are 2nd-instance triggers.
- **Multi-tool-single-class asymmetry** — 3 mapping-level instances; Chris's validation-based ladder at 2/3 (pending `security_agent` validation in Slice 6+).
- **Deliverable persistence-vs-AgentResult decoupling** — 1st documented at S2928 (`content_writer_agent`); watch for 2nd in Slice 6+ auto-persisting tools.
- **Media provider egress as distinct §5a downstream axis** — Fold candidate; ImageEditingAgent (S2928) corroborates the shape from create_brand_video (S2926) initially. Watch for 2nd media-family tool in Slice 6+.

---

## 7. Deferred executable invariants (fork A close-shape decision — Chris D-verdict at S2928 T0)

Rigby T0 SIGN Q5(iv) pushback: "The coupling risk isn't 'doc-only' per se — it's **doc-only without executable invariants** (tests/lints) for tool schemas, output envelopes, dispatcher context promotion, mapping consistency."

Chris ratified **fork A (doc-only close)** at S2928 T0 → the following executable invariants are **deferred to a dedicated Slice 5-hardening session before Slice 6 opens:**

1. **Output-envelope assertion test for content agents** — enforce the standardized shape `{ metadata: { content: { full_text, ... }, ... }, deliverable_id? }` at test level.
2. **Schema-required-field regularization lint** — detect drift between `pa_tool_schemas.py` shape and handler expectations (Slice 5 currently uses only `task` as required; any Slice 6+ divergence would benefit from lint).
3. **Envelope-shape assertion** — enforce the 6-key async receipt envelope (`task_id` + `mode='async'` + `agent` + `auto_followup` + `follow_up_will_fire` + `message`) at handler level for all agent-forwarding tools.
4. **Context-promotion consistency check** — assert that any new top-level schema key is either in `_CONTEXT_PROMOTE_KEYS` OR intentionally nested under `context` (with a rationale comment).

**Existing coverage:** `core/tests/test_tool_to_agent_name_mapping.py` (3 tests from S2927 PR #3487) — 1 of the 4 invariants above (mapping consistency) is partially covered.

**Slice 5-hardening session scope (proposed):** ship 3-4 invariants above as a single PR before Slice 6+ opens. Estimated 1 session of focused work. Would close the "doc-only cadence has structural risk" pushback surfaced at S2928 T0 SIGN Q5(iv).

---

## Related

- **Prior Slice CLOSE artifacts:** S2924 Slice 4 CLOSE §5a tier distribution table (in `docs/handoffs/SESSION_2924_SLICE_4_CLOSE_BATCH_7.md:77+`). Slice 5's structural shift to a single shared handler is why this artifact is a standalone doc (larger scope than a table).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1 — §5a 4-tier taxonomy amended S2921; Slice 5 end-to-end classification guidance in-doc post-S2925 + corroborated across S2926/S2927/S2928).
- **Rigby T0 SIGN cycle envelope (S2928):** Q1 composition AGREED; Q2 completion-verify representative = ContentWriterAgent (YES); Q3 template-driven vs LLM-planner distinction AGREED as new evidence class; Q4 recommend Slice 5 CLOSE artifact (this doc); Q5 zoom-out — content-shape FAIL Fold sketch pre-written; multi-tool-single-class corroboration at 3 mapping-level instances (Chris ladder at 2/3, validation-gated); Slice 5-hardening deferred per fork A.
- **Ratifications:** S2925 batch 1 (opened Slice 5) → S2926 batch 2 → S2927 batch 3 → **S2928 batch 4 (CLOSES Slice 5 at 14/14) + this artifact**.
