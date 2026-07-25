<!-- DOC-POINTER-V1 -->
> **⚠ Stats in this doc may drift from code.** For current verified numbers see [`../PLATFORM_INVENTORY.md`](/docs/PLATFORM_INVENTORY.md) (sole authoritative counts per `DOC_LIFECYCLE.md` §2c). Run `python manage.py verify_doc_claims --only-drift` to see which specific claims currently diverge from runtime reality.

# Claude Code Engineer (PA-Dispatched Autonomous Coding)

The Claude Code Engineer is the platform's **autonomous coding agent**, dispatched by Rigby (PA) via the `claude_code_tool`. When Rigby identifies a bug, a needed feature, or a code change, she calls this tool with a task description; a Celery worker then spawns an LLM loop that can read files, search the codebase, write code, create git branches/commits, and open GitHub pull requests — all inside the caller's working tree, without any human turn-by-turn intervention.

**Session-history anchor:** built at S1226 P3 (PR #2556); hardened at S1229 (queue routing), S1230 P4 (ANSWER/CHANGE mode split, clarification-stall contract), S1262 (AgentExecution row + fail-loud post-back), S2728 F-CC-3 (`follow_up_will_fire` observability), and **S2967** (workspace_id auto-resolve-repo + explicit `repo_root` DI + Sonnet 4.6 model refresh + Makefile openai override removal).

**S2967 close observation (2026-07-25):** the first live production dispatch that actually shipped code changes end-to-end used the S2967 workspace resolution fix. Prior dispatches were either read-only Q&A or no-op'd due to `REPO_ROOT='/app'` fallback on local dev.

---

## Architecture

Three files own the engineer end-to-end:

| File | Purpose |
|---|---|
| `core/services/pa_tool_schemas.py:5545+` | `claude_code_tool` schema Rigby sees (task / conversation_id / workspace_id / request_mode) |
| `core/services/td_handlers_codejobs.py:330` | `_handle_claude_code` — dispatcher, resolves workspace_id → root_path, enqueues Celery task, echoes provenance (`workspace_id_resolved`, `resolved_from`) |
| `core/tasks.py:11873` | `claude_code_engineer_task` — Celery worker entry, creates AgentExecution row, wires S1174 follow-up wake |
| `core/services/claude_code_engineer.py` | The engineer itself — system prompts, tool definitions, LLM loop, tool execution |

### End-to-end flow

```
Rigby (PA) picks claude_code_tool via GPT-5.2 function-calling
    │
    ▼  payload: {task, workspace_id?, conversation_id?, request_mode?}
_handle_claude_code (td_handlers_codejobs.py:330)
    │  • Extracts task text (accepts task / task_description / description / prompt / message)
    │  • Auto-injects conversation_id from PA context if omitted
    │  • Resolves workspace_id → ProjectWorkspace.root_path
    │       (S2967: 4-priority chain — explicit → active_workspace → fallback)
    │  • Response echoes: workspace_id_resolved, workspace_root_path, resolved_from,
    │                     follow_up_will_fire, task_id
    │
    ▼  .delay() on the `code_jobs` Celery queue (--pool=solo locally, --pool=prefork on Railway)
claude_code_engineer_task (tasks.py:11873)
    │  • soft_time_limit=5400 (90 min), max_retries=0 (no LLM re-burn)
    │  • Creates AgentExecution row (input_data.celery_task_id + workspace_root_path)
    │  • Calls execute_engineering_task(...)
    │  • On terminal state → wires create_implicit_followup_subscription
    │       + fire_agent_followup_subscriptions
    │       (posts result back to conversation via S1174 wake path)
    │
    ▼
execute_engineering_task (claude_code_engineer.py:911)
    │  • Resolves request_mode: 'answer' | 'change' | 'auto' (verb heuristic)
    │  • Selects system_prompt: CHANGE_SYSTEM_PROMPT | ANSWER_SYSTEM_PROMPT
    │  • Resolves provider: env CLAUDE_CODE_ENGINE_PROVIDER (default: anthropic)
    │  • Resolves repo_root via _resolve_repo_root(workspace_root_path)
    │       (S2967: explicit path → warm clone → cold clone → REPO_ROOT fallback)
    │  • Enters LLM loop (max_iterations=500 default, NO cost cap)
    │
    ▼  each iteration, LLM picks a tool → engineer executes
_execute_tool(name, input, repo_root)  (claude_code_engineer.py:629)
    │  read_file    — cat file under repo_root (50KB cap per read)
    │  search_code  — grep -rn under repo_root (glob-scoped, 20 result cap)
    │  write_file   — write to path under repo_root
    │  git_command  — arbitrary git subprocess in repo_root (60s timeout)
    │  create_pr    — POST to GitHub /pulls via gh CLI or urllib
    │
    ▼  on stop_reason=end_turn or max_iterations
_post_to_conversation (claude_code_engineer.py:1173)
    │  • If conversation_id: writes ChatConversation row + broadcasts to PA WebSocket
    │  • If no conversation_id: ERROR-log [CLAUDE_CODE_POSTBACK_DROPPED]
    │       (S1262 fail-loud contract — LLM output is still persisted on AgentExecution)
```

---

## The tool surface (what the engineer can actually do)

Five primitive tools defined at `claude_code_engineer.py:352-522`:

| Tool | Behavior | Guardrails |
|---|---|---|
| `read_file` | Read a file under repo_root, optional line range | 50KB output cap |
| `search_code` | grep -rn under repo_root, glob-filterable | 20-match cap, 30s timeout |
| `write_file` | Write content to a path under repo_root | Creates parent dirs; no diff preview |
| `git_command` | Run arbitrary `git <command>` in repo_root | 60s timeout, 10KB output cap |
| `create_pr` | Open GitHub PR via API (or gh CLI fallback) | Requires GITHUB_TOKEN env; hard-coded to `clwest/donkey-betz-platform` repo |

**Not available:** jump-to-definition, cross-file rename, run-tests, run-linter, run-typecheck, read-git-log, resolve-merge-conflict, install-dependency. Everything is grep + read + write.

---

## Context model — cold start every dispatch

The system prompt (CHANGE at `line 315`, ANSWER at `line 330`) is the ONLY context injected. The user message is *literally just the `task` string Rigby passed*. No CLAUDE.md, no `PLATFORM_INVENTORY.md`, no file tree, no directory listing, no relevant-symbol map — the engineer discovers the entire codebase from scratch by running `search_code` and `read_file` calls one at a time.

**Observed cost implication (S2967 Signal Insights UI dispatch, killed at iter 75):**
- 75 iterations in 16 minutes, all `read_file` + `search_code` (zero writes)
- ~$0.067/iteration average
- Would have hit ~$25–45 total at max_iterations=500 with no writes guaranteed
- Cold-start exploration burn: probably $3–5 of the $5 spent was just building the same mental model of `SignalCluster` that any human engineer with `docs/topics/spider-network.md` would already have

**S2967 close position:** this is the single biggest cost lever in the current design. See §Known gaps below.

---

## Two-mode dispatch (ANSWER vs CHANGE)

Session 1230 P4 split the single SYSTEM_PROMPT into two:

- **`ANSWER_SYSTEM_PROMPT`** (`claude_code_engineer.py:~330`) — readonly Q&A. Engineer must produce the requested output shape; no branches, no PRs, no clarification. Wraps a clarification-stall retry contract: if the engineer's response matches `_CLARIFICATION_STALL_MARKERS`, the loop is retried ONCE with a hardened "do not ask for clarification" preamble. If retry also stalls, envelope status flips to `contract_failure`.
- **`CHANGE_SYSTEM_PROMPT`** (`line 315`) — code modification. Engineer reads, edits, creates a branch + commits + PR. Change mode legitimately asks for clarification on ambiguous tasks (so no reflex-retry).

**`request_mode='auto'`** (default) infers mode from task verbs via `_infer_request_mode` (`claude_code_engineer.py:~380`) — write-verbs (add/fix/refactor/implement/...) route to `change`, everything else to `answer`.

**Known model behavior:** `gpt-5-mini` pattern-matches into a clarification-stall on change-mode tasks despite fully-specified prompts. `claude-sonnet-4-6` does not exhibit this pattern. S2967 removed the Makefile-hardcoded `CLAUDE_CODE_ENGINE_PROVIDER=openai` override so local dev now defaults to Anthropic.

---

## Provider routing

Env var `CLAUDE_CODE_ENGINE_PROVIDER` (default `'anthropic'`) selects the LLM:

- `anthropic` — `claude-sonnet-4-6` via `core/services/anthropic_client_factory.py` (S2967 model refresh; old ID `claude-sonnet-4-20250514` returns 404 not_found_error on current Anthropic API).
- `openai` — `gpt-5-mini` via `core/services/openai_client_factory.py`. Session 1226 fallback for Anthropic credit exhaustion. Same 5 tools, different message format.

Provider is resolved at `execute_engineering_task:970`. Response envelope echoes `provider` + `mode` fields.

---

## Response envelope

Dispatch response (from `_handle_claude_code`):
```json
{
  "status": "dispatched",
  "task_id": "<celery task UUID>",
  "request_mode": "change|answer|auto",
  "conversation_id": "<UUID or null>",
  "follow_up_will_fire": true|false,
  "workspace_id_resolved": "<UUID or null>",
  "workspace_root_path": "<path or null>",
  "resolved_from": "explicit|active_workspace|fallback",
  "message": "<human-readable summary>"
}
```

Completion envelope (from `execute_engineering_task`, persisted on `AgentExecution.output_data`):
```json
{
  "status": "success|error|contract_failure",
  "summary": "<first 2000 chars of final_text>",
  "files_changed": ["path1", "path2", ...],
  "pr_url": "<GitHub PR URL or null>",
  "provider": "anthropic|openai",
  "mode": "change|answer",
  "repo_root": "<resolved working tree>"
}
```

---

## Observability

- **AgentExecution row** (`core.models.AgentExecution`, agent=`claude-code`) — the canonical record. Query via `celery_task_id=<UUID>` or via `execution_history_tool` from PA.
- **CeleryTaskEvent** (`core.models_celery_telemetry.CeleryTaskEvent`) — Celery layer status (STARTED/SUCCESS/FAILURE/REVOKED), duration, worker hostname, error type/message.
- **`celery-code-jobs.log`** — engineer's per-iteration log (each `[ClaudeEngineer] Tool: <name> (iteration N)` line).
- **Follow-up wake** — on completion with non-empty conversation_id, `fire_agent_followup_subscriptions` writes a Rigby-authored ChatConversation row (`source='pa'`, `intent='agent_completion'`) and broadcasts `agent_completed` on the `pa_conversation_<conversation_id>` channel.

---

## Known gaps (S2967 close audit — post PR-1/PR-1a shipping)

| # | Gap | Severity | Status |
|---|---|---|---|
| 1 | **No per-dispatch cost cap.** `max_iterations=500` uncapped; no USD budget guard. Runaway dispatches can burn arbitrary credit. Observed S2967: $5 in 16 min at iter 75 with zero writes. | HIGH — customer-facing on A1 | **CLOSED S2967 PR-1** (`max_cost_usd` schema param + per-iteration accumulator + `status='budget_exceeded'` envelope; default $5) |
| 2 | **No context pre-injection.** Every dispatch is a cold start; engineer re-discovers the whole codebase from scratch. Directly amplifies gap #1. | HIGH — cost lever | **CLOSED S2968 PR-2** (`context_files` schema param + `_build_repo_context()` engine helper; defaults inject repo tree + CLAUDE.md excerpt [300 lines] + PLATFORM_INVENTORY excerpt [100 lines]; fixed cost ~$0.03/dispatch) |
| 3 | **No `max_iterations` schema param.** Callers can't request tighter budget per-dispatch. | MEDIUM | **CLOSED S2967 PR-1** (bundled — `max_iterations` schema param; default 150) |
| 4 | **Primitive tool surface.** No jump-to-definition, run-tests, run-linter, install-dependency. Engineer spends iterations on tasks a mature agent would resolve with one tool call. | MEDIUM | OPEN — separate arc; `run_tests` = next-best-ROI addition per Rigby T1 SIGN |
| 5 | **No persistent workspace between dispatches.** Each dispatch re-uses the /tmp clone (on Railway) or the workspace root_path (on local). No caching of prior exploration. | LOW | OPEN — defer |
| 6 | **Test coverage limited to fallback + mode routing.** The full "write real code + open a PR" path has no integration test. | MEDIUM — recycle risk | Partial: S2967 PR-1 added `test_engineer_budget_caps.py` (3 tests). Full write-path integration test still OPEN — S2969+ PR-3 target |
| 7 | **Stale model IDs elsewhere.** ~50 refs to `claude-sonnet-4-20250514` in `models_llm_routing.py` + `claude_code_agent.py` + `tasks_conversations.py`. Any code path routing through those hits Anthropic 404. | MEDIUM — separate arc | **CLOSED S2967 PR-1a** (50 refs swept via sed → `claude-sonnet-4-6`) |

---

## Test coverage

- `core/tests/test_engineer_openai_fallback.py` — verifies `CLAUDE_CODE_ENGINE_PROVIDER` routing (env → provider choice)
- `core/tests/test_engineer_request_mode.py` — verifies ANSWER/CHANGE prompt dispatch, verb heuristic, clarification-stall retry contract
- **Missing:** integration test for full engineer → write_file → git_command → create_pr pipeline
- **Missing:** cost/iteration cap enforcement tests (once implemented per gap #1)

---

## References

- `core/services/pa_tool_schemas.py:5545+` — claude_code_tool schema
- `core/services/td_handlers_codejobs.py:330` — dispatcher / workspace resolver
- `core/tasks.py:11873` — Celery task wrapper + follow-up wake wiring
- `core/services/claude_code_engineer.py` — the engineer proper
  - `line 315` — `CHANGE_SYSTEM_PROMPT`
  - `line 330` — `ANSWER_SYSTEM_PROMPT`
  - `line 352-522` — `TOOLS` list (5 primitive tools)
  - `line 525` — `_ensure_git_repo()`
  - `line 626` — `_resolve_repo_root()` (S2967)
  - `line 629` — `_execute_tool()`
  - `line 911` — `execute_engineering_task()`
  - `line 1173` — `_post_to_conversation()`
- **Session handoffs**: S1226 (P3 initial), S1229 (queue routing), S1230 (P4 mode split), S1262 (fail-loud), S2728 (F-CC-3 observability), **S2967 (workspace_id + repo_root DI + Sonnet 4.6 + Makefile openai revert)**
- **Rigby Tool Gap Ledger:** `5c84e75a-0ce5-4f93-9da5-f6db4e53e7f0`
- **Runaway-cost tool-gap deliverable (S2967):** `c578eaa2-68b3-40ba-94ba-999d5b24dcbd`
