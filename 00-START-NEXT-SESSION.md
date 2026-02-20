# Session 1041 - Start Here

**Previous Sessions:** 1040 (Anti-Hallucination Fixes + Stage 4 ThinkingAgent Fix + PA Tool + Celery OOM), 1039 (Tenant Model + Agent Hallucination Discovery), 1038 (DynamicPersonaAgent), 1037 (Initiative Pipeline Fix)
**Date:** February 19, 2026
**Status:** 92 Agents | 79 Spiders | 25 Advisors | **PA function calling LIVE (GPT-5.2)** | **All 218 agent personas routable** | **Tenant model Phase 1 landed** | 8 ACTIVE initiatives | 28 COMPLETED

---

## Session 1040 — What Happened

### 1. Agent Data Hallucination Fix (PR #1330)

Agents in initiative conversations were fabricating dates and statistics (e.g. "data shows 0 discussions on Oct 15, 2023") when spider data was actually fresh (30K+ records). Three interconnected fixes deployed:

**a) Anti-hallucination guard in system prompt** (`core/tasks.py:7768`)
- Agents now told: "If no == REAL-WORLD INTELLIGENCE == section appears below, you have NO spider data. Say 'No data available' — do NOT invent dates, counts, statistics."
- Updated citation guideline to require source AND date when citing data.

**b) Timestamps + related_content surfacing** (`core/tasks.py:7675-7714`)
- REAL-WORLD INTELLIGENCE header now includes retrieval timestamp.
- Discussion items show `(collected: 2026-02-18T...)` dates.
- `related_content` from `search_spider_data()` (semantic/keyword fallback) was **silently dropped** — now surfaced with source attribution and timestamps.

**c) Broader spider intelligence matching** (`core/services/spider_intelligence.py:1040-1115`)
- Expanded all 5 keyword categories with more terms.
- Added 2 new categories: `is_business` (customer, analytics, retention, growth...) and `is_news` (trend, announcement, research...).
- Bumped `search_spider_data` limit from 3 → 5.
- **Critical fallback**: when NO category matches, semantic search results are promoted into `related_discussions` so the spider_parts builder always picks them up.

### 2. Stage 4 ThinkingAgent Contamination Fix (PR #1331)

**Root cause:** Session 912 replaced ThinkingAgent with ContentWriterAgent in `generate_initiative_stage_document` (auto_pipeline path) because ThinkingAgent dumps system diagnostics instead of reviewing content. But `conversation_initiative_pipeline.py` was **never updated** — still used ThinkingAgent for review/polish stages.

**Impact:** 3/26 completed initiative Stage 4 docs were contaminated with "System scan for the last 24 hours..." metrics dumps instead of actual review content.

**Fix:** Replaced all 4 ThinkingAgent references in `conversation_initiative_pipeline.py` with ContentWriterAgent (content types: strategy, analysis, research, document).

### 3. PA `stage_document` Tool (PR #1331)

PA got stuck in a gibberish loop ("Tool call.Let's call.Ok.No...") when user asked to "Open the Stage 4 doc" because no tool existed to fetch stage document content.

**Fix:** Added `stage_document` action to `initiative_tool` in both `tool_dispatcher.py` and `pa_tool_schemas.py`. Accepts `document_id` or `initiative_id + stage` combo, returns full SelfBlog content.

### 4. Celery-Content OOM Fix (PR #1332)

celery-content kept crashing with 25+ completed initiatives driving heavy LLM tasks.

**Fix:** Moved 5 heaviest tasks from `content` queue to `long_running` (300MB/child, 3 concurrency):
- `generate_initiative_stage_document`
- `execute_approved_artifacts`
- `generate_pending_reviews`
- `execute_initiative_stage_task`
- `execute_dream_implementations`

Reduced `max-tasks-per-child` from 5 → 2 on celery-content for more aggressive recycling.

### Commits
| Commit | Description |
|--------|-------------|
| 457e03f3 | fix: prevent agent data hallucination in initiative conversations |
| 5a20f146 | fix: replace ThinkingAgent in conversation pipeline + add stage_document PA tool |
| 3e807b98 | fix: move 5 heavy tasks off celery-content to stop OOM crashes |

---

## Current System Health (post-Session 1040)

| Metric | Value |
|--------|-------|
| PA routing | **GPT-5.2 function calling** (`PA_USE_FUNCTION_CALLING=true`) |
| Agents routable | **All 218** (82 AGENT_MAP + 139 DynamicPersonaAgent + 2 blocked) |
| Initiatives | **8 ACTIVE**, 28 COMPLETED, 2 TRIAGE (38 total) |
| Content worker | **250MB limit, 2-task recycle**, 5 heavy tasks moved to long_running |
| Long-running worker | Now handles initiative stage docs, artifacts, reviews, dream implementations |
| Tenant model | **Phase 1 merged** (migration applied) |
| Spider data | **30,173 records** (Jan 22 – Feb 19, 2026), 11,957 in last 7 days |
| Anti-hallucination | **LIVE** — guard in system prompt + timestamps + broader matching |
| PA tools | **stage_document** action added to initiative_tool |

