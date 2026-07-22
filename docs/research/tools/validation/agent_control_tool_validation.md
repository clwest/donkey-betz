# `agent_control_tool` — Validation Report (S2892)

**Tool:** `agent_control_tool`
**Schema:** `core/services/pa_tool_schemas.py:2972`
**Handler:** `core/services/td_handlers_ops.py:1981` (`_handle_agent_control`)
**Register site:** `core/services/tool_dispatcher.py:529`
**Session:** S2892 (Path B systematic sweep — Slice 1 batch 1 of `td_handlers_ops`)
**HEAD at validation:** `81502903d`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (every action in the schema `action` enum exercised live).
**Rigby SIGN:** S2892 T1 SIGN AGREE-WITH-EDITS; canary-agent pre-check + try/finally cleanup discipline both accepted before mutation dispatch.

---

## 1. Purpose / when-to-use

Manage the blocked/enabled state of registered agents. Single source of truth — writes here propagate to all dispatch paths (`tasks.py`, `agent_router.py`, `tool_dispatcher.py`). Use to: (a) inspect current block state (`list`), (b) block an agent with a reason + optional TTL (`block`), (c) re-enable an agent (`unblock`), (d) view most-recently-changed entries (`audit_log`).

Distinct from `agent_introspection_tool` (which enumerates the AGENT_MAP registry itself) — `agent_control_tool` mutates the operational block/enable state.

## Covered actions

- `list` — **in scope this ship** — verified live (see §6.1). Returns every `AgentControlEntry` row sorted by `updated_at` DESC plus a `blocked_now` frozenset (TTL-aware).
- `block` — **in scope this ship** — verified live. `update_or_create` on `AgentControlEntry` by `agent_name` (unique index). Auto-populates `blocked_at` on first `enabled→blocked` transition (preserves historical first-block timestamp).
- `unblock` — **in scope this ship** — verified live. `.filter(status='blocked').update(status='enabled', reason=...)` — no-op if agent isn't currently blocked.
- `audit_log` — **in scope this ship** — verified live. **BEHAVIOR MISMATCH with schema description** (see §3 and §5).

## 3. Schema notes

- **Required:** `action` (enum: `list, block, unblock, audit_log`).
- **`agent_name`** — schema declares string; handler raises `ValueError("agent_name required for block action")` for `block` and `unblock`. Same enforcement for the `agent_name` param in the `agent_control_tool` schema definition is soft (no `required` array at the property level).
- **`ttl_hours`** — integer, optional. When set alongside `blocked_at`, `get_blocked_names()` auto-transitions to `enabled` on next read after elapsed > ttl_hours. Verified at code level (`core/models_unified_system.py:135-151`); TTL-expiry side effect not exercised live this session.
- **`blocked_by`** — string, defaults to `'rigby'` at the handler. Truncated at 100 chars.
- **`limit`** — integer, applies only to `audit_log`. Default 20, hard-capped at 50 (`min(int(payload.get('limit', 20)), 50)`).

**Schema description lint (per S2795 F5):** the description says the audit_log action "returns recent changes" and reason field is "stored for audit trail." Handler behavior does NOT match — see §5.

## 4. Golden-path examples

**Inspect current block state:**

```
agent_control_tool  action=list
```

**Block an agent with reason + 1-hour TTL:**

```
agent_control_tool  action=block  agent_name=SomeAgent  reason="Rigby: rate-limited by upstream"  ttl_hours=1  blocked_by=rigby
```

**Unblock:**

```
agent_control_tool  action=unblock  agent_name=SomeAgent  reason="Upstream restored"
```

**View most-recently-changed entries:**

```
agent_control_tool  action=audit_log  limit=5
```

## 5. Failure / empty-state / pagination notes

- **`audit_log` is misnamed** — the action returns `AgentControlEntry.objects.all().order_by('-updated_at')[:limit]` — i.e., current state per agent sorted by last-updated. `AgentControlEntry` is `update_or_create` keyed on `agent_name` (unique index), so block→unblock overwrites the row: **no historical trail is preserved**. Verified live: after Rigby's S2892 mutation sequence (block ValidationCheckAgent → verify → unblock ValidationCheckAgent), the `audit_log` output showed only the current `enabled` state — the intermediate `blocked` row was gone. Schema description implies append-only history that does not exist. **Ledger candidate** (see §Related).
- **`block` for non-existent agent** — handler does NOT validate `agent_name` against the AGENT_MAP registry. Blocks are persisted regardless. Rigby's pre-SIGN raised this: could persist a control row that proves handler works but not agent-registry integration. Verified at code level (`_handle_agent_control` lines 2020-2049); no registry check present.
- **Empty state (no rows):** `list` returns `blocked_now: [], total_entries: 0, entries: []`. `audit_log` returns `count: 0, entries: []`. Both fail-soft.
- **`unblock` when not blocked** — returns `was_blocked: false, success: true`. Idempotent.
- **No pagination** on `list`. `audit_log` supports `limit` only (no offset).

