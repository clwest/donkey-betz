#!/usr/bin/env python
"""
🔍 LEARNING PROGRESS CHECKER
Check what your AI system learned overnight
"""

import os
import django
import sys
from datetime import datetime, timedelta
from tabulate import tabulate

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models_unified_system import (
    SpiderData, AgentSolution, AgentLearning, Agent
)


def check_overnight_learning(hours=12):
    """Check what was learned in the last N hours"""

    print("\n" + "="*70)
    print(" "*20 + "🌙 OVERNIGHT LEARNING REPORT 🌙")
    print("="*70)

    # Time range
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours)

    print(f"\n📅 Time Period: {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')}")
    print(f"   Duration: {hours} hours")

    # 1. Spider Data Collection
    print("\n" + "─"*70)
    print("🕷️  SPIDER DATA COLLECTION")
    print("─"*70)

    new_spider_data = SpiderData.objects.filter(
        created_at__gte=start_time
    )

    spider_by_type = {}
    for item in new_spider_data:
        data_type = item.data_type or 'unknown'
        if data_type not in spider_by_type:
            spider_by_type[data_type] = 0
        spider_by_type[data_type] += 1

    print(f"Total New Items: {new_spider_data.count()}")

    if spider_by_type:
        print("\nBy Type:")
        for dtype, count in sorted(spider_by_type.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {dtype}: {count}")

    # Show sample of latest spider data
    latest_spider = new_spider_data.order_by('-created_at').first()
    if latest_spider:
        print(f"\nLatest Spider Data:")
        print(f"  Spider: {latest_spider.spider_name}")
        print(f"  Type: {latest_spider.data_type}")
        print(f"  Source: {latest_spider.source_url[:50]}..." if latest_spider.source_url else "N/A")

    # 2. Solutions Generated
    print("\n" + "─"*70)
    print("💡 SOLUTIONS GENERATED")
    print("─"*70)

    new_solutions = AgentSolution.objects.filter(
        created_at__gte=start_time
    )

    print(f"Total New Solutions: {new_solutions.count()}")

    # Top agents by solutions
    agent_solutions = {}
    for solution in new_solutions:
        agent_name = solution.agent.name
        if agent_name not in agent_solutions:
            agent_solutions[agent_name] = 0
        agent_solutions[agent_name] += 1

    if agent_solutions:
        print("\nTop Solution Creators:")
        for agent, count in sorted(agent_solutions.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  • {agent}: {count} solutions")

    # Solution types
    solution_types = {}
    for solution in new_solutions:
        stype = solution.solution_type or 'general'
        if stype not in solution_types:
            solution_types[stype] = 0
        solution_types[stype] += 1

    if solution_types:
        print("\nSolution Types:")
        for stype, count in sorted(solution_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  • {stype}: {count}")

    # 3. Learning Events
    print("\n" + "─"*70)
    print("🎓 AGENT LEARNING EVENTS")
    print("─"*70)

    new_learning = AgentLearning.objects.filter(
        created_at__gte=start_time
    )

    print(f"Total Learning Events: {new_learning.count()}")

    # Knowledge transfer network
    knowledge_transfers = {}
    for learning in new_learning:
        teacher = learning.teacher_agent.name
        student = learning.student_agent.name if learning.student_agent else "System"
        pair = f"{teacher} → {student}"
        if pair not in knowledge_transfers:
            knowledge_transfers[pair] = 0
        knowledge_transfers[pair] += 1

    if knowledge_transfers:
        print("\nTop Knowledge Transfers:")
        for pair, count in sorted(knowledge_transfers.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  • {pair}: {count} transfers")

    # 4. Agent Performance Changes
    print("\n" + "─"*70)
    print("📈 AGENT PERFORMANCE IMPROVEMENTS")
    print("─"*70)

    # Calculate average effectiveness improvements
    improvements = []
    for learning in new_learning.select_related('student_agent'):
        if learning.student_agent and learning.effectiveness_improvement:
            improvements.append({
                'agent': learning.student_agent.name,
                'improvement': learning.effectiveness_improvement
            })

    if improvements:
        # Group by agent and average
        agent_improvements = {}
        for imp in improvements:
            if imp['agent'] not in agent_improvements:
                agent_improvements[imp['agent']] = []
            agent_improvements[imp['agent']].append(imp['improvement'])

        print("\nTop Improved Agents:")
        improved_agents = [
            (agent, sum(imps)/len(imps))
            for agent, imps in agent_improvements.items()
        ]

        for agent, avg_imp in sorted(improved_agents, key=lambda x: x[1], reverse=True)[:5]:
            print(f"  • {agent}: +{avg_imp:.1f}% effectiveness")

    # 5. Overall System Growth
    print("\n" + "─"*70)
    print("🚀 SYSTEM GROWTH METRICS")
    print("─"*70)

    # Calculate growth rates
    total_spider = SpiderData.objects.count()
    total_solutions = AgentSolution.objects.count()
    total_learning = AgentLearning.objects.count()

    growth_table = [
        ["Metric", "Before", "After", "Growth", "Rate/Hour"],
        ["Spider Data", total_spider - new_spider_data.count(), total_spider,
         f"+{new_spider_data.count()}", f"{new_spider_data.count()/hours:.1f}"],
        ["Solutions", total_solutions - new_solutions.count(), total_solutions,
         f"+{new_solutions.count()}", f"{new_solutions.count()/hours:.1f}"],
        ["Learning Events", total_learning - new_learning.count(), total_learning,
         f"+{new_learning.count()}", f"{new_learning.count()/hours:.1f}"]
    ]

    print("\n" + tabulate(growth_table, headers="firstrow", tablefmt="grid"))

    # 6. Interesting Discoveries
    print("\n" + "─"*70)
    print("🔍 INTERESTING DISCOVERIES")
    print("─"*70)

    # Find high-value solutions
    high_value_solutions = new_solutions.filter(
        success_rate__gte=80
    ).order_by('-success_rate')[:3]

    if high_value_solutions:
        print("\nHigh Success Rate Solutions:")
        for solution in high_value_solutions:
            print(f"  • {solution.title}")
            print(f"    Agent: {solution.agent.name}")
            print(f"    Success Rate: {solution.success_rate:.1f}%")

    # Find most collaborative agents
    print("\n" + "="*70)
    print("📊 SUMMARY: Your AI system is " +
          ("actively learning! 🎉" if new_learning.count() > 10 else "learning steadily."))

    if new_spider_data.count() > 20:
        print("🕷️  Excellent spider activity - collecting lots of data!")
    if new_solutions.count() > 50:
        print("💡 Great solution generation - agents are being creative!")
    if new_learning.count() > 100:
        print("🎓 Fantastic knowledge transfer - agents are teaching each other!")

    print("="*70 + "\n")

    return {
        'spider_data': new_spider_data.count(),
        'solutions': new_solutions.count(),
        'learning': new_learning.count(),
        'hours': hours
    }


if __name__ == "__main__":
    import sys

    # Check if hours specified
    hours = 12  # default
    if len(sys.argv) > 1:
        try:
            hours = int(sys.argv[1])
        except ValueError:
            print(f"Invalid hours: {sys.argv[1]}, using default 12 hours")

    check_overnight_learning(hours)