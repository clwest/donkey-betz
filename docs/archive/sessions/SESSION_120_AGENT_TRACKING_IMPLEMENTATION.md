# Session 120: Agent Tracking Implementation Plan

**Created:** November 17, 2025
**Status:** Ready for Implementation
**Estimated Time:** 6-10 hours total

---

## 📋 Implementation Checklist

### Phase 1: Database Models ✅ (1-2 hours)
- [ ] Create `AgentContribution` model in `agents/models.py`
- [ ] Add `agent` field to `ImageHistory` model
- [ ] Add `agent` field to `VideoHistory` model
- [ ] Add `agent` field to `AudioHistory` model
- [ ] Create and run migrations
- [ ] Test database relationships in Django shell

### Phase 2: Backend API ✅ (2-3 hours)
- [ ] Create `AgentContributionService` class
- [ ] Modify `CreativeDirectorAgent` to track contributions
- [ ] Modify `EditingOrchestratorAgent` to track contributions
- [ ] Create `/api/v1/projects/<id>/agents/` endpoint
- [ ] Create `/api/v1/projects/<id>/agent-timeline/` endpoint
- [ ] Update content creation to record agent
- [ ] Test API endpoints with Postman/curl

### Phase 3: Frontend UI ✅ (2-3 hours)
- [ ] Add "Agents" section to project detail modal
- [ ] Create `refreshProjectAgents()` JavaScript function
- [ ] Create `showAgentTimeline()` JavaScript function
- [ ] Style agent cards with purple/neon theme
- [ ] Add loading states
- [ ] Add error handling
- [ ] Test UI in browser

### Phase 4: Testing & Polish ✅ (1-2 hours)
- [ ] Create test project with multiple agents
- [ ] Generate content using different agents
- [ ] Verify agent tracking displays correctly
- [ ] Test timeline chronological order
- [ ] Check performance with many contributions
- [ ] Polish UI styling and transitions
- [ ] Update documentation

---

## 💻 Code Implementation

### Phase 1: Database Models

#### 1.1 Add AgentContribution Model

**File:** `agents/models.py`

**Location:** After `AgentExecution` class (~line 650)

