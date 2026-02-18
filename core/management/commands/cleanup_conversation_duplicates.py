"""
Session 1032: Detect and clean up fuzzy-duplicate AgentConversation records.

Problem: The system spawns the same topic as different conversation types
(Discussion, Panel, brainstorm, devils_advocate) with different agent pairs,
each concluding with nearly identical boilerplate. This creates 12 copies
of "Analyze competitor content" that never build on each other.

This command uses the DeduplicationService's Jaccard similarity to cluster
conversations by normalized topic and delete lower-quality duplicates.

Usage:
    # Dry run - show duplicate clusters (default)
    python manage.py cleanup_conversation_duplicates

    # Actually delete duplicates
    python manage.py cleanup_conversation_duplicates --fix

    # Adjust similarity threshold (0.0-1.0, default 0.85)
    python manage.py cleanup_conversation_duplicates --threshold=0.8

    # Change lookback window (default 168 hours = 7 days)
    python manage.py cleanup_conversation_duplicates --hours=336
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Detect and clean up fuzzy-duplicate AgentConversation records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Actually delete duplicates (default is dry run)',
        )
        parser.add_argument(
            '--threshold',
            type=float,
            default=0.85,
            help='Jaccard similarity threshold 0.0-1.0 (default: 0.85)',
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=168,
            help='Lookback window in hours (default: 168 = 7 days)',
        )

    def handle(self, *args, **options):
        from core.services.deduplication_service import get_deduplication_service

        fix = options['fix']
        threshold = options['threshold']
        hours = options['hours']

        self.stdout.write(self.style.NOTICE(
            f"{'FIXING' if fix else 'DRY RUN'}: Finding fuzzy-duplicate conversations "
            f"(threshold: {threshold}, lookback: {hours}h)"
        ))

        dedup_svc = get_deduplication_service()
        result = dedup_svc.cleanup_fuzzy_conversation_duplicates(
            dry_run=not fix,
            hours=hours,
            threshold=threshold,
        )

        self.stdout.write(f"Scanned: {result['conversations_scanned']} conversations")
        self.stdout.write(f"Clusters found: {result['clusters_found']}")

        for i, cluster in enumerate(result.get('clusters', []), 1):
            self.stdout.write(self.style.WARNING(
                f"\n--- Cluster {i} ({cluster['duplicates'] + 1} conversations) ---"
            ))
            self.stdout.write(self.style.SUCCESS(f"  KEEP: {cluster['keeper']}"))
            for topic in cluster['sample_topics']:
                self.stdout.write(f"  DELETE: {topic}")
            if cluster['duplicates'] > len(cluster['sample_topics']):
                self.stdout.write(
                    f"  ... and {cluster['duplicates'] - len(cluster['sample_topics'])} more"
                )

        self.stdout.write(self.style.NOTICE(f"\n--- Summary ---"))
        action = 'Deleted' if fix else 'Would delete'
        count = result['records_deleted'] if fix else result['records_to_delete']
        self.stdout.write(f"{action}: {count} duplicate conversations")

        if not fix and result['records_to_delete'] > 0:
            self.stdout.write(self.style.WARNING(
                "\nRun with --fix to actually delete duplicates."
            ))
