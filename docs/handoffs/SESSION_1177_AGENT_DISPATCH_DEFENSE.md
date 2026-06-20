# Session 1177 — Agent dispatch defense (F1 + F3 root causes closed)

**Status:** Closed. Two real bugs fixed and merged to main. Item A (failed-banner visual) verified end-to-end. Scope B follow-up investigated and skipped (turned out moot — see below).
**Date:** 2026-06-20
**Driving question:** "Continue the agent dispatch / follow-up wake stress testing — pick deferred items from Session 1176."
**Prior session handoffs:**
- [SESSION_1176_AGENT_DISPATCH_RECON_CLOSE.md](./SESSION_1176_AGENT_DISPATCH_RECON_CLOSE.md) — recon + 3 findings filed
- [SESSION_1175_FOLLOWUP_WAKE_CLOSE.md](./SESSION_1175_FOLLOWUP_WAKE_CLOSE.md) — the feature this session stress-tested

## TL;DR

Three Session 1176 deferred items picked up; three PRs merged:

| Item | PR | SHA | Outcome |
|---|---|---|---|
| **A.** Visual confirmation of FAILED-status banner | — | — | Verified end-to-end. F4/F4b hypotheses falsified — Session 1175's vertical slice handles both success and failure branches fully. |
| **B.** F1 root cause — `deliverable_tool update` silent fallback | [#2342](https://github.com/clwest/donkey-betz-platform/pull/2342) | `e9967bc8` | LLM tool-call args parse failures now produce typed `TOOL_ARGS_JSON_MALFORMED` envelope. Handler never invoked on malformed args. |
| **C.** F3 root cause — EditorAgent non-determinism | [#2343](https://github.com/clwest/donkey-betz-platform/pull/2343) | `75993feb` | Was actually dispatcher gather opacity. C1 surfaces `content_provenance` in AgentResult; C2 adds opt-in `strict_content_required` flag. |
| **B'.** Per-handler arg validation (defense in depth) | — | — | Investigated, found `_resolve_deliverable` + per-action `ValueError` raises already defend `deliverable_tool.update`/`create`/`append`/`detail`/`delete`/`export_pdf`. Skipped as moot. |

## What landed (in detail)

### Item A — failed-banner visual confirmation

Used the manual-mutation pattern: dispatched a clean PA-originated `ResearchAgent` task, let it complete naturally, then mutated `status` to `failed` via Django shell `.update()` (which bypasses `agent.completed` signal), then fired `schedule_followup`.

First attempt → no banner. Bisect localized the issue to the browser WS state: the Command Center hadn't connected to the new `pa-9b82bcc72e1945ce` conversation yet (Session 1177 successor of Session 1176's `pa-58c916edf96044cc`). After `Cmd+Shift+R` to force a fresh WS connect, the channel broadcast persisted a `ChatConversation` row (id=577) and emitted the banner WS event end-to-end. Banner rendered with `status=failed` + the error message; chat bubble appeared with "Background completion: Agent ResearchAgent failed (execution 754b6760-…) — Forced failure for Session 1177 visual banner test…".

**Falsified hypotheses:**
- **F4** — AgentCompletionBanner UI filters status=failed. Falsified — UI renders failed status fine when WS is connected.
- **F4b** — `schedule_followup`'s immediate-fire path lacks ChatConversation persistence. Falsified — reading `_handle_schedule_followup` at `td_handlers_agents.py:4577` showed it calls the same `fire_agent_followup_subscriptions` helper as the signal-driven path. One canonical broadcast → consumer handles persistence + banner emit symmetrically.

**Carry-forward diagnostic:** WS broadcasts to empty groups (no connected consumers) vanish silently — by design in Channels. If "where's the banner?" comes up again, first check WS connection state on the right conversation before deeper bisect.

### Item B — F1 root cause (PR #2342)

Identified `unified_pa_entrypoint.py:1521`:
```python
try:
    arguments = json.loads(fn.get('arguments', '{}'))
except (json.JSONDecodeError, TypeError):
    arguments = {}    # silent swallow
```

When the LLM's tool-call args JSON gets truncated mid-stream (long content payload hits the model's output token budget), `json.loads` raises and the empty-dict fallback flowed into `_handle_deliverable_direct`. The handler defaulted `action` to `'list'` (per Session 1077's GPT-5.2 misroute compat), so Rigby's intended `update` returned a list of deliverables and the write was lost without any caller-visible signal.

**Fix:**
- New module-level helper `_build_tool_args_malformed_envelope` with envelope shape ratified by Rigby this session
- Catch path now logs WARNING with `tool_name + args_len + parse_err + tail`, builds the typed envelope, feeds it back to the LLM via `tool_result_inputs`, records `TOOL_ARGS_JSON_MALFORMED` in `tool_runs`, and **never invokes the tool handler** on malformed args
- 6-case regression test (`test_pa_tool_args_malformed.py`) covers truncated JSON, meta fields, retry_hint shape for tool/non-tool names, short args, empty args

**Other `json.loads(...arguments...)` sites surveyed** (none on the same path):
- `views_image_tools.py:1124`, `assistant/base.py:184`, `personal_ai_assistant_enhanced.py:1316` — raise loudly or different paths
- `unified_pa_entrypoint.py:1746` and `:1952` — output truncation / response sanitization, unrelated to args-parsing

### Item C — F3 root cause (PR #2343)

Re-reading the code, **F3 wasn't an EditorAgent bug**. EditorAgent at `editor_agent.py:259-272` correctly fails loud on empty content (per `feedback_editor_fail_loud`). The non-determinism came from `core/services/editor_dispatch_helpers.gather_workspace_content_for_editor` (Sessions 1090/1092/1093), which silently injected recent workspace deliverables as `context['content']` when the caller didn't pass any. Workspace state changed between Session 1176 Run 1 (21:31) and Run 2 (21:37) — Cell 2 deliverables landed in the gap, so Run 1's gather found nothing → agent fail-loud, Run 2's gather scored a match → agent edited an unrelated deliverable.

Architecture per `feedback_editor_fail_loud` is correct (dispatcher recovers, agent fails loud). The gap was that recovery was **invisible to callers**.

**Fix (C1 + C2 in one PR per Rigby's ratification):**
- **C1** — `build_content_provenance` helper returning typed envelope: `{mode, source_deliverable_id, source_title, score, score_reason, gather_window_minutes, [warning]}`. Modes: `caller_provided` / `gathered_workspace_deliverable` / `task_text_fallback` / `none`. Both dispatcher paths (`tool_dispatcher._handle_agent_tool` + `conversation_action_dispatcher._dispatch_to_agent`) compute provenance and stash at `context['_dispatch_metadata']['content_provenance']`. EditorAgent surfaces it in `AgentResult.data['dispatch_metadata']` on both success and fail-loud return paths.
- **C2** — opt-in `strict_content_required=True` flag in context. When set, dispatcher skips gather entirely and lets the agent fail-loud. Default `False` everywhere — no breaking production changes. Test harnesses and QA cells can opt in to detect their own caller bugs.
- 9-case regression test (`test_editor_dispatch_provenance.py`) pins all four modes, the bonus `caller_content_overridden` warning, and the `CONTENT_PROVENANCE_MODES` contract surface.

### Scope B' (skipped — investigation finding)

Per-handler arg validation was originally framed in PR #2342 as defense-in-depth. Investigation showed `_resolve_deliverable` at `td_handlers_agents.py:1644` and the per-action `ValueError` raises already defend the surface:

| Action | Validation site |
|---|---|
| `update` | `_resolve_deliverable` raises `"id or title required for update action"` (line 1656); also raises if no updatable fields (line 2050) |
| `create` | `"title and content are required for create action"` (line 1836) |
| `append`, `detail`, `delete`, `export_pdf` | All use `_resolve_deliverable` → same `id`/`title` validation |

These `ValueError`s bubble up to `tool_dispatcher.py:814` and become `ToolResult(ok=False, error_code=TOOL_EXCEPTION, error_message=str(e))` — the LLM sees the clear error message. The only silent-fallback path that EXISTED was the JSON parse swallow that PR #2342 closed. B' would have added marginal value (converting `TOOL_EXCEPTION` to typed envelopes like `TOOL_ARGS_MISSING_REQUIRED_FIELD`) but didn't address a real failure mode. Skipped intentionally.

## Operational artifacts

- **Conversations:**
  - `pa-58c916edf96044cc` (Session 1174-1176) — retired earlier
  - `pa-9b82bcc72e1945ce` (Session 1177) — actively used; still healthy at session close; carry into Session 1178
- **Live test execution this session:** `754b6760-c97d-4ae0-9b46-9feaf717d820` (ResearchAgent → manually mutated to `failed`) — yielded ChatConversation row id=577 and the visual banner observation
- **Tracking deliverable from Session 1176:** `61247479-1976-4ba8-bc8a-ea67f66ead45` (Local QA workspace) — Session 1177 didn't write to it; findings are in the PRs and this handoff instead
- **Memory:** No new memory added this session beyond `feedback_deliverable_tool_use_append_for_large_payloads` from Session 1176 (which the F1 fix in PR #2342 closes the root cause for)

## How to continue in Session 1178

Three viable directions:

1. **Pick up Session 1175's deferred open queue** — conv-ID divergence recon, banner artifact-pointer enrichment (wire `artifact_pointers` from `fire_agent_followup_subscriptions` payload as click-through links in the banner UI), Phase 2 c1 auto-wake (every PA-originated dispatch creates an implicit subscription).
2. **Stress-test more of the PA tool catalogue** — pick a few high-value tools (gateway_tool, ops_tool actions Rigby flagged, governance_tool) and run the same "find half-wired paths" pattern that surfaced F1/F3.
3. **EditorAgent observability follow-up (C3)** — ops dashboard surface "X% of EditorAgent calls used dispatcher gather" + per-call provenance review. C1 just shipped the data; C3 turns it into operator visibility.

Chris explicitly flagged at Session 1177 close: "check back in with Rigby on where we are working with the Agents and what's next on the list." Rigby has agent-side context she may have queued during this session.
