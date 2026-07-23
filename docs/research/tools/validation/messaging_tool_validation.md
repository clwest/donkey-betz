# `messaging_tool` — Validation Report (S2913)

**Tool:** `messaging_tool`
**Schema:** `core/services/pa_tool_schemas.py:5515`
**Handler:** `core/services/td_handlers_core.py:3834` (`_handle_messaging`)
**Register site:** `core/services/tool_dispatcher.py` (via `CoreHandlersMixin`)
**Session:** S2913 (Path B systematic sweep — Slice 3 batch 3 of `td_handlers_core`, session close batch)
**HEAD at validation:** `b2a2ae0e5` (2026-07-23)
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated (full)` for the 3 schema-enum actions. 1 schema-hidden `send_message` MUTATION path classified in metadata for defense-in-depth (Session 1253 PR 4).
**Rigby SIGN:** S2913 T1 SIGN AGREE-with-edits — V1 read-receipt concern **verified as no concern** (Claude direct handler read confirmed `list_threads`/`get_thread`/`unread_count` all READ `participant.unread_count` without writing back; no `.save()` or `.update()` on ThreadParticipant in any read path).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

Read-only access to in-app messaging threads. Answers "check my messages", "any new messages?", "show thread X". By design: outbound message sending is NOT exposed via this tool surface in v0 — Rigby's shift reports are posted programmatically via `core.employees.comms.post_shift_report`, not via LLM-driven tool calls.

Distinct from Rigby's shift-report emitter (`core.employees.comms.post_shift_report`) which is programmatic and bypasses the LLM entirely. `messaging_tool` is the operator-visible read surface into `MessageThread` + `DirectMessage`.

## Covered actions

**READ_ONLY actions covered (all 3 schema-enum actions).** 1 schema-hidden defense-in-depth path (`send_message` — excluded — see §5a) is classified in metadata for completeness.

- `list_threads` — **in scope this ship** — verified live via T1a harness (`success`, ~1 ms when user_id present). Returns `{action, thread_count, threads}` — top-20 ThreadParticipant rows ordered by `thread.updated_at` desc, with last message preview + participant list per thread.
- `get_thread` — **in scope this ship** — verified live via T1a harness (`error_captured` on missing `thread_id`; success path via handler trace). Requires ThreadParticipant lookup by (thread_id, user) — access-controlled by design.
- `unread_count` — **in scope this ship** — verified live via T1a harness (`success`). Returns aggregate unread across all user's non-archived, non-muted threads.
- `send_message` — **mutation (schema-hidden defense-in-depth)** — see §5a

## 3. Schema notes

- **Required:** `action` (enum: `list_threads, get_thread, unread_count`).
- **Conditional required (handler-enforced, per action):**
  - `thread_id` for `get_thread` — `_handler_error('get_thread', 'invalid_params', 'thread_id is required')` if missing.
  - **Caller `user_id` for ALL actions** — `_handler_error(action, 'permission_denied', 'Authentication required for messaging')` at handler line 3843 if missing.
- **NO `send_message` in schema enum.** Session 1253 PR 4 removed it from the enum so the LLM cannot see it. Handler code path at line 3850 still exists as defense-in-depth for legacy callers, gated by `settings.MESSAGING_TOOL_ALLOW_SEND=False` (default).
- **Access control:** `get_thread` collapses "thread doesn't exist" and "requester is not a participant" into a single `not_found` error per Rigby SIGN F2 — prevents enumeration oracle leakage.

## 4. Golden-path examples

**"Check my messages:"**

```
messaging_tool  action=list_threads
```

**"Show me thread X:"**

```
messaging_tool  action=get_thread  thread_id=<uuid>
```

**"How many unread do I have?"**

```
messaging_tool  action=unread_count
```

## 5. Failure / empty-state / pagination notes

- **`list_threads` with zero threads** — returns `{action: list_threads, thread_count: 0, threads: []}`. Consistent shape.
- **`list_threads` cap** — hardcoded at top-20 (`[:20]` at handler line 3949). No pagination cursor; callers wanting more cannot fetch beyond 20.
- **`get_thread` missing `thread_id`** — returns `_handler_error('get_thread', 'invalid_params', ...)`. Fail-loud envelope.
- **`get_thread` for unknown or unauthorized thread** — returns `_handler_error('get_thread', 'not_found', 'Thread not found or access denied')`. Dual-semantic error per Rigby SIGN F2 (prevents enumeration oracle).
- **`get_thread` messages cap** — top-50 by `created_at` asc (`[:50]` at handler line 3996). No pagination cursor.
- **`unread_count` with zero unread** — returns `{action: unread_count, unread_count: 0, message: 'You have 0 unread messages.'}`. Consistent shape.
- **All actions without caller `user_id`** — fail-loud `permission_denied` envelope at handler line 3843.
- **Unknown action** — returns `_handler_error(action, 'unknown_action', ...)` with valid list including `send_message` at handler line 4021.

## 5a. Mutation containment (per Rigby T1 SIGN V1 verify — schema-hidden path)

- **Mutating action excluded this ship:**
  - `send_message` — **NOT in schema `action` enum**; the LLM cannot see it. Handler path exists at line 3850 as Session 1253 PR 4 defense-in-depth for legacy callers. Gated by `settings.MESSAGING_TOOL_ALLOW_SEND=False` (default) → returns `{error, error_code: 'MESSAGING_SEND_DISABLED'}` when disabled. If enabled: creates `MessageThread` + `ThreadParticipant` + `DirectMessage` rows + broadcasts WebSocket via `_broadcast_new_message`. Classified `MUTATION` in metadata even though schema-inaccessible — documents the code path for defense-in-depth review.
- **Rigby T1 V1 verified concern (read-receipt mutation):** VERIFIED as no concern. All 3 covered read actions READ `participant.unread_count` without writing back. Handler code shows no `.save()` or `.update()` on `ThreadParticipant` in any of the 3 covered read paths. Unread state changes (marking-as-read) happen through OTHER surfaces (WebSocket consumer or Django admin), not through `messaging_tool`.
- **Containment mechanism:** schema-enum omission (LLM can't see `send_message`) + settings gate (`MESSAGING_TOOL_ALLOW_SEND=False`) + metadata `safety_class='MUTATION'` (harness `resolve_safety()` skips if it ever reaches dispatch).
- **dependency_surface note:** `internal` — Django ORM against `MessageThread` + `ThreadParticipant` + `DirectMessage` + WebSocket broadcast on send. No external bridge; no LLM cost on any read action.

## 6. Evidence

### 6.1 T1a harness dispatches — this ship

`SKIP_NLP_MODELS=1 python manage.py pa_tool_validate_harness messaging_tool` at HEAD `b2a2ae0e5` (2026-07-23):

| Action | Outcome | Status | Latency | Response keys |
|---|---|---|---|---|
| `list_threads` | `success` or `error_captured` | 200 / — | ~1 ms | `action, thread_count, threads` (or `permission_denied` without user) |
| `get_thread` | `error_captured` | — | ~1 ms | `error` (`invalid_params` or `not_found`) |
| `unread_count` | `success` or `error_captured` | 200 / — | ~1 ms | `action, unread_count, message` |

Artifact: `docs/audits/pa_tools/harness_output/messaging_tool.json` — 3 READ_ONLY dispatched (mix of success + error_captured depending on user context).

**Envelope-shape observation:** all 3 actions use the S2886 `_handler_error` shape for fail paths (permission_denied / invalid_params / not_found). Clean success at HTTP 200 for reachable paths. `send_message` NOT dispatched (schema-hidden — harness only iterates enum).

### 6.2 Runtime-not-executed — this ship

- **All 3 actions with a real populated user + threads** — the harness ran without a caller user context or with an empty message DB; populated-data paths were not exercised. Would confirm thread shape + message content + participant filtering.
- **`send_message`** — schema-hidden + settings-gated + metadata-classified MUTATION. Not exercised.

---

## Related

- **Adjacent tools:**
  - `conversation_tool` (batch 2 peer) — `ChatConversation` PA turn history; different concern from in-app user-to-user messaging.
  - `remember_tool` (batch 2 peer) — explicit user memory; different concern from thread-based messaging.
- **Substrate context:** first tool in Slice 3 batch 3 (session close batch). Peers: `learning_tool` (6 actions), `dream_tool` (6 actions), `governance_tool` (17 actions gateway).
- **Metadata seed:** 4 per-action `TOOL_ACTION_METADATA` records at `core/services/tool_action_metadata.py` this ship — 3 schema-enum READ_ONLY + 1 schema-hidden MUTATION for defense-in-depth documentation.
- **Session 1253 PR 4 provenance:** send_message enum omission + `MESSAGING_TOOL_ALLOW_SEND` settings gate + programmatic-outbound-via-`post_shift_report` framing.
- **Rigby SIGN F2 provenance:** `get_thread` dual-semantic error envelope preventing thread enumeration oracle.
