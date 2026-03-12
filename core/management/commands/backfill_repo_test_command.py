"""Management command: backfill_repo_test_command

Ensures that Repo rows for 'clwest/donkey-betz-platform' with a NULL or
empty test_command are updated to 'make test-fast'.

Matches repo_url variants:
  - https://github.com/clwest/donkey-betz-platform
  - https://github.com/clwest/donkey-betz-platform.git
  - git@github.com:clwest/donkey-betz-platform.git
  - slug match (name contains 'donkey-betz-platform')

Usage:
    python manage.py backfill_repo_test_command
    python manage.py backfill_repo_test_command --dry-run
"""

from django.core.management.base import BaseCommand
from django.db.models import Q


TARGET_TEST_COMMAND = 'make test-fast'

SLUG = 'donkey-betz-platform'
URL_VARIANTS = [
    'https://github.com/clwest/donkey-betz-platform',
    'https://github.com/clwest/donkey-betz-platform.git',
    'git@github.com:clwest/donkey-betz-platform.git',
    'git@github.com:clwest/donkey-betz-platform',
]


class Command(BaseCommand):
    help = (
        "Backfill test_command='make test-fast' for donkey-betz-platform "
        'Repo rows that have NULL or empty test_command.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without writing to the database.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        try:
            from core.models.executor.models import Repo
        except ImportError:
            self.stderr.write(
                self.style.ERROR(
                    'Could not import Repo model. '
                    'Ensure core.models.executor is configured correctly.'
                )
            )
            return

        # Build a filter for all URL variants + slug/name match
        url_filter = Q()
        for url in URL_VARIANTS:
            url_filter |= Q(repo_url__iexact=url)

        # Also catch partial slug matches in repo_url or name
        url_filter |= Q(repo_url__icontains=SLUG)
        url_filter |= Q(name__icontains=SLUG)

        # Only rows with NULL or empty test_command
        needs_update = Repo.objects.filter(url_filter).filter(
            Q(test_command__isnull=True) | Q(test_command='')
        )

        count = needs_update.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    'No Repo rows need updating — all matching rows already have a test_command.'
                )
            )
            return

        self.stdout.write(
            f'Found {count} Repo row(s) matching donkey-betz-platform with empty/NULL test_command.'
        )

        if dry_run:
            self.stdout.write(self.style.WARNING('[DRY RUN] Would update:'))
            for repo in needs_update:
                self.stdout.write(
                    f'  id={repo.id} name={repo.name!r} repo_url={repo.repo_url!r} '
                    f'test_command={repo.test_command!r} -> {TARGET_TEST_COMMAND!r}'
                )
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] {count} row(s) would be updated. '
                    'Re-run without --dry-run to apply.'
                )
            )
        else:
            updated = needs_update.update(test_command=TARGET_TEST_COMMAND)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {updated} Repo row(s) '
                    f"with test_command='{TARGET_TEST_COMMAND}'."
                )
            )
