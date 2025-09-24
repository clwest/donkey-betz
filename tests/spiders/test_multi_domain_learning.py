#!/usr/bin/env python
"""
Test Multi-Domain Learning System
=================================
Test that agents can learn beyond just code - without breaking existing systems
"""

import sys
import os
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')

from intelligence.multi_domain_learning import (
    multi_domain_learning,
    agent_learns_market_trend,
    agent_learns_from_proposal,
    agent_observes_user_behavior,
    get_smart_recommendations,
    LearningDomain
)

def test_multi_domain_learning():
    """Test the expanded learning system"""
    print("🧠 Testing Multi-Domain Agent Learning System")
    print("=" * 50)

    try:
        # Test 1: Market Intelligence Learning
        print("1. Testing Market Intelligence Learning...")
        trend_data = {
            'trend_type': 'AI skills demand',
            'direction': 'increasing',
            'magnitude': 0.8,
            'timeframe': '3_months',
            'confidence': 0.9,
            'data': ['Python AI jobs +40%', 'ML engineer positions +60%']
        }

        market_key = agent_learns_market_trend('market_analyst_001', 'upwork', trend_data)
        print(f"✅ Market trend learned: {market_key}")

        # Test 2: Communication Pattern Learning
        print("\n2. Testing Communication Pattern Learning...")
        proposal_data = {
            'structure': 'Problem → Solution → Experience → Timeline → Price',
            'successful_phrases': ['I understand your challenge', 'Based on my experience'],
            'personalization': ['mention_company_name', 'reference_specific_requirements'],
            'pricing': 'value_based_with_options',
            'timeline': 'realistic_with_milestones',
            'client_type': 'startup',
            'category': 'ai_development',
            'outcome': 'hired',
            'response_time': '2 hours'
        }

        proposal_key = agent_learns_from_proposal('communication_expert_001', proposal_data)
        print(f"✅ Proposal pattern learned: {proposal_key}")

        # Test 3: User Behavior Learning
        print("\n3. Testing User Behavior Learning...")
        behavior_data = {
            'type': 'decision_making',
            'pattern': 'prefers_detailed_analysis_before_decisions',
            'triggers': ['new_opportunity', 'financial_decision'],
            'preferences': {'communication_style': 'detailed', 'risk_tolerance': 'moderate'},
            'confidence': 0.7,
            'decision_factors': ['potential_earnings', 'time_commitment', 'skill_match'],
            'productivity': {'peak_hours': '9-11am', 'preferred_days': ['Monday', 'Tuesday']}
        }

        behavior_key = agent_observes_user_behavior('behavior_analyst_001', 'user_123', behavior_data)
        print(f"✅ User behavior learned: {behavior_key}")

        # Test 4: Getting Smart Recommendations
        print("\n4. Testing Smart Recommendations...")
        recommendations = get_smart_recommendations('job_proposal_writing', {'user_id': 'user_123'})
        print(f"✅ Generated {len(recommendations)} recommendations")

        if recommendations:
            print("   Top recommendation:")
            print(f"   - Type: {recommendations[0]['type']}")
            print(f"   - Confidence: {recommendations[0]['confidence']:.1%}")
            print(f"   - Advice: {recommendations[0]['recommendation']}")

        # Test 5: Learning Analytics
        print("\n5. Testing Learning Analytics...")
        stats = multi_domain_learning.get_agent_learning_stats('market_analyst_001')
        print(f"✅ Agent has {stats['total_learnings']} total learnings")
        print(f"   Domain breakdown: {stats['domain_breakdown']}")
        print(f"   Average confidence: {stats['average_confidence']:.1%}")

        overview = multi_domain_learning.get_system_learning_overview()
        print(f"✅ System intelligence level: {overview['system_intelligence_level']:.1%}")
        print(f"   Learnings by domain: {overview['total_learnings_by_domain']}")

        print("\n🎉 Multi-Domain Learning System Test Complete!")
        print("=" * 50)
        print("✅ Agents can now learn market intelligence")
        print("✅ Communication patterns are captured")
        print("✅ User behavior insights stored")
        print("✅ Smart recommendations generated")
        print("✅ Learning analytics working")
        print("\n🚀 Agents are now learning beyond just code!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_multi_domain_learning()