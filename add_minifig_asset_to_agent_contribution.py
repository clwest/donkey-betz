#!/usr/bin/env python3
"""
Add minifig_asset field to AgentContribution model.

This migration adds support for tracking 3D model generation agent contributions.
"""
import os
import sys
import django

sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection

# SQL to add the minifig_asset field
sql = """
ALTER TABLE agent_contributions
ADD COLUMN IF NOT EXISTS minifig_asset_id UUID NULL
REFERENCES content_minifigasset(id) ON DELETE CASCADE;
"""

try:
    with connection.cursor() as cursor:
        cursor.execute(sql)
        print("✅ Successfully added minifig_asset_id column to agent_contributions table")
        print("   This enables 3D model agent tracking!")
except Exception as e:
    if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
        print("⚠️  Column minifig_asset_id already exists - skipping")
    else:
        print(f"❌ Error: {e}")
        sys.exit(1)
