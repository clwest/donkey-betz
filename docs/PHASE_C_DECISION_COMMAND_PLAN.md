# Phase C: Decision Command Integration - Complete Implementation Plan

**Status:** Planning - Not Started
**Priority:** Option A - Work on this first
**Estimated Time:** 8-12 hours (3-4 sessions)
**Goal:** Integrate creative strategy and planning tools into AI Studio

---

## 🎯 OVERVIEW

**What is Decision Command?**
Decision Command is a creative strategy and planning system that helps users:
- Plan multi-step creative projects
- Organize workflows into campaigns
- Build portfolios of content
- Track project goals and outcomes
- Make strategic decisions about content creation

**Why Build This?**
- Users need project management for complex creative work
- Multiple workflows should be orchestrated together
- Portfolio building requires organization
- Strategic planning improves content quality

**Success Criteria:**
- [ ] Users can create creative projects with multiple workflows
- [ ] Projects track progress and outcomes
- [ ] Portfolio view shows organized content
- [ ] Strategic planning tools help decision-making
- [ ] Integration with existing workflows seamless

---

## 📋 PHASE C TASK BREAKDOWN

### Task C.1: Project Management System (3-4 hours)

**Goal:** Enable users to create and manage creative projects

#### Subtask C.1.1: Database Models (1 hour)
**File:** `content/models.py`

**What to Build:**
```python
class CreativeProject(UnifiedBaseModel):
    """
    A creative project containing multiple workflows
    Example: "Brand Launch Campaign", "Client Portfolio", "Social Media Series"
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    goal = models.TextField(help_text="What's the objective of this project?")
    deadline = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('planning', 'Planning'),
            ('in_progress', 'In Progress'),
            ('review', 'Under Review'),
            ('completed', 'Completed'),
            ('archived', 'Archived')
        ],
        default='planning'
    )

    # Metadata
    total_workflows = models.IntegerField(default=0)
    completed_workflows = models.IntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.status})"

class ProjectWorkflow(models.Model):
    """
    Links workflows to projects
    """
    project = models.ForeignKey(CreativeProject, on_delete=models.CASCADE, related_name='workflows')
    workflow_history = models.ForeignKey('WorkflowHistory', on_delete=models.CASCADE)
    order = models.IntegerField(default=0, help_text="Order in project sequence")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.project.name} - {self.workflow_history.workflow_name}"
```

**Migration Command:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**Success Criteria:**
- [ ] CreativeProject model created
- [ ] ProjectWorkflow link model created
- [ ] Migrations applied successfully
- [ ] Models show in Django admin

---

#### Subtask C.1.2: API Endpoints (1.5 hours)
**File:** `core/views_image.py`

**Endpoints to Create:**

1. **List Projects** - `GET /api/projects/`
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_projects(request):
    """List all projects for current user"""
    projects = CreativeProject.objects.filter(user=request.user)

    project_data = []
    for project in projects:
        project_data.append({
            'id': str(project.id),
            'name': project.name,
            'description': project.description,
            'goal': project.goal,
            'status': project.status,
            'deadline': project.deadline.isoformat() if project.deadline else None,
            'total_workflows': project.workflows.count(),
            'completed_workflows': project.workflows.filter(
                workflow_history__status='completed'
            ).count(),
            'created_at': project.created_at.isoformat()
        })

    return Response({'projects': project_data})
