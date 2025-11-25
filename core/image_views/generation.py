"""
Image Generation Views
======================

Extracted from views_image.py as part of Phase 3 Architecture Improvements (Task 3.2)

Session 186: Created during modular decomposition

Contains:
- gallery_generate: Main image generation endpoint
- generate_with_stability: Stability AI generation
- generate_with_replicate: Replicate API generation
- test_image_generation: Configuration test endpoint
- optimize_image_prompt: AI-powered prompt optimization
"""

# Re-export from original views_image.py for backward compatibility
# This allows gradual migration without breaking existing imports

from core.views_image import (
    gallery_generate,
    generate_with_stability,
    generate_with_replicate,
    test_image_generation,
    optimize_image_prompt,
)

__all__ = [
    'gallery_generate',
    'generate_with_stability',
    'generate_with_replicate',
    'test_image_generation',
    'optimize_image_prompt',
]
