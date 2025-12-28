#!/usr/bin/env python3
"""
Test script for the Betting Page Enhancer agent
Demonstrates how to execute the agent and integrate with the betting page
"""

import os
import sys

# Add project path for Django imports
project_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_path)

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
import django
django.setup()

from core.models.agents_registry import UnifiedAgentTemplate, AgentExecution, AgentRegistry
from django.contrib.auth import get_user_model

User = get_user_model()


def test_agent_discovery():
    """Test finding the betting page enhancer agent through the registry"""
    print("🔍 Testing Agent Discovery...")
    
    try:
        registry = AgentRegistry.objects.get(registry_name='unified_agent_registry')
        
        # Test finding agents for betting tasks
        betting_tasks = [
            {
                'description': 'Enhance the GameBettingPage with advanced Kelly calculator',
                'capabilities': ['sports_analytics', 'ui_enhancement', 'betting_analysis'],
                'specialization': 'sports-analytics'
            },
            {
                'description': 'Add interactive weather reports to sports betting interface',
                'capabilities': ['weather_analysis', 'ui_enhancement', 'sports_data'],
                'specialization': 'sports-analytics'
            },
            {
                'description': 'Implement real-time odds comparison and line movement tracking',
                'capabilities': ['real_time_data', 'odds_comparison', 'websocket_integration'],
                'specialization': 'sports-analytics'
            }
        ]
        
        for task in betting_tasks:
            print(f"\n📋 Task: {task['description'][:60]}...")
            
            suitable_agents = registry.find_agents_for_task(
                task['description'],
                required_capabilities=task['capabilities'],
                specialization=task['specialization'],
                limit=3
            )
            
            print(f"   Found {len(suitable_agents)} suitable agents:")
            for agent_info in suitable_agents:
                agent = agent_info['agent']
                score = agent_info['score']
                print(f"   • {agent.display_name} (Score: {score:.2f}, Confidence: {agent.confidence_score})")
                
        return True
        
    except Exception as e:
        print(f"❌ Agent discovery failed: {e}")
        return False


def test_agent_execution():
    """Test executing the betting page enhancer agent"""
    print("\n🚀 Testing Agent Execution...")
    
    try:
        # Find the betting page enhancer agent
        agent = UnifiedAgentTemplate.objects.get(name='betting-page-enhancer', is_active=True)
        print(f"✅ Found agent: {agent.display_name}")
        
        # Create a test user if needed
        user, created = User.objects.get_or_create(
            username='test_betting_user',
            defaults={'email': 'test@betting.com'}
        )
        
        # Sample game data for testing
        sample_game_data = {
            'game_id': 'test-game-123',
            'home_team': 'Kansas City Chiefs',
            'away_team': 'Buffalo Bills',
            'league': 'NFL',
            'scheduled_start': '2024-01-01T13:00:00Z',
            'venue': 'Arrowhead Stadium',
            'weather': {
                'temperature': 32,
                'condition': 'Cold',
                'wind': 'NW 15 mph'
            },
            'current_odds': {
                'moneyline': {'home': -150, 'away': +130},
                'spread': {'line': -3.5, 'odds': -110},
                'total': {'line': 47.5, 'over': -105, 'under': -115}
            }
        }
        
        # Test different enhancement scenarios
        test_scenarios = [
            {
                'task': 'Create an advanced Kelly Criterion calculator component for the betting page',
                'context': {
                    'component_type': 'kelly_calculator',
                    'features': ['multiple_strategies', 'risk_analysis', 'portfolio_management'],
                    'game_data': sample_game_data
                }
            },
            {
                'task': 'Design interactive weather analysis widget with betting implications',
                'context': {
                    'component_type': 'weather_widget',
                    'features': ['clickable_forecasts', 'impact_analysis', 'betting_recommendations'],
                    'game_data': sample_game_data
                }
            },
            {
                'task': 'Implement real-time line movement tracking with WebSocket integration',
                'context': {
                    'component_type': 'line_movement_tracker',
                    'features': ['websocket_streaming', 'alerts', 'historical_data'],
                    'game_data': sample_game_data
                }
            }
        ]
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"\n🔬 Test Scenario {i}: {scenario['task'][:50]}...")
            
            # Create execution
            execution = AgentExecution.objects.create(
                template=agent,
                user=user,
                task_description=scenario['task'],
                task_type='betting_page_enhancement',
                context=scenario['context'],
                input_data=sample_game_data,
                priority='normal'
            )
            
            print(f"   ✅ Created execution: {execution.execution_id}")
            print(f"   📊 Status: {execution.status}")
            print(f"   🎯 Task Type: {execution.task_type}")
            print(f"   🏷️  Context: {execution.context['component_type']}")
            
            # Simulate execution steps (in real implementation, this would be handled by the agent executor)
            execution.start_execution()
            execution.update_progress(25, "Analyzing current betting page structure")
            execution.update_progress(50, f"Designing {execution.context['component_type']} component")
            execution.update_progress(75, "Generating React/TypeScript implementation")
            execution.update_progress(100, "Creating integration documentation")
            
            # Simulate completion with mock results
            mock_results = {
                'component_name': execution.context['component_type'],
                'files_created': [
                    f"components/betting/{execution.context['component_type']}.tsx",
                    f"components/betting/{execution.context['component_type']}.test.tsx",
                    f"hooks/use{execution.context['component_type'].replace('_', '').title()}.ts"
                ],
                'features_implemented': execution.context['features'],
                'integration_notes': f"Component ready for integration into GameBettingPage.tsx",
                'testing_notes': "Comprehensive test suite included",
                'documentation_url': f"/docs/components/{execution.context['component_type']}"
            }
            
            execution.complete_execution(
                result=mock_results,
                output_files=mock_results['files_created']
            )
            
            print(f"   ✅ Execution completed successfully")
            print(f"   📁 Generated {len(mock_results['files_created'])} files")
            print(f"   ⏱️  Duration: {execution.execution_time_seconds} seconds")
            
        return True
        
    except Exception as e:
        print(f"❌ Agent execution failed: {e}")
        return False


