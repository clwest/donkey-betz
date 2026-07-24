# Session 2929 — A1 Fold Remediation (BaseBusinessResearchAgent)

**Closed:** 2026-07-24
**HEAD at close:** `1465df616` (after PR #3493 merge)
**Wrapper pin at open:** `pa-9f6a63e5c2be45a4`
**Session arc:** Chris-ratified Option A1 (BaseBusinessResearchAgent Content-Shape FAIL Fold remediation) → root-cause pivoted mid-session (S2928 handoff description was inaccurate) → Path 2 (bundle CompetitorAnalysisAgent parallel fix) proposed → Path 2 abandoned mid-session after ORM verification proved CompetitorAnalysisAgent doesn't exhibit the FAIL → Path 1 revised (base-class-only) shipped as PR #3493.

---

## What shipped

**PR #3493** — `fix(agents): S2929 A1 — BaseBusinessResearchAgent Content-Shape FAIL Fold remediation`

- `core/agents/business/base_business_research_agent.py` — 2 code changes:
  1. **:685-698** — polymorphic content extraction in the `_execute_gpt_loop` fallback. Pre-S2929 used `hasattr(last_msg, 'content')` which was always False for dict-shaped tool response messages (the most common `messages[-1]` at loop exit). Now handles both dict (`.get('content')`) and object (`getattr(..., 'content', None)`) shapes.
  2. **:485-517** — fail-loud gate before the success-path `AgentResult` return. If `data['analysis']` is empty / `'{}'` / `'None'` (whitespace-stripped per Rigby T2 nit) AND data was gathered, return `success=False` with an explicit error naming the specific `synthesize_*` tool that didn't fire.
- `core/tests/test_base_business_research_agent_synthesis_gate.py` (NEW) — 5 tests, all pass:
  - `test_fallback_extracts_content_from_dict_tool_message`
  - `test_fallback_extracts_content_from_object_shaped_message` (Rigby T2 nit)
  - `test_fail_loud_when_synthesis_empty_with_data_gathered`
  - `test_fail_loud_when_analysis_is_empty_dict_string`
  - `test_success_when_synthesis_has_analysis`
- `docs/INDEX.md` — refreshed autogen (was S2908-stamped from prior close cascade lag).

Merge commit `1465df616`. Recycle post-merge: clean (5 fresh workers + beat, no surviving old PIDs).

---

## Root-cause pivots (2 during session)

### Pivot 1 — the S2928 handoff shape description was wrong

Initial hypothesis (per S2928 handoff): `data.keys() == ['query']` (only 1 key). Actual ORM-verified shape of S2928 `marketing_strategy_agent` execution `1933ea98-c8a1-44ca-a0ef-7a673dd025f6`:

- `output_data['data']` has all 10 expected keys — `['analysis', 'data_points_analyzed', 'key_insights', 'project_name', 'query', 'raw_data', 'recommendations', 'research_type', 'saved_id', 'sources_used']`
- The actual FAIL signature: `data['analysis'] == '{}'` (string of empty dict, produced by `str(synthesis)` when `synthesis={}` at base class :494)
- `data_points_analyzed = 20` — data WAS gathered, but the `synthesize_marketing_strategy` tool was never called by GPT and the fallback couldn't rescue

Actual root cause: GPT-5.2 gathered data via 20 tool calls (spider_query + web_search) but never called `synthesize_*`. The fallback at :660-665 had a polymorphism bug that prevented content rescue. Empty synthesis then produced `str({}) = '{}'` in the success return.

### Pivot 2 — CompetitorAnalysisAgent (Fold's "1st instance") isn't actually broken

Chris ratified Path 2 (bundle CompetitorAnalysisAgent parallel fix). Before writing that code, ORM verification of 3 recent CompetitorAnalysisAgent executions (most recent 2026-07-24 04:30) showed:

- `data['analysis']` is a **dict** (not a flat string), containing:
  - `analysis['analysis']` — real markdown with QUALITY HEADER section
  - `analysis['raw_data']` — actual source data
  - `analysis['sources_used'] = 2`
  - `analysis['domain_relevance']` — real scoring dict
  - `analysis['data_points_analyzed'] = 14`
- All 8 expected top-level keys present, `run_status=success`
- Zero S2926-era CompetitorAnalysisAgent executions in the DB window (`2026-07-21` → `2026-07-23`)
- No recent code changes to `competitor_analysis_agent.py` that would have "fixed" a prior FAIL

**Conclusion:** the S2926 "1st instance" of the Fold appears to have been misclassified. CompetitorAnalysisAgent's `execute()` override has a fundamentally different synthesis architecture (`_synthesize_analysis()` method returning a dict), not the flat-string base class shape. It cannot exhibit the `data['analysis']='{}'` failure mode.

Chris D-verdict: revert to Path 1 revised (base-class-only fix). Flag the Fold ratification for governance review.

---

## Blast radius (verified via AGENT_MAP)

Post-fix E2E verify surfaced an additional routing finding: **the `content_strategy_agent` tool routes to `core.agents.strategy.ContentStrategyAgent`, NOT to `core.agents.business.content_strategy_agent.ContentStrategyAgent`** (the BaseBusinessResearchAgent subclass).

| Tool name | Class resolved via AGENT_MAP | Inherits BaseBusinessResearchAgent? | Fix covers? |
|-----------|------------------------------|-------------------------------------|-------------|
| `marketing_strategy_agent` | `core.agents.business.MarketingStrategyAgent` | ✅ Yes (unchanged execute) | ✅ Fix applies |
| `content_strategy_agent` | `core.agents.strategy.ContentStrategyAgent` | ❌ No | ❌ Not affected |
| `brand_strategy_agent` | `core.agents.business.BrandStrategyAgent` | ✅ Yes (has own execute() override) | ❌ Overrides skip base class path |
| `competitor_analysis_agent` | `core.agents.business.CompetitorAnalysisAgent` | ✅ Yes (has own execute() override) | ❌ Overrides skip base class path |
| `customer_research_agent` | `core.agents.business.CustomerResearchAgent` | ✅ Yes (has own execute() override) | ❌ Overrides skip base class path |

**Real blast radius: `MarketingStrategyAgent` only.** The `business.ContentStrategyAgent` subclass exists in the codebase but is never dispatched via tool routing — effectively dead code from the tool-dispatch surface. This is a substrate finding worth flagging for the docs restructuring arc or a follow-up dead-code audit.

---

## Post-merge live-dispatch (per PLAYBOOK-7.4.4)

Merge commit `1465df616` recycled clean. Two dispatches via Rigby:

1. **`content_strategy_agent` — execution `21460668-243b-45a0-abf1-ab8e0304c258`** (10.3s completion). Data shape `['recommendations', 'task', 'tool_results']` with `analysis=None`. This is the `strategy.ContentStrategyAgent` code path — not covered by my fix. Not a valid E2E test target.
2. **`marketing_strategy_agent` — execution `86be25b0-71c1-4d5f-92b8-3c018cc7bed4`** (101.8s completion). All 14 expected keys present. `data['analysis']` = 12,651 chars of real markdown (opens with "### Target Audience Summary\n- Primary audience segments..."). `run_status=success`. **GATE PASSED — positive path unchanged by fix.**

The fail-loud gate branch wasn't triggered in production because GPT successfully called `synthesize_marketing_strategy` this time. Invariant tests cover both branches.

---

## Governance finding — S2928 Fold ratification over-counted

Per the corroboration-ladder Chris uses (Playbook §14.2 default two-trigger; four-trigger for stricter arcs), the S2928 Content-Shape FAIL Fold was ratified 2/2:

- **1st instance:** S2926 CompetitorAnalysisAgent — **appears misclassified** (see Pivot 2 above; current + historical DB state shows well-formed dict output, no `'{}'` failure mode reproducible)
- **2nd instance:** S2928 MarketingStrategyAgent — **real and confirmed** (execution `1933ea98-...` in DB with `data['analysis']='{}'`)

Actual verified instance count: **1**. Under the ratification threshold. Options:

- **Option R1 (de-ratify):** Move the Fold back to candidate status; require 2nd real instance before re-ratifying. Formal but honest.
- **Option R2 (re-scope Fold class):** Narrow the Fold's class scope from "BaseBusinessResearchAgent subclasses" to "BaseBusinessResearchAgent subclasses inheriting base execute()" — that's exactly one class (`MarketingStrategyAgent`), and the fold-of-one becomes a specific bug that the S2929 fix closes. Cleaner artifact.
- **Option R3 (defer):** Leave as-is; watch for future BaseBusinessResearchAgent subclass FAILs. Least effort but leaves the ratification substrate over-stated.

**Recommendation for S2930:** Chris D-verdict R1 vs R2. Not blocking S2929 close.

---

## What's left in the ledger

- **Rigby Tool Gap Ledger deliverable `5c84e75a-...`** — no new entries this session. Existing S2928 entry (`orm_inspect_tool` allowlist expansion for AgentExecution + AgentResult) still valid. I fell back to direct Django shell for ORM inspection during this session — the gap is real and Rigby's honest surface would be improved by closing it.
- **BaseBusinessResearchAgent Fold ratified deliverable `5703a6c8-9bfa-4b11-81cc-baff7c90b3d5`** — status now "remediation shipped for MarketingStrategyAgent surface" (PR #3493). Governance status pending R1/R2/R3 above.
- **CompetitorAnalysisAgent hardening candidate** — deferred by Chris (no evidence of current FAIL). If future runs surface a real FAIL there, revisit as a separate deliberation with real evidence.
- **`content_strategy_agent` tool-to-class routing anomaly** — S2929 substrate finding. `business.ContentStrategyAgent` is unreachable via tool dispatch. Candidate for dead-code audit or explicit deprecation. Consider as an item for the docs restructuring arc scoping session.

---

## Constraints / anti-patterns for S2930

**S2929 additions (all 1st-instance — require corroborating trigger before promotion):**

- **No "S2928-style handoff shape misclassification" Fold promotion without 2nd instance.** 1st (S2929 discovered S2928 handoff described `data.keys()=['query']` when actual shape had all 10 keys). Watch for 2nd handoff-description-vs-reality drift in future sessions.
- **No "tool-to-class routing anomaly" Fold promotion without 2nd instance.** 1st (S2929 `content_strategy_agent` → `strategy.ContentStrategyAgent` instead of `business.ContentStrategyAgent`). Watch for 2nd cross-namespace dispatch collision.
- **No "Fold ratification over-count via unverified handoff description" Fold promotion without 2nd instance.** 1st (S2929 S2928 Fold 2/2 → verified 1/1 after ORM check). Watch for 2nd ratification-quality issue in future close cascades.

**S2928 and earlier forbidden entries carry forward per prior handoffs.**

---

## Session evidence pointers

- **PR:** [#3493](https://github.com/clwest/donkey-betz-platform/pull/3493) — merged at `1465df616`
- **Fixed code:** `core/agents/business/base_business_research_agent.py:485-517` + `:685-698`
- **Regression tests:** `core/tests/test_base_business_research_agent_synthesis_gate.py` (5 tests, all pass)
- **ORM evidence — the S2928 FAIL:** execution `1933ea98-c8a1-44ca-a0ef-7a673dd025f6` (MarketingStrategyAgent, `data['analysis']='{}'`)
- **ORM evidence — CompetitorAnalysisAgent NOT failing:** execution `7f9fdae3-ce64-422b-96c3-d0303836000c` (well-formed dict output)
- **E2E verify — positive path unchanged:** execution `86be25b0-71c1-4d5f-92b8-3c018cc7bed4` (MarketingStrategyAgent, 12,651-char real analysis)
- **E2E verify — wrong routing surfaced:** execution `21460668-243b-45a0-abf1-ab8e0304c258` (content_strategy_agent tool → strategy.ContentStrategyAgent)
- **Rigby T2 SIGN transcripts:** conversation `pa-9f6a63e5c2be45a4`

---

## Handoff to S2930 — Chris decision surface

1. **Governance R1/R2/R3** for the S2928 Fold ratification (see above).
2. **S2929 forbidden-entry additions** — should any of the 3 new 1st-instance observations open substrate arcs? Chris directive is engineering-bias, so likely defer to corroborating trigger.
3. **Next arc scope** — S2930 opens with the same 5-option surface as S2929 opened: A (net-new engineering) / B (Slice 5-hardening) / C (Slice 6 sweep continuation) / D (docs restructuring arc — unblocked) / E (Rigby tool-gap ledger slate).
