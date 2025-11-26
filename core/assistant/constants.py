"""
Constants and Configuration for AI Assistant
=============================================

Centralized configuration values used throughout the assistant package.
"""

# Tool operation types
IMAGE_EDITING_OPERATIONS = [
    'upscale',
    'remove_background',
    'create_variations',
    'recolor',
    'search_and_replace',
    'creative_upscale',
]

VIDEO_GENERATION_OPERATIONS = [
    'generate',
    'animate',
    'extend',
    'chain',
    'lip_sync',
]

AUDIO_GENERATION_OPERATIONS = [
    'generate_voice',
    'add_voiceover',
]

THREE_D_OPERATIONS = [
    'convert',
]

# Video editing operations that support batch processing
VIDEO_EDITING_BATCH_OPERATIONS = [
    'upscale',
    'apply_effect',
    'extract_frame',
    'reverse',
    'trim',
    'speed_change',
    'rotate_flip',
    'fade',
    'crop_resize',
    'audio_control',
    'add_watermark',
    'blur_region',
    'stabilize_video',
    'add_text_animation',
    'chroma_key',
    'export_for_platform',
    'auto_caption',
    'render_professional',
    'apply_lut',
    'color_grade_professional',
]

# All video editing operations
VIDEO_EDITING_ALL_OPERATIONS = [
    'add_text_overlay',
    'apply_color_grading',
] + VIDEO_EDITING_BATCH_OPERATIONS

# ElevenLabs available voices
ELEVENLABS_VOICES = [
    'Rachel', 'Antoni', 'Bella', 'Callum', 'Charlotte',
    'Daniel', 'Domi', 'Elli', 'Emily', 'George',
    'Matilda', 'Sam',
]

# Quality presets for image generation
IMAGE_QUALITY_PRESETS = {
    'fast': 'core',
    'balanced': 'sdxl',
    'high': 'sd3',
    'premium': 'ultra',
}

# Color grading effects
COLOR_GRADING_EFFECTS = [
    'cinematic',
    'vibrant',
    'vintage',
    'noir',
    'warm',
    'cool',
]

# Professional video codecs
PROFESSIONAL_CODECS = [
    'prores_422',
    'prores_422_hq',
    'prores_4444',
    'dnxhd',
    'dnxhr_hq',
    'h264',
    'h265',
]

# Aspect ratio presets
ASPECT_RATIOS = [
    '16:9',
    '9:16',
    '1:1',
    '4:3',
    '3:4',
    '21:9',
    'square',
    'portrait',
    'landscape',
    'cinematic',
]

# Default values
DEFAULT_IMAGE_WIDTH = 1024
DEFAULT_IMAGE_HEIGHT = 1024
DEFAULT_VIDEO_DURATION = 5
DEFAULT_VOICE = 'Rachel'
DEFAULT_QUALITY = 'balanced'
DEFAULT_STYLE = 'photorealistic'
DEFAULT_LORA_SCALE = 0.8

# Context window settings
CONVERSATION_HISTORY_LIMIT = 20
MEMORY_RETRIEVAL_LIMIT = 10
EMBEDDING_SEARCH_LIMIT = 5

# Workflow types for WorkflowOrchestrationAgent (Session 191/200)
WORKFLOW_TYPES = [
    'research_and_create_logos',
    # Session 199/200: New workflows
    'youtube_thumbnail_package',   # Research + create YouTube thumbnails (1280x720)
    'brand_identity_package',      # Research + create brand identity (logo + variations)
    'product_photography_kit',     # Research + create product photography
    'video_thumbnail_series',      # Research + create consistent thumbnail series (1280x720)
    'logo_to_video',               # Animate existing logo into video with audio
]
