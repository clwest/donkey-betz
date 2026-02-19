# Session 1035 - Start Here

**Previous Session:** 1034 (RAG Wiring, Legal Agent Pipeline, Production Stability — 10 PRs)
**Date:** February 18, 2026
**Status:** 92 Agents | 79 Spiders | 25 Advisors | 39 PA intents | **RAG documents wired into ALL agents** | **Legal agent LIVE** | **0 Railway errors** | **0 frontend 404s**

---

## Session 1034 — What Happened

### RAG Document Integration (PR #1319)
User-uploaded documents (PDFs, URLs, YouTube) now flow into **all 92 agents** via a new context layer:
- `_get_user_documents_context()` in AgentRouter — pgvector cosine similarity search
- `_build_intelligent_prompt()` injects relevant chunks as "YOUR UPLOADED DOCUMENTS"
- Legal agent gets additional direct RAG fallback with stricter threshold
- Cost: ~$0.00002 per agent execution (one embedding call)

### Legal Agent Pipeline (PRs #1315–#1318)
LegalDocDrafterAgent fully wired into PA:
- New `legal_assistance` PA intent (priority before `user_feedback`)
- Routes through `AgentRouter.route()` for full context injection
- JDF (Judicial Department Form) reference injected into prompt
- Fixed broken `court_order` document type filter
- Upload hint shown when no user documents found

### COO Recommendations (PR #1320)
- Throttled 4 beat schedules (~40% fewer runs): spider warm-up 4h→6h, clean stale 24h→48h, refresh AI opps 30m→2h, dream execution 2h→4h
- PA `universal_agent_tool` timeout raised 30s→90s
- Broadened trend bounding regex

### Production Stability (PRs #1321–#1323)
- **Workspace path self-healing:** Auto-detect stale local macOS paths on Railway, recompute and update DB
- **Media task guard:** Two-layer regex whitelist blocks non-generative tasks for ImageAgent/VideoAgent/AudioAgent/ThreeDAgent
- **4 Railway log errors fixed:** AgentResult `.result`→`.message`, UUID str() wrapping, OpportunityActionPlan→ActionPlan, SpiderPriority removal
- **3 frontend 404s fixed:** Stub endpoints for AgentsPage channels/tools/templates tabs

### Other Fixes
- PR #1314: Cleaner deliverable titles for research-and-create workflow

---

## Current System Health (post-Session 1034)

| Metric | Value |
|--------|-------|
| Railway log errors | **0** |
| Frontend console 404s | **0** |
| Agents with RAG document access | **92** |
| PA intents | **39** (added legal_assistance) |
| PA timeout | 90s (was 30s) |
| Media task guard | LIVE (two-layer) |
| Initiatives COMPLETED | 3 (from Session 1033) |
| Content finishing loop | LIVE (auto-enhance every 4h) |
| Deliverable scoring | LIVE (score every 6h) |
| Agent health | 92.4% pass rate |

---

## Known Issues / Open Items

### Ghost Celery Dispatcher — HARD-BLOCKED
`execute_remediation_tasks` triggered 41x/48h from unknown source. All execution + assignment paths now blocked. Root cause still unknown.

### 5th Dispatch Path — UNKNOWN
Something reads AuditRemediationTask records and dispatches CodeGeneratorAgent. All tasks cancelled + agent blocked in both dispatch paths, so it's neutralized but the code path is not identified.

### WorkflowAgent / TrendAnalysisAgent Timeout Risk
Both take 43-44min to complete. Celery timeout is 45min. They PASS but have no margin.

### TechnicalDocumentAgent workspace write warning
All initiative doc generation shows `Failed to write document to workspace: Unknown error`. Documents ARE created (SelfBlog + Deliverable), but workspace write fails silently. Non-blocking but should be investigated.

### Railway Cost
User hit $1,200/month limit, bumped to $1,500. Schedule throttling (Session 1034) + media guards should reduce costs.

### AgentsPage Tabs (Channels, Tools, Templates)
Currently return empty stubs. Full backends not yet built (Session 734 frontend, no backend).

