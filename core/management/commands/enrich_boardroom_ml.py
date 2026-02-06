"""
Backfill ML predictions for boardroom attention items.

Session 954: Content-aware ML predictions.

Usage:
    python manage.py enrich_boardroom_ml --pending     # Enrich pending items only
    python manage.py enrich_boardroom_ml --all         # Enrich all items without predictions
    python manage.py enrich_boardroom_ml --stats       # Show prediction accuracy stats
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Backfill ML predictions for boardroom attention items'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pending',
            action='store_true',
            help='Only enrich pending items',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Enrich all items without predictions',
        )
        parser.add_argument(
            '--stats',
            action='store_true',
            help='Show ML prediction accuracy stats',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username to process (default: all users)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum items to process per user (default: 100)',
        )

    def handle(self, *args, **options):
        from core.services.boardroom_ml_service import get_boardroom_ml_service
        from core.models_human_interface import HumanAttentionItem

        User = get_user_model()
        service = get_boardroom_ml_service()

        # Get users to process
        if options['user']:
            users = User.objects.filter(username=options['user'])
            if not users.exists():
                self.stdout.write(self.style.ERROR(f"User '{options['user']}' not found"))
                return
        else:
            # Get users with attention items
            user_ids = HumanAttentionItem.objects.values_list('user_id', flat=True).distinct()
            users = User.objects.filter(pk__in=user_ids)

        if options['stats']:
            self._show_stats(users, service)
            return

        total_enriched = 0
        total_failed = 0

        for user in users:
            self.stdout.write(f"\nProcessing {user.username}...")

            if options['pending']:
                items = HumanAttentionItem.objects.filter(
                    user=user,
                    status__in=['pending', 'viewed'],
                    ml_prediction__isnull=True
                )[:options['limit']]
            elif options['all']:
                items = HumanAttentionItem.objects.filter(
                    user=user,
                    ml_prediction__isnull=True
                )[:options['limit']]
            else:
                # Default: pending items without predictions
                items = HumanAttentionItem.objects.filter(
                    user=user,
                    status__in=['pending', 'viewed'],
                    ml_prediction__isnull=True
                )[:options['limit']]

            for item in items:
                if service.enrich_item_with_prediction(item):
                    prediction = item.ml_prediction.get('prediction', 'unknown')
                    confidence = item.ml_confidence or 0
                    self.stdout.write(
                        f"  {item.title[:50]}... -> {prediction} ({confidence:.0%})"
                    )
                    total_enriched += 1
                else:
                    self.stdout.write(
                        self.style.WARNING(f"  {item.title[:50]}... -> FAILED")
                    )
                    total_failed += 1

        self.stdout.write(
            self.style.SUCCESS(f"\n\nComplete: {total_enriched} enriched, {total_failed} failed")
        )

    def _show_stats(self, users, service):
        """Show ML prediction accuracy statistics."""
        from core.models_human_interface import HumanAttentionItem

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("BOARDROOM ML PREDICTION ACCURACY")
        self.stdout.write("=" * 60)

        for user in users:
            summary = service.get_recommendation_summary(user)

            self.stdout.write(f"\n{user.username}:")

            if summary['accuracy'] is not None:
                accuracy_pct = summary['accuracy'] * 100
                color = self.style.SUCCESS if accuracy_pct >= 70 else (
                    self.style.WARNING if accuracy_pct >= 50 else self.style.ERROR
                )
                self.stdout.write(
                    color(f"  Accuracy: {accuracy_pct:.1f}% "
                          f"({summary['correct_predictions']}/{summary['total_predictions']})")
                )
            else:
                self.stdout.write(f"  {summary['message']}")

            # Show decision breakdown
            decisions = HumanAttentionItem.objects.filter(
                user=user,
                decision__isnull=False
            ).values('decision').order_by('decision')

            decision_counts = {}
            for d in decisions:
                decision_counts[d['decision']] = decision_counts.get(d['decision'], 0) + 1

            if decision_counts:
                self.stdout.write(f"  Decisions: {decision_counts}")

        self.stdout.write("\n" + "=" * 60)
