"""
EnhancedPersonalAIAssistant EPAAgentToolsMixin — extracted handler methods.
"""

"""
Enhanced Personal AI Assistant with Database and System Access
===============================================================

This module extends the Personal AI Assistant with direct database access,
system status monitoring, and agent execution capabilities.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from django.contrib.auth import get_user_model
from django.db import connection
from django.utils import timezone

from core.models import EnhancedUserProfile, UserMemoryContext
from core.personal_ai_assistant import PersonalAIAssistant
from core.llm_enforcer import LLMEnforcer
from core.unified_memory_manager import get_memory_manager
from core.services.memory_context_service import get_memory_context_service
from core.agents.registry import get_agent_registry
from advisors.registry import get_advisor_registry
try:
    from self_awareness.embeddings import CodebaseEmbeddings
except ImportError:
    # Fallback if CodebaseEmbeddings is not available
    class CodebaseEmbeddings:
        def __init__(self):
            pass

# Session 266: Super Platform Integration - Dynamic Prompting System
try:
    from core.super_platform import (
        QueryClassifier,
        ClassificationResult,
        ContextAggregator,
        AggregatedContext,
        get_learning_loop_service,
        get_scifi_integration_service,
        get_learning_companion_service,
    )
    SUPER_PLATFORM_AVAILABLE = True
except ImportError as e:
    SUPER_PLATFORM_AVAILABLE = False

# Session 482: Proactive Intelligence Integration - Connect 19 Autonomous Situations
try:
    from core.services.proactive_intelligence import (
        ProactiveIntelligenceService,
        get_proactive_intelligence_service
    )
    PROACTIVE_INTELLIGENCE_AVAILABLE = True
except ImportError as e:
    PROACTIVE_INTELLIGENCE_AVAILABLE = False
    ProactiveIntelligenceService = None
    get_proactive_intelligence_service = lambda user=None: None
    # Provide fallback classes for graceful degradation
    class QueryClassifier:
        def classify(self, query):
            return None
    class ContextAggregator:
        def __init__(self, user=None):
            pass
        def aggregate(self, classification, query):
            return None
    ClassificationResult = None
    AggregatedContext = None

# Session 482: Reference Resolution - Handle "it", "that", "the first one"
try:
    from core.services.reference_resolver import (
        ReferenceResolver,
        get_reference_resolver
    )
    REFERENCE_RESOLVER_AVAILABLE = True
except ImportError as e:
    REFERENCE_RESOLVER_AVAILABLE = False
    ReferenceResolver = None
    get_reference_resolver = lambda session_id='default': None

# Session 482: Smart Suggestions - Context-aware follow-up suggestions
try:
    from core.services.smart_suggestions import (
        SmartSuggestionsService,
        get_smart_suggestions_service
    )
    SMART_SUGGESTIONS_AVAILABLE = True
except ImportError as e:
    SMART_SUGGESTIONS_AVAILABLE = False
    SmartSuggestionsService = None
    get_smart_suggestions_service = lambda session_id='default': None

# Session 482: Task Memory - Multi-turn task tracking
try:
    from core.services.task_memory import (
        TaskMemoryService,
        get_task_memory_service
    )
    TASK_MEMORY_AVAILABLE = True
except ImportError as e:
    TASK_MEMORY_AVAILABLE = False
    TaskMemoryService = None
    get_task_memory_service = lambda session_id='default': None

# Session 806: Context Optimization Components
try:
    from core.services.context_budget_manager import (
        get_context_budget_manager,
        SectionPriority,
    )
    from core.services.lazy_context_loader import (
        get_lazy_context_loader,
        QueryType,
    )
    from core.services.context_summarizer import get_context_summarizer
    from core.assistant.tool_category_router import get_tool_category_router
    CONTEXT_OPTIMIZATION_AVAILABLE = True
except ImportError as e:
    CONTEXT_OPTIMIZATION_AVAILABLE = False
    get_context_budget_manager = lambda: None
    get_lazy_context_loader = lambda: None
    get_context_summarizer = lambda: None
    get_tool_category_router = lambda: None
    SectionPriority = None
    QueryType = None

logger = logging.getLogger(__name__)
User = get_user_model()




class EPAAgentToolsMixin:
    """Mixin providing handler methods for EnhancedPersonalAIAssistant."""

    def _tool_upscale_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the upscale_image tool - Session 128."""
        logger.info(f"🎨 UPSCALE_IMAGE TOOL CALLED!")
        logger.info(f"🤖 Delegating to Image Editing Agent...")

        try:
            image_id = arguments['image_id']

            # Get current project if in session
            current_project = getattr(self, 'project', None)  # Session 179: Fixed project access

            # Session 128: Delegate to specialized Image Editing Agent
            # Session 202: Consolidated to unified ImageAgent
            from core.agents import ImageAgent

            agent = ImageAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            # Execute agent workflow
            result = agent.edit(
                operation='upscale',
                image_id=image_id
            )

            return result

        except Exception as e:
            logger.error(f"❌ Upscale tool error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to upscale image: {str(e)}"
            }

    # Session 128: Updated to use Image Editing Agent
    def _tool_remove_background(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the remove_background tool - Session 128."""
        logger.info(f"🎨 REMOVE_BACKGROUND TOOL CALLED!")
        logger.info(f"🤖 Delegating to Image Editing Agent...")

        try:
            image_id = arguments['image_id']  # Already converted by handler

            # Get current project if in session
            current_project = getattr(self, 'project', None)  # Session 179: Fixed project access

            # Session 128: Delegate to specialized Image Editing Agent
            # Session 202: Consolidated to unified ImageAgent
            from core.agents import ImageAgent

            agent = ImageAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            # Execute agent workflow
            result = agent.edit(
                operation='remove_background',
                image_id=image_id
            )

            return result

        except Exception as e:
            logger.error(f"❌ Remove background tool error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to remove background: {str(e)}"
            }

    # Session 128: Updated to use Image Editing Agent
    def _tool_create_variations(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the create_image_variations tool - Session 128."""
        logger.info(f"🎨 CREATE_VARIATIONS TOOL CALLED!")
        logger.debug(f"User: {getattr(self.user, 'username', 'N/A')}")
        logger.info(f"🤖 Delegating to Image Editing Agent...")

        try:
            image_id = arguments['image_id']
            count = arguments.get('count', 3)
            prompt = arguments.get('prompt', 'creative variation')

            logger.debug(f"Image ID: {image_id}, Count: {count}")

            # Get current project if in session
            current_project = getattr(self, 'project', None)  # Session 179: Fixed project access

            # Session 128: Delegate to specialized Image Editing Agent
            from core.agents import ImageEditingAgent

            agent = ImageEditingAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )
            logger.debug(f"Created agent with user: {agent.user.username}")

            # Execute agent workflow
            result = agent.execute(
                operation='variations',
                image_id=image_id,
                count=count,
                prompt=prompt
            )

            return result

        except Exception as e:
            logger.error(f"❌ Create variations tool error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to create variations: {str(e)}"
            }

    # Session 128: Updated to use Image Editing Agent
    def _tool_erase_object(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the erase_object tool - Session 128."""
        logger.info(f"🎨 ERASE_OBJECT TOOL CALLED!")
        logger.info(f"🤖 Delegating to Image Editing Agent...")

        try:
            image_id = arguments['image_id']
            object_description = arguments['object_description']

            # Get current project if in session
            current_project = getattr(self, 'project', None)  # Session 179: Fixed project access

            # Session 128: Delegate to specialized Image Editing Agent
            from core.agents import ImageEditingAgent

            agent = ImageEditingAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            # Execute agent workflow
            result = agent.execute(
                operation='erase_object',
                image_id=image_id,
                search_prompt=object_description
            )

            return result

        except Exception as e:
            logger.error(f"❌ Erase object tool error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to erase object: {str(e)}"
            }

    # Session 128: Updated to use Image Editing Agent
    def _tool_recolor_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the recolor_image tool - Session 128."""
        logger.info(f"🎨 RECOLOR_IMAGE TOOL CALLED!")
        logger.info(f"🤖 Delegating to Image Editing Agent...")

        try:
            image_id = arguments['image_id']
            prompt = arguments['prompt']
            select_prompt = arguments.get('select_prompt')

            # Get current project if in session
            current_project = getattr(self, 'project', None)  # Session 179: Fixed project access

            # Session 128: Delegate to specialized Image Editing Agent
            from core.agents import ImageEditingAgent

            agent = ImageEditingAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            # Execute agent workflow
            result = agent.execute(
                operation='recolor',
                image_id=image_id,
                prompt=prompt,
                select_prompt=select_prompt
            )

            return result

        except Exception as e:
            logger.error(f"❌ Recolor tool error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to recolor image: {str(e)}"
            }

    # Session 128: Updated to use Image Editing Agent
    def _tool_refine_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the refine_image tool - Session 128.
        This is a general-purpose refinement tool that GPT can use for variations and modifications.
        """
        logger.info(f"🎨 REFINE_IMAGE TOOL CALLED!")
        logger.info(f"🤖 Delegating to Image Editing Agent...")

        try:
            image_id = arguments['image_id']
            refinement_request = arguments['refinement_request']

            # Get current project if in session
            current_project = getattr(self, 'project', None)  # Session 179: Fixed project access

            # Session 128: Delegate to specialized Image Editing Agent
            from core.agents import ImageEditingAgent

            agent = ImageEditingAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            # Execute agent workflow
            result = agent.execute(
                operation='refine',
                image_id=image_id,
                prompt=refinement_request
            )

            return result

        except Exception as e:
            logger.error(f"❌ Refine image tool error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to refine image: {str(e)}"
            }

    # Session 151: Advanced Image Editing Tools
    def _tool_search_and_replace(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute search_and_replace tool - Remove/replace specific objects in images.
        Session 151: Advanced Image Editing Suite
        """
        logger.info(f"🔍 SEARCH_AND_REPLACE TOOL CALLED!")
        logger.info(f"🤖 Delegating to Image Editing Agent...")

        try:
            image_id = arguments['image_id']
            search_prompt = arguments['search_prompt']
            replace_prompt = arguments.get('replace_prompt', '')  # Optional

            # Get current project if in session
            current_project = getattr(self, 'project', None)  # Session 179: Fixed project access

            # Delegate to specialized Image Editing Agent
            from core.agents import ImageEditingAgent

            agent = ImageEditingAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            # Execute agent workflow
            result = agent.execute(
                operation='search_and_replace',
                image_id=image_id,
                search_prompt=search_prompt,
                replace_prompt=replace_prompt
            )

            return result

        except Exception as e:
            logger.error(f"❌ Search and replace tool error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to search and replace: {str(e)}"
            }

    def _tool_creative_upscale(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute creative_upscale tool - Upscale with AI-generated creative details.
        Session 151: Advanced Image Editing Suite
        """
        logger.info(f"✨ CREATIVE_UPSCALE TOOL CALLED!")
        logger.info(f"🤖 Delegating to Image Editing Agent...")

        try:
            image_id = arguments['image_id']
            prompt = arguments['prompt']
            creativity = arguments.get('creativity', 0.3)

            # Get current project if in session
            current_project = getattr(self, 'project', None)  # Session 179: Fixed project access

            # Delegate to specialized Image Editing Agent
            from core.agents import ImageEditingAgent

            agent = ImageEditingAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            # Execute agent workflow
            result = agent.execute(
                operation='creative_upscale',
                image_id=image_id,
                prompt=prompt,
                creativity=creativity
            )

            return result

        except Exception as e:
            logger.error(f"❌ Creative upscale tool error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to creative upscale: {str(e)}"
            }

    # Session 127: Video & Audio Tool Handlers
    # Session 128: Updated to use Video Generation Agent
    def _tool_generate_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the generate_video tool - Session 128."""
        logger.info(f"🎬 GENERATE_VIDEO TOOL CALLED!")
        logger.info(f"🤖 Delegating to Video Generation Agent...")

        try:
            prompt = arguments['prompt']
            duration = arguments.get('duration', 5)
            image_id = arguments.get('image_id')  # Optional for image-to-video
            quality = arguments.get('quality', 'gen4_turbo')
            ratio = arguments.get('ratio', '1280:720')

            # Get current project if in session
            current_project = getattr(self, 'project', None)  # Session 179: Fixed project access

            # Session 128: Delegate to specialized Video Generation Agent
            from core.agents import VideoAgent

            # Session 517: BaseAgent only accepts user, not project_id
            agent = VideoAgent(user=self.user)
            # Store project_id as attribute if needed
            agent.project_id = str(current_project.id) if current_project else arguments.get('project_id')

            # Execute agent workflow
            result = agent.execute(
                prompt=prompt,
                image_id=image_id,
                duration=duration,
                quality=quality,
                ratio=ratio
            )

            if result.get('success'):
                # Format success message
                video_type = "Image-to-video" if image_id else "Text-to-video"
                message = f"✅ {video_type} generation started!\n\n"
                message += f"Task ID: {result.get('task_id')}\n"
                message += f"Estimated time: {result.get('estimated_time_seconds', 90)}s\n\n"
                message += "The video will automatically appear in the gallery when ready."

                return {
                    'success': True,
                    'video_id': result.get('video_id'),
                    'task_id': result.get('task_id'),
                    'message': message
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Video generation failed')
                }

        except Exception as e:
            logger.error(f"❌ Generate video tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    # Session 128: Updated to use Video Generation Agent
    def _tool_extend_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the extend_video tool - Session 128."""
        logger.info(f"🎬 EXTEND_VIDEO TOOL CALLED!")
        logger.info(f"🤖 Delegating to Video Generation Agent...")

        try:
            video_id = arguments['video_id']
            extension_seconds = arguments.get('extension_seconds', 10)
            prompt = arguments.get('prompt')

            # Session 128: Delegate to specialized Video Generation Agent
            from core.agents import VideoAgent

            # Don't need project_id for extension - it inherits from original video
            agent = VideoAgent(
                user=self.user,
                project_id=None
            )

            # Execute agent workflow
            result = agent.extend_video(
                video_id=video_id,
                extension_seconds=extension_seconds,
                prompt=prompt
            )

            if result.get('success'):
                message = f"✅ Video extension started!\n\n"
                message += f"Adding {extension_seconds} seconds to video {video_id}\n"
                message += f"Task ID: {result.get('task_id')}\n"
                message += f"Estimated time: {result.get('estimated_time_seconds', 120)}s\n\n"
                message += "The extended video will appear in the gallery when ready."

                return {
                    'success': True,
                    'video_id': result.get('video_id'),
                    'task_id': result.get('task_id'),
                    'message': message
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Video extension failed')
                }

        except Exception as e:
            logger.error(f"❌ Extend video tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_chain_videos(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the chain_videos tool."""
        try:
            from django.test import RequestFactory
            import json

            video_ids = arguments['video_ids']
            add_transitions = arguments.get('add_transitions', True)
            project_id = arguments.get('project_id')

            logger.info(f"🎬 Chaining {len(video_ids)} videos...")

            factory = RequestFactory()
            data = {
                'video_ids': video_ids,
                'add_transitions': add_transitions
            }
            if project_id:
                data['project_id'] = project_id

            from core.views_video import chain_videos_view
            view_request = factory.post('/api/tool/chain-videos/',
                                       json.dumps(data),
                                       content_type='application/json')
            view_request.user = self.user

            response = chain_videos_view(view_request)
            result = json.loads(response.content)

            if result.get('success'):
                return {
                    'success': True,
                    'video_url': result.get('video_path'),
                    'message': f"✅ Successfully combined {len(video_ids)} videos!\n\n" + \
                              f"Duration: {result.get('duration', 0):.1f}s\n" + \
                              f"The combined video is now available in your gallery."
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error_message', 'Video chaining failed')
                }

        except Exception as e:
            logger.error(f"❌ Chain videos tool error: {e}")
            return {'success': False, 'error': str(e)}

    # Session 175: Lip Sync for talking characters
    def _tool_lip_sync(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the lip_sync tool - Session 175.

        Sync lip movements in a video to match audio, making characters talk naturally.
        Uses Sync Labs Lipsync-2 via Replicate API.
        """
        logger.info(f"🎬 LIP_SYNC TOOL CALLED!")

        try:
            video_url = arguments.get('video_url')
            audio_url = arguments.get('audio_url')
            sync_mode = arguments.get('sync_mode', 'cut_off')
            temperature = float(arguments.get('temperature', 0.5))
            project_id = arguments.get('project_id')

            if not video_url:
                return {'success': False, 'error': 'video_url is required - provide URL to video with face'}

            if not audio_url:
                return {'success': False, 'error': 'audio_url is required - provide URL to audio file'}

            logger.info(f"   Video: {video_url[:60]}...")
            logger.info(f"   Audio: {audio_url[:60]}...")
            logger.info(f"   Mode: {sync_mode}, Temperature: {temperature}")

            # Call Replicate provider directly
            from content.replicate_provider import get_replicate_provider

            provider = get_replicate_provider()
            result = provider.lip_sync(
                video_url=video_url,
                audio_url=audio_url,
                sync_mode=sync_mode,
                temperature=temperature,
                active_speaker=False
            )

            if not result.success:
                return {
                    'success': False,
                    'error': result.error_message
                }

            # Return prediction info for polling
            return {
                'success': True,
                'prediction_id': result.prediction_id,
                'status': result.status,
                'estimated_time': result.estimated_time,
                'poll_endpoint': f'/api/video/lip-sync/status/{result.prediction_id}/',
                'message': f"🎬 **Lip Sync Started!**\n\n" +
                          f"Your video is being processed to sync lip movements to the audio.\n\n" +
                          f"**Prediction ID:** `{result.prediction_id}`\n" +
                          f"**Estimated Time:** ~{result.estimated_time} seconds\n\n" +
                          f"Use the poll endpoint to check status when complete.",
                'agent': 'LipSyncAgent',
                'operation': 'lip_sync',
                'operation_display': 'Syncing lip movements to audio'
            }

        except Exception as e:
            logger.error(f"❌ Lip sync tool error: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    # Session 175: Talking Character Pipeline for complete video creation
    def _tool_talking_character(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the talking_character tool - Session 175.

        Complete pipeline: Image + Text → Talking Character Video
        Combines TTS (ElevenLabs) + Image-to-Video (Runway) + Lip Sync (Sync Labs)
        """
        logger.info(f"🎬 TALKING_CHARACTER TOOL CALLED!")

        try:
            image_id = arguments.get('image_id')
            image_url = arguments.get('image_url')
            text = arguments.get('text')
            voice = arguments.get('voice', 'Rachel')
            duration = int(arguments.get('duration', 5))
            motion_prompt = arguments.get('motion_prompt', 'subtle talking motion, slight head movements')
            sync_mode = arguments.get('sync_mode', 'cut_off')
            temperature = float(arguments.get('temperature', 0.5))
            lipsync_model = arguments.get('lipsync_model', 'auto')  # Session 177: Model selection

            # Get current project - Session 179: Fixed to use self.project directly
            current_project = getattr(self, 'project', None)
            project_id = str(current_project.id) if current_project else arguments.get('project_id')

            # Validate inputs
            if not image_id and not image_url:
                return {'success': False, 'error': 'image_id or image_url is required - provide character image to animate'}

            if not text:
                return {'success': False, 'error': 'text is required - provide script for character to speak'}

            if duration not in [5, 10]:
                return {'success': False, 'error': 'duration must be 5 or 10 seconds'}

            logger.info(f"   Image ID: {image_id}")
            logger.info(f"   Text: {text[:50]}...")
            logger.info(f"   Voice: {voice}, Duration: {duration}s")
            logger.info(f"   Lip Sync Model: {lipsync_model}")  # Session 177

            # Create pipeline instance
            from content.talking_character_pipeline import get_talking_character_pipeline

            pipeline = get_talking_character_pipeline(user=self.user)

            # Show cost estimate
            cost_estimate = pipeline.estimate_cost(text, duration)
            logger.info(f"   💰 Estimated cost: ${cost_estimate['total_cost']:.3f}")

            # Resolve image URL from image_id if needed
            if not image_url and image_id:
                from content.models import ImageHistory
                try:
                    # Support hybrid ID (numeric or UUID)
                    if str(image_id).isdigit():
                        # Numeric ID - get nth image
                        images = ImageHistory.objects.filter(user=self.user).order_by('created_at')
                        numeric_id = int(image_id)
                        if numeric_id > 0 and numeric_id <= images.count():
                            image = images[numeric_id - 1]
                            # Get public URL from file_path
                            if image.file_path:
                                # file_path can be a data URI, HTTP URL, or local path
                                if image.file_path.startswith('http'):
                                    image_url = image.file_path
                                elif image.file_path.startswith('data:'):
                                    # Data URI - can't use for video generation
                                    return {
                                        'success': False,
                                        'error': f'Image {image_id} is a data URI - please use an uploaded image with a URL'
                                    }
                                else:
                                    # Local file path - convert to URL
                                    # Ensure path starts with / for proper URL construction
                                    path = image.file_path if image.file_path.startswith('/') else f"/{image.file_path}"
                                    image_url = f"http://localhost:8000{path}"
                        else:
                            return {
                                'success': False,
                                'error': f'Image {image_id} not found (you have {images.count()} images)'
                            }
                    else:
                        # UUID
                        image = ImageHistory.objects.get(id=image_id, user=self.user)
                        if image.file_path:
                            # file_path can be a data URI, HTTP URL, or local path
                            if image.file_path.startswith('http'):
                                image_url = image.file_path
                            elif image.file_path.startswith('data:'):
                                # Data URI - can't use for video generation
                                return {
                                    'success': False,
                                    'error': f'Image {image_id} is a data URI - please use an uploaded image with a URL'
                                }
                            else:
                                # Local file path - convert to URL
                                # Ensure path starts with / for proper URL construction
                                path = image.file_path if image.file_path.startswith('/') else f"/{image.file_path}"
                                image_url = f"http://localhost:8000{path}"
                except ImageHistory.DoesNotExist:
                    return {'success': False, 'error': f'Image {image_id} not found'}

            if not image_url:
                return {'success': False, 'error': 'Could not resolve image URL'}

            # Start async pipeline (returns task IDs for polling)
            # Session 177: Pass lipsync_model parameter for cartoon support
            result = pipeline.generate_talking_video_async(
                image_url=image_url,
                text=text,
                voice=voice,
                motion_prompt=motion_prompt,
                duration=duration,
                sync_mode=sync_mode,
                temperature=temperature,
                lipsync_model=lipsync_model,
                project_id=project_id
            )

            if not result.success:
                return {
                    'success': False,
                    'error': result.error_message,
                    'failed_stage': result.failed_stage
                }

            # Return pipeline status with task IDs for polling
            response = {
                'success': True,
                'status': result.status.value,
                'current_stage': result.current_stage,
                'progress_percent': result.progress_percent,
                'progress_message': result.progress_message,
                'estimated_cost': result.estimated_cost,
                'message': f"🎬 **Talking Character Pipeline Started!**\n\n" +
                          f"Your character is being brought to life with speech!\n\n" +
                          f"**Stage:** {result.current_stage}\n" +
                          f"**Progress:** {result.progress_percent}%\n" +
                          f"**Estimated Cost:** ${result.estimated_cost:.3f}\n\n" +
                          f"{result.progress_message}\n\n" +
                          f"The pipeline will automatically proceed through:\n" +
                          f"1. 🎤 Audio generation (ElevenLabs)\n" +
                          f"2. 🎬 Image animation (Runway)\n" +
                          f"3. 👄 Lip sync (Sync Labs)\n\n" +
                          f"I'll keep you updated as each stage completes!",
                'agent': 'TalkingCharacterAgent',
                'operation': 'talking_character',
                'operation_display': 'Creating talking character video'
            }

            # Add task IDs for polling
            if result.tts_task_id:
                response['tts_task_id'] = result.tts_task_id
            if result.video_task_id:
                response['video_task_id'] = result.video_task_id
                response['video_poll_endpoint'] = f'/api/video/status/{result.video_task_id}/'
            if result.lipsync_task_id:
                response['lipsync_task_id'] = result.lipsync_task_id
                response['lipsync_poll_endpoint'] = f'/api/video/lip-sync/status/{result.lipsync_task_id}/'

            # Add URLs when available
            if result.audio_url:
                response['audio_url'] = result.audio_url
            if result.base_video_url:
                response['base_video_url'] = result.base_video_url
            if result.final_video_url:
                response['final_video_url'] = result.final_video_url

            if project_id:
                response['project_id'] = project_id

            return response

        except Exception as e:
            logger.error(f"❌ Talking character tool error: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    # Session 184: Restored web_search handler from Session 65
    def _tool_generate_voice(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the generate_voice tool - Session 128."""
        logger.info(f"🎤 GENERATE_VOICE TOOL CALLED!")
        logger.info(f"🤖 Delegating to Audio Generation Agent...")

        try:
            text = arguments['text']
            voice = arguments.get('voice', 'Rachel')

            # Get current project if in session
            current_project = getattr(self, 'project', None)  # Session 179: Fixed project access

            # Session 128: Delegate to specialized Audio Generation Agent
            from core.agents import AudioAgent

            agent = AudioAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            # Execute agent workflow
            result = agent.execute(
                operation='generate_voice',
                text=text,
                voice=voice
            )

            return result

        except Exception as e:
            logger.error(f"❌ Generate voice tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    # Session 128: Updated to use Audio Generation Agent
    def _tool_add_voiceover(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the add_voiceover tool - Session 128."""
        logger.info(f"🎤 ADD_VOICEOVER TOOL CALLED!")
        logger.info(f"🤖 Delegating to Audio Generation Agent...")

        try:
            video_id = arguments['video_id']
            text = arguments['text']
            voice = arguments.get('voice', 'Rachel')

            # Get current project if in session
            current_project = getattr(self, 'project', None)  # Session 179: Fixed project access

            # Session 128: Delegate to specialized Audio Generation Agent
            from core.agents import AudioAgent

            agent = AudioAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            # Execute agent workflow
            result = agent.execute(
                operation='add_voiceover',
                text=text,
                voice=voice,
                video_id=video_id
            )

            return result

        except Exception as e:
            logger.error(f"❌ Add voiceover tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_animate_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the animate_image tool - Session 127 Part 2: Use VideoAgent directly!"""
        try:
            image_id = arguments['image_id']
            motion_prompt = arguments.get('motion_prompt', 'natural motion')
            duration = arguments.get('duration', 5)

            # Session 127 Part 2: Get project/session from self, not arguments!
            current_project = getattr(self, 'project', None)
            current_session = getattr(self, 'session', None)

            logger.info(f"🎬🎬🎬 ANIMATE_IMAGE TOOL CALLED! Image: {image_id}, Project: {current_project}, Session: {current_session}")

            # Session 127 Part 2: Use VideoAgent directly instead of views!
            from core.agents import VideoAgent
            video_agent = VideoAgent(self.user)

            result = video_agent.animate_image(
                image_id=image_id,
                motion_prompt=motion_prompt,
                duration=duration,
                project=current_project,  # Pass project context!
                session=current_session   # Pass session context!
            )

            if result.get('success'):
                return {
                    'success': True,
                    'task_id': result.get('task_id'),
                    'message': f"✅ Image animation started!\n\n" + \
                              f"Motion: {motion_prompt}\n" + \
                              f"Duration: {duration}s\n" + \
                              f"Task ID: {result.get('task_id')}\n\n" + \
                              f"The animated video will appear in the gallery in ~60 seconds."
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error_message', 'Image animation failed')
                }

        except Exception as e:
            logger.error(f"❌ Animate image tool error: {e}")
            return {'success': False, 'error': str(e)}

    def _tool_convert_to_3d(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the convert_to_3d tool - Session 127 Part 2."""
        try:
            image_id = arguments['image_id']

            # Get project/session from self
            current_project = getattr(self, 'project', None)

            logger.info(f"🎨 CONVERT_TO_3D TOOL CALLED! Image: {image_id}, Project: {current_project}")
            logger.info(f"🤖 Delegating to 3D Generation Agent...")

            # Session 128: Delegate to specialized 3D Generation Agent
            from core.agents import ThreeDAgent as ThreeDGenerationAgent

            agent = ThreeDGenerationAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else None
            )

            # Execute agent workflow
            result = agent.execute(
                image_id=image_id,
                style='toy',
                scale='medium'
            )

            if not result.get('success'):
                logger.error(f"❌ 3D Generation Agent failed: {result.get('error')}")
                return result

            # Associate minifig with current project
            if current_project and result.get('asset_id'):
                from content.models import MiniFigAsset
                try:
                    minifig = MiniFigAsset.objects.get(id=result['asset_id'])
                    minifig.project = current_project
                    minifig.save(update_fields=['project'])
                    logger.info(f"✅ Associated minifig {minifig.id} with project {current_project.id}")
                except MiniFigAsset.DoesNotExist:
                    logger.warning(f"⚠️ Could not associate minifig {result['asset_id']} with project")

            logger.info(f"✅ 3D Generation Agent completed successfully")
            logger.info(f"   Asset ID: {result.get('asset_id')}")
            logger.info(f"   Status: {result.get('status')}")

            return {
                'success': True,
                'minifig_id': result.get('asset_id'),
                'message': f"✅ 3D conversion started!\n\n" + \
                          f"Image #{image_id} is being converted to a 3D model.\n" + \
                          f"Generation time: ~45-60 seconds\n" + \
                          f"Asset ID: {result.get('asset_id')}\n\n" + \
                          f"The 3D model will appear in the project when complete. " + \
                          f"You'll be able to download the GLB file for 3D printing!"
            }

        except Exception as e:
            logger.error(f"❌ Convert to 3D tool error: {e}")
            return {'success': False, 'error': str(e)}

    # Session 128 Part 2: Updated to use Video Editing Agent
    def _tool_add_text_overlay(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the add_text_overlay tool - Session 128 Part 2."""
        logger.info(f"📝 ADD_TEXT_OVERLAY TOOL CALLED!")
        logger.info(f"🤖 Delegating to Video Editing Agent...")

        try:
            video_id = arguments['video_id']
            text = arguments['text']
            position = arguments.get('position', 'center')
            start_second = arguments.get('start_second', 0)
            duration = arguments.get('duration', 3)
            font_size = arguments.get('font_size', 72)

            # Get current project if in session
            current_project = getattr(self, 'project', None)  # Session 179: Fixed project access

            # Session 128 Part 2: Delegate to specialized Video Editing Agent
            from core.agents import VideoEditingAgent

            agent = VideoEditingAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            # Execute agent workflow
            result = agent.execute(
                operation='add_text_overlay',
                video_id=video_id,
                text=text,
                position=position,
                start_second=start_second,
                duration=duration,
                font_size=font_size
            )

            return result

        except Exception as e:
            logger.error(f"❌ Add text overlay tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    # Session 128 Part 2: Updated to use Video Editing Agent
    def _tool_apply_color_grading(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the apply_color_grading tool - Session 128 Part 2."""
        logger.info(f"🎨 APPLY_COLOR_GRADING TOOL CALLED!")
        logger.info(f"🤖 Delegating to Video Editing Agent...")

        try:
            video_id = arguments['video_id']
            style = arguments.get('style', 'cinematic_warm')

            # Get current project if in session
            current_project = getattr(self, 'project', None)  # Session 179: Fixed project access

            # Session 128 Part 2: Delegate to specialized Video Editing Agent
            from core.agents import VideoEditingAgent

            agent = VideoEditingAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            # Execute agent workflow
            result = agent.execute(
                operation='apply_color_grading',
                video_id=video_id,
                style=style
            )

            return result

        except Exception as e:
            logger.error(f"❌ Apply color grading tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_extract_video_frame(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the extract_video_frame tool - Session 159.
        Extracts a single frame from a video at a specified timestamp.
        Creates an image that can be used as a thumbnail or still.
        """
        logger.info(f"📸 EXTRACT_VIDEO_FRAME TOOL CALLED!")
        logger.info(f"📸 Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id = arguments.get('video_id')
            timestamp = arguments.get('timestamp', 0.0)
            output_format = arguments.get('format', 'jpg')
            project_id = arguments.get('project_id')

            if not video_id:
                return {'success': False, 'error': 'video_id is required'}

            # Create request using RequestFactory
            factory = RequestFactory()
            request_data = {
                'video_id': video_id,
                'timestamp': timestamp,
                'format': output_format,
                'project_id': project_id
            }

            request = factory.post('/api/video/extract-frame/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            # Call the backend view function
            from core.views_video import extract_video_frame
            response = extract_video_frame(request)
            result = json.loads(response.content)

            if result.get('success'):
                logger.info(f"✅ Frame extracted: image {result.get('image_id')} at {timestamp}s")
                return {
                    'success': True,
                    'message': result.get('message', f'Frame extracted at {timestamp}s successfully'),
                    'image_id': result.get('image_id'),
                    'image_url': result.get('image_url'),
                    'timestamp': timestamp,
                    'format': output_format,
                    'agent': 'VideoEditingAgent',
                    'operation': 'extract_frame',
                    'operation_display': f'Extracting frame at {timestamp}s'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Frame extraction failed')
                }

        except Exception as e:
            logger.error(f"❌ Extract video frame tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_reverse_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the reverse_video tool - Session 159.
        Reverses a video (plays backwards) with optional audio reversal.
        """
        logger.info(f"⏪ REVERSE_VIDEO TOOL CALLED!")
        logger.info(f"⏪ Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id = arguments.get('video_id')
            reverse_audio = arguments.get('reverse_audio', True)
            project_id = arguments.get('project_id')

            if not video_id:
                return {'success': False, 'error': 'video_id is required'}

            # Create request using RequestFactory
            factory = RequestFactory()
            request_data = {
                'video_id': video_id,
                'reverse_audio': reverse_audio,
                'project_id': project_id
            }

            request = factory.post('/api/video/reverse/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            # Call the backend view function
            from core.views_video import reverse_video
            response = reverse_video(request)
            result = json.loads(response.content)

            if result.get('success'):
                logger.info(f"✅ Video reversed: {result.get('video_id')}")
                return {
                    'success': True,
                    'message': result.get('message', 'Video reversed successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'reverse_audio': reverse_audio,
                    'agent': 'VideoEditingAgent',
                    'operation': 'reverse',
                    'operation_display': f'Reversing video' + (' with audio' if reverse_audio else ' (silent)')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Video reverse failed')
                }

        except Exception as e:
            logger.error(f"❌ Reverse video tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_trim_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the trim_video tool - Session 159.
        Trims a video to a specific time range.
        """
        logger.info(f"✂️ TRIM_VIDEO TOOL CALLED!")
        logger.info(f"✂️ Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id = arguments.get('video_id')
            start_time = arguments.get('start_time', 0)
            end_time = arguments.get('end_time')
            keep_audio = arguments.get('keep_audio', True)
            project_id = arguments.get('project_id')

            if not video_id:
                return {'success': False, 'error': 'video_id is required'}
            if end_time is None:
                return {'success': False, 'error': 'end_time is required'}

            # Create request using RequestFactory
            factory = RequestFactory()
            request_data = {
                'video_id': video_id,
                'start_time': start_time,
                'end_time': end_time,
                'keep_audio': keep_audio,
                'project_id': project_id
            }

            request = factory.post('/api/video/trim/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            # Call the backend view function
            from core.views_video import trim_video
            response = trim_video(request)
            result = json.loads(response.content)

            if result.get('success'):
                logger.info(f"✅ Video trimmed: {result.get('video_id')}")
                return {
                    'success': True,
                    'message': result.get('message', 'Video trimmed successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration': result.get('duration'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'trim',
                    'operation_display': f'Trimming video to {start_time}s-{end_time}s'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Video trim failed')
                }

        except Exception as e:
            logger.error(f"❌ Trim video tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_change_video_speed(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the change_video_speed tool - Session 160.
        Changes video playback speed (slow motion or speed up).
        """
        logger.info(f"⏩ CHANGE_VIDEO_SPEED TOOL CALLED!")
        logger.info(f"⏩ Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id = arguments.get('video_id')
            params = arguments.get('params', {})
            speed = params.get('speed', arguments.get('speed', 1.0))
            preserve_audio = params.get('preserve_audio', arguments.get('preserve_audio', True))
            project_id = arguments.get('project_id')

            if not video_id:
                return {'success': False, 'error': 'video_id is required'}

            # Create request using RequestFactory
            factory = RequestFactory()
            request_data = {
                'video_id': video_id,
                'speed': speed,
                'preserve_audio': preserve_audio,
                'project_id': project_id
            }

            request = factory.post('/api/video/speed/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            # Call the backend view function
            from core.views_video import change_video_speed
            response = change_video_speed(request)
            result = json.loads(response.content)

            if result.get('success'):
                speed_desc = "slow motion" if speed < 1.0 else "sped up" if speed > 1.0 else "normal"
                logger.info(f"✅ Video speed changed: {result.get('video_id')} ({speed}x {speed_desc})")
                return {
                    'success': True,
                    'message': result.get('message', f'Video speed changed to {speed}x'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'speed': speed,
                    'original_duration': result.get('original_duration'),
                    'new_duration': result.get('new_duration'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'speed_change',
                    'operation_display': f'Changing video speed to {speed}x ({speed_desc})'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Video speed change failed')
                }

        except Exception as e:
            logger.error(f"❌ Change video speed tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_concatenate_videos(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the concatenate_videos tool - Session 160.
        Combines multiple videos into one.
        """
        logger.info(f"🔗 CONCATENATE_VIDEOS TOOL CALLED!")
        logger.info(f"🔗 Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            params = arguments.get('params', {})
            video_ids = params.get('video_ids', arguments.get('video_ids', []))
            project_id = arguments.get('project_id')

            # Also try to parse video_id if video_ids not provided
            if not video_ids and arguments.get('video_id'):
                # Parse comma-separated or range format
                video_id_str = arguments.get('video_id', '')
                if ',' in video_id_str or '-' in video_id_str:
                    # Parse the batch format
                    video_ids = self._parse_video_id_range(video_id_str)
                else:
                    video_ids = [video_id_str]

            if not video_ids or len(video_ids) < 2:
                return {'success': False, 'error': 'At least 2 video_ids are required for concatenation'}

            # Create request using RequestFactory
            factory = RequestFactory()
            request_data = {
                'video_ids': video_ids,
                'project_id': project_id
            }

            request = factory.post('/api/video/concatenate/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            # Call the backend view function
            from core.views_video import concatenate_videos
            response = concatenate_videos(request)
            result = json.loads(response.content)

            if result.get('success'):
                logger.info(f"✅ Videos concatenated: {result.get('video_id')}")
                return {
                    'success': True,
                    'message': result.get('message', 'Videos concatenated successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'video_count': result.get('video_count'),
                    'total_duration': result.get('total_duration'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'concatenate',
                    'operation_display': f'Combining {result.get("video_count")} videos'
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', 'Video concatenation failed')
                }

        except Exception as e:
            logger.error(f"❌ Concatenate videos tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    # ==========================================================================
    # SESSION 161: Phase 2 Tool Handlers (5 new video editing features)
    # ==========================================================================

    def _tool_rotate_flip_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the rotate_flip_video tool - Session 161.
        Rotates or flips a video.
        """
        logger.info(f"🔄 ROTATE_FLIP_VIDEO TOOL CALLED!")
        logger.info(f"🔄 Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id = arguments.get('video_id')
            rotation = arguments.get('rotation', 90)
            project_id = arguments.get('project_id')

            factory = RequestFactory()
            request_data = {
                'video_id': video_id,
                'rotation': rotation,
                'project_id': project_id
            }

            request = factory.post('/api/video/rotate/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            from core.views_video import rotate_flip_video
            response = rotate_flip_video(request)
            result = json.loads(response.content)

            if result.get('success'):
                logger.info(f"✅ Video rotated: {result.get('video_id')}")
                return {
                    'success': True,
                    'message': result.get('message', 'Video rotated successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'rotation': result.get('rotation'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'rotate_flip',
                    'operation_display': f'Rotating video {result.get("rotation")}'
                }
            else:
                return {'success': False, 'error': result.get('error', 'Video rotation failed')}

        except Exception as e:
            logger.error(f"❌ Rotate/flip video tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_fade_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the fade_video tool - Session 161.
        Adds fade in/out effects to a video.
        """
        logger.info(f"🎬 FADE_VIDEO TOOL CALLED!")
        logger.info(f"🎬 Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id = arguments.get('video_id')
            fade_in = arguments.get('fade_in', 1.0)
            fade_out = arguments.get('fade_out', 1.0)
            fade_color = arguments.get('fade_color', 'black')
            project_id = arguments.get('project_id')

            factory = RequestFactory()
            request_data = {
                'video_id': video_id,
                'fade_in': fade_in,
                'fade_out': fade_out,
                'fade_color': fade_color,
                'project_id': project_id
            }

            request = factory.post('/api/video/fade/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            from core.views_video import fade_video
            response = fade_video(request)
            result = json.loads(response.content)

            if result.get('success'):
                logger.info(f"✅ Video faded: {result.get('video_id')}")
                return {
                    'success': True,
                    'message': result.get('message', 'Fade effects added successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'fade_in': result.get('fade_in'),
                    'fade_out': result.get('fade_out'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'fade',
                    'operation_display': f'Adding fade effects'
                }
            else:
                return {'success': False, 'error': result.get('error', 'Fade effect failed')}

        except Exception as e:
            logger.error(f"❌ Fade video tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_crop_resize_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the crop_resize_video tool - Session 161.
        Crops, resizes, or changes aspect ratio of a video.
        """
        logger.info(f"✂️ CROP_RESIZE_VIDEO TOOL CALLED!")
        logger.info(f"✂️ Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id = arguments.get('video_id')
            mode = arguments.get('mode', 'aspect')  # crop, resize, aspect
            width = arguments.get('width')
            height = arguments.get('height')
            crop_x = arguments.get('crop_x', 0)
            crop_y = arguments.get('crop_y', 0)
            crop_width = arguments.get('crop_width')
            crop_height = arguments.get('crop_height')
            aspect = arguments.get('aspect', '16:9')
            project_id = arguments.get('project_id')

            factory = RequestFactory()
            request_data = {
                'video_id': video_id,
                'mode': mode,
                'width': width,
                'height': height,
                'crop_x': crop_x,
                'crop_y': crop_y,
                'crop_width': crop_width,
                'crop_height': crop_height,
                'aspect': aspect,
                'project_id': project_id
            }

            request = factory.post('/api/video/crop/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            from core.views_video import crop_resize_video
            response = crop_resize_video(request)
            result = json.loads(response.content)

            if result.get('success'):
                logger.info(f"✅ Video cropped/resized: {result.get('video_id')}")
                return {
                    'success': True,
                    'message': result.get('message', 'Video cropped/resized successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'mode': result.get('mode'),
                    'new_ratio': result.get('new_ratio'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'crop_resize',
                    'operation_display': result.get('operation_display', 'Cropping/resizing video')
                }
            else:
                return {'success': False, 'error': result.get('error', 'Crop/resize failed')}

        except Exception as e:
            logger.error(f"❌ Crop/resize video tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_audio_controls(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the audio_controls tool - Session 161.
        Adjusts volume, mutes, or extracts audio from a video.
        """
        logger.info(f"🔊 AUDIO_CONTROLS TOOL CALLED!")
        logger.info(f"🔊 Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id = arguments.get('video_id')
            operation = arguments.get('audio_operation', 'volume')
            volume = arguments.get('volume', 1.0)
            output_format = arguments.get('output_format', 'mp3')
            project_id = arguments.get('project_id')

            factory = RequestFactory()
            request_data = {
                'video_id': video_id,
                'operation': operation,
                'volume': volume,
                'output_format': output_format,
                'project_id': project_id
            }

            request = factory.post('/api/video/audio/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            from core.views_video import audio_controls
            response = audio_controls(request)
            result = json.loads(response.content)

            if result.get('success'):
                logger.info(f"✅ Audio operation complete: {operation}")
                if operation == 'extract':
                    return {
                        'success': True,
                        'message': result.get('message', 'Audio extracted successfully'),
                        'audio_url': result.get('audio_url'),
                        'format': result.get('format'),
                        'source_video_id': result.get('source_video_id'),
                        'agent': 'VideoEditingAgent',
                        'operation': 'audio_extract',
                        'operation_display': f'Extracting audio as {result.get("format", "MP3").upper()}'
                    }
                else:
                    return {
                        'success': True,
                        'message': result.get('message', 'Audio operation completed'),
                        'video_id': result.get('video_id'),
                        'video_url': result.get('video_url'),
                        'agent': 'VideoEditingAgent',
                        'operation': f'audio_{operation}',
                        'operation_display': result.get('operation_display', f'Audio {operation}')
                    }
            else:
                return {'success': False, 'error': result.get('error', 'Audio operation failed')}

        except Exception as e:
            logger.error(f"❌ Audio controls tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_picture_in_picture(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the picture_in_picture tool - Session 161.
        Overlays one video on another.
        """
        logger.info(f"🖼️ PICTURE_IN_PICTURE TOOL CALLED!")
        logger.info(f"🖼️ Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            bg_video_id = arguments.get('video_id')  # Main video is the background
            overlay_video_id = arguments.get('overlay_video_id')
            position = arguments.get('position', 'bottom-right')
            scale = arguments.get('scale', 0.25)
            margin = arguments.get('margin', 10)
            opacity = arguments.get('opacity', 1.0)
            project_id = arguments.get('project_id')

            if not overlay_video_id:
                return {'success': False, 'error': 'overlay_video_id is required for picture-in-picture'}

            factory = RequestFactory()
            request_data = {
                'background_video_id': bg_video_id,
                'overlay_video_id': overlay_video_id,
                'position': position,
                'scale': scale,
                'margin': margin,
                'opacity': opacity,
                'project_id': project_id
            }

            request = factory.post('/api/video/pip/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            from core.views_video import picture_in_picture
            response = picture_in_picture(request)
            result = json.loads(response.content)

            if result.get('success'):
                logger.info(f"✅ PiP video created: {result.get('video_id')}")
                return {
                    'success': True,
                    'message': result.get('message', 'Picture-in-picture created successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'background_video': result.get('background_video'),
                    'overlay_video': result.get('overlay_video'),
                    'position': result.get('position'),
                    'scale': result.get('scale'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'picture_in_picture',
                    'operation_display': f'Creating PiP with overlay in {position}'
                }
            else:
                return {'success': False, 'error': result.get('error', 'Picture-in-picture failed')}

        except Exception as e:
            logger.error(f"❌ Picture-in-picture tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_add_watermark(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the add_watermark tool - Session 163 Phase 3.
        Adds an image (logo/watermark) overlay to video.
        """
        logger.info(f"🏷️ ADD_WATERMARK TOOL CALLED!")
        logger.info(f"🏷️ Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id = arguments.get('video_id')
            image_id = arguments.get('image_id')
            position = arguments.get('position', 'bottom_right')
            scale = arguments.get('scale', 0.15)
            opacity = arguments.get('opacity', 0.8)
            margin = arguments.get('margin', 20)
            project_id = arguments.get('project_id')

            if not image_id:
                return {'success': False, 'error': 'image_id is required for watermark (the logo/watermark image)'}

            factory = RequestFactory()
            request_data = {
                'video_id': video_id,
                'image_id': image_id,
                'position': position,
                'scale': scale,
                'opacity': opacity,
                'margin': margin,
                'project_id': project_id
            }

            request = factory.post('/api/video/watermark/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            from core.views_video import add_watermark
            response = add_watermark(request)
            result = json.loads(response.content)

            if result.get('success'):
                logger.info(f"✅ Watermarked video created: {result.get('video_id')}")
                return {
                    'success': True,
                    'message': result.get('message', 'Watermark added successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'watermark_image_id': result.get('watermark_image_id'),
                    'position': result.get('position'),
                    'scale': result.get('scale'),
                    'opacity': result.get('opacity'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'add_watermark',
                    'operation_display': f'Adding watermark at {position}'
                }
            else:
                return {'success': False, 'error': result.get('error', 'Watermark failed')}

        except Exception as e:
            logger.error(f"❌ Watermark tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_blur_region(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the blur_region tool - Session 163 Phase 3.
        Adds blur to a region of video for privacy/censoring.
        """
        logger.info(f"🔲 BLUR_REGION TOOL CALLED!")
        logger.info(f"🔲 Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id = arguments.get('video_id')
            region = arguments.get('region', 'center')
            blur_strength = arguments.get('blur_strength', 15)
            x = arguments.get('x', 0)
            y = arguments.get('y', 0)
            width = arguments.get('width')
            height = arguments.get('height')
            start_time = arguments.get('start_time')
            end_time = arguments.get('end_time')
            project_id = arguments.get('project_id')

            factory = RequestFactory()
            request_data = {
                'video_id': video_id,
                'region': region,
                'blur_strength': blur_strength,
                'x': x,
                'y': y,
                'project_id': project_id
            }
            if width:
                request_data['width'] = width
            if height:
                request_data['height'] = height
            if start_time is not None:
                request_data['start_time'] = start_time
            if end_time is not None:
                request_data['end_time'] = end_time

            request = factory.post('/api/video/blur/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            from core.views_video import blur_region
            response = blur_region(request)
            result = json.loads(response.content)

            if result.get('success'):
                logger.info(f"✅ Blurred video created: {result.get('video_id')}")
                return {
                    'success': True,
                    'message': result.get('message', 'Blur added successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'region': result.get('region'),
                    'blur_strength': result.get('blur_strength'),
                    'blur_area': result.get('blur_area'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'blur_region',
                    'operation_display': f'Adding blur at {region}'
                }
            else:
                return {'success': False, 'error': result.get('error', 'Blur failed')}

        except Exception as e:
            logger.error(f"❌ Blur region tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_stabilize_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the stabilize_video tool - Session 164 Phase 3.
        Stabilizes shaky video footage using ffmpeg's vidstab.
        """
        logger.info(f"📹 STABILIZE_VIDEO TOOL CALLED!")
        logger.info(f"📹 Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id = arguments.get('video_id')
            shakiness = arguments.get('shakiness', 5)
            accuracy = arguments.get('accuracy', 15)
            smoothing = arguments.get('smoothing', 10)
            crop = arguments.get('crop', 'keep')
            zoom = arguments.get('zoom', 0)
            project_id = arguments.get('project_id')

            factory = RequestFactory()
            request_data = {
                'video_id': video_id,
                'shakiness': shakiness,
                'accuracy': accuracy,
                'smoothing': smoothing,
                'crop': crop,
                'zoom': zoom,
                'project_id': project_id
            }

            request = factory.post('/api/video/stabilize/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            from core.views_video import stabilize_video
            response = stabilize_video(request)
            result = json.loads(response.content)

            if result.get('success'):
                logger.info(f"✅ Stabilized video created: {result.get('video_id')}")
                return {
                    'success': True,
                    'message': result.get('message', 'Video stabilized successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'shakiness': result.get('shakiness'),
                    'smoothing': result.get('smoothing'),
                    'crop': result.get('crop'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'stabilize_video',
                    'operation_display': 'Stabilizing shaky video'
                }
            else:
                return {'success': False, 'error': result.get('error', 'Stabilization failed')}

        except Exception as e:
            logger.error(f"❌ Stabilize video tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_add_text_animation(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the add_text_animation tool - Session 164 Phase 3.
        Adds animated text overlays to videos.
        """
        logger.info(f"📝 ADD_TEXT_ANIMATION TOOL CALLED!")
        logger.info(f"📝 Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id = arguments.get('video_id')
            text = arguments.get('text', 'Sample Text')
            animation = arguments.get('animation', 'static')
            position = arguments.get('position', 'bottom')
            font_size = arguments.get('font_size', 48)
            font_color = arguments.get('font_color', 'white')
            bg_color = arguments.get('bg_color')
            bg_opacity = arguments.get('bg_opacity', 0.5)
            start_time = arguments.get('start_time', 0)
            duration = arguments.get('duration')
            speed = arguments.get('speed', 100)
            project_id = arguments.get('project_id')

            factory = RequestFactory()
            request_data = {
                'video_id': video_id,
                'text': text,
                'animation': animation,
                'position': position,
                'font_size': font_size,
                'font_color': font_color,
                'bg_opacity': bg_opacity,
                'start_time': start_time,
                'speed': speed,
                'project_id': project_id
            }
            if bg_color:
                request_data['bg_color'] = bg_color
            if duration:
                request_data['duration'] = duration

            request = factory.post('/api/video/text-animation/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            from core.views_video import add_text_animation
            response = add_text_animation(request)
            result = json.loads(response.content)

            if result.get('success'):
                logger.info(f"✅ Text animated video created: {result.get('video_id')}")
                return {
                    'success': True,
                    'message': result.get('message', 'Text animation added successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'text': result.get('text'),
                    'animation': result.get('animation'),
                    'position': result.get('position'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'add_text_animation',
                    'operation_display': f'Adding {animation} text animation'
                }
            else:
                return {'success': False, 'error': result.get('error', 'Text animation failed')}

        except Exception as e:
            logger.error(f"❌ Text animation tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_chroma_key(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the chroma_key tool - Session 165 Phase 3.
        Removes green/blue screen backgrounds and optionally replaces with another background.
        """
        logger.info(f"💚 CHROMA_KEY TOOL CALLED!")
        logger.info(f"💚 Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id = arguments.get('video_id')
            key_color = arguments.get('key_color', 'green')
            similarity = arguments.get('similarity', 0.3)
            blend = arguments.get('blend', 0.1)
            background_video_id = arguments.get('background_video_id')
            background_image_id = arguments.get('background_image_id')
            background_color = arguments.get('background_color')
            project_id = arguments.get('project_id')

            factory = RequestFactory()
            request_data = {
                'video_id': video_id,
                'key_color': key_color,
                'similarity': similarity,
                'blend': blend,
                'project_id': project_id
            }
            if background_video_id:
                request_data['background_video_id'] = background_video_id
            if background_image_id:
                request_data['background_image_id'] = background_image_id
            if background_color:
                request_data['background_color'] = background_color

            request = factory.post('/api/video/chroma-key/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            from core.views_video import chroma_key
            response = chroma_key(request)
            result = json.loads(response.content)

            if result.get('success'):
                logger.info(f"✅ Chroma keyed video created: {result.get('video_id')}")
                return {
                    'success': True,
                    'message': result.get('message', 'Chroma key applied successfully'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'key_color': result.get('key_color'),
                    'background': result.get('background'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'chroma_key',
                    'operation_display': f'Removing {key_color} screen background'
                }
            else:
                return {'success': False, 'error': result.get('error', 'Chroma key failed')}

        except Exception as e:
            logger.error(f"❌ Chroma key tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_export_for_platform(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the export_for_platform tool - Session 166.
        Exports video optimized for YouTube, TikTok, Instagram, etc.
        """
        logger.info(f"📤 EXPORT_FOR_PLATFORM TOOL CALLED!")
        logger.info(f"📤 Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id = arguments.get('video_id')
            platform = arguments.get('platform', 'youtube')
            quality = arguments.get('quality', 'high')
            max_duration = arguments.get('max_duration')
            project_id = arguments.get('project_id')

            factory = RequestFactory()
            request_data = {
                'video_id': video_id,
                'platform': platform,
                'quality': quality,
                'project_id': project_id
            }
            if max_duration:
                request_data['max_duration'] = max_duration

            request = factory.post('/api/video/export/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            from core.views_video import export_for_platform
            response = export_for_platform(request)
            result = json.loads(response.content)

            if result.get('success'):
                logger.info(f"✅ Video exported for {platform}: {result.get('video_id')}")
                return {
                    'success': True,
                    'message': result.get('message', f'Video exported for {platform}'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'platform': result.get('platform'),
                    'preset': result.get('preset'),
                    'resolution': result.get('resolution'),
                    'file_size_mb': result.get('file_size_mb'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'export_for_platform',
                    'operation_display': f'Exporting for {platform}'
                }
            else:
                return {'success': False, 'error': result.get('error', 'Export failed')}

        except Exception as e:
            logger.error(f"❌ Export for platform tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_video_transition(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the video_transition tool - Session 166.
        Adds transition effects (crossfade, wipe, slide, etc.) between two videos.
        """
        logger.info(f"🔄 VIDEO_TRANSITION TOOL CALLED!")
        logger.info(f"🔄 Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id_1 = arguments.get('video_id_1') or arguments.get('video_id')
            video_id_2 = arguments.get('video_id_2')
            transition = arguments.get('transition', 'fade')
            duration = arguments.get('duration', 1.0)
            project_id = arguments.get('project_id')

            factory = RequestFactory()
            request_data = {
                'video_id_1': video_id_1,
                'video_id_2': video_id_2,
                'transition': transition,
                'duration': duration,
                'project_id': project_id
            }

            request = factory.post('/api/video/transition/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            from core.views_video import video_transition
            response = video_transition(request)
            result = json.loads(response.content)

            if result.get('success'):
                logger.info(f"✅ Transition video created: {result.get('video_id')}")
                return {
                    'success': True,
                    'message': result.get('message', f'{transition} transition added'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'transition': result.get('transition'),
                    'duration': result.get('duration'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'video_transition',
                    'operation_display': f'Adding {transition} transition'
                }
            else:
                return {'success': False, 'error': result.get('error', 'Transition failed')}

        except Exception as e:
            logger.error(f"❌ Video transition tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_auto_caption(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the auto_caption tool - Session 166.
        Extracts audio, transcribes with Whisper, and burns subtitles into video.
        """
        logger.info(f"📝 AUTO_CAPTION TOOL CALLED!")
        logger.info(f"📝 Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id = arguments.get('video_id')
            language = arguments.get('language', 'auto')
            font_size = arguments.get('font_size', 24)
            font_color = arguments.get('font_color', 'white')
            background_color = arguments.get('background_color', 'black@0.5')
            position = arguments.get('position', 'bottom')
            project_id = arguments.get('project_id')

            factory = RequestFactory()
            request_data = {
                'video_id': video_id,
                'language': language,
                'font_size': font_size,
                'font_color': font_color,
                'background_color': background_color,
                'position': position,
                'project_id': project_id
            }

            request = factory.post('/api/video/caption/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            from core.views_video import auto_caption
            response = auto_caption(request)
            result = json.loads(response.content)

            if result.get('success'):
                logger.info(f"✅ Captioned video created: {result.get('video_id')}")
                return {
                    'success': True,
                    'message': result.get('message', 'Auto-captioning complete'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'subtitle_file': result.get('subtitle_file'),
                    'transcript': result.get('transcript'),
                    'word_count': result.get('word_count'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'auto_caption',
                    'operation_display': 'Auto-captioning video'
                }
            else:
                return {'success': False, 'error': result.get('error', 'Auto-captioning failed')}

        except Exception as e:
            logger.error(f"❌ Auto-caption tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_render_professional(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 167: Professional render with DaVinci Resolve or ffmpeg.
        Supports ProRes, DNxHD, and other professional codecs.
        Uses GPU acceleration when DaVinci is running!
        """
        logger.info(f"🎬 RENDER_PROFESSIONAL TOOL CALLED!")
        logger.info(f"🎬 Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id = arguments.get('video_id')
            codec = arguments.get('codec', 'prores_422_hq')
            resolution = arguments.get('resolution', '1920x1080')
            frame_rate = arguments.get('frame_rate', 30)
            project_id = arguments.get('project_id')

            factory = RequestFactory()
            request_data = {
                'video_id': video_id,
                'codec': codec,
                'resolution': resolution,
                'frame_rate': frame_rate,
                'project_id': project_id
            }

            request = factory.post('/api/video/render-professional/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            from core.views_video import render_professional
            response = render_professional(request)
            result = json.loads(response.content)

            if result.get('success'):
                gpu_msg = ' (GPU accelerated!)' if result.get('gpu_accelerated') else ''
                logger.info(f"✅ Professional render complete: {result.get('video_id')}{gpu_msg}")
                return {
                    'success': True,
                    'message': result.get('message', f'Professional {codec} render complete'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'codec': result.get('codec'),
                    'processor_used': result.get('processor_used'),
                    'gpu_accelerated': result.get('gpu_accelerated'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'render_professional',
                    'operation_display': f'Professional {codec} render'
                }
            else:
                return {'success': False, 'error': result.get('error', 'Professional render failed')}

        except Exception as e:
            logger.error(f"❌ Render professional tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_apply_lut(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 167: Apply LUT (Look-Up Table) to video.
        Uses DaVinci's color science when available!
        """
        logger.info(f"🎨 APPLY_LUT TOOL CALLED!")
        logger.info(f"🎨 Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id = arguments.get('video_id')
            lut_name = arguments.get('lut_name', 'cinematic_orange_teal')
            lut_path = arguments.get('lut_path')
            intensity = arguments.get('intensity', 1.0)
            project_id = arguments.get('project_id')

            factory = RequestFactory()
            request_data = {
                'video_id': video_id,
                'lut_name': lut_name,
                'lut_path': lut_path,
                'intensity': intensity,
                'project_id': project_id
            }

            request = factory.post('/api/video/apply-lut/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            from core.views_video import apply_lut
            response = apply_lut(request)
            result = json.loads(response.content)

            if result.get('success'):
                logger.info(f"✅ LUT applied: {result.get('lut_applied')}")
                return {
                    'success': True,
                    'message': result.get('message', f'Applied {lut_name} LUT'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'lut_applied': result.get('lut_applied'),
                    'processor_used': result.get('processor_used'),
                    'gpu_accelerated': result.get('gpu_accelerated'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'apply_lut',
                    'operation_display': f'Applying {lut_name} LUT'
                }
            else:
                return {'success': False, 'error': result.get('error', 'LUT application failed')}

        except Exception as e:
            logger.error(f"❌ Apply LUT tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _tool_color_grade_professional(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 167: Professional color grading using DaVinci's color science.
        DaVinci Resolve is THE industry standard for color grading!
        """
        logger.info(f"🎨 COLOR_GRADE_PROFESSIONAL TOOL CALLED!")
        logger.info(f"🎨 Arguments: {arguments}")

        try:
            from django.test import RequestFactory
            import json

            video_id = arguments.get('video_id')
            grade_type = arguments.get('grade_type', 'cinematic')
            saturation = arguments.get('saturation', 1.0)
            contrast = arguments.get('contrast', 1.0)
            lift = arguments.get('lift')
            gamma = arguments.get('gamma')
            gain = arguments.get('gain')
            project_id = arguments.get('project_id')

            factory = RequestFactory()
            request_data = {
                'video_id': video_id,
                'grade_type': grade_type,
                'saturation': saturation,
                'contrast': contrast,
                'lift': lift,
                'gamma': gamma,
                'gain': gain,
                'project_id': project_id
            }

            request = factory.post('/api/video/grade-professional/',
                                   data=json.dumps(request_data),
                                   content_type='application/json')
            request.user = self.user

            from core.views_video import color_grade_professional
            response = color_grade_professional(request)
            result = json.loads(response.content)

            if result.get('success'):
                gpu_msg = ' (GPU accelerated!)' if result.get('gpu_accelerated') else ''
                logger.info(f"✅ Professional grade complete: {grade_type}{gpu_msg}")
                return {
                    'success': True,
                    'message': result.get('message', f'Professional {grade_type} grade complete'),
                    'video_id': result.get('video_id'),
                    'video_url': result.get('video_url'),
                    'grade_type': result.get('grade_type'),
                    'processor_used': result.get('processor_used'),
                    'gpu_accelerated': result.get('gpu_accelerated'),
                    'agent': 'VideoEditingAgent',
                    'operation': 'color_grade_professional',
                    'operation_display': f'Professional {grade_type} grading'
                }
            else:
                return {'success': False, 'error': result.get('error', 'Professional grading failed')}

        except Exception as e:
            logger.error(f"❌ Color grade professional tool error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

