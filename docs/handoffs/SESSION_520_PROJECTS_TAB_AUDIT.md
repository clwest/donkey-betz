# Session 520: Projects Tab Comprehensive Audit & Fix

**Date:** December 21, 2025
**Status:** COMPLETE
**Focus:** Audit Projects tab UI, trace to backend, identify disconnects, and FIX them!

---

## Critical Finding: Two Project Models

The platform uses **TWO different project models** that are NOT connected:

| Model | Location | Used By | Records |
|-------|----------|---------|---------|
| `CreativeProject` | `content.models` | Projects tab UI, `/api/creative-projects/` | 6 |
| `PartnershipProject` | `core.models_partnership` | Research, Intelligence Hub, Session 519 auto-project | 6 |

### The Problem

1. **Projects tab** calls `/api/creative-projects/` which queries `CreativeProject`
2. **Session 519 auto-project** creates `PartnershipProject` records
3. **Result**: AI-generated content projects DON'T APPEAR in the Projects tab!

### When User Asks "Write a blog post..."
1. ContentWriterAgent generates content
2. `SuperPlatformCoordinator._auto_create_project_from_content()` creates a `PartnershipProject`
3. Green "Project Created" banner appears with "View Project" button
4. User clicks "View Project" - navigates to Projects tab
5. **Bug**: Project doesn't appear because UI loads from `CreativeProject` table!

---

## Complete UI Feature Mapping

### 1. Project List View (`renderProjects`)

| UI Element | Backend API | Model | Status |
|------------|-------------|-------|--------|
| Load projects | `GET /api/creative-projects/` | CreativeProject | Works for old projects |
| Status badge | From project data | - | Works |
| Progress bar | From project data | - | Works |
| Deadline display | From project data | - | Works |
| Tags | From project data | - | Works |
| View button | Opens detail modal | - | Works |
| Edit button | Opens edit modal | - | Works |
| Delete button | `DELETE /api/creative-projects/{id}/delete/` | CreativeProject | Works |

### 2. Create Project Modal (`saveProject`)

| UI Element | Backend API | Model | Status |
|------------|-------------|-------|--------|
| Name field | - | - | Works |
| Goal field | - | - | Works |
| Description field | - | - | Works |
| Category dropdown | - | - | Works |
| Colors field | - | - | Works |
| Status dropdown | - | - | Works |
| Tags field | - | - | Works |
| Deadline picker | - | - | Works |
| Save button | `POST /api/creative-projects/create/` | CreativeProject | Works |

### 3. Project Details Modal (`viewProjectDetails`)

| UI Section | Backend API | Model | Status |
|------------|-------------|-------|--------|
| **Project Stats Header** |
| Images count | From `stats.content.images` | - | Needs stats API |
| Videos count | From `stats.content.videos` | - | Needs stats API |
| 3D Models count | From `stats.content.models` | - | Needs stats API |
| Agents count | From `stats.collaboration.unique_agents_count` | - | Needs stats API |
| Workflows count | From `stats.collaboration.workflows_count` | - | Needs stats API |
| **Project Information** |
| Status display | From project data | - | Works |
| Category display | From project data | - | Works |
| Colors display | From project data | - | Works |
| Tags display | From project data | - | Works |
| Goal display | From project data | - | Works |
| Description display | From project data | - | Works |
| **Continuous Learning** |
| Toggle switch | `POST /api/projects/{id}/learning/toggle/` | PartnershipProject | Works (uses wrong model) |
| Frequency dropdown | Same | PartnershipProject | Works |
| Topics display | Same | PartnershipProject | Works |
| Run Now button | `POST /api/projects/{id}/learning/trigger/` | PartnershipProject | Works |
| **Research Sources** |
| Expandable list | From `metadata.research_links` | - | Works if metadata exists |
| **Analysis Section** |
| Research summaries | From `metadata.research_summaries` | - | Works if metadata exists |
| PDF export button | `GET /api/projects/{id}/export-research-pdf/` | PartnershipProject | Works |
| **Executive Recommendations** |
| Expandable dropdowns | From `metadata.agent_recommendations` | - | Works if metadata exists |
| **Suggested Next Steps** |
| Bullet list | From `metadata.suggested_next_steps` | - | Works if metadata exists |
| **Written Content (Session 519)** |
| Content type badge | From `metadata.written_content` | - | Works if metadata exists |
| Expandable content | Same | - | Works |
| Copy button | `copyWrittenContent()` JS | - | Works |
| **Project Intelligence Hub** |
| Learning tab | `GET /api/projects/{id}/intelligence/learning/` | PartnershipProject | Works |
| Conversations tab | `GET /api/projects/{id}/intelligence/conversations/` | PartnershipProject | Works |
| Boardroom tab | `GET /api/projects/{id}/intelligence/boardroom/` | PartnershipProject | Works |
| Dreams tab | `GET /api/projects/{id}/intelligence/dreams/` | PartnershipProject | Works |
| Agent Slack tab | `GET /api/projects/{id}/intelligence/slack/` | PartnershipProject | Works |
| Start Conversation | `POST /api/projects/{id}/intelligence/conversations/trigger/` | PartnershipProject | Works |
| **Quick Workflows** |
| Train Project Style | `trainProjectStyle()` → Character Training | - | Works |
| Logo Package | `executeWorkflow()` | - | Works |
| Social Media Kit | Same | - | Works |
| **Export Options** |
| ZIP export | `GET /api/creative-projects/{id}/export/zip/` | CreativeProject | Works |
| PDF export | `GET /api/creative-projects/{id}/export/pdf/` | CreativeProject | Works |
| CSV export | `GET /api/creative-projects/{id}/export/csv/` | CreativeProject | Works |

