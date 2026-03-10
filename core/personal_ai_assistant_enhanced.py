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



from core.epa_handlers_tools import EPAToolHandlersMixin
from core.epa_handlers_agents import EPAAgentToolsMixin
from core.epa_handlers_utility import EPAUtilityMixin


class EnhancedPersonalAIAssistant(EPAToolHandlersMixin, EPAAgentToolsMixin, EPAUtilityMixin, PersonalAIAssistant):
    """
    Enhanced Personal AI Assistant with database access and system capabilities.
    """

    def __init__(self, user: User):
        super().__init__(user)
        self.system_access_enabled = True
        self.database_queries_executed = []
        self._ensure_enhanced_profile()
        self.llm_enforcer = LLMEnforcer()  # Initialize real AI
        self.memory_manager = get_memory_manager(user)  # Initialize unified memory

        # Initialize registries for agent/advisor communication
        self.agent_registry = get_agent_registry()
        self.advisor_registry = get_advisor_registry()

        # Session 122: Asset tracking for intelligent chaining (logos → videos)
        self.recently_generated_assets = {
            'images': [],  # [{id, url, prompt, timestamp, type}]
            'videos': [],  # [{id, url, prompt, timestamp, source_image_id}]
            'last_updated': None
        }

        # Session 266: Super Platform Integration - Dynamic Prompting
        self.query_classifier = QueryClassifier() if SUPER_PLATFORM_AVAILABLE else None
        self.context_aggregator = ContextAggregator(user) if SUPER_PLATFORM_AVAILABLE else None
        self._learning_service = None  # Lazy loaded
        self._scifi_service = None  # Lazy loaded
        self._learning_companion_service = None  # Lazy loaded - Session 266
        self._last_classification = None  # Store for learning loop

        # Session 482: Proactive Intelligence - Connect 19 Autonomous Situations
        self.proactive_intelligence = get_proactive_intelligence_service(user) if PROACTIVE_INTELLIGENCE_AVAILABLE else None
        self._last_proactive_intelligence = None  # Cache last intelligence for response suggestions

        # Session 482: Reference Resolution - Handle "it", "that", "the first one"
        self.reference_resolver = get_reference_resolver(str(user.id)) if REFERENCE_RESOLVER_AVAILABLE else None

        # Session 482: Smart Suggestions - Context-aware follow-up suggestions
        self.smart_suggestions = get_smart_suggestions_service(str(user.id)) if SMART_SUGGESTIONS_AVAILABLE else None

        # Session 482: Task Memory - Multi-turn task tracking
        self.task_memory = get_task_memory_service(str(user.id)) if TASK_MEMORY_AVAILABLE else None

        # Session 806: Context Optimization - Reduce token usage by ~70%
        self.context_budget_manager = get_context_budget_manager() if CONTEXT_OPTIMIZATION_AVAILABLE else None
        self.lazy_context_loader = get_lazy_context_loader() if CONTEXT_OPTIMIZATION_AVAILABLE else None
        self.context_summarizer = get_context_summarizer() if CONTEXT_OPTIMIZATION_AVAILABLE else None
        self.tool_category_router = get_tool_category_router() if CONTEXT_OPTIMIZATION_AVAILABLE else None

        if SUPER_PLATFORM_AVAILABLE:
            logger.info(f"✅ Enhanced AI Assistant initialized with REAL AI, Unified Memory, Agent/Advisor Communication, Asset Tracking, AND Super Platform Integration for {user.username}")
        else:
            logger.info(f"✅ Enhanced AI Assistant initialized with REAL AI, Unified Memory, Agent/Advisor Communication, and Asset Tracking for {user.username}")

    # Session 131: Agent-Based Tool Definitions
    def get_tool_definitions(self) -> List[Dict]:
        """
        Get agent-based tool definitions for GPT-5.1 Responses API function calling.

        Session 131: Refactored from 14+ individual tools to 5 agent orchestrators.
        This provides clearer intent, less confusion, and better alignment with multi-agent architecture.

        Architecture: GPT-5.1 → Agent → Specific Operation
        """
        return [
            # Session 132: Image Generation Agent - NEW!
            {
                "type": "function",
                "name": "image_generation_agent",
                "description": "Generate BRAND NEW images from scratch using text prompts. CRITICAL: Use this agent whenever user wants to CREATE/GENERATE/MAKE images that don't exist yet: 'create banner', 'generate logo', 'make social media post', 'design avatar', 'create profile picture', 'create images matching style', 'header image', etc. This generates NEW images, not modifications of existing ones. ⚠️ MULTI-TOOL: If user asks for 'blog post + header image' or 'article with banner', call BOTH content_writer_agent AND this tool. Supports custom dimensions (width/height), quality levels, style preferences, and multiple images.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Text description of the image to generate (e.g., 'modern tech company logo', 'social media banner with vibrant colors', 'professional profile picture')"
                        },
                        "count": {
                            "type": "integer",
                            "default": 1,
                            "description": "Number of images to generate (1-5). IMPORTANT: Use this when user asks for multiple images, e.g., 'create 3 logos' -> count=3, 'make 5 banners' -> count=5"
                        },
                        "params": {
                            "type": "object",
                            "description": "Optional generation parameters",
                            "properties": {
                                "width": {"type": "integer", "default": 1024, "description": "Image width (512-2048)"},
                                "height": {"type": "integer", "default": 1024, "description": "Image height (512-2048)"},
                                "quality": {"type": "string", "enum": ["fast", "balanced", "high", "premium"], "default": "balanced", "description": "Quality level: fast (core), balanced (sdxl), high (sd3), premium (ultra)"},
                                "style": {"type": "string", "default": "photorealistic", "description": "Style preset or custom style description"}
                            }
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Optional project ID to associate images with"
                        },
                        "character_model_name": {
                            "type": "string",
                            "description": "Optional trained character/style model to use for generation. CRITICAL: Extract ANY mention of a specific style, brand identity, character model, or trained aesthetic from the user's request. Examples: 'AI content generation company style', 'company style', 'our brand style', 'the trained model', etc. The backend will automatically match variations and trigger words (case-insensitive, handles spaces/dashes). When user mentions a trained style/model, extract it AS SPOKEN/WRITTEN - don't worry about exact formatting. When specified, uses FLUX + custom LoRA training. Omit for standard Stability AI generation. Session 134: Now supports trigger word matching!"
                        }
                    },
                    "required": ["prompt"]
                }
            },

            # Session 131: Image Editing Agent (replaces 6 individual tools)
            # Session 152: BATCH OPERATIONS SUPPORT! 🚀
            {
                "type": "function",
                "name": "image_editing_agent",
                "description": "MODIFY EXISTING images only. Requires an existing image_id. Operations: upscale (4x resolution), remove_background (transparent PNG), create_variations (multiple styles), recolor (change colors), search_and_replace (REMOVE objects by omitting replace_prompt OR replace with something else), creative_upscale (4x upscale + add creative details with prompt). IMPORTANT: This agent modifies images that already exist. For creating NEW images from scratch, use image_generation_agent instead. SESSION 152: Now supports BATCH OPERATIONS - process multiple images at once using ranges or lists!",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "Operation to perform: 'upscale' | 'remove_background' | 'create_variations' | 'recolor' | 'search_and_replace' (remove OR replace objects) | 'creative_upscale'",
                            "enum": ["upscale", "remove_background", "create_variations", "recolor", "search_and_replace", "creative_upscale"]
                        },
                        "image_id": {
                            "type": "string",
                            "description": "Image identifier(s) - supports SINGLE or BATCH: Single: '2' or UUID. BATCH (Session 152): Range '20-25', List '5, 8, 12', Combined '10-15, 20, 25-27'. Examples: 'upscale images 20-25', 'remove backgrounds from images 5, 8, 12', 'create variations of images 10-15'. The agent will process each image sequentially and return a batch summary."
                        },
                        "params": {
                            "type": "object",
                            "description": "Operation-specific parameters: For recolor: {prompt: 'make robot black'}. For create_variations: {count: 3}. For search_and_replace: {search_prompt: 'object to find', replace_prompt: 'optional - omit to REMOVE, include to REPLACE'}. For creative_upscale: {prompt: 'what details to add', creativity: 0.3}.",
                            "properties": {
                                "prompt": {"type": "string"},
                                "search_prompt": {"type": "string"},
                                "replace_prompt": {"type": "string"},
                                "creativity": {"type": "number"},
                                "count": {"type": "integer", "default": 3}
                            }
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Optional project ID to associate result with"
                        }
                    },
                    "required": ["operation", "image_id"]
                }
            },

            # Session 131: Video Generation Agent (replaces 4 tools)
            # Session 175: Added lip_sync for character speech animation
            {
                "type": "function",
                "name": "video_generation_agent",
                "description": "Handle video generation operations: generate (create video from text prompt), animate (transform image to moving video WITHOUT speech), extend (make video longer), chain (combine multiple videos), lip_sync (sync existing audio to existing video). NOTE: For 'make image talk' or 'create talking character', use talking_character_agent instead (it combines TTS + animation + lip sync). Use THIS agent for: video from text prompts, silent animation from images, video extension, video chaining, or manual lip sync when you already have separate audio and video files.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "Operation: 'generate' | 'animate' | 'extend' | 'chain' | 'lip_sync' (Session 175 - sync lips to audio)",
                            "enum": ["generate", "animate", "extend", "chain", "lip_sync"]
                        },
                        "params": {
                            "type": "object",
                            "description": "Operation-specific parameters. For generate: {prompt, duration}. For animate: {image_id, motion_prompt, duration}. For extend: {video_id, extension_seconds, prompt}. For chain: {video_ids, add_transitions}. For lip_sync (Session 175): {video_url, audio_url, sync_mode, temperature}.",
                            "properties": {
                                "prompt": {"type": "string"},
                                "duration": {"type": "integer", "default": 5},
                                "image_id": {"type": "string"},
                                "motion_prompt": {"type": "string", "default": "natural motion"},
                                "video_id": {"type": "string"},
                                "extension_seconds": {"type": "integer", "default": 10},
                                "video_ids": {"type": "array", "items": {"type": "string"}},
                                "add_transitions": {"type": "boolean", "default": True},
                                "video_url": {"type": "string", "description": "Session 175: URL to video with face for lip sync"},
                                "audio_url": {"type": "string", "description": "Session 175: URL to audio file to sync lips to"},
                                "sync_mode": {"type": "string", "enum": ["cut_off", "loop", "bounce"], "default": "cut_off", "description": "Session 175: How to handle duration mismatch"},
                                "temperature": {"type": "number", "default": 0.5, "description": "Session 175: Expression intensity 0-1 (0.5 = natural)"}
                            }
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Optional project ID"
                        }
                    },
                    "required": ["operation", "params"]
                }
            },

            # Session 131: Audio Generation Agent (replaces 2 tools)
            {
                "type": "function",
                "name": "audio_generation_agent",
                "description": "Handle all audio generation: generate_voice (text-to-speech), add_voiceover (add narration to video). Use this agent for ANY audio generation request.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "Operation: 'generate_voice' | 'add_voiceover'",
                            "enum": ["generate_voice", "add_voiceover"]
                        },
                        "params": {
                            "type": "object",
                            "description": "For generate_voice: {text, voice}. For add_voiceover: {video_id, text, voice}.",
                            "properties": {
                                "text": {"type": "string"},
                                "voice": {"type": "string", "default": "Rachel"},
                                "video_id": {"type": "string"}
                            }
                        },
                        "project_id": {"type": "string"}
                    },
                    "required": ["operation", "params"]
                }
            },

            # Session 131: 3D Generation Agent (replaces 1 tool)
            {
                "type": "function",
                "name": "three_d_generation_agent",
                "description": "Convert images to 3D models using Replicate TRELLIS. Creates downloadable GLB files for 3D printing. Use when users want: 'convert to 3D', 'make 3D model', '3D print', 'create 3D object'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "Operation (currently only 'convert')",
                            "enum": ["convert"]
                        },
                        "image_id": {
                            "type": "string",
                            "description": "Image identifier: sequential number OR full UUID"
                        },
                        "project_id": {"type": "string"}
                    },
                    "required": ["operation", "image_id"]
                }
            },

            # Session 131: Video Editing Agent (replaces 2 tools)
            {
                "type": "function",
                "name": "video_editing_agent",
                "description": "Handle all video editing: add_text_overlay (captions/titles with timing), apply_color_grading (DaVinci cinematic effects), upscale (2x or 4x quality enhancement with ffmpeg - FREE!), apply_effect (color grading: cinematic, vibrant, vintage, noir, warm, cool - FREE!), extract_frame (pull a still image from any timestamp - FREE!), reverse (play video backwards - FREE!), trim (cut video to specific time range - FREE!), speed_change (slow motion 0.5x or speed up 2x - FREE!), concatenate (combine multiple videos into one - FREE!), rotate_flip (rotate 90/180/270 degrees or flip horizontal/vertical - FREE!), fade (add fade in/out effects - FREE!), crop_resize (crop to region, resize dimensions, or change aspect ratio - FREE!), audio_control (adjust volume, mute, or extract audio - FREE!), picture_in_picture (overlay one video on another - FREE!), add_watermark (overlay logo/image on video with position and opacity - FREE!), blur_region (blur part of video for privacy/censoring - FREE!), render_professional (EXPORT TO ProRes 422/ProRes 4444/DNxHD - Professional broadcast codecs!), apply_lut (apply color LUT files), color_grade_professional (DaVinci-style lift/gamma/gain color grading). Session 167: Added ProRes/DNxHD rendering. Use this agent for ANY video editing request. SUPPORTS BATCH OPERATIONS: Process multiple videos using ranges '1-3' or lists '1, 3, 5'. FOR PRORES: Say 'render video 1 in ProRes' or 'export video 2 as ProRes 4444'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "description": "Operation: 'add_text_overlay' | 'apply_color_grading' | 'upscale' (Session 154 - ffmpeg 2x/4x) | 'apply_effect' (Session 154 - color grading) | 'extract_frame' (Session 159 - pull still image at timestamp) | 'reverse' (Session 159 - play video backwards) | 'trim' (Session 159 - cut video to time range) | 'speed_change' (Session 160 - slow motion or speed up) | 'concatenate' (Session 160 - combine multiple videos) | 'rotate_flip' (Session 161 - rotate 90/180/270 or flip) | 'fade' (Session 161 - fade in/out effects) | 'crop_resize' (Session 161 - crop/resize/aspect ratio) | 'audio_control' (Session 161 - volume/mute/extract) | 'picture_in_picture' (Session 161 - overlay video) | 'add_watermark' (Session 163 - overlay logo/image) | 'blur_region' (Session 163 - blur for privacy) | 'stabilize_video' (Session 164 - fix shaky footage) | 'add_text_animation' (Session 164 - scrolling/animated text) | 'chroma_key' (Session 165 - green/blue screen removal) | 'export_for_platform' (Session 166 - YouTube/TikTok/Instagram export) | 'video_transition' (Session 166 - crossfade/wipe/slide between videos) | 'auto_caption' (Session 166 - Whisper transcription + burned-in subtitles) | 'render_professional' (Session 167 - DaVinci/ffmpeg ProRes/DNxHD export) | 'apply_lut' (Session 167 - apply color LUT) | 'color_grade_professional' (Session 167 - DaVinci color science grading)",
                            "enum": ["add_text_overlay", "apply_color_grading", "upscale", "apply_effect", "extract_frame", "reverse", "trim", "speed_change", "concatenate", "rotate_flip", "fade", "crop_resize", "audio_control", "picture_in_picture", "add_watermark", "blur_region", "stabilize_video", "add_text_animation", "chroma_key", "export_for_platform", "video_transition", "auto_caption", "render_professional", "apply_lut", "color_grade_professional"]
                        },
                        "video_id": {
                            "type": "string",
                            "description": "Video identifier(s) - supports SINGLE or BATCH: Single: '2' or UUID. BATCH (Session 166): Range '1-3', List '1, 2, 5', Combined '1-3, 5'. Works with ALL operations: upscale, effect, reverse, trim, speed, rotate, fade, crop, audio, watermark, blur, stabilize, text animation, green screen, export presets, auto-caption. Examples: 'stabilize videos 1-3', 'export videos 1, 2, 3 for TikTok', 'add captions to videos 5-8'. Each video processed sequentially. For picture_in_picture/transition: this is the BACKGROUND/first video."
                        },
                        "params": {
                            "type": "object",
                            "description": "For add_text_overlay: {text, position, start_second, duration, font_size}. For apply_color_grading: {style: 'cinematic_warm'}. For upscale: {scale_factor: 2 or 4, quality: 'high'}. For apply_effect: {effect: 'cinematic'|'vibrant'|'vintage'|'noir'|'warm'|'cool', intensity: 0.5-1.0}. For extract_frame: {timestamp: seconds, format: 'jpg'|'png'}. For reverse: {reverse_audio: true|false}. For trim: {start_time: seconds, end_time: seconds, keep_audio: true|false}. For speed_change: {speed: 0.5 for slow-mo, 2.0 for 2x speed, preserve_audio: true|false}. For concatenate: {video_ids: ['1', '2', '3'] - list of video IDs to combine}. For rotate_flip: {rotation: 90|180|270|'horizontal'|'vertical'|'both'}. For fade: {fade_in: seconds, fade_out: seconds, fade_color: 'black'|'white'}. For crop_resize: {mode: 'crop'|'resize'|'aspect', width, height, crop_x, crop_y, crop_width, crop_height, aspect: '16:9'|'9:16'|'1:1'|'4:3'}. For audio_control: {audio_operation: 'volume'|'mute'|'extract', volume: 1.5 for 150%, output_format: 'mp3'|'wav'|'aac'}. For picture_in_picture: {overlay_video_id: '2', position: 'top-left'|'top-right'|'bottom-left'|'bottom-right'|'center', scale: 0.25, margin: 10, opacity: 1.0}. For add_watermark: {image_id: '5' (watermark/logo image), position: 'top_left'|'top_right'|'bottom_left'|'bottom_right'|'center', scale: 0.15 (15% of video width), opacity: 0.8, margin: 20}. For blur_region: {region: 'top_left'|'top_right'|'bottom_left'|'bottom_right'|'center'|'full'|'custom', blur_strength: 1-30 (default 15), x, y, width, height (for custom), start_time, end_time (optional time range)}. For render_professional: {codec: 'prores_422'|'prores_422_hq'|'prores_4444'|'dnxhd'|'dnxhr_hq'|'h264'|'h265'} - PROFESSIONAL BROADCAST CODECS. For apply_lut: {lut_path: 'path/to/file.cube', intensity: 0.0-1.0}. For color_grade_professional: {grade_type: 'cinematic'|'vintage'|'noir'|'warm'|'cool'|'vibrant', saturation: 1.0, contrast: 1.0}.",
                            "properties": {
                                "text": {"type": "string"},
                                "position": {"type": "string", "default": "center"},
                                "start_second": {"type": "number", "default": 0},
                                "duration": {"type": "number", "default": 3},
                                "font_size": {"type": "integer", "default": 72},
                                "style": {"type": "string", "default": "cinematic_warm"},
                                "scale_factor": {"type": "integer", "enum": [2, 4], "default": 2, "description": "Session 154: Upscale factor (2x or 4x)"},
                                "quality": {"type": "string", "default": "high", "description": "Session 154: Upscale quality (high or medium)"},
                                "effect": {"type": "string", "enum": ["cinematic", "vibrant", "vintage", "noir", "warm", "cool"], "default": "cinematic", "description": "Session 154: Color grading effect"},
                                "intensity": {"type": "number", "default": 0.7, "description": "Session 154: Effect intensity (0.0-1.0)"},
                                "timestamp": {"type": "number", "default": 0, "description": "Session 159: Time in seconds to extract frame from (e.g., 5.0 for 5 seconds)"},
                                "format": {"type": "string", "enum": ["jpg", "png"], "default": "jpg", "description": "Session 159: Output format for extracted frame"},
                                "reverse_audio": {"type": "boolean", "default": True, "description": "Session 159: Whether to also reverse the audio (true) or make silent (false)"},
                                "start_time": {"type": "number", "default": 0, "description": "Session 159: Start time in seconds for trim operation"},
                                "end_time": {"type": "number", "description": "Session 159: End time in seconds for trim operation"},
                                "keep_audio": {"type": "boolean", "default": True, "description": "Session 159: Whether to keep audio in trimmed video"},
                                "speed": {"type": "number", "default": 1.0, "description": "Session 160: Speed multiplier (0.25-4.0). 0.5 = slow motion, 2.0 = 2x speed"},
                                "preserve_audio": {"type": "boolean", "default": True, "description": "Session 160: Whether to preserve audio (pitch-corrected) when changing speed"},
                                "video_ids": {"type": "array", "items": {"type": "string"}, "description": "Session 160: List of video IDs to concatenate (for 'concatenate' operation)"},
                                "rotation": {"type": "string", "description": "Session 161: Rotation type - 90, 180, 270 (degrees), or 'horizontal', 'vertical', 'both' for flipping"},
                                "fade_in": {"type": "number", "default": 1.0, "description": "Session 161: Fade in duration in seconds (0 to disable)"},
                                "fade_out": {"type": "number", "default": 1.0, "description": "Session 161: Fade out duration in seconds (0 to disable)"},
                                "fade_color": {"type": "string", "enum": ["black", "white"], "default": "black", "description": "Session 161: Fade color"},
                                "mode": {"type": "string", "enum": ["crop", "resize", "aspect"], "default": "resize", "description": "Session 161: Crop/resize mode"},
                                "width": {"type": "integer", "description": "Session 161: Target width for resize"},
                                "height": {"type": "integer", "description": "Session 161: Target height for resize"},
                                "crop_x": {"type": "integer", "default": 0, "description": "Session 161: Crop start X position"},
                                "crop_y": {"type": "integer", "default": 0, "description": "Session 161: Crop start Y position"},
                                "crop_width": {"type": "integer", "description": "Session 161: Crop width"},
                                "crop_height": {"type": "integer", "description": "Session 161: Crop height"},
                                "aspect": {"type": "string", "enum": ["16:9", "9:16", "1:1", "4:3", "3:4", "21:9", "square", "portrait", "landscape", "cinematic"], "default": "16:9", "description": "Session 161: Target aspect ratio"},
                                "audio_operation": {"type": "string", "enum": ["volume", "mute", "extract"], "default": "volume", "description": "Session 161: Audio control operation"},
                                "volume": {"type": "number", "default": 1.0, "description": "Session 161: Volume multiplier (0.5 = 50%, 1.5 = 150%, 2.0 = 200%)"},
                                "output_format": {"type": "string", "enum": ["mp3", "wav", "aac", "m4a", "flac"], "default": "mp3", "description": "Session 161: Audio extraction output format"},
                                "overlay_video_id": {"type": "string", "description": "Session 161: Video ID for PiP overlay (smaller video)"},
                                "scale": {"type": "number", "default": 0.25, "description": "Session 161: PiP overlay scale (0.1-0.8, 0.25 = 25% of background size)"},
                                "margin": {"type": "integer", "default": 10, "description": "Session 161: PiP margin from edge in pixels"},
                                "opacity": {"type": "number", "default": 1.0, "description": "Session 161: PiP overlay opacity (0.0-1.0)"},
                                "image_id": {"type": "string", "description": "Session 163: Watermark/logo image ID (for add_watermark operation)"},
                                "region": {"type": "string", "enum": ["top_left", "top_right", "bottom_left", "bottom_right", "center", "full", "custom"], "default": "center", "description": "Session 163: Blur region (for blur_region operation)"},
                                "blur_strength": {"type": "integer", "default": 15, "description": "Session 163: Blur intensity 1-30 (higher = more blur)"},
                                "codec": {"type": "string", "enum": ["prores_422", "prores_422_hq", "prores_4444", "dnxhd", "dnxhr_hq", "h264", "h265"], "default": "prores_422_hq", "description": "Session 167: Professional codec for render_professional - ProRes 422/4444, DNxHD/DNxHR for broadcast"},
                                "grade_type": {"type": "string", "enum": ["cinematic", "vintage", "noir", "warm", "cool", "vibrant"], "default": "cinematic", "description": "Session 167: Color grade preset for color_grade_professional"}
                            }
                        },
                        "project_id": {"type": "string"}
                    },
                    "required": ["operation", "video_id"]
                }
            },

            # Session 133: Character Training Agent (FLUX LoRA for style consistency)
            {
                "type": "function",
                "name": "character_training_agent",
                "description": "Train a FLUX LoRA model to learn a consistent visual style from 4-10 example images. Creates reusable style model that can be applied to all future generations. Use when user wants to 'train project style', 'create custom style', 'learn my visual aesthetic', or 'make consistent style'. Perfect for brand consistency across all content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of 4-10 image IDs to train on. Can use sequential numbers (e.g., '1', '2') or full UUIDs. These images should have similar style/aesthetic for best results."
                        },
                        "style_name": {
                            "type": "string",
                            "description": "Name for this trained style model (e.g., 'pixar-robot-style', 'minimalist-logo-style', 'ai-content-generation-company-style'). Use lowercase with hyphens."
                        },
                        "trigger_word": {
                            "type": "string",
                            "description": "Optional trigger word to activate this style in prompts (e.g., 'PIXBOT', 'MINILOGO'). If not provided, uses uppercase version of style_name."
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Optional project ID to associate trained model with. Model can then be used automatically in project workflows."
                        }
                    },
                    "required": ["image_ids", "style_name"]
                }
            },

            # Session 173: Co-Leadership Agent (Conversational AI-Human collaboration)
            # Session 293: Updated to defer to workflow_orchestration_agent for research+create
            {
                "type": "function",
                "name": "coleadership_agent",
                "description": "Get opinions from AI executive team on EXISTING content or decisions. Use when user asks 'what do you think about X', 'get feedback on image 5', 'is this style good'. IMPORTANT: If user wants research AND creation (e.g., 'research X and create Y'), use workflow_orchestration_agent instead - it includes executive review automatically. Only use this for standalone opinion requests on existing work.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "question": {
                            "type": "string",
                            "description": "The decision question or topic to get opinions on. Include any context from the user's message."
                        },
                        "image_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of image IDs being discussed (e.g., ['32', '15']). Extract any image numbers mentioned in the user's message."
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional context about the decision (e.g., 'considering for style training', 'evaluating creative direction')"
                        },
                        "participants": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Which agents to consult. Defaults to all. Options: 'CTOAgent', 'COOAgent', 'CreativeDirectorAgent', 'CFOAgent', 'DataAnalystAgent'"
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project ID for context"
                        }
                    },
                    "required": ["question"]
                }
            },

            # Session 175: Talking Character Agent (Image + Text → Talking Video)
            {
                "type": "function",
                "name": "talking_character_agent",
                "description": "⭐ PREFERRED for 'make image talk' requests ⭐ Create complete talking character videos from a still image and text script in ONE STEP. This pipeline combines Text-to-Speech (ElevenLabs) + Image-to-Video (Runway) + Lip Sync to bring static characters to life with natural speech and mouth movements. NOW SUPPORTS CARTOON/STYLIZED CHARACTERS! Use when user wants: 'make image X talk and say...', 'create talking video', 'add speech to image', 'animate character with voice', 'talking character', 'AI spokesperson video', etc. IMPORTANT: When user says 'using [name] voice' or 'with [name] voice', extract that name as the voice parameter! Available voices: Rachel, Antoni, Bella, Callum, Charlotte, Daniel, Domi, Elli, Emily, George, Matilda, Sam. This is the ONLY tool that generates speech + animation + lip sync automatically. Works great with both photorealistic AND cartoon/Pixar-style characters! Perfect for: YouTube explainer videos, marketing content, AI spokesperson videos, social media content. Cost: ~$0.60-1.00 per 10-second video.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "image_id": {
                            "type": "string",
                            "description": "Character image to animate. Can use sequential number (e.g., '1', '5') or full UUID. Image should show a clear face for best lip sync results."
                        },
                        "text": {
                            "type": "string",
                            "description": "Script text for the character to speak. Keep it concise - 1-2 sentences work best for 5-10 second videos."
                        },
                        "voice": {
                            "type": "string",
                            "default": "Rachel",
                            "enum": ["Rachel", "Antoni", "Bella", "Callum", "Charlotte", "Daniel", "Domi", "Elli", "Emily", "George", "Matilda", "Sam"],
                            "description": "ElevenLabs voice name. MUST extract from user's request if they say 'using [name] voice' or 'with [name] voice'. Rachel=professional female (default), Antoni=male narrator, Daniel=deep male, Emily=calm female, Bella=expressive female, George=warm male."
                        },
                        "duration": {
                            "type": "integer",
                            "enum": [5, 10],
                            "default": 5,
                            "description": "Target video duration in seconds. 5 seconds = ~15-20 words, 10 seconds = ~30-40 words."
                        },
                        "motion_prompt": {
                            "type": "string",
                            "default": "subtle talking motion, slight head movements",
                            "description": "Optional description of character motion during speech (e.g., 'subtle talking motion', 'expressive hand gestures', 'professional presenter stance')."
                        },
                        "sync_mode": {
                            "type": "string",
                            "enum": ["cut_off", "loop", "bounce"],
                            "default": "cut_off",
                            "description": "How to handle duration mismatch between audio and video: cut_off (cut video when audio ends - recommended), loop (repeat video), bounce (reverse-repeat video)."
                        },
                        "temperature": {
                            "type": "number",
                            "default": 0.5,
                            "description": "Lip sync expression intensity 0-1. 0.5 = natural (recommended), 0.8 = expressive, 0.3 = subtle."
                        },
                        "lipsync_model": {
                            "type": "string",
                            "enum": ["auto", "latentsync", "sync_labs"],
                            "default": "auto",
                            "description": "Which lip sync model to use: 'auto' (cartoon-optimized - RECOMMENDED), 'latentsync' (ByteDance - best for cartoon/stylized/Pixar characters), 'sync_labs' (best for photorealistic humans). Default 'auto' intelligently selects cartoon-optimized model for best results."
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Optional project ID to associate the talking character video with."
                        }
                    },
                    "required": ["image_id", "text"]
                }
            },

            # Session 184: Web Search Tool - RESTORED from Session 65!
            # Session 293: Updated to defer to workflow_orchestration_agent for research+create
            {
                "type": "function",
                "name": "web_search",
                "description": "Search the web for information ONLY. Use for pure research requests like 'what's trending', 'look up X', 'find information about Y'. IMPORTANT: If user wants BOTH research AND creation (e.g., 'research X and create/generate Y'), use workflow_orchestration_agent instead - it handles the complete workflow internally. Only use web_search for standalone research with no creation request.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to find information about"
                        }
                    },
                    "required": ["query"]
                }
            },

            # Session 184: Create Brand Video Tool - RESTORED from Session 67!
            {
                "type": "function",
                "name": "create_brand_video",
                "description": "Create a complete brand video from concept to finished product using automated workflow. Orchestrates Runway ML video generation with professional styling. Use when user wants a complete brand video, promotional video, or multiple video clips for a brand/project. Generates 2-5 video clips that can later be chained with transitions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "brand_name": {
                            "type": "string",
                            "description": "The brand or company name"
                        },
                        "concept": {
                            "type": "string",
                            "description": "The video concept or message (e.g., 'luxury coffee experience', 'eco-friendly technology', 'cyberpunk aesthetics')"
                        },
                        "style": {
                            "type": "string",
                            "enum": ["cinematic", "modern", "playful", "elegant", "energetic"],
                            "default": "modern",
                            "description": "Visual style: cinematic (dramatic lighting), modern (clean minimal), playful (colorful fun), elegant (sophisticated), energetic (fast-paced)"
                        },
                        "include_branding": {
                            "type": "boolean",
                            "default": True,
                            "description": "Whether to add brand name text overlay at start/end"
                        },
                        "video_count": {
                            "type": "integer",
                            "default": 3,
                            "description": "Number of video clips to generate (2-5)"
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Optional project ID to associate videos with"
                        }
                    },
                    "required": ["brand_name", "concept"]
                }
            },

            # Session 238: Workflow Orchestration Agent - THE FIX!
            # This was missing, causing GPT to call individual tools instead of the unified workflow
            # Session 495: Updated to handle "create content based on this research" with pre-existing research
            {
                "type": "function",
                "name": "workflow_orchestration_agent",
                "description": "⚡ FOR VISUAL/IMAGE CONTENT ONLY! Use ONLY when user wants IMAGES, LOGOS, THUMBNAILS, or VIDEOS generated from research. Examples: 'Research AI and create logos', 'Make thumbnails about tech'. ⛔ NEVER USE for written content like blog posts, articles, podcast scripts, newsletters - use content_writer_agent instead! Available workflows: 'research_and_create_logos', 'research_and_create_images', 'youtube_thumbnail_package', 'brand_identity_package', 'product_photography_kit', 'logo_to_video'. All of these produce IMAGES/VIDEOS, not written text!",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "workflow": {
                            "type": "string",
                            "enum": ["research_and_create_logos", "research_and_create_images", "youtube_thumbnail_package", "brand_identity_package", "product_photography_kit", "logo_to_video"],
                            "description": "Workflow type: 'research_and_create_logos' (most common - for logo requests), 'research_and_create_images' (for general artwork/illustrations), 'youtube_thumbnail_package' (for YouTube thumbnails), 'brand_identity_package' (full brand kit), 'product_photography_kit' (product photos), 'logo_to_video' (animate a logo)"
                        },
                        "topic": {
                            "type": "string",
                            "description": "The content topic to visualize. CRITICAL: If message contains '--- RESEARCH CONTEXT ---', extract the MAIN SUBJECT from the research (e.g., 'AI startups' if research is about AI startup trends, 'cybersecurity' if about security). DO NOT extract random words like animal names from research text! Extract the PRIMARY TOPIC being discussed."
                        },
                        "count": {
                            "type": "integer",
                            "default": 3,
                            "description": "Number of images/logos to generate (1-5)"
                        },
                        "style_preferences": {
                            "type": "string",
                            "description": "CRITICAL: Extract ANY style mentioned by user! Animation styles: 'pixar', 'disney', 'dreamworks', 'ghibli', 'anime', 'cartoon'. Art styles: 'watercolor', 'cyberpunk', 'minimalist', 'retro'. If user says 'DreamWorks style donkey' → style_preferences='dreamworks'. If user says 'Pixar-style mascot' → style_preferences='pixar'. ALWAYS extract the style - this determines whether we generate mascot characters vs flat geometric icons!"
                        },
                        "image_id": {
                            "type": "string",
                            "description": "For 'logo_to_video' workflow: the logo image ID to animate"
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Optional project ID to associate all generated content with"
                        },
                        "user_message": {
                            "type": "string",
                            "description": "CRITICAL: ALWAYS pass the EXACT original user message here verbatim INCLUDING any '--- RESEARCH CONTEXT ---' section! This ensures the workflow can use provided research and no style info is lost. Copy-paste EVERYTHING the user sent."
                        }
                    },
                    "required": ["workflow", "topic", "user_message"]
                }
            },

            # Session 496: Content Writer Agent - Transform research into written content
            # Session 521: Upgraded to use real-time spider data + instruct to call image agent separately
            {
                "type": "function",
                "name": "content_writer_agent",
                "description": "📝 MANDATORY for WRITTEN TEXT content! Use when user says 'write', 'blog post', 'podcast script', 'video script', 'article', 'newsletter', 'social thread'. ⚡ TRIGGER PHRASES: 'write a blog post', 'write a podcast script', 'write a video script', 'create a blog', 'turn into article', 'make a newsletter'. This produces WRITTEN TEXT using REAL-TIME spider data (no more 2023 dates!). ⚠️ IMPORTANT: If user ALSO asks for an image/header/banner, you MUST call BOTH this tool AND image_generation_agent separately. Example: 'write a blog post about AI and create a header image' requires TWO tool calls. Output: ready-to-publish text content with title, sections, and formatting based on current trends.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content_type": {
                            "type": "string",
                            "enum": ["blog_post", "podcast_script", "video_script", "article", "social_thread", "newsletter"],
                            "description": "Type of content to create: 'blog_post' (SEO-optimized blog), 'podcast_script' (conversational with segments), 'video_script' (scenes and narration), 'article' (professional with headline/lead/CTA), 'social_thread' (connected posts with hashtags), 'newsletter' (email with subject/preview/sections)"
                        },
                        "topic": {
                            "type": "string",
                            "description": "The main topic to write about. If message contains '--- RESEARCH CONTEXT ---', extract the PRIMARY TOPIC from the research."
                        },
                        "tone": {
                            "type": "string",
                            "enum": ["professional", "conversational", "educational", "entertaining", "persuasive", "technical"],
                            "default": "professional",
                            "description": "Writing tone: 'professional' (clear, authoritative), 'conversational' (friendly, approachable), 'educational' (informative, patient), 'entertaining' (engaging, witty), 'persuasive' (compelling, action-oriented), 'technical' (precise, detailed)"
                        },
                        "target_audience": {
                            "type": "string",
                            "description": "Who the content is for (e.g., 'tech entrepreneurs', 'general audience', 'marketing professionals')"
                        },
                        "word_count": {
                            "type": "integer",
                            "default": 1500,
                            "description": "Approximate word count for the content"
                        },
                        "research_context": {
                            "type": "string",
                            "description": "CRITICAL: If message contains '--- RESEARCH CONTEXT ---', pass the FULL research content here. This will be used as the source material for the written content."
                        }
                    },
                    "required": ["content_type", "topic"]
                }
            },

            # Session 293: Business Research Agents (NO image/video API credits!)
            # These agents provide competitor analysis, customer research, and market intelligence
            {
                "type": "function",
                "name": "competitor_analysis_agent",
                "description": "⭐ BUSINESS RESEARCH - NO API CREDITS! Comprehensive competitor and market analysis. Use for: 'Research the X market for my startup', 'Analyze competitors in X', 'Who are the competitors in X?', 'SWOT analysis for X market', 'What's the competitive landscape for X?'. This agent provides: market research with trends, competitor identification and deep analysis, SWOT analysis, feature comparison, pricing analysis, market positioning recommendations. IMPORTANT: This is PURE RESEARCH - no image/video generation. Uses spider network + web search for real data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "market": {
                            "type": "string",
                            "description": "The market or industry to research (e.g., 'AI writing assistants', 'coffee subscription services', 'fitness apps')"
                        },
                        "focus_areas": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional specific areas to focus on (e.g., ['pricing', 'features', 'target_audience']). Defaults to comprehensive analysis."
                        },
                        "competitor_names": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional specific competitors to analyze. If not provided, agent will discover top competitors."
                        },
                        "user_context": {
                            "type": "string",
                            "description": "Additional context about the user's business idea or goals to make analysis more relevant"
                        }
                    },
                    "required": ["market"]
                }
            },

            {
                "type": "function",
                "name": "customer_research_agent",
                "description": "⭐ CUSTOMER RESEARCH - NO API CREDITS! Customer persona and pain point research. Use for: 'Build customer personas for X', 'What are customer pain points for X?', 'Research customer needs for X market', 'Who buys X products?', 'Customer sentiment analysis for X'. This agent provides: 2-3 detailed customer personas with demographics, pain point extraction from Reddit/forums/reviews, customer motivations and goals, sentiment analysis, direct customer quotes and examples, buying behavior insights. IMPORTANT: This is PURE RESEARCH - no image/video generation. Uses spider network (especially Reddit) for real customer data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "market": {
                            "type": "string",
                            "description": "The market or product category to research customers for (e.g., 'AI writing tools', 'home fitness equipment')"
                        },
                        "persona_count": {
                            "type": "integer",
                            "default": 3,
                            "description": "Number of customer personas to build (1-5)"
                        },
                        "focus_on": {
                            "type": "string",
                            "enum": ["pain_points", "desires", "buying_behavior", "all"],
                            "default": "all",
                            "description": "What aspect of customer research to focus on"
                        },
                        "user_context": {
                            "type": "string",
                            "description": "Additional context about the user's product or service to make personas more relevant"
                        }
                    },
                    "required": ["market"]
                }
            },

            # Session 312: Strategy Agents (connecting 5 disconnected agents to Personal Assistant)
            # Brand Identity Agent - manages brand consistency
            {
                "type": "function",
                "name": "brand_identity_agent",
                "description": "Manage brand identity and consistency. Use when the user wants to set brand colors, get brand profile, enhance prompts with brand styling, or generate brand guidelines. Helps maintain consistent branding across all generated content.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["get_profile", "set_colors", "enhance_prompt", "generate_guidelines", "suggest_colors"],
                            "description": "Action: get_profile (current brand settings), set_colors (define brand palette), enhance_prompt (add brand styling to a prompt), generate_guidelines (create brand guide), suggest_colors (get colors for industry)"
                        },
                        "primary_color": {
                            "type": "string",
                            "description": "Primary brand color hex code (e.g., '#FF5733') - for set_colors action"
                        },
                        "secondary_color": {
                            "type": "string",
                            "description": "Secondary brand color hex code - for set_colors action"
                        },
                        "accent_color": {
                            "type": "string",
                            "description": "Accent brand color hex code - for set_colors action"
                        },
                        "prompt": {
                            "type": "string",
                            "description": "The prompt to enhance with brand styling - for enhance_prompt action"
                        },
                        "industry": {
                            "type": "string",
                            "description": "Industry for color suggestions (e.g., 'tech', 'healthcare', 'finance') - for suggest_colors action"
                        }
                    },
                    "required": ["action"]
                }
            },

            # Content Strategy Agent - content recommendations from trends
            {
                "type": "function",
                "name": "content_strategy_agent",
                "description": "Get content strategy recommendations based on spider intelligence and trending topics. Use when user asks what content to create, wants trending topics, or needs a content calendar. Connects trend data to actionable content recommendations.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["get_recommendations", "get_trending", "get_calendar", "analyze_opportunity"],
                            "description": "Action: get_recommendations (what to create), get_trending (hot topics), get_calendar (posting schedule), analyze_opportunity (evaluate specific idea)"
                        },
                        "niche": {
                            "type": "string",
                            "description": "Content niche (e.g., 'tech', 'lifestyle', 'gaming') - optional filter for recommendations"
                        },
                        "content_type": {
                            "type": "string",
                            "enum": ["logos", "thumbnails", "social", "videos", "all"],
                            "default": "all",
                            "description": "Type of content to recommend"
                        },
                        "opportunity_description": {
                            "type": "string",
                            "description": "Description of content opportunity to analyze - for analyze_opportunity action"
                        }
                    },
                    "required": ["action"]
                }
            },

            # SEO Optimizer Agent - hashtags, keywords, metadata
            {
                "type": "function",
                "name": "seo_optimizer_agent",
                "description": "Optimize content for discoverability with SEO. Use when user wants hashtags, keywords, descriptions, alt text, or metadata for their images/videos. Generates platform-specific optimization.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["get_hashtags", "suggest_keywords", "optimize_image", "optimize_for_platform"],
                            "description": "Action: get_hashtags (trending hashtags), suggest_keywords (SEO keywords), optimize_image (full SEO for image), optimize_for_platform (platform-specific optimization)"
                        },
                        "topic": {
                            "type": "string",
                            "description": "Topic or description to generate hashtags/keywords for"
                        },
                        "image_id": {
                            "type": "string",
                            "description": "Image ID to optimize - for optimize_image action"
                        },
                        "platform": {
                            "type": "string",
                            "enum": ["instagram", "twitter", "linkedin", "pinterest", "youtube", "tiktok"],
                            "description": "Target platform for optimization - for optimize_for_platform action"
                        },
                        "hashtag_count": {
                            "type": "integer",
                            "default": 10,
                            "description": "Number of hashtags to generate (5-30)"
                        }
                    },
                    "required": ["action"]
                }
            },

            # Trend Analysis Agent - market intelligence
            {
                "type": "function",
                "name": "trend_analysis_agent",
                "description": "Analyze trends and find emerging opportunities using spider intelligence. Use when user wants trend analysis, daily briefings, opportunity discovery, or sector analysis. Provides actionable insights from market data.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["analyze_sector", "find_opportunities", "daily_briefing", "get_insights"],
                            "description": "Action: analyze_sector (deep dive), find_opportunities (emerging trends), daily_briefing (today's summary), get_insights (quick insights for prompt)"
                        },
                        "sector": {
                            "type": "string",
                            "description": "Sector to analyze (e.g., 'ai', 'design', 'marketing', 'tech')"
                        },
                        "topic": {
                            "type": "string",
                            "description": "Topic for insights - used to enhance generation prompts"
                        }
                    },
                    "required": ["action"]
                }
            },

            # Social Media Agent - platform-specific content
            {
                "type": "function",
                "name": "social_media_agent",
                "description": "Create platform-optimized social media content. Use when user wants content for specific platforms, multi-platform content, content calendars, or platform specs. Knows optimal dimensions, hashtag limits, and best practices for each platform.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["create_for_platform", "create_multi_platform", "get_platform_specs", "create_calendar", "suggest_content_type"],
                            "description": "Action: create_for_platform (single platform), create_multi_platform (all platforms), get_platform_specs (dimensions/limits), create_calendar (posting schedule), suggest_content_type (what works best)"
                        },
                        "platform": {
                            "type": "string",
                            "enum": ["instagram", "twitter", "linkedin", "pinterest", "youtube", "tiktok", "facebook"],
                            "description": "Target platform - for single platform actions"
                        },
                        "content_description": {
                            "type": "string",
                            "description": "Description of the content to create"
                        },
                        "brand_name": {
                            "type": "string",
                            "description": "Brand name for content - optional"
                        },
                        "calendar_days": {
                            "type": "integer",
                            "default": 7,
                            "description": "Number of days for content calendar (1-30)"
                        }
                    },
                    "required": ["action"]
                }
            },

            # Session 313: Creative Director Agent - high-level creative guidance
            {
                "type": "function",
                "name": "creative_director_agent",
                "description": "Get high-level creative direction and guidance for visual projects. Use when user wants prompt enhancement, creative direction for a project, design critique, or creative insights. This agent reviews prompts, suggests improvements, ensures consistency, and provides expert creative guidance based on design principles and trends.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["review_prompt", "establish_direction", "critique_design", "get_insights"],
                            "description": "Action: review_prompt (enhance a creative prompt with design principles), establish_direction (set creative direction for entire project), critique_design (get constructive feedback on a design), get_insights (creative insights for a topic)"
                        },
                        "prompt": {
                            "type": "string",
                            "description": "The creative prompt to review and enhance - for review_prompt action"
                        },
                        "content_type": {
                            "type": "string",
                            "enum": ["logo", "thumbnail", "social_media", "brand_identity"],
                            "description": "Type of content - helps provide relevant design principles"
                        },
                        "project_brief": {
                            "type": "string",
                            "description": "Description of the project - for establish_direction action"
                        },
                        "target_audience": {
                            "type": "string",
                            "description": "Target audience for the content"
                        },
                        "industry": {
                            "type": "string",
                            "description": "Industry category (tech, healthcare, food, etc.)"
                        },
                        "design_description": {
                            "type": "string",
                            "description": "Description of the design to critique - for critique_design action"
                        },
                        "intended_purpose": {
                            "type": "string",
                            "description": "What the design is for - for critique_design action"
                        },
                        "topic": {
                            "type": "string",
                            "description": "Topic to get creative insights for - for get_insights action"
                        }
                    },
                    "required": ["action"]
                }
            },

            # Session 313: Opportunity Scoring Agent - spider data to opportunities
            {
                "type": "function",
                "name": "opportunity_scoring_agent",
                "description": "Transform spider intelligence data into scored, actionable opportunities. Use when user wants to find profitable content opportunities, analyze trends for monetization, score spider data for business potential, or discover top opportunities from market data. Scores opportunities on profit potential, competition level, effort required, and time sensitivity.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["score_data", "analyze_trend", "get_top"],
                            "description": "Action: score_data (score recent spider data for opportunities), analyze_trend (score a specific trend topic), get_top (get highest-scoring opportunities)"
                        },
                        "hours": {
                            "type": "integer",
                            "default": 24,
                            "description": "Look back period in hours for spider data - for score_data action"
                        },
                        "limit": {
                            "type": "integer",
                            "default": 10,
                            "description": "Maximum number of opportunities to return"
                        },
                        "trend_topic": {
                            "type": "string",
                            "description": "The trend topic to analyze and score - for analyze_trend action"
                        },
                        "min_score": {
                            "type": "integer",
                            "default": 50,
                            "description": "Minimum overall score threshold (0-100) - for get_top action"
                        }
                    },
                    "required": ["action"]
                }
            },

            # Session 313: Trained Creation Agent - generate with trained LoRA models
            {
                "type": "function",
                "name": "trained_creation_agent",
                "description": "Generate images using trained character/style LoRA models. Use when user wants to generate images with a previously trained character or style, references a trained model by name, or wants to use custom LoRA weights. Requires a trained model from character_training_agent.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Text description of the image to generate with the trained style/character"
                        },
                        "character_model_name": {
                            "type": "string",
                            "description": "Name or ID of the trained character/style model to use"
                        },
                        "lora_scale": {
                            "type": "number",
                            "default": 0.8,
                            "description": "Strength of LoRA effect (0.0-1.0, default 0.8)"
                        },
                        "width": {
                            "type": "integer",
                            "default": 1024,
                            "description": "Image width in pixels"
                        },
                        "height": {
                            "type": "integer",
                            "default": 1024,
                            "description": "Image height in pixels"
                        },
                        "num_outputs": {
                            "type": "integer",
                            "default": 1,
                            "description": "Number of images to generate (1-4)"
                        }
                    },
                    "required": ["prompt", "character_model_name"]
                }
            },

            # Session 313: CTO Agent - technical architecture and planning
            {
                "type": "function",
                "name": "cto_agent",
                "description": "Get technical architecture analysis, feature planning, and code review guidance. Use when user wants technical analysis, architectural recommendations, implementation planning, documentation review, or agent coordination for complex tasks. The CTO Agent understands the entire codebase.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["analyze_feature", "plan_implementation", "analyze_documentation", "coordinate_agents"],
                            "description": "Action: analyze_feature (assess architecture/code quality), plan_implementation (create implementation plan without executing), analyze_documentation (review docs for gaps), coordinate_agents (orchestrate multiple agents)"
                        },
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature to analyze or implement"
                        },
                        "description": {
                            "type": "string",
                            "description": "Description of the feature or task"
                        },
                        "scope": {
                            "type": "string",
                            "enum": ["feature", "module", "platform"],
                            "default": "feature",
                            "description": "Scope of analysis"
                        },
                        "required_agents": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of agent names to coordinate (for coordinate_agents action)"
                        },
                        "task": {
                            "type": "string",
                            "description": "Task to coordinate agents for"
                        }
                    },
                    "required": ["action"]
                }
            },

            # Session 313: COO Agent - operations and sprint planning
            {
                "type": "function",
                "name": "coo_agent",
                "description": "Get operations planning, roadmap analysis, sprint planning, and risk identification. Use when user wants project planning, sprint recommendations, risk analysis, or operational strategy. Provides strategic planning without execution.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["analyze_roadmap", "propose_sprint", "identify_risks"],
                            "description": "Action: analyze_roadmap (strategic roadmap analysis), propose_sprint (plan next sprint with tasks), identify_risks (identify blockers and risks)"
                        },
                        "project_slug": {
                            "type": "string",
                            "description": "Project identifier for context"
                        },
                        "feature_name": {
                            "type": "string",
                            "description": "Specific feature to focus on"
                        },
                        "scope": {
                            "type": "string",
                            "enum": ["project", "feature", "platform"],
                            "default": "project",
                            "description": "Scope of analysis"
                        },
                        "sprint_duration": {
                            "type": "string",
                            "default": "2 weeks",
                            "description": "Sprint length for propose_sprint action"
                        }
                    },
                    "required": ["action"]
                }
            },

            # Session 313: Meeting Coordinator Agent - executive boardroom
            {
                "type": "function",
                "name": "meeting_coordinator_agent",
                "description": "Coordinate executive boardroom meetings between AI agents. Use when user wants multiple agents to collaborate on a topic, needs strategic alignment between CTO and COO, or wants synthesized decisions from agent discussions. Collects perspectives, synthesizes discussion, and extracts decisions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "The meeting topic/agenda to discuss"
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Optional project context for the meeting"
                        },
                        "participants": {
                            "type": "array",
                            "items": {"type": "string"},
                            "default": ["CTOAgent", "COOAgent"],
                            "description": "List of agent names to participate (default: CTO and COO)"
                        }
                    },
                    "required": ["topic"]
                }
            },

            # Session 313: Content Executor Agent - AI content generation
            {
                "type": "function",
                "name": "content_executor_agent",
                "description": "Execute AI content creation tasks. Use when user wants to generate blog posts, social media content, email copy, or other written content. Creates SEO-optimized content with proper formatting.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "Description of the content to create"
                        },
                        "content_type": {
                            "type": "string",
                            "enum": ["blog_post", "social_media", "email", "landing_page", "product_description"],
                            "default": "blog_post",
                            "description": "Type of content to generate"
                        },
                        "target_audience": {
                            "type": "string",
                            "description": "Target audience for the content"
                        },
                        "tone": {
                            "type": "string",
                            "enum": ["professional", "casual", "persuasive", "informative", "entertaining"],
                            "default": "professional",
                            "description": "Tone/style of the content"
                        }
                    },
                    "required": ["task"]
                }
            },

            # Session 313: AI Project Builder Agent - build AI projects from strategies
            {
                "type": "function",
                "name": "ai_project_builder_agent",
                "description": "Build complete AI projects from monetization strategies discovered by spiders. Use when user wants to create an AI application, build a project from opportunity data, or scaffold a new AI-powered tool. Creates ready-to-launch project with code files.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "Description of the AI project to build"
                        },
                        "project_type": {
                            "type": "string",
                            "enum": ["content_generator", "ai_assistant", "automation_tool", "analytics_dashboard"],
                            "description": "Type of AI project to build"
                        },
                        "use_spider_strategy": {
                            "type": "boolean",
                            "default": True,
                            "description": "Whether to use spider-discovered monetization strategies"
                        }
                    },
                    "required": ["task"]
                }
            },

            # Session 337: Brand Strategy Agent - comprehensive brand strategy research
            {
                "type": "function",
                "name": "brand_strategy_agent",
                "description": "Create comprehensive BRAND STRATEGY research by reading existing project research. Use this when user wants to: 'create a brand strategy', 'develop brand identity', 'brand positioning', 'brand guidelines', 'branding strategy'. This agent reads existing competitor analysis and customer research from the project, then synthesizes actionable brand recommendations including positioning, messaging, visual direction, and differentiation. Must be used INSIDE a project context.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Brand/business topic to analyze (e.g., 'AI podcast platform', 'coffee shop')"
                        },
                        "project_id": {
                            "type": "string",
                            "description": "Project ID to read existing research from and save results to"
                        }
                    },
                    "required": ["topic"]
                }
            },

            # Session 951: Platform Query Tool - Query platform data (reports, deliverables, initiatives)
            {
                "type": "function",
                "name": "platform_query_tool",
                "description": "Query platform data including reports, deliverables, initiatives, and agent executions. Use when user asks: 'what reports have been written', 'show me deliverables', 'list initiatives', 'what has agent X produced', 'show recent blog posts', 'audit reports', 'what content exists'. This tool provides ACTUAL database access to platform data - not conceptual descriptions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query_type": {
                            "type": "string",
                            "enum": ["deliverables", "audit_reports", "initiatives", "agent_outputs", "content_summary"],
                            "description": "Type of data to query: 'deliverables' (blog posts, reports, analyses), 'audit_reports' (agent audit findings), 'initiatives' (tracked initiatives), 'agent_outputs' (what specific agents produced), 'content_summary' (overview of all content)"
                        },
                        "filters": {
                            "type": "object",
                            "description": "Optional filters for the query",
                            "properties": {
                                "agent_name": {"type": "string", "description": "Filter by agent name (e.g., 'ContentWriterAgent', 'MarketIntelligenceAgent')"},
                                "deliverable_type": {"type": "string", "description": "Filter deliverables by type: document, report, analysis, research, strategy, script"},
                                "category": {"type": "string", "description": "Filter by category (e.g., 'Marketing', 'Research', 'Technical')"},
                                "days": {"type": "integer", "default": 30, "description": "Look back period in days (default 30)"},
                                "limit": {"type": "integer", "default": 20, "description": "Maximum results to return (default 20)"}
                            }
                        }
                    },
                    "required": ["query_type"]
                }
            }
        ]

    # Session 125: Tool Execution Handler
    # Session 204: Updated to use AgentRouter for unified tool execution
    def _execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call from GPT.

        Session 204: Now routes through AgentRouter for most tools,
        falling back to legacy handlers for complex/special cases.

        Args:
            tool_call: Tool call dictionary from GPT response

        Returns:
            Dictionary with execution results
        """
        try:
            # Session 761: Track start time for response time metrics
            import time
            self._tool_start_time = time.time()

            function_name = tool_call['function']['name']
            arguments = json.loads(tool_call['function']['arguments'])

            # Session 126: Auto-inject project_id from context if available and not already in arguments
            if hasattr(self, '_current_context') and self._current_context:
                if 'project_id' in self._current_context and 'project_id' not in arguments:
                    arguments['project_id'] = self._current_context['project_id']
                    logger.info(f"💡 Auto-injected project_id: {arguments['project_id']}")

            logger.info(f"🔧 Executing tool: {function_name} with args: {arguments}")

            # Session 204: Try router-based execution first for supported tools
            # This integrates preference learning and unified agent architecture
            # Session 293: Added business research agents
            ROUTER_ENABLED_TOOLS = {
                # Research operations
                'web_search', 'research_topic', 'research',
                # Training operations
                'character_training_agent', 'train_character', 'train_style',
                # Talking character
                'talking_character_agent', 'create_talking_character',
                # Leadership operations
                'coleadership_agent', 'strategic_review',
                # Workflow operations
                'workflow_orchestration_agent', 'create_brand_video',
                'create_project_from_research',
                # Business research (Session 293) - no image/video credits
                'competitor_analysis_agent', 'customer_research_agent',
                # Session 337: Brand strategy agent
                'brand_strategy_agent',
                # Session 496: Content Writer Agent - written content from research
                'content_writer_agent',
            }

            if function_name in ROUTER_ENABLED_TOOLS:
                try:
                    from core.agent_router import AgentRouter
                    logger.info(f"🔀 Using AgentRouter for: {function_name}")

                    result = AgentRouter.execute_tool(
                        tool_name=function_name,
                        arguments=arguments,
                        user=self.user,
                        session=getattr(self, 'session', None),
                        project=getattr(self, 'project', None)
                    )

                    if result.get('success', True):
                        logger.info(f"✅ Router success for {function_name}")
                        self._last_tool_result = result
                        return result
                    else:
                        logger.warning(f"⚠️ Router failed, falling back to legacy: {result.get('error')}")
                        # Fall through to legacy handlers
                except Exception as e:
                    logger.warning(f"⚠️ Router error, falling back to legacy: {e}")
                    # Fall through to legacy handlers

            # Legacy handlers (Session 132) - gradually migrating to AgentRouter
            # These handlers have complex logic specific to this assistant
            if function_name == 'image_generation_agent':
                result = self._handle_image_generation_agent(arguments)
            elif function_name == 'image_editing_agent':
                result = self._handle_image_editing_agent(arguments)
            elif function_name == 'video_generation_agent':
                result = self._handle_video_generation_agent(arguments)
            elif function_name == 'audio_generation_agent':
                result = self._handle_audio_generation_agent(arguments)
            elif function_name == 'three_d_generation_agent':
                result = self._handle_three_d_generation_agent(arguments)
            elif function_name == 'video_editing_agent':
                result = self._handle_video_editing_agent(arguments)
            elif function_name == 'character_training_agent':
                result = self._handle_character_training_agent(arguments)
            elif function_name == 'coleadership_agent':
                result = self._handle_coleadership_agent(arguments)
            elif function_name == 'talking_character_agent':
                result = self._tool_talking_character(arguments)
            # Session 184: Restored tools for autonomous "research and create" workflow
            elif function_name == 'web_search':
                result = self._handle_web_search(arguments)
            elif function_name == 'create_brand_video':
                result = self._handle_create_brand_video(arguments)
            # Session 496: Workflow orchestration agent legacy handler
            elif function_name == 'workflow_orchestration_agent':
                result = self._handle_workflow_orchestration_agent(arguments)
            # Session 496: Content writer agent legacy handler
            elif function_name == 'content_writer_agent':
                result = self._handle_content_writer_agent(arguments)
            # Session 189: Create project from research workflow
            elif function_name == 'create_project_from_research':
                result = self._handle_create_project_from_research(arguments)
            # Session 293: Business research agents (no image/video API credits)
            elif function_name == 'competitor_analysis_agent':
                result = self._handle_competitor_analysis_agent(arguments)
            elif function_name == 'customer_research_agent':
                result = self._handle_customer_research_agent(arguments)
            # Session 337: Business research agents (use BaseBusinessResearchAgent)
            elif function_name == 'brand_strategy_agent':
                result = self._handle_brand_strategy_agent(arguments)
            elif function_name == 'content_strategy_agent':
                result = self._handle_content_strategy_agent(arguments)
            elif function_name == 'marketing_strategy_agent':
                result = self._handle_marketing_strategy_agent(arguments)
            # Session 312: Strategy agents (connected to router - legacy)
            elif function_name == 'brand_identity_agent':
                result = self._handle_strategy_agent('brand_identity_agent', arguments)
            elif function_name == 'seo_optimizer_agent':
                result = self._handle_strategy_agent('seo_optimizer_agent', arguments)
            elif function_name == 'trend_analysis_agent':
                result = self._handle_strategy_agent('trend_analysis_agent', arguments)
            elif function_name == 'social_media_agent':
                result = self._handle_strategy_agent('social_media_agent', arguments)
            # Session 313: Creative Director and Opportunity Scoring agents
            elif function_name == 'creative_director_agent':
                result = self._handle_creative_director_agent(arguments)
            elif function_name == 'opportunity_scoring_agent':
                result = self._handle_opportunity_scoring_agent(arguments)
            # Session 313: Executive and coordination agents
            elif function_name == 'trained_creation_agent':
                result = self._handle_trained_creation_agent(arguments)
            elif function_name == 'cto_agent':
                result = self._handle_cto_agent(arguments)
            elif function_name == 'coo_agent':
                result = self._handle_coo_agent(arguments)
            elif function_name == 'meeting_coordinator_agent':
                result = self._handle_meeting_coordinator_agent(arguments)
            # Session 313: Content Executor and AI Project Builder agents
            elif function_name == 'content_executor_agent':
                result = self._handle_content_executor_agent(arguments)
            elif function_name == 'ai_project_builder_agent':
                result = self._handle_ai_project_builder_agent(arguments)
            # Session 672: ML Pipeline Management Tools
            elif function_name == 'opportunity_manager_tool':
                result = self._handle_opportunity_manager_tool(arguments)
            elif function_name == 'task_manager_tool':
                result = self._handle_task_manager_tool(arguments)
            elif function_name == 'pipeline_orchestrator_tool':
                result = self._handle_pipeline_orchestrator_tool(arguments)
            elif function_name == 'revenue_tracker_tool':
                result = self._handle_revenue_tracker_tool(arguments)
            # Session 683: ML Analysis Tool - auto-select ML models for data analysis
            elif function_name == 'ml_analysis':
                result = self._handle_ml_analysis(arguments)
            # Session 674: Universal Agent Tool - connects PA to ALL agents
            elif function_name == 'universal_agent_tool':
                result = self._handle_universal_agent_tool(arguments)
            # Session 695: SKIN Layer - Workspace Tool for project execution
            elif function_name == 'workspace_tool':
                result = self._handle_workspace_tool(arguments)
            # Session 709: Body Vitals - Connect Brain to Body Systems
            elif function_name == 'get_body_vitals':
                result = self._handle_get_body_vitals(arguments)
            elif function_name == 'check_resource_budget':
                result = self._handle_check_resource_budget(arguments)
            elif function_name == 'get_system_alerts':
                result = self._handle_get_system_alerts(arguments)
            # Session 725: Intelligence Tools - Connect Brain to Intelligence System
            elif function_name == 'predictions_tool':
                result = self._handle_predictions_tool(arguments)
            elif function_name == 'gates_tool':
                result = self._handle_gates_tool(arguments)
            elif function_name == 'pilots_tool':
                result = self._handle_pilots_tool(arguments)
            # Session 796: Human Interface Layer - Connect PA to human decisions
            elif function_name == 'human_decisions_tool':
                result = self._handle_human_decisions_tool(arguments)
            # Session 800: Reasoning Engine - Connect PA to ThinkingAgent
            elif function_name == 'reasoning_engine_tool':
                result = self._handle_reasoning_engine_tool(arguments)
            # Session 951: Platform Query Tool - Query platform data
            elif function_name == 'platform_query_tool':
                result = self._handle_platform_query_tool(arguments)
            else:
                result = {
                    'success': False,
                    'error': f"Unknown agent: {function_name}"
                }

            # Session 135: Store tool result to preserve task_id for video polling
            self._last_tool_result = result
            logger.info(f"📦 Stored tool result: {result}")

            # Session 761: Track tool usage in AgentTool model
            self._track_tool_usage(function_name, result, start_time=getattr(self, '_tool_start_time', None))

            return result

        except Exception as e:
            logger.error(f"❌ Tool execution error: {e}")
            return {
                'success': False,
                'error': f"Tool execution failed: {str(e)}"
            }

    def _generate_ai_response(self, message: str, context: Dict[str, Any]) -> str:
        """
        Generate real AI response using LLMEnforcer.

        Session 266: Now integrates Super Platform for dynamic prompting:
        - QueryClassifier: Understands user intent (9 types)
        - ContextAggregator: Gathers spider data, memories, mood
        - Injects relevant context into prompts

        Args:
            message: User's message
            context: Context including user profile, memories, etc.

        Returns:
            AI-generated response string
        """
        logger.debug("_generate_ai_response() ENTERED")

        # Session 266: Super Platform Integration - Classify the query
        classification = None
        aggregated_context = None
        start_time = timezone.now()

        if self.query_classifier and SUPER_PLATFORM_AVAILABLE:
            try:
                classification = self.query_classifier.classify(message)
                self._last_classification = classification  # Store for learning loop
                logger.info(f"🎯 Query classified as {classification.primary_type.value} "
                           f"(confidence: {classification.confidence:.2f}, "
                           f"requires_spider: {classification.requires_spider_data})")
            except Exception as e:
                logger.warning(f"⚠️ Query classification failed: {e}")

        # Session 266: Aggregate context from Super Platform
        if classification and self.context_aggregator:
            try:
                aggregated_context = self.context_aggregator.aggregate(classification, message)
                logger.info(f"📊 Context aggregated from: {', '.join(aggregated_context.sources_used)}")
            except Exception as e:
                logger.warning(f"⚠️ Context aggregation failed: {e}")

        # Session 628: Build comprehensive context using MemoryContextService
        # This provides decay-weighted preferences, goals, and decisions
        memory_context_service = get_memory_context_service(self.user)
        memory_context = memory_context_service.get_prompt_context(self.user)
        if not memory_context:
            # Fallback to basic memory retrieval if service returns empty
            recent_memories = self.memory_manager.retrieve_memories(
                user=self.user,
                limit=5
            )
            memory_context = "\n".join([f"- {m['type']}: {m['content']}" for m in recent_memories])

        # Get agent activity context using UnifiedMemoryManager
        agent_activities = self.memory_manager.get_agent_activities(
            user=self.user,
            limit=5
        )
        agent_context = "\n".join([f"- {a['content']}" for a in agent_activities]) if agent_activities else "No recent agent activities"

        # Get cross-agent insights
        insights = self.memory_manager.get_cross_agent_insights(self.user)

        # Session 122: Smart Hybrid - Use project context if available, otherwise 10-min window
        if hasattr(self, 'project') and self.project:
            # Customer work: Full project access (spans hours/days)
            assets_context = self.get_project_assets_context(self.project)
        else:
            # Quick experiments: 10-minute window for rapid iteration
            assets_context = self.get_recent_assets_context()

        # Session 169 Phase 3: Get user's learned style preferences
        style_preferences_context = self._get_style_preferences_context()

        # Session 181: Get project brief context for AI guidance
        project_brief_context = self._get_project_brief_context()

        # Extract conversation history from context and load from database
        conversation_context = context.get('conversation_context', '')
        conversation_history = context.get('conversation_history', [])

        # Session 482: Prioritize session conversation history from frontend over database
        # This enables contextual follow-up questions like "research the first one"
        reference_context = ""
        if conversation_history and isinstance(conversation_history, list) and len(conversation_history) > 0:
            # Session 482: Resolve references like "the first one", "it", "that"
            if self.reference_resolver and REFERENCE_RESOLVER_AVAILABLE:
                try:
                    resolved_message, resolutions = self.reference_resolver.resolve_references(
                        message, conversation_history
                    )
                    if resolutions:
                        # Build reference context for the prompt
                        ref_lines = []
                        for r in resolutions:
                            if r.resolution_type == 'ordinal':
                                ref_lines.append(f"- '{r.original}' refers to: **{r.resolved}**")
                            elif r.resolution_type == 'pronoun':
                                ref_lines.append(f"- '{r.original}' likely refers to: {r.resolved}")
                        if ref_lines:
                            reference_context = "\n\n**Reference Resolution:**\n" + "\n".join(ref_lines)
                            logger.info(f"🔍 Session 482: Resolved {len(resolutions)} references")
                except Exception as e:
                    logger.warning(f"⚠️ Reference resolution failed: {e}")

            # Format the session history from frontend
            session_context_lines = []
            for msg in conversation_history[-10:]:  # Last 10 messages for context
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if content:
                    # Truncate very long messages for context
                    truncated = content[:500] + '...' if len(content) > 500 else content
                    session_context_lines.append(f"- {role.upper()}: {truncated}")
            if session_context_lines:
                conversation_context = "**Current Session History:**\n" + "\n".join(session_context_lines)
                # Add reference context if we resolved any references
                if reference_context:
                    conversation_context += reference_context
                logger.info(f"📝 Session 482: Using {len(conversation_history)} messages from session history")
        elif not conversation_context:
            # Fallback: Load recent conversation history from database
            recent_conversations = self._load_conversation_history(limit=5)
            if recent_conversations:
                conversation_context = self._format_conversation_context(recent_conversations)

        # Extract user context (it might be nested)
        user_context = context.get('user_context', {})
        user_first_name = user_context.get('first_name') or context.get('first_name', 'User')
        user_last_name = user_context.get('last_name') or context.get('last_name', '')

        # Session 266: Use central prompt registry instead of inline prompts
        from core.prompts import build_personal_assistant_prompt

        # Build dynamic context sections
        project_id = self._current_context.get('project_id') if hasattr(self, '_current_context') and self._current_context else None

        # Session 340: Build FULL project context from PartnershipProject (not just UUID)
        # Extract meaningful context from AI contributions to understand what the project is ACTUALLY about
        project_context_section = ""
        if project_id:
            try:
                from core.models_partnership import PartnershipProject
                partnership_project = PartnershipProject.objects.get(id=project_id)

                # Extract meaningful context from AI contributions
                ai_context_summary = ""
                if partnership_project.ai_contributions:
                    # Get the first AI analysis output (contains the actual research)
                    for contribution in partnership_project.ai_contributions:
                        if contribution.get('output'):
                            # Take first 500 chars of the analysis for context
                            ai_context_summary = contribution['output'][:500]
                            break

                # Build rich project context
                project_context_section = f"""- **Project Name:** {partnership_project.project_name}
