#!/usr/bin/env python
"""
Add test revenue data to populate the Revenue Dashboard
"""

import os
import sys
import django
from datetime import datetime, timedelta
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from intelligence.models import RevenueMetrics, EarningRecord
from django.utils import timezone

def add_test_revenue_data():
    """Add test revenue data to the database"""
    today = timezone.now().date()

    # Create today's revenue metrics
    metrics, created = RevenueMetrics.objects.update_or_create(
        date=today,
        defaults={
            'revenue_generated': Decimal('2650.00'),
            'proposals_submitted': 47,
            'proposals_responded': 18,
            'conversions': 7,
            'opportunities_identified': 145,
            'average_deal_size': Decimal('378.57'),
            'conversion_rate': 14.9,
            'response_rate': 38.3,
            'platform_metrics': {
                'upwork': {'revenue': 1250.00, 'opportunities': 45, 'conversions': 3},
                'fiverr': {'revenue': 750.00, 'opportunities': 38, 'conversions': 2},
                'freelancer': {'revenue': 450.00, 'opportunities': 32, 'conversions': 1},
                'direct': {'revenue': 200.00, 'opportunities': 30, 'conversions': 1}
            }
        }
    )

    print(f"✓ {'Created' if created else 'Updated'} revenue metrics for {today}")
    print(f"  Total Revenue: ${metrics.revenue_generated}")
    print(f"  Proposals: {metrics.proposals_submitted}")
    print(f"  Conversions: {metrics.conversions}")

    # Skip creating EarningRecords for now as they require a user
    # Just focus on RevenueMetrics which is what the dashboard displays

    # Create metrics for past 7 days with realistic progression
    for i in range(1, 8):
        past_date = today - timedelta(days=i)
        base_revenue = Decimal('200.00') + (Decimal('50.00') * (7 - i))

        past_metrics, created = RevenueMetrics.objects.update_or_create(
            date=past_date,
            defaults={
                'revenue_generated': base_revenue,
                'proposals_submitted': 5 + (i * 2),
                'proposals_responded': 2 + i,
                'conversions': max(1, i // 2),
                'opportunities_identified': 15 + (i * 3),
                'average_deal_size': base_revenue / max(1, i // 2),
                'conversion_rate': 10.0 + (i * 0.5),
                'response_rate': 30.0 + (i * 1.5),
                'platform_metrics': {
                    'upwork': {'revenue': float(base_revenue * Decimal('0.4')), 'opportunities': 5 + i, 'conversions': 1},
                    'fiverr': {'revenue': float(base_revenue * Decimal('0.3')), 'opportunities': 4 + i, 'conversions': 1},
                    'freelancer': {'revenue': float(base_revenue * Decimal('0.2')), 'opportunities': 3 + i, 'conversions': 0},
                    'direct': {'revenue': float(base_revenue * Decimal('0.1')), 'opportunities': 3, 'conversions': 0}
                }
            }
        )
        print(f"  {'✓' if created else '↻'} Metrics for {past_date}: ${past_metrics.revenue_generated}")

    print("\n✅ Test revenue data added successfully!")
    print(f"Total revenue in database: ${RevenueMetrics.objects.all().aggregate(total=django.db.models.Sum('revenue_generated'))['total']}")

if __name__ == "__main__":
    add_test_revenue_data()