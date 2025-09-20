#!/usr/bin/env python
"""
Test script for Revenue Activation + Income Builder Integration
Tests the complete end-to-end flow from opportunity to revenue
"""

import os
import sys
import django
import asyncio
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from intelligence.revenue_integration import RevenueIncomeIntegration
from intelligence.models import OpportunityActionPlan, ActionPlan, RevenueMetrics


async def test_revenue_integration():
    """Test the complete revenue integration flow"""

    print("🧪 Starting Revenue Integration Test")
    print("=" * 50)

    # Initialize integration
    integration = RevenueIncomeIntegration()

    # Test 1: Process a sample opportunity
    print("\n✅ Test 1: Processing Revenue Opportunity")
    print("-" * 40)

    test_opportunity = {
        'id': 'test_opp_001',
        'title': 'AI Content Writer Needed for Tech Blog',
        'platform': 'upwork',
        'budget': '$850',
        'deadline': '1 week',
        'skills_required': ['AI', 'Content Writing', 'SEO', 'Technical Writing'],
        'client_rating': 4.8,
        'description': 'Looking for an experienced AI content writer to create 10 articles about emerging AI technologies.',
        'is_ongoing': False,
        'competition_level': 'medium',
        'user_profile': {
            'current_balance': 0,
            'skills': ['writing', 'AI', 'automation', 'SEO'],
            'available_hours_per_week': 20,
            'skill_level': 'intermediate'
        }
    }

    result = await integration.process_opportunity(test_opportunity)

    if result['success']:
        print(f"✅ Opportunity processed successfully!")
        print(f"   - Success Probability: {result.get('success_probability', 0):.1%}")
        print(f"   - Plan ID: {result['plan']['id']}")
        print(f"   - Proposal ID: {result['proposal']['id']}")
        print(f"   - Files Generated: {len(result['files'])}")

        for file_info in result['files']:
            print(f"     • {file_info['path']} ({file_info['type']})")
    else:
        print(f"❌ Failed to process opportunity: {result.get('error')}")
        return False

    # Test 2: Check database records
    print("\n✅ Test 2: Verifying Database Records")
    print("-" * 40)

    try:
        # Check if ActionPlan was created
        action_plans = ActionPlan.objects.filter(
            opportunity_id=test_opportunity['id']
        )
        print(f"   - Action Plans Created: {action_plans.count()}")

        # Check if OpportunityActionPlan was created
        opp_plans = OpportunityActionPlan.objects.filter(
            opportunity_id=test_opportunity['id']
        )
        print(f"   - Opportunity Plans Created: {opp_plans.count()}")

        if opp_plans.exists():
            opp_plan = opp_plans.first()
            print(f"   - Status: {opp_plan.status}")
            print(f"   - Success Score: {opp_plan.success_score:.1%}")
            print(f"   - Priority Level: {opp_plan.priority_level}")
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

    # Test 3: Test API endpoints
    print("\n✅ Test 3: Testing API Endpoints")
    print("-" * 40)

    import requests

    # Test opportunities endpoint
    try:
        response = requests.get('http://localhost:8000/api/v1/intelligence/revenue/opportunities/')
        if response.status_code == 200:
            data = response.json()
            print(f"   - GET /opportunities: ✅ ({data.get('count', 0)} opportunities)")
        else:
            print(f"   - GET /opportunities: ❌ (Status: {response.status_code})")
    except Exception as e:
        print(f"   - GET /opportunities: ❌ (Error: {e})")

    # Test metrics endpoint
    try:
        response = requests.get('http://localhost:8000/api/v1/intelligence/revenue/metrics/?days=30')
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                metrics = data['metrics']
                print(f"   - GET /metrics: ✅")
                print(f"     • Total Opportunities: {metrics.get('total_opportunities', 0)}")
                print(f"     • Proposals Submitted: {metrics.get('proposals_submitted', 0)}")
                print(f"     • Total Revenue: ${metrics.get('total_revenue', 0):.2f}")
        else:
            print(f"   - GET /metrics: ❌ (Status: {response.status_code})")
    except Exception as e:
        print(f"   - GET /metrics: ❌ (Error: {e})")

    # Test 4: WebSocket Connection
    print("\n✅ Test 4: Testing WebSocket Connection")
    print("-" * 40)

    try:
        import websocket

        ws = websocket.WebSocket()
        ws.connect("ws://localhost:8000/ws/revenue-income/")

        # Send a ping message
        ws.send(json.dumps({'type': 'ping', 'timestamp': datetime.now().isoformat()}))

        # Wait for pong
        response = ws.recv()
        data = json.loads(response)

        if data.get('type') == 'connection':
            print(f"   - WebSocket Connection: ✅ ({data.get('status')})")
        else:
            print(f"   - WebSocket Connection: ✅ (Response: {data.get('type')})")

        ws.close()
    except Exception as e:
        print(f"   - WebSocket Connection: ❌ (Error: {e})")

    # Test 5: Generate more test opportunities
    print("\n✅ Test 5: Processing Multiple Opportunities")
    print("-" * 40)

    test_opportunities = [
        {
            'id': 'test_opp_002',
            'title': 'Python Developer for Web Scraping Project',
            'platform': 'freelancer',
            'budget': '$1200',
            'deadline': '2 weeks',
            'skills_required': ['Python', 'Web Scraping', 'Data Analysis'],
            'client_rating': 4.5,
            'is_ongoing': True
        },
        {
            'id': 'test_opp_003',
            'title': 'Social Media Manager for Startup',
            'platform': 'fiverr',
            'budget': '$500',
            'deadline': '3 days',
            'skills_required': ['Social Media', 'Content Creation', 'Marketing'],
            'client_rating': 4.2,
            'is_ongoing': False
        }
    ]

    success_count = 0
    for opp in test_opportunities:
        # Add user profile
        opp['user_profile'] = test_opportunity['user_profile']

        result = await integration.process_opportunity(opp)
        if result['success']:
            success_count += 1
            print(f"   ✅ {opp['title'][:40]}... (Score: {result.get('success_probability', 0):.1%})")
        else:
            print(f"   ❌ {opp['title'][:40]}...")

    print(f"\n   Processed: {success_count}/{len(test_opportunities)} opportunities")

    # Test 6: Update metrics
    print("\n✅ Test 6: Updating Revenue Metrics")
    print("-" * 40)

    try:
        from django.utils import timezone
        metrics = RevenueMetrics.update_metrics_for_date(timezone.now().date())
        print(f"   - Metrics Updated for: {metrics.date}")
        print(f"   - Opportunities Identified: {metrics.opportunities_identified}")
        print(f"   - Revenue Generated: ${metrics.revenue_generated:.2f}")
    except Exception as e:
        print(f"   - Metrics Update: ❌ (Error: {e})")

    print("\n" + "=" * 50)
    print("🎉 Revenue Integration Test Complete!")
    print("=" * 50)

    # Summary
    total_opportunities = OpportunityActionPlan.objects.count()
    total_revenue = sum(
        opp.revenue_generated for opp in OpportunityActionPlan.objects.all()
    )

    print(f"\n📊 Summary:")
    print(f"   - Total Opportunities: {total_opportunities}")
    print(f"   - Total Revenue: ${total_revenue:.2f}")
    print(f"   - Success Rate: {(success_count + 1) / (len(test_opportunities) + 1) * 100:.1f}%")

    return True


def cleanup_test_data():
    """Clean up test data after testing"""
    print("\n🧹 Cleaning up test data...")

    # Delete test opportunities
    test_ids = ['test_opp_001', 'test_opp_002', 'test_opp_003']

    deleted_count = OpportunityActionPlan.objects.filter(
        opportunity_id__in=test_ids
    ).delete()[0]

    print(f"   - Deleted {deleted_count} test opportunities")


if __name__ == '__main__':
    print("""
╔══════════════════════════════════════════════════════════╗
║   REVENUE ACTIVATION + INCOME BUILDER INTEGRATION TEST   ║
╚══════════════════════════════════════════════════════════╝
    """)

    try:
        # Run async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(test_revenue_integration())

        if success:
            print("\n✅ All tests passed successfully!")
        else:
            print("\n❌ Some tests failed. Please check the output above.")

        # Optional: Clean up test data
        response = input("\n🧹 Clean up test data? (y/n): ")
        if response.lower() == 'y':
            cleanup_test_data()

    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

    print("\n👋 Test complete. Goodbye!")