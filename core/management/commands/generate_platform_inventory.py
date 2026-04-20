"""Generate the master ``docs/PLATFORM_INVENTORY.md`` runtime snapshot (Session 1099).

Usage::

    python manage.py generate_platform_inventory
    python manage.py generate_platform_inventory --output docs/PLATFORM_INVENTORY.md
    python manage.py generate_platform_inventory --stdout
    python manage.py generate_platform_inventory --json > inventory.json
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

from django.core.management.base import BaseCommand

from core.services.platform_inventory import gather_inventory, render_markdown

DEFAULT_OUTPUT = Path('docs') / 'PLATFORM_INVENTORY.md'


class Command(BaseCommand):
    help = 'Generate docs/PLATFORM_INVENTORY.md — runtime-derived master platform snapshot'

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            '--output', '-o',
            default=str(DEFAULT_OUTPUT),
            help=f'Path to write the Markdown output (default: {DEFAULT_OUTPUT})',
        )
        parser.add_argument(
            '--stdout',
            action='store_true',
            help='Write Markdown to stdout instead of a file',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Emit the raw inventory dict as JSON (to stdout or file)',
        )

    def handle(self, *args, **options) -> None:
        self.stdout.write('🧭 Gathering platform inventory...')
        inventory = gather_inventory()

        if options['json']:
            payload = {
                'generated_at': inventory['generated_at'],
                'git_sha': inventory['git_sha'],
                'sections': [asdict(s) for s in inventory['sections']],
            }
            body = json.dumps(payload, indent=2, default=str)
        else:
            body = render_markdown(inventory)

        if options['stdout']:
            sys.stdout.write(body)
            return

        output_path = Path(options['output']).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(body, encoding='utf-8')

        # Summary line for the operator
        total_sections = len(inventory['sections'])
        error_sections = sum(1 for s in inventory['sections'] if s.error)
        self.stdout.write(self.style.SUCCESS(
            f'✅ Wrote {output_path} ({output_path.stat().st_size:,} bytes) — '
            f'{total_sections} sections ({error_sections} with collector errors)'
        ))
