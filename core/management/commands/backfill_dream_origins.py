"""
Session 766: Backfill existing dreams with origin classification.

This command analyzes dream titles and content to classify them as:
- joke: Humorous, absurd, or clearly not serious
- probe: Testing the system, experimentation
- speculative: Exploratory "what if" thinking
- serious: Genuine ideas and innovations (default)

Usage:
    python manage.py backfill_dream_origins --dry-run  # Preview changes
    python manage.py backfill_dream_origins            # Apply changes
    python manage.py backfill_dream_origins --verbose  # Show all classifications
"""

import re
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models_unified_system import AgentDream


class Command(BaseCommand):
    help = 'Backfill existing dreams with origin classification based on content analysis'

    # Keywords/patterns that suggest different origins
    # NOTE: These are EXTREMELY strict to avoid false positives
    # Agent-generated dreams are almost never jokes or probes
    # Only match obvious human testing behavior

    # Match on TITLE ONLY for jokes (content can contain these words legitimately)
    JOKE_TITLE_PATTERNS = [
        r'^joke\s*:',                       # Title starts with "joke:"
        r'^just\s+kidding\b',               # Title starts with "just kidding"
        r'\blol\b',                         # Contains "lol"
        r'\bhaha+\b',                       # Contains "haha" or "hahaha"
    ]

    # Match on TITLE ONLY for probes (these are human testing behaviors)
    PROBE_TITLE_PATTERNS = [
        r'^test$',                          # Title is just "test"
        r'^test\s*\d+$',                    # Title is "test123"
        r'^testing$',                       # Title is just "testing"
        r'^asdf',                           # Title starts with keyboard mashing
        r'^qwerty',                         # Title starts with keyboard mashing
        r'^hello\s*,?\s*world$',            # Title is just "hello world"
        r'^foo$', r'^bar$', r'^baz$',       # Programmer test strings
        r'^xxx+$', r'^yyy+$',               # Placeholder patterns
    ]

    # Match in CONTENT for very specific testing language
    PROBE_CONTENT_PATTERNS = [
        r'^just\s+testing',                 # Content starts with "just testing"
        r'^ignore\s+this',                  # Content starts with "ignore this"
        r'^delete\s+this',                  # Content starts with "delete this"
        r'^this\s+is\s+a\s+test\b',         # Content starts with "this is a test"
    ]

    SPECULATIVE_PATTERNS = [
        # Only match very explicit speculation markers
        r'\bwild\s+idea\b',                 # "wild idea"
        r'\bcrazy\s+thought\b',             # "crazy thought"
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without applying them',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show all classifications, not just changes',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Limit number of dreams to process (0 = all)',
        )
        parser.add_argument(
            '--recalculate-scores',
            action='store_true',
            help='Recalculate composite scores for all dreams (even unchanged)',
        )

    def classify_dream(self, dream):
        """Classify a dream based on its title and content.

        Uses separate patterns for title vs content to reduce false positives.
        Agent-generated dreams are almost always 'serious'.
        """
        title = (dream.title or '').lower().strip()
        content = (dream.content or '').lower().strip()

        # Check title for jokes
        for pattern in self.JOKE_TITLE_PATTERNS:
            if re.search(pattern, title, re.IGNORECASE):
                return 'joke'

        # Check title for probes
        for pattern in self.PROBE_TITLE_PATTERNS:
            if re.search(pattern, title, re.IGNORECASE):
                return 'probe'

        # Check content START for probes (only beginning of content)
        for pattern in self.PROBE_CONTENT_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return 'probe'

        # Check full text for speculative markers
        full_text = f"{title} {content}"
        for pattern in self.SPECULATIVE_PATTERNS:
            if re.search(pattern, full_text, re.IGNORECASE):
                return 'speculative'

        # Default to serious (most agent dreams are serious)
        return 'serious'

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        verbose = options['verbose']
        limit = options['limit']
        recalculate = options['recalculate_scores']

        self.stdout.write(self.style.NOTICE(
            f"{'[DRY RUN] ' if dry_run else ''}Backfilling dream origins..."
        ))

        # Get dreams to process
        queryset = AgentDream.objects.all()
        if limit > 0:
            queryset = queryset[:limit]

        total = queryset.count()
        self.stdout.write(f"Processing {total} dreams...")

        # Track statistics
        stats = {
            'serious': 0,
            'speculative': 0,
            'probe': 0,
            'joke': 0,
            'changed': 0,
            'unchanged': 0,
            'scores_updated': 0,
        }

        changes = []

        for dream in queryset:
            new_origin = self.classify_dream(dream)
            old_origin = dream.origin
            changed = old_origin != new_origin

            stats[new_origin] += 1

            if changed:
                stats['changed'] += 1
                changes.append({
                    'id': dream.id,
                    'title': dream.title[:50],
                    'old': old_origin,
                    'new': new_origin,
                })

                if verbose or new_origin in ['joke', 'probe']:
                    self.stdout.write(
                        f"  [{old_origin} → {new_origin}] {dream.title[:60]}"
                    )
            else:
                stats['unchanged'] += 1
                if verbose:
                    self.stdout.write(f"  [{new_origin}] {dream.title[:60]}")

        # Show summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("Classification Summary:"))
        self.stdout.write(f"  Serious:     {stats['serious']:,}")
        self.stdout.write(f"  Speculative: {stats['speculative']:,}")
        self.stdout.write(f"  Probe:       {stats['probe']:,}")
        self.stdout.write(f"  Joke:        {stats['joke']:,}")
        self.stdout.write(f"\n  Changed:     {stats['changed']:,}")
        self.stdout.write(f"  Unchanged:   {stats['unchanged']:,}")

        if dry_run:
            self.stdout.write(self.style.WARNING(
                "\n[DRY RUN] No changes applied. Run without --dry-run to apply."
            ))
            return

        # Apply changes
        if stats['changed'] > 0 or recalculate:
            self.stdout.write(self.style.NOTICE("\nApplying changes..."))

            with transaction.atomic():
                for dream in queryset:
                    new_origin = self.classify_dream(dream)
                    needs_update = dream.origin != new_origin or recalculate

                    if needs_update:
                        dream.origin = new_origin
                        # save() will recalculate composite_score with origin weight
                        dream.save()
                        stats['scores_updated'] += 1

            self.stdout.write(self.style.SUCCESS(
                f"\nUpdated {stats['scores_updated']:,} dreams with new origins and recalculated scores."
            ))
        else:
            self.stdout.write(self.style.SUCCESS("\nNo changes needed."))

        # Show examples of each category found
        if stats['joke'] > 0:
            self.stdout.write(self.style.WARNING("\nJoke examples:"))
            for c in [ch for ch in changes if ch['new'] == 'joke'][:3]:
                self.stdout.write(f"  - {c['title']}")

        if stats['probe'] > 0:
            self.stdout.write(self.style.WARNING("\nProbe examples:"))
            for c in [ch for ch in changes if ch['new'] == 'probe'][:3]:
                self.stdout.write(f"  - {c['title']}")

        if stats['speculative'] > 0:
            self.stdout.write(self.style.NOTICE("\nSpeculative examples:"))
            for c in [ch for ch in changes if ch['new'] == 'speculative'][:3]:
                self.stdout.write(f"  - {c['title']}")
