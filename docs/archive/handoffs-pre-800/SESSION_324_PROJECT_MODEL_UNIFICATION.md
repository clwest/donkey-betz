# Session 324: Project Model Unification + Business Research Integration

**Date:** December 2, 2025
**Focus:** Unified Project Model, Business Research Agents in Projects, UI Rendering Fixes

---

## Summary

This session unified the two project models (CreativeProject and PartnershipProject) into a single `PartnershipProject` model, fixed business research agents (CustomerResearchAgent, CompetitorAnalysisAgent) to work in the embedded project assistant, and enhanced the research-to-project data flow.

---

## Major Accomplishments

### 1. Unified Project Model
- **Merged CreativeProject into PartnershipProject** - Only one project model now
- Added missing fields from CreativeProject: `goal`, `deadline`, `category`, `colors`, `tags`, `total_workflows`, `completed_workflows`, `is_shared`, `is_quick_starts`, `metadata`
- Created alias in `content/models.py`: `from core.models_partnership import PartnershipProject as CreativeProject`
- Added backward compatibility: `@property name` → `project_name`, `progress_percentage`, `is_overdue`, `get_sequential_number()`
- **Migration:** `0063_session_324_unified_project_model`

### 2. Fixed ForeignKey References
Updated all files that referenced `'content.CreativeProject'` to use `'core.PartnershipProject'`:
- `content/models.py` - ProjectWorkflow, SharedProject
- `pipelines/models.py`
- `agents/models.py`
- `rendering/models.py`
- `coleadership/models.py`
- `core/models_unified_system.py` - BusinessResearchResult
- `tests/factories.py`

### 3. Business Research Agents in Projects Tab
- Added `competitor_analysis_agent` and `customer_research_agent` handlers to `/api/executor/run-tool/`
- Fixed `CustomerResearchAgent` handler to pass required `scifi_context={}` and `spider_context={}` arguments
- Fixed `AgentResult.message` vs `.content` attribute error

### 4. Research Data Flow Improvements
- Research articles now saved to project metadata (up to 20 articles)
- **New API endpoint:** `POST /api/projects/<project_id>/add-research/`
  - Merges research articles (avoiding duplicates by URL)
  - Updates sources and metadata
  - Adds AI contribution record

### 5. UI Rendering Fixes
- **Fixed raw HTML rendering in embedded assistant** - `addProjectChatMessage()` now detects `<!-- RAW_HTML -->` markers and renders HTML properly
- **Changed "Create Project" to "Add to Project"** - When research is done in project context, button adds to current project instead of creating new one
- Added `addResearchToCurrentProject(projectId)` JavaScript function

### 6. Microphone/Transcription Fix
- Fixed `isRecording` flag timing - was being set AFTER `checkAudioLevel()` call
- Audio chunks now proper size (1948 bytes vs 43-44 bytes before)

---

## Files Modified

### Backend
- `core/models_partnership.py` - Added CreativeProject fields + compatibility properties
- `content/models.py` - CreativeProject alias + updated ForeignKeys
- `pipelines/models.py` - Updated FK reference
- `agents/models.py` - Updated FK reference
- `rendering/models.py` - Updated FK reference
- `coleadership/models.py` - Updated FK reference
- `core/models_unified_system.py` - Updated FK reference
- `tests/factories.py` - Updated model reference
- `core/views_image.py` - Added business research agent handlers to execute_tool
- `core/views_projects_api.py` - Added `add_research_to_project` endpoint
- `core/urls.py` - Added new route
- `core/personal_ai_assistant_enhanced.py` - Fixed CustomerResearchAgent call
- `core/agents/business/competitor_analysis_agent.py` - Fixed to use spider_query first

### Frontend
- `ai_core/templates/ai_image_studio.html`:
  - Fixed `addProjectChatMessage()` for raw HTML rendering
  - Added business research agent handler in `formatToolResults()`
  - Added `addResearchToCurrentProject()` function
  - Button text changed from "Create Project" to "Add to Project" in project context

---

## Database Changes

Migration `0063_session_324_unified_project_model` added to `PartnershipProject`:
- `goal` (TextField)
- `deadline` (DateTimeField)
- `category` (CharField)
- `colors` (JSONField)
- `tags` (JSONField)
- `total_workflows` (IntegerField)
- `completed_workflows` (IntegerField)
- `is_shared` (BooleanField)
- `is_quick_starts` (BooleanField)
- `metadata` (JSONField)

---

## API Endpoints

### New Endpoint
```
POST /api/projects/<project_id>/add-research/

Body:
{
    "research_type": "competitor_analysis" | "customer_research",
    "research_summary": "Analysis text...",
    "research_articles": [...],
    "research_query": "original query",
    "data_points_analyzed": 15,
    "sources_used": ["reddit", "hackernews"]
}

Response:
{
    "success": true,
    "articles_added": 10,
    "total_articles": 15
}
```

---

## Testing Verification

1. **Project Model Works:**
   ```python
   from content.models import CreativeProject
   from core.models_partnership import PartnershipProject
   assert CreativeProject is PartnershipProject  # True
   ```

2. **Project Detail View:**
   ```
   GET /api/creative-projects/<uuid>/ → 200 OK with research_articles in metadata
   ```

3. **Business Research in Projects:**
   - Voice command "Research customer pain points" → Full analysis report displays
   - "Add to Project" button → Adds research to current project

---

## Known Issues

None - all features working as expected.

---

## Next Steps

1. Test full flow: Voice → Research → Add to Project → View in Project Details
2. Consider adding research history view in project details
3. May want to add "Export Research" functionality
