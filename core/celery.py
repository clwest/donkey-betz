"""
Celery configuration for the core Django application.
This file initializes Celery with Django settings and automated schedules.
"""

import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('unified_donkey_betz_core')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Celery Beat Schedule for Automated Spider Updates and Real Data Collection
app.conf.beat_schedule = {
    'collect-real-opportunities': {
        'task': 'ai_core.tasks.collect_real_opportunities',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'options': {
            'expires': 900,  # Expire after 15 minutes if not executed
        }
    },
    'refresh-ai-opportunities': {
        'task': 'ai_core.tasks.refresh_ai_content_opportunities',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,
        }
    },
    'sync-revenue-metrics': {
        'task': 'ai_core.tasks.sync_revenue_metrics',
        'schedule': crontab(minute=0),  # Every hour
        'options': {
            'expires': 3600,
        }
    },
    'sync-shared-memory': {
        'task': 'intelligence.shared_memory.sync_all_entity_memories',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
        'options': {
            'expires': 600,
        }
    },
    'clean-stale-data': {
        'task': 'ai_core.tasks.clean_stale_data',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        'options': {
            'expires': 7200,
        }
    },
    'warm-up-spiders': {
        'task': 'ai_core.tasks.warm_up_spider_network',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
        'options': {
            'expires': 14400,
        }
    },
    # ML Model Training & Prediction Tasks (Session 24: Updated retraining pipeline)
    'check-retraining-needed': {
        'task': 'ml.check_retraining_needed',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
        'options': {
            'expires': 3600,
        }
    },
    'retrain-all-models-weekly': {
        'task': 'ml.retrain_all_models',
        'schedule': crontab(day_of_week=0, hour=2, minute=0),  # Sunday 2 AM
        'options': {
            'expires': 7200,
        }
    },
    # Session 425: Weekly Opportunity Digest
    'weekly-opportunity-digest': {
        'task': 'core.tasks.generate_weekly_opportunity_digest',
        'schedule': crontab(day_of_week=0, hour=10, minute=0),  # Sunday 10 AM
        'options': {
            'expires': 3600,
        }
    },
    'cleanup-old-model-files': {
        'task': 'ml.cleanup_old_model_files',
        'schedule': crontab(day_of_week=1, hour=1, minute=0),  # Monday 1 AM
        'options': {
            'expires': 3600,
        }
    },
    # Session 616: Clean up old spider item hashes
    'cleanup-spider-item-hashes': {
        'task': 'core.tasks.cleanup_spider_item_hashes',
        'schedule': crontab(hour=3, minute=30),  # Daily at 3:30 AM
        'options': {
            'expires': 3600,
        }
    },
    # Session 687: Human Interface attention items from system events
    'generate-human-attention-items': {
        'task': 'core.tasks.generate_human_attention_items',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'options': {
            'expires': 900,
        }
    },
    # Session 766: Human Attention lifecycle (auto-expire, auto-approve, escalation)
    'process-human-attention-lifecycle': {
        'task': 'core.tasks.process_human_attention_lifecycle',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
        'options': {
            'expires': 600,
        }
    },
    # Session 1031: Surface top dreams as boardroom attention items
    'dream-daily-surfacing': {
        'task': 'core.tasks.surface_top_dreams',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
        'options': {
            'expires': 3600,
        }
    },
    # Session 954: Boardroom ML predictions - enrich pending items with content-aware predictions
    'enrich-boardroom-ml-predictions': {
        'task': 'core.tasks.enrich_boardroom_ml_predictions',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'options': {
            'expires': 900,
        }
    },
    # Session 766: HiveMind synthesis to Orchestration
    'process-hivemind-sessions': {
        'task': 'core.tasks.process_hivemind_sessions',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,
        }
    },
    # Session 766: High-scoring opportunities to Orchestration
    'process-high-scoring-opportunities': {
        'task': 'core.tasks.process_high_scoring_opportunities',
        'schedule': crontab(minute='*/20'),  # Every 20 minutes
        'options': {
            'expires': 1200,
        }
    },
    # Session 766: Spider Action Pipeline - convert spider data to actions
    'process-spider-actions': {
        'task': 'core.tasks.process_spider_actions',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,
        }
    },
    # Session 766: Gate Progression Pipeline - auto-progress gates and start pilots
    'process-gate-progression': {
        'task': 'core.tasks.process_gate_progression',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'options': {
            'expires': 900,
        }
    },
    # Session 766: Content Idea Pipeline - mine Dreams/Conversations for content ideas
    'process-content-ideas': {
        'task': 'core.tasks.process_content_ideas',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
        'options': {
            'expires': 21600,
        }
    },
    # Session 794: Self-Blog Generation - was in settings.py but overwritten by celery.py
    # Generates AI blog posts about the platform using ContentWriterAgent
    # Session 1003: Switched from generate_self_blog_task to deliberation pipeline
    # Old task had no research, no review, no quality gate — 100 drafts sat forever
    'generate-self-blog': {
        'task': 'core.tasks.generate_self_blog_deliberation_task',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours at :00
        'options': {
            'expires': 21600,  # 6 hours
        }
    },
    # Session 1003: Re-evaluate enhanced blogs (EditorAgent reviewed → quality gate)
    'reevaluate-enhanced-blogs': {
        'task': 'core.tasks.reevaluate_enhanced_blogs',
        'schedule': crontab(hour='*/3', minute=30),
        'options': {
            'expires': 10800,
        },
    },
    # Session 1008: Score unscored legacy blogs so they can enter the publish pipeline
    'evaluate-unscored-blogs': {
        'task': 'core.tasks.evaluate_unscored_blogs',
        'schedule': crontab(hour='*/4', minute=15),
        'options': {
            'expires': 14400,
        },
    },
    # Session 1003: Auto-publish approved blogs
    'auto-publish-approved-blogs': {
        'task': 'core.tasks.auto_publish_approved_blogs',
        'schedule': crontab(hour='*/2', minute=0),
        'options': {
            'expires': 7200,
        },
    },
    # Content autonomy loop: gate-to-repair + budget-throttled publishing
    'content-autonomy-loop': {
        'task': 'core.tasks.content_autonomy_loop',
        'schedule': crontab(hour='*/3', minute=15),  # Every 3h at :15
        'options': {
            'expires': 10800,
            'queue': 'content',
        },
    },
    # Session 1033: Auto-enhance blogs stuck in needs_enhancement
    'auto-enhance-blogs': {
        'task': 'core.tasks.auto_enhance_blogs',
        'schedule': crontab(hour='*/4', minute=45),  # Every 4h at :45
        'options': {
            'expires': 14400,
        },
    },
    # Session 1033: Score deliverables with default quality scores
    'score-unscored-deliverables': {
        'task': 'core.tasks.score_unscored_deliverables',
        'schedule': crontab(hour='*/6', minute=15),  # Every 6h at :15
        'options': {
            'expires': 21600,
        },
    },
    # Session 1007: Aggregate tool call stats daily for dashboard queries
    'aggregate-tool-call-stats': {
        'task': 'core.tasks.aggregate_tool_call_stats',
        'schedule': crontab(hour=2, minute=30),  # Daily at 2:30 AM
        'options': {
            'expires': 7200,
            'queue': 'long_running',  # Session 1102: batch aggregation, moved off default
        },
    },
    # Sports Prediction Evaluation & Bet Settlement
    # Updated Session 23: Using new PredictionEvaluator system
    'generate-game-predictions': {
        'task': 'sports.generate_game_predictions',
        'schedule': crontab(minute=15, hour='*/2'),  # Every 2 hours at :15
        'options': {
            'expires': 7200,
        }
    },
    # Session 1088: Line movement + sharp action analysis (runs 30min after predictions)
    'run-market-analysis': {
        'task': 'sports.run_market_analysis',
        'schedule': crontab(minute=45, hour='*/2'),  # Every 2 hours at :45
        'options': {
            'expires': 7200,
        }
    },
    'update-game-scores': {
        'task': 'sports.update_game_scores',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,
        }
    },
    'verify-betting-outcomes': {
        'task': 'sports.verify_betting_outcomes',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,
        }
    },
    'evaluate-completed-predictions': {
        'task': 'sports.evaluate_completed_predictions',
        'schedule': crontab(minute=0),  # Every hour on the hour
        'options': {
            'expires': 3600,  # Expire after 1 hour
        }
    },
    'settle-user-bets': {
        'task': 'sports.settle_user_bets',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'options': {
            'expires': 900,
        }
    },
    'generate-accuracy-report': {
        'task': 'sports.generate_accuracy_report',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
        'options': {
            'expires': 3600,
        }
    },
    'cleanup-old-predictions': {
        'task': 'sports.cleanup_old_predictions',
        'schedule': crontab(day_of_week=1, hour=3, minute=0),  # Monday 3 AM
        'options': {
            'expires': 7200,
        }
    },
    # Agent Learning & Performance Tracking (Session 26: Phase 3)
    'update-agent-performance': {
        'task': 'agents.update_agent_performance',
        'schedule': crontab(hour=4, minute=0),  # Daily at 4 AM
        'options': {
            'expires': 3600,
        }
    },
    # Partnership System - Spider Orchestration (Session 40)
    'fetch-opportunities-hourly': {
        'task': 'intelligence.tasks.fetch_all_opportunities',
        'schedule': crontab(minute=0, hour='*/1'),  # Every hour at :00
        'options': {
            'expires': 3300,  # 55 minutes
        }
    },
    'cleanup-opportunities-daily': {
        'task': 'intelligence.tasks.cleanup_old_opportunities',
        'schedule': crontab(minute=0, hour=3),  # 3 AM daily
        'args': (30,),  # Days before expiring
        'options': {
            'expires': 7200,  # Session 1000C: was missing expires entirely
        }
    },
    # Session 727: Missing Intelligence Tasks (found in deep system audit)
    # Session 799: Changed to process_pending_action_plans which finds and executes pending plans
    'execute-action-plans': {
        'task': 'intelligence.tasks.process_pending_action_plans',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,  # 30 minutes
        }
    },
    'monitor-and-process-opportunities': {
        'task': 'intelligence.tasks.monitor_and_process_opportunities',
        'schedule': crontab(minute='*/20'),  # Every 20 minutes
        'options': {
            'expires': 1200,  # 20 minutes
        }
    },
    'calculate-daily-revenue-metrics': {
        'task': 'intelligence.tasks.calculate_daily_revenue_metrics',
        'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    'update-ml-model-feedback': {
        'task': 'intelligence.tasks.update_ml_model_with_feedback',
        'schedule': crontab(hour=6, minute=30),  # Daily at 6:30 AM
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    'scan-spider-opportunities': {
        'task': 'intelligence.tasks.scan_spider_opportunities',
        'schedule': crontab(minute='*/30'),  # Session 902: Reduced from 15 to 30 min (OOM fix)
        'options': {
            'expires': 1800,  # 30 minutes
        }
    },
    # Session 6: Automated Spider Data Processing (legacy persistence.models.SpiderData)
    'process-spider-data-automatic': {
        'task': 'core.tasks.process_spider_data_automatic',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'options': {
            'expires': 300,  # Expire after 5 minutes if not executed
        }
    },
    # Session 707: Core Spider Data Processing (core.models_unified_system.SpiderData)
    # Processes the unified system SpiderData table monitored by DIGESTIVE system
    'process-core-spider-data': {
        'task': 'core.tasks.process_core_spider_data',
        'schedule': crontab(minute='*/2'),  # Every 2 minutes (faster to catch up backlog)
        'options': {
            'expires': 120,  # Expire after 2 minutes if not executed
        }
    },
    # Session 139: Background 3D Model Status Polling
    'poll-pending-3d-models': {
        'task': 'core.tasks.poll_pending_3d_models',
        'schedule': 60.0,  # Every 60 seconds (was 30s, throttled Session 1056)
        'options': {
            'expires': 55,  # Expire before next run
        }
    },
    # Session 207: Spider Network Execution (Updated Session 293: 15 min interval)
    'run-spider-network': {
        'task': 'core.tasks.run_spider_network',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes (was 30)
        'options': {
            'expires': 900,  # Expire after 15 minutes
        }
    },
    # Session 293: Spider Embedding Backfill
    'backfill-spider-embeddings': {
        'task': 'core.tasks.backfill_spider_embeddings',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
        'kwargs': {'batch_size': 100},  # Session 1066: Reduced from 500 — batch API call, 500 was 3.7GB spike
        'options': {
            'expires': 600,  # Expire after 10 minutes
        }
    },
    # Session 490: Memory Embedding Backfill
    'backfill-memory-embeddings': {
        'task': 'core.tasks.backfill_memory_embeddings',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,  # Expire after 30 minutes
        }
    },
    # Session 729: Conversation Memory Embedding Backfill
    'backfill-conversation-embeddings': {
        'task': 'core.tasks.backfill_conversation_embeddings',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,  # Expire after 30 minutes
        }
    },
    # Session 915: Stage Document Backfill - Generate missing stage documents
    # Session 1006: Increased batch 50→200, frequency */30→*/15 to clear 1208 backlog
    'backfill-stage-documents': {
        'task': 'core.tasks.backfill_stage_documents',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'kwargs': {'stage_num': 1, 'limit': 200},
        'options': {
            'expires': 900,  # Expire after 15 minutes
        }
    },
    # Session 210: Style Evolution Tracking
    'record-style-evolution': {
        'task': 'core.tasks.record_all_user_style_evolution',
        'schedule': crontab(hour=0, minute=30),  # Daily at 12:30 AM
        'options': {
            'expires': 3600,  # Expire after 1 hour
        }
    },
    # Session 223: Opportunity Engine (Phase 1 - Creative Intelligence Empire)
    'score-opportunities-hourly': {
        'task': 'core.tasks.score_opportunities_from_spider_data',
        'schedule': crontab(minute=15),  # Every hour at :15
        'args': (24, 100),  # hours=24, limit=100
        'options': {
            'expires': 3300,  # 55 minutes
        }
    },
    # Session 672: Agent Execution Automation (completes ML Pipeline)
    'execute-opportunity-tasks': {
        'task': 'core.tasks.execute_pending_opportunity_tasks',
        'schedule': crontab(minute='15,45'),  # Every 30 minutes at :15 and :45
        'args': (20,),  # limit=20 tasks per run
        'options': {
            'expires': 1500,  # 25 minutes
        }
    },
    'expire-old-opportunities': {
        'task': 'core.tasks.expire_old_opportunities',
        'schedule': crontab(hour=4, minute=30),  # Daily at 4:30 AM
        'options': {
            'expires': 3600,
        }
    },
    'generate-opportunity-report': {
        'task': 'core.tasks.generate_opportunity_report',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
        'options': {
            'expires': 3600,
        }
    },
    # Session 233: Learning Loop Tasks (Phase 5 - Creative Intelligence Empire)
    'daily-learning-pipeline': {
        'task': 'core.tasks.run_daily_learning_pipeline',
        'schedule': crontab(hour=5, minute=0),  # Daily at 5 AM
        'options': {
            'expires': 7200,  # 2 hours
        }
    },
    'discover-success-patterns': {
        'task': 'core.tasks.discover_success_patterns',
        'schedule': crontab(hour='*/6', minute=30),  # Every 6 hours at :30
        'options': {
            'expires': 21600,  # 6 hours
        }
    },
    'generate-user-insights': {
        'task': 'core.tasks.generate_user_insights',
        'schedule': crontab(hour='*/4', minute=45),  # Every 4 hours at :45
        'options': {
            'expires': 14400,  # 4 hours
        }
    },
    'update-learning-profiles': {
        'task': 'core.tasks.update_learning_profiles',
        'schedule': crontab(hour=6, minute=0),  # Daily at 6 AM
        'options': {
            'expires': 3600,
        }
    },
    # Session 234: Proactive System Tasks (Phase 6 - Creative Intelligence Empire)
    'proactive-system-check': {
        'task': 'core.tasks.run_proactive_system_check',
        'schedule': crontab(hour='*/2', minute=15),  # Every 2 hours at :15
        'options': {
            'expires': 7200,  # 2 hours
        }
    },
    'check-all-alerts': {
        'task': 'core.tasks.check_all_alerts',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,  # 30 minutes
        }
    },
    'generate-smart-suggestions': {
        'task': 'core.tasks.generate_smart_suggestions',
        'schedule': crontab(hour='*/8', minute=0),  # Every 8 hours
        'options': {
            'expires': 28800,  # 8 hours
        }
    },
    'execute-scheduled-automations': {
        'task': 'core.tasks.execute_scheduled_automations',
        'schedule': crontab(minute=0),  # Every hour
        'options': {
            'expires': 3600,
        }
    },
    'send-pending-notifications': {
        'task': 'core.tasks.send_pending_notifications',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'options': {
            'expires': 300,
        }
    },
    'cleanup-old-notifications': {
        'task': 'core.tasks.cleanup_old_notifications',
        'schedule': crontab(hour=3, minute=30),  # Daily at 3:30 AM
        'args': (30,),  # 30 days
        'options': {
            'expires': 7200,
        }
    },
    'expire-old-suggestions': {
        'task': 'core.tasks.expire_old_suggestions',
        'schedule': crontab(hour=4, minute=0),  # Daily at 4 AM
        'args': (14,),  # 14 days
        'options': {
            'expires': 3600,
        }
    },
    # Session 243: Autonomous Agent Learning System
    # Agents learn from each other in the background
    'agent-learning-cycle': {
        'task': 'core.tasks.run_agent_learning_cycle',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes - agents share knowledge
        'options': {
            'expires': 600,
        }
    },
    'agent-think-synthesize': {
        'task': 'core.tasks.agent_think_and_synthesize',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes - agents synthesize insights
        'options': {
            'expires': 1800,
            'queue': 'long_running',  # Session 1102: LLM-heavy, moved off default
        }
    },
    'update-agent-effectiveness': {
        'task': 'core.tasks.update_agent_effectiveness_from_learning',
        'schedule': crontab(hour=5, minute=30),  # Daily at 5:30 AM
        'options': {
            'expires': 3600,
        }
    },
    # Session 767: Learning Pattern Mining
    # Mines AgentLearning records to create discoverable patterns
    'mine-learning-patterns': {
        'task': 'core.tasks.mine_learning_patterns',
        'schedule': crontab(hour='*/12', minute=45),  # Every 12 hours at :45
        'kwargs': {'days_back': 30},
        'options': {
            'expires': 43200,  # 12 hours
        }
    },
    # Session 767: Knowledge Freshness Maintenance
    # Decays freshness scores and deactivates stale knowledge sources
    'maintain-knowledge-freshness': {
        'task': 'core.tasks.maintain_knowledge_freshness',
        'schedule': crontab(hour=4, minute=15),  # Daily at 4:15 AM
        'options': {
            'expires': 7200,  # 2 hours
        }
    },
    # Session 767: Knowledge Promotion to SharedKnowledge
    # Promotes high-confidence knowledge for all agents to access
    'promote-to-shared-knowledge': {
        'task': 'core.tasks.promote_to_shared_knowledge',
        'schedule': crontab(day_of_week='sunday', hour=5, minute=0),  # Weekly on Sunday at 5 AM
        'kwargs': {'min_confidence': 0.7},
        'options': {
            'expires': 86400,  # 24 hours
        }
    },
    'broadcast-learning-status': {
        'task': 'core.tasks.broadcast_learning_status',
        'schedule': 180.0,  # Every 3 minutes (was 60s, throttled Session 1056)
        'options': {
            'expires': 170,
        }
    },
    # Session 244: Daily Learning Embeddings (LEGACY - kept for knowledge transfers)
    # Convert knowledge transfers into searchable vector embeddings
    'embed-daily-agent-learning': {
        'task': 'core.tasks.embed_daily_agent_learning',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        'options': {
            'expires': 7200,  # 2 hours
        }
    },
    # Session 728: Validate knowledge sources (set is_validated=True)
    'validate-knowledge-sources': {
        'task': 'core.tasks.validate_knowledge_sources',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM (after embeddings)
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # Session 417: Comprehensive Agent Activity Embeddings
    # Embed ALL agent activity (dreams, hive minds, knowledge) every 30 minutes
    'embed-agent-activity': {
        'task': 'core.tasks.embed_agent_activity',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,  # 30 minutes
        }
    },
    # Session 244: Agent Conversations (Inter-Agent Chat)
    # Agents discuss topics with each other autonomously
    # Session 429: Reduced from 5 to 30 min to save OpenAI credits (DB already populated)
    'agent-conversation-cycle': {
        'task': 'core.tasks.run_agent_conversation',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes (was 5 min before Session 429)
        'options': {
            'expires': 1800,  # 30 minutes
        }
    },
    # Session 360/361: Multi-Agent Panel Conversations
    # Panel discussions with 3-5 agents for richer insights
    # Session 429: Reduced from 20 to 60 min to save OpenAI credits
    'multi-agent-panel-cycle': {
        'task': 'core.tasks.run_multi_agent_conversation',
        'schedule': crontab(minute=0),  # Every hour at :00 (was every 20 min before Session 429)
        'options': {
            'expires': 3600,  # 60 minutes
        },
        'kwargs': {
            'max_conversations': 1,  # 1 panel per cycle
            'participants_per_conversation': 4,  # 4 agents per panel
            'max_rounds': 3,  # 3 discussion rounds
        }
    },
    # Session 362: Auto-Promote High-Quality Decisions
    # Promotes decisions to canonical policies to close the feedback loop
    'auto-promote-decisions': {
        'task': 'core.tasks.auto_promote_decisions',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes - check for promotions
        'options': {
            'expires': 1800,  # 30 minutes
        },
        'kwargs': {
            'quality_threshold': 0.6,  # Minimum quality score (0-1)
            'max_promotions': 3,  # Max decisions to promote per run
        }
    },
    # Session 589: Governance-Respecting Low-Risk Decision Auto-Promotion
    # Complements quality-score-based promotion with tiered rules
    # Helps manage the pending review backlog
    'auto-promote-low-risk-decisions': {
        'task': 'core.tasks.auto_promote_low_risk_decisions',
        'schedule': crontab(hour='*/6'),  # Every 6 hours - conservative cadence
        'options': {
            'expires': 3600 * 5,  # 5 hours
        },
        'kwargs': {
            'dry_run': False,  # Set True to report without promoting
        }
    },
    # Session 589: Daily Pending Review Metrics Report
    # Tracks agent suggestion review backlog
    'report-pending-review-metrics': {
        'task': 'core.tasks.report_pending_review_metrics',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # Session 373: Auto-Resolve Knowledge Gaps
    # Automatically fills knowledge gaps from spider data and best practices
    'auto-resolve-knowledge-gaps': {
        'task': 'core.tasks.auto_resolve_knowledge_gaps',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
        'options': {
            'expires': 3600 * 5,  # 5 hours
        },
    },
    'broadcast-conversation-status': {
        'task': 'core.tasks.broadcast_conversation_status',
        'schedule': 300.0,  # Every 5 minutes (was 120s, throttled Session 1056)
        'options': {
            'expires': 290,
        }
    },
    # Session 573: System State Aggregator Cache Refresh
    # Keeps PA's system awareness current by aggregating attention items
    'refresh-system-state-cache': {
        'task': 'core.tasks.refresh_system_state_cache',
        'schedule': 120.0,  # Every 2 minutes (was 60s, throttled Session 1056)
        'options': {
            'expires': 110,
        }
    },
    # Session 247: Agent Dreams (Idle Thoughts & Creative Ideas)
    # Agents dream up creative ideas when they're idle
    # Session 688: Reduced from 15 min to 2 hours to save OpenAI credits (~$20/night was too expensive)
    'agent-dream-cycle': {
        'task': 'core.tasks.generate_agent_dreams',
        'schedule': crontab(minute=0, hour='*/2'),  # Every 2 hours (was every 15 min)
        'options': {
            'expires': 7200,  # 2 hours
        }
    },
    'broadcast-dream-journal': {
        'task': 'core.tasks.broadcast_dream_journal',
        'schedule': 600.0,  # Every 10 minutes (was 180s, throttled Session 1056)
        'options': {
            'expires': 590,
        }
    },
    # Session 366: Dream Productization Pipeline
    # Score dreams for actionability/relevance and promote to Boardroom
    'dream-productization-cycle': {
        'task': 'core.tasks.score_and_promote_dreams',
        'schedule': crontab(minute='*/20'),  # Every 20 minutes - score and promote dreams
        'options': {
            'expires': 1200,  # 20 minutes
        }
    },
    # Session 367: Dream Implementation Pipeline
    # Process approved dreams and create implementation tasks
    'dream-implementation-cycle': {
        'task': 'core.tasks.process_approved_dreams',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes - process approved dreams
        'options': {
            'expires': 900,  # 15 minutes
        }
    },
    # Session 368: Agent Execution Engine
    # Execute in-progress implementations and generate real deliverables
    'dream-execution-cycle': {
        'task': 'core.tasks.execute_dream_implementations',
        'schedule': crontab(minute='*/20'),  # Every 20 minutes - execute implementations
        'options': {
            'expires': 1200,  # 20 minutes
        }
    },
    # Session 579: Dream Auto-Triage
    # Auto-promote high-scoring dreams, archive stale low-scoring ones
    # Session 873: Increased frequency - 2,130 dream backlog with oldest 62 days old
    'dream-auto-triage': {
        'task': 'core.tasks.auto_triage_dreams',
        'schedule': crontab(minute=30),  # Every hour at :30 (was every 4 hours)
        'options': {
            'expires': 3600,  # 1 hour
        },
        'kwargs': {
            'max_promote': 200,  # Session 873: 10x increase (was 20)
            'max_archive': 500,  # Session 873: 10x increase (was 50)
            'archive_age_days': 3,  # Session 873: More aggressive (was 7)
            # Session 874: Adjusted thresholds to clear 1,292 limbo dreams (all scored 0.45-0.60)
            'promote_threshold': 0.55,  # Was 0.75 - promotes top half of limbo dreams
            'archive_score_threshold': 0.55,  # Was 0.40 - archives bottom half of limbo dreams
        }
    },
    # Session 654: Gate Auto-Approval
    # Auto-waive low-risk gates to eliminate approval bottleneck
    # Addresses: 64 low-risk gates sitting in 'not_started' status
    'gate-auto-approval': {
        'task': 'core.tasks.auto_approve_low_risk_gates',
        'schedule': crontab(hour='*/2', minute=15),  # Every 2 hours at :15
        'options': {
            'expires': 7200,  # 2 hours
        },
        'kwargs': {
            'max_gates': 20,
            'auto_deploy': True,  # Session 654: Auto-deploy as running pilots
        }
    },
    # Session 252: Agent Mood System
    # Check for expired moods and reset them periodically
    'check-mood-expirations': {
        'task': 'core.tasks.check_mood_expirations',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes - reset expired moods
        'options': {
            'expires': 300,
        }
    },
    'apply-mood-rules': {
        'task': 'core.tasks.apply_mood_trigger_rules',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes - check mood rules
        'options': {
            'expires': 600,
        }
    },
    # Session 253: Agent Rivalries & Alliances
    # Evolve relationships based on activity
    'evolve-agent-relationships': {
        'task': 'core.tasks.evolve_agent_relationships',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes - evolve relationships
        'options': {
            'expires': 1800,
        }
    },
    'update-alliance-strengths': {
        'task': 'core.tasks.update_alliance_strengths',
        'schedule': crontab(minute=0),  # Every hour - update alliance strengths
        'options': {
            'expires': 3600,
        }
    },
    'broadcast-relationship-status': {
        'task': 'core.tasks.broadcast_relationship_status',
        'schedule': 300.0,  # Every 5 minutes (was 120s, throttled Session 1056)
        'options': {
            'expires': 290,
        }
    },
    # Session 254: Agent Evolution System
    # Agents gain XP from activities and level up
    'process-agent-activity-xp': {
        'task': 'core.tasks.process_agent_activity_xp',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes - process activity XP
        'options': {
            'expires': 900,
        }
    },
    'check-level-milestones': {
        'task': 'core.tasks.check_level_milestones',
        'schedule': crontab(minute=0),  # Every hour - check for missed milestones
        'options': {
            'expires': 3600,
        }
    },
    'broadcast-evolution-status': {
        'task': 'core.tasks.broadcast_evolution_status',
        'schedule': 600.0,  # Every 10 minutes (was 300s/5min, throttled Session 1075 — 34s avg runtime)
        'options': {
            'expires': 580,
        }
    },
    # Session 326: Project-Agent Learning Bridge
    # Sync research results to agent knowledge
    'sync-project-knowledge': {
        'task': 'core.tasks.sync_project_knowledge',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes - convert research to knowledge
        'options': {
            'expires': 1800,
        }
    },
    # Session 326: Spider Priority Recalculation
    # Update spider priorities based on active projects
    'recalculate-spider-priorities': {
        'task': 'core.tasks.recalculate_spider_priorities',
        'schedule': crontab(hour='*/6', minute=45),  # Every 6 hours at :45
        'options': {
            'expires': 21600,  # 6 hours
        }
    },
    # Session 354: Project Learning Loop
    # Projects autonomously learn and track their domain over time
    'project-learning-cycle': {
        'task': 'core.tasks.run_project_learning_cycle',
        'schedule': crontab(hour=6, minute=0),  # Daily at 6 AM
        'options': {
            'expires': 7200,  # 2 hours
        }
    },
    # Session 420: Training Data Collection from HuggingFace
    # Collects conversation data from public datasets for agent training
    'collect-training-data-daily': {
        'task': 'core.tasks.collect_training_data',
        'schedule': crontab(hour=1, minute=0),  # Daily at 1 AM
        'options': {
            'expires': 7200,  # 2 hours
        }
    },
    'collect-training-data-weekly-full': {
        'task': 'core.tasks.collect_training_data_full',
        'schedule': crontab(day_of_week=0, hour=2, minute=30),  # Sunday 2:30 AM - full refresh
        'options': {
            'expires': 14400,  # 4 hours
        }
    },
    # Session 437: Discord Automation - Phase 6
    'proactive-opportunity-alerts': {
        'task': 'core.tasks.send_proactive_opportunity_alerts',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,  # 30 minutes
        }
    },
    'personalized-opportunity-alerts': {
        'task': 'core.tasks.send_personalized_opportunity_alerts',
        'schedule': crontab(minute=15),  # Every hour at :15
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # Session 452: Pipeline Learning <-> Collective Intelligence Bridge
    # Syncs content pipeline insights (style/voice performance) to collective intelligence
    'sync-pipeline-to-collective': {
        'task': 'core.tasks.sync_pipeline_insights_to_collective',
        'schedule': crontab(hour='*/6', minute=10),  # Every 6 hours at :10
        'options': {
            'expires': 21600,  # 6 hours
        }
    },
    # =========================================================================
    # Session 460: Autonomous Intelligence Loop
    # The conductor that makes everything work together!
    # =========================================================================
    # Full intelligence cycle - checks SEC, content opportunities, jobs
    'autonomous-intelligence-loop': {
        'task': 'core.tasks.run_autonomous_intelligence_loop',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'options': {
            'expires': 900,  # 15 minutes
        }
    },
    # Daily digest - morning summary of overnight activity
    'daily-intelligence-digest': {
        'task': 'core.tasks.run_daily_intelligence_digest',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # Quick SEC check - catch high-impact filings fast
    'sec-filings-quick-check': {
        'task': 'core.tasks.check_sec_filings_alert',
        'schedule': crontab(minute='*/5', hour='9-16', day_of_week='1-5'),  # Every 5 min during market hours
        'options': {
            'expires': 300,  # 5 minutes
        }
    },
    # Session 461: Stock Audit - comprehensive market monitoring
    'stock-audit-cycle': {
        'task': 'core.tasks.run_stock_audit_cycle',
        'schedule': crontab(minute='*/30', hour='9-16', day_of_week='1-5'),  # Every 30 min during market hours
        'options': {
            'expires': 1800,  # 30 minutes
        }
    },
    # Session 462: Market Intelligence Desk - daily morning brief (Tier 1 Autonomous Situation)
    'market-intelligence-desk': {
        'task': 'core.tasks.run_market_intelligence_desk',
        'schedule': crontab(minute=0, hour=8, day_of_week='1-5'),  # 8 AM daily, Mon-Fri (before market open)
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # Session 558: Kalshi Prediction Markets Collection
    'collect-kalshi-prediction-markets': {
        'task': 'core.tasks.collect_kalshi_prediction_markets',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,  # 30 minutes
        }
    },
    'collect-kalshi-market-intelligence': {
        'task': 'core.tasks.collect_kalshi_market_intelligence',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # Session 558: Sports Odds Collection (The Odds API)
    'collect-sports-odds': {
        'task': 'core.tasks.collect_sports_odds',
        'schedule': crontab(minute='*/60'),  # Every hour (conserve API quota: 20k/month)
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    'collect-sports-odds-intelligence': {
        'task': 'core.tasks.collect_sports_odds_intelligence',
        'schedule': crontab(minute=30, hour='*/6'),  # Every 6 hours at :30
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # Session 558: Daily Betting Digest - morning briefing
    'daily-betting-digest': {
        'task': 'core.tasks.daily_betting_digest',
        'schedule': crontab(hour=8, minute=0),  # 8 AM MST daily
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # Session 558: Market Intelligence Scan - runs market analysts every 2 hours
    'market-intelligence-scan': {
        'task': 'core.tasks.market_intelligence_scan',
        'schedule': crontab(minute=0, hour='*/2'),  # Every 2 hours
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # Session 558: Market Movement Alerts - real-time monitoring every 30 minutes
    'market-movement-alerts': {
        'task': 'core.tasks.market_movement_alerts',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 900,  # 15 minutes
        }
    },
    # Session 464: Learning Loop - Market Intelligence Desk learns from outcomes
    'track-prediction-outcomes': {
        'task': 'learning_loop.track_prediction_outcomes',
        'schedule': crontab(hour=18, minute=0),  # 6 PM daily (after market close)
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    'calculate-agent-accuracy': {
        'task': 'learning_loop.calculate_agent_accuracy',
        'schedule': crontab(day_of_week=0, hour=20, minute=0),  # Sunday 8 PM (weekly)
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # Session 1009: Removed phantom 'track-content-performance-daily' (autonomous_studio.track_performance doesn't exist)
    # Session 1007: Previously removed duplicate 'autonomous-content-studio-loop' (hourly).
    # Session 470: ML Scoring Engine (Market Intelligence Architecture - Phase 1)
    # Weekly model retraining and daily performance evaluation
    'ml-scoring-weekly-retrain': {
        'task': 'core.tasks.train_ml_scoring_model',
        'schedule': crontab(day_of_week=0, hour=3, minute=30),  # Sunday 3:30 AM
        'options': {
            'expires': 7200,  # 2 hours
        }
    },
    'ml-scoring-evaluate-performance': {
        'task': 'core.tasks.evaluate_ml_model_performance',
        'schedule': crontab(hour=6, minute=30),  # Daily at 6:30 AM
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # Session 470: Phase 2 - Scoring Dispatcher Tasks
    # Real-time queue processing (every 30 seconds for low latency)
    'process-realtime-scoring-queue': {
        'task': 'core.tasks.process_realtime_scoring_queue',
        'schedule': 60.0,  # Every 60 seconds (was 30s, throttled Session 1056)
        'options': {
            'expires': 55,  # Expire before next run
        }
    },
    # Batch queue processing (every hour)
    'process-batch-scoring-queue': {
        'task': 'core.tasks.process_batch_scoring_queue',
        'schedule': crontab(minute=0),  # Every hour at :00
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # Cleanup stale scoring requests (every 15 minutes)
    'cleanup-stale-scoring-requests': {
        'task': 'core.tasks.cleanup_stale_scoring_requests',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'options': {
            'expires': 900,  # 15 minutes
        }
    },
    # Session 470: Phase 3 - HITL Validation Tasks
    # Process escalations (every 15 minutes)
    'process-hitl-escalations': {
        'task': 'core.tasks.process_hitl_escalations',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'options': {
            'expires': 900,  # 15 minutes
        }
    },
    # Expire overdue validations (every hour)
    'expire-overdue-validations': {
        'task': 'core.tasks.expire_overdue_validations',
        'schedule': crontab(minute=30),  # Every hour at :30
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # Session 470: Phase 4 - Event Bus Tasks
    # Process scoring event queue (every 30 seconds)
    'process-event-bus-scoring-queue': {
        'task': 'core.tasks.process_event_bus_scoring_queue',
        'schedule': 60.0,  # Every 60 seconds (was 30s, throttled Session 1056)
        'options': {
            'expires': 55,  # Expire before next run
        }
    },
    # Process validation event queue (every 30 seconds)
    'process-event-bus-validation-queue': {
        'task': 'core.tasks.process_event_bus_validation_queue',
        'schedule': 60.0,  # Every 60 seconds (was 30s, throttled Session 1056)
        'options': {
            'expires': 55,  # Expire before next run
        }
    },
    # Process analytics event queue (every minute)
    'process-event-bus-analytics-queue': {
        'task': 'core.tasks.process_event_bus_analytics_queue',
        'schedule': 120.0,  # Every 2 minutes (was 60s, throttled Session 1056)
        'options': {
            'expires': 110,  # Expire before next run
        }
    },
    # Claim stale events (every 5 minutes)
    'claim-stale-events': {
        'task': 'core.tasks.claim_stale_events',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'options': {
            'expires': 300,  # 5 minutes
        }
    },
    # Event bus stats (every 15 minutes)
    'event-bus-stats': {
        'task': 'core.tasks.get_event_bus_stats',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'options': {
            'expires': 900,  # 15 minutes
        }
    },
    # =========================================================================
    # Session 471: Narrative Drift Detector (Tier 1 Autonomous Situation #2)
    # "The system watches the world for story shifts"
    # =========================================================================
    # Session 1007: Removed duplicate 'narrative-drift-detector-cycle' (every 4h).
    # Consolidated into 'run-narrative-drift-cycle' (every 6h, long_running queue).
    # Process spider data for narrative signals
    'narrative-process-spider-data': {
        'task': 'narrative_drift.process_spider_data',
        'schedule': crontab(minute=30),  # Every hour at :30
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # Update narrative lifecycle statuses
    'narrative-update-statuses': {
        'task': 'narrative_drift.update_narrative_statuses',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours at :00
        'options': {
            'expires': 21600,  # 6 hours
        }
    },
    # Session 1007: Removed duplicate 'narrative-daily-digest' (9 AM).
    # Consolidated into 'send-narrative-daily-digest' (8 AM).

    # Session 473: Process narrative shifts for content creation
    # Runs 30 min after narrative status updates to catch new shifts
    'narrative-shifts-to-content': {
        'task': 'narrative_drift.process_shifts_for_content',
        'schedule': crontab(minute=30, hour='*/6'),  # Every 6 hours at :30
        'options': {
            'expires': 21600,  # 6 hours
        }
    },

    # =========================================================================
    # Session 474: Unified Intelligence Pipeline
    # =========================================================================

    # Session 1007: Removed duplicate 'unified-pipeline-complete-cycle' (every 12h).
    # Consolidated into 'run-unified-intelligence-pipeline' (every 6h, long_running queue).
    # Session 1007: Removed duplicate 'unified-pipeline-health-check' (every 2h).
    # Consolidated into same key at line ~1633 (every 30 min).

    # =========================================================================
    # Session 475: ROI Metrics & Intelligence Briefs
    # =========================================================================

    # Daily ROI aggregation - aggregate metrics from yesterday
    'roi-metrics-daily-aggregation': {
        'task': 'roi_metrics.aggregate_daily',
        'schedule': crontab(minute=0, hour=2),  # Daily at 2:00 AM
        'options': {
            'expires': 86400,  # 24 hours
        }
    },

    # Weekly intelligence brief generation - every Monday
    'roi-metrics-weekly-brief': {
        'task': 'roi_metrics.generate_weekly_brief',
        'schedule': crontab(minute=0, hour=7, day_of_week='monday'),  # Monday 7:00 AM
        'options': {
            'expires': 604800,  # 1 week
        }
    },

    # =========================================================================
    # Session 477: Tier 1 Autonomous Situations - Real-Time Alerts
    # Blockchain Security Monitoring + Stock Market Intelligence
    # These send REAL alerts to Discord channels!
    # =========================================================================

    # Session 1007: Removed duplicate 'autonomous-blockchain-security-monitor' (hourly).
    # Consolidated into 'run-blockchain-security-monitor' (every 4h, long_running queue).

    # Session 989: Removed phantom 'autonomous.stock_market_intelligence' schedule.
    # That task name has no registered @shared_task — celery rejected it every hour.
    # Real task is 'core.tasks.run_stock_market_intelligence' scheduled below as
    # 'run-stock-market-intelligence' at 9,12,16 M-F.

    # =========================================================================
    # Session 487: ENABLING ALL 14 DORMANT AUTONOMOUS SITUATIONS
    # These were built but never scheduled - now activating them!
    # =========================================================================

    # Situation #6: Trend-Driven Design System
    # Monitors Dribbble, Behance, Awwwards for design trends
    # Session 539: increased from 6 hours to 2 hours
    'autonomous-design-trends-monitor': {
        'task': 'core.tasks.run_design_trends_monitor',
        'schedule': crontab(minute=15, hour='*/2'),  # Every 2 hours at :15
        'options': {
            'expires': 7200,  # 2 hours
        }
    },

    # Situation #7: Viral Content Predictor
    # Analyzes Reddit, HackerNews, Bluesky for viral potential
    # Session 539: increased from 4 hours to 1 hour - trends move fast
    'autonomous-viral-content-predictor': {
        'task': 'core.tasks.run_viral_content_predictor',
        'schedule': crontab(minute=20),  # Every hour at :20
        'options': {
            'expires': 3600,  # 1 hour
        }
    },

    # Situation #8: Thumbnail A/B Optimizer
    # Tests thumbnail variations for performance
    'autonomous-thumbnail-optimizer': {
        'task': 'core.tasks.run_thumbnail_optimizer',
        'schedule': crontab(minute=30, hour='*/8'),  # Every 8 hours at :30
        'options': {
            'expires': 28800,  # 8 hours
        }
    },

    # Situation #9: Job Match Intelligence
    # Monitors RemoteOK, WeWorkRemotely, Adzuna for job matches
    'autonomous-job-match-intelligence': {
        'task': 'core.tasks.run_job_match_intelligence',
        'schedule': crontab(minute=0, hour='8,12,18'),  # 3x daily at 8 AM, 12 PM, 6 PM
        'options': {
            'expires': 14400,  # 4 hours
        }
    },

    # Situation #10: Freelance Opportunity Scout
    # Scans job boards for freelance/contract opportunities
    'autonomous-freelance-scout': {
        'task': 'core.tasks.run_freelance_opportunity_scout',
        'schedule': crontab(minute=30, hour='9,15,21'),  # 3x daily at 9:30 AM, 3:30 PM, 9:30 PM
        'options': {
            'expires': 21600,  # 6 hours
        }
    },

    # Situation #11: Side Hustle Detector
    # Finds trending micro-opportunities from Reddit, ProductHunt, Kickstarter
    'autonomous-side-hustle-detector': {
        'task': 'core.tasks.run_side_hustle_detector',
        'schedule': crontab(minute=45, hour='*/12'),  # Every 12 hours at :45
        'options': {
            'expires': 43200,  # 12 hours
        }
    },

    # Situation #12: SEC Filing Analyzer
    # Analyzes SEC filings (13F, 10-K, 10-Q, 8-K) for investment signals
    'autonomous-sec-filing-analyzer': {
        'task': 'core.tasks.run_sec_filing_analyzer',
        'schedule': crontab(minute=0, hour='7,12,17', day_of_week='1-5'),  # 3x daily on weekdays
        'options': {
            'expires': 14400,  # 4 hours
        }
    },

    # Situation #13: Crypto Sentiment Monitor
    # Tracks crypto social sentiment from CoinGecko, Reddit, Bluesky
    # Session 539: increased from 3 hours to 1 hour - crypto moves 24/7
    'autonomous-crypto-sentiment-monitor': {
        'task': 'core.tasks.run_crypto_sentiment_monitor',
        'schedule': crontab(minute=25),  # Every hour at :25
        'options': {
            'expires': 3600,  # 1 hour
        }
    },

    # Situation #14: Earnings Surprise Predictor
    # Predicts earnings surprises from financial data
    'autonomous-earnings-predictor': {
        'task': 'core.tasks.run_earnings_predictor',
        'schedule': crontab(minute=30, hour='6', day_of_week='1-5'),  # Daily at 6:30 AM on weekdays
        'options': {
            'expires': 86400,  # 24 hours
        }
    },

    # Situation #15: Tech Stack Evolution Tracker
    # Monitors rising/falling tech from GitHub, HackerNews, Dev.to
    # Session 539: increased from 8 hours to 4 hours
    'autonomous-tech-stack-tracker': {
        'task': 'core.tasks.run_tech_stack_tracker',
        'schedule': crontab(minute=45, hour='*/4'),  # Every 4 hours at :45
        'options': {
            'expires': 14400,  # 4 hours
        }
    },

    # Situation #16: AI Model Release Monitor
    # Tracks new AI models from HuggingFace, GitHub, HackerNews
    # Session 539: increased from 6 hours to 2 hours - AI releases are big news
    'autonomous-ai-model-monitor': {
        'task': 'core.tasks.run_ai_model_monitor',
        'schedule': crontab(minute=30, hour='*/2'),  # Every 2 hours at :30
        'options': {
            'expires': 7200,  # 2 hours
        }
    },

    # Situation #17: Course & Skill Gap Analyzer
    # Analyzes skill gaps and recommends courses
    'autonomous-skill-gap-analyzer': {
        'task': 'core.tasks.run_skill_gap_analyzer',
        'schedule': crontab(minute=0, hour='7', day_of_week='monday'),  # Weekly on Monday at 7 AM
        'options': {
            'expires': 604800,  # 1 week
        }
    },

    # Situation #18: Case Law Monitor
    # Tracks relevant case decisions from CourtListener, FindLaw, Justia
    'autonomous-case-law-monitor': {
        'task': 'core.tasks.run_case_law_monitor',
        'schedule': crontab(minute=30, hour='8'),  # Daily at 8:30 AM
        'options': {
            'expires': 86400,  # 24 hours
        }
    },

    # Situation #19: Regulatory Change Detector
    # Monitors regulatory news from government, legal news sources
    'autonomous-regulatory-detector': {
        'task': 'core.tasks.run_regulatory_change_detector',
        'schedule': crontab(minute=0, hour='9', day_of_week='1-5'),  # Daily at 9 AM on weekdays
        'options': {
            'expires': 86400,  # 24 hours
        }
    },

    # ==========================================================================
    # SESSION 544: AUTONOMOUS REASONING ENGINE - THE THINKING LOOP
    # The system that thinks, decides, and acts on its own
    # ==========================================================================
    'autonomous-thinking-cycle': {
        'task': 'core.tasks.run_autonomous_thinking_cycle',
        'schedule': crontab(minute=0),  # Every hour at :00 (Session 579: changed from 2h to 1h)
        'kwargs': {'cycle_type': 'scheduled', 'lookback_hours': 24},
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # SESSION 581: AUTOMATIC DREAM CLEANUP
    # Archive stale dreams that have been promoted but never decided on
    'cleanup-stale-dreams': {
        'task': 'core.tasks.cleanup_stale_dreams',
        'schedule': crontab(hour=6, minute=0),  # Daily at 6 AM
        'kwargs': {'max_age_hours': 72},  # Archive dreams older than 3 days
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # SESSION 549: HUMAN ACTION NOTIFICATIONS
    # Scan for concerns requiring human policy decisions and create alerts
    'scan-human-action-notifications': {
        'task': 'core.tasks.scan_concerns_for_human_action',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,  # 30 minutes
        }
    },
    # SESSION 555: CONVERSATION ARTIFACT EXTRACTION (Chief of Staff Layer)
    # Extract actionable proposals, risks, experiments from agent conversations
    'batch-extract-artifacts': {
        'task': 'core.tasks.batch_extract_artifacts',
        'schedule': crontab(minute=15),  # Every hour at :15
        'kwargs': {'hours_back': 24},
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # SESSION 555 PHASE B: ARTIFACT EXECUTION PIPELINE
    # Session 1068: Now a fan-out dispatcher (<1s) — safe to process more per batch
    'execute-approved-artifacts': {
        'task': 'core.tasks.execute_approved_artifacts',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'kwargs': {'limit': 25},  # Session 1068: raised from 10 (dispatcher is instant now)
        'options': {
            'expires': 900,  # 15 minutes
        }
    },
    # SESSION 555 PHASE C: WEEKLY SYNTHESIS
    # Generate weekly executive summary every Sunday at 8 AM
    'generate-weekly-synthesis': {
        'task': 'core.tasks.generate_weekly_synthesis',
        'schedule': crontab(day_of_week=0, hour=8, minute=0),  # Sunday 8 AM
        'kwargs': {'days_back': 7},
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # SESSION 556 OPTION C: AUTO-REVIEW GENERATION
    # Auto-generate reviews for pending artifacts
    'generate-pending-reviews': {
        'task': 'core.tasks.generate_pending_reviews',
        'schedule': crontab(minute=30),  # Every hour at :30
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # SESSION 561: LINE MOVEMENT CHARTS - ODDS SNAPSHOT
    # Capture odds snapshots every 20 minutes for line movement tracking
    'snapshot-odds-for-line-movement': {
        'task': 'core.tasks.snapshot_odds_for_line_movement',
        'schedule': crontab(minute='*/20'),  # Every 20 minutes
        'options': {
            'expires': 1200,  # Expire after 20 minutes
        }
    },

    # SESSION 562: ARBITRAGE ALERTS - PUSH NOTIFICATIONS
    # Scan for arbs every 5 minutes and send push notifications to subscribers
    'scan-arbs-and-notify': {
        'task': 'core.tasks.scan_arbs_and_notify',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'options': {
            'expires': 300,  # Expire after 5 minutes
        }
    },

    # SESSION 594: PILOT AUTO-COMPLETION
    # Check running pilots every 4 hours and auto-complete if 24h+ with no issues
    'auto-complete-pilots': {
        'task': 'core.tasks.auto_complete_pilots',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours at :00
        'options': {
            'expires': 14400,  # Expire after 4 hours
        }
    },

    # SESSION 594: SMART PILOT EVALUATION (Layer B)
    # ThinkingAgent evaluates running pilots and suggests outcomes
    'evaluate-pilots-smart': {
        'task': 'core.tasks.evaluate_pilots_with_thinking_agent',
        'schedule': crontab(minute=30, hour='*/6'),  # Every 6 hours at :30
        'options': {
            'expires': 21600,  # Expire after 6 hours
        }
    },

    # SESSION 599: EXPERIMENT AUTO-HALT MONITORING
    # Check running experiments for halt conditions every 10 minutes
    'monitor-experiment-halt-conditions': {
        'task': 'core.tasks.monitor_running_experiments',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
        'options': {
            'expires': 600,  # Expire after 10 minutes
        }
    },

    # SESSION 609: AUTO KPI TRACKING
    # Automatically update experiment KPIs from data sources (spiders, agents, decisions)
    # Creates KPI snapshots for trend visualization
    'update-experiment-kpis': {
        'task': 'core.tasks.update_experiment_kpis',
        'schedule': crontab(minute=0),  # Every hour at :00
        'options': {
            'expires': 3600,  # Expire after 1 hour
        }
    },

    # SESSION 611: KPI ALERTS
    # Check for KPI drops, trend reversals, stalled experiments
    # Sends Discord notifications for critical/warning alerts
    'check-kpi-alerts': {
        'task': 'core.tasks.check_kpi_alerts',
        'schedule': crontab(minute=30),  # Every hour at :30 (after KPI update)
        'options': {
            'expires': 3600,  # Expire after 1 hour
        }
    },

    # SESSION 611: WEEKLY KPI SUMMARY
    # Send weekly summary of KPI trends to Discord
    'weekly-kpi-summary': {
        'task': 'core.tasks.send_weekly_kpi_summary',
        'schedule': crontab(hour=9, minute=0, day_of_week=1),  # Monday 9 AM
        'options': {
            'expires': 86400,  # Expire after 1 day
        }
    },

    # SESSION 618: PILOT EVALUATION AND LEARNING EXTRACTION
    # Evaluate running pilots, complete experiments, extract learnings
    # Feeds learnings to collective intelligence for system-wide learning
    'evaluate-and-complete-pilots': {
        'task': 'core.tasks.evaluate_and_complete_pilots',
        'schedule': crontab(minute=15, hour='*/2'),  # Every 2 hours at :15
        'options': {
            'expires': 7200,  # Expire after 2 hours
        }
    },

    # SESSION 619: AUTOMATIC GATE PROCESSING AND PILOT DEPLOYMENT
    # Process MEDIUM/HIGH risk gates, generate documentation, deploy pilots
    # Runs every hour at :45 to process 20 gates per batch
    'process-gates-and-deploy-pilots': {
        'task': 'core.tasks.process_gates_and_deploy_pilots',
        'schedule': crontab(minute=45),  # Every hour at :45
        'kwargs': {'batch_size': 20},
        'options': {
            'expires': 3600,  # Expire after 1 hour
        }
    },

    # SESSION 690: IMPLEMENTATION PIPELINE - EXECUTE PILOT RECOMMENDATIONS
    # Execute implementations from completed successful pilots
    # Runs every 2 hours at :30 (after pilot evaluation at :15)
    'execute-pilot-implementations': {
        'task': 'core.tasks.execute_pilot_implementations',
        'schedule': crontab(minute=30, hour='*/2'),  # Every 2 hours at :30
        'kwargs': {'batch_size': 10},
        'options': {
            'expires': 7200,  # Expire after 2 hours
        }
    },

    # ==========================================================================
    # SESSION 648: PREVIOUSLY UNSCHEDULED CRITICAL TASKS
    # These tasks were defined but never added to Beat schedule
    # ==========================================================================

    # Spider Data Collection - Main spider network task
    'collect-spider-data': {
        'task': 'core.tasks.collect_spider_data',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours at :00
        'options': {
            'expires': 14400,  # 4 hours
        }
    },

    # Unified Intelligence Pipeline - Aggregates all intelligence sources
    'run-unified-intelligence-pipeline': {
        'task': 'unified_pipeline.run_complete_cycle',  # Session 919: Fixed task name mismatch
        'schedule': crontab(minute=30, hour='*/6'),  # Every 6 hours at :30
        'options': {
            'expires': 21600,  # 6 hours
        }
    },

    # Stock Market Intelligence - Market analysis
    'run-stock-market-intelligence': {
        'task': 'core.tasks.run_stock_market_intelligence',
        'schedule': crontab(minute=0, hour='9,12,16', day_of_week='1-5'),  # Market hours M-F
        'options': {
            'expires': 3600,  # 1 hour
        }
    },

    # Blockchain Security Monitor - On-chain security analysis
    'run-blockchain-security-monitor': {
        'task': 'autonomous.blockchain_security_monitor',  # Session 919: Fixed task name mismatch
        'schedule': crontab(minute=15, hour='*/4'),  # Every 4 hours at :15
        'options': {
            'expires': 14400,  # 4 hours
        }
    },

    # Session 1007: Removed duplicate 'run-autonomous-content-studio' (overwritten by Session 808 entry).

    # Narrative Drift Cycle - Trend and narrative analysis
    'run-narrative-drift-cycle': {
        'task': 'narrative_drift.run_detector_cycle',  # Session 919: Fixed task name mismatch
        'schedule': crontab(minute=45, hour='*/6'),  # Every 6 hours at :45
        'options': {
            'expires': 21600,  # 6 hours
        }
    },

    # Weekly Intelligence Brief - Executive summary
    'generate-weekly-intelligence-brief': {
        'task': 'core.tasks.generate_weekly_intelligence_brief',
        'schedule': crontab(minute=0, hour=9, day_of_week=1),  # Monday 9 AM
        'options': {
            'expires': 86400,  # 24 hours
        }
    },

    # Unified Pipeline Health Check - System health monitoring
    'unified-pipeline-health-check': {
        'task': 'unified_pipeline.health_check',  # Session 919: Fixed task name mismatch
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,  # 30 minutes
        }
    },

    # Track Content Performance - Analytics tracking
    'track-content-performance': {
        'task': 'core.tasks.track_content_performance',
        'schedule': crontab(minute=0, hour=20),  # Daily 8 PM
        'options': {
            'expires': 3600,  # 1 hour
        }
    },

    # Narrative Daily Digest - Daily narrative summary
    'send-narrative-daily-digest': {
        'task': 'narrative_drift.send_daily_digest',  # Session 919: Fixed task name mismatch
        'schedule': crontab(minute=0, hour=8),  # Daily 8 AM
        'options': {
            'expires': 3600,  # 1 hour
        }
    },

    # Dream Backlog Maintenance - Keep dream queue healthy
    'maintain-dream-backlog': {
        'task': 'core.tasks.maintain_dream_backlog',
        'schedule': crontab(minute=0, hour=3),  # Daily 3 AM
        'options': {
            'expires': 3600,  # 1 hour
        }
    },

    # Cleanup Tasks - Database maintenance
    'cleanup-old-resolve-jobs': {
        'task': 'core.tasks.cleanup_old_resolve_jobs',
        'schedule': crontab(minute=0, hour=4),  # Daily 4 AM
        'kwargs': {'days': 30},
        'options': {
            'expires': 3600,  # 1 hour
        }
    },

    'cleanup-expired-uploads': {
        'task': 'core.tasks.cleanup_expired_uploads',
        'schedule': crontab(minute=30, hour=4),  # Daily 4:30 AM
        'options': {
            'expires': 3600,  # 1 hour
        }
    },

    # Daily ROI Metrics Aggregation
    'aggregate-roi-metrics-daily': {
        'task': 'core.tasks.aggregate_roi_metrics_daily',
        'schedule': crontab(minute=0, hour=1),  # Daily 1 AM
        'options': {
            'expires': 3600,  # 1 hour
            'queue': 'long_running',  # Session 1102: batch DB aggregation, moved off default
        }
    },

    # Session 658: AI Decision Promoter (GPT-5-mini)
    # Uses AI to evaluate and auto-promote high-quality decisions to canonical
    'ai-promote-decisions': {
        'task': 'core.tasks.ai_promote_decisions',
        'schedule': crontab(hour='*/4', minute=20),  # Every 4 hours at :20
        'options': {
            'expires': 14400,  # 4 hours
        },
        'kwargs': {
            'batch_size': 50,  # Process 50 decisions per run
        }
    },

    # Session 701: HEART Service - System Health Monitoring
    # The central heartbeat of the AI body - monitors all vital systems
    'heart-service-heartbeat': {
        'task': 'core.tasks.run_heartbeat',
        'schedule': 600.0,  # Every 10 minutes (was 300s/5min, throttled Session 1075 — 81s avg runtime)
        'options': {
            'expires': 580,  # Expire before next run
        }
    },
    # Session 702: LUNGS Service - Resource & Capacity Management
    # The breathing of the AI body - monitors token/cost budgets
    'lungs-service-breathing': {
        'task': 'core.tasks.check_breathing',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'options': {
            'expires': 840,  # 14 minutes
        }
    },
    'lungs-daily-forecast': {
        'task': 'core.tasks.daily_cost_forecast',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8 AM
        'options': {
            'expires': 3600,
        }
    },
    'lungs-daily-reset': {
        'task': 'core.tasks.reset_daily_respiratory_stats',
        'schedule': crontab(hour=0, minute=1),  # Daily at 00:01
        'options': {
            'expires': 3600,
        }
    },
    # Session 703: CIRCULATORY SYSTEM - Data Flow Monitoring
    # The blood flow of the AI body - monitors Redis queues, Celery tasks, WebSocket channels
    'circulatory-system-pulse': {
        'task': 'core.tasks.check_circulation',
        'schedule': 120.0,  # Every 2 minutes (was 30s, throttled Session 1056)
        'options': {
            'expires': 110,  # Expire before next check
        }
    },
    # Session 704: SPINE - Central API Router
    # The backbone of the AI body - monitors API route health and patterns
    'spine-alignment-check': {
        'task': 'core.tasks.check_spine_alignment',
        'schedule': 300.0,  # Every 5 minutes (was 60s, throttled Session 1056)
        'options': {
            'expires': 290,  # Expire before next check
        }
    },
    # Session 705: IMMUNE SYSTEM - Security & Threat Detection
    # The defense layer of the AI body - detects and responds to threats
    'immune-system-scan': {
        'task': 'core.tasks.immune_scan',
        'schedule': 180.0,  # Every 3 minutes (was 45s, throttled Session 1056)
        'options': {
            'expires': 170,  # Expire before next scan
        }
    },
    # Session 706: DIGESTIVE SYSTEM - Data Ingestion & Processing
    # Monitors how raw spider data is transformed into actionable intelligence
    'digestive-system-check': {
        'task': 'core.tasks.check_digestion',
        'schedule': 300.0,  # Every 5 minutes (was 60s, throttled Session 1056)
        'options': {
            'expires': 290,  # Expire before next check
        }
    },
    # Session 707: MUSCULAR SYSTEM - Agent Work Execution
    # Monitors agent execution performance, strength, fatigue, and strain
    'muscular-system-check': {
        'task': 'core.tasks.check_muscular',
        'schedule': 300.0,  # Every 5 minutes (was 90s, throttled Session 1056)
        'options': {
            'expires': 290,  # Expire before next check
        }
    },
    # Session 721: BRAIN SYSTEM - Cognitive Processing & Reasoning
    # Monitors LLM calls, conversations, agent thinking, and reasoning quality
    'brain-system-check': {
        'task': 'core.tasks.check_brain',
        'schedule': 300.0,  # Every 5 minutes (was 60s, throttled Session 1056)
        'options': {
            'expires': 290,  # Expire before next check
        }
    },
    # Session 723: SKIN SYSTEM - Project Workspace Health
    # Monitors workspace health, file operations, agent activity, and rollback
    'skin-system-check': {
        'task': 'core.tasks.check_skin',
        'schedule': 300.0,  # Every 5 minutes (was 90s, throttled Session 1056)
        'options': {
            'expires': 290,  # Expire before next check
        }
    },
    # Session 724: NERVOUS SYSTEM - WebSocket Communication Health
    # Monitors WebSocket connections, message throughput, Redis channel layer
    'nervous-system-check': {
        'task': 'core.tasks.check_nervous',
        'schedule': 180.0,  # Every 3 minutes (was 60s, throttled Session 1056)
        'options': {
            'expires': 170,  # Expire before next check
        }
    },
    # Session 711: BODY COORDINATOR - Autonomic Nervous System
    # Coordinates responses across all body systems
    'body-coordinator-check': {
        'task': 'core.tasks.coordinate_body',
        'schedule': 60.0,  # Every 60 seconds
        'options': {
            'expires': 55,  # Expire before next check
        }
    },
    # ==========================================================================
    # Session 737: Agent Activation Tasks
    # ==========================================================================
    # These tasks exercise dormant agents to keep them active and functional
    'run-market-monitoring-agents': {
        'task': 'core.tasks.run_market_monitoring_agents',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours
        'options': {
            'expires': 14400,  # 4 hours
        }
    },
    'run-blockchain-monitoring-agents': {
        'task': 'core.tasks.run_blockchain_monitoring_agents',
        'schedule': crontab(minute=30, hour='*/6'),  # Every 6 hours at :30
        'options': {
            'expires': 21600,  # 6 hours
        }
    },
    # Session 1007: Removed duplicate 'run-business-strategy-agents' (overwritten by Session 807 entry).
    # =========================================================================
    # Session 787: Comprehensive Agent Scheduling
    # All 73 agents run autonomously on appropriate schedules
    # =========================================================================
    'run-content-creation-agents': {
        'task': 'core.tasks.run_content_creation_agents',
        'schedule': crontab(minute=10, hour='*/3'),  # Every 3 hours at :10
        'options': {
            'expires': 10800,  # 3 hours
        }
    },
    'run-strategy-marketing-agents': {
        'task': 'core.tasks.run_strategy_marketing_agents',
        'schedule': crontab(minute=20, hour='*/4'),  # Every 4 hours at :20
        'options': {
            'expires': 14400,  # 4 hours
        }
    },
    # Session 1007: Removed duplicate 'run-research-analysis-agents' (overwritten by Session 807 entry).
    'run-stock-financial-agents': {
        'task': 'core.tasks.run_stock_financial_agents',
        'schedule': crontab(minute=40, hour='*/3'),  # Every 3 hours at :40
        'options': {
            'expires': 10800,  # 3 hours
        }
    },
    'run-prediction-market-agents': {
        'task': 'core.tasks.run_prediction_market_agents',
        'schedule': crontab(minute=50, hour='*/2'),  # Every 2 hours at :50
        'options': {
            'expires': 7200,  # 2 hours
        }
    },
    'run-narrative-culture-agents': {
        'task': 'core.tasks.run_narrative_culture_agents',
        'schedule': crontab(minute=15, hour='*/6'),  # Every 6 hours at :15
        'options': {
            'expires': 21600,  # 6 hours
        }
    },
    'run-development-tech-agents': {
        'task': 'core.tasks.run_development_tech_agents',
        'schedule': crontab(minute=25, hour='*/4'),  # Every 4 hours at :25
        'options': {
            'expires': 14400,  # 4 hours
        }
    },
    'run-executive-leadership-agents': {
        'task': 'core.tasks.run_executive_leadership_agents',
        'schedule': crontab(minute=35, hour='*/6'),  # Every 6 hours at :35
        'options': {
            'expires': 21600,  # 6 hours
        }
    },
    'run-podcast-debate-agents': {
        'task': 'core.tasks.run_podcast_debate_agents',
        'schedule': crontab(minute=45, hour='*/8'),  # Every 8 hours at :45
        'options': {
            'expires': 28800,  # 8 hours
        }
    },
    # Session 1007: Removed duplicate 'run-content-studio-agents' (overwritten by Session 807 entry).
    # Session 1007: Removed duplicate 'run-campaign-series-agents' (overwritten by Session 807 entry).
    'run-system-orchestration-agents': {
        'task': 'core.tasks.run_system_orchestration_agents',
        # Session 1035: Throttled 2h → 4h to reduce cost (~$4.91/day gap to $6 target)
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours at :00
        'options': {
            'expires': 14400,  # 4 hours
        }
    },
    'run-quality-audit-agents': {
        'task': 'core.tasks.run_quality_audit_agents',
        'schedule': crontab(minute=15, hour='*/4'),  # Every 4 hours at :15
        'options': {
            'expires': 14400,  # 4 hours
        }
    },
    'run-specialty-agents': {
        'task': 'core.tasks.run_specialty_agents',
        'schedule': crontab(minute=30, hour='*/8'),  # Every 8 hours at :30
        'options': {
            'expires': 28800,  # 8 hours
        }
    },
    # =========================================================================
    # End Session 787 Agent Scheduling
    # =========================================================================
    'exercise-all-dormant-agents': {
        'task': 'core.tasks.exercise_all_dormant_agents',
        'schedule': crontab(day_of_week=0, hour=6, minute=0),  # Weekly on Sunday at 6 AM
        'options': {
            'expires': 21600,  # 6 hours
        }
    },
    # Session 743: Content Diversity Orchestrator
    'check-content-diversity': {
        'task': 'core.tasks.check_content_diversity',
        'schedule': crontab(hour='6,18', minute=0),  # Twice daily at 6 AM and 6 PM
        'options': {
            'expires': 7200,  # 2 hours
        }
    },
    # Session 744: Celery Health Monitoring (Phase 1 Foundation)
    'check-celery-health': {
        'task': 'core.tasks.check_celery_health',
        'schedule': 600.0,  # Every 10 minutes (was 300s/5min, throttled Session 1075 — 81s avg runtime)
        'options': {
            'expires': 580,  # Expire before next run
        }
    },
    # ==========================================================================
    # Session 764: Orchestration Layer - Multi-Agent Workflow Execution
    # ==========================================================================
    # Check for timed-out orchestration executions
    'check-orchestration-timeouts': {
        'task': 'core.tasks.check_orchestration_timeouts',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'options': {
            'expires': 300,  # 5 minutes
        }
    },
    # Check for auto-approvals on expired approval gates
    'check-orchestration-auto-approvals': {
        'task': 'core.tasks.check_orchestration_auto_approvals',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'options': {
            'expires': 300,  # 5 minutes
        }
    },
    # Session 766: Execute approved dreams through orchestration layer
    'execute-approved-dreams-via-orchestration': {
        'task': 'core.tasks.execute_approved_dreams_via_orchestration',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
        'options': {
            'expires': 600,  # 10 minutes
        }
    },
    # ==========================================================================
    # Session 776: SKIN Layer Agent Integration - Agents Write to Workspace
    # ==========================================================================
    # System status report every 6 hours
    'agent-workspace-status-report': {
        'task': 'core.tasks.agent_workspace_status_report',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
        'options': {
            'expires': 3600,
        }
    },
    # Daily summary at midnight
    'agent-daily-summary': {
        'task': 'core.tasks.agent_daily_summary',
        'schedule': crontab(minute=0, hour=0),  # Daily at midnight
        'options': {
            'expires': 3600,
        }
    },
    # Research task every 8 hours (3x daily)
    'agent-research-to-workspace': {
        'task': 'core.tasks.agent_research_to_workspace',
        'schedule': crontab(minute=30, hour='*/8'),  # Every 8 hours at :30
        'options': {
            'expires': 3600,
        }
    },
    # Content generation every 12 hours (2x daily)
    'agent-content-to-workspace': {
        'task': 'core.tasks.agent_content_to_workspace',
        'schedule': crontab(minute=0, hour='6,18'),  # 6 AM and 6 PM
        'options': {
            'expires': 3600,
        }
    },
    # ==========================================================================
    # Session 777: UNIVERSAL AGENT WORKSPACE INTEGRATION
    # Category rotation schedules - each category runs at different times
    # All 74 agents covered across 14 categories
    # ==========================================================================
    # Research agents - Every 6 hours at :00
    'agent-category-research': {
        'task': 'core.tasks.agent_category_rotation',
        'schedule': crontab(minute=0, hour='*/6'),
        'args': ('research',),
        'options': {'expires': 7200}
    },
    # Strategy agents - Daily at 7 AM
    'agent-category-strategy': {
        'task': 'core.tasks.agent_category_rotation',
        'schedule': crontab(minute=0, hour=7),
        'args': ('strategy',),
        'options': {'expires': 7200}
    },
    # Content agents - Every 8 hours at :15
    'agent-category-content': {
        'task': 'core.tasks.agent_category_rotation',
        'schedule': crontab(minute=15, hour='*/8'),
        'args': ('content',),
        'options': {'expires': 7200}
    },
    # Financial agents - Every 4 hours (market hours focus)
    'agent-category-financial': {
        'task': 'core.tasks.agent_category_rotation',
        'schedule': crontab(minute=30, hour='*/4'),
        'args': ('financial',),
        'options': {'expires': 7200}
    },
    # Predictions agents - Every 6 hours at :45
    'agent-category-predictions': {
        'task': 'core.tasks.agent_category_rotation',
        'schedule': crontab(minute=45, hour='*/6'),
        'args': ('predictions',),
        'options': {'expires': 7200}
    },
    # Blockchain agents - Every 4 hours at :20
    'agent-category-blockchain': {
        'task': 'core.tasks.agent_category_rotation',
        'schedule': crontab(minute=20, hour='*/4'),
        'args': ('blockchain',),
        'options': {'expires': 7200}
    },
    # Narrative agents - Every 8 hours at :40
    'agent-category-narrative': {
        'task': 'core.tasks.agent_category_rotation',
        'schedule': crontab(minute=40, hour='*/8'),
        'args': ('narrative',),
        'options': {'expires': 7200}
    },
    # Podcast agents - Every 12 hours at :00
    'agent-category-podcast': {
        'task': 'core.tasks.agent_category_rotation',
        'schedule': crontab(minute=0, hour='5,17'),
        'args': ('podcast',),
        'options': {'expires': 7200}
    },
    # Development agents - Every 8 hours at :50
    'agent-category-development': {
        'task': 'core.tasks.agent_category_rotation',
        'schedule': crontab(minute=50, hour='*/8'),
        'args': ('development',),
        'options': {'expires': 7200}
    },
    # Media agents - Every 12 hours at :10
    'agent-category-media': {
        'task': 'core.tasks.agent_category_rotation',
        'schedule': crontab(minute=10, hour='8,20'),
        'args': ('media',),
        'options': {'expires': 7200}
    },
    # Executive agents - Daily at 8 AM
    'agent-category-executive': {
        'task': 'core.tasks.agent_category_rotation',
        'schedule': crontab(minute=0, hour=8),
        'args': ('executive',),
        'options': {'expires': 7200}
    },
    # Coordination agents - Every 6 hours at :25
    'agent-category-coordination': {
        'task': 'core.tasks.agent_category_rotation',
        'schedule': crontab(minute=25, hour='*/6'),
        'args': ('coordination',),
        'options': {'expires': 7200}
    },
    # System agents - Every 4 hours at :05
    'agent-category-system': {
        'task': 'core.tasks.agent_category_rotation',
        'schedule': crontab(minute=5, hour='*/4'),
        'args': ('system',),
        'options': {'expires': 7200}
    },
    # Security agents - Every 6 hours at :35
    'agent-category-security': {
        'task': 'core.tasks.agent_category_rotation',
        'schedule': crontab(minute=35, hour='*/6'),
        'args': ('security',),
        'options': {'expires': 7200}
    },
    # Assistant agents - Daily at 9 AM
    'agent-category-assistant': {
        'task': 'core.tasks.agent_category_rotation',
        'schedule': crontab(minute=0, hour=9),
        'args': ('assistant',),
        'options': {'expires': 7200}
    },
    # Full rotation - Weekly on Sunday at 3 AM (all 74 agents)
    'agent-full-rotation-weekly': {
        'task': 'core.tasks.full_agent_rotation',
        'schedule': crontab(minute=0, hour=3, day_of_week=0),  # Sunday 3 AM
        'options': {'expires': 14400}
    },
    # Session 807: Agent exercise schedules for weak muscles
    # Research agents - Session 1035: Throttled 2h → 4h to reduce cost
    'run-research-analysis-agents': {
        'task': 'core.tasks.run_research_analysis_agents',
        'schedule': crontab(minute=15, hour='*/4'),  # Every 4 hours at :15
        'options': {'expires': 14400}
    },
    # Content studio agents - Every 4 hours (TopicMinerAgent, ContrarianAgent)
    'run-content-studio-agents': {
        'task': 'core.tasks.run_content_studio_agents',
        'schedule': crontab(minute=30, hour='*/4'),  # Every 4 hours at :30
        'options': {'expires': 14400}
    },
    # Campaign/series agents - Every 6 hours (AISeriesWorkflowAgent, CampaignOrchestratorAgent)
    'run-campaign-series-agents': {
        'task': 'core.tasks.run_campaign_series_agents',
        'schedule': crontab(minute=45, hour='*/6'),  # Every 6 hours at :45
        'options': {'expires': 21600}
    },
    # Business strategy agents - Every 8 hours (CompetitorAnalysisAgent, etc.)
    'run-business-strategy-agents': {
        'task': 'core.tasks.run_business_strategy_agents',
        'schedule': crontab(minute=0, hour='*/8'),  # Every 8 hours at :00
        'options': {'expires': 28800}
    },

    # ==================== SESSION 808: ORPHANED TASKS FIX ====================
    # Workflow scheduling - Every 5 minutes to sync schedules with Celery Beat
    'sync-workflow-schedules': {
        'task': 'core.tasks.sync_workflow_schedules',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'options': {'expires': 300}
    },
    # Workflow check fallback - Every minute to catch missed scheduled workflows
    'check-workflow-schedules': {
        'task': 'core.tasks.check_workflow_schedules',
        'schedule': crontab(minute='*'),  # Every minute
        'options': {'expires': 60}
    },
    # Autonomy engine - Every 30 minutes to run autonomous actions
    'run-autonomy-cycle': {
        'task': 'core.tasks.run_autonomy_cycle',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {'expires': 1800}
    },
    # Session 1009: Removed phantom 'run-autonomous-content-studio' (autonomous_studio.run_main_loop doesn't exist)

    # ==================== SESSION 820: AUTONOMOUS REMEDIATION SYSTEM ====================
    # Self-Healing Orchestration - system automatically discovers audits, assigns findings
    # to agents, executes fixes, and verifies results. No human intervention required.

    # Session 822-823: Remediation pipeline
    # Session 1026: Discovery + assignment KEPT (findings are real and valuable).
    # Execution DISABLED — CodeGeneratorAgent runs in empty sandbox, can't write files,
    # cycles $9/day re-analyzing the same 58 tasks. Findings now surfaced via
    # `python manage.py show_remediation_findings` for Claude Code sessions to act on.
    'discover-and-import-audits': {
        'task': 'core.tasks.discover_and_import_audits',
        'schedule': crontab(hour=0, minute=0),
        'options': {'expires': 3600}
    },
    'assign-open-findings-to-agents': {
        'task': 'core.tasks.assign_open_findings_to_agents',
        'schedule': crontab(minute=0, hour='*/2'),
        'options': {'expires': 7200}
    },
    # Session 1026: DISABLED — execution burns $9/day in empty sandbox
    # 'execute-remediation-tasks': {
    #     'task': 'core.tasks.execute_remediation_tasks',
    #     'schedule': crontab(minute=30, hour='*/4'),
    #     'options': {'expires': 14400}
    # },
    # 'verify-completed-fixes': {
    #     'task': 'core.tasks.verify_completed_fixes',
    #     'schedule': crontab(minute=0, hour='*/6'),
    #     'options': {'expires': 21600}
    # },
    # 'run-autonomous-remediation-cycle': {
    #     'task': 'core.tasks.run_autonomous_remediation_cycle',
    #     'schedule': crontab(hour=2, minute=0),
    #     'options': {'expires': 7200}
    # },

    # ==================== SESSION 823: PERIODIC SYSTEM SELF-AUDIT ====================
    # Generate comprehensive system audits using TechnicalDocumentAgent
    # Audits are saved to docs/audits/ for discovery by remediation system
    'run-system-self-audit': {
        'task': 'core.tasks.run_system_self_audit',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Sundays at 3 AM
        'options': {'expires': 7200}
    },

    # ==================== SESSION 823: METRICS ACTION TRIGGERS ====================
    # Self-execution engine: evaluates live metrics and triggers corrective actions
    # Examples: no spider data → run spiders, high open findings → run remediation
    'run-metrics-action-check': {
        'task': 'core.tasks.run_metrics_action_check',
        'schedule': crontab(minute=0),  # Every hour at :00
        'options': {'expires': 3600}
    },

    # ==================== SESSION 856: DIAGNOSTIC PIPELINE ====================
    # Transform audit output from "stuff failed again" to "here's the root cause and fix"
    # Phase 1: Detect → Phase 2: Diagnose → Phase 3: Prescribe

    # Run diagnostic pipeline to diagnose signatures with undiagnosed detections
    # Requires 3+ samples per signature before diagnosis (guardrail against noise)
    'run-diagnostic-pipeline': {
        'task': 'core.tasks.run_diagnostic_pipeline_task',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'options': {
            'expires': 900,  # 15 minutes
        }
    },

    # Archive old resolved failure signatures (cleanup)
    'cleanup-resolved-signatures': {
        'task': 'core.tasks.cleanup_resolved_signatures',
        'schedule': crontab(hour=4, minute=45),  # Daily at 4:45 AM
        'args': (30,),  # Keep for 30 days before archiving
        'options': {
            'expires': 7200,  # 2 hours
        }
    },

    # ==================== SESSION 865: CONTENT ENHANCEMENT ====================
    # Auto-enhance blogs marked as 'needs_enhancement' using EditorAgent
    # Improves structure, hooks, headers, engagement, and conclusions

    # Session 1009: Removed phantom 'enhance-content' (core.tasks.enhance_all_blogs_needing_enhancement doesn't exist)

    # ==================== SESSION 866: INITIATIVE PIPELINE AUTOMATION ====================
    # Advance initiatives through their 5-stage pipeline automatically
    # Stages: Research Brief → Prototype Plan → Evaluation → Tech Design → Pilot Execution
    # Generates stage documents using TechnicalDocumentAgent
    # Session 926: Increased to 50/15min (200/hour) to keep up with initiative creation rate

    'advance-initiative-pipeline': {
        'task': 'core.tasks.advance_initiative_pipeline',
        'schedule': crontab(minute='*/15'),  # Session 926: Every 15 minutes (was hourly)
        'kwargs': {'limit': 50, 'auto_approve': True},  # Session 926: 50 per run (was 10)
        'options': {
            'expires': 800,  # Just under 15 minutes
        }
    },

    # Session 1058 Level 3: Auto-dispatch pending action items to assigned agents
    'dispatch-pending-action-items': {
        'task': 'core.tasks.dispatch_pending_action_items',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1790,  # Just under 30 minutes
        }
    },

    # ==================== SESSION 872: CELERY HEALTH MONITORING ====================
    # Monitor task execution and send Discord alerts on failures
    # Checks spider data freshness, task completion, and schedule staleness

    'monitor-celery-health': {
        'task': 'core.tasks.monitor_celery_health',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,  # 30 minutes
        }
    },

    # ==================== SESSION 900: SIGNAL INTELLIGENCE ====================
    # Aggregate spider signals into SignalClusters and generate AutoTopics
    # This powers the Origin & Trigger UI showing WHY conversations happen

    'aggregate-spider-signals': {
        'task': 'aggregate_spider_signals',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'kwargs': {'lookback_hours': 6},
        'options': {
            'expires': 1800,  # 30 minutes
        }
    },

    'process-pending-auto-topics': {
        'task': 'process_pending_auto_topics',
        'schedule': crontab(minute=45),  # Every hour at :45
        'kwargs': {'max_topics': 3},
        'options': {
            'expires': 3500,
        }
    },

    'cleanup-expired-signals': {
        'task': 'cleanup_expired_signals',
        'schedule': crontab(hour=4, minute=30),  # Daily at 4:30 AM
        'options': {
            'expires': 3600,
        }
    },

    # Session 905: Research Self-Unblock Loop
    # Checks for blocked research that's ready to retry
    'check-blocked-research': {
        'task': 'core.tasks.check_blocked_research_for_unblock',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'options': {
            'expires': 900,
        }
    },

    # Session 905: Initiative Auto-Progression
    # Automatically progresses initiatives when quality criteria met
    'process-initiative-auto-progression': {
        'task': 'core.tasks.process_initiative_auto_progression',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
        'options': {
            'expires': 600,
        }
    },

    # Session 925: Cleanup Stuck Agent Executions
    # Marks executions stuck in running/in_progress as failed
    # Session 1098: Raised from 25min to 35min — research agents now have 25 min
    # wall-clock timeouts (ResearchAgent, CustomerResearchAgent, WhaleWatcherAgent).
    # 35 min gives 10 min grace past the longest explicit timeout (25 min).
    'cleanup-stuck-agent-executions': {
        'task': 'core.tasks.cleanup_stale_agent_executions',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
        'kwargs': {'minutes_threshold': 35},  # 35 min — 10 min grace past 25 min research agent timeout
        'options': {
            'expires': 600,  # 10 minutes
        }
    },

    # Session 1075: Zombie Work Reaper
    # Closes stalled deliberation sessions (active, 0 turns, >1h)
    # Completes stale pilot executions (running >7 days → partial)
    'reap-zombie-work': {
        'task': 'core.tasks.reap_zombie_work',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
        'options': {
            'expires': 1800,  # 30 minutes
            'queue': 'default',
        }
    },

    # Session 926: Audio Cache Cleanup for Universal Agent Voice System
    # Evicts old cache entries to manage storage (>30 days with <5 accesses)
    'cleanup-audio-cache': {
        'task': 'core.tasks.cleanup_audio_cache',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
        'options': {
            'expires': 3600,  # 1 hour
        }
    },

    # Session 1101: Nightly stale content cleanup
    # Archives ready/draft deliverables older than 7 days (skips saved/pinned/published)
    'cleanup-stale-content': {
        'task': 'core.tasks.cleanup_stale_content',
        'schedule': crontab(hour=10, minute=5),  # 3:05 AM MST (UTC-7)
        'kwargs': {'cutoff_days': 7, 'statuses': ['ready', 'draft'], 'cap': 500},
        'options': {
            'expires': 3600,  # 1 hour
            'queue': 'default',
        }
    },

    # Session 926: Junk Initiative Cleanup to prevent pipeline backlogs
    # Archives initiatives with bad names or stale without Stage 1 docs
    'cleanup-junk-initiatives': {
        'task': 'core.tasks.cleanup_junk_initiatives',
        'schedule': crontab(hour=4, minute=0),  # Daily at 4 AM
        'kwargs': {'stale_days': 7},  # Archive after 7 days with no Stage 1 doc
        'options': {
            'expires': 3600,  # 1 hour
        }
    },

    # Session 927: Boardroom Cleanup to prevent attention item backlog
    # Deletes spider_action news items and [Learned] junk
    'cleanup-boardroom-junk': {
        'task': 'core.tasks.cleanup_boardroom_junk',
        'schedule': crontab(hour=4, minute=30),  # Daily at 4:30 AM
        'kwargs': {'spider_action_hours': 24},  # Delete spider actions older than 24h
        'options': {
            'expires': 3600,  # 1 hour
        }
    },

    # Session 945: Learning Loop - Extract patterns from execution data
    # Runs every 6 hours to keep learning patterns fresh
    'run-learning-loop': {
        'task': 'core.tasks.run_learning_loop_cycle',
        'schedule': crontab(hour='*/6', minute=45),  # Every 6 hours at :45
        'kwargs': {'lookback_days': 7},  # Analyze last 7 days of data
        'options': {
            'expires': 3600,  # 1 hour
        }
    },

    # Session 943: Auto-process ExtractedArtifacts to prevent 42K+ backlog
    # Runs every 6 hours with AGGRESSIVE mode to clear backlog faster
    'auto-process-extracted-artifacts': {
        'task': 'core.tasks.auto_process_extracted_artifacts',
        'schedule': crontab(hour='*/6', minute=15),  # Every 6 hours at :15
        'kwargs': {
            'stale_days': 7,       # Questions/experiments older than 7 days → rejected
            'archive_days': 14,    # Action items older than 14 days with low score → rejected
            'batch_size': 2000,    # Process up to 2000 items per run
            'aggressive': True,    # Enable aggressive cleanup rules
        },
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    # Session 1000: Intelligence Desks — run all 4 desk coordinators daily at 6 AM
    'run-all-desks-intelligence': {
        'task': 'core.tasks.run_all_desks_intelligence',
        'schedule': crontab(minute=0, hour=6),
        'options': {
            'expires': 3600,
        },
    },
    # Session 1032: Daily cleanup of fuzzy-duplicate conversations
    'cleanup-conversation-duplicates': {
        'task': 'core.tasks.cleanup_conversation_duplicates_task',
        'schedule': crontab(hour=4, minute=30),  # Daily at 4:30 AM
        'options': {
            'expires': 3600,
        },
    },
    # Session 1055: Periodic workspace rescan to keep PA context fresh
    'rescan-active-workspaces': {
        'task': 'core.tasks.rescan_active_workspaces',
        'schedule': crontab(day_of_week=3, hour=3, minute=45),  # Wednesday 3:45 AM
        'options': {
            'expires': 3600,
        },
    },
    # Session 1064: Telemetry cleanup — prevent unbounded table growth
    'cleanup-celery-task-events': {
        'task': 'core.tasks.cleanup_celery_task_events',
        'schedule': crontab(day_of_week='sunday', hour=4, minute=0),  # Weekly Sunday 4 AM
        'options': {
            'expires': 7200,
        },
    },
    'cleanup-llm-call-logs': {
        'task': 'core.tasks.cleanup_llm_call_logs',
        'schedule': crontab(day_of_week='sunday', hour=4, minute=15),  # Weekly Sunday 4:15 AM
        'options': {
            'expires': 7200,
        },
    },
    # Session 1064: Daily priority scan — was routed but never scheduled
    'daily-priority-scan': {
        'task': 'core.tasks.run_daily_priority_scan',
        'schedule': crontab(hour=6, minute=0),  # Daily 6 AM
        'options': {
            'expires': 3600,
        },
    },
    # PA Tool Learning Loop — mine ToolCallRecord for patterns
    'analyze-pa-tool-patterns': {
        'task': 'core.tasks.analyze_pa_tool_patterns',
        'schedule': crontab(hour='*/6', minute=15),  # Every 6 hours at :15
        'options': {
            'expires': 21600,
        },
    },
    'cleanup-expired-pa-insights': {
        'task': 'core.tasks.cleanup_expired_pa_insights',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
        'options': {
            'expires': 86400,
        },
    },
    # Session G2: Data retention — archive old artifacts by sensitivity level
    'enforce-data-retention': {
        'task': 'core.tasks.enforce_data_retention',
        'schedule': crontab(hour=4, minute=0),  # Daily at 4 AM
        'options': {
            'expires': 86400,
            'queue': 'default',
        },
    },
    # Session G3: Ops Control Loop — daily self-verification (smoke + health + errors)
    'ops-control-loop': {
        'task': 'core.tasks.ops_control_loop',
        'schedule': crontab(hour=7, minute=0),  # Daily at 7:00 UTC
        'options': {
            'expires': 3600,
        },
    },
    # Session 1068: LLM cost spike detection — hourly check
    'check-llm-cost-spike': {
        'task': 'core.tasks.check_llm_cost_spike',
        'schedule': 3600.0,  # Every hour
        'options': {
            'expires': 3600,
        },
    },
    # Session 1080: Ops Autopilot — automated incident response with governance
    'run-ops-autopilot': {
        'task': 'core.tasks.run_ops_autopilot',
        'schedule': 600.0,  # Every 10 minutes
        'options': {
            'expires': 600,
        },
    },
    # Autonomous ops digest — posts system health into PA conversation
    'post-ops-digest': {
        'task': 'core.tasks.post_ops_digest',
        'schedule': 1800.0,  # Every 30 minutes
        'options': {
            'expires': 1800,
        },
    },
    # Congress data sync — members, bills, embeddings (every 6 hours)
    'sync-congress-data': {
        'task': 'core.tasks.sync_congress_data',
        'schedule': 21600.0,  # 6 hours
        'options': {
            'queue': 'long_running',
            'expires': 21600,
        },
    },
    # RAG retrieval canary — daily at 5 AM MST (12:00 UTC)
    'rag-retrieval-canary': {
        'task': 'core.rag_retrieval_canary',
        'schedule': crontab(hour=12, minute=0),
        'options': {
            'queue': 'default',
            'expires': 3600,
        },
    },
}

# Task routing configuration
# Session 573: Task routes are now defined in settings.py (CELERY_TASK_ROUTES)
# Multi-queue architecture:
#   - default: Quick tasks (most core.tasks.*)
#   - long_running: Spider network, agent conversations, dreams (1+ min tasks)
#   - broadcast: High-frequency status updates (30-180s interval tasks)
#   - agents, sports, content, ml: Module-specific queues
# See settings.py CELERY_TASK_ROUTES for full configuration
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange = 'default'
app.conf.task_default_routing_key = 'default'

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Session 919: Explicitly include task modules with non-standard names.
# autodiscover_tasks() only finds tasks.py, not tasks_agents.py
# Using app.conf.imports ensures workers import these modules at startup.
app.conf.imports = (
    'core.tasks_agents',  # Agent execution tasks (execute_agent, execute_orchestration)
)


# Session 983: Connect Celery task telemetry signals.
# Writes CeleryTaskEvent rows on task_prerun/task_postrun/task_failure
# so status_snapshot_tool can report accurate Celery execution counts
# regardless of the CELERY_RESULT_BACKEND setting.
import core.celery_telemetry  # noqa: F401  — signal handlers connect on import


@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery configuration."""
    logger.error(f'Request: {self.request!r}')
    return 'Core Celery is working!'
