"""
Session 810: Database Health Snapshot

Outputs key database metrics for comparing local vs production environments.
Run on both environments and compare the output to find discrepancies.

Usage:
    python manage.py db_health_snapshot
    python manage.py db_health_snapshot --json  # Machine-readable output
"""

import json
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.db.models import Count
from django.utils import timezone
from django.apps import apps


import logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Output database health snapshot for environment comparison'

    def add_arguments(self, parser):
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output as JSON for easy comparison'
        )

    def _safe_count(self, model_path):
        """Safely count a model, returning 0 if not found"""
        try:
            parts = model_path.rsplit('.', 1)
            if len(parts) == 2:
                app_label, model_name = parts
            else:
                return None
            model = apps.get_model(app_label, model_name)
            return model.objects.count()
        except Exception as _e:
            logger.warning(
                "db_health_snapshot._safe_count: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return None

    def _safe_count_filter(self, model_path, **filters):
        """Safely count with filter"""
        try:
            parts = model_path.rsplit('.', 1)
            if len(parts) == 2:
                app_label, model_name = parts
            else:
                return None
            model = apps.get_model(app_label, model_name)
            return model.objects.filter(**filters).count()
        except Exception as _e:
            logger.warning(
                "db_health_snapshot._safe_count_filter: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return None

    def _safe_count_by_field(self, model_path, field):
        """Safely count grouped by field"""
        try:
            parts = model_path.rsplit('.', 1)
            if len(parts) == 2:
                app_label, model_name = parts
            else:
                return {}
            model = apps.get_model(app_label, model_name)
            result = {}
            for item in model.objects.values(field).annotate(count=Count('id')):
                key = item[field] if item[field] is not None else 'null'
                result[str(key)] = item['count']
            return result
        except Exception as _e:
            logger.warning(
                "db_health_snapshot._safe_count_by_field: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return {}

    def _safe_count_recent(self, model_path, date_field, hours):
        """Safely count recent records"""
        try:
            parts = model_path.rsplit('.', 1)
            if len(parts) == 2:
                app_label, model_name = parts
            else:
                return None
            model = apps.get_model(app_label, model_name)
            cutoff = timezone.now() - timedelta(hours=hours)
            return model.objects.filter(**{f'{date_field}__gte': cutoff}).count()
        except Exception as _e:
            logger.warning(
                "db_health_snapshot._safe_count_recent: swallowed (%s: %s) — returning default",
                type(_e).__name__, _e,
            )
            return None

    def handle(self, *args, **options):
        output_json = options['json']

        stats = {}

        # Core Content
        stats['content'] = {
            'SelfBlog': self._safe_count('core.SelfBlog'),
            'HumanAttentionItem': self._safe_count('core.HumanAttentionItem'),
            'HumanAttentionItem_by_type': self._safe_count_by_field('core.HumanAttentionItem', 'item_type'),
            'ContentChannel': self._safe_count('core.ContentChannel'),
            'ContentEpisode': self._safe_count('core.ContentEpisode'),
        }

        # Intelligence Pipeline
        stats['intelligence'] = {
            'Dream': self._safe_count('core.Dream'),
            'Dream_by_status': self._safe_count_by_field('core.Dream', 'status'),
            'Pilot': self._safe_count('core.Pilot'),
            'Pilot_by_status': self._safe_count_by_field('core.Pilot', 'status'),
            'Gate': self._safe_count('core.Gate'),
            'Gate_by_status': self._safe_count_by_field('core.Gate', 'status'),
            'Opportunity': self._safe_count('core.Opportunity'),
            'Experiment': self._safe_count('core.Experiment'),
            'Experiment_by_status': self._safe_count_by_field('core.Experiment', 'status'),
        }

        # Agents & Learning
        stats['agents'] = {
            'Agent_total': self._safe_count('core.Agent'),
            'Agent_active': self._safe_count_filter('core.Agent', is_active=True),
            'AgentKnowledgeSource': self._safe_count('core.AgentKnowledgeSource'),
            'AgentLearningConnection': self._safe_count('core.AgentLearningConnection'),
            'AgentExecution': self._safe_count('core.AgentExecution'),
            'AgentExecution_last_24h': self._safe_count_recent('core.AgentExecution', 'started_at', 24),
            'AgentMemory': self._safe_count('core.AgentMemory'),
            'KnowledgeItem': self._safe_count('core.KnowledgeItem'),
            'ConversationMemory': self._safe_count('core.ConversationMemory'),
        }

        # Spiders
        stats['spiders'] = {
            'SpiderData': self._safe_count('core.SpiderData'),
            'SpiderData_last_24h': self._safe_count_recent('core.SpiderData', 'created_at', 24),
            'SpiderData_last_7d': self._safe_count_recent('core.SpiderData', 'created_at', 24*7),
            'SpiderDataAnnotation': self._safe_count('core.SpiderDataAnnotation'),
        }

        # Orchestration
        stats['orchestration'] = {
            'Orchestration': self._safe_count('core.Orchestration'),
            'Orchestration_by_status': self._safe_count_by_field('core.Orchestration', 'status'),
            'LLMCallLog': self._safe_count('core.LLMCallLog'),
            'LLMCallLog_last_24h': self._safe_count_recent('core.LLMCallLog', 'created_at', 24),
        }

        # Celery Beat
        stats['celery'] = {
            'PeriodicTask_total': self._safe_count('django_celery_beat.PeriodicTask'),
            'PeriodicTask_enabled': self._safe_count_filter('django_celery_beat.PeriodicTask', enabled=True),
        }

        # Body Systems
        stats['body_systems'] = {
            'HeartPulse': self._safe_count('core.HeartPulse'),
            'LungBreath': self._safe_count('core.LungBreath'),
            'BrainThought': self._safe_count('core.BrainThought'),
            'SkinPulse': self._safe_count('core.SkinPulse'),
            'CirculatoryPulse': self._safe_count('core.CirculatoryPulse'),
            'SpinePulse': self._safe_count('core.SpinePulse'),
            'ImmuneScan': self._safe_count('core.ImmuneScan'),
            'DigestiveStatus': self._safe_count('core.DigestiveStatus'),
            'MuscularStatus': self._safe_count('core.MuscularStatus'),
            'NervousSignal': self._safe_count('core.NervousSignal'),
        }

        # Sci-Fi Features
        stats['scifi'] = {
            'MoodState': self._safe_count('core.MoodState'),
            'TimeCapsule': self._safe_count('core.TimeCapsule'),
            'TimeSimulation': self._safe_count('core.TimeSimulation'),
            'AgentRelationship': self._safe_count('core.AgentRelationship'),
            'MemoryCluster': self._safe_count('core.MemoryCluster'),
        }

        # Workspace (SKIN)
        stats['workspace'] = {
            'AgentWorkspaceFile': self._safe_count('core.AgentWorkspaceFile'),
            'WorkspaceProject': self._safe_count('core.WorkspaceProject'),
        }

        # Betting/Sports
        stats['betting'] = {
            'Wager': self._safe_count('core.Wager'),
            'BettingPrediction': self._safe_count('core.BettingPrediction'),
            'ArbitrageOpportunity': self._safe_count('core.ArbitrageOpportunity'),
        }

        # Users
        stats['users'] = {
            'User': self._safe_count('auth.User'),
        }

        # Filter out None values
        for category in stats:
            stats[category] = {k: v for k, v in stats[category].items() if v is not None}

        # Output
        if output_json:
            self.stdout.write(json.dumps(stats, indent=2, default=str))
        else:
            self._print_formatted(stats)

    def _print_formatted(self, stats):
        """Print formatted output"""
        self.stdout.write(f"\n{'='*70}")
        self.stdout.write("DATABASE HEALTH SNAPSHOT")
        self.stdout.write(f"{'='*70}\n")

        for category, data in stats.items():
            if not data:
                continue

            self.stdout.write(self.style.HTTP_INFO(f"\n=== {category.upper()} ==="))

            for key, value in data.items():
                if isinstance(value, dict):
                    self.stdout.write(f"  {key}:")
                    for k, v in sorted(value.items()):
                        self.stdout.write(f"    {k}: {v}")
                else:
                    # Highlight zeros
                    if value == 0:
                        self.stdout.write(self.style.WARNING(f"  {key}: {value} ⚠️"))
                    else:
                        self.stdout.write(f"  {key}: {value}")