- **Project Type:** {partnership_project.project_type or 'Not specified'}
- **Project Description:** {partnership_project.description or 'No description provided'}
- **Project ID:** {project_id}

**AI Analysis Context (from prior research):**
{ai_context_summary if ai_context_summary else 'No prior analysis available'}

**CRITICAL INSTRUCTIONS FOR TOOL CALLS:**
1. The project "{partnership_project.project_name}" should be understood by its RESEARCH CONTEXT above, NOT by interpreting the project name literally.
2. "Donkey Betz" is a PODCAST NAME - it has NOTHING to do with sports betting or gambling!
3. When generating tool parameters (like "niche", "market", "topic"), use the AI Analysis Context to understand the actual subject matter.
4. Do NOT infer topics from creative/branded project names - always rely on the description and research context."""
                logger.info(f"📁 Session 340: Injected rich project context: {partnership_project.project_name} - Type: {partnership_project.project_type}")
            except Exception as e:
                logger.warning(f"Failed to get PartnershipProject for prompt: {e}")
                project_context_section = f"Active Project ID: {project_id} (could not load details)"

        # Construct the system prompt from registry + dynamic context
        system_prompt = f"""{build_personal_assistant_prompt(user_first_name)}

## User Profile
- Name: {user_first_name} {user_last_name}
- Username: {self.user.username}
- Role: {self.enhanced_profile.primary_role or 'Creative Professional'}
- Communication Style: {self.enhanced_profile.communication_style or 'balanced'}
- Goals: {', '.join(self.enhanced_profile.long_term_goals[:3]) if self.enhanced_profile.long_term_goals else 'Not specified'}

