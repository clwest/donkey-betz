#!/usr/bin/env python3
"""
Force clear ALL action plans from the system
"""

import os
import sys
import django
import redis
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
django.setup()

from django.core.cache import cache
from django.db import connection

print("=" * 80)
print("🔥 FORCE CLEARING ALL ACTION PLANS FROM THE SYSTEM")
print("=" * 80)
print()

# 1. Clear from database tables
print("1️⃣ Clearing database tables...")
with connection.cursor() as cursor:
    tables_to_check = [
        'intelligence_actionplan',
        'agents_actionplan',
        'core_actionplan',
        'income_actionplan'
    ]

    for table in tables_to_check:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            if count > 0:
                cursor.execute(f"DELETE FROM {table}")
                print(f"  ✅ Deleted {count} records from {table}")
        except Exception as e:
            # Table doesn't exist, that's fine
            pass

# 2. Clear from Django cache
print("\n2️⃣ Clearing Django cache...")
cache_keys = [
    'action_plans',
    'income_action_plans',
    'incomeBuilderActionPlans',
    'actionPlans',
    'plans',
    'income_builder_plans'
]

for key in cache_keys:
    try:
        cache.delete(key)
        print(f"  ✅ Cleared cache key: {key}")
    except:
        pass

# Also clear pattern-based cache
try:
    cache.delete_many(cache.keys("*action*plan*"))
    cache.delete_many(cache.keys("*plan*"))
    print("  ✅ Cleared all action plan related cache patterns")
except:
    pass

# 3. Clear from Redis directly
print("\n3️⃣ Clearing Redis directly...")
try:
    r = redis.Redis(host='localhost', port=6379, db=0)

    # Find and delete all keys related to action plans
    patterns = ['*action*plan*', '*plan*', '*income*builder*']
    total_deleted = 0

    for pattern in patterns:
        keys = r.keys(pattern)
        if keys:
            deleted = r.delete(*keys)
            total_deleted += deleted
            print(f"  ✅ Deleted {deleted} Redis keys matching '{pattern}'")

    if total_deleted == 0:
        print("  ℹ️  No action plan keys found in Redis")

except Exception as e:
    print(f"  ⚠️  Redis error: {e}")

# 4. Clear files from filesystem
print("\n4️⃣ Clearing action plan files...")
directories = [
    'income_builder_outputs',
    'agent_outputs',
    'static/income_builder_outputs'
]

files_deleted = 0
for directory in directories:
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            if 'plan' in filename.lower() or 'action' in filename.lower():
                try:
                    filepath = os.path.join(directory, filename)
                    os.remove(filepath)
                    files_deleted += 1
                    print(f"  ✅ Deleted: {filename}")
                except Exception as e:
                    print(f"  ⚠️  Could not delete {filename}: {e}")

if files_deleted == 0:
    print("  ℹ️  No action plan files found")

# 5. Clear from session storage (if using database sessions)
print("\n5️⃣ Clearing session data...")
try:
    with connection.cursor() as cursor:
        cursor.execute("""
            DELETE FROM django_session
            WHERE session_data LIKE '%action%plan%'
        """)
        count = cursor.rowcount
        if count > 0:
            print(f"  ✅ Cleared {count} sessions with action plans")
        else:
            print("  ℹ️  No sessions with action plans found")
except Exception as e:
    print(f"  ⚠️  Session clear error: {e}")

# 6. Create a marker to tell frontend to clear localStorage
print("\n6️⃣ Setting frontend clear marker...")
try:
    cache.set('CLEAR_ACTION_PLANS_MARKER', True, 3600)
    print("  ✅ Set marker for frontend to clear localStorage")
except:
    pass

print()
print("=" * 80)
print("✅ FORCE CLEAR COMPLETE!")
print("=" * 80)
print()
print("Action plans have been cleared from:")
print("  • Database tables")
print("  • Django cache")
print("  • Redis storage")
print("  • File system")
print("  • Session data")
print()
print("⚠️  IMPORTANT: You must also clear browser localStorage:")
print("  1. Open browser DevTools (F12)")
print("  2. Go to Console tab")
print("  3. Run: localStorage.removeItem('incomeBuilderActionPlans')")
print("  4. Refresh the page")
print()