```python
class AgentContribution(UnifiedBaseModel):
    """
    Session 120: Track which agents contributed to which content/project.

    Supports both simple single-agent tracking and complex multi-agent
    collaboration workflows.
    """

    # Agent reference
    agent = models.ForeignKey(
        UnifiedAgentTemplate,
        on_delete=models.CASCADE,
        related_name='contributions',
        help_text="Agent that made this contribution"
    )

    # Project reference (always required)
    project = models.ForeignKey(
        'content.CreativeProject',
        on_delete=models.CASCADE,
        related_name='agent_contributions',
        help_text="Project this contribution belongs to"
    )

    # Optional: Link to specific content (one of these)
    image = models.ForeignKey(
        'content.ImageHistory',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='agent_contributions',
        help_text="Image created/edited by agent"
    )

    video = models.ForeignKey(
        'content.VideoHistory',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='agent_contributions',
        help_text="Video created/edited by agent"
    )

    audio = models.ForeignKey(
        'content.AudioHistory',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='agent_contributions',
        help_text="Audio created/edited by agent"
    )

    # Contribution details
    CONTRIBUTION_TYPES = [
        ('generation', 'Content Generation'),
        ('editing', 'Editing/Enhancement'),
        ('orchestration', 'Workflow Orchestration'),
        ('analysis', 'Analysis/Planning'),
        ('recommendation', 'Recommendation'),
        ('iteration', 'Iterative Improvement'),
    ]

    contribution_type = models.CharField(
        max_length=50,
        choices=CONTRIBUTION_TYPES,
        default='generation',
        help_text="Type of contribution"
    )

    contribution_role = models.CharField(
        max_length=100,
        default="Primary Creator",
        help_text="Role in creation process"
    )

    contribution_percentage = models.IntegerField(
        default=100,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Contribution percentage (0-100)"
    )

    # Execution tracking
    execution = models.ForeignKey(
        AgentExecution,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='content_contributions',
        help_text="Link to agent execution record"
    )

    task_description = models.TextField(
        blank=True,
        help_text="Description of what agent did"
    )

    # Performance metrics
    execution_time_seconds = models.FloatField(
        null=True,
        blank=True,
        help_text="Execution time in seconds"
    )

    tokens_used = models.IntegerField(
        null=True,
        blank=True,
        help_text="AI tokens consumed"
    )

    # User feedback (optional)
    user_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="User rating (1-5 stars)"
    )

    user_selected = models.BooleanField(
        default=False,
        help_text="True if user selected this agent's output as favorite"
    )

    class Meta:
        db_table = 'agent_contributions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', '-created_at']),
            models.Index(fields=['agent', '-created_at']),
            models.Index(fields=['contribution_type']),
        ]
        verbose_name = "Agent Contribution"
        verbose_name_plural = "Agent Contributions"

    def __str__(self):
        content_type = "project"
        if self.image:
            content_type = f"image #{self.image.get_sequential_number()}"
        elif self.video:
            content_type = f"video #{self.video.get_sequential_number()}"
        elif self.audio:
            content_type = f"audio #{self.audio.id}"

        return f"{self.agent.display_name} → {content_type} ({self.contribution_type})"

    @property
    def content_reference(self):
        """Get reference to the content item"""
        if self.image:
            return {'type': 'image', 'id': str(self.image.id), 'number': self.image.get_sequential_number()}
        elif self.video:
            return {'type': 'video', 'id': str(self.video.id), 'number': self.video.get_sequential_number()}
        elif self.audio:
            return {'type': 'audio', 'id': str(self.audio.id)}
        return {'type': 'project', 'id': str(self.project.id)}
```

#### 1.2 Add Agent Field to Content Models

**File:** `content/models.py`

**ImageHistory changes (add after `project` field, ~line 1850):**
```python
    # Session 120: Track which agent created this image
    agent = models.ForeignKey(
        'agents.UnifiedAgentTemplate',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='generated_images',
        help_text="Agent that generated this image (if created by agent)"
    )
```

**VideoHistory changes (add after `project` field, ~line 2050):**
```python
    # Session 120: Track which agent created this video
    agent = models.ForeignKey(
        'agents.UnifiedAgentTemplate',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='generated_videos',
        help_text="Agent that generated this video (if created by agent)"
    )
```

**AudioHistory changes (add after `project` field, ~line 2200):**
```python
    # Session 120: Track which agent created this audio
    agent = models.ForeignKey(
        'agents.UnifiedAgentTemplate',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='generated_audio',
        help_text="Agent that generated this audio (if created by agent)"
    )
```

#### 1.3 Create Migrations

```bash
# Create migrations
python manage.py makemigrations agents
python manage.py makemigrations content

# Review migrations
python manage.py sqlmigrate agents 00XX_add_agent_contribution
python manage.py sqlmigrate content 00XX_add_agent_field

# Run migrations
python manage.py migrate
```

---

### Phase 2: Backend API

#### 2.1 Create AgentContributionService

**File:** `agents/services/contribution_tracking.py` (NEW FILE)

