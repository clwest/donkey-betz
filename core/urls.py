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
from core.intelligence_api import (
    skynet_status, live_opportunities, live_predictions,
    income_builder_analysis, income_action_plan,
    execute_action_plan_view, view_generated_file,
    monetization_opportunities, create_monetization_plan,
    content_automation_plan, track_revenue
)

# Import opportunity aggregator
from backend.api.opportunity_aggregator import get_opportunities, get_actionable
from core.views import (
    platform_status, platform_info, record_metric, health_check,
    blog_list, campaigns_list, styles_list, prompting_settings, execute_agent,
    agent_executions_list, prompt_diagnostics_dashboard, prompt_diagnostics_analyses, prompt_diagnostics_templates,
    feedback_analytics, feedback_history, feedback_submit, prompting_stats,
    assistant_context, research_books, research_documents, prompting_test,
    personal_knowledge_list, agents_discovery_stats, ebooks_list, voice_history
)
# Import agent instance views
from agents.views_instances import (
    list_instances, get_instance_status, delete_instance, delete_multiple_instances
)
from core.views_knowledge import (
    personal_knowledge_upload, personal_knowledge_delete, personal_knowledge_stats
)
# Import Intelligent Assistant with Agent Integration
from core.views_assistant_intelligent import assistant_chat_intelligent as assistant_chat
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
from core.views_profile import (
    ExtendedProfileView, ProfileSkillsView, ProfileForApplicationView
)
# Import Personal Assistant views
from core.views_personal_assistant import (
    chat_with_assistant, get_assistant_context, get_learning_summary,
    provide_feedback, reset_assistant
)
from core.views_personal_assistant_dev import chat_with_assistant_dev, get_assistant_context_dev
from core.views_assistant_bypass import assistant_chat_bypass
from core.views_assistant_minimal import chat_minimal_dev, context_minimal_dev
from core.simple_ping import ping_dev
# Import Unified Assistant
from core.views_unified_assistant import (
    unified_assistant_chat, unified_assistant_context, execute_agent_with_memory,
    get_agent_recommendations, rate_agent_execution, unified_assistant_chat_dev
)
# Import Enhanced Profile views
from core.views_enhanced_profile import (
    get_enhanced_profile, update_enhanced_profile,
    get_user_memories, get_profile_suggestions
)
from agents.views import orchestrations_list

# Import ecosystem activation views
from core.views_ecosystem_activation import (
    activate_ecosystem, ecosystem_status, get_live_opportunities,
    process_opportunity, get_agent_status, get_advisor_network, get_revenue_tracking
)

