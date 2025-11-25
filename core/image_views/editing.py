"""
Image Editing Views
===================

Extracted from views_image.py as part of Phase 3 Architecture Improvements (Task 3.2)

Session 186: Created during modular decomposition

Contains:
- remove_background: Remove image background
- recolor_image: Recolor/style transfer
- upscale_image: Image upscaling
- erase_object: Erase objects from images
- inpaint_image: Inpaint masked areas
- outpaint_image: Extend image canvas
- control_sketch: Control sketch generation
- control_structure: Structure-guided generation
"""

# Re-export from original views_image.py for backward compatibility
# This allows gradual migration without breaking existing imports

from core.views_image import (
    remove_background,
    recolor_image,
    upscale_image,
    erase_object,
    inpaint_image,
    outpaint_image,
    control_sketch,
    control_structure,
)

__all__ = [
    'remove_background',
    'recolor_image',
    'upscale_image',
    'erase_object',
    'inpaint_image',
    'outpaint_image',
    'control_sketch',
    'control_structure',
]
