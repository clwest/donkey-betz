# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
#!/usr/bin/env python
"""
Quick test of RAG functionality
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.append('/Users/donkeyking/development/unified-donkey-betz')
django.setup()

from django.contrib.auth import get_user_model
from core.views_assistant_rag_enhanced import RAGAssistant

User = get_user_model()

# Get a user
user = User.objects.filter(is_superuser=True).first()
if not user:
    user = User.objects.first()

print(f"Testing with user: {user}")

# Create RAG assistant
rag = RAGAssistant(user)

# Test queries
test_queries = [
    "agent orchestration",
    "RAG",
    "workflow automation"
]

for query in test_queries:
    print(f"\n📤 Query: {query}")
    print("-" * 40)
    
    # Search documents
    sources = rag.search_documents(query)
    
    if sources:
        print(f"✅ Found {len(ources)} documents:")
        for source in sources:
            print(f"   • {source['title']}")
            print(f"     {source['content'][:100]}...")
    else:
        print("❌ No documents found")

# Check total documents
from content.models import Document
total_docs = Document.objects.count()
public_docs = Document.objects.filter(is_public=True).count()

print(f"\n📊 Database Status:")
print(f"   Total Documents: {total_docs}")
print(f"   Public Documents: {public_docs}")

# Show a sample document
if total_docs > 0:
    doc = Document.objects.first()
    print(f"\n📄 Sample Document:")
    print(f"   Title: {doc.title}")
    print(f"   Owner: {doc.owner}")
    print(f"   Is Public: {doc.is_public}")
    print(f"   Content Length: {len(doc.raw_content or doc.processed_content or '')}")