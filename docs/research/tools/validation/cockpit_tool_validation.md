# `cockpit_tool` — Validation Report (S2923)

**Tool:** `cockpit_tool`
**Schema:** `core/services/pa_tool_schemas.py:4562`
**Handler:** `core/services/td_handlers_gateway.py:1022` (`_handle_cockpit`)
**Register site:** `core/services/tool_dispatcher.py:571`
**Session:** S2923 (Slice 4 batch 6 — first `external` / cascading-side-effect exercise; single-tool ship per S2923 T0 SIGN Q1(a) AGREE + Chris ratification; 431-line handler, largest single tool in Slice 4; batch 7 closes Slice 4 with `proactive` + `profile` `spreading` pair pre-audited this session)
**HEAD at validation:** `2161c47a4` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape) + §5a mutation-containment with 4-tier blast-radius classification. Both mutation actions (`trigger_task` + `revoke_task`) classified `external` PRIMARY with `cascading` gated side-effect noted; corrects the S2922 close 00-START pre-classification of "cascading" (see §5a rationale). Post-merge live-dispatch verify per PLAYBOOK-7.4.4 on all 8 actions including both mutation actions.
**Category upgrade target:** `untested` → `validated_full` (all 8 actions in scope this ship — 6 pure-read + 2 mutation)
**Rigby SIGN:** S2923 T0 SIGN AGREE — 2-turn cycle grounded in 9 `repo_tool` receipts across Q1/Q2/Q3/Q4/Q5 (Q3 full cascading-tier signal-chain trace: `escalate_failure_cluster` at `failure_cluster_signals.py:123` → `transaction.on_commit(_dispatch(snapshot))` at `:173` → `attention_bridge.create_failure_cluster_attention` → `HumanInterfaceService.create_attention_item(source_type='failure_cluster')` → `HumanAttentionItem` inbox row; dedup 30min via `(idempotency_key OR (task_name, urgency_band))` two-key OR); zero rubber-stamp. **T1 SIGN correction (in-doc):** primary tier reclassified from S2922 close-cascade "cascading" to `external` after handler-line-range re-verification revealed the S2922 handoff's `CeleryTaskEvent.save at 1030-1039` line reference pointed at help-text (not a save); actual mutation sites at 1367 (`create(status='QUEUED')`) and 1421 (`save(status='REVOKED')`) both trip the post_save signal but hit the `status != 'FAILURE'` early-return gate — so signal wiring exists on the model but no cascade effect fires for the tool's own mutations.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`cockpit_tool` is the Celery operations dashboard — Rigby's window into scheduled tasks, live workers, queue pressure, and task failures. Use it when Chris (or Rigby-in-conversation) asks: "what beat tasks run when?" / "what's the status of task `<id>`?" / "which workers are alive and what are they doing?" / "any recent task failures?" / "how backlogged are the queues?" / "kick off a nightly refresh manually" / "cancel that stuck task."

Distinct from `system_health` handlers under `td_handlers_ops.py` (operational health checks — DB freshness, service-level pings — no Celery-substrate depth), from `railway_tool` (Railway service management — restart/redeploy at the platform layer, not task layer), and from `narrative_tool` (drift / shifts / evidence — content-side introspection, not infra). `td_handlers_ops.py` DOES proxy two cockpit actions (`beat_schedule` and `queue_lengths` at `td_handlers_ops.py:295-296` and `:905-914`) via internal `_handle_cockpit(...)` re-entry — those proxy call sites are documented as intentional composition, not dispatcher re-entry.

## Covered actions

- `help` — **in scope this ship** — verified live. Returns the 7-action inventory as a `{tool, actions}` dict at handler lines 1028–1040. Note: line 1030 contains the self-reference literal `'tool': 'cockpit_tool'` — this is help-payload string content, NOT an outbound tool dispatch. Confirmed 0 outbound dispatches gateway-wide via S2923 T0 SIGN Q2 grep.
- `beat_schedule` — **in scope this ship** — verified live. Reads `PeriodicTask.objects.select_related('interval', 'crontab').order_by('name')[:limit]` at handler lines 1043–1046. Envelope: `{action, total, tasks: [{name, task, enabled, schedule, last_run_at, total_run_count, queue}]}`.
- `task_status` — **in scope this ship** — verified live. Reads `CeleryTaskEvent.objects.filter(task_id=...).order_by('-started_at').first()` at handler lines 1066–1068 with `celery_app.AsyncResult(task_id)` fallback at line 1087 when no telemetry row exists. Envelope: `{action, source: 'celery_event'|'async_result', task_id, task_name, status, ..., duration_seconds}` or fallback shape `{action, source: 'async_result', task_id, status, ready, successful, result_preview, note}`.
- `worker_health` — **in scope this ship** — verified live. Uses `celery_app.control.inspect(timeout=5)` at handler line 1101 to fan out `active()` + `stats()` control queries across workers. Envelope: `{action, workers: [{name, active_tasks, concurrency, pool, prefetch_count}]}`. Note: this action makes a Celery control-broadcast round-trip — see §5b.
- `recent_failures` — **in scope this ship** — verified live. Reads `CeleryTaskEvent.objects.filter(status='FAILURE').order_by('-started_at')` with optional `queue` filter at handler lines 1116–1122. Envelope: `{action, count, failures: [{task_name, task_id, started_at, error_type, error_message, queue, worker, duration_seconds}]}`. `error_message` truncated to 300 chars.
- `queue_lengths` — **in scope this ship** — verified live. Multi-source composite: (1) `celery_app.control.inspect(timeout=5)` at line 1198 for active/reserved counts; (2) Redis `LLEN` at line 1226 per allowlisted queue for true broker depth; (3) Redis `LRANGE` sample at line 1247 for oldest-message-age classification (`GREEN` / `YELLOW` / `RED` / `CRITICAL` per depth+age thresholds at lines 1157–1179). Envelope: `{action, queues, overall_state, overall_reasons}` + optional `redis_error` field. Complex read logic — 178 lines (1138–1316) of the handler's total 431. Degrades gracefully on Redis / inspect failures.
- `trigger_task` — **in scope this ship — mutation, classified `external`** — verified live. Allowlist-gated Celery dispatch: `celery_app.send_task(task_name, kwargs=task_kwargs, queue=queue)` at handler lines 1358–1360. Immediately writes `CeleryTaskEvent.objects.create(status='QUEUED')` at lines 1367–1372 (fires post_save signal — see §5a for gate discussion) + `register_task_notification(...)` at lines 1380–1385 (writes Redis key). Envelope: `{action, task_name, task_id, queue, status: 'dispatched'}`. **Allowlist enforced at lines 1331–1353** — 11 fully-qualified task names; unknown task returns `{error, allowed_tasks: sorted(ALLOWED_TASKS)}`. See §5a for blast-radius classification.
- `revoke_task` — **in scope this ship — mutation, classified `external`** — verified live. Celery control broadcast: `celery_app.control.revoke(task_id, terminate=bool(terminate))` at handler line 1406. Then updates `CeleryTaskEvent.status = 'REVOKED'` via `event.save(update_fields=['status'])` at lines 1420–1421 (fires post_save signal — gate discussion in §5a) + Redis delete of any pending notification at line 1430. Envelope: `{action, task_id, revoked, terminate, note}`. See §5a for blast-radius classification.

