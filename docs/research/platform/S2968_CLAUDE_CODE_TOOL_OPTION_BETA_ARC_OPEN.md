# S2968 — Claude Code Tool: Option β (Subprocess Dispatch + Deliverable-as-Spec) — Arc Open

**Status:** Arc-open design doc (S2968 first-action)
**Ratified:** 2026-07-25 (Chris terminal) — supersedes original S2968 first-action (Path A: nightly beat + drift dashboard) as tonight's Option β decision emerged organically from the Signal Insights UI runaway + subsequent PR-2 A/B regression.
**Wrapper pin at arc open:** `pa-7c4e0a19e31c413a` (minted at S2967 close cascade PR #3577)
**HEAD at arc open:** post-PR #3585 (PR-2 revert)

---

## 1. What triggered this arc

**S2967 evening safety batch shipped 5 PRs to prevent runaway spend on `claude_code_tool`** — model ID refresh (Sonnet 4.6), openai override revert, cost + iteration caps, persister allowlist fix, subsystem doc. All correct, all working.

**Then Chris asked two questions that reframed the whole problem:**

> Q1: Are we using an actual coding model or are we using a chatbot model and trying to make it code?
>
> Q2: Would it be easier instead of Rigby giving a prompt to Claude Code to use the Workspace and create a deliverable that has everything that's needed and when the tool is called then the Claude Code tool looks right at the deliverable and begins working?

Honest answers:
- **Q1 = we are using a general-purpose chatbot model (Sonnet 4.6) with 5 primitive tools.** We are NOT using a coding-specialized system.
- **Q2 = yes, Deliverable-as-spec is architecturally much better.** Structured spec > free-form prompt; Chris can review before dispatch; auditable trail; engineer marks state on the same Deliverable.

Both point at the same restructuring: **stop trying to homegrow a coding agent inside `execute_engineering_task`; delegate to Anthropic's real coding agent (the `claude` CLI) driven by a Rigby-authored Deliverable.**

---

## 2. Current-state audit (what exists today)

The engineer at `core/services/claude_code_engineer.py` (~1237 lines post-revert) implements a full custom LLM agent:

- **Model:** general Sonnet 4.6 (or gpt-5-mini fallback)
- **Tools:** 5 primitive (`read_file`, `search_code`, `write_file`, `git_command`, `create_pr`)
- **Loop:** custom `for iteration in range(max_iterations)` with manual `client.messages.create()` calls
- **Context:** just the caller's `task` string (S2967 PR-2 tried adding a `<repo_context>` block, but it caused answer-mode regressions; reverted at PR #3585)
- **Cost accounting:** custom `_cost_from_anthropic_usage(response.usage)` per iteration
- **Post-back:** custom `_post_to_conversation` writing ChatConversation rows

**In contrast, the actual `claude` CLI** (`/Users/donkeyking/.local/bin/claude`, invoked as `claude -p "<task>"`) is:
- Anthropic's shipped coding agent
- Uses whichever Claude model the user's account is configured for (default: latest Sonnet or Opus per subscription)
- Has real coding tools: file editing with context preservation, semantic search across the codebase, plan mode, sub-agent dispatch, test-and-fix loops, git operations, PR creation via `gh`
- Has built-in cost accounting via its own telemetry
- Reads `CLAUDE.md` automatically for context
- Has settings, hooks, permission systems, MCP support
- Supports `--session-id <uuid>` for resumable sessions
- Supports `--output-format json` for structured programmatic output
- Supports `--max-turns` for iteration caps (parity with our PR-1)

**Every capability we built into `claude_code_engineer.py` already exists — and works better — in the CLI.**

---

## 3. Option β architecture (proposed)

### 3.1 Two-mode dispatch

**Mode A — free-form task text** (backwards-compat):
```python
claude_code_tool(task="fix the auth bug in user login", workspace_id=<UUID>, ...)
```
Handler wraps the task as a Deliverable ephemerally, or passes directly to `claude -p`.

**Mode B — Deliverable spec** (preferred going forward):
```python
claude_code_tool(deliverable_id="<UUID>", workspace_id=<UUID>, ...)
```
Handler resolves Deliverable → subprocess dispatches `claude -p` with a prompt that instructs the engineer to first `read` the Deliverable content, then execute.

### 3.2 Engineer becomes a subprocess wrapper

New `execute_engineering_task_v2`:

```python
def execute_engineering_task_v2(
    task_or_deliverable_ref: str,
    conversation_id: Optional[str] = None,
    workspace_root_path: Optional[str] = None,
    max_iterations: Optional[int] = None,
    max_cost_usd: Optional[float] = None,
    timeout_seconds: int = 1800,   # 30 min hard cap
) -> Dict[str, Any]:
    """Dispatch to Claude Code CLI as a subprocess."""

    cmd = [
        'claude',
        '--print',                          # non-interactive
        '--dangerously-skip-permissions',   # trust the sandbox
        '--session-id', str(uuid.uuid4()),
        '--max-turns', str(effective_max_iterations),
        '--output-format', 'json',
        '--model', 'sonnet',                # or 'opus' for hard tasks; configurable
        task_or_deliverable_ref,            # or the actual prompt
    ]

    result = subprocess.run(
        cmd, cwd=workspace_root_path, capture_output=True, text=True,
        timeout=timeout_seconds,
        env={**os.environ, 'ANTHROPIC_API_KEY': anthropic_key},
    )

    parsed = json.loads(result.stdout)
    return {
        'status': 'success' if result.returncode == 0 else 'error',
        'summary': parsed.get('result', ''),
        'cost_usd': parsed.get('cost_usd', 0.0),
        'iterations_used': parsed.get('num_turns', 0),
        'session_id': parsed.get('session_id'),
        'model': parsed.get('model'),
        # ... etc
    }
```

### 3.3 What survives from the current architecture

**KEEP:**
- `claude_code_tool` schema on Rigby (unchanged surface for callers)
- `_handle_claude_code` dispatcher (workspace_id resolution, conversation_id auto-inject, response envelope with resolution provenance — all S2967 wins)
- `claude_code_engineer_task` Celery task (still runs on `code_jobs` queue, still writes AgentExecution row, still wires S1174 follow-up wake)
- `max_iterations` + `max_cost_usd` schema params (map to `--max-turns` + a post-run cost check)
- `budget_exceeded` envelope status (kill subprocess if cost check fails post-run)
- `_post_to_conversation` (fail-loud contract preserved)
- Everything about workspace_tool.update (Ledger #22 discharge — orthogonal)

**DELETE (~600 LOC dead code):**
- `_ENGINE_PRICING_SONNET_46` + `_cost_from_anthropic_usage` (CLI has its own cost telemetry)
- `_execute_tool` + all 5 primitive tool implementations (~200 LOC)
- `_ensure_git_repo` + `_resolve_repo_root` (CLI reads from `cwd`)
- `_execute_engineering_task_openai` + `_execute_engineering_task_anthropic` (main LLM loops) (~200 LOC)
- `CHANGE_SYSTEM_PROMPT` + `ANSWER_SYSTEM_PROMPT` + `_infer_request_mode` + clarification-stall retry contract (CLI has its own system prompt engineering; `request_mode` becomes ~ deprecated or ~ maps to `--effort low/medium/high`)
- `TOOLS` list (~200 LOC of tool schemas)
- `REPO_ROOT` / `WRITABLE_ROOT` constants
- `_build_repo_context` (was reverted at PR #3585; would have been dead code anyway)

**ADD (~200 LOC new):**
- `deliverable_id` param on `claude_code_tool` schema
- Deliverable-resolution branch in `_handle_claude_code`
- New subprocess dispatcher in `execute_engineering_task_v2`
- JSON output parsing
- Model selection param (sonnet default, opus opt-in for complex tasks)
- Deliverable status-update hook (engineer marks Deliverable `completed` / `partial` / `blocked` on ship)

**Net:** delete ~600 LOC, add ~200 LOC. **~400 LOC net reduction** + FAR better output quality.

### 3.4 Deliverable-as-spec schema

New `deliverable_type='engineering_spec'` with structured content sections:
- **Goal** — one-paragraph what-and-why
- **Acceptance criteria** — bulleted list; engineer must satisfy each
- **Files to touch** (optional) — path hints; engineer may explore beyond if needed
- **Related docs** — links to CLAUDE.md sections, ADRs, topic docs, prior handoffs
- **Out of scope** — what NOT to change (prevents scope creep)
- **Expected shape** — PR title convention, commit message format, whether tests are required

Rigby generates this via a new `deliverable_tool.action='create_engineering_spec'` action (or reuses `create` with `deliverable_type='engineering_spec'` — TBD).

**Chris review point:** because the Deliverable is a workspace object, Chris can inspect it in the UI BEFORE dispatch, ratify or revise. Today's $5 Signal Insights runaway would have been caught here — "this scope is too big; break into 3 parts."

### 3.5 Model selection

`claude` CLI supports `--model sonnet` / `--model opus` / `--model haiku` / any full model ID.

- **Default: `sonnet`** — mid-tier, good coding, moderate cost. Matches current homegrown behavior.
- **Opt-in via schema `model` param: `opus`** — top-tier reasoning; for wide-scope architectural changes.
- **Opt-in `haiku`** — fast + cheap; for trivial ANSWER-mode tasks (line count, file exists, etc.).

Rigby picks the model per task. Chris can override via the schema.

---

## 4. What this closes / what stays open

**Discharges (against `docs/topics/claude-code-engineer.md` §Known gaps):**
- **Gap #2 (no context pre-injection)** — CLI reads `CLAUDE.md` automatically + can `read_file` via richer tools
- **Gap #4 (primitive tool surface)** — CLI has jump-to-definition, run-tests, apply-diff, etc.
- **Gap #5 (no persistent workspace)** — CLI's `--session-id` supports resumable sessions
- **Gap #6 (test coverage limited)** — CLI's own test infrastructure is mature; our integration test surface shrinks to "did the subprocess return the right envelope shape?"

**Stays open (orthogonal):**
- **Gap #1 (per-dispatch cost cap)** — PR-1 caps concept survives, mechanism changes from per-iteration to post-run + `--max-turns`
- **Ledger #22 (workspace_tool.update)** — orthogonal, already discharged at S2967 PR #3576

**New gaps introduced:**
- **CLI availability at runtime** — `claude` must be installed on every environment (local dev + Railway). Add to Procfile deploy step.
- **CLI version pinning** — CLI updates could change output-format JSON schema. Pin version + integration test on upgrade.
- **Cost telemetry mapping** — CLI's cost format may differ from our `cost_usd` field. One-time mapping.

---

## 5. Migration plan

### 5.1 Ship path

**PR-A (S2968 first-code PR): subprocess dispatch prototype** (~200 LOC + 3 tests)
- Add `execute_engineering_task_v2` alongside the existing engineer (do NOT delete legacy yet)
- Feature-flag via env var `CLAUDE_CODE_ENGINE_MODE=v2` (default `v1` — legacy engineer preserved)
- Both codepaths write to same AgentExecution + envelope shape
- Test: mock subprocess.run, verify envelope parsing
- **Ship + Rigby A2 SIGN via A/B test:** same task → both engines → compare cost + output quality

**PR-B: Deliverable-as-spec schema + handler branch** (~100 LOC + 2 tests)
- Add `deliverable_id` param to `claude_code_tool` schema
- Handler branch: if `deliverable_id`, resolve → construct engineer prompt that instructs "read Deliverable <UUID> via deliverable_tool.get, execute per its acceptance criteria"
- Test: mock deliverable_tool.get, verify prompt construction

**PR-C: Deliverable status write-back** (~80 LOC + 2 tests)
- New `deliverable_tool.action='update_engineering_status'` — engineer calls it on ship
- Handler updates status: `completed` / `partial` / `blocked` / `escalated`
- Test: dispatch engineer with test Deliverable, verify status transition on completion

**PR-D: Flip default to v2 + delete v1** (~600 LOC deletion + docs update)
- After 3+ successful A/B tests confirming v2 quality, flip `CLAUDE_CODE_ENGINE_MODE` default to `v2`
- Delete legacy engineer LLM loop + all 5 primitive tool implementations
- Update `docs/topics/claude-code-engineer.md` to reflect new architecture
- Session-close ratification

### 5.2 Risk mitigations

- **v1 preserved during transition.** Any regression → flip env var back to `v1` (no rollback PR needed).
- **A/B test methodology.** For each PR-A test, dispatch SAME task on both engines, compare cost + iterations + output quality. Do not delete v1 until at least 3 A/B pairs show v2 ≥ v1 on all metrics.
- **CLI installation.** Add `claude` install to `Makefile` bootstrap + Procfile release step. Fail deploy loud if `claude --version` errors.

### 5.3 Primary risk to prove before PR-B / PR-C (Rigby T1 SIGN refinement)

Rigby explicitly flagged **two blockers that MUST land at PR-A verification stage** before we build PR-B (Deliverable-as-spec) or PR-C (status write-back):

1. **`claude` CLI availability on the code_jobs celery worker's env.** The worker inherits from `make celery` which inherits from the shell that started it. Confirm `subprocess.run(['claude', '--version'])` succeeds inside the worker; add a startup preflight if not. Fail loud on missing CLI.

2. **JSON output schema stability.** `claude --output-format json` schema may change across CLI versions. Pin the CLI version we test against (`claude --version` at pin time recorded in `docs/topics/claude-code-engineer.md`). Add an integration test that asserts our parser handles the expected fields (`result`, `cost_usd`, `num_turns`, `session_id`, `model`). If Anthropic ships a CLI upgrade that changes shape, this test fires + we catch it before PR-B/C break.

**Corollary:** if PR-A cannot get past these two blockers, Option β itself is at risk — pause the arc and reconsider (e.g., use Anthropic Managed Agents SDK directly instead of the CLI subprocess).

### 5.4 Deliverable-as-spec schema availability (Rigby T1 SIGN refinement)

Do NOT assume `deliverable_type='engineering_spec'` will pass through the tool + schema allowlists cleanly. Per `feedback_pa_deliverables_tool_flags_ratifications_as_diagnostic`, the deliverable_tool has a known behavior where unrecognized deliverable_types get flagged `diagnostic_status='diagnostic'` and hidden from the UI.

**PR-B pre-work required:**
- Grep `td_handlers_content.py` + `td_handlers_agents.py:_handle_deliverables` for the deliverable_type allowlist.
- Add `'engineering_spec'` to the allowlist explicitly.
- Verify Deliverable creation with `deliverable_type='engineering_spec'` shows up in the workspace UI (not silently diagnostic-flagged).
- If the allowlist gate is deeper than a simple enum extension, PR-B scope grows — flag before implementing.

---

## 6. Rigby T1 SIGN questions (this doc)

Please tool-verify (`repo_tool.read_file` on the referenced code + specs) before AGREE:

1. **Is the ~600 LOC deletion estimate right?** Read `claude_code_engineer.py` line ranges — confirm what stays vs what dies.
2. **Are there call sites of the current engineer that would break?** Grep for `execute_engineering_task` / `_execute_tool` / `TOOLS` usages outside `claude_code_engineer.py`.
3. **Is Deliverable-as-spec feasible on your tool surface?** Check `deliverable_tool` action enum — does it support `create` with arbitrary `deliverable_type`, or do we need a new action?
4. **Does `claude` CLI installation on Railway make sense?** Any deploy-time concern?

Then answer:

**Zoom-out (mandatory per `feedback_zoom_out_ask_per_rigby_sign`):**
- Is Option β too big a swing? Should we do PR-A only, prove the subprocess model works on ONE dispatch, then commit to the arc?
- Should Mode A (free-form task) be deprecated on ship or preserved permanently for one-off dispatches?
- Is there a coupling risk between the Deliverable system and the engineer that we should design around (e.g., Deliverable schema changes breaking the engineer's status writes)?

**Ship-tonight vs S2968-tomorrow:**
- PR-A alone is ~2-3 hours of focused work + A/B test
- If Chris wants to keep going tonight, we can ship PR-A + Rigby A2 SIGN + 1 A/B pair before session close
- If he wants to sleep on it, this doc becomes S2968 first-action tomorrow

Give me AGREE/REVISE + your read on the zoom-out + timing recommendation.
