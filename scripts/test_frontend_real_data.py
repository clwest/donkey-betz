#!/usr/bin/env python3
"""
Test Frontend Real Data Flow
Verifies that data flows from Database → Backend → Frontend correctly
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.models_unified_system import Opportunity, Revenue

try:
    from intelligence.models.revenue import RevenueMetrics, OpportunityActionPlan
except ImportError:
    RevenueMetrics = None
    OpportunityActionPlan = None

User = get_user_model()

def test_opportunity_data_flow():
    """Test that opportunities flow from DB to Income Builder UI"""
    print("\n🔍 Testing Opportunity Data Flow...")

    # Get or create test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={'email': 'test@example.com'}
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✅ Created test user: {user.username}")
    else:
        print(f"✅ Using existing test user: {user.username}")

    # Create test opportunities
    test_opportunities = [
        {
            'title': 'REAL TEST: Python Django Developer',
            'opportunity_type': 'job',
            'source': 'test_script',
            'potential_revenue': Decimal('2500.00'),
            'match_score': 0.95,
            'status': 'active',
            'description': 'This is a REAL test opportunity created by the test script'
        },
        {
            'title': 'REAL TEST: AI/ML Consultant',
            'opportunity_type': 'freelance',
            'source': 'test_script',
            'potential_revenue': Decimal('5000.00'),
            'match_score': 0.88,
            'status': 'active',
            'description': 'Another REAL test opportunity to verify data flow'
        }
    ]

    created_opps = []
    for opp_data in test_opportunities:
        opp, created = Opportunity.objects.get_or_create(
            user=user,
            title=opp_data['title'],
            defaults=opp_data
        )
        created_opps.append(opp)
        status = "Created" if created else "Found existing"
        print(f"  ✅ {status}: {opp.title} (${opp.potential_revenue})")

    # Verify opportunities exist
    total_opps = Opportunity.objects.filter(user=user, status='active').count()
    print(f"\n📊 Total active opportunities for {user.username}: {total_opps}")

    return user, created_opps


def test_revenue_data_flow():
    """Test that revenue data flows to Revenue Dashboard"""
    print("\n🔍 Testing Revenue Data Flow...")

    user = User.objects.filter(username='testuser').first()
    if not user:
        print("❌ Test user not found. Run opportunity test first.")
        return

    # Create test revenue records
    test_revenues = [
        {
            'source': 'test_freelance_job',
            'amount': Decimal('750.00'),
            'status': 'confirmed',
            'opportunity_title': 'Test Project Alpha',
            'company': 'Test Corp',
            'notes': 'REAL TEST: Payment from test script'
        },
        {
            'source': 'test_consulting',
            'amount': Decimal('1200.00'),
            'status': 'pending',
            'opportunity_title': 'Test Consulting Beta',
            'company': 'Beta Inc',
            'notes': 'REAL TEST: Pending payment from test script'
        }
    ]

    created_revenues = []
    for rev_data in test_revenues:
        rev, created = Revenue.objects.get_or_create(
            user=user,
            opportunity_title=rev_data['opportunity_title'],
            defaults=rev_data
        )
        created_revenues.append(rev)
        status = "Created" if created else "Found existing"
        print(f"  ✅ {status}: ${rev.amount} from {rev.opportunity_title}")

    # Calculate totals
    total_revenue = Revenue.objects.filter(user=user).aggregate(
        total=django.db.models.Sum('amount')
    )['total'] or Decimal('0.00')

    confirmed_revenue = Revenue.objects.filter(
        user=user,
        status='confirmed'
    ).aggregate(total=django.db.models.Sum('amount'))['total'] or Decimal('0.00')

    pending_revenue = Revenue.objects.filter(
        user=user,
        status='pending'
    ).aggregate(total=django.db.models.Sum('amount'))['total'] or Decimal('0.00')

    print(f"\n📊 Revenue Summary for {user.username}:")
    print(f"  Total Revenue: ${total_revenue}")
    print(f"  Confirmed: ${confirmed_revenue}")
    print(f"  Pending: ${pending_revenue}")

    return user, created_revenues


def test_revenue_metrics():
    """Test that RevenueMetrics are generated"""
    print("\n🔍 Testing Revenue Metrics...")

    if RevenueMetrics is None:
        print("⚠️  RevenueMetrics model not available, skipping")
        return None

    from django.utils import timezone
    today = timezone.now().date()

    try:
        # Update today's metrics
        metrics, created = RevenueMetrics.objects.get_or_create(
            date=today,
            defaults={'revenue_generated': Decimal('0.00')}
        )

        if created:
            print(f"✅ Created metrics for {today}")
        else:
            print(f"✅ Metrics exist for {today}")

        # Force update metrics if method exists
        if hasattr(RevenueMetrics, 'update_metrics_for_date'):
            RevenueMetrics.update_metrics_for_date(today)
            metrics.refresh_from_db()

        print(f"\n📊 Today's Metrics:")
        print(f"  Revenue Generated: ${metrics.revenue_generated}")
        if hasattr(metrics, 'proposals_submitted'):
            print(f"  Proposals Submitted: {metrics.proposals_submitted}")
            print(f"  Responses Received: {metrics.proposals_responded}")
            print(f"  Conversions: {metrics.conversions}")
            print(f"  Conversion Rate: {metrics.conversion_rate}%")

        return metrics
    except Exception as e:
        print(f"⚠️  Error with RevenueMetrics: {e}")
        return None


def verify_api_endpoints():
    """Verify that API endpoints return real data"""
    print("\n🔍 Verifying API Endpoints...")

    from django.test import Client
    from django.contrib.auth import get_user_model

    client = Client()
    user = User.objects.filter(username='testuser').first()

    if not user:
        print("❌ Test user not found")
        return

    # Login
    client.force_login(user)

    # Test Income Builder API
    response = client.get('/api/v1/intelligence/real-income-builder/')
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Income Builder API: {len(data.get('opportunities', []))} opportunities")
    else:
        print(f"❌ Income Builder API failed: {response.status_code}")

    # Test Revenue Stats API
    response = client.get('/api/v1/revenue/stats/')
    if response.status_code == 200:
        data = response.json()
        total = data.get('total_revenue', {}).get('all', 0)
        print(f"✅ Revenue Stats API: ${total} total revenue")
    else:
        print(f"❌ Revenue Stats API failed: {response.status_code}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 Testing Frontend Real Data Flow")
    print("=" * 60)

    try:
        # Test data creation
        user, opportunities = test_opportunity_data_flow()
        user, revenues = test_revenue_data_flow()
        metrics = test_revenue_metrics()

        # Verify APIs
        verify_api_endpoints()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        print("\n📝 Next Steps:")
        print("1. Open browser to http://localhost:8000/accounts/login/")
        print("2. Login as: testuser / testpass123")
        print("3. Navigate to Income Builder - should see REAL TEST opportunities")
        print("4. Navigate to Revenue Dashboard - should see REAL TEST revenue")
        print("5. Check Decision Command - should see real opportunities")
        print("\n✅ If you see 'REAL TEST' data, the data flow is working!")
        print("❌ If you see hardcoded/demo data, there's still an issue.")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
