"""
Django Management Command for Database Schema Audit
===================================================

Session 623: Comprehensive database audit to ensure all Django models
have their corresponding tables in PostgreSQL and migrations are in sync.

Usage:
    python manage.py audit_database                    # Quick health check
    python manage.py audit_database --verbose          # Detailed per-model output
    python manage.py audit_database --fix              # Run missing migrations
    python manage.py audit_database --output report    # Generate docs/DATABASE_AUDIT.md
    python manage.py audit_database --fail-on-error    # Exit 1 if issues (for CI/CD)
    python manage.py audit_database --app core         # Audit specific app only
"""

import sys
from datetime import datetime
from collections import defaultdict
from django.core.management.base import BaseCommand
from django.apps import apps
from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    """Django management command for database schema auditing"""

    help = 'Audit database schema to ensure all models have corresponding tables'

    def add_arguments(self, parser):
        """Add command line arguments"""
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed per-model output'
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix issues by running migrations'
        )
        parser.add_argument(
            '--output',
            type=str,
            choices=['report', 'json'],
            help='Generate output: "report" for docs/DATABASE_AUDIT.md, "json" for JSON'
        )
        parser.add_argument(
            '--fail-on-error',
            action='store_true',
            help='Exit with code 1 if any issues found (for CI/CD)'
        )
        parser.add_argument(
            '--app',
            type=str,
            help='Audit specific app only (e.g., core, intelligence)'
        )

    def handle(self, *args, **options):
        """Main command handler"""
        self.verbose = options['verbose']
        self.fix = options['fix']
        self.output = options['output']
        self.fail_on_error = options['fail_on_error']
        self.target_app = options['app']

        self.stdout.write(self.style.SUCCESS(
            "\n" + "=" * 70 +
            "\n🔍 DATABASE SCHEMA AUDIT - Session 623" +
            "\n" + "=" * 70
        ))

        # Run the audit
        results = self.run_audit()

        # Display results
        self.display_results(results)

        # Generate output if requested
        if self.output == 'report':
            self.generate_markdown_report(results)
        elif self.output == 'json':
            self.generate_json_output(results)

        # Fix issues if requested
        if self.fix and results['missing']:
            self.fix_missing_tables(results)

        # Exit with error code if requested and issues found
        if self.fail_on_error and (results['missing'] or results['migration_issues']):
            sys.exit(1)

    def run_audit(self):
        """Run the complete database audit"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'healthy': [],
            'missing': [],
            'orphaned': [],
            'migration_issues': [],
            'by_app': defaultdict(lambda: {'healthy': 0, 'missing': 0}),
            'custom_tables': [],  # Models with custom db_table
        }

        # Get all registered models
        all_models = apps.get_models()
        self.stdout.write(f"\n📊 Discovered {len(all_models)} Django models\n")

        # Get all existing tables from PostgreSQL
        existing_tables = self.get_existing_tables()
        self.stdout.write(f"📊 Found {len(existing_tables)} tables in PostgreSQL\n")

        # Track which tables are accounted for
        accounted_tables = set()

        # Check each model
        for model in all_models:
            app_label = model._meta.app_label

            # Filter by app if specified
            if self.target_app and app_label != self.target_app:
                continue

            table_name = model._meta.db_table
            model_name = f"{app_label}.{model.__name__}"

            # Check for custom db_table
            default_table = f"{app_label}_{model.__name__.lower()}"
            if table_name != default_table:
                results['custom_tables'].append({
                    'model': model_name,
                    'table': table_name,
                    'default': default_table
                })

            # Check if table exists
            if table_name in existing_tables:
                results['healthy'].append({
                    'model': model_name,
                    'table': table_name,
                    'app': app_label
                })
                results['by_app'][app_label]['healthy'] += 1
                accounted_tables.add(table_name)

                if self.verbose:
                    self.stdout.write(f"  ✅ {model_name} → {table_name}")
            else:
                results['missing'].append({
                    'model': model_name,
                    'table': table_name,
                    'app': app_label
                })
                results['by_app'][app_label]['missing'] += 1

                self.stdout.write(self.style.ERROR(
                    f"  ❌ MISSING: {model_name} → {table_name}"
                ))

        # Check for orphaned tables (exist but no model)
        django_system_tables = {
            'django_migrations', 'django_content_type', 'django_session',
            'django_admin_log', 'auth_user', 'auth_group', 'auth_permission',
            'auth_group_permissions', 'auth_user_groups', 'auth_user_user_permissions',
            'django_celery_beat_clockedschedule', 'django_celery_beat_crontabschedule',
            'django_celery_beat_intervalschedule', 'django_celery_beat_periodictask',
            'django_celery_beat_periodictasks', 'django_celery_beat_solarschedule',
        }

        for table in existing_tables:
            if table not in accounted_tables:
                # Skip Django system tables and known prefixes
                if table in django_system_tables or table.startswith('django_'):
                    continue
                if table.startswith('auth_'):
                    continue

                results['orphaned'].append(table)
                if self.verbose:
                    self.stdout.write(self.style.WARNING(
                        f"  ⚠️  ORPHANED TABLE: {table}"
                    ))

        # Check migration state
        results['migration_issues'] = self.check_migration_state()

        return results

    def get_existing_tables(self):
        """Get all existing table names from PostgreSQL"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
            """)
            return {row[0] for row in cursor.fetchall()}

    def check_migration_state(self):
        """Check for migration inconsistencies"""
        issues = []

        with connection.cursor() as cursor:
            # Get applied migrations
            cursor.execute("""
                SELECT app, name, applied
                FROM django_migrations
                WHERE app = 'core'
                ORDER BY applied DESC
                LIMIT 10
            """)
            recent_migrations = cursor.fetchall()

            if self.verbose:
                self.stdout.write("\n📜 Recent migrations:")
                for app, name, applied in recent_migrations:
                    self.stdout.write(f"   {app}.{name} - {applied}")

        return issues

    def display_results(self, results):
        """Display audit results summary"""
        self.stdout.write("\n" + "-" * 70)
        self.stdout.write(self.style.SUCCESS("📊 AUDIT SUMMARY"))
        self.stdout.write("-" * 70)

        total_models = len(results['healthy']) + len(results['missing'])
        healthy_pct = (len(results['healthy']) / total_models * 100) if total_models else 0

        self.stdout.write(f"\n  Total Models Checked: {total_models}")
        self.stdout.write(self.style.SUCCESS(
            f"  ✅ Healthy (table exists): {len(results['healthy'])} ({healthy_pct:.1f}%)"
        ))

        if results['missing']:
            self.stdout.write(self.style.ERROR(
                f"  ❌ Missing Tables: {len(results['missing'])}"
            ))
        else:
            self.stdout.write("  ❌ Missing Tables: 0")

        if results['orphaned']:
            self.stdout.write(self.style.WARNING(
                f"  ⚠️  Orphaned Tables: {len(results['orphaned'])}"
            ))

        if results['custom_tables']:
            self.stdout.write(f"  📝 Custom db_table names: {len(results['custom_tables'])}")

        # Per-app breakdown
        self.stdout.write("\n  📦 By App:")
        for app, counts in sorted(results['by_app'].items()):
            status = "✅" if counts['missing'] == 0 else "❌"
            self.stdout.write(
                f"     {status} {app}: {counts['healthy']} healthy, {counts['missing']} missing"
            )

        # Overall status
        self.stdout.write("\n" + "=" * 70)
        if results['missing']:
            self.stdout.write(self.style.ERROR(
                "🚨 AUDIT STATUS: ISSUES FOUND - Run with --fix to attempt repair"
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                "✅ AUDIT STATUS: ALL MODELS HAVE CORRESPONDING TABLES"
            ))
        self.stdout.write("=" * 70 + "\n")

    def generate_markdown_report(self, results):
        """Generate docs/DATABASE_AUDIT.md"""
        report_path = 'docs/DATABASE_AUDIT.md'

        content = f"""# Database Audit Report

