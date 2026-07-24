# `content_tool` — Validation Report (S2943)

**Tool:** `content_tool`
**Schema:** `core/services/pa_tool_schemas.py:4117-4217`
**Handler:** `core/services/td_handlers_content.py:4577-4919` (`_handle_content`)
**Register site:** `core/services/tool_dispatcher.py:1122`
**Session:** S2943 (Slice 6 close — td_handlers_content.py sweep, PR-A docs-only)
**HEAD at validation:** `adbae9074` (2026-07-24)
**Ship shape:** Doc-only (S2796 shape). Gateway tool — most action families delegate to sibling tools with dedicated validation docs.
**Category upgrade target:** `validated_partial` → `validated_full`
**Rigby SIGN:** S2943 T1 SIGN AGREE — reconciliation confirmed only 2 tools in Slice 6 need doc work post-S2942; content_tool is one of them (tool_runs: 4 repo_tool searches verified gap-map classifier logic + existing doc surface).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`content_tool` is the **unified content gateway** — a thin dispatcher over `content_review_tool`, `generate_blog_tool`, and `deliverables_tool`. It exists so callers who don't know whether a given piece of content is a blog vs a deliverable can still get pipeline overviews, browse, publish, and archive without switching tools mid-thought.

Rigby's preferred surface: **`blog_tool` for blog operations** and **`deliverable_tool` for deliverable operations**. `content_tool` is the aggregate view. When the caller genuinely wants both (e.g. `content_stats` for pipeline overview across blogs + deliverables, `content_search` across both surfaces), it's the correct pick. When the action is unambiguously blog-only or deliverable-only, prefer the focused tool.

Distinct from adjacent tools:
- **`blog_tool`** — focused blog pipeline (stats/list/detail/search/recent/approve/reject/generate). Covered fully by `blog_tool_validation.md` (S2942 close, `live` + `dry_run_supported`).
- **`deliverable_tool`** — focused deliverables library (16 actions incl. bulk_archive, set_status, normalize, link_initiative). Covered fully by `deliverable_tool_validation.md` (S2728, DEFECT-PATCHED-VERIFIED).
- **`feedback_tool`** — user-feedback ledger (submit/update/list/detail). Covered by `feedback_tool_validation.md` (S2942 close, `live` + `dry_run_supported`).

## Covered actions

content_tool's action enum declares **27 actions across 5 delegation families**
(content_review, generate_blog, native async, deliverables, native reads). The
list below enumerates every action with its delegation target and shape
category. Delegated mutation actions inherit dry_run coverage from the target
tool's own validation doc where marked; family-3 actions have native gates
documented at §5a mutation containment.