```python
"""
Session 120: Agent Contribution Tracking Service

Provides utilities for tracking agent contributions to projects and content.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from agents.models import UnifiedAgentTemplate, AgentContribution, AgentExecution
from content.models import CreativeProject, ImageHistory, VideoHistory, AudioHistory

logger = logging.getLogger(__name__)


class AgentContributionService:
    """
    Service for tracking and querying agent contributions.
    """

    @staticmethod
    @transaction.atomic
    def track_contribution(
        agent_name: str,
        project: CreativeProject,
        contribution_type: str = 'generation',
        contribution_role: str = 'Primary Creator',
        task_description: str = '',
        image: Optional[ImageHistory] = None,
        video: Optional[VideoHistory] = None,
        audio: Optional[AudioHistory] = None,
        execution_time: Optional[float] = None,
        tokens_used: Optional[int] = None,
        execution: Optional[AgentExecution] = None
    ) -> AgentContribution:
        """
        Track an agent's contribution to a project/content.

        Args:
            agent_name: Name of the agent (e.g., 'CreativeDirectorAgent')
            project: CreativeProject instance
            contribution_type: Type of contribution
            contribution_role: Role description
            task_description: What the agent did
            image/video/audio: Optional content reference
            execution_time: Seconds taken
            tokens_used: AI tokens consumed
            execution: Optional AgentExecution reference

        Returns:
            AgentContribution instance
        """
        try:
            # Get or create agent template
            agent, created = UnifiedAgentTemplate.objects.get_or_create(
                name=agent_name,
                defaults={
                    'display_name': agent_name.replace('Agent', '').replace('_', ' ').title(),
                    'description': f'Agent: {agent_name}',
                    'specialization': 'creative',
                    'system_prompt': '',
                }
            )

            if created:
                logger.info(f"📝 Created new agent template: {agent_name}")

            # Create contribution record
            contribution = AgentContribution.objects.create(
                agent=agent,
                project=project,
                image=image,
                video=video,
                audio=audio,
                contribution_type=contribution_type,
                contribution_role=contribution_role,
                task_description=task_description,
                execution_time_seconds=execution_time,
                tokens_used=tokens_used,
                execution=execution
            )

            content_type = "project"
            if image:
                content_type = f"image #{image.get_sequential_number()}"
            elif video:
                content_type = f"video #{video.get_sequential_number()}"
            elif audio:
                content_type = f"audio #{audio.id}"

            logger.info(f"✅ Tracked contribution: {agent_name} → {content_type}")

            return contribution

        except Exception as e:
            logger.error(f"❌ Failed to track contribution: {str(e)}")
            raise

    @staticmethod
    def get_project_agents(project: CreativeProject) -> List[Dict[str, Any]]:
        """
        Get all agents that contributed to a project with stats.

        Returns:
            List of dicts with agent info and contribution stats
        """
        from django.db.models import Count, Sum, Avg, Max

        # Get agent contribution stats
        agent_stats = AgentContribution.objects.filter(
            project=project
        ).values(
            'agent__id',
            'agent__name',
            'agent__display_name'
        ).annotate(
            total_contributions=Count('id'),
            images_count=Count('image', distinct=True),
            videos_count=Count('video', distinct=True),
            audio_count=Count('audio', distinct=True),
            total_execution_time=Sum('execution_time_seconds'),
            total_tokens=Sum('tokens_used'),
            avg_execution_time=Avg('execution_time_seconds'),
            last_activity=Max('created_at'),
            avg_rating=Avg('user_rating'),
            selected_count=Count('id', filter=models.Q(user_selected=True))
        ).order_by('-total_contributions')

        return list(agent_stats)

    @staticmethod
    def get_project_timeline(project: CreativeProject) -> List[Dict[str, Any]]:
        """
        Get chronological timeline of agent contributions.

        Returns:
            List of contribution events ordered by time
        """
        contributions = AgentContribution.objects.filter(
            project=project
        ).select_related(
            'agent',
            'image',
            'video',
            'audio'
        ).order_by('-created_at')

        timeline = []
        for contrib in contributions:
            # Determine content reference
            content_ref = None
            if contrib.image:
                content_ref = {
                    'type': 'image',
                    'id': str(contrib.image.id),
                    'number': contrib.image.get_sequential_number(),
                    'url': contrib.image.image_url
                }
            elif contrib.video:
                content_ref = {
                    'type': 'video',
                    'id': str(contrib.video.id),
                    'number': contrib.video.get_sequential_number(),
                    'url': contrib.video.video_url
                }
            elif contrib.audio:
                content_ref = {
                    'type': 'audio',
                    'id': str(contrib.audio.id),
                    'url': contrib.audio.audio_url
                }

            timeline.append({
                'id': str(contrib.id),
                'timestamp': contrib.created_at.isoformat(),
                'agent': {
                    'name': contrib.agent.name,
                    'display_name': contrib.agent.display_name
                },
                'contribution_type': contrib.contribution_type,
                'contribution_role': contrib.contribution_role,
                'task_description': contrib.task_description,
                'content': content_ref,
                'execution_time': contrib.execution_time_seconds,
                'tokens_used': contrib.tokens_used,
                'user_selected': contrib.user_selected
            })

        return timeline
```

