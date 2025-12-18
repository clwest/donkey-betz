"""
Multi-Turn Task Memory Service - Session 482

Tracks multi-step tasks across conversation turns, enabling:
- Task state persistence across messages
- Resume interrupted tasks
- Track progress through multi-step workflows
- Remember context between conversation turns

Examples:
- User: "Help me create a brand identity" (starts multi-step task)
- User: "Use blue and white" (continues with stored context)
- User: "What were we working on?" (retrieves active task)
"""

import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of a tracked task."""
    ACTIVE = 'active'
    PAUSED = 'paused'
    COMPLETED = 'completed'
    ABANDONED = 'abandoned'


@dataclass
class TaskStep:
    """A single step in a multi-step task."""
    name: str
    description: str
    status: str = 'pending'  # pending, in_progress, completed, skipped
    result: Any = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def start(self):
        """Mark step as in progress."""
        self.status = 'in_progress'
        self.started_at = datetime.now()

    def complete(self, result: Any = None):
        """Mark step as completed."""
        self.status = 'completed'
        self.completed_at = datetime.now()
        if result:
            self.result = result

    def skip(self, reason: str = ''):
        """Mark step as skipped."""
        self.status = 'skipped'
        self.metadata['skip_reason'] = reason


@dataclass
class TrackedTask:
    """A multi-turn task being tracked."""
    task_id: str
    task_type: str  # 'brand_identity', 'research', 'content_creation', etc.
    description: str
    status: TaskStatus = TaskStatus.ACTIVE
    steps: List[TaskStep] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_current_step(self) -> Optional[TaskStep]:
        """Get the current in-progress step."""
        for step in self.steps:
            if step.status == 'in_progress':
                return step
        return None

    def get_next_step(self) -> Optional[TaskStep]:
        """Get the next pending step."""
        for step in self.steps:
            if step.status == 'pending':
                return step
        return None

    def get_progress(self) -> Dict[str, Any]:
        """Get task progress as percentage and step counts."""
        total = len(self.steps)
        if total == 0:
            return {'percentage': 0, 'completed': 0, 'total': 0}

        completed = sum(1 for s in self.steps if s.status in ('completed', 'skipped'))
        return {
            'percentage': int((completed / total) * 100),
            'completed': completed,
            'total': total,
            'current_step': self.get_current_step(),
            'next_step': self.get_next_step()
        }

    def update_context(self, **kwargs):
        """Update task context with new information."""
        self.context.update(kwargs)
        self.updated_at = datetime.now()

    def is_stale(self, hours: int = 24) -> bool:
        """Check if task has been inactive for too long."""
        return datetime.now() - self.updated_at > timedelta(hours=hours)


class TaskMemoryService:
    """
    Service to track multi-turn tasks across conversation.

    Features:
    - Create and track multi-step tasks
    - Persist task state across messages
    - Resume interrupted tasks
    - Automatic task timeout/cleanup
    """

    # Task templates with predefined steps
    TASK_TEMPLATES = {
        'brand_identity': {
            'description': 'Create a complete brand identity',
            'steps': [
                TaskStep('research', 'Research industry and competitors'),
                TaskStep('strategy', 'Define brand strategy and positioning'),
                TaskStep('visual_identity', 'Create visual identity (colors, typography)'),
                TaskStep('logo', 'Design logo options'),
                TaskStep('assets', 'Generate brand assets'),
                TaskStep('guidelines', 'Create brand guidelines document'),
            ]
        },
        'content_series': {
            'description': 'Create a content series',
            'steps': [
                TaskStep('planning', 'Plan content series structure'),
                TaskStep('research', 'Research topics and trends'),
                TaskStep('outline', 'Create content outlines'),
                TaskStep('creation', 'Generate content pieces'),
                TaskStep('review', 'Review and refine content'),
            ]
        },
        'video_production': {
            'description': 'Produce a video',
            'steps': [
                TaskStep('concept', 'Define video concept and script'),
                TaskStep('storyboard', 'Create storyboard'),
                TaskStep('assets', 'Generate visual assets'),
                TaskStep('animation', 'Create video/animation'),
                TaskStep('audio', 'Add voiceover and music'),
                TaskStep('finalize', 'Final edits and export'),
            ]
        },
        'market_research': {
            'description': 'Conduct market research',
            'steps': [
                TaskStep('scope', 'Define research scope'),
                TaskStep('competitors', 'Analyze competitors'),
                TaskStep('customers', 'Research customer segments'),
                TaskStep('trends', 'Identify market trends'),
                TaskStep('report', 'Generate research report'),
            ]
        },
        'job_search': {
            'description': 'Job search and application',
            'steps': [
                TaskStep('profile', 'Review/update profile and skills'),
                TaskStep('search', 'Search for matching opportunities'),
                TaskStep('resume', 'Tailor resume for target roles'),
                TaskStep('apply', 'Apply to selected positions'),
                TaskStep('track', 'Track application status'),
            ]
        },
    }

    # Keywords that indicate task types
    TASK_DETECTION_KEYWORDS = {
        'brand_identity': ['brand identity', 'branding', 'brand package', 'logo and colors'],
        'content_series': ['content series', 'blog series', 'video series', 'content plan'],
        'video_production': ['create video', 'produce video', 'make a video', 'video project'],
        'market_research': ['market research', 'competitor analysis', 'market analysis'],
        'job_search': ['find jobs', 'job search', 'looking for work', 'job hunt'],
    }

    def __init__(self):
        self.tasks: Dict[str, TrackedTask] = {}
        self.active_task_id: Optional[str] = None

    def detect_task_type(self, message: str) -> Optional[str]:
        """Detect if message indicates a multi-step task."""
        message_lower = message.lower()

        for task_type, keywords in self.TASK_DETECTION_KEYWORDS.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return task_type

        return None

    def create_task(
        self,
        task_type: str,
        description: Optional[str] = None,
        initial_context: Optional[Dict[str, Any]] = None
    ) -> TrackedTask:
        """
        Create a new tracked task from a template.

        Args:
            task_type: Type of task (must match a template)
            description: Optional custom description
            initial_context: Initial context data

        Returns:
            The created TrackedTask
        """
        import uuid

        template = self.TASK_TEMPLATES.get(task_type)
        if not template:
            # Create a generic task
            task = TrackedTask(
                task_id=str(uuid.uuid4())[:8],
                task_type=task_type,
                description=description or f"{task_type} task",
                context=initial_context or {}
            )
        else:
            # Create from template with copied steps
            task = TrackedTask(
                task_id=str(uuid.uuid4())[:8],
                task_type=task_type,
                description=description or template['description'],
                steps=[
                    TaskStep(
                        name=s.name,
                        description=s.description,
                        status='pending'
                    ) for s in template['steps']
                ],
                context=initial_context or {}
            )

        # Store and make active
        self.tasks[task.task_id] = task
        self.active_task_id = task.task_id

        logger.info(f"📋 Created task '{task_type}' with {len(task.steps)} steps (ID: {task.task_id})")

        return task

    def get_active_task(self) -> Optional[TrackedTask]:
        """Get the currently active task."""
        if self.active_task_id and self.active_task_id in self.tasks:
            task = self.tasks[self.active_task_id]
            if task.status == TaskStatus.ACTIVE:
                return task
        return None

    def start_next_step(self) -> Optional[TaskStep]:
        """Start the next pending step in the active task."""
        task = self.get_active_task()
        if not task:
            return None

        next_step = task.get_next_step()
        if next_step:
            next_step.start()
            task.updated_at = datetime.now()
            logger.info(f"▶️ Started step '{next_step.name}' in task {task.task_id}")

        return next_step

    def complete_current_step(self, result: Any = None) -> Optional[TaskStep]:
        """Complete the current step and return the next one."""
        task = self.get_active_task()
        if not task:
            return None

        current = task.get_current_step()
        if current:
            current.complete(result)
            task.updated_at = datetime.now()
            logger.info(f"✅ Completed step '{current.name}' in task {task.task_id}")

        # Check if all steps are done
        progress = task.get_progress()
        if progress['percentage'] == 100:
            task.status = TaskStatus.COMPLETED
            logger.info(f"🎉 Task {task.task_id} completed!")

        return task.get_next_step()

    def update_task_context(self, **kwargs) -> bool:
        """Update context of the active task."""
        task = self.get_active_task()
        if not task:
            return False

        task.update_context(**kwargs)
        logger.debug(f"📝 Updated context for task {task.task_id}: {list(kwargs.keys())}")
        return True

    def get_task_context(self) -> Dict[str, Any]:
        """Get the current task context."""
        task = self.get_active_task()
        if task:
            return {
                'task_id': task.task_id,
                'task_type': task.task_type,
                'description': task.description,
                'progress': task.get_progress(),
                'context': task.context,
                'current_step': task.get_current_step(),
                'next_step': task.get_next_step(),
            }
        return {}

    def pause_task(self) -> bool:
        """Pause the active task."""
        task = self.get_active_task()
        if task:
            task.status = TaskStatus.PAUSED
            logger.info(f"⏸️ Paused task {task.task_id}")
            return True
        return False

    def resume_task(self, task_id: Optional[str] = None) -> Optional[TrackedTask]:
        """Resume a paused task."""
        if task_id:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = TaskStatus.ACTIVE
                self.active_task_id = task_id
                logger.info(f"▶️ Resumed task {task_id}")
                return task
        else:
            # Resume most recent paused task
            paused_tasks = [
                t for t in self.tasks.values()
                if t.status == TaskStatus.PAUSED
            ]
            if paused_tasks:
                task = max(paused_tasks, key=lambda t: t.updated_at)
                task.status = TaskStatus.ACTIVE
                self.active_task_id = task.task_id
                logger.info(f"▶️ Resumed task {task.task_id}")
                return task

        return None

    def abandon_task(self) -> bool:
        """Abandon the active task."""
        task = self.get_active_task()
        if task:
            task.status = TaskStatus.ABANDONED
            self.active_task_id = None
            logger.info(f"🚫 Abandoned task {task.task_id}")
            return True
        return False

    def get_task_summary(self) -> str:
        """Get a human-readable summary of the active task."""
        task = self.get_active_task()
        if not task:
            return "No active task."

        progress = task.get_progress()
        current = task.get_current_step()
        next_step = task.get_next_step()

        lines = [
            f"**Active Task:** {task.description}",
            f"**Progress:** {progress['percentage']}% ({progress['completed']}/{progress['total']} steps)"
        ]

        if current:
            lines.append(f"**Current Step:** {current.description}")
        elif next_step:
            lines.append(f"**Next Step:** {next_step.description}")

        if task.context:
            lines.append(f"**Context:** {', '.join(f'{k}={v}' for k, v in list(task.context.items())[:3])}")

        return "\n".join(lines)

    def cleanup_stale_tasks(self, hours: int = 24) -> int:
        """Clean up tasks that haven't been updated in a while."""
        stale_count = 0
        for task_id, task in list(self.tasks.items()):
            if task.is_stale(hours) and task.status == TaskStatus.ACTIVE:
                task.status = TaskStatus.ABANDONED
                if self.active_task_id == task_id:
                    self.active_task_id = None
                stale_count += 1
                logger.info(f"🧹 Cleaned up stale task {task_id}")

        return stale_count

    def format_for_prompt(self) -> str:
        """Format active task context for injection into AI prompt."""
        task = self.get_active_task()
        if not task:
            return ""

        progress = task.get_progress()
        lines = [
            "\n## Active Task Context\n",
            f"**Task:** {task.description} ({task.task_type})",
            f"**Progress:** {progress['percentage']}% complete ({progress['completed']}/{progress['total']} steps)",
        ]

        current = task.get_current_step()
        if current:
            lines.append(f"**Current Step:** {current.name} - {current.description}")

        next_step = task.get_next_step()
        if next_step:
            lines.append(f"**Next Step:** {next_step.name} - {next_step.description}")

        if task.context:
            lines.append("\n**Collected Information:**")
            for key, value in task.context.items():
                lines.append(f"- {key}: {value}")

        lines.append("\n*Continue helping with this task. Build on the collected context.*\n")

        return "\n".join(lines)


# Singleton instances per user session
_services: Dict[str, TaskMemoryService] = {}


def get_task_memory_service(session_id: str = 'default') -> TaskMemoryService:
    """Get or create a task memory service for a session."""
    if session_id not in _services:
        _services[session_id] = TaskMemoryService()
    return _services[session_id]


def clear_task_memory_service(session_id: str = 'default') -> None:
    """Clear a session's task memory service."""
    if session_id in _services:
        del _services[session_id]
