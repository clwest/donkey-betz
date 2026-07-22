# `ops_digest_tool` — Validation Report (S2893)

**Tool:** `ops_digest_tool`
**Schema:** `core/services/pa_tool_schemas.py:4371`
**Handler:** `core/services/td_handlers_ops.py:5471` (`_handle_ops_digest`)
**Register site:** `core/services/tool_dispatcher.py:539`
**Session:** S2893 (Path B systematic sweep — Slice 1 batch 2 of `td_handlers_ops`)
**HEAD at validation:** `387ac953e`
**Ship shape:** Doc-only (S2796 shape). Regression tests deferred.
**Category upgrade target:** `untested` → `validated_full` (every action in the schema `action` enum exercised live).
**Rigby SIGN:** S2893 T1 SIGN AGREE-clean.

---

## 1. Purpose / when-to-use

Rigby-narratable ops digest — summarizes autopilot status, blocked agents, activity counts (agent runs / celery tasks / task failures / top failures) over a configurable window, and can post the result into a conversation as a visible message. Use when Chris asks "what happened in the last hour?" or when a scheduled digest posts into an ops thread.

Distinct from `heartbeat_history_tool` (raw HeartBeat table read) and `status_snapshot_tool` (broad 12-section instantaneous snapshot) — `ops_digest_tool` produces a narrative-shape rollup with markdown formatting.

## Covered actions

- `generate` — **in scope this ship** — verified live (see §6.1). Builds digest object with `timestamp`, `window`, `deploy_sha`, `autopilot` sub-object, `blocked_agents` array, `activity` counts, `top_failures` array, `degraded_fields` array, and pre-rendered `markdown` string. **Design gap surfaced:** `autopilot.last_cycle` was 15 days stale but not flagged in `degraded_fields`; digest surfaces the timestamp raw without a staleness heuristic. Ledger candidate #2.
- `post` — **in scope this ship** — verified live to scratch conversation `pa-ee24cc40acaa4694`. Generates digest + writes it into the target conversation. Returns `conversation_id`, `posted_at`, and the full digest object (same shape as `.generate`).

## 3. Schema notes

- **Required:** `action` (enum: `generate, post`).
- **Conditional required:** `conversation_id` required for `post` action; schema declares it as optional string. Marginal Ledger entry candidate — mirrors the S2892/S2893 pattern of handler-required-but-schema-optional args.
- **Optional:** `window` (enum: `10m, 1h, 6h, 24h`, default `1h`).
- **Schema description lint:** clean — enumerates both actions and their arg requirements.

## 4. Golden-path examples

**One-hour narratable rollup:**

```
ops_digest_tool  action=generate  window=1h
```

**Post daily-shape digest into a specific conversation:**

```
ops_digest_tool  action=post  conversation_id=pa-<pin>  window=24h
```

**Short-window pulse (last 10 minutes):**

```
ops_digest_tool  action=generate  window=10m
```

## 5. Failure / empty-state / pagination notes

- **No pagination** — digest is a fixed-shape object regardless of window.
- **`degraded_fields` array** — the digest self-reports which internal probes degraded. Observed live: `["top_failures"]` when the top-failures aggregation could not be computed. This is a good pattern — but see §6.1 finding on missed staleness heuristics.
- **`activity` counts** are windowed to the `window` param — `agent_runs`, `celery_tasks`, `task_failures` all scoped consistently.
- **`.post` writes a user-visible message** into the target conversation. Do not target operational threads with test-shape digests. Use a scratch pin per S2893 SIGN discipline.
- **`autopilot.last_cycle` staleness is NOT flagged** as a degraded field even when weeks stale — see §6.1 finding.

## 5a. Mutation containment (per Rigby SIGN zoom-out #1)

- **Mutating actions:** `post` only (writes ChatMessage row to target conversation).
- **Containment protocol applied this ship:** `post` was targeted to `pa-ee24cc40acaa4694`, a scratch conversation minted via `session_tool.create_fresh` explicitly for this canary. SIGN thread (`pa-7a595cac8cc04bf8`) was not polluted. Post is idempotent per timestamp (rerunning creates a second message; not deduped).
- **Rollback:** none — posted digest messages persist in the target conversation. Cleanup is manual conversation deletion or ignored (scratch pins are noise-tolerant).

