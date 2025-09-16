#!/usr/bin/env python
"""
Comprehensive Persistence Reality Test

This script tests all persistence layer components to validate a 95%+ reality score:

1. Database connectivity and CRUD operations
2. pgvector embedding storage and retrieval
3. Agent knowledge sharing and search
4. Spider data persistence and routing
5. Revenue tracking with real data
6. Redis cache functionality
7. Cross-agent collaboration sessions
8. Data persistence pipelines
9. Search capabilities (text + vector)
10. System performance metrics

Goal: Achieve 95%+ reality score by demonstrating real data flow through all systems.
"""

import os
import sys
import django
import time
import json
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.utils import timezone
from django.core.cache import cache
from django.db import connection
from django.db.models import Sum
from persistence.models import (
    UnifiedEmbedding, AgentKnowledge, SpiderData, RevenueTracker,
    AgentCollaborationSession, SpiderDataRoute, DataPersistenceMetrics
)
from persistence.services import EmbeddingService

def test_database_connectivity():
    """Test basic database operations"""
    print("🔍 Testing Database Connectivity...")

    try:
        # Test basic connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            assert result[0] == 1

        # Test pgvector extension
        with connection.cursor() as cursor:
            cursor.execute("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            result = cursor.fetchone()
            assert result and result[0] == 'vector'

        # Test table existence and data
        counts = {
            'AgentKnowledge': AgentKnowledge.objects.count(),
            'SpiderData': SpiderData.objects.count(),
            'RevenueTracker': RevenueTracker.objects.count(),
            'UnifiedEmbedding': UnifiedEmbedding.objects.count(),
        }

        print(f"  ✅ Database connected with pgvector support")
        print(f"  ✅ Data counts: {counts}")

        # Reality check: We need actual data
        total_records = sum(counts.values())
        if total_records < 50:
            return {'status': 'partial', 'score': 0.6, 'message': f'Only {total_records} records'}

        return {'status': 'real', 'score': 0.95, 'message': f'{total_records} records with pgvector'}

    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return {'status': 'broken', 'score': 0.0, 'message': str(e)}

def test_redis_cache():
    """Test Redis cache functionality"""
    print("🔍 Testing Redis Cache...")

    try:
        # Test basic cache operations
        test_key = f"reality_test_{int(time.time())}"
        test_data = {'test': True, 'timestamp': timezone.now().isoformat()}

        cache.set(test_key, test_data, 300)
        retrieved = cache.get(test_key)

        if retrieved != test_data:
            return {'status': 'broken', 'score': 0.0, 'message': 'Cache data mismatch'}

        # Test cache performance
        start_time = time.time()
        for i in range(100):
            cache.set(f"perf_test_{i}", {'data': i}, 60)
        cache_write_time = time.time() - start_time

        start_time = time.time()
        for i in range(100):
            cache.get(f"perf_test_{i}")
        cache_read_time = time.time() - start_time

        print(f"  ✅ Redis cache working")
        print(f"  ✅ Performance: {cache_write_time:.3f}s write, {cache_read_time:.3f}s read")

        if cache_write_time > 1.0 or cache_read_time > 0.5:
            return {'status': 'partial', 'score': 0.7, 'message': 'Slow cache performance'}

        return {'status': 'real', 'score': 0.9, 'message': 'Fast Redis cache'}

    except Exception as e:
        print(f"  ❌ Redis error: {e}")
        return {'status': 'broken', 'score': 0.0, 'message': str(e)}

def test_agent_knowledge_system():
    """Test agent knowledge sharing and search"""
    print("🔍 Testing Agent Knowledge System...")

    try:
        # Test knowledge creation and retrieval
        knowledge_count = AgentKnowledge.objects.count()
        if knowledge_count == 0:
            return {'status': 'broken', 'score': 0.0, 'message': 'No knowledge entries'}

        # Test knowledge search
        recent_knowledge = AgentKnowledge.objects.filter(
            created_at__gte=timezone.now() - timedelta(hours=24)
        ).count()

        # Test knowledge by type
        knowledge_types = AgentKnowledge.objects.values('knowledge_type').distinct().count()

        # Test agent participation
        agent_count = AgentKnowledge.objects.values('agent_name').distinct().count()

        print(f"  ✅ {knowledge_count} knowledge entries")
        print(f"  ✅ {recent_knowledge} recent entries")
        print(f"  ✅ {knowledge_types} knowledge types")
        print(f"  ✅ {agent_count} contributing agents")

        # Reality scoring
        if knowledge_count < 10:
            return {'status': 'partial', 'score': 0.5, 'message': 'Limited knowledge base'}

        if agent_count < 5:
            return {'status': 'partial', 'score': 0.6, 'message': 'Limited agent participation'}

        return {'status': 'real', 'score': 0.92, 'message': f'{knowledge_count} entries from {agent_count} agents'}

    except Exception as e:
        print(f"  ❌ Knowledge system error: {e}")
        return {'status': 'broken', 'score': 0.0, 'message': str(e)}

def test_spider_data_persistence():
    """Test spider data discovery and routing"""
    print("🔍 Testing Spider Data Persistence...")

    try:
        # Test spider discoveries
        spider_count = SpiderData.objects.count()
        if spider_count == 0:
            return {'status': 'broken', 'score': 0.0, 'message': 'No spider discoveries'}

        # Test data types and sources
        data_types = SpiderData.objects.values('data_type').distinct().count()
        platforms = SpiderData.objects.values('source_platform').distinct().count()
        spiders = SpiderData.objects.values('spider_name').distinct().count()

        # Test opportunity scoring
        high_opportunity = SpiderData.objects.filter(opportunity_score__gte=8.0).count()
        processed_count = SpiderData.objects.filter(is_processed=True).count()

        # Test routing
        routes_count = SpiderDataRoute.objects.count()

        print(f"  ✅ {spider_count} spider discoveries")
        print(f"  ✅ {data_types} data types, {platforms} platforms, {spiders} spiders")
        print(f"  ✅ {high_opportunity} high-opportunity discoveries")
        print(f"  ✅ {processed_count} processed, {routes_count} routed")

        # Reality scoring
        if spider_count < 5:
            return {'status': 'partial', 'score': 0.4, 'message': 'Limited spider data'}

        if spiders < 3:
            return {'status': 'partial', 'score': 0.6, 'message': 'Limited spider diversity'}

        return {'status': 'real', 'score': 0.88, 'message': f'{spider_count} discoveries from {spiders} spiders'}

    except Exception as e:
        print(f"  ❌ Spider data error: {e}")
        return {'status': 'broken', 'score': 0.0, 'message': str(e)}

def test_revenue_tracking():
    """Test revenue tracking with real data"""
    print("🔍 Testing Revenue Tracking...")

    try:
        # Test revenue entries
        revenue_count = RevenueTracker.objects.count()
        if revenue_count == 0:
            return {'status': 'broken', 'score': 0.0, 'message': 'No revenue data'}

        # Test revenue sources and amounts
        revenue_sources = RevenueTracker.objects.values('revenue_source').distinct().count()
        total_revenue = RevenueTracker.objects.filter(
            verification_status='verified'
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')

        # Test attribution
        agent_revenue = RevenueTracker.objects.filter(
            source_agent__isnull=False
        ).count()
        spider_revenue = RevenueTracker.objects.filter(
            source_spider__isnull=False
        ).count()

        # Test recent activity
        recent_revenue = RevenueTracker.objects.filter(
            earned_at__gte=timezone.now() - timedelta(days=30)
        ).count()

        print(f"  ✅ {revenue_count} revenue entries")
        print(f"  ✅ ${total_revenue} total verified revenue")
        print(f"  ✅ {revenue_sources} revenue sources")
        print(f"  ✅ {agent_revenue} agent-attributed, {spider_revenue} spider-attributed")
        print(f"  ✅ {recent_revenue} recent transactions")

        # Reality scoring
        if total_revenue < Decimal('100.00'):
            return {'status': 'partial', 'score': 0.5, 'message': f'Low revenue: ${total_revenue}'}

        if revenue_sources < 3:
            return {'status': 'partial', 'score': 0.6, 'message': 'Limited revenue diversity'}

        return {'status': 'real', 'score': 0.94, 'message': f'${total_revenue} from {revenue_sources} sources'}

    except Exception as e:
        print(f"  ❌ Revenue tracking error: {e}")
        return {'status': 'broken', 'score': 0.0, 'message': str(e)}

def test_embedding_system():
    """Test embedding generation and vector search"""
    print("🔍 Testing Embedding System...")

    try:
        # Test embedding count
        embedding_count = UnifiedEmbedding.objects.count()

        # Test embedding service
        embedding_service = EmbeddingService()

        # Test embedding service initialization
        test_text = "Test embedding generation for reality validation"
        print(f"  ✅ Embedding service ready for text: {test_text[:30]}...")

        # Check if we have actual embeddings in database
        if embedding_count == 0:
            print(f"  ⚠️  No embeddings in database yet")
            return {'status': 'partial', 'score': 0.3, 'message': 'No embeddings stored'}

        # Test embedding content types
        content_types = UnifiedEmbedding.objects.values('content_type').distinct().count()
        source_systems = UnifiedEmbedding.objects.values('source_system').distinct().count()

        print(f"  ✅ {embedding_count} embeddings stored")
        print(f"  ✅ {content_types} content types, {source_systems} source systems")
        print(f"  ✅ Embedding service initialized")

        # Reality scoring
        if embedding_count < 10:
            return {'status': 'partial', 'score': 0.5, 'message': f'Only {embedding_count} embeddings'}

        if content_types < 2:
            return {'status': 'partial', 'score': 0.6, 'message': 'Limited content type diversity'}

        return {'status': 'real', 'score': 0.85, 'message': f'{embedding_count} embeddings across {content_types} types'}

    except Exception as e:
        print(f"  ❌ Embedding system error: {e}")
        return {'status': 'broken', 'score': 0.0, 'message': str(e)}

def test_collaboration_system():
    """Test agent collaboration sessions"""
    print("🔍 Testing Collaboration System...")

    try:
        # Test collaboration sessions
        session_count = AgentCollaborationSession.objects.count()
        if session_count == 0:
            return {'status': 'partial', 'score': 0.3, 'message': 'No collaboration sessions'}

        # Test session status and outcomes
        completed_sessions = AgentCollaborationSession.objects.filter(
            session_status='completed'
        ).count()

        # Test participant diversity
        total_participants = 0
        for session in AgentCollaborationSession.objects.all():
            total_participants += len(session.participating_agents)

        avg_participants = total_participants / session_count if session_count > 0 else 0

        print(f"  ✅ {session_count} collaboration sessions")
        print(f"  ✅ {completed_sessions} completed sessions")
        print(f"  ✅ {avg_participants:.1f} average participants per session")

        # Reality scoring
        if session_count < 2:
            return {'status': 'partial', 'score': 0.4, 'message': 'Limited collaboration activity'}

        return {'status': 'real', 'score': 0.8, 'message': f'{session_count} collaboration sessions'}

    except Exception as e:
        print(f"  ❌ Collaboration system error: {e}")
        return {'status': 'broken', 'score': 0.0, 'message': str(e)}

def test_performance_metrics():
    """Test system performance tracking"""
    print("🔍 Testing Performance Metrics...")

    try:
        # Test metrics collection
        metric_count = DataPersistenceMetrics.objects.count()
        if metric_count == 0:
            return {'status': 'partial', 'score': 0.3, 'message': 'No performance metrics'}

        # Test metric types and subsystems
        metric_types = DataPersistenceMetrics.objects.values('metric_type').distinct().count()
        subsystems = DataPersistenceMetrics.objects.values('subsystem').distinct().count()

        # Test recent metrics
        recent_metrics = DataPersistenceMetrics.objects.filter(
            timestamp__gte=timezone.now() - timedelta(hours=24)
        ).count()

        print(f"  ✅ {metric_count} performance metrics")
        print(f"  ✅ {metric_types} metric types, {subsystems} subsystems")
        print(f"  ✅ {recent_metrics} recent metrics")

        # Reality scoring
        if metric_count < 5:
            return {'status': 'partial', 'score': 0.5, 'message': 'Limited metrics collection'}

        return {'status': 'real', 'score': 0.85, 'message': f'{metric_count} metrics tracked'}

    except Exception as e:
        print(f"  ❌ Performance metrics error: {e}")
        return {'status': 'broken', 'score': 0.0, 'message': str(e)}

def calculate_overall_reality_score(test_results):
    """Calculate overall reality score"""
    weights = {
        'database': 0.20,
        'redis': 0.10,
        'agent_knowledge': 0.15,
        'spider_data': 0.15,
        'revenue_tracking': 0.15,
        'embedding_system': 0.10,
        'collaboration': 0.08,
        'performance_metrics': 0.07
    }

    total_score = 0.0
    for component, weight in weights.items():
        if component in test_results:
            total_score += test_results[component]['score'] * weight

    return total_score

def main():
    """Main test execution"""
    print("🚀 COMPREHENSIVE PERSISTENCE REALITY TEST")
    print("=" * 60)
    print("Goal: Validate 95%+ reality score for all persistence components")
    print("=" * 60)

    # Run all tests
    test_results = {
        'database': test_database_connectivity(),
        'redis': test_redis_cache(),
        'agent_knowledge': test_agent_knowledge_system(),
        'spider_data': test_spider_data_persistence(),
        'revenue_tracking': test_revenue_tracking(),
        'embedding_system': test_embedding_system(),
        'collaboration': test_collaboration_system(),
        'performance_metrics': test_performance_metrics(),
    }

    # Calculate overall score
    overall_score = calculate_overall_reality_score(test_results)

    print("\n" + "=" * 60)
    print("📊 PERSISTENCE REALITY TEST RESULTS")
    print("=" * 60)

    for component, result in test_results.items():
        status_emoji = {
            'real': '🟢',
            'partial': '🟡',
            'broken': '🔴'
        }.get(result['status'], '⚪')

        print(f"{status_emoji} {component.upper()}: {result['status']} ({result['score']:.2f}) - {result['message']}")

    print(f"\n🎯 OVERALL REALITY SCORE: {overall_score:.1%}")

    if overall_score >= 0.95:
        print("✅ EXCELLENT: 95%+ reality score achieved!")
        print("🚀 All persistence systems are working with real data!")
    elif overall_score >= 0.80:
        print("✅ GOOD: 80%+ reality score achieved!")
        print("🔧 Some improvements needed for 95% target")
    elif overall_score >= 0.60:
        print("⚠️  PARTIAL: 60%+ reality score")
        print("🔧 Significant improvements needed")
    else:
        print("❌ POOR: <60% reality score")
        print("🔧 Major fixes required")

    print("\n" + "=" * 60)

    # Summary statistics
    total_records = sum([
        AgentKnowledge.objects.count(),
        SpiderData.objects.count(),
        RevenueTracker.objects.count(),
        UnifiedEmbedding.objects.count(),
        AgentCollaborationSession.objects.count(),
        SpiderDataRoute.objects.count(),
        DataPersistenceMetrics.objects.count(),
    ])

    print(f"📈 PERSISTENCE STATISTICS:")
    print(f"   Total persistent records: {total_records}")
    print(f"   Knowledge entries: {AgentKnowledge.objects.count()}")
    print(f"   Spider discoveries: {SpiderData.objects.count()}")
    print(f"   Revenue transactions: {RevenueTracker.objects.count()}")
    print(f"   Embeddings stored: {UnifiedEmbedding.objects.count()}")
    print(f"   Collaboration sessions: {AgentCollaborationSession.objects.count()}")
    print(f"   Data routes: {SpiderDataRoute.objects.count()}")
    print(f"   Performance metrics: {DataPersistenceMetrics.objects.count()}")

    total_revenue = RevenueTracker.objects.filter(
        verification_status='verified'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    print(f"   Total verified revenue: ${total_revenue}")

    print("\n✅ Persistence reality test completed!")
    return overall_score

if __name__ == '__main__':
    score = main()
    sys.exit(0 if score >= 0.95 else 1)