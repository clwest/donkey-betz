"""
Tool Definitions for AI Assistant
=================================

GPT-5.1 Responses API function calling tool schemas.
These define the available tools/agents that the AI can invoke.

Session 131: Refactored from 14+ individual tools to agent orchestrators.
Session 184: Extracted from personal_ai_assistant_enhanced.py
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


def get_tool_definitions() -> List[Dict]:
    """
    Get agent-based tool definitions for GPT-5.1 Responses API function calling.

    Architecture: GPT-5.1 -> Agent -> Specific Operation

    Returns:
        List of tool definition dictionaries
    """
    return [
        _get_workflow_orchestration_agent_definition(),  # Session 191: PRIORITY - multi-step workflows
        _get_image_generation_agent_definition(),
        _get_image_editing_agent_definition(),
        _get_video_generation_agent_definition(),
        _get_audio_generation_agent_definition(),
        _get_three_d_generation_agent_definition(),
        _get_video_editing_agent_definition(),
        _get_character_training_agent_definition(),
        _get_coleadership_agent_definition(),
        _get_talking_character_agent_definition(),
        _get_web_search_definition(),
        _get_create_brand_video_definition(),
        _get_create_project_from_research_definition(),  # Session 189
        _get_strategic_review_definition(),  # Session 189: Research → Review → Create workflow
    ]


def _get_workflow_orchestration_agent_definition() -> Dict:
    """
    Workflow orchestration agent for multi-step creative workflows.

    Session 191: This agent ensures GPT cannot deviate from intended workflows.
    Instead of calling multiple tools, GPT calls this ONE agent which
    internally executes the correct steps in order.

    CRITICAL: This should be the FIRST tool GPT considers for any request
    that involves RESEARCH + CREATION (multiple steps).
    """
    return {
        "type": "function",
        "name": "workflow_orchestration_agent",
        "description": """CRITICAL: Use this agent for ANY multi-step request that involves RESEARCH + CREATION.

WHEN TO USE THIS AGENT:
- "Research X and create Y logos/images" → workflow='research_and_create_logos'
- "Look up trends for X and make logos" → workflow='research_and_create_logos'
- "Find out about X then create Y professional logos" → workflow='research_and_create_logos'

This agent will AUTOMATICALLY execute ALL required steps in the correct order:
1. Web research (web_search)
2. Executive team review (coleadership_agent)
3. Image generation (image_generation_agent)
4. Project organization (create_project_from_research)

DO NOT try to call these tools individually for research+create requests!
The workflow agent ensures proper order and prevents errors.

