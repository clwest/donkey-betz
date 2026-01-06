"""
Unified URL Configuration - Session 688: Redirects to React Frontend

All page routes now redirect to React. API routes remain unchanged.
"""
from django.urls import path
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout

# Import API views that should remain functional
from . import views_unified


def create_redirect(react_path, require_login=True):
    """Create a redirect view to React frontend."""
    def view(request):
        return redirect(react_path)
    if require_login:
        return login_required(view)
    return view


# Redirect views for all pages
dashboard_redirect = create_redirect('/dashboard')
income_redirect = create_redirect('/dashboard')
decisions_redirect = create_redirect('/intelligence')
opportunities_redirect = create_redirect('/dashboard')
revenue_redirect = create_redirect('/portfolio')
monetization_redirect = create_redirect('/portfolio')
learning_redirect = create_redirect('/agents')
analytics_redirect = create_redirect('/admin')
neural_orchestra_redirect = create_redirect('/agents')
control_redirect = create_redirect('/intelligence')
diagnostics_redirect = create_redirect('/admin')
ai_nexus_redirect = create_redirect('/dashboard')
sports_redirect = create_redirect('/betting')
dbao_redirect = create_redirect('/betting')
assistant_redirect = create_redirect('/assistant')
profile_redirect = create_redirect('/profile')
notifications_redirect = create_redirect('/settings')
login_page_redirect = create_redirect('/login', require_login=False)
signup_redirect = create_redirect('/login', require_login=False)


def logout_view(request):
    """Logout and redirect to React login."""
    auth_logout(request)
    return redirect('/login')


urlpatterns = [
    # Session 688: All page routes redirect to React frontend

    # Main Dashboard -> React /dashboard
    path('', dashboard_redirect, name='unified_dashboard'),
    path('dashboard/', dashboard_redirect, name='unified_dashboard_alt'),

    # Income Generation Section -> React equivalents
    path('income/', income_redirect, name='unified_income_builder'),
    path('income-builder/', income_redirect, name='unified_income_builder_alt'),
    path('decisions/', decisions_redirect, name='unified_decision_command'),
    path('decision-command/', decisions_redirect, name='unified_decision_command_alt'),
    path('opportunity-detail/', opportunities_redirect, name='opportunity_detail'),
    path('opportunities/', opportunities_redirect, name='unified_revenue_opportunities'),
    path('revenue-opportunities/', opportunities_redirect, name='unified_revenue_opportunities_alt'),
    path('revenue/', revenue_redirect, name='unified_revenue_dashboard'),
    path('revenue-dashboard/', revenue_redirect, name='unified_revenue_dashboard_alt'),
    path('monetization/', monetization_redirect, name='unified_monetization_hub'),
    path('monetization-hub/', monetization_redirect, name='unified_monetization_hub_alt'),
    path('learning/', learning_redirect, name='unified_learning_dashboard'),
    path('learning-dashboard/', learning_redirect, name='unified_learning_dashboard_alt'),

    # Analytics -> React /admin
    path('analytics/', analytics_redirect, name='unified_analytics_dashboard'),
    path('analytics-dashboard/', analytics_redirect, name='unified_analytics_dashboard_alt'),

    # AI Intelligence Section -> React equivalents
    path('neural-orchestra/', neural_orchestra_redirect, name='unified_neural_orchestra'),
    path('control/', control_redirect, name='unified_control_center'),
    path('control-center/', control_redirect, name='unified_control_center_alt'),
    path('diagnostics/', diagnostics_redirect, name='unified_diagnostic_dashboard'),
    path('diagnostic-dashboard/', diagnostics_redirect, name='unified_diagnostic_dashboard_alt'),
    path('ai-nexus/', ai_nexus_redirect, name='unified_ai_nexus'),

    # Sports & Analytics -> React /betting
    path('sports/', sports_redirect, name='sports_hub'),
    path('sports-hub/', sports_redirect, name='sports_hub_alt'),
    path('sports/betting-history/', sports_redirect, name='betting_history'),
    path('sports/odds-calculator/', sports_redirect, name='odds_calculator'),
    path('sports/live-scores/', sports_redirect, name='live_scores'),
    path('dbao/', dbao_redirect, name='dbao_dashboard'),
    path('dbao-dashboard/', dbao_redirect, name='dbao_dashboard_alt'),

    # Authentication -> React /login
    path('login/', login_page_redirect, name='login'),
    path('logout/', logout_view, name='logout'),
    path('signup/', signup_redirect, name='signup'),

    # API endpoints - KEEP THESE FUNCTIONAL
    path('api/quick-apply/', views_unified.QuickApplyAPIView.as_view(), name='api_quick_apply'),
    path('api/opportunities/', views_unified.OpportunitiesAPIView.as_view(), name='api_opportunities'),
    path('api/revenue-stats/', views_unified.RevenueStatsAPIView.as_view(), name='api_revenue_stats'),
    path('api/system-health/', views_unified.SystemHealthAPIView.as_view(), name='api_system_health'),
    path('api/spider-status/', views_unified.SpiderStatusAPIView.as_view(), name='api_spider_status'),
    path('api/analytics/data/', views_unified.analytics_api_data_proxy, name='api_analytics_data'),

    # Personal Assistant -> React /assistant
    path('assistant/', assistant_redirect, name='unified_personal_assistant'),

    # Profile Management -> React /profile
    path('profile/', profile_redirect, name='user_profile'),
    path('profile/edit/', profile_redirect, name='edit_profile'),

    # Notifications -> React /settings
    path('notifications/', notifications_redirect, name='notifications'),
    path('api/notifications/', views_unified.NotificationsAPIView.as_view(), name='api_notifications'),
]
