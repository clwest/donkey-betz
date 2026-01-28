"""
Session 855: Aggressive dream backlog triage management command.

The existing triage_dreams action is too conservative for large backlogs.
This command provides more aggressive options for clearing dream backlogs.

Usage:
    # See current backlog status
    python manage.py triage_dream_backlog --status

    # Preview what would be triaged (dry run)
    python manage.py triage_dream_backlog --dry-run

    # Triage with default aggressive settings
    python manage.py triage_dream_backlog

    # Triage with custom thresholds
    python manage.py triage_dream_backlog --max-age-hours 48 --min-score 0.5
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.db.models import Avg, Count


class Command(BaseCommand):
    help = 'Aggressively triage dream backlog to prevent idea rot'

    def add_arguments(self, parser):
        parser.add_argument(
            '--status',
            action='store_true',
            help='Just show current backlog status without triaging',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be triaged without making changes',
        )
        parser.add_argument(
            '--max-age-hours',
            type=int,
            default=48,
            help='Archive dreams older than this (default: 48 hours - the freshness threshold)',
        )
        parser.add_argument(
            '--min-score',
            type=float,
            default=0.6,
            help='Minimum composite score to keep (default: 0.6)',
        )
        parser.add_argument(
            '--boardroom-threshold',
            type=float,
            default=0.7,
            help='Minimum score to promote to Boardroom (default: 0.7)',
        )
        parser.add_argument(
            '--max-process',
            type=int,
            default=200,
            help='Maximum dreams to process (default: 200)',
        )

    def handle(self, *args, **options):
        from core.models_unified_system import AgentDream

        now = timezone.now()

        # Get backlog stats
        pending_dreams = AgentDream.objects.filter(
            promoted_to_decision=False,
            shown_to_user=False
        )
        total_pending = pending_dreams.count()

        if total_pending == 0:
            self.stdout.write(self.style.SUCCESS('No pending dreams in backlog'))
            return

        # Get oldest pending
        oldest = pending_dreams.order_by('dreamed_at').first()
        oldest_age_hours = (now - oldest.dreamed_at).total_seconds() / 3600 if oldest else 0

        # Get score distribution
        score_stats = pending_dreams.aggregate(
            avg_score=Avg('composite_score'),
            avg_actionability=Avg('actionability_score'),
            avg_creativity=Avg('creativity_score'),
        )

        # Count by score ranges
        high_score = pending_dreams.filter(composite_score__gte=0.7).count()
        medium_score = pending_dreams.filter(composite_score__gte=0.5, composite_score__lt=0.7).count()
        low_score = pending_dreams.filter(composite_score__lt=0.5).count()

        # Show status
        self.stdout.write('\n=== Dream Backlog Status ===')
        self.stdout.write(f'Total pending: {total_pending}')
        self.stdout.write(f'Oldest pending: {oldest_age_hours:.1f} hours')
        self.stdout.write(f'Average composite score: {score_stats["avg_score"]:.2f}' if score_stats["avg_score"] else 'N/A')
        self.stdout.write(f'Average actionability: {score_stats["avg_actionability"]:.2f}' if score_stats["avg_actionability"] else 'N/A')
        self.stdout.write(f'\nScore distribution:')
        self.stdout.write(f'  High (>=0.7): {high_score}')
        self.stdout.write(f'  Medium (0.5-0.7): {medium_score}')
        self.stdout.write(f'  Low (<0.5): {low_score}')

        if options['status']:
            return

        # Triage parameters
        max_age_hours = options['max_age_hours']
        min_score = options['min_score']
        boardroom_threshold = options['boardroom_threshold']
        max_process = options['max_process']
        dry_run = options['dry_run']

        self.stdout.write(f'\n=== Triage Settings ===')
        self.stdout.write(f'Max age before archive: {max_age_hours} hours')
        self.stdout.write(f'Min score to keep: {min_score}')
        self.stdout.write(f'Boardroom threshold: {boardroom_threshold}')
        self.stdout.write(f'Max to process: {max_process}')
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - no changes will be made'))

        # Calculate cutoff
        age_cutoff = now - timedelta(hours=max_age_hours)

        # Categorize dreams
        results = {
            'to_boardroom': [],
            'to_archive_stale': [],
            'to_archive_low_score': [],
            'keeping': [],
        }

        dreams_to_process = pending_dreams.select_related('agent').order_by('-composite_score')[:max_process]

        for dream in dreams_to_process:
            age_hours = (now - dream.dreamed_at).total_seconds() / 3600

            # High score + actionable -> Boardroom
            if dream.composite_score >= boardroom_threshold and dream.actionability_score >= 0.5:
                results['to_boardroom'].append({
                    'id': str(dream.id),
                    'title': dream.title[:40] if dream.title else 'Untitled',
                    'score': dream.composite_score,
                    'agent': dream.agent.name if dream.agent else 'Unknown',
                    'age_hours': age_hours,
                })
            # Stale (past max age)
            elif dream.dreamed_at < age_cutoff:
                results['to_archive_stale'].append({
                    'id': str(dream.id),
                    'title': dream.title[:40] if dream.title else 'Untitled',
                    'score': dream.composite_score,
                    'age_hours': age_hours,
                    'reason': f'Stale ({age_hours:.0f}h > {max_age_hours}h threshold)',
                })
            # Low score
            elif dream.composite_score < min_score:
                results['to_archive_low_score'].append({
                    'id': str(dream.id),
                    'title': dream.title[:40] if dream.title else 'Untitled',
                    'score': dream.composite_score,
                    'age_hours': age_hours,
                    'reason': f'Low score ({dream.composite_score:.2f} < {min_score})',
                })
            # Keep for later
            else:
                results['keeping'].append({
                    'id': str(dream.id),
                    'title': dream.title[:40] if dream.title else 'Untitled',
                    'score': dream.composite_score,
                    'age_hours': age_hours,
                })

        # Show what will happen
        self.stdout.write(f'\n=== Triage Plan ===')
        self.stdout.write(f'Promoting to Boardroom: {len(results["to_boardroom"])}')
        for d in results['to_boardroom'][:5]:
            self.stdout.write(f'  + [{d["agent"]}] {d["title"]} (score: {d["score"]:.2f})')
        if len(results['to_boardroom']) > 5:
            self.stdout.write(f'  ... and {len(results["to_boardroom"]) - 5} more')

        self.stdout.write(f'\nArchiving (stale): {len(results["to_archive_stale"])}')
        for d in results['to_archive_stale'][:5]:
            self.stdout.write(f'  - {d["title"]} ({d["reason"]})')
        if len(results['to_archive_stale']) > 5:
            self.stdout.write(f'  ... and {len(results["to_archive_stale"]) - 5} more')

        self.stdout.write(f'\nArchiving (low score): {len(results["to_archive_low_score"])}')
        for d in results['to_archive_low_score'][:5]:
            self.stdout.write(f'  - {d["title"]} ({d["reason"]})')
        if len(results['to_archive_low_score']) > 5:
            self.stdout.write(f'  ... and {len(results["to_archive_low_score"]) - 5} more')

        self.stdout.write(f'\nKeeping for later review: {len(results["keeping"])}')

        if dry_run:
            self.stdout.write(self.style.WARNING('\nDry run complete - no changes made'))
            return

        # Execute triage
        self.stdout.write(f'\n=== Executing Triage ===')

        # Promote to boardroom
        boardroom_ids = [d['id'] for d in results['to_boardroom']]
        if boardroom_ids:
            AgentDream.objects.filter(id__in=boardroom_ids).update(
                promoted_to_decision=True,
                promoted_at=now,
                decision_outcome='pending'
            )
            self.stdout.write(self.style.SUCCESS(f'Promoted {len(boardroom_ids)} to Boardroom'))

        # Archive stale
        stale_ids = [d['id'] for d in results['to_archive_stale']]
        if stale_ids:
            AgentDream.objects.filter(id__in=stale_ids).update(
                shown_to_user=True,
                shown_at=now,
                user_feedback='auto_archived_stale_backlog_triage'
            )
            self.stdout.write(self.style.SUCCESS(f'Archived {len(stale_ids)} stale dreams'))

        # Archive low score
        low_ids = [d['id'] for d in results['to_archive_low_score']]
        if low_ids:
            AgentDream.objects.filter(id__in=low_ids).update(
                shown_to_user=True,
                shown_at=now,
                user_feedback='auto_archived_low_score_backlog_triage'
            )
            self.stdout.write(self.style.SUCCESS(f'Archived {len(low_ids)} low score dreams'))

        total_triaged = len(boardroom_ids) + len(stale_ids) + len(low_ids)
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Total triaged: {total_triaged}'))
        self.stdout.write(f'Remaining in backlog: {total_pending - total_triaged + len(results["keeping"])}')
