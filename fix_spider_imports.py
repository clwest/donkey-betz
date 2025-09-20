#!/usr/bin/env python
"""
Fix Spider Army Module Import Paths
====================================

This script fixes the incorrect module paths in the spider orchestrator
that are preventing the full 1,770 spider deployment.
"""

import os
import re

def fix_spider_imports():
    """Fix the spider module import paths"""

    orchestrator_path = 'intelligence/spiders/spider_army/orchestrator.py'

    print("🔧 Fixing spider module import paths...")

    # Read the file
    with open(orchestrator_path, 'r') as f:
        content = f.read()

    # Count original occurrences
    original_count = content.count("'spider_army.spiders.")
    print(f"Found {original_count} instances of incorrect module paths")

    # Fix the module paths
    # Change 'spider_army.spiders.' to 'intelligence.spiders.spider_army.spiders.'
    content = content.replace(
        "'spider_army.spiders.",
        "'intelligence.spiders.spider_army.spiders."
    )

    # Write the fixed content back
    with open(orchestrator_path, 'w') as f:
        f.write(content)

    # Verify the fix
    with open(orchestrator_path, 'r') as f:
        fixed_content = f.read()

    fixed_count = fixed_content.count("'intelligence.spiders.spider_army.spiders.")
    print(f"✅ Fixed {fixed_count} module paths")

    # Also check for any remaining incorrect paths
    remaining = fixed_content.count("'spider_army.spiders.")
    if remaining > 0:
        print(f"⚠️ Warning: {remaining} incorrect paths still remain")
    else:
        print("✅ All module paths have been corrected!")

    return fixed_count

if __name__ == "__main__":
    fixed = fix_spider_imports()
    print(f"\n🎯 Spider module import fix complete!")
    print(f"The orchestrator should now be able to deploy all 1,770 spiders.")
    print("\n📝 Next steps:")
    print("1. Run: python manage.py deploy_spider_army --action deploy")
    print("2. Check the deployment status")
    print("3. Verify spiders are actively running")