"""
Tool Definitions for AI Assistant
=================================

GPT-5.1 Responses API function calling tool schemas.
These define the available tools/agents that the AI can invoke.

Session 131: Refactored from 14+ individual tools to agent orchestrators.
Session 184: Extracted from personal_ai_assistant_enhanced.py
Session 266: Tool descriptions moved to core/prompts/tool_descriptions.py
"""

from typing import List, Dict
from core.assistant.constants import (
    IMAGE_EDITING_OPERATIONS,
    VIDEO_GENERATION_OPERATIONS,
    AUDIO_GENERATION_OPERATIONS,
    THREE_D_OPERATIONS,
    VIDEO_EDITING_ALL_OPERATIONS,
    ELEVENLABS_VOICES,
    COLOR_GRADING_EFFECTS,
    PROFESSIONAL_CODECS,
    ASPECT_RATIOS,
    WORKFLOW_TYPES,
)

# Session 266: Import tool descriptions from central registry
from core.prompts import get_tool_description


def get_tool_definitions() -> List[Dict]:
    """
    Get agent-based tool definitions for GPT-5.1 Responses API function calling.

    Architecture: GPT-5.1 -> Agent -> Specific Operation

    Returns:
        List of tool definition dictionaries
    """
    # Session 266: Reordered - most common tools first, workflow agent LAST
    # Session 293: Added business research agents (no API credits needed)
    # GPT tends to prefer earlier tools in the list, so put image generation first
    return [
        _get_image_generation_agent_definition(),  # Most common - simple image creation
        _get_image_editing_agent_definition(),     # Second most common - upscale, variations, etc.
        _get_video_generation_agent_definition(),
        _get_audio_generation_agent_definition(),
        _get_three_d_generation_agent_definition(),
        _get_video_editing_agent_definition(),
        _get_character_training_agent_definition(),
        _get_coleadership_agent_definition(),
        _get_talking_character_agent_definition(),
        _get_web_search_definition(),
        _get_create_brand_video_definition(),
        _get_create_project_from_research_definition(),
        _get_strategic_review_definition(),
        _get_competitor_analysis_agent_definition(),  # Session 293: Business research
        _get_customer_research_agent_definition(),    # Session 293: Customer research
        _get_brand_strategy_agent_definition(),       # Session 335: Brand strategy research
        _get_content_strategy_agent_definition(),     # Session 337: Content strategy research
        _get_marketing_strategy_agent_definition(),   # Session 337: Marketing strategy research
        _get_legal_doc_drafter_agent_definition(),    # Session 403: Pro Se Legal Assistant
        _get_workflow_orchestration_agent_definition(),  # LAST - only for explicit package requests
    ]


def _get_workflow_orchestration_agent_definition() -> Dict:
    """
    Workflow orchestration agent for multi-step creative workflows.
    Session 266: Description moved to core/prompts/tool_descriptions.py
    """
    return {
        "type": "function",
        "name": "workflow_orchestration_agent",
        "description": get_tool_description("workflow_orchestration_agent"),
        "parameters": {
            "type": "object",
            "properties": {
                "workflow": {
                    "type": "string",
                    "enum": WORKFLOW_TYPES,
                    "description": "Workflow type: 'research_and_create_logos' (logos), 'youtube_thumbnail_package' (thumbnails), 'social_media_kit' (social graphics), 'logo_to_video' (animate logo)"
                },
                "topic": {
                    "type": "string",
                    "description": "The main topic INCLUDING any character/mascot. Examples: 'AI content generation with donkey mascot', 'coffee shop with owl character', 'tech startup'. If user mentions a specific character (donkey, owl, lion, etc.), INCLUDE it in the topic!"
                },
                "count": {
                    "type": "integer",
                    "default": 3,
                    "description": "Number of logos/images to create (1-5). Extract from user request like 'create 3 logos' → count=3."
                },
                "style_preferences": {
                    "type": "string",
                    "description": "CRITICAL: Extract ANY style mentioned by user! Animation styles: 'pixar', 'disney', 'dreamworks', 'ghibli', 'anime', 'cartoon'. Art styles: 'watercolor', 'cyberpunk', 'minimalist', 'retro'. If user says 'DreamWorks style donkey' → style_preferences='dreamworks'. If user says 'Pixar-style mascot' → style_preferences='pixar'. ALWAYS extract the style - this determines mascot characters vs flat icons!"
                },
                "image_id": {
                    "type": "string",
                    "description": "Image ID to animate (for logo_to_video workflow). Can use sequential number like '5' or full UUID. Required when workflow='logo_to_video'."
                },
                "project_id": {
                    "type": "string",
                    "description": "Optional existing project ID to add content to"
                },
                "user_message": {
                    "type": "string",
                    "description": "CRITICAL: ALWAYS pass the EXACT original user message here! This ensures no style, mascot, or character info is lost. Copy-paste the user's request verbatim."
                }
            },
            "required": ["workflow", "user_message"]
        }
    }


