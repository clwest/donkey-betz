"""
Image views — tools functions.
"""

"""
Image Generation Views
Phase 2: Frontend Reality Fix - Image Generation

Handles image generation requests using:
- Stability AI (Stable Diffusion) - Primary
- Replicate API - Fallback

Created: September 30, 2025
"""

import os
import logging
import requests
import uuid
import json
import zipfile
import base64
from openai import OpenAI
from io import BytesIO
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone  # Session 96 Weekend Project
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from PIL import Image as PILImage

# Phase 2 P1: Rate limiting for image operations
from core.decorators import rate_limit
# Phase 2 P1: Input validation
from core.validators import validate_prompt, sanitize_prompt, validate_uuid, validate_numeric_range
# Phase 2 P1: Safe error handling
# Session 487: Creator watermark integration
from core.services.watermark_integration import save_watermarked_image
# Session 769: Cost tracking for external APIs
from core.services.api_cost_config import calculate_stability_cost

logger = logging.getLogger(__name__)


# ========================================
# SESSION 794: SYSTEM USER FOR AUTONOMOUS OPERATIONS
# ========================================

from django.views.decorators.csrf import csrf_exempt


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assistant_chat(request):
    """
    AI Assistant chat endpoint using GPT-5
    Session 58: Phase B.3 - Personal Assistant Integration
    Session 59: Phase B.4 - Enhanced with user preference learning

    Handles general conversational queries from the AI Assistant.
    Fast, intelligent responses for questions about the platform,
    creative advice, and general help.

    Now includes personalized context based on user's workflow history!

    Example:
        Input: "What's the best way to create professional images?"
        Output: Helpful advice from GPT-5 about image generation techniques
                (personalized based on user's favorite workflows and styles)
    """
    try:
        user_message = request.data.get('message', '').strip()
        conversation_history = request.data.get('history', [])  # Optional for context
        session_id = request.data.get('session_id')  # Session 96 Weekend Project
        project_id = request.data.get('project_id')  # Session 97: Project tracking

        if not user_message:
            return Response({
                'error': 'Message is required'
            }, status=400)

        # Session 96 Weekend Project: Get or create AI session for tracking
        # Session 97: Link to active project
        session = get_or_create_session(
            user=request.user,
            session_id=session_id,
            first_prompt=user_message if not session_id else None,
            project_id=project_id
        )

        # Store user message in session transcript
        update_session_transcript(session, 'user', user_message)

        # Session 59: Phase B.4 - Get user preferences for personalized assistance
        user_prefs = get_user_preferences(request.user)

        # Session 62: Phase C.3.2 - Get user's projects for strategic planning
        from content.models import CreativeProject
        user_projects = CreativeProject.objects.filter(user=request.user).order_by('-created_at')[:5]

        # Build personalized system instructions based on user history
        # Session 65: SUPER AI EXECUTOR - Emphasis on autonomous execution
        ASSISTANT_INSTRUCTIONS = """You are an AI EXECUTOR for the Donkey Betz AI Studio platform.

**CRITICAL: When users want to CREATE content, USE YOUR TOOLS to do it for them immediately. Don't just give advice - EXECUTE!**

You have these autonomous execution tools:
- **generate_image** - Create images/logos/artwork (ONE image per call - if user wants variations, call multiple times!)
  * For LOGOS: Use SIMPLE, CLEAN logo design prompts:
    - Focus on: "logo design", "emblem", "badge", "icon", "brand mark"
    - Specify style: "vector", "flat design", "minimalist", "modern", "clean"
    - Avoid: detailed descriptions of physical objects (cups, beans, etc) - logos are GRAPHIC DESIGNS not photographs!
    - Keep it SHORT and focused on the logo itself, not the business
    - Example: "Modern coffee shop logo with mountain silhouette, vector style, clean lines"
    - NOT: "Detailed coffee shop with beans, cups, steam, multiple Keurig pods..."
  * **NEW (Session 66):** If creating a logo with specific text (company name), pass expected_text parameter!
    Example: generate_image(prompt="Modern coffee shop logo, vector style", expected_text="Mountain Coffee Co.", style="logo")
    The system will AUTOMATICALLY use GPT-4 Vision to verify text and fix it if wrong!
- **generate_video** - Create videos/animations (ONE video per call)
  * Always create cinematic, professional-quality promotional videos
  * IMPORTANT: Keep video prompts under 900 characters (Runway ML limit is 1000)
- **generate_speech** - Create professional voiceovers/narration from text (ONE audio per call)
  * Uses ElevenLabs Eleven v3 for industry-leading voice quality (1-2 second generation!)
  * 12 professional voices available: Rachel (female, warm), Drew (male, clear), Clyde (male, deep), Paul (male, friendly), Aria (female, professional), etc.
  * Example: generate_speech(text="Welcome to our platform", voice="Rachel")
  * IMPORTANT: This creates REAL audio files - don't just respond with text!
- **generate_sound_effect** - Create sound effects from descriptions (ONE sound per call)
  * Generate any sound: thunder, whoosh, door slam, ocean waves, etc.
  * Example: generate_sound_effect(description="thunder clap", duration=3)
  * IMPORTANT: This creates REAL audio files - don't just respond with text!

**VIDEO EDITING WITH DAVINCI RESOLVE (Session 84 - NEW!):**
- **show_recent_videos** - Show user's videos with numbers for easy reference
  * User says "show my videos" or "list videos" → CALL show_recent_videos!
  * Displays videos like: "1. 🎬 Snowboarder on mountain", "2. 🦅 Eagle drone footage"
  * User can then reference by number: "chain videos 1 and 2"
  * IMPORTANT: Call this when user needs to select specific videos!

- **apply_color_grade** - Apply professional color grading to videos using DaVinci Resolve
  * Styles: 'cinematic' (teal/orange Hollywood), 'vibrant' (boosted colors), 'vintage' (film look), 'noir' (B&W), 'warm' (golden hour), 'cool' (blue tones)
  * Example: apply_color_grade(style="cinematic", intensity=0.7)
  * User says "make my video cinematic" → CALL apply_color_grade immediately!
  * This creates a NEW color-graded video (original unchanged)

- **edit_video** - Perform multiple editing operations on videos in one command!
  * Can: chain videos, add text overlays, apply color grading, mix audio
  * Example operations:
    - Chain videos: {type: "chain", transition: "Cross Dissolve", duration: 1.0}
    - Add text: {type: "text", text: "Welcome", position: "center", start: 0, duration: 3}
    - Color grade: {type: "color_grade", style: "cinematic", intensity: 0.7}
    - Add audio: {type: "audio", volume: 0.3}
  * User says "chain my last 3 videos, add a title, and make it cinematic" → CALL edit_video with operations list!
  * This is the MASTER tool for complex editing workflows

**VIDEO SELECTION TIPS:**
- If user asks to chain/edit SPECIFIC videos → First call show_recent_videos so they can see their options!
- User says "chain the snowboarder and eagle videos" → You'll need video numbers, so show videos first
- User says "chain my last 2 videos" → This is clear, no need to show videos
- When unsure which videos user wants → Always show videos first!

**NUMBERED VIDEO REFERENCES (Session 84 - SIMPLIFIED!):**
When user says "chain videos 5 and 8":
1. Extract the numbers: 5 and 8
2. Call edit_video with video_numbers=[5, 8]
3. Backend automatically converts numbers to video IDs!

**IMPORTANT: Use video_numbers parameter for numbered references!**

Example flows:
- User: "Chain videos 5 and 8" → edit_video(video_numbers=[5, 8], operations=[{type: "chain"}])
- User: "Make videos 3 and 7 cinematic" → edit_video(video_numbers=[3, 7], operations=[{type: "color_grade", style: "cinematic"}])
- User: "Chain my last 2 videos" → edit_video(video_selection="last_2", operations=[{type: "chain"}])

**VIDEO NUMBERS vs VIDEO IDs:**
- video_numbers=[5, 8] → Simple! Use when user mentions numbers
- video_ids=['uuid1', 'uuid2'] → Advanced! Use only when you have actual UUIDs
- video_selection="last_2" → Simple! Use for "last X videos"

**VIDEO EDITING PATTERNS:**
- "Make my video cinematic" → apply_color_grade(style="cinematic")
- "Add title to my video" → edit_video(operations=[{type:"text", text:"Title"}])
- "Chain my last 3 videos" → edit_video(video_selection="last_3", operations=[{type:"chain"}])
- "Chain videos and add title" → edit_video(operations=[{type:"chain"}, {type:"text", text:"Title"}])
- "Make it warmer" / "add warm look" → apply_color_grade(style="warm")
- "Make it look like a film" → apply_color_grade(style="vintage")
- "Black and white" → apply_color_grade(style="noir")

**OTHER TOOLS:**
- **inpaint** - Fix specific areas of an existing image (perfect for fixing misspelled text in logos!)
  * Use this to refine logos with text issues
  * Requires: image_url (from previous generate_image), prompt (what to regenerate), mask_description (which area to fix)
- **web_search** - Search Google for information

**AUTONOMOUS TEXT VERIFICATION (Session 66 - CRITICAL!):**
When creating logos with company names, YOU MUST extract the company name and pass it as expected_text!

**REQUIRED PATTERN:**
User: "Create a logo for [Company Name]"
You: Call generate_image(prompt="...", expected_text="[Company Name]")

**Examples:**
User: "Create a logo for Mountain Coffee Co."
→ generate_image(prompt="Mountain coffee shop logo, vector style", expected_text="Mountain Coffee Co.")

User: "Make a logo for Eagle Brewing Company"
→ generate_image(prompt="Eagle brewery logo with beer theme", expected_text="Eagle Brewing Company")

User: "Design a logo for Alpine Tech"
→ generate_image(prompt="Modern tech logo with alpine theme", expected_text="Alpine Tech")

**What happens automatically:**
1. System generates logo
2. GPT-4 Vision checks if text matches expected_text
3. If wrong → autonomously calls inpaint to fix
4. Loops until text is correct (max 3 attempts)
5. Returns perfect logo!

**Manual refinement (if needed):**
If autonomous verification doesn't work, you can still manually call inpaint as backup

The platform also has:
- Image Editing: Recolor, erase, inpaint, outpaint, remove background
- Image Upscaling: Fast 4x, Conservative 4K, Creative upscale
- AI Workflows: Logo Creator, Portrait Enhancer, Style Explorer, etc.
- Projects & Campaigns: Organize workflows into projects

**HOW TO RESPOND:**
- User says "Create a logo" → CALL generate_image tool immediately! Don't just explain!
- User says "Make a video" → CALL generate_video tool immediately!
- User says "Generate speech" → CALL generate_speech tool immediately! Don't just respond with text!
- User says "Create a sound effect" → CALL generate_sound_effect tool immediately!
- User says "Make my video cinematic" → CALL apply_color_grade tool immediately!
- User says "Chain my videos" → CALL edit_video tool immediately!
- User says "Add a title" → CALL edit_video tool immediately!
- User says "Search for trends" → CALL web_search tool immediately!
- User asks "What can you do?" → Explain features (no tools needed)

**MULTI-STEP EXECUTION (CRITICAL!):**
When user requests MULTIPLE things (e.g., "search trends then create logo and video"), YOU MUST CALL ALL TOOLS IN ONE RESPONSE:
- "Search trends then create logo" → Call web_search AND generate_image (both in same response!)
- "Create logo and video" → Call generate_image AND generate_video (both in same response!)
- DO NOT just search and stop! Complete ALL requested steps!

**BE AN EXECUTOR, NOT JUST AN ADVISOR!** Take action when users want content created!

Keep responses under 200 words. Be conversational and practical."""

        # Session 59: Add personalized context based on user preferences
        if user_prefs.get('has_history'):
            personalization = "\n\n**USER PREFERENCES & HISTORY:**\n"

            # Favorite workflow
            if user_prefs.get('favorite_workflow'):
                fav = user_prefs['favorite_workflow']
                workflow_name = fav['type'].replace('_', ' ').title()
                personalization += f"- This user LOVES {workflow_name} ({fav['count']} times, {fav['percentage']}% of workflows)\n"

            # Favorite styles
            if user_prefs.get('favorite_styles'):
                styles_str = ", ".join(user_prefs['favorite_styles'])
                personalization += f"- Preferred styles: {styles_str}\n"

            # Favorite models
            if user_prefs.get('favorite_models'):
                models_str = ", ".join(user_prefs['favorite_models'])
                personalization += f"- Preferred models: {models_str}\n"

            # Total experience
            personalization += f"- Total workflows completed: {user_prefs['total_workflows']}\n"

            # Favorites
            if user_prefs.get('favorites_count', 0) > 0:
                personalization += f"- Has saved {user_prefs['favorites_count']} favorite workflows\n"

            # Common patterns
            if user_prefs.get('common_patterns'):
                patterns_str = ", ".join(user_prefs['common_patterns'][:2])
                personalization += f"- Common workflow patterns: {patterns_str}\n"

            # Recent activity
            if user_prefs.get('recent_activity'):
                recent = user_prefs['recent_activity'][0]
                workflow_name = recent['workflow_name']
                personalization += f"- Most recent: {workflow_name}\n"

            personalization += "\nUSE THIS CONTEXT to give personalized, relevant advice. Mention their preferences when helpful!"

            ASSISTANT_INSTRUCTIONS += personalization

        # Session 62: Phase C.3.2 - Add project context for strategic planning
        # Session 119: ENHANCED - Use project context for content generation!
        if user_projects.exists():
            project_context = "\n\n**ACTIVE PROJECTS:**\n"
            for project in user_projects:
                project_context += f"- {project.name} ({project.status}): {project.goal}\n"
                project_context += f"  Category: {project.category}, Workflows: {project.total_workflows}, Progress: {project.progress_percentage}%\n"
                if project.deadline:
                    project_context += f"  Deadline: {project.deadline.strftime('%Y-%m-%d')}\n"

            # Session 119: Add explicit instructions for using project context in content generation
            project_context += "\n**CRITICAL - USE PROJECT CONTEXT FOR CONTENT GENERATION:**\n"
            project_context += "- When user asks to create content (images/videos/audio) during an active project session, EXTRACT the project theme and style!\n"
            project_context += "- Example: Project is 'Three cartoon style logos for a mechanic shop'\n"
            project_context += "  → Video prompt should be: 'Cartoon-style promo video for a mechanic shop with animated tools and vehicles'\n"
            project_context += "  → NOT just: 'Generic promo video for your brand'\n"
            project_context += "- ALWAYS incorporate the project's goal, category, and any style keywords (cartoon, modern, vintage, etc.) into your prompts!\n"
            project_context += "- If the project name mentions a specific style (cartoon, realistic, vintage), USE that style in all content!\n"
            project_context += "\nAlso provide strategic advice based on their active projects. Suggest workflows, timelines, and organization strategies!"
            ASSISTANT_INSTRUCTIONS += project_context

        # Session 119: Add CURRENT session project context if available
        if session and session.project and not session.project.is_quick_starts:
            current_project_context = f"\n\n**🎯 CURRENT ACTIVE SESSION PROJECT:**\n"
            current_project_context += f"**{session.project.name}**\n"
            current_project_context += f"Goal: {session.project.goal}\n"
            current_project_context += f"Category: {session.project.category}\n"
            current_project_context += f"Status: {session.project.status}\n"
            current_project_context += f"\n⚠️ CRITICAL: The user is CURRENTLY working on this project!\n"
            current_project_context += f"- When they ask to create content, it's FOR THIS PROJECT!\n"
            current_project_context += f"- Extract the theme, style, and subject from the project name and goal!\n"
            current_project_context += f"- Use those details in your content generation prompts!\n"
            current_project_context += f"- Example: If project is '{session.project.name}', make content that matches that theme!\n"
            ASSISTANT_INSTRUCTIONS += current_project_context

        # Session 65: SUPER AI EXECUTOR - Function calling support
        # Build messages array for Chat Completions API
        messages = [
            {"role": "system", "content": ASSISTANT_INSTRUCTIONS}
        ]

        # Add conversation history if provided
        if conversation_history and len(conversation_history) > 0:
            # Include last 6 messages for context (same as before)
            recent_history = conversation_history[-6:]
            for msg in recent_history:
                role = msg.get('role', 'user')
                content = msg.get('content', '')
                if role in ['user', 'assistant'] and content:
                    messages.append({"role": role, "content": content})

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Define tools (functions) that GPT-5 can call
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "generate_image",
                    "description": "Generate a SINGLE AI image using Stability AI. Use ONLY when user explicitly wants ONE image. IMPORTANT: If user wants MULTIPLE images (e.g., 'three logos', 'several banners', 'variations'), use generate_with_options instead which provides choice + learning! Also: Do NOT use this for 'character' requests - use create_character_from_prompt instead. Session 66: Now supports autonomous text verification and refinement!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The detailed description of the image to generate. Be specific and descriptive."
                            },
                            "model": {
                                "type": "string",
                                "enum": ["core", "sdxl", "sd3", "ultra"],
                                "description": "The AI model to use. sdxl is best for most cases, ultra for premium quality, sd3 for high detail, core for fast generation."
                            },
                            "style": {
                                "type": "string",
                                "description": "Optional style preset like 'vector', 'photographic', 'digital-art', etc."
                            },
                            "expected_text": {
                                "type": "string",
                                "description": "CRITICAL FOR LOGOS: If generating a logo with company name or text, YOU MUST provide the expected text here. This enables autonomous text verification. Examples: 'Mountain Coffee Co.', 'Eagle Brewing Company', 'Alpine Tech'. When user says 'Create a logo for [Company Name]', extract [Company Name] and pass it here!"
                            }
                        },
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_video",
                    "description": "Generate an AI video using Runway ML. Use this when the user asks to create a video, animation, or moving content.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {
                                "type": "string",
                                "description": "The detailed description of the video to generate."
                            },
                            "duration": {
                                "type": "number",
                                "enum": [4, 6, 8],
                                "description": "Duration in seconds. Must be 4, 6, or 8 (Runway ML requirement). Default: 6"
                            }
                        },
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "inpaint",
                    "description": "Fix or regenerate specific areas of an existing image. Use this to fix text, correct details, or improve specific parts of an image. Perfect for fixing misspelled text in logos!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "image_url": {
                                "type": "string",
                                "description": "The URL of the image to edit (from a previous generate_image result)"
                            },
                            "prompt": {
                                "type": "string",
                                "description": "Description of what to regenerate in the masked area. Be specific! For text: 'The text COFFEE in bold sans-serif font'"
                            },
                            "mask_description": {
                                "type": "string",
                                "description": "Describe which part to fix, e.g., 'the text area at the bottom', 'the misspelled word in the center', 'the company name'"
                            }
                        },
                        "required": ["image_url", "prompt", "mask_description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "web_search",
                    "description": "Search the web using Google. Use this when the user asks for current information, trends, research, or needs to find something online.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The search query"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "chain_videos",
                    "description": "Chain multiple videos together using DaVinci Resolve. Use this when the user asks to combine videos, chain clips, merge videos, or create a longer video from multiple clips. Requires DaVinci Resolve Studio ($200). Session 67: Professional video chaining with transitions!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "video_count": {
                                "type": "number",
                                "description": "Number of videos to chain (default: 2). User will select videos from gallery after."
                            },
                            "transition_type": {
                                "type": "string",
                                "enum": ["Cross Dissolve", "Fade", "Cut", "Wipe"],
                                "description": "Type of transition between videos. Cross Dissolve is smooth blend, Fade is fade to black, Cut is instant, Wipe is directional. Default: Cross Dissolve"
                            },
                            "add_transitions": {
                                "type": "boolean",
                                "description": "Whether to add transitions between videos. Default: true"
                            },
                            "project_name": {
                                "type": "string",
                                "description": "Optional name for the chained video project"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_text_to_video",
                    "description": "Add text overlay to a video using DaVinci Resolve with PERFECT spelling. Use when user wants to add titles, captions, or text to a video. Supports different positions (center, lower_third, upper_third) and customization. Session 72: Voice-controlled text overlays!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The text to display on the video. Will be spelled EXACTLY as provided - no AI text rendering issues!"
                            },
                            "position": {
                                "type": "string",
                                "enum": ["center", "lower_third", "upper_third"],
                                "description": "Position of text on screen. center = middle of screen, lower_third = bottom area (good for names/captions), upper_third = top area. Default: center"
                            },
                            "start_second": {
                                "type": "number",
                                "description": "When to start showing text (in seconds from video start). Default: 0"
                            },
                            "duration": {
                                "type": "number",
                                "description": "How long to show text (in seconds). Default: 3"
                            },
                            "font_size": {
                                "type": "number",
                                "description": "Text size in points (36-144). Default: 72"
                            },
                            "video_selection": {
                                "type": "string",
                                "enum": ["last", "recent"],
                                "description": "Which video to add text to. 'last' = most recent video, 'recent' = user will select from recent videos. Default: last"
                            }
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "add_music_to_video",
                    "description": "Add background music or audio to a video using DaVinci Resolve. Session 82: AUTOMATIC AUDIO DETECTION! When user says 'add that speech/audio to video', ALWAYS call this function even if you can't find audio URL in conversation. VideoAgent will automatically query AudioAgent for most recent audio. DO NOT ask user for audio URL - just call the function! Extract audio_url from conversation if visible (look for '**AUDIO_URL:**'), otherwise omit it and VideoAgent handles the rest autonomously!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "video_selection": {
                                "type": "string",
                                "enum": ["last", "recent"],
                                "description": "Which video to add music to. 'last' = most recent video, 'recent' = user will select from recent videos. Default: last"
                            },
                            "audio_url": {
                                "type": "string",
                                "description": "OPTIONAL! URL of audio file to add. Session 82: If user says 'add that speech/audio', try to find '**AUDIO_URL:**' in recent messages. If found, pass it here. If NOT found, OMIT this parameter entirely (don't pass empty string) and VideoAgent will automatically query AudioAgent for most recent audio. This is AUTONOMOUS AGENT COMMUNICATION - let the agents handle it!"
                            },
                            "audio_volume": {
                                "type": "number",
                                "description": "Background music volume level (0.0 to 1.0). 0.0 = silent, 0.3 = quiet background, 0.5 = moderate, 1.0 = full volume. Default: 0.3"
                            },
                            "music_style": {
                                "type": "string",
                                "enum": ["cinematic", "upbeat", "calm", "dramatic", "corporate"],
                                "description": "Style of background music to add (user would upload or select from library). Only used if audio_url not provided. Default: cinematic"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "apply_color_grade",
                    "description": "Apply professional color grading to a video using DaVinci Resolve (the industry-standard color grading tool). Use when user wants to make video look cinematic/warm/cool/vintage, apply a film look, adjust colors, or enhance visual style. Handles voice recognition variations like 'somatic' or 'sim-matic' (from 'cinematic'). Session 72: Voice-controlled color grading!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "style": {
                                "type": "string",
                                "enum": ["warm", "cool", "vintage", "modern", "dramatic", "soft", "vibrant"],
                                "description": "Color grading style (SIMPLIFIED for voice recognition). warm = warm orange/teal cinematic tones, cool = cool blue tones, vintage = film look with grain, modern = clean and crisp, dramatic = bold high contrast, soft = muted gentle tones, vibrant = saturated colors. Default: warm. Note: System auto-handles 'somatic'/'sim-matic' as 'warm'."
                            },
                            "video_selection": {
                                "type": "string",
                                "enum": ["last", "recent"],
                                "description": "Which video to apply color grading to. 'last' = most recent video, 'recent' = user will select from recent videos. Default: last"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_brand_video",
                    "description": "Create a complete brand video from concept to finished product using automated workflow. This orchestrates Runway ML video generation → video extension → DaVinci Resolve chaining with professional transitions and branding. Use when user wants a complete, polished brand video without manual steps. Session 67: End-to-end video creation!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "brand_name": {
                                "type": "string",
                                "description": "The brand or company name"
                            },
                            "concept": {
                                "type": "string",
                                "description": "The video concept or message (e.g., 'luxury coffee experience', 'eco-friendly technology', 'family fun')"
                            },
                            "style": {
                                "type": "string",
                                "enum": ["cinematic", "modern", "playful", "elegant", "energetic"],
                                "description": "Visual style for the video. Cinematic = dramatic lighting, Modern = clean & minimal, Playful = colorful & fun, Elegant = sophisticated, Energetic = fast-paced"
                            },
                            "include_branding": {
                                "type": "boolean",
                                "description": "Whether to add brand name text overlay at start/end. Default: true"
                            },
                            "video_count": {
                                "type": "number",
                                "description": "Number of video clips to generate and chain together (2-5). Default: 3"
                            }
                        },
                        "required": ["brand_name", "concept"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_character_from_prompt",
                    "description": "ALWAYS use this tool when user says 'create a character', 'make a character', 'design a character', 'build a character', or 'generate a character'. Creates a trainable character model by generating 5-7 variations with different angles/poses, then trains a custom FLUX LoRA model (30-60 min). The user can later reuse this character by including the trigger word in prompts. DO NOT use generate_image for character requests - always use this tool instead. Session 74: AI-powered character training!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "character_description": {
                                "type": "string",
                                "description": "Detailed description of the character/logo to create (e.g., 'pixar style donkey running a robotics company', 'modern minimalist logo with letter M', 'cartoon superhero cat with red cape')"
                            },
                            "character_name": {
                                "type": "string",
                                "description": "Name for this character model (e.g., 'Robotics Donkey', 'My Company Logo'). If not provided, derived from description."
                            },
                            "trigger_word": {
                                "type": "string",
                                "description": "Trigger word to use in future prompts (short, uppercase, memorable). Default: 'TOK'. Examples: 'LOGO', 'HERO', 'MASCOT'"
                            },
                            "variation_count": {
                                "type": "number",
                                "description": "Number of variations to generate (5-7). More variations = better training but longer wait. Default: 6"
                            },
                            "style": {
                                "type": "string",
                                "description": "Visual style for the character (pixar, anime, realistic, cartoon, minimalist, professional). Default: extracted from description or 'professional'"
                            }
                        },
                        "required": ["character_description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "edit_character_training_image",
                    "description": "Edit a specific training image for a character with natural language instructions. Can use another image as reference for style matching (e.g., 'make image 1 look like image 0'). Regenerates the image with the requested changes (e.g., 'make ears bigger', 'change background to white', 'make more cartoonish'). Use when user wants to refine a training image before starting the training process. If character_id is not known, uses most recent character automatically. Session 75: Image editing workflow with image-to-image!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "character_id": {
                                "type": "number",
                                "description": "ID of the character model being trained (optional - if not provided, uses most recent character)"
                            },
                            "image_number": {
                                "type": "number",
                                "description": "Which image to edit (1-7). Use the image number shown in the preview grid."
                            },
                            "edit_instruction": {
                                "type": "string",
                                "description": "Natural language description of what to change (e.g., 'make the ears bigger', 'change background to white', 'add more detail', 'make it more colorful', 'adjust the lighting')"
                            },
                            "apply_to_all": {
                                "type": "boolean",
                                "description": "If true, applies this edit to all images in the training set. Default: false (only edit specified image)"
                            },
                            "reference_image_number": {
                                "type": "number",
                                "description": "Optional: Use another image as a style/structure reference. When provided, uses image-to-image to make the edited image match the reference (e.g., 'make image 1 look like image 0' would set reference_image_number to 0). This preserves the composition and style of the reference image."
                            },
                            "strength": {
                                "type": "number",
                                "description": "Optional: How much to preserve the reference image structure (0.0-1.0). Default: 0.65. Lower = more like reference, Higher = more creative freedom. Only used when reference_image_number is provided."
                            }
                        },
                        "required": ["image_number", "edit_instruction"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_speech",
                    "description": "Generate speech/voiceover from text using Runway ML text-to-speech. Use when user wants to create voiceover, narration, or spoken audio. Supports multiple voices (Rachel, Drew, Clyde, Paul, Aria, Domi, Dave). Session 81: Audio generation tools!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "text": {
                                "type": "string",
                                "description": "The text to convert to speech. Can be a phrase, sentence, or paragraph."
                            },
                            "voice": {
                                "type": "string",
                                "enum": ["Rachel", "Drew", "Clyde", "Paul", "Aria", "Domi", "Dave"],
                                "description": "Voice to use for speech generation. Rachel (female, warm), Drew (male, clear), Clyde (male, deep), Paul (male, friendly), Aria (female, professional), Domi (female, energetic), Dave (male, casual). Default: Rachel"
                            }
                        },
                        "required": ["text"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_sound_effect",
                    "description": "Generate sound effects from text description using Runway ML. Use when user wants to create sound effects, audio atmospheres, or background sounds. Can generate any sound described in text (thunder, door slam, whoosh, water flowing, etc.). Session 81: Audio generation tools!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "Detailed description of the sound effect to generate. Be specific! Examples: 'thunder clap', 'heavy door slam', 'ocean waves crashing', 'whoosh sound', 'car engine starting'"
                            },
                            "duration": {
                                "type": "number",
                                "description": "Duration of the sound effect in seconds (0.5 to 30). Default: 5"
                            }
                        },
                        "required": ["description"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "apply_color_grade",
                    "description": "Apply professional color grading to a video using DaVinci Resolve. Use when user wants to make their video look more cinematic, vibrant, warm, cool, vintage, or noir. This creates a NEW video with the color grade applied. Session 84: DaVinci Agent-based video editing!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "video_selection": {
                                "type": "string",
                                "enum": ["last", "video_id"],
                                "description": "Which video to color grade. 'last' = most recent video. Default: 'last'"
                            },
                            "video_id": {
                                "type": "string",
                                "description": "Video ID if video_selection is 'video_id'. Optional."
                            },
                            "style": {
                                "type": "string",
                                "enum": ["cinematic", "vibrant", "vintage", "noir", "warm", "cool"],
                                "description": "Color grading style. cinematic=teal/orange Hollywood look, vibrant=boosted saturation, vintage=film-like warm tones, noir=black & white high contrast, warm=golden hour, cool=blue/teal tones. Default: cinematic"
                            },
                            "intensity": {
                                "type": "number",
                                "description": "How strong the color grade is (0.0-1.0). 0.3=subtle, 0.5=balanced, 0.7=strong, 1.0=maximum. Default: 0.5"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "edit_video",
                    "description": "Perform multiple editing operations on videos using DaVinci Resolve. This is the master video editing tool that can chain videos, add text overlays, apply color grading, and mix audio all in one go. Use this when user wants to do multiple edits at once (e.g., 'chain my videos, add a title, and color grade them'). Session 84: DaVinci Agent-based multi-operation editing! IMPORTANT: When user says 'chain videos 5 and 8', use video_numbers=[5, 8] parameter!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "video_selection": {
                                "type": "string",
                                "enum": ["last", "last_2", "last_3", "last_4", "last_5", "specific_ids"],
                                "description": "Which videos to edit. Use 'specific_ids' when user specifies video numbers (e.g., 'chain videos 5 and 8'). Default: 'last'. NOTE: When user provides video numbers, you can omit this field and just use video_numbers parameter!"
                            },
                            "video_numbers": {
                                "type": "array",
                                "items": {"type": "number"},
                                "description": "Session 84: Video numbers to edit (e.g., [5, 8] for 'chain videos 5 and 8'). Backend automatically converts numbers to video IDs. EASIEST way to reference specific videos! Example: user says 'chain videos 5 and 8' → video_numbers=[5, 8]"
                            },
                            "video_ids": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Specific video UUIDs to edit (advanced usage). For most cases, use video_numbers instead! Example: ['uuid1', 'uuid2']"
                            },
                            "operations": {
                                "type": "array",
                                "description": "List of editing operations to perform in sequence. Operations: {type:'chain'}, {type:'text', text:'Hello', position:'center', start:0, duration:3}, {type:'color_grade', style:'cinematic', intensity:0.7}, {type:'audio', volume:0.3}",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["chain", "text", "color_grade", "audio"],
                                            "description": "Operation type"
                                        },
                                        "text": {
                                            "type": "string",
                                            "description": "Text to overlay (for type='text')"
                                        },
                                        "position": {
                                            "type": "string",
                                            "enum": ["center", "lower_third", "upper_third", "top", "bottom"],
                                            "description": "Text position (for type='text'). Default: center"
                                        },
                                        "start": {
                                            "type": "number",
                                            "description": "Start time in seconds (for type='text'). Default: 0"
                                        },
                                        "duration": {
                                            "type": "number",
                                            "description": "Duration in seconds (for type='text' or type='chain' transitions). Default: 3 for text, 1.0 for transitions"
                                        },
                                        "font_size": {
                                            "type": "number",
                                            "description": "Font size 36-144 (for type='text'). Default: 72"
                                        },
                                        "style": {
                                            "type": "string",
                                            "enum": ["cinematic", "vibrant", "vintage", "noir", "warm", "cool"],
                                            "description": "Color grade style (for type='color_grade'). Default: cinematic"
                                        },
                                        "intensity": {
                                            "type": "number",
                                            "description": "Color grade intensity 0.0-1.0 (for type='color_grade'). Default: 0.5"
                                        },
                                        "transition": {
                                            "type": "string",
                                            "enum": ["Cross Dissolve", "Fade", "Wipe", "Slide"],
                                            "description": "Transition type (for type='chain'). Default: Cross Dissolve"
                                        },
                                        "volume": {
                                            "type": "number",
                                            "description": "Audio volume 0.0-1.0 (for type='audio'). Default: 0.3"
                                        }
                                    },
                                    "required": ["type"]
                                }
                            },
                            "project_name": {
                                "type": "string",
                                "description": "Optional project name for DaVinci Resolve. Auto-generated if not provided."
                            }
                        },
                        "required": ["operations"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "show_recent_videos",
                    "description": "Show the user's recent videos with numbers so they can reference specific videos. Use this when user asks 'show my videos', 'list videos', 'what videos do I have', or when they need to select specific videos to edit. Session 84: Video selection enhancement!",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "count": {
                                "type": "number",
                                "description": "Number of recent videos to show (default: 10, max: 20)"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_with_options",
                    "description": "Generate 3-5 creative VARIATIONS of the SAME concept and let user pick favorite. AI learns from their choice! Works for ANY content type: logos, banners, icons, artwork, backgrounds, etc. Session 90: CreativeDirectorAgent integration. IMPORTANT: Pass a SINGLE concept prompt (e.g., 'coffee shop logo' or 'social media banner'), NOT multiple concepts. The agent will generate COUNT variations with DIFFERENT STYLES automatically for maximum variety.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "prompt": {"type": "string", "description": "SINGLE concept to generate (e.g., 'coffee shop logo', 'social media banner', 'app icon', 'background image'). Do NOT include multiple concepts or style descriptions - just the subject. CreativeDirectorAgent will add diverse styles automatically."},
                            "count": {"type": "integer", "default": 3, "description": "Number of variations to generate (3-5). Each will use DIFFERENT creative style automatically."},
                            "style": {"type": "string", "description": "CRITICAL: DO NOT PASS THIS PARAMETER unless user explicitly requests a specific style (e.g., 'make them all photographic'). For logos, banners, icons, or ANY content - OMIT THIS PARAMETER to enable automatic style diversity! The agent will intelligently choose 3 DIFFERENT styles from 69 options. Passing this parameter forces ALL variations to use the SAME style (defeats the purpose!). Only use if user says 'make them all [style]'."},
                            "model": {"type": "string", "enum": ["core", "sdxl", "sd3", "ultra"], "description": "AI model. sdxl recommended."}
                        },
                        "required": ["prompt"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "save_as_template",
                    "description": "Save image as reusable template for exact reproduction. Stores seed for perfect consistency! Session 90: TemplateManagerAgent integration. Use the UUID from Copy ID button (e.g. '351a3cf0-66c9-4cdc-990d-b4172e725b9d').",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "image_id": {"type": "string", "description": "Image UUID (from Copy ID button)"},
                            "template_name": {"type": "string", "description": "Name for template"},
                            "tags": {"type": "array", "items": {"type": "string"}, "description": "Tags like ['logo', 'coffee']"}
                        },
                        "required": ["image_id", "template_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "train_brand_style",
                    "description": "Train FLUX LoRA on brand aesthetic. Takes 30-60 min but enables perfect brand consistency with trigger word. Session 90: BrandStyleAgent integration. Use UUIDs from Copy ID button.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "brand_name": {"type": "string", "description": "Brand name"},
                            "image_ids": {"type": "array", "items": {"type": "string"}, "description": "5-10 image UUIDs (from Copy ID button)"},
                            "auto_submit": {"type": "boolean", "default": False, "description": "Start training immediately?"}
                        },
                        "required": ["brand_name", "image_ids"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "refine_image",
                    "description": "Refine image with natural language: 'make it bigger', 'change to blue', 'add more contrast', etc. Session 90: IterationAgent integration. Use the UUID from Copy ID button.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "image_id": {"type": "string", "description": "Image UUID (from Copy ID button)"},
                            "refinement_request": {"type": "string", "description": "Natural language refinement"}
                        },
                        "required": ["image_id", "refinement_request"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_codebase",
                    "description": "Ask the CTO Agent to analyze a feature or part of the codebase. Session 98: Read-only analysis. Returns comprehensive analysis with implementation details, dependencies, potential improvements, and risk areas.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "feature_name": {
                                "type": "string",
                                "description": "Name of feature to analyze (e.g., 'AI Assistant voice commands', 'Video generation pipeline', 'Agent orchestration')"
                            },
                            "scope": {
                                "type": "string",
                                "enum": ["feature", "integration", "agent", "full_system"],
                                "description": "Scope of analysis: 'feature' for specific feature, 'integration' for API integration, 'agent' for agent system, 'full_system' for platform-wide",
                                "default": "feature"
                            }
                        },
                        "required": ["feature_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "plan_implementation",
                    "description": "Ask the CTO Agent to create a detailed implementation plan. Session 98: PLANNING ONLY - does NOT execute changes. Returns step-by-step plan with code snippets, testing strategy, and documentation updates.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "description": {
                                "type": "string",
                                "description": "What to implement (e.g., 'Add rate limiting to all API endpoints', 'Create new agent for X', 'Refactor Y for performance')"
                            },
                            "approach": {
                                "type": "string",
                                "description": "Implementation approach (e.g., 'decorator_pattern', 'new_agent', 'refactor', 'api_integration')"
                            },
                            "files_to_modify": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Optional: Specific files to modify (e.g., ['core/views_image.py', 'agents/new_agent.py'])"
                            }
                        },
                        "required": ["description", "approach"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_documentation",
                    "description": "Ask the CTO Agent to analyze documentation coverage and identify gaps. Session 98: Read-only analysis. Returns recommendations for docs to create/update but does NOT modify files.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "scope": {
                                "type": "string",
                                "enum": ["changed_files", "all_agents", "all_features", "full"],
                                "description": "Documentation scope: 'changed_files' for recent changes, 'all_agents' for agent docs, 'all_features' for feature docs, 'full' for complete platform",
                                "default": "all_features"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_roadmap",
                    "description": "Ask the COO Agent to analyze the project roadmap and provide strategic recommendations. Session 98: Read-only analysis. Returns summary, priorities, risks, suggested tasks, and timeline.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_slug": {
                                "type": "string",
                                "description": "Optional project identifier (e.g., 'session-management', 'character-training')"
                            },
                            "feature_name": {
                                "type": "string",
                                "description": "Optional specific feature to analyze (e.g., 'AI Assistant voice commands', 'Video chaining workflow')"
                            },
                            "scope": {
                                "type": "string",
                                "enum": ["project", "feature", "platform"],
                                "description": "Analysis scope: 'project' for specific project, 'feature' for single feature, 'platform' for entire platform",
                                "default": "project"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "plan_next_sprint",
                    "description": "Ask the COO Agent to plan the next sprint with concrete tasks. Session 98: Planning only - does NOT execute tasks. Returns sprint goals, tasks, success criteria, and estimated effort.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_slug": {
                                "type": "string",
                                "description": "Optional project identifier for sprint focus"
                            },
                            "feature_name": {
                                "type": "string",
                                "description": "Optional specific feature for sprint focus"
                            },
                            "sprint_duration": {
                                "type": "string",
                                "description": "Sprint length (e.g., '2 weeks', '1 week', '3 days')",
                                "default": "2 weeks"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "analyze_risks",
                    "description": "Ask the COO Agent to identify risks, blockers, and mitigation strategies. Session 98: Read-only analysis. Returns critical risks, moderate risks, dependencies, and mitigation strategies.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "project_slug": {
                                "type": "string",
                                "description": "Optional project identifier for risk analysis"
                            },
                            "feature_name": {
                                "type": "string",
                                "description": "Optional specific feature for risk analysis"
                            },
                            "scope": {
                                "type": "string",
                                "enum": ["project", "feature", "platform"],
                                "description": "Risk analysis scope",
                                "default": "project"
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "start_executive_meeting",
                    "description": "Start an executive boardroom meeting with any combination of 8 executives (CTO, COO, Product Manager, Legal, Marketing, Strategy, HR, CFO) to discuss a topic collaboratively. Session 100: Returns meeting summary with perspectives from all selected executives, decisions, and action items. Natural language examples: 'Include CFO and Marketing' or 'All executives' or 'Technical team (CTO, Product Manager)'",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {
                                "type": "string",
                                "description": "Meeting topic or agenda (e.g., 'Pricing strategy for Q1', 'AI feature roadmap', 'Platform launch plan')"
                            },
                            "project_id": {
                                "type": "string",
                                "description": "Optional project ID for context"
                            },
                            "participants": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "enum": ["CTOAgent", "COOAgent", "ProductManagerAgent", "LegalAgent", "MarketingAgent", "StrategyAgent", "HRAgent", "CFOAgent"]
                                },
                                "description": "List of executive participants. Map natural language to agent names: CTO→CTOAgent, COO→COOAgent, Product Manager/PM→ProductManagerAgent, Legal/General Counsel→LegalAgent, Marketing/CMO→MarketingAgent, Strategy/CSO→StrategyAgent, HR/CHRO→HRAgent, CFO/Finance→CFOAgent. Default: CTO + COO",
                                "default": ["CTOAgent", "COOAgent"]
                            }
                        },
                        "required": ["topic"]
                    }
                }
            }
        ]

        # Call OpenAI GPT-5 using Chat Completions API with function calling
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

        logger.info(f"💬 Assistant chat request from {request.user.username}: '{user_message[:50]}...'")

        # Session 65: Use Chat Completions API with tools instead of Responses API
        # Use gpt-5-mini (same as Session 56) which supports function calling
        logger.info(f"🤖 Calling GPT-5-mini with {len(tools)} tools available...")

        response = client.chat.completions.create(
            model="gpt-5-mini",  # Session 56 confirmed this works with Chat Completions API
            messages=messages,
            tools=tools,
            tool_choice="auto"  # Let the model decide when to call tools
            # Note: gpt-5-mini doesn't support max_tokens parameter
        )

        # Check if the model wants to call a tool
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        logger.info(f"🔍 GPT-4o response - tool_calls: {tool_calls}, content: {response_message.content[:100] if response_message.content else 'None'}...")

        if tool_calls:
            # Model wants to execute a tool!
            logger.info(f"🔧 AI wants to call {len(tool_calls)} tool(s)")

            # Return tool call information to frontend
            # Frontend will execute the tool and show progress
            return Response({
                'tool_calls': [
                    {
                        'id': tool_call.id,
                        'name': tool_call.function.name,
                        'arguments': json.loads(tool_call.function.arguments)
                    }
                    for tool_call in tool_calls
                ],
                'model': 'gpt-5-mini',
                'user_message': user_message,
                'session_id': str(session.session_id),  # Session 96: Return session ID for tracking
                'session_title': session.title,  # Session 96: Frontend integration
                'total_images': session.total_images,  # Session 96: Frontend integration
                'total_videos': session.total_videos,  # Session 96: Frontend integration
                'total_audio': session.total_audio  # Session 96: Frontend integration
            })
        else:
            # Normal text response
            assistant_response = response_message.content

            if not assistant_response:
                logger.error(f"❌ GPT-5 returned empty response")
                assistant_response = "I apologize, but I encountered an issue generating a response. Please try rephrasing your question!"

            assistant_response = assistant_response.strip()
            logger.info(f"✅ Assistant response generated ({len(assistant_response)} chars)")

            # Session 96 Weekend Project: Store assistant response in session transcript
            update_session_transcript(session, 'assistant', assistant_response)

            return Response({
                'message': assistant_response,
                'model': 'gpt-5-mini',
                'user_message': user_message,
                'session_id': str(session.session_id),  # Session 96: Return session ID for tracking
                'session_title': session.title,  # Session 96: Frontend integration
                'total_images': session.total_images,  # Session 96: Frontend integration
                'total_videos': session.total_videos,  # Session 96: Frontend integration
                'total_audio': session.total_audio  # Session 96: Frontend integration
            })

    except Exception as e:
        logger.error(f"❌ Error in assistant chat: {str(e)}")
        return Response({
            'error': 'Sorry, I encountered an error. Please try again!',
            'details': str(e) if settings.DEBUG else None
        }, status=500)


