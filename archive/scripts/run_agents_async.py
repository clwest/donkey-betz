#!/usr/bin/env python
"""
Run agents asynchronously using Celery tasks
"""

import os
import sys
import django
import uuid
import json
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from agents.models import UnifiedAgentTemplate, AgentExecution
from agents.tasks import execute_agent_async  # Import the async task
from sports.models import Game
from django.utils import timezone
from django.db.models import Q
from celery import group


def prepare_agent_executions(game: Game, limit: int = 10):
    """Prepare agent executions for the game"""
    
    # Get betting agents
    betting_keywords = ['bet', 'odds', 'kelly', 'value', 'arbitrage', 'contrarian']
    query = Q()
    for keyword in betting_keywords:
        query |= Q(name__icontains=keyword)
    
    agents = UnifiedAgentTemplate.objects.filter(query).distinct()[:limit]
    
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
    
    executions = []
    
    for agent in agents:
        execution_id = f"async_{agent.name}_{uuid.uuid4().hex[:8]}"
        
        task_description = f"""
Analyze this NCAAF game with these specific betting lines:

{odds_data['away_team']} @ {odds_data['home_team']}

CURRENT ODDS:
• Spread: {odds_data['home_team']} -16.5 (-110) / {odds_data['away_team']} +16.5 (-110)
• Total: 54.5 points - Over -110 / Under -110
• Moneyline: {odds_data['home_team']} -650 / {odds_data['away_team']} +475

Provide specific betting recommendations using these exact odds.
Calculate expected value and recommended bet sizes where applicable.
"""
        
        # Create execution record
        execution = AgentExecution.objects.create(
            execution_id=execution_id,
            template=agent,
            task_description=task_description,
            task_type='betting_analysis',
            input_data=odds_data,
            status='pending',
            context={'async_run': True, 'timestamp': timezone.now().isoformat()}
        )
        
        executions.append(execution)
    
    return executions


def main():
    """Main execution"""
    
    # Get Wisconsin @ Alabama game
    game = Game.objects.filter(
        home_team__name__icontains='Alabama',
        away_team__name__icontains='Wisconsin'
    ).first()
    
    if not game:
        print("❌ Game not found!")
        return
    
    print(f"\n{'='*60}")
    print(f"🏈 {game.away_team.name} @ {game.home_team.name}")
    print(f"📅 {game.scheduled_start}")
    print(f"{'='*60}\n")
    
    # Clean up old pending executions
    old_pending = AgentExecution.objects.filter(
        status='pending',
        created_at__lt=timezone.now() - timezone.timedelta(hours=1)
    )
    if old_pending.exists():
        print(f"🧹 Cleaning {old_pending.count()} old pending executions...")
        old_pending.delete()
    
    # Prepare executions
    print("📝 Creating agent executions...")
    executions = prepare_agent_executions(game, limit=10)
    print(f"✅ Created {len(executions)} executions\n")
    
    # Queue them for async execution
    print("🚀 Queueing agents for async execution...")
    tasks = []
    for ex in executions:
        # Import here to avoid circular imports
        from agents.tasks import execute_agent_async
        
        # Queue the task
        task = execute_agent_async.delay(ex.execution_id)
        tasks.append(task)
        print(f"  • {ex.template.name[:40]:40} [Task ID: {task.id[:8]}...]")
    
    print(f"\n⏳ {len(tasks)} tasks queued for processing")
    print("📊 Monitoring progress...\n")
    
    # Monitor progress for up to 2 minutes
    start_time = time.time()
    timeout = 120  # 2 minutes
    
    while time.time() - start_time < timeout:
        # Check execution statuses
        pending = AgentExecution.objects.filter(
            execution_id__startswith='async_',
            status='pending'
        ).count()
        
        running = AgentExecution.objects.filter(
            execution_id__startswith='async_',
            status='running'
        ).count()
        
        completed = AgentExecution.objects.filter(
            execution_id__startswith='async_',
            status='completed'
        ).count()
        
        failed = AgentExecution.objects.filter(
            execution_id__startswith='async_',
            status='failed'
        ).count()
        
        print(f"\r⏳ Pending: {pending} | 🔄 Running: {running} | ✅ Completed: {completed} | ❌ Failed: {failed}", end='', flush=True)
        
        if pending == 0 and running == 0:
            break
        
        time.sleep(2)
    
    print(f"\n\n{'='*60}")
    print("📊 FINAL RESULTS")
    print(f"{'='*60}")
    
    # Show results
    completed_execs = AgentExecution.objects.filter(
        execution_id__startswith='async_',
        status='completed',
        result__isnull=False
    )
    
    for ex in completed_execs[:5]:
        if ex.result and 'output' in ex.result and ex.result['output']:
            print(f"\n✅ {ex.template.name if ex.template else 'Unknown'}:")
            preview = ex.result['output'][:200].replace('\n', ' ')
            print(f"   {preview}...")
    
    print(f"\n✨ Check the betting page for Wisconsin @ Alabama!")
    print(f"   The Agent Analysis Reports should now show real-time betting analysis.\n")


if __name__ == '__main__':
    # First check if we have the async task
    try:
        from agents.tasks import execute_agent_async
        main()
    except ImportError:
        print("⚠️ The execute_agent_async task doesn't exist yet.")
        print("Let's create it first...")
        
        # Show what needs to be added
        print("\nAdd this to agents/tasks.py:")
        print("-" * 40)
        print("""
@shared_task(bind=True, max_retries=1, time_limit=60)
def execute_agent_async(self, execution_id: str):
    '''Execute an agent asynchronously with timeout'''
    try:
        return execute_agent(execution_id)
    except Exception as e:
        logger.error(f"Agent execution failed: {e}")
        raise self.retry(exc=e)
""")
        print("-" * 40)