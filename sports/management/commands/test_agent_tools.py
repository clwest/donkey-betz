"""
Test Sports Agents with Tool Integration

Run this to verify agents can access and use sports data tools.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import json

from core.models.agents_registry import UnifiedAgentTemplate, AgentExecution
from agents.tasks_enhanced import execute_agent_with_tools, execute_tool
from sports.models import Game, Team, League
from core.tools import ToolRegistry


class Command(BaseCommand):
    help = 'Test sports agents with tool integration'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--agent',
            type=str,
            default='kelly-bet-sizing',
            help='Agent to test'
        )
        parser.add_argument(
            '--game-id',
            type=str,
            help='Game ID to analyze'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n🔧 Testing Sports Agent Tool Integration\n'))
        
        # List available tools
        self.stdout.write('📦 Available Tools:')
        for tool_name in ToolRegistry.list_tools():
            tool = ToolRegistry.get_tool(tool_name)
            if tool:
                self.stdout.write(f'  ✓ {tool_name}: {tool.description if hasattr(tool, "description") else "Available"}')
        
        # Test specific tools
        self.stdout.write('\n🧪 Testing Tool Execution:')
        
        # Test odds data access
        self.stdout.write('\n1️⃣ Testing Odds Data Access Tool:')
        odds_result = execute_tool(
            'odds_data_access',
            sport='americanfootball_nfl',
            market='h2h'
        )
        if odds_result['success']:
            self.stdout.write(self.style.SUCCESS('  ✓ Odds data retrieved successfully'))
            if odds_result['data'].get('live_odds'):
                self.stdout.write(f'  📊 Found {len(odds_result["data"]["live_odds"])} live odds')
        else:
            self.stdout.write(self.style.ERROR(f'  ✗ Failed: {odds_result["error"]}'))
        
        # Test mathematical calculations
        self.stdout.write('\n2️⃣ Testing Mathematical Calculations Tool:')
        math_result = execute_tool(
            'mathematical_calculations',
            operation='implied_probability',
            odds=-150
        )
        if math_result['success']:
            self.stdout.write(self.style.SUCCESS('  ✓ Math calculation successful'))
            self.stdout.write(f'  📈 -150 odds = {math_result["data"]["percentage"]} implied probability')
        else:
            self.stdout.write(self.style.ERROR(f'  ✗ Failed: {math_result["error"]}'))
        
        # Test Kelly Criterion
        self.stdout.write('\n3️⃣ Testing Kelly Criterion Tool:')
        kelly_result = execute_tool(
            'kelly_criterion',
            probability=0.55,
            odds=110,
            bankroll=1000,
            kelly_fraction=0.25
        )
        if kelly_result['success']:
            self.stdout.write(self.style.SUCCESS('  ✓ Kelly calculation successful'))
            self.stdout.write(f'  💰 Recommended bet: ${kelly_result["data"]["recommended_bet"]:.2f}')
            self.stdout.write(f'  📊 Kelly percentage: {kelly_result["data"]["adjusted_kelly"]:.2f}%')
        else:
            self.stdout.write(self.style.ERROR(f'  ✗ Failed: {kelly_result["error"]}'))
        
        # Test with an actual agent
        agent_name = options['agent']
        self.stdout.write(f'\n🤖 Testing Agent: {agent_name}')
        
        try:
            agent = UnifiedAgentTemplate.objects.get(name=agent_name)
            self.stdout.write(f'  Found agent: {agent.display_name}')
            self.stdout.write(f'  Required tools: {", ".join(agent.required_tools)}')
            
            # Create test execution
            game_id = options.get('game_id')
            if not game_id:
                # Try to find a recent game
                recent_game = Game.objects.filter(
                    scheduled_start__gte=timezone.now() - timedelta(days=7)
                ).first()
                if recent_game:
                    game_id = str(recent_game.id)
                    self.stdout.write(f'  Using game: {recent_game.away_team.name} @ {recent_game.home_team.name}')
            
            # Create execution with tool context
            execution = AgentExecution.objects.create(
                template=agent,
                execution_id=f'test_{agent_name}_{datetime.now().timestamp()}',
                task_description='Analyze the betting opportunity and provide recommendations',
                input_data={
                    'game_id': game_id,
                    'sport': 'nfl',
                    'bet_analysis': {
                        'odds': 110,
                        'win_probability': 0.55,
                        'bankroll': 1000,
                        'kelly_fraction': 0.25
                    },
                    'odds_to_analyze': -150
                },
                context={
                    'test_mode': True,
                    'include_tools': True
                }
            )
            
            self.stdout.write(f'\n  Executing agent with tools...')
            
            # Execute with enhanced tools
            from agents.tasks_enhanced import execute_agent_with_tools
            result = execute_agent_with_tools.apply(args=[execution.execution_id]).get(timeout=30)
            
            if result['success']:
                self.stdout.write(self.style.SUCCESS('\n✅ Agent execution successful!'))
                self.stdout.write('\n📝 Agent Response:')
                self.stdout.write('-' * 50)
                self.stdout.write(result['output'][:500] + '...' if len(result['output']) > 500 else result['output'])
                
                if result.get('tools_used'):
                    self.stdout.write('\n🔧 Tools Used:')
                    for tool in result['tools_used']:
                        self.stdout.write(f'  • {tool}')
                
                if result.get('tool_results'):
                    self.stdout.write('\n📊 Tool Results:')
                    for tool_name, tool_data in result['tool_results'].items():
                        self.stdout.write(f'  {tool_name}:')
                        self.stdout.write(f'    {json.dumps(tool_data, indent=4)[:200]}...')
            else:
                self.stdout.write(self.style.ERROR(f'\n❌ Agent execution failed: {result.get("error")}'))
            
        except UnifiedAgentTemplate.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'  Agent {agent_name} not found'))
            self.stdout.write('\n  Available sports agents:')
            
            sports_agents = UnifiedAgentTemplate.objects.filter(
                domain_tags__contains=['sports']
            )[:10]
            
            for agent in sports_agents:
                self.stdout.write(f'    • {agent.name}: {agent.display_name}')
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Test failed: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())
        
        self.stdout.write(self.style.SUCCESS('\n✨ Tool integration test complete!'))