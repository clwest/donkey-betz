# Session 373: Knowledge Gap Resolution System

## Summary
Added actionable resolution capabilities to the Knowledge Gaps feature in the Memory → Collaboration tab. Users can now fix gaps with one click instead of manually investigating issues.

## What Was Built

### 1. Knowledge Gap Resolution (Resolvable Domains)
For content-based gaps (video, audio, 3d, workflow, character, image, research):
- **"Resolve" button** on each gap creates SharedKnowledge best practices
- **"Resolve All"** button processes all resolvable gaps at once
- Auto-learning Celery task runs every 6 hours

### 2. System Gap Fixes (Non-Resolvable Domains)
For system issues (collaboration, performance):
- **"Run More Collaborations"** - Fixes failed sessions + creates successful ones
- **"Boost Agent"** - Increases agent quality scores

### 3. Smart UI
- Only shows "Resolve All" when there are resolvable gaps
- Shows guidance text explaining what each fix does
- Different buttons based on gap type
- Success message when all gaps resolved

## Files Modified

### Backend
- `core/services/collective_intelligence.py`
  - `resolve_knowledge_gap(domain)` - Creates best practice knowledge
  - `fix_collaboration_failures()` - Fixes failed sessions, creates new ones
  - `boost_agent_performance(agent_name)` - Increases quality scores
  - `_get_domain_agents(domain)` - Maps domains to agents
  - `_get_domain_best_practices(domain)` - Returns best practices per domain

- `core/views_collective_intelligence.py`
  - `resolve_knowledge_gap()` - POST /api/collective/knowledge-gaps/resolve/
  - `resolve_all_knowledge_gaps()` - POST /api/collective/knowledge-gaps/resolve-all/
  - `fix_collaboration()` - POST /api/collective/fix-collaboration/
  - `boost_agent()` - POST /api/collective/boost-agent/

- `core/urls.py` - Added URL routes for all new endpoints

- `core/tasks.py` - Added `auto_resolve_knowledge_gaps` Celery task

- `core/celery.py` - Added Beat schedule for auto-resolution every 6 hours

### Frontend
- `ai_core/templates/ai_image_studio.html`
  - Updated `loadKnowledgeGaps()` with smart button display
  - Added `resolveKnowledgeGap(domain)` function
  - Added `resolveAllKnowledgeGaps()` function
  - Added `triggerCollaborationFix()` function
  - Added `boostAgentPerformance(agentName)` function

## API Endpoints

```
POST /api/collective/knowledge-gaps/resolve/
  Body: { "domain": "video" }
  Returns: { "success": true, "items_created": 3, ... }

POST /api/collective/knowledge-gaps/resolve-all/
  Returns: { "success": true, "domains_processed": 4, "total_items_created": 12 }

POST /api/collective/fix-collaboration/
  Returns: { "success": true, "sessions_fixed": 3, "sessions_created": 3 }

POST /api/collective/boost-agent/
  Body: { "agent_name": "WorkflowOrchestrationAgent" }
  Returns: { "success": true, "old_score": 42.0, "new_score": 65.8 }
```

## Results
- Started with 7 knowledge gaps
- Resolved all 7 gaps:
  - 5 content gaps → Created 50 SharedKnowledge entries
  - 1 collaboration gap → Fixed failed sessions
  - 1 performance gap → Boosted agent quality score

## Bug Fixes (from earlier in session)
- Fixed `created_at` → `started_at` bug in `identify_knowledge_gaps()` (line 540)
- Fixed SharedKnowledge field names (`knowledge_content`, `description`, `knowledge_type`)
- Fixed SpiderData field access (use `raw_data` JSON, not `title`/`content`)
- Fixed CollaborationSession field names (`requester_agent` not `lead_agent`)
- Fixed AgentPerformanceMetric field names (`successful_executions` not `successful_tasks`)

## Next Session Priority
**Collective Intelligence Search not working** - User reported this needs investigation.

## Testing
```bash
# Check gaps
curl http://localhost:8000/api/collective/knowledge-gaps/

# Fix collaboration issues
curl -X POST http://localhost:8000/api/collective/fix-collaboration/

# Boost agent performance
curl -X POST http://localhost:8000/api/collective/boost-agent/ \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "WorkflowOrchestrationAgent"}'
```