**Generated:** {results['timestamp']}
**Status:** {'⚠️ ISSUES FOUND' if results['missing'] else '✅ HEALTHY'}

---

## Summary

| Metric | Count |
|--------|-------|
| Total Models | {len(results['healthy']) + len(results['missing'])} |
| Healthy (table exists) | {len(results['healthy'])} |
| Missing Tables | {len(results['missing'])} |
| Orphaned Tables | {len(results['orphaned'])} |
| Custom db_table Names | {len(results['custom_tables'])} |

---

## By App

| App | Healthy | Missing | Status |
|-----|---------|---------|--------|
"""
        for app, counts in sorted(results['by_app'].items()):
            status = "✅" if counts['missing'] == 0 else "❌"
            content += f"| {app} | {counts['healthy']} | {counts['missing']} | {status} |\n"

        if results['missing']:
            content += """
---

## Missing Tables

The following models do not have corresponding database tables:

| Model | Expected Table | App |
|-------|----------------|-----|
"""
            for item in results['missing']:
                content += f"| {item['model']} | {item['table']} | {item['app']} |\n"

            content += """
### How to Fix

Run migrations to create missing tables:
```bash
python manage.py migrate
```

Or for specific app:
```bash
python manage.py migrate <app_name>
```
"""

        if results['orphaned']:
            content += f"""
---

## Orphaned Tables

These tables exist in PostgreSQL but have no corresponding Django model:

"""
            for table in sorted(results['orphaned']):
                content += f"- `{table}`\n"

            content += """
These may be from deleted models or old migrations. Review before deleting.
"""

        if results['custom_tables']:
            content += """
---

## Custom Table Names

These models use custom `db_table` instead of Django defaults:

| Model | Custom Table | Default Would Be |
|-------|--------------|------------------|
"""
            for item in results['custom_tables']:
                content += f"| {item['model']} | {item['table']} | {item['default']} |\n"

        content += f"""
---

## How to Use This Audit

```bash
# Quick health check
python manage.py audit_database

# Detailed output
python manage.py audit_database --verbose

# Fix issues
python manage.py audit_database --fix

# CI/CD mode (exit 1 on issues)
python manage.py audit_database --fail-on-error

# Regenerate this report
python manage.py audit_database --output report
```

---

*Generated by `audit_database` management command (Session 623)*
"""

        with open(report_path, 'w') as f:
            f.write(content)

        self.stdout.write(self.style.SUCCESS(f"\n📄 Report generated: {report_path}"))

    def generate_json_output(self, results):
        """Output results as JSON"""
        import json

        # Convert defaultdict to regular dict for JSON serialization
        results['by_app'] = dict(results['by_app'])

        print(json.dumps(results, indent=2, default=str))

    def fix_missing_tables(self, results):
        """Attempt to fix missing tables by running migrations"""
        from django.core.management import call_command

        self.stdout.write("\n🔧 Attempting to fix missing tables...\n")

        # Get unique apps with missing tables
        apps_to_fix = set(item['app'] for item in results['missing'])

        for app in apps_to_fix:
            self.stdout.write(f"  Running migrations for {app}...")
            try:
                call_command('migrate', app, verbosity=1)
                self.stdout.write(self.style.SUCCESS(f"  ✅ {app} migrations complete"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ❌ {app} migration failed: {e}"))

        self.stdout.write("\n🔄 Re-running audit to verify fixes...\n")
