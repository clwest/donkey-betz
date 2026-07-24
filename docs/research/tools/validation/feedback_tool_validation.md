# `feedback_tool` — Validation Report (S2936)

**Tool:** `feedback_tool`
**Schema:** `core/services/pa_tool_schemas.py:618` (4-action enum + 7 optional params)
**Handler:** `core/services/td_handlers_content.py:3587` (`_handle_feedback`)
**Register site:** `core/services/tool_dispatcher.py:470`
**Session:** S2936 (Slice 6 batch 2 — closing batch for `td_handlers_content.py`; paired with `blog_tool`)
**HEAD at validation:** `6540fb156` (2026-07-24)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4. **Bifurcated verification scope** (per Rigby S2936 T0 SIGN F-BLOCKING #1): §6 covers 2 read actions LIVE-VERIFIED; §5a covers 2 mutation actions ANALYZED-NOT-EXECUTED with signal-chain evidence. Live mutation verification deferred pending handler-layer `dry_run` affordance (Ledger #38). **S2942 update — Ledger #38 dry_run shipped:** mutation actions are now live-verifiable under `dry_run=true`. See §6.4 Rigby live-verify evidence.
**Category upgrade target:** `untested` → `validated_full` (as of S2942 — all 4 actions live-verified: 2 read + 2 mutation-under-dry_run).
**Rigby SIGN:** S2936 T0 SIGN AGREE Option C — same batch shape as blog_tool sibling. Chris "yes proceed" ratification at T1. S2942 T0 SIGN AGREE Option A on plan reconciliation (Ledger #33/#34 already-closed) + Chris "Yes" ratify on revised scope + acceptance-gate live-verify SATISFIED.
**Template variant:** sweep
**Template version:** v1
**Execution mode:** live
**Mutation safety:** dry_run_supported

---

## 1. Purpose / when-to-use

`feedback_tool` is the PA-surface entry point for **user feedback capture + triage** — submitting feedback on agent outputs / content quality / platform features, browsing open feedback, aggregating stats by type/status, and updating feedback status through the resolution workflow. Use it when Chris says "log this as feedback", "submit a bug report", "show me open feedback", "what feedback have we gotten", "mark feedback X as addressed", or when any agent output warrants explicit human rating.

Distinct from `human_decisions_tool` (governance decisions on strategic questions — not user-experience feedback); from `AgentMemory feedback` (auto-generated agent-side feedback loops from content review — different subsystem); from `content_scoring_service` (automated quality signals — no human input). This is the tool for capturing explicit human-authored feedback that flows into the UserFeedback triage queue.

## Covered actions

Enumerating every action in the schema `action` enum. **2 read actions LIVE-VERIFIED at S2936**; **2 mutation actions ANALYZED-NOT-EXECUTED** per Option C batch shape (§5a below).

- `list` — **in scope this ship — verified live.** Recent UserFeedback rows. Default status filter: `'open'`. Envelope: `{action, status_filter, count, items[{id, feedback_type, message, status, created_at, trace_id}]}`.
- `stats` — **in scope this ship — verified live.** Feedback summary counts. Envelope: `{action, total_open, by_type, by_status}`.
- `submit` — **ANALYZED-NOT-EXECUTED — MUTATION `contained`** — see §5a. Creates a UserFeedback row with `feedback_type=<target_type>` (enum-restricted to `ui_ux_issue`/`bug`/`feature_request`/`feedback`; anything else silently coerced to `'feedback'`), `message=<comment>`, `status='open'`, `trace_id` propagated.
- `update` — **ANALYZED-NOT-EXECUTED — MUTATION `contained`** — see §5a. UPDATE UserFeedback.status + optional resolution_notes. **Uses bare `.save()` (not update_fields=[...])** — write-scope drift vs blog_tool discipline. Ledger #37.
- **default (no `action` param)** — verified via handler code inspection (`td_handlers_content.py:3606`). Defaults to `list` per `payload.get('action', 'list')`.
- **invalid action** — verified via handler code inspection (`td_handlers_content.py:3700-3703`). Raises `ValueError("Unknown action: <x>. Valid actions: list, stats, submit, update")`.

## 3. Schema notes

- **Required:** `action` (enum: `submit` | `list` | `stats` | `update`).
- **Optional:** `target_type` (string, `submit` action — coerced to `'feedback'` if not in `{ui_ux_issue, bug, feature_request, feedback}`); `target_id` (UUID string, `submit` action — declared in schema but NOT read by handler at line 3649-3667 → **schema-declared-but-handler-unused param drift**); `rating` (int 1-5, `submit` action — declared in schema but NOT read by handler → same drift class); `comment` (string, required for `submit`); `id` (UUID string, `update` action — required); `new_status` (string enum documented in schema description as `open|acknowledged|in_progress|addressed|wont_fix` — NOT enforced by handler); `limit` (int, default 20 per handler line 3608; schema description says default 10 — **schema/handler default drift**).
- **`feedback_type` silent coercion (line 3661-3663):** if `target_type` is not in the whitelist, handler silently stores `'feedback'` instead. No error surfaced to caller.
- **`trace_id` heuristic (line 3666):** stores caller-provided `trace_id` UNLESS it starts with `'pa-'` (which indicates the PA conversation pin, not a real trace). PA-originated feedback gets `trace_id=''`. Not surfaced in schema.
- **`update` new_status NOT validated:** handler blindly writes whatever string is passed. Schema description enumerates 5 valid values but handler will accept any string. Downstream `UserFeedback.get_feedback_summary()` in `stats` action groups by `status` — arbitrary strings will show up as their own group.
- **User FK fallback (line 3655-3657):** if `user_id` doesn't resolve, handler falls back to `User.objects.first()` — first-user-created-wins. Feedback attribution may be incorrect if user resolution fails.

## 4. Golden-path examples

**Example 1 — View open feedback:**
```json
{"action": "list", "limit": 5}
```
→ `{"action":"list", "status_filter":"open", "count":<N>, "items":[{"id":"<uuid>", "feedback_type":"...", "message":"...", "status":"open", "created_at":"...", "trace_id":"..."}, ...]}` — or `{"count":0, "items":[]}` when empty.

**Example 2 — Feedback overview:**
```json
{"action": "stats"}
```
→ `{"action":"stats", "total_open":<N>, "by_type":{"feedback":1, ...}, "by_status":{"addressed":1, "open":<N>, ...}}`

**Example 3 — Submit new feedback (ANALYZED-NOT-EXECUTED):**
```json
{"action": "submit", "target_type": "bug", "comment": "Trend analysis returned duplicate rows"}
```
→ Would return `{"action":"submit", "id":"<new_uuid>", "success":true, "message":"Feedback submitted successfully"}`. Handler inserts UserFeedback row per §5a.

**Example 4 — Update feedback status (ANALYZED-NOT-EXECUTED):**
```json
{"action": "update", "id": "<uuid>", "new_status": "addressed", "notes": "Fixed in PR #3506"}
```
→ Would return `{"action":"update", "id":"<uuid>", "new_status":"addressed", "success":true}`. Handler updates UserFeedback row via bare `.save()` per §5a.

## 5. Failure / empty-state / pagination notes

- **Empty state (`list`):** returns `{"action":"list", "status_filter":"open", "count":0, "items":[]}` — envelope shape stable. Observed §6.1: 0 items with default `status='open'` filter.
- **`stats` with only closed items:** returns `total_open=0` + `by_type` + `by_status` maps that reflect ALL rows regardless of status. Observed §6.2: `total_open=0` but `by_type={feedback:1}` + `by_status={addressed:1}` — one closed row in the DB.
- **`submit` missing `comment`:** returns `{"action":"submit", "error":{...}, "error_code":"invalid_params"}` via `_handler_error` (line 3653). NOT a raise — in-envelope error.
- **`submit` invalid `target_type`:** silently coerces to `'feedback'` (line 3661-3663). No warning surfaced. Caller may be surprised.
- **`submit` unresolved user:** falls back to `User.objects.first()`. In production this may attribute feedback to Chris regardless of who submitted — not a data-integrity bug in single-user pre-prod (per `project_single_user_pre_prod_operating_context`), but a multi-tenant hazard.
- **`update` missing `id` OR `new_status`:** raises `ValueError("Update requires 'id' and 'new_status'")`.
- **`update` unknown `id`:** raises `ValueError("Feedback item <id> not found")` (line 3697-3698, catches `UserFeedback.DoesNotExist`).
- **`update` invalid `new_status`:** silently accepted — no whitelist validation. Downstream `stats` will show the arbitrary string as its own status group.
- **`schema/handler default drift on `limit`:** schema description says `default 10`; handler defaults to 20 (line 3608). Callers who don't pass `limit` get 20-row pages despite schema. Sub-Ledger drift.
- **Schema-declared `target_id` + `rating` unused:** handler at line 3649-3667 reads only `comment` + `target_type` for the submit branch. Callers can pass `target_id` or `rating` per schema; the values are silently dropped. Sub-Ledger drift (candidate for consolidation with blog_tool's default-drift observations).
- **Pagination:** none. `limit` bounds the query; no offset/cursor.
- **Invalid action string:** raises `ValueError("Unknown action: <x>. Valid actions: list, stats, submit, update")` — clean 4-action list.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1; 4-tier blast-radius taxonomy added S2921)

**REQUIRED — 2 mutation actions declared in `## Covered actions` (submit, update). ANALYZED-NOT-EXECUTED at this ship per Rigby S2936 T0 SIGN F-BLOCKING #1. Live mutation verification deferred pending handler-layer `dry_run` affordance (Ledger #38).**

### Per-action blast-radius classification

| Action | Tier | Handler line | Direct writes | Signal fan-out | External touches |
|---|---|---|---|---|---|
| `submit` | **`contained`** | `td_handlers_content.py:3659-3667` | `UserFeedback.objects.create(user, feedback_type, message, status='open', trace_id)`. Single-row INSERT into `core_userfeedback` table. | None. Grep `sender=UserFeedback` and `receiver.*UserFeedback` returned **zero matches**. No `post_save` receivers wired. No FK cascade fan-out (UserFeedback has FK to User but no reverse-observers registered). | None. No Celery, no LLM, no network. |
| `update` | **`contained`** | `td_handlers_content.py:3684-3689` | UPDATE UserFeedback row: `feedback.status = new_status`, optionally `feedback.resolution_notes = notes`, then bare `feedback.save()` (NOT `update_fields=[...]`). **All columns re-written** — write-scope drift vs blog_tool's targeted saves (Ledger #37). | None. Same signal-grep results as submit. | None. |

### Signal-chain grep evidence (per §5a taxonomy requirement)

- **UserFeedback post_save receivers:** grep patterns `sender=UserFeedback`, `sender="UserFeedback"`, `receiver.*UserFeedback`, `UserFeedback.*post_save` all returned **zero matches** across `*.py`. UserFeedback INSERT/UPDATE fires NO downstream signal chain.
- **FK cascade check:** UserFeedback has a FK to `auth.User`; no reverse-observer registrations found. `UserFeedback` is a terminal telemetry-shape row in this handler's blast radius.
- **Implicit `feedback_processing` signals:** `models_feedback_processing.py` connects "Feedback processing signals" per startup logs, but grep confirmed this module observes `AgentFeedback`-family rows (not `UserFeedback` from this handler). Different subsystem — namespace collision but no fan-out into `UserFeedback`.
- **Conclusion:** both submit + update are truly `contained` — no reason to reclassify up.

### Write-scope discipline drift (Ledger #37 candidate)

**Observation:** `feedback.save()` at line 3689 (`update` branch) is called WITHOUT `update_fields=[...]`. Django ORM's default `.save()` writes all columns.

**Comparison with sibling discipline:**
- `blog_tool.approve` (line 636): `deliverable.save(update_fields=['status', 'updated_at'])` — 2 fields.
- `blog_tool.reject` (line 671): `deliverable.save(update_fields=['status', 'metadata', 'updated_at'])` — 3 fields.
- `feedback_tool.update` (line 3689): `feedback.save()` — all columns (10+ fields).

**Impact:**
- Broader write than semantically necessary. If a concurrent process updated `resolution_notes` between our read and save, this handler would overwrite it.
- Larger row-lock footprint (Postgres row-level, not table-level, so impact is modest for single-user pre-prod).
- Not a bug in current single-user state, but a discipline drift that scales into a hazard in multi-tenant future.

**Fix path (not shipped this batch):** replace bare `.save()` with `.save(update_fields=['status', 'resolution_notes', 'updated_at'])` (adding `updated_at` if the model has that field). ~1-line change. Ledger #37 tracks.

### Why mutations were NOT executed live at this ship

Same reasoning as blog_tool sibling — see `blog_tool_validation.md` §5a "Why mutations were NOT executed live at this ship":

1. **No handler-layer `dry_run` affordance** (Ledger #38).
2. **S2921 process hygiene** — don't mix substrate design with validate-under-substrate in one session.

Consequence: this batch ships §5a evidence-based analysis of what submit + update WOULD do (both `contained`, no signal fan-out, terminal telemetry writes), not proof that they DO it. Live mutation verification is a follow-up batch after handler-layer `dry_run` is designed.

## 5b. First-hop dependency proof

Optional per §5b guidance (this tool has no first-hop that leaves the process — pure ORM). Included anyway for parity with blog_tool sibling.

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `UserFeedback.objects.all().filter(status=...)` (list) | `read` | `td_handlers_content.py:3611-3617` | Live |
| `UserFeedback.get_feedback_summary()` (stats classmethod) | `read` | `td_handlers_content.py:3637` | Live |
| `UserFeedback.objects.create(...)` (submit) | `db_write` | `td_handlers_content.py:3659` | Analyzed-not-executed |
| `UserFeedback.objects.get(id=...)` + `feedback.save()` (update) | `db_write` | `td_handlers_content.py:3685-3689` | Analyzed-not-executed |
| `User.objects.filter(id=user_id).first()` + `User.objects.first()` fallback (submit) | `read` | `td_handlers_content.py:3655-3657` | Live (during any dispatch) |

Appendix N/A not applicable — no network or Celery first-hop.

## 6. Evidence

Live PA-dispatch evidence, S2936 T0 (HEAD `6540fb156`, 2026-07-24 ~11:14 UTC). All exercises via `feedback_tool` handler at `td_handlers_content.py:3587`. Raw envelopes captured verbatim.

### 6.1 `action=list limit=5`

Returned `{"action":"list", "status_filter":"open", "count":0, "items":[]}`. Empty state — no `status='open'` rows in current DB. Envelope shape stable. Confirms default `status_filter='open'` applied per handler line 3616.

### 6.2 `action=stats`

Returned `{"action":"stats", "total_open":0, "by_type":{"feedback":1}, "by_status":{"addressed":1}}`. Notable: `total_open=0` (confirms §6.1 empty state) but `by_type` + `by_status` maps show 1 total row in DB with `status='addressed'` + `feedback_type='feedback'` — meaning some prior feedback exists but has been triaged closed. Envelope shape matches spec. `get_feedback_summary()` classmethod on the model provides the aggregation (not open-coded in handler).

### 6.3 Mutation actions (NOT executed — §5a analysis only)

Per Option C batch shape, `submit` + `update` were NOT dispatched live at this ship. §5a table above documents blast radius (both `contained`) from signal-chain grep + handler code inspection. Live mutation verification is a follow-up batch pending handler-layer `dry_run` affordance (Ledger #38).

### 6.4 S2942 — Ledger #38 dry_run live verification (acceptance-gate proof)

Shipped 2026-07-24 via S2942 handler edits at `td_handlers_content.py:3600-3729` (submit + update branches) plus schema opt-in at `pa_tool_schemas.py:645-655`. Live-verified via Rigby PA dispatch (conversation `pa-07d6a1d43f6a4b42`) with tool_runs captured verbatim:

**Pre-call baseline** — `orm_inspect_tool.count_by model=UserFeedback field=status`:
```json
{"ok":true,"total_matching":1,"groups":[{"value":"addressed","count":1}]}
```

**Dry-run submit** — `feedback_tool action=submit comment="S2942 acceptance gate #1..." target_type=bug dry_run=true`:
```json
{"action":"submit","dry_run":true,"would_action":"create",
 "would_write":{"model":"UserFeedback","feedback_type":"bug",
   "message":"S2942 acceptance gate #1 — live-verify dry_run",
   "status":"open","user_id":"e0c9d44b-...","trace_id":"tool-2-7ba01d55"},
 "no_writes":true,
 "message":"dry_run=true: no UserFeedback row created."}
```

**Post-call verify** — `orm_inspect_tool.count_by model=UserFeedback field=status`:
```json
{"ok":true,"total_matching":1,"groups":[{"value":"addressed","count":1}]}
```

**Result:** `total_matching` unchanged at 1 → **NO UserFeedback row created under dry_run=true**. Acceptance gate satisfied for `feedback_tool.submit`.

**Baseline mutation** — `dry_run=false` still lands: subsequent `feedback_tool action=submit dry_run=false` returned `id=c3faf830-bf8c-4fc7-a2a7-fe3611a7e663` + verified via `orm_inspect_tool.filter` presence check. Real writes preserved.

**Envelope shape confirmed:** `dry_run: true`, `would_action: 'create'`, `would_write.{model,feedback_type,message,status,user_id,trace_id}`, `no_writes: true`, plain-English `message`. Update branch mirrors this shape with `current_status` + `would_change_to` + `notes_would_be` keys.

**Rigby zoom-out fold (PLAYBOOK-6.10.7, record-only):** future envelope enhancement candidates — add `verify_hint` block (model + id + field expectations) and `would_write_count` for multi-row actions. Not shipped this session; logged for a next-instance corroboration trigger.

**Allowlist expansion co-shipped:** `UserFeedback` added to `orm_inspect_tool` allowlist at `td_handlers_agents.py:759-763` (mirrors S2931 pattern for AgentExecution). Enables self-service verification loop.

## Related

- **Adjacent tools (same Slice 6 batch 2):** `blog_tool` (paired — sibling mutation-bearing tool with more mutation surface area and higher blast-radius classification: `spreading`/`external` vs feedback_tool's `contained`).
- **Adjacent tools (Slice 6 batch 1 CLOSED):** `execution_history_tool` (agent telemetry — orthogonal), `learning_patterns_tool` (LearningPattern signals — orthogonal), `recent_activity_tool` (multi-subsystem snapshot — orthogonal), `surgical_moves_status_tool` (deliberation telemetry — orthogonal).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1); `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 6 = 6 untested at open; 0 untested → Slice 6 CLOSED after this batch).
- **Prior ratifications:** same set as blog_tool — S2892 Path B open; S2907 T0 Fold E; S2921 §5a taxonomy; S2928 Slice 5 CLOSE; S2935 Slice 6 batch 1 CLOSE.
- **Rigby S2936 T0 SIGN evidence pointers:** AGREE Option C with 2 F-BLOCKINGs — both addressed in-doc via bifurcated §6 LIVE-VERIFIED vs §5a ANALYZED-NOT-EXECUTED labeling + Ledger #37 for `.save()` discipline drift + Ledger #38 for missing `dry_run`. Non-blocking observations (schema/handler defaults on `limit`, unused `target_id`+`rating` params, silent `feedback_type` coercion, `new_status` non-validation) documented in §3/§5 but not opened as separate Ledger entries this ship — defer to a future consolidation pass on schema-vs-handler param drift class (already tracked by existing Ledger #5 systemic detection lint approaching third-instance threshold).
- **Ledger entries opened this ship (3, shared with blog_tool sibling doc — appended to Rigby Tool Gap Ledger deliverable `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`):**
  - **#36** — blog_tool Deliverable/SelfBlog approve-path gap (orthogonal — blog_tool-scoped).
  - **#37** — `feedback_tool.update` uses bare `.save()` vs sibling's `update_fields=[...]` discipline. Write-scope drift. **This tool's Ledger entry.**
  - **#38** — no handler-layer `dry_run` affordance across 5 batch-2 mutation actions (`approve`, `reject`, `generate`, `submit`, `update`). Substrate gap gating live mutation verification.
- **Post-merge live-dispatch verification (per PLAYBOOK-7.4.4):** exercise `feedback_tool action=stats` + `feedback_tool action=list` via Rigby after `make recycle-all` at merge; confirm counts + envelope shape match §6 evidence. Recorded in S2936 handoff.