## 6. Evidence

### 6.1 Observed runs — this ship

Rigby's live dispatches at S2893 T1 (2026-07-22, HEAD `387ac953e`, pin `pa-7a595cac8cc04bf8`):

**`generate` (77ms, window=1h):**

```json
{"action": "generate",
 "digest": {
   "timestamp": "2026-07-22T22:40:02.087739+00:00",
   "window": "1h",
   "deploy_sha": "387ac953eff2",
   "autopilot": {
     "status": "running",
     "last_cycle": "2026-07-07T17:54:27.028462+00:00",
     "total_cycles": 7,
     "blocks_24h": 0},
   "blocked_agents": [],
   "activity": {"agent_runs": 3, "celery_tasks": 169, "task_failures": 0},
   "top_failures": [],
   "degraded_fields": ["top_failures"],
   "markdown": "## Ops Digest — 2026-07-22 22:40 UTC\n**SHA:** `387ac953eff2` | **Window:** 1h\n\n**Autopilot:** running (last cycle: 2026-07-07T17:54:27Z) | cycles: 7 | blocks 24h: 0\n\n**Blocked agents:** none\n\n**Activity (1h):** 3 agent runs, 169 tasks, 0 failures\n\n**Top failures:** none\n"
 }}
```

**Finding (a) — missing staleness heuristic on `autopilot.last_cycle`:** The digest surfaces `last_cycle: 2026-07-07T17:54:27Z` — 15 days before the digest timestamp — but does not add "autopilot_stale" or similar to `degraded_fields`. The narrative markdown reads "**Autopilot:** running" with the stale timestamp inline, which understates the health signal. **Design gap:** digest needs a staleness threshold (e.g. `>24h` or `>48h` since `last_cycle`) with a `degraded_fields` entry + a markdown badge ("⚠️ stale" or similar). Ledger candidate #2 for S2893.

**Finding (b) — `degraded_fields=["top_failures"]` implies the top-failures aggregation could not be computed** but the digest does not explain why. Not a defect, but a UX gap — a self-degraded field should carry a one-line reason.

**`post` (60ms, conversation_id=pa-ee24cc40acaa4694, window=1h):**

```json
{"action": "post",
 "conversation_id": "pa-ee24cc40acaa4694",
 "posted_at": "2026-07-22T22:40:06.943124+00:00",
 "digest": { /* same shape as .generate above */ }}
```

Post succeeded; digest message visible in the scratch conversation. Same content as the `.generate` output.

### 6.2 Runtime-not-executed — this ship

- **Windows other than `1h`** — `10m`, `6h`, `24h` not exercised. Would confirm activity count scaling.
- **`.post` to a real ops conversation** — deliberately avoided; scratch pin used.
- **`.generate` with autopilot in a healthy `last_cycle` state** — could not exercise (system was actually stale). Would confirm the `degraded_fields` array is empty when everything is fresh.
- **`.generate` with actual blocked_agents / top_failures populated** — not exercised (both empty on the live system).

---

## Related

- **Ledger candidates surfaced this ship** (routed to Ledger at close):
  1. Missing staleness heuristic on `autopilot.last_cycle` — should flag in `degraded_fields` when stale beyond threshold.
  2. `degraded_fields` entries should carry one-line reason strings.
  3. Schema `conversation_id` declared optional but handler-required for `.post` action.
- **S2893 handoff:** `docs/handoffs/SESSION_2893_PA_TOOLS_SWEEP_SLICE_1_BATCH_2.md`.
- **Related tools:** `heartbeat_history_tool` (raw HeartBeat rows), `status_snapshot_tool` (broad 12-section snapshot), `autopilot_tool` (deferred to Slice 1.5 — governs the `autopilot.last_cycle` value this digest surfaces).
