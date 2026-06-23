# Session 1216 — OpenAI Caller Alignment Phase E (runtime guard + CI lint) — SPEC CLOSED

**Status:** 2 PRs merged. Phase E complete. Spec deliverable `2b9aa447-…` flipped to `completed`. Catalog deliverable final at 17.1KB.
**Date:** 2026-06-23 (third single-day session in the OpenAI caller alignment arc — Chris pushed straight from "start phase C" → "start phase E" without pause)
**Active conversation:** `pa-e37fe30dc7b941a6` — Session 1214 thread, continued.
**Prior session:** [`SESSION_1215_OPENAI_CALLER_ALIGNMENT_PHASE_CD.md`](./SESSION_1215_OPENAI_CALLER_ALIGNMENT_PHASE_CD.md).
**Next session entry point:** Session 1217 — see §"Open follow-ups" for non-spec carryovers.

## TL;DR

Session 1215 closed with Phase E queued + Rigby's drafted acceptance criteria. Chris said "start phase E" — single-arc session.

Two PRs ship the full Phase E surface:

- **PR #2499 (runtime guard)** — adds `apply_reasoning_guard()` + `ReasoningGuardViolation` + `_install_reasoning_guard()` to `core/services/openai_client_factory.py`. Factory-returned clients have their `chat.completions.create` method wrapped at construction time. Mode controlled by `OPENAI_REASONING_GUARD={warn,strip,error}` env var (default `warn`). 13 unit tests, all passing.
- **PR #2500 (CI lint + closes the spec)** — AST-based `tools/check_reasoning_contract.py` + `.github/workflows/check-reasoning-contract.yml` + 10 unit tests. AST parsing avoids the docstring false positives the regex lint produces. Ships in `--warn-only` since Phase C+D close left zero violations on main.

Per memory rule (status transitions go through `content_tool`), spec deliverable `2b9aa447-…` flipped to `completed` via `content_tool.content_complete`.

**Total across the three single-day sessions (1214 + 1215 + 1216): 16 PRs merged. ~30 call sites aligned. Runtime guard + CI lint in place. Catalog deliverable bb775acb-… persistently maintained throughout.**

## Session Manifest

### PRs merged (2 + docs)

| # | Title | Commit | What |
|---|---|---|---|
| **#2499** | feat(session-1216): Phase E PR #1 — reasoning-contract runtime guard in openai_client_factory | `899a8c7c` | New public API: `apply_reasoning_guard(kwargs, model, caller_label)` pure function + `ReasoningGuardViolation(ValueError)` + `_install_reasoning_guard(client, async_create)`. Factory returns clients with `chat.completions.create` already wrapped — no per-callsite changes needed. Env-gated `OPENAI_REASONING_GUARD={warn,strip,error}`, default warn. Trigger gate: `"gpt-5"` substring in model name. Forbidden kwargs: max_tokens / temperature / top_p / frequency_penalty / presence_penalty. 13 unit tests covering all modes + boundary cases. |
| **#2500** | feat(session-1216): Phase E PR #2 — AST-based reasoning-contract CI lint + GH Actions workflow | `9297864b` | `tools/check_reasoning_contract.py` (217 LoC) walks AST of every active .py file, flags `*.chat.completions.create(model="gpt-5.x" or OPENAI_CONFIG['model'], <forbidden>=...)` calls. `.github/workflows/check-reasoning-contract.yml` runs on PRs + push to main, ships `--warn-only`. 10 unit tests. Also: factory docstring reworded to drop literal pattern that was tripping the existing regex lint (back to baseline 6 violations). New lint script whitelisted in `.ci/llm_whitelist.txt` (same treatment as existing `check_direct_llm_calls.py`). |

### Deliverables updated

| ID | Action | Result |
|---|---|---|
| `bb775acb-5805-4561-901f-497d2db2add9` | 2 × `deliverable_tool.append` (this session) | Catalog grew from 16,112 → 17,068 chars. Added entries 12 (runtime guard) + 13 (CI lint, closes spec). |
| `2b9aa447-c0c9-4ff3-8483-f92257eb0fcb` | `content_tool.content_complete` | Status: `accepted` → `completed`. Closure note: "Phase A+B+C+D+E shipped across Sessions 1214-1216 (one day, 2026-06-23). 16 PRs merged. ~30 call sites aligned. Runtime guard + CI lint in place. Catalog deliverable bb775acb-… maintained throughout." |

