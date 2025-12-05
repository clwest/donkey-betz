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
    'cleanup-old-model-files': {
        'task': 'ml.cleanup_old_model_files',
        'schedule': crontab(day_of_week=1, hour=1, minute=0),  # Monday 1 AM
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
        'options': {
            'expires': 600,  # Expire after 10 minutes
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
    # Session 244: Daily Learning Embeddings
    # Convert all agent learning into searchable vector embeddings
    'embed-daily-agent-learning': {
        'task': 'core.tasks.embed_daily_agent_learning',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        'options': {
            'expires': 7200,  # 2 hours
        }
    },
    # Session 244: Agent Conversations (Inter-Agent Chat)
    # Agents discuss topics with each other autonomously
    'agent-conversation-cycle': {
        'task': 'core.tasks.run_agent_conversation',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes - agents chat frequently
        'options': {
            'expires': 300,  # 5 minutes
        }
    },
    # Session 360/361: Multi-Agent Panel Conversations
    # Panel discussions with 3-5 agents for richer insights
    'multi-agent-panel-cycle': {
        'task': 'core.tasks.run_multi_agent_conversation',
        'schedule': crontab(minute='*/20'),  # Every 20 minutes - panels take longer
        'options': {
            'expires': 1200,  # 20 minutes
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
    'broadcast-conversation-status': {
        'task': 'core.tasks.broadcast_conversation_status',
        'schedule': 120.0,  # Every 2 minutes - show recent conversations
        'options': {
            'expires': 115,
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
}

# Spider-specific task routing configuration
app.conf.task_routes = {
    'ai_core.spiders.tasks.*': {'queue': 'spider_queue'},
}
app.conf.task_default_queue = 'default'
app.conf.task_default_exchange = 'default'
app.conf.task_default_routing_key = 'default'

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    """Debug task to test Celery configuration."""
    print(f'Request: {self.request!r}')
    return 'Core Celery is working!'