Default action = `help` (per `payload.get('action', 'help')` at handler line 1024).

## 3. Schema notes

- **Required:** `action` (enum: `beat_schedule` / `task_status` / `worker_health` / `recent_failures` / `queue_lengths` / `trigger_task` / `revoke_task` / `help`).
- **Optional:** `task_id` (str; required by `task_status` and `revoke_task`); `limit` (int; default 20 per schema, cap 50 via `min(int(payload.get('limit', 20)), 50)` at handler line 1025 — matches gateway norm); `queue` (str; filter for `recent_failures` OR target queue for `trigger_task`, default `long_running` for trigger); `task_name` (str; required by `trigger_task`); `task_kwargs` (obj; passed through to `send_task` for `trigger_task`); `terminate` (bool; default False for `revoke_task`).
- **Cross-reference:** verbatim schema at `pa_tool_schemas.py:4560-4618`.
- **Envelope shape:** varies substantially by action — `beat_schedule` returns `total` + `tasks[]`; `recent_failures` returns `count` + `failures[]`; `worker_health` returns `workers[]` (no count); `queue_lengths` returns nested `queues` object + `overall_state` + `overall_reasons[]`; `task_status` has two source-conditional shapes (`celery_event` vs `async_result`); `trigger_task` and `revoke_task` each return distinct 4–5 field acknowledgments. Consistent with the envelope-key-asymmetry-across-actions pattern already at 3/3 triggered post-S2919 batch 2 (still Chris-gated).
- **Allowlist enforcement at handler layer, not schema:** the `trigger_task` action accepts any string via schema `task_name` but the handler-side `ALLOWED_TASKS` set at lines 1331–1347 rejects non-allowlisted values with `{error: f'Task not in allowlist: {task_name}', allowed_tasks: sorted(ALLOWED_TASKS)}`. 11 fully-qualified tasks enumerated. Comment at 1324–1329 documents S1246's removal of a ghost task (`check_system_health` — never had a `@shared_task` definition; stuck `QUEUED` telemetry rows were the symptom). Recording the schema-vs-handler split as a defense-in-depth authoring choice: schema stays permissive (any string) for evolvability; handler is the enforcement point. Comparable to how `td_handlers_ops.py:295-296` re-uses `_handle_cockpit(...)` directly rather than re-implementing the allowlist.
- **`terminate` semantic:** default False (queued-only removal from broker); True sends SIGTERM to running workers. Response `note` field surfaces this to the caller.

## 4. Golden-path examples

**Example 1 — list all beat-scheduled tasks (most operator-common):**
```json
{"action": "beat_schedule"}
```
Expected envelope: `{"action": "beat_schedule", "total": <int>, "tasks": [{"name": "...", "task": "core.tasks....", "enabled": <bool>, "schedule": "<interval|crontab str>", "last_run_at": "<isoformat|null>", "total_run_count": <int>, "queue": "<str>"}, ...]}`. Sorted by task name; capped at 20 by default (up to 50 via `limit`).

**Example 2 — check queue pressure across all workers:**
```json
{"action": "queue_lengths"}
```
Expected envelope: `{"action": "queue_lengths", "queues": {"<queue_name>": {"active": <int>, "reserved": <int>, "depth": <int|null>, "oldest_age_seconds": <float|null>, "estimated": <bool>, "sample_size": <int>, "state": "GREEN|YELLOW|RED|CRITICAL", "reasons": [...]}, ...}, "overall_state": "GREEN|YELLOW|RED|CRITICAL", "overall_reasons": ["<queue>=<state> (depth=X, age=Ys)", ...]}`. Optional `redis_error` field appears if the Redis path degraded.

**Example 3 — dispatch an allowlisted task (mutation; external):**
```json
{"action": "trigger_task", "task_name": "core.tasks.run_body_system_check", "queue": "long_running"}
```
Expected envelope: `{"action": "trigger_task", "task_name": "core.tasks.run_body_system_check", "task_id": "<uuid>", "queue": "long_running", "status": "dispatched"}`. Side effects: (1) task queued to Celery broker via `send_task`; (2) `CeleryTaskEvent(status='QUEUED')` row inserted; (3) Redis notification-metadata key written for `task_postrun` back-channel; (4) worker picks task up asynchronously — outcome NOT reflected in the immediate envelope (poll via `task_status`).

**Example 4 — revoke a stuck task with terminate (mutation; external):**
```json
{"action": "revoke_task", "task_id": "<uuid>", "terminate": true}
```
Expected envelope: `{"action": "revoke_task", "task_id": "<uuid>", "revoked": true, "terminate": true, "note": "Task revocation sent. Queued tasks are removed; running tasks are terminated only if terminate=true was set."}`. Side effects: (1) revoke control broadcast to all workers; (2) `CeleryTaskEvent.status = 'REVOKED'` if a QUEUED/STARTED row exists; (3) Redis notification-metadata key deleted; (4) actual termination is best-effort — workers may already have completed the task.

## 5. Failure / empty-state / pagination notes

