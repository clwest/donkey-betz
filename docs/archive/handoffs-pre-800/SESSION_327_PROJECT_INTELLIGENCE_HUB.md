# Session 327: Project Intelligence Hub

**Date:** December 3, 2025
**Focus:** Adding Agent Intelligence (Learning, Conversations, Dreams, Boardroom) to Project View

## Summary

Successfully implemented the **Project Intelligence Hub** - each project now has its own scoped intelligence view showing:
- **Learning**: Knowledge sources derived from project research
- **Conversations**: Hive Mind sessions and agent conversations about the project
- **Dreams**: Agent idle creative thoughts about the project
- **Boardroom**: Decisions made about the project

## What Was Built

### 1. Database Migration (0066)

Added `project` ForeignKey field to:
- `HiveMindSession` - for conversations scoped to projects
- `AgentDecisionSummary` - for boardroom decisions scoped to projects
- `AgentDream` - for dreams about specific projects
- `AgentConversation` - for legacy conversations

### 2. Backend API Endpoints

Created `core/views_project_intelligence.py` with 6 new endpoints:

| Endpoint | Purpose |
|----------|---------|
| `GET /api/projects/<id>/intelligence/` | Overview stats for all intelligence types |
| `GET /api/projects/<id>/intelligence/learning/` | Knowledge sources + feedback for project |
| `GET /api/projects/<id>/intelligence/conversations/` | Hive sessions + conversations |
| `GET /api/projects/<id>/intelligence/dreams/` | Agent dreams about project |
| `GET /api/projects/<id>/intelligence/boardroom/` | Decisions about project |
| `POST /api/projects/<id>/intelligence/conversations/trigger/` | Start a new conversation |

### 3. Frontend UI (Project Detail Modal)

Added a collapsible **Project Intelligence Hub** section after Project Information:

- Purple gradient card matching the platform style
- 4 sub-tabs: Learning, Conversations, Boardroom, Dreams
- Stats badges showing counts
- "Start Conversation" button to trigger agent discussions
- "Refresh" button to reload data

### 4. JavaScript Functions

Added 10 new functions to `ai_image_studio.html`:

| Function | Purpose |
|----------|---------|
| `loadProjectIntelligence(projectId, type)` | Load specific intelligence type |
| `renderProjectLearning()` | Render knowledge sources |
| `renderProjectConversations()` | Render conversations |
| `renderProjectDreams()` | Render agent dreams |
| `renderProjectBoardroom()` | Render boardroom decisions |
| `triggerProjectConversation()` | Start a new agent conversation |
| `refreshProjectIntelligence()` | Refresh current tab |
| `loadProjectIntelligenceOverview()` | Load stats when section opens |

## Files Created/Modified

| File | Action |
|------|--------|
| `core/migrations/0066_session_327_project_agent_intelligence.py` | Created |
| `core/views_project_intelligence.py` | Created |
| `core/models_unified_system.py` | Modified (added project fields) |
| `core/urls.py` | Modified (added 6 routes) |
| `ai_core/templates/ai_image_studio.html` | Modified (HTML + JS) |

## How It Works

```
User opens Project detail modal
        ↓
Clicks "Project Intelligence Hub" section
        ↓
Section expands → loadProjectIntelligenceOverview() called
        ↓
Overview stats fetched → badges updated
        ↓
Learning tab loaded by default → renderProjectLearning()
        ↓
User can switch tabs (Conversations, Boardroom, Dreams)
        ↓
Each tab calls loadProjectIntelligence(projectId, type)
        ↓
"Start Conversation" → triggerProjectConversation()
```

## Integration with Session 326

The Project-Agent Learning Bridge (Session 326) now feeds into this:
- Research → Knowledge conversion creates `AgentKnowledgeSource` with `source_project`
- User feedback on research affects knowledge confidence
- All project-scoped knowledge appears in the Learning tab

## Future Enhancements

1. **Auto-scope new activity**: When agents run for a project, auto-set the project field
2. **Project-scoped Agent Slack**: Create dedicated Slack channels per project
3. **Export intelligence**: PDF/report export of all project intelligence
4. **Real-time updates**: WebSocket push when new intelligence arrives

## Testing

```bash
# Start platform
make start && make celery

# Access AI Studio
open http://localhost:8000/ai-studio/

# Open a project detail modal
# Click "Project Intelligence Hub" section
# Switch between tabs to see scoped data
```

## Key Insight

Projects are now true **intelligence containers**:
- Research data flows in (Session 325)
- Knowledge is extracted (Session 326)
- Agents can discuss projects (new)
- Decisions are tracked (new)
- Everything scoped to the project context!
