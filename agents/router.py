"""
Agent Router - Intent-Based Routing System
==========================================

Session 202: Created as Phase 2 of Agent Architecture Refactor
Session 204: Phase 5 - Tool Consolidation (all tools route through agents)

This router allows the Assistant to speak INTENT rather than IMPLEMENTATION.
Instead of knowing specific tool names and parameter formats, the Assistant
expresses what it wants to accomplish, and the router handles the rest.

Example:
    # Before (Assistant needs implementation details):
    tool_name = 'image_generation_agent'
    parameters = {'prompt': '...', 'model': 'sd3-large-turbo', 'style': 'pixar'}

    # After (Assistant expresses intent):
    result = AgentRouter.route('create_image', {'prompt': '...', 'style': 'pixar'}, user)

The router:
1. Maps intents to the appropriate specialist agent
2. Translates context into agent-specific parameters
3. Executes the operation
4. Returns a consistent result format

Session 204 Addition:
- execute_tool(): Single entry point for ALL tool calls from GPT
- All tools now route through specialist agents (no direct tool access)
- Preference learning integrated via agent execution
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum

from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)
User = get_user_model()


class Intent(str, Enum):
    """
    Taxonomy of user intents.
    The Assistant detects these from natural language.
    """
    # Image intents
    CREATE_IMAGE = 'create_image'
    CREATE_LOGO = 'create_logo'
    CREATE_SOCIAL_MEDIA = 'create_social_media'
    EDIT_IMAGE = 'edit_image'
    UPSCALE_IMAGE = 'upscale_image'
    REMOVE_BACKGROUND = 'remove_background'
    CREATE_VARIATIONS = 'create_variations'
    RECOLOR_IMAGE = 'recolor_image'
    ERASE_OBJECT = 'erase_object'
    REPLACE_OBJECT = 'replace_object'
    INPAINT = 'inpaint'
    OUTPAINT = 'outpaint'

    # Video intents
    CREATE_VIDEO = 'create_video'
    ANIMATE_IMAGE = 'animate_image'
    EXTEND_VIDEO = 'extend_video'
    EDIT_VIDEO = 'edit_video'
    ADD_TEXT_TO_VIDEO = 'add_text_to_video'
    ADD_MUSIC_TO_VIDEO = 'add_music_to_video'
    COLOR_GRADE_VIDEO = 'color_grade_video'
    CHAIN_VIDEOS = 'chain_videos'
    CREATE_TALKING_CHARACTER = 'create_talking_character'  # Session 204: Talking character agent

    # Audio intents
    CREATE_SPEECH = 'create_speech'
    CREATE_SOUND_EFFECT = 'create_sound_effect'
    ADD_VOICEOVER = 'add_voiceover'

    # 3D intents
    CREATE_3D = 'create_3d'
    CONVERT_TO_3D = 'convert_to_3d'

    # Research intents
    WEB_SEARCH = 'web_search'
    RESEARCH_TOPIC = 'research_topic'

    # Workflow intents
    RUN_WORKFLOW = 'run_workflow'
    CREATE_PROJECT = 'create_project'
    CREATE_BRAND_VIDEO = 'create_brand_video'  # Session 204: Brand video workflow

    # Training intents
    TRAIN_CHARACTER = 'train_character'  # Session 204: Character/style training

    # Leadership intents
    EXECUTIVE_REVIEW = 'executive_review'
    STRATEGIC_REVIEW = 'strategic_review'


@dataclass
class RouteResult:
    """Result of routing an intent to an agent."""
    success: bool
    data: Dict[str, Any]
    agent_used: str
    operation: str
    error: Optional[str] = None


class AgentRouter:
    """
    Routes user intents to the appropriate specialist agent.

    This is the central routing layer that decouples the Assistant
    from implementation details. The Assistant expresses WHAT it wants,
    and the router figures out HOW to accomplish it.
    """

    # Intent to Agent mapping
    # Format: intent -> (agent_module, agent_class, method_name, param_transformer)
    ROUTES: Dict[Intent, Tuple[str, str, str, Optional[Callable]]] = {
        # Image routes -> ImageAgent
        Intent.CREATE_IMAGE: ('agents.image_agent', 'ImageAgent', 'generate', None),
        Intent.CREATE_LOGO: ('agents.image_agent', 'ImageAgent', 'generate_logo', None),
        Intent.CREATE_SOCIAL_MEDIA: ('agents.image_agent', 'ImageAgent', 'generate_social', None),
        Intent.EDIT_IMAGE: ('agents.image_agent', 'ImageAgent', 'edit', None),
        Intent.UPSCALE_IMAGE: ('agents.image_agent', 'ImageAgent', 'edit', lambda ctx: {**ctx, 'operation': 'upscale'}),
        Intent.REMOVE_BACKGROUND: ('agents.image_agent', 'ImageAgent', 'edit', lambda ctx: {**ctx, 'operation': 'remove_background'}),
        Intent.CREATE_VARIATIONS: ('agents.image_agent', 'ImageAgent', 'edit', lambda ctx: {**ctx, 'operation': 'variations'}),
        Intent.RECOLOR_IMAGE: ('agents.image_agent', 'ImageAgent', 'edit', lambda ctx: {**ctx, 'operation': 'recolor'}),
        Intent.ERASE_OBJECT: ('agents.image_agent', 'ImageAgent', 'edit', lambda ctx: {**ctx, 'operation': 'erase', 'replace_prompt': ''}),
        Intent.REPLACE_OBJECT: ('agents.image_agent', 'ImageAgent', 'edit', lambda ctx: {**ctx, 'operation': 'search_and_replace'}),
        Intent.INPAINT: ('agents.image_agent', 'ImageAgent', 'edit', lambda ctx: {**ctx, 'operation': 'inpaint'}),
        Intent.OUTPAINT: ('agents.image_agent', 'ImageAgent', 'edit', lambda ctx: {**ctx, 'operation': 'outpaint'}),

        # Video routes -> VideoAgent
        Intent.CREATE_VIDEO: ('agents.video_agent', 'VideoAgent', 'generate', None),
        Intent.ANIMATE_IMAGE: ('agents.video_agent', 'VideoAgent', 'animate_image', None),
        Intent.EXTEND_VIDEO: ('agents.video_agent', 'VideoAgent', 'extend_video', None),
        Intent.EDIT_VIDEO: ('agents.video_agent', 'VideoAgent', 'edit', None),
        Intent.ADD_TEXT_TO_VIDEO: ('agents.video_agent', 'VideoAgent', 'edit', lambda ctx: {**ctx, 'operation': 'add_text_overlay'}),
        Intent.ADD_MUSIC_TO_VIDEO: ('agents.video_agent', 'VideoAgent', 'add_music_to_video', None),
        Intent.COLOR_GRADE_VIDEO: ('agents.video_agent', 'VideoAgent', 'edit', lambda ctx: {**ctx, 'operation': 'apply_color_grade'}),
        Intent.CHAIN_VIDEOS: ('agents.video_agent', 'VideoAgent', 'chain_videos_davinci', None),

        # Audio routes -> AudioAgent
        Intent.CREATE_SPEECH: ('agents.audio_agent', 'AudioAgent', 'generate_speech', None),
        Intent.CREATE_SOUND_EFFECT: ('agents.audio_agent', 'AudioAgent', 'generate_sound_effect', None),
        Intent.ADD_VOICEOVER: ('agents.audio_agent', 'AudioAgent', 'add_voiceover', None),

        # 3D routes -> ThreeDGenerationAgent
        Intent.CREATE_3D: ('agents.three_d_generation_agent', 'ThreeDGenerationAgent', 'execute', None),
        Intent.CONVERT_TO_3D: ('agents.three_d_generation_agent', 'ThreeDGenerationAgent', 'execute', None),

        # Workflow routes -> WorkflowOrchestrationAgent
        Intent.RUN_WORKFLOW: ('agents.workflow_orchestration_agent', 'WorkflowOrchestrationAgent', 'execute', None),
        Intent.CREATE_BRAND_VIDEO: ('agents.workflow_orchestration_agent', 'WorkflowOrchestrationAgent', 'create_brand_video', None),

        # Research routes -> ResearchAgent (Session 203: Spider Integration)
        Intent.WEB_SEARCH: ('agents.research_agent', 'ResearchAgent', 'search', lambda ctx: {'query': ctx.get('query', '')}),
        Intent.RESEARCH_TOPIC: ('agents.research_agent', 'ResearchAgent', 'research_topic', lambda ctx: {'topic': ctx.get('topic', ctx.get('query', ''))}),

        # Training routes -> CharacterTrainingAgent (Session 204: Tool Consolidation)
        Intent.TRAIN_CHARACTER: ('agents.character_training_agent', 'CharacterTrainingAgent', 'execute', None),

        # Talking character routes -> TalkingCharacterAgent (Session 204: Tool Consolidation)
        Intent.CREATE_TALKING_CHARACTER: ('agents.talking_character_agent', 'TalkingCharacterAgent', 'execute', None),

        # Leadership routes (Session 204: Tool Consolidation)
        Intent.EXECUTIVE_REVIEW: ('agents.coleadership_agent', 'CoLeadershipAgent', 'execute', None),
        Intent.STRATEGIC_REVIEW: ('agents.coleadership_agent', 'CoLeadershipAgent', 'strategic_review', None),

        # Project creation (Session 204: Tool Consolidation)
        Intent.CREATE_PROJECT: ('agents.workflow_orchestration_agent', 'WorkflowOrchestrationAgent', 'create_project_from_research', None),
    }

    # Legacy tool name to intent mapping (for backwards compatibility)
    TOOL_TO_INTENT: Dict[str, Intent] = {
        # Image tools
        'generate_image': Intent.CREATE_IMAGE,
        'image_generation_agent': Intent.CREATE_IMAGE,
        'image_editing_agent': Intent.EDIT_IMAGE,
        'upscale_image': Intent.UPSCALE_IMAGE,
        'remove_background': Intent.REMOVE_BACKGROUND,
        'create_variations': Intent.CREATE_VARIATIONS,
        'recolor_image': Intent.RECOLOR_IMAGE,
        'erase_object': Intent.ERASE_OBJECT,
        'search_and_replace': Intent.REPLACE_OBJECT,
        'inpaint': Intent.INPAINT,
        'outpaint': Intent.OUTPAINT,
        'creative_upscale': Intent.UPSCALE_IMAGE,

        # Video tools
        'generate_video': Intent.CREATE_VIDEO,
        'video_generation_agent': Intent.CREATE_VIDEO,
        'video_editing_agent': Intent.EDIT_VIDEO,
        'animate_image': Intent.ANIMATE_IMAGE,
        'extend_video': Intent.EXTEND_VIDEO,
        'add_text_overlay': Intent.ADD_TEXT_TO_VIDEO,
        'add_text_to_video': Intent.ADD_TEXT_TO_VIDEO,
        'add_music': Intent.ADD_MUSIC_TO_VIDEO,
        'add_music_to_video': Intent.ADD_MUSIC_TO_VIDEO,
        'color_grade': Intent.COLOR_GRADE_VIDEO,
        'apply_color_grade': Intent.COLOR_GRADE_VIDEO,

        # Audio tools
        'generate_voice': Intent.CREATE_SPEECH,
        'generate_speech': Intent.CREATE_SPEECH,
        'audio_generation_agent': Intent.CREATE_SPEECH,
        'generate_sound': Intent.CREATE_SOUND_EFFECT,
        'generate_sound_effect': Intent.CREATE_SOUND_EFFECT,
        'add_voiceover': Intent.ADD_VOICEOVER,

        # 3D tools
        'three_d_generation_agent': Intent.CREATE_3D,
        'generate_3d': Intent.CREATE_3D,

        # Workflow tools
        'workflow_orchestration_agent': Intent.RUN_WORKFLOW,
        'create_brand_video': Intent.CREATE_BRAND_VIDEO,

        # Research tools (Session 203: Spider Integration)
        'web_search': Intent.WEB_SEARCH,
        'research_topic': Intent.RESEARCH_TOPIC,
        'research': Intent.RESEARCH_TOPIC,

        # Training tools (Session 204: Tool Consolidation)
        'character_training_agent': Intent.TRAIN_CHARACTER,
        'train_character': Intent.TRAIN_CHARACTER,
        'train_style': Intent.TRAIN_CHARACTER,

        # Talking character tools (Session 204: Tool Consolidation)
        'talking_character_agent': Intent.CREATE_TALKING_CHARACTER,
        'create_talking_character': Intent.CREATE_TALKING_CHARACTER,
        'make_image_talk': Intent.CREATE_TALKING_CHARACTER,

        # Co-leadership tools (Session 204: Tool Consolidation)
        'coleadership_agent': Intent.EXECUTIVE_REVIEW,
        'strategic_review': Intent.STRATEGIC_REVIEW,
        'create_project_from_research': Intent.CREATE_PROJECT,
    }

    @classmethod
    def route(
        cls,
        intent: str,
        context: Dict[str, Any],
        user: Optional[User] = None,
        session=None,
        project=None
    ) -> RouteResult:
        """
        Route an intent to the appropriate agent.

        Args:
            intent: Intent string (e.g., 'create_image', 'edit_video')
            context: Context dictionary with parameters
            user: Django user object
            session: Optional AI session
            project: Optional project

        Returns:
            RouteResult with success status and data
        """
        logger.info(f"🔀 AgentRouter routing intent: {intent}")
        logger.info(f"   Context keys: {list(context.keys())}")

        try:
            # Convert string to Intent enum
            try:
                intent_enum = Intent(intent)
            except ValueError:
                # Try legacy tool name mapping
                intent_enum = cls.TOOL_TO_INTENT.get(intent)
                if not intent_enum:
                    return RouteResult(
                        success=False,
                        data={},
                        agent_used='none',
                        operation='none',
                        error=f"Unknown intent: {intent}. Valid intents: {[i.value for i in Intent]}"
                    )
                logger.info(f"   Mapped legacy tool '{intent}' to intent '{intent_enum.value}'")

            # Get route configuration
            route_config = cls.ROUTES.get(intent_enum)
            if not route_config:
                return RouteResult(
                    success=False,
                    data={},
                    agent_used='none',
                    operation='none',
                    error=f"No route configured for intent: {intent_enum.value}"
                )

            module_path, class_name, method_name, param_transformer = route_config

            # Transform parameters if needed
            if param_transformer:
                context = param_transformer(context)

            # Import and instantiate agent
            logger.info(f"   Agent: {class_name}.{method_name}()")

            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name)

            # Instantiate agent with user
            if class_name in ('ImageAgent', 'VideoAgent', 'AudioAgent', 'ResearchAgent'):
                agent = agent_class(user=user, project_id=str(project.id) if project else None)
            else:
                agent = agent_class(user=user)

            # Get method
            method = getattr(agent, method_name)

            # Add session/project to context if not already present
            if session and 'session' not in context:
                context['session'] = session
            if project and 'project' not in context:
                context['project'] = project

            # Execute
            result = method(**context)

            # Determine success
            success = result.get('success', True) if isinstance(result, dict) else True

            return RouteResult(
                success=success,
                data=result if isinstance(result, dict) else {'result': result},
                agent_used=class_name,
                operation=method_name,
                error=result.get('error') if isinstance(result, dict) else None
            )

        except Exception as e:
            logger.error(f"❌ AgentRouter error: {str(e)}", exc_info=True)
            return RouteResult(
                success=False,
                data={},
                agent_used='unknown',
                operation='unknown',
                error=str(e)
            )

    @classmethod
    def route_tool(
        cls,
        tool_name: str,
        parameters: Dict[str, Any],
        user: Optional[User] = None,
        session=None,
        project=None
    ) -> RouteResult:
        """
        Route a legacy tool call through the router.
        This provides backwards compatibility with existing tool definitions.

        Args:
            tool_name: Legacy tool name (e.g., 'image_generation_agent')
            parameters: Tool parameters
            user: Django user object
            session: Optional AI session
            project: Optional project

        Returns:
            RouteResult with success status and data
        """
        logger.info(f"🔀 AgentRouter routing tool: {tool_name}")

        # Map tool name to intent
        intent = cls.TOOL_TO_INTENT.get(tool_name)

        if not intent:
            # Fall back to using tool_name as intent
            return cls.route(tool_name, parameters, user, session, project)

        return cls.route(intent.value, parameters, user, session, project)

    @classmethod
    def get_available_intents(cls) -> Dict[str, str]:
        """
        Get all available intents with descriptions.

        Returns:
            Dictionary of intent name -> description
        """
        descriptions = {
            Intent.CREATE_IMAGE: "Generate an image from a text prompt",
            Intent.CREATE_LOGO: "Generate a professional logo with brand expertise",
            Intent.CREATE_SOCIAL_MEDIA: "Generate platform-optimized social media content",
            Intent.EDIT_IMAGE: "Edit an existing image (upscale, remove bg, etc.)",
            Intent.UPSCALE_IMAGE: "Upscale an image to 4x resolution",
            Intent.REMOVE_BACKGROUND: "Remove the background from an image",
            Intent.CREATE_VARIATIONS: "Create variations of an existing image",
            Intent.RECOLOR_IMAGE: "Change the color of objects in an image",
            Intent.ERASE_OBJECT: "Erase/remove an object from an image",
            Intent.REPLACE_OBJECT: "Replace one object with another in an image",
            Intent.INPAINT: "Fill in masked areas of an image",
            Intent.OUTPAINT: "Extend an image beyond its borders",
            Intent.CREATE_VIDEO: "Generate a video from text",
            Intent.ANIMATE_IMAGE: "Animate a still image into video",
            Intent.EXTEND_VIDEO: "Extend an existing video",
            Intent.EDIT_VIDEO: "Edit a video (text, color, audio)",
            Intent.ADD_TEXT_TO_VIDEO: "Add text overlay to a video",
            Intent.ADD_MUSIC_TO_VIDEO: "Add music/audio to a video",
            Intent.COLOR_GRADE_VIDEO: "Apply color grading to a video",
            Intent.CHAIN_VIDEOS: "Chain multiple videos together",
            Intent.CREATE_SPEECH: "Generate speech from text",
            Intent.CREATE_SOUND_EFFECT: "Generate a sound effect",
            Intent.ADD_VOICEOVER: "Add voiceover narration to a video",
            Intent.CREATE_3D: "Generate a 3D model",
            Intent.CONVERT_TO_3D: "Convert an image to a 3D model",
            Intent.WEB_SEARCH: "Search the web using Google + 40+ specialized spiders",
            Intent.RESEARCH_TOPIC: "Research a topic in depth with spider intelligence",
            Intent.RUN_WORKFLOW: "Run a multi-step workflow",
            Intent.CREATE_PROJECT: "Create a new project",
            Intent.CREATE_BRAND_VIDEO: "Create a complete brand video from concept",
            Intent.TRAIN_CHARACTER: "Train a FLUX LoRA model for consistent character/style",
            Intent.CREATE_TALKING_CHARACTER: "Create talking character video from image + text",
            Intent.EXECUTIVE_REVIEW: "Get executive team review/feedback",
            Intent.STRATEGIC_REVIEW: "Get strategic review/feedback on research",
        }

        return {intent.value: descriptions.get(intent, "No description") for intent in Intent}

    @classmethod
    def get_intent_for_tool(cls, tool_name: str) -> Optional[str]:
        """
        Get the intent for a legacy tool name.

        Args:
            tool_name: Legacy tool name

        Returns:
            Intent string or None if not found
        """
        intent = cls.TOOL_TO_INTENT.get(tool_name)
        return intent.value if intent else None

    @classmethod
    def execute_tool(
        cls,
        tool_name: str,
        arguments: Dict[str, Any],
        user: Optional[User] = None,
        session=None,
        project=None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Session 204: Single entry point for ALL tool calls from GPT.

        This method consolidates tool execution through the router.
        It handles:
        1. Mapping legacy tool names to intents
        2. Transforming arguments for agent methods
        3. Executing through the appropriate specialist agent
        4. Consistent result format

        Args:
            tool_name: Tool name from GPT (e.g., 'image_generation_agent')
            arguments: Tool arguments from GPT
            user: Django user object
            session: Optional AI session
            project: Optional project
            context: Optional additional context

        Returns:
            Dictionary with execution results
        """
        logger.info(f"🎯 AgentRouter.execute_tool: {tool_name}")
        logger.info(f"   Arguments: {list(arguments.keys())}")

        # Merge context with arguments (context is lower priority)
        merged_args = {**(context or {}), **arguments}

        # Handle operation-based tools that need special transformation
        if tool_name == 'image_editing_agent':
            # Transform to intent based on operation
            operation = arguments.get('operation', 'edit')
            params = arguments.get('params', {})
            image_id = arguments.get('image_id')

            operation_intent_map = {
                'upscale': Intent.UPSCALE_IMAGE,
                'remove_background': Intent.REMOVE_BACKGROUND,
                'create_variations': Intent.CREATE_VARIATIONS,
                'recolor': Intent.RECOLOR_IMAGE,
                'search_and_replace': Intent.REPLACE_OBJECT if params.get('replace_prompt') else Intent.ERASE_OBJECT,
                'creative_upscale': Intent.UPSCALE_IMAGE,
                'inpaint': Intent.INPAINT,
                'outpaint': Intent.OUTPAINT,
            }
            intent = operation_intent_map.get(operation, Intent.EDIT_IMAGE)

            # Flatten params into context
            merged_args = {
                'image_id': image_id,
                'operation': operation,
                **params,
                'project_id': arguments.get('project_id'),
            }

            result = cls.route(intent.value, merged_args, user, session, project)
            return result.data if result.success else {'success': False, 'error': result.error}

        elif tool_name == 'video_generation_agent':
            # Transform to intent based on operation
            operation = arguments.get('operation', 'generate')
            params = arguments.get('params', {})

            operation_intent_map = {
                'generate': Intent.CREATE_VIDEO,
                'animate': Intent.ANIMATE_IMAGE,
                'extend': Intent.EXTEND_VIDEO,
                'chain': Intent.CHAIN_VIDEOS,
                'lip_sync': Intent.EDIT_VIDEO,
            }
            intent = operation_intent_map.get(operation, Intent.CREATE_VIDEO)

            # Flatten params
            merged_args = {
                'operation': operation,
                **params,
                'project_id': arguments.get('project_id'),
            }

            result = cls.route(intent.value, merged_args, user, session, project)
            return result.data if result.success else {'success': False, 'error': result.error}

        elif tool_name == 'audio_generation_agent':
            # Transform to intent based on operation
            operation = arguments.get('operation', 'generate_voice')
            params = arguments.get('params', {})

            operation_intent_map = {
                'generate_voice': Intent.CREATE_SPEECH,
                'add_voiceover': Intent.ADD_VOICEOVER,
            }
            intent = operation_intent_map.get(operation, Intent.CREATE_SPEECH)

            # Flatten params
            merged_args = {
                'operation': operation,
                **params,
                'project_id': arguments.get('project_id'),
            }

            result = cls.route(intent.value, merged_args, user, session, project)
            return result.data if result.success else {'success': False, 'error': result.error}

        elif tool_name == 'video_editing_agent':
            # Transform to intent based on operation
            operation = arguments.get('operation', 'edit')
            params = arguments.get('params', {})
            video_id = arguments.get('video_id')

            # Most video editing goes through EDIT_VIDEO
            merged_args = {
                'video_id': video_id,
                'operation': operation,
                **params,
                'project_id': arguments.get('project_id'),
            }

            result = cls.route(Intent.EDIT_VIDEO.value, merged_args, user, session, project)
            return result.data if result.success else {'success': False, 'error': result.error}

        # Session 239: For workflow_orchestration_agent, auto-extract style from topic
        # GPT-5.1 often fails to extract style_preferences, so we do it ourselves
        if tool_name == 'workflow_orchestration_agent':
            topic = merged_args.get('topic', '').lower()
            style_prefs = merged_args.get('style_preferences', '')

            if not style_prefs:
                animated_styles = {
                    'pixar': 'pixar', 'disney': 'disney', 'dreamworks': 'dreamworks',
                    'ghibli': 'ghibli', 'studio ghibli': 'ghibli', 'anime': 'anime',
                    'cartoon': 'cartoon', 'animated': 'cartoon', 'south park': 'south_park',
                    'simpsons': 'simpsons', 'family guy': 'family_guy', 'chibi': 'chibi',
                    'manga': 'manga', 'looney tunes': 'looney_tunes', '3d animated': 'pixar'
                }
                for style_key, style_value in animated_styles.items():
                    if style_key in topic:
                        merged_args['style_preferences'] = style_value
                        logger.info(f"🎬 Session 239: Router auto-detected style '{style_value}' from topic")
                        break

        # Standard tool routing
        result = cls.route_tool(tool_name, merged_args, user, session, project)

        if result.success:
            return result.data
        else:
            return {
                'success': False,
                'error': result.error,
                'agent_used': result.agent_used,
                'operation': result.operation
            }

    @classmethod
    def get_router_enabled_tools(cls) -> list:
        """
        Session 204: Get the list of tools that can be routed through the AgentRouter.

        Returns:
            List of tool names that can be executed via execute_tool()
        """
        return list(cls.TOOL_TO_INTENT.keys())

    # =========================================================================
    # SESSION 206: MULTI-AGENT COLLABORATION
    # =========================================================================

    @classmethod
    def consult(
        cls,
        requesting_agent: str,
        specialist: str,
        question: str,
        context: Dict[str, Any],
        user: Optional[User] = None
    ) -> Dict[str, Any]:
        """
        Session 206: Enable agents to consult with specialist agents.

        This enables collaboration patterns like:
        - ImageAgent consulting ResearchAgent for style research
        - VideoAgent consulting ImageAgent for thumbnail generation
        - AudioAgent consulting ResearchAgent for voice style analysis

        Args:
            requesting_agent: Name of the agent requesting consultation
            specialist: Name of the specialist agent to consult
            question: What the requesting agent wants to know
            context: Relevant context for the consultation
            user: Django user for preference/memory access

        Returns:
            Dictionary with consultation results
        """
        logger.info(f"🤝 Agent Consultation: {requesting_agent} → {specialist}")
        logger.info(f"   Question: {question[:100]}...")

        # Map specialist names to intents
        specialist_intents = {
            'research': Intent.RESEARCH_TOPIC,
            'image': Intent.CREATE_IMAGE,
            'video': Intent.CREATE_VIDEO,
            'audio': Intent.CREATE_SPEECH,
        }

        intent = specialist_intents.get(specialist.lower())
        if not intent:
            logger.warning(f"Unknown specialist: {specialist}")
            return {
                'success': False,
                'error': f'Unknown specialist agent: {specialist}',
                'consultation': None
            }

        # Build consultation context
        consultation_context = {
            'query': question,
            'prompt': question,  # Some agents use 'prompt'
            'consultation_from': requesting_agent,
            'is_consultation': True,
            **context
        }

        # Route to specialist
        result = cls.route(intent.value, consultation_context, user)

        # Log collaboration
        cls._log_collaboration(
            requesting_agent=requesting_agent,
            specialist=specialist,
            question=question,
            success=result.success,
            user=user
        )

        return {
            'success': result.success,
            'consultation': result.data if result.success else None,
            'specialist': specialist,
            'error': result.error if not result.success else None
        }

    @classmethod
    def _log_collaboration(
        cls,
        requesting_agent: str,
        specialist: str,
        question: str,
        success: bool,
        user: Optional[User] = None
    ):
        """Log agent collaboration for analytics and learning."""
        try:
            # Try to log to database
            from core.models_unified_system import AgentCollaboration
            AgentCollaboration.objects.create(
                requesting_agent=requesting_agent,
                specialist_agent=specialist,
                question=question[:500],
                success=success,
                user_id=user.id if user else None
            )
        except Exception as e:
            # Model might not exist yet, just log to console
            logger.debug(f"Collaboration logged: {requesting_agent}→{specialist} (success={success})")

    @classmethod
    def get_collaboration_stats(cls, user: Optional[User] = None) -> Dict[str, Any]:
        """
        Session 206: Get collaboration statistics.

        Args:
            user: Optional user to filter stats

        Returns:
            Collaboration statistics
        """
        try:
            from core.models_unified_system import AgentCollaboration
            from django.db.models import Count

            queryset = AgentCollaboration.objects.all()
            if user:
                queryset = queryset.filter(user=user)

            # Get collaboration counts by agent pair
            collaborations = queryset.values(
                'requesting_agent', 'specialist_agent'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:10]

            # Get success rate
            total = queryset.count()
            successful = queryset.filter(success=True).count()
            success_rate = (successful / total * 100) if total > 0 else 0

            return {
                'success': True,
                'total_collaborations': total,
                'success_rate': round(success_rate, 2),
                'top_collaborations': list(collaborations)
            }

        except Exception as e:
            logger.error(f"Error getting collaboration stats: {e}")
            return {
                'success': False,
                'total_collaborations': 0,
                'success_rate': 0,
                'top_collaborations': [],
                'error': str(e)
            }


