"""
Dashboard URL configuration.
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('stats/', views.dashboard_stats, name='stats'),
    path('activity/', views.dashboard_activity, name='activity'),
    path('embeddings-stats/', views.embeddings_stats, name='embeddings-stats'),
]