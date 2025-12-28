"""
Unified URL Configuration
Combines AI Studio, Django/DBAO, and Sports interfaces into one unified routing system
"""
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views_unified  # We'll create this next

urlpatterns = [
    # Main Dashboard
    path('', views_unified.UnifiedDashboardView.as_view(), name='unified_dashboard'),
    path('dashboard/', views_unified.UnifiedDashboardView.as_view(), name='unified_dashboard_alt'),

    # Income Generation Section
    path('income/', views_unified.IncomeBuilderView.as_view(), name='unified_income_builder'),
    path('income-builder/', views_unified.IncomeBuilderView.as_view(), name='unified_income_builder_alt'),
    path('decisions/', views_unified.DecisionCommandView.as_view(), name='unified_decision_command'),
    path('decision-command/', views_unified.DecisionCommandView.as_view(), name='unified_decision_command_alt'),
    path('opportunity-detail/', views_unified.opportunity_detail, name='opportunity_detail'),
    path('opportunities/', views_unified.RevenueOpportunitiesView.as_view(), name='unified_revenue_opportunities'),
    path('revenue-opportunities/', views_unified.RevenueOpportunitiesView.as_view(), name='unified_revenue_opportunities_alt'),
    path('revenue/', views_unified.RevenueDashboardView.as_view(), name='unified_revenue_dashboard'),
    path('revenue-dashboard/', views_unified.RevenueDashboardView.as_view(), name='unified_revenue_dashboard_alt'),
    path('monetization/', views_unified.MonetizationHubView.as_view(), name='unified_monetization_hub'),
    path('monetization-hub/', views_unified.MonetizationHubView.as_view(), name='unified_monetization_hub_alt'),
    path('learning/', views_unified.LearningDashboardView.as_view(), name='unified_learning_dashboard'),
    path('learning-dashboard/', views_unified.LearningDashboardView.as_view(), name='unified_learning_dashboard_alt'),

    # Analytics Dashboard (Session 36)
    path('analytics/', views_unified.AnalyticsDashboardViewProxy.as_view(), name='unified_analytics_dashboard'),
    path('analytics-dashboard/', views_unified.AnalyticsDashboardViewProxy.as_view(), name='unified_analytics_dashboard_alt'),

    # AI Intelligence Section
    path('neural-orchestra/', views_unified.NeuralOrchestraView.as_view(), name='unified_neural_orchestra'),
    path('control/', views_unified.ControlCenterView.as_view(), name='unified_control_center'),
    path('control-center/', views_unified.ControlCenterView.as_view(), name='unified_control_center_alt'),
    path('diagnostics/', views_unified.DiagnosticDashboardView.as_view(), name='unified_diagnostic_dashboard'),
    path('diagnostic-dashboard/', views_unified.DiagnosticDashboardView.as_view(), name='unified_diagnostic_dashboard_alt'),
    path('ai-nexus/', views_unified.AINexusView.as_view(), name='unified_ai_nexus'),

    # Sports & Analytics Section (authenticated only)
    path('sports/', views_unified.SportsHubView.as_view(), name='sports_hub'),
    path('sports-hub/', views_unified.SportsHubView.as_view(), name='sports_hub_alt'),
    path('sports/betting-history/', views_unified.BettingHistoryView.as_view(), name='betting_history'),
    path('sports/odds-calculator/', views_unified.OddsCalculatorView.as_view(), name='odds_calculator'),
    path('sports/live-scores/', views_unified.LiveScoresView.as_view(), name='live_scores'),
    path('dbao/', views_unified.DBAODashboardView.as_view(), name='dbao_dashboard'),
    path('dbao-dashboard/', views_unified.DBAODashboardView.as_view(), name='dbao_dashboard_alt'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='unified/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='unified_dashboard'), name='logout'),
    path('signup/', views_unified.SignupView.as_view(), name='signup'),

    # API endpoints for AJAX/WebSocket support
    path('api/quick-apply/', views_unified.QuickApplyAPIView.as_view(), name='api_quick_apply'),
    path('api/opportunities/', views_unified.OpportunitiesAPIView.as_view(), name='api_opportunities'),
    path('api/revenue-stats/', views_unified.RevenueStatsAPIView.as_view(), name='api_revenue_stats'),
    path('api/system-health/', views_unified.SystemHealthAPIView.as_view(), name='api_system_health'),
    path('api/spider-status/', views_unified.SpiderStatusAPIView.as_view(), name='api_spider_status'),
    path('api/analytics/data/', views_unified.analytics_api_data_proxy, name='api_analytics_data'),

    # Personal Assistant
    path('assistant/', views_unified.PersonalAssistantView.as_view(), name='unified_personal_assistant'),

    # Profile Management
    path('profile/', views_unified.UserProfileView.as_view(), name='user_profile'),
    path('profile/edit/', views_unified.EditProfileView.as_view(), name='edit_profile'),

    # Notifications
    path('notifications/', views_unified.NotificationsView.as_view(), name='notifications'),
    path('api/notifications/', views_unified.NotificationsAPIView.as_view(), name='api_notifications'),
]

# Add WebSocket URL patterns (these are usually in routing.py but documenting here for clarity)
websocket_urlpatterns = [
    # These WebSocket endpoints are already configured in core/routing.py:
    # ws/income-builder/
    # ws/decision-command/
    # ws/revenue-opportunities/
    # ws/revenue-dashboard/
    # ws/monetization-hub/
    # ws/control-center/
    # ws/assistant/
    # ws/neural-orchestra/
]