#### 2.2 Modify Agent to Track Contributions

**File:** `ai_core/agents/creative_director_agent.py`

**Add import at top:**
```python
from agents.services.contribution_tracking import AgentContributionService
```

**Modify `generate_options()` method (after images are created, ~line 180):**
```python
        # Session 120: Track agent contributions
        if session_id:
            # Try to get project from session
            try:
                from ai_core.models import AISession
                session = AISession.objects.get(session_id=session_id)
                if session.project:
                    for image in created_images:
                        AgentContributionService.track_contribution(
                            agent_name='CreativeDirectorAgent',
                            project=session.project,
                            contribution_type='generation',
                            contribution_role='Creative Director',
                            task_description=f'Generated creative variation: {prompt}',
                            image=image,
                            execution_time=None,  # Could add timing
                            tokens_used=None  # Could track
                        )
            except Exception as e:
                logger.warning(f"Could not track contribution: {e}")
```

#### 2.3 Create API Endpoints

**File:** `agents/views.py` (add new views)

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from content.models import CreativeProject
from agents.services.contribution_tracking import AgentContributionService

@api_view(['GET'])
def get_project_agents(request, project_id):
    """
    Session 120: Get all agents that contributed to a project.

    Returns agent stats and contribution counts.
    """
    try:
        project = CreativeProject.objects.get(
            id=project_id,
            user=request.user
        )

        agents = AgentContributionService.get_project_agents(project)

        return Response({
            'success': True,
            'project': {
                'id': str(project.id),
                'name': project.name
            },
            'agents': agents,
            'total': len(agents)
        })

    except CreativeProject.DoesNotExist:
        return Response({
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)


@api_view(['GET'])
def get_project_agent_timeline(request, project_id):
    """
    Session 120: Get chronological timeline of agent activity.
    """
    try:
        project = CreativeProject.objects.get(
            id=project_id,
            user=request.user
        )

        timeline = AgentContributionService.get_project_timeline(project)

        return Response({
            'success': True,
            'project': {
                'id': str(project.id),
                'name': project.name
            },
            'timeline': timeline,
            'total': len(timeline)
        })

    except CreativeProject.DoesNotExist:
        return Response({
            'error': 'Project not found'
        }, status=404)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=500)
```

**File:** `agents/urls.py` (add new routes)

```python
# Session 120: Agent contribution tracking
path(
    'projects/<uuid:project_id>/agents/',
    views.get_project_agents,
    name='get-project-agents'
),
path(
    'projects/<uuid:project_id>/agent-timeline/',
    views.get_project_agent_timeline,
    name='get-project-agent-timeline'
),
```

---

### Phase 3: Frontend UI

#### 3.1 Add Agents Section to Project Detail

**File:** `ai_core/templates/ai_image_studio.html`

**Location:** In project detail modal, after Workflows section (~line 19000)

```javascript
                <!-- Session 120: Agents Tracking -->
                <div class="mb-4">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 style="color: #a78bfa;">🤖 Agents</h5>
                        <div class="btn-group">
                            <button class="btn btn-sm" style="background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%); color: white; border: none;" onclick="refreshProjectAgents('${project.id}')" title="Refresh agents">
                                🔄 Refresh
                            </button>
                            <button class="btn btn-sm btn-info" onclick="showAgentTimeline('${project.id}')" title="View agent activity timeline">
                                📅 Timeline
                            </button>
                        </div>
                    </div>
                    <div id="project-agents-${project.id}">
                        <div class="text-center py-4">
                            <div class="spinner-border" style="color: #a78bfa;" role="status"></div>
                            <p class="mt-2 text-muted">Loading agents...</p>
                        </div>
                    </div>
                </div>