- **Unknown action:** returns `{"error": f"Unknown cockpit_tool action: {action}"}` at handler line 1446. Not raised — in-envelope.
- **Handler exception:** caught at line 1448, logged via `logger.error(f"[COCKPIT] {action} error: {e}", exc_info=True)`, returns `{"error": <str>}` from handler. Handler omits `error_code`; **dispatcher auto-backfills `error_code='legacy_error'`** at `tool_dispatcher.py:862-885` per S2874 mixed-mode migration (S2876 breadcrumb telemetry) — final envelope observed by callers is `{"error": <str>, "error_code": "legacy_error"}`. **19th corroborating instance** of the unmigrated-handler pattern post-S2922's 18-instance count. Substrate arc still gated on explicit Chris directive per 00-START forbidden-list; Rigby S2920 Q4(a) semantic-nuance refresh (treat `error_code` values as first-class semantics) deferred post-D6 per S2921 Q5(c) Chris ratification.
- **`task_status` — missing task_id:** returns `{"error": "Provide task_id to check status"}` at line 1064. Not raised.
- **`task_status` — no CeleryTaskEvent row:** falls through to `celery_app.AsyncResult(task_id)` at line 1087 — returns `source: 'async_result'` shape. If task is unknown to the result backend, `result.status = 'PENDING'` (Celery default for unknown IDs) — the envelope includes `note: 'CeleryTaskEvent not yet recorded — task may still be queued or starting'` to distinguish from a genuinely pending task.
- **`worker_health` — no workers available:** `inspector.stats()` returns `{}` on timeout or empty cluster; envelope is `{"action": "worker_health", "workers": []}`. Not an error.
- **`recent_failures` — no failures:** returns `{"action": "recent_failures", "count": 0, "failures": []}`. Empty state is normal.
- **`queue_lengths` — Redis unreachable:** `except Exception as e` at lines 1272–1277 captures the failure. Envelope surfaces `redis_error: f'{type(e).__name__}: {str(e)[:200]}'` — the classifier falls back to inspect-only counts; per-queue `state` defaults to `GREEN` with `reasons: ['depth_unknown']`. Degrades gracefully.
- **`queue_lengths` — inspect timeout:** `celery_app.control.inspect(timeout=5)` at line 1198 — 5s inspect timeout; `active()` / `reserved()` may return `None` (per Celery default) → normalized to `{}` at lines 1199–1200. No queue counted from that worker; Redis path still runs.
- **`queue_lengths` — no timestamp in Redis message:** classifier falls back to depth-only per lines 1157–1179; `parse_error: 'no_timestamp_field'` surfaces on the per-queue entry; classification adjusts (age-based bumps skipped).
- **`trigger_task` — missing task_name:** returns `{"error": "Provide task_name to trigger"}` at line 1321.
- **`trigger_task` — task not in allowlist:** returns `{"error": f"Task not in allowlist: {task_name}", "allowed_tasks": sorted(ALLOWED_TASKS)}` at lines 1350–1353. The allowlist enumeration in the response is a Rigby-usability affordance — she can see what she's allowed to dispatch.
- **`trigger_task` — CeleryTaskEvent write failure:** caught at lines 1373–1374 with `pass`; comment says "non-critical — telemetry signal will create on worker pickup". Dispatch still succeeds. This means the returned `task_id` MAY reference a task whose telemetry row is absent until the worker picks it up — `task_status` handles this via the `AsyncResult` fallback.
- **`trigger_task` — notification-register failure:** caught at lines 1386–1387 with `pass`; comment says "non-critical". Task still dispatches; back-channel notification just won't post to the PA conversation.
- **`revoke_task` — missing task_id:** returns `{"error": "Provide task_id to revoke"}` at line 1400.
- **`revoke_task` — revoke API failure:** returns `{"action": "revoke_task", "task_id": <id>, "revoked": false, "error": <str>}` at lines 1408–1413. Explicitly typed with `revoked: false`, distinguishing broker-level failure from downstream cleanup failures.
- **`revoke_task` — CeleryTaskEvent update failure:** caught at lines 1422–1423 with `pass`. Revoke broadcast still succeeded.
- **`revoke_task` — Redis notification cleanup failure:** caught at lines 1431–1435 with a `logger.warning(...)` (softer than swallowing). Revoke still succeeds; the stale notification key will eventually TTL out.
- **`revoke_task` — task already completed:** the broker-level `revoke()` succeeds silently; there's no "not found" branch. `event.save(update_fields=['status'])` only fires if `event.status in ('QUEUED', 'STARTED')` per line 1419 — SUCCESS/FAILURE/REVOKED rows are left untouched. Caller receives `{revoked: true, ...}` regardless of whether the revoke had any observable effect — semantic-quirk noted here for the caller.
- **No pagination cursor** on `beat_schedule` or `recent_failures` — hard-cap 50. Not a defect for the current single-user use case.

## 5a. Mutation containment (per Rigby SIGN Q3 — §5a 4-tier blast-radius taxonomy amended S2921)

> **⚠ Latent cascade exists on `CeleryTaskEvent`, currently gated.** Dynamic `post_save.connect(escalate_failure_cluster, sender=CeleryTaskEvent, ...)` at `core/signals/failure_cluster_signals.py:183` fires on EVERY `CeleryTaskEvent.save()`. Both mutations in this tool trip the signal, but the receiver hard-gates at `if status != 'FAILURE': return` (line 141) — cockpit writes only `'QUEUED'` (trigger_task line 1371) and `'REVOKED'` (revoke_task line 1420), so the cascade path is never reached from the tool's own mutations. **Classification below is `external` PRIMARY under this gate. If cockpit ever writes `CeleryTaskEvent.status='FAILURE'` OR the receiver's gate condition changes, both mutations reclassify to `cascading+external` (dual-tier) and this doc must be amended.** Reclassify triggers enumerated at the end of this section.

Two mutation actions in this tool. Classification and rationale per the 4-tier blast-radius schema at `_TEMPLATE_per_tool_validation.md` §5a.

