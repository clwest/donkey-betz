"""
URL configuration for workflows app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.workflow_list, name='workflow-list'),
    path('templates/', views.workflow_templates, name='workflow-templates'),
]