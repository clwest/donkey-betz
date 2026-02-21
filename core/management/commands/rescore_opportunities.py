"""
Re-score opportunities using the unified opportunity scorer.

Replaces the old hardcoded freelance-only scoring with type-aware scoring
that differentiates freelance, sports_betting, content, trading, and consulting.

Usage:
    python manage.py rescore_opportunities              # Dry run (shows distribution)
    python manage.py rescore_opportunities --apply       # Apply changes
    python manage.py rescore_opportunities --apply --retype  # Also update opportunity_type
    python manage.py rescore_opportunities --apply --batch-size=500
"""

import logging
from collections import Counter
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Re-score opportunities using unified type-aware scoring'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Actually update scores (default is dry-run)',
        )
        parser.add_argument(
            '--retype',
            action='store_true',
            help='Also update opportunity_type if inferred type differs',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Batch size for updates (default: 1000)',
        )
        parser.add_argument(
            '--score',
            type=int,
            default=50,
            help='Target score to re-score (default: 50)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            dest='rescore_all',
            help='Re-score ALL opportunities, not just those at --score',
        )

    def handle(self, *args, **options):
        from core.models_unified_system import Opportunity
        from core.services.opportunity_scorer import score_opportunity, infer_opportunity_type

        apply = options['apply']
        retype = options['retype']
        batch_size = options['batch_size']
        target_score = options['score']
        rescore_all = options['rescore_all']

        if rescore_all:
            qs = Opportunity.objects.all()
        else:
            qs = Opportunity.objects.filter(match_score=target_score)
        total = qs.count()

        label = 'all' if rescore_all else f'match_score={target_score}'
        self.stdout.write(f"\nFound {total} opportunities ({label})")

        if total == 0:
            self.stdout.write("Nothing to re-score.")
            return

        # Distributions
        score_dist = Counter()
        type_dist = Counter()
        retype_count = 0
        updated = 0
        batch = []
        update_fields = ['match_score']
        if retype:
            update_fields.append('opportunity_type')

        for i, opp in enumerate(qs.iterator(chunk_size=batch_size)):
            md = opp.metadata or {}
            raw = md.get('raw_data', {})

            result = score_opportunity(
                raw_data=raw,
                spider_name=opp.source or '',
                title=opp.title or '',
                description=opp.description or '',
            )

            new_score = result['score_0_100']
            inferred_type = result['opportunity_type']

            score_dist[new_score] += 1
            type_dist[inferred_type] += 1

            changed = False

            if apply and (rescore_all or new_score != target_score):
                opp.match_score = new_score
                changed = True

            if retype and apply and opp.opportunity_type != inferred_type:
                opp.opportunity_type = inferred_type
                retype_count += 1
                changed = True

            if changed:
                batch.append(opp)
                updated += 1

                if len(batch) >= batch_size:
                    Opportunity.objects.bulk_update(batch, update_fields)
                    self.stdout.write(f"  Updated batch: {updated}/{total}")
                    batch = []

            if (i + 1) % 2000 == 0:
                self.stdout.write(f"  Processed {i + 1}/{total}...")

        # Flush remaining
        if apply and batch:
            Opportunity.objects.bulk_update(batch, update_fields)

        # Print score distribution
        self.stdout.write(f"\n{'=' * 50}")
        self.stdout.write(f"Score distribution ({'APPLIED' if apply else 'DRY RUN'}):")
        self.stdout.write(f"{'=' * 50}")

        buckets = {
            '90-100': 0, '80-89': 0, '70-79': 0, '60-69': 0,
            '50-59': 0, '40-49': 0, '30-39': 0, '20-29': 0, '1-19': 0,
        }
        for score, count in score_dist.items():
            if score >= 90:
                buckets['90-100'] += count
            elif score >= 80:
                buckets['80-89'] += count
            elif score >= 70:
                buckets['70-79'] += count
            elif score >= 60:
                buckets['60-69'] += count
            elif score >= 50:
                buckets['50-59'] += count
            elif score >= 40:
                buckets['40-49'] += count
            elif score >= 30:
                buckets['30-39'] += count
            elif score >= 20:
                buckets['20-29'] += count
            else:
                buckets['1-19'] += count

        for bucket, count in buckets.items():
            bar = '#' * min(50, count // max(1, total // 50))
            pct = count / total * 100
            self.stdout.write(f"  {bucket:>6}: {count:>6} ({pct:5.1f}%) {bar}")

        # Top 10 exact scores
        self.stdout.write(f"\nTop 10 exact scores:")
        for score, count in sorted(score_dist.items(), key=lambda x: -x[1])[:10]:
            self.stdout.write(f"  {score}: {count}")

        # Type distribution
        self.stdout.write(f"\n{'=' * 50}")
        self.stdout.write(f"Type distribution:")
        self.stdout.write(f"{'=' * 50}")
        for opp_type, count in sorted(type_dist.items(), key=lambda x: -x[1]):
            pct = count / total * 100
            self.stdout.write(f"  {opp_type:>20}: {count:>6} ({pct:5.1f}%)")

        self.stdout.write(f"\nTotal: {total}")
        if apply:
            self.stdout.write(self.style.SUCCESS(f"Updated: {updated} opportunities"))
            if retype:
                self.stdout.write(self.style.SUCCESS(f"Retyped: {retype_count} opportunities"))
        else:
            would_change = sum(c for s, c in score_dist.items() if s != target_score)
            self.stdout.write(f"Would change score: {would_change} opportunities")
            if not retype:
                self.stdout.write("Tip: add --retype to also update opportunity_type")
            self.stdout.write("Run with --apply to update.")
