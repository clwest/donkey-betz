#!/usr/bin/env python3
"""
Fix aioredis imports across the codebase
Replaces deprecated aioredis with redis.asyncio
"""

import os
import re

files_to_fix = [
    "backend/agents/spider_data_mixin.py",
    "backend/spiders/spider_connector_orchestrator.py",
    "backend/spiders/spider_data_router.py",
    "backend/spiders/monitoring_dashboard.py",
    "backend/spiders/income_builder_connector.py",
    "backend/spiders/advisor_data_processor.py",
    "backend/spiders/agent_data_receiver.py",
    "backend/spiders/data_pipeline.py",
]

def fix_file(filepath):
    """Fix aioredis imports in a single file"""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Check if file needs fixing
        if 'import aioredis' not in content:
            print(f"✓ {filepath} - already fixed or no aioredis import")
            return

        # Replace standalone import
        if 'import aioredis\n' in content:
            content = content.replace('import aioredis\n', 'from redis import asyncio as aioredis\n')

        # Replace from aioredis import
        content = re.sub(
            r'from aioredis import (.+)',
            r'from redis.asyncio import \1',
            content
        )

        # Special case: if both redis and aioredis are imported
        if 'import redis\n' in content and 'from redis import asyncio as aioredis\n' in content:
            # Already handled correctly
            pass

        # Write back
        with open(filepath, 'w') as f:
            f.write(content)

        print(f"✅ Fixed {filepath}")

    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
    except Exception as e:
        print(f"❌ Error fixing {filepath}: {e}")

def main():
    print("Fixing aioredis imports across the codebase...\n")

    for filepath in files_to_fix:
        fix_file(filepath)

    print("\n✨ aioredis fix complete!")
    print("\nNext steps:")
    print("1. Restart the Django server to reload the fixed imports")
    print("2. Test content agents to verify they work")

if __name__ == "__main__":
    main()