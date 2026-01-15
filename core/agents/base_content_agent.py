"""
Base Agent Class for Content Generation Agents
===============================================

Session 728: Migrated from agents/base_agent.py to core/agents/base_content_agent.py

Provides a standardized base class for content generation agents with:
- Consistent initialization and configuration
- Logging and error handling
- Agent contribution tracking
- User and project context management
- Common utility methods
- Learning infrastructure hooks (Session 305)

Session 186: Created as part of Phase 3 Architecture Improvements (Task 3.7)
Session 305: Added learning hooks for cross-agent knowledge sharing

Usage:
    class MyAgent(BaseContentAgent):
        agent_name = "MyAgent"
        specialization = "image_generation"

        def execute(self, **kwargs):
            # Your implementation
            pass
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field

from django.test import RequestFactory

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Standard result structure for agent execution."""
    success: bool
    message: str = ""
    error: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    # Asset tracking
    asset_ids: List[str] = field(default_factory=list)
    asset_type: str = ""  # 'image', 'video', 'audio', '3d_model'
    # Execution metadata
    execution_time_ms: int = 0
    agent_name: str = ""
    operation: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'message': self.message,
            'error': self.error,
            'data': self.data,
            'asset_ids': self.asset_ids,
            'asset_type': self.asset_type,
            'agent': self.agent_name,
            'operation': self.operation,
        }