- `content_stats` — **read** — pipeline overview (blog + deliverable counts); delegated to `_handle_content_review` → sibling `blog_tool.stats`.
- `content_list` — **read** — list content by status (default `ready`); delegated to `_handle_content_review` → sibling `blog_tool.list`.
- `content_detail` — **read** — full details of a deliverable/blog by id; delegated to `_handle_content_review` → sibling `blog_tool.detail`.
- `content_search` — **read** — title-keyword search; delegated to `_handle_content_review` → sibling `blog_tool.search`.
- `content_recent` — **read** — recently created content (any status); delegated to `_handle_content_review` → sibling `blog_tool.recent`.
- `content_approve` — **mutation (publish)** — delegated to `_handle_content_review`; dry_run-supported at `blog_tool.approve` per S2942 Ledger #38.
- `content_reject` — **mutation (archive w/ feedback)** — delegated to `_handle_content_review`; dry_run-supported at `blog_tool.reject` per S2942 Ledger #38.
- `content_complete` — **mutation** — terminal-state alias (Session 1170); delegated to `_handle_content_review` `complete` branch. Analyzed only.
- `generate_blog` — **mutation (external)** — delegated to `_handle_generate_blog`; dry_run-supported at `blog_tool.generate` per S2942 Ledger #38.
- `generate_newsletter` — **mutation (external)** — Celery `apply_async` to `generate_operator_edge_newsletter`; native `dry_run=true` returns cluster preview without LLM call (td_handlers_content.py:4707-4721).
- `bulk_archive` — **mutation (spreading)** — delegated to `_handle_bulk_archive`; `dry_run=TRUE` default + `confirm` gate (S1228 PR-A).
- `bulk_archive_published` — **mutation (cascading)** — admin-only category-scoped archive; delegated to `_handle_bulk_archive_published`. Requires `categories + created_before + confirm`. **S2943 PR-B candidate for dry_run scoreboard-flip.**
- `run_cleanup` — **mutation (external)** — Celery `apply_async` to `cleanup_stale_content`; no dry_run affordance on the async path.
- `deliverable_list` — **read** — delegated to `_handle_deliverables`; covered by `deliverable_tool.list`.
- `deliverable_detail` — **read** — delegated to `_handle_deliverables`; covered by `deliverable_tool.detail`.
- `deliverable_search` — **read** — delegated to `_handle_deliverables`; covered by `deliverable_tool.search`.
- `deliverable_save` — **mutation (contained, bookmark)** — delegated to `_handle_deliverables`; covered by `deliverable_tool.save`.
- `deliverable_create` — **mutation (contained)** — delegated to `_handle_deliverables`; covered by `deliverable_tool.create`.
- `deliverable_update` — **mutation (contained)** — delegated to `_handle_deliverables`; covered by `deliverable_tool.update`.
- `deliverable_append` — **mutation (contained, append-only)** — delegated to `_handle_deliverables`; covered by `deliverable_tool.append`.
- `deliverable_stats` — **read** — delegated to `_handle_deliverables`; covered by `deliverable_tool.stats`.
- `deliverable_export_pdf` — **mutation (contained, PDF export row)** — delegated to `_handle_deliverables`; covered by `deliverable_tool.export_pdf`.
- `podcasts` — **read** — native ORM read of completed `PodcastCoordinatorAgent` executions from `AgentExecution` table.
- `series` — **read** — native ORM read of `AISeriesWorkflowAgent` executions from `AgentExecution` table.
- `content_studio` — **read** — native ORM aggregation of `AgentExecution` counts for content-studio agents (`AutonomousContentStudioCoordinator`, `TopicMinerAgent`).
- `initiative_doc` — **read** — native lookup by `document_id` / `stage_id` / `initiative` name; reads `SelfBlog` + `InitiativeStage`; surfaces 5000-char content-cap signal via `_doc_content_with_signal` (S2730 F-PS-3 hardening).

## 3. Schema notes

**Required param:** `action` (enum, 27 values).

**Silent action inference (td_handlers_content.py:4614-4631):** If `action` is empty, the handler infers from payload keys:
- `append` or `prepend` present → `deliverable_update`
- `content_offset` or `content_limit` present → `deliverable_detail`
- `full` present → `deliverable_detail`
- `topic` + `tone` present → `generate_blog`
- `id` + `content` + >3 keys → `deliverable_update`
- `id` present without `query`/`type`/`category` → `deliverable_detail`
- fallback → `content_stats`

**Action aliases (td_handlers_content.py:4592-4608):** `recent`/`list`/`search`/`stats`/`detail`(`details`)/`approve`/`reject` all map to their `content_*` variants. `complete`/`mark_complete`/`mark_completed`/`done` all map to `content_complete`.

**Common optional params (schema properties dict, 48 fields total):**
- Filters: `type`, `category`, `agent`, `status`, `statuses`, `title_prefixes`, `agent_names`, `protected_categories`, `categories`, `types`
- Pagination: `limit` (default 10), `offset`, `days` (for `content_recent`, default 30)
- Content limits: `full` (bypass 8K cap), `content_offset`, `content_limit`
- Mutation gates: `dry_run` (DEFAULT `true` for `bulk_archive`), `confirm` (required with `dry_run=false`)
- Cleanup tuning: `cutoff_days` (default 7), `cap` (default 500, max 2000), `protected_types`
- Blog gen: `topic`, `tone` (default `enthusiastic`)
- Deliverable create/update: `id`, `title`, `content`, `workspace_id`, `agent_name`, `data_sensitivity`, `is_pinned`, `prepend`, `append`
- Initiative doc: `document_id`, `stage_id`, `initiative`

