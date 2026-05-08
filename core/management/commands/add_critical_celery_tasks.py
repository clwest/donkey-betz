"""
Session 810: Add Critical Missing Celery Beat Tasks

Emergency fix for missing body system health checks and agent rotation tasks.
These tasks were defined in celery.py but never synced to DatabaseScheduler.

Run this immediately on production to enable:
- All 10 Body System health checks (HEART, LUNGS, BRAIN, SKIN, etc.)
- Agent category rotation tasks (15 categories)
- Agent workspace integration tasks
- Dream processing pipeline
- Learning and knowledge tasks
- Market intelligence tasks
- And 100+ more critical tasks

Usage:
    python manage.py add_critical_celery_tasks           # Add all missing
    python manage.py add_critical_celery_tasks --dry-run # Preview only
"""

import json
import logging
from django.core.management.base import BaseCommand, CommandError
from django_celery_beat.models import PeriodicTask, IntervalSchedule, CrontabSchedule

logger = logging.getLogger(__name__)


# Critical tasks that MUST be running
CRITICAL_TASKS = {
    # ==========================================================================
    # BODY SYSTEMS (10 systems) - These monitor the "health" of the AI
    # ==========================================================================
    'heart-service-heartbeat': {
        'task': 'core.tasks.run_heartbeat',
        'interval': 60,  # Every 60 seconds
        'queue': 'broadcast',
    },
    'lungs-service-breathing': {
        'task': 'core.tasks.check_breathing',
        'crontab': {'minute': '*/15'},  # Every 15 minutes
        'queue': 'default',
    },
    'lungs-daily-forecast': {
        'task': 'core.tasks.daily_cost_forecast',
        'crontab': {'hour': '8', 'minute': '0'},  # Daily at 8 AM
        'queue': 'default',
    },
    'lungs-daily-reset': {
        'task': 'core.tasks.reset_daily_respiratory_stats',
        'crontab': {'hour': '0', 'minute': '1'},  # Daily at 00:01
        'queue': 'default',
    },
    'circulatory-system-pulse': {
        'task': 'core.tasks.check_circulation',
        'interval': 30,  # Every 30 seconds
        'queue': 'broadcast',
    },
    'spine-alignment-check': {
        'task': 'core.tasks.check_spine_alignment',
        'interval': 60,  # Every 60 seconds
        'queue': 'broadcast',
    },
    'immune-system-scan': {
        'task': 'core.tasks.immune_scan',
        'interval': 45,  # Every 45 seconds
        'queue': 'broadcast',
    },
    'digestive-system-check': {
        'task': 'core.tasks.check_digestion',
        'interval': 60,  # Every 60 seconds
        'queue': 'broadcast',
    },
    'muscular-system-check': {
        'task': 'core.tasks.check_muscular',
        'interval': 90,  # Every 90 seconds
        'queue': 'broadcast',
    },
    'brain-system-check': {
        'task': 'core.tasks.check_brain',
        'interval': 60,  # Every 60 seconds
        'queue': 'broadcast',
    },
    'skin-system-check': {
        'task': 'core.tasks.check_skin',
        'interval': 90,  # Every 90 seconds
        'queue': 'broadcast',
    },
    'nervous-system-check': {
        'task': 'core.tasks.check_nervous',
        'interval': 60,  # Every 60 seconds
        'queue': 'broadcast',
    },
    'body-coordinator-check': {
        'task': 'core.tasks.coordinate_body',
        'interval': 60,  # Every 60 seconds
        'queue': 'broadcast',
    },

    # ==========================================================================
    # AGENT CATEGORY ROTATION (15 categories)
    # ==========================================================================
    'agent-category-research': {
        'task': 'core.tasks.agent_category_rotation',
        'crontab': {'minute': '0', 'hour': '*/6'},
        'args': ['research'],
        'queue': 'long_running',
    },
    'agent-category-strategy': {
        'task': 'core.tasks.agent_category_rotation',
        'crontab': {'minute': '0', 'hour': '7'},
        'args': ['strategy'],
        'queue': 'long_running',
    },
    'agent-category-content': {
        'task': 'core.tasks.agent_category_rotation',
        'crontab': {'minute': '15', 'hour': '*/8'},
        'args': ['content'],
        'queue': 'long_running',
    },
    'agent-category-financial': {
        'task': 'core.tasks.agent_category_rotation',
        'crontab': {'minute': '30', 'hour': '*/4'},
        'args': ['financial'],
        'queue': 'long_running',
    },
    'agent-category-predictions': {
        'task': 'core.tasks.agent_category_rotation',
        'crontab': {'minute': '45', 'hour': '*/6'},
        'args': ['predictions'],
        'queue': 'long_running',
    },
    'agent-category-blockchain': {
        'task': 'core.tasks.agent_category_rotation',
        'crontab': {'minute': '20', 'hour': '*/4'},
        'args': ['blockchain'],
        'queue': 'long_running',
    },
    'agent-category-narrative': {
        'task': 'core.tasks.agent_category_rotation',
        'crontab': {'minute': '40', 'hour': '*/8'},
        'args': ['narrative'],
        'queue': 'long_running',
    },
    'agent-category-podcast': {
        'task': 'core.tasks.agent_category_rotation',
        'crontab': {'minute': '0', 'hour': '5,17'},
        'args': ['podcast'],
        'queue': 'long_running',
    },
    'agent-category-development': {
        'task': 'core.tasks.agent_category_rotation',
        'crontab': {'minute': '50', 'hour': '*/8'},
        'args': ['development'],
        'queue': 'long_running',
    },
    'agent-category-media': {
        'task': 'core.tasks.agent_category_rotation',
        'crontab': {'minute': '10', 'hour': '8,20'},
        'args': ['media'],
        'queue': 'long_running',
    },
    'agent-category-executive': {
        'task': 'core.tasks.agent_category_rotation',
        'crontab': {'minute': '0', 'hour': '8'},
        'args': ['executive'],
        'queue': 'long_running',
    },
    'agent-category-coordination': {
        'task': 'core.tasks.agent_category_rotation',
        'crontab': {'minute': '25', 'hour': '*/6'},
        'args': ['coordination'],
        'queue': 'long_running',
    },
    'agent-category-system': {
        'task': 'core.tasks.agent_category_rotation',
        'crontab': {'minute': '5', 'hour': '*/4'},
        'args': ['system'],
        'queue': 'long_running',
    },
    'agent-category-security': {
        'task': 'core.tasks.agent_category_rotation',
        'crontab': {'minute': '35', 'hour': '*/6'},
        'args': ['security'],
        'queue': 'long_running',
    },
    'agent-category-assistant': {
        'task': 'core.tasks.agent_category_rotation',
        'crontab': {'minute': '0', 'hour': '9'},
        'args': ['assistant'],
        'queue': 'long_running',
    },

    # ==========================================================================
    # AGENT WORKSPACE INTEGRATION
    # ==========================================================================
    'agent-workspace-status-report': {
        'task': 'core.tasks.agent_workspace_status_report',
        'crontab': {'minute': '0', 'hour': '*/6'},
        'queue': 'long_running',
    },
    'agent-daily-summary': {
        'task': 'core.tasks.agent_daily_summary',
        'crontab': {'minute': '0', 'hour': '0'},
        'queue': 'default',
    },
    'agent-research-to-workspace': {
        'task': 'core.tasks.agent_research_to_workspace',
        'crontab': {'minute': '30', 'hour': '*/8'},
        'queue': 'long_running',
    },
    'agent-content-to-workspace': {
        'task': 'core.tasks.agent_content_to_workspace',
        'crontab': {'minute': '0', 'hour': '6,18'},
        'queue': 'long_running',
    },
    'agent-full-rotation-weekly': {
        'task': 'core.tasks.full_agent_rotation',
        'crontab': {'minute': '0', 'hour': '3', 'day_of_week': '0'},  # Sunday 3 AM
        'queue': 'long_running',
    },

    # ==========================================================================
    # AGENT LEARNING & EVOLUTION
    # ==========================================================================
    'agent-learning-cycle': {
        'task': 'core.tasks.run_agent_learning_cycle',
        'crontab': {'minute': '*/10'},
        'queue': 'default',
    },
    'agent-think-synthesize': {
        'task': 'core.tasks.agent_think_and_synthesize',
        'crontab': {'minute': '*/30'},
        'queue': 'default',
    },
    'embed-agent-activity': {
        'task': 'core.tasks.embed_agent_activity',
        'crontab': {'minute': '*/30'},
        'queue': 'default',
    },
    'embed-daily-agent-learning': {
        'task': 'core.tasks.embed_daily_agent_learning',
        'crontab': {'hour': '2', 'minute': '0'},
        'queue': 'default',
    },
    'update-agent-effectiveness': {
        'task': 'core.tasks.update_agent_effectiveness_from_learning',
        'crontab': {'hour': '5', 'minute': '30'},
        'queue': 'default',
    },
    'update-agent-performance': {
        'task': 'agents.update_agent_performance',
        'crontab': {'hour': '4', 'minute': '0'},
        'queue': 'default',
    },
    'process-agent-activity-xp': {
        'task': 'core.tasks.process_agent_activity_xp',
        'crontab': {'minute': '*/15'},
        'queue': 'default',
    },
    'evolve-agent-relationships': {
        'task': 'core.tasks.evolve_agent_relationships',
        'crontab': {'minute': '*/30'},
        'queue': 'default',
    },
    'update-alliance-strengths': {
        'task': 'core.tasks.update_alliance_strengths',
        'crontab': {'minute': '0'},  # Every hour
        'queue': 'default',
    },
    'check-level-milestones': {
        'task': 'core.tasks.check_level_milestones',
        'crontab': {'minute': '0'},  # Every hour
        'queue': 'default',
    },
    'broadcast-evolution-status': {
        'task': 'core.tasks.broadcast_evolution_status',
        'interval': 120,
        'queue': 'broadcast',
    },
    'broadcast-relationship-status': {
        'task': 'core.tasks.broadcast_relationship_status',
        'interval': 120,
        'queue': 'broadcast',
    },

    # ==========================================================================
    # DREAM PROCESSING PIPELINE
    # ==========================================================================
    'dream-productization-cycle': {
        'task': 'core.tasks.score_and_promote_dreams',
        'crontab': {'minute': '*/20'},
        'queue': 'default',
    },
    'dream-implementation-cycle': {
        'task': 'core.tasks.process_approved_dreams',
        'crontab': {'minute': '*/15'},
        'queue': 'default',
    },
    'dream-execution-cycle': {
        'task': 'core.tasks.execute_dream_implementations',
        'crontab': {'minute': '*/20'},
        'queue': 'default',
    },
    'dream-auto-triage': {
        'task': 'core.tasks.auto_triage_dreams',
        'crontab': {'hour': '*/4', 'minute': '30'},
        'queue': 'default',
    },
    'cleanup-stale-dreams': {
        'task': 'core.tasks.cleanup_stale_dreams',
        'crontab': {'hour': '6', 'minute': '0'},
        'kwargs': {'max_age_hours': 72},
        'queue': 'default',
    },
    'execute-approved-dreams-via-orchestration': {
        'task': 'core.tasks.execute_approved_dreams_via_orchestration',
        'crontab': {'minute': '*/10'},
        'queue': 'default',
    },

    # ==========================================================================
    # SPIDER DATA PROCESSING
    # ==========================================================================
    'process-core-spider-data': {
        'task': 'core.tasks.process_core_spider_data',
        'crontab': {'minute': '*/2'},
        'queue': 'default',
    },
    'process-spider-data-automatic': {
        'task': 'core.tasks.process_spider_data_automatic',
        'crontab': {'minute': '*/5'},
        'queue': 'default',
    },
    'backfill-spider-embeddings': {
        'task': 'core.tasks.backfill_spider_embeddings',
        'crontab': {'minute': '*/10'},
        'kwargs': {'batch_size': 500},
        'queue': 'default',
    },
    'collect-spider-data': {
        'task': 'core.tasks.collect_spider_data',
        'crontab': {'minute': '0', 'hour': '*/4'},
        'queue': 'long_running',
    },
    'recalculate-spider-priorities': {
        'task': 'core.tasks.recalculate_spider_priorities',
        'crontab': {'hour': '*/6', 'minute': '45'},
        'queue': 'default',
    },
    'process-spider-actions': {
        'task': 'core.tasks.process_spider_actions',
        'crontab': {'minute': '*/30'},
        'queue': 'default',
    },
    'scan-spider-opportunities': {
        'task': 'intelligence.tasks.scan_spider_opportunities',
        'crontab': {'minute': '*/15'},
        'queue': 'default',
    },
    'warm-up-spiders': {
        'task': 'ai_core.tasks.warm_up_spider_network',
        'crontab': {'minute': '0', 'hour': '*/4'},
        'queue': 'default',
    },
    'cleanup-spider-item-hashes': {
        'task': 'core.tasks.cleanup_spider_item_hashes',
        'crontab': {'hour': '3', 'minute': '30'},
        'queue': 'default',
    },

    # ==========================================================================
    # LEARNING PIPELINES
    # ==========================================================================
    'daily-learning-pipeline': {
        'task': 'core.tasks.run_daily_learning_pipeline',
        'crontab': {'hour': '5', 'minute': '0'},
        'queue': 'default',
    },
    'project-learning-cycle': {
        'task': 'core.tasks.run_project_learning_cycle',
        'crontab': {'hour': '6', 'minute': '0'},
        'queue': 'default',
    },
    'sync-project-knowledge': {
        'task': 'core.tasks.sync_project_knowledge',
        'crontab': {'minute': '*/30'},
        'queue': 'default',
    },
    'update-learning-profiles': {
        'task': 'core.tasks.update_learning_profiles',
        'crontab': {'hour': '6', 'minute': '0'},
        'queue': 'default',
    },
    'validate-knowledge-sources': {
        'task': 'core.tasks.validate_knowledge_sources',
        'crontab': {'hour': '3', 'minute': '0'},
        'queue': 'default',
    },
    'auto-resolve-knowledge-gaps': {
        'task': 'core.tasks.auto_resolve_knowledge_gaps',
        'crontab': {'hour': '*/6'},
        'queue': 'default',
    },
    'backfill-memory-embeddings': {
        'task': 'core.tasks.backfill_memory_embeddings',
        'crontab': {'minute': '*/30'},
        'queue': 'default',
    },
    'backfill-conversation-embeddings': {
        'task': 'core.tasks.backfill_conversation_embeddings',
        'crontab': {'minute': '*/30'},
        'queue': 'default',
    },
    # Session 915: Backfill missing stage documents for initiatives
    'backfill-stage-documents': {
        'task': 'core.tasks.backfill_stage_documents',
        'crontab': {'minute': '*/30'},
        'kwargs': {'stage_num': 1, 'limit': 50},
        'queue': 'default',
    },

    # ==========================================================================
    # AUTONOMOUS INTELLIGENCE
    # ==========================================================================
    'autonomous-intelligence-loop': {
        'task': 'core.tasks.run_autonomous_intelligence_loop',
        'crontab': {'minute': '*/15'},
        'queue': 'default',
    },
    'autonomous-thinking-cycle': {
        'task': 'core.tasks.run_autonomous_thinking_cycle',
        'crontab': {'minute': '0'},  # Every hour
        'kwargs': {'cycle_type': 'scheduled', 'lookback_hours': 24},
        'queue': 'default',
    },
    'run-autonomy-cycle': {
        'task': 'core.tasks.run_autonomy_cycle',
        'crontab': {'minute': '*/30'},
        'queue': 'long_running',
    },

    # ==========================================================================
    # MARKET INTELLIGENCE
    # ==========================================================================
    'market-intelligence-desk': {
        'task': 'core.tasks.run_market_intelligence_desk',
        'crontab': {'minute': '0', 'hour': '8', 'day_of_week': '1-5'},
        'queue': 'default',
    },
    'market-intelligence-scan': {
        'task': 'core.tasks.market_intelligence_scan',
        'crontab': {'minute': '0', 'hour': '*/2'},
        'queue': 'default',
    },
    'market-movement-alerts': {
        'task': 'core.tasks.market_movement_alerts',
        'crontab': {'minute': '*/30'},
        'queue': 'default',
    },
    'stock-audit-cycle': {
        'task': 'core.tasks.run_stock_audit_cycle',
        'crontab': {'minute': '*/30', 'hour': '9-16', 'day_of_week': '1-5'},
        'queue': 'default',
    },
    'run-stock-market-intelligence': {
        'task': 'core.tasks.run_stock_market_intelligence',
        'crontab': {'minute': '0', 'hour': '9,12,16', 'day_of_week': '1-5'},
        'queue': 'long_running',
    },
    'collect-kalshi-prediction-markets': {
        'task': 'core.tasks.collect_kalshi_prediction_markets',
        'crontab': {'minute': '*/30'},
        'queue': 'default',
    },
    'collect-kalshi-market-intelligence': {
        'task': 'core.tasks.collect_kalshi_market_intelligence',
        'crontab': {'minute': '0', 'hour': '*/4'},
        'queue': 'default',
    },

    # ==========================================================================
    # PILOTS, GATES & EXPERIMENTS
    # ==========================================================================
    'gate-auto-approval': {
        'task': 'core.tasks.auto_approve_low_risk_gates',
        'crontab': {'hour': '*/2', 'minute': '15'},
        'kwargs': {'max_gates': 20, 'auto_deploy': True},
        'queue': 'default',
    },
    'process-gate-progression': {
        'task': 'core.tasks.process_gate_progression',
        'crontab': {'minute': '*/15'},
        'queue': 'default',
    },
    'process-gates-and-deploy-pilots': {
        'task': 'core.tasks.process_gates_and_deploy_pilots',
        'crontab': {'minute': '45'},  # Every hour at :45
        'kwargs': {'batch_size': 20},
        'queue': 'default',
    },
    'auto-complete-pilots': {
        'task': 'core.tasks.auto_complete_pilots',
        'crontab': {'minute': '0', 'hour': '*/4'},
        'queue': 'default',
    },
    'evaluate-and-complete-pilots': {
        'task': 'core.tasks.evaluate_and_complete_pilots',
        'crontab': {'minute': '15', 'hour': '*/2'},
        'queue': 'default',
    },
    'evaluate-pilots-smart': {
        'task': 'core.tasks.evaluate_pilots_with_thinking_agent',
        'crontab': {'minute': '30', 'hour': '*/6'},
        'queue': 'default',
    },
    'execute-pilot-implementations': {
        'task': 'core.tasks.execute_pilot_implementations',
        'crontab': {'minute': '30', 'hour': '*/2'},
        'kwargs': {'batch_size': 10},
        'queue': 'default',
    },
    'monitor-experiment-halt-conditions': {
        'task': 'core.tasks.monitor_running_experiments',
        'crontab': {'minute': '*/10'},
        'queue': 'default',
    },
    'update-experiment-kpis': {
        'task': 'core.tasks.update_experiment_kpis',
        'crontab': {'minute': '0'},  # Every hour
        'queue': 'default',
    },

    # ==========================================================================
    # ORCHESTRATION
    # ==========================================================================
    'check-orchestration-timeouts': {
        'task': 'core.tasks.check_orchestration_timeouts',
        'crontab': {'minute': '*/5'},
        'queue': 'default',
    },
    'check-orchestration-auto-approvals': {
        'task': 'core.tasks.check_orchestration_auto_approvals',
        'crontab': {'minute': '*/5'},
        'queue': 'default',
    },

    # ==========================================================================
    # SYSTEM HEALTH
    # ==========================================================================
    'check-celery-health': {
        'task': 'core.tasks.check_celery_health',
        'interval': 120,  # Every 2 minutes
        'queue': 'celery',
    },
    'refresh-system-state-cache': {
        'task': 'core.tasks.refresh_system_state_cache',
        'interval': 60,  # Every 60 seconds
        'queue': 'default',
    },
    'proactive-system-check': {
        'task': 'core.tasks.run_proactive_system_check',
        'crontab': {'hour': '*/2', 'minute': '15'},
        'queue': 'default',
    },

    # ==========================================================================
    # MOOD SYSTEM
    # ==========================================================================
    'check-mood-expirations': {
        'task': 'core.tasks.check_mood_expirations',
        'crontab': {'minute': '*/5'},
        'queue': 'default',
    },
    'apply-mood-rules': {
        'task': 'core.tasks.apply_mood_trigger_rules',
        'crontab': {'minute': '*/10'},
        'queue': 'default',
    },
}


