#!/usr/bin/env python
"""
Test agent with explicit NCAAF game data in the task description
"""

import os
import sys
import django
import uuid

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from agents.models import UnifiedAgentTemplate, AgentExecution
from agents.tasks import execute_agent

# Get a betting analysis agent
agent = UnifiedAgentTemplate.objects.filter(
    name='odds-calculation-agent'
).first()

if not agent:
    print("Odds calculation agent not found!")
    sys.exit(1)

# Create a very explicit task description
task_description = """
Analyze this NCAAF (college football) betting opportunity:

Game: Oklahoma Sooners @ Temple Owls
Sport: NCAA Football (NCAAF)
Date: September 13, 2025

Current Betting Lines:
- Spread: Oklahoma -21.5 (both sides -110)
- Total: 58.5 O/U (both sides -110)
- Moneyline: Oklahoma -1200, Temple +750

Please provide:
1. Implied probability calculations for each bet
2. Expected value analysis
3. Specific betting recommendation with reasoning
4. Suggested bet size for a $1000 bankroll

Be specific about this being NCAAF/college football, not basketball or any other sport.
"""

# Simple input data
input_data = {
    'sport': 'NCAAF',
    'home_team': 'Temple Owls',
    'away_team': 'Oklahoma Sooners',
    'task': task_description
}

# Create execution
execution_id = f"test_simple_{uuid.uuid4().hex[:8]}"

execution = AgentExecution.objects.create(
    execution_id=execution_id,
    template=agent,
    task_description=task_description,
    task_type='betting_analysis',
    input_data=input_data
)

print(f"Created execution: {execution_id}")
print(f"Agent: {agent.name}")
print("\nExecuting with explicit NCAAF data...")

try:
    result = execute_agent(execution_id)
    print("\n✅ Execution completed!")
    print("\nAgent Response:")
    print("-" * 50)
    if result and 'output' in result:
        output = result['output']
        if output:
            print(output[:2000])  # First 2000 chars
            if len(output) > 2000:
                print("\n[... response truncated ...]")
        else:
            print("Empty output received")
    else:
        print("No output in result")
except Exception as e:
    print(f"\n❌ Execution failed: {e}")

# Check execution
execution.refresh_from_db()
print(f"\nFinal status: {execution.status}")
if execution.llm_response:
    print(f"LLM responded: Yes ({len(execution.llm_response)} chars)")
else:
    print(f"LLM responded: No")