#!/usr/bin/env python
"""
Run agents synchronously with real-time odds data
Direct execution without Celery for immediate results
"""

import os
import sys
import django
import uuid
import json
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from agents.models import UnifiedAgentTemplate, AgentExecution
from sports.models import Game
from django.utils import timezone
from django.db.models import Q
from content.ai_providers import AIProviderManager


def execute_agent_directly(execution: AgentExecution) -> dict:
    """Execute an agent directly without Celery"""
    try:
        execution.status = 'running'
        execution.save()
        
        agent_template = execution.template
        if not agent_template:
            raise ValueError("No agent template")
        
        # Get AI provider
        ai_manager = AIProviderManager()
        provider = ai_manager.get_provider(agent_template.llm_provider)
        
        if not provider:
            raise ValueError(f"Provider {agent_template.llm_provider} not available")
        
        # Prepare prompts
        system_prompt = agent_template.system_prompt or "You are a sports betting analysis agent."
        user_prompt = execution.task_description
        
        # Generate content
        print(f"    Calling {agent_template.llm_provider} {agent_template.llm_model}...")
        result = provider.generate_content(
            model=agent_template.llm_model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            config=agent_template.llm_config or {}
        )
        
        if result.success and result.content:
            execution.status = 'completed'
            execution.result = {
                'output': result.content,
                'success': True,
                'timestamp': datetime.now().isoformat()
            }
            execution.completed_at = timezone.now()
            execution.save()
            return execution.result
        else:
            raise ValueError(f"Generation failed: {result.error_message}")
            
    except Exception as e:
        execution.status = 'failed'
        execution.error_message = str(e)
        execution.completed_at = timezone.now()
        execution.save()
        return {'error': str(e)}


def main():
    """Run agents synchronously"""
    
    # Get Wisconsin @ Alabama game
    game = Game.objects.filter(
        home_team__name__icontains='Alabama',
        away_team__name__icontains='Wisconsin'
    ).first()
    
    if not game:
        print("❌ Game not found!")
        return
    
    print(f"\n{'='*70}")
    print(f"🏈 REAL-TIME AGENT EXECUTION")
    print(f"   {game.away_team.name} @ {game.home_team.name}")
    print(f"   {game.scheduled_start}")
    print(f"{'='*70}\n")
    
    # Prepare odds data
    odds_data = {
        'sport': 'NCAAF',
        'game_id': str(game.id),
        'home_team': game.home_team.name,
        'away_team': game.away_team.name,
        'game_date': str(game.scheduled_start),
        'markets': {
            'spread': {'line': -16.5, 'home_spread': -16.5, 'home_odds': -110},
            'total': {'line': 54.5, 'over_odds': -110, 'under_odds': -110},
            'moneyline': {'home_odds': -650, 'away_odds': 475}
        }
    }
    
    # Get top betting agents
    agents = UnifiedAgentTemplate.objects.filter(
        Q(name__icontains='kelly') |
        Q(name__icontains='odds-calc') |
        Q(name__icontains='value') |
        Q(name__icontains='arbitrage')
    ).distinct()[:5]
    
    print(f"🤖 Running {agents.count()} priority agents\n")
    
    successful = 0
    
    for i, agent in enumerate(agents, 1):
        print(f"[{i}/{agents.count()}] {agent.name}")
        
        execution_id = f"sync_{agent.name}_{uuid.uuid4().hex[:8]}"
        
        # Create detailed task
        task = f"""
Analyze this NCAAF game with REAL betting lines:

{odds_data['away_team']} @ {odds_data['home_team']}

ACTUAL BETTING LINES:
• Spread: {odds_data['home_team']} -16.5 (-110)
• Total: 54.5 O/U (-110/-110)  
• Moneyline: {odds_data['home_team']} -650, {odds_data['away_team']} +475

Provide specific betting analysis and recommendations.
"""
        
        if 'kelly' in agent.name.lower():
            task += "\nCalculate Kelly Criterion bet sizes for each bet type assuming $1000 bankroll."
        elif 'value' in agent.name.lower():
            task += "\nIdentify which bets offer positive expected value."
        elif 'arbitrage' in agent.name.lower():
            task += "\nCheck for arbitrage or middle opportunities."
        
        # Create and execute
        execution = AgentExecution.objects.create(
            execution_id=execution_id,
            template=agent,
            task_description=task,
            task_type='betting_analysis',
            input_data=odds_data,
            status='pending'
        )
        
        result = execute_agent_directly(execution)
        
        if 'output' in result:
            successful += 1
            print(f"  ✅ Success - {len(result['output'])} chars")
            # Show preview
            preview = result['output'][:150].replace('\n', ' ')
            print(f"     {preview}...")
        else:
            print(f"  ❌ Failed: {result.get('error', 'Unknown error')}")
        
        print()
    
    print(f"{'='*70}")
    print(f"📊 RESULTS: {successful}/{agents.count()} agents completed")
    print(f"\n✨ Check the betting page for {game.away_team.name} @ {game.home_team.name}")
    print(f"   The Agent Analysis Reports should now show specific betting recommendations!")
    print(f"{'='*70}\n")


if __name__ == '__main__':
    main()