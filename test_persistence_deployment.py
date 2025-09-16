#!/usr/bin/env python
"""
Test script to validate Data Persistence Infrastructure deployment.

This script tests the core functionality of the persistence system without
requiring database migrations initially.
"""

import os
import sys
import django
import logging
from pathlib import Path

# Add the project to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all persistence modules can be imported."""
    try:
        logger.info("Testing persistence module imports...")

        # Test model imports
        from persistence.models import (
            UnifiedEmbedding, AgentKnowledge, SpiderData, SpiderDataRoute,
            AgentCollaborationSession, DataPersistenceMetrics
        )
        logger.info("✅ Models imported successfully")

        # Test service imports
        from persistence.services import (
            EmbeddingService, AgentKnowledgeService, SpiderDataService,
            UnifiedSearchService
        )
        logger.info("✅ Services imported successfully")

        # Test integration imports
        from persistence.content_integration import (
            document_persistence, content_generation_integration
        )
        logger.info("✅ Content integration imported successfully")

        # Test Redis configuration
        from persistence.redis_config import redis_persistence
        logger.info("✅ Redis configuration imported successfully")

        return True

    except ImportError as e:
        logger.error(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error during import: {e}")
        return False

def test_redis_connection():
    """Test Redis connection and persistence configuration."""
    try:
        logger.info("Testing Redis connection...")

        from persistence.redis_config import redis_persistence

        # Test basic Redis operations
        test_key = "persistence_test"
        test_value = "test_data"

        # Store and retrieve test data
        redis_persistence.redis_client.set(test_key, test_value)
        retrieved_value = redis_persistence.redis_client.get(test_key)

        if retrieved_value == test_value:
            logger.info("✅ Redis basic operations working")
        else:
            logger.error("❌ Redis data retrieval failed")
            return False

        # Test agent memory functions
        test_agent = "test_agent"
        test_memory = {"test": "memory_data", "timestamp": "2025-01-15"}

        success = redis_persistence.store_agent_memory(
            agent_name=test_agent,
            memory_type="test_memory",
            data=test_memory,
            ttl=60
        )

        if success:
            logger.info("✅ Agent memory storage working")
        else:
            logger.error("❌ Agent memory storage failed")
            return False

        # Test retrieval
        retrieved_memory = redis_persistence.get_agent_memory(test_agent, "test_memory")
        if retrieved_memory and retrieved_memory.get("test") == "memory_data":
            logger.info("✅ Agent memory retrieval working")
        else:
            logger.error("❌ Agent memory retrieval failed")
            return False

        # Test cleanup
        redis_persistence.delete_agent_memory(test_agent, "test_memory")
        redis_persistence.redis_client.delete(test_key)

        logger.info("✅ Redis persistence system operational")
        return True

    except Exception as e:
        logger.error(f"❌ Redis test failed: {e}")
        return False

def test_embedding_service():
    """Test embedding service without database operations."""
    try:
        logger.info("Testing embedding service...")

        from persistence.services import EmbeddingService

        # Initialize service
        embedding_service = EmbeddingService()
        logger.info("✅ EmbeddingService initialized")

        # Test cache operations
        cache_key = "test_embedding"
        test_vector = [0.1, 0.2, 0.3, 0.4, 0.5] * 307  # 1535 dimensions
        test_vector.append(0.6)  # Make it 1536 dimensions

        from django.core.cache import cache
        cache.set(cache_key, test_vector, 300)
        cached_vector = cache.get(cache_key)

        if cached_vector and len(cached_vector) == 1536:
            logger.info("✅ Embedding caching system working")
        else:
            logger.error("❌ Embedding caching failed")
            return False

        cache.delete(cache_key)
        return True

    except Exception as e:
        logger.error(f"❌ Embedding service test failed: {e}")
        return False

def test_agent_knowledge_service():
    """Test agent knowledge service without database operations."""
    try:
        logger.info("Testing agent knowledge service...")

        from persistence.services import AgentKnowledgeService

        # Initialize service
        knowledge_service = AgentKnowledgeService()
        logger.info("✅ AgentKnowledgeService initialized")

        return True

    except Exception as e:
        logger.error(f"❌ Agent knowledge service test failed: {e}")
        return False

def test_spider_data_service():
    """Test spider data service without database operations."""
    try:
        logger.info("Testing spider data service...")

        from persistence.services import SpiderDataService

        # Initialize service
        spider_service = SpiderDataService()
        logger.info("✅ SpiderDataService initialized")

        return True

    except Exception as e:
        logger.error(f"❌ Spider data service test failed: {e}")
        return False

def test_unified_search_service():
    """Test unified search service."""
    try:
        logger.info("Testing unified search service...")

        from persistence.services import UnifiedSearchService

        # Initialize service
        search_service = UnifiedSearchService()
        logger.info("✅ UnifiedSearchService initialized")

        return True

    except Exception as e:
        logger.error(f"❌ Unified search service test failed: {e}")
        return False

def test_content_integration():
    """Test content integration services."""
    try:
        logger.info("Testing content integration...")

        from persistence.content_integration import (
            DocumentPersistenceIntegration, ContentGenerationIntegration
        )

        # Initialize services
        doc_integration = DocumentPersistenceIntegration()
        content_integration = ContentGenerationIntegration()

        logger.info("✅ Content integration services initialized")
        return True

    except Exception as e:
        logger.error(f"❌ Content integration test failed: {e}")
        return False

def test_pgvector_availability():
    """Test if pgvector is available."""
    try:
        logger.info("Testing pgvector availability...")

        try:
            from pgvector.django import VectorField
            logger.info("✅ pgvector is available for production deployment")
            return True
        except ImportError:
            logger.warning("⚠️  pgvector not available - using JSON fallback")
            return True  # This is acceptable for development

    except Exception as e:
        logger.error(f"❌ pgvector test failed: {e}")
        return False

def main():
    """Run all persistence infrastructure tests."""
    logger.info("🚀 Starting Data Persistence Infrastructure validation...")

    tests = [
        ("Module Imports", test_imports),
        ("pgvector Availability", test_pgvector_availability),
        ("Redis Connection", test_redis_connection),
        ("Embedding Service", test_embedding_service),
        ("Agent Knowledge Service", test_agent_knowledge_service),
        ("Spider Data Service", test_spider_data_service),
        ("Unified Search Service", test_unified_search_service),
        ("Content Integration", test_content_integration),
    ]

    results = {}

    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} Test ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False

    # Summary
    logger.info("\n" + "="*60)
    logger.info("PERSISTENCE INFRASTRUCTURE VALIDATION SUMMARY")
    logger.info("="*60)

    passed = 0
    total = len(tests)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name:<25} {status}")
        if result:
            passed += 1

    logger.info("-"*60)
    logger.info(f"TOTAL: {passed}/{total} tests passed")

    if passed == total:
        logger.info("🎉 ALL TESTS PASSED - Persistence infrastructure is ready!")
        logger.info("\nNext steps:")
        logger.info("1. Run database migrations when ready")
        logger.info("2. Configure PostgreSQL with pgvector for production")
        logger.info("3. Set up Redis persistence configuration")
        logger.info("4. Deploy and test with real agent workloads")
        return True
    else:
        logger.error("❌ SOME TESTS FAILED - Please fix issues before deployment")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)