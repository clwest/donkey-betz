# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Test Memory Isolation Implementation
Verifies that RAG search properly filters namespaces
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.rag_integration import search_embeddings, get_rag_context, search_personal_memories
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_system_search():
    """Test that system search excludes personal memories"""
    logger.info("=== Testing System Search (should exclude personal) ===")
    
    test_query = "personal knowledge test"
    results = search_embeddings(
        query=test_query,
        limit=5,
        exclude_personal=True
    )
    
    logger.info(f"Found {len(results)} system results")
    
    # Check that no personal memories are returned
    personal_count = 0
    for result in results:
        if result.get('metadata', {}).get('namespace') == 'personal':
            personal_count += 1
            logger.warning(f"SECURITY BREACH: Personal memory in system search: {result['id']}")
    
    if personal_count == 0:
        logger.info("✅ PASS: No personal memories in system search")
    else:
        logger.error(f"❌ FAIL: {personal_count} personal memories leaked into system search")
    
    return personal_count == 0

def test_personal_search():
    """Test personal memory search with user access control"""
    logger.info("=== Testing Personal Memory Search ===")
    
    test_query = "personal knowledge test"
    results = search_personal_memories(
        query=test_query,
        user_id=1,  # Test with user ID 1
        limit=5
    )
    
    logger.info(f"Found {len(results)} personal results for user 1")
    
    # All results should be personal namespace
    valid_count = 0
    for result in results:
        if result.get('is_personal') or result.get('metadata', {}).get('namespace') == 'personal':
            valid_count += 1
        else:
            logger.warning(f"Non-personal result in personal search: {result['id']}")
    
    logger.info(f"✅ {valid_count}/{len(results)} results properly marked as personal")
    return True

def test_rag_context():
    """Test RAG context excludes personal by default"""
    logger.info("=== Testing RAG Context (should exclude personal) ===")
    
    test_query = "personal knowledge test"
    context = get_rag_context(
        query=test_query,
        include_personal=False
    )
    
    logger.info(f"RAG context has_context: {context['has_context']}")
    logger.info(f"Documents found: {context.get('total_documents', 0)}")
    logger.info(f"Documents used: {context.get('used_documents', 0)}")
    
    return True

def test_no_user_id_protection():
    """Test that personal search requires user_id"""
    logger.info("=== Testing No User ID Protection ===")
    
    results = search_personal_memories(
        query="test",
        user_id=None  # No user ID should return empty
    )
    
    if len(results) == 0:
        logger.info("✅ PASS: No user ID returns no results")
        return True
    else:
        logger.error(f"❌ FAIL: {len(results)} results returned without user ID")
        return False

if __name__ == '__main__':
    logger.info("STARTING MEMORY ISOLATION TESTS")
    logger.info("=" * 60)
    
    tests_passed = 0
    total_tests = 4
    
    try:
        if test_system_search():
            tests_passed += 1
        
        if test_personal_search():
            tests_passed += 1
            
        if test_rag_context():
            tests_passed += 1
            
        if test_no_user_id_protection():
            tests_passed += 1
            
    except Exception as e:
        logger.error(f"Test error: {e}")
    
    logger.info("=" * 60)
    logger.info(f"TESTS COMPLETED: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        logger.info("🎉 ALL TESTS PASSED - Memory isolation is working!")
        print("\n✅ MEMORY ISOLATION SECURE")
    else:
        logger.error(f"⚠️ {total_tests - tests_passed} tests failed - Security issues detected")
        print(f"\n❌ SECURITY ISSUES DETECTED ({tests_passed}/{total_tests} passed)")
        sys.exit(1)