#!/usr/bin/env python3
"""
Test script to verify AI Job Market Intelligence system is ready
"""

import sys
import os
import django
import redis
import asyncio
import json
from datetime import datetime


def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")

    dependencies = {
        'Django': True,
        'Redis': True,
        'Channels': True,
        'AsyncIO': True
    }

    # Check Django
    try:
        import django
        print(f"✅ Django {django.VERSION[0]}.{django.VERSION[1]} installed")
    except ImportError:
        print("❌ Django not installed")
        dependencies['Django'] = False

    # Check Channels
    try:
        import channels
        print("✅ Channels installed")
    except ImportError:
        print("❌ Channels not installed")
        dependencies['Channels'] = False

    # Check Redis connection
    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis is running and accessible")
    except:
        print("❌ Redis is not running or not accessible")
        dependencies['Redis'] = False

    return all(dependencies.values())


def check_files():
    """Check if all required files exist"""
    print("\nChecking required files...")

    files = {
        'AI Training System': 'ai_job_market_intelligence.py',
        'WebSocket Consumer': 'core/consumers_ai_training.py',
        'Dashboard HTML': 'ai_job_market_dashboard.html',
        'Launch Script': 'launch_ai_training.sh',
        'Dashboard View': 'core/views_ai_training.py'
    }

    all_exist = True
    for name, filepath in files.items():
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filepath)
        if os.path.exists(full_path):
            print(f"✅ {name}: {filepath}")
        else:
            print(f"❌ {name}: {filepath} - NOT FOUND")
            all_exist = False

    return all_exist


def test_redis_pubsub():
    """Test Redis pub/sub functionality"""
    print("\nTesting Redis pub/sub...")

    try:
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)

        # Test publish
        test_data = {
            'type': 'test',
            'timestamp': datetime.now().isoformat(),
            'message': 'Redis pub/sub test'
        }

        r.publish('ai_training_updates', json.dumps(test_data))
        print("✅ Redis pub/sub working")
        return True
    except Exception as e:
        print(f"❌ Redis pub/sub error: {e}")
        return False


def main():
    """Main test function"""
    print("="*60)
    print("AI JOB MARKET INTELLIGENCE SYSTEM - READINESS CHECK")
    print("="*60)

    # Check dependencies
    deps_ok = check_dependencies()

    # Check files
    files_ok = check_files()

    # Test Redis
    redis_ok = test_redis_pubsub()

    print("\n" + "="*60)
    print("READINESS CHECK SUMMARY")
    print("="*60)

    if deps_ok and files_ok and redis_ok:
        print("✅ SYSTEM IS READY TO LAUNCH!")
        print("\nTo start the training system, run:")
        print("  ./launch_ai_training.sh")
        print("\nOr manually:")
        print("  1. Start Django: python manage.py runserver 8001")
        print("  2. Run training: python ai_job_market_intelligence.py")
        print("  3. Open dashboard: http://localhost:8001/ai-job-market-dashboard/")
        return 0
    else:
        print("❌ SYSTEM NOT READY - Please fix the issues above")
        return 1


if __name__ == "__main__":
    sys.exit(main())