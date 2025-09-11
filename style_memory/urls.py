"""
Style Memory URL configuration.
"""

from django.urls import path
from . import views

app_name = 'style_memory'

urlpatterns = [
    # Main interaction endpoint
    path('', views.capture_interaction, name='capture_interaction'),
    
    # Analytics and insights
    path('insights/', views.get_insights, name='insights'),
    
    # Generation and variations
    path('generate-similar/', views.generate_similar, name='generate_similar'),
    
    # Lineage tracking
    path('lineage/<str:content_id>/', views.get_lineage, name='lineage'),
    
    # Suggestions
    path('suggestions/', views.get_suggestions, name='suggestions'),
    path('suggestions/<uuid:suggestion_id>/respond/', views.respond_to_suggestion, name='respond_suggestion'),
    
    # Style memories list
    path('memories/', views.get_style_memories, name='style_memories'),
]