"""
Tool Descriptions - Central Registry for GPT Function Calling
==============================================================

Session 266: All tool/agent descriptions in one place.

These descriptions tell GPT WHEN to use each tool. They are the
"mini-prompts" that guide tool selection.

Structure:
- TOOL_DESCRIPTIONS: Main tool descriptions (what triggers each tool)
- PARAM_DESCRIPTIONS: Parameter-level descriptions for complex params
"""

from typing import Dict


# =============================================================================
# MAIN TOOL DESCRIPTIONS
# =============================================================================

TOOL_DESCRIPTIONS: Dict[str, str] = {

    # -------------------------------------------------------------------------
    # WORKFLOW & ORCHESTRATION
    # -------------------------------------------------------------------------

    "workflow_orchestration_agent": """Use this agent for COMPLETE PACKAGES requiring research + creation, OR for BUSINESS RESEARCH workflows.

DO NOT USE FOR:
- Questions asking for advice: "What style would work best?" -> Just answer, don't call any tool
- Simple creation requests: "Create a logo" -> Use image_generation_agent instead
- Single-step operations: "Upscale image 3" -> Use image_editing_agent instead

=== CREATIVE WORKFLOWS (research + images) ===
- "Research and create 3 logos for X" -> workflow='research_and_create_logos'
- "Create a complete brand identity package for X" -> workflow='brand_identity_package'
- "Make a YouTube thumbnail package for X" -> workflow='youtube_thumbnail_package'
- "Animate logo 5 into a video" -> workflow='logo_to_video', image_id='5'

=== BUSINESS RESEARCH WORKFLOWS (no images, uses spider data + GPT) ===
These are FREE - no Stability AI credits used!

- "Analyze my competitors in the X market" -> workflow='competitor_analysis'
  Deep competitor analysis with SWOT and positioning maps

- "Research customer personas for X" -> workflow='customer_personas'
  Find pain points from Reddit, build personas, extract quotes

- "Do business research for starting a X company" -> workflow='business_research'
  Full research: market trends + competitors + customers + synthesis

- "Validate my startup idea for X" -> workflow='startup_validation'
  Comprehensive validation: market opportunity, competitors, customer validation, differentiation, go/no-go

Keywords that trigger this:
- Creative: "research and create", "complete package", "brand identity", "thumbnail package"
- Business: "competitor analysis", "customer personas", "business research", "validate idea", "startup validation", "market research"

For regular creation like "create 2 cyberpunk logos", use image_generation_agent directly.""",


    # -------------------------------------------------------------------------
    # IMAGE TOOLS
    # -------------------------------------------------------------------------

    "image_generation_agent": """Generate BRAND NEW images from scratch using text prompts.

THIS IS THE PRIMARY TOOL FOR CREATING LOGOS, BANNERS, AND ALL STATIC IMAGES.

USE THIS WHEN user wants to CREATE/GENERATE/MAKE/DESIGN any image:
- LOGOS: "create a logo", "design a logo", "make a cyberpunk logo", "tech startup logo"
- BANNERS: "create banner", "make header image", "social media banner"
- AVATARS: "design avatar", "create profile picture"
- ANY STATIC IMAGE: "create illustration", "generate artwork", "make graphic"

Examples that ALWAYS use this tool:
- "Create a cyberpunk logo for my tech startup" -> image_generation_agent
- "Make 3 minimalist logos" -> image_generation_agent with count=3
- "Design a professional banner" -> image_generation_agent

Supports 80+ style presets, custom dimensions, quality levels, and multiple images (count parameter).

DO NOT USE FOR:
- Modifying existing images -> use image_editing_agent
- Creating VIDEOS -> use video_generation_agent
- Questions about styles -> just answer conversationally, no tool needed""",


    "image_editing_agent": """MODIFY EXISTING images only. Requires an existing image_id.

Operations:
- upscale: 4x resolution enhancement
- remove_background: transparent PNG
- create_variations: multiple style variations
- recolor: change colors with prompt
- search_and_replace: REMOVE objects (omit replace_prompt) OR replace with something else
- creative_upscale: 4x upscale + add creative details with prompt

Supports BATCH OPERATIONS - process multiple images at once:
- Range: "20-25"
- List: "5, 8, 12"
- Combined: "10-15, 20, 25-27"

DO NOT USE FOR creating NEW images -> use image_generation_agent instead.""",


    # -------------------------------------------------------------------------
    # VIDEO TOOLS
    # -------------------------------------------------------------------------

    "video_generation_agent": """⚠️ EXPENSIVE VIDEO TOOL - USE SPARINGLY! ⚠️

STOP! Before using this tool, ask yourself:
- Did the user EXPLICITLY ask for a VIDEO?
- Did they say "video", "animation", "animate", "moving"?
- If they said "logo", "banner", "image", "design" -> USE image_generation_agent INSTEAD!

🚫 NEVER USE FOR:
- "Create a logo" -> image_generation_agent
- "Make a cyberpunk logo" -> image_generation_agent
- "Design a banner" -> image_generation_agent
- ANY request containing "logo" -> image_generation_agent
- ANY static image request -> image_generation_agent

✅ ONLY USE WHEN user explicitly says:
- "Create a VIDEO of..."
- "Make a VIDEO showing..."
- "Animate this image into a video"
- "Generate a video clip"

Operations: generate, animate, extend, chain, lip_sync

⚠️ COSTS ~22% of monthly credits per video! Only use when specifically requested.""",


    "video_editing_agent": """Handle all video editing operations.

FREE Operations (no API cost):
- upscale: 2x or 4x quality enhancement
- apply_effect: color grading (cinematic, vibrant, vintage, noir, warm, cool)
- extract_frame: pull a still image from any timestamp
- reverse: play video backwards
- trim: cut video to specific time range
- speed_change: slow motion 0.5x or speed up 2x
- concatenate: combine multiple videos into one
- rotate_flip: rotate 90/180/270 degrees or flip horizontal/vertical
- fade: add fade in/out effects
- crop_resize: crop to region, resize dimensions, or change aspect ratio
- audio_control: adjust volume, mute, or extract audio
- picture_in_picture: overlay one video on another
- add_watermark: overlay logo/image on video
- blur_region: blur part of video for privacy/censoring

Premium Operations:
- add_text_overlay: captions/titles with timing
- apply_color_grading: DaVinci cinematic effects
- render_professional: EXPORT TO ProRes 422/ProRes 4444/DNxHD
- apply_lut: apply color LUT files
- color_grade_professional: DaVinci-style lift/gamma/gain

Supports BATCH OPERATIONS: Process multiple videos using ranges '1-3' or lists '1, 3, 5'.""",


    "talking_character_agent": """PREFERRED for 'make image talk' requests.

Create complete talking character videos from a still image and text script in ONE STEP.
Pipeline: Text-to-Speech (ElevenLabs) + Image-to-Video (Runway) + Lip Sync

WORKS WITH BOTH photorealistic AND cartoon/Pixar-style characters!

Use when user wants:
- "make image X talk and say..."
- "create talking video"
- "add speech to image"
- "animate character with voice"
- "AI spokesperson video"

IMPORTANT: When user says 'using [name] voice' or 'with [name] voice', extract that name as the voice parameter!

Cost: ~$0.60-1.00 per 10-second video.""",


    # -------------------------------------------------------------------------
    # AUDIO TOOLS
    # -------------------------------------------------------------------------

    "audio_generation_agent": """Handle all audio generation.

Operations:
- generate_voice: text-to-speech with ElevenLabs
- add_voiceover: add narration to existing video

Use this for ANY standalone audio generation request.
For talking characters (TTS + animation + lip sync), use talking_character_agent instead.""",


    # -------------------------------------------------------------------------
    # 3D TOOLS
    # -------------------------------------------------------------------------

    "three_d_generation_agent": """Convert images to 3D models using Replicate TRELLIS.

Creates downloadable GLB files for 3D printing.

Use when users want:
- "convert to 3D"
- "make 3D model"
- "3D print"
- "create 3D object"

Currently only supports 'convert' operation from existing image.""",


    # -------------------------------------------------------------------------
    # TRAINING TOOLS
    # -------------------------------------------------------------------------

    "character_training_agent": """Train a FLUX LoRA model to learn a consistent visual style.

Requires 4-10 example images with similar style/aesthetic.
Creates a reusable style model for all future generations.

Use when user wants to:
- "train project style"
- "create custom style"
- "learn my visual aesthetic"
- "make consistent style"

Perfect for brand consistency across all content.""",


    # -------------------------------------------------------------------------
    # COLLABORATION TOOLS
    # -------------------------------------------------------------------------

    "coleadership_agent": """Get collaborative opinions from AI executive team.

Team: CTO, COO, Creative Director, CFO, Data Analyst

Use when user asks:
- "what do you think"
- "should we"
- "get opinions"
- "is this a good direction"
- "thoughts on"
- "feedback on"
- "worth pursuing"
- "ask the team"

Can reference specific images/content to get opinions on style, direction, or training decisions.""",


    # -------------------------------------------------------------------------
    # RESEARCH TOOLS
    # -------------------------------------------------------------------------

    "web_search": """Search the web using Google via Serper API.

Use when user asks for:
- Current information or trends
- Research or competitor analysis
- "find out about", "search for", "look up"
- "what are the latest"

Enables the 'research and create' workflow where you can research a topic then generate content based on findings.""",


    # -------------------------------------------------------------------------
    # BUSINESS RESEARCH TOOLS (Session 293)
    # -------------------------------------------------------------------------

    "competitor_analysis_agent": """Comprehensive competitor and market analysis WITHOUT image/video generation.

Use this for BUSINESS RESEARCH requests like:
- "Research the X market for my startup"
- "Analyze competitors in X industry"
- "Who are the main competitors in X?"
- "Do a competitive analysis of X"
- "What's the competitive landscape for X?"
- "SWOT analysis for X market"

This agent provides:
- Market research with trends and insights
- Competitor identification and deep analysis
- SWOT analysis (Strengths, Weaknesses, Opportunities, Threats)
- Feature comparison across competitors
- Pricing analysis when available
- Market positioning recommendations

IMPORTANT: This is for PURE RESEARCH - no image/video generation.
Uses spider network + web search for real data.""",


    "customer_research_agent": """Customer persona and pain point research WITHOUT image/video generation.

Use this for CUSTOMER RESEARCH requests like:
- "Build customer personas for X"
- "What are customer pain points for X?"
- "Research customer needs for X market"
- "Who buys X products?"
- "What do customers complain about in X?"
- "Customer sentiment analysis for X"

This agent provides:
- 2-3 detailed customer personas with demographics
- Pain point extraction from Reddit, forums, reviews
- Customer motivations and goals
- Sentiment analysis
- Direct customer quotes and examples
- Buying behavior insights

IMPORTANT: This is for PURE RESEARCH - no image/video generation.
Uses spider network (especially Reddit) for real customer data.""",


    "brand_strategy_agent": """Comprehensive brand strategy research that READS existing project research.

⭐ BEST FOR: "Create a brand identity" or "Develop brand strategy" when INSIDE a project
that already has competitor/customer research.

Use this for BRAND STRATEGY requests like:
- "Create a brand identity for this project"
- "Develop our brand strategy"
- "What should our brand positioning be?"
- "Create brand guidelines based on our research"
- "Build a brand strategy from the competitor/customer research"

This agent:
1. READS existing project research (competitor analysis, customer research)
2. Synthesizes findings into comprehensive brand strategy
3. Provides positioning, messaging, visual direction, and actionable recommendations

Output includes:
- Brand Positioning (differentiation, market position)
- Target Audience Summary (from customer research)
- Brand Messaging Framework (taglines, value propositions)
- Visual Direction (colors, typography, imagery guidance)
- Competitive Differentiation (how to stand out)
- Actionable Next Steps

IMPORTANT: This is for STRATEGIC RESEARCH - no image/video generation.
Uses existing project research as foundation, enhances with fresh spider/web data.""",


    "strategic_review": """IMPORTANT: Call this AFTER web_search but BEFORE image_generation_agent.

Get strategic review and creative direction from the executive team (CTO, COO, Creative Director) based on research findings.

They will provide:
1. Key insights to incorporate
2. Creative direction recommendations
3. Technical considerations
4. Specific prompt suggestions for image generation

This ensures co-leadership agents guide the creative process rather than just reviewing finished work.""",


    # -------------------------------------------------------------------------
    # PROJECT TOOLS
    # -------------------------------------------------------------------------

    "create_project_from_research": """⭐ SAVE RESEARCH TO PROJECT - Use this to bundle business research into a project.

Use this AFTER completing ANY of these:
1. Business research (competitor_analysis_agent, customer_research_agent)
2. Image generation workflow (research + image generation)

This packages research, analysis, and any images into an organized project.
Images are OPTIONAL - this works for business research without any images.

TRIGGERS: 'save to project', 'create project from research', 'organize research', 'bundle research'""",


    "create_brand_video": """Create a complete brand video from concept to finished product.

Orchestrates Runway ML video generation with professional styling.
Generates 2-5 video clips that can later be chained with transitions.

Use when user wants:
- Complete brand video
- Promotional video
- Multiple video clips for a brand/project""",

}


