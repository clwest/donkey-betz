#!/usr/bin/env python3
"""
Test the RAG fixes we just applied
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
django.setup()

def test_total_embeddings():
    """Test the fixed _get_total_embeddings function"""
    
    print("🧪 Testing _get_total_embeddings fix")
    
    try:
        from core.views_assistant_rag_enhanced import _get_total_embeddings
        
        total = _get_total_embeddings()
        print(f"   ✅ Total embeddings: {total:,}")
        
        if total > 0:
            print(f"   🎯 Success! Now showing unified embeddings count instead of 0")
            return True
        else:
            print(f"   ⚠️  Still showing 0 - check database connection")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_unified_search():
    """Test the updated search_embeddings function"""
    
    print(f"\n🔍 Testing unified embeddings search")
    
    try:
        from core.views_assistant_rag_enhanced import RAGAssistant
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username='test_rag',
            defaults={'email': 'test@example.com'}
        )
        
        rag_assistant = RAGAssistant(user)
        
        # Test code intelligence query
        code_query = "Django model UserLifeProfile"
        results = rag_assistant.search_embeddings(code_query, limit=3)
        
        print(f"   Query: '{code_query}'")
        print(f"   Results found: {len(results)}")
        
        code_results = [r for r in results if r['type'] == 'code']
        print(f"   Code results: {len(code_results)}")
        
        for i, result in enumerate(results, 1):
            result_indicator = "💻" if result['type'] == 'code' else "📄"
            print(f"      {i}. {result_indicator} {result['title']} (relevance: {result['relevance']:.2f})")
        
        if code_results:
            print(f"   🎯 Success! Found code intelligence results")
            return True
        else:
            print(f"   ⚠️  No code results found")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_full_rag_assistant():
    """Test the complete RAG assistant flow"""
    
    print(f"\n🤖 Testing full RAG assistant flow")
    
    try:
        from django.http import HttpRequest
        from django.contrib.auth import get_user_model
        from core.views_assistant_rag_enhanced import assistant_chat_enhanced
        import json
        
        User = get_user_model()
        user, created = User.objects.get_or_create(
            username='test_full_rag',
            defaults={'email': 'test@example.com'}
        )
        
        # Create a mock request
        request = HttpRequest()
        request.method = 'POST'
        request.user = user
        request.content_type = 'application/json'
        
        # Set request data
        test_message = "I am testing the RAG system with code intelligence."
        request_data = {
            'message': test_message,
            'use_rag': True
        }
        request._body = json.dumps(request_data).encode()
        
        # Mock the data attribute
        class MockData:
            def get(self, key, default=None):
                return request_data.get(key, default)
        
        request.data = MockData()
        
        print(f"   Testing message: '{test_message}'")
        
        # Call the assistant
        response = assistant_chat_enhanced(request)
        
        print(f"   Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.data
            message = data.get('message', '')
            rag_used = data.get('rag_used', False)
            sources = data.get('sources', [])
            total_embeddings = data.get('total_embeddings_available', 0)
            
            print(f"   Message length: {len(message)}")
            print(f"   RAG used: {rag_used}")
            print(f"   Sources found: {len(sources)}")
            print(f"   Total embeddings: {total_embeddings:,}")
            
            if message and len(message.strip()) > 0:
                print(f"   Response preview: {message[:100]}...")
                print(f"   🎉 SUCCESS! RAG is now responding properly!")
                return True
            else:
                print(f"   ❌ Still getting empty responses")
                return False
        else:
            print(f"   ❌ HTTP error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔧 TESTING RAG FIXES")
    print("="*60)
    
    # Test 1: Total embeddings count
    embeddings_fixed = test_total_embeddings()
    
    # Test 2: Unified search
    search_fixed = test_unified_search()
    
    # Test 3: Full RAG flow
    rag_fixed = test_full_rag_assistant()
    
    print(f"\n" + "="*60)
    print("🎯 FIX VERIFICATION RESULTS")
    print("="*60)
    
    print(f"✅ Embeddings Count: {'Fixed' if embeddings_fixed else 'Still Broken'}")
    print(f"✅ Unified Search: {'Fixed' if search_fixed else 'Still Broken'}")
    print(f"✅ Full RAG Flow: {'Fixed' if rag_fixed else 'Still Broken'}")
    
    if embeddings_fixed and search_fixed and rag_fixed:
        print(f"\n🎉 ALL FIXES SUCCESSFUL!")
        print(f"🚀 Your RAG system is now working with code intelligence!")
        print(f"💻 Try asking about Django models, UserLifeProfile, or vector search!")
    else:
        print(f"\n⚠️  Some issues remain - check the logs above")
        
    return embeddings_fixed and search_fixed and rag_fixed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)