#!/usr/bin/env python3
"""
Import External Project Documentation to Unified Donkey Betz
Moves all NON-unified-donkey-betz markdown files into organized folder
"""

import json
import shutil
from pathlib import Path
from datetime import datetime

# Source: Documentation intelligence system results
SCAN_RESULTS = Path('/Users/donkeyking/development/documentation-intelligence-system/scan-results')
INVENTORY_FILE = SCAN_RESULTS / 'inventory.json'

# Destination: unified-donkey-betz external docs
UNIFIED_ROOT = Path('/Users/donkeyking/development/unified-donkey-betz')
EXTERNAL_DOCS = UNIFIED_ROOT / 'external-project-docs'

# DO NOT move files from these locations
EXCLUDE_PATHS = [
    '/Users/donkeyking/development/unified-donkey-betz',  # Don't move unified's own files
    'node_modules',
    'venv',
    '.venv',
    '__pycache__',
    '.git'
]

def load_inventory():
    """Load the scan results"""
    print(f"📂 Loading inventory from: {INVENTORY_FILE}")

    if not INVENTORY_FILE.exists():
        print(f"❌ Inventory not found! Run documentation scan first:")
        print(f"   cd /Users/donkeyking/development/documentation-intelligence-system")
        print(f"   python 1_scan_documentation.py")
        return None

    with open(INVENTORY_FILE, 'r') as f:
        inventory = json.load(f)

    print(f"   ✅ Loaded {len(inventory):,} total files")
    return inventory

def filter_external_files(inventory):
    """Filter to ONLY external project files (NOT unified-donkey-betz)"""
    print("\n🔍 Filtering to external project files...")

    external_files = []

    for doc in inventory:
        path = doc['path']

        # Skip if it's from unified-donkey-betz
        if any(exclude in path for exclude in EXCLUDE_PATHS):
            continue

        # Skip if status is archived
        if doc.get('status') == 'archived':
            continue

        external_files.append(doc)

    print(f"   ✅ Found {len(external_files):,} external project files")

    # Show breakdown by project
    projects = {}
    for doc in external_files:
        project = doc.get('project', 'unknown')
        projects[project] = projects.get(project, 0) + 1

    print(f"\n   By Project:")
    for project, count in sorted(projects.items(), key=lambda x: x[1], reverse=True):
        print(f"      • {project}: {count:,} files")

    return external_files

def organize_and_move_files(external_files, dry_run=True):
    """Organize external files by project and move them"""
    print(f"\n{'🔍 DRY RUN - ' if dry_run else '📦 MOVING '}Organizing external documentation...")

    # Create base directory
    if not dry_run:
        EXTERNAL_DOCS.mkdir(parents=True, exist_ok=True)

    stats = {
        'moved': 0,
        'skipped': 0,
        'errors': 0
    }

    # Organize by project
    for doc in external_files:
        try:
            source_path = Path(doc['path'])
            project = doc.get('project', 'unknown')
            category = doc.get('category', 'general')

            # Create destination path: external-project-docs/{project}/{category}/
            dest_dir = EXTERNAL_DOCS / project / category
            dest_file = dest_dir / source_path.name

            # Handle duplicate filenames
            counter = 1
            while dest_file.exists():
                stem = source_path.stem
                suffix = source_path.suffix
                dest_file = dest_dir / f"{stem}_{counter}{suffix}"
                counter += 1

            print(f"   {source_path.name}")
            print(f"      → {dest_file.relative_to(UNIFIED_ROOT)}")

            if not dry_run:
                dest_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, dest_file)

            stats['moved'] += 1

        except Exception as e:
            print(f"      ❌ Error: {e}")
            stats['errors'] += 1

    return stats

