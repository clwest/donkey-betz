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
    # Session 207: Spider Network Execution
    'run-spider-network': {
        'task': 'core.tasks.run_spider_network',
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
    # Session 244: Daily Learning Embeddings
    # Convert all agent learning into searchable vector embeddings
    'embed-daily-agent-learning': {
        'task': 'core.tasks.embed_daily_agent_learning',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
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