# Import migrated API views
from core.views_analytics import (
    analytics_dashboard, track_usage, track_feature_usage, cost_breakdown,
    update_budget, model_performance_analytics
)
from core.views_personal_memories import (
    search_personal_memories_api, personal_memory_stats, delete_personal_memory
)
from core.views_isolation_control import (
    start_document_isolation, isolation_task_status, stop_isolation_task,
    isolation_progress, list_active_tasks, cleanup_isolation
)
from core.views_content import (
    create_content, list_content, generate_blog_post, generate_social_media_post,
    generate_video_script, content_templates, import_file_to_memory, supported_file_formats,
    gallery_videos, gallery_list, content_library, podcasts_list
)
from core.views_video import (
    text_to_video, image_to_video, check_video_status, get_video_detail,
    video_gallery, save_video_to_gallery, test_runway_connection
)
from core.views_agent_orchestration import (
    list_agents, get_agents_by_specialization, execute_agent as execute_agent_orchestration,
    orchestrate_multi_agent_task, suggest_agent, route_task, get_agent_status, health_check_agents,
    get_agent_details, refresh_agent_discovery
)
from core.views_odds_sports import (
    convert_odds, calculate_expected_value, calculate_kelly_criterion, detect_arbitrage,
    sports_game_analysis, live_betting_opportunities, list_betting_markets,
    get_bankroll_management, get_bankroll_stats, live_odds, get_weather_data, get_injury_data,
    get_betting_intelligence, orchestrate_agent_analysis, get_game_details, get_bookmaker_analysis
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

# Import new profile management and job application system views
from core.views_profile_management import (
    ExtendedProfileView, ProfileCompletionView, ResumeUploadView,
    UserContextView, JobApplicationsView
)
from core.views_job_application_system import (
    JobOpportunityView, QuickApplyView, ApplicationStatusView
)

# Create API router
router = DefaultRouter()

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Real data endpoints for demo/recording
    path('', include('core.urls_real_data')),
    
    # Authentication endpoints (original)
    path('api/v1/auth/login/', login_view, name='auth-login'),
    path('api/auth/login/', login_view, name='auth-login-compat'),  # Backward compatibility
    path('api/v1/auth/logout/', logout_view, name='auth-logout'),
    path('api/v1/auth/user/', current_user, name='auth-current-user'),
    
    # Enhanced authentication endpoints
    path('api/v1/auth/register/', register_view, name='auth-register'),
    path('api/v1/auth/verify-email/', verify_email_view, name='auth-verify-email'),
    path('api/v1/auth/login-enhanced/', login_enhanced_view, name='auth-login-enhanced'),
    path('api/v1/auth/forgot-password/', forgot_password_view, name='auth-forgot-password'),
    path('api/v1/auth/reset-password/', reset_password_view, name='auth-reset-password'),
    path('api/v1/auth/change-password/', change_password_view, name='auth-change-password'),
    path('api/v1/auth/profile/', profile_view, name='auth-profile'),
    path('api/v1/auth/logout-enhanced/', logout_enhanced_view, name='auth-logout-enhanced'),
    path('api/v1/auth/validate-token/', validate_token_view, name='auth-validate-token'),
    path('api/v1/auth/resend-verification/', resend_verification_view, name='auth-resend-verification'),
    
    # Core platform APIs
    path('api/v1/status/', platform_status, name='platform-status'),
    path('api/v1/info/', platform_info, name='platform-info'),
    path('api/v1/metrics/', record_metric, name='record-metric'),
    path('api/v1/health/', health_check, name='health-check'),

    # Intelligence endpoints (temporary fix)
    path('api/v1/intelligence/skynet/status/', skynet_status, name='skynet-status'),
    path('api/v1/intelligence/opportunities/', live_opportunities, name='live-opportunities'),
    path('api/v1/intelligence/predictions/', live_predictions, name='live-predictions'),

    # Real Data Ecosystem Activation
    path('api/v1/ecosystem/activate/', activate_ecosystem, name='ecosystem-activate'),
    path('api/v1/ecosystem/status/', ecosystem_status, name='ecosystem-status'),
    path('api/v1/ecosystem/opportunities/', get_live_opportunities, name='ecosystem-opportunities'),
    path('api/v1/ecosystem/process/', process_opportunity, name='ecosystem-process'),
    path('api/v1/ecosystem/agents/', get_agent_status, name='ecosystem-agents'),
    path('api/v1/ecosystem/advisors/', get_advisor_network, name='ecosystem-advisors'),
    path('api/v1/ecosystem/revenue/', get_revenue_tracking, name='ecosystem-revenue'),

    # AI Income Builder - Start from $0
    path('api/v1/intelligence/income-builder/', income_builder_analysis, name='income-builder'),
    path('api/v1/intelligence/income-builder/action-plan/', income_action_plan, name='income-action-plan'),
    path('api/v1/intelligence/income-builder/execute/', execute_action_plan_view, name='execute-action-plan'),
    path('api/v1/intelligence/income-builder/file/<str:filename>/', view_generated_file, name='view-generated-file'),

    # Unified Monetization Engine
    path('api/v1/monetization/opportunities/', monetization_opportunities, name='monetization-opportunities'),
    path('api/v1/monetization/plan/', create_monetization_plan, name='create-monetization-plan'),
    path('api/v1/monetization/content-automation/', content_automation_plan, name='content-automation'),
    path('api/v1/monetization/track-revenue/', track_revenue, name='track-revenue'),

    # Opportunity Aggregator endpoints
    path('api/opportunities/', get_opportunities, name='get-opportunities'),
    path('api/opportunities/actionable/', get_actionable, name='get-actionable'),

    path('api/v1/orchestrations/', orchestrations_list, name='orchestrations-list'),
    
    # Agent execution instances endpoints
    path('api/v1/instances/', list_instances, name='agent-instances'),
    path('api/v1/instances/<str:instance_id>/', get_instance_status, name='agent-instance-status'),
    path('api/v1/instances/<str:instance_id>/delete/', delete_instance, name='agent-instance-delete'),
    path('api/v1/instances/delete-multiple/', delete_multiple_instances, name='agent-instances-delete-multiple'),
    
    path('api/v1/executions/', agent_executions_list, name='agent-executions'),
    
    # Placeholder endpoints for missing APIs
    path('api/v1/content/blog/list/', blog_list, name='blog-list'),
    # path('api/campaigns/', campaigns_list, name='campaigns'),  # Removed - using campaigns.urls instead
    path('api/v1/styles/', styles_list, name='styles-list'),
    path('api/v1/prompting/settings/', prompting_settings, name='prompting-settings'),
    path('api/v1/prompting/stats/', prompting_stats, name='prompting-stats'),
    path('api/v1/prompting/test/', prompting_test, name='prompting-test'),
    path('api/v1/execute/', execute_agent, name='execute-agent'),
    
    # Prompt diagnostics endpoints
    path('api/v1/prompt-diagnostics/dashboard/', prompt_diagnostics_dashboard, name='prompt-diagnostics-dashboard'),
    path('api/v1/prompt-diagnostics/analyses/', prompt_diagnostics_analyses, name='prompt-diagnostics-analyses'),
    path('api/v1/prompt-diagnostics/templates/', prompt_diagnostics_templates, name='prompt-diagnostics-templates'),
    
    # Feedback endpoints
    path('api/v1/feedback/submit/', feedback_submit, name='feedback-submit'),
    path('api/v1/feedback/analytics/', feedback_analytics, name='feedback-analytics'),
    path('api/v1/feedback/history/', feedback_history, name='feedback-history'),
    
    # Assistant endpoints (existing)
    path('api/v1/assistant/context/', assistant_context, name='assistant-context'),
    path('api/v1/assistant/chat/', assistant_chat, name='assistant-chat'),

    # Personal AI Assistant endpoints (new learning system)
    path('api/assistant/chat/', chat_with_assistant, name='personal-assistant-chat'),
    path('api/assistant/context/', get_assistant_context, name='personal-assistant-context'),
    path('api/assistant/learning/', get_learning_summary, name='personal-assistant-learning'),

    # Development assistant endpoints (no auth required)
    path('api/assistant/dev/chat/', chat_with_assistant_dev, name='personal-assistant-chat-dev'),
    path('api/assistant/dev/context/', get_assistant_context_dev, name='personal-assistant-context-dev'),
    path('api/assistant/minimal/chat/', chat_minimal_dev, name='personal-assistant-chat-minimal'),
    path('api/assistant/minimal/context/', context_minimal_dev, name='personal-assistant-context-minimal'),
    path('api/assistant/bypass/', assistant_chat_bypass, name='assistant-chat-bypass'),
    path('api/ping/', ping_dev, name='ping-dev'),
    path('api/assistant/feedback/', provide_feedback, name='personal-assistant-feedback'),
    path('api/assistant/reset/', reset_assistant, name='personal-assistant-reset'),

    # Unified Assistant endpoints (The One True Assistant™)
    path('api/unified/chat/', unified_assistant_chat, name='unified-assistant-chat'),
    path('api/unified/context/', unified_assistant_context, name='unified-assistant-context'),
    path('api/unified/execute-agent/', execute_agent_with_memory, name='unified-execute-agent'),
    path('api/unified/recommendations/', get_agent_recommendations, name='unified-agent-recommendations'),
    path('api/unified/rate/', rate_agent_execution, name='unified-rate-execution'),
    path('api/unified/dev/chat/', unified_assistant_chat_dev, name='unified-assistant-chat-dev'),
    
    # Research endpoints
    path('api/v1/research/books/', research_books, name='research-books'),
    path('api/v1/research/documents/', research_documents, name='research-documents'),
    
    # Personal knowledge endpoints
    path('api/v1/personal-knowledge/list/', personal_knowledge_list, name='personal-knowledge-list'),
    path('api/v1/personal-knowledge/upload/', personal_knowledge_upload, name='personal-knowledge-upload'),
    path('api/v1/personal-knowledge/<str:knowledge_id>/delete/', personal_knowledge_delete, name='personal-knowledge-delete'),
    path('api/v1/personal-knowledge/stats/', personal_knowledge_stats, name='personal-knowledge-stats'),
    
    # Personal memory endpoints (secure access)
    path('api/v1/personal-memories/search/', search_personal_memories_api, name='personal-memories-search'),
    path('api/v1/personal-memories/stats/', personal_memory_stats, name='personal-memories-stats'),
    path('api/v1/personal-memories/delete/', delete_personal_memory, name='personal-memories-delete'),
    
    # Document isolation control endpoints
    path('api/v1/isolation/start/', start_document_isolation, name='isolation-start'),
    path('api/v1/isolation/task/<str:task_id>/status/', isolation_task_status, name='isolation-task-status'),
    path('api/v1/isolation/task/<str:task_id>/stop/', stop_isolation_task, name='isolation-task-stop'),
    path('api/v1/isolation/progress/', isolation_progress, name='isolation-progress'),
    path('api/v1/isolation/tasks/', list_active_tasks, name='isolation-active-tasks'),
    path('api/v1/isolation/cleanup/', cleanup_isolation, name='isolation-cleanup'),
    
    # Agent discovery stats
    path('api/v1/agents/discovery/stats/', agents_discovery_stats, name='agents-discovery-stats'),
    
    # E-books and voice
    path('api/v1/ebooks/', ebooks_list, name='ebooks-list'),
    path('api/v1/voice/history/', voice_history, name='voice-history'),
    
    # Profile endpoints (legacy)
    path('api/v1/profile/', user_profile, name='user-profile'),
    path('api/v1/profile/stats/', profile_stats, name='profile-stats'),
    path('api/v1/profile/update/', update_profile_view, name='profile-update'),
    path('api/v1/profile/avatar/', upload_avatar_view, name='avatar-upload'),
    path('api/v1/profile/avatar/delete/', delete_avatar_view, name='avatar-delete'),
    path('api/v1/profile/avatar/generate/', generate_avatar_view, name='avatar-generate'),

    # Extended Profile Management System (NEW)
    path('api/v1/user/profile/', ExtendedProfileView.as_view(), name='extended-profile'),
    path('api/v1/user/profile/skills/', ProfileSkillsView.as_view(), name='profile-skills'),
    path('api/v1/user/profile/for-application/', ProfileForApplicationView.as_view(), name='profile-for-application'),
    path('api/profile/completion/', ProfileCompletionView.as_view(), name='profile-completion'),
    path('api/profile/resume/', ResumeUploadView.as_view(), name='resume-upload'),
    path('api/profile/context/', UserContextView.as_view(), name='user-context'),
    path('api/profile/applications/', JobApplicationsView.as_view(), name='job-applications'),

    # Enhanced Profile System with Memory (ENHANCED)
    path('api/profile/enhanced/', get_enhanced_profile, name='enhanced-profile-get'),
    path('api/profile/enhanced/update/', update_enhanced_profile, name='enhanced-profile-update'),
    path('api/profile/memories/', get_user_memories, name='user-memories'),
    path('api/profile/suggestions/', get_profile_suggestions, name='profile-suggestions'),

    # Aliases for extended profile (used by ProfessionalProfile component)
    path('api/profile/extended/', get_enhanced_profile, name='extended-profile'),
    path('api/profile/extended/update/', update_enhanced_profile, name='extended-profile-update'),

    # Job Application System (NEW)
    path('api/jobs/opportunities/', JobOpportunityView.as_view(), name='job-opportunities'),
    path('api/jobs/quick-apply/', QuickApplyView.as_view(), name='quick-apply'),
    path('api/jobs/applications/<uuid:application_id>/status/', ApplicationStatusView.as_view(), name='application-status'),
    
    # API router
    path('api/v1/', include(router.urls)),
    
    # ===== MIGRATED API ENDPOINTS =====
    
    # Analytics & Dashboard APIs (from donkey_betz core)
    path('api/v1/analytics/dashboard/', analytics_dashboard, name='analytics-dashboard'),
    path('api/v1/analytics/track-usage/', track_usage, name='track-usage'),
    path('api/v1/analytics/track-feature/', track_feature_usage, name='track-feature'),
    path('api/v1/analytics/cost-breakdown/', cost_breakdown, name='cost-breakdown'),
    path('api/v1/analytics/update-budget/', update_budget, name='update-budget'),
    path('api/v1/analytics/model-performance/', model_performance_analytics, name='model-performance'),
    
    # Content Generation APIs (from ai-content-studio)
    path('api/v1/content/create/', create_content, name='content-create'),
    path('api/v1/content/list/', list_content, name='content-list'),
    path('api/v1/content/blog/generate/', generate_blog_post, name='blog-generate'),
    path('api/v1/content/social/generate/', generate_social_media_post, name='social-generate'),
    path('api/v1/content/video/script/', generate_video_script, name='video-script'),
    path('api/v1/content/templates/', content_templates, name='content-templates'),
    
    # Video Generation endpoints (RunwayML)
    path('api/v1/video/text-to-video/', text_to_video, name='text-to-video'),
    path('api/v1/video/image-to-video/', image_to_video, name='image-to-video'),
    path('api/v1/video/status/<str:task_id>/', check_video_status, name='video-status'),
    path('api/v1/video/<uuid:video_id>/', get_video_detail, name='video-detail'),
    path('api/v1/video/gallery/', video_gallery, name='video-gallery'),
    path('api/v1/video/save/', save_video_to_gallery, name='save-video'),
    path('api/v1/video/test-runway/', test_runway_connection, name='test-runway'),
    path('api/v1/memory/import-file/', import_file_to_memory, name='import-file'),
    path('api/v1/memory/supported-formats/', supported_file_formats, name='supported-formats'),
    path('api/v1/gallery/list/', gallery_list, name='gallery-list'),
    path('api/v1/gallery/videos/', gallery_videos, name='gallery-videos'),
    path('api/v1/content/library/', content_library, name='content-library'),
    path('api/v1/podcasts/', podcasts_list, name='podcasts-list'),
    
    # Agent Orchestration APIs (from DBAO tools-manifest)
    path('api/v1/agents/list/', list_agents, name='agents-list'),
    path('api/v1/agents/by-specialization/', get_agents_by_specialization, name='agents-by-specialization'),
    # path('api/v1/agents/execute/', execute_agent_orchestration, name='agents-execute'),  # Commented out - using agents.urls version
    path('api/v1/agents/orchestrate/', orchestrate_multi_agent_task, name='agents-orchestrate'),
    path('api/v1/agents/suggest/', suggest_agent, name='agents-suggest'),
    path('api/v1/agents/route/', route_task, name='agents-route'),
    path('api/v1/agents/status/<str:instance_id>/', get_agent_status, name='agent-status'),
    path('api/v1/agents/health/', health_check_agents, name='agents-health'),
    path('api/v1/agents/<str:agent_id>/details/', get_agent_details, name='agent-details'),
    path('api/v1/agents/discovery/refresh/', refresh_agent_discovery, name='agent-discovery-refresh'),
    
    # Odds & Sports Analytics APIs (from DBAO tools-manifest)
    path('api/v1/odds/convert-odds/', convert_odds, name='odds-convert'),
    path('api/v1/odds/expected-value/', calculate_expected_value, name='expected-value'),
    path('api/v1/odds/kelly-criterion/', calculate_kelly_criterion, name='kelly-criterion'),
    path('api/v1/odds/arbitrage/', detect_arbitrage, name='arbitrage'),
    path('api/v1/sports/analyze-game/', sports_game_analysis, name='sports-analyze'),
    path('api/v1/sports/live-opportunities/', live_betting_opportunities, name='live-opportunities'),
    path('api/v1/sports/live-odds/', live_odds, name='live-odds'),
    path('api/v1/odds/markets/', list_betting_markets, name='betting-markets'),
    path('api/v1/odds/bankroll/', get_bankroll_management, name='bankroll'),

    # Game detail endpoints
    path('api/v1/games/<str:game_id>/details/', get_game_details, name='game-details'),
    path('api/v1/games/<str:game_id>/bookmaker-analysis/', get_bookmaker_analysis, name='bookmaker-analysis'),
    path('api/v1/odds/bankroll/stats/', get_bankroll_stats, name='bankroll-stats'),
    path('api/v1/sports/weather/', get_weather_data, name='weather-data'),
    path('api/v1/sports/injuries/', get_injury_data, name='injury-data'),
    path('api/v1/sports/betting-intelligence/', get_betting_intelligence, name='betting-intelligence'),
    path('api/v1/sports/orchestrate/', orchestrate_agent_analysis, name='orchestrate-agents'),
    # Add missing betting endpoints expected by verification
    path('api/v1/betting/live/', live_betting_opportunities, name='betting-live'),
    path('api/v1/betting/arbitrage/', detect_arbitrage, name='betting-arbitrage'),
    
    # ===== PHASE 2 ADVANCED FEATURES =====
    
    # Advanced RAG & Embeddings APIs
    path('api/v1/rag/upload-document/', upload_document_for_rag, name='rag-upload'),
    path('api/v1/rag/semantic-search/', semantic_search, name='semantic-search'),
    path('api/v1/rag/generate/', rag_generate, name='rag-generate'),
    path('api/v1/rag/stats/', embeddings_stats, name='rag-stats'),
    path('api/v1/knowledge/collections/create/', create_knowledge_collection, name='create-knowledge-collection'),
    path('api/v1/knowledge/collections/list/', list_knowledge_collections, name='list-knowledge-collections'),
    path('api/v1/rag/advanced-query/', advanced_rag_query, name='advanced-rag-query'),
    path('api/v1/rag/optimize/', optimize_embeddings, name='optimize-embeddings'),
    
    # Multi-LLM Provider Integration APIs
    path('api/v1/llm/providers/', available_llm_providers, name='llm-providers'),
    path('api/v1/llm/intelligent-selection/', intelligent_model_selection, name='intelligent-model-selection'),
    path('api/v1/llm/multi-model-compare/', multi_model_comparison, name='multi-model-compare'),
    path('api/v1/llm/analytics/', llm_analytics, name='llm-analytics'),
    path('api/v1/llm/preferences/', set_model_preferences, name='set-llm-preferences'),
    
    # App-specific APIs - Using standardized /api/v1/ pattern
    path('api/v1/workflows/', include('workflows.urls')),  # REAL workflows with actual agents
    path('api/v1/dashboard/', include('dashboard.urls')),  # Dashboard module
    path('api/v1/style-memory/', include('style_memory.urls')),  # Style Memory module
    path('api/v1/agents/', include('agents.urls')),  # Agent Orchestra module
    path('api/v1/sports/', include('sports.urls')),  # Sports/Betting module
    path('api/v1/content/', include('content.urls')),  # Content Generation module
    path('api/v1/self-awareness/', include('self_awareness.urls')),  # Self-Awareness module
    path('api/v1/campaigns/', include('campaigns.urls')),  # Campaigns module
    path('api/v1/mythology/', include('mythology.urls')),  # Mythology/Hallucination Review module
    path('api/v1/odds-calc/', include('odds_calc.urls')),  # Odds calculation endpoints
    path('api/v1/intelligence/', include('intelligence.urls')),  # Intelligence module with action plan execution
    path('api/v1/persistence/', include('persistence.urls')),  # Data Persistence Infrastructure

    # System Reality Self-Awareness Engine
    path('truth/', include('core.truth_urls')),  # Truth Dashboard and Reality APIs
    
    # Advanced Workflow Orchestration APIs (BACKUP/FALLBACK - these should NOT conflict now)
    path('api/v1/workflows/create-advanced/', create_advanced_workflow, name='create-advanced-workflow'),
    path('api/v1/workflows/execute-advanced/', execute_advanced_workflow, name='execute-advanced-workflow'),
    path('api/v1/workflows/execution/<str:execution_id>/status/', get_workflow_execution_status, name='workflow-execution-status'),
    path('api/v1/workflows/templates-advanced/', list_workflow_templates, name='workflow-templates-advanced'),  # RENAMED to avoid conflict
    path('api/v1/workflows/from-template/', create_workflow_from_template, name='workflow-from-template'),
    path('api/v1/workflows/analytics/', workflow_analytics, name='workflow-analytics'),
    path('api/v1/workflows/schedule/', schedule_workflow, name='schedule-workflow'),
    path('api/v1/workflows/collaborate/', workflow_collaboration, name='workflow-collaboration'),
    
    # REST framework browsable API (development only)
    path('api-auth/', include('rest_framework.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