## Current Session
{conversation_context if conversation_context else 'New conversation'}

## Recent Memories
{memory_context}

## Agent Activities
{agent_context}

{('## Style Preferences' + chr(10) + style_preferences_context) if style_preferences_context else ''}

## Available Assets
{assets_context}

## Project Context
{project_context_section if project_context_section else 'No active project'}

{('## Project Brief' + chr(10) + project_brief_context) if project_brief_context else ''}
"""

        # Session 266: Inject Spider Intelligence from Super Platform
        spider_intelligence_section = self._build_spider_intelligence_section(aggregated_context, classification)
        if spider_intelligence_section:
            system_prompt = system_prompt + spider_intelligence_section

        # Session 482: Inject Proactive Intelligence from 19 Autonomous Situations
        proactive_intelligence_section = self._build_proactive_intelligence_section(message, context)
        if proactive_intelligence_section:
            system_prompt = system_prompt + proactive_intelligence_section

        # Session 796: Inject Pending Human Decisions context
        pending_decisions_section = self._build_pending_decisions_section()
        if pending_decisions_section:
            system_prompt = system_prompt + pending_decisions_section

        # Session 798: Inject Active Workspace context
        workspace_context_section = self._build_workspace_context_section()
        if workspace_context_section:
            system_prompt = system_prompt + workspace_context_section

        # Session 800: Inject Operator Mode context (current state, not capabilities)
        operator_mode_section = self._build_operator_mode_section()
        if operator_mode_section:
            system_prompt = system_prompt + operator_mode_section

        # Session 806: Track token budget for observability
        if CONTEXT_OPTIMIZATION_AVAILABLE and self.context_budget_manager:
            try:
                self.context_budget_manager.start_request()
                # Track major context sections for budget analysis
                self.context_budget_manager.set_section('system_prompt_core', system_prompt[:2000])
                self.context_budget_manager.set_section('user_message', message)
                if conversation_context:
                    self.context_budget_manager.set_section('conversation_history', conversation_context)
                if project_context_section:
                    self.context_budget_manager.set_section('project_context', project_context_section)
                if spider_intelligence_section:
                    self.context_budget_manager.set_section('spider_intelligence', spider_intelligence_section)
                if proactive_intelligence_section:
                    self.context_budget_manager.set_section('proactive_intelligence', proactive_intelligence_section)
                if pending_decisions_section:
                    self.context_budget_manager.set_section('pending_decisions', pending_decisions_section)
                if workspace_context_section:
                    self.context_budget_manager.set_section('workspace_context', workspace_context_section)
                if operator_mode_section:
                    self.context_budget_manager.set_section('operator_mode', operator_mode_section)

                # Log budget report
                budget_report = self.context_budget_manager.get_budget_report()
                logger.info(
                    f"📊 [Session 806] Context Budget: {budget_report.total_used} tokens "
                    f"({'⚠️ OVER' if budget_report.over_budget else '✅ OK'})"
                )
            except Exception as e:
                logger.debug(f"Context budget tracking failed: {e}")

        # Call the LLM Enforcer for real AI response with tool calling support
        try:
            logger.debug(f"Starting LLM call for message: {message[:50]}...")
            # Session 129: Get previous response_id for GPT-5.1 chain of thought
            previous_response_id = None
            current_session = getattr(self, 'session', None)
            if current_session and hasattr(current_session, 'last_response_id'):
                previous_response_id = current_session.last_response_id
                if previous_response_id:
                    logger.info(f"🔗 Using chain of thought from previous response: {previous_response_id[:20]}...")

            # Session 125: Pass tool definitions to enable GPT function calling
            # Session 349: Use ClassificationIntegrationService for intelligent routing
            all_tools = self.get_tool_definitions()

            # Session 349: Use classification to determine tool filtering and behavior
            # This replaces the 100+ keyword matching with classification-based routing
            is_operation = False
            is_question = False
            tools = all_tools  # Default to all tools

            # Session 806: Apply tool category routing for token optimization
            if CONTEXT_OPTIMIZATION_AVAILABLE and self.tool_category_router:
                tools = self._get_optimized_tools(message, all_tools)
                if len(tools) < len(all_tools):
                    logger.info(
                        f"📊 [Session 806] Tool optimization: {len(tools)}/{len(all_tools)} tools "
                        f"(saved ~{(len(all_tools) - len(tools)) * 30} tokens)"
                    )

            try:
                from core.services.classification_integration import (
                    get_classification_integration_service,
                    ClarificationState
                )

                classification_service = get_classification_integration_service()

                # Get or create clarification state for this conversation
                if not hasattr(self, '_clarification_state'):
                    self._clarification_state = ClarificationState()

                # Use existing classification from earlier in this method
                if classification:
                    query_type = classification.primary_type.value
                    confidence = classification.confidence

                    # Determine behavior based on query type
                    if query_type in ('question', 'conversation'):
                        # QUESTIONS/CONVERSATION: No tools, answer directly
                        is_question = True
                        tools = []  # No tools for questions
                        logger.info(f"🎯 Session 349: {query_type.upper()} detected (confidence: {confidence:.2f}) - NO TOOLS")

                    elif query_type in ('creation', 'workflow', 'analysis'):
                        # CREATION/WORKFLOW/ANALYSIS: Enable appropriate tools
                        is_operation = True

                        # Filter tools based on query type
                        allowed_categories = classification_service.classifier.get_routing_decision(classification)
                        tools = classification_service.filter_tools_by_categories(all_tools, set(allowed_categories.get('suggested_agents', [])))
                        if not tools:
                            tools = all_tools  # Fallback to all tools if filtering fails

                        logger.info(f"🎯 Session 349: {query_type.upper()} detected (confidence: {confidence:.2f}) - TOOLS ENABLED ({len(tools)})")

                        # Check if we should clarify (low confidence or missing info)
                        if confidence < 0.6 and self._clarification_state.can_ask_clarification():
                            # Return clarification instead of proceeding
                            self._clarification_state.record_clarification('low_confidence')
                            clarification_response = "I want to make sure I understand correctly. Could you tell me a bit more about what you're looking for?"
                            logger.info(f"🤔 Session 349: Low confidence ({confidence:.2f}) - suggesting clarification")
                            # Note: We continue anyway but with clarification logged

                    elif query_type in ('memory', 'collaboration', 'opportunity', 'system'):
                        # Other types: Enable tools but don't force
                        is_operation = False
                        tools = all_tools
                        logger.info(f"🎯 Session 349: {query_type.upper()} detected - tools available")

                    else:
                        # Unknown type - use all tools in auto mode
                        logger.info(f"🎯 Session 349: Unknown query type '{query_type}' - defaulting to auto mode")

            except ImportError as e:
                logger.warning(f"⚠️ Session 349: ClassificationIntegrationService not available: {e}")
                # Fallback to legacy keyword detection if classification service unavailable
                operation_keywords = [
                    'create', 'generate', 'make', 'design', 'draw', 'build',
                    'upscale', 'remove background', 'animate', 'edit',
                    'research and create', 'workflow', 'brand identity',
                ]
                is_operation = any(kw in message.lower() for kw in operation_keywords)

                question_keywords = ['what', 'how', 'why', 'which', 'ideas', 'suggest', 'recommend']
                is_question = any(kw in message.lower() for kw in question_keywords) and message.strip().endswith('?')

                if is_question:
                    is_operation = False
                    logger.info(f"🤔 Fallback: Detected QUESTION - will not force tool execution")

            except Exception as e:
                logger.warning(f"⚠️ Session 349: Classification error: {e}")
                # Continue with all tools on error

            # Session 349: Handle no-tool mode for questions/conversations
            if not tools or is_question:
                # NO TOOLS - direct response mode
                tool_choice = None
                tools = None  # Explicitly None to disable tools
                logger.info(f"💬 Session 349: NO TOOLS mode - direct conversation response")

            elif is_operation:
                # FORCE tool execution for operations
                tool_choice = {
                    "type": "allowed_tools",
                    "mode": "required",  # Session 131: MUST use a tool, cannot just respond with text
                    "tools": [{"type": "function", "name": t["name"]} for t in tools]
                }
                logger.info(f"🎯 FORCING tool execution (mode: required) - {len(tools)} tools available")

            else:
                # Auto mode for other types (memory, system, etc.)
                tool_choice = {
                    "type": "allowed_tools",
                    "mode": "auto",
                    "tools": [{"type": "function", "name": t["name"]} for t in tools]
                }
                logger.info(f"🔧 Calling LLM with {len(tools)} tools (mode: auto)...")
            # Session 184: Increased max_tokens from 500 to 1500 to prevent
            # truncation of tool call arguments (JSON can be longer than expected!)
            # Session 266: Increased to 4000 for comprehensive responses (app skeletons, code examples)
            ai_result = self.llm_enforcer.enforce_real_ai(
                prompt=message,
                context=system_prompt,
                agent_name="PersonalAssistant",
                task_type="conversation",
                max_tokens=4000,  # Session 266: Increased from 1500 for longer code/skeleton responses
                tools=tools,  # Enable tool calling
                previous_response_id=previous_response_id,  # Session 129: Chain of thought
                tool_choice=tool_choice  # Session 129: Allowed tools with auto mode
                # temperature=0.7  # GPT-5 only supports default temperature
            )
            logger.info(f"✅ LLM returned: success={ai_result.get('success')}, has_tool_calls={'tool_calls' in ai_result}")

            # Session 129: Store new response_id for next turn
            if ai_result.get('response_id') and current_session:
                current_session.last_response_id = ai_result['response_id']
                current_session.save(update_fields=['last_response_id'])
                logger.info(f"💾 Stored response_id for chain of thought: {ai_result['response_id'][:20]}...")

            if ai_result['success']:
                # Session 125/155: Check if GPT returned tool calls
                if 'tool_calls' in ai_result and ai_result['tool_calls']:
                    logger.info(f"🛠️ GPT requested {len(ai_result['tool_calls'])} tool calls")

                    # Session 517: Backend-only tools should execute here, not in frontend
                    # These tools produce content/data that should be returned directly
                    # NOTE: video_generation_agent excluded - it's async and needs progress tracking
                    BACKEND_EXECUTE_TOOLS = {
                        'content_writer_agent',  # Session 517: Written content generation
                        'competitor_analysis_agent',
                        'customer_research_agent',
                        'brand_strategy_agent',
                        'content_strategy_agent',
                        'marketing_strategy_agent',
                        'image_generation_agent',  # Session 517: Image generation for content
                    }

                    # Check if any tool calls should execute in backend
                    backend_results = []
                    frontend_tool_calls = []

                    for tc in ai_result['tool_calls']:
                        tool_name = tc.get('function', {}).get('name', '') if 'function' in tc else tc.get('name', '')

                        if tool_name in BACKEND_EXECUTE_TOOLS:
                            logger.info(f"📝 Session 517: Executing backend tool: {tool_name}")
                            try:
                                result = self._execute_tool_call(tc)
                                backend_results.append({
                                    'name': tool_name,
                                    'arguments': tc.get('function', {}).get('arguments', {}) if 'function' in tc else tc.get('arguments', {}),
                                    'result': result
                                })
                                logger.info(f"✅ Backend tool {tool_name} executed successfully")
                            except Exception as e:
                                logger.error(f"❌ Backend tool {tool_name} failed: {e}")
                                backend_results.append({
                                    'name': tool_name,
                                    'error': str(e)
                                })
                        else:
                            frontend_tool_calls.append(tc)

                    # If we executed backend tools, return their results
                    if backend_results:
                        # Return the first backend result as the main response
                        first_result = backend_results[0].get('result', {})
                        response = first_result.get('message', '') or first_result.get('response', '')

                        # Session 266: Record successful outcome
                        execution_time_ms = int((timezone.now() - start_time).total_seconds() * 1000)
                        agents_used = [r['name'] for r in backend_results]
                        self._record_learning_outcome(
                            message=message,
                            classification=classification,
                            response=response,
                            success=True,
                            agents_used=agents_used,
                            execution_time_ms=execution_time_ms
                        )

                        # Session 518: Auto-create project from generated content
                        project_info = None
                        try:
                            project_info = self._auto_create_project_from_content(
                                backend_results=backend_results,
                                message=message
                            )
                            if project_info:
                                logger.info(f"📁 Session 518: Auto-created project: {project_info.get('project_name')} (ID: {project_info.get('project_id')})")
                        except Exception as e:
                            logger.warning(f"⚠️ Session 518: Auto-project creation failed: {e}")

                        # Return result with tool_calls containing results
                        result = {
                            'text': response,
                            'tool_calls': backend_results,
                            **first_result  # Spread the result data (content, metadata, etc.)
                        }

                        # Session 518: Add project info if created
                        if project_info:
                            result['project_created'] = project_info

                        return result

                    # Session 155 Fix: Return tool_calls to frontend for execution
                    # DON'T execute in backend - let frontend handle it for proper UX
                    # Session 173 FIX: LLM enforcer returns 'content' not 'response'
                    response = ai_result.get('content', '') or ai_result.get('response', '')
                    logger.info(f"✅ Returning {len(frontend_tool_calls)} tool_calls to frontend for execution")

                    # Session 266: Record successful outcome with tool calls
                    execution_time_ms = int((timezone.now() - start_time).total_seconds() * 1000)
                    agents_used = [tc['function']['name'] for tc in frontend_tool_calls if 'function' in tc]
                    self._record_learning_outcome(
                        message=message,
                        classification=classification,
                        response=response,
                        success=True,
                        agents_used=agents_used,
                        execution_time_ms=execution_time_ms
                    )

                    # Return dict with both response and tool_calls
                    return {
                        'text': response,
                        'tool_calls': frontend_tool_calls
                    }
                else:
                    # No tool calls, just return the text response
                    # Session 173 FIX: LLM enforcer returns 'content' not 'response'
                    response = ai_result.get('content', '') or ai_result.get('response', '')
                    logger.info(f"✅ Generated REAL AI response for {self.user.username}")

                    # Session 266: Handle truncated responses - add continuation hint
                    if ai_result.get('truncated', False):
                        logger.warning(f"⚠️ Response was truncated - adding continuation hint")
                        response += "\n\n---\n\n**(Response was truncated due to length. Say \"continue\" to see the rest.)**"

                    # Session 266: Record successful outcome without tool calls
                    execution_time_ms = int((timezone.now() - start_time).total_seconds() * 1000)
                    self._record_learning_outcome(
                        message=message,
                        classification=classification,
                        response=response,
                        success=True,
                        agents_used=[],
                        execution_time_ms=execution_time_ms
                    )

                    return response
            else:
                # Fallback if AI fails
                logger.warning(f"⚠️ AI generation failed, using intelligent fallback")

                # Session 266: Record failed outcome
                execution_time_ms = int((timezone.now() - start_time).total_seconds() * 1000)
                self._record_learning_outcome(
                    message=message,
                    classification=classification,
                    response="",
                    success=False,
                    agents_used=[],
                    execution_time_ms=execution_time_ms
                )

                return self._generate_intelligent_fallback(message, context)

        except Exception as e:
            import traceback
            logger.error(f"❌ LLM ERROR: {e}")
            logger.debug(f"Full traceback:\n{traceback.format_exc()}")
            logger.warning(f"⚠️ LLM not available (likely no API keys configured): {e}")
            logger.info("📋 Using intelligent fallback response with conversation context")
            return self._generate_intelligent_fallback(message, context)

    def _build_spider_intelligence_section(self, aggregated_context, classification) -> str:
        """
        Session 266: Build spider intelligence section for system prompt.

        This injects real-time data from the spider network into the GPT prompt,
        giving the AI access to current trends, news, market data, and opportunities.

        Args:
            aggregated_context: AggregatedContext from ContextAggregator
            classification: ClassificationResult from QueryClassifier

        Returns:
            Formatted string section to append to system prompt
        """
        if not aggregated_context or not SUPER_PLATFORM_AVAILABLE:
            return ""

        sections = []

        # Spider Intelligence Header
        spider_data = aggregated_context.spider_data
        if spider_data:
            sections.append("\n\n--- SPIDER INTELLIGENCE (Session 266 - Real-Time Data) ---")

            # Trending Topics
            if spider_data.get('trends'):
                trends = spider_data['trends'][:5]
                if trends:
                    trend_lines = []
                    for t in trends:
                        if isinstance(t, dict):
                            trend_lines.append(f"- {t.get('title', t.get('name', str(t)))}")
                        else:
                            trend_lines.append(f"- {t}")
                    sections.append(f"\n🔥 TRENDING NOW:\n" + "\n".join(trend_lines))
                    sections.append("*Use these trends to make content more relevant and timely.*")

            # Latest News
            if spider_data.get('news'):
                news = spider_data['news'][:3]
                if news:
                    news_lines = []
                    for n in news:
                        if isinstance(n, dict):
                            news_lines.append(f"- {n.get('title', n.get('headline', str(n)))}")
                        else:
                            news_lines.append(f"- {n}")
                    sections.append(f"\n📰 LATEST NEWS:\n" + "\n".join(news_lines))

            # Market Data
            if spider_data.get('market') or spider_data.get('crypto'):
                market = spider_data.get('market', spider_data)
                crypto = market.get('crypto', [])[:3] if isinstance(market, dict) else []
                if crypto:
                    crypto_parts = []
                    for c in crypto:
                        if isinstance(c, dict):
                            symbol = c.get('symbol', c.get('name', '?'))
                            price = c.get('price', c.get('current_price', 0))
                            if isinstance(price, (int, float)):
                                crypto_parts.append(f"{symbol}: ${price:,.2f}")
                        else:
                            crypto_parts.append(str(c))
                    if crypto_parts:
                        sections.append(f"\n💹 MARKET SNAPSHOT: {', '.join(crypto_parts)}")

            # Hot Skills/Jobs
            if spider_data.get('jobs'):
                jobs = spider_data['jobs']
                if isinstance(jobs, dict) and jobs.get('hot_skills'):
                    skills = jobs['hot_skills'][:5]
                    sections.append(f"\n🎯 HOT SKILLS IN DEMAND: {', '.join(skills)}")

        # Query Classification Context
        if classification:
            if classification.detected_entities:
                entities = classification.detected_entities
                if entities.get('topics'):
                    sections.append(f"\n🏷️ DETECTED TOPICS: {', '.join(entities['topics'][:3])}")
                if entities.get('styles'):
                    sections.append(f"🎨 DETECTED STYLES: {', '.join(entities['styles'][:3])}")

            # Suggested agents based on classification
            if classification.suggested_agents:
                agents = classification.suggested_agents[:3]
                sections.append(f"\n🤖 RECOMMENDED AGENTS: {', '.join(agents)}")

                # Session 266: Add Sci-Fi personality for primary suggested agent
                if agents:
                    primary_agent = agents[0]
                    scifi_context = self._get_agent_scifi_context(primary_agent, "handling user request")
                    if scifi_context:
                        sections.append(f"\n🌟 {primary_agent} STATUS:\n{scifi_context}")

        # Active Opportunities (for revenue-focused queries)
        if aggregated_context.active_opportunities:
            opps = aggregated_context.active_opportunities[:3]
            if opps:
                sections.append("\n💰 ACTIVE OPPORTUNITIES:")
                for opp in opps:
                    if isinstance(opp, dict):
                        title = opp.get('title', opp.get('name', 'Opportunity'))
                        value = opp.get('estimated_value', opp.get('value', ''))
                        if value:
                            sections.append(f"- {title} (Est. ${value})")
                        else:
                            sections.append(f"- {title}")

        # Session 266: Learning Companion Context
        learning_context = self._get_learning_companion_context()
        if learning_context:
            sections.append(learning_context)

        # Session 324: Inject Canonical Policies from Boardroom Decisions
        policy_context = self._get_policy_context()
        if policy_context:
            sections.append(policy_context)

        # Session 324: Inject Agent Knowledge/Learning Insights
        agent_knowledge = self._get_agent_knowledge_context()
        if agent_knowledge:
            sections.append(agent_knowledge)

        if len(sections) > 1:  # More than just the header
            sections.append("\n--- END SPIDER INTELLIGENCE ---\n")
            return "\n".join(sections)

        return ""

    def _build_optimized_context(
        self,
        message: str,
        context: Dict[str, Any],
        classification=None,
        aggregated_context=None
    ) -> Dict[str, Any]:
        """
        Session 806: Build optimized context using new budget/lazy/summarizer components.

        This method uses the new context optimization components to reduce
        token usage by ~70% while preserving critical information.

        Args:
            message: User's message
            context: Existing context dict
            classification: Optional ClassificationResult
            aggregated_context: Optional AggregatedContext

        Returns:
            Dict with optimized context sections and budget report
        """
        if not CONTEXT_OPTIMIZATION_AVAILABLE or not self.context_budget_manager:
            return {'optimized': False, 'sections': {}}

        try:
            # Start budget tracking
            self.context_budget_manager.start_request()

            # Determine query type for lazy loading
            query_type = QueryType.UNKNOWN
            if classification and hasattr(classification, 'primary_type'):
                query_type_str = classification.primary_type.value
                try:
                    query_type = QueryType(query_type_str)
                except ValueError:
                    query_type = self.lazy_context_loader.classify_query_simple(message)
            elif self.lazy_context_loader:
                query_type = self.lazy_context_loader.classify_query_simple(message)

            logger.info(f"📊 [Session 806] Query type: {query_type.value}")

            # Get required sections for this query type
            required_sections = set()
            if self.lazy_context_loader:
                required_sections = self.lazy_context_loader.get_required_sections(
                    query_type=query_type,
                    message=message
                )

            optimized_sections = {}

            # 1. Spider Intelligence (summarized)
            if 'spider_intelligence' in required_sections:
                if self.context_summarizer and aggregated_context:
                    spider_data = aggregated_context.spider_data if aggregated_context else {}
                    spider_summary = self.context_summarizer.summarize_spider_context(spider_data)
                    if spider_summary:
                        optimized_sections['spider_intelligence'] = spider_summary
                        self.context_budget_manager.set_section(
                            'spider_intelligence',
                            spider_summary,
                            priority=SectionPriority.MEDIUM
                        )

            # 2. Learning Patterns (summarized)
            if 'learning_patterns' in required_sections:
                try:
                    from core.services.learning_pattern_engine import get_learning_pattern_engine
                    engine = get_learning_pattern_engine()
                    learning_summary = engine.get_summary('PersonalAssistant', message)
                    if learning_summary:
                        optimized_sections['learning_patterns'] = learning_summary
                        self.context_budget_manager.set_section(
                            'learning_patterns',
                            learning_summary,
                            priority=SectionPriority.MEDIUM
                        )
                except Exception as e:
                    logger.debug(f"Failed to get learning summary: {e}")

            # 3. Advisor Context (summarized)
            if 'advisor_context' in required_sections:
                try:
                    from core.services.advisor_context_builder import get_advisor_context_builder
                    builder = get_advisor_context_builder()
                    advisor_summary = builder.build_summary('PersonalAssistant', message)
                    if advisor_summary:
                        optimized_sections['advisor_context'] = advisor_summary
                        self.context_budget_manager.set_section(
                            'advisor_context',
                            advisor_summary,
                            priority=SectionPriority.LOW
                        )
                except Exception as e:
                    logger.debug(f"Failed to get advisor summary: {e}")

            # 4. Pending Decisions (summarized)
            if 'pending_decisions' in required_sections:
                try:
                    pending_section = self._build_pending_decisions_section()
                    if pending_section:
                        # Use summarizer for compression
                        if self.context_summarizer:
                            # Just truncate for now, could add summarize_pending_decisions
                            pending_compact = pending_section[:400] if len(pending_section) > 400 else pending_section
                        else:
                            pending_compact = pending_section
                        optimized_sections['pending_decisions'] = pending_compact
                        self.context_budget_manager.set_section(
                            'pending_decisions',
                            pending_compact,
                            priority=SectionPriority.HIGH
                        )
                except Exception as e:
                    logger.debug(f"Failed to get pending decisions: {e}")

            # 5. Proactive Intelligence (summarized)
            if 'proactive_intelligence' in required_sections:
                try:
                    proactive_section = self._build_proactive_intelligence_section(message, context)
                    if proactive_section and self.context_summarizer:
                        # Build a minimal summary
                        proactive_compact = proactive_section[:200] if len(proactive_section) > 200 else proactive_section
                        optimized_sections['proactive_intelligence'] = proactive_compact
                        self.context_budget_manager.set_section(
                            'proactive_intelligence',
                            proactive_compact,
                            priority=SectionPriority.LOW
                        )
                except Exception as e:
                    logger.debug(f"Failed to get proactive intelligence: {e}")

            # Get budget report
            budget_report = self.context_budget_manager.get_budget_report()

            return {
                'optimized': True,
                'sections': optimized_sections,
                'query_type': query_type.value,
                'sections_loaded': len(optimized_sections),
                'sections_skipped': len(required_sections) - len(optimized_sections),
                'total_tokens': budget_report.total_used,
                'budget_remaining': budget_report.budget_remaining,
                'over_budget': budget_report.over_budget,
            }

        except Exception as e:
            logger.warning(f"⚠️ Context optimization failed: {e}")
            return {'optimized': False, 'error': str(e), 'sections': {}}

    def _get_optimized_tools(self, message: str, all_tools: List[Dict]) -> List[Dict]:
        """
        Session 806: Get optimized tool list using ToolCategoryRouter.

        Args:
            message: User's message
            all_tools: Full list of available tools

        Returns:
            Filtered list of relevant tools
        """
        if not CONTEXT_OPTIMIZATION_AVAILABLE or not self.tool_category_router:
            return all_tools

        try:
            filtered_tools = self.tool_category_router.get_tools_for_message(
                message=message,
                all_tools=all_tools,
                include_secondary=True
            )
            return filtered_tools
        except Exception as e:
            logger.warning(f"⚠️ Tool routing failed: {e}, using all tools")
            return all_tools

    def _auto_create_project_from_content(
        self,
        backend_results: List[Dict[str, Any]],
        message: str
    ) -> Optional[Dict[str, Any]]:
        """
        Session 518: Auto-create a PartnershipProject from generated content.

        When the assistant generates content (blog posts, images, etc.), automatically
        organize it into a project so users can track and manage their content.

        Args:
            backend_results: List of executed tool results
            message: Original user message (used for project naming)

        Returns:
            Dict with project_id, project_name, project_url if created, None otherwise
        """
        from datetime import datetime
        from core.models_partnership import PartnershipProject

        # Check if we have content that should be organized into a project
        content_results = []
        image_ids = []
        content_data = None

        for result in backend_results:
            tool_name = result.get('name', '')
            tool_result = result.get('result', {})

            if tool_name == 'content_writer_agent':
                # Session 518 FIX: ContentWriterAgent returns {data: {content_type, content: {...}}}
                data_wrapper = tool_result.get('data', {})
                content_data = data_wrapper.get('content', {}) if isinstance(data_wrapper, dict) else {}
                content_type = data_wrapper.get('content_type', 'blog_post') if isinstance(data_wrapper, dict) else 'blog_post'

                # Fallback to direct content if not nested
                if not content_data:
                    content_data = tool_result.get('content', {})
                    content_type = content_data.get('content_type', 'blog_post') if isinstance(content_data, dict) else 'blog_post'

                if content_data:
                    content_results.append({
                        'type': 'written_content',
                        'content_type': content_type,
                        'title': content_data.get('title', ''),
                        'data': content_data
                    })

            elif tool_name == 'image_generation_agent':
                # ImageGenerationAgent returns image IDs
                img_id = tool_result.get('image_id')
                if img_id:
                    image_ids.append(img_id)

        # Only create project if we have content
        if not content_results and not image_ids:
            return None

        # Generate project name from content or message
        project_name = None
        project_type = 'content_creation'

        if content_results:
            first_content = content_results[0]
            project_name = first_content.get('title', '')[:100]
            content_type = first_content.get('content_type', 'blog_post')

            # Map content type to project type
            project_type_map = {
                'blog_post': 'content_creation',
                'podcast_script': 'audio_production',
                'video_script': 'video_production',
                'article': 'content_creation',
                'newsletter': 'marketing',
                'social_thread': 'marketing'
            }
            project_type = project_type_map.get(content_type, 'content_creation')

        if not project_name:
            # Fall back to extracting from message
            project_name = message[:100] if len(message) <= 100 else message[:97] + '...'

        # Build project metadata
        project_metadata = {
            'created_from': 'assistant_pipeline',
            'original_message': message[:500],
            'created_at': datetime.now().isoformat(),
        }

        # Add content to metadata
        if content_results:
            project_metadata['written_content'] = content_results

        # Add image IDs to metadata
        if image_ids:
            project_metadata['image_ids'] = image_ids

        # Build description from content
        description = f"Auto-generated from assistant: {message[:200]}"
        if content_results:
            first_content_data = content_results[0].get('data', {})
            if first_content_data.get('meta_description'):
                description = first_content_data['meta_description']
            elif first_content_data.get('intro'):
                description = first_content_data['intro'][:500]

        # Create the project
        try:
            project = PartnershipProject.objects.create(
                user=self.user,
                project_name=project_name,
                project_type=project_type,
                description=description[:1000],
                status='in_progress',
                ai_contribution_percent=95,
                human_contribution_percent=5,
                metadata=project_metadata,
                ai_contributions=[{
                    'agent': 'PersonalAssistant',
                    'task': message[:200],
                    'timestamp': datetime.now().isoformat(),
                    'output': f'Generated {len(content_results)} content pieces, {len(image_ids)} images',
                    'tools_used': [r.get('name') for r in backend_results]
                }],
                workflow_steps=[{
                    'step': 'Content Generation',
                    'status': 'completed',
                    'description': f'Generated content from assistant pipeline'
                }]
            )

            logger.info(f"📁 Created project '{project.project_name}' (ID: {project.id}) with {len(content_results)} content pieces, {len(image_ids)} images")

            return {
                'project_id': str(project.id),
                'project_name': project.project_name,
                'project_type': project_type,
                'project_url': f'/ai-studio/?tab=projects&project_id={project.id}'
            }

        except Exception as e:
            logger.error(f"❌ Failed to create project: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _record_learning_outcome(
        self,
        message: str,
        classification,
        response: str,
        success: bool,
        agents_used: List[str],
        execution_time_ms: int
    ) -> None:
        """
        Session 266: Record outcome to the Learning Loop service.

        This enables the platform to learn from every interaction:
        - Which query types succeed most
        - Which agents perform best
        - How execution time varies
        - Pattern detection for optimization

        Args:
            message: Original user message
            classification: QueryClassifier result
            response: Generated response
            success: Whether the response was successful
            agents_used: List of agents/tools used
            execution_time_ms: Time taken in milliseconds
        """
        if not SUPER_PLATFORM_AVAILABLE or not classification:
            return

        # Lazy load learning service
        if self._learning_service is None:
            try:
                self._learning_service = get_learning_loop_service(self.user)
            except Exception as e:
                logger.warning(f"⚠️ Could not load learning service: {e}")
                return

        if not self._learning_service:
            return

        try:
            outcome_id = self._learning_service.record_outcome(
                query_type=classification.primary_type.value,
                query_text=message[:500],  # Truncate for storage
                execution_mode='assistant',
                agents_used=agents_used,
                response=response[:500] if response else "",
                execution_time_ms=execution_time_ms,
                success=success,
                classification_confidence=classification.confidence,
                spider_data_used=classification.requires_spider_data,
            )
            if outcome_id:
                logger.info(f"📚 Learning outcome recorded: {outcome_id[:8]}...")
        except Exception as e:
            logger.warning(f"⚠️ Failed to record learning outcome: {e}")

    def process_message(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Enhanced message processing with system command support and full profile integration.

        Args:
            message: User's message
            context: Optional additional context

        Returns:
            Response dictionary with enhanced capabilities
        """
        logger.debug(f"process_message() CALLED with: {message[:80]}...")

        # Analyze user patterns and conversation history for contextual memory
        user_patterns = self._analyze_user_patterns()

        # Load conversation history for context
        conversation_history = self._load_conversation_history(limit=3)
        conversation_context = self._format_conversation_context(conversation_history)

        # Create personalized context based on patterns
        personalized_context = self._create_personalized_context(message, user_patterns)

        # Load enhanced profile context for personalization
        profile_context = self.enhanced_profile.get_context_for_ai('chat')

        # Session 882: Interview System - Auto-trigger for new users with incomplete profiles
        interview_response = self._handle_interview_trigger(message)
        if interview_response:
            return interview_response

        # Session 878: Goal Collection - Help users define their goals
        # (Only runs if interview was skipped or completed - interview includes goals)
        goal_response = self._handle_goal_collection(message)
        if goal_response:
            return goal_response

        # Merge profile context with provided context
        full_context = {
            'user_profile': profile_context,
            'user_role': self.enhanced_profile.primary_role or 'User',
            'communication_style': self.enhanced_profile.communication_style or 'balanced',
            'learning_style': self.enhanced_profile.learning_style or 'mixed',
            'goals': self.enhanced_profile.long_term_goals,
            'current_projects': self.enhanced_profile.current_projects,
            # Session 517: Handle core_competencies as either dict or list
            'skills': {'top_skills': (
                list(self.enhanced_profile.core_competencies.keys())[:5] if isinstance(self.enhanced_profile.core_competencies, dict)
                else self.enhanced_profile.core_competencies[:5] if isinstance(self.enhanced_profile.core_competencies, list)
                else []
            ) if self.enhanced_profile.core_competencies else []},
            'timezone': self.enhanced_profile.time_zone,
            'work_hours': self.enhanced_profile.work_schedule,
            'decision_framework': self.enhanced_profile.decision_framework,
            'conversation_history': conversation_context,
            'personalization_context': personalized_context,
            'user_patterns': user_patterns
        }

        if context:
            full_context.update(context)

        # Session 482: Task Memory - Multi-turn task tracking
        if hasattr(self, 'task_memory') and self.task_memory and TASK_MEMORY_AVAILABLE:
            try:
                # Check if there's an active task
                active_task = self.task_memory.get_active_task()

                if active_task:
                    # Inject active task context for AI to continue
                    task_context = self.task_memory.format_for_prompt()
                    full_context['active_task'] = self.task_memory.get_task_context()
                    full_context['task_context_prompt'] = task_context
                    logger.info(f"📋 TaskMemory: Continuing task '{active_task.task_type}' ({active_task.get_progress()['percentage']}% complete)")

                # Check if message indicates a new multi-step task
                elif not active_task:
                    detected_task_type = self.task_memory.detect_task_type(message)
                    if detected_task_type:
                        # Create new task
                        new_task = self.task_memory.create_task(
                            detected_task_type,
                            description=message[:100],
                            initial_context={'original_request': message}
                        )
                        # Start first step
                        self.task_memory.start_next_step()

                        # Add to context
                        task_context = self.task_memory.format_for_prompt()
                        full_context['active_task'] = self.task_memory.get_task_context()
                        full_context['task_context_prompt'] = task_context
                        logger.info(f"📋 TaskMemory: Started new '{detected_task_type}' task with {len(new_task.steps)} steps")

                # Check for task-related commands
                message_lower = message.lower()
                if 'what were we working on' in message_lower or 'resume task' in message_lower:
                    resumed = self.task_memory.resume_task()
                    if resumed:
                        full_context['active_task'] = self.task_memory.get_task_context()
                        logger.info(f"📋 TaskMemory: Resumed task '{resumed.task_type}'")
                elif 'cancel task' in message_lower or 'abandon task' in message_lower:
                    self.task_memory.abandon_task()
                    logger.info("📋 TaskMemory: Abandoned active task")

            except Exception as e:
                logger.warning(f"⚠️ TaskMemory error: {e}")

        # Session 796 Phase 3: Check for pending consultation responses
        consultation_response = self._check_consultation_response(message)
        if consultation_response:
            return consultation_response

        # Session 126: Store context for tool execution (so tools can access project_id)
        self._current_context = full_context

        # Session 180: Store current prompt for semantic style matching
        # This enables get_style_context_for_user() to find relevant style preferences
        self._current_prompt = message

        # Session 135: Set project and session as instance attributes for all code paths
        # This ensures GPT function calling can access project context via getattr(self, 'project', None)
        self.project = None
        self.session = None

        if full_context.get('project_id'):
            try:
                from content.models import CreativeProject
                self.project = CreativeProject.objects.get(id=full_context['project_id'], user=self.user)
                logger.info(f"✅ Set self.project for all code paths: {self.project.name} (ID: {full_context['project_id']})")
            except CreativeProject.DoesNotExist:
                logger.warning(f"⚠️ Project {full_context['project_id']} not found for user {self.user}")
            except Exception as e:
                logger.error(f"❌ Error resolving project for instance attribute: {e}")

        # Session 127: Check for animation requests and route to VideoAgent
        animation_phrases = ['animate image', 'animate', 'make it move', 'turn into video', 'bring to life']
        is_animation_request = any(phrase in message.lower() for phrase in animation_phrases)

        if is_animation_request:
            logger.info(f"🎬 ANIMATION REQUEST DETECTED in message: '{message}'")

            # Extract image ID from message (e.g., "animate image 271" -> "271")
            import re
            image_id_match = re.search(r'image\s+(\d+|[0-9a-f-]{36})', message.lower())

            if image_id_match:
                image_id = image_id_match.group(1)
                logger.info(f"🎬 Extracted image_id: '{image_id}' (type: {type(image_id).__name__})")
                logger.info(f"🎬 Routing to VideoAgent.animate_image()...")

                # Initialize VideoAgent and call animate_image
                from core.agents import get_video_agent
                video_agent = get_video_agent(user=self.user)
                logger.info(f"✅ VideoAgent initialized for user: {self.user}")

                # Call agent method
                # Session 135: Convert project_id from context to CreativeProject object
                current_project = None
                current_session = None

                # Get project from context if available
                if hasattr(self, '_current_context') and self._current_context:
                    project_id = self._current_context.get('project_id')
                    if project_id:
                        try:
                            from content.models import CreativeProject
                            current_project = CreativeProject.objects.get(id=project_id, user=self.user)
                            logger.info(f"✅ Resolved project_id '{project_id}' to CreativeProject: {current_project.name}")
                        except CreativeProject.DoesNotExist:
                            logger.warning(f"⚠️ Project {project_id} not found for user {self.user}")
                        except Exception as e:
                            logger.error(f"❌ Error resolving project: {e}")

                logger.info(f"🔧 Calling video_agent.animate_image(image_id='{image_id}', project={current_project}, session={current_session})")
                agent_result = video_agent.animate_image(
                    image_id=image_id,
                    motion_prompt='natural motion',  # Default motion
                    duration=5,
                    project=current_project,  # Pass project context!
                    session=current_session   # Pass session context!
                )
                logger.info(f"🔙 VideoAgent.animate_image() returned: {agent_result}")

                # Format response
                if agent_result.get('success'):
                    logger.info(f"✅ Animation SUCCESS! Task ID: {agent_result.get('task_id')}")
                    response = {
                        'response': agent_result.get('message', '✅ Image animation started!'),
                        'success': True,
                        'agent_used': 'VideoAgent',
                        'method': 'animate_image',
                        'task_id': agent_result.get('task_id'),
                        'video_id': agent_result.get('video_id'),
                        'confidence': 0.95
                    }
                else:
                    logger.error(f"❌ Animation FAILED! Error: {agent_result.get('error')}")
                    response = {
                        'response': f"❌ Animation failed: {agent_result.get('error', 'Unknown error')}",
                        'success': False,
                        'agent_used': 'VideoAgent',
                        'method': 'animate_image',
                        'error': agent_result.get('error'),
                        'confidence': 0.9
                    }

                logger.info(f"🔙 Returning response to frontend: {response}")
                return response
            else:
                # No image ID found, let GPT handle it
                logger.info("🎬 Animation request detected but no image ID found, continuing with GPT...")

        # Session 129: Intelligent routing for image editing operations
        # Route to EditingOrchestratorAgent automatically (no need to say "agent")
        # Session 198: Fixed! 'remove text', 'erase', 'remove object' now use 'erase' operation
        # which uses search-and-replace API to find and remove objects (not inpaint which adds content)
        edit_phrases = {
            'remove text': 'erase',  # Session 198: Was 'inpaint' (wrong!) - now uses search-and-replace
            'erase': 'erase',        # Session 198: Was 'inpaint' (wrong!) - now uses search-and-replace
            'remove object': 'erase', # Session 198: Was 'inpaint' (wrong!) - now uses search-and-replace
            'remove the': 'erase',   # Session 198: Added - "remove the watermark", "remove the text"
            'delete': 'erase',       # Session 198: Added - "delete the text"
            'fix': 'inpaint',
            'remove background': 'remove_bg',
            'remove bg': 'remove_bg',
            'transparent': 'remove_bg',
            'upscale': 'upscale',
            'enhance quality': 'upscale',
            'make bigger': 'upscale',
            'change color': 'recolor',
            'recolor': 'recolor',
            'make it': 'recolor',  # "make it blue"
            'edit image': 'inpaint',
            'modify image': 'inpaint',
        }

        detected_operation = None
        for phrase, operation in edit_phrases.items():
            if phrase in message.lower():
                detected_operation = operation
                logger.info(f"🎨 EDITING REQUEST DETECTED: '{phrase}' → operation: '{operation}'")
                break

        if detected_operation:
            # Extract image ID from message (e.g., "remove text from image 2" -> "2")
            # Session 197: Try UUID pattern FIRST to avoid partial matches like "634" from "634f0b6d..."
            import re
            image_id_match = re.search(r'image\s+(?:number\s+)?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|\d+)', message.lower())

            if image_id_match:
                image_id = image_id_match.group(1)
                logger.info(f"🎨 Extracted image_id: '{image_id}' for operation: '{detected_operation}'")

                # Initialize EditingOrchestratorAgent
                # Session 206: EditingOrchestratorAgent was merged into ImageAgent in Phase 1
                from core.agents import ImageAgent as EditingOrchestratorAgent
                editing_agent = EditingOrchestratorAgent(user=self.user)
                logger.info(f"✅ EditingOrchestratorAgent initialized for user: {self.user}")

                # Prepare parameters based on operation
                parameters = {}
                if detected_operation == 'erase':
                    # Session 198: NEW! Erase uses search_prompt to find and remove objects
                    # Extract what to remove from message: "remove text", "erase watermark", "delete the logo"
                    # Common patterns: "remove X from", "erase X from", "delete X from", "remove the X"
                    erase_patterns = [
                        r'remove\s+(?:the\s+)?(\w+(?:\s+\w+)?)\s+from',  # "remove text from", "remove the watermark from"
                        r'erase\s+(?:the\s+)?(\w+(?:\s+\w+)?)\s+from',   # "erase text from", "erase the logo from"
                        r'delete\s+(?:the\s+)?(\w+(?:\s+\w+)?)\s+from',  # "delete text from"
                        r'remove\s+(?:the\s+)?(\w+(?:\s+\w+)?)',         # "remove text" (no "from")
                        r'erase\s+(?:the\s+)?(\w+(?:\s+\w+)?)',          # "erase watermark"
                        r'delete\s+(?:the\s+)?(\w+(?:\s+\w+)?)',         # "delete logo"
                    ]
                    search_prompt = None
                    for pattern in erase_patterns:
                        match = re.search(pattern, message.lower())
                        if match:
                            search_prompt = match.group(1).strip()
                            break

                    # Default fallback if nothing specific found
                    if not search_prompt:
                        search_prompt = 'text'  # Most common use case

                    parameters['search_prompt'] = search_prompt
                    logger.info(f"🧹 Erase operation: search_prompt='{search_prompt}'")

                elif detected_operation == 'inpaint':
                    # Inpaint is for ADDING/REPLACING content, not removing
                    parameters['prompt'] = 'fix and improve'
                elif detected_operation == 'recolor':
                    # Extract color from message
                    color_match = re.search(r'(?:make it|change to|recolor to?)\s+(\w+)', message.lower())
                    if color_match:
                        parameters['prompt'] = f'recolor to {color_match.group(1)}'
                    else:
                        parameters['prompt'] = 'change colors'

                logger.info(f"🔧 Calling editing_agent.execute_single_edit(image_id='{image_id}', operation='{detected_operation}', parameters={parameters})")

                # Execute editing operation
                agent_result = editing_agent.execute_single_edit(
                    image_id=image_id,
                    operation=detected_operation,
                    parameters=parameters
                )
                logger.info(f"🔙 EditingOrchestratorAgent.execute_single_edit() returned: {agent_result}")

                # Format response
                if agent_result.get('success'):
                    logger.info(f"✅ Editing SUCCESS! Result image ID: {agent_result.get('result_image_id')}")
                    response = {
                        'response': agent_result.get('message', f"✅ {detected_operation.title()} completed!"),
                        'success': True,
                        'agent_used': 'EditingOrchestratorAgent',
                        'operation': detected_operation,
                        'result_image_id': agent_result.get('result_image_id'),
                        'confidence': 0.95
                    }
                else:
                    logger.error(f"❌ Editing FAILED! Error: {agent_result.get('error')}")
                    response = {
                        'response': f"❌ {detected_operation.title()} failed: {agent_result.get('error', 'Unknown error')}",
                        'success': False,
                        'agent_used': 'EditingOrchestratorAgent',
                        'operation': detected_operation,
                        'error': agent_result.get('error'),
                        'confidence': 0.9
                    }

                logger.info(f"🔙 Returning response to frontend: {response}")
                return response
            else:
                # No image ID found, let GPT handle it
                logger.info(f"🎨 Editing request detected but no image ID found, continuing with GPT...")

        # Check for agent execution requests
        agent_execution_phrases = [
            'can you have an agent', 'execute agent', 'run agent', 'use agent',
            'deploy agent', 'have the agent', 'get an agent to', 'agent analyze',
            'agent help', 'technical-signal-agent', 'research agent'
        ]

        is_agent_request = any(phrase in message.lower() for phrase in agent_execution_phrases)

        if is_agent_request:
            # Extract the task from the message
            task = self._extract_task_from_message(message)

            # Route to appropriate agent
            routing_result = self.route_to_agent(task)

            if routing_result['success']:
                # Generate AI response with agent execution results
                response_data = self._generate_response(message, full_context)
                response_data['agent_execution'] = routing_result
                response_data['response'] = f"I've successfully routed your request to the {routing_result['agent']['name']} agent. " + \
                                          f"The agent is now analyzing: '{task}'. " + \
                                          f"Execution ID: {routing_result['execution_id']}. " + \
                                          response_data.get('response', '')
                response_data['confidence'] = 0.9
                return response_data
            else:
                # Generate response with agent routing failure
                response_data = self._generate_response(message, full_context)
                response_data['agent_execution'] = routing_result
                response_data['response'] = f"I attempted to route your request to an agent, but encountered an issue: {routing_result.get('error', 'Unknown error')}. " + \
                                          response_data.get('response', '')
                return response_data

        # Check if this is a system command
        # Session 799: Only trigger for actual command patterns, not questions containing keywords
        system_command_patterns = [
            'check database',
            'database status',
            'search embedding',
            'list agents',
            'execute agent',
            'run agent',
            'websocket status',
            'embeddings count',
        ]
        message_lower = message.lower()
        is_system_command = any(pattern in message_lower for pattern in system_command_patterns)

        if is_system_command:
            # Process as system command
            system_result = self.process_system_command(message)

            # Use AI generation instead of parent's template response
            response_data = self._generate_response(message, full_context)

            # Enhanced response with system data - only use system response if it's not the fallback
            if system_result.get('type') != 'unknown_command':
                response_data['response'] = system_result.get('response', response_data['response'])
            response_data['system_data'] = system_result
            response_data['confidence'] = 0.9  # High confidence for system queries

            # Add relevant suggestions based on system command and user profile
            if system_result.get('type') == 'system_status':
                response_data['suggestions'] = [
                    'Search embeddings',
                    'List agents',
                    'Check WebSocket status',
                    'View my applications'
                ]
            elif system_result.get('type') == 'agent_list':
                # Personalize agent suggestions based on user's role and goals
                if 'software' in (self.enhanced_profile.primary_role or '').lower():
                    response_data['suggestions'] = [
                        'Execute agent Code Optimizer',
                        'Execute agent Testing Agent',
                        'Show development agents',
                        'Agent capabilities'
                    ]
                else:
                    response_data['suggestions'] = [
                        'Execute agent Income Builder',
                        'Execute agent Job Matcher',
                        'Show agent categories',
                        'Agent capabilities'
                    ]

            return response_data

        # Regular message processing with AI instead of templates
        logger.debug("About to call _generate_response()")
        response_data = self._generate_response(message, full_context)
        logger.debug(f"_generate_response() returned type={type(response_data)}")

        # Session 135: Inject task_id from tool execution (enables video polling notifications)
        if hasattr(self, '_last_tool_result') and self._last_tool_result:
            if 'task_id' in self._last_tool_result and self._last_tool_result['task_id']:
                response_data['task_id'] = self._last_tool_result['task_id']
                response_data['agent_used'] = 'VideoAgent'  # Mark as video operation for frontend polling
                logger.info(f"✅ Injected task_id into response: {self._last_tool_result['task_id']}")
            # Clear the stored result after use
            self._last_tool_result = None

        # Personalize response based on communication style
        if self.enhanced_profile.communication_style == 'detailed':
            # Add more context and explanation to response
            response_data['additional_context'] = self.get_detailed_explanation(message)
        elif self.enhanced_profile.communication_style == 'concise':
            # Keep response brief
            response_data['response'] = self.make_concise(response_data.get('response', ''))

        # Generate personalized suggestions based on goals and current projects
        response_data['suggestions'] = self.generate_personalized_suggestions(message)

        # Session 482: Smart Suggestions - Add contextual action-based suggestions
        if hasattr(self, 'smart_suggestions') and self.smart_suggestions and SMART_SUGGESTIONS_AVAILABLE:
            try:
                # Detect action type from tool_calls
                tool_calls = response_data.get('tool_calls', [])
                response_text = response_data.get('response', '')

                # Session 483: Debug logging for smart suggestions
                logger.debug(f"🔍 SmartSuggestions: Checking response ({len(response_text)} chars), tool_calls={len(tool_calls)}")

                action_type = self.smart_suggestions.detect_action_from_response(response_text, tool_calls)

                # Session 483: Log detection result
                logger.info(f"🔍 SmartSuggestions: Detected action_type='{action_type}' from response")

                if action_type:
                    # Record the action for future suggestions
                    self.smart_suggestions.record_action(action_type, output=response_text)

                    # Get smart suggestions based on what was just done
                    smart_suggestions = self.smart_suggestions.get_suggestions(limit=2)

                    if smart_suggestions:
                        # Get quick action buttons for frontend
                        quick_actions = self.smart_suggestions.get_quick_actions()
                        response_data['quick_actions'] = quick_actions

                        # Session 483: Log quick actions being added
                        logger.info(f"✨ SmartSuggestions: Adding {len(quick_actions)} quick_actions: {[qa.get('label', '')[:30] for qa in quick_actions]}")

                        # Append smart suggestions text to response if not already included
                        suggestion_text = self.smart_suggestions.format_for_response(smart_suggestions)
                        if suggestion_text and suggestion_text not in response_data.get('response', ''):
                            # Add as a separate field for frontend flexibility
                            response_data['smart_suggestions'] = [s.text for s in smart_suggestions]
                            response_data['smart_suggestions_formatted'] = suggestion_text

                        logger.info(f"✨ SmartSuggestions: Added {len(smart_suggestions)} contextual suggestions for '{action_type}' action")
                    else:
                        # Session 483: Log when action_type detected but no suggestions returned
                        logger.info(f"⚠️ SmartSuggestions: No suggestions returned for action_type='{action_type}'")
            except Exception as e:
                logger.warning(f"⚠️ SmartSuggestions error: {e}")

        # Session 486: Add reference context for frontend indicator
        if self.reference_resolver and REFERENCE_RESOLVER_AVAILABLE:
            try:
                context_summary = self.reference_resolver.get_context_summary()
                response_data['reference_context'] = context_summary
                if context_summary.get('last_topic') or context_summary.get('items'):
                    logger.info(f"🎯 Session 486: Reference context: {context_summary.get('last_topic') or 'items tracked'}")
            except Exception as e:
                logger.warning(f"⚠️ Reference context error: {e}")

        # Enhance response with memory-based personalization
        if response_data.get('response'):
            response_data['response'] = self._enhance_response_with_memory(
                response_data['response'],
                user_patterns
            )

        # Store interaction as memory with context
        self.store_memory(
            'interaction',
            f"User asked: {message[:100]}...",
            response=response_data.get('response', '')[:100],
            importance=5,
            metadata={
                'full_message': message,
                'response_type': response_data.get('type', 'general'),
                'confidence': response_data.get('confidence', 0.5)
            }
        )

        # Update profile from interaction
        self.update_profile_from_interaction(message, response_data.get('response', ''))

        # Store conversation in database for persistence and future retrieval
        self._store_conversation(message, response_data)

        return response_data

