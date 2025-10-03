#!/usr/bin/env python3
"""
Database Mock Data Audit Script
Checks ALL models for mock/placeholder data patterns
Usage: python3 manage.py shell < scripts/audit_database_mock_data.py
"""

from django.apps import apps
import re

print("=" * 80)
print("DATABASE MOCK DATA AUDIT")
print("=" * 80)
print()

# Patterns to check for
MOCK_PATTERNS = {
    'example.com': 'Mock URL pattern',
    'placeholder': 'Placeholder text',
    'demo': 'Demo data',
    'test': 'Test data',
    'fake': 'Fake data',
    'mock': 'Mock data',
    'lorem ipsum': 'Lorem ipsum text',
}

# URL fields to check
URL_FIELD_NAMES = ['url', 'source', 'link', 'href', 'source_url', 'website']

# Get all models
models = apps.get_models()

total_issues = 0
issues_by_model = {}

for model in models:
    table_name = model._meta.db_table
    model_name = model.__name__
    app_label = model._meta.app_label

    # Skip Django internal models
    if model_name.startswith('_'):
        continue
    if 'django' in app_label or 'admin' in app_label or 'auth' in app_label:
        continue
    if 'contenttypes' in app_label or 'sessions' in app_label:
        continue

    try:
        total = model.objects.count()
        if total == 0:
            continue

        print(f"\n{'=' * 80}")
        print(f"{app_label}.{model_name} ({table_name}): {total} records")
        print('=' * 80)

        model_issues = []

        # Check each field
        for field in model._meta.fields:
            field_name = field.name
            field_type = field.get_internal_type()

            # Only check text fields
            if field_type not in ['CharField', 'TextField', 'URLField', 'EmailField']:
                continue

            # Check for each mock pattern
            for pattern, description in MOCK_PATTERNS.items():
                try:
                    filter_kwargs = {f"{field_name}__icontains": pattern}
                    mock_count = model.objects.filter(**filter_kwargs).count()

                    if mock_count > 0:
                        issue = {
                            'field': field_name,
                            'pattern': pattern,
                            'count': mock_count,
                            'description': description
                        }
                        model_issues.append(issue)
                        total_issues += 1

                        print(f"⚠️  {field_name}: {mock_count} records with '{pattern}' ({description})")

                        # Show sample
                        sample = model.objects.filter(**filter_kwargs).first()
                        if sample:
                            value = getattr(sample, field_name)
                            print(f"   Sample: {value[:100] if value else 'N/A'}...")

                except Exception as e:
                    # Some fields might not support icontains
                    pass

        if model_issues:
            issues_by_model[model_name] = model_issues
            print(f"\n⚠️  Total issues in {model_name}: {len(model_issues)}")

            # Suggest cleanup command
            print(f"\n💡 Cleanup suggestion:")
            for issue in model_issues:
                print(f"   {model_name}.objects.filter({issue['field']}__icontains='{issue['pattern']}').delete()")
        else:
            print("✅ No obvious mock data patterns found")

    except Exception as e:
        print(f"❌ Error checking {model_name}: {e}")

# Summary
print("\n" + "=" * 80)
print("AUDIT SUMMARY")
print("=" * 80)
print(f"\nTotal issues found: {total_issues}")
print(f"Models affected: {len(issues_by_model)}")

if issues_by_model:
    print("\n⚠️  MODELS WITH ISSUES:")
    for model_name, issues in issues_by_model.items():
        print(f"\n{model_name}:")
        for issue in issues:
            print(f"  - {issue['field']}: {issue['count']} records with '{issue['pattern']}'")

    print("\n" + "=" * 80)
    print("RECOMMENDED ACTIONS:")
    print("=" * 80)
    print("\n1. Review the samples above to confirm they are mock data")
    print("2. Use the suggested cleanup commands to delete mock records")
    print("3. Re-run this audit to verify cleanup")
    print("\n⚠️  WARNING: Always verify with .count() before using .delete()!")

else:
    print("\n✅ No mock data patterns found in any models!")
    print("   Database appears clean.")

print("\n" + "=" * 80)
print("AUDIT COMPLETE")
print("=" * 80)
