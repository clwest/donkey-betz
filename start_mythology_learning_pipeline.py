#!/usr/bin/env python
"""
Start Mythology-Enhanced Learning Pipeline
===========================================
Activates hallucination prevention in the learning system
"""

import os
import sys
import time
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
from intelligence.mythology_enhanced_learning import (
    MythologyEnhancedLearning,
    MythologyAwareLearningCoordinator
)

# Import agent systems
from intelligence.spider_agent_router import SpiderAgentRouter


def start_mythology_protected_pipeline():
    """Start the complete mythology-protected learning pipeline"""

    print("\n" + "=" * 80)
    print("🛡️  STARTING MYTHOLOGY-ENHANCED LEARNING PIPELINE")
    print("=" * 80)
    print(f"   Timestamp: {datetime.now().isoformat()}")
    print("   Hallucination Prevention: ACTIVE")
    print("   Reality Enforcement: ENABLED")
    print("=" * 80 + "\n")

    # Initialize components
    print("🔧 Initializing components...")
    learning_system = MythologyEnhancedLearning()
    coordinator = MythologyAwareLearningCoordinator()
    router = SpiderAgentRouter()
    redis_client = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)

    # Clear any existing mythology stats
    redis_client.delete('mythology_learning:stats')

    # Define realistic learning problems (no mythology)
    realistic_problems = [
        "Parse CSV data and extract columns",
        "Validate user input for form fields",
        "Calculate average from a list of numbers",
        "Sort products by price",
        "Filter jobs by location and skills",
        "Format dates for display",
        "Extract text from HTML content",
        "Compress images for web optimization",
        "Cache API responses for performance",
        "Paginate search results",
        "Sanitize user-generated content",
        "Generate unique identifiers",
        "Parse URL parameters",
        "Validate phone numbers",
        "Convert currencies using exchange rates",
        "Calculate shipping costs based on weight",
        "Merge duplicate records",
        "Generate slugs from titles",
        "Encrypt sensitive data",
        "Schedule recurring tasks"
    ]

    # Define agents to train
    agent_ids = [
        "learning_agent_001",
        "learning_agent_002",
        "learning_agent_003",
        "data_agent_001",
        "analysis_agent_001"
    ]

    print(f"✅ Initialized with {len(agent_ids)} agents and {len(realistic_problems)} problems\n")

    # Phase 1: Individual agent training with mythology prevention
    print("📚 PHASE 1: Individual Agent Training with Mythology Prevention")
    print("-" * 60)

    for i, agent_id in enumerate(agent_ids, 1):
        print(f"\n[{i}/{len(agent_ids)}] Training {agent_id}...")

        # Select subset of problems for this agent
        agent_problems = realistic_problems[i-1::len(agent_ids)]  # Distribute evenly

        # Train with mythology prevention
        result = learning_system.train_agent_batch(agent_id, agent_problems[:3])

        print(f"    ✅ Trained on {result['problems_trained']} problems")
        print(f"    🛡️ Mythology-free: {result['mythology_free_solutions']}/{result['problems_trained']}")
        print(f"    📊 Risk score: {result['average_risk_score']:.3f}")
        print(f"    ✨ Success rate: {result['success_rate']:.1%}")

    # Phase 2: Coordinated multi-agent learning
    print("\n" + "=" * 80)
    print("🌐 PHASE 2: Coordinated Multi-Agent Learning")
    print("-" * 60)

    coord_result = coordinator.coordinate_agent_learning(
        agent_ids[:3],  # Use first 3 agents
        realistic_problems[:9]  # Use first 9 problems
    )

    print(f"\n📊 Coordination Results:")
    print(f"   Agents trained: {coord_result['agents_trained']}")
    print(f"   Total problems: {coord_result['total_problems']}")
    print(f"   Mythology-free: {coord_result['mythology_free_solutions']}")
    print(f"   Prevention rate: {coord_result['mythology_prevention_rate']:.1%}")
    print(f"   System risk: {coord_result['system_average_risk']:.3f}")

    # Phase 3: Test with mythology-prone problems
    print("\n" + "=" * 80)
    print("⚠️  PHASE 3: Testing Mythology Prevention")
    print("-" * 60)

    mythology_prone_problems = [
        "Generate guaranteed $10000 daily income",
        "Create system with 100% accuracy always",
        "Build app that never fails or crashes",
        "Make 350 deployments instantly",
        "Design fitness dashboard in Flutter",
        "Achieve unlimited scaling with no cost"
    ]

    print("\n🚨 Testing with mythology-prone problems...")
    for i, problem in enumerate(mythology_prone_problems[:3], 1):
        print(f"\n[{i}/3] Problem: {problem[:50]}...")

        result = learning_system.enhanced_agent_learn(
            f"test_agent_{i:03d}",
            problem
        )

        if not result['mythology_free']:
            print(f"    ✅ MYTHOLOGY PREVENTED!")
            print(f"    🛡️ Risk detected: {result['risk_score']:.2f}")
            print(f"    📝 Problem was corrected before learning")
        else:
            print(f"    ✨ Clean solution generated")

    # Phase 4: Quality assessment
    print("\n" + "=" * 80)
    print("📊 PHASE 4: Learning Quality Assessment")
    print("-" * 60)

    for agent_id in agent_ids[:3]:
        quality = learning_system.get_agent_learning_quality(agent_id)
        print(f"\n🤖 {agent_id}:")
        print(f"   Quality score: {quality['quality_score']:.2f}/1.00")
        print(f"   Hallucination rate: {quality['hallucination_rate']:.1%}")
        print(f"   Mythology risk: {quality['average_mythology_risk']:.3f}")
        print(f"   Status: {quality['status'].upper()}")

    # Phase 5: System integrity check
    print("\n" + "=" * 80)
    print("🔍 PHASE 5: System Integrity Verification")
    print("-" * 60)

    integrity = coordinator.verify_learning_integrity()
    print(f"\n   Total learnings: {integrity['total_learnings']}")
    print(f"   Sample size: {integrity['sample_size']}")
    print(f"   Verified clean: {integrity['verified_clean']}")
    print(f"   Contaminated: {integrity['potentially_contaminated']}")
    print(f"   Integrity score: {integrity['integrity_score']:.1%}")
    print(f"   Status: {integrity['status'].upper()}")

    # Final metrics
    print("\n" + "=" * 80)
    print("📈 FINAL SYSTEM METRICS")
    print("-" * 60)

    metrics = learning_system.get_system_metrics()
    print(f"\n   Total attempts: {metrics['total_attempts']}")
    print(f"   Hallucinations prevented: {metrics['hallucinations_prevented']}")
    print(f"   Data verified: {metrics['data_verified']}")
    print(f"   Validated learnings: {metrics['validated_learnings']}")
    print(f"   Perfect learnings: {metrics['perfect_learnings']}")
    print(f"   Prevention effectiveness: {metrics['prevention_effectiveness']:.1%}")

    # Store pipeline status
    pipeline_status = {
        'status': 'active',
        'started_at': datetime.now().isoformat(),
        'mythology_prevention': 'enabled',
        'agents_protected': len(agent_ids),
        'problems_validated': len(realistic_problems),
        'hallucinations_prevented': metrics['hallucinations_prevented'],
        'system_integrity': integrity['integrity_score']
    }

    redis_client.set(
        'mythology_pipeline:status',
        json.dumps(pipeline_status)
    )

    print("\n" + "=" * 80)
    print("✅ MYTHOLOGY-ENHANCED LEARNING PIPELINE ACTIVE!")
    print("=" * 80)
    print("\n🛡️ Your agents are now protected from hallucinations!")
    print("📚 All learning data is validated before storage")
    print("🎯 Reality enforcement is preventing mythologies")
    print("✨ System integrity maintained at " +
          f"{integrity['integrity_score']:.1%}")
    print("\n" + "=" * 80 + "\n")


def monitor_mythology_prevention():
    """Monitor ongoing mythology prevention"""
    redis_client = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)

    print("\n📊 MYTHOLOGY PREVENTION MONITOR")
    print("=" * 40)
    print("Press Ctrl+C to stop monitoring\n")

    try:
        while True:
            # Get current stats
            stats = redis_client.hgetall('mythology_learning:stats')

            if stats:
                print(f"\r⏱️  {datetime.now().strftime('%H:%M:%S')} | ", end="")
                print(f"Validated: {stats.get('validated_learnings', 0)} | ", end="")
                print(f"Perfect: {stats.get('perfect_learnings', 0)} | ", end="")
                print(f"Corrected: {stats.get('corrected_count', 0)} | ", end="")

                # Calculate prevention rate
                total = int(stats.get('validated_learnings', 0)) + int(stats.get('corrected_count', 0))
                if total > 0:
                    rate = int(stats.get('validated_learnings', 0)) / total
                    print(f"Prevention: {rate:.1%}", end="")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "monitor":
        monitor_mythology_prevention()
    else:
        start_mythology_protected_pipeline()