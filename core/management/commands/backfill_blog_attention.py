"""
Session 759: Backfill attention items for existing SelfBlog records.

This command creates HumanAttentionItem records for blogs that don't have them,
so they surface in the Human Interface for review.

Usage:
    python manage.py backfill_blog_attention
    python manage.py backfill_blog_attention --limit 100
    python manage.py backfill_blog_attention --dry-run
"""

from django.core.management.base import BaseCommand
from django.db.models import Q


class Command(BaseCommand):
    help = 'Backfill attention items for existing SelfBlog records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of blogs to process (default: all)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )
        parser.add_argument(
            '--quality-score',
            type=int,
            default=75,
            help='Default quality score for backfilled items (default: 75)',
        )

    def handle(self, *args, **options):
        from core.models_unified_system import SelfBlog
        from core.models_human_interface import HumanAttentionItem
        from core.services.human_attention_bridge import HumanAttentionBridge

        limit = options['limit']
        dry_run = options['dry_run']
        quality_score = options['quality_score']

        self.stdout.write(self.style.NOTICE('Scanning for blogs without attention items...'))

        # Get all blog IDs that already have attention items
        existing_content_ids = set(
            HumanAttentionItem.objects.filter(
                item_type='review',
                source_type__startswith='content:blog'
            ).values_list('source_id', flat=True)
        )

        self.stdout.write(f'Found {len(existing_content_ids)} blogs with existing attention items')

        # Get blogs without attention items
        blogs_query = SelfBlog.objects.all().order_by('-created_at')

        # Filter out blogs that already have attention items
        blogs_to_process = []
        for blog in blogs_query:
            if str(blog.id) not in existing_content_ids:
                blogs_to_process.append(blog)
                if limit and len(blogs_to_process) >= limit:
                    break

        total_to_process = len(blogs_to_process)
        self.stdout.write(f'Found {total_to_process} blogs needing attention items')

        if total_to_process == 0:
            self.stdout.write(self.style.SUCCESS('All blogs already have attention items!'))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING('\n[DRY RUN] Would create attention items for:'))
            for blog in blogs_to_process[:10]:
                self.stdout.write(f'  - {blog.title[:60]}... (ID: {blog.id})')
            if total_to_process > 10:
                self.stdout.write(f'  ... and {total_to_process - 10} more')
            return

        # Create attention items
        bridge = HumanAttentionBridge()
        created = 0
        errors = 0

        for i, blog in enumerate(blogs_to_process):
            try:
                summary = f"Blog post for review: {blog.meta_description[:100]}" if blog.meta_description else "AI-generated blog post ready for review"

                bridge.create_content_review_attention(
                    content_type='blog',
                    title=blog.title,
                    summary=summary,
                    content_id=str(blog.id),
                    agent_name='ContentWriterAgent',
                    quality_score=quality_score,
                )
                created += 1

                if (i + 1) % 50 == 0:
                    self.stdout.write(f'  Processed {i + 1}/{total_to_process}...')

            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f'  Error for blog {blog.id}: {e}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Created {created} attention items'))
        if errors:
            self.stdout.write(self.style.WARNING(f'Errors: {errors}'))

        # Show summary
        total_attention = HumanAttentionItem.objects.filter(
            item_type='review',
            source_type__startswith='content:blog'
        ).count()
        self.stdout.write(f'\nTotal blog attention items now: {total_attention}')
