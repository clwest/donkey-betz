#!/usr/bin/env python
"""
Test agent execution with proper NCAAF game data
"""

import os
import sys
import django
import uuid
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from agents.models import UnifiedAgentTemplate, AgentExecution
from agents.tasks import execute_agent
from sports.models import Game

# Get the game
game = Game.objects.filter(
    home_team__name__icontains='Temple',
    away_team__name__icontains='Oklahoma'
).first()

if not game:
    print("Game not found!")
    sys.exit(1)

# Get a betting agent
agent = UnifiedAgentTemplate.objects.filter(
    name='kelly-bet-sizing-agent'
).first()

if not agent:
    print("Kelly bet sizing agent not found!")
    sys.exit(1)

# Prepare proper input data
proper_input_data = {
    'sport': 'NCAAF',
    'game_id': str(game.id),
    'home_team': game.home_team.name,
    'away_team': game.away_team.name,
    'league': 'NCAA Football',
    'game_time': str(game.scheduled_start),
    'venue': 'Lincoln Financial Field',  # Temple's stadium
    
    # Provide sample odds data (since real data is incomplete)
    'markets': {
        'spread': {
            'line': -21.5,  # Oklahoma favored by 21.5
            'home_odds': -110,
            'away_odds': -110
        },
        'total': {
            'line': 58.5,
            'over_odds': -110,
            'under_odds': -110
        },
        'moneyline': {
            'home_odds': +750,  # Temple big underdog
            'away_odds': -1200  # Oklahoma heavy favorite
        }
    },
    
    # Additional context
    'analysis_request': 'Calculate optimal bet size using Kelly Criterion for Oklahoma -21.5 spread',
    'bankroll': 1000,
    'win_probability': 0.65,  # Estimated 65% chance Oklahoma covers
    'kelly_fraction': 0.25  # Use 1/4 Kelly for safety
}

# Create execution with proper data
execution_id = f"test_{agent.name}_{uuid.uuid4().hex[:8]}"

execution = AgentExecution.objects.create(
    execution_id=execution_id,
    template=agent,
    task_description=f"Analyze NCAAF game: {game.away_team.name} @ {game.home_team.name} - Calculate optimal bet sizing using Kelly Criterion",
    task_type='betting_analysis',
    input_data=proper_input_data,
    context={
        'sport': 'NCAAF',
        'test_execution': True
    }
)

print(f"Created execution: {execution_id}")
print(f"Agent: {agent.name}")
print(f"Game: {game.away_team.name} @ {game.home_team.name}")
print("\nExecuting agent with proper NCAAF data...")

try:
    result = execute_agent(execution_id)
    print("\n✅ Execution completed!")
    print("\nAgent Response:")
    print("-" * 50)
    if result and 'output' in result:
        print(result['output'][:1000])  # First 1000 chars
        if len(result['output']) > 1000:
            print("\n[... response truncated ...]")
    else:
        print("No output received")
except Exception as e:
    print(f"\n❌ Execution failed: {e}")

# Check execution status
execution.refresh_from_db()
print(f"\nFinal status: {execution.status}")
print(f"Has result: {bool(execution.result)}")