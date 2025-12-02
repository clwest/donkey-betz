# Session 302: Direct API for Project Creation & Project Context Awareness

**Date:** December 1, 2025
**Status:** Complete
**Focus:** Fixed Create Project routing (direct API), added project context to business research agents

## Summary

Two major improvements to the business research workflow:
1. **Direct API for Create Project** - Bypasses GPT routing entirely (instant instead of 178+ seconds)
2. **Project Context Awareness** - Business research agents can now use the current project's context

---

## Part 1: Direct API for Create Project

### Problem
Even after Session 301's fix to use "Organize our research" messaging, the Create Project button was still slow and occasionally routed through WorkflowAgent (178+ seconds).

### Solution
Created a **direct REST API endpoint** that bypasses GPT entirely:

```
POST /api/projects/from-research/
```

### Files Created/Modified

| File | Changes |
|------|---------|
| `core/views_projects_api.py` | Added `create_project_from_research()` API endpoint (line 498+) |
| `core/urls.py` | Added URL route for `/api/projects/from-research/` |
| `ai_core/templates/ai_image_studio.html` | Updated `submitCreateProjectFromResearch()` to use `fetch()` directly |

### How It Works

**Before (Session 301):**
```
User clicks "Create Project" → GPT processes message → GPT calls tool → Project created
(178+ seconds, sometimes still mis-routed)
```

**After (Session 302):**
```
User clicks "Create Project" → Direct fetch() to API → Project created
(~1-2 seconds, no GPT involved)
```

### API Details

```python
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project_from_research(request):
    """Direct API - bypass GPT for instant project creation."""
    data = request.data
    market_name = data.get('market_name', 'Research Project')
    research_type = data.get('research_type', 'competitor')
    research_data = data.get('research_data', {})

    # Create project directly in database
    project = PartnershipProject.objects.create(...)

    return Response({'success': True, 'project_id': str(project.id), ...})
```

---

## Part 2: Project Context Awareness

### Problem
When inside a project chat, saying "Research customer pain points" would do generic research rather than using the project's topic/context.

### Solution
Added `project_id` parameter to business research agents. When provided, they automatically enhance vague requests with the project's name and description.

### Files Modified

| File | Changes |
|------|---------|
| `core/assistant/tool_definitions.py` | Added `project_id` parameter to both research agents (lines 661-664, 702-705) |
| `core/agents/business/customer_research_agent.py` | Added `_get_project_context()` and `_enhance_task_with_project()` methods |
| `core/agents/business/competitor_analysis_agent.py` | Added same methods |

### How Context Enhancement Works

```python
def _enhance_task_with_project(self, task: str, project_context: Dict) -> str:
    """Enhance vague requests with project context."""
    # "Research customer pain points"
    # becomes:
    # "Research customer pain points for 'AI Coffee Roasting': Premium coffee..."
```

### Tool Definition Update

```python
"project_id": {
    "type": "string",
    "description": "Optional project ID to use context from. If user says 'for this project' or 'for the current project', extract the project ID from conversation context."
}
```

---

## Testing

### Test Direct API
1. Run competitor research: "Analyze competitors for AI content generation apps"
2. Click "Create Project" button
3. Verify: Project created instantly (1-2 seconds), no spinner for 178 seconds
4. Check Projects tab - new project should appear

### Test Project Context
1. Open an existing project
2. Say "Research customer pain points for this project"
3. Verify: Research uses the project's name/description as context
4. Check logs for: "Enhanced task with project context: ..."

---

## Commits Made

```
b20b04c fix(Session 302): Create Project button now uses direct API, bypasses GPT routing
dfd80b1 feat(Session 302): Add project context awareness to business research agents
```

---

## Next Session Priority: Agent Database Relationship Audit

The user has requested that the next session focus on **auditing all agents for correct database relationships**. This is important because:

1. **Multiple agent systems exist**: Clean agents (BaseAgent), legacy agents, and tool definitions
2. **Database models are fragmented**: PartnershipProject, BusinessResearchResult, Opportunity, etc.
3. **Need to ensure**: All agents that store data are using correct model relationships

### Suggested Audit Areas

1. **Business Research Agents** (CustomerResearchAgent, CompetitorAnalysisAgent)
   - Currently save to: `BusinessResearchResult`
   - Should they also link to: `PartnershipProject`?

2. **Workflow Orchestration**
   - Creates projects but doesn't link research results

3. **Opportunity System**
   - Phase 1-6 models in `models_unified_system.py`
   - Are they properly connected to projects?

4. **Spider Data**
   - `SpiderData` model
   - How does it flow to agents?

5. **Image/Video Generation**
   - `ImageHistory`, `VideoHistory`
   - Are they linked to projects?

### Files to Audit

```
core/models_partnership.py      # PartnershipProject, CollaborativeContent
core/models_unified_system.py   # Opportunity, SpiderData, BusinessResearchResult
content/models.py               # ImageHistory, VideoHistory
core/agents/business/*.py       # Business research agents
core/agents/*.py                # All clean agents
agents/*.py                     # Legacy agents
```

---

## Architecture Note

The routing architecture has multiple layers that need proper database connections:

```
PersonalAssistantEnhanced (GPT + tools)
    ↓
AgentRouter (deterministic routing)
    ↓
Specialized Agents (ImageAgent, VideoAgent, etc.)
    ↓
Database Models (need consistent relationships)
```

Each layer should properly:
1. Receive user/project context
2. Store results with correct foreign keys
3. Link to relevant parent models (Project, Opportunity, etc.)

---

## Notes for Future Claude

### Context from This Session

1. **The user experienced data loss** from migrations not being run in a prior session. Always run `python manage.py makemigrations && python manage.py migrate` after any model changes, and verify migrations completed successfully.

2. **Direct API pattern works well** - When GPT routing causes slowness or mis-routing issues, consider creating direct REST API endpoints that bypass GPT entirely. The `create_project_from_research` endpoint went from 178+ seconds to ~1-2 seconds.

3. **Project context injection pattern** - The `_get_project_context()` and `_enhance_task_with_project()` methods added to business research agents are a good pattern for making any agent context-aware. Consider applying this to other agents during the database relationship audit.

4. **The user explicitly requested** the next session focus on auditing all agents for correct database relationships. This is a significant architectural review task - take time to understand all the model relationships before making changes.

5. **Multiple agent systems coexist**:
   - Clean agents in `core/agents/` (BaseAgent pattern)
   - Legacy agents in `agents/`
   - Tool definitions in `core/assistant/tool_definitions.py`

   The audit should cover all three to ensure consistent database usage.

6. **Key models to understand for the audit**:
   - `PartnershipProject` - Main project model
   - `BusinessResearchResult` - Research data with embeddings
   - `Opportunity` - Phase 1-6 opportunity tracking
   - `SpiderData` - Spider crawl results
   - `ImageHistory`, `VideoHistory` - Generated content

### What's Working Well

- Business research flow: Research -> Create Project -> Generate Content
- Context chaining between research queries
- Direct API for instant project creation
- Project context injection in research agents

### Potential Gotchas

- The frontend is large (~55k lines in `ai_image_studio.html`) - be careful with edits
- There are duplicate function definitions in JS - Session 300 fixed one, there may be others
- The `gpt-5-mini` model needs high `max_completion_tokens` (6000) for reasoning + output
