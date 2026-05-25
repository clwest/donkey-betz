---
originating_session: 1002
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1002: Fix SpiderContextBuilder Under-utilization & PLATFORM_CONTEXT Inflation

**Date:** February 13, 2026
**Focus:** Replace static claims with real data in ContentWriterAgent to eliminate two root causes of fabrication

## Problem

Session 1001 grounded blogs with operational telemetry, but two fabrication root causes remained:

1. **SpiderContextBuilder under-utilization:** `SpiderContextBuilder.build_context_for_agent()` returns 12+ fields (`relevant_trends`, `discussions`, `articles`, `market_data`, `related_discussions`, `freshness`, etc.) but ContentWriterAgent read `spider_context.get('trends', [])` -- the WRONG KEY (should be `relevant_trends`). Result: spider data was **never injected** into blog prompts. All other fields (discussions, articles, market_data, related_discussions) were completely ignored.

2. **PLATFORM_CONTEXT inflation:** A 113-line, ~4,800 char, ~1,400 token STATIC string from `core/prompts/registry.py` listed every spider name, agent name, body system, sci-fi feature, and Discord command. GPT saw "77 spiders: TechCrunch, CoinGecko..." but received no actual data from those spiders, so it fabricated stories about them.

## Research: Agent Execution Model

Investigated how agents plan steps and execute tasks. Key findings:

- **No explicit step planning** -- Agents use a single-pass LLM tool-calling pattern, not multi-step planners. The LLM decides which tools to call in one API call.
- **Execution flow:** Task -> Build Rich Prompt -> Single LLM Call -> Execute Returned Tools -> Return AgentResult
- **WorkflowAgent is the only exception** -- iterates up to 5 turns for cross-agent orchestration via `delegate_to_agent`
- **Delegation is recursive** -- any agent can call `delegate_to_specialist` (max depth 3), routed deterministically via `AgentRouter`
- **Decision tracking (`record_decision`, `time_travel_session`) is passive** -- logs choices to `AgentSession`/`DecisionPoint` for debugging replay, does not control execution flow
- **Tool definitions control behavior** -- each agent class declares a `tools` list; the LLM sees these and decides which to invoke

## Changes (1 file)

### 1. New method: `_build_dynamic_platform_summary()` (~35 lines)

Replaces the static `PLATFORM_CONTEXT` injection. Queries live DB counts and returns a compact ~90-token summary:

| Query | Model | Data |
|-------|-------|------|
| Active agents | `Agent.objects.filter(is_active=True)` | Count |
| Active spiders (72h) | `SpiderData.objects.filter(created_at__gte=cutoff)` | Distinct spider_name count + total data points |
| System health | `HeartBeat.objects.order_by('-recorded_at').first()` | overall_status + health_score |

Output example:
```
## Platform Context (Live)
- Active agents: 212 | Data spiders active (72h): 77 | Data points collected: 16,266
- System health: healthy (score: 100.0)
- Infrastructure: Django + PostgreSQL + Redis + Celery

This is what you are part of. Do NOT list specific spider or agent names unless they appear in the research data below.
```

Falls back to a one-liner on exception: `"AI content platform with multiple agents, spiders, and services."`

### 2. New method: `_format_spider_intelligence()` (~100 lines)

Formats the full `spider_context` dict into citable markdown. Each section in its own try/except.

| Field | Format |
|-------|--------|
| `relevant_trends` | Up to 7: `- **{topic}** (score: {score}) (sources: {sources})` |
| `discussions` | Up to 5: `- {title} -- {source}` |
| `articles` | Up to 5: `- {title} -- {url}` |
| `market_data` | Summary + up to 3 crypto/stocks items with price and change |
| `related_discussions` | Up to 5: `- {title} -- {source}: {snippet[:120]}` |
| `freshness` | `Data quality: {quality}, covering last {hours}h, updated {timestamp}` |

Header: `## Spider Intelligence (Real-Time Data -- cite these specifically)`
Footer: `Reference these data points by name when writing. Do not invent additional spider findings.`
Soft cap: truncates body at 2,000 chars. Returns `""` if no data.

### 3. Replace PLATFORM_CONTEXT injection (was lines 272-274)

**Before:** Injected static `PLATFORM_CONTEXT` (~1,400 tokens listing every spider/agent name)
**After:** Calls `self._build_dynamic_platform_summary()` (~90 tokens of real counts)

### 4. Replace broken spider trends section (was lines 391-402)

**Before:** `spider_context.get('trends', [])` -- wrong key, never matched
**After:** `self._format_spider_intelligence(spider_context)` -- reads all 6 field types from SpiderContextBuilder

## Files Changed (1)

| File | Lines | Change |
|------|-------|--------|
| `core/agents/content_writer_agent.py` | +194, -14 | 2 new methods, 2 edit blocks replacing broken injection points |

No other files modified. `core/prompts/registry.py` and `base_agent.py` untouched -- `PLATFORM_CONTEXT` is still used by other agents/advisors/PA where the static listing is appropriate.

## Verification

- `python -c "import core.agents.content_writer_agent"` -- no import errors
- `_build_dynamic_platform_summary()` returns real counts (212 agents, 77 spiders, 16,266 data points, health 100.0)
- `_format_spider_intelligence()` correctly formats all 6 field types into citable markdown (764 chars for test sample)
- Empty spider context returns `""` (no injection when no data)
- PR #1123 merged to main

## Open Questions for Future Sessions

- **Are agents actually using their tools?** Single-pass LLM tool calling means the LLM decides -- no guarantee it calls the right tools. Could benefit from tool usage auditing.
- **WorkflowAgent multi-turn is the only planning mechanism** -- is this sufficient for complex tasks that need multiple research-then-write steps?
- **Spider data may still be empty at generation time** -- `_format_spider_intelligence()` gracefully returns `""`, but if SpiderContextBuilder returns no data (e.g., spiders haven't run recently), blogs still generate without spider intelligence. Need to verify spider scheduling feeds content pipeline.
- **Disconnected Dots Audit (Session 972)** -- ~200+ items remain. Agent output persistence, orphan endpoints, enrichment data loss still open.
