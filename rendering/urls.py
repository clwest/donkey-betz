"""
Rendering URLs - Session 105

API endpoints for render job management.
"""

from django.urls import path
from . import views

app_name = 'rendering'

urlpatterns = [
    # POST to create new render job
    # GET to list user's render jobs (with optional ?project_id=<uuid>)
    path('', views.list_render_jobs, name='list_render_jobs'),
    path('create/', views.create_render_job, name='create_render_job'),

    # GET render job detail by UUID
    path('<uuid:job_id>/', views.get_render_job, name='get_render_job'),
]