# Apr 2026: Map legacy tool names to agent names for execute_tool routing
_AGENT_TOOL_MAP = {
    'image_editing_agent': 'ImageEditingAgent',
    'video_editing_agent': 'VideoEditingAgent',
    'video_generation_agent': 'VideoAgent',
    'three_d_generation_agent': 'ThreeDAgent',
    'character_training_agent': 'CharacterTrainingAgent',
    'coleadership_agent': 'CreativeDirectorAgent',
    'talking_character_agent': 'TalkingCharacterAgent',
    'competitor_analysis_agent': 'CompetitorAnalysisAgent',
    'customer_research_agent': 'CustomerResearchAgent',
    'brand_strategy_agent': 'BrandStrategyAgent',
    'content_strategy_agent': 'ContentStrategyAgent',
    'marketing_strategy_agent': 'MarketingStrategyAgent',
}


def _route_to_agent(user, agent_name, tool_name, parameters, project=None):
    """Route a tool call through AgentRouter instead of legacy EPA handlers."""
    from core.agent_router import AgentRouter
    if project:
        parameters['project_id'] = str(project.id)
    task = f"Execute {tool_name}: {parameters}"
    router = AgentRouter(user=user)
    result = router.route(agent_name=agent_name, task=task, context=parameters)
    return result.data if result.data else {'success': True, 'message': result.message}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def execute_tool(request):
    """
    Execute a tool called by GPT-5 function calling
    Session 65: SUPER AI EXECUTOR - Autonomous tool execution

    This endpoint receives tool execution requests from the AI assistant
    and routes them to the appropriate service (Stability AI, Runway ML,
    Serper search, spider network, email, etc.)

    Expected JSON:
    {
        "tool_name": "generate_image",
        "parameters": {
            "prompt": "disco dinosaur logo",
            "model": "sdxl",
            "style": "vector"
        }
    }

    Returns:
    {
        "success": true,
        "result": {...},  # Tool-specific result
        "tool_name": "generate_image"
    }
    """
    try:
        tool_name = request.data.get('tool_name')
        parameters = request.data.get('parameters', {})
        session_id = request.data.get('session_id')  # Session 96 Weekend Project
        project_id = request.data.get('project_id')  # Session 156: Project context support

        if not tool_name:
            return Response({
                'error': 'tool_name is required'
            }, status=400)

        logger.info(f"🔧 Executing tool: {tool_name} with params: {parameters}")

        # Session 96 Weekend Project: Get session for linking generated content
        # Session 156: Also support project_id for project context
        session = None
        project = None
        if session_id:
            session = get_or_create_session(user=request.user, session_id=session_id)
        elif project_id:
            # Get project from project_id for context
            # Session 324: Unified to PartnershipProject
            from core.models_partnership import PartnershipProject
            try:
                project = PartnershipProject.objects.get(id=project_id, user=request.user)
                logger.info(f"🔗 Tool execution in project context: {project.project_name} ({project_id})")
            except PartnershipProject.DoesNotExist:
                logger.warning(f"⚠️ Project {project_id} not found for user {request.user.username}")

        # Session 182: Inject project_id into parameters for project association
        if project_id and 'project_id' not in parameters:
            parameters['project_id'] = project_id
            logger.info(f"📁 Injected project_id into parameters: {project_id}")

        # Route to appropriate tool handler
        # Session 181: Added agent name aliases for GPT function calling compatibility
        # Session 191: Workflow Orchestration Agent - HIGHEST PRIORITY
        # Session 202: AgentRouter for unified routing (Phase 2)

        # Try router-based routing first for supported intents
        # This gradually migrates tools to the new unified agent architecture
        # Session 204: Phase 5 - Tool Consolidation (expanded tool list)
        ROUTER_ENABLED_TOOLS = {
            # Image operations through unified ImageAgent
            'upscale_image', 'remove_background', 'create_variations',
            'recolor_image', 'erase_object', 'search_and_replace',
            'creative_upscale', 'inpaint', 'outpaint',
            # Audio operations through unified AudioAgent
            'generate_speech', 'generate_sound_effect', 'add_voiceover',
            # Video operations through unified VideoAgent
            'add_text_to_video', 'add_music_to_video', 'apply_color_grade',
            'chain_videos',
            # Research operations through unified ResearchAgent (Session 203)
            'web_search', 'research_topic', 'research',
            # Training operations (Session 204)
            'character_training_agent', 'train_character', 'train_style',
            # Talking character (Session 204)
            'talking_character_agent', 'create_talking_character', 'make_image_talk',
            # Workflow operations (Session 204)
            'workflow_orchestration_agent', 'create_brand_video',
            # Leadership operations (Session 204)
            'coleadership_agent', 'strategic_review', 'create_project_from_research',
        }

        if tool_name in ROUTER_ENABLED_TOOLS:
            try:
                from core.agent_router import AgentRouter
                logger.info(f"🔀 Using AgentRouter.execute_tool for: {tool_name}")

                # Session 204: Use execute_tool for full agent routing with preference support
                result = AgentRouter.execute_tool(
                    tool_name=tool_name,
                    arguments=parameters,
                    user=request.user,
                    session=session,
                    project=project
                )

                if result.get('success', True):
                    logger.info(f"✅ Router success for {tool_name}")
                else:
                    # Fall through to legacy handling if router fails
                    logger.warning(f"⚠️ Router failed, falling back to legacy: {result.get('error')}")
                    result = None
            except Exception as e:
                logger.error(f"❌ Router error, falling back to legacy: {e}")
                result = None

            # If router succeeded, return early
            if result is not None and result.get('success', True):
                return Response({
                    'success': True,
                    'result': result,
                    'tool_name': tool_name,
                    'routed': True
                })

        # Legacy routing - will be gradually migrated to AgentRouter
        # This agent handles multi-step workflows like "research and create logos"
        if tool_name == 'workflow_orchestration_agent':
            from core.agents import WorkflowOrchestrationAgent

            agent = WorkflowOrchestrationAgent(
                user=request.user,
                project_id=parameters.get('project_id') or (str(project.id) if project else None)
            )

            result = agent.execute(
                workflow=parameters.get('workflow'),
                topic=parameters.get('topic'),
                count=parameters.get('count', 3),
                style_preferences=parameters.get('style_preferences', ''),
                user_message=parameters.get('user_message', '')  # Session 239: Pass original message
            )

        elif tool_name in ('generate_image', 'image_generation_agent'):
            result = _execute_generate_image(request.user, parameters, session=session)
        elif tool_name in ('generate_video', 'video_generation_agent'):
            # Session 267: SAFETY CHECK - Redirect logo/banner requests to image generation
            # GPT sometimes incorrectly routes these to video generation
            prompt = parameters.get('params', {}).get('prompt', '').lower()
            if 'logo' in prompt or 'banner' in prompt or 'icon' in prompt:
                logger.warning(f"⚠️ Session 267: Blocking video generation for logo/banner request. Redirecting to image generation.")
                logger.warning(f"⚠️ Original prompt: {prompt}")
                # Redirect to image generation instead
                image_params = {
                    'prompt': parameters.get('params', {}).get('prompt', ''),
                    'count': 3,
                    'params': {'width': 1024, 'height': 1024, 'quality': 'high'}
                }
                result = _execute_generate_image(request.user, image_params, session=session)
                result['redirected_from'] = 'video_generation_agent'
                result['redirect_reason'] = 'Logo/banner requests should use image generation, not video'
            else:
                result = _execute_generate_video(request.user, parameters, session=session)
        elif tool_name == 'inpaint':
            result = _execute_inpaint(request.user, parameters)
        elif tool_name == 'resize_image_for_format':
            # Session 182: Resize image for social media formats (Exact Match mode)
            result = _execute_resize_image_for_format(request.user, parameters)
        elif tool_name == 'web_search':
            result = _execute_web_search(parameters)
        elif tool_name == 'scrape_website':
            result = _execute_scrape_website(parameters)
        elif tool_name == 'send_email':
            result = _execute_send_email(request.user, parameters)
        elif tool_name == 'create_brand_video':
            result = _execute_create_brand_video(request.user, parameters)
        # Session 189: Create project from research workflow
        elif tool_name == 'create_project_from_research':
            result = _route_to_agent(request.user, 'ThinkingAgent', tool_name, parameters, project)
        # Session 189: Strategic review - co-leadership review BEFORE image generation
        elif tool_name == 'strategic_review':
            result = _execute_strategic_review(request.user, parameters)
        elif tool_name == 'chain_videos':
            result = _execute_chain_videos(request.user, parameters)
        elif tool_name == 'add_text_to_video':
            # Session 81: Route to VideoAgent
            from core.agents import get_video_agent
            video_agent = get_video_agent(user=request.user)
            result = video_agent.add_text_to_video(**parameters)
        elif tool_name == 'add_music_to_video':
            # Session 81: Route to VideoAgent (auto-queries AudioAgent)
            from core.agents import get_video_agent
            video_agent = get_video_agent(user=request.user)
            result = video_agent.add_music_to_video(**parameters)
        elif tool_name == 'apply_color_grade':
            # Session 84: Route to enhanced execution function
            result = _execute_apply_color_grade(request.user, parameters)
        elif tool_name == 'edit_video':
            # Session 84: Master orchestrator for multi-operation editing
            result = _execute_edit_video(request.user, parameters)
        elif tool_name == 'show_recent_videos':
            # Session 84: Show recent videos with numbers
            result = _execute_show_recent_videos(request.user, parameters)
        elif tool_name == 'create_character_from_prompt':
            result = _execute_create_character_from_prompt(request.user, parameters)
        elif tool_name == 'edit_character_training_image':
            result = _execute_edit_character_training_image(request.user, parameters)
        elif tool_name == 'generate_speech':
            # Session 81: Route to AudioAgent (stores state in memory)
            from core.agents import get_audio_agent
            audio_agent = get_audio_agent(user=request.user)
            result = audio_agent.generate_speech(**parameters)
        elif tool_name == 'generate_sound_effect':
            # Session 81: Route to AudioAgent (stores state in memory)
            from core.agents import get_audio_agent
            audio_agent = get_audio_agent(user=request.user)
            result = audio_agent.generate_sound_effect(**parameters)
        elif tool_name == 'audio_generation_agent':
            # Session 190: GPT sometimes calls this generic name - route to appropriate audio handler
            # But if no text is provided, return error explaining the tool wasn't needed
            text = parameters.get('text') or parameters.get('prompt') or parameters.get('message')
            if not text:
                result = {
                    'success': False,
                    'error': 'audio_generation_agent requires a "text" parameter. Did you mean to call create_project_from_research instead?',
                    'suggestion': 'For logo creation workflows, the final step should be create_project_from_research, not audio_generation_agent.'
                }
            else:
                from core.agents import get_audio_agent
                audio_agent = get_audio_agent(user=request.user)
                operation = parameters.get('operation', 'speech')
                if operation == 'sound_effect':
                    result = audio_agent.generate_sound_effect(**{k: v for k, v in parameters.items() if k != 'operation'})
                else:
                    # Default to speech generation
                    result = audio_agent.generate_speech(text=text)
        elif tool_name == 'generate_with_options':
            # Session 90: Route to WorkflowCoordinatorAgent - Multi-generation with learning
            from ai_core.agents.workflow_coordinator_agent import WorkflowCoordinatorAgent
            agent = WorkflowCoordinatorAgent(user=request.user)
            result = agent.execute_generate_with_options_workflow(
                prompt=parameters.get('prompt'),
                count=parameters.get('count', 3),
                style=parameters.get('style'),
                model=parameters.get('model'),
                session=session  # Session 96: Pass session for content linking
            )

            # Store batch_id for later reference
            if result.get('success'):
                # NOTE: batch_id stored in result for frontend reference
                logger.info(f"✅ Generated {len(result.get('options', []))} options, batch_id: {result.get('batch_id')}")

        elif tool_name == 'save_as_template':
            # Session 90: Route to WorkflowCoordinatorAgent - Template creation
            from ai_core.agents.workflow_coordinator_agent import WorkflowCoordinatorAgent
            agent = WorkflowCoordinatorAgent(user=request.user)
            result = agent.execute_save_as_template_workflow(
                image_id=parameters.get('image_id'),
                template_name=parameters.get('template_name'),
                tags=parameters.get('tags', []),
                also_add_to_references=True
            )

        elif tool_name == 'train_brand_style':
            # Session 90: Route to WorkflowCoordinatorAgent - Brand training
            from ai_core.agents.workflow_coordinator_agent import WorkflowCoordinatorAgent
            agent = WorkflowCoordinatorAgent(user=request.user)
            result = agent.execute_train_brand_style_workflow(
                brand_name=parameters.get('brand_name'),
                image_ids=parameters.get('image_ids'),
                auto_submit=parameters.get('auto_submit', False)
            )

        elif tool_name == 'refine_image':
            # Session 90: Route to IterationAgent - Natural language refinement
            from ai_core.agents.iteration_agent import IterationAgent
            agent = IterationAgent(user=request.user)
            result = agent.refine_image(
                image_id=parameters.get('image_id'),
                refinement_request=parameters.get('refinement_request')
            )

        elif tool_name == 'analyze_codebase':
            # Session 98: Route to CTOAgent - Codebase analysis (read-only)
            from core.agents.executive import CTOAgent
            cto = CTOAgent(user=request.user)
            result = cto.analyze_feature(
                feature_name=parameters.get('feature_name'),
                scope=parameters.get('scope', 'feature')
            )

        elif tool_name == 'plan_implementation':
            # Session 98: Route to CTOAgent - Implementation planning (no execution)
            from core.agents.executive import CTOAgent
            cto = CTOAgent(user=request.user)
            result = cto.implement_feature(
                description=parameters.get('description'),
                approach=parameters.get('approach'),
                files_to_modify=parameters.get('files_to_modify')
            )

        elif tool_name == 'analyze_documentation':
            # Session 98: Route to CTOAgent - Documentation analysis (read-only)
            from core.agents.executive import CTOAgent
            cto = CTOAgent(user=request.user)
            result = cto.sync_documentation(
                scope=parameters.get('scope', 'all_features')
            )

        elif tool_name == 'analyze_roadmap':
            # Session 98: Route to COOAgent - Roadmap analysis (read-only)
            from core.agents.executive import COOAgent
            coo = COOAgent(user=request.user)
            result = coo.analyze_roadmap(
                project_slug=parameters.get('project_slug'),
                feature_name=parameters.get('feature_name'),
                scope=parameters.get('scope', 'project')
            )

        elif tool_name == 'plan_next_sprint':
            # Session 98: Route to COOAgent - Sprint planning (no execution)
            from core.agents.executive import COOAgent
            coo = COOAgent(user=request.user)
            result = coo.propose_next_sprint(
                project_slug=parameters.get('project_slug'),
                feature_name=parameters.get('feature_name'),
                sprint_duration=parameters.get('sprint_duration', '2 weeks')
            )

        elif tool_name == 'analyze_risks':
            # Session 98: Route to COOAgent - Risk analysis (read-only)
            from core.agents.executive import COOAgent
            coo = COOAgent(user=request.user)
            result = coo.identify_risks(
                project_slug=parameters.get('project_slug'),
                feature_name=parameters.get('feature_name'),
                scope=parameters.get('scope', 'project')
            )

        elif tool_name == 'start_executive_meeting':
            # Session 98: Route to MeetingCoordinatorAgent - Executive boardroom meeting
            from core.agents.executive import MeetingCoordinatorAgent
            from content.models import AISession

            coordinator = MeetingCoordinatorAgent(user=request.user)

            # Start the meeting
            meeting_result = coordinator.start_meeting(
                topic=parameters.get('topic'),
                project_id=parameters.get('project_id'),
                participants=parameters.get('participants', ['CTOAgent', 'COOAgent'])
            )

            # Create a boardroom AISession to store results
            if meeting_result.get('status') == 'complete':
                session = AISession.objects.create(
                    user=request.user,
                    title=f"Boardroom: {parameters.get('topic')[:100]}",
                    session_type='boardroom',
                    meeting_topic=parameters.get('topic'),
                    participants=meeting_result.get('participants', []),
                    meeting_summary=meeting_result.get('summary', ''),
                    decisions=meeting_result.get('decisions', []),
                    action_items=meeting_result.get('action_items', []),
                    agent_responses=meeting_result.get('agent_responses', {}),
                    is_active=False,  # Meetings are one-shot
                    conversation_transcript=[{
                        'role': 'system',
                        'content': f"Executive meeting conducted: {parameters.get('topic')}"
                    }]
                )

                logger.info(f"✅ Created boardroom session: {session.session_id}")
                meeting_result['session_id'] = str(session.session_id)

                # Session 99: Create co-leadership decision + log agent recommendations
                from coleadership.services import start_decision, log_agent_recommendation
                from core.models.agents_registry import UnifiedAgentTemplate
                from content.models import CreativeProject

                # Get project if provided
                project = None
                if parameters.get('project_id'):
                    try:
                        import uuid
                        # Validate UUID format
                        project_uuid = uuid.UUID(parameters.get('project_id'))
                        project = CreativeProject.objects.get(
                            id=project_uuid,
                            user=request.user
                        )
                    except (CreativeProject.DoesNotExist, ValueError, TypeError):
                        # If UUID is invalid or project doesn't exist, just skip project linkage
                        logger.warning(f"Invalid or non-existent project_id: {parameters.get('project_id')}")

                # Create decision
                decision = start_decision(
                    project=project,
                    session=session,
                    user=request.user,
                    title=parameters.get('topic'),
                    description=meeting_result.get('summary', '')
                )

                # Log each agent's recommendation
                agent_responses = meeting_result.get('agent_responses', {})
                for agent_name, response_text in agent_responses.items():
                    try:
                        # Find agent template
                        agent_template = UnifiedAgentTemplate.objects.get(name=agent_name)

                        # Simple stance inference (can enhance later)
                        stance = 'neutral'  # Default
                        if 'recommend' in response_text.lower() or 'support' in response_text.lower():
                            stance = 'support'
                        elif 'concern' in response_text.lower() or 'risk' in response_text.lower():
                            stance = 'concern'
                        elif 'alternative' in response_text.lower():
                            stance = 'alternative'

                        # Log recommendation
                        log_agent_recommendation(
                            decision=decision,
                            agent_template=agent_template,
                            payload_dict={
                                'stance': stance,
                                'summary': response_text[:200],  # First 200 chars
                                'recommendation': response_text,
                                'risks': '',  # Can extract later
                                'alternative_paths': [],
                                'confidence': None,  # Can add later
                                'time_horizon': ''
                            }
                        )
                    except UnifiedAgentTemplate.DoesNotExist:
                        logger.warning(f"Agent template not found: {agent_name}")
                        continue

                # Add decision_id, session_id, project_id to response (Session 100: Full integration)
                meeting_result['decision_id'] = str(decision.id)
                meeting_result['session_id'] = str(session.session_id) if session else None
                meeting_result['project_id'] = str(project.id) if project else None
                logger.info(f"✅ Created co-leadership decision: {decision.id} (session: {session.session_id if session else 'none'}, project: {project.id if project else 'none'})")

            result = meeting_result

        elif tool_name in _AGENT_TOOL_MAP:
            # Legacy EPA handlers replaced with AgentRouter (Apr 2026)
            result = _route_to_agent(request.user, _AGENT_TOOL_MAP[tool_name], tool_name, parameters, project)

        else:
            return Response({
                'error': f'Unknown tool: {tool_name}'
            }, status=400)

        logger.info(f"✅ Tool {tool_name} executed successfully")

        return Response({
            'success': True,
            'result': result,
            'tool_name': tool_name
        })

    except Exception as e:
        logger.error(f"❌ Error executing tool {tool_name}: {str(e)}")
        return Response({
            'error': f'Failed to execute tool: {str(e)}',
            'details': str(e) if settings.DEBUG else None
        }, status=500)