## 6. Evidence

### 6.1 Observed runs — this ship

Rigby's live dispatches at S2892 T1 (2026-07-22, HEAD `81502903d`, pin `pa-373cf02ba2344b13`):

**`list` (11ms):**

```json
{
  "action": "list",
  "blocked_now": [],
  "total_entries": 1,
  "entries": [
    {"agent_name": "CodeGeneratorAgent", "status": "enabled",
     "reason": "S1247 audit lane I: unblocked for local execution; ...",
     "blocked_at": "2026-06-12T23:41:57.370771+00:00", "blocked_by": "system",
     "ttl_hours": null, "updated_at": "2026-06-28T00:50:21.750202+00:00"}
  ]
}
```

**`block` (11ms) — ValidationCheckAgent, ttl_hours=1:**

```json
{"action": "block", "agent_name": "ValidationCheckAgent", "status": "blocked",
 "reason": "S2892 sweep smoke test — validation batch 1", "ttl_hours": 1,
 "blocked_by": "rigby", "created": true, "success": true}
```

**`list` after block (3ms):** `blocked_now: ["ValidationCheckAgent"]`, both entries returned. Confirms `blocked_now` reflects the new block immediately.

**`audit_log` limit=5 (3ms) between block+unblock:** returned the ValidationCheckAgent `blocked` row + CodeGeneratorAgent — confirmed 2 rows total.

**`unblock` (3ms):**

```json
{"action": "unblock", "agent_name": "ValidationCheckAgent", "status": "enabled",
 "was_blocked": true, "success": true}
```

**`list` after unblock (4ms):** `blocked_now: []` — pre-flight state restored.

**`audit_log` limit=5 after unblock (1ms):** ValidationCheckAgent row now shows `status: enabled, reason: "S2892 sweep smoke test cleanup"` — the earlier `blocked` state was overwritten (not appended). **This is the audit-log misnomer evidence.**

**ORM cross-check (Claude, independent of Rigby):**

```
AgentControlEntry.objects.get(agent_name='ValidationCheckAgent')
→ status='enabled', reason='S2892 sweep smoke test cleanup',
  blocked_at=2026-07-22 22:14:15.735493+00:00 (preserved — original block timestamp),
  updated_at=2026-07-22 22:14:15.738615+00:00
AgentControlEntry.get_blocked_names() = frozenset() → ValidationCheckAgent no longer blocked ✓
```

### 6.2 Runtime-not-executed — this ship

- **TTL expiry side effect** (`get_blocked_names` auto-transition from `blocked` → `enabled` after elapsed > ttl_hours) — not exercised (would require waiting 1 hour or manipulating timestamps).
- **Registry-integration validation** on `block` — handler doesn't check agent_name against AGENT_MAP; would need a non-registered name test.
- **`limit > 50` cap** — not exercised.

---

## Related

- **S2795 gap map:** `docs/audits/PA_TOOLS_GAP_MAP_S2795.md`.
- **S2892 handoff:** `docs/handoffs/SESSION_2892_PA_TOOLS_SWEEP_SLICE_1_BATCH_1.md` (this session).
- **Ledger candidates from this ship (route to Rigby Tool Gap Ledger deliverable `5c84e75a-…`):**
  1. `agent_control_tool.audit_log` is misnamed — returns current state per agent, not append-only history. Options: (a) rename to `recent` + update description, or (b) implement `AgentControlEventLog` model with append-only rows fed by `save()` signal.
  2. `agent_control_tool.block` doesn't validate `agent_name` against AGENT_MAP — silent-persist risk. Optional soft-check: emit warning if `agent_name not in AGENT_MAP`.
- **Related tools:** `agent_introspection_tool` (registry inventory; read-only companion to control state), `governor_tool` (per-agent execution budget controls — orthogonal).
