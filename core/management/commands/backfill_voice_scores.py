"""
Session 784: Backfill Voice Scores for Existing Episodes

Management command to score existing ChannelEpisodes with VoiceCriticAgent.

This runs the "Voice Critic, not Voice Editor" pattern on historical content:
- Scores distinctiveness, specificity, opinion strength
- Classifies intent type (visionary, technical_deep_dive, etc.)
- Flags generic content
- Does NOT edit content - only scores

Usage:
    # Score all unscored episodes (default limit: 50)
    python manage.py backfill_voice_scores

    # Score up to 100 episodes
    python manage.py backfill_voice_scores --limit 100

    # Score all episodes (no limit)
    python manage.py backfill_voice_scores --all

    # Only score episodes with at least 500 chars
    python manage.py backfill_voice_scores --min-length 500

    # Dry run - show what would be scored
    python manage.py backfill_voice_scores --dry-run
"""

import logging
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.db.models.functions import Length

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Backfill voice critique scores for existing ChannelEpisodes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum episodes to score (default: 50)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Score all unscored episodes (ignores --limit)'
        )
        parser.add_argument(
            '--min-length',
            type=int,
            default=100,
            help='Minimum script length to consider (default: 100 chars)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be scored without actually scoring'
        )
        parser.add_argument(
            '--channel-id',
            type=str,
            help='Only score episodes from this channel UUID'
        )

    def handle(self, *args, **options):
        from core.models_autonomous_studio import ChannelEpisode
        from core.agents.content.voice_critic_agent import get_voice_critic_agent

        limit = options['limit']
        score_all = options['all']
        min_length = options['min_length']
        dry_run = options['dry_run']
        channel_id = options.get('channel_id')

        self.stdout.write(
            self.style.NOTICE(
                f"🎭 Voice Critic Backfill - Session 784"
            )
        )
        self.stdout.write(f"   Limit: {'ALL' if score_all else limit}")
        self.stdout.write(f"   Min Length: {min_length} chars")
        self.stdout.write(f"   Dry Run: {dry_run}")
        if channel_id:
            self.stdout.write(f"   Channel: {channel_id}")
        self.stdout.write("")

        # Build query for unscored episodes
        queryset = ChannelEpisode.objects.filter(
            voice_critique_completed=False
        ).exclude(
            Q(script__isnull=True) | Q(script='')
        ).annotate(
            script_length=Length('script')
        ).filter(
            script_length__gte=min_length
        )

        if channel_id:
            queryset = queryset.filter(channel_id=channel_id)

        queryset = queryset.order_by('-created_at')

        if not score_all:
            queryset = queryset[:limit]

        episodes = list(queryset)
        total = len(episodes)

        self.stdout.write(f"Found {total} unscored episodes to process")
        self.stdout.write("")

        if total == 0:
            self.stdout.write(self.style.SUCCESS("✅ No episodes need scoring"))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - Episodes that would be scored:"))
            for i, ep in enumerate(episodes[:20], 1):
                self.stdout.write(
                    f"  {i}. {ep.title[:50]}... ({ep.script_length} chars)"
                )
            if total > 20:
                self.stdout.write(f"  ... and {total - 20} more")
            return

        # Score episodes
        agent = get_voice_critic_agent()
        scored = 0
        failed = 0

        for i, episode in enumerate(episodes, 1):
            self.stdout.write(f"[{i}/{total}] Scoring: {episode.title[:40]}...", ending='')

            try:
                result = agent.execute(
                    task=f"Score voice quality for: {episode.title}",
                    context={
                        'content': episode.script,
                        'title': episode.title,
                        'content_type': 'blog_post',
                    },
                    scifi_context={},
                    spider_context={}
                )

                if result.success:
                    scores = result.data.get('voice_scores', {})

                    # Update episode
                    episode.distinctiveness_score = scores.get('distinctiveness_score', 0)
                    episode.specificity_score = scores.get('specificity_score', 0)
                    episode.opinion_strength_score = scores.get('opinion_strength_score', 0)
                    episode.generic_flag = scores.get('generic_flag', False)
                    episode.intent_type = scores.get('intent_type', '')
                    episode.voice_critique_completed = True
                    episode.save(update_fields=[
                        'distinctiveness_score', 'specificity_score',
                        'opinion_strength_score', 'generic_flag',
                        'intent_type', 'voice_critique_completed'
                    ])

                    scored += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f" ✓ D={scores.get('distinctiveness_score')}, "
                            f"S={scores.get('specificity_score')}, "
                            f"O={scores.get('opinion_strength_score')}, "
                            f"G={scores.get('generic_flag')}, "
                            f"I={scores.get('intent_type', '')[:10]}"
                        )
                    )
                else:
                    failed += 1
                    self.stdout.write(
                        self.style.ERROR(f" ✗ {result.error[:50]}")
                    )

            except Exception as e:
                failed += 1
                self.stdout.write(
                    self.style.ERROR(f" ✗ Exception: {str(e)[:50]}")
                )

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"✅ Backfill complete!"))
        self.stdout.write(f"   Scored: {scored}/{total}")
        self.stdout.write(f"   Failed: {failed}/{total}")

        # Show score distribution
        if scored > 0:
            self.stdout.write("")
            self.stdout.write("Score Distribution (scored episodes):")

            scored_episodes = ChannelEpisode.objects.filter(
                voice_critique_completed=True,
                id__in=[ep.id for ep in episodes if ep.voice_critique_completed]
            )

            if scored_episodes.exists():
                from django.db.models import Avg
                avgs = scored_episodes.aggregate(
                    avg_dist=Avg('distinctiveness_score'),
                    avg_spec=Avg('specificity_score'),
                    avg_opin=Avg('opinion_strength_score'),
                )
                self.stdout.write(
                    f"   Avg Distinctiveness: {avgs['avg_dist']:.1f}"
                )
                self.stdout.write(
                    f"   Avg Specificity: {avgs['avg_spec']:.1f}"
                )
                self.stdout.write(
                    f"   Avg Opinion Strength: {avgs['avg_opin']:.1f}"
                )

                generic_count = scored_episodes.filter(generic_flag=True).count()
                self.stdout.write(
                    f"   Generic Content: {generic_count}/{scored} ({generic_count/scored*100:.1f}%)"
                )
