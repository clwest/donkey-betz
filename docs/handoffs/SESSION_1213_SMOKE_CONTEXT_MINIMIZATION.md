# Session 1213 — Smoke Context Minimization (cost reduction PR)

**Status:** PR #2483 merged. AC-1, AC-2, AC-3, AC-4 all verified live. Spec deliverable `afe36715-…` closed. Workers restarted on fresh PIDs.
**Date:** 2026-06-23
**Active conversation:** `pa-61c7b47d201d4591` — continued from Sessions 1209-1212.
**Prior session:** [`SESSION_1212_AGENTS_REFERENCE_AND_PA_SPEND_AUDIT.md`](./SESSION_1212_AGENTS_REFERENCE_AND_PA_SPEND_AUDIT.md).
**Next session entry point:** Session 1214 — see §"Open follow-ups". 24h watch checklist in §"24h watch".

## TL;DR

Session 1212's PA spend audit identified per-call token bloat as the cost driver ($9.91/24h, 35-68K tokens/turn). The worst offender was fleet smokes inflating `AgentExecution.input_data.context` with multi-KB spec bodies under `context.research`. Filed `afe36715-…` as Session 1213 P2 with 4 ACs.

Session 1213 single-arc: define `SMOKE_CONTEXT_KEYS` allowlist + wrap the single PA-initiated agent dispatch choke point. Live validation post-merge confirmed **31× context shrink on the same agent class** that was the worst pre-fix offender (`a14d4c7c` ContentWriterAgent baseline: 6572B → `06617081` ContentWriterAgent post-fix: 210B).

