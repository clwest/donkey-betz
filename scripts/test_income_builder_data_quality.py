#!/usr/bin/env python
"""
Test Income Builder Data Quality

Verifies that Income Builder is receiving and displaying real learned data.
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from persistence.models import SpiderData
from core.models_unified_system import UserAgentLearning, Opportunity
from core.models.agents_registry import UnifiedAgentTemplate
from django.utils import timezone
from datetime import timedelta


def test_data_pipeline():
    """Test the complete data pipeline from spiders to Income Builder"""

    print("🔍 Income Builder Data Quality Test")
    print("=" * 80)

    # 1. Spider Data Collection
    print("\n📊 Step 1: Spider Data Collection")
    print("-" * 80)

    total_spider_data = SpiderData.objects.count()
    freelance_data = SpiderData.objects.filter(
        spider_name__in=['guru', 'remoteok', 'toptal', 'flexjobs', 'peopleperhour']
    )
    recent_freelance = freelance_data.filter(
        created_at__gte=timezone.now() - timedelta(hours=1)
    )

    print(f"Total spider data: {total_spider_data:,}")
    print(f"Freelance data: {freelance_data.count():,}")
    print(f"Recent freelance (1h): {recent_freelance.count():,}")

    if freelance_data.count() == 0:
        print("❌ No freelance spider data found!")
        return False
    else:
        print("✅ Freelance spider data collecting")

    # 2. Agent Routing
    print("\n🎯 Step 2: Agent Routing")
    print("-" * 80)

    routed_data = freelance_data.exclude(routed_to_agents=[])
    routing_rate = (routed_data.count() / freelance_data.count() * 100) if freelance_data.count() else 0

    print(f"Routed to agents: {routed_data.count():,}")
    print(f"Routing success rate: {routing_rate:.1f}%")

    if routing_rate < 50:
        print(f"⚠️  Routing rate below 50%")
    else:
        print(f"✅ Routing rate excellent: {routing_rate:.1f}%")

    # Sample routing
    if routed_data.exists():
        sample = routed_data.first()
        print(f"\nSample routing:")
        print(f"  Spider: {sample.spider_name}")
        print(f"  Routed to: {sample.routed_to_agents}")
        print(f"  Data type: {sample.data_type}")

    # 3. Learning Entries
    print("\n🧠 Step 3: Learning Entry Creation")
    print("-" * 80)

    income_learning = UserAgentLearning.objects.filter(
        agent_name__in=['income-builder', 'income_builder'],
        learning_source__startswith='spider:'
    )

    print(f"Income builder learning entries: {income_learning.count()}")

    if income_learning.count() == 0:
        print("⚠️  No learning entries for income-builder yet")
    else:
        print("✅ Learning entries created")
        for entry in income_learning:
            print(f"\n  Entry:")
            print(f"    Source: {entry.learning_source}")
            print(f"    Domain: {entry.learning_domain}")
            print(f"    Confidence: {entry.confidence_score:.0%}")
            print(f"    Validations: {entry.validation_count}")

    # 4. Income Builder Agent Status
    print("\n🤖 Step 4: Income Builder Agent Status")
    print("-" * 80)

    try:
        income_agent = UnifiedAgentTemplate.objects.get(name__icontains='income')
        metrics = income_agent.performance_metrics or {}

        print(f"Agent found: {income_agent.name}")
        print(f"Reality score: {metrics.get('reality_score', 0):.1%}")
        print(f"Success rate: {metrics.get('success_rate', 0):.1%}")
        print(f"Total executions: {metrics.get('total_executions', 0)}")

        if metrics.get('reality_score', 0) > 0:
            print("✅ Agent has reality score")
        else:
            print("⚠️  Agent reality score not set")

    except UnifiedAgentTemplate.DoesNotExist:
        print("❌ Income builder agent not found in database")

    # 5. Opportunities
    print("\n💼 Step 5: Income Opportunities")
    print("-" * 80)

    all_opportunities = Opportunity.objects.all()
    recent_opportunities = Opportunity.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=1)
    )

    print(f"Total opportunities: {all_opportunities.count()}")
    print(f"Recent (24h): {recent_opportunities.count()}")

    if recent_opportunities.count() > 0:
        print("✅ Recent opportunities available")
        print(f"\nSample opportunities:")
        for opp in recent_opportunities[:3]:
            print(f"  - {opp.title}")
            print(f"    Type: {opp.opportunity_type}")
            print(f"    Potential: ${opp.revenue_potential:,.2f}" if opp.revenue_potential else "    Potential: N/A")
    else:
        print("⚠️  No recent opportunities created")

    # 6. Data Quality Score
    print("\n📈 Step 6: Overall Data Quality Score")
    print("-" * 80)

    quality_score = 0
    max_score = 5

    if freelance_data.count() > 100:
        quality_score += 1
        print("✅ Sufficient spider data (>100 entries)")
    else:
        print("❌ Insufficient spider data")

    if routing_rate > 75:
        quality_score += 1
        print("✅ Excellent routing rate (>75%)")
    elif routing_rate > 50:
        quality_score += 0.5
        print("⚠️  Good routing rate (>50%)")
    else:
        print("❌ Poor routing rate")

    if income_learning.count() > 0:
        quality_score += 1
        print("✅ Learning entries created")
    else:
        print("❌ No learning entries")

    if all_opportunities.count() > 0:
        quality_score += 1
        print("✅ Opportunities available")
    else:
        print("❌ No opportunities")

    if recent_opportunities.count() > 0:
        quality_score += 1
        print("✅ Recent opportunities active")
    else:
        print("⚠️  No recent opportunities")

    print(f"\n🎯 Data Quality Score: {quality_score}/{max_score} ({quality_score/max_score*100:.0f}%)")

    if quality_score >= 4:
        print("🎉 Excellent! Income Builder has high-quality data")
        return True
    elif quality_score >= 3:
        print("👍 Good! Income Builder is working with real data")
        return True
    else:
        print("⚠️  Needs improvement - some pipeline issues")
        return False


if __name__ == '__main__':
    success = test_data_pipeline()
    sys.exit(0 if success else 1)
