"""
Enhanced Personal AI Assistant with Database and System Access
===============================================================

This module extends the Personal AI Assistant with direct database access,
system status monitoring, and agent execution capabilities.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection
from django.db.models import Q, Count, Avg
from django.utils import timezone

from core.models import ExtendedUserProfile, EnhancedUserProfile, JobApplication, UserEmbedding, UserMemoryContext
from core.agent_context_middleware import AgentContextMiddleware
from core.personal_ai_assistant import PersonalAIAssistant
from core.llm_enforcer import LLMEnforcer
from core.unified_memory_manager import UnifiedMemoryManager, get_memory_manager
from agents.registry import get_agent_registry
from advisors.registry import get_advisor_registry
from ml.core.ml_engine import MLEngine
try:
    from self_awareness.embeddings import CodebaseEmbeddings
except ImportError:
    # Fallback if CodebaseEmbeddings is not available
    class CodebaseEmbeddings:
        def __init__(self):
            pass

logger = logging.getLogger(__name__)
User = get_user_model()


class EnhancedPersonalAIAssistant(PersonalAIAssistant):
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
                "description": "Generate BRAND NEW images from scratch using text prompts. CRITICAL: Use this agent whenever user wants to CREATE/GENERATE/MAKE images that don't exist yet: 'create banner', 'generate logo', 'make social media post', 'design avatar', 'create profile picture', 'create images matching style', etc. This generates NEW images, not modifications of existing ones. Supports custom dimensions (width/height), quality levels, style preferences, and multiple images. Use this for ALL new image creation requests, even if they mention matching a style.",
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
            {
                "type": "function",
                "name": "coleadership_agent",
                "description": "Get collaborative opinions and recommendations from AI executive team (CTO, COO, Creative Director, CFO, Data Analyst) on creative decisions. Use when user asks 'what do you think', 'should we', 'get opinions', 'is this a good direction', 'thoughts on', 'feedback on', 'worth pursuing', 'ask the team', etc. Can reference specific images/content to get opinions on style, direction, or training decisions.",
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
            {
                "type": "function",
                "name": "web_search",
                "description": "Search the web using Google via Serper API. Use this when the user asks for current information, trends, research, competitor analysis, or needs to find something online. CRITICAL: Use this tool when user says 'research', 'find out about', 'search for', 'look up', 'what are the latest', etc. This enables the 'research and create' autonomous workflow where you can research a topic then generate content based on findings.",
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
            }
        ]

    # Session 125: Tool Execution Handler
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

            # Session 126: Auto-inject project_id from context if available and not already in arguments
            if hasattr(self, '_current_context') and self._current_context:
                if 'project_id' in self._current_context and 'project_id' not in arguments:
                    arguments['project_id'] = self._current_context['project_id']
                    logger.info(f"💡 Auto-injected project_id: {arguments['project_id']}")

            logger.info(f"🔧 Executing tool: {function_name} with args: {arguments}")

            # Session 132: Route to agent orchestrators
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
            # Session 189: Create project from research workflow
            elif function_name == 'create_project_from_research':
                result = self._handle_create_project_from_research(arguments)
            else:
                result = {
                    'success': False,
                    'error': f"Unknown agent: {function_name}"
                }

            # Session 135: Store tool result to preserve task_id for video polling
            self._last_tool_result = result
            logger.info(f"📦 Stored tool result: {result}")

            return result

        except Exception as e:
            logger.error(f"❌ Tool execution error: {e}")
            return {
                'success': False,
                'error': f"Tool execution failed: {str(e)}"
            }

    # Session 131: Agent Handler Methods
    def _resolve_hybrid_image_id(self, image_id: str) -> str:
        """Convert sequential image numbers to UUIDs (Session 131, Session 196 - fixed)."""
        if image_id.isdigit():
            from content.models import ImageHistory
            try:
                seq_num = int(image_id)
                # Session 196: Try sequential_number field first (permanent identifier)
                image = ImageHistory.objects.filter(user=self.user, sequential_number=seq_num).first()
                if image:
                    resolved_id = str(image.id)
                    logger.info(f"✅ Converted image #{seq_num} (seq_number) → UUID {resolved_id[:8]}...")
                    return resolved_id
                # Fallback to positional index for backward compatibility
                image = ImageHistory.objects.filter(user=self.user).order_by('created_at')[seq_num - 1]
                resolved_id = str(image.id)
                logger.info(f"✅ Converted image #{seq_num} (positional) → UUID {resolved_id[:8]}...")
                return resolved_id
            except (IndexError, ImageHistory.DoesNotExist):
                raise ValueError(f'Image #{image_id} not found')
        return image_id

    def _parse_id_range(self, id_str: str) -> List[str]:
        """
        Parse image ID ranges into list of individual IDs (Session 152 - Batch Operations).

        Supports:
        - Single ID: "5" → ["5"]
        - Range: "20-25" → ["20", "21", "22", "23", "24", "25"]
        - List: "5, 8, 12" → ["5", "8", "12"]
        - Combined: "10-15, 20, 25-27" → ["10", "11", "12", "13", "14", "15", "20", "25", "26", "27"]
        - Spaces are ignored: "20 - 25, 30" → ["20", "21", "22", "23", "24", "25", "30"]

        Returns: List of ID strings (numbers or UUIDs)
        """
        id_str = id_str.strip()

        # Check if it's a UUID (contains dashes but is a valid UUID format)
        if '-' in id_str and ',' not in id_str:
            # Could be UUID or range - check if it's a valid UUID
            try:
                import uuid as uuid_module
                uuid_module.UUID(id_str)  # Will raise ValueError if not valid UUID
                return [id_str]  # Single UUID
            except ValueError:
                pass  # Not a UUID, parse as range

        # Parse comma-separated segments
        segments = [seg.strip() for seg in id_str.split(',')]
        result = []

        for segment in segments:
            segment = segment.strip()

            # Check if segment contains range (dash between numbers)
            if '-' in segment:
                # Try to parse as range
                parts = [p.strip() for p in segment.split('-')]
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    start = int(parts[0])
                    end = int(parts[1])
                    if start > end:
                        raise ValueError(f"Invalid range: {segment} (start > end)")
                    result.extend([str(i) for i in range(start, end + 1)])
                else:
                    # Not a valid range, treat as single ID
                    result.append(segment)
            else:
                # Single ID
                result.append(segment)

        # Remove duplicates while preserving order
        seen = set()
        unique_result = []
        for id_val in result:
            if id_val not in seen:
                seen.add(id_val)
                unique_result.append(id_val)

        logger.info(f"📋 Parsed ID range '{id_str}' → {len(unique_result)} IDs: {unique_result[:5]}{'...' if len(unique_result) > 5 else ''}")
        return unique_result

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
        quality = params.get('quality', 'balanced')
        style = params.get('style', 'photorealistic')

        try:
            from agents.creation_agent import CreationAgent

            # Initialize agent
            agent = CreationAgent(user=self.user, project_id=project_id)

            # Execute generation
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
            from agents.trained_creation_agent import TrainedCreationAgent

            # Initialize agent
            agent = TrainedCreationAgent(user=self.user, project_id=project_id)

            # Execute generation with LoRA
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

    def _execute_single_image_operation(self, operation: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single image operation (Session 152: Extracted for batch support)."""
        # Route to appropriate existing tool handler
        if operation == 'upscale':
            return self._tool_upscale_image(tool_args)
        elif operation == 'remove_background':
            return self._tool_remove_background(tool_args)
        elif operation == 'create_variations':
            return self._tool_create_variations(tool_args)
        # elif operation == 'erase_object':  # Deprecated: use search_and_replace with empty replace_prompt
        #     return self._tool_erase_object(tool_args)
        elif operation == 'recolor':
            return self._tool_recolor_image(tool_args)
        # elif operation == 'refine':  # TODO: No backend implementation
        #     return self._tool_refine_image(tool_args)
        elif operation == 'search_and_replace':
            return self._tool_search_and_replace(tool_args)  # Session 151 - also handles removal
        elif operation == 'creative_upscale':
            return self._tool_creative_upscale(tool_args)  # Session 151
        else:
            return {'success': False, 'error': f"Unknown image operation: {operation}"}

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

    def _execute_single_video_enhancement(self, operation: str, video_id: str, params: Dict[str, Any], project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a single video enhancement operation (upscale or apply_effect).
        Session 154: Calls the new ffmpeg-based video enhancement views.
        """
        from django.test.client import RequestFactory
        from django.contrib.auth.models import AnonymousUser
        import json

        try:
            factory = RequestFactory()

            if operation == 'upscale':
                # Build request payload for upscale_video view
                scale_factor = params.get('scale_factor', 2)
                quality = params.get('quality', 'high')

                payload = {
                    'video_id': video_id,
                    'scale_factor': scale_factor,
                    'quality': quality,
                    'project_id': project_id  # Session 156: Pass project_id for linking
                }

                # Create POST request
                request = factory.post(
                    '/api/video/upscale/',
                    data=json.dumps(payload),
                    content_type='application/json'
                )
                request.user = self.user

                # Call the view
                from core.views_video import upscale_video
                response = upscale_video(request)

                # Parse response
                import json
                result = json.loads(response.content)
                logger.info(f"✅ [Session 154] Video upscale result: {result.get('success')}")

                # Normalize response format (convert 'error' to 'message')
                if not result.get('success') and 'error' in result and 'message' not in result:
                    result['message'] = result.pop('error')

                # Session 155: Add agent metadata for UI status indicators
                result['agent'] = 'VideoEditingAgent'
                result['operation'] = operation
                result['operation_display'] = f"Upscaling video {scale_factor}x"

                return result

            elif operation == 'apply_effect':
                # Build request payload for apply_video_effect view
                effect = params.get('effect', 'cinematic')
                intensity = params.get('intensity', 0.7)

                payload = {
                    'video_id': video_id,
                    'effect': effect,
                    'intensity': intensity
                }

                # Create POST request
                request = factory.post(
                    '/api/video/effects/',
                    data=json.dumps(payload),
                    content_type='application/json'
                )
                request.user = self.user

                # Call the view
                from core.views_video import apply_video_effect
                response = apply_video_effect(request)

                # Parse response
                import json
                result = json.loads(response.content)
                logger.info(f"✅ [Session 154] Video effect result: {result.get('success')}")

                # Normalize response format (convert 'error' to 'message')
                if not result.get('success') and 'error' in result and 'message' not in result:
                    result['message'] = result.pop('error')

                # Session 155: Add agent metadata for UI status indicators
                result['agent'] = 'VideoEditingAgent'
                result['operation'] = operation
                result['operation_display'] = f"Applying {effect} effect"

                return result

            else:
                return {'success': False, 'message': f"Unknown operation: {operation}"}

        except Exception as e:
            logger.error(f"❌ [Session 154] Video enhancement error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {'success': False, 'message': str(e)}

    def _execute_single_batch_video_operation(self, operation: str, video_id: str, params: Dict[str, Any], project_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Session 166: Execute a single video operation within a batch.
        Routes to the appropriate tool handler based on operation type.
        Supports all video editing operations for batch processing.
        """
        # Build tool arguments
        tool_args = {
            'video_id': video_id,
            'project_id': project_id
        }
        tool_args.update(params)  # Merge operation-specific params

        try:
            # Route to appropriate handler based on operation
            if operation == 'upscale':
                return self._execute_single_video_enhancement(operation, video_id, params, project_id)
            elif operation == 'apply_effect':
                return self._execute_single_video_enhancement(operation, video_id, params, project_id)
            elif operation == 'extract_frame':
                return self._tool_extract_video_frame(tool_args)
            elif operation == 'reverse':
                return self._tool_reverse_video(tool_args)
            elif operation == 'trim':
                return self._tool_trim_video(tool_args)
            elif operation == 'speed_change':
                return self._tool_change_video_speed(tool_args)
            elif operation == 'rotate_flip':
                return self._tool_rotate_flip(tool_args)
            elif operation == 'fade':
                return self._tool_fade_video(tool_args)
            elif operation == 'crop_resize':
                return self._tool_crop_resize(tool_args)
            elif operation == 'audio_control':
                return self._tool_audio_control(tool_args)
            elif operation == 'add_watermark':
                return self._tool_add_watermark(tool_args)
            elif operation == 'blur_region':
                return self._tool_blur_region(tool_args)
            elif operation == 'stabilize_video':
                return self._tool_stabilize_video(tool_args)
            elif operation == 'add_text_animation':
                return self._tool_add_text_animation(tool_args)
            elif operation == 'chroma_key':
                return self._tool_chroma_key(tool_args)
            elif operation == 'export_for_platform':
                return self._tool_export_for_platform(tool_args)
            elif operation == 'auto_caption':
                return self._tool_auto_caption(tool_args)
            # Session 167: DaVinci Resolve operations
            elif operation == 'render_professional':
                return self._tool_render_professional(tool_args)
            elif operation == 'apply_lut':
                return self._tool_apply_lut(tool_args)
            elif operation == 'color_grade_professional':
                return self._tool_color_grade_professional(tool_args)
            else:
                return {'success': False, 'error': f"Unsupported batch operation: {operation}"}
        except Exception as e:
            logger.error(f"❌ [Session 166] Batch operation error: {e}")
            return {'success': False, 'error': str(e), 'video_id': video_id}

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
            from agents.meeting_coordinator_agent import MeetingCoordinatorAgent

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
                # Infer stance
                stance = 'neutral'
                lower_text = response_text.lower()
                if any(w in lower_text for w in ['recommend', 'support', 'approve', 'yes', 'definitely', 'great idea']):
                    stance = 'support'
                elif any(w in lower_text for w in ['concern', 'risk', 'caution', 'careful', 'consider']):
                    stance = 'concern'
                elif any(w in lower_text for w in ['object', 'against', 'reject', 'no', 'not recommend']):
                    stance = 'objection'
                elif any(w in lower_text for w in ['alternative', 'instead', 'another option', 'what if']):
                    stance = 'alternative'

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
    def _tool_upscale_image(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the upscale_image tool - Session 128."""
        logger.info(f"🎨 UPSCALE_IMAGE TOOL CALLED!")
        logger.info(f"🤖 Delegating to Image Editing Agent...")

        try:
            image_id = arguments['image_id']

            # Get current project if in session
            current_project = getattr(self, 'project', None)  # Session 179: Fixed project access

            # Session 128: Delegate to specialized Image Editing Agent
            from agents.image_editing_agent import ImageEditingAgent

            agent = ImageEditingAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            # Execute agent workflow
            result = agent.execute(
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
            from agents.image_editing_agent import ImageEditingAgent

            agent = ImageEditingAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

            # Execute agent workflow
            result = agent.execute(
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
            from agents.image_editing_agent import ImageEditingAgent

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
            from agents.image_editing_agent import ImageEditingAgent

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
            from agents.image_editing_agent import ImageEditingAgent

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
            from agents.image_editing_agent import ImageEditingAgent

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
            from agents.image_editing_agent import ImageEditingAgent

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
            from agents.image_editing_agent import ImageEditingAgent

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
            from agents.video_generation_agent import VideoGenerationAgent

            agent = VideoGenerationAgent(
                user=self.user,
                project_id=str(current_project.id) if current_project else arguments.get('project_id')
            )

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
            from agents.video_generation_agent import VideoGenerationAgent

            # Don't need project_id for extension - it inherits from original video
            agent = VideoGenerationAgent(
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

    # Session 189: Create project from research workflow
    def _handle_create_project_from_research(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle create_project_from_research tool - Session 189.

        Creates a new creative project from research results and generated images.
        This enables the "research → create → organize" autonomous workflow.
        """
        logger.info(f"📁 CREATE_PROJECT_FROM_RESEARCH TOOL CALLED!")

        try:
            from content.models import CreativeProject, ImageHistory
            from core.utils.id_resolver import resolve_image_id

            project_name = arguments.get('project_name', 'Research Project')
            research_summary = arguments.get('research_summary', '')
            image_ids = arguments.get('image_ids', [])
            category = arguments.get('category', 'branding')
            suggested_next_steps = arguments.get('suggested_next_steps', [])

            logger.info(f"📁 Creating project: {project_name}")
            logger.info(f"   Category: {category}")
            logger.info(f"   Images to include: {image_ids}")

            # Create the project
            project = CreativeProject.objects.create(
                user=self.user,
                name=project_name,
                category=category,
                goal=research_summary[:500] if research_summary else f"Research-based project: {project_name}",
                status='active',
                metadata={
                    'auto_generated': True,
                    'source': 'research_workflow',
                    'research_summary': research_summary,
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

            # Build response message
            response_parts = [
                f"## 📁 Project Created: **{project_name}**\n",
                f"**Category:** {category.replace('_', ' ').title()}",
                f"**Images Included:** {images_linked}",
            ]

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
                'linked_images': linked_image_details
            }

        except Exception as e:
            logger.error(f"❌ Create project from research error: {e}", exc_info=True)
            return {
                'success': False,
                'error': f"Failed to create project: {str(e)}"
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
                video = VideoHistory.objects.create(
                    user=self.user,
                    prompt=prompt,
                    task_id=result.task_id,
                    status='processing',
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

    # Session 128: Updated to use Audio Generation Agent
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
            from agents.audio_generation_agent import AudioGenerationAgent

            agent = AudioGenerationAgent(
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
            from agents.audio_generation_agent import AudioGenerationAgent

            agent = AudioGenerationAgent(
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
            from agents.video_agent import VideoAgent
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
            from agents.three_d_generation_agent import ThreeDGenerationAgent

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
            from agents.video_editing_agent import VideoEditingAgent

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
            from agents.video_editing_agent import VideoEditingAgent

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

    def _parse_video_id_range(self, video_id_str: str) -> list:
        """Parse video ID string into list of IDs. Supports '1-3' and '1, 2, 3' formats."""
        video_ids = []
        parts = video_id_str.replace(' ', '').split(',')
        for part in parts:
            if '-' in part:
                try:
                    start, end = part.split('-')
                    for i in range(int(start), int(end) + 1):
                        video_ids.append(str(i))
                except ValueError:
                    video_ids.append(part)
            else:
                video_ids.append(part)
        return video_ids

    def _ensure_enhanced_profile(self):
        """Ensure the user has an enhanced profile."""
        try:
            self.enhanced_profile = EnhancedUserProfile.objects.get(user=self.user)
        except EnhancedUserProfile.DoesNotExist:
            self.enhanced_profile = EnhancedUserProfile.objects.create(user=self.user)
            logger.info(f"Created enhanced profile for {self.user.username}")

    # Session 122: Asset Tracking Methods for Intelligent Chaining
    def track_generated_image(self, image_id: str, image_url: str, prompt: str, asset_type: str = 'logo'):
        """
        Track a newly generated image for intelligent chaining.

        Args:
            image_id: Database ID of the image
            image_url: URL to the generated image
            prompt: The prompt used to generate the image
            asset_type: Type of image (logo, social_media, general, etc.)
        """
        from django.utils import timezone

        asset_data = {
            'id': image_id,
            'url': image_url,
            'prompt': prompt,
            'type': asset_type,
            'timestamp': timezone.now().isoformat()
        }

        self.recently_generated_assets['images'].append(asset_data)
        self.recently_generated_assets['last_updated'] = timezone.now().isoformat()

        # Keep only last 10 images (prevent memory bloat)
        if len(self.recently_generated_assets['images']) > 10:
            self.recently_generated_assets['images'] = self.recently_generated_assets['images'][-10:]

        logger.info(f"📸 Tracked new image: {asset_type} (ID: {image_id})")

    def track_generated_video(self, video_id: str, video_url: str, prompt: str, source_image_id: Optional[str] = None):
        """
        Track a newly generated video for context awareness.

        Args:
            video_id: Database ID of the video
            video_url: URL to the generated video
            prompt: The prompt used to generate the video
            source_image_id: ID of source image if this was image-to-video
        """
        from django.utils import timezone

        asset_data = {
            'id': video_id,
            'url': video_url,
            'prompt': prompt,
            'source_image_id': source_image_id,
            'timestamp': timezone.now().isoformat()
        }

        self.recently_generated_assets['videos'].append(asset_data)
        self.recently_generated_assets['last_updated'] = timezone.now().isoformat()

        # Keep only last 10 videos
        if len(self.recently_generated_assets['videos']) > 10:
            self.recently_generated_assets['videos'] = self.recently_generated_assets['videos'][-10:]

        logger.info(f"🎬 Tracked new video (ID: {video_id}, source_image: {source_image_id})")

    def get_recent_assets_context(self) -> str:
        """
        Get formatted context of recently generated assets for AI prompt.

        Returns:
            Formatted string describing recent assets
        """
        from django.utils import timezone
        from datetime import timedelta

        images = self.recently_generated_assets.get('images', [])
        videos = self.recently_generated_assets.get('videos', [])

        if not images and not videos:
            return "No recently generated assets in this session."

        # Filter to assets from last 10 minutes (keep context fresh)
        cutoff_time = timezone.now() - timedelta(minutes=10)

        recent_images = [
            img for img in images
            if timezone.datetime.fromisoformat(img['timestamp']) > cutoff_time
        ]

        recent_videos = [
            vid for vid in videos
            if timezone.datetime.fromisoformat(vid['timestamp']) > cutoff_time
        ]

        context_parts = []

        if recent_images:
            context_parts.append(f"📸 {len(recent_images)} images generated in last 10 minutes:")
            for img in recent_images[-5:]:  # Show last 5
                context_parts.append(f"  - {img['type'].title()} (ID: {img['id']}): \"{img['prompt'][:50]}...\"")

        if recent_videos:
            context_parts.append(f"🎬 {len(recent_videos)} videos generated in last 10 minutes:")
            for vid in recent_videos[-5:]:
                source_info = f", from image {vid['source_image_id']}" if vid['source_image_id'] else ""
                context_parts.append(f"  - Video (ID: {vid['id']}{source_info}): \"{vid['prompt'][:50]}...\"")

        return "\n".join(context_parts)

    def get_latest_generated_images(self, limit: int = 5) -> List[Dict]:
        """
        Get the most recently generated images for use in image-to-video.

        Args:
            limit: Maximum number of images to return

        Returns:
            List of recent image data dictionaries
        """
        images = self.recently_generated_assets.get('images', [])
        return images[-limit:] if images else []

    def get_project_assets_context(self, project) -> str:
        """
        Get ALL assets from a specific project for long-term work.

        Session 122: Smart Hybrid - Use this when working in a project context
        for customer work that spans hours/days, not just 10-minute sessions.

        Args:
            project: CreativeProject instance

        Returns:
            Formatted string describing all project assets
        """
        from content.models import ImageHistory, VideoHistory

        try:
            # Session 129: Get MORE images so GPT can see early sequential numbers (not just recent)
            # Get images from project (last 50 - enough to see most assets including #1, #2, etc.)
            recent_images = ImageHistory.objects.filter(
                project=project
            ).order_by('created_at')[:50]  # Changed to chronological order so #1, #2, etc. appear first

            # Get videos from project (last 20)
            recent_videos = VideoHistory.objects.filter(
                project=project
            ).order_by('created_at')[:20]  # Changed to chronological order

            context_parts = [f"📁 **Project: {project.name}** (All assets available)"]

            if recent_images.exists():
                context_parts.append(f"\n📸 {recent_images.count()} recent images in project:")
                for img in recent_images:
                    # Determine type from prompt or image_type
                    img_type = 'image'
                    if 'logo' in img.prompt.lower():
                        img_type = 'logo'
                    elif any(word in img.prompt.lower() for word in ['character', 'mascot']):
                        img_type = 'character'
                    elif any(word in img.prompt.lower() for word in ['product', 'merchandise']):
                        img_type = 'product'

                    seq_num = img.get_sequential_number()
                    context_parts.append(f"  - Image #{seq_num}: {img_type.title()} (ID: {img.id}): \"{img.prompt[:50]}...\"")

            if recent_videos.exists():
                context_parts.append(f"\n🎬 {recent_videos.count()} recent videos in project:")
                for vid in recent_videos:
                    seq_num = vid.get_sequential_number()
                    source_info = f", from image {vid.source_image.id}" if vid.source_image else ""
                    context_parts.append(f"  - Video #{seq_num} (ID: {vid.id}{source_info}): \"{vid.prompt[:50]}...\"")

            if not recent_images.exists() and not recent_videos.exists():
                context_parts.append("\n⚠️ No assets in project yet")

            return "\n".join(context_parts)

        except Exception as e:
            logger.error(f"Error getting project assets context: {e}")
            return f"📁 Project: {project.name} (Unable to load assets)"

    def execute_database_query(self, query: str, params: List = None) -> Dict[str, Any]:
        """
        Execute a database query safely and return results.

        Args:
            query: SQL query to execute
            params: Query parameters for safe execution

        Returns:
            Dictionary with query results and metadata
        """
        try:
            with connection.cursor() as cursor:
                # Log the query for audit
                self.database_queries_executed.append({
                    'query': query,
                    'timestamp': timezone.now().isoformat(),
                    'user': self.user.username
                })

                # Execute query
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)

                # Fetch results
                if query.strip().upper().startswith('SELECT'):
                    columns = [col[0] for col in cursor.description]
                    results = cursor.fetchall()

                    # Convert to list of dictionaries
                    data = [dict(zip(columns, row)) for row in results]

                    return {
                        'success': True,
                        'data': data,
                        'count': len(data),
                        'query': query,
                        'columns': columns
                    }
                else:
                    # For non-SELECT queries, return affected rows
                    return {
                        'success': True,
                        'affected_rows': cursor.rowcount,
                        'query': query
                    }

        except Exception as e:
            logger.error(f"Database query error: {e}")
            return {
                'success': False,
                'error': str(e),
                'query': query
            }

    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status including database, agents, and platform health.

        Returns:
            Dictionary with system status information
        """
        status = {
            'timestamp': timezone.now().isoformat(),
            'database': {},
            'agents': {},
            'embeddings': {},
            'platform': {},
            'websockets': {},
            'user': {}
        }

        try:
            # Check database status - use existing tables
            try:
                embeddings_count = self.execute_database_query(
                    "SELECT COUNT(*) as count FROM core_userembedding"
                )
                status['embeddings']['total_count'] = embeddings_count.get('data', [{}])[0].get('count', 0)

                # Check recent embeddings
                recent_embeddings = self.execute_database_query(
                    """
                    SELECT COUNT(*) as count
                    FROM core_userembedding
                    WHERE created_at > %s
                    """,
                    [timezone.now() - timedelta(days=1)]
                )
                status['embeddings']['last_24h'] = recent_embeddings.get('data', [{}])[0].get('count', 0)
            except Exception as e:
                logger.warning(f"Error checking embeddings: {e}")
                status['embeddings']['total_count'] = 0
                status['embeddings']['last_24h'] = 0

            # Check agents status
            agent_registry = get_agent_registry()
            status['agents']['total_registered'] = len(agent_registry.list_agents())
            status['agents']['categories'] = {}
            for agent in agent_registry.list_agents():
                category = agent.get('category', 'uncategorized')
                status['agents']['categories'][category] = status['agents']['categories'].get(category, 0) + 1

            # Check job applications
            job_apps_count = self.execute_database_query(
                "SELECT COUNT(*) as count FROM core_jobapplication WHERE user_id = %s",
                [self.user.id]
            )
            status['user']['job_applications'] = job_apps_count.get('data', [{}])[0].get('count', 0)

            # Check user embeddings
            user_embeddings_count = self.execute_database_query(
                "SELECT COUNT(*) as count FROM core_userembedding WHERE user_id = %s",
                [self.user.id]
            )
            status['user']['embeddings'] = user_embeddings_count.get('data', [{}])[0].get('count', 0)

            # Check WebSocket status
            try:
                from core.unified_hub import UnifiedWebSocketHub
                hub = UnifiedWebSocketHub()
                ws_status = hub.get_status()
                status['websockets'] = {
                    'active': ws_status.get('websocket_active', False),
                    'connections': ws_status.get('active_connections', 0),
                    'last_message': ws_status.get('last_message_time')
                }
            except Exception as e:
                status['websockets']['error'] = str(e)

            # Calculate platform operational percentage
            operational_checks = [
                status['embeddings']['total_count'] > 0,
                status['agents']['total_registered'] > 0,
                status.get('websockets', {}).get('active', False),
                'error' not in status.get('database', {})
            ]
            status['platform']['operational_percentage'] = (sum(operational_checks) / len(operational_checks)) * 100

            # Platform health summary
            status['platform']['health'] = 'healthy' if status['platform']['operational_percentage'] > 75 else 'degraded'
            status['platform']['summary'] = f"Platform is {status['platform']['operational_percentage']:.0f}% operational"

        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            status['error'] = str(e)
            status['platform']['health'] = 'error'

        return status

    def search_embeddings(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search embeddings database for relevant content.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of matching embeddings with metadata
        """
        try:
            # Search in unified embeddings
            results = self.execute_database_query(
                """
                SELECT
                    id, content_type, content_id, content_text,
                    metadata, relevance_score, created_at
                FROM self_awareness_unifiedembedding
                WHERE content_text ILIKE %s
                ORDER BY relevance_score DESC, created_at DESC
                LIMIT %s
                """,
                [f'%{query}%', limit]
            )

            if results.get('success'):
                return results.get('data', [])

            # Fallback to user embeddings
            user_results = self.execute_database_query(
                """
                SELECT
                    id, content, confidence_score,
                    metadata, created_at
                FROM core_userembedding
                WHERE user_id = %s AND content ILIKE %s
                ORDER BY confidence_score DESC, created_at DESC
                LIMIT %s
                """,
                [self.user.id, f'%{query}%', limit]
            )

            return user_results.get('data', [])

        except Exception as e:
            logger.error(f"Error searching embeddings: {e}")
            return []

    def execute_agent(self, agent_name: str, task: str) -> Dict[str, Any]:
        """
        Execute an agent with a specific task.

        Args:
            agent_name: Name of the agent to execute
            task: Task description for the agent

        Returns:
            Agent execution results
        """
        try:
            agent_registry = get_agent_registry()

            # Find the agent
            agents = [a for a in agent_registry.list_agents() if agent_name.lower() in a.get('name', '').lower()]

            if not agents:
                return {
                    'success': False,
                    'error': f'Agent "{agent_name}" not found',
                    'available_agents': [a.get('name') for a in agent_registry.list_agents()[:10]]
                }

            agent = agents[0]

            # Execute agent (simplified - in production this would use proper agent execution)
            result = {
                'success': True,
                'agent': agent.get('name'),
                'task': task,
                'status': 'executed',
                'message': f"Agent {agent.get('name')} has been triggered with task: {task}",
                'metadata': {
                    'category': agent.get('category'),
                    'description': agent.get('description'),
                    'timestamp': datetime.now().isoformat()
                }
            }

            return result

        except Exception as e:
            logger.error(f"Error executing agent: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _generate_ai_response(self, message: str, context: Dict[str, Any]) -> str:
        """
        Generate real AI response using LLMEnforcer.

        Args:
            message: User's message
            context: Context including user profile, memories, etc.

        Returns:
            AI-generated response string
        """
        logger.debug("_generate_ai_response() ENTERED")
        # Build comprehensive context using UnifiedMemoryManager
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

        # Load recent conversation history from database for context
        recent_conversations = self._load_conversation_history(limit=5)
        if recent_conversations and not conversation_context:
            conversation_context = self._format_conversation_context(recent_conversations)

        # Extract user context (it might be nested)
        user_context = context.get('user_context', {})
        user_first_name = user_context.get('first_name') or context.get('first_name', 'User')
        user_last_name = user_context.get('last_name') or context.get('last_name', '')

        # Build the comprehensive prompt
        system_prompt = f"""You are a highly intelligent personal AI assistant for {self.user.username}.
You have access to their complete profile and learning history, AND the current conversation context.

User Profile:
- Name: {user_first_name} {user_last_name}
- Username: {self.user.username}
- Role: {self.enhanced_profile.primary_role or 'Not specified'}
- Communication Style: {self.enhanced_profile.communication_style or 'balanced'}
- Learning Style: {self.enhanced_profile.learning_style or 'mixed'}
- Long-term Goals: {', '.join(self.enhanced_profile.long_term_goals) if self.enhanced_profile.long_term_goals else 'Not specified'}
- Current Projects: {', '.join(self.enhanced_profile.current_projects) if self.enhanced_profile.current_projects else 'Not specified'}
- Core Skills: {', '.join(list(self.enhanced_profile.core_competencies.keys())[:5]) if self.enhanced_profile.core_competencies else 'Not specified'}

Current Conversation Context:
{conversation_context if conversation_context else 'This is the beginning of our conversation.'}

Recent Memories:
{memory_context}

Recent Agent Activities:
{agent_context}

{f'''User Style Preferences (Session 169 - Personalized Generation):
{style_preferences_context}
''' if style_preferences_context else ''}Available Assets in Current Context:
{assets_context}

CRITICAL - Project Context (Session 132 + Session 181 Enhancement):
{f"- Active Project ID: {self._current_context.get('project_id')}" if hasattr(self, '_current_context') and self._current_context and 'project_id' in self._current_context else "- No active project"}
- When using image_generation_agent, video_generation_agent, audio_generation_agent, three_d_generation_agent, or video_editing_agent, you MUST include the project_id parameter with the EXACT UUID shown above
- DO NOT make up project IDs like "admin-project-assets" or "user-project" - use the actual UUID from "Active Project ID" above
- If no Active Project ID is shown above, omit the project_id parameter (let the system handle it)

{f'''PROJECT BRIEF (Session 181 - Creative Direction):
{project_brief_context}
''' if project_brief_context else ''}

IMPORTANT - Image & Video References:
- When user says "image 2", "image number two", or "image #2", they mean Image #2 from the list above
- When user says "video 1", they mean Video #1 from the list above
- Use the sequential number (e.g., "2") as the image_id parameter in tool calls
- The system will automatically convert sequential numbers to the correct UUIDs

System Capabilities:
- You can check system status and database queries
- You can execute agents on behalf of the user
- You have access to 149 registered agents and 25 legendary advisors
- You can search embeddings and access platform intelligence

CRITICAL INSTRUCTIONS:
1. ALWAYS address the user by their name: {user_first_name}
2. Maintain conversation continuity - reference what we discussed earlier
3. Build upon previous exchanges naturally - don't restart the conversation
4. Pay attention to nuanced language - distinguish between "exploring/looking at" vs "updating/changing"
5. If they're exploring profile options, help them understand what's available
6. If they're actually making changes, help them complete the process
7. **INTELLIGENT ASSET CHAINING:** If the user requests video generation AND there are recently generated images (especially logos, characters, or products), STRONGLY suggest using image-to-video mode with those image IDs. Format your response to include: "VIDEO: image_to_video [image_id] [prompt]"
8. **AVOID TEXT-TO-VIDEO WHEN IMAGES EXIST:** Do NOT use text-to-video mode if relevant images were just generated. Use image-to-video instead for better consistency and quality
9. **CRITICAL - RESPECT EXACT COUNTS:** When the user specifies a number (e.g., "create 2 videos", "make 5 images"), create EXACTLY that many assets. Do NOT multiply by the number of available images. Example: "Create 3 logos and 2 videos using those logos" = create exactly 3 logos + exactly 2 videos (NOT 2 videos per logo!). Pick the BEST logo(s) to use for the specified number of videos.
10. **CREDIT CONSERVATION:** Video generation is expensive (~22% of monthly credits per video). ALWAYS confirm the exact count before generating videos. If unclear, ask the user to clarify the exact number they want.
11. **AGENT ORCHESTRATION (SESSION 134 - DUAL-AGENT ARCHITECTURE):** You have access to specialized agent orchestrators. ALWAYS explicitly announce which agent you're routing the request to:
   - NEW image creation (standard) → "🎨 Routing to Creation Agent..." (Stability AI)
   - NEW image creation (trained style) → "🎨 Routing to Trained Creation Agent..." (FLUX + LoRA when character_model_name is specified)
   - EXISTING image editing → "✏️ Routing to Image Editing Agent..." (upscale, remove_background, etc.)
   - Video operations → "🎬 Routing to Video Generation Agent..."
   - Audio operations → "🎤 Routing to Audio Generation Agent..."
   - 3D conversion → "🎨 Routing to 3D Generation Agent..."
   - Video editing → "✂️ Routing to Video Editing Agent..."
12. **TOOL CALLING PREAMBLE (SESSION 129 - GPT-5.1 REQUIREMENT):** When you have access to a tool that can fulfill the user's request, you MUST call that tool. State which agent is handling it, then IMMEDIATELY execute the tool call. Do NOT just say you will do something without actually calling the tool function.
13. **PERSONALIZED STYLE (SESSION 169 - LEARNING SYSTEM):** If "User Style Preferences" are shown above, incorporate them when generating new content. Example: if user prefers "vibrant" colors and "modern" style, enhance prompts to include those preferences. Say "🧠 Using your learned style preferences..." when applying them.
14. **SINGLE TOOL CALL FOR COUNTED REQUESTS (SESSION 189):** When the user requests a specific number of items (e.g., "create 3 images"), generate ALL requested items in ONE tool call by setting the count parameter appropriately. Do NOT make multiple tool calls to generate the same type of content. Example: "create 3 DreamWorks images" = ONE call to image_generation_agent with count=3, NOT three separate calls.
15. **NO HALLUCINATING COMPLETED WORK (SESSION 189 - CRITICAL):** NEVER claim that images, videos, or other content has been created unless you actually called the tool in THIS conversation turn. If you receive tool results that only show "web_search" was executed, you CANNOT claim images were generated. You MUST call image_generation_agent to actually create images. The continuation message will tell you which tools were ACTUALLY executed - only those tools have run.
16. **NEVER REPEAT COMPLETED WORK (SESSION 189 - CRITICAL):** When you receive a continuation message, it will include a "COMPLETED WORK" section showing what has ALREADY been done:
    - If you see "🛑 IMAGE GENERATION COMPLETE", do NOT call image_generation_agent again.
    - If you see "🛑 STRATEGIC/EXECUTIVE REVIEW COMPLETE", do NOT call coleadership_agent or strategic_review again.
    - Instead, proceed to the NEXT STEP suggested in the continuation message.
    REPEATING TOOL CALLS WASTES USER CREDITS AND IS STRICTLY FORBIDDEN.
17. **WORKFLOW ORCHESTRATION AGENT (SESSION 191 - HIGHEST PRIORITY):**
    ⚡ CRITICAL: For ANY request involving BOTH "research" AND "create/make/generate":
    ✅ Call workflow_orchestration_agent(workflow="research_and_create_logos", topic="...", count=N)
    ⛔ DO NOT call web_search, coleadership_agent, image_generation_agent, or character_training_agent individually!
    ⛔ DO NOT call audio_generation_agent - logo workflows do NOT need audio!

    The workflow_orchestration_agent will AUTOMATICALLY handle ALL steps:
    1. Web research (research trends and best practices)
    2. Executive review (get co-leadership creative direction)
    3. Image generation (create the logos)
    4. Project organization (save everything to a project)

    Examples that MUST use workflow_orchestration_agent:
    - "Research modern AI company logo trends and create 3 professional logos"
      → workflow_orchestration_agent(workflow="research_and_create_logos", topic="modern AI company", count=3)
    - "Look up fitness brand logos and make 5 designs"
      → workflow_orchestration_agent(workflow="research_and_create_logos", topic="fitness brand", count=5)

    This ensures proper order and prevents tool calling errors. ONE tool call handles everything!

18. **LOGO GENERATION RULE (SESSION 190):** When generating logos:
    - Each image should contain EXACTLY ONE logo design, NOT multiple logos
    - Use count parameter to generate multiple separate images (e.g., count=3 for 3 different logo images)
    - WRONG: "three distinct logo concepts in one image" or "logo set with multiple designs"
    - CORRECT: "single professional logo design" with count=3 to get 3 separate logo images
    - The prompt should describe ONE logo. The count parameter handles creating multiple images.

**Example - CORRECT (Session 191 - Workflow Orchestration Agent):**
User: "Research cloud computing logo trends and create 3 modern logos"
Call: workflow_orchestration_agent(workflow="research_and_create_logos", topic="cloud computing", count=3)
[ONE tool call handles ALL steps automatically: research → executive review → image generation → project creation]

**Example - CORRECT (Session 131 - Agent Orchestration):**
User: "Remove background from image 3"
Your response: "🎨 Routing to Image Editing Agent for background removal on image #3..."
[Then you MUST call: image_editing_agent(operation="remove_background", image_id="3")]

**Example - CORRECT (Session 131 - Agent Orchestration):**
User: "Animate image 16"
Your response: "🎬 Routing to Video Generation Agent to animate image #16..."
[Then you MUST call: video_generation_agent(operation="animate", params={{"image_id": "16"}})]

**Example - CORRECT (Session 168 - ProRes/DNxHD Rendering):**
User: "Render video 1 in ProRes 422"
Your response: "✂️ Routing to Video Editing Agent for professional ProRes 422 rendering..."
[Then you MUST call: video_editing_agent(operation="render_professional", video_id="1", params={{"codec": "prores_422"}})]

**Example - CORRECT (Session 167 - Professional Color Grading):**
User: "Apply cinematic grading to video 2"
Your response: "✂️ Routing to Video Editing Agent for professional color grading..."
[Then you MUST call: video_editing_agent(operation="color_grade_professional", video_id="2", params={{"grade_type": "cinematic"}})]

**Example - WRONG:**
User: "Convert image 25 to 3D"
Your response: "✅ Conversion to 3D model is starting! This will take about 45-60 seconds."
[NO tool call made - THIS IS WRONG! You must announce the agent AND call the tool!]

**Remember:** Always announce which agent is handling the request, then execute the agent orchestrator tool. Never say you'll do something without executing it.

<persistence>
- You are an autonomous agent - please keep going until the user's query is COMPLETELY resolved, before ending your turn and yielding back to the user.
- Only terminate your turn when you are SURE that the problem is solved and the tool has been executed.
- Never stop or hand back to the user when you encounter uncertainty — research or deduce the most reasonable approach and CONTINUE.
- Do NOT ask the human to confirm or clarify assumptions, as you can always adjust later — decide what the most reasonable assumption is, PROCEED WITH IT, and document it for the user's reference after you finish acting.
- When you identify a tool that can fulfill the user's request, EXECUTE IT IMMEDIATELY after your brief explanation. Do not wait for confirmation.
</persistence>

Respond in a helpful, personalized way that:
1. Starts by addressing {user_first_name} by name
2. References the current conversation context and continues the discussion naturally
3. If they mentioned updating their profile, acknowledge and build on that
4. References relevant past interactions and learned preferences
5. Mentions recent agent activities when relevant
6. Suggests next actions based on their goals and current conversation
7. Uses their preferred communication style ({self.enhanced_profile.communication_style or 'balanced'})
"""

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
            # Session 131: FORCE tool usage with "required" mode for operations
            tools = self.get_tool_definitions()

            # Session 131: Detect if this is an operation request (stronger tool forcing)
            operation_keywords = [
                # Image operations (broad keywords for workflow support)
                'generate image', 'create image', 'draw', 'make image', 'picture of',
                'create banner', 'create post', 'create avatar', 'create profile',  # Session 131: Workflow keywords
                'social media banner', 'social media post', 'profile image', 'avatar image',  # Session 131: Workflow phrases
                'upscale', 'remove background', 'create variation', 'erase', 'recolor', 'refine',
                # Video operations - Generation
                'animate', 'generate video', 'extend video', 'chain video', 'make video',
                'create video', 'promo video', 'marketing video',  # Session 131: Workflow keywords
                # Video operations - Phase 1 (Session 159-160)
                'extract frame', 'reverse video', 'trim video', 'speed', 'slow motion', 'speed up',
                'concatenate', 'combine videos', 'merge videos',
                # Video operations - Phase 2 (Session 161) 🆕
                'rotate', 'flip', 'turn upside', '90 degrees', '180 degrees', '270 degrees',  # Rotate/Flip
                'fade in', 'fade out', 'add fade',  # Fade
                'crop', 'resize', 'aspect ratio', 'make square', 'make portrait', 'make landscape', '16:9', '9:16', '1:1',  # Crop/Resize
                'mute', 'volume', 'extract audio', 'audio control',  # Audio Controls
                'picture in picture', 'pip', 'overlay video', 'put video in corner',  # Picture-in-Picture
                # Session 163: Watermark/Logo
                'watermark', 'add watermark', 'logo', 'add logo', 'overlay image', 'brand video',
                # Session 163: Blur Region
                'blur', 'add blur', 'blur region', 'privacy blur', 'censor', 'pixelate', 'hide face',
                # Session 164: Video Stabilization
                'stabilize', 'stabilize video', 'fix shaky', 'remove shake', 'smooth video', 'deshake', 'camera shake', 'shaky video',
                # Session 164: Text Animations
                'text animation', 'animated text', 'scrolling text', 'scroll text', 'add title', 'add credits', 'ticker', 'news ticker', 'rolling credits', 'fade text',
                # Audio operations
                'generate voice', 'voiceover', 'text to speech',
                # 3D & editing
                'convert to 3d', 'text overlay', 'color grading',
                # Character training (Session 133) - Session 173: Added 'flux' keyword
                'train style', 'train model', 'train lora', 'learn style', 'character training',
                'create style model', 'learn visual style', 'train project style',
                'flux lora', 'flux model', 'train a flux',
                # Session 173: Co-Leadership / Opinion requests
                'what do you think', 'what does the team think', 'get opinions', 'get the team',
                'should we', 'should i', 'opinion on', 'thoughts on', 'feedback on',
                'creative team', 'technical team', 'cto think', 'coo think',
                'is this a good', 'worth pursuing', 'good direction', 'right approach',
                'ask the agents', 'consult the team', 'team input', 'agent opinions',
                # Session 184: Web Search & Brand Video keywords (restored autonomous workflow)
                'research', 'search for', 'look up', 'find out', 'what are the latest',
                'brand video', 'create brand', 'promotional video', 'promo videos',
                'create logos', 'create logo', 'make logos', 'make logo',
                'cyberpunk', 'cinematic style', 'modern style', 'playful style'
            ]
            is_operation = any(keyword in message.lower() for keyword in operation_keywords)

            if is_operation:
                # FORCE tool execution for operations
                tool_choice = {
                    "type": "allowed_tools",
                    "mode": "required",  # Session 131: MUST use a tool, cannot just respond with text
                    "tools": [{"type": "function", "name": t["name"]} for t in tools]
                }
                logger.info(f"🎯 FORCING tool execution (mode: required) - {len(tools)} tools available")
            else:
                # Auto mode for general conversation
                tool_choice = {
                    "type": "allowed_tools",
                    "mode": "auto",
                    "tools": [{"type": "function", "name": t["name"]} for t in tools]
                }
                logger.info(f"🔧 Calling LLM with {len(tools)} tools (mode: auto)...")
            # Session 184: Increased max_tokens from 500 to 1500 to prevent
            # truncation of tool call arguments (JSON can be longer than expected!)
            ai_result = self.llm_enforcer.enforce_real_ai(
                prompt=message,
                context=system_prompt,
                agent_name="PersonalAssistant",
                task_type="conversation",
                max_tokens=1500,  # Session 184: Increased from 500 to prevent tool call truncation!
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

                    # Session 155 Fix: Return tool_calls to frontend for execution
                    # DON'T execute in backend - let frontend handle it for proper UX
                    # Session 173 FIX: LLM enforcer returns 'content' not 'response'
                    response = ai_result.get('content', '') or ai_result.get('response', '')
                    logger.info(f"✅ Returning {len(ai_result['tool_calls'])} tool_calls to frontend for execution")

                    # Return dict with both response and tool_calls
                    return {
                        'text': response,
                        'tool_calls': ai_result['tool_calls']
                    }
                else:
                    # No tool calls, just return the text response
                    # Session 173 FIX: LLM enforcer returns 'content' not 'response'
                    response = ai_result.get('content', '') or ai_result.get('response', '')
                    logger.info(f"✅ Generated REAL AI response for {self.user.username}")
                    return response
            else:
                # Fallback if AI fails
                logger.warning(f"⚠️ AI generation failed, using intelligent fallback")
                return self._generate_intelligent_fallback(message, context)

        except Exception as e:
            import traceback
            logger.error(f"❌ LLM ERROR: {e}")
            logger.debug(f"Full traceback:\n{traceback.format_exc()}")
            logger.warning(f"⚠️ LLM not available (likely no API keys configured): {e}")
            logger.info("📋 Using intelligent fallback response with conversation context")
            return self._generate_intelligent_fallback(message, context)

    def _generate_intelligent_fallback(self, message: str, context: Dict[str, Any]) -> str:
        """
        Generate an intelligent fallback response when AI is unavailable.
        Uses context and patterns to create relevant response.
        """
        # Extract user context properly
        user_context = context.get('user_context', {})
        user_name = user_context.get('first_name') or context.get('first_name', 'there')
        conversation_context = context.get('conversation_context', '')

        # Analyze message for key topics
        message_lower = message.lower()

        # Profile-related responses
        if any(word in message_lower for word in ['profile', 'professional', 'setup', 'setting up']):
            if 'professional' in message_lower:
                if any(word in message_lower for word in ['feeling out', 'exploring', 'looking at', 'checking out']):
                    return f"Hi {user_name}! I understand you're exploring the Professional profile section to see what options are available. The Professional profile typically includes advanced fields like core competencies, quarterly objectives, delegation preferences, and detailed work schedules. Would you like me to walk you through what each section does, or do you have specific areas you'd like to understand better?"
                else:
                    return f"Hi {user_name}! I can help you set up your Professional profile. This includes defining your primary role, core competencies, communication style, long-term goals, and work preferences. What aspect would you like to start with?"

        # Check for system commands
        if 'status' in message_lower:
            status = self.get_system_status()
            return f"Hi {user_name}! System is {status.get('platform', {}).get('operational_percentage', 0):.0f}% operational with {status.get('embeddings', {}).get('total_count', 0)} embeddings and {status.get('agents', {}).get('total_registered', 0)} agents ready."

        if 'help' in message_lower:
            return f"Hi {user_name}! I can help you with job searches, profile management, agent execution, and system queries. What would you like to explore?"

        if 'agent' in message_lower:
            return f"Hi {user_name}! I have access to {len(get_agent_registry().list_agents())} specialized agents. Would you like me to list them or execute a specific one?"

        # Context-aware responses
        if conversation_context and 'profile' in conversation_context.lower():
            return f"Hi {user_name}! Continuing our discussion about profiles - what specific aspect would you like to explore or set up next?"

        # Default personalized response
        recent_project = self.enhanced_profile.current_projects[0] if self.enhanced_profile.current_projects else None
        if recent_project:
            return f"Hi {user_name}! I see you're working on {recent_project}. How can I assist you with that today?"
        else:
            return f"Hello {user_name}! I'm here to help with your goals. What would you like to work on?"

    def _generate_response(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Override parent's template-based response with real AI.

        Args:
            message: User's message
            context: Context dictionary

        Returns:
            Response dictionary with AI-generated content
        """
        logger.debug("_generate_response() ENTERED, calling _generate_ai_response()")
        # Generate real AI response
        ai_response = self._generate_ai_response(message, context)
        logger.debug(f"_generate_ai_response() returned type={type(ai_response)}")

        # Session 155 Fix: Handle dict response with tool_calls
        if isinstance(ai_response, dict) and 'tool_calls' in ai_response:
            # GPT requested tool calls - return them to frontend
            response_text = ai_response.get('text', '')
            raw_tool_calls = ai_response['tool_calls']

            # Transform Responses API format to frontend-expected format
            # Responses API: {function: {name, arguments}}
            # Frontend expects: {name, arguments} where arguments is a dict
            tool_calls = []
            for tool_call in raw_tool_calls:
                if 'function' in tool_call:
                    # Flatten the structure and parse arguments JSON string
                    arguments_str = tool_call['function']['arguments']
                    try:
                        # Parse JSON string to dict
                        arguments_dict = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
                    except json.JSONDecodeError:
                        logger.warning(f"⚠️ Could not parse arguments JSON: {arguments_str}")
                        arguments_dict = {}

                    tool_calls.append({
                        'name': tool_call['function']['name'],
                        'arguments': arguments_dict
                    })
                else:
                    # Already in correct format
                    tool_calls.append(tool_call)

            logger.info(f"🔧 Passing {len(tool_calls)} tool_calls to frontend (flattened format)")

            response_data = {
                'response': response_text,
                'tool_calls': tool_calls,
                'suggestions': self.generate_personalized_suggestions(message),
                'actions': [],  # No actions when tools are being called
                'confidence': 0.95,  # High confidence for tool execution
                'ai_generated': True,
                'model': 'gpt-5-mini'
            }
            return response_data

        # No tool calls - regular text response
        response_text = ai_response if isinstance(ai_response, str) else str(ai_response)

        # Determine intent for suggestions
        intent = context.get('intent', 'general')

        # Generate smart suggestions based on context and AI response
        suggestions = self.generate_personalized_suggestions(message)

        # Determine confidence based on whether we used real AI or fallback
        confidence = 0.9 if 'Generated REAL AI response' in str(logger) else 0.6

        # Build response dictionary
        response_data = {
            'response': response_text,
            'suggestions': suggestions,
            'actions': self._extract_actions_from_response(response_text),
            'confidence': confidence,
            'ai_generated': True,  # Flag to indicate real AI was used
            'model': 'gpt-5-mini' if self.llm_enforcer.openai_client else 'intelligent-fallback'
        }

        return response_data

    def _extract_actions_from_response(self, response: str) -> List[str]:
        """
        Extract potential actions from AI response.

        Args:
            response: AI-generated response

        Returns:
            List of action identifiers
        """
        actions = []
        response_lower = response.lower()

        # Map keywords to actions
        action_map = {
            'search': ['search_jobs', 'search_embeddings'],
            'agent': ['list_agents', 'execute_agent'],
            'profile': ['edit_profile', 'view_profile'],
            'job': ['search_jobs', 'view_applications'],
            'status': ['system_status', 'check_health'],
            'help': ['show_help_menu']
        }

        for keyword, action_list in action_map.items():
            if keyword in response_lower:
                actions.extend(action_list)

        return list(set(actions))[:5]  # Return unique actions, max 5

    def process_system_command(self, command: str) -> Dict[str, Any]:
        """
        Process system-level commands from the assistant.

        Args:
            command: System command to process

        Returns:
            Command execution results
        """
        command_lower = command.lower()

        # Database status command
        if 'database' in command_lower or 'embeddings count' in command_lower:
            status = self.get_system_status()
            return {
                'type': 'system_status',
                'embeddings': status.get('embeddings'),
                'database_health': status.get('platform', {}).get('health'),
                'response': f"Database contains {status.get('embeddings', {}).get('total_count', 0)} embeddings. "
                           f"Platform is {status.get('platform', {}).get('operational_percentage', 0):.0f}% operational."
            }

        # Search embeddings command
        elif 'search' in command_lower and 'embedding' in command_lower:
            # Extract search term (simple extraction)
            search_term = command.replace('search embeddings', '').replace('search embedding', '').strip()
            if search_term:
                results = self.search_embeddings(search_term, limit=3)
                return {
                    'type': 'search_results',
                    'query': search_term,
                    'count': len(results),
                    'results': results,
                    'response': f"Found {len(results)} embeddings matching '{search_term}'"
                }

        # WebSocket status
        elif 'websocket' in command_lower:
            status = self.get_system_status()
            ws_status = status.get('websockets', {})
            return {
                'type': 'websocket_status',
                'status': ws_status,
                'response': f"WebSocket hub is {'active' if ws_status.get('active') else 'inactive'}. "
                           f"Active connections: {ws_status.get('connections', 0)}"
            }

        # Agent list command
        elif 'list agents' in command_lower:
            agent_registry = get_agent_registry()
            agents = agent_registry.list_agents()[:10]  # First 10 agents
            return {
                'type': 'agent_list',
                'total_agents': len(agent_registry.list_agents()),
                'sample_agents': [a.get('name') for a in agents],
                'response': f"System has {len(agent_registry.list_agents())} registered agents. "
                           f"Sample: {', '.join([a.get('name') for a in agents[:5]])}"
            }

        # Execute agent command
        elif 'execute agent' in command_lower or 'run agent' in command_lower:
            # Simple parsing - in production this would be more sophisticated
            parts = command.split(' ')
            if len(parts) > 2:
                agent_name = parts[2] if 'agent' in parts else parts[1]
                task = ' '.join(parts[3:]) if len(parts) > 3 else 'default task'
                result = self.execute_agent(agent_name, task)
                return {
                    'type': 'agent_execution',
                    'result': result,
                    'response': result.get('message', 'Agent execution completed')
                }

        return {
            'type': 'unknown_command',
            'response': "I can help with database queries, embeddings search, system status, and agent execution. "
                       "Try: 'check database status', 'search embeddings [term]', 'list agents', or 'execute agent [name] [task]'"
        }

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

        # Merge profile context with provided context
        full_context = {
            'user_profile': profile_context,
            'user_role': self.enhanced_profile.primary_role or 'User',
            'communication_style': self.enhanced_profile.communication_style or 'balanced',
            'learning_style': self.enhanced_profile.learning_style or 'mixed',
            'goals': self.enhanced_profile.long_term_goals,
            'current_projects': self.enhanced_profile.current_projects,
            'skills': {'top_skills': list(self.enhanced_profile.core_competencies.keys())[:5] if self.enhanced_profile.core_competencies else []},
            'timezone': self.enhanced_profile.time_zone,
            'work_hours': self.enhanced_profile.work_schedule,
            'decision_framework': self.enhanced_profile.decision_framework,
            'conversation_history': conversation_context,
            'personalization_context': personalized_context,
            'user_patterns': user_patterns
        }

        if context:
            full_context.update(context)

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
                from agents.video_agent import get_video_agent
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
                from ai_core.agents.editing_orchestrator_agent import EditingOrchestratorAgent
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
        system_keywords = ['database', 'embedding', 'system', 'status', 'websocket', 'query']

        if any(keyword in message.lower() for keyword in system_keywords):
            # Process as system command
            system_result = self.process_system_command(message)

            # Use AI generation instead of parent's template response
            response_data = self._generate_response(message, full_context)

            # Enhanced response with system data
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

    def get_enhanced_context(self) -> Dict[str, Any]:
        """
        Get enhanced context with system status and profile data.

        Returns:
            Enhanced context dictionary
        """
        # Get base context
        context = self.get_personalized_context()

        # Add system status
        system_status = self.get_system_status()
        context['system'] = {
            'database_healthy': system_status.get('platform', {}).get('health') == 'healthy',
            'total_embeddings': system_status.get('embeddings', {}).get('total_count', 0),
            'total_agents': system_status.get('agents', {}).get('total_registered', 0),
            'websocket_active': system_status.get('websockets', {}).get('active', False),
            'operational_percentage': system_status.get('platform', {}).get('operational_percentage', 0)
        }

        # Add recent database queries
        context['system']['recent_queries'] = len(self.database_queries_executed)

        # Add enhanced profile context
        if hasattr(self, 'enhanced_profile'):
            context['enhanced_profile'] = self.enhanced_profile.get_context_for_ai('general')

        return context

    def store_memory(self, memory_type: str, content: str, **kwargs) -> UserMemoryContext:
        """
        Store a memory using UnifiedMemoryManager.

        Args:
            memory_type: Type of memory (decision, preference, etc.)
            content: Content of the memory
            **kwargs: Additional metadata

        Returns:
            Created UserMemoryContext instance
        """
        memory = self.memory_manager.store_memory(
            user=self.user,
            source='assistant',
            memory_type=memory_type,
            content=content,
            importance=kwargs.get('importance', 5),
            related_project=kwargs.get('related_project', ''),
            related_goal=kwargs.get('related_goal', ''),
            tags=kwargs.get('tags', []),
            metadata=kwargs.get('metadata', {})
        )
        logger.info(f"Stored {memory_type} memory via UnifiedMemoryManager for {self.user.username}: {content[:50]}...")
        return memory

    def retrieve_memories(self, memory_type: str = None, limit: int = 10) -> List[UserMemoryContext]:
        """
        Retrieve user memories.

        Args:
            memory_type: Filter by memory type (optional)
            limit: Maximum number of memories to retrieve

        Returns:
            List of UserMemoryContext instances
        """
        query = UserMemoryContext.objects.filter(user=self.user)

        if memory_type:
            query = query.filter(memory_type=memory_type)

        memories = query[:limit]

        # Update access counts
        for memory in memories:
            memory.accessed_count += 1
            memory.last_accessed = timezone.now()
            memory.save(update_fields=['accessed_count', 'last_accessed'])

        return list(memories)

    def update_profile_from_interaction(self, message: str, response: str):
        """
        Enhanced profile update with intelligent pattern extraction and learning.

        Args:
            message: User's message
            response: Assistant's response
        """
        message_lower = message.lower()
        updates_made = []

        # Detect and store preferences
        if 'prefer' in message_lower or 'like' in message_lower or 'favorite' in message_lower:
            self.store_memory('preference', message, importance=7)
            updates_made.append('preference')

        # Detect goals
        if 'goal' in message_lower or 'want to' in message_lower or 'plan to' in message_lower:
            self.store_memory('goal', message, importance=8)
            updates_made.append('goal')

            # Extract and update long-term goals if mentioned
            if 'long term' in message_lower or 'future' in message_lower:
                goal_text = self.extract_goal_text(message)
                if goal_text and goal_text not in (self.enhanced_profile.long_term_goals or []):
                    if not self.enhanced_profile.long_term_goals:
                        self.enhanced_profile.long_term_goals = []
                    self.enhanced_profile.long_term_goals.append(goal_text)
                    self.enhanced_profile.save(update_fields=['long_term_goals'])
                    logger.info(f"Added long-term goal for {self.user.username}: {goal_text}")

        # Detect decisions
        if 'decide' in message_lower or 'choose' in message_lower or 'selected' in message_lower:
            self.store_memory('decision', message, importance=6)
            updates_made.append('decision')

        # Extract skills mentioned
        skill_keywords = ['know', 'can', 'skilled in', 'experience with', 'worked with', 'expert in']
        if any(keyword in message_lower for keyword in skill_keywords):
            skills = self.extract_skills(message)
            if skills:
                current_skills = self.enhanced_profile.core_competencies or {}
                for skill in skills:
                    if skill not in current_skills:
                        # Add with default proficiency level 5
                        current_skills[skill] = 5
                if len(current_skills) > len(self.enhanced_profile.core_competencies or {}):
                    self.enhanced_profile.core_competencies = current_skills
                    self.enhanced_profile.save(update_fields=['core_competencies'])
                    new_skills = [s for s in skills if s not in (self.enhanced_profile.core_competencies or {})]
                    self.store_memory('skill', f"Identified skills: {', '.join(skills)}", importance=6)
                    logger.info(f"Added skills for {self.user.username}: {skills}")

        # Extract project mentions
        project_keywords = ['working on', 'project', 'building', 'developing', 'creating']
        if any(keyword in message_lower for keyword in project_keywords):
            projects = self.extract_projects(message)
            if projects:
                current_projects = self.enhanced_profile.current_projects or []
                new_projects = [p for p in projects if p not in current_projects]
                if new_projects:
                    self.enhanced_profile.current_projects = current_projects + new_projects
                    self.enhanced_profile.save(update_fields=['current_projects'])
                    self.store_memory('project', f"Working on: {', '.join(new_projects)}", importance=7)
                    logger.info(f"Added projects for {self.user.username}: {new_projects}")

        # Detect communication style patterns
        if self.enhanced_profile.interaction_count > 5:
            # After 5 interactions, start detecting patterns
            self.detect_communication_patterns(message)

        # Track profile access
        if hasattr(self, 'enhanced_profile'):
            self.enhanced_profile.interaction_count += 1
            self.enhanced_profile.save(update_fields=['interaction_count'])

        # Store summary of what was learned
        if updates_made:
            self.store_memory(
                'learning',
                f"Learned about: {', '.join(updates_made)}",
                importance=5,
                metadata={'message': message[:200], 'categories': updates_made}
            )

    def generate_personalized_suggestions(self, message: str) -> List[str]:
        """
        Generate personalized suggestions based on user profile and message context.

        Args:
            message: User's message

        Returns:
            List of personalized suggestions
        """
        suggestions = []

        # Base suggestions on user's primary role
        if self.enhanced_profile.primary_role:
            if 'engineer' in self.enhanced_profile.primary_role.lower():
                suggestions.extend(['Review code', 'Check system status', 'Run tests'])
            elif 'manager' in self.enhanced_profile.primary_role.lower():
                suggestions.extend(['Review team progress', 'Check project status', 'Schedule meeting'])
            elif 'designer' in self.enhanced_profile.primary_role.lower():
                suggestions.extend(['Review designs', 'Check feedback', 'Update portfolio'])

        # Add suggestions based on current projects
        if self.enhanced_profile.current_projects:
            for project in self.enhanced_profile.current_projects[:2]:
                suggestions.append(f"Update on {project}")

        # Add goal-based suggestions
        if self.enhanced_profile.long_term_goals:
            suggestions.append('Review goal progress')

        # Default suggestions if none generated
        if not suggestions:
            suggestions = ['Tell me more', 'Show options', 'Help me decide', 'What else?']

        return suggestions[:5]  # Limit to 5 suggestions

    def get_detailed_explanation(self, message: str) -> str:
        """
        Generate detailed explanation for users who prefer detailed communication.

        Args:
            message: User's message

        Returns:
            Detailed explanation string
        """
        explanations = []

        # Add context about the message type
        if 'how' in message.lower():
            explanations.append("This appears to be a how-to question. I'll provide step-by-step guidance.")
        elif 'why' in message.lower():
            explanations.append("This is a reasoning question. I'll explain the underlying concepts.")
        elif 'what' in message.lower():
            explanations.append("This is a definitional question. I'll provide clear explanations.")

        # Add profile-based context
        if self.enhanced_profile.learning_style == 'visual':
            explanations.append("Based on your visual learning style, I'll try to paint a clear picture.")
        elif self.enhanced_profile.learning_style == 'hands-on':
            explanations.append("Given your hands-on learning preference, I'll include practical examples.")

        return ' '.join(explanations) if explanations else ''

    def make_concise(self, response: str, max_length: int = 200) -> str:
        """
        Make response more concise for users who prefer brief communication.

        Args:
            response: Original response
            max_length: Maximum length for concise response

        Returns:
            Concise version of the response
        """
        if len(response) <= max_length:
            return response

        # Try to cut at sentence boundary
        sentences = response.split('. ')
        concise = []
        current_length = 0

        for sentence in sentences:
            if current_length + len(sentence) <= max_length:
                concise.append(sentence)
                current_length += len(sentence) + 2  # +2 for '. '
            else:
                break

        result = '. '.join(concise)
        if result and not result.endswith('.'):
            result += '.'

        return result if result else response[:max_length] + '...'

    def extract_goal_text(self, message: str) -> Optional[str]:
        """
        Extract goal text from user message.

        Args:
            message: User's message containing goal

        Returns:
            Extracted goal text or None
        """
        # Simple extraction - in production this would use NLP
        goal_phrases = ['want to', 'goal is to', 'plan to', 'aiming to', 'hoping to']

        for phrase in goal_phrases:
            if phrase in message.lower():
                start = message.lower().index(phrase) + len(phrase)
                # Extract up to next punctuation or end
                end = len(message)
                for punct in ['.', '!', '?', ',', ';']:
                    if punct in message[start:]:
                        end = start + message[start:].index(punct)
                        break

                goal = message[start:end].strip()
                # Clean up common words
                goal = goal.replace(' to ', ' ').replace(' the ', ' ')
                return goal[:100]  # Limit length

        return None

    def extract_skills(self, message: str) -> List[str]:
        """
        Extract skills mentioned in user message.

        Args:
            message: User's message

        Returns:
            List of extracted skills
        """
        skills = []

        # Common skill patterns
        skill_patterns = [
            'know ', 'skilled in ', 'experience with ', 'worked with ',
            'expert in ', 'familiar with ', 'proficient in '
        ]

        message_lower = message.lower()
        for pattern in skill_patterns:
            if pattern in message_lower:
                start = message_lower.index(pattern) + len(pattern)
                # Extract word or phrase after pattern
                words = message[start:].split()
                if words:
                    # Take up to 3 words as skill
                    skill = ' '.join(words[:3]).strip('.,!?;')
                    if len(skill) > 2:  # Minimum skill length
                        skills.append(skill)

        # Common tech skills mentioned directly
        tech_skills = ['Python', 'JavaScript', 'React', 'Django', 'SQL', 'Docker',
                      'AWS', 'Machine Learning', 'AI', 'DevOps', 'Kubernetes']

        for skill in tech_skills:
            if skill.lower() in message_lower and skill not in skills:
                skills.append(skill)

        return skills[:10]  # Limit to 10 skills

    def extract_projects(self, message: str) -> List[str]:
        """
        Extract project names or descriptions from message.

        Args:
            message: User's message

        Returns:
            List of project names/descriptions
        """
        projects = []

        # Project indicators
        project_patterns = [
            'working on ', 'building ', 'developing ', 'creating ',
            'project called ', 'project named '
        ]

        message_lower = message.lower()
        for pattern in project_patterns:
            if pattern in message_lower:
                start = message_lower.index(pattern) + len(pattern)
                # Extract following words
                words = message[start:].split()
                if words:
                    # Take up to 5 words as project description
                    project = ' '.join(words[:5]).strip('.,!?;')
                    if len(project) > 2:
                        projects.append(project)

        return projects[:5]  # Limit to 5 projects

    def detect_communication_patterns(self, message: str):
        """
        Detect and update communication style patterns.

        Args:
            message: User's message
        """
        # Analyze message length patterns
        recent_memories = self.retrieve_memories('interaction', limit=10)

        if len(recent_memories) >= 5:
            avg_length = sum(len(m.content) for m in recent_memories) / len(recent_memories)

            # Detect communication style
            if avg_length < 50:
                new_style = 'concise'
            elif avg_length > 200:
                new_style = 'detailed'
            else:
                new_style = 'balanced'

            # Update if different from current
            if self.enhanced_profile.communication_style != new_style:
                self.enhanced_profile.communication_style = new_style
                self.enhanced_profile.save(update_fields=['communication_style'])
                self.store_memory(
                    'pattern',
                    f"Communication style updated to: {new_style}",
                    importance=6
                )
                logger.info(f"Updated communication style for {self.user.username}: {new_style}")

        # Detect question patterns
        if '?' in message:
            # User asks questions - might prefer interactive style
            question_count = sum(1 for m in recent_memories if '?' in m.content)
            if question_count > len(recent_memories) * 0.7:  # 70% questions
                if self.enhanced_profile.learning_style != 'interactive':
                    self.enhanced_profile.learning_style = 'interactive'
                    self.enhanced_profile.save(update_fields=['learning_style'])
                    logger.info(f"Detected interactive learning style for {self.user.username}")

    def _store_conversation(self, message: str, response_data: Dict[str, Any]) -> None:
        """
        Store conversation in database for persistence and future retrieval.

        Args:
            message: User's message
            response_data: Assistant's response data
        """
        try:
            from core.models import ConversationMemory, ChatConversation
            import uuid

            # Store in ConversationMemory for learning
            ConversationMemory.objects.create(
                user=self.user,
                message=message,
                response=response_data.get('response', ''),
                agents_used=response_data.get('agents_used', []),
                intent=response_data.get('intent', 'general'),
                success=True
            )

            # Store in ChatConversation for detailed tracking
            ChatConversation.objects.create(
                user=self.user,
                conversation_id=str(uuid.uuid4()),
                user_message=message,
                assistant_response=response_data.get('response', ''),
                context_used=response_data.get('context', {}),
                metadata={
                    'confidence': response_data.get('confidence', 0.5),
                    'ai_generated': response_data.get('ai_generated', False),
                    'model': response_data.get('model', 'unknown'),
                    'actions': response_data.get('actions', []),
                    'suggestions': response_data.get('suggestions', [])
                },
                response_time_ms=response_data.get('response_time_ms', 0)
            )

            # Create embedding for the conversation
            self._create_conversation_embedding(message, response_data.get('response', ''))

            logger.info(f"💾 Stored conversation for {self.user.username}: {message[:50]}...")

        except Exception as e:
            logger.error(f"Error storing conversation: {e}")

    def _create_conversation_embedding(self, message: str, response: str) -> None:
        """
        Create embedding for conversation to enable semantic search.

        Args:
            message: User's message
            response: Assistant's response
        """
        try:
            from core.models import UserEmbedding

            # Combine message and response for comprehensive context
            combined_text = f"User: {message}\nAssistant: {response}"

            # Use memory manager to create embedding
            self.memory_manager.store_memory(
                'conversation',
                combined_text,
                metadata={
                    'message': message,
                    'response': response,
                    'timestamp': datetime.now().isoformat()
                }
            )

            # Also create direct UserEmbedding for compatibility
            UserEmbedding.objects.create(
                user=self.user,
                content=combined_text,
                content_type='conversation',
                source='personal_assistant',
                metadata={
                    'message_length': len(message),
                    'response_length': len(response),
                    'conversation_type': 'interactive'
                }
            )

            logger.info(f"🧠 Created conversation embedding for {self.user.username}")

        except Exception as e:
            logger.error(f"Error creating conversation embedding: {e}")

    def _load_conversation_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Load recent conversation history from database.

        Args:
            limit: Maximum number of conversations to load

        Returns:
            List of conversation dictionaries
        """
        try:
            from core.models import ConversationMemory

            conversations = ConversationMemory.objects.filter(
                user=self.user
            ).order_by('-created_at')[:limit]

            return [
                {
                    'message': conv.message,
                    'response': conv.response,
                    'timestamp': conv.created_at.isoformat(),
                    'intent': conv.intent
                }
                for conv in conversations
            ]

        except Exception as e:
            logger.error(f"Error loading conversation history: {e}")
            return []

    def _get_project_brief_context(self) -> str:
        """
        Session 181: Build comprehensive project brief for AI context.

        Provides the AI Assistant with full project information including:
        - Project name and status
        - Goal and description (the creative brief)
        - Category and tags for style guidance
        - Color palette preferences

        This allows the AI to generate content that aligns with the project's
        vision without requiring the user to repeat the brief each time.

        Returns:
            Formatted project brief string, or empty string if no active project.
        """
        try:
            project = getattr(self, 'project', None)
            if not project:
                return ""

            lines = []
            lines.append(f"📁 **Active Project: {project.name}**")
            lines.append(f"   Status: {project.get_status_display()}")

            # Goal is the most important - the creative brief
            if project.goal:
                lines.append(f"   🎯 Goal: {project.goal}")

            # Description provides additional context
            if project.description:
                lines.append(f"   📝 Description: {project.description}")

            # Category helps with style decisions
            if project.category:
                lines.append(f"   📂 Category: {project.category}")

            # Color palette is critical for visual consistency
            if project.colors:
                lines.append(f"   🎨 Color Palette: {project.colors}")

            # Tags provide style keywords
            if project.tags and len(project.tags) > 0:
                lines.append(f"   🏷️ Style Tags: {', '.join(project.tags)}")

            # Add guidance for AI
            lines.append("")
            lines.append("**IMPORTANT - Project Brief Integration (Session 181):**")
            lines.append("- Use the Goal and Description above as your creative brief")
            lines.append("- Match the Color Palette when generating visual content")
            lines.append("- Incorporate Style Tags into image/video generation prompts")
            lines.append("- Maintain consistency with the project's Category aesthetic")
            lines.append("- If user's request is vague, infer style from project context")

            return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error building project brief context: {e}")
            return ""

    def _get_style_preferences_context(self) -> str:
        """
        Session 169 Phase 3 + Session 179 Enhancement:
        Get user's learned style preferences for personalized generation.

        Session 179: Now also includes semantic style context from embeddings
        when available, enabling more sophisticated preference matching.

        Returns:
            Formatted string of style preferences, or empty string if no preferences.
        """
        try:
            from style_memory.models import StyleMemory, StylePattern

            # Get interaction counts
            total_interactions = StyleMemory.objects.filter(user=self.user).count()
            if total_interactions == 0:
                return ""

            loved_count = StyleMemory.objects.filter(user=self.user, interaction_type='love').count()
            liked_count = StyleMemory.objects.filter(user=self.user, interaction_type='like').count()
            disliked_count = StyleMemory.objects.filter(user=self.user, interaction_type='dislike').count()

            # Get detected patterns
            patterns = StylePattern.objects.filter(user=self.user).order_by('-confidence', '-frequency')[:10]

            if not patterns.exists() and total_interactions < 3:
                return ""  # Not enough data yet

            # Build the preferences context
            lines = [f"Style Learning (based on {total_interactions} ratings: {loved_count} loved, {liked_count} liked, {disliked_count} disliked):"]

            if patterns.exists():
                pattern_groups = {}
                for p in patterns:
                    if p.pattern_type not in pattern_groups:
                        pattern_groups[p.pattern_type] = []
                    pattern_groups[p.pattern_type].append(p.pattern_value)

                for ptype, values in pattern_groups.items():
                    lines.append(f"- Preferred {ptype}: {', '.join(values[:3])}")

            # Session 179: Try to add semantic context from embeddings
            try:
                from style_memory.embedding_bridge import get_style_context_for_user
                # Get the current prompt/context for semantic matching
                current_context = getattr(self, '_current_prompt', '')
                if current_context:
                    semantic_context = get_style_context_for_user(self.user, current_context)
                    if semantic_context:
                        lines.append("\nSemantic style match:")
                        lines.append(semantic_context)
            except Exception as embed_err:
                # Embeddings not available or not populated - that's fine
                logger.debug(f"Semantic style context not available: {embed_err}")

            return "\n".join(lines)

        except Exception as e:
            logger.debug(f"Error getting style preferences: {e}")
            return ""

    def _format_conversation_context(self, conversations: List[Dict[str, Any]]) -> str:
        """
        Format conversation history into context string.

        Args:
            conversations: List of conversation dictionaries

        Returns:
            Formatted conversation context string
        """
        if not conversations:
            return ""

        context_parts = ["Recent conversation history:"]

        # Reverse to show oldest first (chronological order)
        for conv in reversed(conversations):
            context_parts.append(f"User: {conv['message']}")
            context_parts.append(f"Assistant: {conv['response'][:100]}...")
            context_parts.append("")  # Empty line for readability

        return "\n".join(context_parts)

    def _analyze_user_patterns(self) -> Dict[str, Any]:
        """
        Analyze user conversation patterns and preferences.

        Returns:
            Dictionary containing user patterns and preferences
        """
        try:
            from core.models import ConversationMemory, UserProfile
            from collections import Counter
            import json

            # Get user conversations
            conversations = ConversationMemory.objects.filter(
                user=self.user
            ).order_by('-created_at')[:50]  # Last 50 conversations

            if not conversations:
                return {}

            # Analyze conversation patterns
            intents = [conv.intent for conv in conversations if conv.intent]
            agents_used = []
            for conv in conversations:
                if conv.agents_used:
                    if isinstance(conv.agents_used, str):
                        try:
                            agents_used.extend(json.loads(conv.agents_used))
                        except:
                            pass
                    elif isinstance(conv.agents_used, list):
                        agents_used.extend(conv.agents_used)

            # Get user profile if exists
            user_profile = None
            try:
                user_profile = UserProfile.objects.get(user=self.user)
            except UserProfile.DoesNotExist:
                pass

            patterns = {
                'conversation_count': len(conversations),
                'common_intents': dict(Counter(intents).most_common(5)),
                'preferred_agents': dict(Counter(agents_used).most_common(5)),
                'interaction_frequency': self._calculate_interaction_frequency(conversations),
                'user_profile': {
                    'skills': user_profile.skills if user_profile and user_profile.skills else [],
                    'current_role': user_profile.current_role if user_profile and user_profile.current_role else '',
                    'occupation': user_profile.occupation if user_profile and user_profile.occupation else '',
                    'industries': user_profile.industries if user_profile and user_profile.industries else [],
                    'remote_only': user_profile.remote_only if user_profile else False,
                    'preferred_ai_model': user_profile.preferred_ai_model if user_profile and user_profile.preferred_ai_model else '',
                } if user_profile else {}
            }

            return patterns

        except Exception as e:
            logger.error(f"Error analyzing user patterns: {e}")
            return {}

    def _calculate_interaction_frequency(self, conversations) -> str:
        """Calculate user interaction frequency."""
        if len(conversations) < 2:
            return "new_user"

        from datetime import datetime, timedelta

        now = timezone.now()
        recent_conversations = [
            conv for conv in conversations
            if (now - conv.created_at.replace(tzinfo=None)) <= timedelta(days=7)
        ]

        weekly_count = len(recent_conversations)

        if weekly_count >= 20:
            return "very_active"
        elif weekly_count >= 10:
            return "active"
        elif weekly_count >= 3:
            return "regular"
        else:
            return "occasional"

    def _create_personalized_context(self, message: str, patterns: Dict[str, Any]) -> str:
        """
        Create personalized context based on user patterns and current message.

        Args:
            message: Current user message
            patterns: User patterns from analysis

        Returns:
            Personalized context string
        """
        context_parts = []

        # User interaction profile
        frequency = patterns.get('interaction_frequency', 'new_user')
        conv_count = patterns.get('conversation_count', 0)

        if frequency == "very_active":
            context_parts.append("🔥 Very active user - provide detailed, advanced responses")
        elif frequency == "active":
            context_parts.append("⚡ Active user - can handle comprehensive information")
        elif frequency == "regular":
            context_parts.append("👤 Regular user - balance detail with clarity")
        else:
            context_parts.append("🌟 Welcome! Provide clear, helpful introductory responses")

        # User preferences and skills
        user_profile = patterns.get('user_profile', {})
        if user_profile.get('skills'):
            skills_text = ", ".join(user_profile['skills'][:3])
            context_parts.append(f"💼 User skills: {skills_text}")

        if user_profile.get('goals'):
            goals_text = ", ".join(user_profile['goals'][:2])
            context_parts.append(f"🎯 User goals: {goals_text}")

        # Common intents
        common_intents = patterns.get('common_intents', {})
        if common_intents:
            top_intent = next(iter(common_intents.keys()))
            context_parts.append(f"🧠 User typically asks about: {top_intent}")

        # Preferred agents
        preferred_agents = patterns.get('preferred_agents', {})
        if preferred_agents:
            top_agents = list(preferred_agents.keys())[:2]
            context_parts.append(f"🤖 Often uses: {', '.join(top_agents)}")

        # Message intent analysis
        message_lower = message.lower()
        if any(word in message_lower for word in ['urgent', 'asap', 'quickly', 'fast']):
            context_parts.append("⚡ URGENT REQUEST - Prioritize speed and direct answers")
        elif any(word in message_lower for word in ['explain', 'how', 'why', 'understand']):
            context_parts.append("📚 LEARNING REQUEST - Provide educational, detailed responses")
        elif any(word in message_lower for word in ['help', 'stuck', 'problem', 'issue']):
            context_parts.append("🆘 HELP REQUEST - Focus on practical solutions")

        if context_parts:
            return "PERSONALIZATION CONTEXT:\n" + "\n".join(context_parts) + "\n\n"

        return ""

    def _enhance_response_with_memory(self, response: str, patterns: Dict[str, Any]) -> str:
        """
        Enhance response with memory-based personalization.

        Args:
            response: Original response
            patterns: User patterns

        Returns:
            Enhanced response
        """
        try:
            # Add memory-based enhancements
            enhancements = []

            # Reference past interactions if relevant
            conv_count = patterns.get('conversation_count', 0)
            if conv_count > 5:
                frequency = patterns.get('interaction_frequency', 'new_user')
                if frequency in ['active', 'very_active']:
                    enhancements.append("Based on our previous conversations")

            # Suggest relevant agents based on past usage
            preferred_agents = patterns.get('preferred_agents', {})
            if preferred_agents and len(preferred_agents) > 0:
                top_agent = next(iter(preferred_agents.keys()))
                if 'opportunity' in response.lower() or 'job' in response.lower():
                    enhancements.append(f"You might also want to try the {top_agent} agent")

            # Add goal-oriented suggestions
            user_goals = patterns.get('user_profile', {}).get('goals', [])
            if user_goals and any(goal in response.lower() for goal in [g.lower() for g in user_goals]):
                enhancements.append("This aligns with your stated goals")

            # Enhance response if we have enhancements
            if enhancements:
                enhanced_parts = [response]
                enhanced_parts.append("\n💡 Personal Notes:")
                for enhancement in enhancements:
                    enhanced_parts.append(f"  • {enhancement}")

                return "\n".join(enhanced_parts)

            return response

        except Exception as e:
            logger.error(f"Error enhancing response with memory: {e}")
            return response

    # =====================================================
    # AGENT COMMUNICATION BRIDGE METHODS
    # =====================================================

    def route_to_agent(self, task: str, agent_type: str = None, required_capabilities: List[str] = None) -> Dict[str, Any]:
        """
        Route a task to the most appropriate agent.

        Args:
            task: Task description
            agent_type: Preferred agent type/specialization
            required_capabilities: Required agent capabilities

        Returns:
            Agent routing and execution results
        """
        try:
            # Find the best agent for the task
            best_agent = self.agent_registry.find_best_agent(
                task_description=task,
                required_capabilities=required_capabilities,
                preferred_specialization=agent_type
            )

            if not best_agent:
                return {
                    'success': False,
                    'error': 'No suitable agent found for this task',
                    'suggestions': self._suggest_alternative_agents(task)
                }

            # Execute the agent
            execution_id = self.agent_registry.execute_agent(
                agent_name=best_agent['name'],
                task_data={
                    'task': task,
                    'user_id': str(self.user.id),  # Convert to string for JSON serialization
                    'context': self._get_agent_context()
                }
            )

            if execution_id:
                # Store agent interaction as memory
                self.store_memory(
                    'agent_interaction',
                    f"Routed task to {best_agent['name']}: {task}",
                    importance=7,
                    metadata={
                        'agent_name': best_agent['name'],
                        'execution_id': execution_id,
                        'task': task
                    }
                )

                logger.info(f"🤖 Routed task to agent {best_agent['name']} for {self.user.username}")

                return {
                    'success': True,
                    'agent': best_agent,
                    'execution_id': execution_id,
                    'message': f"Task routed to {best_agent['display_name']} agent",
                    'status': 'initiated'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to execute agent',
                    'agent': best_agent
                }

        except Exception as e:
            logger.error(f"Error routing to agent: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_agent_response(self, agent_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get response from a specific agent.

        Args:
            agent_id: Agent identifier
            task_data: Task data to send to agent

        Returns:
            Agent response data
        """
        try:
            # Get agent details
            agent = self.agent_registry.get_agent(agent_id)
            if not agent:
                return {
                    'success': False,
                    'error': f'Agent {agent_id} not found'
                }

            # Execute agent with enhanced task data
            enhanced_task_data = {
                **task_data,
                'user_profile': self.enhanced_profile.get_context_for_ai('agent'),
                'user_preferences': {
                    'communication_style': self.enhanced_profile.communication_style,
                    'learning_style': self.enhanced_profile.learning_style
                },
                'context': self._get_agent_context()
            }

            execution_id = self.agent_registry.execute_agent(agent_id, enhanced_task_data)

            if execution_id:
                # Monitor execution status
                status = self.agent_registry.get_execution_status(execution_id)

                # Store interaction
                self.store_memory(
                    'agent_response',
                    f"Got response from {agent['name']}: {task_data.get('task', 'No task specified')}",
                    importance=6,
                    metadata={
                        'agent_id': agent_id,
                        'execution_id': execution_id,
                        'status': status
                    }
                )

                return {
                    'success': True,
                    'agent_id': agent_id,
                    'agent_name': agent['name'],
                    'execution_id': execution_id,
                    'status': status,
                    'response_available': status.get('status') == 'completed'
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to get agent response'
                }

        except Exception as e:
            logger.error(f"Error getting agent response: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def aggregate_agent_results(self, execution_ids: List[str]) -> Dict[str, Any]:
        """
        Aggregate results from multiple agent executions.

        Args:
            execution_ids: List of agent execution IDs

        Returns:
            Aggregated results from all agents
        """
        try:
            results = []
            successful_executions = 0
            failed_executions = 0

            for execution_id in execution_ids:
                status = self.agent_registry.get_execution_status(execution_id)
                if status:
                    results.append(status)
                    if status.get('status') == 'completed':
                        successful_executions += 1
                    elif status.get('status') == 'failed':
                        failed_executions += 1

            # Analyze results for patterns and insights
            insights = self._analyze_agent_results(results)

            # Store aggregated results as memory
            self.store_memory(
                'agent_aggregation',
                f"Aggregated results from {len(execution_ids)} agents",
                importance=8,
                metadata={
                    'execution_ids': execution_ids,
                    'successful_count': successful_executions,
                    'failed_count': failed_executions,
                    'insights': insights
                }
            )

            return {
                'success': True,
                'total_executions': len(execution_ids),
                'successful_executions': successful_executions,
                'failed_executions': failed_executions,
                'results': results,
                'insights': insights,
                'summary': f"Processed {len(execution_ids)} agent executions with {successful_executions} successes"
            }

        except Exception as e:
            logger.error(f"Error aggregating agent results: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def communicate_with_advisor(self, advisor_id: str, consultation_topic: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Initiate communication with an advisor.

        Args:
            advisor_id: Advisor identifier
            consultation_topic: Topic for consultation
            context: Additional context for the consultation

        Returns:
            Advisor consultation results
        """
        try:
            # Get advisor profile
            advisor = self.advisor_registry.get_advisor(advisor_id)
            if not advisor:
                return {
                    'success': False,
                    'error': f'Advisor {advisor_id} not found'
                }

            # Create consultation context
            consultation_context = {
                'user_profile': self.enhanced_profile.get_context_for_ai('advisor'),
                'goals': self.enhanced_profile.long_term_goals,
                'current_projects': self.enhanced_profile.current_projects,
                'skills': self.enhanced_profile.core_competencies,
                'recent_decisions': self._get_recent_decisions(),
                'consultation_history': self._get_advisor_history(advisor_id)
            }

            if context:
                consultation_context.update(context)

            # Request consultation
            consultation_id = self.advisor_registry.request_consultation(
                advisor_id=advisor_id,
                user_id=str(self.user.id),
                topic=consultation_topic,
                consultation_type='strategy',
                initial_request=json.dumps(consultation_context)
            )

            if consultation_id:
                # Store advisor interaction
                self.store_memory(
                    'advisor_consultation',
                    f"Consulted with {advisor.name} about: {consultation_topic}",
                    importance=9,
                    metadata={
                        'advisor_id': advisor_id,
                        'advisor_name': advisor.name,
                        'consultation_id': consultation_id,
                        'topic': consultation_topic,
                        'domain': advisor.domain.value
                    }
                )

                logger.info(f"🎓 Initiated consultation with advisor {advisor.name} for {self.user.username}")

                return {
                    'success': True,
                    'advisor': {
                        'id': advisor.id,
                        'name': advisor.name,
                        'title': advisor.title,
                        'domain': advisor.domain.value,
                        'expertise_level': advisor.expertise_level.value
                    },
                    'consultation_id': consultation_id,
                    'message': f"Consultation initiated with {advisor.name}",
                    'expected_response_time': f"{advisor.response_time_hours} hours"
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to initiate consultation'
                }

        except Exception as e:
            logger.error(f"Error communicating with advisor: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def find_relevant_advisors(self, topic: str, domain: str = None) -> List[Dict[str, Any]]:
        """
        Find advisors relevant to a specific topic or domain.

        Args:
            topic: Topic or question for consultation
            domain: Specific domain to filter by

        Returns:
            List of relevant advisor recommendations
        """
        try:
            from advisors.registry import AdvisorDomain

            # Convert string domain to enum if provided
            domain_enum = None
            if domain:
                try:
                    domain_enum = AdvisorDomain(domain.lower())
                except ValueError:
                    # Try to find matching domain
                    for d in AdvisorDomain:
                        if domain.lower() in d.value:
                            domain_enum = d
                            break

            # Get advisor recommendations
            recommendations = self.advisor_registry.get_advisor_recommendations(topic, {
                'user_profile': self.enhanced_profile.get_context_for_ai('advisor'),
                'domain': domain_enum
            })

            # Store search as memory
            self.store_memory(
                'advisor_search',
                f"Searched for advisors on topic: {topic}",
                importance=5,
                metadata={
                    'topic': topic,
                    'domain': domain,
                    'recommendations_count': len(recommendations.get('recommendations', []))
                }
            )

            return recommendations

        except Exception as e:
            logger.error(f"Error finding relevant advisors: {e}")
            return {
                'error': str(e),
                'recommendations': []
            }

    def execute_multi_agent_workflow(self, workflow_name: str, task: str) -> Dict[str, Any]:
        """
        Execute a workflow involving multiple agents working together.

        Args:
            workflow_name: Name of the workflow to execute
            task: Primary task description

        Returns:
            Workflow execution results
        """
        try:
            # Define workflow templates
            workflows = {
                'opportunity_analysis': [
                    {'agent_type': 'research', 'capabilities': ['web_search', 'data_analysis']},
                    {'agent_type': 'analysis', 'capabilities': ['financial_analysis', 'risk_assessment']},
                    {'agent_type': 'recommendation', 'capabilities': ['strategy', 'planning']}
                ],
                'skill_development': [
                    {'agent_type': 'assessment', 'capabilities': ['skill_analysis', 'gap_analysis']},
                    {'agent_type': 'planning', 'capabilities': ['learning_path', 'curriculum']},
                    {'agent_type': 'tracking', 'capabilities': ['progress_monitoring', 'feedback']}
                ],
                'job_application': [
                    {'agent_type': 'research', 'capabilities': ['job_search', 'company_research']},
                    {'agent_type': 'application', 'capabilities': ['resume_optimization', 'cover_letter']},
                    {'agent_type': 'follow_up', 'capabilities': ['communication', 'tracking']}
                ]
            }

            if workflow_name not in workflows:
                return {
                    'success': False,
                    'error': f'Unknown workflow: {workflow_name}',
                    'available_workflows': list(workflows.keys())
                }

            workflow_steps = workflows[workflow_name]
            execution_ids = []
            step_results = []

            # Execute each step in the workflow
            for i, step in enumerate(workflow_steps):
                # Find agent for this step
                best_agent = self.agent_registry.find_best_agent(
                    task_description=f"{task} - Step {i+1}",
                    required_capabilities=step['capabilities'],
                    preferred_specialization=step['agent_type']
                )

                if best_agent:
                    # Execute step
                    execution_id = self.agent_registry.execute_agent(
                        agent_name=best_agent['name'],
                        task_data={
                            'task': task,
                            'workflow_step': i + 1,
                            'step_description': step,
                            'previous_results': step_results,
                            'user_context': self._get_agent_context()
                        }
                    )

                    if execution_id:
                        execution_ids.append(execution_id)
                        step_results.append({
                            'step': i + 1,
                            'agent': best_agent['name'],
                            'execution_id': execution_id
                        })

            # Store workflow execution
            self.store_memory(
                'workflow_execution',
                f"Executed {workflow_name} workflow: {task}",
                importance=9,
                metadata={
                    'workflow_name': workflow_name,
                    'task': task,
                    'execution_ids': execution_ids,
                    'steps_completed': len(step_results)
                }
            )

            logger.info(f"🔄 Executed {workflow_name} workflow with {len(execution_ids)} agents for {self.user.username}")

            return {
                'success': True,
                'workflow_name': workflow_name,
                'task': task,
                'total_steps': len(workflow_steps),
                'execution_ids': execution_ids,
                'step_results': step_results,
                'message': f"Workflow '{workflow_name}' initiated with {len(execution_ids)} agents"
            }

        except Exception as e:
            logger.error(f"Error executing multi-agent workflow: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _suggest_alternative_agents(self, task: str) -> List[str]:
        """Suggest alternative agents when no exact match is found."""
        try:
            # Get all available agents
            all_agents = self.agent_registry.list_agents()

            # Simple keyword matching for suggestions
            task_keywords = task.lower().split()
            suggestions = []

            for agent in all_agents[:10]:  # Top 10 agents
                agent_keywords = (agent.get('name', '') + ' ' +
                                agent.get('description', '') + ' ' +
                                ' '.join(agent.get('capabilities', []))).lower()

                # Check for keyword overlap
                if any(keyword in agent_keywords for keyword in task_keywords):
                    suggestions.append(agent.get('name', 'Unknown'))

            return suggestions[:5]  # Top 5 suggestions

        except Exception as e:
            logger.error(f"Error suggesting alternative agents: {e}")
            return []

    def _get_agent_context(self) -> Dict[str, Any]:
        """Get context data for agent execution."""
        return {
            'user_id': str(self.user.id),  # Convert to string
            'user_role': self.enhanced_profile.primary_role or 'Not specified',
            'user_goals': self.enhanced_profile.long_term_goals or [],
            'user_skills': list(self.enhanced_profile.core_competencies.keys()) if self.enhanced_profile.core_competencies else [],
            'current_projects': self.enhanced_profile.current_projects or [],
            'communication_style': self.enhanced_profile.communication_style or 'balanced',
            'timezone': self.enhanced_profile.time_zone or 'UTC',
            'timestamp': datetime.now().isoformat()
        }

    def _analyze_agent_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze agent execution results for insights."""
        try:
            total_time = sum(r.get('execution_time_ms', 0) for r in results)
            avg_time = total_time / len(results) if results else 0

            successful_agents = [r for r in results if r.get('status') == 'completed']
            failed_agents = [r for r in results if r.get('status') == 'failed']

            return {
                'total_executions': len(results),
                'successful_count': len(successful_agents),
                'failed_count': len(failed_agents),
                'success_rate': len(successful_agents) / len(results) if results else 0,
                'average_execution_time_ms': avg_time,
                'fastest_agent': min(results, key=lambda x: x.get('execution_time_ms', float('inf')))['agent_name'] if results else None,
                'slowest_agent': max(results, key=lambda x: x.get('execution_time_ms', 0))['agent_name'] if results else None
            }

        except Exception as e:
            logger.error(f"Error analyzing agent results: {e}")
            return {}

    def _get_recent_decisions(self) -> List[Dict[str, Any]]:
        """Get recent user decisions for advisor context."""
        try:
            recent_decisions = self.retrieve_memories('decision', limit=5)
            return [
                {
                    'content': decision.content,
                    'timestamp': decision.created_at.isoformat(),
                    'importance': decision.importance
                }
                for decision in recent_decisions
            ]
        except Exception as e:
            logger.error(f"Error getting recent decisions: {e}")
            return []

    def _get_advisor_history(self, advisor_id: str) -> List[Dict[str, Any]]:
        """Get consultation history with specific advisor."""
        try:
            advisor_memories = self.retrieve_memories('advisor_consultation', limit=10)
            relevant_memories = [
                {
                    'content': memory.content,
                    'timestamp': memory.created_at.isoformat(),
                    'metadata': memory.metadata
                }
                for memory in advisor_memories
                if memory.metadata and memory.metadata.get('advisor_id') == advisor_id
            ]
            return relevant_memories
        except Exception as e:
            logger.error(f"Error getting advisor history: {e}")
            return []

    def _extract_task_from_message(self, message: str) -> str:
        """Extract the task description from a user message requesting agent execution."""
        try:
            message_lower = message.lower()

            # Common patterns for task extraction
            task_patterns = [
                r'can you have an agent (.+?)(?:\?|$)',
                r'execute agent.+?to (.+?)(?:\?|$)',
                r'run agent.+?to (.+?)(?:\?|$)',
                r'use agent.+?to (.+?)(?:\?|$)',
                r'deploy agent.+?to (.+?)(?:\?|$)',
                r'get an agent to (.+?)(?:\?|$)',
                r'agent analyze (.+?)(?:\?|$)',
                r'agent help.+?with (.+?)(?:\?|$)',
                r'technical-signal-agent.+?to (.+?)(?:\?|$)',
                r'research agent.+?for (.+?)(?:\?|$)'
            ]

            import re
            for pattern in task_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    task = match.group(1).strip()
                    # Clean up the task description
                    task = task.replace(' and ', ' ').replace(' the ', ' ')
                    return task.capitalize()

            # If no specific pattern matches, try to extract after common trigger words
            trigger_words = ['analyze', 'research', 'help with', 'work on', 'examine', 'investigate']
            for trigger in trigger_words:
                if trigger in message_lower:
                    # Extract everything after the trigger word
                    start_idx = message_lower.find(trigger) + len(trigger)
                    remaining_text = message[start_idx:].strip()
                    # Remove common prefixes and suffixes
                    remaining_text = remaining_text.lstrip('the ').rstrip('?!.')
                    if remaining_text:
                        return remaining_text.capitalize()

            # Default fallback - return the original message without common prefixes
            cleaned_message = message.replace('Can you have an agent ', '').replace('Please ', '').strip()
            return cleaned_message.capitalize()

        except Exception as e:
            logger.error(f"Error extracting task from message: {e}")
            return message.strip()