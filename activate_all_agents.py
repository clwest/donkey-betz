#!/usr/bin/env python
"""
Activate All 153 Agents - Use Existing Infrastructure
Created: 9/26/25 7:45 PM MST

This script uses the EXISTING agent orchestration layer to activate all agents
"""

import os
import sys
import django
import asyncio

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from backend.agents.agent_orchestration_layer import agent_orchestrator
from backend.agents.execution_tracker import execution_tracker
from datetime import datetime
import pytz

mst = pytz.timezone('America/Denver')

async def activate_all_agents():
    """Use existing orchestration to activate agents with real workflows"""

    print("🚀 Activating All 153 Agents Using Existing Infrastructure")
    print(f"🕐 Started: {datetime.now(mst).strftime('%Y-%m-%d %I:%M %p MST')}")
    print("=" * 60)

    # Start the orchestration layer
    await agent_orchestrator.start()

    # Create multiple workflows to engage different agent groups
    workflows = []

    print("\n📋 Creating Pre-Built Workflows...")

    # 1. Opportunity workflows for different skill sets
    skill_sets = [
        ['python', 'django', 'ai'],
        ['javascript', 'react', 'frontend'],
        ['data-science', 'ml', 'analytics'],
        ['content-writing', 'seo', 'marketing'],
        ['blockchain', 'crypto', 'defi']
    ]

    for i, skills in enumerate(skill_sets):
        workflow = await agent_orchestrator.create_opportunity_workflow(skills)
        workflows.append(('opportunity', workflow))
        print(f"   ✅ Opportunity Workflow {i+1}: {skills}")

    # 2. Content creation workflows
    topics = [
        'AI and Machine Learning Trends',
        'Remote Work Best Practices',
        'Cryptocurrency Investment Guide',
        'Python Development Tips',
        'Digital Marketing Strategies'
    ]

    for i, topic in enumerate(topics):
        workflow = await agent_orchestrator.create_content_workflow(topic)
        workflows.append(('content', workflow))
        print(f"   ✅ Content Workflow {i+1}: {topic}")

    # 3. Trading analysis workflows
    capitals = [1000, 5000, 10000]

    for i, capital in enumerate(capitals):
        workflow = await agent_orchestrator.create_trading_workflow(capital)
        workflows.append(('trading', workflow))
        print(f"   ✅ Trading Workflow {i+1}: ${capital}")

    print(f"\n🔄 Executing {len(workflows)} Workflows...")
    print("-" * 40)

    # Execute all workflows (this will activate agents)
    results = []
    for workflow_type, workflow in workflows:
        print(f"   🎯 Executing {workflow_type} workflow: {workflow.name}")

        try:
            result = await agent_orchestrator.execute_workflow(workflow.workflow_id)
            results.append((workflow_type, result))

            if result['success']:
                print(f"      ✅ Success - {len(result.get('results', {}))} tasks completed")
            else:
                print(f"      ❌ Failed - {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"      ❌ Exception - {str(e)}")
            results.append((workflow_type, {'success': False, 'error': str(e)}))

    print("\n" + "=" * 60)
    print("📊 ACTIVATION SUMMARY")
    print("=" * 60)

    # Check metrics after activation
    stats = execution_tracker.get_comprehensive_stats()
    print(f"Active Agents After Activation: {stats['active_agents']}")
    print(f"Total Executions: {stats.get('total_executions', 0)}")
    print(f"Success Rate: {stats['success_rate']}%")
    print(f"Files Created: {stats['files_created']}")

    # Summary by workflow type
    success_count = sum(1 for _, result in results if result.get('success', False))
    print(f"\nWorkflow Execution Success: {success_count}/{len(results)}")

    # Show active workflows
    active_workflows = agent_orchestrator.get_active_workflows()
    print(f"Currently Active Workflows: {len(active_workflows)}")

    print(f"\n🕐 Completed: {datetime.now(mst).strftime('%Y-%m-%d %I:%M %p MST')}")
    print("\n💡 Next Steps:")
    print("   1. Check dashboard - agents should now show as active")
    print("   2. Monitor WebSocket connections for real-time updates")
    print("   3. Verify frontend shows increased agent activity")

    # Stop orchestration layer
    await agent_orchestrator.stop()

if __name__ == "__main__":
    asyncio.run(activate_all_agents())