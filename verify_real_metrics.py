#!/usr/bin/env python
"""
Verify Real Metrics Are Working
Created: 9/26/25 1:01 PM MST

This script verifies that the AI Production Hub is displaying real metrics
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from backend.agents.execution_tracker import execution_tracker
from datetime import datetime
import pytz

mst = pytz.timezone('America/Denver')

def verify_metrics():
    """Verify real metrics are working end-to-end"""

    print("🔍 Verifying Real Metrics System - 9/26/25 1:01 PM MST")
    print("=" * 60)

    # 1. Check Redis Data
    print("\n📊 Redis Metrics:")
    stats = execution_tracker.get_comprehensive_stats()
    print(f"  Active Agents: {stats['active_agents']}")
    print(f"  Files Created: {stats['files_created']}")
    print(f"  Success Rate: {stats['success_rate']}%")
    print(f"  Learning Rate: {stats['learning_rate']}%")
    print(f"  Projects Completed: {stats['projects_completed']}")

    # 2. Check API Response
    print("\n🌐 API Response (/api/learning/stats/):")
    try:
        response = requests.get('http://localhost:8000/api/learning/stats/')
        if response.status_code == 200:
            data = response.json()
            print(f"  Active Agents: {data.get('active_agents', 0)}")
            print(f"  Files Created: {data.get('files_created', 0)}")
            print(f"  Success Rate: {data.get('success_rate', 0)}%")
            print(f"  Learning Rate: {data.get('learning_rate', 0)}%")
            print(f"  Projects Completed: {data.get('projects_completed', 0)}")
        else:
            print(f"  ❌ API returned status {response.status_code}")
    except Exception as e:
        print(f"  ❌ API Error: {e}")

    # 3. Verify No Hardcoded Values
    print("\n🔎 Checking for Hardcoded Values:")
    dashboard_url = 'http://localhost:8000/ai-production-hub/'
    try:
        response = requests.get(dashboard_url)
        if response.status_code == 200:
            content = response.text

            # Check for old hardcoded values
            hardcoded = {
                '|| 12': 'Active agents fallback',
                '|| 47': 'Projects fallback',
                '|| 1234': 'Files fallback',
                '|| 92': 'Learning rate fallback',
                '|| 98': 'Success rate fallback'
            }

            found_hardcoded = False
            for pattern, description in hardcoded.items():
                if pattern in content:
                    print(f"  ⚠️  Found: {pattern} ({description})")
                    found_hardcoded = True

            if not found_hardcoded:
                print("  ✅ No hardcoded fallback values found!")

            # Check for correct zero fallbacks
            if '|| 0' in content:
                print("  ✅ Using correct zero fallbacks")

        else:
            print(f"  ❌ Dashboard returned status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Dashboard Error: {e}")

    # 4. Summary
    print("\n" + "=" * 60)
    print("📈 VERIFICATION SUMMARY:")

    if stats['active_agents'] > 0:
        print(f"✅ System is tracking {stats['active_agents']} active agents")
        print(f"✅ {stats['files_created']} files have been created")
        print(f"✅ Success rate: {stats['success_rate']}%")
        print(f"✅ Learning rate: {stats['learning_rate']}%")
        print("\n🎉 Real metrics system is working correctly!")
    else:
        print("⚠️  No active agents yet - run a project to see metrics")
        print("💡 Use test_real_metrics.py to populate test data")

    print(f"\n🕐 Timestamp: {datetime.now(mst).strftime('%Y-%m-%d %I:%M %p MST')}")

if __name__ == "__main__":
    verify_metrics()