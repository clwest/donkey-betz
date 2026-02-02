"""
Session 913: Backfill Initiative Signal Intelligence Links

Management command to link existing initiatives to SignalClusters and AutoTopics
based on timing and content matching.

Usage:
    python manage.py backfill_initiative_signals --dry-run
    python manage.py backfill_initiative_signals --fix
"""

import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Backfill Initiative signal_cluster and auto_topic links'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be linked without making changes'
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Actually update the initiatives'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of initiatives to process (default: 100)'
        )

    def handle(self, *args, **options):
        from core.models_document_registry import Initiative
        from core.models_signal_intelligence import SignalCluster, AutoTopic

        dry_run = options['dry_run']
        fix = options['fix']
        limit = options['limit']

        if not dry_run and not fix:
            self.stdout.write(self.style.WARNING(
                'Please specify --dry-run or --fix'
            ))
            return

        self.stdout.write(self.style.HTTP_INFO('=' * 60))
        self.stdout.write(self.style.HTTP_INFO('Session 913: Backfill Initiative Signals'))
        self.stdout.write(self.style.HTTP_INFO('=' * 60))

        # Get initiatives without signal links
        unlinked = Initiative.objects.filter(
            signal_cluster__isnull=True,
            auto_topic__isnull=True
        ).order_by('-created_at')[:limit]

        self.stdout.write(f"\nFound {unlinked.count()} initiatives without signal links")

        # Get all signal clusters and auto topics
        clusters = list(SignalCluster.objects.all().order_by('-detected_at'))
        topics = list(AutoTopic.objects.all().order_by('-created_at'))

        self.stdout.write(f"Available SignalClusters: {len(clusters)}")
        self.stdout.write(f"Available AutoTopics: {len(topics)}")

        linked_count = 0
        cluster_links = 0
        topic_links = 0

        for init in unlinked:
            matched_cluster = None
            matched_topic = None

            # Strategy 1: Match by HiveMind session source_decision_id
            if init.source_decision_id:
                from core.models import HiveMindSession
                try:
                    session = HiveMindSession.objects.get(id=init.source_decision_id)
                    if session.signal_cluster:
                        matched_cluster = session.signal_cluster
                    if session.auto_topic:
                        matched_topic = session.auto_topic
                except HiveMindSession.DoesNotExist:
                    pass

            # Strategy 2: Match by timing (cluster detected within 1 hour of initiative creation)
            if not matched_cluster:
                for cluster in clusters:
                    time_diff = abs((init.created_at - cluster.detected_at).total_seconds())
                    if time_diff < 3600:  # Within 1 hour
                        # Check for keyword overlap
                        init_words = set(init.name.lower().split())
                        cluster_keywords = set(k.lower() for k in cluster.keywords)
                        if init_words & cluster_keywords:  # Any overlap
                            matched_cluster = cluster
                            break

            # Strategy 3: Match AutoTopic by name similarity
            if not matched_topic:
                init_name_lower = init.name.lower()
                for topic in topics:
                    if topic.name.lower() in init_name_lower or init_name_lower in topic.name.lower():
                        matched_topic = topic
                        break
                    # Check for significant word overlap
                    topic_words = set(topic.name.lower().split())
                    init_words = set(init_name_lower.split())
                    overlap = topic_words & init_words
                    if len(overlap) >= 2:  # At least 2 words match
                        matched_topic = topic
                        break

            if matched_cluster or matched_topic:
                linked_count += 1
                if matched_cluster:
                    cluster_links += 1
                if matched_topic:
                    topic_links += 1

                self.stdout.write(f"\n{'[DRY-RUN] ' if dry_run else ''}Initiative: {init.name[:50]}...")
                if matched_cluster:
                    self.stdout.write(f"  → SignalCluster: {matched_cluster.name[:50]}")
                if matched_topic:
                    self.stdout.write(f"  → AutoTopic: {matched_topic.name[:50]}")

                if fix:
                    if matched_cluster:
                        init.signal_cluster = matched_cluster
                    if matched_topic:
                        init.auto_topic = matched_topic
                    init.save(update_fields=['signal_cluster', 'auto_topic'])

        # Summary
        self.stdout.write(f"\n{'=' * 60}")
        self.stdout.write(self.style.HTTP_INFO('SUMMARY'))
        self.stdout.write(f"{'=' * 60}")
        self.stdout.write(f"Initiatives processed: {unlinked.count()}")
        self.stdout.write(f"Initiatives linked: {linked_count}")
        self.stdout.write(f"  - With SignalCluster: {cluster_links}")
        self.stdout.write(f"  - With AutoTopic: {topic_links}")

        if fix:
            self.stdout.write(self.style.SUCCESS(f"\n✅ Updated {linked_count} initiatives"))
        else:
            self.stdout.write(self.style.WARNING(
                f"\n⚠️ DRY RUN - Would link {linked_count} initiatives"
            ))
            self.stdout.write(self.style.WARNING("Run with --fix to apply changes"))
