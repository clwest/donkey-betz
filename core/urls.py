"""
URL configuration for Unified Donkey Betz Platform.

Main URL routing for the unified mega-platform.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponsePermanentRedirect
from rest_framework.routers import DefaultRouter


# Session 237: Redirect handler for legacy broken URLs
def legacy_portfolio_image_redirect(request, path):
    """
    Redirect legacy /api/portfolio/generated_images/... URLs to /media/generated_images/...
    These broken URLs were cached in browsers from old versions.
    """
    return HttpResponsePermanentRedirect(f'/media/generated_images/{path}')
 
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
    projects_list, project_detail, project_agents, assign_agent_to_project,
    create_project_from_research,  # Session 302: Direct API endpoint
    add_research_to_project,  # Session 324: Add research to existing project
    export_research_pdf,  # Session 325: Export research as PDF
    export_comprehensive_pdf,  # Session 352: Export ALL research as single PDF
    add_creative_content_to_project,  # Session 334: Add creative content to existing project
    # Session 353: Research → Creative Pipeline
    generate_brand_assets,
    analyze_brand_styles,
    get_available_styles,
    create_project_from_creative_content,  # Session 334: Create project from creative content
    # Session 335: Living Project API
    project_feed,
    activate_living_project,
    update_insight_status,
    update_living_config,
    # Session 354: Project Learning Loop
    toggle_project_learning,
    get_project_learning_status,
    trigger_project_learning,
)

# Import agent tracking API views (Session 120)
from core.views_agent_tracking import (
    project_agents as project_contributing_agents,
    agent_timeline,
    rate_contribution,
    mark_contribution_selected
)

# Session 338: Business Ideas API - Autonomous Pipeline Entry Point
from core.views_business_ideas import (
    create_business_idea,
    get_business_idea,
    generate_assets,
    list_business_ideas,
    pipeline_stats,  # Session 343: Pipeline stats for UI
    get_brand_recommendations,  # Session 394: Brand style recommendations
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

# Session 388: Income Action Pipeline - Spider to Income Bridge
from core.views_income_action import (
    save_opportunity as income_save_opportunity,
    generate_application as income_generate_application,
    update_status as income_update_status,
    get_opportunities as income_get_opportunities,
    get_statistics as income_get_statistics,
    quick_apply as income_quick_apply,
)

# Session 208: Import spider intelligence views
# Session 343: Added spider_registry, test_spider, run_all_spiders
from core.views_spider_intelligence import (
    trending_topics,
    market_insights,
    tech_trends,
    job_market,
    search_data,
    data_summary,
    prompt_insights,
    daily_report,
    spider_registry,
    test_spider,
    run_all_spiders,
    market_research_dashboard,  # Session 344
    dashboard_stats as spider_dashboard_stats,  # Session 345
    opportunities_dashboard,  # Session 385
    # Session 399: Spider Data UI
    spider_data_feed,
    spider_knowledge,
    spider_timeline,
)

# Session 219: Import agent intelligence views (Phase A)
from core.views_agent_intelligence import (
    list_agents as ai_agents_list,
    get_agent_feed as ai_agent_feed,
    get_trends as ai_trends,
    get_suggestions as ai_suggestions,
    get_stats as ai_stats,
    get_categories as ai_categories,
    get_capabilities as ai_capabilities,
    get_bridge_status as ai_bridge_status,
    inject_test_data as ai_inject_test
)

# Session 219 Phase B: Import agent collaboration views
from core.views_agent_collaboration import (
    send_message as collab_send_message,
    get_messages as collab_get_messages,
    initiate_collaboration as collab_initiate,
    consult_expert as collab_consult,
    request_consensus as collab_request_consensus,
    submit_vote as collab_submit_vote,
    get_consensus_status as collab_consensus_status,
    share_knowledge as collab_share_knowledge,
    query_knowledge as collab_query_knowledge,
    get_collaboration_stats as collab_stats,
    get_agent_activity as collab_agent_activity
)

# Session 219 Phase C: Import agent learning views
from core.views_agent_learning import (
    record_interaction as learning_record,
    get_preferences as learning_preferences,
    get_adaptive_context as learning_context,
    get_learning_stats as learning_stats,
    apply_preferences as learning_apply,
    clear_preferences as learning_clear,
    get_preferences_summary as learning_summary,
    share_learning as learning_share,
    get_all_preferences as learning_all,
    # Session 244: Agent Conversations
    get_agent_conversations,
    trigger_agent_conversation,
    # Session 247: Agent Dreams
    get_agent_dreams,
    trigger_agent_dreams,
    mark_dreams_shown,
    react_to_dream,
    # Session 248: Knowledge Transfer Activity Feed
    get_knowledge_transfer_feed,
    # Session 249: Dream Feedback System
    get_dream_preferences,
    get_dream_exploration,
    # Session 323: Boardroom Decisions
    get_boardroom_decisions,
    promote_decision,
    reject_decision,
    # Session 368: Dream Validation UI
    get_boardroom_dreams,
    decide_dream,
    get_dream_implementations,
    validate_implementation,
    rate_dream,
    get_validation_metrics,
    # Session 417: Agent Profile
    get_agent_profile,
    # Session 417: Activity Detail endpoints
    get_conversation_detail,
    get_hivemind_detail,
    get_decision_detail,
    get_dream_detail,
)

# Session 250: Hive Mind Mode
from core.views_hive_mind import (
    start_hive_mind_session,
    get_hive_mind_session,
    list_hive_mind_sessions,
    get_available_agents,
    preview_agents,
)

# Session 251: Memory Palace
from core.views_memory_palace import (
    get_agent_memories,
    get_memory_detail,
    create_memory,
    search_memories,
    get_memory_palace_rooms,
    get_room_memories,
    assign_memory_to_room,
    get_memory_summary,
    connect_memories,
    get_memory_connections,
    get_memory_palace_overview,
    delete_memory,
)

# Session 252: Agent Mood System
from core.views_agent_mood import (
    get_mood_overview,
    get_agent_mood,
    set_agent_mood,
    get_mood_history,
    get_mood_rules,
    create_mood_rule,
    delete_mood_rule,
    trigger_mood_from_memory,
    get_mood_prompt_context,
)

# Session 253: Agent Rivalries & Alliances
from core.views_agent_relationships import (
    get_relationships_overview,
    get_agent_relationships,
    create_relationship,
    record_interaction,
    get_alliance,
    create_alliance,
    add_alliance_member,
    disband_alliance,
    get_rivalry,
    create_rivalry,
    record_competition,
    end_rivalry,
    get_relationship_events,
    auto_generate_relationships,
)

# Session 254: Agent Evolution System
from core.views_agent_evolution import (
    get_evolution_overview,
    get_agent_evolution,
    award_agent_xp,
    prestige_agent,
    get_available_abilities,
    create_ability,
    unlock_ability,
    get_xp_leaderboard,
    get_recent_xp_gains,
    initialize_all_evolutions,
    record_task_completion,
)

# Session 255: Time Travel Debugging API
from core.views_time_travel import (
    get_time_travel_overview,
    get_session_detail,
    start_session,
    end_session,
    toggle_bookmark_session,
    record_decision,
    update_decision_outcome,
    flag_decision,
    create_bookmark,
    delete_bookmark,
    add_annotation,
    delete_annotation,
    search_sessions,
    get_flagged_decisions,
    get_agent_sessions,
    simulate_session,
)

# Session 256: Agent Personality System
from core.views_personality import (
    personality_overview,
    agent_personality,
    generate_personality,
    generate_all_personalities,
    personality_compatibility,
    personality_archetypes,
)

# Session 257: Agent Memory Clusters
from core.views_memory_clusters import (
    clusters_overview,
    agent_clusters,
    cluster_detail,
    cluster_visualization_data,
    generate_all_clusters,
    add_memory_to_cluster,
    remove_memory_from_cluster,
    cluster_evolution,
    find_similar_clusters,
)

# Session 258: Agent Predictions / Prophecies
from core.views_predictions import (
    predictions_overview,
    agent_predictions,
    prediction_detail,
    verify_prediction,
    upvote_prediction,
    add_comment,
    prediction_leaderboard,
    generate_predictions_from_dreams,
    expire_old_predictions,
)

# Session 259: Time Capsule Messages
from core.views_time_capsules import (
    TimeCapsuleOverviewView,
    AgentTimeCapsuleView,
    TimeCapsuleDetailView,
    RevealTimeCapsuleView,
    TimeCapsuleReactView,
    ReadyToRevealView,
    GenerateTimeCapsuleView,
    ExpireOldCapsulesView,
)

# Session 219 Phase D: Import marketplace views
from core.views_marketplace import (
    browse_workflows as marketplace_browse,
    featured_workflows as marketplace_featured,
    trending_workflows as marketplace_trending,
    workflow_details as marketplace_details,
    install_workflow as marketplace_install,
    publish_workflow as marketplace_publish,
    add_review as marketplace_add_review,
    get_reviews as marketplace_get_reviews,
    my_published_workflows as marketplace_my_published,
    my_installed_workflows as marketplace_my_installed,
    marketplace_stats,
    get_categories as marketplace_categories,
)

# Session 220: Import project collaboration views
from core.views_project_collaboration import (
    list_create_projects as proj_collab_projects,
    project_detail as proj_collab_detail,
    invite_collaborator as proj_collab_invite,
    list_invitations as proj_collab_invitations,
    accept_invitation as proj_collab_accept,
    decline_invitation as proj_collab_decline,
    list_collaborators as proj_collab_collaborators,
    remove_collaborator as proj_collab_remove,
    get_activity as proj_collab_activity,
    project_comments as proj_collab_comments,
    get_presences as proj_collab_presences,
)

# Session 206: Import preferences dashboard views
# Session 210: Added implicit learning & recommendations
# Session 211: Added A/B testing
from core.views_preferences import (
    get_all_preferences,
    domain_preferences,
    clear_all_preferences,
    preference_history,
    learn_from_project,
    preference_stats,
    smart_style_suggestions,
    apply_style_suggestion,
    # Session 210: Implicit Learning & Recommendations
    track_behavior,
    get_implicit_preferences,
    get_style_recommendations,
    get_similar_styles,
    get_discovery_styles,
    # Session 210: Style Evolution Tracking
    get_style_evolution,
    record_evolution_snapshot,
    get_style_shifts,
    # Session 211: A/B Testing Framework
    list_experiments,
    create_experiment,
    start_experiment,
    stop_experiment,
    get_experiment_results,
    get_my_variant,
    track_ab_conversion,
)

# Session 223: Import Opportunity Engine views (Phase 1 - Creative Intelligence Empire)
from core.views_opportunity import (
    opportunity_list,
    opportunity_detail,
    opportunity_score,
    opportunity_act,
    opportunity_top,
    opportunity_rescore,
    opportunity_analyze,
    opportunity_stats,
    # Session 224: Revenue Reality endpoints
    opportunity_log_revenue,
    opportunity_revenue_list,
    revenue_stats,
    opportunity_link_content,
    opportunity_content_list,
    # Session 425: Opportunity Pipeline Automation - Task Management
    opportunity_task_list,
    opportunity_task_detail,
    opportunity_task_accept,
    opportunity_task_apply,
    opportunity_task_won,
    opportunity_task_lost,
    opportunity_task_update_action_items,
    opportunity_task_stats,
)

# Session 227: Import Team Power views (Phase 3 - Multi-Agent Collaboration)
from core.views_team_collaboration import (
    list_teams,
    create_team,
    get_team,
    add_team_member,
    list_agent_roles,
    create_agent_role,
    send_agent_message,
    get_agent_messages,
    get_message_thread,
    create_team_workflow,
    get_team_workflow,
    start_team_workflow,
    complete_workflow_step,
    team_stats,
    # Session 228: Workflow Engine API
    list_workflow_templates as team_workflow_templates,
    execute_workflow,
    execute_workflow_step,
    workflow_status,
    run_full_workflow,
    list_active_workflows,
)

# Session 229: Import Smart Distribution views (Phase 4)
from core.views_distribution import (
    list_platforms,
    create_platform,
    get_platform,
    list_user_accounts,
    connect_platform,
    list_distributions,
    create_distribution,
    submit_distribution,
    publish_distribution,
    record_sale,
    get_recommendations,
    distribution_stats,
    platform_analytics,
    seed_platforms_api,
)

# Session 230: Import Platform Integration views (OAuth, APIs)
from core.views_platform_integrations import (
    oauth_connect,
    oauth_callback,
    refresh_token,
    list_platform_integrations,
    disconnect_platform,
    # Etsy
    etsy_get_shop,
    etsy_create_listing,
    # Shutterstock
    shutterstock_get_portfolio,
    shutterstock_submit_content,
    # Gumroad
    gumroad_get_products,
    gumroad_create_product,
    # Revenue sync
    sync_platform_revenue,
)

# Session 230: Import Auto-Distribution views
from core.views_auto_distribution import (
    create_auto_distribution,
    batch_distribute,
    list_scheduled_distributions,
    reschedule_distribution,
    cancel_scheduled_distribution,
    auto_distribution_settings,
    distribution_templates,
    apply_distribution_template,
)

# Session 230: Import Revenue Analytics views
from core.views_revenue_analytics import (
    revenue_dashboard,
    platform_revenue_detail,
    compare_platforms,
    calculate_roi,
    revenue_forecast,
    revenue_goals,
    export_revenue_data,
)

# Session 232: Import Learning Loop views (Phase 5)
from core.views_learning_loop import (
    list_success_patterns,
    pattern_detail,
    analyze_patterns,
    predict_performance,
    list_predictions,
    get_pricing_optimization,
    get_learning_profile,
    update_learning_profile,
    list_insights,
    generate_insights,
    mark_insight_read,
    dismiss_insight,
    get_performance_comparison,
    learning_dashboard,
)

# Session 449: Import Pipeline Learning views (Learning Loops for AI Series)
from core.views_learning import (
    record_feedback as pipeline_record_feedback,
    record_engagement as pipeline_record_engagement,
    recommend_style as pipeline_recommend_style,
    recommend_voice as pipeline_recommend_voice,
    style_leaderboard as pipeline_style_leaderboard,
    get_insights as pipeline_get_insights,
    get_statistics as pipeline_get_statistics,
    generate_insights as pipeline_generate_insights,
)

# Session 234: Import proactive system views (Phase 6)
from core.views_proactive import (
    proactive_dashboard,
    run_proactive_check,
    list_alerts,
    create_alert,
    alert_detail,
    toggle_alert,
    check_alerts,
    list_notifications,
    mark_notification_read,
    dismiss_notification,
    mark_all_notifications_read,
    notification_preferences,
    list_suggestions,
    generate_suggestions,
    suggestion_detail,
    list_automations,
    create_automation,
    automation_detail,
    execute_automation,
    toggle_automation,
    automation_logs,
)

# Session 235: Import A/B Testing Framework views (Phase 6)
from core.views_ab_testing import (
    ab_testing_dashboard,
    list_tests,
    create_test,
    test_detail,
    start_test,
    pause_test,
    complete_test,
    test_results,
    add_variant,
    variant_detail,
    record_event,
    list_goals,
    create_goal,
    goal_detail,
    update_goal_progress,
)

# Session 213: Import workflow API views
from core.views_workflow import (
    workflows_list_create,
    workflow_detail,
    workflow_execute,
    workflow_duplicate,
    builtin_workflows,
    available_agents,
    execution_list,
    execution_detail,
    workflow_schedule,
    workflow_share,
    workflow_unshare,
    shared_workflow,
    import_shared_workflow,
    public_workflows,
)

# Session 214: Import collaboration API views
from core.views_collaboration import (
    request_collaboration,
    get_collaboration,
    respond_to_collaboration,
    collaboration_history,
    send_message,
    get_messages,
    mark_message_processed,
    share_knowledge,
    search_knowledge,
    learn_knowledge,
    rate_knowledge,
    get_agent_performance,
    get_top_performers,
    get_collaboration_stats,
    find_collaborator,
    delegate_task,
    request_consultation,
)

# Session 215: Import collective intelligence API views
from core.views_collective_intelligence import (
    aggregate_insights,
    generate_report,
    get_knowledge_gaps,
    get_agent_improvements,
    get_collaboration_monitor,
    get_collaboration_network,
    orchestrate_task,
    get_collective_stats,
    get_dashboard_data,
    get_agent_collective_profile,
    resolve_knowledge_gap,  # Session 373
    resolve_all_knowledge_gaps,  # Session 373
    fix_collaboration,  # Session 373
    boost_agent,  # Session 373
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
# Session 439: Stripe Webhook
from core.views_stripe import stripe_webhook, subscription_status

# Session 440: Voice Marketplace
from core.views_voice_marketplace import (
    marketplace_browse, voice_detail, my_voices, publish_voice, unpublish_voice,
    update_voice, generate_speech, preview_voice, add_review, earnings_summary,
    transaction_history, create_voice_from_elevenlabs, start_clone_request,
    clone_request_status,
)

from core import views_portfolio
from core.views_profile import (
    ExtendedProfileView, ProfileSkillsView, ProfileForApplicationView
)
# Import Personal Assistant views
from core.views_personal_assistant import (
    chat_with_assistant, get_assistant_context, get_learning_summary,
    provide_feedback, reset_assistant, voice_to_assistant,
    voice_interview_response, transcribe_only  # Session 456: Voice interview
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
# Session 430: Import Interview views
from core.views_interview import (
    start_interview, respond_interview, interview_status,
    resume_interview, get_user_profile_summary,
    # Session 457: Certification endpoints
    list_certifications, add_certification, delete_certification
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
    learning_stats, learning_insights,
    # Session 217: Chart.js Analytics
    get_chart_agent_trends, get_chart_agent_comparison, get_chart_agent_heatmap,
    get_chart_workflow_trends, get_chart_workflow_success,
    get_chart_knowledge_growth, get_chart_knowledge_domains,
    get_chart_system_health, get_chart_dashboard,
    # Session 221: Advanced Analytics Phase F
    analytics_overview_v2, usage_timeline_v2, performance_timeline_v2,
    cost_breakdown_v2, analytics_dashboards_v2, analytics_alerts_v2,
    realtime_stats_v2, track_event_v2
)
# Session 217B: Agent Training
from core.views_agent_training import (
    list_agents as training_list_agents, get_agent as training_get_agent,
    update_agent as training_update_agent, list_capabilities,
    add_capability, remove_capability, list_templates, create_from_template,
    training_history, training_stats, training_dashboard,
    agent_chat, agent_invoke  # Session 383: Chat & Invoke
)
# Session 217C: Workflow Analytics API
from core.views_workflow_analytics import (
    get_execution_history as wf_execution_history,
    get_execution_trends as wf_execution_trends,
    get_success_failure_analysis as wf_success_failure,
    get_performance_metrics as wf_performance_metrics,
    get_performance_comparison as wf_performance_comparison,
    compare_workflows as wf_compare_workflows,
    get_step_performance as wf_step_performance,
    get_execution_heatmap as wf_execution_heatmap,
    get_analytics_summary as wf_analytics_summary,
    get_analytics_dashboard as wf_analytics_dashboard,
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
    image_history, toggle_favorite, delete_image, batch_download_images, serve_image,
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
    # Session 237: Portfolio Delete APIs
    delete_portfolio_item, bulk_delete_portfolio_items, check_portfolio_broken_links,
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
    create_knowledge_collection, list_knowledge_collections, advanced_rag_query, optimize_embeddings,
    # Session 402: Document ingestion APIs
    list_documents, ingest_url, ingest_file, get_document, delete_document
)
# Session 403: Legal Case Files APIs
# Session 407: Added export_legal_section for document downloads
from core.views_legal import (
    list_legal_case_files, upload_legal_case_file, get_legal_case_file,
    analyze_legal_case_file, delete_legal_case_file, export_legal_section,
    # Session 408: Litigation Document Management
    list_litigation_documents, upload_litigation_document, get_case_knowledge_graph,
    rebuild_knowledge_graph, generate_response_to_filing, list_generated_responses,
    get_generated_response, create_filing_package, get_document_types,
    # Session 410: Document Threading APIs
    get_document_threads, get_document_thread, get_documents_needing_response,
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

# Session 240: New Workflow Engine (user-vision-first philosophy)
from core.views_workflow_engine import execute_workflow_v2, parse_intent

# Session 264: Super Platform Coordinator (Phase 1 - Unified Intelligence)
from core.views_super_platform import (
    SuperPlatformProcessView,
    SuperPlatformClassifyView,
    SuperPlatformStatusView,
    SuperPlatformQuickAskView,
)

# Session 326: Project-Agent Learning Bridge API
from core.views_research_feedback import (
    submit_research_feedback,
    get_research_feedback,
    get_project_learning_stats,
    trigger_knowledge_sync,
    trigger_priority_recalculation,
    get_spider_priorities,
)

# Session 429: Discord Account Linking API
from core.views_discord import (
    generate_discord_link_code,
    get_discord_status,
    unlink_discord,
    verify_discord_link_code,
)

# Session 327: Project-Scoped Agent Intelligence API
from core.views_project_intelligence import (
    get_project_intelligence_overview,
    get_project_learning,
    get_project_conversations,
    get_project_dreams,
    get_project_boardroom,
    trigger_project_conversation,
    get_project_spiders,
    refresh_project_spiders,
    get_project_slack_channel,
    post_project_slack_message,
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

    # Session 295: Content Provenance, Audit, Originality & Marketplace APIs
    path('api/provenance/', include('core.urls_provenance')),

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
    path('api/projects/from-research/', create_project_from_research, name='create-project-from-research'),  # Session 302
    path('api/projects/<uuid:project_id>/add-research/', add_research_to_project, name='add-research-to-project'),  # Session 324
    path('api/projects/<uuid:project_id>/export-research-pdf/', export_research_pdf, name='export-research-pdf'),  # Session 325
    path('api/projects/<uuid:project_id>/export-comprehensive-pdf/', export_comprehensive_pdf, name='export-comprehensive-pdf'),  # Session 352
    path('api/projects/<uuid:project_id>/add-creative-content/', add_creative_content_to_project, name='add-creative-content-to-project'),  # Session 334
    # Session 353: Research → Creative Pipeline
    path('api/projects/<uuid:project_id>/generate-brand-assets/', generate_brand_assets, name='generate-brand-assets'),
    path('api/projects/<uuid:project_id>/analyze-brand-styles/', analyze_brand_styles, name='analyze-brand-styles'),
    path('api/styles/available/', get_available_styles, name='get-available-styles'),
    path('api/projects/from-creative-content/', create_project_from_creative_content, name='create-project-from-creative-content'),  # Session 334
    path('api/projects/<uuid:project_id>/learning/', get_project_learning_stats, name='project-learning-stats'),  # Session 326

    # Session 335: Living Project APIs
    path('api/projects/<uuid:project_id>/feed/', project_feed, name='project-feed'),
    path('api/projects/<uuid:project_id>/activate-living/', activate_living_project, name='activate-living-project'),
    path('api/projects/<uuid:project_id>/insights/<uuid:insight_id>/status/', update_insight_status, name='update-insight-status'),
    path('api/projects/<uuid:project_id>/living-config/', update_living_config, name='update-living-config'),

    # Session 354: Project Learning Loop APIs
    path('api/projects/<uuid:project_id>/learning/toggle/', toggle_project_learning, name='toggle-project-learning'),
    path('api/projects/<uuid:project_id>/learning/status/', get_project_learning_status, name='project-learning-status'),
    path('api/projects/<uuid:project_id>/learning/trigger/', trigger_project_learning, name='trigger-project-learning'),

    # Session 338: Business Ideas API - Autonomous Pipeline
    # THE entry point: "I have a business idea" -> Complete research -> Business plan -> Assets
    path('api/business-ideas/', create_business_idea, name='create-business-idea'),
    path('api/business-ideas/list/', list_business_ideas, name='list-business-ideas'),
    path('api/business-ideas/stats/', pipeline_stats, name='pipeline-stats'),  # Session 343
    path('api/business-ideas/<uuid:project_id>/', get_business_idea, name='get-business-idea'),
    path('api/business-ideas/<uuid:project_id>/generate-assets/', generate_assets, name='generate-assets'),

    # Session 394: Brand Recommendations API
    path('api/brand-recommendations/', get_brand_recommendations, name='brand-recommendations'),

    # Session 327: Project-Scoped Agent Intelligence APIs
    path('api/projects/<uuid:project_id>/intelligence/', get_project_intelligence_overview, name='project-intelligence'),
    path('api/projects/<uuid:project_id>/intelligence/learning/', get_project_learning, name='project-intelligence-learning'),
    path('api/projects/<uuid:project_id>/intelligence/conversations/', get_project_conversations, name='project-intelligence-conversations'),
    path('api/projects/<uuid:project_id>/intelligence/conversations/trigger/', trigger_project_conversation, name='project-trigger-conversation'),
    path('api/projects/<uuid:project_id>/intelligence/dreams/', get_project_dreams, name='project-intelligence-dreams'),
    path('api/projects/<uuid:project_id>/intelligence/boardroom/', get_project_boardroom, name='project-intelligence-boardroom'),

    # Session 328: Project-Scoped Spider & Agent Slack APIs
    path('api/projects/<uuid:project_id>/intelligence/spiders/', get_project_spiders, name='project-intelligence-spiders'),
    path('api/projects/<uuid:project_id>/intelligence/spiders/refresh/', refresh_project_spiders, name='project-refresh-spiders'),
    path('api/projects/<uuid:project_id>/intelligence/slack/', get_project_slack_channel, name='project-intelligence-slack'),
    path('api/projects/<uuid:project_id>/intelligence/slack/message/', post_project_slack_message, name='project-slack-message'),

    # Session 326: Research Feedback & Learning Bridge APIs
    path('api/research/feedback/', submit_research_feedback, name='submit-research-feedback'),
    path('api/research/<uuid:research_id>/feedback/', get_research_feedback, name='get-research-feedback'),
    path('api/research/sync/', trigger_knowledge_sync, name='trigger-knowledge-sync'),
    path('api/spiders/priorities/', get_spider_priorities, name='get-spider-priorities'),
    path('api/spiders/recalculate-priorities/', trigger_priority_recalculation, name='recalculate-spider-priorities'),

    # Session 429: Discord Account Linking APIs
    path('api/discord/generate-link-code/', generate_discord_link_code, name='discord-generate-link-code'),
    path('api/discord/status/', get_discord_status, name='discord-status'),
    path('api/discord/unlink/', unlink_discord, name='discord-unlink'),
    path('api/discord/verify-link-code/', verify_discord_link_code, name='discord-verify-link-code'),

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

    # Session 223: Opportunity Engine API (Phase 1 - Creative Intelligence Empire)
    path('api/opportunities/', opportunity_list, name='opportunity-list'),
    path('api/opportunities/top/', opportunity_top, name='opportunity-top'),
    path('api/opportunities/stats/', opportunity_stats, name='opportunity-stats'),
    path('api/opportunities/score/', opportunity_score, name='opportunity-score'),
    path('api/opportunities/analyze/', opportunity_analyze, name='opportunity-analyze'),
    path('api/opportunities/<uuid:opportunity_id>/', opportunity_detail, name='opportunity-detail'),
    path('api/opportunities/<uuid:opportunity_id>/act/', opportunity_act, name='opportunity-act'),
    path('api/opportunities/<uuid:opportunity_id>/rescore/', opportunity_rescore, name='opportunity-rescore'),

    # Session 224: Revenue Reality API (Phase 2 - Creative Intelligence Empire)
    path('api/opportunities/revenue/stats/', revenue_stats, name='revenue-stats'),
    path('api/opportunities/<uuid:opportunity_id>/revenue/', opportunity_log_revenue, name='opportunity-log-revenue'),
    path('api/opportunities/<uuid:opportunity_id>/revenue/list/', opportunity_revenue_list, name='opportunity-revenue-list'),
    path('api/opportunities/<uuid:opportunity_id>/content/', opportunity_link_content, name='opportunity-link-content'),
    path('api/opportunities/<uuid:opportunity_id>/content/list/', opportunity_content_list, name='opportunity-content-list'),

    # Session 425: Opportunity Pipeline Automation - Task Management API
    path('api/opportunity-tasks/', opportunity_task_list, name='opportunity-task-list'),
    path('api/opportunity-tasks/stats/', opportunity_task_stats, name='opportunity-task-stats'),
    path('api/opportunity-tasks/<uuid:task_id>/', opportunity_task_detail, name='opportunity-task-detail'),
    path('api/opportunity-tasks/<uuid:task_id>/accept/', opportunity_task_accept, name='opportunity-task-accept'),
    path('api/opportunity-tasks/<uuid:task_id>/apply/', opportunity_task_apply, name='opportunity-task-apply'),
    path('api/opportunity-tasks/<uuid:task_id>/won/', opportunity_task_won, name='opportunity-task-won'),
    path('api/opportunity-tasks/<uuid:task_id>/lost/', opportunity_task_lost, name='opportunity-task-lost'),
    path('api/opportunity-tasks/<uuid:task_id>/action-items/', opportunity_task_update_action_items, name='opportunity-task-action-items'),

    # Session 227: Team Power API (Phase 3 - Multi-Agent Collaboration)
    path('api/teams/', list_teams, name='teams-list'),
    path('api/teams/create/', create_team, name='teams-create'),
    path('api/teams/stats/', team_stats, name='teams-stats'),
    path('api/teams/roles/', list_agent_roles, name='teams-roles-list'),
    path('api/teams/roles/create/', create_agent_role, name='teams-roles-create'),
    path('api/teams/<uuid:team_id>/', get_team, name='teams-detail'),
    path('api/teams/<uuid:team_id>/members/', add_team_member, name='teams-add-member'),
    path('api/teams/messages/', send_agent_message, name='teams-messages-send'),
    path('api/teams/messages/<uuid:agent_id>/', get_agent_messages, name='teams-messages-agent'),
    path('api/teams/messages/thread/<uuid:thread_id>/', get_message_thread, name='teams-messages-thread'),
    path('api/teams/workflows/', create_team_workflow, name='teams-workflows-create'),
    path('api/teams/workflows/<uuid:workflow_id>/', get_team_workflow, name='teams-workflows-detail'),
    path('api/teams/workflows/<uuid:workflow_id>/start/', start_team_workflow, name='teams-workflows-start'),
    path('api/teams/workflows/<uuid:workflow_id>/steps/<uuid:step_id>/complete/', complete_workflow_step, name='teams-workflows-step-complete'),

    # Session 228: Workflow Engine API
    path('api/teams/workflows/templates/', team_workflow_templates, name='teams-workflows-templates'),
    path('api/teams/workflows/active/', list_active_workflows, name='teams-workflows-active'),
    path('api/teams/workflows/<uuid:workflow_id>/execute/', execute_workflow, name='teams-workflows-execute'),
    path('api/teams/workflows/<uuid:workflow_id>/run/', run_full_workflow, name='teams-workflows-run'),
    path('api/teams/workflows/<uuid:workflow_id>/status/', workflow_status, name='teams-workflows-status'),
    path('api/teams/workflows/<uuid:workflow_id>/steps/<uuid:step_id>/execute/', execute_workflow_step, name='teams-workflows-step-execute'),

    # Session 229: Smart Distribution API (Phase 4)
    path('api/distribution/platforms/', list_platforms, name='distribution-platforms'),
    path('api/distribution/platforms/create/', create_platform, name='distribution-platforms-create'),
    path('api/distribution/platforms/<uuid:platform_id>/', get_platform, name='distribution-platform-detail'),
    path('api/distribution/accounts/', list_user_accounts, name='distribution-accounts'),
    path('api/distribution/accounts/connect/', connect_platform, name='distribution-accounts-connect'),
    path('api/distribution/content/', list_distributions, name='distribution-content'),
    path('api/distribution/content/create/', create_distribution, name='distribution-content-create'),
    path('api/distribution/content/<uuid:distribution_id>/submit/', submit_distribution, name='distribution-content-submit'),
    path('api/distribution/content/<uuid:distribution_id>/publish/', publish_distribution, name='distribution-content-publish'),
    path('api/distribution/content/<uuid:distribution_id>/sale/', record_sale, name='distribution-content-sale'),
    path('api/distribution/recommendations/', get_recommendations, name='distribution-recommendations'),
    path('api/distribution/stats/', distribution_stats, name='distribution-stats'),
    path('api/distribution/analytics/<uuid:platform_id>/', platform_analytics, name='distribution-analytics'),
    path('api/distribution/seed/', seed_platforms_api, name='distribution-seed'),

    # Session 230: Platform Integration APIs (OAuth, Uploads)
    path('api/distribution/integrations/', list_platform_integrations, name='distribution-integrations'),
    # OAuth flows
    path('api/distribution/oauth/<str:platform>/connect/', oauth_connect, name='oauth-connect'),
    path('api/distribution/oauth/<str:platform>/callback/', oauth_callback, name='oauth-callback'),
    path('api/distribution/oauth/<str:platform>/refresh/', refresh_token, name='oauth-refresh'),
    path('api/distribution/oauth/<str:platform>/disconnect/', disconnect_platform, name='oauth-disconnect'),
    # Etsy API
    path('api/distribution/etsy/shop/', etsy_get_shop, name='etsy-shop'),
    path('api/distribution/etsy/listings/create/', etsy_create_listing, name='etsy-create-listing'),
    # Shutterstock API
    path('api/distribution/shutterstock/portfolio/', shutterstock_get_portfolio, name='shutterstock-portfolio'),
    path('api/distribution/shutterstock/submit/', shutterstock_submit_content, name='shutterstock-submit'),
    # Gumroad API
    path('api/distribution/gumroad/products/', gumroad_get_products, name='gumroad-products'),
    path('api/distribution/gumroad/products/create/', gumroad_create_product, name='gumroad-create-product'),
    # Revenue sync
    path('api/distribution/<str:platform>/sync-revenue/', sync_platform_revenue, name='sync-platform-revenue'),

    # Session 230: Auto-Distribution APIs
    path('api/distribution/auto/create/', create_auto_distribution, name='auto-distribution-create'),
    path('api/distribution/auto/settings/', auto_distribution_settings, name='auto-distribution-settings'),
    path('api/distribution/batch/', batch_distribute, name='batch-distribute'),
    path('api/distribution/scheduled/', list_scheduled_distributions, name='scheduled-distributions'),
    path('api/distribution/<uuid:distribution_id>/reschedule/', reschedule_distribution, name='reschedule-distribution'),
    path('api/distribution/<uuid:distribution_id>/cancel/', cancel_scheduled_distribution, name='cancel-distribution'),
    path('api/distribution/templates/', distribution_templates, name='distribution-templates'),
    path('api/distribution/templates/apply/', apply_distribution_template, name='apply-distribution-template'),

    # Session 230: Revenue Analytics APIs
    path('api/distribution/revenue/dashboard/', revenue_dashboard, name='revenue-dashboard'),
    path('api/distribution/revenue/platform/<str:platform_name>/', platform_revenue_detail, name='platform-revenue-detail'),
    path('api/distribution/revenue/compare/', compare_platforms, name='compare-platforms'),
    path('api/distribution/revenue/roi/', calculate_roi, name='calculate-roi'),
    path('api/distribution/revenue/forecast/', revenue_forecast, name='revenue-forecast'),
    path('api/distribution/revenue/goals/', revenue_goals, name='revenue-goals'),
    path('api/distribution/revenue/export/', export_revenue_data, name='export-revenue-data'),

    # Session 232: Learning Loop APIs (Phase 5)
    path('api/learning/dashboard/', learning_dashboard, name='learning-dashboard'),
    path('api/learning/patterns/', list_success_patterns, name='learning-patterns'),
    path('api/learning/patterns/<uuid:pattern_id>/', pattern_detail, name='learning-pattern-detail'),
    path('api/learning/patterns/analyze/', analyze_patterns, name='learning-patterns-analyze'),
    path('api/learning/predict/', predict_performance, name='learning-predict'),
    path('api/learning/predictions/', list_predictions, name='learning-predictions'),
    path('api/learning/pricing/', get_pricing_optimization, name='learning-pricing'),
    path('api/learning/profile/', get_learning_profile, name='learning-profile'),
    path('api/learning/profile/update/', update_learning_profile, name='learning-profile-update'),
    path('api/learning/insights/', list_insights, name='learning-insights'),
    path('api/learning/insights/generate/', generate_insights, name='learning-insights-generate'),
    path('api/learning/insights/<uuid:insight_id>/read/', mark_insight_read, name='learning-insight-read'),
    path('api/learning/insights/<uuid:insight_id>/dismiss/', dismiss_insight, name='learning-insight-dismiss'),
    path('api/learning/compare/', get_performance_comparison, name='learning-compare'),

    # Session 449: Pipeline Learning APIs (Learning Loops for AI Content Pipeline)
    path('api/pipeline-learning/feedback/', pipeline_record_feedback, name='pipeline-learning-feedback'),
    path('api/pipeline-learning/engagement/', pipeline_record_engagement, name='pipeline-learning-engagement'),
    path('api/pipeline-learning/recommend/style/', pipeline_recommend_style, name='pipeline-learning-recommend-style'),
    path('api/pipeline-learning/recommend/voice/', pipeline_recommend_voice, name='pipeline-learning-recommend-voice'),
    path('api/pipeline-learning/leaderboard/styles/', pipeline_style_leaderboard, name='pipeline-learning-style-leaderboard'),
    path('api/pipeline-learning/insights/', pipeline_get_insights, name='pipeline-learning-insights'),
    path('api/pipeline-learning/insights/generate/', pipeline_generate_insights, name='pipeline-learning-insights-generate'),
    path('api/pipeline-learning/stats/', pipeline_get_statistics, name='pipeline-learning-stats'),

    # Session 234: Proactive System APIs (Phase 6)
    # Dashboard & Overview
    path('api/proactive/dashboard/', proactive_dashboard, name='proactive-dashboard'),
    path('api/proactive/check/', run_proactive_check, name='proactive-check'),

    # Alerts API
    path('api/proactive/alerts/', list_alerts, name='proactive-alerts'),
    path('api/proactive/alerts/create/', create_alert, name='proactive-alerts-create'),
    path('api/proactive/alerts/<uuid:alert_id>/', alert_detail, name='proactive-alert-detail'),
    path('api/proactive/alerts/<uuid:alert_id>/toggle/', toggle_alert, name='proactive-alert-toggle'),
    path('api/proactive/alerts/check/', check_alerts, name='proactive-alerts-check'),

    # Notifications API
    path('api/proactive/notifications/', list_notifications, name='proactive-notifications'),
    path('api/proactive/notifications/<uuid:notification_id>/read/', mark_notification_read, name='proactive-notification-read'),
    path('api/proactive/notifications/<uuid:notification_id>/dismiss/', dismiss_notification, name='proactive-notification-dismiss'),
    path('api/proactive/notifications/read-all/', mark_all_notifications_read, name='proactive-notifications-read-all'),
    path('api/proactive/notifications/preferences/', notification_preferences, name='proactive-notification-preferences'),

    # Suggestions API
    path('api/proactive/suggestions/', list_suggestions, name='proactive-suggestions'),
    path('api/proactive/suggestions/generate/', generate_suggestions, name='proactive-suggestions-generate'),
    path('api/proactive/suggestions/<uuid:suggestion_id>/', suggestion_detail, name='proactive-suggestion-detail'),

    # Automations API
    path('api/proactive/automations/', list_automations, name='proactive-automations'),
    path('api/proactive/automations/create/', create_automation, name='proactive-automations-create'),
    path('api/proactive/automations/<uuid:automation_id>/', automation_detail, name='proactive-automation-detail'),
    path('api/proactive/automations/<uuid:automation_id>/execute/', execute_automation, name='proactive-automation-execute'),
    path('api/proactive/automations/<uuid:automation_id>/toggle/', toggle_automation, name='proactive-automation-toggle'),
    path('api/proactive/automations/<uuid:automation_id>/logs/', automation_logs, name='proactive-automation-logs'),

    # Session 235: A/B Testing Framework APIs (Phase 6)
    path('api/ab-testing/dashboard/', ab_testing_dashboard, name='ab-testing-dashboard'),
    path('api/ab-testing/tests/', list_tests, name='ab-testing-tests'),
    path('api/ab-testing/tests/create/', create_test, name='ab-testing-create'),
    path('api/ab-testing/tests/<uuid:test_id>/', test_detail, name='ab-testing-detail'),
    path('api/ab-testing/tests/<uuid:test_id>/start/', start_test, name='ab-testing-start'),
    path('api/ab-testing/tests/<uuid:test_id>/pause/', pause_test, name='ab-testing-pause'),
    path('api/ab-testing/tests/<uuid:test_id>/complete/', complete_test, name='ab-testing-complete'),
    path('api/ab-testing/tests/<uuid:test_id>/results/', test_results, name='ab-testing-results'),
    path('api/ab-testing/tests/<uuid:test_id>/variants/', add_variant, name='ab-testing-add-variant'),
    path('api/ab-testing/variants/<uuid:variant_id>/', variant_detail, name='ab-testing-variant-detail'),
    path('api/ab-testing/variants/<uuid:variant_id>/event/', record_event, name='ab-testing-record-event'),

    # Session 264: Super Platform Coordinator API (Phase 1 - Unified Intelligence)
    path('api/super-platform/process/', SuperPlatformProcessView.as_view(), name='super-platform-process'),
    path('api/super-platform/classify/', SuperPlatformClassifyView.as_view(), name='super-platform-classify'),
    path('api/super-platform/status/', SuperPlatformStatusView.as_view(), name='super-platform-status'),
    path('api/super-platform/ask/', SuperPlatformQuickAskView.as_view(), name='super-platform-ask'),

    # Goals API
    path('api/goals/', list_goals, name='goals-list'),
    path('api/goals/create/', create_goal, name='goals-create'),
    path('api/goals/<uuid:goal_id>/', goal_detail, name='goals-detail'),
    path('api/goals/<uuid:goal_id>/progress/', update_goal_progress, name='goals-update-progress'),

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
    path('api/agents/', all_agents_list, name='agents-list'),  # Session 267: Add agents list endpoint for sci-fi features
    path('api/agents/assigned/', agents_assigned, name='agents-assigned'),
    path('api/agents/<uuid:agent_id>/profile/', get_agent_profile, name='agent-profile'),  # Session 417: Agent Profile
    # Session 417: Detail endpoints for conversations, decisions, dreams, hivemind
    path('api/conversations/<uuid:conversation_id>/', get_conversation_detail, name='conversation-detail'),
    path('api/hivemind/<uuid:session_id>/', get_hivemind_detail, name='hivemind-detail'),
    path('api/decisions/<uuid:decision_id>/', get_decision_detail, name='decision-detail'),
    path('api/dreams/<uuid:dream_id>/', get_dream_detail, name='dream-detail'),
    path('api/commands/execute/', execute_command, name='execute-command'),

    # Session 206: Preferences Dashboard APIs
    path('api/preferences/', get_all_preferences, name='preferences-all'),
    path('api/preferences/stats/', preference_stats, name='preferences-stats'),
    path('api/preferences/history/', preference_history, name='preferences-history'),
    path('api/preferences/clear/', clear_all_preferences, name='preferences-clear-all'),
    path('api/preferences/learn/', learn_from_project, name='preferences-learn'),
    path('api/preferences/suggestions/', smart_style_suggestions, name='preferences-suggestions'),
    path('api/preferences/apply-suggestion/', apply_style_suggestion, name='preferences-apply-suggestion'),

    # Session 210: Implicit Learning & Recommendations API
    # NOTE: These must come BEFORE the <str:domain> catch-all pattern!
    path('api/preferences/track/', track_behavior, name='preferences-track-behavior'),
    path('api/preferences/implicit/', get_implicit_preferences, name='preferences-implicit'),
    path('api/preferences/recommendations/', get_style_recommendations, name='preferences-recommendations'),
    path('api/preferences/recommendations/similar/<str:style>/', get_similar_styles, name='preferences-similar-styles'),
    path('api/preferences/recommendations/discover/', get_discovery_styles, name='preferences-discover-styles'),
    # Session 210: Style Evolution Tracking
    path('api/preferences/evolution/', get_style_evolution, name='preferences-evolution'),
    path('api/preferences/evolution/snapshot/', record_evolution_snapshot, name='preferences-evolution-snapshot'),
    path('api/preferences/evolution/shifts/', get_style_shifts, name='preferences-evolution-shifts'),

    # Session 211: A/B Testing Framework API
    path('api/experiments/', list_experiments, name='experiments-list'),
    path('api/experiments/create/', create_experiment, name='experiments-create'),
    path('api/experiments/<str:experiment_id>/start/', start_experiment, name='experiments-start'),
    path('api/experiments/<str:experiment_id>/stop/', stop_experiment, name='experiments-stop'),
    path('api/experiments/<str:experiment_id>/results/', get_experiment_results, name='experiments-results'),
    path('api/experiments/<str:experiment_id>/variant/', get_my_variant, name='experiments-variant'),
    path('api/experiments/<str:experiment_id>/convert/', track_ab_conversion, name='experiments-convert'),

    # Session 213: Workflow Management API
    path('api/workflows/', workflows_list_create, name='workflows-list-create'),
    path('api/workflows/builtin/', builtin_workflows, name='workflows-builtin'),
    path('api/workflows/agents/', available_agents, name='workflows-agents'),
    path('api/workflows/executions/', execution_list, name='workflow-executions'),
    path('api/workflows/executions/<str:execution_id>/', execution_detail, name='workflow-execution-detail'),
    path('api/workflows/public/', public_workflows, name='workflows-public'),
    path('api/workflows/shared/<str:slug>/', shared_workflow, name='workflow-shared'),
    path('api/workflows/shared/<str:slug>/import/', import_shared_workflow, name='workflow-import'),
    path('api/workflows/<str:workflow_id>/', workflow_detail, name='workflow-detail'),
    path('api/workflows/<str:workflow_id>/execute/', workflow_execute, name='workflow-execute'),
    path('api/workflows/<str:workflow_id>/duplicate/', workflow_duplicate, name='workflow-duplicate'),
    path('api/workflows/<str:workflow_id>/schedule/', workflow_schedule, name='workflow-schedule'),
    path('api/workflows/<str:workflow_id>/share/', workflow_share, name='workflow-share'),
    path('api/workflows/<str:workflow_id>/unshare/', workflow_unshare, name='workflow-unshare'),

    # Session 240: New Workflow Engine v2 (user-vision-first philosophy)
    # User's style/subject = SACRED | System ENHANCES with trending colors/moods
    path('api/v2/workflow/execute/', execute_workflow_v2, name='workflow-v2-execute'),
    path('api/v2/workflow/parse/', parse_intent, name='workflow-v2-parse'),

    # Session 214: Agent Collaboration API
    path('api/collaboration/request/', request_collaboration, name='collaboration-request'),
    path('api/collaboration/history/', collaboration_history, name='collaboration-history'),
    path('api/collaboration/stats/', get_collaboration_stats, name='collaboration-stats'),
    path('api/collaboration/find-collaborator/', find_collaborator, name='collaboration-find'),
    path('api/collaboration/delegate/', delegate_task, name='collaboration-delegate'),
    path('api/collaboration/consult/', request_consultation, name='collaboration-consult'),
    path('api/collaboration/<str:collaboration_id>/', get_collaboration, name='collaboration-detail'),
    path('api/collaboration/<str:collaboration_id>/respond/', respond_to_collaboration, name='collaboration-respond'),
    # Messages
    path('api/collaboration/messages/send/', send_message, name='collaboration-message-send'),
    path('api/collaboration/messages/', get_messages, name='collaboration-messages'),
    path('api/collaboration/messages/<str:message_id>/processed/', mark_message_processed, name='collaboration-message-processed'),
    # Knowledge
    path('api/collaboration/knowledge/share/', share_knowledge, name='collaboration-knowledge-share'),
    path('api/collaboration/knowledge/', search_knowledge, name='collaboration-knowledge'),
    path('api/collaboration/knowledge/<str:knowledge_id>/learn/', learn_knowledge, name='collaboration-knowledge-learn'),
    path('api/collaboration/knowledge/<str:knowledge_id>/rate/', rate_knowledge, name='collaboration-knowledge-rate'),
    # Performance
    path('api/collaboration/performance/', get_agent_performance, name='collaboration-performance'),
    path('api/collaboration/top-performers/', get_top_performers, name='collaboration-top-performers'),

    # Session 215: Collective Intelligence API
    path('api/collective/insights/', aggregate_insights, name='collective-insights'),
    path('api/collective/report/', generate_report, name='collective-report'),
    path('api/collective/knowledge-gaps/', get_knowledge_gaps, name='collective-knowledge-gaps'),
    path('api/collective/knowledge-gaps/resolve/', resolve_knowledge_gap, name='collective-resolve-gap'),  # Session 373
    path('api/collective/knowledge-gaps/resolve-all/', resolve_all_knowledge_gaps, name='collective-resolve-all-gaps'),  # Session 373
    path('api/collective/fix-collaboration/', fix_collaboration, name='collective-fix-collaboration'),  # Session 373
    path('api/collective/boost-agent/', boost_agent, name='collective-boost-agent'),  # Session 373
    path('api/collective/improvements/', get_agent_improvements, name='collective-improvements'),
    path('api/collective/monitor/', get_collaboration_monitor, name='collective-monitor'),
    path('api/collective/network/', get_collaboration_network, name='collective-network'),
    path('api/collective/orchestrate/', orchestrate_task, name='collective-orchestrate'),
    path('api/collective/stats/', get_collective_stats, name='collective-stats'),
    path('api/collective/dashboard/', get_dashboard_data, name='collective-dashboard'),
    path('api/collective/agents/<str:agent_name>/', get_agent_collective_profile, name='collective-agent-profile'),

    # Domain preferences (catch-all - must be LAST in preferences routes)
    path('api/preferences/<str:domain>/', domain_preferences, name='preferences-domain'),

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

    # Session 430: User Interview System
    path('api/interview/start/', start_interview, name='interview-start'),
    path('api/interview/respond/', respond_interview, name='interview-respond'),
    path('api/interview/status/', interview_status, name='interview-status'),
    path('api/interview/resume/', resume_interview, name='interview-resume'),
    path('api/profile/summary/', get_user_profile_summary, name='profile-summary'),

    # Session 456: Voice Interview (Whisper transcription)
    path('api/interview/voice/', voice_interview_response, name='interview-voice'),
    path('api/transcribe/', transcribe_only, name='transcribe-only'),

    # Session 457: Certifications
    path('api/certifications/', list_certifications, name='certifications-list'),
    path('api/certifications/add/', add_certification, name='certifications-add'),
    path('api/certifications/<int:cert_id>/delete/', delete_certification, name='certifications-delete'),

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

    # Session 217: Chart.js Analytics API
    path('api/analytics/charts/agent-trends/', get_chart_agent_trends, name='chart-agent-trends'),
    path('api/analytics/charts/agent-comparison/', get_chart_agent_comparison, name='chart-agent-comparison'),
    path('api/analytics/charts/agent-heatmap/', get_chart_agent_heatmap, name='chart-agent-heatmap'),
    path('api/analytics/charts/workflow-trends/', get_chart_workflow_trends, name='chart-workflow-trends'),
    path('api/analytics/charts/workflow-success/', get_chart_workflow_success, name='chart-workflow-success'),
    path('api/analytics/charts/knowledge-growth/', get_chart_knowledge_growth, name='chart-knowledge-growth'),
    path('api/analytics/charts/knowledge-domains/', get_chart_knowledge_domains, name='chart-knowledge-domains'),
    path('api/analytics/charts/system-health/', get_chart_system_health, name='chart-system-health'),
    path('api/analytics/charts/dashboard/', get_chart_dashboard, name='chart-dashboard'),

    # Session 221: Advanced Analytics Phase F
    path('api/analytics/v2/overview/', analytics_overview_v2, name='analytics-overview-v2'),
    path('api/analytics/v2/usage-timeline/', usage_timeline_v2, name='usage-timeline-v2'),
    path('api/analytics/v2/performance-timeline/', performance_timeline_v2, name='performance-timeline-v2'),
    path('api/analytics/v2/cost-breakdown/', cost_breakdown_v2, name='cost-breakdown-v2'),
    path('api/analytics/v2/dashboards/', analytics_dashboards_v2, name='analytics-dashboards-v2'),
    path('api/analytics/v2/alerts/', analytics_alerts_v2, name='analytics-alerts-v2'),
    path('api/analytics/v2/realtime/', realtime_stats_v2, name='realtime-stats-v2'),
    path('api/analytics/v2/track/', track_event_v2, name='track-event-v2'),

    # Session 217B: Agent Training API
    path('api/training/agents/', training_list_agents, name='training-list-agents'),
    path('api/training/agents/from-template/', create_from_template, name='training-create-from-template'),
    path('api/training/agents/<str:agent_name>/', training_get_agent, name='training-get-agent'),
    path('api/training/agents/<str:agent_name>/update/', training_update_agent, name='training-update-agent'),
    path('api/training/agents/<str:agent_name>/capabilities/', add_capability, name='training-add-capability'),
    path('api/training/agents/<str:agent_name>/capabilities/<str:capability_id>/', remove_capability, name='training-remove-capability'),
    path('api/training/capabilities/', list_capabilities, name='training-list-capabilities'),
    path('api/training/templates/', list_templates, name='training-list-templates'),
    path('api/training/history/', training_history, name='training-history'),
    path('api/training/stats/', training_stats, name='training-stats'),
    path('api/training/dashboard/', training_dashboard, name='training-dashboard'),

    # Session 383: Agent Chat & Invoke
    path('api/training/agents/chat/', agent_chat, name='training-agent-chat'),
    path('api/training/agents/invoke/', agent_invoke, name='training-agent-invoke'),

    # Session 217C: Workflow Analytics API
    path('api/workflow-analytics/history/', wf_execution_history, name='wf-execution-history'),
    path('api/workflow-analytics/trends/', wf_execution_trends, name='wf-execution-trends'),
    path('api/workflow-analytics/success-failure/', wf_success_failure, name='wf-success-failure'),
    path('api/workflow-analytics/performance/', wf_performance_metrics, name='wf-performance-metrics'),
    path('api/workflow-analytics/performance-comparison/', wf_performance_comparison, name='wf-performance-comparison'),
    path('api/workflow-analytics/compare/', wf_compare_workflows, name='wf-compare-workflows'),
    path('api/workflow-analytics/steps/<int:workflow_id>/', wf_step_performance, name='wf-step-performance'),
    path('api/workflow-analytics/heatmap/', wf_execution_heatmap, name='wf-execution-heatmap'),
    path('api/workflow-analytics/summary/', wf_analytics_summary, name='wf-analytics-summary'),
    path('api/workflow-analytics/dashboard/', wf_analytics_dashboard, name='wf-analytics-dashboard'),

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

    # Session 458: Chat Voice Output - TTS for assistant responses
    path('api/tts/speak/', lambda r: __import__('core.views_audio', fromlist=['speak_text']).speak_text(r), name='tts-speak'),
    path('api/tts/settings/', lambda r: __import__('core.views_audio', fromlist=['get_user_voice_settings']).get_user_voice_settings(r), name='tts-settings'),

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
    path('api/images/<uuid:image_id>/view/', serve_image, name='serve-image'),  # Session 293: Serve image data
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
    # Session 237: Portfolio Delete APIs
    path('api/portfolio/<str:item_type>/<uuid:item_id>/delete/', delete_portfolio_item, name='delete-portfolio-item'),
    path('api/portfolio/bulk-delete/', bulk_delete_portfolio_items, name='bulk-delete-portfolio'),
    path('api/portfolio/check-broken/', check_portfolio_broken_links, name='check-broken-portfolio'),
    # Session 237: Redirect legacy broken URLs (cached in browsers from old versions)
    re_path(r'^api/portfolio/generated_images/(?P<path>.+)$', legacy_portfolio_image_redirect, name='legacy-portfolio-redirect'),

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

    # Session 402: Document Ingestion APIs
    path('api/documents/', list_documents, name='documents-list'),
    path('api/documents/ingest-url/', ingest_url, name='documents-ingest-url'),
    path('api/documents/ingest-file/', ingest_file, name='documents-ingest-file'),
    path('api/documents/<uuid:document_id>/', get_document, name='documents-get'),
    path('api/documents/<uuid:document_id>/delete/', delete_document, name='documents-delete'),

    # Session 403: Legal Case Files APIs
    path('api/legal/case-files/', list_legal_case_files, name='legal-case-files-list'),
    path('api/legal/case-files/upload/', upload_legal_case_file, name='legal-case-files-upload'),
    path('api/legal/case-files/<uuid:document_id>/', get_legal_case_file, name='legal-case-files-get'),
    path('api/legal/case-files/<uuid:document_id>/analyze/', analyze_legal_case_file, name='legal-case-files-analyze'),
    path('api/legal/case-files/<uuid:document_id>/delete/', delete_legal_case_file, name='legal-case-files-delete'),
    # Session 407: Document section export
    path('api/legal/export-section/', export_legal_section, name='legal-export-section'),

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

    # Session 208: Spider Intelligence API - Agents query spider data
    path('api/spider-intelligence/trends/', trending_topics, name='spider-intelligence-trends'),
    path('api/spider-intelligence/market/', market_insights, name='spider-intelligence-market'),
    path('api/spider-intelligence/tech/', tech_trends, name='spider-intelligence-tech'),
    path('api/spider-intelligence/jobs/', job_market, name='spider-intelligence-jobs'),
    path('api/spider-intelligence/search/', search_data, name='spider-intelligence-search'),
    path('api/spider-intelligence/summary/', data_summary, name='spider-intelligence-summary'),
    path('api/spider-intelligence/insights/', prompt_insights, name='spider-intelligence-insights'),
    path('api/spider-intelligence/report/', daily_report, name='spider-intelligence-report'),

    # Session 343: Spider registry and testing endpoints
    path('api/spider-intelligence/registry/', spider_registry, name='spider-intelligence-registry'),
    path('api/spider-intelligence/test/', test_spider, name='spider-intelligence-test'),
    path('api/spider-intelligence/run-all/', run_all_spiders, name='spider-intelligence-run-all'),

    # Session 344: Enhanced market research dashboard
    path('api/spider-intelligence/market-research/', market_research_dashboard, name='spider-intelligence-market-research'),

    # Session 345: Unified dashboard stats endpoint
    path('api/spider-intelligence/dashboard-stats/', spider_dashboard_stats, name='spider-intelligence-dashboard-stats'),

    # Session 385: Opportunities dashboard (freelance, jobs, crowdfunding, startups)
    path('api/spider-intelligence/opportunities/', opportunities_dashboard, name='spider-intelligence-opportunities'),

    # Session 399: Spider Data UI - Data Feed, Knowledge, Timeline
    path('api/spider-intelligence/feed/', spider_data_feed, name='spider-intelligence-feed'),
    path('api/spider-intelligence/knowledge/', spider_knowledge, name='spider-intelligence-knowledge'),
    path('api/spider-intelligence/timeline/', spider_timeline, name='spider-intelligence-timeline'),

    # Session 388: Income Action Pipeline - Spider to Income Bridge
    path('api/income/save-opportunity/', income_save_opportunity, name='income-save-opportunity'),
    path('api/income/generate-application/', income_generate_application, name='income-generate-application'),
    path('api/income/update-status/', income_update_status, name='income-update-status'),
    path('api/income/opportunities/', income_get_opportunities, name='income-opportunities'),
    path('api/income/statistics/', income_get_statistics, name='income-statistics'),
    path('api/income/quick-apply/', income_quick_apply, name='income-quick-apply'),

    # Session 219: Agent Intelligence API - Phase A Spider-Agent Integration
    path('api/agent-intelligence/agents/', ai_agents_list, name='ai-agents-list'),
    path('api/agent-intelligence/feed/<str:agent_name>/', ai_agent_feed, name='ai-agent-feed'),
    path('api/agent-intelligence/trends/', ai_trends, name='ai-trends'),
    path('api/agent-intelligence/suggestions/', ai_suggestions, name='ai-suggestions'),
    path('api/agent-intelligence/stats/', ai_stats, name='ai-stats'),
    path('api/agent-intelligence/categories/', ai_categories, name='ai-categories'),
    path('api/agent-intelligence/capabilities/', ai_capabilities, name='ai-capabilities'),
    path('api/agent-intelligence/bridge/', ai_bridge_status, name='ai-bridge-status'),
    path('api/agent-intelligence/test/', ai_inject_test, name='ai-inject-test'),

    # Session 219 Phase B: Agent Collaboration API
    path('api/agent-collab/message/', collab_send_message, name='collab-send-message'),
    path('api/agent-collab/messages/<str:agent_name>/', collab_get_messages, name='collab-get-messages'),
    path('api/agent-collab/collaborate/', collab_initiate, name='collab-initiate'),
    path('api/agent-collab/consult/', collab_consult, name='collab-consult'),
    path('api/agent-collab/consensus/', collab_request_consensus, name='collab-request-consensus'),
    path('api/agent-collab/vote/', collab_submit_vote, name='collab-submit-vote'),
    path('api/agent-collab/consensus/<str:consensus_id>/', collab_consensus_status, name='collab-consensus-status'),
    path('api/agent-collab/knowledge/', collab_share_knowledge, name='collab-share-knowledge'),
    path('api/agent-collab/knowledge/query/', collab_query_knowledge, name='collab-query-knowledge'),
    path('api/agent-collab/stats/', collab_stats, name='collab-stats'),
    path('api/agent-collab/activity/<str:agent_name>/', collab_agent_activity, name='collab-agent-activity'),

    # Session 219 Phase C: Agent Learning API
    path('api/agent-learning/interaction/', learning_record, name='learning-record'),
    path('api/agent-learning/preferences/<str:agent_name>/', learning_preferences, name='learning-preferences'),
    path('api/agent-learning/context/<str:agent_name>/', learning_context, name='learning-context'),
    path('api/agent-learning/stats/', learning_stats, name='learning-stats'),
    path('api/agent-learning/apply/', learning_apply, name='learning-apply'),
    path('api/agent-learning/clear/', learning_clear, name='learning-clear'),
    path('api/agent-learning/summary/<str:agent_name>/', learning_summary, name='learning-summary'),
    path('api/agent-learning/share/<str:agent_name>/', learning_share, name='learning-share'),
    path('api/agent-learning/all-preferences/', learning_all, name='learning-all'),
    # Session 248: Knowledge Transfer Activity Feed
    path('api/agent-learning/activity/', get_knowledge_transfer_feed, name='learning-activity'),

    # Session 244: Agent Conversations API
    path('api/agent-conversations/', get_agent_conversations, name='agent-conversations'),
    path('api/agent-conversations/trigger/', trigger_agent_conversation, name='trigger-agent-conversation'),

    # Session 247: Agent Dreams API
    path('api/agent-dreams/', get_agent_dreams, name='agent-dreams'),
    path('api/agent-dreams/trigger/', trigger_agent_dreams, name='trigger-agent-dreams'),
    path('api/agent-dreams/mark-shown/', mark_dreams_shown, name='mark-dreams-shown'),
    path('api/agent-dreams/<uuid:dream_id>/react/', react_to_dream, name='react-to-dream'),
    # Session 249: Dream Feedback System
    path('api/agent-dreams/preferences/', get_dream_preferences, name='dream-preferences'),
    path('api/agent-dreams/explorations/<uuid:exploration_id>/', get_dream_exploration, name='dream-exploration'),

    # Session 323: Boardroom Decisions API
    path('api/boardroom/decisions/', get_boardroom_decisions, name='boardroom-decisions'),
    path('api/boardroom/decisions/<uuid:decision_id>/promote/', promote_decision, name='promote-decision'),
    path('api/boardroom/decisions/<uuid:decision_id>/reject/', reject_decision, name='reject-decision'),

    # Session 368: Dream Validation UI API
    path('api/boardroom/dreams/', get_boardroom_dreams, name='boardroom-dreams'),
    path('api/boardroom/dreams/<uuid:dream_id>/decide/', decide_dream, name='decide-dream'),
    path('api/dream-implementations/', get_dream_implementations, name='dream-implementations'),
    path('api/dream-implementations/<uuid:implementation_id>/validate/', validate_implementation, name='validate-implementation'),
    path('api/dream-implementations/metrics/', get_validation_metrics, name='validation-metrics'),
    path('api/agent-dreams/<uuid:dream_id>/rate/', rate_dream, name='rate-dream'),

    # Session 250: Hive Mind Mode API
    path('api/hive-mind/start/', start_hive_mind_session, name='hive-mind-start'),
    path('api/hive-mind/session/<uuid:session_id>/', get_hive_mind_session, name='hive-mind-session'),
    path('api/hive-mind/sessions/', list_hive_mind_sessions, name='hive-mind-sessions'),
    path('api/hive-mind/agents/', get_available_agents, name='hive-mind-agents'),
    path('api/hive-mind/preview/', preview_agents, name='hive-mind-preview'),

    # Session 251: Memory Palace API
    path('api/memory-palace/', get_memory_palace_overview, name='memory-palace-overview'),
    path('api/memory-palace/agent/<uuid:agent_id>/memories/', get_agent_memories, name='memory-palace-agent-memories'),
    path('api/memory-palace/agent/<uuid:agent_id>/rooms/', get_memory_palace_rooms, name='memory-palace-rooms'),
    path('api/memory-palace/agent/<uuid:agent_id>/summary/', get_memory_summary, name='memory-palace-summary'),
    path('api/memory-palace/memory/<uuid:memory_id>/', get_memory_detail, name='memory-palace-detail'),
    path('api/memory-palace/memory/<uuid:memory_id>/delete/', delete_memory, name='memory-palace-delete'),
    path('api/memory-palace/memory/<uuid:memory_id>/connections/', get_memory_connections, name='memory-connections'),
    path('api/memory-palace/room/<uuid:room_id>/memories/', get_room_memories, name='memory-room-memories'),
    path('api/memory-palace/create/', create_memory, name='memory-create'),
    path('api/memory-palace/search/', search_memories, name='memory-search'),
    path('api/memory-palace/assign/', assign_memory_to_room, name='memory-assign-room'),
    path('api/memory-palace/connect/', connect_memories, name='memory-connect'),

    # Session 252: Agent Mood System API
    path('api/agent-mood/', get_mood_overview, name='agent-mood-overview'),
    path('api/agent-mood/agent/<uuid:agent_id>/', get_agent_mood, name='agent-mood-detail'),
    path('api/agent-mood/agent/<uuid:agent_id>/set/', set_agent_mood, name='agent-mood-set'),
    path('api/agent-mood/agent/<uuid:agent_id>/history/', get_mood_history, name='agent-mood-history'),
    path('api/agent-mood/agent/<uuid:agent_id>/prompt-context/', get_mood_prompt_context, name='agent-mood-prompt'),
    path('api/agent-mood/rules/', get_mood_rules, name='agent-mood-rules'),
    path('api/agent-mood/rules/create/', create_mood_rule, name='agent-mood-rule-create'),
    path('api/agent-mood/rules/<uuid:rule_id>/delete/', delete_mood_rule, name='agent-mood-rule-delete'),
    path('api/agent-mood/trigger-from-memory/', trigger_mood_from_memory, name='agent-mood-from-memory'),

    # Session 253: Agent Rivalries & Alliances API
    path('api/agent-relationships/', get_relationships_overview, name='agent-relationships-overview'),
    path('api/agent-relationships/agent/<uuid:agent_id>/', get_agent_relationships, name='agent-relationships-detail'),
    path('api/agent-relationships/create/', create_relationship, name='agent-relationship-create'),
    path('api/agent-relationships/relationship/<uuid:relationship_id>/interact/', record_interaction, name='agent-relationship-interact'),
    path('api/agent-relationships/relationship/<uuid:relationship_id>/events/', get_relationship_events, name='agent-relationship-events'),
    path('api/agent-relationships/auto-generate/', auto_generate_relationships, name='agent-relationships-auto'),
    # Alliances
    path('api/agent-relationships/alliances/<uuid:alliance_id>/', get_alliance, name='agent-alliance-detail'),
    path('api/agent-relationships/alliances/create/', create_alliance, name='agent-alliance-create'),
    path('api/agent-relationships/alliances/<uuid:alliance_id>/add/', add_alliance_member, name='agent-alliance-add'),
    path('api/agent-relationships/alliances/<uuid:alliance_id>/disband/', disband_alliance, name='agent-alliance-disband'),
    # Rivalries
    path('api/agent-relationships/rivalries/<uuid:rivalry_id>/', get_rivalry, name='agent-rivalry-detail'),
    path('api/agent-relationships/rivalries/create/', create_rivalry, name='agent-rivalry-create'),
    path('api/agent-relationships/rivalries/<uuid:rivalry_id>/compete/', record_competition, name='agent-rivalry-compete'),
    path('api/agent-relationships/rivalries/<uuid:rivalry_id>/end/', end_rivalry, name='agent-rivalry-end'),

    # Session 254: Agent Evolution System API
    path('api/agent-evolution/', get_evolution_overview, name='agent-evolution-overview'),
    path('api/agent-evolution/agent/<uuid:agent_id>/', get_agent_evolution, name='agent-evolution-detail'),
    path('api/agent-evolution/agent/<uuid:agent_id>/award-xp/', award_agent_xp, name='agent-evolution-award-xp'),
    path('api/agent-evolution/agent/<uuid:agent_id>/prestige/', prestige_agent, name='agent-evolution-prestige'),
    path('api/agent-evolution/agent/<uuid:agent_id>/task/', record_task_completion, name='agent-evolution-task'),
    path('api/agent-evolution/agent/<uuid:agent_id>/unlock/<uuid:ability_id>/', unlock_ability, name='agent-evolution-unlock'),
    path('api/agent-evolution/abilities/', get_available_abilities, name='agent-evolution-abilities'),
    path('api/agent-evolution/abilities/create/', create_ability, name='agent-evolution-ability-create'),
    path('api/agent-evolution/leaderboard/', get_xp_leaderboard, name='agent-evolution-leaderboard'),
    path('api/agent-evolution/xp-gains/', get_recent_xp_gains, name='agent-evolution-xp-gains'),
    path('api/agent-evolution/initialize/', initialize_all_evolutions, name='agent-evolution-initialize'),

    # Session 255: Time Travel Debugging API
    # Replay agent decisions and see what they were "thinking"
    path('api/time-travel/', get_time_travel_overview, name='time-travel-overview'),
    path('api/time-travel/session/<uuid:session_id>/', get_session_detail, name='time-travel-session-detail'),
    path('api/time-travel/session/start/', start_session, name='time-travel-start'),
    path('api/time-travel/session/<uuid:session_id>/end/', end_session, name='time-travel-end'),
    path('api/time-travel/session/<uuid:session_id>/bookmark/', toggle_bookmark_session, name='time-travel-bookmark-session'),
    path('api/time-travel/decision/', record_decision, name='time-travel-record-decision'),
    path('api/time-travel/decision/<uuid:decision_id>/outcome/', update_decision_outcome, name='time-travel-update-outcome'),
    path('api/time-travel/decision/<uuid:decision_id>/flag/', flag_decision, name='time-travel-flag'),
    path('api/time-travel/bookmark/', create_bookmark, name='time-travel-create-bookmark'),
    path('api/time-travel/bookmark/<uuid:bookmark_id>/', delete_bookmark, name='time-travel-delete-bookmark'),
    path('api/time-travel/annotation/', add_annotation, name='time-travel-add-annotation'),
    path('api/time-travel/annotation/<uuid:annotation_id>/', delete_annotation, name='time-travel-delete-annotation'),
    path('api/time-travel/search/', search_sessions, name='time-travel-search'),
    path('api/time-travel/flagged/', get_flagged_decisions, name='time-travel-flagged'),
    path('api/time-travel/agent/<uuid:agent_id>/sessions/', get_agent_sessions, name='time-travel-agent-sessions'),
    path('api/time-travel/agent/<uuid:agent_id>/simulate/', simulate_session, name='time-travel-simulate'),

    # Session 256: Agent Personality System API
    path('api/personality/', personality_overview, name='personality-overview'),
    path('api/personality/agent/<uuid:agent_id>/', agent_personality, name='personality-agent'),
    path('api/personality/agent/<uuid:agent_id>/generate/', generate_personality, name='personality-generate'),
    path('api/personality/generate-all/', generate_all_personalities, name='personality-generate-all'),
    path('api/personality/compatibility/<uuid:agent1_id>/<uuid:agent2_id>/', personality_compatibility, name='personality-compatibility'),
    path('api/personality/archetypes/', personality_archetypes, name='personality-archetypes'),

    # Session 257: Memory Clusters API
    path('api/memory-clusters/', clusters_overview, name='memory-clusters-overview'),
    path('api/memory-clusters/agent/<uuid:agent_id>/', agent_clusters, name='memory-clusters-agent'),
    path('api/memory-clusters/cluster/<uuid:cluster_id>/', cluster_detail, name='memory-clusters-detail'),
    path('api/memory-clusters/visualization/', cluster_visualization_data, name='memory-clusters-viz'),
    path('api/memory-clusters/visualization/<uuid:agent_id>/', cluster_visualization_data, name='memory-clusters-viz-agent'),
    path('api/memory-clusters/generate-all/', generate_all_clusters, name='memory-clusters-generate-all'),
    path('api/memory-clusters/cluster/<uuid:cluster_id>/add-memory/', add_memory_to_cluster, name='memory-clusters-add-memory'),
    path('api/memory-clusters/cluster/<uuid:cluster_id>/memory/<uuid:memory_id>/', remove_memory_from_cluster, name='memory-clusters-remove-memory'),
    path('api/memory-clusters/evolution/<uuid:agent_id>/', cluster_evolution, name='memory-clusters-evolution'),
    path('api/memory-clusters/find-similar/', find_similar_clusters, name='memory-clusters-find-similar'),

    # Session 258: Agent Predictions / Prophecies API
    path('api/predictions/', predictions_overview, name='predictions-overview'),
    path('api/predictions/agent/<uuid:agent_id>/', agent_predictions, name='predictions-agent'),
    path('api/predictions/<uuid:prediction_id>/', prediction_detail, name='predictions-detail'),
    path('api/predictions/<uuid:prediction_id>/verify/', verify_prediction, name='predictions-verify'),
    path('api/predictions/<uuid:prediction_id>/upvote/', upvote_prediction, name='predictions-upvote'),
    path('api/predictions/<uuid:prediction_id>/comment/', add_comment, name='predictions-comment'),
    path('api/predictions/leaderboard/', prediction_leaderboard, name='predictions-leaderboard'),
    path('api/predictions/generate-from-dreams/', generate_predictions_from_dreams, name='predictions-from-dreams'),
    path('api/predictions/expire-old/', expire_old_predictions, name='predictions-expire'),

    # Session 259: Time Capsule Messages API
    path('api/time-capsules/', TimeCapsuleOverviewView.as_view(), name='time-capsules-overview'),
    path('api/time-capsules/agent/<uuid:agent_id>/', AgentTimeCapsuleView.as_view(), name='time-capsules-agent'),
    path('api/time-capsules/<uuid:capsule_id>/', TimeCapsuleDetailView.as_view(), name='time-capsules-detail'),
    path('api/time-capsules/<uuid:capsule_id>/reveal/', RevealTimeCapsuleView.as_view(), name='time-capsules-reveal'),
    path('api/time-capsules/<uuid:capsule_id>/react/', TimeCapsuleReactView.as_view(), name='time-capsules-react'),
    path('api/time-capsules/ready-to-reveal/', ReadyToRevealView.as_view(), name='time-capsules-ready'),
    path('api/time-capsules/generate/', GenerateTimeCapsuleView.as_view(), name='time-capsules-generate'),
    path('api/time-capsules/expire-old/', ExpireOldCapsulesView.as_view(), name='time-capsules-expire'),

    # Session 219 Phase D: Workflow Marketplace API
    path('api/marketplace/workflows/', marketplace_browse, name='marketplace-browse'),
    path('api/marketplace/workflows/featured/', marketplace_featured, name='marketplace-featured'),
    path('api/marketplace/workflows/trending/', marketplace_trending, name='marketplace-trending'),
    path('api/marketplace/workflows/<str:workflow_id>/', marketplace_details, name='marketplace-details'),
    path('api/marketplace/workflows/<str:workflow_id>/install/', marketplace_install, name='marketplace-install'),
    path('api/marketplace/workflows/<str:workflow_id>/reviews/', marketplace_get_reviews, name='marketplace-get-reviews'),
    path('api/marketplace/publish/', marketplace_publish, name='marketplace-publish'),
    path('api/marketplace/reviews/', marketplace_add_review, name='marketplace-add-review'),
    path('api/marketplace/my-published/', marketplace_my_published, name='marketplace-my-published'),
    path('api/marketplace/my-installed/', marketplace_my_installed, name='marketplace-my-installed'),
    path('api/marketplace/stats/', marketplace_stats, name='marketplace-stats'),
    path('api/marketplace/categories/', marketplace_categories, name='marketplace-categories'),

    # Session 220: Real-Time Project Collaboration API
    # Note: More specific paths (invitations/) MUST come before catch-all (<str:project_id>/)
    path('api/projects/shared/', proj_collab_projects, name='proj-collab-projects'),
    path('api/projects/shared/invitations/', proj_collab_invitations, name='proj-collab-invitations'),
    path('api/projects/shared/invitations/<str:invitation_id>/accept/', proj_collab_accept, name='proj-collab-accept'),
    path('api/projects/shared/invitations/<str:invitation_id>/decline/', proj_collab_decline, name='proj-collab-decline'),
    path('api/projects/shared/<str:project_id>/', proj_collab_detail, name='proj-collab-detail'),
    path('api/projects/shared/<str:project_id>/invite/', proj_collab_invite, name='proj-collab-invite'),
    path('api/projects/shared/<str:project_id>/collaborators/', proj_collab_collaborators, name='proj-collab-collaborators'),
    path('api/projects/shared/<str:project_id>/collaborators/<str:user_id>/', proj_collab_remove, name='proj-collab-remove'),
    path('api/projects/shared/<str:project_id>/activity/', proj_collab_activity, name='proj-collab-activity'),
    path('api/projects/shared/<str:project_id>/comments/', proj_collab_comments, name='proj-collab-comments'),
    path('api/projects/shared/<str:project_id>/presences/', proj_collab_presences, name='proj-collab-presences'),

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

    # Session 439: Stripe Subscription Webhook
    path('api/stripe/webhook/', stripe_webhook, name='stripe-webhook'),
    path('api/stripe/subscription-status/', subscription_status, name='stripe-subscription-status'),

    # Session 440: Voice Marketplace API
    path('api/voice-marketplace/', marketplace_browse, name='voice-marketplace-browse'),
    path('api/voice-marketplace/my-voices/', my_voices, name='voice-marketplace-my-voices'),
    path('api/voice-marketplace/earnings/', earnings_summary, name='voice-marketplace-earnings'),
    path('api/voice-marketplace/transactions/', transaction_history, name='voice-marketplace-transactions'),
    path('api/voice-marketplace/create/', create_voice_from_elevenlabs, name='voice-marketplace-create'),
    path('api/voice-marketplace/clone/start/', start_clone_request, name='voice-clone-start'),
    path('api/voice-marketplace/clone/<uuid:request_id>/status/', clone_request_status, name='voice-clone-status'),
    path('api/voice-marketplace/<uuid:voice_id>/', voice_detail, name='voice-marketplace-detail'),
    path('api/voice-marketplace/<uuid:voice_id>/publish/', publish_voice, name='voice-marketplace-publish'),
    path('api/voice-marketplace/<uuid:voice_id>/unpublish/', unpublish_voice, name='voice-marketplace-unpublish'),
    path('api/voice-marketplace/<uuid:voice_id>/update/', update_voice, name='voice-marketplace-update'),
    path('api/voice-marketplace/<uuid:voice_id>/generate/', generate_speech, name='voice-marketplace-generate'),
    path('api/voice-marketplace/<uuid:voice_id>/preview/', preview_voice, name='voice-marketplace-preview'),
    path('api/voice-marketplace/<uuid:voice_id>/reviews/', add_review, name='voice-marketplace-add-review'),
]

# =============================================================================
# Session 450: Stripe Voice Checkout API
# =============================================================================
from core.views_stripe_voice import (
    create_checkout, price_estimate, stripe_webhook,
    checkout_status, checkout_success, checkout_cancel,
    simulate_purchase
)

urlpatterns += [
    # Checkout
    path('api/voice-checkout/create/', create_checkout, name='voice-checkout-create'),
    path('api/voice-checkout/price/', price_estimate, name='voice-checkout-price'),
    path('api/voice-checkout/webhook/', stripe_webhook, name='voice-checkout-webhook'),
    path('api/voice-checkout/status/<str:session_id>/', checkout_status, name='voice-checkout-status'),
    path('api/voice-checkout/simulate/', simulate_purchase, name='voice-checkout-simulate'),

    # Success/Cancel pages
    path('voice-checkout/success/', checkout_success, name='voice-checkout-success'),
    path('voice-checkout/cancel/', checkout_cancel, name='voice-checkout-cancel'),
]

# =============================================================================
# Session 451: User Upload API
# =============================================================================
from core.views_upload import (
    upload_image, upload_video,
    chunked_upload_init, chunked_upload_chunk, chunked_upload_status,
    get_uploads
)

urlpatterns += [
    # Simple uploads (< 50MB)
    path('api/upload/image/', upload_image, name='upload-image'),
    path('api/upload/video/', upload_video, name='upload-video'),

    # Chunked uploads (large files)
    path('api/upload/chunked/init/', chunked_upload_init, name='chunked-upload-init'),
    path('api/upload/chunked/<uuid:upload_id>/chunk/', chunked_upload_chunk, name='chunked-upload-chunk'),
    path('api/upload/chunked/<uuid:upload_id>/status/', chunked_upload_status, name='chunked-upload-status'),

    # List uploads
    path('api/upload/list/', get_uploads, name='upload-list'),
]

# Add WebSocket test endpoint if available
try:
    from core.health import websocket_test
    urlpatterns.append(path('api/v1/websocket-test/', websocket_test, name='websocket-test'))
except ImportError:
    pass

# =============================================================================
# Session 406: Legal Case Management API
# =============================================================================
from core.views_legal_cases import (
    case_profiles_list, case_profile_detail,
    add_child, delete_child,
    add_document, delete_document,
    get_case_context, active_case
)

urlpatterns += [
    # Case Profiles
    path('api/legal/cases/', case_profiles_list, name='legal-cases-list'),
    path('api/legal/cases/<uuid:case_id>/', case_profile_detail, name='legal-case-detail'),
    path('api/legal/cases/<uuid:case_id>/context/', get_case_context, name='legal-case-context'),

    # Children
    path('api/legal/cases/<uuid:case_id>/children/', add_child, name='legal-case-add-child'),
    path('api/legal/cases/<uuid:case_id>/children/<uuid:child_id>/', delete_child, name='legal-case-delete-child'),

    # Documents
    path('api/legal/cases/<uuid:case_id>/documents/', add_document, name='legal-case-add-document'),
    path('api/legal/cases/<uuid:case_id>/documents/<uuid:document_id>/', delete_document, name='legal-case-delete-document'),

    # Active Case
    path('api/legal/active-case/', active_case, name='legal-active-case'),

    # Session 408: Litigation Document Management
    path('api/legal/litigation/<uuid:case_profile_id>/documents/', list_litigation_documents, name='litigation-documents-list'),
    path('api/legal/litigation/<uuid:case_profile_id>/documents/upload/', upload_litigation_document, name='litigation-documents-upload'),
    path('api/legal/litigation/<uuid:case_profile_id>/knowledge-graph/', get_case_knowledge_graph, name='litigation-knowledge-graph'),
    path('api/legal/litigation/<uuid:case_profile_id>/knowledge-graph/rebuild/', rebuild_knowledge_graph, name='litigation-knowledge-graph-rebuild'),
    path('api/legal/litigation/<uuid:case_profile_id>/responses/', list_generated_responses, name='litigation-responses-list'),
    path('api/legal/litigation/<uuid:document_id>/generate-response/', generate_response_to_filing, name='litigation-generate-response'),
    path('api/legal/litigation/response/<uuid:response_id>/', get_generated_response, name='litigation-response-detail'),
    path('api/legal/litigation/response/<uuid:response_id>/package/', create_filing_package, name='litigation-filing-package'),
    path('api/legal/litigation/document-types/', get_document_types, name='litigation-document-types'),

    # Session 410: Document Threading APIs
    path('api/legal/litigation/<uuid:case_profile_id>/threads/', get_document_threads, name='litigation-document-threads'),
    path('api/legal/litigation/document/<uuid:document_id>/thread/', get_document_thread, name='litigation-document-thread'),
    path('api/legal/litigation/<uuid:case_profile_id>/needs-response/', get_documents_needing_response, name='litigation-needs-response'),
]

# =============================================================================
# Session 455: Cross-Platform Session Handoff API
# =============================================================================
from core.views_session_handoff import (
    get_active_sessions,
    get_session_details,
    resume_session,
    end_session,
    get_cross_platform_status,
)

urlpatterns += [
    # Session management
    path('api/sessions/active/', get_active_sessions, name='sessions-active'),
    path('api/sessions/<str:conversation_id>/', get_session_details, name='sessions-detail'),
    path('api/sessions/resume/', resume_session, name='sessions-resume'),
    path('api/sessions/end/', end_session, name='sessions-end'),
    path('api/sessions/status/', get_cross_platform_status, name='sessions-cross-platform-status'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns.append(path('health/', include('backend.auto_endpoints.urls')))  # public health