# Convenience function for direct routing
def route(intent: str, context: Dict[str, Any], user=None, **kwargs) -> Dict[str, Any]:
    """
    Route an intent and return the result data.
    Convenience function for simple usage.

    Args:
        intent: Intent string
        context: Context dictionary
        user: Django user
        **kwargs: Additional arguments (session, project)

    Returns:
        Result dictionary
    """
    result = AgentRouter.route(intent, context, user, **kwargs)

    if result.success:
        return result.data
    else:
        return {
            'success': False,
            'error': result.error
        }


__all__ = [
    'AgentRouter',
    'Intent',
    'RouteResult',
    'route',
    'execute_tool',  # Session 204: Single entry point for all tools
    'consult',  # Session 206: Multi-agent collaboration
]


# Session 204: Convenience function for single entry point
def execute_tool(tool_name: str, arguments: Dict[str, Any], user=None, **kwargs) -> Dict[str, Any]:
    """
    Execute a tool through the AgentRouter.
    Convenience function for direct usage from personal_ai_assistant.

    Args:
        tool_name: Tool name from GPT
        arguments: Tool arguments
        user: Django user
        **kwargs: Additional arguments (session, project, context)

    Returns:
        Result dictionary
    """
    return AgentRouter.execute_tool(tool_name, arguments, user, **kwargs)


# Session 206: Convenience function for agent consultation
def consult(
    requesting_agent: str,
    specialist: str,
    question: str,
    context: Dict[str, Any] = None,
    user=None
) -> Dict[str, Any]:
    """
    Request consultation from a specialist agent.
    Convenience function for agent-to-agent collaboration.

    Example usage:
        from agents.router import consult

        # ImageAgent consulting ResearchAgent
        result = consult(
            requesting_agent='ImageAgent',
            specialist='research',
            question='Find trending cyberpunk art styles',
            context={'style_focus': 'neon', 'era': 'modern'},
            user=request.user
        )

    Args:
        requesting_agent: Name of the agent making the request
        specialist: Specialist to consult ('research', 'image', 'video', 'audio')
        question: What you want to know
        context: Additional context for the consultation
        user: Django user for preferences/memory

    Returns:
        Dictionary with consultation results
    """
    return AgentRouter.consult(
        requesting_agent=requesting_agent,
        specialist=specialist,
        question=question,
        context=context or {},
        user=user
    )