def _get_image_generation_agent_definition() -> Dict:
    """Image generation agent tool definition. Session 266: Description in registry."""
    return {
        "type": "function",
        "name": "image_generation_agent",
        "description": get_tool_description("image_generation_agent"),
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
                    "description": "Optional trained character/style model to use for generation. CRITICAL: Extract ANY mention of a specific style, brand identity, character model, or trained aesthetic from the user's request. Examples: 'AI content generation company style', 'company style', 'our brand style', 'the trained model', etc. The backend will automatically match variations and trigger words (case-insensitive, handles spaces/dashes). When user mentions a trained style/model, extract it AS SPOKEN/WRITTEN - don't worry about exact formatting. When specified, uses FLUX + custom LoRA training. Omit for standard Stability AI generation."
                }
            },
            "required": ["prompt"]
        }
    }


def _get_image_editing_agent_definition() -> Dict:
    """Image editing agent tool definition. Session 266: Description in registry."""
    return {
        "type": "function",
        "name": "image_editing_agent",
        "description": get_tool_description("image_editing_agent"),
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Operation to perform: 'upscale' | 'remove_background' | 'create_variations' | 'recolor' | 'search_and_replace' (remove OR replace objects) | 'creative_upscale'",
                    "enum": IMAGE_EDITING_OPERATIONS
                },
                "image_id": {
                    "type": "string",
                    "description": "Image identifier(s) - supports SINGLE or BATCH: Single: '2' or UUID. BATCH: Range '20-25', List '5, 8, 12', Combined '10-15, 20, 25-27'. Examples: 'upscale images 20-25', 'remove backgrounds from images 5, 8, 12', 'create variations of images 10-15'. The agent will process each image sequentially and return a batch summary."
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
    }


def _get_video_generation_agent_definition() -> Dict:
    """Video generation agent tool definition. Session 266: Description in registry."""
    return {
        "type": "function",
        "name": "video_generation_agent",
        "description": get_tool_description("video_generation_agent"),
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Operation: 'generate' | 'animate' | 'extend' | 'chain' | 'lip_sync'",
                    "enum": VIDEO_GENERATION_OPERATIONS
                },
                "params": {
                    "type": "object",
                    "description": "Operation-specific parameters. For generate: {prompt, duration}. For animate: {image_id, motion_prompt, duration}. For extend: {video_id, extension_seconds, prompt}. For chain: {video_ids, add_transitions}. For lip_sync: {video_url, audio_url, sync_mode, temperature}.",
                    "properties": {
                        "prompt": {"type": "string"},
                        "duration": {"type": "integer", "default": 5},
                        "image_id": {"type": "string"},
                        "motion_prompt": {"type": "string", "default": "natural motion"},
                        "video_id": {"type": "string"},
                        "extension_seconds": {"type": "integer", "default": 10},
                        "video_ids": {"type": "array", "items": {"type": "string"}},
                        "add_transitions": {"type": "boolean", "default": True},
                        "video_url": {"type": "string", "description": "URL to video with face for lip sync"},
                        "audio_url": {"type": "string", "description": "URL to audio file to sync lips to"},
                        "sync_mode": {"type": "string", "enum": ["cut_off", "loop", "bounce"], "default": "cut_off", "description": "How to handle duration mismatch"},
                        "temperature": {"type": "number", "default": 0.5, "description": "Expression intensity 0-1 (0.5 = natural)"}
                    }
                },
                "project_id": {
                    "type": "string",
                    "description": "Optional project ID"
                }
            },
            "required": ["operation", "params"]
        }
    }


