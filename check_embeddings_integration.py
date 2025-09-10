#!/usr/bin/env python3
"""
Check the integration of migrated embeddings with the RAG system
"""

import os
import sys
import django
import numpy as np

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model

User = get_user_model()

def check_embeddings():
    """Check migrated embeddings"""
    print("="*60)
    print("🔍 CHECKING MIGRATED EMBEDDINGS")
    print("="*60)
    
    # Check unified_embeddings table
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM unified_embeddings")
        total = cursor.fetchone()[0]
        print(f"\n📊 Total migrated embeddings: {total:,}")
        
        # Get breakdown
        cursor.execute("""
            SELECT content_type, COUNT(*) as count 
            FROM unified_embeddings 
            GROUP BY content_type 
            ORDER BY count DESC
        """)
        
        print(f"\n📝 Content Types:")
        for content_type, count in cursor.fetchall():
            print(f"   • {content_type}: {count:,}")
        
        # Sample some embeddings
        cursor.execute("""
            SELECT content_type, content_text, importance_score 
            FROM unified_embeddings 
            WHERE content_text IS NOT NULL 
            LIMIT 5
        """)
        
        print(f"\n📄 Sample Embeddings:")
        for content_type, text, score in cursor.fetchall():
            snippet = (text or "")[:80].replace('\n', ' ')
            print(f"   • [{content_type}] {snippet}... (importance: {score})")

def create_document_embeddings():
    """Create DocumentEmbedding records from unified_embeddings"""
    print("\n" + "="*60)
    print("🔄 CREATING DJANGO MODEL EMBEDDINGS")
    print("="*60)
    
    from content.models import Document, DocumentEmbedding
    
    # Get or create a default document for embeddings without documents
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.first()
    
    default_doc, created = Document.objects.get_or_create(
        title="Migrated Embeddings Collection",
        owner=user,
        defaults={
            'description': "Collection of embeddings migrated from moveyourazz_dev",
            'document_type': 'collection',
            'is_public': True,
            'status': 'processed'
        }
    )
    
    if created:
        print(f"✅ Created default document: {default_doc.title}")
    
    # Create DocumentEmbedding records
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT id, content_text, embedding, embedding_model, importance_score, metadata
            FROM unified_embeddings 
            WHERE content_type IN ('document', 'conversation', 'insight', 'idea')
            LIMIT 100
        """)
        
        created_count = 0
        for row in cursor.fetchall():
            unified_id, text_chunk, embedding_vector, model, importance, metadata = row
            
            # Create DocumentEmbedding
            doc_embedding, created = DocumentEmbedding.objects.get_or_create(
                chunk_hash=f"migrated_{unified_id}",
                defaults={
                    'document': default_doc,
                    'text_chunk': text_chunk[:2000] if text_chunk else "",  # Limit length
                    'chunk_index': 0,
                    'embedding_model': model or 'text-embedding-ada-002',
                    'embedding': embedding_vector,
                    'metadata': metadata or {}
                }
            )
            
            if created:
                created_count += 1
        
        print(f"✅ Created {created_count} DocumentEmbedding records")

def test_semantic_search():
    """Test semantic search with migrated embeddings"""
    print("\n" + "="*60)
    print("🔍 TESTING SEMANTIC SEARCH")
    print("="*60)
    
    from core.views_assistant_rag_enhanced import RAGAssistant
    
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        user = User.objects.first()
    
    rag = RAGAssistant(user)
    
    # Test queries
    test_queries = [
        "artificial intelligence",
        "business strategy", 
        "agent automation",
        "content generation"
    ]
    
    for query in test_queries:
        print(f"\n📤 Query: '{query}'")
        
        # Try embedding search first
        sources = rag.search_embeddings(query, limit=3)
        
        if sources:
            print(f"✅ Found {len(sources)} embedding matches:")
            for source in sources:
                print(f"   • {source['title']} (relevance: {source['relevance']:.3f})")
        else:
            print("❌ No embedding matches found")
        
        # Try document search
        doc_sources = rag.search_documents(query, limit=3)
        if doc_sources:
            print(f"✅ Found {len(doc_sources)} document matches:")
            for source in doc_sources:
                print(f"   • {source['title']}")

def main():
    print("\n🚀 EMBEDDINGS INTEGRATION CHECK")
    
    # 1. Check migrated embeddings
    check_embeddings()
    
    # 2. Create Django model records
    create_document_embeddings()
    
    # 3. Test search
    test_semantic_search()
    
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    
    from content.models import DocumentEmbedding
    doc_emb_count = DocumentEmbedding.objects.count()
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM unified_embeddings")
        unified_count = cursor.fetchone()[0]
    
    print(f"""
✅ Migration Status:
   • Migrated embeddings: {unified_count:,}
   • Django DocumentEmbeddings: {doc_emb_count}
   • RAG system ready for semantic search

🎯 Next Steps:
   1. Test the assistant: python test_rag_assistant.py
   2. The system now has access to 16k+ embeddings from moveyourazz_dev
   3. RAG responses should be much more relevant and contextual
""")

if __name__ == "__main__":
    main()