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

# Session 688: React frontend redirect views
from core.views_redirect import (
    ai_studio_redirect, ai_nexus_redirect, content_studio_redirect,
    ai_production_hub_redirect, command_redirect, diagnostics_redirect,
    income_builder_redirect, neural_orchestra_redirect, login_redirect,
    # Session 871: Removed unused imports: visualization_redirect, assistant_redirect
)
from core.views_react import react_app

# Session 758: Integration Health & Observability
from core.views_integration_health import (
    integration_health,
    context_injection_metrics,
    IntegrationAlertView,
    execution_quality_analysis,
)

# Session 843: Trace Viewer - Orchestration Contract
# Session 846: Citation Gate - Citation Violations
from core.views_trace_viewer import (
    TraceViewerView,
    WiringDefectsListView,
    WiringDefectResolveView,
    CitationViolationsListView,
    CitationViolationResolveView,
)

# Session 865: ConceptForge Dossier Pipeline API
from core.views_conceptforge import (
    list_runs as conceptforge_list_runs,
    get_run_detail as conceptforge_run_detail,
    get_stage_content as conceptforge_stage_content,
    get_artifact_content as conceptforge_artifact_content,
    retry_run as conceptforge_retry_run,
    get_stats as conceptforge_stats,
    get_domain_labs as conceptforge_domain_labs,
)

# Session 962 Phase 2: Strategic Memory API
from core.views_strategic_memory import (
    memory_precedents,
    memory_failures,
    memory_strategy,
)

# Session 962 + 963: Deliberation Persistence API
from core.views_deliberation import (
    deliberation_sessions_list,
    deliberation_session_detail,
    deliberation_turns,
    deliberation_contracts,
    doc_versions_list,
    doc_version_detail,
    deliberation_evidence,
    deliberation_trace,
    deliberation_replay,
    blog_deliberation_detail,
    deliberation_verification_report,
    deliberation_failure_stats,
)

# Session 866: ATS Optimization API
from core.views_ats_optimization import (
    ATSAnalyzeView,
    ATSExtractKeywordsView,
    ATSOptimizeSuggestionsView,
    ATSTemplatesView,
    ATSGenerateSummaryView,
    ATSConversionStatsView,
)

# Session 930: User Learning System API
from core.views_user_learning_api import (
    record_agent_feedback,
    get_agent_effectiveness,
    get_user_agent_summary,
    get_profile_completeness,
    get_next_profile_question,
    record_profile_response,
    get_goals_dashboard,
    get_goal_detail,
    record_goal_progress,
    get_skills_summary,
    get_skill_growth_chart,
    record_skill_demonstration,
    get_skill_recommendations,
    get_user_learning_summary,
)

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

# Import podcast API views (Session 502, 865)
from core.views_podcast import (
    podcast_list as podcast_list_view,
    podcast_create as podcast_create_view,
    podcast_status as podcast_status_view,
    podcast_script as podcast_script_view,
    podcast_delete as podcast_delete_view,
    podcast_generate_audio as podcast_generate_audio_view,
    podcast_stats as podcast_stats_view,
)

# Import campaign API views (Session 513)
from core.views_campaign import (
    campaign_list,
    campaign_create,
    campaign_detail,
    campaign_start,
    campaign_status,
    campaign_deliverables,
    campaign_delete,
    campaign_budget_tiers,
)

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

# Session 773: Learning Journey API views (replaces stubs)
from core.views_learning_journey_api import (
    learning_journeys_list, learning_journeys_active, learning_journey_detail,
    learning_journey_start, learning_journey_pause, learning_journey_resume,
    learning_journey_complete, learning_journey_abandon,
    learning_step_start, learning_step_complete, learning_step_skip,
    learning_step_content,
    learning_templates, learning_template_detail,
    learning_journey_analytics, learning_achievements,
)

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
    # Session 520: PartnershipProject CRUD endpoints
    update_project as update_partnership_project,
    delete_project as delete_partnership_project,
    create_project as create_partnership_project,
    # Session 521: Content Export & Edit
    export_written_content,
    update_written_content,
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

# Session 1009: Removed views_agent_collaboration_api import (orphan cleanup)

# Import spider dashboard views
from core.views_spider_dashboard import (
    spider_network_data,
    spider_activity_feed,
    spider_data_stats,
    execute_spider,
    # Session 484: Spider Health Dashboard
    spider_execution_logs,
    spider_error_detail,
    retry_spider_execution,
    spider_embedding_coverage,
    run_spider_manual,
    spider_health_summary,
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
    # Session 536: Cross-references for ICC
    intelligence_cross_references,
    spider_detail,
    agent_detail,  # Session 537: Agent detail for ICC
    situation_detail,  # Session 537: Situation detail for ICC
    # Session 558: Prediction Markets & Sports Odds
    get_prediction_markets,
    get_sports_odds,
)

# Session 783: Spider News Feed
from core.views_spider_feed import (
    spider_feed,
    spider_feed_trending,
    spider_feed_item_detail,
    spider_feed_annotate,
    spider_feed_vote,
    spider_feed_stats,
    sports_hub_feed,
)

# Session 784: Documentation index API
from core.views_docs_index import (
    docs_index,
    docs_detail,
    docs_graph_summary,
    docs_stats,
)

# Session 1009: Removed views_agent_intelligence import (orphan cleanup)

# Session 1009: Removed views_agent_collaboration import (orphan cleanup)

# Session 219 Phase C: Import agent learning views
# Session 1009: Removed orphaned learning aliases (learning_record, etc.)
from core.views_agent_learning import (
    # Session 244: Agent Conversations
    get_agent_conversations,
    get_agent_conversation_detail,  # Session 835: Single conversation detail
    trigger_agent_conversation,
    get_conversation_task_status,  # Session 827: Async task status
    # Session 247: Agent Dreams
    # Session 843: Added get_agent_dream_detail
    get_agent_dreams,
    get_agent_dream_detail,
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
    # Session 942: Bulk decision actions
    bulk_promote_decisions,
    bulk_reject_decisions,
    # Session 659: Governance Stats
    get_governance_stats,
    # Session 660: Celery & Health APIs
    get_celery_stats,
    get_system_health,
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
    # Session 590: Pilot Readiness Gate
    get_pilot_readiness_gates,
    get_pilot_gate_detail,
    update_gate_status,
    update_checklist_item,
    create_pilot_gate,
    # Session 592: Pilot Execution
    start_pilot_execution,
    complete_pilot_execution,
    # Session 593: Gate Dashboard
    get_pilot_gate_dashboard,
    # Session 594: Regenerate content & Approve all
    regenerate_checklist_content,
    approve_all_checklist_items,
    # Session 595: Pilot Dashboard
    get_pilot_executions_dashboard,
    # Session 690: Implementation Pipeline
    get_pilot_implementation,
    trigger_pilot_implementation,
    # Session 596: Experiment Tracking
    get_experiments,
    update_experiment_kpi,
    complete_experiment,
    raise_experiment_target,  # Session 657
    get_experiment_portfolio,
    # Session 598: Learning Loop UI
    get_experiment_learnings,
    get_success_patterns,
    # Session 599: Experiment Halt
    halt_experiment,
    # Session 600: Experiment Metrics & Rollback
    get_experiment_metrics,
    get_rollback_plan,
    update_remediation_step,
    # Session 606: Experiment Suggestions
    get_experiment_suggestions,
    # Session 607: Pilot Progress Dashboard
    get_pilot_progress_dashboard,
    get_pilot_progress_detail,
    # Session 609: Auto KPI Tracking
    trigger_kpi_update,
    get_experiment_kpi_trend,
    get_all_experiment_kpi_trends,
    # Session 611: KPI Alerts
    get_kpi_alerts,
    get_weekly_kpi_summary,
    # Session 614: Recent Activity
    get_recent_activity as get_system_recent_activity,
    # Session 615: Experiment Recommendations
    get_experiment_recommendations,
    # Session 602: Boardroom Learning Integration
    get_decision_learning_context,
    get_boardroom_learning_summary,
    # Session 603: Learning Velocity Dashboard
    get_learning_velocity_dashboard,
    get_theme_velocity,
    # Session 604: Decision Prioritization
    get_prioritized_decisions,
    get_decision_priority,
    # Session 717: Conversation Contract Analytics
    get_conversation_contract_overview,
    get_conversation_contract_detail,
)

# Session 628 + 631 + 632 + 741: Content Calendar & Channels
from core.views_content_calendar import (
    content_calendar_main,
    content_calendar_upcoming,
    content_calendar_history,
    content_calendar_reschedule,
    content_calendar_episode_detail,  # Session 631
    content_calendar_generate,  # Session 632
    content_channels_list,  # Session 741
    content_channel_detail,  # Session 741
    content_episode_detail,  # Session 741
)

# Session 886: Content Learning Feedback Loop API
from core.views_content_learning import (
    BlogPerformanceContextView,
    BlogPerformanceMetricsView,
    LearningRulesView,
    ContentQualityTrendsView,
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
    list_all_memories,  # Session 860
)

# Session 1009: Removed views_agent_mood import (orphan cleanup)

# Session 253: Agent Relationships (Session 871: Alliance/Rivalry removed)
from core.views_agent_relationships import (
    get_relationships_overview,
    get_agent_relationships,
    create_relationship,
    record_interaction,
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
    opportunity_dismiss,  # Session 688
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
    gumroad_publish_image,  # Session 487: Golden Egg - actual file upload
    gumroad_webhook,  # Session 487: Sale notifications
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
    # Session 954: Learning Loop Effectiveness
    learning_loop_stats,
    track_learning_outcome,
    run_learning_cycle,
    get_agent_learnings,
)

