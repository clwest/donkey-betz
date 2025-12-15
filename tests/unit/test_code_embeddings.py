# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python3
"""
Test code embeddings integration with RAG system
"""
import pytest
import os
import sys
import django
import numpy as np

# Session 452: Skip tests that require production database tables (unified_embeddings)
pytestmark = [
    pytest.mark.django_db,
    pytest.mark.skip(reason="Requires unified_embeddings table from production DB")
]

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
django.setup()

from django.db import connection

def test_code_embeddings_direct():
    """Test direct access to code embeddings"""
    
    print("🧪 Testing Direct Code Embeddings Access")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        # Check total embeddings
        cursor.execute("SELECT COUNT(*) FROM unified_embeddings")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total unified embeddings: {total_count:,}")
        
        # Check code embeddings specifically
        cursor.execute("""
            SELECT COUNT(*) FROM unified_embeddings 
            WHERE source_database = 'moveyourazz_dev'
            AND source_table = 'ai_partner_codeembedding'
        """)
        code_count = cursor.fetchone()[0]
        print(f"💻 Code embeddings: {code_count}")
        
        if code_count > 0:
            print(f"\n📋 Code Embedding Breakdown:")
            
            # By content type
            cursor.execute("""
                SELECT content_type, COUNT(*) 
                FROM unified_embeddings 
                WHERE source_database = 'moveyourazz_dev'
                AND source_table = 'ai_partner_codeembedding'
                GROUP BY content_type
                ORDER BY COUNT(*) DESC
            """)
            
            for content_type, count in cursor.fetchall():
                print(f"   • {content_type}: {count}")
            
            # Sample a few embeddings
            print(f"\n🔍 Sample Code Embeddings:")
            cursor.execute("""
                SELECT content_type, content_text
                FROM unified_embeddings 
                WHERE source_database = 'moveyourazz_dev'
                AND source_table = 'ai_partner_codeembedding'
                ORDER BY id LIMIT 5
            """)
            
            for i, (content_type, content_text) in enumerate(cursor.fetchall(), 1):
                preview = content_text[:80].replace('\n', ' ')
                print(f"   {i}. {content_type}: {preview}...")
    
    return code_count > 0

def test_django_model_queries():
    """Test searching for Django model related content"""
    
    print(f"\n🔍 Testing Django Model Queries")
    print("=" * 60)
    
    # Test queries that should match our code embeddings
    test_queries = [
        "Django model class definition",
        "UserLifeProfile model", 
        "ConversationMemory class",
        "vector embeddings in Django",
        "RAG performance metrics model",
        "pgvector database indexing"
    ]
    
    with connection.cursor() as cursor:
        for query in test_queries:
            print(f"\n📤 Query: '{query}'")
            
            # Search in code embeddings using simple keyword search
            keyword = query.split()[0].lower()
            cursor.execute("""
                SELECT COUNT(*) FROM unified_embeddings 
                WHERE source_database = 'moveyourazz_dev'
                AND source_table = 'ai_partner_codeembedding'
                AND LOWER(content_text) LIKE %s
            """, [f'%{keyword}%'])
            
            count = cursor.fetchone()[0]
            print(f"   💻 Code matches: {count}")
            
            if count > 0:
                cursor.execute("""
                    SELECT content_text FROM unified_embeddings 
                    WHERE source_database = 'moveyourazz_dev'
                    AND source_table = 'ai_partner_codeembedding'
                    AND LOWER(content_text) LIKE %s
                    LIMIT 1
                """, [f'%{keyword}%'])
                
                content_text = cursor.fetchone()[0]
                preview = content_text[:100].replace('\n', ' ')
                print(f"      Preview: {preview}...")

def test_vector_similarity():
    """Test if vector similarity search is working"""
    
    print(f"\n🎯 Testing Vector Similarity Search")
    print("=" * 60)
    
    with connection.cursor() as cursor:
        # Get a sample embedding to test with
        cursor.execute("""
            SELECT id, content_type, content_text, embedding
            FROM unified_embeddings 
            WHERE source_database = 'moveyourazz_dev'
            AND source_table = 'ai_partner_codeembedding'
            AND embedding IS NOT NULL
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        
        if result:
            id_, content_type, content_text, embedding = result
            print(f"✅ Found sample embedding: {content_type}")
            print(f"   Content preview: {content_text[:80]}...")
            
            try:
                # Try a simple similarity search using raw SQL
                cursor.execute("""
                    SELECT id, content_type, LEFT(content_text, 60) as preview,
                           embedding <-> %s as distance
                    FROM unified_embeddings 
                    WHERE source_database = 'moveyourazz_dev'
                    AND source_table = 'ai_partner_codeembedding'
                    AND embedding IS NOT NULL
                    ORDER BY embedding <-> %s
                    LIMIT 3
                """, [embedding, embedding])
                
                results = cursor.fetchall()
                print(f"   ✅ Similar embeddings found: {len(results)}")
                
                for i, (id_, content_type, preview, distance) in enumerate(results, 1):
                    preview_clean = preview.replace('\n', ' ')
                    print(f"      {i}. {content_type} (distance: {distance:.3f}): {preview_clean}...")
            
            except Exception as e:
                print(f"   ⚠️  Vector search test failed: {str(e)}")
        else:
            print("❌ No code embeddings with vectors found")

def test_rag_integration():
    """Test if RAG system can find our code embeddings"""
    
    print(f"\n🤖 Testing RAG System Integration")
    print("=" * 60)
    
    try:
        from core.views_assistant_rag_enhanced import search_embeddings
        
        # Test code-related queries
        code_queries = [
            "Django model with vector embeddings",
            "UserLifeProfile class definition",
            "conversation memory model",
            "RAG performance metrics"
        ]
        
        for query in code_queries:
            print(f"\n📤 RAG Query: '{query}'")
            
            try:
                results = search_embeddings(query, limit=3)
                print(f"   📚 RAG results: {len(results)} found")
                
                for i, result in enumerate(results, 1):
                    if hasattr(result, 'content_type'):
                        print(f"      {i}. {result.content_type}: {result.content_text[:60]}...")
                    else:
                        print(f"      {i}. Result: {str(result)[:60]}...")
                        
            except Exception as e:
                print(f"   ❌ RAG search failed: {str(e)}")
                
    except ImportError as e:
        print(f"❌ Could not import RAG functions: {str(e)}")

def main():
    print("🧪 CODE EMBEDDINGS INTEGRATION TEST")
    print("=" * 80)
    
    try:
        # Test 1: Direct database access
        has_code_embeddings = test_code_embeddings_direct()
        
        if has_code_embeddings:
            # Test 2: Django model queries  
            test_django_model_queries()
            
            # Test 3: Vector similarity
            test_vector_similarity()
            
            # Test 4: RAG integration
            test_rag_integration()
        else:
            print("❌ No code embeddings found in database!")
            return False
        
        print(f"\n" + "=" * 80)
        print("✅ CODE EMBEDDINGS TEST COMPLETE")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)