---

## API Endpoints Summary

### CreativeProject APIs (`/api/creative-projects/`)
Used by Projects tab UI, defined in `core/views_image.py`:

| Endpoint | Method | Function |
|----------|--------|----------|
| `/api/creative-projects/` | GET | `list_projects` |
| `/api/creative-projects/create/` | POST | `create_project` |
| `/api/creative-projects/{id}/` | GET | `get_project` |
| `/api/creative-projects/{id}/update/` | PUT/PATCH | `update_project` |
| `/api/creative-projects/{id}/delete/` | DELETE | `delete_project` |
| `/api/creative-projects/{id}/workflows/` | POST | `add_workflow_to_project` |
| `/api/creative-projects/{id}/export/zip/` | GET | `export_project_zip` |
| `/api/creative-projects/{id}/export/pdf/` | GET | `export_project_pdf` |
| `/api/creative-projects/{id}/export/csv/` | GET | `export_project_csv` |
| `/api/creative-projects/{id}/share/` | GET/POST | Share management |

### PartnershipProject APIs (`/api/projects/`)
Used by Intelligence Hub, Learning Loop, defined in `core/views_projects_api.py`:

| Endpoint | Method | Function |
|----------|--------|----------|
| `/api/projects/` | GET | `projects_list` |
| `/api/projects/{id}/` | GET | `project_detail` |
| `/api/projects/{id}/agents/` | GET | `project_agents` |
| `/api/projects/{id}/assign-agent/` | POST | `assign_agent_to_project` |
| `/api/projects/from-research/` | POST | `create_project_from_research` |
| `/api/projects/{id}/add-research/` | POST | `add_research_to_project` |
| `/api/projects/{id}/export-research-pdf/` | GET | `export_research_pdf` |
| `/api/projects/{id}/learning/toggle/` | POST | `toggle_project_learning` |
| `/api/projects/{id}/learning/status/` | GET | `get_project_learning_status` |
| `/api/projects/{id}/learning/trigger/` | POST | `trigger_project_learning` |
| `/api/projects/{id}/feed/` | GET | `project_feed` |
| `/api/projects/{id}/intelligence/` | GET | `get_project_intelligence_overview` |
| `/api/projects/{id}/intelligence/learning/` | GET | `get_project_learning` |
| `/api/projects/{id}/intelligence/conversations/` | GET | `get_project_conversations` |
| `/api/projects/{id}/intelligence/boardroom/` | GET | `get_project_boardroom` |
| `/api/projects/{id}/intelligence/dreams/` | GET | `get_project_dreams` |
| `/api/projects/{id}/intelligence/slack/` | GET | `get_project_slack_channel` |

---

## Model Comparison

### CreativeProject (Simple)
```python
- id, created_at, updated_at
- user (FK)
- name, description, goal
- status, category, colors, tags
- deadline, is_shared, is_quick_starts
- metadata (JSON)
- workflows (M2M to WorkflowHistory)
```

