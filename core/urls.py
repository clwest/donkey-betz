"""
URL configuration for Unified Donkey Betz Platform.

Main URL routing for the unified mega-platform.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
 
# Session 31: Removed views_unified_v2 import - consolidated to root routes
# from core import views_unified_v2

# Import advisor API views (Session 25)
from core.views_advisor_api import advisor_consult, advisor_list, advisor_detail

# Import intelligence API views (Session 25)
from core.views_intelligence_api import (
    intelligence_activity_feed, spider_network_status, intelligence_data_quality
)

# Import core views
from core.intelligence_api import (
    skynet_status, live_opportunities, live_predictions,
    income_builder_analysis, income_action_plan,
    execute_action_plan_view, view_generated_file,
    monetization_opportunities, create_monetization_plan,
    content_automation_plan, track_revenue
)

# Import ecosystem views
from core.views_ecosystem import ecosystem_stats, ecosystem_live_feed, get_project_status, ai_building_products, code_preview

# Import visualization views
from core.views_visualization import ai_agents_visualization

# Import project builder views
from core.views_projects import (
    switch_project, build_project_module, execute_latest_code,
    get_latest_code, get_project_stats, get_agent_suggestions, apply_suggestion,
    orchestrate_real_build, get_real_agents
)
# Import project API views (Phase 3: Frontend Reality Fix)
from core.views_projects_api import (
    projects_list, project_detail, project_agents, assign_agent_to_project
)

# Import agent tracking API views (Session 120)
from core.views_agent_tracking import (
    project_agents as project_contributing_agents,
    agent_timeline,
    rate_contribution,
    mark_contribution_selected
)

# Import image/export views (Session 148/149)
from core import views_image, views_share

# Import deployment views
from core.views_deploy import (
    view_generated_files, download_project, deploy_project,
    get_recent_project, get_database_files
)

# Import auto-fix views
from core.views_auto_fix import auto_fix_code

# Import AI Training dashboard view
from core.views_ai_training import ai_job_market_dashboard

# Import agent dashboard views
from core.views_agent_dashboard import (
    agent_learning_data,
    agent_collaboration_data,
    agent_costs_data,
    system_health_data,
    learning_feed_data,
    all_agents_list
)

# Import spider dashboard views
from core.views_spider_dashboard import (
    spider_network_data,
    spider_activity_feed,
    spider_data_stats,
    execute_spider
)
from core.views_spider_data import (
    get_spider_items,
    get_spider_summary,
    mark_spider_item_processed
)

# Import learning path views
from core.views_learning_path import (
    trigger_learning_query,
    get_learning_status,
    get_agent_knowledge_map,
    get_learning_feed,
    get_agent_solutions_recent,
    get_overall_learning_status
)

# Import opportunity aggregator
from ai_core.api.opportunity_aggregator import get_opportunities, get_actionable
# Import real opportunities API
from ai_core.api.opportunities_api import opportunities_api_view
# Import freelance API
from ai_core.api.freelance_api import (
    get_freelance_opportunities,
    analyze_opportunity,
    get_pending_approvals,
    process_approval,
    get_active_projects,
    start_freelance_spider,
    project_decision,
    deploy_deliverable,
    completed_deliverables,
    deliverable_content
)
# Import AI opportunity pipeline
from ai_core.ai_opportunity_api import (
    execute_ai_opportunity_pipeline,
    get_ai_strategies,
    build_ai_project,
    get_generated_projects
)
# Import Autonomous Revenue System APIs
from ai_core.api.autonomous_system_api import (
    AutonomousSystemStartView,
    AutonomousSystemStatusView,
    AutonomousSystemPauseView,
    AutonomousSystemResumeView
)
from core.views import (
    platform_info, record_metric, health_check,
    blog_list, styles_list, prompting_settings, execute_agent,
    agent_executions_list, prompt_diagnostics_dashboard, prompt_diagnostics_analyses, prompt_diagnostics_templates,
    feedback_analytics, feedback_history, feedback_submit, prompting_stats,
    assistant_context, research_books, research_documents, prompting_test,
    personal_knowledge_list, agents_discovery_stats, ebooks_list, voice_history, llm_chat, platform_status
)
from core.views_unified_intelligence import (
    unified_intelligence_dashboard, get_unified_intelligence_data,
    implement_insight, investigate_behavior, approve_proposal, reject_proposal
)
from core.views_dashboard_stats import (
    dashboard_stats, live_agent_activity, advisor_insights
)
from core.views_public_stats import public_system_stats
# Import agent instance views
from agents.views_instances import (
    list_instances, get_instance_status, delete_instance, delete_multiple_instances
)
from core.views_knowledge import (
    personal_knowledge_upload, personal_knowledge_delete, personal_knowledge_stats
)
# Import Intelligent Assistant with Agent Integration (Session 58: Replaced with GPT-5 version from views_image)
# from core.views_assistant_intelligent import assistant_chat_intelligent as assistant_chat
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
from core.views_user_profile import (
    profile_extended, ai_configuration, agents_assigned, execute_command
)
from core.views_real_income_builder import (
    real_income_opportunities, analyze_real_opportunities
)
from core.views_income_builder import income_builder_view
from core.views_neural_orchestra import (
    neural_orchestra_view,
    ecosystem_live_feed as neural_ecosystem_feed,
    agents_stats as neural_agents_stats,
    learning_status as neural_learning_status,
    learning_feed as neural_learning_feed,
    neural_orchestra_health,
    neural_orchestra_websocket_bridge,
    neural_orchestra_debug_info
)
from core import views_portfolio
from core.views_profile import (
    ExtendedProfileView, ProfileSkillsView, ProfileForApplicationView
)
# Import Personal Assistant views
from core.views_personal_assistant import (
    chat_with_assistant, get_assistant_context, get_learning_summary,
    provide_feedback, reset_assistant, voice_to_assistant
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
# Import Unified Bridge views for REAL money-making functionality
from core.views_unified_bridge import (
    sync_user_profile, get_real_opportunities, submit_real_application,
    record_user_revenue, get_opportunity_decision, get_user_dashboard_data,
    trigger_component_sync
)
from core.views_unified_metrics import unified_platform_metrics
from core.views_unified import WebSocketDiagnosticsView
from core.views_unified_placeholders import (
    unified_assistant_chat,
    unified_assistant_context,
    execute_agent_with_memory,
    get_agent_recommendations,
    rate_agent_execution,
    unified_assistant_chat_dev
)
from core.views_learning_dashboard import (
    learning_dashboard_data, learning_updates_stream
)
from core.views_ai_learning_api import (
    baseline_knowledge, collect_data, analyze_data, synthesize_knowledge,
    learning_history, save_learning_session
)
# Import Dashboard API views for unified learning dashboard
from core.views_dashboard_api import (
    dashboard_all_data, dashboard_learning_data, dashboard_collaboration_data,
    dashboard_cost_data, dashboard_health_data, dashboard_feed_data,
    dashboard_verification_data
)
# Import Verification API views
from core.views_verification_api import (
    start_verification_session, run_baseline_test, expose_learning_material,
    run_post_learning_test, get_session_status, list_verification_sessions,
    run_quick_verification_demo
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
    update_budget, model_performance_analytics,
    # Session 36: Analytics Dashboard
    AnalyticsDashboardView, analytics_api_data,
    # Phase 1: Learning Loop Integration
    learning_stats, learning_insights
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
    gallery_videos, gallery_list, content_library, podcasts_list,
    # Phase 4: Frontend Reality Fix
    generate_email, generate_podcast_script,
    ai_image_studio  # Session 32: New AI Image Studio interface
)
from core.views_video import (
    text_to_video, image_to_video, check_video_status, get_video_detail,
    video_gallery, save_video_to_gallery, test_runway_connection,
    get_video_history, toggle_video_favorite, delete_video, increment_video_view,
    increment_video_download, video_to_video_endpoint, video_upscale_endpoint,
    character_performance_endpoint,
    # Session 154: Video Enhancement
    upscale_video, apply_video_effect,
    # Session 159: Frame Extraction, Video Reverse, Video Trim
    extract_video_frame, reverse_video, trim_video,
    # Session 160: Speed Control, Video Concatenation
    change_video_speed, concatenate_videos,
    # Session 161: DaVinci Expansion Phase 2 (5 new video editing features)
    rotate_flip_video, fade_video, crop_resize_video, audio_controls, picture_in_picture,
    # Session 163: Phase 3 - Watermark/Logo feature
    add_watermark,
    # Session 163: Phase 3 - Blur Region feature
    blur_region,
    # Session 164: Phase 3 - Video Stabilization
    stabilize_video,
    # Session 164: Phase 3 - Text Animations
    add_text_animation,
    # Session 165: Phase 3 - Green Screen / Chroma Key
    chroma_key,
    # Session 166: Export Presets
    export_for_platform,
    # Session 166: Video Transitions
    video_transition,
    # Session 166: Auto-Captioning
    auto_caption,
    # Session 175: Lip Sync & Talking Character Pipeline
    lip_sync,
    lip_sync_status,
    talking_character,
    # Session 167: DaVinci Resolve Studio Integration
    davinci_status,
    render_professional,
    apply_lut,
    color_grade_professional,
    # Session 171: ElevenLabs Audio Integration
    generate_voice_view,
    add_voiceover_view
)
# Session 66 Part 2: DaVinci Resolve video editing
# Session 72: Added text overlay and color grading endpoints
# Session 73: Added audio mixing endpoint
from core.views_davinci import (
    create_video_project_endpoint, check_davinci_status, chain_videos_simple,
    add_text_overlay_endpoint, apply_color_grading_endpoint, add_audio_to_video_endpoint
)
from core.views_image import (
    gallery_generate, test_image_generation, optimize_image_prompt,
    image_history, toggle_favorite, delete_image, batch_download_images,
    control_sketch, control_structure, control_unified, execute_workflow_step, unified_gallery, session_gallery, list_sessions, get_project_sessions, get_session_analytics, get_session_assets, delete_session, promote_session_to_project, unified_batch_download, unified_toggle_favorite,
    track_image_view, track_image_download, get_featured_examples, improve_workflow_prompt,
    list_workflow_history, get_workflow_history, toggle_workflow_favorite, save_workflow_favorite,
    list_workflow_favorites, delete_workflow_favorite, rerun_workflow,
    start_workflow_execution, complete_workflow_execution, execute_workflow_for_project, assistant_chat, transcribe_audio, execute_tool, get_user_preferences_api,
    # Session 60: Phase C.1.2 - Project Management API
    list_projects, create_project, get_project, update_project, delete_project,
    add_workflow_to_project, remove_workflow_from_project,
    # Session 61: Phase C.2.1 - Portfolio View API
    get_portfolio,
    # Session 100: Part 11 - Leadership Dashboard API
    list_executive_meetings, get_meeting_details
)
# Session 74: Character Training API
from core.views_character_training import (
    list_characters, get_character, create_character, submit_training,
    check_training_status, toggle_favorite as toggle_character_favorite,
    delete_character, training_requirements
)
# Session 90: CreativeDirectorAgent - Partnership Model
from core.views_creative_director import (
    generate_options, record_choice, get_recommendation,
    get_user_preferences, get_batch_history
)
# Session 90: Complete Agent Ecosystem
from core.views_agent_ecosystem import (
    # Template Manager
    save_as_template, generate_from_template, list_templates, delete_template,
    # Version Control
    track_generation, rate_version, list_versions, get_perfect_versions,
    # Brand Style
    create_brand_style, submit_brand_training, check_brand_training_status, list_brand_styles,
    # Reference Library
    add_reference, list_references, delete_reference,
    # Editing Orchestrator
    execute_single_edit, create_editing_workflow, execute_editing_workflow,
    # Iteration Agent
    refine_image,
    # Workflow Coordinator
    execute_workflow_generate_with_options, execute_workflow_save_as_template,
    execute_workflow_train_brand_style, execute_workflow_refine_and_perfect,
    get_ecosystem_status
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
    get_betting_intelligence, orchestrate_agent_analysis, get_orchestration_status, get_game_details,
    get_bookmaker_analysis, get_game_spider_insights
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
# Import AI Ecosystem views
from core.views_ai_ecosystem import (
    get_ecosystem_stats, get_live_learning_feed,
    get_agent_network, trigger_learning_event
)
# Import enhanced agent execution views
from core import views_agent_execution
from core import views_categorized_opportunities
from core import views_agent_work_platform
from core import views_self_development
from core.views_revenue_tracking import (
    revenue_stats_view,
    track_revenue_view,
    update_revenue_status_view,
    revenue_history_view
)
# Import Partnership views (Session 38)
from core import views_partnership

# Import enhanced learning workflow API
try:
    from enhanced_learning_workflow_api import learning_workflow_api
except ImportError:
    learning_workflow_api = None

# Create API router
router = DefaultRouter()

from core.views_diagnostics import (
    diagnostic_master_endpoint,
    test_spider_network,
    test_income_builder,
    websocket_test_page,
    diagnostic_dashboard
)

urlpatterns = [
    # UNIFIED FRONTEND - Primary routing (Session 31: Consolidated to root routes)
    # Removed duplicate /v2/ namespace - see docs/debugging-sessions/SESSION_31_URL_CONSOLIDATION_PLAN.md
    path('', include('core.urls_unified')),  # Unified platform URLs

    # Legacy homepage (will be overridden by unified dashboard)
    # path('', lambda request: render(request, 'home.html'), name='home'),

    # Django admin
    path('admin/', admin.site.urls),

    # Main dashboard pages
    path('ai-nexus/', login_required(lambda request: render(request, 'ai_nexus.html')), name='ai-nexus'),
    path('content-studio/', login_required(lambda request: render(request, 'content_studio.html')), name='content-studio'),
    path('ai-studio/', ai_image_studio, name='ai-image-studio'),  # Session 32: New AI Image Studio
    path('ai-production-hub/', login_required(lambda request: render(request, 'ai_production_hub.html')), name='ai-production-hub'),
    path('command/', login_required(lambda request: render(request, 'command_center.html')), name='command-center'),
    path('diagnostics/', login_required(lambda request: render(request, 'diagnostic_dashboard.html')), name='diagnostics'),
    path('income-builder/', income_builder_view, name='income-builder'),
    path('neural-orchestra/', neural_orchestra_view, name='neural-orchestra'),

    # Session 145: Neural Orchestra API endpoints - REAL DATA!
    path('api/neural-orchestra/ecosystem/live-feed/', neural_ecosystem_feed, name='neural-ecosystem-feed'),
    path('api/neural-orchestra/agents/stats/', neural_agents_stats, name='neural-agents-stats'),
    path('api/neural-orchestra/learning/status/', neural_learning_status, name='neural-learning-status'),
    path('api/neural-orchestra/learning/feed/', neural_learning_feed, name='neural-learning-feed'),
    path('api/neural-orchestra/health/', neural_orchestra_health, name='neural-orchestra-health'),
    path('api/neural-orchestra/websocket-config/', neural_orchestra_websocket_bridge, name='neural-websocket-config'),
    path('api/neural-orchestra/debug/', neural_orchestra_debug_info, name='neural-orchestra-debug'),

    # Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', lambda request: (logout(request), redirect('/'))[1], name='logout'),

    # Diagnostic Endpoints - Complete Backend Visibility
    path('diagnostics/', diagnostic_dashboard, name='diagnostics-dashboard'),
    path('api/diagnostics/', diagnostic_master_endpoint, name='diagnostics-master'),
    path('api/diagnostics/test-spiders/', test_spider_network, name='diagnostics-test-spiders'),
    path('api/diagnostics/test-income-builder/', test_income_builder, name='diagnostics-test-income'),
    path('diagnostics/websocket-test/', websocket_test_page, name='diagnostics-websocket-test'),
    path('diagnostics/websockets/', WebSocketDiagnosticsView.as_view(), name='websocket-diagnostics'),
    path("api/llm/chat/", llm_chat),
    # AI Building Products page (moved up to ensure it's matched first)
    path('ai-building-products/', ai_building_products, name='ai-building-products'),

    # Agent Deployment System for AI Building Products
    path('api/agent-deployment/', include('agents.urls_deployment')),

    # AI Agents Visualization page
    path('visualization/', ai_agents_visualization, name='ai-agents-visualization'),

    # Real data endpoints for demo/recording
    path('', include('core.urls_real_data')),

    # Ecosystem endpoints for visualization
    path('api/ecosystem/stats/', ecosystem_stats, name='ecosystem-stats'),
    path('api/ecosystem/live-feed/', ecosystem_live_feed, name='ecosystem-live-feed'),
    path('api/ecosystem/project-status/', get_project_status, name='project-status'),
    path('api/ecosystem/code-preview/', code_preview, name='code-preview'),

    # Project Management APIs (Phase 3: Frontend Reality Fix)
    path('api/projects/', projects_list, name='projects-list'),
    path('api/projects/<uuid:project_id>/', project_detail, name='project-detail'),
    path('api/projects/<uuid:project_id>/agents/', project_agents, name='project-agents'),
    path('api/projects/<uuid:project_id>/assign-agent/', assign_agent_to_project, name='assign-agent'),

    # Agent Tracking APIs (Session 120)
    path('api/projects/<uuid:project_id>/contributions/agents/', project_contributing_agents, name='project-contributing-agents'),
    path('api/projects/<uuid:project_id>/contributions/timeline/', agent_timeline, name='agent-timeline'),
    path('api/agent-contributions/<uuid:contribution_id>/rate/', rate_contribution, name='rate-contribution'),
    path('api/agent-contributions/<uuid:contribution_id>/select/', mark_contribution_selected, name='select-contribution'),

    # Project Builder endpoints for dynamic code generation
    path('api/projects/switch/', switch_project, name='switch-project'),
    path('api/projects/build/', build_project_module, name='build-project'),
    path('api/projects/execute/', execute_latest_code, name='execute-code'),
    path('api/projects/latest-code/', get_latest_code, name='get-latest-code'),
    path('api/projects/stats/', get_project_stats, name='project-stats'),
    path('api/projects/suggestions/', get_agent_suggestions, name='project-suggestions'),
    path('api/projects/apply-suggestion/', apply_suggestion, name='apply-suggestion'),
    path('api/projects/orchestrate-real/', orchestrate_real_build, name='orchestrate-real-build'),
    path('api/projects/real-agents/', get_real_agents, name='get-real-agents'),

    # Deployment endpoints for generated projects
    path('api/projects/<str:project_name>/files/', view_generated_files, name='view-generated-files'),
    path('api/projects/<str:project_name>/download/', download_project, name='download-project'),
    path('api/projects/deploy/', deploy_project, name='deploy-project'),
    path('api/projects/recent/', get_recent_project, name='recent-project'),
    path('api/projects/database-files/', get_database_files, name='database-files'),

    # Auto-fix endpoint for agent debugging
    path('api/projects/auto-fix/', auto_fix_code, name='auto-fix-code'),

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

    # User Profile and AI Configuration APIs
    # path('api/profile/extended/', profile_extended, name='profile-extended'),  # Commented out - using enhanced profile instead
    path('api/ai/configuration/', ai_configuration, name='ai-configuration'),
    path('api/agents/assigned/', agents_assigned, name='agents-assigned'),
    path('api/commands/execute/', execute_command, name='execute-command'),

    # Intelligence endpoints (temporary fix)
    path('api/v1/intelligence/skynet/status/', skynet_status, name='skynet-status'),
    path('api/v1/intelligence/opportunities/', live_opportunities, name='live-opportunities'),

    # Enhanced Neural Orchestra API endpoints (conditionally included)
] + ([
    # TODO: Fix learning workflow API integration
    # path('api/neural-orchestra/start-learning/', learning_workflow_api.StartLearningWorkflowView.as_view(), name='start_learning_workflow'),
    # path('api/neural-orchestra/workflow-status/<str:workflow_id>/', learning_workflow_api.WorkflowStatusView.as_view(), name='workflow_status'),
    # path('api/neural-orchestra/current-data/', learning_workflow_api.CurrentDataView.as_view(), name='current_learning_data'),
] if learning_workflow_api else []) + [
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

    # Real Income Builder APIs (with actual jobs from spiders and simulator)
    path('api/v1/intelligence/real-income-builder/', real_income_opportunities, name='real-income-builder'),
    path('api/v1/intelligence/real-income-builder/analyze/', analyze_real_opportunities, name='real-income-analyze'),

    # Portfolio Management APIs (for saving and managing project deliverables)
    path('api/v1/portfolio/projects/', views_portfolio.portfolio_projects, name='portfolio-projects'),
    path('api/v1/portfolio/projects/<str:project_id>/delete/', views_portfolio.delete_portfolio_project, name='delete-portfolio-project'),
    path('api/v1/portfolio/projects/<str:project_id>/export/', views_portfolio.export_portfolio_project, name='export-portfolio-project'),

    # Unified Monetization Engine
    path('api/v1/monetization/opportunities/', monetization_opportunities, name='monetization-opportunities'),
    path('api/v1/monetization/plan/', create_monetization_plan, name='create-monetization-plan'),
    path('api/v1/monetization/content-automation/', content_automation_plan, name='content-automation'),
    path('api/v1/monetization/track-revenue/', track_revenue, name='track-revenue'),

    # Revenue Tracking API
    path('api/v1/revenue/stats/', revenue_stats_view, name='revenue-stats'),
    path('api/v1/revenue/track/', track_revenue_view, name='revenue-track'),
    path('api/v1/revenue/<uuid:revenue_id>/update-status/', update_revenue_status_view, name='revenue-update-status'),
    path('api/v1/revenue/history/', revenue_history_view, name='revenue-history'),

    # AI Opportunity Pipeline - Spider Research to Agent Execution
    path('api/v1/ai-opportunities/execute/', execute_ai_opportunity_pipeline, name='ai-opportunities-execute'),
    path('api/v1/ai-opportunities/strategies/', get_ai_strategies, name='ai-strategies'),
    path('api/v1/ai-opportunities/build/', build_ai_project, name='ai-build-project'),
    path('api/v1/ai-opportunities/projects/', get_generated_projects, name='ai-generated-projects'),

    # Autonomous Revenue System - 30-day self-running platform
    path('api/autonomous-system/start', AutonomousSystemStartView.as_view(), name='autonomous-start'),
    path('api/autonomous-system/status', AutonomousSystemStatusView.as_view(), name='autonomous-status'),
    path('api/autonomous-system/pause', AutonomousSystemPauseView.as_view(), name='autonomous-pause'),
    path('api/autonomous-system/resume', AutonomousSystemResumeView.as_view(), name='autonomous-resume'),

    # Opportunity Aggregator endpoints
    path('api/opportunities/', get_opportunities, name='get-opportunities'),
    path('api/opportunities/actionable/', get_actionable, name='get-actionable'),

    # Proposals API endpoints
    path('api/proposals/', lambda r: __import__('core.views_proposals', fromlist=['get_proposals']).get_proposals(r), name='get-proposals'),
    path('api/proposals/stats/', lambda r: __import__('core.views_proposals', fromlist=['get_proposal_stats']).get_proposal_stats(r), name='get-proposal-stats'),
    path('api/proposals/save-consciousness/', lambda r: __import__('core.views_proposals', fromlist=['save_consciousness_proposals']).save_consciousness_proposals(r), name='save-consciousness-proposals'),
    path('api/proposals/<str:proposal_id>/approve/', lambda r, proposal_id: __import__('core.views_proposals', fromlist=['approve_proposal']).approve_proposal(r), name='approve-proposal'),
    path('api/proposals/<str:proposal_id>/reject/', lambda r, proposal_id: __import__('core.views_proposals', fromlist=['reject_proposal']).reject_proposal(r), name='reject-proposal'),
    path('api/proposals/<str:proposal_id>/execute/', lambda r, proposal_id: __import__('core.views_proposals', fromlist=['execute_proposal']).execute_proposal(r), name='execute-proposal'),

    # Spider Dashboard API endpoints
    path('api/spider/stats/', lambda r: __import__('ai_core.api.spider_api', fromlist=['SpiderStatsAPI']).SpiderStatsAPI.as_view()(r), name='spider_stats'),
    path('api/spider/data/', lambda r: __import__('ai_core.api.spider_api', fromlist=['SpiderDataAPI']).SpiderDataAPI.as_view()(r), name='spider_data'),
    path('api/opportunities/live/', lambda r: __import__('ai_core.api.spider_api', fromlist=['OpportunitiesAPI']).OpportunitiesAPI.as_view()(r), name='opportunities_api'),
    path('api/revenue/', lambda r: __import__('ai_core.api.spider_api', fromlist=['RevenueAPI']).RevenueAPI.as_view()(r), name='revenue_api'),
    path('api/agents/status/', lambda r: __import__('ai_core.api.spider_api', fromlist=['AgentStatusAPI']).AgentStatusAPI.as_view()(r), name='agent_status_api'),
    path('api/trending/', lambda r: __import__('ai_core.api.spider_api', fromlist=['TrendingContentAPI']).TrendingContentAPI.as_view()(r), name='trending_api'),

    # Agent Dashboard API endpoints
    path('api/agents/stats/', lambda r: __import__('ai_core.api.agent_api', fromlist=['AgentStatsAPI']).AgentStatsAPI.as_view()(r), name='agent_stats'),
    path('api/agents/activity/', lambda r: __import__('ai_core.api.agent_api', fromlist=['AgentActivityAPI']).AgentActivityAPI.as_view()(r), name='agent_activity'),
    path('api/agents/execute/', lambda r: __import__('ai_core.api.agent_api', fromlist=['AgentExecuteAPI']).AgentExecuteAPI.as_view()(r), name='agent_execute'),
    path('api/agents/debug-registry/', lambda r: __import__('agents.views_deployment_execute_improved', fromlist=['debug_agent_registry']).debug_agent_registry(r), name='debug_agent_registry'),
    path('api/agents/run-tests/', lambda r: __import__('agents.agent_testing_system', fromlist=['run_agent_tests']).run_agent_tests(r), name='run_agent_tests'),
    path('api/agents/test-status/', lambda r: __import__('agents.agent_testing_system', fromlist=['get_agent_test_status']).get_agent_test_status(r), name='get_agent_test_status'),
    path('agent-testing/', lambda r: __import__('django.shortcuts', fromlist=['render']).render(r, 'agent_testing_dashboard.html'), name='agent_testing_dashboard'),
    path('api/agents/connections/', lambda r: __import__('ai_core.api.agent_api', fromlist=['AgentSpiderConnectionAPI']).AgentSpiderConnectionAPI.as_view()(r), name='agent_spider_connections'),

    # Simple Agent API endpoints (without complex models)
    path('api/agents/simple/list/', lambda r: __import__('ai_core.api.agent_simple_api', fromlist=['agent_list']).agent_list(r), name='agent_simple_list'),
    path('api/agents/simple/categories/', lambda r: __import__('ai_core.api.agent_simple_api', fromlist=['agent_categories']).agent_categories(r), name='agent_simple_categories'),
    path('api/agents/execute/<str:agent_name>/', lambda r, agent_name: __import__('ai_core.api.agent_simple_api', fromlist=['execute_agent']).execute_agent(r, agent_name), name='agent_execute'),

    # Real-time opportunities for Income Builder
    path('api/v1/opportunities/live/', opportunities_api_view, name='live-opportunities-real'),

    # Freelance Pipeline API endpoints
    path('api/freelance/opportunities/', get_freelance_opportunities, name='freelance_opportunities'),
    path('api/freelance/analyze/<str:job_id>/', analyze_opportunity, name='analyze_opportunity'),
    path('api/freelance/project-decision/', project_decision, name='project_decision'),
    path('api/freelance/deploy-deliverable/', deploy_deliverable, name='deploy_deliverable'),
    path('api/freelance/completed-deliverables/', completed_deliverables, name='completed_deliverables'),
    path('api/freelance/deliverable/<str:deliverable_id>/content/', deliverable_content, name='deliverable_content'),
    path('api/freelance/approvals/', get_pending_approvals, name='pending_approvals'),
    path('api/freelance/approve/<str:approval_id>/', process_approval, name='process_approval'),
    path('api/freelance/projects/', get_active_projects, name='active_projects'),
    path('api/freelance/spider/start/', start_freelance_spider, name='start_freelance_spider'),

    # Dashboard Statistics - The Heart of Everything!
    path('api/dashboard/stats/', dashboard_stats, name='dashboard-stats'),
    path('api/dashboard/agents/', live_agent_activity, name='live-agent-activity'),
    path('api/dashboard/advisors/', advisor_insights, name='advisor-insights'),
    path('api/public/system-stats/', public_system_stats, name='public-system-stats'),

    # AI Job Market Intelligence Training Dashboard
    path('ai-job-market-dashboard/', ai_job_market_dashboard, name='ai-job-market-dashboard'),

    # Unified Intelligence Dashboard (AI Nexus Intelligence View)
    path('nexus/', unified_intelligence_dashboard, name='unified-intelligence-dashboard'),
    path('intelligence/', unified_intelligence_dashboard, name='intelligence-dashboard'),
    path('api/nexus/intelligence-data/', get_unified_intelligence_data, name='nexus-intelligence-data'),
    path('api/nexus/implement-insight/', implement_insight, name='nexus-implement-insight'),
    path('api/nexus/investigate-behavior/', investigate_behavior, name='nexus-investigate-behavior'),
    path('api/nexus/approve-proposal/', approve_proposal, name='nexus-approve-proposal'),
    path('api/nexus/reject-proposal/', reject_proposal, name='nexus-reject-proposal'),

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

    # Personal AI Assistant endpoints (Session 58: Phase B.3 - Using GPT-5)
    # Session 125: Use bypass endpoint with EnhancedPersonalAIAssistant (backend tool execution)
    path('api/assistant/chat/', assistant_chat_bypass, name='personal-assistant-chat'),
    path('api/assistant/transcribe/', transcribe_audio, name='assistant-transcribe'),  # Session 64: Voice input
    path('api/assistant/voice/', voice_to_assistant, name='personal-assistant-voice'),  # Session 113: Voice Input MVP
    path('api/executor/run-tool/', execute_tool, name='executor-run-tool'),  # Session 65: SUPER AI EXECUTOR
    path('api/assistant/preferences/', get_user_preferences_api, name='user-preferences'),  # Session 59: Phase B.4
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
    path('api/unified/metrics/', unified_platform_metrics, name='unified-metrics'),
    
    # Research endpoints
    path('api/v1/research/books/', research_books, name='research-books'),
    path('api/v1/research/documents/', research_documents, name='research-documents'),
    
    # Personal knowledge endpoints
    path('api/v1/personal-knowledge/list/', personal_knowledge_list, name='personal-knowledge-list'),
    path('api/v1/personal-knowledge/upload/', personal_knowledge_upload, name='personal-knowledge-upload'),
    path('api/v1/personal-knowledge/<str:knowledge_id>/delete/', personal_knowledge_delete, name='personal-knowledge-delete'),
    path('api/v1/personal-knowledge/stats/', personal_knowledge_stats, name='personal-knowledge-stats'),
    
    # Enhanced Agent Execution (No Celery Required!)
    path('api/v1/agents/execute-sync/', views_agent_execution.execute_agent_sync, name='agent-execute-sync'),
    path('api/v1/agents/list-executable/', views_agent_execution.list_executable_agents, name='agent-list-executable'),
    path('api/v1/agents/execution-history/', views_agent_execution.agent_execution_history, name='agent-execution-history'),
    path('api/v1/agents/test-execution/', views_agent_execution.test_agent_execution, name='agent-test-execution'),
    path('api/v1/agents/batch-execute/', views_agent_execution.execute_agent_batch, name='agent-batch-execute'),

    # Advisor API Endpoints (Session 25)
    path('api/v1/advisors/consult/', advisor_consult, name='advisor-consult'),
    path('api/v1/advisors/list/', advisor_list, name='advisor-list'),
    path('api/v1/advisors/<uuid:advisor_id>/', advisor_detail, name='advisor-detail'),

    # Intelligence Hub API Endpoints (Session 25)
    path('api/v1/intelligence/activity/', intelligence_activity_feed, name='intelligence-activity'),
    path('api/v1/intelligence/spider-status/', spider_network_status, name='spider-status'),
    path('api/v1/intelligence/data-quality/', intelligence_data_quality, name='data-quality'),

    # Categorized Opportunities with ML Pipeline
    path('api/v1/categorized-opportunities/', views_categorized_opportunities.async_categorized_opportunities_view, name='categorized-opportunities'),
    path('api/v1/select-opportunity/', views_categorized_opportunities.select_opportunity, name='select-opportunity'),
    path('api/v1/category-stats/', views_categorized_opportunities.category_stats, name='category-stats'),

    # Agent Work Platform - Where Agents Actually Make Money
    path('api/v1/agent-work-platform/', views_agent_work_platform.async_agent_work_platform_view, name='agent-work-platform'),
    path('api/v1/agent-revenue-dashboard/', views_agent_work_platform.agent_revenue_dashboard, name='agent-revenue-dashboard'),
    path('api/v1/agent-workforce-status/', views_agent_work_platform.agent_workforce_status, name='agent-workforce-status'),
    # Self-Development & Autonomous Learning APIs
    path('api/self-awareness/', views_self_development.self_awareness_api, name='self-awareness-api'),
    path('api/self-awareness/report/', views_self_development.self_awareness_report, name='self-awareness-report'),
    path('api/collaboration/suggest-team/', views_self_development.suggest_team_api, name='suggest-team'),
    path('api/agent/execute/', views_self_development.execute_agent_api, name='execute-agent-api'),
    path('api/learning/status/', views_self_development.learning_status_api, name='learning-status'),
    path('api/agents/list/', views_self_development.list_agents_api, name='list-agents'),

    path('api/v1/assign-job/', views_agent_work_platform.assign_specific_job, name='assign-specific-job'),
    path('api/v1/revenue-analytics/', views_agent_work_platform.revenue_analytics, name='revenue-analytics'),

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

    # ===== UNIFIED BRIDGE: REAL MONEY-MAKING ENDPOINTS =====
    # These endpoints connect all components and enable actual revenue generation
    path('api/bridge/profile/sync/', sync_user_profile, name='bridge-profile-sync'),
    path('api/bridge/opportunities/real/', get_real_opportunities, name='bridge-real-opportunities'),
    path('api/bridge/apply/submit/', submit_real_application, name='bridge-submit-application'),
    path('api/bridge/revenue/record/', record_user_revenue, name='bridge-record-revenue'),
    path('api/bridge/decision/analyze/', get_opportunity_decision, name='bridge-opportunity-decision'),
    path('api/bridge/dashboard/unified/', get_user_dashboard_data, name='bridge-dashboard-data'),
    path('api/bridge/sync/trigger/', trigger_component_sync, name='bridge-component-sync'),

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

    # Learning Loop Integration (Phase 1: Frontend Reality Fix)
    path('api/learning/stats/', learning_stats, name='learning-stats'),
    path('api/learning/insights/', learning_insights, name='learning-insights'),

    # Content Generation APIs (from ai-content-studio)
    path('api/v1/content/create/', create_content, name='content-create'),
    path('api/v1/content/list/', list_content, name='content-list'),
    path('api/v1/content/blog/generate/', generate_blog_post, name='blog-generate'),
    path('api/v1/content/social/generate/', generate_social_media_post, name='social-generate'),
    path('api/v1/content/video/script/', generate_video_script, name='video-script'),
    path('api/v1/content/email/generate/', generate_email, name='email-generate'),  # Phase 4
    path('api/v1/content/podcast/generate/', generate_podcast_script, name='podcast-generate'),  # Phase 4
    path('api/v1/content/templates/', content_templates, name='content-templates'),
    
    # Video Generation endpoints (RunwayML)
    path('api/v1/video/text-to-video/', text_to_video, name='text-to-video'),
    path('api/v1/video/image-to-video/', image_to_video, name='image-to-video'),
    # Session 49: New video endpoints
    path('api/v1/video/video-to-video/', video_to_video_endpoint, name='video-to-video'),
    path('api/v1/video/upscale/', video_upscale_endpoint, name='video-upscale'),
    path('api/v1/video/character-performance/', character_performance_endpoint, name='character-performance'),
    # Session 154: Video Enhancement with ffmpeg (free!)
    path('api/video/upscale/', upscale_video, name='video-upscale-ffmpeg'),
    path('api/video/effects/', apply_video_effect, name='video-effects'),
    # Session 159: Frame Extraction (free!)
    path('api/video/extract-frame/', extract_video_frame, name='video-extract-frame'),
    # Session 159: Video Reverse (free!)
    path('api/video/reverse/', reverse_video, name='video-reverse'),
    # Session 159: Video Trim (free!)
    path('api/video/trim/', trim_video, name='video-trim'),
    # Session 160: Speed Control (free!)
    path('api/video/speed/', change_video_speed, name='video-speed'),
    # Session 160: Video Concatenation (free!)
    path('api/video/concatenate/', concatenate_videos, name='video-concatenate'),
    # Session 161: DaVinci Expansion Phase 2 (5 new video editing features - all FREE!)
    path('api/video/rotate/', rotate_flip_video, name='video-rotate'),
    path('api/video/fade/', fade_video, name='video-fade'),
    path('api/video/crop/', crop_resize_video, name='video-crop'),
    path('api/video/audio/', audio_controls, name='video-audio'),
    path('api/video/pip/', picture_in_picture, name='video-pip'),
    # Session 163: Phase 3 - Watermark/Logo feature
    path('api/video/watermark/', add_watermark, name='video-watermark'),
    # Session 163: Phase 3 - Blur Region feature
    path('api/video/blur/', blur_region, name='video-blur'),
    # Session 164: Phase 3 - Video Stabilization
    path('api/video/stabilize/', stabilize_video, name='video-stabilize'),
    # Session 164: Phase 3 - Text Animations
    path('api/video/text-animation/', add_text_animation, name='video-text-animation'),
    # Session 165: Phase 3 - Green Screen / Chroma Key
    path('api/video/chroma-key/', chroma_key, name='video-chroma-key'),
    # Session 166: Export Presets
    path('api/video/export/', export_for_platform, name='video-export'),
    # Session 166: Video Transitions
    path('api/video/transition/', video_transition, name='video-transition'),
    # Session 166: Auto-Captioning (Whisper)
    path('api/video/caption/', auto_caption, name='video-caption'),
    # Session 175: Lip Sync (Sync Labs via Replicate)
    path('api/video/lip-sync/', lip_sync, name='video-lip-sync'),
    path('api/video/lip-sync/status/<str:prediction_id>/', lip_sync_status, name='video-lip-sync-status'),
    # Session 175: Talking Character Pipeline (Image + Text → Talking Video)
    path('api/video/talking-character/', talking_character, name='video-talking-character'),
    # Session 167: DaVinci Resolve Studio Integration - Making the $295 COUNT!
    path('api/video/davinci-status/', davinci_status, name='hybrid-davinci-status'),
    path('api/video/render-professional/', render_professional, name='video-render-professional'),
    path('api/video/apply-lut/', apply_lut, name='video-apply-lut'),
    path('api/video/grade-professional/', color_grade_professional, name='video-grade-professional'),
    # Session 171: ElevenLabs Audio Integration
    path('api/tool/generate-voice/', generate_voice_view, name='generate-voice'),
    path('api/tool/add-voiceover/', add_voiceover_view, name='add-voiceover'),
    # Session 66 Part 2: Video extension for longer videos (up to 40 seconds!)
    path('api/v1/video/extend/', lambda r: __import__('core.views_video', fromlist=['extend_video_endpoint']).extend_video_endpoint(r), name='video-extend'),
    path('api/v1/video/status/<str:task_id>/', check_video_status, name='video-status'),

    # Session 66 Part 2: DaVinci Resolve video editing endpoints
    path('api/v1/davinci/status/', check_davinci_status, name='davinci-status'),
    path('api/v1/davinci/create-project/', create_video_project_endpoint, name='davinci-create-project'),
    path('api/v1/davinci/chain-videos/', chain_videos_simple, name='davinci-chain-videos'),
    # Session 72: Voice-controlled DaVinci features
    path('api/v1/davinci/add-text-overlay/', add_text_overlay_endpoint, name='davinci-add-text'),
    path('api/v1/davinci/apply-color-grading/', apply_color_grading_endpoint, name='davinci-color-grade'),
    # Session 73: Audio mixing endpoint
    path('api/v1/davinci/add-audio-to-video/', add_audio_to_video_endpoint, name='davinci-add-audio'),
    path('api/v1/video/<uuid:video_id>/', get_video_detail, name='video-detail'),
    path('api/v1/video/gallery/', video_gallery, name='video-gallery'),
    path('api/v1/video/save/', save_video_to_gallery, name='save-video'),
    path('api/v1/video/test-runway/', test_runway_connection, name='test-runway'),
    # Video History endpoints (Session 44: Video Gallery)
    path('api/v1/video/history/', get_video_history, name='video-history'),
    path('api/v1/video/history/<str:video_id>/favorite/', toggle_video_favorite, name='toggle-video-favorite'),
    path('api/v1/video/history/<str:video_id>/view/', increment_video_view, name='increment-video-view'),
    path('api/v1/video/history/<str:video_id>/download/', increment_video_download, name='increment-video-download'),
    path('api/v1/video/history/<str:video_id>/', delete_video, name='delete-video'),
    
    # Audio Generation endpoints (Session 48: Phase 3)
    path('api/v1/audio/text-to-speech/', lambda r: __import__('core.views_audio', fromlist=['text_to_speech']).text_to_speech(r), name='audio-text-to-speech'),
    path('api/v1/audio/text-to-sound/', lambda r: __import__('core.views_audio', fromlist=['text_to_sound']).text_to_sound(r), name='audio-text-to-sound'),
    path('api/v1/audio/voice-dubbing/', lambda r: __import__('core.views_audio', fromlist=['voice_dubbing']).voice_dubbing(r), name='audio-voice-dubbing'),
    path('api/v1/audio/speech-to-speech/', lambda r: __import__('core.views_audio', fromlist=['speech_to_speech']).speech_to_speech(r), name='audio-speech-to-speech'),
    path('api/v1/audio/voice-isolation/', lambda r: __import__('core.views_audio', fromlist=['voice_isolation']).voice_isolation(r), name='audio-voice-isolation'),
    path('api/v1/audio/status/<str:task_id>/', lambda r, task_id: __import__('core.views_audio', fromlist=['check_audio_status']).check_audio_status(r, task_id), name='audio-status'),

    # Image Generation endpoints (Phase 2: Frontend Reality Fix)
    path('api/v1/gallery/generate/', gallery_generate, name='gallery-generate'),
    path('api/v1/gallery/optimize-prompt/', optimize_image_prompt, name='optimize-image-prompt'),  # Session 32: Intelligent prompting
    path('api/v1/gallery/test/', test_image_generation, name='test-image-generation'),

    # Image Editing endpoints (Session 35: Image Editing UI)
    # Session 125: Updated to use image_id wrappers
    # Session 126: Added create_variations, search_and_replace, recolor wrappers
    path('api/stability/remove-background/', lambda r: __import__('core.views_image', fromlist=['remove_background_view']).remove_background_view(r), name='stability-remove-background'),
    path('api/stability/recolor/', lambda r: __import__('core.views_image', fromlist=['recolor_image_view']).recolor_image_view(r), name='stability-recolor'),
    path('api/stability/upscale/', lambda r: __import__('core.views_image', fromlist=['upscale_image_view']).upscale_image_view(r), name='stability-upscale'),
    path('api/stability/create-variations/', lambda r: __import__('core.views_image', fromlist=['create_variations_view']).create_variations_view(r), name='stability-create-variations'),
    path('api/stability/search-and-replace/', lambda r: __import__('core.views_image', fromlist=['search_and_replace_view']).search_and_replace_view(r), name='stability-search-replace'),
    path('api/stability/creative-upscale/', lambda r: __import__('core.views_image', fromlist=['creative_upscale_view']).creative_upscale_view(r), name='stability-creative-upscale'),  # Session 151
    path('api/stability/erase/', lambda r: __import__('core.views_image', fromlist=['erase_object']).erase_object(r), name='stability-erase'),
    path('api/stability/inpaint/', lambda r: __import__('core.views_image', fromlist=['inpaint_image']).inpaint_image(r), name='stability-inpaint'),
    path('api/stability/outpaint/', lambda r: __import__('core.views_image', fromlist=['outpaint_image']).outpaint_image(r), name='stability-outpaint'),

    # Image History / Gallery endpoints (Session 36: Feature 9)
    path('api/images/history/', image_history, name='image-history'),
    path('api/v1/images/upload/', lambda r: __import__('core.views_image', fromlist=['upload_image']).upload_image(r), name='upload-image'),  # Session 197
    path('api/images/<uuid:image_id>/favorite/', toggle_favorite, name='toggle-favorite'),
    path('api/images/<uuid:image_id>/delete/', delete_image, name='delete-image'),
    path('api/images/view/<uuid:image_id>/', track_image_view, name='track-image-view'),  # Session 53: Track views
    path('api/images/download/<uuid:image_id>/', track_image_download, name='track-image-download'),  # Session 53: Track downloads

    # Batch Download (Session 37: Feature 10)
    path('api/images/batch-download/', batch_download_images, name='batch-download-images'),

    # Featured Examples (Session 56: Phase A Task 2)
    path('api/images/examples/', get_featured_examples, name='featured-examples'),

    # Session 74: Character Training API endpoints
    path('api/characters/', list_characters, name='list-characters'),
    path('api/characters/requirements/', training_requirements, name='training-requirements'),
    path('api/characters/create/', create_character, name='create-character'),
    path('api/characters/<int:character_id>/', get_character, name='get-character'),
    path('api/characters/<int:character_id>/submit-training/', submit_training, name='submit-training'),
    path('api/characters/<int:character_id>/training-status/', check_training_status, name='check-training-status'),
    path('api/characters/<int:character_id>/toggle-favorite/', toggle_character_favorite, name='toggle-character-favorite'),
    path('api/characters/<int:character_id>/delete/', delete_character, name='delete-character'),

    # Session 90: CreativeDirectorAgent - Partnership Model API
    path('api/creative-director/generate-options/', generate_options, name='creative-director-generate-options'),
    path('api/creative-director/record-choice/', record_choice, name='creative-director-record-choice'),
    path('api/creative-director/recommendation/', get_recommendation, name='creative-director-recommendation'),
    path('api/creative-director/preferences/', get_user_preferences, name='creative-director-preferences'),
    path('api/creative-director/batch-history/', get_batch_history, name='creative-director-batch-history'),

    # Session 90: Complete Agent Ecosystem API
    # Template Manager
    path('api/agents/templates/save/', save_as_template, name='agent-save-template'),
    path('api/agents/templates/generate/', generate_from_template, name='agent-generate-from-template'),
    path('api/agents/templates/', list_templates, name='agent-list-templates'),
    path('api/agents/templates/<str:template_id>/', delete_template, name='agent-delete-template'),
    # Version Control
    path('api/agents/versions/track/', track_generation, name='agent-track-generation'),
    path('api/agents/versions/rate/', rate_version, name='agent-rate-version'),
    path('api/agents/versions/', list_versions, name='agent-list-versions'),
    path('api/agents/versions/perfect/', get_perfect_versions, name='agent-get-perfect-versions'),
    # Brand Style
    path('api/agents/brand-styles/create/', create_brand_style, name='agent-create-brand-style'),
    path('api/agents/brand-styles/train/', submit_brand_training, name='agent-submit-brand-training'),
    path('api/agents/brand-styles/<int:character_id>/status/', check_brand_training_status, name='agent-check-brand-training-status'),
    path('api/agents/brand-styles/', list_brand_styles, name='agent-list-brand-styles'),
    # Reference Library
    path('api/agents/references/add/', add_reference, name='agent-add-reference'),
    path('api/agents/references/', list_references, name='agent-list-references'),
    path('api/agents/references/<str:reference_id>/', delete_reference, name='agent-delete-reference'),
    # Editing Orchestrator
    path('api/agents/editing/execute/', execute_single_edit, name='agent-execute-single-edit'),
    path('api/agents/editing/workflow/', create_editing_workflow, name='agent-create-editing-workflow'),
    path('api/agents/editing/workflow/execute/', execute_editing_workflow, name='agent-execute-editing-workflow'),
    # Iteration Agent
    path('api/agents/iteration/refine/', refine_image, name='agent-refine-image'),
    # Workflow Coordinator
    path('api/agents/workflows/generate-with-options/', execute_workflow_generate_with_options, name='agent-workflow-generate-options'),
    path('api/agents/workflows/save-as-template/', execute_workflow_save_as_template, name='agent-workflow-save-template'),
    path('api/agents/workflows/train-brand-style/', execute_workflow_train_brand_style, name='agent-workflow-train-brand'),
    path('api/agents/workflows/refine-and-perfect/', execute_workflow_refine_and_perfect, name='agent-workflow-refine-perfect'),
    path('api/agents/status/', get_ecosystem_status, name='agent-ecosystem-status'),

    # Intelligent Prompt Improvement (Session 56: Phase B.1)
    path('api/workflows/improve-prompt/', improve_workflow_prompt, name='improve-workflow-prompt'),

    # Session 63: Project-linked workflow execution
    path('api/workflows/execute-for-project/', execute_workflow_for_project, name='execute-workflow-for-project'),

    # Workflow History & Favorites (Session 57: Phase B.2)
    path('api/workflows/execution/start/', start_workflow_execution, name='start-workflow-execution'),
    path('api/workflows/execution/<uuid:workflow_id>/complete/', complete_workflow_execution, name='complete-workflow-execution'),  # Session 58: Fixed to accept UUID
    path('api/workflows/history/', list_workflow_history, name='list-workflow-history'),
    path('api/workflows/history/<int:workflow_id>/', get_workflow_history, name='get-workflow-history'),
    path('api/workflows/history/<int:workflow_id>/toggle-favorite/', toggle_workflow_favorite, name='toggle-workflow-favorite'),
    path('api/workflows/history/<int:workflow_id>/rerun/', rerun_workflow, name='rerun-workflow'),
    path('api/workflows/favorites/', list_workflow_favorites, name='list-workflow-favorites'),
    path('api/workflows/favorites/save/', save_workflow_favorite, name='save-workflow-favorite'),
    path('api/workflows/favorites/<int:favorite_id>/delete/', delete_workflow_favorite, name='delete-workflow-favorite'),

    # Creative Project Management (Session 60: Phase C.1)
    path('api/creative-projects/', list_projects, name='creative-projects-list'),
    path('api/creative-projects/create/', create_project, name='creative-project-create'),
    path('api/creative-projects/<uuid:project_id>/', get_project, name='creative-project-detail'),
    path('api/creative-projects/<uuid:project_id>/update/', update_project, name='creative-project-update'),
    path('api/creative-projects/<uuid:project_id>/delete/', delete_project, name='creative-project-delete'),
    path('api/creative-projects/<uuid:project_id>/workflows/', add_workflow_to_project, name='creative-project-add-workflow'),
    path('api/creative-projects/<uuid:project_id>/workflows/<int:workflow_id>/', remove_workflow_from_project, name='creative-project-remove-workflow'),

    # Session 148: Project Export Endpoints
    path('api/creative-projects/<uuid:project_id>/export/zip/', views_image.export_project_zip, name='export-project-zip'),
    path('api/creative-projects/<uuid:project_id>/export/pdf/', views_image.export_project_pdf, name='export-project-pdf'),
    path('api/creative-projects/<uuid:project_id>/export/csv/', views_image.export_project_csv, name='export-project-csv'),

    # Session 149: Project Share Endpoints
    path('api/creative-projects/<uuid:project_id>/share/create/', views_share.create_project_share, name='create-project-share'),
    path('api/creative-projects/<uuid:project_id>/share/', views_share.get_project_share, name='get-project-share'),
    path('api/creative-projects/<uuid:project_id>/share/revoke/', views_share.revoke_project_share, name='revoke-project-share'),
    path('share/<str:share_token>/', views_share.view_shared_project, name='view-shared-project'),

    # Portfolio View (Session 61: Phase C.2.1)
    path('api/portfolio/', get_portfolio, name='portfolio'),

    # Image-to-Image Control (Session 38: Feature 11)
    path('api/stability/control/sketch/', control_sketch, name='stability-control-sketch'),
    path('api/stability/control/structure/', control_structure, name='stability-control-structure'),
    path('api/stability/control/', control_unified, name='stability-control-unified'),  # Session 199: Unified endpoint

    # Workflow Execution (Session 41: Real API Integration)
    path('api/workflow/execute/', execute_workflow_step, name='workflow-execute-step'),

    path('api/v1/memory/import-file/', import_file_to_memory, name='import-file'),
    path('api/v1/memory/supported-formats/', supported_file_formats, name='supported-formats'),
    path('api/v1/gallery/list/', gallery_list, name='gallery-list'),
    path('api/v1/gallery/videos/', gallery_videos, name='gallery-videos'),

    # Unified Gallery API (Session 53: Phase 2 & 3)
    path('api/v1/gallery/all/', unified_gallery, name='unified-gallery'),
    path('api/v1/gallery/session/', session_gallery, name='session-gallery'),  # Session 96: Session content viewer
    path('api/v1/sessions/list/', list_sessions, name='list-sessions'),  # Session 97: List all sessions with filters
    path('api/v1/sessions/project/<uuid:project_id>/', get_project_sessions, name='get-project-sessions'),  # Session 97: Option 3 - Get sessions for a project
    path('api/v1/sessions/analytics/', get_session_analytics, name='get-session-analytics'),  # Session 97: Option 4 - Session analytics dashboard
    path('api/v1/sessions/<uuid:session_id>/delete/', delete_session, name='delete-session'),  # Session 97: Delete session
    path('api/v1/sessions/<uuid:session_id>/promote/', promote_session_to_project, name='promote-session-to-project'),  # Session 98: Promote Quick Starts session to standalone project
    path('api/v1/sessions/<uuid:session_id>/assets/', get_session_assets, name='get-session-assets'),  # Session 101: Get all images and videos for a session
    path('api/v1/gallery/batch-download/', unified_batch_download, name='unified-batch-download'),
    path('api/v1/gallery/toggle-favorite/', unified_toggle_favorite, name='unified-toggle-favorite'),
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
    path('api/v1/games/<str:game_id>/spider-insights/', get_game_spider_insights, name='game-spider-insights'),
    path('api/v1/odds/bankroll/stats/', get_bankroll_stats, name='bankroll-stats'),
    path('api/v1/sports/weather/', get_weather_data, name='weather-data'),
    path('api/v1/sports/injuries/', get_injury_data, name='injury-data'),
    path('api/v1/sports/betting-intelligence/', get_betting_intelligence, name='betting-intelligence'),
    path('api/v1/sports/orchestrate/', orchestrate_agent_analysis, name='orchestrate-agents'),
    path('api/v1/sports/orchestration/status/<str:task_id>/', get_orchestration_status, name='orchestration-status'),
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
    path('api/v1/coleadership/', include('coleadership.urls')),  # AI-Human Co-Leadership (Session 99)
    path('api/v1/render-jobs/', include('rendering.urls')),  # Render Jobs & DaVinci Integration (Session 105)
    path('api/v1/pipelines/', include('pipelines.urls')),  # Creative Pipelines v1 - Template-Based Orchestration (Session 109)
    path('api/v1/sports/', include('sports.urls')),  # Sports/Betting module
    path('api/v1/content/', include('content.urls')),  # Content Generation module
    path('api/v1/self-awareness/', include('self_awareness.urls')),  # Self-Awareness module
    # path('api/v1/campaigns/', include('campaigns.urls')),  # Campaigns module (archived)
    path('api/v1/mythology/', include('mythology.urls')),  # Mythology/Hallucination Review module
    path('api/v1/odds-calc/', include('odds_calc.urls')),  # Odds calculation endpoints
    path('api/v1/intelligence/', include('intelligence.urls')),  # Intelligence module with action plan execution
    path('api/v1/persistence/', include('persistence.urls')),  # Data Persistence Infrastructure

    # System Reality Self-Awareness Engine
    path('truth/', include('core.truth_urls')),  # Truth Dashboard and Reality APIs

    # AI Platform Learning and Verification APIs
    path('', include('ai_platform.urls')),  # AI Platform endpoints

    # Learning Dashboard APIs for real-time proof
    path('api/learning/dashboard/', learning_dashboard_data, name='learning-dashboard-data'),
    path('api/learning/updates/', learning_updates_stream, name='learning-updates-stream'),

    # AI Learning System APIs - Real user-facing learning system
    path('api/learning/baseline/', baseline_knowledge, name='learning-baseline'),
    path('api/learning/collect/', collect_data, name='learning-collect'),
    path('api/learning/analyze/', analyze_data, name='learning-analyze'),
    path('api/learning/synthesize/', synthesize_knowledge, name='learning-synthesize'),
    path('api/learning/history/', learning_history, name='learning-history'),
    path('api/learning/save/', save_learning_session, name='learning-save'),

    # Unified Learning Dashboard API - Real data for frontend
    path('api/dashboard/all/', dashboard_all_data, name='dashboard-all-data'),
    path('api/dashboard/learning/', dashboard_learning_data, name='dashboard-learning-data'),
    path('api/dashboard/collaboration/', dashboard_collaboration_data, name='dashboard-collaboration-data'),
    path('api/dashboard/costs/', dashboard_cost_data, name='dashboard-cost-data'),
    path('api/dashboard/health/', dashboard_health_data, name='dashboard-health-data'),
    path('api/dashboard/feed/', dashboard_feed_data, name='dashboard-feed-data'),
    path('api/dashboard/verification/', dashboard_verification_data, name='dashboard-verification-data'),

    # Real agent dashboard endpoints with database data
    path('api/agent-dashboard/learning/', agent_learning_data, name='agent-dashboard-learning'),
    path('api/agent-dashboard/collaboration/', agent_collaboration_data, name='agent-dashboard-collaboration'),
    path('api/agent-dashboard/costs/', agent_costs_data, name='agent-dashboard-costs'),
    path('api/agent-dashboard/health/', system_health_data, name='agent-dashboard-health'),
    path('api/agent-dashboard/feed/', learning_feed_data, name='agent-dashboard-feed'),
    path('api/agent-dashboard/agents/', all_agents_list, name='agent-dashboard-agents'),

    # Spider network dashboard endpoints
    path('api/spider-dashboard/network/', spider_network_data, name='spider-dashboard-network'),
    path('api/spider-dashboard/activity/', spider_activity_feed, name='spider-dashboard-activity'),
    path('api/spider-dashboard/data/', spider_data_stats, name='spider-dashboard-stats'),
    path('api/spider-dashboard/execute/', execute_spider, name='spider-dashboard-execute'),

    # Spider Data Viewer API - See what spiders actually collected
    path('api/spider-data/<str:spider_name>/items/', get_spider_items, name='spider-data-items'),
    path('api/spider-data/summary/', get_spider_summary, name='spider-data-summary'),
    path('api/spider-data/item/<str:item_id>/process/', mark_spider_item_processed, name='spider-data-process'),

    # Learning path endpoints
    path('api/learning/trigger/', trigger_learning_query, name='learning-trigger'),
    path('api/learning/status/', get_overall_learning_status, name='learning-status-overall'),
    path('api/learning/status/<str:session_id>/', get_learning_status, name='learning-status'),
    path('api/learning/knowledge-map/<str:agent_id>/', get_agent_knowledge_map, name='agent-knowledge-map'),
    path('api/learning/feed/', get_learning_feed, name='learning-feed'),
    path('api/agents/<str:agent_name>/solutions/recent/', get_agent_solutions_recent, name='agent-solutions-recent'),

    # Solution Explorer and Learning Pipeline APIs
    path('api/solutions/', lambda r: __import__('core.views_solution_explorer', fromlist=['get_solutions']).get_solutions(r), name='solutions-list'),
    path('api/solutions/<str:solution_id>/', lambda r, solution_id: __import__('core.views_solution_explorer', fromlist=['get_solution_detail']).get_solution_detail(r, solution_id), name='solution-detail'),
    path('api/solutions/<str:solution_id>/apply/', lambda r, solution_id: __import__('core.views_solution_explorer', fromlist=['apply_solution']).apply_solution(r, solution_id), name='apply-solution'),
    path('api/learning/data-flow/', lambda r: __import__('core.views_solution_explorer', fromlist=['get_data_flow']).get_data_flow(r), name='learning-data-flow'),
    path('api/learning/progress/', lambda r: __import__('core.views_solution_explorer', fromlist=['get_learning_progress']).get_learning_progress(r), name='learning-progress'),
    path('api/learning/personalize/', lambda r: __import__('core.views_solution_explorer', fromlist=['personalize_learning']).personalize_learning(r), name='personalize-learning'),

    # Learning Journey APIs - Interactive learning paths with progress tracking
    path('api/journey/start/', lambda r: __import__('core.views_learning_journey', fromlist=['start_learning_journey']).start_learning_journey(r), name='journey-start'),
    path('api/journey/<str:journey_id>/status/', lambda r, journey_id: __import__('core.views_learning_journey', fromlist=['get_journey_status']).get_journey_status(r, journey_id), name='journey-status'),
    path('api/journey/<str:journey_id>/step/<int:step_id>/start/', lambda r, journey_id, step_id: __import__('core.views_learning_journey', fromlist=['start_journey_step']).start_journey_step(r, journey_id, step_id), name='journey-step-start'),
    path('api/journey/<str:journey_id>/step/<int:step_id>/complete/', lambda r, journey_id, step_id: __import__('core.views_learning_journey', fromlist=['complete_journey_step']).complete_journey_step(r, journey_id, step_id), name='journey-step-complete'),
    path('api/journey/active/', lambda r: __import__('core.views_learning_journey', fromlist=['get_active_journeys']).get_active_journeys(r), name='journey-active'),
    path('api/journey/<str:journey_id>/reset/', lambda r, journey_id: __import__('core.views_learning_journey', fromlist=['reset_journey']).reset_journey(r, journey_id), name='journey-reset'),

    # Agent Learning Verification API - Prove agents actually learn
    path('api/verify/start/', start_verification_session, name='verification-start'),
    path('api/verify/baseline/', run_baseline_test, name='verification-baseline'),
    path('api/verify/expose/', expose_learning_material, name='verification-expose'),
    path('api/verify/post-learning/', run_post_learning_test, name='verification-post-learning'),
    path('api/verify/status/', get_session_status, name='verification-status'),
    path('api/verify/sessions/', list_verification_sessions, name='verification-sessions'),
    path('api/verify/demo/', run_quick_verification_demo, name='verification-demo'),

    # AI Ecosystem Visualization APIs
    path('api/ecosystem/stats/', get_ecosystem_stats, name='ecosystem-stats'),
    path('api/ecosystem/feed/', get_live_learning_feed, name='ecosystem-feed'),
    path('api/ecosystem/network/', get_agent_network, name='ecosystem-network'),
    path('api/ecosystem/trigger/', trigger_learning_event, name='ecosystem-trigger'),
    
    # Advanced Workflow Orchestration APIs (BACKUP/FALLBACK - these should NOT conflict now)
    path('api/v1/workflows/create-advanced/', create_advanced_workflow, name='create-advanced-workflow'),
    path('api/v1/workflows/execute-advanced/', execute_advanced_workflow, name='execute-advanced-workflow'),
    path('api/v1/workflows/execution/<str:execution_id>/status/', get_workflow_execution_status, name='workflow-execution-status'),
    path('api/v1/workflows/templates-advanced/', list_workflow_templates, name='workflow-templates-advanced'),  # RENAMED to avoid conflict
    path('api/v1/workflows/from-template/', create_workflow_from_template, name='workflow-from-template'),
    path('api/v1/workflows/analytics/', workflow_analytics, name='workflow-analytics'),
    path('api/v1/workflows/schedule/', schedule_workflow, name='schedule-workflow'),
    path('api/v1/workflows/collaborate/', workflow_collaboration, name='workflow-collaboration'),

    # Revenue tracking endpoints (CRITICAL FIX - Session 37-A Priority 3)
    path('api/revenue/create/', lambda r: __import__('core.views_revenue', fromlist=['create_revenue']).create_revenue(r), name='create-revenue'),
    path('api/revenue/summary/', lambda r: __import__('core.views_revenue', fromlist=['get_revenue_summary']).get_revenue_summary(r), name='revenue-summary'),

    # Opportunity and application endpoints (CRITICAL FIX - Session 37-A Priority 5)
    path('api/opportunities/quick-apply/', lambda r: __import__('core.views_opportunities', fromlist=['quick_apply']).quick_apply(r), name='quick-apply'),

    # ===== PARTNERSHIP SYSTEM (Session 38) =====
    # Human-AI Partnership tracking and collaboration features
    path('partnership/', views_partnership.partnership_dashboard, name='partnership-dashboard'),
    path('partnership/start/<uuid:opportunity_id>/', views_partnership.start_partnership, name='start-partnership'),
    path('partnership/project/<uuid:project_id>/', views_partnership.partnership_project_detail, name='partnership-project-detail'),

    # Partnership API endpoints
    path('api/partnership/ai-contribution/<uuid:project_id>/', views_partnership.add_ai_contribution, name='add-ai-contribution'),
    path('api/partnership/human-contribution/<uuid:project_id>/', views_partnership.add_human_contribution, name='add-human-contribution'),
    path('api/partnership/complete/<uuid:project_id>/', views_partnership.complete_partnership, name='complete-partnership'),
    path('api/partnership/opportunities/', views_partnership.partnership_opportunities_api, name='partnership-opportunities-api'),
    path('api/partnership/stats/', views_partnership.partnership_stats_api, name='partnership-stats-api'),
    path('api/partnership/health/', views_partnership.partnership_health_check, name='partnership-health'),
    path('api/v1/', include('backend.auto_endpoints.urls')),

    # Session 100: Part 11 - Leadership Dashboard Endpoints
    path('api/leadership/meetings/', list_executive_meetings, name='list-executive-meetings'),
    path('api/leadership/meetings/<str:meeting_key>/', get_meeting_details, name='get-meeting-details'),

    # TEST ROUTE DONE HERE line 973
    # REST framework browsable API (development only)
    path('api-auth/', include('rest_framework.urls')),
]

# Add WebSocket test endpoint if available
try:
    from core.health import websocket_test
    urlpatterns.append(path('api/v1/websocket-test/', websocket_test, name='websocket-test'))
except ImportError:
    pass

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns.append(path('health/', include('backend.auto_endpoints.urls')))  # public health
