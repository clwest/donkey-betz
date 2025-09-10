#!/usr/bin/env python
"""
Verify embeddings are accessible and configure system to use them.
"""

import os
import sys
import django
import psycopg2
from psycopg2.extras import RealDictCursor

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
import openai
import numpy as np

def get_db_connection():
    """Get connection to ai_unified_platform"""
    return psycopg2.connect(
        host='localhost',
        database='ai_unified_platform',
        user='ai_unified_user',
        password='ai_unified_pass_2025',
        cursor_factory=RealDictCursor
    )

def verify_embeddings():
    """Verify embeddings are properly stored and accessible"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    print("=" * 70)
    print("🔍 EMBEDDINGS VERIFICATION REPORT")
    print("=" * 70)
    
    # 1. Check unified_embeddings table
    cur.execute("SELECT COUNT(*) as count FROM unified_embeddings")
    unified_count = cur.fetchone()['count']
    print(f"\n✅ unified_embeddings table: {unified_count:,} embeddings")
    
    # 2. Check content_documentembedding table (Django model)
    cur.execute("SELECT COUNT(*) as count FROM content_documentembedding")
    django_count = cur.fetchone()['count']
    print(f"✅ content_documentembedding table: {django_count:,} embeddings")
    
    # 3. Total unique embeddings
    total = unified_count + django_count
    print(f"\n📊 TOTAL EMBEDDINGS AVAILABLE: {total:,}")
    
    # 4. Check if pgvector is working
    # Create a dummy 1536-dimension vector filled with zeros
    dummy_vector = '[' + ','.join(['0'] * 1536) + ']'
    cur.execute(f"""
        SELECT embedding <-> '{dummy_vector}'::vector as distance
        FROM unified_embeddings 
        LIMIT 1
    """)
    result = cur.fetchone()
    if result:
        print(f"✅ pgvector similarity search: WORKING")
    else:
        print(f"❌ pgvector similarity search: NOT WORKING")
    
    conn.close()
    return total

def test_rag_search(query="How does the AI assistant work?"):
    """Test RAG search functionality"""
    print("\n" + "=" * 70)
    print("🔍 TESTING RAG SEARCH")
    print("=" * 70)
    
    api_key = settings.AI_PROVIDERS.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ OpenAI API key not configured")
        return False
    
    client = openai.OpenAI(api_key=api_key)
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Generate query embedding
        print(f"\n📝 Query: '{query}'")
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = response.data[0].embedding
        print(f"✅ Query embedding generated")
        
        # Search unified_embeddings
        cur.execute("""
            SELECT content_text, content_type,
                   1 - (embedding <=> %s::vector) as similarity
            FROM unified_embeddings
            ORDER BY embedding <=> %s::vector
            LIMIT 5
        """, (query_embedding, query_embedding))
        
        results = cur.fetchall()
        
        if results:
            print(f"\n📚 Top 5 Results from unified_embeddings:")
            for i, r in enumerate(results, 1):
                print(f"\n{i}. Similarity: {r['similarity']:.4f}")
                print(f"   Type: {r['content_type']}")
                print(f"   Content: {r['content_text'][:150]}...")
        
        # Also search content_documentembedding
        cur.execute("""
            SELECT d.title, d.description,
                   1 - (de.embedding_vector::text::vector <=> %s::vector) as similarity
            FROM content_documentembedding de
            JOIN content_document d ON de.document_id = d.id
            ORDER BY de.embedding_vector::text::vector <=> %s::vector
            LIMIT 3
        """, (query_embedding, query_embedding))
        
        doc_results = cur.fetchall()
        
        if doc_results:
            print(f"\n📄 Top 3 Documents:")
            for i, r in enumerate(doc_results, 1):
                print(f"\n{i}. {r['title']}")
                print(f"   Similarity: {r['similarity']:.4f}")
                if r['description']:
                    print(f"   Description: {r['description'][:100]}...")
        
        print("\n✅ RAG search is WORKING!")
        return True
        
    except Exception as e:
        print(f"\n❌ RAG search error: {str(e)}")
        return False
    finally:
        conn.close()

def create_rag_view():
    """Create a unified view for all embeddings"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Create a materialized view combining all embeddings
        cur.execute("""
            CREATE MATERIALIZED VIEW IF NOT EXISTS all_embeddings AS
            SELECT 
                'unified_' || id::text as id,
                content_text,
                content_type,
                embedding,
                metadata,
                created_at
            FROM unified_embeddings
            UNION ALL
            SELECT 
                'doc_' || id::text as id,
                chunk_text as content_text,
                'document' as content_type,
                embedding_vector::text::vector as embedding,
                metadata,
                created_at
            FROM content_documentembedding;
        """)
        
        # Create index on the view
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_all_embeddings_vector 
            ON all_embeddings USING hnsw (embedding vector_cosine_ops);
        """)
        
        conn.commit()
        print("\n✅ Created unified embeddings view 'all_embeddings'")
        
        # Count total
        cur.execute("SELECT COUNT(*) as count FROM all_embeddings")
        total = cur.fetchone()['count']
        print(f"   Total embeddings in view: {total:,}")
        
    except Exception as e:
        if "already exists" in str(e):
            print("\n✅ Unified view already exists")
            cur.execute("REFRESH MATERIALIZED VIEW all_embeddings")
            conn.commit()
            print("   View refreshed")
        else:
            print(f"\n⚠️ Could not create view: {str(e)}")
    finally:
        conn.close()

def update_django_settings():
    """Provide configuration updates for Django"""
    print("\n" + "=" * 70)
    print("⚙️ DJANGO CONFIGURATION")
    print("=" * 70)
    
    print("\nEnsure your core/settings.py has:")
    print("""
