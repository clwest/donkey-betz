#!/usr/bin/env python
"""
Review Overnight Learning Results
==================================
Analyzes and displays results from overnight autonomous learning test.

Usage:
    python scripts/review_overnight_results.py
"""

import os
import sys
import django
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# Setup Django
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Avg, Q
from core.models_unified_system import AgentExecution, UserAgentLearning, Agent
from persistence.models import SpiderData

User = get_user_model()


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def review_results(user, hours_back=12):
    """Review learning results from the last N hours"""

    cutoff_time = timezone.now() - timedelta(hours=hours_back)

    print("\n" + "🌅" * 40)
    print_section("OVERNIGHT AUTONOMOUS LEARNING TEST RESULTS")

    # 1. Overall Statistics
    print_section("📊 OVERALL STATISTICS")

    total_executions = AgentExecution.objects.filter(
        user=user,
        created_at__gte=cutoff_time
    ).count()

    total_learning = UserAgentLearning.objects.filter(
        user=user,
        created_at__gte=cutoff_time
    ).count()

    total_spider_data = SpiderData.objects.filter(
        created_at__gte=cutoff_time
    ).count()

    print(f"\nTime Period: Last {hours_back} hours")
    print(f"From: {cutoff_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"To: {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n📈 Data Generated:")
    print(f"  • Agent Executions: {total_executions}")
    print(f"  • Learning Records: {total_learning}")
    print(f"  • Spider Data: {total_spider_data}")

    if total_executions > 0:
        learning_ratio = total_learning / total_executions
        print(f"  • Learning Ratio: {learning_ratio:.2f} records per execution")

    # 2. Agent Performance
    print_section("🤖 AGENT EXECUTION BREAKDOWN")

    agent_stats = AgentExecution.objects.filter(
        user=user,
        created_at__gte=cutoff_time
    ).values('agent__name', 'status').annotate(
        count=Count('id')
    ).order_by('-count')

    agent_summary = defaultdict(lambda: {'completed': 0, 'failed': 0, 'total': 0})

    for stat in agent_stats:
        agent_name = stat['agent__name']
        status = stat['status']
        count = stat['count']
        agent_summary[agent_name][status] = count
        agent_summary[agent_name]['total'] += count

    print(f"\n{'Agent':<30} {'Completed':<12} {'Failed':<12} {'Success Rate':<15}")
    print("-" * 80)

    for agent_name in sorted(agent_summary.keys(), key=lambda x: agent_summary[x]['total'], reverse=True):
        stats = agent_summary[agent_name]
        completed = stats['completed']
        failed = stats['failed']
        total = stats['total']
        success_rate = (completed / total * 100) if total > 0 else 0

        print(f"{agent_name:<30} {completed:<12} {failed:<12} {success_rate:>6.1f}%")

    # 3. Learning Insights
    print_section("🧠 LEARNING INSIGHTS GENERATED")

    learning_by_domain = UserAgentLearning.objects.filter(
        user=user,
        created_at__gte=cutoff_time
    ).values('learning_domain').annotate(
        count=Count('id'),
        avg_confidence=Avg('confidence_score')
    ).order_by('-count')

    print(f"\n{'Learning Domain':<40} {'Count':<10} {'Avg Confidence':<15}")
    print("-" * 80)

    for domain in learning_by_domain:
        print(f"{domain['learning_domain']:<40} {domain['count']:<10} {domain['avg_confidence']:>6.2f}")

    # 4. Learning by Agent
    print_section("📈 LEARNING BY AGENT")

    learning_by_agent = UserAgentLearning.objects.filter(
        user=user,
        created_at__gte=cutoff_time
    ).values('agent_name').annotate(
        count=Count('id'),
        avg_confidence=Avg('confidence_score')
    ).order_by('-count')[:15]

    print(f"\n{'Agent':<30} {'Learning Records':<18} {'Avg Confidence':<15}")
    print("-" * 80)

    for agent in learning_by_agent:
        print(f"{agent['agent_name']:<30} {agent['count']:<18} {agent['avg_confidence']:>6.2f}")

    # 5. Spider Data Collection
    print_section("🕷️  SPIDER DATA COLLECTION")

    spider_stats = SpiderData.objects.filter(
        created_at__gte=cutoff_time
    ).values('spider_name').annotate(
        count=Count('id')
    ).order_by('-count')

    print(f"\n{'Spider Type':<30} {'Items Collected':<20}")
    print("-" * 80)

    for spider in spider_stats:
        print(f"{spider['spider_name']:<30} {spider['count']:<20}")

    # 6. Top Learning Sources
    print_section("🎯 TOP LEARNING SOURCES")

    learning_sources = UserAgentLearning.objects.filter(
        user=user,
        created_at__gte=cutoff_time
    ).values('learning_source').annotate(
        count=Count('id')
    ).order_by('-count')

    print(f"\n{'Learning Source':<40} {'Count':<10}")
    print("-" * 80)

    for source in learning_sources:
        print(f"{source['learning_source']:<40} {source['count']:<10}")

    # 7. High Confidence Learning
    print_section("⭐ HIGH CONFIDENCE LEARNING (>0.75)")

    high_confidence = UserAgentLearning.objects.filter(
        user=user,
        created_at__gte=cutoff_time,
        confidence_score__gte=0.75
    ).order_by('-confidence_score')[:10]

    if high_confidence.exists():
        print(f"\n{'Agent':<25} {'Domain':<30} {'Confidence':<12} {'Source':<20}")
        print("-" * 90)

        for learning in high_confidence:
            print(f"{learning.agent_name:<25} {learning.learning_domain:<30} {learning.confidence_score:>6.2f}      {learning.learning_source:<20}")
    else:
        print("\nNo high confidence learning records found yet.")

    # 8. Learning Trends Over Time
    print_section("📊 LEARNING TRENDS")

    # Group by hour
    from django.db.models.functions import TruncHour

    hourly_learning = UserAgentLearning.objects.filter(
        user=user,
        created_at__gte=cutoff_time
    ).annotate(
        hour=TruncHour('created_at')
    ).values('hour').annotate(
        count=Count('id'),
        avg_confidence=Avg('confidence_score')
    ).order_by('hour')

    if hourly_learning.exists():
        print(f"\n{'Time':<20} {'Learning Records':<20} {'Avg Confidence':<15}")
        print("-" * 60)

        for hour in hourly_learning:
            time_str = hour['hour'].strftime('%Y-%m-%d %H:00')
            print(f"{time_str:<20} {hour['count']:<20} {hour['avg_confidence']:>6.2f}")

    # 9. Summary & Recommendations
    print_section("💡 SUMMARY & RECOMMENDATIONS")

    print("\n✅ What Worked Well:")
    if total_learning > 50:
        print(f"  • Excellent learning generation: {total_learning} records created")
    elif total_learning > 20:
        print(f"  • Good learning generation: {total_learning} records created")
    else:
        print(f"  • Learning started: {total_learning} records created")

    if agent_summary:
        best_agent = max(agent_summary.items(), key=lambda x: x[1]['completed'])[0]
        print(f"  • Best performing agent: {best_agent}")

    if spider_stats.exists():
        best_spider = spider_stats.first()
        print(f"  • Most productive spider: {best_spider['spider_name']} ({best_spider['count']} items)")

    print("\n🎯 Next Steps:")
    print("  • Continue overnight tests to build more learning data")
    print("  • Monitor high-confidence learning patterns")
    print("  • Identify agents that need more training data")
    print("  • Review and optimize spider collection strategies")

    # 10. Detailed Logs Location
    print_section("📄 DETAILED LOGS")
    print("\nFor detailed logs, check:")
    print("  • overnight_learning_test.log")
    print("  • overnight_test_report_*.json")

    print("\n" + "=" * 80)
    print("Review complete! 🎉")
    print("=" * 80 + "\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Review overnight learning test results')
    parser.add_argument('--user', type=str, default='chris',
                       help='Username to review (default: chris)')
    parser.add_argument('--hours', type=int, default=12,
                       help='Hours to look back (default: 12)')

    args = parser.parse_args()

    try:
        user = User.objects.get(username=args.user)
    except User.DoesNotExist:
        print(f"Error: User '{args.user}' not found")
        return

    review_results(user, args.hours)


if __name__ == '__main__':
    main()
