# Session 120: Agent Tracking System Design

**Created:** November 17, 2025
**Status:** Design Phase
**Priority:** 4 of 4 (User's architectural improvement plan)

---

## 🎯 Problem Statement

**User Feedback:** "We don't have any way of tracking Agents with Projects"

**Current State:**
- ✅ 51 agent files in `ai_core/agents/`
- ✅ 10 dedicated agents (CreativeDirectorAgent, EditingOrchestratorAgent, etc.)
- ✅ Agent database models exist (UnifiedAgentTemplate, AgentExecution)
- ❌ **NO link between agents and projects**
- ❌ **NO tracking of which agents contributed to which content**
- ❌ **NO visibility of agent activity per project**

**Goal:** Create a comprehensive agent tracking system that shows:
1. Which agents contributed to a project
2. What content each agent created (images, videos, audio)
3. Agent activity timeline per project
4. Agent performance metrics per project

---

## 🔍 System Investigation Results

### 1. Agent System Architecture

**Agent Models (`agents/models.py`):**
```python
class UnifiedAgentTemplate(UnifiedBaseModel):
    # Agent definition: name, capabilities, specialization, system_prompt
    # 20+ specializations: research, content, creative, marketing, etc.

class AgentExecution(UnifiedBaseModel):
    # Individual agent execution instances
    # Links: template, user, task, status, results
```

**Agent Files (`ai_core/agents/`):**
- Total: 51 agent files
- Key agents:
  - `creative_director_agent.py` - Image variation generation with learning
  - `editing_orchestrator_agent.py` - Multi-operation video editing
  - `brand_style_agent.py` - Brand consistency
  - `iteration_agent.py` - Iterative improvements
  - `reference_library_agent.py` - Reference management
  - `template_manager_agent.py` - Template handling
  - `version_control_agent.py` - Version tracking
  - `workflow_coordinator_agent.py` - Workflow orchestration
  - And 43 more specialized agents

**Current Agent Usage:**
- Agents are called via AI Assistant tool functions
- Agents use `AgentMemoryInterface` for learning
- Agents save to `ImageHistory`, `VideoHistory` but DON'T track themselves
- No database link between AgentExecution and CreativeProject

### 2. Content Models (`content/models.py`)

**Current Content Tracking:**
```python
class ImageHistory:
    user, session, project  # ✅ Links to user/session/project
    # ❌ NO agent field

class VideoHistory:
    user, session, project  # ✅ Links to user/session/project
    # ❌ NO agent field

class AudioHistory:
    user, session, project  # ✅ Links to user/session/project
    # ❌ NO agent field
```

**Gap:** Content knows WHAT was created and WHERE (project), but NOT WHO (agent) created it.

### 3. Existing Related Features

**Co-Leadership Decisions (`coleadership/models.py`):**
```python
class AgentRecommendation:
    decision, agent_template, stance, summary, confidence
```
- ✅ Links agents to decisions
- ✅ Shows agent recommendations in Decision Timeline
- ✅ Tracks agent correctness vs human override
- ❌ Only for decisions, not content creation

**Decision Timeline (Already Working):**
- Shows agent recommendations per project
- Displays agent stance (Support/Oppose)
- Tracks AI vs Human correctness
- Beautiful UI in project details

---

## 💡 Proposed Solution: Agent Contribution Tracking

### Option 1: Add Agent Field to Content Models (SIMPLE)

**Pros:**
- ✅ Minimal code changes
- ✅ Fast to implement
- ✅ Direct relationship
- ✅ Easy queries

**Cons:**
- ❌ Modifies 3 existing models
- ❌ Requires database migration
- ❌ Doesn't support multi-agent collaboration

**Implementation:**
```python
class ImageHistory(models.Model):
    # ... existing fields ...
    agent = models.ForeignKey(
        'agents.UnifiedAgentTemplate',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='generated_images',
        help_text="Agent that generated this image"
    )

class VideoHistory(models.Model):
    # ... existing fields ...
    agent = models.ForeignKey(
        'agents.UnifiedAgentTemplate',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='generated_videos',
        help_text="Agent that generated this video"
    )

class AudioHistory(models.Model):
    # ... existing fields ...
    agent = models.ForeignKey(
        'agents.UnifiedAgentTemplate',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='generated_audio',
        help_text="Agent that generated this audio"
    )
```

### Option 2: Through Model for Many-to-Many (FLEXIBLE)

**Pros:**
- ✅ Supports multi-agent collaboration
- ✅ Tracks contribution details (role, percentage)
- ✅ Doesn't modify existing models
- ✅ More flexible for future features

**Cons:**
- ❌ More complex queries
- ❌ Additional model to maintain
- ❌ Slightly slower queries

**Implementation:**
```python
class AgentContribution(UnifiedBaseModel):
    """
    Tracks which agents contributed to which content/project.
    Supports multi-agent collaboration with roles and percentages.
    """
    # Agent reference
    agent = models.ForeignKey(
        'agents.UnifiedAgentTemplate',
        on_delete=models.CASCADE,
        related_name='contributions'
    )

    # What they contributed to
    project = models.ForeignKey(
        'content.CreativeProject',
        on_delete=models.CASCADE,
        related_name='agent_contributions'
    )

    # Optional: Link to specific content
    image = models.ForeignKey(
        'content.ImageHistory',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='agent_contributions'
    )

    video = models.ForeignKey(
        'content.VideoHistory',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='agent_contributions'
    )

    audio = models.ForeignKey(
        'content.AudioHistory',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='agent_contributions'
    )

    # Contribution details
    contribution_type = models.CharField(
        max_length=50,
        choices=[
            ('generation', 'Content Generation'),
            ('editing', 'Editing/Enhancement'),
            ('orchestration', 'Workflow Orchestration'),
            ('analysis', 'Analysis/Planning'),
            ('recommendation', 'Recommendation'),
        ]
    )

    contribution_role = models.CharField(
        max_length=100,
        help_text="Role in creation (e.g., 'Primary Creator', 'Style Advisor', 'Editor')"
    )

    contribution_percentage = models.IntegerField(
        default=100,
        help_text="Contribution percentage (0-100)"
    )

    # Execution details
    execution = models.ForeignKey(
        'agents.AgentExecution',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='content_contributions'
    )

    # Metadata
    task_description = models.TextField(
        blank=True,
        help_text="What the agent did"
    )

    execution_time_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="How long it took"
    )

    tokens_used = models.IntegerField(
        null=True,
        blank=True,
        help_text="AI tokens consumed"
    )

    class Meta:
        db_table = 'agent_contributions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['agent', '-created_at']),
        ]
```

### Option 3: Hybrid Approach (RECOMMENDED) ⭐

**Combine both options:**
1. Add `agent` field to content models for PRIMARY agent
2. Create `AgentContribution` model for detailed tracking

**Benefits:**
- ✅ Simple queries for "who created this?" (use direct field)
- ✅ Detailed tracking for multi-agent workflows (use through model)
- ✅ Backward compatible (agent field is nullable)
- ✅ Future-proof for complex orchestrations

---

## 🎨 Frontend UI Design

### Project Detail View - New "Agents" Section

**Location:** After Workflows section in project details modal

**Layout:**
```
┌─────────────────────────────────────────────────────────┐
│ 🤖 Agents (5)                          🔄 Refresh       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ ┌──────────────────────────────────────────────────┐   │
│ │ 🎨 CreativeDirectorAgent                          │   │
│ │ ─────────────────────────────────────────────────│   │
│ │ Contribution: Primary Creator                     │   │
│ │ Content: 12 images, 3 variations                  │   │
│ │ Activity: Last used 2 hours ago                   │   │
│ │ Success: 95% user satisfaction                    │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ ┌──────────────────────────────────────────────────┐   │
│ │ 🎬 EditingOrchestratorAgent                       │   │
│ │ ─────────────────────────────────────────────────│   │
│ │ Contribution: Video Editor                        │   │
│ │ Content: 4 videos edited                          │   │
│ │ Activity: Last used 1 day ago                     │   │
│ │ Performance: 2.3s avg execution                   │   │
│ └──────────────────────────────────────────────────┘   │
│                                                          │
│ [View Agent Timeline]  [View All Contributions]         │
└─────────────────────────────────────────────────────────┘
```

**Agent Card Design:**
- **Header:** Agent display name + emoji/icon
- **Stats:**
  - Contribution count (images/videos/audio)
  - Last activity timestamp
  - Performance metrics (execution time, success rate)
- **Actions:**
  - Click to see agent details
  - View content created by this agent
  - See agent activity timeline

**Agent Activity Timeline:**
```
┌─────────────────────────────────────────────────────────┐
│ Agent Activity Timeline                                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ 📅 Nov 17, 2025 - 2:30 PM                               │
│   🎨 CreativeDirectorAgent                              │
│   Generated 5 logo variations → User chose #3           │
│   ─────────────────────────────────────────────────     │
│                                                          │
│ 📅 Nov 17, 2025 - 1:15 PM                               │
│   🎬 EditingOrchestratorAgent                           │
│   Chained 3 videos + added text overlays               │
│   ─────────────────────────────────────────────────     │
│                                                          │
│ 📅 Nov 16, 2025 - 4:45 PM                               │
│   🎨 CreativeDirectorAgent                              │
│   Enhanced image #12 with style transfer                │
│   ─────────────────────────────────────────────────     │
└─────────────────────────────────────────────────────────┘
```

---

## 📋 Implementation Plan

### Phase 1: Database Models (1-2 hours)

**Tasks:**
1. Create `AgentContribution` model in `agents/models.py`
2. Add migration for new model
3. Add `agent` field to ImageHistory, VideoHistory, AudioHistory (nullable)
4. Create migration for content model changes
5. Run migrations
6. Test database relationships

**Files to Modify:**
- `agents/models.py` - Add AgentContribution model
- `content/models.py` - Add agent ForeignKey to content models
- Migrations for both apps

### Phase 2: Backend API (2-3 hours)

**Tasks:**
1. Create `AgentContributionService` for tracking
2. Modify agent execution to auto-track contributions
3. Create API endpoint: `/api/v1/projects/<id>/agents/`
4. Create API endpoint: `/api/v1/projects/<id>/agent-timeline/`
5. Update content creation to record agent

**Files to Create:**
- `agents/services/contribution_tracking.py`
- New views in `agents/views.py`

**Files to Modify:**
- `ai_core/agents/creative_director_agent.py` - Track contributions
- `ai_core/agents/editing_orchestrator_agent.py` - Track contributions
- `core/views_image.py` - Record agent when creating content
- `core/views_video.py` - Record agent when creating content

### Phase 3: Frontend UI (2-3 hours)

**Tasks:**
1. Add "Agents" section to project detail modal
2. Create `refreshProjectAgents()` function
3. Create agent cards with stats
4. Create agent timeline view
5. Style with purple/neon theme matching Decision Timeline

**Files to Modify:**
- `ai_core/templates/ai_image_studio.html`
  - Add Agents section (~150 lines)
  - Add JavaScript functions (~200 lines)

### Phase 4: Testing & Polish (1-2 hours)

**Tasks:**
1. Create test project with multiple agents
2. Verify agent tracking works
3. Test timeline display
4. Test API endpoints
5. Polish UI styling
6. Add loading states and error handling

---

## 🎯 Success Criteria

**Phase 1 (Database):**
- ✅ AgentContribution model created and migrated
- ✅ Content models have agent field
- ✅ Can query agents per project
- ✅ Can query content per agent

**Phase 2 (Backend):**
- ✅ Agent contributions auto-tracked during execution
- ✅ API returns list of agents for project
- ✅ API returns agent activity timeline
- ✅ Content creation records which agent was used

**Phase 3 (Frontend):**
- ✅ Agents section visible in project details
- ✅ Agent cards show stats and contribution count
- ✅ Timeline shows chronological agent activity
- ✅ Beautiful UI matching existing design

**Phase 4 (Testing):**
- ✅ Can see which agents contributed to a project
- ✅ Can see what content each agent created
- ✅ Timeline shows complete agent activity history
- ✅ No errors or performance issues

---

## 🔄 Integration with Existing Features

### Decision Timeline Integration
- Agents section shows agent WORK (content created)
- Decision Timeline shows agent RECOMMENDATIONS (decisions made)
- Complementary views of agent activity

### Workflows Integration
- Track which agents executed workflow steps
- Show agent contribution percentage in workflow results
- Link workflow executions to agent contributions

### Analytics Dashboard Integration
- Add agent performance metrics
- Show most productive agents
- Track agent success rates per project

---

## 💾 Data Examples

**Agent Contribution Record:**
```json
{
    "id": "abc-123",
    "agent": {
        "name": "CreativeDirectorAgent",
        "display_name": "🎨 Creative Director",
        "specialization": "creative"
    },
    "project": {
        "id": "project-456",
        "name": "Three cartoon style logos for mechanic shop"
    },
    "image": {
        "id": "image-789",
        "sequential_number": 199
    },
    "contribution_type": "generation",
    "contribution_role": "Primary Creator",
    "contribution_percentage": 100,
    "task_description": "Generated 5 logo variations with cartoon style",
    "execution_time_seconds": 12.5,
    "tokens_used": 1500,
    "created_at": "2025-11-17T14:30:00Z"
}
```

**API Response: `/api/v1/projects/<id>/agents/`**
```json
{
    "success": true,
    "project": {
        "id": "project-456",
        "name": "Three cartoon style logos for mechanic shop"
    },
    "agents": [
        {
            "agent": {
                "name": "CreativeDirectorAgent",
                "display_name": "🎨 Creative Director"
            },
            "contribution_count": 15,
            "content_breakdown": {
                "images": 12,
                "videos": 3,
                "audio": 0
            },
            "last_activity": "2025-11-17T14:30:00Z",
            "total_execution_time": 145.5,
            "total_tokens": 18500,
            "avg_satisfaction": 0.95
        },
        {
            "agent": {
                "name": "EditingOrchestratorAgent",
                "display_name": "🎬 Video Editor"
            },
            "contribution_count": 4,
            "content_breakdown": {
                "images": 0,
                "videos": 4,
                "audio": 0
            },
            "last_activity": "2025-11-16T16:45:00Z",
            "total_execution_time": 45.2,
            "total_tokens": 5200,
            "avg_execution_time": 11.3
        }
    ],
    "total_agents": 2
}
```

---

## 🚀 Recommended Next Steps

1. **Get User Approval** - Show this design and get feedback
2. **Choose Implementation Option** - Hybrid approach recommended
3. **Implement Phase 1** - Database models and migrations
4. **Implement Phase 2** - Backend API and tracking
5. **Implement Phase 3** - Frontend UI
6. **Test & Polish** - Phase 4

**Estimated Total Time:** 6-10 hours
**Complexity:** Medium
**Impact:** High (fills major gap in project visibility)

---

## 📝 Notes

- This design builds on existing patterns (Decision Timeline, Workflows)
- Uses consistent UI styling (purple/neon theme)
- Backward compatible (nullable fields, through model)
- Extensible for future features (multi-agent collaboration)
- Aligns with user's "one step at a time" approach

**Ready for user review and approval!**
