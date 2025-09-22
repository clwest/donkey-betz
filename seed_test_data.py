#!/usr/bin/env python
"""
Seed test data to demonstrate the verification systems
This creates realistic-looking data to show how the system would work with real users
"""

import random
import json
from datetime import datetime, timedelta
from decimal import Decimal

# Import our verification systems
from intelligence.user_value_impact_tracker import UserValueImpactTracker
from revenue.revenue_verifier import RevenueRealityVerifier
from intelligence.spider_authenticity_verifier import SpiderAuthenticityVerifier

def seed_user_impact_data():
    """Seed some test user impact data"""
    tracker = UserValueImpactTracker()

    print("🌱 Seeding user impact data...")

    # Create test users with different outcomes
    test_users = [
        {
            'user_id': 'test_user_001',
            'name': 'Alice Johnson',
            'outcomes': [
                {
                    'outcome_type': 'job_obtained',
                    'details': {
                        'position': 'Senior React Developer',
                        'company': 'TechStartup Inc',
                        'salary': 125000,
                        'source': 'spider_network'
                    }
                },
                {
                    'outcome_type': 'income_earned',
                    'amount': 8500,
                    'details': {
                        'type': 'freelance',
                        'projects': 3,
                        'duration': '1 month'
                    }
                }
            ]
        },
        {
            'user_id': 'test_user_002',
            'name': 'Bob Smith',
            'outcomes': [
                {
                    'outcome_type': 'time_saved',
                    'hours': 40,
                    'details': {
                        'automation': 'job_applications',
                        'tasks_automated': 150
                    }
                },
                {
                    'outcome_type': 'skill_learned',
                    'skill': 'Machine Learning',
                    'details': {
                        'course': 'AI for Developers',
                        'completion_time': '2 weeks'
                    }
                }
            ]
        },
        {
            'user_id': 'test_user_003',
            'name': 'Carol Davis',
            'outcomes': [
                {
                    'outcome_type': 'job_obtained',
                    'details': {
                        'position': 'Data Analyst',
                        'company': 'Analytics Corp',
                        'salary': 95000,
                        'source': 'agent_recommendation'
                    }
                },
                {
                    'outcome_type': 'task_automated',
                    'task_count': 25,
                    'details': {
                        'type': 'reporting',
                        'time_saved_weekly': '10 hours'
                    }
                }
            ]
        }
    ]

    # Track outcomes for each test user
    for user in test_users:
        print(f"  Creating data for {user['name']}...")
        for outcome in user['outcomes']:
            outcome['user_id'] = user['user_id']
            tracker.track_user_outcome(outcome)

    # Calculate and display statistics
    stats = tracker.get_platform_impact()
    print(f"\n✅ User Impact Data Seeded:")
    print(f"  - Users helped: {stats.get('total_users_helped', 0)}")
    print(f"  - Jobs obtained: {stats.get('total_jobs_obtained', 0)}")
    print(f"  - Income generated: ${stats.get('total_income_generated', 0):,.2f}")
    print(f"  - Time saved: {stats.get('total_time_saved', 0)} hours")

