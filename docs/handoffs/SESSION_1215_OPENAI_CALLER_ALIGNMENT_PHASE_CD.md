# Session 1215 — OpenAI Caller Alignment Phases C+D (reasoning-contract fixes)

**Status:** 3 PRs merged. Phase C+D active scope closed. Catalog deliverable at 16.1KB. Phase E queued for Session 1216 with AC.
**Date:** 2026-06-23 (same day as Session 1214 close — Chris opted to push straight into Phase C from the 1214 closeout)
**Active conversation:** `pa-e37fe30dc7b941a6` — Session 1214 thread, continued.
**Prior session:** [`SESSION_1214_OPENAI_CALLER_ALIGNMENT_PHASES_A_B.md`](./SESSION_1214_OPENAI_CALLER_ALIGNMENT_PHASES_A_B.md).
**Next session entry point:** Session 1216 — Phase E (CI lint + runtime guard). See §"Phase E queued for Session 1216" + AC block.

## TL;DR

Session 1214 closed pointing at Phase C/D. Chris said "start phase C" — single-arc session.

**Major scoping correction surfaced during the per-file inspection sweep:** the raw `\bmax_tokens\s*=` grep returned **158 matches across 77 files**, but `LLMRequest.max_tokens` is correctly abstracted by `core/services/llm_provider_registry.py` (maps to `max_output_tokens` for gpt-5.x via `_call_responses_api:237`, passes `max_tokens` for non-reasoning via `_call_chat_api:296`). Most of those 158 matches route through that registry abstraction and are **NOT Phase C/D targets**.

Cross-referencing with direct `.chat.completions.create(...)` calls narrowed scope to **6 active files**. Per-file audit found only **3 actually broken** — the other 3 were already correct (Sessions 56, 876 prior fixes) or conditional-on-env-default-ok.

**Top-impact win:** `content/ai_providers.py` was making 2 API round-trips on every gpt-5-mini call — try-with-wrong-params → fail → catch → retry-without-token-limit. PR #2495 eliminated the wasted round-trip while fixing the underlying contract.

## Session Manifest

### PRs merged (3 total)

| # | Title | What | Files | LoC |
|---|---|---|---|---|
| **#2495** | feat(session-1215): Phase C+D PR #1 — content/ai_providers.py OpenAIProvider reasoning-contract fix | Collapsed broken gpt-5-mini + gpt-5 branches into single `'gpt-5' in model.lower()` check. gpt-5.x path passes `max_completion_tokens` only. Removed exception-driven retry-with-different-params (no longer needed). Fixed stale "GPT-4o" comments + duplicate retry branches in fallback block (L221-247). | content/ai_providers.py | -54 / +23 |
| **#2496** | feat(session-1215): Phase C+D PR #2 — views_ai_learning_api.py reasoning-contract fix (3 sites) | Three Django view handlers (baseline_knowledge, learning_insights, personalized_synthesis) were calling `client.chat.completions.create()` against `OPENAI_CONFIG['model']` (gpt-5-mini default) with `temperature=` + `max_tokens=`. Fixed all 3 to pass only `max_completion_tokens`. Silent backend 500s replaced with correct calls. | core/views_ai_learning_api.py | -6 / +3 |
| **#2497** | feat(session-1215): Phase D PR #3 — base_executor.py conditional temperature strip for gpt-5.x | `BaseExecutor.call_openai_api` already used `max_completion_tokens` correctly but unconditionally passed `temperature=`. Default model is gpt-5-mini. Fix: build kwargs dict, only include `temperature` when `'gpt-5'` not in model — preserves sampling control for non-reasoning callers. | agents/executors/base_executor.py | +13 / -6 |

### Deliverables updated

| ID | Action | Result |
|---|---|---|
| `bb775acb-5805-4561-901f-497d2db2add9` | 5 × `deliverable_tool.append` (this session) | Catalog grew from 10,871 → 16,112 chars. Added: Phase C scope refinement (post-audit), entries 8/9/10 for the 3 PRs, entry 11 bundling provenance for 3 already-aligned files + the 1 conditional_ok_default. |
| `2b9aa447-c0c9-4ff3-8483-f92257eb0fcb` | (no action this session) | Spec status: Phase A+B+C+D complete. Phase E remains. Still `accepted`. |

## What shipped

### Phase C/D scope refinement (the most important finding)

Before this session, the spec deliverable estimated Phase C as "~50-80 active files, per-site review" based on the 158-match raw grep. Per-file audit revealed:

- `LLMRequest.max_tokens` in `core/services/llm_provider_registry.py:55` is the abstraction layer's universal param. `OpenAIProvider._call_responses_api:237` maps it to `max_output_tokens` (correct for GPT-5 Responses API). `_call_chat_api:296` passes it as `max_tokens` (correct for non-reasoning models). **Callers passing `max_tokens=N` to `LLMRequest(...)` are NOT Phase C/D targets.**
- `unified_pa_entrypoint.py` (9 sites) routes through `agent_llm_router` / `llm_provider_registry` — same story, not direct OpenAI SDK calls.
- After filtering on `chat.completions.create(... max_tokens=...)` multiline grep, only 13 files match. After excluding archive/tests/one-off scripts, **6 active files** remain.

Per-file inspection of those 6:

| File | Sites | Phase C | Phase D | Real status |
|---|---|---|---|---|
| `content/ai_providers.py` | 4 | **needs fix** | **needs fix** | Fixed PR #2495 |
| `core/views_ai_learning_api.py` | 3 | **needs fix** | **needs fix** | Fixed PR #2496 |
| `agents/executors/base_executor.py` | 1 | ok | **needs fix** | Fixed PR #2497 (Phase D only) |
| `agents/executors/ai_project_executor.py` | 5 | ok | ok | Already correct (Session 876 prior) |
| `core/views_image_tools.py` | 1 | ok | ok | Already correct (Session 56 prior, comment notes "gpt-5-mini doesn't support max_tokens") |
| `core/management/commands/ragtest.py` | 1 | conditional_ok | conditional_ok | LLM_MODEL env defaults to qwen2.5:14b-instruct (Ollama non-reasoning, correct); only broken if env override to gpt-5.x |

**Actual Phase C+D work: 3 files, 8 sites.**

### PR #2495 — `content/ai_providers.py` (highest-leverage win)

Before:

```python
if 'gpt-5-mini' in model.lower():
    # GPT-4o models use standard parameters    ← STALE COMMENT
    completion_params["max_tokens"] = config.get('max_tokens', 4000)
    completion_params["temperature"] = config.get('temperature', 0.7)
    # + top_p + freq_penalty + pres_penalty (all forbidden)
elif 'gpt-5' in model.lower():
    # treat them like GPT-4o                   ← STALE COMMENT
    completion_params["max_tokens"] = config.get('max_tokens', 4000)
    completion_params["temperature"] = config.get('temperature', 0.7)
```

Wrapped in `try/except` that caught the resulting ValueError and retried without any token limit. **Every gpt-5-mini content call through this path made 2 round-trips:** one failed with wrong params, one succeeded without limit. Cost + latency regression on the primary content-generation path.

After:

```python
if 'gpt-5' in model.lower():
    completion_params["max_completion_tokens"] = config.get(
        'max_completion_tokens', config.get('max_tokens', 4000)
    )
else:
    completion_params["max_tokens"] = config.get('max_tokens', 2000)
    completion_params["temperature"] = config.get('temperature', 0.7)
    # + top_p + freq + pres unchanged

response = self.client.chat.completions.create(**completion_params)
```

Single call site, no exception-driven control flow.

### PR #2496 — `core/views_ai_learning_api.py` (Django endpoint correctness)

3 view handlers (`baseline_knowledge`, `learning_insights`, `personalized_synthesis`) all calling the same broken pattern: `temperature=X, max_tokens=Y` against gpt-5-mini. Each was returning silent backend 500s when the SDK rejected the kwargs. Fixed all 3 to pass only `max_completion_tokens={500, 600, 800}` respectively.

### PR #2497 — `agents/executors/base_executor.py` (conditional Phase D strip)

`BaseExecutor.call_openai_api` has signature `(prompt, model="gpt-5-mini", max_tokens=1000, temperature=0.7)`. Already passed `max_completion_tokens=max_tokens` (Phase C ok). Unconditionally passed `temperature=temperature` (Phase D fail on gpt-5.x default).

Pattern: build `create_kwargs` dict; only include `temperature` when model name doesn't contain `'gpt-5'`. Non-reasoning callers retain sampling control.

## Known issues / follow-ons

### Phase E queued for Session 1216 (Rigby's drafted AC, verbatim)

#### (a) Env var semantics — `OPENAI_REASONING_GUARD={warn,strip,error}`

- **`warn` (default)** — Detect forbidden params for reasoning models; log a structured warning per callsite (rate-limited; include model + params present + caller label). Do not modify the request. Do not raise.
- **`strip`** — Detect forbidden params; remove them from request kwargs before calling the SDK; log a structured "stripped" event (rate-limited; include what was stripped). Do not raise.
- **`error`** — Detect forbidden params; raise a clear exception before the API call (`ValueError` or custom `ReasoningGuardViolation`). Error message includes model + forbidden params + fix hint.

