"""
URL configuration for Unified Donkey Betz Platform.

Main URL routing for the unified mega-platform.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

# Import core views
from core.views import (
    platform_status, platform_info, record_metric, health_check,
    blog_list, campaigns_list, styles_list, prompting_settings, execute_agent,
    agent_instances, prompt_diagnostics_dashboard, prompt_diagnostics_analyses,
    feedback_analytics, feedback_history, prompting_stats,
    assistant_context, research_books, research_documents,
    personal_knowledge_list, agents_discovery_stats, ebooks_list, voice_history
)
# Import RAG-enhanced assistant
from core.views_assistant_rag_enhanced import assistant_chat_enhanced as assistant_chat
from core.auth_views import login_view, logout_view, current_user, user_profile, profile_stats
from core.auth_views_enhanced import (
    register_view, verify_email_view, login_enhanced_view,
    forgot_password_view, reset_password_view, change_password_view,
    profile_view, logout_enhanced_view, validate_token_view,
    resend_verification_view
)
from core.profile_views import (
    upload_avatar_view, delete_avatar_view, update_profile_view, generate_avatar_view
)
from agents.views import orchestrations_list

# Import migrated API views
from core.views_analytics import (
    analytics_dashboard, track_usage, track_feature_usage, cost_breakdown,
    update_budget, model_performance_analytics
)
from core.views_content import (
    create_content, list_content, generate_blog_post, generate_social_media_post,
    generate_video_script, content_templates, import_file_to_memory, supported_file_formats,
    gallery_videos, gallery_list, content_library, podcasts_list
)
from core.views_video import (
    text_to_video, image_to_video, check_video_status, get_video_detail,
    video_gallery, save_video_to_gallery
)
from core.views_agent_orchestration import (
    list_agents, get_agents_by_specialization, execute_agent as execute_agent_orchestration,
    orchestrate_multi_agent_task, suggest_agent, route_task, get_agent_status, health_check_agents,
    get_agent_details, refresh_agent_discovery
)
from core.views_odds_sports import (
    convert_odds, calculate_expected_value, calculate_kelly_criterion, detect_arbitrage,
    sports_game_analysis, live_betting_opportunities, list_betting_markets,
    get_bankroll_management, get_bankroll_stats
)

# Import Phase 2 advanced features
from core.views_rag_embeddings import (
    upload_document_for_rag, semantic_search, rag_generate, embeddings_stats,
    create_knowledge_collection, list_knowledge_collections, advanced_rag_query, optimize_embeddings
)
from core.views_multi_llm import (
    available_llm_providers, intelligent_model_selection, multi_model_comparison,
    model_performance_analytics as llm_analytics, set_model_preferences
)
from core.views_advanced_workflows import (
    create_advanced_workflow, execute_advanced_workflow, get_workflow_execution_status,
    list_workflow_templates, create_workflow_from_template, workflow_analytics,
    schedule_workflow, workflow_collaboration
)

# Create API router
router = DefaultRouter()

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # Authentication endpoints (original)
    path('api/auth/login/', login_view, name='auth-login'),
    path('api/auth/logout/', logout_view, name='auth-logout'),
    path('api/auth/user/', current_user, name='auth-current-user'),
    
    # Enhanced authentication endpoints
    path('api/auth/register/', register_view, name='auth-register'),
    path('api/auth/verify-email/', verify_email_view, name='auth-verify-email'),
    path('api/auth/login-enhanced/', login_enhanced_view, name='auth-login-enhanced'),
    path('api/auth/forgot-password/', forgot_password_view, name='auth-forgot-password'),
    path('api/auth/reset-password/', reset_password_view, name='auth-reset-password'),
    path('api/auth/change-password/', change_password_view, name='auth-change-password'),
    path('api/auth/profile/', profile_view, name='auth-profile'),
    path('api/auth/logout-enhanced/', logout_enhanced_view, name='auth-logout-enhanced'),
    path('api/auth/validate-token/', validate_token_view, name='auth-validate-token'),
    path('api/auth/resend-verification/', resend_verification_view, name='auth-resend-verification'),
    
    # Core platform APIs
    path('api/status/', platform_status, name='platform-status'),
    path('api/info/', platform_info, name='platform-info'),
    path('api/metrics/', record_metric, name='record-metric'),
    path('api/health/', health_check, name='health-check'),
    path('api/orchestrations/', orchestrations_list, name='orchestrations-list'),
    path('api/instances/', agent_instances, name='agent-instances'),
    
    # Placeholder endpoints for missing APIs
    path('api/content/blog/list/', blog_list, name='blog-list'),
    # path('api/campaigns/', campaigns_list, name='campaigns'),  # Removed - using campaigns.urls instead
    path('api/styles/', styles_list, name='styles-list'),
    path('api/prompting/settings/', prompting_settings, name='prompting-settings'),
    path('api/prompting/stats/', prompting_stats, name='prompting-stats'),
    path('api/execute/', execute_agent, name='execute-agent'),
    
    # Prompt diagnostics endpoints
    path('api/prompt-diagnostics/dashboard/', prompt_diagnostics_dashboard, name='prompt-diagnostics-dashboard'),
    path('api/prompt-diagnostics/analyses/', prompt_diagnostics_analyses, name='prompt-diagnostics-analyses'),
    
    # Feedback endpoints
    path('api/feedback/analytics/', feedback_analytics, name='feedback-analytics'),
    path('api/feedback/history/', feedback_history, name='feedback-history'),
    
    # Assistant endpoints
    path('api/assistant/context/', assistant_context, name='assistant-context'),
    path('api/assistant/chat/', assistant_chat, name='assistant-chat'),
    
    # Research endpoints
    path('api/research/books/', research_books, name='research-books'),
    path('api/research/documents/', research_documents, name='research-documents'),
    
    # Personal knowledge endpoints
    path('api/personal-knowledge/list/', personal_knowledge_list, name='personal-knowledge-list'),
    
    # Agent discovery stats
    path('api/agents/discovery/stats/', agents_discovery_stats, name='agents-discovery-stats'),
    
    # E-books and voice
    path('api/ebooks/', ebooks_list, name='ebooks-list'),
    path('api/voice/history/', voice_history, name='voice-history'),
    
    # Profile endpoints
    path('api/profile/', user_profile, name='user-profile'),
    path('api/profile/stats/', profile_stats, name='profile-stats'),
    path('api/profile/update/', update_profile_view, name='profile-update'),
    path('api/profile/avatar/', upload_avatar_view, name='avatar-upload'),
    path('api/profile/avatar/delete/', delete_avatar_view, name='avatar-delete'),
    path('api/profile/avatar/generate/', generate_avatar_view, name='avatar-generate'),
    
    # API router
    path('api/v1/', include(router.urls)),
    
    # ===== MIGRATED API ENDPOINTS =====
    
    # Analytics & Dashboard APIs (from donkey_betz core)
    path('api/analytics/dashboard/', analytics_dashboard, name='analytics-dashboard'),
    path('api/analytics/track-usage/', track_usage, name='track-usage'),
    path('api/analytics/track-feature/', track_feature_usage, name='track-feature'),
    path('api/analytics/cost-breakdown/', cost_breakdown, name='cost-breakdown'),
    path('api/analytics/update-budget/', update_budget, name='update-budget'),
    path('api/analytics/model-performance/', model_performance_analytics, name='model-performance'),
    
    # Content Generation APIs (from ai-content-studio)
    path('api/content/create/', create_content, name='content-create'),
    path('api/content/list/', list_content, name='content-list'),
    path('api/content/blog/generate/', generate_blog_post, name='blog-generate'),
    path('api/content/social/generate/', generate_social_media_post, name='social-generate'),
    path('api/content/video/script/', generate_video_script, name='video-script'),
    path('api/content/templates/', content_templates, name='content-templates'),
    
    # Video Generation endpoints (RunwayML)
    path('api/video/text-to-video/', text_to_video, name='text-to-video'),
    path('api/video/image-to-video/', image_to_video, name='image-to-video'),
    path('api/video/status/<str:task_id>/', check_video_status, name='video-status'),
    path('api/video/<uuid:video_id>/', get_video_detail, name='video-detail'),
    path('api/video/gallery/', video_gallery, name='video-gallery'),
    path('api/video/save/', save_video_to_gallery, name='save-video'),
    path('api/memory/import-file/', import_file_to_memory, name='import-file'),
    path('api/memory/supported-formats/', supported_file_formats, name='supported-formats'),
    path('api/gallery/list/', gallery_list, name='gallery-list'),
    path('api/gallery/videos/', gallery_videos, name='gallery-videos'),
    path('api/content/library/', content_library, name='content-library'),
    path('api/podcasts/', podcasts_list, name='podcasts-list'),
    
    # Agent Orchestration APIs (from DBAO tools-manifest)
    path('api/agents/list/', list_agents, name='agents-list'),
    path('api/agents/by-specialization/', get_agents_by_specialization, name='agents-by-specialization'),
    path('api/agents/execute/', execute_agent_orchestration, name='agents-execute'),
    path('api/agents/orchestrate/', orchestrate_multi_agent_task, name='agents-orchestrate'),
    path('api/agents/suggest/', suggest_agent, name='agents-suggest'),
    path('api/agents/route/', route_task, name='agents-route'),
    path('api/agents/status/<str:instance_id>/', get_agent_status, name='agent-status'),
    path('api/agents/health/', health_check_agents, name='agents-health'),
    path('api/agents/<str:agent_id>/details/', get_agent_details, name='agent-details'),
    path('api/agents/discovery/refresh/', refresh_agent_discovery, name='agent-discovery-refresh'),
    
    # Odds & Sports Analytics APIs (from DBAO tools-manifest)
    path('api/v1/odds/convert-odds/', convert_odds, name='odds-convert'),
    path('api/v1/odds/expected-value/', calculate_expected_value, name='expected-value'),
    path('api/v1/odds/kelly-criterion/', calculate_kelly_criterion, name='kelly-criterion'),
    path('api/v1/odds/arbitrage/', detect_arbitrage, name='arbitrage'),
    path('api/v1/sports/analyze-game/', sports_game_analysis, name='sports-analyze'),
    path('api/v1/sports/live-opportunities/', live_betting_opportunities, name='live-opportunities'),
    path('api/v1/odds/markets/', list_betting_markets, name='betting-markets'),
    path('api/v1/odds/bankroll/', get_bankroll_management, name='bankroll'),
    path('api/v1/odds/bankroll/stats/', get_bankroll_stats, name='bankroll-stats'),
    
    # ===== PHASE 2 ADVANCED FEATURES =====
    
    # Advanced RAG & Embeddings APIs
    path('api/rag/upload-document/', upload_document_for_rag, name='rag-upload'),
    path('api/rag/semantic-search/', semantic_search, name='semantic-search'),
    path('api/rag/generate/', rag_generate, name='rag-generate'),
    path('api/rag/stats/', embeddings_stats, name='rag-stats'),
    path('api/knowledge/collections/create/', create_knowledge_collection, name='create-knowledge-collection'),
    path('api/knowledge/collections/list/', list_knowledge_collections, name='list-knowledge-collections'),
    path('api/rag/advanced-query/', advanced_rag_query, name='advanced-rag-query'),
    path('api/rag/optimize/', optimize_embeddings, name='optimize-embeddings'),
    
    # Multi-LLM Provider Integration APIs
    path('api/llm/providers/', available_llm_providers, name='llm-providers'),
    path('api/llm/intelligent-selection/', intelligent_model_selection, name='intelligent-model-selection'),
    path('api/llm/multi-model-compare/', multi_model_comparison, name='multi-model-compare'),
    path('api/llm/analytics/', llm_analytics, name='llm-analytics'),
    path('api/llm/preferences/', set_model_preferences, name='set-llm-preferences'),
    
    # Advanced Workflow Orchestration APIs
    path('api/workflows/create-advanced/', create_advanced_workflow, name='create-advanced-workflow'),
    path('api/workflows/execute-advanced/', execute_advanced_workflow, name='execute-advanced-workflow'),
    path('api/workflows/execution/<str:execution_id>/status/', get_workflow_execution_status, name='workflow-execution-status'),
    path('api/workflows/templates/', list_workflow_templates, name='workflow-templates'),
    path('api/workflows/from-template/', create_workflow_from_template, name='workflow-from-template'),
    path('api/workflows/analytics/', workflow_analytics, name='workflow-analytics'),
    path('api/workflows/schedule/', schedule_workflow, name='schedule-workflow'),
    path('api/workflows/collaborate/', workflow_collaboration, name='workflow-collaboration'),
    
    # App-specific APIs (existing modules)
    path('api/dashboard/', include('dashboard.urls')),  # Dashboard at /api/dashboard/ for compatibility
    path('api/agents/', include('agents.urls')),  # Also expose at /api/agents/ for compatibility
    path('api/v1/agents/', include('agents.urls')),
    path('api/sports/', include('sports.urls')),  # Also expose at /api/sports/ for compatibility
    path('api/v1/sports/', include('sports.urls')),
    path('api/content/', include('content.urls')),  # Also expose at /api/content/ for compatibility
    path('api/v1/content/', include('content.urls')),
    path('api/v1/self-awareness/', include('self_awareness.urls')),
    path('api/campaigns/', include('campaigns.urls')),
    path('api/workflows/', include('workflows.urls')),
    path('api/odds-calc/', include('odds_calc.urls')),  # Odds calculation endpoints
    
    # REST framework browsable API (development only)
    path('api-auth/', include('rest_framework.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
