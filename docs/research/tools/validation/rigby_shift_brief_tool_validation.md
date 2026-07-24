# `rigby_shift_brief_tool` — Validation Report (S2937)

**Tool:** `rigby_shift_brief_tool`
**Schema:** `core/services/pa_tool_schemas.py:4373` (1-action enum + 2 optional params)
**Handler:** `core/services/td_handlers_rigby_shift_brief.py:22` (`_handle_rigby_shift_brief`)
**Register site:** `core/services/tool_dispatcher.py:561`
**Session:** S2937 (Slice 7 batch 1 — trio with `spider_data_aggregation_tool` + `zoom_out_tool`)
**HEAD at validation:** `416931160` (2026-07-24)
**Ship shape:** Doc-only (S2796 shape). Post-merge live-dispatch verify per PLAYBOOK-7.4.4.
**Category upgrade target:** `untested` → `validated_full`
**Rigby SIGN:** S2937 T0 SIGN AGREE (tool-grounded — 8 tool_runs against 4 handler files; verified single-action pure-read surface + §5c consistency).
**Template variant:** sweep
**Template version:** v1

---

## 1. Purpose / when-to-use

`rigby_shift_brief_tool` is Rigby's **operator-shift pulse** for Chris at the start of a session — a one-minute structured snapshot bundling ops_digest, cockpit worker_health + queue_lengths, session health, audit findings, and recent activity into a 6-section response: top priority, platform health, active risks, what changed, what NOT to work on, suggested next action. Use it when Chris asks "what's happening right now?", "shift brief please", "give me a status check", or when Rigby is opening a session and wants a compact rollup instead of running each subsystem probe separately.

Distinct from `recent_activity_tool` (raw 6-subsystem snapshot without operator framing); from `morning_brief` workflow (heavier narrative-shape content workflow, not operational status); from `ops_tool` (per-subsystem SLO / staleness reads, not bundled). This tool is the "compact operator-facing brief" — narrative-shaped, one-call, always live.

## Covered actions

Enumerating every action in the schema `action` enum. **1 action, LIVE-VERIFIED at S2937.**

- `generate` — **in scope this ship — verified live (4083ms, RED traffic-light snapshot).** Default (and only) action. Calls `core.services.rigby_shift_brief.build_shift_brief(user_id, conversation_id, window)`. Envelope: `{ok, summary_text, traffic_light, sections{top_priority, platform_health, active_risks, what_changed, what_not_to_work_on, next_action}, metadata{runtime_ms, degraded_fields, tools_called, truncated, char_count, generated_at, window, conversation_id}, tool, action}` — see §6.1 for verbatim capture.
- **default (no `action` param)** — verified via handler code inspection (`td_handlers_rigby_shift_brief.py:32`). Defaults to `generate` per `p.get("action", "generate")`.
- **invalid action** — verified via handler code inspection (`td_handlers_rigby_shift_brief.py:34-41`). Returns in-envelope error `{"ok": False, "tool": "rigby_shift_brief_tool", "error": "Unknown action <x>. Supported: generate."}`. Non-raising (`ok:false` envelope, no exception).

## 3. Schema notes

- **Required:** `action` (enum: `generate` — only value).
- **Optional:** `conversation_id` (string — pinned conversation for the session health-check sub-section; falls back to `self._current_conversation_id` attribute on the dispatcher per handler line 44-46); `window` (enum: `10m`/`1h`/`6h`/`24h` — default `24h`, lookback for activity counts).
- **No `action` enum-value drift:** schema declares only `"generate"`; handler defaults to `"generate"`. Zero action-space drift.
- **conversation_id fallback chain (line 43-46):** payload `conversation_id` → `self._current_conversation_id` (dispatcher-injected) → `None`. Handler passes whatever it resolves into `build_shift_brief`; the shift-brief service handles the null case.
- **window default:** `"24h"` when caller omits (line 47). Schema description matches.
- **No `dry_run` affordance:** pure-read tool — none needed.
- **No auth gate:** module docstring line 7-8 explicitly notes "No human notification surface. No agent dispatch. No state mutation. No feature flag — this tool is always live." Verified against handler code.

## 4. Golden-path examples

**Example 1 — Default shift brief (24h window):**
```json
{"action": "generate"}
```
→ `{"tool":"rigby_shift_brief_tool", "action":"generate", "generated_at":"<iso>", "window":"24h", "sections":{"top_priority":{...}, "platform_health":{...}, "active_risks":{...}, "what_changed":{...}, "what_not_to_work_on":{...}, "suggested_next_action":{...}}}` — 6-section payload per `build_shift_brief` contract. Exact per-section fields depend on `build_shift_brief`'s current v1 shape (not in scope for this handler-boundary doc).

**Example 2 — Tight 1-hour window:**
```json
{"action": "generate", "window": "1h"}
```
→ Same envelope shape; activity counts narrowed to 1-hour lookback.