---

## Known Issues / Open Items

### Ghost Celery Dispatcher — HARD-BLOCKED
`execute_remediation_tasks` triggered 41x/48h from unknown source. All 6 execution + assignment paths blocked. Root cause still unknown.

### WorkflowAgent / TrendAnalysisAgent Timeout Risk
Both take 43-44min to complete. Celery timeout is 45min. They PASS but have no margin.

### Railway Cost
User hit $1,200/month limit, bumped to $1,500. Schedule throttling (Session 1034) + media guards should reduce costs.

### 3 Contaminated Stage 4 Docs (Session 1040)
These completed initiatives have Stage 4 docs filled with ThinkingAgent system diagnostics instead of real content. They could be regenerated if needed:
- "Navigating Time-Sensitive Securities Fraud Alerts"
- "Revise and Enhance Class Action Landscape Briefing"
- "Revise Florida High School Soccer Playoff Broadcast Information"

### Future Improvements
- Tenant Phases 2-3 (budget enforcement, customer API endpoints, TenantScopeMixin)
- Profile consolidation (Phase 4 model dedup)
- Initiative data validation gate (check data source exists before creating data-dependent initiatives)
- Build real backends for AgentsPage channels/tools/templates tabs
- Score remaining ~3,500 deliverables
- Enhance remaining ~111 `needs_enhancement` blogs
- Consider removing legacy keyword router once function calling is proven stable

---

## Verify Before Starting

```bash
# 1. Check celery-content not OOMing after task redistribution
railway logs -n 200 2>&1 | grep -i 'OOM\|killed\|memory'

# 2. Verify anti-hallucination guard is working
railway run python manage.py shell -c "
from core.services.spider_intelligence import SpiderIntelligenceService
svc = SpiderIntelligenceService()
insights = svc.get_insights_for_prompt('customer behavior signals')
print(f'related_content: {len(insights.get(\"related_content\", []))} items')
print(f'suggestions: {insights.get(\"suggestions\", [])}')
"

# 3. Verify PA stage_document tool works
railway run python manage.py shell -c "
from core.services.tool_dispatcher import ToolDispatcher
td = ToolDispatcher()
# Should return full document content
print('stage_document action registered:', hasattr(td, '_handle_initiative'))
"

# 4. Verify ThinkingAgent removed from conversation pipeline
railway run python manage.py shell -c "
from core.services.conversation_initiative_pipeline import CONTENT_TYPE_STAGES
for ct, stages in CONTENT_TYPE_STAGES.items():
    for sn, si in stages.items():
        for t in si.get('tasks', []):
            if t.get('agent') == 'ThinkingAgent':
                print(f'STILL HAS ThinkingAgent: {ct} Stage {sn}')
print('Check complete')
"
```

---

## Critical Patterns & Gotchas

**Anti-hallucination guard (Session 1040):** Conversation system prompt now includes CRITICAL instruction: if no REAL-WORLD INTELLIGENCE section appears, agent must say "No data available" and never fabricate. Spider context header includes retrieval timestamp. `related_content` from semantic search is now surfaced (was silently dropped).

**ThinkingAgent banned from document generation:** ThinkingAgent returns system diagnostics instead of reviewing content. Session 912 fixed `generate_initiative_stage_document` (auto_pipeline). Session 1040 fixed `conversation_initiative_pipeline.py`. If adding new pipelines, NEVER use ThinkingAgent for content tasks.

**Celery-content task routing (Session 1040):** 5 heavy tasks moved from content → long_running queue. Content queue now only has: deliberation, blog gen, auto-progression, scoring, publishing. If OOM returns again, next step is splitting deliberation into chained tasks.

**PA stage_document tool (Session 1040):** `initiative_tool(action='stage_document', id=<initiative_uuid>, stage=4)` or `initiative_tool(action='stage_document', document_id=<doc_uuid>)` returns full SelfBlog content.

**Tenant model (Session 1039):** `Tenant` in `core/models_tenant.py`, registered via `core/models/__init__.py`. All FKs nullable — no enforcement yet (Phase 2-3).

**DynamicPersonaAgent (Session 1038):** `AgentRouter.route()` falls back to `DynamicPersonaAgent` when `AGENT_MAP` lookup fails. Has `web_search` + `spider_query` tools only.

**PA function calling (Session 1036):** `PA_USE_FUNCTION_CALLING=true` env var. Agentic loop in `_run_agentic_loop()` — max 5 iterations, GPT-5.2 decides tool calls.

**Dual dispatch block (Session 1032):** CodeGeneratorAgent and AudioAgent blocked in BOTH `execute_agent_task` AND `AgentRouter.route()`.

**6 remediation paths ALL blocked (Session 1031):** execute_remediation_tasks, run_autonomous_remediation_cycle, assign_and_execute_remediation, run_agent_remediation_batch, assign_open_findings_to_agents, discover_and_import_audits.
