#!/usr/bin/env python
"""
Model Audit Script for HANDOFF_04: Database Consolidation

This script analyzes all Django models in the codebase to identify:
1. All model classes and their locations
2. Usage of each model across the codebase
3. Potential orphaned/unused models
4. Duplicate or near-duplicate models

Run with: python scripts/audit_models.py
"""

import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Directories to skip when searching for usage
SKIP_DIRS = {
    'migrations', '__pycache__', '.venv', 'venv', 'node_modules',
    '.git', 'staticfiles', 'media', 'logs', '.pytest_cache',
    'htmlcov', 'docs/archive'
}

# Files to skip
SKIP_FILES = {'audit_models.py'}

# Model files to analyze
MODEL_FILES = [
    'content/models.py',
    'agents/models.py',
    'core/models_unified_system.py',
    'core/models.py',  # Check if exists
]


def find_model_classes(filepath):
    """Extract model class names and their base classes from a file."""
    models = []

    if not os.path.exists(filepath):
        return models

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match class definitions that inherit from Model-like classes
    # Matches: class ClassName(BaseClass, Mixin, ...):
    pattern = r'^class\s+(\w+)\s*\(([^)]+)\)\s*:'

    for match in re.finditer(pattern, content, re.MULTILINE):
        class_name = match.group(1)
        bases = match.group(2)

        # Check if it's a Django model (inherits from Model, UnifiedBaseModel, etc.)
        model_bases = ['Model', 'UnifiedBaseModel', 'models.Model']
        is_model = any(base.strip() in bases for base in model_bases)

        # Skip TextChoices, Enum, and other non-model classes
        skip_bases = ['TextChoices', 'Enum', 'Exception', 'Mixin']
        is_skip = any(skip in bases for skip in skip_bases)

        if is_model and not is_skip:
            # Get line number
            line_num = content[:match.start()].count('\n') + 1
            models.append({
                'name': class_name,
                'bases': bases.strip(),
                'line': line_num,
                'file': filepath
            })

    return models


def find_model_usage(model_name, directory='.'):
    """Find where a model is used in the codebase."""
    usages = []

    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

        for filename in files:
            if filename in SKIP_FILES:
                continue
            if not filename.endswith('.py'):
                continue

            filepath = os.path.join(root, filename)

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (IOError, UnicodeDecodeError):
                continue

            # Count occurrences of the model name
            # Use word boundaries to avoid partial matches
            pattern = rf'\b{re.escape(model_name)}\b'
            matches = re.findall(pattern, content)
            count = len(matches)

            if count > 0:
                # Get context (imports, usage type)
                is_import = f'import {model_name}' in content or f'from.*import.*{model_name}' in content
                is_foreign_key = f"'{model_name}'" in content or f'"{model_name}"' in content

                usages.append({
                    'file': filepath,
                    'count': count,
                    'is_import': is_import,
                    'is_foreign_key': is_foreign_key
                })

    return usages


def find_duplicate_models(all_models):
    """Find models with the same name in different files."""
    name_to_files = defaultdict(list)

    for model in all_models:
        name_to_files[model['name']].append(model['file'])

    duplicates = {name: files for name, files in name_to_files.items() if len(files) > 1}
    return duplicates


def analyze_model_fields(filepath, model_name):
    """Extract field names from a model to help identify similar models."""
    if not os.path.exists(filepath):
        return []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the model class definition
    pattern = rf'^class\s+{model_name}\s*\([^)]+\)\s*:(.+?)(?=^class\s|\Z)'
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)

    if not match:
        return []

    class_body = match.group(1)

    # Find field definitions
    field_pattern = r'^\s+(\w+)\s*=\s*models\.\w+\('
    fields = re.findall(field_pattern, class_body, re.MULTILINE)

    return fields


