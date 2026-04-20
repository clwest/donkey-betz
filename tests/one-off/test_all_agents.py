#!/usr/bin/env python
"""
Session 310: Comprehensive Agent and Spider Test Suite
Tests all agents and verifies data flows work correctly.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Tuple

# Test results storage
RESULTS = {
    'spiders': {'passed': 0, 'failed': 0, 'errors': []},
    'clean_agents': {'passed': 0, 'failed': 0, 'errors': []},
    'legacy_agents': {'passed': 0, 'failed': 0, 'errors': []},
    'data_flow': {'passed': 0, 'failed': 0, 'errors': []},
}


def test_result(category: str, name: str, success: bool, error: str = None):
    """Record a test result."""
    if success:
        RESULTS[category]['passed'] += 1
        print(f"  ✅ {name}")
    else:
        RESULTS[category]['failed'] += 1
        RESULTS[category]['errors'].append(f"{name}: {error}")
        print(f"  ❌ {name}: {error[:80]}...")


# =============================================================================
# SPIDER TESTS
# =============================================================================
def test_spiders():
    """Test spider network data collection."""
    print("\n" + "="*60)
    print("🕷️  SPIDER NETWORK TESTS")
    print("="*60)

    from ai_core.spiders.spider_registry import SpiderRegistry
    from core.models_unified_system import SpiderData

    registry = SpiderRegistry()
    stats = registry.get_spider_count()
    print(f"\nRegistered spiders: {stats['total']}")

    # Test a few key spiders that should have real data
    test_spiders = ['hackernews', 'reddit', 'techcrunch', 'devto', 'coingecko']

    for spider_name in test_spiders:
        try:
            spider_class = registry.get_spider_class(spider_name)
            if spider_class:
                spider = spider_class()
                # Check if spider can be instantiated
                test_result('spiders', f"Spider '{spider_name}' instantiation", True)
            else:
                test_result('spiders', f"Spider '{spider_name}' instantiation", False, "Not found in registry")
        except Exception as e:
            test_result('spiders', f"Spider '{spider_name}' instantiation", False, str(e))

    # Check existing spider data
    spider_data_count = SpiderData.objects.count()
    print(f"\nExisting spider data records: {spider_data_count}")

    if spider_data_count > 0:
        test_result('spiders', "Spider data exists in database", True)
        # Show some recent data
        recent = SpiderData.objects.order_by('-created_at')[:3]
        for item in recent:
            data_preview = str(item.raw_data)[:50] if item.raw_data else "No data"
            print(f"    - {item.spider_name}: {data_preview}... ({item.created_at})")
    else:
        test_result('spiders', "Spider data exists in database", False, "No data found")


# =============================================================================
# CLEAN ARCHITECTURE AGENT TESTS
# =============================================================================
def test_clean_agents():
    """Test all clean architecture agents in core/agents/."""
    print("\n" + "="*60)
    print("🏗️  CLEAN ARCHITECTURE AGENT TESTS")
    print("="*60)

    # Import clean agents
    agents_to_test = [
        ('ImageAgent', 'core.agents.image_agent', 'ImageAgent'),
        ('VideoAgent', 'core.agents.video_agent', 'VideoAgent'),
        ('AudioAgent', 'core.agents.audio_agent', 'AudioAgent'),
        ('ThreeDAgent', 'core.agents.three_d_agent', 'ThreeDAgent'),
        ('ImageEditingAgent', 'core.agents.image_editing_agent', 'ImageEditingAgent'),
        ('VideoEditingAgent', 'core.agents.video_editing_agent', 'VideoEditingAgent'),
        ('ResearchAgent', 'core.agents.research_agent', 'ResearchAgent'),
        ('WorkflowAgent', 'core.agents.workflow_agent', 'WorkflowAgent'),
    ]

    for display_name, module_path, class_name in agents_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name)

            # Try to instantiate
            agent = agent_class()

            # Check for required methods
            has_execute = hasattr(agent, 'execute') or hasattr(agent, 'process')
            # Learning hooks use underscore-prefixed methods from mixin
            has_learning = (hasattr(agent, '_share_knowledge') or
                          hasattr(agent, '_create_execution_memory') or
                          hasattr(agent, 'learning_loop'))

            if has_execute:
                test_result('clean_agents', f"{display_name} instantiation", True)
            else:
                test_result('clean_agents', f"{display_name} instantiation", False, "Missing execute method")

            # Check for learning hooks (Session 305-308)
            if has_learning:
                test_result('clean_agents', f"{display_name} learning hooks", True)
            else:
                # Not all agents have learning hooks yet
                print(f"  ⚠️  {display_name} learning hooks: Not implemented")

        except Exception as e:
            test_result('clean_agents', f"{display_name}", False, str(e))


# =============================================================================
# LEGACY AGENT TESTS
# =============================================================================
def test_legacy_agents():
    """Test legacy agents in agents/ directory."""
    print("\n" + "="*60)
    print("📦 LEGACY AGENT TESTS (with learning hooks)")
    print("="*60)

    # These are the agents from Sessions 305-308 that got learning hooks
    legacy_agents = [
        ('TrendAnalysisAgent', 'agents.trend_analysis_agent', 'TrendAnalysisAgent'),
        ('ContentStrategyAgent', 'agents.content_strategy_agent', 'ContentStrategyAgent'),
        ('SEOOptimizerAgent', 'agents.seo_optimizer_agent', 'SEOOptimizerAgent'),
        ('BrandIdentityAgent', 'agents.brand_identity_agent', 'BrandIdentityAgent'),
        ('SocialMediaAgent', 'agents.social_media_agent', 'SocialMediaAgent'),
        ('CreativeDirectorAgent', 'agents.creative_director_agent', 'CreativeDirectorAgent'),
        ('OpportunityScoringAgent', 'agents.opportunity_scoring_agent', 'OpportunityScoringAgent'),
        ('BookmakerAgent', 'agents.bookmaker_agent', 'BookmakerAgent'),
        # Note: PromptEngineeringAgent and CharacterTrainingAgent require special initialization
    ]

    for display_name, module_path, class_name in legacy_agents:
        try:
            module = __import__(module_path, fromlist=[class_name])
            agent_class = getattr(module, class_name)

            # Try to instantiate
            agent = agent_class()

            # Check for learning methods (Sessions 305-308 use underscore-prefixed methods)
            has_share = hasattr(agent, '_share_knowledge')
            has_memory = hasattr(agent, '_create_execution_memory')
            has_retrieve = hasattr(agent, '_get_shared_knowledge')
            has_learning_loop = hasattr(agent, 'learning_loop') or hasattr(agent, '_learning_loop')

            test_result('legacy_agents', f"{display_name} instantiation", True)

            learning_methods = []
            if has_share: learning_methods.append('_share_knowledge')
            if has_memory: learning_methods.append('_create_execution_memory')
            if has_retrieve: learning_methods.append('_get_shared_knowledge')
            if has_learning_loop: learning_methods.append('learning_loop')

            if learning_methods:
                test_result('legacy_agents', f"{display_name} learning hooks", True)
                print(f"      Methods: {', '.join(learning_methods)}")
            else:
                print(f"  ⚠️  {display_name} learning hooks: Not found")

        except ImportError as e:
            test_result('legacy_agents', f"{display_name}", False, f"Import error: {e}")
        except Exception as e:
            test_result('legacy_agents', f"{display_name}", False, str(e))


# =============================================================================
# DATA FLOW TESTS
# =============================================================================
def test_data_flow():
    """Test data flows between components."""
    print("\n" + "="*60)
    print("🔄 DATA FLOW TESTS")
    print("="*60)

    # Test 1: Spider -> Agent Knowledge Source
    print("\n📊 Test 1: Spider Data -> Agent Knowledge")
    try:
        from core.models_unified_system import SpiderData, AgentKnowledgeSource

        spider_count = SpiderData.objects.count()
        knowledge_count = AgentKnowledgeSource.objects.count()

        print(f"   Spider Data records: {spider_count}")
        print(f"   Agent Knowledge Sources: {knowledge_count}")

        if spider_count > 0 and knowledge_count > 0:
            test_result('data_flow', "Spider -> Knowledge pipeline", True)
        elif spider_count == 0:
            test_result('data_flow', "Spider -> Knowledge pipeline", False, "No spider data")
        else:
            test_result('data_flow', "Spider -> Knowledge pipeline", False, "No knowledge sources")
    except Exception as e:
        test_result('data_flow', "Spider -> Knowledge pipeline", False, str(e))

    # Test 2: Agent Memory System
    print("\n📊 Test 2: Agent Memory System")
    try:
        from core.models_unified_system import AgentMemory

        memory_count = AgentMemory.objects.count()
        print(f"   Agent Memory records: {memory_count}")

        if memory_count > 0:
            test_result('data_flow', "Agent Memory system", True)
            # Show recent memories
            recent = AgentMemory.objects.select_related('agent').order_by('-created_at')[:3]
            for mem in recent:
                agent_name = mem.agent.name if mem.agent else 'Unknown'
                print(f"      - {agent_name}: {mem.memory_type} ({mem.created_at})")
        else:
            test_result('data_flow', "Agent Memory system", False, "No memories recorded")
    except Exception as e:
        test_result('data_flow', "Agent Memory system", False, str(e))

    # Test 3: Agent Execution Records
    print("\n📊 Test 3: Agent Execution Tracking")
    try:
        from core.models_unified_system import AgentExecution

        exec_count = AgentExecution.objects.count()
        print(f"   Agent Execution records: {exec_count}")

        if exec_count > 0:
            test_result('data_flow', "Agent Execution tracking", True)
        else:
            test_result('data_flow', "Agent Execution tracking", False, "No executions recorded")
    except Exception as e:
        test_result('data_flow', "Agent Execution tracking", False, str(e))

    # Test 4: Collective Intelligence Service
    print("\n📊 Test 4: Collective Intelligence Service")
    try:
        from core.services.collective_intelligence import get_collective_intelligence_service
        from django.contrib.auth import get_user_model

        User = get_user_model()
        user = User.objects.first()

        service = get_collective_intelligence_service(user)
        stats = service.get_collective_stats()

        if 'error' not in stats:
            test_result('data_flow', "Collective Intelligence Service", True)
            print(f"      Total agents: {stats.get('agents', {}).get('total', 0)}")
            print(f"      Knowledge items: {stats.get('knowledge', {}).get('total_items', 0)}")
        else:
            test_result('data_flow', "Collective Intelligence Service", False, stats['error'])
    except Exception as e:
        test_result('data_flow', "Collective Intelligence Service", False, str(e))


# =============================================================================
# SUMMARY
# =============================================================================
def print_summary():
    """Print test summary."""
    print("\n" + "="*60)
    print("📋 TEST SUMMARY")
    print("="*60)

    total_passed = 0
    total_failed = 0

    for category, results in RESULTS.items():
        passed = results['passed']
        failed = results['failed']
        total = passed + failed
        total_passed += passed
        total_failed += failed

        status = "✅" if failed == 0 else "⚠️" if passed > failed else "❌"
        print(f"\n{status} {category.upper()}: {passed}/{total} passed")

        if results['errors']:
            print("   Errors:")
            for error in results['errors'][:5]:  # Show first 5 errors
                print(f"     - {error[:70]}...")

    print("\n" + "-"*60)
    total = total_passed + total_failed
    percentage = (total_passed / total * 100) if total > 0 else 0

    if percentage >= 90:
        print(f"🎉 OVERALL: {total_passed}/{total} tests passed ({percentage:.1f}%)")
    elif percentage >= 70:
        print(f"⚠️  OVERALL: {total_passed}/{total} tests passed ({percentage:.1f}%)")
    else:
        print(f"❌ OVERALL: {total_passed}/{total} tests passed ({percentage:.1f}%)")

    return total_failed == 0


# =============================================================================
# MAIN
# =============================================================================
if __name__ == '__main__':
    print("="*60)
    print("🚀 SESSION 310: COMPREHENSIVE AGENT TEST SUITE")
    print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    test_spiders()
    test_clean_agents()
    test_legacy_agents()
    test_data_flow()

    success = print_summary()
    sys.exit(0 if success else 1)
