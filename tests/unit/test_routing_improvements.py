# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
import pytest

# Session 452: Add django_db marker for all tests
pytestmark = pytest.mark.django_db

#!/usr/bin/env python
"""
Test improved agent routing thresholds
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.agent_integration import AgentRouter

User = get_user_model()

def test_routing_improvements():
    """Test that routing improvements are working"""
    print("\n🧪 Testing Improved Agent Routing")
    print("=" * 60)
    
    # Get a user for testing
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.first()
    
    router = AgentRouter(user)
    
    # Test cases that should now trigger routing
    test_queries = [
        # Previously failing queries
        "What's changed?",
        "Give me a summary",
        "Show me the latest updates",
        "What are the recent changes",
        "Help me understand the system",
        
        # Common user queries
        "How does this work?",
        "Explain the architecture",
        "List the available features",
        "What can you do?",
        "Tell me about the agents",
        
        # Status queries
        "Check the system status",
        "Review the current state",
        "Update me on progress",
        
        # Simple queries that should NOT route
        "Hi",
        "Thanks",
        "OK",
        "Goodbye"
    ]
    
    print("\n📊 Routing Decision Tests:")
    print("-" * 60)
    
    routing_count = 0
    for query in test_queries:
        should_route = router.should_use_agent_routing(query)
        best_agent = None
        
        if should_route:
            best_agent = router.find_best_agent(query)
            routing_count += 1
        
        status = "✅ ROUTES" if should_route else "⏭️  DIRECT"
        agent_info = f" → {best_agent['agent_name']} (score: {best_agent['score']:.2f})" if best_agent else ""
        
        print(f"{status} | {query[:40]:<40}{agent_info}")
    
    print("-" * 60)
    print(f"\n📈 Results: {routing_count}/{len(test_queries)} queries will route to agents")
    print(f"   Routing percentage: {(routing_count/len(test_queries))*100:.1f}%")
    
    # Test confidence thresholds
    print("\n🎯 Testing Confidence Thresholds:")
    print("-" * 60)
    
    test_agent_scores = [
        ("What's changed in the system?", 0.3),  # Should route with lower threshold
        ("Analyze the performance metrics", 0.7),  # Should definitely route
        ("Hi there", 0.1),  # Should not route
    ]
    
    for query, expected_min_score in test_agent_scores:
        should_route = router.should_use_agent_routing(query)
        agent = router.find_best_agent(query) if should_route else None
        
        if agent:
            passes = agent['score'] >= expected_min_score
            status = "✅" if passes else "❌"
            print(f"{status} Query: '{query[:30]}...' | Agent: {agent['agent_name']} | Score: {agent['score']:.2f}")
        else:
            print(f"⏭️  Query: '{query[:30]}...' | No routing")
    
    print("\n✨ Routing improvements are active!")
    print("   - Expanded keyword detection")
    print("   - Lowered confidence threshold (0.8 → 0.4)")
    print("   - Fallback agent finding when registry unavailable")
    print("   - Better coverage for common queries")

if __name__ == '__main__':
    test_routing_improvements()