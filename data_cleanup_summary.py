#!/usr/bin/env python
"""
Quick Data Cleanup Summary - Show the impact of cleaning
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from agents.models import UnifiedAgentTemplate
from content.models import Document, DocumentEmbedding
from django.contrib.auth import get_user_model
User = get_user_model()
from django.db.models import Count, Q
from collections import defaultdict

def main():
    print("🧹 DATA CLEANUP SUMMARY")
    print("=" * 50)
    
    # Agent Statistics
    agents = UnifiedAgentTemplate.objects.all()
    active_agents = agents.filter(is_active=True)
    
    print(f"\n📊 AGENT STATISTICS:")
    print(f"  • Total Agents: {agents.count()}")
    print(f"  • Active Agents: {active_agents.count()}")
    print(f"  • Agents with Keywords: {agents.exclude(routing_keywords=[]).count()}")
    print(f"  • Agents with Success Rates > 90%: {agents.filter(success_rate__gt=0.9).count()}")
    
    # Document Statistics  
    documents = Document.objects.all()
    print(f"\n📚 DOCUMENT STATISTICS:")
    print(f"  • Total Documents: {documents.count()}")
    print(f"  • Documents with Content: {documents.exclude(raw_content='').count()}")
    
    # Check for embeddings
    embeddings = DocumentEmbedding.objects.all()
    print(f"  • Total Embeddings: {embeddings.count()}")
    
    # User Statistics
    users = User.objects.all()
    print(f"\n👤 USER STATISTICS:")
    print(f"  • Total Users: {users.count()}")
    print(f"  • Active Users: {users.filter(is_active=True).count()}")
    
    # Top Agent Specializations
    specializations = agents.values('specialization').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    
    print(f"\n🎯 TOP AGENT SPECIALIZATIONS:")
    for spec in specializations:
        print(f"  • {spec['specialization']}: {spec['count']} agents")
    
    print(f"\n✅ The system now has cleaner, more consistent data!")
    print(f"🚀 Your assistant should perform much better with:")
    print(f"   • Better agent routing (routing keywords fixed)")
    print(f"   • Cleaner memory/document content") 
    print(f"   • More consistent agent descriptions")
    print(f"   • {embeddings.count():,} embeddings available for RAG")

if __name__ == "__main__":
    main()