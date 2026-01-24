# Session 798: Workspace & Docs Context Injection

**Date:** January 23, 2026
**Focus:** Making agents workspace-aware and docs-aware
**PRs Merged:** 12 (#25-28, #30, #32-36)

---

## Summary

Session 798 implemented automatic context injection for all agents. Every agent now receives:
1. **Workspace context** - Active workspace's tech stack, key files, directory structure
2. **Docs context** - Relevant documentation based on agent type and task

This enables agents to understand the codebase they're working with and access relevant system documentation automatically.

---

## Key Implementations

### 1. Workspace Context Injection (PR #28)

**File:** `core/agent_router.py`

Added `_get_workspace_context()` method that:
- Fetches active workspace via `WorkspaceManager`
- Extracts tech_stack, key_files, directory_purposes, coding_patterns
- Merges into `spider_context['workspace']`

```python
spider_context['workspace'] = {
    'has_workspace': True,
    'workspace_name': 'unified-donkey-betz',
    'tech_stack': {'frontend': 'react', 'backend': 'django'},
    'key_files': {'urls': 'core/urls.py', 'models': 'core/models.py'},
    'directory_purposes': {'agents': 'AI agents', 'services': 'Business logic'},
    'coding_patterns': {'test_pattern': 'test_*.py'},
}
```

### 2. Docs Context Injection (PR #30)

**File:** `core/services/docs_context_builder.py` (NEW - 510 lines)

Created `DocsContextBuilder` service that:
- Maps agent types to documentation categories via `AGENT_DOCS_MAPPINGS`
- Boosts categories based on task keywords via `TASK_KEYWORD_BOOSTS`
- Loads and caches `docs/_index.json` (1,548 documents)
- Filters and ranks documents by relevance
- Includes 5 most recent session handoffs

```python
spider_context['docs'] = {
    'has_docs': True,
    'categories_queried': ['architecture', 'api', 'integration'],
    'relevant_docs': [...],  # Up to 10 relevant docs
    'recent_sessions': [...],  # Last 5 session handoffs
    'total_docs_available': 1548,
}
```

### 3. BaseAgent Docs Tools (PR #30)

**File:** `core/agents/base_agent.py`

Added 6 documentation tools to BaseAgent:

| Tool | Purpose |
|------|---------|
| `_read_doc(doc_path)` | Read docs with security checks |
| `_write_doc(doc_path, content)` | Write/update with auto-backup |
| `_create_session_handoff(num, title, content)` | Create handoff docs |
| `_update_start_next_session(num, focus)` | Update session start file |
| `_regenerate_docs_index()` | Run build_docs_index command |
| `_get_docs_for_task(task)` | Get relevant docs for task |

**Security:** Read/write restricted to `docs/` directory plus `CLAUDE.md` and `00-START-NEXT-SESSION.md`

### 4. PA Workspace Awareness (PR #33-34)

**File:** `core/personal_ai_assistant_enhanced.py`

Added `_build_workspace_context_section()` that injects active workspace context into the Personal Assistant's system prompt.

**Bug Fix (PR #34):**
- Frontend was calling wrong endpoint (`/v1/assistant/chat/` instead of `/assistant/chat/`)
- Model relationship fix: `key_files`, `directory_purposes` etc. are on `WorkspaceContext` model (via `workspace.context`), not directly on `ProjectWorkspace`

### 5. Code Agent Docs Expansion (PR #36)

**File:** `core/services/docs_context_builder.py`

Expanded `AGENT_DOCS_MAPPINGS` for development agents:

| Agent | Added Categories |
|-------|------------------|
| code_generator | +backend, +integration, +learning |
| full_stack_developer | +backend, +integration, +learning |
| code_review | +backend, +integration |
| devops | +backend, +integration |
| prompt_engineering | +learning |
| technical_document | +backend, +integration |
| personal_assistant | +integration, +learning, +backend, +frontend |
| default (all agents) | +integration |

---

## Bug Fixes

### Dashboard Math (PR #35)

**File:** `frontend/src/pages/DashboardPage.tsx`

1. **Learning Velocity trend:** `velocity_trend.rate` is absolute change, not percentage
   - Before: `-21.861%`
   - After: `-21.86/day`

2. **Agent effectiveness:** `Agent.effectiveness_score` is 0-100, not 0-1
   - Before: `9500%` (was multiplying by 100)
   - After: `95%`

### Auth & Validation (PR #25-26)

1. **WorkspacePage auth gating:** Added `enabled: isAuthenticated` to prevent 404 errors
2. **GitHub URL validation:** Added `validate_github_url()` for clear error messages

---

## Files Modified

| File | Changes |
|------|---------|
| `core/agent_router.py` | +_get_workspace_context(), +_get_docs_context() |
| `core/services/docs_context_builder.py` | **NEW** - DocsContextBuilder service |
| `core/agents/base_agent.py` | +6 docs tools |
| `core/personal_ai_assistant_enhanced.py` | +_build_workspace_context_section() |
| `core/views_workspace_api.py` | +validate_github_url() |
| `frontend/src/pages/WorkspacePage.tsx` | +auth gating |
| `frontend/src/pages/DashboardPage.tsx` | Fixed math calculations |
| `frontend/src/lib/api.ts` | Changed PA endpoint |
| `Dockerfile` | +git in production runtime |

---

## Testing

### Verify Workspace Context
```bash
# Check agent logs for workspace context
# Look for: "📁 [Session 798] Workspace context for AgentName: workspace=..."
```

### Verify Docs Context
```bash
# Check agent logs for docs context
# Look for: "📚 [Session 798] Docs context for AgentName: categories=..."
```

### Test PA Workspace Awareness
```bash
# Ask PA about the workspace
curl -X POST http://localhost:8000/assistant/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token YOUR_TOKEN" \
  -d '{"message": "What tech stack is this workspace using?"}'
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        AgentRouter.route()                       │
├─────────────────────────────────────────────────────────────────┤
│                              │                                   │
│    ┌─────────────────────────┼─────────────────────────┐        │
│    │                         │                         │        │
│    ▼                         ▼                         ▼        │
│ _get_workspace_context()  _get_docs_context()    _get_spider_*  │
│         │                       │                      │        │
│         ▼                       ▼                      ▼        │
│   WorkspaceManager       DocsContextBuilder     SpiderService   │
│         │                       │                      │        │
│         └───────────────────────┼──────────────────────┘        │
│                                 │                               │
│                                 ▼                               │
│                          spider_context                         │
│                   {workspace: {...}, docs: {...}}               │
│                                 │                               │
│                                 ▼                               │
│                         Agent.execute()                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Next Steps (Session 799)

1. Test workspace + docs integration in production
2. Have agents use `_create_session_handoff()` to write docs
3. Monitor context injection in agent execution logs
