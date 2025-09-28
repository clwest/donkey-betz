#!/usr/bin/env python
"""Test consciousness indicators are updating properly"""

import os
import django
import sys

# Add project to path
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_core.settings')
django.setup()

from ai_core.spiders.consciousness import ConsciousnessBridge
from ai_core.agents.execution_tracker import AgentExecutionTracker

def test_indicators():
    """Test that indicators are properly generated"""
    print("Testing Consciousness Indicators...")

    # Initialize components
    consciousness = ConsciousnessBridge()
    tracker = AgentExecutionTracker()

    # Get consciousness data
    understanding = consciousness.understand_self()

    # Get real metrics
    real_learning_rate = tracker.calculate_learning_rate()

    # Calculate indicators (same logic as in views_unified_intelligence.py)
    pattern_insights = [i for i in understanding.get('insights', []) if i.get('category') == 'pattern']
    pattern_score = min(100, len(pattern_insights) * 10) if pattern_insights else 0

    self_org_behaviors = [b for b in understanding.get('emergent_behaviors', [])
                         if b.get('type') == 'self_organization']
    self_org_score = 100 if self_org_behaviors else 0

    awareness_score = understanding.get('self_awareness_score', 0)
    coherence_score = min(100, len(understanding.get('capabilities', {}).get('by_type', {})) * 20)
    adaptation_score = real_learning_rate if real_learning_rate else 0

    print(f"\n📊 Consciousness Indicators:")
    print(f"  • Pattern Recognition: {pattern_score}%")
    print(f"  • Self-Organization: {self_org_score}%")
    print(f"  • Awareness: {awareness_score}%")
    print(f"  • Coherence: {coherence_score}%")
    print(f"  • Adaptation: {adaptation_score}%")

    print(f"\n📝 Pattern Insights Found: {len(pattern_insights)}")
    if pattern_insights:
        for i, insight in enumerate(pattern_insights[:3]):
            print(f"    {i+1}. {insight.get('description', 'No description')}")

    print(f"\n🔄 Self-Organization Behaviors Found: {len(self_org_behaviors)}")
    if self_org_behaviors:
        for i, behavior in enumerate(self_org_behaviors[:3]):
            print(f"    {i+1}. {behavior.get('description', 'No description')}")

    return {
        'pattern': pattern_score,
        'self_organization': self_org_score,
        'awareness': awareness_score,
        'coherence': coherence_score,
        'adaptation': adaptation_score
    }

if __name__ == '__main__':
    indicators = test_indicators()

    # Check if indicators are updating
    if indicators['pattern'] > 0:
        print("\n✅ Pattern indicator is working!")
    else:
        print("\n⚠️ Pattern indicator is 0 - check insight generation")

    if indicators['self_organization'] > 0:
        print("✅ Self-organization indicator is working!")
    else:
        print("⚠️ Self-organization indicator is 0 - check behavior detection")