| Action | Mutation type | Blast-radius tier | Rationale |
|---|---|---|---|
| `trigger_task` | `celery_app.send_task(...)` at handler line 1358–1360; `CeleryTaskEvent.objects.create(status='QUEUED')` at 1367–1372; `register_task_notification(...)` writing Redis at 1380–1385 | `external` PRIMARY | Leaves the process via THREE distinct external boundaries: (1) Celery `send_task` publishes to broker → picked up by worker → worker executes arbitrary allowlisted task (which may itself do LLM calls, DB writes, network fetches, sub-tool dispatch — the tool has NO visibility into what the dispatched task does); (2) `CeleryTaskEvent.create` fires `post_save` signal — `escalate_failure_cluster` receiver runs but hits the `status != 'FAILURE'` early-return gate (line 141 of `failure_cluster_signals.py`) since inserted status is `'QUEUED'`; (3) `register_task_notification` writes a Redis key via `_get_redis()`. Signal wiring EXISTS on the model (dynamic `post_save.connect(...)` at `failure_cluster_signals.py:183`); cascade EFFECT does NOT fire for this tool's insert (gate returns early). Downstream: worker eventually completes or fails → celery_telemetry writes an updated `CeleryTaskEvent` row with terminal status → IF terminal status is `'FAILURE'`, the cascade path fires (aggregator + dedup + `HumanAttentionBridge.create_failure_cluster_attention` → `HumanAttentionItem` inbox row). But that downstream cascade is triggered by the worker's telemetry write, not by the tool's own insert — the tool's blast-radius stops at "task dispatched + telemetry stub created + notification key set." |
| `revoke_task` | `celery_app.control.revoke(task_id, terminate=...)` at handler line 1406; `event.save(update_fields=['status'])` where status='REVOKED' at 1420–1421; `r.delete(f'{_KEY_PREFIX}{task_id}')` at 1430 | `external` PRIMARY | Leaves the process via THREE distinct external boundaries: (1) Celery `control.revoke` sends a control message to ALL workers via broker — best-effort (workers may have already completed the task); with `terminate=True` sends SIGTERM to running workers; (2) `event.save(update_fields=['status'])` fires `post_save` signal — same gate discussion as `trigger_task` (`status='REVOKED'` hits the `status != 'FAILURE'` early-return gate; no cascade effect); (3) Redis delete via `_get_redis()`. Bounded to (task_id, notification_key) tuple; no cross-user reach unless the caller passes a task_id belonging to a different user's dispatched task — which is the single-user-pre-prod-absorbed multi-tenant-leak pattern already at 3/3 instances. |

**Signal-cascade side-effect discussion (both mutations):** Dynamic `post_save.connect(escalate_failure_cluster, sender=CeleryTaskEvent, ...)` is wired at Django startup by `connect_failure_cluster_signals()` at `failure_cluster_signals.py:183–189` (called from `core/apps.py:234–235`). This signal fires on EVERY `CeleryTaskEvent.save()` — including the two mutations in this tool. However:

- The receiver early-returns when `getattr(instance, 'status', None) != 'FAILURE'` (line 141 of `failure_cluster_signals.py`).
- `trigger_task` writes `status='QUEUED'` (line 1371 of the handler) → gate returns early.
- `revoke_task` writes `status='REVOKED'` (line 1420) → gate returns early.
- Kill switch: `settings.FAILURE_CLUSTER_HAI_ENABLED` (default True) at line 138 of `failure_cluster_signals.py`.
- Dedup: `_open_hai_exists()` at lines 69–106 checks a two-key OR — `idempotency_key` (narrow race) OR `(task_name, urgency_band)` inside a 30-min window (per `settings.FAILURE_CLUSTER_DEDUP_MINUTES`, default 30). Fails safe to `False` on lookup error → allows escalation (documented preference for false-positive over swallowed critical).
- On-commit dispatch via `transaction.on_commit(lambda: _dispatch(snapshot))` at line 173 → `attention_bridge.create_failure_cluster_attention(snapshot)` at `_dispatch(...)` in the same file → `HumanInterfaceService.create_attention_item(source_type='failure_cluster')` → `HumanAttentionItem` inbox row.

**Net effect:** cockpit's own mutations produce NO cascade effect (both hit the gate). BUT the ripple-effect from `trigger_task` — the dispatched worker may fail and produce a `status='FAILURE'` telemetry row later — DOES trigger the cascade path downstream. That cascade fires from the worker's write, not the tool's write. So the correct §5a authoring choice is `external` PRIMARY for both mutations (Celery leaves the process; that's the highest-tier blast-radius), with the `cascading` signal wiring documented as a side-effect that does NOT fire for the tool's own operations under normal shape.

**S2922 close-cascade discovery — reclassification correction:**
The S2922 close 00-START refresh pre-classified cockpit as `cascading` tier based on the dynamic `.connect()` discovery. Handler-line-range re-verification during this ship's authoring shows:
- The 00-START's reference `CeleryTaskEvent.save at 1030-1039` points at the `help` payload return dict (lines 1028–1040), NOT a save.
- Actual mutation sites are lines 1367 (`create(status='QUEUED')`) and 1421 (`save(status='REVOKED')`).
- Both trip the post_save signal but hit the `status != 'FAILURE'` early-return gate.
- Neither writes `status='FAILURE'` directly — so neither exercises the cascade path.
- The tool's PRIMARY blast-radius is `external` (Celery fan-out / control broadcast + Redis writes), not `cascading`.

