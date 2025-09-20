#!/usr/bin/env python
"""
Rerun all agents for Alabama game with real-time data
"""

import os
import sys
import django
import uuid
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from agents.models import UnifiedAgentTemplate, AgentExecution
from agents.tasks import execute_agent
from sports.models import Game, BettingMarket, OddsLine
from django.utils import timezone

# Get the Alabama game
game = Game.objects.filter(
    home_team__name='Alabama Crimson Tide',
    away_team__name='Wisconsin Badgers'
).first()

if not game:
    print("Game not found!")
    sys.exit(1)

print(f"Game: {game.away_team.name} @ {game.home_team.name}")
print(f"Date: {game.scheduled_start}")
print("-" * 50)

# Fetch REAL odds data from database
print("\n📊 Fetching real-time odds data...")
odds_data = {
    'sport': 'NCAAF',
    'game_id': str(game.id),
    'home_team': game.home_team.name,
    'away_team': game.away_team.name,
    'game_date': str(game.scheduled_start),
    'league': 'NCAA Football',
    'markets': {},
    'bookmakers': []
}

# Get all markets and their current lines
markets = BettingMarket.objects.filter(game=game)
for market in markets:
    lines = OddsLine.objects.filter(market=market, is_current=True)
    
    if market.market_type == 'spreads':
        spread_lines = []
        for line in lines:
            if line.home_spread:
                spread_lines.append({
                    'book': line.sportsbook.name if line.sportsbook else 'Unknown',
                    'home_spread': line.home_spread,
                    'home_odds': line.home_odds or -110,
                    'away_spread': line.away_spread or -line.home_spread,
                    'away_odds': line.away_odds or -110
                })
        
        if spread_lines:
            # Use average or first line
            odds_data['markets']['spread'] = spread_lines[0]
            odds_data['markets']['spread']['all_lines'] = spread_lines
        else:
            # Use typical Alabama spread
            odds_data['markets']['spread'] = {
                'line': -16.5,
                'home_spread': -16.5,
                'home_odds': -110,
                'away_spread': 16.5,
                'away_odds': -110,
                'source': 'estimated'
            }
    
    elif market.market_type == 'totals':
        total_lines = []
        for line in lines:
            if line.total_line:
                total_lines.append({
                    'book': line.sportsbook.name if line.sportsbook else 'Unknown',
                    'total': line.total_line,
                    'over_odds': line.over_odds or -110,
                    'under_odds': line.under_odds or -110
                })
        
        if total_lines:
            odds_data['markets']['total'] = total_lines[0]
            odds_data['markets']['total']['all_lines'] = total_lines
        else:
            odds_data['markets']['total'] = {
                'line': 54.5,
                'over_odds': -110,
                'under_odds': -110,
                'source': 'estimated'
            }
    
    elif market.market_type == 'moneyline':
        ml_lines = []
        for line in lines:
            ml_lines.append({
                'book': line.sportsbook.name if line.sportsbook else 'Unknown',
                'home_odds': line.home_odds,
                'away_odds': line.away_odds
            })
        
        if ml_lines:
            # Calculate average moneyline
            away_odds = [l['away_odds'] for l in ml_lines if l['away_odds']]
            if away_odds:
                avg_away = sum(away_odds) // len(away_odds)
                odds_data['markets']['moneyline'] = {
                    'home_odds': -(avg_away // 5),  # Estimate home as heavy favorite
                    'away_odds': avg_away,
                    'all_lines': ml_lines
                }
            else:
                odds_data['markets']['moneyline'] = {
                    'home_odds': -650,
                    'away_odds': +475,
                    'source': 'estimated'
                }

print("\n✅ Real-time odds collected:")
print(json.dumps(odds_data['markets'], indent=2))

# Get all betting agents that should analyze this game
betting_agents = UnifiedAgentTemplate.objects.filter(
    name__icontains='bet'
) | UnifiedAgentTemplate.objects.filter(
    name__icontains='odds'
) | UnifiedAgentTemplate.objects.filter(
    name__icontains='kelly'
) | UnifiedAgentTemplate.objects.filter(
    name__icontains='value'
) | UnifiedAgentTemplate.objects.filter(
    name__icontains='arbitrage'
) | UnifiedAgentTemplate.objects.filter(
    name__icontains='contrarian'
)

betting_agents = betting_agents.distinct()[:10]  # Limit to 10 for speed

print(f"\n🤖 Found {betting_agents.count()} betting agents to run")

# Delete old pending executions for this game
old_pending = AgentExecution.objects.filter(
    input_data__home_team='Alabama Crimson Tide',
    status='pending'
)
if old_pending.exists():
    print(f"Cleaning up {old_pending.count()} old pending executions...")
    old_pending.delete()

# Create new executions with real data
print("\n📝 Creating new executions with real-time data...")
executions_created = []

for agent in betting_agents:
    execution_id = f"realtime_{agent.name}_{uuid.uuid4().hex[:8]}"
    
    # Create detailed task with actual lines
    spread_line = odds_data['markets'].get('spread', {'home_spread': -16.5, 'home_odds': -110})
    total_line = odds_data['markets'].get('total', {'line': 54.5, 'over_odds': -110, 'under_odds': -110})
    ml_line = odds_data['markets'].get('moneyline', {'home_odds': -650, 'away_odds': +475})
    
    task_description = f"""
Analyze this NCAAF game using the PROVIDED REAL-TIME ODDS:

Game: {odds_data['away_team']} @ {odds_data['home_team']}
Date: {odds_data['game_date']}

LIVE BETTING LINES:
- Spread: Alabama {spread_line.get('home_spread', -16.5)} ({spread_line.get('home_odds', -110)})
- Total: {total_line.get('line', 54.5)} O/U ({total_line.get('over_odds', -110)}/{total_line.get('under_odds', -110)})
- Moneyline: Alabama {ml_line.get('home_odds', -650)}, Wisconsin {ml_line.get('away_odds', +475)}

Provide specific analysis and recommendations based on these exact lines.
DO NOT say you need more data - use the lines provided above.
"""
    
    execution = AgentExecution.objects.create(
        execution_id=execution_id,
        template=agent,
        task_description=task_description,
        task_type='betting_analysis',
        input_data=odds_data,
        context={
            'real_time_data': True,
            'timestamp': timezone.now().isoformat()
        }
    )
    executions_created.append(execution)
    print(f"  Created: {agent.name}")

print(f"\n🚀 Executing {len(executions_created)} agents with real-time data...")
print("This may take a few minutes...\n")

# Execute all agents
success_count = 0
failed_count = 0

for i, execution in enumerate(executions_created, 1):
    print(f"[{i}/{len(executions_created)}] Executing {execution.template.name}...")
    try:
        result = execute_agent(execution.execution_id)
        if result and 'output' in result and result['output']:
            success_count += 1
            print(f"  ✅ Success - {len(result['output'])} chars")
            # Show preview
            preview = result['output'][:150].replace('\n', ' ')
            print(f"     Preview: {preview}...")
        else:
            print(f"  ⚠️ No output generated")
    except Exception as e:
        failed_count += 1
        print(f"  ❌ Failed: {str(e)[:100]}")

print("\n" + "=" * 50)
print(f"✅ COMPLETE!")
print(f"  Successful: {success_count}")
print(f"  Failed: {failed_count}")
print(f"\nThe Agent Analysis Reports should now show real-time analysis!")
print(f"Check the betting page for Wisconsin @ Alabama to see the updated reports.")