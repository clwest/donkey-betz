#!/usr/bin/env python
"""
Test REAL Proposal Execution
=============================
This script tests that AI proposals now execute REAL optimizations
instead of simulated ones.
"""

import os
import sys
import django
import json
import requests
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def test_real_proposal_execution():
    """Test that proposals execute real optimizations"""

    print("\n" + "="*80)
    print("🚀 TESTING REAL PROPOSAL EXECUTION")
    print("="*80)

    # Import the ProposalManager and AIProposal
    from backend.intelligence.proposal_manager import ProposalManager, AIProposal

    manager = ProposalManager()

    # Get or create a test optimization proposal
    from backend.intelligence.proposal_manager import ProposalStatus, ProposalRisk

    test_proposal = AIProposal(
        id="test_websocket_opt_001",
        title="Optimize WebSocket Connection Pool",
        category="optimization",
        description="Optimize WebSocket connections for better performance",
        risk_level=ProposalRisk.LOW,
        status=ProposalStatus.APPROVED,
        created_at=datetime.now(),
        impact_score=8.5,
        roi_estimate=5.2,
        affected_components=["WebSocket", "Redis", "Channels"],
        dependencies=[],
        implementation_steps=[
            "Optimize Redis connection pool",
            "Enable TCP keepalive",
            "Clear stale connections",
            "Increase channel capacity"
        ],
        estimated_time="5 minutes",
        rollback_plan="Revert Redis config changes",
        evidence={"current_connections": 50, "target": 1000},
        confidence_score=0.9,
        ai_reasoning="WebSocket connections can be optimized for better performance",
        approved_by="test_user",
        approved_at=datetime.now()
    )

    # Add to manager's proposals
    manager.proposals[test_proposal.id] = test_proposal

    print(f"\n📋 Testing proposal: {test_proposal.title}")
    print(f"   Category: {test_proposal.category}")
    print(f"   Status: {test_proposal.status}")

    print("\n🔧 Executing REAL optimization...")
    print("-" * 40)

    # Execute the proposal
    result = manager.execute_proposal(test_proposal.id)

    print("\n📊 Execution Result:")
    print(json.dumps(result, indent=2))

    # Check if it's real or simulated
    if "[SIMULATED]" in str(result):
        print("\n❌ STILL SIMULATED - Optimization is not real!")
    elif result.get("real_execution"):
        print("\n✅ REAL EXECUTION CONFIRMED!")
        print("   Improvements made:")
        for improvement in result.get("improvements", []):
            print(f"   • {improvement}")

        print("\n   Metrics:")
        for key, value in result.get("metrics", {}).items():
            print(f"   • {key}: {value}")
    else:
        print("\n⚠️ Execution status unclear - check result above")

    # Test cache optimization
    print("\n" + "="*80)
    print("🔧 Testing Cache Optimization")
    print("-" * 40)

    cache_proposal = AIProposal(
        id="test_cache_opt_001",
        title="Optimize Redis Cache Performance",
        category="optimization",
        description="Optimize cache for better memory usage",
        risk_level=ProposalRisk.LOW,
        status=ProposalStatus.APPROVED,
        created_at=datetime.now(),
        impact_score=7.5,
        roi_estimate=4.8,
        affected_components=["Redis", "Cache"],
        dependencies=[],
        implementation_steps=[
            "Set LRU eviction policy",
            "Configure max memory",
            "Add expiry to keys"
        ],
        estimated_time="3 minutes",
        rollback_plan="Restore previous Redis settings",
        evidence={"memory_usage": "80%", "target": "60%"},
        confidence_score=0.85,
        ai_reasoning="Cache optimization can reduce memory usage",
        approved_by="test_user",
        approved_at=datetime.now()
    )

    manager.proposals[cache_proposal.id] = cache_proposal
    cache_result = manager.execute_proposal(cache_proposal.id)

    if cache_result.get("real_execution"):
        print("✅ Cache optimization REALLY executed!")
        for improvement in cache_result.get("improvements", []):
            print(f"   • {improvement}")
    else:
        print("❌ Cache optimization failed or simulated")

    # Test agent optimization
    print("\n" + "="*80)
    print("🤖 Testing Agent Performance Optimization")
    print("-" * 40)

    agent_proposal = AIProposal(
        id="test_agent_opt_001",
        title="Optimize Agent Performance",
        category="optimization",
        description="Speed up agent execution with indexes",
        risk_level=ProposalRisk.MEDIUM,
        status=ProposalStatus.APPROVED,
        created_at=datetime.now(),
        impact_score=9.0,
        roi_estimate=6.5,
        affected_components=["Agents", "Database"],
        dependencies=["PostgreSQL"],
        implementation_steps=[
            "Create database indexes",
            "Enable caching",
            "Set batch processing"
        ],
        estimated_time="10 minutes",
        rollback_plan="Drop created indexes",
        evidence={"query_time": "500ms", "target": "50ms"},
        confidence_score=0.92,
        ai_reasoning="Database indexes will significantly improve agent query performance",
        approved_by="test_user",
        approved_at=datetime.now()
    )

    manager.proposals[agent_proposal.id] = agent_proposal
    agent_result = manager.execute_proposal(agent_proposal.id)

    if agent_result.get("real_execution"):
        print("✅ Agent optimization REALLY executed!")
        for improvement in agent_result.get("improvements", []):
            print(f"   • {improvement}")
    else:
        print("❌ Agent optimization failed or simulated")

    print("\n" + "="*80)
    print("🎉 REAL PROPOSAL EXECUTION TEST COMPLETE!")
    print("="*80)

    # Summary
    total_real = sum([
        1 if result.get("real_execution") else 0,
        1 if cache_result.get("real_execution") else 0,
        1 if agent_result.get("real_execution") else 0
    ])

    print(f"\n📊 SUMMARY:")
    print(f"   • Total proposals tested: 3")
    print(f"   • Real executions: {total_real}/3")
    print(f"   • Success rate: {(total_real/3)*100:.1f}%")

    if total_real == 3:
        print("\n🚀 ALL PROPOSALS ARE NOW EXECUTING REAL OPTIMIZATIONS!")
        print("   The system is no longer simulating - it's making real changes!")
    elif total_real > 0:
        print(f"\n⚠️ PARTIAL SUCCESS: {total_real}/3 proposals executed real optimizations")
    else:
        print("\n❌ NO REAL EXECUTIONS - Check error messages above")

    print("="*80)

if __name__ == "__main__":
    test_real_proposal_execution()