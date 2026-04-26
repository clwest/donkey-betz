"""Refresh `<!-- @inventory-block:NAME -->` regions across registered docs (Session 1100).

Usage::

    python manage.py refresh_doc_inventory_blocks
    python manage.py refresh_doc_inventory_blocks --check  # exit non-zero if anything would change
    python manage.py refresh_doc_inventory_blocks --doc CLAUDE.md docs/CAPABILITIES.md

Closes the doc-drift loop. Authors put markers in docs once; this command
keeps the content between them in lock-step with `gather_inventory()`.

Pattern in source docs::

    <!-- @inventory-block:platform-stats -->
    ...auto-managed content...
    <!-- @inventory-block:end -->

Block names are registered in ``platform_inventory.INVENTORY_BLOCKS``.
"""
from __future__ import annotations

import sys
from pathlib import Path

from django.core.management.base import BaseCommand

from core.services.platform_inventory import (
    INVENTORY_BLOCKS,
    gather_inventory,
    refresh_doc_blocks,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# Default doc set scanned by this command. Add new docs here when you put
# inventory-block markers in them.
REGISTERED_DOCS: list[Path] = [
    REPO_ROOT / 'CLAUDE.md',
    REPO_ROOT / 'docs' / 'BACKEND_INVENTORY.md',
    REPO_ROOT / 'docs' / 'CAPABILITIES.md',
    REPO_ROOT / 'docs' / 'AGENTS.md',
    REPO_ROOT / 'docs' / 'topics' / 'agent-system.md',
    REPO_ROOT / 'docs' / 'topics' / 'personal-assistant.md',
]


class Command(BaseCommand):
    help = (
        'Refresh <!-- @inventory-block:NAME --> regions in registered docs '
        'using runtime-derived data from gather_inventory().'
    )

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--doc',
            nargs='*',
            help='Specific doc paths to refresh (relative to repo root). '
                 'Defaults to the REGISTERED_DOCS list.',
        )
        parser.add_argument(
            '--check',
            action='store_true',
            help='Dry-run: report what would change and exit non-zero if any '
                 'block needs updating. Useful for CI.',
        )
        parser.add_argument(
            '--list-blocks',
            action='store_true',
            help='List the available block names and exit.',
        )

    def handle(self, *args, **options) -> None:
        if options['list_blocks']:
            self.stdout.write('Registered inventory blocks:')
            for name in sorted(INVENTORY_BLOCKS.keys()):
                self.stdout.write(f'  - {name}')
            return

        if options['doc']:
            docs = [REPO_ROOT / p for p in options['doc']]
        else:
            docs = REGISTERED_DOCS

        self.stdout.write('🧭 Gathering platform inventory...')
        inventory = gather_inventory()

        any_changes = False
        total_updated = 0
        total_skipped = 0
        unknown_names: set[str] = set()

        for path in docs:
            if not path.exists():
                self.stdout.write(self.style.WARNING(f'  skip (missing): {path.relative_to(REPO_ROOT)}'))
                continue

            if options['check']:
                # Snapshot original, run refresh, then compare and revert
                original = path.read_text()
                updated, skipped, unknown = refresh_doc_blocks(path, inventory)
                changed_now = path.read_text() != original
                if changed_now:
                    path.write_text(original)  # revert
                    any_changes = True
                state = 'WOULD UPDATE' if changed_now else 'ok'
            else:
                updated, skipped, unknown = refresh_doc_blocks(path, inventory)
                state = 'updated' if updated else 'no markers'

            total_updated += updated
            total_skipped += skipped
            unknown_names.update(unknown)
            self.stdout.write(
                f'  [{state:>14}] {path.relative_to(REPO_ROOT)} '
                f'(updated={updated}, skipped={skipped})'
            )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Total: {total_updated} blocks updated, {total_skipped} skipped'
        ))
        if unknown_names:
            self.stdout.write(self.style.WARNING(
                f'Unknown block names encountered: {sorted(unknown_names)}'
            ))

        if options['check'] and any_changes:
            self.stderr.write(self.style.ERROR(
                'check mode: at least one block would change. Run without --check to apply.'
            ))
            sys.exit(1)
