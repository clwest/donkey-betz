"""
Enhanced Personal AI Assistant - Base Module (DEPRECATED)
=========================================================

DEPRECATED: This module is no longer actively used. All PA traffic routes
through Rigby via UnifiedPAEntrypoint. Kept for backward compatibility
with any remaining internal references.

Core assistant class with modular tool execution capabilities.
This serves as the central coordinator for all AI assistant functionality.

Session 184: Refactored from personal_ai_assistant_enhanced.py (6,905 lines)

Architecture:
- base.py: Core class, initialization, main interface
- tool_definitions.py: GPT-5.1 tool schemas
- image_tools.py: Image operation handlers (mixin)
- video_tools.py: Video operation handlers (mixin) - placeholder
- audio_tools.py: Audio operation handlers (mixin) - placeholder
- utils.py: ID resolution, range parsing utilities
- constants.py: Configuration values
"""

import json
import logging
from typing import Dict, Any, List

from django.contrib.auth import get_user_model

from core.models import EnhancedUserProfile
from core.personal_ai_assistant import PersonalAIAssistant
from core.llm_enforcer import LLMEnforcer
from core.unified_memory_manager import get_memory_manager

from core.assistant.tool_definitions import get_tool_definitions
from core.assistant.utils import (
    resolve_hybrid_image_id,
    resolve_hybrid_video_id,
    parse_id_range,
    is_batch_operation,
    format_batch_result,
)
from core.assistant.image_tools import ImageToolsMixin
from core.assistant.audio_tools import AudioToolsMixin
from core.assistant.video_tools import VideoGenerationToolsMixin, VideoEditingToolsMixin

# Try to import optional dependencies
try:
    from core.agents.registry import get_agent_registry
    from advisors.registry import get_advisor_registry
except ImportError:
    get_agent_registry = None
    get_advisor_registry = None

try:
    from self_awareness.embeddings import CodebaseEmbeddings
except ImportError:
    class CodebaseEmbeddings:
        def __init__(self):
            pass

try:
    from ml.core.ml_engine import MLEngine
except ImportError:
    MLEngine = None

logger = logging.getLogger(__name__)
User = get_user_model()


