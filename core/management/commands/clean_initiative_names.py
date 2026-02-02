"""
Session 906: Clean up initiative names that are technical descriptions instead of titles.

Problem: Some initiatives have names like:
  "derived expertise as inputs, outputs ranked actionable recommendations, integrat..."
Instead of clean titles like:
  "Design 3 Lightweight Experiments"

Usage:
    # Dry run - show what would be cleaned
    python manage.py clean_initiative_names

    # Actually clean them
    python manage.py clean_initiative_names --fix

    # Limit to most recent
    python manage.py clean_initiative_names --fix --limit=50
"""

from django.core.management.base import BaseCommand
import re
import logging

logger = logging.getLogger(__name__)


def is_bad_name(name: str) -> bool:
    """Check if an initiative name looks like technical description instead of a title."""
    if not name:
        return True

    # Signs of bad names:
    bad_indicators = [
        # Contains arrow notation (workflow diagrams)
        '->' in name or '→' in name,
        # Contains technical symbols
        name.startswith('>') or name.startswith('-'),
        # Contains semicolons (multiple clauses)
        ';' in name,
        # Contains "outputs" or "inputs" (workflow language)
        'outputs:' in name.lower() or 'inputs:' in name.lower(),
        'outputs =' in name.lower(),
        # Is exactly 150 chars (was truncated)
        len(name) == 150,
        # Contains commas and is long (probably a list/description)
        name.count(',') > 2 and len(name) > 100,
        # Starts with lowercase (not a proper title)
        name[0].islower() if name else False,
        # Contains multiple technical terms in sequence
        bool(re.search(r'(vector DB|embeddings|API|JSON|reranker|synthesis)', name)),
    ]

    return any(bad_indicators)


def extract_clean_title(initiative) -> str:
    """Try to extract a clean title from initiative data."""
    name = initiative.name
    description = initiative.description or ''
    parent_topic = initiative.parent_topic or ''

    # Option 1: Use parent_topic if it's cleaner and short
    if parent_topic and len(parent_topic) < 60 and not is_bad_name(parent_topic):
        return _title_case(parent_topic)

    # Option 2: Extract from description
    if description:
        # Look for "Auto-created for: X" pattern
        match = re.search(r'Auto-created (?:initiative )?for[: ]+(.*?)(?:\.|$)', description, re.IGNORECASE)
        if match:
            topic = match.group(1).strip()
            if topic and len(topic) < 60:
                return _title_case(topic)

    # Option 3: Extract first meaningful phrase (before special chars)
    # Be aggressive - stop at first special character
    for delimiter in [';', ' -> ', ' → ', ':', ',', '/', '=']:
        if delimiter in name:
            first_part = name.split(delimiter)[0].strip()
            # Clean up technical prefixes
            first_part = re.sub(r'^[>\-\s]+', '', first_part)
            if first_part and len(first_part) >= 5:
                # Truncate to max 50 chars, title case it
                return _title_case(first_part[:50])

    # Option 4: Take first 3-4 words only
    words = name.split()[:4]
    if words:
        cleaned = ' '.join(words)
        cleaned = re.sub(r'^[>\-\s]+', '', cleaned)  # Remove leading special chars
        return _title_case(cleaned[:50])

    return name[:50]


def _title_case(text: str) -> str:
    """Convert text to title case, handling edge cases."""
    if not text:
        return text

    # Remove leading special characters
    text = re.sub(r'^[>\-\s]+', '', text)

    # If it's already title-cased or uppercase, return as-is
    if text[0].isupper():
        # Just ensure reasonable length
        return text[:50] if len(text) > 50 else text

    # Title case it
    words = text.split()
    titled = []
    small_words = {'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'}
    for i, word in enumerate(words):
        if i == 0 or word.lower() not in small_words:
            titled.append(word.capitalize())
        else:
            titled.append(word.lower())

    result = ' '.join(titled)
    return result[:50] if len(result) > 50 else result


class Command(BaseCommand):
    help = 'Clean up initiative names that look like technical descriptions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Actually update the names (default is dry run)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=500,
            help='Maximum number of initiatives to check (default: 500)',
        )
        parser.add_argument(
            '--min-length',
            type=int,
            default=80,
            help='Only check names longer than this (default: 80)',
        )

    def handle(self, *args, **options):
        from core.models_document_registry import Initiative

        fix = options['fix']
        limit = options['limit']
        min_length = options['min_length']

        self.stdout.write(self.style.NOTICE(
            f"{'FIXING' if fix else 'DRY RUN'}: Cleaning initiative names (limit: {limit}, min_length: {min_length})"
        ))

        # Find initiatives with potentially bad names
        initiatives = Initiative.objects.order_by('-created_at')[:limit]

        bad_count = 0
        fixed_count = 0
        skipped_count = 0

        for init in initiatives:
            if not is_bad_name(init.name):
                continue

            if len(init.name) < min_length:
                skipped_count += 1
                continue

            bad_count += 1
            new_name = extract_clean_title(init)

            # Skip if no improvement
            if new_name == init.name or len(new_name) >= len(init.name):
                self.stdout.write(self.style.WARNING(
                    f"SKIP: {init.name[:50]}... (no improvement found)"
                ))
                skipped_count += 1
                continue

            if fix:
                old_name = init.name
                init.name = new_name
                init.save(update_fields=['name', 'updated_at'])
                fixed_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f"FIXED: '{old_name[:40]}...' → '{new_name}'"
                ))
            else:
                self.stdout.write(
                    f"WOULD FIX: '{init.name[:40]}...' → '{new_name}'"
                )
                fixed_count += 1

        self.stdout.write(self.style.NOTICE(f"\nSummary:"))
        self.stdout.write(f"  Found bad names: {bad_count}")
        self.stdout.write(self.style.SUCCESS(f"  {'Fixed' if fix else 'Would fix'}: {fixed_count}"))
        self.stdout.write(self.style.WARNING(f"  Skipped: {skipped_count}"))
