#!/usr/bin/env python3
"""
Test Task Delegation Orchestrator
Demonstrates automated task extraction and delegation from Income Builder plans
"""

import json
from pathlib import Path
from intelligence.task_delegation_orchestrator import TaskDelegationOrchestrator

def test_task_delegation():
    # Load the AI Content Writing plan
    plan_path = Path("income_builder_outputs/AI-Assisted_Content_Writing_Complete_Plan.md")
    with open(plan_path, 'r') as f:
        plan_content = f.read()

    # Initialize orchestrator
    orchestrator = TaskDelegationOrchestrator()

    print("=" * 80)
    print("🚀 TASK DELEGATION ORCHESTRATOR - DEMONSTRATION")
    print("=" * 80)
    print()

    # Parse the action plan
    print("📋 PARSING ACTION PLAN...")
    tasks = orchestrator.parse_action_plan(plan_content)
    print(f"✅ Extracted {len(tasks)} actionable tasks")
    print()

    # Display extracted tasks by phase
    print("📊 TASKS BY PHASE:")
    print("-" * 40)
    phases = {}
    for task in tasks:
        if task.phase not in phases:
            phases[task.phase] = []
        phases[task.phase].append(task)

    for phase, phase_tasks in phases.items():
        print(f"\n{phase}:")
        for task in phase_tasks:
            print(f"  • [{task.priority.name}] {task.title}")
            print(f"    Agent: {task.agent_type}")
            print(f"    Timeline: {task.day_range}")
            if task.platform_tools:
                print(f"    Tools: {', '.join(task.platform_tools)}")
            if task.success_metrics:
                print(f"    Metrics: {task.success_metrics}")
            print()

    # Create execution queue
    print("=" * 80)
    print("🔄 CREATING EXECUTION QUEUE...")
    print("-" * 40)
    execution_queue = orchestrator.create_execution_queue()
    print(f"✅ Queue created with {len(execution_queue)} tasks")
    print()

    # Show first 5 tasks in priority order
    print("📝 TOP 5 PRIORITY TASKS:")
    for i, task in enumerate(execution_queue[:5], 1):
        print(f"\n{i}. {task.title}")
        print(f"   Priority: {task.priority.name}")
        print(f"   Agent: {task.agent_type}")
        print(f"   Dependencies: {len(task.dependencies)} tasks")

    # Simulate batch execution
    print()
    print("=" * 80)
    print("⚡ SIMULATING BATCH EXECUTION...")
    print("-" * 40)

    # Execute first batch
    batch1 = orchestrator.execute_next_batch(batch_size=3)
    print(f"\n🎯 BATCH 1 - Delegating {len(batch1)} tasks:")
    for delegation in batch1:
        print(f"\n  Task: {delegation['context']['title']}")
        print(f"  Agent: {delegation['agent']}")
        print(f"  Priority: {delegation['context']['priority']}")
        print(f"  Command: {delegation['command'][:100]}...")

    # Mark first batch as complete
    print("\n✅ Marking Batch 1 tasks as complete...")
    for delegation in batch1:
        orchestrator.mark_task_complete(delegation['task_id'], success=True)

    # Execute second batch
    batch2 = orchestrator.execute_next_batch(batch_size=3)
    print(f"\n🎯 BATCH 2 - Delegating {len(batch2)} tasks:")
    for delegation in batch2:
        print(f"\n  Task: {delegation['context']['title']}")
        print(f"  Agent: {delegation['agent']}")
        print(f"  Priority: {delegation['context']['priority']}")

    # Get progress report
    print()
    print("=" * 80)
    print("📈 PROGRESS REPORT")
    print("-" * 40)
    progress = orchestrator.get_progress_report()
    print(f"Total Tasks: {progress['total_tasks']}")
    print(f"Completed: {progress['completed']}")
    print(f"In Progress: {progress['in_progress']}")
    print(f"Pending: {progress['pending']}")
    print(f"Completion: {progress['completion_percentage']:.1f}%")

    print("\nPhase Breakdown:")
    for phase, stats in progress['status_breakdown'].items():
        print(f"  {phase}: {stats['completed']}/{stats['total']} completed")

    # Export delegation plan
    print()
    print("=" * 80)
    print("💾 EXPORTING DELEGATION PLAN...")
    print("-" * 40)

    delegation_plan = {
        "plan_type": "AI-Assisted Content Writing",
        "total_tasks": len(tasks),
        "execution_queue": [
            {
                "task_id": task.id,
                "title": task.title,
                "agent": task.agent_type,
                "phase": task.phase,
                "priority": task.priority.name,
                "timeline": task.day_range,
                "dependencies": task.dependencies,
                "platform_tools": task.platform_tools,
                "success_metrics": task.success_metrics
            }
            for task in execution_queue
        ]
    }

    output_path = Path("income_builder_outputs/delegation_plan.json")
    with open(output_path, 'w') as f:
        json.dump(delegation_plan, f, indent=2)

    print(f"✅ Delegation plan exported to: {output_path}")
    print()
    print("🎉 DEMONSTRATION COMPLETE!")
    print()
    print("Next Steps:")
    print("1. Connect to actual agent execution endpoints")
    print("2. Implement real-time status monitoring")
    print("3. Add webhook notifications for task completion")
    print("4. Create dashboard for progress visualization")
    print()

if __name__ == "__main__":
    test_task_delegation()