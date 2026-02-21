"""
Session 1062: Re-score opportunities stuck at match_score=50.

11,513 opportunities were created with default quality_score=0.5 (→ match_score=50)
because the heuristic scoring function didn't exist yet. This command re-scores them
using actual attributes from their metadata.raw_data.

Usage:
    python manage.py rescore_opportunities              # Dry run (shows distribution)
    python manage.py rescore_opportunities --apply       # Apply changes
    python manage.py rescore_opportunities --apply --batch-size=500
"""

import logging
from collections import Counter
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


def _compute_score_from_metadata(opp) -> int:
    """
    Compute a differentiated match_score (0-100) from opportunity attributes.

    Uses metadata.raw_data (spider source data) and model fields to derive
    a score based on real signals instead of the static default 50.
    """
    md = opp.metadata or {}
    raw = md.get('raw_data', {})

    score = 0.35  # Base

    # ── Budget / salary signals (+0.15) ──
    has_salary = bool(raw.get('salary_min') or raw.get('salary_max'))
    has_budget = bool(raw.get('budget'))
    if has_salary or has_budget:
        score += 0.15
    elif opp.potential_revenue and float(opp.potential_revenue) > 0:
        score += 0.10

    # ── Description quality (+0.10) ──
    desc = opp.description or ''
    if len(desc) > 200:
        score += 0.10
    elif len(desc) > 50:
        score += 0.05

    # ── Skills / tags (+0.10) ──
    tags = raw.get('tags', raw.get('skills', raw.get('skills_required', [])))
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]
    if isinstance(tags, list) and len(tags) >= 3:
        score += 0.10
    elif isinstance(tags, list) and len(tags) >= 1:
        score += 0.05

    # ── Requirements from model field (+0.05) ──
    reqs = opp.requirements or []
    if isinstance(reqs, list) and len(reqs) >= 2:
        score += 0.05

    # ── Company name present (+0.05) — indicates legitimate posting ──
    if raw.get('company') and raw['company'].strip():
        score += 0.05

    # ── Has application URL (+0.05) — actionable ──
    if raw.get('application_url') or raw.get('url'):
        score += 0.05

    # ── Location specified (+0.03) ──
    location = raw.get('location', '')
    if location and location.strip() and location.lower() != 'remote':
        score += 0.03

    # ── ML analysis available (+0.02) — system already evaluated it ──
    analysis = md.get('analysis', {})
    ml_score = analysis.get('ml_score', {})
    fit = ml_score.get('fit_score')
    if fit and fit != 0.64:  # 0.64 is the default that all got
        # If ML actually differentiated, use it as a boost
        score += 0.05 * (fit - 0.5)  # Small ML adjustment

    return max(1, min(100, int(score * 100)))


class Command(BaseCommand):
    help = 'Re-score opportunities stuck at match_score=50 using heuristic scoring'

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Actually update scores (default is dry-run)',
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

    def handle(self, *args, **options):
        from core.models_unified_system import Opportunity

        apply = options['apply']
        batch_size = options['batch_size']
        target_score = options['score']

        qs = Opportunity.objects.filter(match_score=target_score)
        total = qs.count()

        self.stdout.write(f"\nFound {total} opportunities with match_score={target_score}")

        if total == 0:
            self.stdout.write("Nothing to re-score.")
            return

        # Score distribution preview
        score_dist = Counter()
        updated = 0
        batch = []

        for i, opp in enumerate(qs.iterator(chunk_size=batch_size)):
            new_score = _compute_score_from_metadata(opp)
            score_dist[new_score] += 1

            if apply and new_score != target_score:
                opp.match_score = new_score
                batch.append(opp)
                updated += 1

                if len(batch) >= batch_size:
                    Opportunity.objects.bulk_update(batch, ['match_score'])
                    self.stdout.write(f"  Updated batch: {updated}/{total}")
                    batch = []

            if (i + 1) % 2000 == 0:
                self.stdout.write(f"  Processed {i + 1}/{total}...")

        # Flush remaining
        if apply and batch:
            Opportunity.objects.bulk_update(batch, ['match_score'])

        # Print distribution
        self.stdout.write(f"\n{'=' * 50}")
        self.stdout.write(f"Score distribution ({'APPLIED' if apply else 'DRY RUN'}):")
        self.stdout.write(f"{'=' * 50}")

        # Group into buckets for readability
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

        self.stdout.write(f"\nTotal: {total}")
        if apply:
            self.stdout.write(self.style.SUCCESS(f"Updated: {updated} opportunities"))
        else:
            would_change = sum(c for s, c in score_dist.items() if s != target_score)
            self.stdout.write(f"Would change: {would_change} opportunities")
            self.stdout.write("Run with --apply to update.")
