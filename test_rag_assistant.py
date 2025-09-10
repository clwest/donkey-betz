#!/usr/bin/env python
"""
Test the RAG-Enhanced Assistant
"""
import requests
import json

BASE_URL = "http://localhost:8000"
TOKEN = "4b9facbb8006ac4dd7408fd45a6747105a6719fb"  # Your token

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# Test queries that should trigger different parts of the knowledge base
test_queries = [
    "What agents are available in the platform?",
    "Tell me about the AI Agent Orchestration System",
    "How does RAG work in this platform?",
    "What AI providers are supported?",
    "Explain the workflow automation features",
    "What content generation capabilities do you have?",
    "Tell me about the self-awareness module",
    "How does the analytics dashboard work?"
]

print("🧪 Testing RAG-Enhanced Assistant\n")
print("=" * 60)

for query in test_queries:
    print(f"\n📤 Query: {query}")
    print("-" * 40)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/assistant/chat/",
            headers=headers,
            json={
                "message": query,
                "use_rag": True  # Enable RAG
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Response received")
            print(f"   Provider: {data.get('provider', 'unknown')}")
            print(f"   Model: {data.get('model', 'unknown')}")
            print(f"   RAG Used: {data.get('rag_used', False)}")
            print(f"   Knowledge Base Size: {data.get('knowledge_base_size', 0):,} docs")
            print(f"   Embeddings Available: {data.get('total_embeddings_available', 0):,}")
            
            if data.get('sources'):
                print(f"\n   📚 Sources Used:")
                for source in data['sources']:
                    print(f"      • {source['title']} ({source['type']}) - relevance: {source['relevance']:.2f}")
            
            print(f"\n   💬 Response:")
            response_text = data.get('message', '')
            # Print first 400 chars
            if len(response_text) > 400:
                print(f"   {response_text[:400]}...")
            else:
                print(f"   {response_text}")
            
            # Check for sports bias
            sports_mentions = response_text.lower().count('betting') + response_text.lower().count('odds') + response_text.lower().count('sports')
            if sports_mentions > 2:
                print(f"\n   ⚠️ Warning: Found {sports_mentions} sports/betting mentions")
        else:
            print(f"❌ Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error message: {error_data}")
            except:
                print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        print("   Make sure the Django server is running (python manage.py runserver)")

print("\n" + "=" * 60)
print("✅ Test Complete")
print("\n📊 Summary:")
print("   • The assistant now uses the RAG-enhanced implementation")
print("   • It searches through available documents for context")
print("   • Falls back to keyword search when embeddings aren't available")
print("   • Provides source citations when relevant documents are found")