Substrate observation: this is the pattern the amended §5a §4-tier taxonomy wants callers to write down — when signal wiring EXISTS on a model but the receiver's gate exempts the tool's specific mutation shape, `external` (or the mutation's actual highest-reach tier) is the correct PRIMARY label, with the `cascading` wiring documented as side-effect / gate-exempt. Adds nuance to the S2921 taxonomy without changing it.

**Deferral status:** NOT deferred. Ship-in-scope this batch — this ship exercises both mutation actions post-merge to verify the `external` classifications hold end-to-end (see §6 post-merge verification protocol).

**Comparison to batch-7 candidates (final Slice-4 spreading pair):**
- `proactive.bulk_ack` — `spreading` (bulk multi-row: up to 200 rows in `ProactiveNotification.filter(...).update(is_read=True)`; user-scoped but broad within that user). Batch 7 pre-audit confirmed spreading via S2923 T0 SIGN Q4 — no signal receivers, no `.connect(`, no `transaction.on_commit` dispatch chain in the handler region.
- `profile.update_preferences` — `spreading` (`get_or_create` × 2 + `save` × 1 — may implicitly create `EnhancedUserProfile` row + persist preference changes). Batch 7 pre-audit confirmed spreading via S2923 T0 SIGN Q4 — direct ORM writes only.

**Reclassify triggers (any of the following flips this tool's mutations to `cascading+external` dual-tier):**
1. Any code path in `_handle_cockpit` (or any tool that proxies into it) begins writing `CeleryTaskEvent.status='FAILURE'` — the gate at `failure_cluster_signals.py:141` no longer exempts the write; the escalation chain fires.
2. The gate literal `if status != 'FAILURE': return` at `failure_cluster_signals.py:141` changes to accept a status this tool writes (e.g. gate becomes `if status not in ('FAILURE', 'REVOKED'): return` — then `revoke_task` fires the cascade).
3. Kill switch `settings.FAILURE_CLUSTER_HAI_ENABLED` semantics change from default-True to config-dependent AND the config is toggled at runtime — cascade may fire under some deployments and not others; document dual-state classification.
4. Any new `post_save.connect(..., sender=CeleryTaskEvent, ...)` or `@receiver(post_save, sender=CeleryTaskEvent)` is added anywhere in the codebase with a gate that DOES accept `'QUEUED'` or `'REVOKED'` status — new receiver may cascade from this tool's writes.
5. Any allowlisted `trigger_task` target begins directly calling `_handle_*` in `td_handlers_*.py` (dispatcher re-entry from the fanned-out worker) — the tool's downstream reach expands and re-entry hotspot list changes.

Rigby T1 SIGN codified this "gate-quoted + reclassify-trigger enumerated" pattern as the correct §5a authoring convention for tools with latent-but-gated signal cascades — see S2923 T1 SIGN Q5(ii) AGREE. Pattern is doc-level, not template-level: keep the §5a template as-is; use this doc's §5a as the reference exemplar for future latent-cascade authoring.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `PeriodicTask.objects.select_related(...).order_by(...)[:limit]` | `read` | `td_handlers_gateway.py:1043-1046` | ORM SELECT with JOIN; `beat_schedule` action |
| `PeriodicTask.objects.count()` | `read` | `td_handlers_gateway.py:1049` | ORM aggregate; `beat_schedule` action |
| `CeleryTaskEvent.objects.filter(task_id=...).order_by(...).first()` | `read` | `td_handlers_gateway.py:1066-1068` | ORM SELECT; `task_status` action |
| `celery_app.AsyncResult(task_id)` | `network` (result backend) | `td_handlers_gateway.py:1087` | Celery result backend read (Redis); `task_status` fallback |
| `celery_app.control.inspect(timeout=5).active()` / `.stats()` | `network` (broker broadcast) | `td_handlers_gateway.py:1101-1103` | Celery control broadcast; `worker_health` action |
| `CeleryTaskEvent.objects.filter(status='FAILURE').order_by(...)[:limit]` | `read` | `td_handlers_gateway.py:1116-1122` | ORM SELECT; `recent_failures` action |
| `celery_app.control.inspect(timeout=5).active()` / `.reserved()` | `network` (broker broadcast) | `td_handlers_gateway.py:1198-1200` | Celery control broadcast; `queue_lengths` action |
| `redis_lib.from_url(...).llen(q)` / `.lrange(q, -20, -1)` | `network` (redis) | `td_handlers_gateway.py:1218, 1226, 1247` | Redis direct I/O; `queue_lengths` action; degrades on failure |
| `celery_app.send_task(task_name, kwargs=..., queue=...)` | `dispatch` | `td_handlers_gateway.py:1358-1360` | Celery apply-async equivalent; `trigger_task` — see Appendix A |
| `CeleryTaskEvent.objects.create(status='QUEUED')` | `db_write` | `td_handlers_gateway.py:1367-1372` | ORM INSERT (1 row); fires post_save signal → gate returns early — see §5a |
| `register_task_notification(...)` | `network` (redis) | `td_handlers_gateway.py:1380-1385` | Redis SET via `_get_redis()`; `trigger_task` back-channel |
| `celery_app.control.revoke(task_id, terminate=...)` | `dispatch` | `td_handlers_gateway.py:1406` | Celery control broadcast; `revoke_task` — see Appendix A |
| `CeleryTaskEvent.objects.filter(task_id=...).first()` + `.save(update_fields=['status'])` | `read` + `db_write` | `td_handlers_gateway.py:1418, 1421` | ORM SELECT + UPDATE (1 row, 1 field); fires post_save signal → gate returns early — see §5a |
| `_get_redis().delete(f'{_KEY_PREFIX}{task_id}')` | `network` (redis) | `td_handlers_gateway.py:1427-1430` | Redis DEL; `revoke_task` notification-key cleanup |
| `os.environ` / `django.conf.settings` reads | `read` | `td_handlers_gateway.py:1217-1218` | Config read; no network I/O |

### Appendix N — Network-Preflight

Cockpit has multiple network first-hops: Celery control broadcasts via broker (worker_health, queue_lengths, revoke_task), Redis LLEN/LRANGE/SET/DEL (queue_lengths, trigger_task, revoke_task), and Celery send_task via broker (trigger_task). All go to platform-internal infrastructure — no external HTTP endpoints. Appendix N (Network-Preflight) is filled at reduced fidelity because the endpoint set is internal-only.

- **N1. Endpoint derivation source** — `settings.CELERY_BROKER_URL` (used by `celery_app` init + explicitly at line 1219 for Redis client construction). `_get_redis()` at `core/services/task_notification.py` — same broker URL for notification-substrate Redis. All endpoints resolved from Django settings; NO user-payload-driven URL construction.
- **N2. Auth posture** — `none` at the transport layer; broker/Redis authentication is at the URL-embedded credential level (`redis://user:pass@host:port/db` format). Broker/Redis are platform-internal; no bearer / basic / HMAC applied by this handler.
- **N3. Timeout envelope** — Celery `control.inspect(timeout=5)` explicit at handler lines 1101 + 1198 (5 second inspect timeout). Redis client init: `socket_connect_timeout=2, socket_timeout=2` at lines 1220–1221. No retry logic in-handler (Celery/redis-py defaults apply). No total-run bound.
- **N4. SSRF / egress allowlist** — URL source is Django settings (repo-controlled config), not user payload. Standard SSRF waiver applies: caller cannot inject a URL. Redis client construction uses `redis_lib.from_url(...)` directly with `settings.CELERY_BROKER_URL` — no allowlist regex needed because there's no untrusted URL source.
- **N5. Redirect + non-2xx handling** — N/A for broker/Redis (protocol-level, not HTTP). Broker control broadcasts return `None` on worker non-response (silent — normalized to `{}` at lines 1199–1200). Redis client raises exceptions on connection failure → caught at lines 1272–1277 for `queue_lengths` (surfaces `redis_error` field); NOT caught for `trigger_task` / `revoke_task` Redis writes (they use `pass` swallowing at 1373–1374 + 1386–1387 or `logger.warning` at 1431–1435).

### Appendix A — Async-Fanout

Two actions dispatch asynchronously (`trigger_task`) or broadcast asynchronously (`revoke_task`). Filled per S2917 batch 7 pattern.

- **A1. Dispatch target type(s)** — `trigger_task` uses `celery_app.send_task(...)` — dispatches by fully-qualified task name to a Celery worker. The tool has NO visibility into what the dispatched task actually does — it's `direct_task` opacity: the handler SEES only the task name string and kwargs; what actually RUNS is the entire body of the allowlisted task (11 tasks per `ALLOWED_TASKS` at handler lines 1331–1347; each may itself do LLM calls, DB writes, network fetches, sub-tool dispatch, dispatcher re-entry, spider crawls, etc.). `revoke_task` uses `celery_app.control.revoke(...)` — control-plane broadcast, not a task dispatch (no new task queued; just cancellation signal).
- **A2. Queue name(s) + priority** — `trigger_task` queue defaults to `long_running` at handler line 1356 (`payload.get('queue', '') or 'long_running'`); overridable via `queue` param. All 11 allowlisted tasks are safe against the `long_running` pool (long-running-1 and long-running-2 workers) — none of them are known-fast tasks that would starve the pool. Priority NOT set. `revoke_task` broadcast has no queue (control-plane).
- **A3. Task_id envelope + polling contract** —
  - **(a) Identifiers returned:** `trigger_task` returns `{task_name, task_id, queue, status: 'dispatched'}` — SINGLE identifier (`task_id`). `revoke_task` returns `{task_id, revoked, terminate, note}` — SINGLE identifier (`task_id`).
  - **(b) Polling endpoint(s):** `task_status` action on the same tool is the canonical polling surface. First reads `CeleryTaskEvent` row (populated by celery_telemetry post-run signal at S2734); falls back to `celery_app.AsyncResult(task_id)` if telemetry row absent. Note: `CeleryTaskEvent` may briefly show `status='QUEUED'` (from `trigger_task`'s eager write at line 1367–1372) even if the worker hasn't picked the task up yet.
  - **(c) Idempotency stance:** `none` — `trigger_task` produces a fresh `task_id` on every dispatch; repeat calls create duplicate Celery jobs. `revoke_task` IS safe_re_run: `yes` for status update (if event already at `REVOKED`, the `if event and event.status in ('QUEUED', 'STARTED')` guard at line 1419 skips re-save); broker-level `revoke()` is idempotent (revoking an already-completed task is a no-op).
- **A4. Downstream side-effect boundary** — this is the audit hotspot. Each of the 11 allowlisted `trigger_task` targets has its own downstream reach:
  - `core.tasks.sync_congress_data` at `core/tasks.py:<varies>` — API fetches from congress.gov + DB writes to congressional-tracking models.
  - `core.tasks.run_all_spiders` — dispatches N sub-tasks (one per spider) via `apply_async` — dispatcher re-entry level 2.
  - `core.tasks.run_spider_network` — spider-network orchestration + `apply_async` fan-out to spider jobs.
  - `core.tasks.spider_data_retention` — DB DELETE bulk on stale spider items.
  - `core.tasks.run_signal_aggregation` — signal-clustering pipeline; may write `SignalCluster` rows + `AutoTopic` rows via `initiative_pipeline_service`.
  - `core.tasks.generate_self_blog_deliberation_task` — v2 content pipeline entrypoint; **LLM calls** downstream via `content_deliberation_runner`; may also chain to `EditorAgent` for gate repairs.
  - `core.tasks.backfill_spider_embeddings` — LLM embedding calls to pgvector.
  - `core.tasks.check_content_diversity` — content-scoring aggregate; DB writes.
  - `core.tasks.run_body_system_check` — 9 body-system checks; DB writes to `BodyCheck` + `OpsRun`; may trigger `BodyCoordinator` reflexes → downstream Celery tasks.
  - `core.tasks.backfill_deliverable_workspaces` — data-migration task; bulk DB writes.
  - `core.tasks.content_autonomy_loop` — S1098 canary-priming path; `EditorAgent` invocation → LLM calls + `DELIVERABLE_APPEND` gate repair; **budget-preflight protected** per comment at 1342–1346.
  - **Dispatcher re-entry:** none of the allowlisted tasks directly call `_handle_*` in `td_handlers_*.py`. But `run_all_spiders` → `run_spider_network` → per-spider apply_async is a 2-level fan-out; `content_autonomy_loop` → `EditorAgent` → agent execution may re-enter `execute_agent_task` (which itself has downstream reach). These are downstream-of-first-hop; the first-hop from cockpit is `send_task` to the entry-point task.
- **A5. Observability + cancel semantics + revisit triggers** —
  - **(a) Observability contract:** `task_status` action is the authoritative surface. `CeleryTaskEvent` fields (status, started_at, finished_at, duration_seconds, worker, queue, error_message, rss_mb_start, rss_mb_end) are populated by celery_telemetry signal handlers. `AsyncResult` fallback is best-effort — its `status='PENDING'` may mean either "still queued" or "unknown task_id" (indistinguishable without the CeleryTaskEvent). Comment at line 1096 documents this.
  - **(b) Cancel semantics:** `revoke_task` provides cancel. `terminate=False` (default) removes from queue only; `terminate=True` sends SIGTERM to running workers via the Celery control channel. Broker-level revoke is best-effort — workers that have already picked up the task will only see the terminate signal if their pool implementation supports it (solo/prefork/gevent all support; celery default). Domain-side status marker: `CeleryTaskEvent.status = 'REVOKED'` written at line 1420 (only for QUEUED/STARTED rows per line 1419 guard).
  - **(c) Revisit triggers:** the `ALLOWED_TASKS` set is the single largest audit surface — any addition to it expands the tool's downstream reach. Comment at 1324–1329 (S1246 ghost-task removal) shows the operational-safety concern is real. Revisit this Appendix A on: (1) any addition or removal in `ALLOWED_TASKS`; (2) any change to `celery_app.send_task` signature or default queue routing; (3) any change to the polling contract (schema of `CeleryTaskEvent` fields, or if a new fallback beyond `AsyncResult` is added); (4) any change to Celery version (control-plane semantics can shift); (5) any new dispatcher-re-entry site added inside the allowlisted tasks.

Both Appendices declared "filled at reduced fidelity" because cockpit is the first Slice 4 tool where they apply substantively — batches 1–5 were declared N/A per S2918 T0 SIGN Q2 gateway-wide DISAGREE (0/17 gateway tools with the three literal patterns) + per-tool confirmation. Batch 6 shifts that count: cockpit IS a first-hop dispatcher via `celery_app.send_task` and `celery_app.control.revoke`. Gateway-wide first-hop-literal count updates: **1/17** post-batch-6 (cockpit); other 16 still 0. Per Rigby S2923 T0 SIGN Q2 confirmation — this is the first Slice 4 tool where Appendix A is authored substantively; per-tool watch continues for batches 7+.

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification on all 8 actions (including both mutation actions) appended to the S2923 handoff. Expected envelope shapes documented in §4 golden-path examples.

**Post-merge verification protocol:**

For `help`:
1. Dispatch `{"action": "help"}`.
2. Response envelope: `{"tool": "cockpit_tool", "actions": [<7-item list>]}`.
3. Verify all 7 action names in the list match the schema enum minus `help` itself.

For `beat_schedule`:
1. Dispatch `{"action": "beat_schedule", "limit": 5}`.
2. Response envelope contains `total` matching `PeriodicTask.objects.count()` at dispatch time; `tasks` array has ≤5 entries.
3. Cross-check first entry against `PeriodicTask.objects.order_by('name').first()` — `name`, `task`, `enabled` fields match.

For `task_status`:
1. Pick a recent task_id from `CeleryTaskEvent.objects.order_by('-started_at').first().task_id`.
2. Dispatch `{"action": "task_status", "task_id": "<uuid>"}`.
3. Response envelope contains `source: 'celery_event'` + all documented fields; verify `task_name` + `status` match the ORM row.
4. Repeat with a fabricated UUID → expect `source: 'async_result'` fallback shape + `note` field.

For `worker_health`:
1. Dispatch `{"action": "worker_health"}`.
2. Response envelope: `{action: 'worker_health', workers: [<per-worker dict>, ...]}` — verify at least one worker present if the recycle cascade ran.
3. Each worker entry has `name`, `active_tasks`, `concurrency`, `pool`, `prefetch_count` populated (concurrency may be `'unknown'`).

For `recent_failures`:
1. Dispatch `{"action": "recent_failures"}`.
2. Response envelope: `{action, count, failures: [...]}`. Empty state (`count: 0`) is normal in a healthy dev env.
3. If failures exist, verify `error_message` is truncated at 300 chars.

For `queue_lengths`:
1. Dispatch `{"action": "queue_lengths"}`.
2. Response envelope contains `queues` object with entries for at least the QUEUE_ALLOWLIST (default, long_running, pa, content, broadcast, ml, workflow, celery).
3. Verify `overall_state` is one of `GREEN|YELLOW|RED|CRITICAL`; `overall_reasons` array length ≤ 3.
4. If Redis is up: each queue entry has `depth` (int) + `state` fields; `oldest_age_seconds` may be null if no timestamps.
5. If Redis is down: `redis_error` field appears + per-queue entries fall back to inspect-only counts.

For `trigger_task` — verify target choice:
None of the 11 `ALLOWED_TASKS` are truly "no-op safe"; all perform real work when the worker picks them up. Verified during authoring: `check_content_diversity` invokes `ContentDiversityOrchestrator` which auto-creates content for detected gaps (unsafe for dev-DB verify); `spider_data_retention` deletes stale rows; `sync_congress_data` writes new congressional-tracking data; `content_autonomy_loop` publishes blog posts (though budget-gated). The most idempotent-in-effect target is `core.tasks.run_body_system_check` — writes a monitoring snapshot row (analogous to `self_awareness.collect`'s `SystemMetrics` shape). Snapshot-write style is safe to invoke duplicatively; adds one row to the body-check history but does not cascade to other systems.

Verify protocol:
1. Dispatch `{"action": "trigger_task", "task_name": "core.tasks.run_body_system_check", "queue": "long_running"}`.
2. Response envelope: `{action, task_name, task_id, queue, status: 'dispatched'}`.
3. ORM cross-check: `CeleryTaskEvent.objects.filter(task_id=<returned_id>).exists()` returns True (eager write at line 1367–1372); status is `'QUEUED'`.
4. Redis cross-check (best-effort): `_get_redis().exists(f'{_KEY_PREFIX}{task_id}')` returns True IF conversation_id was passed (skip if not).
5. Post-a-few-seconds poll: `{"action": "task_status", "task_id": "<uuid>"}` — should progress QUEUED → STARTED → SUCCESS as worker picks up.
6. Verify cascade non-fire for the tool's own eager QUEUED insert: `HumanAttentionItem.objects.filter(source_type='failure_cluster', payload__task_name='core.tasks.run_body_system_check', created_at__gte=<dispatch_time>).exists()` returns False (gate exempted the insert). Note: `payload__task_name` predicate assumes the failure-cluster bridge stores `task_name` at the top level of payload — confirm via `attention_bridge.create_failure_cluster_attention` signature if false-positive suspected; fall back to `payload__icontains='run_body_system_check'` if the exact key path shifts.
7. Optional stricter check: `HumanAttentionItem.objects.filter(source_type='failure_cluster').order_by('-created_at').first().created_at` is UNCHANGED after step 3 — proves no HAI row landed from the tool's insert.
8. **Latent-cascade reclassify probe (DEV/LOCAL ONLY — do NOT run against prod).** Split into two substeps because a single-row FAILURE insert cannot distinguish "receiver not wired" from "receiver wired + threshold-gated" — the receiver returns early at `failure_cluster_aggregator.py:_DEFAULT_THRESHOLD = 5` (needs ≥5 distinct `task_id` values with matching `task_name` inside the 5-minute sliding window before `snapshot.exceeds_threshold` flips true). One row will always short-circuit at that gate regardless of whether the receiver is wired.

   **Substep A (immediate — receiver-wired check via startup log grep):** in the worker log, look for the init line emitted at `core/apps.py::CoreConfig._register_signals`:
   ```bash
   grep -E '\[FAILURE_CLUSTER_SIGNALS\] receiver wired on CeleryTaskEvent\.post_save' logs/celery.log logs/celery-long-running.log
   ```
   Expected: at least one hit per worker process on startup. Presence confirms the `escalate_failure_cluster` post_save receiver is registered. Absence invalidates the `external` classification (receiver not wired → mutations may cascade unobserved) and the doc must be amended. This substep runs on every recycle and is the required verify.

   **Substep B (OPTIONAL — cascade-fires check via ≥5-tagged-FAILURE-rows probe):** only run when Substep A alone is insufficient (e.g., re-verifying gate mechanics after a threshold config change). In a scratch Django shell on a dev/local DB, insert **five distinct-task_id** FAILURE rows sharing the tagged task_name within the 5-minute window:
   ```python
   from core.models_celery_telemetry import CeleryTaskEvent
   for i in range(5):
       CeleryTaskEvent.objects.create(
           task_id=f'__s2923_cockpit_probe_{i}__',
           task_name='__s2923_cockpit_probe__',
           status='FAILURE',
           queue='long_running',
       )
   ```
   Expected: `[FAILURE_CLUSTER]` action log line (not just the init line) AND one `HumanAttentionItem(source_type='failure_cluster', payload__task_name='__s2923_cockpit_probe__')` row landed. Cleanup after: `CeleryTaskEvent.objects.filter(task_name='__s2923_cockpit_probe__').delete()` + `HumanAttentionItem.objects.filter(source_type='failure_cluster', payload__task_name='__s2923_cockpit_probe__').delete()`. If the cascade does NOT fire from ≥5 tagged FAILURE rows in-window, either the kill switch (`FAILURE_CLUSTER_HAI_ENABLED`) is off or the threshold config was raised — inspect `SystemConfiguration` before invalidating the `external` classification.

For `revoke_task` (on a queued task_id from step 3 above, before it starts running):
1. Immediately after step 3 of `trigger_task` verify, dispatch `{"action": "revoke_task", "task_id": "<uuid>", "terminate": false}`.
2. Response envelope: `{action, task_id, revoked: true, terminate: false, note: "..."}`.
3. ORM cross-check: `CeleryTaskEvent.objects.get(task_id=<uuid>).status` is `'REVOKED'` (may race with worker pickup — accept `'REVOKED'` OR `'STARTED'` OR `'SUCCESS'` as valid depending on race).
4. Verify cascade non-fire for the tool's REVOKED status flip: same HAI check as trigger_task step 6/7 — no `failure_cluster` HAI landed.
5. Redis cross-check: notification key deleted (`exists()` returns False).

**Signal-cascade non-fire assertion for both mutations:** the `escalate_failure_cluster` receiver runs on both the QUEUED insert (trigger_task) and the REVOKED save (revoke_task) — this is invisible from application code but observable in worker logs at `[FAILURE_CLUSTER_SIGNALS] receiver wired on CeleryTaskEvent.post_save (dedup_window_min=30)` init line and NO subsequent `[FAILURE_CLUSTER]` action-log lines during verify (early return at status-gate produces no log). If any `[FAILURE_CLUSTER]` action log DOES appear during verify, the `external` classification for cockpit is invalidated (would indicate the gate was bypassed) and this doc is amended.

## Related

- **Adjacent tools:** `system_health` handlers under `td_handlers_ops.py` (operational health — DB freshness, service pings — no Celery-substrate depth); `railway_tool` (Railway platform management — restart/redeploy, not task management); `narrative_tool` (drift / shifts / evidence — content-side introspection, not infra); `td_handlers_ops.py:295-296` and `:905-914` proxy `beat_schedule` and `queue_lengths` via internal `_handle_cockpit(...)` re-entry (intentional composition, not dispatcher re-entry).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1 — §5a 4-tier blast-radius taxonomy from S2921; first `external` PRIMARY tier exercise this doc); `core/models_celery_telemetry.py:CeleryTaskEvent` (the shared substrate that all mutation actions touch); `core/signals/failure_cluster_signals.py` (dynamic `.connect()` receiver + gate + dedup); `core/apps.py:234-235` (startup registration site for the signal receiver); `core/services/task_notification.py` (`register_task_notification` + `_get_redis` + `_KEY_PREFIX`); `core/services/human_attention_bridge.py` + `core/services/human_interface_service.py` (downstream cascade destination — WOULD fire if the tool wrote status='FAILURE', which it does not).
- **Prior ratifications:** S2892 Path B open, S2918–S2922 Slice 4 batches 1–5, S2921 §5a 4-tier taxonomy amendment.
- **Ledger rows relevant to this ship:**
  - **Legacy-error envelope 19th instance** — continued corroboration; still gated on explicit Chris directive per 00-START forbidden-list. Semantic-nuance refresh (S2920 Q4(a)) deferred post-D6 per S2921 Q5(c) Chris ratification.
  - **First Slice-4 exercise of §5a `external` PRIMARY tier + first tool with substantive Appendix A** — cockpit is the first Slice-4 mutation where the primary blast-radius LEAVES the process (Celery send_task + control broadcast + Redis I/O). Batch 7 (`proactive` + `profile` spreading pair) will not exercise `external` again; Slice 5 (`tool_dispatcher.py`, 14 tools) is where the pattern next surfaces.
  - **First tool where signal wiring EXISTS on the mutation-target model but the receiver's gate exempts the tool's specific mutation shape** — nuance-added-to-taxonomy authoring pattern. Documents that `cascading` classification is EFFECT-based (does the cascade actually reach a downstream row/side-effect?), not merely wiring-based (is there a `post_save.connect` on the model?). No template change; adds a §5a rationale-writing convention. 1st observation — 2nd instance would trigger Ledger evaluation for possible §5a rationale-authoring codification.
  - **S2922 close 00-START pre-classification correction** — the "cockpit = cascading" pre-classification was based on 00-START line reference `1030-1039` which pointed at help-payload text, not a save. Corrected here to `external` PRIMARY + gate-exempt cascading side-effect. Documents the value of handler-line-range re-verification during authoring (Rigby T0 SIGN Q3 caught the correction).
  - **First-hop-literal watch update:** gateway-wide count moves from 0/17 to 1/17 (cockpit — via `celery_app.send_task` at line 1358–1360 and `celery_app.control.revoke` at line 1406). Batch 7 (`proactive` + `profile`) is expected to remain 0 first-hop-literal; overall Slice 4 close will publish the final count.
  - **Cockpit-tool cross-reference proxy pattern** — `td_handlers_ops.py:295-296` (proxy to `_handle_cockpit(action='beat_schedule')`) + `:905-914` (proxy to `queue_lengths`). Intentional composition (ops tool wraps cockpit for op-team-facing calls). Not dispatcher re-entry (direct method call); not an outbound dispatch (no `send_task` from ops side). Recording as an authoring pattern for future cross-referenced tools. 1st observation in-sweep.
  - **11-item ALLOWED_TASKS allowlist audit surface** — the single largest "unknown reach" surface in the tool. Each addition expands the tool's downstream blast-radius. Comment at handler lines 1324–1329 (S1246 ghost-task removal) shows Chris/team have already had one operational-safety incident here. Recording for future audit — any PR that touches `ALLOWED_TASKS` should revisit this doc's Appendix A A4.
  - **00-START span-math regen 3rd time** — cockpit handler 431 lines matched between 00-START pre-count (`handler 1022-1452 = 431 lines`) and this ship's re-count. Rigby Q5(ii) span-math regen commitment now permanent close-ceremony step per S2922 close; validated on 3 consecutive sessions (self_awareness S2921 batch 4 pilot; podcast S2922 batch 5; cockpit S2923 batch 6).
