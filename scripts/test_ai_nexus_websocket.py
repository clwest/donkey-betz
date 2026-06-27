#!/usr/bin/env python3
"""
Test AI Nexus WebSocket Data
Simulates what the WebSocket consumer sends
"""

import os
import sys
import django
from datetime import timedelta

sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.models.agents_registry import UnifiedAgentTemplate, AgentTaskExecution
from core.models_unified_system import Advisor
from core.models import Revenue
from django.utils import timezone
from django.db.models import Sum, Count, Avg

try:
    from intelligence.spider_quality_tracker import SpiderQualityMetrics
    has_spider_metrics = True
except:
    has_spider_metrics = False
    SpiderQualityMetrics = None

try:
    from intelligence.models import OpportunityInteraction
    has_opp_interaction = True
except:
    has_opp_interaction = False
    OpportunityInteraction = None

print("=" * 60)
print("🧠 AI NEXUS WEBSOCKET DATA TEST")
print("=" * 60)

# Get REAL agent counts
total_agents = UnifiedAgentTemplate.objects.filter(is_active=True).count()
print(f"\n✅ Total Agents: {total_agents}")

one_hour_ago = timezone.now() - timedelta(hours=1)
active_agent_ids = AgentTaskExecution.objects.filter(
    created_at__gte=one_hour_ago
).values_list('template_id', flat=True).distinct()
active_agents = len(set(active_agent_ids))
print(f"✅ Active Agents (last hour): {active_agents}")

# Get REAL task stats
total_executions = AgentTaskExecution.objects.count()
successful_executions = AgentTaskExecution.objects.filter(status='completed').count()
success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
print(f"✅ Total Executions: {total_executions}")
print(f"✅ Successful: {successful_executions}")
print(f"✅ Success Rate: {success_rate:.1f}%")

# Get REAL spider data
print(f"\n🕷️ SPIDER DATA:")
if has_spider_metrics:
    total_spiders = 46  # From registry
    one_day_ago = timezone.now() - timedelta(hours=24)

    active_metrics = SpiderQualityMetrics.objects.filter(
        last_updated__gte=one_day_ago
    )
    active_spiders = active_metrics.count()

    crawling_metrics = SpiderQualityMetrics.objects.filter(
        last_updated__gte=one_hour_ago
    )
    crawling_spiders = crawling_metrics.count()

    opportunities_found = SpiderQualityMetrics.objects.aggregate(
        total=Sum('opportunities_fetched')
    )['total'] or 0

    print(f"✅ Total Spiders: {total_spiders}")
    print(f"✅ Active (24h): {active_spiders}")
    print(f"✅ Crawling (1h): {crawling_spiders}")
    print(f"✅ Opportunities Found: {opportunities_found}")
else:
    print("❌ SpiderQualityMetrics not available")

# Get REAL advisor counts
print(f"\n👔 ADVISOR DATA:")
total_advisors = Advisor.objects.filter(is_active=True).count()
available_advisors = total_advisors
total_consultations = Advisor.objects.aggregate(
    total=Sum('total_consultations')
)['total'] or 0

print(f"✅ Total Advisors: {total_advisors}")
print(f"✅ Available: {available_advisors}")
print(f"✅ Total Consultations: {total_consultations}")

# Get REAL revenue data
print(f"\n💰 REVENUE DATA:")
total_revenue = Revenue.objects.filter(status='confirmed').aggregate(
    total=Sum('amount')
)['total'] or 0

this_month = timezone.now().replace(day=1)
month_revenue = Revenue.objects.filter(
    status='confirmed',
    created_at__gte=this_month
).aggregate(total=Sum('amount'))['total'] or 0

opportunities_count = OpportunityInteraction.objects.count() if has_opp_interaction else 0

print(f"✅ Total Revenue: ${float(total_revenue):.2f}")
print(f"✅ This Month: ${float(month_revenue):.2f}")
print(f"✅ Opportunities: {opportunities_count}")

# Show what would be sent to frontend
print("\n" + "=" * 60)
print("📤 WEBSOCKET MESSAGE THAT WOULD BE SENT:")
print("=" * 60)

status = {
    'agents': {
        'total': total_agents,
        'active': active_agents,
        'idle': total_agents - active_agents,
        'tasks_completed': total_executions,
        'success_rate': round(success_rate, 1)
    },
    'spiders': {
        'total': 46 if has_spider_metrics else 0,
        'active': active_spiders if has_spider_metrics else 0,
        'crawling': crawling_spiders if has_spider_metrics else 0,
        'opportunities_found': opportunities_found if has_spider_metrics else 0
    },
    'advisors': {
        'total': total_advisors,
        'available': available_advisors,
        'consultations': total_consultations,
        'insights_generated': total_consultations
    },
    'revenue': {
        'total': float(total_revenue),
        'this_month': float(month_revenue),
        'opportunities': opportunities_count,
        'conversion': round((total_revenue / opportunities_count * 100), 1) if opportunities_count > 0 else 0
    }
}

import json
print(json.dumps(status, indent=2))

print("\n" + "=" * 60)
print("✅ TEST COMPLETE")
print("=" * 60)
print("\n📝 This is the actual data that should appear in AI Nexus")
print("If you don't see these numbers, the frontend isn't receiving/displaying data correctly")
