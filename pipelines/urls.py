"""
URL Configuration for Creative Pipelines API

Session 109 - Creative Pipelines v1
"""

from django.urls import path
from . import views

app_name = 'pipelines'

urlpatterns = [
    # Templates
    path('templates/', views.list_templates, name='list-templates'),

    # Runs - Combined GET (list) and POST (create) endpoint
    path('runs/<uuid:run_id>/', views.get_run_detail, name='get-run-detail'),
    path('runs/', views.runs_endpoint, name='runs'),
]