### Future Improvements
- Score remaining ~3,500 deliverables (periodic task will handle over time)
- Enhance remaining ~111 `needs_enhancement` blogs (periodic task processes 5 per 4h run)
- Monitor new TRIAGE initiatives for end-to-end completion
- Build real backends for AgentsPage channels/tools/templates tabs
- Test RAG document injection with uploaded court orders via PA legal assistant

---

## Verify Before Starting

```bash
# 1. Check Railway errors (should be 0)
railway logs -n 200 2>&1 | grep -i 'ERROR\|WARNING\|Traceback' | grep -v 'errors=0\|error_count\|error_message\|error_type\|INFO'

# 2. Test RAG document context
railway run python manage.py shell -c "
from content.models import DocumentEmbedding
print(f'Document embeddings: {DocumentEmbedding.objects.count()}')
"

# 3. Test legal agent via PA
# Ask: "What are my options for enforcing a custody agreement?"
# Should route to LegalDocDrafterAgent with RAG context

# 4. Initiative & content status
railway run python manage.py shell -c "
from core.models_document_registry import Initiative
from core.models_unified_system import SelfBlog
from django.db.models import Count
print('=== Initiatives ===')
for s in Initiative.objects.values('status').annotate(cnt=Count('id')).order_by('-cnt'):
    print(f'{s[\"status\"]:15} {s[\"cnt\"]}')
print('=== Blogs ===')
for s in SelfBlog.objects.values('status').annotate(cnt=Count('id')).order_by('-cnt'):
    print(f'{s[\"status\"]:20} {s[\"cnt\"]}')
"

# 5. Agent health
railway run python manage.py shell -c "
from core.models import AgentExecution
from django.utils import timezone; from datetime import timedelta
from django.db.models import Count, Q
since = timezone.now() - timedelta(hours=6)
for a in AgentExecution.objects.filter(created_at__gte=since).values('agent__name').annotate(
    cnt=Count('id'), ok=Count('id', filter=Q(status='completed'))
).order_by('-cnt')[:15]:
    rate = a['ok']/max(a['cnt'],1)*100
    print(f'{a[\"agent__name\"]:35} {a[\"cnt\"]:3} runs {rate:.0f}%')
"
```

---

## Critical Patterns & Gotchas

**RAG context layer (Session 1034):** `_get_user_documents_context()` in AgentRouter — pgvector cosine search, threshold 0.45, top 5 chunks. Legal agent has additional direct fallback at 0.40. Only runs when `self.user` is set.

**Legal agent routing (Session 1034):** `legal_assistance` intent → `universal_agent_tool` → `AgentRouter.route()` → `LegalDocDrafterAgent`. Intent priority MUST be before `user_feedback` (which matches "order").

**Media task guard (Session 1034):** `_MEDIA_AGENTS` frozenset + `_MEDIA_GENERATION_PATTERN` regex. Two layers: pre-dispatch filter in `ConversationActionDispatcher` + fallback in `execute_agent_task`.

**Workspace path self-healing (Session 1034):** `_get_workspace_for_skin_layer()` detects invalid `root_path`, recomputes from `__file__`, updates DB. Handles Railway vs local path mismatch.

**Content finishing loop (Session 1033):** `auto_enhance_blogs` → EditorAgent with `save=True` → blog status `pending_review` → `reevaluate_enhanced_blogs` re-scores → `auto_publish_approved_blogs` publishes.

**Initiative dead state fix (Session 1033):** If stage has `status=IN_REVIEW` but no document, `advance_initiative_pipeline` now generates the doc.

**Dual dispatch block (Session 1032):** CodeGeneratorAgent and AudioAgent blocked in BOTH `execute_agent_task` AND `AgentRouter.route()`.

**6 remediation paths ALL blocked (Session 1031):** execute_remediation_tasks, run_autonomous_remediation_cycle, assign_and_execute_remediation, run_agent_remediation_batch, assign_open_findings_to_agents, discover_and_import_audits.

**Railway multi-service deployment:** GitHub push auto-deploys ALL services. Web service takes several minutes.

**Auth for production API:** `Token 0cdc1c72dba99ea637485076ee952d571440aa30`