```

#### 3.2 Add JavaScript Functions

**Location:** In `<script>` section with other project functions (~line 19300)

```javascript
        /**
         * Session 120: Refresh agent contributions for a project
         */
        async function refreshProjectAgents(projectId) {
            const container = document.getElementById(`project-agents-${projectId}`);
            if (!container) return;

            try {
                // Show loading
                container.innerHTML = `
                    <div class="text-center py-4">
                        <div class="spinner-border" style="color: #a78bfa;" role="status"></div>
                        <p class="mt-2 text-muted">Loading agents...</p>
                    </div>
                `;

                // Fetch agents
                const response = await fetch(`/api/v1/agents/projects/${projectId}/agents/`, {
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });

                const data = await response.json();

                if (data.success && data.agents && data.agents.length > 0) {
                    // Render agent cards
                    container.innerHTML = data.agents.map(agentStat => {
                        const totalContent = agentStat.images_count + agentStat.videos_count + agentStat.audio_count;
                        const lastActivity = new Date(agentStat.last_activity);
                        const timeAgo = getTimeAgo(lastActivity);

                        // Calculate satisfaction percentage
                        const satisfactionPct = agentStat.avg_rating ?
                            (agentStat.avg_rating / 5 * 100).toFixed(0) : null;

                        // Determine agent emoji based on type
                        const agentEmoji = agentStat.agent__name.includes('Creative') ? '🎨' :
                                          agentStat.agent__name.includes('Editing') ? '🎬' :
                                          agentStat.agent__name.includes('Brand') ? '🏷️' :
                                          agentStat.agent__name.includes('Iteration') ? '🔄' :
                                          '🤖';

                        return `
                            <div class="card mb-3" style="background: linear-gradient(135deg, rgba(167, 139, 250, 0.1), rgba(124, 58, 237, 0.05)); border: 2px solid rgba(167, 139, 250, 0.3);">
                                <div class="card-body">
                                    <div class="d-flex justify-content-between align-items-start">
                                        <div class="flex-grow-1">
                                            <h6 style="color: #a78bfa; margin-bottom: 0.5rem;">
                                                ${agentEmoji} ${agentStat.agent__display_name}
                                            </h6>
                                            <p class="small text-muted mb-2">
                                                Contribution: ${totalContent} item${totalContent !== 1 ? 's' : ''}
                                            </p>
                                        </div>
                                        <span class="badge" style="background: linear-gradient(135deg, #a78bfa 0%, #7c3aed 100%);">
                                            ${totalContent}
                                        </span>
                                    </div>

                                    <!-- Content Breakdown -->
                                    <div class="row g-2 mb-2">
                                        ${agentStat.images_count > 0 ? `
                                            <div class="col-auto">
                                                <span class="badge" style="background: rgba(59, 130, 246, 0.2); border: 1px solid #3b82f6; color: #60a5fa;">
                                                    🖼️ ${agentStat.images_count} image${agentStat.images_count !== 1 ? 's' : ''}
                                                </span>
                                            </div>
                                        ` : ''}
                                        ${agentStat.videos_count > 0 ? `
                                            <div class="col-auto">
                                                <span class="badge" style="background: rgba(236, 72, 153, 0.2); border: 1px solid #ec4899; color: #f9a8d4;">
                                                    🎬 ${agentStat.videos_count} video${agentStat.videos_count !== 1 ? 's' : ''}
                                                </span>
                                            </div>
                                        ` : ''}
                                        ${agentStat.audio_count > 0 ? `
                                            <div class="col-auto">
                                                <span class="badge" style="background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #34d399;">
                                                    🎤 ${agentStat.audio_count} audio
                                                </span>
                                            </div>
                                        ` : ''}
                                    </div>

                                    <!-- Performance Metrics -->
                                    <div class="row g-2 small text-muted">
                                        <div class="col-md-6">
                                            ⏰ Last activity: ${timeAgo}
                                        </div>
                                        ${agentStat.avg_execution_time ? `
                                            <div class="col-md-6">
                                                ⚡ Avg time: ${agentStat.avg_execution_time.toFixed(1)}s
                                            </div>
                                        ` : ''}
                                        ${satisfactionPct ? `
                                            <div class="col-md-6">
                                                ⭐ Satisfaction: ${satisfactionPct}%
                                            </div>
                                        ` : ''}
                                        ${agentStat.total_tokens ? `
                                            <div class="col-md-6">
                                                🎯 Tokens: ${agentStat.total_tokens.toLocaleString()}
                                            </div>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('');
                } else {
                    container.innerHTML = `
                        <div class="text-center py-4">
                            <p class="text-muted">📭 No agent activity yet</p>
                            <p class="small text-muted">Agents will appear here as they contribute to your project</p>
                        </div>
                    `;
                }

            } catch (error) {
                console.error('Failed to load project agents:', error);
                container.innerHTML = `
                    <div class="text-center py-4">
                        <p class="text-danger">❌ Failed to load agents</p>
                    </div>
                `;
            }
        }

        /**
         * Session 120: Show agent activity timeline
         */
        async function showAgentTimeline(projectId) {
            try {
                // Fetch timeline
                const response = await fetch(`/api/v1/agents/projects/${projectId}/agent-timeline/`, {
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken')
                    }
                });

                const data = await response.json();

                if (!data.success || !data.timeline || data.timeline.length === 0) {
                    showNotification('No agent activity to show', 'info');
                    return;
                }

                // Create timeline modal
                const modalHtml = `
                    <div class="modal fade" id="agent-timeline-modal" tabindex="-1">
                        <div class="modal-dialog modal-lg">
                            <div class="modal-content" style="background: #1a1a1a; border: 2px solid #a78bfa;">
                                <div class="modal-header" style="border-color: rgba(167, 139, 250, 0.3);">
                                    <h5 class="modal-title" style="color: #a78bfa;">🤖 Agent Activity Timeline</h5>
                                    <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                                </div>
                                <div class="modal-body" style="max-height: 600px; overflow-y: auto;">
                                    ${data.timeline.map(event => {
                                        const timestamp = new Date(event.timestamp);
                                        const timeStr = timestamp.toLocaleString();
                                        const timeAgo = getTimeAgo(timestamp);

                                        // Determine content badge
                                        let contentBadge = '';
                                        if (event.content) {
                                            const type = event.content.type;
                                            const emoji = type === 'image' ? '🖼️' : type === 'video' ? '🎬' : '🎤';
                                            const number = event.content.number || '';
                                            contentBadge = `<span class="badge badge-secondary">${emoji} ${type} ${number}</span>`;
                                        }

                                        return `
                                            <div class="card mb-3" style="background: linear-gradient(135deg, rgba(167, 139, 250, 0.1), rgba(124, 58, 237, 0.05)); border-left: 4px solid #a78bfa;">
                                                <div class="card-body">
                                                    <div class="d-flex justify-content-between align-items-start mb-2">
                                                        <h6 style="color: #a78bfa; margin: 0;">
                                                            ${event.agent.display_name}
                                                        </h6>
                                                        <small class="text-muted">${timeAgo}</small>
                                                    </div>
                                                    <p class="mb-2">${event.task_description || event.contribution_type}</p>
                                                    <div class="d-flex gap-2 flex-wrap">
                                                        ${contentBadge}
                                                        <span class="badge" style="background: rgba(167, 139, 250, 0.2); color: #a78bfa;">
                                                            ${event.contribution_role}
                                                        </span>
                                                        ${event.execution_time ? `
                                                            <span class="badge badge-secondary">
                                                                ⚡ ${event.execution_time.toFixed(1)}s
                                                            </span>
                                                        ` : ''}
                                                        ${event.user_selected ? `
                                                            <span class="badge" style="background: #10b981; color: white;">
                                                                ⭐ User Selected
                                                            </span>
                                                        ` : ''}
                                                    </div>
                                                    <div class="small text-muted mt-2">${timeStr}</div>
                                                </div>
                                            </div>
                                        `;
                                    }).join('')}
                                </div>
                            </div>
                        </div>
                    </div>
                `;

                // Remove existing modal
                document.getElementById('agent-timeline-modal')?.remove();

                // Add and show modal
                document.body.insertAdjacentHTML('beforeend', modalHtml);
                const modal = new bootstrap.Modal(document.getElementById('agent-timeline-modal'));
                modal.show();

            } catch (error) {
                console.error('Failed to load agent timeline:', error);
                showNotification('Failed to load agent timeline', 'error');
            }
        }

        // Helper function for relative time
        function getTimeAgo(date) {
            const seconds = Math.floor((new Date() - date) / 1000);

            if (seconds < 60) return 'just now';
            if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
            if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
            if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
            return `${Math.floor(seconds / 604800)}w ago`;
        }

        // Make functions global
        window.refreshProjectAgents = refreshProjectAgents;
        window.showAgentTimeline = showAgentTimeline;
```

---

## 🧪 Testing Plan

### Manual Testing

1. **Create Test Project:**
   ```python
   # Django shell
   from content.models import CreativeProject
   from django.contrib.auth.models import User

   user = User.objects.first()
   project = CreativeProject.objects.create(
       user=user,
       name="Agent Tracking Test Project",
       goal="Test agent tracking feature",
       category="Test"
   )
   ```

2. **Generate Content with Agents:**
   - Use AI Assistant to create images with CreativeDirectorAgent
   - Use multi-operation video editing with EditingOrchestratorAgent
   - Verify contributions are tracked

3. **Test API Endpoints:**
   ```bash
   # Get project agents
   curl http://localhost:8000/api/v1/agents/projects/{PROJECT_ID}/agents/ \
        -H "X-CSRFToken: {TOKEN}"

   # Get agent timeline
   curl http://localhost:8000/api/v1/agents/projects/{PROJECT_ID}/agent-timeline/ \
        -H "X-CSRFToken: {TOKEN}"
   ```

4. **Test Frontend:**
   - Open project in Projects tab
   - Click "View Project Details"
   - Scroll to Agents section
   - Click "Refresh" button
   - Verify agent cards appear with correct stats
   - Click "Timeline" button
   - Verify timeline modal shows chronological events

---

## 📝 Documentation Updates

### Update Session Documentation

**File:** `00-START-NEXT-SESSION.md`

Add to "What's Next" section:
```markdown
### Priority 4: Agent Tracking (COMPLETE) ✅
- ✅ Database models created (AgentContribution)
- ✅ Backend API implemented
- ✅ Frontend UI integrated
- ✅ Agents tracked per project with stats and timeline
```

### Update CLAUDE.md

Add to recent session history:
```markdown
**Session 120:** AGENT TRACKING SYSTEM - COMPLETE! 🤖✨
- Priority 4: Agent tracking for projects implemented
- AgentContribution model tracks which agents created what
- API endpoints return agent stats and activity timeline
- Beautiful UI shows agents per project with metrics
- ~800 lines production code | Reality Score: 100%!
```

---

## ✅ Success Verification

After implementation, verify:

1. ✅ Database models exist and migrate successfully
2. ✅ API endpoints return agent data
3. ✅ Frontend displays agent cards with stats
4. ✅ Timeline modal shows chronological activity
5. ✅ Agent contributions automatically tracked during creation
6. ✅ No errors in browser console or Django logs
7. ✅ Performance is acceptable with many contributions

**Ready to implement!** 🚀
