# Session 1214 — OpenAI Caller Alignment Phases A+B (factory adoption + dead-code removal)

**Status:** All 8 PRs merged. Phase A done. Phase B closed at 22-of-21 verified Session 1213 sites cleared. Catalog deliverable shipped + maintained live (10.9KB).
**Date:** 2026-06-23
**Active conversation:** `pa-e37fe30dc7b941a6` — Session 1214 thread (Rigby PA).
**Prior session:** [`SESSION_1213_SMOKE_CONTEXT_MINIMIZATION.md`](./SESSION_1213_SMOKE_CONTEXT_MINIMIZATION.md).
**Next session entry point:** Session 1215 — Phase C (`max_tokens=` → `max_completion_tokens=` per-callsite audit). See §"Open follow-ups" + §"Session 1215 opener".

## TL;DR

Session 1213 closed pointing at the **OpenAI caller alignment to gpt-5-mini reasoning contract** spec (deliverable `2b9aa447-…`, 5-phase plan). Original audit flagged 74 bare `OpenAI()`/`AsyncOpenAI()` instantiations + ~150 hardcoded model literals + ~90 `max_tokens=` + ~86 `temperature=` callers.

Session 1214 verified-greppable surface area was **21 truly bare no-arg instantiations across 6 active files**. Walked all 21 + 1 expanded scope target through 8 PRs:

- **Phase A**: archived dead `gpt-3.5-turbo` demo file (not live-imported).
- **Phase B**: 6 factory swaps (`OpenAI()` → `get_openai_client()`) + 15 dead-code removals (vestigial `AsyncOpenAI()` instantiations whose `client` variable was never invoked — actual dispatch flows through `agent_llm_integration.generate_for_agent`) + 1 async factory infrastructure PR (`get_async_openai_client()`) + 1 central swap (`OpenAIProvider.__init__`).

**Net: 22 × 600s SDK timeout footguns eliminated. 50+ lines of vestigial dead code gone. Async factory now available for future migrations.**

Per Chris's session-open ask, also created **`OpenAI Call Site Catalog — Session 1214`** as a pinned deliverable in the Donkey Betz workspace (id `bb775acb-…`, category Platform Capability Audit). Catalog grew from 6.3KB seed → 10.9KB live with per-callsite entries logged on every PR close.

## Session Manifest

### PRs merged (8 total)

| # | Title | Commit | What |
|---|---|---|---|
| **#2486** | chore(session-1214): Phase A — archive MAKE_MONEY_NOW_WITH_APIS | `98297ab3` | Moved `ai_core/MAKE_MONEY_NOW_WITH_APIS.py` → `archive/old_experiments/`. Pre-platform demo, never live-imported, hardcoded `gpt-3.5-turbo` + bare `openai.api_key` module-level. Per "never delete" rule. |
| **#2487** | feat(session-1214): Phase B — intelligence/real_agents.py BaseAgent factory swap | `97aca26e` | `BaseAgent.__init__`: `OpenAI()` → `get_openai_client()`. Single base-class change propagates to 9 subclasses (ContentCreator, MLAnalytics, ImageGenerator, PublishingAutomation, DataAnalyst, SEOOptimizer, EmailMarketing, SocialMediaScheduler, MarketResearch). |
| **#2488** | feat(session-1214): Phase B PR #2 — agent_execution_pipeline.py factory swap (3 sites) | `cc5a18b4` | Module-level cache (L19) + `ContentCreatorAgent.__init__` (L35) + dynamic `RegistryAgent.__init__` (L306). Widened module-level `except` to `(ImportError, RuntimeError)` to preserve no-key fallback. |
| **#2489** | feat(session-1214): Phase B PR #3 — agent_factory.py factory swap (2 sites) | `<unchecked>` | Fallback `BaseAgent` (L26, only used if `from .real_agents import BaseAgent` fails) + `UnifiedAgentFactory.__init__` (L75). Added narrow `try/except RuntimeError` to preserve `use_real_apis=True` + no-key fallback. |
| **#2490** | feat(session-1214): Phase B PR #4 — add get_async_openai_client() factory variant | `<unchecked>` | Infrastructure: mirrors `get_openai_client()` for `AsyncOpenAI` with separate `_ASYNC_CLIENT_CACHE` dict + lock. Same forbidden-kwargs guard, same 20/90/60/60s timeouts, same RuntimeError-on-no-key. Unblocked PR #5-7. |
| **#2491** | feat(session-1214): Phase B PR #5 — remove 11 vestigial AsyncOpenAI() from real_work_delivery_engine.py | `<unchecked>` | Dead-code removal: all 11 `client = openai.AsyncOpenAI()` instantiations + `import openai`. `grep "client\."` returns 0 matches; actual dispatch routes through `agent_llm_integration.generate_for_agent`. |
| **#2492** | feat(session-1214): Phase B PR #6 — remove 4 vestigial AsyncOpenAI() from ai_proposal_engine + real_client_acquisition | `<unchecked>` | Same dead-code pattern as PR #5. 3 + 1 instantiations + 2 `import openai` lines removed across 2 sibling files. |
| **#2493** | feat(session-1214): Phase B PR #7 — agent_llm_integration.py OpenAIProvider factory swap | `<unchecked>` | The central indirect-dispatch surface for everything PR #5+#6 cleaned. `OpenAIProvider.__init__`: `openai.AsyncOpenAI(api_key=self.api_key)` → `get_async_openai_client(api_key=self.api_key)`. Dropped stale openai-v0.x `openai.api_key = self.api_key` module mutation. Closes original Session 1213 scope + 1 expanded target. |