**Example 3 — Pin to a specific conversation for session health:**
```json
{"action": "generate", "conversation_id": "pa-abc123"}
```
→ Same envelope shape; session health-check sub-section evaluated against `pa-abc123` instead of the current PA conversation.

## 5. Failure / empty-state / pagination notes

- **Empty state (no activity in window):** `build_shift_brief` returns its 6-section envelope regardless of activity level — sections with no data return their empty-payload shape (specific shape depends on the service, not this handler). Handler-boundary contract: envelope always has `tool` + `action` keys + service payload merged in.
- **Invalid action:** returns `{"ok": False, "tool": "rigby_shift_brief_tool", "error": "Unknown action <x>. Supported: generate."}`. Non-raising in-envelope error. Divergence from siblings that `raise ValueError` — matches the recent_activity_tool pattern (documented S2935) rather than the execution_history_tool / learning_patterns_tool pattern. Not a bug, just a divergence class already tracked by Ledger #5 systemic consistency lint candidate.
- **Missing `conversation_id`:** falls back to `self._current_conversation_id` on the dispatcher (handler line 45). If that's also None, `build_shift_brief` receives `conversation_id=None` and handles accordingly (session health-check sub-section may be sparse or omitted — dependent on service, not handler).
- **Invalid `window` value:** the schema enum-constraints `window` to `10m`/`1h`/`6h`/`24h`, but the handler does NOT validate — passes whatever string arrives to `build_shift_brief`. Service-side handling of unexpected `window` values is out of scope for this handler-boundary doc; enum drift observed but low risk (LLM/UI callers stay in-enum).
- **Pagination:** none. Single-call full snapshot.
- **Rate limits / retry:** none at handler layer.

## 5c. Contract ↔ Implementation Consistency (S2937 retro-fold; per Rigby zoom-out #4)

### 5c.1 Handler / module header claims match action reality

**Disposition: PARTIAL DRIFT.** Module docstring (line 1-9) accurately states single `generate` action, "Read-only", "No human notification surface. No agent dispatch. No state mutation. No feature flag — this tool is always live." Handler-boundary claims match. **However, schema description (line 4374-4383) drifts in two ways surfaced by live-verify at S2937 §6.1:**

1. **Section-name drift:** schema description says "6-section response: top priority, platform health, active risks, what changed, what NOT to work on, **suggested next action**", but the actual JSON key in `sections{}` is `next_action` — NOT `suggested_next_action`. Callers writing to schema description will not find the field they expect.
2. **Undocumented response fields:** schema description names 6 sub-sections but omits the top-level response fields the handler+service actually return: `ok`, `summary_text` (pre-formatted string aggregating the 6 sections), `traffic_light` (e.g., `"RED"`), `metadata{runtime_ms, degraded_fields, tools_called, truncated, char_count, generated_at, window, conversation_id}`. The `sections{}` sub-object is correctly named but its wrapping is not.

**Same schema-under-describes-handler drift class already tracked as Ledger #5 systemic detection lint (approaching third-instance promotion threshold at S2936 close per 00-START-NEXT-SESSION.md).** Sub-Ledger candidate for consolidation with the S2935 recent_activity_tool + surgical_moves_status_tool schema-realignment PR precedent — record-only this ship; potential same-batch fix pattern for future rigby_shift_brief schema tightening.

Ledger #39 (this ship, `td_handlers_rigby_work_queue.py` docstring drift) covers a peer instance of the same drift class in the sibling Slice 7 handler-read.

### 5c.2 Gating truth matches runtime behavior

**Disposition: PASS — no gate.** Module docstring line 8 explicitly states "always live." No settings flag, no env var, no feature toggle. §6 LIVE-VERIFY covers the always-live path (the only path).

### 5c.3 Shared handler-file coupling noted

**Disposition: PASS — dedicated handler.** `td_handlers_rigby_shift_brief.py` is a 56-line dedicated file with a single tool. No sibling tools share this module. No coupling to note.

## 6. Evidence

Live PA-dispatch evidence, S2937 T0 (HEAD `416931160`, 2026-07-24). Dispatched via `rigby_shift_brief_tool` handler at `td_handlers_rigby_shift_brief.py:22`. Envelope shape captured verbatim in §6.1.

### 6.1 `action=generate` (default `window=24h`) — LIVE at S2937 T0

Captured verbatim via Rigby dispatch, HEAD `416931160`, 2026-07-24 17:49 UTC. Runtime **4083ms** (dominated by 6 sub-tool calls: `ops_digest`, `worker_health`, `queue_lengths`, `audit_findings`, `recent_activity`, `flag_state`; 2 of 6 sub-tools degraded — `worker_health` + `queue_lengths`). Traffic light: **RED**.

