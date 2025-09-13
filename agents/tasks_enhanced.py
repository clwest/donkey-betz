"""
Enhanced Agent Execution with Tool Integration

This module provides enhanced agent execution that integrates tools
for data access and computation.
"""

import json
import logging
import traceback
from typing import Dict, Any, List, Optional
from datetime import datetime

from celery import shared_task
from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import UnifiedAgentTemplate, AgentExecution, AgentStatus
from content.ai_providers import AIProviderManager
from core.tools import ToolRegistry

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


def execute_tool(tool_name: str, **kwargs) -> Dict[str, Any]:
    """Execute a tool and return its results"""
    try:
        tool = ToolRegistry.get_tool(tool_name)
        if not tool:
            return {
                'success': False,
                'error': f'Tool {tool_name} not found',
                'data': None
            }
        
        result = tool.execute(**kwargs)
        return {
            'success': True,
            'tool': tool_name,
            'data': result
        }
        
    except Exception as e:
        logger.error(f"Tool execution error for {tool_name}: {e}")
        return {
            'success': False,
            'error': str(e),
            'data': None
        }


def prepare_tools_context(required_tools: List[str], input_data: Dict) -> Dict[str, Any]:
    """Prepare tool execution context based on agent requirements"""
    tools_context = {}
    
    for tool_name in required_tools:
        if tool_name == 'odds_data_access':
            # Fetch odds data if game context is provided
            if 'game_id' in input_data or 'sport' in input_data:
                result = execute_tool(
                    'odds_data_access',
                    sport=input_data.get('sport', 'americanfootball_nfl'),
                    game_id=input_data.get('game_id')
                )
                tools_context['odds_data'] = result['data'] if result['success'] else {}
        
        elif tool_name == 'game_data':
            # Fetch game information
            if 'game_id' in input_data or 'team' in input_data:
                result = execute_tool(
                    'game_data',
                    operation='get_games',
                    sport=input_data.get('sport', 'nfl')
                )
                tools_context['game_data'] = result['data'] if result['success'] else {}
        
        elif tool_name == 'mathematical_calculations':
            # Make calculator available
            tools_context['calculator'] = {
                'available_operations': [
                    'implied_probability',
                    'expected_value',
                    'roi_calculation',
                    'parlay_odds',
                    'hedge_calculation'
                ]
            }
        
        elif tool_name == 'kelly_criterion':
            # Prepare Kelly context
            if 'bankroll' in input_data:
                tools_context['kelly_context'] = {
                    'bankroll': input_data['bankroll'],
                    'kelly_fraction': input_data.get('kelly_fraction', 0.25)
                }
        
        elif tool_name == 'line_movement':
            # Fetch line movement data
            if 'game_id' in input_data:
                result = execute_tool(
                    'line_movement',
                    game_id=input_data['game_id'],
                    market_type=input_data.get('market_type', 'spread')
                )
                tools_context['line_movements'] = result['data'] if result['success'] else {}
        
        elif tool_name == 'arbitrage_detection':
            # Run arbitrage scan
            result = execute_tool(
                'arbitrage_detection',
                sport=input_data.get('sport', 'nfl'),
                min_profit=input_data.get('min_arb_profit', 1.0)
            )
            tools_context['arbitrage_opportunities'] = result['data'] if result['success'] else {}
    
    return tools_context


def format_tools_for_prompt(tools_context: Dict) -> str:
    """Format tools context for inclusion in prompt"""
    formatted = []
    
    if 'odds_data' in tools_context and tools_context['odds_data'].get('success'):
        formatted.append("=== CURRENT ODDS DATA ===")
        odds = tools_context['odds_data']
        if odds.get('live_odds'):
            formatted.append(f"Live Odds: {json.dumps(odds['live_odds'][:3], indent=2)}")
        if odds.get('cached_odds'):
            formatted.append(f"Historical Odds: {json.dumps(odds['cached_odds'][:3], indent=2)}")
    
    if 'game_data' in tools_context and tools_context['game_data'].get('success'):
        formatted.append("\n=== GAME INFORMATION ===")
        games = tools_context['game_data']
        if games.get('db_games'):
            formatted.append(f"Upcoming Games: {json.dumps(games['db_games'][:5], indent=2)}")
    
    if 'line_movements' in tools_context and tools_context['line_movements'].get('success'):
        formatted.append("\n=== LINE MOVEMENT ANALYSIS ===")
        movements = tools_context['line_movements']
        if movements.get('analysis'):
            formatted.append(f"Movement Analysis: {json.dumps(movements['analysis'], indent=2)}")
    
    if 'arbitrage_opportunities' in tools_context:
        formatted.append("\n=== ARBITRAGE SCAN ===")
        arbs = tools_context['arbitrage_opportunities']
        if arbs.get('opportunities'):
            formatted.append(f"Found {len(arbs['opportunities'])} arbitrage opportunities")
            formatted.append(json.dumps(arbs['opportunities'][:3], indent=2))
    
    if 'kelly_context' in tools_context:
        formatted.append("\n=== KELLY CRITERION CONTEXT ===")
        formatted.append(f"Bankroll: ${tools_context['kelly_context']['bankroll']}")
        formatted.append(f"Kelly Fraction: {tools_context['kelly_context']['kelly_fraction']}")
    
    return "\n".join(formatted) if formatted else "No tool data available"