class EnhancedPersonalAIAssistant(
    ImageToolsMixin,
    AudioToolsMixin,
    VideoGenerationToolsMixin,
    VideoEditingToolsMixin,
    PersonalAIAssistant
):
    """
    Enhanced Personal AI Assistant with database access and system capabilities.

    This class provides:
    - Tool execution for image, video, audio, and 3D operations
    - Multi-agent orchestration
    - Memory management and context handling
    - Conversation processing with GPT-5.1

    The class uses mixins for tool handlers:
    - ImageToolsMixin: Image editing tool handlers

    Key methods:
    - process_message(): Main entry point for user messages
    - get_tool_definitions(): Returns available GPT tools
    - execute_tool(): Executes a specific tool

    Session 184: Decomposed from monolithic 6,905 line file
    """

    def __init__(self, user: User):
        """
        Initialize the Enhanced Personal AI Assistant.

        Args:
            user: Django User object for the current session
        """
        super().__init__(user)
        self.system_access_enabled = True
        self.database_queries_executed = []
        self._ensure_enhanced_profile()
        self.llm_enforcer = LLMEnforcer()
        self.memory_manager = get_memory_manager(user)

        # Initialize registries for agent/advisor communication
        if get_agent_registry:
            self.agent_registry = get_agent_registry()
        else:
            self.agent_registry = None

        if get_advisor_registry:
            self.advisor_registry = get_advisor_registry()
        else:
            self.advisor_registry = None

        # Asset tracking for intelligent chaining
        self.recently_generated_assets = {
            'images': [],
            'videos': [],
            'last_updated': None
        }

        # Current context for tool execution
        self._current_context = {}
        self._last_tool_result = None

        logger.info(f"Enhanced AI Assistant initialized for {user.username}")

    def get_tool_definitions(self) -> List[Dict]:
        """
        Get agent-based tool definitions for GPT-5.1 Responses API.

        Returns:
            List of tool definition dictionaries
        """
        return get_tool_definitions()

    def _resolve_hybrid_image_id(self, image_id: str) -> str:
        """Convert sequential image numbers to UUIDs."""
        return resolve_hybrid_image_id(image_id, self.user)

    def _resolve_hybrid_video_id(self, video_id: str) -> str:
        """Convert sequential video numbers to UUIDs."""
        return resolve_hybrid_video_id(video_id, self.user)

    def _parse_id_range(self, id_str: str) -> List[str]:
        """Parse ID ranges into list of individual IDs."""
        return parse_id_range(id_str)

    def _is_batch_operation(self, id_str: str) -> bool:
        """Check if an ID string represents a batch operation."""
        return is_batch_operation(id_str)

    def _ensure_enhanced_profile(self):
        """Ensure user has an enhanced profile."""
        try:
            EnhancedUserProfile.objects.get_or_create(user=self.user)
        except Exception as e:
            logger.warning(f"Could not create enhanced profile: {e}")

    # =========================================================================
    # Tool Execution Methods
    # =========================================================================

    def _execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call from GPT.

        Args:
            tool_call: Tool call dictionary from GPT response

        Returns:
            Dictionary with execution results
        """
        try:
            function_name = tool_call['function']['name']
            arguments = json.loads(tool_call['function']['arguments'])

            # Auto-inject project_id from context if available
            if self._current_context and 'project_id' in self._current_context:
                if 'project_id' not in arguments:
                    arguments['project_id'] = self._current_context['project_id']
                    logger.info(f"Auto-injected project_id: {arguments['project_id']}")

            logger.info(f"Executing tool: {function_name}")

            # Route to appropriate handler
            result = self._route_tool_call(function_name, arguments)

            # Store result for video polling etc.
            self._last_tool_result = result

            return result

        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {
                'success': False,
                'error': f"Tool execution failed: {str(e)}"
            }

    def _route_tool_call(self, function_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route a tool call to the appropriate handler.

        Args:
            function_name: Name of the tool/agent to invoke
            arguments: Tool arguments

        Returns:
            Execution result dictionary
        """
        # Map function names to handler methods
        handlers = {
            'image_generation_agent': self._handle_image_generation_agent,
            'image_editing_agent': self._handle_image_editing_agent,
            'video_generation_agent': self._handle_video_generation_agent,
            'audio_generation_agent': self._handle_audio_generation_agent,
            'three_d_generation_agent': self._handle_three_d_generation_agent,
            'video_editing_agent': self._handle_video_editing_agent,
            'character_training_agent': self._handle_character_training_agent,
            'coleadership_agent': self._handle_coleadership_agent,
            'talking_character_agent': self._tool_talking_character,
            'web_search': self._handle_web_search,
            'create_brand_video': self._handle_create_brand_video,
        }

        handler = handlers.get(function_name)
        if handler:
            return handler(arguments)
        else:
            return {
                'success': False,
                'error': f"Unknown agent: {function_name}"
            }

    # =========================================================================
    # Agent Handler Stubs (Full implementations in original file)
    # These delegate to the specialized agents
    # =========================================================================

    def _handle_image_generation_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle image_generation_agent calls."""
        prompt = arguments.get('prompt')
        params = arguments.get('params', {})
        project_id = arguments.get('project_id')
        character_model_name = arguments.get('character_model_name')

        if character_model_name:
            return self._handle_trained_creation_agent(prompt, character_model_name, params, project_id)
        else:
            return self._handle_creation_agent(prompt, params, project_id)

    def _handle_creation_agent(self, prompt: str, params: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Handle standard image generation via CreationAgent."""
        logger.info(f"Creation Agent: prompt='{prompt[:50]}...'")

        width = params.get('width', 1024)
        height = params.get('height', 1024)
        count = params.get('count', 1)
        quality = params.get('quality', 'balanced')
        style = params.get('style', 'photorealistic')

        try:
            from core.agents.creation_agent import CreationAgent

            agent = CreationAgent(user=self.user, project_id=project_id)
            from core.services.priority.enforce import check_priority, log_decision  # Session 1086 PR 3c
            _pd = check_priority('CreationAgent', trigger_source='user_chat'); log_decision(_pd, 'CreationAgent')
            result = agent.execute(
                prompt=prompt,
                size=f"{width}x{height}",
                num_images=count,
                quality=quality,
                style=style
            )

            if result.get('success'):
                return {
                    'success': True,
                    'message': result.get('message'),
                    'image_ids': result.get('image_ids', [])
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Image generation failed')
                }

        except Exception as e:
            logger.error(f"Creation Agent error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to generate image: {str(e)}"
            }

    def _handle_trained_creation_agent(self, prompt: str, character_model_name: str,
                                       params: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Handle LoRA-based image generation via TrainedCreationAgent."""
        logger.info(f"Trained Creation Agent: model='{character_model_name}'")

        width = params.get('width', 1024)
        height = params.get('height', 1024)
        count = params.get('count', 1)
        lora_scale = params.get('lora_scale', 0.8)

        try:
            from core.agents.training import TrainedCreationAgent

            agent = TrainedCreationAgent(user=self.user, project_id=project_id)
            from core.services.priority.enforce import check_priority, log_decision  # Session 1086 PR 3c
            _pd = check_priority('TrainedCreationAgent', trigger_source='user_chat'); log_decision(_pd, 'TrainedCreationAgent')
            result = agent.execute(
                prompt=prompt,
                character_model_name=character_model_name,
                width=width,
                height=height,
                num_outputs=count,
                lora_scale=lora_scale
            )

            if result.get('success'):
                return {
                    'success': True,
                    'message': result.get('message'),
                    'image_ids': result.get('image_ids', [])
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Trained image generation failed')
                }

        except Exception as e:
            logger.error(f"Trained Creation Agent error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to generate image with trained model: {str(e)}"
            }

    def _handle_image_editing_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle image_editing_agent calls with batch support."""
        operation = arguments.get('operation')
        image_id = arguments.get('image_id')
        params = arguments.get('params', {})
        project_id = arguments.get('project_id')

        logger.info(f"Image Editing Agent: operation={operation}, image_id={image_id}")

        # Check for batch operation
        if self._is_batch_operation(image_id):
            return self._execute_batch_image_operation(operation, image_id, params, project_id)
        else:
            return self._execute_single_image_edit(operation, image_id, params, project_id)

    def _execute_batch_image_operation(self, operation: str, image_id: str,
                                       params: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Execute batch image operation."""
        try:
            image_ids = self._parse_id_range(image_id)
        except ValueError as e:
            return {'success': False, 'error': f"Invalid ID range: {str(e)}"}

        logger.info(f"Batch operation: {operation} on {len(image_ids)} images")

        results = []
        successes = []
        failures = []

        for idx, img_id in enumerate(image_ids, 1):
            try:
                resolved_id = self._resolve_hybrid_image_id(img_id)
                result = self._execute_single_image_edit(operation, resolved_id, params, project_id)

                if result.get('success'):
                    successes.append({'id': img_id, 'result': result})
                else:
                    failures.append({'id': img_id, 'error': result.get('error', 'Unknown error')})

                results.append(result)

            except Exception as e:
                error_msg = str(e)
                logger.error(f"Failed to process image {img_id}: {error_msg}")
                failures.append({'id': img_id, 'error': error_msg})
                results.append({'success': False, 'error': error_msg})

        return format_batch_result(
            operation=operation,
            successes=len(successes),
            total=len(image_ids),
            failures=len(failures),
            results=results,
            successful_ids=[s['id'] for s in successes],
            failed_ids=[f['id'] for f in failures],
            errors=[f['error'] for f in failures] if failures else []
        )

    def _execute_single_image_edit(self, operation: str, image_id: str,
                                   params: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Execute a single image editing operation."""
        try:
            resolved_id = self._resolve_hybrid_image_id(image_id)
        except ValueError as e:
            return {'success': False, 'error': str(e)}

        tool_args = {'image_id': resolved_id, 'project_id': project_id}
        tool_args.update(params)

        # Route to appropriate tool handler from ImageToolsMixin
        operation_map = {
            'upscale': self._tool_upscale_image,
            'remove_background': self._tool_remove_background,
            'create_variations': self._tool_create_variations,
            'recolor': self._tool_recolor_image,
            'search_and_replace': self._tool_search_and_replace,
            'creative_upscale': self._tool_creative_upscale,
        }

        handler = operation_map.get(operation)
        if handler:
            return handler(tool_args)
        else:
            return {'success': False, 'error': f"Unknown image operation: {operation}"}

    # =========================================================================
    # Handlers provided by Mixins:
    # - _handle_audio_generation_agent: AudioToolsMixin
    # - _handle_video_generation_agent: VideoGenerationToolsMixin
    # - _handle_video_editing_agent: VideoEditingToolsMixin
    # - _tool_talking_character: VideoGenerationToolsMixin
    # =========================================================================

    # Handlers that still need implementation (delegate to specialized agents)
    def _handle_three_d_generation_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle three_d_generation_agent calls - delegates to ThreeDGenerationAgent."""
        operation = arguments.get('operation')
        image_id = arguments.get('image_id')
        project_id = arguments.get('project_id')

        logger.info(f"3D Generation Agent: operation={operation}, image_id={image_id}")

        if operation == 'convert':
            try:
                from core.agents import ThreeDAgent as ThreeDGenerationAgent

                current_project = getattr(self, 'project', None)
                agent = ThreeDGenerationAgent(
                    user=self.user,
                    project_id=str(current_project.id) if current_project else project_id
                )

                from core.services.priority.enforce import check_priority, log_decision  # Session 1086 PR 3c
                _pd = check_priority('ThreeDGenerationAgent', trigger_source='user_chat'); log_decision(_pd, 'ThreeDGenerationAgent')
                result = agent.execute(
                    image_id=image_id,
                    style='toy',
                    scale='medium'
                )

                return result

            except Exception as e:
                logger.error(f"3D Generation Agent error: {e}", exc_info=True)
                return {'success': False, 'error': str(e)}
        else:
            return {'success': False, 'error': f"Unknown 3D operation: {operation}"}

    def _handle_character_training_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle character_training_agent calls - delegates to CharacterTrainingAgent."""
        operation = arguments.get('operation')
        params = arguments.get('params', {})
        project_id = arguments.get('project_id')

        logger.info(f"Character Training Agent: operation={operation}")

        try:
            from core.agents.training import CharacterTrainingAgent

            current_project = getattr(self, 'project', None)
            agent = CharacterTrainingAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else project_id
            )

            from core.services.priority.enforce import check_priority, log_decision  # Session 1086 PR 3c
            _pd = check_priority('CharacterTrainingAgent', trigger_source='user_chat'); log_decision(_pd, 'CharacterTrainingAgent')
            result = agent.execute(operation=operation, **params)
            return result

        except Exception as e:
            logger.error(f"Character Training Agent error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _handle_coleadership_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle coleadership_agent calls - delegates to CoLeadershipAgent."""
        operation = arguments.get('operation')
        params = arguments.get('params', {})

        logger.info(f"Co-Leadership Agent: operation={operation}")

        try:
            from coleadership.views import CoLeadershipAgent

            agent = CoLeadershipAgent(user=self.user)
            from core.services.priority.enforce import check_priority, log_decision  # Session 1086 PR 3c
            _pd = check_priority('CoLeadershipAgent', trigger_source='user_chat'); log_decision(_pd, 'CoLeadershipAgent')
            result = agent.execute(operation=operation, **params)
            return result

        except ImportError:
            return {'success': False, 'error': 'Co-leadership module not available'}
        except Exception as e:
            logger.error(f"Co-Leadership Agent error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _handle_web_search(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle web_search calls - uses external search API."""
        query = arguments.get('query')

        logger.info(f"Web Search: query='{query[:50]}...'")

        try:
            # Web search can be implemented with various providers
            # For now, return a placeholder
            return {
                'success': False,
                'error': 'Web search not yet configured. Add SEARCH_API_KEY to enable.'
            }

        except Exception as e:
            logger.error(f"Web Search error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _handle_create_brand_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_brand_video workflow calls."""
        brand_name = arguments.get('brand_name')
        style = arguments.get('style', 'modern')
        project_id = arguments.get('project_id')

        logger.info(f"Create Brand Video: brand='{brand_name}', style={style}")

        try:
            # This is a complex workflow that orchestrates multiple agents
            # Typically handled by workflow system
            return {
                'success': False,
                'error': 'Brand video workflow should be invoked through the workflow system'
            }

        except Exception as e:
            logger.error(f"Brand Video error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