**Autofill-hardened flags:** `dry_run`, `confirm` — Python `False` is treated as autofill and gated per Session 1228 PR-A belt-and-suspenders.

## 4. Golden-path examples

### Example 1 — `content_stats` (pipeline overview)

```json
{"action": "content_stats"}
```

Response shape (via `blog_tool.stats` delegation):
```json
{
  "gateway": "content_tool",
  "action": "content_stats",
  "blogs": {"draft": N, "ready": N, "published": N, "archived": N},
  "deliverables": {"draft": N, "ready": N, "completed": N, "archived": N},
  "total": N
}
```

### Example 2 — `initiative_doc` (fetch by initiative name)

```json
{"action": "initiative_doc", "initiative": "Session 2942 Ratification"}
```

Response shape:
```json
{
  "gateway": "content_tool",
  "action": "initiative_doc",
  "initiative": "Session 2942 Ratification",
  "stages": [
    {"stage": "...", "status": "...", "document_id": "...", "document_title": "...", "document_preview": "..."}
  ]
}
```

### Example 3 — `bulk_archive` (dry_run preview, safe default)

```json
{"action": "bulk_archive", "agent_names": ["StockAnalystAgent"], "title_prefixes": ["Stock Analysis:"]}
```

`dry_run` defaults to `true`; preview returns count + sample rows without archiving. To execute: `{"dry_run": false, "confirm": true}` in the same payload.

## 5. Failure / empty-state / pagination notes

- **Unknown action** — returns typed error via `_handler_error(action, 'unknown_action', ...)` with the full valid-action list enumerated.
- **`initiative_doc` with no lookup key** — returns `{"error": "Provide document_id, stage_id, or initiative name"}`.
- **`initiative_doc` with truncated content** — sets `content_truncated=true` + `content_original_length=N` when doc exceeds 5000-char cap (S2730 hardening).
- **Delegated read failures** — surface via the underlying handler's error envelope; `gateway: content_tool` is still appended.
- **`podcasts`/`series`/`content_studio`** — wrapped in try/except; failures return `{"error": str(e)}` with `gateway` + `action` echo.
- **Pagination** — `limit` caps at 30 for `podcasts`/`series`, at 50 for `deliverable_list` (via `_handle_deliverables` hard cap).
- **`bulk_archive` without confirm** — even with `dry_run=false`, if `confirm` is not explicitly `true` the write is refused (Session 1228 PR-A gate).

## 5a. Mutation containment

`content_tool` has **mutation actions across all 5 delegation families**. Blast-radius classification per action:

| Action | Tier | Rationale | Deferred / in-scope |
|---|---|---|---|
| `content_approve` | `cascading` | delegates to blog_tool.approve → status flip on Blog row → `post_save` fires publishing signal chain | dry_run-supported at delegated tool (S2942 Ledger #38) |
| `content_reject` | `cascading` | delegates to blog_tool.reject → status flip + feedback persistence + audit-log signal | dry_run-supported at delegated tool (S2942) |
| `content_complete` | `spreading` | delegates to `_handle_content_review` complete branch → status flip + DeliverableEvent row | not currently dry_run-gated at content_tool surface; delegated coverage TBD |
| `generate_blog` | `external` | delegates to blog_tool.generate → deliberation pipeline (LLM + Celery fan-out) | dry_run-supported at delegated tool (S2942 Ledger #38) |
| `generate_newsletter` | `external` | Celery `apply_async` to `generate_operator_edge_newsletter` → LLM call + evidence gather | native `dry_run=true` returns cluster preview without LLM call (td_handlers_content.py:4707-4721) |
| `bulk_archive` | `spreading` | user-scoped `.update()` over ≤`cap` rows (default 500, max 2000) | dry_run=TRUE default + confirm gate |
| `bulk_archive_published` | `cascading` | admin-only category-scoped `.update()` on published rows | dry_run gate documented in schema but handler behavior needs live-verify at PR-B (S2943 candidate) |
| `run_cleanup` | `external` | Celery `apply_async` to `cleanup_stale_content` | no dry_run affordance on async path; async task itself may have dry_run |
| `deliverable_save`/`create`/`update`/`append`/`export_pdf` | see `deliverable_tool_validation.md` | delegated to deliverables handler | per-action coverage in sibling doc |

**S2943 PR-B candidate:** `bulk_archive_published` is the natural next dry_run-scoreboard target after S2942 (sibling of already-supported `bulk_archive`). See PR-B scope in ratification envelope.

## 5b. First-hop dependency proof

`content_tool` handler is itself a dispatcher — its first hops are almost entirely sibling-handler calls within the same process. Native side effects are limited to Celery dispatch (family 3) and direct ORM reads (family 5).

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `_handle_content_review` | dispatch (in-process) | td_handlers_content.py:4655 | covered by blog_tool sibling |
| `_handle_generate_blog` | dispatch (in-process) | td_handlers_content.py:4694 | covered by blog_tool sibling |
| `_handle_deliverables` | dispatch (in-process) | td_handlers_content.py:4752 | covered by deliverable_tool sibling |
| `_handle_bulk_archive` | dispatch (in-process) | td_handlers_content.py:4663 | covered by deliverable_tool sibling (delegates to _handle_deliverables) |
| `_handle_bulk_archive_published` | dispatch (in-process) | td_handlers_content.py:4667 | native to td_handlers_content.py:5065 |
| `cleanup_stale_content.delay` | dispatch (Celery) | td_handlers_content.py:4676 | see Appendix A |
| `generate_operator_edge_newsletter.apply_async` | dispatch (Celery) | td_handlers_content.py:4723 | see Appendix A |
| `AgentExecution.objects.filter(...)` | read | td_handlers_content.py:4763-4814 | direct ORM |
| `SelfBlog.objects.filter(...)` + `InitiativeStage.objects.select_related(...)` | read | td_handlers_content.py:4851-4884 | direct ORM |

### Appendix A — Async-Fanout (first-hop = Celery `apply_async`)

- **A1. Dispatch target type(s):** `direct_task` — both fan-outs are `@shared_task` functions in `core.tasks` / `core.tasks_content`. `cleanup_stale_content` is a maintenance sweep; `generate_operator_edge_newsletter` is an LLM+deliverable-create workflow.
- **A2. Queue name(s):** `generate_operator_edge_newsletter` → queue `content`. `cleanup_stale_content` → default queue (`.delay()` without explicit `queue=`).
- **A3. Task_id envelope + polling contract:**
  - (a) Identifiers returned: `task_id` (str) only. No domain-object id echoed at dispatch time (deliverable/report row is created inside the task).
  - (b) Polling endpoint: `AsyncResult` via Celery. No dedicated status action on content_tool. Newsletter response text suggests "Check deliverables for the result" — implicit polling via deliverable_tool.list.
  - (c) Idempotency stance: `none` — repeated dispatches will run duplicate work. `bulk_archive` gates prevent duplicate deliverable-archive; newsletter/cleanup do not.
- **A4. Downstream side-effect boundary:**
  - `generate_operator_edge_newsletter` (core/tasks_content.py) — LLM call + Deliverable row create (workspace-scoped) + evidence gathering (spider queries).
  - `cleanup_stale_content` (core/tasks.py) — bulk `.update()` on stale Deliverable/SelfBlog rows.
- **A5. Observability + cancel semantics + revisit triggers:**
  - (a) Observability: task status via `AsyncResult`; deliverable/report row appears in `deliverable_tool.list` on success. Best-effort — no structured completion event.
  - (b) Cancel: no revoke path exposed. Long-running LLM call is not gracefully cancellable.
  - (c) Revisit triggers: any new async action added to content_tool; any change to `generate_operator_edge_newsletter` return contract; any new deliverable-side-effect from `cleanup_stale_content`.

## 5c. Contract ↔ Implementation Consistency

### 5c.1 Handler / module header claims match action reality

**PASS.** Schema `description` correctly names all 5 delegation families; handler `_handle_content` docstring (td_handlers_content.py:4578-4586) correctly identifies the 3 replaced tools (`content_review_tool`, `generate_blog_tool`, `deliverables_tool`) and matches the enum. Native family 5 actions (`podcasts`/`series`/`content_studio`/`initiative_doc`) are documented in the schema description but omitted from the handler docstring — minor drift, not action-count-drift. Recording only.

### 5c.2 Gating truth matches runtime behavior

**PASS — no gate.** content_tool has no Django settings toggle or feature flag. `bulk_archive` and `bulk_archive_published` have `dry_run` + `confirm` payload-level gates (not tool-level).

### 5c.3 Shared handler-file coupling noted

**Shared handler file** — `td_handlers_content.py` also hosts: `_handle_deliverable_direct` (deliverable_tool), `_handle_blog_direct` (blog_tool), `_handle_content_review` (delegated target of content_tool.content_*), `_handle_blog_query`, `_handle_generate_blog`, `_handle_initiative`, `_handle_spider_data`, `_handle_execution_history`, `_handle_learning_patterns`, `_handle_feedback` (feedback_tool), `_handle_recent_activity`, `_handle_surgical_moves_status`, `_handle_stock_intelligence`, `_handle_sports_betting`, `_handle_bulk_archive`, `_handle_bulk_archive_published`. **17 handlers total in this file.** Coupled tools per gap map: `blog_tool` + `deliverable_tool` + `feedback_tool` + `execution_history_tool` + `learning_patterns_tool` + `recent_activity_tool` + `surgical_moves_status_tool`.

Operators editing `_handle_content` should also review sibling handlers for shared imports (`_handler_error`, `AgentExecution`, `SelfBlog`, `InitiativeStage`) and shared action-alias patterns — the same alias-map hardening (Session 1103c) appears in adjacent handlers.

## 6. Evidence

**Ship shape:** doc-only. No live-dispatch exercise this ship. content_tool's mutation surface is covered via sibling-tool live-verify (`blog_tool` + `deliverable_tool` docs already carry S2728 + S2942 live evidence for the delegated code paths). Native-family read actions (`podcasts`/`series`/`content_studio`/`initiative_doc`) are analyzed from code + adjacent existing evidence; live-verify deferred as low-risk (pure ORM reads, no writes).

**Prior evidence pointers:**
- `blog_tool_validation.md` §6 — S2942 live-verify of `blog_tool.approve` + `blog_tool.reject` + `blog_tool.generate` with `dry_run=true`.
- `deliverable_tool_validation.md` §6 (implicit) — S2728 DEFECT-PATCHED-VERIFIED trace covering 16-action deliverable surface.
- `feedback_tool_validation.md` §6 — S2942 live-verify of `feedback_tool.submit` with `dry_run=true`.

## Related

- **Sibling tools with dedicated docs:** `blog_tool_validation.md`, `deliverable_tool_validation.md`, `feedback_tool_validation.md`, `execution_history_tool_validation.md`, `learning_patterns_tool_validation.md`, `recent_activity_tool_validation.md`, `surgical_moves_status_tool_validation.md`.
- **Ledger #38 (dry_run MVP):** `docs/audits/PA_TOOLS_GAP_MAP.md` + S2942 close handoff. Content_tool's mutation actions inherit dry_run coverage from delegated targets where flagged.
- **S2943 PR-B candidate:** `bulk_archive_published` mutation-safety scoreboard flip (sibling of already-supported `bulk_archive`). See S2943 ratification envelope.
- **Substrate docs:** `docs/audits/pa_tools/substrate/T1b_ship_shape_s2904.md` (template ratification); `_TEMPLATE_per_tool_validation.md` v1 template.
- **Prior ratifications:** S2942 close (Ledger #38 + #41), S2728 (deliverable_tool DEFECT-PATCHED-VERIFIED batch).