def generate_index(external_files):
    """Generate index of imported documentation"""
    print(f"\n📝 Generating index...")

    index_file = EXTERNAL_DOCS / 'INDEX.md'

    # Organize by project
    by_project = {}
    for doc in external_files:
        project = doc.get('project', 'unknown')
        if project not in by_project:
            by_project[project] = []
        by_project[project].append(doc)

    with open(index_file, 'w') as f:
        f.write("# External Project Documentation Index\n\n")
        f.write(f"**Imported**: {datetime.now().isoformat()}\n")
        f.write(f"**Total Files**: {len(external_files):,}\n\n")
        f.write("---\n\n")

        for project, docs in sorted(by_project.items()):
            f.write(f"## {project.upper()} ({len(docs)} files)\n\n")

            # Organize by category
            by_category = {}
            for doc in docs:
                category = doc.get('category', 'general')
                if category not in by_category:
                    by_category[category] = []
                by_category[category].append(doc)

            for category, cat_docs in sorted(by_category.items()):
                f.write(f"### {category} ({len(cat_docs)} files)\n\n")
                for doc in sorted(cat_docs, key=lambda x: x.get('title', '')):
                    title = doc.get('title') or doc['filename']
                    rel_path = f"{project}/{doc.get('category', 'general')}/{doc['filename']}"
                    f.write(f"- [{title}](./{rel_path})\n")
                f.write("\n")

            f.write("\n")

    print(f"   ✅ Index created: {index_file}")
    return index_file

def main():
    """Main execution"""
    import sys

    # Check for auto-confirm flag
    auto_confirm = '--yes' in sys.argv or '-y' in sys.argv

    print("=" * 70)
    print("📥 Import External Project Documentation")
    print("=" * 70)
    print(f"\nSource: All projects EXCEPT unified-donkey-betz")
    print(f"Destination: {EXTERNAL_DOCS}\n")

    # 1. Load inventory
    inventory = load_inventory()
    if not inventory:
        return

    # 2. Filter to external files only
    external_files = filter_external_files(inventory)

    if not external_files:
        print("\n⚠️  No external files found!")
        return

    # 3. Show what will be moved (dry run)
    print(f"\n{'='*70}")
    print("DRY RUN - Preview")
    print(f"{'='*70}")
    stats_dry = organize_and_move_files(external_files, dry_run=True)

    print(f"\n📊 Dry Run Summary:")
    print(f"   • Files to move: {stats_dry['moved']:,}")
    print(f"   • Errors: {stats_dry['errors']}")

    # 4. Confirm
    print(f"\n⚠️  This will COPY {len(external_files):,} files to:")
    print(f"   {EXTERNAL_DOCS}")
    print(f"\n   Structure: external-project-docs/{{project}}/{{category}}/{{filename}}")

    if auto_confirm:
        print(f"\n✅ Auto-confirmed (--yes flag)")
        response = 'yes'
    else:
        response = input(f"\n❓ Proceed with import? (yes/no): ").strip().lower()

    if response != 'yes':
        print("   ❌ Cancelled")
        return

    # 5. Actually move files
    print(f"\n{'='*70}")
    print("IMPORTING FILES")
    print(f"{'='*70}")
    stats = organize_and_move_files(external_files, dry_run=False)

    # 6. Generate index
    index_file = generate_index(external_files)

    # 7. Summary
    print(f"\n{'='*70}")
    print("✅ IMPORT COMPLETE")
    print(f"{'='*70}")
    print(f"\n📊 Final Summary:")
    print(f"   • Files imported: {stats['moved']:,}")
    print(f"   • Errors: {stats['errors']}")
    print(f"   • Location: {EXTERNAL_DOCS}")
    print(f"   • Index: {index_file}")

    print(f"\n📁 Directory Structure:")
    print(f"   unified-donkey-betz/")
    print(f"   └── external-project-docs/")
    print(f"       ├── ai-content-studio/")
    print(f"       ├── dbao-studio/")
    print(f"       ├── root-agents/")
    print(f"       ├── archive/")
    print(f"       └── INDEX.md")

    print(f"\n✅ All external documentation now in unified-donkey-betz!")
    print(f"✅ Organized by project and category")
    print(f"✅ Original files unchanged (copied, not moved)")

if __name__ == "__main__":
    main()
