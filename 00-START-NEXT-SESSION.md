# Session 1040 - Start Here

**Previous Sessions:** 1039 (Tenant Model + Celery OOM Fix + Agent Hallucination Discovery), 1038 (DynamicPersonaAgent), 1037 (Initiative Pipeline Fix), 1036 (PA Function Calling Hardening)
**Date:** February 19, 2026
**Status:** 92 Agents | 79 Spiders | 25 Advisors | **PA function calling LIVE (GPT-5.2)** | **All 218 agent personas routable** | **Tenant model foundation landed (Phase 1/3)** | 19 ACTIVE initiatives

---

## Session 1039 — What Happened

### Tenant Model & Customer Access Foundation (Phase 1 of 3)

Created multi-tenant infrastructure for future customer-facing access control. PR #1327 merged to main.

**New model:** `Tenant` (`core/models_tenant.py`) — UUID PK, name, slug, owner FK, subscription_tier, monthly cost guardrails, features JSONField, is_active.

**Modified models:**
- `UnifiedUser` — added nullable `tenant` FK + `customer_role` (viewer/user/org_admin)
- `AgentExecution` — added nullable `tenant` FK for cost attribution
- `CostTracking` — added nullable `tenant` FK for cost attribution
- `EnhancedUserProfile` — added nullable `tenant` FK
- `Budget` — added `tenant`/`user` scope choices + nullable FKs

**Profile cleanup:**
- Deleted dead duplicate `core/models/user_profile.py` (imported Django `User` not `UnifiedUser`, nothing referenced it)
- Added `EnhancedUserProfile` auto-create in user post_save signal handler

**Migration:** `0249_session_1039_tenant_model_and_customer_access` — all FKs nullable, non-destructive.

### Celery-Content OOM Fix

`celery-content` worker was OOMing on Railway (user received 2 OOM emails). Root cause: deliberation pipeline tasks use 80-120MB per task, but child limit was only 150MB.

**Fix:** Bumped `--max-memory-per-child` from 150MB → 250MB and `--max-tasks-per-child` from 10 → 5. Peak: 200MB parent + 250MB child = 450MB, fits Railway 512MB with 62MB headroom.

### Agent Hallucination Discovery (THE BIG ISSUE)

User spotted agents in initiative conversations fabricating data dates and claiming no data exists when spider data is actually fresh. This is the **#1 priority for Session 1040**.

### Commits
| Commit | Description |
|--------|-------------|
| 17dc0664 | feat: add Tenant model and customer access foundation (Phase 1 of 3) |
| bdf1e0f2 | fix: bump celery-content memory 150→250MB and recycle 10→5 tasks |
| 979c6911 | docs: Session 1039 handoff |

---

## TOP PRIORITY: Agent Data Hallucination in Initiative Conversations

### The Problem

Agents in initiative-triggered conversations are **fabricating data dates and claiming no data exists** when the spider network actually has 30,023 records (11,872 from the last 7 days alone).

**Example:** CodeGeneratorAgent + Data Scientist Pro conversation about "Summarize customer behavior signals from spider data":
- Agents claimed: "spider dataset shows 0 discussions collected on Oct 15, 2023 — ~28 months old"
- Reality: Spider data ranges from Jan 22, 2026 to Feb 19, 2026 (today), 30K+ records, 11K+ in last 7 days
- The date "Oct 15, 2023" is **completely fabricated** — no spider record has that timestamp

### Root Cause Analysis (4 interconnected issues — PA independently confirmed #1)

**1. Agents assigned tasks they have no tools for** (PA confirmed via agent introspection)
- CodeGeneratorAgent only has codebase tools (read_file, write_file, edit_file, generate_code) — **cannot query spider data**
- Data Scientist Pro has **no attached toolset** at all
- The conversation orchestrator asked them to "summarize recent spider data" without injecting any data
- Agents hallucinated because they literally had nothing to work with
- **PA recommendation:** orchestrator should fetch data first, inject `NOW_UTC=...` + actual records, then ask agent to summarize only what's provided

**2. Spider intelligence keyword matching is too narrow** (`core/services/spider_intelligence.py:1040`)
- `get_insights_for_prompt()` only matches 5 categories: tech, crypto, finance, jobs, design
- "Customer behavior signals" matches NONE of them
- So `spider_context` injected into the conversation system prompt is **empty**

**3. No data provenance / timestamps in agent context** (`core/tasks.py:7674-7695`)
- When spider data IS injected, the `spider_parts` list shows titles and summaries only
- Never includes "this data is from [date]" or "collected [N] hours ago"
- Agents can't distinguish fresh data from stale data, so they hallucinate dates

**4. Initiative pipeline creates tasks without validating data availability**
- Initiative "Summarize customer behavior signals from spider data" was auto-created from a conversation decision
- Pipeline ran it through all 5 stages without checking if any spider actually collects "customer behavior" data
- Result: agents argue for 7 messages about data that doesn't exist in the format they expect

### Files to Fix

| File | Issue | Fix |
|------|-------|-----|
| `core/services/spider_intelligence.py:1040` | `get_insights_for_prompt()` keyword matching too narrow | Add broader category matching OR use embedding similarity instead of keyword lists |
| `core/tasks.py:7674-7695` | Spider context has no timestamps | Include `created_at` dates on injected spider items so agents know data freshness |
| `core/tasks.py:7731-7754` | System prompt doesn't tell agents what to do when no data is available | Add explicit instruction: "If no spider data was injected below, state 'No data available' — do NOT fabricate dates or statistics" |
| `core/tasks.py` (conversation orchestrator) | No data availability pre-check | Before starting a conversation about data, verify the data actually exists |

