"""
Image Views Package
===================

Modular decomposition of image-related views from the monolithic views_image.py file.

Session 186: Created as part of Phase 3 Architecture Improvements (Task 3.2)

Original file: core/views_image.py (~13,000 lines)
This package organizes those views into logical modules:

Modules:
- session: Session management helpers (get_or_create_session, etc.)
- generation: Image generation views (gallery_generate, etc.)
- editing: Image editing views (remove_background, upscale, etc.)
- gallery: Gallery and history views (image_history, unified_gallery, etc.)
- projects: Project management views (list_projects, create_project, etc.)

Architecture:
- Each module handles a specific domain of functionality
- All modules can be imported from this package for convenience
- Original views_image.py still works (backward compatible)

Usage:
    from core.image_views import gallery_generate, remove_background
    # or
    from core.image_views.generation import gallery_generate
    from core.image_views.editing import remove_background
"""

# Re-export commonly used views for convenience

# Session management (internal helpers - extracted directly)
from core.image_views.session import (
    get_or_create_session,
    update_session_transcript,
    get_image_by_number,
    increment_session_counter,
    save_to_history,
)

# Image generation (re-exports from views_image.py)
from core.image_views.generation import (
    gallery_generate,
    generate_with_stability,
    generate_with_replicate,
    test_image_generation,
    optimize_image_prompt,
)

# Image editing (re-exports from views_image.py)
from core.image_views.editing import (
    remove_background,
    recolor_image,
    upscale_image,
    erase_object,
    inpaint_image,
    outpaint_image,
    control_sketch,
    control_structure,
)

# Gallery and history (re-exports from views_image.py)
from core.image_views.gallery import (
    image_history,
    toggle_favorite,
    delete_image,
    unified_gallery,
    session_gallery,
    list_sessions,
)

# Project management (re-exports from views_image.py)
from core.image_views.projects import (
    list_projects,
    create_project,
    get_project,
    update_project,
    delete_project,
)

__all__ = [
    # Session
    'get_or_create_session',
    'update_session_transcript',
    'get_image_by_number',
    'increment_session_counter',
    'save_to_history',
    # Generation
    'gallery_generate',
    'generate_with_stability',
    'generate_with_replicate',
    'test_image_generation',
    'optimize_image_prompt',
    # Editing
    'remove_background',
    'recolor_image',
    'upscale_image',
    'erase_object',
    'inpaint_image',
    'outpaint_image',
    'control_sketch',
    'control_structure',
    # Gallery
    'image_history',
    'toggle_favorite',
    'delete_image',
    'unified_gallery',
    'session_gallery',
    'list_sessions',
    # Projects
    'list_projects',
    'create_project',
    'get_project',
    'update_project',
    'delete_project',
]