def _get_audio_generation_agent_definition() -> Dict:
    """Audio generation agent tool definition. Session 266: Description in registry."""
    return {
        "type": "function",
        "name": "audio_generation_agent",
        "description": get_tool_description("audio_generation_agent"),
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Operation: 'generate_voice' | 'add_voiceover'",
                    "enum": AUDIO_GENERATION_OPERATIONS
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
    }


def _get_three_d_generation_agent_definition() -> Dict:
    """3D generation agent tool definition. Session 266: Description in registry."""
    return {
        "type": "function",
        "name": "three_d_generation_agent",
        "description": get_tool_description("three_d_generation_agent"),
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Operation (currently only 'convert')",
                    "enum": THREE_D_OPERATIONS
                },
                "image_id": {
                    "type": "string",
                    "description": "Image identifier: sequential number OR full UUID"
                },
                "project_id": {"type": "string"}
            },
            "required": ["operation", "image_id"]
        }
    }


def _get_video_editing_agent_definition() -> Dict:
    """Video editing agent tool definition. Session 266: Description in registry."""
    return {
        "type": "function",
        "name": "video_editing_agent",
        "description": get_tool_description("video_editing_agent"),
        "parameters": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "description": "Video editing operation to perform",
                    "enum": VIDEO_EDITING_ALL_OPERATIONS
                },
                "video_id": {
                    "type": "string",
                    "description": "Video identifier(s) - supports SINGLE or BATCH: Single: '2' or UUID. BATCH: Range '1-3', List '1, 2, 5', Combined '1-3, 5'. Works with ALL operations. Each video processed sequentially. For picture_in_picture/transition: this is the BACKGROUND/first video."
                },
                "params": {
                    "type": "object",
                    "description": "Operation-specific parameters",
                    "properties": {
                        "text": {"type": "string"},
                        "position": {"type": "string", "default": "center"},
                        "start_second": {"type": "number", "default": 0},
                        "duration": {"type": "number", "default": 3},
                        "font_size": {"type": "integer", "default": 72},
                        "style": {"type": "string", "default": "cinematic_warm"},
                        "scale_factor": {"type": "integer", "enum": [2, 4], "default": 2, "description": "Upscale factor (2x or 4x)"},
                        "quality": {"type": "string", "default": "high", "description": "Upscale quality (high or medium)"},
                        "effect": {"type": "string", "enum": COLOR_GRADING_EFFECTS, "default": "cinematic", "description": "Color grading effect"},
                        "intensity": {"type": "number", "default": 0.7, "description": "Effect intensity (0.0-1.0)"},
                        "timestamp": {"type": "number", "default": 0, "description": "Time in seconds to extract frame from"},
                        "format": {"type": "string", "enum": ["jpg", "png"], "default": "jpg", "description": "Output format for extracted frame"},
                        "reverse_audio": {"type": "boolean", "default": True, "description": "Whether to also reverse the audio"},
                        "start_time": {"type": "number", "default": 0, "description": "Start time in seconds for trim operation"},
                        "end_time": {"type": "number", "description": "End time in seconds for trim operation"},
                        "keep_audio": {"type": "boolean", "default": True, "description": "Whether to keep audio in trimmed video"},
                        "speed": {"type": "number", "default": 1.0, "description": "Speed multiplier (0.25-4.0). 0.5 = slow motion, 2.0 = 2x speed"},
                        "preserve_audio": {"type": "boolean", "default": True, "description": "Whether to preserve audio when changing speed"},
                        "video_ids": {"type": "array", "items": {"type": "string"}, "description": "List of video IDs to concatenate"},
                        "rotation": {"type": "string", "description": "Rotation type - 90, 180, 270 (degrees), or 'horizontal', 'vertical', 'both' for flipping"},
                        "fade_in": {"type": "number", "default": 1.0, "description": "Fade in duration in seconds"},
                        "fade_out": {"type": "number", "default": 1.0, "description": "Fade out duration in seconds"},
                        "fade_color": {"type": "string", "enum": ["black", "white"], "default": "black", "description": "Fade color"},
                        "mode": {"type": "string", "enum": ["crop", "resize", "aspect"], "default": "resize", "description": "Crop/resize mode"},
                        "width": {"type": "integer", "description": "Target width for resize"},
                        "height": {"type": "integer", "description": "Target height for resize"},
                        "crop_x": {"type": "integer", "default": 0, "description": "Crop start X position"},
                        "crop_y": {"type": "integer", "default": 0, "description": "Crop start Y position"},
                        "crop_width": {"type": "integer", "description": "Crop width"},
                        "crop_height": {"type": "integer", "description": "Crop height"},
                        "aspect": {"type": "string", "enum": ASPECT_RATIOS, "default": "16:9", "description": "Target aspect ratio"},
                        "audio_operation": {"type": "string", "enum": ["volume", "mute", "extract"], "default": "volume", "description": "Audio control operation"},
                        "volume": {"type": "number", "default": 1.0, "description": "Volume multiplier"},
                        "output_format": {"type": "string", "enum": ["mp3", "wav", "aac", "m4a", "flac"], "default": "mp3", "description": "Audio extraction output format"},
                        "overlay_video_id": {"type": "string", "description": "Video ID for PiP overlay"},
                        "scale": {"type": "number", "default": 0.25, "description": "PiP overlay scale (0.1-0.8)"},
                        "margin": {"type": "integer", "default": 10, "description": "PiP margin from edge in pixels"},
                        "opacity": {"type": "number", "default": 1.0, "description": "PiP overlay opacity (0.0-1.0)"},
                        "image_id": {"type": "string", "description": "Watermark/logo image ID"},
                        "region": {"type": "string", "enum": ["top_left", "top_right", "bottom_left", "bottom_right", "center", "full", "custom"], "default": "center", "description": "Blur region"},
                        "blur_strength": {"type": "integer", "default": 15, "description": "Blur intensity 1-30"},
                        "codec": {"type": "string", "enum": PROFESSIONAL_CODECS, "default": "prores_422_hq", "description": "Professional codec for render_professional"},
                        "grade_type": {"type": "string", "enum": COLOR_GRADING_EFFECTS, "default": "cinematic", "description": "Color grade preset for color_grade_professional"}
                    }
                },
                "project_id": {"type": "string"}
            },
            "required": ["operation", "video_id"]
        }
    }