```

2. **Create Project** - `POST /api/projects/`
3. **Get Project Details** - `GET /api/projects/<uuid>/`
4. **Update Project** - `PUT /api/projects/<uuid>/`
5. **Delete Project** - `DELETE /api/projects/<uuid>/`
6. **Add Workflow to Project** - `POST /api/projects/<uuid>/workflows/`
7. **Remove Workflow from Project** - `DELETE /api/projects/<uuid>/workflows/<workflow_id>/`

**URL Routes:**
```python
# In core/urls.py
urlpatterns = [
    # ... existing patterns ...

    # Phase C: Decision Command
    path('api/projects/', list_projects, name='list-projects'),
    path('api/projects/create/', create_project, name='create-project'),
    path('api/projects/<uuid:project_id>/', get_project, name='get-project'),
    path('api/projects/<uuid:project_id>/update/', update_project, name='update-project'),
    path('api/projects/<uuid:project_id>/delete/', delete_project, name='delete-project'),
    path('api/projects/<uuid:project_id>/workflows/', add_workflow_to_project, name='add-workflow'),
    path('api/projects/<uuid:project_id>/workflows/<uuid:workflow_id>/', remove_workflow, name='remove-workflow'),
]
```

**Success Criteria:**
- [ ] All 7 endpoints implemented
- [ ] UUID routing working (not integers!)
- [ ] Authentication enforced
- [ ] Error handling for missing projects
- [ ] Test with curl or Postman

---

#### Subtask C.1.3: Frontend UI (1.5 hours)
**File:** `ai_core/templates/ai_image_studio.html`

**What to Build:**
- New "Projects" tab in AI Studio
- Project list view with cards
- "Create New Project" button
- Project detail view
- Add workflows to projects
- Progress tracking visualization

**UI Structure:**
```html
<!-- Projects Tab -->
<div id="projectsContent" class="tab-content" style="display: none;">
    <!-- Projects List -->
    <div id="projectsList">
        <div class="flex justify-between items-center mb-4">
            <h2 class="text-2xl font-bold">Creative Projects</h2>
            <button onclick="showCreateProjectModal()" class="btn-primary">
                ➕ New Project
            </button>
        </div>

        <!-- Projects Grid -->
        <div id="projectsGrid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <!-- Project cards will be inserted here -->
        </div>
    </div>

    <!-- Project Detail View -->
    <div id="projectDetail" style="display: none;">
        <!-- Project header, workflows, progress -->
    </div>
</div>

<!-- Create Project Modal -->
<div id="createProjectModal" class="modal" style="display: none;">
    <!-- Form for creating new project -->
</div>
```

**JavaScript Functions:**
```javascript
// Load and display projects
async function loadProjects() {
    const response = await fetch('/api/projects/');
    const data = await response.json();
    displayProjects(data.projects);
}

// Create new project
async function createProject(projectData) {
    const response = await fetch('/api/projects/create/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify(projectData)
    });
    return await response.json();
}