class BaseContentAgent(ABC):
    """
    Abstract base class for content generation agents.

    Provides:
    - User and project context management
    - Request factory for internal API calls
    - Logging configuration
    - Error handling utilities
    - Agent contribution tracking

    Subclasses must implement:
    - execute(): Main execution method

    Subclasses may override:
    - agent_name: Name for logging and attribution (default: class name)
    - specialization: Agent specialization category
    """

    # Class-level configuration (override in subclasses)
    agent_name: str = "BaseAgent"
    specialization: str = "general"

    def __init__(
        self,
        user,  # Django User object
        project_id: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
        """
        Initialize the agent.

        Args:
            user: Django User object for the request
            project_id: Optional UUID string for project association
            session_id: Optional UUID string for session association
        """
        self.user = user
        self.project_id = project_id
        self.session_id = session_id

        # Set agent name from class if not overridden
        if self.agent_name == "BaseAgent":
            self.agent_name = self.__class__.__name__

        # Request factory for internal API calls
        self._request_factory = RequestFactory()

        # Logging
        self.logger = logging.getLogger(f"agents.{self.agent_name}")
        self.logger.info(
            f"{self.agent_name} initialized for user={user.username}, "
            f"project={project_id or 'None'}"
        )

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the agent's primary operation.

        Args:
            **kwargs: Operation-specific parameters

        Returns:
            Dictionary with at least 'success' and 'message' or 'error' keys
        """

    # =========================================================================
    # Internal API Call Utilities
    # =========================================================================

    def _make_internal_request(
        self,
        method: str,
        path: str,
        data: Dict[str, Any] = None,
        content_type: str = 'application/json'
    ):
        """
        Make an internal API request using RequestFactory.

        Args:
            method: HTTP method (GET, POST, etc.)
            path: URL path for the request
            data: Request data
            content_type: Request content type

        Returns:
            Request object with user authentication
        """
        factory_method = getattr(self._request_factory, method.lower())

        if method.upper() in ('GET', 'DELETE'):
            request = factory_method(path)
        else:
            request = factory_method(
                path,
                data=data,
                content_type=content_type
            )

        request.user = self.user
        return request

    # =========================================================================
    # Result Builders
    # =========================================================================

    def _success_result(
        self,
        message: str,
        data: Dict[str, Any] = None,
        asset_ids: List[str] = None,
        asset_type: str = "",
        operation: str = ""
    ) -> Dict[str, Any]:
        """
        Build a successful result dictionary.

        Args:
            message: Success message
            data: Additional result data
            asset_ids: List of created asset UUIDs
            asset_type: Type of assets created
            operation: Name of operation performed

        Returns:
            Standardized success result dictionary
        """
        result = {
            'success': True,
            'message': message,
            'agent': self.agent_name,
            'operation': operation,
        }

        if data:
            result.update(data)

        if asset_ids:
            result['asset_ids'] = asset_ids
            result['asset_type'] = asset_type

            # Use appropriate key based on asset type
            if asset_type == 'image':
                result['image_ids'] = asset_ids
            elif asset_type == 'video':
                result['video_ids'] = asset_ids
            elif asset_type == 'audio':
                result['audio_ids'] = asset_ids
            elif asset_type == '3d_model':
                result['model_ids'] = asset_ids

        return result

    def _error_result(
        self,
        error: str,
        details: str = None,
        operation: str = ""
    ) -> Dict[str, Any]:
        """
        Build an error result dictionary.

        Args:
            error: Error message
            details: Additional error details
            operation: Name of operation that failed

        Returns:
            Standardized error result dictionary
        """
        result = {
            'success': False,
            'error': error,
            'agent': self.agent_name,
            'operation': operation,
        }

        if details:
            result['details'] = details

        return result

    # =========================================================================
    # Agent Contribution Tracking
    # =========================================================================

    def _track_contribution(
        self,
        operation: str,
        asset_ids: List[str],
        asset_type: str,
        success: bool = True,
        metadata: Dict[str, Any] = None
    ):
        """
        Track agent contribution for analytics.

        Session 754: Fixed to use correct model and fields.
        - Uses AgentContribution from core.models.agents_registry
        - Looks up UnifiedAgentTemplate by agent name
        - Links to actual content objects

        Args:
            operation: Operation performed (maps to contribution_type)
            asset_ids: List of affected asset IDs
            asset_type: Type of assets (image, video, etc.)
            success: Whether operation succeeded
            metadata: Additional metadata
        """
        try:
            from core.models.agents_registry import AgentContribution, UnifiedAgentTemplate
            from content.models import ImageHistory, VideoHistory

            # Get or create the UnifiedAgentTemplate for this agent
            agent_template, _ = UnifiedAgentTemplate.objects.get_or_create(
                name=self.agent_name,
                defaults={
                    'display_name': self.agent_name.replace('Agent', ' Agent'),
                    'description': f'{self.agent_name} content agent',
                    'specialization': 'content',
                    'system_prompt': '',
                }
            )

            # Map operation to contribution_type choices
            operation_mapping = {
                'generate': 'generation',
                'create': 'generation',
                'edit': 'editing',
                'enhance': 'editing',
                'orchestrate': 'orchestration',
                'analyze': 'analysis',
                'recommend': 'recommendation',
                'iterate': 'iteration',
            }
            contribution_type = operation_mapping.get(operation.lower(), 'generation')

            # Get project if we have project_id
            project = self._get_project() if self.project_id else None

            # Create contributions for each asset
            created_count = 0
            for asset_id in asset_ids:
                try:
                    contribution_kwargs = {
                        'agent': agent_template,
                        'contribution_type': contribution_type,
                        'contribution_role': 'Primary Creator' if success else 'Attempted',
                        'contribution_percentage': 100 if success else 0,
                        'task_description': f'{operation} {asset_type}',
                    }

                    if project:
                        contribution_kwargs['project'] = project

                    # Link to specific content type
                    if asset_type == 'image':
                        try:
                            image = ImageHistory.objects.get(id=asset_id)
                            contribution_kwargs['image'] = image
                        except (ImageHistory.DoesNotExist, ValueError):
                            pass
                    elif asset_type == 'video':
                        try:
                            video = VideoHistory.objects.get(id=asset_id)
                            contribution_kwargs['video'] = video
                        except (VideoHistory.DoesNotExist, ValueError):
                            pass

                    AgentContribution.objects.create(**contribution_kwargs)
                    created_count += 1

                except Exception as asset_error:
                    self.logger.debug(f"Could not track contribution for {asset_type} {asset_id}: {asset_error}")

            if created_count > 0:
                self.logger.info(f"✓ Tracked {created_count} contribution(s): {operation} on {asset_type}s")

        except ImportError:
            self.logger.debug("AgentContribution model not available, skipping tracking")
        except Exception as e:
            self.logger.warning(f"Failed to track contribution: {e}")

    # =========================================================================
    # Project and Session Context
    # =========================================================================

    def _get_project(self):
        """Get the associated project object if project_id is set."""
        if not self.project_id:
            return None

        try:
            from content.models import CreativeProject
            return CreativeProject.objects.get(id=self.project_id)
        except Exception as e:
            self.logger.warning(f"Could not get project {self.project_id}: {e}")
            return None

    def _get_session(self):
        """Get the associated AI session object if session_id is set."""
        if not self.session_id:
            return None

        try:
            from content.models import AISession
            return AISession.objects.get(id=self.session_id)
        except Exception as e:
            self.logger.warning(f"Could not get session {self.session_id}: {e}")
            return None

    # =========================================================================
    # Validation Utilities
    # =========================================================================

    def _validate_required_params(
        self,
        params: Dict[str, Any],
        required: List[str]
    ) -> Optional[str]:
        """
        Validate that required parameters are present.

        Args:
            params: Parameters dictionary
            required: List of required parameter names

        Returns:
            Error message if validation fails, None if valid
        """
        missing = [p for p in required if p not in params or params[p] is None]
        if missing:
            return f"Missing required parameters: {', '.join(missing)}"
        return None

    def _validate_uuid(self, value: str, field_name: str = "id") -> Optional[str]:
        """
        Validate that a value is a valid UUID.

        Args:
            value: Value to validate
            field_name: Field name for error message

        Returns:
            Error message if invalid, None if valid
        """
        import uuid as uuid_module
        try:
            uuid_module.UUID(str(value))
            return None
        except ValueError:
            return f"Invalid UUID for {field_name}: {value}"

    # =========================================================================
    # Logging Utilities
    # =========================================================================

    def log_start(self, operation: str, **kwargs):
        """Log the start of an operation."""
        self.logger.info(f"{self.agent_name} starting {operation}")
        for key, value in kwargs.items():
            if isinstance(value, str) and len(value) > 100:
                self.logger.info(f"  {key}: {value[:100]}...")
            else:
                self.logger.info(f"  {key}: {value}")

    def log_complete(self, operation: str, success: bool = True):
        """Log the completion of an operation."""
        status = "completed" if success else "failed"
        self.logger.info(f"{self.agent_name} {operation} {status}")

    def log_error(self, operation: str, error: Exception):
        """Log an error during operation."""
        self.logger.error(f"{self.agent_name} {operation} error: {error}", exc_info=True)

    # =========================================================================
    # Session 305: Learning Infrastructure Hooks
    # =========================================================================
    # These methods mirror the learning hooks in core/agents/base_agent.py
    # to enable cross-agent knowledge sharing for legacy agents.

    # Lazy-loaded service instances
    _learning_loop = None
    _memory_service = None
    _agent_model = None

    @property
    def learning_loop(self):
        """Lazy-load LearningLoopService."""
        if self._learning_loop is None:
            try:
                from core.super_platform.learning_loop import get_learning_loop_service
                self._learning_loop = get_learning_loop_service(self.user)
            except ImportError:
                self.logger.debug("LearningLoopService not available")
                return None
        return self._learning_loop

    @property
    def memory_service(self):
        """Lazy-load MemoryEmbeddingService."""
        if self._memory_service is None:
            try:
                from core.services.memory_embedding_service import get_memory_embedding_service
                self._memory_service = get_memory_embedding_service()
            except ImportError:
                self.logger.debug("MemoryEmbeddingService not available")
                return None
        return self._memory_service

    @property
    def agent_model(self):
        """Lazy-load or create Agent model instance."""
        if self._agent_model is None:
            try:
                from core.models_unified_system import Agent
                self._agent_model, _ = Agent.objects.get_or_create(
                    name=self.agent_name,
                    defaults={
                        'agent_type': 'legacy_content',
                        'specialization': self.specialization,
                        'description': f'Legacy content agent: {self.agent_name}',
                        'is_active': True,
                    }
                )
            except ImportError:
                self.logger.debug("Agent model not available")
                return None
        return self._agent_model

    def _record_learning_outcome(
        self,
        result: Dict[str, Any],
        task: str,
        context: Dict[str, Any] = None,
        spider_data_used: bool = False,
        scifi_context_used: bool = False
    ):
        """
        Record execution outcome for XP and pattern learning.
        Session 305: Learning infrastructure hook for legacy agents.
        """
        if not self.learning_loop:
            return None

        try:
            outcome_id = self.learning_loop.record_outcome(
                query_type=self._detect_query_type(task),
                query_text=task,
                execution_mode='agent',
                agents_used=[self.agent_name],
                response=result.get('message', str(result.get('data', ''))),
                execution_time_ms=result.get('execution_time_ms', 0),
                success=result.get('success', False),
                spider_data_used=spider_data_used,
                scifi_context_used=scifi_context_used,
                context=context or {}
            )
            return outcome_id
        except Exception as e:
            self.logger.debug(f"Failed to record learning outcome: {e}")
            return None

    def _detect_query_type(self, task: str) -> str:
        """Detect the type of query from the task text."""
        task_lower = task.lower()
        if any(word in task_lower for word in ['research', 'search', 'find', 'look up']):
            return 'research'
        elif any(word in task_lower for word in ['create', 'generate', 'make', 'design']):
            return 'create'
        elif any(word in task_lower for word in ['edit', 'modify', 'change', 'update']):
            return 'edit'
        elif any(word in task_lower for word in ['workflow', 'process', 'pipeline']):
            return 'workflow'
        return 'general'

    def _create_execution_memory(
        self,
        result: Dict[str, Any],
        task: str,
        memory_type: str = "interaction",
        importance: float = 0.5
    ):
        """
        Create a memory from the interaction.
        Session 305: Learning infrastructure hook for legacy agents.
        """
        if not self.memory_service or not self.agent_model:
            return None

        try:
            memory = self.memory_service.create_memory(
                agent=self.agent_model,
                title=f"{self.agent_name}: {task[:50]}...",
                content=result.get('message', str(result.get('data', ''))),
                memory_type=memory_type,
                valence="positive" if result.get('success') else "negative",
                importance_score=importance,
                metadata={
                    'task': task,
                    'success': result.get('success', False),
                    'specialization': self.specialization,
                    'project_id': self.project_id,
                    'session_id': self.session_id,
                }
            )
            return memory
        except Exception as e:
            self.logger.debug(f"Failed to create execution memory: {e}")
            return None

    def _share_knowledge(
        self,
        knowledge_type: str,
        title: str,
        knowledge_value: Dict[str, Any],
        confidence: float = 0.8
    ):
        """
        Share learned knowledge for cross-agent learning.
        Session 305: Learning infrastructure hook for legacy agents.
        """
        if not self.agent_model:
            return None

        try:
            import json
            from core.models_unified_system import AgentKnowledgeSource

            # Map generic types to model's choices
            type_mapping = {
                'technique': 'tool_discovery',
                'insight': 'market',
                'pattern': 'user_behavior',
                'preference': 'user_behavior',
                'workflow': 'tool_discovery',
            }
            mapped_type = type_mapping.get(knowledge_type, knowledge_type)

            valid_types = ['trend', 'market', 'opportunity', 'competitor',
                          'pricing', 'user_behavior', 'content_idea', 'tool_discovery']
            if mapped_type not in valid_types:
                mapped_type = 'tool_discovery'

            knowledge, created = AgentKnowledgeSource.objects.update_or_create(
                agent=self.agent_model,
                title=title,
                knowledge_type=mapped_type,
                defaults={
                    'summary': json.dumps(knowledge_value),
                    'confidence_score': confidence,
                    'is_active': True,
                }
            )
            return knowledge
        except Exception as e:
            self.logger.debug(f"Failed to share knowledge: {e}")
            return None

    def _get_shared_knowledge(
        self,
        knowledge_type: str = None,
        title_contains: str = None,
        from_agents: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve knowledge from other agents.
        Session 305: Learning infrastructure hook for legacy agents.
        """
        try:
            import json
            from core.models_unified_system import AgentKnowledgeSource

            queryset = AgentKnowledgeSource.objects.filter(is_active=True)

            if knowledge_type:
                type_mapping = {
                    'technique': 'tool_discovery',
                    'insight': 'market',
                    'pattern': 'user_behavior',
                    'preference': 'user_behavior',
                }
                mapped_type = type_mapping.get(knowledge_type, knowledge_type)
                queryset = queryset.filter(knowledge_type=mapped_type)

            if title_contains:
                queryset = queryset.filter(title__icontains=title_contains)

            if from_agents:
                queryset = queryset.filter(agent__name__in=from_agents)

            # Exclude own knowledge to learn from others
            if self.agent_model:
                queryset = queryset.exclude(agent=self.agent_model)

            return [
                {
                    'source_agent': ks.agent.name,
                    'title': ks.title,
                    'type': ks.knowledge_type,
                    'value': json.loads(ks.summary) if ks.summary else {},
                    'confidence': ks.confidence_score,
                    'created': ks.created_at.isoformat() if ks.created_at else None,
                }
                for ks in queryset.order_by('-confidence_score')[:10]
            ]
        except Exception as e:
            self.logger.debug(f"Failed to get shared knowledge: {e}")
            return []
