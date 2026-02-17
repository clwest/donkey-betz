"""
Session 1026: Surface remediation findings for Claude Code sessions.

Replaces the old execute-remediation-tasks Celery schedule that burned $9/day
running CodeGeneratorAgent in an empty sandbox. Findings are real and valuable —
this command makes them actionable by a developer or Claude Code session that
can actually access the codebase.

Usage:
    python manage.py show_remediation_findings              # All open/in_progress
    python manage.py show_remediation_findings --priority P0 P1  # Critical/High only
    python manage.py show_remediation_findings --category security  # By category
    python manage.py show_remediation_findings --limit 5    # Top 5 by priority
"""
from django.core.management.base import BaseCommand

from core.models_audit_tracking import AuditFinding


PRIORITY_ORDER = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}


class Command(BaseCommand):
    help = 'Show open remediation findings for Claude Code sessions to act on'

    def add_arguments(self, parser):
        parser.add_argument(
            '--priority', nargs='+', default=None,
            help='Filter by priority (P0, P1, P2, P3)',
        )
        parser.add_argument(
            '--category', type=str, default=None,
            help='Filter by category (security, performance, code_quality, etc.)',
        )
        parser.add_argument(
            '--limit', type=int, default=20,
            help='Max findings to show (default: 20)',
        )
        parser.add_argument(
            '--verbose', action='store_true',
            help='Show full descriptions and recommendations',
        )

    def handle(self, *args, **options):
        qs = AuditFinding.objects.filter(
            status__in=['open', 'in_progress']
        ).select_related('audit_report')

        if options['priority']:
            qs = qs.filter(priority__in=options['priority'])
        if options['category']:
            qs = qs.filter(category=options['category'])

        qs = qs.order_by('priority', '-created_at')

        findings = list(qs[:options['limit']])
        total = qs.count()

        if not findings:
            self.stdout.write('No open findings found.')
            return

        # Summary header
        self.stdout.write(f'\n{"=" * 70}')
        self.stdout.write(f'REMEDIATION FINDINGS — {total} open ({len(findings)} shown)')
        self.stdout.write(f'{"=" * 70}\n')

        # Priority breakdown
        from django.db.models import Count
        breakdown = dict(
            AuditFinding.objects.filter(status__in=['open', 'in_progress'])
            .values_list('priority')
            .annotate(c=Count('id'))
            .values_list('priority', 'c')
        )
        for p in ['P0', 'P1', 'P2', 'P3']:
            count = breakdown.get(p, 0)
            if count:
                self.stdout.write(f'  {p}: {count}')

        # Category breakdown
        cat_breakdown = dict(
            AuditFinding.objects.filter(status__in=['open', 'in_progress'])
            .values_list('category')
            .annotate(c=Count('id'))
            .values_list('category', 'c')
        )
        self.stdout.write(f'\n  Categories: {", ".join(f"{k}={v}" for k, v in sorted(cat_breakdown.items(), key=lambda x: -x[1]))}')
        self.stdout.write('')

        # Individual findings
        for i, f in enumerate(findings, 1):
            self.stdout.write(f'--- [{f.priority}] #{i}: {f.title}')
            self.stdout.write(f'    Category: {f.category} | Impact: {f.impact} | Status: {f.status}')

            if f.affected_files:
                files = f.affected_files if isinstance(f.affected_files, list) else []
                if files:
                    shown = files[:5]
                    self.stdout.write(f'    Files: {", ".join(shown)}')
                    if len(files) > 5:
                        self.stdout.write(f'           ... and {len(files) - 5} more')

            if options['verbose']:
                if f.description:
                    desc = f.description[:500]
                    self.stdout.write(f'    Description: {desc}')
                if f.recommendation:
                    rec = f.recommendation[:500]
                    self.stdout.write(f'    Recommendation: {rec}')

            self.stdout.write('')

        if total > len(findings):
            self.stdout.write(f'... {total - len(findings)} more findings not shown (use --limit {total})')

        self.stdout.write(f'\nTo fix a finding, address it in the codebase and then mark it:')
        self.stdout.write(f'  AuditFinding.objects.filter(id="<uuid>").update(status="fixed", fixed_by="Session XXXX")')