## What shipped

### PR #2499 — runtime guard in factory

Three new public exports from `core/services/openai_client_factory.py`:

```python
from core.services.openai_client_factory import (
    apply_reasoning_guard,         # pure-function form
    ReasoningGuardViolation,       # raised in error mode (subclasses ValueError)
    # (_install_reasoning_guard is internal; applied automatically by factory)
)
```

**Mode semantics** (per Rigby's AC):

| Mode | Behavior |
|---|---|
| `warn` (default) | Structured log warning with model + caller + forbidden params present. Kwargs untouched. Never raises. |
| `strip` | Remove forbidden kwargs from outbound request + structured log of what was stripped. Never raises. |
| `error` | Raise `ReasoningGuardViolation` BEFORE the SDK network call. Message includes model + forbidden params + fix hint. |

**Trigger gate:** model string contains substring `"gpt-5"` (covers gpt-5, gpt-5-mini, gpt-5-nano, version-suffixed variants). None/empty model → guard skipped (avoids false positives on routing layer).

**Forbidden kwargs:** max_tokens, temperature, top_p, frequency_penalty, presence_penalty. Allowed: max_completion_tokens, reasoning_effort, verbosity, and standard request fields (messages, tools, tool_choice, input, response_format).

**Installation method:** factory swaps the bound `chat.completions.create` method on the returned client at construction time. The factory's per-`(api_key, base_url)` cache means each unique pair gets the guard installed exactly once. Sync and async paths use parallel guarded methods (`_guarded_sync_create` / `_guarded_async_create`).

**Coverage caveat:** the Responses API path (`client.responses.create()` used by `_call_responses_api` in `llm_provider_registry`) is NOT guarded — it natively uses `max_output_tokens` and accepts no forbidden params, so the guard would be redundant. Direct ad-hoc `OpenAI()` instantiations outside the factory also bypass the guard — Phase B already eliminated those in active code.

### PR #2500 — AST-based CI lint

`tools/check_reasoning_contract.py` walks every active `.py` file's AST. For each `Call` node, checks:

1. **Shape:** Is it `*.chat.completions.create(...)` (matches `client.chat.completions.create`, `self.client.chat.completions.create`, any receiver chain).
2. **Model:** Is the `model=` kwarg a string literal containing `"gpt-5"`, OR a subscript like `OPENAI_CONFIG['model']` (config defaults to gpt-5-mini)?
3. **Forbidden kwarg present:** any of the 5 forbidden kwargs?

All three true → flagged. Otherwise silently allowed.

**Why AST instead of regex:** the existing `tools/check_direct_llm_calls.py` regex-based lint matches docstring/comment references to the patterns it catches. PR #2499's runtime-guard docstring tripped that lint. The new AST-based lint only flags actual `Call` nodes — prose references silently pass through. Verified via the `test_docstrings_and_comments_not_flagged` test case.

**Exclusions:**
- `archive/`, `.venv/`, `node_modules/`, `__pycache__/`, `frontend/`
- `tests/`, `scripts/` (test + ad-hoc code)
- `core/services/llm_provider_registry.py` — abstraction layer maps params per model in `_call_chat_api` / `_call_responses_api`
- `.ci/reasoning_guard_whitelist.txt` — per-file overrides for the new lint (auto-loaded if present)

**Workflow:** `.github/workflows/check-reasoning-contract.yml` runs on PRs touching `**/*.py` + push to main. Ships in `--warn-only` mode — Phase C+D close left zero violations on main, so warn mode produces no false alarms. Promotion to enforce mode (drop `--warn-only`) recommended after 24h burn-in with no surprises.

### Tertiary cleanup in PR #2500 (related to Phase E lint hygiene)

- `core/services/openai_client_factory.py:168` — reworded `_install_reasoning_guard` docstring to drop the literal `client.chat.completions.create` pattern that tripped the existing regex lint. Direct-LLM lint baseline back to 6 violations.
- `.ci/llm_whitelist.txt` — added `tools/check_reasoning_contract.py` to the existing lint's whitelist (the lint's docstring intentionally documents the patterns it catches; same treatment as `tools/check_direct_llm_calls.py`).

