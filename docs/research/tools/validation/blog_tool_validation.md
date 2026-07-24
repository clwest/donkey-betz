# `blog_tool` — Validation Report (S2936)

**Tool:** `blog_tool`
**Schema:** `core/services/pa_tool_schemas.py:4287` (8-action enum + 8 optional params)
**Handler:** `core/services/td_handlers_content.py:213` (`_handle_blog_direct` — routes to `_handle_content_review` at :286 and `_handle_generate_blog` at :1545; `_handle_content_review` in turn falls back to `_handle_blog_query` at :741 for `content_type='blog'`)
**Register site:** `core/services/tool_dispatcher.py:562`
**Session:** S2936 (Slice 6 batch 2 — closing batch for `td_handlers_content.py`; paired with `feedback_tool`)
**HEAD at validation:** `6540fb156` (2026-07-24)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. **Bifurcated verification scope** (per Rigby S2936 T0 SIGN F-BLOCKING #1): §6 covers 5 read actions LIVE-VERIFIED; §5a covers 3 mutation actions ANALYZED-NOT-EXECUTED with signal-chain evidence. Live mutation verification deferred pending handler-layer `dry_run` affordance (Ledger #38).
**Category upgrade target:** `untested` → `validated_partial` (read actions live-verified; mutation actions analyzed-only)
**Rigby SIGN:** S2936 T0 SIGN AGREE Option C with 2 F-BLOCKINGs — both addressed in-doc (bifurcated labeling + Ledger #36 for Deliverable/SelfBlog approve-path correctness trap). Chris "yes proceed" ratification at T1.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`blog_tool` is the PA-surface entry point for the **blog/content review pipeline** — pipeline stats, ready-for-review browsing, deep detail on a specific blog or deliverable, keyword search across both Deliverable + SelfBlog tables, recent-content snapshots, and mutation actions (approve/reject/generate). Use it when Chris asks "what content is queued for review", "show me the blog pipeline", "search for posts about X", "what's ready to publish", "approve/reject this piece", or "generate a new blog about Y".

Distinct from `deliverable_tool` (broader deliverable CRUD across all `deliverable_type` values — this tool is scoped to content-review workflow); from `newsletter_tool` (downstream publishing to Substack/Beehiiv — this tool operates on pre-publish artifacts); from `content_scoring_service` (rule-based reach/intent/replicability scoring, not surfaced through this tool). This is the tool Rigby reaches for whenever the question is about the content-review-pipeline state or a specific blog decision.

## Covered actions

Enumerating every action in the schema `action` enum. **5 read actions LIVE-VERIFIED at S2936**; **3 mutation actions ANALYZED-NOT-EXECUTED** per Option C batch shape (§5a below).

- `stats` — **in scope this ship — verified live.** Pipeline overview: Deliverable counts (ready/drafts/published) + by_type/by_category + SelfBlog counts (total/published/publish_ready/drafts/by_status). Envelope: `{action, ready_for_review, drafts, published, by_type, by_category, blogs:{total, published, publish_ready, drafts, by_status}, gateway:"blog_tool"}`.
- `list` — **in scope this ship — verified live.** Deliverable list with status filter (default: none — see §5). Envelope: `{action, total, count, items[], applied_filters, status_defaulted, filters_applied, gateway}`.
- `detail` — **in scope this ship — verified live (fallback path).** Full detail by `id`. Queries Deliverable first; on 404, falls back to SelfBlog. Envelope varies by resolved source (`content_kind: 'deliverable'` or `'blog'`); on double-404 returns `{action:"details", error:"Content ... not found in deliverables or blogs — it may have been deleted", status:"gone"}`.
- `search` — **in scope this ship — verified live.** Keyword search across BOTH Deliverable + SelfBlog title (icontains). Envelope: `{action, query, deliverables:{count, items}, blogs:{count, items}, total_found, gateway}`.
- `recent` — **in scope this ship — verified live.** Recently-created Deliverables (default 30 days per schema; handler default 7 via `payload.get('days', 7)` at line 421 — **schema/handler default drift**). Envelope: `{action, count, total, items[], period_days, by_status, filters_applied, gateway}`.
- `approve` — **ANALYZED-NOT-EXECUTED — MUTATION `spreading`** — see §5a. Aliased to `publish` at line 219. Mutates Deliverable.status → 'published'. Fires deliverable_status_signals (writes DeliverableEvent; gated Celery enqueue). Also writes AgentMemory + UserAgentLearning.
- `reject` — **ANALYZED-NOT-EXECUTED — MUTATION `spreading`** — see §5a. Aliased to `archive` at line 219. Mutates Deliverable.status → 'archived' + metadata['archive_reason']=feedback. Same signal fan-out as approve.
- `generate` — **ANALYZED-NOT-EXECUTED — MUTATION `external` / `cascading`** — see §5a. Dispatches Celery `generate_blog_with_topic_task` (if topic given) or `generate_self_blog_deliberation_task` — deliberation pipeline → LLM calls → creates SelfBlog/Deliverable rows downstream.
- **default (no `action` param)** — verified via handler code inspection (`td_handlers_content.py:215`). Defaults to `stats` per `payload.get('action', 'stats')`.
- **invalid action** — verified via handler code inspection. `_handle_blog_direct` passes unknown actions through to `_handle_content_review` which raises `ValueError("Unknown action: <x>. Valid actions: list, stats, details, publish, archive, complete (aliases: approve=publish, reject=archive, mark_complete/done=complete)")` at line 736.

## 3. Schema notes

- **Required:** `action` (enum: `stats` | `list` | `detail` | `search` | `recent` | `approve` | `reject` | `generate`).
- **Optional:** `id` (UUID string, required for `detail` / `approve` / `reject`); `query` (string, required for `search`); `status` (string filter for `list` — schema names it but handler default is empty-string, not `'ready'`; see §5); `topic` (string, `generate` action); `tone` (string, default `'enthusiastic'`, `generate` action); `feedback` (string, optional for `reject`, default `'Archived via PA'`); `days` (int, default 30 per schema BUT handler default is **7** — see §5); `limit` (int, various defaults).
- **Schema/handler default drift on `days`:** schema description says "default 30" (line 4315); handler uses `payload.get('days', 7)` (line 421). GPT-5.2 relies on schema description for calling behavior, so this is asymmetric. Ledger candidate documented in §Related.
- **`content_type='blog'` implicit branch:** if caller passes `type='blog'` (not in this tool's schema — leaks from a shared handler surface), routes through `_handle_blog_query` (line 741) which queries SelfBlog instead of Deliverable. Not a first-class schema surface but reachable via passthrough.
- **`approve`/`reject` aliases (line 311-318):** `_handle_content_review` maps `approve→publish`, `reject→archive`, `get→details`, `mark_complete→complete`, `mark_completed→complete`, `done→complete`. Schema exposes `approve`/`reject` but the underlying handler branches on `publish`/`archive`.
- **`approve` implicit precondition:** requires the target Deliverable to be in `status='ready'` (line 631). Any other status raises `"Deliverable <id> not found or not in ready status"`. Not surfaced in schema description.
- **`generate` is fire-and-forget async:** returns `{action:"generate_blog", mode:"async", task_id, message}` immediately; caller must poll via `task_breakdown_tool` or similar. Blog generation typically 60-300s.
- **PA-exclusion NOT applied:** unlike execution_history_tool, this handler does NOT `.exclude(agent__name='PersonalAssistant')`. Content generated by PA meta-agent operations shows up in stats/list/recent.

## 4. Golden-path examples

**Example 1 — Pipeline overview:**
```json
{"action": "stats"}
```
→ `{"action":"stats", "ready_for_review":206, "drafts":3, "published":0, "by_type":{"analysis":58, "ratification_record":52, "initiative_phase_doc":30, ...}, "by_category":{"governance":62, "Research":17, ...}, "blogs":{"total":37, "published":0, "publish_ready":0, "drafts":32, "by_status":{"archived":4, "draft":32, "pending_review":1}}, "gateway":"blog_tool"}`

**Example 2 — Recent content across 7 days:**
```json
{"action": "recent", "days": 7}
```
→ `{"action":"recent", "count":10, "total":204, "items":[...], "period_days":7, "by_status":{"ready":10}, "filters_applied":{...}, "gateway":"blog_tool"}`

**Example 3 — Search across both Deliverable + SelfBlog:**
```json
{"action": "search", "query": "COO"}
```
→ `{"action":"search", "query":"COO", "deliverables":{"count":3, "items":[...COOAgent analyses]}, "blogs":{"count":0, "items":[]}, "total_found":3, "gateway":"blog_tool"}`

**Example 4 — List with status filter:**
```json
{"action": "list", "status": "draft", "limit": 3}
```
→ `{"action":"list", "total":3, "count":3, "items":[...3 draft documents], "applied_filters":{"status":"draft"}, "status_defaulted":false, "filters_applied":{...}, "gateway":"blog_tool"}`

**Example 5 — Detail lookup (fallback path):**
```json
{"action": "detail", "id": "<uuid>"}
```
→ Deliverable envelope (`content_kind:"deliverable"`) if found in Deliverable table; else SelfBlog envelope (`content_kind:"blog"`) if found in SelfBlog table; else 404 envelope `{"action":"details", "error":"Content <id> not found in deliverables or blogs — it may have been deleted", "status":"gone"}`.

## 5. Failure / empty-state / pagination notes

- **`list` with empty `status` filter (schema-defaulted):** returns `{"total":0, "count":0, "items":[]}` — the handler treats empty-string status as an explicit filter matching zero rows, NOT as "no filter." Callers wanting all-status behavior must pass `status='all'` (line 353 escape hatch). Observed at S2936 §6.2: `blog_tool action=list limit=3` returned 0 items despite 206 ready deliverables in stats.
- **`list` with `status='draft'`:** returns 3 draft rows (verified §6.3). `applied_filters={status:"draft"}` and `status_defaulted:false` confirm the filter fired.
- **`recent` `days` default drift:** schema says default 30; handler defaults to 7 (line 421). Callers who don't pass `days` get a 7-day window despite reading the schema and expecting 30. Ledger candidate.
- **`detail` unknown id:** returns 404 envelope with `status:"gone"` and `error_code:"legacy_error"`. Both Deliverable AND SelfBlog fallback paths execute before the 404 response (verified §6.6 via null-UUID sentinel).
- **`search` no-match:** returns `{"deliverables":{"count":0, "items":[]}, "blogs":{"count":0, "items":[]}, "total_found":0}` — envelope shape stable across match count. Observed §6.4: `query=arbitrage` returned 0 in both tables.
- **`approve` precondition failure:** if target Deliverable exists but has `status ≠ 'ready'`, raises `ValueError("Deliverable <id> not found or not in ready status")`. This is a hard-raise, not an in-envelope error.
- **`approve`/`reject` on SelfBlog UUID:** **KNOWN CORRECTNESS TRAP (Ledger #36).** `detail` action falls back to SelfBlog on 404, so a caller CAN discover a SelfBlog row via `blog_tool action=detail`. But `approve`/`reject` only query `Deliverable` base_qs — passing that SelfBlog UUID to `approve` raises "not found." A caller who followed the natural detail→approve flow gets a UX mismatch. See §Related + Ledger #36 for repro.
- **`generate` async response:** returns immediately with `mode:"async"` + `task_id`. Caller must poll separately. `generate` failures during background processing surface only in Celery event logs, not in the tool response.
- **Invalid action string:** raises `ValueError("Unknown action: <x>. Valid actions: list, stats, details, publish, archive, complete (aliases: approve=publish, reject=archive, mark_complete/done=complete)")` — surfaces `list/stats/details/publish/archive/complete` in the error message, but schema declares `stats/list/detail/search/recent/approve/reject/generate`. Error message drifts from schema — reader who invokes an invalid action gets a confusing action-list. Sub-Ledger drift, not critical.
- **Pagination:** `list` supports `offset` + `limit` (verified handler line 384-386); `recent` uses `limit` only (no offset). `search` uses `limit` per source-table, no cross-source offset.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1; 4-tier blast-radius taxonomy added S2921)

**REQUIRED — 3 mutation actions declared in `## Covered actions` (approve, reject, generate). ANALYZED-NOT-EXECUTED at this ship per Rigby S2936 T0 SIGN F-BLOCKING #1. Live mutation verification deferred pending handler-layer `dry_run` affordance (Ledger #38).**

### Per-action blast-radius classification

| Action | Tier | Handler line | Direct writes | Signal fan-out | External touches |
|---|---|---|---|---|---|
| `approve` | **`spreading`** (or `contained` if `RIGBY_EVENT_INTAKE_ENABLED=False`) | `td_handlers_content.py:626-654` | `Deliverable.save(update_fields=['status', 'updated_at'])` → status='published'. Then `AgentMemory.objects.create(...)` at line 256. Then `UserAgentLearning.objects.get_or_create(...)` + `record_success()` at line 273. | `deliverable_status_signals.py:110,133` — pre+post_save. Writes `DeliverableEvent(event_type='status_transition', metadata={from,to,direction})`. Then `transaction.on_commit → rigby_event_intake.apply_async(dry_run=True)` **only if `settings.RIGBY_EVENT_INTAKE_ENABLED=True`** (default False → gated OFF → contained). `deliverable_mirror_signals.py:33` DOES NOT fire (guards on `created=True` + `deliverable_type='ratification_record'`). SelfBlog signals DO NOT fire (approve mutates Deliverable, not SelfBlog). | Celery `rigby_event_intake.apply_async` only if flag on (currently OFF). Zero LLM. Zero network. |
| `reject` | **`spreading`** (or `contained` if flag off) | `td_handlers_content.py:656-689` | `Deliverable.save(update_fields=['status', 'metadata', 'updated_at'])` → status='archived' + metadata['archive_reason']=feedback. Same AgentMemory + UserAgentLearning writes as approve (with `record_failure()` instead of `record_success()`). | Same as approve — deliverable_status_signals fires (terminal transition: `archived` classified as `terminal`, still writes DeliverableEvent). Mirror signal + SelfBlog signals do NOT fire. | Same as approve (gated Celery on flag). |
| `generate` | **`external` + `cascading`** | `td_handlers_content.py:1545-1586` (dispatches `generate_blog_with_topic_task` or `generate_self_blog_deliberation_task`) | None directly; row-writes happen inside the Celery task chain downstream. | None at handler layer — signal fan-out happens in the fanned-out task (deliberation pipeline creates SelfBlog + potentially Deliverable rows, each firing their own post_save signals). | **YES — Celery apply_async** (`generate_blog_with_topic_task.delay(...)` or `generate_self_blog_deliberation_task.delay(...)`). **YES — LLM invocation** (deliberation pipeline calls OpenAI/Anthropic). Truly external + cascading. |

### Signal-chain grep evidence (per §5a taxonomy requirement)

- **Deliverable post_save receivers** (2 total, both verified via `Grep sender=Deliverable` + file read):
  1. `core/signals/deliverable_status_signals.py:110` (pre_save) + `:133` (post_save) — writes DeliverableEvent + gated `rigby_event_intake` Celery.
  2. `core/signals/deliverable_mirror_signals.py:33` — post_save receiver ONLY fires on `created=True` + `deliverable_type='ratification_record'`. blog_tool.approve/reject mutate existing rows (created=False) → **dormant path**.
- **SelfBlog post_save receivers** (1 total): `core/signals/conceptforge_signals.py:29` — fires on `status='published'` + `quality_score>=0.80` → Celery `run_conceptforge_pipeline`. **BUT blog_tool.approve mutates Deliverable, not SelfBlog** — this signal does NOT fire from blog_tool.approve. It WOULD fire if `generate` produces a high-quality SelfBlog that later gets published via a different path.
- **AgentMemory + UserAgentLearning receivers:** grep returned no matches → INSERT paths are terminal (no fan-out).

### Known correctness trap surfaced during grep (Ledger #36 candidate)

**Setup:** SelfBlog rows are reachable via `blog_tool action=detail` (fallback path at line 596-616). A caller sees a valid `content_kind:"blog"` envelope and reasonably attempts `blog_tool action=approve id=<same UUID>`.

**Trap:** `_handle_content_review` at line 626 (`publish` branch) only queries `base_qs = Deliverable.objects.all()...` — SelfBlog UUIDs miss and raise `"Deliverable <id> not found or not in ready status"`. The caller has no signal that SelfBlog approval requires a different tool path.

**Impact:** UX inconsistency between the discover path (fallback works) and the act path (fallback missing). Not a data-corruption bug, but a legitimate user-facing behavior mismatch.

**Repro (theoretical, not executed):**
1. `blog_tool action=list` (with `type='blog'` or against a SelfBlog-populated environment) → get a SelfBlog UUID.
2. `blog_tool action=detail id=<selfblog_uuid>` → returns `{content_kind:"blog", ...}` envelope. Success.
3. `blog_tool action=approve id=<selfblog_uuid>` → raises `ValueError("Deliverable <selfblog_uuid> not found or not in ready status")`. Failure.

**Fix path (not shipped this batch):** Either (a) extend `_handle_content_review` publish/archive branches to fall back to SelfBlog + apply SelfBlog-appropriate status transitions, or (b) surface a schema-level distinction between deliverable-scoped and blog-scoped approve semantics. Ledger #36 tracks.

### Why mutations were NOT executed live at this ship

Two Rigby-articulated reasons at S2936 T0 SIGN F-BLOCKING analysis:

1. **No handler-layer `dry_run` affordance** — none of the 3 mutation actions declare a `dry_run=True` short-circuit. Adding one is substrate-design work (per S2907 Fold E gated-write-dry_run-only shape), not batch-2-validation-ship work. Ledger #38 tracks.
2. **S2921 process hygiene** — don't mix substrate design ("add `dry_run` params to handlers") with validate-under-substrate ("write validation docs against current handler shape") in one session. Split into design-only + ship-only sessions.

Consequence: this batch ships §5a evidence-based analysis of what mutations WOULD do, not proof that they DO it. Live mutation verification is a follow-up batch after handler-layer `dry_run` is designed.

## 5b. First-hop dependency proof

Recommended per §5b guidance (tool has first-hops that leave the handler in the `generate` branch). Table below covers all 8 actions.

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `Deliverable.objects.all().filter(...)` (5 read actions) | `read` | `td_handlers_content.py:305, 332` | Live |
| `SelfBlog.objects.filter(...)` (detail fallback + search + list `type='blog'` branch) | `read` | `td_handlers_content.py:493, 599, 763` | Live |
| `Deliverable.save(update_fields=[...])` (approve, reject) | `db_write` | `td_handlers_content.py:636, 671` | Analyzed-not-executed |
| `AgentMemory.objects.create(...)` (approve, reject) | `db_write` | `td_handlers_content.py:256` | Analyzed-not-executed |
| `UserAgentLearning.objects.get_or_create(...) + record_success/failure()` (approve, reject) | `db_write` | `td_handlers_content.py:273-281` | Analyzed-not-executed |
| `generate_blog_with_topic_task.delay(topic, tone)` (generate w/ topic) | `dispatch` | `td_handlers_content.py:1563` | Analyzed-not-executed → see Appendix A |
| `generate_self_blog_deliberation_task.delay(tone)` (generate no topic) | `dispatch` | `td_handlers_content.py:1577` | Analyzed-not-executed → see Appendix A |
| Cascaded signal-chain: `deliverable_status_signals.record_status_transition` on Deliverable.save | `db_write` (DeliverableEvent) + gated `dispatch` (rigby_event_intake) | `core/signals/deliverable_status_signals.py:133-232` | Live signal wired (verified `[deliverable_status] signals connected` in startup log); `apply_async` gated OFF by default |

### Appendix A — Async-Fanout (first-hop = Celery `apply_async`)

Filled for `generate` action per S2917 Appendix A discipline.

- **A1. Dispatch target type(s):** `agent_task_wrapper` — both `generate_blog_with_topic_task` and `generate_self_blog_deliberation_task` are Celery tasks in `core/tasks.py`. First-hop opacity: handler sees `{task_id, mode:"async"}`; actual downstream is the deliberation pipeline (contract-driven multi-turn LLM orchestration).
- **A2. Queue name(s) + priority:** dedicated `content` Celery queue per platform architecture (`core/celery.py` routing). Priority not set at dispatch site.
- **A3. Task_id envelope + polling contract:**
  - (a) **Identifiers returned:** `task_id` only (no domain-object id — the SelfBlog/Deliverable rows are created downstream by the task and are not surfaced in the initial dispatch response).
  - (b) **Polling endpoint(s):** `task_breakdown_tool` per the handler's own `message` field ("Use task_breakdown_tool to check progress"). Also `CeleryTaskEvent` row for telemetry.
  - (c) **Idempotency stance:** `none` — repeated calls with the same `topic` create N distinct Celery tasks + N distinct SelfBlog/Deliverable outputs. No dedupe_key.
- **A4. Downstream side-effect boundary:** deliberation pipeline invokes LLM (OpenAI/Anthropic per current provider config) — verified from `core/services/content_deliberation_runner.py`. Creates SelfBlog rows (which may trigger `conceptforge_signals` if quality ≥ 0.80). May create Deliverable rows depending on task variant. Dispatcher re-entry: none observed at first-hop; downstream task does not re-invoke `tool_dispatcher._handle_*`.
- **A5. Observability + cancel semantics + revisit triggers:**
  - (a) **Observability contract:** `CeleryTaskEvent` rows (telemetry table); task result available via `AsyncResult(task_id)`. Domain-object side: check new SelfBlog rows via `blog_tool action=recent` after ~5 min.
  - (b) **Cancel semantics:** no explicit revoke at handler layer. Standard Celery `AsyncResult.revoke(terminate=False)` available but not surfaced.
  - (c) **Revisit triggers:** re-audit Appendix A if (1) new dispatch target added (e.g., a third `generate_*_task` variant), (2) task migrates queues, (3) task_id envelope shape changes, (4) dispatcher re-entry introduced at first-hop.

## 6. Evidence

Live PA-dispatch evidence, S2936 T0 (HEAD `6540fb156`, 2026-07-24 ~11:14 UTC). All exercises via `blog_tool` handler at `td_handlers_content.py:213`. Raw envelopes captured verbatim.

### 6.1 `action=stats`

Returned full pipeline overview: `ready_for_review=206, drafts=3, published=0`. `by_type` has 10 types (top: `analysis:58, ratification_record:52, initiative_phase_doc:30`). `by_category` has 10 categories (top: `governance:62, Research:17, Content Writing:14`). SelfBlog side: `total=37, published=0, publish_ready=0, drafts=32, by_status={archived:4, draft:32, pending_review:1}`. All fields typed correctly. Envelope shape matches spec.

### 6.2 `action=list limit=3` (default status filter empty)

Returned `{total:0, count:0, items:[]}`. **Notable:** despite 206 ready deliverables surfaced in `stats`, `list` with the default empty-string status filter returned zero rows. Handler treats empty-string as an explicit `.filter(status='')` (line 355-356) — not as "no filter." `applied_filters={status:""}` + `status_defaulted:false` confirm the filter fired with a zero-matching value. Documented in §5.

### 6.3 `action=list limit=3 status=draft`

Returned 3 draft documents (`COO Backlog #9`, `COO Backlog #4`, `deliverable_tool tooling improvements`). `applied_filters={status:"draft"}` + `status_defaulted:false` — explicit filter applied. Envelope shape stable.

### 6.4 `action=search query=arbitrage limit=3`

Returned `{deliverables:{count:0, items:[]}, blogs:{count:0, items:[]}, total_found:0}`. Envelope shape stable for zero-match case. No `arbitrage` matches in either table.

### 6.5 `action=search query=COO`

Returned `deliverables.count=3` (COOAgent analyses), `blogs.count=0`, `total_found=3`. Envelope shape stable for partial-match case (only one side has matches).

### 6.6 `action=detail id=00000000-0000-0000-0000-000000000000` (null-UUID sentinel — falls through both fallback paths)

Returned `{action:"details", error:"Content 00000000-0000-0000-0000-000000000000 not found in deliverables or blogs — it may have been deleted", status:"gone", error_code:"legacy_error", gateway:"blog_tool"}`. **This proves both Deliverable AND SelfBlog fallback code paths execute before the 404.** The `error_code:"legacy_error"` is added by the PA wrapper, not the handler.

### 6.7 `action=recent days=7 limit=10`

Returned `{count:10, total:204, items:[...], period_days:7, by_status:{ready:10}}`. Top items: OpportunityScoringAgent (signal_dispatch_v1), TrendAnalysisAgent (2 near-identical outputs — pattern noise). Timestamps confirm 24h-window activity. Envelope shape stable.

### 6.8 Mutation actions (NOT executed — §5a analysis only)

Per Option C batch shape, `approve` / `reject` / `generate` were NOT dispatched live at this ship. §5a table above documents blast radius from signal-chain grep + handler code inspection. Live mutation verification is a follow-up batch pending handler-layer `dry_run` affordance (Ledger #38).

## Related

- **Adjacent tools (same Slice 6 batch 2):** `feedback_tool` (paired — sibling mutation-bearing tool with orthogonal subsystem: UserFeedback vs Deliverable/SelfBlog).
- **Adjacent tools (Slice 6 batch 1 CLOSED):** `execution_history_tool` (agent telemetry — orthogonal), `learning_patterns_tool` (LearningPattern signals — orthogonal), `recent_activity_tool` (multi-subsystem snapshot — orthogonal, may surface blog counts in its `blogs` section), `surgical_moves_status_tool` (deliberation telemetry — orthogonal but note: `generate` action creates deliberation sessions surfaced by that tool).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1); `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 6 = 6 untested at open; 2 untested → 0 after this batch closes → Slice 6 CLOSED).
- **Prior ratifications:** S2892 Path B open (PA tools sweep); S2907 T0 Fold E (three canonical batch shapes: gated-write dry_run-only vs mixed vs uniform pure-read); S2921 §5a 4-tier taxonomy + freeze-template-per-session process hygiene; S2928 Slice 5 CLOSE (14/14); S2935 Slice 6 batch 1 CLOSE (4/6, pure-read quartet).
- **Rigby S2936 T0 SIGN evidence pointers:** AGREE Option C with 2 F-BLOCKINGs — (F1) explicit bifurcated §6 LIVE-VERIFIED vs §5a ANALYZED-NOT-EXECUTED labeling, (F2) log Deliverable/SelfBlog approve-path mismatch as Ledger #36. Both addressed in-doc. Non-blocking: (NB1) `feedback_tool.update` `.save()` discipline drift (Ledger #37 in sibling doc), (NB2) log `no dry_run affordance` as substrate gap (Ledger #38). Rigby Q4 zoom-out surfaced the coupling risk: future readers may misread the slice as "tool verified" while mutations remain unexecuted — mitigated by explicit labeling.
- **Ledger entries opened this ship (3, appended to Rigby Tool Gap Ledger deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`):**
  - **#36** — `blog_tool` Deliverable/SelfBlog approve-path gap: `detail` falls back to SelfBlog but `approve`/`reject` only query Deliverable → UX mismatch on natural detail→approve flow. Correctness bug candidate.
  - **#37** — `feedback_tool.update` uses bare `.save()` vs blog_tool's `update_fields=[...]` discipline. Write-scope drift.
  - **#38** — No handler-layer `dry_run` affordance across the 5 batch-2 mutation actions (`approve`, `reject`, `generate`, `submit`, `update`). Substrate gap gating live mutation verification.
- **Sub-Ledger drift observed but not opened as separate entries this ship (defer to future consolidation):**
  - **Schema/handler `days` default drift** on `recent` action (schema says 30, handler defaults 7). Reader-vs-runtime mismatch.
  - **Invalid-action error message drift** — error message says `list/stats/details/publish/archive/complete` but schema declares `stats/list/detail/search/recent/approve/reject/generate`. Confusing to callers.
- **Post-merge live-dispatch verification (per PLAYBOOK-7.4.4):** exercise `blog_tool action=stats` + `blog_tool action=recent` via Rigby after `make recycle-all` at merge; confirm counts and envelope shape match §6 evidence. Recorded in S2936 handoff.