Envelope (full JSON):
```json
{
  "ok": true,
  "summary_text": "Rigby Shift Brief — Fri 2026-07-24 17:49Z — RED\n[ Top priority ]\n  Stabilize platform before opening new work.\n[ Platform health ]\n  - 119 agent runs · 4062 celery tasks · 0 failures (24h).\n[ Active risks ]\n  - None — all clear.\n[ What changed ]\n  - 4062 celery tasks fired.\n  - 211 spider items (65 spiders).\n[ What NOT to work on ]\n  - Don't flip S1250 flags — dormant by design.\n  - Don't re-open closed audit findings without new evidence.\n[ Suggested next action ]\n  Investigate degraded sub-tools: worker_health, queue_lengths.\n-- built in 4075ms · 6 tools · 2 degraded",
  "traffic_light": "RED",
  "sections": {
    "top_priority": "Stabilize platform before opening new work.",
    "platform_health": ["119 agent runs · 4062 celery tasks · 0 failures (24h)."],
    "active_risks": ["None — all clear."],
    "what_changed": ["4062 celery tasks fired.", "211 spider items (65 spiders)."],
    "what_not_to_work_on": [
      "Don't flip S1250 flags — dormant by design.",
      "Don't re-open closed audit findings without new evidence."
    ],
    "next_action": "Investigate degraded sub-tools: worker_health, queue_lengths."
  },
  "metadata": {
    "runtime_ms": 4075,
    "degraded_fields": ["worker_health", "queue_lengths"],
    "tools_called": ["ops_digest", "worker_health", "queue_lengths", "audit_findings", "recent_activity", "flag_state"],
    "truncated": false,
    "char_count": 575,
    "generated_at": "2026-07-24T17:49:34.513112+00:00",
    "window": "24h",
    "conversation_id": null
  },
  "tool": "rigby_shift_brief_tool",
  "action": "generate"
}
```

**Observations locked at this HEAD:**
- 6 sub-tools fanned out; `worker_health` + `queue_lengths` degraded — an observability signal, not a Rigby-tool bug (upstream dependency degradation surfaced through `metadata.degraded_fields`).
- 24h activity: 119 agent runs / 4062 celery tasks / 0 failures / 211 spider items across 65 spiders.
- `summary_text` is a pre-formatted string aggregating all 6 sections (with an em-dash-separated footer showing runtime + sub-tool count + degraded count). Convenient for chat surfaces that want a single string rather than the structured `sections{}` sub-object.
- `traffic_light` value ("RED" here) is a top-level classification not documented in the schema description — a §5c.1 drift finding, see above.
- `sections.next_action` is a string (single suggested action), NOT the plural "actions" or a list. Schema description narrative ("suggested next action") maps here — but the key name is `next_action`, not `suggested_next_action`, per §5c.1 drift.

### 6.2 `action=generate window=1h`

Not exercised as a separate call this batch — handler line 47 confirms `window` passthrough with no handler-layer transformation. Envelope shape identical to §6.1; per-section counts narrow to 1h.

### 6.3 Default action (no `action` in payload)

Not exercised as a separate call — handler line 32 confirms default = `"generate"` via `p.get("action", "generate")`. Behavior identical to §6.1.

### 6.4 Invalid action gating

Not exercised via failing dispatch this batch. Handler line 34-41 confirms in-envelope error return `{"ok": False, "tool": ..., "error": ...}`. Non-raising — differs from execution_history_tool sibling class (which uses `raise ValueError`). Documented but not fixed — Ledger #5 consistency lint candidate approaches third-instance threshold across the sweep.

## Related

- **Adjacent tools (same Slice 7 batch 1):** `spider_data_aggregation_tool` (SpiderData group-by rollup — orthogonal subsystem), `zoom_out_tool` (governance ledger read — orthogonal subsystem). All 3 pure-read + no shared-module coupling.
- **Adjacent tools (heavier brief workflows):** `morning_brief` (workflow, not a PA tool — content-heavy narrative shape); `recent_activity_tool` (raw 6-subsystem snapshot without operator framing).
- **Substrate docs:** `docs/audits/pa_tools/substrate/_TEMPLATE_per_tool_validation.md` (T1b canonical template v1 + §5c retro-fold added S2937); `docs/audits/PA_TOOLS_GAP_MAP.md` (Slice 7 open = 9 untested; this doc + 2 siblings this batch → 6 remaining).
- **Prior ratifications:** S2892 Path B open; S2907 T0 Fold E; S2921 §5a taxonomy; S2928 Slice 5 CLOSE; S2936 Slice 6 CLOSE (bifurcated Option C shape precedent for batch 2); S2937 T1 Chris ratification (4-batch Slice 7 plan + template §5c retro-fold).
- **First-hop dependencies:** none — pure Python function call to `core.services.rigby_shift_brief.build_shift_brief`. §5b Appendix N/A not applicable.
- **Post-merge live-dispatch verification:** exercise `rigby_shift_brief_tool action=generate` after `make recycle-all` at merge; confirm 6-section envelope shape matches §6.1. Recorded in S2937 handoff.
