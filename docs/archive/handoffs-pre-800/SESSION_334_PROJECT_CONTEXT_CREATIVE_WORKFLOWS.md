# Session 334: Project Context for Creative Workflows

**Date:** December 3, 2025
**Branch:** `feature/session-52-ai-assistant`

---

## Overview

This session added **project research context as guidance** to the `WorkflowOrchestrationAgent`. When running creative workflows (like `brand_identity_package`) from within a project that has existing research, the workflow now uses that research to **guide** (not replace) each step.

---

## Problem Solved

Previously, when a user said "Create a brand identity" from within a project that already had competitor analysis and customer research:
- The workflow would start fresh without knowing about the existing research
- No connection between prior research and creative generation
- Users had to manually describe the context

Now:
- The workflow automatically fetches existing project research
- Research context is injected into each step as **guidance**
- Web search, executive review, and image generation all benefit from project context
- Agents still do their own fresh research, but it's more targeted

---

## Implementation Details

### New Method: `_get_project_research_context()`

Location: `agents/workflow_orchestration_agent.py:692-780`

This method:
1. Fetches `BusinessResearchResult` records linked to the project
2. Checks project metadata for `research_summaries` (Session 325 format)
3. Extracts competitor insights, customer insights, and pain points
4. Returns a context dict with `has_research`, `project_name`, `competitor_insights`, `customer_insights`, `customer_pain_points`, and `brand_recommendations`

### Enhanced Steps

#### 1. Web Search Step (lines 1135-1157)
- Augments search query with terms from customer pain points
- Adds "differentiate" if competitor insights exist
- Helps find MORE RELEVANT information, not less

#### 2. Co-Leadership Step (lines 1308-1337)
- Injects project research into executive review context
- Executives see: project name, competitor insights (500 chars), customer insights (500 chars), pain points
- Helps executives make informed recommendations

#### 3. Image Generation Step (lines 1711-1745)
- Maps customer pain points to visual concepts:
  - "trust/reliable" → "trustworthy stable"
  - "simple/easy" → "simple approachable"
  - "expensive/cost" → "premium value"
  - "confusing/overwhelming" → "clear organized"
  - "slow/time" → "fast efficient dynamic"
- Adds "distinctive unique" if competitor insights exist

### Bug Fix

Fixed `has_research` flag not being set when research came from project metadata (Session 325 format) vs `BusinessResearchResult` records.

---

## Testing

### Prerequisites
1. A project with research (e.g., "Donkey Betz Podcast" has competitor + customer research)

### Steps
1. Go to http://localhost:8000/ai-studio/
2. Click on a project with research
3. In the project assistant, say "Create a brand identity"
4. Watch logs for Session 334 messages:
   - `📊 Session 334: Found project research context for {project}: has_research=True`
   - `📊 Session 334: Enhanced topic with project name`
   - `📊 Session 334: Enhanced query with project context`
   - `📊 Session 334: Injected project research context for executive review`
   - `📊 Session 334: Enhanced prompt with project research`

### Verification Script
```python
from agents.workflow_orchestration_agent import WorkflowOrchestrationAgent
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()
project_id = '27ebd338-8fa3-415e-a87a-fe95a068f8d5'  # Donkey Betz Podcast

agent = WorkflowOrchestrationAgent(user=user, project_id=project_id)
context = agent._get_project_research_context()

print(f'has_research: {context.get("has_research")}')
print(f'project_name: {context.get("project_name")}')
print(f'has competitor_insights: {bool(context.get("competitor_insights"))}')
print(f'has customer_insights: {bool(context.get("customer_insights"))}')
```

---

## Files Modified

| File | Changes |
|------|---------|
| `agents/workflow_orchestration_agent.py` | Added `_get_project_research_context()` (lines 692-780), enhanced `_execute_web_search_step()` (lines 1135-1157), `_execute_coleadership_step()` (lines 1308-1337), `_execute_image_generation_step()` (lines 1711-1745) |
| `00-START-NEXT-SESSION.md` | Updated for Session 335 |

---

## Key Principle

**"Agents still do their own research - project context is GUIDANCE, not replacement"**

This was a specific user requirement. We never skip research steps; we enhance them with project context to make them more targeted and relevant.

---

## Next Steps

1. Apply same pattern to other creative agents (ImageAgent, VideoAgent, etc.)
2. Add project context to single-step generation (not just workflows)
3. Show project context in UI when generating content