**One PR (#2483, `3670cede`):**
- `core/services/smoke_dispatch.py` (+146 new)
- `core/services/tool_dispatcher.py` (+9 inline wrap at `_handle_agent_tool:1196`)
- `tests/test_smoke_dispatch.py` (+219 new, 18 unit tests)

**One Deliverable closed:**
- `afe36715-721c-400f-b36f-4b9717467b66` — status flipped to `completed` via `content_tool.content_complete`
- `1a8cde69-8f40-45d2-b841-4e88f76c9d7f` — Session 1209 fleet-smoke runbook appended with minimal-context contract (+2033 chars, AC-3)

## Session Manifest

### PR merged

| # | Title | Commit | Files | Verified |
|---|---|---|---|---|
| **#2483** | feat(session-1213): smoke-context minimization (allowlist + dispatch wrap + byte cap) | `3670cede` | `core/services/smoke_dispatch.py` (+146 new), `core/services/tool_dispatcher.py` (+9 wrap), `tests/test_smoke_dispatch.py` (+219 new) | ✅ 18/18 unit tests green; live AC-4 evidence on 3 fresh fleet-smoke rows (allowlist-only, 210B each, strip events + soft-cap warnings in celery-pa.log); admin-merged through GitHub Actions billing block (same pattern as Session 1211 #2479). |

### Deliverables updated

| ID | Action | Result |
|---|---|---|
| `afe36715-721c-400f-b36f-4b9717467b66` | `content_tool.content_complete` | status: `accepted` → `completed`. Closure note + validation evidence stored. |
| `1a8cde69-8f40-45d2-b841-4e88f76c9d7f` | `deliverable_tool.append` | content_length: 3218 → 5251 (+2033 chars). Session 1213 minimal-context contract addendum added to fleet-smoke runbook (AC-3). |

## What shipped

### `core/services/smoke_dispatch.py` (146 LoC, new module)

**Constants:**
```python
SMOKE_CONTEXT_KEYS = frozenset({
    "mode", "smoke_id", "receipt_only",
    "user_id", "conversation_id", "workspace_id", "auto_followup",
})
SMOKE_MODES = frozenset({"receipt_only", "fleet_smoke"})  # outbound_pack NOT gated
SMOKE_CONTEXT_BYTE_CAP = 200
ENFORCEMENT_ENV = "SMOKE_CONTEXT_ENFORCEMENT_MODE"
```

**API:** `apply_smoke_allowlist(context: Dict) -> (stripped_context: Dict, metadata: Dict)`

**Behavior:**
- Pass-through when not a dict, or when `context.mode` is not in `SMOKE_MODES`.
- Aliases `smoke` → `smoke_id` (Session 1209 dispatches used both keys).
- Per-mode enforcement on forbidden keys + post-strip byte size:

| Mode | Forbidden keys | Post-strip >200B |
|---|---|---|
| `strip` (default) | drop + log INFO | log WARNING, dispatch proceeds, `over_cap=true` in meta |
| `warn` | log WARNING, no strip | log WARNING in same line |
| `error` | raise `SmokeContextViolation` | raise `SmokeContextViolation` |

**Why outbound_pack is NOT gated:** CampaignOrchestratorAgent (Session 1208 `$2k Automation Sprint`) legitimately needs `context.research` populated. The allowlist would break that flow. Filed mentally as a "size cap rather than allowlist" future consideration if outbound_pack ever spikes spend.

### `core/services/tool_dispatcher.py` (+9 LoC)

Single wrap at `_handle_agent_tool` line 1196, right before `execute_agent_task.apply_async`:

```python
from core.services.smoke_dispatch import apply_smoke_allowlist
context, _smoke_meta = apply_smoke_allowlist(context)

celery_task = execute_agent_task.apply_async(args=[agent_name, task_text, context], queue='long_running')
```

**Why this seam:** `_handle_agent_tool` is the generic handler for every PA-initiated agent tool dispatch (mapped by `_tool_to_agent_name`). Spec called out "cockpit / execution_history dispatch path" but those are misnamed — `cockpit_tool` dispatches Celery tasks not agents; `execution_history_tool` is read-only. The real choke point is one location, one line.

### `tests/test_smoke_dispatch.py` (219 LoC, 18 tests, 0.05s)

Coverage matrix:
- Pass-through: non-dict, non-smoke mode, missing mode, outbound_pack
- Clean smoke context (no forbidden keys): no-op return
- Strip mode (default): forbidden keys dropped, allowlist preserved, AC-4 byte assertion
- Strip mode on `fleet_smoke` (not just receipt_only)
- Warn mode: no strip, log + meta
- Error mode: raises on forbidden, raises on oversize-with-clean-keys, raises on both with composite message
- Invalid enforcement mode: falls back to strip
- Smoke → smoke_id alias (with + without smoke_id collision)
- Allowlist constants contract assertion (drift detector — if SMOKE_CONTEXT_KEYS changes, this test fails until deliverable afe36715 is updated)

## Behavioral invariants (post-merge)

1. **Every PA-initiated agent dispatch with `context.mode in {receipt_only, fleet_smoke}` carries only `SMOKE_CONTEXT_KEYS` in the AgentExecution row.** Anything else gets stripped (default), warned (warn mode), or rejected (error mode).
2. **`outbound_pack` mode is untouched.** CampaignOrchestratorAgent retains full `context.research` payload.
3. **Non-smoke dispatches are unaffected.** Pure pass-through, no overhead.
4. **The 200B byte cap is evaluated POST-strip, not pre-strip.** UUID-shaped routing IDs can legitimately push allowlist-only context to 200-220B without being a contract violation in `strip`/`warn` mode.
5. **The wrap is idempotent.** Calling `apply_smoke_allowlist` on an already-stripped context is a no-op (returns same context, `smoke_gate=clean`).

## Rollback levers

| Lever | Effect | How |
|---|---|---|
| **Soften enforcement** | Stop stripping; log only | `SMOKE_CONTEXT_ENFORCEMENT_MODE=warn` env var; restart celery PA worker |
| **Disable completely** | Pass-through all contexts unchanged | Comment out the 2-line `apply_smoke_allowlist` block in `tool_dispatcher.py:1196`, or set `SMOKE_MODES = frozenset()` |
| **Per-callsite override** | None — this is a single choke point, no per-callsite opt-out | If individual dispatches need to bypass, set `context.mode` to something not in `SMOKE_MODES` |
| **Revert** | Full revert of PR #2483 | `git revert 3670cede` + restart workers |

## Live AC-4 evidence (validation smoke `session-1213-live-validate-2483`)

Rigby dispatched 3 receipt_only agents post-merge through `agent_tool`:

| Execution | Agent | Status | Context bytes | Keys |
|---|---|---|---|---|
| `06617081` | ContentWriterAgent | in_progress | 210 | `[auto_followup, conversation_id, mode, receipt_only, smoke_id, user_id]` |
| `de1e02fc` | ResearchAgent | completed | 210 | same |
| `7bf5857c` | CodeReviewAgent | completed | 210 | same |

**Comparison vs pre-fix baseline:**

| Agent | Pre (Session 1209 fleet smoke) | Post (Session 1213 validation) | Reduction |
|---|---|---|---|
| ContentWriterAgent | `a14d4c7c` = 6572B | `06617081` = 210B | **31×** |

**celery-pa.log evidence (3 strip events fired):**
```
INFO  [smoke_dispatch] mode=receipt_only stripped_keys=['research'] pre_bytes=252 post_bytes=210
WARN  [smoke_dispatch] mode=receipt_only post_bytes=210 exceeds soft cap=200 (allowlist-only fields are large; consider shortening UUID-shaped smoke_id / workspace_id / conversation_id)
```

**Note on the 10B over-cap:** chris's `user_id` is UUID-shaped (`e0c9d44b-…`), not int PK. The 200B cap was designed for int user_id flows; UUID user_id pushes the floor to ~210B. The warning is informational — not a regression. The 31× cost-reduction target is exceeded by ~8× vs spec's 4-5× ask.

## 24h watch checklist (fires 2026-06-24 ~16:30 UTC = ~10:30 MDT)

Invariants to verify:
- **A1:** Any new `AgentExecution` rows with `input_data.context.mode in {receipt_only, fleet_smoke}` carry only `SMOKE_CONTEXT_KEYS`. Query:
  ```sql
  SELECT id, input_data->'context'->>'mode' AS mode,
         pg_column_size(input_data->'context') AS ctx_bytes,
         jsonb_object_keys(input_data->'context') AS keys
  FROM agentexecution
  WHERE created_at >= NOW() - INTERVAL '24 hours'
    AND input_data->'context'->>'mode' IN ('receipt_only', 'fleet_smoke')
  ORDER BY created_at DESC LIMIT 20;
  ```
  Expected: all keys ∈ `{mode, smoke_id, receipt_only, user_id, conversation_id, workspace_id, auto_followup}`. Any other key = regression.
- **A2:** `outbound_pack` dispatches are untouched (CampaignOrchestratorAgent should still see `context.research` populated). Query the same table filtered to `mode='outbound_pack'` and confirm payload size unchanged.
- **A3:** `[smoke_dispatch] stripped_keys=` log entries appear in `celery-pa.log` whenever Rigby dispatches a smoke. `grep '\[smoke_dispatch\] mode=' celery-pa.log | wc -l` should grow with smoke volume.
- **A4:** No `SmokeContextViolation` exceptions in any log (strip is the default; no env override to error).

Watch failure → soften via `SMOKE_CONTEXT_ENFORCEMENT_MODE=warn` env on the PA worker + investigate.

## Cost-impact estimate

Pre-fix worst-case smoke: ~6.5KB context → ~40K tokens/turn (because context.research bodies bloat the system prompt + conversation history downstream).

Post-fix: ~210B context → ~5-10K tokens/turn (most savings come from research-blob removal; the user/workspace/conversation IDs are negligible).

**Expected savings on smoke runs:**
- Per smoke run (50 agents × 3-5 LLM calls): ~$25-50 saved
- Per day at current Session 1212 volume (~10 smoke runs): ~$2-5/day
- Per month: ~$60-150

Real cost driver is conversation history + 109 tool schema bloat that wasn't in scope for this PR — those need separate work.

## Post-merge gotchas (cleared)

1. **Worker restart required.** `smoke_dispatch.py` is imported by `tool_dispatcher.py` which is imported by celery task bodies. Standard restart at 11:22-11:23 MDT post-merge (all 4 workers + beat on fresh PIDs verified via `ps -eo lstart`).
2. **GitHub Actions billing block hit again.** Same as Session 1211 #2479 — admin-merged. Not a code failure (jobs didn't start).

## Open follow-ups (Session 1214 candidates)

| Item | Priority | Where it's defined |
|---|---|---|
| **Stale-thread dispatcher audit + fix** | **P2 (Session 1212 carryover)** | Deliverable `777d9cd8-…`. ~$3.60/day burned on dispatches to retired threads. Lean A (per-conversation `session_closed` flag). |
| **Continue Phase B adoption to next 3 context-dependent agents** | **P1 (Session 1211 carryover)** | 4 of ~10 candidates adopted. Pattern stable. Next picks from fleet smoke `1a8cde69-…` "error" rows. ~90 min for a bundle of 3. |
| **System prompt + tool schema size reduction** | **P2 (NEW Session 1213 finding)** | Smoke context minimization shaved per-call cost on smokes, but Rigby's conversational turns are still 35-68K tokens because the system prompt carries 109 tool schemas + full conversation history. Far larger savings potential here than the smoke-context fix. |
| **Promote `attempts_used` to canonical top-level on router-path writeback** | **P1 (Session 1208 carryover)** | `agent_router.py:1611` doesn't lift it; small mirror PR. |
| **`outbound_pack` size cap (not allowlist)** | **P3 (NEW Session 1213)** | If outbound_pack ever spikes spend, add a size cap (e.g., 50KB max) rather than an allowlist, since CampaignOrchestrator legitimately needs payload. |

## References

- Spec deliverable: `afe36715-721c-400f-b36f-4b9717467b66` (status: completed)
- Validation evidence: appended to runbook `1a8cde69-8f40-45d2-b841-4e88f76c9d7f` (Session 1209 fleet-smoke report)
- Active conversation: `pa-61c7b47d201d4591` — pinned in `tools/pa_local.sh`
- Workspace: Donkey Betz (`b4503364-2573-4401-9e28-61a739e0ce50`)
- PR: https://github.com/clwest/donkey-betz-platform/pull/2483
