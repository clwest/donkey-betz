from django.urls import path
from . import views

app_name = 'sports_betting'

urlpatterns = [
    # Main interface
    path('', views.sports_ai_betting, name='main'),

    # API endpoints
    path('api/odds/', views.api_get_odds, name='api_odds'),
    path('api/place-bet/', views.api_place_bet, name='api_place_bet'),
    path('api/ai-recommendation/', views.api_ai_recommendation, name='api_ai_recommendation'),
    path('api/agent-status/', views.api_agent_status, name='api_agent_status'),
]