#!/usr/bin/env python
"""
Test Spider Data Learning Bridge

Tests that the new spider_data_bridge creates learning entries
from existing spider data.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from persistence.models import SpiderData
from core.models_unified_system import UserAgentLearning
from core.learning_bridges.spider_data_bridge import spider_data_learning
from django.utils import timezone
from datetime import timedelta


def test_spider_learning():
    """Test the spider learning bridge with recent data"""

    print("=" * 80)
    print("🧪 Testing Spider Data Learning Bridge")
    print("=" * 80)

    # Get current state
    initial_learning_count = UserAgentLearning.objects.count()
    print(f"\n📊 Initial State:")
    print(f"   Total Learning Entries: {initial_learning_count}")

    # Get recent spider data with routing
    recent_routed_data = SpiderData.objects.exclude(
        routed_to_agents=[]
    ).order_by('-created_at')[:10]

    print(f"\n🕷️ Recent Spider Data with Agent Routing:")
    print(f"   Found: {recent_routed_data.count()} entries")

    if recent_routed_data.count() == 0:
        print("   ⚠️  No spider data with agent routing found!")
        print("   This means spiders haven't routed data to agents yet.")
        return

    # Test processing a few entries
    print("\n🔄 Processing Sample Entries:")
    processed = 0
    for spider_data in recent_routed_data[:5]:
        print(f"\n   Processing: {spider_data.spider_name} (ID: {spider_data.id})")
        print(f"   - Routed to: {', '.join(spider_data.routed_to_agents[:3])}")
        print(f"   - Quality: {spider_data.quality_score:.2f}")

        try:
            spider_data_learning.process_spider_data(spider_data)
            processed += 1
            print(f"   ✅ Processed successfully")
        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Check results
    final_learning_count = UserAgentLearning.objects.count()
    new_entries = final_learning_count - initial_learning_count

    print("\n" + "=" * 80)
    print("📈 Results:")
    print("=" * 80)
    print(f"   Spider Data Processed: {processed}")
    print(f"   New Learning Entries: {new_entries}")
    print(f"   Total Learning Entries: {final_learning_count}")

    if new_entries > 0:
        print("\n✅ SUCCESS! Learning bridge is working!")

        # Show sample entries
        print("\n📋 Sample Learning Entries Created:")
        recent_entries = UserAgentLearning.objects.filter(
            learning_source__startswith='spider:'
        ).order_by('-created_at')[:5]

        for entry in recent_entries:
            print(f"\n   Agent: {entry.agent_name}")
            print(f"   Domain: {entry.learning_domain}")
            print(f"   Source: {entry.learning_source}")
            print(f"   Confidence: {entry.confidence_score:.2%}")
            print(f"   Created: {entry.created_at.strftime('%Y-%m-%d %H:%M')}")

    else:
        print("\n⚠️  No new learning entries created")
        print("   This could mean:")
        print("   - Agents in routed_to_agents don't exist in database")
        print("   - Learning entries already existed (get_or_create)")
        print("   - An error occurred during processing")

    print("\n" + "=" * 80)


def show_statistics():
    """Show learning statistics"""
    print("\n📊 Learning Bridge Statistics:")
    print("=" * 80)

    # Spider data stats
    total_spider_data = SpiderData.objects.count()
    routed_data = SpiderData.objects.exclude(routed_to_agents=[]).count()

    print(f"\n🕷️ Spider Data:")
    print(f"   Total: {total_spider_data}")
    print(f"   Routed to Agents: {routed_data} ({routed_data/total_spider_data*100:.1f}%)")

    # Learning entries by source
    spider_learning = UserAgentLearning.objects.filter(
        learning_source__startswith='spider:'
    ).count()

    print(f"\n🧠 Learning Entries:")
    print(f"   Total: {UserAgentLearning.objects.count()}")
    print(f"   From Spiders: {spider_learning}")

    # By domain
    from django.db.models import Count
    by_domain = UserAgentLearning.objects.filter(
        learning_source__startswith='spider:'
    ).values('learning_domain').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    if by_domain:
        print(f"\n📈 Top Learning Domains (from spiders):")
        for item in by_domain:
            print(f"   {item['learning_domain']}: {item['count']}")

    print("\n" + "=" * 80)


if __name__ == '__main__':
    test_spider_learning()
    show_statistics()
