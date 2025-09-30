#!/usr/bin/env python
"""
Test script for Learning Loop API endpoints
Phase 1: Frontend Reality Fix
"""

import os
import django
import sys

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.views_analytics import learning_stats, learning_insights
from django.test import RequestFactory
from rest_framework.test import force_authenticate

User = get_user_model()

def test_learning_stats():
    """Test the learning stats endpoint"""
    print("\n🧪 Testing /api/learning/stats/ endpoint...")

    # Get or create test user
    user = User.objects.first()
    if not user:
        print("❌ No users in database")
        return False

    print(f"✅ Testing with user: {user.username}")

    # Create fake request
    factory = RequestFactory()
    request = factory.get('/api/learning/stats/')
    force_authenticate(request, user=user)

    # Call the view
    response = learning_stats(request)

    # Check response
    if response.status_code == 200:
        data = response.data
        print(f"✅ API Response Success")
        print(f"   Total Learnings: {data.get('total_learnings', 0)}")
        print(f"   Active Agents: {data.get('active_agents', 0)}")
        print(f"   Projects Completed: {data.get('projects_completed', 0)}")
        print(f"   Success Rate: {data.get('success_rate', 0)}")
        return True
    else:
        print(f"❌ API returned status {response.status_code}")
        print(f"   Error: {response.data}")
        return False

def test_learning_insights():
    """Test the learning insights endpoint"""
    print("\n🧪 Testing /api/learning/insights/ endpoint...")

    # Get or create test user
    user = User.objects.first()
    if not user:
        print("❌ No users in database")
        return False

    print(f"✅ Testing with user: {user.username}")

    # Create fake request
    factory = RequestFactory()
    request = factory.get('/api/learning/insights/')
    force_authenticate(request, user=user)

    # Call the view
    response = learning_insights(request)

    # Check response
    if response.status_code == 200:
        data = response.data
        print(f"✅ API Response Success")
        print(f"   Recent Insights: {len(data.get('recent_insights', []))}")
        print(f"   Recommendations: {len(data.get('recommendations', []))}")
        print(f"   Total Insights: {data.get('total_insights', 0)}")
        return True
    else:
        print(f"❌ API returned status {response.status_code}")
        print(f"   Error: {response.data}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("🔬 LEARNING LOOP API TEST")
    print("="*60)

    stats_ok = test_learning_stats()
    insights_ok = test_learning_insights()

    print("\n" + "="*60)
    if stats_ok and insights_ok:
        print("✅ ALL TESTS PASSED")
        print("Phase 1 API endpoints are functional!")
    else:
        print("❌ SOME TESTS FAILED")
        print("Check errors above")
    print("="*60)