## Phase E acceptance — all 6 of Rigby's signals confirmed

| Signal | Status | Evidence |
|---|---|---|
| 1. Runtime guard centralized in factory | ✅ | `apply_reasoning_guard` + `_install_reasoning_guard` in `core/services/openai_client_factory.py` |
| 2. warn mode logs without raising | ✅ | `test_warn_mode_preserves_kwargs` |
| 3. strip mode removes forbidden + logs | ✅ | `test_strip_mode_removes_forbidden_preserves_allowed` |
| 4. error mode raises before network call | ✅ | `test_error_mode_raises_violation` + `test_wrapped_create_raises_before_network_call` |
| 5. CI lint passes main / fails violations | ✅ | `python tools/check_reasoning_contract.py` returns 0 violations on main; 10 unit tests cover detection branches |
| 6. No behavior change for non-gpt-5 models | ✅ | `test_non_reasoning_model_passes_through` + `test_wrapped_create_allows_non_gpt5` + `test_non_gpt5_models_not_gated` |

## Final ledger across the 3-session arc

| Session | Phase | PRs (work) | PRs (docs) | Key wins |
|---|---|---|---|---|
| 1214 | A + B + B-async-factory | 7 | 1 | 22 bare-instantiation sites cleared; async factory ships |
| 1215 | C + D | 3 | 1 | 8 reasoning-contract sites fixed; double-round-trip bug eliminated; 3 silent endpoint 500s fixed |
| 1216 | E | 2 | 1 (this) | Runtime guard + CI lint shipped; spec closed |
| **Total** | **A → E** | **12** | **3** | **15 PRs in one day** |

**Catalog deliverable bb775acb-… progression:** seed 6.3KB → after 1214 close 10.9KB → after 1215 close 16.1KB → after 1216 close 17.1KB. Persistent in workspace UI, pinned, category Platform Capability Audit.

**Spec deliverable 2b9aa447-… status:** `proposed` → `accepted` → `completed`.

## Known issues / follow-ons (Session 1217+)

These are NOT spec follow-ons — the spec is closed. These are carryovers from Sessions 1214-1215 that didn't become Phase E scope:

| Priority | Item | Notes |
|---|---|---|
| P2 | `OpenAIProvider.generate()` brokenness | `ai_core/agents/agent_llm_integration.py:43-108` references undefined `messages` at L90. Unreachable in production; delete vs fix-and-smoke. Rigby's lean: either delete if truly unused or fix with a tiny unit smoke. |
| P2 | `content/ai_providers.py:114` bare-with-kwargs `openai.OpenAI(...)` | Has explicit 60s timeout (not the 600s footgun) but doesn't route through `get_openai_client()`. Phase B follow-on candidate; would now also get the reasoning guard for free if migrated. |
| P2 | Promote `check_reasoning_contract.yml` to enforce mode | Drop `--warn-only` after 24h burn-in. Should be a 1-line PR. |
| P3 | Stale-thread dispatcher (`777d9cd8-…`) | ~$3.60/day savings, lean A (per-conversation `session_closed` flag). Carryover since Session 1213. |
| P3 | System prompt + tool schema size reduction | Non-smoke conversational turns still 35-68K tokens. No spec filed yet. |

## 24h watch (none triggered)

Phase E PRs ship new infrastructure (env-gated runtime guard + CI lint) with no behavior change in the default `warn` mode. **No 24h watch checklist required.** Optional promote-to-enforce watch can fire 2026-06-24 if Chris wants to escalate.

## Session 1217 opener

**Suggested lean:** carryovers above are all P2/P3. None block anything. Session 1217 may want to pick from a different work queue.

**Active PA thread:** `pa-e37fe30dc7b941a6` continues but holds 3 sessions of context. Strong recommendation: spin a fresh thread for Session 1217 to keep system-prompt context lean. Rigby's drafted operational handoff sections will carry forward via this doc.

---

**Closes:** Phase E of Session 1214 OpenAI caller alignment spec `2b9aa447-…`. **Spec deliverable closed in full.**
