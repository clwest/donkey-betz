#!/usr/bin/env python
"""
Check actual database counts to verify what's really stored
"""

import os
import sys
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection

print("\n" + "=" * 60)
print("📊 Actual Database Counts")
print("=" * 60 + "\n")

try:
    with connection.cursor() as cursor:
        # Check unified embeddings
        try:
            cursor.execute("SELECT COUNT(*) FROM self_awareness_unifiedembedding")
            count = cursor.fetchone()[0]
            print(f"Unified Embeddings: {count}")
        except Exception as e:
            print(f"Unified Embeddings: Error - {e}")

        # Check user memories
        try:
            cursor.execute("SELECT COUNT(*) FROM core_usermemorycontext")
            count = cursor.fetchone()[0]
            print(f"User Memory Contexts: {count}")
        except Exception as e:
            print(f"User Memory Contexts: Error - {e}")

        # Check user embeddings
        try:
            cursor.execute("SELECT COUNT(*) FROM core_userembedding")
            count = cursor.fetchone()[0]
            print(f"User Embeddings: {count}")
        except Exception as e:
            print(f"User Embeddings: Error - {e}")

        # Check recent memories
        try:
            cursor.execute("""
                SELECT COUNT(*), MAX(created_at)
                FROM core_usermemorycontext
            """)
            count, latest = cursor.fetchone()
            print(f"\nRecent Activity:")
            print(f"  Total memories: {count}")
            print(f"  Latest memory: {latest}")
        except Exception as e:
            print(f"Recent Activity: Error - {e}")

except Exception as e:
    print(f"Database connection error: {e}")

print("\n" + "=" * 60)