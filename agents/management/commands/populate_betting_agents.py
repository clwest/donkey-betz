"""
Management command to populate sports betting agents in the database.
"""

from django.core.management.base import BaseCommand
from agents.models import UnifiedAgentTemplate
import json


class Command(BaseCommand):
    help = 'Populate sports betting agents in the database'

    def handle(self, *args, **options):
        self.stdout.write('Creating sports betting agents...')
        
        # Define all sports betting agents
        agents = [
            {
                'name': 'betting_intelligence_analyzer',
                'display_name': 'Betting Intelligence Analyzer',
                'description': 'Advanced betting intelligence with Kelly Criterion, market value analysis, and sentiment tracking',
                'specialization': 'sports_betting_intelligence',
                'capabilities': json.dumps([
                    {'name': 'kelly_criterion', 'description': 'Optimal bet sizing calculations'},
                    {'name': 'market_analysis', 'description': 'Line value and efficiency analysis'},
                    {'name': 'sentiment_tracking', 'description': 'Public vs sharp money analysis'}
                ]),
                'routing_keywords': json.dumps(['betting intelligence', 'kelly criterion', 'market sentiment', 'advanced analytics']),
                'llm_model': 'gpt-4'
            },
            {
                'name': 'market_value_analyzer',
                'display_name': 'Market Value Analyzer',
                'description': 'Line value assessment, market efficiency ratings, and implied probability analysis',
                'specialization': 'market_analysis',
                'capabilities': json.dumps([
                    {'name': 'line_value_assessment', 'description': 'Evaluate betting line value'},
                    {'name': 'market_efficiency', 'description': 'Rate market efficiency'},
                    {'name': 'implied_probability', 'description': 'Calculate true probabilities'}
                ]),
                'routing_keywords': json.dumps(['market value', 'line value', 'market efficiency', 'implied probability']),
                'llm_model': 'gpt-4'
            },
            {
                'name': 'public_sentiment_analyzer',
                'display_name': 'Public Sentiment Analyzer',
                'description': 'Public vs sharp money analysis, reverse line movement detection, and contrarian opportunities',
                'specialization': 'sentiment_analysis',
                'capabilities': json.dumps([
                    {'name': 'public_betting_analysis', 'description': 'Analyze public betting percentages'},
                    {'name': 'sharp_money_detection', 'description': 'Detect professional money movement'},
                    {'name': 'contrarian_opportunities', 'description': 'Find contrarian betting spots'}
                ]),
                'routing_keywords': json.dumps(['public sentiment', 'sharp money', 'contrarian', 'reverse line movement']),
                'llm_model': 'gpt-4',
            },
            {
                'name': 'situational_analyzer',
                'display_name': 'Situational Analyzer',
                'description': 'Advanced situational analysis including rest advantages, travel factors, and historical performance',
                'specialization': 'situational_analysis',
                'capabilities': json.dumps([
                    {'name': 'situational_factors', 'description': 'Analyze game situation factors'},
                    {'name': 'rest_advantage', 'description': 'Calculate rest differentials'},
                    {'name': 'historical_performance', 'description': 'Historical situational trends'}
                ]),
                'routing_keywords': json.dumps(['situational analysis', 'rest advantage', 'travel factors', 'situational edge']),
                'llm_model': 'gpt-4',
            },
            {
                'name': 'weather_analyzer',
                'display_name': 'Weather Analyzer',
                'description': 'Real-time weather analysis and impact assessment on game conditions and betting lines',
                'specialization': 'weather_analysis',
                'capabilities': json.dumps([
                    {'name': 'weather_impact', 'description': 'Assess weather impact on games'},
                    {'name': 'wind_analysis', 'description': 'Wind speed and direction analysis'},
                    {'name': 'precipitation_effects', 'description': 'Rain/snow impact on totals'}
                ]),
                'routing_keywords': json.dumps(['weather', 'conditions', 'wind', 'precipitation', 'weather impact']),
                'llm_model': 'gpt-3.5-turbo',
            },
            {
                'name': 'injury_analyzer',
                'display_name': 'Injury Analyzer',
                'description': 'Comprehensive injury intelligence with impact assessment and lineup analysis',
                'specialization': 'injury_analysis',
                'capabilities': json.dumps([
                    {'name': 'injury_impact', 'description': 'Assess injury impact on performance'},
                    {'name': 'replacement_analysis', 'description': 'Analyze backup player capabilities'},
                    {'name': 'injury_trends', 'description': 'Track injury patterns and recovery'}
                ]),
                'routing_keywords': json.dumps(['injuries', 'injury report', 'player health', 'injury intelligence']),
                'llm_model': 'gpt-4',
            },
            {
                'name': 'kelly_bet_sizing',
                'display_name': 'Kelly Bet Sizing Agent',
                'description': 'Optimal bet sizing using Kelly Criterion with risk management and bankroll optimization',
                'specialization': 'bet_sizing',
                'capabilities': json.dumps([
                    {'name': 'kelly_calculation', 'description': 'Calculate optimal bet sizes'},
                    {'name': 'risk_management', 'description': 'Assess and manage betting risk'},
                    {'name': 'bankroll_optimization', 'description': 'Optimize bankroll allocation'}
                ]),
                'routing_keywords': json.dumps(['kelly criterion', 'bet sizing', 'bankroll', 'risk management']),
                'llm_model': 'gpt-4',
            },
            {
                'name': 'odds_calculation',
                'display_name': 'Odds Calculation Agent',
                'description': 'Convert between odds formats, calculate implied probabilities, and identify value opportunities',
                'specialization': 'odds_calculation',
                'capabilities': json.dumps([
                    {'name': 'odds_conversion', 'description': 'Convert between odds formats'},
                    {'name': 'probability_calculation', 'description': 'Calculate implied probabilities'},
                    {'name': 'value_identification', 'description': 'Identify value betting opportunities'}
                ]),
                'routing_keywords': json.dumps(['odds', 'probability', 'value betting', 'odds conversion']),
                'llm_model': 'gpt-3.5-turbo',
            },
            {
                'name': 'line_movement_analyzer',
                'display_name': 'Line Movement Analyzer',
                'description': 'Track and analyze betting line movements, identify sharp action, and predict line direction',
                'specialization': 'line_movement',
                'capabilities': json.dumps([
                    {'name': 'line_tracking', 'description': 'Track betting line changes'},
                    {'name': 'sharp_detection', 'description': 'Detect professional money movement'},
                    {'name': 'movement_prediction', 'description': 'Predict future line movement'}
                ]),
                'routing_keywords': json.dumps(['line movement', 'line tracking', 'sharp action', 'line prediction']),
                'llm_model': 'gpt-4',
            },
            {
                'name': 'arbitrage_hunter',
                'display_name': 'Arbitrage Hunter',
                'description': 'Identify arbitrage opportunities across multiple sportsbooks with profit calculations',
                'specialization': 'arbitrage_betting',
                'capabilities': json.dumps([
                    {'name': 'arbitrage_detection', 'description': 'Find arbitrage opportunities'},
                    {'name': 'profit_calculation', 'description': 'Calculate guaranteed profits'},
                    {'name': 'sportsbook_comparison', 'description': 'Compare odds across books'}
                ]),
                'routing_keywords': json.dumps(['arbitrage', 'sure bet', 'guaranteed profit', 'sportsbook comparison']),
                'llm_model': 'gpt-4',
            },
            {
                'name': 'value_betting_agent',
                'display_name': 'Value Betting Agent',
                'description': 'Identify positive expected value bets with comprehensive edge analysis and confidence ratings',
                'specialization': 'value_betting',
                'capabilities': json.dumps([
                    {'name': 'value_identification', 'description': 'Find positive EV opportunities'},
                    {'name': 'edge_calculation', 'description': 'Calculate betting edges'},
                    {'name': 'confidence_rating', 'description': 'Rate bet confidence levels'}
                ]),
                'routing_keywords': json.dumps(['value betting', 'positive ev', 'betting edge', 'expected value']),
                'llm_model': 'gpt-4',
            },
            {
                'name': 'contrarian_betting',
                'display_name': 'Contrarian Betting Agent',
                'description': 'Fade-the-public strategies, identify contrarian opportunities, and reverse line movement analysis',
                'specialization': 'contrarian_betting',
                'capabilities': json.dumps([
                    {'name': 'fade_public', 'description': 'Identify fade-the-public spots'},
                    {'name': 'contrarian_analysis', 'description': 'Find contrarian opportunities'},
                    {'name': 'reverse_movement', 'description': 'Analyze reverse line movement'}
                ]),
                'routing_keywords': json.dumps(['contrarian', 'fade public', 'reverse line', 'contrarian betting']),
                'llm_model': 'gpt-4',
            }
        ]
        
        # Common fields for all agents (only valid fields from the model)
        common_fields = {
            'system_prompt': "You are an expert sports betting analyst. Provide detailed, data-driven analysis based on your specialization.",
            'llm_provider': 'openai',
            'is_public': True,
            'is_verified': True,
            'learning_enabled': True,
            'success_rate': 95.0,
            'usage_count': 0
        }
        
        # Create or update each agent
        created_count = 0
        updated_count = 0
        
        for agent_data in agents:
            # Merge with common fields
            full_agent_data = {**common_fields, **agent_data}
            
            # Create or update agent
            agent, created = UnifiedAgentTemplate.objects.update_or_create(
                name=full_agent_data['name'],
                defaults=full_agent_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created agent: {agent.display_name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Updated agent: {agent.display_name}'))
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully populated {created_count} new agents and updated {updated_count} existing agents!'
            )
        )