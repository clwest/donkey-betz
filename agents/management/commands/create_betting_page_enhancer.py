"""
Management command to create the specialized Betting Page Enhancer agent
"""

from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal

from core.models.agents_registry import UnifiedAgentTemplate, AgentRegistry, AgentSpecialization


class Command(BaseCommand):
    help = 'Create the specialized Betting Page Enhancer agent for transforming the sports betting interface'
    
    def handle(self, *args, **options):
        self.stdout.write("Creating Betting Page Enhancer agent...")
        
        agent_data = {
            'name': 'betting-page-enhancer',
            'display_name': 'Betting Page Enhancer',
            'description': """Expert agent specialized in transforming basic sports betting interfaces into world-class, 
professional-grade betting analysis platforms. This agent combines deep knowledge of sports betting mathematics, 
Kelly Criterion optimization, real-time data integration, and user experience design to create comprehensive 
betting tools that rival major sportsbooks.""",
            
            'specialization': AgentSpecialization.SPORTS_ANALYTICS,
            
            'capabilities': [
                # Core Betting Analysis
                'Advanced Kelly Criterion calculator with multiple betting strategies',
                'Real-time odds comparison across multiple sportsbooks',
                'Sophisticated bankroll management tools',
                'Expected value calculations and optimization',
                'Betting pattern analysis and trend identification',
                
                # Interactive Data Features
                'Interactive weather impact analysis with clickable forecasts',
                'Detailed injury report analysis with impact ratings',
                'Real-time line movement tracking and alerts',
                'Historical matchup analysis with trend visualization',
                'Live data feeds integration and processing',
                
                # UI/UX Enhancement
                'Gaming-themed UI component enhancement',
                'Real-time WebSocket data streaming',
                'Interactive dashboard widgets',
                'Mobile-responsive betting interface design',
                'Professional-grade data visualization',
                
                # Backend Integration
                'Sports API endpoint optimization',
                'Database schema enhancements for betting data',
                'WebSocket consumer implementation',
                'Caching strategies for real-time data',
                'API rate limiting and optimization',
                
                # Advanced Features
                'Multi-agent integration for collaborative analysis',
                'Smart notification systems for value betting',
                'Automated bet slip optimization',
                'Risk assessment and portfolio management',
                'Machine learning model integration for predictions'
            ],
            
            'required_tools': [
                'sports_api_integration',
                'react_typescript_development',
                'django_backend_development',
                'websocket_implementation',
                'database_optimization',
                'ui_component_library',
                'real_time_data_processing'
            ],
            
            'optional_tools': [
                'machine_learning_models',
                'advanced_visualization',
                'mobile_development',
                'third_party_odds_apis',
                'notification_systems',
                'caching_solutions'
            ],
            
            'system_prompt': '''You are the Betting Page Enhancer, an elite specialist in transforming basic sports betting interfaces into world-class, professional-grade betting analysis platforms.

## YOUR CORE EXPERTISE:

### Betting Mathematics & Analytics
- Advanced Kelly Criterion implementation with multiple strategies (full Kelly, fractional Kelly, multi-outcome Kelly)
- Expected value calculations, implied probability analysis, and edge detection
- Sophisticated bankroll management with risk assessment and portfolio optimization
- Real-time odds comparison with line movement tracking and arbitrage opportunities
- Historical trend analysis with predictive modeling and pattern recognition

### Interactive Data Integration
- Weather impact analysis with detailed forecasts, wind effects, and venue conditions
- Comprehensive injury reports with impact ratings, recovery timelines, and historical performance
- Real-time data feeds with WebSocket streaming and automatic updates
- Multi-sportsbook integration with odds aggregation and comparison tools
- Live statistics tracking with performance metrics and in-game analysis

### Technical Implementation
- React/TypeScript frontend development with gaming-themed UI components
- Django backend integration with optimized API endpoints and database schemas
- WebSocket implementation for real-time data streaming and user notifications
- Responsive design principles with mobile-first approach and cross-platform compatibility
- Performance optimization with caching strategies and efficient data handling

## YOUR APPROACH:

1. **Analysis Phase**: Examine the current GameBettingPage.tsx structure and identify enhancement opportunities
2. **Architecture Phase**: Design scalable solutions that integrate with existing tech stack
3. **Implementation Phase**: Create modular, maintainable code that follows best practices
4. **Enhancement Phase**: Add advanced features that provide professional-grade betting analysis
5. **Integration Phase**: Ensure seamless integration with existing agent system and APIs

## YOUR PERSONALITY:
- Highly analytical and detail-oriented
- Expert in sports betting mathematics and risk management
- Focused on creating professional, institutional-quality tools
- Committed to user experience and interface design excellence
- Pragmatic approach to feature implementation with scalability in mind

## YOUR OUTPUTS SHOULD INCLUDE:

### Code Enhancements
- Clean, documented TypeScript/React components
- Optimized Django backend endpoints
- Real-time WebSocket consumers
- Database migrations and schema improvements
- Comprehensive test suites

### Feature Specifications
- Detailed technical specifications for new features
- User interaction flow diagrams
- Data flow architecture documentation
- Performance benchmarks and optimization strategies

### Integration Guidelines
- Step-by-step implementation instructions
- Compatibility considerations with existing codebase
- Migration strategies for data and user preferences
- Testing procedures and quality assurance protocols

Always prioritize code quality, user experience, and professional-grade functionality. Your enhancements should transform the betting page from a basic interface into a comprehensive platform that rivals major sportsbooks in terms of functionality and user experience.''',
            
            'personality_traits': {
                'style': 'analytical',
                'tone': 'professional',
                'detail_level': 'comprehensive',
                'approach': 'systematic',
                'focus': 'results-oriented',
                'expertise_level': 'expert',
                'problem_solving': 'methodical',
                'communication': 'technical_precise'
            },
            
            'llm_provider': 'anthropic',
            'llm_model': 'claude-3-5-sonnet-20241022',
            'llm_config': {
                'temperature': 0.1,  # Low temperature for precise, consistent technical output
                'max_tokens': 4096,
                'top_p': 0.9,
                'frequency_penalty': 0.0,
                'presence_penalty': 0.0
            },
            
            'fallback_provider': 'openai',
            'fallback_model': 'gpt-5-mini',
            
            'routing_keywords': [
                # Betting & Sports
                'betting', 'sportsbook', 'odds', 'kelly criterion', 'bankroll management',
                'sports betting', 'gambling', 'wager', 'stake', 'line movement',
                'implied probability', 'expected value', 'arbitrage', 'sharp betting',
                
                # Technical Implementation
                'GameBettingPage', 'betting interface', 'betting page', 'sports page',
                'react component', 'typescript', 'django backend', 'websocket',
                'real-time data', 'API integration', 'database optimization',
                
                # UI/UX Enhancement
                'ui enhancement', 'user interface', 'user experience', 'responsive design',
                'gaming theme', 'interactive', 'dashboard', 'visualization',
                'mobile betting', 'betting tools',
                
                # Data & Analytics
                'weather data', 'injury reports', 'team statistics', 'trends analysis',
                'odds comparison', 'betting analytics', 'performance metrics',
                'data visualization', 'real-time updates'
            ],
            
            'routing_patterns': [
                r'betting.*page.*enhance',
                r'sports.*betting.*interface',
                r'GameBettingPage.*improve',
                r'kelly.*criterion.*calculator',
                r'odds.*comparison.*tool',
                r'bankroll.*management.*system',
                r'real.*time.*betting.*data',
                r'sportsbook.*integration',
                r'betting.*analytics.*platform'
            ],
            
            'domain_tags': [
                'sports',
                'betting',
                'analytics', 
                'ui-enhancement',
                'real-time-data',
                'react-typescript',
                'django-backend',
                'websockets',
                'gambling',
                'fintech'
            ],
            
            'confidence_score': 0.95,
            'avg_completion_time': 900,  # 15 minutes for comprehensive enhancements
            'success_rate': 0.92,
            'estimated_cost_per_execution': Decimal('0.250000'),  # Higher cost for complex analysis
            
            'avg_token_usage': {
                'input_tokens': 3500,
                'output_tokens': 2800,
                'total_tokens': 6300
            },
            
            'resource_requirements': {
                'cpu': 'medium',
                'memory': '2GB',
                'disk': '500MB',
                'network': 'high',  # For real-time data integration
                'concurrent_executions': 2
            },
            
            'agent_version': '1.0.0',
            'is_template': True,
            'is_public': True,
            'is_verified': True,
            
            'supports_streaming': True,
            'supports_interruption': True,
            'supports_collaboration': True,
            'max_concurrent_executions': 2,
            
            'learning_enabled': True,
            'self_improvement_enabled': True,
            
            'collaboration_history': [
                'sports-analytics-agent',
                'odds-calculation-agent', 
                'ui-designer-agent',
                'backend-optimization-agent',
                'real-time-data-agent'
            ]
        }
        
        with transaction.atomic():
            try:
                # Create or update the agent
                agent, created = UnifiedAgentTemplate.objects.update_or_create(
                    name=agent_data['name'],
                    defaults=agent_data
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Created new agent: {agent.display_name}")
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f"🔄 Updated existing agent: {agent.display_name}")
                    )
                
                # Update agent registry
                registry, registry_created = AgentRegistry.objects.get_or_create(
                    registry_name='unified_agent_registry'
                )
                registry.rebuild_indexes()
                
                self.stdout.write(
                    self.style.SUCCESS(f"📊 Agent registry updated: {registry.total_agents} total agents")
                )
                
                # Print agent summary
                self.stdout.write("\n" + "="*80)
                self.stdout.write("🎯 BETTING PAGE ENHANCER AGENT SUMMARY")
                self.stdout.write("="*80)
                self.stdout.write(f"Name: {agent.name}")
                self.stdout.write(f"Display Name: {agent.display_name}")
                self.stdout.write(f"Specialization: {agent.get_specialization_display()}")
                self.stdout.write(f"Capabilities: {len(agent.capabilities)} total")
                self.stdout.write(f"Routing Keywords: {len(agent.routing_keywords)} keywords")
                self.stdout.write(f"Domain Tags: {', '.join(agent.domain_tags)}")
                self.stdout.write(f"Confidence Score: {agent.confidence_score}")
                self.stdout.write(f"LLM: {agent.llm_provider} - {agent.llm_model}")
                self.stdout.write(f"Supports: Streaming={agent.supports_streaming}, Collaboration={agent.supports_collaboration}")
                
                self.stdout.write("\n📋 KEY CAPABILITIES:")
                for i, capability in enumerate(agent.capabilities[:10], 1):
                    self.stdout.write(f"  {i}. {capability}")
                if len(agent.capabilities) > 10:
                    self.stdout.write(f"  ... and {len(agent.capabilities) - 10} more")
                    
                self.stdout.write("\n🔍 ROUTING KEYWORDS (sample):")
                for keyword in agent.routing_keywords[:12]:
                    self.stdout.write(f"  • {keyword}")
                    
                self.stdout.write("\n" + "="*80)
                self.stdout.write("🚀 Agent is ready for deployment!")
                self.stdout.write("="*80)
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Failed to create agent: {str(e)}")
                )
                raise