def seed_revenue_data():
    """Seed some test revenue verification data"""
    verifier = RevenueRealityVerifier()

    print("\n💰 Seeding revenue verification data...")

    test_transactions = [
        {
            'transaction_id': 'txn_001',
            'amount': Decimal('1250.00'),
            'user_id': 'test_user_001',
            'payment_provider': 'stripe',
            'external_transaction_id': 'pi_1234567890',
            'created_at': datetime.now() - timedelta(days=2),
            'currency': 'USD',
            'flow_id': 'flow_001'
        },
        {
            'transaction_id': 'txn_002',
            'amount': Decimal('850.00'),
            'user_id': 'test_user_002',
            'payment_provider': 'paypal',
            'external_transaction_id': 'PP123456789',
            'created_at': datetime.now() - timedelta(days=1),
            'currency': 'USD',
            'flow_id': 'flow_002'
        },
        {
            'transaction_id': 'txn_003',
            'amount': Decimal('2100.00'),
            'user_id': 'test_user_003',
            'payment_provider': 'stripe',
            'external_transaction_id': 'ch_9876543210',
            'created_at': datetime.now() - timedelta(hours=5),
            'currency': 'USD',
            'flow_id': 'flow_003'
        }
    ]

    verified_count = 0
    total_amount = Decimal('0')

    for txn in test_transactions:
        # Track the flow
        verifier.track_revenue_flow('opportunity_discovered', {'flow_id': txn['flow_id']})
        verifier.track_revenue_flow('payment_initiated', {'flow_id': txn['flow_id']})
        verifier.track_revenue_flow('payment_received', {'flow_id': txn['flow_id']})

        # Verify the transaction
        is_real, proof = verifier.verify_revenue_is_real(txn)
        if is_real:
            verified_count += 1
            total_amount += txn['amount']

        print(f"  Transaction {txn['transaction_id']}: {'✓ Verified' if is_real else '✗ Not verified'} (Score: {proof['verification_score']})")

    print(f"\n✅ Revenue Data Seeded:")
    print(f"  - Transactions verified: {verified_count}/{len(test_transactions)}")
    print(f"  - Total amount verified: ${total_amount:,.2f}")

def seed_spider_data():
    """Seed some test spider authenticity data"""
    verifier = SpiderAuthenticityVerifier()

    print("\n🕷️ Seeding spider authenticity data...")

    test_spider_data = [
        {
            'spider_id': 'job_spider_001',
            'data_source': 'https://api.indeed.com/jobs',
            'data_collected': {
                'job_title': 'Senior Developer',
                'company': 'Tech Corp',
                'salary': '$120,000',
                'location': 'San Francisco'
            },
            'timestamp': datetime.now(),
            'http_headers': {
                'server': 'nginx',
                'content-type': 'application/json',
                'x-ratelimit-remaining': '95'
            }
        },
        {
            'spider_id': 'linkedin_spider_002',
            'data_source': 'https://api.linkedin.com/v2/jobs',
            'data_collected': {
                'job_title': 'Data Scientist',
                'company': 'Analytics Inc',
                'requirements': ['Python', 'ML', 'SQL']
            },
            'timestamp': datetime.now() - timedelta(minutes=30),
            'http_headers': {
                'server': 'LinkedIn-API',
                'x-api-version': 'v2'
            }
        },
        {
            'spider_id': 'market_spider_003',
            'data_source': 'https://api.marketdata.com/stocks',
            'data_collected': {
                'symbol': 'AAPL',
                'price': 185.50,
                'change': '+2.3%'
            },
            'timestamp': datetime.now() - timedelta(minutes=5),
            'http_headers': {
                'server': 'MarketData-Server',
                'cache-control': 'no-cache'
            }
        }
    ]

    authentic_count = 0

    for spider_data in test_spider_data:
        is_authentic, verification = verifier.verify_spider_data(spider_data)
        if is_authentic:
            authentic_count += 1

        print(f"  Spider {spider_data['spider_id']}: {'✓ Authentic' if is_authentic else '✗ Not authentic'} (Score: {verification['authenticity_score']})")

    stats = verifier.get_verification_statistics()
    print(f"\n✅ Spider Data Seeded:")
    print(f"  - Spiders verified: {authentic_count}/{len(test_spider_data)}")
    print(f"  - Authenticity rate: {stats.get('authenticity_rate', 0):.1f}%")

def main():
    print("=" * 60)
    print("VERIFICATION SYSTEM TEST DATA SEEDER")
    print("=" * 60)
    print("\nThis script seeds test data to demonstrate how the")
    print("verification systems would work with real users.\n")

    # Seed all verification systems
    seed_user_impact_data()
    seed_revenue_data()
    seed_spider_data()

    print("\n" + "=" * 60)
    print("✨ Test data seeding complete!")
    print("\nThe dashboards will now show this test data when you:")
    print("1. Start the Django server: python manage.py runserver 8001")
    print("2. Open the dashboards in your browser")
    print("\nNote: This is TEST DATA for demonstration purposes.")
    print("Real data would come from actual user interactions.")
    print("=" * 60)

if __name__ == "__main__":
    main()