# =============================================================================
# PARAMETER DESCRIPTIONS (for complex parameters)
# =============================================================================

PARAM_DESCRIPTIONS: Dict[str, Dict[str, str]] = {

    "workflow_orchestration_agent": {
        "workflow": "Workflow type: 'research_and_create_logos', 'youtube_thumbnail_package', 'brand_identity_package', 'product_photography_kit', 'video_thumbnail_series', 'logo_to_video'",
        "topic": "The main topic INCLUDING any character/mascot. If user mentions a specific character (donkey, owl, lion), INCLUDE it in the topic!",
        "count": "Number of images to create (1-5). Extract from 'create 3 logos' -> count=3",
        "style_preferences": "CRITICAL: Extract ANY style mentioned! Animation: 'pixar', 'disney', 'dreamworks', 'ghibli', 'anime'. Art: 'watercolor', 'cyberpunk', 'minimalist'. ALWAYS extract the style!",
        "image_id": "Image ID to animate (for logo_to_video). Can use sequential number or UUID.",
        "user_message": "CRITICAL: ALWAYS pass the EXACT original user message here! Copy-paste verbatim.",
    },

    "image_generation_agent": {
        "prompt": "Text description of the image to generate",
        "count": "Number of images (1-5). Use when user asks for multiple: 'create 3 logos' -> count=3",
        "character_model_name": "Trained style/model name. Extract if user mentions 'our brand style', 'company style', 'the trained model'. Uses FLUX + custom LoRA.",
    },

    "image_editing_agent": {
        "operation": "upscale | remove_background | create_variations | recolor | search_and_replace | creative_upscale",
        "image_id": "Single: '2' or UUID. BATCH: Range '20-25', List '5, 8, 12', Combined '10-15, 20'",
    },

    "video_generation_agent": {
        "operation": "generate | animate | extend | chain | lip_sync",
    },

    "talking_character_agent": {
        "image_id": "Character image to animate. Should show a clear face for best lip sync.",
        "text": "Script text (1-2 sentences work best for 5-10 second videos)",
        "voice": "MUST extract from user's request if they say 'using [name] voice'. Options: Rachel, Antoni, Daniel, Emily, Bella, George",
        "lipsync_model": "auto (recommended), latentsync (best for cartoon), sync_labs (best for photorealistic)",
    },

}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_tool_description(tool_name: str) -> str:
    """Get the description for a specific tool."""
    return TOOL_DESCRIPTIONS.get(tool_name, f"Tool for {tool_name} operations.")


def get_param_description(tool_name: str, param_name: str) -> str:
    """Get the description for a specific tool parameter."""
    tool_params = PARAM_DESCRIPTIONS.get(tool_name, {})
    return tool_params.get(param_name, "")


def list_available_tools() -> list:
    """List all tools with descriptions defined."""
    return list(TOOL_DESCRIPTIONS.keys())
