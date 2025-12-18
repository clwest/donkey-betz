"""
Streaming Progress Service - Session 482
Session 489: WebSocket Integration

Provides real-time progress updates for agent execution, enabling:
- WebSocket-based progress streaming (Session 489: now connected!)
- SSE (Server-Sent Events) support
- Polling fallback for progress status
- Stage-by-stage execution tracking

Examples:
- Image generation: "Analyzing prompt..." → "Generating image..." → "Processing..." → "Complete!"
- Research: "Searching..." → "Analyzing results..." → "Formatting..." → "Done!"
- Video: "Preparing assets..." → "Rendering..." → "Processing audio..." → "Finalizing..."
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import threading
from queue import Queue

logger = logging.getLogger(__name__)

# Session 489: Map agent names to progress types
AGENT_TO_PROGRESS_TYPE = {
    # Creation agents
    'ImageAgent': 'image_generation',
    'VideoAgent': 'video_generation',
    'AudioAgent': 'audio_generation',
    'ThreeDAgent': 'image_generation',  # Similar stages
    # Editing agents
    'ImageEditingAgent': 'image_generation',
    'VideoEditingAgent': 'video_generation',
    # Research agents
    'ResearchAgent': 'research',
    'CompetitorAnalysisAgent': 'competitor_analysis',
    'CustomerResearchAgent': 'research',
    # Strategy agents
    'ContentStrategyAgent': 'brand_strategy',
    'BrandIdentityAgent': 'brand_strategy',
    'SEOOptimizerAgent': 'research',
    'SocialMediaAgent': 'brand_strategy',
    # Executive agents
    'CTOAgent': 'research',
    'COOAgent': 'research',
    'CreativeDirectorAgent': 'brand_strategy',
    'MeetingCoordinatorAgent': 'research',
    # Workflow
    'WorkflowAgent': 'workflow',
    'AISeriesWorkflowAgent': 'workflow',
    # Default for others
}


class ProgressStage(Enum):
    """Standard progress stages."""
    QUEUED = 'queued'
    STARTING = 'starting'
    PROCESSING = 'processing'
    GENERATING = 'generating'
    REFINING = 'refining'
    FINALIZING = 'finalizing'
    COMPLETE = 'complete'
    ERROR = 'error'


@dataclass
class ProgressUpdate:
    """A single progress update."""
    task_id: str
    stage: str
    message: str
    percentage: int  # 0-100
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            'task_id': self.task_id,
            'stage': self.stage,
            'message': self.message,
            'percentage': self.percentage,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


# Default stage configurations for different agent types
AGENT_STAGES = {
    'image_generation': [
        ('analyzing', 'Analyzing your prompt...', 10),
        ('preparing', 'Preparing image generation...', 20),
        ('generating', 'Generating image...', 50),
        ('processing', 'Processing image...', 80),
        ('finalizing', 'Finalizing...', 95),
        ('complete', 'Image ready!', 100),
    ],
    'video_generation': [
        ('analyzing', 'Analyzing video request...', 5),
        ('preparing', 'Preparing assets...', 15),
        ('rendering', 'Rendering video frames...', 40),
        ('processing', 'Processing video...', 70),
        ('audio', 'Processing audio...', 85),
        ('finalizing', 'Finalizing video...', 95),
        ('complete', 'Video ready!', 100),
    ],
    'research': [
        ('analyzing', 'Understanding your query...', 10),
        ('searching', 'Searching sources...', 30),
        ('gathering', 'Gathering information...', 50),
        ('analyzing', 'Analyzing results...', 70),
        ('formatting', 'Formatting response...', 90),
        ('complete', 'Research complete!', 100),
    ],
    'audio_generation': [
        ('analyzing', 'Analyzing text...', 15),
        ('generating', 'Generating audio...', 50),
        ('processing', 'Processing audio...', 80),
        ('complete', 'Audio ready!', 100),
    ],
    'competitor_analysis': [
        ('gathering', 'Gathering market data...', 20),
        ('analyzing', 'Analyzing competitors...', 50),
        ('synthesizing', 'Synthesizing insights...', 75),
        ('formatting', 'Creating report...', 90),
        ('complete', 'Analysis complete!', 100),
    ],
    'brand_strategy': [
        ('research', 'Researching brand landscape...', 20),
        ('analyzing', 'Analyzing brand positioning...', 40),
        ('developing', 'Developing strategy...', 60),
        ('creating', 'Creating recommendations...', 80),
        ('complete', 'Strategy ready!', 100),
    ],
    'workflow': [
        ('initializing', 'Initializing workflow...', 5),
        ('step_1', 'Executing step 1...', 25),
        ('step_2', 'Executing step 2...', 50),
        ('step_3', 'Executing step 3...', 75),
        ('finalizing', 'Completing workflow...', 95),
        ('complete', 'Workflow complete!', 100),
    ],
    'default': [
        ('starting', 'Starting...', 10),
        ('processing', 'Processing...', 50),
        ('complete', 'Complete!', 100),
    ],
}


class StreamingProgressService:
    """
    Service to manage streaming progress updates.

    Features:
    - Register tasks for progress tracking
    - Emit progress updates (WebSocket/SSE ready)
    - Subscribe to progress events
    - Automatic stage progression
    - Session 489: WebSocket channel layer broadcasting
    """

    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.subscribers: Dict[str, List[Callable]] = {}
        self._update_queue: Queue = Queue()
        self._lock = threading.Lock()
        self._channel_layer = None  # Session 489: Lazy-loaded channel layer
        self._websocket_enabled = True  # Session 489: Can disable if needed

    @property
    def channel_layer(self):
        """Session 489: Lazy-load Django Channels layer for WebSocket broadcasting."""
        if self._channel_layer is None:
            try:
                from channels.layers import get_channel_layer
                self._channel_layer = get_channel_layer()
            except ImportError:
                logger.warning("Django Channels not available - WebSocket broadcasting disabled")
                self._websocket_enabled = False
        return self._channel_layer

    def _broadcast_to_websocket(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Session 489: Broadcast progress update to WebSocket clients.

        Sends to the 'agents_general' group that AgentProgressConsumer joins.

        Args:
            event_type: Type of event (agent_progress, agent_completed, agent_failed)
            data: Event data to broadcast
        """
        if not self._websocket_enabled or not self.channel_layer:
            return

        try:
            import asyncio
            from asgiref.sync import async_to_sync

            # Broadcast to the agents_general group
            async_to_sync(self.channel_layer.group_send)(
                'agents_general',
                {
                    'type': event_type.replace('_', '.'),  # agent_progress -> agent.progress
                    'data': data
                }
            )
            logger.debug(f"📡 Broadcast {event_type} to WebSocket: {data.get('task_id', 'unknown')}")
        except Exception as e:
            logger.warning(f"WebSocket broadcast failed: {e}")

    def register_task(
        self,
        task_id: str,
        agent_type: str,
        description: str = '',
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register a new task for progress tracking.

        Args:
            task_id: Unique task identifier
            agent_type: Type of agent (image_generation, research, etc.)
            description: Human-readable description
            metadata: Additional task metadata

        Returns:
            Task tracking info
        """
        stages = AGENT_STAGES.get(agent_type, AGENT_STAGES['default'])

        task_info = {
            'task_id': task_id,
            'agent_type': agent_type,
            'description': description,
            'stages': stages,
            'current_stage_index': 0,
            'status': 'registered',
            'percentage': 0,
            'created_at': datetime.now(),
            'updates': [],
            'metadata': metadata or {}
        }

        with self._lock:
            self.tasks[task_id] = task_info

        logger.info(f"📊 Registered task '{task_id}' for progress tracking ({agent_type})")
        return task_info

    def emit_progress(
        self,
        task_id: str,
        stage: str,
        message: str,
        percentage: int,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ProgressUpdate]:
        """
        Emit a progress update for a task.

        Args:
            task_id: Task to update
            stage: Current stage name
            message: Human-readable progress message
            percentage: Progress percentage (0-100)
            metadata: Additional update metadata

        Returns:
            The ProgressUpdate or None if task not found
        """
        with self._lock:
            if task_id not in self.tasks:
                logger.warning(f"⚠️ Task '{task_id}' not found for progress update")
                return None

            update = ProgressUpdate(
                task_id=task_id,
                stage=stage,
                message=message,
                percentage=min(100, max(0, percentage)),
                metadata=metadata or {}
            )

            # Update task state
            self.tasks[task_id]['status'] = stage
            self.tasks[task_id]['percentage'] = update.percentage
            self.tasks[task_id]['updates'].append(update.to_dict())
            self.tasks[task_id]['last_update'] = datetime.now()

        # Notify subscribers
        self._notify_subscribers(task_id, update)

        # Session 489: Broadcast to WebSocket clients
        self._broadcast_to_websocket('agent_progress', update.to_dict())

        logger.debug(f"📊 Progress: {task_id} - {stage} ({percentage}%): {message}")

        return update

    def advance_stage(self, task_id: str) -> Optional[ProgressUpdate]:
        """
        Advance to the next stage for a task.

        Args:
            task_id: Task to advance

        Returns:
            The new ProgressUpdate or None if complete/not found
        """
        with self._lock:
            if task_id not in self.tasks:
                return None

            task = self.tasks[task_id]
            stages = task['stages']
            current_index = task['current_stage_index']

            if current_index >= len(stages) - 1:
                # Already at last stage
                return None

            # Move to next stage
            next_index = current_index + 1
            task['current_stage_index'] = next_index

            stage_name, message, percentage = stages[next_index]

        return self.emit_progress(task_id, stage_name, message, percentage)

    def complete_task(
        self,
        task_id: str,
        message: str = 'Complete!',
        result: Optional[Any] = None
    ) -> Optional[ProgressUpdate]:
        """
        Mark a task as complete.

        Args:
            task_id: Task to complete
            message: Completion message
            result: Task result to store

        Returns:
            The final ProgressUpdate
        """
        with self._lock:
            if task_id not in self.tasks:
                return None

            self.tasks[task_id]['result'] = result
            self.tasks[task_id]['completed_at'] = datetime.now()

        update = self.emit_progress(
            task_id,
            'complete',
            message,
            100,
            metadata={'result': str(result)[:200] if result else None}
        )

        # Session 489: Broadcast completion to WebSocket
        if update:
            self._broadcast_to_websocket('agent_completed', {
                'task_id': task_id,
                'message': message,
                'result': str(result)[:200] if result else None,
                'timestamp': datetime.now().isoformat()
            })

        return update

    def fail_task(
        self,
        task_id: str,
        error: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Optional[ProgressUpdate]:
        """
        Mark a task as failed.

        Args:
            task_id: Task that failed
            error: Error message
            details: Additional error details

        Returns:
            The error ProgressUpdate
        """
        with self._lock:
            if task_id not in self.tasks:
                return None

            self.tasks[task_id]['error'] = error
            self.tasks[task_id]['failed_at'] = datetime.now()

        update = self.emit_progress(
            task_id,
            'error',
            f"Error: {error}",
            self.tasks.get(task_id, {}).get('percentage', 0),
            metadata={'error': error, 'details': details}
        )

        # Session 489: Broadcast failure to WebSocket
        if update:
            self._broadcast_to_websocket('agent_failed', {
                'task_id': task_id,
                'error': error,
                'details': details,
                'timestamp': datetime.now().isoformat()
            })

        return update

    def get_progress(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get current progress for a task."""
        with self._lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                return {
                    'task_id': task_id,
                    'status': task['status'],
                    'percentage': task['percentage'],
                    'description': task['description'],
                    'agent_type': task['agent_type'],
                    'created_at': task['created_at'].isoformat(),
                    'last_update': task.get('last_update', task['created_at']).isoformat(),
                    'updates_count': len(task['updates']),
                    'latest_message': task['updates'][-1]['message'] if task['updates'] else None
                }
        return None

    def get_task_updates(self, task_id: str, since_index: int = 0) -> List[Dict[str, Any]]:
        """Get updates for a task since a specific index (for polling)."""
        with self._lock:
            if task_id in self.tasks:
                return self.tasks[task_id]['updates'][since_index:]
        return []

    def subscribe(self, task_id: str, callback: Callable[[ProgressUpdate], None]) -> None:
        """Subscribe to progress updates for a task."""
        with self._lock:
            if task_id not in self.subscribers:
                self.subscribers[task_id] = []
            self.subscribers[task_id].append(callback)
        logger.debug(f"📊 Subscribed to task '{task_id}' progress")

    def unsubscribe(self, task_id: str, callback: Callable) -> None:
        """Unsubscribe from task updates."""
        with self._lock:
            if task_id in self.subscribers:
                self.subscribers[task_id] = [
                    cb for cb in self.subscribers[task_id] if cb != callback
                ]

    def _notify_subscribers(self, task_id: str, update: ProgressUpdate) -> None:
        """Notify all subscribers of an update."""
        with self._lock:
            callbacks = self.subscribers.get(task_id, [])[:]

        for callback in callbacks:
            try:
                callback(update)
            except Exception as e:
                logger.error(f"Error in progress subscriber callback: {e}")

    def cleanup_completed(self, max_age_minutes: int = 60) -> int:
        """Clean up old completed/failed tasks."""
        from datetime import timedelta
        cutoff = datetime.now() - timedelta(minutes=max_age_minutes)
        removed = 0

        with self._lock:
            for task_id in list(self.tasks.keys()):
                task = self.tasks[task_id]
                completed_at = task.get('completed_at') or task.get('failed_at')
                if completed_at and completed_at < cutoff:
                    del self.tasks[task_id]
                    if task_id in self.subscribers:
                        del self.subscribers[task_id]
                    removed += 1

        if removed:
            logger.info(f"🧹 Cleaned up {removed} old progress tasks")

        return removed


class ProgressTracker:
    """
    Context manager for easy progress tracking.

    Usage:
        with ProgressTracker(task_id, 'image_generation') as tracker:
            tracker.advance()  # Move to next stage
            # ... do work ...
            tracker.advance()
            # ... more work ...
    """

    def __init__(
        self,
        task_id: str,
        agent_type: str,
        description: str = '',
        service: Optional[StreamingProgressService] = None
    ):
        self.task_id = task_id
        self.agent_type = agent_type
        self.description = description
        self.service = service or get_streaming_progress_service()

    def __enter__(self):
        self.service.register_task(
            self.task_id,
            self.agent_type,
            self.description
        )
        # Start with first stage
        stages = AGENT_STAGES.get(self.agent_type, AGENT_STAGES['default'])
        if stages:
            stage_name, message, percentage = stages[0]
            self.service.emit_progress(self.task_id, stage_name, message, percentage)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.service.fail_task(self.task_id, str(exc_val))
        else:
            self.service.complete_task(self.task_id)
        return False

    def advance(self, custom_message: Optional[str] = None) -> None:
        """Advance to the next stage."""
        update = self.service.advance_stage(self.task_id)
        if update and custom_message:
            self.service.emit_progress(
                self.task_id,
                update.stage,
                custom_message,
                update.percentage
            )

    def update(self, message: str, percentage: int) -> None:
        """Send a custom progress update."""
        self.service.emit_progress(
            self.task_id,
            'processing',
            message,
            percentage
        )


# Singleton instance
_service: Optional[StreamingProgressService] = None


def get_streaming_progress_service() -> StreamingProgressService:
    """Get or create the streaming progress service singleton."""
    global _service
    if _service is None:
        _service = StreamingProgressService()
    return _service


def create_progress_tracker(
    task_id: str,
    agent_type: str,
    description: str = ''
) -> ProgressTracker:
    """Create a new progress tracker for a task."""
    return ProgressTracker(task_id, agent_type, description)


def get_progress_type_for_agent(agent_name: str) -> str:
    """
    Session 489: Get the progress stage type for an agent.

    Maps agent names to appropriate progress stage configurations.

    Args:
        agent_name: Name of the agent (e.g., 'ImageAgent')

    Returns:
        Progress type key for AGENT_STAGES
    """
    return AGENT_TO_PROGRESS_TYPE.get(agent_name, 'default')
