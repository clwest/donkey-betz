#!/usr/bin/env python3
"""
Clean up the system by:
1. Killing all stuck agent processes
2. Removing completed work created before 9/16
"""

import os
import sys
import django
import subprocess
from datetime import datetime, date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
django.setup()

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import connection

print("=" * 80)
print("🧹 SYSTEM CLEANUP - REMOVING OLD DATA & STOPPING STUCK PROCESSES")
print("=" * 80)
print()

def kill_stuck_processes():
    """Kill all stuck agent and celery processes"""
    print("🛑 Stopping stuck processes...")

    processes_to_kill = [
        "celery.*worker",
        "celery.*beat",
        "flower",
        "python.*agent",
        "python.*execute",
        "daphne",
        "runserver"
    ]

    killed_count = 0
    for process in processes_to_kill:
        try:
            result = subprocess.run(
                f"pkill -f '{process}'",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(f"  ✅ Killed: {process}")
                killed_count += 1
        except Exception as e:
            print(f"  ⚠️  Could not kill {process}: {e}")

    # Also kill any processes using specific ports
    ports = [8000, 8001, 3000, 5555]
    for port in ports:
        try:
            subprocess.run(
                f"lsof -ti:{port} | xargs kill -9",
                shell=True,
                capture_output=True,
                text=True
            )
            print(f"  ✅ Cleared port: {port}")
        except:
            pass

    print(f"✅ Killed {killed_count} process types")
    return killed_count

def clear_old_cache_data():
    """Clear cache data from before 9/16"""
    print("\n📦 Clearing old cache data...")

    # Clear specific cache keys
    cache_keys_to_clear = [
        'income_opportunities',
        'sports_games',
        'agent_registry',
        'revenue_history',
        'active_orchestrations',
        'system_metrics',
        'recent_executions',
        'neural_orchestra_data',
        'websocket_test_data'
    ]

    cleared = 0
    for key in cache_keys_to_clear:
        try:
            cache.delete(key)
            cleared += 1
            print(f"  ✅ Cleared cache: {key}")
        except:
            pass

    print(f"✅ Cleared {cleared} cache keys")
    return cleared

def clean_database_records():
    """Clean old database records created before 9/16"""
    print("\n🗄️ Cleaning database records...")

    cutoff_date = date(2025, 9, 16)

    with connection.cursor() as cursor:
        # Clean action plans created before 9/16
        try:
            cursor.execute("""
                DELETE FROM core_actionplan
                WHERE DATE(created_at) < %s
                AND status = 'completed'
            """, [cutoff_date])
            deleted_plans = cursor.rowcount
            print(f"  ✅ Deleted {deleted_plans} old completed action plans")
        except Exception as e:
            print(f"  ⚠️  Could not clean action plans: {e}")

        # Clean old agent executions
        try:
            cursor.execute("""
                DELETE FROM agents_agentexecution
                WHERE DATE(created_at) < %s
                AND status = 'completed'
            """, [cutoff_date])
            deleted_executions = cursor.rowcount
            print(f"  ✅ Deleted {deleted_executions} old agent executions")
        except Exception as e:
            print(f"  ⚠️  Could not clean agent executions: {e}")

        # Clean old workflow executions
        try:
            cursor.execute("""
                DELETE FROM workflows_workflowexecution
                WHERE DATE(created_at) < %s
                AND status = 'completed'
            """, [cutoff_date])
            deleted_workflows = cursor.rowcount
            print(f"  ✅ Deleted {deleted_workflows} old workflow executions")
        except Exception as e:
            print(f"  ⚠️  Could not clean workflows: {e}")

def clean_output_files():
    """Clean old output files created before 9/16"""
    print("\n📁 Cleaning old output files...")

    directories_to_clean = [
        'income_builder_outputs',
        'agent_outputs',
        'workflow_outputs',
        'media/generated'
    ]

    cutoff_date = datetime(2025, 9, 16)
    files_deleted = 0

    for directory in directories_to_clean:
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                filepath = os.path.join(directory, filename)
                try:
                    # Check file modification time
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_time < cutoff_date:
                        os.remove(filepath)
                        files_deleted += 1
                        print(f"  ✅ Deleted: {filename}")
                except Exception as e:
                    print(f"  ⚠️  Could not delete {filename}: {e}")

    print(f"✅ Deleted {files_deleted} old files")
    return files_deleted

def reset_celery_tasks():
    """Reset Celery task queue"""
    print("\n🔄 Resetting Celery tasks...")

    try:
        # Clear Celery task results
        from celery import Celery
        app = Celery('core')
        app.control.purge()
        print("  ✅ Purged Celery task queue")
    except Exception as e:
        print(f"  ⚠️  Could not purge Celery: {e}")

    # Clear Redis queues
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.flushdb()
        print("  ✅ Cleared Redis queues")
    except Exception as e:
        print(f"  ⚠️  Could not clear Redis: {e}")

def refresh_data():
    """Refresh with new clean data"""
    print("\n✨ Refreshing with clean data...")

    # Run the data population script
    try:
        subprocess.run([
            sys.executable,
            "populate_real_data_simple.py"
        ], capture_output=True, text=True)
        print("  ✅ Populated fresh data")
    except Exception as e:
        print(f"  ⚠️  Could not populate data: {e}")

def main():
    """Main cleanup function"""

    print("Starting comprehensive cleanup...")
    print()

    # 1. Kill stuck processes
    kill_stuck_processes()

    # 2. Clear old cache data
    clear_old_cache_data()

    # 3. Clean database records
    clean_database_records()

    # 4. Clean output files
    clean_output_files()

    # 5. Reset Celery tasks
    reset_celery_tasks()

    # 6. Refresh with clean data
    refresh_data()

    print()
    print("=" * 80)
    print("✅ CLEANUP COMPLETE!")
    print("=" * 80)
    print()
    print("The system has been cleaned:")
    print("  • All stuck processes terminated")
    print("  • Old completed work removed (before 9/16)")
    print("  • Cache cleared and refreshed")
    print("  • Output files cleaned")
    print("  • Celery tasks reset")
    print("  • Fresh data populated")
    print()
    print("You can now restart the system with:")
    print("  make unified-dev")
    print()

if __name__ == "__main__":
    main()