# SESSION 2932 — A2: ContentStrategyAgent consolidation + strategy-arch fail-loud gate

**Date:** 2026-07-24
**Merge SHA:** `71234d547`
**PR:** [#3499](https://github.com/clwest/donkey-betz-platform/pull/3499)
**Shape:** Net-new engineering — 30-line diff surface + 4 new tests, ~45 min end-to-end.
**Ratification:** none (implementation session, no governance decisions).

---

## What shipped

Two `ContentStrategyAgent` classes existed side-by-side pre-S2932. `core.agents.business.ContentStrategyAgent` (`BaseBusinessResearchAgent`, 123 LOC) was unreachable via live PA tool dispatch — only imported by the dead `personal_ai_assistant_enhanced` handler (Session 184 refactor left it dead in prod) and one base-class regression test — so it carried the S2929 fail-loud gate while the `AGENT_MAP`-registered `core.agents.strategy.ContentStrategyAgent` (`BaseAgent`, 799 LOC — ML + niche strategies + structured tools + Deliverable persistence) silently returned `success=True` with `"Generated 0 content recommendations"` when tool calls came back empty.

**Consolidation onto the reachable strategy class + S2929-semantic backport:**

1. **Deleted** `core/agents/business/content_strategy_agent.py`.
2. **Updated 6 import/config sites** (`business/__init__`, `agents/__init__`, `epa_handlers_tools`, `policy_context`, `models_llm_routing`, `discord_training_spider`) to remove the `BusinessContentStrategyAgent` alias/entries. `agents/__init__` business-research count 5→4.
3. **Retargeted** the `BaseBusinessResearchAgent` gate test to `MarketingStrategyAgent` — the only remaining concrete BBRA subclass (verified: `CompetitorAnalysisAgent`, `CustomerResearchAgent`, `BrandStrategyAgent` all inherit `BaseAgent`).
4. **Added** the strategy-arch analog of the S2929 gate to `strategy.ContentStrategyAgent.execute()` — when tool calls dispatch but every call returns empty recommendations, return `success=False` instead of `success=True` with "Generated 0". Scoped strictly to the `tool_calls` branch per Rigby T0 SIGN concern #1 — the conversational branch stays `success=True` since narrative text is a legitimate strategy output.
5. **Added** `core/tests/test_content_strategy_agent_fail_loud_gate.py` — 4 tests (fail-loud on empty recommendations, fail-loud on no recommendations key, positive path, conversational-branch untouched).

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

- PR #3499 recycled clean at `sha=71234d547` via `make recycle-all`.
- Rigby verification triad:
  - `orm_inspect_tool list_models` — platform loads clean (12 models returned).
  - `orm_inspect_tool count_by Agent name=ContentStrategyAgent` — exactly **1 row** (no duplicate).
  - `content_strategy_agent` dispatch — envelope `{task_id: c7198928-47c8-4212-b431-ae0387c7e592, mode: async, agent: 'ContentStrategyAgent'}`. Follow-up `job_status` poll returned `status: completed` — end-to-end path healthy through the consolidated class.

## Rigby T0 SIGN highlights

**Verdict:** AGREE (untool-verified — Rigby self-flagged). Three concerns:

1. **[APPLIED]** Scope the new gate strictly to the `tool_calls` branch — the conversational branch handles legitimate narrative strategy output and must not fail-loud on missing recommendations.
2. **[APPLIED]** Update import sites (specifically `_handle_content_strategy_agent`) to avoid parse/import-time breaks after deleting the duplicate.
3. **[VERIFIED + APPLIED]** BBRA gate test needs a concrete subclass — Rigby suggested `CompetitorAnalysisAgent`; Claude verified it inherits `BaseAgent`, not `BaseBusinessResearchAgent`. Swapped to `MarketingStrategyAgent` (the only remaining concrete BBRA subclass) and updated the error-message assertion from `synthesize_content_strategy` → `synthesize_marketing_strategy`.

## Governance

None this session. D6 moratorium unchanged. Zero new forbidden-entry candidates. Zero Fold candidates.

## Rigby Tool Gap Ledger

No new entries. `#33`+`#34` remain **RESOLVED** at S2931 PR #3497.

## Deferred

- Pre-existing `test_content_strategy_agent_persistence.test_conversational_response_persists_deliverable` failure — fails on both HEAD and this branch (verified via `git stash`). Not introduced by this ship. Belongs to the bundled dev-env drift slate.
- Dead-handler cleanup in `epa_handlers_tools._handle_content_strategy_agent` — the strategy version's `execute()` signature (4 args) mismatches the handler's 2-arg call, but the handler is only reachable via the dead `personal_ai_assistant_enhanced.py` (Session 184 refactor removed it from prod). Explicit non-scope for this ship per "don't clean up beyond what the task requires."

## Files changed

```
 M ai_core/spiders/specialized/discord_training_spider.py
 M core/agents/__init__.py
 M core/agents/business/__init__.py
 D core/agents/business/content_strategy_agent.py
 M core/agents/strategy/content_strategy_agent.py
 M core/epa_handlers_tools.py
 M core/models_llm_routing.py
 M core/services/policy_context.py
 M core/tests/test_base_business_research_agent_synthesis_gate.py
 A core/tests/test_content_strategy_agent_fail_loud_gate.py
```

10 files changed, 202 insertions(+), 141 deletions(-).
