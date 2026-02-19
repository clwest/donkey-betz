# Session 1040 - Start Here

**Previous Sessions:** 1039 (Tenant Model + Celery OOM Fix), 1038 (DynamicPersonaAgent), 1037 (Initiative Pipeline Fix), 1036 (PA Function Calling Hardening)
**Date:** February 19, 2026
**Status:** 92 Agents | 79 Spiders | 25 Advisors | **PA function calling LIVE (GPT-5.2)** | **All 218 agent personas routable** | **Tenant model foundation landed (Phase 1/3)** | 19 ACTIVE initiatives

---

## Session 1039 — What Happened

### Tenant Model & Customer Access Foundation (Phase 1 of 3)

Created multi-tenant infrastructure for future customer-facing access control. PR #1327 on branch `feature/session-1039-tenant-model-customer-access`.

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

**What's NOT in this phase:**
| Deferred | Phase |
|----------|-------|
| Pre-execution budget check in AgentRouter.route() | Phase 2 |
| LUNGS can_breathe() tenant/user extension | Phase 2 |
| Customer-safe API endpoints (/api/customer/) | Phase 3 |
| TenantScopeMixin for ViewSets | Phase 3 |

### Celery-Content OOM Fix

`celery-content` worker was OOMing on Railway (user received 2 OOM emails). Root cause: deliberation pipeline tasks use 80-120MB per task (ClaimsPack + double ContentWriterAgent instantiation + 3-reviewer ConversationOrchestrator), but child limit was only 150MB.

**Fix:** Bumped `--max-memory-per-child` from 150MB → 250MB and `--max-tasks-per-child` from 10 → 5. Peak: 200MB parent + 250MB child = 450MB, fits Railway 512MB with 62MB headroom.

### Commits
| Commit | Description |
|--------|-------------|
| 17dc0664 | feat: add Tenant model and customer access foundation (Phase 1 of 3) |
| bdf1e0f2 | fix: bump celery-content memory 150→250MB and recycle 10→5 tasks |

### PR
- PR #1327: `feature/session-1039-tenant-model-customer-access` — **needs merge**

---

## Priority for Session 1040

**User saw an interesting agent conversation that exposes a big issue.** Ask the user to share what they saw — this is the top priority.

---

## Current System Health (post-Session 1039)

| Metric | Value |
|--------|-------|
| PA routing | **GPT-5.2 function calling** (`PA_USE_FUNCTION_CALLING=true`) |
| Agents routable | **All 218** (82 AGENT_MAP + 139 DynamicPersonaAgent + 2 blocked) |
| Initiatives | **19 ACTIVE**, 8 COMPLETED, 0 TRIAGE |
| Content worker | **250MB limit, 5-task recycle** (was 150MB/10, OOMing) |
| Tenant model | **Phase 1 landed** (PR #1327, needs merge + migrate on Railway) |
| Agent health | 92.4% pass rate |

---

## Known Issues / Open Items

### Profile Consolidation (Phase 4)
Three user profile models: UserProfile + ExtendedUserProfile + EnhancedUserProfile. Need to merge into UnifiedUserProfile. Deferred from Session 1035.

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
- Verify DynamicPersonaAgent working on Railway

---

## Verify Before Starting

```bash
# 1. Check PR #1327 merged and migration applied
railway run python manage.py shell -c "
from core.models_tenant import Tenant
from core.models import UnifiedUser
u = UnifiedUser.objects.first()
print(f'tenant={u.tenant}, customer_role={u.customer_role}')
print('Tenant model accessible: OK')
"

# 2. Check celery-content not OOMing anymore
railway logs -n 200 2>&1 | grep -i 'OOM\|killed\|memory'

# 3. Initiative pipeline status
railway run python manage.py shell -c "
from core.models import Initiative
from django.db.models import Count
for s in Initiative.objects.values('status').annotate(cnt=Count('id')).order_by('-cnt'):
    print(f'{s[\"status\"]:15} {s[\"cnt\"]}')
"
```

---

## Critical Patterns & Gotchas

**Tenant model (Session 1039):** `Tenant` in `core/models_tenant.py`, registered via `core/models/__init__.py`. Import: `from core.models_tenant import Tenant` or `from core.models import Tenant`. All FKs nullable — no enforcement yet (Phase 2-3).

**Celery-content OOM (Session 1039):** Deliberation tasks use 80-120MB. Worker now at 250MB limit with 5-task recycle. If OOM returns, the fix is to split deliberation into chained tasks (build claims → draft → review → rewrite).

**DynamicPersonaAgent (Session 1038):** `AgentRouter.route()` falls back to `DynamicPersonaAgent` when `AGENT_MAP` lookup fails. Checks `Agent.objects.filter(name=agent_name, is_active=True)`. Has `web_search` + `spider_query` tools only.

**PA function calling (Session 1036):** `PA_USE_FUNCTION_CALLING=true` env var. Agentic loop in `_run_agentic_loop()` — max 5 iterations, GPT-5.2 decides tool calls.

**Dual dispatch block (Session 1032):** CodeGeneratorAgent and AudioAgent blocked in BOTH `execute_agent_task` AND `AgentRouter.route()`.

**6 remediation paths ALL blocked (Session 1031):** execute_remediation_tasks, run_autonomous_remediation_cycle, assign_and_execute_remediation, run_agent_remediation_batch, assign_open_findings_to_agents, discover_and_import_audits.