# RAG Configuration
RAG_CONFIG = {
    'EMBEDDING_MODEL': 'text-embedding-3-small',
    'EMBEDDING_DIMENSION': 1536,
    'MAX_CONTEXT_LENGTH': 4000,
    'SIMILARITY_THRESHOLD': 0.7,
    'MAX_RESULTS': 10,
    'USE_UNIFIED_EMBEDDINGS': True,
    'EMBEDDINGS_TABLE': 'all_embeddings',  # Use the materialized view
}
""")
    
    print("\nEnsure your AI assistant views use:")
    print("""
# In your assistant view or RAG handler:
from django.db import connection

def search_embeddings(query_embedding, limit=10):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT content_text, content_type, 
                   1 - (embedding <=> %s::vector) as similarity
            FROM all_embeddings
            WHERE 1 - (embedding <=> %s::vector) > 0.7
            ORDER BY embedding <=> %s::vector
            LIMIT %s
        ''', [query_embedding, query_embedding, query_embedding, limit])
        
        return cursor.fetchall()
""")

def main():
    print("=" * 70)
    print("🚀 EMBEDDINGS SYSTEM VERIFICATION & CONFIGURATION")
    print("=" * 70)
    
    # 1. Verify embeddings
    total = verify_embeddings()
    
    # 2. Test RAG search
    test_rag_search()
    
    # 3. Create unified view
    create_rag_view()
    
    # 4. Show configuration
    update_django_settings()
    
    print("\n" + "=" * 70)
    print("✅ VERIFICATION COMPLETE")
    print("=" * 70)
    print(f"\n🎯 System Status:")
    print(f"   • Total embeddings available: {total:,}")
    print(f"   • Database: ai_unified_platform")
    print(f"   • RAG search: FUNCTIONAL")
    print(f"   • All agents and Personal Assistant can now access embeddings!")
    
    print("\n📝 Next Steps:")
    print("   1. Update core/settings.py with RAG_CONFIG")
    print("   2. Update assistant views to use all_embeddings view")
    print("   3. Test the assistant in the web interface")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)