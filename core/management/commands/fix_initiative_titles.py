"""
Management command to fix initiative titles.

Session 905: Cleans up messy initiative titles using the title generator.

Usage:
    # Dry run (preview changes)
    python manage.py fix_initiative_titles

    # Actually fix titles
    python manage.py fix_initiative_titles --fix

    # Fix specific initiatives
    python manage.py fix_initiative_titles --fix --ids="uuid1,uuid2"
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from core.services.initiative_title_generator import generate_initiative_title, _is_valid_title


class Command(BaseCommand):
    help = 'Fix messy initiative titles using smart title generation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Actually update the titles (default is dry run)',
        )
        parser.add_argument(
            '--ids',
            type=str,
            help='Comma-separated list of initiative IDs to fix (default: all with bad titles)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of initiatives to process (default: 100)',
        )

    def handle(self, *args, **options):
        from core.models_document_registry import Initiative

        fix_mode = options['fix']
        ids_filter = options['ids']
        limit = options['limit']

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("Initiative Title Fixer (Session 905)")
        self.stdout.write("=" * 60 + "\n")

        # Build queryset
        queryset = Initiative.objects.all()

        if ids_filter:
            ids = [i.strip() for i in ids_filter.split(',')]
            queryset = queryset.filter(id__in=ids)

        initiatives = queryset.order_by('-created_at')[:limit]

        bad_titles = []
        good_titles = []

        # Analyze titles
        for init in initiatives:
            if _is_valid_title(init.name, max_length=80):
                good_titles.append(init)
            else:
                bad_titles.append(init)

        self.stdout.write(f"Total initiatives analyzed: {len(initiatives)}")
        self.stdout.write(f"  Good titles: {len(good_titles)}")
        self.stdout.write(f"  Bad titles:  {len(bad_titles)}")

        if not bad_titles:
            self.stdout.write(self.style.SUCCESS("\nNo bad titles found!"))
            return

        self.stdout.write(f"\n{'DRY RUN' if not fix_mode else 'FIXING'} - {len(bad_titles)} initiatives:\n")

        fixed_count = 0
        failed_count = 0

        for init in bad_titles:
            old_title = init.name
            old_title_preview = old_title[:60] + "..." if len(old_title) > 60 else old_title

            # Generate new title from description or parent_topic
            content = init.description or ""
            topic_hint = init.parent_topic or ""

            new_title = generate_initiative_title(
                content=content,
                topic_hint=topic_hint,
                max_length=80,
                use_llm=True  # Use LLM for better titles
            )

            self.stdout.write(f"\n[{init.id}]")
            self.stdout.write(f"  OLD: {old_title_preview}")
            self.stdout.write(f"  NEW: {new_title}")

            if fix_mode:
                try:
                    with transaction.atomic():
                        init.name = new_title
                        init.save(update_fields=['name'])
                        fixed_count += 1
                        self.stdout.write(self.style.SUCCESS("  ✓ Fixed"))
                except Exception as e:
                    failed_count += 1
                    self.stdout.write(self.style.ERROR(f"  ✗ Error: {e}"))

        self.stdout.write("\n" + "-" * 60)

        if fix_mode:
            self.stdout.write(self.style.SUCCESS(f"Fixed: {fixed_count}"))
            if failed_count:
                self.stdout.write(self.style.ERROR(f"Failed: {failed_count}"))
        else:
            self.stdout.write(self.style.WARNING(
                f"Dry run complete. Run with --fix to update {len(bad_titles)} titles."
            ))
