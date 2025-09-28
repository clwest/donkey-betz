#!/usr/bin/env python
"""
Run agents in batches with timeout and better error handling
"""

import os
import sys
import django
import uuid
import json
import signal
from contextlib import contextmanager
from typing import Dict, Optional

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from agents.models import UnifiedAgentTemplate, AgentExecution
from agents.tasks import execute_agent
from sports.models import Game
from django.utils import timezone
from django.db.models import Q


class TimeoutException(Exception):
    pass


@contextmanager
def timeout(seconds):
    """Context manager for timing out operations"""
    def signal_handler(signum, frame):
        raise TimeoutException(f"Operation timed out after {seconds} seconds")
    
    # Set the signal handler and alarm
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Disable the alarm
        signal.alarm(0)


def get_simple_odds_data(game: Game) -> Dict:
    """Get simplified odds data for the game"""
    return {
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


def execute_single_agent(agent: UnifiedAgentTemplate, game: Game, 
                        timeout_seconds: int = 30) -> Dict:
    """Execute a single agent with timeout"""
    
    odds_data = get_simple_odds_data(game)
    execution_id = f"batch_{agent.name}_{uuid.uuid4().hex[:8]}"
    
    # Create simple task description
    task_description = f"""
Analyze this NCAAF game with these betting lines:

{odds_data['away_team']} @ {odds_data['home_team']}

BETTING LINES:
• Spread: Alabama -16.5 (-110)
• Total: 54.5 O/U (-110/-110)  
• Moneyline: Alabama -650, Wisconsin +475

Provide specific betting analysis using these exact odds.
"""
    
    try:
        # Create execution
        execution = AgentExecution.objects.create(
            execution_id=execution_id,
            template=agent,
            task_description=task_description,
            task_type='betting_analysis',
            input_data=odds_data,
            context={'batch_run': True}
        )
        
        # Execute with timeout
        with timeout(timeout_seconds):
            result = execute_agent(execution.execution_id)
            
        if result and 'output' in result and result['output']:
            return {
                'status': 'success',
                'output_length': len(result['output']),
                'preview': result['output'][:150]
            }
        else:
            return {'status': 'no_output'}
            
    except TimeoutException:
        # Mark as failed if it exists
        try:
            ex = AgentExecution.objects.get(execution_id=execution_id)
            ex.status = 'failed'
            ex.error_message = 'Timeout'
            ex.save()
        except:
            pass
        return {'status': 'timeout'}
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)[:100]
        }


def main():
    """Run agents in batches"""
    
    # Get Wisconsin @ Alabama game
    game = Game.objects.filter(
        home_team__name__icontains='Alabama',
        away_team__name__icontains='Wisconsin'
    ).first()
    
    if not game:
        print("❌ Game not found!")
        return
    
    print(f"\n🏈 {game.away_team.name} @ {game.home_team.name}")
    print(f"📅 {game.scheduled_start}\n")
    
    # Get betting agents
    betting_keywords = ['bet', 'odds', 'kelly', 'value', 'arbitrage', 'contrarian']
    query = Q()
    for keyword in betting_keywords:
        query |= Q(name__icontains=keyword)
    
    agents = UnifiedAgentTemplate.objects.filter(query).distinct()[:10]  # Limit to 10
    
    print(f"🤖 Running {agents.count()} agents with 30-second timeout each\n")
    
    results = {
        'success': 0,
        'timeout': 0,
        'error': 0,
        'no_output': 0
    }
    
    for i, agent in enumerate(agents, 1):
        print(f"[{i}/{agents.count()}] {agent.name[:40]:40} ", end='', flush=True)
        
        result = execute_single_agent(agent, game, timeout_seconds=30)
        
        if result['status'] == 'success':
            results['success'] += 1
            print(f"✅ {result['output_length']} chars")
        elif result['status'] == 'timeout':
            results['timeout'] += 1
            print("⏱️ Timeout")
        elif result['status'] == 'no_output':
            results['no_output'] += 1
            print("📭 No output")
        else:
            results['error'] += 1
            print(f"❌ {result.get('error', 'Error')[:30]}")
    
    # Summary
    print(f"\n{'='*50}")
    print(f"📊 SUMMARY")
    print(f"{'='*50}")
    print(f"✅ Successful: {results['success']}")
    print(f"⏱️ Timeouts: {results['timeout']}")
    print(f"📭 No Output: {results['no_output']}")
    print(f"❌ Errors: {results['error']}")
    
    if results['success'] > 0:
        print(f"\n✨ Check the betting page for new agent analysis!")


if __name__ == '__main__':
    main()