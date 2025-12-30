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
    # Sports Prediction Evaluation & Bet Settlement
    # Updated Session 23: Using new PredictionEvaluator system
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
        'args': (30,)  # Days before expiring
    },
    # Session 6: Automated Spider Data Processing
    'process-spider-data-automatic': {
        'task': 'core.tasks.process_spider_data_automatic',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'options': {
            'expires': 300,  # Expire after 5 minutes if not executed
        }
    },
    # Session 139: Background 3D Model Status Polling
    'poll-pending-3d-models': {
        'task': 'core.tasks.poll_pending_3d_models',
        'schedule': 30.0,  # Every 30 seconds
        'options': {
            'expires': 25,  # Expire after 25 seconds if not executed (just before next run)
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
        'kwargs': {'batch_size': 500},  # Session 604: Increased from 200 to 500
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
        }
    },
    'update-agent-effectiveness': {
        'task': 'core.tasks.update_agent_effectiveness_from_learning',
        'schedule': crontab(hour=5, minute=30),  # Daily at 5:30 AM
        'options': {
            'expires': 3600,
        }
    },
    'broadcast-learning-status': {
        'task': 'core.tasks.broadcast_learning_status',
        'schedule': 60.0,  # Every 60 seconds - real-time learning updates
        'options': {
            'expires': 55,
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
    # Addresses the 82% execution gap identified in Session 588
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
    # Session 589: Daily Execution Gap Metrics Report
    # Tracks progress on closing the decision-action gap
    'report-execution-gap-metrics': {
        'task': 'core.tasks.report_execution_gap_metrics',
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
        'schedule': 120.0,  # Every 2 minutes - show recent conversations
        'options': {
            'expires': 115,
        }
    },
    # Session 573: System State Aggregator Cache Refresh
    # Keeps PA's system awareness current by aggregating attention items
    'refresh-system-state-cache': {
        'task': 'core.tasks.refresh_system_state_cache',
        'schedule': 60.0,  # Every 60 seconds
        'options': {
            'expires': 55,
        }
    },
    # Session 247: Agent Dreams (Idle Thoughts & Creative Ideas)
    # Agents dream up creative ideas when they're idle
    'agent-dream-cycle': {
        'task': 'core.tasks.generate_agent_dreams',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes - agents dream when idle
        'options': {
            'expires': 900,  # 15 minutes
        }
    },
    'broadcast-dream-journal': {
        'task': 'core.tasks.broadcast_dream_journal',
        'schedule': 180.0,  # Every 3 minutes - show recent dreams
        'options': {
            'expires': 175,
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
    # Addresses: 422 dreams/day generated vs 83 decisions/day processed
    'dream-auto-triage': {
        'task': 'core.tasks.auto_triage_dreams',
        'schedule': crontab(hour='*/4', minute=30),  # Every 4 hours at :30
        'options': {
            'expires': 14400,  # 4 hours
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
        'schedule': 120.0,  # Every 2 minutes - broadcast status
        'options': {
            'expires': 115,
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
        'schedule': 120.0,  # Every 2 minutes - broadcast evolution status
        'options': {
            'expires': 115,
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
    # Session 466: Autonomous Content Studio (Tier 1 Autonomous Situation)
    # Property #5: Self-Renewal - system runs forever without intervention
    # Session 539: Increased frequency from 4 hours to 1 hour for timely content
    'autonomous-content-studio-loop': {
        'task': 'autonomous_studio.run_main_loop',
        'schedule': crontab(minute=0),  # Every hour at :00
        'options': {
            'expires': 3600,  # 1 hour
        }
    },
    'track-content-performance-daily': {
        'task': 'autonomous_studio.track_performance',
        'schedule': crontab(hour=20, minute=0),  # Daily at 8 PM
        'options': {
            'expires': 7200,  # 2 hours
        }
    },
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
        'schedule': 30.0,  # Every 30 seconds
        'options': {
            'expires': 25,  # Expire before next run
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
        'schedule': 30.0,  # Every 30 seconds
        'options': {
            'expires': 25,  # Expire before next run
        }
    },
    # Process validation event queue (every 30 seconds)
    'process-event-bus-validation-queue': {
        'task': 'core.tasks.process_event_bus_validation_queue',
        'schedule': 30.0,  # Every 30 seconds
        'options': {
            'expires': 25,  # Expire before next run
        }
    },
    # Process analytics event queue (every minute)
    'process-event-bus-analytics-queue': {
        'task': 'core.tasks.process_event_bus_analytics_queue',
        'schedule': 60.0,  # Every minute
        'options': {
            'expires': 55,  # Expire before next run
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
    # Main detection cycle - scans for narrative shifts
    'narrative-drift-detector-cycle': {
        'task': 'narrative_drift.run_detector_cycle',
        'schedule': crontab(minute=0, hour='*/4'),  # Every 4 hours at :00
        'options': {
            'expires': 14400,  # 4 hours
        }
    },
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
    # Daily narrative digest to Discord
    'narrative-daily-digest': {
        'task': 'narrative_drift.send_daily_digest',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9 AM
        'options': {
            'expires': 3600,  # 1 hour
        }
    },

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

    # Full pipeline run - comprehensive cycle through all 3 Tier 1 Autonomous Situations
    # Spider → ML Score → Narrative Check → Content Gen → Revenue Track
    'unified-pipeline-complete-cycle': {
        'task': 'unified_pipeline.run_complete_cycle',
        'schedule': crontab(minute=0, hour='*/12'),  # Every 12 hours at :00
        'options': {
            'expires': 43200,  # 12 hours
        }
    },

    # Quick health check - lightweight verification all systems are operational
    'unified-pipeline-health-check': {
        'task': 'unified_pipeline.health_check',
        'schedule': crontab(minute=15, hour='*/2'),  # Every 2 hours at :15
        'options': {
            'expires': 7200,  # 2 hours
        }
    },

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

    # Blockchain Security Monitor - Session 539: increased to hourly
    # Analyzes etherscan/coingecko data for whale movements, price manipulation, unusual volume
    # Sends alerts to #blockchain-alerts Discord channel
    'autonomous-blockchain-security-monitor': {
        'task': 'autonomous.blockchain_security_monitor',
        'schedule': crontab(minute=5),  # Every hour at :05
        'options': {
            'expires': 3600,  # 1 hour
        }
    },

    # Stock Market Intelligence - Session 539: increased to hourly
    # Analyzes yahoo_finance/finnhub/sec_edgar data with Bull vs Bear debate
    # Sends alerts to #stock-alerts Discord channel
    'autonomous-stock-market-intelligence': {
        'task': 'autonomous.stock_market_intelligence',
        'schedule': crontab(minute=10),  # Every hour at :10
        'options': {
            'expires': 3600,  # 1 hour
        }
    },

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
    # Execute approved artifacts via agent routing
    'execute-approved-artifacts': {
        'task': 'core.tasks.execute_approved_artifacts',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
        'kwargs': {'limit': 10},
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

@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery configuration."""
    logger.error(f'Request: {self.request!r}')
    return 'Core Celery is working!'