If env var is missing/empty: treat as `warn`.

#### (b) Params inspected (and actions taken)

**Forbidden for reasoning models (warn/strip/error):**
- `max_tokens`
- `temperature`
- `top_p`
- `frequency_penalty`
- `presence_penalty`

**Allowed / ignored (no guard action):**
- `max_completion_tokens`, `reasoning_effort`, `verbosity`, plus normal request fields (`messages`, `tools`, `tool_choice`, `input`, `response_format`, etc.)

Guard touches only forbidden keys; leaves everything else unchanged.

#### (c) Model gating rule

Guard triggers when model string contains substring **`"gpt-5"`** (normalized consistently).

- Guarded: `gpt-5-mini`, `gpt-5`, `gpt-5-nano`, version-suffixed variants
- Not guarded: `gpt-4o`, `gpt-4.1`, `o3`, `qwen*`, etc.

If `model` is missing/None, guard does nothing (avoid false positives). Extending gating to other reasoning families (e.g., `o1/o3`) is explicitly out of Phase E scope.

#### (d) CI lint shape

Sibling to `tools/check_direct_llm_calls.py`. Fail-fast pattern. Detects:

- `.chat.completions.create(... max_tokens|temperature|top_p|frequency_penalty|presence_penalty ...)` paired with a `gpt-5` model literal or `OPENAI_CONFIG['model']` reference

Lint should **not** flag:
- Calls routed through `LLMRequest` / `llm_provider_registry` abstraction
- Non-OpenAI providers (Anthropic etc.)
- `tests/`, `scripts/`, `archive/` directories (match existing lint exclusions)

Output: file:line + offending param keys + one-line fix hint ("use max_completion_tokens; remove temperature/top_p/penalties for gpt-5.x").

#### (e) Phase E acceptance signals

Phase E is shipped when ALL of the following are true:

1. **Runtime guard available** in the OpenAI client creation/call path (preferably centralized in `core/services/openai_client_factory.py` or a shared helper used by all OpenAI SDK callsites).
2. **`warn` mode:** a known-bad synthetic call (local dev) produces a warning log containing model + forbidden param list, without raising.
3. **`strip` mode:** the same synthetic call succeeds and outbound kwargs no longer include forbidden keys (verified by debug log or small unit/integration test).
4. **`error` mode:** the synthetic call raises before network call, with clear actionable error message.
5. **CI lint runs in pipeline** and: passes on main after Phase C+D merges, fails on an intentionally-introduced sample violation (validated locally).
6. **No behavior changes for non-gpt-5 models** (temperature/top_p/penalties remain allowed and unmodified).

### Other carryovers (Session 1216+ unless quick win)

- **`OpenAIProvider.generate()` brokenness** (Session 1214 finding, P2) — `ai_core/agents/agent_llm_integration.py:43-108` references undefined `messages` at L90. Unreachable in production; delete vs fix.
- **`content/ai_providers.py:114` bare-with-kwargs `openai.OpenAI(api_key=..., timeout=..., max_retries=2)`** — has explicit timeout (not the 600s footgun), but doesn't use `get_openai_client()`. Phase B follow-on candidate.
- **`agent_llm_integration.py` `AsyncLLMAdapter.chat()` indirect dispatch path** (Session 1214 finding) — actual production LLM call surface; reasoning contract enforcement should also live there. Investigate Session 1216+.
- **Stale-thread dispatcher** (`777d9cd8-…`, P2) — ~$3.60/day savings.
- **System prompt + tool schema size reduction** (P2) — non-smoke conversational turns still 35-68K tokens.

## 24h watch (none triggered)

Phase C+D fixes are pure call-site corrections. No new behavior, no beat schedule, no runtime path. **No 24h watch checklist required.**

## Session 1216 opener

**Catalog deliverable to keep updated:** `bb775acb-5805-4561-901f-497d2db2add9` ("OpenAI Call Site Catalog — Session 1214"). 16.1KB. Append a Phase E entry per AC milestone close.

**Lean:** Phase E is opt-in CI + runtime guard. Default mode `warn` is safe — won't change behavior, just emits structured warnings. Ship the runtime guard first, burn in for 24h, then escalate to `strip` once log volume is reviewed. `error` mode only after all warn/strip findings are zero.

**Active PA thread:** `pa-e37fe30dc7b941a6` continues. Rigby has full Phase A+B+C+D context. Phase E may benefit from a fresh thread to keep system-prompt context lean.

---

**Closes:** Phase C + Phase D active scope of Session 1214 OpenAI caller alignment spec `2b9aa447-…`. Phase E remains.
