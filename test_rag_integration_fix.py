#!/usr/bin/env python
"""
Test script to verify RAG integration with unified_embeddings
"""

import os
import sys
import django
import requests
import json

# Setup Django
sys.path.insert(0, '/Users/donkeyking/development/unified-donkey-betz')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def test_rag_integration():
    """Test the RAG integration"""
    
    print("=" * 60)
    print("Testing RAG Integration with Unified Embeddings")
    print("=" * 60)
    
    # Login first
    base_url = 'http://localhost:8000'
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    print("\n1. Logging in...")
    login_response = requests.post(f'{base_url}/api/auth/login/', json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    token = login_response.json().get('token')
    headers = {'Authorization': f'Token {token}'}
    print(f"✅ Logged in successfully")
    
    # Test queries
    test_queries = [
        "What do you know about sports betting and Kelly Criterion?",
        "Tell me about agent orchestration and AI workflows",
        "How does the platform handle embeddings and RAG?",
        "What security features are available?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Testing query: '{query[:50]}...'")
        print("-" * 40)
        
        chat_data = {
            'message': query,
            'use_rag': True  # Explicitly enable RAG
        }
        
        try:
            response = requests.post(
                f'{base_url}/api/assistant/chat/',
                json=chat_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if RAG was used
                has_rag = 'rag_context' in data
                
                print(f"✅ Response received")
                print(f"   Provider: {data.get('provider', 'unknown')}")
                print(f"   Model: {data.get('model', 'unknown')}")
                print(f"   RAG Used: {'Yes' if has_rag else 'No'}")
                
                if has_rag:
                    rag_info = data['rag_context']
                    print(f"   Documents Used: {len(rag_info.get('documents_used', []))}")
                    print(f"   Total Found: {rag_info.get('total_documents_found', 0)}")
                    
                    # Show document types used
                    if rag_info.get('documents_used'):
                        doc_types = set(d['type'] for d in rag_info['documents_used'])
                        print(f"   Document Types: {', '.join(doc_types)}")
                
                # Show first 200 chars of response
                message = data.get('message', '')
                print(f"\n   Response Preview:")
                print(f"   {message[:200]}...")
                
            else:
                print(f"❌ Request failed: {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Test direct RAG function
    print("\n" + "=" * 60)
    print("Testing Direct RAG Function")
    print("=" * 60)
    
    try:
        from core.rag_integration import search_embeddings, get_rag_context
        
        test_query = "sports betting Kelly Criterion"
        print(f"\nSearching for: '{test_query}'")
        
        # Test search
        results = search_embeddings(test_query, limit=3)
        print(f"\n✅ Found {len(results)} documents")
        
        for i, doc in enumerate(results, 1):
            print(f"\n   Document {i}:")
            print(f"   - Type: {doc['content_type']}")
            print(f"   - Similarity: {doc['similarity_score']:.3f}")
            print(f"   - Content: {doc['content'][:100]}...")
        
        # Test context building
        context = get_rag_context(test_query)
        if context['has_context']:
            print(f"\n✅ RAG context built successfully")
            print(f"   - Used {len(context['documents'])} documents")
            print(f"   - Context length: {len(context['context_text'])} chars")
        else:
            print("\n⚠️  No RAG context found")
            
    except Exception as e:
        print(f"\n❌ Direct RAG test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rag_integration()