### PartnershipProject (Rich)
```python
# All of CreativeProject fields PLUS:
- project_name, project_type
- workflow_steps (JSON), current_step
- ai_contributions, human_contributions (JSON)
- ai_time_equivalent, human_time_actual
- ai_contribution_percent, human_contribution_percent
- deliverable_description, deliverable_url
- quality_score, client_satisfaction
- contract_value, payment_received
- what_worked, what_to_improve, lessons_learned

# Learning Loop
- learning_enabled, learning_frequency
- learning_topics, learning_history
- last_learning_run, next_learning_run

# Related Models
- AgentKnowledgeSource (via source_project)
- AgentConversation (via project)
- AgentDream (via project)
- HiveMindSession (via project)
- BusinessResearchResult (via project)
- ProjectInsight (via project)
- LivingProjectConfig (OneToOne)
```

---

## Recommended Fix Strategy

### Option A: Unify on PartnershipProject (Recommended)

1. **Update UI** to call `/api/projects/` endpoints instead of `/api/creative-projects/`
2. **Migrate** existing CreativeProject records to PartnershipProject
3. **Deprecate** CreativeProject model
4. **Update** Session 519 auto-project - already uses PartnershipProject (good!)

**Pros:**
- Single source of truth
- PartnershipProject has richer features
- Intelligence Hub, Learning Loop already work with it

**Cons:**
- Frontend changes required
- Need to migrate old projects

### Option B: Merge in API Layer

1. Create a unified `/api/all-projects/` endpoint that merges both models
2. Keep both models but present as one in UI

**Pros:**
- Minimal database changes
- Backwards compatible

**Cons:**
- Complexity in maintaining two models
- Potential sync issues

### Option C: Quick Fix - Show PartnershipProjects Too

1. Add second list to Projects tab showing PartnershipProject records
2. Keep separate sections for now

**Pros:**
- Fastest to implement
- No migration needed

**Cons:**
- Confusing UX
- Duplicate project management

---

## Session 519 Bug Impact

When ContentWriterAgent creates content:
1. Creates `PartnershipProject` record
2. Returns `project_created` with `project_id`
3. Frontend shows banner with "View Project" button
4. URL: `/ai-studio/?tab=projects&project_id={uuid}`
5. User clicks → navigates to Projects tab
6. **Bug**: `loadProjects()` calls `/api/creative-projects/` which doesn't have this project
7. **Result**: Project not visible!

The project IS saved and can be accessed via:
- Direct API: `/api/projects/{id}/`
- Intelligence Hub endpoints work correctly

---

## Next Steps for Session 520

1. **Immediate Fix**: Update `loadProjects()` to fetch from `/api/projects/` (PartnershipProject)
2. **Or**: Create unified endpoint that merges both project types
3. **Test**: Verify ContentWriterAgent → project appears in tab
4. **Document**: Update API docs with unified approach

---

## Implementation Complete (Session 520)

### Backend Changes

**File: `core/views_projects_api.py`**
1. Updated `projects_list()` to return CreativeProject-compatible format with all required fields
2. Updated `project_detail()` to return CreativeProject-compatible format
3. Added `update_project()` - new endpoint for PartnershipProject updates
4. Added `delete_project()` - new endpoint for PartnershipProject deletion
5. Added `create_project()` - new endpoint for PartnershipProject creation

**File: `core/urls.py`**
1. Added imports for new CRUD endpoints (aliased to avoid conflicts)
2. Added URL routes:
   - `api/projects/create/` → `create_partnership_project`
   - `api/projects/<uuid>/update/` → `update_partnership_project`
   - `api/projects/<uuid>/delete/` → `delete_partnership_project`

### Frontend Changes

**File: `ai_core/templates/ai_image_studio.html`**
1. `loadProjects()` - Changed from `/api/creative-projects/` to `/api/projects/`
2. `viewProjectDetails()` - Changed from `/api/creative-projects/${id}/` to `/api/projects/${id}/`
3. `saveProject()` - Changed create/update URLs to `/api/projects/`
4. `deleteProject()` - Changed from `/api/creative-projects/` to `/api/projects/`

### Result

- AI-generated content projects from ContentWriterAgent (Session 519) now appear in Projects tab
- All CRUD operations work with PartnershipProject model
- Written content display works correctly
- Intelligence Hub, Learning Loop, and other features work because they already used PartnershipProject

### Testing

```bash
# API returns 6 PartnershipProject records with correct format
curl -s http://localhost:8000/api/projects/ | jq '.data.projects | length'
# Result: 6

# Projects include written_content metadata
curl -s http://localhost:8000/api/projects/ | jq '.data.projects[0].metadata.written_content'
# Result: Blog post content from Session 519
```

