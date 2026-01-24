"""
Session 810: Backfill HumanAttentionItem entries for existing SelfBlogs

This command creates HumanAttentionItem entries for SelfBlogs that were created
before Session 804's fix was deployed. Without these entries, blogs don't appear
in the Human Interface.

Usage:
    python manage.py backfill_blog_attention_items           # Backfill all
    python manage.py backfill_blog_attention_items --dry-run # Preview only
    python manage.py backfill_blog_attention_items --limit=100 # Limit to 100
"""

import logging
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Backfill HumanAttentionItem entries for existing SelfBlogs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without making changes'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Limit number of blogs to process (0 = all)'
        )
        parser.add_argument(
            '--days',
            type=int,
            default=0,
            help='Only process blogs from last N days (0 = all)'
        )

    def handle(self, *args, **options):
        from core.models import SelfBlog, HumanAttentionItem
        from core.services.human_attention_bridge import HumanAttentionBridge

        dry_run = options['dry_run']
        limit = options['limit']
        days = options['days']

        self.stdout.write(f"\n{'='*60}")
        self.stdout.write("SESSION 810: Backfill Blog Attention Items")
        self.stdout.write(f"{'='*60}\n")

        # Get blogs that don't have attention items
        blogs = SelfBlog.objects.all().order_by('-created_at')

        if days > 0:
            cutoff = timezone.now() - timedelta(days=days)
            blogs = blogs.filter(created_at__gte=cutoff)
            self.stdout.write(f"Filtering to blogs from last {days} days")

        if limit > 0:
            blogs = blogs[:limit]
            self.stdout.write(f"Limiting to {limit} blogs")

        # Check which blogs already have attention items
        # We'll use title matching since there's no direct FK
        existing_titles = set(
            HumanAttentionItem.objects.filter(
                item_type='review'
            ).values_list('title', flat=True)
        )

        self.stdout.write(f"\nTotal SelfBlogs: {SelfBlog.objects.count()}")
        self.stdout.write(f"Blogs to process: {blogs.count()}")
        self.stdout.write(f"Existing attention items (review type): {len(existing_titles)}")

        bridge = HumanAttentionBridge()
        created = 0
        skipped = 0
        errors = []

        for blog in blogs:
            # Skip if already has attention item
            if blog.title in existing_titles:
                skipped += 1
                continue

            # Determine content type from title
            if '[Report]' in blog.title:
                content_type = 'report'
            elif '[Research]' in blog.title:
                content_type = 'research'
            elif '[Deliverable]' in blog.title:
                content_type = 'deliverable'
            else:
                content_type = 'insight'

            if dry_run:
                self.stdout.write(f"  [DRY RUN] Would create: {blog.title[:60]}...")
                created += 1
                continue

            try:
                # Build summary from blog intro or title
                summary = blog.intro[:200] if blog.intro else f"Auto-generated {content_type}: {blog.title}"

                bridge.create_content_review_attention(
                    content_type=content_type,
                    title=blog.title,
                    summary=summary,
                    content_id=str(blog.id),
                    agent_name='ThinkingAgent',
                )
                created += 1
                self.stdout.write(self.style.SUCCESS(f"  + Created: {blog.title[:60]}..."))

            except Exception as e:
                errors.append(f"{blog.title[:40]}: {str(e)}")
                self.stdout.write(self.style.ERROR(f"  ! Error: {blog.title[:40]}: {e}"))

        # Summary
        self.stdout.write(f"\n{'='*60}")
        self.stdout.write("SUMMARY")
        self.stdout.write(f"{'='*60}")

        if dry_run:
            self.stdout.write(f"Would create: {created} attention items")
            self.stdout.write(f"Would skip (already exist): {skipped}")
        else:
            self.stdout.write(self.style.SUCCESS(f"Created: {created} attention items"))
            self.stdout.write(f"Skipped (already exist): {skipped}")

            # Final count
            total_reviews = HumanAttentionItem.objects.filter(item_type='review').count()
            self.stdout.write(f"\nTotal review attention items: {total_reviews}")

        if errors:
            self.stdout.write(self.style.WARNING(f"\nErrors ({len(errors)}):"))
            for error in errors[:10]:  # Show first 10 errors
                self.stdout.write(self.style.WARNING(f"  - {error}"))
            if len(errors) > 10:
                self.stdout.write(self.style.WARNING(f"  ... and {len(errors) - 10} more"))