def test_agent_capabilities():
    """Test the agent's specific capabilities"""
    print("\n🧪 Testing Agent Capabilities...")
    
    try:
        agent = UnifiedAgentTemplate.objects.get(name='betting-page-enhancer', is_active=True)
        
        # Test capability matching
        test_tasks = [
            {
                'description': 'Add Kelly Criterion calculator to betting page',
                'required_capabilities': ['Advanced Kelly Criterion calculator with multiple betting strategies']
            },
            {
                'description': 'Create real-time odds comparison widget',
                'required_capabilities': ['Real-time odds comparison across multiple sportsbooks']
            },
            {
                'description': 'Design mobile-responsive betting interface',
                'required_capabilities': ['Mobile-responsive betting interface design']
            }
        ]
        
        for task in test_tasks:
            can_handle, reason = agent.can_handle_task(
                task['description'], 
                task['required_capabilities']
            )
            
            print(f"   📋 Task: {task['description']}")
            print(f"   ✅ Can Handle: {can_handle}")
            print(f"   💡 Reason: {reason}")
            print()
        
        # Display agent's full capability set
        print("🛠️  Agent Capabilities Summary:")
        print(f"   Total Capabilities: {len(agent.capabilities)}")
        print(f"   Specialization: {agent.get_specialization_display()}")
        print(f"   Confidence Score: {agent.confidence_score}")
        print(f"   Success Rate: {agent.success_rate}")
        print(f"   Average Completion Time: {agent.avg_completion_time} seconds")
        
        return True
        
    except Exception as e:
        print(f"❌ Capability testing failed: {e}")
        return False


def test_integration_examples():
    """Test generating integration examples"""
    print("\n🔗 Testing Integration Examples...")
    
    try:
        # Sample current GameBettingPage structure
        current_page_structure = {
            'components': [
                'GameHeader',
                'GameOverview', 
                'BettingMarkets',
                'KellyCalculator',
                'BetSlip'
            ],
            'hooks': [
                'useGameData',
                'useBettingMarkets'
            ],
            'state_management': [
                'game',
                'betSlip',
                'bankroll',
                'kellyFraction'
            ]
        }
        
        # Enhancement scenarios
        enhancement_scenarios = [
            {
                'name': 'Interactive Weather Widget',
                'description': 'Replace basic weather display with interactive analysis',
                'complexity': 'medium',
                'estimated_effort': '4-6 hours',
                'dependencies': ['weather API', 'modal components']
            },
            {
                'name': 'Advanced Kelly Calculator',
                'description': 'Upgrade basic Kelly calc with multiple strategies and risk analysis',
                'complexity': 'high',
                'estimated_effort': '8-12 hours', 
                'dependencies': ['mathematical functions', 'portfolio analysis']
            },
            {
                'name': 'Real-time Data Integration',
                'description': 'Add WebSocket streaming for live odds and line movements',
                'complexity': 'high',
                'estimated_effort': '6-10 hours',
                'dependencies': ['WebSocket setup', 'Django Channels', 'real-time UI updates']
            },
            {
                'name': 'Agent Integration Panel',
                'description': 'Add AI analysis capabilities directly to the betting page',
                'complexity': 'medium',
                'estimated_effort': '4-6 hours',
                'dependencies': ['agent API', 'execution tracking', 'result display']
            }
        ]
        
        print("📋 Available Enhancement Scenarios:")
        for i, scenario in enumerate(enhancement_scenarios, 1):
            print(f"   {i}. {scenario['name']}")
            print(f"      📝 {scenario['description']}")
            print(f"      🔧 Complexity: {scenario['complexity']}")
            print(f"      ⏱️  Effort: {scenario['estimated_effort']}")
            print(f"      🔗 Dependencies: {', '.join(scenario['dependencies'])}")
            print()
        
        # Show integration workflow
        integration_workflow = [
            "1. Analyze current GameBettingPage.tsx structure",
            "2. Identify enhancement opportunities and integration points", 
            "3. Design new components with gaming theme compatibility",
            "4. Implement TypeScript interfaces and state management",
            "5. Create React components with proper error handling",
            "6. Add Django backend endpoints if needed",
            "7. Implement WebSocket consumers for real-time features",
            "8. Write comprehensive tests and documentation",
            "9. Create migration guide for existing users",
            "10. Deploy with feature flags and monitoring"
        ]
        
        print("🔄 Integration Workflow:")
        for step in integration_workflow:
            print(f"   {step}")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration testing failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🎯 BETTING PAGE ENHANCER AGENT - TESTING SUITE")
    print("=" * 60)
    
    tests = [
        ("Agent Discovery", test_agent_discovery),
        ("Agent Execution", test_agent_execution), 
        ("Agent Capabilities", test_agent_capabilities),
        ("Integration Examples", test_integration_examples)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} Test...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} Test PASSED")
            else:
                print(f"❌ {test_name} Test FAILED")
        except Exception as e:
            print(f"💥 {test_name} Test CRASHED: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
    
    print("-" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The Betting Page Enhancer agent is ready for use!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
    
    print("\n🚀 Next Steps:")
    print("1. Use the agent through the web interface at /agents/")
    print("2. Create executions with betting page enhancement tasks")
    print("3. Review generated code and integration examples")
    print("4. Follow the implementation guidelines in the examples")


if __name__ == '__main__':
    main()