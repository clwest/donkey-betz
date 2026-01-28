"""
Session 855: Fix mislabeled SelfBlog categories.

SelfBlogs created before Session 852 may have wrong category='blog' when they
should be 'research_brief', 'technical_document', or 'audit' based on their title.

Usage:
    python manage.py fix_selfblog_categories
    python manage.py fix_selfblog_categories --dry-run
"""

from django.core.management.base import BaseCommand
from core.models_unified_system import SelfBlog


class Command(BaseCommand):
    help = 'Fix mislabeled SelfBlog categories based on title patterns'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be fixed without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - no changes will be made'))

        # Fix research briefs
        research_qs = SelfBlog.objects.filter(
            category='blog',
            title__icontains='Research Brief'
        )
        research_count = research_qs.count()
        if not dry_run:
            research_qs.update(category='research_brief')
        self.stdout.write(f'Fixed {research_count} research briefs')

        # Fix prototype plans as technical documents
        plan_qs = SelfBlog.objects.filter(
            category='blog',
            title__icontains='Prototype Plan'
        )
        plan_count = plan_qs.count()
        if not dry_run:
            plan_qs.update(category='technical_document')
        self.stdout.write(f'Fixed {plan_count} prototype plans')

        # Fix anything with [Stage X - pattern
        stage_qs = SelfBlog.objects.filter(
            category='blog',
            title__regex=r'^\[Stage \d+'
        )
        stage_count = stage_qs.count()
        if not dry_run:
            stage_qs.update(category='technical_document')
        self.stdout.write(f'Fixed {stage_count} stage documents')

        # Fix [Report] titles as audits
        report_qs = SelfBlog.objects.filter(
            category='blog',
            title__istartswith='[Report]'
        )
        report_count = report_qs.count()
        if not dry_run:
            report_qs.update(category='audit')
        self.stdout.write(f'Fixed {report_count} audit reports')

        # Fix root_cause items as research
        rootcause_qs = SelfBlog.objects.filter(
            category='blog',
            title__icontains='root_cause'
        )
        rootcause_count = rootcause_qs.count()
        if not dry_run:
            rootcause_qs.update(category='research_brief')
        self.stdout.write(f'Fixed {rootcause_count} root cause items')

        # Summary
        total_fixed = research_count + plan_count + stage_count + report_count + rootcause_count

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Total fixed: {total_fixed} items'))

        # Show final distribution
        from django.db.models import Count
        self.stdout.write('')
        self.stdout.write('=== Category Distribution ===')
        cats = SelfBlog.objects.values('category').annotate(count=Count('id')).order_by('-count')
        for c in cats:
            self.stdout.write(f"  {c['category'] or 'None'}: {c['count']}")
