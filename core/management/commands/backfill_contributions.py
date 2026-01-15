"""
Backfill AgentContribution Records from Historical Content

Session 757: Create AgentContribution records for existing ImageHistory and VideoHistory
that don't have contribution tracking yet.

This ensures the Live Feed shows all historical agent activity, not just new content.
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from content.models import ImageHistory, VideoHistory
from core.models.agents_registry import AgentContribution, UnifiedAgentTemplate


class Command(BaseCommand):
    help = 'Backfill AgentContribution records from existing ImageHistory and VideoHistory'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without creating records'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit number of records to process (default: all)'
        )
        parser.add_argument(
            '--content-type',
            type=str,
            choices=['all', 'images', 'videos'],
            default='all',
            help='Which content type to backfill (default: all)'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        content_type = options['content_type']

        self.stdout.write(self.style.NOTICE("=" * 60))
        self.stdout.write(self.style.NOTICE("AgentContribution Backfill - Session 757"))
        self.stdout.write(self.style.NOTICE("=" * 60))

        if dry_run:
            self.stdout.write(self.style.WARNING("\nDRY RUN MODE - no records will be created\n"))

        # Get or create default agents for content without agent links
        image_agent = self._get_or_create_agent('image-generation-agent', 'Image Generation Agent', 'content')
        video_agent = self._get_or_create_agent('video-generation-agent', 'Video Generation Agent', 'content')

        created_images = 0
        created_videos = 0
        skipped = 0
        errors = 0

        # Process ImageHistory
        if content_type in ['all', 'images']:
            self.stdout.write(self.style.NOTICE("\n=== Processing ImageHistory ==="))
            created_images, img_skipped, img_errors = self._process_images(
                image_agent, dry_run, limit
            )
            skipped += img_skipped
            errors += img_errors

        # Process VideoHistory
        if content_type in ['all', 'videos']:
            self.stdout.write(self.style.NOTICE("\n=== Processing VideoHistory ==="))
            created_videos, vid_skipped, vid_errors = self._process_videos(
                video_agent, dry_run, limit
            )
            skipped += vid_skipped
            errors += vid_errors

        # Summary
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("Backfill Complete!"))
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(f"  Image contributions created: {created_images}")
        self.stdout.write(f"  Video contributions created: {created_videos}")
        self.stdout.write(f"  Skipped (already had contribution): {skipped}")
        self.stdout.write(f"  Errors: {errors}")

        # Show totals
        total_contributions = AgentContribution.objects.count()
        image_contributions = AgentContribution.objects.filter(image__isnull=False).count()
        video_contributions = AgentContribution.objects.filter(video__isnull=False).count()

        self.stdout.write(f"\nTotal AgentContribution records: {total_contributions}")
        self.stdout.write(f"  With images: {image_contributions}")
        self.stdout.write(f"  With videos: {video_contributions}")

    def _get_or_create_agent(self, name: str, display_name: str, specialization: str) -> UnifiedAgentTemplate:
        """Get or create a UnifiedAgentTemplate for backfill."""
        agent, created = UnifiedAgentTemplate.objects.get_or_create(
            name=name,
            defaults={
                'display_name': display_name,
                'description': f'{display_name} - AI content generation',
                'specialization': specialization,
                'system_prompt': f'Agent for {display_name.lower()}',
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Created agent template: {name}"))
        return agent

    def _process_images(self, default_agent: UnifiedAgentTemplate, dry_run: bool, limit: int | None):
        """Process ImageHistory records that don't have contributions."""
        created = 0
        skipped = 0
        errors = 0

        # Get IDs of images that already have contributions
        existing_image_ids = set(
            AgentContribution.objects.filter(image__isnull=False)
            .values_list('image_id', flat=True)
        )

        # Get images without contributions
        images = ImageHistory.objects.exclude(id__in=existing_image_ids)
        if limit:
            images = images[:limit]

        total = images.count()
        self.stdout.write(f"Found {total} images needing backfill")

        for i, image in enumerate(images, 1):
            if i % 50 == 0:
                self.stdout.write(f"  Progress: {i}/{total}")

            # Use the linked agent if available, otherwise use default
            agent = image.agent if image.agent else default_agent

            if dry_run:
                created += 1
                continue

            try:
                with transaction.atomic():
                    AgentContribution.objects.create(
                        agent=agent,
                        image=image,
                        project=image.project,
                        contribution_type='generation',
                        contribution_role='Primary Creator',
                        contribution_percentage=100,
                        task_description=f'Generated image: {image.filename or image.prompt[:50] if image.prompt else "Unknown"}',
                    )
                    created += 1
            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f"  Error processing image {image.id}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"  Created {created} image contributions"))
        return created, skipped, errors

    def _process_videos(self, default_agent: UnifiedAgentTemplate, dry_run: bool, limit: int | None):
        """Process VideoHistory records that don't have contributions."""
        created = 0
        skipped = 0
        errors = 0

        # Get IDs of videos that already have contributions
        existing_video_ids = set(
            AgentContribution.objects.filter(video__isnull=False)
            .values_list('video_id', flat=True)
        )

        # Get videos without contributions
        videos = VideoHistory.objects.exclude(id__in=existing_video_ids)
        if limit:
            videos = videos[:limit]

        total = videos.count()
        self.stdout.write(f"Found {total} videos needing backfill")

        for i, video in enumerate(videos, 1):
            # Use the linked agent if available, otherwise use default
            agent = video.agent if video.agent else default_agent

            if dry_run:
                created += 1
                continue

            try:
                with transaction.atomic():
                    # VideoHistory uses video_url, not filename
                    description = video.prompt[:50] if video.prompt else video.video_url.split('/')[-1] if video.video_url else 'Unknown'
                    AgentContribution.objects.create(
                        agent=agent,
                        video=video,
                        project=video.project if hasattr(video, 'project') else None,
                        contribution_type='generation',
                        contribution_role='Primary Creator',
                        contribution_percentage=100,
                        task_description=f'Generated video: {description}',
                    )
                    created += 1
            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f"  Error processing video {video.id}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"  Created {created} video contributions"))
        return created, skipped, errors
