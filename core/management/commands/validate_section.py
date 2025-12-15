# core/management/commands/validate_section.py
"""
Management command for running section validation agents.

Usage:
    python manage.py validate_section --section=images
    python manage.py validate_section --section=videos
    python manage.py validate_section --section=agents
    python manage.py validate_section --section=spiders
    python manage.py validate_section --all
    python manage.py validate_section --list
"""

import json
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from core.validation import (
    VALIDATORS,
    get_validator_for_section,
    run_all_validations,
)

User = get_user_model()


class Command(BaseCommand):
    help = 'Run section validation agents to verify platform health'

    def add_arguments(self, parser):
        parser.add_argument(
            '--section',
            type=str,
            help='Section to validate (images, videos, agents, spiders)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Validate all sections',
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List available sections',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output results as JSON',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username for authenticated requests (optional)',
        )

    def handle(self, *args, **options):
        # Get user if specified
        user = None
        if options.get('user'):
            try:
                user = User.objects.get(username=options['user'])
            except User.DoesNotExist:
                raise CommandError(f"User '{options['user']}' not found")

        # List sections
        if options.get('list'):
            self.stdout.write("\nAvailable validation sections:")
            for section in VALIDATORS.keys():
                self.stdout.write(f"  - {section}")
            self.stdout.write("\nUsage: python manage.py validate_section --section=<name>")
            return

        # Validate all sections
        if options.get('all'):
            self.stdout.write("\n" + "=" * 60)
            self.stdout.write("Running ALL section validations...")
            self.stdout.write("=" * 60 + "\n")

            results = run_all_validations(user=user)

            if options.get('json'):
                self.stdout.write(json.dumps(results, indent=2))
            else:
                self._print_full_report(results)
            return

        # Validate specific section
        section = options.get('section')
        if not section:
            raise CommandError(
                "Please specify --section=<name>, --all, or --list\n"
                f"Available sections: {', '.join(VALIDATORS.keys())}"
            )

        validator_class = get_validator_for_section(section)
        if not validator_class:
            raise CommandError(
                f"Unknown section: {section}\n"
                f"Available sections: {', '.join(VALIDATORS.keys())}"
            )

        self.stdout.write(f"\nValidating section: {section}")
        self.stdout.write("-" * 40)

        validator = validator_class(user=user)
        results = validator.validate_all()

        if options.get('json'):
            self.stdout.write(json.dumps(results, indent=2))
        else:
            self._print_section_results(results)

    def _print_section_results(self, results):
        """Print results for a single section."""
        status = results.get('status', 'unknown')
        status_color = {
            'healthy': self.style.SUCCESS,
            'degraded': self.style.WARNING,
            'unhealthy': self.style.ERROR,
        }.get(status, self.style.NOTICE)

        self.stdout.write(f"\nSection: {results.get('section', 'unknown')}")
        self.stdout.write(status_color(f"Status: {status.upper()}"))
        self.stdout.write(f"Duration: {results.get('duration_ms', 0):.1f}ms")
        self.stdout.write("")

        # Print checks
        for check in results.get('checks', []):
            passed = check.get('pass', False)
            mark = self.style.SUCCESS("✓") if passed else self.style.ERROR("✗")
            name = check.get('name', 'unknown')
            message = check.get('message', '')
            duration = check.get('duration_ms', 0)

            self.stdout.write(f"  {mark} {name}: {message} ({duration:.0f}ms)")

        # Print summary
        summary = results.get('summary', {})
        self.stdout.write("")
        self.stdout.write(f"Total: {summary.get('total', 0)} checks")
        self.stdout.write(self.style.SUCCESS(f"Passed: {summary.get('passed', 0)}"))
        if summary.get('failed', 0) > 0:
            self.stdout.write(self.style.ERROR(f"Failed: {summary.get('failed', 0)}"))
        else:
            self.stdout.write(f"Failed: 0")

    def _print_full_report(self, results):
        """Print full validation report for all sections."""
        overall = results.get('overall_status', 'unknown')
        overall_color = {
            'healthy': self.style.SUCCESS,
            'degraded': self.style.WARNING,
            'unhealthy': self.style.ERROR,
        }.get(overall, self.style.NOTICE)

        # Print each section
        for section_name, section_results in results.get('sections', {}).items():
            self._print_section_results(section_results)
            self.stdout.write("")

        # Print overall summary
        self.stdout.write("=" * 60)
        self.stdout.write(overall_color(f"OVERALL STATUS: {overall.upper()}"))

        summary = results.get('summary', {})
        self.stdout.write(f"Total checks: {summary.get('total', 0)}")
        self.stdout.write(self.style.SUCCESS(f"Passed: {summary.get('passed', 0)}"))
        if summary.get('failed', 0) > 0:
            self.stdout.write(self.style.ERROR(f"Failed: {summary.get('failed', 0)}"))
        self.stdout.write("=" * 60)
