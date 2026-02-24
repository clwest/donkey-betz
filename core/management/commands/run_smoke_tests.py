"""
Management command: run deploy verification checks from the CLI.

Usage:
    python manage.py run_smoke_tests --base-url https://... --token <token>
    railway run python manage.py run_smoke_tests --token <token>
"""

from django.core.management.base import BaseCommand

from core.views_deploy_verify import run_verification


class Command(BaseCommand):
    help = 'Run deploy verification checks against a running server'

    def add_arguments(self, parser):
        parser.add_argument(
            '--base-url',
            default='https://donkey-betz-platform-production.up.railway.app',
            help='Base URL of the server to check',
        )
        parser.add_argument(
            '--token',
            default=None,
            help='DRF auth token for authenticated endpoints',
        )

    def handle(self, *args, **options):
        base_url = options['base_url']
        token = options['token']

        self.stdout.write(f'Running smoke tests against {base_url}')
        results = run_verification(base_url, token=token)

        for check in results['results']:
            icon = 'PASS' if check['ok'] else 'FAIL'
            style = self.style.SUCCESS if check['ok'] else self.style.ERROR
            self.stdout.write(style(
                f'  [{icon}] {check["name"]}: {check["detail"]} ({check["latency_ms"]}ms)'
            ))

        summary = f'{results["passed"]}/{results["total"]} checks passed'
        if results['all_ok']:
            self.stdout.write(self.style.SUCCESS(f'\n{summary}'))
        else:
            self.stdout.write(self.style.ERROR(f'\n{summary}'))
