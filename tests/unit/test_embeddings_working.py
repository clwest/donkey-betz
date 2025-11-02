# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Quick test to verify embeddings and RAG are working
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from content.models import Document, DocumentEmbedding
import openai
from django.conf import settings
import json

def test_embeddings():
    """Test that embeddings exist and can be searched"""
    
    print("=" * 50)
    print("Testing Embeddings and RAG Setup")
    print("=" * 50)
    
    # Check documents and embeddings
    total_docs = Document.objects.count()
    docs_with_embeddings = Document.objects.filter(embeddings__isnull=False).distinct().count()
    total_embeddings = DocumentEmbedding.objects.count()
    
    print(f"\n📊 Database Status:")
    print(f"  Total documents: {total_docs}")
    print(f"  Documents with embeddings: {docs_with_embeddings}")
    print(f"  Total embeddings: {total_embeddings}")
    
    if total_embeddings == 0:
        print("\n❌ No embeddings found!")
        return False
    
    # Test similarity search
    print("\n🔍 Testing Similarity Search:")
    
    api_key = settings.AI_PROVIDERS.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY not configured")
        return False
    
    client = openai.OpenAI(api_key=api_key)
    
    # Create a test query embedding
    test_query = "How does the RAG system work?"
    print(f"  Query: '{test_query}'")
    
    try:
        # Generate embedding for query
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=test_query
        )
        query_embedding = response.data[0].embedding
        print(f"  ✅ Query embedding generated (dimensions: {len(query_embedding)})")
        
        # Manually calculate similarities (simple dot product)
        print("\n📄 Top 3 Most Similar Documents:")
        
        results = []
        for embedding in DocumentEmbedding.objects.all():
            # Calculate dot product similarity
            doc_embedding = embedding.embedding_vector
            if isinstance(doc_embedding, (list, tuple)) and len(doc_embedding) == len(query_embedding):
                similarity = sum(a * b for a, b in zip(query_embedding, doc_embedding))
                results.append((embedding.document, similarity))
        
        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Show top 3
        for i, (doc, similarity) in enumerate(results[:3], 1):
            print(f"\n  {i}. {doc.title}")
            print(f"     Similarity: {similarity:.4f}")
            print(f"     Type: {doc.document_type}")
            if doc.description:
                print(f"     Description: {doc.description[:100]}...")
        
        print("\n✅ RAG system is working! Embeddings are properly configured.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing similarity search: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_embeddings()
    sys.exit(0 if success else 1)