def _get_character_training_agent_definition() -> Dict:
    """Character training agent tool definition. Session 266: Description in registry."""
    return {
        "type": "function",
        "name": "character_training_agent",
        "description": get_tool_description("character_training_agent"),
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
    }


def _get_coleadership_agent_definition() -> Dict:
    """Co-leadership agent tool definition. Session 266: Description in registry."""
    return {
        "type": "function",
        "name": "coleadership_agent",
        "description": get_tool_description("coleadership_agent"),
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
    }


def _get_talking_character_agent_definition() -> Dict:
    """Talking character agent tool definition. Session 266: Description in registry."""
    return {
        "type": "function",
        "name": "talking_character_agent",
        "description": get_tool_description("talking_character_agent"),
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
                    "enum": ELEVENLABS_VOICES,
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
                    "description": "Optional description of character motion during speech."
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
                    "description": "Which lip sync model to use: 'auto' (cartoon-optimized - RECOMMENDED), 'latentsync' (ByteDance - best for cartoon/stylized/Pixar characters), 'sync_labs' (best for photorealistic humans)."
                },
                "project_id": {
                    "type": "string",
                    "description": "Optional project ID to associate the talking character video with."
                }
            },
            "required": ["image_id", "text"]
        }
    }


def _get_web_search_definition() -> Dict:
    """Web search tool definition. Session 266: Description in registry."""
    return {
        "type": "function",
        "name": "web_search",
        "description": get_tool_description("web_search"),
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
    }