# Session 954: Import RAG Observability views
from core.views_rag_observability import (
    rag_observability_dashboard,
    rag_document_inventory,
    rag_context_budget,
    rag_risk_boost_stats,
    rag_critical_docs,
    rag_risk_distribution,
    rag_retrieval_channels,
    rag_run_classification,
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

# Session 484: Import Autonomous Dashboard views
from core.views_autonomous_dashboard import (
    list_situations,
    situation_detail,
    toggle_situation,
    run_situation_now,
    list_triggers,
    list_trigger_events,
    analytics_summary as autonomous_analytics_summary,
    # Session 484: Trigger Tuning
    trigger_detail,
    update_trigger,
    toggle_trigger,
    reset_trigger_cooldown,
    trigger_analytics,
    viral_predictions_api,
    skill_gap_api,
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
    get_all_messages,  # Session 782: All messages for Messages tab
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
from core.views_collective_intelligence import get_shared_knowledge
from core.views_collective_intelligence import (
    aggregate_insights,
    generate_report,
    get_knowledge_gaps,
    get_knowledge_topics,  # Session 782
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
    dashboard_stats, live_agent_activity, advisor_insights,
    dashboard_summary,  # Session 459: Personalized greeting + "While You Were Away"
)
from core.views_public_stats import public_system_stats

# Session 884: Home Page Boot API
# Session 1000: Intelligence Desks API
from core.views_home import home_boot, intelligence_desks, trigger_desks, purge_queue
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
    resend_verification_view, auth_debug_view
)
from core.profile_views import (
    upload_avatar_view, delete_avatar_view, update_profile_view, generate_avatar_view
)
from core.views_user_profile import (
    ai_configuration, agents_assigned, execute_command
)
from core.views_real_income_builder import (
    real_income_opportunities, analyze_real_opportunities
)
# Session 871: Removed unused import: income_builder_view
from core.views_neural_orchestra import (
    # Session 871: Removed unused import: neural_orchestra_view
    ecosystem_live_feed as neural_ecosystem_feed,
    agents_stats as neural_agents_stats,
    learning_status as neural_learning_status,
    learning_feed as neural_learning_feed,
    neural_orchestra_health,
    neural_orchestra_websocket_bridge,
    neural_orchestra_debug_info,
    trigger_neural_orchestra_reality_check,
)
# Session 439: Stripe Webhook
from core.views_stripe import stripe_webhook, subscription_status

# Session 440: Voice Marketplace
from core.views_voice_marketplace import (
    marketplace_browse, voice_detail, my_voices, publish_voice, unpublish_voice,
    update_voice, generate_speech, preview_voice, add_review, earnings_summary,
    transaction_history, create_voice_from_elevenlabs, start_clone_request,
    clone_request_status, clone_voice_upload, marketplace_categories, marketplace_stats, marketplace_purchases,
)

from core import views_portfolio
from core.views_profile import (
    ExtendedProfileView, ProfileSkillsView, ProfileForApplicationView
)
# Import Personal Assistant views
from core.views_personal_assistant import (
    chat_with_assistant, get_assistant_context, get_learning_summary,
    provide_feedback, reset_assistant, voice_to_assistant,
    voice_interview_response, transcribe_only,  # Session 456: Voice interview
    get_attention_items,  # Session 574: Attention items for PA UI
    get_unified_attention, get_attention_stats,  # Session 932: Unified attention aggregator
    unified_pa_chat, unified_pa_context,  # Session 932: Unified PA REST endpoints
    pa_chat_status,  # Session 974b: Async PA chat polling
    pa_message_feedback,  # Session 1085: Thumbs up/down on PA responses
    list_pa_conversations, get_pa_conversation, create_pa_conversation,  # Session 974: Conversation history
    trigger_boardroom_maintenance,  # Session 977: On-demand boardroom cleanup
    pa_conversation_post_message, pa_conversation_messages,  # 3-way chat: store-only + message polling
    pa_activity_feed,  # Rigby accountability: actual tool call activity
    session_health,  # Context-aware session management
)
from core.views_assistant_bypass import assistant_chat_bypass, get_task_progress
if settings.DEBUG:
    from core.views_personal_assistant_dev import chat_with_assistant_dev, get_assistant_context_dev
    from core.views_assistant_minimal import chat_minimal_dev, context_minimal_dev
    from core.simple_ping import ping_dev
# Session 1103c: legacy Unified Assistant views removed — fully replaced
# by Rigby at /api/pa/chat/. The 6 /api/unified/* endpoints and their
# dev /api/unified/dev/chat/ variant had zero frontend callers and
# were documented as dead in docs/audit-2026/HALF_BUILT_FEATURES_AUDIT.md.
# Import Enhanced Profile views
from core.views_enhanced_profile import (
    get_enhanced_profile, update_enhanced_profile,
    get_user_memories, get_profile_suggestions
)
# Session 430: Import Interview views
# Session 1009: Removed orphaned certification imports
from core.views_interview import (
    start_interview, respond_interview, interview_status,
    resume_interview, get_user_profile_summary,
)
# Import Unified Bridge views for REAL money-making functionality
from core.views_unified_bridge import (
    sync_user_profile, get_real_opportunities, submit_real_application,
    record_user_revenue, get_opportunity_decision, get_user_dashboard_data,
    trigger_component_sync
)
from core.views_unified import WebSocketDiagnosticsView
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
# Session 869: Stripe billing - real implementations replacing stubs
from core.views_stripe_billing import (
    stripe_plans, stripe_payment_methods, stripe_add_payment_method,
    stripe_remove_payment_method, stripe_set_default_payment_method,
    stripe_invoices, stripe_invoice_detail, stripe_upcoming_invoice,
    stripe_usage, stripe_subscribe, stripe_cancel_subscription,
    stripe_resume_subscription, stripe_billing_portal,
)
# NOTE: All stubs from views_frontend_stubs.py have been replaced:
# - Stripe billing: Now using views_stripe_billing.py (Session 869)
# - Learning journey: Now using views_learning_journey_api.py (Session 782)
# - Autonomous: Now using views_autonomous_dashboard.py (Session 782)
# - Reasoning: Now using views_autonomous_reasoning.py (Session 782)
# - Analytics: Now using views_analytics_real.py (Session 780)

# Session 780: Real analytics implementation replacing stubs
from core.views_analytics_real import (
    analytics_overview, analytics_summary, analytics_reports_list,
    analytics_reports_generate,
)

# Session 782: Reasoning engine - real views already exist in views_autonomous_reasoning.py
# (imported at line 1322 and routed at lines 2750-2768)

from core.views_analytics import (
    analytics_dashboard, track_usage, track_feature_usage, cost_breakdown,
    update_budget, model_performance_analytics,
    # Session 36: Analytics Dashboard - Session 871: Removed unused: AnalyticsDashboardView, analytics_api_data
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
    realtime_stats_v2, track_event_v2,
    # Session 775: Missing chart endpoints
    get_chart_agent_activity, get_chart_content_production, get_chart_revenue,
    get_chart_user_engagement, get_chart_spider_performance,
    get_chart_learning_progress, get_chart_collaboration,
    # Session 775: Missing v2 endpoints for Insights tab
    top_performers_v2, anomalies_v2, forecast_v2,
    trends_v2, comparison_v2, breakdown_v2, export_v2,
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
    # Session 871: Removed unused import: ai_image_studio
)
from core.views_video_agents import (
    video_resolve, video_transcribe, video_transcripts_list, video_transcript_detail,
    video_content_pack,
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
    add_voiceover_view,
    # Session 1013: SFX-to-Video Pipeline
    add_sfx_to_video_view,
    # Session 479: DaVinci Resolve Gallery
    get_resolve_renders,
    download_resolve_render,
    rate_resolve_render
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
from core.views_agent_extras import agent_channels, agent_tools, agent_templates
from core.views_agent_orchestration import (
    list_agents, get_agents_by_specialization, orchestrate_multi_agent_task,
    suggest_agent, route_task, get_agent_status, health_check_agents, get_agent_details,
    refresh_agent_discovery, comprehensive_agents_list
)
from core.views_odds_sports import (
    convert_odds, calculate_expected_value, calculate_kelly_criterion, detect_arbitrage,
    sports_game_analysis, live_betting_opportunities, list_betting_markets,
    get_bankroll_management, get_bankroll_stats, live_odds, live_odds_with_scores,
    get_player_props, get_weather_data, get_injury_data,
    get_betting_intelligence, orchestrate_agent_analysis, get_orchestration_status, get_game_details,
    get_bookmaker_analysis, get_game_spider_insights, scan_arbitrage_opportunities, get_futures_odds,
    log_wager, get_line_movement, get_games_with_movement,
    get_todays_games, get_betting_brief, get_sharp_action, get_ai_track_record,
    get_pipeline_status,
)
# Session 562: Push Notification APIs
from core.views_push_notifications import (
    get_vapid_public_key, subscribe_push, unsubscribe_push,
    notification_preferences, get_subscription_status, send_test_push
)

# Session 563: Bet Tracking APIs
from core.views_betting import (
    place_bet, get_wagers, get_wager_detail, settle_wager,
    cancel_wager, get_betting_stats, get_recent_activity, quick_pick
)

# Import Phase 2 advanced features
from core.views_rag_embeddings import (
    upload_document_for_rag, semantic_search, rag_generate, embeddings_stats,
    create_knowledge_collection, list_knowledge_collections, advanced_rag_query, optimize_embeddings,
    # Session 402: Document ingestion APIs
    list_documents, ingest_url, ingest_file, get_document, delete_document,
    # Video RAG ingest
    ingest_video, ingest_video_status,
    # YouTube Whisper fallback
    ingest_youtube_whisper,
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
# Session 699: LLM Routing API endpoints (real database-backed)
from core.views_llm_routing import (
    llm_routing_status, llm_providers_list, llm_models_list,
    agent_llm_configs_list, llm_call_logs_list, llm_cost_analytics,
    update_agent_llm_config
)
from core.views_advanced_workflows import (
    create_advanced_workflow, execute_advanced_workflow, get_workflow_execution_status,
    list_workflow_templates, create_workflow_from_template, get_workflow_output
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

# Session 544: Autonomous Reasoning Engine API
from core import views_autonomous_reasoning

# Session 550: Research Demo API
from core import views_research_demo
from core import views_competitor_comparison  # Session G1
from core import views_workflow_run  # WorkflowRun API
from core import views_initiative_kickstart  # Session 884

# Import enhanced learning workflow API
try:
    from enhanced_learning_workflow_api import learning_workflow_api
except ImportError:
    learning_workflow_api = None

# Create API router
router = DefaultRouter()

# Session 972: Audit trail ViewSets
from core.views_audit_api import DecisionRecordViewSet, ToolCallRecordViewSet, ToolCallAggregateViewSet, SignalClusterViewSet
router.register(r'decision-records', DecisionRecordViewSet, basename='decision-record')
router.register(r'tool-call-records', ToolCallRecordViewSet, basename='tool-call-record')
router.register(r'tool-call-aggregates', ToolCallAggregateViewSet, basename='tool-call-aggregate')  # Session 1007
router.register(r'signal-clusters', SignalClusterViewSet, basename='signal-cluster')

from core.views_obs import (
    cockpit_obs_health,
    cockpit_obs_status,
    cockpit_obs_start,
    cockpit_obs_stop,
    cockpit_obs_last,
    cockpit_obs_upload,
)

from core.views_diagnostics import (
    diagnostic_master_endpoint,
    test_spider_network,
    test_income_builder,
    websocket_test_page,
    config_snapshot,        # Session 1069: Cross-service config comparison
    debug_raise_500,        # Session 1069: Middleware verification endpoint
    cockpit_error_summary,  # Focus Cockpit: error signatures
    cockpit_runs_list,      # Focus Cockpit: agent execution runs
    cockpit_runs_metrics,   # Session 1077: noise metrics — North Star coverage
    cockpit_conversations_metrics,  # Session 1077: conversation metrics — topic clusters, zombie rate
    cockpit_focus_mode_status,  # Session 1077: Focus Mode status for cockpit
    cockpit_focus_mode_update,  # Session 1077: Focus Mode config update
    cockpit_inbox,          # Focus Cockpit: read-only inbox aggregation
    cockpit_create_blog,    # Focus Cockpit: create blog post
    cockpit_create_talking_video,  # Focus Cockpit: create talking video
    cockpit_job_status,     # Focus Cockpit: poll job status
    cockpit_ops_overview,   # Focus Cockpit: ops health overview
    cockpit_resolve_node_health,  # Resolve node health proxy
    cockpit_resolve_node_render_start,  # Resolve node render start proxy
    cockpit_resolve_node_render_status,  # Resolve node render status proxy
    cockpit_resolve_node_render_result,  # Resolve node render result proxy
    cockpit_resolve_node_jobs,  # Resolve node jobs list proxy
    cockpit_library_deliverables,  # Focus Cockpit: library deliverables
    cockpit_library_media,  # Focus Cockpit: library media
    cockpit_approvals_list,  # Focus Cockpit: actionable approvals
    cockpit_approve_decision,  # Focus Cockpit: approve/reject decision
    cockpit_approve_gate,  # Focus Cockpit: approve/block gate
    cockpit_alerts,  # Focus Cockpit: in-app alerts
    cockpit_runbook,  # Focus Cockpit: deterministic runbooks
    cockpit_retry_run,  # Focus Cockpit: retry failed run
    cockpit_create_incident_note,  # Focus Cockpit: create incident note
    cockpit_audit_list,  # Focus Cockpit: audit log list
    cockpit_agent_fleet,  # Focus Cockpit: agent fleet list
    cockpit_agent_detail,  # Focus Cockpit: agent detail
    cockpit_agent_run_now,  # Focus Cockpit: run agent now
    cockpit_agent_pause,  # Focus Cockpit: pause agent
    cockpit_agent_resume,  # Focus Cockpit: resume agent
    cockpit_queues_overview,  # Focus Cockpit: queue/worker/task load
    cockpit_queue_depths,  # Focus Cockpit: live Redis LLEN per queue
    cockpit_cost_overview,  # Focus Cockpit: cost/token/provider usage
    cockpit_autopilot_policies,  # Focus Cockpit: autopilot policies
    cockpit_autopilot_toggle,  # Focus Cockpit: toggle autopilot policy
    cockpit_autopilot_evaluate,  # Focus Cockpit: evaluate autopilot policies
    cockpit_autopilot_history,  # Focus Cockpit: autopilot event history
    cockpit_run_trace,  # Focus Cockpit: run trace debugger
    cockpit_config_overview,  # Focus Cockpit: config overview
    cockpit_config_toggle_provider,  # Focus Cockpit: toggle provider
    cockpit_config_flags,  # Focus Cockpit: feature flags CRUD
    cockpit_config_delete_flag,  # Focus Cockpit: delete flag
    cockpit_config_changes,  # Focus Cockpit: config change log
    cockpit_incidents_list,  # Focus Cockpit: incidents list/create
    cockpit_incident_detail,  # Focus Cockpit: incident detail
    cockpit_incident_update,  # Focus Cockpit: update incident
    cockpit_incident_add_event,  # Focus Cockpit: add incident event
    cockpit_ops_runs_list,  # Focus Cockpit: ops runs list
    cockpit_ops_run_detail,  # Focus Cockpit: ops run detail + events
    cockpit_vip_context,  # VIP personalization context
    cockpit_learning_loop,  # Learning Loop Control Panel
    system_version,  # Session 1078: Build/deploy version info
    # Session 871: Removed unused import: diagnostic_dashboard
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

# Session 641: Agent Analytics API
# Session 1009: Removed orphaned agent_analytics_* imports
from core.views_agent_analytics import (
    system_health_check,
    test_agent_execution,
    celery_status,  # Session 642: Celery monitoring
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

    # Session 688: Legacy dashboard pages redirect to React frontend
    path('ai-nexus/', ai_nexus_redirect, name='ai-nexus'),
    path('content-studio/', content_studio_redirect, name='content-studio'),
    path('ai-studio/', ai_studio_redirect, name='ai-image-studio'),
    path('ai-production-hub/', ai_production_hub_redirect, name='ai-production-hub'),
    path('command/', command_redirect, name='command-center'),
    path('diagnostics/', diagnostics_redirect, name='diagnostics'),
    path('income-builder/', income_builder_redirect, name='income-builder'),
    path('neural-orchestra/', neural_orchestra_redirect, name='neural-orchestra'),

    # Session 145: Neural Orchestra API endpoints - REAL DATA!
    path('api/neural-orchestra/ecosystem/live-feed/', neural_ecosystem_feed, name='neural-ecosystem-feed'),
    path('api/neural-orchestra/agents/stats/', neural_agents_stats, name='neural-agents-stats'),
    path('api/neural-orchestra/learning/status/', neural_learning_status, name='neural-learning-status'),
    path('api/neural-orchestra/learning/feed/', neural_learning_feed, name='neural-learning-feed'),
    path('api/neural-orchestra/health/', neural_orchestra_health, name='neural-orchestra-health'),
    path('api/neural-orchestra/websocket-config/', neural_orchestra_websocket_bridge, name='neural-websocket-config'),
    path('api/neural-orchestra/debug/', neural_orchestra_debug_info, name='neural-orchestra-debug'),
    path('api/neural-orchestra/reality-check/', trigger_neural_orchestra_reality_check, name='neural-orchestra-reality-check'),

    # Session 688: Authentication redirects to React
    path('accounts/login/', login_redirect, name='login'),
    path('accounts/logout/', lambda request: (logout(request), redirect('/login'))[1], name='logout'),

    # Session 758: Integration Health & Observability Endpoints
    path('api/integration/health/', integration_health, name='integration-health'),
    path('api/integration/metrics/', context_injection_metrics, name='integration-metrics'),
    path('api/integration/alerts/', IntegrationAlertView.as_view(), name='integration-alerts'),
    path('api/integration/quality/', execution_quality_analysis, name='integration-quality'),

    # Session 843: Trace Viewer - Orchestration Contract
    path('api/traces/<uuid:trace_id>/', TraceViewerView.as_view(), name='trace-viewer'),
    path('api/wiring-defects/', WiringDefectsListView.as_view(), name='wiring-defects-list'),
    path('api/wiring-defects/<uuid:defect_id>/resolve/', WiringDefectResolveView.as_view(), name='wiring-defect-resolve'),

    # Session 846: Citation Gate - Citation Violations
    path('api/citation-violations/', CitationViolationsListView.as_view(), name='citation-violations-list'),
    path('api/citation-violations/<uuid:violation_id>/resolve/', CitationViolationResolveView.as_view(), name='citation-violation-resolve'),

    # Session 865: ConceptForge Dossier Pipeline API
    path('api/conceptforge/runs/', conceptforge_list_runs, name='conceptforge-list-runs'),
    path('api/conceptforge/runs/<uuid:run_id>/', conceptforge_run_detail, name='conceptforge-run-detail'),
    path('api/conceptforge/runs/<uuid:run_id>/stages/<str:stage_name>/', conceptforge_stage_content, name='conceptforge-stage-content'),
    path('api/conceptforge/runs/<uuid:run_id>/retry/', conceptforge_retry_run, name='conceptforge-retry-run'),
    path('api/conceptforge/artifacts/<uuid:artifact_id>/', conceptforge_artifact_content, name='conceptforge-artifact-content'),
    path('api/conceptforge/stats/', conceptforge_stats, name='conceptforge-stats'),
    path('api/conceptforge/labs/', conceptforge_domain_labs, name='conceptforge-domain-labs'),

    # Session 962 Phase 1: Deliberation Persistence API
    path('api/deliberation/sessions/', deliberation_sessions_list, name='deliberation-sessions-list'),
    path('api/deliberation/sessions/<uuid:session_id>/', deliberation_session_detail, name='deliberation-session-detail'),
    path('api/deliberation/sessions/<uuid:session_id>/turns/', deliberation_turns, name='deliberation-turns'),
    path('api/deliberation/sessions/<uuid:session_id>/contracts/', deliberation_contracts, name='deliberation-contracts'),
    # Session 963 Phase 3: Evidence, Trace, Replay
    path('api/deliberation/sessions/<uuid:session_id>/evidence/', deliberation_evidence, name='deliberation-evidence'),
    path('api/deliberation/sessions/<uuid:session_id>/trace/', deliberation_trace, name='deliberation-trace'),
    path('api/deliberation/sessions/<uuid:session_id>/replay/', deliberation_replay, name='deliberation-replay'),
    # Session 970 Phase 5.1: Verification report
    path('api/deliberation/sessions/<uuid:session_id>/verification-report/', deliberation_verification_report, name='deliberation-verification-report'),
    path('api/docs/versions/', doc_versions_list, name='doc-versions-list'),
    path('api/docs/versions/<int:version_id>/', doc_version_detail, name='doc-version-detail'),
    path('api/deliberation/failure-stats/', deliberation_failure_stats, name='deliberation-failure-stats'),
    # Phase 4: Blog deliberation detail
    path('api/blog/<uuid:blog_id>/deliberation/', blog_deliberation_detail, name='blog-deliberation-detail'),

    # Session 962 Phase 2: Strategic Memory API
    path('api/memory/precedents/', memory_precedents, name='memory-precedents'),
    path('api/memory/failures/', memory_failures, name='memory-failures'),
    path('api/memory/strategy/', memory_strategy, name='memory-strategy'),

    # Session 866: ATS Optimization API
    path('api/ats/analyze/', ATSAnalyzeView.as_view(), name='ats-analyze'),
    path('api/ats/extract-keywords/', ATSExtractKeywordsView.as_view(), name='ats-extract-keywords'),
    path('api/ats/optimize/', ATSOptimizeSuggestionsView.as_view(), name='ats-optimize'),
    path('api/ats/templates/', ATSTemplatesView.as_view(), name='ats-templates'),
    path('api/ats/generate-summary/', ATSGenerateSummaryView.as_view(), name='ats-generate-summary'),
    path('api/ats/stats/', ATSConversionStatsView.as_view(), name='ats-stats'),

    # Session 930: User Learning System API
    # Agent Feedback
    path('api/user-learning/feedback/', record_agent_feedback, name='user-learning-feedback'),
    path('api/user-learning/effectiveness/<uuid:agent_id>/', get_agent_effectiveness, name='user-learning-effectiveness'),
    path('api/user-learning/agent-summary/', get_user_agent_summary, name='user-learning-agent-summary'),
    # Profile Completeness
    path('api/user-learning/profile-completeness/', get_profile_completeness, name='user-learning-profile-completeness'),
    path('api/user-learning/profile-next-question/', get_next_profile_question, name='user-learning-profile-question'),
    path('api/user-learning/profile-response/', record_profile_response, name='user-learning-profile-response'),
    # Goal Tracking
    path('api/user-learning/goals/', get_goals_dashboard, name='user-learning-goals'),
    path('api/user-learning/goals/<uuid:goal_id>/', get_goal_detail, name='user-learning-goal-detail'),
    path('api/user-learning/goals/<uuid:goal_id>/progress/', record_goal_progress, name='user-learning-goal-progress'),
    # Skill Evolution
    path('api/user-learning/skills/', get_skills_summary, name='user-learning-skills'),
    path('api/user-learning/skills/growth/', get_skill_growth_chart, name='user-learning-skills-growth'),
    path('api/user-learning/skills/demonstrate/', record_skill_demonstration, name='user-learning-skill-demonstrate'),
    path('api/user-learning/skills/recommendations/', get_skill_recommendations, name='user-learning-skill-recommendations'),
    # Combined Summary
    path('api/user-learning/summary/', get_user_learning_summary, name='user-learning-summary'),

    # Diagnostic Endpoints - Complete Backend Visibility (API only, redirect above handles page)
    path('api/diagnostics/', diagnostic_master_endpoint, name='diagnostics-master'),
    path('api/diagnostics/test-spiders/', test_spider_network, name='diagnostics-test-spiders'),
    path('api/diagnostics/test-income-builder/', test_income_builder, name='diagnostics-test-income'),
    path('diagnostics/websocket-test/', websocket_test_page, name='diagnostics-websocket-test'),
    # Session 1069: Cross-service config snapshot + middleware test
    path('api/internal/config-snapshot/', config_snapshot, name='config-snapshot'),
    path('api/internal/debug-raise-500/', debug_raise_500, name='debug-raise-500'),
    # Focus Cockpit API
    path('api/cockpit/errors/', cockpit_error_summary, name='cockpit-error-summary'),
    path('api/cockpit/runs/', cockpit_runs_list, name='cockpit-runs-list'),
    path('api/cockpit/runs/metrics/', cockpit_runs_metrics, name='cockpit-runs-metrics'),
    path('api/cockpit/conversations/metrics/', cockpit_conversations_metrics, name='cockpit-conversations-metrics'),
    path('api/cockpit/focus-mode/status/', cockpit_focus_mode_status, name='cockpit-focus-mode-status'),
    path('api/cockpit/focus-mode/update/', cockpit_focus_mode_update, name='cockpit-focus-mode-update'),
    path('api/cockpit/inbox/', cockpit_inbox, name='cockpit-inbox'),
    path('api/cockpit/create/blog/', cockpit_create_blog, name='cockpit-create-blog'),
    path('api/cockpit/create/talking-video/', cockpit_create_talking_video, name='cockpit-create-talking-video'),
    path('api/cockpit/create/status/<str:job_id>/', cockpit_job_status, name='cockpit-job-status'),
    path('api/cockpit/ops/overview/', cockpit_ops_overview, name='cockpit-ops-overview'),
    path('api/cockpit/resolve-node/health/', cockpit_resolve_node_health, name='cockpit-resolve-node-health'),
    path('api/cockpit/resolve-node/render/start/', cockpit_resolve_node_render_start, name='cockpit-resolve-node-render-start'),
    path('api/cockpit/resolve-node/render/status/<str:job_id>/', cockpit_resolve_node_render_status, name='cockpit-resolve-node-render-status'),
    path('api/cockpit/resolve-node/render/result/<str:job_id>/', cockpit_resolve_node_render_result, name='cockpit-resolve-node-render-result'),
    path('api/cockpit/resolve-node/jobs/', cockpit_resolve_node_jobs, name='cockpit-resolve-node-jobs'),
    path('api/cockpit/library/deliverables/', cockpit_library_deliverables, name='cockpit-library-deliverables'),
    path('api/cockpit/library/media/', cockpit_library_media, name='cockpit-library-media'),
    path('api/cockpit/approvals/', cockpit_approvals_list, name='cockpit-approvals-list'),
    path('api/cockpit/approvals/decision/<str:item_id>/decide/', cockpit_approve_decision, name='cockpit-approve-decision'),
    path('api/cockpit/approvals/gate/<str:gate_id>/decide/', cockpit_approve_gate, name='cockpit-approve-gate'),
    path('api/cockpit/alerts/', cockpit_alerts, name='cockpit-alerts'),
    path('api/cockpit/remediate/runbook/<str:alert_kind>/', cockpit_runbook, name='cockpit-runbook'),
    path('api/cockpit/remediate/retry-run/<str:run_id>/', cockpit_retry_run, name='cockpit-retry-run'),
    path('api/cockpit/remediate/incident-note/', cockpit_create_incident_note, name='cockpit-incident-note'),
    path('api/cockpit/audit/', cockpit_audit_list, name='cockpit-audit-list'),
    # P12: Agent Fleet Management
    path('api/cockpit/agents/', cockpit_agent_fleet, name='cockpit-agent-fleet'),
    path('api/cockpit/agents/<str:agent_name>/', cockpit_agent_detail, name='cockpit-agent-detail'),
    path('api/cockpit/agents/<str:agent_name>/run-now/', cockpit_agent_run_now, name='cockpit-agent-run-now'),
    path('api/cockpit/agents/<str:agent_name>/pause/', cockpit_agent_pause, name='cockpit-agent-pause'),
    path('api/cockpit/agents/<str:agent_name>/resume/', cockpit_agent_resume, name='cockpit-agent-resume'),
    # P13: Queues + Cost
    path('api/cockpit/queues/', cockpit_queues_overview, name='cockpit-queues-overview'),
    path('api/cockpit/queues/depths/', cockpit_queue_depths, name='cockpit-queue-depths'),
    path('api/cockpit/cost/', cockpit_cost_overview, name='cockpit-cost-overview'),
    # P14: Autopilot
    path('api/cockpit/autopilot/policies/', cockpit_autopilot_policies, name='cockpit-autopilot-policies'),
    path('api/cockpit/autopilot/policies/<str:policy_id>/toggle/', cockpit_autopilot_toggle, name='cockpit-autopilot-toggle'),
    path('api/cockpit/autopilot/evaluate/', cockpit_autopilot_evaluate, name='cockpit-autopilot-evaluate'),
    path('api/cockpit/autopilot/history/', cockpit_autopilot_history, name='cockpit-autopilot-history'),
    # P15: Run Trace
    path('api/cockpit/runs/<str:run_id>/trace/', cockpit_run_trace, name='cockpit-run-trace'),
    # P16: Config Control Plane
    path('api/cockpit/config/', cockpit_config_overview, name='cockpit-config-overview'),
    path('api/cockpit/config/providers/<str:provider_id>/toggle/', cockpit_config_toggle_provider, name='cockpit-config-toggle-provider'),
    path('api/cockpit/config/flags/', cockpit_config_flags, name='cockpit-config-flags'),
    path('api/cockpit/config/flags/<str:flag_id>/delete/', cockpit_config_delete_flag, name='cockpit-config-delete-flag'),
    path('api/cockpit/config/changes/', cockpit_config_changes, name='cockpit-config-changes'),
    # VIP personalization context
    path('api/cockpit/vip-context/', cockpit_vip_context, name='cockpit-vip-context'),
    path('api/cockpit/learning-loop/', cockpit_learning_loop, name='cockpit-learning-loop'),
    # P17: Incident Commander
    path('api/cockpit/incidents/', cockpit_incidents_list, name='cockpit-incidents-list'),
    path('api/cockpit/incidents/<str:incident_id>/', cockpit_incident_detail, name='cockpit-incident-detail'),
    path('api/cockpit/incidents/<str:incident_id>/update/', cockpit_incident_update, name='cockpit-incident-update'),
    path('api/cockpit/incidents/<str:incident_id>/events/', cockpit_incident_add_event, name='cockpit-incident-add-event'),
    # Ops Runs (Context Packet #9)
    path('api/cockpit/ops-runs/', cockpit_ops_runs_list, name='cockpit-ops-runs-list'),
    path('api/cockpit/ops-runs/<uuid:run_id>/', cockpit_ops_run_detail, name='cockpit-ops-run-detail'),
    # OBS Bridge proxy
    path('api/cockpit/obs/health/', cockpit_obs_health, name='cockpit-obs-health'),
    path('api/cockpit/obs/status/', cockpit_obs_status, name='cockpit-obs-status'),
    path('api/cockpit/obs/start/', cockpit_obs_start, name='cockpit-obs-start'),
    path('api/cockpit/obs/stop/', cockpit_obs_stop, name='cockpit-obs-stop'),
    path('api/cockpit/obs/last/', cockpit_obs_last, name='cockpit-obs-last'),
    path('api/cockpit/obs/upload/', cockpit_obs_upload, name='cockpit-obs-upload'),

    path('diagnostics/websockets/', WebSocketDiagnosticsView.as_view(), name='websocket-diagnostics'),
    path("api/llm/chat/", llm_chat),
    # AI Building Products page (moved up to ensure it's matched first)
    path('ai-building-products/', ai_building_products, name='ai-building-products'),

    # Session 1009: Removed agent-deployment include (orphan cleanup)

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
    path('api/projects/create/', create_partnership_project, name='partnership-project-create'),  # Session 520
    path('api/projects/<uuid:project_id>/', project_detail, name='project-detail'),
    path('api/projects/<uuid:project_id>/update/', update_partnership_project, name='partnership-project-update'),  # Session 520
    path('api/projects/<uuid:project_id>/delete/', delete_partnership_project, name='partnership-project-delete'),  # Session 520
    path('api/projects/<uuid:project_id>/agents/', project_agents, name='project-agents'),
    path('api/projects/<uuid:project_id>/assign-agent/', assign_agent_to_project, name='assign-agent'),
    path('api/projects/from-research/', create_project_from_research, name='create-project-from-research'),  # Session 302
    path('api/projects/<uuid:project_id>/add-research/', add_research_to_project, name='add-research-to-project'),  # Session 324
    path('api/projects/<uuid:project_id>/export-research-pdf/', export_research_pdf, name='export-research-pdf'),  # Session 325
    path('api/projects/<uuid:project_id>/export-comprehensive-pdf/', export_comprehensive_pdf, name='export-comprehensive-pdf'),  # Session 352
    path('api/projects/<uuid:project_id>/export-content/', export_written_content, name='export-written-content'),  # Session 521
    path('api/projects/<uuid:project_id>/update-content/', update_written_content, name='update-written-content'),  # Session 521
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

    # Session 628 + 631 + 632: Content Calendar APIs
    path('api/content-calendar/', content_calendar_main, name='content-calendar'),
    path('api/content-calendar/upcoming/', content_calendar_upcoming, name='content-calendar-upcoming'),
    path('api/content-calendar/history/', content_calendar_history, name='content-calendar-history'),
    path('api/content-calendar/reschedule/', content_calendar_reschedule, name='content-calendar-reschedule'),
    path('api/content-calendar/episode/<uuid:episode_id>/', content_calendar_episode_detail, name='content-calendar-episode-detail'),  # Session 631
    path('api/content-calendar/generate/<uuid:channel_id>/', content_calendar_generate, name='content-calendar-generate'),  # Session 632

    # Session 741: Content Channels API
    path('api/content-channels/', content_channels_list, name='content-channels-list'),
    path('api/content-channels/<uuid:channel_id>/', content_channel_detail, name='content-channel-detail'),
    path('api/content-channels/episode/<uuid:episode_id>/', content_episode_detail, name='content-episode-detail'),

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
    path('api/opportunities/<uuid:opportunity_id>/dismiss/', opportunity_dismiss, name='opportunity-dismiss'),  # Session 688
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
    path('api/distribution/gumroad/publish/', gumroad_publish_image, name='gumroad-publish-image'),  # Session 487
    path('api/distribution/gumroad/webhook/', gumroad_webhook, name='gumroad-webhook'),  # Session 487
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

    # Session 954: Learning Loop Effectiveness APIs
    path('api/learning/loop/stats/', learning_loop_stats, name='learning-loop-stats'),
    path('api/learning/loop/track/', track_learning_outcome, name='learning-loop-track'),
    path('api/learning/loop/run/', run_learning_cycle, name='learning-loop-run'),
    path('api/learning/loop/agent/', get_agent_learnings, name='learning-loop-agent'),

    # Session 954: RAG Observability Dashboard APIs
    path('api/rag/observability/dashboard/', rag_observability_dashboard, name='rag-observability-dashboard'),
    path('api/rag/observability/inventory/', rag_document_inventory, name='rag-observability-inventory'),
    path('api/rag/observability/budget/', rag_context_budget, name='rag-observability-budget'),
    path('api/rag/observability/boost/', rag_risk_boost_stats, name='rag-observability-boost'),
    path('api/rag/observability/critical-docs/', rag_critical_docs, name='rag-observability-critical-docs'),
    path('api/rag/observability/risk-distribution/', rag_risk_distribution, name='rag-observability-risk-distribution'),
    path('api/rag/observability/channels/', rag_retrieval_channels, name='rag-observability-channels'),
    path('api/rag/observability/classify/', rag_run_classification, name='rag-observability-classify'),

    # Session 449: Pipeline Learning APIs (Learning Loops for AI Content Pipeline)
    path('api/pipeline-learning/feedback/', pipeline_record_feedback, name='pipeline-learning-feedback'),
    path('api/pipeline-learning/engagement/', pipeline_record_engagement, name='pipeline-learning-engagement'),
    path('api/pipeline-learning/recommend/style/', pipeline_recommend_style, name='pipeline-learning-recommend-style'),
    path('api/pipeline-learning/recommend/voice/', pipeline_recommend_voice, name='pipeline-learning-recommend-voice'),
    path('api/pipeline-learning/leaderboard/styles/', pipeline_style_leaderboard, name='pipeline-learning-style-leaderboard'),
    path('api/pipeline-learning/insights/', pipeline_get_insights, name='pipeline-learning-insights'),
    path('api/pipeline-learning/insights/generate/', pipeline_generate_insights, name='pipeline-learning-insights-generate'),
    path('api/pipeline-learning/stats/', pipeline_get_statistics, name='pipeline-learning-stats'),

    # Session 886: Content Learning Feedback Loop (BlogPerformanceContextBuilder)
    path('api/content-learning/performance-context/', BlogPerformanceContextView.as_view(), name='content-learning-performance-context'),
    path('api/content-learning/metrics/', BlogPerformanceMetricsView.as_view(), name='content-learning-metrics'),
    path('api/content-learning/rules/', LearningRulesView.as_view(), name='content-learning-rules'),
    path('api/content-learning/trends/', ContentQualityTrendsView.as_view(), name='content-learning-trends'),

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
    path('api/v1/auth/debug/', auth_debug_view, name='auth-debug'),  # Session 830: Auth debugging

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
    path('api/agents/test/', test_agent_execution, name='agent-test'),  # Session 641: Test agent execution

    # Session 1009: Removed agent-analytics endpoints (orphan cleanup)
    path('api/system-health/', system_health_check, name='system-health'),
    path('api/system/version/', system_version, name='system-version'),  # Session 1078
    path('api/celery/status/', celery_status, name='celery-status'),  # Session 642: Celery monitoring

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
    path('api/collective/knowledge-topics/', get_knowledge_topics, name='collective-knowledge-topics'),  # Session 782
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
    path('api/v1/collective/shared-knowledge/', get_shared_knowledge, name='collective-shared-knowledge'),

    # Domain preferences (catch-all - must be LAST in preferences routes)
    path('api/preferences/<str:domain>/', domain_preferences, name='preferences-domain'),

    # Intelligence endpoints (temporary fix)
    path('api/v1/intelligence/skynet/status/', skynet_status, name='skynet-status'),
    path('api/v1/intelligence/opportunities/', live_opportunities, name='live-opportunities'),

    # Enhanced Neural Orchestra API endpoints (conditionally included)
] + ([
    # Learning workflow API integration pending
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
    path('api/autonomous-system/start/', AutonomousSystemStartView.as_view(), name='autonomous-start'),
    path('api/autonomous-system/status/', AutonomousSystemStatusView.as_view(), name='autonomous-status'),
    path('api/autonomous-system/pause/', AutonomousSystemPauseView.as_view(), name='autonomous-pause'),
    path('api/autonomous-system/resume/', AutonomousSystemResumeView.as_view(), name='autonomous-resume'),

    # Opportunity Aggregator endpoints
    # api/opportunities/ — REMOVED: duplicate of line 1858 (opportunity_list wins)
    path('api/opportunities/actionable/', get_actionable, name='get-actionable'),

    # Proposals API endpoints
    path('api/proposals/', lambda r: __import__('core.views_proposals', fromlist=['get_proposals']).get_proposals(r), name='get-proposals'),
    path('api/proposals/stats/', lambda r: __import__('core.views_proposals', fromlist=['get_proposal_stats']).get_proposal_stats(r), name='get-proposal-stats'),
    path('api/proposals/save-consciousness/', lambda r: __import__('core.views_proposals', fromlist=['save_consciousness_proposals']).save_consciousness_proposals(r), name='save-consciousness-proposals'),
    path('api/proposals/<str:proposal_id>/approve/', lambda r, proposal_id: __import__('core.views_proposals', fromlist=['approve_proposal']).approve_proposal(r), name='approve-proposal'),
    path('api/proposals/<str:proposal_id>/reject/', lambda r, proposal_id: __import__('core.views_proposals', fromlist=['reject_proposal']).reject_proposal(r), name='reject-proposal'),
    path('api/proposals/<str:proposal_id>/execute/', lambda r, proposal_id: __import__('core.views_proposals', fromlist=['execute_proposal']).execute_proposal(r), name='execute-proposal'),

    # Session 1077: Ops Console REST endpoints
    path('api/ops/slo-status/', lambda r: __import__('core.views_ops_console', fromlist=['slo_status']).slo_status(r), name='ops-slo-status'),
    path('api/ops/failure-signatures/', lambda r: __import__('core.views_ops_console', fromlist=['failure_signatures']).failure_signatures(r), name='ops-failure-signatures'),
    path('api/ops/blocked-agents/', lambda r: __import__('core.views_ops_console', fromlist=['blocked_agents']).blocked_agents(r), name='ops-blocked-agents'),

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
    path('agent-testing/', neural_orchestra_redirect, name='agent_testing_dashboard'),  # Session 688: Redirect to React /agents
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

    # Session 884: Home Page Boot API - AI OS boot experience
    path('api/home/boot/', home_boot, name='home-boot'),
    # Session 1000: Intelligence Desks API
    path('api/home/intelligence-desks/', intelligence_desks, name='intelligence-desks'),
    path('api/home/trigger-desks/', trigger_desks, name='trigger-desks'),
    path('api/home/purge-queue/', purge_queue, name='purge-queue'),

    # Dashboard Statistics - The Heart of Everything!
    path('api/dashboard/stats/', dashboard_stats, name='dashboard-stats'),
    path('api/dashboard/agents/', live_agent_activity, name='live-agent-activity'),
    path('api/dashboard/advisors/', advisor_insights, name='advisor-insights'),
    path('api/dashboard/summary/', dashboard_summary, name='dashboard-summary'),  # Session 459: Personalized greeting
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

    path('api/orchestrations/', orchestrations_list, name='orchestrations-list'),  # Session 884: Migrated from /api/v1/
    
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
    path('api/assistant/task-progress/', get_task_progress, name='assistant-task-progress'),  # Session 486: Task Progress

    # Development assistant endpoints — gated behind DEBUG (see bottom of file)
    path('api/assistant/bypass/', assistant_chat_bypass, name='assistant-chat-bypass'),
    path('api/assistant/feedback/', provide_feedback, name='personal-assistant-feedback'),
    path('api/assistant/reset/', reset_assistant, name='personal-assistant-reset'),
    path('api/assistant/attention-items/', get_attention_items, name='assistant-attention-items'),  # Session 574
    # Session 932: Unified attention aggregator (combines system + human attention)
    path('api/assistant/attention/unified/', get_unified_attention, name='assistant-attention-unified'),
    path('api/assistant/attention/stats/', get_attention_stats, name='assistant-attention-stats'),
    # Session 932: Unified PA REST endpoints (same behavior as WebSocket)
    path('api/pa/chat/', unified_pa_chat, name='unified-pa-chat'),
    path('api/pa/chat/status/<str:task_id>/', pa_chat_status, name='pa-chat-status'),
    path('api/pa/feedback/', pa_message_feedback, name='pa-message-feedback'),
    path('api/pa/context/', unified_pa_context, name='unified-pa-context'),
    # Session 974: PA conversation history endpoints
    path('api/pa/conversations/', list_pa_conversations, name='pa-conversations-list'),
    path('api/pa/conversations/new/', create_pa_conversation, name='pa-conversations-new'),
    path('api/pa/conversations/<str:conversation_id>/', get_pa_conversation, name='pa-conversations-detail'),
    # 3-way chat: store-only message post + incremental message polling
    path('api/pa/conversations/<str:conversation_id>/message/', pa_conversation_post_message, name='pa-conversation-post-message'),
    path('api/pa/conversations/<str:conversation_id>/messages/', pa_conversation_messages, name='pa-conversation-messages'),
    # Rigby activity feed — accountability dashboard
    path('api/pa/activity/', pa_activity_feed, name='pa-activity-feed'),
    # Session health — context-aware session management
    path('api/pa/conversations/<str:conversation_id>/health/', session_health, name='pa-session-health'),
    # Session 977: On-demand boardroom maintenance trigger
    path('api/pa/boardroom/maintenance/', trigger_boardroom_maintenance, name='boardroom-maintenance'),

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
    # Session 760: Unified execution history and detail for Output Modal
    path('api/v1/agents/unified-executions/', views_agent_execution.unified_execution_history, name='unified-execution-history'),
    path('api/v1/agents/execution/<str:execution_id>/', views_agent_execution.execution_detail, name='execution-detail'),
    path('api/v1/agents/test-execution/', views_agent_execution.test_agent_execution, name='agent-test-execution'),
    path('api/v1/agents/batch-execute/', views_agent_execution.execute_agent_batch, name='agent-batch-execute'),

    # Session 761: Agent Monitoring API Endpoints
    path('api/v1/agents/monitoring/dashboard/', views_agent_execution.monitoring_dashboard, name='agent-monitoring-dashboard'),
    path('api/v1/agents/monitoring/alerts/', views_agent_execution.monitoring_alerts, name='agent-monitoring-alerts'),
    path('api/v1/agents/monitoring/agent/<str:agent_name>/', views_agent_execution.monitoring_agent_detail, name='agent-monitoring-detail'),

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

    # Session 1009: Removed certifications endpoints (orphan cleanup)

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
    # Session 972: Removed duplicate api/learning/insights/ route — handled by list_insights at line 1883

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

    # Session 775: Missing chart endpoints for AnalyticsDashboardPage
    path('api/analytics/charts/agent-activity/', get_chart_agent_activity, name='chart-agent-activity'),
    path('api/analytics/charts/content-production/', get_chart_content_production, name='chart-content-production'),
    path('api/analytics/charts/revenue/', get_chart_revenue, name='chart-revenue'),
    path('api/analytics/charts/user-engagement/', get_chart_user_engagement, name='chart-user-engagement'),
    path('api/analytics/charts/spider-performance/', get_chart_spider_performance, name='chart-spider-performance'),
    path('api/analytics/charts/learning-progress/', get_chart_learning_progress, name='chart-learning-progress'),
    path('api/analytics/charts/collaboration/', get_chart_collaboration, name='chart-collaboration'),

    # Session 221: Advanced Analytics Phase F
    path('api/analytics/v2/overview/', analytics_overview_v2, name='analytics-overview-v2'),
    path('api/analytics/v2/usage-timeline/', usage_timeline_v2, name='usage-timeline-v2'),
    path('api/analytics/v2/performance-timeline/', performance_timeline_v2, name='performance-timeline-v2'),
    path('api/analytics/v2/cost-breakdown/', cost_breakdown_v2, name='cost-breakdown-v2'),
    path('api/analytics/v2/dashboards/', analytics_dashboards_v2, name='analytics-dashboards-v2'),
    path('api/analytics/v2/alerts/', analytics_alerts_v2, name='analytics-alerts-v2'),
    path('api/analytics/v2/realtime/', realtime_stats_v2, name='realtime-stats-v2'),
    path('api/analytics/v2/track/', track_event_v2, name='track-event-v2'),
    # Session 775: Missing v2 endpoints for Insights tab
    path('api/analytics/v2/top-performers/', top_performers_v2, name='top-performers-v2'),
    path('api/analytics/v2/anomalies/', anomalies_v2, name='anomalies-v2'),
    path('api/analytics/v2/forecast/', forecast_v2, name='forecast-v2'),
    path('api/analytics/v2/trends/', trends_v2, name='trends-v2'),
    path('api/analytics/v2/comparison/', comparison_v2, name='comparison-v2'),
    path('api/analytics/v2/breakdown/', breakdown_v2, name='breakdown-v2'),
    path('api/analytics/v2/export/', export_v2, name='export-v2'),

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
    path('api/tool/add-sfx-to-video/', add_sfx_to_video_view, name='add-sfx-to-video'),
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
    # Video Agents — resolve, transcribe, transcripts
    path('api/v1/video/resolve/', video_resolve, name='video-resolve'),
    path('api/v1/video/transcribe/', video_transcribe, name='video-transcribe'),
    path('api/v1/video/transcripts/', video_transcripts_list, name='video-transcripts-list'),
    path('api/v1/video/transcripts/<uuid:transcript_id>/', video_transcript_detail, name='video-transcript-detail'),
    path('api/v1/video/content-pack/', video_content_pack, name='video-content-pack'),

    # Video History endpoints (Session 44: Video Gallery)
    path('api/v1/video/history/', get_video_history, name='video-history'),
    path('api/v1/video/history/<str:video_id>/favorite/', toggle_video_favorite, name='toggle-video-favorite'),
    path('api/v1/video/history/<str:video_id>/view/', increment_video_view, name='increment-video-view'),
    path('api/v1/video/history/<str:video_id>/download/', increment_video_download, name='increment-video-download'),
    path('api/v1/video/history/<str:video_id>/', delete_video, name='delete-video'),

    # Session 479: DaVinci Resolve Renders Gallery
    path('api/resolve-renders/', get_resolve_renders, name='resolve-renders-list'),
    path('api/resolve-renders/<uuid:render_id>/download/', download_resolve_render, name='resolve-render-download'),
    path('api/resolve-renders/<uuid:render_id>/rate/', rate_resolve_render, name='resolve-render-rate'),

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

    # Session 926: Universal Agent Voice System - Listen Button TTS
    path('api/tts/generate/', lambda r: __import__('core.views_audio', fromlist=['tts_generate']).tts_generate(r), name='tts-generate'),
    path('api/tts/estimate/', lambda r: __import__('core.views_audio', fromlist=['tts_estimate']).tts_estimate(r), name='tts-estimate'),
    path('api/tts/voices/', lambda r: __import__('core.views_audio', fromlist=['tts_voices']).tts_voices(r), name='tts-voices'),

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
    # api/agents/status/ — REMOVED: duplicate of line 2286 (AgentStatusAPI wins)

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

    # Session 502: Podcast Studio APIs (real data, replaces mock)
    path('api/podcasts/list/', podcast_list_view, name='podcast-list-real'),
    path('api/podcasts/create/', podcast_create_view, name='podcast-create'),
    path('api/podcasts/stats/', podcast_stats_view, name='podcast-stats'),
    path('api/podcasts/<uuid:episode_id>/status/', podcast_status_view, name='podcast-status'),
    path('api/podcasts/<uuid:episode_id>/script/', podcast_script_view, name='podcast-script'),
    path('api/podcasts/<uuid:episode_id>/generate-audio/', podcast_generate_audio_view, name='podcast-generate-audio'),
    path('api/podcasts/<uuid:episode_id>/', podcast_delete_view, name='podcast-delete'),

    # Session 513: Campaign Orchestrator APIs
    path('api/campaigns/', campaign_list, name='campaign-list'),
    path('api/campaigns/create/', campaign_create, name='campaign-create'),
    path('api/campaigns/budget-tiers/', campaign_budget_tiers, name='campaign-budget-tiers'),
    path('api/campaigns/<uuid:campaign_id>/', campaign_detail, name='campaign-detail'),
    path('api/campaigns/<uuid:campaign_id>/start/', campaign_start, name='campaign-start'),
    path('api/campaigns/<uuid:campaign_id>/status/', campaign_status, name='campaign-status'),
    path('api/campaigns/<uuid:campaign_id>/deliverables/', campaign_deliverables, name='campaign-deliverables'),
    path('api/campaigns/<uuid:campaign_id>/delete/', campaign_delete, name='campaign-delete'),

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
    path('api/v1/agents/comprehensive/', comprehensive_agents_list, name='agents-comprehensive'),  # Session 663

    # Session 1036 → now wired to real data
    path('api/v1/agents/channels/', agent_channels, name='v1-agent-channels'),
    path('api/v1/agents/tools/', agent_tools, name='v1-agent-tools'),
    path('api/v1/agents/templates/', agent_templates, name='v1-agent-templates'),

    # Odds & Sports Analytics APIs (from DBAO tools-manifest)
    path('api/v1/odds/convert-odds/', convert_odds, name='odds-convert'),
    path('api/v1/odds/expected-value/', calculate_expected_value, name='expected-value'),
    path('api/v1/odds/kelly-criterion/', calculate_kelly_criterion, name='kelly-criterion'),
    path('api/v1/odds/arbitrage/', detect_arbitrage, name='arbitrage'),
    path('api/v1/sports/analyze-game/', sports_game_analysis, name='sports-analyze'),
    path('api/v1/sports/live-opportunities/', live_betting_opportunities, name='live-opportunities'),
    path('api/v1/sports/live-odds/', live_odds, name='live-odds'),
    path('api/v1/sports/live-odds-scores/', live_odds_with_scores, name='live-odds-scores'),
    path('api/v1/sports/events/<str:event_id>/props/', get_player_props, name='player-props'),
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
    # Session 559: GET endpoint for live arbitrage scanning
    path('api/v1/betting/arbitrage/scan/', scan_arbitrage_opportunities, name='betting-arbitrage-scan'),
    # Session 560: Futures odds endpoint
    path('api/v1/betting/futures/', get_futures_odds, name='betting-futures'),
    # Session 560: Web wager logging
    path('api/v1/betting/wager/', log_wager, name='betting-wager-log'),
    # Session 561: Line Movement Charts
    path('api/v1/betting/line-movement/', get_line_movement, name='betting-line-movement'),
    path('api/v1/betting/line-movement/<str:game_id>/', get_line_movement, name='betting-line-movement-game'),
    path('api/v1/betting/movers/', get_games_with_movement, name='betting-movers'),

    # Session 563: Bet Tracking APIs
    path('api/v1/betting/place/', place_bet, name='betting-place'),
    path('api/v1/betting/wagers/', get_wagers, name='betting-wagers'),
    path('api/v1/betting/wagers/<uuid:wager_id>/', get_wager_detail, name='betting-wager-detail'),
    path('api/v1/betting/wagers/<uuid:wager_id>/settle/', settle_wager, name='betting-wager-settle'),
    path('api/v1/betting/wagers/<uuid:wager_id>/cancel/', cancel_wager, name='betting-wager-cancel'),
    path('api/v1/betting/stats/', get_betting_stats, name='betting-stats'),
    path('api/v1/betting/recent/', get_recent_activity, name='betting-recent'),
    path('api/v1/betting/quick-pick/', quick_pick, name='betting-quick-pick'),
    # Session 995B: Sports betting intelligence endpoints
    path('api/v1/betting/todays-games/', get_todays_games, name='betting-todays-games'),
    path('api/v1/betting/brief/', get_betting_brief, name='betting-brief'),
    path('api/v1/betting/sharp-action/', get_sharp_action, name='betting-sharp-action'),
    path('api/v1/betting/track-record/', get_ai_track_record, name='betting-track-record'),
    path('api/v1/betting/pipeline-status/', get_pipeline_status, name='betting-pipeline-status'),

    # Session 562: Push Notifications for Arb Alerts
    path('api/v1/push/vapid-key/', get_vapid_public_key, name='push-vapid-key'),
    path('api/v1/push/subscribe/', subscribe_push, name='push-subscribe'),
    path('api/v1/push/unsubscribe/', unsubscribe_push, name='push-unsubscribe'),
    path('api/v1/push/preferences/', notification_preferences, name='push-preferences'),
    path('api/v1/push/status/', get_subscription_status, name='push-status'),
    path('api/v1/push/test/', send_test_push, name='push-test'),

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

    # Video RAG ingest
    path('api/documents/ingest-video/', ingest_video, name='documents-ingest-video'),
    path('api/documents/ingest-youtube-whisper/', ingest_youtube_whisper, name='documents-ingest-youtube-whisper'),
    path('api/documents/ingest-status/<str:job_id>/', ingest_video_status, name='documents-ingest-status'),

    # Session 403: Legal Case Files APIs
    path('api/legal/case-files/', list_legal_case_files, name='legal-case-files-list'),
    path('api/legal/case-files/upload/', upload_legal_case_file, name='legal-case-files-upload'),
    path('api/legal/case-files/<uuid:document_id>/', get_legal_case_file, name='legal-case-files-get'),
    path('api/legal/case-files/<uuid:document_id>/analyze/', analyze_legal_case_file, name='legal-case-files-analyze'),
    path('api/legal/case-files/<uuid:document_id>/delete/', delete_legal_case_file, name='legal-case-files-delete'),
    # Session 407: Document section export
    path('api/legal/export-section/', export_legal_section, name='legal-export-section'),

    # Multi-LLM Provider Integration APIs (legacy - hardcoded data)
    path('api/v1/llm/providers/', available_llm_providers, name='llm-providers'),
    path('api/v1/llm/intelligent-selection/', intelligent_model_selection, name='intelligent-model-selection'),
    path('api/v1/llm/multi-model-compare/', multi_model_comparison, name='multi-model-compare'),
    path('api/v1/llm/analytics/', llm_analytics, name='llm-analytics'),
    path('api/v1/llm/preferences/', set_model_preferences, name='set-llm-preferences'),

    # Session 699: LLM Routing APIs (real database-backed)
    # Session 871: LLM routing migrated to /api/
    path('api/llm-routing/status/', llm_routing_status, name='llm-routing-status'),
    path('api/llm-routing/providers/', llm_providers_list, name='llm-routing-providers'),
    path('api/llm-routing/models/', llm_models_list, name='llm-routing-models'),
    path('api/llm-routing/agent-configs/', agent_llm_configs_list, name='llm-routing-agent-configs'),
    path('api/llm-routing/logs/', llm_call_logs_list, name='llm-routing-logs'),
    path('api/llm-routing/cost-analytics/', llm_cost_analytics, name='llm-routing-cost-analytics'),
    path('api/llm-routing/agent-configs/<str:agent_name>/', update_agent_llm_config, name='llm-routing-update-agent-config'),

    # WorkflowRun API (must be before workflows.urls include to avoid 404)
    path('api/v1/workflows/runs/', views_workflow_run.workflow_run_list, name='workflow-run-list'),
    path('api/v1/workflows/runs/<uuid:run_id>/', views_workflow_run.workflow_run_detail, name='workflow-run-detail'),
    path('api/v1/workflows/runs/<uuid:run_id>/dispatch/', views_workflow_run.workflow_run_dispatch, name='workflow-run-dispatch'),
    path('api/v1/workflows/queue-diagnostic/', views_workflow_run.workflow_queue_diagnostic, name='workflow-queue-diagnostic'),
    path('api/v1/workflows/add-consumer/', views_workflow_run.workflow_add_consumer, name='workflow-add-consumer'),

    # App-specific APIs - See docs/API_PATH_POLICY.md for conventions
    # Note: Some modules use /api/v1/ to avoid path conflicts with core/urls.py endpoints
    path('api/v1/workflows/', include('workflows.urls')),  # REAL workflows - conflicts with /api/workflows/
    # Session 872: Removed dashboard.urls include - endpoints unused (frontend uses /api/dashboard/ from core)
    # Session 1009: Removed style-memory, agents.urls, coleadership, render-jobs includes (orphan cleanup)
    path('api/pipelines/', include('pipelines.urls')),  # Creative Pipelines (Session 871: migrated to /api/)
    path('api/v1/sports/', include('sports.urls')),  # Sports/Betting module - conflicts with /api/sports/
    path('api/v1/content/', include('content.urls')),  # Content Generation - conflicts with /api/content/
    path('api/v1/self-awareness/', include('self_awareness.urls')),  # Self-Awareness module
    # path('api/v1/campaigns/', include('campaigns.urls')),  # Campaigns module (archived)
    path('api/mythology/', include('mythology.urls')),  # Mythology (Session 871: migrated to /api/)

    # Session 542: Research Demo API - Interactive visualization of knowledge pipeline
    path('api/v1/research/network-graph/', views_research_demo.network_graph_api, name='research-network-graph'),
    path('api/v1/research/live-feed/', views_research_demo.live_feed_api, name='research-live-feed'),
    path('api/v1/research/stats/', views_research_demo.stats_api, name='research-stats'),
    path('api/v1/research/mythology-gate/', views_research_demo.mythology_gate_api, name='research-mythology-gate'),
    # Session 552: Self-blog API
    path('api/v1/research/self-blog/', views_research_demo.self_blog_api, name='research-self-blog'),
    # Session 780: Paginated self-blog list
    path('api/v1/research/self-blog/list/', views_research_demo.self_blog_list_api, name='research-self-blog-list'),
    # Session 570: Self-blog by ID endpoint
    path('api/v1/research/self-blog/<uuid:blog_id>/', views_research_demo.self_blog_by_id_api, name='research-self-blog-by-id'),
    # Session 971: Related blogs endpoint
    path('api/v1/research/self-blog/<uuid:blog_id>/related/', views_research_demo.related_self_blogs_api, name='research-self-blog-related'),
    # Session 814: Delete self-blog endpoint
    path('api/v1/research/self-blog/<uuid:blog_id>/delete/', views_research_demo.delete_self_blog_api, name='research-self-blog-delete'),
    # Session 833: Approve and publish self-blog endpoints
    path('api/v1/research/self-blog/<uuid:blog_id>/approve/', views_research_demo.approve_self_blog_api, name='research-self-blog-approve'),
    path('api/v1/research/self-blog/<uuid:blog_id>/publish/', views_research_demo.publish_self_blog_api, name='research-self-blog-publish'),
    # Session 865: EditorAgent enhancement endpoint
    path('api/v1/research/self-blog/<uuid:blog_id>/enhance/', views_research_demo.enhance_self_blog_api, name='research-self-blog-enhance'),
    # Session 643: Enabled self-blog generation endpoints
    path('api/v1/research/self-blog/generate/', views_research_demo.generate_self_blog_api, name='research-generate-self-blog'),
    # Phase 4: v2 deliberation pipeline
    path('api/v1/research/self-blog/generate-v2/', views_research_demo.generate_v2_blog_api, name='generate-v2-blog'),
    path('api/v1/research/self-blog/task/<str:task_id>/', views_research_demo.self_blog_task_status_api, name='research-self-blog-task'),

    # Session G1: Competitor Comparison API
    path('api/v1/competitor/compare/generate/', views_competitor_comparison.generate_comparison_api, name='competitor-compare-generate'),
    path('api/v1/competitor/compare/<uuid:comparison_id>/', views_competitor_comparison.comparison_detail_api, name='competitor-compare-detail'),
    path('api/v1/competitor/compare/', views_competitor_comparison.comparison_list_api, name='competitor-compare-list'),

    # Session 588: System Insights API
    path('api/v1/research/system-insights/', views_research_demo.system_insights_api, name='research-system-insights'),
    # Session 622: Deliverables API
    path('api/v1/research/deliverables/', views_research_demo.deliverables_api, name='research-deliverables'),

    # Session 622: Document Registry / Initiatives API
    path('api/initiatives/', views_research_demo.initiatives_api, name='initiatives-list'),  # Session 871: migrated to /api/
    path('api/initiatives/populate/', views_research_demo.populate_initiatives_api, name='initiatives-populate'),
    path('api/initiatives/trigger/', views_research_demo.trigger_initiative_pipeline_api, name='initiatives-trigger'),  # Session 880: Manual trigger
    path('api/initiatives/kickstart/', views_initiative_kickstart.kickstart_initiatives, name='initiatives-kickstart'),  # Session 884: Kickstart stuck initiatives
    path('api/initiatives/fix-stages/', views_initiative_kickstart.fix_initiative_stages, name='initiatives-fix-stages'),  # Session 884: Fix inconsistent stages
    path('api/initiatives/retry-stuck/', views_initiative_kickstart.retry_stuck_initiatives, name='initiatives-retry-stuck'),  # Session 884: Retry stuck Stage 1 initiatives
    path('api/initiatives/circuit-breaker/', views_initiative_kickstart.initiative_circuit_breaker, name='initiatives-circuit-breaker'),  # Session 884: Pause/resume initiative creation
    path('api/initiatives/cleanup/', views_initiative_kickstart.cleanup_initiatives, name='initiatives-cleanup'),  # Session 884: Archive/delete stuck initiatives
    path('api/initiatives/backfill-documents/', views_initiative_kickstart.backfill_stage_documents, name='initiatives-backfill-documents'),  # Session 915: Backfill missing stage documents
    path('api/initiatives/fix-titles/', views_initiative_kickstart.fix_initiative_titles, name='initiatives-fix-titles'),  # Session 916: Fix messy initiative titles
    path('api/initiatives/reset-premature-completed/', views_initiative_kickstart.reset_premature_completed, name='initiatives-reset-premature-completed'),  # Session 920: Reset prematurely-completed initiatives
    path('api/initiatives/pipeline-health/', views_initiative_kickstart.pipeline_health, name='initiatives-pipeline-health'),  # Session 921: Real-time pipeline health monitoring
    path('api/initiatives/diagnose-stuck/', views_initiative_kickstart.diagnose_stuck_initiatives, name='initiatives-diagnose-stuck'),  # Session 921: Diagnose why initiatives aren't progressing
    path('api/initiatives/trigger-backfill/', views_initiative_kickstart.trigger_stage_backfill, name='initiatives-trigger-backfill'),  # Session 921: Trigger Stage 1 document generation
    path('api/initiatives/<uuid:initiative_id>/start-conversation/', views_initiative_kickstart.start_initiative_conversation, name='initiatives-start-conversation'),  # Session 928: Start conversation about initiative
    path('api/initiatives/<uuid:initiative_id>/origin-trace/', views_research_demo.initiative_origin_trace_api, name='initiatives-origin-trace'),  # Session 898: Full origin chain trace
    # Session 902: Action Items API
    path('api/initiatives/<uuid:initiative_id>/action-items/', views_research_demo.initiative_action_items_api, name='initiative-action-items'),
    path('api/initiatives/<uuid:initiative_id>/action-items/create/', views_research_demo.action_item_create_api, name='action-item-create'),
    path('api/initiatives/<uuid:initiative_id>/action-items/extract/', views_research_demo.extract_action_items_api, name='action-items-extract'),
    path('api/action-items/<uuid:item_id>/', views_research_demo.action_item_update_api, name='action-item-update'),
    path('api/action-items/<uuid:item_id>/delete/', views_research_demo.action_item_delete_api, name='action-item-delete'),
    path('api/action-items/extract/', views_research_demo.extract_action_items_api, name='action-items-bulk-extract'),  # Bulk extract without initiative
    # Session 914.7: Operating Rhythm API
    path('api/operating-rhythm/', views_research_demo.operating_rhythm_api, name='operating-rhythm'),
    path('api/initiatives/<uuid:initiative_id>/rhythm/', views_research_demo.initiative_rhythm_api, name='initiative-rhythm'),
    # Session 919: Set Founder Intent API
    path('api/initiatives/<uuid:initiative_id>/founder-intent/', views_research_demo.set_founder_intent_api, name='initiative-set-founder-intent'),

    # Session 544: Autonomous Reasoning Engine APIs
    path('api/v1/reasoning/thoughts/', views_autonomous_reasoning.thoughts_api, name='reasoning-thoughts'),
    path('api/v1/reasoning/thoughts/<uuid:thought_id>/', views_autonomous_reasoning.thought_detail_api, name='reasoning-thought-detail'),
    path('api/v1/reasoning/actions/', views_autonomous_reasoning.actions_api, name='reasoning-actions'),
    path('api/v1/reasoning/trigger/', views_autonomous_reasoning.trigger_thinking_api, name='reasoning-trigger'),
    path('api/v1/reasoning/task/<str:task_id>/', views_autonomous_reasoning.thinking_task_status_api, name='reasoning-task-status'),
    path('api/v1/reasoning/config/', views_autonomous_reasoning.reasoning_config_api, name='reasoning-config'),
    path('api/v1/reasoning/config/update/', views_autonomous_reasoning.update_reasoning_config_api, name='reasoning-config-update'),
    path('api/v1/reasoning/dashboard/', views_autonomous_reasoning.reasoning_dashboard_api, name='reasoning-dashboard'),
    # Session 872: Pilot Readiness Gates API
    path('api/v1/reasoning/gates/', views_autonomous_reasoning.gates_api, name='reasoning-gates'),

    # Session 546: Concern Tracking APIs
    path('api/v1/reasoning/concerns/', views_autonomous_reasoning.concerns_dashboard_api, name='concerns-dashboard'),
    path('api/v1/reasoning/concerns/verify/', views_autonomous_reasoning.verify_concerns_api, name='concerns-verify'),
    path('api/v1/reasoning/concerns/register-historical/', views_autonomous_reasoning.register_historical_concerns_api, name='concerns-register-historical'),
    path('api/v1/reasoning/concerns/<uuid:concern_id>/', views_autonomous_reasoning.concern_detail_api, name='concern-detail'),

    # Session 549: Human Action Required APIs
    path('api/v1/reasoning/actions/pending/', views_autonomous_reasoning.pending_human_actions_api, name='pending-actions'),
    path('api/v1/reasoning/actions/create/', views_autonomous_reasoning.create_action_notifications_api, name='create-actions'),
    path('api/v1/reasoning/actions/<uuid:notification_id>/respond/', views_autonomous_reasoning.handle_human_action_api, name='handle-action'),

    # Session 550: Research Demo APIs — REMOVED: exact duplicates of Session 542 routes (lines 3072-3075)

    # Session 1009: Removed odds-calc include (orphan cleanup)
    path('api/v1/intelligence/', include('intelligence.urls')),  # Intelligence module with action plan execution
    path('api/v1/persistence/', include('persistence.urls')),  # Data Persistence Infrastructure

    # System Reality Self-Awareness Engine
    path('truth/', include('core.truth_urls')),  # Truth Dashboard and Reality APIs

    # AI Platform Learning and Verification APIs
    path('', include('ai_platform.urls')),  # AI Platform endpoints

    # Learning Dashboard APIs for real-time proof
    # api/learning/dashboard/ — REMOVED: duplicate of line 1966 (learning_dashboard wins)
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

    # Session 484: Spider Health Dashboard - Error Diagnostics & Controls
    path('api/spider-health/summary/', spider_health_summary, name='spider-health-summary'),
    path('api/spider-health/executions/', spider_execution_logs, name='spider-health-executions'),
    path('api/spider-health/executions/<uuid:execution_id>/', spider_error_detail, name='spider-health-error-detail'),
    path('api/spider-health/executions/<uuid:execution_id>/retry/', retry_spider_execution, name='spider-health-retry'),
    path('api/spider-health/embedding-coverage/', spider_embedding_coverage, name='spider-health-embedding-coverage'),
    path('api/spider-health/run/<str:spider_name>/', run_spider_manual, name='spider-health-run'),

    # Session 624: System Reality Check - Verify all autonomous systems
    path('api/v1/system/reality-check/', lambda r: __import__('django.http', fromlist=['JsonResponse']).JsonResponse(
        __import__('core.services.system_reality_checker', fromlist=['SystemRealityChecker']).SystemRealityChecker(
            lookback_hours=int(r.GET.get('lookback', 6))
        ).run()
    ), name='system-reality-check'),

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

    # Session 783: Spider News Feed
    path('api/spider-feed/', spider_feed, name='spider-feed'),
    path('api/spider-feed/trending/', spider_feed_trending, name='spider-feed-trending'),
    path('api/spider-feed/item/<uuid:item_id>/', spider_feed_item_detail, name='spider-feed-item-detail'),
    path('api/spider-feed/<uuid:item_id>/annotate/', spider_feed_annotate, name='spider-feed-annotate'),
    path('api/spider-feed/<uuid:item_id>/vote/', spider_feed_vote, name='spider-feed-vote'),
    path('api/spider-feed/stats/', spider_feed_stats, name='spider-feed-stats'),

    # Session 998B: Sports Betting Hub Feed
    path('api/sports-hub/feed/', sports_hub_feed, name='sports-hub-feed'),

    # Session 784: Documentation Index API
    path('api/docs/index/', docs_index, name='docs-index'),
    path('api/docs/stats/', docs_stats, name='docs-stats'),
    path('api/docs/graph/', docs_graph_summary, name='docs-graph'),
    path('api/docs/detail/<path:doc_path>/', docs_detail, name='docs-detail'),

    # Session 536: Cross-references for Intelligence Command Center
    path('api/intelligence/cross-references/', intelligence_cross_references, name='intelligence-cross-references'),
    path('api/spider-intelligence/detail/<str:spider_name>/', spider_detail, name='spider-intelligence-detail'),
    # Session 1009: Removed agent-intelligence/detail endpoint (orphan cleanup)
    path('api/situation-intelligence/detail/<str:situation_type>/', situation_detail, name='situation-intelligence-detail'),  # Session 537

    # Session 558: Prediction Markets API
    path('api/prediction-markets/', get_prediction_markets, name='prediction-markets'),
    path('api/sports-odds/', get_sports_odds, name='sports-odds'),

    # Session 388: Income Action Pipeline - Spider to Income Bridge
    path('api/income/save-opportunity/', income_save_opportunity, name='income-save-opportunity'),
    path('api/income/generate-application/', income_generate_application, name='income-generate-application'),
    path('api/income/update-status/', income_update_status, name='income-update-status'),
    path('api/income/opportunities/', income_get_opportunities, name='income-opportunities'),
    path('api/income/statistics/', income_get_statistics, name='income-statistics'),
    path('api/income/quick-apply/', income_quick_apply, name='income-quick-apply'),

    # Session 1009: Removed agent-intelligence endpoints (orphan cleanup)

    # Session 1009: Removed agent-collab endpoints (orphan cleanup)

    # Session 1031: Re-added — frontend still polls this endpoint
    path('api/agent-learning/activity/', get_knowledge_transfer_feed, name='agent-learning-activity'),

    # Session 244: Agent Conversations API
    path('api/agent-conversations/', get_agent_conversations, name='agent-conversations'),
    path('api/agent-conversations/<uuid:conversation_id>/', get_agent_conversation_detail, name='agent-conversation-detail'),  # Session 835
    path('api/agent-conversations/trigger/', trigger_agent_conversation, name='trigger-agent-conversation'),
    path('api/agent-conversations/task/<str:task_id>/', get_conversation_task_status, name='conversation-task-status'),  # Session 827

    # Session 717: Conversation Contract Analytics API
    path('api/conversation-contract/overview/', get_conversation_contract_overview, name='conversation-contract-overview'),
    path('api/conversation-contract/<uuid:conversation_id>/', get_conversation_contract_detail, name='conversation-contract-detail'),

    # Session 247: Agent Dreams API
    # Session 843: Added dream detail endpoint
    path('api/agent-dreams/', get_agent_dreams, name='agent-dreams'),
    path('api/agent-dreams/<uuid:dream_id>/', get_agent_dream_detail, name='agent-dream-detail'),
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
    # Session 942: Bulk decision actions
    path('api/boardroom/decisions/bulk-promote/', bulk_promote_decisions, name='bulk-promote-decisions'),
    path('api/boardroom/decisions/bulk-reject/', bulk_reject_decisions, name='bulk-reject-decisions'),
    # Session 604: Decision Prioritization
    path('api/boardroom/decisions/prioritized/', get_prioritized_decisions, name='prioritized-decisions'),
    path('api/boardroom/decisions/<uuid:decision_id>/priority/', get_decision_priority, name='decision-priority'),
    # Session 602: Boardroom Learning Integration
    path('api/boardroom/decisions/<uuid:decision_id>/learning/', get_decision_learning_context, name='decision-learning-context'),
    path('api/boardroom/learning-summary/', get_boardroom_learning_summary, name='boardroom-learning-summary'),
    # Session 659: Governance Stats API
    path('api/boardroom/governance-stats/', get_governance_stats, name='governance-stats'),
    # Session 660: Celery & System Health APIs
    path('api/celery/stats/', get_celery_stats, name='celery-stats'),
    path('api/icc/health/', get_system_health, name='icc-health'),

    # Session 603: Learning Velocity Dashboard
    path('api/learning/velocity/', get_learning_velocity_dashboard, name='learning-velocity-dashboard'),
    path('api/learning/velocity/theme/<str:theme>/', get_theme_velocity, name='theme-velocity'),

    # Session 590: Pilot Readiness Gate API
    path('api/pilot-gates/', get_pilot_readiness_gates, name='pilot-gates'),
    path('api/pilot-gates/<uuid:gate_id>/', get_pilot_gate_detail, name='pilot-gate-detail'),
    path('api/pilot-gates/<uuid:gate_id>/status/', update_gate_status, name='pilot-gate-status'),
    path('api/pilot-gates/<uuid:gate_id>/items/<uuid:item_id>/', update_checklist_item, name='pilot-gate-item'),
    path('api/pilot-gates/create/<uuid:decision_id>/', create_pilot_gate, name='pilot-gate-create'),
    # Session 592: Pilot Execution API
    path('api/pilot-gates/<uuid:gate_id>/pilot/', start_pilot_execution, name='start-pilot-execution'),
    path('api/pilot-gates/<uuid:gate_id>/pilot/<uuid:pilot_id>/complete/', complete_pilot_execution, name='complete-pilot-execution'),
    # Session 593: Gate Dashboard
    path('api/pilot-gates/dashboard/', get_pilot_gate_dashboard, name='pilot-gate-dashboard'),
    # Session 594: Regenerate checklist content & Approve all
    path('api/pilot-gates/<uuid:gate_id>/regenerate/', regenerate_checklist_content, name='regenerate-checklist-content'),
    path('api/pilot-gates/<uuid:gate_id>/approve-all/', approve_all_checklist_items, name='approve-all-checklist-items'),
    # Session 595: Pilot Executions Dashboard
    path('api/pilots/dashboard/', get_pilot_executions_dashboard, name='pilot-executions-dashboard'),
    # Session 690: Implementation Pipeline
    path('api/pilots/<uuid:pilot_id>/implementation/', get_pilot_implementation, name='pilot-implementation'),
    path('api/pilots/<uuid:pilot_id>/implement/', trigger_pilot_implementation, name='trigger-pilot-implementation'),
    # Session 596: Experiment Tracking Registry
    # Session 692: Added /pilot-experiments/ to avoid conflict with A/B experiments at /experiments/
    path('api/pilot-experiments/', get_experiments, name='pilot-experiments-list'),
    # api/experiments/ — REMOVED: duplicate of line 2137 (list_experiments wins). Use /api/pilot-experiments/ above instead.
    path('api/experiments/portfolio/', get_experiment_portfolio, name='experiment-portfolio'),
    path('api/experiments/<uuid:experiment_id>/update-kpi/', update_experiment_kpi, name='update-experiment-kpi'),
    path('api/experiments/<uuid:experiment_id>/complete/', complete_experiment, name='complete-experiment'),
    # Session 657: Raise target for exceeding experiments
    path('api/experiments/<uuid:experiment_id>/raise-target/', raise_experiment_target, name='raise-experiment-target'),
    # Session 598: Learning Loop UI
    path('api/experiments/learnings/', get_experiment_learnings, name='experiment-learnings'),
    path('api/experiments/patterns/', get_success_patterns, name='experiment-patterns'),
    # Session 599: Experiment Halt
    path('api/experiments/<uuid:experiment_id>/halt/', halt_experiment, name='halt-experiment'),
    # Session 600: Experiment Metrics & Rollback
    path('api/experiments/<uuid:experiment_id>/metrics/', get_experiment_metrics, name='experiment-metrics'),
    path('api/experiments/<uuid:experiment_id>/rollback/', get_rollback_plan, name='experiment-rollback'),
    path('api/experiments/<uuid:experiment_id>/remediation/', update_remediation_step, name='experiment-remediation'),
    # Session 606: Experiment Suggestions
    path('api/experiments/suggestions/', get_experiment_suggestions, name='experiment-suggestions'),
    # Session 607: Pilot Progress Dashboard
    path('api/pilots/progress/', get_pilot_progress_dashboard, name='pilot-progress-dashboard'),
    path('api/pilots/progress/<uuid:experiment_id>/', get_pilot_progress_detail, name='pilot-progress-detail'),
    # Session 609: Auto KPI Tracking
    path('api/experiments/kpis/update/', trigger_kpi_update, name='trigger-kpi-update'),
    path('api/experiments/<uuid:experiment_id>/kpi-trend/', get_experiment_kpi_trend, name='experiment-kpi-trend'),
    path('api/experiments/kpi-trends/', get_all_experiment_kpi_trends, name='all-experiment-kpi-trends'),
    # Session 611: KPI Alerts
    path('api/experiments/kpi-alerts/', get_kpi_alerts, name='kpi-alerts'),
    path('api/experiments/kpi-summary/', get_weekly_kpi_summary, name='kpi-weekly-summary'),
    # Session 614: Recent Activity Feed
    path('api/recent-activity/', get_system_recent_activity, name='recent-activity'),
    # Session 615: Experiment Recommendations
    path('api/experiment-recommendations/', get_experiment_recommendations, name='experiment-recommendations'),

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
    path('api/memory-palace/memories/', list_all_memories, name='memory-palace-list'),  # Session 860
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

    # Session 1009: Removed agent-mood endpoints (orphan cleanup)

    # Session 253: Agent Relationships API (Session 871: Alliance/Rivalry routes removed)
    path('api/agent-relationships/', get_relationships_overview, name='agent-relationships-overview'),
    path('api/agent-relationships/agent/<uuid:agent_id>/', get_agent_relationships, name='agent-relationships-detail'),
    path('api/agent-relationships/create/', create_relationship, name='agent-relationship-create'),
    path('api/agent-relationships/relationship/<uuid:relationship_id>/interact/', record_interaction, name='agent-relationship-interact'),
    path('api/agent-relationships/relationship/<uuid:relationship_id>/events/', get_relationship_events, name='agent-relationship-events'),
    path('api/agent-relationships/auto-generate/', auto_generate_relationships, name='agent-relationships-auto'),

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

    # Session 484: Autonomous Systems Dashboard API
    # Visibility into the 19 autonomous situations running 24/7
    path('api/autonomous/situations/', list_situations, name='autonomous-situations'),
    path('api/autonomous/situations/<str:situation_type>/', situation_detail, name='autonomous-situation-detail'),
    path('api/autonomous/situations/<str:situation_type>/toggle/', toggle_situation, name='autonomous-situation-toggle'),
    path('api/autonomous/situations/<str:situation_type>/run-now/', run_situation_now, name='autonomous-situation-run-now'),
    path('api/autonomous/triggers/', list_triggers, name='autonomous-triggers'),
    path('api/autonomous/trigger-events/', list_trigger_events, name='autonomous-trigger-events'),
    path('api/autonomous/analytics/summary/', autonomous_analytics_summary, name='autonomous-analytics-summary'),

    # Session 484: Trigger Tuning API
    path('api/autonomous/triggers/<uuid:trigger_id>/', trigger_detail, name='autonomous-trigger-detail'),
    path('api/autonomous/triggers/<uuid:trigger_id>/update/', update_trigger, name='autonomous-trigger-update'),
    path('api/autonomous/triggers/<uuid:trigger_id>/toggle/', toggle_trigger, name='autonomous-trigger-toggle'),
    path('api/autonomous/triggers/<uuid:trigger_id>/reset-cooldown/', reset_trigger_cooldown, name='autonomous-trigger-reset-cooldown'),
    path('api/autonomous/triggers/<uuid:trigger_id>/analytics/', trigger_analytics, name='autonomous-trigger-analytics'),

    # Orphan data surfaces — predictions & analyses
    path('api/autonomous/viral-predictions/', viral_predictions_api, name='viral-predictions'),
    path('api/autonomous/skill-gaps/', skill_gap_api, name='skill-gaps'),

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
    # api/learning/status/ — REMOVED: duplicate of line 2465 (learning_status_api wins)
    path('api/learning/status/<str:session_id>/', get_learning_status, name='learning-status-by-session'),
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
    # api/ecosystem/stats/ — REMOVED: duplicate of line 1741 (ecosystem_stats wins)
    path('api/ecosystem/feed/', get_live_learning_feed, name='ecosystem-feed'),
    path('api/ecosystem/network/', get_agent_network, name='ecosystem-network'),
    path('api/ecosystem/trigger/', trigger_learning_event, name='ecosystem-trigger'),
    
    # Advanced Workflow Orchestration APIs (BACKUP/FALLBACK - these should NOT conflict now)
    path('api/v1/workflows/create-advanced/', create_advanced_workflow, name='create-advanced-workflow'),
    path('api/v1/workflows/execute-advanced/', execute_advanced_workflow, name='execute-advanced-workflow'),
    path('api/v1/workflows/execution/<str:execution_id>/status/', get_workflow_execution_status, name='workflow-execution-status'),
    path('api/v1/workflows/execution/<str:execution_id>/output/', get_workflow_output, name='workflow-execution-output'),  # Session 735: View full output
    path('api/v1/workflows/templates-advanced/', list_workflow_templates, name='workflow-templates-advanced'),  # RENAMED to avoid conflict
    path('api/v1/workflows/from-template/', create_workflow_from_template, name='workflow-from-template'),
    # Note: workflow_analytics, schedule_workflow, workflow_collaboration removed - functions not implemented

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

    # Session 745: Stripe/Billing stub endpoints
    path('api/stripe/plans/', stripe_plans, name='stripe-plans'),
    path('api/stripe/payment-methods/', stripe_payment_methods, name='stripe-payment-methods'),
    path('api/stripe/payment-methods/add/', stripe_add_payment_method, name='stripe-add-payment-method'),
    path('api/stripe/payment-methods/<str:payment_method_id>/', stripe_remove_payment_method, name='stripe-remove-payment-method'),
    path('api/stripe/payment-methods/<str:payment_method_id>/default/', stripe_set_default_payment_method, name='stripe-set-default-payment-method'),
    path('api/stripe/invoices/', stripe_invoices, name='stripe-invoices'),
    path('api/stripe/invoices/<str:invoice_id>/', stripe_invoice_detail, name='stripe-invoice-detail'),
    path('api/stripe/upcoming-invoice/', stripe_upcoming_invoice, name='stripe-upcoming-invoice'),
    path('api/stripe/usage/', stripe_usage, name='stripe-usage'),
    path('api/stripe/subscribe/', stripe_subscribe, name='stripe-subscribe'),
    path('api/stripe/cancel-subscription/', stripe_cancel_subscription, name='stripe-cancel-subscription'),
    path('api/stripe/resume-subscription/', stripe_resume_subscription, name='stripe-resume-subscription'),
    path('api/stripe/billing-portal/', stripe_billing_portal, name='stripe-billing-portal'),

    # Session 773: Learning Journey API (real implementation replacing stubs)
    path('api/learning/journeys/', learning_journeys_list, name='learning-journeys-list'),
    path('api/learning/journeys/active/', learning_journeys_active, name='learning-journeys-active'),
    path('api/learning/journeys/start/', learning_journey_start, name='learning-journey-start'),
    path('api/learning/journeys/analytics/', learning_journey_analytics, name='learning-journey-analytics'),
    path('api/learning/journeys/<str:journey_id>/', learning_journey_detail, name='learning-journey-detail'),
    path('api/learning/journeys/<str:journey_id>/pause/', learning_journey_pause, name='learning-journey-pause'),
    path('api/learning/journeys/<str:journey_id>/resume/', learning_journey_resume, name='learning-journey-resume'),
    path('api/learning/journeys/<str:journey_id>/complete/', learning_journey_complete, name='learning-journey-complete'),
    path('api/learning/journeys/<str:journey_id>/abandon/', learning_journey_abandon, name='learning-journey-abandon'),
    path('api/learning/journeys/<str:journey_id>/step/<int:step_number>/start/', learning_step_start, name='learning-step-start'),
    path('api/learning/journeys/<str:journey_id>/step/<int:step_number>/complete/', learning_step_complete, name='learning-step-complete'),
    path('api/learning/journeys/<str:journey_id>/step/<int:step_number>/skip/', learning_step_skip, name='learning-step-skip'),
    path('api/learning/journeys/<str:journey_id>/step/<int:step_number>/content/', learning_step_content, name='learning-step-content'),
    path('api/learning/templates/', learning_templates, name='learning-templates'),
    path('api/learning/templates/<str:template_id>/', learning_template_detail, name='learning-template-detail'),
    path('api/learning/achievements/', learning_achievements, name='learning-achievements'),

    # Session 782: Autonomous System stubs removed - real views in views_autonomous_dashboard.py
    # Real endpoints defined earlier at lines 3140-3153

    # Session 782: Reasoning Engine stubs removed
    # Real reasoning views already exist at lines 2750-2768 using views_autonomous_reasoning.py

    # Session 745: Analytics stub endpoints
    path('api/analytics/overview/', analytics_overview, name='analytics-overview'),
    path('api/analytics/summary/', analytics_summary, name='analytics-summary'),
    path('api/analytics/reports/', analytics_reports_list, name='analytics-reports-list'),
    path('api/analytics/reports/generate/', analytics_reports_generate, name='analytics-reports-generate'),

    # Session 440: Voice Marketplace API
    path('api/voice-marketplace/', marketplace_browse, name='voice-marketplace-browse'),
    path('api/voice-marketplace/my-voices/', my_voices, name='voice-marketplace-my-voices'),
    path('api/voice-marketplace/earnings/', earnings_summary, name='voice-marketplace-earnings'),
    path('api/voice-marketplace/transactions/', transaction_history, name='voice-marketplace-transactions'),
    path('api/voice-marketplace/categories/', marketplace_categories, name='voice-marketplace-categories'),  # Session 745
    path('api/voice-marketplace/stats/', marketplace_stats, name='voice-marketplace-stats'),  # Session 745
    path('api/voice-marketplace/purchases/', marketplace_purchases, name='voice-marketplace-purchases'),  # Session 745
    path('api/voice-marketplace/create/', create_voice_from_elevenlabs, name='voice-marketplace-create'),
    path('api/voice-marketplace/clone/start/', start_clone_request, name='voice-clone-start'),
    path('api/voice-marketplace/clone/upload/', clone_voice_upload, name='voice-clone-upload'),
    path('api/voice-marketplace/clone/<uuid:request_id>/status/', clone_request_status, name='voice-clone-status'),
    path('api/voice-marketplace/<uuid:voice_id>/', voice_detail, name='voice-marketplace-detail'),
    path('api/voice-marketplace/<uuid:voice_id>/publish/', publish_voice, name='voice-marketplace-publish'),
    path('api/voice-marketplace/<uuid:voice_id>/unpublish/', unpublish_voice, name='voice-marketplace-unpublish'),
    path('api/voice-marketplace/<uuid:voice_id>/update/', update_voice, name='voice-marketplace-update'),
    path('api/voice-marketplace/<uuid:voice_id>/generate/', generate_speech, name='voice-marketplace-generate'),
    path('api/voice-marketplace/<uuid:voice_id>/preview/', preview_voice, name='voice-marketplace-preview'),
    path('api/voice-marketplace/<uuid:voice_id>/reviews/', add_review, name='voice-marketplace-add-review'),
]


# Session 1009: Removed voice-checkout endpoints (orphan cleanup)

# =============================================================================
# Session 451: User Upload API
# =============================================================================
from core.views_upload import (
    upload_image, upload_video,
    chunked_upload_init, chunked_upload_chunk, chunked_upload_status,
    get_uploads,
    cloudinary_upload_sign, cloudinary_upload_register,
)

urlpatterns += [
    # Simple uploads (< 50MB)
    path('api/upload/image/', upload_image, name='upload-image'),
    path('api/upload/video/', upload_video, name='upload-video'),

    # Chunked uploads (large files)
    path('api/upload/chunked/init/', chunked_upload_init, name='chunked-upload-init'),
    path('api/upload/chunked/<uuid:upload_id>/chunk/', chunked_upload_chunk, name='chunked-upload-chunk'),
    path('api/upload/chunked/<uuid:upload_id>/status/', chunked_upload_status, name='chunked-upload-status'),

    # Cloudinary direct upload (browser → Cloudinary, no server bottleneck)
    path('api/upload/cloudinary/sign/', cloudinary_upload_sign, name='cloudinary-upload-sign'),
    path('api/upload/video/register/', cloudinary_upload_register, name='cloudinary-upload-register'),

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

# =============================================================================
# Session 470: HITL Validation API (Human-in-the-Loop)
# =============================================================================
from core.views_validation import (
    validation_queue, validation_approve, validation_reject,
    validation_escalate, validation_defer, validation_stats,
    validation_detail, validation_assign, validation_unassign
)

urlpatterns += [
    # Validation Queue
    path('api/validation/queue/', validation_queue, name='validation-queue'),
    path('api/validation/stats/', validation_stats, name='validation-stats'),

    # Validation Actions
    path('api/validation/<uuid:validation_id>/', validation_detail, name='validation-detail'),
    path('api/validation/<uuid:validation_id>/approve/', validation_approve, name='validation-approve'),
    path('api/validation/<uuid:validation_id>/reject/', validation_reject, name='validation-reject'),
    path('api/validation/<uuid:validation_id>/escalate/', validation_escalate, name='validation-escalate'),
    path('api/validation/<uuid:validation_id>/defer/', validation_defer, name='validation-defer'),

    # Assignment
    path('api/validation/<uuid:validation_id>/assign/', validation_assign, name='validation-assign'),
    path('api/validation/<uuid:validation_id>/unassign/', validation_unassign, name='validation-unassign'),
]

# =============================================================================
# MARKET INTELLIGENCE PROVENANCE & COMPLIANCE (Phase 5 - Session 472)
# =============================================================================
from core.views_provenance import (
    # Data Lineage
    get_mi_lineage, get_mi_descendants, verify_mi_integrity, get_mi_provenance_detail,
    # Audit Trail
    get_mi_audit_trail,
    # Compliance
    get_mi_compliance_summary, get_mi_compliance_rules, get_mi_compliance_issues,
    remediate_mi_compliance_issue,
    # Statistics
    get_mi_provenance_stats,
)

urlpatterns += [
    # Data Lineage
    path('api/mi/lineage/<str:entity_type>/<str:entity_id>/', get_mi_lineage, name='mi-lineage'),
    path('api/mi/provenance/<uuid:provenance_id>/', get_mi_provenance_detail, name='mi-provenance-detail'),
    path('api/mi/provenance/<uuid:provenance_id>/descendants/', get_mi_descendants, name='mi-descendants'),
    path('api/mi/provenance/<uuid:provenance_id>/verify/', verify_mi_integrity, name='mi-verify-integrity'),

    # Audit Trail
    path('api/mi/audit/trail/', get_mi_audit_trail, name='mi-audit-trail'),

    # Compliance
    path('api/mi/compliance/summary/', get_mi_compliance_summary, name='mi-compliance-summary'),
    path('api/mi/compliance/rules/', get_mi_compliance_rules, name='mi-compliance-rules'),
    path('api/mi/compliance/issues/', get_mi_compliance_issues, name='mi-compliance-issues'),
    path('api/mi/compliance/<int:check_id>/remediate/', remediate_mi_compliance_issue, name='mi-compliance-remediate'),

    # Statistics
    path('api/mi/provenance/stats/', get_mi_provenance_stats, name='mi-provenance-stats'),
]

# =============================================================================
# MARKET INTELLIGENCE ROI METRICS (Phase 6 - Session 472)
# =============================================================================
from core.views_roi_metrics import (
    # ROI Summary
    roi_summary, roi_aggregate, roi_dashboard, roi_stats,
    # Conversion Events
    record_conversion, conversion_events_list, conversion_path,
    # Funnel
    funnel_metrics,
    # Attribution
    attribution_by_source, attribution_paths, attribution_path_detail,
    # Weekly Briefs
    weekly_briefs_list, generate_weekly_brief, weekly_brief_detail,
)

urlpatterns += [
    # ROI Summary
    path('api/mi/roi/summary/', roi_summary, name='mi-roi-summary'),
    path('api/mi/roi/aggregate/', roi_aggregate, name='mi-roi-aggregate'),
    path('api/mi/roi/dashboard/', roi_dashboard, name='mi-roi-dashboard'),
    path('api/mi/roi/stats/', roi_stats, name='mi-roi-stats'),

    # Conversion Events
    path('api/mi/conversion/record/', record_conversion, name='mi-conversion-record'),
    path('api/mi/conversion/events/', conversion_events_list, name='mi-conversion-events'),
    path('api/mi/conversion/<uuid:event_id>/path/', conversion_path, name='mi-conversion-path'),

    # Funnel
    path('api/mi/funnel/', funnel_metrics, name='mi-funnel'),

    # Attribution
    path('api/mi/attribution/by-source/', attribution_by_source, name='mi-attribution-by-source'),
    path('api/mi/attribution/paths/', attribution_paths, name='mi-attribution-paths'),
    path('api/mi/attribution/<uuid:path_id>/', attribution_path_detail, name='mi-attribution-detail'),

    # Weekly Briefs
    path('api/mi/briefs/', weekly_briefs_list, name='mi-briefs-list'),
    path('api/mi/briefs/generate/', generate_weekly_brief, name='mi-briefs-generate'),
    path('api/mi/briefs/<uuid:brief_id>/', weekly_brief_detail, name='mi-brief-detail'),

    # =========================================================================
    # Session 555: Conversation Artifacts API (Chief of Staff Layer Phase A)
    # =========================================================================
    path('api/artifacts/', lambda r: __import__('core.views_artifacts', fromlist=['list_artifacts']).list_artifacts(r), name='artifacts-list'),
    path('api/artifacts/pending/', lambda r: __import__('core.views_artifacts', fromlist=['pending_artifacts_summary']).pending_artifacts_summary(r), name='artifacts-pending'),
    path('api/artifacts/<uuid:artifact_id>/', lambda r, artifact_id: __import__('core.views_artifacts', fromlist=['get_artifact']).get_artifact(r, artifact_id), name='artifacts-detail'),
    path('api/artifacts/<uuid:artifact_id>/decide/', lambda r, artifact_id: __import__('core.views_artifacts', fromlist=['decide_artifact']).decide_artifact(r, artifact_id), name='artifacts-decide'),
    path('api/conversations/<uuid:conversation_id>/artifacts/', lambda r, conversation_id: __import__('core.views_artifacts', fromlist=['conversation_artifacts']).conversation_artifacts(r, conversation_id), name='conversation-artifacts'),
    path('api/conversations/<uuid:conversation_id>/extract/', lambda r, conversation_id: __import__('core.views_artifacts', fromlist=['extract_conversation']).extract_conversation(r, conversation_id), name='conversation-extract'),

    # =========================================================================
    # Session 555: Artifact Execution API (Chief of Staff Layer Phase B)
    # =========================================================================
    path('api/artifacts/execution-status/', lambda r: __import__('core.views_artifacts', fromlist=['execution_status']).execution_status(r), name='artifacts-execution-status'),
    path('api/artifacts/<uuid:artifact_id>/execute/', lambda r, artifact_id: __import__('core.views_artifacts', fromlist=['execute_artifact']).execute_artifact(r, artifact_id), name='artifacts-execute'),
    path('api/artifacts/<uuid:artifact_id>/executions/', lambda r, artifact_id: __import__('core.views_artifacts', fromlist=['list_executions']).list_executions(r, artifact_id), name='artifacts-executions'),
    path('api/artifacts/executions/<uuid:execution_id>/', lambda r, execution_id: __import__('core.views_artifacts', fromlist=['get_execution']).get_execution(r, execution_id), name='execution-detail'),

    # Session 1070: Decision Gate Classification
    path('api/artifacts/needs-classification/', lambda r: __import__('core.views_artifacts', fromlist=['list_unclassified_artifacts']).list_unclassified_artifacts(r), name='artifacts-needs-classification'),
    path('api/artifacts/<uuid:artifact_id>/classify/', lambda r, artifact_id: __import__('core.views_artifacts', fromlist=['classify_artifact']).classify_artifact(r, artifact_id), name='artifacts-classify'),

    # =========================================================================
    # Session 555: Review Documents API (Chief of Staff Layer Phase D)
    # =========================================================================
    path('api/reviews/', lambda r: __import__('core.views_artifacts', fromlist=['list_review_documents']).list_review_documents(r), name='reviews-list'),
    path('api/reviews/<uuid:review_id>/', lambda r, review_id: __import__('core.views_artifacts', fromlist=['get_review_document']).get_review_document(r, review_id), name='reviews-detail'),
    path('api/reviews/<uuid:review_id>/ask-pro/', lambda r, review_id: __import__('core.views_artifacts', fromlist=['ask_pro_side']).ask_pro_side(r, review_id), name='reviews-ask-pro'),
    path('api/reviews/<uuid:review_id>/ask-con/', lambda r, review_id: __import__('core.views_artifacts', fromlist=['ask_con_side']).ask_con_side(r, review_id), name='reviews-ask-con'),
    path('api/reviews/<uuid:review_id>/decide/', lambda r, review_id: __import__('core.views_artifacts', fromlist=['decide_review']).decide_review(r, review_id), name='reviews-decide'),
    path('api/artifacts/<uuid:artifact_id>/generate-review/', lambda r, artifact_id: __import__('core.views_artifacts', fromlist=['generate_review_for_artifact']).generate_review_for_artifact(r, artifact_id), name='artifacts-generate-review'),

    # =========================================================================
    # Session 556: Auto-Review Generation (Chief of Staff Layer Option C)
    # =========================================================================
    path('api/artifacts/trigger-auto-reviews/', lambda r: __import__('core.views_artifacts', fromlist=['trigger_auto_reviews']).trigger_auto_reviews(r), name='artifacts-trigger-auto-reviews'),
    path('api/artifacts/auto-review-stats/', lambda r: __import__('core.views_artifacts', fromlist=['get_auto_review_stats']).get_auto_review_stats(r), name='artifacts-auto-review-stats'),

    # =========================================================================
    # Session 556: Dream Reviews (Chief of Staff Layer Option D)
    # =========================================================================
    path('api/dreams/<uuid:dream_id>/generate-review/', lambda r, dream_id: __import__('core.views_artifacts', fromlist=['generate_review_for_dream']).generate_review_for_dream(r, dream_id), name='dreams-generate-review'),
    path('api/dreams/reviews/', lambda r: __import__('core.views_artifacts', fromlist=['list_dream_reviews']).list_dream_reviews(r), name='dreams-reviews-list'),

    # =========================================================================
    # Session 476: Autonomous Monitoring Dashboard
    # =========================================================================
    path('monitoring/', lambda r: __import__('core.views_autonomous_monitoring', fromlist=['autonomous_monitoring_dashboard']).autonomous_monitoring_dashboard(r), name='autonomous-monitoring'),
    path('api/monitoring/health/', lambda r: __import__('core.views_autonomous_monitoring', fromlist=['api_unified_health']).api_unified_health(r), name='monitoring-health'),
    path('api/monitoring/content-studio/', lambda r: __import__('core.views_autonomous_monitoring', fromlist=['api_content_studio_status']).api_content_studio_status(r), name='monitoring-content-studio'),
    path('api/monitoring/narrative-drift/', lambda r: __import__('core.views_autonomous_monitoring', fromlist=['api_narrative_drift_status']).api_narrative_drift_status(r), name='monitoring-narrative-drift'),
    path('api/monitoring/market-intelligence/', lambda r: __import__('core.views_autonomous_monitoring', fromlist=['api_market_intelligence_status']).api_market_intelligence_status(r), name='monitoring-market-intelligence'),
    path('api/monitoring/roi/', lambda r: __import__('core.views_autonomous_monitoring', fromlist=['api_roi_metrics']).api_roi_metrics(r), name='monitoring-roi'),
    path('api/monitoring/provenance/', lambda r: __import__('core.views_autonomous_monitoring', fromlist=['api_provenance_chain']).api_provenance_chain(r), name='monitoring-provenance'),
    path('api/monitoring/activity/', lambda r: __import__('core.views_autonomous_monitoring', fromlist=['api_activity_stream']).api_activity_stream(r), name='monitoring-activity'),
    path('api/monitoring/schedules/', lambda r: __import__('core.views_autonomous_monitoring', fromlist=['api_celery_schedules']).api_celery_schedules(r), name='monitoring-schedules'),
    # Session 497: ML Scoring API
    path('api/monitoring/ml-scoring/', lambda r: __import__('core.views_autonomous_monitoring', fromlist=['api_ml_scoring_status']).api_ml_scoring_status(r), name='monitoring-ml-scoring'),
    # Session 511: ML Scoring Training and Explanation APIs
    path('api/monitoring/ml-scoring/train/', lambda r: __import__('core.views_autonomous_monitoring', fromlist=['api_ml_scoring_train']).api_ml_scoring_train(r), name='monitoring-ml-scoring-train'),
    path('api/monitoring/ml-scoring/opportunity/<uuid:opportunity_id>/explanation/', lambda r, opportunity_id: __import__('core.views_autonomous_monitoring', fromlist=['api_ml_scoring_explanation']).api_ml_scoring_explanation(r, opportunity_id), name='monitoring-ml-scoring-explanation'),
]

# =========================================================================
# Session 695-696: SKIN Layer - Workspace Management API
# =========================================================================
from rest_framework.routers import DefaultRouter as WorkspaceRouter
from core.views_workspace_api import (
    ProjectWorkspaceViewSet,
    WorkspaceOperationViewSet,
    workspace_dashboard,
    file_history,
    pending_reviews,
)
from core.views_code_artifacts import CodeArtifactViewSet

# Create dedicated router for workspace API
workspace_router = WorkspaceRouter()
workspace_router.register(r'workspaces', ProjectWorkspaceViewSet, basename='workspace')
workspace_router.register(r'workspace-operations', WorkspaceOperationViewSet, basename='workspace-operation')
workspace_router.register(r'code-artifacts', CodeArtifactViewSet, basename='code-artifact')

from core.views_workspace_templates import (
    list_templates, template_detail, create_from_template,
    workspace_dashboard as ws_biz_dashboard, workspace_config,
    trigger_pipeline, pipeline_status, pipeline_history, pipeline_stage_detail, workspace_packets,
    add_workspace_member,
)
urlpatterns += [
    # Specific Workspace Endpoints (must come BEFORE router to avoid {pk} pattern matching)
    path('api/workspaces/dashboard/', workspace_dashboard, name='workspace-dashboard'),
    path('api/workspaces/<uuid:workspace_id>/file-history/', file_history, name='workspace-file-history'),
    path('api/workspace-operations/pending-reviews/', pending_reviews, name='workspace-pending-reviews'),

    # Workspace Templates & Business-Unit APIs (BEFORE router)
    path('api/workspace-templates/', list_templates, name='workspace-templates-list'),
    path('api/workspace-templates/<slug:slug>/', template_detail, name='workspace-templates-detail'),
    path('api/workspaces/create-from-template/', create_from_template, name='workspace-create-from-template'),
    path('api/workspaces/<uuid:workspace_id>/biz-dashboard/', ws_biz_dashboard, name='workspace-biz-dashboard'),
    path('api/workspaces/<uuid:workspace_id>/config/', workspace_config, name='workspace-config'),
    path('api/workspaces/<uuid:workspace_id>/pipeline/run/', trigger_pipeline, name='workspace-pipeline-run'),
    path('api/workspaces/<uuid:workspace_id>/pipeline/status/', pipeline_status, name='workspace-pipeline-status'),
    path('api/workspaces/<uuid:workspace_id>/pipeline/history/', pipeline_history, name='workspace-pipeline-history'),
    path('api/workspaces/<uuid:workspace_id>/pipeline/<uuid:run_id>/stage/<int:stage_index>/', pipeline_stage_detail, name='workspace-pipeline-stage-detail'),
    path('api/workspaces/<uuid:workspace_id>/packets/', workspace_packets, name='workspace-packets'),
    path('api/workspaces/<uuid:workspace_id>/members/', add_workspace_member, name='workspace-add-member'),

    # Workspace Router URLs (generic patterns last)
    path('api/', include(workspace_router.urls)),
]

# =========================================================================
# Session 861B: WorkspaceTrigger API - Autonomous Work Queue
# =========================================================================
from core.views_workspace_triggers import (
    WorkspaceTriggerViewSet,
    WorkspaceTriggerConfigViewSet,
    autopilot_status,
    trigger_operations_task,  # Session 886: Manual trigger for Operations Tab
    trigger_category_rotation,  # Session 917: Manual trigger for category rotations
)

# Create dedicated router for workspace triggers
trigger_router = WorkspaceRouter()
trigger_router.register(r'workspace-triggers', WorkspaceTriggerViewSet, basename='workspace-trigger')
trigger_router.register(r'workspace-trigger-configs', WorkspaceTriggerConfigViewSet, basename='workspace-trigger-config')

urlpatterns += [
    # Autopilot status endpoint
    path('api/workspace-triggers/autopilot-status/', autopilot_status, name='workspace-autopilot-status'),
    # Session 886: Manual trigger for Operations Tab tasks
    path('api/workspace-triggers/trigger-operations/', trigger_operations_task, name='workspace-trigger-operations'),
    # Session 917: Manual trigger for category rotations (financial, predictions, etc.)
    path('api/workspace-triggers/trigger-category/', trigger_category_rotation, name='workspace-trigger-category'),

    # Trigger Router URLs
    path('api/', include(trigger_router.urls)),
]

# =========================================================================
# Session 686: Human Interface Layer API
# =========================================================================
from core.views_human_interface import get_human_interface_urls
urlpatterns += get_human_interface_urls()

# =========================================================================
# Session 764: Orchestration Layer API (Multi-Agent Workflow Execution)
# =========================================================================
from core.views_orchestration import get_urlpatterns as get_orchestration_urls
urlpatterns += [
    path('api/orchestration/', include((get_orchestration_urls(), 'orchestration'))),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns.append(path('health/', include('backend.auto_endpoints.urls')))  # public health

# =========================================================================
# Session 701: HEART Service API (System Health Monitoring)
# =========================================================================
from core.views_heart import (
    heart_pulse,
    heart_status,
    heart_history,
    heart_component,
    heart_is_alive,
)

urlpatterns += [
    path('api/heart/pulse/', heart_pulse, name='heart-pulse'),
    path('api/heart/status/', heart_status, name='heart-status'),
    path('api/heart/history/', heart_history, name='heart-history'),
    path('api/heart/component/<str:component_name>/', heart_component, name='heart-component'),
    path('api/heart/alive/', heart_is_alive, name='heart-alive'),
]

# =========================================================================
# Session 702: LUNGS Service API (Resource & Capacity Management)
# =========================================================================
from core.views_lungs import (
    lungs_breathe,
    lungs_status,
    lungs_oxygen,
    lungs_budgets,
    lungs_budget_detail,
    lungs_forecast,
    lungs_history,
    lungs_can_breathe,
    lungs_is_breathing,
)

urlpatterns += [
    path('api/lungs/breathe/', lungs_breathe, name='lungs-breathe'),
    path('api/lungs/status/', lungs_status, name='lungs-status'),
    path('api/lungs/oxygen/', lungs_oxygen, name='lungs-oxygen'),
    path('api/lungs/budgets/', lungs_budgets, name='lungs-budgets'),
    path('api/lungs/budgets/<uuid:budget_id>/', lungs_budget_detail, name='lungs-budget-detail'),
    path('api/lungs/forecast/', lungs_forecast, name='lungs-forecast'),
    path('api/lungs/history/', lungs_history, name='lungs-history'),
    path('api/lungs/can-breathe/', lungs_can_breathe, name='lungs-can-breathe'),
    path('api/lungs/alive/', lungs_is_breathing, name='lungs-alive'),
]

# =========================================================================
# Session 703: CIRCULATORY System API (Data Flow Monitoring)
# =========================================================================
from core.views_circulatory import (
    circulate_view,
    status_view as circulatory_status_view,
    routes_list_view,
    route_detail_view,
    bottlenecks_view,
    velocity_view,
    history_view as circulatory_history_view,
    is_flowing_view,
)

urlpatterns += [
    path('api/circulatory/circulate/', circulate_view, name='circulatory-circulate'),
    path('api/circulatory/status/', circulatory_status_view, name='circulatory-status'),
    path('api/circulatory/routes/', routes_list_view, name='circulatory-routes'),
    path('api/circulatory/routes/<uuid:route_id>/', route_detail_view, name='circulatory-route-detail'),
    path('api/circulatory/bottlenecks/', bottlenecks_view, name='circulatory-bottlenecks'),
    path('api/circulatory/velocity/', velocity_view, name='circulatory-velocity'),
    path('api/circulatory/history/', circulatory_history_view, name='circulatory-history'),
    path('api/circulatory/is-flowing/', is_flowing_view, name='circulatory-is-flowing'),
]

# =========================================================================
# Session 704: SPINE System API (Central API Router)
# =========================================================================
from core.views_spine import (
    align_view,
    spine_status_view,
    patterns_list_view,
    pattern_detail_view,
    route_metrics_view,
    history_view as spine_history_view,
    can_route_view,
    is_aligned_view,
    categories_view,
)

urlpatterns += [
    path('api/spine/align/', align_view, name='spine-align'),
    path('api/spine/status/', spine_status_view, name='spine-status'),
    path('api/spine/patterns/', patterns_list_view, name='spine-patterns'),
    path('api/spine/patterns/<uuid:pattern_id>/', pattern_detail_view, name='spine-pattern-detail'),
    path('api/spine/metrics/', route_metrics_view, name='spine-metrics'),
    path('api/spine/history/', spine_history_view, name='spine-history'),
    path('api/spine/can-route/', can_route_view, name='spine-can-route'),
    path('api/spine/is-aligned/', is_aligned_view, name='spine-is-aligned'),
    path('api/spine/categories/', categories_view, name='spine-categories'),
]

# =========================================================================
# Session 705: IMMUNE System API (Security & Threat Detection)
# =========================================================================
from core.views_immune import (
    scan_view as immune_scan_view,
    immune_status_view,
    patterns_list_view as immune_patterns_list_view,
    pattern_detail_view as immune_pattern_detail_view,
    threats_list_view,
    quarantine_list_view,
    quarantine_release_view,
    is_healthy_view as immune_is_healthy_view,
    check_request_view,
    categories_view as immune_categories_view,
)

urlpatterns += [
    path('api/immune/scan/', immune_scan_view, name='immune-scan'),
    path('api/immune/status/', immune_status_view, name='immune-status'),
    path('api/immune/patterns/', immune_patterns_list_view, name='immune-patterns'),
    path('api/immune/patterns/<uuid:pattern_id>/', immune_pattern_detail_view, name='immune-pattern-detail'),
    path('api/immune/threats/', threats_list_view, name='immune-threats'),
    path('api/immune/quarantine/', quarantine_list_view, name='immune-quarantine'),
    path('api/immune/quarantine/<str:entity_type>/<str:entity_value>/', quarantine_release_view, name='immune-quarantine-release'),
    path('api/immune/is-healthy/', immune_is_healthy_view, name='immune-is-healthy'),
    path('api/immune/check-request/', check_request_view, name='immune-check-request'),
    path('api/immune/categories/', immune_categories_view, name='immune-categories'),
]

# =========================================================================
# Session 706: DIGESTIVE System API (Data Ingestion & Processing)
# =========================================================================
from core.views_digestive import (
    digestive_digest_view,
    digestive_status_view,
    digestive_routes_list_view,
    digestive_route_detail_view,
    digestive_bottlenecks_view,
    digestive_metabolism_view,
    digestive_history_view,
    digestive_is_digesting_view,
)

urlpatterns += [
    path('api/digestive/digest/', digestive_digest_view, name='digestive-digest'),
    path('api/digestive/status/', digestive_status_view, name='digestive-status'),
    path('api/digestive/routes/', digestive_routes_list_view, name='digestive-routes'),
    path('api/digestive/routes/<uuid:route_id>/', digestive_route_detail_view, name='digestive-route-detail'),
    path('api/digestive/bottlenecks/', digestive_bottlenecks_view, name='digestive-bottlenecks'),
    path('api/digestive/metabolism/', digestive_metabolism_view, name='digestive-metabolism'),
    path('api/digestive/history/', digestive_history_view, name='digestive-history'),
    path('api/digestive/is-digesting/', digestive_is_digesting_view, name='digestive-is-digesting'),
]

# =========================================================================
# Session 707: MUSCULAR SYSTEM API Routes
# =========================================================================
# Monitors agent work execution and performance
from core.views_muscular import (
    muscular_flex_view,
    muscular_status_view,
    muscular_groups_list_view,
    muscular_group_detail_view,
    muscular_weak_view,
    muscular_overworked_view,
    muscular_history_view,
    muscular_is_strong_view,
)

urlpatterns += [
    path('api/muscular/flex/', muscular_flex_view, name='muscular-flex'),
    path('api/muscular/status/', muscular_status_view, name='muscular-status'),
    path('api/muscular/groups/', muscular_groups_list_view, name='muscular-groups'),
    path('api/muscular/groups/<uuid:group_id>/', muscular_group_detail_view, name='muscular-group-detail'),
    path('api/muscular/weak/', muscular_weak_view, name='muscular-weak'),
    path('api/muscular/overworked/', muscular_overworked_view, name='muscular-overworked'),
    path('api/muscular/history/', muscular_history_view, name='muscular-history'),
    path('api/muscular/is-strong/', muscular_is_strong_view, name='muscular-is-strong'),
]

# =========================================================================
# Session 721: BRAIN SYSTEM - Cognitive Processing & Reasoning
# =========================================================================
# Monitors LLM calls, conversations, agent thinking, and reasoning quality
from core.views_brain import (
    BrainStatusView,
    BrainThinkView,
    BrainVitalsView,
    BrainHistoryView,
    BrainIsThinkingView,
)

urlpatterns += [
    path('api/brain/status/', BrainStatusView.as_view(), name='brain-status'),
    path('api/brain/think/', BrainThinkView.as_view(), name='brain-think'),
    path('api/brain/vitals/', BrainVitalsView.as_view(), name='brain-vitals'),
    path('api/brain/history/', BrainHistoryView.as_view(), name='brain-history'),
    path('api/brain/is-thinking/', BrainIsThinkingView.as_view(), name='brain-is-thinking'),
]

# =========================================================================
# Session 723: SKIN SYSTEM - Project Workspace Health Monitoring
# =========================================================================
# Monitors workspace health, file operations, agent activity, and rollback capability
from core.views_skin import (
    SkinStatusView,
    SkinFeelView,
    SkinVitalsView,
    SkinHistoryView,
    SkinIsHealthyView,
    SkinWorkspacesView,
)

urlpatterns += [
    path('api/skin/status/', SkinStatusView.as_view(), name='skin-status'),
    path('api/skin/feel/', SkinFeelView.as_view(), name='skin-feel'),
    path('api/skin/vitals/', SkinVitalsView.as_view(), name='skin-vitals'),
    path('api/skin/history/', SkinHistoryView.as_view(), name='skin-history'),
    path('api/skin/is-healthy/', SkinIsHealthyView.as_view(), name='skin-is-healthy'),
    path('api/skin/workspaces/', SkinWorkspacesView.as_view(), name='skin-workspaces'),
]

# =========================================================================
# Session 724: NERVOUS SYSTEM - WebSocket Communication Monitoring
# =========================================================================
from core.views_nervous import (
    NervousStatusView,
    NervousFeelView,
    NervousVitalsView,
    NervousHistoryView,
    NervousIsResponsiveView,
    NervousConsumersView,
)

urlpatterns += [
    path('api/nervous/status/', NervousStatusView.as_view(), name='nervous-status'),
    path('api/nervous/feel/', NervousFeelView.as_view(), name='nervous-feel'),
    path('api/nervous/vitals/', NervousVitalsView.as_view(), name='nervous-vitals'),
    path('api/nervous/history/', NervousHistoryView.as_view(), name='nervous-history'),
    path('api/nervous/is-responsive/', NervousIsResponsiveView.as_view(), name='nervous-is-responsive'),
    path('api/nervous/consumers/', NervousConsumersView.as_view(), name='nervous-consumers'),
]

# =========================================================================
# Session 710: BODY UNIFIED - Body Health Dashboard API
# =========================================================================
from core.views_body import (
    body_vitals_view,
    body_alerts_view,
    body_history_view,
    body_system_detail_view,
    body_summary_view,
    # Session 711: Body Coordination
    body_coordination_status_view,
    body_coordination_run_view,
    body_coordination_log_view,
    body_throttle_status_view,
)

urlpatterns += [
    path('api/body/vitals/', body_vitals_view, name='body-vitals'),
    path('api/body/alerts/', body_alerts_view, name='body-alerts'),
    path('api/body/history/', body_history_view, name='body-history'),
    path('api/body/summary/', body_summary_view, name='body-summary'),
    # Session 711: Body Coordination
    path('api/body/coordination/status/', body_coordination_status_view, name='body-coordination-status'),
    path('api/body/coordination/run/', body_coordination_run_view, name='body-coordination-run'),
    path('api/body/coordination/log/', body_coordination_log_view, name='body-coordination-log'),
    path('api/body/throttle/', body_throttle_status_view, name='body-throttle'),
    # System detail must be last (catch-all pattern)
    path('api/body/<str:system_name>/', body_system_detail_view, name='body-system-detail'),
]

# =========================================================================
# Session 744: Celery Health API
# =========================================================================
from core.views_celery_api import (
    CeleryStatusView, CeleryQuickStatusView, CeleryWorkersView,
    CeleryQueuesView, CeleryTasksView, CeleryScheduleView,
    CeleryPingView, CeleryStaleTasks,
    TaskBreakdownView, TaskBreakdownDetailView,  # Session 1048
)

urlpatterns += [
    # api/celery/status/ — REMOVED: duplicate of line 2106 (celery_status function view wins)
    path('api/celery/quick/', CeleryQuickStatusView.as_view(), name='celery-quick'),
    path('api/celery/workers/', CeleryWorkersView.as_view(), name='celery-workers'),
    path('api/celery/queues/', CeleryQueuesView.as_view(), name='celery-queues'),
    path('api/celery/tasks/', CeleryTasksView.as_view(), name='celery-tasks'),
    path('api/celery/schedule/', CeleryScheduleView.as_view(), name='celery-schedule'),
    path('api/celery/ping/', CeleryPingView.as_view(), name='celery-ping'),
    path('api/celery/stale/', CeleryStaleTasks.as_view(), name='celery-stale'),
    # Session 1048: Task volume breakdown
    path('api/celery/breakdown/', TaskBreakdownView.as_view(), name='celery-breakdown'),
    path('api/celery/breakdown/task/', TaskBreakdownDetailView.as_view(), name='celery-breakdown-task'),
]

# =========================================================================
# Session 815: Platform Command Center API
# =========================================================================
from core.views_platform_command import (
    mission_view,
    metrics_view,
    governance_view,
    decision_summary_detail_view,  # Session 845
    create_initiative_from_decision_view,  # Session 852
    emergency_halt_view,
    canon_view,
    canon_promote_view,  # Session 819
    playbooks_view,
    audits_view,
    audit_run_view,  # Session 819
    doc_content_view,
    skin_lock_toggle_view,
    # Session 824: Live Metrics & Self-Execution Control
    live_metrics_view,
    triggers_list_view,
    trigger_toggle_view,
    trigger_run_now_view,
    action_run_spiders_view,
    action_run_remediation_view,
    action_agent_health_check_view,
    action_agent_category_rotation_view,  # Session 884
    action_run_self_audit_view,
    remediation_status_view,
    self_healing_progress_view,  # Session 830
    cleanup_stale_executions_view,  # Session 842
    delete_failed_executions_view,  # Session 895
    celery_debug_view,  # Session 842
)

urlpatterns += [
    path('api/platform/mission/', mission_view, name='platform-mission'),
    path('api/platform/metrics/', metrics_view, name='platform-metrics'),
    path('api/platform/governance/', governance_view, name='platform-governance'),
    # Session 845: Decision summary detail for System Activity modal
    path('api/platform/decision-summary/<uuid:decision_id>/', decision_summary_detail_view, name='platform-decision-summary-detail'),
    # Session 852: Create initiative from decision
    path('api/platform/decision-summary/<uuid:decision_id>/create-initiative/', create_initiative_from_decision_view, name='platform-decision-create-initiative'),
    path('api/platform/emergency-halt/', emergency_halt_view, name='platform-emergency-halt'),
    path('api/platform/canon/', canon_view, name='platform-canon'),
    path('api/platform/canon/promote/', canon_promote_view, name='platform-canon-promote'),  # Session 819
    path('api/platform/playbooks/', playbooks_view, name='platform-playbooks'),
    path('api/platform/audits/', audits_view, name='platform-audits'),
    path('api/platform/audits/run/', audit_run_view, name='platform-audits-run'),  # Session 819
    path('api/platform/doc-content/', doc_content_view, name='platform-doc-content'),  # Session 818
    path('api/platform/skin-lock/', skin_lock_toggle_view, name='platform-skin-lock'),  # Session 818
    # Session 824: Live Metrics & Self-Execution Control
    path('api/platform/live-metrics/', live_metrics_view, name='platform-live-metrics'),
    path('api/platform/triggers/', triggers_list_view, name='platform-triggers-list'),
    path('api/platform/triggers/<str:rule_name>/toggle/', trigger_toggle_view, name='platform-trigger-toggle'),
    path('api/platform/triggers/run-now/', trigger_run_now_view, name='platform-trigger-run-now'),
    path('api/platform/actions/run-spiders/', action_run_spiders_view, name='platform-action-run-spiders'),
    path('api/platform/actions/run-remediation/', action_run_remediation_view, name='platform-action-run-remediation'),
    path('api/platform/actions/agent-health-check/', action_agent_health_check_view, name='platform-action-agent-health'),
    path('api/platform/actions/agent-category-rotation/', action_agent_category_rotation_view, name='platform-action-category-rotation'),  # Session 884
    path('api/platform/actions/run-self-audit/', action_run_self_audit_view, name='platform-action-run-self-audit'),
    path('api/platform/remediation/status/', remediation_status_view, name='platform-remediation-status'),
    # Session 830: Live self-healing progress for UI polling
    path('api/self-healing/progress/', self_healing_progress_view, name='self-healing-progress'),
    # Session 842: Manual cleanup of stale executions (when Celery Beat is not running)
    path('api/platform/cleanup-stale-executions/', cleanup_stale_executions_view, name='platform-cleanup-stale-executions'),
    # Session 895: Delete old failed executions to clean up the UI
    path('api/platform/delete-failed-executions/', delete_failed_executions_view, name='platform-delete-failed-executions'),
    # Session 842: Debug endpoint for Celery status
    path('api/platform/celery-debug/', celery_debug_view, name='platform-celery-debug'),
]

# =========================================================================
# Session 819: Deliverables Marketplace API
# =========================================================================
from core.views_deliverables import (
    list_deliverables,
    get_deliverable,
    save_deliverable,
    unsave_deliverable,
    delete_deliverable,
    clone_deliverable,
    templateize_deliverable,
    export_deliverable,
    get_deliverable_stats,
    get_deliverable_types,
    record_deliverable_event,
    link_deliverable_workspace,
    stage3_dashboard,
)

urlpatterns += [
    path('api/deliverables/', list_deliverables, name='deliverables-list'),
    path('api/deliverables/stats/', get_deliverable_stats, name='deliverables-stats'),
    path('api/deliverables/types/', get_deliverable_types, name='deliverables-types'),
    path('api/deliverables/stage3-dashboard/', stage3_dashboard, name='stage3-dashboard'),
    path('api/deliverables/<uuid:deliverable_id>/', get_deliverable, name='deliverable-detail'),
    path('api/deliverables/<uuid:deliverable_id>/save/', save_deliverable, name='deliverable-save'),
    path('api/deliverables/<uuid:deliverable_id>/unsave/', unsave_deliverable, name='deliverable-unsave'),
    path('api/deliverables/<uuid:deliverable_id>/delete/', delete_deliverable, name='deliverable-delete'),
    path('api/deliverables/<uuid:deliverable_id>/clone/', clone_deliverable, name='deliverable-clone'),
    path('api/deliverables/<uuid:deliverable_id>/templateize/', templateize_deliverable, name='deliverable-templateize'),
    path('api/deliverables/<uuid:deliverable_id>/export/', export_deliverable, name='deliverable-export'),
    path('api/deliverables/<uuid:deliverable_id>/event/', record_deliverable_event, name='deliverable-event'),
    path('api/deliverables/<uuid:deliverable_id>/link-workspace/', link_deliverable_workspace, name='deliverable-link-workspace'),
]

# =========================================================================
# Project Hub API
# =========================================================================
from core.views_project_hub import list_projects, project_hub

urlpatterns += [
    path('api/projects/', list_projects, name='projects-list'),
    path('api/projects/<uuid:workspace_id>/hub/', project_hub, name='project-hub'),
]

# =========================================================================
# Session 819: Audit Tracking System API
# =========================================================================
from core.views_audit_tracking import (
    findings_list,
    finding_detail,
    finding_update_status,
    finding_create_task,
    finding_verify,
    findings_summary,
    audit_reports_list,
    audit_report_detail,
    import_audits,
    open_p0_findings,
)

urlpatterns += [
    # Findings
    path('api/audit-tracking/findings/', findings_list, name='audit-findings-list'),
    path('api/audit-tracking/findings/summary/', findings_summary, name='audit-findings-summary'),
    path('api/audit-tracking/findings/p0/', open_p0_findings, name='audit-p0-findings'),
    path('api/audit-tracking/findings/<uuid:finding_id>/', finding_detail, name='audit-finding-detail'),
    path('api/audit-tracking/findings/<uuid:finding_id>/status/', finding_update_status, name='audit-finding-status'),
    path('api/audit-tracking/findings/<uuid:finding_id>/task/', finding_create_task, name='audit-finding-task'),
    path('api/audit-tracking/findings/<uuid:finding_id>/verify/', finding_verify, name='audit-finding-verify'),
    # Reports
    path('api/audit-tracking/reports/', audit_reports_list, name='audit-reports-list'),
    path('api/audit-tracking/reports/<uuid:report_id>/', audit_report_detail, name='audit-report-detail'),
    # Import
    path('api/audit-tracking/import/', import_audits, name='audit-import'),
]

# =========================================================================
# Session 918: PDF Export API
# =========================================================================
from core.views_pdf_export import (
    download_operation_pdf,
    generate_pdf as pdf_generate_view,
    list_exportable_operations,
)

urlpatterns += [
    path('api/reports/pdf/<uuid:operation_id>/', download_operation_pdf, name='pdf-download'),
    path('api/reports/pdf/generate/', pdf_generate_view, name='pdf-generate'),
    path('api/reports/pdf/list/', list_exportable_operations, name='pdf-list'),
]

# =========================================================================
# Stock Intelligence Dashboard
# =========================================================================
from core.views_stock_intelligence import (
    stock_hub,
    stock_dashboard,
    stock_briefs,
    stock_brief_detail,
    stock_alerts,
    stock_predictions,
    stock_sec_filings,
    stock_market_news,
    ticker_lookup,
    watchlist_list,
    watchlist_add,
    watchlist_remove,
)

urlpatterns += [
    path('api/stocks/hub/', stock_hub, name='stock-hub'),
    path('api/stocks/dashboard/', stock_dashboard, name='stock-dashboard'),
    path('api/stocks/briefs/', stock_briefs, name='stock-briefs'),
    path('api/stocks/briefs/<uuid:brief_id>/', stock_brief_detail, name='stock-brief-detail'),
    path('api/stocks/alerts/', stock_alerts, name='stock-alerts'),
    path('api/stocks/predictions/', stock_predictions, name='stock-predictions'),
    path('api/stocks/sec-filings/', stock_sec_filings, name='stock-sec-filings'),
    path('api/stocks/market-news/', stock_market_news, name='stock-market-news'),
    path('api/stocks/ticker/<str:symbol>/', ticker_lookup, name='stock-ticker-lookup'),
    path('api/stocks/watchlist/', watchlist_list, name='stock-watchlist-list'),
    path('api/stocks/watchlist/add/', watchlist_add, name='stock-watchlist-add'),
    path('api/stocks/watchlist/<str:symbol>/', watchlist_remove, name='stock-watchlist-remove'),
]

# =========================================================================
# Session 1015: Government & Legislation Hub
# =========================================================================
from core.views_government import (
    government_hub, bills_list, bill_detail, bill_search,
    members_list, member_detail, states_list, districts_list,
)

urlpatterns += [
    path('api/government/hub/', government_hub, name='government-hub'),
    path('api/government/bills/', bills_list, name='government-bills'),
    path('api/government/bills/search/', bill_search, name='government-bill-search'),
    path('api/government/bills/<str:bill_uid>/', bill_detail, name='government-bill-detail'),
    path('api/government/members/', members_list, name='government-members'),
    path('api/government/members/<str:bioguide_id>/', member_detail, name='government-member-detail'),
    path('api/government/states/', states_list, name='government-states'),
    path('api/government/states/<str:state>/districts/', districts_list, name='government-districts'),
]

# =========================================================================
# Session 971b: Page-View Telemetry
# =========================================================================
from core.views_telemetry import page_view_api

urlpatterns += [
    path('api/v1/telemetry/page-view/', page_view_api, name='telemetry-page-view'),
]

# =========================================================================
# Session 1071: Platform Awareness + Deploy Verification
# =========================================================================
from core.views_app_manifest import app_manifest, pa_tool_registry
from core.views_deploy_verify import deploy_verify

urlpatterns += [
    path('api/app/manifest/', app_manifest, name='app-manifest'),
    path('api/deploy/verify/', deploy_verify, name='deploy-verify'),
    path('api/v1/pa/tools/', pa_tool_registry, name='pa-tool-registry'),
]

# =========================================================================
# Session 1073: Mobile Push Notifications
# =========================================================================
from core.views_mobile import register_push_token

urlpatterns += [
    path('api/v1/mobile/push/register/', register_push_token, name='mobile-push-register'),
]

# =========================================================================
# Session 1074: Executor Single-Repo MVP
# =========================================================================
from core.views_executor_runs import (
    create_run, list_runs, run_detail, run_logs, run_diff,
    cancel_run, approve_run, approve_step,
)

urlpatterns += [
    path('api/v1/executor/runs/', create_run, name='executor-create-run'),
    path('api/v1/executor/runs/list/', list_runs, name='executor-list-runs'),
    path('api/v1/executor/runs/<uuid:run_id>/', run_detail, name='executor-run-detail'),
    path('api/v1/executor/runs/<uuid:run_id>/logs/', run_logs, name='executor-run-logs'),
    path('api/v1/executor/runs/<uuid:run_id>/diff/', run_diff, name='executor-run-diff'),
    path('api/v1/executor/runs/<uuid:run_id>/cancel/', cancel_run, name='executor-cancel-run'),
    path('api/v1/executor/runs/<uuid:run_id>/approve/', approve_run, name='executor-approve-run'),
    path('api/v1/executor/runs/<uuid:run_id>/approve-step/', approve_step, name='executor-approve-step'),
]

# =========================================================================
# Code Runner (Beta) — admin-only code-agent dispatch
# =========================================================================
from core.views_code_runner import code_run_create, code_run_status, code_run_logs

urlpatterns += [
    path('api/v1/code/run/', code_run_create, name='code-run-create'),
    path('api/v1/code/status/<uuid:run_id>/', code_run_status, name='code-run-status'),
    path('api/v1/code/logs/<uuid:run_id>/', code_run_logs, name='code-run-logs'),
]

# =========================================================================
# VIP Invites (OVL) — magic-link onboarding for demo viewers
# =========================================================================
from core.views_vip_invite import vip_invite_create, vip_invite_exchange, vip_invite_revoke, vip_invite_list

urlpatterns += [
    path('api/v1/vip-invites/', vip_invite_list, name='vip-invite-list'),
    path('api/v1/vip-invites/create/', vip_invite_create, name='vip-invite-create'),
    path('api/v1/vip-invites/exchange/', vip_invite_exchange, name='vip-invite-exchange'),
    path('api/v1/vip-invites/revoke/', vip_invite_revoke, name='vip-invite-revoke'),
]

# =========================================================================
# Remote Code Worker — code job submission and monitoring
# =========================================================================
from core.views_code_jobs import (
    create_code_job, list_code_jobs, code_job_detail,
    code_job_logs, cancel_code_job,
)

urlpatterns += [
    path('api/code-jobs/', create_code_job, name='code-job-create'),
    path('api/code-jobs/list/', list_code_jobs, name='code-job-list'),
    path('api/code-jobs/<uuid:job_id>/', code_job_detail, name='code-job-detail'),
    path('api/code-jobs/<uuid:job_id>/logs/', code_job_logs, name='code-job-logs'),
    path('api/code-jobs/<uuid:job_id>/cancel/', cancel_code_job, name='code-job-cancel'),
]

# =========================================================================
# Newsletter — Operator Edge (public, no auth)
# =========================================================================
from core.views_newsletter import newsletter_subscribe, newsletter_subscriber_count

urlpatterns += [
    path('api/newsletter/subscribe/', newsletter_subscribe, name='newsletter-subscribe'),
    path('api/newsletter/count/', newsletter_subscriber_count, name='newsletter-count'),
]

# =========================================================================
# Development-only endpoints — never exposed in production
# =============================================================================
# Preview System: Workspace Hosted Previews + Magic Links + Feedback
# =============================================================================
from rest_framework.routers import DefaultRouter as PreviewRouter
from core.views_preview_api import (
    WorkspaceProjectViewSet, ProjectRepoViewSet, ProjectEnvVarViewSet,
    PreviewEnvironmentViewSet, FeedbackItemViewSet,
    review_context, review_feedback,
)

_preview_router = PreviewRouter()
_preview_router.register(r'preview/projects', WorkspaceProjectViewSet, basename='preview-project')
_preview_router.register(r'preview/repos', ProjectRepoViewSet, basename='preview-repo')
_preview_router.register(r'preview/env-vars', ProjectEnvVarViewSet, basename='preview-env-var')
_preview_router.register(r'preview/environments', PreviewEnvironmentViewSet, basename='preview-env')
_preview_router.register(r'preview/feedback', FeedbackItemViewSet, basename='preview-feedback')

urlpatterns += [
    path('api/', include(_preview_router.urls)),
    # Public review endpoints (magic link)
    path('api/review/<str:token>/context/', review_context, name='review-context'),
    path('api/review/<str:token>/feedback/', review_feedback, name='review-feedback'),
]

# =============================================================================
# Revenue API (consolidated JSON endpoints for frontend)
# =============================================================================
from core.views_revenue import create_revenue, get_revenue_summary

urlpatterns += [
    path('api/revenue/summary/', get_revenue_summary, name='revenue-api-summary'),
    path('api/revenue/record/', create_revenue, name='revenue-api-record'),
]

# =============================================================================
# Status Overview API
# =============================================================================
from core.views_status_api import status_overview, tool_metrics

urlpatterns += [
    path('api/status/overview/', status_overview, name='status-overview'),
    path('api/status/tool-metrics/', tool_metrics, name='tool-metrics'),
]

# =============================================================================
# BPaaS: Build Packet as a Service
# =============================================================================
from core.views_bpaas_api import (
    bpaas_schema, bpaas_example, create_from_packet, generate_close_pack,
)

urlpatterns += [
    path('api/bpaas/schema/', bpaas_schema, name='bpaas-schema'),
    path('api/bpaas/example/', bpaas_example, name='bpaas-example'),
    path('api/bpaas/create-from-packet/', create_from_packet, name='bpaas-create-from-packet'),
    path('api/bpaas/generate-close-pack/', generate_close_pack, name='bpaas-generate-close-pack'),
]

# =========================================================================
if settings.DEBUG:
    urlpatterns += [
        path('api/assistant/dev/chat/', chat_with_assistant_dev, name='personal-assistant-chat-dev'),
        path('api/assistant/dev/context/', get_assistant_context_dev, name='personal-assistant-context-dev'),
        path('api/assistant/minimal/chat/', chat_minimal_dev, name='personal-assistant-chat-minimal'),
        path('api/assistant/minimal/context/', context_minimal_dev, name='personal-assistant-context-minimal'),
        path('api/ping/', ping_dev, name='ping-dev'),
    ]

# (Workspace Templates URLs moved BEFORE the workspace router — see line ~4031)

# =========================================================================
# Demo Pipeline — "First Win" for onboarding
# =========================================================================
from core.views_demo_pipeline import run_demo_pipeline, demo_pipeline_status
urlpatterns += [
    path('api/demo-pipeline/run/', run_demo_pipeline, name='demo-pipeline-run'),
    path('api/demo-pipeline/status/<str:run_id>/', demo_pipeline_status, name='demo-pipeline-status'),
]

# =========================================================================
# In-App Messaging / Inbox
# =========================================================================
from core.views_inbox import inbox_threads, thread_messages, mark_thread_read, unread_count
urlpatterns += [
    path('api/inbox/threads/', inbox_threads, name='inbox-threads'),
    path('api/inbox/threads/<uuid:thread_id>/messages/', thread_messages, name='inbox-thread-messages'),
    path('api/inbox/threads/<uuid:thread_id>/read/', mark_thread_read, name='inbox-thread-read'),
    path('api/inbox/unread-count/', unread_count, name='inbox-unread-count'),
]

# =========================================================================
# Session 688: React Frontend Catch-All (MUST BE LAST!)
# =========================================================================
# This catches all remaining routes and serves the React SPA.
# React Router handles client-side routing for these paths.
# Excludes: /api/, /admin/, /media/, /static/, /ws/, /health/
urlpatterns.append(
    re_path(r'^(?!api/|admin/|media/|static/|ws/|health/)(?!.*\.\w{1,10}(?:/|$)).*$', react_app, name='react-app')
)
