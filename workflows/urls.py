"""
URL configuration for workflows app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.workflow_list, name='workflow-list'),
    path('templates/', views.workflow_templates, name='workflow-templates'),
    path('create/', views.create_workflow, name='workflow-create'),
    path('execute/', views.execute_workflow, name='workflow-execute'),
    path('status/<str:execution_id>/', views.workflow_status, name='workflow-status'),
    path('history/', views.workflow_history, name='workflow-history'),
]