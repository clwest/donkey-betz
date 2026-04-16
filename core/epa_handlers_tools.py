"""
EnhancedPersonalAIAssistant EPAToolHandlersMixin — extracted handler methods.
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




class EPAToolHandlersMixin:
    """Mixin providing handler methods for EnhancedPersonalAIAssistant."""

    def _handle_image_generation_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle image_generation_agent calls - routes to appropriate Creation Agent (Session 134)."""
        prompt = arguments.get('prompt')
        params = arguments.get('params', {})
        project_id = arguments.get('project_id')
        character_model_name = arguments.get('character_model_name')  # Session 134: LoRA model name

        # Session 134: Route to appropriate agent based on whether trained model is requested
        if character_model_name:
            logger.info(f"🎨 Routing to Trained Creation Agent: '{character_model_name}'")
            logger.info(f"   User: {self.user.username} (ID: {self.user.id})")
            return self._handle_trained_creation_agent(prompt, character_model_name, params, project_id)
        else:
            logger.info(f"🖼️ Routing to Creation Agent (standard Stability AI)")
            logger.info(f"   User: {self.user.username} (ID: {self.user.id})")
            return self._handle_creation_agent(prompt, params, project_id)

    def _handle_creation_agent(self, prompt: str, params: Dict[str, Any], project_id: str) -> Dict[str, Any]:
        """Handle standard image generation via CreationAgent (Session 134)."""
        logger.info(f"🖼️ Creation Agent: prompt='{prompt[:50]}...'")

        # Extract parameters with defaults
        width = params.get('width', 1024)
        height = params.get('height', 1024)
        count = params.get('count', 1)
        style = params.get('style', 'photorealistic')

        # Session 353: Use SD3 (high quality) for logos - it's the best model for logo generation
        prompt_lower = prompt.lower()
        is_logo_request = any(word in prompt_lower for word in ['logo', 'logos', 'brand mark', 'wordmark', 'emblem', 'icon'])
        quality = params.get('quality', 'high' if is_logo_request else 'balanced')

        if is_logo_request:
            logger.info(f"🎨 Detected logo request - using SD3 (high quality) for best results")

        # Session 353: Enrich prompt with project research context if available
        enriched_prompt = prompt
        if project_id:
            # Session 517: Validate UUID format before lookup
            import uuid
            try:
                uuid.UUID(str(project_id))  # Validate UUID format
            except (ValueError, AttributeError):
                logger.info(f"⚠️ Invalid project_id format '{project_id}', skipping project context")
                project_id = None  # Reset to skip project lookup

        if project_id:
            try:
                from core.models_partnership import PartnershipProject
                project = PartnershipProject.objects.get(id=project_id)

                # Build context from research
                context_parts = []

                # Project name for branding
                if project.project_name:
                    context_parts.append(f"for '{project.project_name}'")

                # Get brand strategy from research summaries
                if project.metadata:
                    research_summaries = project.metadata.get('research_summaries', [])

                    # Find brand strategy
                    brand_strategy = next(
                        (r for r in research_summaries if r.get('type') == 'brand_strategy'),
                        None
                    )
                    if brand_strategy:
                        summary = brand_strategy.get('summary', '')
                        # Extract key brand attributes
                        if 'color' in summary.lower():
                            # Try to extract color mentions
                            import re
                            colors = re.findall(r'\b(blue|red|green|yellow|orange|purple|pink|black|white|gold|silver|navy|teal|coral)\b', summary.lower())
                            if colors:
                                context_parts.append(f"brand colors: {', '.join(set(colors[:3]))}")

                        # Look for style/personality keywords
                        style_keywords = ['modern', 'minimalist', 'bold', 'professional', 'playful',
                                        'elegant', 'luxury', 'tech', 'innovative', 'creative', 'friendly']
                        found_styles = [kw for kw in style_keywords if kw in summary.lower()]
                        if found_styles:
                            context_parts.append(f"style: {', '.join(found_styles[:3])}")

                    # Find competitor analysis for industry context
                    competitor = next(
                        (r for r in research_summaries if r.get('type') == 'competitor_analysis'),
                        None
                    )
                    if competitor:
                        summary = competitor.get('summary', '')
                        # Extract industry mentions
                        industries = ['tech', 'fintech', 'healthcare', 'ecommerce', 'saas', 'food',
                                    'fashion', 'fitness', 'education', 'real estate', 'travel']
                        found_industries = [ind for ind in industries if ind in summary.lower()]
                        if found_industries:
                            context_parts.append(f"industry: {found_industries[0]}")

                # Enrich the prompt if we have context
                if context_parts:
                    enriched_prompt = f"{prompt} ({', '.join(context_parts)})"
                    logger.info(f"🎨 Enriched prompt with project context: {enriched_prompt[:100]}...")

            except Exception as e:
                logger.warning(f"Failed to enrich prompt with project context: {e}")

        try:
            from core.agents.creation_agent import CreationAgent

            # Initialize agent
            agent = CreationAgent(user=self.user, project_id=project_id)

            # Execute generation with enriched prompt (Session 353)
            from core.services.priority.enforce import check_priority, log_decision  # Session 1086 PR 3c
            _pd = check_priority('CreationAgent', trigger_source='user_chat'); log_decision(_pd, 'CreationAgent')
            result = agent.execute(
                prompt=enriched_prompt,
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
                error_msg = result.get('error', 'Image generation failed')
                logger.error(f"❌ Creation Agent failed: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }

        except Exception as e:
            logger.error(f"❌ Creation Agent error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to generate image: {str(e)}"
            }

    def _handle_trained_creation_agent(
        self,
        prompt: str,
        character_model_name: str,
        params: Dict[str, Any],
        project_id: str
    ) -> Dict[str, Any]:
        """Handle LoRA-based image generation via TrainedCreationAgent (Session 134)."""
        logger.info(f"🎨 Trained Creation Agent: model='{character_model_name}'")
        logger.info(f"   Prompt: '{prompt[:50]}...'")

        # Extract parameters with defaults
        width = params.get('width', 1024)
        height = params.get('height', 1024)
        count = params.get('count', 1)
        lora_scale = params.get('lora_scale', 0.8)

        try:
            from core.agents.training import TrainedCreationAgent

            # Initialize agent
            agent = TrainedCreationAgent(user=self.user, project_id=project_id)

            # Execute generation with LoRA
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
                error_msg = result.get('error', 'Trained image generation failed')
                logger.error(f"❌ Trained Creation Agent failed: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg
                }

        except Exception as e:
            logger.error(f"❌ Trained Creation Agent error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to generate image with trained model: {str(e)}"
            }

    def _handle_image_editing_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle image_editing_agent calls - routes to specific operation (Session 152: Batch support!)."""
        operation = arguments.get('operation')
        image_id = arguments.get('image_id')
        params = arguments.get('params', {})
        project_id = arguments.get('project_id')

        logger.info(f"🎨 Image Editing Agent: operation={operation}, image_id={image_id}")

        # Session 152: Check if this is a batch operation (range or list)
        # Check for comma (list) OR numeric range pattern (e.g., "1-3", "10-20")
        is_batch = ',' in image_id

        if not is_batch and '-' in image_id:
            # Check if it's a numeric range (not a UUID)
            # Simple heuristic: if removing dashes leaves only digits (or whitespace+digits), it's a range
            cleaned = image_id.replace('-', '').replace(' ', '')
            is_batch = cleaned.isdigit()  # "1-3" → "13" → True, UUID → has letters → False

        if is_batch:
            # Batch operation - parse range and process each ID
            try:
                image_ids = self._parse_id_range(image_id)
            except ValueError as e:
                return {'success': False, 'error': f"Invalid ID range: {str(e)}"}

            logger.info(f"⚡ Batch operation: {operation} on {len(image_ids)} images")

            # Process each image
            results = []
            successes = []
            failures = []

            for idx, img_id in enumerate(image_ids, 1):
                try:
                    # Resolve hybrid ID to UUID
                    resolved_id = self._resolve_hybrid_image_id(img_id)

                    # Build arguments for this specific image
                    tool_args = {'image_id': resolved_id, 'project_id': project_id}
                    tool_args.update(params)

                    # Execute operation
                    logger.info(f"  [{idx}/{len(image_ids)}] Processing image {img_id}...")
                    result = self._execute_single_image_operation(operation, tool_args)

                    if result.get('success'):
                        successes.append({'id': img_id, 'result': result})
                    else:
                        failures.append({'id': img_id, 'error': result.get('error', 'Unknown error')})

                    results.append(result)

                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"  ❌ Failed to process image {img_id}: {error_msg}")
                    failures.append({'id': img_id, 'error': error_msg})
                    results.append({'success': False, 'error': error_msg})

            # Return batch summary
            total = len(image_ids)
            success_count = len(successes)
            failure_count = len(failures)

            summary = f"Batch {operation} complete: {success_count}/{total} succeeded"
            if failure_count > 0:
                summary += f", {failure_count} failed"

            return {
                'success': failure_count == 0,  # Success only if ALL succeeded
                'message': summary,
                'batch': True,
                'total': total,
                'successes': success_count,
                'failures': failure_count,
                'results': results,
                'details': {
                    'successful_ids': [s['id'] for s in successes],
                    'failed_ids': [f['id'] for f in failures],
                    'errors': [f['error'] for f in failures] if failures else []
                }
            }
        else:
            # Single image operation (existing logic)
            try:
                image_id = self._resolve_hybrid_image_id(image_id)
            except ValueError as e:
                return {'success': False, 'error': str(e)}

            # Build arguments for the specific tool handler
            tool_args = {'image_id': image_id, 'project_id': project_id}
            tool_args.update(params)

            # Execute operation
            return self._execute_single_image_operation(operation, tool_args)

    def _handle_video_generation_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle video_generation_agent calls - routes to specific operation."""
        operation = arguments.get('operation')
        params = arguments.get('params', {})
        project_id = arguments.get('project_id')

        logger.info(f"🎬 Video Generation Agent: operation={operation}")

        # Build arguments for the specific tool handler
        tool_args = {'project_id': project_id}
        tool_args.update(params)  # Merge operation-specific params

        # Route to appropriate existing tool handler
        if operation == 'generate':
            return self._tool_generate_video(tool_args)
        elif operation == 'animate':
            return self._tool_animate_image(tool_args)
        elif operation == 'extend':
            return self._tool_extend_video(tool_args)
        elif operation == 'chain':
            return self._tool_chain_videos(tool_args)
        elif operation == 'lip_sync':
            # Session 175: Lip sync for talking characters
            return self._tool_lip_sync(tool_args)
        else:
            return {'success': False, 'error': f"Unknown video operation: {operation}"}

    def _handle_audio_generation_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle audio_generation_agent calls - routes to specific operation."""
        operation = arguments.get('operation')
        params = arguments.get('params', {})
        project_id = arguments.get('project_id')

        logger.info(f"🎤 Audio Generation Agent: operation={operation}")

        # Build arguments for the specific tool handler
        tool_args = {'project_id': project_id}
        tool_args.update(params)  # Merge operation-specific params

        # Route to appropriate existing tool handler
        if operation == 'generate_voice':
            return self._tool_generate_voice(tool_args)
        elif operation == 'add_voiceover':
            return self._tool_add_voiceover(tool_args)
        else:
            return {'success': False, 'error': f"Unknown audio operation: {operation}"}

    def _handle_three_d_generation_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle three_d_generation_agent calls - routes to convert operation."""
        operation = arguments.get('operation')
        image_id = arguments.get('image_id')
        project_id = arguments.get('project_id')

        logger.info(f"🤖 3D Generation Agent: operation={operation}, image_id={image_id}")

        # Route to convert_to_3d handler
        if operation == 'convert':
            return self._tool_convert_to_3d({'image_id': image_id, 'project_id': project_id})
        else:
            return {'success': False, 'error': f"Unknown 3D operation: {operation}"}

    def _handle_video_editing_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle video_editing_agent calls - routes to specific operation.
        Session 154: Added upscale and apply_effect operations with batch support.
        """
        operation = arguments.get('operation')
        video_id = arguments.get('video_id')
        params = arguments.get('params', {})
        project_id = arguments.get('project_id')

        logger.info(f"✂️ Video Editing Agent: operation={operation}, video_id={video_id}")

        # Session 154: Check if this is a batch operation
        is_batch = False
        if isinstance(video_id, str):
            is_batch = ',' in video_id
            if not is_batch and '-' in video_id:
                # Could be a range like "1-3" or a UUID with dashes
                # Check if it's a numeric range
                cleaned = video_id.replace('-', '').replace(' ', '')
                if cleaned.isdigit():
                    is_batch = True

        # Session 154/166: Handle batch operations for ALL single-video operations
        # Session 166: Expanded from just upscale/apply_effect to support all video operations
        batch_supported_operations = [
            'upscale', 'apply_effect', 'extract_frame', 'reverse', 'trim', 'speed_change',
            'rotate_flip', 'fade', 'crop_resize', 'audio_control', 'add_watermark',
            'blur_region', 'stabilize_video', 'add_text_animation', 'chroma_key',
            'export_for_platform', 'auto_caption',
            # Session 167: DaVinci Resolve operations
            'render_professional', 'apply_lut', 'color_grade_professional'
        ]

        if is_batch and operation in batch_supported_operations:
            video_ids = self._parse_id_range(video_id)
            logger.info(f"🎬 [Session 166] Batch video editing: {len(video_ids)} videos, operation={operation}")

            results = []
            successes = 0
            failures = 0

            for vid_id in video_ids:
                try:
                    # Session 166: Generic batch execution for all operations
                    result = self._execute_single_batch_video_operation(operation, vid_id, params, project_id)
                    results.append(result)
                    if result.get('success'):
                        successes += 1
                    else:
                        failures += 1
                except Exception as e:
                    logger.error(f"❌ Error processing video {vid_id}: {e}")
                    results.append({
                        'success': False,
                        'video_id': vid_id,
                        'error': str(e)
                    })
                    failures += 1

            # Return batch summary with properly formatted message
            # Session 166: Expanded operation names dictionary
            operation_names = {
                'upscale': 'upscaling',
                'apply_effect': 'effect application',
                'extract_frame': 'frame extraction',
                'reverse': 'reversal',
                'trim': 'trimming',
                'speed_change': 'speed adjustment',
                'rotate_flip': 'rotation/flip',
                'fade': 'fade effect',
                'crop_resize': 'crop/resize',
                'audio_control': 'audio adjustment',
                'add_watermark': 'watermark',
                'blur_region': 'blur effect',
                'stabilize_video': 'stabilization',
                'add_text_animation': 'text animation',
                'chroma_key': 'green screen removal',
                'export_for_platform': 'platform export',
                'auto_caption': 'auto-captioning',
                # Session 167: DaVinci Resolve operations
                'render_professional': 'professional rendering',
                'apply_lut': 'LUT application',
                'color_grade_professional': 'professional color grading'
            }
            op_name = operation_names.get(operation, operation)

            if successes == len(video_ids):
                message = f"✅ Batch {op_name} complete! All {successes} videos processed successfully."
            elif successes > 0:
                message = f"⚠️ Batch {op_name} partially complete: {successes}/{len(video_ids)} videos succeeded, {failures} failed."
            else:
                message = f"❌ Batch {op_name} failed: All {failures} videos failed to process."

            return {
                'success': successes > 0,
                'message': message,
                'batch': True,
                'total': len(video_ids),
                'successes': successes,
                'failures': failures,
                'video_ids': [r.get('video_id') for r in results if r.get('success')],
                'results': results,
                # Session 155: Add agent metadata for batch operations
                'agent': 'VideoEditingAgent',
                'operation': operation,
                'operation_display': f"Batch {op_name} ({len(video_ids)} videos)"
            }

        # Single video operation
        # Build arguments for the specific tool handler
        tool_args = {'video_id': video_id, 'project_id': project_id}
        tool_args.update(params)  # Merge operation-specific params

        # Route to appropriate tool handler
        if operation == 'add_text_overlay':
            return self._tool_add_text_overlay(tool_args)
        elif operation == 'apply_color_grading':
            return self._tool_apply_color_grading(tool_args)
        elif operation == 'upscale':
            # Session 154: ffmpeg upscaling
            return self._execute_single_video_enhancement(operation, video_id, params, project_id)
        elif operation == 'apply_effect':
            # Session 154: ffmpeg color grading effects
            return self._execute_single_video_enhancement(operation, video_id, params, project_id)
        elif operation == 'extract_frame':
            # Session 159: Frame extraction
            return self._tool_extract_video_frame(tool_args)
        elif operation == 'reverse':
            # Session 159: Video reverse
            return self._tool_reverse_video(tool_args)
        elif operation == 'trim':
            # Session 159: Video trim
            return self._tool_trim_video(tool_args)
        elif operation == 'speed_change':
            # Session 160: Speed control
            return self._tool_change_video_speed(tool_args)
        elif operation == 'concatenate':
            # Session 160: Video concatenation
            return self._tool_concatenate_videos(tool_args)
        elif operation == 'rotate_flip':
            # Session 161: Video rotation/flip
            return self._tool_rotate_flip_video(tool_args)
        elif operation == 'fade':
            # Session 161: Video fade in/out
            return self._tool_fade_video(tool_args)
        elif operation == 'crop_resize':
            # Session 161: Video crop/resize/aspect
            return self._tool_crop_resize_video(tool_args)
        elif operation == 'audio_control':
            # Session 161: Audio controls (volume/mute/extract)
            return self._tool_audio_controls(tool_args)
        elif operation == 'picture_in_picture':
            # Session 161: Picture-in-picture overlay
            return self._tool_picture_in_picture(tool_args)
        elif operation == 'add_watermark':
            # Session 163: Phase 3 - Watermark/logo overlay
            return self._tool_add_watermark(tool_args)
        elif operation == 'blur_region':
            # Session 163: Phase 3 - Blur region for privacy
            return self._tool_blur_region(tool_args)
        elif operation == 'stabilize_video':
            # Session 164: Phase 3 - Video Stabilization
            return self._tool_stabilize_video(tool_args)
        elif operation == 'add_text_animation':
            # Session 164: Phase 3 - Text Animations
            return self._tool_add_text_animation(tool_args)
        elif operation == 'chroma_key':
            # Session 165: Phase 3 - Green Screen / Chroma Key
            return self._tool_chroma_key(tool_args)
        elif operation == 'export_for_platform':
            # Session 166: Export Presets
            return self._tool_export_for_platform(tool_args)
        elif operation == 'video_transition':
            # Session 166: Video Transitions
            return self._tool_video_transition(tool_args)
        elif operation == 'auto_caption':
            # Session 166: Auto-Captioning (Whisper)
            return self._tool_auto_caption(tool_args)
        elif operation == 'render_professional':
            # Session 167: DaVinci/ffmpeg Professional Rendering
            return self._tool_render_professional(tool_args)
        elif operation == 'apply_lut':
            # Session 167: LUT Application
            return self._tool_apply_lut(tool_args)
        elif operation == 'color_grade_professional':
            # Session 167: DaVinci Professional Color Grading
            return self._tool_color_grade_professional(tool_args)
        else:
            return {'success': False, 'error': f"Unknown video editing operation: {operation}"}

    def _handle_character_training_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle character_training_agent calls - trains FLUX LoRA models (Session 133)."""
        image_ids = arguments.get('image_ids', [])
        style_name = arguments.get('style_name')
        trigger_word = arguments.get('trigger_word', style_name.upper().replace('-', ''))
        project_id = arguments.get('project_id')

        logger.info(f"🎨 Character Training Agent: {len(image_ids)} images → '{style_name}'")
        logger.info(f"   Trigger word: {trigger_word}")
        logger.info(f"   User: {self.user.username} (ID: {self.user.id})")

        try:
            # Convert hybrid IDs (numbers or UUIDs) to UUIDs
            from content.models import ImageHistory, CharacterModel
            import uuid as uuid_module

            resolved_images = []
            for img_id in image_ids:
                try:
                    # Try UUID first
                    uuid_obj = uuid_module.UUID(img_id)
                    # Get image if it exists and belongs to user
                    img = ImageHistory.objects.filter(id=uuid_obj, user=self.user).first()
                    if img:
                        resolved_images.append(img)
                    else:
                        logger.warning(f"⚠️ Image {img_id} not found or doesn't belong to user")
                except (ValueError, AttributeError):
                    # Try sequential number
                    try:
                        seq_num = int(img_id)
                        images = ImageHistory.objects.filter(user=self.user).order_by('created_at')
                        if seq_num > 0 and seq_num <= images.count():
                            resolved_images.append(images[seq_num - 1])
                        else:
                            logger.warning(f"⚠️ Sequential number {seq_num} out of range")
                    except (ValueError, IndexError):
                        logger.warning(f"⚠️ Could not resolve image ID: {img_id}")

            logger.info(f"✅ Resolved {len(resolved_images)} images")

            if len(resolved_images) < 4:
                return {
                    'success': False,
                    'error': f"Need at least 4 images for training, got {len(resolved_images)}. Please provide more images."
                }

            # Create CharacterModel with these images
            from content.models import CharacterTrainingImage
            from PIL import Image as PILImage
            from django.core.files.base import ContentFile
            import io

            character = CharacterModel.objects.create(
                user=self.user,
                name=style_name,
                trigger_word=trigger_word,
                training_status='preparing'
            )
            logger.info(f"✅ Created CharacterModel: {character.id}")

            # Create CharacterTrainingImage objects from ImageHistory images
            import requests
            from django.core.files.storage import default_storage

            for idx, img_hist in enumerate(resolved_images):
                # Get image data from file_path
                if img_hist.file_path.startswith('data:'):
                    # Data URI - extract base64 data
                    import base64
                    import re
                    match = re.match(r'data:image/\w+;base64,(.+)', img_hist.file_path)
                    if match:
                        img_data = base64.b64decode(match.group(1))
                    else:
                        logger.warning(f"⚠️ Could not parse data URI for image {img_hist.id}")
                        continue
                elif img_hist.file_path.startswith('http'):
                    # URL - fetch the image
                    response = requests.get(img_hist.file_path)
                    img_data = response.content
                else:
                    # Local file path
                    with default_storage.open(img_hist.file_path, 'rb') as f:
                        img_data = f.read()

                # Get image dimensions
                pil_img = PILImage.open(io.BytesIO(img_data))
                width, height = pil_img.size

                # Create CharacterTrainingImage
                training_img = CharacterTrainingImage(
                    character_model=character,
                    original_filename=img_hist.filename,
                    file_size=len(img_data),
                    width=width,
                    height=height,
                    order=idx,
                    is_valid=True
                )

                # Save the image file
                training_img.image.save(
                    img_hist.filename,
                    ContentFile(img_data),
                    save=False
                )
                training_img.save()

            character.training_images_count = len(resolved_images)
            character.save()
            logger.info(f"✅ Created {len(resolved_images)} CharacterTrainingImage objects")

            # Create training ZIP file
            from content.character_training import create_training_zip
            zip_path = create_training_zip(character)
            logger.info(f"✅ Created training ZIP: {zip_path}")

            # Submit training job using existing infrastructure
            from content.character_training import submit_training_job
            result = submit_training_job(character)

            logger.info(f"✅ Training submitted! ID: {result['training_id']}")

            return {
                'success': True,
                'message': f"🎨 Training '{style_name}' started! Training ID: {result['training_id']}. This will take approximately 15-30 minutes. The model will be ready to use in all workflows once complete.",
                'training_id': result['training_id'],
                'character_id': str(character.id),
                'trigger_word': trigger_word,
                'style_name': style_name,
                'status': result.get('status', 'pending'),
                'estimated_time_minutes': result.get('estimated_time_minutes', 20)
            }

        except Exception as e:
            logger.error(f"❌ Character training error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to start training: {str(e)}"
            }

    # Session 173: Co-Leadership Agent Handler
    def _handle_coleadership_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle co-leadership opinion requests - get collaborative AI agent recommendations.

        This enables conversational co-leadership: users can ask questions like
        "Should we train on images like #32?" and get opinions from the AI executive team.
        """
        question = arguments.get('question', '')
        image_ids = arguments.get('image_ids', [])
        context = arguments.get('context', '')
        # Session 173: Default to 5 executive agents for comprehensive team input
        participants = arguments.get('participants', ['CTOAgent', 'COOAgent', 'CreativeDirectorAgent', 'CFOAgent', 'DataAnalystAgent'])
        project_id = arguments.get('project_id') or getattr(getattr(self, 'project', None), 'id', None)

        logger.info(f"🎯 Co-Leadership Agent: Getting opinions on '{question}'")
        logger.info(f"   Image IDs: {image_ids}")
        logger.info(f"   Participants: {participants}")

        try:
            # Build enriched topic with image context
            topic = question
            if image_ids:
                # Get image details for context
                from content.models import ImageHistory
                image_details = []
                for img_id in image_ids:
                    try:
                        # Try sequential number first
                        seq_num = int(img_id)
                        images = ImageHistory.objects.filter(user=self.user).order_by('created_at')
                        if seq_num > 0 and seq_num <= images.count():
                            img = images[seq_num - 1]
                            image_details.append(f"Image #{seq_num}: {img.prompt[:100] if img.prompt else 'No prompt'}")
                    except (ValueError, TypeError):
                        pass

                if image_details:
                    topic += f"\n\nReferenced images:\n" + "\n".join(image_details)

            if context:
                topic += f"\n\nAdditional context: {context}"

            # Call the boardroom API
            from core.agents.executive import MeetingCoordinatorAgent

            coordinator = MeetingCoordinatorAgent(user=self.user)
            meeting_result = coordinator.start_meeting(
                topic=topic,
                project_id=str(project_id) if project_id else None,
                participants=participants
            )

            if meeting_result.get('status') != 'complete':
                return {
                    'success': False,
                    'error': 'Failed to get team opinions',
                    'details': meeting_result.get('message', 'Unknown error')
                }

            # Format recommendations conversationally
            agent_responses = meeting_result.get('agent_responses', {})
            recommendations = []

            stance_emoji = {
                'support': '👍',
                'concern': '⚠️',
                'objection': '👎',
                'alternative': '💡',
                'neutral': '🤔'
            }

            for agent_name, response_text in agent_responses.items():
                # Session 201: Improved stance detection with scoring system
                # Count positive and negative signals, then determine overall stance
                lower_text = response_text.lower()

                # Positive signals (supportive)
                positive_words = [
                    'recommend', 'support', 'approve', 'yes', 'definitely', 'great idea',
                    'would suggest', 'lean toward', 'go with', 'perfect', 'excellent',
                    'love', 'works well', 'ideal', 'strong', 'effective', 'good choice',
                    'should work', 'will help', 'great fit', 'nicely', 'complements',
                    'resonates', 'aligns', 'enhances', 'strengthens'
                ]
                positive_count = sum(1 for w in positive_words if w in lower_text)

                # Negative signals (concern/objection)
                negative_words = [
                    'concern', 'risk', 'caution', 'careful', 'worry', 'issue',
                    'problem', 'danger', 'warning', 'hesitant', 'unsure', 'doubt',
                    'reconsider', 'rethink', 'not sure', 'might not'
                ]
                negative_count = sum(1 for w in negative_words if w in lower_text)

                # Objection signals (strong negative)
                objection_words = ['object', 'against', 'reject', 'no', 'not recommend', 'bad idea', 'avoid', 'don\'t']
                objection_count = sum(1 for w in objection_words if w in lower_text)

                # Alternative signals
                alternative_words = ['alternative', 'instead', 'another option', 'what if', 'consider also', 'or we could']
                alternative_count = sum(1 for w in alternative_words if w in lower_text)

                # Determine stance based on scoring
                if objection_count > 0 and objection_count >= positive_count:
                    stance = 'objection'
                elif alternative_count > 0 and alternative_count > positive_count:
                    stance = 'alternative'
                elif positive_count > negative_count:
                    stance = 'support'
                elif negative_count > positive_count:
                    stance = 'concern'
                else:
                    # Default to support if giving constructive suggestions
                    # Most agents in a creative review are being helpful
                    if any(w in lower_text for w in ['suggest', 'would', 'could', 'should', 'try']):
                        stance = 'support'
                    else:
                        stance = 'neutral'

                emoji = stance_emoji.get(stance, '🤔')
                agent_display = agent_name.replace('Agent', '')
                recommendations.append({
                    'agent': agent_display,
                    'stance': stance,
                    'emoji': emoji,
                    'response': response_text
                })

            # Build conversational response
            response_parts = [f"**🎯 Team Opinions on: {question}**\n"]

            for rec in recommendations:
                response_parts.append(f"\n**{rec['emoji']} {rec['agent']}** ({rec['stance']})")
                response_parts.append(f"{rec['response'][:500]}{'...' if len(rec['response']) > 500 else ''}\n")

            # Add summary
            support_count = sum(1 for r in recommendations if r['stance'] == 'support')
            concern_count = sum(1 for r in recommendations if r['stance'] in ['concern', 'objection'])

            if support_count > concern_count:
                summary = "📊 **Summary:** The team is generally supportive!"
            elif concern_count > support_count:
                summary = "📊 **Summary:** There are concerns to address."
            else:
                summary = "📊 **Summary:** Mixed opinions - consider all perspectives."

            response_parts.append(f"\n{summary}")
            response_parts.append("\n\n*Use the Decision Timeline to formally commit your choice and track outcomes.*")

            return {
                'success': True,
                'message': '\n'.join(response_parts),
                'recommendations': recommendations,
                'summary': meeting_result.get('summary', ''),
                'question': question,
                'image_ids': image_ids
            }

        except Exception as e:
            logger.error(f"❌ Co-Leadership error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to get team opinions: {str(e)}"
            }

    # Session 128: Updated to use Image Editing Agent
    def _handle_web_search(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle web_search tool - Session 184 (restored from Session 65).

        Searches the web using Serper API (Google search).
        Enables the "research and create" autonomous workflow.
        """
        import os
        import requests

        logger.info(f"🔍 WEB_SEARCH TOOL CALLED!")

        try:
            query = arguments.get('query', '').strip()

            if not query:
                return {'success': False, 'error': 'Query is required for web search'}

            logger.info(f"🔍 Searching web for: {query}")

            # Use Serper API for Google search
            serper_key = os.getenv('SERPER_API_KEY')
            if not serper_key:
                return {
                    'success': False,
                    'error': 'Serper API key not configured. Add SERPER_API_KEY to your .env file.'
                }

            # Call Serper API
            url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": serper_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "num": 5  # Get top 5 results
            }

            response = requests.post(url, json=payload, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()

            # Extract organic search results
            results = []
            organic = data.get('organic', [])
            for item in organic[:5]:  # Top 5 results
                results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                })

            logger.info(f"✅ Found {len(results)} search results for '{query}'")

            return {
                'success': True,
                'results': results,
                'query': query,
                'message': f"Found {len(results)} results for '{query}'. Use these insights to inform your creative work!"
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Web search API error: {e}")
            return {'success': False, 'error': f'Web search failed: {str(e)}'}
        except Exception as e:
            logger.error(f"❌ Web search error: {e}")
            return {'success': False, 'error': str(e)}

    # Session 189/201: Create project from research workflow
    def _handle_create_project_from_research(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle create_project_from_research tool - Session 189/201.

        Creates a new creative project from research results and generated images.
        Session 201: Now auto-fills ALL project fields from workflow data.
        """
        logger.info(f"📁 CREATE_PROJECT_FROM_RESEARCH TOOL CALLED!")

        try:
            from content.models import CreativeProject
            from core.utils.id_resolver import resolve_image_id

            # Session 201: Extract all available project fields
            project_name = arguments.get('project_name', 'Research Project')
            description = arguments.get('description', '')
            goal = arguments.get('goal', '')
            research_summary = arguments.get('research_summary', '')
            executive_direction = arguments.get('executive_direction', '')
            research_links = arguments.get('research_links', [])  # Session 201: Full research sources
            agent_recommendations = arguments.get('agent_recommendations', [])  # Session 201: Agent recommendations
            image_ids = arguments.get('image_ids', [])
            video_ids = arguments.get('video_ids', [])
            category = arguments.get('category', 'branding')
            colors = arguments.get('colors', '')
            tags = arguments.get('tags', [])
            suggested_next_steps = arguments.get('suggested_next_steps', [])

            logger.info(f"📁 Creating project: {project_name}")
            logger.info(f"   Category: {category}")
            logger.info(f"   Colors: {colors}")
            logger.info(f"   Tags: {tags}")
            logger.info(f"   Images to include: {image_ids}")

            # Session 201: Create project with ALL fields populated
            project = CreativeProject.objects.create(
                user=self.user,
                name=project_name,
                description=description or f"Auto-generated project for {project_name}",
                goal=goal or (research_summary[:500] if research_summary else f"Research-based project: {project_name}"),
                category=category,
                colors=colors,
                tags=tags,
                status='in_progress',  # Has content, so in progress
                metadata={
                    'auto_generated': True,
                    'source': 'research_workflow',
                    'research_summary': research_summary,
                    'executive_direction': executive_direction,
                    'research_links': research_links,  # Session 201: Full research sources with links
                    'agent_recommendations': agent_recommendations,  # Session 201: Agent recommendations with stance
                    'suggested_next_steps': suggested_next_steps
                }
            )

            logger.info(f"✅ Project created: {project.id}")

            # Associate images with the project
            images_linked = 0
            linked_image_details = []

            for img_id in image_ids:
                try:
                    # Session 194: resolve_image_id returns (instance, error) tuple
                    # The instance is already the ImageHistory object, no need to re-fetch
                    image, error = resolve_image_id(img_id, self.user)
                    if image and not error:
                        image.project = project
                        image.save(update_fields=['project'])
                        images_linked += 1
                        linked_image_details.append({
                            'id': str(image.id),
                            'sequential': img_id,
                            'prompt': (image.prompt[:50] + '...') if image.prompt and len(image.prompt) > 50 else image.prompt
                        })
                        logger.info(f"   ✅ Linked image {img_id} to project")
                    else:
                        logger.warning(f"   ⚠️ Could not resolve image {img_id}: {error}")
                except Exception as e:
                    logger.warning(f"   ⚠️ Could not link image {img_id}: {e}")

            # Session 299: Link stored BusinessResearchResult records to this project
            research_linked = 0
            try:
                from core.models_unified_system import BusinessResearchResult

                # Extract market/topic from project name for matching
                # Clean common words to get the core topic
                topic_words = project_name.lower().replace('research', '').replace('project', '').replace('for', '').strip()
                topic_words = ' '.join(topic_words.split()[:4])  # First 4 meaningful words

                if topic_words:
                    # Find unlinked research that matches this topic
                    for research in BusinessResearchResult.objects.filter(
                        project__isnull=True,  # Only unlinked research
                        market_topic__icontains=topic_words.split()[0] if topic_words else ''
                    ).order_by('-created_at')[:5]:
                        research.project = project
                        research.save(update_fields=['project'])
                        research_linked += 1
                        logger.info(f"   ✅ Linked {research.research_type} research to project")

                    # Also try to link by query content match
                    if research_linked == 0:
                        for research in BusinessResearchResult.objects.filter(
                            project__isnull=True,
                            query__icontains=topic_words.split()[0] if topic_words else ''
                        ).order_by('-created_at')[:5]:
                            research.project = project
                            research.save(update_fields=['project'])
                            research_linked += 1
                            logger.info(f"   ✅ Linked {research.research_type} research (by query) to project")

                if research_linked > 0:
                    logger.info(f"📊 Session 299: Linked {research_linked} research reports to project")
            except Exception as e:
                logger.warning(f"Session 299: Could not link research to project: {e}")

            # Build response message
            response_parts = [
                f"## 📁 Project Created: **{project_name}**\n",
                f"**Category:** {category.replace('_', ' ').title()}",
                f"**Images Included:** {images_linked}",
            ]

            if research_linked > 0:
                response_parts.append(f"**Research Reports Linked:** {research_linked}")

            if research_summary:
                response_parts.append(f"\n### 📋 Research Summary\n{research_summary[:300]}{'...' if len(research_summary) > 300 else ''}")

            if linked_image_details:
                response_parts.append("\n### 🖼️ Project Images")
                for img in linked_image_details:
                    response_parts.append(f"- Image #{img['sequential']}: {img['prompt'] or 'No prompt'}")

            if suggested_next_steps:
                response_parts.append("\n### 🚀 Suggested Next Steps")
                for step in suggested_next_steps:
                    response_parts.append(f"- {step}")

            response_parts.append(f"\n\n✨ **Your project is ready!** You can find it in the project dropdown above.")
            response_parts.append(f"\n💡 Say \"switch to project {project_name[:20]}\" to start working on it!")

            return {
                'success': True,
                'message': '\n'.join(response_parts),
                'project_id': str(project.id),
                'project_name': project_name,
                'images_linked': images_linked,
                'research_linked': research_linked,
                'linked_images': linked_image_details
            }

        except Exception as e:
            logger.error(f"❌ Create project from research error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to create project: {str(e)}"
            }

    # Session 293: Business Research Agents (no image/video API credits)
    def _handle_competitor_analysis_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle competitor_analysis_agent tool - Session 293.

        Comprehensive competitor and market analysis WITHOUT image/video generation.
        Uses spider network and web search for real data.
        """
        logger.info(f"🏢 COMPETITOR_ANALYSIS_AGENT TOOL CALLED!")
        logger.info(f"🏢 Arguments: {arguments}")

        try:
            from core.agents.business import CompetitorAnalysisAgent

            market = arguments.get('market', '').strip()
            focus_areas = arguments.get('focus_areas', [])
            competitor_names = arguments.get('competitor_names', [])
            user_context = arguments.get('user_context', '')
            # Session 325: Extract project_id for context awareness
            project_id = arguments.get('project_id')

            if not market:
                return {'success': False, 'error': 'Market is required for competitor analysis'}

            logger.info(f"🏢 Analyzing competitors in: {market}")

            # Session 325: If we have a project, get its full context for the agent
            project_context_str = ""
            if project_id:
                try:
                    from core.models_partnership import PartnershipProject
                    project = PartnershipProject.objects.get(id=project_id)
                    project_context_str = f"Project: {project.project_name}"
                    if project.description:
                        project_context_str += f" - {project.description[:200]}"
                    # Include any prior research from this project
                    if project.metadata:
                        prior_research = project.metadata.get('research_summaries', [])
                        if prior_research:
                            latest = prior_research[-1]
                            project_context_str += f". Prior research ({latest.get('type', 'unknown')}): {latest.get('summary', '')[:300]}..."
                    logger.info(f"🏢 Project context: {project_context_str[:100]}...")
                except Exception as e:
                    logger.warning(f"Failed to get project context: {e}")

            # Instantiate and execute the agent
            agent = CompetitorAnalysisAgent(user=self.user)

            # Build task description - Session 325: Include project context
            task = f"Analyze the {market} market"
            if focus_areas:
                task += f" focusing on: {', '.join(focus_areas)}"
            if competitor_names:
                task += f". Specifically analyze: {', '.join(competitor_names)}"
            if user_context:
                task += f". Context: {user_context}"
            if project_context_str:
                task += f" {project_context_str}"

            logger.info(f"🏢 Task: {task}")

            # Session 293: Execute the agent with ALL required parameters
            # AgentResult requires: task, context, scifi_context, spider_context
            # Session 325: Now passing project_id for full context awareness
            from core.services.priority.enforce import check_priority, log_decision  # Session 1086 PR 3c
            _pd = check_priority('CompetitorAnalysisAgent', trigger_source='user_chat'); log_decision(_pd, 'CompetitorAnalysisAgent')
            result = agent.execute(
                task=task,
                context={
                    'market': market,
                    'focus_areas': focus_areas,
                    'competitor_names': competitor_names,
                    'user_context': user_context,
                    'project_id': project_id  # Session 325: Pass project_id!
                },
                scifi_context={},  # Session 293: Required parameter
                spider_context={}  # Session 293: Required parameter
            )

            logger.info(f"🏢 Agent result: success={result.success}, message={result.message[:100] if result.message else 'N/A'}...")
            logger.info(f"🏢 Agent data keys: {result.data.keys() if result.data else 'None'}")

            if result.success:
                # Session 293: Build response with proper structure for frontend
                # Frontend expects: agent_result.data.analysis (object with .analysis string)
                response = {
                    'success': True,
                    'message': result.message,  # Session 293: Use .message not .content
                    'agents_used': ['CompetitorAnalysisAgent'],
                    'metadata': {
                        'agent_result': {
                            'success': result.success,
                            'message': result.message,
                            'data': result.data,  # Contains {analysis: {...}, raw_data, query}
                            'agent_name': result.agent_name,
                            'execution_time_ms': result.execution_time_ms,
                            'decisions_made': result.decisions_made,
                            'tool_calls': result.tool_calls
                        }
                    },
                    'market': market,
                    'data': result.data  # Also at top level for legacy compatibility
                }
                logger.info(f"🏢 Returning success response with analysis")
                return response
            else:
                logger.error(f"🏢 Agent returned failure: {result.error}")
                return {
                    'success': False,
                    'error': result.error or 'Competitor analysis failed'
                }

        except Exception as e:
            logger.error(f"❌ Competitor analysis error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Competitor analysis failed: {str(e)}"
            }

    def _handle_customer_research_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle customer_research_agent tool - Session 293.

        Customer persona and pain point research WITHOUT image/video generation.
        Uses spider network (especially Reddit) for real customer data.
        """
        logger.info(f"👥 CUSTOMER_RESEARCH_AGENT TOOL CALLED!")

        try:
            from core.agents.business import CustomerResearchAgent

            market = arguments.get('market', '').strip()
            persona_count = arguments.get('persona_count', 3)
            focus_on = arguments.get('focus_on', 'all')
            user_context = arguments.get('user_context', '')
            # Session 325: Extract project_id for context awareness
            project_id = arguments.get('project_id')

            if not market:
                return {'success': False, 'error': 'Market is required for customer research'}

            logger.info(f"👥 Researching customers for: {market}")

            # Session 325: If we have a project, get its full context for the agent
            project_context_str = ""
            if project_id:
                try:
                    from core.models_partnership import PartnershipProject
                    project = PartnershipProject.objects.get(id=project_id)
                    project_context_str = f"Project: {project.project_name}"
                    if project.description:
                        project_context_str += f" - {project.description[:200]}"
                    # Include any prior research from this project
                    if project.metadata:
                        prior_research = project.metadata.get('research_summaries', [])
                        if prior_research:
                            latest = prior_research[-1]
                            project_context_str += f". Prior research ({latest.get('type', 'unknown')}): {latest.get('summary', '')[:300]}..."
                    logger.info(f"👥 Project context: {project_context_str[:100]}...")
                except Exception as e:
                    logger.warning(f"Failed to get project context: {e}")

            # Instantiate and execute the agent
            agent = CustomerResearchAgent(user=self.user)

            # Build task description - Session 325: Include project context
            task = f"Research customers for {market}"
            if focus_on != 'all':
                task += f" focusing on {focus_on}"
            task += f". Build {persona_count} customer personas."
            if user_context:
                task += f" Context: {user_context}"
            if project_context_str:
                task += f" {project_context_str}"

            # Execute the agent
            # Session 324: Agent requires scifi_context and spider_context
            # Session 325: Now passing project_id for full context awareness
            from core.services.priority.enforce import check_priority, log_decision  # Session 1086 PR 3c
            _pd = check_priority('CustomerResearchAgent', trigger_source='user_chat'); log_decision(_pd, 'CustomerResearchAgent')
            result = agent.execute(
                task=task,
                context={
                    'market': market,
                    'persona_count': persona_count,
                    'focus_on': focus_on,
                    'user_context': user_context,
                    'project_id': project_id  # Session 325: Pass project_id!
                },
                scifi_context={},  # Optional sci-fi features context
                spider_context={}  # Spider data is fetched internally by the agent
            )

            if result.success:
                # Session 324: AgentResult uses .message not .content
                return {
                    'success': True,
                    'message': result.message,
                    'agent': 'CustomerResearchAgent',
                    'market': market,
                    'data': result.data if hasattr(result, 'data') else {},
                    'metadata': {
                        'agent_result': {
                            'success': result.success,
                            'message': result.message,
                            'data': result.data,
                            'agent_name': result.agent_name,
                            'execution_time_ms': result.execution_time_ms
                        }
                    }
                }
            else:
                return {
                    'success': False,
                    'error': result.error or 'Customer research failed'
                }

        except Exception as e:
            logger.error(f"❌ Customer research error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Customer research failed: {str(e)}"
            }

    # Session 335: Brand Strategy Agent
    def _handle_brand_strategy_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle brand_strategy_agent tool - Session 335.

        Comprehensive brand strategy that reads existing project research
        (competitor analysis, customer research) and synthesizes it into
        actionable brand recommendations.

        IMPORTANT: This agent works best AFTER competitor and customer research
        has been completed for the project.
        """
        logger.info(f"🎨 BRAND_STRATEGY_AGENT TOOL CALLED!")
        logger.info(f"🎨 Arguments: {arguments}")

        try:
            from core.agents.business import BrandStrategyAgent

            project_id = arguments.get('project_id')
            brand_name = arguments.get('brand_name', '')
            focus_areas = arguments.get('focus_areas', [])
            user_context = arguments.get('user_context', '')

            if not project_id:
                return {
                    'success': False,
                    'error': 'Project ID is required for brand strategy. This agent reads existing project research.'
                }

            logger.info(f"🎨 Creating brand strategy for project: {project_id}")

            # Get project context
            project_context_str = ""
            project_name = brand_name
            try:
                from core.models_partnership import PartnershipProject
                project = PartnershipProject.objects.get(id=project_id)
                if not project_name:
                    project_name = project.project_name
                project_context_str = f"Project: {project.project_name}"
                if project.description:
                    project_context_str += f" - {project.description[:200]}"
                logger.info(f"🎨 Project context: {project_context_str[:100]}...")
            except Exception as e:
                logger.warning(f"Failed to get project context: {e}")

            # Instantiate and execute the agent
            agent = BrandStrategyAgent(user=self.user)

            # Build task description
            task = f"Create comprehensive brand strategy for '{project_name}'"
            if focus_areas:
                task += f" focusing on: {', '.join(focus_areas)}"
            if user_context:
                task += f". Context: {user_context}"
            if project_context_str:
                task += f" {project_context_str}"

            logger.info(f"🎨 Task: {task}")

            # Execute the agent
            from core.services.priority.enforce import check_priority, log_decision  # Session 1086 PR 3c
            _pd = check_priority('BrandStrategyAgent', trigger_source='user_chat'); log_decision(_pd, 'BrandStrategyAgent')
            result = agent.execute(
                task=task,
                context={
                    'project_id': project_id,
                    'brand_name': project_name,
                    'focus_areas': focus_areas,
                    'user_context': user_context
                },
                scifi_context={},
                spider_context={}
            )

            logger.info(f"🎨 Agent result: success={result.success}")

            if result.success:
                return {
                    'success': True,
                    'message': result.message,
                    'agents_used': ['BrandStrategyAgent'],
                    'metadata': {
                        'agent_result': {
                            'success': result.success,
                            'message': result.message,
                            'data': result.data,
                            'agent_name': result.agent_name,
                            'execution_time_ms': result.execution_time_ms,
                            'decisions_made': result.decisions_made,
                            'tool_calls': result.tool_calls
                        }
                    },
                    'project_id': project_id,
                    'brand_name': project_name,
                    'data': result.data
                }
            else:
                logger.error(f"🎨 Agent returned failure: {result.error}")
                return {
                    'success': False,
                    'error': result.error or 'Brand strategy creation failed'
                }

        except Exception as e:
            logger.error(f"❌ Brand strategy error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Brand strategy failed: {str(e)}"
            }

    # Session 337: Content Strategy Agent (NEW - uses BaseBusinessResearchAgent)
    def _handle_content_strategy_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle content_strategy_agent tool - Session 337.

        Strategic content planning that reads existing project research
        (competitor, customer, brand) and provides actionable content recommendations.
        """
        logger.info(f"📝 CONTENT_STRATEGY_AGENT TOOL CALLED!")
        logger.info(f"📝 Arguments: {arguments}")

        try:
            from core.agents.business import ContentStrategyAgent

            project_id = arguments.get('project_id')
            topic = arguments.get('topic', '')
            user_context = arguments.get('user_context', '')

            if not project_id:
                return {
                    'success': False,
                    'error': 'Project ID is required for content strategy. This agent reads existing project research.'
                }

            logger.info(f"📝 Creating content strategy for project: {project_id}")

            # Get project context
            project_context_str = ""
            project_name = topic
            try:
                from core.models_partnership import PartnershipProject
                project = PartnershipProject.objects.get(id=project_id)
                if not project_name:
                    project_name = project.project_name
                project_context_str = f"Project: {project.project_name}"
                if project.description:
                    project_context_str += f" - {project.description[:200]}"
                logger.info(f"📝 Project context: {project_context_str[:100]}...")
            except Exception as e:
                logger.warning(f"Failed to get project context: {e}")

            # Instantiate and execute the agent
            # Session 340: Pass project_id so agent can look up project context internally
            agent = ContentStrategyAgent(user=self.user, project_id=project_id)

            # Build task description
            task = f"Create comprehensive content strategy for '{project_name}'"
            if user_context:
                task += f". Context: {user_context}"
            if project_context_str:
                task += f" {project_context_str}"

            logger.info(f"📝 Task: {task}")

            # Execute the agent
            # Session 339: BaseBusinessResearchAgent.execute() only takes task and context
            from core.services.priority.enforce import check_priority, log_decision  # Session 1086 PR 3c
            _pd = check_priority('ContentStrategyAgent', trigger_source='user_chat'); log_decision(_pd, 'ContentStrategyAgent')
            result = agent.execute(
                task=task,
                context={
                    'project_id': project_id,
                    'topic': project_name,
                    'user_context': user_context
                }
            )

            logger.info(f"📝 Agent result: success={result.success}")

            if result.success:
                # Session 339: Build data structure for frontend
                # The frontend expects data.analysis to contain the synthesis
                result_data = result.data or {}

                # Session 339: Wrap analysis in structure frontend expects
                # Frontend looks for r.data.analysis.analysis (nested)
                # or r.data.analysis as a string
                if isinstance(result_data.get('analysis'), str):
                    # Wrap string analysis in expected structure
                    result_data['analysis'] = {
                        'analysis': result_data.get('analysis', ''),
                        'raw_data': result_data.get('raw_data', []),
                        'query': result_data.get('query', project_name),
                        'sources_used': result_data.get('sources_used', []),
                        'data_points_analyzed': result_data.get('data_points_analyzed', 0)
                    }

                return {
                    'success': True,
                    'message': result.message,
                    'agents_used': ['ContentStrategyAgent'],
                    'metadata': {
                        'agent_result': {
                            'success': result.success,
                            'message': result.message,
                            'data': result_data,
                            'agent_name': result.agent_name,
                            'execution_time_ms': result.execution_time_ms,
                            'decisions_made': getattr(result, 'decisions_made', 0),
                            'tool_calls': getattr(result, 'tool_calls', [])
                        }
                    },
                    'project_id': project_id,
                    'topic': project_name,
                    'data': result_data
                }
            else:
                logger.error(f"📝 Agent returned failure: {result.error}")
                return {
                    'success': False,
                    'error': result.error or 'Content strategy creation failed'
                }

        except Exception as e:
            logger.error(f"❌ Content strategy error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Content strategy failed: {str(e)}"
            }

    # Session 337: Marketing Strategy Agent (NEW - uses BaseBusinessResearchAgent)
    def _handle_marketing_strategy_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle marketing_strategy_agent tool - Session 337.

        Strategic marketing planning that reads existing project research
        (competitor, customer, brand, content) and provides actionable marketing recommendations.
        """
        logger.info(f"📣 MARKETING_STRATEGY_AGENT TOOL CALLED!")
        logger.info(f"📣 Arguments: {arguments}")

        try:
            from core.agents.business import MarketingStrategyAgent

            project_id = arguments.get('project_id')
            topic = arguments.get('topic', '')
            user_context = arguments.get('user_context', '')
            budget = arguments.get('budget', '')

            if not project_id:
                return {
                    'success': False,
                    'error': 'Project ID is required for marketing strategy. This agent reads existing project research.'
                }

            logger.info(f"📣 Creating marketing strategy for project: {project_id}")

            # Get project context
            project_context_str = ""
            project_name = topic
            try:
                from core.models_partnership import PartnershipProject
                project = PartnershipProject.objects.get(id=project_id)
                if not project_name:
                    project_name = project.project_name
                project_context_str = f"Project: {project.project_name}"
                if project.description:
                    project_context_str += f" - {project.description[:200]}"
                logger.info(f"📣 Project context: {project_context_str[:100]}...")
            except Exception as e:
                logger.warning(f"Failed to get project context: {e}")

            # Instantiate and execute the agent
            # Session 340: Pass project_id so agent can look up project context internally
            agent = MarketingStrategyAgent(user=self.user, project_id=project_id)

            # Build task description
            task = f"Create comprehensive marketing strategy for '{project_name}'"
            if budget:
                task += f" with budget considerations: {budget}"
            if user_context:
                task += f". Context: {user_context}"
            if project_context_str:
                task += f" {project_context_str}"

            logger.info(f"📣 Task: {task}")

            # Execute the agent
            # Session 339: BaseBusinessResearchAgent.execute() only takes task and context
            from core.services.priority.enforce import check_priority, log_decision  # Session 1086 PR 3c
            _pd = check_priority('MarketingStrategyAgent', trigger_source='user_chat'); log_decision(_pd, 'MarketingStrategyAgent')
            result = agent.execute(
                task=task,
                context={
                    'project_id': project_id,
                    'topic': project_name,
                    'user_context': user_context,
                    'budget': budget
                }
            )

            logger.info(f"📣 Agent result: success={result.success}")

            if result.success:
                # Session 339: Build data structure for frontend
                # The frontend expects data.analysis to contain the synthesis
                result_data = result.data or {}

                # Session 339: Wrap analysis in structure frontend expects
                # Frontend looks for r.data.analysis.analysis (nested)
                # or r.data.analysis as a string
                if isinstance(result_data.get('analysis'), str):
                    # Wrap string analysis in expected structure
                    result_data['analysis'] = {
                        'analysis': result_data.get('analysis', ''),
                        'raw_data': result_data.get('raw_data', []),
                        'query': result_data.get('query', project_name),
                        'sources_used': result_data.get('sources_used', []),
                        'data_points_analyzed': result_data.get('data_points_analyzed', 0)
                    }

                return {
                    'success': True,
                    'message': result.message,
                    'agents_used': ['MarketingStrategyAgent'],
                    'metadata': {
                        'agent_result': {
                            'success': result.success,
                            'message': result.message,
                            'data': result_data,
                            'agent_name': result.agent_name,
                            'execution_time_ms': result.execution_time_ms,
                            'decisions_made': getattr(result, 'decisions_made', 0),
                            'tool_calls': getattr(result, 'tool_calls', [])
                        }
                    },
                    'project_id': project_id,
                    'topic': project_name,
                    'data': result_data
                }
            else:
                logger.error(f"📣 Agent returned failure: {result.error}")
                return {
                    'success': False,
                    'error': result.error or 'Marketing strategy creation failed'
                }

        except Exception as e:
            logger.error(f"❌ Marketing strategy error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Marketing strategy failed: {str(e)}"
            }

    # Session 312: Unified strategy agent handler
    def _handle_strategy_agent(self, agent_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle strategy agent tools - Session 312.

        Unified handler for: brand_identity_agent, content_strategy_agent,
        seo_optimizer_agent, trend_analysis_agent, social_media_agent.

        These agents were previously disconnected from the Personal Assistant.
        """
        logger.info(f"📊 STRATEGY_AGENT: {agent_name} CALLED!")

        try:
            action = arguments.get('action', '')
            if not action:
                return {'success': False, 'error': 'Action is required'}

            # Import and instantiate the appropriate agent
            import warnings
            warnings.filterwarnings('ignore', category=DeprecationWarning)

            if agent_name == 'brand_identity_agent':
                from core.agents.strategy import BrandIdentityAgent
                agent = BrandIdentityAgent(user=self.user)

                if action == 'get_profile':
                    result = agent.get_brand_profile()
                elif action == 'set_colors':
                    result = agent.set_brand_colors(
                        primary=arguments.get('primary_color', '#3498DB'),
                        secondary=arguments.get('secondary_color', '#2ECC71'),
                        accent=arguments.get('accent_color', '#E74C3C')
                    )
                elif action == 'enhance_prompt':
                    result = agent.enhance_prompt(arguments.get('prompt', ''))
                elif action == 'generate_guidelines':
                    result = agent.generate_guidelines()
                elif action == 'suggest_colors':
                    result = agent.suggest_colors_for_industry(arguments.get('industry', 'tech'))
                else:
                    return {'success': False, 'error': f'Unknown action: {action}'}

            elif agent_name == 'content_strategy_agent':
                from core.agents.strategy import ContentStrategyAgent
                agent = ContentStrategyAgent(user=self.user)

                if action == 'get_recommendations':
                    result = agent.get_recommendations(
                        niche=arguments.get('niche'),
                        content_type=arguments.get('content_type', 'all')
                    )
                elif action == 'get_trending':
                    result = agent.get_trending_topics()
                elif action == 'get_calendar':
                    result = agent.get_content_calendar()
                elif action == 'analyze_opportunity':
                    result = agent.analyze_opportunity(arguments.get('opportunity_description', ''))
                else:
                    return {'success': False, 'error': f'Unknown action: {action}'}

            elif agent_name == 'seo_optimizer_agent':
                from core.agents.strategy import SEOOptimizerAgent
                agent = SEOOptimizerAgent(user=self.user)

                if action == 'get_hashtags':
                    result = agent.get_hashtags(
                        topic=arguments.get('topic', ''),
                        count=arguments.get('hashtag_count', 10)
                    )
                elif action == 'suggest_keywords':
                    result = agent.suggest_keywords(arguments.get('topic', ''))
                elif action == 'optimize_image':
                    result = agent.optimize_image(image_id=arguments.get('image_id', ''))
                elif action == 'optimize_for_platform':
                    result = agent.optimize_for_platform(
                        content=arguments.get('topic', ''),
                        platform=arguments.get('platform', 'instagram')
                    )
                else:
                    return {'success': False, 'error': f'Unknown action: {action}'}

            elif agent_name == 'trend_analysis_agent':
                from core.agents.analysis import TrendAnalysisAgent
                agent = TrendAnalysisAgent(user=self.user)

                if action == 'analyze_sector':
                    result = agent.analyze_sector(arguments.get('sector', 'tech'))
                elif action == 'find_opportunities':
                    result = agent.find_emerging_opportunities()
                elif action == 'daily_briefing':
                    result = agent.generate_daily_briefing()
                elif action == 'get_insights':
                    result = agent.get_insights_for_prompt(arguments.get('topic', ''))
                else:
                    return {'success': False, 'error': f'Unknown action: {action}'}

            elif agent_name == 'social_media_agent':
                from core.agents.strategy import SocialMediaAgent
                agent = SocialMediaAgent(user=self.user)

                if action == 'create_for_platform':
                    result = agent.create_for_platform(
                        platform=arguments.get('platform', 'instagram'),
                        content_description=arguments.get('content_description', '')
                    )
                elif action == 'create_multi_platform':
                    result = agent.create_multi_platform(arguments.get('content_description', ''))
                elif action == 'get_platform_specs':
                    result = agent.get_platform_specs(arguments.get('platform', 'instagram'))
                elif action == 'create_calendar':
                    result = agent.create_content_calendar(
                        days=arguments.get('calendar_days', 7)
                    )
                elif action == 'suggest_content_type':
                    result = agent.suggest_content_type(arguments.get('platform', 'instagram'))
                else:
                    return {'success': False, 'error': f'Unknown action: {action}'}

            else:
                return {'success': False, 'error': f'Unknown strategy agent: {agent_name}'}

            # Return the result
            if isinstance(result, dict):
                return {'success': True, 'agent': agent_name, 'action': action, **result}
            else:
                return {'success': True, 'agent': agent_name, 'action': action, 'result': result}

        except Exception as e:
            logger.error(f"❌ Strategy agent error ({agent_name}): {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Strategy agent failed: {str(e)}"
            }

    # Session 313: Creative Director Agent handler
    def _handle_creative_director_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle creative_director_agent tool - Session 313.

        Provides high-level creative guidance and direction for visual projects.
        """
        logger.info(f"🎨 CREATIVE_DIRECTOR_AGENT CALLED!")

        try:
            action = arguments.get('action', '')
            if not action:
                return {'success': False, 'error': 'Action is required'}

            import warnings
            warnings.filterwarnings('ignore', category=DeprecationWarning)

            from core.agents.executive import CreativeDirectorAgent
            agent = CreativeDirectorAgent(user=self.user)

            if action == 'review_prompt':
                prompt = arguments.get('prompt', '')
                if not prompt:
                    return {'success': False, 'error': 'Prompt is required for review_prompt action'}
                result = agent.review_prompt(
                    prompt=prompt,
                    content_type=arguments.get('content_type')
                )
            elif action == 'establish_direction':
                project_brief = arguments.get('project_brief', '')
                if not project_brief:
                    return {'success': False, 'error': 'Project brief is required for establish_direction action'}
                result = agent.establish_creative_direction(
                    project_brief=project_brief,
                    target_audience=arguments.get('target_audience'),
                    industry=arguments.get('industry')
                )
            elif action == 'critique_design':
                design_description = arguments.get('design_description', '')
                intended_purpose = arguments.get('intended_purpose', '')
                if not design_description or not intended_purpose:
                    return {'success': False, 'error': 'Design description and intended purpose are required'}
                result = agent.critique_design(
                    design_description=design_description,
                    intended_purpose=intended_purpose
                )
            elif action == 'get_insights':
                topic = arguments.get('topic', '')
                if not topic:
                    return {'success': False, 'error': 'Topic is required for get_insights action'}
                result = agent.get_creative_insights(topic=topic)
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

            # Return the result
            if isinstance(result, dict):
                return {'success': True, 'agent': 'creative_director_agent', 'action': action, **result}
            else:
                return {'success': True, 'agent': 'creative_director_agent', 'action': action, 'result': result}

        except Exception as e:
            logger.error(f"❌ Creative Director agent error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Creative Director agent failed: {str(e)}"
            }

    # Session 313: Opportunity Scoring Agent handler
    def _handle_opportunity_scoring_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle opportunity_scoring_agent tool - Session 313.

        Transforms spider intelligence data into scored, actionable opportunities.
        """
        logger.info(f"📊 OPPORTUNITY_SCORING_AGENT CALLED!")

        try:
            action = arguments.get('action', '')
            if not action:
                return {'success': False, 'error': 'Action is required'}

            import warnings
            warnings.filterwarnings('ignore', category=DeprecationWarning)

            from core.agents.analysis import OpportunityScoringAgent
            agent = OpportunityScoringAgent()

            if action == 'score_data':
                hours = arguments.get('hours', 24)
                limit = arguments.get('limit', 50)
                results = agent.score_spider_data(hours=hours, limit=limit, user=self.user)
                # Convert ScoringResult objects to dicts
                scored_items = [r.to_dict() if hasattr(r, 'to_dict') else r for r in results]
                result = {
                    'success': True,
                    'scored_opportunities': scored_items,
                    'count': len(scored_items),
                    'message': f"Scored {len(scored_items)} spider data items from last {hours} hours"
                }
            elif action == 'analyze_trend':
                trend_topic = arguments.get('trend_topic', '')
                if not trend_topic:
                    return {'success': False, 'error': 'Trend topic is required for analyze_trend action'}
                scoring_result = agent.analyze_trend(
                    trend_topic=trend_topic,
                    user=self.user
                )
                result = scoring_result.to_dict() if hasattr(scoring_result, 'to_dict') else scoring_result
            elif action == 'get_top':
                limit = arguments.get('limit', 10)
                min_score = arguments.get('min_score', 50)
                results = agent.get_top_opportunities(limit=limit, min_score=min_score)
                # Convert to serializable format
                opportunities = []
                for opp in results:
                    if hasattr(opp, 'to_dict'):
                        opportunities.append(opp.to_dict())
                    elif hasattr(opp, '__dict__'):
                        opportunities.append({k: str(v) if hasattr(v, '__str__') else v for k, v in opp.__dict__.items()})
                    else:
                        opportunities.append(str(opp))
                result = {
                    'success': True,
                    'opportunities': opportunities,
                    'count': len(opportunities),
                    'message': f"Found {len(opportunities)} top opportunities (min score: {min_score})"
                }
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

            # Return the result
            if isinstance(result, dict):
                return {'success': True, 'agent': 'opportunity_scoring_agent', 'action': action, **result}
            else:
                return {'success': True, 'agent': 'opportunity_scoring_agent', 'action': action, 'result': result}

        except Exception as e:
            logger.error(f"❌ Opportunity Scoring agent error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Opportunity Scoring agent failed: {str(e)}"
            }

    # Session 313: Trained Creation Agent handler
    def _handle_trained_creation_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle trained_creation_agent tool - Session 313.

        Generates images using trained LoRA models (character/style).
        """
        logger.info(f"🎨 TRAINED_CREATION_AGENT CALLED!")

        try:
            prompt = arguments.get('prompt', '')
            character_model_name = arguments.get('character_model_name', '')

            if not prompt:
                return {'success': False, 'error': 'Prompt is required'}
            if not character_model_name:
                return {'success': False, 'error': 'Character model name is required'}

            import warnings
            warnings.filterwarnings('ignore', category=DeprecationWarning)

            from core.agents.training import TrainedCreationAgent
            agent = TrainedCreationAgent(user=self.user, project_id=getattr(self, 'project_id', None))

            from core.services.priority.enforce import check_priority, log_decision  # Session 1086 PR 3c
            _pd = check_priority('TrainedCreationAgent', trigger_source='user_chat'); log_decision(_pd, 'TrainedCreationAgent')
            result = agent.execute(
                prompt=prompt,
                character_model_name=character_model_name,
                lora_scale=arguments.get('lora_scale', 0.8),
                width=arguments.get('width', 1024),
                height=arguments.get('height', 1024),
                num_outputs=arguments.get('num_outputs', 1)
            )

            return {'success': True, 'agent': 'trained_creation_agent', **result}

        except Exception as e:
            logger.error(f"❌ Trained Creation agent error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Trained Creation agent failed: {str(e)}"
            }

    # Session 313: CTO Agent handler
    def _handle_cto_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle cto_agent tool - Session 313.

        Provides technical architecture analysis and planning.
        """
        logger.info(f"🏗️ CTO_AGENT CALLED!")

        try:
            action = arguments.get('action', '')
            if not action:
                return {'success': False, 'error': 'Action is required'}

            import warnings
            warnings.filterwarnings('ignore', category=DeprecationWarning)

            from core.agents.executive import CTOAgent
            agent = CTOAgent(user=self.user)

            if action == 'analyze_feature':
                feature_name = arguments.get('feature_name', arguments.get('description', ''))
                if not feature_name:
                    return {'success': False, 'error': 'Feature name is required for analyze_feature action'}
                result = agent.analyze_feature(
                    feature_name=feature_name,
                    scope=arguments.get('scope', 'feature')
                )
            elif action == 'plan_implementation':
                description = arguments.get('description', arguments.get('feature_name', ''))
                if not description:
                    return {'success': False, 'error': 'Description is required for plan_implementation action'}
                result = agent.implement_feature(
                    description=description,
                    approach=arguments.get('approach', 'recommended')
                )
            elif action == 'analyze_documentation':
                result = agent.sync_documentation(
                    scope=arguments.get('scope', 'all_agents')
                )
            elif action == 'coordinate_agents':
                task = arguments.get('task', '')
                required_agents = arguments.get('required_agents', [])
                if not task:
                    return {'success': False, 'error': 'Task is required for coordinate_agents action'}
                result = agent.coordinate_agents(
                    task=task,
                    required_agents=required_agents
                )
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

            if isinstance(result, dict):
                return {'success': True, 'agent': 'cto_agent', 'action': action, **result}
            else:
                return {'success': True, 'agent': 'cto_agent', 'action': action, 'result': result}

        except Exception as e:
            logger.error(f"❌ CTO agent error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"CTO agent failed: {str(e)}"
            }

    # Session 313: COO Agent handler
    def _handle_coo_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle coo_agent tool - Session 313.

        Provides operations planning and risk analysis.
        """
        logger.info(f"🏢 COO_AGENT CALLED!")

        try:
            action = arguments.get('action', '')
            if not action:
                return {'success': False, 'error': 'Action is required'}

            import warnings
            warnings.filterwarnings('ignore', category=DeprecationWarning)

            from core.agents.executive import COOAgent
            agent = COOAgent(user=self.user)

            if action == 'analyze_roadmap':
                result = agent.analyze_roadmap(
                    project_slug=arguments.get('project_slug'),
                    feature_name=arguments.get('feature_name'),
                    scope=arguments.get('scope', 'project')
                )
            elif action == 'propose_sprint':
                result = agent.propose_next_sprint(
                    project_slug=arguments.get('project_slug'),
                    feature_name=arguments.get('feature_name'),
                    sprint_duration=arguments.get('sprint_duration', '2 weeks')
                )
            elif action == 'identify_risks':
                result = agent.identify_risks(
                    project_slug=arguments.get('project_slug'),
                    feature_name=arguments.get('feature_name'),
                    scope=arguments.get('scope', 'project')
                )
            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

            if isinstance(result, dict):
                return {'success': True, 'agent': 'coo_agent', 'action': action, **result}
            else:
                return {'success': True, 'agent': 'coo_agent', 'action': action, 'result': result}

        except Exception as e:
            logger.error(f"❌ COO agent error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"COO agent failed: {str(e)}"
            }

    # Session 313: Meeting Coordinator Agent handler
    def _handle_meeting_coordinator_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle meeting_coordinator_agent tool - Session 313.

        Coordinates executive boardroom meetings between agents.
        """
        logger.info(f"🏢 MEETING_COORDINATOR_AGENT CALLED!")

        try:
            topic = arguments.get('topic', '')
            if not topic:
                return {'success': False, 'error': 'Topic is required'}

            import warnings
            warnings.filterwarnings('ignore', category=DeprecationWarning)

            from core.agents.executive import MeetingCoordinatorAgent
            agent = MeetingCoordinatorAgent(user=self.user)

            result = agent.start_meeting(
                topic=topic,
                project_id=arguments.get('project_id'),
                participants=arguments.get('participants')
            )

            if isinstance(result, dict):
                return {'success': True, 'agent': 'meeting_coordinator_agent', **result}
            else:
                return {'success': True, 'agent': 'meeting_coordinator_agent', 'result': result}

        except Exception as e:
            logger.error(f"❌ Meeting Coordinator agent error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Meeting Coordinator agent failed: {str(e)}"
            }

    # Session 313: Content Executor Agent handler
    def _handle_content_executor_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle content_executor_agent tool - Session 313.

        Executes AI content creation tasks.
        """
        logger.info(f"📝 CONTENT_EXECUTOR_AGENT CALLED!")

        try:
            task = arguments.get('task', '')
            if not task:
                return {'success': False, 'error': 'Task description is required'}

            from core.services.content_executor import DonkeyBetzContentExecutor
            from core.models.agents_registry import AgentExecution, UnifiedAgentTemplate

            # Create execution record
            try:
                template = UnifiedAgentTemplate.objects.get(name='DonkeyBetzContentExecutor')
            except UnifiedAgentTemplate.DoesNotExist:
                template = UnifiedAgentTemplate.objects.create(
                    name='DonkeyBetzContentExecutor',
                    display_name='Content Executor',
                    description='Executes AI content creation tasks'
                )

            execution = AgentExecution.objects.create(
                agent=template,
                user=self.user,
                input_data={
                    'task': task,
                    'content_type': arguments.get('content_type', 'blog_post'),
                    'target_audience': arguments.get('target_audience', 'general audience'),
                    'tone': arguments.get('tone', 'professional')
                }
            )

            executor = DonkeyBetzContentExecutor()
            result = executor.execute_content_creation(
                execution_id=str(execution.id),
                task_data=execution.input_data
            )

            return {'success': True, 'agent': 'content_executor_agent', **result}

        except Exception as e:
            logger.error(f"❌ Content Executor agent error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Content Executor agent failed: {str(e)}"
            }

    # Session 313: AI Project Builder Agent handler
    def _handle_ai_project_builder_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle ai_project_builder_agent tool - Session 313.

        Builds AI projects from spider-discovered monetization strategies.
        """
        logger.info(f"🏗️ AI_PROJECT_BUILDER_AGENT CALLED!")

        try:
            task = arguments.get('task', '')
            if not task:
                return {'success': False, 'error': 'Task description is required'}

            from agents.ai_project_builder import AIProjectBuilder

            builder = AIProjectBuilder()

            # Optionally provide a strategy hint based on project type
            strategy = None
            project_type = arguments.get('project_type')
            if project_type:
                strategy = {'strategy_type': project_type, 'title': task}

            result = builder.build_project(
                task=task,
                strategy=strategy if not arguments.get('use_spider_strategy', True) else None
            )

            return {'success': True, 'agent': 'ai_project_builder_agent', **result}

        except Exception as e:
            logger.error(f"❌ AI Project Builder agent error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"AI Project Builder agent failed: {str(e)}"
            }

    # Session 184: Restored create_brand_video handler from Session 67
    def _handle_create_brand_video(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle create_brand_video tool - Session 184 (restored from Session 67).

        Creates a complete brand video from concept to finished product.
        Orchestrates Runway ML video generation with professional styling.
        """
        logger.info(f"🎬 CREATE_BRAND_VIDEO TOOL CALLED!")

        try:
            brand_name = arguments.get('brand_name', '').strip()
            concept = arguments.get('concept', '').strip()
            style = arguments.get('style', 'modern')
            include_branding = arguments.get('include_branding', True)
            video_count = arguments.get('video_count', 3)
            project_id = arguments.get('project_id')

            # Get current project if not provided
            if not project_id:
                current_project = getattr(self, 'project', None)
                if current_project:
                    project_id = str(current_project.id)

            if not brand_name:
                return {'success': False, 'error': 'Brand name is required'}
            if not concept:
                return {'success': False, 'error': 'Concept is required'}

            # Validate video_count (2-5)
            if video_count < 2 or video_count > 5:
                logger.warning(f"⚠️ Invalid video_count {video_count}, defaulting to 3")
                video_count = 3

            logger.info(f"🎬 Creating brand video for {brand_name}: {concept} ({style} style, {video_count} clips)")

            # Style-specific prompt modifiers
            style_modifiers = {
                'cinematic': 'dramatic lighting, cinematic composition, film grain, depth of field',
                'modern': 'clean lines, minimalist, bright natural lighting, contemporary design',
                'playful': 'vibrant colors, dynamic movement, fun energy, cheerful atmosphere',
                'elegant': 'sophisticated, refined aesthetic, smooth movements, luxury feel',
                'energetic': 'fast-paced, dynamic transitions, bold colors, high energy'
            }

            style_prompt = style_modifiers.get(style, style_modifiers['modern'])

            # Generate prompts for each video clip
            prompts = []
            if video_count == 2:
                prompts = [
                    f"{concept}, {style_prompt}, opening shot",
                    f"{brand_name} showcase, {concept}, {style_prompt}, closing scene"
                ]
            elif video_count == 3:
                prompts = [
                    f"{concept}, {style_prompt}, establishing shot",
                    f"{brand_name} product or service, {concept}, {style_prompt}, detail view",
                    f"{concept}, {style_prompt}, powerful closing scene with {brand_name}"
                ]
            elif video_count == 4:
                prompts = [
                    f"{concept}, {style_prompt}, opening sequence",
                    f"{brand_name} highlights, {concept}, {style_prompt}, feature showcase",
                    f"{concept} in action, {style_prompt}, dynamic demonstration",
                    f"{brand_name} finale, {concept}, {style_prompt}, memorable closing"
                ]
            else:  # 5 clips
                prompts = [
                    f"{concept}, {style_prompt}, captivating opening",
                    f"{brand_name} introduction, {concept}, {style_prompt}",
                    f"{concept}, {style_prompt}, mid-point highlight",
                    f"{brand_name} key features, {concept}, {style_prompt}",
                    f"{concept}, {style_prompt}, impactful conclusion with {brand_name}"
                ]

            # Generate all videos using Runway ML
            from content.video_provider import runway_provider
            from content.models import VideoHistory

            task_ids = []
            video_ids = []
            total_estimated_time = 0

            for i, prompt in enumerate(prompts):
                logger.info(f"🎬 Generating clip {i+1}/{len(prompts)}: {prompt[:60]}...")

                result = runway_provider.text_to_video(
                    prompt=prompt,
                    duration=8,  # 8 seconds per clip for professional feel
                    quality='veo3.1_fast',
                    style='realistic',
                    enhance_prompt=True,
                    enhancement_level='advanced',
                    ratio='1920:1080'
                )

                if not result.success:
                    logger.warning(f"⚠️ Clip {i+1} generation failed: {result.error_message}")
                    continue

                # Store in VideoHistory
                from core.services.workspace_resolver import get_active_workspace
                video = VideoHistory.objects.create(
                    user=self.user,
                    prompt=prompt,
                    task_id=result.task_id,
                    status='processing',
                    workspace=get_active_workspace(self.user),
                    parameters={
                        'duration': 8,
                        'quality': 'veo3.1_fast',
                        'style': style,
                        'type': 'brand_video_clip',
                        'brand_name': brand_name,
                        'clip_number': i + 1,
                        'total_clips': len(prompts),
                        'estimated_time': result.estimated_time,
                        'include_branding': include_branding,
                        'project_id': project_id
                    }
                )

                # Associate with project if available
                if project_id:
                    try:
                        from core.models import Project
                        project = Project.objects.get(id=project_id)
                        video.project = project
                        video.save()
                    except Exception as e:
                        logger.warning(f"⚠️ Could not associate video with project: {e}")

                task_ids.append(result.task_id)
                video_ids.append(str(video.id))
                total_estimated_time += result.estimated_time

            logger.info(f"✅ Started {len(task_ids)} video generations for {brand_name}")

            return {
                'success': True,
                'brand_name': brand_name,
                'task_ids': task_ids,
                'video_ids': video_ids,
                'prompts': prompts,
                'video_count': len(task_ids),
                'estimated_time': total_estimated_time,
                'include_branding': include_branding,
                'project_id': project_id,
                'message': f'🎬 Started generating {len(task_ids)} video clips for {brand_name}! Videos will appear in your gallery when ready (~{total_estimated_time}s). Once complete, you can chain them together with transitions and branding!'
            }

        except Exception as e:
            logger.error(f"❌ Create brand video error: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}

    def _handle_workflow_orchestration_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle workflow_orchestration_agent tool - Session 496 (legacy fallback).

        Executes creative workflows like research_and_create_logos, youtube_thumbnail_package, etc.
        This is a fallback handler if the AgentRouter.execute_tool() fails.
        """
        logger.info(f"🔄 WORKFLOW_ORCHESTRATION_AGENT TOOL CALLED (legacy handler)")
        logger.info(f"📋 Arguments: {arguments}")

        try:
            from core.agents.workflow_orchestration_agent import WorkflowOrchestrationAgent

            workflow = arguments.get('workflow', 'research_and_create_images')
            topic = arguments.get('topic', '')
            count = arguments.get('count', 3)
            style_preferences = arguments.get('style_preferences', '')
            user_message = arguments.get('user_message', '')
            project_id = arguments.get('project_id')

            # Get current project if not provided
            if not project_id:
                current_project = getattr(self, 'project', None)
                if current_project:
                    project_id = str(current_project.id)

            # Create agent instance
            agent = WorkflowOrchestrationAgent(
                user=self.user,
                project_id=project_id
            )

            # Build context
            context = {
                'workflow': workflow,
                'topic': topic,
                'count': count,
                'style_preferences': style_preferences,
                'user_message': user_message,
            }

            logger.info(f"🎯 Executing workflow: {workflow} for topic: {topic}")
            logger.info(f"📝 User message length: {len(user_message)} chars")

            # Check if research context is present
            if '--- RESEARCH CONTEXT ---' in user_message:
                logger.info(f"📊 Research context detected in user_message!")

            # Execute workflow
            from core.services.priority.enforce import check_priority, log_decision  # Session 1086 PR 3c
            _pd = check_priority('WorkflowOrchestrationAgent', trigger_source='user_chat'); log_decision(_pd, 'WorkflowOrchestrationAgent')
            result = agent.execute(
                task=user_message or topic,
                context=context,
                scifi_context={},
                spider_context={}
            )

            # Convert AgentResult to dict
            if result.success:
                return {
                    'success': True,
                    'message': result.message,
                    'data': result.data,
                    'agent_name': result.agent_name
                }
            else:
                return {
                    'success': False,
                    'error': result.error
                }

        except Exception as e:
            logger.error(f"❌ Workflow orchestration agent error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _handle_content_writer_agent(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle content_writer_agent tool - Session 496.
        Session 521: Now fetches REAL spider data for current trends!

        Transforms research into written content: blog posts, podcast scripts,
        video scripts, articles, social threads, newsletters.
        """
        logger.info(f"📝 CONTENT_WRITER_AGENT TOOL CALLED!")
        logger.info(f"📋 Arguments: {arguments}")

        try:
            from core.agents.content_writer_agent import ContentWriterAgent
            from datetime import datetime

            content_type = arguments.get('content_type', 'blog_post')
            # Session 496: Tool definition uses 'topic', but also accept 'task' for compatibility
            task = arguments.get('topic', '') or arguments.get('task', '')
            tone = arguments.get('tone', 'professional')
            target_audience = arguments.get('target_audience', 'general audience')
            word_count = arguments.get('word_count', 1500)
            research = arguments.get('research_context', '')

            # Session 521: Fetch REAL spider data if no research provided
            spider_context = {}
            if not research and task:
                logger.info(f"🕷️ Session 521: Fetching real-time spider data for topic: {task}")
                try:
                    from core.services.smart_trending_service import SmartTrendingService
                    trending_service = SmartTrendingService()
                    trending_data = trending_service.get_trending_for_query(
                        query=task,
                        hours=72,
                        article_limit=10,
                        use_cache=True
                    )

                    # Build research context from spider data
                    if trending_data:
                        spider_context = trending_data
                        now = datetime.now()
                        today = now.strftime('%B %d, %Y')
                        month_year = now.strftime('%B %Y')
                        year = now.year
                        # Dynamic "don't use old years" instruction
                        old_years = f"{year-2} or {year-1}"
                        # Format spider data as research context
                        research_parts = [
                            f"## Real-Time Research Data (as of {today})",
                            f"**IMPORTANT: This content is for {year}. DO NOT reference {old_years}.**\n"
                        ]

                        # Add trending topics/keywords (service returns 'trends', not 'trending_keywords')
                        trends = trending_data.get('trends') or trending_data.get('trending_keywords', [])
                        if trends:
                            research_parts.append(f"### Current Trending Topics ({month_year}):")
                            for kw in trends[:10]:
                                research_parts.append(f"- {kw}")

                        # Add articles with real data - Session 523: Include URLs for citation
                        articles = trending_data.get('articles', [])
                        if articles:
                            research_parts.append(f"\n### Latest Articles ({len(articles)} found) - ALL FROM {year}:")
                            research_parts.append("**CITE THESE SOURCES in your content!**\n")
                            for i, article in enumerate(articles[:8], 1):
                                title = article.get('title', 'Unknown')
                                source = article.get('source', 'Unknown')
                                url = article.get('url', article.get('link', ''))
                                pub_date = article.get('published', '')
                                summary = article.get('summary', article.get('content', ''))[:200]
                                date_str = f" - Published: {pub_date[:10]}" if pub_date else ""

                                # Session 523: Include URL for source citation
                                research_parts.append(f"\n**{i}. {title}**")
                                research_parts.append(f"   Source: {source}{date_str}")
                                if url and not url.startswith('internal'):
                                    research_parts.append(f"   URL: {url}")
                                if summary:
                                    research_parts.append(f"   Summary: {summary}...")

                        # Add categories matched
                        if trending_data.get('categories'):
                            research_parts.append(f"\n### Relevant Categories: {', '.join(trending_data['categories'])}")

                        research = "\n".join(research_parts)
                        logger.info(f"📊 Session 521: Built {len(research)} chars of research from spider data")
                        logger.info(f"📊 Found {len(articles)} articles, {len(trends) if trends else 0} trends")

                except Exception as e:
                    logger.warning(f"⚠️ Session 521: Spider data fetch failed: {e}")
                    # Continue without spider data

            # Get current project if not provided
            project_id = arguments.get('project_id')
            if not project_id:
                current_project = getattr(self, 'project', None)
                if current_project:
                    project_id = str(current_project.id)

            # Create agent instance
            agent = ContentWriterAgent(
                user=self.user,
                project_id=project_id
            )

            # Build context
            context = {
                'content_type': content_type,
                'research': research,
                'tone': tone,
                'target_audience': target_audience,
                'word_count': word_count,
                'task': task,
            }

            logger.info(f"🎯 Writing {content_type}: {task}")
            logger.info(f"📝 Research context length: {len(research)} chars")

            # Session 523: Fetch scifi context (mood, evolution, memories) for intelligent prompting
            scifi_context = {}
            try:
                if SUPER_PLATFORM_AVAILABLE:
                    scifi_service = get_scifi_integration_service()
                    if scifi_service:
                        scifi_result = scifi_service.get_scifi_context(
                            agent_name='ContentWriterAgent',
                            task=task,
                            user=self.user
                        )
                        if scifi_result and hasattr(scifi_result, 'to_dict'):
                            scifi_context = scifi_result.to_dict()
                        elif isinstance(scifi_result, dict):
                            scifi_context = scifi_result
                        logger.info(f"🎭 Session 523: Fetched scifi context: mood={scifi_context.get('mood', {}).get('name', 'none')}")
            except Exception as e:
                logger.debug(f"Could not fetch scifi context: {e}")

            # Execute content writing
            from core.services.priority.enforce import check_priority, log_decision  # Session 1086 PR 3c
            _pd = check_priority('ContentWriterAgent', trigger_source='user_chat'); log_decision(_pd, 'ContentWriterAgent')
            result = agent.execute(
                task=task or f"Write {content_type}",
                context=context,
                scifi_context=scifi_context,
                spider_context=spider_context
            )

            # Session 496: Convert AgentResult to dict with proper structure for frontend
            # Must match pattern from CompetitorAnalysisAgent for proper display
            if result.success:
                content_data = result.data.get('content', {})
                full_text = content_data.get('full_text', '') if isinstance(content_data, dict) else str(content_data)

                # Build response with proper structure for frontend
                response = {
                    'success': True,
                    'message': result.message,
                    'delegated_to': 'ContentWriterAgent',  # Session 496: For SuperPlatformCoordinator
                    'agents_used': ['ContentWriterAgent'],  # Session 496: Include agent tracking
                    'metadata': {
                        'agent_result': {
                            'success': result.success,
                            'message': result.message,
                            'data': result.data,  # Contains {content, metadata}
                            'agent_name': result.agent_name,
                            'execution_time_ms': result.execution_time_ms,
                            'decisions_made': result.decisions_made,
                            'tool_calls': getattr(result, 'tool_calls', [])
                        }
                    },
                    'content_type': content_type,
                    'content': content_data,
                    'full_text': full_text,
                    'data': result.data  # Also at top level for legacy compatibility
                }

                logger.info(f"📝 Returning success response with {content_type}")
                logger.info(f"📝 Full text length: {len(full_text)} chars")
                return response
            else:
                logger.error(f"📝 Agent returned failure: {result.error}")
                return {
                    'success': False,
                    'error': result.error or 'Content writing failed'
                }

        except Exception as e:
            logger.error(f"❌ Content writer agent error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    # Session 128: Updated to use Audio Generation Agent
    def _handle_goal_collection(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Handle goal collection flow for users who haven't set goals.

        Session 878: Users need goals for the PA to personalize advice effectively.
        This method handles:
        1. Detecting if goals are needed
        2. Prompting for goals
        3. Extracting and saving goals from user responses

        Args:
            message: The user's current message

        Returns:
            Response dict if goal collection is handled, None to continue normal processing
        """
        try:
            # Check if user already has goals
            if self.enhanced_profile.long_term_goals and len(self.enhanced_profile.long_term_goals) > 0:
                # User has goals - clear any pending goal collection state
                if self.enhanced_profile.dynamic_attributes and self.enhanced_profile.dynamic_attributes.get('goals_collection_pending'):
                    self.enhanced_profile.dynamic_attributes['goals_collection_pending'] = False
                    self.enhanced_profile.save()
                return None

            # Get or initialize dynamic_attributes
            dynamic_attrs = self.enhanced_profile.dynamic_attributes or {}

            # Check if we're waiting for a goal response
            if dynamic_attrs.get('goals_collection_pending'):
                # Check if user wants to skip instead of providing goals
                skip_keywords = ['skip', 'later', 'not now', 'no thanks', 'pass', "don't want to", "i'll pass"]
                if any(kw in message.lower() for kw in skip_keywords):
                    # User wants to skip goal setting
                    dynamic_attrs['goals_collection_pending'] = False
                    dynamic_attrs['goals_collection_skipped'] = True
                    dynamic_attrs['goals_collection_skipped_at'] = datetime.now().isoformat()
                    self.enhanced_profile.dynamic_attributes = dynamic_attrs
                    self.enhanced_profile.save()
                    logger.info(f"Session 878: User {self.user.username} skipped goal collection")
                    return None

                # User is responding to our goal question - try to extract goals
                extracted_goals = self._extract_goals_from_response(message)

                if extracted_goals:
                    # Save the goals
                    self.enhanced_profile.long_term_goals = extracted_goals
                    self.enhanced_profile.dynamic_attributes = dynamic_attrs
                    self.enhanced_profile.dynamic_attributes['goals_collection_pending'] = False
                    self.enhanced_profile.dynamic_attributes['goals_collected_at'] = datetime.now().isoformat()
                    self.enhanced_profile.save()

                    logger.info(f"Session 878: Saved {len(extracted_goals)} goals for user {self.user.username}")

                    # Return a confirmation and continue to help them
                    return {
                        'response': f"Thanks for sharing your goals! I've noted:\n\n" +
                                   "\n".join([f"- {goal}" for goal in extracted_goals]) +
                                   "\n\nI'll keep these in mind to help you more effectively. What would you like to work on today?",
                        'success': True,
                        'confidence': 0.95,
                        'type': 'goal_collection_complete',
                        'goals_saved': extracted_goals
                    }
                else:
                    # Couldn't extract clear goals, ask for clarification
                    return {
                        'response': "I want to make sure I understand your goals correctly. "
                                   "Could you list 2-3 specific things you want to achieve? "
                                   "For example:\n"
                                   "- Build a side income of $2000/month\n"
                                   "- Learn Python and get a developer job\n"
                                   "- Launch my startup idea",
                        'success': True,
                        'confidence': 0.9,
                        'type': 'goal_collection_clarification'
                    }

            # Check if we should ask for goals (first time)
            # Only ask if: no goals, haven't asked recently, and not a skip keyword in message
            skip_keywords = ['skip', 'later', 'not now', 'no thanks', 'pass']
            if any(kw in message.lower() for kw in skip_keywords):
                # User wants to skip goal setting
                dynamic_attrs['goals_collection_skipped'] = True
                dynamic_attrs['goals_collection_skipped_at'] = datetime.now().isoformat()
                self.enhanced_profile.dynamic_attributes = dynamic_attrs
                self.enhanced_profile.save()
                logger.info(f"Session 878: User {self.user.username} skipped goal collection")
                return None

            # Check if we've asked before and were skipped
            if dynamic_attrs.get('goals_collection_skipped'):
                # Don't keep asking if they skipped
                return None

            # Check if we've recently asked (within last 24 hours)
            last_asked = dynamic_attrs.get('goals_collection_last_asked')
            if last_asked:
                try:
                    last_asked_time = datetime.fromisoformat(last_asked)
                    if (datetime.now() - last_asked_time).total_seconds() < 86400:  # 24 hours
                        return None
                except (ValueError, TypeError):
                    pass

            # First interaction without goals - ask for them
            dynamic_attrs['goals_collection_pending'] = True
            dynamic_attrs['goals_collection_last_asked'] = datetime.now().isoformat()
            self.enhanced_profile.dynamic_attributes = dynamic_attrs
            self.enhanced_profile.save()

            logger.info(f"Session 878: Asking user {self.user.username} to set goals")

            return {
                'response': f"Hi {self.user.first_name or self.user.username}! To help you most effectively, "
                           "I'd love to know what you're working toward.\n\n"
                           "**What are your top 2-3 goals right now?**\n\n"
                           "They could be anything - career goals, learning goals, income targets, or personal projects. "
                           "For example:\n"
                           "- Increase my freelance income to $5k/month\n"
                           "- Build and launch a SaaS product\n"
                           "- Transition into a data science role\n\n"
                           "(Type 'skip' if you'd rather set goals later)",
                'success': True,
                'confidence': 0.95,
                'type': 'goal_collection_prompt',
                'suggestions': [
                    {'text': 'Set my goals', 'action': 'Tell me your goals'},
                    {'text': 'Skip for now', 'action': 'skip'}
                ]
            }

        except Exception as e:
            logger.error(f"Session 878: Error in goal collection: {e}")
            return None

    def _handle_interview_trigger(self, message: str) -> Optional[Dict[str, Any]]:
        """
        Handle interview triggering for users with incomplete profiles.

        Session 882: PA should automatically prompt new users to complete
        the interview to build their profile for personalization.

        Args:
            message: The user's current message

        Returns:
            Response dict if interview prompt is handled, None to continue normal processing
        """
        try:
            # Calculate profile completeness
            completeness = self.enhanced_profile.calculate_completeness()

            # If profile is reasonably complete (>= 30%), no need for interview
            if completeness >= 30:
                return None

            # Get or initialize dynamic_attributes
            dynamic_attrs = self.enhanced_profile.dynamic_attributes or {}

            # Check if user has already completed an interview
            interview_state = dynamic_attrs.get('interview_state', {})
            if interview_state.get('completion_percentage', 0) >= 80:
                return None

            # Check if user has skipped interview
            if dynamic_attrs.get('interview_skipped'):
                # Check if enough time has passed (7 days) to ask again
                skipped_at = dynamic_attrs.get('interview_skipped_at')
                if skipped_at:
                    try:
                        skipped_time = datetime.fromisoformat(skipped_at)
                        days_since_skip = (datetime.now() - skipped_time).days
                        if days_since_skip < 7:
                            return None
                    except (ValueError, TypeError):
                        pass

            # Check if we're currently prompting for interview
            if dynamic_attrs.get('interview_prompt_pending'):
                # Check user's response to the interview prompt
                message_lower = message.lower()

                # User wants to start interview
                start_keywords = ['yes', 'sure', 'ok', 'okay', 'start', 'let\'s do it', 'ready', 'begin', 'go ahead', 'sounds good']
                if any(kw in message_lower for kw in start_keywords):
                    # Clear the pending flag
                    dynamic_attrs['interview_prompt_pending'] = False
                    self.enhanced_profile.dynamic_attributes = dynamic_attrs
                    self.enhanced_profile.save()

                    logger.info(f"Session 882: User {self.user.username} agreed to start interview")

                    return {
                        'response': "Let's get to know you better! I'll ask you a few questions about "
                                   "your skills, experience, and goals. This will help me find the best "
                                   "opportunities for you.\n\n"
                                   "**To begin, please click the button below or visit the Interview page.**",
                        'success': True,
                        'confidence': 0.95,
                        'type': 'interview_start',
                        'action': 'start_interview',
                        'suggestions': [
                            {'text': 'Start Interview', 'action': 'start_interview', 'url': '/api/interview/start/'},
                            {'text': 'Skip for now', 'action': 'skip_interview'}
                        ]
                    }

                # User wants to skip
                skip_keywords = ['skip', 'later', 'not now', 'no thanks', 'pass', 'maybe later', 'no']
                if any(kw in message_lower for kw in skip_keywords):
                    dynamic_attrs['interview_prompt_pending'] = False
                    dynamic_attrs['interview_skipped'] = True
                    dynamic_attrs['interview_skipped_at'] = datetime.now().isoformat()
                    self.enhanced_profile.dynamic_attributes = dynamic_attrs
                    self.enhanced_profile.save()

                    logger.info(f"Session 882: User {self.user.username} skipped interview")
                    return None  # Continue normal processing

                # User responded with something else - they may be ignoring the prompt
                # Don't force the interview, just continue normal processing
                return None

            # Check if we've recently prompted (within last 24 hours)
            last_prompted = dynamic_attrs.get('interview_last_prompted')
            if last_prompted:
                try:
                    last_prompted_time = datetime.fromisoformat(last_prompted)
                    if (datetime.now() - last_prompted_time).total_seconds() < 86400:  # 24 hours
                        return None
                except (ValueError, TypeError):
                    pass

            # New user with incomplete profile - prompt for interview
            dynamic_attrs['interview_prompt_pending'] = True
            dynamic_attrs['interview_last_prompted'] = datetime.now().isoformat()
            self.enhanced_profile.dynamic_attributes = dynamic_attrs
            self.enhanced_profile.save()

            logger.info(f"Session 882: Prompting user {self.user.username} to complete interview (completeness: {completeness:.0f}%)")

            user_name = self.user.first_name or self.user.username

            return {
                'response': f"Hi {user_name}! Welcome to your Personal AI Assistant. 👋\n\n"
                           f"I noticed your profile is only {completeness:.0f}% complete. "
                           "To help you find the best income opportunities and give you personalized advice, "
                           "I'd love to learn more about you.\n\n"
                           "**Would you like to complete a quick interview?** (Takes about 5-10 minutes)\n\n"
                           "I'll ask about your skills, experience, and goals so I can match you with "
                           "opportunities that fit your unique situation.\n\n"
                           "(Say 'yes' to start, or 'skip' if you'd rather do this later)",
                'success': True,
                'confidence': 0.95,
                'type': 'interview_prompt',
                'profile_completeness': completeness,
                'suggestions': [
                    {'text': 'Yes, let\'s do it!', 'action': 'yes'},
                    {'text': 'Skip for now', 'action': 'skip'}
                ]
            }

        except Exception as e:
            logger.error(f"Session 882: Error in interview trigger: {e}")
            return None

    # Session 122: Asset Tracking Methods for Intelligent Chaining
    def _handle_opportunity_manager_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle opportunity queries and management."""
        from core.models_unified_system import Opportunity
        from django.db.models import Avg, Count

        action = arguments.get('action', 'list')

        try:
            if action == 'list':
                # Build query with filters
                queryset = Opportunity.objects.filter(user=self.user)

                if arguments.get('status'):
                    queryset = queryset.filter(status=arguments['status'])
                if arguments.get('category'):
                    queryset = queryset.filter(opportunity_type=arguments['category'])
                if arguments.get('min_score'):
                    queryset = queryset.filter(match_score__gte=arguments['min_score'])

                limit = arguments.get('limit', 10)
                opportunities = queryset.order_by('-match_score', '-created_at')[:limit]

                return {
                    'success': True,
                    'action': 'list',
                    'count': queryset.count(),
                    'showing': len(opportunities),
                    'opportunities': [
                        {
                            'id': str(opp.id),
                            'title': opp.title,
                            'type': opp.opportunity_type,
                            'source': opp.source,
                            'potential_revenue': float(opp.potential_revenue),
                            'match_score': opp.match_score,
                            'status': opp.status,
                            'created_at': opp.created_at.isoformat() if opp.created_at else None,
                            'has_task': hasattr(opp, 'task')
                        }
                        for opp in opportunities
                    ]
                }

            elif action == 'get':
                opp_id = arguments.get('opportunity_id')
                if not opp_id:
                    return {'success': False, 'error': 'opportunity_id required'}

                try:
                    opp = Opportunity.objects.get(id=opp_id, user=self.user)
                except Opportunity.DoesNotExist:
                    return {'success': False, 'error': f'Opportunity {opp_id} not found'}

                # Get related task if exists
                task_info = None
                if hasattr(opp, 'task'):
                    task = opp.task
                    task_info = {
                        'id': str(task.id),
                        'status': task.status,
                        'priority': task.priority,
                        'primary_agent': task.primary_agent.name if task.primary_agent else None
                    }

                return {
                    'success': True,
                    'action': 'get',
                    'opportunity': {
                        'id': str(opp.id),
                        'title': opp.title,
                        'type': opp.opportunity_type,
                        'source': opp.source,
                        'potential_revenue': float(opp.potential_revenue),
                        'hourly_rate': float(opp.hourly_rate) if opp.hourly_rate else None,
                        'match_score': opp.match_score,
                        'status': opp.status,
                        'recommended_by': opp.recommended_by.name if opp.recommended_by else None,
                        'created_at': opp.created_at.isoformat() if opp.created_at else None,
                        'task': task_info
                    }
                }

            elif action == 'stats':
                queryset = Opportunity.objects.filter(user=self.user)

                stats = queryset.aggregate(
                    total_count=Count('id'),
                    avg_score=Avg('match_score'),
                    avg_revenue=Avg('potential_revenue')
                )

                # Count by status
                status_counts = {}
                for status, _ in Opportunity._meta.get_field('status').choices:
                    status_counts[status] = queryset.filter(status=status).count()

                return {
                    'success': True,
                    'action': 'stats',
                    'stats': {
                        'total_opportunities': stats['total_count'],
                        'average_match_score': round(stats['avg_score'] or 0, 1),
                        'average_potential_revenue': round(float(stats['avg_revenue'] or 0), 2),
                        'by_status': status_counts
                    }
                }

            elif action == 'search':
                query = arguments.get('query', '')
                if not query:
                    return {'success': False, 'error': 'query required for search'}

                opportunities = Opportunity.objects.filter(
                    user=self.user,
                    title__icontains=query
                )[:10]

                return {
                    'success': True,
                    'action': 'search',
                    'query': query,
                    'results': [
                        {
                            'id': str(opp.id),
                            'title': opp.title,
                            'match_score': opp.match_score,
                            'status': opp.status
                        }
                        for opp in opportunities
                    ]
                }

            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error in opportunity_manager_tool: {e}")
            return {'success': False, 'error': str(e)}

    def _handle_task_manager_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle OpportunityTask management."""
        from core.models_unified_system import OpportunityTask
        from django.utils import timezone

        action = arguments.get('action', 'list')

        try:
            if action == 'list':
                queryset = OpportunityTask.objects.filter(user=self.user)

                if arguments.get('status'):
                    queryset = queryset.filter(status=arguments['status'])
                if arguments.get('priority'):
                    queryset = queryset.filter(priority=arguments['priority'])

                limit = arguments.get('limit', 10)
                tasks = queryset.order_by('-opportunity_score', '-created_at')[:limit]

                return {
                    'success': True,
                    'action': 'list',
                    'count': queryset.count(),
                    'tasks': [
                        {
                            'id': str(task.id),
                            'title': task.title,
                            'status': task.status,
                            'priority': task.priority,
                            'opportunity_score': task.opportunity_score,
                            'opportunity_id': str(task.opportunity_id),
                            'primary_agent': task.primary_agent.name if task.primary_agent else None,
                            'due_date': task.due_date.isoformat() if task.due_date else None
                        }
                        for task in tasks
                    ]
                }

            elif action == 'get':
                task_id = arguments.get('task_id')
                if not task_id:
                    return {'success': False, 'error': 'task_id required'}

                try:
                    task = OpportunityTask.objects.select_related('opportunity', 'primary_agent').get(
                        id=task_id, user=self.user
                    )
                except OpportunityTask.DoesNotExist:
                    return {'success': False, 'error': f'Task {task_id} not found'}

                return {
                    'success': True,
                    'action': 'get',
                    'task': {
                        'id': str(task.id),
                        'title': task.title,
                        'description': task.description,
                        'status': task.status,
                        'priority': task.priority,
                        'opportunity_score': task.opportunity_score,
                        'score_breakdown': task.score_breakdown,
                        'action_items': task.action_items,
                        'user_notes': task.user_notes,
                        'opportunity': {
                            'id': str(task.opportunity.id),
                            'title': task.opportunity.title,
                            'potential_revenue': float(task.opportunity.potential_revenue)
                        },
                        'primary_agent': task.primary_agent.name if task.primary_agent else None,
                        'assigned_agents': [a.name for a in task.assigned_agents.all()],
                        'created_at': task.created_at.isoformat(),
                        'accepted_at': task.accepted_at.isoformat() if task.accepted_at else None,
                        'applied_at': task.applied_at.isoformat() if task.applied_at else None
                    }
                }

            elif action == 'accept':
                task_id = arguments.get('task_id')
                if not task_id:
                    return {'success': False, 'error': 'task_id required'}

                try:
                    task = OpportunityTask.objects.get(id=task_id, user=self.user)
                except OpportunityTask.DoesNotExist:
                    return {'success': False, 'error': f'Task {task_id} not found'}

                task.status = 'accepted'
                task.accepted_at = timezone.now()
                task.save()

                return {
                    'success': True,
                    'action': 'accept',
                    'message': f'Task "{task.title}" accepted',
                    'task_id': str(task.id)
                }

            elif action == 'start':
                task_id = arguments.get('task_id')
                if not task_id:
                    return {'success': False, 'error': 'task_id required'}

                try:
                    task = OpportunityTask.objects.get(id=task_id, user=self.user)
                except OpportunityTask.DoesNotExist:
                    return {'success': False, 'error': f'Task {task_id} not found'}

                task.status = 'in_progress'
                task.save()

                return {
                    'success': True,
                    'action': 'start',
                    'message': f'Task "{task.title}" started',
                    'task_id': str(task.id)
                }

            elif action == 'apply':
                task_id = arguments.get('task_id')
                if not task_id:
                    return {'success': False, 'error': 'task_id required'}

                try:
                    task = OpportunityTask.objects.get(id=task_id, user=self.user)
                except OpportunityTask.DoesNotExist:
                    return {'success': False, 'error': f'Task {task_id} not found'}

                task.status = 'applied'
                task.applied_at = timezone.now()
                task.save()

                # Update opportunity status too
                task.opportunity.status = 'applied'
                task.opportunity.save()

                return {
                    'success': True,
                    'action': 'apply',
                    'message': f'Marked as applied: "{task.title}"',
                    'task_id': str(task.id)
                }

            elif action == 'complete':
                task_id = arguments.get('task_id')
                outcome = arguments.get('outcome', 'won')  # 'won' or 'lost'

                if not task_id:
                    return {'success': False, 'error': 'task_id required'}

                try:
                    task = OpportunityTask.objects.get(id=task_id, user=self.user)
                except OpportunityTask.DoesNotExist:
                    return {'success': False, 'error': f'Task {task_id} not found'}

                task.status = outcome
                task.completed_at = timezone.now()
                task.save()

                # Update opportunity status
                task.opportunity.status = 'accepted' if outcome == 'won' else 'rejected'
                task.opportunity.save()

                return {
                    'success': True,
                    'action': 'complete',
                    'outcome': outcome,
                    'message': f'Task "{task.title}" marked as {outcome}',
                    'task_id': str(task.id)
                }

            elif action == 'add_note':
                task_id = arguments.get('task_id')
                note = arguments.get('note', '')

                if not task_id:
                    return {'success': False, 'error': 'task_id required'}
                if not note:
                    return {'success': False, 'error': 'note required'}

                try:
                    task = OpportunityTask.objects.get(id=task_id, user=self.user)
                except OpportunityTask.DoesNotExist:
                    return {'success': False, 'error': f'Task {task_id} not found'}

                # Append note with timestamp
                timestamp = timezone.now().strftime('%Y-%m-%d %H:%M')
                if task.user_notes:
                    task.user_notes += f"\n\n[{timestamp}] {note}"
                else:
                    task.user_notes = f"[{timestamp}] {note}"
                task.save()

                return {
                    'success': True,
                    'action': 'add_note',
                    'message': 'Note added to task',
                    'task_id': str(task.id)
                }

            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error in task_manager_tool: {e}")
            return {'success': False, 'error': str(e)}

    def _handle_pipeline_orchestrator_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle manual pipeline execution and status checks."""
        from core.models_unified_system import OpportunityTask
        from core.agent_router import AgentRouter
        from django.utils import timezone
        from datetime import timedelta

        action = arguments.get('action', 'status')

        try:
            if action == 'execute_task':
                task_id = arguments.get('task_id')
                if not task_id:
                    return {'success': False, 'error': 'task_id required'}

                try:
                    task = OpportunityTask.objects.select_related('opportunity', 'primary_agent').get(
                        id=task_id, user=self.user
                    )
                except OpportunityTask.DoesNotExist:
                    return {'success': False, 'error': f'Task {task_id} not found'}

                if not task.primary_agent:
                    return {'success': False, 'error': 'No agent assigned to this task'}

                # Execute via AgentRouter
                router = AgentRouter()
                result = router.execute_agent(
                    agent_name=task.primary_agent.name,
                    task=f"Help with opportunity: {task.opportunity.title}. Details: {task.description}",
                    context={
                        'opportunity_id': str(task.opportunity.id),
                        'task_id': str(task.id),
                        'potential_revenue': float(task.opportunity.potential_revenue),
                        'user_id': str(self.user.id)
                    }
                )

                # Update task status
                task.status = 'in_progress'
                task.metadata['last_agent_execution'] = {
                    'agent': task.primary_agent.name,
                    'timestamp': timezone.now().isoformat(),
                    'result_preview': str(result)[:500] if result else None
                }
                task.save()

                return {
                    'success': True,
                    'action': 'execute_task',
                    'task_id': str(task.id),
                    'agent_executed': task.primary_agent.name,
                    'result': result
                }

            elif action == 'execute_opportunity':
                opp_id = arguments.get('opportunity_id')
                if not opp_id:
                    return {'success': False, 'error': 'opportunity_id required'}

                from core.models_unified_system import Opportunity
                try:
                    opp = Opportunity.objects.get(id=opp_id, user=self.user)
                except Opportunity.DoesNotExist:
                    return {'success': False, 'error': f'Opportunity {opp_id} not found'}

                # Check if task exists
                if not hasattr(opp, 'task'):
                    return {
                        'success': False,
                        'error': 'No task exists for this opportunity. Tasks are created for opportunities with score >= 70.'
                    }

                # Redirect to execute_task
                return self._handle_pipeline_orchestrator_tool({
                    'action': 'execute_task',
                    'task_id': str(opp.task.id)
                })

            elif action == 'status':
                # Get pipeline status overview
                pending_tasks = OpportunityTask.objects.filter(
                    user=self.user,
                    status='pending'
                ).count()

                in_progress = OpportunityTask.objects.filter(
                    user=self.user,
                    status='in_progress'
                ).count()

                recently_completed = OpportunityTask.objects.filter(
                    user=self.user,
                    status__in=['won', 'lost'],
                    completed_at__gte=timezone.now() - timedelta(days=7)
                ).count()

                return {
                    'success': True,
                    'action': 'status',
                    'pipeline_status': {
                        'pending_tasks': pending_tasks,
                        'in_progress': in_progress,
                        'completed_last_7_days': recently_completed,
                        'automated_execution': 'Every 30 minutes at :15 and :45'
                    }
                }

            elif action == 'queue':
                # Show next tasks to be executed
                tasks = OpportunityTask.objects.filter(
                    user=self.user,
                    status__in=['pending', 'accepted']
                ).select_related('opportunity', 'primary_agent').order_by(
                    '-opportunity_score'
                )[:5]

                return {
                    'success': True,
                    'action': 'queue',
                    'next_in_queue': [
                        {
                            'task_id': str(t.id),
                            'title': t.title,
                            'score': t.opportunity_score,
                            'status': t.status,
                            'agent': t.primary_agent.name if t.primary_agent else 'Unassigned'
                        }
                        for t in tasks
                    ]
                }

            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error in pipeline_orchestrator_tool: {e}")
            return {'success': False, 'error': str(e)}

    def _handle_revenue_tracker_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle revenue logging and ML feedback loop."""
        from core.models_unified_system import OpportunityRevenue, Opportunity
        from django.db.models import Sum, Avg, Count
        from django.utils import timezone
        from decimal import Decimal

        action = arguments.get('action', 'stats')

        try:
            if action == 'log_revenue':
                opp_id = arguments.get('opportunity_id')
                amount = arguments.get('amount')

                if not opp_id:
                    return {'success': False, 'error': 'opportunity_id required'}
                if not amount:
                    return {'success': False, 'error': 'amount required'}

                try:
                    opp = Opportunity.objects.get(id=opp_id, user=self.user)
                except Opportunity.DoesNotExist:
                    return {'success': False, 'error': f'Opportunity {opp_id} not found'}

                # Calculate fees and net
                platform_fee = arguments.get('platform_fee', 0)
                net_amount = Decimal(str(amount)) - Decimal(str(platform_fee))

                # Create revenue record
                revenue = OpportunityRevenue.objects.create(
                    opportunity=opp,
                    user=self.user,
                    amount=Decimal(str(amount)),
                    currency=arguments.get('currency', 'USD'),
                    platform_fee=Decimal(str(platform_fee)),
                    net_amount=net_amount,
                    platform=arguments.get('platform', 'direct'),
                    content_type=arguments.get('content_type', 'service'),
                    notes=arguments.get('notes', '')
                )

                # Update opportunity status
                opp.status = 'accepted'
                opp.save()

                # Update task if exists
                if hasattr(opp, 'task'):
                    opp.task.status = 'won'
                    opp.task.completed_at = timezone.now()
                    opp.task.save()

                return {
                    'success': True,
                    'action': 'log_revenue',
                    'revenue_id': str(revenue.id),
                    'amount': float(amount),
                    'net_amount': float(net_amount),
                    'message': f'Revenue of ${amount} logged for "{opp.title}"'
                }

            elif action == 'list_revenue':
                limit = arguments.get('limit', 10)
                revenues = OpportunityRevenue.objects.filter(
                    user=self.user
                ).select_related('opportunity').order_by('-created_at')[:limit]

                return {
                    'success': True,
                    'action': 'list_revenue',
                    'revenues': [
                        {
                            'id': str(r.id),
                            'opportunity_title': r.opportunity.title,
                            'amount': float(r.amount),
                            'net_amount': float(r.net_amount),
                            'platform': r.platform,
                            'status': r.status,
                            'created_at': r.created_at.isoformat()
                        }
                        for r in revenues
                    ]
                }

            elif action == 'stats':
                revenues = OpportunityRevenue.objects.filter(user=self.user)

                stats = revenues.aggregate(
                    total_gross=Sum('amount'),
                    total_net=Sum('net_amount'),
                    total_fees=Sum('platform_fee'),
                    count=Count('id'),
                    avg_amount=Avg('amount')
                )

                # Calculate this month
                from datetime import datetime
                month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                month_stats = revenues.filter(created_at__gte=month_start).aggregate(
                    month_gross=Sum('amount'),
                    month_net=Sum('net_amount'),
                    month_count=Count('id')
                )

                return {
                    'success': True,
                    'action': 'stats',
                    'revenue_stats': {
                        'total_gross': float(stats['total_gross'] or 0),
                        'total_net': float(stats['total_net'] or 0),
                        'total_fees': float(stats['total_fees'] or 0),
                        'transaction_count': stats['count'],
                        'average_transaction': float(stats['avg_amount'] or 0),
                        'this_month': {
                            'gross': float(month_stats['month_gross'] or 0),
                            'net': float(month_stats['month_net'] or 0),
                            'transactions': month_stats['month_count']
                        }
                    }
                }

            elif action == 'accuracy':
                # Calculate ML prediction accuracy
                from core.models_unified_system import OpportunityTask

                # Get completed tasks with outcomes
                completed = OpportunityTask.objects.filter(
                    user=self.user,
                    status__in=['won', 'lost']
                ).values('status', 'opportunity_score')

                if not completed:
                    return {
                        'success': True,
                        'action': 'accuracy',
                        'message': 'Not enough data yet for accuracy calculation',
                        'accuracy': None
                    }

                # Calculate accuracy by comparing scores with outcomes
                won_scores = [t['opportunity_score'] for t in completed if t['status'] == 'won']
                lost_scores = [t['opportunity_score'] for t in completed if t['status'] == 'lost']

                avg_won_score = sum(won_scores) / len(won_scores) if won_scores else 0
                avg_lost_score = sum(lost_scores) / len(lost_scores) if lost_scores else 0

                return {
                    'success': True,
                    'action': 'accuracy',
                    'accuracy': {
                        'total_outcomes': len(list(completed)),
                        'wins': len(won_scores),
                        'losses': len(lost_scores),
                        'win_rate': len(won_scores) / len(list(completed)) * 100 if completed else 0,
                        'avg_winning_score': round(avg_won_score, 1),
                        'avg_losing_score': round(avg_lost_score, 1),
                        'score_differential': round(avg_won_score - avg_lost_score, 1),
                        'interpretation': 'Higher score differential = better ML prediction accuracy'
                    }
                }

            elif action == 'link_content':
                revenue_id = arguments.get('revenue_id')
                content_id = arguments.get('content_id')

                if not revenue_id or not content_id:
                    return {'success': False, 'error': 'revenue_id and content_id required'}

                try:
                    revenue = OpportunityRevenue.objects.get(id=revenue_id, user=self.user)
                except OpportunityRevenue.DoesNotExist:
                    return {'success': False, 'error': f'Revenue {revenue_id} not found'}

                # Update metadata with content link
                if not revenue.metadata:
                    revenue.metadata = {}
                revenue.metadata['linked_content_id'] = str(content_id)
                revenue.save()

                return {
                    'success': True,
                    'action': 'link_content',
                    'message': f'Content {content_id} linked to revenue record'
                }

            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error in revenue_tracker_tool: {e}")
            return {'success': False, 'error': str(e)}

    # =========================================================================
    # SESSION 683: ML ANALYSIS TOOL - AUTO-SELECT OPTIMAL ML MODELS
    # =========================================================================

    def _handle_ml_analysis(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle ml_analysis tool - auto-select optimal ML models for data analysis.

        Session 683: This tool allows GPT to invoke the Agent-Model Router's
        auto_route() method to analyze data using the best ML models.

        Features:
        - Auto-detects data type (time series, graph, text, anomaly, etc.)
        - Selects optimal models from 15+ available ML models
        - Returns predictions with confidence scores
        - Explains why models were selected
        """
        from core.services.agent_model_router import get_agent_model_router

        try:
            data = arguments.get('data', {})
            task_type_str = arguments.get('task_type', 'auto')
            analysis_goal = arguments.get('analysis_goal', '')
            max_models = arguments.get('max_models', 2)

            logger.info(f"🤖 ML Analysis: task_type={task_type_str}, max_models={max_models}")
            logger.info(f"   Data keys: {list(data.keys()) if isinstance(data, dict) else type(data)}")
            logger.info(f"   Goal: {analysis_goal}")

            # Get the Agent-Model Router
            router = get_agent_model_router()

            # Convert task type string to TaskType enum if not 'auto'
            task_hint = None
            if task_type_str != 'auto':
                try:
                    from ml.auto_selection import TaskType
                    task_hint = TaskType(task_type_str)
                except (ValueError, ImportError) as e:
                    logger.warning(f"Could not parse task_type '{task_type_str}': {e}")

            # Run auto-route with the data
            result = router.auto_route(
                data=data,
                task_hint=task_hint,
                max_models=max_models
            )

            # Format response for GPT
            response = {
                'success': result.success,
                'task_detected': result.auto_selection.get('task_type', 'unknown'),
                'models_used': result.models_used,
                'confidence': round(result.confidence, 2),
                'score': round(result.score, 4) if result.score else None,
                'analysis': result.explanation,
                'selection_reason': result.auto_selection.get('selection_reason', ''),
                'characteristics_detected': result.auto_selection.get('characteristics', []),
            }

            # Add prediction details if available
            if result.predictions:
                response['predictions'] = result.predictions

            logger.info(f"✅ ML Analysis complete: {response['task_detected']} -> {response['models_used']}")
            return response

        except Exception as e:
            logger.error(f"Error in ml_analysis: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'task_detected': 'error',
                'models_used': [],
                'analysis': f'ML analysis failed: {str(e)}'
            }

    # =========================================================================
    # SESSION 674: UNIVERSAL AGENT TOOL - CONNECTS PA TO ALL 42+ AGENTS
    # =========================================================================

    def _handle_universal_agent_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle universal agent invocation - routes ANY agent through AgentRouter.

        This single handler connects the PA (brain) to all 42 previously
        unreachable agents (organs), enabling:
        - Blockchain auditing
        - Stock analysis
        - Code generation/review (with SKIN layer workspace integration!)
        - Podcast creation
        - Market analysis
        - Narrative tracking
        - And more...

        Session 695: Development agents now write to workspace via SKIN layer.
        """
        from core.agent_router import AgentRouter, AgentNotFoundError

        agent_name = arguments.get('agent_name')
        task = arguments.get('task')
        context = arguments.get('context', {})
        # Session 695: Workspace options
        write_to_workspace = arguments.get('write_to_workspace', True)
        base_path = arguments.get('base_path', '')

        if not agent_name:
            return {'success': False, 'error': 'agent_name is required'}
        if not task:
            return {'success': False, 'error': 'task is required'}

        try:
            # Initialize router with user
            router = AgentRouter(user=self.user)

            # Validate agent exists
            if not router.is_valid_agent(agent_name):
                available = router.get_available_agents()
                return {
                    'success': False,
                    'error': f"Unknown agent: '{agent_name}'",
                    'available_agents': available[:20],  # Show first 20
                    'hint': "Use one of the available agent names exactly as shown"
                }

            # Session 695: SKIN Layer Integration for ALL agents
            # All agents inherit workspace methods from BaseAgent.
            # These agents are specifically enabled for workspace file writing.
            WORKSPACE_AWARE_AGENTS = [
                # Development Agents - Primary workspace users
                'FullStackDeveloperAgent',
                'CodeGeneratorAgent',
                'CodeReviewAgent',
                'DevOpsAgent',

                # Content Agents - Can write content files
                'ContentWriterAgent',
                'ContentStrategyAgent',
                'TechnicalDocumentAgent',

                # Strategy Agents - Can write strategy docs
                'BrandIdentityAgent',
                'SEOOptimizerAgent',
                'BrandStrategyAgent',
                'MarketingStrategyAgent',

                # Research Agents - Can write research reports
                'ResearchAgent',
                'CompetitorAnalysisAgent',
                'CustomerResearchAgent',
                'TrendAnalysisAgent',
                'MarketIntelligenceAgent',

                # Analysis Agents - Can write analysis reports
                'StockAnalystAgent',
                'OpportunityScoringAgent',

                # Legal Agents - Can write legal documents
                'LegalDocDrafterAgent',

                # System Agents - Can write system docs
                'SystemIntelligenceAgent',
            ]

            if agent_name in WORKSPACE_AWARE_AGENTS and write_to_workspace:
                logger.info(f"Universal Agent Tool: Using workspace-aware execution for {agent_name}")

                # Get the agent class directly
                agent_class = router.get_agent_class(agent_name)
                if agent_class and hasattr(agent_class, 'execute_with_workspace'):
                    agent_instance = agent_class(user=self.user)
                    result = agent_instance.execute_with_workspace(
                        task=task,
                        context=context,
                        user=self.user,
                        write_to_workspace=write_to_workspace,
                        base_path=base_path
                    )
                else:
                    # Fallback to standard routing
                    result = router.route(
                        agent_name=agent_name,
                        task=task,
                        context=context
                    )
            else:
                # Standard execution for non-workspace agents
                logger.info(f"Universal Agent Tool: Invoking {agent_name} for task: {task[:50]}...")
                result = router.route(
                    agent_name=agent_name,
                    task=task,
                    context=context
                )

            # Convert AgentResult to dict
            if result.success:
                response = {
                    'success': True,
                    'agent_name': result.agent_name,
                    'message': result.message,
                    'data': result.data,
                    'execution_time_ms': getattr(result, 'execution_time_ms', None)
                }
                # Session 695: Include workspace write info if available
                if result.data and 'workspace_write' in result.data:
                    response['workspace_write'] = result.data['workspace_write']
                return response
            else:
                return {
                    'success': False,
                    'agent_name': agent_name,
                    'error': result.error or 'Agent execution failed',
                    'message': result.message
                }

        except AgentNotFoundError as e:
            logger.error(f"Agent not found: {e}")
            return {
                'success': False,
                'error': str(e),
                'hint': "Check the agent name spelling. Use exact agent class names."
            }

        except Exception as e:
            logger.error(f"Error in universal_agent_tool: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'agent_name': agent_name
            }

    # =========================================================================
    # SESSION 695: SKIN LAYER - WORKSPACE TOOL FOR PROJECT EXECUTION
    # =========================================================================

    def _handle_workspace_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle workspace management - the SKIN layer where AI touches reality.

        This tool enables agents to:
        - Register and manage project workspaces
        - Write code to real files with full audit trail
        - Execute git operations
        - Rollback changes when needed
        """
        from core.services.workspace_manager import WorkspaceManager
        from core.models_skin_layer import ProjectWorkspace, WorkspaceOperation

        action = arguments.get('action')
        if not action:
            return {'success': False, 'error': 'action is required'}

        try:
            manager = WorkspaceManager(user=self.user)

            # ===== REGISTER =====
            if action == 'register':
                path = arguments.get('path')
                name = arguments.get('name')
                if not path:
                    return {'success': False, 'error': 'path is required for register action'}

                workspace = manager.register_workspace(root_path=path, name=name)
                return {
                    'success': True,
                    'message': f"Registered workspace: {workspace.name}",
                    'workspace': {
                        'id': str(workspace.id),
                        'name': workspace.name,
                        'path': workspace.root_path,
                        'is_active': workspace.is_active,
                        'tech_stack': workspace.tech_stack
                    }
                }

            # ===== LIST =====
            elif action == 'list':
                workspaces = ProjectWorkspace.objects.filter(user=self.user).order_by('-updated_at')
                return {
                    'success': True,
                    'workspaces': [
                        {
                            'id': str(w.id),
                            'name': w.name,
                            'path': w.root_path,
                            'is_active': w.is_active,
                            'tech_stack': w.tech_stack.get('frontend_framework', 'Unknown'),
                            'total_operations': w.total_operations
                        }
                        for w in workspaces
                    ],
                    'count': workspaces.count()
                }

            # ===== SET_ACTIVE =====
            elif action == 'set_active':
                name = arguments.get('name')
                workspace_id = arguments.get('workspace_id')
                if not name and not workspace_id:
                    return {'success': False, 'error': 'name or workspace_id required'}

                # Find workspace
                if workspace_id:
                    workspace = ProjectWorkspace.objects.filter(user=self.user, id=workspace_id).first()
                else:
                    workspace = ProjectWorkspace.objects.filter(user=self.user, name__icontains=name).first()

                if not workspace:
                    return {'success': False, 'error': f'Workspace not found: {name or workspace_id}'}

                # Deactivate all, activate this one
                ProjectWorkspace.objects.filter(user=self.user, is_active=True).update(is_active=False)
                workspace.is_active = True
                workspace.save()

                return {
                    'success': True,
                    'message': f"Activated workspace: {workspace.name}",
                    'workspace': {
                        'id': str(workspace.id),
                        'name': workspace.name,
                        'path': workspace.root_path
                    }
                }

            # ===== STATUS =====
            elif action == 'status':
                workspace = manager.get_active_workspace()
                if not workspace:
                    return {
                        'success': False,
                        'error': 'No active workspace. Use "register" or "set_active" first.',
                        'hint': 'Try: workspace_tool action="list" to see available workspaces'
                    }

                context = manager.get_workspace_context_for_agent(workspace, 'PersonalAssistant', 'status')
                return {
                    'success': True,
                    'workspace': {
                        'id': str(workspace.id),
                        'name': workspace.name,
                        'path': workspace.root_path,
                        'tech_stack': workspace.tech_stack,
                        'total_operations': workspace.total_operations,
                        'total_files_written': workspace.total_files_written,
                        'current_branch': workspace.current_branch
                    },
                    'context': context
                }

            # ===== SCAN =====
            elif action == 'scan':
                workspace_id = arguments.get('workspace_id')
                workspace = manager.get_active_workspace() if not workspace_id else \
                    ProjectWorkspace.objects.filter(user=self.user, id=workspace_id).first()

                if not workspace:
                    return {'success': False, 'error': 'No workspace to scan'}

                from core.services.workspace_manager import WorkspaceScanner
                scanner = WorkspaceScanner()
                context = scanner.scan_workspace(workspace)

                return {
                    'success': True,
                    'message': f"Scanned workspace: {workspace.name}",
                    'stats': {
                        'total_files': context.total_files,
                        'total_directories': context.total_directories,
                        'total_lines_of_code': context.total_lines_of_code,
                        'file_types': context.file_type_counts,
                        'scan_duration_ms': context.scan_duration_ms
                    }
                }

            # ===== WRITE =====
            elif action == 'write':
                path = arguments.get('path')
                content = arguments.get('content')
                agent_name = arguments.get('agent_name', 'PersonalAssistant')

                if not path:
                    return {'success': False, 'error': 'path is required for write action'}
                if content is None:
                    return {'success': False, 'error': 'content is required for write action'}

                workspace = manager.get_active_workspace()
                if not workspace:
                    return {'success': False, 'error': 'No active workspace'}

                operation = manager.write_file(workspace, path, content, agent_name)
                return {
                    'success': operation.success,
                    'message': f"{'Wrote' if operation.success else 'Failed to write'} {path}",
                    'operation_id': str(operation.id),
                    'file_path': operation.file_path,
                    'error': operation.error_message if not operation.success else None
                }

            # ===== READ =====
            elif action == 'read':
                path = arguments.get('path')
                if not path:
                    return {'success': False, 'error': 'path is required for read action'}

                workspace = manager.get_active_workspace()
                if not workspace:
                    return {'success': False, 'error': 'No active workspace'}

                import os
                full_path = os.path.join(workspace.root_path, path)
                if not os.path.exists(full_path):
                    return {'success': False, 'error': f'File not found: {path}'}

                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                return {
                    'success': True,
                    'file_path': path,
                    'content': content[:50000],  # Limit to 50k chars
                    'truncated': len(content) > 50000
                }

            # ===== GIT_STATUS =====
            elif action == 'git_status':
                workspace = manager.get_active_workspace()
                if not workspace:
                    return {'success': False, 'error': 'No active workspace'}

                from core.services.workspace_manager import GitIntegrator
                git = GitIntegrator()
                status = git.status(workspace)
                return {
                    'success': True,
                    'git_status': status
                }

            # ===== GIT_COMMIT =====
            elif action == 'git_commit':
                message = arguments.get('message')
                agent_name = arguments.get('agent_name', 'PersonalAssistant')
                if not message:
                    return {'success': False, 'error': 'message is required for git_commit'}

                workspace = manager.get_active_workspace()
                if not workspace:
                    return {'success': False, 'error': 'No active workspace'}

                operation = manager.git_commit(workspace, message, agent_name)
                return {
                    'success': operation.success,
                    'message': f"{'Committed' if operation.success else 'Failed to commit'}: {message[:50]}...",
                    'operation_id': str(operation.id),
                    'error': operation.error_message if not operation.success else None
                }

            # ===== GIT_BRANCH =====
            elif action == 'git_branch':
                branch_name = arguments.get('branch_name')
                agent_name = arguments.get('agent_name', 'PersonalAssistant')
                if not branch_name:
                    return {'success': False, 'error': 'branch_name is required'}

                workspace = manager.get_active_workspace()
                if not workspace:
                    return {'success': False, 'error': 'No active workspace'}

                from core.services.workspace_manager import GitIntegrator
                git = GitIntegrator()
                operation = git.create_branch(workspace, branch_name, self.user, agent_name)
                return {
                    'success': operation.success,
                    'message': f"{'Created branch' if operation.success else 'Failed'}: {branch_name}",
                    'operation_id': str(operation.id),
                    'error': operation.error_message if not operation.success else None
                }

            # ===== OPERATIONS =====
            elif action == 'operations':
                limit = arguments.get('limit', 10)
                workspace = manager.get_active_workspace()
                if not workspace:
                    return {'success': False, 'error': 'No active workspace'}

                ops = WorkspaceOperation.objects.filter(workspace=workspace).order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'operations': [
                        {
                            'id': str(op.id),
                            'type': op.operation_type,
                            'agent': op.agent_name,
                            'file_path': op.file_path,
                            'success': op.success,
                            'created_at': op.created_at.isoformat(),
                            'can_rollback': op.can_rollback and not op.rolled_back
                        }
                        for op in ops
                    ]
                }

            # ===== ROLLBACK =====
            elif action == 'rollback':
                operation_id = arguments.get('operation_id')
                if not operation_id:
                    return {'success': False, 'error': 'operation_id is required for rollback'}

                operation = WorkspaceOperation.objects.filter(id=operation_id, user=self.user).first()
                if not operation:
                    return {'success': False, 'error': f'Operation not found: {operation_id}'}

                rollback_op = manager.rollback_operation(operation)
                return {
                    'success': rollback_op.success,
                    'message': f"{'Rolled back' if rollback_op.success else 'Failed to rollback'} operation",
                    'rollback_operation_id': str(rollback_op.id),
                    'error': rollback_op.error_message if not rollback_op.success else None
                }

            else:
                return {
                    'success': False,
                    'error': f'Unknown action: {action}',
                    'valid_actions': [
                        'register', 'list', 'set_active', 'status', 'scan',
                        'write', 'read', 'git_status', 'git_commit', 'git_branch',
                        'operations', 'rollback'
                    ]
                }

        except Exception as e:
            logger.error(f"Error in workspace_tool: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'action': action
            }

    # =========================================================================
    # Session 709: Body Vitals Tools - Connect Brain to Body Systems
    # =========================================================================

    def _handle_get_body_vitals(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle get_body_vitals tool call.

        Query health status of all 7 body systems or specific systems.

        Args:
            arguments: Dict with optional 'systems' (list) and 'include_details' (bool)

        Returns:
            Unified health report with overall status and per-system breakdown
        """
        try:
            from core.services.body_vitals import get_body_vitals_service
            service = get_body_vitals_service()

            systems = arguments.get('systems', ['all'])
            include_details = arguments.get('include_details', False)

            # If 'all' or empty, get full vitals
            if not systems or 'all' in systems:
                vitals = service.get_all_vitals(include_details=include_details)
                return {
                    'success': True,
                    'tool': 'get_body_vitals',
                    **vitals
                }

            # Query specific systems
            result = {
                'success': True,
                'tool': 'get_body_vitals',
                'systems': {},
                'alerts': []
            }

            for system in systems:
                system_vitals = service.get_system_vitals(system, include_details=include_details)
                result['systems'][system] = system_vitals
                if system_vitals.get('alerts'):
                    result['alerts'].extend(system_vitals['alerts'])

            # Sort alerts by severity
            result['alerts'] = sorted(
                result['alerts'],
                key=lambda x: x.get('severity_score', 0),
                reverse=True
            )

            return result

        except Exception as e:
            logger.error(f"Error in get_body_vitals: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'tool': 'get_body_vitals'
            }

    def _handle_check_resource_budget(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle check_resource_budget tool call.

        Check if budget allows for an operation before executing.

        Args:
            arguments: Dict with optional 'estimated_tokens' (int) and 'estimated_cost' (float)

        Returns:
            Budget check result with can_proceed flag and recommendation
        """
        try:
            from core.services.body_vitals import get_body_vitals_service
            service = get_body_vitals_service()

            estimated_tokens = arguments.get('estimated_tokens', 0)
            estimated_cost = arguments.get('estimated_cost', 0)

            budget_check = service.check_budget(
                estimated_tokens=estimated_tokens,
                estimated_cost=estimated_cost
            )

            return {
                'success': True,
                'tool': 'check_resource_budget',
                **budget_check
            }

        except Exception as e:
            logger.error(f"Error in check_resource_budget: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'tool': 'check_resource_budget',
                # Default to allowing operation if check fails
                'can_proceed': True,
                'warning': f'Budget check failed: {str(e)}'
            }

    def _handle_get_system_alerts(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle get_system_alerts tool call.

        Get active alerts from all body systems above severity threshold.

        Args:
            arguments: Dict with optional 'severity_threshold' ('info', 'warning', 'critical')

        Returns:
            List of alerts sorted by severity
        """
        try:
            from core.services.body_vitals import get_body_vitals_service
            service = get_body_vitals_service()

            severity_threshold = arguments.get('severity_threshold', 'warning')

            alerts = service.get_alerts(severity_threshold=severity_threshold)

            return {
                'success': True,
                'tool': 'get_system_alerts',
                'severity_threshold': severity_threshold,
                'alert_count': len(alerts),
                'alerts': alerts,
                'message': f"{len(alerts)} alert(s) found at {severity_threshold} level or above" if alerts else "No alerts found"
            }

        except Exception as e:
            logger.error(f"Error in get_system_alerts: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'tool': 'get_system_alerts',
                'alerts': []
            }

    # =========================================================================
    # Session 725: Intelligence Tools - Connect Brain to Intelligence System
    # =========================================================================

    def _handle_predictions_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle predictions_tool - Query agent predictions from Intelligence system.

        Actions: list, get, stats, leaderboard, by_agent, by_category
        """
        try:
            from core.models_unified_system import AgentPrediction, Agent
            from django.db.models import Count, Avg

            action = arguments.get('action', 'list')
            limit = arguments.get('limit', 20)

            if action == 'list':
                # Get recent predictions
                predictions = AgentPrediction.objects.select_related('agent').order_by('-created_at')

                # Apply filters
                if arguments.get('status'):
                    predictions = predictions.filter(status=arguments['status'])
                if arguments.get('category'):
                    predictions = predictions.filter(category=arguments['category'])

                predictions = predictions[:limit]

                return {
                    'success': True,
                    'tool': 'predictions_tool',
                    'action': action,
                    'count': len(predictions),
                    'predictions': [
                        {
                            'id': str(p.id),
                            'title': p.title,
                            'prediction': p.prediction[:500] if p.prediction else '',
                            'category': p.category,
                            'status': p.status,
                            'confidence': p.confidence,
                            'agent_name': p.agent.name if p.agent else 'Unknown',
                            'created_at': p.created_at.isoformat() if p.created_at else None,
                        }
                        for p in predictions
                    ]
                }

            elif action == 'get':
                prediction_id = arguments.get('prediction_id')
                if not prediction_id:
                    return {'success': False, 'error': 'prediction_id required for get action'}

                try:
                    p = AgentPrediction.objects.select_related('agent').get(id=prediction_id)
                    return {
                        'success': True,
                        'tool': 'predictions_tool',
                        'prediction': {
                            'id': str(p.id),
                            'title': p.title,
                            'prediction': p.prediction,
                            'category': p.category,
                            'status': p.status,
                            'confidence': p.confidence,
                            'source': p.source,
                            'agent_name': p.agent.name if p.agent else 'Unknown',
                            'created_at': p.created_at.isoformat() if p.created_at else None,
                            'deadline': p.deadline.isoformat() if hasattr(p, 'deadline') and p.deadline else None,
                        }
                    }
                except AgentPrediction.DoesNotExist:
                    return {'success': False, 'error': f'Prediction {prediction_id} not found'}

            elif action == 'stats':
                total = AgentPrediction.objects.count()
                by_status = dict(AgentPrediction.objects.values('status').annotate(count=Count('id')).values_list('status', 'count'))
                by_category = dict(AgentPrediction.objects.values('category').annotate(count=Count('id')).values_list('category', 'count'))

                verified_true = by_status.get('verified_true', 0)
                verified_false = by_status.get('verified_false', 0)
                verified_total = verified_true + verified_false
                accuracy = (verified_true / verified_total * 100) if verified_total > 0 else 0

                return {
                    'success': True,
                    'tool': 'predictions_tool',
                    'action': 'stats',
                    'total_predictions': total,
                    'accuracy_rate': round(accuracy, 1),
                    'by_status': by_status,
                    'by_category': by_category,
                }

            elif action == 'leaderboard':
                # Agents ranked by prediction accuracy
                from django.db.models import Q
                agents_with_predictions = Agent.objects.filter(
                    predictions__status__in=['verified_true', 'verified_false']
                ).annotate(
                    total_verified=Count('predictions'),
                    correct=Count('predictions', filter=Q(predictions__status='verified_true'))
                ).order_by('-correct')[:limit]

                return {
                    'success': True,
                    'tool': 'predictions_tool',
                    'action': 'leaderboard',
                    'agents': [
                        {
                            'name': a.name,
                            'total_verified': a.total_verified,
                            'correct': a.correct,
                            'accuracy': round(a.correct / a.total_verified * 100, 1) if a.total_verified > 0 else 0
                        }
                        for a in agents_with_predictions
                    ]
                }

            elif action == 'by_agent':
                agent_id = arguments.get('agent_id')
                if not agent_id:
                    return {'success': False, 'error': 'agent_id required for by_agent action'}

                predictions = AgentPrediction.objects.filter(agent_id=agent_id).order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'tool': 'predictions_tool',
                    'action': 'by_agent',
                    'count': len(predictions),
                    'predictions': [
                        {
                            'id': str(p.id),
                            'title': p.title,
                            'category': p.category,
                            'status': p.status,
                            'confidence': p.confidence,
                        }
                        for p in predictions
                    ]
                }

            elif action == 'by_category':
                category = arguments.get('category')
                if not category:
                    return {'success': False, 'error': 'category required for by_category action'}

                predictions = AgentPrediction.objects.filter(category=category).order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'tool': 'predictions_tool',
                    'action': 'by_category',
                    'category': category,
                    'count': len(predictions),
                    'predictions': [
                        {
                            'id': str(p.id),
                            'title': p.title,
                            'status': p.status,
                            'agent_name': p.agent.name if p.agent else 'Unknown',
                        }
                        for p in predictions
                    ]
                }

            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error in predictions_tool: {e}", exc_info=True)
            return {'success': False, 'error': str(e), 'tool': 'predictions_tool'}

    def _handle_gates_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle gates_tool - Query pilot readiness gates from Intelligence system.

        Actions: list, get, stats, checklist, by_status, by_risk
        """
        try:
            from core.models_pilot_readiness import PilotReadinessGate, ChecklistItem
            from django.db.models import Count

            action = arguments.get('action', 'list')
            limit = arguments.get('limit', 20)

            if action == 'list':
                gates = PilotReadinessGate.objects.select_related('decision').order_by('-created_at')

                if arguments.get('status'):
                    gates = gates.filter(status=arguments['status'])
                if arguments.get('risk_level'):
                    gates = gates.filter(risk_level=arguments['risk_level'])

                gates = gates[:limit]

                return {
                    'success': True,
                    'tool': 'gates_tool',
                    'action': action,
                    'count': len(gates),
                    'gates': [
                        {
                            'id': str(g.id),
                            'status': g.status,
                            'risk_level': g.risk_level,
                            'summary': g.summary[:200] if g.summary else '',
                            'decision_title': g.decision.title if g.decision else 'Unknown',
                            'created_at': g.created_at.isoformat() if g.created_at else None,
                        }
                        for g in gates
                    ]
                }

            elif action == 'get':
                gate_id = arguments.get('gate_id')
                if not gate_id:
                    return {'success': False, 'error': 'gate_id required for get action'}

                try:
                    g = PilotReadinessGate.objects.select_related('decision').get(id=gate_id)
                    return {
                        'success': True,
                        'tool': 'gates_tool',
                        'gate': {
                            'id': str(g.id),
                            'status': g.status,
                            'risk_level': g.risk_level,
                            'risk_factors': g.risk_factors,
                            'summary': g.summary,
                            'success_criteria': g.success_criteria,
                            'failure_criteria': g.failure_criteria,
                            'approved_by': g.approved_by,
                            'approval_notes': g.approval_notes,
                            'decision_title': g.decision.title if g.decision else 'Unknown',
                            'created_at': g.created_at.isoformat() if g.created_at else None,
                        }
                    }
                except PilotReadinessGate.DoesNotExist:
                    return {'success': False, 'error': f'Gate {gate_id} not found'}

            elif action == 'stats':
                total = PilotReadinessGate.objects.count()
                by_status = dict(PilotReadinessGate.objects.values('status').annotate(count=Count('id')).values_list('status', 'count'))
                by_risk = dict(PilotReadinessGate.objects.values('risk_level').annotate(count=Count('id')).values_list('risk_level', 'count'))

                return {
                    'success': True,
                    'tool': 'gates_tool',
                    'action': 'stats',
                    'total_gates': total,
                    'by_status': by_status,
                    'by_risk_level': by_risk,
                    'pending_approval': by_status.get('ready', 0),
                    'blocked': by_status.get('blocked', 0),
                }

            elif action == 'checklist':
                gate_id = arguments.get('gate_id')
                if not gate_id:
                    return {'success': False, 'error': 'gate_id required for checklist action'}

                items = ChecklistItem.objects.filter(gate_id=gate_id).order_by('order')
                return {
                    'success': True,
                    'tool': 'gates_tool',
                    'action': 'checklist',
                    'gate_id': gate_id,
                    'item_count': len(items),
                    'items': [
                        {
                            'id': str(item.id),
                            'title': item.title,
                            'category': item.category,
                            'status': item.status,
                            'is_required': item.is_required,
                            'completed_at': item.completed_at.isoformat() if item.completed_at else None,
                        }
                        for item in items
                    ]
                }

            elif action == 'by_status':
                status = arguments.get('status')
                if not status:
                    return {'success': False, 'error': 'status required for by_status action'}

                gates = PilotReadinessGate.objects.filter(status=status).order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'tool': 'gates_tool',
                    'action': 'by_status',
                    'status': status,
                    'count': len(gates),
                    'gates': [{'id': str(g.id), 'summary': g.summary[:100] if g.summary else '', 'risk_level': g.risk_level} for g in gates]
                }

            elif action == 'by_risk':
                risk_level = arguments.get('risk_level')
                if not risk_level:
                    return {'success': False, 'error': 'risk_level required for by_risk action'}

                gates = PilotReadinessGate.objects.filter(risk_level=risk_level).order_by('-created_at')[:limit]
                return {
                    'success': True,
                    'tool': 'gates_tool',
                    'action': 'by_risk',
                    'risk_level': risk_level,
                    'count': len(gates),
                    'gates': [{'id': str(g.id), 'summary': g.summary[:100] if g.summary else '', 'status': g.status} for g in gates]
                }

            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error in gates_tool: {e}", exc_info=True)
            return {'success': False, 'error': str(e), 'tool': 'gates_tool'}

    def _handle_pilots_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle pilots_tool - Query pilot executions from Intelligence system.

        Actions: list, get, stats, running, completed, by_outcome
        """
        try:
            from core.models_pilot_readiness import PilotExecution
            from django.db.models import Count

            action = arguments.get('action', 'list')
            limit = arguments.get('limit', 20)

            if action == 'list':
                pilots = PilotExecution.objects.select_related('gate').order_by('-created_at')

                if arguments.get('status'):
                    pilots = pilots.filter(status=arguments['status'])
                if arguments.get('outcome'):
                    pilots = pilots.filter(outcome=arguments['outcome'])

                pilots = pilots[:limit]

                return {
                    'success': True,
                    'tool': 'pilots_tool',
                    'action': action,
                    'count': len(pilots),
                    'pilots': [
                        {
                            'id': str(p.id),
                            'name': p.name,
                            'status': p.status,
                            'outcome': p.outcome,
                            'started_at': p.started_at.isoformat() if p.started_at else None,
                            'completed_at': p.completed_at.isoformat() if p.completed_at else None,
                        }
                        for p in pilots
                    ]
                }

            elif action == 'get':
                pilot_id = arguments.get('pilot_id')
                if not pilot_id:
                    return {'success': False, 'error': 'pilot_id required for get action'}

                try:
                    p = PilotExecution.objects.select_related('gate').get(id=pilot_id)
                    return {
                        'success': True,
                        'tool': 'pilots_tool',
                        'pilot': {
                            'id': str(p.id),
                            'name': p.name,
                            'description': p.description,
                            'status': p.status,
                            'outcome': p.outcome,
                            'outcome_summary': p.outcome_summary,
                            'scope': p.scope,
                            'constraints': p.constraints,
                            'metrics': p.metrics,
                            'learnings': p.learnings,
                            'kill_switch_triggered': p.kill_switch_triggered,
                            'kill_switch_reason': p.kill_switch_reason,
                            'started_at': p.started_at.isoformat() if p.started_at else None,
                            'completed_at': p.completed_at.isoformat() if p.completed_at else None,
                        }
                    }
                except PilotExecution.DoesNotExist:
                    return {'success': False, 'error': f'Pilot {pilot_id} not found'}

            elif action == 'stats':
                total = PilotExecution.objects.count()
                by_status = dict(PilotExecution.objects.values('status').annotate(count=Count('id')).values_list('status', 'count'))
                by_outcome = dict(PilotExecution.objects.values('outcome').annotate(count=Count('id')).values_list('outcome', 'count'))

                return {
                    'success': True,
                    'tool': 'pilots_tool',
                    'action': 'stats',
                    'total_pilots': total,
                    'by_status': by_status,
                    'by_outcome': by_outcome,
                    'running': by_status.get('running', 0),
                    'completed': by_status.get('completed', 0),
                    'success_rate': round(by_outcome.get('success', 0) / total * 100, 1) if total > 0 else 0,
                }

            elif action == 'running':
                pilots = PilotExecution.objects.filter(status='running').order_by('-started_at')[:limit]
                return {
                    'success': True,
                    'tool': 'pilots_tool',
                    'action': 'running',
                    'count': len(pilots),
                    'pilots': [
                        {
                            'id': str(p.id),
                            'name': p.name,
                            'started_at': p.started_at.isoformat() if p.started_at else None,
                            'scope': p.scope[:200] if p.scope else '',
                        }
                        for p in pilots
                    ]
                }

            elif action == 'completed':
                pilots = PilotExecution.objects.filter(status='completed').order_by('-completed_at')[:limit]
                return {
                    'success': True,
                    'tool': 'pilots_tool',
                    'action': 'completed',
                    'count': len(pilots),
                    'pilots': [
                        {
                            'id': str(p.id),
                            'name': p.name,
                            'outcome': p.outcome,
                            'completed_at': p.completed_at.isoformat() if p.completed_at else None,
                        }
                        for p in pilots
                    ]
                }

            elif action == 'by_outcome':
                outcome = arguments.get('outcome')
                if not outcome:
                    return {'success': False, 'error': 'outcome required for by_outcome action'}

                pilots = PilotExecution.objects.filter(outcome=outcome).order_by('-completed_at')[:limit]
                return {
                    'success': True,
                    'tool': 'pilots_tool',
                    'action': 'by_outcome',
                    'outcome': outcome,
                    'count': len(pilots),
                    'pilots': [{'id': str(p.id), 'name': p.name, 'status': p.status} for p in pilots]
                }

            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error in pilots_tool: {e}", exc_info=True)
            return {'success': False, 'error': str(e), 'tool': 'pilots_tool'}

    # Session 796: Human Decisions Tool - Connect PA to Human Interface Layer
    def _handle_human_decisions_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle human_decisions_tool - Manage items that need human attention.

        This bridges the Human Interface Layer with the AI Assistant, allowing
        users to review and act on pending decisions via natural language.

        Actions: list, get, decide, stats
        """
        try:
            from core.models_human_interface import HumanAttentionItem
            from core.services.human_interface_service import get_human_interface_service
            from django.db.models import Count

            action = arguments.get('action', 'list')
            limit = arguments.get('limit', 10)

            # Get the human interface service for this user
            service = get_human_interface_service(self.user)

            if action == 'list':
                # Get pending items
                urgency_filter = [arguments['urgency_filter']] if arguments.get('urgency_filter') else None
                items = service.get_attention_stream(
                    limit=limit,
                    urgency_filter=urgency_filter,
                    status_filter=['pending', 'viewed']
                )

                # Format for natural language response
                if not items:
                    return {
                        'success': True,
                        'tool': 'human_decisions_tool',
                        'action': 'list',
                        'count': 0,
                        'message': 'No pending items need your attention right now.',
                        'items': []
                    }

                formatted_items = []
                for i, item in enumerate(items, 1):
                    urgency_emoji = {
                        'critical': '🚨',
                        'high': '⚠️',
                        'medium': '📋',
                        'low': 'ℹ️'
                    }.get(item.get('urgency', 'low'), '📋')

                    formatted_items.append({
                        'number': i,
                        'id': item['id'],
                        'emoji': urgency_emoji,
                        'urgency': item.get('urgency', 'medium'),
                        'type': item.get('item_type', 'review'),
                        'title': item.get('title', 'Untitled'),
                        'summary': item.get('summary', '')[:150],
                        'source_agent': item.get('source_agent', ''),
                        'ml_recommendation': item.get('ml_recommendation', ''),
                        'ml_confidence': item.get('ml_confidence', 0),
                    })

                return {
                    'success': True,
                    'tool': 'human_decisions_tool',
                    'action': 'list',
                    'count': len(formatted_items),
                    'message': f'You have {len(formatted_items)} item(s) that need your attention:',
                    'items': formatted_items
                }

            elif action == 'get':
                item_id = arguments.get('item_id')
                if not item_id:
                    return {'success': False, 'error': 'item_id required for get action'}

                try:
                    item = HumanAttentionItem.objects.get(id=item_id, user=self.user)
                    return {
                        'success': True,
                        'tool': 'human_decisions_tool',
                        'action': 'get',
                        'item': {
                            'id': str(item.id),
                            'title': item.title,
                            'summary': item.summary,
                            'urgency': item.urgency,
                            'item_type': item.item_type,
                            'source_type': item.source_type,
                            'source_agent': item.source_agent,
                            'status': item.status,
                            'payload': item.payload,
                            'ml_prediction': item.ml_prediction,
                            'ml_confidence': item.ml_confidence,
                            'ml_recommendation': item.ml_recommendation,
                            'created_at': item.created_at.isoformat(),
                        }
                    }
                except HumanAttentionItem.DoesNotExist:
                    return {'success': False, 'error': f'Item {item_id} not found'}

            elif action == 'decide':
                item_id = arguments.get('item_id')
                decision = arguments.get('decision')
                feedback = arguments.get('feedback', '')

                if not item_id:
                    return {'success': False, 'error': 'item_id required for decide action'}
                if not decision:
                    return {'success': False, 'error': 'decision required (approve, reject, defer, watch)'}

                # Use the service to record the decision
                result = service.record_decision(
                    item_id=item_id,
                    decision=decision,
                    feedback=feedback,
                    confidence=0.9  # High confidence when user explicitly decides
                )

                if result.get('success'):
                    decision_verb = {
                        'approve': 'approved',
                        'reject': 'rejected',
                        'defer': 'deferred',
                        'watch': 'marked for watching'
                    }.get(decision, decision)

                    return {
                        'success': True,
                        'tool': 'human_decisions_tool',
                        'action': 'decide',
                        'message': f'Done! Item has been {decision_verb}.',
                        'decision': decision,
                        'item_id': item_id,
                    }
                else:
                    return {'success': False, 'error': result.get('error', 'Failed to record decision')}

            elif action == 'stats':
                stats = service.get_attention_stats()
                return {
                    'success': True,
                    'tool': 'human_decisions_tool',
                    'action': 'stats',
                    'stats': stats,
                    'message': f"You have {stats.get('pending', 0)} pending items. "
                               f"Average decision time: {stats.get('avg_decision_time_ms', 0):.0f}ms."
                }

            # Session 796 Phase 2: Batch decide - apply same decision to multiple items
            elif action == 'batch_decide':
                decision = arguments.get('decision')
                feedback = arguments.get('feedback', '')
                urgency_filter = arguments.get('urgency_filter')
                type_filter = arguments.get('type_filter')

                if not decision:
                    return {'success': False, 'error': 'decision required for batch_decide action'}

                # Build filter for items to decide
                filters = {'status__in': ['pending', 'viewed'], 'user': self.user}
                if urgency_filter:
                    filters['urgency'] = urgency_filter
                if type_filter:
                    filters['item_type'] = type_filter

                items = HumanAttentionItem.objects.filter(**filters)
                count = items.count()

                if count == 0:
                    filter_desc = []
                    if urgency_filter:
                        filter_desc.append(f"urgency={urgency_filter}")
                    if type_filter:
                        filter_desc.append(f"type={type_filter}")
                    filter_str = f" matching {', '.join(filter_desc)}" if filter_desc else ""
                    return {
                        'success': True,
                        'tool': 'human_decisions_tool',
                        'action': 'batch_decide',
                        'count': 0,
                        'message': f'No pending items found{filter_str}.'
                    }

                # Execute decisions
                success_count = 0
                for item in items:
                    result = service.record_decision(
                        item_id=str(item.id),
                        decision=decision,
                        feedback=feedback or f"Batch {decision} via PA",
                        confidence=0.85  # Batch decisions have slightly lower confidence
                    )
                    if result.get('success'):
                        success_count += 1

                decision_verb = {
                    'approve': 'approved',
                    'reject': 'rejected',
                    'defer': 'deferred',
                    'watch': 'marked for watching'
                }.get(decision, decision)

                return {
                    'success': True,
                    'tool': 'human_decisions_tool',
                    'action': 'batch_decide',
                    'count': success_count,
                    'total': count,
                    'decision': decision,
                    'message': f'Done! {decision_verb.capitalize()} {success_count} of {count} items.'
                }

            # Session 796 Phase 2: Auto-execute low-risk decisions with high ML confidence
            elif action == 'auto_execute':
                confidence_threshold = arguments.get('confidence_threshold', 0.85)

                # Find low-risk items with high ML confidence
                candidates = HumanAttentionItem.objects.filter(
                    user=self.user,
                    status__in=['pending', 'viewed'],
                    urgency__in=['low', 'medium'],  # Not critical/high
                    ml_confidence__gte=confidence_threshold,
                    ml_recommendation__isnull=False
                ).exclude(
                    item_type='policy'  # Never auto-execute policy decisions
                )

                count = candidates.count()
                if count == 0:
                    return {
                        'success': True,
                        'tool': 'human_decisions_tool',
                        'action': 'auto_execute',
                        'count': 0,
                        'message': f'No low-risk items with ML confidence >= {confidence_threshold:.0%} found.'
                    }

                # Execute ML-recommended decisions
                executed = []
                for item in candidates:
                    ml_decision = item.ml_recommendation  # 'approve', 'reject', etc.
                    result = service.record_decision(
                        item_id=str(item.id),
                        decision=ml_decision,
                        feedback=f"Auto-executed (ML confidence: {item.ml_confidence:.0%})",
                        confidence=item.ml_confidence
                    )
                    if result.get('success'):
                        executed.append({
                            'id': str(item.id),
                            'title': item.title[:50],
                            'decision': ml_decision,
                            'confidence': item.ml_confidence
                        })

                return {
                    'success': True,
                    'tool': 'human_decisions_tool',
                    'action': 'auto_execute',
                    'count': len(executed),
                    'threshold': confidence_threshold,
                    'executed': executed,
                    'message': f'Auto-executed {len(executed)} low-risk decisions (ML confidence >= {confidence_threshold:.0%}).'
                }

            # Session 796 Phase 2: Consultation prompt - PA asks before autonomous action
            elif action == 'consult':
                consultation_context = arguments.get('consultation_context', '')

                if not consultation_context:
                    return {'success': False, 'error': 'consultation_context required for consult action'}

                # Create a consultation item in the human attention queue
                consultation_item = HumanAttentionItem.objects.create(
                    user=self.user,
                    source_type='assistant',
                    source_id='personal_assistant',
                    source_agent='PersonalAssistant',
                    item_type='approval',
                    title='PA Consultation Request',
                    summary=consultation_context,
                    urgency='high',  # Consultations are high priority
                    priority_score=80,
                    status='pending',
                    payload={
                        'consultation': True,
                        'context': consultation_context,
                        'awaiting_response': True
                    }
                )

                return {
                    'success': True,
                    'tool': 'human_decisions_tool',
                    'action': 'consult',
                    'consultation_id': str(consultation_item.id),
                    'message': f"I'd like your input before proceeding: {consultation_context}\n\nPlease respond with 'yes', 'no', or provide guidance.",
                    'awaiting_response': True
                }

            else:
                return {'success': False, 'error': f'Unknown action: {action}'}

        except Exception as e:
            logger.error(f"Error in human_decisions_tool: {e}", exc_info=True)
            return {'success': False, 'error': str(e), 'tool': 'human_decisions_tool'}

    # =========================================================================
    # SESSION 800: REASONING ENGINE TOOL - CONNECT PA TO THINKINGAGENT
    # =========================================================================

    def _handle_reasoning_engine_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle reasoning_engine_tool - Access the Autonomous Reasoning Engine (ThinkingAgent).

        This connects the PA to the system's autonomous thinking layer, allowing
        users to see what the system has been thinking about and what actions
        it has taken autonomously.

        Actions: thoughts, insights, actions, status, trigger
        """
        try:
            from core.models_unified_system import ThoughtRecord, AutonomousAction
            from django.utils import timezone
            from datetime import timedelta

            action = arguments.get('action', 'thoughts')
            limit = arguments.get('limit', 10)
            include_context = arguments.get('include_context', False)

            if action == 'thoughts':
                # Get recent thought records
                thoughts = ThoughtRecord.objects.order_by('-started_at')[:limit]

                if not thoughts.exists():
                    return {
                        'success': True,
                        'tool': 'reasoning_engine_tool',
                        'action': 'thoughts',
                        'count': 0,
                        'message': 'No thinking cycles have been recorded yet. The reasoning engine runs automatically on a schedule.',
                        'thoughts': []
                    }

                thought_list = []
                for thought in thoughts:
                    thought_data = {
                        'id': str(thought.id),
                        'cycle_number': thought.cycle_number,
                        'cycle_type': thought.cycle_type,
                        'reflection_preview': thought.reflection[:300] + '...' if thought.reflection and len(thought.reflection) > 300 else thought.reflection,
                        'insights_count': len(thought.insights) if thought.insights else 0,
                        'patterns_count': len(thought.patterns) if thought.patterns else 0,
                        'decisions_count': len(thought.decisions) if thought.decisions else 0,
                        'actions_executed_count': len(thought.actions_executed) if thought.actions_executed else 0,
                        'priority_score': thought.priority_score,
                        'execution_status': thought.execution_status,
                        'started_at': thought.started_at.isoformat() if thought.started_at else None,
                    }

                    if include_context:
                        thought_data['context_summary'] = thought.context_summary
                        thought_data['insights'] = thought.insights
                        thought_data['patterns'] = thought.patterns

                    thought_list.append(thought_data)

                return {
                    'success': True,
                    'tool': 'reasoning_engine_tool',
                    'action': 'thoughts',
                    'count': len(thought_list),
                    'message': f'Found {len(thought_list)} recent thinking cycle(s):',
                    'thoughts': thought_list
                }

            elif action == 'insights':
                # Get just insights from recent thoughts
                thoughts = ThoughtRecord.objects.filter(
                    insights__isnull=False
                ).exclude(insights=[]).order_by('-started_at')[:limit]

                all_insights = []
                for thought in thoughts:
                    if thought.insights:
                        for insight in thought.insights:
                            all_insights.append({
                                'insight': insight.get('insight', ''),
                                'confidence': insight.get('confidence', 0),
                                'category': insight.get('category', 'general'),
                                'from_cycle': thought.cycle_number,
                                'date': thought.started_at.isoformat() if thought.started_at else None,
                            })

                return {
                    'success': True,
                    'tool': 'reasoning_engine_tool',
                    'action': 'insights',
                    'count': len(all_insights),
                    'message': f'Found {len(all_insights)} insight(s) from the reasoning engine:',
                    'insights': all_insights[:limit * 3]  # More insights per thought
                }

            elif action == 'actions':
                # Get recent autonomous actions
                actions = AutonomousAction.objects.select_related('thought_record').order_by('-created_at')[:limit]

                action_list = []
                for a in actions:
                    action_list.append({
                        'id': str(a.id),
                        'action_type': a.action_type,
                        'action_name': a.action_name,
                        'reasoning': a.reasoning[:200] if a.reasoning else '',
                        'priority': a.priority,
                        'status': a.status,
                        'result_summary': a.result_summary[:200] if a.result_summary else '',
                        'created_at': a.created_at.isoformat() if a.created_at else None,
                        'from_cycle': a.thought_record.cycle_number if a.thought_record else None,
                    })

                return {
                    'success': True,
                    'tool': 'reasoning_engine_tool',
                    'action': 'actions',
                    'count': len(action_list),
                    'message': f'Found {len(action_list)} autonomous action(s) taken by the system:',
                    'actions': action_list
                }

            elif action == 'status':
                # Get reasoning engine status
                total_thoughts = ThoughtRecord.objects.count()
                completed_thoughts = ThoughtRecord.objects.filter(execution_status='completed').count()
                last_thought = ThoughtRecord.objects.order_by('-started_at').first()

                # Count total insights and actions
                total_insights = sum(
                    len(t.insights) if t.insights else 0
                    for t in ThoughtRecord.objects.all()[:100]  # Limit for performance
                )
                total_actions = AutonomousAction.objects.count()
                successful_actions = AutonomousAction.objects.filter(status='completed').count()

                status_data = {
                    'total_thinking_cycles': total_thoughts,
                    'completed_cycles': completed_thoughts,
                    'total_insights_generated': total_insights,
                    'total_autonomous_actions': total_actions,
                    'successful_actions': successful_actions,
                    'last_cycle': {
                        'cycle_number': last_thought.cycle_number if last_thought else None,
                        'started_at': last_thought.started_at.isoformat() if last_thought and last_thought.started_at else None,
                        'status': last_thought.execution_status if last_thought else None,
                    } if last_thought else None,
                }

                return {
                    'success': True,
                    'tool': 'reasoning_engine_tool',
                    'action': 'status',
                    'status': status_data,
                    'message': f'Reasoning Engine has run {total_thoughts} thinking cycles, generated {total_insights} insights, and taken {total_actions} autonomous actions.'
                }

            elif action == 'trigger':
                # Queue a new thinking cycle
                from core.tasks import run_thinking_cycle

                # Queue the task
                result = run_thinking_cycle.delay()

                return {
                    'success': True,
                    'tool': 'reasoning_engine_tool',
                    'action': 'trigger',
                    'task_id': str(result.id) if result else None,
                    'message': 'A new thinking cycle has been queued. The reasoning engine will gather context, reflect, and generate insights shortly.'
                }

            elif action == 'get':
                # Get specific thought by ID
                thought_id = arguments.get('thought_id')
                if not thought_id:
                    return {'success': False, 'error': 'thought_id required for get action'}

                try:
                    thought = ThoughtRecord.objects.get(id=thought_id)
                    actions = AutonomousAction.objects.filter(thought_record=thought).order_by('created_at')

                    return {
                        'success': True,
                        'tool': 'reasoning_engine_tool',
                        'action': 'get',
                        'thought': {
                            'id': str(thought.id),
                            'cycle_number': thought.cycle_number,
                            'cycle_type': thought.cycle_type,
                            'context_summary': thought.context_summary,
                            'reflection': thought.reflection,
                            'insights': thought.insights,
                            'patterns': thought.patterns,
                            'opportunities': thought.opportunities,
                            'concerns': thought.concerns,
                            'decisions': thought.decisions,
                            'priority_score': thought.priority_score,
                            'execution_status': thought.execution_status,
                            'started_at': thought.started_at.isoformat() if thought.started_at else None,
                            'completed_at': thought.completed_at.isoformat() if thought.completed_at else None,
                        },
                        'actions': [
                            {
                                'action_type': a.action_type,
                                'action_name': a.action_name,
                                'status': a.status,
                                'result_summary': a.result_summary,
                            }
                            for a in actions
                        ]
                    }
                except ThoughtRecord.DoesNotExist:
                    return {'success': False, 'error': f'Thought record {thought_id} not found'}

            else:
                return {'success': False, 'error': f'Unknown action: {action}. Valid actions: thoughts, insights, actions, status, trigger'}

        except Exception as e:
            logger.error(f"Error in reasoning_engine_tool: {e}", exc_info=True)
            return {'success': False, 'error': str(e), 'tool': 'reasoning_engine_tool'}

    def _handle_platform_query_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Session 951: Handle platform_query_tool - Query platform data including reports,
        deliverables, initiatives, and agent outputs.

        This tool provides the PA with actual database access to answer questions
        like "what reports have been written by agents" with real data.
        """
        try:
            from core.models_deliverables import Deliverable
            from core.models_audit_tracking import AuditReport
            from core.models_document_registry import Initiative
            from django.utils import timezone
            from datetime import timedelta

            query_type = arguments.get('query_type', 'content_summary')
            filters = arguments.get('filters', {})

            days = filters.get('days', 30)
            limit = filters.get('limit', 20)
            cutoff = timezone.now() - timedelta(days=days)

            if query_type == 'deliverables':
                # Query deliverables (blog posts, reports, analyses)
                queryset = Deliverable.objects.filter(
                    created_at__gte=cutoff
                ).order_by('-created_at')

                # Apply optional filters
                if filters.get('agent_name'):
                    queryset = queryset.filter(agent_name__icontains=filters['agent_name'])
                if filters.get('deliverable_type'):
                    queryset = queryset.filter(deliverable_type=filters['deliverable_type'])
                if filters.get('category'):
                    queryset = queryset.filter(category__icontains=filters['category'])

                deliverables = queryset[:limit]

                items = []
                for d in deliverables:
                    items.append({
                        'id': str(d.id),
                        'title': d.title,
                        'type': d.deliverable_type,
                        'category': d.category or 'Uncategorized',
                        'agent': d.agent_name,
                        'created_at': d.created_at.strftime('%Y-%m-%d %H:%M'),
                        'preview': d.content[:200] + '...' if d.content and len(d.content) > 200 else (d.content or ''),
                    })

                return {
                    'success': True,
                    'tool': 'platform_query_tool',
                    'query_type': 'deliverables',
                    'count': len(items),
                    'total_in_period': queryset.count(),
                    'message': f"Found {queryset.count()} deliverable(s) in the last {days} days:",
                    'items': items
                }

            elif query_type == 'audit_reports':
                # Query audit reports
                queryset = AuditReport.objects.filter(
                    created_at__gte=cutoff
                ).order_by('-created_at')

                reports = queryset[:limit]

                items = []
                for r in reports:
                    items.append({
                        'id': str(r.id),
                        'title': r.title,
                        'type': r.audit_type,
                        'auditor': r.auditor,
                        'session': r.session_number,
                        'total_findings': r.total_findings,
                        'p0_findings': r.p0_findings,
                        'open_findings': r.open_findings,
                        'created_at': r.created_at.strftime('%Y-%m-%d'),
                    })

                return {
                    'success': True,
                    'tool': 'platform_query_tool',
                    'query_type': 'audit_reports',
                    'count': len(items),
                    'message': f"Found {queryset.count()} audit report(s) in the last {days} days:",
                    'items': items
                }

            elif query_type == 'initiatives':
                # Query initiatives
                queryset = Initiative.objects.filter(
                    created_at__gte=cutoff
                ).order_by('-created_at')

                initiatives = queryset[:limit]

                items = []
                for i in initiatives:
                    items.append({
                        'id': str(i.id),
                        'name': i.name,
                        'stage': i.stage,
                        'status': i.status if hasattr(i, 'status') else None,
                        'priority': getattr(i, 'priority', None),
                        'created_at': i.created_at.strftime('%Y-%m-%d'),
                        'source': i.source_type if hasattr(i, 'source_type') else None,
                    })

                return {
                    'success': True,
                    'tool': 'platform_query_tool',
                    'query_type': 'initiatives',
                    'count': len(items),
                    'message': f"Found {queryset.count()} initiative(s) in the last {days} days:",
                    'items': items
                }

            elif query_type == 'agent_outputs':
                # Query deliverables grouped by agent
                agent_name = filters.get('agent_name')

                if agent_name:
                    queryset = Deliverable.objects.filter(
                        created_at__gte=cutoff,
                        agent_name__icontains=agent_name
                    ).order_by('-created_at')[:limit]

                    items = []
                    for d in queryset:
                        items.append({
                            'title': d.title,
                            'type': d.deliverable_type,
                            'category': d.category or 'Uncategorized',
                            'created_at': d.created_at.strftime('%Y-%m-%d %H:%M'),
                        })

                    return {
                        'success': True,
                        'tool': 'platform_query_tool',
                        'query_type': 'agent_outputs',
                        'agent': agent_name,
                        'count': len(items),
                        'message': f"Found {len(items)} output(s) from {agent_name}:",
                        'items': items
                    }
                else:
                    # Summary by agent
                    from django.db.models import Count
                    agent_summary = Deliverable.objects.filter(
                        created_at__gte=cutoff
                    ).values('agent_name').annotate(
                        count=Count('id')
                    ).order_by('-count')[:20]

                    return {
                        'success': True,
                        'tool': 'platform_query_tool',
                        'query_type': 'agent_outputs',
                        'message': f"Agent output summary for last {days} days:",
                        'by_agent': list(agent_summary)
                    }

            elif query_type == 'content_summary':
                # Overview of all content
                from django.db.models import Count

                deliverable_count = Deliverable.objects.filter(created_at__gte=cutoff).count()
                audit_count = AuditReport.objects.filter(created_at__gte=cutoff).count()
                initiative_count = Initiative.objects.filter(created_at__gte=cutoff).count()

                # Type breakdown
                type_breakdown = Deliverable.objects.filter(
                    created_at__gte=cutoff
                ).values('deliverable_type').annotate(
                    count=Count('id')
                ).order_by('-count')

                # Top agents
                top_agents = Deliverable.objects.filter(
                    created_at__gte=cutoff
                ).values('agent_name').annotate(
                    count=Count('id')
                ).order_by('-count')[:5]

                return {
                    'success': True,
                    'tool': 'platform_query_tool',
                    'query_type': 'content_summary',
                    'period_days': days,
                    'summary': {
                        'deliverables': deliverable_count,
                        'audit_reports': audit_count,
                        'initiatives': initiative_count,
                    },
                    'by_type': list(type_breakdown),
                    'top_agents': list(top_agents),
                    'message': f"Platform content summary for last {days} days: {deliverable_count} deliverables, {audit_count} audit reports, {initiative_count} initiatives."
                }

            else:
                return {
                    'success': False,
                    'error': f"Unknown query_type: {query_type}. Valid types: deliverables, audit_reports, initiatives, agent_outputs, content_summary"
                }

        except Exception as e:
            logger.error(f"Error in platform_query_tool: {e}", exc_info=True)
            return {'success': False, 'error': str(e), 'tool': 'platform_query_tool'}

    # ── BPaaS Tool: Build Packet as a Service ─────────────────────────────

    def _handle_bpaas_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle BPaaS operations — create projects from build packets,
        generate close packs, and manage the BPaaS pipeline.
        """
        action = arguments.get('action')
        if not action:
            return {'success': False, 'error': 'action is required'}

        try:
            if action == 'create_project':
                from core.services.bpaas.packet_service import create_project_from_packet
                from core.models_skin_layer import ProjectWorkspace

                workspace_id = arguments.get('workspace_id')
                packet = arguments.get('packet')

                if not workspace_id or not packet:
                    return {'success': False, 'error': 'workspace_id and packet are required'}

                workspace = ProjectWorkspace.objects.get(id=workspace_id)
                result = create_project_from_packet(
                    workspace=workspace,
                    packet=packet,
                    created_by=self.user,
                )
                return {
                    'success': True,
                    'action': 'create_project',
                    **result,
                    'message': f"Created BPaaS project '{result['project']['name']}' with {len(result['repos'])} repos, preview env, and magic link",
                }

            elif action == 'generate_close_pack':
                from core.services.bpaas.packet_service import generate_close_pack

                packet = arguments.get('packet')
                if not packet:
                    return {'success': False, 'error': 'packet is required'}

                close_pack = generate_close_pack(packet)
                return {
                    'success': True,
                    'action': 'generate_close_pack',
                    **close_pack,
                    'message': 'Generated SOW, delivery checklist, and proposal',
                }

            elif action == 'get_schema':
                from core.services.bpaas.build_packet_schema import BUILD_PACKET_SCHEMA
                return {
                    'success': True,
                    'action': 'get_schema',
                    'schema': BUILD_PACKET_SCHEMA,
                    'message': 'Build packet JSON schema',
                }

            elif action == 'get_example':
                from core.services.bpaas.build_packet_schema import NORMAN_HANDYMAN_EXAMPLE
                return {
                    'success': True,
                    'action': 'get_example',
                    'example': NORMAN_HANDYMAN_EXAMPLE,
                    'message': 'Norman Handyman MVP example build packet',
                }

            else:
                return {
                    'success': False,
                    'error': f"Unknown action: {action}. Valid actions: create_project, generate_close_pack, get_schema, get_example",
                }

        except Exception as e:
            logger.error(f"Error in bpaas_tool: {e}", exc_info=True)
            return {'success': False, 'error': str(e), 'tool': 'bpaas_tool'}

    # Session 796 Phase 3: Consultation Response Detection