def _get_create_brand_video_definition() -> Dict:
    """Brand video creation tool definition. Session 266: Description in registry."""
    return {
        "type": "function",
        "name": "create_brand_video",
        "description": get_tool_description("create_brand_video"),
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


def _get_create_project_from_research_definition() -> Dict:
    """Session 189/266: Create project from research. Description in registry."""
    return {
        "type": "function",
        "name": "create_project_from_research",
        "description": get_tool_description("create_project_from_research"),
        "parameters": {
            "type": "object",
            "properties": {
                "project_name": {
                    "type": "string",
                    "description": "A clear, professional project name (e.g., 'AI Content Platform Branding', 'Mechanic Shop Logos'). Should reflect the research topic and content type."
                },
                "research_summary": {
                    "type": "string",
                    "description": "A brief summary of the research findings (2-3 sentences). This becomes the project's context and helps future AI interactions."
                },
                "image_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of image IDs (sequential numbers like '1', '2', '3') to include in the project. These should be the images just generated."
                },
                "category": {
                    "type": "string",
                    "enum": ["branding", "marketing", "social_media", "product", "entertainment", "education", "other"],
                    "default": "branding",
                    "description": "Project category based on the content type"
                },
                "suggested_next_steps": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "3-5 suggested next steps for the user (e.g., 'Upscale favorite images', 'Create video animations', 'Train a character model')"
                }
            },
            "required": ["project_name", "research_summary"]
        }
    }


def _get_strategic_review_definition() -> Dict:
    """Session 189/266: Strategic review. Description in registry."""
    return {
        "type": "function",
        "name": "strategic_review",
        "description": get_tool_description("strategic_review"),
        "parameters": {
            "type": "object",
            "properties": {
                "research_topic": {
                    "type": "string",
                    "description": "The original research topic/request from the user"
                },
                "research_findings": {
                    "type": "string",
                    "description": "Summary of key findings from web_search - include competitor info, trends, best practices discovered"
                },
                "content_type": {
                    "type": "string",
                    "enum": ["logo", "banner", "social_media", "brand_identity", "marketing", "video", "general"],
                    "default": "general",
                    "description": "What type of content will be created based on this research"
                },
                "user_context": {
                    "type": "string",
                    "description": "Any additional context from the user's original request (brand name, preferences, constraints, etc.)"
                }
            },
            "required": ["research_topic", "research_findings"]
        }
    }


# =============================================================================
# BUSINESS RESEARCH AGENTS (Session 293)
# =============================================================================

def _get_competitor_analysis_agent_definition() -> Dict:
    """
    Session 293: Competitor analysis agent for business research.
    Does NOT use Stability AI or Runway ML credits.
    """
    return {
        "type": "function",
        "name": "competitor_analysis_agent",
        "description": get_tool_description("competitor_analysis_agent"),
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
                },
                "project_id": {
                    "type": "string",
                    "description": "Optional project ID to use context from. If user says 'for this project' or 'for the current project', extract the project ID from conversation context."
                }
            },
            "required": ["market"]
        }
    }


def _get_customer_research_agent_definition() -> Dict:
    """
    Session 293: Customer research agent for persona building and pain point discovery.
    Does NOT use Stability AI or Runway ML credits.
    """
    return {
        "type": "function",
        "name": "customer_research_agent",
        "description": get_tool_description("customer_research_agent"),
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
                },
                "project_id": {
                    "type": "string",
                    "description": "Optional project ID to use context from. If user says 'for this project' or 'for the current project', extract the project ID from conversation context."
                }
            },
            "required": ["market"]
        }
    }