// Add workflow to project
async function addWorkflowToProject(projectId, workflowId) {
    const response = await fetch(`/api/projects/${projectId}/workflows/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ workflow_id: workflowId })
    });
    return await response.json();
}
```

**Success Criteria:**
- [ ] Projects tab visible in UI
- [ ] Can create new projects
- [ ] Projects display in grid
- [ ] Can view project details
- [ ] Can add workflows to projects
- [ ] Progress visualization working

---

### Task C.2: Portfolio View (2-3 hours)

**Goal:** Organized view of all user's creative work

#### Subtask C.2.1: Portfolio API (1 hour)
**Endpoint:** `GET /api/portfolio/`

**What it Returns:**
```json
{
    "portfolio": {
        "total_projects": 5,
        "total_workflows": 23,
        "total_images": 150,
        "total_videos": 12,
        "total_audio": 8,
        "categories": {
            "logos": {
                "count": 45,
                "recent": [...]
            },
            "portraits": {
                "count": 30,
                "recent": [...]
            }
        },
        "recent_activity": [...]
    }
}
```

#### Subtask C.2.2: Portfolio UI (2 hours)
- Gallery-style portfolio view
- Filter by project, type, date
- Search across all content
- Export portfolio as PDF or web page

**Success Criteria:**
- [ ] Portfolio endpoint implemented
- [ ] Beautiful gallery UI
- [ ] Filtering and search working
- [ ] Portfolio export feature

---

### Task C.3: Strategic Planning Tools (2-3 hours)

**Goal:** Help users plan and strategize creative projects

#### Subtask C.3.1: Campaign Planner (1.5 hours)
- Campaign creation wizard
- Suggest workflow sequences based on campaign type
- Automated workflow generation for common patterns

**Example Campaigns:**
- "Brand Launch" → Logo + Social Media + Marketing Materials
- "Client Portfolio" → Multiple portraits + upscaling
- "Content Series" → Style Explorer + variations

#### Subtask C.3.2: GPT-5 Strategy Assistant (1 hour)
Enhance GPT-5 assistant with project context:
- "What workflows should I run for a brand launch?"
- "Help me plan a social media campaign"
- "Suggest content for my portfolio"

**Success Criteria:**
- [ ] Campaign templates created
- [ ] Wizard UI implemented
- [ ] GPT-5 gives strategic advice
- [ ] Automated workflow generation working

---

### Task C.4: Multi-Workflow Orchestration (1-2 hours)

**Goal:** Run multiple workflows in sequence automatically

#### What to Build:
- Workflow pipeline builder (drag & drop)
- Automatic output → input chaining
- Batch execution with progress tracking

**Example:**
1. Generate Logo (Logo Creator)
2. Upscale Result (Creative Upscale)
3. Create Variations (Style Explorer)
4. Package for Social (Social Media Pack)

**Success Criteria:**
- [ ] Pipeline builder UI
- [ ] Automatic workflow chaining
- [ ] Batch execution working
- [ ] Progress tracking visible

---

## 🐛 COMMON ISSUES & SOLUTIONS

### Issue: UUID vs Integer Fields
**Problem:** Using IntegerField instead of UUIDField for foreign keys
**Solution:** Always use UUIDField for model references
**Reference:** `docs/UUID_FIELD_PATTERN.md`

### Issue: CSRF Token Errors
**Problem:** Missing or incorrect CSRF token in POST requests
**Solution:** Always include `'X-CSRFToken': getCsrfToken()` in headers

### Issue: Project Not Found (404)
**Problem:** UUID routing not configured correctly
**Solution:** Use `<uuid:project_id>` in URL patterns, not `<int:project_id>`

### Issue: Workflows Not Linking to Projects
**Problem:** ProjectWorkflow relationship not set up correctly
**Solution:** Verify foreign keys point to correct models with correct field types

---

## ✅ PHASE C COMPLETION CHECKLIST

### Task C.1: Project Management ✅
- [ ] Database models created and migrated
- [ ] All 7 API endpoints working
- [ ] Frontend projects tab complete
- [ ] Can create, view, edit, delete projects
- [ ] Can add/remove workflows from projects
- [ ] Progress tracking working

### Task C.2: Portfolio View ✅
- [ ] Portfolio API endpoint working
- [ ] Portfolio UI displays all content
- [ ] Filtering and search functional
- [ ] Export feature working

### Task C.3: Strategic Planning ✅
- [ ] Campaign planner implemented
- [ ] Campaign templates created
- [ ] GPT-5 strategy assistant enhanced
- [ ] Workflow suggestions working

### Task C.4: Multi-Workflow Orchestration ✅
- [ ] Pipeline builder UI complete
- [ ] Workflow chaining functional
- [ ] Batch execution working
- [ ] Progress tracking visible

### Documentation ✅
- [ ] SESSION_60_PHASE_C_COMPLETE.md created
- [ ] CLAUDE.md updated
- [ ] 00-START-NEXT-SESSION.md updated
- [ ] Code comments added

### Testing ✅
- [ ] Create 3 test projects
- [ ] Add workflows to projects
- [ ] Test portfolio view
- [ ] Test campaign planner
- [ ] Test multi-workflow pipeline
- [ ] Verify all features working

---

## 📊 PROGRESS TRACKING

| Task | Status | Time Spent | Notes |
|------|--------|-----------|-------|
| C.1.1: Database Models | ⏳ Not Started | 0h | - |
| C.1.2: API Endpoints | ⏳ Not Started | 0h | - |
| C.1.3: Frontend UI | ⏳ Not Started | 0h | - |
| C.2.1: Portfolio API | ⏳ Not Started | 0h | - |
| C.2.2: Portfolio UI | ⏳ Not Started | 0h | - |
| C.3.1: Campaign Planner | ⏳ Not Started | 0h | - |
| C.3.2: GPT-5 Strategy | ⏳ Not Started | 0h | - |
| C.4: Multi-Workflow | ⏳ Not Started | 0h | - |

**Current Status:** Planning Complete, Ready to Start Implementation
**Next Step:** Begin Task C.1.1 (Database Models)

---

## 🚀 GETTING STARTED

When ready to begin Phase C:

1. Read this entire document
2. Start with Task C.1.1 (Database Models)
3. Work through tasks in order
4. Update progress table as you go
5. Test each subtask before moving to next
6. Document any issues encountered
7. Update completion checklist

**Let's build Decision Command!** 🎯
