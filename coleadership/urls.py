"""
Co-Leadership URL Configuration - Session 99

Simple, focused endpoints for AI-Human co-leadership decisions.
"""

from django.urls import path
from . import views

app_name = 'coleadership'

urlpatterns = [
    # Boardroom meeting start (Session 100: Part 13 - Flutter integration)
    path(
        'boardroom/start/',
        views.start_boardroom_meeting,
        name='start-boardroom-meeting'
    ),

    # Decision list and detail (Session 108)
    path(
        'decisions/',
        views.list_decisions,
        name='list-decisions'
    ),
    path(
        'decisions/<uuid:decision_id>/',
        views.get_decision_detail,
        name='get-decision-detail'
    ),

    # Delete decision (Session 180)
    path(
        'decisions/<uuid:decision_id>/delete/',
        views.delete_decision,
        name='delete-decision'
    ),

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

    # User preferences (Session 108)
    path(
        'preferences/',
        views.manage_preferences,
        name='manage-preferences'
    ),

    # Project decisions (Session 100: Part 2)
    path(
        'projects/<uuid:project_id>/decisions/',
        views.get_project_decisions,
        name='get-project-decisions'
    ),
]
