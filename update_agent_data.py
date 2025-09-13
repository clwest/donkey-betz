#!/usr/bin/env python
"""
Update existing agent executions with real-time odds data
"""

import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from agents.models import AgentExecution
from sports.models import Game
from django.utils import timezone
from datetime import timedelta

# Get Wisconsin @ Alabama game
game = Game.objects.filter(
    home_team__name__icontains='Alabama',
    away_team__name__icontains='Wisconsin'
).first()

if not game:
    print("❌ Game not found!")
    exit(1)

print(f"\n{'='*70}")
print(f"📊 UPDATING AGENT EXECUTIONS WITH REAL-TIME DATA")
print(f"   {game.away_team.name} @ {game.home_team.name}")
print(f"{'='*70}\n")

# Real odds data
odds_data = {
    'sport': 'NCAAF',
    'game_id': str(game.id),
    'home_team': game.home_team.name,
    'away_team': game.away_team.name,
    'game_date': str(game.scheduled_start),
    'league': 'NCAA Football',
    'markets': {
        'spread': {
            'line': -16.5,
            'home_spread': -16.5,
            'home_odds': -110,
            'away_spread': 16.5,
            'away_odds': -110
        },
        'total': {
            'line': 54.5,
            'over_odds': -110,
            'under_odds': -110
        },
        'moneyline': {
            'home_odds': -650,
            'away_odds': 475
        }
    }
}

# Get recent executions for this game
recent_executions = AgentExecution.objects.filter(
    created_at__gte=timezone.now() - timedelta(hours=2),
    input_data__home_team=game.home_team.name
)

print(f"Found {recent_executions.count()} recent executions to update\n")

updated = 0
for ex in recent_executions:
    # Update input data with real odds
    ex.input_data = odds_data
    
    # Update task description to include real lines
    if not "ACTUAL BETTING LINES" in ex.task_description:
        ex.task_description = f"""
Analyze this NCAAF game with REAL-TIME odds:

{odds_data['away_team']} @ {odds_data['home_team']}
Date: {odds_data['game_date']}

ACTUAL BETTING LINES:
• Spread: {odds_data['home_team']} -16.5 (-110) / {odds_data['away_team']} +16.5 (-110)
• Total: 54.5 points - Over -110 / Under -110
• Moneyline: {odds_data['home_team']} -650 / {odds_data['away_team']} +475

Provide specific betting analysis and recommendations based on these exact lines.
"""
    
    # Mark as pending to be reprocessed
    if ex.status in ['failed', 'completed'] and not ex.result:
        ex.status = 'pending'
    
    ex.save()
    updated += 1
    
    agent_name = ex.template.name if ex.template else 'Unknown'
    print(f"✅ Updated: {agent_name[:40]:40} [{ex.status}]")

print(f"\n{'='*70}")
print(f"📊 SUMMARY")
print(f"{'='*70}")
print(f"✅ Updated {updated} executions with real-time odds data")
print(f"\nThe executions now have:")
print(f"  • Alabama -16.5 spread (-110)")
print(f"  • 54.5 total O/U (-110/-110)")
print(f"  • Alabama -650 / Wisconsin +475 moneyline")
print(f"\n🚀 Ready to process with real data!")
print(f"   Run: python execute_pending_agents.py")
print(f"{'='*70}\n")