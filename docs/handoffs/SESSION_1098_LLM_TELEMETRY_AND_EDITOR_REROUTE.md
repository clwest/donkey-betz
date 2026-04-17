# Session 1098 — LLM telemetry wrapper + EditorAgent reroute + initiative_id routing

**Date:** 2026-04-17
**Conversation:** `pa-3c7ddc058db1` (ongoing since Session 1094)
**Theme:** Boardroom-dispatch-hang remediation (Rigby's 4-PR plan) + EditorAgent misroute
fixes (Fix A input-side, Fix B-minimal output-side)

## What shipped

Three PRs, stacked in order. Suggested merge order: `#1999 → #2000 → #2001`.

| PR | Title | Branch |
|----|-------|--------|
| [#1999](https://github.com/clwest/donkey-betz-platform/pull/1999) | `feat(llm): per-call telemetry + execution_id wrapper (Session 1098, PR #1 of 4)` | `feature/llm-telemetry-execid` |
| [#2000](https://github.com/clwest/donkey-betz-platform/pull/2000) | `feat(editor): reroute synthesis tasks to ContentWriterAgent (Session 1098 Fix A)` | `feature/editor-synthesis-reroute` |
| [#2001](https://github.com/clwest/donkey-betz-platform/pull/2001) | `feat(deliverable): thread initiative_id + atomic commit (Session 1098 Fix B-minimal)` | `feature/editor-initiative-routing` |

### PR #1999 — LLM telemetry wrapper + execution_id (Rigby's plan PR #1 of 4)

- New model `LLMCallEvent` (migration `0334_llmcallevent.py`). UUID `call_id`
  PK, `execution_id` as UUIDField (not FK) so telemetry survives cleanup-
  watchdog pruning. Indexed on `execution_id` / `provider` / `status`.
- New `core/services/llm_call_wrapper.py`:
  - `llm_call_span` sync context manager
  - `llm_call_async` for async callers (accepts sync or async `fn`)
  - `LLMCallCancelled` exception class (reserved for PR #3)
  - `CancelToken` dataclass (no-op in PR #1, wired in PR #3)
  - `_classify_error` → {timeout, rate_limit, auth, api_error, client_error, cancelled, unknown}
  - `_extract_usage` → OpenAI `prompt_tokens`, Anthropic `input_tokens`, dict
- Telemetry is best-effort: every ORM write is wrapped in
  `_save_event_safe()` so telemetry failures never mask LLM errors.
- **Proof-point rewire:** `core/agents/thinking_agent.py::_call_llm` now
  routes through `llm_call_async`. `core/agent_router.py` injects
  `context['execution_id']` before dispatching `agent.execute()`.
- **21 new tests** (16 pure-logic classify/extract + 5 sync span + 3 async); 12 adjacent tests (thinking/editor/base) confirmed no regression.
- **Model kwarg naming gotcha:** async wrapper uses `model_name=` (not
  `model=`) because it forwards `**kwargs` to the provider SDK which also
  takes `model=`. Sync context manager keeps `model=`. Documented in both
  docstrings.

### PR #2000 — EditorAgent synthesis reroute (Fix A, input-side misroute)

- New helper `core/services/editor_dispatch_helpers.reroute_synthesis_to_content_writer`
  - Conservative regex: synthesis VERB (`synthesiz|combine|merge|consolidat|integrat`) +
    source-target NOUN (`brief|analyses|report|sources|...`) within 60 chars.
  - Swaps `agent_name = 'ContentWriterAgent'` when all triggers hold.
  - Gathered workspace sources land in `context['research']` (ContentWriter's
    expected key).
  - Adds `routing_hint='synthesis_reroute_from_EditorAgent'` for audit.
- Wired into both dispatcher paths:
  - `core/services/tool_dispatcher.py::_handle_agent_tool`
  - `core/services/conversation_action_dispatcher.py::_dispatch_to_agent`
- Feature flag: `settings.EDITOR_SYNTHESIS_REROUTE_ENABLED` (default `True`).
- **19 new tests** (10 regex + 9 reroute decision) — Rigby's 4 scenarios
  plus feature-flag-off, non-editor passthrough, gathered-sources populate
  research, reroute-without-sources still swaps, context immutability.

### PR #2001 — initiative_id routing + atomic commit (Fix B-minimal)

- `core/agents/base_agent.py::_save_to_deliverable`: new optional
  `initiative_id` kwarg. Precedence: explicit kwarg → `_execution_context
  ['initiative_id']` → `metadata['initiative_id']` → `None`.
- `core/services/deliverable_factory.py::create_deliverable`:
  - Validates `initiative_id` exists before setting the FK. Invalid id →
    `WARNING` log + link dropped (row still creates in workspace bucket).
    Lookup failure caught; never blocks the write.
  - Wrapped `Deliverable.objects.create` in `@transaction.atomic` so
    post-save signal failures roll back cleanly.
- **8 new tests** (5 factory: valid/invalid/no-id/dedupe-survives/atomic-
  rollback; 3 plumbing: explicit kwarg > context > metadata).
- Closes ~80% of the "wrong deliverable stream" misroute class.
  Remaining 20% (mid-flight initiative promotion race) deferred to
  **B-full**, task #9.

## Migrations applied

- `core/migrations/0334_llmcallevent.py` — applied locally. Additive
  (new table + 3 indexes). Safe to deploy without downtime.

## Monitoring to watch post-merge

- **LLMCallEvent ingestion rate** — should climb as agents adopt wrapper.
  Start with ThinkingAgent only; subsequent agents land in PR #A2
  (Rigby's lint + remediation pass).
- **`LLMCallEvent.error_type='unknown'` spikes** — indicates a provider
  SDK shape the `_classify_error` regex missed. Add regex patterns as
  needed.
- **`[editor-reroute]` INFO log** — count of synthesis tasks rerouted
  from EditorAgent to ContentWriterAgent. Watch for spike (regex too
  aggressive) or silence (regex too conservative).
- **`[DeliverableFactory] initiative_id=... not found` WARNING** — stale
  initiative references from LLM-generated task text. Non-zero rate
  expected during initial rollout.
- **EditorAgent failure rate** — "No content provided" failures should
  drop materially once Fix A deploys.

## Queued follow-ups

### PR #A2 — CI lint forbidding direct SDK calls (Rigby drafting now)

Rigby is drafting the artifacts:
- `tools/check_direct_llm_calls.py` (grep script)
- `.ci/llm_whitelist.txt` (seeded with the top-5 hotspots from #1999 PR body)
- `.github/workflows/check-llm-sdk.yml` (GitHub Action)

When Rigby posts them in conversation `pa-3c7ddc058db1`, Claude Code
implements + opens PR. Pre-approved top-5 remediation shortlist (from
PR #1999 body):

1. `core/agents/content_writer_agent.py` (3 sites: 1456, 1608, 1920)
2. `core/tasks_initiatives.py` (5 sites: 754, 788, 1042, 1076, 1318)
3. `core/agents/analysis/market_intelligence_agent.py` (2 sites: 305, 353)
4. `core/agents/code_review_agent.py` (5 sites: 704, 780, 867, 941, 998)
5. `core/agents/devops_agent.py` (5 sites: 590, 652, 729, 798, 865)

### Rigby's 4-PR plan — PRs #3, #4 queued

- **PR #3 — Cooperative `cancel_token` end-to-end.** Propagate token
  from orchestration → wrapper → provider adapters. Provider-adapter
  aborts (`httpx` transport close for Anthropic/OpenAI). Supervisor that
  force-cancels stuck executions. Retry loops check token before
  rescheduling. `LLMCallCancelled` + `CancelToken` ship today so no
  signature churn when this lands.
- **PR #4 — Nested dispatch budget.** Parent `cancel_token` propagates
  into sub-dispatches — a cancelled COO/CTO boardroom stops all children.
  Blocks on #3.

### B-full (task #9) — separate sprint

Deferred from Fix B-minimal because it requires a migration + canary:

- New `deliverable_appends` table. `call_id` UUID PK, unique constraint
  on `call_id` for idempotent retries. Columns: `deliverable_id`,
  `execution_id`, `agent_name`, `content`, `append_offset`, `status`
  (pending|committed|failed), `routing_metadata` JSON,
  `created_at`/`updated_at`.
- `target_stream_id` append-to-existing-deliverable semantics.
- `SELECT FOR UPDATE` ownership revalidation inside transaction to detect
  mid-flight initiative promotion.
- Streaming multi-chunk append support (`append_id` + `chunk_index`
  unique).
- Canary rollout plan.

### ThinkingAgent 3s router timeout (Rigby priority #5, task #6)

Not investigated in this session — Rigby confirmed the 3s is NOT the
outer `agent_router` wall-clock (which is 300s for ThinkingAgent). It's
an "internal intent/router fast-path timeout", probably in a cognitive
router or priority-router module. Needs a targeted search:

- `FAST_PATH_TIMEOUT`, `ROUTER_FAST_PATH`
- Numeric constants: `3.0`, `3000` (ms), `timeout=3`
- Look in `core/services/priority/`, `core/agents/thinking_*.py` internals

Rigby offered to run that scan on request.

## Known blockers / assumptions

- **COO 24h observation window** — Session 1097's COO daily diagnostic
  fires at 7:30 AM Denver. Observation started this morning
  (2026-04-17), closes 2026-04-18 ~7:30 AM MT. Do not flip
  `POSTING=true` until observation data lands. See
  `project_session_1096_anti_spam_rails.md` for baseline targets.
- **Pre-existing test failures in `test_editor_dispatch_helpers.py`**
  — 2 tests fail on `main` (not caused by Session 1098 work). The v2
  gather refactor from Session 1093 changed the return shape; these
  tests were never updated. Separate cleanup ticket.
- **Railway deploy gotcha (memory):** `railway redeploy` during a build
  CANCELS the build and redeploys OLD code. Let CI finish before any
  manual deploy.
- **Telemetry ingestion safety:** PR #1999 wrapper swallows DB write
  failures silently (logged at ERROR). Monitor the logger for
  `[llm_call_wrapper] LLMCallEvent save failed` pattern.

## Session entry points

- Active conversation: `pa-3c7ddc058db1`
- Memory note this session added:
  (none — design discussions in-conversation; PRs capture the shipped code)
- Handoff to next session: pick up Rigby's lint artifacts as PR #A2, then
  consider PR #3 (`cancel_token`) scope discussion.

## Reference

- Rigby's original 5-priority list (session start):
  1. Boardroom dispatch hang — hard LLM timeout + cancellation (→ PR #1999, #3, #4)
  2. Heartbeat during long deliberations (partially complete pre-session via Session 1091)
  3. Per-execution LLM telemetry (→ PR #1999)
  4. EditorAgent synthesis misroute (→ PR #2000 input-side, #2001 B-minimal output-side, B-full queued)
  5. ThinkingAgent 3s router timeout (queued, task #6)