### Deliverables created / updated

| ID | Action | Result |
|---|---|---|
| `bb775acb-5805-4561-901f-497d2db2add9` | `deliverable_tool.create` + 7 × `append` calls | "OpenAI Call Site Catalog — Session 1214". Category renamed from default to **Platform Capability Audit**. Pinned in Donkey Betz workspace. Final size: 10,871 chars. Contains: overview + methodology + verified counts + 5-phase plan + 7 per-callsite/PR entries. |
| `2b9aa447-c0c9-4ff3-8483-f92257eb0fcb` | (no action this session) | Phase A+B complete against this spec. Phase C/D/E ongoing — status remains `accepted` for Session 1215+. |

## What shipped

### Phase A — archive dead caller

`ai_core/MAKE_MONEY_NOW_WITH_APIS.py` was the only active code site hardcoding `gpt-3.5-turbo` (lines 35, 69). Live-import check via `grep -r MAKE_MONEY_NOW_WITH_APIS *.py` returned **0 Python file matches** (only 3 doc references). Pre-platform demo script using openai-v0.x `openai.api_key = OPENAI_KEY` module-level pattern. Moved to `archive/old_experiments/` rather than deleted (per Chris's "never delete" corpus rule) or migrated to factory (would be churn for never-invoked code).

### Phase B — factory adoption + dead-code removal

**Verified bare-instantiation scope (vs Session 1213 estimate of 74):**

- Original session estimate of 74 was conservative — actual `^\s*(client|self\.client|openai_client|self\.openai_client)\s*=\s*(openai\.)?(Async)?OpenAI\(\s*\)` grep across active code found **21 truly bare no-arg instantiations** across 6 files.
- Expanded by 1 during PR #5 audit: `agent_llm_integration.py:38` had bare-with-kwargs (`AsyncOpenAI(api_key=self.api_key)`) — pattern not captured by no-arg grep but same 600s timeout footgun. Closed in PR #2493.

**Pattern A (factory swap, 6 sites):** `intelligence/real_agents.py` + `intelligence/agent_execution_pipeline.py` + `intelligence/agent_factory.py`. These use the constructed client (call `self.client.chat.completions.create(...)`), so the swap is mechanical: replace the constructor + preserve any conditional/fallback semantics with `try/except (ImportError, RuntimeError)` widening.

**Pattern B (dead-code removal, 15 sites):** `ai_core/agents/real_work_delivery_engine.py` (×11) + `ai_core/agents/ai_proposal_engine.py` (×3) + `ai_core/agents/real_client_acquisition.py` (×1). All have `client = openai.AsyncOpenAI()` at method scope but **never invoke `client`** — actual LLM dispatch routes through `agent_llm_integration.generate_for_agent()` (which itself was fixed in PR #2493). The local `client` was vestigial pre-integration code. Removing it (vs migrating to factory) eliminates the footgun without baking dead code into the factory's call surface and drops 3 `import openai` lines.

**Pattern C (central swap, 1 site + infrastructure):** `agent_llm_integration.py:38` (`OpenAIProvider.__init__`) is the actual dispatch surface for everything pattern B cleaned. Migrated to factory via `get_async_openai_client(api_key=self.api_key)` after PR #2490 added the async variant.

### `get_async_openai_client()` — async factory infrastructure (PR #2490)

New public function in `core/services/openai_client_factory.py`. Mirrors `get_openai_client()` exactly:

- **Type:** returns `AsyncOpenAI`
- **Cache:** separate `_ASYNC_CLIENT_CACHE` dict + `_ASYNC_CLIENT_CACHE_LOCK`. Same `(api_key, base_url)` key shape, but isolated store — `OpenAI` and `AsyncOpenAI` are not interchangeable; mixing in one dict invites silent "wrong type returned" bugs on later sync↔async refactors (Rigby's design call).
- **Contract:** 20/90/60/60s timeouts, 2 retries (shared constants), forbidden kwargs `(timeout, max_retries, api_key)`, `RuntimeError` at construction if no key.
- **Lifecycle:** process-global singleton — underlying `httpx.AsyncClient` is not explicitly `aclose()`'d (matches sync factory; pool dies with process). Documented inline.

## Known issues / follow-ons

### `OpenAIProvider.generate()` pre-existing bug (surfaced during PR #7 audit)

`ai_core/agents/agent_llm_integration.py:43-108` — the `generate()` method on `OpenAIProvider`:

- **L90:** `response = await AsyncLLMAdapter().chat(messages, **kwargs)` references undefined `messages` variable. Would raise `NameError` if invoked.
- **L92-97:** Subsequent access to `.output_text`, `.id`, `.usage` on what Pyright types as `str` (because `AsyncLLMAdapter.chat()` may return a string).
- **L77:** `kwargs` is rebound to a new dict, overwriting the `**kwargs` parameter.

The system survives in production because actual dispatch flows `AgentLLMIntegration.generate_for_agent → llm_provider.generate(...)` — but the live path appears to use `AsyncLLMAdapter` directly (not via `OpenAIProvider.generate`), so this broken code is effectively unreachable. **Out of Phase B scope.** Catalog flagged as `reasoning_contract: pre_existing_bug`. Rigby's recommendation: either delete (if truly unused) or fix + add a tiny unit smoke. Defer to Session 1215+.

### Pre-existing lint floor (not introduced this session)

- `Direct LLM SDK usage check`: 6 violations on main, same 6 on all branches. Files: `core/management/commands/extract_initiatives_from_survey.py:151`, `draft_repo_verifier_claims.py:162`, `survey_external_repo.py:157`, `core/agents/campaign_orchestrator_agent.py:660`, `core/services/curated_action_card_generator.py:245`, `scripts/one-off/rag_docs.py:47`. These should migrate to `core/services/llm_call_wrapper.py` per Session 1098 PR #1's pattern.
- `Repo Guardrails`: "platform inventory is stale" — pre-existing, not Phase B-induced.
- **GitHub Actions billing block** continues — all 8 PRs admin-merged through it (same pattern as Session 1211 #2479 + Session 1213 #2483). Local lints verified instead.

## 24h watch (none triggered by Phase B work)

Phase A+B changes are pure factory adoption + dead-code removal. No new behavior, no new beat schedule, no new runtime path. **No 24h watch checklist required.** Catalog deliverable is a static artifact in the workspace — no expiry or drift target.

## Open follow-ups (queue for Session 1215+)

| Priority | Item | Notes |
|---|---|---|
| **P1** | **Phase C** — `max_tokens=` → `max_completion_tokens=` per-callsite audit (~50-80 active files; 158 raw `max_tokens=` matches across 77 files including archive) | Not mechanical — per-site review needed to distinguish call kwargs from function signatures. Catalog will track each conversion. |
| **P1** | **Phase D** — `temperature=` audit (~86 sites per Session 1213 estimate). Strip/document-then-strip/conditional-for-non-reasoning. Decision per-site. | Forbidden for gpt-5.x reasoning models. |
| **P2** | **Phase E** — CI lint (sibling to `tools/check_direct_llm_calls.py`) + runtime guard in `openai_client_factory.py` behind `OPENAI_REASONING_GUARD={warn,strip,error}` env flag. | Burn-in `warn` mode first, escalate after Phase C+D close. |
| **P2** | **`OpenAIProvider.generate()` brokenness** — delete vs fix-and-smoke | Surfaced in PR #7 audit. Effectively unreachable in prod; safer to delete than maintain. |
| **P3** | **Stale-thread dispatcher** (`777d9cd8-…`, Session 1213 carryover) | ~$3.60/day savings, lean A (per-conversation `session_closed` flag). |
| **P3** | **Continue URC adoption to next 3 agents** (Session 1211 carryover) | 4 of ~10 done. Pattern stable. |
| **P3** | **System prompt + tool schema size reduction** (Session 1213 finding) | Non-smoke conversational turns still 35-68K tokens. No spec filed yet. |

## Session 1215 opener

**Spec deliverable still active:** `2b9aa447-c0c9-4ff3-8483-f92257eb0fcb` ("Spec: OpenAI Caller Alignment to gpt-5-mini Reasoning Contract"). Phase A+B complete; Phase C/D/E remain.

**Catalog deliverable to keep updated:** `bb775acb-5805-4561-901f-497d2db2add9` ("OpenAI Call Site Catalog — Session 1214"). Pinned in Donkey Betz workspace, category Platform Capability Audit. Append per-callsite entries on every Phase C/D PR close — schema per Rigby: `file:line | model | client pattern | params | what it does | reasoning_contract: {ok | needs_max_completion_tokens | needs_temp_strip | needs_both | moot_removed | moot_archived | unknown | pre_existing_bug} | migration: <PR # + summary>`.

**Lean for Phase C kickoff:** start with the **active call sites only** (filter `158 raw max_tokens=` matches by excluding archive/ + tests/ + function signatures). Group by file. Per-site review on whether the model literal is gpt-5.x (needs migration) vs non-reasoning (kwarg OK). Expect ~30-50 actual fixes across ~15-20 files.

**Pinned PA thread:** `pa-e37fe30dc7b941a6` (Session 1214). Rigby has full Phase A+B context in this thread. Spin a fresh thread for Session 1215 if you want a clean slate; otherwise continue here.

---

**Closes:** Phase A + Phase B of Session 1214 OpenAI caller alignment spec `2b9aa447-…`.
