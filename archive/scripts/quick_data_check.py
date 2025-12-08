#!/usr/bin/env python
"""
Quick check for real-time data issues
"""

import os
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from agents.models import UnifiedAgentTemplate
from intelligence.models import OpportunityActionPlan, RevenueMetrics, EarningRecord
from advisors.registry import advisor_registry
from core.agents.registry import agent_registry

print("="*60)
print("CHECKING DATA AVAILABILITY")
print("="*60)

# Check agents
agent_count = UnifiedAgentTemplate.objects.filter(is_active=True).count()
print(f"\n✅ Active Agents in Database: {agent_count}")
if agent_count == 0:
    print("   ❌ NO AGENTS REGISTERED - This is why Neural Orchestra shows 0 agents!")
    print("   Fix: Run 'python manage.py register_all_agents'")

# Check opportunities
opp_count = OpportunityActionPlan.objects.count()
print(f"\n✅ Opportunities in Database: {opp_count}")
if opp_count == 0:
    print("   ❌ NO OPPORTUNITIES - Decision Command has nothing to show!")
    print("   Fix: Run spider deployment or create test opportunities")

# Check revenue metrics
revenue_count = RevenueMetrics.objects.count()
earnings_count = EarningRecord.objects.count()
print(f"\n✅ Revenue Metrics Records: {revenue_count}")
print(f"✅ Earning Records: {earnings_count}")
if revenue_count == 0:
    print("   ❌ NO REVENUE METRICS - Revenue Dashboard has no data!")
    print("   Fix: Create initial revenue metrics")

# Check registries
try:
    registry_agents = agent_registry.list_agents()
    print(f"\n✅ Agent Registry has {len(registry_agents)} agents")
except:
    print("\n❌ Agent Registry not initialized properly")

try:
    registry_advisors = advisor_registry.list_advisors()
    print(f"✅ Advisor Registry has {len(registry_advisors)} advisors")
except:
    print("❌ Advisor Registry not initialized properly")

print("\n" + "="*60)
print("CHECKING UNIFIED HUB DATA FORMAT")
print("="*60)

# Check what unified hub would return
from core.unified_hub import UnifiedWebSocketHub
hub = UnifiedWebSocketHub()

# Simulate getting data for each component
from django.utils import timezone
from datetime import timedelta
import random

# Check Neural Orchestra data
agents = list(UnifiedAgentTemplate.objects.filter(is_active=True).values('id', 'name', 'display_name', 'specialization'))
print(f"\nNeural Orchestra would receive {len(agents)} agents")
if len(agents) > 0:
    print(f"  Sample agent: {agents[0]}")

# Check Income Builder data
opportunities = list(OpportunityActionPlan.objects.filter(
    status__in=['identified', 'analyzing', 'plan_created']
).order_by('-success_score')[:10].values('opportunity_id', 'platform', 'success_score'))
print(f"\nIncome Builder would receive {len(opportunities)} opportunities")
if len(opportunities) > 0:
    print(f"  Sample opportunity: {opportunities[0]}")

print("\n" + "="*60)
print("RECOMMENDATIONS TO FIX REAL-TIME UPDATES")
print("="*60)

if agent_count == 0:
    print("\n1. REGISTER AGENTS:")
    print("   python manage.py shell")
    print("   >>> from agents.management.commands.register_all_agents import Command")
    print("   >>> Command().handle()")

if opp_count == 0:
    print("\n2. CREATE TEST OPPORTUNITIES:")
    print("   python manage.py shell")
    print("   >>> from intelligence.models import OpportunityActionPlan")
    print("   >>> OpportunityActionPlan.objects.create(")
    print("       opportunity_id='test-001',")
    print("       platform='freelance',")
    print("       opportunity_data={'title': 'Test Opportunity'},")
    print("       success_score=0.85,")
    print("       ml_confidence=0.9,")
    print("       revenue_potential=1000,")
    print("       status='identified'")
    print("   )")

if revenue_count == 0:
    print("\n3. CREATE INITIAL REVENUE METRICS:")
    print("   python manage.py shell")
    print("   >>> from intelligence.models import RevenueMetrics")
    print("   >>> from django.utils import timezone")
    print("   >>> RevenueMetrics.objects.create(")
    print("       date=timezone.now().date(),")
    print("       revenue_generated=2600,")
    print("       proposals_submitted=10,")
    print("       proposals_responded=5,")
    print("       conversions=2")
    print("   )")