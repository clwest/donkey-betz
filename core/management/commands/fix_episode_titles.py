"""
Session 741: Fix generic episode titles

This command regenerates unique titles for all episodes that have generic titles
by analyzing their script content with GPT.
"""

import os
import time
from django.core.management.base import BaseCommand
import openai


class Command(BaseCommand):
    help = 'Fix generic episode titles by generating unique titles from script content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )
        parser.add_argument(
            '--channel',
            type=str,
            help='Only fix episodes for a specific channel name',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of episodes to fix (default: 100)',
        )

    def handle(self, *args, **options):
        from core.models_autonomous_studio import ChannelEpisode, ContentChannel

        dry_run = options['dry_run']
        channel_name = options.get('channel')
        limit = options['limit']

        self.stdout.write(self.style.NOTICE(
            f"Session 741: Fixing generic episode titles (dry_run={dry_run})"
        ))

        # Get episodes with generic titles (containing the full topic_domain pattern)
        episodes = ChannelEpisode.objects.filter(
            script__isnull=False
        ).exclude(script='').select_related('channel')

        if channel_name:
            episodes = episodes.filter(channel__name__icontains=channel_name)

        # Filter to only episodes with generic titles
        generic_episodes = []
        for ep in episodes:
            # Check if title is generic (contains topic_domain or is just the channel name + topic)
            if (
                'Latest' in ep.title and 'Developments' in ep.title or
                'Machine Learning, AI Research' in ep.title or
                'narrative shifts, cultural trends' in ep.title.lower() or
                ep.title == ep.topic or
                len(ep.title) > 80  # Overly long titles are likely generic
            ):
                generic_episodes.append(ep)

        self.stdout.write(f"Found {len(generic_episodes)} episodes with generic titles")

        if not generic_episodes:
            self.stdout.write(self.style.SUCCESS("No generic titles to fix!"))
            return

        # Limit the number of episodes to process
        episodes_to_fix = generic_episodes[:limit]
        self.stdout.write(f"Processing {len(episodes_to_fix)} episodes...")

        # Initialize OpenAI client
        client = openai.OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

        fixed_count = 0
        error_count = 0

        for i, episode in enumerate(episodes_to_fix, 1):
            try:
                self.stdout.write(f"\n[{i}/{len(episodes_to_fix)}] {episode.channel.name}")
                self.stdout.write(f"  Current: {episode.title[:70]}...")

                # Generate new title from script
                title_prompt = f"""Based on this podcast script, generate a short, catchy episode title (max 60 chars).
The title should capture the SPECIFIC topic discussed, not be generic.

Script excerpt:
{episode.script[:1500]}

Reply with ONLY the title, nothing else. Do not include the show name prefix."""

                response = client.chat.completions.create(
                    model="gpt-5-mini",
                    messages=[{"role": "user", "content": title_prompt}],
                    max_completion_tokens=50
                )

                generated_title = response.choices[0].message.content.strip().strip('"\'')

                # Ensure it's not too long
                if len(generated_title) > 60:
                    generated_title = generated_title[:57] + "..."

                new_title = f"{episode.channel.name}: {generated_title}"

                self.stdout.write(f"  New:     {new_title}")

                if not dry_run:
                    episode.title = new_title
                    episode.save(update_fields=['title'])
                    fixed_count += 1
                else:
                    self.stdout.write(self.style.WARNING("  (dry run - not saved)"))
                    fixed_count += 1

                # Rate limit to avoid API throttling
                time.sleep(0.5)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error: {e}"))
                error_count += 1

        self.stdout.write("\n" + "=" * 60)
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"DRY RUN: Would fix {fixed_count} episode titles ({error_count} errors)"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"Fixed {fixed_count} episode titles ({error_count} errors)"
            ))
