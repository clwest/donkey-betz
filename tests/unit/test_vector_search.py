#!/usr/bin/env python
"""
Test vector similarity search on conversation embeddings
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.rag_integration import search_embeddings

# Test searching for our recent conversation about Python and chocolate cake
print("Testing vector similarity search on conversation embeddings...")
print("=" * 60)

# Search for Python-related conversations
query = "Python programming chocolate cake enjoyment"
print(f"\nSearching for: '{query}'")
results = search_embeddings(query, limit=5, content_types=['conversation'], similarity_threshold=0.3)

if results:
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Type: {result['content_type']}")
        print(f"   Similarity: {result['similarity_score']:.3f}")
        print(f"   Content: {result['content'][:200]}...")
        if 'user_message' in result.get('metadata', {}):
            print(f"   User message: {result['metadata']['user_message'][:100]}...")
else:
    print("\nNo results found!")

# Try a broader search
print("\n" + "=" * 60)
print("\nBroader search without content type filter:")
query = "embeddings database conversations"
results = search_embeddings(query, limit=5, similarity_threshold=0.2)

if results:
    print(f"\nFound {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. Type: {result['content_type']}")
        print(f"   Similarity: {result['similarity_score']:.3f}")
        print(f"   Content: {result['content'][:150]}...")
else:
    print("\nNo results found!")