# ========================================
# TOOL EXECUTION HANDLERS (Session 65)
# ========================================



# Session 1083 (Rigby audit): pyflakes surfaced 21 undefined names in
# this file. This view file calls a large fan-out of `_execute_*`
# helpers for image/video/3D/voice/character operations plus session
# state helpers, none of which were imported. Every tool call through
# these routes would throw NameError at dispatch time.
#
# Imports deferred to EOF so they don't trigger circular init — several
# of the target helper modules import from watermark / stability /
# openai wrappers which transitively touch core.views_image_tools.
# Keeping the imports at module level (not inside functions) so
# pyflakes can verify them without a runtime call, while still
# sidestepping the init cycle.
from core.views_image_helpers import (  # noqa: E402
    _execute_generate_image,
    _execute_generate_video,
    _execute_inpaint,
    _execute_web_search,
    _execute_scrape_website,
    _execute_send_email,
    _execute_create_brand_video,
    _execute_strategic_review,
    _execute_chain_videos,
    _execute_show_recent_videos,
    _execute_create_character_from_prompt,
    _execute_edit_character_training_image,
    _execute_edit_video,
)
from core.views_image_edit import (  # noqa: E402
    _execute_apply_color_grade,
    _execute_resize_image_for_format,
)
# Session 1083 (Rigby audit): session helpers via lazy proxy to
# views_image_misc (sibling definition of the same helpers) —
# importing from core.image_views.session triggers the image_views
# package __init__ which has a pre-existing circular dependency.
def get_or_create_session(*args, **kwargs):
    from core.views_image_misc import get_or_create_session as _f
    return _f(*args, **kwargs)

def update_session_transcript(*args, **kwargs):
    from core.views_image_misc import update_session_transcript as _f
    return _f(*args, **kwargs)

from core.views_creative_director import get_user_preferences  # noqa: E402