def _get_brand_strategy_agent_definition() -> Dict:
    """
    Session 335: Brand strategy agent that reads existing project research.
    Produces comprehensive brand strategy reports (no image/video generation).
    """
    return {
        "type": "function",
        "name": "brand_strategy_agent",
        "description": get_tool_description("brand_strategy_agent"),
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "REQUIRED: Project ID to read existing research from. This agent works best when the project already has competitor/customer research."
                },
                "brand_name": {
                    "type": "string",
                    "description": "Optional: The brand name to develop strategy for. If not provided, uses project name."
                },
                "focus_areas": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional areas to focus on: 'positioning', 'messaging', 'visual_direction', 'differentiation', 'audience'. Defaults to comprehensive strategy."
                },
                "user_context": {
                    "type": "string",
                    "description": "Additional context about brand goals, preferences, or constraints"
                }
            },
            "required": ["project_id"]
        }
    }


def _get_content_strategy_agent_definition() -> Dict:
    """
    Session 337: Content strategy agent that analyzes existing research
    and trends to recommend what content to create.
    """
    return {
        "type": "function",
        "name": "content_strategy_agent",
        "description": get_tool_description("content_strategy_agent"),
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "REQUIRED: Project ID to read existing research from. Works best with prior competitor/customer/brand research."
                },
                "task": {
                    "type": "string",
                    "description": "The content strategy request, e.g., 'Create a content strategy for our podcast' or 'What content should we create next?'"
                },
                "focus_areas": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional areas to focus on: 'pillars', 'formats', 'topics', 'calendar', 'seo'. Defaults to comprehensive strategy."
                }
            },
            "required": ["project_id"]
        }
    }


def _get_marketing_strategy_agent_definition() -> Dict:
    """
    Session 337: Marketing strategy agent that creates comprehensive
    marketing plans based on existing research.
    """
    return {
        "type": "function",
        "name": "marketing_strategy_agent",
        "description": get_tool_description("marketing_strategy_agent"),
        "parameters": {
            "type": "object",
            "properties": {
                "project_id": {
                    "type": "string",
                    "description": "REQUIRED: Project ID to read existing research from. Works best with prior competitor/customer/brand/content research."
                },
                "task": {
                    "type": "string",
                    "description": "The marketing strategy request, e.g., 'Create a marketing plan' or 'How should we promote our content?'"
                },
                "budget": {
                    "type": "string",
                    "description": "Optional budget context: 'bootstrap' (minimal), 'moderate', 'significant'. Affects recommendations."
                },
                "channels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Optional specific channels to focus on: 'social', 'email', 'paid', 'seo', 'partnerships'."
                }
            },
            "required": ["project_id"]
        }
    }


# =============================================================================
# LEGAL AGENTS (Session 403)
# =============================================================================

def _get_legal_doc_drafter_agent_definition() -> Dict:
    """
    Session 403: Pro Se Legal Assistant for Colorado family law.
    Provides general legal information and document templates.
    NOT legal advice - always recommends attorney consultation.
    """
    return {
        "type": "function",
        "name": "legal_doc_drafter_agent",
        "description": get_tool_description("legal_doc_drafter_agent"),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The legal question, situation, or document request. Be specific about what type of document or information is needed."
                },
                "document_type": {
                    "type": "string",
                    "enum": ["guidance", "motion", "email", "declaration", "checklist"],
                    "description": "Type of output needed: 'guidance' (general info), 'motion' (court filing template), 'email' (meet-and-confer), 'declaration' (sworn statement template), 'checklist' (procedural steps)"
                },
                "jurisdiction": {
                    "type": "string",
                    "default": "Colorado",
                    "description": "State jurisdiction (currently focused on Colorado family law)"
                },
                "case_type": {
                    "type": "string",
                    "enum": ["divorce", "custody", "child_support", "parenting_time", "modification", "enforcement", "general"],
                    "description": "Type of family law case: divorce, custody, child_support, parenting_time, modification, enforcement, or general"
                },
                "user_context": {
                    "type": "string",
                    "description": "Additional context about the user's situation to make the response more relevant (without sharing sensitive details)"
                }
            },
            "required": ["query"]
        }
    }
