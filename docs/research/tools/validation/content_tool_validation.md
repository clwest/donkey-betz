# `content_tool` — Validation Report (S2944)

**Tool:** `content_tool`
**Schema:** `core/services/pa_tool_schemas.py:4117-4217`
**Handler:** `core/services/td_handlers_content.py:4577-4919` (`_handle_content`)
**Register site:** `core/services/tool_dispatcher.py:1122`
**Session:** S2944 (Ledger #38 batch 3 — bundled `generate_newsletter` + `bulk_archive` dry_run alignment). Extends S2943 (Slice 6 close + `bulk_archive_published` alignment) which extended S2796 sweep shape.
**HEAD at validation:** `e0e15561e` (2026-07-24, S2943 close cascade merged) → S2944 PR extends
**Ship shape:** Doc + code + live-verify (S2796 shape extended with S2942-aligned dry_run evidence for two additional mutations). Gateway tool — most action families delegate to sibling tools with dedicated validation docs.
**Category upgrade target:** unchanged (`validated_full` + Metric B `dry_run_supported` already earned at S2943). S2944 adds two additional actions to the per-action dry_run-aligned count (2/3 mutations now pattern-aligned).
**Rigby SIGN:** S2944 T1 SIGN AGREE (Option B bundle) — reconciliation confirmed via 6 `repo_tool` tool_runs; pre-existing schema/handler default-mismatch on generate_newsletter surfaced as record-only. Live-verified via Rigby dispatch (see §6.5).
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** dry_run_supported

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
- `generate_newsletter` — **mutation (external)** — Celery `apply_async` to `generate_operator_edge_newsletter`; native `dry_run=true` returns cluster preview + S2942-aligned `no_writes` / `would_action=dispatch_celery` envelope without LLM call (td_handlers_content.py:4707-4732, S2944 batch 3 alignment).
- `bulk_archive` — **mutation (spreading)** — delegated to `_handle_bulk_archive`; `dry_run=TRUE` default via `require_write_authorization` + S2942-aligned `no_writes` / `would_action=archive` envelope (td_handlers_content.py:5044-5057, S2944 batch 3 alignment).
- `bulk_archive_published` — **mutation (cascading)** — admin-only category-scoped archive; delegated to `_handle_bulk_archive_published`. Requires `categories + created_before + confirm`; S2942-aligned dry_run envelope shipped S2943.
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
| `generate_newsletter` | `external` | Celery `apply_async` to `generate_operator_edge_newsletter` → LLM call + evidence gather | S2944 batch 3: `dry_run=true` returns cluster preview + S2942 envelope (`would_action=dispatch_celery`, `would_task=generate_operator_edge_newsletter`, `no_writes=true`) without LLM call |
| `bulk_archive` | `spreading` | user-scoped `.update()` over ≤`cap` rows (default 500, max 2000) | S2944 batch 3: `dry_run=TRUE` default via `require_write_authorization` + S2942 envelope (`would_action=archive`, `would_change_to=archived`, `would_archive_count=N`, `no_writes=true`) |
| `bulk_archive_published` | `cascading` | admin-only category-scoped `.update()` on published rows | S2943 batch 2: `dry_run` gate + S2942 envelope (`would_action=archive_published`, `would_change_to=archived`, `would_archive_count=N`, `no_writes=true`) |
| `run_cleanup` | `external` | Celery `apply_async` to `cleanup_stale_content` | no dry_run affordance on async path; async task itself may have dry_run |
| `deliverable_save`/`create`/`update`/`append`/`export_pdf` | see `deliverable_tool_validation.md` | delegated to deliverables handler | per-action coverage in sibling doc |

**S2944 batch 3:** `bulk_archive` + `generate_newsletter` alignment closes the last two content_tool mutations that predated the S2942 envelope contract. `run_cleanup` remains the only mutation without a dry_run affordance (async-only Celery dispatch; would require a new dry_run branch, deferred as separate ledger candidate).

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

### 6.1 PR-B live-verify — `bulk_archive_published` with `dry_run=true` (S2943)

**Dispatch context:** Rigby PA route via `tools/pa_local.sh` (pin `pa-5e0a153475dd44f7`), post `make celery-recycle`, HEAD at `11745a9bd` + this PR's handler changes loaded in worker.

**Payload:**
```json
{
  "action": "bulk_archive_published",
  "categories": ["s2943_live_verify_nonexistent"],
  "created_before": "2026-07-24T00:00:00Z",
  "dry_run": true
}
```

**Response (raw from `content_tool` handler, 21ms):**
```json
{
  "action": "bulk_archive_published",
  "dry_run": true,
  "total_matching": 0,
  "cap": 500,
  "will_archive": 0,
  "filters": {
    "status": "published",
    "categories": ["s2943_live_verify_nonexistent"],
    "created_before": "2026-07-24T00:00:00Z",
    "agent": ""
  },
  "breakdown": {"by_type": [], "by_category": [], "by_agent": []},
  "sample_items": [],
  "would_action": "archive_published",
  "would_change_to": "archived",
  "would_archive_count": 0,
  "no_writes": true,
  "message": "dry_run=true: 0 published items would be archived. No writes performed. Set dry_run=false and confirm=true to execute."
}
```

**S2942-alignment check (5/5 fields present):**
- `dry_run: true` ✓
- `would_action: "archive_published"` ✓
- `would_change_to: "archived"` ✓
- `would_archive_count: 0` ✓
- `no_writes: true` ✓

**No-writes guarantee:** confirmed at handler level (short-circuits before the `Deliverable.objects.filter(...).update(...)` call at td_handlers_content.py:5199). Corroborated by regression tests in `core/tests/test_s2943_bulk_archive_published_dry_run.py` (6/6 pass, 0.150s).

### 6.2 Regression coverage (S2943)

`core/tests/test_s2943_bulk_archive_published_dry_run.py` (6 tests):
- `test_dry_run_true_default_returns_would_envelope` — dry_run defaults TRUE; all 5 S2942 fields; 0 rows archived
- `test_dry_run_true_explicit_returns_would_envelope` — same when `dry_run=True` explicit
- `test_dry_run_false_without_confirm_refuses` — belt-and-suspenders (S1228 PR-A) still fires
- `test_dry_run_false_with_confirm_actually_archives` — real archive lands (regression sanity)
- `test_non_admin_denied` — permission gate holds
- `test_blog_type_blocked` — `types=['blog']` refused

**Combined S2942 + S2943 suite:** 27 tests, 0.364s, all pass. Gap-map `--check` exits 0.

### 6.3 Prior evidence pointers (sibling tools)

- `blog_tool_validation.md` §6 — S2942 live-verify of `blog_tool.approve` + `blog_tool.reject` + `blog_tool.generate` with `dry_run=true`.
- `deliverable_tool_validation.md` §6 (implicit) — S2728 DEFECT-PATCHED-VERIFIED trace covering 16-action deliverable surface.
- `feedback_tool_validation.md` §6 — S2942 live-verify of `feedback_tool.submit` with `dry_run=true`.

### 6.4 Analyzed-only actions (not exercised live this ship)

Native-family read actions (`podcasts`/`series`/`content_studio`/`initiative_doc`) are analyzed from code + adjacent existing evidence; live-verify deferred as low-risk (pure ORM reads, no writes). `run_cleanup` async dispatch (Celery `apply_async` to `cleanup_stale_content`) has no dry_run affordance; adding one is deferred as a separate ledger candidate.

### 6.5 S2944 Ledger #38 batch 3 — `generate_newsletter` + `bulk_archive` alignment

**Dispatch context:** Rigby PA route via `tools/pa_local.sh` (S2944 wrapper pin `pa-ea0a625600184be2`), post `make celery-recycle`, HEAD at `e0e15561e` + this PR's handler changes loaded in worker.

#### 6.5.a `generate_newsletter` with `dry_run=true`

**Payload:** `{"action":"generate_newsletter","dry_run":true,"hours":72,"cluster_limit":3}`

**Response (raw from `content_tool` handler, 4164ms — evidence-gather runs real DB queries over signal clusters):**
```json
{
  "gateway": "content_tool",
  "action": "generate_newsletter",
  "dry_run": true,
  "mode": "dry_run",
  "would_action": "dispatch_celery",
  "would_task": "generate_operator_edge_newsletter",
  "no_writes": true,
  "clusters_found": 5,
  "top_clusters": ["Iran, Trump emerging trend", "Anthropic, Opus opportunity window", "Openai, Face opportunity window"],
  "evidence_preview": "### Cluster: Iran, Trump emerging trend (type: trend_emergence, confidence: 100%, signals: 15)\n...",
  "message": "dry_run=true: found 5 clusters. No Celery task enqueued and no writes performed. Run with dry_run=false to generate the newsletter."
}
```

**S2942-alignment check (4/4 sentinel fields present):**
- `dry_run: true` ✓
- `would_action: "dispatch_celery"` ✓
- `would_task: "generate_operator_edge_newsletter"` ✓
- `no_writes: true` ✓

**Pre-existing preview data preserved:** `clusters_found: 5`, `top_clusters` (3 non-empty entries), `evidence_preview` (non-empty markdown block).

**No-dispatch guarantee:** confirmed at handler level (short-circuits before the `generate_operator_edge_newsletter.apply_async(...)` call at td_handlers_content.py:4733). Corroborated by regression test `test_dry_run_true_returns_s2942_envelope` in `core/tests/test_s2944_dry_run_batch_3.py` (mocks `apply_async` and asserts `not_called`).

#### 6.5.b `bulk_archive` with `dry_run=true`

**Payload:** `{"action":"bulk_archive","category":"s2944_live_verify_nonexistent","statuses":["draft"]}`

**Response (raw from `content_tool` handler, 33ms):**
```json
{
  "action": "bulk_archive",
  "dry_run": true,
  "total_matching": 0,
  "cap": 500,
  "will_archive": 0,
  "filters": {"statuses": ["draft"], "type": "", "category": "s2944_live_verify_nonexistent", "agent": "", "created_before": "", "created_after": ""},
  "breakdown": {"by_type": [], "by_category": [], "by_agent": [], "by_status": []},
  "sample_items": [],
  "would_action": "archive",
  "would_change_to": "archived",
  "would_archive_count": 0,
  "no_writes": true,
  "message": "dry_run=true: 0 items would be archived. No writes performed. Set dry_run=false AND confirm=true to execute."
}
```

**S2942-alignment check (5/5 sentinel fields present):**
- `dry_run: true` ✓
- `would_action: "archive"` ✓
- `would_change_to: "archived"` ✓
- `would_archive_count: 0` ✓
- `no_writes: true` ✓

**No-writes guarantee:** confirmed at handler level (short-circuits before the `Deliverable.objects.filter(id__in=...).update(status='archived', ...)` call at td_handlers_content.py:5062). Corroborated by regression test `test_dry_run_true_default_returns_would_envelope` in `core/tests/test_s2944_dry_run_batch_3.py`.

**Autofill observation (record-only, S2944 zoom-out surface):** first Rigby dispatch WITHOUT explicit `statuses` triggered `invalid_params` — GPT-5.2 autofilled `statuses: []` (empty list) instead of omitting the key, so `payload.get('statuses', ['ready','draft','completed'])` returned `[]` rather than the default. Handler robustness candidate: coerce empty list back to default before the `safe_statuses` gate. Deferred as separate ledger candidate.

#### 6.5.c Regression coverage (S2944)

`core/tests/test_s2944_dry_run_batch_3.py` (7 tests, all pass):

- **generate_newsletter (3 tests):**
  - `test_dry_run_true_returns_s2942_envelope` — all 4 sentinel fields + `apply_async` not called
  - `test_dry_run_true_preserves_evidence_preview` — existing `clusters_found` / `top_clusters` / `evidence_preview` still present
  - `test_dry_run_false_dispatches_celery` — regression sanity that non-dry-run still enqueues
- **bulk_archive (4 tests):**
  - `test_dry_run_true_default_returns_would_envelope` — envelope shape + no writes
  - `test_dry_run_true_explicit_returns_would_envelope` — same when `dry_run=True` explicit
  - `test_dry_run_false_without_confirm_stays_safe` — belt-and-suspenders (`require_write_authorization`) coerces back to dry_run
  - `test_dry_run_false_with_confirm_actually_archives` — real archive lands (regression sanity)

**Combined S2942 + S2943 + S2944 suite:** 24 tests, 1.081s, all pass. Gap-map `--check` exits 0.

#### 6.5.d Pre-existing record-only observation

Rigby T1 SIGN surfaced a pre-existing schema/handler default mismatch: the shared `dry_run` schema description says "DEFAULT: true" for `generate_newsletter` (pa_tool_schemas.py:4190), but the handler treats missing as `False` (td_handlers_content.py:4705). S2944 preserves the pre-existing behavior — flipping the default is a separate ledger candidate that would need per-caller regression review.

## Related

- **Sibling tools with dedicated docs:** `blog_tool_validation.md`, `deliverable_tool_validation.md`, `feedback_tool_validation.md`, `execution_history_tool_validation.md`, `learning_patterns_tool_validation.md`, `recent_activity_tool_validation.md`, `surgical_moves_status_tool_validation.md`.
- **Ledger #38 (dry_run alignment arc):** `docs/audits/PA_TOOLS_GAP_MAP.md` + S2942 close handoff. Content_tool's mutation actions have native alignment (S2943 bulk_archive_published, S2944 bulk_archive + generate_newsletter) or inherit dry_run coverage from delegated targets where flagged (blog_tool, feedback_tool, deliverable_tool).
- **Substrate docs:** `docs/audits/pa_tools/substrate/T1b_ship_shape_s2904.md` (template ratification); `_TEMPLATE_per_tool_validation.md` v1 template.
- **Prior ratifications:** S2944 (Ledger #38 batch 3), S2943 (Slice 6 close + Ledger #38 batch 2), S2942 close (Ledger #38 + #41), S2728 (deliverable_tool DEFECT-PATCHED-VERIFIED batch).
