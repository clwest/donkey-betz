#!/usr/bin/env python
"""
Test to show the assistant is not using embeddings
Run this BEFORE and AFTER applying the fix to see the difference
"""

import requests
import json

# Security fix: Load environment variables
import os
from dotenv import load_dotenv
load_dotenv()

BASE_URL = os.getenv("BASE_URL", "http://localhost:8001")
TOKEN = os.getenv("TEST_AUTH_TOKEN", "")
if not TOKEN:
    print("WARNING: No TEST_AUTH_TOKEN found. Please set it in .env file.")
    import sys
    sys.exit(1)

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 70)
print("🧪 TESTING: Is the Assistant Using Your 265k Embeddings?")
print("=" * 70)

# Test 1: Ask about something that's definitely in the knowledge base
print("\n📝 Test 1: Asking about Autonomous Knowledge Evolution Engine")
print("(This is in your knowledge base based on the conversation you shared)")
print("-" * 50)

response = requests.post(
    f"{BASE_URL}/api/v1/assistant/chat/",
    headers=headers,
    json={"message": "Tell me about the Autonomous Knowledge Evolution Engine"}
)

if response.status_code == 200:
    data = response.json()
    
    # Check response
    response_text = data.get('message', '').lower()
    
    # Look for indicators that embeddings were used
    embeddings_mentioned = 'embedding' in response_text or 'knowledge base' in response_text
    documents_found = data.get('documents_found', 0)
    total_embeddings = data.get('total_embeddings', 0)
    knowledge_used = data.get('knowledge_base_used', False)
    
    print(f"✅ Response received from {data.get('provider', 'unknown')}")
    print(f"\n📊 Knowledge Base Usage:")
    print(f"   • Documents found: {documents_found}")
    print(f"   • Total embeddings available: {total_embeddings:,}")
    print(f"   • Knowledge base used: {knowledge_used}")
    
    # Check if response mentions the specific capabilities
    if 'continuously turns your data' in response_text or 'semantic knowledge graph' in response_text:
        print(f"\n✅ GOOD: Response includes specific details from knowledge base!")
    else:
        print(f"\n⚠️ WARNING: Response seems generic, not from knowledge base")
    
    print(f"\n💬 First 300 chars of response:")
    print(f"   {data.get('message', '')[:300]}...")
else:
    print(f"❌ Error: {response.status_code}")

# Test 2: Check if it defaults to sports
print("\n\n📝 Test 2: General Platform Question")
print("(Should NOT default to sports betting)")
print("-" * 50)

response = requests.post(
    f"{BASE_URL}/api/v1/assistant/chat/",
    headers=headers,
    json={"message": "What can I do with this platform?"}
)

if response.status_code == 200:
    data = response.json()
    response_text = data.get('message', '').lower()
    
    # Count sports/betting mentions
    sports_words = ['betting', 'odds', 'wager', 'bet', 'sports betting', 'kelly criterion']
    sports_count = sum(response_text.count(word) for word in sports_words)
    
    # Count business/general mentions
    business_words = ['agent', 'content', 'workflow', 'automation', 'knowledge', 'document']
    business_count = sum(response_text.count(word) for word in business_words)
    
    print(f"✅ Response received")
    print(f"\n📊 Content Analysis:")
    print(f"   • Sports/betting mentions: {sports_count}")
    print(f"   • Business/general mentions: {business_count}")
    
    if sports_count > business_count:
        print(f"\n⚠️ WARNING: Response is sports-focused!")
    else:
        print(f"\n✅ GOOD: Response is balanced/business-focused")
    
    print(f"\n💬 First 300 chars of response:")
    print(f"   {data.get('message', '')[:300]}...")
else:
    print(f"❌ Error: {response.status_code}")

# Test 3: Direct knowledge base check
print("\n\n📝 Test 3: Direct Knowledge Base Query")
print("(Should report available embeddings)")
print("-" * 50)

response = requests.post(
    f"{BASE_URL}/api/v1/assistant/chat/",
    headers=headers,
    json={"message": "How many documents and embeddings do you have access to?"}
)

if response.status_code == 200:
    data = response.json()
    response_text = data.get('message', '')
    
    # Check if numbers are mentioned
    has_265k = '265' in response_text or '265,318' in response_text
    mentions_embeddings = 'embedding' in response_text.lower()
    
    print(f"✅ Response received")
    print(f"\n📊 Knowledge Base Awareness:")
    print(f"   • Mentions 265k embeddings: {has_265k}")
    print(f"   • Mentions embeddings at all: {mentions_embeddings}")
    print(f"   • Total embeddings (from metadata): {data.get('total_embeddings', 'Not provided')}")
    
    if has_265k:
        print(f"\n✅ EXCELLENT: Assistant knows about the 265k embeddings!")
    elif mentions_embeddings:
        print(f"\n⚠️ OK: Assistant mentions embeddings but not the correct count")
    else:
        print(f"\n❌ PROBLEM: Assistant doesn't seem aware of embeddings")
    
    print(f"\n💬 Response:")
    print(f"   {response_text[:500]}...")
else:
    print(f"❌ Error: {response.status_code}")

# Summary
print("\n" + "=" * 70)
print("📊 SUMMARY")
print("=" * 70)

print("""
🔍 WHAT TO LOOK FOR:

BEFORE FIX (Current State):
- ❌ No mention of 265k embeddings
- ❌ Generic responses without specific knowledge
- ❌ May default to sports betting topics
- ❌ No document citations or sources

AFTER FIX (Expected):
- ✅ Mentions access to 265,318 embeddings
- ✅ Includes specific information from knowledge base
- ✅ Balanced focus on business/AI capabilities
- ✅ Citations from actual documents

📝 Next Steps:
1. If tests show problems, apply the fix from FIX_ASSISTANT_EMBEDDINGS.md
2. Run this test again after applying the fix
3. You should see dramatic improvement in responses
""")
