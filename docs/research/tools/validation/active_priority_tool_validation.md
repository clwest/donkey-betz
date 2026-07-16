# `active_priority_tool` — Validation Report (S2796)

**Tool:** `active_priority_tool`
**Schema:** `core/services/pa_tool_schemas.py:2774`
**Handler:** `core/services/td_handlers_ops.py:1730` (`_handle_active_priority`)
**Register site:** `core/services/tool_dispatcher.py:513`
**Session:** S2796 (Slice 1 of `td_handlers_ops` validation)
**HEAD at validation:** `0c38718b0`
**Ship shape:** Doc-only (per S2796 Chris directive "validation quickest"). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (per gap-map classifier)
**Rigby SIGN:** S2796 T1 SIGN-WITH-EDITS; 6-section template per Rigby Z3; evidence per Rigby Z1 edit A.

---

## 1. Purpose / when-to-use

`active_priority_tool` manages Rigby's active-priorities registry for priority-aware routing. Each active priority represents a current focus (e.g. "Platform hardening", "Newsletter Issue 2 ship"); beat tasks and autonomous dispatches check alignment against these priorities before running (PriorityRouter is the PR-2 substrate — `test_match` action is stubbed until it lands).

Use to answer "what am I working on right now?", to gate autonomous dispatches on current focus, or to preview whether a candidate agent+task would match Rigby's current priorities (once PR-2 delivers the router).

TTL bounds are enforced at the handler edge: minimum 10 minutes (anti-flap protection), maximum 7 days (anti-zombie protection), default 24 hours.

## Covered actions

All 6 schema-declared actions enumerated as a flat list for gap-map classifier. Per-action admission class inlined per Rigby SIGN Z1 edit A (F1).

- `list` — **in scope this ship** — verified live at S2796 T1 (see §Evidence). Returns currently-active priorities (auto-expires TTL); observed empty state `count: 0, priorities: [], matching_cache_summary: []`.
- `set` — runtime-not-executed. **Mutating action — regression test priority for follow-up PR.** Requires `name`; optional tags/whitelist/blacklist/description/priority_rank/ttl_hours/enable_keyword_match/owner.
- `update` — runtime-not-executed. **Mutating.** Requires `priority_id`.
- `archive` — runtime-not-executed. **Mutating.** Requires `priority_id`. Soft-delete (row preserved for audit).
- `test_match` — runtime-not-executed. **Stubbed until PR-2 delivers `PriorityRouter`** per schema description. Preview match decision for `(agent_name, task)`.
- `history` — runtime-not-executed. Full list including archived/expired (optional `limit`).

## 3. Schema notes

- **Required:** `action` (enum, 6 values).
- **Conditionally-required per action:**
  - `set` requires `name` (≤120 chars).
  - `update` / `archive` require `priority_id` (UUID).
  - `test_match` uses `agent_name` + `task`.
- **Optional params:**
  - `description` — free-form intent.
  - `tags` — array of strings. Primary automatic matching mechanism (matched against derived agent tags).
  - `agent_whitelist` — agents that ALWAYS match (highest precedence).
  - `agent_blacklist` — agents that NEVER match.
  - `enable_keyword_match` — bool; **off by default** per schema description ("keyword matching creates false positives, only enable when the tag list is explicitly narrow").
  - `priority_rank` — integer; lower = higher priority; default 100.
  - `owner` — enum-ish string (`rigby` / `chris` / `system`); default `rigby`.
  - `ttl_hours` — number (accepts floats); default 24. **Handler-enforced clamp `[10/60, 7*24]`** — 10 min minimum (anti-flap), 7 day maximum (anti-zombie). Clamp is documented in schema but the response shape when clamp fires is not verified this ship.
- **Schema description lint (per S2795 F5):** none flagged. Description ≥ 40 chars; action verbs mentioned in description.

## 4. Golden-path examples

**List current priorities (S2796 T1 usage):**

```
active_priority_tool action=list
# → {"count": N, "priorities": [...], "matching_cache_summary": [...]}
```

**Set a new priority (deferred — runtime-not-executed):**

```
active_priority_tool action=set \
  name="Platform hardening" \
  tags=["platform","ops","routing"] \
  ttl_hours=48 \
  priority_rank=50
```

**Preview match (deferred — stubbed until PR-2):**

```
active_priority_tool action=test_match \
  agent_name="AudioAgent" \
  task="Generate voiceover for newsletter"
```

## 5. Failure / empty-state / pagination notes

- **Empty state:** `list` with no active priorities returns `count: 0, priorities: [], matching_cache_summary: []` (verified live — see §6.1). Not a fail-loud shape; consumers must check `count` explicitly.
- **TTL clamp behavior:** handler enforces `[10/60, 7*24]` on `ttl_hours` per schema description. Response shape when clamp fires (does it echo the clamped value in `ttl_hours_clamped` or silently apply?) **not verified this ship** — flag as DOC-note follow-up.
- **`enable_keyword_match` default:** schema explicitly warns keyword matching creates false positives — off by default. Enable only when tag list is narrow. Consumer discipline required.
- **`test_match` stub behavior:** action is documented as stubbed until PR-2 delivers `PriorityRouter`. Live invocation before PR-2 is expected to return a placeholder-shape response. **Not verified this ship.**
- **Pagination:** `history` accepts `limit`; no offset param documented. Deferred.
- **Archive vs delete:** `archive` is soft-delete (row preserved for audit); no hard-delete surface exposed.

## 6. Evidence

### 6.1 Observed run — this ship

**S2796 T1 evidence-capture dispatch** (`bash tools/pa_local.sh` → Rigby `active_priority_tool action=list` invocation):

```json
{
  "action": "list",
  "count": 0,
  "priorities": [],
  "matching_cache_summary": []
}
```

**Response returned in 4ms** (from `Tool Runs (verbose)` block). Response fields verified: `action` echo, `count` integer, `priorities` array, `matching_cache_summary` array. Empty state is intact — no errors, no null-shape surprises. Consistent with S2796 open state (no active priorities set).

**Observation:** `matching_cache_summary` is empty in the observed empty state — behavior when priorities exist + cache has been warmed is **not verified this ship**; deferred to follow-up PR.

### 6.2 Runtime-not-executed — this ship

- `set` — mutating action; not exercised (would create test row + require cleanup).
- `update` — mutating; requires pre-existing priority_id.
- `archive` — mutating; requires pre-existing priority_id.
- `test_match` — stubbed until PR-2 `PriorityRouter` lands.
- `history` — not exercised.
- **TTL clamp response shape** — not exercised (would need to send `ttl_hours=0.05` and verify clamp behavior).

---

## Related

- **S2795 gap map:** `docs/audits/PA_TOOLS_GAP_MAP_S2795.md`.
- **S2796 zoom-out folds:** ledger rows 65-68.
- **PR-2 dependency:** `test_match` is stubbed until `PriorityRouter` substrate lands.
- **Related tools:** `ops_tool` (SRE reliability), `status_snapshot_tool` (broad dashboard), `diagnostics_tool` (per-component inventory).
- **Session 1086** — original tool introduction (initiative `2dcb79d7`).
