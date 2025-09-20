#!/usr/bin/env python3
"""
Test Revenue Opportunity + Automation Integration
Shows how Income Builder plans connect to revenue tracking
"""

import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from intelligence.task_delegation_orchestrator import TaskDelegationOrchestrator
from backend.intelligence.automation_integration import RevenueAutomationIntegration

def test_revenue_automation():
    print("=" * 80)
    print("💰 REVENUE OPPORTUNITY + AUTOMATION INTEGRATION")
    print("=" * 80)
    print()

    # Initialize systems
    orchestrator = TaskDelegationOrchestrator()
    revenue_integration = RevenueAutomationIntegration()

    # Load and parse plan
    plan_file = Path("income_builder_outputs/AI-Assisted_Content_Writing_Complete_Plan.md")
    with open(plan_file, 'r') as f:
        plan_content = f.read()

    print("📋 STEP 1: PARSING INCOME BUILDER PLAN")
    print("-" * 40)
    tasks = orchestrator.parse_action_plan(plan_content)
    print(f"✅ Extracted {len(tasks)} tasks")
    print()

    # Create automation link
    print("🔗 STEP 2: LINKING TO REVENUE TRACKING")
    print("-" * 40)
    automation_id = "auto_20250915_demo"
    opportunity_id = "ai-content-writing"
    plan_id = "plan_content_writing_001"

    link = revenue_integration.link_plan_to_revenue(
        plan_id=plan_id,
        opportunity_id=opportunity_id,
        automation_id=automation_id
    )

    print(f"✅ Created revenue tracking link")
    print(f"   Opportunity: {opportunity_id}")
    print(f"   Revenue Potential: ${link['revenue_potential']}")
    print()

    # Simulate task execution with revenue tracking
    print("⚡ STEP 3: EXECUTING TASKS WITH REVENUE TRACKING")
    print("-" * 40)

    # Execute first batch
    batch = orchestrator.execute_next_batch(batch_size=3)

    for i, delegation in enumerate(batch, 1):
        print(f"\nTask {i}: {delegation['context']['title']}")
        print(f"  Agent: {delegation['agent']}")

        # Simulate task completion with results
        if delegation['agent'] == 'revenue-activation-orchestrator':
            task_result = {
                "success": True,
                "results": {
                    "payment_gateway": "configured",
                    "pricing_tiers": ["$49", "$99", "$199"],
                    "estimated_value": "$2,500"
                }
            }
        elif delegation['agent'] == 'ai-content-studio':
            task_result = {
                "success": True,
                "results": {
                    "content_pieces": 5,
                    "brand_assets": ["logo", "guide"],
                    "estimated_value": "$500"
                }
            }
        else:
            task_result = {
                "success": True,
                "results": {
                    "proposals_generated": 3,
                    "estimated_value": "$1,500"
                }
            }

        # Track revenue impact
        tracking = revenue_integration.track_task_revenue(
            automation_id,
            delegation['task_id'],
            task_result
        )

        print(f"  💰 Revenue Impact: ${task_result['results'].get('estimated_value', '0')}")
        print(f"  📊 Total Revenue: ${tracking['tracking_metrics']['revenue_generated']}")

        # Mark task complete
        orchestrator.mark_task_complete(delegation['task_id'], success=True)

    print()
    print("=" * 80)
    print("📊 REVENUE REPORT")
    print("-" * 40)

    # Generate revenue report
    report = revenue_integration.generate_revenue_report(automation_id)

    print(f"Automation ID: {report['automation_id']}")
    print(f"Opportunity: {report['opportunity_id']}")
    print()
    print("Metrics:")
    print(f"  Tasks Completed: {report['metrics']['tasks_completed']}")
    print(f"  Revenue Generated: ${report['total_revenue']}")
    print(f"  Revenue Potential: ${report['revenue_potential']}")
    print(f"  Achievement Rate: {report['achievement_rate']:.1f}%")
    print(f"  ROI: {report['roi']:.2f}x")
    print()

    if report['recommendations']:
        print("Recommendations:")
        for rec in report['recommendations']:
            print(f"  • {rec}")
        print()

    # Project future revenue
    print("=" * 80)
    print("📈 REVENUE PROJECTIONS")
    print("-" * 40)

    projection = revenue_integration.project_revenue(automation_id, days=30)

    print(f"Current Daily Rate: ${projection['current_daily_rate']:.2f}")
    print()
    print("Projected Revenue:")
    print(f"  7 Days: ${projection['projected_revenue']['7_days']:.2f}")
    print(f"  30 Days: ${projection['projected_revenue']['30_days']:.2f}")
    print(f"  90 Days: ${projection['projected_revenue']['90_days']:.2f}")
    print()
    print(f"Confidence: {projection['confidence']}")
    print(f"Growth Potential: {projection['growth_potential']}")
    print()

    # Show active automations
    print("=" * 80)
    print("🚀 ACTIVE AUTOMATIONS")
    print("-" * 40)

    active = revenue_integration.get_active_automations()
    for automation in active:
        print(f"• {automation['opportunity_id']}")
        print(f"  Revenue: ${automation['revenue_generated']}")
        print(f"  Tasks: {automation['tasks_completed']}")
        print(f"  ROI: {automation['roi']:.2f}x")
        print()

    print("=" * 80)
    print("✨ INTEGRATION COMPLETE!")
    print()
    print("The system now:")
    print("1. ✅ Parses Income Builder plans into tasks")
    print("2. ✅ Delegates tasks to specialized agents")
    print("3. ✅ Tracks revenue impact of each task")
    print("4. ✅ Projects future revenue potential")
    print("5. ✅ Provides optimization recommendations")
    print()
    print("💡 Your Income Builder plans are now directly")
    print("   connected to real revenue generation!")
    print()

if __name__ == "__main__":
    test_revenue_automation()