For SIMPLE single-step requests (just "create a logo" without research, "upscale image 3"), use the individual agents directly.""",
        "parameters": {
            "type": "object",
            "properties": {
                "workflow": {
                    "type": "string",
                    "enum": WORKFLOW_TYPES,
                    "description": "Workflow type. Use 'research_and_create_logos' for any request involving research + logo/image creation."
                },
                "topic": {
                    "type": "string",
                    "description": "The main topic to research (e.g., 'modern AI company', 'tech startup', 'coffee shop', 'fitness brand'). Extract the key subject from the user's request."
                },
                "count": {
                    "type": "integer",
                    "default": 3,
                    "description": "Number of logos/images to create (1-5). Extract from user request like 'create 3 logos' → count=3."
                },
                "style_preferences": {
                    "type": "string",
                    "description": "Optional style preferences mentioned by user (e.g., 'minimalist', 'bold colors', 'geometric', 'professional')"
                },
                "project_id": {
                    "type": "string",
                    "description": "Optional existing project ID to add content to"
                }
            },
            "required": ["workflow", "topic"]
        }
    }


def _get_image_generation_agent_definition() -> Dict:
    """Image generation agent tool definition."""
    return {
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
                    "description": "Optional trained character/style model to use for generation. CRITICAL: Extract ANY mention of a specific style, brand identity, character model, or trained aesthetic from the user's request. Examples: 'AI content generation company style', 'company style', 'our brand style', 'the trained model', etc. The backend will automatically match variations and trigger words (case-insensitive, handles spaces/dashes). When user mentions a trained style/model, extract it AS SPOKEN/WRITTEN - don't worry about exact formatting. When specified, uses FLUX + custom LoRA training. Omit for standard Stability AI generation."
                }
            },
            "required": ["prompt"]
        }
    }


def _get_image_editing_agent_definition() -> Dict:
    """Image editing agent tool definition with batch support."""
    return {
        "type": "function",
        "name": "image_editing_agent",
        "description": "MODIFY EXISTING images only. Requires an existing image_id. Operations: upscale (4x resolution), remove_background (transparent PNG), create_variations (multiple styles), recolor (change colors), search_and_replace (REMOVE objects by omitting replace_prompt OR replace with something else), creative_upscale (4x upscale + add creative details with prompt). IMPORTANT: This agent modifies images that already exist. For creating NEW images from scratch, use image_generation_agent instead. Supports BATCH OPERATIONS - process multiple images at once using ranges or lists!",
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
    """Video generation agent tool definition."""
    return {
        "type": "function",
        "name": "video_generation_agent",
        "description": "Handle video generation operations: generate (create video from text prompt), animate (transform image to moving video WITHOUT speech), extend (make video longer), chain (combine multiple videos), lip_sync (sync existing audio to existing video). NOTE: For 'make image talk' or 'create talking character', use talking_character_agent instead (it combines TTS + animation + lip sync). Use THIS agent for: video from text prompts, silent animation from images, video extension, video chaining, or manual lip sync when you already have separate audio and video files.",
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
    """Audio generation agent tool definition."""
    return {
        "type": "function",
        "name": "audio_generation_agent",
        "description": "Handle all audio generation: generate_voice (text-to-speech), add_voiceover (add narration to video). Use this agent for ANY audio generation request.",
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
    """3D generation agent tool definition."""
    return {
        "type": "function",
        "name": "three_d_generation_agent",
        "description": "Convert images to 3D models using Replicate TRELLIS. Creates downloadable GLB files for 3D printing. Use when users want: 'convert to 3D', 'make 3D model', '3D print', 'create 3D object'.",
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
    """Video editing agent tool definition with all operations."""
    return {
        "type": "function",
        "name": "video_editing_agent",
        "description": "Handle all video editing: add_text_overlay (captions/titles with timing), apply_color_grading (DaVinci cinematic effects), upscale (2x or 4x quality enhancement with ffmpeg - FREE!), apply_effect (color grading: cinematic, vibrant, vintage, noir, warm, cool - FREE!), extract_frame (pull a still image from any timestamp - FREE!), reverse (play video backwards - FREE!), trim (cut video to specific time range - FREE!), speed_change (slow motion 0.5x or speed up 2x - FREE!), concatenate (combine multiple videos into one - FREE!), rotate_flip (rotate 90/180/270 degrees or flip horizontal/vertical - FREE!), fade (add fade in/out effects - FREE!), crop_resize (crop to region, resize dimensions, or change aspect ratio - FREE!), audio_control (adjust volume, mute, or extract audio - FREE!), picture_in_picture (overlay one video on another - FREE!), add_watermark (overlay logo/image on video with position and opacity - FREE!), blur_region (blur part of video for privacy/censoring - FREE!), render_professional (EXPORT TO ProRes 422/ProRes 4444/DNxHD - Professional broadcast codecs!), apply_lut (apply color LUT files), color_grade_professional (DaVinci-style lift/gamma/gain color grading). Use this agent for ANY video editing request. SUPPORTS BATCH OPERATIONS: Process multiple videos using ranges '1-3' or lists '1, 3, 5'. FOR PRORES: Say 'render video 1 in ProRes' or 'export video 2 as ProRes 4444'.",
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
    """Character training agent tool definition for FLUX LoRA."""
    return {
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
    }


def _get_coleadership_agent_definition() -> Dict:
    """Co-leadership agent tool definition for AI-Human collaboration."""
    return {
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
    }


def _get_talking_character_agent_definition() -> Dict:
    """Talking character agent tool definition for TTS + animation + lip sync."""
    return {
        "type": "function",
        "name": "talking_character_agent",
        "description": "PREFERRED for 'make image talk' requests. Create complete talking character videos from a still image and text script in ONE STEP. This pipeline combines Text-to-Speech (ElevenLabs) + Image-to-Video (Runway) + Lip Sync to bring static characters to life with natural speech and mouth movements. NOW SUPPORTS CARTOON/STYLIZED CHARACTERS! Use when user wants: 'make image X talk and say...', 'create talking video', 'add speech to image', 'animate character with voice', 'talking character', 'AI spokesperson video', etc. IMPORTANT: When user says 'using [name] voice' or 'with [name] voice', extract that name as the voice parameter! This is the ONLY tool that generates speech + animation + lip sync automatically. Works great with both photorealistic AND cartoon/Pixar-style characters! Cost: ~$0.60-1.00 per 10-second video.",
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
    """Web search tool definition for research capabilities."""
    return {
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
    }


def _get_create_brand_video_definition() -> Dict:
    """Brand video creation tool definition."""
    return {
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


def _get_create_project_from_research_definition() -> Dict:
    """
    Session 189: Create a new project from research results and generated content.

    This enables the "research → create → organize" workflow where the AI can:
    1. Research a topic (web_search)
    2. Generate starter images
    3. Package everything into a new project
    """
    return {
        "type": "function",
        "name": "create_project_from_research",
        "description": "Create a new creative project from research results and generated images. Use this AFTER completing research (web_search) and generating starter images (image_generation_agent). This packages everything into an organized project that the user can continue working on. Use when: 1) Research has been completed, 2) Images have been generated, 3) User would benefit from having an organized project. DO NOT use this for simple one-off image generations.",
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
            "required": ["project_name", "research_summary", "image_ids"]
        }
    }


def _get_strategic_review_definition() -> Dict:
    """
    Session 189: Get executive team review of research before generating content.

    This enables the "research → strategic review → create" workflow where:
    1. Research is conducted (web_search)
    2. Executive team (CTO, COO, Creative Director) reviews findings
    3. They provide strategic direction and creative recommendations
    4. THEN images/content are generated based on their guidance

    This makes the co-leadership agents an integral part of the creative process,
    not just reactive reviewers of finished work.
    """
    return {
        "type": "function",
        "name": "strategic_review",
        "description": "IMPORTANT: Call this AFTER web_search but BEFORE image_generation_agent. Get strategic review and creative direction from the executive team (CTO, COO, Creative Director) based on research findings. They will analyze the research and provide: 1) Key insights to incorporate, 2) Creative direction recommendations, 3) Technical considerations, 4) Specific prompt suggestions for image generation. This ensures the co-leadership agents guide the creative process rather than just reviewing finished work.",
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
