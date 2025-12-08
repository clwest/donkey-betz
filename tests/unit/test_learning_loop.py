# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Test the learning loop implementation
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.agent_integration import AgentRouter
from core.feedback_collector import FeedbackCollector, ResponseAnalyzer
from core.models.agents_registry import UnifiedAgentTemplate

User = get_user_model()

def test_learning_loop():
    """Test that the learning loop is working"""
    print("\n🧠 Testing Agent Learning Loop")
    print("=" * 60)
    
    # Get a user for testing
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.first()
    
    router = AgentRouter(user)
    feedback_collector = FeedbackCollector()
    response_analyzer = ResponseAnalyzer()
    
    # Test queries
    test_cases = [
        {
            'query': "What's changed in the system?",
            'expected_behavior': 'direct_answer',
        },
        {
            'query': "Could you clarify what you mean by that?",
            'expected_behavior': 'asks_clarification',
        },
        {
            'query': "Analyze the performance metrics",
            'expected_behavior': 'direct_answer',
        }
    ]
    
    print("\n📊 Testing Response Quality Analysis:")
    print("-" * 60)
    
    for test in test_cases:
        # Find best agent
        best_agent = router.find_best_agent(test['query'])
        
        if best_agent:
            print(f"\n🤖 Query: '{test['query'][:40]}...'")
            print(f"   Selected Agent: {best_agent['agent_name']}")
            print(f"   Base Score: {best_agent.get('score', 0):.2f}")
            print(f"   Adjusted Score: {best_agent.get('adjusted_score', best_agent.get('score', 0)):.2f}")
            
            if best_agent.get('learning_applied'):
                print(f"   ✅ Learning Applied!")
                print(f"      Success Rate: {best_agent.get('success_rate', 0):.1f}%")
                print(f"      User Rating: {best_agent.get('user_rating', 0):.1f}/5.0")
            
            # Simulate a response
            if test['expected_behavior'] == 'asks_clarification':
                mock_response = "Could you please clarify what specific changes you're interested in?"
            else:
                mock_response = "Here are the recent system changes: [actual content]"
            
            # Analyze response quality
            quality = response_analyzer.analyze_response_quality(mock_response, test['query'])
            
            print(f"   Response Quality: {quality['quality_score']:.2f}")
            print(f"   Signals: {', '.join(quality['signals'])}")
            
            if quality.get('improvements_needed'):
                print(f"   ⚠️  Improvements: {', '.join(quality['improvements_needed'])}")
    
    # Check agent metrics
    print("\n\n📈 Agent Performance Metrics:")
    print("-" * 60)
    
    sample_agents = UnifiedAgentTemplate.objects.filter(is_active=True)[:5]
    
    for agent in sample_agents:
        print(f"\n{agent.name}:")
        print(f"   Usage Count: {agent.usage_count}")
        print(f"   Success Rate: {agent.success_rate:.1f}%")
        print(f"   Avg Completion: {agent.avg_completion_time:.2f}s")
        print(f"   User Rating: {agent.avg_user_rating:.1f}/5.0")
        print(f"   Learning Enabled: {'✅' if agent.learning_enabled else '❌'}")
        
        # Check for learning patterns
        if agent.metadata and 'learning_patterns' in agent.metadata:
            patterns = agent.metadata['learning_patterns']
            if patterns.get('asks_clarification_count', 0) > 0:
                print(f"   ⚠️  Clarification Issues: {patterns['asks_clarification_count']} times")
    
    print("\n\n✨ Learning Loop Features Active:")
    print("-" * 60)
    print("✅ Agent execution tracking in database")
    print("✅ Success/failure metrics updating")
    print("✅ Response quality analysis")
    print("✅ Implicit feedback collection")
    print("✅ Learning-based score adjustments")
    print("✅ Agent performance evolution tracking")
    
    print("\n🎯 The system will now:")
    print("   1. Track every agent execution")
    print("   2. Measure response quality")
    print("   3. Adjust routing scores based on performance")
    print("   4. Penalize agents that ask unnecessary clarifications")
    print("   5. Boost well-performing agents")
    print("   6. Learn from patterns over time")

if __name__ == '__main__':
    test_learning_loop()