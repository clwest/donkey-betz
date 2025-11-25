"""
Base Agent Class for Content Generation Agents
===============================================

Provides a standardized base class for content generation agents with:
- Consistent initialization and configuration
- Logging and error handling
- Agent contribution tracking
- User and project context management
- Common utility methods

Session 186: Created as part of Phase 3 Architecture Improvements (Task 3.7)

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
from datetime import datetime

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
        pass

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

        Args:
            operation: Operation performed
            asset_ids: List of affected asset IDs
            asset_type: Type of assets
            success: Whether operation succeeded
            metadata: Additional metadata
        """
        try:
            from agents.models import AgentContribution

            AgentContribution.objects.create(
                agent_name=self.agent_name,
                operation=operation,
                user_id=self.user.id if self.user else None,
                project_id=self.project_id,
                session_id=self.session_id,
                asset_type=asset_type,
                asset_ids=asset_ids,
                success=success,
                metadata=metadata or {},
            )
            self.logger.debug(f"Tracked contribution: {operation} on {len(asset_ids)} {asset_type}s")

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
