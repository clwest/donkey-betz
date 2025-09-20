#!/usr/bin/env python3
"""Test task parsing with actual plan content"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from intelligence.task_delegation_orchestrator import TaskDelegationOrchestrator
from pathlib import Path

# Read an actual plan
plan_file = Path("income_builder_outputs/AI-Assisted_Content_Writing_Complete_Plan.md")
if plan_file.exists():
    with open(plan_file, 'r') as f:
        plan_content = f.read()

    orchestrator = TaskDelegationOrchestrator()
    tasks = orchestrator.parse_action_plan(plan_content)

    print(f"✅ Successfully parsed {len(tasks)} tasks from plan!")

    if tasks:
        print("\nFirst 5 tasks:")
        for i, task in enumerate(tasks[:5], 1):
            print(f"  {i}. {task.title}")
            print(f"     → Agent: {task.agent_type}")
            print(f"     → Phase: {task.phase}")
else:
    print("❌ Plan file not found")