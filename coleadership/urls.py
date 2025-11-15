"""
Co-Leadership URL Configuration - Session 99

Simple, focused endpoints for AI-Human co-leadership decisions.
"""

from django.urls import path
from . import views

app_name = 'coleadership'

urlpatterns = [
    # Human decision commit
    path(
        'decisions/<uuid:decision_id>/human_decision/',
        views.save_human_decision,
        name='save-human-decision'
    ),

    # Outcome logging
    path(
        'decisions/<uuid:decision_id>/outcome/',
        views.save_outcome,
        name='save-outcome'
    ),

    # User statistics
    path(
        'stats/',
        views.get_stats,
        name='get-stats'
    ),

    # Project decisions (Session 100: Part 2)
    path(
        'projects/<uuid:project_id>/decisions/',
        views.get_project_decisions,
        name='get-project-decisions'
    ),
]
