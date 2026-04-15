"""
Bulk Spider Embedding Command
=============================

Session 394: Fast bulk embedding for spider data.

This command processes all SpiderData entries that need embeddings in an
efficient manner:
1. Skips entries with no embeddable content (marks them as processed)
2. Uses batch processing for OpenAI API efficiency
3. Shows progress and can be interrupted/resumed

Usage:
    python manage.py bulk_embed_spiders              # Process all
    python manage.py bulk_embed_spiders --batch=200  # Custom batch size
    python manage.py bulk_embed_spiders --hours=24   # Only last 24 hours
    python manage.py bulk_embed_spiders --dry-run    # Preview without changes
"""

import time
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from django.conf import settings


class Command(BaseCommand):
    help = 'Bulk generate embeddings for spider data entries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch',
            type=int,
            default=100,
            help='Batch size for processing (default: 100)'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=168,
            help='Only process entries from last N hours (default: 168 = 7 days)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be processed without making changes'
        )
        parser.add_argument(
            '--mark-empty',
            action='store_true',
            help='Mark entries with no items as processed (skip in future)'
        )

    def handle(self, *args, **options):
        from core.models_unified_system import SpiderData
        from core.services.openai_client_factory import get_openai_client

        batch_size = options['batch']
        hours = options['hours']
        dry_run = options['dry_run']
        mark_empty = options['mark_empty']

        self.stdout.write(self.style.NOTICE(
            f"\n{'='*60}\n"
            f"Bulk Spider Embedding\n"
            f"{'='*60}\n"
            f"Batch size: {batch_size}\n"
            f"Hours: {hours}\n"
            f"Dry run: {dry_run}\n"
            f"Mark empty: {mark_empty}\n"
            f"{'='*60}\n"
        ))

        # Get OpenAI client
        api_key = settings.AI_PROVIDERS.get('OPENAI_API_KEY')
        if not api_key:
            self.stdout.write(self.style.ERROR('No OpenAI API key found!'))
            return

        client = get_openai_client(api_key=api_key)

        # Get entries needing embeddings
        since = timezone.now() - timedelta(hours=hours)
        entries = SpiderData.objects.filter(
            created_at__gte=since,
            embedding__isnull=True
        ).order_by('-created_at')

        total_count = entries.count()
        self.stdout.write(f"Found {total_count} entries needing embeddings\n")

        # Analyze entries
        embeddable = []
        empty = []

        self.stdout.write("Analyzing entries...")
        for entry in entries:
            # Handle raw_data as string (JSON) or dict
            raw_data = entry.raw_data
            if isinstance(raw_data, str):
                try:
                    import json
                    raw_data = json.loads(raw_data)
                except (json.JSONDecodeError, TypeError):
                    raw_data = {}

            # For single-item entries (from news spiders), wrap in items list
            items = raw_data.get('items', []) if isinstance(raw_data, dict) else []
            if not items and isinstance(raw_data, dict) and raw_data.get('title'):
                # Single item stored directly (not wrapped in 'items')
                items = [raw_data]

            # Session 534: Check for nested article structures (VentureBeat, Kickstarter, etc.)
            has_content = False
            if items:
                for item in items:
                    if isinstance(item, dict):
                        # Check if nested articles exist (VentureBeat)
                        if item.get('articles') or item.get('ai_highlights'):
                            has_content = True
                            break
                        # Check for Kickstarter nested items
                        if 'items' in item and isinstance(item.get('items'), list) and item.get('items'):
                            has_content = True
                            break
                        # Check for Kickstarter by_category
                        if 'by_category' in item:
                            has_content = True
                            break
                        # Or direct title/name
                        if item.get('title') or item.get('name'):
                            has_content = True
                            break

            if has_content:
                # Has items - can be embedded
                text = self._build_embedding_text(entry)
                if text and len(text) > 20:
                    embeddable.append((entry, text))
            else:
                # No items - mark as empty
                empty.append(entry)

        self.stdout.write(self.style.SUCCESS(
            f"\nAnalysis complete:\n"
            f"  Embeddable: {len(embeddable)}\n"
            f"  Empty (no items): {len(empty)}\n"
        ))

        if dry_run:
            self.stdout.write(self.style.WARNING("\nDRY RUN - No changes made"))
            return

        # Mark empty entries if requested
        if mark_empty and empty:
            self.stdout.write(f"\nMarking {len(empty)} empty entries...")
            # Set embedding to empty list to skip in future
            for entry in empty:
                entry.embedding = []
                entry.embedding_text = "[NO_ITEMS]"
                entry.save(update_fields=['embedding', 'embedding_text'])
            self.stdout.write(self.style.SUCCESS(f"Marked {len(empty)} entries as empty"))

        # Process embeddable entries in batches
        if not embeddable:
            self.stdout.write(self.style.WARNING("No embeddable entries to process"))
            return

        self.stdout.write(f"\nProcessing {len(embeddable)} embeddable entries...")

        processed = 0
        succeeded = 0
        failed = 0
        start_time = time.time()

        # Process in batches
        for i in range(0, len(embeddable), batch_size):
            batch = embeddable[i:i + batch_size]
            batch_texts = [text for _, text in batch]
            batch_entries = [entry for entry, _ in batch]

            try:
                # Batch embedding API call
                response = client.embeddings.create(
                    input=batch_texts,
                    model="text-embedding-3-small"
                )

                # Save embeddings
                for j, embedding_data in enumerate(response.data):
                    entry = batch_entries[j]
                    entry.embedding = embedding_data.embedding
                    entry.embedding_text = batch_texts[j][:1000]
                    entry.save(update_fields=['embedding', 'embedding_text'])
                    succeeded += 1

                processed += len(batch)
                elapsed = time.time() - start_time
                rate = processed / elapsed if elapsed > 0 else 0

                self.stdout.write(
                    f"  Processed {processed}/{len(embeddable)} "
                    f"({succeeded} succeeded, {failed} failed) "
                    f"[{rate:.1f}/sec]"
                )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Batch failed: {e}"))
                failed += len(batch)
                processed += len(batch)

            # Small delay to respect rate limits
            time.sleep(0.1)

        # Final stats
        elapsed = time.time() - start_time
        self.stdout.write(self.style.SUCCESS(
            f"\n{'='*60}\n"
            f"Complete!\n"
            f"  Total processed: {processed}\n"
            f"  Succeeded: {succeeded}\n"
            f"  Failed: {failed}\n"
            f"  Empty marked: {len(empty) if mark_empty else 0}\n"
            f"  Time: {elapsed:.1f}s\n"
            f"{'='*60}\n"
        ))

    def _build_embedding_text(self, entry) -> str:
        """Build searchable text from spider data entry."""
        if not entry.raw_data:
            return ""

        # Handle raw_data as string (JSON) or dict
        raw_data = entry.raw_data
        if isinstance(raw_data, str):
            try:
                import json
                raw_data = json.loads(raw_data)
            except (json.JSONDecodeError, TypeError):
                return ""

        # Get items list, or treat single item as list
        items = raw_data.get('items', []) if isinstance(raw_data, dict) else []
        if not items and isinstance(raw_data, dict) and raw_data.get('title'):
            # Single item stored directly (not wrapped in 'items')
            items = [raw_data]

        if not items:
            return ""

        parts = []
        # Include spider/source context
        parts.append(f"Source: {entry.spider_name}")

        # Session 534: Handle nested structures (VentureBeat, Kickstarter, etc.)
        # Flatten nested article/item lists into items
        flat_items = []
        for item in items[:10]:
            if not isinstance(item, dict):
                continue
            # VentureBeat: articles key
            if 'articles' in item:
                flat_items.extend(item.get('articles', [])[:10])
            # VentureBeat: ai_highlights key
            elif 'ai_highlights' in item:
                flat_items.extend(item.get('ai_highlights', [])[:5])
            # Kickstarter: nested items key
            elif 'items' in item and isinstance(item.get('items'), list):
                flat_items.extend(item.get('items', [])[:15])
            # Kickstarter: by_category dict with category lists
            elif 'by_category' in item:
                for cat_items in item.get('by_category', {}).values():
                    if isinstance(cat_items, list):
                        flat_items.extend(cat_items[:5])
            else:
                flat_items.append(item)

        # Include up to 15 items from flattened list
        for item in flat_items[:15]:
            if not isinstance(item, dict):
                continue
            title = item.get('title') or item.get('name') or ''
            desc = item.get('description') or item.get('summary') or item.get('snippet') or ''

            if title:
                parts.append(title)
            if desc:
                parts.append(desc[:300])

            tags = item.get('tags', [])
            if isinstance(tags, list) and tags:
                parts.append(f"Tags: {', '.join(str(t) for t in tags[:5])}")

        text = ". ".join(parts)
        return text[:8000]  # Truncate for API limits
