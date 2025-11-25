"""
Gallery and History Views
=========================

Extracted from views_image.py as part of Phase 3 Architecture Improvements (Task 3.2)

Session 186: Created during modular decomposition

Contains:
- image_history: Get paginated image history
- toggle_favorite: Toggle image favorite status
- delete_image: Delete image from history
- unified_gallery: Unified gallery with filtering
- session_gallery: Session-specific gallery
- list_sessions: List all AI sessions
"""

# Re-export from original views_image.py for backward compatibility
# This allows gradual migration without breaking existing imports

from core.views_image import (
    image_history,
    toggle_favorite,
    delete_image,
    unified_gallery,
    session_gallery,
    list_sessions,
)

__all__ = [
    'image_history',
    'toggle_favorite',
    'delete_image',
    'unified_gallery',
    'session_gallery',
    'list_sessions',
]
