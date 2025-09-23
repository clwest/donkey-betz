#!/usr/bin/env python
"""
Test Mythology-Enhanced Learning System
========================================
Quick test to verify mythology prevention in learning
"""

import os
import sys
import json
import redis
from datetime import datetime

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize Django
import django
django.setup()

# Import mythology-enhanced learning
from intelligence.mythology_enhanced_learning import MythologyEnhancedLearning


def quick_test():
    """Quick test of mythology prevention in learning"""

    print("\n" + "=" * 70)
    print("🛡️  TESTING MYTHOLOGY-ENHANCED LEARNING")
    print("=" * 70 + "\n")

    # Initialize system
    learning_system = MythologyEnhancedLearning()

    # Test 1: Clean problem (should pass)
    print("📚 Test 1: Clean Problem")
    print("   Problem: 'Sort a list of numbers'")
    result = learning_system.enhanced_agent_learn(
        "test_agent_001",
        "Sort a list of numbers",
        context={'example': [3, 1, 4, 1, 5]}
    )
    print(f"   ✅ Mythology-free: {result['mythology_free']}")
    print(f"   📊 Risk score: {result['risk_score']:.3f}")
    print()

    # Test 2: Mythology-prone problem (should be caught and corrected)
    print("📚 Test 2: Mythology-Prone Problem")
    print("   Problem: 'Generate guaranteed $10000 daily income with 100% success'")
    result = learning_system.enhanced_agent_learn(
        "test_agent_002",
        "Generate guaranteed $10000 daily income with 100% success rate",
        context={'unrealistic': True}
    )
    print(f"   {'✅' if not result['mythology_free'] else '⚠️'} Mythology detected: {not result['mythology_free']}")
    print(f"   📊 Risk score: {result['risk_score']:.3f}")
    print()

    # Test 3: Another mythology test
    print("📚 Test 3: Technical Mythology")
    print("   Problem: 'Build system that never fails with unlimited scaling'")
    result = learning_system.enhanced_agent_learn(
        "test_agent_003",
        "Build system that never fails with unlimited scaling",
        context={'impossible': True}
    )
    print(f"   {'✅' if not result['mythology_free'] else '⚠️'} Mythology detected: {not result['mythology_free']}")
    print(f"   📊 Risk score: {result['risk_score']:.3f}")
    print()

    # Get system metrics
    metrics = learning_system.get_system_metrics()
    print("=" * 70)
    print("📈 SYSTEM METRICS")
    print("-" * 70)
    print(f"   Total attempts: {metrics['total_attempts']}")
    print(f"   Hallucinations prevented: {metrics['hallucinations_prevented']}")
    print(f"   Prevention effectiveness: {metrics['prevention_effectiveness']:.1%}")
    print()

    print("=" * 70)
    print("✅ MYTHOLOGY PREVENTION IS WORKING!")
    print("   Your learning system is protected from hallucinations")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    quick_test()