class Command(BaseCommand):
    help = 'Add critical missing Celery Beat tasks to database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be added without making changes'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing tasks'
        )

    def get_or_create_interval(self, seconds):
        """Get or create an interval schedule"""
        interval, _ = IntervalSchedule.objects.get_or_create(
            every=seconds,
            period=IntervalSchedule.SECONDS
        )
        return interval

    def get_or_create_crontab(self, crontab_args):
        """Get or create a crontab schedule (handles duplicate entries)"""
        defaults = {
            'minute': '*',
            'hour': '*',
            'day_of_week': '*',
            'day_of_month': '*',
            'month_of_year': '*',
        }
        defaults.update(crontab_args)

        # First try to find an existing one (handles duplicates)
        existing = CrontabSchedule.objects.filter(**defaults).first()
        if existing:
            return existing

        # If none exists, create one
        return CrontabSchedule.objects.create(**defaults)

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        force = options['force']

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write("SESSION 810: Adding Critical Missing Celery Beat Tasks")
        self.stdout.write(f"{'='*60}\n")

        existing = set(PeriodicTask.objects.values_list('name', flat=True))
        self.stdout.write(f"Existing tasks in database: {len(existing)}")
        self.stdout.write(f"Critical tasks to ensure: {len(CRITICAL_TASKS)}")

        created = 0
        updated = 0
        skipped = 0
        errors = []

        for name, config in CRITICAL_TASKS.items():
            task_name = config['task']
            queue = config.get('queue', 'default')

            if name in existing and not force:
                skipped += 1
                continue

            if dry_run:
                action = "Would update" if name in existing else "Would create"
                self.stdout.write(f"  [DRY RUN] {action}: {name}")
                continue

            try:
                # Determine schedule type
                if 'interval' in config:
                    interval = self.get_or_create_interval(config['interval'])
                    task, task_created = PeriodicTask.objects.update_or_create(
                        name=name,
                        defaults={
                            'task': task_name,
                            'interval': interval,
                            'crontab': None,
                            'args': json.dumps(config.get('args', [])),
                            'kwargs': json.dumps(config.get('kwargs', {})),
                            'queue': queue,
                            'enabled': True,
                        }
                    )
                elif 'crontab' in config:
                    crontab = self.get_or_create_crontab(config['crontab'])
                    task, task_created = PeriodicTask.objects.update_or_create(
                        name=name,
                        defaults={
                            'task': task_name,
                            'crontab': crontab,
                            'interval': None,
                            'args': json.dumps(config.get('args', [])),
                            'kwargs': json.dumps(config.get('kwargs', {})),
                            'queue': queue,
                            'enabled': True,
                        }
                    )
                else:
                    self.stdout.write(self.style.WARNING(f"  ⚠ {name}: No schedule defined"))
                    continue

                if task_created:
                    created += 1
                    self.stdout.write(self.style.SUCCESS(f"  ✓ Created: {name}"))
                else:
                    updated += 1
                    self.stdout.write(f"  ↻ Updated: {name}")

            except Exception as e:
                logger.exception("[CELERY_SYNC] Failed to ensure critical task %s", name)
                self.stdout.write(self.style.ERROR(f"  ✗ Error with {name}: {type(e).__name__}: {e}"))
                errors.append(f"{name}: {type(e).__name__}: {e}")

        # Summary
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write("SUMMARY")
        self.stdout.write(f"{'='*60}")

        if dry_run:
            to_create = len(CRITICAL_TASKS) - skipped
            self.stdout.write(f"Would create/update: {to_create} tasks")
            self.stdout.write(f"Would skip (already exist): {skipped} tasks")
        else:
            self.stdout.write(self.style.SUCCESS(f"Created: {created} tasks"))
            self.stdout.write(f"Updated: {updated} tasks")
            self.stdout.write(f"Skipped (already exist): {skipped} tasks")

            final_count = PeriodicTask.objects.filter(enabled=True).count()
            self.stdout.write(f"\nTotal enabled tasks in database: {final_count}")
            if errors:
                raise CommandError(
                    f"Failed to ensure {len(errors)} critical Celery task(s); "
                    f"see logs for tracebacks"
                )

        # Show body system status
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write("BODY SYSTEM STATUS")
        self.stdout.write(f"{'='*60}")
        body_tasks = ['heart', 'lung', 'brain', 'skin', 'spine', 'immune',
                      'digest', 'muscul', 'nervous', 'circulat', 'body-coordinator']
        for keyword in body_tasks:
            tasks = PeriodicTask.objects.filter(name__icontains=keyword, enabled=True)
            if tasks.exists():
                self.stdout.write(self.style.SUCCESS(f"  ✓ {keyword}: {tasks.count()} task(s) enabled"))
            else:
                self.stdout.write(self.style.WARNING(f"  ⚠ {keyword}: MISSING"))