def main():
    print("=" * 80)
    print("MODEL AUDIT REPORT")
    print("=" * 80)
    print()

    # Step 1: Find all models
    print("STEP 1: Finding all model classes...")
    print("-" * 40)

    all_models = []
    for model_file in MODEL_FILES:
        if os.path.exists(model_file):
            models = find_model_classes(model_file)
            all_models.extend(models)
            print(f"\n{model_file}: {len(models)} models")
            for m in models:
                print(f"  Line {m['line']:4d}: {m['name']}")

    print(f"\nTotal models found: {len(all_models)}")

    # Step 2: Find duplicates
    print("\n" + "=" * 80)
    print("STEP 2: Checking for duplicate model names...")
    print("-" * 40)

    duplicates = find_duplicate_models(all_models)
    if duplicates:
        print(f"\nFound {len(duplicates)} duplicate model names:")
        for name, files in duplicates.items():
            print(f"\n  {name}:")
            for f in files:
                print(f"    - {f}")
    else:
        print("\nNo duplicate model names found.")

    # Step 3: Analyze usage
    print("\n" + "=" * 80)
    print("STEP 3: Analyzing model usage across codebase...")
    print("-" * 40)

    unused_models = []
    low_usage_models = []
    well_used_models = []

    for model in all_models:
        model_name = model['name']
        usages = find_model_usage(model_name)

        # Filter out the definition file itself
        external_usages = [u for u in usages if u['file'] != model['file']]
        total_external = sum(u['count'] for u in external_usages)

        model['usages'] = external_usages
        model['total_external_refs'] = total_external
        model['usage_files'] = len(external_usages)

        if total_external == 0:
            unused_models.append(model)
        elif total_external <= 3:
            low_usage_models.append(model)
        else:
            well_used_models.append(model)

    # Report unused models
    print(f"\n\nUNUSED MODELS ({len(unused_models)}) - Candidates for removal:")
    print("-" * 60)
    for m in sorted(unused_models, key=lambda x: x['file']):
        print(f"  {m['name']:40s} ({m['file']}:{m['line']})")

    # Report low usage models
    print(f"\n\nLOW USAGE MODELS ({len(low_usage_models)}) - Review for consolidation:")
    print("-" * 60)
    for m in sorted(low_usage_models, key=lambda x: x['total_external_refs']):
        print(f"  {m['name']:40s} {m['total_external_refs']} refs in {m['usage_files']} files")

    # Report well-used models
    print(f"\n\nWELL-USED MODELS ({len(well_used_models)}) - Keep:")
    print("-" * 60)
    for m in sorted(well_used_models, key=lambda x: -x['total_external_refs'])[:30]:
        print(f"  {m['name']:40s} {m['total_external_refs']} refs in {m['usage_files']} files")
    if len(well_used_models) > 30:
        print(f"  ... and {len(well_used_models) - 30} more")

    # Step 4: Categorize by purpose
    print("\n" + "=" * 80)
    print("STEP 4: Categorizing models by purpose...")
    print("-" * 40)

    categories = {
        'Content/Media': ['Image', 'Video', 'Audio', 'Document', 'Content', 'Media', 'MiniFig', 'Character'],
        'Agents': ['Agent', 'Execution', 'Orchestration', 'Tool', 'Registry'],
        'Spider/Intelligence': ['Spider', 'Trend', 'Opportunity', 'Insight'],
        'Revenue/Distribution': ['Revenue', 'Payment', 'Distribution', 'Platform', 'Pricing'],
        'Sci-Fi Features': ['Dream', 'Mood', 'Memory', 'Evolution', 'Relationship', 'Alliance', 'Rivalry',
                           'Prophecy', 'Prediction', 'TimeCapsule', 'Personality', 'HiveMind', 'Conversation'],
        'Analytics/Testing': ['Analytics', 'Metric', 'AB', 'Test', 'Performance', 'Usage', 'Log'],
        'Workflow': ['Workflow', 'Step', 'Schedule'],
        'Collaboration': ['Collaboration', 'Team', 'Message', 'Channel', 'Share', 'Project'],
        'Learning': ['Learning', 'Knowledge', 'Transfer', 'Pattern'],
        'User': ['User', 'Preference', 'Profile', 'Goal', 'Notification'],
    }

    categorized = defaultdict(list)
    uncategorized = []

    for model in all_models:
        name = model['name']
        found_category = False

        for category, keywords in categories.items():
            if any(kw in name for kw in keywords):
                categorized[category].append(model)
                found_category = True
                break

        if not found_category:
            uncategorized.append(model)

    for category, models in sorted(categorized.items()):
        print(f"\n{category}: {len(models)} models")
        for m in models:
            status = "UNUSED" if m['total_external_refs'] == 0 else f"{m['total_external_refs']} refs"
            print(f"  - {m['name']:40s} [{status}]")

    if uncategorized:
        print(f"\nUncategorized: {len(uncategorized)} models")
        for m in uncategorized:
            status = "UNUSED" if m['total_external_refs'] == 0 else f"{m['total_external_refs']} refs"
            print(f"  - {m['name']:40s} [{status}]")

    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"""
Total models:        {len(all_models)}
Unused models:       {len(unused_models)} (candidates for removal)
Low usage models:    {len(low_usage_models)} (review for consolidation)
Well-used models:    {len(well_used_models)} (keep)
Duplicate names:     {len(duplicates)}

Files analyzed:
""")
    for model_file in MODEL_FILES:
        if os.path.exists(model_file):
            size = os.path.getsize(model_file)
            count = len([m for m in all_models if m['file'] == model_file])
            print(f"  {model_file}: {count} models, {size:,} bytes")

    # Write detailed report to file
    report_path = PROJECT_ROOT / 'scripts' / 'model_audit_report.txt'
    with open(report_path, 'w') as f:
        f.write("MODEL AUDIT DETAILED REPORT\n")
        f.write("=" * 80 + "\n\n")

        f.write("UNUSED MODELS (candidates for removal):\n")
        f.write("-" * 40 + "\n")
        for m in sorted(unused_models, key=lambda x: x['name']):
            f.write(f"{m['name']}\n")
            f.write(f"  File: {m['file']}:{m['line']}\n")
            f.write(f"  Bases: {m['bases']}\n\n")

        f.write("\n\nDUPLICATE MODELS:\n")
        f.write("-" * 40 + "\n")
        for name, files in duplicates.items():
            f.write(f"{name}:\n")
            for file in files:
                f.write(f"  - {file}\n")
            f.write("\n")

    print(f"\nDetailed report written to: {report_path}")

    return {
        'all_models': all_models,
        'unused': unused_models,
        'low_usage': low_usage_models,
        'well_used': well_used_models,
        'duplicates': duplicates
    }


if __name__ == '__main__':
    main()
