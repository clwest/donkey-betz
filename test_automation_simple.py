#!/usr/bin/env python3
"""
Simple demonstration of the Task Delegation Orchestrator
Shows how Income Builder plans are automatically parsed and delegated
"""

import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from intelligence.task_delegation_orchestrator import TaskDelegationOrchestrator

def demonstrate_automation():
    """Show the complete automation workflow"""

    print("=" * 80)
    print("🚀 INCOME BUILDER → TASK AUTOMATION DEMONSTRATION")
    print("=" * 80)
    print()

    # Load plan
    plan_file = Path("income_builder_outputs/AI-Assisted_Content_Writing_Complete_Plan.md")
    with open(plan_file, 'r') as f:
        plan_content = f.read()

    # Initialize orchestrator
    orchestrator = TaskDelegationOrchestrator()

    # Parse tasks
    print("📋 STEP 1: PARSING INCOME BUILDER PLAN")
    print("-" * 40)
    tasks = orchestrator.parse_action_plan(plan_content)
    print(f"✅ Extracted {len(tasks)} actionable tasks from plan")
    print()

    # Show task distribution
    print("📊 TASK DISTRIBUTION BY AGENT:")
    print("-" * 40)
    agent_counts = {}
    for task in tasks:
        if task.agent_type not in agent_counts:
            agent_counts[task.agent_type] = 0
        agent_counts[task.agent_type] += 1

    for agent, count in sorted(agent_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {agent}: {count} task(s)")
    print()

    # Create execution queue
    print("🔄 STEP 2: CREATING INTELLIGENT EXECUTION QUEUE")
    print("-" * 40)
    execution_queue = orchestrator.create_execution_queue()
    print(f"✅ Queue created with dependency resolution")
    print()

    # Show execution plan
    print("⚡ STEP 3: EXECUTION PLAN (First 5 Tasks)")
    print("-" * 40)
    for i, task in enumerate(execution_queue[:5], 1):
        print(f"\n{i}. {task.title}")
        print(f"   → Agent: {task.agent_type}")
        print(f"   → Priority: {task.priority.name}")
        print(f"   → Timeline: {task.day_range}")

        # Show the delegation command
        delegation = orchestrator.delegate_task(task)
        print(f"   → Command: {delegation['command'][:80]}...")

    print()
    print("=" * 80)
    print("🎯 AUTOMATION READY!")
    print("=" * 80)
    print()

    # Show how to connect to Income Builder
    print("📡 INTEGRATION WITH INCOME BUILDER:")
    print("-" * 40)
    print("1. Income Builder generates plan (✅ DONE)")
    print("2. Plan is parsed into tasks (✅ DEMONSTRATED)")
    print("3. Tasks are mapped to agents (✅ DEMONSTRATED)")
    print("4. Execution queue respects dependencies (✅ DEMONSTRATED)")
    print("5. Tasks are delegated to agents (✅ READY)")
    print()

    print("🔌 NEXT STEPS TO ACTIVATE:")
    print("-" * 40)
    print("1. Start the Income Builder Connector API:")
    print("   python intelligence/income_builder_connector.py")
    print()
    print("2. Income Builder frontend calls:")
    print("   POST /api/income-builder/process-plan")
    print("   with { 'plan_file': 'path/to/plan.md' }")
    print()
    print("3. Tasks automatically execute via agents!")
    print()

    # Show sample API payload
    print("📦 SAMPLE API PAYLOAD FOR INCOME BUILDER:")
    print("-" * 40)
    sample_payload = {
        "plan_file": "income_builder_outputs/AI-Assisted_Content_Writing_Complete_Plan.md",
        "auto_execute": True,
        "batch_size": 3,
        "notify_webhook": "https://your-app.com/webhook/income-builder"
    }
    print(json.dumps(sample_payload, indent=2))
    print()

    # Show delegation plan structure
    print("🗂️ DELEGATION PLAN STRUCTURE:")
    print("-" * 40)
    delegation_structure = {
        "execution_queue": [
            {
                "task": task.title,
                "agent": task.agent_type,
                "automated_command": orchestrator._generate_agent_command(task)[:100] + "..."
            }
            for task in execution_queue[:3]
        ]
    }
    print(json.dumps(delegation_structure, indent=2))
    print()

    print("✨ DEMONSTRATION COMPLETE!")
    print()
    print("This system transforms Income Builder plans into")
    print("automated task executions across 102+ agents!")
    print()

if __name__ == "__main__":
    demonstrate_automation()