"""
Project Management Views
========================

Extracted from views_image.py as part of Phase 3 Architecture Improvements (Task 3.2)

Session 186: Created during modular decomposition

Contains:
- list_projects: List all user projects
- create_project: Create new project
- get_project: Get single project details
- update_project: Update project
- delete_project: Delete project
"""

# Re-export from original views_image.py for backward compatibility
# This allows gradual migration without breaking existing imports

from core.views_image import (
    list_projects,
    create_project,
    get_project,
    update_project,
    delete_project,
)

__all__ = [
    'list_projects',
    'create_project',
    'get_project',
    'update_project',
    'delete_project',
]