@shared_task(bind=True, max_retries=3)
def execute_agent_with_tools(self, execution_id: str):
    """
    Enhanced agent execution with integrated tool support
    """
    try:
        # Get the execution instance
        execution = AgentExecution.objects.get(execution_id=execution_id)
        agent_template = execution.template
        
        logger.info(f"Starting enhanced execution for {execution_id} with agent {agent_template.name}")
        
        # Update status
        execution.status = AgentStatus.RUNNING
        execution.started_at = timezone.now()
        execution.save()
        
        # Prepare tools context based on agent requirements
        tools_context = prepare_tools_context(
            agent_template.required_tools,
            execution.input_data
        )
        
        # Execute tool calculations if needed
        tool_results = {}
        
        # Example: Kelly Criterion calculation
        if 'kelly_criterion' in agent_template.required_tools:
            if 'bet_analysis' in execution.input_data:
                bet = execution.input_data['bet_analysis']
                kelly_result = execute_tool(
                    'kelly_criterion',
                    probability=bet.get('win_probability', 0.5),
                    odds=bet.get('odds', 100),
                    bankroll=bet.get('bankroll', 1000),
                    kelly_fraction=bet.get('kelly_fraction', 0.25)
                )
                tool_results['kelly_calculation'] = kelly_result['data']
        
        # Example: Mathematical calculations
        if 'mathematical_calculations' in agent_template.required_tools:
            if 'odds_to_analyze' in execution.input_data:
                odds = execution.input_data['odds_to_analyze']
                
                # Calculate implied probability
                prob_result = execute_tool(
                    'mathematical_calculations',
                    operation='implied_probability',
                    odds=odds
                )
                tool_results['implied_probability'] = prob_result['data']
                
                # Calculate expected value if probability provided
                if 'win_probability' in execution.input_data:
                    ev_result = execute_tool(
                        'mathematical_calculations',
                        operation='expected_value',
                        odds=odds,
                        probability=execution.input_data['win_probability'],
                        stake=execution.input_data.get('stake', 100)
                    )
                    tool_results['expected_value'] = ev_result['data']
        
        # Initialize AI provider
        ai_manager = AIProviderManager()
        provider = ai_manager.get_provider(agent_template.llm_provider)
        
        if not provider:
            raise ValueError(f"AI provider {agent_template.llm_provider} not configured")
        
        # Build enhanced prompt with tool data
        tools_data_formatted = format_tools_for_prompt(tools_context)
        
        system_prompt = f"""
{agent_template.system_prompt}

You have access to the following tools and their data:
- Required Tools: {', '.join(agent_template.required_tools)}
- Optional Tools: {', '.join(agent_template.optional_tools)}

Use the provided data to give accurate, data-driven analysis.
"""
        
        user_prompt = f"""
Task: {execution.task_description}

Input Data:
{json.dumps(execution.input_data, indent=2)}

Tool Data Available:
{tools_data_formatted}

Tool Calculations:
{json.dumps(tool_results, indent=2) if tool_results else 'None performed yet'}

Context:
{json.dumps(execution.context, indent=2)}

Please complete this task using the provided data and your specialized capabilities.
Provide specific, actionable insights based on the real data available.
"""
        
        # Execute AI call with enhanced context
        result = provider.generate_content(
            model=agent_template.llm_model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            config=agent_template.llm_config
        )
        
        if not result.success:
            raise ValueError(f"Generation failed: {result.error_message}")
        
        # Store results with tool context
        execution.status = AgentStatus.COMPLETED
        execution.completed_at = timezone.now()
        execution.result = {
            'output': result.content,
            'success': True,
            'tools_used': list(tool_results.keys()),
            'tool_results': tool_results
        }
        execution.output_data = {
            'response': result.content,
            'tools_context': tools_context,
            'tool_calculations': tool_results
        }
        execution.save()
        
        logger.info(f"Enhanced execution {execution_id} completed with {len(tool_results)} tool calculations")
        
        return execution.result
        
    except Exception as e:
        logger.error(f"Enhanced execution failed for {execution_id}: {e}\n{traceback.format_exc()}")
        
        try:
            execution = AgentExecution.objects.get(execution_id=execution_id)
            execution.status = AgentStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = timezone.now()
            execution.save()
        except:
            pass
        
        raise


def execute_sports_agent_orchestration(game_id: str, agent_ids: List[str], context: Dict) -> Dict:
    """
    Execute multiple sports agents with shared tool context for comprehensive analysis
    """
    try:
        # Load game data once for all agents
        game_data_result = execute_tool(
            'game_data',
            operation='get_games',
            sport=context.get('sport', 'nfl')
        )
        
        odds_data_result = execute_tool(
            'odds_data_access',
            sport=context.get('sport', 'americanfootball_nfl'),
            game_id=game_id
        )
        
        # Shared tools context for all agents
        shared_context = {
            'game_data': game_data_result['data'] if game_data_result['success'] else {},
            'odds_data': odds_data_result['data'] if odds_data_result['success'] else {},
            'game_id': game_id,
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Execute each agent with shared context
        results = {}
        for agent_id in agent_ids:
            try:
                agent = UnifiedAgentTemplate.objects.get(name=agent_id)
                
                # Create execution
                execution = AgentExecution.objects.create(
                    template=agent,
                    execution_id=f"{agent_id}_{game_id}_{datetime.now().timestamp()}",
                    task_description=f"Analyze game {game_id} from {agent.specialization} perspective",
                    input_data={
                        'game_id': game_id,
                        **context
                    },
                    context=shared_context
                )
                
                # Execute with tools
                result = execute_agent_with_tools(execution.execution_id)
                results[agent_id] = result
                
            except Exception as e:
                logger.error(f"Failed to execute agent {agent_id}: {e}")
                results[agent_id] = {'success': False, 'error': str(e)}
        
        return {
            'success': True,
            'game_id': game_id,
            'agents_executed': len(results),
            'results': results,
            'shared_context': shared_context
        }
        
    except Exception as e:
        logger.error(f"Orchestration failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }