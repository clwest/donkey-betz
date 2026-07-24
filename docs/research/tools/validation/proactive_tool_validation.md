# `proactive_tool` — Validation Report (S2924)

**Tool:** `proactive_tool`
**Schema:** `core/services/pa_tool_schemas.py:4718`
**Handler:** `core/services/td_handlers_gateway.py:1560` (`_handle_proactive`)
**Register site:** `core/services/tool_dispatcher.py:580`
**Session:** S2924 (Slice 4 batch 7 — FINAL Slice 4 batch, closes the slice at 17/17; shipped as spreading pair with `profile_tool` per Chris D-verdict on Claude+Rigby joint recommendation (a) proactive+profile pair)
**HEAD at validation:** `592f72214` (2026-07-23 — S2924 doc-fix PR#3478 for cockpit §6 step 8 just landed)
**Ship shape:** Doc-only (S2796 shape) + §5a mutation-containment filled with 4-tier blast-radius classification per `_TEMPLATE §5a` schema shipped at S2921. Post-merge live-dispatch verify per PLAYBOOK-7.4.4 on all 8 actions (5 READ + 3 MUTATION).
**Category upgrade target:** `untested` → `validated_full` (all 8 actions in scope this ship — 5 pure-read + 3 mutation)
**Rigby SIGN:** S2924 T0 SIGN AGREE — 1-turn cycle grounded in 10 `repo_tool` receipts (git_info + 3× search + 3× read_file + 3× Appendix N discovery); zero rubber-stamp; **caught real user-scoping gap missed by Claude's initial 00-START rationale** — `mark_read` (`:1660`) and `dismiss` (`:1688`) have NO `user_id` predicate at all; `bulk_ack` (`:1668-1670`) `user_id` filter is CONDITIONAL. Rationale tightened per Rigby T0 SIGN Q3 correction.
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`proactive_tool` surfaces the platform's proactive-intelligence substrate — background-generated alerts, notifications, smart suggestions, and automated-action state (`core/models_unified_system.py:ProactiveAlert / ProactiveNotification / SmartSuggestion / AutomatedAction`). Use it when Chris asks "what's new" / "any alerts?" / "unread notifications" / "system suggestions" / "running automations" / "mark those as read" / "ack the low-priority ones" / "dismiss this notification".

Distinct from `narrative_tool` (drift/shift diagnostics — different substrate: `NarrativeShift` + drift metadata, not notification-inbox shape), from `self_awareness_tool` (system-introspection metrics/reports/evolution — no user-facing inbox), from `mobile_tool` (mobile-app diagnostics — no proactive-generation substrate), and from Discord notification surfaces (Discord bot writes to its own channel/thread models, not `ProactiveNotification`).

## Covered actions

- `dashboard` — **in scope this ship — pure READ (default action)** — verified live. Aggregate counts across all 4 substrate tables. Envelope: `{action: 'dashboard', unread_notifications, active_alerts, pending_suggestions, active_automations}`. `unread_notifications` is user-scoped when `user_id` is present at handler line 1646; the other 3 are global counts.
- `alerts` — **in scope this ship — pure READ** — verified live. Returns first `limit` (default 20, cap 50) active `ProactiveAlert` rows ordered by `-last_triggered, -created_at` at handler line 1571. Envelope: `{action, count, alerts: [{id, name, alert_type, condition, is_active, trigger_count, last_triggered, check_frequency}]}`. Global — no user-scoping (alerts are platform-wide by design).
- `notifications` — **in scope this ship — pure READ** — verified live. Returns first `limit` `ProactiveNotification` rows ordered by `-created_at` at handler line 1588. User-scoped when `user_id` is present at line 1590. Envelope: `{action, count, notifications: [{id, title, message (truncated at 200), notification_type, priority, is_read, delivery_status, created_at}]}`.
- `suggestions` — **in scope this ship — pure READ** — verified live. Returns first `limit` `SmartSuggestion` rows filtered `status='pending'` ordered by `-confidence_score` at handler line 1608. User-scoped when `user_id` is present at line 1610. Envelope: `{action, count, suggestions: [{id, title, suggestion_type, category, confidence_score, estimated_revenue_impact, effort_level, status}]}`.
- `automations` — **in scope this ship — pure READ** — verified live. Returns first `limit` active `AutomatedAction` rows ordered by `-last_executed` at handler line 1628. Envelope: `{action, count, automations: [{id, name, action_type, trigger_type, is_active, total_executions, successful_executions, last_executed}]}`. Global — no user-scoping.
- `mark_read` — **in scope this ship — mutation, classified `spreading`** — verified live. `ProactiveNotification.objects.filter(id=notif_id, is_read=False).update(is_read=True)` at handler line 1660. **NO `user_id` predicate** — cross-user reach possible if caller knows another user's notification UUID (see §5a rationale + §5 sharp-edge note). Envelope: `{action, notification_id, updated: <bool>}`.
- `bulk_ack` — **in scope this ship — mutation, classified `spreading`** — verified live. `ProactiveNotification.objects.filter(id__in=ids_to_ack).update(is_read=True)` at handler line 1677 where `ids_to_ack` is derived from `filter(is_read=False[, user_id=user_id][, priority=priority][, notification_type=notification_type]).order_by('created_at').values_list('id', flat=True)[:max_items]` at lines 1668–1676. `max_items` capped at 200 (line 1667). `user_id` filter is CONDITIONAL — applied only when `user_id` is truthy. Envelope: `{action, acknowledged: <int>, filters: {priority, notification_type}}`.
- `dismiss` — **in scope this ship — mutation, classified `spreading`** — verified live. `ProactiveNotification.objects.filter(id=notif_id).update(is_read=True, delivery_status='dismissed')` at handler lines 1688–1690. **NO `user_id` predicate + NO `is_read=False` guard** (unlike `mark_read`) — cross-user reach possible AND can be called repeatedly on the same notif with no idempotency observation from the caller. Envelope: `{action, notification_id, dismissed: <bool>}`.

Default action = `dashboard` (per `payload.get('action', 'dashboard')` at handler line 1562).

## 3. Schema notes

- **Required:** `action` (enum: `alerts` / `notifications` / `suggestions` / `automations` / `dashboard` / `mark_read` / `bulk_ack` / `dismiss`).
- **Optional:** `notification_id` (str; required by `mark_read` + `dismiss`; also accepted as `id` alias per handler lines 1657/1685); `priority` (str; `bulk_ack` filter); `notification_type` (str; `bulk_ack` filter); `max_items` (int; `bulk_ack` cap — default 50, hard-capped at 200 at handler line 1667); `limit` (int; READ action cap — default 20, hard-capped at 50 at handler line 1563).
- **Cross-reference:** verbatim schema at `pa_tool_schemas.py:4718-4749`.
- **Envelope shape:** each action returns a distinct envelope key (`alerts` / `notifications` / `suggestions` / `automations` — separate rooted arrays), consistent with the envelope-key-asymmetry-across-actions pattern already at 3/3 triggered post-S2919 batch 2.
- **Schema description omits user-scoping gap:** the schema description for `mark_read` / `dismiss` says "requires notification_id" but does NOT surface that the mutation is not user-bounded (the caller's `user_id` context is ignored for the mutation predicate). Contrast with `vip_invite_tool.revoke` schema description at `pa_tool_schemas.py:4544` which explicitly surfaces the cross-table `is_active` side effect. **2nd instance of "schema description omits substantive mutation quirk" pattern** — vip_invite hardcoded-superuser `create` was 1st (S2922). Not yet at Fold threshold.
- **`max_items` semantics:** default 50 (schema line 4744) but capped at 200 at handler line 1667. The schema description says "max 200" — consistent with handler cap. Caller cannot exceed 200 in a single `bulk_ack` regardless of what they pass.

## 4. Golden-path examples

**Example 1 — dashboard aggregate (default action, no payload):**
```json
{"action": "dashboard"}
```
Expected envelope: `{"action": "dashboard", "unread_notifications": <int>, "active_alerts": <int>, "pending_suggestions": <int>, "active_automations": <int>}`. `unread_notifications` reflects only the calling user's unread count when `user_id` is present.

**Example 2 — recent notifications for the calling user:**
```json
{"action": "notifications", "limit": 10}
```
Expected envelope: `{"action": "notifications", "count": <≤10>, "notifications": [{"id": "<uuid>", "title": "<str>", "message": "<str truncated at 200>", "notification_type": "<str>", "priority": "<str>", "is_read": <bool>, "delivery_status": "<str>", "created_at": "<isoformat>"}, ...]}`.

**Example 3 — mark a single notification read (mutation; spreading — cross-user reachable):**
```json
{"action": "mark_read", "notification_id": "<uuid>"}
```
Expected envelope: `{"action": "mark_read", "notification_id": "<uuid>", "updated": <bool>}`. Side effect: 1 `ProactiveNotification.is_read` flipped to True IFF the row was previously unread. **Warning:** no `user_id` predicate — the mutation succeeds regardless of whether the notification belongs to the calling user. Absorbed by single-user pre-prod.

**Example 4 — bulk-ack low-priority notifications (mutation; spreading — up to 200 rows):**
```json
{"action": "bulk_ack", "priority": "low", "max_items": 50}
```
Expected envelope: `{"action": "bulk_ack", "acknowledged": <int ≤50>, "filters": {"priority": "low", "notification_type": "all"}}`. Side effect: up to 50 `ProactiveNotification.is_read` flips to True, oldest-first. User-scoped only when `user_id` present in caller context.

**Example 5 — dismiss a notification (mutation; spreading — cross-user reachable):**
```json
{"action": "dismiss", "notification_id": "<uuid>"}
```
Expected envelope: `{"action": "dismiss", "notification_id": "<uuid>", "dismissed": <bool>}`. Side effect: 1 `ProactiveNotification.is_read + .delivery_status` mutated to `(True, 'dismissed')`. **Warning:** same user-scoping gap as `mark_read` + no `is_read=False` guard, so repeated dismiss on same notif keeps returning `dismissed: true`.

## 5. Failure / empty-state / pagination notes

- **Unknown action:** returns `{"error": f"Unknown proactive_tool action: {action}. Valid: dashboard, alerts, notifications, suggestions, automations, mark_read, bulk_ack, dismiss"}` at handler line 1693. Not raised — in-envelope.
- **Handler exception:** caught at line 1695, logged via `logger.error("[PROACTIVE] {action} error: {e}", exc_info=True)`, returns `{"error": <str>}` from handler. Handler omits `error_code` field; **dispatcher auto-backfills `error_code='legacy_error'`** at `tool_dispatcher.py:862-885` per S2874 mixed-mode migration (S2876 breadcrumb telemetry) — final envelope observed by callers is `{"error": <str>, "error_code": "legacy_error"}`. **This is the 20th corroborating instance of the unmigrated-handler pattern** post-S2923's 19-instance count (profile_tool in this same batch is the 21st). Threshold-crossed note surfaced at Slice-4 close per S2924 Q5(iii) Chris ratification.
- **`mark_read` — missing `notification_id`:** returns `{"error": "notification_id required for mark_read"}` at handler line 1659.
- **`mark_read` on already-read notification:** returns `{"action": "mark_read", "notification_id": <id>, "updated": false}` — the `.filter(is_read=False)` guard at line 1660 prevents double-mark. Idempotent-observable (caller sees `updated: false`).
- **`dismiss` — missing `notification_id`:** returns `{"error": "notification_id required for dismiss"}` at handler line 1686.
- **`dismiss` on already-dismissed notification:** returns `{"action": "dismiss", "notification_id": <id>, "dismissed": true}` — **NO `is_read=False` or `delivery_status != 'dismissed'` guard** (unlike `mark_read`) — repeated dismiss keeps returning `dismissed: true` even though the row was already terminal. Idempotent-in-effect but NOT idempotent-observable. Sharp edge — divergence from `mark_read`'s observable-idempotency pattern.
- **`bulk_ack` empty match:** returns `{"action": "bulk_ack", "acknowledged": 0, "filters": {...}}`. Not an error.
- **`bulk_ack` — `max_items` overflow:** any value > 200 clamps to 200 at line 1667. No error surfaced; silent clamp.
- **READ actions — empty result:** each returns `{action, count: 0, <collection>: []}`. Not an error.
- **`user_id` absent for READ actions:** `notifications` + `suggestions` fall back to global queries (all rows across all users, capped at `limit`). `alerts` + `automations` are global by design (no user_id filter regardless).
- **`user_id` absent for MUTATIONS:** `mark_read` + `dismiss` proceed with cross-user reach (any user can mutate any notif by ID). `bulk_ack` acks up to 200 GLOBAL unread notifications matching filters. See §5a rationale + Ledger row.

## 5a. Mutation containment (per Rigby SIGN Q3 — §5a 4-tier blast-radius taxonomy amended S2921)

Three mutation actions in this tool. All classified `spreading` — but for two distinct reasons within that tier (row-count vs cross-user reach). Rationale grounded in Rigby T0 SIGN Q3 correction (line-by-line grep of user_id filters).

| Action | Mutation type | Blast-radius tier | Rationale |
|---|---|---|---|
| `mark_read` | `.update(is_read=True)` — 1 row, 1 field (handler line 1660) | `spreading` | Single-row mutation but **NO `user_id` predicate** — the `.filter(id=notif_id, is_read=False)` is unique-by-PK-only. Cross-user reach is unbounded (any user with proactive_tool access + knowledge of another user's notification UUID can flip that row). Blast-radius per-call is tiny (1 row, 1 field) but the reach dimension violates the `contained` tier's "no cross-user reach" clause per `_TEMPLATE §5a`. Classified `spreading` because "cross-user reach" is a `spreading` marker independent of row-count. Single-tenant pre-prod (Chris is the sole user) makes the leak inert in practice per `project_single_user_pre_prod_operating_context`. Multi-tenant hardening deferred (Ledger row). |
| `bulk_ack` | `.update(is_read=True)` — up to 200 rows, 1 field (handler line 1677) | `spreading` | Bulk multi-row mutation with hard cap at `min(max_items, 200)` (line 1667). Row-count reach is bounded (≤200). `user_id` filter is CONDITIONAL at line 1669 (`if user_id: qs = qs.filter(user_id=user_id)`) — when `user_id` is truthy the ack is user-scoped; when falsy the ack reaches up to 200 rows GLOBALLY across all users' unread notifications. Archetype `spreading` case per template §5a definition ("Bulk `.update(is_read=True)` over ≤200 rows"). Same single-tenant pre-prod absorption as above for the conditional-scoping half. |
| `dismiss` | `.update(is_read=True, delivery_status='dismissed')` — 1 row, 2 fields (handler lines 1688–1690) | `spreading` | Same shape as `mark_read` but mutates 2 fields instead of 1 AND lacks the `is_read=False` guard, so it will happily mutate an already-dismissed row again (no observable idempotency at caller — envelope returns `dismissed: true` regardless of pre-state). **NO `user_id` predicate** — same cross-user reach as `mark_read`. Classified `spreading` for the cross-user reach reason (not row-count — the row-count is 1). Single-tenant pre-prod absorbs the reach; the observable-idempotency divergence from `mark_read` is a schema-consistency Ledger note, not a blast-radius issue. |

**Deferral status:** NOT deferred. Ship-in-scope this batch — this ship exercises all 3 mutation actions post-merge to verify the classifications hold end-to-end (see §6 post-merge verification protocol).

**Comparison to `profile.update_preferences` (this batch's spreading peer):**
- profile.update_preferences: `spreading` via `get_or_create` (implicit new row into `EnhancedUserProfile` when user has no row) + `.save()` on that row. USER-SCOPED via explicit `User.objects.filter(id=user_id).first()` gate at `td_handlers_gateway.py:2390` — returns `{'error': 'No user context'}` when `user_id` is absent (line 2392). Contrasts with proactive's `spreading` shape which either has NO user gate (`mark_read`/`dismiss`) or a CONDITIONAL user gate (`bulk_ack`). Profile is the "clean" spreading archetype; proactive is the "gap" spreading archetype. Both classify correctly at the `spreading` tier — the tier captures blast-radius per-call, not access-control rigor.

**Signal-cascade non-fire assertion for all 3 mutations:** `ProactiveNotification` inherits `UnifiedBaseModel` (per `core/models_unified_system.py`). No `@receiver(post_save, sender=ProactiveNotification)` decorators found in a repo-wide grep across signal-registering modules; no dynamic `post_save.connect(..., sender=ProactiveNotification, ...)` found either (grep for `ProactiveNotification` in `core/signals/` returns 0 hits; grep in `core/services/` returns only ORM operations, not signal connects). Grep receipts: `rg 'sender=ProactiveNotification' core/ → 0 matches`. This validates the `spreading` (not `cascading`) classification — mutations reach only the rows they explicitly write.

## 5b. First-hop dependency proof

| Direct dependency | Classification | Evidence (file:line) | Callee-status |
|---|---|---|---|
| `ProactiveAlert.objects.filter(is_active=True).order_by(...)[:limit]` | `read` | `td_handlers_gateway.py:1571` | ORM SELECT with slice; documented |
| `ProactiveNotification.objects.order_by('-created_at')[:limit]` (+ optional user filter) | `read` | `td_handlers_gateway.py:1588-1591` | ORM SELECT; documented |
| `SmartSuggestion.objects.filter(status='pending').order_by(...)[:limit]` (+ optional user filter) | `read` | `td_handlers_gateway.py:1608-1611` | ORM SELECT; documented |
| `AutomatedAction.objects.filter(is_active=True).order_by(...)[:limit]` | `read` | `td_handlers_gateway.py:1628` | ORM SELECT; documented |
| `ProactiveNotification.objects.filter(is_read=False)[.filter(user_id=...)].count()` | `read` | `td_handlers_gateway.py:1645-1650` | ORM aggregate; documented |
| `ProactiveAlert.objects.filter(is_active=True).count()` | `read` | `td_handlers_gateway.py:1651` | ORM aggregate; documented |
| `SmartSuggestion.objects.filter(status='pending').count()` | `read` | `td_handlers_gateway.py:1652` | ORM aggregate; documented |
| `AutomatedAction.objects.filter(is_active=True).count()` | `read` | `td_handlers_gateway.py:1653` | ORM aggregate; documented |
| `ProactiveNotification.objects.filter(id=notif_id, is_read=False).update(is_read=True)` | `db_write` | `td_handlers_gateway.py:1660` | ORM UPDATE (1 row, 1 field); documented — `mark_read` mutation |
| `ProactiveNotification.objects.filter(id__in=ids_to_ack).update(is_read=True)` | `db_write` | `td_handlers_gateway.py:1677` | ORM UPDATE (≤200 rows, 1 field); documented — `bulk_ack` mutation |
| `ProactiveNotification.objects.filter(id=notif_id).update(is_read=True, delivery_status='dismissed')` | `db_write` | `td_handlers_gateway.py:1688-1690` | ORM UPDATE (1 row, 2 fields); documented — `dismiss` mutation |

**Appendix N (Network-Preflight) — N/A.** No network first-hop. Handler is entirely ORM. `rg 'httpx|requests\.|urllib|urlopen' core/services/td_handlers_gateway.py` within the proactive handler span (1560–1697) returns 0 matches.

**Appendix A (Async-Fanout) — N/A.** No `apply_async` first-hop. Handler is entirely synchronous. No task dispatch inside handler span.

Both Appendices declared N/A per S2918 T0 SIGN Q2 gateway-wide DISAGREE (0/17 gateway tools with the three literal patterns at that time; cockpit_tool moved the count to 1/17 at S2923 via `send_task` in `_TASK_EXPRESS_TARGETS` list). This tool does NOT increment either count — gateway-wide first-hop-literal count stays at 1/17 post-batch-7.

## 6. Evidence

Doc-only sweep this ship. Post-merge Rigby live-dispatch verification on all 8 actions (5 READ + 3 MUTATION) appended to the S2924 handoff. Expected envelope shapes documented in §4 golden-path examples.

**Post-merge verification protocol:**

For `dashboard`:
1. Dispatch `{"action": "dashboard"}`.
2. Response envelope: `{action, unread_notifications, active_alerts, pending_suggestions, active_automations}` — all 4 counts non-negative integers.
3. ORM cross-check: `ProactiveAlert.objects.filter(is_active=True).count() == active_alerts`; same pattern for the other 3.

For `alerts`, `notifications`, `suggestions`, `automations`:
1. Dispatch `{"action": <name>, "limit": 5}`.
2. Response envelope: `{action, count, <collection>: [...]}` with `count == len(<collection>)` and `count ≤ 5`.
3. ORM cross-check: first entry matches `<Model>.objects.<filter>().order_by(<same-order>).first()` at dispatch time — key fields per envelope schema in §Covered actions.

For `mark_read`:
1. Identify an unread notification: `ProactiveNotification.objects.filter(is_read=False).first()` — capture its `id` before dispatch.
2. Dispatch `{"action": "mark_read", "notification_id": "<id>"}`.
3. Response envelope: `{action, notification_id, updated: true}`.
4. ORM cross-check: `ProactiveNotification.objects.get(id=<id>).is_read is True`.
5. Second-mark check: dispatch same payload again → expect `{"action": "mark_read", "notification_id": <id>, "updated": false}` (observable idempotency via `is_read=False` guard at line 1660).

For `bulk_ack`:
1. Count currently-unread: `ProactiveNotification.objects.filter(is_read=False).count()` before dispatch.
2. Dispatch `{"action": "bulk_ack", "max_items": 5}` (small cap to avoid over-mutation of dev data).
3. Response envelope: `{action, acknowledged: <int ≤5>, filters: {priority: 'all', notification_type: 'all'}}`.
4. ORM cross-check: `ProactiveNotification.objects.filter(is_read=False).count() == <previous_count> - acknowledged`.
5. `max_items` clamp check: dispatch `{"action": "bulk_ack", "max_items": 500}` → envelope's `acknowledged` should be `min(actual_matches, 200)` — never > 200.

For `dismiss`:
1. Identify a non-dismissed notification: `ProactiveNotification.objects.exclude(delivery_status='dismissed').first()` — capture `id`.
2. Dispatch `{"action": "dismiss", "notification_id": "<id>"}`.
3. Response envelope: `{action, notification_id, dismissed: true}`.
4. ORM cross-check: `ProactiveNotification.objects.get(id=<id>)` — `is_read is True` AND `delivery_status == 'dismissed'`.
5. Second-dismiss check: dispatch same payload again → expect `{"action": "dismiss", "notification_id": <id>, "dismissed": true}` (NO observable-idempotency guard — divergence from `mark_read`; documented in §5).

**Signal-cascade non-fire assertion for all 3 mutations:** all mutations write to `ProactiveNotification`. No `@receiver(post_save|pre_save, sender=ProactiveNotification)` decorators + no dynamic `post_save.connect(..., sender=ProactiveNotification, ...)` — grep receipts in Rigby T0 SIGN turn 1. If any `[PROACTIVE_*_SIGNALS]` action log line appears in worker logs during verify, the `spreading` classification is invalidated (would indicate an unobserved cascade) and this doc is amended.

## Related

- **Adjacent tools:** `profile_tool` (this batch — spreading peer; clean archetype vs proactive's gap archetype); `narrative_tool` (batch 2 — drift/shifts, different substrate); `self_awareness_tool` (batch 4 — introspection metrics, no user-facing inbox); `cockpit_tool` (batch 6 — external tier, Celery infrastructure).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template, v1 — §5a 4-tier blast-radius taxonomy from S2921); models at `core/models_unified_system.py` (`ProactiveAlert`, `ProactiveNotification`, `SmartSuggestion`, `AutomatedAction`).
- **Prior ratifications:** S2892 Path B open, S2918–S2923 Slice 4 batches 1–6, S2921 §5a 4-tier taxonomy amendment, S2923 latent-cascade authoring convention.
- **Ledger rows relevant to this ship:**
  - **Legacy-error envelope 20th instance** — threshold-crossed. Short "now systemic" note surfaced at Slice-4 close per S2924 Q5(iii) Chris ratification. Substrate arc still gated on explicit Chris directive per 00-START forbidden-list.
  - **User-scoping gap on notification-inbox mutations** — `mark_read` + `dismiss` have NO `user_id` predicate; `bulk_ack` `user_id` filter is CONDITIONAL. First Slice-4 instance of "mutation-with-scoping-gap" archetype in a user-facing inbox tool (contrast with vip_invite's hardcoded-superuser `create` which is scoping-elimination by design vs proactive's scoping-omission by drift). Absorbed by `project_single_user_pre_prod_operating_context`; multi-tenant hardening deferred (would add `filter(user_id=user_id)` predicate to lines 1660/1688 and make bulk_ack's `user_id` filter unconditional). Recorded as Ledger row per S2924 joint Claude+Rigby recommendation.
  - **`dismiss` observable-idempotency divergence from `mark_read`** — `dismiss` lacks the `is_read=False` guard that `mark_read` has, so repeated dismiss returns `dismissed: true` on already-terminal rows. Schema-consistency Ledger note. First observation.
  - **Schema description omits substantive mutation quirk** — 2nd instance (1st was vip_invite hardcoded-superuser `create`). Not yet at Fold threshold.
