#!/usr/bin/env python
"""
Direct reality check without cache to identify issues
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.db import connection
from intelligence.models import OpportunityActionPlan, ActionPlan, EarningRecord
from core.models.agents_registry import UnifiedAgentTemplate, AgentTaskExecution
from persistence.models import (
    UnifiedUser, UserProfile, DocumentEmbedding, PersistentMemory,
    AgentKnowledge, SpiderDiscovery, SystemMetrics
)

def check_database_reality():
    """Check database reality directly"""
    print("\n" + "="*50)
    print("DATABASE REALITY CHECK")
    print("="*50)

    # Check connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("✅ Database connection: ACTIVE")

    # Check intelligence models
    opp_count = OpportunityActionPlan.objects.count()
    plan_count = ActionPlan.objects.count()
    earning_count = EarningRecord.objects.count()

    print(f"\nIntelligence Data:")
    print(f"  Opportunities: {opp_count}")
    print(f"  Action Plans: {plan_count}")
    print(f"  Earnings: {earning_count}")

    # Check persistence models
    doc_count = DocumentEmbedding.objects.count()
    memory_count = PersistentMemory.objects.count()
    knowledge_count = AgentKnowledge.objects.count()
    spider_count = SpiderDiscovery.objects.count()
    metrics_count = SystemMetrics.objects.count()

    print(f"\nPersistence Data:")
    print(f"  Document Embeddings: {doc_count}")
    print(f"  Persistent Memories: {memory_count}")
    print(f"  Agent Knowledge: {knowledge_count}")
    print(f"  Spider Discoveries: {spider_count}")
    print(f"  System Metrics: {metrics_count}")

    # Check agents
    agent_count = UnifiedAgentTemplate.objects.count()
    execution_count = AgentTaskExecution.objects.count()

    print(f"\nAgent Data:")
    print(f"  Registered Agents: {agent_count}")
    print(f"  Agent Executions: {execution_count}")

    # Check users
    user_count = UnifiedUser.objects.count()
    profile_count = UserProfile.objects.count()

    print(f"\nUser Data:")
    print(f"  Users: {user_count}")
    print(f"  Profiles: {profile_count}")

    # Calculate reality score
    total_checks = 10
    passed_checks = sum([
        opp_count > 0 or plan_count > 0 or earning_count > 0,
        doc_count > 0,
        memory_count > 0,
        knowledge_count > 0,
        spider_count > 0,
        metrics_count > 0,
        agent_count > 0,
        execution_count > 0,
        user_count > 0,
        profile_count > 0
    ])

    reality_score = (passed_checks / total_checks) * 100

    print(f"\n{'='*50}")
    print(f"DATABASE REALITY SCORE: {reality_score:.1f}%")
    print(f"Status: {'✅ REAL' if reality_score > 80 else '⚠️ PARTIAL' if reality_score > 30 else '❌ MOCK'}")
    print(f"{'='*50}")

    return reality_score

def check_agent_reality():
    """Check if agents are real or just registered"""
    print("\n" + "="*50)
    print("AGENT REALITY CHECK")
    print("="*50)

    try:
        from core.models.agents_registry import UnifiedAgentTemplate

        agents = UnifiedAgentTemplate.objects.all()
        total_agents = agents.count()

        print(f"\nTotal Registered Agents: {total_agents}")

        # Check execution stats
        for agent in agents[:10]:  # Sample first 10
            exec_count = agent.executions.count()
            if exec_count > 0:
                print(f"  ✅ {agent.name}: {exec_count} executions")
            else:
                print(f"  ⚠️ {agent.name}: No executions")

        # Check if agents have implementation
        has_impl = 0
        for agent in agents:
            if agent.code_implementation and len(agent.code_implementation) > 100:
                has_impl += 1

        print(f"\nAgents with Implementation: {has_impl}/{total_agents}")

        reality_score = (has_impl / total_agents * 100) if total_agents > 0 else 0

        print(f"\n{'='*50}")
        print(f"AGENT REALITY SCORE: {reality_score:.1f}%")
        print(f"Status: {'✅ REAL' if reality_score > 80 else '⚠️ PARTIAL' if reality_score > 30 else '❌ MOCK'}")
        print(f"{'='*50}")

        return reality_score

    except Exception as e:
        print(f"❌ Error checking agents: {e}")
        return 0

def check_ml_reality():
    """Check ML pipeline reality"""
    print("\n" + "="*50)
    print("ML PIPELINE REALITY CHECK")
    print("="*50)

    try:
        from intelligence.ml_engine import UnifiedMLEngine

        ml_engine = UnifiedMLEngine()

        # Check MLX availability
        print(f"MLX Available: {ml_engine.mlx_available}")

        # Check models
        models = ml_engine.list_models()
        print(f"Registered Models: {len(models)}")
        for model_name in models:
            print(f"  - {model_name}")

        # Test prediction
        try:
            test_data = {"test": "data"}
            result = ml_engine.predict("sports_crypto_lstm", test_data)
            print(f"\n✅ ML Prediction Working")
            reality_score = 90
        except Exception as e:
            print(f"\n⚠️ ML Prediction Error: {e}")
            reality_score = 50

        print(f"\n{'='*50}")
        print(f"ML PIPELINE REALITY SCORE: {reality_score:.1f}%")
        print(f"Status: {'✅ REAL' if reality_score > 80 else '⚠️ PARTIAL' if reality_score > 30 else '❌ MOCK'}")
        print(f"{'='*50}")

        return reality_score

    except Exception as e:
        print(f"❌ Error checking ML pipeline: {e}")
        return 0

def main():
    """Run comprehensive reality check"""
    print("\n" + "="*70)
    print("🔍 UNIFIED DONKEY BETZ PLATFORM - DIRECT REALITY CHECK")
    print("="*70)

    scores = []

    # Check each component
    scores.append(check_database_reality())
    scores.append(check_agent_reality())
    scores.append(check_ml_reality())

    # Calculate overall score
    overall_score = sum(scores) / len(scores)

    print("\n" + "="*70)
    print("📊 OVERALL PLATFORM REALITY SCORE")
    print("="*70)
    print(f"\nOverall Score: {overall_score:.1f}%")

    if overall_score >= 95:
        print("Status: 🏆 FULLY OPERATIONAL")
    elif overall_score >= 70:
        print("Status: ✅ MOSTLY REAL")
    elif overall_score >= 50:
        print("Status: ⚠️ PARTIALLY OPERATIONAL")
    else:
        print("Status: ❌ MOSTLY MOCK")

    print("\n🎯 To achieve 95%+ reality score:")
    if overall_score < 95:
        print("1. Deploy real spiders to collect opportunity data")
        print("2. Execute agents to generate action plans")
        print("3. Track real revenue in earning records")
        print("4. Store embeddings and memories from real interactions")
        print("5. Connect all components with real data flows")

    print("="*70)

if __name__ == "__main__":
    main()