### Proposed Fix Order

1. **Quick win — anti-hallucination guard in system prompt** (5 min): Add to the conversation system prompt: "If no == REAL-WORLD INTELLIGENCE == section appears below, you have NO spider data. Say 'No data available' — do NOT invent dates, counts, or statistics."
2. **Add timestamps to spider context** (15 min): When building `spider_parts`, include `created_at` on each item
3. **Broaden spider intelligence matching** (30 min): Add embedding-based or broader keyword matching to `get_insights_for_prompt()`
4. **Initiative data validation gate** (future): Before creating an initiative about data, check the data source exists

---

## Current System Health (post-Session 1039)

| Metric | Value |
|--------|-------|
| PA routing | **GPT-5.2 function calling** (`PA_USE_FUNCTION_CALLING=true`) |
| Agents routable | **All 218** (82 AGENT_MAP + 139 DynamicPersonaAgent + 2 blocked) |
| Initiatives | **19 ACTIVE**, 8 COMPLETED, 0 TRIAGE |
| Content worker | **250MB limit, 5-task recycle** (was 150MB/10, OOMing) |
| Tenant model | **Phase 1 merged** (migration runs on next Railway deploy) |
| Agent health | 92.4% pass rate |
| Spider data | **30,023 records** (Jan 22 – Feb 19, 2026), 11,872 in last 7 days |

---

## Known Issues / Open Items

### Ghost Celery Dispatcher — HARD-BLOCKED
`execute_remediation_tasks` triggered 41x/48h from unknown source. All 6 execution + assignment paths blocked. Root cause still unknown.

### WorkflowAgent / TrendAnalysisAgent Timeout Risk
Both take 43-44min to complete. Celery timeout is 45min. They PASS but have no margin.

### Railway Cost
User hit $1,200/month limit, bumped to $1,500. Schedule throttling (Session 1034) + media guards should reduce costs.

### Future Improvements
- Tenant Phases 2-3 (budget enforcement, customer API endpoints, TenantScopeMixin)
- Profile consolidation (Phase 4 model dedup)
- Build real backends for AgentsPage channels/tools/templates tabs
- Score remaining ~3,500 deliverables
- Enhance remaining ~111 `needs_enhancement` blogs
- Consider removing legacy keyword router once function calling is proven stable

---

## Verify Before Starting

```bash
# 1. Check migration applied on Railway
railway run python manage.py shell -c "
from core.models_tenant import Tenant
from core.models import UnifiedUser
u = UnifiedUser.objects.first()
print(f'tenant={u.tenant}, customer_role={u.customer_role}')
print('Tenant model accessible: OK')
"

# 2. Check celery-content not OOMing anymore
railway logs -n 200 2>&1 | grep -i 'OOM\|killed\|memory'

# 3. Verify spider data is fresh (root cause confirmation)
railway run python manage.py shell -c "
from core.models_unified_system import SpiderData
from django.db.models import Min, Max, Count
agg = SpiderData.objects.aggregate(oldest=Min('created_at'), newest=Max('created_at'), total=Count('id'))
print(f'Spider data: {agg[\"total\"]} records, {agg[\"oldest\"]} to {agg[\"newest\"]}')
"

# 4. Check how many initiative conversations have empty spider context
railway logs -n 500 2>&1 | grep -c 'Injected spider intelligence'
railway logs -n 500 2>&1 | grep -c 'Could not get spider intelligence'
```

---

## Critical Patterns & Gotchas

**Agent hallucination in conversations (Session 1039):** When `spider_context` is empty (keyword matching misses), agents fabricate dates and statistics. `get_insights_for_prompt()` in `core/services/spider_intelligence.py:1040` only matches 5 narrow categories. Fix: anti-hallucination guard in system prompt + broaden matching + add timestamps.

**Tenant model (Session 1039):** `Tenant` in `core/models_tenant.py`, registered via `core/models/__init__.py`. Import: `from core.models_tenant import Tenant` or `from core.models import Tenant`. All FKs nullable — no enforcement yet (Phase 2-3).

**Celery-content OOM (Session 1039):** Deliberation tasks use 80-120MB. Worker now at 250MB limit with 5-task recycle. If OOM returns, the fix is to split deliberation into chained tasks (build claims → draft → review → rewrite).

**DynamicPersonaAgent (Session 1038):** `AgentRouter.route()` falls back to `DynamicPersonaAgent` when `AGENT_MAP` lookup fails. Checks `Agent.objects.filter(name=agent_name, is_active=True)`. Has `web_search` + `spider_query` tools only.

**PA function calling (Session 1036):** `PA_USE_FUNCTION_CALLING=true` env var. Agentic loop in `_run_agentic_loop()` — max 5 iterations, GPT-5.2 decides tool calls.

**Dual dispatch block (Session 1032):** CodeGeneratorAgent and AudioAgent blocked in BOTH `execute_agent_task` AND `AgentRouter.route()`.

**6 remediation paths ALL blocked (Session 1031):** execute_remediation_tasks, run_autonomous_remediation_cycle, assign_and_execute_remediation, run_agent_remediation_batch, assign_open_findings_to_agents, discover_and_import_audits.
